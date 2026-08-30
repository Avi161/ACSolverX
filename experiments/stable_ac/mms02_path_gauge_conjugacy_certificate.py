"""Exact conjugacy gate for the MMS02 path-gauge pair."""

from __future__ import annotations

from dataclasses import dataclass

A_WORD = "xzYXyxZXYxyZ"
U_WORD = "zYX"
V_WORD = "Xyz"
BASE_RELATOR = "bdAbDBaD"
SOURCE_NORMAL = "yaD"
TARGET_NORMAL = "yAd"


def inverse(word: str) -> str:
    return word[::-1].swapcase()


def free_reduce(word: str) -> str:
    reduced = []
    for letter in word:
        if reduced and reduced[-1] == letter.swapcase():
            reduced.pop()
        else:
            reduced.append(letter)
    return "".join(reduced)


def substitute(word: str, images: dict[str, str]) -> str:
    expanded = []
    for letter in word:
        image = images[letter.lower()]
        expanded.append(image if letter.islower() else inverse(image))
    return free_reduce("".join(expanded))


def exponent_vector(word: str, generators: str) -> tuple[int, ...]:
    return tuple(word.count(generator) - word.count(generator.upper()) for generator in generators)


def quotient_abelianization(word: str) -> tuple[int, int]:
    x_exponent, y_exponent, z_exponent = exponent_vector(word, "xyz")
    return x_exponent + z_exponent, y_exponent


def base_abelianization(word: str) -> tuple[int, int]:
    a_exponent, b_exponent, d_exponent = exponent_vector(word, "abd")
    return a_exponent, b_exponent + d_exponent


ClassTwo = tuple[int, int, int]
RankThreeClassTwo = tuple[int, int, int, int, int, int]


def rank_three_class_two_coordinate(word: str) -> RankThreeClassTwo:
    generators = "xyz"
    exponents = [0, 0, 0]
    commutators = [0, 0, 0]
    pairs = ((0, 1), (0, 2), (1, 2))
    for letter in word:
        index = generators.index(letter.lower())
        sign = 1 if letter.islower() else -1
        for pair_index, (left, right) in enumerate(pairs):
            if left == index:
                commutators[pair_index] -= sign * exponents[right]
        exponents[index] += sign
    return tuple(exponents + commutators)


def class_two_multiply(left: ClassTwo, right: ClassTwo) -> ClassTwo:
    left_x, left_y, left_commutator = left
    right_x, right_y, right_commutator = right
    return (
        left_x + right_x,
        left_y + right_y,
        left_commutator + right_commutator - left_y * right_x,
    )


def class_two_inverse(element: ClassTwo) -> ClassTwo:
    x_exponent, y_exponent, commutator_exponent = element
    return (
        -x_exponent,
        -y_exponent,
        -commutator_exponent - x_exponent * y_exponent,
    )


def class_two_word(word: str) -> ClassTwo:
    images: dict[str, ClassTwo] = {
        "x": (1, 0, 0),
        "y": (0, 1, 0),
        "z": (1, 0, 0),
    }
    result = (0, 0, 0)
    for letter in word:
        image = images[letter.lower()]
        if letter.isupper():
            image = class_two_inverse(image)
        result = class_two_multiply(result, image)
    return result


def class_two_conjugate(conjugator: str, word: str) -> ClassTwo:
    return class_two_word(conjugator + word + inverse(conjugator))


@dataclass(frozen=True)
class PathGaugeConjugacyDecision:
    source_abelianization: tuple[int, int]
    target_abelianization: tuple[int, int]
    base_relator: str
    source_normal: str
    target_normal: str
    forced_b_power: int
    forced_base_conjugator: str
    forced_condition_defect: str
    free_factor_defect: str
    rank_three_relator_coordinate: RankThreeClassTwo
    class_two_source: ClassTwo
    class_two_target: ClassTwo
    class_two_forced_conjugate: ClassTwo
    verdict: str


def decide_path_gauge_conjugacy() -> PathGaugeConjugacyDecision:
    original_images = {"a": "Yxy", "b": "x", "d": "z", "y": "y"}
    if substitute(BASE_RELATOR, original_images) != A_WORD:
        raise AssertionError("the Magnus base relator drifted")
    if substitute(SOURCE_NORMAL, original_images) != inverse(U_WORD):
        raise AssertionError("the source HNN normal form drifted")
    if substitute(TARGET_NORMAL, original_images) != V_WORD:
        raise AssertionError("the target HNN normal form drifted")

    if exponent_vector(BASE_RELATOR, "abd") != (0, 1, -1):
        raise AssertionError("the Magnus base abelian relation drifted")
    source_tail = "aD"
    target_tail = "Ad"
    forced_b_power = 2
    condition_left = source_tail + "b" * forced_b_power + inverse(target_tail)
    condition_right = "a" * forced_b_power
    if base_abelianization(condition_left) != base_abelianization(condition_right):
        raise AssertionError("the forced Collins exponent no longer solves abelianization")
    if base_abelianization(condition_left) != (2, 0):
        raise AssertionError("the forced Collins abelian class drifted")
    forced_base_conjugator = "B" * forced_b_power
    forced_condition_defect = free_reduce(
        condition_left + inverse(condition_right)
    )
    free_factor_defect = free_reduce("A" + forced_condition_defect + "a")
    if forced_condition_defect != "aDbbDA":
        raise AssertionError("the forced Collins condition defect drifted")
    if free_factor_defect != "DbbD":
        raise AssertionError("the free-factor defect drifted")

    if quotient_abelianization(A_WORD) != (0, 0):
        raise AssertionError("the path-gauge relator abelianization drifted")
    if quotient_abelianization(U_WORD) != (0, -1):
        raise AssertionError("the source row abelianization drifted")
    if quotient_abelianization(inverse(U_WORD)) != quotient_abelianization(V_WORD):
        raise AssertionError("row inversion no longer gives the only abelian orientation")

    rank_three_relator_coordinate = rank_three_class_two_coordinate(A_WORD)
    if rank_three_class_two_coordinate("XYxy") != (0, 0, 0, 1, 0, 0):
        raise AssertionError("the rank-three commutator convention drifted")
    if rank_three_relator_coordinate != (1, 0, -1, 0, 0, 0):
        raise AssertionError("the literal rank-three class-two relator drifted")
    if class_two_word("XYxy") != (0, 0, 1):
        raise AssertionError("the class-two commutator convention drifted")
    if class_two_word(A_WORD) != (0, 0, 0):
        raise AssertionError("the class-two relator substitution drifted")
    class_two_source = class_two_word(inverse(U_WORD))
    class_two_target = class_two_word(V_WORD)
    class_two_forced_conjugate = class_two_conjugate("XX", inverse(U_WORD))
    if (class_two_source, class_two_target) != ((0, 1, 1), (0, 1, -1)):
        raise AssertionError("the class-two endpoint pair drifted")
    if class_two_forced_conjugate != (0, 1, -1):
        raise AssertionError("the forced base conjugator image drifted")
    if class_two_forced_conjugate != class_two_target:
        raise AssertionError("the class-two shadow no longer selects the forced conjugator")

    return PathGaugeConjugacyDecision(
        source_abelianization=quotient_abelianization(U_WORD),
        target_abelianization=quotient_abelianization(V_WORD),
        base_relator=BASE_RELATOR,
        source_normal=SOURCE_NORMAL,
        target_normal=TARGET_NORMAL,
        forced_b_power=forced_b_power,
        forced_base_conjugator=forced_base_conjugator,
        forced_condition_defect=forced_condition_defect,
        free_factor_defect=free_factor_defect,
        rank_three_relator_coordinate=rank_three_relator_coordinate,
        class_two_source=class_two_source,
        class_two_target=class_two_target,
        class_two_forced_conjugate=class_two_forced_conjugate,
        verdict="PATH_GAUGE_ROWS_NOT_CONJUGATE_UP_TO_INVERSION",
    )


if __name__ == "__main__":
    print(decide_path_gauge_conjugacy())
