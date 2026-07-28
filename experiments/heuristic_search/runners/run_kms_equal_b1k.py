"""Equal-proportion mix of K, MK, S at budget 1,000 on subset-60.

Best one-feature peaks were ``L+8·K``, ``L+8·MK``, ``L+24·S``. Those make
unequal mean contributions on this set (~36 / ~21 / ~26). Here each feature
is standardized by its subset-60 mean so the three enter in **equal
proportions**, then a shared strength ``α`` is swept:

    score = L + α · (K/μ_K + MK/μ_MK + S/μ_S)

At typical starts each of the three terms contributes ``α``; ``α ≈ 28``
matches the average one-feature peak contribution. Cap 24; no xyimb.

    python3 -m experiments.heuristic_search.runners.run_kms_equal_b1k
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
OUT_CSV = os.path.join(ROOT, "results/comparison/kms_equal_b1k_subset60.csv")
OUT_MD = os.path.join(ROOT, "results/comparison/KMS_EQUAL_B1K.md")

BUDGET = 1_000
CAP = 24

# Fixed means on subset-60 originals (same set the one-feature sweeps used).
# Pinning them keeps the priority identity stable across re-runs.
MU_K = 4.533333333333333
MU_MK = 2.6
MU_S = 1.09

# Shared per-feature contribution. α≈28 ≈ mean of the three one-feature
# peak contributions (8·μ_K, 8·μ_MK, 24·μ_S). First pass peaked at the low
# edge (α=5 → 40/60), so the grid extends downward.
ALPHAS = (1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 15.0, 20.0, 28.0, 40.0)


def _kms(r1, r2):
    n1, x1, y1, xr1, yr1, _ = word_stats(r1)
    n2, x2, y2, xr2, yr2, _ = word_stats(r2)
    k1 = 0 if (x1 == 0 or y1 == 0) else max(x1, y1)
    k2 = 0 if (x2 == 0 or y2 == 0) else max(x2, y2)
    xs, ys = xr1 + xr2, yr1 + yr2
    mx = sum(xs) / len(xs) if xs else 0.0
    my = sum(ys) / len(ys) if ys else 0.0
    if not xs or not ys:
        s = (mx or my)
    else:
        s = min(mx, my)
    L = float(n1 + n2)
    K = float(k1 + k2)
    MK = float(max(k1, k2))
    return L, K, MK, float(s)


def make_priority(alpha):
    def priority(r1, r2):
        L, K, MK, S = _kms(r1, r2)
        return L + alpha * (K / MU_K + MK / MU_MK + S / MU_S)
    priority.__name__ = f"L+{alpha:g}*eq(K,MK,S)"
    return priority


def _tag(alpha):
    return f"eq_a{f'{alpha:g}'.replace('.', '_')}"


def _is_true(v):
    return v if isinstance(v, bool) else str(v).lower() == "true"


def run():
    with open(SOURCE) as f:
        src = list(csv.DictReader(f))
    if len(src) != 60:
        raise RuntimeError(f"expected 60, got {len(src)}")

    hsearch("X", "Y", 20, priority=make_priority(28.0), max_relator_length=CAP)

    fieldnames = [
        "pres_id", "bin", "r1", "r2",
        "b1k_greedy_solved", "b1k_greedy_nodes", "b1k_greedy_path",
        "b1k_heur_solved", "b1k_heur_nodes", "b1k_heur_path",
    ]
    for a in ALPHAS:
        tag = _tag(a)
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
        for a in ALPHAS:
            tag = _tag(a)
            res = hsearch(
                s["r1"], s["r2"], BUDGET,
                priority=make_priority(a), max_relator_length=CAP)
            row[f"{tag}_solved"] = bool(res["solved"])
            row[f"{tag}_nodes"] = int(res["nodes_explored"])
            row[f"{tag}_path"] = (
                int(res["path_length"]) if res["solved"] else "")
            if int(res["nodes_explored"]) > BUDGET:
                raise RuntimeError(
                    f"budget exceeded on ms{s['pres_id']} α={a}")
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
        raise SystemExit(f"α=0 control gate failed: {drift}")
    print("α=0 length-only control PASSED on first 5 rows", flush=True)

    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with open(OUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            out = dict(r)
            for a in ALPHAS:
                tag = _tag(a)
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

    # equivalent raw weights at a given α: w_f = α / μ_f
    def raw_w(alpha):
        return (alpha / MU_K, alpha / MU_MK, alpha / MU_S)

    summary = {}
    lines = [
        "# Equal-proportion K + MK + S at budget 1,000 (subset-60)",
        "",
        "Best one-feature peaks were `L+8·K` (37), `L+8·MK` (38), "
        "`L+24·S` (37). Those make unequal mean contributions on this set "
        f"(~{8*MU_K:.1f} / ~{8*MU_MK:.1f} / ~{24*MU_S:.1f}). This run "
        "standardizes each feature by its subset-60 mean so the three enter "
        "in **equal proportions**, then sweeps shared strength `α`:",
        "",
        "```",
        f"score = L + α · (K/{MU_K:g} + MK/{MU_MK:g} + S/{MU_S:g})",
        "```",
        "",
        "Equivalent raw weights: `w_K = α/μ_K`, `w_MK = α/μ_MK`, "
        "`w_S = α/μ_S`. At typical starts each feature contributes `α`. "
        f"`α ≈ 28` matches the average one-feature peak contribution "
        f"({(8*MU_K + 8*MU_MK + 24*MU_S)/3:.1f}). Cap 24; no xyimb.",
        "",
        "`S` = smaller mean block (thinner generator over the pair), not "
        "shorter-relator length.",
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

    lines.extend([
        "",
        "| α | raw (w_K, w_MK, w_S) | solved | mean nodes | med nodes | "
        "mean path | med path |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ])
    for a in ALPHAS:
        tag = _tag(a)
        n, mn, mdn, mp, mdp = arm_stats(
            f"{tag}_solved", f"{tag}_nodes", f"{tag}_path")
        summary[tag] = n
        wk, wmk, ws = raw_w(a)
        if n == 0:
            lines.append(
                f"| {a:g} | ({wk:.3f}, {wmk:.3f}, {ws:.3f}) | "
                f"**0/60** | — | — | — | — |")
        else:
            lines.append(
                f"| {a:g} | ({wk:.3f}, {wmk:.3f}, {ws:.3f}) | "
                f"**{n}/60** | {mn:.1f} | {mdn:.0f} | {mp:.1f} | {mdp:.0f} |")

    best_n = max(summary[_tag(a)] for a in ALPHAS)
    best_as = [a for a in ALPHAS if summary[_tag(a)] == best_n]
    best_a = best_as[0]
    wk, wmk, ws = raw_w(best_a)
    best_list = ", ".join(
        f"`α={a:g}` (raw `{raw_w(a)[0]:.3f}·K+{raw_w(a)[1]:.3f}·MK+"
        f"{raw_w(a)[2]:.3f}·S`)" for a in best_as)

    lines.extend([
        "",
        "## Verdict",
        "",
        f"- Best tune(s): {best_list} → **{best_n}/60**",
        f"- vs length-only 29/60 and full RECOMMENDED 43/60 "
        f"(RECOMMENDED also has xyimb).",
        f"- One-feature peaks for context: `L+8·MK` = 38/60, "
        f"`L+8·K` = 37/60, `L+24·S` = 37/60.",
        "",
        "## vs length-only / RECOMMENDED",
        "",
    ])
    for a in ALPHAS:
        tag = _tag(a)
        got = {r["pres_id"] for r in rows if r[f"{tag}_solved"]}
        lines.append(
            f"- α={a:g}: +{len(got - greedy)} over greedy, "
            f"-{len(greedy - got)} vs greedy; "
            f"vs RECOMMENDED +{len(got - heur)} / -{len(heur - got)}")

    lines.extend([
        "",
        "## Source",
        "",
        f"- Input: [`cov_heur_b1k_subset60.csv`](cov_heur_b1k_subset60.csv)",
        f"- Table: [`kms_equal_b1k_subset60.csv`](kms_equal_b1k_subset60.csv)",
        "- Runner: `experiments/heuristic_search/runners/run_kms_equal_b1k.py`",
        "- Prior one-feature: [`K_VS_KDEN_B1K.md`](K_VS_KDEN_B1K.md), "
        "[`MK_B1K.md`](MK_B1K.md), [`S_B1K.md`](S_B1K.md)",
        "",
    ])
    with open(OUT_MD, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"wrote {OUT_MD}")
    print(json.dumps(summary, indent=2))
    print(f"VERDICT: α={best_a:g} → {best_n}/60  "
          f"(w_K={wk:.3f}, w_MK={wmk:.3f}, w_S={ws:.3f})")
    return rows


def main():
    run()


if __name__ == "__main__":
    main()
