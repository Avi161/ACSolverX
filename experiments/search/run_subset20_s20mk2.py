"""Baseline greedy vs. the ``s20_mk2`` heap ordering on the 20-row benchmark, budget 1,000.

    priority(r1, r2) = L + 20*S + 2*MK

A measurement script, not a production default: ``S20_MK2`` is defined here rather than exported
from ``heuristics.py``, so nothing that imports the search picks it up. Everything else — the move
generator, the reduction, the canonicalisation, the per-relator cap, the visited set and the
``(priority, depth, key)`` tie-break — is the baseline's, reached through ``greedy_search_h``. So a
difference between the two arms is attributable to the ordering and to nothing else.

The baseline arm calls ``greedy_baseline.greedy_search`` directly rather than
``greedy_search_h(config=None)``: the two are the same search pop for pop (the control gate in
``tests/test_greedy_heuristic.py`` pins that), and calling the original keeps this script honest if
the gate ever breaks.

Rows are ``benchmark/subsets/benchmark_subset_20.json`` in file order, cross-checked against the
``data/ms640_solved.txt`` line each ``pres_id`` indexes -- a stale ``r1``/``r2`` in the JSON would
otherwise silently benchmark a different presentation.

    python -m experiments.search.run_subset20_s20mk2 [--budget 1000] [--json OUT.json]
"""
import argparse
import ast
import json
import os
import statistics
import sys

from experiments.search.greedy_baseline import greedy_search
from experiments.search.heuristics import greedy_search_h

# Budget and cap are the ones CI measures at (``tests/test_greedy_heuristic.py``). A search at
# budget B is exactly the first B pops of any longer search, so the budget bounds reach, not
# behaviour; the cap is the layout of ``data/ms640_solved.txt`` (48 ints per line, 24 per relator).
DEFAULT_BUDGET = 1000
MAX_RELATOR_LENGTH = 24

# priority = L + 20*S + 2*MK. One segment, no length boundary: total length, plus penalties for the
# smaller mean block (S) and the worse relator's knot count (MK). Lower pops first.
S20_MK2 = {"segments": [{"upto": None, "w": {"L": 1.0, "S": 20.0, "MK": 2.0}}]}

_INT_TO_CHAR = {1: 'x', -1: 'X', 2: 'y', -2: 'Y'}
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_rows():
    """``[(pres_id, r1, r2)]`` for the shipped subset-20, in file order, cross-checked."""
    with open(os.path.join(_ROOT, "benchmark", "subsets", "benchmark_subset_20.json")) as f:
        subset = json.load(f)["subset"]
    with open(os.path.join(_ROOT, "data", "ms640_solved.txt")) as f:
        lines = [ast.literal_eval(ln.strip()) for ln in f if ln.strip()]

    rows = []
    for row in subset:
        pid = row["pres_id"]
        ints = lines[pid]
        half = len(ints) // 2
        r1 = ''.join(_INT_TO_CHAR[t] for t in ints[:half] if t != 0)
        r2 = ''.join(_INT_TO_CHAR[t] for t in ints[half:] if t != 0)
        if (r1, r2) != (row["r1"], row["r2"]):
            raise SystemExit(
                f"pres_id {pid}: subset JSON says {row['r1']!r}/{row['r2']!r} but "
                f"ms640_solved.txt line {pid} is {r1!r}/{r2!r}")
        rows.append((pid, r1, r2))
    return rows


def summarise(name, results):
    solved = [r for r in results.values() if r["solved"]]
    return {
        "arm": name,
        "solved": len(solved),
        "total": len(results),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--budget", type=int, default=DEFAULT_BUDGET,
                    help=f"node budget per presentation (default {DEFAULT_BUDGET})")
    ap.add_argument("--json", dest="json_out", default=None,
                    help="also write the per-row table and the summary here")
    args = ap.parse_args(argv)

    rows = load_rows()
    budget = args.budget

    baseline = {}
    s20mk2 = {}
    for pid, r1, r2 in rows:
        baseline[pid] = greedy_search(r1, r2, budget, max_relator_length=MAX_RELATOR_LENGTH)
        s20mk2[pid] = greedy_search_h(r1, r2, budget, max_relator_length=MAX_RELATOR_LENGTH,
                                      config=S20_MK2)

    # Path length is only comparable where BOTH arms produced a certificate: a row one arm failed
    # has no path to average, and dropping it from one column only would compare two different
    # row sets.
    both = [pid for pid, _, _ in rows if baseline[pid]["solved"] and s20mk2[pid]["solved"]]

    print(f"20-row benchmark subset (benchmark/subsets/benchmark_subset_20.json), "
          f"budget {budget}, cap {MAX_RELATOR_LENGTH}\n")
    hdr = (f"{'pres_id':>7}  {'bin':>3}  {'greedy':>16}   {'s20_mk2':>16}")
    print(hdr)
    print(f"{'':>7}  {'':>3}  {'nodes':>7} {'path':>8}   {'nodes':>7} {'path':>8}")
    print("-" * len(hdr))
    with open(os.path.join(_ROOT, "benchmark", "subsets", "benchmark_subset_20.json")) as f:
        bins = {r["pres_id"]: r["bin"] for r in json.load(f)["subset"]}
    for pid, _, _ in rows:
        b, h = baseline[pid], s20mk2[pid]
        bp = b["path_length"] if b["solved"] else "-"
        hp = h["path_length"] if h["solved"] else "-"
        print(f"{pid:>7}  {bins[pid]:>3}  {b['nodes_explored']:>7} {str(bp):>8}   "
              f"{h['nodes_explored']:>7} {str(hp):>8}")

    n = len(rows)
    nb = sum(1 for r in baseline.values() if r["solved"])
    nh = sum(1 for r in s20mk2.values() if r["solved"])
    print(f"\nsolved: greedy {nb}/{n}   s20_mk2 {nh}/{n}")

    summary = {
        "budget": budget,
        "max_relator_length": MAX_RELATOR_LENGTH,
        "n_rows": n,
        "greedy_solved": nb,
        "s20_mk2_solved": nh,
        "both_solved_ids": both,
        "n_both_solved": len(both),
    }

    if both:
        bpaths = [baseline[p]["path_length"] for p in both]
        hpaths = [s20mk2[p]["path_length"] for p in both]
        summary["greedy_path_mean"] = statistics.mean(bpaths)
        summary["greedy_path_median"] = statistics.median(bpaths)
        summary["s20_mk2_path_mean"] = statistics.mean(hpaths)
        summary["s20_mk2_path_median"] = statistics.median(hpaths)
        print(f"\npath length on the {len(both)} rows BOTH solve "
              f"(ids {', '.join(str(p) for p in both)}):")
        print(f"{'arm':>10}  {'mean':>8}  {'median':>8}")
        print(f"{'greedy':>10}  {statistics.mean(bpaths):>8.2f}  "
              f"{statistics.median(bpaths):>8.1f}")
        print(f"{'s20_mk2':>10}  {statistics.mean(hpaths):>8.2f}  "
              f"{statistics.median(hpaths):>8.1f}")
    else:
        print("\nno row solved by both arms -- no comparable path lengths")

    if args.json_out:
        payload = {
            "summary": summary,
            "rows": [{"pres_id": pid, "bin": bins[pid],
                      "greedy_solved": baseline[pid]["solved"],
                      "greedy_nodes": baseline[pid]["nodes_explored"],
                      "greedy_path": baseline[pid]["path_length"],
                      "s20_mk2_solved": s20mk2[pid]["solved"],
                      "s20_mk2_nodes": s20mk2[pid]["nodes_explored"],
                      "s20_mk2_path": s20mk2[pid]["path_length"]}
                     for pid, _, _ in rows],
        }
        with open(args.json_out, "w") as f:
            json.dump(payload, f, indent=2)
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
