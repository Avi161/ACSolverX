from experiments.stable_ac.mms02_terminal_target_hnn_certificate import (
    apply_images,
)
from experiments.stable_ac.mms02_terminal_twisted_coboundary_certificate import (
    EXPECTED_C_P,
    EXPECTED_C_Q,
    EXPECTED_R,
    P_WORD,
    Q_WORD,
    abelianization,
    decide_twisted_coboundary,
    l_coefficient,
)


def test_terminal_hnn_descent_is_literal_and_stops_in_the_base():
    decision = decide_twisted_coboundary()
    assert apply_images(Q_WORD, {"p": "q", "q": "pqPq"}) == P_WORD
    assert decision.p_abelianization == (0, 7)
    assert decision.q_abelianization == (-1, 4)
    assert abelianization(Q_WORD)[0] == -1


def test_terminal_hnn_fox_specializations_and_rhs_are_pinned():
    decision = decide_twisted_coboundary()
    assert decision.c_p == EXPECTED_C_P
    assert decision.c_q == EXPECTED_C_Q
    assert decision.rhs == EXPECTED_R
    assert sum(coefficient for _, coefficient in decision.rhs) == -7
    assert decision.rhs[0][0] == 4
    assert decision.rhs[-1] == (52, 1)


def test_terminal_hnn_mahler_coefficients_have_exact_degree_six_conflict():
    decision = decide_twisted_coboundary()
    coefficients = dict(decision.forced_coefficients)
    assert coefficients == {
        2: 2,
        3: 0,
        4: 0,
        5: 1,
        6: 1,
        7: 0,
        8: 0,
        9: 1,
        10: 0,
        11: 1,
        12: 1,
    }
    rhs = dict(decision.rhs)
    for degree in (52, 48, 44, 40, 36, 32, 28, 24, 20, 16, 12):
        assert l_coefficient(coefficients, degree) == rhs.get(degree, 0)
    assert decision.contradiction_degree == 6
    assert l_coefficient(coefficients, 6) == 1 - 2 == -1
    assert rhs.get(6, 0) == 0
    assert decision.verdict == "NO_TERMINAL_HNN_BASE_CONJUGATOR"
