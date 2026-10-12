"""How often the relator-length cap alone ends a search.

The search loop is ``while heap and nodes < budget``. An unsolved search that
stopped below its node budget therefore ran out of states: every child it
still had was dropped by the cap. This counts those searches in every result
file of a directory (controls, rank-3 lengths, relator subwords, rank 4/5).

    python3 -m experiments.stable_ac.rank3.cap_exhaustion --dir results/stable_ac/rank3_bf

Where a run stored the cap counters (``run_rank3_bf.CAP_DOC``) a second table
counts, per file, the searches in which the cap dropped a child at all and
those in which a dropped child could have been popped (``cap_first_bind``).
A search with no such pop is the same search at every larger cap.
"""
import argparse
import glob
import gzip
import json
import os
import re

import numpy as np


def _rows(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as f:
        return [json.loads(line) for line in f if line.strip()]


CAP_KEYS = ("cap_dropped_a_child", "cap_could_bind", "cap_could_bind_solved",
            "cap_could_bind_unsolved", "children_dropped")


def _caps(dropped, bind, solved):
    """Counts from the cap counters of one file (bind: -1 = never)."""
    dropped, bind, solved = (np.asarray(a) for a in (dropped, bind, solved))
    hit = bind >= 0
    return {"cap_dropped_a_child": int((dropped > 0).sum()),
            "cap_could_bind": int(hit.sum()),
            "cap_could_bind_solved": int((hit & solved).sum()),
            "cap_could_bind_unsolved": int((hit & ~solved).sum()),
            "children_dropped": int(dropped.astype(np.int64).sum())}


def _entry(name, kind, budget, cap, searches, unsolved, early, pres_early, min_nodes,
           caps=None):
    return dict({"file": name, "kind": kind, "node_budget": int(budget),
                 "max_relator_length_cap": int(cap), "searches": int(searches),
                 "unsolved": int(unsolved), "unsolved_before_budget": int(early),
                 "presentations_with_one": int(pres_early),
                 "fewest_nodes_of_those": None if min_nodes is None else int(min_nodes)},
                **(caps or dict.fromkeys(CAP_KEYS)))


def from_jsonl(path, kind, prefix=""):
    """``prefix``: where the row keeps its cap counters (control rows: ``n2_``)."""
    rows = _rows(path)
    uns = [r for r in rows if not r["solved"]]
    early = [r for r in uns if r["nodes_explored"] < r["node_budget"]]
    caps = None
    if prefix + "cap_dropped" in rows[0]:
        caps = _caps([r[prefix + "cap_dropped"] for r in rows],
                     [-1 if r[prefix + "cap_first_bind"] is None
                      else r[prefix + "cap_first_bind"] for r in rows],
                     [bool(r["solved"]) for r in rows])
    return _entry(os.path.basename(path), kind, rows[0]["node_budget"],
                  rows[0]["max_relator_length_cap"], len(rows), len(uns), len(early),
                  len({r["pres_id"] for r in early}),
                  min((r["nodes_explored"] for r in early), default=None), caps)


def from_npz(path, kind, budget, cap):
    """Counters: the ``_capcount.npz`` beside a rank-3 file, or the file itself."""
    with np.load(path) as z:
        nodes = z["nodes"].astype(np.int64)
        plen = z["path_len"].astype(np.int64)
        caps = (z["cap_dropped"], z["cap_first_bind"]) if "cap_dropped" in z.files else None
    side = path[:-len(".npz")] + "_capcount.npz"
    if caps is None and os.path.exists(side):
        with np.load(side) as z:
            caps = (z["cap_dropped"], z["cap_first_bind"])
    uns = plen < 0
    early = uns & (nodes < budget)
    return _entry(os.path.basename(path), kind, budget, cap, nodes.size, uns.sum(),
                  early.sum(), early.any(axis=1).sum(),
                  nodes[early].min() if early.any() else None,
                  None if caps is None else _caps(caps[0], caps[1], ~uns))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="results/stable_ac/rank3_bf")
    ap.add_argument("--out", default=None, help="json path (default: <dir>/cap_exhaustion.json)")
    a = ap.parse_args(argv)
    files = []
    for path in sorted(glob.glob(os.path.join(a.dir, "*"))):
        name = os.path.basename(path)
        if re.fullmatch(r"rank3_bf_.+_b\d+_cap\d+_control\.jsonl", name):
            files.append(from_jsonl(path, "control", "n2_"))
        elif re.fullmatch(r"rank3_bf_.+_b\d+_cap\d+_relsub\.jsonl(\.gz)?", name):
            files.append(from_jsonl(path, "relator subwords"))
        else:
            m = re.fullmatch(r"rank3_bf_.+_b(\d+)_cap(\d+)_L(\d+)(_inv)?\.npz", name)
            if m:
                kind = f"rank 3, length {m[3]}" + (", inverse words" if m[4] else "")
                files.append(from_npz(path, kind, int(m[1]), int(m[2])))
            m = re.fullmatch(r"rankn_bf_.+_b(\d+)_cap(\d+)_r(\d+)\.npz", name)
            if m:
                files.append(from_npz(path, f"rank {m[3]}", int(m[1]), int(m[2])))
    tot = {k: sum(f[k] for f in files)
           for k in ("searches", "unsolved", "unsolved_before_budget")}
    counted = [f for f in files if f["cap_could_bind"] is not None]
    if counted:
        tot["searches_with_cap_counters"] = sum(f["searches"] for f in counted)
        tot.update({k: sum(f[k] for f in counted) for k in CAP_KEYS})
    out = {"dir": a.dir, "files": files, "total": tot}
    dst = a.out or os.path.join(a.dir, "cap_exhaustion.json")
    with open(dst, "w") as f:
        json.dump(out, f, indent=1)
    md = ["# Searches ended by the cap", "",
          "Unsolved searches that stopped below the node budget: the frontier was "
          "empty, every remaining child was over the cap.", "",
          "| file | kind | budget | cap | searches | unsolved | of those, stopped "
          "before the budget | presentations with one | fewest nodes of those |",
          "|---|---|---|---|---|---|---|---|---|"]
    for f in files:
        md.append(f"| `{f['file']}` | {f['kind']} | {f['node_budget']:,} | "
                  f"{f['max_relator_length_cap']} | {f['searches']:,} | {f['unsolved']:,} | "
                  f"{f['unsolved_before_budget']:,} | {f['presentations_with_one']:,} | "
                  f"{'' if f['fewest_nodes_of_those'] is None else f['fewest_nodes_of_those']} |")
    md += ["", f"Total: {tot['searches']:,} searches, {tot['unsolved']:,} unsolved, "
               f"{tot['unsolved_before_budget']:,} stopped before the budget.", ""]
    print(md[-2])
    if counted:
        md += ["## Children the cap dropped", "",
               "A child is dropped when one of its relators is longer than the cap. "
               "\"Could bind\" counts the searches in which a dropped child had a heap "
               "key (total length, depth) no larger than a state popped later, so a "
               "larger cap could have popped it first. Every other search is the same "
               "search at any larger cap.", "",
               "| file | kind | budget | cap | searches | cap dropped a child | could bind | "
               "of those, solved | of those, unsolved | children dropped |",
               "|---|---|---|---|---|---|---|---|---|---|"]
        for f in counted:
            md.append(f"| `{f['file']}` | {f['kind']} | {f['node_budget']:,} | "
                      f"{f['max_relator_length_cap']} | {f['searches']:,} | "
                      + " | ".join(f"{f[k]:,}" for k in CAP_KEYS) + " |")
        md += ["", f"Total with counters: {tot['searches_with_cap_counters']:,} searches, "
                   f"the cap dropped a child in {tot['cap_dropped_a_child']:,}, could bind in "
                   f"{tot['cap_could_bind']:,} ({tot['cap_could_bind_solved']:,} solved, "
                   f"{tot['cap_could_bind_unsolved']:,} unsolved).", ""]
        print(md[-2])
    with open(os.path.splitext(dst)[0] + ".md", "w") as f:
        f.write("\n".join(md))
    print(dst)


if __name__ == "__main__":
    main()
