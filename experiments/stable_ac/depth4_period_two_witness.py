from __future__ import annotations

from dataclasses import dataclass


Syllable = tuple[str, int]
Word = tuple[Syllable, ...]


def multiply(*words: Word) -> Word:
    reduced: list[Syllable] = []
    for factor, exponent in (syllable for word in words for syllable in word):
        if reduced and reduced[-1][0] == factor:
            exponent += reduced.pop()[1]
        if factor == "c":
            exponent %= 2
        if exponent:
            reduced.append((factor, exponent))
    return tuple(reduced)


def inverse(word: Word) -> Word:
    return multiply(tuple((factor, -exponent) for factor, exponent in reversed(word)))


def conjugate(word: Word, conjugator: Word) -> Word:
    return multiply(conjugator, word, inverse(conjugator))


SOURCE_A: Word = (
    ("t", -2),
    ("c", 1),
    ("t", -2),
    ("c", 1),
    ("t", 2),
    ("c", 1),
)
SOURCE_B: Word = (
    ("t", -3),
    ("c", 1),
    ("t", 1),
    ("c", 1),
    ("t", 1),
    ("c", 1),
)
H0: Word = (("c", 1), ("t", -2), ("c", 1), ("t", 3))
H1: Word = ()
H2: Word = (("c", 1), ("t", -1), ("c", 1), ("t", 3))
H3: Word = (("t", 1),)
TARGET: Word = (("t", 1),)


@dataclass(frozen=True)
class PeriodTwoWitness:
    source_a: Word
    source_b: Word
    conjugators: tuple[Word, Word, Word, Word]
    r: Word
    s: Word
    u: Word
    x: Word
    y: Word
    z: Word
    target: Word
    x_r_inverse_y: Word
    y_target_inverse_x: Word


def period_two_witness() -> PeriodTwoWitness:
    r = multiply(SOURCE_A, conjugate(inverse(SOURCE_B), H0))
    s = multiply(SOURCE_B, conjugate(inverse(r), H1))
    x = conjugate(s, H2)
    y = conjugate(s, H3)
    u = multiply(r, inverse(x))
    z = multiply(inverse(u), y)
    witness = PeriodTwoWitness(
        source_a=SOURCE_A,
        source_b=SOURCE_B,
        conjugators=(H0, H1, H2, H3),
        r=r,
        s=s,
        u=u,
        x=x,
        y=y,
        z=z,
        target=TARGET,
        x_r_inverse_y=multiply(x, inverse(r), y),
        y_target_inverse_x=multiply(y, inverse(TARGET), x),
    )
    assert witness.z == TARGET
    assert witness.x_r_inverse_y == TARGET
    assert witness.y_target_inverse_x == witness.r
    return witness


if __name__ == "__main__":
    print(period_two_witness())
