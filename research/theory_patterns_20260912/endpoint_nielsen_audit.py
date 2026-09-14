"""Read-only independent audit of saved endpoint Nielsen paths and gate ledgers."""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
from check_ac_words import canonical, inverse, reduce_word

HERE = Path(__file__).resolve().parent


def image(word, images):
    mapping = {'x': images[0], 'X': inverse(images[0]), 'y': images[1], 'Y': inverse(images[1])}
    return reduce_word(''.join(mapping[c] for c in word))


def canonical_pair(pair):
    return sorted(canonical(word) for word in pair)


def main():
    wall, cpu = time.perf_counter(), time.process_time()
    source = (HERE / 'endpoint_nielsen.py').read_bytes()
    assignments = {}
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in ('MAPS', 'INVERSES'):
                    assignments[target.id] = ast.literal_eval(node.value)
    maps, inverses = assignments['MAPS'], assignments['INVERSES']
    assert len(maps) == len(inverses) == 8
    checks = 0
    for index, images in enumerate(maps):
        opposite = maps[inverses[index]]
        for word in ('x', 'y', 'xyXY', 'xYXYxyy', ''):
            assert image(image(word, images), opposite) == reduce_word(word)
            assert image(image(word, opposite), images) == reduce_word(word)
            checks += 2
    summary = json.loads((HERE / 'endpoint_nielsen.json').read_text())
    assert summary['source_hashes']['endpoint_nielsen.py'] == hashlib.sha256(source).hexdigest()
    digest = hashlib.sha256()
    records = []
    states, steps, evaluations = 0, 0, 0
    row_pairs, global_pairs = {}, set()
    with (HERE / 'endpoint_nielsen.jsonl').open('rb') as stream:
        for raw in stream:
            digest.update(raw)
            row = json.loads(raw)
            originals = canonical_pair(row['input'])
            state_evaluations = 0
            pairs = set()
            for state in row['states']:
                current = canonical_pair(state['pair'])
                assert current == state['canonical_pair']
                for step in state['trace']:
                    index = step['map']
                    assert type(index) is int and 0 <= index < 8
                    assert step['images'] == list(maps[index])
                    assert step['inverse_images'] == list(maps[inverses[index]])
                    assert step['before'] == current
                    child = canonical_pair(image(word, maps[index]) for word in current)
                    assert step['after'] == child
                    assert sum(map(len, child)) < sum(map(len, current))
                    current = child
                    steps += 1
                assert current == state['best_pair']
                assert sum(map(len, current)) == state['best_length']
                assert state['image_evaluations'] == 8 * (len(state['trace']) + int(state['strict_descent_exhausted']))
                state_evaluations += state['image_evaluations']
                pairs.add(tuple(current))
                states += 1
            assert state_evaluations == row['image_evaluations'] <= 1000
            assert len(row['states']) == row['normalized_candidate_count']
            assert row['best_length'] == min([sum(map(len, originals))] + [s['best_length'] for s in row['states']])
            assert row['best_length'] == sum(map(len, row['best_pair']))
            assert row['input_length'] == sum(map(len, row['input']))
            evaluations += state_evaluations
            records.append(row)
            row_pairs[row['name']] = pairs
            global_pairs.update(pairs)
    assert len(records) == len({r['name'] for r in records}) == 124
    assert {r['name'] for r in records} == {'aca_' + str(i) for i in range(124)}
    assert states == summary['normalized_candidate_count']
    assert steps == summary['descent_steps']
    assert evaluations == summary['image_evaluations']
    assert summary['improved'] == [r['name'] for r in records if r['best_length'] < r['input_length']]
    assert summary['solved'] == [r['name'] for r in records if r['best_length'] == 2]
    by_name = {r['name']: r for r in records}
    for row in summary['rows']:
        assert all(by_name[row['name']][key] == value for key, value in row.items())
    gates_raw = (HERE / 'endpoint_gates.json').read_bytes()
    gates = json.loads(gates_raw)
    assert gates['source_sha256'] == digest.hexdigest()
    assert gates['script_sha256'] == hashlib.sha256((HERE / 'endpoint_gates.py').read_bytes()).hexdigest()
    terminal_ids = []
    bs_charges, endpoint_rows = 0, 0
    for row in gates['rows']:
        assert row['distinct_pairs_checked'] == len(row_pairs[row['name']])
        assert 0 <= row['bs_charges'] <= 1000
        bs_charges += row['bs_charges']
        endpoint_rows += row['distinct_pairs_checked']
        if any(any(k in match['hits'] for k in ('primitive', 'two_block', 'stable_power_Q', 'consecutive_bs_solved'))
               or any(hit['terminal'] for hit in match['hits'].get('ms_residue', [])) for match in row['matches']):
            terminal_ids.append(row['name'])
    assert len(gates['rows']) == len({r['name'] for r in gates['rows']}) == 124
    assert terminal_ids == gates['terminal_candidate_ids'] == []
    assert endpoint_rows == gates['counts']['endpoint_rows']
    assert bs_charges == gates['counts']['bs_charges']
    assert len(global_pairs) == gates['globally_distinct_pairs']
    audit = {'status': 'pass', 'rows': 124, 'map_inverse_word_checks': checks,
        'states': states, 'strict_descent_steps': steps, 'image_evaluations': evaluations,
        'maximum_image_evaluations_per_input': max(r['image_evaluations'] for r in records),
        'improved_ids': summary['improved'], 'solved_ids': summary['solved'],
        'gate_ledger': {'endpoint_rows': endpoint_rows, 'globally_distinct_pairs': len(global_pairs),
                        'bs_charges': bs_charges, 'terminal_candidate_ids': terminal_ids,
                        'recorded_bs_matches': gates['counts']['consecutive_bs_matches'],
                        'recorded_bs_stalled': gates['counts']['consecutive_bs_normal_form_stalled'],
                        'bs_match_count_verification': 'Recorded summary values only; individual negative BS gate calls are not stored and were not rerun.'},
        'source_hashes': {'endpoint_nielsen.py': hashlib.sha256(source).hexdigest(),
                          'endpoint_nielsen.json': hashlib.sha256((HERE / 'endpoint_nielsen.json').read_bytes()).hexdigest(),
                          'endpoint_nielsen.jsonl': digest.hexdigest(),
                          'endpoint_gates.json': hashlib.sha256(gates_raw).hexdigest()},
        'cpu_seconds': time.process_time() - cpu, 'wall_seconds': time.perf_counter() - wall,
        'scope': 'Independent word-image/canonicalization replay of every stored trace; inverse identities, strict descent and recorded budget arithmetic. No endpoint descent or terminal gate is rerun. The maximality of exhausted descents is not independently retested. Ambient maps are not ordinary AC certificates.'}
    (HERE / 'endpoint_nielsen_audit.json').write_text(json.dumps(audit, indent=2) + '\n')
    (HERE / 'endpoint_nielsen_audit.md').write_text(
        '# Endpoint Nielsen audit\n\n'
        f"Pass:124 rows, {states} stored states, {steps} strictly decreasing map steps and {evaluations} image evaluations; maximum {audit['maximum_image_evaluations_per_input']} per input. All eight maps and listed inverses compose to the identity in both orders. Every stored image and canonical pair was checked with independent word routines.\n\n"
        'No row improves its saved starting length or solves. These explicit ambient-map traces do not supply ordinary AC certificates. No endpoints or gates were rerun.\n\n'
        f"The gate ledger confirms {endpoint_rows} endpoint rows, {len(global_pairs)} globally distinct pairs, {bs_charges} summed BS charges and zero terminal candidates. The362 BS matches/stalls are recorded summary counts; individual negative calls are absent from the ledger, so those two counts were not independently recomputed.\n\n"
        f"Runtime: {audit['cpu_seconds']:.6f}s CPU / {audit['wall_seconds']:.6f}s wall. Source hashes and scope limits are in `endpoint_nielsen_audit.json`.\n")
    print(json.dumps(audit))


if __name__ == '__main__':
    main()
