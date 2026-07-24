from experiments.equivalence_classes.lib.autcanon import (
    DESCENT,
    _reduce_pair,
    aut_min_len,
)
from experiments.equivalence_classes.lib.words import cyc_reduce
from experiments.stable_ac.rank3_compression.two_stabilization import (
    cyclic_orientations,
    free_reduce,
    inverse,
    substitute_generator,
)


A = "xxxzXXXXZ"
D = "TzxZ"
POWER_RELATOR = "xxxTTTT"
ROTATED_POWER = "TTTTxxx"
POWER_BASE = "xxx"


def word_power(word: str, exponent: int) -> str:
    if exponent >= 0:
        return word * exponent
    return inverse(word) * (-exponent)


def reverse_mixed_recovery(n: int, m: int) -> str:
    commutator = free_reduce(
        "T"
        + word_power(POWER_BASE, m)
        + "t"
        + word_power(POWER_BASE, -m)
    )
    return free_reduce(
        "t" + commutator + word_power(ROTATED_POWER, n)
    )


def reverse_mixed_endpoint(n: int, m: int) -> tuple[str, str]:
    z_expression = free_reduce("x" + reverse_mixed_recovery(n, m))
    return tuple(
        cyc_reduce(
            substitute_generator(word, "z", z_expression).translate(
                str.maketrans("tT", "yY")
            )
        )
        for word in (A, D)
    )


def expected_floor(n: int, m: int) -> int:
    if n == 0:
        if m == 0:
            return 14
        return 3 * m + 14 if m > 0 else 3 * (-m) + 12
    if m == 0:
        return 28 * n - 5 if n > 0 else 28 * (-n) + 15
    constant = (
        3
        if n > 0 and m > 0
        else -1
        if n > 0
        else 15
        if m > 0
        else -13
    )
    return 28 * abs(n) + 18 * abs(m) + constant


def expected_deltas(n: int, m: int) -> list[int]:
    assert n and m
    n_abs = abs(n)
    m_abs = abs(m)
    if n > 0 and m > 0:
        first = 8 * n_abs + 5
        second = 16 * n_abs - 5
        seventh = 18 * m_abs + 4 * n_abs - 2
        eighth = 18 * m_abs + 12 * n_abs - 12
    elif n > 0:
        first = 8 * n_abs + 3
        second = 16 * n_abs - 3
        seventh = 18 * m_abs + 4 * n_abs - 8
        eighth = 18 * m_abs + 12 * n_abs - 14
    elif m > 0:
        first = 8 * n_abs + 1
        second = 16 * n_abs - 1
        seventh = 18 * m_abs + 4 * n_abs + 6
        eighth = 18 * m_abs + 12 * n_abs + 4
    elif m_abs == 1:
        first = 8 * n_abs + 7
        second = 16 * n_abs + 1
        seventh = 4 * n_abs + 2
        eighth = 12 * n_abs - 4
    else:
        first = 8 * n_abs + 7
        second = 16 * n_abs - 7
        seventh = 18 * m_abs + 4 * n_abs - 16
        eighth = 18 * m_abs + 12 * n_abs - 30
    return [
        first,
        second,
        0,
        second,
        first,
        0,
        seventh,
        eighth,
        0,
        eighth,
        seventh,
        0,
    ]


def expected_lengths(n: int, m: int) -> tuple[int, int]:
    assert n and m
    n_abs = abs(n)
    m_abs = abs(m)
    if n > 0:
        first = 14 * n_abs + 6 * m_abs + 3
        second = (
            14 * n_abs + 12 * m_abs
            if m > 0
            else 14 * n_abs + 12 * m_abs - 4
        )
    else:
        first = (
            14 * n_abs + 6 * m_abs + 9
            if m > 0
            else 14 * n_abs + 6 * m_abs - 3
        )
        second = (
            14 * n_abs + 12 * m_abs + 6
            if m > 0
            else 14 * n_abs + 12 * m_abs - 10
        )
    return first, second


def test_reverse_mixed_recovery_has_the_stated_factor_order():
    assert ROTATED_POWER in cyclic_orientations(POWER_RELATOR)

    for n in range(-6, 7):
        for m in range(-6, 7):
            commutator = free_reduce(
                "T"
                + word_power(POWER_BASE, m)
                + "t"
                + word_power(POWER_BASE, -m)
            )
            assert reverse_mixed_recovery(n, m) == free_reduce(
                word_power(POWER_BASE, m)
                + "t"
                + word_power(POWER_BASE, -m)
                + word_power(ROTATED_POWER, n)
            )
            assert bool(commutator) is (m != 0)


def test_reverse_mixed_complete_floor_formula():
    for n in range(-6, 7):
        for m in range(-6, 7):
            assert (
                aut_min_len(reverse_mixed_endpoint(n, m))
                == expected_floor(n, m)
            )


def test_reverse_mixed_nonzero_quadrants_are_already_whitehead_minimal():
    for n in range(-5, 6):
        if n == 0:
            continue
        for m in range(-5, 6):
            if m == 0:
                continue

            pair = reverse_mixed_endpoint(n, m)
            assert tuple(map(len, pair)) == expected_lengths(n, m)
            total = sum(map(len, pair))
            assert total == expected_floor(n, m)
            deltas = [
                sum(map(len, _reduce_pair(pair, automorphism)))
                - total
                for automorphism in DESCENT
            ]
            assert deltas == expected_deltas(n, m)
            assert min(deltas) == 0
