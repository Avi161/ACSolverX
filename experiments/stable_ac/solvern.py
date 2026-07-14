"""General-n greedy best-first S-move solver — CPU + numba only.

A numba port of ``experiments/greedy_tests/spec/search.py``, generalised to any
``n_gen`` (<= 26 for rendering) and any ``n_rel >= 2``. It reproduces the spec's
pop order exactly wherever the spec can run (``n_gen <= 3``), so spec
trace-equality is a bonus test rather than a coincidence.

Words are 1-D ``np.int8`` arrays: generator ``i`` is ``+-i`` (exactly the spec's
signed-int tuples). Rendering to characters is I/O only — the search never
touches strings.

TWO SYMBOL ORDERS COEXIST and must never be conflated (see spec/words.py):

* BOOTH order ``(-abs(g), g > 0)`` -> ``Z < z < Y < y < X < x``. This is what
  canonicalisation minimises over and what the relator-list sort uses. It only
  decides which representative of an orbit is stored.
* ASCII order ``(g > 0, abs(g))`` -> ``X < Y < Z < x < y < z``. The heap
  tie-breaks on the rendered state key, so the packed-bytes tiebreak must
  reproduce THIS order (uppercase/inverse block below the lowercase block).
"""

from dataclasses import dataclass
from heapq import heappop, heappush

import numpy as np
from numba import njit

_HB_CHECK_EVERY = 1024

#: first 3 are identical to the spec ("xyz"); the rest extend rendering to n=26.
GEN_CHARS = "xyz" + "abcdefghijklmnopqrstuvw"


# ---------------------------------------------------------------------------
# @njit primitives on 1-D int8 words (all n-agnostic)
# ---------------------------------------------------------------------------
@njit(cache=True)
def reduce_word_nj(w, cyclic=True):
    """Free-reduce; when ``cyclic`` also cancel across the wrap-around.

    Stack-based (guarded peeks): a word that cancels completely returns the
    empty word. The cyclic tail mirrors spec ``reduce_word`` / the baseline
    ``reduce_relator_nj`` exactly, including the strict ``i < length / 2`` bound
    (which is why the cyclic step can never empty an already free-reduced word).
    """
    n = len(w)
    if n == 0:
        return w
    buf = np.empty(n, dtype=np.int8)
    length = 0
    for idx in range(n):
        if length > 0 and buf[length - 1] == -w[idx]:
            length -= 1
        else:
            buf[length] = w[idx]
            length += 1
    red = buf[:length]
    if cyclic and length > 1 and red[0] == -red[length - 1]:
        i = 1
        half = length / 2
        while i < half and red[i] == -red[length - 1 - i]:
            i += 1
        red = red[i:length - i]
    return red


@njit(cache=True)
def inverse_nj(w):
    n = len(w)
    out = np.empty(n, dtype=np.int8)
    for idx in range(n):
        out[idx] = -w[n - 1 - idx]
    return out


@njit(inline='always')
def _booth_lt(a, b):
    """``a < b`` under booth order ``(-abs(g), g > 0)`` (Z<z<Y<y<X<x)."""
    aa = abs(a)
    ab = abs(b)
    if aa != ab:
        return aa > ab
    return a < b


@njit(inline='always')
def _booth_word_lt(a, b):
    """Lexicographic ``a < b`` under booth order, shorter-prefix-first."""
    la = len(a)
    lb = len(b)
    m = la if la < lb else lb
    for idx in range(m):
        if a[idx] != b[idx]:
            return _booth_lt(a[idx], b[idx])
    return la < lb


@njit(cache=True)
def booth_min_rotation_nj(w):
    """Index-min cyclic rotation under booth order, via Booth's algorithm."""
    n = len(w)
    if n == 0:
        return w
    ww = np.empty(2 * n, dtype=np.int8)
    for idx in range(n):
        ww[idx] = w[idx]
        ww[idx + n] = w[idx]
    f = np.full(2 * n, -1, dtype=np.int64)
    k = 0
    for j in range(1, 2 * n):
        i = f[j - k - 1]
        while i != -1 and ww[j] != ww[k + i + 1]:
            if _booth_lt(ww[j], ww[k + i + 1]):
                k = j - i - 1
            i = f[i]
        if i == -1 and ww[j] != ww[k]:
            if _booth_lt(ww[j], ww[k]):
                k = j
            f[j - k] = -1
        else:
            f[j - k] = i + 1
    out = np.empty(n, dtype=np.int8)
    for idx in range(n):
        out[idx] = ww[k + idx]
    return out


@njit(cache=True)
def canonical_word_nj(w):
    """Least element of the orbit of ``w`` under rotation and inversion."""
    if len(w) == 0:
        return w
    a = booth_min_rotation_nj(w)
    b = booth_min_rotation_nj(inverse_nj(w))
    if _booth_word_lt(b, a):
        return b
    return a


@njit(cache=True)
def expand_pair_nj(ri, oj, cap, cyclic):
    """Every seam-cancelling ``rot_k1(ri) . rot_k2(oj)``, reduced, cap-filtered.

    Returns ``(words, lens, k1s, k2s, count)``; child ``c`` is the reduced new
    target relator ``words[c, :lens[c]]`` produced by rotations ``k1s[c], k2s[c]``.
    Only per-relator cap applies (no total-length cap). Follows the baseline
    ``expand_node_nj`` efficiency pattern: rotations of ``oj`` are hoisted out of
    the ``k1`` loop, and only matching (k1, k2) seams are concatenated.
    """
    len_i = len(ri)
    len_o = len(oj)
    ub = len_i * len_o
    words = np.empty((ub, cap), dtype=np.int8)
    lens = np.empty(ub, dtype=np.int64)
    k1s = np.empty(ub, dtype=np.int64)
    k2s = np.empty(ub, dtype=np.int64)
    count = 0
    if len_i == 0 or len_o == 0:
        return words, lens, k1s, k2s, count

    rots_o = [np.roll(oj, k2) for k2 in range(len_o)]
    for k1 in range(len_i):
        rot_i = np.roll(ri, k1)
        last = rot_i[len_i - 1]
        for k2 in range(len_o):
            rot_o = rots_o[k2]
            if last != -rot_o[0]:
                continue
            piece = np.concatenate((rot_i, rot_o))
            red = reduce_word_nj(piece, cyclic)
            lr = len(red)
            if lr > cap:
                continue
            for t in range(lr):
                words[count, t] = red[t]
            lens[count] = lr
            k1s[count] = k1
            k2s[count] = k2
            count += 1
    return words, lens, k1s, k2s, count


# ---------------------------------------------------------------------------
# Python layer: codecs, canonicalisation, keys, replay
# ---------------------------------------------------------------------------
def symbol_to_char(g):
    c = GEN_CHARS[abs(g) - 1]
    return c if g > 0 else c.upper()


def char_to_symbol(c):
    g = GEN_CHARS.index(c.lower()) + 1
    return g if c.islower() else -g


def word_to_str(w):
    return "".join(symbol_to_char(g) for g in w)


def str_to_word(s):
    return tuple(char_to_symbol(c) for c in s)


def _sort_key(r):
    """spec Presentation.canonical's ordering: (length, booth-lex)."""
    return (len(r), tuple((-abs(g), g > 0) for g in r))


def _canonical_relator(r, cyclic):
    arr = np.array([int(g) for g in r], dtype=np.int8)
    red = reduce_word_nj(arr, cyclic)
    canon = canonical_word_nj(red)
    return tuple(int(x) for x in canon)


def canonical_presentation(relators, cyclic=True):
    """Canonicalise each relator, then sort the list by (length, booth-lex).

    Returns the canonical state as a tuple of int-tuples (the visited-dict key).
    Matches spec Presentation.canonical (presentation.py:56-62).
    """
    canon = [_canonical_relator(r, cyclic) for r in relators]
    canon.sort(key=_sort_key)
    return tuple(canon)


def _tiebreak(relators):
    """Packed-bytes heap tiebreak reproducing spec's ASCII string-tuple order.

    Per word ``bytes(abs(g) + 64*(g>0))``: inverses map to 1..26, generators to
    65..90, so the inverse block sorts below the generator block and indices
    ascend within a block -- exactly ``ascii_order_key``. Words are joined by a
    0 separator, which is below every symbol byte, so the shorter word sorts
    first (Python's string-prefix rule) and the join compares elementwise.
    """
    return b"\x00".join(
        bytes(abs(g) + 64 * (g > 0) for g in r) for r in relators
    )


def move_to_str(move):
    """(i, j, s, k1, k2) tuple -> 'i_j_s_k1_k2'."""
    return "_".join(str(int(v)) for v in move)


def str_to_move(s):
    """'i_j_s_k1_k2' -> (i, j, s, k1, k2) int tuple."""
    return tuple(int(v) for v in s.split("_"))


def moves_to_states(start_relators, moves, cyclic=True):
    """Authoritative replay: apply the raw move, reduce, canonicalise per step.

    ``moves`` are 'i_j_s_k1_k2' strings or (i, j, s, k1, k2) tuples. Returns the
    list of int-tuple states (length ``len(moves) + 1``), the canonical parent
    first. The stored move is relative to the canonical parent, so decoding is
    replay, never a diff of stored states.
    """
    cur = canonical_presentation(start_relators, cyclic)
    out = [cur]
    for mv in moves:
        if isinstance(mv, str):
            mv = str_to_move(mv)
        i, j, s, k1, k2 = mv
        ri = np.array([int(g) for g in cur[i]], dtype=np.int8)
        rj = np.array([int(g) for g in cur[j]], dtype=np.int8)
        oj = rj if s == 1 else inverse_nj(rj)
        piece = np.concatenate((np.roll(ri, k1), np.roll(oj, k2)))
        red = reduce_word_nj(piece, cyclic)
        canon = tuple(int(x) for x in canonical_word_nj(red))
        child = list(cur)
        child[i] = canon
        child.sort(key=_sort_key)
        cur = tuple(child)
        out.append(cur)
    return out


# ---------------------------------------------------------------------------
# Tietze: add a generator with a word (AC4 + the isolate step, as one relator)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Pres:
    n_gen: int
    relators: tuple

    def __post_init__(self):
        object.__setattr__(
            self, "relators", tuple(tuple(int(g) for g in r) for r in self.relators)
        )

    @property
    def n_rel(self):
        return len(self.relators)

    @property
    def is_balanced(self):
        return self.n_rel == self.n_gen


def add_generator_with_word(relator_strs, w_str, n_gen=None):
    """``<g1..gk | R>`` -> ``<g1..gk, g_{k+1} | R, G_{k+1}.w>``.

    The new relator is the inverse of the new generator followed by ``w``. When
    ``n_gen`` is omitted it is inferred from the letters present.
    """
    words = [str_to_word(s) for s in relator_strs]
    w = str_to_word(w_str)
    if n_gen is None:
        n_gen = max((abs(g) for r in words for g in r), default=0)
    z = n_gen + 1
    new_relator = (-z,) + w
    return Pres(z, tuple(words) + (new_relator,))


def nocov_presentation(r1, r2, w):
    """Branch-A no-CoV target: ``<x, y, z | r1, r2, Z.w>`` (add_generator at k=2)."""
    return add_generator_with_word([r1, r2], w, n_gen=2)


# ---------------------------------------------------------------------------
# The search
# ---------------------------------------------------------------------------
def search_n(pres, budget, cap=64, cyclic=True, progress=None):
    """Greedy best-first S-move search over canonical presentations.

    ``pres`` is anything with ``.n_gen`` and ``.relators`` (spec Presentation
    works; relators as int tuples). Returns a stats dict generalised to n_rel
    relators. Per-relator cap only (no total-length cap); a child is dropped
    when ANY of its relators exceeds cap, inherited ones included, exactly as
    spec/search.py does. Spec-shaped loop: pop, count, progress every
    1024 pops, terminate when every relator has length 1, expand i->j->s->k1->k2
    (j != i, empty relators skipped), first-time-seen children pushed at
    depth+1, and min/max stats updated by FIRST-CROSSING during iteration.
    """
    n_gen = pres.n_gen
    n_rel = len(tuple(pres.relators))

    init_key = canonical_presentation(pres.relators, cyclic)
    init_total = sum(len(r) for r in init_key)

    visited = {init_key: None}
    move_in = {init_key: None}
    pq = [(init_total, 0, _tiebreak(init_key), init_key)]

    min_key = max_key = max_expanded_key = init_key
    min_total = max_total = max_expanded_total = init_total

    nodes = 0
    solved_key = None
    while pq and nodes < budget:
        total, depth, _tb, key = heappop(pq)
        nodes += 1
        if progress is not None and nodes % _HB_CHECK_EVERY == 0:
            progress(nodes)
        if total > max_expanded_total:
            max_expanded_key, max_expanded_total = key, total

        if all(len(r) == 1 for r in key):
            solved_key = key
            break

        arrs = [np.array([int(g) for g in r], dtype=np.int8) for r in key]
        # spec/search.py:72 drops a child when ANY of its relators exceeds cap,
        # inherited ones included. An inherited relator is over-cap iff the
        # parent carries an over-cap relator other than the target (only the
        # start state can — every pushed child is fully cap-filtered), so the
        # check hoists to one guard per target instead of one per child.
        over = [len(r) > cap for r in key]
        n_over = sum(over)
        depth1 = depth + 1
        for i in range(n_rel):
            if len(key[i]) == 0:
                continue
            if n_over - over[i] > 0:
                continue
            ri = arrs[i]
            for j in range(n_rel):
                if j == i or len(key[j]) == 0:
                    continue
                for s in (1, -1):
                    oj = arrs[j] if s == 1 else inverse_nj(arrs[j])
                    words, lens, k1s, k2s, count = expand_pair_nj(
                        ri, oj, cap, cyclic)
                    for c in range(count):
                        lc = lens[c]
                        canon_i = canonical_word_nj(words[c, :lc].copy())
                        child = list(key)
                        child[i] = tuple(int(x) for x in canon_i)
                        child.sort(key=_sort_key)
                        ckey = tuple(child)
                        if ckey in visited:
                            continue
                        visited[ckey] = key
                        move_in[ckey] = (i, j, s, int(k1s[c]), int(k2s[c]))
                        ctotal = sum(len(r) for r in ckey)
                        if ctotal < min_total:
                            min_key, min_total = ckey, ctotal
                        elif ctotal > max_total:
                            max_key, max_total = ckey, ctotal
                        heappush(pq, (ctotal, depth1, _tiebreak(ckey), ckey))

    path_words, path_moves = [], []
    if solved_key is not None:
        k = solved_key
        while k is not None:
            path_words.append(k)
            if move_in[k] is not None:
                path_moves.append(move_in[k])
            k = visited[k]
        path_words.reverse()
        path_moves.reverse()

    return {
        "solved": solved_key is not None,
        "nodes_explored": nodes,
        "path_length": len(path_moves) if solved_key is not None else None,
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
