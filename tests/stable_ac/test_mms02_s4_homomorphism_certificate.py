from experiments.stable_ac.mms02_s4_homomorphism_certificate import (
    collapsed_homomorphisms,
    collapsed_pairs,
    decide_s4_homomorphisms,
    original_homomorphisms,
    power,
)


def test_original_and_collapsed_s4_censuses_agree() -> None:
    pairs = collapsed_pairs()
    collapsed = collapsed_homomorphisms()
    original = original_homomorphisms()
    assert len(pairs) == 24
    assert all(z_image == power(y_image, 3) for y_image, z_image in pairs)
    assert len(collapsed) == len(pairs)
    assert collapsed == original
    assert len(original) == 24
    assert all(x_image == y_image == z_image for x_image, y_image, z_image in original)


def test_every_s4_homomorphism_is_cyclic() -> None:
    decision = decide_s4_homomorphisms()
    assert decision.collapsed_candidate_count == 576
    assert decision.original_candidate_count == 13_824
    assert decision.image_order_histogram == ((1, 1), (2, 9), (3, 8), (4, 6))
    assert decision.cyclic_specialization_count == 24
    assert decision.noncyclic_specialization_count == 0
    assert decision.epimorphism_count == 0
    assert (
        decision.verdict
        == "EVERY_G_MINUS_TO_S4_HOMOMORPHISM_FACTORS_THROUGH_ABELIANIZATION"
    )
