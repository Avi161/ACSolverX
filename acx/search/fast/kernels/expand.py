"""Child expansion of one state: every legal substitution move, reduced and canonical.

A move ``(i, j, s, k1, k2)`` replaces ``r_i`` by ``rot(r_i, k1) * rot(r_j ** s, k2)`` and is legal when the seam
cancels at least one letter pair. ``expand`` builds the children exactly as ``acx.search.spec`` does; ``expand_drops``
also serves the cap counters, which need the children the cap dropped.

Two skips keep the work down (cyclic reduction only). In an ``(i, j, s)`` block the child of ``(k1, k2)`` is a
conjugate of the child of ``(k1 - 1, k2 + 1)`` whenever that predecessor's seam cancels, so both reduce to the same
canonical relator and the later one is a repeat the dedup table would drop anyway: the bitmap ``seen`` marks a move
when its child is written or skipped, and ``(k1, k2)`` is skipped only when its predecessor is marked. Over-cap moves
have their own bitmap ``dseen`` (the cyclically reduced length is a conjugacy invariant, so the successor of a dropped
move is dropped too); they are counted without being built.
"""
import numpy as np
from numba import njit

from .score import LENGTH, S20_MK2, rel_terms, s20_mk2
from .words import canon_buf, reduce_buf, rel_less


@njit(cache=True)
def max_children(lens):
    """Upper bound on the legal moves of a state with relator lengths ``lens``: ``sum_{i != j} 2 l_i l_j``."""
    total = squares = 0
    for n in lens:
        total += n
        squares += n * n
    return total * total - squares


@njit(cache=True)
def child_width(lens):
    """Upper bound on any child relator's length: ``max_{i != j} l_i + l_j``."""
    longest = second = 0
    for n in lens:
        if n > longest:
            longest, second = n, longest
        elif n > second:
            second = n
    return longest + second


# ---- one move ----------------------------------------------------------------------------------------------------

@njit(inline="always")
def _source_letter(syms, j, lj, s, t):
    """Letter ``t`` of ``r_j ** s`` (``s`` is 1 or -1)."""
    return syms[j, t] if s == 1 else syms[j, lj - 1 - t] ^ 1


@njit(inline="always")
def _seam_cancels(syms, i, li, j, lj, s, k1, k2):
    """Whether ``rot(r_i, k1) * rot(r_j ** s, k2)`` cancels at the seam."""
    last = syms[i, li - 1 - k1]
    first = _source_letter(syms, j, lj, s, lj - k2 if k2 else 0)
    return first == last ^ 1


@njit(inline="always")
def _join_rotations(syms, i, li, j, lj, s, k1, k2, buf):
    """Write ``rot(r_i, k1) * rot(r_j ** s, k2)`` to ``buf[:li + lj]``."""
    for t in range(li):
        u = t - k1
        buf[t] = syms[i, u + li if u < 0 else u]
    for t in range(lj):
        u = t - k2
        buf[li + t] = _source_letter(syms, j, lj, s, u + lj if u < 0 else u)


@njit(inline="always")
def _predecessor(lj, k1, k2):
    """Bitmap index of the move ``(k1 - 1, k2 + 1)``, whose child may equal the child of ``(k1, k2)``."""
    return (k1 - 1) * lj + (k2 + 1 if k2 + 1 < lj else 0)


# ---- the state around the move -----------------------------------------------------------------------------------

@njit(inline="always")
def _canonical_untouched(syms, lens, cyclic, can, cl, buf):
    """Each relator reduced and canonical into ``can[r]``, its length in ``cl[r]`` (the identity on a cyclic state)."""
    for r in range(len(lens)):
        for t in range(lens[r]):
            buf[t] = syms[r, t]
        lo, m = reduce_buf(buf, lens[r], cyclic)
        canon_buf(buf, lo, m, can[r])
        cl[r] = m


@njit(inline="always")
def _other_relator_over_cap(cl, i, cap):
    """Whether a relator other than ``r_i`` is over the cap, which rejects every move of ``r_i``."""
    if cap < 0:
        return False
    for k in range(len(cl)):
        if k != i and cl[k] > cap:
            return True
    return False


@njit(inline="always")
def _count_legal_moves(syms, j, lj, s, letter_count):
    """Legal moves of ``r_i`` with ``r_j ** s``, given how often each symbol occurs in ``r_i``.

    A move is legal exactly when the seam letters are inverse, so each letter of ``r_j ** s`` pairs with every
    occurrence of its inverse in ``r_i``.
    """
    legal = 0
    for t in range(lj):
        legal += letter_count[_source_letter(syms, j, lj, s, t) ^ 1]
    return legal


@njit(inline="always")
def _sort_order(order, can, cl, new, m, i):
    """Fill ``order`` with the relator indices sorted by ``rel_less``; relator ``i`` is the new one (length ``m``)."""
    for a in range(len(order)):
        order[a] = a
        b = a
        while b > 0:
            x, y = order[b - 1], order[b]
            wx = new if x == i else can[x]
            wy = new if y == i else can[y]
            lx = m if x == i else cl[x]
            ly = m if y == i else cl[y]
            if not rel_less(wy, ly, wx, lx):
                break
            order[b - 1], order[b] = y, x
            b -= 1


@njit(inline="always")
def _write_state(dst, dst_len, c, order, can, cl, new, m, i):
    """Write the relators in ``order`` as state ``c`` of ``dst`` / ``dst_len``."""
    for a in range(len(order)):
        x = order[a]
        n = m if x == i else cl[x]
        word = new if x == i else can[x]
        for t in range(n):
            dst[c, a, t] = word[t]
        dst_len[c, a] = n


@njit(inline="always")
def _write_move(out_mv, c, i, j, s, k1, k2):
    out_mv[c, 0] = i
    out_mv[c, 1] = j
    out_mv[c, 2] = s
    out_mv[c, 3] = k1
    out_mv[c, 4] = k2


# ---- scoring the dropped children (cap counters) -----------------------------------------------------------------

@njit(inline="always")
def _untouched_terms(can, cl, n_gen, terms):
    """``terms[r]`` = the S20_MK2 terms of untouched relator ``r`` (all zero for an empty one)."""
    for r in range(len(cl)):
        if cl[r] > 0:
            a, b, c, d, e = rel_terms(can[r], 0, cl[r], n_gen)
            terms[r, 0], terms[r, 1], terms[r, 2], terms[r, 3], terms[r, 4] = a, b, c, d, e


@njit(inline="always")
def _others_terms(terms, i):
    """The pooled S20_MK2 terms of every relator but ``i``: ``(x_letters, y_letters, x_blocks, y_blocks, knots)``."""
    x_letters = y_letters = x_blocks = y_blocks = knots = 0
    for k in range(len(terms)):
        if k != i:
            x_letters += terms[k, 0]
            y_letters += terms[k, 1]
            x_blocks += terms[k, 2]
            y_blocks += terms[k, 3]
            knots = max(knots, terms[k, 4])
    return x_letters, y_letters, x_blocks, y_blocks, knots


@njit(inline="always")
def _drop_score(pid, total, others, buf, start, m, n_gen, build, dmin):
    """The score of a dropped child, from its reduced relator ``buf[start:start+m]`` (before canonicalisation).

    Returns ``(skip, score)``. When no drop is built, an S20_MK2 child whose lower bound ``L + 2 MK_others + 20``
    cannot lower ``dmin`` is skipped unscored (``S >= 1`` and ``MK >= MK_others``).
    """
    if pid == LENGTH:
        return False, float(total)
    x_letters, y_letters, x_blocks, y_blocks, knots = others
    if not build and total + 2.0 * knots + 20.0 >= dmin:
        return True, 0.0
    lx = ly = bx = by = k = 0
    if m > 0:
        lx, ly, bx, by, k = rel_terms(buf, start, m, n_gen)
    return False, s20_mk2(total, max(knots, k), x_blocks + bx, y_blocks + by, x_letters + lx, y_letters + ly)


# ---- the expansion -----------------------------------------------------------------------------------------------

@njit(inline="always")
def _expand(syms, lens, n_gen, cap, cyclic, out, out_len, out_mv, dout, dout_len, dprio, pid, dmax, kept):
    """The kernel behind ``expand`` and ``expand_drops``; see ``expand_drops`` for the arguments.

    With ``pid >= 0`` every dropped child is scored; ``dout`` empty means none is built. Returns
    ``(count, rejected, dcount, dmin, tmin)``.
    """
    R = len(lens)
    widest = 1
    for r in range(R):
        widest = max(widest, lens[r])
    can = np.empty((R, widest), dtype=np.uint8)          # the untouched relators
    cl = np.empty(R, dtype=np.int64)
    buf = np.empty(2 * widest, dtype=np.uint8)
    _canonical_untouched(syms, lens, cyclic, can, cl, buf)
    track = pid >= 0
    build = track and len(dout) > 0
    scoring_s20 = track and pid == S20_MK2
    terms = np.zeros((R, 5), dtype=np.int64)
    if scoring_s20:
        _untouched_terms(can, cl, n_gen, terms)
    total = 0
    for r in range(R):
        total += cl[r]
    new = np.empty(2 * widest, dtype=np.uint8)
    seen = np.zeros(widest * widest, dtype=np.bool_)
    dseen = np.zeros(widest * widest, dtype=np.bool_)    # dropped moves (cut-shift repeats of drops)
    order = np.empty(R, dtype=np.int64)
    letter_count = np.zeros(2 * n_gen, dtype=np.int64)
    count = rejected = dcount = 0
    dmin = np.inf
    tmin = -1
    for i in range(R):
        li = lens[i]
        if li == 0:
            continue
        over = _other_relator_over_cap(cl, i, cap)
        count_only = over and not track
        if count_only:       # every legal move of r_i is dropped: count them without building children
            letter_count[:] = 0
            for t in range(li):
                letter_count[syms[i, t]] += 1
        rest = total - cl[i]
        others = (0, 0, 0, 0, 0)
        if scoring_s20:
            others = _others_terms(terms, i)
        for j in range(R):
            lj = lens[j]
            if j == i or lj == 0:
                continue
            for s in (1, -1):
                if count_only:
                    rejected += _count_legal_moves(syms, j, lj, s, letter_count)
                    continue
                if cyclic:
                    seen[:li * lj] = False
                    dseen[:li * lj] = False
                for k1 in range(li):
                    for k2 in range(lj):
                        if not _seam_cancels(syms, i, li, j, lj, s, k1, k2):
                            continue
                        mark = k1 * lj + k2
                        if cyclic and k1 >= 1:
                            before = _predecessor(lj, k1, k2)
                            if seen[before]:                      # cut-shift repeat
                                seen[mark] = True
                                continue
                            if dseen[before]:                     # cut-shift repeat of a dropped move
                                dseen[mark] = True
                                rejected += 1
                                continue
                        _join_rotations(syms, i, li, j, lj, s, k1, k2, buf)
                        start, m = reduce_buf(buf, li + lj, cyclic)
                        dropped = over or (cap >= 0 and m > cap)
                        dp = 0.0
                        if dropped:
                            rejected += 1
                            if cyclic:
                                dseen[mark] = True
                            if not track:
                                continue
                            child_total = rest + m
                            if tmin < 0 or child_total < tmin:
                                tmin = child_total
                            skip, dp = _drop_score(pid, child_total, others, buf, start, m, n_gen, build, dmin)
                            if skip:
                                continue
                            dmin = min(dmin, dp)
                            if not build or dp > dmax:
                                continue
                        else:
                            if cyclic:
                                seen[mark] = True
                            if not kept:
                                continue
                        canon_buf(buf, start, m, new)
                        _sort_order(order, can, cl, new, m, i)
                        if dropped:
                            _write_state(dout, dout_len, dcount, order, can, cl, new, m, i)
                            dprio[dcount] = dp
                            dcount += 1
                        else:
                            _write_state(out, out_len, count, order, can, cl, new, m, i)
                            _write_move(out_mv, count, i, j, s, k1, k2)
                            count += 1
    return count, rejected, dcount, dmin, tmin


@njit(cache=True)
def expand(syms, lens, n_gen, cap, cyclic, out, out_len, out_mv):
    """Write every new-relator child of the state ``(syms, lens)`` into ``out[c]`` / ``out_len[c]``, with its move
    ``(i, j, s, k1, k2)`` in ``out_mv[c]``, exactly as ``acx.search.spec`` builds them (order ``i -> j -> s -> k1
    -> k2``; relators reduced, canonical and sorted by ``(length, Booth order)``). ``cap < 0`` is uncapped.

    Returns ``(count, rejected)``: ``rejected`` counts the legal moves whose child has a relator over the cap
    (``cap_dropped``). ``out`` needs ``max_children(lens)`` rows and ``child_width(lens)`` columns.
    """
    dout = np.empty((0, 1, 1), dtype=np.uint8)
    dout_len = np.empty((0, 1), dtype=np.int32)
    dprio = np.empty(0, dtype=np.float64)
    count, rejected, _, _, _ = _expand(syms, lens, n_gen, cap, cyclic, out, out_len, out_mv,
                                       dout, dout_len, dprio, -1, np.inf, True)
    return count, rejected


@njit(cache=True)
def expand_drops(syms, lens, n_gen, cap, cyclic, out, out_len, out_mv, dout, dout_len, dprio, pid, dmax, kept):
    """``expand`` that also serves the cap counters. Returns ``(count, rejected, dcount, dmin, tmin)``.

    With ``pid >= 0`` it scores every dropped child from its reduced relator (the float ``score`` gives the built
    child), returns the least score ``dmin`` and least total ``tmin`` over the drops, and builds the drops scoring
    ``<= dmax`` (canonical and sorted, one per cut-shift repeat class, so ``dcount <= rejected``) into ``dout`` /
    ``dout_len`` / ``dprio``; ``dout`` needs ``max_children(lens)`` rows and ``child_width(lens)`` columns.
    ``kept=False`` skips building the kept children.
    """
    return _expand(syms, lens, n_gen, cap, cyclic, out, out_len, out_mv, dout, dout_len, dprio, pid, dmax, kept)
