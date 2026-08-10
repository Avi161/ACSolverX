"""Aut-disjoint S+K+MK weight tune @ budget 1k (no xyimb).

Select on ``splits_ac1m_hard_aut.json`` train (120 Aut-orbits).
One holdout read on 60 Aut-disjoint orbits AFTER ranking on train.
Zero Aut overlap; prior s_grid / scale10k scout orbits excluded from both.

Grid: 336 (S,K,MK) cells + length. Same grids as scout_skmk_weight_tune.

    python3 -m experiments.heuristic_search.runners.scout_skmk_aut_tune
"""
from __future__ import annotations

import csv
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
OUT_DIR = os.path.join(ROOT, "results", "heuristic_search", "skmk_aut_tune")
JSONL = os.path.join(OUT_DIR, "runs.jsonl")
RESULTS = os.path.join(OUT_DIR, "RESULTS.md")
CSV = os.path.join(OUT_DIR, "arm_ranking_train.csv")
HOLDOUT_CSV = os.path.join(OUT_DIR, "arm_ranking_holdout.csv")
SPLIT = os.path.join(ROOT, "results", "heuristic_search", "splits",
                     "splits_ac1m_hard_aut.json")
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
            continue
        arms.append((_tag(s, k, mk), _cfg(s, k, mk), s, k, mk))
    return arms


def _iso():
    return datetime.now(timezone.utc).isoformat()


def _append(row):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(JSONL, "a") as f:
        f.write(json.dumps(row) + "\n")
        f.flush()
        os.fsync(f.fileno())


def _done(keys):
    s = set()
    if not os.path.exists(JSONL):
        return s
    for line in open(JSONL):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        s.add(tuple(r.get(k) for k in keys))
    return s


def _worker_job(job):
    """Spawn-worker entry: one (arm, presentation) search via hcompact (numba)."""
    (half_name, arm, cfg, s, k, mk, rec) = job
    res = greedy_search_hcompact(
        rec["r1"], rec["r2"], BUDGET, max_relator_length=CAP, config=cfg,
        reserve_states=RESERVE)
    return {
        "half": half_name, "arm": arm,
        "S": s, "K": k, "MK": mk,
        "idx": rec["idx"], "L": rec["L"],
        "aut_rep_r1": rec.get("aut_rep_r1"),
        "aut_rep_r2": rec.get("aut_rep_r2"),
        "budget": BUDGET, "cap": CAP,
        "solved": bool(res["solved"]),
        "nodes": int(res["nodes_explored"]),
        "solved_at": int(res["nodes_explored"]) if res["solved"] else None,
        "ts": _iso(),
    }


def _n_workers():
    # HIGH_SPEEDUP: all cores at budget 1k (hcompact ~tens of MB/search).
    return max(1, os.cpu_count() or 1)


def run_half(rows, half_name, arms):
    """Resume-safe parallel grid: spawn pool, parent-only jsonl writes."""
    import concurrent.futures
    import multiprocessing as mp

    done = _done(("half", "arm", "idx"))
    jobs = []
    for rec in rows:
        for arm, cfg, s, k, mk in arms:
            if (half_name, arm, rec["idx"]) in done:
                continue
            jobs.append((half_name, arm, cfg, s, k, mk, rec))

    nw = _n_workers()
    print(f"[aut-tune] {half_name}: {len(rows)}×{len(arms)} "
          f"todo={len(jobs)} workers={nw} engine=hcompact", flush=True)
    if not jobs:
        return 0

    # Warm in parent so fork workers inherit compiled numba kernels.
    greedy_search_hcompact("X", "Y", 50, max_relator_length=CAP,
                           config=_cfg(12, 0, 0), reserve_states=5000)

    n_new = 0
    t0 = time.time()
    # fork (Linux): inherits JIT'd hcompact; spawn re-compiles per worker.
    ctx = mp.get_context("fork")
    with concurrent.futures.ProcessPoolExecutor(
            max_workers=nw, mp_context=ctx) as ex:
        # chunk submissions to bound memory of futures
        CHUNK = 256
        for i0 in range(0, len(jobs), CHUNK):
            batch = jobs[i0:i0 + CHUNK]
            futs = [ex.submit(_worker_job, j) for j in batch]
            for fut in concurrent.futures.as_completed(futs):
                row = fut.result()
                _append(row)
                n_new += 1
                if n_new % 200 == 0 or n_new == len(jobs):
                    rate = n_new / max(time.time() - t0, 1e-9)
                    print(f"  [{half_name}] +{n_new}/{len(jobs)} "
                          f"{rate:.2f}/s last={row['arm']} "
                          f"sol={row['solved']}", flush=True)
    print(f"[aut-tune] {half_name} new={n_new}", flush=True)
    return n_new


def _rank(rows, half):
    by = defaultdict(list)
    for r in rows:
        if r["half"] == half:
            by[r["arm"]].append(r)
    ranked = []
    for arm, rs in by.items():
        sol = [r for r in rs if r["solved"]]
        mean_n = (sum(r["nodes"] for r in sol) / len(sol)) if sol else None
        ranked.append({
            "arm": arm, "S": rs[0]["S"], "K": rs[0]["K"], "MK": rs[0]["MK"],
            "n": len(rs), "solved": len(sol),
            "mean_nodes_solved": mean_n,
        })
    ranked.sort(key=lambda r: (r["solved"], -(r["mean_nodes_solved"] or 1e9)),
                reverse=True)
    return ranked


def write_results(winner_arm=None):
    rows = [json.loads(l) for l in open(JSONL)]
    train = _rank(rows, "train")
    hold = _rank(rows, "holdout")
    split = json.load(open(SPLIT))
    length_tr = next((r for r in train if r["arm"] == "length"), None)
    length_ho = next((r for r in hold if r["arm"] == "length"), None)

    lines = [
        "# Aut-disjoint S+K+MK weight tune @ budget 1,000",
        "",
        f"Updated `{_iso()}`",
        "",
        f"Split: [`splits_ac1m_hard_aut.json`](../splits/splits_ac1m_hard_aut.json) "
        f"— train={split['n_train']} holdout={split['n_holdout']} Aut-orbits, "
        f"zero Aut overlap; prior s_grid/scale10k scout orbits excluded.",
        "",
        f"Grid: |S|={len(S_GRID)} × |K|={len(K_GRID)} × |MK|={len(MK_GRID)} "
        f"= {len(S_GRID)*len(K_GRID)*len(MK_GRID)} (+ **length baseline**). "
        f"**No xyimb.**",
        "",
        f"**selected_on** = train · **evaluated_on** = holdout (one read).",
        "",
        "Every arm is scored against the **length-only greedy baseline** "
        "(`arm=length`). Without that column a lift is undefined.",
        "",
        "Note: this pool is *defined* as length-failures at budget 1k, so "
        "length is expected to be ~0/N here — useful for ranking treatments, "
        "but the production comparison is Colab @200k where baseline can move.",
        "",
    ]
    if train:
        b = train[0]
        d_base = (
            f" vs length **{length_tr['solved']}/{length_tr['n']}** "
            f"(Δ=+{b['solved'] - length_tr['solved']})"
            if length_tr else "")
        lines += [
            f"## Winner on TRAIN: `{b['arm']}`",
            "",
            f"S={b['S']:g}, K={b['K']:g}, MK={b['MK']:g} → "
            f"**{b['solved']}/{b['n']}**"
            + (f" (mean nodes {b['mean_nodes_solved']:.0f})"
               if b["mean_nodes_solved"] else "")
            + d_base,
            "",
            "### Train top 30 (Δ vs length)",
            "",
            "| rank | arm | S | K | MK | solved | Δ vs length | mean nodes |",
            "|---:|---|---:|---:|---:|---:|---:|---:|",
        ]
        base_n = length_tr["solved"] if length_tr else 0
        for i, r in enumerate(train[:30], 1):
            mn = f"{r['mean_nodes_solved']:.0f}" if r["mean_nodes_solved"] else "—"
            dlt = r["solved"] - base_n
            lines.append(
                f"| {i} | `{r['arm']}` | {r['S']:g} | {r['K']:g} | "
                f"{r['MK']:g} | **{r['solved']}/{r['n']}** | "
                f"{dlt:+d} | {mn} |")
        lines.append("")

        def fam(name, pred):
            xs = [r for r in train if pred(r)]
            if xs:
                r = xs[0]
                dlt = r["solved"] - base_n
                lines.append(
                    f"- **{name}:** `{r['arm']}` → {r['solved']}/{r['n']} "
                    f"(Δ={dlt:+d} vs length; "
                    f"S={r['S']:g}, K={r['K']:g}, MK={r['MK']:g})")

        lines.append("### Train best by family (each vs length)")
        lines.append("")
        fam("length", lambda r: r["arm"] == "length")
        fam("pure S", lambda r: r["S"] > 0 and r["K"] == 0 and r["MK"] == 0)
        fam("pure K", lambda r: r["S"] == 0 and r["K"] > 0 and r["MK"] == 0)
        fam("pure MK", lambda r: r["S"] == 0 and r["K"] == 0 and r["MK"] > 0)
        fam("S+K", lambda r: r["S"] > 0 and r["K"] > 0 and r["MK"] == 0)
        fam("S+MK", lambda r: r["S"] > 0 and r["K"] == 0 and r["MK"] > 0)
        fam("K+MK", lambda r: r["S"] == 0 and r["K"] > 0 and r["MK"] > 0)
        fam("S+K+MK", lambda r: r["S"] > 0 and r["K"] > 0 and r["MK"] > 0)
        lines.append("")

        with open(CSV, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=[
                "rank", "arm", "S", "K", "MK", "solved", "n",
                "delta_vs_length", "mean_nodes_solved",
                "length_solved", "length_n"])
            w.writeheader()
            for i, r in enumerate(train, 1):
                w.writerow({
                    "rank": i, "arm": r["arm"], "S": r["S"], "K": r["K"],
                    "MK": r["MK"], "solved": r["solved"], "n": r["n"],
                    "delta_vs_length": r["solved"] - base_n,
                    "mean_nodes_solved": r["mean_nodes_solved"],
                    "length_solved": base_n,
                    "length_n": length_tr["n"] if length_tr else None,
                })

    if hold:
        base_h = length_ho["solved"] if length_ho else 0
        lines += [
            "## HOLDOUT (Aut-disjoint — one read; always vs length)",
            "",
            "| rank | arm | S | K | MK | solved | Δ vs length | mean nodes |",
            "|---:|---|---:|---:|---:|---:|---:|---:|",
        ]
        for i, r in enumerate(hold[:30], 1):
            mn = f"{r['mean_nodes_solved']:.0f}" if r["mean_nodes_solved"] else "—"
            mark = " ← train winner" if winner_arm and r["arm"] == winner_arm else ""
            dlt = r["solved"] - base_h
            lines.append(
                f"| {i} | `{r['arm']}` | {r['S']:g} | {r['K']:g} | "
                f"{r['MK']:g} | **{r['solved']}/{r['n']}** | "
                f"{dlt:+d} | {mn} |{mark}")
        lines.append("")
        with open(HOLDOUT_CSV, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=[
                "rank", "arm", "S", "K", "MK", "solved", "n",
                "delta_vs_length", "mean_nodes_solved",
                "length_solved", "length_n"])
            w.writeheader()
            for i, r in enumerate(hold, 1):
                w.writerow({
                    "rank": i, "arm": r["arm"], "S": r["S"], "K": r["K"],
                    "MK": r["MK"], "solved": r["solved"], "n": r["n"],
                    "delta_vs_length": r["solved"] - base_h,
                    "mean_nodes_solved": r["mean_nodes_solved"],
                    "length_solved": base_h,
                    "length_n": length_ho["n"] if length_ho else None,
                })
        if winner_arm:
            wr = next((r for r in hold if r["arm"] == winner_arm), None)
            if wr and length_ho:
                lines += [
                    f"**Train winner on holdout:** `{winner_arm}` → "
                    f"**{wr['solved']}/{wr['n']}** vs length "
                    f"**{length_ho['solved']}/{length_ho['n']}** "
                    f"(Δ={wr['solved'] - length_ho['solved']:+d}).",
                    "",
                ]

    open(RESULTS, "w").write("\n".join(lines) + "\n")
    print(f"wrote {RESULTS}", flush=True)
    return train[0]["arm"] if train else None


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    split = json.load(open(SPLIT))
    train_rows = split["train_rows"]
    hold_rows = split["holdout_rows"]
    arms = all_arms()
    print(f"[aut-tune] {len(arms)} arms · train={len(train_rows)} "
          f"holdout={len(hold_rows)} · Aut-disjoint", flush=True)
    greedy_search_hcompact("X", "Y", 50, max_relator_length=CAP,
                           config=_cfg(12, 0, 0), reserve_states=5000)

    run_half(train_rows, "train", arms)
    winner = write_results(None)
    print(f"[aut-tune] train winner = {winner}", flush=True)

    # Holdout: top train arms + best-of-family + length (not all 336 — Aut-disjoint
    # one-read on the selection shortlist). Full 336 ranking lives on TRAIN.
    train_rank = _rank([json.loads(l) for l in open(JSONL)], "train")
    hold_arms_names = []
    for r in train_rank[:40]:
        hold_arms_names.append(r["arm"])
    for r in train_rank:
        if r["arm"] == "length" or (
                r["S"] > 0 and r["K"] > 0 and r["MK"] > 0) or (
                r["S"] > 0 and r["K"] == 0 and r["MK"] == 0) or (
                r["S"] > 0 and r["K"] == 0 and r["MK"] > 0) or (
                r["S"] > 0 and r["K"] > 0 and r["MK"] == 0):
            if r["arm"] not in hold_arms_names:
                hold_arms_names.append(r["arm"])
        # one of each family already covered by scanning sorted list
    # ensure family winners
    for pred in [
        lambda r: r["S"] > 0 and r["K"] == 0 and r["MK"] == 0,
        lambda r: r["S"] > 0 and r["K"] > 0 and r["MK"] == 0,
        lambda r: r["S"] > 0 and r["K"] == 0 and r["MK"] > 0,
        lambda r: r["S"] > 0 and r["K"] > 0 and r["MK"] > 0,
        lambda r: r["S"] == 0 and r["K"] > 0 and r["MK"] > 0,
        lambda r: r["arm"] == "length",
    ]:
        for r in train_rank:
            if pred(r) and r["arm"] not in hold_arms_names:
                hold_arms_names.append(r["arm"])
                break
    hold_arms = [a for a in arms if a[0] in set(hold_arms_names)]
    print(f"[aut-tune] holdout evaluating {len(hold_arms)} shortlisted arms",
          flush=True)
    run_half(hold_rows, "holdout", hold_arms)
    write_results(winner)
    print("[aut-tune] DONE", flush=True)


if __name__ == "__main__":
    main()
