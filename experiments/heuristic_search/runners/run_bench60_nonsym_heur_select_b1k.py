"""Nonsym CoVs ranked by RECOMMENDED start priority → greedy @1k (bench60).

Fairer than the μ-beam+greedy pivot: **one hop** of non-automorphic CoVs
only (``n_subs>1`` + orbit moved), Aut-min each child (Whitehead), score
with the static RECOMMENDED min-heap priority

    prio = L + 2.53·K + 6.418·MK + 8.458·S + 3.292·xyimb

pick ``argmin`` prio, then run length-greedy **and** RECOMMENDED search at
budget 1000 from that Aut-min start.

Arms written per row:
  * ``nonsym_heur`` — this selector + length-greedy @1k
  * ``nonsym_heur_h`` — same start + RECOMMENDED search @1k
  * ``nonsym_mumin`` — control: pick lowest-μ nonsym Aut-min child + length @1k
  * shipped ``b1k_*`` loaded, not re-run

    PYTHONPATH=. python3 -m experiments.heuristic_search.runners.run_bench60_nonsym_heur_select_b1k
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

from experiments.heuristic_search.core.hlab import FEATURES, phi  # noqa: E402
from experiments.heuristic_search.core.hsolve import (  # noqa: E402
    RECOMMENDED, greedy_search_h,
)
from experiments.heuristic_search.runners.run_bench60_covbeam_b1k import (  # noqa: E402
    CONTROL_CSV, ORIG_CAP, load_control, search_cap, _run_greedy,
)
from experiments.heuristic_search.runners.run_sweep import (  # noqa: E402
    load, subset_ids,
)
from experiments.stable_ac.cov.ladder.autcanon_fast import warm  # noqa: E402
from experiments.stable_ac.cov.ladder.mu_ladder_nonsym import (  # noqa: E402
    hop_nonsym, orbit_fast,
)

ROOT = _d
OUT_DIR = os.path.join(ROOT, "results", "comparison")
BUDGET = 1000
LOCAL_CAP = 1000
DIMS = ("L", "K", "MK", "S", "xyimb")
WEIGHTS = RECOMMENDED["segments"][0]["w"]
STEM = "nonsym_heur_select_b1k_subset60"


def recommended_prio(r1, r2):
    v = phi(r1, r2)
    idx = {f: i for i, f in enumerate(FEATURES)}
    return sum(WEIGHTS[d] * float(v[idx[d]]) for d in DIMS)


def select_nonsym(r1, r2, cap=ORIG_CAP):
    """One-hop nonsym children from Aut-min(parent); return heur-best and μ-best."""
    mu0, rep0 = orbit_fast((r1, r2))
    hops = hop_nonsym(rep0[0], rep0[1], cap)
    if not hops:
        p0 = recommended_prio(rep0[0], rep0[1])
        base = {
            "parent_mu": mu0,
            "parent_rep": list(rep0),
            "n_nonsym": 0,
            "fallback": "autmin_original",
            "z": None, "iso_gen": None, "iso_index": None, "n_subs": None,
            "mu": mu0, "rep": list(rep0), "prio": p0,
            "concrete_pair": list(rep0),
        }
        return base, dict(base)

    heur_best = None
    mu_best = None
    for h in hops:
        rep = (h["rep"][0], h["rep"][1])
        p = recommended_prio(rep[0], rep[1])
        cand = {
            "parent_mu": mu0,
            "parent_rep": list(rep0),
            "n_nonsym": len(hops),
            "fallback": None,
            "z": h["z"],
            "iso_gen": h["iso_gen"],
            "iso_index": h["iso_index"],
            "n_subs": h["n_subs"],
            "mu": h["mu"],
            "rep": list(rep),
            "prio": p,
            "concrete_pair": list(h["concrete_pair"]),
        }
        if heur_best is None or (p, h["mu"], rep) < (
                heur_best["prio"], heur_best["mu"], tuple(heur_best["rep"])):
            heur_best = cand
        if mu_best is None or (h["mu"], p, rep) < (
                mu_best["mu"], mu_best["prio"], tuple(mu_best["rep"])):
            mu_best = {
                "parent_mu": mu0,
                "parent_rep": list(rep0),
                "n_nonsym": len(hops),
                "fallback": None,
                "z": h["z"],
                "iso_gen": h["iso_gen"],
                "iso_index": h["iso_index"],
                "n_subs": h["n_subs"],
                "mu": h["mu"],
                "rep": list(rep),
                "prio": p,
                "concrete_pair": list(h["concrete_pair"]),
            }
    return heur_best, mu_best


def _run_heur(r1, r2, budget, cap):
    g = greedy_search_h(r1, r2, budget, max_relator_length=cap,
                        config=RECOMMENDED)
    return {
        "solved": bool(g["solved"]),
        "nodes_explored": int(g["nodes_explored"]),
        "path_length": g.get("path_length"),
        "min_relator_length": g.get("min_relator_length"),
    }


def run(subset_n=60, budget=BUDGET):
    if budget > LOCAL_CAP:
        raise SystemExit(f"budget={budget} > local cap {LOCAL_CAP}")
    os.makedirs(OUT_DIR, exist_ok=True)
    warm()
    control = load_control()
    rows = load(subset_ids(subset_n))
    # JIT
    _run_greedy(rows[0][1], rows[0][2], 50, ORIG_CAP)
    greedy_search_h(rows[0][1], rows[0][2], 50, max_relator_length=ORIG_CAP,
                    config=RECOMMENDED)

    results = []
    t0 = time.perf_counter()
    for i, (pres_id, r1, r2) in enumerate(rows):
        pid = str(pres_id)
        ctrl = control[pid]
        heur_sel, mu_sel = select_nonsym(r1, r2)

        # heur-selected start
        hr1, hr2 = heur_sel["rep"][0], heur_sel["rep"][1]
        hcap = search_cap(hr1, hr2)
        g_len = _run_greedy(hr1, hr2, budget, hcap)
        g_heur = _run_heur(hr1, hr2, budget, hcap)

        # μ-min nonsym control start
        mr1, mr2 = mu_sel["rep"][0], mu_sel["rep"][1]
        mcap = search_cap(mr1, mr2)
        g_mu = _run_greedy(mr1, mr2, budget, mcap)

        row = {
            "pres_id": pid,
            "bin": ctrl["bin"],
            "r1": r1, "r2": r2,
            "n_nonsym": heur_sel["n_nonsym"],
            "fallback": heur_sel["fallback"],
            # heur selector
            "hsel_z": heur_sel["z"],
            "hsel_n_subs": heur_sel["n_subs"],
            "hsel_mu": heur_sel["mu"],
            "hsel_prio": heur_sel["prio"],
            "hsel_rep": heur_sel["rep"],
            "hsel_cap": hcap,
            "nonsym_heur_solved": g_len["solved"],
            "nonsym_heur_nodes": g_len["nodes_explored"],
            "nonsym_heur_path": g_len["path_length"],
            "nonsym_heur_h_solved": g_heur["solved"],
            "nonsym_heur_h_nodes": g_heur["nodes_explored"],
            "nonsym_heur_h_path": g_heur["path_length"],
            # μ-min control
            "msel_z": mu_sel["z"],
            "msel_mu": mu_sel["mu"],
            "msel_prio": mu_sel["prio"],
            "msel_rep": mu_sel["rep"],
            "same_as_mumin": heur_sel["rep"] == mu_sel["rep"],
            "nonsym_mumin_solved": g_mu["solved"],
            "nonsym_mumin_nodes": g_mu["nodes_explored"],
            "nonsym_mumin_path": g_mu["path_length"],
            # shipped
            "b1k_greedy_solved": ctrl["b1k_greedy_solved"],
            "b1k_heur_solved": ctrl["b1k_heur_solved"],
            "b1k_covgreedy_solved": ctrl["b1k_covgreedy_solved"],
        }
        results.append(row)
        print(
            f"  [{i+1:02d}/{subset_n}] ms{pid}: n_nonsym={heur_sel['n_nonsym']} "
            f"hsel μ={heur_sel['mu']} prio={heur_sel['prio']:.1f} "
            f"g={g_len['solved']}/{g_len['nodes_explored']} "
            f"h={g_heur['solved']}/{g_heur['nodes_explored']} "
            f"mumin_g={g_mu['solved']}/{g_mu['nodes_explored']} "
            f"same_mu={row['same_as_mumin']}",
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
            flat["hsel_rep"] = json.dumps(r["hsel_rep"])
            flat["msel_rep"] = json.dumps(r["msel_rep"])
            w.writerow(flat)

    n = len(results)
    def cnt(k):
        return sum(1 for r in results if r[k])

    n_nh = cnt("nonsym_heur_solved")
    n_nhh = cnt("nonsym_heur_h_solved")
    n_mu = cnt("nonsym_mumin_solved")
    n_g = cnt("b1k_greedy_solved")
    n_h = cnt("b1k_heur_solved")
    n_cg = cnt("b1k_covgreedy_solved")
    n_same = cnt("same_as_mumin")
    n_fb = sum(1 for r in results if r["fallback"])

    new_vs_g = [r["pres_id"] for r in results
                if r["nonsym_heur_solved"] and not r["b1k_greedy_solved"]]
    lost_vs_g = [r["pres_id"] for r in results
                 if r["b1k_greedy_solved"] and not r["nonsym_heur_solved"]]
    new_vs_cg = [r["pres_id"] for r in results
                 if r["nonsym_heur_solved"] and not r["b1k_covgreedy_solved"]]
    beat_mumin = [r["pres_id"] for r in results
                  if r["nonsym_heur_solved"] and not r["nonsym_mumin_solved"]]
    lose_mumin = [r["pres_id"] for r in results
                  if r["nonsym_mumin_solved"] and not r["nonsym_heur_solved"]]

    wall = time.perf_counter() - t0
    lines = [
        "# Nonsym CoV × RECOMMENDED priority → greedy @1k (bench60)",
        "",
        "One hop only (fair cost): Aut-min parent → all non-automorphic CoVs "
        "(`n_subs>1` + orbit moved) → Aut-min each child → pick min "
        "RECOMMENDED start priority → length-greedy / RECOMMENDED @1000.",
        "",
        f"Shipped controls from `{CONTROL_CSV}` (not re-run).",
        "",
        "## Solve rates @ budget 1000",
        "",
        "| arm | start | search | solved |",
        "|---|---|---|---:|",
        f"| `b1k_greedy` (shipped) | original | length | **{n_g}**/60 |",
        f"| `b1k_heur` (shipped) | original | RECOMMENDED | **{n_h}**/60 |",
        f"| `b1k_covgreedy` (shipped oracle) | best-of-all-CoV | length | "
        f"**{n_cg}**/60 |",
        f"| `nonsym_mumin` | lowest-μ nonsym Aut-min | length | "
        f"**{n_mu}**/60 |",
        f"| **`nonsym_heur`** | min RECOMMENDED prio nonsym Aut-min | length | "
        f"**{n_nh}**/60 |",
        f"| **`nonsym_heur_h`** | same start | RECOMMENDED | "
        f"**{n_nhh}**/60 |",
        "",
        f"- Heur selector = μ-min selector on **{n_same}/60** rows "
        f"(fallback to Aut-min original: {n_fb}).",
        f"- `nonsym_heur` vs `b1k_greedy`: new {new_vs_g or '—'}; "
        f"lost {lost_vs_g or '—'}.",
        f"- `nonsym_heur` vs oracle `b1k_covgreedy`: new {new_vs_cg or '—'} "
        f"({len(new_vs_cg)}).",
        f"- `nonsym_heur` vs `nonsym_mumin`: beats μ-pick on {beat_mumin or '—'}; "
        f"loses on {lose_mumin or '—'}.",
        "",
        "Not comparable to the pure uncapped μ-beam's 50/60 μ≤12 leads "
        "(different finish line, multi-hop, no greedy).",
        "",
        f"Wall {wall:.1f}s. Artifacts: `{STEM}.*`.",
    ]
    with open(out_md, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return out_md


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--budget", type=int, default=BUDGET)
    ap.add_argument("--subset", type=int, default=60)
    args = ap.parse_args()
    run(subset_n=args.subset, budget=args.budget)


if __name__ == "__main__":
    main()
