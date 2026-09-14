"""Test retained triangular expansions on a frozen hard-but-solved AC19 panel."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys
import time


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
U124 = ROOT / 'research/u124_rank_3h_20260912'
HIGH_RANK = ROOT / 'research/u124_high_rank_ac_20260912'
PRIOR = ROOT / 'research/rank_unbounded_20260912'
sys.path[:0] = [str(ROOT), str(HIGH_RANK), str(U124), str(PRIOR)]

from experiments.search.greedy_baseline import moves_to_states, str_to_move
import high_rank_ac_search as fixed_engine
import high_rank_ac_search_v2 as fixed_search
from high_rank_triangles import excess, triangulate
import theory_short_relators
import verify


PANEL = HERE / 'hard_solved_panel.jsonl'
AC19 = ROOT / 'data/AC19_extended_aut_min.csv'
PANEL_SHA256 = '667e4d19474755a779e6fc0ec8554d1353535df497c7e670a6c54a37131d742f'
AC19_SHA256 = '7e220253bd0d950378d6ca6944be46ff4b77e49f30067b9ff6c6c6da82f64ae2'
S20_NODES = {
    'ac19_15866': 17369,
    'ac19_25244': 21637,
    'ac19_44158': 23977,
    'ac19_66724': 37682,
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def parse_word(value):
    labels = {'x': 1, 'y': 2}
    return tuple(labels[c.lower()] * (1 if c.islower() else -1) for c in value)


def tuple_words(value):
    return tuple(tuple(word) for word in value)


def generators(value):
    return {abs(letter) for word in tuple_words(value) for letter in word}


def load_panel():
    if sha(PANEL) != PANEL_SHA256 or sha(AC19) != AC19_SHA256:
        raise AssertionError('frozen panel or AC19 census changed')
    with AC19.open(newline='') as stream:
        census = {row['name']: row for row in csv.DictReader(stream)}
    rows = [json.loads(line) for line in PANEL.read_text().splitlines()]
    if len(rows) != 4 or len({row['name'] for row in rows}) != 4:
        raise AssertionError('panel denominator or IDs changed')
    if {row['name'] for row in rows} != set(S20_NODES):
        raise AssertionError('panel membership changed')
    for row in rows:
        name = row['name']
        if [census[name]['r1'], census[name]['r2']] != [row['r1'], row['r2']]:
            raise AssertionError(name + ': census words changed')
        moves = [str_to_move(move) for move in row['path_moves']]
        states = moves_to_states(row['r1'], row['r2'], moves)
        if states != row['path'] or states[-1] != ['Y', 'X']:
            raise AssertionError(name + ': saved rank-two certificate failed')
    return rows


def replay_expansion(initial, events):
    current = tuple_words(initial)
    for event in events:
        if event['kind'] != 'defining_compression':
            raise AssertionError('expansion used an unexpected event')
        if tuple_words(event['before']) != current:
            raise AssertionError('expansion path discontinuity')
        current = verify.verify_event(event, known_trivial=True)
    return current


def replay_fixed(initial, events):
    current = tuple_words(initial)
    rank = len(current)
    declared = generators(current)
    if declared != set(range(1, rank + 1)):
        raise AssertionError('expanded presentation does not use its declared basis')
    for event in events:
        if event['kind'] != 'normal_product_substitution':
            raise AssertionError('fixed-rank suffix used another operation')
        if tuple_words(event['before']) != current:
            raise AssertionError('fixed-rank path discontinuity')
        current = verify.verify_event(event, known_trivial=False)
        if len(current) != rank or generators(current) != declared:
            raise AssertionError('fixed-rank path changed rank or declared basis')
    return current


def phase(initial, *, pops, cap, beam, neighborhood):
    cpu, wall = time.process_time(), time.perf_counter()
    audited_verifier = fixed_engine.verify.verify_event

    def constructor_checked_endpoint(event, *, known_trivial=False):
        if event['kind'] != 'normal_product_substitution':
            raise AssertionError('search generator emitted another operation')
        return tuple_words(event['after'])

    fixed_engine.verify.verify_event = constructor_checked_endpoint
    try:
        result = fixed_search.search_row(
            initial, pop_budget=pops, relator_cap=cap, beam=beam,
            neighborhood=neighborhood)
    finally:
        fixed_engine.verify.verify_event = audited_verifier
    result['cpu_seconds'] = time.process_time() - cpu
    result['wall_seconds'] = time.perf_counter() - wall
    if replay_fixed(initial, result['events']) != tuple_words(result['endpoint']):
        raise AssertionError('reported endpoint differs from replay')
    if replay_fixed(initial, result['best_fixed_events']) != tuple_words(result['best_fixed_endpoint']):
        raise AssertionError('reported best endpoint differs from replay')
    result['queue_exhausted_without_beam_loss'] = (
        result['heap_pops'] < result['pop_budget']
        and result['heap_pops'] == result['discovered_states'])
    return result


def terminal_compile(endpoint):
    endpoint = tuple_words(endpoint)
    if not all(len(word) <= 2 for word in endpoint):
        return None
    compiled = theory_short_relators.trivialize(
        endpoint, generators=range(1, len(endpoint) + 1))
    if not compiled['trivial']:
        raise AssertionError('known-trivial short endpoint has a C2 quotient')
    replayed = theory_short_relators.replay(endpoint, compiled['moves'])
    if replayed != tuple(compiled['endpoint']):
        raise AssertionError('terminal compiler replay failed')
    if sorted(replayed) != [(g,) for g in range(1, len(endpoint) + 1)]:
        raise AssertionError('terminal compiler did not reach the retained basis')
    return compiled


def run_row(source, args):
    original = fixed_engine.search.normalize(
        (parse_word(source['r1']), parse_word(source['r2'])))
    cpu, wall = time.process_time(), time.perf_counter()
    expanded, expansion_events, expansion_units = triangulate(
        original, budget=args.expansion_budget)
    expansion_cpu = time.process_time() - cpu
    expansion_wall = time.perf_counter() - wall
    if excess(expanded):
        raise AssertionError(source['name'] + ': triangularization incomplete')
    if replay_expansion(original, expansion_events) != expanded:
        raise AssertionError(source['name'] + ': expansion replay failed')

    macro = phase(expanded, pops=args.macro_pops, cap=4, beam=args.macro_beam,
                  neighborhood='short_macros')
    if macro['solved_to_length_at_most_two']:
        endpoint = tuple_words(macro['endpoint'])
        suffix = list(macro['events'])
        deep = None
    else:
        seed = tuple_words(macro['best_fixed_endpoint'])
        deep = phase(seed, pops=args.deep_pops, cap=args.deep_cap,
                     beam=args.deep_beam, neighborhood='quartic')
        endpoint = tuple_words(deep['endpoint'])
        suffix = list(macro['best_fixed_events']) + list(deep['events'])
        if replay_fixed(expanded, suffix) != endpoint:
            raise AssertionError(source['name'] + ': combined suffix failed')

    compiled = terminal_compile(endpoint)
    solved = compiled is not None
    return {
        'name': source['name'],
        'original': original,
        'original_lengths': list(map(len, original)),
        'known_rank2': {
            'greedy_nodes': source['nodes_explored'],
            'greedy_path_length': source['path_length'],
            'greedy_budget': source['budget'],
            's20_mk2_nodes': S20_NODES[source['name']],
            'saved_greedy_certificate_replayed': True,
        },
        'expansion': {
            'endpoint': expanded,
            'events': expansion_events,
            'charged_units': expansion_units,
            'cpu_seconds': expansion_cpu,
            'wall_seconds': expansion_wall,
            'rank': len(expanded),
            'total_length': sum(map(len, expanded)),
            'maximum_relator_length': max(map(len, expanded)),
        },
        'macro': macro,
        'deep': deep,
        'combined_search_events': suffix,
        'endpoint': endpoint,
        'solved_at_retained_rank': solved,
        'terminal_compiler': compiled,
        'retained_rank': len(expanded),
        'rank_preserved_after_expansion': len(endpoint) == len(expanded),
        'minimum_relator_length_reached': min(map(len, endpoint)),
        'maximum_relator_length_at_endpoint': max(map(len, endpoint)),
        'triangles_at_endpoint': sum(len(word) == 3 for word in endpoint),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--macro-pops', type=int, default=100)
    parser.add_argument('--macro-beam', type=int, default=128)
    parser.add_argument('--deep-pops', type=int, default=500)
    parser.add_argument('--deep-cap', type=int, default=5)
    parser.add_argument('--deep-beam', type=int, default=256)
    parser.add_argument('--expansion-budget', type=int, default=1000)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.macro_pops < 10000 or not 1 <= args.deep_pops < 10000:
        raise ValueError('each search budget must be in 1..9999')
    if args.output.exists():
        raise ValueError('refusing to overwrite output')
    rows = [run_row(source, args) for source in load_panel()]
    report = {
        'schema': 'ac19_hard_solved_retained_triangle_search_v1',
        'panel_sha256': sha(PANEL),
        'ac19_sha256': sha(AC19),
        'source_branch_commit': '9f50ff3ad47423bbdce0cf1c439a0ee272a6efa2',
        'parameters': vars(args) | {'output': str(args.output)},
        'source_sha256': {
            path.name: sha(path) for path in (
                Path(__file__), U124 / 'high_rank_triangles.py',
                HIGH_RANK / 'high_rank_ac_search_v2.py',
                HIGH_RANK / 'high_rank_ac_search.py',
                U124 / 'theory_short_relators.py', U124 / 'verify.py')
        },
        'summary': {
            'rows': len(rows),
            'solved_at_retained_rank': sum(row['solved_at_retained_rank'] for row in rows),
            'ranks': [row['retained_rank'] for row in rows],
            'macro_pops': sum(row['macro']['heap_pops'] for row in rows),
            'deep_pops': sum((row['deep'] or {}).get('heap_pops', 0) for row in rows),
            'rotation_products': sum(
                row['macro']['generated_rotation_products']
                + (row['deep'] or {}).get('generated_rotation_products', 0)
                for row in rows),
            'search_cpu_seconds': sum(
                row['macro']['cpu_seconds'] + (row['deep'] or {}).get('cpu_seconds', 0)
                for row in rows),
            'search_wall_seconds': sum(
                row['macro']['wall_seconds'] + (row['deep'] or {}).get('wall_seconds', 0)
                for row in rows),
        },
        'generation_verification': (
            'The constructor checks exact conjugator/cyclic-product identity for every child; '
            'only retained best and solution paths receive the independent Fraction/determinant replay.'),
        'scope': ('Expansion is a certified stable rank increase. Search and terminal compilation '
                  'preserve the expanded rank; no destabilization is performed.'),
        'rows': rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    partial = args.output.with_suffix(args.output.suffix + '.partial')
    partial.write_text(json.dumps(report, indent=2) + '\n')
    partial.replace(args.output)
    print(json.dumps(report['summary'], indent=2))


if __name__ == '__main__':
    main()
