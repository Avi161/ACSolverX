"""Strict donor descent with exact cyclic-length prefiltering."""
from experiments.equivalence_classes.lib.words import ORDER, apply_hom, canon_rel
from experiments.search.heuristic_1k import NIELSEN


def cyclic_length_deltas(word):
    """Return exact length changes for the four ordered Nielsen images."""
    nx = sum(letter in 'xX' for letter in word)
    ny = len(word) - nx
    edges = {}
    if word:
        for left, right in zip(word, word[1:] + word[:1]):
            edges[left, right] = edges.get((left, right), 0) + 1
    count = edges.get
    return (
        nx - 2 * (count(('x', 'Y'), 0) + count(('y', 'X'), 0)),
        nx - 2 * (count(('x', 'y'), 0) + count(('Y', 'X'), 0)),
        ny - 2 * (count(('y', 'X'), 0) + count(('x', 'Y'), 0)),
        ny - 2 * (count(('y', 'x'), 0) + count(('X', 'Y'), 0)),
    )


def match(word, evaluation_cap=400, **unused):
    if not isinstance(word, str) or any(c not in 'xXyY' for c in word):
        raise ValueError('word must use xXyY')
    if type(evaluation_cap) is not int or evaluation_cap < 1:
        raise ValueError('evaluation_cap must be positive integer')
    current = canon_rel(word)
    maps = []
    evaluations = 0
    while True:
        choices = []
        deltas = cyclic_length_deltas(current)
        for index, transform in enumerate(NIELSEN):
            if evaluations == evaluation_cap:
                return dict(status='unknown', input_analysis=dict(evaluations=evaluations), reason='evaluation_cap')
            evaluations += 1
            if deltas[index] >= 0:
                continue
            child = canon_rel(apply_hom(current, transform))
            if len(child) != len(current) + deltas[index]:
                raise AssertionError('cyclic length delta mismatch')
            choices.append((len(child), tuple(ORDER[c] for c in child), index, child))
        if not choices:
            return dict(status='match', template='strict_donor_endpoint', template_word=current,
                        maps=maps, input_analysis=dict(evaluations=evaluations, descent_steps=len(maps)))
        _, _, index, current = min(choices)
        maps.append(dict(NIELSEN[index]))
