"""Heap priority of one state, in numba: the kernel twin of ``acx.core.priority``.

``LENGTH`` (0) gives the total length. ``S20_MK2`` (1) gives ``L + 20 S + 2 MK`` (two generators; see
``acx.core.priority`` for the terms) in the reference operation order, so scores are bit-identical (no fastmath
anywhere, hence no FMA contraction).
"""
from numba import njit

LENGTH, S20_MK2 = 0, 1
PRIORITY_IDS = {"length": LENGTH, "s20_mk2": S20_MK2}


def priority_id(priority, rels):
    """The kernel id of a priority name; ``s20_mk2`` needs two generators, as in ``acx.core.priority``."""
    if priority == "s20_mk2" and any(abs(g) > 2 for r in rels for g in r):
        raise ValueError("s20_mk2 is defined for two generators only")
    return PRIORITY_IDS[priority]


@njit(inline="always")
def rel_terms(w, lo, m, n_gen):
    """S20_MK2 terms of one relator ``w[lo:lo+m]`` (``m > 0``).

    Returns ``(x_letters, y_letters, x_blocks, y_blocks, knots)``, blocks read cyclically (so any rotation or
    inverse gives the same terms). A cyclic word in x and y alternates x- and y-blocks: with ``T`` cyclic generator
    changes there are ``T / 2`` blocks of each (one block of one generator when ``T == 0``), and the knots are the
    blocks of one generator. So the per-letter loop has no branch.
    """
    x_gen = n_gen - 1                    # Booth symbol >> 1 of x; any other generator counts as y
    prev_is_x = (w[lo + m - 1] >> 1) == x_gen
    x_letters = changes = 0
    for t in range(m):
        is_x = (w[lo + t] >> 1) == x_gen
        x_letters += is_x
        changes += is_x != prev_is_x
        prev_is_x = is_x
    if changes == 0:
        return x_letters, m - x_letters, 1 if x_letters else 0, 0 if x_letters else 1, 0
    blocks = changes >> 1
    return x_letters, m - x_letters, blocks, blocks, blocks


@njit(inline="always")
def s20_mk2(total, knots, x_blocks, y_blocks, x_letters, y_letters):
    """``L + 20 S + 2 MK`` from the pooled terms, in the operation order of ``acx.core.priority.s20_mk2``."""
    x_mean = x_letters / x_blocks if x_blocks else 0.0
    y_mean = y_letters / y_blocks if y_blocks else 0.0
    if x_blocks == 0 or y_blocks == 0:
        smaller_mean = y_mean if x_mean == 0.0 else x_mean
    else:
        smaller_mean = x_mean if x_mean < y_mean else y_mean
    acc = 0.0
    acc += 1.0 * total
    acc += 2.0 * knots
    acc += 20.0 * smaller_mean
    return acc


@njit(cache=True)
def score(row, rlen, n_gen, prio):
    """Heap priority of one state: the total length for ``LENGTH``, ``L + 20 S + 2 MK`` for ``S20_MK2``."""
    total = 0
    for r in range(len(rlen)):
        total += rlen[r]
    if prio == LENGTH:
        return float(total)
    knots = x_blocks = y_blocks = x_letters = y_letters = 0
    for r in range(len(rlen)):
        if rlen[r] > 0:
            lx, ly, bx, by, k = rel_terms(row[r], 0, rlen[r], n_gen)
            x_letters += lx
            y_letters += ly
            x_blocks += bx
            y_blocks += by
            knots = max(knots, k)
    return s20_mk2(total, knots, x_blocks, y_blocks, x_letters, y_letters)
