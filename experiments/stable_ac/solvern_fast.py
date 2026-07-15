"""HIGH_SPEEDUP twin of ``solvern.search_n`` — same search, fused bookkeeping.

``search_n_fast`` returns a dict **bit-identical** to ``search_n``'s on every
field, paths included. It is a pure speed toggle: profiling showed ~70% of
``search_n``'s wall time is per-child Python work (``list.sort`` + ``_sort_key``
tuple-building, ``_tiebreak`` byte-packing, ``tuple(int(x))`` conversions), so
this module fuses expansion + canonicalisation + relator-sort + key-packing
into ONE ``@njit`` kernel call per pop and carries states as packed ``bytes``.

Why the results cannot differ:

* The packed key is exactly ``solvern._tiebreak``'s bytes (symbol ->
  ``abs(g) + 64*(g>0)``, relators joined by 0x00). That encoding is
  order-preserving (bytes comparison == the spec's ASCII heap tie-break,
  fuzz-pinned in test_solvern.py) AND injective, so it doubles as the state.
* Heap entries are ``(total, depth, packed)``. Packing is injective and every
  state is pushed at most once, so no two entries ever tie on all three
  elements — ``search_n``'s 4th tuple element (the key) is never load-bearing,
  and the pop sequence is identical.
* Children are emitted in exactly ``search_n``'s iteration order
  (i asc / j asc / s in (1,-1) / k1 asc / k2 asc), so the visited-set
  evolution, the first-crossing min/max states, and the parent/move pointers
  (hence the path) all match.

Two traps this file must never regress on:

* The relator sort is **length-first** (``_sort_key`` = ``(len, booth-lex)``);
  ``_booth_word_lt`` alone is length-recessive and misorders e.g. ``x`` vs
  ``ZZ`` — compare lengths, then booth-lex only on equal length.
* Unpacking negates inverse symbols — promote the uint8 byte to a signed int
  BEFORE negating (``-b`` on uint8 wraps to 256-b).
"""

from heapq import heappop, heappush

import numpy as np
from numba import njit

from experiments.stable_ac.solvern import (
    _HB_CHECK_EVERY,
    _booth_word_lt,
    _tiebreak,
    canonical_presentation,
    canonical_word_nj,
    expand_pair_nj,
    inverse_nj,
    move_to_str,
    word_to_str,
)


# ---------------------------------------------------------------------------
# packed-state codec (must match solvern._tiebreak byte-for-byte)
# ---------------------------------------------------------------------------
@njit(cache=True)
def _pack_state_nj(words, lens, n_rel):
    """State (padded int8 rows + lens) -> packed uint8 key, ``_tiebreak`` bytes."""
    total = 0
    for r in range(n_rel):
        total += lens[r]
    out = np.empty(total + n_rel - 1, dtype=np.uint8)
    pos = 0
    for r in range(n_rel):
        if r > 0:
            out[pos] = 0
            pos += 1
        for t in range(lens[r]):
            g = np.int64(words[r, t])
            if g > 0:
                out[pos] = g + 64
            else:
                out[pos] = -g
            pos += 1
    return out


@njit(cache=True)
def _unpack_state_nj(packed, n_rel):
    """Packed uint8 key -> (padded int8 rows, lens). Empty segments are fine."""
    n = len(packed)
    lens = np.zeros(n_rel, dtype=np.int64)
    r = 0
    for idx in range(n):
        if packed[idx] == 0:
            r += 1
        else:
            lens[r] += 1
    width = 0
    for r in range(n_rel):
        if lens[r] > width:
            width = lens[r]
    words = np.zeros((n_rel, width if width > 0 else 1), dtype=np.int8)
    r = 0
    t = 0
    for idx in range(n):
        b = np.int64(packed[idx])
        if b == 0:
            r += 1
            t = 0
        else:
            if b >= 65:
                words[r, t] = b - 64
            else:
                words[r, t] = -b
            t += 1
    return words, lens


@njit(inline='always')
def _relator_lt(words, lens, a, b):
    """Row a < row b under ``solvern._sort_key``: length first, then booth-lex."""
    if lens[a] != lens[b]:
        return lens[a] < lens[b]
    return _booth_word_lt(words[a, :lens[a]], words[b, :lens[b]])


@njit(cache=True)
def expand_node_packed_nj(words, lens, n_rel, cap, cyclic):
    """All children of one state, canonicalised, sorted and packed in-kernel.

    Emits children in exactly ``search_n``'s order (i asc / j asc / s in
    (1,-1) / k1 asc / k2 asc), duplicates included — the caller's visited set
    dedups in emission order, like ``search_n``'s per-child visited check.
    Returns ``(packed_rows, row_lens, totals, moves, count)``; child ``c`` is
    ``packed_rows[c, :row_lens[c]]`` with move ``moves[c] = (i, j, s, k1, k2)``.
    """
    # upper bound on children: for each ordered pair (i, j) both signs of
    # every rotation pair; sized from the ACTUAL lens (an over-cap start
    # relator may exceed cap, so cap-based sizing would be wrong).
    ub = 0
    max_len = 0
    for i in range(n_rel):
        if lens[i] > max_len:
            max_len = lens[i]
        for j in range(n_rel):
            if j != i:
                ub += 2 * lens[i] * lens[j]
    child_cap = cap if cap > max_len else max_len
    row_width = n_rel * child_cap + (n_rel - 1)
    packed_rows = np.empty((max(ub, 1), row_width), dtype=np.uint8)
    row_lens = np.empty(max(ub, 1), dtype=np.int64)
    totals = np.empty(max(ub, 1), dtype=np.int64)
    moves = np.empty((max(ub, 1), 5), dtype=np.int64)
    count = 0

    # spec/search.py:72 drops a child when ANY relator exceeds cap, inherited
    # ones included — hoisted to one guard per target, as in search_n.
    n_over = 0
    for r in range(n_rel):
        if lens[r] > cap:
            n_over += 1

    child = np.empty((n_rel, child_cap), dtype=np.int8)
    child_lens = np.empty(n_rel, dtype=np.int64)
    order = np.empty(n_rel, dtype=np.int64)

    for i in range(n_rel):
        if lens[i] == 0:
            continue
        over_i = 1 if lens[i] > cap else 0
        if n_over - over_i > 0:
            continue
        ri = words[i, :lens[i]]
        for j in range(n_rel):
            if j == i or lens[j] == 0:
                continue
            rj = words[j, :lens[j]]
            for s_idx in range(2):
                s = 1 if s_idx == 0 else -1
                oj = rj if s == 1 else inverse_nj(rj)
                cand, cand_lens, k1s, k2s, n_cand = expand_pair_nj(
                    ri, oj, cap, cyclic)
                for c in range(n_cand):
                    lc = cand_lens[c]
                    canon_i = canonical_word_nj(cand[c, :lc].copy())
                    # assemble the child: parent relators with slot i replaced
                    for r in range(n_rel):
                        if r == i:
                            child_lens[r] = len(canon_i)
                            for t in range(len(canon_i)):
                                child[r, t] = canon_i[t]
                        else:
                            child_lens[r] = lens[r]
                            for t in range(lens[r]):
                                child[r, t] = words[r, t]
                    # insertion sort by (len, booth-lex); stability is moot —
                    # relators equal under the key are identical.
                    for r in range(n_rel):
                        order[r] = r
                    for a in range(1, n_rel):
                        b = a
                        while b > 0 and _relator_lt(
                                child, child_lens, order[b], order[b - 1]):
                            tmp = order[b]
                            order[b] = order[b - 1]
                            order[b - 1] = tmp
                            b -= 1
                    # pack in sorted order (same bytes as solvern._tiebreak)
                    pos = 0
                    ctotal = 0
                    for r in range(n_rel):
                        if r > 0:
                            packed_rows[count, pos] = 0
                            pos += 1
                        row = order[r]
                        for t in range(child_lens[row]):
                            g = np.int64(child[row, t])
                            if g > 0:
                                packed_rows[count, pos] = g + 64
                            else:
                                packed_rows[count, pos] = -g
                            pos += 1
                        ctotal += child_lens[row]
                    row_lens[count] = pos
                    totals[count] = ctotal
                    moves[count, 0] = i
                    moves[count, 1] = j
                    moves[count, 2] = s
                    moves[count, 3] = k1s[c]
                    moves[count, 4] = k2s[c]
                    count += 1
    return packed_rows, row_lens, totals, moves, count


# ---------------------------------------------------------------------------
# Python layer: packed bytes <-> solvern's tuple states
# ---------------------------------------------------------------------------
#: tuple-of-int-tuples state -> packed bytes. The packed state IS the heap
#: tiebreak — one definition, imported, so the two can never drift.
_pack_key = _tiebreak


def _unpack_key(packed):
    """Packed bytes -> tuple-of-int-tuples state (inverse of ``_pack_key``)."""
    return tuple(
        tuple(b - 64 if b >= 65 else -b for b in seg)
        for seg in packed.split(b"\x00")
    )


def _solved(packed, n_rel):
    """Every relator has length 1 <=> n_rel single symbols + n_rel-1 seps."""
    if len(packed) != 2 * n_rel - 1:
        return False
    for idx, b in enumerate(packed):
        if (b == 0) != (idx % 2 == 1):
            return False
    return True


# ---------------------------------------------------------------------------
# the search — pop-for-pop identical to solvern.search_n
# ---------------------------------------------------------------------------
def search_n_fast(pres, budget, cap=64, cyclic=True, progress=None):
    """``solvern.search_n`` with fused numba bookkeeping — identical results.

    Same signature, same return dict, every field equal (paths included; the
    parent/move pointers are kept, so no recovery re-solve exists). Only the
    speed differs. Pinned by experiments/greedy_tests/test_solvern_fast.py.
    """
    n_rel = len(tuple(pres.relators))

    init_key = canonical_presentation(pres.relators, cyclic)
    init_packed = _pack_key(init_key)
    init_total = sum(len(r) for r in init_key)

    visited = {init_packed: None}          # packed -> (parent packed, move)
    pq = [(init_total, 0, init_packed)]

    min_packed = max_packed = max_expanded_packed = init_packed
    min_total = max_total = max_expanded_total = init_total

    nodes = 0
    solved_packed = None
    solved_depth = 0
    while pq and nodes < budget:
        total, depth, packed = heappop(pq)
        nodes += 1
        if progress is not None and nodes % _HB_CHECK_EVERY == 0:
            progress(nodes)
        if total > max_expanded_total:
            max_expanded_packed, max_expanded_total = packed, total

        if _solved(packed, n_rel):
            solved_packed = packed
            solved_depth = depth
            break

        words, lens = _unpack_state_nj(
            np.frombuffer(packed, dtype=np.uint8), n_rel)
        rows, row_lens, totals, moves, count = expand_node_packed_nj(
            words, lens, n_rel, cap, cyclic)
        depth1 = depth + 1
        for c in range(count):
            cpacked = rows[c, :row_lens[c]].tobytes()
            if cpacked in visited:
                continue
            m = moves[c]
            visited[cpacked] = (
                packed, (int(m[0]), int(m[1]), int(m[2]), int(m[3]), int(m[4])))
            ctotal = int(totals[c])
            if ctotal < min_total:
                min_packed, min_total = cpacked, ctotal
            elif ctotal > max_total:
                max_packed, max_total = cpacked, ctotal
            heappush(pq, (ctotal, depth1, cpacked))

    path_words, path_moves = [], []
    if solved_packed is not None:
        p = solved_packed
        while p is not None:
            path_words.append(_unpack_key(p))
            entry = visited[p]
            if entry is None:
                p = None
            else:
                p, mv = entry
                path_moves.append(mv)
        path_words.reverse()
        path_moves.reverse()

    min_key = _unpack_key(min_packed)
    max_key = _unpack_key(max_packed)
    max_expanded_key = _unpack_key(max_expanded_packed)
    return {
        "solved": solved_packed is not None,
        "nodes_explored": nodes,
        "path_length": solved_depth if solved_packed is not None else None,
        "min_relator_length": min_total,
        "min_relator": [word_to_str(r) for r in min_key],
        "max_relator_length": max_total,
        "max_relator": [word_to_str(r) for r in max_key],
        "max_relator_length_expanded": max_expanded_total,
        "max_relator_expanded": [word_to_str(r) for r in max_expanded_key],
        "path": [tuple(word_to_str(r) for r in st) for st in path_words],
        "path_words": path_words,
        "path_moves": [move_to_str(m) for m in path_moves],
    }
