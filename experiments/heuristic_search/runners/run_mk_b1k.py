"""L + w·MK (max knots) weight sweep at budget 1,000 on subset-60.

``MK = max(knots(r1), knots(r2))``. Mean MK on this set is ~2.6; the shipped
RECOMMENDED coefficient is 6.418. The grid brackets that value and extends
upward the way the raw-``K`` one-feature sweep did (peak there was above the
RECOMMENDED ``K`` coeff).

No K, S, or xyimb. Cap 24. Compared to shipped length-only and RECOMMENDED.

    python3 -m experiments.heuristic_search.runners.run_mk_b1k
"""
from __future__ import annotations

import csv
import json
import os
import statistics
import sys
import time


def _repo_root(start=None):
    d = os.path.abspath(start or os.path.dirname(os.path.abspath(__file__)))
    while d != os.path.dirname(d):
        if (os.path.isdir(os.path.join(d, "experiments"))
                and os.path.isdir(os.path.join(d, "data"))):
            return d
        d = os.path.dirname(d)
    raise RuntimeError("repo root (experiments/ + data/) not found")


ROOT = _repo_root()
sys.path.insert(0, ROOT)

from experiments.heuristic_search.core.hlab import word_stats  # noqa: E402
from experiments.heuristic_search.core.hsearch import hsearch  # noqa: E402

SOURCE = os.path.join(ROOT, "results/comparison/cov_heur_b1k_subset60.csv")
OUT_CSV = os.path.join(ROOT, "results/comparison/mk_b1k_subset60.csv")
OUT_MD = os.path.join(ROOT, "results/comparison/MK_B1K.md")

BUDGET = 1_000
CAP = 24

# MK ≈ 2.6 here; RECOMMENDED uses 6.418. Bracket it and probe higher
# (raw-K alone peaked above its RECOMMENDED coeff).
WEIGHTS = (2.0, 4.0, 6.418, 8.0, 10.0, 12.0, 16.0, 24.0)


def _mk(r1, r2):
    n1, x1, y1, *_ = word_stats(r1)
    n2, x2, y2, *_ = word_stats(r2)
    k1 = 0 if (x1 == 0 or y1 == 0) else max(x1, y1)
    k2 = 0 if (x2 == 0 or y2 == 0) else max(x2, y2)
    L = float(n1 + n2)
    return L, float(max(k1, k2))


def make_priority(w):
    def priority(r1, r2):
        L, mk = _mk(r1, r2)
        return L + w * mk
    priority.__name__ = f"L+{w:g}*MK"
    return priority


def _tag(w):
    return f"mk_w{f'{w:g}'.replace('.', '_')}"


def _is_true(v):
    return v if isinstance(v, bool) else str(v).lower() == "true"


def run():
    with open(SOURCE) as f:
        src = list(csv.DictReader(f))
    if len(src) != 60:
        raise RuntimeError(f"expected 60, got {len(src)}")

    hsearch("X", "Y", 20, priority=make_priority(6.418), max_relator_length=CAP)

    fieldnames = [
        "pres_id", "bin", "r1", "r2",
        "b1k_greedy_solved", "b1k_greedy_nodes", "b1k_greedy_path",
        "b1k_heur_solved", "b1k_heur_nodes", "b1k_heur_path",
    ]
    for w in WEIGHTS:
        tag = _tag(w)
        fieldnames.extend([f"{tag}_solved", f"{tag}_nodes", f"{tag}_path"])

    rows = []
    t0 = time.time()
    for i, s in enumerate(src):
        row = {
            "pres_id": s["pres_id"],
            "bin": s["bin"],
            "r1": s["r1"],
            "r2": s["r2"],
            "b1k_greedy_solved": s["b1k_greedy_solved"],
            "b1k_greedy_nodes": s["b1k_greedy_nodes"],
            "b1k_greedy_path": s["b1k_greedy_path"],
            "b1k_heur_solved": s["b1k_heur_solved"],
            "b1k_heur_nodes": s["b1k_heur_nodes"],
            "b1k_heur_path": s["b1k_heur_path"],
        }
        for w in WEIGHTS:
            tag = _tag(w)
            res = hsearch(
                s["r1"], s["r2"], BUDGET,
                priority=make_priority(w), max_relator_length=CAP)
            row[f"{tag}_solved"] = bool(res["solved"])
            row[f"{tag}_nodes"] = int(res["nodes_explored"])
            row[f"{tag}_path"] = (
                int(res["path_length"]) if res["solved"] else "")
            if int(res["nodes_explored"]) > BUDGET:
                raise RuntimeError(
                    f"budget exceeded on ms{s['pres_id']} w={w}")
        rows.append(row)
        if (i + 1) % 10 == 0 or i + 1 == len(src):
            print(f"  [{i+1}/60] {time.time()-t0:.0f}s", flush=True)

    drift = []
    p0 = make_priority(0.0)
    for s in src[:5]:
        res = hsearch(s["r1"], s["r2"], BUDGET, priority=p0,
                      max_relator_length=CAP)
        want_sol = _is_true(s["b1k_greedy_solved"])
        want_n = int(s["b1k_greedy_nodes"])
        if (bool(res["solved"]), int(res["nodes_explored"])) != (want_sol, want_n):
            drift.append((s["pres_id"], want_n, want_sol,
                          res["nodes_explored"], res["solved"]))
    if drift:
        raise SystemExit(f"w=0 control gate failed: {drift}")
    print("w=0 length-only control PASSED on first 5 rows", flush=True)

    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with open(OUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            out = dict(r)
            for w in WEIGHTS:
                tag = _tag(w)
                out[f"{tag}_solved"] = (
                    "true" if r[f"{tag}_solved"] else "false")
            writer.writerow(out)
    print(f"wrote {OUT_CSV}")

    def arm_stats(solved_key, nodes_key, path_key):
        sol = [r for r in rows if _is_true(r[solved_key])]
        if not sol:
            return 0, None, None, None, None
        nodes = [int(r[nodes_key]) for r in sol]
        paths = [int(r[path_key]) for r in sol if str(r[path_key]) != ""]
        return (len(sol),
                statistics.fmean(nodes), statistics.median(nodes),
                statistics.fmean(paths) if paths else None,
                statistics.median(paths) if paths else None)

    def fmt_row(label, n, mn, mdn, mp, mdp):
        if n == 0:
            return f"| {label} | **0/60** | — | — | — | — |"
        return (
            f"| {label} | **{n}/60** | {mn:.1f} | {mdn:.0f} | "
            f"{mp:.1f} | {mdp:.0f} |")

    greedy = {r["pres_id"] for r in rows if _is_true(r["b1k_greedy_solved"])}
    heur = {r["pres_id"] for r in rows if _is_true(r["b1k_heur_solved"])}

    summary = {}
    lines = [
        "# L + w·MK at budget 1,000 (subset-60)",
        "",
        "Priority `L + w * max(knots(r1), knots(r2))`. Cap 24. No K / S / "
        "xyimb. Compared to shipped `b1k_greedy` (length-only) and "
        "`b1k_heur` (full RECOMMENDED).",
        "",
        "Mean MK on these starts is ~2.6; RECOMMENDED's MK coefficient is "
        "6.418. Grid: `{2, 4, 6.418, 8, 10, 12, 16, 24}`.",
        "",
        "Mean/median nodes and path are over **solved** rows only.",
        "",
        "| arm | solved | mean nodes | med nodes | mean path | med path |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for label, sk, nk, pk in (
        ("b1k_greedy (L only)", "b1k_greedy_solved", "b1k_greedy_nodes",
         "b1k_greedy_path"),
        ("b1k_heur (RECOMMENDED)", "b1k_heur_solved", "b1k_heur_nodes",
         "b1k_heur_path"),
    ):
        n, mn, mdn, mp, mdp = arm_stats(sk, nk, pk)
        summary[label] = n
        lines.append(fmt_row(label, n, mn, mdn, mp, mdp))

    for w in WEIGHTS:
        tag = _tag(w)
        n, mn, mdn, mp, mdp = arm_stats(
            f"{tag}_solved", f"{tag}_nodes", f"{tag}_path")
        summary[tag] = n
        lines.append(fmt_row(f"`L + {w:g}·MK`", n, mn, mdn, mp, mdp))

    best_w = max(WEIGHTS, key=lambda w: summary[_tag(w)])
    best_n = summary[_tag(best_w)]

    lines.extend([
        "",
        "## Verdict",
        "",
        f"- Best weight: `L + {best_w:g}·MK` → **{best_n}/60**",
        f"- vs length-only 29/60 and full RECOMMENDED 43/60.",
        f"- Nearby one-feature peaks for context: `L+8·K` = 37/60, "
        f"`L+10·K_den` = 32/60.",
        "",
        "## vs length-only / RECOMMENDED",
        "",
    ])
    for w in WEIGHTS:
        tag = _tag(w)
        got = {r["pres_id"] for r in rows if r[f"{tag}_solved"]}
        lines.append(
            f"- w={w:g}: +{len(got - greedy)} over greedy, "
            f"-{len(greedy - got)} vs greedy; "
            f"vs RECOMMENDED +{len(got - heur)} / -{len(heur - got)}")

    lines.extend([
        "",
        "## Source",
        "",
        f"- Input: [`cov_heur_b1k_subset60.csv`](cov_heur_b1k_subset60.csv)",
        f"- Table: [`mk_b1k_subset60.csv`](mk_b1k_subset60.csv)",
        "- Runner: `experiments/heuristic_search/runners/run_mk_b1k.py`",
        "",
    ])
    with open(OUT_MD, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"wrote {OUT_MD}")
    print(json.dumps(summary, indent=2))
    print(f"VERDICT: L + {best_w:g}·MK → {best_n}/60")
    return rows


def main():
    run()


if __name__ == "__main__":
    main()
