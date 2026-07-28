"""L + w·K_den vs L + w·K at budget 1,000 on the 60-row benchmark.

Two one-feature families, different weight scales (K ≈ 4.5, K_den ≈ 0.25
on this set, so the same numeric ``w`` is not comparable):

* ``K_den`` weights ``{5, 10, 20, 40, 80}`` — extends the earlier
  ``run_kden_b1k`` sweep (adds 5 and 20; drops the collapsed 160).
* ``K`` (total knots ``k1+k2``) weights
  ``{0.5, 1, 2, 2.53, 5, 8, 10, 16}`` — the productive ``K_den`` band maps
  to ``w_K ≈ w_den · K_den/K ≈ w_den/L`` (~0.5–2.2 for ``w_den`` 10–40);
  2.53 is the shipped RECOMMENDED ``K`` coefficient; 5 is one step above
  that band; ``{8, 10, 16}`` probe upward because the mapped-band edge
  won the first pass.

No xyimb, no MK, no S. Cap 24. Compared to shipped length-only and
RECOMMENDED arms at the same budget.

    python3 -m experiments.heuristic_search.runners.run_k_vs_kden_b1k
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
OUT_CSV = os.path.join(ROOT, "results/comparison/k_vs_kden_b1k_subset60.csv")
OUT_MD = os.path.join(ROOT, "results/comparison/K_VS_KDEN_B1K.md")

BUDGET = 1_000
CAP = 24

# Density: prior best was w=10 (32/60); fill the gap at 5 and 20.
KDEN_WEIGHTS = (5.0, 10.0, 20.0, 40.0, 80.0)

# Raw knots: scale so w_K·K ≈ w_den·K_den on this set (K≈4.5, K_den≈0.25,
# L≈19 → w_K ≈ w_den/L). Productive dens band 10–40 ⇒ ~0.5–2.2; plus
# RECOMMENDED's 2.53, one step above (5), then an upward probe (8, 10, 16)
# because the mapped-band edge won the first pass.
K_WEIGHTS = (0.5, 1.0, 2.0, 2.53, 5.0, 8.0, 10.0, 16.0)


def _knot_pair(r1, r2):
    n1, x1, y1, *_ = word_stats(r1)
    n2, x2, y2, *_ = word_stats(r2)
    k1 = 0 if (x1 == 0 or y1 == 0) else max(x1, y1)
    k2 = 0 if (x2 == 0 or y2 == 0) else max(x2, y2)
    L = float(n1 + n2)
    K = float(k1 + k2)
    kden = (K / L) if L else 0.0
    return L, K, kden


def make_kden_priority(w):
    def priority(r1, r2):
        L, _K, kd = _knot_pair(r1, r2)
        return L + w * kd
    priority.__name__ = f"L+{w:g}*K_den"
    return priority


def make_k_priority(w):
    def priority(r1, r2):
        L, K, _kd = _knot_pair(r1, r2)
        return L + w * K
    priority.__name__ = f"L+{w:g}*K"
    return priority


def _tag_kden(w):
    return f"kden_w{w:g}"


def _tag_k(w):
    # Underscore for the decimal so CSV headers stay simple: k_w2_53
    s = f"{w:g}".replace(".", "_")
    return f"k_w{s}"


def _is_true(v):
    return v if isinstance(v, bool) else str(v).lower() == "true"


def run():
    with open(SOURCE) as f:
        src = list(csv.DictReader(f))
    if len(src) != 60:
        raise RuntimeError(f"expected 60, got {len(src)}")

    # warm both priority shapes
    hsearch("X", "Y", 20, priority=make_kden_priority(10.0),
            max_relator_length=CAP)
    hsearch("X", "Y", 20, priority=make_k_priority(2.53),
            max_relator_length=CAP)

    arms = (
        [("kden", w, make_kden_priority(w), _tag_kden(w)) for w in KDEN_WEIGHTS]
        + [("k", w, make_k_priority(w), _tag_k(w)) for w in K_WEIGHTS]
    )

    fieldnames = [
        "pres_id", "bin", "r1", "r2",
        "b1k_greedy_solved", "b1k_greedy_nodes", "b1k_greedy_path",
        "b1k_heur_solved", "b1k_heur_nodes", "b1k_heur_path",
    ]
    for _fam, _w, _prio, tag in arms:
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
        for _fam, w, prio, tag in arms:
            res = hsearch(
                s["r1"], s["r2"], BUDGET,
                priority=prio, max_relator_length=CAP)
            row[f"{tag}_solved"] = bool(res["solved"])
            row[f"{tag}_nodes"] = int(res["nodes_explored"])
            row[f"{tag}_path"] = (
                int(res["path_length"]) if res["solved"] else "")
            if int(res["nodes_explored"]) > BUDGET:
                raise RuntimeError(
                    f"budget exceeded on ms{s['pres_id']} {tag} w={w}")
        rows.append(row)
        if (i + 1) % 10 == 0 or i + 1 == len(src):
            print(f"  [{i+1}/60] {time.time()-t0:.0f}s", flush=True)

    # control: w=0 length-only must match greedy on first 5
    drift = []
    p0 = make_kden_priority(0.0)
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
            for _fam, _w, _prio, tag in arms:
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

    lines = [
        "# L + w·K_den vs L + w·K at budget 1,000 (subset-60)",
        "",
        "One-feature orderings, no xyimb / MK / S. Cap 24. Compared to "
        "shipped `b1k_greedy` (length-only) and `b1k_heur` (full RECOMMENDED).",
        "",
        "## Why the weight ranges differ",
        "",
        "On this set the original starts have mean `K ≈ 4.53` and "
        "`K_den ≈ 0.247` (mean `L ≈ 19.3`). Matching priority contribution "
        "`w_K · K ≈ w_den · K_den` gives `w_K ≈ w_den / L`:",
        "",
        "| `w_den` | ≈ matching `w_K` |",
        "|---:|---:|",
        "| 5 | 0.27 |",
        "| 10 | 0.55 |",
        "| 20 | 1.09 |",
        "| 40 | 2.18 |",
        "| 80 | 4.36 |",
        "",
        "So the `K_den` grid stays at `{5, 10, 20, 40, 80}` (prior peak was "
        "`w=10` → 32/60; 160 collapsed to 1/60 and is dropped). The raw-`K` "
        "grid starts at `{0.5, 1, 2, 2.53, 5}` (dens-band map + RECOMMENDED "
        "`2.53` + one step above) and extends to `{8, 10, 16}` after the "
        "mapped-band edge won the first pass.",
        "",
        "Mean/median nodes and path are over **solved** rows only.",
        "",
        "| arm | solved | mean nodes | med nodes | mean path | med path |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    summary = {}
    for label, sk, nk, pk in (
        ("b1k_greedy (L only)", "b1k_greedy_solved", "b1k_greedy_nodes",
         "b1k_greedy_path"),
        ("b1k_heur (RECOMMENDED)", "b1k_heur_solved", "b1k_heur_nodes",
         "b1k_heur_path"),
    ):
        n, mn, mdn, mp, mdp = arm_stats(sk, nk, pk)
        summary[label] = n
        lines.append(fmt_row(label, n, mn, mdn, mp, mdp))

    lines.extend(["", "### `L + w·K_den`", ""])
    lines.append(
        "| arm | solved | mean nodes | med nodes | mean path | med path |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for w in KDEN_WEIGHTS:
        tag = _tag_kden(w)
        n, mn, mdn, mp, mdp = arm_stats(
            f"{tag}_solved", f"{tag}_nodes", f"{tag}_path")
        summary[tag] = n
        lines.append(fmt_row(f"`L + {w:g}·K_den`", n, mn, mdn, mp, mdp))

    lines.extend(["", "### `L + w·K` (total knots)", ""])
    lines.append(
        "| arm | solved | mean nodes | med nodes | mean path | med path |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for w in K_WEIGHTS:
        tag = _tag_k(w)
        n, mn, mdn, mp, mdp = arm_stats(
            f"{tag}_solved", f"{tag}_nodes", f"{tag}_path")
        summary[tag] = n
        lines.append(fmt_row(f"`L + {w:g}·K`", n, mn, mdn, mp, mdp))

    # best of each family
    best_kden = max(KDEN_WEIGHTS, key=lambda w: summary[_tag_kden(w)])
    best_k = max(K_WEIGHTS, key=lambda w: summary[_tag_k(w)])
    n_kd = summary[_tag_kden(best_kden)]
    n_k = summary[_tag_k(best_k)]
    winner = (
        f"`L + {best_kden:g}·K_den` ({n_kd}/60)"
        if n_kd > n_k else
        f"`L + {best_k:g}·K` ({n_k}/60)"
        if n_k > n_kd else
        f"tie at {n_kd}/60 "
        f"(`L + {best_kden:g}·K_den` vs `L + {best_k:g}·K`)"
    )

    lines.extend([
        "",
        "## Verdict",
        "",
        f"- Best density arm: `L + {best_kden:g}·K_den` → **{n_kd}/60**",
        f"- Best raw-K arm: `L + {best_k:g}·K` → **{n_k}/60**",
        f"- Winner (solve count): {winner}",
        f"- Both vs length-only 29/60 and full RECOMMENDED 43/60.",
        "",
        "## vs length-only / RECOMMENDED",
        "",
    ])
    for fam, weights, tag_fn, label in (
        ("K_den", KDEN_WEIGHTS, _tag_kden, "K_den"),
        ("K", K_WEIGHTS, _tag_k, "K"),
    ):
        lines.append(f"### {label}")
        lines.append("")
        for w in weights:
            tag = tag_fn(w)
            got = {r["pres_id"] for r in rows if r[f"{tag}_solved"]}
            lines.append(
                f"- w={w:g}: +{len(got - greedy)} over greedy, "
                f"-{len(greedy - got)} vs greedy; "
                f"vs RECOMMENDED +{len(got - heur)} / -{len(heur - got)}")
        lines.append("")

    # pairwise: which presentations each family uniquely unlocks at its best
    got_kd = {r["pres_id"] for r in rows
              if r[f"{_tag_kden(best_kden)}_solved"]}
    got_k = {r["pres_id"] for r in rows
             if r[f"{_tag_k(best_k)}_solved"]}
    lines.extend([
        "## Best arms head-to-head",
        "",
        f"- Only density (`w={best_kden:g}`): "
        f"{sorted(got_kd - got_k, key=lambda x: int(x))}",
        f"- Only raw K (`w={best_k:g}`): "
        f"{sorted(got_k - got_kd, key=lambda x: int(x))}",
        f"- Both: {len(got_kd & got_k)}; neither of these two: "
        f"{60 - len(got_kd | got_k)}",
        "",
        "## Source",
        "",
        f"- Input: [`cov_heur_b1k_subset60.csv`](cov_heur_b1k_subset60.csv)",
        f"- Table: [`k_vs_kden_b1k_subset60.csv`](k_vs_kden_b1k_subset60.csv)",
        "- Runner: `experiments/heuristic_search/runners/run_k_vs_kden_b1k.py`",
        "- Prior dens-only sweep: [`KDEN_B1K.md`](KDEN_B1K.md)",
        "",
    ])
    with open(OUT_MD, "w") as f:
        f.write("\n".join(lines))
    print(f"wrote {OUT_MD}")
    print(json.dumps(summary, indent=2))
    print(f"VERDICT: {winner}")
    return rows


def main():
    run()


if __name__ == "__main__":
    main()
