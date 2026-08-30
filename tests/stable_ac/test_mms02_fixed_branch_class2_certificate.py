from experiments.stable_ac.mms02_fixed_branch_class2_certificate import (
    EXPECTED_A_WEDGE,
    EXPECTED_B_WEDGE,
    EXPECTED_D_VECTOR,
    EXPECTED_D_WEDGE,
    EXPECTED_RESIDUAL,
    EXPECTED_T_VECTOR,
    decide_fixed_branch_class_two,
)


def reduce_word(word: str) -> str:
    stack = []
    for letter in word:
        if stack and stack[-1] == letter.swapcase():
            stack.pop()
        else:
            stack.append(letter)
    return "".join(stack)


def test_fixed_commutator_substitutions_solve_the_second_equation() -> None:
    commutator_u_v = "uvUV"
    commutator_v_u_inverse = "vUVu"
    conjugated = "U" + commutator_u_v + "u"
    assert reduce_word(commutator_v_u_inverse) == reduce_word(conjugated)


def test_canonical_branch_has_an_integral_class_two_obstruction() -> None:
    decision = decide_fixed_branch_class_two()
    assert decision.endpoint_wedges == (EXPECTED_A_WEDGE, EXPECTED_B_WEDGE)
    assert decision.twisted_source_vector == EXPECTED_D_VECTOR
    assert decision.twisted_source_wedge == EXPECTED_D_WEDGE
    assert decision.forced_conjugator_vector == EXPECTED_T_VECTOR
    assert decision.central_residual == EXPECTED_RESIDUAL
    assert decision.image_invariant_values == (0, 0, 0, 0, 0, 0)
    assert decision.residual_invariant == 8
    assert (
        decision.verdict
        == "CANONICAL_G_V_H_X_J_U_INVERSE_BRANCH_OBSTRUCTED_IN_BASE_CLASS_TWO"
    )
