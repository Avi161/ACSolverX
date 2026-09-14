"""Replay saved ordinary rank3 AC suffixes from audited stable definitions.

No descent, candidate enumeration, or author word functions are imported.
"""
from __future__ import annotations

import copy
import csv
import hashlib
import json
from pathlib import Path
import time

from stable_dictionary_independent_audit import verify_prefix as verify_dictionary

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CODE = {'x': 1, 'X': -1, 'y': 2, 'Y': -2, 'z': 3, 'Z': -3}
CHAR = {v: k for k, v in CODE.items()}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def word(value):
    require(isinstance(value, str) and all(c in CODE for c in value), 'invalid free word')
    return tuple(CODE[c] for c in value)


def text(values):
    return ''.join(CHAR[v] for v in values)


def reduced(values):
    stack = []
    for value in values:
        if stack and stack[-1] == -value:
            stack.pop()
        else:
            stack.append(value)
    return tuple(stack)


def inverse(values):
    return tuple(-v for v in reversed(values))


def canonical(value):
    values = reduced(word(value))
    while len(values) > 1 and values[0] == -values[-1]:
        values = values[1:-1]
    choices = []
    for signed in (values, inverse(values)):
        choices.extend(text(signed[i:] + signed[:i]) for i in range(len(signed)))
    return min(choices, default='')


def replay_integer(initial, moves):
    state = [reduced(word(w)) for w in initial]
    boundaries = [list(map(text, state))]
    for move in moves:
        i = move['target']
        require(type(i) is int and 0 <= i < len(state), 'invalid elementary target')
        if move['op'] == 'AC1':
            state[i] = inverse(state[i])
        elif move['op'] == 'AC2':
            j = move['donor']
            require(type(j) is int and 0 <= j < len(state) and i != j, 'invalid elementary donor')
            state[i] = reduced(state[i] + state[j])
        elif move['op'] == 'AC3':
            letter = word(move['by'])
            require(len(letter) == 1, 'AC3 must have a one-letter conjugator')
            state[i] = reduced(inverse(letter) + state[i] + letter)
        else:
            raise ValueError('unknown elementary move')
        boundaries.append(list(map(text, state)))
    return boundaries


def replay_string(initial, moves):
    def collapse(value):
        previous = None
        while previous != value:
            previous = value
            for positive in 'xyz':
                value = value.replace(positive + positive.upper(), '').replace(positive.upper() + positive, '')
        return value
    state = [collapse(w) for w in initial]
    boundaries = [list(state)]
    for move in moves:
        i = move['target']
        if move['op'] == 'AC1':
            state[i] = state[i].swapcase()[::-1]
        elif move['op'] == 'AC2':
            state[i] = collapse(state[i] + state[move['donor']])
        else:
            c = move['by']
            state[i] = collapse(c.swapcase() + state[i] + c)
        boundaries.append(list(state))
    return boundaries


def verify_prefix(record):
    """Verify source definition and every ordinary AC step; return full minimum.

    The ordinary suffix is expanded and independently replayed by two reducers.
    The preceding rank2-to-rank3 definition remains a theorem-backed stable macro.
    """
    source = verify_dictionary(record['input'], record['source_witness'])
    result = record['result']
    require(source['rank'] == result['rank'] == 3, 'wrong suffix rank')
    state = list(source['relators'])
    moves = []

    def emit(move):
        nonlocal state
        moves.append(move)
        state = replay_integer(state, [move])[-1]

    def conjugate(i, by):
        for c in by:
            emit({'op': 'AC3', 'target': i, 'by': c})

    def normalize(i, witness, expected):
        before = state[i]
        sign = witness['sign']
        require(type(sign) is int and sign in (1, -1), 'invalid canonical sign')
        word(witness['conjugator'])
        if sign == -1:
            emit({'op': 'AC1', 'target': i})
        conjugate(i, witness['conjugator'])
        require(state[i] == expected == canonical(before), 'canonical witness failed')

    initial = result['initial_normalization']
    require(initial['before'] == state, 'normalization attached to wrong dictionary tuple')
    require(len(initial['after']) == len(initial['canonical_witnesses']) == 3, 'initial normalization arity')
    for i in range(3):
        normalize(i, initial['canonical_witnesses'][i], initial['after'][i])
    require(state == initial['after'], 'initial whole tuple normalization differs')
    stage_endpoints = [{'label': 'initial_canonical_tuple', 'relators': list(state), 'move_count': len(moves)}]
    for index, step in enumerate(result['steps']):
        require(step['before'] == state, 'substitution input boundary differs')
        i, j, sign = step['target'], step['donor'], step['donor_sign']
        require(type(i) is int and type(j) is int and 0 <= i < 3 and 0 <= j < 3 and i != j, 'invalid substitution roles')
        require(type(sign) is int and sign in (1, -1), 'invalid substitution sign')
        old_state = list(state)
        target_cut, donor_cut = step['target_cut'], step['donor_cut']
        base = state[j] if sign == 1 else text(inverse(word(state[j])))
        require(type(target_cut) is int and 0 <= target_cut < max(1, len(state[i])), 'invalid target cut')
        require(type(donor_cut) is int and 0 <= donor_cut < max(1, len(base)), 'invalid donor cut')
        target_prefix, donor_prefix = state[i][:target_cut], base[:donor_cut]
        conjugate(i, target_prefix)
        if sign == -1:
            emit({'op': 'AC1', 'target': j})
        conjugate(j, donor_prefix)
        require(state[i] == old_state[i][target_cut:] + old_state[i][:target_cut], 'target rotation failed')
        require(state[j] == base[donor_cut:] + base[:donor_cut], 'donor rotation failed')
        emit({'op': 'AC2', 'target': i, 'donor': j})
        require(state[i] == step['raw_product'], 'raw multiplication boundary differs')
        conjugate(j, text(inverse(word(donor_prefix))))
        if sign == -1:
            emit({'op': 'AC1', 'target': j})
        require(state[j] == old_state[j], 'donor not restored')
        require(all(state[k] == old_state[k] for k in range(3) if k != i), 'bystander changed')
        normalize(i, step['canonical_witness'], step['after'][i])
        require(state == step['after'] and step['rank'] == 3, 'post-substitution tuple differs')
        require(sum(map(len, state)) == step['total_length'] < sum(map(len, old_state)), 'accepted substitution is not strict total descent')
        stage_endpoints.append({'label': f'substitution_{index}', 'relators': list(state), 'move_count': len(moves)})
    require(state == result['endpoint'] and sum(map(len, state)) == result['total_length'], 'suffix endpoint differs')
    require(record['improves_prefix'] == (result['total_length'] < source['total_length']), 'prefix improvement flag differs')
    integers = replay_integer(source['relators'], moves)
    strings = replay_string(source['relators'], moves)
    require(integers == strings, 'independent replay implementations disagree')
    minimum_index = min(range(len(integers)), key=lambda index: (sum(map(len, integers[index])), index))
    minimum = integers[minimum_index]
    return {'relators': minimum, 'rank': 3, 'relator_lengths': list(map(len, minimum)),
            'total_length': sum(map(len, minimum)), 'independently_verified': True,
            'endpoint': state, 'endpoint_total_length': sum(map(len, state)),
            'dictionary_total_length': source['total_length'], 'dictionary_prefix_verified': True,
            'elementary_moves': moves, 'elementary_move_count': len(moves),
            'ordinary_suffix_start': source['relators'], 'ordinary_suffix_minimum_move_index': minimum_index,
            'all_ordinary_suffix_boundaries': integers, 'stage_endpoints': stage_endpoints,
            'certificate_kind': 'theorem_backed_stable_definition_then_independently_replayed_strict_ordinary_AC_suffix'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    started_cpu, started_wall = time.process_time(), time.perf_counter()
    report_path = HERE / 'stable_rank3_ac_descent_report.json'
    report = json.loads(report_path.read_text())
    dictionary_path = HERE / 'stable_dictionary_compression_report.json'
    dictionary = json.loads(dictionary_path.read_text())
    require(report['source_report_sha256'] == sha(dictionary_path), 'dictionary source report changed')
    reporting_sha = report.get('metadata_correction', {}).get('current_reporting_script_sha256', report['script_sha256'])
    require(reporting_sha == sha(HERE / 'stable_rank3_ac_descent.py'), 'descent reporting source changed')
    source_rows = {r['name']: r for r in dictionary['rows'] if r['best'] is not None}
    require(len(source_rows) == len(report['rows']) == 84, 'rank3 panel differs')
    seen, ledger, positive, combined_work = set(), [], [], []
    for index, row in enumerate(report['rows']):
        require(row['name'] not in seen and row['name'] in source_rows, 'duplicate or unknown rank3 row')
        seen.add(row['name'])
        original = source_rows[row['name']]
        require(row['input'] == original['input'] and row['source_witness'] == original['best'], 'exact dictionary join differs')
        count = row['result']['substitutions']
        require(type(count) is int and 0 <= count <= 1000, 'invalid logged suffix budget')
        combined = original['candidate_definitions'] + count
        require(combined <= 1000, 'combined definition-candidate and suffix-child budget exceeded')
        combined_work.append(combined)
        checked = verify_prefix(row)
        checked['json_pointer'] = f'/rows/{index}'
        ledger.append({'name': row['name'], 'input': row['input'], 'input_length': original['input_length'],
                       'minimum_rank3_total_length': checked['total_length'], 'minimum_rank3_witness': checked,
                       'all_rank_minimum_total_length': min(original['input_length'], checked['total_length']),
                       'rank2_endpoint_minimum_length': original['input_length'],
                       'rank2_endpoint_strict_gain': False,
                       'all_rank_strict_gain': checked['total_length'] < original['input_length'],
                       'improves_dictionary_prefix': checked['total_length'] < original['best']['total_length'],
                       'logged_definition_candidates': original['candidate_definitions'],
                       'logged_substitution_children': count, 'combined_logged_work': combined})
        if row['improves_prefix']:
            positive.append(row['name'])
    require(positive == report['prefix_improvement_ids'] == ['aca_24'], 'prefix gain list differs')
    require(sum(r['result']['substitutions'] for r in report['rows']) == report['substitutions'] == 36328, 'suffix count total differs')
    require(max(r['result']['substitutions'] for r in report['rows']) == report['maximum_substitutions_per_row'] == 640, 'suffix maximum differs')
    require(sum(len(r['result']['steps']) for r in report['rows']) == report['strict_steps'] == 1, 'step total differs')
    example = next(r for r in report['rows'] if r['name'] == 'aca_24')
    damaged = []
    for field, value in [('donor_sign', -1), ('donor_cut', 3), ('target_cut', True), ('raw_product', 'x')]:
        bad = copy.deepcopy(example); bad['result']['steps'][0][field] = value; damaged.append(bad)
    for bad in damaged:
        try:
            verify_prefix(bad)
        except ValueError:
            pass
        else:
            raise AssertionError('corrupted ordinary suffix accepted')
    result = {'status': 'pass', 'source_report_sha256': sha(report_path),
              'source_report': str(report_path), 'audit_script_sha256': sha(Path(__file__)),
              'author_script_sha256': sha(HERE / 'stable_rank3_ac_descent.py'),
              'original_executed_author_script_sha256': report['script_sha256'],
              'dictionary_source_report_sha256': sha(dictionary_path),
              'dictionary_auditor_sha256': sha(HERE / 'stable_dictionary_independent_audit.py'),
              'source_csv_sha256': dictionary['source_sha256'], 'rows': ledger,
              'counts': {'source_rows': 84, 'ordinary_suffixes_replayed': 84,
                         'strict_substitution_steps': 1, 'extra_prefix_gain_rows': 1,
                         'logged_substitution_children': 36328,
                         'maximum_logged_substitution_children': 640,
                         'maximum_combined_logged_work_per_input': max(combined_work),
                         'corruptions_rejected': len(damaged)},
              'prefix_improvement_ids': positive, 'solved_ids': [], 'rank2_gain_ids': [],
              'scope': 'All 84 saved suffixes including initial canonicalizations independently replayed; no negative local-minimality enumeration rerun. Every intermediate elementary rank3 state is retained and all3 relators counted. Stable definition is theorem-backed, ordinary suffix is explicit.',
              'metadata_note': 'A stop reason no_strict_AC_substitution_descent describes the final endpoint. It does not imply that the row made no earlier improvement; aca24 has one strict step before that stop.',
              'budget_units': 'Combined logged work adds defining-word candidates to substitution child evaluations. This bounds declared candidate work, not total elementary stable-definition expansion or all cyclic-tokenization dynamic-program operations.',
              'cpu_seconds': time.process_time() - started_cpu,
              'wall_seconds': time.perf_counter() - started_wall}
    (HERE / 'stable_rank3_ac_independent_audit.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k:v for k,v in result.items() if k!='rows'}, indent=2))


if __name__ == '__main__':
    main()
