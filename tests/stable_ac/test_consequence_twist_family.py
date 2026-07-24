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
    cyclic_orientations,
    free_reduce,
    inverse,
    substitute_generator,
)


A = "xxxzXXXXZ"
D = "TzxZ"
COMPRESSED_POWER = "xxxTTTT"
ROTATED_POWER = "TTTTxxx"


def word_power(word: str, exponent: int) -> str:
    if exponent >= 0:
        return word * exponent
    return inverse(word) * (-exponent)


def consequence_endpoint(n: int) -> tuple[str, str]:
    recovery = free_reduce("t" + word_power(ROTATED_POWER, n))
    z_expression = free_reduce("x" + recovery)
    return tuple(
        substitute_generator(word, "z", z_expression).translate(
            str.maketrans("tT", "yY")
        )
        for word in (A, D)
    )


def whitehead_coordinates(n: int) -> tuple[str, str]:
    pair = consequence_endpoint(n)
    phi = {"x": "Y", "y": "x"} if n > 0 else {"x": "y", "y": "X"}
    return tuple(cyc_reduce(apply_hom(word, phi)) for word in pair)


def test_consequence_twists_are_literal_ac_recovery_words():
    assert ROTATED_POWER in cyclic_orientations(COMPRESSED_POWER)

    for n in range(-6, 7):
        recovery = free_reduce(
            "t" + word_power(ROTATED_POWER, n)
        )
        if n >= 0:
            assert recovery == free_reduce(
                "t" + ROTATED_POWER * n
            )
        else:
            assert recovery == free_reduce(
                "t" + inverse(ROTATED_POWER) * (-n)
            )
        assert consequence_endpoint(n)


def test_consequence_twist_complete_floor_formulas():
    for n in range(-6, 7):
        floor, _, _ = aut_canon(consequence_endpoint(n))
        expected = (
            14
            if n == 0
            else 28 * n - 5
            if n > 0
            else 28 * (-n) + 15
        )
        assert floor == expected


def test_symbolic_whitehead_length_change_tables():
    for m in range(1, 7):
        positive = whitehead_coordinates(m)
        assert positive == (
            "YYYXXX"
            + "YYYXXXX" * (m - 1)
            + "yyyy"
            + "xxxxyyy" * (m - 1)
            + "xxx",
            "XYXXX"
            + "YYYXXXX" * (m - 1)
            + "Y"
            + "xxxxyyy" * (m - 1)
            + "xxxy",
        )
        positive_length = sum(map(len, positive))
        assert positive_length == 28 * m - 5
        positive_deltas = [
            sum(map(len, _reduce_pair(positive, automorphism)))
            - positive_length
            for automorphism in DESCENT
        ]
        assert positive_deltas == [
            12 * m - 6,
            4 * m,
            0,
            4 * m,
            12 * m - 6,
            0,
            16 * m - 7,
            8 * m - 1,
            0,
            8 * m - 1,
            16 * m - 7,
            0,
        ]

        negative = whitehead_coordinates(-m)
        assert negative == (
            "yyyX"
            + "YYYXXXX" * m
            + "YYYY"
            + "xxxxyyy" * m
            + "x",
            "xyX"
            + "YYYXXXX" * m
            + "y"
            + "xxxxyyy" * m
            + "xY",
        )
        negative_length = sum(map(len, negative))
        assert negative_length == 28 * m + 15
        negative_deltas = [
            sum(map(len, _reduce_pair(negative, automorphism)))
            - negative_length
            for automorphism in DESCENT
        ]
        assert negative_deltas == [
            12 * m + 4,
            4 * m + 6,
            0,
            4 * m + 6,
            12 * m + 4,
            0,
            16 * m - 1,
            8 * m + 1,
            0,
            8 * m + 1,
            16 * m - 1,
            0,
        ]
