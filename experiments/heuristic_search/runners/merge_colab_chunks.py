"""Merge stride-chunked Colab jsonls (bigger-wins on duplicate keys).

    python3 -m experiments.heuristic_search.runners.merge_colab_chunks \\
      --glob 'hsearch_colab5_c*of5_*.jsonl' --out merged_colab5.jsonl

Multiple ``--dir`` values are OR-ed (stale Aut-min Drive dir + covstart dir).
"""
from __future__ import annotations

import argparse
import glob
import json
import os


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--glob", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dir", action="append", default=None,
                    help="search directory (repeatable). Default: .")
    args = ap.parse_args()
    dirs = args.dir or ["."]
    paths = []
    for d in dirs:
        paths.extend(sorted(glob.glob(os.path.join(d, args.glob))))
    paths = list(dict.fromkeys(paths))
    if not paths:
        raise SystemExit(f"no files match {args.glob!r} in {dirs}")
    best = {}  # (arm, name) -> row
    for p in paths:
        with open(p) as f:
            for line in f:
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                key = (r.get("arm"), r.get("name"))
                if key[0] is None or key[1] is None:
                    continue
                prev = best.get(key)
                if prev is None:
                    best[key] = r
                    continue

                def rank(x):
                    return (1 if x.get("solved") else 0,
                            -(x.get("nodes_explored") or 10**18))

                if rank(r) > rank(prev):
                    best[key] = r
    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    with open(args.out, "w") as f:
        for key in sorted(best):
            f.write(json.dumps(best[key]) + "\n")
    print(f"merged {len(paths)} files from {len(dirs)} dir(s) "
          f"→ {len(best)} rows → {args.out}")


if __name__ == "__main__":
    main()
