"""Search-by-search comparison of the same searches run at two relator caps.

    python3 -m experiments.stable_ac.rank3.cap_compare --base DIR_CAP24 \
        --other DIR_CAP32 --other DIR_CAP48 --budget 1000 --out cap_compare_b1000.json

For every result file of ``--base`` at ``--budget`` (control, relator
subwords, one array per word length) it finds the file of the same kind in
each ``--other`` directory and counts the searches whose outcome differs:
solved on one side only, a different node count, a different path length.
Searches are matched by presentation id and word, never by position alone.

Equal node counts and path lengths mean the two caps gave the same result.
They do not mean the smaller cap dropped nothing: a dropped child that the
larger cap never popped leaves no trace in either result.
"""
import argparse
import glob
import gzip
import json
import os
import re

import numpy as np

KEYS = ("searches", "solved_base", "solved_other", "solved_only_base",
        "solved_only_other", "nodes_differ", "path_length_differs",
        "both_solved_fewer_nodes_other", "both_solved_more_nodes_other")


def _rows(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as f:
        return [json.loads(line) for line in f if line.strip()]


def _count(sb, so, nb, no, pb, po):
    """Counts from aligned arrays: solved (bool), nodes, path length (-1 unsolved)."""
    both = sb & so
    return {"searches": int(sb.size), "solved_base": int(sb.sum()),
            "solved_other": int(so.sum()),
            "solved_only_base": int((sb & ~so).sum()),
            "solved_only_other": int((so & ~sb).sum()),
            "nodes_differ": int((nb != no).sum()),
            "path_length_differs": int((pb != po).sum()),
            "both_solved_fewer_nodes_other": int((both & (no < nb)).sum()),
            "both_solved_more_nodes_other": int((both & (no > nb)).sum()),
            "largest_node_difference": int(np.abs(nb - no).max()) if sb.size else 0}


def _jsonl_arrays(path, key, prefix=""):
    listed = _rows(path)
    rows = {key(r): r for r in listed}
    if len(rows) != len(listed):
        raise SystemExit(f"{path}: {len(listed) - len(rows)} repeated searches")
    return rows, lambda ks: (
        np.array([bool(rows[k][prefix + "solved"]) for k in ks]),
        np.array([rows[k][prefix + ("nodes" if prefix else "nodes_explored")]
                  for k in ks], dtype=np.int64),
        np.array([-1 if rows[k][prefix + "path_length"] is None
                  else rows[k][prefix + "path_length"] for k in ks], dtype=np.int64))


def compare_jsonl(pb, po, key, prefix=""):
    rb, fb = _jsonl_arrays(pb, key, prefix)
    ro, fo = _jsonl_arrays(po, key, prefix)
    if set(rb) != set(ro):
        raise SystemExit(f"{pb} and {po}: different searches "
                         f"({len(set(rb) ^ set(ro))} keys on one side only)")
    ks = sorted(rb)
    return _from_triples(fb(ks), fo(ks))


def _from_triples(b, o):
    return _count(b[0], o[0], b[1], o[1], b[2], o[2])


def compare_npz(pb, po):
    with np.load(pb) as zb, np.load(po) as zo:
        for k in ("pres_ids", "words"):
            if zb[k].shape != zo[k].shape or (zb[k] != zo[k]).any():
                raise SystemExit(f"{pb} and {po}: {k} differ")
        nb, no = zb["nodes"].astype(np.int64), zo["nodes"].astype(np.int64)
        lb, lo = zb["path_len"].astype(np.int64), zo["path_len"].astype(np.int64)
    if nb.shape != no.shape:
        raise SystemExit(f"{pb} and {po}: shapes differ")
    lb, lo = np.where(lb < 0, -1, lb), np.where(lo < 0, -1, lo)
    return _from_triples((lb >= 0, nb, lb), (lo >= 0, no, lo))


def _find(directory, budget, tail):
    """The one file ``rank3_bf_<source>_b<budget>_cap<cap><tail>`` of a directory."""
    hits = [p for p in glob.glob(os.path.join(directory, f"rank3_bf_*_b{budget}_cap*{tail}*"))
            if re.fullmatch(rf"rank3_bf_.+_b{budget}_cap\d+{re.escape(tail)}(\.gz)?",
                            os.path.basename(p))]
    if len(hits) != 1:
        raise SystemExit(f"{directory}: {len(hits)} files match *_b{budget}_cap*{tail}")
    return hits[0]


def _cap_of(path):
    return int(re.search(r"_cap(\d+)_", os.path.basename(path))[1])


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--other", action="append", required=True)
    ap.add_argument("--budget", type=int, required=True)
    ap.add_argument("--out", required=True, help="json path; a .md table is written beside it")
    a = ap.parse_args(argv)

    control = _find(a.base, a.budget, "_control.jsonl")
    relsub = _find(a.base, a.budget, "_relsub.jsonl")
    lengths = sorted(int(m[1]) for p in glob.glob(os.path.join(a.base, "*.npz"))
                     if (m := re.fullmatch(rf"rank3_bf_.+_b{a.budget}_cap\d+_L(\d+)\.npz",
                                           os.path.basename(p))))
    base_cap = _cap_of(control)
    out = {"budget": a.budget, "base": a.base, "base_cap": base_cap, "comparisons": []}
    for other in a.other:
        oc = _find(other, a.budget, "_control.jsonl")
        cap = _cap_of(oc)
        by_pres = lambda r: r["pres_id"]
        rows = [("control, 2 generators", compare_jsonl(control, oc, by_pres)),
                ("control, rank-n code on 2 generators",
                 compare_jsonl(control, oc, by_pres, "n2_")),
                ("control, third relator Z", compare_jsonl(control, oc, by_pres, "null_")),
                ("relator subwords", compare_jsonl(
                    relsub, _find(other, a.budget, "_relsub.jsonl"),
                    lambda r: (r["pres_id"], r["z_word"])))]
        missing = []
        for n in lengths:
            try:
                po = _find(other, a.budget, f"_L{n}.npz")
            except SystemExit:
                missing.append(n)
                continue
            rows.append((f"words of length {n}",
                         compare_npz(_find(a.base, a.budget, f"_L{n}.npz"), po)))
        words = [c for k, c in rows if k.startswith("words of length")]
        if words:
            rows.append(("all word lengths compared",
                         {k: (max if k == "largest_node_difference" else sum)(c[k] for c in words)
                          for k in words[0]}))
        out["comparisons"].append({
            "cap": cap, "dir": other, "word_lengths_not_in_other": missing,
            "rows": [dict(c, kind=k) for k, c in rows]})

    with open(a.out, "w") as f:
        json.dump(out, f, indent=1)
    md = [f"# Cap {base_cap} against other caps, budget {a.budget:,}", "",
          "Same searches at two caps, matched by presentation and word. "
          "\"only\" columns count searches solved at one cap and not the other.", ""]
    for c in out["comparisons"]:
        md += [f"## Cap {base_cap} against cap {c['cap']}", "",
               f"| searches | number | solved at {base_cap} | solved at {c['cap']} | "
               f"only at {base_cap} | only at {c['cap']} | node count differs | "
               f"path length differs | both solved, fewer nodes at {c['cap']} | "
               f"both solved, more nodes at {c['cap']} | largest node difference |",
               "|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in c["rows"]:
            md.append(f"| {r['kind']} | " + " | ".join(f"{r[k]:,}" for k in KEYS)
                      + f" | {r['largest_node_difference']:,} |")
            if r["kind"] in ("relator subwords", "all word lengths compared", "control, 2 generators"):
                print(f"b{a.budget} cap {base_cap} vs {c['cap']}: {r['kind']}: "
                      f"{r['searches']:,} searches, solved {r['solved_base']:,} vs "
                      f"{r['solved_other']:,}, only-base {r['solved_only_base']:,}, "
                      f"only-other {r['solved_only_other']:,}, nodes differ "
                      f"{r['nodes_differ']:,}, path differs {r['path_length_differs']:,}")
        if c["word_lengths_not_in_other"]:
            md.append("")
            md.append(f"Word lengths not run at cap {c['cap']}: "
                      f"{c['word_lengths_not_in_other']}.")
        md.append("")
    with open(os.path.splitext(a.out)[0] + ".md", "w") as f:
        f.write("\n".join(md))
    print(a.out)


if __name__ == "__main__":
    main()
