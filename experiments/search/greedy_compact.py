"""Memory-compact twin of ``GreedyHeavySolver`` — same search, numpy containers.

At a 1M node budget with ``max_relator_length=48`` a heavy search discovers
~63.7M states and costs a measured **220 bytes each**. Almost none of that is
data. Per state CPython holds:

    ~125 B  the packed ``bytes`` key   (33 B object header + ~92 B payload)
    ~ 32 B  its ``set`` entry          (hash + pointer, amortised)
      48 B  the ``(total, depth, key)`` heap tuple -- pure PyTupleObject overhead
    ~  9 B  the heap list's slot

So ~70% is object overhead. ``expand_node_nj`` -- the actual mathematics -- is
already ``@njit`` and is reused here **verbatim**. Only the containers change:

    arena   uint8[n * rw]   the two relators, 4 bits per symbol, fixed width
    len1/2  uint8[n]        symbol counts (the trivial test is len1==1==len2)
    depth   int32[n]        first-visit depth, the heap's second key
    heap    int32[n]        state ids, ordered by (total, depth, row)
    table   int32[tcap]     open-addressing visited set, stores id+1

which is ~66 B/state, a little over 3x smaller.

WHY THIS IS RESULT-IDENTICAL
============================
Every state is pushed **exactly once** (it is checked against ``visited`` before
being pushed), so no two heap entries share a row. ``(total, depth, row)`` is
therefore a *strict* total order with no true ties, and the pop sequence is
determined by the ordering relation alone -- not by the heap implementation.
``heapq`` is not a stable heap, but it never needs to be: no two entries compare
equal. A binary heap with the same comparison pops in the same order.

That leaves three things to preserve, and each is preserved by construction:

1. **The row must sort like the old key.** The old key is
   ``c1 + b'\\x00' + c2`` over order-preserving codes ``X=1 < Y=2 < x=3 < y=4``.
   Here each relator gets a fixed, byte-aligned region of ``w = (cap+1)//2``
   bytes, zero-padded, r1 then r2. Nibbles are stored most-significant first, so
   within a byte ``16*hi + lo`` is dominated by ``hi`` and nibble order *is* byte
   order. Zero pads below every code (codes are 1..4), which reproduces ``str``'s
   shorter-prefix-is-smaller rule at the first past-the-end slot. Byte-aligning
   r2's region stops a short r1 from shifting it. ``memcmp`` on the row therefore
   sorts exactly like the old key, and like ``(r1_str, r2_str)``.
2. **Children must be enumerated in the same order**, because ``depth`` is fixed
   by first-visit order. ``expand_node_nj`` is called unchanged.
3. **The min/max statistics** are tracked at the same moments: ``max_expanded``
   on POP, ``min``/``max`` on DISCOVERY with an ``elif`` (a first state that is
   both a new min and a new max updates only the min -- matching the original).

MEMORY IS RESERVED, NOT COMMITTED
=================================
The arrays are allocated once at their projected size and never copied. A
grow-by-copy on a 3 GB arena would hold old+new simultaneously, and four workers
resizing at once is a 30 GB spike -- the exact failure this module exists to
remove. ``np.empty`` returns lazily-faulted pages, so a presentation that solves
after 200 nodes touches ~200 rows and its RSS reflects that, not the reservation.
``bytes_touched()`` reports what is actually live; ``bytes_reserved()`` the
address space. If the projection is ever exceeded the arrays do grow, loudly.
"""

import numpy as np
from numba import njit

from experiments.search.greedy_baseline import (
    _HB_CHECK_EVERY,
    canonical_pair_nj,
    expand_node_nj,
    reduce_relator_nj,
    str_to_arr,
)

# Discovered states per node popped: discovered ~ A * budget**P. Measured on
# ms_reps_unsolved with the heavy solver and fitted on the mrl=48 row, which is
# an upper envelope for every smaller cap (they coincide until the cap binds).
# Duplicated from run_baseline rather than imported: the solver must not depend
# on the runner. Used only to size a reservation, never to change a result.
_DISCOVERY_A = 82.9
_DISCOVERY_P = 0.981
_RESERVE_SLACK = 1.5     # covers the ~1.3x per-presentation spread + fit error

_CODE_TO_CHAR = {1: 'X', 2: 'Y', 3: 'x', 4: 'y'}

# _run_chunk status codes
_OK, _SOLVED, _EMPTY, _NEED_CAPACITY = 0, 1, 2, 3


_CHAR_TO_CODE = {'X': 1, 'Y': 2, 'x': 3, 'y': 4}


def _next_pow2(n):
    p = 1
    while p < n:
        p <<= 1
    return p


def row_width(cap):
    """Bytes per arena row. Each relator gets a byte-aligned ``(cap+1)//2``."""
    return 2 * ((cap + 1) // 2)


def pack_row(r1, r2, cap):
    """``(r1_str, r2_str)`` -> the arena row, as ``bytes``. Python mirror of the
    njit packer, and the thing the heap's tie-break compares with ``memcmp``.

    Exists so the sort invariant -- that this sorts exactly like ``(r1, r2)`` and
    like ``greedy_baseline.pack_key`` -- can be tested without running a search.
    """
    if len(r1) > cap or len(r2) > cap:
        raise ValueError(f"relator longer than cap={cap}")
    w = (cap + 1) // 2
    row = bytearray(2 * w)
    for base, word in ((0, r1), (2 * w, r2)):
        for t, ch in enumerate(word):
            i = base + t
            if i % 2 == 0:
                row[i >> 1] |= _CHAR_TO_CODE[ch] << 4
            else:
                row[i >> 1] |= _CHAR_TO_CODE[ch]
    return bytes(row)


def est_states(node_budget):
    """Projected discovered-state count. Sizing only — never a search input."""
    return int(_DISCOVERY_A * float(node_budget) ** _DISCOVERY_P) + 64


# ---------------------------------------------------------------------------
# nibble row primitives
# ---------------------------------------------------------------------------
@njit(inline='always')
def _get_nib(row, t):
    # int64 on BOTH branches: numba unifies a uint8/int64 ternary to float64,
    # and `float64 & 1` is a typing error twenty frames deep.
    b = np.int64(row[t >> 1])
    if (t & 1) == 0:
        return b >> 4
    return b & 15


@njit(inline='always')
def _get_nib_at(arena, off, t):
    """Nibble ``t`` of the row starting at byte ``off`` — no slice allocated."""
    b = np.int64(arena[off + (t >> 1)])
    if (t & 1) == 0:
        return b >> 4
    return b & 15


@njit(inline='always')
def _code_of(b0, b1):
    """(b0, b1) -> order-preserving code. Mirrors greedy_baseline._CODE_TABLE,
    which is indexed by 2*b0 + b1: Y=0->2, y=1->4, X=2->1, x=3->3."""
    v = 2 * np.int64(b0) + np.int64(b1)
    if v == 0:
        return np.int64(2)
    elif v == 1:
        return np.int64(4)
    elif v == 2:
        return np.int64(1)
    return np.int64(3)


@njit(inline='always')
def _set_nib_at(arena, off, t, v):
    i = off + (t >> 1)
    c = np.int64(v)
    if (t & 1) == 0:
        arena[i] = np.uint8(np.int64(arena[i]) | (c << 4))
    else:
        arena[i] = np.uint8(np.int64(arena[i]) | c)


@njit(inline='always')
def _row_less(arena, a, b, rw):
    """memcmp(row_a, row_b) < 0. Rows are fixed width and zero padded."""
    oa = a * rw
    ob = b * rw
    for i in range(rw):
        va = arena[oa + i]
        vb = arena[ob + i]
        if va != vb:
            return va < vb
    return False


@njit(inline='always')
def _less(arena, len1, len2, depth, a, b, rw):
    """The heap order: (total, depth, row). A strict total order — see module doc."""
    ta = len1[a] + len2[a]
    tb = len1[b] + len2[b]
    if ta != tb:
        return ta < tb
    if depth[a] != depth[b]:
        return depth[a] < depth[b]
    return _row_less(arena, a, b, rw)


@njit(inline='always')
def _fnv(arena, off, rw):
    h = np.uint64(1469598103934665603)
    p = np.uint64(1099511628211)
    for i in range(rw):
        h = (h ^ np.uint64(arena[off + i])) * p
    return h


@njit(inline='always')
def _rows_equal(arena, a, b, rw):
    oa = a * rw
    ob = b * rw
    for i in range(rw):
        if arena[oa + i] != arena[ob + i]:
            return False
    return True


@njit(inline='always')
def _slot0(h, tmask):
    # Both operands must be uint64: numba refuses to unify uint64 with int64 in a
    # bitwise op, and silently widening to float64 would corrupt the index.
    return np.int64(h & np.uint64(tmask))


@njit(inline='always')
def _lookup(table, tmask, arena, cand, rw, h):
    """Return the id of the state equal to row ``cand``, or -1. Linear probing."""
    i = _slot0(h, tmask)
    while True:
        slot = table[i]
        if slot == 0:
            return -1
        if _rows_equal(arena, slot - 1, cand, rw):
            return slot - 1
        i += 1
        if i > tmask:
            i = 0


@njit(inline='always')
def _insert(table, tmask, h, sid):
    i = _slot0(h, tmask)
    while table[i] != 0:
        i += 1
        if i > tmask:
            i = 0
    table[i] = sid + 1


@njit(cache=True)
def _rehash(table, tmask, arena, n, rw):
    for sid in range(n):
        _insert(table, tmask, _fnv(arena, sid * rw, rw), sid)


@njit(cache=True)
def _init_state(arena, len1, len2, depth, table, tmask, a1, a2, w, rw):
    """Pack the initial state as id 0 and mark it visited.

    Runs in njit rather than Python because ``_fnv`` returns a uint64: unboxing
    it to a Python int and passing it back in overflows int64 at the boundary.
    """
    nb2 = 2 * w
    for t in range(rw):
        arena[t] = 0
    for t in range(len(a1)):
        _set_nib_at(arena, 0, t, _code_of(a1[t, 0], a1[t, 1]))
    for t in range(len(a2)):
        _set_nib_at(arena, 0, nb2 + t, _code_of(a2[t, 0], a2[t, 1]))
    len1[0] = len(a1)
    len2[0] = len(a2)
    depth[0] = 0
    _insert(table, tmask, _fnv(arena, 0, rw), 0)


# ---------------------------------------------------------------------------
# heap
# ---------------------------------------------------------------------------
@njit(inline='always')
def _sift_up(heap, i, arena, len1, len2, depth, rw):
    v = heap[i]
    while i > 0:
        parent = (i - 1) >> 1
        if _less(arena, len1, len2, depth, v, heap[parent], rw):
            heap[i] = heap[parent]
            i = parent
        else:
            break
    heap[i] = v


@njit(inline='always')
def _sift_down(heap, n, arena, len1, len2, depth, rw):
    i = 0
    v = heap[0]
    while True:
        c = 2 * i + 1
        if c >= n:
            break
        if c + 1 < n and _less(arena, len1, len2, depth, heap[c + 1], heap[c], rw):
            c += 1
        if _less(arena, len1, len2, depth, heap[c], v, rw):
            heap[i] = heap[c]
            i = c
        else:
            break
    heap[i] = v


# ---------------------------------------------------------------------------
# decode / encode
# ---------------------------------------------------------------------------
@njit(inline='always')
def _decode(arena, sid, base, n, rw):
    """Nibble region -> (n, 2) bool array, the form expand_node_nj wants."""
    off = sid * rw
    a = np.empty((n, 2), dtype=np.bool_)
    for t in range(n):
        c = _get_nib_at(arena, off, base + t)
        a[t, 0] = (c & 1) == 1
        a[t, 1] = c >= 3
    return a


@njit(cache=True)
def _run_chunk(arena, len1, len2, depth, heap, table, st,
               cap, w, rw, cyclic, max_pops, states_cap):
    """Advance the search by at most ``max_pops`` pops.

    All state lives in the arrays and in ``st``; nothing is returned but a status,
    so Python can re-enter after servicing the progress callback or growing a
    buffer. An @njit loop cannot call back into Python, and the memory guard and
    heartbeat both ride ``progress`` — this is what keeps them working.
    """
    nodes = st[0]
    heap_len = st[1]
    n_disc = st[2]
    tmask = st[3]
    min_id, min_total = st[4], st[5]
    max_id, max_total = st[6], st[7]
    exp_id, exp_total = st[8], st[9]

    nb2 = 2 * w                       # r2's first nibble slot (r1 gets [0, 2w))
    maxc = 4 * (cap + 1) * (cap + 1)  # upper bound on children of one pop
    pops = 0
    status = _OK

    while pops < max_pops:
        if heap_len == 0:
            status = _EMPTY
            break
        # Headroom for one whole expansion, checked before the pop so a return
        # never lands mid-expansion.
        if (n_disc + maxc > states_cap
                or (n_disc + maxc) * 2 > table.size
                or heap_len + maxc > heap.size):
            status = _NEED_CAPACITY
            break

        top = heap[0]
        heap_len -= 1
        if heap_len > 0:
            heap[0] = heap[heap_len]
            _sift_down(heap, heap_len, arena, len1, len2, depth, rw)
        nodes += 1
        pops += 1

        l1 = len1[top]
        l2 = len2[top]
        total = l1 + l2
        if total > exp_total:
            exp_total = total
            exp_id = top
        if l1 == 1 and l2 == 1:
            status = _SOLVED
            break

        a1 = _decode(arena, top, 0, l1, rw)
        a2 = _decode(arena, top, nb2, l2, rw)
        codes, lens, moves, count = expand_node_nj(a1, a2, cap, cyclic)

        d1 = depth[top] + 1
        for i in range(count):
            la = lens[i, 0]
            lb = lens[i, 1]
            # Pack the candidate straight into the next free arena row. It is not
            # in the table, so it can never collide with itself during lookup.
            off = n_disc * rw
            for t in range(rw):
                arena[off + t] = 0
            for t in range(la):
                _set_nib_at(arena, off, t, codes[i, t])
            for t in range(lb):
                _set_nib_at(arena, off, nb2 + t, codes[i, la + t])

            h = _fnv(arena, off, rw)
            if _lookup(table, tmask, arena, n_disc, rw, h) != -1:
                continue

            sid = n_disc
            len1[sid] = la
            len2[sid] = lb
            depth[sid] = d1
            _insert(table, tmask, h, sid)
            n_disc += 1

            nt = la + lb
            if nt < min_total:
                min_total = nt
                min_id = sid
            elif nt > max_total:
                max_total = nt
                max_id = sid

            heap[heap_len] = sid
            heap_len += 1
            _sift_up(heap, heap_len - 1, arena, len1, len2, depth, rw)

    st[0] = nodes
    st[1] = heap_len
    st[2] = n_disc
    st[3] = tmask
    st[4], st[5] = min_id, min_total
    st[6], st[7] = max_id, max_total
    st[8], st[9] = exp_id, exp_total
    return status


class GreedyCompactSolver:
    """Pops in exactly the order ``GreedyHeavySolver`` does. Tracks no paths."""

    def __init__(self, r1, r2, max_nodes=10000, max_relator_length=24,
                 cyclic_reduce=True, reserve_states=None):
        if not 1 <= max_relator_length <= 255:
            # len1/len2 are uint8. A larger cap would wrap silently and the
            # trivial test (len1 == 1 == len2) would fire on the wrong state.
            raise ValueError(
                f"max_relator_length must be in 1..255, got {max_relator_length}")
        self.max_nodes = max_nodes
        self.cap = max_relator_length
        self.cyclic_reduce = cyclic_reduce
        self.w = (self.cap + 1) // 2
        self.rw = 2 * self.w
        self.grew = 0

        self.initial_state = canonical_pair_nj(
            reduce_relator_nj(str_to_arr(r1), cyclic_reduce),
            reduce_relator_nj(str_to_arr(r2), cyclic_reduce),
        )

        want = reserve_states or est_states(max_nodes)
        # One expansion's worth of headroom, so _run_chunk's pre-pop check can
        # never be unsatisfiable at the reservation size.
        n = max(1024, int(want * _RESERVE_SLACK)) + 4 * (self.cap + 1) ** 2
        self._alloc(n)

    def _alloc(self, n, old=None):
        self.states_cap = n
        self.arena = np.empty(n * self.rw, dtype=np.uint8)
        self.len1 = np.empty(n, dtype=np.uint8)
        self.len2 = np.empty(n, dtype=np.uint8)
        self.depth = np.empty(n, dtype=np.int32)
        self.heap = np.empty(n, dtype=np.int32)
        self.tcap = _next_pow2(2 * n)
        self.table = np.zeros(self.tcap, dtype=np.int32)
        if old is not None:
            k = old["n"]
            self.arena[:k * self.rw] = old["arena"][:k * self.rw]
            self.len1[:k] = old["len1"][:k]
            self.len2[:k] = old["len2"][:k]
            self.depth[:k] = old["depth"][:k]
            self.heap[:old["heap_len"]] = old["heap"][:old["heap_len"]]
            _rehash(self.table, self.tcap - 1, self.arena, k, self.rw)

    def _grow(self, st):
        self.grew += 1
        old = {"n": int(st[2]), "heap_len": int(st[1]), "arena": self.arena,
               "len1": self.len1, "len2": self.len2, "depth": self.depth,
               "heap": self.heap}
        print(f"    [compact] reservation exceeded at {old['n']:,} states; "
              f"growing to {2 * self.states_cap:,} (this copies)", flush=True)
        self._alloc(2 * self.states_cap, old)
        st[3] = self.tcap - 1

    def bytes_reserved(self):
        return (self.arena.nbytes + self.len1.nbytes + self.len2.nbytes
                + self.depth.nbytes + self.heap.nbytes + self.table.nbytes)

    def bytes_per_state(self):
        """Reserved bytes per state the reservation is sized for. Exact, not RSS."""
        return self.bytes_reserved() / self.states_cap

    def solve(self, progress=None):
        """Return (solved, nodes_visited). Stats live on ``self``."""
        a1, a2 = self.initial_state
        _init_state(self.arena, self.len1, self.len2, self.depth, self.table,
                    self.tcap - 1, a1, a2, self.w, self.rw)
        init_total = int(self.len1[0]) + int(self.len2[0])

        st = np.zeros(10, dtype=np.int64)
        st[1] = 1                      # heap_len: the initial state
        st[2] = 1                      # n_discovered
        st[3] = self.tcap - 1          # tmask
        st[5] = init_total             # min_total (min_id stays 0)
        st[7] = init_total             # max_total
        st[9] = init_total             # max_expanded_total
        self.heap[0] = 0

        solved = False
        next_tick = _HB_CHECK_EVERY
        while True:
            remaining = self.max_nodes - int(st[0])
            if remaining <= 0:
                break
            status = _run_chunk(
                self.arena, self.len1, self.len2, self.depth, self.heap,
                self.table, st, self.cap, self.w, self.rw, self.cyclic_reduce,
                min(_HB_CHECK_EVERY, remaining), self.states_cap)

            if progress is not None and int(st[0]) >= next_tick:
                # The guard raises out of here, exactly as it does from the
                # heavy solver's loop. All state is already written back to the
                # arrays, so nothing is corrupted by unwinding.
                progress(int(st[0]))
                next_tick = (int(st[0]) // _HB_CHECK_EVERY + 1) * _HB_CHECK_EVERY

            if status == _SOLVED:
                solved = True
                break
            if status == _EMPTY:
                break
            if status == _NEED_CAPACITY:
                self._grow(st)

        self.n_discovered = int(st[2])
        self.min_id, self.min_total = int(st[4]), int(st[5])
        self.max_id, self.max_total = int(st[6]), int(st[7])
        self.max_expanded_id, self.max_expanded_total = int(st[8]), int(st[9])
        return solved, int(st[0])

    def relators(self, sid):
        """(r1_str, r2_str) for a state id."""
        off = sid * self.rw
        row = self.arena[off:off + self.rw]
        nb2 = 2 * self.w

        def word(base, n):
            return ''.join(_CODE_TO_CHAR[int(_get_nib(row, base + t))]
                           for t in range(n))
        return word(0, int(self.len1[sid])), word(nb2, int(self.len2[sid]))


def greedy_search_compact(r1_str, r2_str, node_budget, max_relator_length=24,
                          cyclic_reduce=True, progress=None, reserve_states=None):
    """Same stats dict as ``_greedy_search_heavy``: no path, identical numbers."""
    solver = GreedyCompactSolver(
        r1_str, r2_str,
        max_nodes=node_budget,
        max_relator_length=max_relator_length,
        cyclic_reduce=cyclic_reduce,
        reserve_states=reserve_states,
    )
    solved, nodes_visited = solver.solve(progress)
    min_r = solver.relators(solver.min_id)
    max_r = solver.relators(solver.max_id)
    exp_r = solver.relators(solver.max_expanded_id)
    return {
        "solved": solved,
        "nodes_explored": nodes_visited,
        "path_length": None,
        "min_relator_length": solver.min_total,
        "min_relator": [min_r[0], min_r[1]],
        "max_relator_length": solver.max_total,
        "max_relator": [max_r[0], max_r[1]],
        "max_relator_length_expanded": solver.max_expanded_total,
        "max_relator_expanded": [exp_r[0], exp_r[1]],
        "path": [],
        "path_moves": [],
    }
