"""Independent, search-free replay of saved one-helper dictionary prefixes."""
from __future__ import annotations

from collections import Counter
import copy
import csv
import hashlib
import json
from pathlib import Path
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LETTERS = {'x': 1, 'X': -1, 'y': 2, 'Y': -2, 'z': 3, 'Z': -3}
CHARACTERS = {v: k for k, v in LETTERS.items()}


def require(value, message):
    if not value:
        raise ValueError(message)


def integers(word, rank=3):
    require(isinstance(word, str), 'word must be a string')
    require(all(c in LETTERS and abs(LETTERS[c]) <= rank for c in word), 'word outside basis')
    return [LETTERS[c] for c in word]


def freely_reduced(word):
    values = integers(word)
    return all(a != -b for a, b in zip(values, values[1:]))


def inverse(word):
    return ''.join(CHARACTERS[-v] for v in reversed(integers(word)))


def verify_prefix(input_pair, witness):
    """Return a verified complete rank3 boundary, or raise ValueError.

    This checks literal expansions before any free reduction, so disjoint signed
    occurrences and the token-count length formula are independently certified.
    The stable-definition step uses the known-trivial-group lemma; no explicit
    normal-product realization is claimed by this API.
    """
    require(isinstance(input_pair, (list, tuple)) and len(input_pair) == 2, 'two source words required')
    for word in input_pair:
        integers(word, 2)
        require(freely_reduced(word), 'source word is not reduced')
    definition = witness['defining_word']
    integers(definition, 2)
    require(len(definition) >= 2 and freely_reduced(definition), 'invalid dictionary definition')
    compressed, cuts = witness['compressed_relators'], witness['cuts']
    require(len(compressed) == len(cuts) == 2, 'two tokenizations and cuts required')
    token_counts, literal_occurrences = [], []
    for source, template, cut in zip(input_pair, compressed, cuts):
        require(type(cut) is int and 0 <= cut < max(1, len(source)), 'invalid cyclic cut')
        integers(template)
        require(freely_reduced(template), 'compressed word not reduced')
        oriented = source[cut:] + source[:cut]
        chunks = [definition if c == 'z' else inverse(definition) if c == 'Z' else c for c in template]
        require(''.join(chunks) == oriented, 'literal expansion differs from rotated source')
        position, occurrences = 0, []
        for token, chunk in zip(template, chunks):
            if token in 'zZ':
                occurrences.append({'start': position, 'end': position + len(chunk), 'sign': 1 if token == 'z' else -1})
            position += len(chunk)
        token_counts.append(len(occurrences))
        literal_occurrences.append(occurrences)
    expected = ['Z' + definition, *compressed]
    require(witness['relators'] == expected, 'complete rank3 tuple differs from definition and templates')
    require(all(freely_reduced(word) for word in expected), 'complete tuple not freely reduced')
    require(type(witness['rank']) is int and witness['rank'] == 3, 'rank must be exactly three')
    total = sum(map(len, expected))
    require(type(witness['total_length']) is int and witness['total_length'] == total, 'incorrect all-relator length')
    source_length = sum(map(len, input_pair))
    count = sum(token_counts)
    formula = source_length + len(definition) + 1 - count * (len(definition) - 1)
    require(formula == total, 'literal token-count formula failed')
    return {'relators': expected, 'rank': 3, 'relator_lengths': list(map(len, expected)),
            'total_length': total, 'independently_verified': True,
            'defining_word': definition, 'cuts': list(cuts),
            'compressed_relators': list(compressed), 'token_counts': token_counts,
            'literal_occurrences': literal_occurrences, 'total_tokens': count,
            'formula_length': formula, 'input_length': source_length,
            'strict_gain': total < source_length,
            'certificate_kind': 'independently_verified_theorem_backed_stable_literal_prefix'}


def check_rejections(example):
    input_pair, witness = example
    bad = []
    item = copy.deepcopy(witness); item['total_length'] -= 1; bad.append(item)
    item = copy.deepcopy(witness); item['relators'] = item['relators'][1:]; bad.append(item)
    item = copy.deepcopy(witness); item['rank'] = 2; bad.append(item)
    item = copy.deepcopy(witness); item['cuts'][0] = True; bad.append(item)
    item = copy.deepcopy(witness); item['compressed_relators'][0] += 'x'; bad.append(item)
    item = copy.deepcopy(witness); item['defining_word'] = inverse(item['defining_word']); bad.append(item)
    for damaged in bad:
        try:
            verify_prefix(input_pair, damaged)
        except ValueError:
            continue
        raise AssertionError('corrupted witness was accepted')
    return len(bad)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    began_cpu, began_wall = time.process_time(), time.perf_counter()
    report_path = HERE / 'stable_dictionary_compression_report.json'
    source = json.loads(report_path.read_text())
    csv_path = ROOT / 'data/ms_unsolved_reps/aca_124_best.csv'
    csv_rows = list(csv.DictReader(csv_path.open()))
    author_path = HERE / 'stable_dictionary_compression.py'
    require(digest(csv_path) == source['source_sha256'], 'source CSV hash changed')
    require(digest(author_path) == source['script_sha256'], 'author script hash changed')
    require(len(source['rows']) == len(csv_rows) == 124, 'wrong full-panel cardinality')
    require(len({r['name'] for r in source['rows']}) == 124, 'duplicate row identifier')
    rows, gains, attempts, raw_cuts = [], [], [], 0
    example = None
    for index, (row, original) in enumerate(zip(source['rows'], csv_rows)):
        pair = [original['r1'], original['r2']]
        require(row['name'] == original['name'] and row['input'] == pair, 'exact input join failed')
        start = sum(map(len, pair))
        require(row['input_length'] == start, 'incorrect input length')
        count = row['candidate_definitions']
        require(type(count) is int and 0 <= count <= 1000, 'logged defining-word candidate budget invalid')
        attempts.append(count)
        raw_cuts += count * sum(max(1, len(w)) for w in pair)
        item = {'name': row['name'], 'input': pair, 'input_length': start,
                'candidate_definitions': count, 'minimum_rank3_total_length': None,
                'minimum_rank3_witness': None, 'all_rank_minimum_total_length': start,
                'all_rank_strict_gain': False, 'rank2_endpoint_minimum_length': start,
                'rank2_endpoint_strict_gain': False}
        if row['best'] is not None:
            verified = verify_prefix(pair, row['best'])
            require(verified['strict_gain'], 'saved positive is not a strict total-length gain')
            verified['json_pointer'] = f'/rows/{index}/best'
            item.update(minimum_rank3_total_length=verified['total_length'],
                        minimum_rank3_witness=verified,
                        all_rank_minimum_total_length=verified['total_length'], all_rank_strict_gain=True)
            gains.append(row['name'])
            if example is None:
                example = (pair, row['best'])
        require(row['best_length_including_start'] == item['all_rank_minimum_total_length'], 'row minimum mismatch')
        rows.append(item)
    require(gains == source['strict_stable_gain_ids'], 'saved gain ID list mismatch')
    total_start = sum(r['input_length'] for r in rows)
    total_end = sum(r['all_rank_minimum_total_length'] for r in rows)
    require(total_start == source['starting_total'] and total_end == source['best_total_including_start'], 'aggregate mismatch')
    require(sum(attempts) == source['candidate_definitions'] and max(attempts) == source['maximum_candidate_definitions_per_input'], 'candidate summary mismatch')
    rejected = check_rejections(example)
    result = {'status': 'pass', 'source_report_sha256': digest(report_path),
              'source_report': str(report_path), 'source_csv_sha256': digest(csv_path),
              'audit_script_sha256': digest(Path(__file__)), 'author_script_sha256': digest(author_path),
              'conventions_sha256': digest(HERE / 'STABLE_CERTIFICATE_CONVENTIONS.md'),
              'counts': {'rows': len(rows), 'positive_prefixes_independently_verified': len(gains),
                         'strict_stable_gain_rows': len(gains), 'rank2_endpoint_gain_rows': 0,
                         'starting_total': total_start, 'best_total_including_start': total_end,
                         'strict_total_reduction': total_start - total_end,
                         'corruption_cases_rejected': rejected,
                         'logged_candidate_definitions': sum(attempts),
                         'maximum_logged_candidate_definitions_per_input': max(attempts)},
              'strict_stable_gain_ids': gains, 'rank2_gain_ids': [], 'solved_ids': [], 'rows': rows,
              'replay_scope': 'All 84 saved positive prefixes replayed as literal signed disjoint replacements; all three rank3 relators are counted. No author verifier or enumerator imported or run.',
              'negative_scope': 'Rows without saved gains were checked for provenance and accounting only. No claim that arbitrary stable AC or hidden-cancellation compression cannot improve them.',
              'budget_scope': 'Logged work units are defining-word candidates (each entails two cyclic compression optimizations). They are not elementary AC counts, individual word-image evaluations, or dynamic-program transitions. The finite normal-product definition expansion is not emitted or charged.',
              'theorem_scope': 'Stable prefix validity uses known triviality of the input group and the established stable-definition lemma. Compression thereafter is exact ordinary donor-restored replacement. No rank2 endpoint or solution is asserted.',
              'cpu_seconds': time.process_time() - began_cpu,
              'wall_seconds': time.perf_counter() - began_wall}
    (HERE / 'stable_dictionary_independent_audit.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('rows', 'strict_stable_gain_ids')}, indent=2))


if __name__ == '__main__':
    main()
