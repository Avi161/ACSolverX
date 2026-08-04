"""Independent checks for the unsolved124 × s20_mk2 census jsonl.

1. Every row has start_total / min_relator / min_delta consistent.
2. Every solved row with path_moves replays to a trivial pair (Def 2.1).
3. Optional: exact 124 unique names when merging all chunks.

    PYTHONPATH=. python3 -m experiments.heuristic_search.verify.verify_u124_s20mk2 \\
        results/heuristic_search/u124_s20mk2_1m/merged_*.jsonl
"""
from __future__ import annotations

import argparse
import json
import os
import sys

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

from experiments.search.greedy_baseline import (  # noqa: E402
    moves_to_states, str_to_move,
)


def verify_file(path, expect_n=None):
    fails = []
    n = n_solved = n_replay = n_improved = 0
    names = set()
    with open(path) as f:
        for i, line in enumerate(f, 1):
            if not line.strip():
                continue
            r = json.loads(line)
            n += 1
            names.add(r.get("name"))
            st = r.get("start_total")
            mrl = r.get("min_relator_length")
            mr = r.get("min_relator")
            if st is None or mrl is None:
                fails.append(f"{path}:{i} missing start_total/min_relator_length")
                continue
            if int(st) != len(r.get("r1", "")) + len(r.get("r2", "")):
                fails.append(f"{path}:{i} start_total mismatch")
            if r.get("min_delta") != int(st) - int(mrl):
                fails.append(f"{path}:{i} min_delta mismatch")
            if bool(r.get("improved")) != (int(st) - int(mrl) > 0):
                fails.append(f"{path}:{i} improved flag mismatch")
            if mr is not None:
                if not (isinstance(mr, (list, tuple)) and len(mr) == 2):
                    fails.append(f"{path}:{i} min_relator not a pair")
                elif len(mr[0]) + len(mr[1]) != int(mrl):
                    fails.append(
                        f"{path}:{i} min_relator lengths {len(mr[0])+len(mr[1])} "
                        f"!= min_relator_length {mrl}")
                else:
                    n_improved += int(bool(r.get("improved")))
            if r.get("solved"):
                n_solved += 1
                if r.get("path_pending"):
                    fails.append(f"{path}:{i} {r.get('name')}: path_pending still set")
                    continue
                moves_raw = r.get("path_moves") or []
                if not moves_raw:
                    fails.append(f"{path}:{i} {r.get('name')}: solved, empty path_moves")
                    continue
                try:
                    moves = [str_to_move(m) if isinstance(m, str) else tuple(m)
                             for m in moves_raw]
                    states = moves_to_states(r["r1"], r["r2"], moves,
                                             cyclic_reduce=True)
                except Exception as e:  # noqa: BLE001
                    fails.append(f"{path}:{i} replay raised {e}")
                    continue
                end = states[-1]
                if not (len(end[0]) == 1 and len(end[1]) == 1):
                    fails.append(f"{path}:{i} terminal not trivial: {end}")
                else:
                    n_replay += 1
    if expect_n is not None and len(names) != expect_n:
        fails.append(f"unique names {len(names)} != expect_n {expect_n}")
    return {
        "n": n, "names": len(names), "solved": n_solved,
        "replay_ok": n_replay, "fails": fails,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("jsonl", nargs="+")
    ap.add_argument("--expect-n", type=int, default=None,
                    help="expected unique presentation count (124 after merge)")
    args = ap.parse_args()
    all_fails = []
    for p in args.jsonl:
        if not os.path.exists(p):
            print(f"MISSING {p}")
            sys.exit(2)
        s = verify_file(p, expect_n=args.expect_n if len(args.jsonl) == 1 else None)
        print(f"{p}: rows={s['n']} names={s['names']} solved={s['solved']} "
              f"replay_ok={s['replay_ok']} fails={len(s['fails'])}")
        all_fails.extend(s["fails"])
    for x in all_fails[:30]:
        print("  FAIL", x)
    if all_fails:
        sys.exit(1)
    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
