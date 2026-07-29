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
