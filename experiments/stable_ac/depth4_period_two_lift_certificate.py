from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass


Word = tuple[int, ...]
ModuleVector = dict[Word, int]
GroupRing = dict[Word, int]


def reduce_word(word: Word) -> Word:
    reduced: list[int] = []
    for letter in word:
        if reduced and reduced[-1] == -letter:
            reduced.pop()
        else:
            reduced.append(letter)
    return tuple(reduced)


def inverse(word: Word) -> Word:
    return tuple(-letter for letter in reversed(word))


def multiply(*words: Word) -> Word:
    return reduce_word(tuple(letter for word in words for letter in word))


def conjugate(word: Word, conjugator: Word) -> Word:
    return multiply(conjugator, word, inverse(conjugator))


def power(letter: int, exponent: int) -> Word:
    return (letter if exponent >= 0 else -letter,) * abs(exponent)


def quotient_append(word: Word, letter: int) -> Word:
    quotient_letter = abs(letter) if abs(letter) == C else letter
    if word and abs(quotient_letter) == C and abs(word[-1]) == C:
        return word[:-1]
    if word and word[-1] == -quotient_letter:
        return word[:-1]
    return word + (quotient_letter,)


def quotient_reduce(word: Word) -> Word:
    reduced: Word = ()
    for letter in word:
        reduced = quotient_append(reduced, letter)
    return reduced


def quotient_inverse(word: Word) -> Word:
    return quotient_reduce(tuple(-letter for letter in reversed(word)))


def quotient_multiply(*words: Word) -> Word:
    return quotient_reduce(tuple(letter for word in words for letter in word))


def c_vertex(word: Word) -> Word:
    reduced = quotient_reduce(word)
    if reduced and abs(reduced[-1]) == C:
        return reduced[:-1]
    return reduced


def clean_vector(values: dict[Word, int]) -> ModuleVector:
    return {c_vertex(word): coefficient for word, coefficient in values.items() if coefficient}


def relation_module(word: Word) -> ModuleVector:
    quotient_prefix: Word = ()
    values: dict[Word, int] = defaultdict(int)
    for letter in word:
        if letter == C and quotient_prefix and abs(quotient_prefix[-1]) == C:
            values[quotient_prefix[:-1]] += 1
        elif letter == -C and not (
            quotient_prefix and abs(quotient_prefix[-1]) == C
        ):
            values[quotient_prefix] -= 1
        quotient_prefix = quotient_append(quotient_prefix, letter)
    assert quotient_prefix == ()
    return clean_vector(values)


def group_ring(*terms: tuple[int, Word]) -> GroupRing:
    values: dict[Word, int] = defaultdict(int)
    for coefficient, word in terms:
        values[quotient_reduce(word)] += coefficient
    return {word: coefficient for word, coefficient in values.items() if coefficient}


def add_group_ring(*values: GroupRing) -> GroupRing:
    return group_ring(*(
        (coefficient, word)
        for value in values
        for word, coefficient in value.items()
    ))


def multiply_group_ring(left: GroupRing, right: GroupRing) -> GroupRing:
    return group_ring(*(
        (left_coefficient * right_coefficient, quotient_multiply(left_word, right_word))
        for left_word, left_coefficient in left.items()
        for right_word, right_coefficient in right.items()
    ))


def add_vectors(*values: ModuleVector) -> ModuleVector:
    result: dict[Word, int] = defaultdict(int)
    for value in values:
        for module_vertex, coefficient in value.items():
            result[c_vertex(module_vertex)] += coefficient
    return clean_vector(result)


def scale_vector(value: ModuleVector, coefficient: int) -> ModuleVector:
    return clean_vector({word: coefficient * entry for word, entry in value.items()})


def apply_operator(operator: GroupRing, value: ModuleVector) -> ModuleVector:
    result: dict[Word, int] = defaultdict(int)
    for group_element, group_coefficient in operator.items():
        for module_vertex, module_coefficient in value.items():
            destination = c_vertex(quotient_multiply(group_element, module_vertex))
            result[destination] += group_coefficient * module_coefficient
    return clean_vector(result)


def literal(word: Word) -> str:
    alphabet = {C: "c", -C: "C", T: "t", -T: "T"}
    return "".join(alphabet[letter] for letter in word)


def parse_quotient(literal_word: str) -> Word:
    alphabet = {"c": C, "C": -C, "t": T, "T": -T}
    return c_vertex(tuple(alphabet[letter] for letter in literal_word))


def relation_generator(module_vertex: Word) -> Word:
    return multiply(module_vertex, power(C, 2), inverse(module_vertex))


def lift_module_vector(value: ModuleVector) -> Word:
    result: Word = ()
    for module_vertex, coefficient in sorted(
        value.items(), key=lambda item: (len(item[0]), item[0])
    ):
        result = multiply(result, power_word(relation_generator(module_vertex), coefficient))
    return result


def power_word(word: Word, exponent: int) -> Word:
    if exponent < 0:
        return power_word(inverse(word), -exponent)
    result: Word = ()
    for _ in range(exponent):
        result = multiply(result, word)
    return result


C = 1
T = 2
SOURCE_A = multiply(
    power(T, -1),
    power(C, 4),
    power(T, -1),
    power(C, 3),
    power(T, -1),
    power(C, 4),
    power(T, -1),
    power(C, -1),
    power(T, 1),
    power(C, -4),
    power(T, 1),
    power(C, -1),
)
SOURCE_B = multiply(
    power(T, -1),
    power(C, 4),
    power(T, -1),
    power(C, 4),
    power(T, -1),
    power(C, -1),
    power(T, 1),
    power(C, -3),
    power(T, 1),
    power(C, -1),
)
H0 = multiply(power(C, 1), power(T, -2), power(C, 1), power(T, 3))
H1: Word = ()
H2 = multiply(power(C, 1), power(T, -1), power(C, 1), power(T, 3))
H3 = power(T, 1)
TARGET = power(T, 1)


CORRECTION = (
    (0, 2, "cT"),
    (0, -2, "cTTct"),
    (0, -2, "cTTctt"),
    (2, -2, "cTct"),
    (2, -2, "cTctt"),
    (3, -2, ""),
    (3, -1, "TTct"),
    (4, 1, "Tct"),
)


@dataclass(frozen=True)
class PeriodTwoLiftCertificate:
    row_lengths: tuple[int, int, int, int, int]
    quotient_z_literal: str
    defect_vector: tuple[tuple[str, int], ...]
    defect_terms: int
    defect_l1: int
    defect_augmentation: int
    operator_term_counts: tuple[int, int, int, int, int]
    operator_augmentations: tuple[int, int, int, int, int]
    correction: tuple[tuple[int, int, str], ...]
    correction_l1: int
    corrected_defect: tuple[tuple[str, int], ...]
    corrected_direct_defect: tuple[tuple[str, int], ...]
    corrected_residual_length: int


def build_operators(
    r: Word,
    s: Word,
    u: Word,
) -> tuple[GroupRing, GroupRing, GroupRing, GroupRing, GroupRing]:
    q_a = quotient_reduce(SOURCE_A)
    q_b = quotient_reduce(SOURCE_B)
    q_r = quotient_reduce(r)
    q_s = quotient_reduce(s)
    q_u = quotient_reduce(u)
    q_x = quotient_multiply(quotient_reduce(H2), q_s, quotient_inverse(H2))
    one = group_ring((1, ()))
    d_r = group_ring((1, q_a), (-1, q_r))
    d_s_0 = multiply_group_ring(group_ring((-1, q_s)), d_r)
    d_s_1 = group_ring((1, q_b), (-1, q_s))
    bridge = group_ring(
        (1, quotient_reduce(H2)),
        (1, quotient_multiply(quotient_inverse(q_u), quotient_reduce(H3))),
    )
    return (
        add_group_ring(
            multiply_group_ring(
                group_ring((-1, quotient_inverse(q_u))),
                d_r,
            ),
            multiply_group_ring(bridge, d_s_0),
        ),
        multiply_group_ring(bridge, d_s_1),
        add_group_ring(one, group_ring((-1, q_x))),
        group_ring((1, quotient_inverse(q_u)), (-1, TARGET)),
        group_ring((1, TARGET), (-1, ())),
    )


def period_two_lift_certificate() -> PeriodTwoLiftCertificate:
    r = multiply(SOURCE_A, conjugate(inverse(SOURCE_B), H0))
    s = multiply(SOURCE_B, conjugate(inverse(r), H1))
    u = multiply(r, conjugate(inverse(s), H2))
    z = multiply(inverse(u), conjugate(s, H3))
    defect_word = multiply(z, inverse(TARGET))
    defect = relation_module(defect_word)
    operators = build_operators(r, s, u)
    variables: list[ModuleVector] = [{} for _ in operators]
    for operator_index, coefficient, module_vertex in CORRECTION:
        vertex_word = parse_quotient(module_vertex)
        variables[operator_index][vertex_word] = (
            variables[operator_index].get(vertex_word, 0) + coefficient
        )
    correction_image = add_vectors(*(
        apply_operator(operator, variable)
        for operator, variable in zip(operators, variables)
    ))
    corrected = add_vectors(defect, correction_image)

    lifted_corrections = tuple(lift_module_vector(variable) for variable in variables)
    corrected_conjugators = (
        multiply(lifted_corrections[0], H0),
        multiply(lifted_corrections[1], H1),
        multiply(lifted_corrections[2], H2),
        multiply(lifted_corrections[3], H3),
    )
    corrected_r = multiply(
        SOURCE_A,
        conjugate(inverse(SOURCE_B), corrected_conjugators[0]),
    )
    corrected_s = multiply(
        SOURCE_B,
        conjugate(inverse(corrected_r), corrected_conjugators[1]),
    )
    corrected_u = multiply(
        corrected_r,
        conjugate(inverse(corrected_s), corrected_conjugators[2]),
    )
    corrected_z = multiply(
        inverse(corrected_u),
        conjugate(corrected_s, corrected_conjugators[3]),
    )
    corrected_target = conjugate(TARGET, lifted_corrections[4])
    corrected_residual = multiply(corrected_z, inverse(corrected_target))
    direct_corrected = relation_module(corrected_residual)

    vector_tuple = tuple(sorted(
        ((literal(word), coefficient) for word, coefficient in defect.items()),
        key=lambda item: (len(item[0]), item[0], item[1]),
    ))
    corrected_tuple = tuple(sorted(
        ((literal(word), coefficient) for word, coefficient in corrected.items()),
        key=lambda item: (len(item[0]), item[0], item[1]),
    ))
    direct_corrected_tuple = tuple(sorted(
        ((literal(word), coefficient) for word, coefficient in direct_corrected.items()),
        key=lambda item: (len(item[0]), item[0], item[1]),
    ))
    certificate = PeriodTwoLiftCertificate(
        row_lengths=(len(r), len(s), len(u), len(z), len(defect_word)),
        quotient_z_literal=literal(quotient_reduce(z)),
        defect_vector=vector_tuple,
        defect_terms=len(defect),
        defect_l1=sum(abs(coefficient) for coefficient in defect.values()),
        defect_augmentation=sum(defect.values()),
        operator_term_counts=tuple(len(operator) for operator in operators),
        operator_augmentations=tuple(sum(operator.values()) for operator in operators),
        correction=CORRECTION,
        correction_l1=sum(abs(coefficient) for _, coefficient, _ in CORRECTION),
        corrected_defect=corrected_tuple,
        corrected_direct_defect=direct_corrected_tuple,
        corrected_residual_length=len(corrected_residual),
    )
    assert certificate.quotient_z_literal == "t"
    assert certificate.corrected_defect == ()
    assert certificate.corrected_direct_defect == ()
    return certificate


if __name__ == "__main__":
    print(period_two_lift_certificate())
