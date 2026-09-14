"""Replay recursive literal-compression witnesses and screen frozen audited seeds."""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
import recursive_stable_compression as subject

HERE = Path(__file__).resolve().parent
PREFLIGHT = ('aca_13', 'aca_59', 'aca_96')
ALPHABET = 'xXyYzZuUvVwW'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def inverse(word):
    return ''.join(c.upper() if c.islower() else c.lower() for c in reversed(word))


def reduce_word(word):
    need(isinstance(word, str) and all(c in ALPHABET for c in word), 'invalid word')
    while True:
        previous = word
        for letter in 'xyzuvw':
            word = word.replace(letter + letter.upper(), '').replace(letter.upper() + letter, '')
        if word == previous:
            return word


def replay(words, basis, moves):
    words = list(words)
    for move in moves:
        target = move['target']
        need(type(target) is int and 1 <= target <= len(words), 'invalid target')
        i = target - 1
        if move['op'] == 'invert':
            words[i] = inverse(words[i])
        elif move['op'] == 'multiply':
            source = move['source']
            need(type(source) is int and 1 <= source <= len(words) and source != target, 'invalid donor')
            words[i] = reduce_word(words[i] + words[source - 1])
        elif move['op'] == 'conjugate':
            letter = move['by']
            need(isinstance(letter, str) and len(letter) == 1 and letter.lower() in basis, 'invalid conjugator')
            words[i] = reduce_word(inverse(letter) + words[i] + letter)
        else:
            raise ValueError('nonordinary operation in suffix')
    return words


def state(label, words, basis):
    need(len(words) == len(basis), 'unbalanced boundary')
    need(all(reduce_word(w) == w and all(c.lower() in basis for c in w) for w in words), 'boundary alphabet/reduction')
    return {'label': label, 'basis': list(basis), 'rank': len(basis), 'relators': list(words),
            'relator_lengths': list(map(len, words)), 'total_length': sum(map(len, words))}


def verify_compression(words, basis, witness):
    helper, defining = witness['helper'], witness['defining_word']
    need(helper in 'xyzuvw' and helper not in basis, 'helper is not fresh')
    need(len(defining) >= 2 and all(c.lower() in basis for c in defining), 'definition not an old word')
    need(reduce_word(defining) == defining, 'definition not reduced')
    compressed, cuts = witness['compressed_relators'], witness['cuts']
    need(len(compressed) == len(cuts) == len(words), 'one compression per current relator required')
    tokens, oriented = [], []
    for index, (word, template, cut) in enumerate(zip(words, compressed, cuts)):
        need(type(cut) is int and 0 <= cut < max(1, len(word)), 'invalid cyclic cut')
        need(witness['rotation_conjugators'][index] == word[:cut], 'rotation witness mismatch')
        target = word[cut:] + word[:cut]
        need(reduce_word(inverse(word[:cut]) + word + word[:cut]) == target, 'rotation does not replay')
        expanded = ''.join(defining if c == helper else inverse(defining) if c == helper.upper() else c for c in template)
        need(expanded == target, 'literal compression expansion mismatch')
        tokens.append(sum(c.lower() == helper for c in template))
        oriented.append(target)
    after, new_basis = [helper.upper() + defining, *compressed], [*basis, helper]
    length = sum(map(len, after))
    formula = sum(map(len, words)) + len(defining) + 1 - sum(tokens) * (len(defining) - 1)
    need(witness['relators'] == after and witness['basis_before'] == list(basis)
         and witness['basis_after'] == new_basis, 'complete new tuple/basis mismatch')
    need(witness['rank'] == len(after) == len(new_basis), 'new rank mismatch')
    need(witness['token_counts'] == tokens and witness['formula_length'] == formula == length == witness['total_length'], 'all-relator token-count formula mismatch')
    need(length < sum(map(len, words)), 'accepted compression is not a strict gain')
    return after, new_basis, [state('cyclic_orientations', oriented, basis),
        state('defining_relator_added', [helper.upper() + defining, *oriented], new_basis),
        state('literal_compression', after, new_basis)]


def verify_deletion(words, basis, record):
    need(record['before'] == words and record['basis_before'] == basis, 'deletion source mismatch')
    index, axis = record['source_index'], record['generator']
    need(type(index) is int and 0 <= index < len(words) and words[index].lower() == axis and len(words[index]) == 1, 'not a literal singleton')
    after = replay(words, basis, record['ordinary_moves'])
    need(after == record['after_substitutions'] and after[index] == axis, 'singleton substitutions do not replay')
    need(all(axis not in word.lower() for j, word in enumerate(after) if j != index), 'generator survives outside singleton')
    need(record['destabilization'] == {'generator': axis, 'relator_index': index}, 'destabilization target mismatch')
    remaining = after[:index] + after[index + 1:]
    new_basis = [g for g in basis if g != axis]
    need(remaining == record['after_deletion'] and new_basis == record['basis_after'], 'deletion tuple mismatch')
    cleaned = replay(remaining, new_basis, record['cyclic_cleanup_moves'])
    need(cleaned == record['after'], 'cyclic cleanup does not replay')
    need(sum(map(len, cleaned)) < sum(map(len, words)), 'singleton deletion not a strict gain')
    return cleaned, new_basis, [state('singleton_substitutions', after, basis),
        state('strict_destabilization', remaining, new_basis), state('cyclic_cleanup', cleaned, new_basis)]


def verify_result(result):
    current, basis = list(result['input']), list(result['input_basis'])
    expected = [state('audited_seed', current, basis)]
    rounds, deletions, charged = 0, 0, 0
    for event in result['events']:
        if event['kind'] == 'compression_round':
            need(event['index'] == rounds, 'round order mismatch')
            record = result['rounds'][rounds]
            rounds += 1
            need(record['before'] == current and record['basis_before'] == basis, 'compression chain mismatch')
            charged += record['defining_word_candidates']
            need(0 <= record['defining_word_candidates'] <= record['definitions_generated'], 'candidate accounting')
            need(record['definition_screen_complete'] == (record['defining_word_candidates'] == record['definitions_generated']), 'screen completeness flag')
            if record['best'] is not None:
                current, basis, states = verify_compression(current, basis, record['best'])
                expected.extend(states)
        elif event['kind'] == 'singleton_deletion':
            need(event['index'] == deletions, 'deletion order mismatch')
            current, basis, states = verify_deletion(current, basis, result['singleton_deletions'][deletions])
            deletions += 1
            expected.extend(states)
        else:
            raise ValueError('unknown event')
    need(rounds == len(result['rounds']) and deletions == len(result['singleton_deletions']), 'events omit a transformation')
    need(expected == result['boundaries'], 'stored boundaries omitted or changed a relator')
    need(current == result['final_relators'] and basis == result['final_basis'], 'final tuple mismatch')
    need(result['final_rank'] == len(current) == len(basis) <= result['rank_limit'] <= 6, 'rank bound')
    need(result['final_length'] == sum(map(len, current)), 'final length mismatch')
    need(result['input_length'] == sum(map(len, result['input'])), 'initial length mismatch')
    need(result['additional_length_gain'] == result['input_length'] - result['final_length'], 'gain mismatch')
    need(charged == result['defining_word_candidates'] <= result['candidate_limit'] <= 1000, 'shared candidate budget')
    need(result['solved'] is False, 'automatic solution claim prohibited')
    return True


def planted_checks():
    examples = []
    for words, basis in ((['xxxxxxxxxxxxy', 'xxxxxxxxxxxxxy', 'z'], ['x', 'y', 'z']),
                         (['u', 'UUxy', 'Yz', 'Zx'], ['x', 'y', 'z', 'u'])):
        result = subject.run(words, basis=basis)
        verify_result(result)
        examples.append(result)
    need(any(r['singleton_deletions'] for r in examples), 'singleton path not exercised')
    need(any(a['best'] for r in examples for a in r['rounds']), 'dictionary path not exercised')
    sample = next(r for r in examples if any(a['best'] for a in r['rounds']))
    bad = deepcopy(sample)
    next(a['best'] for a in bad['rounds'] if a['best'])['total_length'] -= 1
    try:
        verify_result(bad)
    except ValueError:
        pass
    else:
        raise AssertionError('omitted-length corruption accepted')
    for limit in (0, 1, 5, 20):
        result = subject.run(['xxxxxxxxxxxxy', 'xxxxxxxxxxxxxy', 'z'], candidate_limit=limit)
        verify_result(result)
    return {'planted_paths': len(examples), 'tiny_candidate_budgets': 4,
            'corrupted_total_rejected': True}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_checker(name):
    specification = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def verify_seed(row):
    witness = row['certificate_witness']
    for filekey, hashkey in (('audit_file', 'audit_sha256'), ('source_file', 'source_sha256'), ('auditor_file', 'auditor_sha256')):
        need(sha(HERE / witness[filekey]) == witness[hashkey], 'audited seed provenance changed')
    source = json.loads((HERE / witness['source_file']).read_text())
    checker = load_checker(Path(witness['auditor_file']).stem)
    parts = witness['json_pointer'].strip('/').split('/')
    value = source
    for part in parts:
        value = value[int(part)] if isinstance(value, list) else value[part]
    if witness['source_file'] == 'primitive_compression_report.json':
        attempt = source['rows'][int(parts[1])]['attempts'][int(parts[3])]
        need(attempt['input'] == row['starting_words'], 'primitive seed source differs')
        checked = checker.verify_prefix(attempt, witness['boundary_index'])
    elif witness['source_file'] == 'stable_dictionary_compression_report.json':
        checked = checker.verify_prefix(row['starting_words'], value)
    else:
        raise ValueError('unsupported seed proof family')
    need(checked['relators'] == row['best_words'] and checked['total_length'] == row['best_any_rank_length'], 'seed tuple does not replay')


def summarize(records):
    return {'rows': len(records), 'additional_gain_ids': [r['name'] for r in records if r['additional_length_gain']],
        'input_total': sum(r['input_length'] for r in records), 'final_total': sum(r['final_length'] for r in records),
        'additional_total_reduction': sum(r['additional_length_gain'] for r in records),
        'defining_word_candidates': sum(r['defining_word_candidates'] for r in records),
        'maximum_candidates_per_input': max(r['defining_word_candidates'] for r in records),
        'maximum_recorded_rank': max(b['rank'] for r in records for b in r['boundaries']),
        'accepted_compressions': sum(a['best'] is not None for r in records for a in r['rounds']),
        'singleton_deletions': sum(len(r['singleton_deletions']) for r in records),
        'cpu_seconds': sum(r['cpu_seconds'] for r in records),
        'wall_seconds': sum(r['wall_seconds'] for r in records),
        'cooldown_seconds': sum(r['cooldown_seconds'] for r in records)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--full', action='store_true')
    parser.add_argument('--cooldown-seconds', type=float, default=0.05)
    args = parser.parse_args()
    need(0 <= args.cooldown_seconds <= 60, 'invalid cooldown')
    start_cpu, start_wall = time.process_time(), time.perf_counter()
    planted = planted_checks()
    output = HERE / 'recursive_stable_compression_report.json'
    previous = json.loads(output.read_text()) if args.full and output.exists() else None
    if previous is not None:
        need(previous['module_sha256'] == sha(Path(subject.__file__)), 'module changed after preflight')
        source_text = previous['source_table_text']
        reuse = {r['name']: r for r in previous['records']}
    else:
        source_text = (HERE / 'u124_final_table.json').read_text()
        reuse = {}
    table = json.loads(source_text)
    seeds = [r for r in table['rows'] if r['gain_this_session'] > 0]
    need(len(seeds) == 85 and all(r['best_rank'] == 3 for r in seeds), 'expected exact85 audited rank3 keepers')
    need({r['name'] for r in seeds} == set(table['new_gain_ids']), 'keeper ID mismatch')
    selected = seeds if args.full else [next(r for r in seeds if r['name'] == name) for name in PREFLIGHT]
    records = []
    for row in selected:
        name = row['name']
        if name in reuse:
            record = reuse[name]
            need(record['input'] == row['best_words'], 'reused preflight input mismatch')
        else:
            verify_seed(row)
            record = subject.run(row['best_words'])
            verify_result(record)
            record.update({'name': name, 'source_keeper': row,
                           'source_table_sha256': hashlib.sha256(source_text.encode()).hexdigest()})
            cooldown = time.perf_counter()
            time.sleep(args.cooldown_seconds)
            record['cooldown_seconds'] = time.perf_counter() - cooldown
        records.append(record)
    report = {'status': 'full85_author_verified_pending_independent_audit' if args.full else 'preflight3_author_verified',
        'records': records, 'summary': summarize(records), 'planted_checks': planted,
        'reused_rows': len(set(reuse) & {r['name'] for r in records}),
        'source_table_text': source_text, 'source_table_sha256': hashlib.sha256(source_text.encode()).hexdigest(),
        'module_sha256': sha(Path(subject.__file__)), 'checks_sha256': sha(Path(__file__)),
        'conventions_sha256': sha(HERE / 'STABLE_CERTIFICATE_CONVENTIONS.md'),
        'wall_seconds_including_seed_replay_checks_and_cooling': time.perf_counter() - start_wall,
        'cpu_seconds_including_seed_replay_checks': time.process_time() - start_cpu,
        'solved_ids': [], 'scope': 'Additional greedy literal compression from85 audited keepers only, not a rerun of the original rank3 screen. All relators are retained and charged in length. At most1000 additional defining-word candidates per row and rank6. Exact candidate work is distinct from ordinary suffix moves and unexpanded normal-product definition realizations. No heap or automatic solution claims. Independent audit required before aggregate admission.'}
    output.write_text(json.dumps(report, indent=2) + '\n')
    summary = report['summary']
    lines = ['# Recursive stable dictionary compression', '',
        f"Status: **{report['status']}**. {summary['rows']} audited starting tuples; {len(summary['additional_gain_ids'])} further shortening candidates. Input length {summary['input_total']}→{summary['final_total']}. No solution claims.", '',
        report['scope'], '',
        'For each fresh helper h and old word w, exact disjoint signed tokenizations of every current relator give L′=L+|w|+1−M(|w|−1). The greedy step chooses the least total length among evaluated definitions and accepts only a strict decrease. Every cyclic cut has its prefix conjugation witness, and the new defining relator H w stays in the tuple. Literal singleton cleanup emits ordinary donor-restored substitution moves before an explicitly checked strict generator-relator deletion. It then records ordinary cyclic cleanup. All macro boundaries, including the temporary larger defining-relator state, are retained.', '',
        f"Defining-word candidates: {summary['defining_word_candidates']}; maximum per input {summary['maximum_candidates_per_input']}; accepted compressions {summary['accepted_compressions']}; singleton deletions {summary['singleton_deletions']}; maximum recorded rank {summary['maximum_recorded_rank']}. Algorithm CPU {summary['cpu_seconds']:.6f}s; measured cooldown {summary['cooldown_seconds']:.6f}s. The full pass reuses the three preflight records.", '',
        '| row | audited seed length | candidate final length | final rank | extra reduction | candidates | stop |',
        '|---|---:|---:|---:|---:|---:|---|']
    for r in records:
        lines.append(f"| {r['name']} | {r['input_length']} | {r['final_length']} | {r['final_rank']} | {r['additional_length_gain']} | {r['defining_word_candidates']} | {r['stop_reason']} |")
    (HERE / 'recursive_stable_compression_report.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k not in ('records', 'source_table_text', 'scope')}))


if __name__ == '__main__':
    main()
