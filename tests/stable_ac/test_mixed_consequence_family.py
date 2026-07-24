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


def cyclic_rotation(left: str, right: str) -> bool:
    left = cyc_reduce(left)
    right = cyc_reduce(right)
    return len(left) == len(right) and right in left + left


def mixed_recovery_endpoint(n: int, m: int) -> tuple[str, str]:
    commutator = free_reduce(
        "T"
        + word_power(POWER_BASE, m)
        + "t"
        + word_power(POWER_BASE, -m)
    )
    recovery = free_reduce(
        "t" + word_power(ROTATED_POWER, n) + commutator
    )
    z_expression = free_reduce("x" + recovery)
    return tuple(
        substitute_generator(word, "z", z_expression).translate(
            str.maketrans("tT", "yY")
        )
        for word in (A, D)
    )


def displayed_mixed_pair(n: int, m: int) -> tuple[str, str]:
    assert n and m
    corridor = free_reduce(
        "t" + word_power(ROTATED_POWER, n) + "T"
    ).translate(str.maketrans("tT", "yY"))
    power = word_power(POWER_BASE, m)
    inverse_power = inverse(power)
    inverse_corridor = inverse(corridor)
    return (
        free_reduce(
            POWER_BASE
            + corridor
            + power
            + "yXXXXY"
            + inverse_power
            + inverse_corridor
        ),
        free_reduce(
            "Yx"
            + corridor
            + power
            + "yxY"
            + inverse_power
            + inverse_corridor
            + "X"
        ),
    )


def expected_floor(n: int, m: int) -> int:
    if n == 0:
        if m == 0:
            return 14
        return 3 * m + 14 if m > 0 else 3 * (-m) + 12
    if m == 0:
        return 28 * n - 5 if n > 0 else 28 * (-n) + 15
    return 28 * abs(n) + 12 * abs(m) + 15


def expected_mixed_deltas(n: int, m: int) -> list[int]:
    assert n and m
    n_abs = abs(n)
    m_abs = abs(m)
    if n > 0:
        first = 8 * n_abs - 5
        second = 16 * n_abs - 3
        seventh = 12 * m_abs + 4 * n_abs
        eighth = 12 * m_abs + 12 * n_abs + 2
    elif m > 0:
        first = 8 * n_abs + 1
        second = 16 * n_abs - 9
        seventh = 12 * m_abs + 4 * n_abs + 6
        eighth = 12 * m_abs + 12 * n_abs - 4
    else:
        first = 8 * n_abs - 7
        second = 16 * n_abs - 1
        seventh = 12 * m_abs + 4 * n_abs - 2
        eighth = 12 * m_abs + 12 * n_abs + 4
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


def test_mixed_recovery_uses_the_retained_relator_in_the_stated_order():
    assert ROTATED_POWER in cyclic_orientations(POWER_RELATOR)

    for n in range(-6, 7):
        for m in range(-6, 7):
            commutator = free_reduce(
                "T"
                + word_power(POWER_BASE, m)
                + "t"
                + word_power(POWER_BASE, -m)
            )
            recovery = free_reduce(
                "t" + word_power(ROTATED_POWER, n) + commutator
            )
            assert recovery
            assert mixed_recovery_endpoint(n, m)


def test_mixed_consequence_complete_floor_formula():
    for n in range(-6, 7):
        for m in range(-6, 7):
            assert (
                aut_min_len(mixed_recovery_endpoint(n, m))
                == expected_floor(n, m)
            )


def test_nonzero_mixed_quadrants_have_symbolic_whitehead_certificates():
    for n in range(-5, 6):
        if n == 0:
            continue
        for m in range(-5, 6):
            if m == 0:
                continue

            displayed = displayed_mixed_pair(n, m)
            actual = mixed_recovery_endpoint(n, m)
            assert all(
                cyclic_rotation(actual_word, displayed_word)
                for actual_word, displayed_word in zip(
                    actual, displayed, strict=True
                )
            )

            total = sum(map(len, displayed))
            assert total == expected_floor(n, m)
            deltas = [
                sum(map(len, _reduce_pair(displayed, automorphism)))
                - total
                for automorphism in DESCENT
            ]
            assert deltas == expected_mixed_deltas(n, m)
            assert min(deltas) == 0
