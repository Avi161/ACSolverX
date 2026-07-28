from experiments.stable_ac.verify_internal_bs34_flow import (
    canonical_collapse_matrix,
    classify_one_y_selected_edge,
    half_star_indices,
    matrix_rank,
    one_y_double_coset_signature,
    one_y_scalar_patterns,
)


def test_incoming_half_star_is_independent_of_vertex_representative():
    expected = (0, 1, 2, 3)

    assert half_star_indices("incoming", representative_power=0) == expected
    assert half_star_indices("incoming", representative_power=1) == expected
    assert half_star_indices("incoming", representative_power=-9) == expected


def test_outgoing_half_star_uses_three_cosets_and_is_representative_independent():
    expected = (0, 1, 2)

    assert half_star_indices("outgoing", representative_power=0) == expected
    assert half_star_indices("outgoing", representative_power=1) == expected
    assert half_star_indices("outgoing", representative_power=14) == expected


def test_four_incoming_constraints_have_full_rank_for_both_signs():
    for sigma, expected_star_coefficient in ((1, 5), (-1, -3)):
        matrix = canonical_collapse_matrix(branching=4, sigma=sigma)

        assert len(matrix) == 5
        assert all(len(row) == 5 for row in matrix)
        assert matrix[-1] == (-1, -1, -1, -1, 1)
        assert sum(matrix[index][-1] for index in range(4)) + 1 == (
            expected_star_coefficient
        )
        assert matrix_rank(matrix) == 5


def test_three_outgoing_constraints_have_full_rank_for_both_signs():
    for sigma, expected_star_coefficient in ((1, 4), (-1, -2)):
        matrix = canonical_collapse_matrix(branching=3, sigma=sigma)

        assert len(matrix) == 4
        assert all(len(row) == 4 for row in matrix)
        assert matrix[-1] == (-1, -1, -1, 1)
        assert sum(matrix[index][-1] for index in range(3)) + 1 == (
            expected_star_coefficient
        )
        assert matrix_rank(matrix) == 4


def test_one_y_double_coset_keeps_left_x_residue_and_discards_right_power():
    assert one_y_double_coset_signature(0, 0) == 0
    assert one_y_double_coset_signature(4, 17) == 0
    assert one_y_double_coset_signature(-8, -3) == 0

    assert one_y_double_coset_signature(1, 0) == 1
    assert one_y_double_coset_signature(6, 99) == 2
    assert one_y_double_coset_signature(-1, -11) == 3


def test_cxy_is_a_britton_reduced_selected_edge_outside_both_local_half_stars():
    canonical = classify_one_y_selected_edge(0, 5)
    noncanonical = classify_one_y_selected_edge(1, 0)

    assert canonical.left_residue == 0
    assert canonical.local_half_star == "outgoing"
    assert noncanonical.left_residue == 1
    assert noncanonical.britton_word == "xy"
    assert noncanonical.local_half_star is None


def test_one_y_scalar_system_splits_into_fixed_turn_and_height_lowering_patterns():
    canonical = one_y_scalar_patterns(0)
    noncanonical = one_y_scalar_patterns(5)

    assert canonical.left_residue == 0
    assert canonical.intralayer_turns == ((0, 0), (0, 1), (0, 2))
    assert canonical.interlayer_x_powers == (0, 1, 2, 3)

    assert noncanonical.left_residue == 1
    assert noncanonical.intralayer_turns == ((-1, 0), (-1, 1), (-1, 2))
    assert noncanonical.interlayer_x_powers == (-1, 0, 1, 2)
