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


def substitute(word, images):
    signed = images | {letter.upper(): inverse(value) for letter, value in images.items()}
    return reduced("".join(signed[letter] for letter in word))


def phi(word, b_image="AbaB"):
    return substitute(word, {"a": "b", "b": b_image})


def iterate(word, count, b_image="AbaB"):
    for _ in range(count):
        word = phi(word, b_image)
    return word


def power(word, exponent):
    return reduced((word if exponent >= 0 else inverse(word)) * abs(exponent))


def height_scan(word):
    height, entries = 0, []
    for letter in word:
        if letter in "tT":
            height += 1 if letter == "t" else -1
        else:
            assert letter in "aA"
            entries.append((height, 1 if letter == "a" else -1))
    return tuple(entries), height


def rewritten(entries, shift, b_image="AbaB"):
    parts = []
    for height, sign in entries:
        assert height + shift >= 0
        image = iterate("a", height + shift, b_image)
        parts.append(image if sign == 1 else inverse(image))
    return reduced("".join(parts))


def fox_abelian(word, generator):
    a_exponent = b_exponent = 0
    derivative = {}
    for letter in word:
        sign = 1 if letter.islower() else -1
        if letter.lower() == generator and sign == 1:
            key = (a_exponent, b_exponent)
            derivative[key] = derivative.get(key, 0) + 1
        if letter.lower() == "a":
            a_exponent += sign
        else:
            assert letter.lower() == "b"
            b_exponent += sign
        if letter.lower() == generator and sign == -1:
            key = (a_exponent, b_exponent)
            derivative[key] = derivative.get(key, 0) - 1
    return {key: value for key, value in derivative.items() if value}, (a_exponent, b_exponent)


def test_opposite_donor_height_scans_are_derived_from_literal_raw_words():
    raw_a, raw_b = "xYxYXyyXYxyXy", "XyyXYXyxYYxy"
    images = {"x": "at", "y": "t"}
    b_entries, b_height = height_scan(substitute(raw_b, images))
    assert b_height == 0
    assert min(height for height, _ in b_entries) == -2
    names = {0: "a", 1: "b", 2: "d"}
    indexed_b = reduced("".join(names[height + 2] if sign == 1 else names[height + 2].upper()
                                for height, sign in b_entries))
    assert indexed_b == "BDAba"
    assert substitute(indexed_b, {"a": "a", "b": "b", "d": phi("b")}) == ""
    assert rewritten(b_entries, 2) == ""
    assert rewritten(b_entries, 2, "abAB") != ""
    a_entries, a_height = height_scan(substitute(inverse(raw_a), images))
    assert a_height == -1
    assert min(height for height, _ in a_entries) >= -3
    coefficient = rewritten(a_entries, 3)
    d_word = phi("b")
    assert coefficient == reduced(d_word + phi(d_word) + inverse(d_word))
    assert coefficient == iterate("abA", 2)


def test_opposite_donor_fifth_iterate_has_nontrivial_fox_invisible_defect():
    u_word = "abA"
    for m in (-2, 0, 1, 3):
        a_power = power("a", m)

        def transformation(word):
            return reduced(inverse(u_word) + phi(word) + a_power)

        q_word = ""
        for _ in range(4):
            q_word = transformation(q_word)
        left = reduced("".join(iterate(inverse(u_word), index) for index in range(4)))
        right = reduced("".join(iterate(a_power, index) for index in (3, 2, 1, 0)))
        assert q_word == reduced(left + right)
        next_word = transformation(q_word)
        assert next_word == reduced(left + iterate(reduced(inverse(u_word) + a_power), 4) + right)
        defect = reduced(next_word + inverse(q_word))
        assert defect != ""
        for generator in "ab":
            derivative, abelianization = fox_abelian(defect, generator)
            assert abelianization == (0, 0)
            assert derivative == {}


def test_opposite_donor_basis_letter_counts_and_ob2_residual_controls():
    words = ("", "a", "A", "q", "Q", "qAq", "qaQ", "qAQ", "Qaq", "QAq", "QaQ",
             "aqa", "AQA", "qq", "QQ", "aaqqAAQQ", "qAAqaaQ", "AQaqAQ", "qqaQQAqq")
    for word in words:
        assert reduced(word) == word
        c_word = substitute(word, {"a": "a", "q": "ba"})
        phi_c = substitute(word, {"a": "b", "q": "Aba"})
        assert phi(c_word) == phi_c
        b_count = sum(letter in "bB" for letter in c_word)
        phi_b_count = sum(letter in "bB" for letter in phi_c)
        assert b_count == sum(letter in "qQ" for letter in word)
        assert phi_b_count == len(word)
        for m in (-3, 0, 1, 4):
            rhs = reduced("aBA" + phi_c + power("a", m))
            assert sum(letter in "bB" for letter in rhs) == 1 + phi_b_count
            assert sum(letter in "bB" for letter in rhs) > b_count
            assert reduced(rhs + inverse(c_word)) != ""


def test_extra_b_count_requires_the_fixed_donor_boundary():
    u_control, c_word = "bA", "a"
    unreduced_rhs = inverse(u_control) + phi(c_word)
    assert unreduced_rhs == "aBb"
    assert reduced(unreduced_rhs) == c_word
    assert sum(letter in "bB" for letter in reduced(unreduced_rhs)) == 0
    assert 1 + sum(letter in "bB" for letter in phi(c_word)) == 2
