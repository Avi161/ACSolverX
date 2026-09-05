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


RAW_A = "TccccTcccTccccTCtCCCCtC"
RAW_B = "TccccTccccTCtCCCtC"
RAW_WITNESS = ("cTTcttt", "", "cTcttt", "t", "")


def literal_inverse(word):
    return word[::-1].swapcase()


def literal_multiply(*words):
    stack = []
    for word in words:
        for letter in word:
            if stack and stack[-1].swapcase() == letter:
                stack.pop()
            else:
                stack.append(letter)
    return "".join(stack)


def literal_conjugate(word, prefix):
    return literal_multiply(prefix, word, literal_inverse(prefix))


def literal_recurrence(conjugators):
    g0, g1, g2, g3, g4 = conjugators
    r = literal_multiply(RAW_A, literal_conjugate(literal_inverse(RAW_B), g0))
    s = literal_multiply(RAW_B, literal_conjugate(literal_inverse(r), g1))
    u = literal_multiply(r, literal_conjugate(literal_inverse(s), g2))
    z = literal_multiply(literal_inverse(u), literal_conjugate(s, g3))
    target = literal_conjugate("t", g4)
    return r, s, u, z, target, literal_multiply(z, literal_inverse(target))


def independent_c2_z_reduce(word):
    syllables = []
    for letter in word:
        factor = "c" if letter.lower() == "c" else "t"
        value = 1 if factor == "c" or letter == "t" else -1
        if syllables and syllables[-1][0] == factor:
            value += syllables.pop()[1]
        if factor == "c":
            value %= 2
        if value:
            syllables.append((factor, value))
    return "".join("c" if factor == "c" else ("t" if value > 0 else "T") * abs(value)
                   for factor, value in syllables)


def test_witness_row_quotients_and_s_cyclic_blocks_are_independent() -> None:
    encoding = {"c": 1, "C": -1, "t": 2, "T": -2}
    assert tuple(encoding[letter] for letter in RAW_A) == lift.SOURCE_A
    assert tuple(encoding[letter] for letter in RAW_B) == lift.SOURCE_B
    assert tuple(tuple(encoding[letter] for letter in word) for word in RAW_WITNESS) == (
        lift.H0, lift.H1, lift.H2, lift.H3, (),
    )
    r, s, _, _, target, _ = literal_recurrence(RAW_WITNESS)
    assert independent_c2_z_reduce(RAW_B) == "TTTctctc"
    assert independent_c2_z_reduce(r) == "TTctcTctc"
    assert independent_c2_z_reduce(s) == "TTTcttcTctt"
    assert independent_c2_z_reduce(target) == "t"
    assert RAW_B.count("t") - RAW_B.count("T") == -1
    assert r.count("t") - r.count("T") == -1
    assert target.count("t") - target.count("T") == 1
    cyclic_s = independent_c2_z_reduce("ttt" + s + "TTT")
    assert cyclic_s == "cttcTcT"
    blocks = tuple(block.count("t") - block.count("T") for block in cyclic_s.split("c")[1:])
    assert blocks == (2, -1, -1)
    assert cyclic_s.count("c") == 3
    assert tuple(exponent for exponent in range(2, 4) if 3 % exponent == 0) == (3,)
    assert blocks != blocks[:1] * 3
    cube_control = independent_c2_z_reduce("ctt" * 3)
    cube_blocks = tuple(block.count("t") - block.count("T") for block in cube_control.split("c")[1:])
    assert cube_blocks == (2, 2, 2)
    assert cube_blocks == cube_blocks[:1] * 3


def test_literal_right_row_power_gauges_preserve_arbitrary_lift_recurrences() -> None:
    cases = (
        RAW_WITNESS,
        ("cc" + RAW_WITNESS[0], "cc", "CC" + RAW_WITNESS[2], "cct", "Tcc"),
        ("tccT" + RAW_WITNESS[0], "CCT", "tccT" + RAW_WITNESS[2], "CCt", "ctCC"),
    )
    exponents = ((0, 0, 0, 0, 0), (1, -1, 1, -1, 1), (-1, 1, -1, 1, -1))
    for conjugators in cases:
        baseline = literal_recurrence(conjugators)
        r, s = baseline[:2]
        donors = (RAW_B, r, s, s, "t")
        for powers in exponents:
            gauged = tuple(literal_multiply(prefix, (donor if exponent >= 0 else literal_inverse(donor)) * abs(exponent))
                           for prefix, donor, exponent in zip(conjugators, donors, powers, strict=True))
            assert literal_recurrence(gauged) == baseline
    witness_rows = literal_recurrence(RAW_WITNESS)
    wrong = (literal_multiply(RAW_WITNESS[0], RAW_A),) + RAW_WITNESS[1:]
    assert literal_recurrence(wrong)[0] != witness_rows[0]
