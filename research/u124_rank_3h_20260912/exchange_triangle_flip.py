"""Rank-preserving diagonal flips on two triangular relators."""
from collections import Counter
import json
from pathlib import Path

import exchange_templates
import lemma11
import search
import verify
import whitehead


def frame(row, letter):
    sign = 1 if letter in row else -1
    signed = row if sign > 0 else search.inverse(row)
    position = signed.index(letter)
    return signed[position:] + signed[:position], {'sign': sign, 'conjugator': signed[:position]}


def score(words):
    return max(map(len, words), default=0), sum(len(w) >= 3 for w in words), search.length(words)


def generate(words, remaining):
    if type(remaining) is not int or not 0 <= remaining <= 1000:
        raise ValueError('remaining must be in0..1000')
    before = tuple(tuple(w) for w in words)
    if search.normalize(before) != before:
        raise ValueError('normalized input required')
    basis = sorted({abs(x) for row in before for x in row})
    if len(basis) != len(before) or any(len(row) > 3 for row in before):
        raise ValueError('balanced input with every row length at most3 required')
    degrees = Counter(abs(x) for row in before for x in row)
    out, seen, charged = [], {before}, 0
    for generator in basis:
        if charged == remaining:
            break
        charged += 1
        if degrees[generator] != 2:
            continue
        indices = [i for i, row in enumerate(before) if any(abs(x) == generator for x in row)]
        if len(indices) != 2 or any(len(before[i]) != 3 for i in indices):
            continue
        for i, j in (indices, indices[::-1]):
            if charged == remaining:
                break
            charged += 1
            donor, donor_frame = frame(before[i], -generator)
            target, target_frame = frame(before[j], generator)
            _, a, b = donor
            _, c, d = target
            forward = {x: (x,) for x in basis}
            backward = dict(forward)
            forward[generator] = search.reduced((a, generator, -c))
            backward[generator] = search.reduced((-a, generator, c))
            raw = tuple(whitehead.apply(row, forward) for row in before)
            after, normalization = lemma11.normalize_witness(raw)
            expected = list(before)
            expected[i], expected[j] = (-generator, b, c), (a, generator, d)
            assert after == search.normalize(expected) and len(after) == len(before)
            assert max(map(len, after), default=0) <= 3
            if after in seen:
                continue
            seen.add(after)
            event = {'kind': 'ambient_automorphism', 'before': before, 'after': after,
                     'images': forward, 'inverse_images': backward, 'raw_after': raw,
                     'normalization': normalization,
                     'triangle_flip': {'generator': generator, 'donor_index': i, 'target_index': j,
                                       'donor_frame': donor_frame, 'target_frame': target_frame,
                                       'oriented_before': (donor, target),
                                       'oriented_after': ((-generator, b, c), (a, generator, d)),
                                       'before_objective': score(before), 'after_objective': score(after),
                                       'rank_preserved': True, 'shortness_scope': 'macro endpoints; two Nielsen factors may have a length4 intermediate'},
                     'charged_units': 1}
            assert verify.verify_event(event, known_trivial=True) == after
            out.append((after, [event]))
    return sorted(out, key=lambda item: (score(item[0]), item[0])), charged


def controls():
    a, b, z = 101, 307, 10**20
    start = search.normalize(((-z, a, b), (z, -b, -b), (b,)))
    choices, charged = generate(start, 1000)
    endpoint, events = choices[0]
    assert score(start) == (3, 2, 7) and score(endpoint) == (3, 1, 5)
    assert len(endpoint) == 3
    current = start
    for event in json.loads(json.dumps(events)):
        assert tuple(map(tuple, event['before'])) == current
        current = verify.verify_event(event, known_trivial=True)
    for budget in (0, 1, 2, 3, 5):
        _, used = generate(start, budget)
        assert used <= budget
    larger = search.normalize(start + tuple((z + i,) for i in range(1, 9)))
    high, used = generate(larger, 1000)
    assert len(high[0][0]) == 11 and score(high[0][0])[:2] == (3, 1)
    sharing_start = search.normalize(((1, 2, 1, 2, 1), (1, 2, 1)))
    shared, event, work = exchange_templates.compress_dictionary(sharing_start, ((1, 2),), 1000)
    assert len(shared) == 3 and max(map(len, shared)) == 3
    assert verify.verify_event(event, known_trivial=True) == shared
    return {'triangle_flip': {'initial': start, 'endpoint': endpoint, 'events': events, 'charged_units': charged,
                             'known_triviality': 'b=1 implies z=1 from zBB, then a=1 from Zab.',
                             'scope': 'rank retained; macro endpoints have all relators of length at most3'},
            'rank11_control': {'initial': larger, 'endpoint': high[0][0], 'events': high[0][1], 'charged_units': used},
            'shared_binary_definition': {'initial': sharing_start, 'endpoint': shared, 'events': [event],
                                         'charged_units': work, 'helpers_used': 1, 'independent_prefix_helpers': 2,
                                         'known_triviality': 'aba=1 gives b=a^-2; ababa then gives a^-1=1.'},
            'census_runs': 0}


if __name__ == '__main__':
    result = controls()
    Path(__file__).with_name('exchange_triangle_flip_control.json').write_text(json.dumps(result, indent=2) + '\n')
    print({'status': 'PASS', 'flip_objective': [score(result['triangle_flip']['initial']), score(result['triangle_flip']['endpoint'])],
           'rank_retained': len(result['rank11_control']['endpoint']), 'shared_helpers': 1})
