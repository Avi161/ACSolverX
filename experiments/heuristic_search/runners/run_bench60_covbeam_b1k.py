"""Bench60 non-automorphic CoV best-first vs shipped greedy@1k (advisor-REVISE).

Control arms are **loaded** from ``cov_heur_b1k_subset60.csv`` (never re-run):
``b1k_greedy`` (29/60), ``b1k_heur`` (43/60), ``b1k_covgreedy`` (45/60).

Per row (one regenerable script):
  1. ``climb_nonsym`` — best-first, n_subs>1, Aut-min after hop, full provenance,
     ``autcanon_fast``; charge unit = ``n_aut_canon``.
  2. length-greedy @1000 from ``best_rep`` at ``treat_cap`` (full-1k / α=0 end).
  3. Cap controls @1000 at the **same** ``treat_cap``:
       (a) original pair; (b) Aut-min(original) — Thm-3 relabel, zero CoV.
  4. Rescore α-sweep from (2) with zero extra search:
       solved(α) = treat_solved and treat_nodes ≤ 1000 − α·n_aut_canon.

Headline claims follow ac-advisor Q5 (cost-matched α arm under-powered when
α·n_aut_canon ≥ 1000; full-1k framed vs b1k_heur / oracle, not raw +12).

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
from experiments.stable_ac.cov.ladder.autcanon_fast import aut_min  # noqa: E402
from experiments.stable_ac.cov.ladder.mu_ladder_nonsym import (  # noqa: E402
    climb_nonsym, solved_at_alpha,
)

ROOT = _d
CONTROL_CSV = os.path.join(
    ROOT, "results", "comparison", "cov_heur_b1k_subset60.csv")
OUT_DIR = os.path.join(ROOT, "results", "comparison")
TOTAL_NODES = 1000
ORIG_CAP = 24
# α grid: nodes charged per aut_canon call (0 = full 1k search, CoV free).
ALPHAS = (0, 1, 2, 5, 10, 15, 33)
STEM = "covbeam_nonsym_b1kfull_subset60"
STEM_EQ = "covbeam_nonsym_b1keq_subset60"  # α-sweep summary companion


def load_control(path=CONTROL_CSV):
    out = {}
    with open(path) as f:
        for r in csv.DictReader(f):
            pid = str(r["pres_id"])

            def _bool(k):
                return r[k].strip().lower() in ("1", "true", "yes")

            def _int(k):
                return (int(float(r[k])) if r.get(k) not in ("", None) else None)

            out[pid] = {
                "pres_id": pid,
                "bin": int(r["bin"]),
                "r1": r["r1"], "r2": r["r2"],
                "b1k_greedy_solved": _bool("b1k_greedy_solved"),
                "b1k_greedy_nodes": _int("b1k_greedy_nodes"),
                "b1k_heur_solved": _bool("b1k_heur_solved"),
                "b1k_heur_nodes": _int("b1k_heur_nodes"),
                "b1k_covgreedy_solved": _bool("b1k_covgreedy_solved"),
                "b1k_covgreedy_nodes": _int("b1k_covgreedy_nodes"),
            }
    if len(out) != 60:
        raise AssertionError(f"control csv has {len(out)} rows, want 60")
    return out


def search_cap(r1, r2, base=ORIG_CAP, headroom=16):
    return max(base, max(len(r1), len(r2)) + headroom)


def _run_greedy(r1, r2, budget, cap):
    if budget <= 0:
        return {"solved": False, "nodes_explored": 0, "path_length": None,
                "min_relator_length": len(r1) + len(r2)}
    g = greedy_search(r1, r2, budget, max_relator_length=cap)
    return {
        "solved": bool(g["solved"]),
        "nodes_explored": int(g["nodes_explored"]),
        "path_length": g.get("path_length"),
        "min_relator_length": g.get("min_relator_length"),
    }


def run(subset_n=60, max_expand=64, total_nodes=TOTAL_NODES,
        alphas=ALPHAS, do_cap_controls=True):
    os.makedirs(OUT_DIR, exist_ok=True)
    control = load_control()
    rows = load(subset_ids(subset_n))
    if len(rows) != subset_n:
        raise AssertionError(f"loaded {len(rows)} != {subset_n}")

    # Warm JIT (aut_min + greedy) — not a baseline re-run.
    aut_min((rows[0][1], rows[0][2]))
    greedy_search(rows[0][1], rows[0][2], 50, max_relator_length=ORIG_CAP)

    results = []
    t_all = time.perf_counter()
    for i, (pres_id, r1, r2) in enumerate(rows):
        pid = str(pres_id)
        ctrl = control[pid]
        if (ctrl["r1"], ctrl["r2"]) != (r1, r2):
            raise AssertionError(f"{pid}: control strings != subset")

        climb = climb_nonsym(
            r1, r2, max_expand=max_expand, cap=ORIG_CAP, stop_mu=12)
        br1, br2 = climb["best_rep"][0], climb["best_rep"][1]
        treat_cap = search_cap(br1, br2)
        n_ac = int(climb["cost"]["n_aut_canon"])

        # Full 1000 from best_rep (α=0 end of the sweep).
        treat = _run_greedy(br1, br2, total_nodes, treat_cap)

        # Cap-matched controls at treat_cap (advisor must-address #2).
        cap_orig = cap_aut = None
        if do_cap_controls:
            cap_orig = _run_greedy(r1, r2, total_nodes, treat_cap)
            mu_a, rep_a = aut_min((r1, r2))
            cap_aut = _run_greedy(rep_a[0], rep_a[1], total_nodes, treat_cap)
            cap_aut["mu"] = int(mu_a)
            cap_aut["rep"] = list(rep_a)

        alpha_rows = {}
        for a in alphas:
            ok, b_rem, spent = solved_at_alpha(
                treat["solved"], treat["nodes_explored"], n_ac, a,
                total_nodes=total_nodes)
            alpha_rows[str(a)] = {
                "solved": ok, "B_rem": b_rem, "spent_eq": spent}

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
            "best_chain_hops": climb["best_chain_hops"],
            "n_orbits_seen": climb["n_orbits_seen"],
            "stopped_reason": climb["stopped_reason"],
            "n_aut_canon": n_ac,
            "n_expanded": climb["cost"]["n_expanded"],
            "n_subs1_skipped": climb["cost"]["n_subs1_skipped"],
            "treat_cap": treat_cap,
            "full1k_solved": treat["solved"],
            "full1k_nodes": treat["nodes_explored"],
            "full1k_path": treat["path_length"],
            "full1k_min_relator_length": treat["min_relator_length"],
            # α-sweep (deterministic rescore of full1k)
            "alpha_sweep": alpha_rows,
            # shipped controls (not re-run)
            "b1k_greedy_solved": ctrl["b1k_greedy_solved"],
            "b1k_greedy_nodes": ctrl["b1k_greedy_nodes"],
            "b1k_heur_solved": ctrl["b1k_heur_solved"],
            "b1k_heur_nodes": ctrl["b1k_heur_nodes"],
            "b1k_covgreedy_solved": ctrl["b1k_covgreedy_solved"],
            "b1k_covgreedy_nodes": ctrl["b1k_covgreedy_nodes"],
            "control_source": CONTROL_CSV,
            # cap-matched local controls
            "cap_orig_solved": (cap_orig["solved"] if cap_orig else None),
            "cap_orig_nodes": (cap_orig["nodes_explored"] if cap_orig else None),
            "cap_autmin_solved": (cap_aut["solved"] if cap_aut else None),
            "cap_autmin_nodes": (cap_aut["nodes_explored"] if cap_aut else None),
        }
        results.append(row)
        print(
            f"  [{i+1:02d}/{subset_n}] ms{pid}: μ {climb['mu_in']}→{climb['best_mu']} "
            f"n_ac={n_ac} full1k={treat['solved']}/{treat['nodes_explored']} "
            f"cap={treat_cap} ctrl_g={ctrl['b1k_greedy_solved']} "
            f"ctrl_h={ctrl['b1k_heur_solved']}",
            flush=True)

    out_jsonl = os.path.join(OUT_DIR, f"{STEM}.jsonl")
    out_csv = os.path.join(OUT_DIR, f"{STEM}.csv")
    out_md = os.path.join(OUT_DIR, f"{STEM}.md")
    out_eq_md = os.path.join(OUT_DIR, f"{STEM_EQ}.md")
    out_eq_csv = os.path.join(OUT_DIR, f"{STEM_EQ}.csv")

    with open(out_jsonl, "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")

    # Flat CSV (drop heavy hop list)
    flat_fields = [k for k in results[0] if k != "best_chain_hops"]
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=flat_fields)
        w.writeheader()
        for r in results:
            flat = {k: r[k] for k in flat_fields}
            for k in ("best_rep", "best_chain", "best_nsubs", "alpha_sweep"):
                flat[k] = json.dumps(r[k])
            w.writerow(flat)

    # α-sweep table (cost-matched companion)
    with open(out_eq_csv, "w", newline="") as f:
        fields = ["pres_id", "n_aut_canon", "full1k_nodes", "full1k_solved",
                  "b1k_greedy_solved", "b1k_heur_solved"] + [
            f"alpha_{a}_solved" for a in alphas]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in results:
            row = {
                "pres_id": r["pres_id"],
                "n_aut_canon": r["n_aut_canon"],
                "full1k_nodes": r["full1k_nodes"],
                "full1k_solved": r["full1k_solved"],
                "b1k_greedy_solved": r["b1k_greedy_solved"],
                "b1k_heur_solved": r["b1k_heur_solved"],
            }
            for a in alphas:
                row[f"alpha_{a}_solved"] = r["alpha_sweep"][str(a)]["solved"]
            w.writerow(row)

    _write_reports(results, alphas, out_md, out_eq_md, time.perf_counter() - t_all)
    return out_jsonl, out_csv, out_md


def _write_reports(results, alphas, out_md, out_eq_md, wall_s):
    n = len(results)
    n_g = sum(1 for r in results if r["b1k_greedy_solved"])
    n_h = sum(1 for r in results if r["b1k_heur_solved"])
    n_cg = sum(1 for r in results if r["b1k_covgreedy_solved"])
    n_full = sum(1 for r in results if r["full1k_solved"])
    n_desc = sum(1 for r in results if r["descended"])
    n_cap_gt = sum(1 for r in results if int(r["treat_cap"]) > ORIG_CAP)

    new_vs_g = [r["pres_id"] for r in results
                if r["full1k_solved"] and not r["b1k_greedy_solved"]]
    lost_vs_g = [r["pres_id"] for r in results
                 if r["b1k_greedy_solved"] and not r["full1k_solved"]]
    new_cap_clean = [
        r["pres_id"] for r in results
        if r["pres_id"] in new_vs_g and int(r["treat_cap"]) == ORIG_CAP]

    # Cap-matched local controls
    n_cap_orig = sum(1 for r in results if r.get("cap_orig_solved"))
    n_cap_aut = sum(1 for r in results if r.get("cap_autmin_solved"))

    lines = [
        "# Bench60 non-automorphic CoV best-first (advisor-REVISE claims)",
        "",
        "Control arms loaded from "
        f"`{CONTROL_CSV}` — **not re-run**.",
        "",
        "## Shipped baselines @1000 / cap 24",
        "",
        f"- `b1k_greedy` (length): **{n_g}/{n}**",
        f"- `b1k_heur` (tuned ordering): **{n_h}/{n}**",
        f"- `b1k_covgreedy` (oracle CoV + length): **{n_cg}/{n}**",
        "",
        "## Full greedy@1000 from μ-selected Aut-min best_rep "
        "(CoV compute EXTRA / α=0)",
        "",
        f"- solves: **{n_full}/{n}**",
        f"- μ-descenders: **{n_desc}/{n}**",
        f"- rows with treat_cap > 24: **{n_cap_gt}/{n}** (cap confound vs shipped)",
        f"- new vs `b1k_greedy`: {new_vs_g or '—'} "
        f"({len(new_vs_g)}; cap-clean among them: {new_cap_clean or '—'})",
        f"- lost vs `b1k_greedy`: {lost_vs_g or '—'}",
        "",
        "**Honest framing (ac-advisor):** compare against `b1k_heur` and "
        "`b1k_covgreedy` in the same CSV, not only plain greedy; state cap "
        "confound (`treat_cap>24`) and Aut-min-only control. Do **not** "
        "headline raw “+N over greedy” alone — `b1k_heur` is the free "
        "ordering baseline at cap 24.",
        "",
        f"This run: full1k-from-best_rep **{n_full}/{n}** vs greedy {n_g}, "
        f"heur {n_h}, oracle-CoV {n_cg}; Aut-min-only @treat_cap {n_cap_aut}/{n}; "
        f"original @treat_cap {n_cap_orig}/{n}.",
        "",
        "## Cap-matched local controls @1000 (same treat_cap)",
        "",
        f"- original @ treat_cap: **{n_cap_orig}/{n}**",
        f"- Aut-min(original) @ treat_cap (Thm-3 relabel, no CoV): "
        f"**{n_cap_aut}/{n}**",
        "",
        "Attribute gains to CoV only when full1k beats **both** of these at "
        "the same cap.",
        "",
        f"Wall {wall_s:.1f}s. Artifacts beside this file.",
        "",
        "Unsolved ≠ counterexample. A solve from best_rep certifies the "
        "source **stably** AC-trivial (Prop A + Thm 3 + AC path), never "
        "AC-trivial unqualified. μ-descent is structural, not a solve predictor.",
    ]
    with open(out_md, "w") as f:
        f.write("\n".join(lines) + "\n")

    # Cost-matched α-sweep report (primary under-powered-by-construction claim)
    eq_lines = [
        "# Cost-matched α-sweep (charge α nodes per aut_canon call)",
        "",
        "Derived from one greedy@1000-from-best_rep run per row "
        "(zero extra search). Replaces unreproducible wall-clock `node_eq_ms`.",
        "",
        "| α | solves/60 | B_rem=0 rows |",
        "|---:|---:|---:|",
    ]
    for a in alphas:
        n_sol = sum(1 for r in results if r["alpha_sweep"][str(a)]["solved"])
        n_zero = sum(
            1 for r in results if r["alpha_sweep"][str(a)]["B_rem"] == 0)
        eq_lines.append(f"| {a} | **{n_sol}**/60 | {n_zero} |")
    eq_lines += [
        "",
        f"Shipped `b1k_greedy` = {n_g}/60; `b1k_heur` = {n_h}/60 "
        "(neither charges CoV).",
        "",
        "At large α the beam leaves no search budget — that is a statement "
        "about **this cost model**, not “the transform hurts”.",
    ]
    with open(out_eq_md, "w") as f:
        f.write("\n".join(eq_lines) + "\n")
    print("\n".join(lines))
    print()
    print("\n".join(eq_lines))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--subset", type=int, default=60)
    ap.add_argument("--max-expand", type=int, default=64)
    ap.add_argument("--no-cap-controls", action="store_true")
    args = ap.parse_args()
    run(subset_n=args.subset, max_expand=args.max_expand,
        do_cap_controls=not args.no_cap_controls)


if __name__ == "__main__":
    main()
