"""Heap priorities, lower pops first: ``length`` (total relator length, an int) and ``s20_mk2`` (a float).

``PRIORITIES`` maps names to functions of the relators; ``get`` looks one up. ``acx.search.fast.kernels.score``
computes the same values, bit for bit.
"""


def _blocks(w):
    """Cyclic generator runs of ``w`` as ``(generator, length)`` pairs."""
    runs = []
    for g in w:
        a = abs(g)
        if runs and runs[-1][0] == a:
            runs[-1][1] += 1
        else:
            runs.append([a, 1])
    if len(runs) > 1 and runs[0][0] == runs[-1][0]:
        runs[0][1] += runs.pop()[1]
    return runs


def length(rels):
    """The ``length`` priority: total relator length."""
    return sum(map(len, rels))


def features(rels):
    """``(L, MK, S)`` of a two-generator presentation, reading relators as rings of generator runs.

    ``L``: total length. Blocks are cyclic runs of one generator (``x`` and ``X`` count alike; a run across the
    seam is one block). ``knots(r)`` is 0 for a pure power, else max(#x-blocks, #y-blocks); ``MK`` is the largest
    knots. ``S`` is the smaller of the mean x-block and mean y-block lengths pooled over all relators (the one
    nonzero mean when a generator is absent). ``ValueError`` past two generators.
    """
    mk = nx = ny = sx = sy = 0
    for r in rels:
        b = _blocks(r)
        bx = [n for g, n in b if g == 1]
        by = [n for g, n in b if g == 2]
        if len(bx) + len(by) != len(b):
            raise ValueError("s20_mk2 is defined for two generators only")
        k = max(len(bx), len(by)) if bx and by else 0
        mk = max(mk, k)
        nx, ny, sx, sy = nx + len(bx), ny + len(by), sx + sum(bx), sy + sum(by)
    mx = sx / nx if nx else 0.0
    my = sy / ny if ny else 0.0
    if nx == 0 or ny == 0:
        s = my if mx == 0.0 else mx
    else:
        s = mx if mx < my else my
    return sx + sy, mk, s


def s20_mk2(rels):
    """The ``s20_mk2`` priority ``L + 20 S + 2 MK`` (``features``), summed in the order L, MK, S: the fast
    engine's order, so both backends give identical floats."""
    L, mk, s = features(rels)
    acc = 0.0
    acc += 1.0 * L
    acc += 2.0 * mk
    acc += 20.0 * s
    return acc


PRIORITIES = {"length": length, "s20_mk2": s20_mk2}


def get(name):
    """The priority function called ``name``; ``ValueError`` for an unknown name."""
    try:
        return PRIORITIES[name]
    except KeyError:
        raise ValueError(f"unknown priority {name!r}; choose from {sorted(PRIORITIES)}") from None
