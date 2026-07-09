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

from experiments import wandb_tracking
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
    # None = OS default (fork on Linux/Colab). A child forked from a process that
    # wandb.init() has made multi-threaded can deadlock on an inherited lock; the
    # parent-side numba warm-up should prevent that, but "forkserver" (or "spawn")
    # forks from a clean single-threaded process and sidesteps it entirely.
    "MP_START_METHOD": None,

    # output
    "MOUNT_DRIVE": False,
    "DRIVE_OUT_DIR": "/content/drive/MyDrive/acsolverx_results/greedy_baseline",
    "LOCAL_OUT_DIR": "results/greedy_baseline",

    # W&B. None of these change the search, so none of them enter _run_prefix.
    "USE_WANDB": False,
    "WANDB_ENTITY": "avigyapaudel045-aisc",   # writable team entity (org-managed acct; None = account default)
    "WANDB_PROJECT": "acsolver",
    "WANDB_MODE": "online",
    # Default group is the SWEEP identity: {dataset}-mrl{cap}-{cyc}-{subset}.
    # Runs inside a group differ only by node_budget, so the group view compares
    # budgets directly. Override only to force two sweeps into one section.
    "WANDB_GROUP": None,
    "WANDB_JOB_TYPE": None,          # default "greedy_baseline" (the algorithm family)
    "WANDB_RUN_NAME": None,          # default "50k · ms640_solved · mrl24 · cyc"
    "WANDB_TAGS": None,              # extra tags on top of the derived ones
    "WANDB_NOTES": None,
    # Solution paths replayed at finish to draw |r1|+|r2| along the path (the
    # two humps). 0 = off; this is the only finish-time step that costs work.
    "WANDB_PATH_PROFILES": 8,        # how many paths get their own line
    "WANDB_PATH_SAMPLE": 200,        # how many get replayed for the hump stats
    "WANDB_LOG_PRES_SCALARS": True,  # per-presentation pres/* metrics

    "PROGRESS_EVERY": 10,            # print a status line every N processed presentations

    # Live nodes/s while a single presentation is still running (a 1M-node solve
    # takes minutes, so PROGRESS_EVERY says nothing until it finishes). 0 = off.
    # Result-neutral, so it is deliberately absent from _run_prefix.
    "HEARTBEAT_EVERY_S": 0,
    # Diagnose a silent heartbeat: prints a [hb-dbg] line every 5s (messages
    # received, queue depth, presentations live) and emits the first sample on
    # the very first 1024-node tick instead of waiting ~10s.
    "HEARTBEAT_DEBUG": False,
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
    ``interval`` seconds, so the per-node cost is a modulo and a clock read.

    The FIRST sample is emitted after at most ``first_after`` seconds rather
    than a full interval: with a 90 s interval, waiting a full period before
    saying anything is indistinguishable from a hang (and the worker's clock
    starts before numba JIT, which eats the first seconds anyway).
    """

    def __init__(self, pres_id, budget, interval, sink, first_after=10.0):
        self.pres_id, self.budget, self.sink = pres_id, budget, sink
        self.interval = interval
        self.t0 = self.t_last = time.time()
        self.next_at = self.t0 + min(first_after, interval)
        self.n_last = 0

    def __call__(self, nodes):
        now = time.time()
        if now < self.next_at:
            return
        dt = now - self.t_last
        rate = (nodes - self.n_last) / dt if dt > 0 else 0.0
        self.t_last, self.n_last = now, nodes
        self.next_at = now + self.interval
        self.sink((self.pres_id, nodes, self.budget, now - self.t0, rate))


def _fmt_hb(sample):
    pres_id, nodes, budget, elapsed, rate = sample
    eta = (budget - nodes) / rate if rate > 0 else 0.0
    return (f"pres {pres_id}: {nodes:,}/{budget:,} ({nodes / budget:.0%}) | "
            f"{rate:,.0f} nodes/s | {elapsed:.0f}s elapsed, ETA {eta:.0f}s")


class _HbPrinter:
    """Drains the worker->parent heartbeat queue and prints, from the MAIN thread.

    A background thread's stdout is not reliably attributed to the running cell
    in Colab, so all printing happens on the thread that runs ``run_dataset``.

    Messages are explicitly tagged so a silent heartbeat is diagnosable:
      ``("start", pres_id, worker_pid)``  worker picked up a presentation
      ``("sample", pres_id, nodes, budget, elapsed, rate)``
      ``("done", pres_id)``               stop counting its rate into ``agg``
    """

    def __init__(self, every, debug=False):
        self.every, self.debug = every, debug
        self.live = {}          # pres_id -> (sample, arrival_time)
        self.last_print = 0.0   # epoch 0 => first sample to arrive prints at once
        self.last_dbg = 0.0
        self.t0 = time.time()
        self.n_msgs = 0
        self.n_samples = 0
        self.warned = False

    def drain(self, q):
        import queue as _queue

        while True:
            try:
                msg = q.get_nowait()
            except _queue.Empty:
                break
            self.n_msgs += 1
            kind = msg[0]
            if kind == "start":
                print(f"    [hb] pres {msg[1]} started (worker pid {msg[2]})",
                      flush=True)
            elif kind == "done":
                self.live.pop(msg[1], None)
            else:
                self.n_samples += 1
                self.live[msg[1]] = (msg[1:], time.time())

        now = time.time()
        # Workers announced themselves but none has ever completed 1024 nodes:
        # they are blocked inside greedy_search. Point at the stack dumps.
        if (self.debug and not self.warned and self.n_samples == 0
                and self.n_msgs > 0 and now - self.t0 > 50):
            self.warned = True
            print("    [hb-dbg] workers started but produced NO progress tick in 50s"
                  " -- they are blocked inside greedy_search.", flush=True)
            print("    [hb-dbg] their Python stacks were dumped; run:"
                  "  !cat hb_stack_*.txt", flush=True)
        if self.debug and now - self.last_dbg >= 5.0:
            self.last_dbg = now
            try:
                qsize = q.qsize()
            except NotImplementedError:      # macOS has no sem_getvalue()
                qsize = -1
            print(f"    [hb-dbg] t={now - self.t0:5.1f}s  msgs_received={self.n_msgs}"
                  f"  qsize={qsize}  live={len(self.live)}", flush=True)

        if now - self.last_print < self.every:
            return
        # Backstop for a worker that died without sending its done-sentinel:
        # otherwise its last rate would be summed into `agg` forever.
        for pid in [p for p, v in self.live.items() if now - v[1] > 2 * self.every]:
            self.live.pop(pid)
        if not self.live:
            # Nothing to say yet (workers still starting / JIT-compiling). Do NOT
            # advance last_print, or this empty tick costs a whole `every` period
            # before the first block appears.
            return
        samples = [v[0] for v in self.live.values()]
        agg = sum(s[4] for s in samples)
        print(f"    [hb] {len(samples)} solving | agg {agg:,.0f} nodes/s", flush=True)
        for s in sorted(samples):
            print(f"         {_fmt_hb(s)}", flush=True)
        self.last_print = now


def _iter_with_heartbeat(it, q, every, debug=False):
    """Yield pool results, draining the heartbeat queue while they are pending."""
    import multiprocessing as mp

    if q is None:
        yield from it
        return
    printer = _HbPrinter(every, debug)
    while True:
        try:
            item = it.next(timeout=0.5)
        except mp.TimeoutError:
            printer.drain(q)
            continue
        except StopIteration:
            return
        printer.drain(q)
        yield item


def _solve_one(job):
    """Top-level (picklable) worker: run one presentation, return its stats."""
    pres_id, r1, r2, node_budget, mrl, cyc, high, hb_s, hb_dbg = job

    # Watchdog: if this worker is still stuck 40s from now with no progress tick,
    # dump its Python stack to a file. A worker's stderr is not visible in a
    # notebook, so a file is the only way to see WHERE a hang actually lives.
    dbg_f = None
    if hb_dbg:
        import faulthandler
        dbg_f = open(os.path.abspath(f"hb_stack_{os.getpid()}.txt"), "w")
        faulthandler.dump_traceback_later(40, repeat=True, file=dbg_f)

    def _cancel_watchdog():
        if dbg_f is not None:
            import faulthandler
            faulthandler.cancel_dump_traceback_later()

    progress = None
    if hb_s > 0:
        if _HB_Q is not None:
            # Announce liveness BEFORE the first numba call: proves the worker and
            # the queue are alive even though no sample exists yet.
            _HB_Q.put_nowait(("start", pres_id, os.getpid()))
            seen_first = []

            def sink(s):
                if not seen_first:      # a tick proves the worker is running
                    seen_first.append(True)
                    _cancel_watchdog()
                _HB_Q.put_nowait(("sample",) + s)

            # The parent prints every hb_s, so sample twice as often or its
            # aggregate would be summed from rates up to hb_s seconds old.
            interval = max(1.0, hb_s / 2)
        else:
            # Serial: this IS the printer, so sample at exactly the asked cadence.
            sink, interval = (lambda s: print(f"    [hb] {_fmt_hb(s)}", flush=True)), hb_s
        # Debug: emit on the very first 1024-node tick (its rate includes JIT).
        progress = _Heartbeat(pres_id, node_budget, interval, sink,
                              first_after=0.0 if hb_dbg else 10.0)
    t0 = time.time()
    try:
        stats = greedy_search(r1, r2, node_budget, max_relator_length=mrl,
                              cyclic_reduce=cyc, high_speedup=high, progress=progress)
    finally:
        _cancel_watchdog()
        if dbg_f is not None:
            dbg_f.close()
        if progress is not None and _HB_Q is not None:
            # Tell the printer to stop counting this presentation's last rate
            # into the aggregate; the worker moves on to the next job.
            _HB_Q.put_nowait(("done", pres_id))
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
    out_path, paths_path, _date, stem = _resolve_paths(cfg, node_budget, n_pres)

    if cfg["RESUME"]:
        done, n_seen, n_solved = _read_done(out_path)
    else:
        done, n_seen, n_solved = set(), 0, 0

    todo_ids = [pid for (pid, _r1, _r2) in presentations if pid not in done]

    run = None
    logger = None
    run_id = stem   # same collision-safe identity as the jsonl (W&B ids allow it)
    if cfg["USE_WANDB"]:
        run = wandb_tracking.init_run(
            cfg, node_budget, n_pres, run_id,
            _run_prefix(cfg, node_budget, n_pres), _subset_tag(cfg["SUBSET"]))
        # Rebuild the Table from any already-written rows, and seed the
        # cumulative counters so a resumed run's live curves stay continuous.
        prior = wandb_tracking.read_jsonl(out_path)
        logger = wandb_tracking.LiveLogger(
            run, cfg, node_budget, n_todo=len(todo_ids), n_seen=n_seen,
            n_solved=n_solved,
            cum_nodes=sum(r.get("nodes_explored") or 0 for r in prior))
        for prior_row in prior:
            logger.add_existing_row(prior_row)

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
    hb_dbg = bool(cfg.get("HEARTBEAT_DEBUG", False))
    jobs = [(pid, a, b, node_budget, mrl, cyc, high, hb_s, hb_dbg)
            for pid, a, b in todo]
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
        if logger is not None:
            logger.on_row(row)

    # Heavy mode drops path tracking, so a solved presentation is re-solved by
    # the normal solver AFTER the pool is torn down (it needs the full RAM).
    deferred = []
    try:
        if high and n_workers > 1:
            import multiprocessing as mp
            # Compile the numba kernels HERE, before forking. Two reasons:
            #  - a forked child inherits the compiled code, so 4 workers no longer
            #    each pay a cold compile;
            #  - wandb.init() has already spawned threads in this process, and a
            #    child forked from a threaded parent can deadlock inside numba's
            #    compiler on a lock that was held at fork. Warming here means the
            #    child never enters the compiler at all.
            t_warm = time.time()
            print("    warming numba in the parent (forked workers inherit it)...",
                  flush=True)
            _w1, _w2 = todo[0][1], todo[0][2]
            greedy_search(_w1, _w2, 2, max_relator_length=mrl,
                          cyclic_reduce=cyc, high_speedup=True)
            print(f"    numba warm in {time.time() - t_warm:.1f}s", flush=True)

            ctx = mp.get_context(cfg.get("MP_START_METHOD") or None)
            hb_q = ctx.Queue() if hb_s > 0 else None
            pool = ctx.Pool(n_workers, initializer=_init_worker, initargs=(hb_q,))
            if hb_q is not None:
                print(f"    [hb] armed: {n_workers} worker(s); first sample after "
                      f"numba JIT + ~{0 if hb_dbg else 10}s"
                      f"{'  [DEBUG]' if hb_dbg else ''}", flush=True)
            results = _iter_with_heartbeat(
                pool.imap_unordered(_solve_one, jobs), hb_q, hb_s, hb_dbg)
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
            if logger is not None:
                # Cumulative run/* counters advance HERE, once per worker result.
                # A heavy-mode solved presentation is re-solved later to recover
                # its path; accumulating again there would double-count its nodes.
                logger.on_result(stats)

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
        if pool is not None:
            pool.terminate()
            pool.join()
        out_f.close()
        if paths_f is not None:
            paths_f.close()

    if run is not None:
        wandb_tracking.finish_run(run, logger, out_path, paths_path, run_id,
                                  n_seen, n_solved, total_time, cfg, node_budget)

    print(f"[{out_path}] {n_seen} presentations, {n_solved} solved "
          f"({n_solved / max(n_seen, 1):.1%}).")
    return out_path
