"""Depth tie-break flip on bench60: (score, +depth) vs (score, −depth).

Uses ``search_fast(..., tie=±1)`` — already supported in hfast (new scout only).
Arms: length-only and S20_MK2. Budget 1000, cap 48 (local hard cap).

``tie=+1`` (current): among equal score, prefer shallower (BFS-among-ties).
``tie=-1`` (proposal): among equal score, prefer deeper (DFS-among-ties).

    PYTHONPATH=. python3 -m experiments.heuristic_search.runners.scout_depth_tie_bench60
"""
from __future__ import annotations

import csv
import json
import os
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from statistics import mean, median

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

from experiments.heuristic_search.core.hfast import search_fast  # noqa: E402

ROOT = _d
SUBSET = os.path.join(ROOT, "benchmark", "subsets", "benchmark_subset_60.json")
ARMS_JSON = os.path.join(ROOT, "benchmark", "subsets",
                         "benchmark_subset_60_arms.json")
OUT_DIR = os.path.join(ROOT, "results", "heuristic_search", "depth_tie_bench60")
JSONL = os.path.join(OUT_DIR, "runs.jsonl")
RESULTS = os.path.join(OUT_DIR, "RESULTS.md")
CSV_OUT = os.path.join(OUT_DIR, "per_row.csv")
BUDGET = 1000
CAP = 48

CFGS = {
    "length": {"segments": [{"upto": None, "w": {"L": 1.0}}]},
    "s20_mk2": {"segments": [{"upto": None, "w": {"L": 1.0, "S": 20.0, "MK": 2.0}}]},
}
TIES = (1, -1)


def _load_rows():
    d = json.load(open(SUBSET))
    # subset list under "subset" — each entry has name/r1/r2/bin or similar
    raw = d["subset"]
    arms = {int(r["pres_id"]): r for r in json.load(open(ARMS_JSON))["rows"]}
    rows = []
    for item in raw:
        if isinstance(item, dict):
            pid = int(item.get("pres_id", item.get("id")))
            r1, r2 = item["r1"], item["r2"]
            binn = int(item.get("bin", arms[pid]["bin"]))
            name = item.get("name", f"ms{pid}")
        else:
            # sometimes just pres_id ints
            pid = int(item)
            a = arms[pid]
            r1, r2, binn = a["r1"], a["r2"], int(a["bin"])
            name = f"ms{pid}"
        a = arms[pid]
        rows.append({
            "pres_id": pid, "name": name, "bin": binn, "r1": r1, "r2": r2,
            "b1k_greedy_solved": bool(a["b1k_greedy_solved"]),
            "b1k_greedy_nodes": a.get("b1k_greedy_nodes"),
            "b1k_greedy_path": a.get("b1k_greedy_path"),
            "m10k_greedy_solved": bool(a["m10k_greedy_solved"]),
            "m10k_greedy_nodes": a.get("m10k_greedy_nodes"),
            "m10k_greedy_path": a.get("m10k_greedy_path"),
            "greedy_1m_nodes": a.get("greedy_nodes"),
            "greedy_1m_path": a.get("greedy_path"),
        })
    rows.sort(key=lambda r: (r["bin"], r["pres_id"]))
    return rows


def _done():
    s = set()
    if not os.path.exists(JSONL):
        return s
    for line in open(JSONL):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        s.add((r["arm"], r["tie"], r["pres_id"]))
    return s


def _append(row):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(JSONL, "a") as f:
        f.write(json.dumps(row) + "\n")
        f.flush()
        os.fsync(f.fileno())


def _stats(vals):
    if not vals:
        return {"n": 0}
    return {
        "n": len(vals),
        "mean": mean(vals),
        "median": median(vals),
        "min": min(vals),
        "max": max(vals),
    }


def main():
    rows = _load_rows()
    print(f"[depth-tie] n={len(rows)} arms={list(CFGS)} ties={list(TIES)} "
          f"budget={BUDGET} cap={CAP}", flush=True)
    # warm
    search_fast("xyx", "yx", 30, CFGS["s20_mk2"], 32, tie=1)
    search_fast("xyx", "yx", 30, CFGS["s20_mk2"], 32, tie=-1)

    done = _done()
    t0 = time.perf_counter()
    n_new = 0
    for arm, cfg in CFGS.items():
        for tie in TIES:
            for rec in rows:
                key = (arm, tie, rec["pres_id"])
                if key in done:
                    continue
                res = search_fast(rec["r1"], rec["r2"], BUDGET, cfg, CAP,
                                  tie=tie)
                _append({
                    "arm": arm, "tie": int(tie),
                    "pres_id": rec["pres_id"], "name": rec["name"],
                    "bin": rec["bin"],
                    "budget": BUDGET, "cap": CAP,
                    "solved": bool(res["solved"]),
                    "nodes": int(res["nodes"]),
                    "solved_at": (int(res["nodes"]) if res["solved"] else None),
                    "path_length": res.get("path_length"),
                    "ts": datetime.now(timezone.utc).isoformat(),
                })
                n_new += 1
                if n_new % 20 == 0:
                    print(f"  +{n_new} {(time.perf_counter()-t0)/60:.1f} min "
                          f"last={arm} tie={tie:+d} {rec['name']} "
                          f"sol={res['solved']}", flush=True)
    print(f"[run] new={n_new}", flush=True)

    # load all
    data = [json.loads(l) for l in open(JSONL)]
    by = defaultdict(dict)  # (arm,tie) -> pres_id -> row
    for r in data:
        by[(r["arm"], r["tie"])][r["pres_id"]] = r

    arms_rows = {r["pres_id"]: r for r in rows}

    def summarize(arm, tie):
        mp = by[(arm, tie)]
        sol = [mp[pid] for pid in sorted(mp) if mp[pid]["solved"]]
        nodes = [r["nodes"] for r in sol]
        paths = [r["path_length"] for r in sol if r["path_length"] is not None]
        return {
            "solved": len(sol),
            "n": len(mp),
            "nodes": _stats(nodes),
            "path": _stats(paths),
            "mp": mp,
        }

    summaries = {(arm, tie): summarize(arm, tie)
                 for arm in CFGS for tie in TIES}

    # write per-row csv
    fieldnames = ["pres_id", "name", "bin",
                  "b1k_greedy_solved", "b1k_greedy_nodes", "b1k_greedy_path"]
    for arm in CFGS:
        for tie in TIES:
            tag = f"{arm}_tie{tie:+d}".replace("+", "p").replace("-", "m")
            fieldnames += [f"{tag}_solved", f"{tag}_nodes", f"{tag}_path"]
    with open(CSV_OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for rec in rows:
            row = {
                "pres_id": rec["pres_id"], "name": rec["name"], "bin": rec["bin"],
                "b1k_greedy_solved": rec["b1k_greedy_solved"],
                "b1k_greedy_nodes": rec["b1k_greedy_nodes"],
                "b1k_greedy_path": rec["b1k_greedy_path"],
            }
            for arm in CFGS:
                for tie in TIES:
                    tag = f"{arm}_tie{tie:+d}".replace("+", "p").replace("-", "m")
                    r = by[(arm, tie)][rec["pres_id"]]
                    row[f"{tag}_solved"] = r["solved"]
                    row[f"{tag}_nodes"] = r["nodes"]
                    row[f"{tag}_path"] = r["path_length"]
            w.writerow(row)

    def fmt_stat(s, key="median"):
        if not s or s.get("n", 0) == 0:
            return "—"
        return f"{s[key]:.1f}" if key == "mean" else f"{s[key]:.0f}"

    lines = [
        "# Depth tie-break on bench60 — `(score, +depth)` vs `(score, −depth)`",
        "",
        f"Updated `{datetime.now(timezone.utc).isoformat()}`",
        "",
        f"**evaluated_on** = `benchmark_subset_60` (n={len(rows)}), budget {BUDGET}, "
        f"cap {CAP}, engine `search_fast`.",
        "",
        "Heap entry is `((seg, score), tie·depth, key)`. "
        "`tie=+1` (shipped) prefers shallower ties; `tie=−1` prefers deeper. "
        "This never changes scores — only exact-score ties. "
        "(Precedent: EXP-24 on bins 4–7; this scout is the full 60 × s20_mk2.)",
        "",
        "## Headline @ budget 1,000",
        "",
        "| arm | tie | solved | median nodes | mean nodes | median path | mean path |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    g1 = sum(1 for r in rows if r["b1k_greedy_solved"])
    g_nodes = [float(r["b1k_greedy_nodes"]) for r in rows
               if r["b1k_greedy_solved"] and r["b1k_greedy_nodes"] not in (None, "")]
    g_paths = [float(r["b1k_greedy_path"]) for r in rows
               if r["b1k_greedy_solved"] and r["b1k_greedy_path"] not in (None, "")]
    lines.append(
        f"| greedy baseline (frozen) | +1 | **{g1}/60** | "
        f"{median(g_nodes):.0f} | {mean(g_nodes):.1f} | "
        f"{median(g_paths):.0f} | {mean(g_paths):.1f} |"
    )
    for arm in ("length", "s20_mk2"):
        for tie in TIES:
            s = summaries[(arm, tie)]
            tag = " ← current" if tie == 1 else " ← deepest"
            lines.append(
                f"| `{arm}`{tag} | {tie:+d} | **{s['solved']}/{s['n']}** | "
                f"{fmt_stat(s['nodes'])} | {fmt_stat(s['nodes'], 'mean')} | "
                f"{fmt_stat(s['path'])} | {fmt_stat(s['path'], 'mean')} |"
            )

    # paired +depth vs -depth
    lines += [
        "",
        "## `+depth` vs `−depth` (same arm, same engine)",
        "",
        "| arm | +depth solved | −depth solved | Δ solves | "
        "−depth-only | +depth-only | both |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for arm in ("length", "s20_mk2"):
        a = summaries[(arm, 1)]["mp"]
        b = summaries[(arm, -1)]["mp"]
        only_m = only_p = both = 0
        for pid in a:
            sa, sb = a[pid]["solved"], b[pid]["solved"]
            if sa and sb:
                both += 1
            elif sb and not sa:
                only_m += 1
            elif sa and not sb:
                only_p += 1
        lines.append(
            f"| `{arm}` | {summaries[(arm,1)]['solved']} | "
            f"{summaries[(arm,-1)]['solved']} | "
            f"{summaries[(arm,-1)]['solved']-summaries[(arm,1)]['solved']:+d} | "
            f"{only_m} | {only_p} | {both} |"
        )

    # path/nodes on jointly solved by both ties
    lines += [
        "",
        "### Cost on jointly solved (both ties)",
        "",
        "| arm | n joint | median nodes (+/−) | median path (+/−) | "
        "mean path (+/−) |",
        "|---|---:|---|---|---|",
    ]
    for arm in ("length", "s20_mk2"):
        a = summaries[(arm, 1)]["mp"]
        b = summaries[(arm, -1)]["mp"]
        np_, nm, pp, pm = [], [], [], []
        for pid in a:
            if a[pid]["solved"] and b[pid]["solved"]:
                np_.append(a[pid]["nodes"])
                nm.append(b[pid]["nodes"])
                if a[pid]["path_length"] is not None:
                    pp.append(a[pid]["path_length"])
                if b[pid]["path_length"] is not None:
                    pm.append(b[pid]["path_length"])
        if not np_:
            lines.append(f"| `{arm}` | 0 | — | — | — |")
            continue
        lines.append(
            f"| `{arm}` | {len(np_)} | {median(np_):.0f} / {median(nm):.0f} | "
            f"{median(pp):.0f} / {median(pm):.0f} | "
            f"{mean(pp):.1f} / {mean(pm):.1f} |"
        )

    # vs frozen greedy
    lines += [
        "",
        "## vs frozen greedy @1k (arms.json `b1k_greedy_*`)",
        "",
        "| arm | tie | solved | Δ vs greedy | notes |",
        "|---|---:|---:|---:|---|",
    ]
    for arm in ("length", "s20_mk2"):
        for tie in TIES:
            s = summaries[(arm, tie)]["solved"]
            lines.append(
                f"| `{arm}` | {tie:+d} | {s}/60 | {s-g1:+d} | "
                f"{'same-engine length control' if arm=='length' else 'L+20S+2MK'} |"
            )
    lines += [
        "",
        "Cap note: frozen greedy columns are historically **mrl 24**; this scout "
        "uses **mrl 48**. Same-engine `length tie=+1` is the clean control for "
        "the flip; greedy is the published baseline reference.",
        "",
        "## Per-bin solves",
        "",
        "| bin | greedy@1k | length + | length − | s20_mk2 + | s20_mk2 − |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for binn in range(10):
        pids = [r["pres_id"] for r in rows if r["bin"] == binn]
        g = sum(1 for pid in pids if arms_rows[pid]["b1k_greedy_solved"])
        cells = [str(g)]
        for arm in ("length", "s20_mk2"):
            for tie in TIES:
                cells.append(str(sum(
                    1 for pid in pids if by[(arm, tie)][pid]["solved"])))
        lines.append(f"| {binn} | " + " | ".join(f"{c}/6" for c in cells) + " |")

    lines += [
        "",
        "## Verdict",
        "",
    ]
    # auto verdict
    s_p = summaries[("s20_mk2", 1)]["solved"]
    s_m = summaries[("s20_mk2", -1)]["solved"]
    l_p = summaries[("length", 1)]["solved"]
    l_m = summaries[("length", -1)]["solved"]
    if s_m > s_p or l_m > l_p:
        lines.append(
            f"`tie=−1` gains solves on at least one arm "
            f"(length {l_p}→{l_m}, s20_mk2 {s_p}→{s_m}). Check path inflation "
            "on the joint subset before promoting.")
    elif s_m < s_p or l_m < l_p:
        lines.append(
            f"`tie=−1` **loses or ties** on solves "
            f"(length {l_p}→{l_m}, s20_mk2 {s_p}→{s_m}). "
            "Shipped `+depth` stays. Matches EXP-24's reading on richer orderings.")
    else:
        lines.append(
            f"`tie=−1` is **solve-inert** vs `+depth` "
            f"(length {l_p}, s20_mk2 {s_p}). Compare path/nodes on the joint "
            "subset — if paths inflate without node wins, do not flip.")
    lines += [
        "",
        "Row table: `per_row.csv`.",
        "",
    ]
    with open(RESULTS, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines), flush=True)
    print(f"[write] {RESULTS}", flush=True)


if __name__ == "__main__":
    main()
