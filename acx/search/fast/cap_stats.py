"""The cap counters of the fast engine, computed after the search from what it recorded.

Stage 1 runs inside the pop loop (``best_first._run``): every dropped child is scored from its reduced relator,
building none; per pop only the popped id and the least drop score ``dmin`` are kept, plus the per-move count and
least total.

Stage 2 is here. A dropped child can only be popped before a later bar if its score is at most the largest score
popped after it (``smax``, a suffix maximum). If no pop has ``dmin <= smax`` then ``cap_would_pop`` is 0 and nothing
more is computed, so a cap that never binds is cheap. Otherwise ``_replay`` walks the recorded pops with the numba
twin of ``CapCount``: each pop's bar (``cc_pop``) and, at the pops that may matter, the drops scoring ``<= smax``
(``cc_drop``). A drop above ``smax`` never drains, nor does any later drop of the same state, so leaving them out
changes no count.
"""
import numpy as np
from numba import njit

from ...core.capcount import C_POOL, CapArrays, blank, cc_drop, cc_free, cc_pop
from ...core.words import state_bytes
from .counters import DMIN_T, DROPPED, HEAP_LEN, NODES
from .kernels import expand_drops, max_children, tie_bytes


@njit(cache=True)
def _suffix_max(prio, popped, n, dry):
    """``smax[t]``: the largest score popped after pop ``t`` (``inf`` from a dry queue, whose pending drops would
    pop next)."""
    smax = np.empty(n, dtype=np.float64)
    largest = np.inf if dry else -np.inf
    for t in range(n - 1, -1, -1):
        smax[t] = largest
        largest = max(largest, prio[popped[t]])
    return smax


@njit(cache=True)
def _replay(arena, lens, depth, prio, popped, n, t0, smax, live, n_gen, cap, cyclic, pid,
            out, out_len, out_mv, dout, dout_len, dprio, bar, cc):
    """The exact counter over the recorded pops ``t0..n-1`` (``live[t]``: pop ``t``'s drops may matter).

    Returns the pop to resume from when the counter's arrays need to grow, else ``n``.
    """
    R = lens.shape[1]
    for t in range(t0, n):
        top = popped[t]
        if live[t]:
            room = max_children(lens[top])
            if not cc_free(cc, room, room * (R * dout.shape[2] + R)):
                return t
            if room > len(out):
                out = np.empty((2 * room, R, out.shape[2]), dtype=np.uint8)
                out_len = np.empty((2 * room, R), dtype=np.int32)
                out_mv = np.empty((2 * room, 5), dtype=np.int32)
                dout = np.empty((2 * room, R, dout.shape[2]), dtype=np.uint8)
                dout_len = np.empty((2 * room, R), dtype=np.int32)
                dprio = np.empty(2 * room, dtype=np.float64)
        # The bar comes before this pop's own drops (the solving pop included).
        bar_len = tie_bytes(arena[top], lens[top], n_gen, bar, 0)
        cc_pop(cc, prio[top], depth[top], bar, bar_len)
        if not live[t]:
            continue
        _, _, dcount, _, _ = expand_drops(arena[top], lens[top], n_gen, cap, cyclic, out, out_len, out_mv,
                                          dout, dout_len, dprio, pid, smax[t], False)
        child_depth = depth[top] + 1
        pool = cc[8]
        for c in range(dcount):
            total = longest = 0
            for r in range(R):
                total += dout_len[c, r]
                longest = max(longest, dout_len[c, r])
            key_len = tie_bytes(dout[c], dout_len[c], n_gen, pool, cc[0][C_POOL])
            cc_drop(cc, dprio[c], child_depth, key_len, total, longest)
    return n


def cap_counts(arrays, st, start, cfg, pid, popped, dmin, solved):
    """The cap counters' record, with spec's exact values.

    ``st`` is the engine's counters array (``counters``), ``popped`` / ``dmin`` stage 1's per-pop record.
    """
    n, R = int(st[NODES]), len(start.rels)
    left = cfg.budget - n
    dry = not solved and st[HEAP_LEN] == 0 and left > 0
    record = blank(cap=cfg.cap)
    record["cap_dropped"] = int(st[DROPPED])
    record["cap_dropped_min_total"] = int(st[DMIN_T]) if st[DMIN_T] >= 0 else None
    if not record["cap_dropped"]:
        return record
    smax = _suffix_max(arrays.prio, popped, n, dry)
    live = (dmin[:n] < np.inf) & (dmin[:n] <= smax)
    if not live.any():
        return record

    counter = CapArrays(cfg.cap)
    counter.known(state_bytes(start.rels, start.n_gen))
    width = arrays.arena.shape[2]
    longest_popped = int(arrays.lens[popped[:n]].max(axis=1).max())
    drop_width = max(2 * cfg.cap, 2 * longest_popped)              # child_width of any popped state
    rows = 64
    out = np.empty((rows, R, width), dtype=np.uint8)
    out_len = np.empty((rows, R), dtype=np.int32)
    out_mv = np.empty((rows, 5), dtype=np.int32)
    dout = np.empty((rows, R, drop_width), dtype=np.uint8)
    dout_len = np.empty((rows, R), dtype=np.int32)
    dprio = np.empty(rows, dtype=np.float64)
    bar = np.empty(R * (width + 1), dtype=np.uint8)
    t = 0
    while t < n:
        t = _replay(arrays.arena, arrays.lens, arrays.depth, arrays.prio, popped, n, t, smax, live, start.n_gen,
                    cfg.cap, cfg.cyclic, pid, out, out_len, out_mv, dout, dout_len, dprio, bar, counter.cc)
        if t < n:                                                   # the counter's arrays are full: grow, resume
            room = int(max_children(arrays.lens[popped[t]]))
            counter.grow(room, room * (R * drop_width + R))
    counter.end(dry, left)
    counted = counter.record()
    return {**record, **{k: counted[k] for k in ("cap_would_pop", "cap_first_bind", "cap_needed")}}
