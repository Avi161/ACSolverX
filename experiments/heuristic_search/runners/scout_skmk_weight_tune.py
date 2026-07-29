"""Hundreds of (S, K, MK) weight combos at budget 1,000 — no xyimb.

Grid (including zeros so pure-S / pure-K / pure-MK / pairs are covered):

  S  ∈ {0, 4, 8, 12, 16, 20, 24, 28}
  K  ∈ {0, 1, 2, 2.53, 4, 6, 8}
  MK ∈ {0, 2, 4, 6.418, 8, 10}

= 8 × 7 × 6 = **336** arms. Skip the all-zero (identical to length-only,
kept once as ``length``). Dataset: frozen fresh_hard 60 (primary) and
l_stratified 80 (secondary readout).

    python3 -m experiments.heuristic_search.runners.scout_skmk_weight_tune
"""
from __future__ import annotations

import itertools
import json
import os
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

from experiments.heuristic_search.core.hcompact import greedy_search_hcompact  # noqa: E402

ROOT = _d
OUT_DIR = os.path.join(ROOT, "results", "heuristic_search", "skmk_tune")
JSONL = os.path.join(OUT_DIR, "runs.jsonl")
SUMMARY = os.path.join(OUT_DIR, "arm_summary.jsonl")
RESULTS = os.path.join(OUT_DIR, "RESULTS.md")
CSV = os.path.join(OUT_DIR, "arm_ranking.csv")
SLICE_H = os.path.join(ROOT, "results", "heuristic_search", "scale10k",
                       "slice_fresh_hard.json")
SLICE_L = os.path.join(ROOT, "results", "heuristic_search", "scale10k",
                       "slice_l_stratified.json")
BUDGET = 1000
CAP = 48
RESERVE = 120 * BUDGET

S_GRID = (0.0, 4.0, 8.0, 12.0, 16.0, 20.0, 24.0, 28.0)
K_GRID = (0.0, 1.0, 2.0, 2.53, 4.0, 6.0, 8.0)
MK_GRID = (0.0, 2.0, 4.0, 6.418, 8.0, 10.0)


def _tag(s, k, mk):
    def f(x):
        return f"{x:g}".replace(".", "_")
    return f"S{f(s)}_K{f(k)}_MK{f(mk)}"


def _cfg(s, k, mk):
    w = {"L": 1.0}
    if s:
        w["S"] = float(s)
    if k:
        w["K"] = float(k)
    if mk:
        w["MK"] = float(mk)
    return {"segments": [{"upto": None, "w": w}]}


def all_arms():
    arms = [("length", None, 0.0, 0.0, 0.0)]
    for s, k, mk in itertools.product(S_GRID, K_GRID, MK_GRID):
        if s == 0 and k == 0 and mk == 0:
            continue  # covered by length
        arms.append((_tag(s, k, mk), _cfg(s, k, mk), s, k, mk))
    return arms


def _iso():
    return datetime.now(timezone.utc).isoformat()


def _append(path, row):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(row) + "\n")
        f.flush()
        os.fsync(f.fileno())


def _done(path, keys):
    s = set()
    if not os.path.exists(path):
        return s
    for line in open(path):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        s.add(tuple(r.get(k) for k in keys))
    return s


def _search(r1, r2, cfg):
    t0 = time.perf_counter()
    res = greedy_search_hcompact(
        r1, r2, BUDGET, max_relator_length=CAP, config=cfg,
        reserve_states=RESERVE)
    dt = time.perf_counter() - t0
    return {
        "solved": bool(res["solved"]),
        "nodes": int(res["nodes_explored"]),
        "solved_at": int(res["nodes_explored"]) if res["solved"] else None,
        "secs": round(dt, 3),
        "pops_s": round(res["nodes_explored"] / max(dt, 1e-9), 1),
    }


def run_slice(slice_path, slice_name, arms):
    rows = json.load(open(slice_path))["rows"]
    done = _done(JSONL, ("slice", "arm", "idx"))
    n_new = 0
    t0 = time.time()
    total = len(rows) * len(arms)
    print(f"[tune] {slice_name}: {len(rows)}×{len(arms)}={total} "
          f"resumed={len([1 for d in done if d[0]==slice_name])}", flush=True)
    for rec in rows:
        for arm, cfg, s, k, mk in arms:
            key = (slice_name, arm, rec["idx"])
            if key in done:
                continue
            res = _search(rec["r1"], rec["r2"], cfg)
            _append(JSONL, {
                "slice": slice_name, "arm": arm,
                "S": s, "K": k, "MK": mk,
                "idx": rec["idx"], "L": rec.get("L"),
                "budget": BUDGET, "cap": CAP,
                "ts": _iso(), **res,
            })
            done.add(key)
            n_new += 1
            if n_new % 50 == 0:
                rate = n_new / max(time.time() - t0, 1e-9)
                print(f"  +{n_new} {rate:.2f}/s last={arm} "
                      f"sol={res['solved']}", flush=True)
    print(f"[tune] {slice_name} new={n_new}", flush=True)
    return n_new


def summarize():
    rows = []
    for line in open(JSONL):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        rows.append(r)

    # per (slice, arm)
    by = defaultdict(list)
    for r in rows:
        by[(r["slice"], r["arm"])].append(r)

    summaries = []
    if os.path.exists(SUMMARY):
        os.remove(SUMMARY)
    for (sl, arm), rs in by.items():
        sol = [r for r in rs if r["solved"]]
        mean_n = (sum(r["nodes"] for r in sol) / len(sol)) if sol else None
        row = {
            "slice": sl,
            "arm": arm,
            "S": rs[0]["S"], "K": rs[0]["K"], "MK": rs[0]["MK"],
            "n": len(rs),
            "solved": len(sol),
            "solve_rate": len(sol) / len(rs) if rs else 0.0,
            "mean_nodes_solved": mean_n,
            "mean_nodes_all": sum(r["nodes"] for r in rs) / len(rs),
        }
        summaries.append(row)
        _append(SUMMARY, row)

    # write rankings
    lines = [
        "# S+K+MK weight tune @ budget 1,000 (no xyimb)",
        "",
        f"Updated `{_iso()}`",
        "",
        f"Grid: S∈{list(S_GRID)}, K∈{list(K_GRID)}, MK∈{list(MK_GRID)} "
        f"→ **{len(S_GRID)*len(K_GRID)*len(MK_GRID)}** cells "
        f"(+ `length` = all-zero). No `xyimb`.",
        "",
        f"Total search rows: **{len(rows)}**.",
        "",
    ]

    for sl in ("fresh_hard", "l_stratified"):
        sub = [s for s in summaries if s["slice"] == sl]
        if not sub:
            continue
        sub.sort(key=lambda r: (
            r["solved"],
            -(r["mean_nodes_solved"] or 1e9),
        ), reverse=True)
        n_pres = sub[0]["n"] if sub else 0
        lines += [
            f"## `{sl}` (n={n_pres} presentations)",
            "",
            f"**Best:** `{sub[0]['arm']}` → "
            f"**{sub[0]['solved']}/{sub[0]['n']}** "
            f"(S={sub[0]['S']:g}, K={sub[0]['K']:g}, MK={sub[0]['MK']:g})"
            + (f", mean nodes {sub[0]['mean_nodes_solved']:.0f}"
               if sub[0]["mean_nodes_solved"] else ""),
            "",
            "### Top 25",
            "",
            "| rank | arm | S | K | MK | solved | mean nodes |",
            "|---:|---|---:|---:|---:|---:|---:|",
        ]
        for i, r in enumerate(sub[:25], 1):
            mn = f"{r['mean_nodes_solved']:.0f}" if r["mean_nodes_solved"] else "—"
            lines.append(
                f"| {i} | `{r['arm']}` | {r['S']:g} | {r['K']:g} | "
                f"{r['MK']:g} | **{r['solved']}/{r['n']}** | {mn} |")
        lines.append("")

        # family breakdowns
        def fam(pred, title):
            xs = [r for r in sub if pred(r)]
            if not xs:
                return
            lines.append(f"### {title} (best 10)")
            lines.append("")
            lines.append("| arm | S | K | MK | solved |")
            lines.append("|---|---:|---:|---:|---:|")
            for r in xs[:10]:
                lines.append(
                    f"| `{r['arm']}` | {r['S']:g} | {r['K']:g} | "
                    f"{r['MK']:g} | {r['solved']}/{r['n']} |")
            lines.append("")

        fam(lambda r: r["S"] > 0 and r["K"] == 0 and r["MK"] == 0, "Pure S")
        fam(lambda r: r["S"] == 0 and r["K"] > 0 and r["MK"] == 0, "Pure K")
        fam(lambda r: r["S"] == 0 and r["K"] == 0 and r["MK"] > 0, "Pure MK")
        fam(lambda r: r["S"] > 0 and r["K"] > 0 and r["MK"] == 0, "S+K (no MK)")
        fam(lambda r: r["S"] > 0 and r["K"] == 0 and r["MK"] > 0, "S+MK (no K)")
        fam(lambda r: r["S"] == 0 and r["K"] > 0 and r["MK"] > 0, "K+MK (no S)")
        fam(lambda r: r["S"] > 0 and r["K"] > 0 and r["MK"] > 0, "S+K+MK (all three)")
        fam(lambda r: r["arm"] == "length", "Length-only control")

        # best of each family
        lines.append("### Best of each family")
        lines.append("")
        for name, pred in [
            ("length", lambda r: r["arm"] == "length"),
            ("pure S", lambda r: r["S"] > 0 and r["K"] == 0 and r["MK"] == 0),
            ("pure K", lambda r: r["S"] == 0 and r["K"] > 0 and r["MK"] == 0),
            ("pure MK", lambda r: r["S"] == 0 and r["K"] == 0 and r["MK"] > 0),
            ("S+K", lambda r: r["S"] > 0 and r["K"] > 0 and r["MK"] == 0),
            ("S+MK", lambda r: r["S"] > 0 and r["K"] == 0 and r["MK"] > 0),
            ("K+MK", lambda r: r["S"] == 0 and r["K"] > 0 and r["MK"] > 0),
            ("S+K+MK", lambda r: r["S"] > 0 and r["K"] > 0 and r["MK"] > 0),
        ]:
            xs = [r for r in sub if pred(r)]
            if not xs:
                continue
            b = xs[0]  # already sorted
            lines.append(
                f"- **{name}:** `{b['arm']}` → {b['solved']}/{b['n']} "
                f"(S={b['S']:g}, K={b['K']:g}, MK={b['MK']:g})")
        lines.append("")

    # CSV of all fresh_hard ranks
    import csv
    hard = [s for s in summaries if s["slice"] == "fresh_hard"]
    hard.sort(key=lambda r: (r["solved"], -(r["mean_nodes_solved"] or 1e9)),
              reverse=True)
    with open(CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "rank", "arm", "S", "K", "MK", "solved", "n", "solve_rate",
            "mean_nodes_solved", "mean_nodes_all"])
        w.writeheader()
        for i, r in enumerate(hard, 1):
            w.writerow({
                "rank": i, "arm": r["arm"], "S": r["S"], "K": r["K"],
                "MK": r["MK"], "solved": r["solved"], "n": r["n"],
                "solve_rate": round(r["solve_rate"], 4),
                "mean_nodes_solved": r["mean_nodes_solved"],
                "mean_nodes_all": r["mean_nodes_all"],
            })

    lines += [
        "## Files",
        "",
        f"- Ranking CSV (fresh_hard): [`arm_ranking.csv`](arm_ranking.csv)",
        f"- Per-arm jsonl: [`arm_summary.jsonl`](arm_summary.jsonl)",
        f"- Raw: [`runs.jsonl`](runs.jsonl)",
        "",
    ]
    open(RESULTS, "w").write("\n".join(lines) + "\n")
    print(f"wrote {RESULTS} and {CSV}", flush=True)
    if hard:
        b = hard[0]
        print(f"BEST fresh_hard: {b['arm']} {b['solved']}/{b['n']} "
              f"S={b['S']} K={b['K']} MK={b['MK']}", flush=True)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    arms = all_arms()
    print(f"[tune] {len(arms)} arms (incl length) @ budget {BUDGET}", flush=True)
    greedy_search_hcompact("X", "Y", 50, max_relator_length=CAP,
                           config=_cfg(12, 0, 0), reserve_states=5000)
    # Primary: fresh_hard (the ranking that matters for hard recovery)
    run_slice(SLICE_H, "fresh_hard", arms)
    summarize()
    # Secondary: L-stratified
    run_slice(SLICE_L, "l_stratified", arms)
    summarize()
    print("[tune] DONE", flush=True)


if __name__ == "__main__":
    main()
