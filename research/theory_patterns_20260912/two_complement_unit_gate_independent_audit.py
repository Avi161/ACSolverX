"""Independent gate accounting and elementary suffix replay; never runs search."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import time

import two_complement_probe_checks as independent

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ENCODE = {'x': 1, 'X': -1, 'y': 2, 'Y': -2}
DECODE = {v: k for k, v in ENCODE.items()}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def reduced(word):
    stack = []
    for value in word:
        if stack and value == -stack[-1]:
            stack.pop()
        else:
            stack.append(value)
    return tuple(stack)


def word(text):
    require(isinstance(text, str) and all(c in ENCODE for c in text), 'invalid rank2 word')
    return tuple(ENCODE[c] for c in text)


def display(values):
    return ''.join(DECODE[c] for c in values)


def replay_elementary(initial, moves, boundaries=None):
    """Independently replay strict one-based AC1/AC2/letter-AC3 and retain min."""
    require(isinstance(initial, (list, tuple)) and len(initial) == 2, 'two ordinary relators required')
    state = [reduced(word(w)) for w in initial]
    minimum = list(state); minimum_index = 0; minimum_length = sum(map(len, state))
    maximum_total = minimum_length
    total_lengths = [minimum_length]
    checkpoints = {}
    for boundary in boundaries or []:
        count = boundary['move_count']
        require(type(count) is int and 0 <= count <= len(moves), 'boundary index out of range')
        checkpoints.setdefault(count, []).append(boundary['pair'])

    def check_boundary(index):
        for expected in checkpoints.get(index, []):
            require(expected == list(map(display, state)), 'elementary boundary differs')

    check_boundary(0)
    for index, move in enumerate(moves, 1):
        target = move['target']
        require(type(target) is int and target in (1, 2), 'invalid elementary target')
        i = target - 1
        if move['op'] == 'invert':
            state[i] = tuple(-v for v in reversed(state[i]))
        elif move['op'] == 'multiply':
            donor = move['source']
            require(type(donor) is int and donor == 3 - target, 'invalid elementary donor')
            state[i] = reduced(state[i] + state[donor - 1])
        elif move['op'] == 'conjugate':
            conjugator = word(move['by'])
            require(len(conjugator) == 1, 'conjugation is not a single-letter AC3')
            state[i] = reduced((-conjugator[0],) + state[i] + conjugator)
        else:
            raise ValueError('not a strict elementary AC operation')
        length = sum(map(len, state))
        total_lengths.append(length)
        maximum_total = max(maximum_total, length)
        if length < minimum_length:
            minimum, minimum_length, minimum_index = list(state), length, index
        check_boundary(index)
    return {'relators': list(map(display, minimum)), 'rank': 2,
            'relator_lengths': list(map(len, minimum)), 'total_length': minimum_length,
            'minimum_move_index': minimum_index, 'endpoint': list(map(display, state)),
            'endpoint_total_length': sum(map(len, state)), 'elementary_move_count': len(moves),
            'maximum_replayed_total_length': maximum_total, 'boundaries_verified': len(boundaries or []),
            'replayed_total_lengths': total_lengths,
            'independently_verified': True}


def verify_marked_bridge(row):
    """Independent marked-basis replay allowing the explicitly declared q=2/3."""
    pair, complements = row['input'], row['complements']
    require(complements in (['x', 'yy'], ['x', 'yyy']), 'undeclared two-complement family')
    require(row['initial_image_tuple'] == [*pair, *complements], 'image tuple differs from declared complements')
    full = independent.independent_full_fold(row['initial_image_tuple'])
    require(full == row['join_is_full'], 'independent join fold differs')
    if not full:
        require(row['projected'] is None and row['status'] == 'join_not_full', 'proper join was admitted')
        return {'join_rejected': True, 'basis_verified': False, 'projected_verified': False}
    search = row['search']
    images = tuple(independent.encode(w, independent.XENC) for w in row['initial_image_tuple'])
    basis = tuple((i,) for i in range(1, 5))
    for operation in search['nielsen_row_moves']:
        images, basis = independent.move(images, operation), independent.move(basis, operation)
    require([independent.decode(w, independent.XENC) for w in images] == search['images'], 'marked image path differs')
    require([independent.decode(w, independent.DENC) for w in basis] == search['domain_basis'], 'marked domain path differs')
    backwards = tuple(independent.encode(w, independent.DENC) for w in search['inverse_domain_basis'])
    for i in range(4):
        require(independent.apply(basis[i], dict(enumerate(backwards, 1))) == (i + 1,), 'basis inverse forward composition failed')
        require(independent.apply(backwards[i], dict(enumerate(basis, 1))) == (i + 1,), 'basis inverse backward composition failed')
    mapping = {i + 1: independent.encode(w, independent.XENC) for i, w in enumerate(row['initial_image_tuple'])}
    require([independent.apply(w, mapping) for w in basis] == list(images), 'full basis f-marking failed')
    projected = row['projected']
    if projected is None:
        return {'join_rejected': False, 'basis_verified': True, 'projected_verified': False}
    require(search['images'] == ['', '', 'x', 'y'], 'kernel/target basis terminal marking differs')

    def project(values):
        return reduced(tuple((abs(v) - 2) * (1 if v > 0 else -1) for v in values if abs(v) > 2))

    q_pair = [display(project(w)) for w in basis[:2]]
    p_pair = [display(project(w)) for w in backwards[:2]]
    require(q_pair == projected['pair'], 'kernel projection does not give Q')
    require(p_pair == pair, 'inverse marking does not give literal P')
    q_vectors = [(w.count('x') - w.count('X'), w.count('y') - w.count('Y')) for w in q_pair]
    q_det = q_vectors[0][0] * q_vectors[1][1] - q_vectors[0][1] * q_vectors[1][0]
    require(abs(q_det) == 1 and q_det == projected['determinant'], 'projected determinant differs')
    require(projected['total_length'] == sum(map(len, q_pair)), 'raw projected length differs')
    witness = row['stable_equivalence_witness']
    require(witness['P'] == pair and witness['Q'] == q_pair, 'bridge endpoints differ')
    require(witness['kernel_basis'] == search['domain_basis'] and witness['inverse_basis'] == search['inverse_domain_basis'], 'bridge basis marking differs')
    require(witness['rank4_tuple'] == ['r', 's', *search['domain_basis'][:2]], 'rank4 bridge omits or changes a relator')
    require(witness['theta_r_s_after_killing_kernel_coordinates'] == pair, 'declared inverse marking differs')
    require(witness['maximum_displayed_rank'] == 4 and witness['maximum_rank_using_one_helper_ambient_macro'] == 5 and witness['ordinary_equivalence_claimed'] is False, 'bridge rank/scope metadata differs')
    expected_theta = [w.translate(str.maketrans('rRsStTuU', 'rRsSxXyY')) for w in search['inverse_domain_basis']]
    require(witness['theta_old_generator_images_in_coordinates_R_S_x_y'] == expected_theta, 'ambient marking spelling differs')
    return {'join_rejected': False, 'basis_verified': True, 'projected_verified': True}


def verify_gate(row):
    """Replay full marked basis/bridge plus unit-plan accounting and reserve."""
    require(row['input_length'] == sum(map(len, row['input'])), 'original total length differs')
    vectors = [(w.count('x') - w.count('X'), w.count('y') - w.count('Y')) for w in row['input']]
    require(abs(vectors[0][0] * vectors[1][1] - vectors[0][1] * vectors[1][0]) == 1, 'original exponent matrix is not unimodular')
    checked = verify_marked_bridge(row)
    if 'original_input' in row:
        bridge = row['input_bridge']
        require(bridge == {'ordinary_invert_relator': 2, 'ambient_images': {'x': 'y', 'y': 'x'},
                           'inverse_ambient_images': {'x': 'y', 'y': 'x'}}, 'undeclared prepared-input bridge')
        original = [word(w) for w in row['original_input']]
        require(row['original_input_length'] == sum(map(len, original)), 'prepared-input original length differs')
        original[1] = tuple(-v for v in reversed(original[1]))
        mapped = [display(tuple((3 - abs(v)) * (1 if v > 0 else -1) for v in w)) for w in original]
        require(mapped == row['input'], 'input inversion and ambient axis-swap bridge differs')
        checked['input_bridge_verified'] = True
    counts = row['image_evaluation_counts']
    require(all(type(n) is int and n >= 0 for n in counts.values()), 'invalid charge bucket')
    require(sum(counts.values()) == row['image_evaluations'] <= row['image_limit'] == 1000, 'shared prefix budget differs')
    require(row['remaining_shared_budget'] == row['image_limit'] - row['image_evaluations'], 'remaining budget differs')
    if not row['join_is_full']:
        require(row['image_evaluations'] == 0, 'proper-join rejection spent undeclared image work')
        return {**checked, 'charged_prefix_units': 0, 'remaining_shared_budget': row['remaining_shared_budget']}
    if not checked['projected_verified']:
        return {**checked, 'charged_prefix_units': row['image_evaluations'],
                'remaining_shared_budget': row['remaining_shared_budget']}
    search = row['search']
    require(search['status'] == 'marked_kernel_basis_found', 'saved full join not completed')
    plan, recognition = search['unit_completion_plan'], search['unit_goal_recognition']
    require(plan == search['completion_plan'], 'duplicate completion plans differ')
    require(plan['image_states'][0] == search['unit_goal_image_tuple'], 'unit gate input differs')
    require(plan['images_after'] == plan['image_states'][-1] == ['', '', 'x', 'y'], 'unit plan marking differs')
    require(len(plan['image_states']) == len(plan['operations']) + 1, 'unit-plan state count differs')
    state = tuple(independent.encode(w, independent.XENC) for w in plan['image_states'][0])
    product_count, inverse_count = 0, 0
    for operation, expected in zip(plan['operations'], plan['image_states'][1:]):
        before = sum(map(len, state))
        state = independent.move(state, operation)
        require([independent.decode(w, independent.XENC) for w in state] == expected, 'unit-plan image step differs')
        if operation['op'] == 'multiply':
            require(sum(map(len, state)) == before - 1, 'unit compiler did not remove exactly one letter')
            product_count += 1
        elif operation['op'] == 'invert':
            require(sum(map(len, state)) == before, 'unit inversion changed length')
            inverse_count += 1
        else:
            require(operation['op'] == 'permute' and sum(map(len, state)) == before, 'invalid unit plan operation')
    require(product_count == sum(map(len, plan['image_states'][0])) - 2, 'natural-number compiler bound differs')
    require(inverse_count <= 2, 'unexpected unit sign inversions')
    compiler_count = product_count + inverse_count
    require(compiler_count == plan['word_operations'] == recognition['word_operations'] == search['compiler_word_operations'] == counts['unit_completion_word_images'], 'compiler exact-cost reservation differs')
    require(counts['kernel_projection_word_images'] == 2, 'two projections were not charged')
    require(search['reserved_completion_and_projection_units'] == compiler_count + 2, 'reserved completion total differs')
    require(search['work_before_completion'] + compiler_count + 2 == row['image_evaluations'] <= row['image_limit'], 'reservation did not precede bounded completion')
    if search['unit_goal_location'] == 'direct':
        require(checked.get('input_bridge_verified') is True, 'direct compiler lacks audited input preparation')
        expected_direct = ([{'op': 'multiply', 'target': 1, 'donor': 2, 'sign': -1, 'side': 'right'}] * 4
                           + [{'op': 'multiply', 'target': 1, 'donor': 3, 'sign': 1, 'side': 'right'}] * 3)
        require(search['nielsen_row_moves'][:search['prior_nielsen_move_count']] == expected_direct, 'direct Euclidean marking differs')
        require(counts == {'input_inversion_and_two_ambient_word_images': 3, 'initial_image_words': 4,
                           'direct_Euclidean_image_updates': 7, 'unit_completion_word_images': compiler_count,
                           'kernel_projection_word_images': 2}, 'direct prefix charge buckets differ')
        require(search['work_before_completion'] == 3 + 4 + len(expected_direct), 'direct prefix reservation differs')
        require(plan['image_states'][0] == [row['input'][0], 'Y', 'x', 'yy'], 'direct Euclidean unit not exposed')
    else:
        require(search['guards'] == {}, 'unexpected guard requires a different candidate accounting audit')
        generated = search['generated_candidates']
        require(counts['multiplication_candidate_images'] == generated and counts['row_inverse_images'] == generated + 4, 'candidate/inversion charge arithmetic differs')
        require(search['work_before_completion'] == 4 + 2 * generated, 'prefix candidate total differs')
    prefix = search['nielsen_row_moves'][:search['prior_nielsen_move_count']]
    state = tuple(independent.encode(w, independent.XENC) for w in row['initial_image_tuple'])
    for operation in prefix:
        state = independent.move(state, operation)
    require([independent.decode(w, independent.XENC) for w in state] == search['unit_goal_image_tuple'], 'saved unit-goal boundary is not on marked path')
    require(search['nielsen_row_moves'][search['prior_nielsen_move_count']:] == plan['operations'], 'compiler path does not concatenate with source')
    return {**checked, 'charged_prefix_units': row['image_evaluations'],
            'remaining_shared_budget': row['remaining_shared_budget'],
            'compiler_word_operations': compiler_count, 'projection_word_images': 2,
            'marked_projected_pair': row['projected']['pair'], 'stable_bridge_verified': True}


def verify_reservation_controls():
    import two_complement_unit_gate as subject
    import types
    compiler = subject.completion_module()
    calls = Counter()

    def plan(images):
        calls['plans'] += 1
        return compiler.plan_unit_completion(images)

    def complete(*args, **kwargs):
        calls['completions'] += 1
        return compiler.complete_snapshot(*args, **kwargs)

    facade = types.SimpleNamespace(recognize_unit_lifts=compiler.recognize_unit_lifts,
                                  plan_unit_completion=plan, complete_snapshot=complete)
    original_loader = subject.completion_module
    subject.completion_module = lambda: facade
    passed = 0
    try:
        initial = ['x', 'y', 'x', 'yy']
        for limit, prior, expected in ((4, 0, False), (5, 0, True), (10, 6, False), (10, 5, True)):
            budget = subject.prototype.Budget(limit)
            if prior:
                budget.charge('prior_control_work', prior)
            counters = Counter(); before_calls = dict(calls)
            result = subject.finish_if_possible(initial, (tuple(initial), tuple('rstu'), []), budget, counters, 'control')
            require((result is not None) == expected, 'reservation threshold control failed')
            if expected:
                require(budget.used == prior + 5 and result['reserved_completion_and_projection_units'] == 5, 'accepted gate did not charge exact five units')
            else:
                require(budget.used == prior and dict(calls) == before_calls, 'rejected reservation called compiler or spent work')
            passed += 1
    finally:
        subject.completion_module = original_loader
    return {'passed': passed, 'accepted_plans': calls['plans'], 'accepted_completions': calls['completions'],
            'heap_or_candidate_search_run': False}


def verify_elementary_controls():
    initial = ['xy', 'y']
    moves = [{'op': 'invert', 'target': 2}, {'op': 'multiply', 'target': 1, 'source': 2},
             {'op': 'invert', 'target': 2}, {'op': 'conjugate', 'target': 1, 'by': 'y'},
             {'op': 'conjugate', 'target': 1, 'by': 'Y'}]
    result = replay_elementary(initial, moves)
    require(result['endpoint'] == ['x', 'y'] and result['total_length'] == 2 and result['minimum_move_index'] == 2, 'elementary replay control failed')
    invalid = [[{'op': 'invert', 'target': True}], [{'op': 'multiply', 'target': 1, 'source': 1}],
               [{'op': 'conjugate', 'target': 1, 'by': 'xy'}]]
    for damaged in invalid:
        try:
            replay_elementary(initial, damaged)
        except ValueError:
            continue
        raise AssertionError('malformed elementary move accepted')
    return {'positive_prefix': True, 'malformed_moves_rejected': len(invalid)}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit_gate_report():
    path = HERE / 'two_complement_unit_gate_report.json'
    report = json.loads(path.read_text())
    require(sha(HERE / 'two_complement_unit_gate.py') == report['script_sha256'], 'unit-gate script changed')
    for name, expected in report['source_hashes'].items():
        require(sha(HERE / name) == expected, 'unit-gate dependency changed: ' + name)
    inventory_path = ROOT.parent / 'u124_inventory.json'
    require(sha(inventory_path) == report['source_inventory_sha256'], 'exact input inventory changed')
    inventory = json.loads(inventory_path.read_text())
    require(report['panel_ids'] == [r['name'] for r in inventory['panel']['rows']], 'exact20 panel order changed')
    require(len(report['rows']) == 20, 'wrong unit-gate row count')
    rows = []
    for index, (row, source) in enumerate(zip(report['rows'], inventory['panel']['rows'])):
        require(row['name'] == source['name'] and row['input'] == [source['r1'], source['r2']], 'exact original input join failed')
        rows.append({'name': row['name'], 'input': row['input'], 'input_length': row['input_length'],
                     'source_row_index': index, **verify_gate(row)})
    require(sum(r['charged_prefix_units'] for r in rows) == report['total_image_evaluations'] == 4224, 'gate aggregate cost differs')
    require(max(r['charged_prefix_units'] for r in rows) == report['maximum_image_evaluations'] == 733, 'gate maximum differs')
    return report, rows


def verify_prefix(gate_row, certificate, search_row=None):
    """Verify P -> stable marked Q -> strict ordinary prefix; no search is run.

    Callers pin the containing source reports and join P to the known-trivial
    census. The returned minimum counts both rank2 relators at every AC step.
    The implicit stable ambient bridge has no asserted intermediate length cap.
    """
    gate = verify_gate(gate_row)
    original_input = gate_row.get('original_input', gate_row['input'])
    original_length = gate_row.get('original_input_length', gate_row['input_length'])
    require(gate.get('stable_bridge_verified') is True, 'no admitted stable bridge')
    require(gate_row['name'] == certificate['name'], 'ordinary certificate name differs')
    require(certificate['input'] == gate['marked_projected_pair'], 'ordinary suffix does not start at raw marked Q')
    checked = replay_elementary(certificate['input'], certificate['moves'], certificate['boundaries'])
    require(checked['endpoint'] == certificate['endpoint'], 'ordinary certificate endpoint differs')
    require(checked['elementary_move_count'] == certificate['elementary_move_count'], 'elementary move count differs')
    require(checked['endpoint_total_length'] == certificate['total_length'], 'ordinary endpoint length differs')
    require(certificate['boundaries'] and certificate['boundaries'][-1]['move_count'] == len(certificate['moves']), 'final ordinary boundary is missing')
    if search_row is not None:
        require(search_row['name'] == gate_row['name'], 'search row name differs')
        require(search_row.get('original_input', search_row.get('input')) == original_input, 'original input differs between stages')
        require(search_row.get('original_input_length', search_row.get('input_length')) == original_length, 'original length differs between stages')
        require(search_row.get('projected_input', gate_row['projected']['pair']) == certificate['input'], 'search projected input differs')
        require(search_row.get('projected_input_length', gate_row['projected']['total_length']) == sum(map(len, certificate['input'])), 'search projected length differs')
        result = search_row['result']
        states = result['states'] if result['solved'] else result['best_states']
        steps = result['steps'] if result['solved'] else result['best_steps']
        require(len(states) == len(steps) + 1, 'captured search path sizes differ')
        require([b['pair'] for b in certificate['boundaries']] == states, 'elementary boundaries differ from captured search states')
        require(len(steps) == certificate['substitution_count'], 'substitution count differs')
        require(all(step['kind'] == 'substitution' for step in steps), 'ordinary suffix contains another move family')
        require(checked['endpoint'] == search_row['best_pair'] == result['best_state'], 'saved search endpoint differs')
        require(search_row['best_length'] == result['min_total_length_seen'] == checked['endpoint_total_length'], 'saved search minimum differs')
        require(search_row['elementary_move_count'] == checked['elementary_move_count'], 'row elementary count differs')
        require(result['basis_evaluations'] == 0, 'unaccounted ambient-image search')
        require(search_row.get('prefix_units', gate_row['image_evaluations']) == gate_row['image_evaluations'], 'search prefix charge differs')
        require(search_row.get('heap_pop_budget', gate_row['remaining_shared_budget']) == gate_row['remaining_shared_budget'], 'remaining heap budget differs')
        pops = search_row['heap_pops']
        require(type(pops) is int and 0 <= pops == result['nodes_explored'] <= gate_row['remaining_shared_budget'], 'heap budget exceeded')
        require(search_row['combined_units'] == pops + gate_row['image_evaluations'] <= 1000, 'combined shared budget exceeded')
        require(search_row['solved'] is result['solved'], 'solve metadata differs')
        require(search_row['improves_original'] == (checked['endpoint_total_length'] < original_length), 'original endpoint gain metadata differs')
        if result['solved']:
            require(sorted(checked['endpoint']) == ['x', 'y'], 'claimed solved endpoint is not literal basis')
        checked.update(heap_pops=pops, combined_units=search_row['combined_units'])
    checked.update(name=gate_row['name'], input=original_input, input_length=original_length,
                   prepared_input=gate_row['input'], input_bridge_verified=gate.get('input_bridge_verified', False),
                   complements=gate_row['complements'], projected_input=certificate['input'],
                   projected_input_length=sum(map(len, certificate['input'])),
                   charged_prefix_units=gate_row['image_evaluations'],
                   compiler_word_operations=gate['compiler_word_operations'],
                   projection_word_images=gate['projection_word_images'],
                   stable_bridge_verified=True, certificate_kind='theorem_backed_stable_bridge_then_ordinary_AC_prefix',
                   ordinary_equivalence_from_original_claimed=False,
                   stable_bridge_internal_length_bound=None,
                   minimum_including_original_length=min(original_length, checked['total_length']),
                   strict_original_gain=checked['total_length'] < original_length)
    return checked


def verify_source_hashes(report):
    outer = ROOT.parents[2]
    special = {'two_complement_q3_run.py': ROOT / 'two_complement_q3_run.py',
               'heuristic_1k.py': outer / 'experiments/search/heuristic_1k.py',
               'hexpand.py': outer / 'experiments/heuristic_search/core/hexpand.py'}
    for filename, expected in report['source_hashes'].items():
        require(sha(special.get(filename, HERE / filename)) == expected, 'source file changed: ' + filename)


def audit_suffix_report(filename, gate_rows, certificate_source=None):
    path = HERE / filename
    report = json.loads(path.read_text())
    verify_source_hashes(report)
    certificates_path = HERE / report['certificate_file']
    require(sha(certificates_path) == report['certificate_sha256'], 'ordinary certificate file hash differs')
    certificate_format = 'json' if certificates_path.suffix == '.json' else 'jsonl'
    certificates = ([json.loads(certificates_path.read_text())] if certificate_format == 'json'
                    else [json.loads(line) for line in certificates_path.read_text().splitlines()])
    require(len(certificates) == len(report['rows']), 'ordinary certificate row count differs')
    require(len({r['name'] for r in certificates}) == len(certificates), 'duplicate ordinary certificates')
    require([r['name'] for r in certificates] == [r['name'] for r in report['rows']], 'ordinary certificate row order differs')
    expected_names = [r['name'] for r in gate_rows if r['projected'] is not None]
    require([r['name'] for r in report['rows']] == expected_names, 'search rows omit or add marked projections')
    if certificate_source:
        source_hash = sha(HERE / certificate_source)
        require(report['projection_source_sha256'] == source_hash, 'search source projection hash differs')
    by_name = {row['name']: row for row in gate_rows}
    minima = []
    for index, (row, certificate) in enumerate(zip(report['rows'], certificates)):
        if certificate_source:
            require(certificate['projection_source_sha256'] == source_hash, 'certificate source projection hash differs')
            require(certificate['source_pointer'] == certificate_source + '#' + row['name'], 'certificate source pointer differs')
        checked = verify_prefix(by_name[row['name']], certificate, row)
        checked.update(source_report=filename, source_report_sha256=sha(path), source_row_index=index,
                       certificate_file=report['certificate_file'], certificate_file_sha256=sha(certificates_path),
                       certificate_format=certificate_format,
                       certificate_line_index=index,
                       gate_source_report=certificate_source or filename,
                       gate_source_report_sha256=sha(HERE / (certificate_source or filename)))
        minima.append(checked)
    require(report['solved_ids'] == [r['name'] for r in report['rows'] if r['solved']], 'aggregate solved IDs differ')
    require(report['strict_original_gain_ids'] == [r['name'] for r in report['rows'] if r['improves_original']], 'aggregate endpoint gain IDs differ')
    if 'total_heap_pops' in report:
        require(report['total_heap_pops'] == sum(r['heap_pops'] for r in minima), 'aggregate heap count differs')
        require(report['total_combined_units'] == sum(r['combined_units'] for r in minima), 'aggregate combined count differs')
    return report, minima


def main():
    started = time.process_time()
    gate_report, gate_checks = audit_gate_report()
    q2_report, q2 = audit_suffix_report('two_complement_unit_gate_s20_report.json', gate_report['rows'], 'two_complement_unit_gate_report.json')
    q3_path = HERE / 'two_complement_q3_report.json'
    q3_report = json.loads(q3_path.read_text())
    require([r['name'] for r in q3_report['rows']] == ['aca_115', 'aca_59'], 'q3 selection differs')
    originals = {r['name']: r for r in gate_report['rows']}
    for row, power in zip(q3_report['rows'], (3, 7)):
        require(row['input'] == originals[row['name']]['input'], 'q3 original input join failed')
        require(originals[row['name']]['join_is_full'] is False, 'q3 input was not a proper q2 join')
        require(row['input'][1] == 'YYYY' + 'x' * power, 'q3 Bezout selection premise differs')
        require(row['complements'] == ['x', 'yyy'], 'q3 complement differs')
    q3_report, q3 = audit_suffix_report(q3_path.name, q3_report['rows'])
    direct_path = HERE / 'euclidean_power_complement_report.json'
    direct_report = json.loads(direct_path.read_text())
    require(len(direct_report['rows']) == 1 and direct_report['rows'][0]['name'] == 'aca_59', 'Euclidean selection differs')
    require(direct_report['rows'][0]['original_input'] == originals['aca_59']['input'], 'Euclidean original census join failed')
    direct_report, direct = audit_suffix_report(direct_path.name, direct_report['rows'])
    controls = {'reservation': verify_reservation_controls(), 'elementary': verify_elementary_controls()}
    sources = {name: sha(HERE / name) for name in (
        'two_complement_unit_gate_report.json', 'two_complement_unit_gate_s20_report.json',
        'two_complement_unit_gate_s20_certificates.jsonl', 'two_complement_q3_report.json',
        'two_complement_q3_certificates.jsonl', 'two_complement_probe_checks.py',
        'euclidean_power_complement_report.json', 'euclidean_power_complement_certificate.json',
        'two_complement_independent_theory.md', 'two_complement_independent_theory.json')}
    inventory_path = ROOT.parent / 'u124_inventory.json'
    sources[str(inventory_path.relative_to(ROOT.parent))] = sha(inventory_path)
    input_path = ROOT / 'data/ms_unsolved_reps/aca_124_best.csv'
    sources['data/ms_unsolved_reps/aca_124_best.csv'] = sha(input_path)
    require(sources['data/ms_unsolved_reps/aca_124_best.csv'] == '8df25b3fc585553f80886934707b147c99252dcedf4b827a9a220fe99ebb58a3', 'saved best-input CSV changed')
    require(sources['two_complement_independent_theory.md'] == 'dd7a6970bed27f337718bd1ee84ae9a31f2c4899b118d6f27bfeaac1ac7dbf8e', 'independent bridge proof changed')
    require(sources['two_complement_independent_theory.json'] == 'e6b30624e1cc1084fd34c3fd850c687a59a20e9a370fee2634106fc426ca63b9', 'independent bridge theory audit changed')
    require(sources['two_complement_probe_checks.py'] == '9045b8523f55886b61d0f76b701149fa16e2f77a60aed4c0c1a52c39c38002a1', 'independent word checker changed')

    def aggregate(rows):
        return {'rows': len(rows), 'prefix_units': sum(r['charged_prefix_units'] for r in rows),
                'compiler_word_operations': sum(r['compiler_word_operations'] for r in rows),
                'projection_word_images': sum(r['projection_word_images'] for r in rows),
                'heap_pops': sum(r['heap_pops'] for r in rows),
                'combined_units': sum(r['combined_units'] for r in rows),
                'maximum_combined_units': max(r['combined_units'] for r in rows),
                'elementary_moves': sum(r['elementary_move_count'] for r in rows),
                'boundaries_verified': sum(r['boundaries_verified'] for r in rows),
                'all_elementary_states_checked': sum(len(r['replayed_total_lengths']) for r in rows),
                'strict_original_gain_ids': [r['name'] for r in rows if r['strict_original_gain']],
                'solved_ids': []}

    output = {'status': 'pass', 'auditor_source_sha256': sha(Path(__file__)), 'source_hashes': sources,
              'known_trivial_input_basis': 'Literal rows of the pinned Miller-Schupp saved-best U124 census; unimodularity alone is not used as a triviality proof.',
              'q2_exact20_gate': {'rows': len(gate_checks), 'full_join_marked_projections': 15,
                  'proper_join_rejects': [r['name'] for r in gate_checks if r['join_rejected']],
                  'checks': gate_checks},
              'q2_suffix_summary': aggregate(q2), 'q3_selected_summary': aggregate(q3),
              'euclidean_direct_summary': aggregate(direct),
              'minima': q2 + q3 + direct, 'controls': controls, 'audit_cpu_seconds': time.process_time() - started,
              'search_or_regeneration_run': False,
              'scope': 'q2 exact20 followed by15 suffixes, two separately budgeted q3 attempts, and one separately budgeted Euclidean direct attempt. Each completed attempt has1000 heterogeneous candidate-image/compiler/heap units. Integer proof replay is additional audit work. All complete rank2 ordinary states are counted, including temporary donor states. The Nielsen image tuple is not an admissible presentation. Stable bridge may use rank5; no finite internal word-length cap or ordinary equivalence from P is claimed.',
              'source_metadata_notes': ['q3 and Euclidean certificate rows omit a direct source pointer/hash; this audit joins each raw Q to the same-name marked basis in the hashed containing report and pins the entire certificate file. No mathematical witness is missing.',
                  'S20 search-time min_total_length_seen concerns captured search states; this audit independently checks every emitted elementary state. In all18 retained prefixes the two minima agree.',
                  'Negative outcomes mean no gain on the saved bounded prefix; no obstruction or optimality theorem is claimed.']}
    require(all(r['total_length'] == r['endpoint_total_length'] for r in output['minima']), 'microstate minimum differs from endpoint; update outcome metadata')
    (HERE / 'two_complement_unit_gate_independent_audit.json').write_text(json.dumps(output, indent=2) + '\n')
    write_markdown(output)
    print(json.dumps({k: output[k] for k in ('status', 'auditor_source_sha256', 'q2_suffix_summary', 'q3_selected_summary', 'euclidean_direct_summary', 'audit_cpu_seconds')}, indent=2))


def write_markdown(report):
    q2, q3, direct = report['q2_suffix_summary'], report['q3_selected_summary'], report['euclidean_direct_summary']
    lines = ['# Independent early-unit gate and stable suffix audit', '',
        'PASS. No search was rerun. All 18 marked bases, both inverse compositions, literal original/projection joins, and fully elementary suffixes pass independent integer replay. There are no solves and no strict original-input length gains.', '',
        '| Cohort | Marked rows | Prefix units | S20 pops | Combined | Elementary moves | Checkpoint boundaries |',
        '|---|---:|---:|---:|---:|---:|---:|',
        f"| Fixed x,y² panel | {q2['rows']} | {q2['prefix_units']} | {q2['heap_pops']} | {q2['combined_units']} | {q2['elementary_moves']} | {q2['boundaries_verified']} |",
        f"| Selected x,y³ follow-up | {q3['rows']} | {q3['prefix_units']} | {q3['heap_pops']} | {q3['combined_units']} | {q3['elementary_moves']} | {q3['boundaries_verified']} |",
        f"| Prepared-frame Euclidean x,y² | {direct['rows']} | {direct['prefix_units']} | {direct['heap_pops']} | {direct['combined_units']} | {direct['elementary_moves']} | {direct['boundaries_verified']} |", '',
        'Every completed attempt consumes exactly 1000 declared heterogeneous units. The q³ and Euclidean attempts are separately authorized attempts; this is not a claim of cumulative 1000 work across earlier experiments. Independent proof replay and source verification are additional work.', '',
        '## Cost and termination audit', '',
        'The gate preserves the frozen candidate order, normalizes only by relator inversions and permutations, and checks unit lifts at a popped state and each normalized generated child before deduplication. Each candidate reserves two units before its multiplication image and inverse-comparison image are formed; four initial inverse comparisons are also charged. No saved searched row hit a word-length guard. All 17 successful searched gates occur at generated children; the Euclidean gate uses its explicit direct construction.', '',
        'The compiler first makes its two selected lifts literal positive units. Every multiplication removes exactly one image letter, so there are L−2 multiplications, where L is the unit-gate input image length, plus at most two sign inversions. With the two kernel projections this gives an exact reservation before planning or completion. All 367 compiler updates and 36 projections replay with the declared costs. Four threshold controls confirm that a one-unit-short reservation neither invokes the compiler nor spends its reserved work. These controls do not run a candidate search.', '',
        'The Euclidean attempt first inverts original relator 2 and swaps ambient x,y, with both whole relator images checked. It charges these three preparation operations and four initial image words, then the seven recorded updates s←s t⁻⁴ u³ expose the literal image Y because the prepared second relator is y⁻⁷x⁴ and f(u)=y². The exact saved left-clearing compiler marking, rather than a different theoretically possible basis, is replayed. Its twelve compiler updates and two projections give prefix charge 28, leaving 972 S20 pops. No Nielsen candidate search occurs in this prefix.', '',
        '## Stable bridge and ordinary suffix', '',
        'The original P is taken from the pinned known-trivial Miller–Schupp census. The Euclidean row first uses its explicit inversion and axis swap to obtain a prepared P. For each declared complement (x,y²) or (x,y³), replay verifies an F₄ basis B=(W₁,W₂,Vₓ,Vᵧ), its two-sided inverse, and f(B)=(1,1,x,y). Killing original r,s in W₁,W₂ gives the literal raw Q. Killing the first two new coordinates in the inverse basis recovers the literal P used by that gate. These are precisely the hypotheses of the separately audited two-complement bridge.', '',
        'The balanced rank-four tuple (r,s,W₁,W₂) is known trivial by the quotient identification before the stable ambient-basis lemma is used. Unit elimination connects it to Q; the ambient basis change followed by kernel-unit elimination connects it to P. This certifies stable equivalence, potentially using a fifth helper generator. It does not certify ordinary equivalence from P or bound all internal stable word lengths. The generating image tuple (1,1,x,y) is not a balanced rank-two presentation and is never counted as a solve or length-two state.', '',
        'From raw Q, each suffix uses only relator inversion, right multiplication by the other current relator, or conjugation by one signed generator. The independent checker evaluates all intermediate words and both-relator length sums, including temporary donors, initial canonicalization and swaps. Every saved search boundary is checked at its exact elementary move index. All elementary minima equal the corresponding saved endpoint length; no hidden temporary state improves an original input.', '',
        '## Exact retained minima', '',
        '| Input | Complement exponent | Original length | Raw Q length | Minimum ordinary suffix length | First minimum move |',
        '|---|---:|---:|---:|---:|---:|']
    for r in report['minima']:
        lines.append(f"| {r['name']} | {len(r['complements'][1])} | {r['input_length']} | {r['projected_input_length']} | {r['total_length']} | {r['minimum_move_index']} |")
    lines += ['', '## Admission API and provenance', '',
        '`verify_prefix(gate_row, certificate, search_row=None)` returns the independently replayed minimum with `relators`, `rank`, `total_length`, `minimum_move_index`, endpoint, complete intermediate total-length ledger, `independently_verified`, and `stable_bridge_verified`. Supplying the search row additionally checks all captured boundaries, endpoint metadata and shared-budget arithmetic. Callers must pin the containing reports and join the original P to the known-trivial census. The JSON ledger supplies report/certificate hashes, row/line indices and the exact original input for that join.', '',
        'The q³ and Euclidean certificates do not carry a source pointer individually. The audit supplies that missing provenance link by verifying raw Q against the same-name marked witness and hashing both whole artifacts. This is a metadata qualification, not a missing algebraic certificate. The Euclidean certificate is a single JSON object; all other certificates are JSONL. Each minimum declares its certificate format. The same verify_prefix API accepts all three cohorts and checks the explicit prepared-input bridge when present.', '',
        'The integer bridge checker dependency is the frozen independent `two_complement_probe_checks.py`; the ordinary word stack is implemented directly in this audit. The current gate code is imported only for four reservation controls, with no heap or search execution. Negative claims remain bounded saved-prefix outcomes.', '',
        f"Auditor SHA-256: `{report['auditor_source_sha256']}`.",
        f"Audit CPU: {report['audit_cpu_seconds']:.6f} seconds. Source hashes and the full intermediate length ledger are in the companion JSON.", '']
    (HERE / 'two_complement_unit_gate_independent_audit.md').write_text('\n'.join(lines))


if __name__ == '__main__':
    main()
