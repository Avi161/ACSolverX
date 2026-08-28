"""W1c: bounded greedy preflight on the MMS02 bridge triples (rank 3).

Runs the repo's general-n greedy solver (experiments/stable_ac/solvern.py,
imported, unmodified) on

    Txy  = (A, B, zYX)   control: certified AC-trivial (134 primitive moves)
    Tpub = (A, B, Xyz)   target: the open bridge equation

at node budget <= 1,000 (repo hard cap for locally launched searches) and the
solver's default per-relator cap 64. A solve of Tpub at any budget proves the
bridge and hence AK(3) stably AC-trivial through the MMS02 corridor; this
preflight is expected to profile, not solve — its output sizes a production
run for Colab.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from experiments.stable_ac.solvern import Pres, search_n, str_to_word

WORD_A = "xzYXyxZXYxyZ"
WORD_B = "XyxZXYXyxzXYxy"
BUDGET = 1000  # repo hard cap for local searches; do not raise here.


def run(name, third):
    rels = tuple(
        tuple(int(g) for g in str_to_word(s))
        for s in (WORD_A, WORD_B, third)
    )
    stats = search_n(Pres(3, rels), BUDGET)
    out = {
        "triple": name,
        "third_relator": third,
        "budget": BUDGET,
        "solved": stats["solved"],
        "nodes_explored": stats["nodes_explored"],
        "path_length": stats["path_length"],
        "min_relator_length": stats["min_relator_length"],
        "max_relator_length": stats["max_relator_length"],
    }
    print(json.dumps(out))
    if stats["solved"]:
        print(f"  moves: {stats.get('path_moves', 'see stats')}")
    return stats


def main():
    control = run("Txy(control)", "zYX")
    target = run("Tpub(target)", "Xyz")
    if target["solved"]:
        print("TPUB SOLVED — bridge proved at this budget; escalate immediately.")
        return 1
    if control["solved"]:
        print("control solved; target profiled unsolved at 1,000 nodes.")
    else:
        print("neither solved at 1,000 nodes (expected for control? "
              "134-primitive-move path may exceed greedy horizon).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
