"""Class-two obstruction to one canonical MMS02 signed-lift branch."""

from __future__ import annotations

from dataclasses import dataclass

from experiments.stable_ac.mms02_depth_five_lift_equations_certificate import (
    EXPECTED_D2_WORD,
    EXPECTED_ENDPOINT_BASE_WORDS,
    EXPECTED_M_MINUS_I_INVERSE,
    EXPECTED_MONODROMY_MATRIX,
    IndexedWord,
    apply_indexed_images,
    inverse_indexed_word,
    reduce_indexed_word,
)

Vector4 = tuple[int, int, int, int]
Wedge6 = tuple[int, int, int, int, int, int]
ClassTwoCoordinate = tuple[Vector4, Wedge6]

BASIS = (-2, -1, 0, 1)
ZERO_VECTOR: Vector4 = (0, 0, 0, 0)
ZERO_WEDGE: Wedge6 = (0, 0, 0, 0, 0, 0)
EXPECTED_A_WEDGE: Wedge6 = (0, -2, 1, 2, -2, 0)
EXPECTED_B_WEDGE: Wedge6 = (0, 4, -3, -6, 6, -6)
EXPECTED_W_WEDGE: Wedge6 = (-1, -1, -1, 3, 3, -5)
EXPECTED_D_VECTOR: Vector4 = (-5, 12, -16, 2)
EXPECTED_D_WEDGE: Wedge6 = (-6, -10, -8, 30, 22, -44)
EXPECTED_T_VECTOR: Vector4 = (-3, 10, -17, 9)
EXPECTED_RESIDUAL: Wedge6 = (-11, 25, -24, -31, 55, -62)


def add_vector(left: Vector4, right: Vector4) -> Vector4:
    return tuple(left[index] + right[index] for index in range(4))


def scale_vector(scale: int, value: Vector4) -> Vector4:
    return tuple(scale * coordinate for coordinate in value)


def add_wedge(left: Wedge6, right: Wedge6) -> Wedge6:
    return tuple(left[index] + right[index] for index in range(6))


def scale_wedge(scale: int, value: Wedge6) -> Wedge6:
    return tuple(scale * coordinate for coordinate in value)


def wedge(left: Vector4, right: Vector4) -> Wedge6:
    return (
        left[0] * right[1] - left[1] * right[0],
        left[0] * right[2] - left[2] * right[0],
        left[0] * right[3] - left[3] * right[0],
        left[1] * right[2] - left[2] * right[1],
        left[1] * right[3] - left[3] * right[1],
        left[2] * right[3] - left[3] * right[2],
    )


def basis_vector(index: int, sign: int = 1) -> Vector4:
    coordinates = [0, 0, 0, 0]
    coordinates[BASIS.index(index)] = sign
    return tuple(coordinates)


def class_two_coordinate(word: IndexedWord) -> ClassTwoCoordinate:
    vector = ZERO_VECTOR
    omega = ZERO_WEDGE
    for index, sign in word:
        letter = basis_vector(index, sign)
        omega = add_wedge(omega, wedge(vector, letter))
        vector = add_vector(vector, letter)
    return vector, omega


def multiply_words(*words: IndexedWord) -> IndexedWord:
    return reduce_indexed_word(tuple(letter for word in words for letter in word))


PHI_IMAGES: dict[int, IndexedWord] = {
    -2: ((-1, 1),),
    -1: ((0, 1),),
    0: ((1, 1),),
    1: EXPECTED_D2_WORD,
}


def phi_word(word: IndexedWord) -> IndexedWord:
    return apply_indexed_images(word, PHI_IMAGES)


def phi_power_word(word: IndexedWord, power: int) -> IndexedWord:
    if power < 0:
        raise ValueError("this certificate needs only nonnegative powers")
    result = word
    for _ in range(power):
        result = phi_word(result)
    return result


def matrix_vector(value: Vector4) -> Vector4:
    return tuple(
        sum(EXPECTED_MONODROMY_MATRIX[row][column] * value[column] for column in range(4))
        for row in range(4)
    )


def exterior_monodromy(value: Wedge6) -> Wedge6:
    result = ZERO_WEDGE
    wedge_pairs = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))
    columns = tuple(
        tuple(EXPECTED_MONODROMY_MATRIX[row][column] for row in range(4))
        for column in range(4)
    )
    for coefficient, (left, right) in zip(value, wedge_pairs, strict=True):
        result = add_wedge(
            result,
            scale_wedge(coefficient, wedge(columns[left], columns[right])),
        )
    return result


def phi_coordinate(coordinate: ClassTwoCoordinate) -> ClassTwoCoordinate:
    vector, omega = coordinate
    return (
        matrix_vector(vector),
        add_wedge(exterior_monodromy(omega), scale_wedge(vector[3], EXPECTED_W_WEDGE)),
    )


def invariant(value: Wedge6) -> int:
    return value[1] + 3 * value[2] + value[4]


def solve_t_vector(target: Vector4, source: Vector4) -> Vector4:
    difference = tuple(target[index] - source[index] for index in range(4))
    return tuple(
        -sum(EXPECTED_M_MINUS_I_INVERSE[row][column] * difference[column] for column in range(4))
        for row in range(4)
    )


@dataclass(frozen=True)
class FixedBranchClassTwoDecision:
    endpoint_vectors: tuple[Vector4, Vector4]
    endpoint_wedges: tuple[Wedge6, Wedge6]
    monodromy_generator_wedge: Wedge6
    twisted_source_vector: Vector4
    twisted_source_wedge: Wedge6
    forced_conjugator_vector: Vector4
    central_residual: Wedge6
    image_invariant_values: tuple[int, ...]
    residual_invariant: int
    verdict: str


def decide_fixed_branch_class_two() -> FixedBranchClassTwoDecision:
    a_word, b_word = EXPECTED_ENDPOINT_BASE_WORDS
    a_coordinate = class_two_coordinate(a_word)
    b_coordinate = class_two_coordinate(b_word)
    w_coordinate = class_two_coordinate(EXPECTED_D2_WORD)
    if a_coordinate[1] != EXPECTED_A_WEDGE:
        raise AssertionError("the source endpoint class-two coordinate drifted")
    if b_coordinate[1] != EXPECTED_B_WEDGE:
        raise AssertionError("the target endpoint class-two coordinate drifted")
    if w_coordinate[1] != EXPECTED_W_WEDGE:
        raise AssertionError("the nonlinear monodromy coordinate drifted")

    for word in (a_word, b_word, EXPECTED_D2_WORD):
        if class_two_coordinate(phi_word(word)) != phi_coordinate(
            class_two_coordinate(word)
        ):
            raise AssertionError("the word and exterior monodromy engines disagree")

    d2_word = EXPECTED_D2_WORD
    d3_word = phi_word(d2_word)
    d4_word = phi_word(d3_word)
    p_word = multiply_words(d3_word, inverse_indexed_word(d4_word))
    k_word = multiply_words(d3_word, inverse_indexed_word(d2_word))
    if phi_word(k_word) != inverse_indexed_word(p_word):
        raise AssertionError("the collapsed x inverse transport drifted")

    a0_word = phi_power_word(a_word, 3)
    b0_word = phi_power_word(b_word, 2)
    c0_word = multiply_words(
        a0_word,
        phi_word(b0_word),
        phi_word(inverse_indexed_word(a0_word)),
        inverse_indexed_word(b0_word),
    )
    d0_word = multiply_words(
        a0_word,
        inverse_indexed_word(p_word),
        c0_word,
        p_word,
    )

    q_word = multiply_words(EXPECTED_D2_WORD, ((1, -1),))
    c_hat = multiply_words(
        phi_word(a_word),
        phi_word(b_word),
        phi_power_word(inverse_indexed_word(a_word), 2),
        inverse_indexed_word(b_word),
    )
    d_hat = multiply_words(
        phi_word(a_word),
        q_word,
        c_hat,
        inverse_indexed_word(q_word),
    )
    if phi_power_word(d_hat, 2) != d0_word:
        raise AssertionError("the normalized canonical branch transport drifted")
    d_vector, d_wedge = class_two_coordinate(d_hat)
    if d_vector != EXPECTED_D_VECTOR or d_wedge != EXPECTED_D_WEDGE:
        raise AssertionError("the canonical twisted source coordinate drifted")

    t_vector = solve_t_vector(b_coordinate[0], d_vector)
    if t_vector != EXPECTED_T_VECTOR:
        raise AssertionError("the forced twisted conjugator vector drifted")
    if add_vector(d_vector, add_vector(t_vector, scale_vector(-1, matrix_vector(t_vector)))) != b_coordinate[0]:
        raise AssertionError("the forced exponent equation stopped replaying")

    residual = add_wedge(
        add_wedge(
            add_wedge(
                b_coordinate[1],
                scale_wedge(-1, d_wedge),
            ),
            scale_wedge(-1, wedge(t_vector, d_vector)),
        ),
        add_wedge(
            scale_wedge(t_vector[3], EXPECTED_W_WEDGE),
            wedge(add_vector(t_vector, d_vector), matrix_vector(t_vector)),
        ),
    )
    if residual != EXPECTED_RESIDUAL:
        raise AssertionError("the central twisted-conjugacy residual drifted")

    wedge_basis = tuple(
        tuple(1 if index == basis_index else 0 for index in range(6))
        for basis_index in range(6)
    )
    image_invariants = tuple(
        invariant(add_wedge(value, scale_wedge(-1, exterior_monodromy(value))))
        for value in wedge_basis
    )
    if image_invariants != (0, 0, 0, 0, 0, 0):
        raise AssertionError("the obstruction covector stopped killing im(I-L)")
    residual_invariant = invariant(residual)
    if residual_invariant != 8:
        raise AssertionError("the canonical class-two obstruction drifted")

    return FixedBranchClassTwoDecision(
        endpoint_vectors=(a_coordinate[0], b_coordinate[0]),
        endpoint_wedges=(a_coordinate[1], b_coordinate[1]),
        monodromy_generator_wedge=w_coordinate[1],
        twisted_source_vector=d_vector,
        twisted_source_wedge=d_wedge,
        forced_conjugator_vector=t_vector,
        central_residual=residual,
        image_invariant_values=image_invariants,
        residual_invariant=residual_invariant,
        verdict="CANONICAL_G_V_H_X_J_U_INVERSE_BRANCH_OBSTRUCTED_IN_BASE_CLASS_TWO",
    )


if __name__ == "__main__":
    print(decide_fixed_branch_class_two())
