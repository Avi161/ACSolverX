from experiments.stable_ac.mms02_depth_five_lift_equations_certificate import (
    EXPECTED_D2_WORD,
    EXPECTED_COLLAPSED_ENDPOINTS,
    EXPECTED_COLLAPSED_GENERATORS,
    EXPECTED_ENDPOINT_BASE_WORDS,
    EXPECTED_MAGNUS_RELATOR,
    EXPECTED_ENDPOINT_BASE_VECTORS,
    EXPECTED_M_MINUS_I_INVERSE,
    EXPECTED_MONODROMY_MATRIX,
    FORWARD,
    R_STAR,
    apply_images,
    decide_lift_equation_coordinates,
    exponent_vector,
)


def test_tietze_map_pins_every_collapsed_original_generator():
    decision = decide_lift_equation_coordinates()
    assert decision.collapsed_generators == EXPECTED_COLLAPSED_GENERATORS
    assert decision.collapsed_generators == (
        "zyZ",
        "y",
        "zYZYzYzYZyzyZ",
    )
    assert apply_images("XyxZXYXyxzXYxy", FORWARD) == "x"


def test_depth_five_lift_equation_endpoints_are_literal():
    decision = decide_lift_equation_coordinates()
    assert decision.collapsed_endpoints == EXPECTED_COLLAPSED_ENDPOINTS
    assert decision.collapsed_endpoints == (
        "zyZyzYZYzyZyZyzyZ",
        "zYZyzYZYzYzYZyzyZ",
    )


def test_magnus_exponent_vector_is_pinned_without_module_calculus():
    decision = decide_lift_equation_coordinates()
    assert len(R_STAR) == 26
    assert exponent_vector(R_STAR) == (-3, 1)
    assert decision.relator_exponent_vector == (-3, 1)
    assert decision.verdict == "EXACT_DEPTH_FIVE_LIFT_EQUATION_COORDINATES_PINNED"


def test_magnus_relator_has_two_unique_extremes_and_free_base_elimination():
    decision = decide_lift_equation_coordinates()
    assert decision.magnus_relator == EXPECTED_MAGNUS_RELATOR
    assert decision.magnus_relator.count((-2, 1)) == 1
    assert decision.magnus_relator.count((2, 1)) == 1
    assert decision.d2_word == EXPECTED_D2_WORD
    assert decision.d2_word.count((-2, -1)) == 1


def test_terminal_words_have_pinned_length_one_hnn_normalizations():
    decision = decide_lift_equation_coordinates()
    assert decision.endpoint_base_words == EXPECTED_ENDPOINT_BASE_WORDS
    assert tuple(map(len, decision.endpoint_base_words)) == (10, 10)
    assert all(
        all(-2 <= index <= 1 for index, _ in word)
        for word in decision.endpoint_base_words
    )


def test_base_abelianization_is_a_vacuous_lift_shadow():
    decision = decide_lift_equation_coordinates()
    assert decision.monodromy_matrix == EXPECTED_MONODROMY_MATRIX
    assert decision.m_minus_i_inverse == EXPECTED_M_MINUS_I_INVERSE
    assert decision.endpoint_base_vectors == EXPECTED_ENDPOINT_BASE_VECTORS
    assert decision.endpoint_base_vectors[1] == tuple(
        -value for value in decision.endpoint_base_vectors[0]
    )
