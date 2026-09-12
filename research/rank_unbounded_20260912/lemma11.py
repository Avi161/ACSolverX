"""Theorem-backed Lemma 11 removals on known trivial-group presentations.

The caller must establish triviality; unimodular abelianization is insufficient.
Work units count each attempted removal and each per-relator minimum cut. They
are not elementary AC moves or a bound on the lemma's normal-product expansion.
"""
from __future__ import annotations

from collections import Counter

from search import canonical, inverse, length, normalize, reduced
from whitehead import graph, minimum_cut, transform


def canonical_witness(word):
    original = reduced(word)
    core, prefix = original, ()
    while len(core) > 1 and core[0] == -core[-1]:
        prefix += core[:1]
        core = core[1:-1]
    if not core:
        return (), {'sign': 1, 'conjugator': ()}
    choices = [(base[k:] + base[:k], sign, reduced(prefix + base[:k]))
               for sign, base in ((1, core), (-1, inverse(core)))
               for k in range(len(core))]
    after, sign, conjugator = min(choices)
    if reduced(inverse(conjugator) + (original if sign == 1 else inverse(original))
               + conjugator) != after:
        raise AssertionError('canonical conjugation does not replay')
    return after, {'sign': sign, 'conjugator': conjugator}


def normalize_witness(words):
    rows = []
    for i, word in enumerate(words):
        after, witness = canonical_witness(word)
        rows.append({'input_index': i, 'before': tuple(word), 'after': after, **witness})
    rows.sort(key=lambda row: (row['after'], row['input_index']))
    return tuple(row['after'] for row in rows), rows


def single_occurrences(word):
    return sorted(g for g, count in Counter(map(abs, word)).items() if count == 1)


def substitute(word, generator, replacement):
    backward = inverse(replacement)
    return tuple(y for x in word for y in
                 (replacement if x == generator else backward if x == -generator else (x,)))


def remove_one(words, defining_index, generator):
    """Construct one exact removal; the caller charges its attempted evaluation."""
    words = tuple(tuple(w) for w in words)
    if any(reduced(w) != w for w in words):
        raise ValueError('remove_one requires freely reduced relators')
    if type(defining_index) is not int or not 0 <= defining_index < len(words):
        raise ValueError('invalid defining row')
    if type(generator) is not int or generator <= 0:
        raise ValueError('generator must be a positive integer')
    defining = words[defining_index]
    positions = [k for k, x in enumerate(defining) if abs(x) == generator]
    if len(positions) != 1:
        raise ValueError('the defining relator must contain the generator exactly once')
    position = positions[0]
    left, letter, right = defining[:position], defining[position], defining[position + 1:]
    if letter < 0:
        replacement, sign, conjugator = reduced(right + left), 1, left
    else:
        replacement, sign, conjugator = reduced(inverse(left) + inverse(right)), -1, inverse(right)
    normal_form = (-generator,) + replacement
    oriented = reduced(inverse(conjugator) + (defining if sign == 1 else inverse(defining))
                       + conjugator)
    if oriented != normal_form or generator in map(abs, replacement):
        raise AssertionError('isolating normal form does not replay')
    rows = []
    for i, word in enumerate(words):
        if i == defining_index:
            continue
        raw = substitute(word, generator, replacement)
        rows.append({'input_index': i, 'before': word, 'raw_substitution': raw,
                     'after_free_reduction': reduced(raw),
                     'replaced_occurrences': sum(abs(x) == generator for x in word)})
    raw_after = tuple(row['after_free_reduction'] for row in rows)
    after, normalization = normalize_witness(raw_after)
    occurrences = sum(row['replaced_occurrences'] for row in rows)
    literal_length = length(words) - len(defining) + occurrences * (len(replacement) - 1)
    if literal_length != sum(len(row['raw_substitution']) for row in rows):
        raise AssertionError('substitution length accounting differs')
    event = {'kind': 'lemma11_removal', 'certificate_kind': 'theorem_backed_stable_composite',
             'required_hypothesis': 'known balanced presentation of the trivial group',
             'before': words, 'defining_index': defining_index, 'defining_relator': defining,
             'generator': generator, 'occurrence_position': position, 'occurrence_sign': 1 if letter > 0 else -1,
             'isolating_word': replacement, 'normal_form': normal_form,
             'normal_form_witness': {'sign': sign, 'conjugator': conjugator},
             'substitutions': rows, 'raw_after': raw_after, 'normalization': normalization,
             'after': after, 'before_generator_ids': sorted({abs(x) for w in words for x in w}),
             'after_generator_ids': sorted({abs(x) for w in after for x in w}),
             'generator_relabeling': 'identity_on_survivors',
             'literal_substitution_length': literal_length, 'final_length': length(after),
             'length_change': length(after) - length(words), 'charged_units': 1,
             'fully_expanded_elementary_certificate': False}
    replay_removal(event)
    return after, event


def replay_removal(event):
    """Check a removal's word identities, including after a JSON round trip."""
    before = tuple(tuple(w) for w in event['before'])
    i, g = event['defining_index'], event['generator']
    defining = before[i]
    if defining != tuple(event['defining_relator']):
        raise AssertionError('defining row differs')
    positions = [k for k, x in enumerate(defining) if abs(x) == g]
    if positions != [event['occurrence_position']]:
        raise AssertionError('unique occurrence differs')
    w = tuple(event['isolating_word'])
    normal = (-g,) + w
    witness = event['normal_form_witness']
    c, sign = tuple(witness['conjugator']), witness['sign']
    if type(sign) is not int or sign not in (-1, 1) or any(abs(x) == g for x in w):
        raise AssertionError('invalid isolating witness')
    if tuple(event['normal_form']) != normal or reduced(inverse(c) +
            (defining if sign == 1 else inverse(defining)) + c) != normal:
        raise AssertionError('normal-form witness differs')
    expected_rows = [j for j in range(len(before)) if j != i]
    if [row['input_index'] for row in event['substitutions']] != expected_rows:
        raise AssertionError('a surviving row was omitted or duplicated')
    survivors = []
    for row in event['substitutions']:
        original = before[row['input_index']]
        if tuple(row['before']) != original:
            raise AssertionError('substitution input differs')
        pieces = []
        for x in original:
            pieces.extend(w if x == g else inverse(w) if x == -g else (x,))
        if tuple(pieces) != tuple(row['raw_substitution']):
            raise AssertionError('substitution expansion differs')
        word = reduced(pieces)
        if word != tuple(row['after_free_reduction']):
            raise AssertionError('substitution free reduction differs')
        survivors.append(word)
    if tuple(survivors) != tuple(tuple(w) for w in event['raw_after']):
        raise AssertionError('raw surviving tuple differs')
    after = tuple(tuple(w) for w in event['after'])
    if normalize(survivors) != after or len(after) != len(before) - 1:
        raise AssertionError('normalized removal endpoint differs')
    if any(abs(x) == g for word in after for x in word):
        raise AssertionError('removed generator survives')
    if event['final_length'] != length(after) or event['length_change'] != length(after) - length(before):
        raise AssertionError('reported removal length differs')
    normalized_rows = event['normalization']
    if sorted(row['input_index'] for row in normalized_rows) != list(range(len(survivors))):
        raise AssertionError('normalization omits a row')
    for row in normalized_rows:
        old = survivors[row['input_index']]
        c, sign = tuple(row['conjugator']), row['sign']
        if type(sign) is not int or sign not in (-1, 1):
            raise AssertionError('invalid normalization sign')
        if tuple(row['before']) != old or reduced(inverse(c) +
                (old if sign == 1 else inverse(old)) + c) != tuple(row['after']):
            raise AssertionError('normalization witness differs')
    if tuple(tuple(row['after']) for row in normalized_rows) != after:
        raise AssertionError('normalization order differs')
    return after


def _expose_target(words, target_index, available):
    current, path, charged = words, [], 0
    candidates = []
    while charged < available:
        target = current[target_index]
        eligible = single_occurrences(target)
        if eligible:
            for g in eligible:
                if charged == available:
                    break
                after, event = remove_one(current, target_index, g)
                charged += 1
                candidates.append((after, path + [event]))
            break
        if charged + 1 >= available or len(target) <= 1:
            break
        edges = graph((target,))
        vertices = sorted({v for edge in edges for v in edge})
        options, pass_cuts = [], 0
        for multiplier in vertices:
            if charged + 1 == available:
                break
            capacity, side = minimum_cut(edges, multiplier)
            charged += 1
            pass_cuts += 1
            degree = sum(n for edge, n in edges.items() if multiplier in edge)
            if capacity < degree:
                options.append((capacity - degree, multiplier, sorted(side)))
        if not options:
            break
        delta, multiplier, side = min(options)
        after, event = transform(current, multiplier, set(side))
        normalized, witnesses = normalize_witness(event['raw_after'])
        if normalized != after:
            raise AssertionError('Whitehead normalization differs')
        next_index = next(k for k, row in enumerate(witnesses) if row['input_index'] == target_index)
        if len(after[next_index]) - len(target) != delta:
            raise AssertionError('per-relator cut prediction differs from replay')
        event.update({'objective': 'expose_lemma11_defining_relator',
                      'target_index_before': target_index, 'target_index_after': next_index,
                      'target_length_change': delta, 'length_change': length(after) - length(current),
                      'normalization': witnesses, 'cut_evaluations_this_pass': pass_cuts,
                      'complete_cut_pass': pass_cuts == len(vertices)})
        path.append(event)
        current, target_index = after, next_index
    return candidates, charged


def generate_removals(words, remaining, *, expose_primitives=False):
    """Return ``(candidates, charged)`` with candidates ``[(after, events)]``.

    Direct removals are evaluated first. Optional per-relator Whitehead descent
    applies each selected map to the entire tuple and stops as soon as a unique
    occurrence permits Lemma 11, without requiring the target to become a letter.
    Failed cuts and duplicate outcomes still consume work. Only evaluated
    endpoints are ranked, by their complete final length. Labels are arbitrary
    signed integers, retained on survivors; no rank or length ceiling is imposed.
    """
    if type(remaining) is not int or remaining < 0:
        raise ValueError('remaining must be a nonnegative integer')
    before = tuple(tuple(w) for w in words)
    current, witnesses = normalize_witness(before)
    prefix = [] if current == before else [{'kind': 'relator_normalization',
                                           'before': before, 'after': current,
                                           'normalization': witnesses}]
    candidates, charged = [], 0
    for i, word in enumerate(current):
        for g in single_occurrences(word):
            if charged == remaining:
                break
            after, event = remove_one(current, i, g)
            charged += 1
            candidates.append((after, prefix + [event]))
        if charged == remaining:
            break
    if expose_primitives:
        for i, word in sorted(enumerate(current), key=lambda item: (len(item[1]), item[1], item[0])):
            if charged == remaining:
                break
            if single_occurrences(word):
                continue
            exposed, cost = _expose_target(current, i, remaining - charged)
            charged += cost
            candidates.extend((after, prefix + events) for after, events in exposed)
    candidates.sort(key=lambda candidate: (length(candidate[0]), candidate[0], len(candidate[1])))
    return candidates, charged
