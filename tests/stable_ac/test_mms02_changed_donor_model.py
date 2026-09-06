RAW_A = "xYxYXyyXYxyXy"
RAW_B = "XyyXYXyxYYxy"


def reduced(word):
    stack = []
    for letter in word:
        if stack and stack[-1] == -letter:
            stack.pop()
        else:
            stack.append(letter)
    return tuple(stack)


def inverse(word):
    return tuple(-letter for letter in reversed(word))


def substitute(word, images):
    return reduced(part for letter in word
                   for part in (images[letter] if letter > 0 else inverse(images[-letter])))


PHI = {1: (2,), 2: (3,), 3: (4,), 4: (5,),
       5: (-5, -2, -2, 1, 4, 4, 5, -4, 5, 5)}
PSI = {1: (1, 1, 4, 5, -4, -4, 3, -4, -3, -3),
       2: (1,), 3: (2,), 4: (3,), 5: (4,)}


def iterate(word, exponent, phi=PHI):
    result = tuple(word)
    for _ in range(abs(exponent)):
        result = substitute(result, phi if exponent >= 0 else PSI)
    return result


def multiply(left, right, phi=PHI):
    word, height = left
    other, shift = right
    return reduced(word + iterate(other, height, phi)), height + shift


def group_inverse(element, phi=PHI):
    word, height = element
    return iterate(inverse(word), -height, phi), -height


def evaluate(word, images, phi=PHI):
    result = ((), 0)
    for letter in word:
        image = images[letter.lower()]
        if letter.isupper():
            image = group_inverse(image, phi)
        result = multiply(result, image, phi)
    return result


def scan(word):
    expansions = {"x": "att", "X": "TTA", "y": "t", "Y": "T"}
    height, occurrences = 0, []
    for letter in word:
        for expanded in expansions[letter]:
            if expanded in "aA":
                occurrences.append((height, 1 if expanded == "a" else -1))
            else:
                height += 1 if expanded == "t" else -1
    return tuple(occurrences), height


def test_changed_basis_and_literal_height_scans():
    # Integer alphabets encode x,y and a,t respectively as 1,2.
    forward = {1: (1, -2, -2), 2: (2,)}
    backward = {1: (1, 2, 2), 2: (2,)}
    for generator in (1, 2):
        assert substitute(forward[generator], backward) == (generator,)
        assert substitute(backward[generator], forward) == (generator,)
    a_scan = ((0, 1), (1, 1), (0, -1), (0, -1), (-1, 1), (0, -1))
    b_scan = ((-2, -1), (-2, -1), (-5, -1), (-4, 1), (-4, 1))
    assert scan(RAW_A) == (a_scan, 1)
    assert scan(RAW_B) == (b_scan, -1)
    expected_r = a_scan + ((-1, -1), (-1, -1), (-4, -1), (-3, 1), (-3, 1))
    assert scan(RAW_A + RAW_B) == (expected_r, 0)


def test_changed_donor_automorphism_and_semidirect_presentation():
    for generator in range(1, 6):
        assert substitute(PHI[generator], PSI) == (generator,)
        assert substitute(PSI[generator], PHI) == (generator,)
    relation = (5, 6, -5, -5, 4, -5, -4, -4, -1, 2, 2)
    images = {generator: (generator,) for generator in range(1, 6)}
    images[6] = PHI[5]
    assert substitute(relation, images) == ()
    normal_images = {"a": ((5,), 0), "t": ((), 1)}
    raw_images = {"x": ((5,), 2), "y": ((), 1)}
    for index in range(5):
        shift = index - 4
        element = multiply(multiply(((), shift), normal_images["a"]), ((), -shift))
        assert element == ((index + 1,), 0)
        assert multiply(multiply(((), 1), element), ((), -1)) == (PHI[index + 1], 0)
    assert evaluate("xYY", raw_images) == normal_images["a"]
    assert evaluate("y", raw_images) == normal_images["t"]
    assert evaluate("att", normal_images) == raw_images["x"]
    assert evaluate("t", normal_images) == raw_images["y"]
    left = ((-2, -2, 1, 4, 4), 1)
    right = ((4, -3, 4, 4, -5, -4), -1)
    assert evaluate(RAW_A, raw_images) == left
    assert evaluate(RAW_B, raw_images) == right
    assert evaluate(RAW_A + RAW_B, raw_images) == ((), 0)
    assert multiply(left, right) == ((), 0)
    for raw in (RAW_A, RAW_B, RAW_A + RAW_B):
        occurrences, height = scan(raw)
        coefficient = reduced(letter for index, sign in occurrences
                              for letter in iterate((5 if sign > 0 else -5,), index))
        assert evaluate(raw, raw_images) == (coefficient, height)
    corrupted = dict(PHI)
    corrupted[5] = PHI[5][:-1]
    assert substitute(corrupted[5], PSI) != (5,)
    wrong_relation_images = dict(images)
    wrong_relation_images[6] = inverse(PHI[5])
    assert substitute(relation, wrong_relation_images) != ()


def test_small_twisted_conjugacy_formula_controls():
    left = ((-2, -2, 1, 4, 4), 1)
    for seed in ((), (1,), (4, -5)):
        for exponent in (-1, 0, 1):
            word = iterate(seed, exponent)
            conjugator = (word, 0)
            actual = multiply(multiply(group_inverse(conjugator), left), conjugator)
            expected = reduced(inverse(word) + left[0] + substitute(word, PHI)), 1
            assert actual == expected
            general_conjugator = (seed, exponent)
            actual_general = multiply(multiply(group_inverse(general_conjugator), left), general_conjugator)
            base_coefficient = reduced(inverse(seed) + left[0] + substitute(seed, PHI))
            assert actual_general == (iterate(base_coefficient, -exponent), 1)
