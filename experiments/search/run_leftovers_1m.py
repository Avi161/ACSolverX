"""Lift the AC19 aut-min 100k residuals to a 1,000,000-node budget, one arm per call.

THE ROW LISTS
-------------
The ~70k AC19 aut-min screen (72,779 ``Aut(F2)``-orbit representatives of
``data/AC19_extended.txt``) ran every arm at budget 1,000, the top four again at
10,000, then escalated each arm's own 10k failures to 100,000. What survived that
100,000-node pass is the input here -- shipped beside this file, presentations
inline, no join needed:

    unsolved_100k_baseline.csv    222 rows   greedy / total-length ordering
    unsolved_100k_s20_mk2.csv      39 rows   L + 20*S + 2*MK

Both are ``solved == false`` read straight off the 100k jsonl, which ships too
(``results/heuristic_search/hsearch_ac19_hard100k/``): 609/831 solved for the
greedy arm, 220/259 for s20_mk2. ``tests/test_leftovers_1m.py`` re-derives both
CSVs from that jsonl rather than trusting them. The 39 are a strict subset of the
222 -- s20_mk2 recovers 182 of the greedy arm's failures and loses none.

    221 OR 222? Both, and they do not conflict. ``RESULTS.md`` scores over the
    70,723 orbits BOTH arms searched at 10k; exactly one greedy failure,
    ``ac19_33435``, sits outside that intersection because s20_mk2 never searched
    it. So 222 = every orbit the greedy arm actually failed, 221 = the common
    denominator. This runner ships all 222 and takes ``common_denominator=True``
    to drop that one row, so either number can be quoted as long as it says which.
    Full provenance: ``ac19_autmin_screen/UNSOLVED_AFTER_100k.md``.

    PYTHONPATH=. python3 -m experiments.search.run_leftovers_1m --arm greedy --smoke

WHAT COMES BACK
---------------
For each arm: how many of its 100k leftovers a 1,000,000-node budget solves. The
smaller budgets come free -- ``solved_at`` is a PREFIX PROPERTY, a search at
budget B being exactly the first B pops of any longer search -- so one run also
gives the anytime curve at 250k and 500k with no second search. The 100k column
is a self-check rather than a result: every row here was unsolved at 100,000 by
construction, so a row coming back solved at or below 100,000 nodes means the
search being run is not the search that built the list.

WHICH SEARCH RUNS
-----------------
Both arms run ``hcompact`` -- the packed-arena engine (nibble arena, int32 binary
heap, open-addressing table, all in numba) that the 100k wave itself used, ported
onto this branch with its chain. The heap ordering is the only thing that differs:

    greedy    config=LENGTH_ONLY    priority = L
    s20_mk2   config=S20_MK2        priority = L + 20*S + 2*MK

Measured on ``ac19_7284`` from this row list, budget 60,000, cap 48: 802 nodes/s
in 7.6 GB at 1M, against the pure-Python ``LeanHeuristicSolver``'s 290 nodes/s in
46 GB -- 6 workers on a 51 GB runtime instead of 1.

    ``LeanHeuristicSolver`` and ``greedy_search(high_speedup=True)`` are still
    here, and are still exercised: they are the fallback where the engine is
    absent, and they are the ORACLE the tests check the engine against field for
    field on real rows from these lists. Swapping an engine under an experiment
    with published numbers is only legitimate if it is the same search.

    Since this is the engine the 100k wave ran, ``nodes_explored`` IS comparable
    across the two runs -- an earlier revision of this file, running the Python
    solvers, warned that it was not. That caveat no longer applies.

The withdrawn ``RECOMMENDED`` weight vector is refused by name; see ``resolve_arm``.
"""
from __future__ import annotations

import argparse
import csv
import heapq
import json
import multiprocessing as mp
import os
import queue as _queue
import shutil
import sys
import threading
import time

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from experiments.search import heuristics as _heur  # noqa: E402
from experiments.search.greedy_baseline import (  # noqa: E402
    _HB_CHECK_EVERY, _KEY_SEP, GreedyHeavySolver, expand_node_nj, greedy_search,
    key_lengths, pack_key, unpack_arrays, unpack_key,
)
from experiments.search.heuristics import make_priority  # noqa: E402

# The packed-arena engine: a nibble arena, an int32 binary heap and an
# open-addressing table, all in numba, at ~76-84 B/state against the Python
# solvers' ~390 B. Measured on ac19_7284 from this very row list, budget 60,000,
# cap 48: 802 n/s against LeanHeuristicSolver's 290, and 7.6 GB at 1M against 46
# -- which is 6 workers on a 51 GB runtime instead of 1. Between them that is
# more than an order of magnitude of wall clock.
#
# Imported behind a guard so this module still works where the engine is absent
# (it is not on `main`); the Python solvers below stay as the fallback AND as the
# oracle the tests check the engine against.
try:  # pragma: no cover - exercised by whichever branch this sits on
    from experiments.heuristic_search.core.hcompact import greedy_search_hcompact
    from experiments.heuristic_search.core.hsolve import LENGTH_ONLY
    from experiments.search.greedy_compact import (
        _RESERVE_SLACK, est_states, row_width)
    HAVE_HCOMPACT = True
except ImportError:  # pragma: no cover
    greedy_search_hcompact = None
    LENGTH_ONLY = {"segments": [{"upto": None, "w": {"L": 1.0}}]}
    HAVE_HCOMPACT = False

ROOT = _ROOT
SCREEN_DIR = os.path.join(
    ROOT, "results", "heuristic_search", "ac19_autmin_screen")
HARD100K_DIR = os.path.join(
    ROOT, "results", "heuristic_search", "hsearch_ac19_hard100k")

# The shipped ordering, as a config for ``heuristics.make_priority``:
#
#     priority(r1, r2) = L + 20*S + 2*MK
#
# Imported from the module on branches that carry the name (PR #17 replaces the
# withdrawn RECOMMENDED with it) and defined identically here on branches that do
# not, so this runner works beside either. The literal is byte-for-byte the one on
# ``origin/claude/heuristic-search-benchmark-e1f9l8``.
try:  # pragma: no cover - depends on the branch this file sits beside
    from experiments.search.heuristics import S20_MK2
except ImportError:
    S20_MK2 = {"segments": [
        {"upto": None, "w": {"L": 1.0, "S": 20.0, "MK": 2.0}}]}

NODE_BUDGET = 1_000_000
MAX_RELATOR_LENGTH = 48          # the cap every wave of this screen has used

# Free extra columns: a row solved at 300,000 pops was solved at every budget
# above that and unsolved below it, so the anytime curve is already in the jsonl.
# 100,000 is the self-check described in the module docstring, not a result.
CHECKPOINTS = (100_000, 250_000, 500_000, 1_000_000)

# The one greedy row outside the 70,723-orbit common denominator; see docstring.
COMMON_DENOMINATOR_EXCLUDED = {"greedy": ("ac19_33435",), "s20_mk2": ()}


# ------------------------------------------- the heuristic arm at a 1M budget
#
# ``heuristics.greedy_search_h`` cannot reach 1,000,000 nodes. It is the
# dict-based solver -- ``visited`` (state -> parent), ``move_in`` and ``new_seen``,
# all keyed by tuples of Python strings -- because it reconstructs the certificate
# path. Measured on ``ac19_1007`` from this screen at cap 48: **1.64 GB by 12,288
# popped nodes**, which extrapolates past 100 GB at 1M. That is not a slow run,
# it is an OOM on any runtime.
#
# The length-only arm never had this problem: ``greedy_search(high_speedup=True)``
# is ``GreedyHeavySolver``, a memory-lean twin that keeps one ``set`` of packed
# byte keys and no parent map, and reports ``path_length`` as the solved node's
# depth instead of rebuilding the path. It exists for exactly this budget.
#
# So the heuristic arm gets the same treatment: subclass that lean solver and swap
# the heap's priority expression, which is the one thing that differs between the
# arms. Everything else -- the numba expansion, the reduction, the
# canonicalisation, the cap, the visited set, the ``(priority, depth, key)`` push
# shape -- is inherited, exactly as ``heuristics.HeuristicSolver`` inherits from
# ``GreedyBaselineSolver``, so a difference between the arms stays attributable to
# the ordering and to nothing else.
#
# Pop order is unchanged by the leaner key. The heavy solver pushes the packed
# bytes where the dict solver pushes the ``(r1, r2)`` string tuple, and
# ``pack_key`` sorts identically to the string pair -- the code table is
# order-preserving and the ``\x00`` separator sorts below every code, so a shorter
# relator that prefixes a longer one still compares smaller. That equivalence is
# pinned row by row against ``greedy_search_h`` itself rather than argued.


def _flat_priority(config):
    """A bare-float scorer for a one-segment config, or ``None`` if not applicable.

    ``make_priority`` returns ``(segment_index, score)``. The leading index is what
    lets an endgame boundary rank every state in a shorter segment above every
    state in a longer one -- but a config with a single ``upto: None`` segment,
    which is what ``S20_MK2`` and the baseline both are, puts every state in
    segment 0, so the index is constant and the tuple is pure overhead. Comparing
    ``(0, a)`` with ``(0, b)`` is comparing ``a`` with ``b``, and the ``depth`` and
    ``key`` tie-breaks behind it are untouched, so pop order is identical.

    It is worth the special case because that tuple is allocated once per
    DISCOVERED state and lives in the heap until the state is popped -- and a
    best-first search discovers far more than it pops. Measured on ``ac19_7284``
    from this list, dropping it takes the arm from ~63 GB projected at 1,000,000
    nodes, which does not fit a 51 GB high-RAM runtime, to something that does.

    Multi-segment configs keep the tuple; correctness first, and nothing this
    experiment runs is multi-segment.
    """
    segs = (config or {}).get("segments") or []
    if len(segs) != 1 or segs[0].get("upto") is not None:
        return None
    inner = make_priority(config)

    def priority(r1, r2):
        return inner(r1, r2)[1]
    return priority


class LeanHeuristicSolver(GreedyHeavySolver):
    """``GreedyHeavySolver`` with the heap ordering lifted out into ``self.priority``.

    Returns no path -- ``path_length`` is the solved node's depth, which is the
    number this experiment reports anyway. Recover a certificate for one row by
    re-running that row through ``greedy_search_h``, affordable once the list is
    39 long rather than 259.
    """

    def __init__(self, r1, r2, config=None, **kw):
        super().__init__(r1, r2, **kw)
        self.priority = _flat_priority(config) or make_priority(config)

    def _score(self, key):
        """Priority for a packed key, without leaving it in the pair cache.

        ``heuristics.phi`` memoises on ``(r1, r2)`` in a module-level dict. That
        cache pays for itself in the dict solver, which re-scores a state every
        time it is reached -- but here the visited set means every state is scored
        exactly once, so not one entry is ever read again and the dict is a pure
        leak: it would hold an entry per discovered state, millions of them, for
        the life of the worker. ``word_stats``'s own cache is left alone; that one
        is keyed on the relator string, is bounded by the distinct relators seen,
        and does hit.
        """
        pair = unpack_key(key)
        pr = self.priority(*pair)
        _heur._STATE_CACHE.pop(pair, None)
        return pr

    def solve(self, progress=None):
        cap = self.max_relator_length
        init_key = pack_key(self.initial_state[0], self.initial_state[1])
        init_total = len(self.initial_state[0]) + len(self.initial_state[1])
        heapq.heappush(self.pq, (self._score(init_key), 0, init_key))
        self.visited.add(init_key)
        self.n_discovered = 1

        self.min_key, self.min_total = init_key, init_total
        self.max_key, self.max_total = init_key, init_total
        self.max_expanded_key, self.max_expanded_total = init_key, init_total

        nodes_visited = 0
        pq = self.pq
        visited = self.visited
        score = self._score
        while pq and nodes_visited < self.max_nodes:
            _, depth, key = heapq.heappop(pq)
            nodes_visited += 1
            if progress is not None and nodes_visited % _HB_CHECK_EVERY == 0:
                progress(nodes_visited)

            l1, l2 = key_lengths(key)
            total = l1 + l2
            if total > self.max_expanded_total:
                self.max_expanded_key, self.max_expanded_total = key, total

            if l1 == 1 and l2 == 1:
                self.solved_depth = depth
                return True, nodes_visited

            a1, a2 = unpack_arrays(key)
            codes, lens, moves, count = expand_node_nj(
                a1, a2, cap, self.cyclic_reduce)

            depth1 = depth + 1
            for i in range(count):
                la = lens[i, 0]
                lb = lens[i, 1]
                row = codes[i]
                key_new = row[:la].tobytes() + _KEY_SEP + row[la:la + lb].tobytes()
                if key_new not in visited:
                    visited.add(key_new)
                    self.n_discovered += 1
                    new_total = int(la) + int(lb)
                    if new_total < self.min_total:
                        self.min_key, self.min_total = key_new, new_total
                    elif new_total > self.max_total:
                        self.max_key, self.max_total = key_new, new_total
                    heapq.heappush(pq, (score(key_new), depth1, key_new))

        return False, nodes_visited


def greedy_search_h_lean(r1_str, r2_str, node_budget, max_relator_length=24,
                         cyclic_reduce=True, config=None, progress=None):
    """``greedy_search_h``'s stats dict, minus ``path``/``path_moves``.

    The same eleven keys, so nothing downstream branches on which solver ran;
    ``path`` and ``path_moves`` come back empty exactly as they do from
    ``greedy_search(high_speedup=True)``.
    """
    solver = LeanHeuristicSolver(
        r1_str, r2_str,
        config=config,
        max_nodes=node_budget,
        max_relator_length=max_relator_length,
        cyclic_reduce=cyclic_reduce,
    )
    solved, nodes_visited = solver.solve(progress)
    min_r = unpack_key(solver.min_key)
    max_r = unpack_key(solver.max_key)
    exp_r = unpack_key(solver.max_expanded_key)
    return {
        "solved": solved,
        "nodes_explored": nodes_visited,
        "path_length": solver.solved_depth,
        "min_relator_length": solver.min_total,
        "min_relator": [min_r[0], min_r[1]],
        "max_relator_length": solver.max_total,
        "max_relator": [max_r[0], max_r[1]],
        "max_relator_length_expanded": solver.max_expanded_total,
        "max_relator_expanded": [exp_r[0], exp_r[1]],
        "path": [],
        "path_moves": [],
    }


def _run_greedy(r1, r2, budget, mrl, progress=None, reserve_states=None,
                track_path=False):
    if HAVE_HCOMPACT:
        return greedy_search_hcompact(r1, r2, budget, max_relator_length=mrl,
                                      config=LENGTH_ONLY, progress=progress,
                                      reserve_states=reserve_states,
                                      track_path=track_path)
    return greedy_search(r1, r2, budget, mrl, high_speedup=True, progress=progress)


def _run_s20_mk2(r1, r2, budget, mrl, progress=None, reserve_states=None,
                 track_path=False):
    if HAVE_HCOMPACT:
        return greedy_search_hcompact(r1, r2, budget, max_relator_length=mrl,
                                      config=S20_MK2, progress=progress,
                                      reserve_states=reserve_states,
                                      track_path=track_path)
    return greedy_search_h_lean(r1, r2, budget, mrl, config=S20_MK2,
                                progress=progress)


def est_gb(budget=NODE_BUDGET, mrl=MAX_RELATOR_LENGTH, track_path=False):
    """Peak GB one search costs, for sizing the pool. Not a limit, an estimate.

    With the arena engine this is its own reservation formula, so the number the
    pool is sized by and the number the search actually allocates are the same
    quantity rather than two guesses that can drift apart. Without it, the
    fallback Python solvers are measured: ~16 GB at 1M for the greedy arm's lean
    solver and ~46 GB for the heuristic one, so the larger is used -- undersizing
    is an OOM, oversizing is only a slower run.
    """
    if not HAVE_HCOMPACT:
        return max(1.0, 46.0 * budget / 1_000_000)
    n = max(1024, int(est_states(budget) * _RESERVE_SLACK)) + 4 * (mrl + 1) ** 2
    # +8 when capturing paths: an int32 parent and the move's four int8s
    per = row_width(mrl) + 31 + (8 if track_path else 0)
    return n * per / 2 ** 30 + 0.6


# name -> the search, its 100k-unsolved CSV, the 100k jsonl that CSV was read off,
#         the row counts (all-failures / common-denominator), and the RAM a worker
#         must be given.
#
# The row counts are asserted, not assumed: a stale or shallow clone handing the
# runner a different list would otherwise run a different experiment to completion
# and report it under this name.
ARMS = {
    "greedy": {
        "run": _run_greedy,
        "csv": "unsolved_100k_baseline.csv",
        "jsonl": "ac19_unsolved10k_baseline_b100000_mrl48.jsonl",
        "n_rows": 222,
        "n_common": 221,
        "label": "greedy (total-length ordering; the screen's `baseline` arm)",
    },
    "s20_mk2": {
        "run": _run_s20_mk2,
        "csv": "unsolved_100k_s20_mk2.csv",
        "jsonl": "ac19_unsolved10k_s20_mk2_b100000_mrl48.jsonl",
        "n_rows": 39,
        "n_common": 39,
        "label": "s20_mk2 (priority = L + 20*S + 2*MK)",
    },
}

# Guarded rather than merely absent. ``RECOMMENDED`` is still importable from
# heuristics.py on a branch cut from main, and it is the easiest thing to reach for
# by muscle memory; running it here would be a withdrawn, in-sample weight vector
# wearing this experiment's name.
_REFUSED = ("recommended", "s20", "s20_mk20_l", "mk20")


def resolve_arm(name):
    """``(key, spec)`` for ``name``, with the withdrawn/confusable names refused."""
    key = str(name).strip().lower()
    if key in ARMS:
        return key, ARMS[key]
    if key in _REFUSED:
        raise ValueError(
            f"arm {name!r} is not run by this experiment. The heuristic arm is "
            f"'s20_mk2' (L + 20*S + 2*MK). The former 'RECOMMENDED' vector "
            f"(L + 2.53*K + 6.418*MK + 8.458*S + 3.292*xyimb) was withdrawn as "
            f"overfit and must not be run.")
    raise KeyError(f"unknown arm {name!r}; known={sorted(ARMS)}")


# ------------------------------------------------------------------------ rows
def load_rows(arm, csv_path=None, ids=None, common_denominator=False):
    """``([{name, r1, r2, min_relator_length}], path)`` for ``arm``, in file order.

    ``common_denominator``: drop the rows outside the 70,723 orbits both arms
    searched at 10k -- one row, on the greedy arm -- so the count matches the 221
    that ``RESULTS.md`` quotes. Off by default: the CSV's own 222 is the number of
    orbits that arm actually failed, and dropping a row should be a choice someone
    made rather than one the runner made for them.

    ``ids``: an explicit subset, in the order given. Every id must be in the arm's
    own list; a name from the other arm's is a different experiment.
    """
    key, spec = resolve_arm(arm)
    path = csv_path or os.path.join(SCREEN_DIR, spec["csv"])
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"row list missing: {path}\n"
            f"It ships with this branch under {SCREEN_DIR}; a clone of the wrong "
            f"branch is the usual cause.")
    with open(path, newline="") as f:
        rows = [{"name": r["name"], "r1": r["r1"], "r2": r["r2"],
                 "min_relator_length": r.get("min_relator_length")}
                for r in csv.DictReader(f)]
    if not rows:
        raise RuntimeError(f"empty row list: {path}")
    names = [r["name"] for r in rows]
    if len(names) != len(set(names)):
        raise RuntimeError(f"duplicate names in {path}")
    if csv_path is None and len(rows) != spec["n_rows"]:
        raise RuntimeError(
            f"{spec['csv']} has {len(rows)} rows, expected {spec['n_rows']} -- "
            f"stale clone; pull the branch before running.")
    if common_denominator:
        drop = set(COMMON_DENOMINATOR_EXCLUDED.get(key, ()))
        rows = [r for r in rows if r["name"] not in drop]
    if ids is not None:
        want = list(dict.fromkeys(ids))
        by_name = {r["name"]: r for r in rows}
        missing = [n for n in want if n not in by_name]
        if missing:
            raise KeyError(
                f"{len(missing)} id(s) not in {os.path.basename(path)}, e.g. "
                f"{missing[:5]} -- an id list must be a subset of this arm's own "
                f"100k-unsolved rows.")
        rows = [by_name[n] for n in want]
    return rows, path


def unsolved_at_100k(arm):
    """The arm's 100k leftovers re-derived from the 100k jsonl, sorted by name.

    The CSVs beside this file are supposed to be exactly this. Deriving it again
    is what lets a test check them instead of trusting them.
    """
    key, spec = resolve_arm(arm)
    path = os.path.join(HARD100K_DIR, spec["jsonl"])
    rows = read_rows(path)
    if not rows:
        raise FileNotFoundError(f"100k jsonl missing or empty: {path}")
    return sorted(r["name"] for r in rows if not r.get("solved"))


# --------------------------------------------------------------------- workers
def _available_gb():
    """Free RAM in GB, best effort. Colab guarantees no psutil; /proc is there."""
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemAvailable:"):
                    return int(line.split()[1]) / (1024.0 * 1024.0)
    except OSError:
        pass
    try:
        return (os.sysconf("SC_AVPHYS_PAGES") * os.sysconf("SC_PAGE_SIZE")
                / 1024.0 ** 3)
    except (ValueError, OSError, AttributeError):
        return 8.0


def resolve_workers(arm, n_workers="auto", available_gb=None, cpu_count=None,
                    budget=NODE_BUDGET, mrl=MAX_RELATOR_LENGTH,
                    track_path=False):
    """``(n_workers, gb_per_worker)`` -- RAM-bound, not CPU-bound.

    A 1M-node search is a memory event before it is a compute one, and it grows
    with what the search *discovers*, not with what it pops -- a best-first search
    queues far more than it expands. Measured at cap 48 on rows from these lists,
    extrapolated linearly to 1,000,000 nodes:

        greedy    2.71 GB at 200,000 pops (ac19_420)    -> ~16 GB, ~1050 nodes/s
        s20_mk2   1.17 GB at  25,600 pops (ac19_7284)   -> ~46 GB, ~330 nodes/s

    The arms differ because the orderings go different places: s20_mk2 prefers
    thicker blocks, which means longer relators near the cap and a wider frontier.
    On a 51 GB high-RAM Colab that is 3 greedy workers, or 1 for s20_mk2 -- and
    39 rows is a small job. Oversubscribing does not make a slow run, it makes an
    OOM that loses the session, so the RAM ceiling wins over the core count. One
    worker is always allowed even when the estimate says there is no room, because
    the estimate is linear and a real row may well be cheaper.
    """
    resolve_arm(arm)
    per = est_gb(budget, mrl, track_path=track_path)
    cpus = cpu_count or os.cpu_count() or 1
    if n_workers not in (None, "auto"):
        return max(1, int(n_workers)), per
    gb = available_gb if available_gb is not None else _available_gb()
    # keep ~2 GB back for the parent, the numba runtime and Drive I/O
    return max(1, min(cpus, int((gb - 2.0) // per))), per


# ------------------------------------------------------------------------- run
def _in_search_heartbeat(name, budget, every=60.0, log=print):
    """A ``progress`` callback that reports from INSIDE one row's search.

    Without this the run is silent for the length of a whole row -- 25 to 80
    minutes at a 1,000,000-node budget -- because the only other progress line
    is emitted when a row *finishes*. A quiet hour is indistinguishable from a
    hung session, which is the wrong thing to make someone guess about.

    The solvers call ``progress`` every ``_HB_CHECK_EVERY`` (1024) pops, i.e.
    about once a second, so the wall-clock gate here is what sets the rate; the
    callback itself is result-neutral. The row name leads every line because
    with more than one worker these interleave.
    """
    state = {"t0": time.time(), "last": time.time()}

    def progress(n):
        now = time.time()
        if now - state["last"] < every:
            return
        state["last"] = now
        elapsed = now - state["t0"]
        rate = n / elapsed if elapsed > 0 else 0.0
        eta = (budget - n) / rate if rate > 0 else float("inf")
        log(f"      {name}: {n:,}/{budget:,} nodes ({100.0 * n / budget:.1f}%) "
            f"{rate:,.0f} n/s, ~{eta / 60:.0f} min left on this row")
    return progress


# Set in each pool worker by ``_init_worker``. A spawn worker is a fresh
# interpreter whose ``sys.stdout`` is the real fd 1 -- which under Colab is the
# kernel's log, NOT the cell output -- so anything a worker prints is invisible in
# the notebook. That is why the heartbeat showed up on the single-worker arm
# (which runs in the parent) and vanished on the three-worker one. Workers hand
# their lines to the parent over this queue instead of printing them.
_WORKER_LOG_Q = None


def _init_worker(q):
    global _WORKER_LOG_Q
    _WORKER_LOG_Q = q


def _worker_log(msg):
    """Send one line to the parent, or print it when running in the parent."""
    if _WORKER_LOG_Q is None:
        print(msg, flush=True)
        return
    try:
        _WORKER_LOG_Q.put_nowait(msg)
    except Exception:                  # a full or closed queue must not kill a row
        pass


def _job(args):
    arm, row, budget, mrl, heartbeat_secs = args
    _, spec = resolve_arm(arm)
    # Both caches in heuristics are module-level and unbounded, so in a worker
    # that handles more than one row they carry the previous row's states into
    # the next one's memory ceiling. Rows are independent; start each one clean.
    _heur._STATE_CACHE.clear()
    _heur._WORD_CACHE.clear()
    t = time.time()
    st = spec["run"](row["r1"], row["r2"], budget, mrl,
                     progress=_in_search_heartbeat(row["name"], budget,
                                                   heartbeat_secs,
                                                   log=_worker_log))
    return {
        "name": row["name"],
        "arm": arm,
        "r1": row["r1"],
        "r2": row["r2"],
        "budget": budget,
        "max_relator_length": mrl,
        "solved": bool(st["solved"]),
        "nodes_explored": int(st["nodes_explored"]),
        "path_length": st["path_length"],
        "min_relator_length": st["min_relator_length"],
        "max_relator_length_expanded": st["max_relator_length_expanded"],
        "seconds": round(time.time() - t, 3),
    }


def read_rows(path):
    """Rows in ``path``; empty when it does not exist yet or ends mid-line.

    A REPORT cell run before its RUN cell is an ordinary thing to do in a
    notebook, and so is reading a jsonl a dropped session left half-written.
    """
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except ValueError:
                continue
    return rows


def _done(path):
    return {r["name"] for r in read_rows(path) if "name" in r}


def _ensure_trailing_newline(path):
    """Terminate a torn last line so the next append starts a FRESH line.

    A hard stop mid-write can leave the jsonl ending without a newline.
    ``read_rows`` already refuses such a line (a strict prefix of a JSON
    object never parses), so resume can never count it as finished -- but an
    append reopened onto it would weld the next record to the torn tail,
    making that one GOOD record unparseable too. One byte closes the hole.
    """
    try:
        with open(path, "rb+") as f:
            f.seek(0, os.SEEK_END)
            if f.tell() == 0:
                return
            f.seek(-1, os.SEEK_END)
            if f.read(1) != b"\n":
                f.write(b"\n")
    except OSError:
        pass                       # no file yet: "a" below will create it


def out_path(arm, out_dir, budget=NODE_BUDGET, mrl=MAX_RELATOR_LENGTH):
    """The jsonl for one (arm, budget, cap). RUN and REPORT must agree on it."""
    key, _ = resolve_arm(arm)
    return os.path.join(out_dir, f"leftovers_1m_{key}_b{budget}_mrl{mrl}.jsonl")


def classify(rows, budget=NODE_BUDGET, checkpoints=CHECKPOINTS):
    """Split result rows, and read the smaller budgets off the same run.

    ``anytime`` is free: a row solved after N pops was solved at every budget >= N
    and unsolved below it. ``solved_at_or_below_100k`` should be EMPTY -- every row
    in this experiment was unsolved at 100,000 by construction, so a name in there
    says the search that ran is not the search that built the list.
    """
    solved, unsolved, suspicious = [], [], []
    for r in rows:
        if r.get("solved") and int(r["nodes_explored"]) <= budget:
            solved.append(r["name"])
            if int(r["nodes_explored"]) <= 100_000:
                suspicious.append(r["name"])
        else:
            unsolved.append(r["name"])
    return {
        "n": len(rows),
        "solved_at_1m": solved,
        "unsolved_at_1m": unsolved,
        "solved_at_or_below_100k": suspicious,
        "anytime": {c: sum(1 for r in rows
                           if r.get("solved") and int(r["nodes_explored"]) <= c)
                    for c in checkpoints},
    }


def run_arm(arm, out_dir, budget=NODE_BUDGET, mrl=MAX_RELATOR_LENGTH,
            n_workers="auto", resume=True, ids=None, csv_path=None,
            common_denominator=False, mirror_dir=None, limit=None,
            heartbeat_secs=60, log=print):
    """Run one arm to ``out_dir/leftovers_1m_<arm>_b<budget>_mrl<mrl>.jsonl``.

    Appends locally and mirrors the whole file to ``mirror_dir`` (Drive) as it
    goes -- never appends to a mount, which is the failure mode that silently
    truncates a jsonl when a Colab session drops.
    """
    key, spec = resolve_arm(arm)
    rows, used = load_rows(key, csv_path=csv_path, ids=ids,
                           common_denominator=common_denominator)
    if limit:
        rows = rows[:int(limit)]

    os.makedirs(out_dir, exist_ok=True)
    out = out_path(key, out_dir, budget, mrl)
    if resume:
        _seed_from_mirror(out, mirror_dir, log)
    seen = _done(out) if resume else set()
    todo = [r for r in rows if r["name"] not in seen]

    n_workers, per_gb = resolve_workers(key, n_workers, budget=budget, mrl=mrl)
    log(f"  arm     : {key} -- {spec['label']}")
    log(f"  rows    : {len(rows)} from {used}"
        + ("  [common denominator]" if common_denominator else ""))
    log(f"  budget  : {budget:,} nodes, cap {mrl}")
    log(f"  engine  : {'hcompact (packed arena, numba)' if HAVE_HCOMPACT else 'python fallback'}")
    log(f"  workers : {n_workers} (~{per_gb:.1f} GB/search reserved)")
    log(f"  resume  : {len(seen)} row(s) already on disk, {len(todo)} to run")
    log(f"  -> {out}")

    t0 = time.time()
    last = t0
    jobs = [(key, r, budget, mrl, heartbeat_secs) for r in todo]
    done = 0
    if jobs:
        _ensure_trailing_newline(out)
        with open(out, "a") as fh:
            for rec in _iter_results(jobs, n_workers, log):
                fh.write(json.dumps(rec) + "\n")
                fh.flush()
                done += 1
                last = _beat(rec, done, len(jobs), t0, last, heartbeat_secs,
                             out, mirror_dir, log)
    _mirror(out, mirror_dir)
    log(f"  {done} row(s) run in {time.time() - t0:,.0f}s; jsonl at {out}")
    return out


def _iter_results(jobs, n_workers, log=print):
    if n_workers <= 1:
        for j in jobs:                 # in-process: the heartbeat prints directly
            yield _job(j)
        return
    # maxtasksperchild=1: every row gets a fresh interpreter, so one row's peak
    # RSS cannot become the next row's floor. The cost is a numba re-import per
    # row (seconds, and cached on disk) against a search measured in hours.
    #
    # The queue goes in through `initializer`, not as a task argument -- a
    # multiprocessing Queue cannot be pickled into an imap payload. The parent is
    # blocked on imap_unordered for the length of a row, so a daemon thread does
    # the draining; printing is the parent's job because only the parent's stdout
    # is the one Colab renders.
    ctx = mp.get_context("spawn")
    q = ctx.Queue()
    stop = threading.Event()

    def drain():
        while True:
            try:
                log(q.get(timeout=0.25))
            except _queue.Empty:
                if stop.is_set():
                    return
            except (OSError, ValueError):      # queue closed under us
                return

    pump = threading.Thread(target=drain, daemon=True)
    pump.start()
    try:
        with ctx.Pool(n_workers, initializer=_init_worker, initargs=(q,),
                      maxtasksperchild=1) as pool:
            for rec in pool.imap_unordered(_job, jobs):
                yield rec
    finally:
        stop.set()
        pump.join(timeout=5.0)


def _beat(rec, done, total, t0, last, every, out, mirror_dir, log):
    """Print the completed-row line. Not rate-limited: a row is 25-80 minutes at
    this budget, so every one of them is worth a line. The per-second reporting
    happens inside the search, in ``_in_search_heartbeat``."""
    now = time.time()
    rate = done / max(now - t0, 1e-9)
    eta = (total - done) / rate if rate else float("inf")
    if rec.get("error"):
        # a crash-guarded row has no node count; the progress line must not be
        # a second casualty of the row that just failed
        body = f"ERROR ({rec['error'][:80]})"
    else:
        body = (f"solved={rec['solved']} nodes={rec['nodes_explored']:,} "
                f"({rec['seconds']:.0f}s)")
    log(f"    [{done}/{total}] {rec['name']} {body} -- "
        f"{rate * 3600:.1f} rows/h, eta {eta / 3600:.1f} h")
    _mirror(out, mirror_dir)
    return now


def _seed_from_mirror(out, mirror_dir, log=print):
    """Copy the Drive jsonl back down when it holds rows the local one does not.

    RESUME reads the LOCAL jsonl, but Colab recycles ``/content`` -- the clone,
    the results directory and all -- while Drive survives. Without this, a
    session that comes back to a wiped VM re-runs every row it already paid for,
    which at 25-80 minutes a row is the difference between resuming and starting
    over. The mirror is written whole-file from the local copy, so normally Drive
    is a prefix of local and this is a no-op; it only fires when local is behind.
    """
    if not mirror_dir:
        return
    src = os.path.join(mirror_dir, os.path.basename(out))
    try:
        if not os.path.exists(src):
            return
        theirs, ours = len(_done(src)), len(_done(out))
        if theirs > ours:
            os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
            shutil.copyfile(src, out)
            log(f"  resume  : seeded {theirs} row(s) back from the Drive mirror "
                f"(local had {ours})")
    except OSError as e:
        log(f"  [warn] could not read the Drive mirror ({e}); "
            f"resuming from the local jsonl only")


def _mirror(out, mirror_dir):
    if not mirror_dir:
        return
    try:
        os.makedirs(mirror_dir, exist_ok=True)
        shutil.copyfile(out, os.path.join(mirror_dir, os.path.basename(out)))
    except OSError as e:                    # a dropped mount must not kill the run
        print(f"    [warn] Drive mirror failed ({e}); local jsonl is authoritative")


# ---------------------------------------------------------------------- report
def report(arm, out_dir, budget=NODE_BUDGET, mrl=MAX_RELATOR_LENGTH,
           common_denominator=False, write_ids=True, log=print):
    """Print what the 1M budget bought and write the id lists it produced.

    ``mrl`` is part of the jsonl filename, so a report that defaults it while the
    run overrode it reads an empty directory and says "no rows" about a finished
    run. Callers pass the same value to both.
    """
    key, spec = resolve_arm(arm)
    out = out_path(key, out_dir, budget, mrl)
    rows = read_rows(out)
    if not rows:
        log(f"no rows yet at {out}")
        return None
    if common_denominator:
        drop = set(COMMON_DENOMINATOR_EXCLUDED.get(key, ()))
        rows = [r for r in rows if r["name"] not in drop]
    c = classify(rows, budget=budget)
    expected = spec["n_common"] if common_denominator else spec["n_rows"]
    n_solved = len(c["solved_at_1m"])

    log("")
    log(f"=== {key} -- {spec['label']}")
    log(f"    rows complete        : {len(rows)}/{expected}"
        + ("" if len(rows) == expected else
           "   (PARTIAL -- these numbers are not final)"))
    pct = f"   ({100.0 * n_solved / len(rows):.1f}%)" if rows else ""
    log(f"    solved at {budget:>9,}  : {n_solved}{pct}")
    log(f"    still unsolved       : {len(c['unsolved_at_1m'])}")
    log("    anytime (free -- one search answers every budget below it):")
    for cp in sorted(c["anytime"]):
        log(f"      <= {cp:>9,} : {c['anytime'][cp]}")
    if c["solved_at_or_below_100k"]:
        # Every row here failed at 100,000 in the run that built the list, so this
        # cannot happen unless a different search is running.
        log(f"    !! {len(c['solved_at_or_below_100k'])} row(s) solved at or below "
            f"100,000 nodes, which the 100k run says is impossible: "
            f"{c['solved_at_or_below_100k'][:5]}")
        log("       -> the search being run is not the one that built this list; "
            "stop and check the arm, the cap and the row list before reading "
            "anything above.")

    if write_ids:
        for stem, ids in (("solved_at_1m", c["solved_at_1m"]),
                          ("still_unsolved_1m", c["unsolved_at_1m"])):
            p = os.path.join(out_dir, f"{stem}_{key}.txt")
            with open(p, "w") as f:
                f.write("".join(n + "\n" for n in ids))
            log(f"    {stem} ids -> {p}")
    return c


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--arm", required=True, choices=sorted(ARMS))
    ap.add_argument("--out-dir", default=os.path.join(
        ROOT, "results", "heuristic_search", "leftovers_1m"))
    ap.add_argument("--budget", type=int, default=NODE_BUDGET)
    ap.add_argument("--workers", default="auto")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--common-denominator", action="store_true",
                    help="drop the rows outside the 70,723-orbit intersection "
                         "(one, on the greedy arm) so the count matches 221")
    ap.add_argument("--smoke", action="store_true",
                    help="2 rows at a 2,000-node budget -- proves the pipeline, "
                         "measures nothing")
    a = ap.parse_args(argv)
    budget, limit = a.budget, a.limit
    out_dir = a.out_dir
    if a.smoke:
        budget, limit = 2_000, 2
        out_dir = out_dir + "_smoke"
    run_arm(a.arm, out_dir, budget=budget, n_workers=a.workers, limit=limit,
            common_denominator=a.common_denominator)
    report(a.arm, out_dir, budget=budget,
           common_denominator=a.common_denominator)


if __name__ == "__main__":
    main()
