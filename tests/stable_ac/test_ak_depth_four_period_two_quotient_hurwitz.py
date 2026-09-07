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


def literal_hurwitz_swap(conjugators):
    g0, g1, g2, g3, g4 = conjugators
    _, s, u, _, _, _ = literal_recurrence(conjugators)
    c = literal_conjugate(s, g3)
    return g0, g1, g3, literal_multiply(u, g2), literal_multiply(c, g4)


def literal_hurwitz_swap_inverse(conjugators):
    k0, k1, k2, k3, k4 = conjugators
    r, s = literal_recurrence(conjugators)[:2]
    c = literal_conjugate(s, k2)
    return (
        k0,
        k1,
        literal_multiply(literal_inverse(r), k3, s),
        k2,
        literal_multiply(literal_inverse(c), k4),
    )


def test_literal_hurwitz_swap_and_inverse_conjugate_nonzero_residuals() -> None:
    cases = (RAW_WITNESS, ("c", "t", "T", "C", "ct"), ("tC", "c", "ct", "T", "tc"))
    nonzero_residuals = []
    wrong_fifth_controls = []
    for conjugators in cases:
        r, s, u, z, target, residual = literal_recurrence(conjugators)
        c = literal_conjugate(s, conjugators[3])
        swapped = literal_hurwitz_swap(conjugators)
        assert swapped == (
            conjugators[0], conjugators[1], conjugators[3],
            literal_multiply(u, conjugators[2]), literal_multiply(c, conjugators[4]),
        )
        assert literal_recurrence(swapped) == (
            r, s, literal_multiply(r, literal_inverse(c)),
            literal_conjugate(z, c), literal_conjugate(target, c),
            literal_conjugate(residual, c),
        )
        assert literal_hurwitz_swap_inverse(swapped) == conjugators
        assert literal_hurwitz_swap(literal_hurwitz_swap_inverse(conjugators)) == conjugators
        nonzero_residuals.append(bool(residual))
        wrong_fifth = swapped[:4] + (conjugators[4],)
        wrong_rows = literal_recurrence(wrong_fifth)
        wrong_fifth_controls.append(
            wrong_rows[4] != literal_conjugate(target, c)
            and wrong_rows[5] != literal_conjugate(residual, c)
        )
    assert all(nonzero_residuals[1:])
    assert all(wrong_fifth_controls[1:])


def test_hurwitz_swap_changes_witness_u_cyclic_syllable_length_in_quotient() -> None:
    original = literal_recurrence(RAW_WITNESS)
    swapped_conjugators = literal_hurwitz_swap(RAW_WITNESS)
    assert tuple(independent_c2_z_reduce(word) for word in swapped_conjugators) == (
        "cTTcttt", "", "t", "TTcttcTTcttt", "TTcttcTct",
    )
    swapped = literal_recurrence(swapped_conjugators)
    r, s, _, z, target, residual = original
    c = literal_conjugate(s, RAW_WITNESS[3])
    assert swapped == (
        r, s, literal_multiply(r, literal_inverse(c)),
        literal_conjugate(z, c), literal_conjugate(target, c),
        literal_conjugate(residual, c),
    )
    assert independent_c2_z_reduce(z) == independent_c2_z_reduce(target)
    assert independent_c2_z_reduce(swapped[3]) == independent_c2_z_reduce(swapped[4])
    u = "TTcttcTc"
    u_prime = "TTctcTctcTctcTTctt"
    k = "TTct"
    w = "cTctcTctcT"
    assert independent_c2_z_reduce(original[2]) == u
    assert independent_c2_z_reduce(swapped[2]) == u_prime
    assert independent_c2_z_reduce(literal_conjugate(w, k)) == u_prime
    assert independent_c2_z_reduce(u) == u
    assert independent_c2_z_reduce(w) == w
    assert u[0].lower() != u[-1].lower()
    assert w[0].lower() != w[-1].lower()
    u_syllables = 1 + sum(a.lower() != b.lower() for a, b in zip(u, u[1:]))
    w_syllables = 1 + sum(a.lower() != b.lower() for a, b in zip(w, w[1:]))
    assert u_syllables == 6
    assert w_syllables == 10
    encoding = {"c": 1, "C": -1, "t": 2, "T": -2}
    for word in (*original, *swapped, u, u_prime, k, w, literal_conjugate(w, k)):
        encoded = tuple(encoding[letter] for letter in word)
        assert lift.literal(lift.quotient_reduce(encoded)) == independent_c2_z_reduce(word)
