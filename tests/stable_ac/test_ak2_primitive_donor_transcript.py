def inverse(word):
    return word[::-1].swapcase()


def reduced(word):
    stack = []
    for letter in word:
        if stack and stack[-1].swapcase() == letter:
            stack.pop()
        else:
            stack.append(letter)
    return "".join(stack)


def power(word, exponent):
    return reduced((word if exponent >= 0 else inverse(word)) * abs(exponent))


def conjugate(word, prefix):
    return reduced(prefix + word + inverse(prefix))


def substitute(word, images):
    signed = images | {letter.upper(): inverse(value) for letter, value in images.items()}
    return reduced("".join(signed[letter] for letter in word))


def test_five_left_donor_factors_have_the_prescribed_family_transcript():
    for n in (2, 3, 4):
        donor = power("x", n) + power("y", -(n + 1))
        initial = "xyxYXY"
        start = "x" + "Y" * n
        prefixes = ("xyxYX", start, start + "x", start + "xY", start + "xY" + "x" * (n - 1))
        signs = (1, 1, -1, 1, -1)
        expected = (
            "xyxY" + "x" * (n - 1) + "Y" * (n + 2),
            start + "x" * (n + 1) + "Y" + "x" * (n - 1) + "Y" * (n + 2),
            start + "x" + "y" * n + "x" * (n - 1) + "Y" * (n + 2),
            start + "xY" + "x" * (2 * n - 1) + "Y" * (n + 2),
            start + "xY" + "x" * (n - 1) + "Y",
        )
        row = initial
        for sign, prefix, endpoint in zip(signs, prefixes, expected, strict=True):
            signed_donor = donor if sign == 1 else inverse(donor)
            temporary_donor = conjugate(signed_donor, prefix)
            assert reduced(endpoint + inverse(row)) == temporary_donor
            row = reduced(temporary_donor + row)
            assert row == endpoint
            restored = conjugate(temporary_donor, inverse(prefix))
            if sign == -1:
                restored = inverse(restored)
            assert restored == donor
        wrong = initial
        for index, (sign, prefix) in enumerate(zip(signs, prefixes, strict=True)):
            corrupted_sign = -sign if index == 0 else sign
            wrong = reduced(conjugate(donor if corrupted_sign == 1 else inverse(donor), prefix) + wrong)
        assert wrong != expected[-1]


def test_ak2_primitive_donor_basis_and_defining_deletion_are_literal():
    r2, w2 = "xxYYY", "xYYxYxY"
    forward = {"x": "pQ", "y": "Q"}
    backward = {"p": "xY", "q": "Y"}
    for generator in "xy":
        assert substitute(substitute(generator, forward), backward) == generator
    for generator in "pq":
        assert substitute(substitute(generator, backward), forward) == generator
    first, second = substitute(r2, forward), substitute(w2, forward)
    assert first == "pQpqq"
    assert second == "pqpp"
    second = conjugate(second, "P")
    assert second == "qppp"
    defining_change = {"p": "p", "q": "zPPP"}
    inverse_change = {"p": "p", "z": "qppp"}
    for generator in "pq":
        assert substitute(substitute(generator, defining_change), inverse_change) == generator
    for generator in "pz":
        assert substitute(substitute(generator, inverse_change), defining_change) == generator
    changed = (substitute(first, defining_change), substitute(second, defining_change))
    assert changed[0] == reduced("p" + "pppZ" + "p" + "zPPP" + "zPPP")
    assert changed[1] == "z"
    assert tuple(substitute(word, {"p": "p", "z": ""}) for word in changed) == ("P", "")


def test_ak2_cleanup_is_an_ordinary_ac_transcript_in_original_generators():
    first = "ppppZpzPPPzPPP"
    prefixes, signs = ("pppp", "ppppp", "pp"), (1, -1, -1)
    expected = ("pppppzPPPzPPP", "ppzPPP", "P")
    original_basis = {"p": "xY", "z": "YxYxYxY"}
    assert substitute(first, original_basis) == "xxYYY"
    for images in ({"p": "p", "z": "z"}, original_basis):
        row, donor = substitute(first, images), substitute("z", images)
        for prefix, sign, endpoint in zip(prefixes, signs, expected, strict=True):
            by = substitute(prefix, images)
            temporary = conjugate(donor if sign == 1 else inverse(donor), by)
            row = reduced(temporary + row)
            assert row == substitute(endpoint, images)
            restored = conjugate(temporary, inverse(by))
            if sign == -1:
                restored = inverse(restored)
            assert restored == donor
        row = inverse(row)
        assert row == substitute("p", images)
        q_row = donor
        for _ in range(3):
            q_row = reduced(q_row + inverse(row))
        assert q_row == substitute("zPPP", images)
        row = reduced(row + inverse(q_row))
        q_row = inverse(q_row)
        if images == original_basis:
            assert (row, q_row) == ("x", "y")


def test_actual_ak3_both_row_replay_keeps_the_actual_donor():
    p_word, first, w_word = "xY", "xxxYYYY", "xYYYxYxxY"
    donor = conjugate(w_word, inverse(p_word))
    assert donor == "YYxYxxYxY"
    assert donor != substitute("z", {"p": "xY", "z": "YxYxYxY"})
    lengths = []
    for exponent, sign in ((4, 1), (5, -1), (2, -1)):
        prefix = power(p_word, exponent)
        temporary = conjugate(donor if sign == 1 else inverse(donor), prefix)
        first = reduced(temporary + first)
        lengths.append(len(first))
        restored = conjugate(temporary, inverse(prefix))
        if sign == -1:
            restored = inverse(restored)
        assert restored == donor
    f_word = "XyXyyxYXyXyyyXYYxYxyXyxxYYYY"
    assert first == f_word
    assert lengths == [22, 27, 28]
    first = inverse(first)
    second = donor
    for _ in range(3):
        second = reduced(second + inverse(first))
    first = reduced(first + inverse(second))
    second = inverse(second)
    assert (first, second) == (reduced(power(f_word, -4) + inverse(donor)),
                               reduced(power(f_word, -3) + inverse(donor)))
    assert (len(first), len(second)) == (121, 93)
    for row in (first, second):
        assert reduced(row) == row
        assert row[0] != row[-1].swapcase()
