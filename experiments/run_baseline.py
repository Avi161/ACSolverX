"""Baseline greedy pipeline runner — data load, jsonl (resumable), W&B.

CPU + numba only. Run from the ACSolverX repo root (data paths are relative).
The heavy lifting is in ``experiments.search.greedy_baseline``; this module is
just the experiment harness around it.
"""

import ast
import hashlib
import json
import os
import shutil
import sys
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
    "N_WORKERS": 0,                  # 0 = auto (bounded by usable cores AND RAM)
    # "auto" = size each search from the node budget (~70 states/node x 220 B,
    # both measured). A positive number pins it instead. The old fixed 9.0 was
    # calibrated at 1M/mrl=48 yet applied at EVERY budget: a 50k run needs <1 GB
    # but was provisioned as if it needed 9, and 1M actually needs ~15, not 9.
    "GB_PER_PRES": "auto",
    # None = OS default (fork on Linux/Colab). A child forked from a process that
    # wandb.init() has made multi-threaded can deadlock on an inherited lock; the
    # parent-side numba warm-up should prevent that, but "forkserver" (or "spawn")
    # forks from a clean single-threaded process and sidesteps it entirely.
    "MP_START_METHOD": None,

    # output
    "MOUNT_DRIVE": False,
    "DRIVE_OUT_DIR": "/content/drive/MyDrive/acsolverx_results/greedy_baseline",
    "LOCAL_OUT_DIR": "results/greedy_baseline",

    # Durable output. When the output lands on a network mount (Drive), rows are
    # appended to a local staging copy and the mount receives a whole-file copy.
    # Result-neutral, so neither key enters _run_prefix.
    "STAGE_DIR": None,          # None -> "<LOCAL_OUT_DIR>/_stage"
    "MIRROR_EVERY_S": 60,       # at most one mirror per N seconds; always at the end

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


def _repair_jsonl(path):
    """Drop a half-written trailing line, returning the number of bytes removed.

    Rows are appended as ``json.dumps(row) + "\\n"`` and flushed, so a process
    killed mid-write (a Colab disconnect, an OOM kill, Ctrl-C) can only ever
    damage the LAST line. Repairing it here, before anything opens the file for
    append, is what makes the damage recoverable: left in place, the stub has no
    newline, so the next appended row is concatenated onto it and a *truncated
    final* line becomes a *corrupt interior* line that no later read can undo.

    Truncating back to the last newline can discard one complete row whose
    newline was lost. That is safe and deliberate: the row is simply absent from
    ``done``, so resume re-runs that one presentation. Losing a search is
    cheaper than guessing whether a partial line was complete.
    """
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return 0
    with open(path, "rb+") as f:
        f.seek(-1, os.SEEK_END)
        if f.read(1) == b"\n":
            return 0                      # last row is intact
        size = f.tell()
        keep = size
        while keep > 0:                   # walk back to the last completed row
            f.seek(keep - 1)
            if f.read(1) == b"\n":
                break
            keep -= 1
        f.truncate(keep)
    dropped = size - keep
    print(f"    repaired {os.path.basename(path)}: dropped a {dropped}-byte "
          f"truncated final line (a crash mid-write); that presentation will "
          f"be re-run", flush=True)
    return dropped


def _read_done(out_path):
    """(done_ids, n_seen, n_solved) reconstructed from an existing jsonl.

    Tolerates an unparseable FINAL line so that reading an unrepaired file (one
    `_repair_jsonl` has not been run over) still resumes rather than crashing.
    An unparseable line anywhere else is real corruption -- not a torn write --
    and is raised rather than silently skipped, which would drop a presentation
    from ``done`` and silently re-run it.
    """
    done, n_seen, n_solved = set(), 0, 0
    if not os.path.exists(out_path):
        return done, n_seen, n_solved
    with open(out_path, "r") as f:
        lines = [ln.strip() for ln in f]
    for i, ln in enumerate(lines):
        if not ln:
            continue
        try:
            row = json.loads(ln)
        except ValueError:
            if i == len(lines) - 1:
                print(f"    WARNING: ignoring a truncated final line in "
                      f"{os.path.basename(out_path)}", flush=True)
                break
            raise
        done.add(row["pres_id"])
        n_seen += 1
        n_solved += int(bool(row.get("solved")))
    return done, n_seen, n_solved


def _read_pending(out_path):
    """pres_ids whose SEARCH finished and is durable, but whose path was never
    recovered (``path_pending``).

    These are already in ``_read_done``'s ``done`` set, so they are never
    re-searched; only their comparatively cheap path recovery is retried.
    """
    pending = set()
    if os.path.exists(out_path):
        with open(out_path, "r") as f:
            for ln in f:
                ln = ln.strip()
                if not ln:
                    continue
                row = json.loads(ln)
                if row.get("path_pending"):
                    pending.add(row["pres_id"])
    return pending


def _read_mem_pending(out_path):
    """pres_ids the memory guard stopped, whose serial retry never ran.

    Written the instant the guard fires, so a session that dies before the pool
    drains still records which presentations tripped. Without this the tripped id
    is absent from the jsonl, resume feeds it back into the *pool*, it trips
    again on the same 1/n share, and the presentation is re-searched forever —
    which is exactly what a 29-hour pool on a 12-hour Colab session guarantees.

    Being on disk puts the id in ``done``, so resume never re-searches it in the
    pool; it is routed to the serial retry instead, where it gets the whole
    machine. A ``mem_abort`` row *without* this flag is terminal: the search does
    not fit here even alone, and re-running it would only waste the budget again.
    """
    pending = set()
    if os.path.exists(out_path):
        with open(out_path, "r") as f:
            for ln in f:
                ln = ln.strip()
                if not ln:
                    continue
                row = json.loads(ln)
                if row.get("mem_abort_pending"):
                    pending.add(row["pres_id"])
    return pending


def _report_lost_rows(out_path, done_before, todo_ids):
    """pres_ids the runner wrote but that are not on disk. Returns them, sorted.

    ``_emit`` writes and fsyncs every row, so after a clean run every id that was
    already done plus every id in ``todo`` must be present. This catches the one
    failure the code cannot prevent: a filesystem that accepts a flushed, fsynced
    write and drops it anyway. Colab's Google Drive FUSE mount did exactly that —
    a 1M pooled run silently lost two presentations, and because they stayed
    absent from ``done`` every resume re-searched them and lost them again.

    A warning, never an exception: a 30-hour run must not die at the finish line
    over rows the caller can simply re-run.
    """
    expected = set(done_before) | set(todo_ids)
    on_disk, _, _ = _read_done(out_path)
    lost = sorted(expected - on_disk)
    if lost:
        print(f"    !! {len(lost)} row(s) were written but are NOT on disk: {lost}",
              flush=True)
        print(f"       {out_path} dropped them after a successful write+fsync. "
              f"Write to local disk and copy to the network share instead; "
              f"RESUME=True re-runs only these.", flush=True)
    return lost


def _read_paths_done(paths_path):
    """pres_ids already present in the *_paths.jsonl (keeps appends idempotent)."""
    ids = set()
    if os.path.exists(paths_path):
        with open(paths_path, "r") as f:
            for ln in f:
                ln = ln.strip()
                if ln:
                    ids.add(json.loads(ln)["pres_id"])
    return ids


# --- durable output ---------------------------------------------------------
# Local disk is authoritative; a network mount only ever receives a whole-file
# copy. Colab's Google Drive FUSE mount accepted flushed, appended rows from a
# long-idle handle and silently dropped them — a 1M pooled run lost two
# presentations that way, and because the ids never entered ``done`` every resume
# re-searched them and lost them again. The five SERIAL ms640 files on that same
# mount are complete, so the mount is fine with short writes and fine with
# whole-file replacement; it is the long-idle append handle it cannot keep.
#
# None of this changes what a search computes, so none of it enters _run_prefix.

_REMOTE_PREFIXES = ("/content/drive/",)


def _is_remote(path):
    """True for a path on a mount whose flushed appends may not persist."""
    return os.path.abspath(path).startswith(_REMOTE_PREFIXES)


def _n_lines(path):
    """Line count, or -1 when the file does not exist (so it always loses)."""
    if not os.path.exists(path):
        return -1
    with open(path, "rb") as f:
        return sum(1 for _ in f)


def _copy_file(src, dst):
    """Whole-file copy, fsynced, then swapped in atomically."""
    os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
    tmp = dst + ".tmp"
    with open(src, "rb") as s, open(tmp, "wb") as d:
        shutil.copyfileobj(s, d)
        _persist(d)
    os.replace(tmp, dst)


def _seed_stage(local, remote):
    """Pull the mirror down onto local disk.

    A resumed run lands on a *fresh* Colab VM: the local staging file is gone and
    the mirror is the only record. Seed from whichever side has more rows, so a
    mid-session re-run never discards work the mirror has not caught up with.
    """
    if _n_lines(remote) <= _n_lines(local):
        return
    _copy_file(remote, local)
    print(f"    seeded {os.path.basename(local)} from the mirror "
          f"({_n_lines(local)} rows)", flush=True)


def _persist(f):
    """flush() hands bytes to the OS; fsync() makes the filesystem keep them.

    On a network filesystem the difference is the whole bug. Colab's Google Drive
    FUSE mount accepted flushed rows and then dropped them: a 1M-budget pooled run
    silently lost the two presentations whose rows were written after the handle
    had sat idle ~17 minutes, while the serial ms640 runs — appending a row every
    couple of seconds — never lost one. Rows are minutes apart at production
    budgets, so an fsync per row costs nothing measurable.

    An fsync that the filesystem refuses is not worth aborting a 30-hour run over;
    ``_report_lost_rows`` is the backstop that notices if data went missing.
    """
    f.flush()
    try:
        os.fsync(f.fileno())
    except OSError:
        pass


def _update_row(out_path, pres_id, new_row):
    """Replace the row for ``pres_id`` in place, atomically. Returns whether a
    row was actually found and replaced.

    The jsonl is one row per pres_id (every consumer assumes it), so a recovered
    path fills in the existing row instead of appending a second one. Written to
    a temp file and ``os.replace``d, so a crash leaves the previous, still-valid
    file untouched — the row simply stays ``path_pending`` and is retried.

    The return value is load-bearing for ``_finalize``: it replaces a placeholder
    while holding a result that exists nowhere else, so a silent no-op here would
    discard a multi-hour search. Callers that merely enrich a row can ignore it.
    """
    tmp = out_path + ".tmp"
    found = False
    with open(out_path, "r") as src, open(tmp, "w") as dst:
        for ln in src:
            s = ln.strip()
            if not s:
                continue
            row = json.loads(s)
            if row["pres_id"] == pres_id:
                row, found = new_row, True
            dst.write(json.dumps(row) + "\n")
        _persist(dst)
    os.replace(tmp, out_path)
    return found


# --- resource detection + memory budgeting (HIGH_SPEEDUP path only) --------
# Everything below is result-neutral: it decides HOW MANY searches run at once,
# never what any one search computes. None of it belongs in _run_prefix.

# Bytes of process memory per DISCOVERED state, for the heavy solver. Each state
# costs a packed-bytes key + a `visited` set entry + a `(total, depth, key)` heap
# tuple + its list slot. Measured by building exactly those structures at real key
# lengths: 214 B/state, FLAT from 500k to 8M entries (marginal 214.1 -> 214.5), and
# it agrees with the 213 B/state seen from real RSS on Colab. 220 leaves a little
# for allocator fragmentation.
# NB a shallow search reads lower (~185 B) only because its relators, hence its
# keys, are shorter -- calibrate at the key lengths the deep search actually holds.
_BYTES_PER_STATE = 220

# DISCOVERED states per node popped. Measured on ms_reps_unsolved (heavy solver):
#     budget   25k    50k   100k   200k   400k   600k     1M
#     mrl=24   67.1   64.9   69.8   50.7   42.0      -   29.7
#     mrl=48   67.1   64.9   69.8   70.5   63.8   61.6      -
# Fitting discovered = A*budget^p on the mrl=48 row (six points, 25k..600k) gives
# A=82.9, p=0.981 (<=6.7% error everywhere). mrl=24 bends far below it (p=0.772)
# once the cap starts pruning, and the two rows are identical until the cap binds
# -- so the uncapped mrl=48 curve is an upper envelope for EVERY cap, and one fit
# covers all mrl. It predicts 63.7 states/node at 1M, i.e. ~14 GB per search.
# Per-presentation spread is ~1.3x (ratio 44.4..81.9 at 50k); that tail is left to
# _MemGuard rather than paid for by every worker.
_DISCOVERY_A = 82.9
_DISCOVERY_P = 0.981

# Interpreter + numba + numpy baseline, per worker process.
_BASE_GB = 0.35

# Fraction of usable RAM committed to searches when sizing the pool. The guard
# below is the real protection, so this does not need to be timid.
_RAM_SAFETY = 0.90

# Memory we refuse to let the machine drop below. Crossing this is what "about to
# OOM" actually means -- not "a worker went over its 1/n share".
_MEM_RESERVE_GB = 2.0


def _total_ram_gb():
    try:
        return (os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")) / 1e9
    except (ValueError, OSError, AttributeError):
        return 0.0


def _avail_ram_gb():
    """RAM we may actually use, in GB — the tightest of every limit we can see.

    ``SC_PHYS_PAGES`` (what this used to read) is the machine's TOTAL RAM. It
    ignores what the parent already holds (wandb, the mounted Drive cache, the
    notebook kernel) and it ignores a cgroup cap, which is exactly how a
    container like Colab limits a runtime. Both make it an over-estimate, and an
    over-estimate here means too many workers, which means the OOM killer.
    """
    cands = []
    total = _total_ram_gb()
    if total:
        cands.append(total)

    # Linux: memory not yet spoken for (excludes the parent's own footprint).
    try:
        with open("/proc/meminfo") as f:
            for ln in f:
                if ln.startswith("MemAvailable:"):
                    cands.append(int(ln.split()[1]) * 1024 / 1e9)
                    break
    except OSError:
        pass

    # Container cap (cgroup v2, then v1). Colab/Docker limit the runtime here,
    # and /proc/meminfo happily reports the whole host underneath it.
    for path in ("/sys/fs/cgroup/memory.max",
                 "/sys/fs/cgroup/memory/memory.limit_in_bytes"):
        try:
            with open(path) as f:
                raw = f.read().strip()
            if raw and raw != "max":
                lim = int(raw) / 1e9
                if 0 < lim < 1e6:          # v1 writes a sentinel ~2^63 for "no limit"
                    cands.append(lim)
        except (OSError, ValueError):
            pass

    return min(cands) if cands else 0.0


def _usable_cores():
    """Cores we may actually run on — affinity- and quota-aware.

    ``os.cpu_count()`` reports the HOST's cores, so in a container it can be
    several times the number we are scheduled on.
    """
    cands = []
    try:
        cands.append(len(os.sched_getaffinity(0)))     # Linux: honours affinity
    except (AttributeError, OSError):
        pass
    if os.cpu_count():
        cands.append(os.cpu_count())

    # cgroup v2 CPU quota, e.g. "200000 100000" -> 2 cores.
    try:
        with open("/sys/fs/cgroup/cpu.max") as f:
            quota, period = f.read().split()
        if quota != "max":
            cands.append(max(1, int(int(quota) / int(period))))
    except (OSError, ValueError):
        pass

    return min(cands) if cands else 1


def _est_gb_per_pres(cfg, node_budget):
    """Peak GB of ONE heavy search at this node budget.

    An explicit positive GB_PER_PRES always wins; "auto" (or 0/None) estimates.
    The old fixed 9.0 was calibrated at 1M/mrl=48 and applied at every budget,
    so a 50k run — which needs well under 1 GB — was provisioned as if it needed
    9, silently starving the pool of workers. It was also too LOW at its own
    calibration point: 1M x 70 states x 220 B is ~15 GB, not 9.
    """
    gb = cfg.get("GB_PER_PRES", "auto")
    if isinstance(gb, (int, float)) and not isinstance(gb, bool) and gb > 0:
        return float(gb)
    discovered = _DISCOVERY_A * node_budget ** _DISCOVERY_P
    return _BASE_GB + discovered * _BYTES_PER_STATE / 1e9


def _auto_workers(cfg, node_budget):
    """Worker count for HIGH_SPEEDUP: bounded by cores AND by RAM.

    Each concurrent search holds its own frontier, so RAM is the real cap —
    oversubscribing cores would OOM long before it helped. Under-provisioning
    cores merely wastes time; under-provisioning memory kills the runtime, so
    every estimate here is biased high and the floor is 1 worker.
    """
    n = int(cfg.get("N_WORKERS", 0) or 0)
    if n > 0:
        return n
    ram = _avail_ram_gb()
    gb = _est_gb_per_pres(cfg, node_budget)
    by_ram = int((ram * _RAM_SAFETY) // gb) if ram else 1
    return max(1, min(_usable_cores(), by_ram or 1))


def _proc_rss_bytes():
    """This process's resident memory. 0 if it cannot be read."""
    try:                                   # Linux: field 2 of statm is resident pages
        with open("/proc/self/statm") as f:
            return int(f.read().split()[1]) * os.sysconf("SC_PAGE_SIZE")
    except (OSError, ValueError, IndexError):
        pass
    try:                                   # macOS: bytes (Linux would be KB)
        import resource as _res
        v = _res.getrusage(_res.RUSAGE_SELF).ru_maxrss
        return v if sys.platform == "darwin" else v * 1024
    except Exception:
        return 0


def _sys_avail_bytes():
    """RAM the whole machine still has free, right now. 0 if unreadable.

    This is the only honest "about to OOM" signal: a worker legitimately larger
    than its 1/n share is fine as long as the machine has room, and no worker is
    fine once the machine does not. macOS exposes no MemAvailable, so there it
    returns 0 and the guard falls back to the per-worker cap.
    """
    try:
        with open("/proc/meminfo") as f:
            for ln in f:
                if ln.startswith("MemAvailable:"):
                    return int(ln.split()[1]) * 1024
    except (OSError, ValueError, IndexError):
        pass
    return 0


class _MemBudgetExceeded(Exception):
    """A search hit its per-worker memory allowance and stopped itself.

    Raised in a pool worker and pickled back to the parent, so ``args`` must be
    exactly the constructor's arguments: unpickling replays ``cls(*args)``, and a
    pre-formatted message there would raise TypeError inside the pool's result
    thread — the parent would then hang rather than see the abort.
    """

    def __init__(self, pres_id, nodes, rss_gb, limit_gb):
        super().__init__(pres_id, nodes, rss_gb, limit_gb)
        self.pres_id, self.nodes = pres_id, nodes
        self.rss_gb, self.limit_gb = rss_gb, limit_gb

    def __str__(self):
        return (f"pres {self.pres_id}: {self.rss_gb:.1f} GB > {self.limit_gb:.1f} GB "
                f"after {self.nodes:,} nodes")


class _MemGuard:
    """Stop a search before it can OOM the machine.

    The provisioning above is an estimate; this is the backstop that makes a
    wrong estimate cost one presentation instead of the whole runtime. Raising
    from the progress callback unwinds the plain-Python solve loop cleanly, so
    the worker survives and the pool keeps going.

    Two conditions, both required. Exceeding ``soft_gb`` (this worker's 1/n share)
    is NOT itself a problem: at 1M nodes a search legitimately peaks near 14 GB,
    which is above the 1/4 share of a 51 GB runtime, and a guard that fired there
    would abort almost every presentation and re-run it serially — a throughput
    disaster dressed up as safety. So a worker over its share only stops once the
    MACHINE is actually short of memory. Checking RSS first keeps the common case
    to one cheap read; and because the largest worker crosses ``soft_gb`` first,
    it is the one that yields, which is the one whose exit frees the most.
    """

    def __init__(self, pres_id, soft_gb, reserve_gb=_MEM_RESERVE_GB, every=8):
        self.pres_id = pres_id
        self.soft = soft_gb * 1e9
        self.reserve = reserve_gb * 1e9
        self.every, self.k = every, 0

    def __call__(self, nodes):
        self.k += 1
        if self.k % self.every:            # ~8k nodes between checks; ~2 s of work
            return
        rss = _proc_rss_bytes()
        if not rss or rss <= self.soft:
            return
        avail = _sys_avail_bytes()
        if avail and avail > self.reserve:
            return                         # over its share, but the machine is fine
        raise _MemBudgetExceeded(self.pres_id, nodes, rss / 1e9, self.soft / 1e9)


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
    """Top-level (picklable) worker: run one presentation, return its stats.

    On a memory abort it returns ``(pres_id, r1, r2, None, elapsed, exc)`` so the
    parent can retry it serially with the whole machine to itself; every other
    return has ``stats`` set and ``exc`` None.
    """
    pres_id, r1, r2, node_budget, mrl, cyc, high, hb_s, hb_dbg, mem_gb = job

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

    # The memory guard rides the same 1024-node tick as the heartbeat.
    guard = _MemGuard(pres_id, mem_gb) if mem_gb else None
    if guard is not None and progress is not None:
        hb = progress

        def progress(nodes, _hb=hb, _g=guard):
            _hb(nodes)
            _g(nodes)
    elif guard is not None:
        progress = guard

    t0 = time.time()
    try:
        stats = greedy_search(r1, r2, node_budget, max_relator_length=mrl,
                              cyclic_reduce=cyc, high_speedup=high, progress=progress)
    except _MemBudgetExceeded as e:
        return pres_id, r1, r2, None, time.time() - t0, e
    finally:
        _cancel_watchdog()
        if dbg_f is not None:
            dbg_f.close()
        if progress is not None and _HB_Q is not None:
            # Tell the printer to stop counting this presentation's last rate
            # into the aggregate; the worker moves on to the next job.
            _HB_Q.put_nowait(("done", pres_id))
    return pres_id, r1, r2, stats, time.time() - t0, None


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


def _abort_stats(exc):
    """Stats for a presentation the memory guard stopped: truthful, mostly null.

    ``nodes_explored`` is where it got to, not ``node_budget``; the row also
    carries ``mem_abort: true`` so it can never be read as a completed search.
    """
    stats = dict.fromkeys(
        ("path_length", "min_relator_length", "min_relator", "max_relator_length",
         "max_relator", "max_relator_length_expanded", "max_relator_expanded",
         "path", "path_moves"))
    stats["nodes_explored"] = exc.nodes
    stats["solved"] = False
    return stats


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

    Writes one jsonl per budget (crash-safe: fsync every row). Resumable via the
    pres_id set already present in the output file. When that file lives on a
    network mount, rows are appended to a local staging copy and the mount gets a
    whole-file mirror — see ``_is_remote``.
    """
    import time

    cfg = {**DEFAULT_CONFIG, **cfg}
    presentations = list(load_dataset(cfg["DATASET"], cfg["SUBSET"]))
    n_pres = len(presentations)
    out_path, paths_path, _date, stem = _resolve_paths(cfg, node_budget, n_pres)

    # Redirect the append handles to local disk and keep the mount as a mirror.
    # The mirror is what a *later session* resumes from — its VM, and therefore
    # the staging file, is gone — so seed the stage from it before reading `done`.
    mirror = []
    if _is_remote(out_path):
        stage_dir = cfg.get("STAGE_DIR") or os.path.join(cfg["LOCAL_OUT_DIR"],
                                                         "_stage")
        os.makedirs(stage_dir, exist_ok=True)
        stage_out = os.path.join(stage_dir, os.path.basename(out_path))
        stage_paths = os.path.join(stage_dir, os.path.basename(paths_path))
        _seed_stage(stage_out, out_path)
        _seed_stage(stage_paths, paths_path)
        mirror = [(stage_out, out_path), (stage_paths, paths_path)]
        print(f"    durable output: appending to {stage_dir} (local disk), "
              f"mirroring to {os.path.dirname(out_path)} every "
              f"{cfg['MIRROR_EVERY_S']}s", flush=True)
        out_path, paths_path = stage_out, stage_paths

    mirror_every_s = float(cfg.get("MIRROR_EVERY_S", 60) or 0)
    last_mirror = [time.time()]

    def _mirror_all(force=False):
        """Copy the staging files onto the mount. No-op when output is local."""
        if not mirror:
            return
        now = time.time()
        if not force and now - last_mirror[0] < mirror_every_s:
            return
        last_mirror[0] = now
        for local, remote in mirror:
            if os.path.exists(local):
                _copy_file(local, remote)

    # Before ANY reader or the append handles below touch these files. Not gated
    # on RESUME: a non-resumed run still opens them "a" and would concatenate
    # its first row onto a leftover stub.
    _repair_jsonl(out_path)
    _repair_jsonl(paths_path)

    if cfg["RESUME"]:
        done, n_seen, n_solved = _read_done(out_path)
        pending = _read_pending(out_path)
        mem_pending = _read_mem_pending(out_path)
    else:
        done, pending, mem_pending, n_seen, n_solved = set(), set(), set(), 0, 0

    todo_ids = [pid for (pid, _r1, _r2) in presentations if pid not in done]

    run = None
    logger = None
    run_id = stem   # same collision-safe identity as the jsonl (W&B ids allow it)
    if cfg["USE_WANDB"]:
        run = wandb_tracking.init_run(
            cfg, node_budget, n_pres, run_id,
            _run_prefix(cfg, node_budget, n_pres), _subset_tag(cfg["SUBSET"]))
        # Seed the cumulative counters so a resumed run's live curves stay
        # continuous. The results Table is built from the jsonl at finish time.
        prior = wandb_tracking.read_jsonl(out_path)
        logger = wandb_tracking.LiveLogger(
            run, cfg, node_budget, n_todo=len(todo_ids), n_seen=n_seen,
            n_solved=n_solved,
            cum_nodes=sum(r.get("nodes_explored") or 0 for r in prior))

    todo = [(pid, r1, r2) for (pid, r1, r2) in presentations if pid not in done]
    n_todo = len(todo)
    every = max(1, int(cfg["PROGRESS_EVERY"]))
    print(f"=== budget={node_budget} | {n_pres} presentations | "
          f"{len(done)} already done, {n_todo} to run | -> {out_path}",
          flush=True)
    if pending:
        print(f"    {len(pending)} solved row(s) still need a path: "
              f"{sorted(pending)} (search NOT repeated)", flush=True)
    if n_todo == 0 and not pending:
        print("    nothing to do (all done). ", flush=True)

    high = bool(cfg["HIGH_SPEEDUP"])
    mrl = cfg["MAX_RELATOR_LENGTH"]
    cyc = cfg["CYCLIC_REDUCE"]
    hb_s = float(cfg.get("HEARTBEAT_EVERY_S", 0) or 0)
    hb_dbg = bool(cfg.get("HEARTBEAT_DEBUG", False))
    # Resource provisioning is HIGH_SPEEDUP-only: the normal path runs one search
    # in this process, so there is nothing to divide up and nothing to guard.
    n_workers = _auto_workers(cfg, node_budget) if high else 1
    mem_gb = 0.0
    if high:
        avail = _avail_ram_gb()
        est = _est_gb_per_pres(cfg, node_budget)
        # Per-worker allowance. The guard only fires if a search overshoots the
        # estimate, so a correct estimate costs nothing.
        mem_gb = (avail * _RAM_SAFETY / n_workers) if avail else 0.0
        src = ("pinned" if isinstance(cfg.get("GB_PER_PRES"), (int, float))
               and not isinstance(cfg.get("GB_PER_PRES"), bool)
               and cfg.get("GB_PER_PRES", 0) > 0 else "auto")
        print(f"    HIGH_SPEEDUP: {n_workers} worker(s) | {avail:.0f} GB usable"
              f" / {_total_ram_gb():.0f} GB total | {_usable_cores()} core(s)"
              f" | ~{est:.1f} GB/presentation ({src})", flush=True)
        if mem_gb:
            print(f"    memory guard: a worker over {mem_gb:.1f} GB stops only if "
                  f"the machine drops below {_MEM_RESERVE_GB:.0f} GB free "
                  f"(then it is retried serially)", flush=True)
        if int(cfg.get("N_WORKERS", 0) or 0) > 0 and avail and \
                n_workers * est > avail:
            print(f"    NOTE: N_WORKERS={n_workers} pinned; {n_workers} x "
                  f"{est:.1f} GB = {n_workers * est:.0f} GB vs {avail:.0f} GB "
                  f"usable. Auto would pick "
                  f"{_auto_workers({**cfg, 'N_WORKERS': 0}, node_budget)}. The "
                  f"guard will catch a genuine shortfall.", flush=True)
    jobs = [(pid, a, b, node_budget, mrl, cyc, high, hb_s, hb_dbg, mem_gb)
            for pid, a, b in todo]
    if hb_s > 0:
        print(f"    heartbeat: nodes/s every {hb_s:g}s", flush=True)

    total_time = 0.0
    t_start = time.time()
    processed = 0
    out_f = open(out_path, "a")
    paths_f = open(paths_path, "a") if cfg["PATH_IN_SEPARATE_FILE"] else None
    # Only on RESUME: a retried recovery must not append a second path row for a
    # pres_id whose previous attempt already wrote one.
    paths_done = (_read_paths_done(paths_path)
                  if cfg["PATH_IN_SEPARATE_FILE"] and cfg["RESUME"] else set())
    pool = None

    def _write_path(pres_id, r1, r2, stats):
        if not (cfg["PATH_IN_SEPARATE_FILE"] and cfg["use_path"]
                and stats["solved"] and pres_id not in paths_done):
            return
        path_row = {"pres_id": pres_id, "r1": r1, "r2": r2}
        path_row.update(_path_payload(cfg, stats))
        paths_f.write(json.dumps(path_row) + "\n")
        _persist(paths_f)
        paths_done.add(pres_id)

    def _emit(pres_id, r1, r2, stats, elapsed, mem_abort=False,
              path_pending=False, mem_abort_pending=False, notify=True):
        row = _build_row(cfg, pres_id, r1, r2, node_budget, stats, elapsed)
        if mem_abort:
            # nodes_explored is the count reached before the guard fired, NOT the
            # full node_budget. Never read this row as "searched the whole budget".
            row["mem_abort"] = True
        if mem_abort_pending:
            row["mem_abort_pending"] = True
        if path_pending:
            row["path_pending"] = True
        out_f.write(json.dumps(row) + "\n")
        _persist(out_f)
        if not path_pending:
            _write_path(pres_id, r1, r2, stats)
        _mirror_all()
        # A pending row is a placeholder, not a result: notify=False keeps it out
        # of the W&B table, which _finalize then fills with the real row.
        if logger is not None and notify:
            logger.on_row(row)

    def _finalize(pres_id, r1, r2, stats, elapsed, mem_abort=False,
                  path_pending=False):
        """Overwrite an existing ``mem_abort_pending`` row with its real result.

        Appending would leave two rows for one pres_id, which every consumer's
        one-row-per-id assumption forbids. Requires ``out_f`` already closed:
        ``_update_row`` rewrites via ``os.replace`` and would orphan the fd.
        """
        row = _build_row(cfg, pres_id, r1, r2, node_budget, stats, elapsed)
        if mem_abort:
            row["mem_abort"] = True
        if path_pending:
            row["path_pending"] = True
        if not _update_row(out_path, pres_id, row):
            # The placeholder should always be there — _emit wrote it, or resume
            # read it back. If it is not, the filesystem dropped it (the failure
            # _report_lost_rows exists for). Append rather than let _update_row's
            # no-op silently discard a search that cost hours.
            print(f"    !! pres {pres_id}: no row to update; appending instead.",
                  flush=True)
            with open(out_path, "a") as f:
                f.write(json.dumps(row) + "\n")
                _persist(f)
        if not path_pending:
            _write_path(pres_id, r1, r2, stats)
        _mirror_all()
        if logger is not None:
            logger.on_row(row)

    # Heavy mode drops path tracking, so a solved presentation must be re-solved
    # by the normal solver AFTER the pool is torn down (it needs the full RAM).
    # Its search result is written IMMEDIATELY as a `path_pending` row, so a
    # crash or disconnect during recovery can never lose the expensive search —
    # only the path, which resume then retries without re-searching.
    by_id = {pid: (a, b) for pid, a, b in presentations}
    deferred = [(pid, *by_id[pid]) for pid in sorted(pending)]
    # Guard-tripped in THIS session (exc set) or in a previous one (exc None, read
    # back from the mem_abort_pending rows). Both are retried serially below; the
    # resumed ones are already in `done`, so the pool never sees them again.
    aborted = [(pid, *by_id[pid], None) for pid in sorted(mem_pending)]
    try:
        # `and jobs`: a fully-resumed sweep has nothing to search. Without this
        # the warm-up below reads todo[0] and raises IndexError, so re-running a
        # finished heavy run just to confirm it is complete crashes.
        if high and n_workers > 1 and jobs:
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

        for pres_id, r1, r2, stats, elapsed, exc in results:
            total_time += elapsed
            if exc is not None:
                # Out of its memory allowance, not out of memory: the worker is
                # alive and the machine never went near the OOM killer. Retry it
                # after teardown, alone, with the whole budget.
                #
                # Persist the trip BEFORE the retry. The retry only runs once the
                # pool has drained every other presentation (~29 h at 1M x 261),
                # so a session that dies first would otherwise leave no trace that
                # this id tripped, and the next resume would feed it back into the
                # pool to trip again. _finalize overwrites this row in place.
                print(f"    pres {pres_id}: memory guard tripped ({exc}); row "
                      f"persisted as mem_abort_pending, deferring to a serial retry",
                      flush=True)
                _emit(pres_id, r1, r2, _abort_stats(exc), elapsed,
                      mem_abort=True, mem_abort_pending=True, notify=False)
                aborted.append((pres_id, r1, r2, exc))
                continue
            # `use_path`: with paths switched off there is nothing to recover, and
            # the recovery re-solve is the NORMAL solver at the full budget with no
            # memory guard (~25 GB at 1M/mrl48). Deferring here would spend it to
            # produce a path that _write_path then discards.
            solved_no_path = high and stats["solved"] and cfg["use_path"]
            _emit(pres_id, r1, r2, stats, elapsed, path_pending=solved_no_path)
            if solved_no_path:
                deferred.append((pres_id, r1, r2))   # path filled in after teardown

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

        # Every row is already durable, including the mem_abort_pending
        # placeholders. _update_row — which both loops below use to fill a
        # placeholder in place — rewrites the file via os.replace, and that would
        # orphan this append handle's fd. So close it before either runs.
        out_f.close()
        out_f = None

        # Retry memory-aborted presentations one at a time. The pool is gone, so
        # a retry gets the whole budget instead of a 1/n_workers slice — usually
        # enough to finish. With a single worker there was no slice to reclaim, so
        # retrying would just re-run the same search into the same wall — unless
        # the trip happened in an EARLIER session (exc is None), which never got a
        # serial attempt at all and is the whole reason the row was persisted.
        for pres_id, r1, r2, exc in aborted:
            resumed = exc is None
            solo_gb = _avail_ram_gb() * _RAM_SAFETY
            if solo_gb and (resumed or n_workers > 1):
                print(f"    retrying pres {pres_id} serially ({solo_gb:.1f} GB "
                      f"allowance)...", flush=True)
                t0 = time.time()
                try:
                    stats = greedy_search(
                        r1, r2, node_budget, max_relator_length=mrl,
                        cyclic_reduce=cyc, high_speedup=True,
                        progress=_MemGuard(pres_id, solo_gb))
                except _MemBudgetExceeded as e:
                    exc = e
                else:
                    elapsed = time.time() - t0
                    total_time += elapsed
                    # always heavy, so a solved row still needs its path recovered
                    solved_no_path = stats["solved"] and cfg["use_path"]
                    _finalize(pres_id, r1, r2, stats, elapsed,
                              path_pending=solved_no_path)
                    if solved_no_path:
                        deferred.append((pres_id, r1, r2))
                    n_solved += int(stats["solved"])
                    if not resumed:
                        # A resumed placeholder was already counted by _read_done;
                        # counting it again would push processed past n_todo.
                        n_seen += 1
                        processed += 1
                    if logger is not None:
                        # These never reached on_result in the worker loop (they
                        # returned an exception, not stats), so count them here or
                        # the cumulative run/* counters silently lose them.
                        logger.on_result(stats)
                    continue
            if exc is None:
                # No retry ran and nothing new was learned. Leave the placeholder
                # so the next session tries again, rather than burning the id on a
                # terminal mem_abort row we have no evidence for.
                print(f"    pres {pres_id}: no serial retry possible here; row "
                      f"stays mem_abort_pending for the next run.", flush=True)
                continue
            # It genuinely does not fit on this machine. Record that honestly
            # rather than crash the run or silently drop the presentation.
            print(f"    pres {pres_id}: ABORTED on memory ({exc}). "
                  f"Row written with mem_abort=true.", flush=True)
            stats = _abort_stats(exc)
            _finalize(pres_id, r1, r2, stats, 0.0, mem_abort=True)
            if not resumed:
                n_seen += 1
                processed += 1
            if logger is not None:
                logger.on_result(stats)

        n_failed = 0
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
            try:
                stats = greedy_search(r1, r2, node_budget, max_relator_length=mrl,
                                      cyclic_reduce=cyc, high_speedup=False,
                                      progress=recover_hb)
            except Exception as e:
                # The normal solver is the memory-hungry one, and it runs with no
                # _MemGuard. Losing one path is survivable; losing the other
                # presentations' rows is not. KeyboardInterrupt still exits.
                n_failed += 1
                print(f"    !! path recovery FAILED for pres {pres_id}: "
                      f"{type(e).__name__}: {e}", flush=True)
                print("       its search row is kept (path_pending); re-run with "
                      "RESUME=True to retry just this path.", flush=True)
                continue
            # Path first: a crash between the two leaves path_pending set, and
            # _write_path is idempotent, so the retry converges.
            _write_path(pres_id, r1, r2, stats)
            row = _build_row(cfg, pres_id, r1, r2, node_budget, stats,
                             time.time() - t0)
            row["path_recovered"] = True
            _update_row(out_path, pres_id, row)
            _mirror_all()

        if n_failed:
            print(f"    {n_failed} path(s) not recovered; all search rows intact.",
                  flush=True)
    finally:
        if pool is not None:
            pool.terminate()
            pool.join()
        if out_f is not None:
            out_f.close()
        if paths_f is not None:
            paths_f.close()
        # Unconditional: a Ctrl-C / KeyboardInterrupt must still push the rows this
        # session earned onto the mount, because the staging disk dies with the VM.
        _mirror_all(force=True)

    _report_lost_rows(out_path, done, todo_ids)

    if run is not None:
        wandb_tracking.finish_run(run, logger, out_path, paths_path, run_id,
                                  n_seen, n_solved, total_time, cfg, node_budget)

    # The mirror, not the staging copy, is what outlives the VM.
    final_path = mirror[0][1] if mirror else out_path
    print(f"[{final_path}] {n_seen} presentations, {n_solved} solved "
          f"({n_solved / max(n_seen, 1):.1%}).")
    return final_path
