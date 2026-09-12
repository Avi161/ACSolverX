"""Finite residual-pattern check for the rank-three length-at-most-twelve lemma.

This checks word substitutions combinatorially on unimodular tuples. Stable-AC
interpretation additionally requires known triviality of the presentation.
"""
from __future__ import annotations

from collections import Counter
from functools import lru_cache
from itertools import product
import json
from pathlib import Path


def free(word):
    stack = []
    for letter in word:
        if stack and stack[-1] == -letter:
            stack.pop()
        else:
            stack.append(letter)
    return tuple(stack)


def inverse(word):
    return tuple(-x for x in reversed(word))


def canonical(word):
    word = free(word)
    while len(word) > 1 and word[0] == -word[-1]:
        word = word[1:-1]
    if not word:
        return ()
    return min(base[i:] + base[:i] for base in (word, inverse(word)) for i in range(len(word)))


def determinant(rows, basis):
    a, b, c = [[sum((x == g) - (x == -g) for x in row) for g in basis] for row in rows]
    return a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0]) + a[2] * (b[0] * c[1] - b[1] * c[0])


def removal(rows, index, generator):
    donor = rows[index]
    positions = [i for i, x in enumerate(donor) if abs(x) == generator]
    if len(positions) != 1:
        raise ValueError('the donor must have exactly one occurrence')
    position = positions[0]
    left, right = donor[:position], donor[position + 1:]
    replacement = free(inverse(left) + inverse(right) if donor[position] > 0 else right + left)
    after = []
    for i, row in enumerate(rows):
        if i == index:
            continue
        image = tuple(t for x in row for t in
                      (replacement if x == generator else inverse(replacement) if x == -generator else (x,)))
        after.append(canonical(image))
    after = tuple(sorted(after))
    return {'before': rows, 'after': after, 'defining_index': index, 'generator': generator,
            'isolating_word': replacement, 'before_length': sum(map(len, rows)),
            'after_length': sum(map(len, after)),
            'interpretation': 'combinatorial substitution; stable AC additionally requires known triviality'}


def nonincreasing(rows):
    tested = 0
    for i, row in enumerate(rows):
        for generator, count in sorted(Counter(map(abs, row)).items()):
            if count == 1:
                tested += 1
                witness = removal(rows, i, generator)
                if witness['after_length'] <= witness['before_length']:
                    witness['tested_removal_candidates'] = tested
                    return witness
    return None


@lru_cache(None)
def pattern_words(counts, basis):
    letters = tuple(g for g, count in zip(basis, counts) for _ in range(count))
    unsigned = set()

    def permutations(prefix, remaining):
        if not remaining:
            unsigned.add(prefix)
            return
        for letter in set(remaining):
            index = remaining.index(letter)
            permutations(prefix + (letter,), remaining[:index] + remaining[index + 1:])

    permutations((), letters)
    result = set()
    for word in unsigned:
        for signs in product((1, -1), repeat=len(word)):
            signed = tuple(x * sign for x, sign in zip(word, signs))
            if free(signed) != signed or (signed and signed[0] == -signed[-1]):
                continue
            result.add(canonical(signed))
    return tuple(sorted(result))


def verify_residual_patterns(basis=(101, 307, 10**20)):
    if len(set(basis)) != 3 or any(type(g) is not int or g <= 0 for g in basis):
        raise ValueError('three distinct positive integer generators required')
    g, h, k = basis
    first = (g, h, h)
    cases = (
        ((6, 3, 3), (1, 0, 3), (4, 1, 0)),
        ((5, 3, 4), (3, 0, 1), (1, 1, 3)),
        ((5, 3, 4), (1, 0, 3), (3, 1, 1)),
        ((5, 4, 3), (3, 1, 0), (1, 1, 3)),
        ((5, 4, 3), (1, 1, 2), (3, 1, 1)),
    )
    summaries, witnesses, tested, unimodular = [], [], 0, 0
    for degrees, four_counts, five_counts in cases:
        case_tested, case_unimodular = 0, 0
        for four in pattern_words(four_counts, basis):
            for five in pattern_words(five_counts, basis):
                rows = (first, four, five)
                actual = tuple(sum(abs(x) == old for row in rows for x in row) for old in basis)
                assert actual == degrees and tuple(map(len, rows)) == (3, 4, 5)
                tested += 1
                case_tested += 1
                if abs(determinant(rows, basis)) != 1:
                    continue
                unimodular += 1
                case_unimodular += 1
                witness = nonincreasing(rows)
                if witness is None:
                    raise AssertionError(('counterexample', rows))
                witnesses.append(witness)
        summaries.append({'degrees': degrees, 'four_counts': four_counts, 'five_counts': five_counts,
                          'tested_presentations': case_tested, 'unimodular_presentations': case_unimodular})
    removal_checks = sum(w['tested_removal_candidates'] for w in witnesses)
    assert tested + removal_checks <= 1000
    return {'status': 'all_residual_patterns_have_nonincreasing_removal', 'basis': basis,
            'tested_presentations': tested, 'unimodular_presentations': unimodular,
            'removal_candidate_checks': removal_checks, 'combined_checks': tested + removal_checks,
            'patterns': summaries, 'witnesses': witnesses,
            'scope': 'complete finite residual cases after the proof reductions in rank3_low_length.md; no census search'}


if __name__ == '__main__':
    result = verify_residual_patterns()
    target = Path(__file__).with_name('rank3_low_length.json')
    target.write_text(json.dumps(result, indent=2) + '\n')
    print({k: result[k] for k in ('status', 'tested_presentations', 'unimodular_presentations', 'combined_checks')})
