"""Regenerate the committed golden baseline.

    .venv/bin/python3 -m experiments.greedy_tests.tools.regen_golden

A golden failure means the search returns different results than it used to.
That is a **result change**, not a stale fixture. Find out why before running
this, and say why in the commit message.

Only deterministic fields are recorded. ``min_relator`` and ``max_relator`` are
excluded on purpose: the normal solver picks them with ``min()``/``max()`` over
a ``set``, so ties are broken by ``PYTHONHASHSEED`` and the strings vary between
processes and between the normal and heavy solvers. Their *lengths* never do.
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))

from experiments.search.greedy_baseline import greedy_search  # noqa: E402
from experiments.greedy_tests.fixtures.presentations import (  # noqa: E402
    MS640, MS_UNSOLVED, load_dataset, repo_root,
)

GOLDEN = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "golden", "greedy_golden.json")

RECORDED = (
    "solved", "nodes_explored", "path_length", "min_relator_length",
    "max_relator_length", "max_relator_length_expanded", "max_relator_expanded",
)


def _cases():
    """(dataset, pres_id, budget, cap, cyclic, tier)."""
    for i in range(0, 15):
        yield (MS640, i, 2000, 24, True, "fast")
    for i in (0, 1, 2):
        yield (MS640, i, 2000, 24, False, "fast")
    for i in (0, 1, 2):
        yield (MS_UNSOLVED, i, 1500, 24, True, "fast")

    # The sweep CLAUDE.md records as 10 solved / 10 budget-capped.
    for i in range(620, 640):
        yield (MS640, i, 30000, 24, True, "slow")
    # cap24 vs cap48 on the two cases recorded as giving identical traces.
    for i in (621, 630):
        yield (MS640, i, 30000, 48, True, "slow")


def main():
    cache = {}
    entries = []
    t0 = time.time()
    for dataset, pid, budget, cap, cyclic, tier in _cases():
        if dataset not in cache:
            cache[dataset] = load_dataset(dataset)
        pres = cache[dataset][pid]
        r1, r2 = pres.to_strs()
        t = time.time()
        stats = greedy_search(r1, r2, budget, max_relator_length=cap,
                              cyclic_reduce=cyclic)
        row = {
            "dataset": dataset, "pres_id": pid, "budget": budget, "cap": cap,
            "cyclic": cyclic, "tier": tier,
        }
        row.update({k: stats[k] for k in RECORDED})
        entries.append(row)
        print(f"  {dataset} {pid} b={budget} cap={cap} cyc={cyclic} -> "
              f"solved={stats['solved']} nodes={stats['nodes_explored']} "
              f"({time.time() - t:.1f}s)", flush=True)

    payload = {
        "note": "Deterministic fields only; min_relator/max_relator strings are "
                "PYTHONHASHSEED-dependent and deliberately excluded.",
        "regen": "python3 -m experiments.greedy_tests.tools.regen_golden",
        "entries": entries,
    }
    os.makedirs(os.path.dirname(GOLDEN), exist_ok=True)
    with open(GOLDEN, "w") as f:
        json.dump(payload, f, indent=1, sort_keys=True)
        f.write("\n")
    print(f"wrote {len(entries)} entries to {GOLDEN} in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
