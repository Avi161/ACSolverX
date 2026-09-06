import pytest

from experiments.equivalence_classes.lib.words import SIGNED_PERMS, apply_pair, canon_pair, inv
from experiments.search.bs_collapse import collapse


def family(n):
    return "YxyXX", "Y" * (n + 1) + "X" + "y" * n + "x"


def replay(pair, record):
    from experiments.search.greedy_baseline import moves_to_states, str_to_move

    got = moves_to_states(*pair, [str_to_move(m) for m in record["path_moves"]])
    assert got == record["states"]
    assert record["nodes_explored"] == len(record["steps"]) + 1
    assert record["rewrites"] == len(record["steps"])
    assert record["max_intermediate_relator_length"] == max(
        len(w) for state in got for w in state)


@pytest.mark.parametrize("n", [0, 1, 2, 3, 5, 7])
def test_symbolic_conjugate_power_family_has_a_replayable_solution(n):
    pair = family(n)
    record = collapse(pair)
    assert record["solved"] and record["applicable"]
    assert record["nodes_explored"] <= 1000
    assert {w.lower() for w in record["states"][-1]} == {"x", "y"}
    replay(pair, record)


@pytest.mark.parametrize("images", [images for _, images in SIGNED_PERMS])
def test_signed_generators_rotation_inversion_and_swap(images):
    a, b = apply_pair(family(3), images)
    pair = (inv(b[2:] + b[:2]), a[1:] + a[:1])
    record = collapse(pair)
    assert record["solved"]
    replay(pair, record)


@pytest.mark.parametrize("companion", ["yxxxxYYx", "YXXyxYxx"])
def test_nonfamily_companions_use_both_pinch_directions(companion):
    pair = ("YxyXX", companion)
    record = collapse(pair)
    assert record["solved"]
    replay(pair, record)


def test_budget_failure_returns_only_the_replayable_prefix():
    pair = family(5)
    record = collapse(pair, budget=4)
    assert not record["solved"] and record["reason"] == "budget"
    assert record["nodes_explored"] == 4
    replay(pair, record)


def test_exact_budget_boundary():
    pair = family(3)
    completed = collapse(pair)
    assert collapse(pair, budget=completed["nodes_explored"])["solved"]
    limited = collapse(pair, budget=completed["nodes_explored"] - 1)
    assert not limited["solved"] and limited["reason"] == "budget"
    replay(pair, limited)


def test_cap_failure_does_not_hide_the_large_intermediate():
    pair = family(7)
    record = collapse(pair, intermediate_cap=48)
    assert not record["solved"] and record["reason"] == "intermediate_cap"
    assert record["max_intermediate_relator_length"] <= 48
    replay(pair, record)


def test_nonrecognized_input_is_not_reported_solved():
    pair = ("YXYxyx", "YYYYxxx")
    record = collapse(pair)
    assert not record["solved"] and not record["applicable"]
    assert record["reason"] == "not_recognized"
    assert record["states"] == [list(canon_pair(*pair))]
    assert record["steps"] == []


def test_terminal_input_needs_no_rewrite():
    record = collapse(("x", "Y"), budget=1)
    assert record["solved"] and record["nodes_explored"] == 1
    assert record["steps"] == []


@pytest.mark.parametrize("budget", [0, 10001, True, 1.5])
def test_invalid_budget_is_rejected(budget):
    with pytest.raises(ValueError, match="budget"):
        collapse(family(1), budget=budget)


@pytest.mark.parametrize("cap", [0, 257, True, 1.5])
def test_invalid_intermediate_cap_is_rejected(cap):
    with pytest.raises(ValueError, match="intermediate_cap"):
        collapse(family(1), intermediate_cap=cap)
