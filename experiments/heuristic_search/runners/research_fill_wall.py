"""Fill remaining wall with more ≤10k experiments (do not idle).

1) Expand fresh_hard to +120 never-s_grid rows × {length,s12,s20,s28,recommended}
2) Fine S-weight grid on 40 fresh-hard idxs: w∈{10,12,14,16,18,20,24,28}
3) Keep writing RESULTS until scale10k wall_end.

    python3 -m experiments.heuristic_search.runners.research_fill_wall
"""
from __future__ import annotations

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
from experiments.heuristic_search.core.hsolve import RECOMMENDED  # noqa: E402

ROOT = _d
OUT_DIR = os.path.join(ROOT, "results", "heuristic_search", "fill_wall")
JSONL = os.path.join(OUT_DIR, "runs.jsonl")
RESULTS = os.path.join(OUT_DIR, "RESULTS.md")
SCREEN = os.path.join(ROOT, "results", "heuristic_search", "campaign_12h",
                      "screen_length_ac1m.jsonl")
S_GRID = os.path.join(ROOT, "results", "heuristic_search", "campaign_12h",
                      "s_grid_hard.jsonl")
USED = os.path.join(ROOT, "results", "heuristic_search", "scale10k",
                    "slice_fresh_hard.json")
SCALE_STATE = os.path.join(ROOT, "results", "heuristic_search", "scale10k",
                           "state.json")
BUDGET = 10_000
CAP = 48
RESERVE = 120 * BUDGET

ARMS = {
    "length": None,
    "s12": {"segments": [{"upto": None, "w": {"L": 1.0, "S": 12.0}}]},
    "s20": {"segments": [{"upto": None, "w": {"L": 1.0, "S": 20.0}}]},
    "s28": {"segments": [{"upto": None, "w": {"L": 1.0, "S": 28.0}}]},
    "recommended": RECOMMENDED,
}
WEIGHTS = (10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 24.0, 28.0)


def _iso():
    return datetime.now(timezone.utc).isoformat()


def _rem():
    end = datetime.fromisoformat(json.load(open(SCALE_STATE))["wall_end"])
    return (end - datetime.now(timezone.utc)).total_seconds()


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
        r = json.loads(line)
        s.add(tuple(r.get(k) for k in keys))
    return s


def _search(r1, r2, cfg):
    t0 = time.perf_counter()
    res = greedy_search_hcompact(
        r1, r2, BUDGET, max_relator_length=CAP, config=cfg,
        reserve_states=RESERVE)
    dt = time.perf_counter() - t0
    out = {
        "solved": bool(res["solved"]),
        "nodes": int(res["nodes_explored"]),
        "solved_at": int(res["nodes_explored"]) if res["solved"] else None,
        "min_relator_length": res["min_relator_length"],
        "secs": round(dt, 3),
        "pops_s": round(res["nodes_explored"] / max(dt, 1e-9), 1),
        "budget": BUDGET,
        "cap": CAP,
    }
    for c in (1000, 2000, 5000, 10000):
        out[f"solved_le_{c}"] = bool(
            out["solved_at"] is not None and out["solved_at"] <= c)
    return out


def _fresh_pool(n=120, skip_first=60):
    sgrid = {json.loads(l)["idx"] for l in open(S_GRID)}
    used = {r["idx"] for r in json.load(open(USED))["rows"]}
    hard = []
    for line in open(SCREEN):
        r = json.loads(line)
        if (not r["solved"]) and r["idx"] not in sgrid and r["idx"] not in used:
            hard.append(r)
    hard.sort(key=lambda r: r["idx"])
    return hard[skip_first:skip_first + n] if skip_first else hard[:n]


def phase_expand_hard():
    rows = _fresh_pool(120, skip_first=0)
    # skip idxs already in scale10k fresh slice
    used = {r["idx"] for r in json.load(open(USED))["rows"]}
    rows = [r for r in rows if r["idx"] not in used][:120]
    done = _done(("phase", "arm", "idx"))
    n = 0
    print(f"[expand] {len(rows)} fresh-hard2 rows", flush=True)
    for rec in rows:
        for arm, cfg in ARMS.items():
            if _rem() < 90:
                return n
            key = ("expand_hard", arm, rec["idx"])
            if key in done:
                continue
            res = _search(rec["r1"], rec["r2"], cfg)
            _append({"phase": "expand_hard", "arm": arm, "idx": rec["idx"],
                     "L": rec["L"], "r1": rec["r1"], "r2": rec["r2"],
                     "ts": _iso(), **res})
            done.add(key)
            n += 1
            if n % 15 == 0:
                print(f"  [expand] +{n} {arm}/idx={rec['idx']} "
                      f"solved={res['solved']}", flush=True)
    return n


def phase_s_grid():
    rows = _fresh_pool(40, skip_first=0)
    used = {r["idx"] for r in json.load(open(USED))["rows"]}
    # prefer unused; if short, use scale10k fresh slice itself for grid
    pool = [r for r in rows if r["idx"] not in used][:40]
    if len(pool) < 40:
        pool = json.load(open(USED))["rows"][:40]
        pool = [{"idx": r["idx"], "r1": r["r1"], "r2": r["r2"], "L": r["L"]}
                for r in pool]
    done = _done(("phase", "w", "idx"))
    n = 0
    print(f"[sgrid] {len(pool)} rows × {len(WEIGHTS)} weights", flush=True)
    for rec in pool:
        for w in WEIGHTS:
            if _rem() < 90:
                return n
            key = ("s_grid", w, rec["idx"])
            if key in done:
                continue
            cfg = {"segments": [{"upto": None, "w": {"L": 1.0, "S": float(w)}}]}
            res = _search(rec["r1"], rec["r2"], cfg)
            half = "even" if int(rec["idx"]) % 2 == 0 else "odd"
            _append({"phase": "s_grid", "w": w, "idx": rec["idx"],
                     "half": half, "L": rec.get("L"), "ts": _iso(), **res})
            done.add(key)
            n += 1
            if n % 20 == 0:
                print(f"  [sgrid] +{n} w={w} idx={rec['idx']} "
                      f"solved={res['solved']}", flush=True)
    return n


def write_results():
    if not os.path.exists(JSONL):
        return
    rows = [json.loads(l) for l in open(JSONL)]
    lines = [
        "# fill_wall RESULTS",
        "",
        f"Updated `{_iso()}` remain={_rem()/3600:.2f}h rows={len(rows)}",
        "",
    ]
    exp = [r for r in rows if r["phase"] == "expand_hard"]
    if exp:
        lines += ["## expand_hard @10k", "",
                  "| arm | @1k | @5k | @10k | n |",
                  "|---|---:|---:|---:|---:|"]
        by = defaultdict(list)
        for r in exp:
            by[r["arm"]].append(r)
        for arm in ("length", "s12", "s20", "s28", "recommended"):
            rs = by.get(arm, [])
            if not rs:
                continue
            def c(k):
                return sum(1 for r in rs if r.get(k))
            lines.append(
                f"| `{arm}` | {c('solved_le_1000')} | {c('solved_le_5000')} | "
                f"{c('solved_le_10000')} | {len(rs)} |")
        lines.append("")
    grid = [r for r in rows if r["phase"] == "s_grid"]
    if grid:
        lines += ["## s_grid @10k (select=even / holdout=odd)", "",
                  "| w | even solved | odd solved | all |",
                  "|---:|---:|---:|---:|"]
        byw = defaultdict(list)
        for r in grid:
            byw[r["w"]].append(r)
        for w in sorted(byw):
            rs = byw[w]
            even = [r for r in rs if r["half"] == "even"]
            odd = [r for r in rs if r["half"] == "odd"]
            lines.append(
                f"| {w:g} | {sum(r['solved'] for r in even)}/{len(even)} | "
                f"{sum(r['solved'] for r in odd)}/{len(odd)} | "
                f"{sum(r['solved'] for r in rs)}/{len(rs)} |")
        lines.append("")
    open(RESULTS, "w").write("\n".join(lines) + "\n")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"[fill] remain={_rem()/3600:.2f}h", flush=True)
    greedy_search_hcompact("X", "Y", 50, max_relator_length=48,
                           config=ARMS["s20"], reserve_states=5000)
    while _rem() > 120:
        n1 = phase_expand_hard()
        n2 = phase_s_grid()
        write_results()
        print(f"[fill] cycle new={n1+n2}", flush=True)
        if n1 + n2 == 0:
            time.sleep(min(120, max(0, _rem() - 60)))
    write_results()
    print("[fill] wall near — stop", flush=True)


if __name__ == "__main__":
    main()
