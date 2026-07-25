from __future__ import annotations

from experiments.equivalence_classes.lib.words import free_reduce, inv
from experiments.stable_ac.rank3_compression.recovery_word_equation import (
    normal_form,
)


D_P = "TxtxTX"
ORDERS = {"x": 3, "t": 4}


def conjugate(word: str, by: str) -> str:
    return free_reduce(by + word + inv(by))


def power(generator: str, exponent: int) -> str:
    return generator * exponent if exponent >= 0 else generator.swapcase() * (-exponent)


def torus_weight(word: str) -> int:
    central, syllables = normal_form(word)
    return 12 * central + sum(
        (4 if generator == "x" else 3) * exponent
        for generator, exponent in syllables
    )


def projected_cyclic_reduce(
    syllables: tuple[tuple[str, int], ...],
) -> tuple[tuple[str, int], ...]:
    reduced = list(syllables)
    while len(reduced) > 1 and reduced[0][0] == reduced[-1][0]:
        generator = reduced[0][0]
        exponent = (reduced[-1][1] + reduced[0][1]) % ORDERS[generator]
        reduced = reduced[1:-1]
        if exponent:
            reduced.insert(0, (generator, exponent))
    return tuple(reduced)


def projected_conjugacy_key(word: str) -> tuple[tuple[str, int], ...]:
    projected = projected_cyclic_reduce(normal_form(word)[1])
    if not projected:
        return ()
    return min(
        projected[index:] + projected[:index]
        for index in range(len(projected))
    )


def conjugacy_signature(word: str) -> tuple[int, tuple[tuple[str, int], ...]]:
    return torus_weight(word), projected_conjugacy_key(word)


def tail(exponent: int) -> str:
    return free_reduce(
        power("t", -exponent)
        + "xt"
        + power("x", exponent)
    )


def evaluate_d(value: str) -> str:
    return free_reduce("T" + value + "x" + inv(value))


def test_central_shifts_have_one_projection_and_weight_gap_twelve():
    base = "xTtxT"
    base_signature = conjugacy_signature(base)

    for exponent in range(-4, 5):
        shifted = free_reduce(power("x", 3 * exponent) + base)
        weight, projected_key = conjugacy_signature(shifted)

        assert projected_key == base_signature[1]
        assert weight == base_signature[0] + 12 * exponent
        assert (conjugacy_signature(shifted) == base_signature) == (exponent == 0)


def test_conjugacy_signature_accepts_conjugates_and_rejects_each_missing_half():
    for conjugator in ("", "xt", "TXXt", "xTXt"):
        assert conjugacy_signature(conjugate(D_P, conjugator)) == (
            conjugacy_signature(D_P)
        )

    central_shift = free_reduce("xxx" + D_P)
    assert projected_conjugacy_key(central_shift) == projected_conjugacy_key(D_P)
    assert torus_weight(central_shift) != torus_weight(D_P)

    same_weight_other_projection = "Tx"
    assert torus_weight(same_weight_other_projection) == torus_weight(D_P)
    assert projected_conjugacy_key(same_weight_other_projection) != (
        projected_conjugacy_key(D_P)
    )


def test_representative_hnn_tails_have_the_d_p_conjugacy_signature():
    expected = conjugacy_signature(D_P)

    for exponent in range(-12, 13):
        endpoint = evaluate_d(tail(exponent))

        assert endpoint == conjugate(D_P, power("t", -exponent))
        assert conjugacy_signature(endpoint) == expected
