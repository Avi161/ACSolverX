"""Witnessed strict donor shortening; no claim of complete orbit recognition."""
from experiments.equivalence_classes.lib.words import ORDER, apply_hom, canon_rel
from experiments.search.heuristic_1k import NIELSEN


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
        for index, transform in enumerate(NIELSEN):
            if evaluations == evaluation_cap:
                return dict(status='unknown', input_analysis=dict(evaluations=evaluations), reason='evaluation_cap')
            child = canon_rel(apply_hom(current, transform))
            evaluations += 1
            if len(child) < len(current):
                choices.append((len(child), tuple(ORDER[c] for c in child), index, child))
        if not choices:
            return dict(status='match', template='strict_donor_endpoint', template_word=current,
                        maps=maps, input_analysis=dict(evaluations=evaluations, descent_steps=len(maps)))
        _, _, index, current = min(choices)
        maps.append(dict(NIELSEN[index]))
