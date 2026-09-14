"""Read-only independent audit of saved primitive macros and MS scope witnesses.

No subject compiler, template generation, Whitehead search, or orbit search is
imported or run. verify_attempt/verify_prefix are reusable adapter entry points.
"""
from __future__ import annotations

import ast
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ENCODE = {'x': 1, 'X': -1, 'y': 2, 'Y': -2, 'z': 3, 'Z': -3}
DECODE = {value: key for key, value in ENCODE.items()}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def reduce_int(word):
    output = []
    for letter in word:
        if output and output[-1] == -letter:
            output.pop()
        else:
            output.append(letter)
    return output


def encode(word):
    need(isinstance(word, str) and all(c in ENCODE for c in word), 'invalid word alphabet')
    return [ENCODE[c] for c in word]


def decode(word):
    return ''.join(DECODE[c] for c in word)


def red(word):
    return decode(reduce_int(encode(word)))


def inv(word):
    return decode([-c for c in reversed(encode(word))])


def apply(word, images):
    mapped = {ENCODE[g]: encode(w) for g, w in images.items()}
    need(all(g in ('x', 'y', 'z') for g in images), 'map keys must be positive basis letters')
    output = []
    for c in encode(word):
        need(abs(c) in mapped, 'unmapped generator in word')
        part = mapped[abs(c)]
        output.extend(part if c > 0 else [-v for v in reversed(part)])
    return decode(reduce_int(output))


def canon(word):
    letters = reduce_int(encode(word))
    while len(letters) > 1 and letters[0] == -letters[-1]:
        letters = letters[1:-1]
    word = decode(letters)
    return min((w[i:] + w[:i] for w in (word, inv(word)) for i in range(len(w))), default='')


def pair_key(pair):
    return tuple(sorted(canon(w) for w in pair))


def check_inverse(images, backwards):
    need(set(images) == set(backwards), 'inverse basis keys differ')
    for g in images:
        need(apply(images[g], backwards) == g and apply(backwards[g], images) == g,
             'recorded map inverse composition failed')


def check_normalization(before, after, witnesses):
    need(len(before) == len(after) == len(witnesses), 'canonical tuple cardinality mismatch')
    for word, target, witness in zip(before, after, witnesses):
        sign, conjugator = witness['sign'], witness['conjugator']
        need(type(sign) is int and sign in (-1, 1), 'canonical sign invalid')
        signed = word if sign == 1 else inv(word)
        need(red(inv(conjugator) + signed + conjugator) == target, 'canonical conjugation witness invalid')
        need(target == canon(word), 'recorded canonical word is not the independent canonical word')


def verify_attempt(record):
    """Verify every stored macro boundary and optional rank2 quotient witness."""
    pair, candidate = record['input'], record['candidate']
    need(len(pair) == 2 and all(set(w) <= set('xXyY') and red(w) == w for w in pair), 'invalid input pair')
    source, sign = candidate['source'], candidate['source_sign']
    need(type(source) is int and source in (0, 1), 'source role invalid')
    need(type(sign) is int and sign in (-1, 1), 'source sign invalid')
    c = candidate['source_conjugator']
    oriented = red(inv(c) + (pair[source] if sign == 1 else inv(pair[source])) + c)
    need(oriented == candidate['oriented_source'], 'source orientation does not replay')
    defining = candidate['defining_word']
    need(2 <= len(defining) <= 6 and set(defining) <= set('xXyY'), 'defining word violates recorded limits')
    isolator, companion = candidate['isolator'], candidate['companion_template']
    sub = {'x': 'x', 'y': 'y', 'z': defining}
    need(apply(isolator, sub) == oriented, 'isolator template expansion is false')
    need(apply(companion, sub) == pair[1 - source], 'companion template expansion is false')
    counts = Counter(canon(isolator).lower())
    need('z' in counts and all(n >= 2 for n in counts.values()), 'literal single-occurrence candidate not excluded')
    donor = red('Z' + defining)
    initial = [donor, isolator, companion]
    need(record['initial_rank3'] == initial, 'initial rank3 tuple differs from exact compression')
    norm = record['initial_normalization']
    need(norm['before'] == initial, 'initial normalization chain invalid')
    check_normalization(initial, norm['after'], norm['canonical_witnesses'])
    current = norm['after']
    expected = [pair, [donor, oriented, pair[1 - source]], initial, current]
    whole_tuple_steps = 0
    for step in record['whitehead_steps']:
        need(step['before'] == current, 'rank3 map chain is discontinuous')
        need(set(step['images']) == set('xyz'), 'rank3 map does not name all generators')
        check_inverse(step['images'], step['inverse_images'])
        raw = [apply(w, step['images']) for w in current]
        need(raw == step['raw_image'], 'rank3 map not applied to the whole tuple')
        check_normalization(raw, step['after'], step['canonical_witnesses'])
        need(len(step['after'][1]) < len(current[1]), 'selected isolator map does not strictly shorten')
        current = step['after']
        expected.extend((raw, current))
        whole_tuple_steps += 1
    need(current == record['rank3_endpoint'], 'rank3 endpoint chain invalid')
    positive = 'endpoint' in record
    rank2_steps = 0
    if positive:
        need(record['status'] == 'primitive_with_replayed_rank2_macro_endpoint', 'positive endpoint status mismatch')
        need(len(current[1]) == 1, 'deletion attempted without a literal generator relator')
        axis = current[1].lower()
        deletion = record['deletion']
        need(deletion['axis'] == axis and deletion['before'] == current, 'deletion source mismatch')
        need(deletion['isolator_sign'] == (1 if current[1] == axis else -1), 'singleton sign normalization wrong')
        erase = {g: '' if g == axis else g for g in 'xyz'}
        remaining = [apply(current[i], erase) for i in (0, 2)]
        deleted = [remaining[0], axis, remaining[1]]
        need(deletion['surviving_words'] == remaining and deletion['after_substitution'] == deleted,
             'generator deletion failed on one of the remaining relators')
        need(all(axis not in w.lower() for w in remaining), 'deleted generator survives in another relator')
        axes = [g for g in 'xyz' if g != axis]
        relabel = dict(zip(axes, 'xy'))
        need(record['relabel'] == relabel, 'surviving basis was mislabeled')
        rank2 = [apply(w, relabel) for w in remaining]
        need(rank2 == record['raw_rank2_endpoint'], 'rank2 quotient word mismatch')
        expected.extend((deleted, rank2))
        descent = record['rank2_nielsen']
        norm2 = descent['initial_normalization']
        need(norm2['before'] == rank2, 'rank2 initial normalization chain invalid')
        check_normalization(rank2, norm2['after'], norm2['canonical_witnesses'])
        current2 = norm2['after']
        for step in descent['steps']:
            need(step['before'] == current2, 'rank2 Nielsen chain invalid')
            need(set(step['images']) == set('xy'), 'rank2 map basis invalid')
            check_inverse(step['images'], step['inverse_images'])
            raw = [apply(w, step['images']) for w in current2]
            need(raw == step['raw_image'], 'rank2 map not applied to both words')
            check_normalization(raw, step['after'], step['canonical_witnesses'])
            need(sum(map(len, step['after'])) < sum(map(len, current2)), 'rank2 descent is not strict')
            current2 = step['after']
            rank2_steps += 1
        need(current2 == descent['endpoint'] == record['endpoint'], 'rank2 endpoint chain invalid')
        length = sum(map(len, current2))
        need(length == record['endpoint_length'], 'rank2 endpoint total miscounted')
        need(record['strict_length_gain'] == (length < sum(map(len, pair))), 'rank2-only gain flag wrong')
    boundaries = record['boundaries']
    need([b['relators'] for b in boundaries] == expected, 'recorded boundary tuple omitted/reordered a state')
    verified_boundaries = []
    for index, b in enumerate(boundaries):
        words = b['relators']
        need(all(red(w) == w for w in words), 'boundary word not freely reduced')
        need(b['rank'] == len(words), 'boundary rank does not count all relators')
        need(b['relator_lengths'] == list(map(len, words)), 'boundary relator lengths false')
        need(b['total_length'] == sum(map(len, words)), 'boundary total omits a relator')
        verified_boundaries.append({**b, 'boundary_index': index, 'independently_verified': True})
    rank3 = [b for b in verified_boundaries if b['rank'] == 3]
    need(record['recorded_rank3_boundary_max_total_length'] == max(b['total_length'] for b in rank3),
         'recorded rank3 boundary maximum false')
    charges = record['image_evaluation_counts']
    rounds = whole_tuple_steps + (record['status'] == 'nonprimitive_whitehead_minimum')
    need(charges.get('rank3_candidate_images', 0) == 90 * rounds, 'rank3 round charge mismatch')
    need(charges.get('selected_whole_rank3_images', 0) == 3 * whole_tuple_steps, 'whole-tuple image charge mismatch')
    if positive:
        rounds2 = rank2_steps + (record['rank2_nielsen']['stop'] == 'no_strict_nielsen_descent')
        need(charges.get('rank2_candidate_images', 0) == 16 * rounds2, 'rank2 candidate image charge mismatch')
    need(sum(charges.values()) == record['image_evaluations'] <= 1000, 'attempt image budget mismatch')
    return {'verified': True, 'boundaries': verified_boundaries, 'positive_quotient': positive,
            'whole_rank3_map_steps': whole_tuple_steps, 'rank2_nielsen_steps': rank2_steps,
            'image_evaluations': record['image_evaluations']}


def verify_prefix(record, boundary_index):
    """Return a verified complete tuple at the requested saved macro boundary."""
    need(type(boundary_index) is int and 0 <= boundary_index < len(record['boundaries']), 'invalid boundary index')
    return verify_attempt(record)['boundaries'][boundary_index]


def primitive_audit(report, original_inventory):
    selected = [r for r in original_inventory['panel']['rows'] if r['name'] != 'aca_115']
    need(len(selected) == 19 and report['selected_ids'] == [r['name'] for r in selected],
         'fixed panel is not exactly original20 minus aca115')
    by_name = {r['name']: r for r in selected}
    need([r['name'] for r in report['rows']] == report['selected_ids'], 'panel rows incomplete or reordered')
    counters = Counter()
    audited = []
    for row_index, row in enumerate(report['rows']):
        source = by_name[row['name']]
        need(row['input'] == [source['r1'], source['r2']], 'input differs from exact original fixed panel')
        need(row['input_length'] == sum(map(len, row['input'])), 'input total incorrect')
        need(sum(a['image_evaluations'] for a in row['attempts']) == row['image_evaluations'], 'row budget not shared among attempts')
        combined = Counter()
        rank3 = []
        endpoints = []
        for attempt_index, attempt in enumerate(row['attempts']):
            need(attempt['input'] == row['input'], 'attempt attached to wrong source input')
            checked = verify_attempt(attempt)
            counters['attempts_independently_replayed'] += 1
            counters['positive_quotient_witnesses'] += checked['positive_quotient']
            counters['whole_rank3_map_steps'] += checked['whole_rank3_map_steps']
            counters['rank2_nielsen_steps'] += checked['rank2_nielsen_steps']
            combined.update(attempt['image_evaluation_counts'])
            for b in checked['boundaries']:
                counters['all_rank_boundaries_verified'] += 1
                if b['rank'] == 3:
                    rank3.append({**b, 'attempt_index': attempt_index,
                                  'json_pointer': f'/rows/{row_index}/attempts/{attempt_index}/boundaries/{b["boundary_index"]}',
                                  'attempt_status': attempt['status']})
            if checked['positive_quotient']:
                endpoints.append((attempt['endpoint_length'], attempt['endpoint'], attempt_index))
        need(dict(combined) == row['image_evaluation_counts'], 'per-kind image charges not shared across row')
        need(sum(combined.values()) == row['image_evaluations'] <= row['image_limit'] <= 1000, 'row image cap exceeded')
        need(len(endpoints) == row['primitive_candidates'], 'primitive endpoint occurrences miscounted')
        best_rank2 = min(endpoints) if endpoints else None
        need(row['best_endpoint'] == (best_rank2[1] if best_rank2 else None), 'best endpoint selection false')
        need(row['best_endpoint_length'] == (best_rank2[0] if best_rank2 else None), 'best endpoint length false')
        need(row['strict_length_gain'] == bool(best_rank2 and best_rank2[0] < row['input_length']), 'endpoint-only row gain false')
        best_rank3 = min(rank3, key=lambda b: (b['total_length'], b['attempt_index'], b['boundary_index'])) if rank3 else None
        min3 = best_rank3['total_length'] if best_rank3 else None
        all_minimum = min([row['input_length']] + ([min3] if min3 is not None else []) + ([best_rank2[0]] if best_rank2 else []))
        audited.append({'name': row['name'], 'input': row['input'], 'input_length': row['input_length'],
                        'attempts_verified': len(row['attempts']), 'image_evaluations': row['image_evaluations'],
                        'minimum_rank3_total_length': min3, 'minimum_rank3_witness': best_rank3,
                        'rank2_endpoint_minimum_length': best_rank2[0] if best_rank2 else None,
                        'rank2_endpoint_minimum_pair': best_rank2[1] if best_rank2 else None,
                        'rank3_strict_gain': min3 is not None and min3 < row['input_length'],
                        'rank2_endpoint_strict_gain': bool(best_rank2 and best_rank2[0] < row['input_length']),
                        'all_rank_minimum_total_length': all_minimum,
                        'all_rank_strict_gain': all_minimum < row['input_length']})
    counters['rows_verified'] = len(audited)
    counters['rank3_gain_rows'] = sum(r['rank3_strict_gain'] for r in audited)
    counters['rank2_endpoint_gain_rows'] = sum(r['rank2_endpoint_strict_gain'] for r in audited)
    counters['shared_word_image_evaluations'] = sum(r['image_evaluations'] for r in audited)
    return audited, dict(counters)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_ms_match(pair, match):
    base, stable = match['base'], match['stable']
    need(base in 'xXyY' and stable in 'xXyY' and base.lower() != stable.lower(), 'MS axes invalid')
    mapping = {base: 'y', inv(base): 'Y', stable: 'x', inv(stable): 'X'}
    donor = match['donor_index']
    need(type(donor) is int and donor in (0, 1), 'MS donor role invalid')
    n, k, r, s = (match[a] for a in ('n', 'k', 'r', 's'))
    need(all(type(v) is int for v in (n, k, r, s)) and n >= 1, 'MS parameters invalid')
    power = lambda exponent: 'y' * exponent if exponent >= 0 else 'Y' * -exponent
    expected_donor = 'X' + power(n) + 'x' + power(-n - 1)
    expected_companion = red('X' + power(-k) + 'X' + power(r) + 'x' + power(s))
    need(canon(''.join(mapping[c] for c in pair[donor])) == canon(expected_donor), 'MS donor parameter orientation failed')
    need(canon(''.join(mapping[c] for c in pair[1 - donor])) == canon(expected_companion), 'MS companion parameter orientation failed')
    terminal = r % n == 0 or s % (n + 1) == 0 or any((r - e) % n == 0 and (s + e) % (n + 1) == 0 for e in (-1, 1))
    need(match['terminal'] == terminal, 'MS terminal predicate differs')
    return terminal


def audit_scope():
    paths = {name: HERE / (name + '.json') for name in ('ms_census_scope', 'ms_residue_class_probe', 'ms_residue_orbits')}
    records = {name: json.loads(path.read_text()) for name, path in paths.items()}
    for name, report in records.items():
        need(sha(HERE / (name + '.py')) == report['script_sha256'], 'scope author script hash changed')
    census_path, solved_path = ROOT / 'data/1190MS.txt', ROOT / 'data/ms640_solved.txt'
    census_report = records['ms_census_scope']
    need(sha(census_path) == census_report['input_sha256'] and sha(solved_path) == census_report['solved_input_sha256'], 'census inputs changed')

    def load48(path):
        rows = {}
        for i, line in enumerate(path.read_text().splitlines(), 1):
            if not line.strip():
                continue
            values = ast.literal_eval(line)
            need(len(values) == 48 and all(type(v) is int and v in (0, 1, -1, 2, -2) for v in values), 'bad census encoding')
            rows[i] = [decode(v for v in values[:24] if v), decode(v for v in values[24:] if v)]
        return rows

    census, solved = load48(census_path), load48(solved_path)
    need(len(census) == 1190 and len(solved) == 640, 'census cardinality differs')
    solved_keys = {pair_key(pair) for pair in solved.values()}
    counts = Counter()
    seen_lines = set()
    match_count = 0
    for row in census_report['rows']:
        line = row['census_line_1based']
        need(line not in seen_lines and census[line] == row['pair'], 'census exact source join failed')
        seen_lines.add(line)
        was_solved = pair_key(row['pair']) in solved_keys
        need(row['already_in_solved640'] == was_solved, 'solved640 join failed')
        matched_terminal = [check_ms_match(row['pair'], match) for match in row['matches']]
        need(bool(matched_terminal), 'empty saved recognition')
        terminal = any(matched_terminal)
        match_count += len(matched_terminal)
        need(terminal == row['terminal_by_proved_residue_criterion'], 'terminal aggregate differs')
        counts['matched_rows'] += 1
        counts['terminal_rows'] += terminal
        counts['terminal_already_in_solved640'] += terminal and was_solved
        counts['terminal_outside_solved640'] += terminal and not was_solved
    need(dict(counts) == census_report['counts'], 'census counts differ')

    probe = records['ms_residue_class_probe']
    grid_path = ROOT / 'data/ms_unsolved_reps/ms_solved_grid.csv'
    best_path = ROOT / 'data/ms_unsolved_reps/aca_124_best.csv'
    need(sha(grid_path) == probe['grid_sha256'] and sha(best_path) == probe['best_input_sha256'], 'scope grid or best CSV changed')
    best = list(csv.DictReader(best_path.open()))
    members = {member: row for row in best for member in row['members'].split()}
    grid = {(int(n), row['w']): row[n] for row in csv.DictReader(grid_path.open()) if row['w'] for n in map(str, range(1, 8))}
    power = lambda e: 'y' * e if e >= 0 else 'Y' * -e
    targets = {}
    target_classes = defaultdict(set)
    for row in probe['rows']:
        n, w = row['ms_cell']['n'], row['ms_cell']['w']
        member = grid[n, w]
        need(member != 'trivial' and member == row['member_name'], 'original cell label join failed')
        parent = members[member]
        need(parent['name'] == row['aca_id'], 'U124 class label join failed')
        raw = ['X' + power(n) + 'x' + power(-n - 1), 'X' + w]
        need(raw == row['original_ms_pair'], 'original MS words differ')
        match = row['winner']['match']
        check_ms_match(raw, match)
        m, r, s = match['n'], match['r'], match['s']
        rr, ss = row['winner']['residues']
        for value, remainder, modulus in ((r, rr, m), (s, ss, m + 1)):
            need((value - remainder) % modulus == 0 and abs(remainder) <= modulus / 2, 'unbalanced or incongruent residue')
        target = ['X' + power(m) + 'x' + power(-m - 1), red('XX' + power(rr) + 'x' + power(ss))]
        normalization = row['winner']['normalization']
        need(normalization['residue_pair'] == target and normalization['trace'] == [], 'unexpected saved normalization trace')
        need(normalization['endpoint'] == list(pair_key(target)), 'empty-trace normalization endpoint differs')
        need(normalization['complete'] is True and normalization['image_evaluations'] == 8, 'normalization metadata differs')
        endpoint_length = sum(map(len, normalization['endpoint']))
        need(normalization['endpoint_length'] == endpoint_length, 'normalization length differs')
        starting = len(parent['r1']) + len(parent['r2'])
        need(row['u124_starting_length'] == starting and row['potential_gain'] == starting - endpoint_length, 'scope length comparison differs')
        key = (m, rr, ss)
        need(key not in targets or targets[key] == normalization, 'repeated residue target changed')
        targets[key] = normalization
        target_classes[tuple(normalization['endpoint'])].add(row['aca_id'])
    need(len(probe['rows']) == probe['matched_unsolved_cells'] == 338, 'residue cell count differs')
    need(len({r['aca_id'] for r in probe['rows']}) == probe['distinct_u124_components'] == 31, 'residue component count differs')
    need(len(targets) == probe['unique_residue_targets'] == 64, 'residue target count differs')
    need(sum(v['image_evaluations'] for v in targets.values()) == probe['image_evaluations'] == 512, 'map-pair evaluation accounting differs')
    need(sorted({r['aca_id'] for r in probe['rows'] if r['potential_gain'] > 0}) == probe['potential_gain_ids'] == [], 'potential gains differ')

    orbit = records['ms_residue_orbits']
    need(sha(paths['ms_residue_class_probe']) == orbit['source_sha256'], 'orbit source changed')
    groups, seen_targets = defaultdict(set), set()
    for row in orbit['rows']:
        target = tuple(row['input'])
        need(target in target_classes and target not in seen_targets, 'orbit target join failed')
        seen_targets.add(target)
        need(row['classes'] == sorted(target_classes[target]) and row['status'] == 'complete', 'orbit class or status differs')
        mapping = row['images']
        need(set(mapping) == {'x', 'y'} and all(len(v) == 1 and v in 'xXyY' for v in mapping.values()) and {v.lower() for v in mapping.values()} == {'x', 'y'}, 'saved orbit map is not an invertible signed permutation')
        need(pair_key([apply(word, mapping) for word in target]) == pair_key(row['representative']), 'orbit image witness failed')
        need(row['length'] == sum(map(len, row['representative'])), 'orbit representative length differs')
        groups[tuple(row['representative'])].update(row['classes'])
    need(seen_targets == set(target_classes) and len(seen_targets) == orbit['targets'] == 64, 'orbit targets incomplete')
    need(len(groups) == orbit['complete_orbits'] == 32 and orbit['capped_targets'] == 0, 'saved orbit grouping counts differ')
    need(not [c for c in groups.values() if len(c) > 1] and orbit['potential_class_merges'] == [], 'potential cross-class merge differs')
    return {'status': 'saved_witnesses_and_joins_pass', 'source_report_sha256': {name: sha(path) for name, path in paths.items()},
            'census_counts': dict(counts), 'ms_signed_parameter_matches_verified': match_count,
            'original_unsolved_cells_verified': 338, 'class_label_components': 31,
            'residue_targets_verified': 64, 'saved_orbit_signed_permutation_maps_verified': 64,
            'distinct_saved_orbit_representatives': 32, 'new_gains_or_merges': 0,
            'limits': 'Read-only replay of saved recognitions, normalizations and orbit witnesses. No recognizer, Nielsen descent or full orbit search rerun; absent matches and global orbit completeness are not independently reproved. Old grid/member labels certify only data joins, not AC bridges.',
            'charge_units': 'The residue probe counts 512 map-pair evaluations, equivalent to 1024 individual word images; these differ from the primitive screen individual-word-image budget.'}


def main():
    start_wall, start_cpu = time.perf_counter(), time.process_time()
    report_path = HERE / 'primitive_compression_report.json'
    report = json.loads(report_path.read_text())
    original_path = ROOT.parent / 'u124_inventory.json'
    original = json.loads(original_path.read_text())
    source_hash_checks = []
    for name, expected in report['source_sha256'].items():
        path = Path(name)
        actual = sha(path)
        need(actual == expected, f'source changed since saved primitive screen: {path}')
        source_hash_checks.append({'path': name, 'sha256': actual, 'verified': True})
    rows, counts = primitive_audit(report, original)
    audit = {'status': 'pass', 'source_report_sha256': sha(report_path),
             'source_report': str(report_path), 'audit_script_sha256': sha(Path(__file__)),
             'original_panel_inventory_sha256': sha(original_path),
             'source_hash_checks': source_hash_checks, 'counts': counts, 'rows': rows,
             'rank3_gain_ids': [r['name'] for r in rows if r['rank3_strict_gain']],
             'rank2_endpoint_gain_ids': [r['name'] for r in rows if r['rank2_endpoint_strict_gain']],
             'certificate_kind': 'independently_replayed_theorem_backed_stable_macro_boundaries_not_expanded_ordinary_streams',
             'important_correction': 'Zero rank2 endpoint gains does not mean zero admissible rank3 boundary gains:12/19 exact panel rows have shorter complete rank3 tuples.',
             'scope_audit': audit_scope(),
             'wall_seconds': time.perf_counter() - start_wall,
             'cpu_seconds': time.process_time() - start_cpu}
    (HERE / 'primitive_compression_independent_audit.json').write_text(json.dumps(audit, indent=2) + '\n')
    print(json.dumps({'status': audit['status'], 'counts': counts, 'rank3_gain_ids': audit['rank3_gain_ids'],
                      'rank2_endpoint_gain_ids': audit['rank2_endpoint_gain_ids'], 'wall_seconds': audit['wall_seconds']}))


if __name__ == '__main__':
    main()
