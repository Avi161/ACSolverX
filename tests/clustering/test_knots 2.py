"""The knot definition: the balance theorem, the pure-power exception, cyclic invariance.

The theorem is what lets ``knot_number`` be a single expression instead of a convention, so it is
pinned here rather than trusted -- both by exhaustive enumeration over short words and against
every relator that actually ships in the two tables.
"""
import itertools
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from experiments.clustering.features import (  # noqa: E402
    block_counts, gen_runs, knot_number,
)

ALPHA = "xXyY"


def _reduced_cyclic(w):
    """Freely and cyclically reduced: no letter beside its own inverse, including at the seam."""
    if not w:
        return False
    inv = {"x": "X", "X": "x", "y": "Y", "Y": "y"}
    return all(inv[w[i]] != w[(i + 1) % len(w)] for i in range(len(w)))


def _words(nmax):
    for n in range(1, nmax + 1):
        for t in itertools.product(ALPHA, repeat=n):
            w = "".join(t)
            if _reduced_cyclic(w):
                yield w


def test_worked_examples():
    """The two examples the definition was specified against."""
    assert block_counts("yyyxxxyyyxxx") == (2, 2)
    assert knot_number("yyyxxxyyyxxx") == 2
    assert block_counts("yxxyxyxx") == (3, 3)
    assert knot_number("yxxyxyxx") == 3


def test_balance_theorem_exhaustive():
    """#x-blocks == #y-blocks for every cyclically reduced word using BOTH generators, |w| <= 9."""
    checked = 0
    for w in _words(9):
        gens = {c.lower() for c in w}
        if len(gens) < 2:
            continue
        nx, ny = block_counts(w)
        assert nx == ny, f"{w}: {nx} x-blocks vs {ny} y-blocks"
        checked += 1
    assert checked > 20_000, f"only {checked} two-generator words checked -- corpus too thin"


def test_pure_power_is_the_only_exception_and_scores_zero():
    """A word on one generator is the sole case outside the theorem, and it has 0 knots.

    Nothing is squashed inside anything when the other generator does not occur, so the literal
    reading of the definition gives 0 -- not the 1 a ``max(#x, #y)`` tie-break would produce.
    """
    for w in _words(8):
        nx, ny = block_counts(w)
        if nx != ny:
            assert len({c.lower() for c in w}) == 1, f"{w} unbalanced but uses both generators"
            assert {nx, ny} == {0, 1}
            assert knot_number(w) == 0
    assert block_counts("X") == (1, 0)
    assert knot_number("X") == 0
    assert block_counts("yyy") == (0, 1)
    assert knot_number("yyy") == 0
    # A single block of each generator is NOT a pure power and really is one knot.
    assert block_counts("YYYYxxx") == (1, 1)
    assert knot_number("YYYYxxx") == 1


def test_pure_power_convention_does_not_move_max_knots():
    """The 0-vs-1 choice must be inert where it matters: no presentation's max_knots may change.

    It only reaches min_knots, and only for the 7 presentations whose r1 is the bare relator X.
    """
    import csv as _csv
    alt = lambda w: max(block_counts(w))          # the rejected max() tie-break
    path = os.path.join(ROOT, "results", "equivalence_classes", "ms1190_tables",
                        "solved_640_aut_orbits.csv")
    moved_max, moved_min = 0, 0
    with open(path) as f:
        for row in _csv.DictReader(f):
            r1, r2 = row["rep_r1"], row["rep_r2"]
            if max(knot_number(r1), knot_number(r2)) != max(alt(r1), alt(r2)):
                moved_max += 1
            if min(knot_number(r1), knot_number(r2)) != min(alt(r1), alt(r2)):
                moved_min += 1
    assert moved_max == 0, f"{moved_max} presentations changed max_knots -- the choice is not inert"
    assert moved_min == 7, f"expected exactly 7 min_knots shifts (the X relators), got {moved_min}"


def test_knots_is_half_the_run_count_when_both_generators_occur():
    for w in _words(8):
        if len({c.lower() for c in w}) == 2:
            assert knot_number(w) == len(gen_runs(w)) // 2


def test_cyclic_invariance():
    """Rotating the ring must not move the count -- otherwise it reads the canonicaliser's cut."""
    for w in _words(8):
        base = knot_number(w)
        for k in range(1, len(w)):
            assert knot_number(w[k:] + w[:k]) == base, f"{w} rotated by {k}"


def test_inversion_and_relabel_invariance():
    """Knots survive relator inversion and the x<->y swap, both of which canon_pair quotients."""
    swap = {"x": "y", "y": "x", "X": "Y", "Y": "X"}
    inv = {"x": "X", "X": "x", "y": "Y", "Y": "y"}
    for w in _words(8):
        assert knot_number("".join(swap[c] for c in w)) == knot_number(w)
        assert knot_number("".join(inv[c] for c in reversed(w))) == knot_number(w)


@pytest.mark.parametrize("csvname,cols", [
    ("solved_640_aut_orbits.csv", ("rep_r1", "rep_r2")),
    ("unsolved_124_aca_classes.csv", ("r1", "r2")),
])
def test_balance_holds_on_every_shipped_relator(csvname, cols):
    import csv as _csv
    path = os.path.join(ROOT, "results", "equivalence_classes", "ms1190_tables", csvname)
    n_pure = 0
    with open(path) as f:
        for row in _csv.DictReader(f):
            for c in cols:
                nx, ny = block_counts(row[c])
                if len({ch.lower() for ch in row[c]}) == 2:
                    assert nx == ny, f"{row[c]}: {nx} vs {ny}"
                else:
                    n_pure += 1
                    assert min(nx, ny) == 0, f"{row[c]}: one-generator word must miss a block type"
                    assert knot_number(row[c]) == 0
    # The pure-power case must actually occur, or the exception branch is untested here.
    if csvname.startswith("solved"):
        assert n_pure > 0, "no pure-power relator found -- the max branch would be vacuous"
