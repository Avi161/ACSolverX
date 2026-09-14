"""Bounded ordinary-AC search from the retained triangular U124 states.

The search permits a one-letter ascent from triangular relators, because the
product of two length-three words has even cyclically reduced length.  Thus a
unit cannot be created in one such substitution; length four is the first
nontrivial bridge to an odd-length descendant.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import heapq
import json
from pathlib import Path
import sys
import time


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
U124 = ROOT / 'research/u124_rank_3h_20260912'
PRIOR = ROOT / 'research/rank_unbounded_20260912'
sys.path[:0] = [str(U124), str(PRIOR)]

import search
import verify


SOURCE = U124 / 'HIGH_RANK_TRIANGLES.json'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rotations(word):
    return tuple((word[k:] + word[:k], word[:k], k) for k in range(len(word)))


def structural_score(words):
    lengths = tuple(map(len, words))
    excess = sum(max(0, n - 2) for n in lengths)
    degrees = Counter(abs(x) for word in words for x in word)
    digram_rows = Counter()
    for word in words:
        if len(word) < 2:
            continue
        keys = set()
        for k in range(len(word)):
            pair = (word[k], word[(k + 1) % len(word)])
            keys.add(min(pair, search.inverse(pair)))
        digram_rows.update(keys)
    shared_digrams = sum(count * (count - 1) // 2
                         for count in digram_rows.values())
    repeated = sum(len(word) - len(set(map(abs, word))) for word in words)
    return (int(excess != 0), excess, max(lengths, default=0),
            sum(n > 2 for n in lengths), -sum(n == 1 for n in lengths),
            -sum(n == 2 for n in lengths), -shared_digrams, repeated,
            min(degrees.values(), default=0), sum(lengths), len(words))


def normal_product_event(words, target, donor, sign, target_cut, donor_cut):
    left = words[target]
    base = words[donor] if sign == 1 else search.inverse(words[donor])
    left_rotation, left_prefix, _ = rotations(left)[target_cut]
    right_rotation, right_prefix, _ = rotations(base)[donor_cut]
    conjugator = search.reduced(right_prefix + search.inverse(left_prefix))
    replacement = search.reduced(left + search.inverse(conjugator) + base + conjugator)
    product = search.canonical(left_rotation + right_rotation)
    if search.canonical(replacement) != product:
        raise AssertionError('transported cyclic product differs')
    raw = words[:target] + (replacement,) + words[target + 1:]
    after = search.normalize(raw)
    event = {
        'kind': 'normal_product_substitution',
        'before': words,
        'target': target,
        'factors': [{'donor_index': donor, 'sign': sign,
                     'conjugator': conjugator}],
        'raw_target_after': replacement,
        'raw_after': raw,
        'after': after,
        'cyclic_product_witness': {
            'target_cut': target_cut,
            'donor_cut': donor_cut,
            'target_rotation': left_rotation,
            'donor_rotation': right_rotation,
            'canonical_product': product,
        },
        'charged_units': 1,
    }
    if verify.verify_event(event, known_trivial=True) != after:
        raise AssertionError('normal-product verifier differs')
    return after, event


def generate(words, relator_cap):
    """Generate every signed cyclic one-donor product within ``relator_cap``."""
    if search.normalize(words) != words:
        raise ValueError('normalized state required')
    outcomes = {}
    attempted = 0
    for i, target in enumerate(words):
        for j, donor in enumerate(words):
            if i == j or not target or not donor:
                continue
            for sign in (1, -1):
                base = donor if sign == 1 else search.inverse(donor)
                for k1 in range(len(target)):
                    left = target[k1:] + target[:k1]
                    for k2 in range(len(base)):
                        attempted += 1
                        product = search.canonical(left + base[k2:] + base[:k2])
                        if product == target or len(product) > relator_cap:
                            continue
                        raw = words[:i] + (product,) + words[i + 1:]
                        endpoint = search.normalize(raw)
                        candidate = (i, j, sign, k1, k2)
                        if endpoint not in outcomes or candidate < outcomes[endpoint]:
                            outcomes[endpoint] = candidate
    emitted = []
    for endpoint, (i, j, sign, k1, k2) in outcomes.items():
        rebuilt, event = normal_product_event(words, i, j, sign, k1, k2)
        if rebuilt != endpoint:
            raise AssertionError('generated endpoint changed during witness construction')
        emitted.append((endpoint, event))
    emitted.sort(key=lambda item: (structural_score(item[0]), item[0]))
    return emitted, attempted


def generate_target(words, target_index, relator_cap):
    """Generate all products changing one declared target row."""
    outcomes = {}
    attempted = 0
    target = words[target_index]
    for donor_index, donor in enumerate(words):
        if donor_index == target_index or not target or not donor:
            continue
        for sign in (1, -1):
            base = donor if sign == 1 else search.inverse(donor)
            for target_cut in range(len(target)):
                left = target[target_cut:] + target[:target_cut]
                for donor_cut in range(len(base)):
                    attempted += 1
                    product = search.canonical(left + base[donor_cut:] + base[:donor_cut])
                    if product == target or len(product) > relator_cap:
                        continue
                    endpoint = search.normalize(
                        words[:target_index] + (product,) + words[target_index + 1:])
                    witness = (target_index, donor_index, sign, target_cut, donor_cut)
                    if endpoint not in outcomes or witness < outcomes[endpoint]:
                        outcomes[endpoint] = witness
    emitted = []
    for endpoint, witness in outcomes.items():
        rebuilt, event = normal_product_event(words, *witness)
        if rebuilt != endpoint:
            raise AssertionError('targeted endpoint changed during witness construction')
        emitted.append((endpoint, [event]))
    emitted.sort(key=lambda item: (structural_score(item[0]), item[0]))
    return emitted, attempted


def generate_short_macros(words):
    """Every short direct product and every two-step path through one quartic."""
    direct, direct_attempts = generate(words, 3)
    outcomes = {endpoint: [event] for endpoint, event in direct}
    first, first_attempts = generate(words, 4)
    attempted = direct_attempts + first_attempts
    for intermediate, first_event in first:
        quartics = [i for i, word in enumerate(intermediate) if len(word) == 4]
        if len(quartics) != 1 or any(len(word) > 4 for word in intermediate):
            continue
        second, charge = generate_target(intermediate, quartics[0], 3)
        attempted += charge
        for endpoint, second_events in second:
            path = [first_event, *second_events]
            if endpoint not in outcomes:
                outcomes[endpoint] = path
    emitted = sorted(outcomes.items(), key=lambda item: (structural_score(item[0]), item[0]))
    return emitted, attempted


def search_row(initial, *, pop_budget=250, relator_cap=4, beam=128,
               neighborhood='short_macros'):
    initial = search.normalize(initial)
    records = [{'words': initial, 'parent': None, 'events': []}]
    seen = {initial}
    best_fixed = (structural_score(initial), 0)
    solved = None
    generated_attempts = emitted_states = 0
    heap = [(structural_score(initial), initial, 0)]
    pops = 0
    while heap and pops < pop_budget and solved is None:
        _, _, parent = heapq.heappop(heap)
        current = records[parent]['words']
        current_score = structural_score(current)
        if not current_score[0]:
            solved = parent
            break
        if neighborhood == 'short_macros':
            children, attempted = generate_short_macros(current)
        elif neighborhood == 'quartic':
            one_step, attempted = generate(current, relator_cap)
            children = [(endpoint, [event]) for endpoint, event in one_step]
        else:
            raise ValueError('unknown neighborhood')
        generated_attempts += attempted
        pops += 1
        ranked = []
        for endpoint, events in children:
            if endpoint in seen:
                continue
            seen.add(endpoint)
            index = len(records)
            records.append({'words': endpoint, 'parent': parent, 'events': events})
            fixed_score = structural_score(endpoint)
            if fixed_score < best_fixed[0]:
                best_fixed = (fixed_score, index)
            ranked.append((fixed_score, endpoint, index))
        ranked.sort()
        emitted_states += len(ranked)
        for item in ranked[:beam]:
            heapq.heappush(heap, item)

    fixed_index = solved if solved is not None else best_fixed[1]
    endpoint = records[fixed_index]['words']
    chunks = []
    cursor = fixed_index
    while records[cursor]['parent'] is not None:
        chunks.append(records[cursor]['events'])
        cursor = records[cursor]['parent']
    path = [event for chunk in reversed(chunks) for event in chunk]
    best_fixed_index = best_fixed[1]
    best_chunks = []
    while records[best_fixed_index]['parent'] is not None:
        best_chunks.append(records[best_fixed_index]['events'])
        best_fixed_index = records[best_fixed_index]['parent']
    best_fixed_path = [event for chunk in reversed(best_chunks) for event in chunk]
    return {
        'endpoint': endpoint,
        'events': path,
        'solved_to_length_at_most_two': solved is not None,
        'best_fixed_endpoint': records[best_fixed[1]]['words'],
        'best_fixed_events': best_fixed_path,
        'initial_score': structural_score(initial),
        'endpoint_score': structural_score(endpoint),
        'best_fixed_score': best_fixed[0],
        'heap_pops': pops,
        'pop_budget': pop_budget,
        'relator_cap': relator_cap,
        'neighborhood': neighborhood,
        'beam': beam,
        'discovered_states': len(seen),
        'generated_rotation_products': generated_attempts,
        'emitted_unique_states': emitted_states,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ids', nargs='*')
    parser.add_argument('--pops', type=int, default=250)
    parser.add_argument('--cap', type=int, default=4)
    parser.add_argument('--beam', type=int, default=128)
    parser.add_argument('--neighborhood', choices=('short_macros', 'quartic'),
                        default='short_macros')
    parser.add_argument('--seed-results')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    if not 1 <= args.pops < 10000:
        raise ValueError('pops must be in 1..9999')
    if args.cap < 4:
        raise ValueError('cap must be at least4 to leave the triangular parity barrier')
    output = Path(args.output)
    if output.exists():
        raise ValueError('refusing to overwrite output')
    source = json.loads(SOURCE.read_text())
    seed_path = Path(args.seed_results) if args.seed_results else None
    seed_report = json.loads(seed_path.read_text()) if seed_path else None
    seeds = {row['name']: row for row in seed_report['rows']} if seed_report else {}
    selected = [row for row in source['retained_rows']
                if not args.ids or row['name'] in args.ids]
    if args.ids and {row['name'] for row in selected} != set(args.ids):
        raise ValueError('unknown or duplicate requested ID')
    baseline = verify.load_baseline()
    rows = []
    for source_row in selected:
        source_endpoint = tuple(map(tuple, source_row['endpoint']))
        seed = seeds.get(source_row['name'])
        seed_events = list(seed['best_fixed_events']) if seed else []
        initial = tuple(map(tuple, seed['best_fixed_endpoint'])) if seed else source_endpoint
        cpu, wall = time.process_time(), time.perf_counter()
        result = search_row(initial, pop_budget=args.pops,
                            relator_cap=args.cap, beam=args.beam,
                            neighborhood=args.neighborhood)
        result.update({
            'name': source_row['name'],
            'source_sha256': sha(SOURCE),
            'source_endpoint': source_endpoint,
            'search_initial': initial,
            'seed_results': str(seed_path) if seed_path else None,
            'seed_results_sha256': sha(seed_path) if seed_path else None,
            'seed_events': seed_events,
            'cpu_seconds': time.process_time() - cpu,
            'wall_seconds': time.perf_counter() - wall,
        })
        full = {
            'name': source_row['name'],
            'baseline_sha256': source_row['baseline_sha256'],
            'source_key': source_row['source_key'],
            'initial': source_row['initial'],
            'events': source_row['events'] + seed_events + result['events'],
            'endpoint': result['endpoint'],
        }
        result['verification'] = verify.verify_record(full, baseline)
        rows.append(result)
        print(source_row['name'], 'solved', result['solved_to_length_at_most_two'],
              'pops', result['heap_pops'], 'states', result['discovered_states'],
              'score', result['endpoint_score'], flush=True)
        time.sleep(0.05)
    report = {
        'schema': 'u124_retained_triangle_fixed_rank_ordinary_ac_search_v1',
        'source_sha256': sha(SOURCE),
        'script_sha256': sha(Path(__file__)),
        'parameters': {'pop_budget': args.pops, 'relator_cap': args.cap,
                       'beam': args.beam, 'neighborhood': args.neighborhood},
        'summary': {
            'rows': len(rows),
            'solved_to_length_at_most_two': sum(r['solved_to_length_at_most_two'] for r in rows),
            'fixed_rank_structural_improvements': sum(
                r['best_fixed_score'] < r['initial_score'] for r in rows),
            'heap_pops': sum(r['heap_pops'] for r in rows),
            'discovered_states': sum(r['discovered_states'] for r in rows),
            'generated_rotation_products': sum(r['generated_rotation_products'] for r in rows),
            'cpu_seconds': sum(r['cpu_seconds'] for r in rows),
            'wall_seconds': sum(r['wall_seconds'] for r in rows),
        },
        'certificate_scope': 'fixed-rank ordinary AC normal-product composites only; independently replayed by verify.py; no generator removal or destabilization',
        'rows': rows,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    partial = output.with_suffix(output.suffix + '.partial')
    partial.write_text(json.dumps(report, indent=2) + '\n')
    partial.replace(output)
    print(json.dumps(report['summary'], indent=2))


if __name__ == '__main__':
    main()
