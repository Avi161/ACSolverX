from experiments.stable_ac import depth4_period_two_lift_certificate as lift


def recurrence(conjugators):
    g_0, g_1, g_2, g_3, g_4 = conjugators
    row_r = lift.multiply(
        lift.SOURCE_A,
        lift.conjugate(lift.inverse(lift.SOURCE_B), g_0),
    )
    row_s = lift.multiply(
        lift.SOURCE_B,
        lift.conjugate(lift.inverse(row_r), g_1),
    )
    row_u = lift.multiply(
        row_r,
        lift.conjugate(lift.inverse(row_s), g_2),
    )
    row_z = lift.multiply(
        lift.inverse(row_u),
        lift.conjugate(row_s, g_3),
    )
    target = lift.conjugate(lift.TARGET, g_4)
    residual = lift.multiply(row_z, lift.inverse(target))
    return row_r, row_s, row_u, row_z, target, residual


def left_multiply(word, left):
    return lift.multiply(left, word)


def test_four_hurwitz_symmetries_conjugate_the_literal_residual() -> None:
    conjugators = (lift.H0, lift.H1, lift.H2, lift.H3, ())
    row_r, row_s, row_u, row_z, target, residual = recurrence(conjugators)

    a_inverse = lift.inverse(lift.SOURCE_A)
    h_a = (
        left_multiply(conjugators[0], a_inverse),
        lift.multiply(conjugators[1], lift.SOURCE_A),
        left_multiply(conjugators[2], a_inverse),
        left_multiply(conjugators[3], a_inverse),
        left_multiply(conjugators[4], a_inverse),
    )
    a_rows = recurrence(h_a)
    assert a_rows[:5] == (
        lift.conjugate(row_r, a_inverse),
        row_s,
        lift.conjugate(row_u, a_inverse),
        lift.conjugate(row_z, a_inverse),
        lift.conjugate(target, a_inverse),
    )
    assert a_rows[5] == lift.conjugate(residual, a_inverse)

    b_inverse = lift.inverse(lift.SOURCE_B)
    h_b = (
        conjugators[0],
        left_multiply(conjugators[1], b_inverse),
        lift.multiply(conjugators[2], lift.SOURCE_B),
        lift.multiply(conjugators[3], lift.SOURCE_B),
        conjugators[4],
    )
    b_rows = recurrence(h_b)
    assert b_rows[:5] == (
        row_r,
        lift.conjugate(row_s, b_inverse),
        row_u,
        row_z,
        target,
    )
    assert b_rows[5] == residual

    r_inverse = lift.inverse(row_r)
    h_r = (
        conjugators[0],
        conjugators[1],
        left_multiply(conjugators[2], r_inverse),
        left_multiply(conjugators[3], r_inverse),
        left_multiply(conjugators[4], r_inverse),
    )
    r_rows = recurrence(h_r)
    assert r_rows[:5] == (
        row_r,
        row_s,
        lift.conjugate(row_u, r_inverse),
        lift.conjugate(row_z, r_inverse),
        lift.conjugate(target, r_inverse),
    )
    assert r_rows[5] == lift.conjugate(residual, r_inverse)

    h_u = (
        conjugators[0],
        conjugators[1],
        conjugators[2],
        left_multiply(conjugators[3], row_u),
        left_multiply(conjugators[4], row_u),
    )
    u_rows = recurrence(h_u)
    assert u_rows[:5] == (
        row_r,
        row_s,
        row_u,
        lift.conjugate(row_z, row_u),
        lift.conjugate(target, row_u),
    )
    assert u_rows[5] == lift.conjugate(residual, row_u)


def test_witness_hurwitz_orbit_leaves_the_row_centralizer_gauge_class() -> None:
    conjugators = (lift.H0, lift.H1, lift.H2, lift.H3, ())
    row_r = recurrence(conjugators)[0]
    quotient_a = lift.quotient_reduce(lift.SOURCE_A)
    quotient_r = lift.quotient_reduce(row_r)
    conjugated_r = lift.quotient_multiply(
        lift.quotient_inverse(quotient_a),
        quotient_r,
        quotient_a,
    )
    assert lift.literal(quotient_a) == "TTcTTcttc"
    assert lift.literal(quotient_r) == "TTctcTctc"
    assert lift.literal(conjugated_r) == "cTTctttcTctcTTcTTcttc"
    assert conjugated_r != quotient_r
