"""Baseline greedy pipeline runner — data load, jsonl (resumable), W&B.

CPU + numba only. Run from the ACSolverX repo root (data paths are relative).
The heavy lifting is in ``experiments.search.greedy_baseline``; this module is
just the experiment harness around it.
"""

import ast
import hashlib
import json
import os
import time
from datetime import datetime

from experiments.search.greedy_baseline import greedy_search


# Integer encoding of data/ms640_solved.txt: 1=x, -1=X, 2=y, -2=Y, 0=pad.
_INT_TO_CHAR = {1: 'x', -1: 'X', 2: 'y', -2: 'Y'}


DEFAULT_CONFIG = {
    "DATASET": "data/ms640_solved.txt",
    "SUBSET": None,                  # None=all, list[int] of pres_id, or (start, end)
    "MAX_RELATOR_LENGTH": 24,        # per-relator cap
    "CYCLIC_REDUCE": True,

    # jsonl field toggles (each keeps BOTH the length + the relator pair)
    "use_min_relator": True,            # min_relator_length + min_relator
    "use_max_relator": True,            # max_relator_length + max_relator
    "use_max_relator_expanded": True,   # longest presentation actually popped/expanded (length + relator)
    "use_time": True,
    "use_path": True,
    "PATH_IN_SEPARATE_FILE": True,
    # How to store a solved path: "moves" = compact Definition 2.1 tuples
    # 'target_jsign_k1_k2' (replayable via moves_to_states, ~4 ints/step);
    # "strings" = [r1, r2] state list; "both" = keep each under its own key.
    "PATH_FORMAT": "moves",

    "RESUME": True,

    # HIGH_SPEEDUP — for heavy (e.g. 1M-node) runs ONLY. Same solved /
    # nodes_explored / min+max relator lengths as the normal path (verified),
    # but ~2.6x less memory and ~2.4x faster, and it parallelises across
    # presentations. Solved presentations are re-solved by the normal solver
    # afterwards to recover their path (rare: heavy runs are the hard ones).
    "HIGH_SPEEDUP": False,
    "N_WORKERS": 0,                  # 0 = auto (bounded by RAM / GB_PER_PRES)
    "GB_PER_PRES": 9.0,              # measured: 1M nodes, mrl=48, heavy solver

    # output
    "MOUNT_DRIVE": False,
    "DRIVE_OUT_DIR": "/content/drive/MyDrive/acsolverx_results/greedy_baseline",
    "LOCAL_OUT_DIR": "results/greedy_baseline",

    # W&B
    "USE_WANDB": False,
    "WANDB_ENTITY": "avigyapaudel045-aisc",   # writable team entity (org-managed acct; None = account default)
    "WANDB_PROJECT": "acsolver",
    "WANDB_MODE": "online",
    "WANDB_GROUP": None,             # default set at runtime to greedy_baseline_{date}

    "PROGRESS_EVERY": 10,            # print a status line every N processed presentations

    # Live nodes/s while a single presentation is still running (a 1M-node solve
    # takes minutes, so PROGRESS_EVERY says nothing until it finishes). 0 = off.
    # Result-neutral, so it is deliberately absent from _run_prefix.
    "HEARTBEAT_EVERY_S": 0,
}


def int_line_to_relators(line_ints):
    """A 48-int ms640 line -> (r1_str, r2_str) in the xXyY alphabet."""
    half = len(line_ints) // 2
    r1 = ''.join(_INT_TO_CHAR[t] for t in line_ints[:half] if t != 0)
    r2 = ''.join(_INT_TO_CHAR[t] for t in line_ints[half:] if t != 0)
    return r1, r2


def load_dataset(path, subset=None):
    """Yield (pres_id, r1_str, r2_str) for the selected presentations.

    Parsing matches envs/ac_s.py:initiate_states (literal_eval per line).
    ``subset``: None=all, list[int] of pres_ids, or (start, end) half-open range.
    """
    with open(path, "r") as f:
        lines = [ast.literal_eval(ln.strip()) for ln in f if ln.strip()]

    if subset is None:
        ids = range(len(lines))
    elif isinstance(subset, tuple):
        ids = range(subset[0], subset[1])
    else:
        ids = subset

    for pres_id in ids:
        r1, r2 = int_line_to_relators(lines[pres_id])
        yield pres_id, r1, r2


def _subset_tag(subset):
    """A short, collision-safe tag identifying WHICH presentations ran.

    ``n_pres`` alone is ambiguous (e.g. SUBSET=(0,5) and SUBSET=[10,20,30,40,50]
    both have 5), so different subsets could otherwise share a filename. This
    encodes the actual selection: 'all' / a range / a hash of an explicit list.
    """
    if subset is None:
        return "all"
    if isinstance(subset, tuple):
        return f"{subset[0]}-{subset[1]}"
    # Explicit list: order-independent hash of its members.
    key = ",".join(str(i) for i in sorted(subset))
    return "ids" + hashlib.sha1(key.encode()).hexdigest()[:8]


def _run_prefix(cfg, node_budget, n_pres):
    """Date-less filename stem covering every knob that changes the search result.

    Two runs collide (share a file, and resume-merge) ONLY if they are truly
    the same experiment. Search-affecting knobs (cap, cyclic_reduce) and the
    subset selection are all encoded; jsonl field toggles are intentionally
    excluded (they change stored columns, not the computed result, and resume
    correctly reuses those rows). The DATE is deliberately NOT here — it must
    not gate resume (see _resolve_paths).
    """
    cyc = "cyc" if cfg["CYCLIC_REDUCE"] else "noncyc"
    tag = _subset_tag(cfg["SUBSET"])
    return (f"greedy_{node_budget}_{n_pres}_mrl{cfg['MAX_RELATOR_LENGTH']}"
            f"_{cyc}_{tag}_")


def _resolve_paths(cfg, node_budget, n_pres):
    import glob
    out_dir = cfg["DRIVE_OUT_DIR"] if cfg["MOUNT_DRIVE"] else cfg["LOCAL_OUT_DIR"]
    os.makedirs(out_dir, exist_ok=True)
    prefix = _run_prefix(cfg, node_budget, n_pres)
    date = datetime.now().strftime("%m_%d_%y")
    stem = prefix + date

    # Resume must be date-agnostic: a run continued on a later day (or after a
    # Colab disconnect spanning midnight) has to reattach to the SAME file, not
    # start a fresh one. The date only marks when the run first began, so match
    # any existing file with this identity prefix and continue the furthest one.
    if cfg.get("RESUME", True):
        existing = [p for p in glob.glob(os.path.join(out_dir, prefix + "*.jsonl"))
                    if not p.endswith("_paths.jsonl")]
        if existing:
            best = max(existing, key=lambda p: sum(1 for _ in open(p)))
            stem = os.path.basename(best)[:-len(".jsonl")]

    out_path = os.path.join(out_dir, stem + ".jsonl")
    paths_path = os.path.join(out_dir, stem + "_paths.jsonl")
    return out_path, paths_path, date, stem


def _read_done(out_path):
    """(done_ids, n_seen, n_solved) reconstructed from an existing jsonl."""
    done, n_seen, n_solved = set(), 0, 0
    if os.path.exists(out_path):
        with open(out_path, "r") as f:
            for ln in f:
                ln = ln.strip()
                if not ln:
                    continue
                row = json.loads(ln)
                done.add(row["pres_id"])
                n_seen += 1
                n_solved += int(bool(row.get("solved")))
    return done, n_seen, n_solved


def _total_ram_gb():
    try:
        return (os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")) / 1e9
    except (ValueError, OSError, AttributeError):
        return 0.0


def _auto_workers(cfg):
    """Worker count for HIGH_SPEEDUP: bounded by cores AND by RAM.

    Each concurrent search holds its own frontier (~GB_PER_PRES), so RAM is the
    real cap — oversubscribing cores would OOM long before it helped.
    """
    n = int(cfg.get("N_WORKERS", 0) or 0)
    if n > 0:
        return n
    cores = os.cpu_count() or 1
    ram = _total_ram_gb()
    gb = float(cfg.get("GB_PER_PRES", 9.0)) or 9.0
    by_ram = int((ram * 0.8) // gb) if ram else 1
    return max(1, min(cores, by_ram or 1))


# --- live nodes/s heartbeat ------------------------------------------------
# A pool worker cannot print into a notebook: ipykernel's stdout proxy relies on
# a background pub_thread that a forked child does not inherit, so the write is
# silently dropped. Workers therefore push samples onto an mp.Queue that a
# thread in the PARENT drains and prints.
_HB_Q = None


def _init_worker(q):
    global _HB_Q
    _HB_Q = q


class _Heartbeat:
    """Rate-limited nodes/s sampler, called from inside the search loop.

    The solver calls this every 1024 pops; it emits at most one sample per
    ``every`` seconds, so the per-node cost is a modulo and a clock read.
    """

    def __init__(self, pres_id, budget, every, sink):
        self.pres_id, self.budget, self.every, self.sink = pres_id, budget, every, sink
        self.t0 = self.t_last = time.time()
        self.n_last = 0

    def __call__(self, nodes):
        now = time.time()
        dt = now - self.t_last
        if dt < self.every:
            return
        rate = (nodes - self.n_last) / dt
        self.t_last, self.n_last = now, nodes
        self.sink((self.pres_id, nodes, self.budget, now - self.t0, rate))


def _fmt_hb(sample):
    pres_id, nodes, budget, elapsed, rate = sample
    eta = (budget - nodes) / rate if rate > 0 else 0.0
    return (f"pres {pres_id}: {nodes:,}/{budget:,} ({nodes / budget:.0%}) | "
            f"{rate:,.0f} nodes/s | {elapsed:.0f}s elapsed, ETA {eta:.0f}s")


def _hb_monitor(q, stop_evt, every):
    """Parent-side drain: print one aggregate block per ``every`` seconds."""
    import queue as _queue

    live = {}          # pres_id -> (sample, arrival_time)
    last_print = time.time()
    while not stop_evt.is_set():
        try:
            sample = q.get(timeout=0.2)
            if sample[1] is None:            # worker finished this presentation
                live.pop(sample[0], None)
            else:
                live[sample[0]] = (sample, time.time())
        except _queue.Empty:
            pass
        now = time.time()
        if now - last_print < every:
            continue
        # Backstop for a worker that died without sending its done-sentinel:
        # otherwise its last rate would be summed into `agg` forever.
        live = {p: v for p, v in live.items() if now - v[1] <= 2 * every}
        if live:
            samples = [v[0] for v in live.values()]
            agg = sum(s[4] for s in samples)
            print(f"    [hb] {len(samples)} solving | agg {agg:,.0f} nodes/s",
                  flush=True)
            for s in sorted(samples):
                print(f"         {_fmt_hb(s)}", flush=True)
        last_print = now


def _solve_one(job):
    """Top-level (picklable) worker: run one presentation, return its stats."""
    pres_id, r1, r2, node_budget, mrl, cyc, high, hb_s = job
    progress = None
    if hb_s > 0:
        # In a pool worker, hand samples to the parent; serially, print directly.
        sink = (_HB_Q.put_nowait if _HB_Q is not None
                else (lambda s: print(f"    [hb] {_fmt_hb(s)}", flush=True)))
        progress = _Heartbeat(pres_id, node_budget, hb_s, sink)
    t0 = time.time()
    try:
        stats = greedy_search(r1, r2, node_budget, max_relator_length=mrl,
                              cyclic_reduce=cyc, high_speedup=high, progress=progress)
    finally:
        if progress is not None and _HB_Q is not None:
            # Tell the monitor to stop counting this presentation's last rate
            # into the aggregate; the worker moves on to the next job.
            _HB_Q.put_nowait((pres_id, None))
    return pres_id, r1, r2, stats, time.time() - t0


def _path_payload(cfg, stats):
    """The path fields to store for a solved presentation, per PATH_FORMAT.

    "moves" (default) stores the compact Definition 2.1 tuples (replay with
    experiments.search.greedy_baseline.moves_to_states); "strings" stores the
    [r1, r2] state list; "both" stores each under its own key.
    """
    fmt = cfg.get("PATH_FORMAT", "moves")
    payload = {}
    if fmt in ("moves", "both"):
        payload["path_moves"] = stats["path_moves"]
    if fmt in ("strings", "both"):
        payload["path"] = stats["path"]
    return payload


def _build_row(cfg, pres_id, r1, r2, node_budget, stats, elapsed):
    row = {
        "pres_id": pres_id,
        "r1": r1,
        "r2": r2,
        "node_budget": node_budget,
        "max_relator_length_cap": cfg["MAX_RELATOR_LENGTH"],
        "cyclic_reduce": cfg["CYCLIC_REDUCE"],
        "nodes_explored": stats["nodes_explored"],
        "solved": stats["solved"],
        "path_length": stats["path_length"],
    }
    if cfg["use_min_relator"]:
        row["min_relator_length"] = stats["min_relator_length"]
        row["min_relator"] = stats["min_relator"]
    if cfg["use_max_relator"]:
        row["max_relator_length"] = stats["max_relator_length"]
        row["max_relator"] = stats["max_relator"]
    if cfg["use_max_relator_expanded"]:
        row["max_relator_length_expanded"] = stats["max_relator_length_expanded"]
        row["max_relator_expanded"] = stats["max_relator_expanded"]
    if cfg["use_time"]:
        row["time_seconds"] = round(elapsed, 4)
    if cfg["use_path"] and not cfg["PATH_IN_SEPARATE_FILE"] and stats["solved"]:
        row.update(_path_payload(cfg, stats))
    return row


def run_dataset(cfg, node_budget):
    """Run the baseline greedy over the dataset at one node budget.

    Writes one jsonl per budget (crash-safe: flush every row). Resumable via
    the pres_id set already present in the output file.
    """
    import time

    cfg = {**DEFAULT_CONFIG, **cfg}
    presentations = list(load_dataset(cfg["DATASET"], cfg["SUBSET"]))
    n_pres = len(presentations)
    out_path, paths_path, date, stem = _resolve_paths(cfg, node_budget, n_pres)

    if cfg["RESUME"]:
        done, n_seen, n_solved = _read_done(out_path)
    else:
        done, n_seen, n_solved = set(), 0, 0

    run = None
    table = None
    if cfg["USE_WANDB"]:
        import wandb
        group = cfg["WANDB_GROUP"] or f"greedy_baseline_{date}"
        # Same collision-safe identity as the jsonl file (W&B ids allow these chars).
        run_id = stem
        run = wandb.init(
            entity=cfg["WANDB_ENTITY"] or None, project=cfg["WANDB_PROJECT"],
            id=run_id, name=run_id, resume="allow",
            group=group, job_type="greedy_baseline", mode=cfg["WANDB_MODE"],
            config={
                "node_budget": node_budget,
                "max_relator_length": cfg["MAX_RELATOR_LENGTH"],
                "cyclic_reduce": cfg["CYCLIC_REDUCE"],
                "dataset": cfg["DATASET"], "n_pres": n_pres,
                "subset": str(cfg["SUBSET"]),
            },
        )
        # Give the running solve_rate its own x-axis (pres_id) instead of the
        # global step. On a resumed run the global step is already past the last
        # pres_id (finish-time Table/panel logs bumped it), so logging
        # step=pres_id would be rejected as non-monotonic ("step N < current").
        run.define_metric("pres_id")
        run.define_metric("solve_rate", step_metric="pres_id")
        table = wandb.Table(columns=[
            "pres_id", "r1", "r2", "node_budget", "max_relator_length_cap",
            "cyclic_reduce", "nodes_explored", "solved", "path_length",
            "min_relator_length", "max_relator_length",
        ])
        # Rebuild the Table from any already-written rows (resume).
        if os.path.exists(out_path):
            with open(out_path) as f:
                for ln in f:
                    ln = ln.strip()
                    if ln:
                        _add_table_row(table, json.loads(ln))

    todo = [(pid, r1, r2) for (pid, r1, r2) in presentations if pid not in done]
    n_todo = len(todo)
    every = max(1, int(cfg["PROGRESS_EVERY"]))
    print(f"=== budget={node_budget} | {n_pres} presentations | "
          f"{len(done)} already done, {n_todo} to run | -> {out_path}",
          flush=True)
    if n_todo == 0:
        print("    nothing to do (all done). ", flush=True)

    high = bool(cfg["HIGH_SPEEDUP"])
    mrl = cfg["MAX_RELATOR_LENGTH"]
    cyc = cfg["CYCLIC_REDUCE"]
    hb_s = float(cfg.get("HEARTBEAT_EVERY_S", 0) or 0)
    jobs = [(pid, a, b, node_budget, mrl, cyc, high, hb_s) for pid, a, b in todo]
    n_workers = _auto_workers(cfg) if high else 1
    if high:
        print(f"    HIGH_SPEEDUP: {n_workers} worker(s) | {_total_ram_gb():.0f} GB RAM"
              f" | ~{cfg['GB_PER_PRES']} GB/presentation", flush=True)
    if hb_s > 0:
        print(f"    heartbeat: nodes/s every {hb_s:g}s", flush=True)

    total_time = 0.0
    t_start = time.time()
    processed = 0
    out_f = open(out_path, "a")
    paths_f = open(paths_path, "a") if cfg["PATH_IN_SEPARATE_FILE"] else None
    pool = None

    def _emit(pres_id, r1, r2, stats, elapsed, recovered=False):
        row = _build_row(cfg, pres_id, r1, r2, node_budget, stats, elapsed)
        if recovered:
            row["path_recovered"] = True
        out_f.write(json.dumps(row) + "\n")
        out_f.flush()
        if cfg["PATH_IN_SEPARATE_FILE"] and cfg["use_path"] and stats["solved"]:
            path_row = {"pres_id": pres_id, "r1": r1, "r2": r2}
            path_row.update(_path_payload(cfg, stats))
            paths_f.write(json.dumps(path_row) + "\n")
            paths_f.flush()
        if run is not None:
            _add_table_row(table, row)

    # Heavy mode drops path tracking, so a solved presentation is re-solved by
    # the normal solver AFTER the pool is torn down (it needs the full RAM).
    deferred = []
    hb_thread = None
    hb_stop = None
    try:
        if high and n_workers > 1:
            import multiprocessing as mp
            hb_q = mp.Queue() if hb_s > 0 else None
            pool = mp.Pool(n_workers, initializer=_init_worker, initargs=(hb_q,))
            if hb_q is not None:
                import threading
                hb_stop = threading.Event()
                hb_thread = threading.Thread(
                    target=_hb_monitor, args=(hb_q, hb_stop, hb_s), daemon=True)
                hb_thread.start()
            results = pool.imap_unordered(_solve_one, jobs)
        else:
            results = (_solve_one(j) for j in jobs)

        for pres_id, r1, r2, stats, elapsed in results:
            total_time += elapsed
            if high and stats["solved"]:
                deferred.append((pres_id, r1, r2))   # row written after recovery
            else:
                _emit(pres_id, r1, r2, stats, elapsed)

            n_seen += 1
            n_solved += int(stats["solved"])
            processed += 1
            if run is not None:
                run.log({"pres_id": pres_id, "solve_rate": n_solved / max(n_seen, 1)})

            if processed % every == 0 or processed == n_todo:
                wall = time.time() - t_start
                rate = processed / wall if wall > 0 else 0.0
                eta = (n_todo - processed) / rate if rate > 0 else 0.0
                nps = stats["nodes_explored"] / elapsed if elapsed > 0 else 0.0
                print(f"    [{node_budget}] {processed}/{n_todo} | "
                      f"solved {n_solved}/{n_seen} ({n_solved / max(n_seen, 1):.1%}) | "
                      f"pres {pres_id}: {'ok' if stats['solved'] else 'unsolved'} "
                      f"nodes={stats['nodes_explored']} ({nps:,.0f} nodes/s) | "
                      f"{wall:.0f}s elapsed, ETA {eta:.0f}s ({rate:.1f}/s)",
                      flush=True)

        if pool is not None:
            pool.close()
            pool.join()
            pool = None

        for pres_id, r1, r2 in deferred:
            print(f"    recovering path for pres {pres_id} (normal solver)...", flush=True)
            t0 = time.time()
            # Runs in the parent (the pool is torn down), so print directly —
            # this is the slow normal-mode solve, the one worth watching.
            recover_hb = None
            if hb_s > 0:
                recover_hb = _Heartbeat(
                    pres_id, node_budget, hb_s,
                    lambda s: print(f"    [hb] {_fmt_hb(s)}", flush=True))
            stats = greedy_search(r1, r2, node_budget, max_relator_length=mrl,
                                  cyclic_reduce=cyc, high_speedup=False,
                                  progress=recover_hb)
            _emit(pres_id, r1, r2, stats, time.time() - t0, recovered=True)
    finally:
        if hb_stop is not None:
            hb_stop.set()
            hb_thread.join(timeout=2)
        if pool is not None:
            pool.terminate()
            pool.join()
        out_f.close()
        if paths_f is not None:
            paths_f.close()

    if run is not None:
        _finish_wandb(run, table, out_path, paths_path, run_id,
                      n_seen, n_solved, total_time, cfg)

    print(f"[{out_path}] {n_seen} presentations, {n_solved} solved "
          f"({n_solved / max(n_seen, 1):.1%}).")
    return out_path


def _add_table_row(table, row):
    table.add_data(
        row["pres_id"], row["r1"], row["r2"], row["node_budget"],
        row.get("max_relator_length_cap"), row.get("cyclic_reduce"),
        row["nodes_explored"], row["solved"], row["path_length"],
        row.get("min_relator_length"), row.get("max_relator_length"),
    )


def _finish_wandb(run, table, out_path, paths_path, run_id,
                  n_seen, n_solved, total_time, cfg):
    import statistics
    import wandb

    # Recompute headline aggregates from the full jsonl (source of truth).
    nodes_all, nodes_solved, paths_solved = [], [], []
    scatter_pts = []  # (nodes_explored, path_length) for solved presentations
    with open(out_path) as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            row = json.loads(ln)
            nodes_all.append(row["nodes_explored"])
            if row["solved"]:
                nodes_solved.append(row["nodes_explored"])
                if row["path_length"] is not None:
                    paths_solved.append(row["path_length"])
                    scatter_pts.append([row["nodes_explored"], row["path_length"]])

    def _mean(xs):
        return statistics.fmean(xs) if xs else None

    def _median(xs):
        return statistics.median(xs) if xs else None

    run.summary["n_pres"] = n_seen
    run.summary["n_solved"] = n_solved
    run.summary["solve_rate"] = n_solved / max(n_seen, 1)
    run.summary["nodes_explored_mean"] = _mean(nodes_all)
    run.summary["nodes_explored_solved_mean"] = _mean(nodes_solved)
    run.summary["path_length_mean"] = _mean(paths_solved)
    run.summary["path_length_median"] = _median(paths_solved)
    run.summary["total_time_s"] = round(total_time, 2)

    run.log({"results": table})

    # Auto-rendered graphs (the two headline metrics as distributions).
    panels = {}
    if nodes_all:
        panels["nodes_explored_hist"] = wandb.Histogram(nodes_all)
    if paths_solved:
        panels["path_length_hist"] = wandb.Histogram(paths_solved)
    if scatter_pts:
        _sc = wandb.Table(data=scatter_pts, columns=["nodes_explored", "path_length"])
        panels["nodes_vs_path"] = wandb.plot.scatter(
            _sc, "nodes_explored", "path_length",
            title="nodes explored vs path length (solved)")
    if panels:
        run.log(panels)

    art = wandb.Artifact(run_id, type="results")
    art.add_file(out_path)
    if cfg["PATH_IN_SEPARATE_FILE"] and os.path.exists(paths_path):
        art.add_file(paths_path)
    run.log_artifact(art)
    run.finish()
