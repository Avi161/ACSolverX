"""Quick L + w·K_den search at budget 1,000 on the 60-row benchmark.

Priority::

    score = L + w * K_den
    K_den = (k1 + k2) / L

No xyimb, no MK, no S. Sweeps a few ``w`` values and compares to the shipped
length-only and RECOMMENDED arms at the same budget.

    .venv/bin/python3 -m experiments.heuristic_search.runners.run_kden_b1k
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
OUT_CSV = os.path.join(ROOT, "results/comparison/kden_b1k_subset60.csv")
OUT_MD = os.path.join(ROOT, "results/comparison/KDEN_B1K.md")

BUDGET = 1_000
CAP = 24
# K_den ~ 0.25; w~40 makes w·K_den ~ 10, same ballpark as a few letters of L
WEIGHTS = (10.0, 40.0, 80.0, 160.0)


def _kden(r1, r2):
    n1, x1, y1, *_ = word_stats(r1)
    n2, x2, y2, *_ = word_stats(r2)
    k1 = 0 if (x1 == 0 or y1 == 0) else max(x1, y1)
    k2 = 0 if (x2 == 0 or y2 == 0) else max(x2, y2)
    L = n1 + n2
    return (float(L), (k1 + k2) / L if L else 0.0)


def make_priority(w):
    def priority(r1, r2):
        L, kd = _kden(r1, r2)
        return L + w * kd
    priority.__name__ = f"L+{w:g}*K_den"
    return priority


def run():
    with open(SOURCE) as f:
        src = list(csv.DictReader(f))
    if len(src) != 60:
        raise RuntimeError(f"expected 60, got {len(src)}")

    # warm
    hsearch("X", "Y", 20, priority=make_priority(40.0), max_relator_length=CAP)

    fieldnames = [
        "pres_id", "bin", "r1", "r2",
        "b1k_greedy_solved", "b1k_greedy_nodes", "b1k_greedy_path",
        "b1k_heur_solved", "b1k_heur_nodes", "b1k_heur_path",
    ]
    for w in WEIGHTS:
        tag = f"kden_w{w:g}"
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
            tag = f"kden_w{w:g}"
            res = hsearch(
                s["r1"], s["r2"], BUDGET,
                priority=make_priority(w), max_relator_length=CAP)
            row[f"{tag}_solved"] = bool(res["solved"])
            row[f"{tag}_nodes"] = int(res["nodes_explored"])
            row[f"{tag}_path"] = (
                int(res["path_length"]) if res["solved"] else "")
            if int(res["nodes_explored"]) > BUDGET:
                raise RuntimeError(f"budget exceeded on ms{s['pres_id']} w={w}")
        rows.append(row)
        if (i + 1) % 10 == 0 or i + 1 == len(src):
            print(f"  [{i+1}/60] {time.time()-t0:.0f}s", flush=True)

    # control: length-only via w=0 should match greedy on solved+nodes
    # spot-check first 5 with w=0
    drift = []
    p0 = make_priority(0.0)
    for s in src[:5]:
        res = hsearch(s["r1"], s["r2"], BUDGET, priority=p0, max_relator_length=CAP)
        want_sol = str(s["b1k_greedy_solved"]).lower() == "true"
        want_n = int(s["b1k_greedy_nodes"])
        if (bool(res["solved"]), int(res["nodes_explored"])) != (want_sol, want_n):
            drift.append((s["pres_id"], want_n, want_sol,
                          res["nodes_explored"], res["solved"]))
    if drift:
        raise SystemExit(f"w=0 control gate failed: {drift}")
    print("w=0 length-only control PASSED on first 5 rows", flush=True)

    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with open(OUT_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            out = dict(r)
            for wgt in WEIGHTS:
                tag = f"kden_w{wgt:g}"
                out[f"{tag}_solved"] = "true" if r[f"{tag}_solved"] else "false"
            w.writerow(out)
    print(f"wrote {OUT_CSV}")

    def arm_stats(solved_key, nodes_key, path_key, boolish=True):
        if boolish:
            sol = [r for r in rows if (
                r[solved_key] if isinstance(r[solved_key], bool)
                else str(r[solved_key]).lower() == "true")]
        else:
            sol = [r for r in rows if str(r[solved_key]).lower() == "true"]
        if not sol:
            return 0, None, None, None, None
        nodes = [int(r[nodes_key]) for r in sol]
        paths = [int(r[path_key]) for r in sol if str(r[path_key]) != ""]
        return (len(sol),
                statistics.fmean(nodes), statistics.median(nodes),
                statistics.fmean(paths) if paths else None,
                statistics.median(paths) if paths else None)

    lines = [
        "# L + w·K_den at budget 1,000 (subset-60)",
        "",
        "Priority `L + w * ((k1+k2)/L)`. Cap 24. Compared to shipped "
        "`b1k_greedy` (length-only) and `b1k_heur` (full RECOMMENDED).",
        "",
        "Mean/median nodes and path are over **solved** rows only.",
        "",
        "| arm | solved | mean nodes | med nodes | mean path | med path |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    summary = {}
    for label, sk, nk, pk, is_bool in (
        ("b1k_greedy (L only)", "b1k_greedy_solved", "b1k_greedy_nodes",
         "b1k_greedy_path", False),
        ("b1k_heur (RECOMMENDED)", "b1k_heur_solved", "b1k_heur_nodes",
         "b1k_heur_path", False),
    ):
        n, mn, mdn, mp, mdp = arm_stats(sk, nk, pk, boolish=is_bool)
        summary[label] = n
        lines.append(
            f"| {label} | **{n}/60** | {mn:.1f} | {mdn:.0f} | "
            f"{mp:.1f} | {mdp:.0f} |")

    for wgt in WEIGHTS:
        tag = f"kden_w{wgt:g}"
        n, mn, mdn, mp, mdp = arm_stats(
            f"{tag}_solved", f"{tag}_nodes", f"{tag}_path", boolish=True)
        summary[tag] = n
        lines.append(
            f"| `L + {wgt:g}·K_den` | **{n}/60** | {mn:.1f} | {mdn:.0f} | "
            f"{mp:.1f} | {mdp:.0f} |")

    # gains vs greedy
    greedy = {r["pres_id"] for r in rows
              if str(r["b1k_greedy_solved"]).lower() == "true"}
    heur = {r["pres_id"] for r in rows
            if str(r["b1k_heur_solved"]).lower() == "true"}
    lines.extend(["", "## vs length-only", ""])
    for wgt in WEIGHTS:
        tag = f"kden_w{wgt:g}"
        got = {r["pres_id"] for r in rows if r[f"{tag}_solved"]}
        lines.append(
            f"- w={wgt:g}: +{len(got - greedy)} over greedy, "
            f"-{len(greedy - got)} vs greedy; "
            f"vs RECOMMENDED +{len(got - heur)} / -{len(heur - got)}")

    lines.extend([
        "",
        "## Source",
        "",
        f"- Input: [`cov_heur_b1k_subset60.csv`](cov_heur_b1k_subset60.csv)",
        f"- Table: [`kden_b1k_subset60.csv`](kden_b1k_subset60.csv)",
        "- Runner: `experiments/heuristic_search/runners/run_kden_b1k.py`",
        "",
    ])
    with open(OUT_MD, "w") as f:
        f.write("\n".join(lines))
    print(f"wrote {OUT_MD}")
    print(json.dumps(summary, indent=2))
    return rows


def main():
    run()


if __name__ == "__main__":
    main()
