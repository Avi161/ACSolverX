from experiments.equivalence_classes.lib.autcanon import aut_min_len
from experiments.stable_ac.mms02_terminal_base_pair_certificate import (
    EXPECTED_D,
    EXPECTED_D_MINIMUM,
    EXPECTED_E_REWRITE,
    EXPECTED_MINIMUM,
    EXPECTED_T_REWRITE,
    EXPECTED_U,
    EXPECTED_V,
    decide_terminal_base_pair,
    theta,
    to_xy,
)
from experiments.stable_ac.mms02_terminal_twisted_coboundary_certificate import (
    Q_WORD,
)


def test_terminal_killer_stably_eliminates_to_the_pinned_base_pair():
    decision = decide_terminal_base_pair()
    assert decision.target_rewrite == EXPECTED_T_REWRITE
    assert decision.killer_rewrite == EXPECTED_E_REWRITE
    assert decision.target_rewrite[-1] == "qPqxQXp"
    assert decision.killer_rewrite[-1].endswith("x")
    assert decision.expanded_rows[0] == "xpXQ"
    assert decision.expanded_rows[1] == "xqXQpQP"
    assert decision.expanded_rows[2].endswith("x")
    assert decision.ambient_images[:2] == ("p", "q")
    assert decision.base_pair == (EXPECTED_U, EXPECTED_V)
    assert decision.base_lengths == (54, 51)


def test_terminal_base_pair_has_two_independent_floor_104_checks():
    decision = decide_terminal_base_pair()
    assert decision.base_minimum == EXPECTED_MINIMUM
    assert decision.base_floor == 104
    assert decision.base_descent == (("xy", "y"),)
    assert aut_min_len(tuple(to_xy(word) for word in decision.base_pair)) == 104
    assert decision.verdict == "TARGET_STABLE_BASE_PAIR_FLOOR_104"


def test_terminal_cocycle_consequence_is_nonprimitive_not_a_donor():
    decision = decide_terminal_base_pair()
    assert theta(Q_WORD) == EXPECTED_D == decision.consequence
    assert decision.consequence_minimum == EXPECTED_D_MINIMUM
    assert decision.consequence_floor == 16
    duplicate = (to_xy(decision.consequence), to_xy(decision.consequence))
    assert aut_min_len(duplicate) == 32
