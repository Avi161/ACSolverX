"""Finite mod-23 matrix witness for the literal six-three endpoint words."""

import json

PRIME = 23
IDENTITY = (1, 0, 0, 1)
A_MATRIX = (1, 1, 0, 1)
B_MATRIX = (1, 0, 21, 1)
W_WORD = "baBABabABAba"
U_WORD = "AABAbABabaBAbabABAbaa"
V_WORD = "AABabABabaBABabABAbaa"


def determinant(matrix):
    a, b, c, d = matrix
    return (a * d - b * c) % PRIME


def matrix_multiply(left, right):
    a, b, c, d = left
    e, f, g, h = right
    return tuple(value % PRIME for value in (a * e + b * g, a * f + b * h,
                                            c * e + d * g, c * f + d * h))


def matrix_inverse(matrix):
    if determinant(matrix) != 1:
        raise ValueError("the modular inverse requires determinant one")
    a, b, c, d = matrix
    return (d % PRIME, -b % PRIME, -c % PRIME, a % PRIME)


def word_matrix(word, s=2):
    b_matrix = (1, 0, -s % PRIME, 1)
    images = {"a": A_MATRIX, "b": b_matrix,
              "A": matrix_inverse(A_MATRIX), "B": matrix_inverse(b_matrix)}
    value = IDENTITY
    for letter in word:
        value = matrix_multiply(value, images[letter])
    return value


def data():
    relator = "a" + W_WORD + "B" + W_WORD[::-1].swapcase()
    matrices = {"a": A_MATRIX, "b": B_MATRIX, "w": word_matrix(W_WORD),
                "relator": word_matrix(relator), "U": word_matrix(U_WORD), "V": word_matrix(V_WORD)}
    traces = {name: (matrix[0] + matrix[3]) % PRIME for name, matrix in matrices.items()}
    determinants = {name: determinant(matrix) for name, matrix in matrices.items()}
    if matrices["relator"] != IDENTITY or matrix_multiply(A_MATRIX, matrices["w"]) != matrix_multiply(matrices["w"], B_MATRIX):
        raise AssertionError("the mod-23 six-three relation drifted")
    if traces["U"] != 11 or traces["V"] != 11 or any(value != 1 for value in determinants.values()):
        raise AssertionError("the mod-23 endpoint matrix invariants drifted")
    return {"prime": PRIME, "s": 2, "matrix_entry_order": ["00", "01", "10", "11"],
            "words": {"w": W_WORD, "U": U_WORD, "V": V_WORD, "relator": relator},
            "matrices": matrices, "traces": traces, "determinants": determinants}


if __name__ == "__main__":
    print(json.dumps(data(), sort_keys=True))
