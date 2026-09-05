from experiments.equivalence_classes.lib.autcanon import (
    DESCENT,
    _reduce_pair,
    aut_canon,
)
from experiments.equivalence_classes.lib.words import (
    apply_hom,
    cyc_reduce,
)
from experiments.stable_ac.rank3_compression.two_stabilization import (
    free_reduce,
    inverse,
    substitute_generator,
)


A = "xxxzXXXXZ"
D = "TzxZ"
POWER_RELATOR = "xxxTTTT"
POWER_BASE = "xxx"


def word_power(word: str, exponent: int) -> str:
    if exponent >= 0:
        return word * exponent
    return inverse(word) * (-exponent)


def conjugate(word: str, by: str) -> str:
    return free_reduce(by + word + inverse(by))


def cyclic_equivalent(left: str, right: str) -> bool:
    left = cyc_reduce(left)
    right = cyc_reduce(right)
    return len(left) == len(right) and right in left + left


def consequence_factors(m: int) -> tuple[str, ...]:
    factors = []
    if m > 0:
        for j in range(m):
            flank = word_power(POWER_BASE, j)
            factors.extend(
                (
                    conjugate(POWER_RELATOR, flank + "T"),
                    conjugate(inverse(POWER_RELATOR), flank),
                )
            )
    elif m < 0:
        for j in range(-1, m - 1, -1):
            flank = word_power(POWER_BASE, j)
            factors.extend(
                (
                    conjugate(POWER_RELATOR, flank),
                    conjugate(inverse(POWER_RELATOR), flank + "T"),
                )
            )
    return tuple(factors)


def conjugated_recovery_endpoint(m: int) -> tuple[str, str]:
    recovery = free_reduce(
        word_power(POWER_BASE, m)
        + "t"
        + word_power(POWER_BASE, -m)
    )
    z_expression = free_reduce("x" + recovery)
    return tuple(
        substitute_generator(word, "z", z_expression).translate(
            str.maketrans("tT", "yY")
        )
        for word in (A, D)
    )


def whitehead_coordinates(m: int) -> tuple[str, str]:
    pair = conjugated_recovery_endpoint(m)
    if m >= 0:
        exponent = 3 * m + 1
        phi = {"x": "x", "y": "X" * exponent + "Y"}
    else:
        exponent = 3 * (-m) - 1
        phi = {"x": "x", "y": "y" + "x" * exponent}
    return tuple(cyc_reduce(apply_hom(word, phi)) for word in pair)


def test_commutator_consequence_is_literal_product_of_relator_conjugates():
    for m in range(-8, 9):
        consequence = free_reduce("".join(consequence_factors(m)))
        expected = free_reduce(
            "T"
            + word_power(POWER_BASE, m)
            + "t"
            + word_power(POWER_BASE, -m)
        )
        assert consequence == expected
        assert len(consequence_factors(m)) == 2 * abs(m)

        recovery = free_reduce("t" + consequence)
        assert recovery == free_reduce(
            word_power(POWER_BASE, m)
            + "t"
            + word_power(POWER_BASE, -m)
        )


def test_conjugated_recovery_complete_floor_formulas():
    for m in range(-8, 9):
        floor, _, _ = aut_canon(conjugated_recovery_endpoint(m))
        expected = (
            14
            if m == 0
            else 3 * m + 14
            if m > 0
            else 3 * (-m) + 12
        )
        assert floor == expected


def test_symbolic_whitehead_length_change_tables():
    for m in range(9):
        positive_exponent = 3 * m + 1
        positive = (
            "xxxYXXXXy",
            "y" + "x" * positive_exponent + "Yxy",
        )
        assert all(
            cyclic_equivalent(actual, predicted)
            for actual, predicted in zip(
                whitehead_coordinates(m), positive, strict=True
            )
        )
        positive_length = sum(map(len, positive))
        assert positive_length == 3 * m + 14
        positive_deltas = [
            sum(map(len, _reduce_pair(positive, automorphism)))
            - positive_length
            for automorphism in DESCENT
        ]
        assert positive_deltas == [
            1,
            1,
            0,
            1,
            1,
            0,
            3 * m + 5,
            3 * m + 5,
            0,
            3 * m + 5,
            3 * m + 5,
            0,
        ]

    for m in range(1, 9):
        negative_exponent = 3 * m - 1
        negative = (
            "yXXXXYxxx",
            "Y" + "X" * negative_exponent + "yxY",
        )
        assert all(
            cyclic_equivalent(actual, predicted)
            for actual, predicted in zip(
                whitehead_coordinates(-m), negative, strict=True
            )
        )
        negative_length = sum(map(len, negative))
        assert negative_length == 3 * m + 12
        negative_deltas = [
            sum(map(len, _reduce_pair(negative, automorphism)))
            - negative_length
            for automorphism in DESCENT
        ]
        assert negative_deltas == [
            1,
            1,
            0,
            1,
            1,
            0,
            3 * m + 3,
            3 * m + 3,
            0,
            3 * m + 3,
            3 * m + 3,
            0,
        ]
