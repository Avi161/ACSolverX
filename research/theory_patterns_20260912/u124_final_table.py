"""Build an interim all124 table; admit gains only through replayed witnesses."""
from __future__ import annotations

import argparse
from copy import deepcopy
import csv
from datetime import datetime, timezone
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from ac_words import Trace, replay
from check_ac_words import independent_replay

HERE = Path(__file__).resolve().parent
IDS = ['aca_' + str(i) for i in range(124)]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def solved_pair(pair):
    return (2 <= len(pair) <= 6 and all(isinstance(w, str) and len(w) == 1 for w in pair)
            and len({w.lower() for w in pair}) == len(pair)
            and all(w in 'xXyYzZuUvVwW' for w in pair))


def record_verified(rows, name, pair, pointer, *, kind, moves, witness=None):
    row = rows[name]
    rank, length = len(pair), sum(map(len, pair))
    if not 2 <= rank <= 6 or not all(isinstance(w, str) for w in pair):
        raise ValueError(f'{pointer}: unsupported balanced presentation rank')
    if solved_pair(pair):
        row['status'] = ('solved_ordinary' if kind == 'ordinary' or row['status'] == 'solved_ordinary'
                         else 'solved_stable')
    if rank == 2 and length < row['best_rank2_length']:
        row.update({'best_rank2_length': length, 'best_rank2_words': pair,
                    'best_rank2_certificate_kind': kind,
                    'best_rank2_source_certificate_pointer': pointer,
                    'best_rank2_certificate_moves': moves, 'best_rank2_witness': witness})
    if (length, rank) >= (row['best_any_rank_length'], row['best_rank']):
        return False
    row.update({'best_certified_length': length, 'best_any_rank_length': length,
                'best_rank': rank, 'best_words': pair,
                'gain_this_session': row['starting_best_length'] - length,
                'certificate_kind': kind, 'source_certificate_pointer': pointer,
                'certificate_moves': moves, 'certificate_witness': witness})
    return True


def admit(rows, name, pair, moves, pointer, *, kind='ordinary', rank=2):
    if name not in rows:
        raise ValueError(f'{pointer}: unknown U124 name {name}')
    row = rows[name]
    if not isinstance(pair, list) or not all(isinstance(w, str) for w in pair):
        raise ValueError(f'{pointer}: malformed endpoint')
    length = sum(map(len, pair))
    if length >= row['best_rank2_length'] and length >= row['best_any_rank_length'] and not solved_pair(pair):
        return False
    if kind != 'ordinary' or rank != 2 or len(pair) != 2:
        raise ValueError(f'{pointer}: stable gains require an independent theorem-prefix replay adapter')
    if not isinstance(moves, list):
        raise ValueError(f'{pointer}: claimed ordinary gain has no elementary witness')
    if replay(row['starting_words'], moves) != pair or independent_replay(row['starting_words'], moves) != pair:
        raise ValueError(f'{pointer}: claimed gain fails independent replay from authoritative starting words')
    if solved_pair(pair):
        cleanup = Trace(pair)
        for target in (0, 1):
            if cleanup.pair[target].isupper():
                cleanup.invert(target)
        if cleanup.pair == ['y', 'x']:
            for op, target in (('invert', 0), ('multiply', 1), ('invert', 1),
                               ('multiply', 0), ('invert', 0), ('multiply', 1)):
                getattr(cleanup, op)(target)
        moves = moves + cleanup.moves
        pair = cleanup.pair
        assert pair == ['x', 'y'] and independent_replay(row['starting_words'], moves) == pair
    return record_verified(rows, name, pair, pointer, kind='ordinary', moves=moves)


def admit_audited_stable(rows, name, pair, pointer, witness, verified_pair):
    """Adapter hook: verified_pair must be returned by an independent prefix replayer."""
    if pair != verified_pair:
        raise ValueError(f'{pointer}: stable prefix does not match independent replay')
    if not isinstance(witness, dict) or not witness.get('audit_sha256') or not witness.get('source_sha256'):
        raise ValueError(f'{pointer}: stable prefix provenance is incomplete')
    return record_verified(rows, name, pair, pointer, kind='theorem_backed_stable_prefix',
                           moves=None, witness=witness)


def load_independent_checker(audit_name, source_name, module_name):
    audit_path, source_path, module_path = (HERE / name for name in (audit_name, source_name, module_name))
    audit = json.loads(audit_path.read_text())
    if audit['status'] != 'pass':
        raise ValueError(f'{audit_name}: independent audit is not complete/pass')
    if digest(source_path) != audit['source_report_sha256'] or digest(module_path) != audit['audit_script_sha256']:
        raise ValueError(f'{audit_name}: source report or independent checker hash mismatch')
    source = json.loads(source_path.read_text())
    specification = importlib.util.spec_from_file_location(module_path.stem, module_path)
    checker = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(checker)
    return audit, source, checker, {
        'audit_file': audit_name, 'audit_sha256': digest(audit_path),
        'source_file': source_name, 'source_sha256': digest(source_path),
        'auditor_file': module_name, 'auditor_sha256': digest(module_path),
        'proof': 'STABLE_CERTIFICATE_CONVENTIONS.md',
        'certificate_kind': 'independently_verified_theorem_backed_stable_prefix',
        'expanded_normal_products': False}


def admit_primitive_stable(rows):
    audit_name = 'primitive_compression_independent_audit.json'
    if not (HERE / audit_name).exists():
        return None
    audit, source, checker, evidence = load_independent_checker(
        audit_name, 'primitive_compression_report.json', 'check_primitive_compression_independent.py')
    if audit['original_panel_inventory_sha256'] != digest(HERE / 'u124_inventory.json'):
        raise ValueError('primitive audit input inventory hash differs from authoritative inventory')
    for source_check in audit['source_hash_checks']:
        if source_check['verified'] is not True or digest(Path(source_check['path'])) != source_check['sha256']:
            raise ValueError('primitive audited source bytes changed: ' + source_check['path'])
    source_rows = {r['name']: r for r in source['rows']}
    if len(audit['rows']) != len(source_rows) or {r['name'] for r in audit['rows']} != set(source_rows):
        raise ValueError('primitive independent ledger/source row coverage mismatch')
    admitted, verified = [], 0
    for audited in audit['rows']:
        name = audited['name']
        original = rows[name]['starting_words']
        row = source_rows[name]
        if audited['input'] != original or row['input'] != original:
            raise ValueError(f'{audit_name}: {name} input differs from saved-best CSV')
        if audited['input_length'] != sum(map(len, original)):
            raise ValueError(f'{audit_name}: {name} input length differs')
        prefix = audited['minimum_rank3_witness']
        if prefix is not None:
            attempt = row['attempts'][prefix['attempt_index']]
            if attempt['input'] != original:
                raise ValueError('primitive attempt is attached to another source input')
            checked = checker.verify_prefix(attempt, prefix['boundary_index'])
            for key in ('relators', 'rank', 'total_length', 'label', 'relator_lengths'):
                if checked[key] != prefix[key]:
                    raise ValueError(f'{audit_name}: {name} stored prefix {key} differs from independent replay')
            if checked['total_length'] != audited['minimum_rank3_total_length']:
                raise ValueError('primitive rank3 minimum disagrees with its exact witness')
            pointer = evidence['source_file'] + '#' + prefix['json_pointer']
            changed = admit_audited_stable(rows, name, checked['relators'], pointer,
                {**evidence, 'json_pointer': prefix['json_pointer'], 'attempt_index': prefix['attempt_index'],
                 'boundary_index': prefix['boundary_index'], 'label': checked['label']}, checked['relators'])
            verified += 1
            if changed:
                admitted.append(name)
        endpoint = audited['rank2_endpoint_minimum_pair']
        if endpoint is not None and sum(map(len, endpoint)) < rows[name]['best_rank2_length']:
            index, attempt = next((i, a) for i, a in enumerate(row['attempts']) if a.get('endpoint') == endpoint)
            checked = checker.verify_attempt(attempt)
            if not checked['verified']:
                raise ValueError('independent primitive endpoint replay failed')
            pointer = evidence['source_file'] + f'#name={name}/attempts/{index}/endpoint'
            admit_audited_stable(rows, name, endpoint, pointer,
                {**evidence, 'attempt_index': index, 'boundary': 'rank2_endpoint'}, attempt['endpoint'])
    return {**evidence, 'prefixes_independently_replayed_on_refresh': verified,
            'admitted_best_changes': admitted}


def admit_dictionary_stable(rows):
    audit_name = 'stable_dictionary_independent_audit.json'
    if not (HERE / audit_name).exists():
        return None
    audit, source, checker, evidence = load_independent_checker(
        audit_name, 'stable_dictionary_compression_report.json', 'stable_dictionary_independent_audit.py')
    csv_path = HERE.parents[1] / 'data/ms_unsolved_reps/aca_124_best.csv'
    if audit['source_csv_sha256'] != digest(csv_path) or source['source_sha256'] != digest(csv_path):
        raise ValueError('dictionary input CSV hash mismatch')
    if audit['author_script_sha256'] != digest(HERE / 'stable_dictionary_compression.py'):
        raise ValueError('dictionary author source hash mismatch')
    if audit['conventions_sha256'] != digest(HERE / 'STABLE_CERTIFICATE_CONVENTIONS.md'):
        raise ValueError('dictionary finite-realizability conventions changed')
    source_rows = {r['name']: (i, r) for i, r in enumerate(source['rows'])}
    if len(audit['rows']) != 124 or len(source_rows) != 124 or {r['name'] for r in audit['rows']} != set(rows):
        raise ValueError('dictionary audited/source U124 coverage mismatch')
    admitted, verified = [], 0
    for audited in audit['rows']:
        name = audited['name']
        source_index, record = source_rows[name]
        original = rows[name]['starting_words']
        if audited['input'] != original or record['input'] != original:
            raise ValueError(f'{audit_name}: {name} input differs from saved-best CSV')
        if audited['input_length'] != sum(map(len, original)):
            raise ValueError('dictionary input total mismatch')
        prefix = audited['minimum_rank3_witness']
        if prefix is None:
            if record['best'] is not None or audited['all_rank_minimum_total_length'] != sum(map(len, original)):
                raise ValueError('dictionary negative/minimum ledger mismatch')
            continue
        checked = checker.verify_prefix(original, record['best'])
        for key in ('relators', 'rank', 'total_length', 'relator_lengths', 'defining_word', 'cuts', 'compressed_relators'):
            if checked[key] != prefix[key]:
                raise ValueError(f'{audit_name}: {name} {key} differs from independent replay')
        expected_pointer = f'/rows/{source_index}/best'
        if (prefix['json_pointer'] != expected_pointer or checked['total_length'] != audited['minimum_rank3_total_length']
                or checked['total_length'] != audited['all_rank_minimum_total_length']):
            raise ValueError('dictionary pointer/minimum mismatch')
        pointer = evidence['source_file'] + '#' + expected_pointer
        changed = admit_audited_stable(rows, name, checked['relators'], pointer,
            {**evidence, 'json_pointer': expected_pointer, 'defining_word': checked['defining_word'],
             'cuts': checked['cuts'], 'compressed_relators': checked['compressed_relators'],
             'token_counts': checked['token_counts'], 'all_relator_lengths': checked['relator_lengths']},
            checked['relators'])
        verified += 1
        if changed:
            admitted.append(name)
    if verified != audit['counts']['positive_prefixes_independently_verified']:
        raise ValueError('dictionary verified positive count mismatch')
    return {**evidence, 'prefixes_independently_replayed_on_refresh': verified,
            'admitted_best_changes': admitted}


def admit_rank3_ac_stable(rows):
    audit_name = 'stable_rank3_ac_independent_audit.json'
    if not (HERE / audit_name).exists():
        return None
    audit, source, checker, evidence = load_independent_checker(
        audit_name, 'stable_rank3_ac_descent_report.json', 'stable_rank3_ac_independent_audit.py')
    dependencies = {
        'source_csv_sha256': HERE.parents[1] / 'data/ms_unsolved_reps/aca_124_best.csv',
        'author_script_sha256': HERE / 'stable_rank3_ac_descent.py',
        'dictionary_source_report_sha256': HERE / 'stable_dictionary_compression_report.json',
        'dictionary_auditor_sha256': HERE / 'stable_dictionary_independent_audit.py'}
    for key, path in dependencies.items():
        if audit[key] != digest(path):
            raise ValueError('rank3 ordinary suffix dependency changed: ' + str(path))
    source_rows = {r['name']: (i, r) for i, r in enumerate(source['rows'])}
    if len(source_rows) != len(source['rows']) or len(audit['rows']) != len(source_rows):
        raise ValueError('rank3 ordinary suffix audited/source row count mismatch')
    if {r['name'] for r in audit['rows']} != set(source_rows):
        raise ValueError('rank3 ordinary suffix audited/source row names mismatch')
    admitted, verified = [], 0
    for audited in audit['rows']:
        name = audited['name']
        index, record = source_rows[name]
        original = rows[name]['starting_words']
        if record['input'] != original or audited['input'] != original:
            raise ValueError('rank3 ordinary suffix input differs from authoritative saved start')
        if audited['input_length'] != sum(map(len, original)):
            raise ValueError('rank3 ordinary suffix input length mismatch')
        prefix = audited['minimum_rank3_witness']
        checked = checker.verify_prefix(record)
        if not checked['independently_verified'] or prefix['json_pointer'] != f'/rows/{index}':
            raise ValueError('rank3 ordinary suffix independent replay or pointer mismatch')
        for key in ('relators', 'rank', 'total_length', 'relator_lengths', 'endpoint',
                    'endpoint_total_length', 'elementary_moves', 'ordinary_suffix_minimum_move_index'):
            if prefix[key] != checked[key]:
                raise ValueError(f'rank3 ordinary suffix {name} independent {key} mismatch')
        if checked['total_length'] != audited['all_rank_minimum_total_length']:
            raise ValueError('rank3 ordinary suffix minimum ledger mismatch')
        if audited['combined_logged_work'] > 1000:
            raise ValueError('rank3 ordinary suffix exceeded the declared shared candidate budget')
        endpoint_is_minimum = checked['endpoint_total_length'] == checked['total_length']
        pair = checked['endpoint'] if endpoint_is_minimum else checked['relators']
        pointer = evidence['source_file'] + '#' + prefix['json_pointer']
        changed = admit_audited_stable(rows, name, pair, pointer,
            {**evidence, 'json_pointer': prefix['json_pointer'],
             'boundary': 'canonical_endpoint' if endpoint_is_minimum else 'earliest_minimum',
             'ordinary_suffix_moves': checked['elementary_moves'] if endpoint_is_minimum
                 else checked['elementary_moves'][:checked['ordinary_suffix_minimum_move_index']],
             'ordinary_suffix_index_convention': 'zero_based_targets_and_donors',
             'all_relator_lengths': list(map(len, pair)),
             'dictionary_source_report_sha256': audit['dictionary_source_report_sha256'],
             'dictionary_auditor_sha256': audit['dictionary_auditor_sha256']}, pair)
        verified += 1
        if changed:
            admitted.append(name)
    return {**evidence, 'prefixes_independently_replayed_on_refresh': verified,
            'admitted_best_changes': admitted}


def admit_recursive_stable(rows):
    audit_name = 'recursive_stable_compression_independent_audit.json'
    if not (HERE / audit_name).exists():
        return None
    audit, source, checker, evidence = load_independent_checker(
        audit_name, 'recursive_stable_compression_report.json', 'recursive_stable_compression_independent_audit.py')
    for filename, key in (('recursive_stable_compression.py', 'module_sha256'),
                          ('recursive_stable_compression_checks.py', 'checks_sha256'),
                          ('STABLE_CERTIFICATE_CONVENTIONS.md', 'conventions_sha256')):
        if source[key] != digest(HERE / filename):
            raise ValueError('recursive source dependency changed: ' + filename)
    table_hash = hashlib.sha256(source['source_table_text'].encode()).hexdigest()
    if table_hash != source['source_table_sha256'] or table_hash != audit['source_table_sha256']:
        raise ValueError('recursive frozen seed table hash mismatch')
    table = json.loads(source['source_table_text'])
    if len(table['rows']) != 124 or {r['name'] for r in table['rows']} != set(rows):
        raise ValueError('recursive frozen seed table U124 coverage mismatch')
    keepers = {r['name']: r for r in table['rows'] if r['gain_this_session'] > 0}
    records = source['records']
    if (len(keepers) != len(records) or len(audit['rows']) != len(records)
            or {r['name'] for r in audit['rows']} != set(keepers)):
        raise ValueError('recursive independent ledger/frozen seed coverage mismatch')
    admitted, verified = [], 0
    for audited in audit['rows']:
        name, index = audited['name'], audited['source_record_index']
        record = records[index]
        if (record['name'] != name or record['source_keeper'] != keepers[name]
                or record['source_keeper']['starting_words'] != rows[name]['starting_words']
                or record['source_table_sha256'] != table_hash):
            raise ValueError('recursive record is not linked to the exact audited saved-start keeper')
        if audited['json_pointer'] != f'/records/{index}':
            raise ValueError('recursive source pointer mismatch')
        checked = checker.verify_prefix(record)
        if not checked['independently_verified'] or not checked['source_provenance_verified']:
            raise ValueError('recursive independent prefix replay failed')
        for target, field in (('relators', 'minimum_relators'), ('rank', 'minimum_rank'),
                              ('total_length', 'minimum_total_length')):
            if checked[target] != audited[field]:
                raise ValueError(f'recursive independent ledger {name} {field} mismatch')
        if audited['input_total_length'] != sum(map(len, record['input'])):
            raise ValueError('recursive seed length mismatch')
        pointer = evidence['source_file'] + '#' + audited['json_pointer']
        changed = admit_audited_stable(rows, name, checked['relators'], pointer,
            {**evidence, 'json_pointer': audited['json_pointer'], 'source_table_sha256': table_hash,
             'seed_source_certificate_pointer': record['source_keeper']['source_certificate_pointer'],
             'seed_certificate_witness': record['source_keeper']['certificate_witness'],
             'basis': checked['basis'], 'all_relator_lengths': list(map(len, checked['relators']))},
            checked['relators'])
        verified += 1
        if changed:
            admitted.append(name)
    continuations = source.get('continuations', [])
    if len(continuations) != audit['continuations_checked']:
        raise ValueError('recursive continuation coverage mismatch')
    for index, record in enumerate(continuations):
        checked = checker.verify_prefix(record)
        if not checked['independently_verified'] or record['combined_recursive_candidates'] > 1000:
            raise ValueError('recursive continuation replay/budget failed')
        pointer = evidence['source_file'] + f'#/continuations/{index}'
        changed = admit_audited_stable(rows, record['name'], checked['relators'], pointer,
            {**evidence, 'json_pointer': f'/continuations/{index}',
             'seed_source_prefix': record['source_prefix'], 'basis': checked['basis'],
             'all_relator_lengths': list(map(len, checked['relators']))}, checked['relators'])
        if changed:
            admitted.append(record['name'])
    return {**evidence, 'prefixes_independently_replayed_on_refresh': verified,
            'continuations_independently_replayed_on_refresh': len(continuations),
            'admitted_best_changes': admitted}


def admit_complement_suffixes(rows):
    audit_name = 'two_complement_unit_gate_independent_audit.json'
    audit_path = HERE / audit_name
    if not audit_path.exists():
        return None
    audit = json.loads(audit_path.read_text())
    module_path = HERE / 'two_complement_unit_gate_independent_audit.py'
    if audit['status'] != 'pass' or digest(module_path) != audit['auditor_source_sha256']:
        raise ValueError('complement suffix audit is incomplete or its checker changed')
    for filename, expected in audit['source_hashes'].items():
        if filename == 'u124_inventory.json':
            path = HERE.parents[2] / filename
        elif filename.startswith('data/'):
            path = HERE.parents[1] / filename
        else:
            path = HERE / filename
        if digest(path) != expected:
            raise ValueError('complement suffix audited source changed: ' + filename)
    spec = importlib.util.spec_from_file_location(module_path.stem, module_path)
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    evidence = {'audit_file': audit_name, 'audit_sha256': digest(audit_path),
                'auditor_file': module_path.name, 'auditor_sha256': digest(module_path),
                'proof': 'two_complement_independent_theory.md',
                'proof_sha256': digest(HERE / 'two_complement_independent_theory.md'),
                'certificate_kind': 'independently_verified_stable_bridge_then_ordinary_prefix',
                'expanded_normal_products': False, 'ordinary_equivalence_from_original_claimed': False}
    cache, admitted, rank2_changes, seen = {}, [], [], set()

    def read_source(filename, expected, file_format='json'):
        path = HERE / filename
        if digest(path) != expected:
            raise ValueError('complement minimum source hash mismatch: ' + filename)
        key = filename, file_format
        if key not in cache:
            text = path.read_text()
            cache[key] = [json.loads(line) for line in text.splitlines()] if file_format == 'jsonl' else json.loads(text)
        return cache[key]

    for minimum in audit['minima']:
        name, index = minimum['name'], minimum['source_row_index']
        source_name = minimum['source_report']
        source = read_source(source_name, minimum['source_report_sha256'])
        source_row = source['rows'][index]
        gate_source = read_source(minimum['gate_source_report'], minimum['gate_source_report_sha256'])
        gate_rows = [(i, r) for i, r in enumerate(gate_source['rows']) if r['name'] == name]
        if len(gate_rows) != 1 or source_row['name'] != name:
            raise ValueError('complement minimum input/source row join is ambiguous')
        gate_index, gate_row = gate_rows[0]
        file_format = minimum.get('certificate_format', 'jsonl')
        if file_format not in ('json', 'jsonl'):
            raise ValueError('unsupported complement certificate format')
        certificates = read_source(minimum['certificate_file'], minimum['certificate_file_sha256'], file_format)
        line_index = minimum.get('certificate_line_index', 0)
        certificate = certificates[line_index] if file_format == 'jsonl' else certificates
        identity = source_name, index, minimum['certificate_file'], line_index
        if identity in seen:
            raise ValueError('duplicate complement minimum ledger entry')
        seen.add(identity)
        checked = checker.verify_prefix(gate_row, certificate, source_row)
        if (checked['input'] != rows[name]['starting_words'] or minimum['input'] != rows[name]['starting_words']
                or checked['input_length'] != rows[name]['starting_best_length']):
            raise ValueError('complement stable bridge is not joined to the authoritative original input')
        if (not checked['independently_verified'] or not checked['stable_bridge_verified'] or checked['rank'] != 2
                or len(checked['relators']) != 2 or checked['ordinary_equivalence_from_original_claimed']):
            raise ValueError('complement prefix lacks the required stable bridge/ordinary suffix proof')
        for key in ('relators', 'rank', 'relator_lengths', 'total_length', 'minimum_move_index', 'endpoint',
                    'endpoint_total_length', 'elementary_move_count', 'replayed_total_lengths',
                    'minimum_including_original_length', 'combined_units'):
            if checked[key] != minimum[key]:
                raise ValueError('complement independent minimum replay mismatch: ' + key)
        if checked['combined_units'] > 1000:
            raise ValueError('complement continuation exceeds its declared per-attempt budget')
        pointer = minimum['certificate_file'] + (f'#line={line_index + 1}' if file_format == 'jsonl' else '#/')
        before_rank2 = rows[name]['best_rank2_length']
        changed = admit_audited_stable(rows, name, checked['relators'], pointer,
            {**evidence, 'source_file': source_name, 'source_sha256': minimum['source_report_sha256'],
             'source_json_pointer': f'/rows/{index}',
             'gate_source_report': minimum['gate_source_report'], 'gate_source_report_sha256': minimum['gate_source_report_sha256'],
             'gate_source_json_pointer': f'/rows/{gate_index}', 'certificate_file': minimum['certificate_file'],
             'certificate_sha256': minimum['certificate_file_sha256'], 'certificate_format': file_format,
             'certificate_line_index': line_index, 'minimum_move_index': checked['minimum_move_index'],
             'ordinary_suffix_moves': certificate['moves'][:checked['minimum_move_index']],
             'ordinary_suffix_input': certificate['input'], 'all_relator_lengths': checked['relator_lengths'],
             'stable_bridge_maximum_rank': 5, 'stable_bridge_internal_length_bound': None}, checked['relators'])
        if changed:
            admitted.append(name)
        if rows[name]['best_rank2_length'] < before_rank2:
            rank2_changes.append(name)
    return {**evidence, 'prefixes_independently_replayed_on_refresh': len(seen),
            'admitted_best_changes': admitted, 'admitted_rank2_best_changes': rank2_changes,
            'source_hashes': audit['source_hashes']}


def candidates_from_standard(rows, records, source, pairs='best_pair', moves='best_moves'):
    for index, record in enumerate(records):
        name = record['name']
        if record.get('input') is not None and record['input'] != rows[name]['starting_words']:
            raise ValueError(f'{source}/records/{index}: input differs from authoritative saved best')
        if pairs in record and record[pairs] is not None:
            admit(rows, name, record[pairs], record.get(moves), f'{source}#/records/{index}/{pairs}')


def named_claims(node, rows, pointer='', name=None):
    """Find new numerical/solve claims even in an unregistered future component."""
    if isinstance(node, list):
        for index, value in enumerate(node):
            yield from named_claims(value, rows, pointer + '/' + str(index), name)
    elif isinstance(node, dict):
        if node.get('name') in rows:
            name = node['name']
        for key in ('solved', 'solved_ids', 'solved_ordinary_ids', 'solved_stable_ids', 'strict_length_improved', 'strict_length_improved_ids', 'improved', 'improved_ids', 'new_gain_ids', 'strict_stable_gain_ids', 'rank3_gain_ids', 'rank2_gain_ids', 'rank2_endpoint_gain_ids'):
            value = node.get(key)
            if isinstance(value, list):
                for claimed_name in value:
                    if isinstance(claimed_name, str) and claimed_name in rows:
                        yield claimed_name, (None if key.startswith('solved') else 'gain'), pointer + '/' + key
        if name is not None:
            baseline = rows[name]['starting_best_length']
            for key in ('best_length', 'best_certified_length', 'best_any_rank_length', 'minimum_rank3_total_length', 'all_rank_minimum_total_length', 'best_length_including_start', 'best_rank2_length', 'rank2_endpoint_minimum_length', 'best_endpoint_length', 'total_length', 'final_length'):
                value = node.get(key)
                if isinstance(value, (int, float)) and value < baseline:
                    yield name, value, pointer + '/' + key
            if node.get('strict_length_improvement') is True and not isinstance(node.get('best_length'), (int, float)):
                yield name, 'gain', pointer + '/strict_length_improvement'
            if isinstance(node.get('gain_this_session'), (int, float)) and node['gain_this_session'] > 0:
                yield name, 'gain', pointer + '/gain_this_session'
            if node.get('solved') is True or node.get('status') in ('solved', 'solved_ordinary', 'solved_stable'):
                yield name, None, pointer + '/solved'
        for key, value in node.items():
            if key in ('planted', 'checks', 'full_certificates', 'corridor_cases', 'torus_cases'):
                continue
            yield from named_claims(value, rows, pointer + '/' + key, key if key in rows else name)


def claim_covered(row, length, pointer):
    field = pointer.rsplit('/', 1)[-1]
    compared = row['best_rank2_length'] if ('rank2' in field or field == 'best_endpoint_length') else row['best_any_rank_length']
    return ((length is None and row['status'] in ('solved_ordinary', 'solved_stable'))
            or (length == 'gain' and compared < row['starting_best_length'])
            or (isinstance(length, (int, float)) and compared <= length))


def check_unadapted_notes(rows):
    checks = []
    path = HERE / 'two_complement_independent_theory.json'
    if path.exists():
        theory = json.loads(path.read_text())
        case = theory['aca1_rooted_bs_two_pinches']
        current = case['source_pair']
        minimum = sum(map(len, current))
        cyclic_minimum = minimum
        for move in case['elementary_moves']:
            current = independent_replay(current, [move])
            minimum = min(minimum, sum(map(len, current)))
            cores = []
            for word in current:
                while len(word) > 1 and word[0] == word[-1].swapcase():
                    word = word[1:-1]
                cores.append(word)
            cyclic_minimum = min(cyclic_minimum, sum(map(len, cores)))
        if current != case['final_pair']:
            raise ValueError('aca1 saved proper-power ordinary suffix failed replay')
        original = next(r for r in rows if r['name'] == 'aca_1')
        length = sum(map(len, case['final_pair']))
        if length != case['final_total'] or min(minimum, cyclic_minimum) < original['starting_best_length']:
            raise ValueError('new aca1 proper-power original-input gain requires a verified stable bridge adapter')
        checks.append({'source': path.name, 'source_sha256': digest(path),
                       'name': 'aca_1', 'original_start_length': original['starting_best_length'],
                       'projected_source_length': sum(map(len, case['source_pair'])),
                       'ordinary_suffix_endpoint_length': length,
                       'all_elementary_minimum_length': minimum, 'cyclic_length_minimum': cyclic_minimum,
                       'elementary_moves_replayed': len(case['elementary_moves']),
                       'reason': 'projected shortening remains longer than original input'})
    return checks


def validate_table(result):
    rows = result['rows']
    if len(rows) != 124 or [r['name'] for r in rows] != IDS:
        raise ValueError('published table does not cover every U124 input exactly once')
    csv_path, json_path, md_path = (HERE / ('u124_final_table.' + suffix) for suffix in ('csv', 'json', 'md'))
    if b'\r' in csv_path.read_bytes():
        raise ValueError('table CSV is not LF-only')
    with csv_path.open() as stream:
        csv_rows = list(csv.DictReader(stream))
    if [r['name'] for r in csv_rows] != IDS or len([s for s in md_path.read_text().splitlines() if s.startswith('| aca_')]) != 124:
        raise ValueError('CSV/Markdown U124 row coverage mismatch')
    for row, csv_row in zip(rows, csv_rows):
        if not (row['best_any_rank_length'] == row['best_certified_length'] == sum(map(len, row['best_words']))
                <= row['best_rank2_length'] == sum(map(len, row['best_rank2_words'])) <= row['starting_best_length']):
            raise ValueError('endpoint ranks, words, or saved-start minima disagree')
        if json.loads(csv_row['best_words']) != row['best_words'] or json.loads(csv_row['best_rank2_words']) != row['best_rank2_words']:
            raise ValueError('CSV exact words differ from JSON')
        if csv_row['best_rank2_certificate_kind'] != row['best_rank2_certificate_kind']:
            raise ValueError('CSV rank2 proof kind differs from JSON')
        for field in ('archival_initial_length', 'starting_best_length', 'best_rank2_length',
                      'best_any_rank_length', 'best_certified_length', 'best_rank', 'gain_this_session'):
            if int(csv_row[field]) != row[field]:
                raise ValueError('CSV numerical ledger differs from JSON: ' + field)
        for witness in (row['certificate_witness'], row['best_rank2_witness']):
            if witness:
                for filename, key in (('source_file', 'source_sha256'), ('audit_file', 'audit_sha256'), ('auditor_file', 'auditor_sha256')):
                    if digest(HERE / witness[filename]) != witness[key]:
                        raise ValueError('admitted witness source changed before table validation')
    if sum(r['archival_initial_length'] for r in rows) != 2446 or sum(r['starting_best_length'] for r in rows) != 2356:
        raise ValueError('historical baseline totals differ')
    historical_count = sum(r['archival_initial_length'] > r['starting_best_length'] for r in rows)
    if historical_count != 36:
        raise ValueError('historical reduced-row count differs from immutable baselines')
    sample = deepcopy(rows[0])
    sample.update(starting_best_length=6, best_rank2_length=6, best_any_rank_length=6, best_rank=2,
                  status='unsolved', best_words=['xxx', 'yyy'], best_rank2_words=['xxx', 'yyy'])
    synthetic = {'control': sample}
    record_verified(synthetic, 'control', ['xx', 'y'], 'validation_only', kind='theorem_backed_stable_prefix', moves=None)
    if sample['best_rank2_certificate_kind'] != 'theorem_backed_stable_prefix' or sample['status'] != 'unsolved':
        raise ValueError('stable rank2 endpoint mislabeled ordinary or solved')
    record_verified(synthetic, 'control', ['x', 'y'], 'validation_only', kind='theorem_backed_stable_prefix', moves=None)
    if sample['status'] != 'solved_stable':
        raise ValueError('stable rank2 terminal basis mislabeled ordinary')
    guard_row = {'starting_best_length': 6, 'best_rank2_length': 6, 'best_any_rank_length': 6, 'status': 'unsolved'}
    rejected = list(named_claims({'name': 'control', 'best_length': 0, 'solved': True}, {'control': guard_row}))
    if len(rejected) != 2 or any(claim_covered(guard_row, length, pointer) for _, length, pointer in rejected):
        raise ValueError('unproved gain/solve claim guard failed')
    marking_claims = list(named_claims({'name': IDS[0], 'search': {'images': ['', '', 'x', 'y'], 'best_image_length': 2}}, {r['name']: r for r in rows}))
    if marking_claims:
        raise ValueError('Nielsen image marking was treated as presentation progress')
    validation = {'status': 'pass', 'snapshot_utc': result['snapshot_utc'], 'table_status': result['status'],
        'row_count': 124, 'exact_id_sequence': True, 'csv_lf_only': True,
        'artifacts_sha256': {p.name: digest(p) for p in (json_path, csv_path, md_path, Path(__file__))},
        'archival_initial_length_sum': 2446, 'starting_best_length_sum': 2356,
        'historical_reduced_rows_not_credited_to_session': historical_count,
        'best_rank2_length_sum': result['best_rank2_length_sum'], 'best_any_rank_length_sum': result['best_any_rank_length_sum'],
        'gain_rows': len(result['new_gain_ids']), 'unsolved_rows': result['unsolved_count'],
        'ordinary_solved_rows': len(result['solved_ordinary_ids']), 'stable_solved_rows': len(result['solved_stable_ids']),
        'best_rank_counts': {str(rank): sum(r['best_rank'] == rank for r in rows) for rank in sorted({r['best_rank'] for r in rows})},
        'non_admitted_component_checks': result['non_admitted_component_checks'],
        'semantic_checks': ['all relators counted', 'rank2 endpoint may have a stable proof',
                            'stable rank2 solve is not ordinary', 'unproved gain and solve rejected',
                            'Nielsen image marking is not a presentation state'],
        'scope': 'Validation of this saved table and its admitted proof hashes; no search or new mathematical result.'}
    (HERE / 'final_table_validation.json').write_text(json.dumps(validation, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--final', action='store_true', help='Label an explicitly requested deadline snapshot final.')
    parser.add_argument('--extra-component', type=Path, action='append', default=[],
                        help='JSON with certified_rows: name,input,final_pair,moves,rank,certificate_kind.')
    args = parser.parse_args()
    inventory = json.loads((HERE / 'u124_inventory.json').read_text())
    root = HERE.parents[1]
    baselines = {}
    for kind in ('initial', 'best'):
        path = root / inventory['sources'][kind]['path']
        if digest(path) != inventory['sources'][kind]['sha256']:
            raise ValueError('authoritative baseline changed: ' + str(path))
        with path.open() as stream:
            baselines[kind] = {r['name']: r for r in csv.DictReader(stream)}
        assert set(baselines[kind]) == set(IDS)
    rows = {}
    for name in IDS:
        original, start = baselines['initial'][name], baselines['best'][name]
        words = [start['r1'], start['r2']]
        length = sum(map(len, words))
        rows[name] = {'name': name, 'archival_initial_length': len(original['r1']) + len(original['r2']),
            'starting_best_length': length, 'best_certified_length': length,
            'best_rank2_length': length, 'best_any_rank_length': length, 'best_rank2_words': words,
            'status': 'unsolved', 'best_rank': 2, 'starting_words': words, 'best_words': words,
            'gain_this_session': 0, 'certificate_kind': 'identity_at_saved_start',
            'source_certificate_pointer': inventory['sources']['best']['path'] + '#name=' + name,
            'certificate_moves': [], 'certificate_witness': None,
            'best_rank2_certificate_kind': 'identity_at_saved_start',
            'best_rank2_source_certificate_pointer': inventory['sources']['best']['path'] + '#name=' + name,
            'best_rank2_certificate_moves': [], 'best_rank2_witness': None}
    assert sum(r['archival_initial_length'] for r in rows.values()) == 2446
    assert sum(r['starting_best_length'] for r in rows.values()) == 2356
    component_data, component_hashes = {}, {}
    excluded = {'u124_inventory.json', 'session.json', 'u124_final_table.json', 'final_table_validation.json'}
    for path in sorted(HERE.glob('*.json')):
        if path.name in excluded or path.name.startswith('u124_final_table'):
            continue
        raw = path.read_bytes()
        component_data[path.name] = json.loads(raw)
        component_hashes[path.name] = hashlib.sha256(raw).hexdigest()
    intermediate = component_data['intermediate_minima.json']
    assert intermediate['status'] == 'complete'
    candidates_from_standard(rows, intermediate['rows'], 'intermediate_minima.json')
    extreme = component_data['extreme_residues_report.json']['saved_checkpoint_extension']
    candidates_from_standard(rows, extreme['records'], 'extreme_residues_report.json#/saved_checkpoint_extension')
    boundary = component_data['boundary_compiler_report.json']['full_u124']['records']
    for ri, record in enumerate(boundary):
        assert record['input'] == rows[record['name']]['starting_words']
        for ai, attempt in enumerate(record['attempts']):
            pointer = f'boundary_compiler_report.json#/full_u124/records/{ri}/attempts/{ai}'
            admit(rows, record['name'], attempt['best_pair'], attempt['best_moves'], pointer + '/best_moves')
            if attempt['status'] == 'solved':
                admit(rows, record['name'], attempt['final_pair'], attempt['moves'], pointer + '/moves')
    prepared_summary = component_data['prepared_frames_report.json']['full_u124']
    prepared_claims = set(prepared_summary['strict_length_improved_ids']) | set(prepared_summary['solved_ids'])
    if prepared_claims:
        with gzip.open(HERE / 'prepared_frames_full124.jsonl.gz', 'rt') as stream:
            for line, text in enumerate(stream, 1):
                record = json.loads(text)
                if record['name'] in prepared_claims:
                    admit(rows, record['name'], record['best_pair'], record['best_moves'],
                          f'prepared_frames_full124.jsonl#line={line}/best_moves')
    for ri, record in enumerate(component_data['critical_pairs_panel.json']['records']):
        assert record['input'] == rows[record['name']]['starting_words']
        for ci, case in enumerate(record['cases']):
            admit(rows, record['name'], case['pair'], case['moves'],
                  f'critical_pairs_panel.json#/records/{ri}/cases/{ci}/moves')
    for path in args.extra_component:
        data = json.loads(path.read_text())
        component_data[str(path)] = data
        component_hashes[str(path)] = digest(path)
        for index, record in enumerate(data['certified_rows']):
            if record['input'] != rows[record['name']]['starting_words']:
                raise ValueError(f'{path}: certificate input differs from saved start')
            admit(rows, record['name'], record['final_pair'], record.get('moves'),
                  f'{path}#/certified_rows/{index}', kind=record.get('certificate_kind', 'ordinary'),
                  rank=record.get('rank', 2))
    stable_adapters = [value for value in (admit_primitive_stable(rows), admit_dictionary_stable(rows),
                                          admit_rank3_ac_stable(rows), admit_recursive_stable(rows),
                                          admit_complement_suffixes(rows)) if value is not None]
    unresolved_claims = []
    for source, data in component_data.items():
        for name, length, pointer in named_claims(data, rows):
            row = rows[name]
            if not claim_covered(row, length, pointer):
                unresolved_claims.append({'source': source, 'pointer': pointer, 'name': name,
                                          'claimed_length': length})
    if unresolved_claims:
        raise ValueError('Unvalidated component improvements; wire and verify their original-input certificates before publishing: '
                         + json.dumps(unresolved_claims[:20]))
    result_rows = list(rows.values())
    non_admitted_checks = check_unadapted_notes(result_rows)
    assert [r['name'] for r in result_rows] == IDS
    assert all(r['best_certified_length'] == sum(map(len, r['best_words'])) for r in result_rows)
    snapshot = datetime.now(timezone.utc).isoformat()
    session = json.loads((HERE / 'session.json').read_text())
    result = {'status': 'final_snapshot' if args.final else 'interim_pending_deadline',
        'snapshot_utc': snapshot, 'session_deadline_utc': session['deadline_utc'],
        'row_count': 124, 'archival_initial_length_sum': 2446, 'starting_best_length_sum': 2356,
        'best_certified_length_sum': sum(r['best_certified_length'] for r in result_rows),
        'best_rank2_length_sum': sum(r['best_rank2_length'] for r in result_rows),
        'best_any_rank_length_sum': sum(r['best_any_rank_length'] for r in result_rows),
        'new_gain_ids': [r['name'] for r in result_rows if r['gain_this_session']],
        'rank2_gain_ids': [r['name'] for r in result_rows if r['best_rank2_length'] < r['starting_best_length']],
        'solved_ordinary_ids': [r['name'] for r in result_rows if r['status'] == 'solved_ordinary'],
        'solved_stable_ids': [r['name'] for r in result_rows if r['status'] == 'solved_stable'],
        'unsolved_count': sum(r['status'] == 'unsolved' for r in result_rows),
        'rows': result_rows, 'component_snapshot_sha256': component_hashes, 'stable_adapters': stable_adapters,
        'non_admitted_component_checks': non_admitted_checks,
        'baseline_sources': inventory['sources'], 'builder_sha256': digest(Path(__file__)),
        'admission_policy': 'Saved-best start is included with its identity certificate. New ordinary gains require two exact replayers from that saved start. Stable prefixes require an independently replayed theorem-backed macro witness with pinned source/auditor hashes; expanded normal products are not required under the authorized finite-realizability theorem. Named U124 claims in all current JSON reports are checked against admitted certified minima; an uncovered numerical gain or solve aborts without replacing the table. Extra explicit components may be supplied with --extra-component.',
        'scope': 'Historical36 reductions (2446→2356) predate this session and are not new gains. Unsolved means no admitted solve in these bounded component records, not unreachable, nontrivial, or an exhaustive failure. The U124 retained bounded AC/Aut components are an upper bound, not124 proved distinct AC classes. Only independently verified stable prefixes are admitted; recognizer candidates alone are excluded. Every all-rank length sums all current relators, including defining relators.'}
    (HERE / 'u124_final_table.json').write_text(json.dumps(result, indent=2) + '\n')
    fields = ('name', 'archival_initial_length', 'starting_best_length', 'best_rank2_length', 'best_any_rank_length', 'best_certified_length', 'status',
              'best_rank', 'best_words', 'gain_this_session', 'certificate_kind', 'source_certificate_pointer',
              'best_rank2_words', 'best_rank2_certificate_kind', 'best_rank2_source_certificate_pointer')
    with (HERE / 'u124_final_table.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fields, extrasaction='ignore', lineterminator='\n')
        writer.writeheader()
        for row in result_rows:
            writer.writerow({**row, 'best_words': json.dumps(row['best_words'], separators=(',', ':')),
                             'best_rank2_words': json.dumps(row['best_rank2_words'], separators=(',', ':'))})
    lines = ['# U124 certified length table — ' + ('final snapshot' if args.final else 'interim'), '',
        f"Snapshot: {snapshot}. Session deadline: {session['deadline_utc']}. This table remains interim until the deadline snapshot is explicitly requested." if not args.final else f"Snapshot: {snapshot}.", '',
        f"All124 rows: **{len(result['solved_ordinary_ids'])} ordinary solves, {len(result['solved_stable_ids'])} stable solves, {result['unsolved_count']} unsolved**. Length totals: archival initial **2446**, saved starting best **2356**, current rank-two best **{result['best_rank2_length_sum']}**, current all-rank certified best **{result['best_any_rank_length_sum']}**. Session gains: **{len(result['new_gain_ids'])} shortened presentations**, **{2356 - result['best_certified_length_sum']} total letters**. The36 historical reductions are not credited to this session.", '',
        'Each row includes its saved starting state, so a method that produces longer endpoints cannot worsen the table. A new ordinary gain requires elementary replay; a stable gain requires independent exact replay of a theorem-backed prefix whose finite stable-AC realization is established. Expanded normal products are not required. All current relators are counted, including the helper defining relator. Recognition gates alone supply no admitted gains. Unsolved means no certified solve in the tested records; it makes no claim that untested states are unreachable.', '',
        'Rank2 best describes the rank of the endpoint. Its proof may use stable AC moves; the JSON and CSV retain the separate rank2 proof kind and source pointer. The Nielsen image tuple `(1,1,x,y)` is a generating-tuple marking, not a balanced presentation state or a solve. Only the verified projected relators and their ordinary suffix states are eligible for a length comparison.', '',
        'Source/certificate pointer S means `data/ms_unsolved_reps/aca_124_best.csv#name=<row>` with the empty identity certificate at that exact saved input. Any new witness receives its explicit component pointer in the JSON/CSV. Exact words and rank are shown below.', '',
        '| row | archival initial | starting best | rank2 best | any-rank best | status | best rank | exact best words | new gain | source/cert |',
        '|---|---:|---:|---:|---:|---|---:|---|---:|---|']
    for row in result_rows:
        pointer = 'S' if row['certificate_kind'] == 'identity_at_saved_start' else row['source_certificate_pointer']
        words = ', '.join('`' + word + '`' for word in row['best_words'])
        lines.append(f"| {row['name']} | {row['archival_initial_length']} | {row['starting_best_length']} | {row['best_rank2_length']} | {row['best_any_rank_length']} | {row['status']} | {row['best_rank']} | {words} | {row['gain_this_session']} | {pointer} |")
    lines += ['', 'Refresh from the original checkout with `.venv/bin/python .scratch/theory_3h_20260912/worktree/research/theory_patterns_20260912/u124_final_table.py`. The builder reads current reports, hashes the snapshot, checks all124 names, and refuses uncovered gain claims. Add `--final` only for the explicitly requested final snapshot.', '']
    (HERE / 'u124_final_table.md').write_text('\n'.join(lines))
    validate_table(result)
    print(json.dumps({k: v for k, v in result.items() if k not in ('rows', 'component_snapshot_sha256', 'baseline_sources', 'admission_policy', 'scope')}))


if __name__ == '__main__':
    main()
