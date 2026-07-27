from experiments.stable_ac.verify_relative_free_product import (
    evaluate_relative_word,
    power_syllables,
    reduce_syllables,
    trim_base_endpoints,
)


def test_reduction_merges_factor_syllables_and_removes_identity_values():
    assert reduce_syllables(
        (("A", 2), ("A", -1), ("C", 3), ("C", -3), ("A", 1))
    ) == (("A", 2),)
    assert reduce_syllables(
        (("C", 3), ("C", 3), ("A", 2)),
        orders={"C": 5},
    ) == (("C", 1), ("A", 2))


def test_endpoint_trim_removes_only_the_two_base_factor_syllables():
    word = (("A", 2), ("C", 1), ("A", -3), ("C", -2), ("A", 4))

    assert trim_base_endpoints(word) == (
        ("A", 2),
        (("C", 1), ("A", -3), ("C", -2)),
        ("A", 4),
    )


def test_powers_keep_other_factor_endpoints_when_boundary_merge_survives():
    core = (("C", 2), ("A", 3), ("C", 5))

    assert power_syllables(core, 2) == (
        ("C", 2),
        ("A", 3),
        ("C", 7),
        ("A", 3),
        ("C", 5),
    )
    assert power_syllables(core, -1) == (
        ("C", -5),
        ("A", -3),
        ("C", -2),
    )


def test_powers_keep_other_factor_endpoints_through_nested_boundary_cancellation():
    one_layer = (("C", 2), ("A", 3), ("C", -2))
    two_layers = (
        ("C", 2),
        ("A", 3),
        ("C", 4),
        ("A", -3),
        ("C", -2),
    )

    assert power_syllables(one_layer, 3) == (
        ("C", 2),
        ("A", 9),
        ("C", -2),
    )
    assert power_syllables(one_layer, -2) == (
        ("C", 2),
        ("A", -6),
        ("C", -2),
    )
    assert power_syllables(two_layers, 2) == (
        ("C", 2),
        ("A", 3),
        ("C", 8),
        ("A", -3),
        ("C", -2),
    )


def test_alternating_relative_word_has_literal_other_base_other_seams():
    core = (("C", 2), ("A", 3), ("C", -2))
    relative_word = (
        ("A", 2),
        ("S", 2),
        ("A", -1),
        ("S", -1),
        ("A", 3),
    )

    assert evaluate_relative_word(relative_word, core) == (
        ("A", 2),
        ("C", 2),
        ("A", 6),
        ("C", -2),
        ("A", -1),
        ("C", 2),
        ("A", -3),
        ("C", -2),
        ("A", 3),
    )


def test_outside_torsion_element_has_a_relative_power_kernel():
    outside_torsion = (("C", 1),)

    assert power_syllables(outside_torsion, 1, orders={"C": 2}) == (("C", 1),)
    assert evaluate_relative_word(
        (("S", 2),),
        outside_torsion,
        orders={"C": 2},
    ) == ()


def test_infinite_untrimmed_element_can_have_a_finite_core_and_relative_kernel():
    orders = {"A": 2, "C": 2}
    infinite_untrimmed = (("A", 1), ("C", 1))

    assert power_syllables(infinite_untrimmed, 3, orders=orders) == (
        ("A", 1),
        ("C", 1),
        ("A", 1),
        ("C", 1),
        ("A", 1),
        ("C", 1),
    )
    assert trim_base_endpoints(infinite_untrimmed, orders=orders) == (
        ("A", 1),
        (("C", 1),),
        None,
    )
    assert evaluate_relative_word(
        (("A", 1), ("S", 1), ("A", 1), ("S", 1)),
        infinite_untrimmed,
        orders=orders,
    ) == ()


def test_internal_element_has_the_literal_relative_kernel():
    internal = (("A", 3),)

    assert evaluate_relative_word(
        (("S", 1), ("A", -3)),
        internal,
    ) == ()
