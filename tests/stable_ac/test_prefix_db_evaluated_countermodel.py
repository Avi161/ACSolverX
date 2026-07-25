from __future__ import annotations

from collections import Counter
from math import gcd

from experiments.equivalence_classes.lib.words import free_reduce, inv
from experiments.stable_ac.rank3_compression.recovery_word_equation import (
    normal_form,
)


P = "xt"
D_P = "TxtxTX"

E = "XXXXXX" + "xtxtttxtx"
B = "XXXXXXXXX" + "xxtttxxtxx"
C = "XXXXXX" + "xxtttxx"
ALPHA = "xtxtttxt"
BETA = "xx"

D = free_reduce("T" + E + "x" + inv(E))
K = free_reduce(D + ALPHA + B + inv(ALPHA))
SECOND_TARGET = free_reduce(B + BETA + K + inv(BETA))

ORDERS = {"x": 3, "t": 4}


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


def syllable_rotations(
    syllables: tuple[tuple[str, int], ...],
) -> tuple[tuple[tuple[str, int], ...], ...]:
    return tuple(
        syllables[index:] + syllables[:index]
        for index in range(len(syllables))
    )


def syllable_word(syllables: tuple[tuple[str, int], ...]) -> str:
    return "".join(
        generator * exponent
        for generator, exponent in syllables
    )


def test_explicit_lifts_solve_every_evaluated_prefix_db_equation():
    assert normal_form(inv(E) + P) == normal_form(B)
    assert normal_form(K) == normal_form(C)
    assert normal_form(SECOND_TARGET) == normal_form(C)
    assert normal_form(K + inv(C)) == (0, ())


def test_countermodel_occupies_the_positive_positive_negative_row():
    assert torus_weight(E) == 7
    assert torus_weight(B) == 0
    assert torus_weight(D) == 1
    assert torus_weight(K) == 1
    assert torus_weight(C) == 1
    assert torus_weight(SECOND_TARGET) == 1


def test_survivor_is_a_projected_killer_but_not_in_the_braid_class():
    survivor_key = projected_conjugacy_key(C)

    assert survivor_key == (("t", 3), ("x", 1))
    assert len(survivor_key) == 2
    assert len(projected_conjugacy_key(D_P)) == 6
    assert len(projected_conjugacy_key(inv(D_P))) == 6
    assert survivor_key != projected_conjugacy_key(D_P)
    assert survivor_key != projected_conjugacy_key(inv(D_P))

    # Killing x t^{-1} identifies the C3 and C4 generators.
    assert gcd(3, 4) == 1


def test_quotient_b_commutator_sieve_excludes_the_countermodel():
    braid = normal_form(D_P)[1]
    inverse_braid = normal_form(inv(D_P))[1]
    twists = ("", "x", "xx", "t", "tt", "ttt")
    length_counts = Counter()

    for left in syllable_rotations(braid):
        for right in syllable_rotations(inverse_braid):
            for twist in twists:
                commutator_shadow = (
                    syllable_word(left)
                    + twist
                    + syllable_word(right)
                    + inv(twist)
                )
                cyclic = projected_cyclic_reduce(
                    normal_form(commutator_shadow)[1]
                )
                length_counts[len(cyclic)] += 1

    assert length_counts == Counter({12: 130, 8: 40, 10: 28, 0: 18})
    assert len(projected_conjugacy_key(B)) == 4
    assert 4 not in length_counts
