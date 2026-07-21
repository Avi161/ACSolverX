"""Idea benchmark: race start-transform strategies against the greedy baseline
AT THE SAME NODE BUDGET, on a boundary-rich subset, and rank by coverage and
honest node cost.

The question this answers: at a small budget (500-1000 nodes), does any idea
solve a presentation the plain greedy CANNOT at that same budget (coverage), or
solve a commonly-solved one for fewer total nodes / a shorter path (efficiency)?

Design (why it is trustworthy):
- **Every metric is a delta vs the greedy baseline run at the SAME budget**, per
  presentation. The baseline is itself a strategy (candidates = just the original
  pair), so "baseline at budget B" is literally ``run_baseline.greedy_search`` and
  nothing is compared across budgets. (User rule: always compare at same budget.)
- A **transform-strategy** is a pure function ``candidates(r1, r2, cap) ->
  [(r1', r2', cap'), ...]`` that returns candidate STARTING presentations (new
  coordinate systems via change-of-variables, relabels, stabilization, …). It runs
  NO search itself. The harness searches each candidate IN ORDER with the trusted
  numba greedy at the run budget and stops at the first solve. So a buggy strategy
  can only pick bad starts and underperform — it can never corrupt a measurement,
  because the only searcher is the trusted solver. This is what makes the subagent
  fan-out safe.
- **Fairness / honest cost.** ``total_nodes`` = cumulative ``nodes_explored`` across
  every candidate searched until the first solve (the realistic portfolio cost, and
  it rewards a strategy that ORDERS its candidates well). ``winning_nodes`` = nodes
  in the solving search (color only — a 30-candidate portfolio always has one lucky
  fast start; never headline it). ``changed_coords`` flags whether the solving start
  differs from the original: if it does, ``path_length`` is in DIFFERENT coordinates
  and EXCLUDES the (unbounded, Lemma-11) change-of-variables prefix, so a "shorter
  path" is NOT comparable to baseline — path wins count only when changed_coords is
  False.
- Ranking headline = **coverage** (solves the baseline can't at the same budget;
  a per-search budget is legitimate here because a portfolio parallelizes across
  coordinate systems) then **total_nodes** on commonly-solved. Winning-nodes and
  cross-coordinate path are reported but never rank.

CPU + numba only; every search ≤ the run budget (≤1000 locally). New files only —
reuses ``run_baseline.greedy_search`` read-only.

CLI:
    .venv/bin/python3 -m experiments.stable_ac.idea_bench.harness --budgets 500 1000
"""

import argparse
import csv
import importlib
import json
import os
import pkgutil
import time
from datetime import datetime

from experiments import run_baseline

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CAP = 24


def find_repo_root(start):
    d = os.path.abspath(start)
    while True:
        if (os.path.isdir(os.path.join(d, "experiments"))
                and os.path.isdir(os.path.join(d, "data"))):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            raise RuntimeError(f"no repo root above {start}")
        d = parent


COMBINED = {
    11: "results/benchmark/combined/benchmark_combined_11.csv",
    22: "results/benchmark/combined/benchmark_combined_22.csv",
}


def load_bench(bench="combined_22"):
    """Load a benchmark set. ``bench`` is 'combined_11' | 'combined_22' (the repo's
    canonical ladder+reach benchmarks, keyed by ``name``), 'bench_set' (the local
    boundary set), or a CSV path. ``nodes_1M`` / ``path_1M`` may be empty (reach
    rows such as AK(3)) — kept as None, so those presentations are pure coverage
    probes with no known optimum."""
    root = find_repo_root(HERE)
    if bench in ("combined_11", "combined_22"):
        path = os.path.join(root, COMBINED[int(bench.split("_")[1])])
    elif bench == "bench_set":
        path = os.path.join(HERE, "bench_set.csv")
    elif bench == "aca_124":
        path = os.path.join(root, "data/ms_unsolved_reps/aca_124.csv")
    elif bench == "mu_descents_d2":
        path = os.path.join(root, "data/ms_unsolved_reps/mu_descents_d2.csv")
    elif bench == "mu_descents_d4":
        path = os.path.join(root, "data/ms_unsolved_reps/mu_descents_d4.csv")
    else:
        path = bench if os.path.isabs(bench) else os.path.join(root, bench)
    rows = []
    with open(path) as f:
        for r in csv.DictReader(f):
            def _int(k):
                v = r.get(k, "")
                return int(v) if v not in (None, "") else None
            rows.append({
                "pres_id": r.get("name") or r.get("pres_id"),
                "r1": r["r1"], "r2": r["r2"],
                "nodes_1M": _int("nodes_1M"), "path_1M": _int("path_1M"),
                "tier": r.get("source") or r.get("tier") or "",
            })
    return rows


# ── built-in strategies ────────────────────────────────────────────────────

def _baseline_candidates(r1, r2, cap):
    """The control: search the original coordinates only. 'Baseline at budget B'."""
    return [(r1, r2, cap)]


BUILTIN = {"baseline": _baseline_candidates}


def load_strategies():
    """{name: candidates_fn}. Built-in baseline + every module in strategies/
    exposing NAME (str) and candidates (callable). KIND defaults to 'transform'."""
    strat = dict(BUILTIN)
    import experiments.stable_ac.idea_bench.strategies as pkg
    for mod in pkgutil.iter_modules(pkg.__path__):
        if mod.name.startswith("_"):
            continue
        m = importlib.import_module(
            f"experiments.stable_ac.idea_bench.strategies.{mod.name}")
        if hasattr(m, "NAME") and hasattr(m, "candidates"):
            if getattr(m, "KIND", "transform") != "transform":
                continue
            strat[m.NAME] = m.candidates
    return strat


# ── evaluation ─────────────────────────────────────────────────────────────

def _search(r1, r2, budget, cap):
    # env var (not a param) so spawned sweep workers inherit it; result-neutral
    return run_baseline.greedy_search(
        r1, r2, budget, max_relator_length=cap, cyclic_reduce=True,
        high_speedup=os.environ.get("ACSOLVERX_HIGH_SPEEDUP") == "1")


def evaluate_cands(cands, r1, r2, budget, cap):
    """Search precomputed candidate starts IN ORDER, stop at first solve.

    total_nodes accumulates across candidates until first solve (honest cost);
    a strategy that orders its candidates well spends fewer. Candidates are
    budget-independent, so the caller generates them ONCE and calls this per
    budget (the parallel runner relies on that). Returns the result dict in the
    module docstring.
    """
    if not cands:
        cands = [(r1, r2, cap)]
    total_nodes = calls = 0
    for i, (cr1, cr2, ccap) in enumerate(cands):
        st = _search(cr1, cr2, budget, ccap)
        calls += 1
        total_nodes += st["nodes_explored"]
        if st["solved"]:
            return {"solved": True, "winning_nodes": st["nodes_explored"],
                    "path_length": st["path_length"], "solve_idx": i,
                    "n_candidates": len(cands), "search_calls": calls,
                    "total_nodes": total_nodes,
                    "changed_coords": (cr1, cr2) != (r1, r2)}
    return {"solved": False, "winning_nodes": None, "path_length": None,
            "solve_idx": None, "n_candidates": len(cands), "search_calls": calls,
            "total_nodes": total_nodes, "changed_coords": False}


def evaluate(cand_fn, r1, r2, budget, cap):
    """Generate candidates then search them (single-budget convenience wrapper)."""
    try:
        cands = list(cand_fn(r1, r2, cap))
    except Exception as e:                       # a broken strategy = no solve, logged
        return {"solved": False, "error": repr(e), "n_candidates": 0,
                "search_calls": 0, "total_nodes": 0, "winning_nodes": None,
                "path_length": None, "solve_idx": None, "changed_coords": False}
    return evaluate_cands(cands, r1, r2, budget, cap)


def run_bench(budgets, cap=DEFAULT_CAP, only=None, bench="combined_22",
              out_dir="results/stable_ac/idea_bench"):
    root = find_repo_root(HERE)
    bench_rows = load_bench(bench)
    strategies = load_strategies()
    if only:
        strategies = {k: v for k, v in strategies.items()
                      if k in set(only) | {"baseline"}}
    od = out_dir if os.path.isabs(out_dir) else os.path.join(root, out_dir)
    os.makedirs(od, exist_ok=True)
    stamp = datetime.now().strftime("%m_%d_%y_%H%M%S")
    out_path = os.path.join(
        od, f"idea_bench_{bench}_{'_'.join(map(str, budgets))}_{stamp}.jsonl")

    print(f"{len(bench_rows)} presentations ({bench}) × {len(strategies)} "
          f"strategies × budgets {budgets} -> {os.path.basename(out_path)}",
          flush=True)
    with open(out_path, "w") as f:
        for budget in budgets:
            for name, fn in strategies.items():
                for p in bench_rows:
                    t0 = time.perf_counter()
                    res = evaluate(fn, p["r1"], p["r2"], budget, cap)
                    res.update({
                        "pres_id": p["pres_id"], "tier": p["tier"],
                        "strategy": name, "budget": budget,
                        "nodes_1M": p["nodes_1M"], "path_1M": p["path_1M"],
                        "elapsed": round(time.perf_counter() - t0, 3),
                    })
                    f.write(json.dumps(res) + "\n")
                    f.flush()
                print(f"  [{budget}] {name:<22} done", flush=True)
    print(f"written: {out_path}", flush=True)
    return out_path


# ── summary ────────────────────────────────────────────────────────────────

def summarize(jsonl_path):
    rows = [json.loads(ln) for ln in open(jsonl_path) if ln.strip()]
    budgets = sorted({r["budget"] for r in rows})
    # index: (budget, strategy, pres_id) -> row
    idx = {(r["budget"], r["strategy"], r["pres_id"]): r for r in rows}
    pres_ids = [r["pres_id"] for r in rows if r["strategy"] == "baseline"
                and r["budget"] == budgets[0]]
    strategies = sorted({r["strategy"] for r in rows} - {"baseline"})

    for budget in budgets:
        base = {pid: idx[(budget, "baseline", pid)] for pid in pres_ids}
        base_solved = {pid for pid in pres_ids if base[pid]["solved"]}
        print(f"\n{'='*78}\nBUDGET {budget}  (baseline solves "
              f"{len(base_solved)}/{len(pres_ids)}: "
              f"{sorted(base_solved)})\n{'='*78}")
        print(f"{'strategy':<22} {'solved':>6} {'covWIN':>7} {'covLOSS':>7} "
              f"{'effWIN':>6} {'effLOSS':>7} {'pathWIN':>7}  notes")
        # baseline line
        print(f"{'baseline':<22} {len(base_solved):>6} {'-':>7} {'-':>7} "
              f"{'-':>6} {'-':>7} {'-':>7}  (anchor)")
        rankable = []
        for s in strategies:
            solved = cov_win = cov_loss = eff_win = eff_loss = path_win = 0
            cov_win_ids, eff_win_ids = [], []
            for pid in pres_ids:
                r = idx.get((budget, s, pid))
                if r is None:
                    continue
                b = base[pid]
                if r["solved"]:
                    solved += 1
                # coverage vs baseline at same budget
                if r["solved"] and not b["solved"]:
                    cov_win += 1; cov_win_ids.append(pid)
                if b["solved"] and not r["solved"]:
                    cov_loss += 1
                # efficiency on commonly solved: honest total_nodes
                if r["solved"] and b["solved"]:
                    if r["total_nodes"] < b["total_nodes"]:
                        eff_win += 1; eff_win_ids.append(pid)
                    elif r["total_nodes"] > b["total_nodes"]:
                        eff_loss += 1
                    # path win only WITHIN coordinates (else prefix excluded)
                    if (not r["changed_coords"] and r["path_length"] is not None
                            and b["path_length"] is not None
                            and r["path_length"] < b["path_length"]):
                        path_win += 1
            note = ""
            if cov_win_ids:
                note += f"cov+:{cov_win_ids} "
            if eff_win_ids:
                note += f"eff+:{eff_win_ids}"
            print(f"{s:<22} {solved:>6} {cov_win:>7} {cov_loss:>7} "
                  f"{eff_win:>6} {eff_loss:>7} {path_win:>7}  {note}")
            rankable.append((cov_win, eff_win, -cov_loss, s))
        rankable.sort(reverse=True)
        top = [f"{s}(cov{cw},eff{ew})" for cw, ew, _, s in rankable[:5]]
        print(f"\n  most promising @ {budget}: {top}")


def main():
    ap = argparse.ArgumentParser(description="Idea benchmark vs same-budget greedy.")
    ap.add_argument("--budgets", type=int, nargs="+", default=[500, 1000])
    ap.add_argument("--cap", type=int, default=DEFAULT_CAP)
    ap.add_argument("--bench", default="combined_22",
                    help="combined_11 | combined_22 | bench_set | a CSV path")
    ap.add_argument("--only", nargs="*", default=None,
                    help="restrict to these strategy names (+baseline)")
    ap.add_argument("--summarize", default=None, help="summarize an existing jsonl")
    args = ap.parse_args()
    if args.summarize:
        summarize(args.summarize)
        return
    path = run_bench(args.budgets, cap=args.cap, only=args.only, bench=args.bench)
    summarize(path)


if __name__ == "__main__":
    main()
