"""K=4 nonsym beam starts × s20_mk2 search @1k (same climb as the 49/60 run).

Reuses ``covbeam_nonsym_beam_k4_climb_subset60.jsonl`` so the CoV beam /
Aut-min / visited / K=4 path is **bit-identical**; only the terminal search
ordering changes:

  * length-greedy  (reproduce the 49/60 headline)
  * ``s20_mk2 = L + 20·S + 2·MK``

Local budget hard-capped at 1000.

    PYTHONPATH=. python3 -m experiments.heuristic_search.runners.run_bench60_beam_k4_s20mk2_b1k
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

from experiments.heuristic_search.core.hsolve import greedy_search_h  # noqa: E402
from experiments.heuristic_search.runners.run_bench60_covbeam_b1k import (  # noqa: E402
    CONTROL_CSV, ORIG_CAP, load_control, search_cap, _run_greedy,
)
from experiments.search.greedy_baseline import greedy_search  # noqa: E402

ROOT = _d
OUT_DIR = os.path.join(ROOT, "results", "comparison")
CLIMB_JSONL = os.path.join(
    ROOT, "results", "comparison", "covbeam_nonsym_beam_k4_climb_subset60.jsonl")
BUDGET = 1000
LOCAL_CAP = 1000
S20_MK2 = {"segments": [{"upto": None, "w": {"L": 1.0, "S": 20.0, "MK": 2.0}}]}
STEM = "covbeam_nonsym_beam_k4_s20mk2_b1k_subset60"


def load_climb(path=CLIMB_JSONL):
    out = {}
    with open(path) as f:
        for line in f:
            r = json.loads(line)
            out[str(r["pres_id"])] = r
    if len(out) != 60:
        raise AssertionError(f"climb has {len(out)} rows, want 60")
    return out


def run(budget=BUDGET, climb_path=CLIMB_JSONL):
    if budget > LOCAL_CAP:
        raise SystemExit(f"budget={budget} > local cap {LOCAL_CAP}")
    os.makedirs(OUT_DIR, exist_ok=True)
    control = load_control()
    climb = load_climb(climb_path)

    # JIT
    sample = next(iter(climb.values()))
    br = sample["best_rep"]
    if isinstance(br, str):
        br = json.loads(br)
    greedy_search(br[0], br[1], 50, max_relator_length=ORIG_CAP)
    greedy_search_h(br[0], br[1], 50, max_relator_length=ORIG_CAP,
                    config=S20_MK2)

    results = []
    t0 = time.perf_counter()
    for i, pid in enumerate(sorted(climb, key=lambda x: (len(x), x))):
        c = climb[pid]
        ctrl = control[pid]
        br = c["best_rep"]
        if isinstance(br, str):
            br = json.loads(br)
        r1, r2 = br[0], br[1]
        cap = int(c.get("treat_cap") or search_cap(r1, r2))

        g_len = _run_greedy(r1, r2, budget, cap)
        g_s20 = greedy_search_h(r1, r2, budget, max_relator_length=cap,
                                config=S20_MK2)
        row = {
            "pres_id": pid,
            "bin": ctrl["bin"],
            "mu_in": c["mu_in"],
            "best_mu": c["best_mu"],
            "hits_stop": c.get("hits_stop"),
            "best_rep": list(br),
            "treat_cap": cap,
            "beam_k": 4,
            "budget": budget,
            # same climb, length-greedy (should reproduce ~49)
            "length_solved": bool(g_len["solved"]),
            "length_nodes": int(g_len["nodes_explored"]),
            "length_path": g_len["path_length"],
            # s20_mk2
            "s20_mk2_solved": bool(g_s20["solved"]),
            "s20_mk2_nodes": int(g_s20["nodes_explored"]),
            "s20_mk2_path": g_s20.get("path_length"),
            # shipped
            "b1k_greedy_solved": ctrl["b1k_greedy_solved"],
            "b1k_heur_solved": ctrl["b1k_heur_solved"],
            "b1k_covgreedy_solved": ctrl["b1k_covgreedy_solved"],
            "climb_source": climb_path,
        }
        results.append(row)
        print(
            f"  [{i+1:02d}/60] ms{pid}: μ {c['mu_in']}→{c['best_mu']} "
            f"len={row['length_solved']}/{row['length_nodes']} "
            f"s20={row['s20_mk2_solved']}/{row['s20_mk2_nodes']}",
            flush=True)

    out_jsonl = os.path.join(OUT_DIR, f"{STEM}.jsonl")
    out_csv = os.path.join(OUT_DIR, f"{STEM}.csv")
    out_md = os.path.join(OUT_DIR, f"{STEM}.md")

    with open(out_jsonl, "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")

    fields = list(results[0].keys())
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in results:
            flat = dict(r)
            flat["best_rep"] = json.dumps(r["best_rep"])
            w.writerow(flat)

    n = len(results)
    n_len = sum(1 for r in results if r["length_solved"])
    n_s20 = sum(1 for r in results if r["s20_mk2_solved"])
    n_g = sum(1 for r in results if r["b1k_greedy_solved"])
    n_h = sum(1 for r in results if r["b1k_heur_solved"])
    n_cg = sum(1 for r in results if r["b1k_covgreedy_solved"])

    both = [r["pres_id"] for r in results
            if r["length_solved"] and r["s20_mk2_solved"]]
    only_len = [r["pres_id"] for r in results
                if r["length_solved"] and not r["s20_mk2_solved"]]
    only_s20 = [r["pres_id"] for r in results
                if r["s20_mk2_solved"] and not r["length_solved"]]

    # mean nodes on intersection
    inter = [r for r in results if r["length_solved"] and r["s20_mk2_solved"]]
    mean_len = (sum(r["length_nodes"] for r in inter) / len(inter)
                if inter else None)
    mean_s20 = (sum(r["s20_mk2_nodes"] for r in inter) / len(inter)
                if inter else None)

    wall = time.perf_counter() - t0
    lines = [
        "# K=4 nonsym beam → s20_mk2 vs length-greedy @1k (bench60)",
        "",
        "Same climb jsonl as the K=4 sweep "
        f"(`{os.path.basename(climb_path)}`): nonsym CoV beam, Aut-min every "
        "hop, global visited, K=4. Only the terminal search ordering changes.",
        "",
        f"`s20_mk2` = `L + 20·S + 2·MK`. Budget {budget}.",
        "",
        "## Solve rates",
        "",
        "| arm | solved |",
        "|---|---:|",
        f"| shipped `b1k_greedy` (original) | **{n_g}**/60 |",
        f"| shipped `b1k_heur` (RECOMMENDED, original) | **{n_h}**/60 |",
        f"| shipped `b1k_covgreedy` (oracle CoV) | **{n_cg}**/60 |",
        f"| K=4 beam → **length-greedy** @1k | **{n_len}**/60 |",
        f"| K=4 beam → **s20_mk2** @1k | **{n_s20}**/60 |",
        "",
        f"- Both solve: {len(both)}/60",
        f"- Length only: {only_len or '—'}",
        f"- s20_mk2 only: {only_s20 or '—'}",
    ]
    if inter:
        lines += [
            f"- Mean nodes on both-solved intersection (n={len(inter)}): "
            f"length {mean_len:.1f}, s20_mk2 {mean_s20:.1f}",
        ]
    lines += [
        "",
        f"Wall {wall:.1f}s. Artifacts: `{STEM}.*`.",
        "",
        f"Controls loaded from `{CONTROL_CSV}` (not re-run).",
    ]
    with open(out_md, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return out_md


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--budget", type=int, default=BUDGET)
    ap.add_argument("--climb", type=str, default=CLIMB_JSONL)
    args = ap.parse_args()
    run(budget=args.budget, climb_path=args.climb)


if __name__ == "__main__":
    main()
