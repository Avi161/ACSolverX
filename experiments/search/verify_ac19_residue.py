"""Regenerate and verify the three AC19 rows that 10,000,000 nodes never solved.

    PYTHONPATH=. python -m experiments.search.verify_ac19_residue

ac19_44381, ac19_51034 and ac19_65753 are the mutual residue of every arm at
every budget through the 10M stage: `s20_mk2` failed all three at 10,000,000
nodes twice (`results/heuristic_search/ac19_10m/`), and the 501-node cascade
prefix failed them too. They are solved by the SAME cascade, with `s40_gen`'s
starter budget raised off its 500-node default -- 984, 4,272 and 4,274 nodes,
about six seconds for all three.

The stored certificate is the cascade's own mixed move-wise path (72, 48 and
49 steps), matching the campaign convention: elementary AC moves are 58,000
moves for these three and `ac_decode.decode_elementary` regenerates them on
demand. This module does that regeneration and replays the result
independently, so "solved" here means a pure elementary AC path was replayed
letter by letter to (x, y) -- not that a search reported success.
"""
from __future__ import annotations

import json
import os

ROWS = {
    "ac19_44381": {"pair": ("YXXYXXyxx", "YXyXyxxxxx"), "starter_budget": 1000},
    "ac19_51034": {"pair": ("YYXXXXYX", "YYYXYXyyX"), "starter_budget": 5000},
    "ac19_65753": {"pair": ("YXXYxYxxx", "YYYYXyXyxxx"), "starter_budget": 5000},
}

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "..", "results", "heuristic_search", "ac19_residue_solved",
                   "certificates.json")


def solve(name, log=print):
    """``(record, elementary_moves)`` for one row, replay-verified."""
    from experiments.search.cascade_heuristics import search
    from experiments.search.ac_decode import decode_elementary, replay_elementary
    spec = ROWS[name]
    pair, sb = tuple(spec["pair"]), spec["starter_budget"]
    # budget == starter_budget: s40_gen gets the whole allowance and the
    # s20_mk2 fallback never runs. It is the starter that solves these.
    res = search(pair, budget=sb, cap=64, starter_budget=sb)
    if not res["solved"]:
        raise AssertionError(f"{name} did not solve at starter_budget {sb}")
    totals = [len(a) + len(b) for a, b in res["states"]]
    moves = decode_elementary(pair, res["states"], res["steps"])
    states = replay_elementary(pair, moves, keep_states=True)
    final = states[-1]
    if sorted(w.lower() for w in final) != ["x", "y"] or \
            final[0].lower() == final[1].lower():
        raise AssertionError(f"{name} elementary replay ended at {final}")
    rec = {
        "name": name, "r1": pair[0], "r2": pair[1],
        "starter_budget": sb, "winner": res["winner"],
        "nodes_explored": res["nodes_explored"],
        "steps": len(res["states"]) - 1,
        "start_total": totals[0], "peak_total": max(totals),
        "peak_at_step": totals.index(max(totals)), "end_total": totals[-1],
        "totals": totals,
        "elementary_move_count": len(moves),
        "elementary_replay_final": list(final),
        "replay_verified": True,
        # the mixed path itself -- the certificate; elementary is regenerated
        "states": [list(s) for s in res["states"]],
        "steps_detail": [{k: v for k, v in s.items() if k != "state"}
                         for s in res["steps"]],
    }
    log(f"  {name}: {res['nodes_explored']:,} nodes -> {len(moves):,} "
        f"elementary AC moves -> {final}  (climb {totals[0]} -> "
        f"{max(totals)} -> {totals[-1]})")
    return rec, moves


def main(argv=None):
    out = []
    print("regenerating and replay-verifying the AC19 residue")
    for name in ROWS:
        rec, _ = solve(name)
        out.append(rec)
    path = os.path.normpath(OUT)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print(f"all {len(out)}/{len(ROWS)} verified; certificates at {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
