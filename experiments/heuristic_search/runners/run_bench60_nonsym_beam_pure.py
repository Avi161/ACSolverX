"""Pure nonsym CoV beam on bench60 — NO greedy, NO Aut-min call cap.

User algorithm only:
  1. start from presentation (Aut-min)
  2. all non-automorphic CoVs
  3. Whitehead Aut-min each child
  4. keep top-K
  5. loop 2–4 until μ≤12 / closed / rung cap

``hits_stop`` (best_mu ≤ 12) is the only success metric — a stable-AC
triviality *lead* (MU_CRITERION), never an AC solve. No greedy pivot, so
this is not comparable to ``b1k_greedy`` / ``b1k_covgreedy`` node counts.

    PYTHONPATH=. python3 -m experiments.heuristic_search.runners.run_bench60_nonsym_beam_pure
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

from experiments.heuristic_search.runners.run_sweep import (  # noqa: E402
    load, subset_ids,
)
from experiments.stable_ac.cov.ladder.autcanon_fast import warm  # noqa: E402
from experiments.stable_ac.cov.ladder.mu_ladder_nonsym_beam import (  # noqa: E402
    climb_beam,
)

ROOT = _d
OUT_DIR = os.path.join(ROOT, "results", "comparison")
DEFAULT_KS = (1, 2, 4, 8, 10, 16)
DEFAULT_RUNGS = 256  # structural backstop only; not an Aut-min call cap
STEM = "covbeam_nonsym_beam_pure_uncapped_subset60"


def run(ks=DEFAULT_KS, rungs=DEFAULT_RUNGS, stop_mu=12, subset_n=60, cap=24):
    os.makedirs(OUT_DIR, exist_ok=True)
    warm()
    rows = load(subset_ids(subset_n))
    detail = []
    summaries = []
    t_all = time.perf_counter()

    for K in ks:
        print(f"\n=== pure beam_k={K} (no greedy, no max_aut_canon) ===", flush=True)
        k_rows = []
        t_k = time.perf_counter()
        for i, (pres_id, r1, r2) in enumerate(rows):
            pid = str(pres_id)
            climb = climb_beam(
                r1, r2, beam_k=K, rungs=rungs, cap=cap, stop_mu=stop_mu,
                max_aut_canon=None)  # uncapped Aut-min work
            row = {
                "pres_id": pid,
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
                "rungs_cap": rungs,
                "stop_mu": stop_mu,
            }
            k_rows.append(row)
            detail.append(row)
            print(
                f"  [{i+1:02d}/{subset_n}] k={K} ms{pid}: "
                f"μ {climb['mu_in']}→{climb['best_mu']} "
                f"hit={climb['hits_stop']} reason={climb['stopped_reason']} "
                f"n_ac={climb['cost']['n_aut_canon']} "
                f"rungs={climb['cost']['n_rungs']}",
                flush=True)
        n_hit = sum(1 for r in k_rows if r["hits_stop"])
        n_desc = sum(1 for r in k_rows if r["descended"])
        n_closed = sum(1 for r in k_rows if r["stopped_reason"] == "closed")
        n_rungcap = sum(
            1 for r in k_rows if r["stopped_reason"] == "rungs_exhausted")
        mean_ac = sum(r["n_aut_canon"] for r in k_rows) / len(k_rows)
        max_ac = max(r["n_aut_canon"] for r in k_rows)
        summaries.append({
            "beam_k": K,
            "n": subset_n,
            "hits_stop": n_hit,
            "descended": n_desc,
            "closed_no_hit": n_closed,
            "rungs_exhausted_no_hit": n_rungcap,
            "mean_n_aut_canon": round(mean_ac, 1),
            "max_n_aut_canon": max_ac,
            "wall_s": round(time.perf_counter() - t_k, 1),
        })
        print(
            f"  k={K}: hits_stop={n_hit}/{subset_n} "
            f"closed={n_closed} rungcap={n_rungcap} "
            f"mean_ac={mean_ac:.0f} max_ac={max_ac} "
            f"wall={summaries[-1]['wall_s']}s",
            flush=True)

    ranked = sorted(
        summaries,
        key=lambda s: (-s["hits_stop"], s["mean_n_aut_canon"], s["beam_k"]))
    best = ranked[0]

    out_jsonl = os.path.join(OUT_DIR, f"{STEM}.jsonl")
    out_csv = os.path.join(OUT_DIR, f"{STEM}.csv")
    out_sum = os.path.join(OUT_DIR, f"{STEM}_summary.csv")
    out_md = os.path.join(OUT_DIR, f"{STEM}.md")

    with open(out_jsonl, "w") as f:
        for r in detail:
            f.write(json.dumps(r) + "\n")

    fields = list(detail[0].keys())
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in detail:
            flat = dict(r)
            flat["best_rep"] = json.dumps(r["best_rep"])
            flat["best_chain"] = json.dumps(r["best_chain"])
            w.writerow(flat)

    with open(out_sum, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(summaries[0].keys()))
        w.writeheader()
        for s in sorted(summaries, key=lambda x: x["beam_k"]):
            w.writerow(s)

    wall = time.perf_counter() - t_all
    lines = [
        "# Pure nonsym CoV beam (no greedy, uncapped Aut-min) — bench60",
        "",
        "Bias fix: the prior K-sweep charged up to 1000 Whitehead/`aut_min` "
        "calls **then** gave greedy another 1000 nodes — that is not a fair "
        "comparison to plain greedy@1k. This run drops greedy entirely.",
        "",
        "Algorithm: non-automorphic CoV → Aut-min → keep top-K → loop until "
        f"μ≤{stop_mu} / closed / rungs={rungs} (structural backstop only; "
        "**no** `max_aut_canon`).",
        "",
        "## Success metric",
        "",
        f"**`hits_stop`** = `best_mu ≤ {stop_mu}`. That is a *stable*-AC "
        "triviality lead (MU_CRITERION / MM03), **not** an AC solve and not "
        "comparable to `b1k_covgreedy` node budgets.",
        "",
        "## K sweep (uncapped)",
        "",
        "| K | hits_stop (μ≤12) | descended | closed (no hit) | "
        "rung-cap (no hit) | mean n_aut_canon | max n_aut_canon | wall_s |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for s in sorted(summaries, key=lambda x: x["beam_k"]):
        mark = " ← best" if s["beam_k"] == best["beam_k"] else ""
        lines.append(
            f"| {s['beam_k']} | **{s['hits_stop']}**/60 | {s['descended']}/60 | "
            f"{s['closed_no_hit']} | {s['rungs_exhausted_no_hit']} | "
            f"{s['mean_n_aut_canon']} | {s['max_n_aut_canon']} | "
            f"{s['wall_s']}{mark} |")
    lines += [
        "",
        f"**Best K = {best['beam_k']}** by hits_stop "
        f"({best['hits_stop']}/60), tie-break lower mean Aut-min work.",
        "",
        "Rows that stop as `closed` with μ>12 found no further "
        "non-automorphic Aut-min children in the beam — uncapping Aut-min "
        "calls cannot help those. `rungs_exhausted` would mean the "
        f"{rungs}-rung backstop bound; raise it if that count is >0.",
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
    ap.add_argument("--rungs", type=int, default=DEFAULT_RUNGS)
    ap.add_argument("--stop-mu", type=int, default=12)
    args = ap.parse_args()
    ks = tuple(int(x) for x in args.ks.split(",") if x.strip())
    run(ks=ks, rungs=args.rungs, stop_mu=args.stop_mu)


if __name__ == "__main__":
    main()
