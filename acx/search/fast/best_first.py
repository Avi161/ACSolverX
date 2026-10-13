"""The fast best-first engine: ``acx.search.spec``'s search on flat numba arrays, with the same ``Result``.

The pieces: ``arrays.Arrays`` (the state arena and its growth), ``heap`` (the ordered heap of state ids), ``dedup``
(the open-addressing table of discovered states), ``cap_stats`` (the cap counters, computed after the search) and the
kernels in ``kernels`` (children, scores). This module is the pop loop and the Python wrapper that sizes the arrays
and builds the ``Result``. Uncapped searches skip the cap counters.

``_run`` pops until solved, empty or out of budget, and returns early (before popping) when the next pop's children
might not fit: ``NEED_CAPACITY`` (the arrays and table are doubled and rehashed) or, uncapped only, ``NEED_WIDTH``
(the arena is re-laid at a wider row). With a cap the row width is ``max(cap, longest start relator)`` and never
changes.
"""
import numpy as np
from numba import njit

from ...core.capcount import blank
from ...core.moves import Move
from ...core.words import Presentation, fmt
from ..engine import Result
from .arrays import Arrays
from .cap_stats import cap_counts
from .counters import (COUNTER_SIZE, DMIN_T, DROPPED, EXP_ID, EXP_T, HEAP_LEN, MAX_T, MIN_T, N_DISC, NEED_CAPACITY,
                       NEED_WIDTH, NODES, OK, SOLVED, SOLVED_ID)
from .dedup import find_slot, hash_state, rehash
from .heap import heap_pop, heap_push
from .kernels import child_width, decode, encode, expand_drops, max_children, priority_id, score


@njit(inline="always")
def _store_state(arena, lens, sid, row, rlen):
    """Copy a child into the arena; returns its total length."""
    total = 0
    for r in range(len(rlen)):
        n = rlen[r]
        lens[sid, r] = n
        total += n
        for t in range(n):
            arena[sid, r, t] = row[r, t]
    return total


@njit(cache=True)
def _run(arena, lens, depth, prio, parent, pmove, heap, table, trace, st,
         budget, n_gen, cap, cyclic, pid, track, out, out_len, out_mv, popped, dmin):
    """Pop and expand until solved, empty or out of budget; returns ``OK``, ``SOLVED`` or a ``NEED_*`` code.

    The heap orders state ids by ``(prio, depth, relators by key_code with a proper prefix first)``, which is
    spec's ``state_key`` order. When counting the cap (``len(popped) > 0``) it records per pop the popped id and the
    least score ``dmin`` of the children the cap dropped, for ``cap_stats`` (stage 1: the drops are scored, not built).
    """
    counting = len(popped) > 0
    dout = np.empty((0, 1, 1), dtype=np.uint8)               # no drop is built in stage 1
    dout_len = np.empty((0, 1), dtype=np.int32)
    dprio = np.empty(0, dtype=np.float64)
    while st[NODES] < budget:
        if st[HEAP_LEN] == 0:
            return OK
        top = heap[0]
        max_new = max_children(lens[top])
        if st[N_DISC] + max_new > len(depth) or 2 * (st[N_DISC] + max_new) > len(table):
            return NEED_CAPACITY
        if cap < 0 and child_width(lens[top]) > arena.shape[2]:
            return NEED_WIDTH
        if max_new > len(out):          # the larger buffers last for the rest of this call only
            out = np.empty((2 * max_new, out.shape[1], out.shape[2]), dtype=np.uint8)
            out_len = np.empty((2 * max_new, out.shape[1]), dtype=np.int32)
            out_mv = np.empty((2 * max_new, 5), dtype=np.int32)

        # Pop.
        st[HEAP_LEN] = heap_pop(heap, st[HEAP_LEN], prio, depth, arena, lens, n_gen)
        pop_no = st[NODES]
        st[NODES] += 1
        if len(trace) > 0:
            trace[pop_no] = top
        if counting:
            popped[pop_no] = top
            dmin[pop_no] = np.inf
        total = 0
        solved = True
        for r in range(lens.shape[1]):
            total += lens[top, r]
            solved = solved and lens[top, r] == 1
        if total > st[EXP_T]:
            st[EXP_T] = total
            st[EXP_ID] = top
        if solved:
            st[SOLVED_ID] = top
            return SOLVED

        # Expand: store and push every child not seen before.
        count, rejected, _, least_drop, least_drop_total = expand_drops(
            arena[top], lens[top], n_gen, cap, cyclic, out, out_len, out_mv,
            dout, dout_len, dprio, pid if counting else -1, -np.inf, True)
        if rejected > 0:
            st[DROPPED] += rejected
            if st[DMIN_T] < 0 or least_drop_total < st[DMIN_T]:
                st[DMIN_T] = least_drop_total
            dmin[pop_no] = least_drop
        for c in range(count):
            row, rlen = out[c], out_len[c]
            slot = find_slot(table, arena, lens, row, rlen, hash_state(row, rlen))
            if table[slot] != 0:
                continue
            sid = st[N_DISC]
            st[N_DISC] = sid + 1
            table[slot] = sid + 1
            child_total = _store_state(arena, lens, sid, row, rlen)
            depth[sid] = depth[top] + 1
            prio[sid] = score(row, rlen, n_gen, pid)
            if track:
                parent[sid] = top
                pmove[sid] = out_mv[c]
            st[MIN_T] = min(st[MIN_T], child_total)
            st[MAX_T] = max(st[MAX_T], child_total)
            st[HEAP_LEN] = heap_push(heap, st[HEAP_LEN], sid, prio, depth, arena, lens, n_gen)
    return OK


def _initial_arrays(start, cfg, pid):
    """Arrays holding the start as state 0 (and the heap), and the counters array ``st``."""
    n_gen, R = start.n_gen, len(start.rels)
    syms, lens = encode(start.rels, n_gen, width=cfg.cap)     # uncapped: the start, widened on demand
    room = max(1024, min(cfg.budget, 1 << 16) * 8) + int(max_children(lens))
    arrays = Arrays(room, R, syms.shape[1], cfg.capture_path)
    arrays.arena[0], arrays.lens[0], arrays.depth[0], arrays.heap[0] = syms, lens, 0, 0
    arrays.prio[0] = score(syms, lens, n_gen, pid)
    arrays.parent[0] = -1
    rehash(arrays.table, arrays.arena, arrays.lens, 1)
    st = np.zeros(COUNTER_SIZE, dtype=np.int64)
    st[HEAP_LEN], st[N_DISC], st[SOLVED_ID], st[DMIN_T] = 1, 1, -1, -1
    st[MIN_T] = st[MAX_T] = st[EXP_T] = int(lens.sum())
    return arrays, st


def _result(arrays, st, status, start, cfg, pid, trace, popped, dmin, width):
    """Spec's ``Result`` from the engine's final arrays and counters."""
    n_gen = start.n_gen

    def rels(sid):
        return decode(arrays.arena[sid], arrays.lens[sid], n_gen)

    solved = status == SOLVED
    caps = blank()
    if cfg.cap is not None:
        caps = cap_counts(arrays, st, start, cfg, pid, popped, dmin, solved)
    path = end = depth = None
    if solved:
        sid = int(st[SOLVED_ID])
        end = Presentation(n_gen, rels(sid))
        depth = int(arrays.depth[sid])
        if cfg.capture_path:
            moves = []
            while arrays.parent[sid] >= 0:
                moves.append(Move(*map(int, arrays.pmove[sid])))
                sid = int(arrays.parent[sid])
            path = tuple(reversed(moves))
    stats = {"discovered": int(st[N_DISC]), **caps, "min_total": int(st[MIN_T]), "max_total": int(st[MAX_T]),
             "max_total_expanded": int(st[EXP_T]),
             "max_expanded": tuple(map(fmt, rels(int(st[EXP_ID])))), "row_width": width}
    popped_states = None
    if cfg.trace:
        popped_states = tuple(tuple(map(fmt, rels(int(sid)))) for sid in trace[:st[NODES]])
    return Result(solved, int(st[NODES]), path, start, end, stats, popped_states, depth)


def run(start, cfg):
    """Search from ``start`` (a normal form) under ``cfg``; spec's ``Result``, step for step."""
    n_gen, R = start.n_gen, len(start.rels)
    pid = priority_id(cfg.priority, start.rels)
    cap = -1 if cfg.cap is None else cfg.cap
    arrays, st = _initial_arrays(start, cfg, pid)
    width = arrays.arena.shape[2]
    trace = np.empty(cfg.budget if cfg.trace else 0, dtype=np.int32)
    rows = max(int(max_children(arrays.lens[0])), 64)
    out = np.empty((rows, R, width), dtype=np.uint8)
    out_len = np.empty((rows, R), dtype=np.int32)
    out_mv = np.empty((rows, 5), dtype=np.int32)
    counting = cfg.cap is not None
    popped = np.empty(cfg.budget if counting else 0, dtype=np.int32)
    dmin = np.empty(cfg.budget if counting else 0, dtype=np.float64)
    while True:
        status = _run(arrays.arena, arrays.lens, arrays.depth, arrays.prio, arrays.parent, arrays.pmove,
                      arrays.heap, arrays.table, trace, st, cfg.budget, n_gen, cap, cfg.cyclic, pid,
                      cfg.capture_path, out, out_len, out_mv, popped, dmin)
        if status == NEED_CAPACITY:
            arrays = arrays.grow(2 * arrays.capacity, width, int(st[N_DISC]), int(st[HEAP_LEN]))
        elif status == NEED_WIDTH:
            width = max(2 * width, int(child_width(arrays.lens[arrays.heap[0]])))
            arrays = arrays.grow(arrays.capacity, width, int(st[N_DISC]), int(st[HEAP_LEN]))
            out = np.empty((len(out), R, width), dtype=np.uint8)
        else:
            break
    return _result(arrays, st, status, start, cfg, pid, trace, popped, dmin, width)
