"""Budgeted primitive-donor completion with explicit mixed/elementary witnesses."""
from experiments.equivalence_classes.lib.words import (
    abelian_det, apply_hom, apply_pair, canon_pair, canon_rel,
)
from experiments.search.heuristic_1k import NIELSEN
from research.supermoves_20260908.two_block import inverse, reduce_word, replay


class Exhausted(Exception):
    pass


def complete(pair, budget=1000, donor_word=None):
    if budget < 1:
        return {'solved': False, 'work': 0, 'reason': 'budget'}
    current = list(canon_pair(*pair))
    if abs(abelian_det(*current)) != 1:
        return {'solved': False, 'work': 1, 'reason': 'determinant'}
    states, steps, tail = [current[:]], [], []
    work = 1

    def charge(amount=1):
        nonlocal work
        if work + amount > budget:
            raise Exhausted
        work += amount

    def emit(move):
        nonlocal current
        charge()
        current = replay(current, [move])
        tail.append(move)

    def conjugate(target, word):
        for letter in word:
            emit(['C', target, letter])

    try:
        donor = min(current, key=lambda word: (len(word), word)) if donor_word is None else canon_rel(donor_word)
        if donor not in current:
            raise ValueError('specified donor is not in the canonical pair')
        while len(donor) > 1:
            choice = None
            for transform in NIELSEN:
                charge(len(donor))
                image = canon_rel(apply_hom(donor, transform))
                if len(image) < len(donor) and (choice is None or image < choice[0]):
                    choice = image, transform
            if choice is None:
                return {'solved': False, 'work': work, 'reason': 'no_strict_reduction'}
            donor, transform = choice
            charge(sum(map(len, current)))
            current = list(apply_pair(current, transform))
            states.append(current[:])
            steps.append({'kind': 'automorphism', 'images': transform})
            assert donor in current
        if len(donor) != 1:
            return {'solved': False, 'work': work, 'reason': 'empty_donor'}
        source = current.index(donor) + 1
        target = 3 - source
        while any(letter.lower() == donor.lower() for letter in current[target - 1]):
            word = current[target - 1]
            position = next(index for index, letter in enumerate(word)
                            if letter.lower() == donor.lower())
            letter, suffix = word[position], word[position + 1:]
            conjugate(source, suffix)
            flip = letter == donor
            if flip:
                emit(['I', source])
            emit(['M', target, source])
            if flip:
                emit(['I', source])
            conjugate(source, inverse(suffix))
            assert current[source - 1] == donor
            assert current[target - 1] == reduce_word(word[:position] + suffix)
        assert sorted(word.lower() for word in current) == ['x', 'y']
        for index in (1, 2):
            if current[index - 1].isupper():
                emit(['I', index])
        if current[0] != 'x':
            emit(['S'])
        assert current == ['x', 'y']
        return dict(solved=True, work=work, states=states, steps=steps, elementary_tail=tail)
    except Exhausted:
        return {'solved': False, 'work': work, 'reason': 'budget'}
