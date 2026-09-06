def reduced(word):
    stack = []
    for letter in word:
        if stack and stack[-1] == letter.swapcase():
            stack.pop()
        else:
            stack.append(letter)
    return "".join(stack)


def inverse(word):
    return word[::-1].swapcase()


def r_power(exponent):
    return ("r" if exponent >= 0 else "R") * abs(exponent)


def collect_x_letters(word):
    height = 0
    occurrences = []
    for letter in word:
        if letter in "rR":
            height += 1 if letter == "r" else -1
        else:
            assert letter in "xX"
            occurrences.append((height, 1 if letter == "x" else -1))
    return tuple(occurrences), height


def test_signed_letter_collection_and_exponent_one_defect():
    cases = (("RRxrrr", ((-2, 1),)),
             ("RxXrr", ((-1, 1), (-1, -1))),
             ("rXRRxrr", ((1, -1), (-1, 1))))
    for word, expected in cases:
        occurrences, exponent = collect_x_letters(word)
        assert occurrences == expected and exponent == 1
        factors = [r_power(height) + ("x" if sign == 1 else "X") + r_power(-height)
                   for height, sign in occurrences]
        product = "".join(factors)
        assert reduced(word) == reduced(product + r_power(exponent))
        defining_row = "Y" + word
        assert reduced(defining_row + "R") == reduced("Y" + product)
    assert collect_x_letters("RxXrr")[0] == ((-1, 1), (-1, -1))
    assert reduced("RxXrr") == "r"


def test_wrong_terminal_power_fails_for_exponent_two():
    word = "RxxXrrr"
    occurrences, exponent = collect_x_letters(word)
    assert exponent == 2
    product = "".join(r_power(height) + ("x" if sign == 1 else "X") + r_power(-height)
                      for height, sign in occurrences)
    assert reduced(word) == reduced(product + "rr")
    assert reduced(word) != reduced(product + "r")
    assert reduced("Y" + word + "R") != reduced("Y" + product)


def test_exponent_one_example_has_the_pinned_length_five_cyclic_core():
    word = "yxyXYxyXY"
    conjugator = "yx"
    core = "yXYxy"
    assert reduced(word) == word
    assert reduced(conjugator + core + inverse(conjugator)) == word
    assert reduced(inverse(conjugator) + word + conjugator) == core
    assert len(core) == 5 and reduced(core) == core
    assert core[0] != core[-1].swapcase()
    assert sum(1 if letter == "y" else -1 if letter == "Y" else 0 for letter in word) == 1
