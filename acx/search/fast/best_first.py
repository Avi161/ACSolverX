"""The fast best-first engine: ``acx.search.spec``'s search on flat numba arrays.

Ported from ``hcompact`` (``origin/codex/ac-elementary-decoder:experiments/
heuristic_search/core/hcompact.py``, blob 046a6003, commit d01a315f, the
newest of its versions), generalised to any number of relators and to a
configurable or absent cap.

Layout: state ``sid`` is ``arena[sid]`` (``(R, W)`` uint8 Booth symbols) with
``lens[sid]``, ``depth``, ``prio`` (float64), ``parent`` and ``pmove``
(``(i, j, s, k1, k2)`` as int32, so path capture has no limit on the cap). The
heap is an int32 binary heap of state ids ordered by
``(prio, depth, key)``, where ``key`` compares relators in turn by
``key_code``, a proper prefix first: exactly spec's ``state_key`` tuples. Keys
are unique (dedup before push), so the order is strict and the pop sequence
does not depend on the heap. Dedup is an open-addressing int32 table (FNV-1a
over the lengths and symbols, linear probing).

``_run`` pops until solved, empty or out of budget, and returns early (before
popping) when the next pop's children might not fit: ``NEED_CAPACITY`` (the
arrays and table are doubled and rehashed), ``NEED_CC`` (the cap counter's
arrays are grown) or, uncapped only, ``NEED_WIDTH`` (the arena is re-laid at a
wider row). With a cap the row width is ``max(cap, longest start relator)`` and
never changes.

Cap counters (``acx.core.capcount``), with spec's exact values, in two stages
so that a cap that never binds costs almost nothing:

1. The search scores every dropped child from its reduced relator (no
   canonicalisation; ``expand_drops`` with ``dmax = -inf`` builds none) and
   keeps, per pop, the popped state id and the least dropped score ``dmin``,
   plus the per-move count and least total.
2. A dropped child can only be popped before a later bar if its score is at
   most the largest score popped after it (``smax``, a suffix maximum). Pops
   with ``dmin <= smax`` are the only ones whose drops can matter: none, and
   ``cap_would_pop`` is 0. Otherwise ``_replay`` walks the recorded pops again
   with the numba twin of ``CapCount``: each pop's bar (``cc_pop``) and, at those
   pops, the drops scoring ``<= smax`` (``cc_drop``, keyed ``(prio, depth,
   tie bytes)``). A drop scoring above ``smax`` never drains, and neither does
   any later drop of the same state (same score, ``smax`` only falls), so
   leaving them out changes no count. The start's bytes are seeded as known.

Uncapped searches skip all of it.
"""
import numpy as np
from numba import njit

from ...core.capcount import C_POOL, CapArrays, blank, cc_drop, cc_free, cc_pop
from ...core.moves import Move
from ...core.words import Presentation, fmt, state_bytes
from ..engine import Result
from .kernels import child_width, decode, encode, expand_drops, key_code, max_children, priority_id, score, tie_bytes

OK, SOLVED, NEED_CAPACITY, NEED_WIDTH, NEED_CC = 0, 1, 2, 3, 4
# st slots
# st slots; DROPPED / DMIN_T: the cap's per-move count and least dropped total (-1: none)
NODES, HEAP_LEN, N_DISC, MIN_T, MAX_T, EXP_T, EXP_ID, SOLVED_ID, DROPPED, DMIN_T = range(10)


@njit(inline="always")
def _hash(row, rlen):
    h = np.uint64(1469598103934665603)
    p = np.uint64(1099511628211)
    for r in range(len(rlen)):
        h = (h ^ np.uint64(rlen[r] + 256)) * p
        for t in range(rlen[r]):
            h = (h ^ np.uint64(row[r, t])) * p
    return h ^ (h >> np.uint64(29))


@njit(inline="always")
def _same(arena, lens, sid, row, rlen):
    for r in range(len(rlen)):
        if lens[sid, r] != rlen[r]:
            return False
    for r in range(len(rlen)):
        for t in range(rlen[r]):
            if arena[sid, r, t] != row[r, t]:
                return False
    return True


@njit(inline="always")
def _find(table, arena, lens, row, rlen, h):
    """Slot holding the state equal to ``row``, or the empty slot where it goes."""
    mask = np.uint64(len(table) - 1)
    i = np.int64(h & mask)
    while table[i] != 0 and not _same(arena, lens, table[i] - 1, row, rlen):
        i = (i + 1) & (len(table) - 1)
    return i


@njit(cache=True)
def _rehash(table, arena, lens, n):
    table[:] = 0
    for sid in range(n):
        table[_find(table, arena, lens, arena[sid], lens[sid], _hash(arena[sid], lens[sid]))] = sid + 1


@njit(inline="always")
def _less(a, b, prio, depth, arena, lens, n_gen):
    if prio[a] != prio[b]:
        return prio[a] < prio[b]
    if depth[a] != depth[b]:
        return depth[a] < depth[b]
    for r in range(lens.shape[1]):
        la, lb = lens[a, r], lens[b, r]
        for t in range(min(la, lb)):
            x, y = arena[a, r, t], arena[b, r, t]
            if x != y:
                return key_code(x, n_gen) < key_code(y, n_gen)
        if la != lb:
            return la < lb
    return False


@njit(cache=True)
def _run(arena, lens, depth, prio, parent, pmove, heap, table, trace, st,
         budget, n_gen, cap, cyclic, pid, track, out, out_len, out_mv, popped, dmin):
    counting = len(popped) > 0
    dout = np.empty((0, 1, 1), dtype=np.uint8)
    dout_len = np.empty((0, 1), dtype=np.int32)
    dprio = np.empty(0, dtype=np.float64)
    while st[NODES] < budget:
        hl = st[HEAP_LEN]
        if hl == 0:
            return OK
        top = heap[0]
        mc = max_children(lens[top])
        if st[N_DISC] + mc > len(depth) or 2 * (st[N_DISC] + mc) > len(table):
            return NEED_CAPACITY
        if cap < 0 and child_width(lens[top]) > arena.shape[2]:
            return NEED_WIDTH
        if mc > len(out):
            out = np.empty((2 * mc, out.shape[1], out.shape[2]), dtype=np.uint8)
            out_len = np.empty((2 * mc, out.shape[1]), dtype=np.int32)
            out_mv = np.empty((2 * mc, 5), dtype=np.int32)
        # pop
        hl -= 1
        st[HEAP_LEN] = hl
        if hl > 0:
            v = heap[hl]
            i = 0
            while True:
                c = 2 * i + 1
                if c >= hl:
                    break
                if c + 1 < hl and _less(heap[c + 1], heap[c], prio, depth, arena, lens, n_gen):
                    c += 1
                if _less(heap[c], v, prio, depth, arena, lens, n_gen):
                    heap[i] = heap[c]
                    i = c
                else:
                    break
            heap[i] = v
        if len(trace) > 0:
            trace[st[NODES]] = top
        t_pop = st[NODES]
        st[NODES] += 1
        if counting:
            popped[t_pop] = top
            dmin[t_pop] = np.inf
        tot = 0
        done = True
        for r in range(lens.shape[1]):
            tot += lens[top, r]
            done = done and lens[top, r] == 1
        if tot > st[EXP_T]:
            st[EXP_T] = tot
            st[EXP_ID] = top
        if done:
            st[SOLVED_ID] = top
            return SOLVED
        # stage 1 of the cap counter: score the drops, build none
        count, rej, _, dm, tm = expand_drops(arena[top], lens[top], n_gen, cap, cyclic, out, out_len, out_mv,
                                             dout, dout_len, dprio, pid if counting else -1, -np.inf, True)
        if rej > 0:
            st[DROPPED] += rej
            if st[DMIN_T] < 0 or tm < st[DMIN_T]:
                st[DMIN_T] = tm
            dmin[t_pop] = dm
        d1 = depth[top] + 1
        for c in range(count):
            row, rlen = out[c], out_len[c]
            slot = _find(table, arena, lens, row, rlen, _hash(row, rlen))
            if table[slot] != 0:
                continue
            sid = st[N_DISC]
            st[N_DISC] = sid + 1
            table[slot] = sid + 1
            ct = 0
            for r in range(len(rlen)):
                n = rlen[r]
                lens[sid, r] = n
                ct += n
                for t in range(n):
                    arena[sid, r, t] = row[r, t]
            depth[sid] = d1
            prio[sid] = score(row, rlen, n_gen, pid)
            if track:
                parent[sid] = top
                pmove[sid] = out_mv[c]
            st[MIN_T] = min(st[MIN_T], ct)
            st[MAX_T] = max(st[MAX_T], ct)
            i = hl
            hl += 1
            while i > 0:
                p = (i - 1) >> 1
                if _less(sid, heap[p], prio, depth, arena, lens, n_gen):
                    heap[i] = heap[p]
                    i = p
                else:
                    break
            heap[i] = sid
            st[HEAP_LEN] = hl
    return OK


@njit(cache=True)
def _suffix_max(prio, popped, n, dry):
    """``smax[t]``: the largest score popped after pop ``t`` (``inf`` from a dry queue, whose pending
    drops would pop next)."""
    smax = np.empty(n, dtype=np.float64)
    m = np.inf if dry else -np.inf
    for t in range(n - 1, -1, -1):
        smax[t] = m
        m = max(m, prio[popped[t]])
    return smax


@njit(cache=True)
def _replay(arena, lens, depth, prio, popped, n, t0, smax, live, n_gen, cap, cyclic, pid,
            out, out_len, out_mv, dout, dout_len, dprio, bar, cc):
    """Stage 2: the exact counter over the recorded pops ``t0..n-1`` (``live[t]``: pop ``t``'s drops may
    matter). Returns the pop to resume from when the counter's arrays need to grow, else ``n``."""
    R = lens.shape[1]
    for t in range(t0, n):
        top = popped[t]
        if live[t]:
            mc = max_children(lens[top])
            if not cc_free(cc, mc, mc * (R * dout.shape[2] + R)):
                return t
            if mc > len(out):
                out = np.empty((2 * mc, R, out.shape[2]), dtype=np.uint8)
                out_len = np.empty((2 * mc, R), dtype=np.int32)
                out_mv = np.empty((2 * mc, 5), dtype=np.int32)
                dout = np.empty((2 * mc, R, dout.shape[2]), dtype=np.uint8)
                dout_len = np.empty((2 * mc, R), dtype=np.int32)
                dprio = np.empty(2 * mc, dtype=np.float64)
        # the bar, before this pop's own drops (the solving pop included)
        cc_pop(cc, prio[top], depth[top], bar, tie_bytes(arena[top], lens[top], n_gen, bar, 0))
        if not live[t]:
            continue
        _, _, dcount, _, _ = expand_drops(arena[top], lens[top], n_gen, cap, cyclic, out, out_len, out_mv,
                                          dout, dout_len, dprio, pid, smax[t], False)
        d1 = depth[top] + 1
        pool = cc[8]
        for c in range(dcount):
            drow, dlen = dout[c], dout_len[c]
            ct = lg = 0
            for r in range(R):
                ct += dlen[r]
                lg = max(lg, dlen[r])
            nb = tie_bytes(drow, dlen, n_gen, pool, cc[0][C_POOL])
            cc_drop(cc, dprio[c], d1, nb, ct, lg)
    return n


class _Arrays:
    """The engine's arrays, grown by doubling (``NEED_CAPACITY``) or re-laid wider (``NEED_WIDTH``)."""

    def __init__(self, n, R, W, track):
        self.track = track
        self.arena = np.empty((n, R, W), dtype=np.uint8)
        self.lens = np.empty((n, R), dtype=np.int32)
        self.depth = np.empty(n, dtype=np.int32)
        self.prio = np.empty(n, dtype=np.float64)
        self.heap = np.empty(n, dtype=np.int32)
        self.parent = np.empty(n if track else 1, dtype=np.int32)
        self.pmove = np.empty((n if track else 1, 5), dtype=np.int32)
        self.table = np.zeros(1 << (2 * n - 1).bit_length(), dtype=np.int32)

    def grow(self, n_states, W, n_disc, heap_len):
        """A copy at ``n_states`` rows of width ``W`` holding the first ``n_disc`` states."""
        new = _Arrays(n_states, self.lens.shape[1], W, self.track)
        k = n_disc
        new.arena[:k, :, :self.arena.shape[2]] = self.arena[:k]
        for name in ("lens", "depth", "prio") + (("parent", "pmove") if self.track else ()):
            getattr(new, name)[:k] = getattr(self, name)[:k]
        new.heap[:heap_len] = self.heap[:heap_len]
        _rehash(new.table, new.arena, new.lens, k)
        return new


def run(start, cfg):
    """Search from ``start`` (reduced and canonical) under ``cfg``; spec's ``Result``, step for step."""
    n, R = start.n_gen, len(start.rels)
    pid = priority_id(cfg.priority, start.rels)
    cap = -1 if cfg.cap is None else cfg.cap
    syms, lens0 = encode(start.rels, n, width=cfg.cap)   # uncapped: the start, widened on demand
    W = syms.shape[1]
    a = _Arrays(max(1024, min(cfg.budget, 1 << 16) * 8) + int(max_children(lens0)), R, W, cfg.capture_path)
    a.arena[0], a.lens[0], a.depth[0], a.heap[0] = syms, lens0, 0, 0
    a.prio[0] = score(syms, lens0, n, pid)
    a.parent[0] = -1
    _rehash(a.table, a.arena, a.lens, 1)
    tot0 = int(lens0.sum())
    st = np.zeros(10, dtype=np.int64)
    st[HEAP_LEN], st[N_DISC], st[SOLVED_ID], st[DMIN_T] = 1, 1, -1, -1
    st[MIN_T] = st[MAX_T] = st[EXP_T] = tot0
    trace = np.empty(cfg.budget if cfg.trace else 0, dtype=np.int32)
    mc = max(int(max_children(lens0)), 64)
    out = np.empty((mc, R, W), dtype=np.uint8)
    out_len = np.empty((mc, R), dtype=np.int32)
    out_mv = np.empty((mc, 5), dtype=np.int32)
    counting = cfg.cap is not None
    popped = np.empty(cfg.budget if counting else 0, dtype=np.int32)
    dmin = np.empty(cfg.budget if counting else 0, dtype=np.float64)
    while True:
        status = _run(a.arena, a.lens, a.depth, a.prio, a.parent, a.pmove, a.heap, a.table, trace, st,
                      cfg.budget, n, cap, cfg.cyclic, pid, cfg.capture_path,
                      out, out_len, out_mv, popped, dmin)
        if status == NEED_CAPACITY:
            a = a.grow(2 * len(a.depth), W, int(st[N_DISC]), int(st[HEAP_LEN]))
        elif status == NEED_WIDTH:
            W = max(2 * W, int(child_width(a.lens[a.heap[0]])))
            a = a.grow(len(a.depth), W, int(st[N_DISC]), int(st[HEAP_LEN]))
            out = np.empty((len(out), R, W), dtype=np.uint8)
        else:
            break

    def rels(sid):
        return decode(a.arena[sid], a.lens[sid], n)

    solved = status == SOLVED
    sid = int(st[SOLVED_ID])
    caps = _cap_counts(a, st, start, cfg, pid, popped, dmin, solved) if counting else blank()
    path = end = None
    if solved:
        end = Presentation(n, rels(sid))
        if cfg.capture_path:
            path = []
            while a.parent[sid] >= 0:
                path.append(Move(*map(int, a.pmove[sid])))
                sid = int(a.parent[sid])
            path = tuple(reversed(path))
    stats = {"discovered": int(st[N_DISC]), **caps, "cap_rejected": caps["cap_dropped"],
             "min_total": int(st[MIN_T]), "max_total": int(st[MAX_T]),
             "max_total_expanded": int(st[EXP_T]),
             "max_expanded": tuple(map(fmt, rels(int(st[EXP_ID])))), "row_width": W}
    tr = tuple(tuple(map(fmt, rels(int(s)))) for s in trace[:st[NODES]]) if cfg.trace else None
    return Result(solved, int(st[NODES]), path, start, end, stats, tr)


def _cap_counts(a, st, start, cfg, pid, popped, dmin, solved):
    """The cap counter's record (stage 2 when some pop's drops may matter; module docstring)."""
    n, R = int(st[NODES]), len(start.rels)
    left = cfg.budget - n
    dry = not solved and st[HEAP_LEN] == 0 and left > 0
    rec = blank(cap=cfg.cap)
    rec["cap_dropped"] = int(st[DROPPED])
    rec["cap_dropped_min_total"] = int(st[DMIN_T]) if st[DMIN_T] >= 0 else None
    if not rec["cap_dropped"]:
        return rec
    smax = _suffix_max(a.prio, popped, n, dry)
    live = (dmin[:n] < np.inf) & (dmin[:n] <= smax)
    if not live.any():
        return rec
    ca = CapArrays(cfg.cap)
    ca.known(state_bytes(start.rels, start.n_gen))
    lens0 = a.lens[popped[:n]]
    W = a.arena.shape[2]
    Wd = max(2 * cfg.cap, int(lens0.max(axis=1).max()) * 2)          # child_width of any popped state
    mc = 64
    out = np.empty((mc, R, W), dtype=np.uint8)
    out_len = np.empty((mc, R), dtype=np.int32)
    out_mv = np.empty((mc, 5), dtype=np.int32)
    dout = np.empty((mc, R, Wd), dtype=np.uint8)
    dout_len = np.empty((mc, R), dtype=np.int32)
    dprio = np.empty(mc, dtype=np.float64)
    bar = np.empty(R * (W + 1), dtype=np.uint8)
    t = 0
    while t < n:
        t = _replay(a.arena, a.lens, a.depth, a.prio, popped, n, t, smax, live, start.n_gen, cfg.cap, cfg.cyclic,
                    pid, out, out_len, out_mv, dout, dout_len, dprio, bar, ca.cc)
        if t < n:
            k = int(max_children(a.lens[popped[t]]))
            ca.grow(k, k * (R * Wd + R))
    ca.end(dry, left)
    r = ca.record()
    return {**rec, **{k: r[k] for k in ("cap_would_pop", "cap_first_bind", "cap_needed")}}
