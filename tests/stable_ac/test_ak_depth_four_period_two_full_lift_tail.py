from collections import defaultdict
from itertools import product

from experiments.stable_ac import depth4_period_two_lift_certificate as lift
from experiments.stable_ac.depth4_period_two_phi_infinity_hessian_certificate import (
    residual_occurrences,
)
from experiments.stable_ac.depth4_period_two_source_flow_certificate import (
    C_ACTION,
    T_ACTION,
    T_INVERSE,
    compose,
)


PAIRED_INTERVALS = (
    (3, 4),
    (7, 8),
    (11, 12),
    (2, 5),
    (10, 13),
    (1, 6),
    (9, 14),
    (15, 16),
)


def _prefixes() -> tuple[lift.Word, ...]:
    return tuple(occurrence.quotient_prefix for occurrence in residual_occurrences())


def _difference(left: lift.Word, right: lift.Word) -> lift.Word:
    return lift.quotient_multiply(lift.quotient_inverse(left), right)


def _right_action(word: lift.Word) -> tuple[int, ...]:
    action = tuple(range(4))
    for letter in lift.quotient_reduce(word):
        if abs(letter) == lift.C:
            letter_action = C_ACTION
        elif letter == lift.T:
            letter_action = T_ACTION
        else:
            letter_action = T_INVERSE
        action = compose(action, letter_action)
    return action


def _semilinear_multiply(
    left: tuple[int, int, int],
    right: tuple[int, int, int],
) -> tuple[int, int, int]:
    left_a, left_b, left_parity = left
    right_a, right_b, right_parity = right
    if left_parity:
        right_a, right_b = right_b, right_a
    return left_a + right_a, left_b + right_b, left_parity ^ right_parity


def _semilinear(word: lift.Word) -> tuple[int, int, int]:
    value = (0, 0, 0)
    for letter in lift.quotient_reduce(word):
        if abs(letter) == lift.C:
            letter_value = (0, 0, 1)
        elif letter == lift.T:
            letter_value = (1, 0, 0)
        else:
            letter_value = (-1, 0, 0)
        value = _semilinear_multiply(value, letter_value)
    return value


def test_tail_paired_words_duplicate_classes_and_shadow_identities() -> None:
    prefixes = _prefixes()
    paired_words = tuple(
        lift.literal(_difference(prefixes[left - 1], prefixes[right - 1]))
        for left, right in PAIRED_INTERVALS
    )
    assert paired_words == (
        "cTctcTTTcttc",
        "cTctcTTTcttc",
        "cTctcTTTcttc",
        "cTctcTctt",
        "cTctcTctt",
        "ctcTcTctc",
        "TTcttcTct",
        "T",
    )

    classes: dict[lift.Word, list[int]] = defaultdict(list)
    for index, prefix in enumerate(prefixes, start=1):
        classes[prefix].append(index)
    duplicates = tuple(
        sorted(tuple(indices) for indices in classes.values() if len(indices) > 1)
    )
    assert duplicates == ((1, 16), (2, 3), (6, 7), (10, 11), (14, 15))

    g_0 = _difference(prefixes[2], prefixes[3])
    g_1 = _difference(prefixes[1], prefixes[4])
    assert tuple(
        _difference(prefixes[left - 1], prefixes[right - 1])
        for left, right in ((2, 4), (6, 8), (10, 12))
    ) == (g_0, g_0, g_0)
    assert tuple(
        _difference(prefixes[left - 1], prefixes[right - 1])
        for left, right in ((3, 5), (11, 13))
    ) == (g_1, g_1)


def test_tail_semilinear_and_four_state_tables() -> None:
    prefixes = _prefixes()
    assert tuple(_semilinear(prefix) for prefix in prefixes) == (
        (0, 0, 0),
        (1, 0, 1),
        (1, 0, 1),
        (-3, 3, 0),
        (-1, 3, 1),
        (0, 0, 1),
        (0, 0, 1),
        (-4, 3, 0),
        (-2, 3, 1),
        (-1, 2, 0),
        (-1, 2, 0),
        (2, -2, 1),
        (2, 0, 0),
        (1, 0, 0),
        (1, 0, 0),
        (0, 0, 0),
    )

    source_images = tuple(
        _semilinear(
            lift.quotient_multiply(
                prefixes[right - 1],
                lift.quotient_inverse(prefixes[left - 1]),
            )
        )
        for left, right in PAIRED_INTERVALS
    )
    assert source_images == (
        (-3, 2, 1),
        (-4, 3, 1),
        (0, -1, 1),
        (-2, 3, 0),
        (3, -2, 0),
        (0, 0, 1),
        (-2, 2, 1),
        (-1, 0, 0),
    )

    g_0 = _difference(prefixes[2], prefixes[3])
    g_1 = _difference(prefixes[1], prefixes[4])
    assert _semilinear(g_0) == (3, -4, 1)
    assert _semilinear(g_1) == (3, -2, 0)
    assert (_semilinear(g_0)[0] - _semilinear(g_0)[1], -1) == (7, -1)
    assert (_semilinear(g_1)[0] - _semilinear(g_1)[1], 1) == (5, 1)

    assert tuple(_right_action(prefix)[0] for prefix in prefixes) == (
        0,
        1,
        1,
        0,
        2,
        0,
        0,
        3,
        0,
        0,
        0,
        3,
        0,
        0,
        0,
        0,
    )
    assert _right_action(g_0) == (3, 0, 2, 1)
    assert _right_action(g_1) == (0, 2, 3, 1)


def test_duplicate_prefix_path_degrees_for_all_coefficient_rows() -> None:
    representative = {
        1: 1,
        2: 2,
        3: 2,
        4: 4,
        5: 5,
        6: 6,
        7: 6,
        8: 8,
        9: 9,
        10: 10,
        11: 10,
        12: 12,
        13: 13,
        14: 14,
        15: 14,
        16: 1,
    }
    edge_slots = (
        (3, 4, 0),
        (7, 8, 0),
        (11, 12, 0),
        (2, 5, 1),
        (10, 13, 1),
        (1, 6, 2),
        (9, 14, 3),
        (15, 16, 4),
    )

    for coefficients in product((0, 1), repeat=5):
        degrees: dict[int, int] = defaultdict(int)
        for left, right, slot in edge_slots:
            if coefficients[slot]:
                degrees[representative[left]] ^= 1
                degrees[representative[right]] ^= 1
        f_0, f_1, f_2, f_3, f_4 = coefficients
        assert tuple(degrees[index] for index in (4, 2, 5, 8, 6, 1, 14, 9, 12, 10, 13)) == (
            f_0,
            f_0 ^ f_1,
            f_1,
            f_0,
            f_0 ^ f_2,
            f_2 ^ f_4,
            f_4 ^ f_3,
            f_3,
            f_0,
            f_0 ^ f_1,
            f_1,
        )
