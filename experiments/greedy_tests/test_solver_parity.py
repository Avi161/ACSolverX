"""Exact-trace parity between the normal and heavy solvers.

These are two implementations of one search, so they owe each other an exact
trace: same ``solved``, same ``nodes_explored``, same length statistics. That is
the whole justification for ``HIGH_SPEEDUP`` -- it is only allowed to be cheaper,
never different.

Two fields are deliberately excluded. The normal solver picks ``min_relator`` and
``max_relator`` with ``min()``/``max()`` over a ``set``, so ties among equal-length
states are broken by ``PYTHONHASHSEED``; the heavy solver takes the first state
that strictly beat the running extreme. Their *lengths* always agree; their
*strings* need not, and measurably do not (``max_relator`` in ~85% of runs,
``min_relator`` in ~8%). ``max_relator_expanded`` is set during the deterministic
pop sequence, so it does agree and is asserted.

This parity is a contract of *this pair*. A future stable-AC solver owes no such
thing -- see ``adapters.PARITY_PAIR``.
"""

import pytest

from experiments.search.greedy_baseline import greedy_search
from experiments.greedy_tests.fixtures.presentations import (
    MMS02_LEN14, ak, ms640, ms_unsolved,
)

#: solved, budget-capped, and structurally awkward inputs
FAST_CASES = (
    [(p, 1000) for p in ms640(range(0, 10))]
    + [(p, 800) for p in ms_unsolved(range(0, 2))]
    + [(ak(3), 600), (MMS02_LEN14, 600)]
)
#: Deeper searches across the cap x cyclic matrix. The budget stays small on
#: purpose: parity is a statement about the *pop sequence*, and a run at budget B
#: is the first B pops of any longer run, so a longer budget cannot expose a
#: disagreement that 1,000 nodes does not. It would only cost minutes.
SLOW_CASES = (
    [(ms640([551])[0], 1000)]                # the deepest solve under the ceiling
    + [(ms640([621])[0], 1000)]              # budget-capped, long relators
    + [(ms_unsolved([0])[0], 1000)]          # the hard Miller-Schupp reps
)

#: every field both solvers must agree on, exactly
PARITY_FIELDS = (
    "solved", "nodes_explored", "min_relator_length", "max_relator_length",
    "max_relator_length_expanded", "max_relator_expanded",
)


def _both(pres, budget, cap, cyclic):
    r1, r2 = pres.to_strs()
    kw = dict(max_relator_length=cap, cyclic_reduce=cyclic)
    return (greedy_search(r1, r2, budget, high_speedup=False, **kw),
            greedy_search(r1, r2, budget, high_speedup=True, **kw))


def _assert_parity(pres, budget, cap, cyclic):
    normal, heavy = _both(pres, budget, cap, cyclic)
    for field in PARITY_FIELDS:
        assert normal[field] == heavy[field], (
            f"{field}: normal={normal[field]!r} heavy={heavy[field]!r} "
            f"for {pres.to_strs()} budget={budget} cap={cap} cyclic={cyclic}")
    return normal, heavy


@pytest.mark.parametrize("cyclic", [True, False])
@pytest.mark.parametrize("pres,budget", FAST_CASES,
                         ids=lambda v: None if isinstance(v, int) else "p")
def test_normal_and_heavy_agree_exactly(pres, budget, cyclic):
    _assert_parity(pres, budget, 24, cyclic)


@pytest.mark.slow
@pytest.mark.parametrize("cyclic", [True, False])
@pytest.mark.parametrize("cap", [24, 48])
@pytest.mark.parametrize("pres,budget", SLOW_CASES,
                         ids=lambda v: None if isinstance(v, int) else "p")
def test_normal_and_heavy_agree_at_depth(pres, budget, cap, cyclic):
    _assert_parity(pres, budget, cap, cyclic)


def test_heavy_reports_no_path_even_when_solved():
    """The runner re-solves with the normal solver to recover it."""
    normal, heavy = _both(ms640([0])[0], 500, 24, True)
    assert normal["solved"] and heavy["solved"]
    assert normal["path_moves"] and normal["path"]
    assert heavy["path_moves"] == [] and heavy["path"] == []
    assert heavy["path_length"] is None


def test_the_length_stats_are_consistent_with_their_strings():
    """Guards against a length/string pair drifting apart in either solver."""
    for high in (False, True):
        for pres in ms640(range(0, 6)):
            s = greedy_search(*pres.to_strs(), 800, high_speedup=high)
            for length, strings in (
                ("min_relator_length", "min_relator"),
                ("max_relator_length", "max_relator"),
                ("max_relator_length_expanded", "max_relator_expanded"),
            ):
                assert s[length] == sum(len(x) for x in s[strings])


def test_min_and_max_relator_strings_are_not_a_parity_contract():
    """Pins *why* they are excluded: both are tie-broken, and the ties are real.

    If this ever stops finding a divergence, the two solvers have become
    string-identical and the exclusion above could be tightened.
    """
    diverged = set()
    for pres in ms640(range(0, 20)):
        normal, heavy = _both(pres, 1000, 24, True)
        assert normal["min_relator_length"] == heavy["min_relator_length"]
        assert normal["max_relator_length"] == heavy["max_relator_length"]
        if normal["max_relator"] != heavy["max_relator"]:
            diverged.add("max_relator")
        if normal["min_relator"] != heavy["min_relator"]:
            diverged.add("min_relator")
    assert "max_relator" in diverged, "expected tie-broken max_relator to differ"
