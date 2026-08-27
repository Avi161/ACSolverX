"""Greedy (length-only) vs S20_MK2 on the shipped 20-row benchmark, same node budget.

S20_MK2 is not "subset-20 mark 2". It is the heap ordering

    priority(r1, r2) = L + 20*S + 2*MK

already in this Andrews-Curtis solver: total length plus a weight-20 penalty on
the smaller mean block (S) and a weight-2 penalty on max knots (MK). On ``main``
the named constant is not imported (``RECOMMENDED`` still ships there); the
formula lives as ``S20_MK2`` on the research branch
``claude/heuristic-search-benchmark-e1f9l8``. This runner passes that weight
vector through ``greedy_search_h`` and does not change the solver.

The length-only arm is the same function with ``config=None``, which the control
gate in ``tests/test_greedy_heuristic.py`` pins as pop-for-pop identical to
``greedy_baseline.greedy_search``.

Default subset and budget match what Avi asked for: the frozen 20-row list and
a 1,000-node ceiling.

    python experiments/search/compare_greedy_s20mk2_subset20.py
    python experiments/search/compare_greedy_s20mk2_subset20.py \\
        --subset benchmark/subsets/benchmark_subset_20.json \\
        --budget 1000 --max-relator-length 24
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

# Repo root on sys.path so this file can be run as a script from anywhere.
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from experiments.search.heuristics import greedy_search_h

# Named constant on the research branch; fallback is that same vector, not a new one.
try:
    from experiments.search.heuristics import S20_MK2 as _S20_MK2
except ImportError:  # pragma: no cover - main does not export the name
    _S20_MK2 = {"segments": [{"upto": None, "w": {"L": 1.0, "S": 20.0, "MK": 2.0}}]}

S20_MK2 = _S20_MK2
DEFAULT_SUBSET = _ROOT / "benchmark" / "subsets" / "benchmark_subset_20.json"
DEFAULT_BUDGET = 1000
DEFAULT_CAP = 24


def _mean(xs):
    return statistics.fmean(xs) if xs else None


def _median(xs):
    return float(statistics.median(xs)) if xs else None


def load_subset(path):
    with open(path) as fh:
        doc = json.load(fh)
    rows = doc["subset"]
    if len(rows) != 20:
        raise SystemExit(f"{path} has {len(rows)} rows, expected 20")
    return doc, rows


def run_arm(rows, config, budget, cap):
    out = {}
    for row in rows:
        pid = row["pres_id"]
        stats = greedy_search_h(
            row["r1"], row["r2"],
            node_budget=budget,
            max_relator_length=cap,
            config=config,
        )
        out[pid] = {
            "pres_id": pid,
            "bin": row["bin"],
            "r1": row["r1"],
            "r2": row["r2"],
            "solved": bool(stats["solved"]),
            "nodes_explored": stats["nodes_explored"],
            "path_length": stats["path_length"],
        }
    return out


def summarise(greedy, s20, budget, cap, subset_path):
    g_solved = sorted(p for p, r in greedy.items() if r["solved"])
    s_solved = sorted(p for p, r in s20.items() if r["solved"])
    both = sorted(set(g_solved) & set(s_solved))
    g_paths = [greedy[p]["path_length"] for p in both]
    s_paths = [s20[p]["path_length"] for p in both]
    return {
        "subset": str(subset_path),
        "n": 20,
        "node_budget": budget,
        "budget_flag": "--budget",
        "max_relator_length": cap,
        "greedy": {
            "entry": "experiments.search.heuristics.greedy_search_h(config=None)",
            "config": None,
            "n_solved": len(g_solved),
            "solved_ids": g_solved,
            "failed_ids": sorted(p for p in greedy if p not in set(g_solved)),
        },
        "s20mk2": {
            "entry": "experiments.search.heuristics.greedy_search_h(config=S20_MK2)",
            "formula": "L + 20*S + 2*MK",
            "config": S20_MK2,
            "n_solved": len(s_solved),
            "solved_ids": s_solved,
            "failed_ids": sorted(p for p in s20 if p not in set(s_solved)),
        },
        "both_solved": {
            "n": len(both),
            "ids": both,
            "greedy_mean_path": _mean(g_paths),
            "greedy_median_path": _median(g_paths),
            "s20mk2_mean_path": _mean(s_paths),
            "s20mk2_median_path": _median(s_paths),
        },
        "rows": [
            {
                "pres_id": pid,
                "bin": greedy[pid]["bin"],
                "greedy_solved": greedy[pid]["solved"],
                "greedy_nodes": greedy[pid]["nodes_explored"],
                "greedy_path": greedy[pid]["path_length"],
                "s20mk2_solved": s20[pid]["solved"],
                "s20mk2_nodes": s20[pid]["nodes_explored"],
                "s20mk2_path": s20[pid]["path_length"],
            }
            for pid in greedy
        ],
    }


def print_report(summary):
    g, s, both = summary["greedy"], summary["s20mk2"], summary["both_solved"]
    print(f"subset:  {summary['subset']}")
    print(f"budget:  {summary['budget_flag']} {summary['node_budget']}")
    print(f"cap:     --max-relator-length {summary['max_relator_length']}")
    print(f"greedy:  {g['n_solved']}/20  solved={g['solved_ids']}  failed={g['failed_ids']}")
    print(f"s20mk2:  {s['n_solved']}/20  solved={s['solved_ids']}  failed={s['failed_ids']}")
    print(f"both:    {both['n']} presentations")
    if both["n"]:
        print(f"  greedy  mean path {both['greedy_mean_path']:.4f}  "
              f"median path {both['greedy_median_path']:.4f}")
        print(f"  s20mk2  mean path {both['s20mk2_mean_path']:.4f}  "
              f"median path {both['s20mk2_median_path']:.4f}")
    print()
    print(f"{'pres_id':>8} {'bin':>4} {'g_ok':>5} {'g_nodes':>8} {'g_path':>7} "
          f"{'s_ok':>5} {'s_nodes':>8} {'s_path':>7}")
    for row in summary["rows"]:
        gp = "-" if row["greedy_path"] is None else row["greedy_path"]
        sp = "-" if row["s20mk2_path"] is None else row["s20mk2_path"]
        print(f"{row['pres_id']:8d} {row['bin']:4d} "
              f"{str(row['greedy_solved']):>5} {row['greedy_nodes']:8d} {str(gp):>7} "
              f"{str(row['s20mk2_solved']):>5} {row['s20mk2_nodes']:8d} {str(sp):>7}")


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    p.add_argument("--subset", type=Path, default=DEFAULT_SUBSET,
                   help="path to benchmark_subset_20.json")
    p.add_argument("--budget", type=int, default=DEFAULT_BUDGET,
                   help="max nodes popped per presentation (node_budget)")
    p.add_argument("--max-relator-length", type=int, default=DEFAULT_CAP,
                   help="per-relator cap (ms640 layout is 24)")
    p.add_argument("--out", type=Path, default=None,
                   help="write the summary JSON here (default: results/comparison/...)")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    subset_path = args.subset if args.subset.is_absolute() else _ROOT / args.subset
    _, rows = load_subset(subset_path)
    greedy = run_arm(rows, None, args.budget, args.max_relator_length)
    s20 = run_arm(rows, S20_MK2, args.budget, args.max_relator_length)
    try:
        subset_recorded = Path(subset_path).resolve().relative_to(_ROOT).as_posix()
    except ValueError:
        subset_recorded = str(subset_path)
    summary = summarise(greedy, s20, args.budget, args.max_relator_length, subset_recorded)
    print_report(summary)
    out = args.out
    if out is None:
        out = _ROOT / "results" / "comparison" / f"greedy_vs_s20mk2_subset20_b{args.budget}.json"
    elif not out.is_absolute():
        out = _ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as fh:
        json.dump(summary, fh, indent=2)
        fh.write("\n")
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
