from experiments.stable_ac.depth4_period_two_witness import period_two_witness


def test_exact_period_two_recurrence_hits_the_target_literally() -> None:
    witness = period_two_witness()

    assert witness.z == (("t", 1),)
    assert witness.y == witness.u + (("t", 1),)


def test_period_two_witness_has_the_claimed_reduced_rows() -> None:
    witness = period_two_witness()

    assert witness.r == (
        ("t", -2),
        ("c", 1),
        ("t", 1),
        ("c", 1),
        ("t", -1),
        ("c", 1),
        ("t", 1),
        ("c", 1),
    )
    assert witness.s == (
        ("t", -3),
        ("c", 1),
        ("t", 2),
        ("c", 1),
        ("t", -1),
        ("c", 1),
        ("t", 2),
    )
    assert witness.u == (
        ("t", -2),
        ("c", 1),
        ("t", 2),
        ("c", 1),
        ("t", -1),
        ("c", 1),
    )


def test_backward_class_product_identity_replays_exactly() -> None:
    witness = period_two_witness()

    assert witness.x_r_inverse_y == witness.target
    assert witness.y_target_inverse_x == witness.r
