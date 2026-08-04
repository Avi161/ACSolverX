"""Bench60: non-automorphic CoV beam + greedy @ remaining budget vs shipped g1k.

Control ``b1k_greedy_*`` is **loaded** from
``results/comparison/cov_heur_b1k_subset60.csv`` — never re-run.

Treatment: climb with ``mu_ladder_nonsym`` (n_subs>1, Aut-min after every hop,
visited = Aut-min orbits), cost-capped at 1k-node-equivalent wall time, then
length-greedy from ``best_rep`` with ``B_rem``.

    PYTHONPATH=. python3 -m experiments.heuristic_search.runners.run_bench60_covbeam_b1k
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from statistics import mean, median

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

from experiments.heuristic_search.runners.run_sweep import (  # noqa: E402
    load, subset_ids,
)
from experiments.search.greedy_baseline import greedy_search  # noqa: E402
from experiments.stable_ac.cov.ladder.mu_ladder_nonsym import (  # noqa: E402
    calibrate_node_eq_ms, climb_nonsym, remaining_budget,
)

ROOT = _d
CONTROL_CSV = os.path.join(
    ROOT, "results", "comparison", "cov_heur_b1k_subset60.csv")
OUT_DIR = os.path.join(ROOT, "results", "comparison")
TOTAL_NODES = 1000
ORIG_CAP = 24
BEAM = 10
RUNGS = 6
STOP_MU = 12


def load_control(path=CONTROL_CSV):
    """Shipped length-greedy @1000 on bench60 — do not recompute."""
    out = {}
    with open(path) as f:
        for r in csv.DictReader(f):
            pid = str(r["pres_id"])
            out[pid] = {
                "pres_id": pid,
                "bin": int(r["bin"]),
                "r1": r["r1"],
                "r2": r["r2"],
                "b1k_greedy_solved": r["b1k_greedy_solved"].strip().lower()
                in ("1", "true", "yes"),
                "b1k_greedy_nodes": (
                    int(float(r["b1k_greedy_nodes"]))
                    if r["b1k_greedy_nodes"] not in ("", None) else None),
                "b1k_greedy_path": (
                    int(float(r["b1k_greedy_path"]))
                    if r.get("b1k_greedy_path") not in ("", None) else None),
            }
    if len(out) != 60:
        raise AssertionError(f"control csv has {len(out)} rows, want 60")
    return out


def search_cap(r1, r2, base=ORIG_CAP, headroom=16):
    return max(base, max(len(r1), len(r2)) + headroom)


def run(subset_n=60, beam=BEAM, rungs=RUNGS, total_nodes=TOTAL_NODES,
        out_stem="covbeam_nonsym_b1keq_subset60"):
    os.makedirs(OUT_DIR, exist_ok=True)
    control = load_control()
    rows = load(subset_ids(subset_n))  # [(pres_id, r1, r2), ...]
    if len(rows) != subset_n:
        raise AssertionError(f"loaded {len(rows)} != {subset_n}")

    # Calibrate ms/node on a few easy rows (budget 200 — not the shipped 1k).
    calib_pairs = [(r1, r2) for _, r1, r2 in rows[:5]]
    calib = calibrate_node_eq_ms(calib_pairs, budget=200, cap=ORIG_CAP)
    node_eq_ms = calib["node_eq_ms"]
    cost_budget_ms = total_nodes * node_eq_ms
    print(f"calib node_eq_ms={node_eq_ms:.4f}  "
          f"CoV cost cap={cost_budget_ms:.1f} ms (= {total_nodes} node-eq)",
          flush=True)

    out_jsonl = os.path.join(OUT_DIR, f"{out_stem}.jsonl")
    out_csv = os.path.join(OUT_DIR, f"{out_stem}.csv")
    out_md = os.path.join(OUT_DIR, f"{out_stem}.md")

    results = []
    t_all = time.perf_counter()
    for i, (pres_id, r1, r2) in enumerate(rows):
        pid = str(pres_id)
        ctrl = control[pid]
        # Sanity: control strings match loaded subset.
        if (ctrl["r1"], ctrl["r2"]) != (r1, r2):
            raise AssertionError(
                f"{pid}: control (r1,r2) != subset load")

        climb = climb_nonsym(
            r1, r2, rungs=rungs, beam_k=beam, cap=ORIG_CAP,
            stop_mu=STOP_MU, cost_budget_ms=cost_budget_ms)
        b_rem, spent_eq = remaining_budget(
            climb["cost"]["wall_ms"], node_eq_ms, total_nodes=total_nodes)
        br1, br2 = climb["best_rep"][0], climb["best_rep"][1]
        cap = search_cap(br1, br2)

        if b_rem <= 0:
            treat = {
                "solved": False, "nodes_explored": 0,
                "path_length": None, "min_relator_length": len(br1) + len(br2),
                "skipped": True,
            }
        else:
            g = greedy_search(br1, br2, b_rem, max_relator_length=cap)
            treat = {
                "solved": bool(g["solved"]),
                "nodes_explored": int(g["nodes_explored"]),
                "path_length": g.get("path_length"),
                "min_relator_length": g.get("min_relator_length"),
                "skipped": False,
            }

        row = {
            "pres_id": pid,
            "bin": ctrl["bin"],
            "r1": r1, "r2": r2,
            "mu_in": climb["mu_in"],
            "best_mu": climb["best_mu"],
            "descended": climb["descended"],
            "best_rep": climb["best_rep"],
            "best_chain": climb["best_chain"],
            "best_nsubs": climb["best_nsubs"],
            "n_orbits_seen": climb["n_orbits_seen"],
            "stopped_reason": climb["stopped_reason"],
            "cov_wall_ms": round(climb["cost"]["wall_ms"], 3),
            "cov_n_aut_canon": climb["cost"]["n_aut_canon"],
            "cov_n_subs1_skipped": climb["cost"]["n_subs1_skipped"],
            "node_eq_ms": node_eq_ms,
            "cov_nodes_eq_spent": spent_eq,
            "B_rem": b_rem,
            "treat_cap": cap,
            "treat_solved": treat["solved"],
            "treat_nodes": treat["nodes_explored"],
            "treat_path": treat["path_length"],
            "treat_min_relator_length": treat["min_relator_length"],
            "treat_skipped": treat["skipped"],
            # shipped control — not re-run
            "b1k_greedy_solved": ctrl["b1k_greedy_solved"],
            "b1k_greedy_nodes": ctrl["b1k_greedy_nodes"],
            "b1k_greedy_path": ctrl["b1k_greedy_path"],
            "control_source": CONTROL_CSV,
        }
        results.append(row)
        print(
            f"  [{i+1:02d}/60] ms{pid}: μ {climb['mu_in']}→{climb['best_mu']} "
            f"B_rem={b_rem} treat_solved={treat['solved']} "
            f"ctrl_solved={ctrl['b1k_greedy_solved']}",
            flush=True)

    # Persist
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
            flat["best_chain"] = json.dumps(r["best_chain"])
            flat["best_nsubs"] = json.dumps(r["best_nsubs"])
            w.writerow(flat)

    n_ctrl = sum(1 for r in results if r["b1k_greedy_solved"])
    n_treat = sum(1 for r in results if r["treat_solved"])
    both = [r for r in results
            if r["b1k_greedy_solved"] and r["treat_solved"]]
    n_desc = sum(1 for r in results if r["descended"])
    lines = [
        f"# Non-automorphic CoV beam vs shipped greedy @1k (bench60)",
        "",
        f"- Control: `{CONTROL_CSV}` `b1k_greedy_*` (**not re-run**).",
        f"- Treatment: n_subs>1 CoV beam (K={beam}, rungs≤{rungs}), "
        f"Aut-min after every hop, visited=Aut-min orbits; "
        f"then length-greedy @ B_rem (cost-matched to {total_nodes} node-eq).",
        f"- calib `node_eq_ms`={node_eq_ms:.4f}; wall {time.perf_counter()-t_all:.1f}s.",
        "",
        "## Headline",
        "",
        f"- shipped greedy@1k solves: **{n_ctrl}/60**",
        f"- covbeam + greedy@B_rem solves: **{n_treat}/60**",
        f"- μ-descenders under beam: **{n_desc}/60**",
    ]
    if both:
        ctrl_nodes = [r["b1k_greedy_nodes"] for r in both]
        treat_nodes = [r["treat_nodes"] + r["cov_nodes_eq_spent"] for r in both]
        lines += [
            f"- both-solved intersection: **{len(both)}**",
            f"- mean nodes (ctrl / treat_total_eq): "
            f"{mean(ctrl_nodes):.1f} / {mean(treat_nodes):.1f}",
            f"- median nodes (ctrl / treat_total_eq): "
            f"{median(ctrl_nodes):.1f} / {median(treat_nodes):.1f}",
        ]
    # flips
    new_solves = [r["pres_id"] for r in results
                  if r["treat_solved"] and not r["b1k_greedy_solved"]]
    lost = [r["pres_id"] for r in results
            if r["b1k_greedy_solved"] and not r["treat_solved"]]
    lines += [
        "",
        f"- new solves (treat yes, ctrl no): {new_solves or '—'}",
        f"- lost solves (ctrl yes, treat no): {lost or '—'}",
        "",
        "Unsolved means unsolved within the matched budget — never a "
        "counterexample. CoV prefix is stably AC (Prop A), not AC-trivial.",
        "",
        f"Artifacts: `{out_jsonl}`, `{out_csv}`",
    ]
    with open(out_md, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return out_jsonl, out_csv, out_md


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--beam", type=int, default=BEAM)
    ap.add_argument("--rungs", type=int, default=RUNGS)
    ap.add_argument("--subset", type=int, default=60)
    args = ap.parse_args()
    run(subset_n=args.subset, beam=args.beam, rungs=args.rungs)


if __name__ == "__main__":
    main()
