"""Class-two obstruction for the fixed-row terminal MMS02 reduction."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations


Word = tuple[int, ...]
Matrix = tuple[tuple[int, ...], ...]

W = "YxyxY"
C = "yXYxy"
D0 = "XyXYXyxYxy"
BASE_CHANGE = {"x": "x", "y": "xy"}

EXPECTED_R = "XyXYXyxYxyxYXyXYxyxYxyXYXy"
EXPECTED_E_SOURCE = "YXyXYxyxYxx"
EXPECTED_E_TARGET = "YXyXYxyxYxyXYxy"
EXPECTED_TRANSFORMED = (
    "yXYXyxYxyxYXyXYxyxYxyXYXy",
    "YXyXYxyxYx",
    "YXyXYxyxYxyXYxy",
)

EXPECTED_MAGNUS_RELATOR = (
    3,
    -2,
    1,
    -2,
    3,
    -4,
    3,
    -2,
    3,
    -4,
    5,
    -4,
    3,
)
EXPECTED_Y2_WORD = (4, -3, 2, -3, 4, -3, 2, -1, 2, -3, -3, 4)
EXPECTED_P_SOURCE = (-3, 2, -1, 2, -3)
EXPECTED_P_TARGET = (-3, 2, -1, 2, -3, 4, -3, 4)
EXPECTED_PHI_MATRIX = (
    (0, 0, 0, -1),
    (1, 0, 0, 3),
    (0, 1, 0, -5),
    (0, 0, 1, 3),
)
EXPECTED_AB_SOLUTION = (1, -2, 4, -1)
EXPECTED_CLASS2_DEFECT = (0, -2, -2, 6, 6, -11)
EXPECTED_EXTERIOR_MATRIX = (
    (-1, 0, 1, 0, 0, 0),
    (0, -1, 0, 0, 1, 0),
    (0, 0, -1, 0, 0, 1),
    (1, 0, -5, -1, -3, 0),
    (0, 1, 3, 0, -1, -3),
    (0, 0, 0, 1, 3, 4),
)
ANNIHILATORS = (
    (0, 1, 3, 0, 1, 0),
    (1, 0, -4, 1, 0, 1),
)


@dataclass(frozen=True)
class TerminalFixedRowDecision:
    rank_two_pair_source: tuple[str, str]
    rank_two_pair_target: tuple[str, str]
    transformed_words: tuple[str, str, str]
    magnus_relator: Word
    solved_y2: Word
    phi_matrix: Matrix
    phi_minus_identity_determinant: int
    abelian_difference: tuple[int, int, int, int]
    abelian_solution: tuple[int, int, int, int]
    class_two_defect: tuple[int, int, int, int, int, int]
    exterior_matrix: Matrix
    annihilators: tuple[tuple[int, ...], ...]
    obstruction_values: tuple[int, int]
    verdict: str


def inverse_string(word: str) -> str:
    return word[::-1].swapcase()


def free_reduce_string(word: str) -> str:
    reduced: list[str] = []
    for letter in word:
        if reduced and reduced[-1] == letter.swapcase():
            reduced.pop()
        else:
            reduced.append(letter)
    return "".join(reduced)


def apply_images(word: str, images: dict[str, str]) -> str:
    return free_reduce_string(
        "".join(
            images[letter]
            if letter.islower()
            else inverse_string(images[letter.lower()])
            for letter in word
        )
    )


def inverse(word: Word) -> Word:
    return tuple(-letter for letter in reversed(word))


def free_reduce(word: Word) -> Word:
    reduced: list[int] = []
    for letter in word:
        if reduced and reduced[-1] == -letter:
            reduced.pop()
        else:
            reduced.append(letter)
    return tuple(reduced)


def substitute(word: Word, images: dict[int, Word]) -> Word:
    signed_images = dict(images)
    signed_images.update(
        {-generator: inverse(image) for generator, image in images.items()}
    )
    return free_reduce(
        tuple(letter for symbol in word for letter in signed_images[symbol])
    )


def magnus_occurrences(word: str) -> tuple[Word, int]:
    height = 0
    occurrences: list[int] = []
    for letter in word:
        if letter == "x":
            height += 1
        elif letter == "X":
            height -= 1
        else:
            index = height + 3
            occurrences.append(index if letter == "y" else -index)
    return tuple(occurrences), height


def abelian_vector(word: Word) -> tuple[int, int, int, int]:
    return tuple(
        sum(1 if letter == generator else -1 if letter == -generator else 0
            for letter in word)
        for generator in range(1, 5)
    )


def image_matrix(images: dict[int, Word]) -> Matrix:
    columns = tuple(abelian_vector(images[index]) for index in range(1, 5))
    return tuple(tuple(columns[column][row] for column in range(4)) for row in range(4))


def matrix_vector(matrix: Matrix, vector: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(
        sum(matrix[row][column] * vector[column] for column in range(len(vector)))
        for row in range(len(matrix))
    )


def determinant(matrix: Matrix) -> int:
    size = len(matrix)
    total = 0
    for permutation in permutations(range(size)):
        inversions = sum(
            permutation[left] > permutation[right]
            for left in range(size)
            for right in range(left + 1, size)
        )
        product = 1
        for row in range(size):
            product *= matrix[row][permutation[row]]
        total += (-1 if inversions % 2 else 1) * product
    return total


def magnus_degree_two(word: Word) -> tuple[tuple[int, ...], tuple[int, ...]]:
    polynomial: dict[tuple[int, ...], int] = {(): 1}
    for letter in word:
        generator = abs(letter)
        factor = (
            {(): 1, (generator,): 1}
            if letter > 0
            else {(): 1, (generator,): -1, (generator, generator): 1}
        )
        product: dict[tuple[int, ...], int] = {}
        for left, left_coefficient in polynomial.items():
            for right, right_coefficient in factor.items():
                if len(left) + len(right) <= 2:
                    monomial = left + right
                    product[monomial] = (
                        product.get(monomial, 0)
                        + left_coefficient * right_coefficient
                    )
        polynomial = {
            monomial: coefficient
            for monomial, coefficient in product.items()
            if coefficient
        }
    linear = tuple(polynomial.get((index,), 0) for index in range(1, 5))
    quadratic = tuple(
        polynomial.get((left, right), 0)
        for left in range(1, 5)
        for right in range(1, 5)
    )
    return linear, quadratic


def exterior_vector(word: Word) -> tuple[int, int, int, int, int, int]:
    linear, quadratic = magnus_degree_two(word)
    if linear != (0, 0, 0, 0):
        raise AssertionError("the exterior coordinate requires zero linear part")
    matrix = tuple(tuple(quadratic[4 * row + column] for column in range(4)) for row in range(4))
    if any(matrix[index][index] for index in range(4)):
        raise AssertionError("a class-two kernel word has a diagonal term")
    if any(matrix[i][j] != -matrix[j][i] for i in range(4) for j in range(4)):
        raise AssertionError("the degree-two kernel tensor is not alternating")
    return tuple(matrix[i][j] for i in range(4) for j in range(i + 1, 4))


def exterior_matrix(matrix: Matrix) -> Matrix:
    pairs = tuple((i, j) for i in range(4) for j in range(i + 1, 4))
    result = []
    for row_pair in pairs:
        p, q = row_pair
        row = []
        for column_pair in pairs:
            i, j = column_pair
            coefficient = (
                matrix[p][i] * matrix[q][j]
                - matrix[q][i] * matrix[p][j]
            )
            if row_pair == column_pair:
                coefficient -= 1
            row.append(coefficient)
        result.append(tuple(row))
    return tuple(result)


def decide_terminal_fixed_row_class2() -> TerminalFixedRowDecision:
    rank_two_relator = free_reduce_string(D0 + "x" + inverse_string(D0) + inverse_string(W))
    source_row = free_reduce_string(inverse_string(D0) + "x")
    target_row = free_reduce_string(inverse_string(D0) + C)
    if (rank_two_relator, source_row, target_row) != (
        EXPECTED_R,
        EXPECTED_E_SOURCE,
        EXPECTED_E_TARGET,
    ):
        raise AssertionError("the stable-letter cancellation reduction drifted")

    transformed = tuple(
        apply_images(word, BASE_CHANGE)
        for word in (rank_two_relator, source_row, target_row)
    )
    if transformed != EXPECTED_TRANSFORMED:
        raise AssertionError("the rank-two base change drifted")

    relator_occurrences, relator_height = magnus_occurrences(transformed[0])
    source_occurrences, source_height = magnus_occurrences(transformed[1])
    target_occurrences, target_height = magnus_occurrences(transformed[2])
    if (relator_occurrences, relator_height) != (EXPECTED_MAGNUS_RELATOR, 0):
        raise AssertionError("the Magnus relator drifted")
    if (source_occurrences, source_height) != (EXPECTED_P_SOURCE, 1):
        raise AssertionError("the source Magnus row drifted")
    if (target_occurrences, target_height) != (EXPECTED_P_TARGET, 1):
        raise AssertionError("the target Magnus row drifted")

    position = relator_occurrences.index(5)
    if relator_occurrences.count(5) != 1 or -5 in relator_occurrences:
        raise AssertionError("the extremal Magnus generator is not uniquely positive")
    solved_y2 = free_reduce(
        inverse(relator_occurrences[:position])
        + inverse(relator_occurrences[position + 1 :])
    )
    if solved_y2 != EXPECTED_Y2_WORD:
        raise AssertionError("the solved extremal Magnus generator drifted")
    if sum(abs(letter) == 1 for letter in solved_y2) != 1:
        raise AssertionError("the last shift image is not visibly relative primitive")

    phi_images = {1: (2,), 2: (3,), 3: (4,), 4: solved_y2}
    phi_matrix = image_matrix(phi_images)
    if phi_matrix != EXPECTED_PHI_MATRIX:
        raise AssertionError("the rank-four shift matrix drifted")
    phi_minus_identity = tuple(
        tuple(phi_matrix[row][column] - (row == column) for column in range(4))
        for row in range(4)
    )
    phi_minus_identity_determinant = determinant(phi_minus_identity)
    if phi_minus_identity_determinant != 1:
        raise AssertionError("the abelian twisted equation is not uniquely soluble")

    abelian_difference = tuple(
        target - source
        for source, target in zip(
            abelian_vector(source_occurrences),
            abelian_vector(target_occurrences),
            strict=True,
        )
    )
    if matrix_vector(phi_minus_identity, EXPECTED_AB_SOLUTION) != abelian_difference:
        raise AssertionError("the pinned abelian solution does not solve the equation")

    k0 = (1, -2, -2, 3, 3, 3, 3, -4)
    if abelian_vector(k0) != EXPECTED_AB_SOLUTION:
        raise AssertionError("the collected abelian lift drifted")
    defect_word = free_reduce(
        inverse(k0)
        + source_occurrences
        + substitute(k0, phi_images)
        + inverse(target_occurrences)
    )
    class_two_defect = exterior_vector(defect_word)
    if class_two_defect != EXPECTED_CLASS2_DEFECT:
        raise AssertionError("the class-two twisted defect drifted")

    correction_matrix = exterior_matrix(phi_matrix)
    if correction_matrix != EXPECTED_EXTERIOR_MATRIX:
        raise AssertionError("the exterior correction matrix drifted")
    obstruction_values = tuple(
        sum(functional[index] * class_two_defect[index] for index in range(6))
        for functional in ANNIHILATORS
    )
    for functional in ANNIHILATORS:
        if any(
            sum(functional[row] * correction_matrix[row][column] for row in range(6))
            for column in range(6)
        ):
            raise AssertionError("an obstruction functional does not kill every correction")
    if obstruction_values != (-2, 3):
        raise AssertionError("the class-two obstruction values drifted")

    return TerminalFixedRowDecision(
        rank_two_pair_source=(rank_two_relator, source_row),
        rank_two_pair_target=(rank_two_relator, target_row),
        transformed_words=transformed,
        magnus_relator=relator_occurrences,
        solved_y2=solved_y2,
        phi_matrix=phi_matrix,
        phi_minus_identity_determinant=phi_minus_identity_determinant,
        abelian_difference=abelian_difference,
        abelian_solution=EXPECTED_AB_SOLUTION,
        class_two_defect=class_two_defect,
        exterior_matrix=correction_matrix,
        annihilators=ANNIHILATORS,
        obstruction_values=obstruction_values,
        verdict="NO_FIXED_R_RELATIVE_AC_PATH",
    )


if __name__ == "__main__":
    print(decide_terminal_fixed_row_class2())
