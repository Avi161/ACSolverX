"""Stream saved ordinary-AC endpoints through a shared 1000-identification cap."""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import sys
import time

from .check_complement import HERE, ROSE, complement, independent_graph, sha256
from .ac_words import exponent, replay

sys.path.insert(0, str(HERE))
from check_ac_words import independent_replay


def determinant(pair):
    return (exponent(pair[0], 'x') * exponent(pair[1], 'y')
            - exponent(pair[0], 'y') * exponent(pair[1], 'x'))


def decompressed_sha256(path):
    digest = hashlib.sha256()
    with gzip.open(path, 'rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def candidates(boundary, prepared, hashes):
    original, unique = tuple(prepared['input']), {}
    assert boundary['input'] == prepared['input']

    def add(pair, moves, source, indices, pair_field, moves_field):
        key = tuple(pair)
        if key == original:
            return
        candidate = {'pair': list(pair), 'moves': moves,
                     'provenance': {'source': source, 'source_sha256': hashes[source],
                                    'name': prepared['name'], 'indices': indices,
                                    'pair_field': pair_field, 'moves_field': moves_field}}
        current = unique.get(key)
        if current is None or len(moves) < len(current['moves']):
            unique[key] = candidate

    for index, attempt in enumerate(boundary['attempts']):
        for pair_field, moves_field in [('final_pair', 'moves'), ('best_pair', 'best_moves')]:
            add(attempt[pair_field], attempt[moves_field], 'boundary_compiler_report.json',
                ['full_u124', 'records', boundary['_record_index'], 'attempts', index], pair_field, moves_field)
    for index, attempt in enumerate(prepared['attempts']):
        preparation = attempt['preparation']
        for pair_field, moves_field in [('final_pair', 'moves'), ('best_pair', 'best_moves')]:
            add(preparation[pair_field], preparation[moves_field], 'prepared_frames_full124.jsonl',
                ['attempts', index, 'preparation'], pair_field, moves_field)
        for theorem_index, theorem in enumerate(attempt['theorem_calls']):
            for pair_field, moves_field in [('final_pair', 'composed_moves'),
                                          ('best_pair', 'composed_best_moves')]:
                add(theorem[pair_field], theorem[moves_field], 'prepared_frames_full124.jsonl',
                    ['attempts', index, 'theorem_calls', theorem_index], pair_field, moves_field)
    return sorted(unique.values(), key=lambda c: (sum(map(len, c['pair'])), max(map(len, c['pair'])),
                                                 tuple(c['pair']), len(c['moves'])))


def screen_row(boundary, prepared, saved_root, hashes):
    started_wall, started_cpu = time.perf_counter(), time.process_time()
    original = prepared['input']
    assert saved_root['pair'] == original and abs(determinant(original)) == 1
    selected = candidates(boundary, prepared, hashes)
    root_graph = tuple(map(tuple, saved_root['graph']))
    cache = {root_graph: {'status': 'no_cyclic_complement', 'pairs_checked': 0, 'complete': True,
                          'cache_origin': 'independently audited literal input subgroup'}}
    tested, checks, positive = [], 0, None
    for candidate in selected:
        if checks >= 1000:
            break
        pair, moves = candidate['pair'], candidate['moves']
        assert independent_replay(original, moves) == pair
        assert replay(original, moves) == pair
        assert abs(determinant(pair)) == 1
        graph = independent_graph(pair)
        if graph in cache:
            result = dict(cache[graph])
            result['pairs_checked'] = 0
            reused = True
        else:
            result = complement(graph, 1000 - checks, shortest_first=True)
            cache[graph] = {**result, 'cache_origin': len(tested)}
            reused = False
        checks += result['pairs_checked']
        certificate_digest = hashlib.sha256(json.dumps(moves, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        state = {'pair': pair, 'total_length': sum(map(len, pair)),
                 'provenance': candidate['provenance'], 'prefix_elementary_moves': len(moves),
                 'prefix_sha256': certificate_digest, 'prefix_verified_by_two_replayers': True,
                 'determinant': determinant(pair), 'vertices': len({0} | {u for u, _, _ in graph}),
                 'graph_sha256': hashlib.sha256(json.dumps(graph).encode()).hexdigest(),
                 'reused_exact_graph': reused, **result}
        tested.append(state)
        if 'complement' in result:
            assert independent_graph([*pair, result['complement']]) == ROSE
            state['prefix_moves'] = moves
            state['joined_graph_is_full_rose'] = True
            positive = state
            print(json.dumps({'positive': prepared['name'], 'pair': pair,
                              'complement': result['complement'],
                              'claim': 'stable criterion witness pending full proof review'}), flush=True)
            break
    exhaustive = positive is not None or (len(tested) == len(selected) and all(s['complete'] for s in tested))
    return {'name': prepared['name'], 'input': original, 'input_determinant': determinant(original),
            'new_distinct_endpoint_count': len(selected), 'tested_state_count': len(tested),
            'untested_state_count': len(selected) - len(tested), 'merge_count': checks,
            'exact_graph_reuses': sum(s['reused_exact_graph'] for s in tested),
            'status': 'stable_criterion_witness_pending_full_proof_review' if positive else
                      ('no_complement_in_all_saved_endpoints' if exhaustive else 'unknown_capped'),
            'endpoint_portfolio_exhaustive': exhaustive, 'complement': positive.get('complement') if positive else None,
            'tested_states': tested, 'wall_seconds': time.perf_counter() - started_wall,
            'cpu_seconds': time.process_time() - started_cpu}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit', type=int, default=124)
    args = parser.parse_args()
    assert 1 <= args.limit <= 124
    started_wall, started_cpu = time.perf_counter(), time.process_time()
    boundary_path = HERE / 'boundary_compiler_report.json'
    prepared_path = HERE / 'prepared_frames_full124.jsonl.gz'
    source_paths = [boundary_path, prepared_path, HERE / 'cyclic_complement_u124.json',
                    HERE / 'complement_audit.json', HERE / 'check_complement.py', Path(__file__),
                    HERE / 'check_ac_words.py', HERE / 'ac_words.py']
    hashes = {p.name: sha256(p) for p in source_paths if p != prepared_path}
    hashes['prepared_frames_full124.jsonl'] = decompressed_sha256(prepared_path)
    boundary = {row['name']: {**row, '_record_index': index}
                for index, row in enumerate(json.loads(boundary_path.read_text())['full_u124']['records'])}
    saved_roots = {row['name']: row for row in json.loads((HERE / 'cyclic_complement_u124.json').read_text())['records']}
    audit = json.loads((HERE / 'complement_audit.json').read_text())
    assert audit['status'] == 'pass'
    assert audit['hashes']['cyclic_complement_u124.json'] == hashes['cyclic_complement_u124.json']
    rows, seen = [], set()
    with gzip.open(prepared_path, 'rt') as source, (HERE / 'complement_followup.jsonl').open('w') as output:
        for line_index, line in enumerate(source):
            if len(rows) == args.limit:
                break
            prepared = json.loads(line)
            name = prepared['name']
            assert name not in seen
            seen.add(name)
            row = screen_row(boundary[name], prepared, saved_roots[name], hashes)
            row['prepared_source_line_1based'] = line_index + 1
            row['prepared_source_line_sha256'] = hashlib.sha256(line.encode()).hexdigest()
            output.write(json.dumps(row, separators=(',', ':')) + '\n')
            output.flush()
            rows.append({k: v for k, v in row.items() if k != 'tested_states'})
            if len(rows) % 20 == 0 or row['complement'] is not None:
                print(json.dumps({'rows': len(rows), 'merges': sum(r['merge_count'] for r in rows),
                                  'positive_ids': [r['name'] for r in rows if r['complement'] is not None]}), flush=True)
            time.sleep(0.1)
    assert len(rows) == args.limit
    if args.limit == 124:
        assert seen == set(boundary) == set(saved_roots)
    summary = {'status': 'complete', 'algorithm': 'independent explicit-set-partition fold and finite vertex identification',
               'source_hashes': hashes, 'row_count': len(rows), 'per_input_merge_cap': 1000,
               'selection': 'Saved boundary final/best, preparation final/best and prepared theorem final/best endpoints; exact pair dedup; shortest total length first, then maximum length and literal pair. For duplicate endpoints choose the shortest saved prefix. Vertex pairs are ordered by induced reduced complement length.',
               'graph_dedup': 'Reuse exact canonically rooted labelled graph only, including independently audited roots; no AC/Aut canonicalization.',
               'verification': 'Only chosen endpoint prefixes replayed with two word-level replayers; no re-execution of compilers or replay of the complete 252 MB artifact.',
               'negative_scope': 'Negative decisions apply only to tested literal subgroups. Unknown capped rows leave graph identifications or saved endpoints unchecked. No group nontriviality or stable obstruction is asserted.',
               'positive_claim': 'Any graph witness is a stable criterion witness pending full proof review; never an automatic ordinary solve.',
               'positive_ids': [r['name'] for r in rows if r['complement'] is not None],
               'counts': dict(Counter(r['status'] for r in rows)),
               'tested_state_count': sum(r['tested_state_count'] for r in rows),
               'new_distinct_endpoint_count': sum(r['new_distinct_endpoint_count'] for r in rows),
               'merge_count': sum(r['merge_count'] for r in rows),
               'exact_graph_reuses': sum(r['exact_graph_reuses'] for r in rows),
               'heap_nodes': 0, 'cooldown_seconds_per_row': 0.1,
               'row_search_wall_seconds': sum(r['wall_seconds'] for r in rows),
               'row_search_cpu_seconds': sum(r['cpu_seconds'] for r in rows),
               'wall_seconds_including_stream_hashes_and_cooling': time.perf_counter() - started_wall,
               'cpu_seconds_including_stream_hashes': time.process_time() - started_cpu,
               'rows': rows}
    (HERE / 'complement_followup.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({k: summary[k] for k in ['row_count', 'counts', 'positive_ids', 'tested_state_count',
          'new_distinct_endpoint_count', 'merge_count', 'exact_graph_reuses', 'row_search_wall_seconds',
          'row_search_cpu_seconds', 'wall_seconds_including_stream_hashes_and_cooling']}), flush=True)


if __name__ == '__main__':
    main()
