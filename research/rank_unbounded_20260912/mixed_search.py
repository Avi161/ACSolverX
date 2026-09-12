"""Finite work budget for rank-unbounded stable moves; no length ceiling."""
from __future__ import annotations

import argparse
from collections import Counter
import heapq
import json
from pathlib import Path
import time

import lemma11
import search
import whitehead


def all_definitions(words):
    candidates = Counter()
    for word in words:
        doubled = word + word
        for size in range(2, len(word) + 1):
            for cut in range(len(word)):
                defining = doubled[cut:cut + size]
                candidates[min(defining, search.inverse(defining))] += 1
    return sorted(candidates, key=lambda w: (-(candidates[w] * (len(w) - 1) - len(w) - 1), len(w), w))


def ac_descents(words, available):
    used, out, seen = 0, [], set()
    for i, target in enumerate(words):
        for j, donor in enumerate(words):
            if i == j or not target or not donor:
                continue
            for sign in (1, -1):
                base = donor if sign == 1 else search.inverse(donor)
                for k1 in range(len(target)):
                    left = target[k1:] + target[:k1]
                    for k2 in range(len(base)):
                        right = base[k2:] + base[:k2]
                        if left[-1] != -right[0] and right[-1] != -left[0]:
                            continue
                        if used == available:
                            return out, used
                        used += 1
                        product = search.canonical(left + right)
                        if len(product) >= len(target):
                            continue
                        raw = words[:i] + (product,) + words[i + 1:]
                        after = search.normalize(raw)
                        if after in seen:
                            continue
                        seen.add(after)
                        out.append((after, [{'kind': 'ordinary_ac_substitution', 'before': words,
                                             'target': i, 'donor': j, 'donor_sign': sign,
                                             'target_cut': k1, 'donor_cut': k2,
                                             'after': after}]))
    return out, used


def run_row(row, *, budget=1000, mode='frontier'):
    cpu, wall = time.process_time(), time.perf_counter()
    saved, mapping = search.parse_words(row['best_words'])
    original, old_mapping = search.parse_words(row['starting_words'])
    records, seen, heap = [], set(), []
    costs = Counter()
    best, best_length, max_rank, expanded = None, search.length(saved), len(saved), 0
    seen_by_rank = Counter()

    def remaining():
        return budget - sum(costs.values())

    def register(words, parent, events, source):
        nonlocal best, best_length, max_rank
        words = search.normalize(words)
        max_rank = max(max_rank, len(words))
        if words in seen:
            return None
        seen.add(words)
        index = len(records)
        records.append({'words': words, 'parent': parent, 'events': events, 'source': source})
        seen_by_rank[len(words)] += 1
        heapq.heappush(heap, (search.length(words), len(words), index))
        if search.length(words) < best_length:
            best, best_length = index, search.length(words)
        return index

    for source, seed in (('saved_best', saved), ('saved_rank2', original)):
        after, events, charge, _ = whitehead.descend(seed, remaining())
        costs['minimum_cuts'] += charge
        register(after, None, events, source)
    ladder_cursor = 0
    while remaining() > 0 and (heap if mode == 'frontier' else ladder_cursor < len(records)):
        if mode == 'frontier':
            _, _, parent = heapq.heappop(heap)
        else:
            parent = ladder_cursor
        words = records[parent]['words']
        source = records[parent]['source']
        expanded += 1
        ac, charge = ac_descents(words, min(16 if mode == 'ladder' else 64, remaining()))
        costs['ac_products'] += charge
        for after, events in ac:
            register(after, parent, events, source)
        removals, charge = lemma11.generate_removals(words, min(8 if mode == 'ladder' else 120, remaining()),
                                                   expose_primitives=mode != 'ladder')
        costs['lemma11_and_primitive_units'] += charge
        for after, events in removals:
            register(after, parent, events, source)
        choices = []
        # In the ladder arm one promising definition is accepted per round,
        # even when its complete tuple is longer; budget alone stops growth.
        number = 3 if mode == 'ladder' else 12
        for defining in all_definitions(words)[:number]:
            if remaining() <= 0:
                break
            after, event = search.compress(words, defining)
            event['kind'] = 'defining_compression'
            costs['definitions'] += 1
            after, path, charge, _ = whitehead.descend(after, remaining())
            costs['minimum_cuts'] += charge
            index = register(after, parent, [event, *path], source)
            if index is not None:
                choices.append((search.length(after), after, index))
        if mode == 'ladder':
            if not choices:
                break
            ladder_cursor = min(choices)[2]
    endpoint, source, events = saved, 'saved_best', []
    if best is not None:
        endpoint, source = records[best]['words'], records[best]['source']
        while best is not None:
            events = records[best]['events'] + events
            best = records[best]['parent']
    rank_curve = {rank: min(search.length(r['words']) for r in records if len(r['words']) == rank)
                  for rank in seen_by_rank}
    return {'name': row['name'], 'mode': mode, 'saved_best': saved, 'saved_rank2': original,
            'input_generator_map': mapping, 'rank2_generator_map': old_mapping,
            'saved_best_pointer': row['source_certificate_pointer'],
            'saved_rank2_pointer': row['best_rank2_source_certificate_pointer'],
            'input_length': search.length(saved), 'best': endpoint, 'best_length': search.length(endpoint),
            'best_rank': len(endpoint), 'additional_gain': search.length(saved) - search.length(endpoint),
            'path_source': source, 'events': events, 'costs': dict(costs),
            'total_units': sum(costs.values()), 'budget': budget,
            'rank_limit': None, 'length_limit': None,
            'maximum_accepted_rank': max_rank, 'rank_length_curve': rank_curve,
            'expanded_states': expanded, 'discovered_states': len(records),
            'stop': 'work_budget' if remaining() <= 0 else 'screened_frontier_exhausted',
            'cpu_seconds': time.process_time() - cpu, 'wall_seconds': time.perf_counter() - wall,
            'fully_expanded_stable_certificate': False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=('frontier', 'ladder'), default='frontier')
    parser.add_argument('--ids', nargs='*')
    parser.add_argument('--output', required=True)
    parser.add_argument('--reuse')
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    source = here.parent / 'theory_patterns_20260912/u124_final_table.json'
    paths = [source, Path(__file__), here / 'search.py', here / 'whitehead.py', here / 'lemma11.py']
    hashes = {p.name: search.sha(p) for p in paths}
    previous = json.loads(Path(args.reuse).read_text()) if args.reuse else None
    if previous and (previous['hashes'] != hashes or previous['mode'] != args.mode):
        raise ValueError('pilot provenance differs')
    reuse = {r['name']: r for r in previous['rows']} if previous else {}
    records = []
    for row in json.loads(source.read_text())['rows']:
        if args.ids and row['name'] not in args.ids:
            continue
        result = reuse.get(row['name'])
        if result is None:
            result = run_row(row, mode=args.mode)
            time.sleep(0.05)
        records.append(result)
        print(row['name'], result['input_length'], result['best_length'], 'rank', result['best_rank'],
              'visited rank', result['maximum_accepted_rank'], result['total_units'], flush=True)
    summary = {'rows': len(records), 'gain_ids': [r['name'] for r in records if r['additional_gain']],
               'input_total': sum(r['input_length'] for r in records),
               'best_total': sum(r['best_length'] for r in records),
               'cpu_seconds': sum(r['cpu_seconds'] for r in records),
               'wall_seconds': sum(r['wall_seconds'] for r in records),
               'total_units': sum(r['total_units'] for r in records),
               'best_ranks': dict(Counter(r['best_rank'] for r in records)),
               'maximum_accepted_rank': max(r['maximum_accepted_rank'] for r in records)}
    output = Path(args.output)
    if output.exists():
        raise ValueError('refusing to overwrite existing result')
    output.write_text(json.dumps({'hashes': hashes, 'mode': args.mode, 'rows': records, 'summary': summary}, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
