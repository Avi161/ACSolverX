"""Compare nonsym CoV-beam + greedy vs oracle best-CoV at budget 10,000.

Local searches stay ≤ 1,000 (repo hard cap). This script is **analysis-only**:

1. Load climb + greedy@1k from ``covbeam_nonsym_b1kfull_subset60.jsonl``.
2. Rescore: any row with ``full1k_solved`` is solved at every B ≥ nodes (incl. 10k).
3. Join the shipped one-shot CoV sweep @10k
   (``covsweep_10000_66_…jsonl``) by Aut-orbit of ``best_rep`` — a *witness*
   that some string in the same orbit solves ≤10k, **not** a run of our
   Aut-min start (greedy is string-sensitive; see AUTOMORPHISMS_COV.md).
4. Load oracle best-CoV @10k from ``greedy_vs_bestcov_subset60_b10000.csv``.

Headline table is written under ``results/comparison/``.

True greedy@10k from Aut-min ``best_rep`` belongs on Colab:
``experiments/heuristic_search/hsearch_colab_covbeam_nonsym_b10k.ipynb``.

    PYTHONPATH=. python3 -m experiments.heuristic_search.runners.compare_covbeam_vs_bestcov_b10k
"""
from __future__ import annotations

import csv
import json
import os
import sys

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

from experiments.stable_ac.cov.ladder.autcanon_fast import aut_min, warm  # noqa: E402

ROOT = _d
CLIMB_JSONL = os.path.join(
    ROOT, "results", "comparison", "covbeam_nonsym_b1kfull_subset60.jsonl")
BESTCOV_CSV = os.path.join(
    ROOT, "results", "stable_ac", "cov", "greedy_vs_bestcov_subset60_b10000.csv")
SWEEP_JSONL = os.path.join(
    ROOT, "results", "stable_ac", "cov",
    "covsweep_10000_66_subnc2pxysb_mrl24_cyc_s60r6_07_20_26.jsonl")
OUT_DIR = os.path.join(ROOT, "results", "comparison")
STEM = "covbeam_nonsym_vs_bestcov_b10k_subset60"


def _ac_key(x):
    if x is None:
        return None
    if isinstance(x, str):
        if "," in x:
            a, b = x.split(",", 1)
            return (a, b)
        return x
    if isinstance(x, (list, tuple)) and len(x) == 2:
        return (x[0], x[1])
    return tuple(x)


def load_climb(path=CLIMB_JSONL):
    out = {}
    with open(path) as f:
        for line in f:
            r = json.loads(line)
            out[str(r["pres_id"])] = r
    if len(out) != 60:
        raise AssertionError(f"climb jsonl has {len(out)} rows, want 60")
    return out


def load_bestcov(path=BESTCOV_CSV):
    out = {}
    with open(path) as f:
        for r in csv.DictReader(f):
            pid = str(r["pres_id"])
            solved = r["cov_solved"].strip().lower() in ("1", "true", "yes")
            nodes = (int(float(r["cov_nodes"]))
                     if r.get("cov_nodes") not in ("", None) and solved
                     else None)
            out[pid] = {
                "bestcov_b10k_solved": solved,
                "bestcov_b10k_nodes": nodes,
                "bestcov_b10k_z": r.get("best_z") or None,
                "n_cov_tried": int(r["n_cov_tried"]),
                "n_cov_solved": int(r["n_cov_solved"]),
            }
    if len(out) != 60:
        raise AssertionError(f"bestcov csv has {len(out)} rows, want 60")
    return out


def join_sweep_orbit(climb, path=SWEEP_JSONL):
    """Cheapest solved one-shot CoV in the same Aut-orbit as best_rep, else None."""
    from collections import defaultdict
    by_pres = defaultdict(list)
    with open(path) as f:
        for line in f:
            r = json.loads(line)
            pid = str(r["pres_id"])
            if pid in climb:
                by_pres[pid].append(r)

    witnesses = {}
    for pid, row in climb.items():
        br = tuple(row["best_rep"])
        _mu, rep = aut_min(br)
        ac_br = (rep[0], rep[1])
        matches = []
        for r in by_pres[pid]:
            pair = (r["r1"], r["r2"])
            ac_c = _ac_key(r.get("aut_canon_cov"))
            if pair == br or pair == (br[1], br[0]) or pair == ac_br or ac_c == ac_br:
                matches.append(r)
        solved = [r for r in matches if r["solved"]]
        if solved:
            best = min(solved, key=lambda r: (
                r["nodes_explored"], r.get("path_length") or 10**9))
            exact = (best["r1"], best["r2"]) in (br, (br[1], br[0]), ac_br)
            witnesses[pid] = {
                "orbit_witness_solved": True,
                "orbit_witness_nodes": int(best["nodes_explored"]),
                "orbit_witness_path": best.get("path_length"),
                "orbit_witness_cap": int(best["max_relator_length_cap"]),
                "orbit_witness_z": best.get("z_word"),
                "orbit_witness_r1": best["r1"],
                "orbit_witness_r2": best["r2"],
                "orbit_witness_exact_best_rep": exact,
                "orbit_n_matches": len(matches),
                "orbit_n_solved": len(solved),
            }
        else:
            witnesses[pid] = {
                "orbit_witness_solved": False,
                "orbit_witness_nodes": None,
                "orbit_witness_path": None,
                "orbit_witness_cap": None,
                "orbit_witness_z": None,
                "orbit_witness_r1": None,
                "orbit_witness_r2": None,
                "orbit_witness_exact_best_rep": False,
                "orbit_n_matches": len(matches),
                "orbit_n_solved": 0,
            }
    return witnesses


def build_rows(climb, bestcov, witnesses):
    rows = []
    for pid in sorted(climb, key=lambda x: (len(x), x)):
        c = climb[pid]
        b = bestcov[pid]
        w = witnesses[pid]
        proven_1k = bool(c["full1k_solved"])
        # Proven at 10k by truncation: solved within 1k ⇒ solved within 10k.
        proven_b10k = proven_1k
        # Upper-bound style orbit witness (NOT our Aut-min start).
        orbit_lb = proven_b10k or bool(w["orbit_witness_solved"])
        rows.append({
            "pres_id": pid,
            "bin": c.get("bin"),
            "mu_in": c["mu_in"],
            "best_mu": c["best_mu"],
            "descended": c["descended"],
            "chain_len": len(c.get("best_chain") or []),
            "best_rep": c["best_rep"],
            "treat_cap": c["treat_cap"],
            "full1k_solved": proven_1k,
            "full1k_nodes": c["full1k_nodes"],
            "algo_proven_b10k": proven_b10k,
            "algo_orbit_witness_b10k": orbit_lb,
            "orbit_witness_solved": w["orbit_witness_solved"],
            "orbit_witness_nodes": w["orbit_witness_nodes"],
            "orbit_witness_cap": w["orbit_witness_cap"],
            "orbit_witness_exact_best_rep": w["orbit_witness_exact_best_rep"],
            "orbit_witness_z": w["orbit_witness_z"],
            "orbit_witness_r1": w["orbit_witness_r1"],
            "orbit_witness_r2": w["orbit_witness_r2"],
            "bestcov_b10k_solved": b["bestcov_b10k_solved"],
            "bestcov_b10k_nodes": b["bestcov_b10k_nodes"],
            "bestcov_b10k_z": b["bestcov_b10k_z"],
            "n_cov_tried": b["n_cov_tried"],
            "n_cov_solved": b["n_cov_solved"],
        })
    return rows


def write_outputs(rows):
    os.makedirs(OUT_DIR, exist_ok=True)
    out_csv = os.path.join(OUT_DIR, f"{STEM}.csv")
    out_md = os.path.join(OUT_DIR, f"{STEM}.md")
    out_jsonl = os.path.join(OUT_DIR, f"{STEM}.jsonl")

    with open(out_jsonl, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

    fields = list(rows[0].keys())
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            flat = dict(r)
            flat["best_rep"] = json.dumps(r["best_rep"])
            w.writerow(flat)

    n = len(rows)
    n_1k = sum(1 for r in rows if r["full1k_solved"])
    n_proven = sum(1 for r in rows if r["algo_proven_b10k"])
    n_orbit = sum(1 for r in rows if r["algo_orbit_witness_b10k"])
    n_bc = sum(1 for r in rows if r["bestcov_b10k_solved"])
    n_exact = sum(1 for r in rows if r["orbit_witness_exact_best_rep"])

    # Rescore algo@1k nodes at tiny budgets (literal "budget 10" reading).
    def rescore(B):
        return sum(
            1 for r in rows
            if r["full1k_solved"] and int(r["full1k_nodes"]) <= B)

    open_proven = [r["pres_id"] for r in rows if not r["algo_proven_b10k"]]
    open_orbit = [r["pres_id"] for r in rows if not r["algo_orbit_witness_b10k"]]
    orbit_only = [
        r["pres_id"] for r in rows
        if r["algo_orbit_witness_b10k"] and not r["algo_proven_b10k"]]
    bc_only = [
        r["pres_id"] for r in rows
        if r["bestcov_b10k_solved"] and not r["algo_orbit_witness_b10k"]]
    algo_only = [
        r["pres_id"] for r in rows
        if r["algo_orbit_witness_b10k"] and not r["bestcov_b10k_solved"]]

    lines = [
        "# Nonsym CoV-beam vs oracle best-CoV @ budget 10,000 (bench60)",
        "",
        "Local hard cap forbids launching greedy @10k here. Numbers below are "
        "from existing artifacts only (climb+greedy@1k jsonl, one-shot "
        "covsweep@10k, shipped bestcov@10k table).",
        "",
        "## Headlines",
        "",
        "| arm | solves/60 | what it is |",
        "|---|---:|---|",
        f"| nonsym beam → Aut-min `best_rep` → greedy, **proven @10k** "
        f"| **{n_proven}** | truncation of greedy@1k "
        f"(`full1k_solved`; {n_1k}/60 at ≤1k) |",
        f"| same + Aut-orbit **witness** in covsweep@10k | **{n_orbit}** | "
        f"some one-shot CoV in the *same Aut-orbit* as `best_rep` solves "
        f"≤10k — **not** a run from our Aut-min string "
        f"(exact best_rep hits in sweep: {n_exact}/60) |",
        f"| oracle best-CoV @10k (brute every subword CoV, pick cheapest) "
        f"| **{n_bc}** | "
        f"[`greedy_vs_bestcov_subset60_b10000.csv`](../stable_ac/cov/greedy_vs_bestcov_subset60_b10000.csv) |",
        "",
        f"- Orbit-witness-only rows (need Colab greedy@10k from Aut-min to "
        f"confirm): {orbit_only or '—'}",
        f"- Still open even with orbit witness: {open_orbit or '—'}",
        f"- bestcov@10k solves we lack even as orbit witness: {bc_only or '—'}",
        f"- orbit witness solves bestcov@10k misses: {algo_only or '—'}",
        "",
        "## Verdict",
        "",
        f"Oracle best-CoV @10k = **{n_bc}/60**. Our runnable nonsym beam is "
        f"**proven** at **{n_proven}/60** for budget 10k (already done by 1k). "
        f"Joining the one-shot sweep by Aut-orbit lifts the *optimistic* "
        f"count to **{n_orbit}/60** — matching bestcov — but those +3 "
        f"({orbit_only}) are **different string labels** of the same orbit "
        f"(relabel trap) with sweep caps 32–33 vs our `treat_cap` 30. Do "
        f"**not** headline 52 as our algorithm until Colab runs greedy@10k "
        f"from Aut-min `best_rep`.",
        "",
        "The eight aut-class-106 rows (`622–625`, `636–639`) stay open for "
        "both: bestcov needs 20k, and our multi-hop `best_rep` orbit has no "
        "solving one-shot CoV in the 10k sweep.",
        "",
        "## Side note — if “10 budget” meant node_budget=10",
        "",
        f"- nonsym → greedy rescore @10: **{rescore(10)}**/60",
        f"- bestcov rescore @10 (from 10k table, nodes≤10): "
        f"**{sum(1 for r in rows if r['bestcov_b10k_nodes'] is not None and r['bestcov_b10k_nodes'] <= 10)}**/60",
        f"- bestcov @10k remains **{n_bc}/60**",
        "",
        "True Aut-min greedy@10k: "
        "`experiments/heuristic_search/hsearch_colab_covbeam_nonsym_b10k.ipynb`.",
        "",
        f"Open for proven arm: {open_proven}",
    ]
    with open(out_md, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return out_csv, out_md, out_jsonl


def main():
    warm()
    climb = load_climb()
    bestcov = load_bestcov()
    witnesses = join_sweep_orbit(climb)
    rows = build_rows(climb, bestcov, witnesses)
    write_outputs(rows)


if __name__ == "__main__":
    main()
