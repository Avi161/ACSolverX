"""The tuned ordering on the compact packed arena — ``hsolve`` results at ~1/4 the memory.

``greedy_search_h(keep_path=False)`` costs a measured **24 kB per node popped** on the unsolved
124 at cap 48, which caps a 51 GB machine at ~2M nodes. Almost none of that is data: it is CPython
object overhead on the packed ``bytes`` keys, the visited-set entries, and the heap tuples — the
exact overhead ``greedy_compact`` already eliminated for the length ordering with a nibble arena,
an int32 binary heap and an open-addressing table at ~75 B/state. This module is that layout with
the heap comparison swapped for the tuned heuristic's.

WHY THE POP ORDER IS IDENTICAL TO ``greedy_search_h``
=====================================================
``hsolve`` pushes ``((seg, score), depth, key)`` into ``heapq``; every state is pushed exactly
once (dedup before push), so no two entries share a ``key`` and the comparison is a strict total
order — the pop sequence follows from the ordering relation alone, not from the heap
implementation (the same argument ``greedy_compact``'s docstring makes for the length ordering).
Three things must therefore be preserved, and each is preserved by construction:

1. **The scores are bit-identical floats.** Children are generated and scored by importing and
   calling the exact ``expand_and_score_nj`` kernel ``hsolve`` calls — same accumulation, same
   order, no ``fastmath`` anywhere in the chain — and the root is scored by the same Python
   expression ``hsolve`` uses for its root. IEEE doubles from identical operation sequences are
   equal bit for bit, so ``score[a] != score[b]`` resolves exactly where ``hsolve``'s does.
2. **The tie-break sorts like the key.** The comparator is seg, then score, then depth, then
   ``_row_less_h`` on the arena row: r1 lexicographic on the common prefix, shorter first on
   a tie, then the same for r2. That is exactly how ``memcmp`` orders the packed key
   ``c1 + b'\\x00' + c2`` (the separator sits below every code and ``bytes`` puts a prefix
   first) and exactly how it ordered ``greedy_compact``'s zero-padded nibble rows; the proof
   is in ``_row_less_h``'s docstring and the sort-corpus test in ``tests/test_leftovers_5m.py``
   pins it pair for pair against ``greedy_compact.pack_row``. The code tables agree:
   ``hfast._pack``'s ``(2, 4, 1, 3)`` is ``greedy_compact._code_of``.
3. **Discovery order is the enumeration order** of the same kernel, so ``depth`` and the
   first-seen min/max statistics land on the same states. ``hsolve`` updates min and max with two
   INDEPENDENT ``if``s on discovery (not the heavy solver's ``elif``) and max-expanded on pop
   before the solved test — mirrored here line for line.

``verify_hcompact.py`` checks all of this against ``greedy_search_h`` on every benchmark row and
a slice of the unsolved 124, all three shipped configs, budgets 500 and 1,000 — every scalar
field plus the first-seen min/max/expanded relator *strings*, which pin discovery order.

WHAT IT BUYS
============
Per state: row (2 bits a symbol: cap 48 → 24 B, cap 64 → 32 B) + len1/len2 (2) + depth (4)
+ heap (4) + score (8) + seg (1) + table (~8–16 amortised) ≈ **52–68 B** (the nibble layout
this replaced spent 48–64 B on the row alone), reserved once at the projected count (lazily faulted,
never grow-copied unless exceeded — then loudly). The arena is one allocation at the cap
width; rows start narrow and widen in place, so address space is the full-width figure from
birth and physical memory is only what the rows at their current width have touched. Against ``hsolve``'s ~390 B/state that is the
difference between 10⁶ nodes needing ~24 GB and needing ~7 GB, i.e. between 2M being the ceiling
on a 51 GB machine and ~5M fitting. No path is tracked (the ``keep_path=False`` trade); recover a
certificate by re-running the one presentation that solved through ``greedy_search_h`` — the
search is deterministic, so the path is exact.

    from experiments.heuristic_search.core.hcompact import greedy_search_hcompact
    stats = greedy_search_hcompact(r1, r2, node_budget=3 * 10**6,
                                   max_relator_length=48, config=RECOMMENDED)
"""
import os
import sys

import numpy as np
from numba import njit

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

from experiments.search.greedy_baseline import (                    # noqa: E402
    move_to_str,
    canonical_pair_nj, reduce_relator_nj, str_to_arr,
)
from experiments.search.greedy_compact import (                     # noqa: E402
    _CODE_TO_CHAR, _HB_CHECK_EVERY, _EMPTY, _NEED_CAPACITY, _OK, _SOLVED,
    _code_of, _insert, _next_pow2, _slot0, est_states, _RESERVE_SLACK,
)
from experiments.heuristic_search.core.hfast import (                    # noqa: E402
    _SEP, _feats_nj, _pack, compile_config, expand_and_score_nj,
)
from experiments.heuristic_search.core.hlab import N_FEAT                # noqa: E402
from experiments.heuristic_search.core.hexpand import (                  # noqa: E402
    expand_and_score_h,
)
from experiments.heuristic_search.core.hsolve import LENGTH_ONLY         # noqa: E402


# ---------------------------------------------------------------------------
# 2-bit rows.
#
# The alphabet is four symbols with order-preserving codes 1..4 (X=1 < Y=2 <
# x=3 < y=4, ``_code_of``). ``greedy_compact`` spends a nibble on each and
# leaves 0 free as padding, which is what lets a plain ``memcmp`` of the row
# double as the heap's tie-break. Here a symbol is two bits -- ``code - 1``,
# most-significant field first within each byte -- so a row is
#
#     [r1 region: w bytes][r2 region: w bytes]      w = (cap + 3) // 4
#
# zero padded, 32 B per state at cap 64 instead of 64. Within a byte the value
# is ``64*s0 + 16*s1 + 4*s2 + s3`` (base 4, most significant first), so byte
# order IS symbol order for the four symbols a byte holds, and the region
# layout is the nibble engine's with w halved: ``_widen_in_place`` (regions of
# w bytes each) and the arena reservation shape carry over untouched.
#
# What does NOT carry over is the comparator. 0 is now a code (X), so padding
# is no longer a terminator and raw memcmp cannot see where a relator ends;
# ``_row_less_h`` below is length-aware and reproduces the nibble order
# exactly (its docstring carries the proof; the sort-corpus test in
# tests/test_leftovers_5m.py pins it against ``greedy_compact.pack_row``).
# ---------------------------------------------------------------------------
_CHAR_TO_CODE = {c: k for k, c in _CODE_TO_CHAR.items()}


def row_width_h(cap):
    """Bytes per arena row of THIS engine at the cap: two byte-aligned regions
    of ``(cap + 3) // 4``, i.e. 32 at cap 64 (``greedy_compact.row_width``
    describes the nibble engine and is 64 there)."""
    return 2 * ((cap + 3) // 4)


def pack_row_h(r1, r2, cap):
    """``(r1_str, r2_str)`` -> the 2-bit arena row at the cap width, as
    ``bytes``. Python mirror of the njit packer (``_set_sym2_at``), for tests
    that want to build rows without running a search. NOTE: unlike
    ``greedy_compact.pack_row`` this does NOT memcmp-sort like ``(r1, r2)``
    -- only ``_row_less_h`` does, given the lengths."""
    if len(r1) > cap or len(r2) > cap:
        raise ValueError(f"relator longer than cap={cap}")
    w = (cap + 3) // 4
    row = bytearray(2 * w)
    for base, word in ((0, r1), (w, r2)):
        for t, ch in enumerate(word):
            row[base + (t >> 2)] |= (_CHAR_TO_CODE[ch] - 1) << (6 - 2 * (t & 3))
    return bytes(row)


@njit(inline='always')
def _get_sym2(row, t):
    """Code (1..4) of symbol ``t`` of a row slice. int64 throughout: numba
    unifies a uint8/int64 mix to float64 and the caller then fails to type."""
    b = np.int64(row[t >> 2])
    return ((b >> (6 - 2 * (t & 3))) & 3) + 1


@njit(inline='always')
def _get_sym2_at(arena, off, t):
    """Code of symbol ``t`` of the row at byte ``off`` -- no slice allocated."""
    b = np.int64(arena[off + (t >> 2)])
    return ((b >> (6 - 2 * (t & 3))) & 3) + 1


@njit(inline='always')
def _set_sym2_at(arena, off, t, v):
    """Store code ``v`` (1..4) as symbol ``t``. ORs into a byte the caller has
    already zeroed (rows are zero-filled before packing, and a widen zeroes the
    bytes it opens), exactly as ``_set_nib_at`` assumes."""
    i = off + (t >> 2)
    arena[i] = np.uint8(np.int64(arena[i])
                        | ((np.int64(v) - 1) << (6 - 2 * (t & 3))))


@njit(inline='always')
def _region_cmp2(arena, oa, ob, la, lb):
    """Compare one region of two rows as words: -1, 0 or +1.

    The common prefix is ``m = min(la, lb)`` symbols: ``m >> 2`` whole bytes
    compared as bytes, then the ``m & 3`` symbols of the next byte compared
    under a mask that keeps only its top ``2 * (m & 3)`` bits. If the prefix
    agrees the shorter word is smaller; equal lengths and an equal prefix mean
    the words are equal.
    """
    m = la if la < lb else lb
    nfull = m >> 2
    for i in range(nfull):
        va = arena[oa + i]
        vb = arena[ob + i]
        if va != vb:
            return np.int64(-1) if va < vb else np.int64(1)
    r = m & 3
    if r != 0:
        mask = np.int64((0xFF << (8 - 2 * r)) & 0xFF)
        va = np.int64(arena[oa + nfull]) & mask
        vb = np.int64(arena[ob + nfull]) & mask
        if va != vb:
            return np.int64(-1) if va < vb else np.int64(1)
    if la != lb:
        return np.int64(-1) if la < lb else np.int64(1)
    return np.int64(0)


@njit(inline='always')
def _row_less_h(arena, len1, len2, a, b, w, rw):
    """The heap's last tie-break on 2-bit rows: ``row_a < row_b`` in exactly
    the order ``greedy_compact._row_less`` (memcmp on nibble rows) gives the
    same two states, which is the order of the Python reference's packed key
    ``c1 + b'\x00' + c2``.

    THE TARGET RELATION. A nibble row is ``[c1, 0-pad][c2, 0-pad]``, one
    nibble per symbol, most significant first, so byte memcmp on it is
    nibble-lexicographic. Walk two such rows: they agree on the first
    ``m = min(la, lb)`` nibbles iff r1's common prefixes agree; if not, the
    first differing symbol decides (codes compare as codes). If they agree
    and ``la < lb``, nibble ``la`` is 0 in ``a`` (padding; ``la < lb <=``
    region size, so it IS inside the region) and a code ``>= 1`` in ``b``,
    so ``a < b`` -- and symmetrically. If ``la == lb`` the r1 regions are
    identical bytes (codes then zeros) and the walk reaches the r2 regions,
    where the same argument repeats; two rows with equal words are equal.
    That is: r1 lexicographic on the common prefix, then shorter-is-smaller,
    then the same for r2. ``pack_key``'s ``c1 + b'\x00' + c2`` sorts the
    same way for the same reason (the separator 0 sits below every code,
    and ``bytes`` order is shorter-is-smaller on a tie).

    WHY THIS FUNCTION COMPUTES IT. Symbol ``t`` of a region is stored as
    ``code - 1`` in bits ``6 - 2*(t & 3)`` of byte ``t >> 2``, so a byte is
    ``64*s0 + 16*s1 + 4*s2 + s3``: the base-4, most-significant-first number
    of its four symbols. Hence (i) for two bytes holding four common-prefix
    symbols each, byte order is symbol-lexicographic order, and the FIRST
    byte that differs among the ``m >> 2`` whole prefix bytes contains the
    first differing symbol and orders it correctly; (ii) for the byte holding
    the last ``r = m & 3 != 0`` prefix symbols, masking to its top ``2r``
    bits zeroes every symbol beyond the prefix in both operands (a code in the
    longer word, padding in the shorter -- the very bits a raw memcmp would
    wrongly read, since ``X`` and padding are both 0), and the masked values
    compare as those ``r`` symbols do; (iii) if all ``m`` symbols agree the
    lengths decide, shorter first, exactly the padding-versus-code step of the
    nibble walk, and equal lengths with an equal prefix means equal words, so
    the comparison moves to r2 (``+w`` bytes in). Region boundaries are
    respected by construction: the partial byte is read only when ``r != 0``,
    which forces ``m < 4w`` and so ``m >> 2 <= w - 1``. No terminator is
    needed and none is stored; the lengths ``len1``/``len2`` the engine
    already keeps supply the ends. Pinned pair-for-pair against
    ``greedy_compact.pack_row`` by the sort-corpus test.
    """
    oa = a * rw
    ob = b * rw
    c = _region_cmp2(arena, oa, ob, np.int64(len1[a]), np.int64(len1[b]))
    if c != 0:
        return c < 0
    c = _region_cmp2(arena, oa + w, ob + w, np.int64(len2[a]), np.int64(len2[b]))
    return c < 0


# ---------------------------------------------------------------------------
# dedup without packing.
#
# ~94% of a pop's candidates are duplicates, and the original loop paid full
# price to find that out: zero a 64-byte arena row, pack ~30 nibbles, FNV the
# 64 bytes, then memcmp them. A row plus its lengths is uniquely determined by
# (len1, len2, codes), so the same identity can be hashed straight off the
# candidate's code array (~30 iterations, not 64), false collisions rejected
# by two integer length compares before any content is read, and the row
# packed ONLY once the candidate is known to be new. Same equality predicate,
# same dedup decisions, same insertion order -- the search is unchanged
# bit-for-bit (the equivalence gates against the Python oracle pin this);
# only the wasted work on the 94% is gone.
# ---------------------------------------------------------------------------
@njit(inline='always')
def _hash_codes(blob, o, la, lb):
    """FNV-1a over (la, lb, r1 codes, r2 codes) of an unpacked candidate.

    Same function, same 64-bit value as before, on every input: only the
    INDEXING changed. ``blob[o + t]`` with a signed index makes numba emit a
    wraparound check (``if i < 0: i += n``) on every byte, and on this loop
    -- whose body is one ``xor`` and one ``imul`` -- that check was a third
    of the time (measured 52.5 -> 35.0 ns per 45-symbol candidate on the lab
    box). ``o``, ``la`` and ``lb`` are non-negative by construction (offsets
    and lengths from ``expand_and_score_nj``), so indexing through ``uint64``
    reads exactly the same bytes and drops the check. The value being
    unchanged means slot placement, probe sequences and the table layout are
    unchanged too -- nothing downstream can tell (``test_hcompact_kernels``
    pins it against the frozen baseline's hash on random and real states).

    On word-at-a-time hashing, since the memo ranked it first: a 4-lane
    variant that breaks the serial chain measured NO faster than this below
    ~60 symbols per candidate (the lab rows run 38-43) and 30% faster at 80;
    the chain was never the bottleneck, the index checks were. By Lemma B
    any hash is search-identical, so that variant stays available for a
    campaign-length regime; it was not adopted here because it changes
    values for no measurable gain at this budget.
    """
    h = np.uint64(1469598103934665603)
    p = np.uint64(1099511628211)
    h = (h ^ np.uint64(la)) * p
    h = (h ^ np.uint64(lb)) * p
    q = np.uint64(o)
    for t in range(la):
        h = (h ^ np.uint64(blob[q + np.uint64(t)])) * p
    q = np.uint64(o + la + 1)
    for t in range(lb):
        h = (h ^ np.uint64(blob[q + np.uint64(t)])) * p
    return h


@njit(inline='always')
def _hash_row(arena, sid, len1, len2, sym2, rw):
    """The same hash as ``_hash_codes``, computed from a packed arena row
    (rehash after a grow). ``_get_sym2`` yields the code (1..4) a symbol was
    packed from, so the byte sequence fed to FNV is the candidate's own
    ``(la, lb, r1 codes, r2 codes)``; pinned by a direct test."""
    h = np.uint64(1469598103934665603)
    p = np.uint64(1099511628211)
    la = np.int64(len1[sid])
    lb = np.int64(len2[sid])
    h = (h ^ np.uint64(la)) * p
    h = (h ^ np.uint64(lb)) * p
    row = arena[sid * rw:(sid + 1) * rw]
    for t in range(la):
        h = (h ^ np.uint64(_get_sym2(row, t))) * p
    for t in range(lb):
        h = (h ^ np.uint64(_get_sym2(row, sym2 + t))) * p
    return h


@njit(inline='always')
def _codes_equal_row(arena, sid, len1, len2, blob, o, la, lb, sym2, rw):
    if np.int64(len1[sid]) != la or np.int64(len2[sid]) != lb:
        return False
    row = arena[sid * rw:(sid + 1) * rw]
    for t in range(la):
        if _get_sym2(row, t) != np.int64(blob[o + t]):
            return False
    for t in range(lb):
        if _get_sym2(row, sym2 + t) != np.int64(blob[o + la + 1 + t]):
            return False
    return True


@njit(inline='always')
def _lookup_codes(table, tmask, arena, len1, len2, blob, o, la, lb, sym2, rw, h):
    """Id of the state equal to the UNPACKED candidate, or -1. Linear probing."""
    i = _slot0(h, tmask)
    while True:
        slot = table[i]
        if slot == 0:
            return -1
        if _codes_equal_row(arena, slot - 1, len1, len2, blob, o, la, lb,
                            sym2, rw):
            return slot - 1
        i += 1
        if i > tmask:
            i = 0


@njit(cache=True)
def _rehash_h(table, tmask, arena, len1, len2, n, sym2, rw):
    for sid in range(n):
        _insert(table, tmask, _hash_row(arena, sid, len1, len2, sym2, rw), sid)


@njit(cache=True)
def _init_state_h(arena, len1, len2, depth, table, tmask, a1, a2, w, rw):
    """greedy_compact._init_state on 2-bit rows, inserting with the codes hash."""
    sym2 = 4 * w
    for t in range(rw):
        arena[t] = 0
    for t in range(len(a1)):
        _set_sym2_at(arena, 0, t, _code_of(a1[t, 0], a1[t, 1]))
    for t in range(len(a2)):
        _set_sym2_at(arena, 0, sym2 + t, _code_of(a2[t, 0], a2[t, 1]))
    len1[0] = len(a1)
    len2[0] = len(a2)
    depth[0] = 0
    _insert(table, tmask, _hash_row(arena, 0, len1, len2, sym2, rw), 0)


@njit(inline='always')
def _decode_h(arena, sid, base, n, rw):
    """2-bit region -> (n, 2) bool array, the form the kernel wants
    (``greedy_compact._decode`` for these rows; same code->bits map)."""
    off = sid * rw
    a = np.empty((n, 2), dtype=np.bool_)
    for t in range(n):
        c = _get_sym2_at(arena, off, base + t)
        a[t, 0] = (c & 1) == 1
        a[t, 1] = c >= 3
    return a


# ---------------------------------------------------------------------------
# heap ordered by (seg, score, depth, row) — hsolve's ((seg, sc), nd, key).
# The row step is _row_less_h, which needs the lengths and the region width.
# ---------------------------------------------------------------------------
@njit(inline='always')
def _less_h(arena, len1, len2, seg, score, depth, a, b, w, rw):
    if seg[a] != seg[b]:
        return seg[a] < seg[b]
    if score[a] != score[b]:
        return score[a] < score[b]
    if depth[a] != depth[b]:
        return depth[a] < depth[b]
    return _row_less_h(arena, len1, len2, a, b, w, rw)


@njit(inline='always')
def _sift_up_h(heap, i, arena, len1, len2, seg, score, depth, w, rw):
    v = heap[i]
    while i > 0:
        parent = (i - 1) >> 1
        if _less_h(arena, len1, len2, seg, score, depth, v, heap[parent], w, rw):
            heap[i] = heap[parent]
            i = parent
        else:
            break
    heap[i] = v


@njit(inline='always')
def _sift_down_h(heap, n, arena, len1, len2, seg, score, depth, w, rw):
    i = 0
    v = heap[0]
    while True:
        c = 2 * i + 1
        if c >= n:
            break
        if c + 1 < n and _less_h(arena, len1, len2, seg, score, depth,
                                 heap[c + 1], heap[c], w, rw):
            c += 1
        if _less_h(arena, len1, len2, seg, score, depth, heap[c], v, w, rw):
            heap[i] = heap[c]
            i = c
        else:
            break
    heap[i] = v


_NEED_WIDTH = 4          # storage rows too narrow for this pop's children


@njit(cache=True)
def _widen_in_place(arena, n, w_old, w_new):
    """Re-lay the first ``n`` rows at the wider stride IN PLACE, last row
    first. Row ``sid`` moves from ``sid*rw_old`` to ``sid*rw_new``; every
    lower row's source lies below ``sid*rw_old <= sid*rw_new``, so a
    backward pass never overwrites a byte it has yet to read. A row's own
    source can overlap its destination (the first ``rw_old/(rw_new-rw_old)``
    rows), so each row is staged through ``tmp`` before it is written.
    Regions keep their bytes verbatim -- packed codes then zero padding -- so
    no comparison outcome can change (``_row_less_h`` reads only the bytes
    the lengths cover, and the lengths do not move) and the codes-based hash
    needs no rehash. Regions are ``w`` bytes each whatever a byte holds,
    so the 2-bit rows use this unchanged. The old copy-into-a-second-arena repack held BOTH arenas in
    address space at once (293 GiB on a 2.14B reservation at cap 64, the
    number that clipped 256 GiB boxes out of the u124 campaign) and touched
    +48 B/state of fresh pages during the copy (aca_1's 158 GB peak); this
    holds one arena and touches only the widened tail."""
    rw_old = 2 * w_old
    rw_new = 2 * w_new
    tmp = np.empty(rw_old, dtype=np.uint8)
    for sid in range(n - 1, -1, -1):
        so = sid * rw_old
        sn = sid * rw_new
        for i in range(rw_old):
            tmp[i] = arena[so + i]
        for i in range(w_old):
            arena[sn + i] = tmp[i]
        for i in range(w_old, w_new):
            arena[sn + i] = 0
        for i in range(w_old):
            arena[sn + w_new + i] = tmp[w_old + i]
        for i in range(w_old, w_new):
            arena[sn + w_new + i] = 0


@njit(cache=True)
def _run_chunk_h(arena, len1, len2, depth, seg, score, heap, table, st,
                 cap, w, rw, cyclic, seg_upto, seg_w, seg_depth, use_depth,
                 max_pops, states_cap, parent, pmove, track, w_cap):
    """Advance by at most ``max_pops`` pops; all state lives in the arrays and ``st``.

    The skeleton is ``greedy_compact._run_chunk``; the two deliberate differences are the
    comparator (via the ``_h`` sifts) and the min/max update, which uses hsolve's two
    independent ``if``s rather than the heavy solver's ``elif``.
    """
    nodes = st[0]
    heap_len = st[1]
    n_disc = st[2]
    tmask = st[3]
    min_id, min_total = st[4], st[5]
    max_id, max_total = st[6], st[7]
    exp_id, exp_total = st[8], st[9]

    sym2 = 4 * w                 # symbol index where the r2 region starts
    maxc = 4 * (cap + 1) * (cap + 1)
    pops = 0
    status = _OK

    while pops < max_pops:
        if heap_len == 0:
            status = _EMPTY
            break
        if (n_disc + maxc > states_cap
                or (n_disc + maxc) * 2 > table.size
                or heap_len + maxc > heap.size):
            status = _NEED_CAPACITY
            break
        # A child's single relator never exceeds the popped total, so this,
        # checked BEFORE the pop, guarantees every child of this pop fits the
        # current storage width (4 symbols a byte, so 4*w a region). At
        # w == w_cap every child fits by the cap itself and the guard never
        # fires.
        if w < w_cap:
            nxt = heap[0]
            if np.int64(len1[nxt]) + np.int64(len2[nxt]) > sym2:
                status = _NEED_WIDTH
                break

        top = heap[0]
        heap_len -= 1
        if heap_len > 0:
            heap[0] = heap[heap_len]
            _sift_down_h(heap, heap_len, arena, len1, len2, seg, score, depth,
                         w, rw)
        nodes += 1
        pops += 1

        l1 = len1[top]
        l2 = len2[top]
        total = l1 + l2
        if total > exp_total:
            exp_total = total
            exp_id = top
        if l1 == 1 and l2 == 1:
            st[10] = np.int64(depth[top])
            st[11] = np.int64(top)          # the solved node, for path recovery
            status = _SOLVED
            break

        a1 = _decode_h(arena, top, 0, l1, rw)
        a2 = _decode_h(arena, top, sym2, l2, rw)
        blob, offs, klens, seg_idx, sc, tots, knots, moves, count = \
            expand_and_score_h(a1, a2, cap, cyclic, seg_upto, seg_w, True, False)

        d1 = depth[top] + 1
        for i in range(count):
            o = offs[i]
            kl = klens[i]
            la = 0
            for t in range(kl):
                if blob[o + t] == 0:
                    la = t
                    break
            lb = kl - la - 1

            h = _hash_codes(blob, o, la, lb)
            if _lookup_codes(table, tmask, arena, len1, len2, blob, o,
                             la, lb, sym2, rw, h) != -1:
                continue

            sid = n_disc
            off = sid * rw
            for t in range(rw):
                arena[off + t] = 0
            for t in range(la):
                _set_sym2_at(arena, off, t, np.int64(blob[o + t]))
            for t in range(lb):
                _set_sym2_at(arena, off, sym2 + t, np.int64(blob[o + la + 1 + t]))
            len1[sid] = la
            len2[sid] = lb
            depth[sid] = d1
            si = seg_idx[i]
            s_val = sc[i]
            if use_depth:
                # Mirrors hsolve: sc += seg_depth[seg] * nd, at the same point.
                s_val = s_val + seg_depth[si] * d1
            seg[sid] = np.uint8(si)
            score[sid] = s_val
            if track:
                parent[sid] = top
                # a move is (target, jsign, k1, k2); all four fit in int8
                # (target 0/1, jsign +-1, k1/k2 bounded by cap <= 127)
                for t in range(4):
                    pmove[sid, t] = np.int8(moves[i, t])
            _insert(table, tmask, h, sid)
            n_disc += 1

            nt = la + lb
            # Two INDEPENDENT ifs — hsolve's semantics, not the heavy solver's elif.
            if nt < min_total:
                min_total = nt
                min_id = sid
            if nt > max_total:
                max_total = nt
                max_id = sid

            heap[heap_len] = sid
            heap_len += 1
            _sift_up_h(heap, heap_len - 1, arena, len1, len2, seg, score,
                       depth, w, rw)

    st[0] = nodes
    st[1] = heap_len
    st[2] = n_disc
    st[3] = tmask
    st[4], st[5] = min_id, min_total
    st[6], st[7] = max_id, max_total
    st[8], st[9] = exp_id, exp_total
    return status


def _proc_name():
    """This process's kernel comm -- the runners set it to the row name
    (prctl PR_SET_NAME), so engine prints can attribute themselves. Widen
    and grow lines from five interleaved workers were otherwise anonymous:
    'nearest preceding row token' is not sound, and the operator had to
    treat every such line as unattributable."""
    try:
        with open("/proc/self/comm") as f:
            return f.read().strip()
    except OSError:
        return "?"


def _advise_hugepages(*arrays):
    """Best-effort ``madvise(MADV_HUGEPAGE)`` on the big per-search arrays.

    Under the kernel's ``defrag=madvise`` default, un-advised memory only
    gets a 2 MiB page when one happens to be free at fault time -- measured
    at 40-45% coverage on a fresh box, against 99%+ with advice, and workers
    hugepage-backed from birth ran 2-9% faster than the same rows reaching
    coverage mid-life. Advice changes page BACKING, never bytes: the search
    is bit-identical with or without it (the identity gates re-check this).
    Returns how many regions took the advice; 0 on non-Linux or any failure.
    """
    if not sys.platform.startswith("linux"):
        return 0
    try:
        import ctypes
        libc = ctypes.CDLL(None, use_errno=True)
        page = os.sysconf("SC_PAGESIZE")
        advised = 0
        for a in arrays:
            addr = a.ctypes.data
            start = -(-addr // page) * page           # first page boundary in
            end = (addr + a.nbytes) // page * page    # last page boundary in
            if end - start >= (1 << 21):              # holds a 2 MiB window
                if libc.madvise(ctypes.c_void_p(start),
                                ctypes.c_size_t(end - start),
                                14) == 0:             # 14 = MADV_HUGEPAGE
                    advised += 1
        return advised
    except Exception:
        return 0


class HCompactSolver:
    """Pops in exactly the order ``greedy_search_h`` does. Tracks no paths."""

    def __init__(self, r1, r2, max_nodes=10000, max_relator_length=24,
                 cyclic_reduce=True, config=None, reserve_states=None,
                 track_path=False, storage_width=None):
        if not 1 <= max_relator_length <= 255:
            raise ValueError(
                f"max_relator_length must be in 1..255, got {max_relator_length}")
        self.max_nodes = max_nodes
        self.cap = max_relator_length
        self.cyclic_reduce = cyclic_reduce
        # Storage width vs semantic cap. ``cap`` prunes children (the search);
        # ``w`` only sizes arena rows (the storage): a region is ``w`` bytes
        # of 4 symbols each. Rows start narrow -- most searches never store a
        # relator near the cap, and at cap 64 full-width rows are ~80%
        # padding -- and widen in place the first time a pop could produce a
        # child that would not fit. Bit-identical because the tie-break reads
        # only the bytes the lengths cover: no comparison outcome depends on
        # width (pinned by tests against full-width runs).
        self.w_cap = (self.cap + 3) // 4
        self.grew = 0
        self.widened = 0

        cfg = config or LENGTH_ONLY
        self.track_path = bool(track_path)
        self.seg_upto, self.seg_w, self.seg_depth = compile_config(cfg)
        self.use_depth = bool(np.any(self.seg_depth != 0.0))
        self.n_seg = len(self.seg_upto)
        if self.n_seg >= 255:
            raise ValueError("seg is uint8; configs are 1-3 segments in practice")

        self.initial_state = canonical_pair_nj(
            reduce_relator_nj(str_to_arr(r1), cyclic_reduce),
            reduce_relator_nj(str_to_arr(r2), cyclic_reduce),
        )

        # The initial state must fit whatever width is chosen -- an override
        # below it would overflow _init_state_h into the neighbouring region
        # and corrupt the earliest rows (caught by the width-identity gate).
        a1, a2 = self.initial_state
        need = (max(len(a1), len(a2), 1) + 3) // 4
        if storage_width is not None:
            w0 = min(max(int(storage_width), need), self.w_cap)
        else:
            w0 = min(max(6, need), self.w_cap)    # 24-symbol regions to start
        self.w = max(1, w0)
        self.rw = 2 * self.w

        # An EXPLICIT reservation is honored as-is: the caller (plan_memory)
        # already applied slack, and re-applying it here made states_cap
        # 2.25x the estimate -- which pushed the hash table across a
        # power-of-two boundary to 8 GiB resident per worker at 5M.
        if reserve_states:
            n = max(1024, int(reserve_states)) + 4 * (self.cap + 1) ** 2
        else:
            n = (max(1024, int(est_states(max_nodes) * _RESERVE_SLACK))
                 + 4 * (self.cap + 1) ** 2)
        self._alloc(n)
        self.solved_id = None

    def _alloc(self, n, old=None):
        self.states_cap = n
        # Reserved at the CAP width once; rows live at the current stride
        # ``rw`` in its prefix and are re-laid in place when they widen. The
        # address space is the full-width figure from birth (np.empty commits
        # nothing until touched, so physical memory is still what the rows
        # at their current width actually occupy), and a widen allocates
        # nothing -- there is no second arena and no repack transient.
        self.arena = np.empty(n * 2 * self.w_cap, dtype=np.uint8)
        self.len1 = np.empty(n, dtype=np.uint8)
        self.len2 = np.empty(n, dtype=np.uint8)
        self.depth = np.empty(n, dtype=np.int32)
        self.seg = np.empty(n, dtype=np.uint8)
        self.score = np.empty(n, dtype=np.float64)
        self.heap = np.empty(n, dtype=np.int32)
        # parent + the move that produced each state: what turns "path_length"
        # into an actual move sequence. 5 B/state, and only when tracking --
        # a run that does not want paths allocates nothing and is byte-for-byte
        # the search it always was.
        m = n if self.track_path else 1
        # np.empty, NOT np.full: full() writes the fill value into every page
        # (2.6 GiB resident at init for a 5M reservation). Only the root's -1
        # is ever read as a walk terminator; every other entry is written at
        # discovery before the path walk can reach it.
        self.parent = np.empty(m, dtype=np.int32)
        self.pmove = np.zeros((m, 4), dtype=np.int8)
        self.tcap = _next_pow2(2 * n)
        self.table = np.zeros(self.tcap, dtype=np.int32)
        # advised BEFORE the old-data copy below, so even a grow's copy
        # faults its pages in as 2 MiB from the first touch
        _advise_hugepages(self.arena, self.table, self.score, self.heap,
                          self.depth, self.parent, self.pmove,
                          self.len1, self.len2, self.seg)
        if old is None:
            self.parent[0] = -1
        else:
            k = old["n"]
            self.arena[:k * self.rw] = old["arena"][:k * self.rw]
            self.len1[:k] = old["len1"][:k]
            self.len2[:k] = old["len2"][:k]
            self.depth[:k] = old["depth"][:k]
            self.seg[:k] = old["seg"][:k]
            self.score[:k] = old["score"][:k]
            self.heap[:old["heap_len"]] = old["heap"][:old["heap_len"]]
            if self.track_path:
                self.parent[:k] = old["parent"][:k]
                self.pmove[:k, :] = old["pmove"][:k, :]
            _rehash_h(self.table, self.tcap - 1, self.arena,
                      self.len1, self.len2, k, 4 * self.w, self.rw)

    def _grow_width(self, st):
        self.widened += 1
        n = int(st[2])
        w_new = min(max(2 * self.w, 1), self.w_cap)
        print(f"    [hcompact:{_proc_name()}] rows widen {self.w}B -> {w_new}B "
              f"per relator at {n:,} states (in place)", flush=True)
        # the arena was advised for hugepages at _alloc; nothing new to advise
        _widen_in_place(self.arena, n, self.w, w_new)
        self.w = w_new
        self.rw = 2 * w_new

    def _grow(self, st):
        self.grew += 1
        old = {"n": int(st[2]), "heap_len": int(st[1]), "arena": self.arena,
               "len1": self.len1, "len2": self.len2, "depth": self.depth,
               "seg": self.seg, "score": self.score, "heap": self.heap,
               "parent": self.parent, "pmove": self.pmove}
        print(f"    [hcompact:{_proc_name()}] reservation exceeded at "
              f"{old['n']:,} states; growing to {2 * self.states_cap:,} "
              f"(this copies)", flush=True)
        try:
            self._alloc(2 * self.states_cap, old)
        except MemoryError as e:
            # The doubling did not fit (a rate-floored reservation under the
            # RLIMIT cap, by design). Name the measurement on the way out:
            # states discovered / pops made IS this row's discovery rate,
            # and a retry sized below it would die at this exact pop again.
            raise MemoryError(
                f"reservation exhausted at {old['n']:,} states after "
                f"{int(st[0]):,} pops (growing to {2 * self.states_cap:,} "
                f"did not fit)") from e
        st[3] = self.tcap - 1

    def bytes_reserved(self):
        return (self.arena.nbytes + self.len1.nbytes + self.len2.nbytes
                + self.parent.nbytes + self.pmove.nbytes + self.depth.nbytes + self.seg.nbytes + self.score.nbytes
                + self.heap.nbytes + self.table.nbytes)

    def bytes_per_state(self):
        """What one discovered state occupies at the CURRENT row width, the
        table amortised over the reservation. ``bytes_reserved`` is address
        space and charges the arena at the cap width from birth; this is the
        physical figure adaptive width actually saves."""
        fixed = (self.len1.itemsize + self.len2.itemsize + self.depth.itemsize
                 + self.seg.itemsize + self.score.itemsize + self.heap.itemsize
                 + ((self.parent.itemsize + self.pmove.shape[1])
                    if self.track_path else 0))
        return self.rw + fixed + self.table.nbytes / self.states_cap

    def solve(self, progress=None):
        a1, a2 = self.initial_state
        _init_state_h(self.arena, self.len1, self.len2, self.depth, self.table,
                      self.tcap - 1, a1, a2, self.w, self.rw)
        init_total = int(self.len1[0]) + int(self.len2[0])

        # Root score: hsolve's exact Python expression (its p0 block), so the root's stored
        # (seg, score) is bit-identical too. It is popped first regardless (heap of one), but
        # a child can rediscover the root and dedup against it — the stored value must be the
        # one hsolve stored.
        key0 = _pack(a1, a2)
        scratch = np.empty(N_FEAT, dtype=np.float64)
        r_isx = np.empty(2 * self.cap + 2, dtype=np.bool_)
        r_len = np.empty(2 * self.cap + 2, dtype=np.int64)
        c0 = np.frombuffer(key0.replace(_SEP, b""), dtype=np.uint8)
        _feats_nj(c0, 0, len(a1), len(a2), r_isx, r_len, scratch)
        p0 = None
        for s in range(self.n_seg):
            if scratch[0] <= self.seg_upto[s]:
                p0 = (s, float(sum(self.seg_w[s, d] * scratch[d]
                                   for d in range(N_FEAT) if self.seg_w[s, d] != 0.0)))
                break
        if p0 is None:
            p0 = (self.n_seg, float(scratch[0]))
        self.seg[0] = p0[0]
        self.score[0] = p0[1]

        st = np.zeros(12, dtype=np.int64)
        st[10] = -1
        st[11] = -1
        st[1] = 1
        st[2] = 1
        st[3] = self.tcap - 1
        st[5] = init_total
        st[7] = init_total
        st[9] = init_total
        self.heap[0] = 0

        solved = False
        next_tick = _HB_CHECK_EVERY
        while True:
            remaining = self.max_nodes - int(st[0])
            if remaining <= 0:
                break
            status = _run_chunk_h(
                self.arena, self.len1, self.len2, self.depth, self.seg,
                self.score, self.heap, self.table, st, self.cap, self.w,
                self.rw, self.cyclic_reduce, self.seg_upto, self.seg_w,
                self.seg_depth, self.use_depth,
                min(_HB_CHECK_EVERY, remaining), self.states_cap,
                self.parent, self.pmove, self.track_path, self.w_cap)

            if progress is not None and int(st[0]) >= next_tick:
                # Optional 2nd arg = current min pair-total (st[5]). One-arg
                # callbacks stay valid via TypeError fallback.
                try:
                    # nodes, best (minimum) total relator length so far, max
                    # total expanded so far -- st[5]/st[9] are maintained by
                    # the kernel for the final record anyway, so live
                    # reduction reporting costs the hot loop nothing.
                    progress(int(st[0]), int(st[5]), int(st[9]))
                except TypeError:
                    try:
                        progress(int(st[0]), int(st[5]))
                    except TypeError:
                        progress(int(st[0]))
                next_tick = (int(st[0]) // _HB_CHECK_EVERY + 1) * _HB_CHECK_EVERY

            if status == _SOLVED:
                solved = True
                break
            if status == _EMPTY:
                break
            if status == _NEED_CAPACITY:
                self._grow(st)
            if status == _NEED_WIDTH:
                self._grow_width(st)

        self.n_discovered = int(st[2])
        self.min_id, self.min_total = int(st[4]), int(st[5])
        self.max_id, self.max_total = int(st[6]), int(st[7])
        self.max_expanded_id, self.max_expanded_total = int(st[8]), int(st[9])
        self.solved_depth = int(st[10]) if solved else None
        self.solved_id = int(st[11]) if solved and st[11] >= 0 else None
        return solved, int(st[0])

    def path(self):
        """``(states, moves)`` root -> solution, or ``([], [])``.

        Walks the parent chain from the solved node. The chain is acyclic by
        construction -- a state is written once, when it is first discovered,
        and its parent is always an already-popped node -- but the walk is
        bounded anyway so a corrupt array can never hang a 39-hour run.
        """
        if not self.track_path or self.solved_id is None:
            return [], []
        sid, states, moves = self.solved_id, [], []
        for _ in range(int(self.states_cap) + 1):
            states.append(self.relators(sid))
            p = int(self.parent[sid])
            if p < 0:
                states.reverse()
                moves.reverse()
                return states, moves
            moves.append(tuple(int(v) for v in self.pmove[sid]))
            sid = p
        raise RuntimeError("parent chain did not reach the root -- corrupt arena")

    def relators(self, sid):
        off = sid * self.rw
        row = self.arena[off:off + self.rw]
        sym2 = 4 * self.w

        def word(base, n):
            return ''.join(_CODE_TO_CHAR[int(_get_sym2(row, base + t))]
                           for t in range(n))
        return word(0, int(self.len1[sid])), word(sym2, int(self.len2[sid]))


def greedy_search_hcompact(r1_str, r2_str, node_budget, max_relator_length=24,
                           cyclic_reduce=True, config=None, progress=None,
                           reserve_states=None, track_path=False,
                           storage_width=None):
    """``greedy_search_h``'s exact dict, from the compact layout.

    ``track_path=False`` reproduces ``keep_path=False``: no certificate comes
    back and the search is byte-for-byte what it always was. ``track_path=True``
    reproduces ``keep_path=True`` -- the move sequence and the presentation at
    every step -- for 8 B/state (an int32 parent and the move's four int8s),
    which is about 8% on top of the arena. The Python solver keeps a whole parent dict
    for the same thing, at 36.5 kB/node against 24 kB.
    """
    solver = HCompactSolver(
        r1_str, r2_str,
        max_nodes=node_budget,
        max_relator_length=max_relator_length,
        cyclic_reduce=cyclic_reduce,
        config=config,
        reserve_states=reserve_states,
        track_path=track_path,
        storage_width=storage_width,
    )
    solved, nodes_visited = solver.solve(progress)
    states, moves = solver.path()
    min_r = solver.relators(solver.min_id)
    max_r = solver.relators(solver.max_id)
    exp_r = solver.relators(solver.max_expanded_id)
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
        "path": [[a, b] for a, b in states],
        "path_moves": [move_to_str(m) for m in moves],
    }
