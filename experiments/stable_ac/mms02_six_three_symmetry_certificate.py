"""Exact mod-313 trace separation for four explicitly proposed basis maps."""

import json

from experiments.stable_ac.mms02_six_three_parabolic_certificate import U_WORD, V_WORD, W_WORD

PRIME = 313
IDENTITY = (1, 0, 0, 1)
A_MATRIX = (1, 1, 0, 1)
B_MATRIX = (1, 0, 310, 1)
D_MATRIX = (312, 0, 0, 1)
J_MATRIX = (0, 1, 310, 0)
RELATOR = "a" + W_WORD + "B" + W_WORD[::-1].swapcase()
MAPS = (
    ("identity", {"a": "a", "b": "b"}),
    ("swap", {"a": "b", "b": "a"}),
    ("both_inverse", {"a": "A", "b": "B"}),
    ("swap_inverse", {"a": "B", "b": "A"}),
)


def determinant(matrix):
    a, b, c, d = matrix
    return (a * d - b * c) % PRIME


def matrix_multiply(left, right):
    a, b, c, d = left
    e, f, g, h = right
    return tuple(value % PRIME for value in (a * e + b * g, a * f + b * h,
                                            c * e + d * g, c * f + d * h))


def matrix_inverse(matrix):
    a, b, c, d = matrix
    scale = pow(determinant(matrix), -1, PRIME)
    return tuple(value * scale % PRIME for value in (d, -b, -c, a))


def word_matrix(word, s=3):
    b_matrix = (1, 0, -s % PRIME, 1)
    images = {"a": A_MATRIX, "b": b_matrix,
              "A": matrix_inverse(A_MATRIX), "B": matrix_inverse(b_matrix)}
    value = IDENTITY
    for letter in word:
        value = matrix_multiply(value, images[letter])
    return value


def mapped_word(word, images):
    signed = images | {letter.upper(): value[::-1].swapcase() for letter, value in images.items()}
    return "".join(signed[letter] for letter in word)


def trace(matrix):
    return (matrix[0] + matrix[3]) % PRIME


def data():
    if word_matrix(RELATOR) != IDENTITY:
        raise AssertionError("the mod-313 base relation drifted")
    for conjugator, expected in ((D_MATRIX, (matrix_inverse(A_MATRIX), matrix_inverse(B_MATRIX))),
                                 (J_MATRIX, (B_MATRIX, A_MATRIX))):
        actual = tuple(matrix_multiply(matrix_multiply(conjugator, matrix), matrix_inverse(conjugator))
                       for matrix in (A_MATRIX, B_MATRIX))
        if actual != expected:
            raise AssertionError("the explicit GL2 symmetry action drifted")
    matrices = {"a": A_MATRIX, "b": B_MATRIX, "D": D_MATRIX, "J": J_MATRIX,
                "relator": word_matrix(RELATOR), "U": word_matrix(U_WORD),
                "V": word_matrix(V_WORD), "V_inverse": word_matrix(V_WORD[::-1].swapcase())}
    if (trace(matrices["U"]), trace(matrices["V"]), trace(matrices["V_inverse"])) != (229, 272, 272):
        raise AssertionError("the mod-313 endpoint traces drifted")
    maps = []
    for name, images in MAPS:
        relator_image = mapped_word(RELATOR, images)
        matches = [{"sign": sign, "rotation": cut}
                   for sign, word in ((1, RELATOR), (-1, RELATOR[::-1].swapcase()))
                   for cut in range(len(word)) if relator_image == word[cut:] + word[:cut]]
        u_image = mapped_word(U_WORD, images)
        matrix = word_matrix(u_image)
        if trace(matrix) != 229 or determinant(matrix) != 1:
            raise AssertionError("the proposed map endpoint image drifted")
        generator_matrices = tuple(word_matrix(images[letter]) for letter in "ab")
        if any(determinant(value) != 1 for value in generator_matrices):
            raise AssertionError("a mapped generator lost determinant one")
        maps.append({"name": name, "images": images, "relator_image": relator_image,
                     "cyclic_relator_matches": matches, "cyclic_relator_preserved": bool(matches),
                     "generator_matrices": generator_matrices, "U_image": u_image,
                     "U_matrix": matrix, "U_trace": trace(matrix)})
    return {"prime": PRIME, "s": 3, "words": {"R": RELATOR, "U": U_WORD, "V": V_WORD},
            "matrices": matrices, "traces": {name: trace(matrix) for name, matrix in matrices.items()},
            "determinants": {name: determinant(matrix) for name, matrix in matrices.items()},
            "maps": maps, "status": "ONLY_FOUR_PROPOSED_MAPS_DO_NOT_GIVE_ENDPOINT_CONJUGACY",
            "full_automorphism_classification_claimed": False, "ac_conclusion_claimed": False}


if __name__ == "__main__":
    print(json.dumps(data(), sort_keys=True))
