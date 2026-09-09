"""Raising the budget ceiling must move exactly one thing: stage 4's allowance.

Stages 1-3 are capped by their own constants, and ``mixed_search`` pops in a
deterministic priority order, so a bigger budget has to reproduce a smaller
run exactly and then continue. If that ever stops being true, a 10M cascade
run is a different search from the 100k one and the archive no longer
brackets it.
"""
import pytest

from experiments.search import cascade_heuristics as ch
from experiments.search.run_ac19_cascade_screen import MAX_BUDGET, search_row

# An orbit the cascade does not settle quickly, so stage 4 actually runs.
PAIR = ("YYXXXYx", "YYxyxyXyXyx")
CAP = 48          # cheap: maxc is 4*(cap+1)^2 scratch per pop
SMALL, BIG = 1_500, 5_000


def stages(result):
    return {a["component"]: a for a in result["attempts"]}


def test_shipped_default_is_unchanged():
    assert ch.MAX_BUDGET == MAX_BUDGET == 100_000
    with pytest.raises(ValueError):
        ch.search(PAIR, budget=100_001, cap=CAP)


def test_max_budget_must_be_a_positive_int():
    for bad in (0, -1, True, 1.5, "10"):
        with pytest.raises(ValueError):
            ch.search(PAIR, budget=10, cap=CAP, max_budget=bad)


def test_raising_the_ceiling_alone_changes_nothing():
    """Same budget, higher ceiling -> byte-identical result."""
    a = ch.search(PAIR, budget=BIG, cap=CAP, starter_budget=500)
    b = ch.search(PAIR, budget=BIG, cap=CAP, starter_budget=500,
                  max_budget=10_000_000)
    assert a == b


def test_bigger_budget_reproduces_the_smaller_run_in_stages_1_to_3():
    small = ch.search(PAIR, budget=SMALL, cap=CAP, starter_budget=500)
    big = ch.search(PAIR, budget=BIG, cap=CAP, starter_budget=500,
                    max_budget=10_000_000)
    s, b = stages(small), stages(big)
    for stage in ("normalization", "rewrite", "s40_gen"):
        assert s.get(stage) == b.get(stage), stage
    # ... and only stage 4 grows.
    assert b["s20_mk2"]["nodes"] > s["s20_mk2"]["nodes"]
    assert big["nodes_explored"] > small["nodes_explored"]


def test_stage_4_allowance_is_budget_minus_the_fixed_prefix():
    for budget in (SMALL, BIG):
        r = ch.search(PAIR, budget=budget, cap=CAP, starter_budget=500,
                      max_budget=10_000_000)
        st = stages(r)
        prefix = st["normalization"]["nodes"] + st["rewrite"]["nodes"] \
            + st["s40_gen"]["nodes"]
        assert prefix == 501, prefix          # stages 1-3, budget-independent
        assert st["s20_mk2"]["nodes"] <= budget - prefix


def test_runner_threads_the_ceiling_through():
    """The runner accepts a budget past its own MAX_BUDGET only when told to."""
    # A row the rewrite stage settles in a handful of nodes, so the huge
    # ceiling costs nothing to exercise: the budget is the cap, not the work.
    easy = ("X", "YYXyx")
    with pytest.raises(ValueError):
        search_row(easy, budget=MAX_BUDGET + 1)
    r = search_row(easy, budget=MAX_BUDGET + 1, starter_budget=500,
                   max_budget=10_000_000)
    assert r["solved"] and r["nodes_explored"] < 100
