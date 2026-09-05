from experiments.stable_ac.mms02_six_three_parabolic_certificate import data, word_matrix


def multiply(left, right):
    return [[sum(left[row][index] * right[index][column] for index in range(2)) % 23
             for column in range(2)] for row in range(2)]


def inverse(matrix):
    assert (matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]) % 23 == 1
    return [[matrix[1][1] % 23, -matrix[0][1] % 23], [-matrix[1][0] % 23, matrix[0][0] % 23]]


def evaluate(word, s=2):
    a, b = [[1, 1], [0, 1]], [[1, 0], [-s % 23, 1]]
    images = {"a": a, "A": inverse(a), "b": b, "B": inverse(b)}
    value = [[1, 0], [0, 1]]
    for letter in word:
        value = multiply(value, images[letter])
    return value


def test_six_three_mod23_witness_has_independent_full_matrix_replay():
    certificate = data()
    w, u, v = "baBABabABAba", "AABAbABabaBAbabABAbaa", "AABabABabaBABabABAbaa"
    relator = "a" + w + "B" + w[::-1].swapcase()
    assert certificate["words"] == {"w": w, "U": u, "V": v, "relator": relator}
    assert certificate["prime"] == 23 and certificate["s"] == 2
    images = {"y": "A", "Y": "a", "z": "AAB", "Z": "baa"}
    for raw, expected in (("zyZyzYZYzyZyZyzyZ", u), ("zYZyzYZYzYzYZyzyZ", v)):
        stack = []
        for letter in "".join(images[letter] for letter in raw):
            if stack and stack[-1].swapcase() == letter:
                stack.pop()
            else:
                stack.append(letter)
        assert "".join(stack) == expected
    identity, a, b = [[1, 0], [0, 1]], evaluate("a"), evaluate("b")
    assert multiply(a, evaluate(w)) == multiply(evaluate(w), b)
    assert evaluate(relator) == identity
    for name, word in (("a", "a"), ("b", "b"), ("w", w), ("relator", relator), ("U", u), ("V", v)):
        matrix = evaluate(word)
        assert tuple(value for row in matrix for value in row) == certificate["matrices"][name]
        assert (matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]) % 23 == certificate["determinants"][name] == 1
        assert (matrix[0][0] + matrix[1][1]) % 23 == certificate["traces"][name]
    assert certificate["traces"]["U"] == certificate["traces"]["V"] == 11
    assert 11 * 11 % 23 == 6 != 4
    assert evaluate(relator, s=1) != identity
    assert tuple(value for row in evaluate(relator, s=1) for value in row) == word_matrix(relator, s=1)


def test_mod23_meridian_power_and_known_centralizers_are_positive_controls():
    a, b = evaluate("a"), evaluate("b")
    seventh = evaluate("a" * 7)
    conjugated = multiply(multiply(b, seventh), inverse(b))
    assert (seventh[0][0] + seventh[1][1]) % 23 == 2
    assert (conjugated[0][0] + conjugated[1][1]) % 23 == 2
    for diagonal in (1, 22):
        for upper in range(23):
            matrix = [[diagonal, upper], [0, diagonal]]
            assert multiply(a, matrix) == multiply(matrix, a)
            assert (matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]) % 23 == 1
            assert ((matrix[0][0] + matrix[1][1]) % 23) ** 2 % 23 == 4
