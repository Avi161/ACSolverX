from experiments.stable_ac.mms02_depth_five_lift_equations_certificate import (
    EXPECTED_COLLAPSED_ENDPOINTS,
    EXPECTED_COLLAPSED_GENERATORS,
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
