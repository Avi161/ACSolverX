"""W&B run identity and derived charts for the greedy baseline.

Everything here is computed from the jsonl rows ``run_baseline.py`` already
writes. No solver change, no jsonl schema change: ``initial_length`` comes from
``len(r1) + len(r2)``, the hump baseline from replaying the stored moves, and
the anytime profile from the ``nodes_explored`` of the solved rows.

The module is split so the interesting half is testable without wandb:

    compute_analytics(...)  -> plain dicts/lists, no wandb import, no network
    build_panels(...)       -> maps that onto wandb.Histogram / Table / plot.*

``wandb`` is imported lazily inside the functions that need it, so importing
this module costs nothing when ``USE_WANDB`` is off.

Panel keys are namespaced (``profile/``, ``difficulty/``, ``hump/``, ``dist/``,
``perf/``, ``unsolved/``, ``rel/``, ``run/``, ``pres/``) so the W&B workspace
groups them into sections instead of one flat wall of charts.

TIMING CAVEAT — read before trusting any timing panel on a HIGH_SPEEDUP run.
``time_seconds`` means two different things there. An *unsolved* row is timed
inside a pool worker (inflated by contention). A *solved* row is timed by the
serial, full-price normal-mode recovery re-solve that runs after the pool tears
down (``run_baseline.py``, the ``deferred`` loop) — not by the heavy solve that
actually found it. So solved and unsolved timings come from different regimes
and are not comparable. Rows carry ``path_recovered`` for exactly this reason:
when any row has it, the timing panels are titled as mixed-regime and
``summary["timing_regime"]`` reads ``mixed(heavy)``. Timing panels are clean and
unqualified whenever HIGH_SPEEDUP is off (the whole <=50k sweep).
"""

import json
import os
import socket
import statistics
import subprocess
from bisect import bisect_right

# Budgets the anytime profile reports a solve rate at (those <= node_budget).
BUDGET_THRESHOLDS = (1_000, 5_000, 10_000, 25_000, 50_000,
                     100_000, 250_000, 500_000, 1_000_000)

# Replaying a solution path costs numba calls per move. Cap how many we replay
# at finish time; the sample is spread across the path_length distribution.
DEFAULT_PATH_SAMPLE = 200

TABLE_COLUMNS = [
    "pres_id", "r1", "r2", "node_budget", "max_relator_length_cap",
    "cyclic_reduce", "nodes_explored", "solved", "path_length",
    "min_relator_length", "max_relator_length", "max_relator_length_expanded",
    "time_seconds", "initial_length", "nodes_per_s", "hump_height",
    "budget_frac", "path_recovered",
]


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def human_budget(n):
    """1000 -> '1k', 1000000 -> '1M'. Used in names/tags, never in identity."""
    n = int(n)
    if n >= 1_000_000 and n % 1_000_000 == 0:
        return f"{n // 1_000_000}M"
    if n >= 1_000 and n % 1_000 == 0:
        return f"{n // 1_000}k"
    return str(n)


def _mean(xs):
    return statistics.fmean(xs) if xs else None


def _median(xs):
    return statistics.median(xs) if xs else None


def _percentile(xs, q):
    """Nearest-rank percentile; q in [0,1]. None on empty."""
    if not xs:
        return None
    s = sorted(xs)
    i = min(len(s) - 1, max(0, int(round(q * (len(s) - 1)))))
    return s[i]


def _git_commit():
    try:
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                             capture_output=True, text=True, timeout=5)
        return out.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def canonical_initial_length(r1_str, r2_str, cyclic_reduce=True):
    """|r1|+|r2| of the state the search actually starts from.

    The search reduces and canonicalises before its first pop, and cyclic
    reduction can shorten the stored input. Comparing a canonical
    ``max_relator_length_expanded`` against a raw ``len(r1)+len(r2)`` would then
    inflate the hump height. The two agree on all 901 presentations of
    ms640_solved + ms_reps_unsolved under both cyclic settings, but the baseline
    must not depend on that holding for future data.
    """
    from experiments.search.greedy_baseline import (
        arr_to_str, canonical_pair_nj, reduce_relator_nj, str_to_arr)
    a = reduce_relator_nj(str_to_arr(r1_str), cyclic_reduce)
    b = reduce_relator_nj(str_to_arr(r2_str), cyclic_reduce)
    a, b = canonical_pair_nj(a, b)
    return len(arr_to_str(a)) + len(arr_to_str(b))


# ---------------------------------------------------------------------------
# Run identity
# ---------------------------------------------------------------------------
def compute_identity(cfg, node_budget, n_pres, run_prefix, subset_tag):
    """group / name / job_type / tags / config for one run.

    ``group`` is the sweep identity: the run prefix minus budget and date. Runs
    in a group differ only by node_budget, so the group view compares budgets
    directly. ``id`` (the resume key) is the caller's stem and is not touched.

    ``config`` is an allowlist. Dumping the whole cfg would put HEARTBEAT_*,
    MP_START_METHOD, GB_PER_PRES and the output dirs in the runs table, which is
    the mess this is meant to fix. Only knobs that change the search, plus
    provenance, get in.
    """
    dataset_name = os.path.splitext(os.path.basename(cfg["DATASET"]))[0]
    cap = cfg["MAX_RELATOR_LENGTH"]
    cyc = "cyc" if cfg["CYCLIC_REDUCE"] else "noncyc"
    budget_h = human_budget(node_budget)
    solver = "heavy" if cfg.get("HIGH_SPEEDUP") else "normal"

    group = cfg.get("WANDB_GROUP") or f"{dataset_name}-mrl{cap}-{cyc}-{subset_tag}"
    job_type = cfg.get("WANDB_JOB_TYPE") or "greedy_baseline"

    name = cfg.get("WANDB_RUN_NAME")
    if not name:
        name = f"{budget_h} · {dataset_name} · mrl{cap} · {cyc}"
        if subset_tag != "all":
            name += f" · {subset_tag}"

    tags = [dataset_name, f"mrl{cap}", cyc, f"b{budget_h}", solver,
            f"subset:{subset_tag}"]
    tags.extend(cfg.get("WANDB_TAGS") or [])

    config = {
        "node_budget": int(node_budget),      # numeric so it sorts and plots
        "budget_human": budget_h,
        "max_relator_length": cap,
        "cyclic_reduce": bool(cfg["CYCLIC_REDUCE"]),
        "dataset": cfg["DATASET"],
        "dataset_name": dataset_name,
        "n_pres": int(n_pres),
        "subset": str(cfg["SUBSET"]),
        "subset_tag": subset_tag,
        "solver": solver,
        "n_workers": int(cfg.get("N_WORKERS", 0) or 0),
        "run_prefix": run_prefix,
        "git_commit": _git_commit(),
        "hostname": socket.gethostname(),
    }
    return {"group": group, "name": name, "job_type": job_type,
            "tags": tags, "config": config}


# ---------------------------------------------------------------------------
# Pure derivations
# ---------------------------------------------------------------------------
def derive_row(row, canon_length=None):
    """Add derived fields to a jsonl row. Never raises on a minimal row.

    Fields gated behind the ``use_*`` toggles may be absent (older rows, or a
    run with a toggle off), so anything underivable comes back as None and every
    aggregator below filters it out.
    """
    out = dict(row)
    initial_length = len(row.get("r1") or "") + len(row.get("r2") or "")
    out["initial_length"] = initial_length
    out["canonical_initial_length"] = (
        initial_length if canon_length is None else int(canon_length))
    out["solved"] = bool(row.get("solved"))
    out["path_recovered"] = bool(row.get("path_recovered", False))

    t = row.get("time_seconds")
    nodes = row.get("nodes_explored")
    out["nodes_per_s"] = (nodes / t) if (t and nodes is not None and t > 0) else None

    expanded = row.get("max_relator_length_expanded")
    out["hump_height"] = (
        expanded - out["canonical_initial_length"] if expanded is not None else None)

    budget = row.get("node_budget")
    out["budget_frac"] = (nodes / budget) if (budget and nodes is not None) else None
    return out


def anytime_profile(rows, n_pres, node_budget, thresholds=BUDGET_THRESHOLDS):
    """The solve rate a smaller budget would have reached, exactly.

    The search is deterministic and a budget only truncates it, so a
    presentation that solved after ``nodes_explored`` pops would also have
    solved under any budget >= that. Hence

        solve_rate(b) = |{solved and nodes_explored <= b}| / n_pres

    is exact for every b <= node_budget, and one run gives the whole curve.
    Returns ``(points, solve_rate_at)`` where points is [[budget, rate], ...]
    stepping up at each distinct solved cost and flat to node_budget.
    """
    n_pres = max(int(n_pres), 1)
    solved_nodes = sorted(r["nodes_explored"] for r in rows if r.get("solved"))

    points = [[0, 0.0]]
    for i, v in enumerate(solved_nodes):
        if i + 1 < len(solved_nodes) and solved_nodes[i + 1] == v:
            continue                      # only emit the last of a tied group
        points.append([int(v), (i + 1) / n_pres])

    final = len(solved_nodes) / n_pres
    if points[-1][0] < int(node_budget):
        points.append([int(node_budget), final])

    solve_rate_at = {}
    for t in thresholds:
        if t <= node_budget:
            hit = bisect_right(solved_nodes, t)
            solve_rate_at[f"solve_rate_at_{human_budget(t)}"] = hit / n_pres
    return points, solve_rate_at


def bucket_by_initial_length(rows):
    """Per initial |r1|+|r2|: how often we solve and how much it costs."""
    buckets = {}
    for r in rows:
        buckets.setdefault(r["initial_length"], []).append(r)

    out = []
    for L in sorted(buckets):
        group = buckets[L]
        nodes = [g["nodes_explored"] for g in group if g.get("nodes_explored") is not None]
        solved = [g for g in group if g["solved"]]
        solved_nodes = [g["nodes_explored"] for g in solved]
        out.append({
            "initial_length": L,
            "n": len(group),
            "n_solved": len(solved),
            "solve_rate": len(solved) / len(group),
            "median_nodes": _median(nodes),
            "median_nodes_solved": _median(solved_nodes),
        })
    return out


def replay_lengths(path_rows, cyclic_reduce=True, limit=DEFAULT_PATH_SAMPLE):
    """Replay stored moves into the total-length profile L(t) of each path.

    L(t) = |r1|+|r2| of the canonical state after t moves, so L(0) is the
    canonical start length and L(-1) is 2 (the trivial presentation). This is
    the Two-Hump curve: substitution moves solve by temporarily *lengthening* a
    relator, which is invisible in every other metric we store.

    Deterministic: rows are ordered by (path_length, pres_id) and the sample is
    spread evenly across that order, so the same run always replays the same
    paths.
    """
    from experiments.search.greedy_baseline import moves_to_states, str_to_move

    usable = [r for r in path_rows if r.get("path_moves") is not None]
    usable.sort(key=lambda r: (len(r["path_moves"]), r["pres_id"]))
    for r in _spread(usable, limit):
        moves = [str_to_move(s) for s in r["path_moves"]]
        states = moves_to_states(r["r1"], r["r2"], moves, cyclic_reduce)
        yield r["pres_id"], [len(a) + len(b) for a, b in states]


def _spread(items, k):
    """<=k items spread evenly across a list, endpoints included. Deterministic."""
    n = len(items)
    if k <= 0 or n == 0:
        return []
    if n <= k:
        return list(items)
    if k == 1:
        return [items[0]]
    idx = sorted({round(i * (n - 1) / (k - 1)) for i in range(k)})
    return [items[i] for i in idx]


def path_analytics(path_rows, cyclic_reduce=True, n_profiles=8,
                   sample=DEFAULT_PATH_SAMPLE):
    """One replay pass -> both the L(t) line series and the hump statistics.

    ``n_profiles <= 0`` skips the replay entirely: it is the only part of the
    finish-time analytics that costs real work. The cheap ``hump/overshoot_hist``
    (built from ``max_relator_length_expanded``) still covers the phenomenon.
    """
    if n_profiles <= 0 or not path_rows:
        return {"series": None, "overshoots": [], "peak_positions": []}

    profiles = list(replay_lengths(path_rows, cyclic_reduce, sample))
    if not profiles:
        return {"series": None, "overshoots": [], "peak_positions": []}

    overshoots, peak_positions = [], []
    for _pid, L in profiles:
        peak = max(L)
        overshoots.append(peak - L[0])
        if len(L) > 1:
            peak_positions.append(L.index(peak) / (len(L) - 1))

    chosen = _spread(profiles, n_profiles)
    series = None
    if chosen:
        series = {
            "xs": [list(range(len(L))) for _pid, L in chosen],
            "ys": [L for _pid, L in chosen],
            "keys": [f"#{pid} ({len(L) - 1} moves)" for pid, L in chosen],
        }
    return {"series": series, "overshoots": overshoots,
            "peak_positions": peak_positions}


def summary_stats(rows, n_pres, n_solved, total_time):
    nodes_all = [r["nodes_explored"] for r in rows if r.get("nodes_explored") is not None]
    nodes_solved = [r["nodes_explored"] for r in rows if r["solved"]]
    paths_solved = [r["path_length"] for r in rows
                    if r["solved"] and r.get("path_length") is not None]
    nps = [r["nodes_per_s"] for r in rows if r["nodes_per_s"] is not None]
    humps = [r["hump_height"] for r in rows if r["hump_height"] is not None]

    n_seen = max(int(n_pres), 1)
    return {
        "n_pres": n_pres,
        "n_solved": n_solved,
        "solve_rate": n_solved / n_seen,
        "censored_fraction": (n_seen - n_solved) / n_seen,
        "nodes_explored_mean": _mean(nodes_all),
        "nodes_explored_median": _median(nodes_all),
        "nodes_explored_p90": _percentile(nodes_all, 0.9),
        "nodes_explored_solved_mean": _mean(nodes_solved),
        "path_length_mean": _mean(paths_solved),
        "path_length_median": _median(paths_solved),
        "nodes_per_s_mean": _mean(nps),
        "hump_height_median": _median(humps),
        "total_time_s": round(total_time, 2),
    }


# ---------------------------------------------------------------------------
# jsonl -> analytics
# ---------------------------------------------------------------------------
def read_jsonl(path):
    rows = []
    if path and os.path.exists(path):
        with open(path) as f:
            for ln in f:
                ln = ln.strip()
                if ln:
                    rows.append(json.loads(ln))
    return rows


def compute_analytics(rows, path_rows, cfg, node_budget, n_seen, n_solved,
                      total_time, canon_len_fn=None):
    """Everything the charts need, as plain Python. No wandb, no network."""
    cyc = bool(cfg.get("CYCLIC_REDUCE", True))
    if canon_len_fn is None:
        derived = [derive_row(r) for r in rows]
    else:
        derived = [derive_row(r, canon_len_fn(r.get("r1", ""), r.get("r2", ""), cyc))
                   for r in rows]

    summary = summary_stats(derived, n_seen, n_solved, total_time)
    points, solve_rate_at = anytime_profile(derived, n_seen, node_budget)
    summary.update(solve_rate_at)

    # Solved rows on a heavy run are timed by the serial recovery re-solve, not
    # by the heavy solve that found them (see module docstring).
    mixed_timing = any(r["path_recovered"] for r in derived)
    summary["timing_regime"] = "mixed(heavy)" if mixed_timing else "uniform"

    solved = [r for r in derived if r["solved"]]
    unsolved = [r for r in derived if not r["solved"]]
    paths = path_analytics(path_rows, cyc, int(cfg.get("WANDB_PATH_PROFILES", 8) or 0),
                           int(cfg.get("WANDB_PATH_SAMPLE", DEFAULT_PATH_SAMPLE)))

    return {
        "summary": summary,
        "rows": derived,
        "mixed_timing": mixed_timing,
        "profile_points": points,
        "buckets": bucket_by_initial_length(derived),
        "hists": {
            "dist/nodes_explored_solved": [r["nodes_explored"] for r in solved],
            "dist/nodes_explored_unsolved": [r["nodes_explored"] for r in unsolved],
            "dist/path_length": [r["path_length"] for r in solved
                                 if r.get("path_length") is not None],
            "dist/time_seconds": [r["time_seconds"] for r in derived
                                  if r.get("time_seconds") is not None],
            "dist/nodes_per_s": [r["nodes_per_s"] for r in derived
                                 if r["nodes_per_s"] is not None],
            "hump/overshoot_hist": [r["hump_height"] for r in derived
                                    if r["hump_height"] is not None],
            "hump/path_overshoot_hist": paths["overshoots"],
            "hump/path_peak_position_hist": paths["peak_positions"],
            "unsolved/closest_approach_hist": [r["min_relator_length"] for r in unsolved
                                               if r.get("min_relator_length") is not None],
        },
        "scatters": {
            "rel/nodes_vs_path": (
                ["nodes_explored", "path_length"],
                [[r["nodes_explored"], r["path_length"]] for r in solved
                 if r.get("path_length") is not None]),
            "difficulty/initial_length_vs_nodes": (
                ["initial_length", "nodes_explored"],
                [[r["initial_length"], r["nodes_explored"]] for r in derived]),
            "hump/peak_vs_initial": (
                ["initial_length", "max_relator_length_expanded"],
                [[r["canonical_initial_length"], r["max_relator_length_expanded"]]
                 for r in derived if r.get("max_relator_length_expanded") is not None]),
            "perf/nodes_per_s_vs_initial_length": (
                ["initial_length", "nodes_per_s"],
                [[r["initial_length"], r["nodes_per_s"]] for r in derived
                 if r["nodes_per_s"] is not None]),
        },
        "path_series": paths["series"],
    }


# ---------------------------------------------------------------------------
# analytics -> wandb panels
# ---------------------------------------------------------------------------
def build_panels(analytics):
    """Map the analytics dict onto wandb chart objects. Skips empty panels."""
    import wandb

    panels = {}
    timing_note = (" [heavy run: solved rows timed by the serial recovery re-solve]"
                   if analytics["mixed_timing"] else "")

    points = analytics["profile_points"]
    if len(points) > 1:
        t = wandb.Table(data=points, columns=["budget", "solve_rate"])
        panels["profile/solve_rate_vs_budget"] = wandb.plot.line(
            t, "budget", "solve_rate",
            title="solve rate a given node budget would have reached")

    buckets = analytics["buckets"]
    if buckets:
        # Zero-padded labels keep the bar chart's categorical axis in numeric order.
        t = wandb.Table(data=[[f"{b['initial_length']:02d}", b["solve_rate"]]
                              for b in buckets],
                        columns=["initial_length", "solve_rate"])
        panels["difficulty/solve_rate_by_initial_length"] = wandb.plot.bar(
            t, "initial_length", "solve_rate",
            title="solve rate by initial |r1|+|r2|")

        med = [[b["initial_length"], b["median_nodes"]] for b in buckets
               if b["median_nodes"] is not None]
        if med:
            t = wandb.Table(data=med, columns=["initial_length", "median_nodes"])
            panels["difficulty/median_nodes_by_initial_length"] = wandb.plot.line(
                t, "initial_length", "median_nodes",
                title="median nodes explored by initial |r1|+|r2|")

    for key, values in analytics["hists"].items():
        if values:
            panels[key] = wandb.Histogram(values)

    for key, (columns, data) in analytics["scatters"].items():
        if data:
            title = key.split("/", 1)[1].replace("_", " ")
            if key.startswith("perf/"):
                title += timing_note
            panels[key] = wandb.plot.scatter(
                wandb.Table(data=data, columns=columns), columns[0], columns[1],
                title=title)

    series = analytics["path_series"]
    if series:
        panels["hump/path_profile"] = wandb.plot.line_series(
            xs=series["xs"], ys=series["ys"], keys=series["keys"],
            title="|r1|+|r2| along the solution path (the two humps)",
            xname="move")
    return panels


# ---------------------------------------------------------------------------
# Run lifecycle
# ---------------------------------------------------------------------------
def init_run(cfg, node_budget, n_pres, run_id, run_prefix, subset_tag):
    """Start (or reattach to) the W&B run and declare the custom step metrics."""
    import wandb

    ident = compute_identity(cfg, node_budget, n_pres, run_prefix, subset_tag)
    run = wandb.init(
        entity=cfg["WANDB_ENTITY"] or None, project=cfg["WANDB_PROJECT"],
        id=run_id, name=ident["name"], resume="allow",
        group=ident["group"], job_type=ident["job_type"], tags=ident["tags"],
        mode=cfg["WANDB_MODE"], notes=cfg.get("WANDB_NOTES") or None,
        config=ident["config"],
    )

    # Two independent x-axes, neither of which is the global step. `run/*` is
    # cumulative so it needs a monotone counter; `pres/*` is per-presentation so
    # it is keyed on pres_id, which HIGH_SPEEDUP delivers out of order. Passing
    # step= for either would be rejected as non-monotonic on a resumed run.
    run.define_metric("n_processed")
    run.define_metric("run/*", step_metric="n_processed")
    run.define_metric("pres_id")
    run.define_metric("pres/*", step_metric="pres_id")

    # init() ignores a changed group/job_type on reattach and tag merging is
    # version-fragile, so mark the resume after the fact.
    if getattr(run, "resumed", False) and "resumed" not in (run.tags or ()):
        run.tags = tuple(run.tags or ()) + ("resumed",)
    return run


class LiveLogger:
    """Per-presentation logging, split to survive HIGH_SPEEDUP's ordering.

    In heavy mode ``imap_unordered`` yields results in arbitrary pres_id order,
    and a *solved* presentation's row is not written until after the pool tears
    down and a serial re-solve recovers its path. So the two things you want to
    watch happen at different times:

      on_result  fires as each worker result arrives -> cumulative `run/*`
      on_row     fires when the row is finally written -> per-pres `pres/*`

    `run/*` counters accumulate only in on_result. The recovery re-solve reports
    the same nodes_explored, so accumulating again in on_row would double-count.
    """

    def __init__(self, run, cfg, node_budget, n_todo, n_seen, n_solved, cum_nodes):
        import time
        import wandb

        self.run = run
        self.node_budget = int(node_budget)
        self.n_todo = int(n_todo)
        self.n_processed = int(n_seen)      # seeded from the jsonl on resume
        self.n_solved = int(n_solved)
        self.cum_nodes = int(cum_nodes)
        self.log_pres = bool(cfg.get("WANDB_LOG_PRES_SCALARS", True))
        self.cyclic_reduce = bool(cfg.get("CYCLIC_REDUCE", True))
        self.table = wandb.Table(columns=TABLE_COLUMNS)
        self._t0 = time.time()
        # Throughput and ETA describe THIS session, so they must not be computed
        # from the resume-seeded totals -- those were earned in an earlier one.
        self._session_done = 0
        self._session_nodes = 0

    def add_existing_row(self, row):
        """Rebuild the Table from a row written by an earlier session."""
        self.table.add_data(*self._table_data(row))

    def on_result(self, stats):
        import time

        self.n_processed += 1
        self.n_solved += int(bool(stats["solved"]))
        self.cum_nodes += int(stats["nodes_explored"])
        self._session_done += 1
        self._session_nodes += int(stats["nodes_explored"])

        elapsed = time.time() - self._t0
        rate = (self._session_done / elapsed) if elapsed > 0 else 0.0
        remaining = max(self.n_todo - self._session_done, 0)

        self.run.log({
            "n_processed": self.n_processed,
            "run/solve_rate": self.n_solved / max(self.n_processed, 1),
            "run/n_solved": self.n_solved,
            "run/cum_nodes": self.cum_nodes,
            "run/elapsed_s": round(elapsed, 2),
            "run/nodes_per_s": (self._session_nodes / elapsed) if elapsed > 0 else 0.0,
            "run/eta_min": (remaining / rate / 60.0) if rate > 0 else 0.0,
        })

    def on_row(self, row):
        self.table.add_data(*self._table_data(row))
        if not self.log_pres:
            return
        derived = self._derive(row)
        payload = {"pres_id": row["pres_id"],
                   "pres/nodes_explored": row["nodes_explored"],
                   "pres/initial_length": derived["initial_length"]}
        for src, dst in (("path_length", "pres/path_length"),
                         ("time_seconds", "pres/time_seconds")):
            if row.get(src) is not None:
                payload[dst] = row[src]
        if derived["hump_height"] is not None:
            payload["pres/hump_height"] = derived["hump_height"]
        self.run.log(payload)

    def _derive(self, row):
        return derive_row(row, canonical_initial_length(
            row.get("r1", ""), row.get("r2", ""), self.cyclic_reduce))

    def _table_data(self, row):
        d = self._derive(row)
        return [d.get(c) for c in TABLE_COLUMNS]


def finish_run(run, logger, out_path, paths_path, run_id, n_seen, n_solved,
               total_time, cfg, node_budget):
    """Recompute everything from the jsonl (source of truth), log, archive."""
    import wandb

    rows = read_jsonl(out_path)
    path_rows = read_jsonl(paths_path) if cfg.get("PATH_IN_SEPARATE_FILE") else []
    analytics = compute_analytics(rows, path_rows, cfg, node_budget, n_seen,
                                  n_solved, total_time,
                                  canon_len_fn=canonical_initial_length)

    run.summary.update(analytics["summary"])
    run.log({"tables/results": logger.table})
    panels = build_panels(analytics)
    if panels:
        run.log(panels)

    art = wandb.Artifact(run_id, type="results")
    art.add_file(out_path)
    if cfg["PATH_IN_SEPARATE_FILE"] and os.path.exists(paths_path):
        art.add_file(paths_path)
    run.log_artifact(art)
    run.finish()
