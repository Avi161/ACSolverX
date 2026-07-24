from experiments.equivalence_classes.lib.autcanon import aut_canon
from experiments.equivalence_classes.lib.words import apply_hom, cyc_reduce
from experiments.stable_ac.rank3_compression.two_stabilization import (
    cyclic_orientations,
    free_reduce,
    solve_isolator,
    substitute_generator,
)


AK3 = ("xxxYYYY", "xyxYXY")
A = "xxxzXXXXZ"
B = "ZxzxZ"


def x_power(exponent: int) -> str:
    return "x" * exponent if exponent >= 0 else "X" * (-exponent)


def family_words(
    sign: int,
    p: int,
    q: int,
) -> tuple[str, str, str, str, str]:
    block = "zxZ" if sign == 1 else "zXZ"
    word_t = x_power(p) + block + x_power(q)
    defining_t = "T" + word_t
    if sign == 1:
        compressed_a = "xxx" + 4 * (
            x_power(q) + "T" + x_power(p)
        )
        compressed_b = (
            "Z" + x_power(1 - p) + "t" + x_power(-q)
        )
    else:
        compressed_a = "xxx" + 4 * (
            x_power(-p) + "t" + x_power(-q)
        )
        compressed_b = (
            "Z" + x_power(q + 1) + "T" + x_power(p)
        )
    expression_z = solve_isolator(compressed_b, "z")
    survivor = substitute_generator(defining_t, "z", expression_z)
    return word_t, defining_t, compressed_a, compressed_b, survivor


def test_twist_family_literal_compression_and_elimination():
    for sign in (-1, 1):
        for p in range(-4, 5):
            for q in range(-4, 5):
                word_t, _, compressed_a, compressed_b, survivor = (
                    family_words(sign, p, q)
                )

                assert substitute_generator(compressed_a, "t", word_t) == A
                assert substitute_generator(compressed_b, "t", word_t) == B
                if sign == 1:
                    assert solve_isolator(compressed_b, "z") == (
                        x_power(1 - p) + "t" + x_power(-q)
                    )
                    assert survivor == (
                        "TxtxT" + x_power(p + q - 1)
                    )
                else:
                    assert solve_isolator(compressed_b, "z") == (
                        x_power(q + 1) + "T" + x_power(p)
                    )
                    assert survivor == (
                        "T" + x_power(p + q + 1) + "TXtX"
                    )


def test_twist_parameter_is_an_ambient_gauge():
    for sign in (-1, 1):
        for p in range(-4, 5):
            for q in range(-4, 5):
                _, _, compressed_a, _, survivor = family_words(
                    sign, p, q
                )
                pair = tuple(
                    word.translate(str.maketrans("tT", "yY"))
                    for word in (compressed_a, survivor)
                )
                image_y = "y" if sign == 1 else "Y"
                shear = {
                    "x": "x",
                    "y": x_power(p) + image_y + x_power(q),
                }

                linear_image = tuple(
                    free_reduce(apply_hom(word, shear)) for word in pair
                )
                assert linear_image[0] == AK3[0]
                assert cyc_reduce(linear_image[1]) in cyclic_orientations(
                    AK3[1]
                )

                floor, representative, witness = aut_canon(pair)
                assert floor == 13
                assert representative == ("YXYxyx", "YYYYxxx")
                assert witness
