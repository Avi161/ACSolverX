"""A sharp rank-four removal bound with an explicit ordinary donor escape."""
from collections import Counter
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'rank_unbounded_20260912'))
import lemma11
import rank3_low_length as independent
import verify


def build(basis=(101, 307, 10**20, 10**20 + 1)):
    g, h, u, v = basis
    if len(set(basis)) != 4 or any(type(x) is not int or x <= 0 for x in basis):
        raise ValueError('four distinct positive integer generator IDs required')
    rows = ((g, u, u), (h, v, v), (u, h, g, -h, -g), (v, g, h, -g, -h))
    checks = []
    for index, row in enumerate(rows):
        for generator, count in Counter(map(abs, row)).items():
            if count == 1:
                check = independent.removal(rows, index, generator)
                assert check['before_length'] == 16 and check['after_length'] == 17
                checks.append(check)
    assert len(checks) == 4
    matrix = [[sum((x == old) - (x == -old) for x in row) for old in basis] for row in rows]
    assert matrix == [[1, 0, 2, 0], [0, 1, 0, 2], [0, 0, 1, 0], [0, 0, 0, 1]]
    raw = rows[:2] + ((u, v), rows[3])
    current, normalization = lemma11.normalize_witness(raw)
    event = {'kind': 'normal_product_substitution', 'before': rows, 'target': 2,
             'factors': [{'donor_index': 3, 'sign': 1, 'conjugator': (v,)}],
             'raw_target_after': (u, v), 'after': current, 'normalization': normalization,
             'certificate_kind': 'ordinary_AC_normal_product'}
    assert verify.verify_event(event, known_trivial=False) == current
    events, boundaries = [event], [(4, 16), (4, sum(map(len, current)))]
    for generator in (v, g, h, u):
        available = [(len(row), index) for index, row in enumerate(current)
                     if sum(abs(x) == generator for x in row) == 1]
        assert available
        _, index = min(available)
        following, step = lemma11.remove_one(current, index, generator)
        assert verify.verify_event(step, known_trivial=True) == following
        independent_step = independent.removal(current, index, generator)
        assert independent_step['after'] == following
        events.append(step)
        current = following
        boundaries.append((len(current), sum(map(len, current))))
    assert current == ()
    return {'basis': basis, 'initial': rows, 'exponent_matrix': matrix, 'determinant': 1,
            'all_single_occurrence_checks': checks, 'events': events, 'rank_length_boundaries': boundaries,
            'known_triviality': 'With C=[g,h], rows give u=C, v=C^-1, g=u^-2, h=u^2; thus C=1 and all generators are 1.',
            'scope': 'Sharpness of the 4r bound for nonincreasing one-occurrence removal, not an AC counterexample.',
            'verification': 'Every initial removal independently increases16->17; one ordinary donor multiplication gives16->13, then four verified removals reach empty.',
            'charged_candidate_checks': len(checks) + 1 + 4}


if __name__ == '__main__':
    result = build()
    Path(__file__).with_name('exchange_rank4_sharp.json').write_text(json.dumps(result, indent=2) + '\n')
    print({'rank_length_boundaries': result['rank_length_boundaries'],
           'all_initial_removal_lengths': [x['after_length'] for x in result['all_single_occurrence_checks']],
           'charged_candidate_checks': result['charged_candidate_checks']})
