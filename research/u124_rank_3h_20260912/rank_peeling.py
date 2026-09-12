"""Length-nonincreasing Lemma11 removal, prioritized by occurrence accounting."""
from collections import Counter
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'rank_unbounded_20260912'))
import lemma11
import search


def pivots(words):
    degrees = Counter(abs(x) for word in words for x in word)
    choices = []
    for index, word in enumerate(words):
        for generator in lemma11.single_occurrences(word):
            bound = (degrees[generator] - 2) * (len(word) - 2) - 2
            choices.append((bound, degrees[generator], len(word), index, generator))
    return sorted(choices)


def descend(words, remaining):
    if type(remaining) is not int or not 0 <= remaining <= 1000:
        raise ValueError('remaining must be an integer in0..1000')
    current, normalization = lemma11.normalize_witness(words)
    events = [] if current == words else [{'kind': 'relator_normalization',
              'before': words, 'after': current, 'normalization': normalization}]
    used = 0
    while current:
        accepted = False
        for bound, degree, donor_length, index, generator in pivots(current):
            if used == remaining:
                return current, events, used, False
            used += 1
            after, event = lemma11.remove_one(current, index, generator)
            if search.length(after) - search.length(current) > bound:
                raise AssertionError('one-occurrence elimination exceeded its literal upper bound')
            if search.length(after) > search.length(current):
                continue
            event['occurrence_accounting'] = {'generator_degree': degree,
                'donor_length': donor_length, 'length_change_upper_bound': bound}
            current = after
            events.append(event)
            accepted = True
            break
        if not accepted:
            return current, events, used, True
    return current, events, used, True


def probe(words, remaining):
    after, events, charged, _ = descend(words, remaining)
    return ([(after, events)] if events else []), charged
