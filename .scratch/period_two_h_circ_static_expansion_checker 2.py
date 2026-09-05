#!/usr/bin/env python3
"""Independent static audit of the gauged occurrence Hessian H^circ.

This checker deliberately does not import the production certificate.  It
encodes the sixteen pinned triples, constructs (3.40), applies (3.54) and
(3.70), and compares the result with the separately pinned ledger entries.
"""

from __future__ import annotations

from collections import defaultdict
from hashlib import sha256


Word = str
Ring = dict[Word, int]
Matrix = list[list[Ring]]
Syllable = tuple[str, int]


def reduce_word(raw: str) -> Word:
    out: list[str] = []
    for letter in raw:
        if letter == "C":
            letter = "c"
        assert letter in "ctT", (raw, letter)
        if out and ((out[-1] == "c" and letter == "c") or
                    (out[-1], letter) in (("t", "T"), ("T", "t"))):
            out.pop()
        else:
            out.append(letter)
    return "".join(out)


def multiply_word(left: Word, right: Word) -> Word:
    return reduce_word(left + right)


def inverse_word(word: Word) -> Word:
    return reduce_word("".join({"c": "c", "t": "T", "T": "t"}[x]
                              for x in reversed(word)))


def syllables(word: Word) -> tuple[Syllable, ...]:
    result: list[Syllable] = []
    exponent = 0
    for letter in reduce_word(word):
        if letter == "c":
            if exponent:
                result.append(("t", exponent))
                exponent = 0
            result.append(("c", 1))
        else:
            exponent += 1 if letter == "t" else -1
    if exponent:
        result.append(("t", exponent))
    return tuple(result)


def cyclic_syllables(word: Word) -> tuple[Syllable, ...]:
    value = list(syllables(word))
    while len(value) > 1 and value[0][0] == value[-1][0]:
        first = value.pop(0)
        last = value.pop()
        if first[0] == "t":
            combined = last[1] + first[1]
            if combined:
                value.append(("t", combined))
    if len(value) > 1 and value[0][0] == "t":
        value = [value[-1], *value[:-1]]
    return tuple(value)


def syllable_word(value: tuple[Syllable, ...]) -> Word:
    return "".join(
        "c" if factor == "c" else ("t" * exponent if exponent > 0 else "T" * -exponent)
        for factor, exponent in value
    )


def cyclic_rotation_equal(left: tuple[Syllable, ...], right: tuple[Syllable, ...]) -> bool:
    return len(left) == len(right) and any(
        left == right[offset:] + right[:offset] for offset in range(len(right))
    )


def is_proper_power(value: tuple[Syllable, ...]) -> bool:
    if len(value) == 1:
        factor, exponent = value[0]
        return factor == "t" and abs(exponent) > 1
    return any(
        len(value) % period == 0
        and value == value[:period] * (len(value) // period)
        for period in range(1, len(value))
    )


def is_inverse_cyclic(value: tuple[Syllable, ...]) -> bool:
    inverse = tuple(
        (factor, exponent if factor == "c" else -exponent)
        for factor, exponent in reversed(value)
    )
    return cyclic_rotation_equal(value, inverse)


def ring(*terms: tuple[int, Word]) -> Ring:
    total: dict[Word, int] = defaultdict(int)
    for coefficient, word in terms:
        total[reduce_word(word)] += coefficient
    return {word: coefficient for word, coefficient in total.items() if coefficient}


def add(*values: Ring) -> Ring:
    return ring(*((coefficient, word)
                  for value in values for word, coefficient in value.items()))


def scale(value: Ring, coefficient: int) -> Ring:
    return ring(*((coefficient * entry, word) for word, entry in value.items()))


def multiply(left: Ring, right: Ring) -> Ring:
    return ring(*((left_entry * right_entry, multiply_word(left_word, right_word))
                  for left_word, left_entry in left.items()
                  for right_word, right_entry in right.items()))


def star(value: Ring) -> Ring:
    return ring(*((coefficient, inverse_word(word)) for word, coefficient in value.items()))


ONE = ring((1, ""))
ZERO: Ring = {}

# Literal order, slot, sign, raw quotient prefix.  This is intentionally
# duplicated from the certificate rather than imported from it.
OCCURRENCES: tuple[tuple[int, int, Word], ...] = (
    (2, 1, ""),
    (1, 1, "tc"),
    (0, 1, "tc"),
    (0, -1, "ctcTTTcttc"),
    (1, -1, "ctcTctt"),
    (2, -1, "ctcTcTctc"),
    (0, 1, "ctcTcTctc"),
    (0, -1, "ctcTTTTcttc"),
    (3, 1, "ctcTTctt"),
    (1, 1, "ctcTctc"),
    (0, 1, "ctcTctc"),
    (0, -1, "cTTcttc"),
    (1, -1, "tt"),
    (3, -1, "t"),
    (4, 1, "t"),
    (4, -1, ""),
)
OCCURRENCES = tuple((slot, sign, reduce_word(word)) for slot, sign, word in OCCURRENCES)
COUNTS = (3, 2, 1, 1, 1)


def operators() -> list[Ring]:
    return [ring(*((sign, word) for slot, sign, word in OCCURRENCES if slot == target))
            for target in range(5)]


def occurrence_hessian() -> Matrix:
    result: Matrix = [[ring((COUNTS[row], "")) if row == column else {}
                       for column in range(5)] for row in range(5)]
    for before, (row, row_sign, row_word) in enumerate(OCCURRENCES):
        for column, column_sign, column_word in OCCURRENCES[before + 1:]:
            term = ring((row_sign * column_sign,
                         multiply_word(inverse_word(row_word), column_word)))
            result[row][column] = add(result[row][column], term)
    return result


def gauged_h_circ() -> Matrix:
    value = occurrence_hessian()
    linear = operators()
    # (3.54): H-hat = H + L^* e_4.
    for row in range(5):
        value[row][4] = add(value[row][4], star(linear[row]))
    # (3.70): Q^out L, with Q^out_2=-q_1^{-1}, Q^out_3=-q_9^{-1}.
    for row, occurrence_index in ((2, 0), (3, 8)):
        factor = ring((-1, inverse_word(OCCURRENCES[occurrence_index][2])))
        for column in range(5):
            value[row][column] = add(value[row][column], multiply(factor, linear[column]))
    return value


def pinned(*terms: tuple[int, Word]) -> Ring:
    return ring(*terms)


# Separate expected dictionary: a literal transcription of the static ledger,
# not an expression in the occurrence construction above.
EXPECTED: dict[tuple[int, int], Ring] = {
    (0, 0): pinned((3, ""), (-3, "cTctcTTTcttc"), (1, "cTctcTcTctc"),
                    (-1, "cTctcTTTTcttc"), (1, "cTctcTctc"), (-1, "cTcTTcttc"),
                    (-1, "cTTcttcTctc"), (1, "cTTcTcttc"), (-1, "cTTcttctc"),
                    (1, "cTTctttcTTTcttc"), (1, "cTcttc"),
                    (-1, "cTctctcTTTcttc"), (-1, "cTTctttctc"),
                    (1, "cTTcttttcTTTcttc")),
    (0, 1): pinned((-2, "cTctcTctt"), (1, "cTctcTctc"), (-1, "ct"),
                    (2, "cTTcttctt"), (-1, "cTTcttctc"),
                    (1, "cTTctttcTctt"), (1, "cTcttc"),
                    (-1, "cTctctcTctt"), (-1, "cTTctttctc"),
                    (1, "cTTcttttcTctt")),
    (0, 2): pinned((-1, "cTctcTcTctc"), (1, "cTTcttcTctc")),
    (0, 3): pinned((1, "cTctcTTctt"), (-1, "c"), (-1, "cTTctctt"),
                    (1, "cTTctttcTct"), (1, "cTctcTctt"),
                    (-1, "cTctctcTct"), (-1, "cTTcttctt"),
                    (1, "cTTcttttcTct"), (-1, "cTctcTct"), (1, "cTTcttct")),
    (0, 4): pinned((1, "c"), (-1, "cTTctttcTct"), (1, "cTctctcTct"),
                    (-1, "cTTcttttcTct"), (1, "cTctcTct"), (-1, "cTTcttct")),
    (1, 0): pinned((2, ""), (-2, "cTctcTTTcttc"), (1, "cTctcTcTctc"),
                    (-1, "cTctcTTTTcttc"), (1, "cTctcTctc"), (-1, "cTcTTcttc"),
                    (-1, "TTTctc"), (1, "TTcTTTcttc"), (-1, "Tc"),
                    (1, "TTctcTTTcttc")),
    (1, 1): pinned((2, ""), (-2, "cTctcTctt"), (1, "cTctcTctc"), (-1, "ct"),
                    (-1, "Tc"), (1, "TTctcTctt")),
    (1, 2): pinned((-1, "cTctcTcTctc"), (1, "TTTctc")),
    (1, 3): pinned((1, "cTctcTTctt"), (-1, "c"), (-1, "TTcTctt"),
                    (1, "TTctcTct"), (-1, "cTctcTct"), (1, "T")),
    (1, 4): pinned((1, "c"), (-1, "TTctcTct"), (1, "cTctcTct"), (-1, "T")),
    (2, 0): pinned((-1, ""), (1, "cTctcTTTcttc"), (-1, "cTcttc"),
                    (1, "cTctctcTTTcttc")),
    (2, 1): pinned((-1, "cTcttc"), (1, "cTctctcTctt")),
    (2, 2): {},
    (2, 3): pinned((-1, "cTctcTctt"), (1, "cTctctcTct")),
    (2, 4): pinned((1, ""), (-1, "cTctctcTct")),
    (3, 0): pinned((-1, "TTcttcTctc"), (1, "TTcTcttc"),
                    (-1, "TTctcTctc"), (1, "TTcTTcttc")),
    (3, 1): pinned((-1, "TTcttcTctc"), (1, "TTctctt")),
    (3, 2): pinned((-1, "TTcttcTc"), (1, "TTctcTctc")),
    (3, 3): {},
    (3, 4): pinned((1, "TTcttcTc"), (-1, "")),
    (4, 0): {}, (4, 1): {}, (4, 2): {}, (4, 3): {}, (4, 4): {},
}

PURE_T_EXPECTED: dict[tuple[int, int], Ring] = {
    (0, 0): pinned((3, "")),
    (1, 0): pinned((2, "")),
    (1, 1): pinned((2, "")),
    (1, 3): pinned((1, "T")),
    (1, 4): pinned((-1, "T")),
    (2, 0): pinned((-1, "")),
    (2, 4): pinned((1, "")),
    (3, 4): pinned((-1, "")),
}

PAIRED_INTERVALS = ((3, 4), (7, 8), (11, 12), (2, 5),
                    (10, 13), (1, 6), (9, 14), (15, 16))
PAIR_AXIS_EXPECTED = (
    (3, 4, "cTctcTTTcttc", "ctcTTTct", (1, -3, 1), 3, -1, False, False),
    (7, 8, "cTctcTTTcttc", "ctcTTTct", (1, -3, 1), 3, -1, False, False),
    (11, 12, "cTctcTTTcttc", "ctcTTTct", (1, -3, 1), 3, -1, False, False),
    (2, 5, "cTctcTctt", "cTctcTctt", (-1, 1, -1, 2), 4, 1, False, False),
    (10, 13, "cTctcTctt", "cTctcTctt", (-1, 1, -1, 2), 4, 1, False, False),
    (1, 6, "ctcTcTctc", "cTcTctt", (-1, -1, 2), 3, 0, False, False),
    (9, 14, "TTcttcTct", "cttcTcT", (2, -1, -1), 3, 0, False, False),
    (15, 16, "T", "T", (-1,), 0, -1, False, False),
)


def formula_rows_23(linear: list[Ring]) -> dict[tuple[int, int], Ring]:
    q = [word for _, _, word in OCCURRENCES]
    left6 = ring((-1, inverse_word(q[5])))
    left9 = ring((-1, inverse_word(q[8])))
    return {
        (2, 0): multiply(left6, add(ring((1, q[6])), ring((-1, q[7])),
                                      ring((1, q[10])), ring((-1, q[11])))),
        (2, 1): multiply(left6, add(ring((1, q[9])), ring((-1, q[12])))),
        (2, 2): {},
        (2, 3): multiply(left6, linear[3]),
        (2, 4): add(star(linear[2]), multiply(left6, linear[4])),
        (3, 0): multiply(left9, add(ring((1, q[2])), ring((-1, q[3])),
                                      ring((1, q[6])), ring((-1, q[7])))),
        (3, 1): multiply(left9, add(ring((1, q[1])), ring((-1, q[4])))),
        (3, 2): multiply(left9, linear[2]),
        (3, 3): {},
        (3, 4): add(star(linear[3]), multiply(ring((-1, inverse_word(q[13]))), linear[4])),
    }


def augmentation(value: Ring) -> int:
    return sum(value.values())


def canonical_matrix(value: Matrix) -> str:
    return "|".join(
        f"{row}{column}:" + ",".join(f"{word or '1'}={coefficient}"
                                      for word, coefficient in sorted(value[row][column].items()))
        for row in range(5) for column in range(5)
    )


def main() -> None:
    actual = gauged_h_circ()
    linear = operators()
    assert set(EXPECTED) == {(row, column) for row in range(5) for column in range(5)}
    for key, expected in EXPECTED.items():
        row, column = key
        assert actual[row][column] == expected, (key, actual[row][column], expected)
    # (3.72) is independently checked against its printed row formulas.
    for key, expected in formula_rows_23(linear).items():
        row, column = key
        assert actual[row][column] == expected, ("(3.72)", key, actual[row][column], expected)
    # (3.73), and the complete augmentation assertion (3.87).
    assert all(actual[4][column] == {} for column in range(5))
    assert all(augmentation(actual[row][column]) == 0
               for row in range(5) for column in range(5))
    actual_pure = {
        (row, column): {word: coefficient for word, coefficient
                        in actual[row][column].items() if "c" not in word}
        for row in range(5) for column in range(5)
    }
    actual_pure = {key: value for key, value in actual_pure.items() if value}
    assert actual_pure == PURE_T_EXPECTED, (actual_pure, PURE_T_EXPECTED)
    pair_rows = []
    for start, end in PAIRED_INTERVALS:
        start_word = OCCURRENCES[start - 1][2]
        end_word = OCCURRENCES[end - 1][2]
        pair_word = multiply_word(inverse_word(start_word), end_word)
        cyclic = cyclic_syllables(pair_word)
        cycle = tuple(exponent for factor, exponent in cyclic if factor == "t")
        height = pair_word.count("t") - pair_word.count("T")
        expected_height = (end_word.count("t") - end_word.count("T")
                           - start_word.count("t") + start_word.count("T"))
        assert height == expected_height
        pair_rows.append((start, end, pair_word, syllable_word(cyclic), cycle,
                          sum(factor == "c" for factor, _ in cyclic), height,
                          is_proper_power(cyclic), is_inverse_cyclic(cyclic)))
    assert tuple(pair_rows) == PAIR_AXIS_EXPECTED, (pair_rows, PAIR_AXIS_EXPECTED)
    digest = sha256(canonical_matrix(actual).encode("ascii")).hexdigest()
    pair_digest = sha256(repr(pair_rows).encode("ascii")).hexdigest()
    support = tuple(sum(len(actual[row][column]) for column in range(5)) for row in range(5))
    print(f"Hcirc-static ok entries=25 row-support={support} digest={digest}")
    for row in pair_rows:
        print("pair-axis", row)
    print(f"pair-axis ok entries=8 digest={pair_digest}")


if __name__ == "__main__":
    main()
