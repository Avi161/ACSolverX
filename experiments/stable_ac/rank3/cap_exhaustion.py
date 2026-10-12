"""How often the relator-length cap alone ends a search.

The search loop is ``while heap and nodes < budget``. An unsolved search that
stopped below its node budget therefore ran out of states: every child it
still had was dropped by the cap. This counts those searches in every result
file of a directory (controls, rank-3 lengths, relator subwords, rank 4/5).

    python3 -m experiments.stable_ac.rank3.cap_exhaustion --dir results/stable_ac/rank3_bf

It does not count children the cap dropped inside searches that went on; that
is not stored. The cap-sensitivity runs (PLAN section 11) measure that part.
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


def _entry(name, kind, budget, cap, searches, unsolved, early, pres_early, min_nodes):
    return {"file": name, "kind": kind, "node_budget": int(budget),
            "max_relator_length_cap": int(cap), "searches": int(searches),
            "unsolved": int(unsolved), "unsolved_before_budget": int(early),
            "presentations_with_one": int(pres_early),
            "fewest_nodes_of_those": None if min_nodes is None else int(min_nodes)}


def from_jsonl(path, kind):
    rows = _rows(path)
    uns = [r for r in rows if not r["solved"]]
    early = [r for r in uns if r["nodes_explored"] < r["node_budget"]]
    return _entry(os.path.basename(path), kind, rows[0]["node_budget"],
                  rows[0]["max_relator_length_cap"], len(rows), len(uns), len(early),
                  len({r["pres_id"] for r in early}),
                  min((r["nodes_explored"] for r in early), default=None))


def from_npz(path, kind, budget, cap):
    with np.load(path) as z:
        nodes = z["nodes"].astype(np.int64)
        plen = z["path_len"].astype(np.int64)
    uns = plen < 0
    early = uns & (nodes < budget)
    return _entry(os.path.basename(path), kind, budget, cap, nodes.size, uns.sum(),
                  early.sum(), early.any(axis=1).sum(),
                  nodes[early].min() if early.any() else None)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="results/stable_ac/rank3_bf")
    ap.add_argument("--out", default=None, help="json path (default: <dir>/cap_exhaustion.json)")
    a = ap.parse_args(argv)
    files = []
    for path in sorted(glob.glob(os.path.join(a.dir, "*"))):
        name = os.path.basename(path)
        if re.fullmatch(r"rank3_bf_.+_b\d+_cap\d+_control\.jsonl", name):
            files.append(from_jsonl(path, "control"))
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
    with open(os.path.splitext(dst)[0] + ".md", "w") as f:
        f.write("\n".join(md))
    print(md[-2])
    print(dst)


if __name__ == "__main__":
    main()
