"""Independent checks for the unsolved124 × s20_mk2 census jsonl.

1. Every row has start_total / min_relator / min_delta consistent.
2. ``r1``/``r2`` match μ-ladder ``best_rep`` for that ``aca_*`` id.
3. Every solved row with path_moves replays to a trivial pair (Def 2.1).
4. Optional: exact 124 unique names when merging all chunks; ``n == names``.
5. A solve certifies **stable** AC-triviality of the class (wording only here;
   certificate = Prop A CoV chain + Thm 3 + AC path) — never AC-trivial.

    PYTHONPATH=. python3 -m experiments.heuristic_search.verify.verify_u124_s20mk2 \\
        --expect-n 124 merged.jsonl
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
from experiments.heuristic_search.runners.run_unsolved124_s20mk2 import (  # noqa: E402
    MU_SOLVE_THRESHOLD, load_mu_ladder_best_reps,
)


def verify_file(path, expect_n=None, expect_names=None, floors=None):
    if floors is None:
        floors = load_mu_ladder_best_reps()
    fails = []
    n = n_solved = n_replay = n_cov = 0
    names = set()
    with open(path) as f:
        for i, line in enumerate(f, 1):
            if not line.strip():
                continue
            r = json.loads(line)
            n += 1
            names.add(r.get("name"))
            if r.get("arm") != "s20_mk2":
                fails.append(f"{path}:{i} arm != s20_mk2")
            if r.get("depth_tie") != "+depth":
                fails.append(f"{path}:{i} depth_tie != +depth")
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
            name = r.get("name")
            if name in floors:
                fl = floors[name]
                if r.get("r1") != fl["r1"] or r.get("r2") != fl["r2"]:
                    fails.append(
                        f"{path}:{i} {name}: r1/r2 != mu-ladder best_rep")
                if bool(r.get("cov_reduced")) != bool(fl["cov_reduced"]):
                    fails.append(
                        f"{path}:{i} {name}: cov_reduced flag != ladder")
                if r.get("cov_reduced"):
                    n_cov += 1
            else:
                fails.append(f"{path}:{i} unknown name {name}")
            if mr is not None:
                if not (isinstance(mr, (list, tuple)) and len(mr) == 2):
                    fails.append(f"{path}:{i} min_relator not a pair")
                elif len(mr[0]) + len(mr[1]) != int(mrl):
                    fails.append(
                        f"{path}:{i} min_relator lengths "
                        f"{len(mr[0])+len(mr[1])} != min_relator_length {mrl}")
            if (r.get("mu_min") is not None
                    and int(r["mu_min"]) <= MU_SOLVE_THRESHOLD
                    and name == "aca_115"):
                fails.append(
                    f"{path}:{i} aca_115 mu_min={r['mu_min']} ≤ "
                    f"{MU_SOLVE_THRESHOLD}: presumed bug until reproduced "
                    "(MU_CRITERION.md)")
            if r.get("solved"):
                n_solved += 1
                if r.get("path_pending"):
                    fails.append(
                        f"{path}:{i} {r.get('name')}: path_pending still set")
                    continue
                moves_raw = r.get("path_moves") or []
                if not moves_raw:
                    fails.append(
                        f"{path}:{i} {r.get('name')}: solved, empty path_moves")
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
                elif (r.get("path_length") is not None
                      and int(r["path_length"]) != len(moves)):
                    fails.append(f"{path}:{i} path_length != len(moves)")
                else:
                    n_replay += 1
    if expect_n is not None and len(names) != expect_n:
        fails.append(f"unique names {len(names)} != expect_n {expect_n}")
    if expect_n is not None and n != len(names):
        fails.append(
            f"row count {n} != unique names {len(names)} (duplicates?)")
    if expect_n == 124 and n_cov != 36:
        fails.append(f"cov_reduced rows {n_cov} != 36 on full merge")
    if expect_names is not None and names != set(expect_names):
        missing = sorted(set(expect_names) - names)
        extra = sorted(names - set(expect_names))
        fails.append(f"name set drift missing={missing[:5]} extra={extra[:5]}")
    return {
        "n": n, "names": len(names), "solved": n_solved,
        "replay_ok": n_replay, "cov_reduced": n_cov, "fails": fails,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("jsonl", nargs="+")
    ap.add_argument("--expect-n", type=int, default=None,
                    help="required unique presentation count (use 124 after merge)")
    args = ap.parse_args()
    floors = load_mu_ladder_best_reps()
    all_fails = []
    for p in args.jsonl:
        if not os.path.exists(p):
            print(f"MISSING {p}")
            sys.exit(2)
        s = verify_file(
            p, expect_n=args.expect_n if len(args.jsonl) == 1 else None,
            floors=floors)
        print(f"{p}: rows={s['n']} names={s['names']} solved={s['solved']} "
              f"cov_reduced={s['cov_reduced']} replay_ok={s['replay_ok']} "
              f"fails={len(s['fails'])}")
        all_fails.extend(s["fails"])
    for x in all_fails[:30]:
        print("  FAIL", x)
    if all_fails:
        sys.exit(1)
    print("ALL CHECKS PASSED")
    print("Note: a solve certifies the class stably AC-trivial "
          "(Prop A + Thm 3 + AC path), never AC-trivial unqualified.")


if __name__ == "__main__":
    main()
