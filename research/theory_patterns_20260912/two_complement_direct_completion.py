"""Deterministic unit-lift completion of saved marked Nielsen snapshots.

This module never invokes a heap, Nielsen candidate search, or a terminal search.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import time

from two_complement_probe import inv, red, row_move, verify_basis, stable_equivalence_witness, determinant, pair_key
from two_complement_probe_checks import verify_record

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def recognize_unit_lifts(images):
    """Inspect a four-tuple and give an exact compiler image-operation estimate."""
    if len(images) != 4 or any(set(w) - set('xXyY') or red(w) != w for w in images):
        raise ValueError('four reduced image words required')
    for axis in 'xy':
        units = [i for i, w in enumerate(images) if len(w) == 1 and w.lower() == axis]
        if not units:
            continue
        donor = units[0]
        other = 'y' if axis == 'x' else 'x'
        choices = [(len(w), j) for j, w in enumerate(images) if j != donor and w.lower().count(other) == 1]
        if not choices:
            continue
        _, lifted = min(choices)
        other_letter = next(c for c in images[lifted] if c.lower() == other)
        count = int(images[donor].isupper()) + len(images[lifted]) - 1 + int(other_letter.isupper())
        count += sum(len(w) for i, w in enumerate(images) if i not in (donor, lifted))
        return {'known_axis': axis, 'known_unit_row': donor, 'other_axis': other, 'other_lift_row': lifted,
                'known_unit_sign': -1 if images[donor].isupper() else 1,
                'other_lift_sign': -1 if other_letter.isupper() else 1,
                'word_operations': count, 'projection_word_images': 2,
                'word_operations_including_projection': count + 2}
    return None


def plan_unit_completion(images):
    recognition = recognize_unit_lifts(images)
    if recognition is None:
        return None
    current, operations, states = tuple(images), [], [list(images)]

    def emit(operation):
        nonlocal current
        current = row_move(current, operation)
        operations.append(operation)
        states.append(list(current))

    axis, donor, lifted = recognition['known_axis'], recognition['known_unit_row'], recognition['other_lift_row']
    if recognition['known_unit_sign'] == -1:
        emit({'op': 'invert', 'target': donor})
    while current[lifted] and current[lifted][0].lower() == axis:
        emit({'op': 'multiply', 'target': lifted, 'donor': donor,
              'sign': -1 if current[lifted][0].islower() else 1, 'side': 'left'})
    while len(current[lifted]) > 1:
        if current[lifted][-1].lower() != axis:
            raise AssertionError('single-occurrence lift factorization failed')
        emit({'op': 'multiply', 'target': lifted, 'donor': donor,
              'sign': -1 if current[lifted][-1].islower() else 1, 'side': 'right'})
    if recognition['other_lift_sign'] == -1:
        emit({'op': 'invert', 'target': lifted})
    lift_rows = {axis: donor, recognition['other_axis']: lifted}
    kernel_rows = [i for i in range(4) if i not in lift_rows.values()]
    for i in kernel_rows:
        while current[i]:
            c = current[i][0]
            emit({'op': 'multiply', 'target': i, 'donor': lift_rows[c.lower()],
                  'sign': -1 if c.islower() else 1, 'side': 'left'})
    order = [*kernel_rows, lift_rows['x'], lift_rows['y']]
    if order != list(range(4)):
        emit({'op': 'permute', 'order': order})
    count = sum(op['op'] != 'permute' for op in operations)
    if current != ('', '', 'x', 'y') or count != recognition['word_operations']:
        raise AssertionError('unit compiler estimate or final marking failed')
    return {**recognition, 'operations': operations, 'image_states': states,
            'images_after': list(current), 'word_operations': count}


def complete_snapshot(initial_images, snapshot, plan=None):
    """Complete an already marked snapshot; no projection or search is run."""
    verify_basis(initial_images, snapshot['images'], snapshot['domain_basis'], snapshot['nielsen_row_moves'])
    if plan is None:
        plan = plan_unit_completion(snapshot['images'])
    if plan is None:
        return {'status': 'unit_lift_not_recognized'}
    if plan['image_states'][0] != snapshot['images']:
        raise ValueError('unit plan belongs to another image snapshot')
    basis = tuple(snapshot['domain_basis'])
    for operation in plan['operations']:
        basis = row_move(basis, operation)
    path = [*snapshot['nielsen_row_moves'], *plan['operations']]
    result = verify_basis(initial_images, plan['images_after'], basis, path)
    return {'status': 'marked_kernel_basis_found', **result, 'compiler_word_operations': plan['word_operations'],
            'completion_plan': plan, 'best_image_length': 2,
            'prior_nielsen_move_count': len(snapshot['nielsen_row_moves']),
            'new_nielsen_move_count': len(plan['operations'])}


def canonical_witness(word):
    word = red(word); prefix, core = '', word
    while len(core) > 1 and core[0] == core[-1].swapcase():
        prefix += core[0]; core = core[1:-1]
    candidates = []
    for sign, base in ((1, core), (-1, inv(core))):
        for cut in range(max(1, len(base))):
            candidates.append((base[cut:] + base[:cut], sign, red(prefix + base[:cut])))
    target, sign, conjugator = min(candidates)
    if red(inv(conjugator) + (word if sign == 1 else inv(word)) + conjugator) != target:
        raise AssertionError('canonical projection witness failed')
    return target, {'sign': sign, 'conjugator': conjugator,
                    'elementary_word_operations': int(sign == -1) + len(conjugator)}


def structural_observations(pair):
    return [{'word': w, 'signed_counts': {c: w.count(c) for c in 'xXyY'},
             'cyclic_letter_changes': sum(a != b for a, b in zip(w, w[1:] + w[:1])),
             'absolute_generator_counts': {c: w.lower().count(c) for c in 'xy'},
             'literal_generator_row': len(w) == 1,
             'mixed_sign_generator': any(g in w and g.upper() in w for g in 'xy')}
            for w in pair]


def finish_all_existing_verified_bases(source):
    rows = []
    for source_index, old in enumerate(source['rows']):
        if not old['join_is_full']:
            continue
        verify_record(old)
        completed = complete_snapshot(old['initial_image_tuple'], old['search'])
        if completed['status'] != 'marked_kernel_basis_found':
            rows.append({'name': old['name'], 'status': completed['status'], 'source_row_index': source_index})
            continue
        witness = stable_equivalence_witness(old['input'], completed)
        raw_pair = witness['Q']
        if abs(determinant(raw_pair)) != 1:
            raise AssertionError('completed projection is not unimodular')
        normalized = [canonical_witness(w) for w in raw_pair]
        normalized_pair = [w for w, _ in normalized]
        projected = {'pair': raw_pair, 'total_length': sum(map(len, raw_pair)), 'determinant': determinant(raw_pair),
                     'cyclic_inverse_permutation_match': pair_key(raw_pair) == pair_key(old['input']),
                     'stable_equivalence_verified': True}
        replay_row = {**copy.deepcopy(old), 'search': completed, 'projected': projected,
                      'stable_equivalence_witness': witness, 'status': 'marked_kernel_basis_found'}
        checked = verify_record(replay_row)
        rows.append({'name': old['name'], 'input': old['input'], 'input_length': old['input_length'],
                     'source_row_index': source_index, 'source_snapshot_images': old['search']['images'],
                     'source_candidate_word_images': old['image_evaluations'],
                     'compiler_word_operations': completed['compiler_word_operations'],
                     'projection_word_images': 2,
                     'normalization_elementary_word_operations': sum(w['elementary_word_operations'] for _, w in normalized),
                     'conservative_candidate_plus_compiler_and_projection': old['image_evaluations'] + completed['compiler_word_operations'] + 2,
                     'completed_basis': completed, 'stable_equivalence_witness': witness,
                     'raw_projected_pair': raw_pair, 'raw_projected_total_length': sum(map(len, raw_pair)),
                     'canonical_projected_pair': normalized_pair,
                     'canonical_witnesses': [w for _, w in normalized],
                     'canonical_projected_total_length': sum(map(len, normalized_pair)),
                     'strict_gain_over_original': sum(map(len, normalized_pair)) < old['input_length'],
                     'exact_cyclic_inverse_permutation_return': pair_key(raw_pair) == pair_key(old['input']),
                     'Aut_orbit_comparison': 'verified_same' if pair_key(raw_pair) == pair_key(old['input']) else 'not_tested',
                     'structural_terminal_observations': structural_observations(normalized_pair),
                     'independent_verification': checked, 'status': 'completed_and_independently_replayed'})
    return rows


def checks():
    from two_complement_probe_checks import encode, decode, XENC, DENC, move, apply, inverse
    examples = [(['x', 'y', 'xy', 'yx'], ['r', 's', 't', 'u']),
                (['X', 'XXyXX', '', 'yx'], ['r', 's', 't', 'u']),
                (['Y', 'yyXy', 'xy', ''], ['r', 's', 't', 'u']),
                (['', '', 'x', 'y'], ['r', 's', 't', 'u'])]
    for images, basis in examples:
        plan = plan_unit_completion(images)
        assert plan is not None
        state = tuple(encode(w, XENC) for w in images)
        for operation, expected in zip(plan['operations'], plan['image_states'][1:]):
            state = move(state, operation)
            assert [decode(w, XENC) for w in state] == expected
        assert [decode(w, XENC) for w in state] == ['', '', 'x', 'y']
        snapshot = {'images': images, 'domain_basis': basis, 'nielsen_row_moves': []}
        result = complete_snapshot(images, snapshot, plan)
        assert result['images'] == ['', '', 'x', 'y']
    assert recognize_unit_lifts(['xx', 'yy', 'xyxy', '']) is None
    assert recognize_unit_lifts(['x', 'yy', 'XYXY', '']) is None
    for w in ['xyX', 'xyyYX', 'xYxyXY', '']:
        target, witness = canonical_witness(w)
        assert red(inv(witness['conjugator']) + (red(w) if witness['sign'] == 1 else inv(red(w))) + witness['conjugator']) == target
    return {'planted_unit_plans': len(examples), 'negative_recognizers': 2, 'canonical_controls': 4}


def main():
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    source_path = HERE / 'two_complement_probe_report.json'
    source = json.loads(source_path.read_text())
    started_cpu, started_wall = time.process_time(), time.perf_counter()
    control = checks()
    rows = finish_all_existing_verified_bases(source)
    report = {'status': 'direct_saved_snapshot_completion_verified', 'rows': rows,
              'source_report_sha256': sha(source_path), 'script_sha256': sha(Path(__file__)),
              'prototype_sha256': sha(HERE / 'two_complement_probe.py'),
              'independent_checker_sha256': sha(HERE / 'two_complement_probe_checks.py'),
              'source_panel_size': 20, 'source_full_join_rows': 15,
              'directly_completed_rows': sum(r['status'] == 'completed_and_independently_replayed' for r in rows),
              'newly_completed_prior_budget_rows': sum(r.get('source_snapshot_images') != ['', '', 'x', 'y'] and r['status'] == 'completed_and_independently_replayed' for r in rows),
              'strict_projected_gain_ids': [r['name'] for r in rows if r.get('strict_gain_over_original')],
              'solved_ids': [], 'compiler_word_operations': sum(r.get('compiler_word_operations', 0) for r in rows),
              'projection_word_images': sum(r.get('projection_word_images', 0) for r in rows),
              'normalization_elementary_word_operations': sum(r.get('normalization_elementary_word_operations', 0) for r in rows),
              'maximum_candidate_plus_compiler_and_projection': max(r.get('conservative_candidate_plus_compiler_and_projection', 0) for r in rows),
              'checks': control, 'cpu_seconds': time.process_time() - started_cpu,
              'wall_seconds': time.perf_counter() - started_wall,
              'scope': 'Only saved marked snapshots are completed; no heap or candidate search runs. Existing candidate work, deterministic compiler word operations, projection and ordinary canonicalization are separate ledgers. Several totals exceed1000, explicitly not a shared1k search claim. New smaller projections would be stable endpoints under the independently reviewed known-trivial-group bridge, not ordinary-equivalent endpoints.'}
    (HERE / 'two_complement_direct_completion_report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k:v for k,v in report.items() if k != 'rows'}, indent=2))


if __name__ == '__main__':
    main()
