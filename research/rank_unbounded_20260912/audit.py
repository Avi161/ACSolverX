"""Independent saved-witness audit; no census search or elementary-solve claim."""
from __future__ import annotations

import ast
from collections import Counter
import csv
from fractions import Fraction
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import sys
import time


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def word(value):
    require(all(type(x) is int and x != 0 for x in value), 'invalid signed integer')
    return tuple(value)


def words(value):
    return tuple(word(w) for w in value)


def invert(value):
    return tuple(-value[i] for i in range(len(value) - 1, -1, -1))


def free(value):
    result = list(word(value))
    while True:
        for i in range(len(result) - 1):
            if result[i] + result[i + 1] == 0:
                del result[i:i + 2]
                break
        else:
            return tuple(result)


def cyclic(value):
    result = free(value)
    start, end = 0, len(result)
    while end - start > 1 and result[start] + result[end - 1] == 0:
        start += 1
        end -= 1
    return result[start:end]


def representative(value):
    result = cyclic(value)
    if not result:
        return ()
    orbit = []
    for sign in (1, -1):
        oriented = result if sign == 1 else invert(result)
        for offset in range(len(oriented)):
            orbit.append(tuple(oriented[(i + offset) % len(oriented)] for i in range(len(oriented))))
    return min(orbit)


def normalized(value):
    return tuple(sorted(representative(w) for w in value))


def size(value):
    return sum(len(w) for w in value)


def image(value, mapping, reduce=True):
    output = []
    for letter in value:
        replacement = mapping[abs(letter)]
        output.extend(replacement if letter > 0 else invert(replacement))
    return free(output) if reduce else tuple(output)


def parse(value, stored_mapping):
    alphabet = sorted({c.lower() for w in value for c in w}, key='xyzuvw'.index)
    expected = {letter: i + 1 for i, letter in enumerate(alphabet)}
    require(expected == stored_mapping, 'source generator map differs')
    result = tuple(tuple(expected[c.lower()] * (1 if c == c.lower() else -1) for c in w) for w in value)
    return words(result)


def determinant(value):
    rank = len(value)
    basis = sorted({abs(x) for w in value for x in w})
    require(len(basis) == rank, 'unbalanced ambient basis')
    matrix = [[Fraction(sum((x > 0) - (x < 0) for x in w if abs(x) == j))
               for j in basis] for w in value]
    answer = Fraction(1)
    for col in range(rank):
        pivot = next((i for i in range(col, rank) if matrix[i][col]), None)
        if pivot is None:
            return 0
        if pivot != col:
            matrix[col], matrix[pivot] = matrix[pivot], matrix[col]
            answer *= -1
        factor = matrix[col][col]
        answer *= factor
        for j in range(col, rank):
            matrix[col][j] /= factor
        for i in range(col + 1, rank):
            factor = matrix[i][col]
            for j in range(col, rank):
                matrix[i][j] -= factor * matrix[col][j]
    return int(answer)


def check_tuple(value):
    require(abs(determinant(value)) == 1, 'nonunimodular boundary')
    require(all(free(w) == w for w in value), 'unreduced boundary')


def defining_event(event):
    before = words(event['before'])
    defining = word(event['defining'])
    helper = event['helper']
    require(helper == max(abs(x) for w in before for x in w) + 1, 'helper not fresh')
    require(defining and free(defining) == defining, 'invalid definition')
    require(all(abs(x) < helper for x in defining), 'definition uses fresh generator')
    templates = words(event['templates'])
    cuts = event['cuts']
    require(len(templates) == len(cuts) == len(before), 'old relator omitted')
    mapping = {g: (g,) for g in range(1, helper)}
    mapping[helper] = defining
    selected = 0
    for old, template, cut in zip(before, templates, cuts):
        require(type(cut) is int and 0 <= cut < max(1, len(old)), 'invalid cut')
        rotated = old[cut:] + old[:cut]
        require(image(template, mapping, reduce=False) == rotated, 'template expansion not literal rotation')
        require(free(template) == template, 'template freely cancels')
        selected += sum(abs(x) == helper for x in template)
    raw = words(event['raw_after'])
    require(raw == ((-helper,) + defining,) + templates, 'new or old defining relator omitted')
    require(len(raw) == len(before) + 1, 'rank increment wrong')
    expected_length = size(before) + len(defining) + 1 - selected * (len(defining) - 1)
    require(selected == event['uses'], 'occurrence count wrong')
    require(size(raw) == expected_length == event['literal_length'], 'literal length accounting wrong')
    after = words(event['after'])
    require(normalized(raw) == after, 'definition normalization wrong')
    require(size(after) == event['final_length'], 'final definition length wrong')
    check_tuple(before)
    check_tuple(after)
    return after


def whitehead_images(basis, multiplier, side):
    output = {}
    if isinstance(basis, int):
        basis = range(1, basis + 1)
    for generator in basis:
        if abs(multiplier) == generator:
            output[generator] = (generator,)
        elif generator in side and -generator in side:
            output[generator] = (-multiplier, generator, multiplier)
        elif generator in side:
            output[generator] = (generator, multiplier)
        elif -generator in side:
            output[generator] = (-multiplier, generator)
        else:
            output[generator] = (generator,)
    return output


def adjacency(value):
    edges = Counter()
    for w in value:
        require(cyclic(w) == w, 'graph input not cyclically reduced')
        for i in range(len(w)):
            edge = tuple(sorted((w[i], -w[(i + 1) % len(w)])))
            require(edge[0] != edge[1], 'graph loop')
            edges[edge] += 1
    return edges


def capacity(edges, side):
    return sum(weight for (a, b), weight in edges.items() if (a in side) != (b in side))


def whitehead_event(event):
    before = words(event['before'])
    rank = len(before)
    basis = {abs(x) for w in before for x in w}
    a, side = event['multiplier'], set(event['side'])
    require(a in side and -a not in side, 'invalid Whitehead side')
    require(side <= basis | {-g for g in basis}, 'Whitehead side outside basis')
    forward = {int(k): word(v) for k, v in event['images'].items()}
    backward = {int(k): word(v) for k, v in event['inverse_images'].items()}
    require(set(forward) == set(backward) == basis, 'incomplete basis map')
    require(forward == whitehead_images(basis, a, side), 'forward map not claimed Whitehead map')
    require(backward == whitehead_images(basis, -a, side - {a} | {-a}), 'inverse map not claimed inverse')
    for x in basis:
        require(image(forward[x], backward) == (x,), 'left inverse fails')
        require(image(backward[x], forward) == (x,), 'right inverse fails')
        require(image(invert(forward[x]), backward) == (-x,), 'negative-generator inverse fails')
    raw = words(event['raw_after'])
    require(raw == tuple(image(w, forward) for w in before), 'Whitehead omitted or altered a relator')
    after = words(event['after'])
    require(len(after) == rank and normalized(raw) == after, 'Whitehead normalization wrong')
    edges = adjacency(before)
    expected_delta = capacity(edges, side) - sum(n for edge, n in edges.items() if a in edge)
    require(size(after) - size(before) == expected_delta, 'cut formula does not match replay')
    if 'length_change' in event:
        require(event['length_change'] == expected_delta, 'stored Whitehead length change wrong')
    if 'normalization' in event:
        normalization(raw, event['normalization'], after)
    if 'target_index_before' in event:
        i, j = event['target_index_before'], event['target_index_after']
        require(event['normalization'][j]['input_index'] == i, 'primitive target tracking differs')
        require(event['target_length_change'] == len(after[j]) - len(before[i]) < 0, 'primitive target length differs')
    if 'selected_length_change' in event:
        selected_before, selected_after = event['selected_indices_before'], event['selected_indices_after']
        require(sorted(event['normalization'][j]['input_index'] for j in selected_after) == sorted(selected_before), 'selected subtuple tracking differs')
        selected_delta = sum(len(after[j]) for j in selected_after) - sum(len(before[i]) for i in selected_before)
        require(selected_delta == event['selected_length_change'] < 0, 'selected subtuple length change differs')
    check_tuple(before)
    check_tuple(after)
    return after


def conjugation(before, sign, conjugator):
    require(type(sign) is int and sign in (-1, 1), 'invalid witness sign')
    return free(invert(conjugator) + (before if sign == 1 else invert(before)) + conjugator)


def normalization(before, witness_rows, after):
    require(sorted(row['input_index'] for row in witness_rows) == list(range(len(before))), 'normalization omits or duplicates relator')
    for row in witness_rows:
        original = before[row['input_index']]
        require(word(row['before']) == original, 'normalization input wrong')
        require(conjugation(original, row['sign'], word(row['conjugator'])) == word(row['after']) == representative(original), 'normalization conjugation wrong')
    require(tuple(word(row['after']) for row in witness_rows) == after == normalized(before), 'normalization order wrong')


def removal_event(event):
    before = words(event['before'])
    i, generator = event['defining_index'], event['generator']
    require(type(i) is int and 0 <= i < len(before), 'invalid removal row')
    require(type(generator) is int and generator > 0, 'invalid removed generator')
    defining = before[i]
    require(defining == word(event['defining_relator']), 'defining row wrong')
    positions = [p for p, x in enumerate(defining) if abs(x) == generator]
    require(positions == [event['occurrence_position']], 'removed generator not unique in defining row')
    require(event['occurrence_sign'] == (1 if defining[positions[0]] > 0 else -1), 'occurrence sign wrong')
    replacement = word(event['isolating_word'])
    require(all(abs(x) != generator for x in replacement) and free(replacement) == replacement, 'invalid isolating word')
    form = (-generator,) + replacement
    require(word(event['normal_form']) == form, 'normal form wrong')
    witness = event['normal_form_witness']
    require(conjugation(defining, witness['sign'], word(witness['conjugator'])) == form, 'isolating conjugation wrong')
    basis = {abs(x) for w in before for x in w}
    mapping = {g: ((g,) if g != generator else replacement) for g in basis}
    surviving_indices = [j for j in range(len(before)) if j != i]
    require([r['input_index'] for r in event['substitutions']] == surviving_indices, 'removal omits or duplicates old relator')
    survivors, total_raw_length = [], 0
    for row in event['substitutions']:
        original = before[row['input_index']]
        require(word(row['before']) == original, 'substitution input wrong')
        raw = image(original, mapping, reduce=False)
        require(raw == word(row['raw_substitution']), 'signed removal expansion wrong')
        require(row['replaced_occurrences'] == sum(abs(x) == generator for x in original), 'removal occurrence count wrong')
        reduced_word = free(raw)
        require(reduced_word == word(row['after_free_reduction']), 'removal free reduction wrong')
        survivors.append(reduced_word)
        total_raw_length += len(raw)
    raw_after = words(event['raw_after'])
    require(tuple(survivors) == raw_after, 'raw removal survivors wrong')
    after = words(event['after'])
    normalization(raw_after, event['normalization'], after)
    require(len(after) == len(before) - 1 and all(abs(x) != generator for w in after for x in w), 'rank or generator removal wrong')
    require(event['before_generator_ids'] == sorted(basis), 'input generator metadata wrong')
    require(event['after_generator_ids'] == sorted(basis - {generator}), 'surviving generator metadata wrong')
    require(event['generator_relabeling'] == 'identity_on_survivors', 'unexpected relabeling')
    require(event['literal_substitution_length'] == total_raw_length, 'removal literal length wrong')
    require(event['final_length'] == size(after) and event['length_change'] == size(after) - size(before), 'removal final length wrong')
    require(event['charged_units'] == 1 and event['fully_expanded_elementary_certificate'] is False, 'removal work or certificate scope wrong')
    require(event['required_hypothesis'] == 'known balanced presentation of the trivial group', 'missing Lemma11 hypothesis')
    require(event['certificate_kind'] == 'theorem_backed_stable_composite', 'removal certificate kind wrong')
    check_tuple(before)
    check_tuple(after)
    return after


def ac_event(event):
    before = words(event['before'])
    i, j, sign = event['target'], event['donor'], event['donor_sign']
    require(type(i) is int and type(j) is int and 0 <= i < len(before) and 0 <= j < len(before) and i != j, 'invalid target/donor')
    require(type(sign) is int and sign in (-1, 1), 'invalid AC donor sign')
    left = before[i]
    right = before[j] if sign == 1 else invert(before[j])
    k, l = event['target_cut'], event['donor_cut']
    require(type(k) is int and type(l) is int and 0 <= k < len(left) and 0 <= l < len(right), 'invalid AC rotation')
    multiplied = representative(left[k:] + left[:k] + right[l:] + right[:l])
    raw = before[:i] + (multiplied,) + before[i + 1:]
    after = words(event['after'])
    require(normalized(raw) == after and len(after) == len(before), 'AC substitution endpoint wrong')
    require(len(multiplied) < len(before[i]), 'AC descent is not strict')
    check_tuple(before)
    check_tuple(after)
    return after


def check_event(event):
    kind = event['kind']
    if kind == 'defining_compression':
        return defining_event(event)
    if kind == 'ambient_whitehead':
        return whitehead_event(event)
    if kind == 'lemma11_removal':
        return removal_event(event)
    if kind == 'ordinary_ac_substitution':
        return ac_event(event)
    if kind == 'relator_normalization':
        after = words(event['after'])
        normalization(words(event['before']), event['normalization'], after)
        return after
    raise AssertionError(f'unsupported event kind {kind}')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def saved_paths():
    source_path = ROOT / 'research/theory_patterns_20260912/u124_final_table.json'
    source = json.loads(source_path.read_text())
    report = json.loads((HERE / 'basis_all124.json').read_text())
    require(report['hashes']['u124_final_table.json'] == sha(source_path), 'source table changed')
    for name in ('search.py', 'basis_search.py'):
        require(report['hashes'][name] == sha(HERE / name), f'{name} provenance differs')
    require(report['hashes']['whitehead.py'] == sha(HERE / 'whitehead_first_screen.py'), 'executed Whitehead snapshot differs')
    source_rows = {row['name']: row for row in source['rows']}
    rows = report['rows']
    require(len(rows) == len({r['name'] for r in rows}) == 124, 'wrong or duplicate denominator')
    require(set(source_rows) == {r['name'] for r in rows}, 'source denominator differs')
    csv_path = ROOT / 'data/ms_unsolved_reps/aca_124_best.csv'
    with csv_path.open() as handle:
        archive = {r['name']: [r['r1'], r['r2']] for r in csv.DictReader(handle)}
    gained = []
    all_events = Counter()
    for row in rows:
        old = source_rows[row['name']]
        saved = parse(old['best_words'], row['input_generator_map'])
        original = parse(old['starting_words'], row['rank2_generator_map'])
        require(archive[row['name']] == old['starting_words'], 'starting_words differ from saved rank-two archive')
        require(saved == words(row['saved_best']) and original == words(row['saved_rank2']), 'source words differ')
        require(row['source_pointer'] == old['source_certificate_pointer'], 'saved-best source pointer differs')
        require(row['input_length'] == size(saved), 'input length wrong')
        require(row['total_units'] == row['definition_evaluations'] + row['minimum_cut_evaluations'] <= 1000, 'candidate budget wrong')
        require(row['fully_expanded_stable_certificate'] is False and row['rank_limit'] is None, 'certificate/rank scope changed')
        require(row['path_source'] in ('saved_best', 'saved_rank2'), 'unknown initial source')
        initial = saved if row['path_source'] == 'saved_best' else original
        current = normalized(initial)
        boundaries = [{'rank': len(current), 'length': size(current)}]
        for event in row['events']:
            require(words(event['before']) == current, 'broken path continuity')
            all_events[event['kind']] += 1
            current = check_event(event)
            boundaries.append({'rank': len(current), 'length': size(current)})
        if row['events']:
            require(current == words(row['best']), 'path endpoint differs')
        else:
            require(normalized(row['best']) == current, 'identity endpoint differs')
        endpoint = words(row['best'])
        check_tuple(endpoint)
        require(size(endpoint) == row['best_length'] and len(endpoint) == row['best_rank'], 'endpoint metrics wrong')
        require(row['additional_gain'] == size(saved) - size(endpoint) >= 0, 'gain wrong')
        if row['additional_gain']:
            gained.append({'name': row['name'], 'path_source': row['path_source'],
                           'actual_source_pointer': old['source_certificate_pointer'] if row['path_source'] == 'saved_best' else f'data/ms_unsolved_reps/aca_124_best.csv#name={row["name"]}',
                           'input_length': row['input_length'], 'path_start_length': size(initial),
                           'best_length': row['best_length'], 'boundaries': boundaries,
                           'endpoint': endpoint, 'status': 'PASS'})
    summary = report['summary']
    ids = [r['name'] for r in gained]
    require(ids == summary['gain_ids'] == ['aca_36', 'aca_57', 'aca_80', 'aca_82', 'aca_86'], 'gain IDs differ')
    require(sum(r['input_length'] for r in rows) == summary['input_total'] == 2191, 'input total wrong')
    require(sum(r['best_length'] for r in rows) == summary['best_total'] == 2186, 'endpoint total wrong')
    for key in ('total_units', 'definition_evaluations', 'minimum_cut_evaluations'):
        require(sum(r[key] for r in rows) == summary[key], 'summary budget wrong')
    require(dict(Counter(str(r['best_rank']) for r in rows)) == summary['best_ranks'], 'rank distribution wrong')
    return {'status': 'PASS', 'rows_checked': 124, 'gain_rows': gained, 'events': dict(all_events),
            'input_total': 2191, 'best_total': 2186, 'archive_sha256': sha(csv_path),
            'source_table_sha256': sha(source_path), 'search_frontier_not_reexecuted': True}


def mixed_paths(filename):
    source_path = ROOT / 'research/theory_patterns_20260912/u124_final_table.json'
    source_rows = {r['name']: r for r in json.loads(source_path.read_text())['rows']}
    report = json.loads((HERE / filename).read_text())
    for name, expected in report['hashes'].items():
        path = source_path if name == source_path.name else HERE / name
        require(sha(path) == expected, f'{filename}: {name} provenance differs')
    rows = report['rows']
    require(len(rows) == len({r['name'] for r in rows}) == 124, 'mixed denominator wrong')
    require({r['name'] for r in rows} == set(source_rows), 'mixed IDs differ')
    gains, events, retained_prefix_gains = [], Counter(), []
    for row in rows:
        source = source_rows[row['name']]
        saved = parse(source['best_words'], row['input_generator_map'])
        original = parse(source['starting_words'], row['rank2_generator_map'])
        require(saved == words(row['saved_best']) and original == words(row['saved_rank2']), 'mixed input words differ')
        require(row['saved_best_pointer'] == source['source_certificate_pointer'], 'mixed stable source pointer wrong')
        require(row['saved_rank2_pointer'] == source['best_rank2_source_certificate_pointer'], 'mixed rank-two source pointer wrong')
        require(source['starting_words'] == source['best_rank2_words'], 'rank-two pointer does not identify starting_words')
        require(row['path_source'] in ('saved_best', 'saved_rank2'), 'mixed path source unknown')
        initial = saved if row['path_source'] == 'saved_best' else original
        current = normalized(initial)
        boundaries = [{'kind': 'source', 'rank': len(current), 'length': size(current)}]
        for event in row['events']:
            require(words(event['before']) == current, 'mixed path discontinuity')
            current = check_event(event)
            events[event['kind']] += 1
            boundaries.append({'kind': event['kind'], 'rank': len(current), 'length': size(current)})
        endpoint = words(row['best'])
        require(current == normalized(endpoint), 'mixed endpoint differs')
        require(row['input_length'] == size(saved) and row['best_length'] == size(endpoint), 'mixed length wrong')
        require(row['best_rank'] == len(endpoint), 'mixed endpoint rank wrong')
        require(row['additional_gain'] == size(saved) - size(endpoint) >= 0, 'mixed gain wrong')
        require(row['total_units'] == sum(row['costs'].values()) <= row['budget'] == 1000, 'mixed budget wrong')
        require(row['rank_limit'] is None and row['length_limit'] is None, 'mixed ceiling unexpectedly set')
        require(row['fully_expanded_stable_certificate'] is False, 'mixed certificate scope wrong')
        check_tuple(endpoint)
        best_prefix = min(b['length'] for b in boundaries)
        if best_prefix < row['best_length']:
            retained_prefix_gains.append({'name': row['name'], 'reported_length': row['best_length'], 'retained_prefix_length': best_prefix})
        if row['additional_gain']:
            gains.append({'name': row['name'], 'path_source': row['path_source'],
                          'actual_source_pointer': row[row['path_source'] + '_pointer'],
                          'input_length': size(saved), 'path_start_length': size(initial),
                          'best_length': size(endpoint), 'best_rank': len(endpoint),
                          'boundaries': boundaries, 'endpoint': endpoint, 'status': 'PASS'})
    summary = report['summary']
    require([r['name'] for r in gains] == summary['gain_ids'], 'mixed summary gain IDs wrong')
    require(sum(r['input_length'] for r in rows) == summary['input_total'] == 2191, 'mixed input total wrong')
    require(sum(r['best_length'] for r in rows) == summary['best_total'], 'mixed endpoint total wrong')
    require(sum(r['total_units'] for r in rows) == summary['total_units'], 'mixed work total wrong')
    require(dict(Counter(str(r['best_rank']) for r in rows)) == summary['best_ranks'], 'mixed rank distribution wrong')
    return {'status': 'PASS', 'file': filename, 'file_sha256': sha(HERE / filename),
            'rows_checked': 124, 'gain_rows': gains, 'events': dict(events),
            'input_total': summary['input_total'], 'best_total': summary['best_total'],
            'retained_prefix_improvements_beyond_report': retained_prefix_gains,
            'limitation': 'Only stored winning paths and their boundaries are replayed. Unretained candidate/intermediate boundaries, visited-rank maxima, frontier coverage and global minima are not independently established.'}


def observer_paths():
    table_path = ROOT / 'research/theory_patterns_20260912/u124_final_table.json'
    source_rows = {r['name']: r for r in json.loads(table_path.read_text())['rows']}
    reports, census_ids, total_units = [], [], 0
    for filename in ('observed_pilot.json', 'observed_remainder.json', 'observed_rank16.json'):
        report = json.loads((HERE / filename).read_text())
        require(report['script_sha256'] == sha(HERE / 'observed_search.py'), 'observer script changed')
        reference_path = HERE / Path(report['reference']).name
        require(sha(reference_path) == report['reference_sha256'], 'observer reference changed')
        reference = json.loads(reference_path.read_text())
        reference_rows = {r['name']: r for r in reference['rows']}
        witnesses, event_counts = [], Counter()
        names = [r['name'] for r in report['rows']]
        require(len(names) == len(set(names)), 'observer duplicate row')
        if filename != 'observed_rank16.json':
            census_ids.extend(names)
        else:
            require(names == ['aca_108'], 'rank16 identity changed')
        for row in report['rows']:
            source, prior = source_rows[row['name']], reference_rows[row['name']]
            require(row['mode'] == prior['mode'], 'observer mode differs')
            require(row['input_length'] == prior['input_length'], 'observer input length wrong')
            require(row['reference_best_length'] == prior['best_length'], 'observer reference length wrong')
            require(row['total_units'] == prior['total_units'] == 1000, 'observer physical budget wrong')
            require(row['original_search_decisions_reproduced'] is True, 'observer decision check absent')
            require(row['certificate_kind'] == 'theorem_backed_stable_composite', 'observer certificate scope wrong')
            require(row['additional_gain'] == row['input_length'] - row['best_length'], 'observer gain wrong')
            require(row['new_gain_from_boundary_capture'] == prior['best_length'] - row['best_length'] == 0, 'observer reports extra prefix gain')
            row_witnesses = {}
            for key in ('best_witness', 'maximum_rank_witness'):
                witness = row[key]
                require(witness['source'] in ('saved_best', 'saved_rank2'), 'observer source unknown')
                if witness['source'] == 'saved_best':
                    initial = parse(source['best_words'], prior['input_generator_map'])
                else:
                    initial = parse(source['starting_words'], prior['rank2_generator_map'])
                current = normalized(initial)
                require(current == words(witness['initial']), 'observer initial words wrong')
                boundaries = [{'rank': len(current), 'length': size(current)}]
                for event in witness['events']:
                    require(words(event['before']) == current, 'observer path discontinuity')
                    current = check_event(event)
                    event_counts[event['kind']] += 1
                    boundaries.append({'rank': len(current), 'length': size(current)})
                require(current == words(witness['endpoint']), 'observer endpoint wrong')
                require(len(current) == witness['rank'] and size(current) == witness['total_length'], 'observer endpoint metrics wrong')
                check_tuple(current)
                require(all(b['length'] >= row['best_length'] and b['rank'] <= row['maximum_inspected_rank'] for b in boundaries), 'saved chain contradicts observer extrema')
                row_witnesses[key] = {'rank': len(current), 'total_length': size(current), 'boundaries': boundaries}
            require(row['best_witness']['total_length'] == row['best_length'], 'best observer witness not best length')
            require(row['maximum_rank_witness']['rank'] == row['maximum_inspected_rank'], 'highest observer witness not highest rank')
            curve = {int(rank): length for rank, length in row['inspected_rank_length_curve'].items()}
            require(max(curve) == row['maximum_inspected_rank'] and min(curve.values()) == row['best_length'], 'observer rank curve extrema wrong')
            require(curve[row['maximum_inspected_rank']] == row['maximum_rank_witness']['total_length'], 'highest-rank curve length wrong')
            witnesses.append({'name': row['name'], 'status': 'PASS', **row_witnesses})
        summary = report['summary']
        require(summary['rows'] == len(names), 'observer summary denominator wrong')
        require(summary['gain_ids'] == [r['name'] for r in report['rows'] if r['additional_gain']], 'observer gain IDs wrong')
        require(summary['boundary_capture_gains'] == [], 'unexpected observer gain')
        for key in ('input_total', 'best_total'):
            field = 'input_length' if key == 'input_total' else 'best_length'
            require(summary[key] == sum(r[field] for r in report['rows']), 'observer length sum wrong')
        units = sum(r['total_units'] for r in report['rows'])
        require(summary['physical_replayed_work_units'] == units, 'observer work sum wrong')
        require(summary['maximum_inspected_rank'] == max(r['maximum_inspected_rank'] for r in report['rows']), 'observer max rank summary wrong')
        total_units += units
        reports.append({'file': filename, 'file_sha256': sha(HERE / filename), 'status': 'PASS',
                        'rows': len(names), 'events_replayed_including_shared_prefixes': dict(event_counts),
                        'physical_replayed_work_units': units, 'witnesses': witnesses})
    require(len(census_ids) == len(set(census_ids)) == 124 and set(census_ids) == set(source_rows), 'observer pilot/remainder do not partition U124')
    require(total_units == 125000, 'observer replay work total wrong')
    high = reports[-1]['witnesses'][0]['maximum_rank_witness']
    require(high['rank'] == 16 and high['total_length'] == 44, 'aca108 rank16 endpoint wrong')
    require({10, 11, 12, 13, 14, 15, 16} <= {b['rank'] for b in high['boundaries']}, 'high-rank witness omits intermediate ranks')
    return {'status': 'PASS', 'reports': reports, 'frontier_joint_distinct_ids': 124,
            'frontier_physical_replayed_units': 124000, 'separate_ladder_replay_units': 1000,
            'total_extra_physical_replayed_units': total_units,
            'rank16_witness': {'name': 'aca_108', 'rank': 16, 'total_length': 44, 'boundaries': high['boundaries']},
            'scope': 'Every stored best and maximum-rank chain independently replayed. Observer extrema outside these chains rely on the pinned instrumentation record; no census search rerun by audit.py.'}


def resolve_pointer(pointer, base=HERE):
    filename, fragment = pointer.split('#', 1)
    path = (base / filename).resolve()
    require(path.is_file(), 'witness pointer file missing: ' + pointer)
    data = json.loads(path.read_text())
    for component in fragment.lstrip('/').split('/'):
        component = component.replace('~1', '/').replace('~0', '~')
        data = data[int(component)] if isinstance(data, list) else data[component]
    return data


def rendered(value):
    alphabet = 'xyzuvw'
    rendered_words = []
    for w in value:
        if all(abs(x) <= len(alphabet) for x in w):
            rendered_words.append(''.join(alphabet[abs(x) - 1] if x > 0 else alphabet[abs(x) - 1].upper() for x in w))
        else:
            rendered_words.append(' '.join('g' + str(abs(x)) + ('^-1' if x < 0 else '') for x in w))
    return '(' + ', '.join(rendered_words) + ')'


def final_delivery():
    source_path = ROOT / 'research/theory_patterns_20260912/u124_final_table.json'
    source = json.loads(source_path.read_text())
    prior_rows = {r['name']: r for r in source['rows']}
    report = json.loads((HERE / 'all124.json').read_text())
    require(report['baseline_sha256'] == sha(source_path), 'delivery baseline hash wrong')
    rows = report['rows']
    require(len(rows) == len({r['name'] for r in rows}) == 124, 'delivery denominator wrong')
    require({r['name'] for r in rows} == set(prior_rows), 'delivery IDs wrong')
    certificates = [json.loads(line) for line in (HERE / 'shortening_witnesses.jsonl').read_text().splitlines()]
    require(len(certificates) == len({r['name'] for r in certificates}) == 15, 'export certificate denominator wrong')
    exported = {r['name']: r for r in certificates}
    pointer_count, event_counts, solved = 0, Counter(), 0
    checked_exports = []
    for row in rows:
        prior = prior_rows[row['name']]
        pointed = resolve_pointer(row['witness_pointer'])
        pointer_count += 1
        new = row['new_gain'] > 0 or row['rank_reduction'] > 0
        if new:
            require(row['name'] in exported, 'missing exported new witness')
            cert = exported[row['name']]
            require(cert['witness'] == pointed, 'JSONL witness differs from final table pointer')
            require(cert['old_table_sha256'] == sha(source_path), 'JSONL baseline hash wrong')
            witness = cert['witness']
            kind = cert['source_kind']
            require(kind == witness['source'] and kind in ('saved_best', 'saved_rank2'), 'JSONL source kind wrong')
            strings = prior['best_words'] if kind == 'saved_best' else prior['starting_words']
            expected_pointer = prior['source_certificate_pointer'] if kind == 'saved_best' else prior['best_rank2_source_certificate_pointer']
            require(cert['source_pointer'] == expected_pointer, 'stale JSONL source pointer')
            initial = parse(strings, cert['input_letter_map'])
            if expected_pointer.startswith('data/'):
                filename, fragment = expected_pointer.split('#', 1)
                with (ROOT / filename).open() as handle:
                    upstream = {r['name']: r for r in csv.DictReader(handle)}[row['name']]
                require(fragment == 'name=' + row['name'] and [upstream['r1'], upstream['r2']] == strings, 'rank-two upstream pointer wrong')
            else:
                upstream = resolve_pointer(expected_pointer, source_path.parent)
                upstream_strings = upstream.get('final_relators', upstream.get('relators'))
                require(upstream_strings == strings, 'stable upstream pointer words differ')
            current = normalized(initial)
            require(current == words(witness['initial']), 'JSONL witness starts from wrong source')
            for event in witness['events']:
                require(words(event['before']) == current, 'JSONL path discontinuity')
                current = check_event(event)
                event_counts[event['kind']] += 1
            endpoint = words(witness['endpoint'])
            require(current == endpoint, 'JSONL path endpoint wrong')
            require(cert['endpoint_length'] == witness['total_length'] == size(endpoint), 'JSONL endpoint length wrong')
            require(witness['rank'] == len(endpoint), 'JSONL endpoint rank wrong')
            require(cert['previous_best_length'] == prior['best_any_rank_length'], 'JSONL prior length wrong')
            require(cert['length_gain'] == row['new_gain'] and cert['rank_reduction'] == row['rank_reduction'], 'JSONL gain/rank metadata wrong')
            require(cert['certificate_kind'] == row['certificate_kind'] == 'theorem_backed_stable_composite' and cert['fully_expanded_elementary_path'] is False, 'JSONL certificate scope wrong')
            checked_exports.append({'name': row['name'], 'status': 'PASS', 'length': size(endpoint), 'rank': len(endpoint), 'source_kind': kind, 'source_pointer': cert['source_pointer']})
        else:
            require(pointed == prior, 'unchanged row pointer resolves to wrong baseline row')
            mapping = {c: i + 1 for i, c in enumerate(sorted({c.lower() for w in prior['best_words'] for c in w}, key='xyzuvw'.index))}
            endpoint = parse(prior['best_words'], mapping)
            require(row['name'] not in exported, 'unchanged row unexpectedly exported')
        require(row['best_words'] == rendered(endpoint), 'table endpoint words differ from source witness')
        require(row['best_rank'] == len(endpoint) and row['best_any_rank_length'] == size(endpoint), 'table endpoint metrics wrong')
        require(row['archival_initial_length'] == prior['archival_initial_length'], 'archival length wrong')
        require(row['saved_rank2_length'] == prior['starting_best_length'], 'saved rank-two length wrong')
        require(row['previous_any_rank_length'] == prior['best_any_rank_length'], 'previous stable length wrong')
        require(row['new_gain'] == prior['best_any_rank_length'] - size(endpoint), 'table gain wrong')
        require(row['rank_reduction'] == max(0, prior['best_rank'] - len(endpoint)), 'table rank reduction wrong')
        is_solved = not endpoint or all(len(w) == 1 for w in endpoint) and len({abs(w[0]) for w in endpoint}) == len(endpoint)
        require(row['solved'] == is_solved, 'table solve flag wrong')
        solved += is_solved
        check_tuple(endpoint)
    summary = report['summary']
    expected = {'rows': 124, 'new_gain_ids': [r['name'] for r in rows if r['new_gain']],
                'same_length_rank_reduction_ids': [r['name'] for r in rows if not r['new_gain'] and r['rank_reduction']],
                'previous_total': sum(r['previous_any_rank_length'] for r in rows),
                'new_total': sum(r['best_any_rank_length'] for r in rows),
                'saved_rank2_total': sum(r['saved_rank2_length'] for r in rows),
                'shorter_than_saved_rank2': sum(r['best_any_rank_length'] < r['saved_rank2_length'] for r in rows),
                'solved': solved, 'best_rank_counts': dict(Counter(str(r['best_rank']) for r in rows))}
    require(summary == expected, 'final summary does not match rows')
    require(summary['previous_total'] == 2191 and summary['new_total'] == 2180 and summary['saved_rank2_total'] == 2356, 'final totals wrong')
    require(summary['shorter_than_saved_rank2'] == 89 and solved == 0, 'final coverage wrong')
    require(summary['best_rank_counts'] == {'2': 35, '3': 87, '4': 2}, 'final rank distribution wrong')
    require(summary['same_length_rank_reduction_ids'] == ['aca_108', 'aca_112', 'aca_113', 'aca_114'], 'rank reduction IDs wrong')
    require(len(summary['new_gain_ids']) == 11, 'length gain count wrong')
    with (HERE / 'all124.csv').open(newline='') as handle:
        csv_rows = list(csv.DictReader(handle))
    require(csv_rows == [{k: str(v) for k, v in r.items()} for r in rows], 'CSV differs from JSON')
    markdown_rows = [line for line in (HERE / 'ALL124.md').read_text().splitlines() if line.startswith('| aca_')]
    expected_markdown = ['| ' + ' | '.join(str(row[k]) for k in ('name', 'archival_initial_length', 'saved_rank2_length', 'previous_any_rank_length', 'best_any_rank_length', 'best_rank', 'new_gain')) + ' |' for row in rows]
    require(markdown_rows == expected_markdown, 'Markdown table differs from JSON')
    return {'status': 'PASS', 'table_rows': 124, 'resolved_witness_pointers': pointer_count,
            'exported_witnesses': checked_exports, 'exported_event_counts': dict(event_counts),
            'summary': summary, 'all_output_words_and_ranks_match_witnesses': True,
            'CSV_JSON_Markdown_agree': True,
            'file_sha256': {name: sha(HERE / name) for name in ('README.md', 'ALL124.md', 'all124.json', 'all124.csv', 'shortening_witnesses.jsonl', 'summarize.py')}}


def partial_panel_paths():
    report = json.loads((HERE / 'partial_panel.json').read_text())
    for name, expected in report['hashes'].items():
        require(sha(HERE / name) == expected, 'partial panel source hash differs')
    mixed = json.loads((HERE / 'mixed_all124.json').read_text())
    selected = {r['name']: r for r in mixed['rows'] if r['additional_gain'] or r['best_rank'] >= 4}
    require(len(report['rows']) == len(selected) == 17 and {r['name'] for r in report['rows']} == set(selected), 'partial panel selection wrong')
    candidates, events, total_units = 0, Counter(), 0
    for row in report['rows']:
        initial = words(row['input'])
        require(initial == words(selected[row['name']]['best']), 'partial panel source input wrong')
        require(row['input_length'] == size(initial), 'partial panel input length wrong')
        for candidate in row['candidates']:
            current = initial
            for event in candidate['events']:
                require(words(event['before']) == current, 'partial candidate discontinuity')
                current = check_event(event)
                require(size(current) >= row['best_length'], 'partial candidate prefix has unreported gain')
                events[event['kind']] += 1
            require(current == words(candidate['after']), 'partial candidate endpoint wrong')
            candidates += 1
        require(words(row['best']) == initial and row['events'] == [] and row['additional_gain'] == 0, 'partial outcome differs')
        require(row['best_length'] == size(initial) and row['best_rank'] == len(initial), 'partial endpoint metrics wrong')
        require(0 <= row['total_units'] <= row['budget'] == 1000, 'partial budget wrong')
        total_units += row['total_units']
    require(report['summary']['gain_ids'] == [] and report['summary']['total_units'] == total_units == 5380, 'partial summary wrong')
    return {'status': 'PASS', 'rows': 17, 'candidates_replayed': candidates,
            'event_counts': dict(events), 'additional_gains': 0, 'total_units': total_units,
            'file_sha256': sha(HERE / 'partial_panel.json')}


def load_subjects():
    sys.path.insert(0, str(HERE))
    import search
    import whitehead
    import whitehead_first_screen
    return search, whitehead, whitehead_first_screen


def tiny_controls(search, whitehead):
    mincuts, formulas = 0, 0
    vertices = (-2, -1, 1, 2)
    pairs = list(combinations(vertices, 2))
    for weights in product(range(3), repeat=len(pairs)):
        graph = {pair: n for pair, n in zip(pairs, weights) if n}
        if {v for e in graph for v in e} != set(vertices):
            continue
        for a in vertices:
            free_vertices = [x for x in vertices if x not in (a, -a)]
            brute = min(capacity(graph, {a} | {x for x, b in zip(free_vertices, mask) if b})
                        for mask in product((False, True), repeat=len(free_vertices)))
            got, side = whitehead.minimum_cut(graph, a)
            require(got == brute == capacity(graph, side) and a in side and -a not in side, 'minimum cut differs from exhaustive partitions')
            mincuts += 1
    for rank, maximum_length in ((1, 4), (2, 4), (3, 3)):
        letters = tuple(range(-rank, 0)) + tuple(range(1, rank + 1))
        for length in range(1, maximum_length + 1):
            for value in product(letters, repeat=length):
                if cyclic(value) != value:
                    continue
                edges = adjacency((value,))
                require(dict(whitehead.graph((value,))) == dict(edges), 'implementation graph differs')
                for a in letters:
                    remaining = [x for x in letters if x not in (a, -a)]
                    for mask in product((False, True), repeat=len(remaining)):
                        side = {a} | {x for x, included in zip(remaining, mask) if included}
                        mapping = whitehead_images(rank, a, side)
                        require(whitehead.images(range(1, rank + 1), a, side) == mapping, 'signed image formula differs')
                        delta = len(cyclic(image(value, mapping))) - len(value)
                        expected = capacity(edges, side) - sum(n for edge, n in edges.items() if a in edge)
                        require(delta == expected, 'Whitehead formula fails on tiny exhaustive word')
                        formulas += 1
    high_rank = []
    for rank in (7, 8, 12):
        defining = (1, -2, 3)
        seed = tuple((g,) for g in range(1, rank - 1)) + ((rank - 1,) + defining * 3, (rank,) + invert(defining) * 3)
        require(abs(determinant(seed)) == 1, 'planted tuple has wrong determinant')
        require(image(seed[-2], {g: (() if g < rank - 1 else (g,)) for g in range(1, rank + 1)}) == (rank - 1,), 'planted triviality substitution failed')
        require(image(seed[-1], {g: (() if g < rank else (g,)) for g in range(1, rank + 1)}) == (rank,), 'planted triviality substitution failed')
        require(words(search.normalize(seed)) == normalized(seed), 'arbitrary-rank normalization differs')
        after, event = search.compress(normalized(seed), defining)
        require(defining_event(event) == words(after), 'arbitrary-rank compression fails')
        require(size(seed) - size(after) == 8, 'planted signed compression gain wrong')
        next_after, next_event = search.compress(after, (rank + 1, rank + 1))
        require(defining_event(next_event) == words(next_after), 'recursive high-rank compression fails')
        for a in (rank + 2, -(rank + 2)):
            changed, event = whitehead.transform(next_after, a, {a, -1, 2})
            require(whitehead_event(event) == words(changed), 'arbitrary-rank signed Whitehead map fails')
        high_rank.append({'start_rank': rank, 'after_two_definitions_rank': rank + 2,
                          'largest_signed_generator_tested': rank + 2, 'status': 'PASS'})
    return {'status': 'PASS', 'weighted_rank2_graph_minimum_cuts': mincuts,
            'exhaustive_signed_word_partition_formulas': formulas, 'high_rank_planted_trivial_tuples': high_rank,
            'scope': 'finite unit controls, not census searches; high-rank triviality follows by the displayed triangular substitutions'}


def removal_controls():
    import lemma11
    count = 0
    for rank in (8, 13):
        generator = rank - 1
        for sign in (-1, 1):
            seed = tuple((g,) for g in range(1, rank - 1)) + ((2, sign * generator, -1), (rank, generator, 1, -generator))
            check_tuple(seed)
            after, event = lemma11.remove_one(seed, rank - 2, generator)
            require(removal_event(event) == words(after), 'high-rank Lemma11 signed isolation fails')
            require({abs(x) for w in after for x in w} == set(range(1, rank + 1)) - {generator}, 'nonconsecutive surviving labels lost')
            count += 1
    return {'status': 'PASS', 'signed_high_rank_removals': count,
            'initial_ranks': [8, 13], 'nonconsecutive_survivor_labels_verified': True,
            'triviality_proof': 'Lower generators are singleton relators; the defining row then kills the isolated generator, and the final row kills the last generator.'}


def reporting_fix(whitehead, original):
    class StripMetadata(ast.NodeTransformer):
        def visit_Assign(self, node):
            if any(isinstance(x, ast.Name) and x.id in ('complete', 'scanned') for x in node.targets):
                return None
            return self.generic_visit(node)

        def visit_AugAssign(self, node):
            if isinstance(node.target, ast.Name) and node.target.id == 'scanned':
                return None
            return self.generic_visit(node)

    def algorithm(path):
        return ast.dump(StripMetadata().visit(ast.parse(path.read_text())), include_attributes=False)

    require(algorithm(HERE / 'whitehead.py') == algorithm(HERE / 'whitehead_first_screen.py'), 'fix changes nonmetadata algorithm')
    basis_tree = ast.parse((HERE / 'basis_search.py').read_text())
    references = [n for n in ast.walk(basis_tree) if isinstance(n, ast.Constant) and n.value == 'aut_minimal']
    dictionary_keys = [key for n in ast.walk(basis_tree) if isinstance(n, ast.Dict) for key in n.keys]
    require(len(references) == 2 and all(x in dictionary_keys for x in references), 'basis search reads metadata')
    previous = original.descend(((1,), (2, 1)), 7)
    current = whitehead.descend(((1,), (2, 1)), 7)
    require(previous[:3] == current[:3] and previous[3] is True and current[3] is False, 'incomplete-last-cut control differs')
    for budget in (6, 8):
        require(original.descend(((1,), (2, 1)), budget) == whitehead.descend(((1,), (2, 1)), budget), 'neighboring budget changed')
    return {'status': 'PASS', 'executed_snapshot_sha256': sha(HERE / 'whitehead_first_screen.py'),
            'corrected_sha256': sha(HERE / 'whitehead.py'), 'only_reporting_dataflow_changed': True,
            'basis_search_never_reads_aut_minimal': True,
            'reproducer': {'tuple': [[1], [2, 1]], 'cut_budget': 7, 'old_complete': True, 'new_complete': False,
                           'endpoint_path_and_charged_cuts_identical': True}}


def main():
    if '--delivery-only' in sys.argv:
        output = json.loads((HERE / 'audit.json').read_text())
        require(output['status'] == 'PASS', 'previous audit did not pass')
        output['final_delivery_validation'] = final_delivery()
        output['partial_panel_validation'] = partial_panel_paths()
        output['final_review_script_sha256'] = sha(HERE / 'audit.py')
        output['final_review_report_sha256'] = sha(HERE / 'AUDIT.md')
        output['final_review_repeats_exhaustive_controls'] = False
        (HERE / 'audit.json').write_text(json.dumps(output, indent=2) + '\n')
        print(json.dumps({'status': 'PASS', 'final_summary': output['final_delivery_validation']['summary'],
                          'witnesses_replayed': len(output['final_delivery_validation']['exported_witnesses']),
                          'partial_panel': output['partial_panel_validation']}, indent=2))
        return
    start = time.process_time()
    saved = saved_paths()
    mixed = [mixed_paths(name) for name in ('mixed_all124.json', 'ladder_all124.json')]
    observed = observer_paths()
    search, whitehead, original = load_subjects()
    controls = tiny_controls(search, whitehead)
    removals = removal_controls()
    fix = reporting_fix(whitehead, original)
    report = {'status': 'PASS', 'audit_kind': 'independent stable-composite witness audit',
              'independence': 'Saved-witness reduction, cyclic canonicalization, signed expansion, inverse checks, graph capacity and determinant use only audit.py implementations. Subject modules are called only to exercise planted controls and compare mincuts with exhaustive tiny partitions.',
              'saved_paths': saved, 'mixed_reports': mixed, 'unit_controls': controls,
              'observer_reports': observed, 'lemma11_controls': removals, 'reporting_fix': fix,
              'certificate_conventions_sha256': sha(ROOT / 'research/theory_patterns_20260912/STABLE_CERTIFICATE_CONVENTIONS.md'),
              'theorem_review': {'status': 'PASS_WITH_SCOPE',
                                 'two_step_bypass': 'Valid at freely and cyclically reduced literal boundaries, with no intervening operations beyond rotations. It asserts existence and gain of a direct compression, not equal endpoints or necessity of a first step.',
                                 'stable_realizability': 'Uses the known-trivial-group hypothesis of Lemma 11 and its reverse; unimodularity alone is insufficient. No elementary normal-product expansion was generated.',
                                 'rank_bounds': 'Valid under the stated strict-gain/full-rank and singleton-free hypotheses. Neither arbitrary input lengths nor accepted neutral/uphill moves have a universal fixed rank bound.'},
              'verified_file_sha256': {name: sha(HERE / name) for name in ('audit.py', 'AUDIT.md', 'basis_all124.json', 'basis_search.py', 'search.py', 'whitehead.py', 'whitehead_first_screen.py', 'THEOREM_NOTE.md', 'mixed_search.py', 'mixed_all124.json', 'ladder_all124.json', 'lemma11.py', 'observed_search.py', 'observed_pilot.json', 'observed_remainder.json', 'observed_rank16.json')},
              'audit_cpu_seconds': time.process_time() - start}
    report['final_delivery_validation'] = final_delivery()
    report['partial_panel_validation'] = partial_panel_paths()
    (HERE / 'audit.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'basis_gain_ids': [r['name'] for r in saved['gain_rows']],
                      'mixed_reports': [{'file': r['file'], 'gain_rows': len(r['gain_rows']),
                                         'input_total': r['input_total'], 'best_total': r['best_total']} for r in mixed],
                      'observer_witness_chains': 2 * sum(r['rows'] for r in observed['reports']),
                      'verified_rank16_total_length': observed['rank16_witness']['total_length'],
                      'minimum_cut_controls': controls['weighted_rank2_graph_minimum_cuts'],
                      'signed_word_partition_controls': controls['exhaustive_signed_word_partition_formulas'],
                      'audit_cpu_seconds': report['audit_cpu_seconds']}, indent=2))


if __name__ == '__main__':
    main()
