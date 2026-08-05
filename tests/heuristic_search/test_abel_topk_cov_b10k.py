"""Unit tests for abelianized-magnitude top-K CoV selection (0 search nodes).

The runner reads a frozen sweep and runs no search, so what needs pinning is the
*key* and the *ranking semantics* — a drift in either silently moves the headline.
"""
from __future__ import annotations

import pytest

from experiments.heuristic_search.runners.abel_topk_cov_b10k import (
    abel_magnitude,
    cumulative_nodes,
    exponent_sums,
    rank,
    solves_within,
    KEYS,
)


def _cand(r1, r2, solved, nodes, z="z", iso="x", idx=0):
    return {"r1": r1, "r2": r2, "solved": solved, "nodes_explored": nodes,
            "z_word": z, "iso_gen": iso, "iso_index": idx}


# ------------------------------------------------------------------ the key

@pytest.mark.parametrize("rel,expected", [
    ("", (0, 0)),
    ("x", (1, 0)),
    ("X", (-1, 0)),
    ("xX", (0, 0)),          # freely trivial: exponent sums cancel
    ("YYXyx", (0, -1)),
    ("Yx", (1, -1)),
])
def test_exponent_sums(rel, expected):
    assert exponent_sums(rel) == expected


def test_abel_magnitude_matches_restart_planner_definition():
    """|Sx| + |Sy| over both relators — the same quantity restart_planner ranks by."""
    assert abel_magnitude("YYXyx", "Yx") == 0 + 1 + 1 + 1


def test_abel_magnitude_is_absolute_not_signed():
    """A cancelling pair must NOT come out at 0 — the key sums magnitudes per relator."""
    assert abel_magnitude("x", "X") == 2
    assert abel_magnitude("xy", "XY") == 4


def test_abel_magnitude_is_order_and_rotation_blind():
    """Only exponent sums enter, so a cyclic rotation cannot move the key."""
    assert abel_magnitude("xyX", "y") == abel_magnitude("yXx", "y")


def test_abel_magnitude_never_reads_the_search():
    """The key takes two strings; a search-derived field cannot reach it."""
    d = _cand("xxY", "yX", solved=True, nodes=1)
    d["min_relator"] = ["ignored"]          # search-derived; must not matter
    assert abel_magnitude(d["r1"], d["r2"]) == abel_magnitude("xxY", "yX")


# -------------------------------------------------------------- the ranking

def test_ident_tie_break_is_deterministic():
    a = _cand("xy", "xy", True, 5, z="b")
    b = _cand("xy", "xy", False, 5, z="a")
    key = KEYS["abel"]
    assert [d["z_word"] for d in rank([a, b], key)] == ["a", "b"]
    assert [d["z_word"] for d in rank([b, a], key)] == ["a", "b"]


def test_adversarial_and_optimistic_bracket_the_tie():
    """Same key value, one solver and one not: the two tie modes must disagree at K=1."""
    solver = _cand("xy", "xy", True, 5, z="b")
    dud = _cand("xy", "xy", False, 10_000, z="a")
    key = KEYS["abel"]
    assert not solves_within(rank([solver, dud], key, "adversarial"), 1)
    assert solves_within(rank([solver, dud], key, "optimistic"), 1)
    # and K=2 closes the bracket — the point of quoting a K > 1
    assert solves_within(rank([solver, dud], key, "adversarial"), 2)


def test_lower_abel_ranks_first():
    lo = _cand("xX", "yY", True, 1, z="hi")     # abel 0
    hi = _cand("xx", "yy", True, 1, z="lo")     # abel 4
    assert rank([hi, lo], KEYS["abel"])[0] is lo


def test_abel_len_lex_breaks_an_abel_tie_by_length():
    short = _cand("x", "y", True, 1, z="b")
    long = _cand("xXx", "yYy", True, 1, z="a")  # same abel, longer start
    assert rank([long, short], KEYS["abel_len_lex"])[0] is short
    # the bare key would have taken the identity tie-break instead
    assert rank([long, short], KEYS["abel"])[0] is long


def test_len_only_control_ignores_abel():
    short_high_abel = _cand("xx", "yy", True, 1, z="b")   # abel 4, len 4
    long_low_abel = _cand("xXxX", "yYyY", True, 1, z="a")  # abel 0, len 8
    assert rank([long_low_abel, short_high_abel], KEYS["len_only"])[0] is short_high_abel


# ----------------------------------------------------------------- the cost

def test_cumulative_nodes_charges_every_failed_try():
    duds = [_cand("xy", "xy", False, 10_000, z=c) for c in "ab"]
    win = _cand("xy", "xy", True, 42, z="c")
    assert cumulative_nodes(duds + [win], 3) == 20_042


def test_cumulative_nodes_stops_at_the_first_solve():
    win = _cand("xy", "xy", True, 42, z="a")
    after = _cand("xy", "xy", True, 1, z="b")
    assert cumulative_nodes([win, after], 3) == 42


def test_cumulative_nodes_is_none_when_nothing_solves():
    duds = [_cand("xy", "xy", False, 10_000, z=c) for c in "abc"]
    assert cumulative_nodes(duds, 3) is None


def test_solves_within_respects_k():
    duds = [_cand("xy", "xy", False, 10_000, z=c) for c in "ab"]
    win = _cand("xy", "xy", True, 1, z="c")
    ordered = duds + [win]
    assert not solves_within(ordered, 2)
    assert solves_within(ordered, 3)
