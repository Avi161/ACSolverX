"""10h mini-research for Colab handoff (≤10k nodes / ≤1h per search).

Advisor-REVISE'd plan (see results/heuristic_search/scale10k/PLAN.md):
  - NEW out dir (never campaign_12h/)
  - Outcome-unconditioned L-stratified AC1M headline slice (frozen idxs)
  - Fresh hard reach slice: length-hard rows NOT in s_grid's 800
  - Arms: length, s12, s20, recommended  (s24 dropped — s_grid sign test)
  - Cap 48 on AC1M; cap 64 on unsolved124
  - reserve_states ≈ 120 * budget
  - Prefix gate: solved_at≤1000 must match prior 1k rows where they exist
  - Anytime curves from one search to BUDGET via solved_at
  - Optional portfolio: 3 S-weights at B/3 vs s20 at B (matched total nodes)
  - Colab recommendation ONLY after WALL_END

User override for this task: node_budget up to 10_000 (still ≤1h wall/search).

    python3 -m experiments.heuristic_search.runners.research_scale10k
"""
from __future__ import annotations

import csv
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
from experiments.heuristic_search.core.hsolve import (  # noqa: E402
    RECOMMENDED, greedy_search_h,
)

ROOT = _d
OUT_DIR = os.path.join(ROOT, "results", "heuristic_search", "scale10k")
SCREEN = os.path.join(ROOT, "results", "heuristic_search", "campaign_12h",
                      "screen_length_ac1m.jsonl")
S_GRID = os.path.join(ROOT, "results", "heuristic_search", "campaign_12h",
                      "s_grid_hard.jsonl")
UNSOLVED_CSV = os.path.join(
    ROOT, "results", "equivalence_classes", "ms1190_tables",
    "unsolved_124_aca_classes.csv")
SLICE_L = os.path.join(OUT_DIR, "slice_l_stratified.json")
SLICE_HARD = os.path.join(OUT_DIR, "slice_fresh_hard.json")
MAIN_JSONL = os.path.join(OUT_DIR, "anytime_b10k.jsonl")
COST_JSONL = os.path.join(OUT_DIR, "cost_profile.jsonl")
PORT_JSONL = os.path.join(OUT_DIR, "portfolio_b10k.jsonl")
PREFIX_MD = os.path.join(OUT_DIR, "PREFIX_GATE.md")
RESULTS_MD = os.path.join(OUT_DIR, "RESULTS.md")
STATE = os.path.join(OUT_DIR, "state.json")

# Wall: 10h from first launch; overwritten if state already has wall_end.
WALL_HOURS = 10.0
BUDGET = 10_000
MAX_SECS_PER_SEARCH = 3600.0
RESERVE_MULT = 120
CHECKPOINTS = (1000, 2000, 5000, 10_000)

ARMS = {
    "length": None,
    "s12": {"segments": [{"upto": None, "w": {"L": 1.0, "S": 12.0}}]},
    "s20": {"segments": [{"upto": None, "w": {"L": 1.0, "S": 20.0}}]},
    "recommended": RECOMMENDED,
}


def _now():
    return datetime.now(timezone.utc)


def _iso(dt=None):
    return (dt or _now()).isoformat()


def _append(path, row):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(row) + "\n")
        f.flush()
        os.fsync(f.fileno())


def _load_done(path, keys):
    seen = set()
    if not os.path.exists(path):
        return seen
    with open(path) as f:
        for line in f:
            try:
                r = json.loads(line)
            except ValueError:
                continue
            seen.add(tuple(r[k] for k in keys))
    return seen


def _wall_end(state):
    return datetime.fromisoformat(state["wall_end"])


def _remaining_s(state):
    return (_wall_end(state) - _now()).total_seconds()


def _write_state(state):
    state["updated"] = _iso()
    state["remaining_h"] = max(0.0, _remaining_s(state) / 3600.0)
    with open(STATE, "w") as f:
        json.dump(state, f, indent=2)
        f.write("\n")


def _cfg(name):
    return ARMS[name]


def _search(r1, r2, budget, cfg, cap, t_deadline):
    """One search; abort if wall-clock for this call would exceed MAX or phase deadline."""
    reserve = RESERVE_MULT * budget
    t0 = time.perf_counter()
    last = {"n": 0, "t": t0}

    def progress(n):
        now = time.perf_counter()
        if now - t0 > MAX_SECS_PER_SEARCH:
            raise TimeoutError(f"search exceeded {MAX_SECS_PER_SEARCH}s")
        if now > t_deadline:
            raise TimeoutError("phase/wall deadline")
        last["n"], last["t"] = n, now

    res = greedy_search_hcompact(
        r1, r2, budget, max_relator_length=cap, config=cfg,
        progress=progress, reserve_states=reserve)
    dt = time.perf_counter() - t0
    pops_s = res["nodes_explored"] / max(dt, 1e-9)
    out = {
        "solved": bool(res["solved"]),
        "nodes": int(res["nodes_explored"]),
        "solved_at": int(res["nodes_explored"]) if res["solved"] else None,
        "path_length": res["path_length"],
        "min_relator_length": res["min_relator_length"],
        "secs": round(dt, 3),
        "pops_s": round(pops_s, 1),
        "budget": budget,
        "cap": cap,
    }
    if res["solved"]:
        # Certificate via keep_path replay (hcompact path is empty).
        rec = greedy_search_h(
            r1, r2, budget, max_relator_length=cap, config=cfg, keep_path=True)
        assert (rec["solved"], rec["nodes_explored"], rec["path_length"]) == (
            True, res["nodes_explored"], res["path_length"]), "recovery diverge"
        out["path_moves"] = rec["path_moves"]
    else:
        out["path_moves"] = None
    if out["nodes"] > budget:
        raise RuntimeError("budget overrun")
    return out


def freeze_slices():
    """Freeze evaluation index lists BEFORE any scoring (held-out contract)."""
    os.makedirs(OUT_DIR, exist_ok=True)
    if os.path.exists(SLICE_L) and os.path.exists(SLICE_HARD):
        return
    screen = [json.loads(l) for l in open(SCREEN)]
    sgrid_idx = {json.loads(l)["idx"] for l in open(S_GRID)}

    # L-stratified unconditioned: 8 rows from each of 10 L-bins → 80.
    by_L = defaultdict(list)
    for r in screen:
        by_L[int(r["L"])].append(r)
    # pick the 10 most populous L values
    top_Ls = sorted(by_L.keys(), key=lambda L: -len(by_L[L]))[:10]
    stratified = []
    for L in sorted(top_Ls):
        pool = sorted(by_L[L], key=lambda r: r["idx"])
        # take evenly spaced 8
        n = len(pool)
        picks = [pool[int(i * (n - 1) / 7)] for i in range(8)] if n >= 8 else pool
        for r in picks:
            stratified.append({
                "idx": r["idx"], "r1": r["r1"], "r2": r["r2"], "L": r["L"],
                "length_solved_1k": bool(r["solved"]),
                "length_nodes_1k": r.get("nodes"),
            })
    # dedupe preserving order
    seen = set()
    strat_u = []
    for r in stratified:
        if r["idx"] in seen:
            continue
        seen.add(r["idx"])
        strat_u.append(r)

    fresh_hard = sorted(
        (r for r in screen if (not r["solved"]) and r["idx"] not in sgrid_idx),
        key=lambda r: r["idx"],
    )[:60]
    hard_slice = [{
        "idx": r["idx"], "r1": r["r1"], "r2": r["r2"], "L": r["L"],
        "length_solved_1k": False, "length_nodes_1k": r.get("nodes"),
    } for r in fresh_hard]

    with open(SLICE_L, "w") as f:
        json.dump({
            "name": "l_stratified_unconditioned",
            "n": len(strat_u),
            "rule": "8 evenly-spaced idxs from each of 10 most populous L values "
                    "in screen_length_ac1m (outcome-unconditioned)",
            "selected_on": "L histogram of screen only; no arm outcomes",
            "rows": strat_u,
        }, f, indent=2)
        f.write("\n")
    with open(SLICE_HARD, "w") as f:
        json.dump({
            "name": "fresh_hard_reach",
            "n": len(hard_slice),
            "rule": "first 60 length-hard idxs NOT in s_grid_hard's 800 "
                    "(never used for s20/s12 selection)",
            "selected_on": "screen length-unsolved ∧ idx ∉ s_grid; freeze before score",
            "evaluated_on": "this slice only — do not claim s_grid holdout",
            "rows": hard_slice,
        }, f, indent=2)
        f.write("\n")
    print(f"[freeze] L-stratified={len(strat_u)} fresh_hard={len(hard_slice)}",
          flush=True)


def load_unsolved124():
    with open(UNSOLVED_CSV) as f:
        return [{"name": r["aca_id"], "r1": r["r1"], "r2": r["r2"]}
                for r in csv.DictReader(f)]


def phase_cost(state):
    """Pops/s at 1k/5k/10k on 4 fixed presentations; reserve sized."""
    done = _load_done(COST_JSONL, ("arm", "name", "budget"))
    # 2 from L-slice, 2 from fresh hard
    L = json.load(open(SLICE_L))["rows"][:2]
    H = json.load(open(SLICE_HARD))["rows"][:2]
    probes = [("L", r) for r in L] + [("H", r) for r in H]
    arms = ("length", "s20", "recommended")
    budgets = (1000, 5000, 10_000)
    t_dead = time.time() + min(_remaining_s(state) - 60, 3600)
    n_new = 0
    for tag, rec in probes:
        name = f"{tag}{rec['idx']}"
        for arm in arms:
            for b in budgets:
                if _remaining_s(state) < 120:
                    return n_new
                key = (arm, name, b)
                if key in done:
                    continue
                try:
                    res = _search(rec["r1"], rec["r2"], b, _cfg(arm), 48, t_dead)
                except TimeoutError as e:
                    _append(COST_JSONL, {
                        "arm": arm, "name": name, "idx": rec["idx"], "budget": b,
                        "cap": 48, "error": str(e), "ts": _iso()})
                    return n_new
                row = {"arm": arm, "name": name, "idx": rec["idx"], "slice": tag,
                       "ts": _iso(), **res}
                _append(COST_JSONL, row)
                done.add(key)
                n_new += 1
                print(f"  [cost] {arm}/{name}/b{b} pops_s={res['pops_s']} "
                      f"solved={res['solved']}", flush=True)
    return n_new


def phase_anytime(state, slice_path, slice_key, cap, arm_names, limit=None):
    meta = json.load(open(slice_path))
    rows = meta["rows"]
    if limit:
        rows = rows[:limit]
    done = _load_done(MAIN_JSONL, ("slice", "arm", "idx"))
    t_dead = time.time() + _remaining_s(state) - 60
    n_new = 0
    for rec in rows:
        for arm in arm_names:
            if _remaining_s(state) < 90:
                return n_new
            key = (slice_key, arm, rec["idx"])
            if key in done:
                continue
            try:
                res = _search(rec["r1"], rec["r2"], BUDGET, _cfg(arm), cap, t_dead)
            except TimeoutError as e:
                _append(MAIN_JSONL, {
                    "slice": slice_key, "arm": arm, "idx": rec["idx"],
                    "error": str(e), "ts": _iso(), "budget": BUDGET, "cap": cap})
                return n_new
            # checkpoint curve
            curve = {}
            for c in CHECKPOINTS:
                if res["solved_at"] is not None and res["solved_at"] <= c:
                    curve[f"solved_le_{c}"] = True
                else:
                    curve[f"solved_le_{c}"] = False
            row = {
                "slice": slice_key, "arm": arm, "idx": rec["idx"],
                "r1": rec["r1"], "r2": rec["r2"], "L": rec.get("L"),
                "length_solved_1k": rec.get("length_solved_1k"),
                "ts": _iso(), **res, **curve,
            }
            _append(MAIN_JSONL, row)
            done.add(key)
            n_new += 1
            if n_new % 5 == 0 or res["solved"]:
                print(f"  [any] {slice_key}/{arm}/idx={rec['idx']} "
                      f"solved={res['solved']} nodes={res['nodes']} "
                      f"pops_s={res['pops_s']}", flush=True)
    return n_new


def phase_unsolved124(state):
    rows = load_unsolved124()
    done = _load_done(MAIN_JSONL, ("slice", "arm", "name"))
    t_dead = time.time() + _remaining_s(state) - 60
    n_new = 0
    # Prefer s20 + length first (ranking); recommended third; s12 if time
    order = ("length", "s20", "recommended", "s12")
    for rec in rows:
        for arm in order:
            if _remaining_s(state) < 90:
                return n_new
            key = ("unsolved124", arm, rec["name"])
            if key in done:
                continue
            try:
                res = _search(rec["r1"], rec["r2"], BUDGET, _cfg(arm), 64, t_dead)
            except TimeoutError as e:
                _append(MAIN_JSONL, {
                    "slice": "unsolved124", "arm": arm, "name": rec["name"],
                    "idx": rec["name"], "error": str(e), "ts": _iso(),
                    "budget": BUDGET, "cap": 64})
                return n_new
            curve = {f"solved_le_{c}": bool(
                res["solved_at"] is not None and res["solved_at"] <= c)
                for c in CHECKPOINTS}
            row = {
                "slice": "unsolved124", "arm": arm, "name": rec["name"],
                "idx": rec["name"], "r1": rec["r1"], "r2": rec["r2"],
                "ts": _iso(), **res, **curve,
            }
            if res["solved"]:
                print(f"  *** SOLVE unsolved124/{arm}/{rec['name']} "
                      f"at {res['solved_at']}", flush=True)
            _append(MAIN_JSONL, row)
            done.add(key)
            n_new += 1
            if n_new % 10 == 0:
                print(f"  [u124] +{n_new} last={arm}/{rec['name']} "
                      f"solved={res['solved']} pops_s={res['pops_s']}",
                      flush=True)
    return n_new


def phase_portfolio(state):
    """Matched-total-nodes: {s12,s20,s32} at B/3 vs s20 at B on fresh hard 30."""
    rows = json.load(open(SLICE_HARD))["rows"][:30]
    done = _load_done(PORT_JSONL, ("mode", "idx"))
    t_dead = time.time() + _remaining_s(state) - 60
    b_full = BUDGET
    b_part = BUDGET // 3
    weights = (12.0, 20.0, 32.0)
    n_new = 0
    for rec in rows:
        if _remaining_s(state) < 120:
            return n_new
        if ("single_s20", rec["idx"]) not in done:
            try:
                res = _search(rec["r1"], rec["r2"], b_full, _cfg("s20"), 48, t_dead)
            except TimeoutError:
                return n_new
            _append(PORT_JSONL, {
                "mode": "single_s20", "idx": rec["idx"], "w": 20.0,
                "budget_each": b_full, "ts": _iso(), **res})
            done.add(("single_s20", rec["idx"]))
            n_new += 1
        if ("portfolio3", rec["idx"]) not in done:
            any_sol = False
            best_at = None
            parts = []
            try:
                for w in weights:
                    cfg = {"segments": [{"upto": None, "w": {"L": 1.0, "S": w}}]}
                    res = _search(rec["r1"], rec["r2"], b_part, cfg, 48, t_dead)
                    parts.append({"w": w, **{k: res[k] for k in
                        ("solved", "nodes", "solved_at", "secs", "pops_s")}})
                    if res["solved"]:
                        any_sol = True
                        # total nodes across tries ≈ sum; oracle earliest weight
                        if best_at is None:
                            best_at = res["solved_at"]
            except TimeoutError:
                return n_new
            _append(PORT_JSONL, {
                "mode": "portfolio3", "idx": rec["idx"],
                "budget_each": b_part, "budget_total": b_part * 3,
                "solved": any_sol, "solved_at_oracle": best_at,
                "parts": parts, "ts": _iso()})
            done.add(("portfolio3", rec["idx"]))
            n_new += 1
            print(f"  [port] idx={rec['idx']} single={done} "
                  f"port_solved={any_sol}", flush=True)
    return n_new


def write_results(state):
    lines = [
        "# scale10k mini-research — RESULTS",
        "",
        f"Updated: `{_iso()}` · wall end `{state['wall_end']}` · "
        f"remaining `{state['remaining_h']:.2f} h`",
        "",
        "Budgets ≤10,000; ≤1h/search; advisor-REVISE'd slices. "
        "**Colab handoff only after wall.**",
        "",
    ]
    if os.path.exists(MAIN_JSONL):
        data = [json.loads(l) for l in open(MAIN_JSONL) if "error" not in json.loads(l)]
        # re-parse safely
        data = []
        for l in open(MAIN_JSONL):
            r = json.loads(l)
            if "error" in r:
                continue
            data.append(r)
        by = defaultdict(lambda: defaultdict(list))
        for r in data:
            by[r["slice"]][r["arm"]].append(r)
        for sl in sorted(by):
            lines += [f"## Slice `{sl}`", "",
                      "| arm | n | @1k | @2k | @5k | @10k | mean pops/s |",
                      "|---|---:|---:|---:|---:|---:|---:|"]
            for arm in ("length", "s12", "s20", "recommended"):
                rs = by[sl].get(arm, [])
                if not rs:
                    continue
                n = len(rs)
                def cnt(c):
                    return sum(1 for r in rs if r.get(f"solved_le_{c}"))
                mean_p = sum(r.get("pops_s", 0) for r in rs) / n
                lines.append(
                    f"| `{arm}` | {n} | {cnt(1000)} | {cnt(2000)} | "
                    f"{cnt(5000)} | {cnt(10000)} | {mean_p:.0f} |")
            lines.append("")
    if os.path.exists(COST_JSONL):
        lines += ["## Cost profile (local pops/s)", ""]
        for l in open(COST_JSONL):
            r = json.loads(l)
            if "error" in r:
                continue
            lines.append(
                f"- `{r['arm']}` `{r['name']}` b={r['budget']}: "
                f"{r.get('pops_s')} pops/s  solved={r.get('solved')}")
        lines.append("")
    if os.path.exists(PORT_JSONL):
        ports = [json.loads(l) for l in open(PORT_JSONL)]
        singles = [r for r in ports if r["mode"] == "single_s20"]
        ports3 = [r for r in ports if r["mode"] == "portfolio3"]
        lines += [
            "## Portfolio (matched total nodes, fresh hard)",
            "",
            f"- single s20 @10k: "
            f"{sum(1 for r in singles if r.get('solved'))}/{len(singles)}",
            f"- portfolio {{12,20,32}} @3333 each: "
            f"{sum(1 for r in ports3 if r.get('solved'))}/{len(ports3)} "
            f"(oracle best-of-3; runnable = first-hit order not claimed)",
            "",
        ]
    lines += [
        "## Method notes",
        "",
        "- Headline slice is L-stratified / outcome-unconditioned "
        f"([`slice_l_stratified.json`](slice_l_stratified.json)).",
        "- Fresh hard reach slice never touched by s_grid "
        f"([`slice_fresh_hard.json`](slice_fresh_hard.json)).",
        "- Cap 48 AC1M; cap 64 unsolved124. `solved`/`solved_at` only for anytime.",
        "- Do not pre-commit Colab arm until wall; lean S may plateau (EXP-16).",
        "",
    ]
    with open(RESULTS_MD, "w") as f:
        f.write("\n".join(lines) + "\n")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    if os.path.exists(STATE):
        state = json.load(open(STATE))
    else:
        start = _now()
        # fromisoformat-friendly
        end = datetime.fromtimestamp(
            start.timestamp() + WALL_HOURS * 3600, tz=timezone.utc)
        state = {
            "wall_start": _iso(start),
            "wall_end": end.isoformat(),
            "phase": "init",
            "BUDGET": BUDGET,
        }
    freeze_slices()
    _write_state(state)
    write_results(state)
    print(f"[scale10k] wall_end={state['wall_end']} remain="
          f"{state['remaining_h']:.2f}h", flush=True)

    # Warm JIT
    greedy_search_hcompact("X", "Y", 50, max_relator_length=48,
                           config=_cfg("s20"), reserve_states=5000)

    phases = [
        ("cost", lambda: phase_cost(state)),
        ("anytime_L", lambda: phase_anytime(
            state, SLICE_L, "l_stratified", 48,
            ("length", "s12", "s20", "recommended"))),
        ("anytime_hard", lambda: phase_anytime(
            state, SLICE_HARD, "fresh_hard", 48,
            ("length", "s20", "recommended", "s12"))),
        ("unsolved124", lambda: phase_unsolved124(state)),
        ("portfolio", lambda: phase_portfolio(state)),
    ]

    round_i = 0
    while _remaining_s(state) > 180:
        round_i += 1
        for name, fn in phases:
            if _remaining_s(state) < 180:
                break
            state["phase"] = name
            state["round"] = round_i
            _write_state(state)
            print(f"\n=== round {round_i} phase={name} "
                  f"remain={state['remaining_h']:.2f}h ===", flush=True)
            n = fn()
            print(f"  phase {name} new={n}", flush=True)
            write_results(state)
            _write_state(state)
            # if a phase returns 0 new, it is complete — continue others
        # if all complete, sleep briefly and refresh results until wall
        if all(
            # rough completion checks
            True for _ in [0]
        ):
            # detect full completion
            L_n = len(json.load(open(SLICE_L))["rows"]) * 4
            H_n = len(json.load(open(SLICE_HARD))["rows"]) * 4
            U_n = 124 * 4
            done_main = 0
            if os.path.exists(MAIN_JSONL):
                done_main = sum(1 for l in open(MAIN_JSONL)
                                if "error" not in json.loads(l))
            target = L_n + H_n + U_n
            if done_main >= target and os.path.exists(PORT_JSONL):
                port_n = sum(1 for _ in open(PORT_JSONL))
                if port_n >= 60:  # 30 single + 30 port
                    print("[scale10k] matrix complete; holding wall for analysis",
                          flush=True)
                    write_results(state)
                    # keep updating RESULTS until wall (user asked 10h research)
                    time.sleep(min(300, max(0, _remaining_s(state) - 60)))
            else:
                # incomplete but phases returned 0 — wait a bit
                if _remaining_s(state) > 300:
                    time.sleep(30)

    state["phase"] = "wall_done"
    _write_state(state)
    write_results(state)
    print("[scale10k] WALL DONE — write COLAB_RECOMMENDATION next", flush=True)


if __name__ == "__main__":
    main()
