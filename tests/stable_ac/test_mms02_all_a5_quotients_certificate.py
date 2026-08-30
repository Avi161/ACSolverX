from experiments.stable_ac.mms02_all_a5_quotients_certificate import (
    canonical_epimorphism,
    collapsed_epimorphisms,
    decide_all_a5_quotients,
    three_generator_epimorphisms,
)


def test_two_presentations_give_the_same_complete_epimorphism_set() -> None:
    direct = three_generator_epimorphisms()
    collapsed = collapsed_epimorphisms()
    assert direct == collapsed
    assert len(direct) == 120
    assert len({canonical_epimorphism(triple) for triple in direct}) == 1


def test_complete_a5_lift_predicate_is_solvable() -> None:
    decision = decide_all_a5_quotients()
    assert decision.automorphism_orbit_sizes == (120,)
    assert decision.source_commutator_value_count == 12
    assert decision.target_commutator_value_count == 12
    assert decision.compatible_commutator_count == 12
    assert decision.successful_commutator_product_count == 105
    assert decision.verdict == "EVERY_A5_QUOTIENT_SOLVES_THE_SIGNED_LIFT_GATE"
