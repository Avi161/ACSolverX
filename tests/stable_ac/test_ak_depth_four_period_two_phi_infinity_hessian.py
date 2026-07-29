from collections import Counter

from experiments.stable_ac import depth4_period_two_lift_certificate as lift
from experiments.stable_ac import depth4_period_two_degree_two_escape_certificate as escape
from experiments.stable_ac import depth4_period_two_tree_flow_factorization_certificate as tree


PINNED_OCCURRENCES = (
    (2, 1, ""),
    (1, 1, "tc"),
    (0, 1, "tc"),
    (0, -1, "ctcTTTcttc"),
    (1, -1, "ctcTctt"),
    (2, -1, "ctcTcTctc"),
    (0, 1, "ctcTcTctc"),
    (0, -1, "ctcTTTTcttc"),
    (3, 1, "ctcTTctt"),
    (1, 1, "ctcTctc"),
    (0, 1, "ctcTctc"),
    (0, -1, "cTTcttc"),
    (1, -1, "tt"),
    (3, -1, "t"),
    (4, 1, "t"),
    (4, -1, ""),
)


def test_residual_occurrences_match_the_independent_literal_table() -> None:
    from experiments.stable_ac.depth4_period_two_phi_infinity_hessian_certificate import (
        residual_occurrences,
    )

    occurrences = residual_occurrences()
    actual = tuple(
        (occurrence.slot, occurrence.polarity, lift.literal(occurrence.quotient_prefix))
        for occurrence in occurrences
    )
    assert actual == PINNED_OCCURRENCES
    assert tuple(Counter(occurrence.slot for occurrence in occurrences)[slot] for slot in range(5)) == (
        6,
        4,
        2,
        2,
        2,
    )


def test_signed_occurrence_prefixes_reproduce_every_operator() -> None:
    from experiments.stable_ac.depth4_period_two_phi_infinity_hessian_certificate import (
        occurrence_operator,
    )

    r = lift.multiply(lift.SOURCE_A, lift.conjugate(lift.inverse(lift.SOURCE_B), lift.H0))
    s = lift.multiply(lift.SOURCE_B, lift.conjugate(lift.inverse(r), lift.H1))
    u = lift.multiply(r, lift.conjugate(lift.inverse(s), lift.H2))
    expected = lift.build_operators(r, s, u)
    assert tuple(occurrence_operator(slot) for slot in range(5)) == expected


def test_positive_and_negative_section_jets_have_opposite_orientations() -> None:
    from experiments.stable_ac.depth4_period_two_phi_infinity_hessian_certificate import (
        gamma_negative,
        gamma_positive,
    )

    identity = lift.parse_quotient("")
    t_vertex = lift.parse_quotient("t")
    left = {identity: 2, t_vertex: -1}
    right = {identity: 3, t_vertex: 4}
    assert gamma_positive(left, right) == {
        (identity, identity): 6,
        (identity, t_vertex): 5,
        (t_vertex, t_vertex): -4,
    }
    assert gamma_negative(left, right) == {
        (identity, identity): 6,
        (t_vertex, identity): 5,
        (t_vertex, t_vertex): -4,
    }


def test_raw_commutator_tensor_retains_the_translated_diagonal_pair() -> None:
    from experiments.stable_ac.depth4_period_two_phi_infinity_hessian_certificate import (
        raw_tensor_from_kernel_word,
    )

    identity = lift.parse_quotient("")
    t_vertex = lift.parse_quotient("t")
    doubled_lift = lift.power_word(lift.relation_generator(identity), 2)
    commutator = lift.multiply(
        doubled_lift,
        lift.TARGET,
        lift.inverse(doubled_lift),
        lift.inverse(lift.TARGET),
    )
    assert lift.quotient_reduce(commutator) == ()
    kernel_word = escape.schreier_word(commutator)
    assert kernel_word == (
        (identity, 1),
        (identity, 1),
        (t_vertex, -1),
        (t_vertex, -1),
    )
    tensor = raw_tensor_from_kernel_word(kernel_word)
    assert tensor == {
        (identity, identity): 1,
        (identity, t_vertex): -4,
        (t_vertex, t_vertex): 3,
    }
    mod_two_support = {pair for pair, coefficient in tensor.items() if coefficient % 2}
    assert mod_two_support == {
        (identity, identity),
        (t_vertex, t_vertex),
    }
    mod_two_exterior = {
        pair
        for pair, coefficient in tensor.items()
        if pair[0] != pair[1] and coefficient % 2
    }
    assert mod_two_exterior == set()


def _combine_tensors(*terms):
    result = Counter()
    for coefficient, tensor in terms:
        for key, value in tensor.items():
            result[key] += coefficient * value
    return {key: value for key, value in result.items() if value}


def _raw_residual_tensor(variables):
    from experiments.stable_ac.depth4_period_two_phi_infinity_hessian_certificate import (
        raw_tensor_from_kernel_word,
    )

    residual = escape.corrected_residual(variables)
    return raw_tensor_from_kernel_word(escape.schreier_word(residual))


def test_symbolic_mixed_tensor_matches_the_independent_four_corner_oracle() -> None:
    from experiments.stable_ac.depth4_period_two_phi_infinity_hessian_certificate import (
        symbolic_mixed_subtotals,
        symbolic_mixed_tensor,
        symbolic_mixed_wedge,
    )

    base = escape.variables_from_entries(lift.CORRECTION)
    alternate_10 = escape.variables_from_entries(escape.ALTERNATE_10)
    alternate_01 = escape.variables_from_entries(escape.ALTERNATE_01)
    left = escape.subtract_variables(alternate_10, base)
    right = escape.subtract_variables(alternate_01, base)
    alternate_11 = escape.add_variables(base, left, right)
    direct = _combine_tensors(
        (1, _raw_residual_tensor(alternate_11)),
        (-1, _raw_residual_tensor(alternate_10)),
        (-1, _raw_residual_tensor(alternate_01)),
        (1, _raw_residual_tensor(base)),
    )
    symbolic = symbolic_mixed_tensor(left, right)
    assert symbolic == direct
    assert all(coefficient == 0 for (left_vertex, right_vertex), coefficient in symbolic.items() if left_vertex == right_vertex)
    for (left_vertex, right_vertex), coefficient in symbolic.items():
        assert symbolic.get((right_vertex, left_vertex), 0) == -coefficient
    expected_wedge = {
        pair: coefficient
        for pair, coefficient in direct.items()
        if (len(pair[0]), pair[0]) < (len(pair[1]), pair[1]) and coefficient
    }
    assert symbolic_mixed_wedge(left, right) == expected_wedge
    subtotals = symbolic_mixed_subtotals(left, right)
    reconstructed = _combine_tensors(
        (1, subtotals.positive_internal),
        (1, subtotals.negative_internal),
        (1, subtotals.external),
        (1, subtotals.propagated_diagonal),
    )
    assert reconstructed == symbolic
    assert all(left_vertex == right_vertex for left_vertex, right_vertex in subtotals.propagated_diagonal)
    assert all(left_vertex != right_vertex for left_vertex, right_vertex in subtotals.positive_internal)
    assert all(left_vertex != right_vertex for left_vertex, right_vertex in subtotals.negative_internal)


def test_mixed_tensor_rejects_nonhomogeneous_directions() -> None:
    import pytest

    from experiments.stable_ac.depth4_period_two_phi_infinity_hessian_certificate import (
        symbolic_mixed_tensor,
    )

    zero = ({}, {}, {}, {}, {})
    nonhomogeneous = ({(): 1}, {}, {}, {}, {})
    with pytest.raises(AssertionError, match="homogeneous correction direction"):
        symbolic_mixed_tensor(nonhomogeneous, zero)


def test_symbolic_base_unary_and_all_syndrome_bits_match_direct_fixtures() -> None:
    from experiments.stable_ac.depth4_period_two_phi_infinity_hessian_certificate import (
        symbolic_residual_tensor,
        symbolic_syndrome,
        symbolic_unary_tensor,
    )

    zero = ({}, {}, {}, {}, {})
    x = tree.anchored_direction(lift.parse_quotient("TT"))
    y = tree.anchored_direction(lift.parse_quotient("TTTct"))
    base = escape.variables_from_entries(lift.CORRECTION)
    base_x = escape.add_variables(base, x)
    base_y = escape.add_variables(base, y)
    direct_base = _raw_residual_tensor(base)
    direct_x = _raw_residual_tensor(base_x)
    direct_y = _raw_residual_tensor(base_y)
    assert symbolic_residual_tensor(zero) == direct_base
    assert symbolic_residual_tensor(x) == direct_x
    assert symbolic_residual_tensor(y) == direct_y
    assert symbolic_unary_tensor(x) == _combine_tensors((1, direct_x), (-1, direct_base))
    assert symbolic_unary_tensor(y) == _combine_tensors((1, direct_y), (-1, direct_base))
    assert symbolic_syndrome(zero) == tuple(int(bit) for bit in "111010110101011")
    assert symbolic_syndrome(x) == tree.syndrome(x)
    assert symbolic_syndrome(y) == tree.syndrome(y)
    assert symbolic_syndrome(tree.add_directions(x, y)) == tuple(
        int(bit) for bit in "000000000000001"
    )


def test_symbolic_paths_do_not_call_long_residual_or_raw_oracles(monkeypatch) -> None:
    from experiments.stable_ac import depth4_period_two_phi_infinity_hessian_certificate as hessian

    zero = ({}, {}, {}, {}, {})

    def forbidden(*_args, **_kwargs):
        raise AssertionError("direct oracle called from symbolic path")

    monkeypatch.setattr(escape, "corrected_residual", forbidden)
    monkeypatch.setattr(escape, "schreier_word", forbidden)
    monkeypatch.setattr(hessian, "raw_tensor_from_kernel_word", forbidden)
    monkeypatch.setattr(hessian, "_expand", forbidden)
    assert hessian.symbolic_syndrome(zero) == tuple(int(bit) for bit in "111010110101011")


def test_phi_infinity_hessian_matches_cross_biadditivity_and_self_fixtures() -> None:
    from experiments.stable_ac.depth4_period_two_phi_infinity_hessian_certificate import (
        phi_infinity_hessian,
    )

    x = tree.anchored_direction(lift.parse_quotient("TT"))
    y = tree.anchored_direction(lift.parse_quotient("TTTct"))
    z = tree.anchored_direction(lift.parse_quotient("Tctt"))
    assert phi_infinity_hessian(x, y) == tree.polarization(x, y)[-1]
    assert phi_infinity_hessian(tree.add_directions(x, y), z) == (
        tree.polarization(x, z)[-1] ^ tree.polarization(y, z)[-1]
    )
    assert all(
        phi_infinity_hessian(direction, direction) == 0
        for direction in (x, y, z, tree.add_directions(x, y))
    )


def test_pair_value_interfaces_match_balanced_source_flow_and_fail_closed() -> None:
    from experiments.stable_ac.depth4_period_two_phi_infinity_hessian_certificate import (
        anchored_pair_value,
        diagonal_left_pair_value,
        symbolic_syndrome,
    )
    from experiments.stable_ac import depth4_period_two_source_flow_certificate as source

    left = lift.parse_quotient("TT")
    right = lift.parse_quotient("TTTct")
    direct = source.build_l0_direction({left: 1, right: 1}).variables
    assert anchored_pair_value(left, right, 1) == (1, symbolic_syndrome(direct))
    assert anchored_pair_value(lift.parse_quotient(""), lift.parse_quotient("T"), 1) == (
        0,
        (0,) * 15,
    )
    context = lift.quotient_reduce((lift.T,))
    translated_left = lift.c_vertex(lift.quotient_multiply(context, left))
    translated_right = lift.c_vertex(lift.quotient_multiply(context, right))
    assert diagonal_left_pair_value(context, left, right, 1) == anchored_pair_value(
        translated_left,
        translated_right,
        1,
    )


def test_kernel_normal_form_and_certificate_pin_exact_subtotals() -> None:
    from experiments.stable_ac.depth4_period_two_phi_infinity_hessian_certificate import (
        kernel_normal_form,
        phi_infinity_hessian_certificate,
    )

    normal_form = kernel_normal_form()
    assert normal_form.occurrence_count == 16
    assert normal_form.slot_counts == (6, 4, 2, 2, 2)
    assert normal_form.positive_internal_terms == 8
    assert normal_form.negative_internal_terms == 8
    assert normal_form.external_pair_terms == 120
    assert normal_form.propagated_diagonal_terms == 16
    assert normal_form.coefficient_sha256 == "854992f8a84a26ede55b22cd6a6a413c706101170766b59a33ea6c86b596a9a8"

    certificate = phi_infinity_hessian_certificate()
    assert certificate.normal_form == normal_form
    assert certificate.operator_matches == (True,) * 5
    assert certificate.raw_commutator_tensor == (
        ("", "", 1),
        ("", "t", -4),
        ("t", "t", 3),
    )
    assert certificate.raw_commutator_mod_two_diagonal_labels == ("", "t")
    assert certificate.raw_commutator_exterior_zero
    assert certificate.alternate_mixed_raw_matches
    assert certificate.base_raw_matches
    assert certificate.unary_raw_matches == (True, True)
    assert certificate.syndrome_matches == (True, True, True, True)
    assert certificate.bounded_base_syndrome == "111010110101011"
    assert certificate.bounded_unary_syndromes == (
        "110101011011001",
        "101111111110111",
    )
    assert certificate.bounded_cross_syndrome == "100000010000100"
    assert certificate.bounded_biadditivity == "100000001000100"
    assert certificate.bounded_zero_self_polarizations == 4


def test_anchored_normal_form_pins_every_active_and_internal_kernel() -> None:
    from experiments.stable_ac.depth4_period_two_phi_infinity_hessian_certificate import (
        active_anchored_occurrences,
        anchored_kernel_normal_form,
        external_order_kernels,
        internal_equality_kernels,
        internal_inversion_kernels,
    )

    active = active_anchored_occurrences()
    assert tuple(
        (
            record.active_order,
            record.residual_order,
            record.slot,
            record.polarity,
            lift.literal(record.action),
        )
        for record in active
    ) == (
        (1, 1, 2, 1, ""),
        (2, 3, 0, 1, "tc"),
        (3, 4, 0, -1, "ctcTTTcttc"),
        (4, 6, 2, -1, "ctcTcTctc"),
        (5, 7, 0, 1, "ctcTcTctc"),
        (6, 8, 0, -1, "ctcTTTTcttc"),
        (7, 9, 3, 1, "ctcTTctt"),
        (8, 11, 0, 1, "ctcTctc"),
        (9, 12, 0, -1, "cTTcttc"),
        (10, 14, 3, -1, "t"),
        (11, 15, 4, 1, "t"),
        (12, 16, 4, -1, ""),
    )

    equality = internal_equality_kernels()
    assert tuple(
        (
            record.slot,
            record.negative_active_orders,
            record.integral_multiplicity,
            record.mod_two_coefficient,
        )
        for record in equality
    ) == (
        (0, (3, 6, 9), 3, 1),
        (2, (4,), 1, 1),
        (3, (10,), 1, 1),
        (4, (12,), 1, 1),
    )

    inversion = internal_inversion_kernels()
    assert tuple(
        (
            record.slot,
            record.positive_active_order,
            record.negative_active_order,
            lift.literal(record.base_action),
            lift.literal(record.paired_action),
            lift.literal(record.multiplier),
            record.mod_two_coefficient,
        )
        for record in inversion
    ) == (
        (0, 2, 3, "tc", "ctcTTTcttc", "ctcTTTct", 1),
        (
            0,
            5,
            6,
            "ctcTcTctc",
            "ctcTTTTcttc",
            "ctcTTTTctctctcTc",
            1,
        ),
        (0, 8, 9, "ctcTctc", "cTTcttc", "cTTctctcTc", 1),
        (2, 1, 4, "", "ctcTcTctc", "ctcTcTctc", 1),
        (3, 7, 10, "ctcTTctt", "t", "TcttcTc", 1),
        (4, 11, 12, "t", "", "T", 1),
    )
    assert inversion[-1].slot == 4
    assert inversion[-1].mod_two_coefficient == 1

    external = external_order_kernels()
    assert len(external) == 66
    assert Counter(record.integral_coefficient for record in external) == {
        -1: 36,
        1: 30,
    }
    assert all(record.mod_two_coefficient == 1 for record in external)
    keys = tuple(record.ordered_type_key for record in external)
    assert len(set(keys)) == 66
    assert not any(record.transpose_type_key in set(keys) for record in external)

    normal_form = anchored_kernel_normal_form()
    assert normal_form.active_occurrence_count == 12
    assert normal_form.active_slot_counts == (6, 0, 2, 2, 2)
    assert normal_form.equality_terms == 4
    assert normal_form.inversion_terms == 6
    assert normal_form.external_pair_terms == 66
    assert normal_form.external_oriented_monomials == 132
    assert normal_form.duplicate_external_keys == 0
    assert normal_form.generic_transpose_pairs == 0
    assert normal_form.slot4_t_inversion_coefficient == 1
    assert normal_form.slot_one_zero_on_anchored_directions
    assert normal_form.external_reversal_from_homogeneity
    assert normal_form.pullback_uses_unique_linear_tree_flow
    assert normal_form.coefficient_sha256 == (
        "c044b3d7d3dbeb430f8d27c89f69d85aeedbf058363892e2b19acc4c4aaefdef"
    )


def test_anchored_kernel_subtotals_reconstruct_the_direct_hessian() -> None:
    from experiments.stable_ac.depth4_period_two_phi_infinity_hessian_certificate import (
        anchored_hessian_subtotals,
        beta_infinity,
        phi_infinity_hessian,
    )

    fixtures = (
        (
            "TT",
            "TTTct",
            (1, 1, 1, 1),
            (0, 0, 0, 1, 0, 0),
            (0, 1, 1, 1, 0),
        ),
        (
            "Tctt",
            "Tctct",
            (1, 1, 1, 1),
            (0, 0, 0, 0, 1, 1),
            (0, 0, 0, 0, 0),
        ),
    )
    for left_label, right_label, equality_terms, inversion_terms, totals in fixtures:
        left = lift.parse_quotient(left_label)
        right = lift.parse_quotient(right_label)
        subtotals = anchored_hessian_subtotals(left, right)
        assert subtotals.equality_terms == equality_terms
        assert subtotals.inversion_terms == inversion_terms
        assert len(subtotals.external_terms) == 66
        assert len(subtotals.external_reversed_terms) == 66
        assert (
            subtotals.equality,
            subtotals.inversion,
            subtotals.external,
            subtotals.external_reversed,
            subtotals.total,
        ) == totals
        left_direction = tree.anchored_direction(left)
        right_direction = tree.anchored_direction(right)
        assert subtotals.external == subtotals.external_reversed
        assert beta_infinity(left, right) == subtotals.total
        assert subtotals.total == phi_infinity_hessian(left_direction, right_direction)


def test_task_two_pair_path_and_tracked_fixtures_use_the_universal_formula(
    monkeypatch,
) -> None:
    import importlib

    from experiments import stable_ac
    from experiments.stable_ac import depth4_period_two_source_flow_certificate as source
    from experiments.stable_ac import depth4_period_two_phi_infinity_hessian_certificate as hessian

    def forbidden_census(*_args, **_kwargs):
        raise AssertionError("source-depth census called by Task 2 certificate")

    class ForbiddenCensusModule:
        def __getattr__(self, name):
            raise AssertionError(f"census aggregate attribute accessed: {name}")

    monkeypatch.setattr(source, "source_vertices", forbidden_census)
    monkeypatch.setattr(
        stable_ac,
        "depth4_period_two_depth6_l0_census_certificate",
        ForbiddenCensusModule(),
        raising=False,
    )
    monkeypatch.delattr(hessian, "census", raising=False)
    hessian = importlib.reload(hessian)
    assert not hasattr(hessian, "census")
    hessian.phi_infinity_hessian_certificate.cache_clear()
    certificate = hessian.phi_infinity_hessian_certificate()

    assert certificate.anchored_normal_form == hessian.anchored_kernel_normal_form()
    assert certificate.near_survivor_pair_values == (
        ("TT", "TTTct", 1, 1, "000000000000001"),
        ("Tctt", "Tctct", 1, 1, "000000000000001"),
    )
    assert certificate.near_survivor_direct_matches == (True, True)
    assert certificate.negative_balanced_pair_value == (
        "TTT",
        "cTTT",
        -1,
        1,
        "111100000011001",
    )
    assert certificate.negative_balanced_direct_match
    assert certificate.unbalanced_pair_value == ("", "T", 1, 0, "000000000000000")
    assert certificate.near_survivor_extensions == (
        ("c", "000100000000100", "100100011000001"),
        ("t", "000000001000000", "100100011000100"),
        ("T", "011110110101110", "011110111101010"),
    )
    assert certificate.near_survivor_extension_direct_matches == (
        (True, True),
        (True, True),
        (True, True),
    )
    assert certificate.tracked_direction_syndromes == (
        "100000011000000",
        "100000001100000",
        "011000011101100",
        "001000001011100",
        "000100000000100",
        "000010110110110",
        "000000011110000",
        "000000001000000",
        "000000000110000",
        "000000000011000",
        "000000000000100",
    )
    assert certificate.tracked_direction_direct_matches == (True,) * 11
