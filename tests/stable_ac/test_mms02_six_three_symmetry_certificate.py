from experiments.stable_ac.mms02_six_three_symmetry_certificate import data, word_matrix


def multiply(left, right):
    return [[sum(left[row][index] * right[index][column] for index in range(2)) % 313
             for column in range(2)] for row in range(2)]


def determinant(matrix):
    return (matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]) % 313


def inverse(matrix):
    scale = pow(determinant(matrix), -1, 313)
    return [[matrix[1][1] * scale % 313, -matrix[0][1] * scale % 313],
            [-matrix[1][0] * scale % 313, matrix[0][0] * scale % 313]]


def evaluate(word, s=3):
    a, b = [[1, 1], [0, 1]], [[1, 0], [-s % 313, 1]]
    images = {"a": a, "b": b, "A": inverse(a), "B": inverse(b)}
    value = [[1, 0], [0, 1]]
    for letter in word:
        value = multiply(value, images[letter])
    return value


def trace(matrix):
    return (matrix[0][0] + matrix[1][1]) % 313


def test_mod313_relation_endpoint_pins_and_gl2_symmetries_are_independent():
    certificate = data()
    r_word = "abaBABabABAbaBABabaBAbabAB"
    u_word, v_word = "AABAbABabaBAbabABAbaa", "AABabABabaBABabABAbaa"
    assert certificate["words"] == {"R": r_word, "U": u_word, "V": v_word}
    assert certificate["prime"] == 313 and certificate["s"] == 3
    assert evaluate(r_word) == [[1, 0], [0, 1]]
    assert (trace(evaluate(u_word)), trace(evaluate(v_word)), trace(evaluate(v_word[::-1].swapcase()))) == (229, 272, 272)
    a, b, d, j = evaluate("a"), evaluate("b"), [[312, 0], [0, 1]], [[0, 1], [310, 0]]
    assert multiply(multiply(d, a), inverse(d)) == inverse(a)
    assert multiply(multiply(d, b), inverse(d)) == inverse(b)
    assert multiply(multiply(j, a), inverse(j)) == b
    assert multiply(multiply(j, b), inverse(j)) == a
    matrices = {"a": a, "b": b, "D": d, "J": j, "relator": evaluate(r_word),
                "U": evaluate(u_word), "V": evaluate(v_word), "V_inverse": evaluate(v_word[::-1].swapcase())}
    for name, matrix in matrices.items():
        assert tuple(entry for row in matrix for entry in row) == certificate["matrices"][name]
        assert trace(matrix) == certificate["traces"][name]
        assert determinant(matrix) == certificate["determinants"][name]
        if name not in ("D", "J"):
            assert determinant(matrix) == 1
    assert evaluate(r_word, s=1) != [[1, 0], [0, 1]]
    assert tuple(entry for row in evaluate(r_word, s=1) for entry in row) == word_matrix(r_word, s=1)


def test_only_four_proposed_maps_have_trace_separation_with_positive_control():
    certificate = data()
    raw_maps = (("identity", {"a": "a", "b": "b"}), ("swap", {"a": "b", "b": "a"}),
                ("both_inverse", {"a": "A", "b": "B"}), ("swap_inverse", {"a": "B", "b": "A"}))
    r_word = "abaBABabABAbaBABabaBAbabAB"
    u_word = "AABAbABabaBAbabABAbaa"
    assert len(certificate["maps"]) == 4
    for record, (name, images) in zip(certificate["maps"], raw_maps, strict=True):
        signed = images | {letter.upper(): image.swapcase() for letter, image in images.items()}
        r_image = "".join(signed[letter] for letter in r_word)
        u_image = "".join(signed[letter] for letter in u_word)
        matches = [{"sign": sign, "rotation": cut}
                   for sign, word in ((1, r_word), (-1, r_word[::-1].swapcase()))
                   for cut in range(len(word)) if r_image == word[cut:] + word[:cut]]
        assert record["name"] == name and record["images"] == images
        assert record["relator_image"] == r_image
        assert record["cyclic_relator_matches"] == matches
        assert record["cyclic_relator_preserved"] is bool(matches)
        assert record["U_image"] == u_image
        assert trace(evaluate(u_image)) == record["U_trace"] == 229
        assert determinant(evaluate(u_image)) == 1
        assert tuple(entry for row in evaluate(u_image) for entry in row) == record["U_matrix"]
        assert tuple(tuple(entry for row in evaluate(images[letter]) for entry in row) for letter in "ab") == record["generator_matrices"]
    assert trace(evaluate(u_word)) == certificate["maps"][0]["U_trace"]
    assert trace(evaluate("b" + u_word + "B")) == trace(evaluate(u_word)) == 229
    assert 229 != 272
    assert certificate["status"] == "ONLY_FOUR_PROPOSED_MAPS_DO_NOT_GIVE_ENDPOINT_CONJUGACY"
    assert certificate["full_automorphism_classification_claimed"] is False
    assert certificate["ac_conclusion_claimed"] is False
