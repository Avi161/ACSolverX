#!/usr/bin/env python3
"""Build the distance-until-trivialization (d-o-t) training archive.

Reads `data/merged_best_paths.jsonl` (best path per presentation, as a state
trajectory) and produces the per-canonical-class label table the supervised
model trains on:

  For every solved presentation's path of length N, the state after move m gets
  d-o-t = N - m (one path -> N+1 labelled states, ending at the trivial state
  with d-o-t 0). Each state is keyed by its canonical form (`canon.canon_key`,
  the lab's `canonical_pair_nj`), and we keep the **minimum d-o-t ever seen** per
  class -- the only unbiased estimator, since every found path is an UPPER BOUND
  (PLAN.md sec 3).

Unsolved presentations' initial states are recorded as **right-censored** (no
point label) -- but only if that canonical class never appears on a solved path
(if it does, it is solvable and the finite label wins).

Outputs (in data/):
  dot_archive.jsonl    one record per canonical class:
      {r1, r2, total_len, min_dot, n_obs, sources, censored}
    censored=false rows carry an integer min_dot (training labels);
    censored=true rows have min_dot=null (d-o-t > budget; for the censored
    loss / auxiliary solvable head later).

Stdlib + numpy only (canon is numba-optional). Run from repo root:
    ../.venv/bin/python scripts/build_dot_archive.py
"""

import argparse
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # scripts/
import canon  # noqa: E402

MERGED = "data/derived/paths/merged_best_paths.jsonl"
OUT = "data/derived/labels/dot_archive.jsonl"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--merged", default=MERGED)
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args()

    if not os.path.exists(args.merged):
        raise SystemExit(f"not found: {args.merged} (run build_merged_paths.py first)")

    # memoize canonicalization: many intermediate states repeat across paths
    canon_cache = {}

    def ckey(r1, r2):
        k = (r1, r2)
        if k not in canon_cache:
            canon_cache[k] = canon.canon_key(r1, r2)  # (key_str, total_len)
        return canon_cache[k]

    # canonical key -> aggregate
    solved = {}        # key_str -> {min_dot, total_len, n_obs, sources:set}
    unsolved_init = {} # key_str -> {total_len, r1, r2}  (initial states of unsolved pres)
    canon_strs = {}    # key_str -> (canon_r1, canon_r2)

    n_records = n_solved = n_states = 0
    with open(args.merged) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            n_records += 1
            if not rec["solved"]:
                r1, r2 = rec["r1"], rec["r2"]
                key, tot = ckey(r1, r2)
                c1, c2 = key.split("|")
                unsolved_init[key] = {"total_len": tot}
                canon_strs[key] = (c1, c2)
                continue

            n_solved += 1
            path = rec["best_path"]           # [r1_0,r2_0, ... r1_N,r2_N]
            N = rec["best_path_length"]
            src = rec["best_source"]
            for m in range(N + 1):
                r1, r2 = path[2 * m], path[2 * m + 1]
                key, tot = ckey(r1, r2)
                dot = N - m
                n_states += 1
                if key not in solved:
                    c1, c2 = key.split("|")
                    canon_strs[key] = (c1, c2)
                    solved[key] = {"min_dot": dot, "total_len": tot,
                                   "n_obs": 1, "sources": {src}}
                else:
                    s = solved[key]
                    s["min_dot"] = min(s["min_dot"], dot)
                    s["n_obs"] += 1
                    s["sources"].add(src)

    # write archive: solved labels first, then censored unsolved-initials not
    # already present as solvable
    n_censored = 0
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as f:
        for key, s in solved.items():
            c1, c2 = canon_strs[key]
            f.write(json.dumps({
                "r1": c1, "r2": c2, "total_len": s["total_len"],
                "min_dot": s["min_dot"], "n_obs": s["n_obs"],
                "sources": sorted(s["sources"]), "censored": False,
            }) + "\n")
        for key, u in unsolved_init.items():
            if key in solved:
                continue  # solvable after all -> labelled row already written
            n_censored += 1
            c1, c2 = canon_strs[key]
            f.write(json.dumps({
                "r1": c1, "r2": c2, "total_len": u["total_len"],
                "min_dot": None, "n_obs": 0, "sources": [], "censored": True,
            }) + "\n")

    # ---- report ----
    dots = [s["min_dot"] for s in solved.values()]
    import statistics
    print(f"merged records read       : {n_records}  (solved {n_solved})")
    print(f"on-path states processed  : {n_states}")
    print(f"unique canonical classes  : {len(solved)} labelled  +  {n_censored} censored")
    print(f"min d-o-t label           : min {min(dots)}  median {statistics.median(dots):.0f}  "
          f"mean {statistics.mean(dots):.2f}  max {max(dots)}")
    src = Counter()
    for s in solved.values():
        for so in s["sources"]:
            src[so] += 1
    print(f"classes touched by source : {dict(src)} (a class can have both)")
    # label histogram
    h = Counter(min(d, 30) for d in dots)
    print("d-o-t label histogram (>=30 bucketed):")
    mx = max(h.values())
    for d in range(0, 31):
        if h.get(d):
            bar = "#" * max(1, round(40 * h[d] / mx))
            lab = f"{d:>2d}" if d < 30 else ">=30"
            print(f"  {lab} | {bar} {h[d]}")
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
