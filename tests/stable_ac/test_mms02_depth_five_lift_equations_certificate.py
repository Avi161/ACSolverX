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
from experiments.stable_ac.mms02_path_gauge_conjugacy_certificate import (
    decide_path_gauge_conjugacy,
    rank_three_class_two_coordinate,
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


def test_class_two_lift_system_has_the_trivial_commutator_solution():
    decision = decide_path_gauge_conjugacy()
    assert decision.class_two_source == (0, 1, 1)
    assert decision.class_two_target == (0, 1, -1)
    assert decision.class_two_forced_conjugate == decision.class_two_target
    assert decision.forced_base_conjugator == "BB"


def test_actual_class_two_quotient_is_infinite_cyclic():
    relation_a = rank_three_class_two_coordinate("xzYXyxZXYxyZ")
    relation_b = rank_three_class_two_coordinate("XyxZXYXyxzXYxy")
    assert relation_a == (1, 0, -1, 0, 0, 0)
    assert relation_b == (-1, 1, 0, 0, -1, 0)

    exponent_a = relation_a[:3]
    exponent_b = relation_b[:3]
    e_x = (1, 0, 0)
    e_y = (0, 1, 0)
    e_z = (0, 0, 1)
    determinant = (
        exponent_a[0]
        * (exponent_b[1] * e_z[2] - exponent_b[2] * e_z[1])
        - exponent_b[0]
        * (exponent_a[1] * e_z[2] - exponent_a[2] * e_z[1])
        + e_z[0]
        * (exponent_a[1] * exponent_b[2] - exponent_a[2] * exponent_b[1])
    )
    assert determinant == 1

    def wedge(left, right):
        return (
            left[0] * right[1] - left[1] * right[0],
            left[0] * right[2] - left[2] * right[0],
            left[1] * right[2] - left[2] * right[1],
        )

    xy = wedge(e_x, exponent_b)
    minus_xz = wedge(e_x, exponent_a)
    minus_xy_minus_yz = wedge(e_y, exponent_a)
    assert xy == (1, 0, 0)
    assert minus_xz == (0, -1, 0)
    assert tuple(
        -(minus_xy_minus_yz[index] + xy[index]) for index in range(3)
    ) == (0, 0, 1)
