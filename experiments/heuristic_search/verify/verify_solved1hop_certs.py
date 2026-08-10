"""Replay every solved path_moves on a solved1hop jsonl through the pure-Python spec.

Independent of hsolve/hcompact: ``str_to_move`` → ``moves_to_states`` → assert
the terminal pair is two single letters. Start relators come from the freeze
(``run_ab`` rows do not store r1/r2). Refuse to publish any solve that fails.

    python3 -m experiments.heuristic_search.verify.verify_solved1hop_certs \\
        results/heuristic_search/hsearch_solved1hop_100k/merged_*.jsonl
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

FREEZE = os.path.join(
    _d, "results", "heuristic_search", "splits", "solved_1hop_autclean.json")


def _load_starts(freeze_path=FREEZE):
    data = json.load(open(freeze_path))
    return {r["name"]: (r["r1"], r["r2"]) for r in data["rows"]}


def verify_file(path, starts):
    fails = []
    n_solved = n_ok = 0
    with open(path) as f:
        for i, line in enumerate(f, 1):
            if not line.strip():
                continue
            r = json.loads(line)
            if not r.get("solved"):
                continue
            n_solved += 1
            moves_raw = r.get("path_moves") or []
            if not moves_raw:
                fails.append(f"{path}:{i} {r.get('arm')}/{r.get('name')}: "
                             "solved but empty path_moves")
                continue
            pair = starts.get(r.get("name"))
            if pair is None:
                fails.append(f"{path}:{i} {r.get('arm')}/{r.get('name')}: "
                             "name not in freeze")
                continue
            r1, r2 = pair
            try:
                moves = [str_to_move(m) for m in moves_raw]
                states = moves_to_states(r1, r2, moves, cyclic_reduce=True)
            except Exception as e:  # noqa: BLE001
                fails.append(f"{path}:{i} {r.get('arm')}/{r.get('name')}: "
                             f"replay raised {e!r}")
                continue
            last = states[-1]
            if not (len(last[0]) == 1 and len(last[1]) == 1):
                fails.append(f"{path}:{i} {r.get('arm')}/{r.get('name')}: "
                             f"not trivial: {last}")
                continue
            n_ok += 1
    return n_solved, n_ok, fails


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("jsonl", nargs="+")
    ap.add_argument("--freeze", default=FREEZE)
    args = ap.parse_args(argv)
    starts = _load_starts(args.freeze)
    all_fails = []
    tot_s = tot_ok = 0
    for path in args.jsonl:
        n_s, n_ok, fails = verify_file(path, starts)
        tot_s += n_s
        tot_ok += n_ok
        all_fails.extend(fails)
        print(f"  {path}: {n_ok}/{n_s} certificates OK, {len(fails)} fails",
              flush=True)
    if all_fails:
        for f in all_fails[:30]:
            print("FAIL", f)
        raise SystemExit(f"{len(all_fails)} certificate failures "
                         f"({tot_ok}/{tot_s} ok) — do not publish")
    print(f"ALL {tot_ok}/{tot_s} SOLVED CERTIFICATES REPLAY", flush=True)


if __name__ == "__main__":
    main()
