"""Sweep beam width K for nonsym CoV beam on bench60 @ greedy budget 1k.

Algorithm (per presentation, per K):
  1–4. Rung-local nonsym beam (``climb_beam``): non-automorphic CoVs →
       Whitehead Aut-min → keep top-K → repeat until μ≤12 / closed /
       ``max_aut_canon`` ladder budget.
  5. Length-greedy @ ``GREEDY_BUDGET`` from Aut-min ``best_rep``
     (local hard cap 1000).

Primary ranking: greedy solve rate /60. Secondary: μ≤12 hits_stop.
Shipped controls loaded (not re-run) from ``cov_heur_b1k_subset60.csv``.

    PYTHONPATH=. python3 -m experiments.heuristic_search.runners.sweep_bench60_nonsym_beam_k
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

from experiments.heuristic_search.runners.run_bench60_covbeam_b1k import (  # noqa: E402
    load_control, search_cap, _run_greedy, ORIG_CAP, CONTROL_CSV,
)
from experiments.heuristic_search.runners.run_sweep import (  # noqa: E402
    load, subset_ids,
)
from experiments.stable_ac.cov.ladder.autcanon_fast import warm  # noqa: E402
from experiments.stable_ac.cov.ladder.mu_ladder_nonsym_beam import (  # noqa: E402
    climb_beam,
)

ROOT = _d
OUT_DIR = os.path.join(ROOT, "results", "comparison")
GREEDY_BUDGET = 1000
LOCAL_CAP = 1000
DEFAULT_KS = (1, 2, 4, 8, 10, 16, 32)
DEFAULT_RUNGS = 32
# Ladder Whitehead budget per presentation (deterministic); separate from
# the greedy node budget. 1000 matches the "1k" work unit for Aut-min calls.
DEFAULT_MAX_AUT = 1000
STEM = "covbeam_nonsym_beam_k_sweep_b1k_subset60"


def run_sweep(ks=DEFAULT_KS, greedy_budget=GREEDY_BUDGET, rungs=DEFAULT_RUNGS,
              max_aut_canon=DEFAULT_MAX_AUT, stop_mu=12, subset_n=60):
    if greedy_budget > LOCAL_CAP:
        raise SystemExit(
            f"greedy_budget={greedy_budget} > local cap {LOCAL_CAP}")
    os.makedirs(OUT_DIR, exist_ok=True)
    warm()
    control = load_control()
    rows = load(subset_ids(subset_n))
    # JIT warm
    _run_greedy(rows[0][1], rows[0][2], 50, ORIG_CAP)

    per_k = {}
    detail_rows = []
    t_all = time.perf_counter()

    for K in ks:
        print(f"\n=== beam_k={K} ===", flush=True)
        k_rows = []
        t_k = time.perf_counter()
        for i, (pres_id, r1, r2) in enumerate(rows):
            pid = str(pres_id)
            ctrl = control[pid]
            climb = climb_beam(
                r1, r2, beam_k=K, rungs=rungs, cap=ORIG_CAP,
                stop_mu=stop_mu, max_aut_canon=max_aut_canon)
            br1, br2 = climb["best_rep"][0], climb["best_rep"][1]
            treat_cap = search_cap(br1, br2)
            treat = _run_greedy(br1, br2, greedy_budget, treat_cap)
            row = {
                "pres_id": pid,
                "bin": ctrl["bin"],
                "beam_k": K,
                "mu_in": climb["mu_in"],
                "best_mu": climb["best_mu"],
                "hits_stop": climb["hits_stop"],
                "descended": climb["descended"],
                "best_rep": climb["best_rep"],
                "best_chain": climb["best_chain"],
                "chain_len": len(climb["best_chain"]),
                "n_orbits_seen": climb["n_orbits_seen"],
                "stopped_reason": climb["stopped_reason"],
                "n_aut_canon": climb["cost"]["n_aut_canon"],
                "n_expanded": climb["cost"]["n_expanded"],
                "n_rungs": climb["cost"]["n_rungs"],
                "treat_cap": treat_cap,
                "greedy_budget": greedy_budget,
                "greedy_solved": treat["solved"],
                "greedy_nodes": treat["nodes_explored"],
                "greedy_path": treat["path_length"],
                "greedy_min_relator_length": treat["min_relator_length"],
                "b1k_greedy_solved": ctrl["b1k_greedy_solved"],
                "b1k_heur_solved": ctrl["b1k_heur_solved"],
                "b1k_covgreedy_solved": ctrl["b1k_covgreedy_solved"],
            }
            k_rows.append(row)
            detail_rows.append(row)
            print(
                f"  [{i+1:02d}/{subset_n}] k={K} ms{pid}: "
                f"μ {climb['mu_in']}→{climb['best_mu']} "
                f"hit={climb['hits_stop']} "
                f"g={treat['solved']}/{treat['nodes_explored']} "
                f"n_ac={climb['cost']['n_aut_canon']}",
                flush=True)
        n_hit = sum(1 for r in k_rows if r["hits_stop"])
        n_sol = sum(1 for r in k_rows if r["greedy_solved"])
        n_desc = sum(1 for r in k_rows if r["descended"])
        mean_ac = sum(r["n_aut_canon"] for r in k_rows) / len(k_rows)
        per_k[K] = {
            "beam_k": K,
            "n": subset_n,
            "hits_stop": n_hit,
            "greedy_solved": n_sol,
            "descended": n_desc,
            "mean_n_aut_canon": round(mean_ac, 1),
            "wall_s": round(time.perf_counter() - t_k, 1),
        }
        print(
            f"  k={K} summary: hits_stop={n_hit}/{subset_n} "
            f"greedy={n_sol}/{subset_n} wall={per_k[K]['wall_s']}s",
            flush=True)

    # Rank: primary greedy_solved, tie-break hits_stop, then smaller K.
    ranked = sorted(
        per_k.values(),
        key=lambda s: (-s["greedy_solved"], -s["hits_stop"], s["beam_k"]))
    best = ranked[0]

    out_jsonl = os.path.join(OUT_DIR, f"{STEM}.jsonl")
    out_csv = os.path.join(OUT_DIR, f"{STEM}.csv")
    out_sum = os.path.join(OUT_DIR, f"{STEM}_summary.csv")
    out_md = os.path.join(OUT_DIR, f"{STEM}.md")

    with open(out_jsonl, "w") as f:
        for r in detail_rows:
            f.write(json.dumps(r) + "\n")

    fields = [k for k in detail_rows[0]]
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in detail_rows:
            flat = dict(r)
            flat["best_rep"] = json.dumps(r["best_rep"])
            flat["best_chain"] = json.dumps(r["best_chain"])
            w.writerow(flat)

    sum_fields = list(ranked[0].keys())
    with open(out_sum, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=sum_fields)
        w.writeheader()
        for s in sorted(per_k.values(), key=lambda x: x["beam_k"]):
            w.writerow(s)

    n_g = sum(1 for r in control.values() if r["b1k_greedy_solved"])
    n_h = sum(1 for r in control.values() if r["b1k_heur_solved"])
    n_cg = sum(1 for r in control.values() if r["b1k_covgreedy_solved"])
    wall = time.perf_counter() - t_all

    lines = [
        "# Nonsym CoV beam — K sweep @ greedy budget 1,000 (bench60)",
        "",
        "Algorithm: non-automorphic CoV → Whitehead Aut-min → keep top-K → "
        "repeat until μ≤12 / closed / "
        f"`max_aut_canon={max_aut_canon}`; then length-greedy @ "
        f"{greedy_budget} from Aut-min `best_rep`.",
        "",
        f"Controls (loaded, not re-run) from `{CONTROL_CSV}`: "
        f"greedy {n_g}/60, heur {n_h}/60, covgreedy {n_cg}/60.",
        "",
        "## Sweep",
        "",
        "| K | hits_stop (μ≤12) | greedy@1k solved | descended | mean n_aut_canon | wall_s |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for s in sorted(per_k.values(), key=lambda x: x["beam_k"]):
        mark = " ← best" if s["beam_k"] == best["beam_k"] else ""
        lines.append(
            f"| {s['beam_k']} | **{s['hits_stop']}**/60 | "
            f"**{s['greedy_solved']}**/60 | {s['descended']}/60 | "
            f"{s['mean_n_aut_canon']} | {s['wall_s']}{mark} |")
    lines += [
        "",
        f"**Best K = {best['beam_k']}** by greedy@1k solve rate "
        f"({best['greedy_solved']}/60), tie-break hits_stop="
        f"{best['hits_stop']}/60, then smaller K.",
        "",
        "Claim hygiene: μ≤12 is a *stable*-AC-triviality lead "
        "(MU_CRITERION), not an AC solve. Greedy solves certify the "
        "Aut-min start is AC-trivial within budget; source is stably "
        "AC-trivial via Prop A + Thm 3 + path.",
        "",
        f"Next: re-run best K={best['beam_k']} at greedy budget 10k on Colab "
        f"(`run_covbeam_greedy_from_climb` / dedicated notebook).",
        "",
        f"Wall {wall:.1f}s. Artifacts: `{STEM}.*`.",
    ]
    with open(out_md, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return best, out_md


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ks", type=str, default=",".join(str(k) for k in DEFAULT_KS))
    ap.add_argument("--budget", type=int, default=GREEDY_BUDGET)
    ap.add_argument("--rungs", type=int, default=DEFAULT_RUNGS)
    ap.add_argument("--max-aut-canon", type=int, default=DEFAULT_MAX_AUT)
    ap.add_argument("--stop-mu", type=int, default=12)
    args = ap.parse_args()
    ks = tuple(int(x) for x in args.ks.split(",") if x.strip())
    run_sweep(ks=ks, greedy_budget=args.budget, rungs=args.rungs,
              max_aut_canon=args.max_aut_canon, stop_mu=args.stop_mu)


if __name__ == "__main__":
    main()
