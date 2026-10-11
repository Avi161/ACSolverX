"""Heap priorities: LENGTH (default) and S20_MK2. Lower pops first.

``length``  = L, the total relator length (main's baseline ordering; an int).

``s20_mk2`` = L + 20*S + 2*MK (a float), the single shipped tuned vector
(``origin/claude/heuristic-search-benchmark-e1f9l8:experiments/search/heuristics.py``,
``S20_MK2``), two generators only. Every term reads relators as rings:

* blocks: cyclic runs of one GENERATOR (``x`` and ``X`` are the same generator);
  a run wrapping the seam is one block.
* knots(r) = 0 if ``r`` is a pure power, else max(#x-blocks, #y-blocks);
  MK = max knots over the relators.
* S = the smaller mean block length: ``mx = x-letters / x-blocks`` and
  ``my = y-letters / y-blocks`` pooled over all relators (0.0 when a generator
  has no block); S = min(mx, my), or the one nonzero mean when a generator is
  absent from the whole presentation.

The float is evaluated in this exact operation order, which is the fast
engine's (``hfast.expand_and_score_nj`` sums weights in feature-index order
L, MK, S) so both backends produce bit-identical scores::

    acc = 0.0; acc += 1.0 * L; acc += 2.0 * MK; acc += 20.0 * S

(main's pure-Python ``make_priority`` adds S before MK; the two can differ in
the last ulp, so the fast engine's order is the reference here.)
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
    return sum(map(len, rels))


def features(rels):
    """``(L, MK, S)`` for a two-generator presentation."""
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
    L, mk, s = features(rels)
    acc = 0.0
    acc += 1.0 * L
    acc += 2.0 * mk
    acc += 20.0 * s
    return acc


PRIORITIES = {"length": length, "s20_mk2": s20_mk2}


def get(name):
    try:
        return PRIORITIES[name]
    except KeyError:
        raise ValueError(f"unknown priority {name!r}; choose from {sorted(PRIORITIES)}") from None
