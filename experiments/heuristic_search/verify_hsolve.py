"""Prove ``hsolve.greedy_search_h`` is a safe drop-in for ``greedy_baseline.greedy_search``.

Three separate claims, each of which could fail without the others noticing:

1. **With no config it IS the baseline.** ``config=None`` orders by total length, so every field
   must match ``greedy_search`` exactly -- not just ``solved``/``nodes_explored`` but the min/max
   relator strings and the certificate path. If this fails the module is not a drop-in and nothing
   below matters.

2. **With a config it matches the research harness.** ``search_fast`` is what every result in this
   program was measured with. If ``greedy_search_h`` pops differently under the same ordering then
   the recommendation and the production path have diverged, and the numbers in the reports do not
   describe what a Colab run would do.

3. **The certificates are real.** A returned path is replayed *independently* -- through
   ``moves_to_states``, from the recorded Definition 2.1 moves -- and must land on a trivial pair.
   This is the check that cannot be satisfied by a self-consistent bug: the moves are decoded by a
   function that knows nothing about how they were produced.

Claim 3 is the one worth the most. A search that reports ``solved`` with a path that does not
replay would corrupt every downstream results row, and it would do so silently.

    python3 -m experiments.heuristic_search.verify_hsolve
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.search.greedy_baseline import (                    # noqa: E402
    greedy_search, moves_to_states, str_to_move,
)
from experiments.heuristic_search.hfast import search_fast          # noqa: E402
from experiments.heuristic_search.hlab import load_split            # noqa: E402
from experiments.heuristic_search.hsolve import (                   # noqa: E402
    LEAN_SMALL_BUDGET, RECOMMENDED, greedy_search_h,
)

BUDGET = 500
MRL = 48
EXACT = ("solved", "nodes_explored", "path_length", "min_relator_length",
         "max_relator_length", "max_relator_length_expanded")


def main():
    rows = load_split("train")[:8]
    fails = []

    # ---------------------------------------------------------------- 1. it is the baseline
    print("1. config=None must reproduce greedy_search exactly", flush=True)
    for r in rows:
        want = greedy_search(r["r1"], r["r2"], BUDGET, max_relator_length=MRL)
        got = greedy_search_h(r["r1"], r["r2"], BUDGET, max_relator_length=MRL, config=None)
        if set(want) != set(got):
            fails.append(f"{r['name']}: key mismatch {sorted(set(want) ^ set(got))}")
            continue
        for k in EXACT:
            if want[k] != got[k]:
                fails.append(f"{r['name']}: {k} {want[k]!r} != {got[k]!r}")
        # The path itself, not just its length.
        if want["path_moves"] != got["path_moves"]:
            fails.append(f"{r['name']}: path_moves differ")
    print(f"   {len(rows)} presentations, {len(fails)} mismatches", flush=True)

    # ------------------------------------------------- 2. under a config it matches the harness
    print("2. under a tuned config it must match search_fast", flush=True)
    n2 = 0
    for name, cfg in (("recommended", RECOMMENDED), ("lean", LEAN_SMALL_BUDGET)):
        for r in rows:
            a = search_fast(r["r1"], r["r2"], BUDGET, cfg, MRL)
            b = greedy_search_h(r["r1"], r["r2"], BUDGET, max_relator_length=MRL, config=cfg)
            n2 += 1
            if a["solved"] != b["solved"] or a["nodes"] != b["nodes_explored"]:
                fails.append(f"{name}/{r['name']}: harness {a['solved']}/{a['nodes']} vs "
                             f"production {b['solved']}/{b['nodes_explored']}")
            if a["solved"] and a["path_length"] != b["path_length"]:
                fails.append(f"{name}/{r['name']}: path_length {a['path_length']} != "
                             f"{b['path_length']}")
            if a["min_total"] != b["min_relator_length"]:
                fails.append(f"{name}/{r['name']}: min_total {a['min_total']} != "
                             f"{b['min_relator_length']}")
    print(f"   {n2} searches, {len(fails)} cumulative mismatches", flush=True)

    # ------------------------------------------------------------ 3. the certificates replay
    print("3. every returned path must replay to a trivial pair, independently", flush=True)
    checked = 0
    for cfg_name_, cfg in (("recommended", RECOMMENDED), ("lean", LEAN_SMALL_BUDGET),
                           ("baseline", None)):
        for r in rows:
            got = greedy_search_h(r["r1"], r["r2"], BUDGET, max_relator_length=MRL, config=cfg)
            if not got["solved"]:
                continue
            checked += 1
            moves = [str_to_move(m) for m in got["path_moves"]]
            states = moves_to_states(r["r1"], r["r2"], moves, cyclic_reduce=True)
            if [list(s) for s in states] != got["path"]:
                fails.append(f"{cfg_name_}/{r['name']}: replayed states != reported path")
                continue
            last = states[-1]
            if not (len(last[0]) == 1 and len(last[1]) == 1):
                fails.append(f"{cfg_name_}/{r['name']}: path does not end trivial: {last}")
    print(f"   {checked} certificates replayed, {len(fails)} cumulative mismatches", flush=True)

    print()
    if fails:
        for f in fails[:15]:
            print("   FAIL", f)
        raise SystemExit(f"{len(fails)} failures — hsolve is NOT a safe drop-in")
    print(f"ALL PASS — greedy_search_h reproduces the baseline, matches the research harness "
          f"under a tuned ordering, and its {checked} certificates replay independently.")


if __name__ == "__main__":
    main()
