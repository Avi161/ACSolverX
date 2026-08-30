from itertools import permutations

from experiments.stable_ac.mms02_fixed_b_a5_conjugacy_certificate import (
    A_WORD,
    B_WORD,
    IDENTITY,
    IMAGES,
    U_WORD,
    V_WORD,
    decide_fixed_b_conjugacy,
)


def _inverse(value: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(value.index(index) for index in range(5))


def _compose(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(left[right[index]] for index in range(5))


def _evaluate(word: str) -> tuple[int, ...]:
    result = IDENTITY
    for letter in word:
        image = IMAGES[letter.lower()]
        result = _compose(result, image if letter.islower() else _inverse(image))
    return result


def _parity(value: tuple[int, ...]) -> int:
    return sum(
        value[left] > value[right]
        for left in range(5)
        for right in range(left + 1, 5)
    ) % 2


def _conjugate(conjugator: tuple[int, ...], value: tuple[int, ...]) -> tuple[int, ...]:
    return _compose(_compose(conjugator, value), _inverse(conjugator))


def test_fixed_b_a5_assignment_kills_the_actual_base_rows():
    assert _evaluate(A_WORD) == IDENTITY
    assert _evaluate(B_WORD) == IDENTITY
    assert {_parity(value) for value in IMAGES.values()} == {0}


def test_fixed_b_endpoint_images_are_pinned_independently():
    decision = decide_fixed_b_conjugacy()
    assert _evaluate(U_WORD) == decision.source_image == (2, 3, 4, 0, 1)
    assert _evaluate(V_WORD) == decision.target_image == (2, 0, 4, 1, 3)
    assert _evaluate(U_WORD.swapcase()[::-1]) == decision.source_inverse_image
    assert _evaluate(V_WORD.swapcase()[::-1]) == decision.target_inverse_image


def test_fixed_b_all_orientations_have_only_odd_s5_conjugators():
    decision = decide_fixed_b_conjugacy()
    sources = (decision.source_image, decision.source_inverse_image)
    targets = (decision.target_image, decision.target_inverse_image)
    all_s5 = tuple(permutations(range(5)))
    even_counts = []
    odd_counts = []
    for source in sources:
        even_row = []
        odd_row = []
        for target in targets:
            conjugators = tuple(
                candidate
                for candidate in all_s5
                if _conjugate(candidate, source) == target
            )
            even_row.append(sum(_parity(candidate) == 0 for candidate in conjugators))
            odd_row.append(sum(_parity(candidate) == 1 for candidate in conjugators))
        even_counts.append(tuple(even_row))
        odd_counts.append(tuple(odd_row))
    assert tuple(even_counts) == decision.a5_conjugator_counts == ((0, 0), (0, 0))
    assert tuple(odd_counts) == decision.s5_odd_conjugator_counts == ((5, 5), (5, 5))


def test_fixed_b_scope_verdict_is_pinned():
    decision = decide_fixed_b_conjugacy()
    assert decision.source_a5_class_size == decision.target_a5_class_size == 12
    assert decision.verdict == "EVERY_B_CONFINED_TERMINAL_PAIR_PATH_OBSTRUCTED"
