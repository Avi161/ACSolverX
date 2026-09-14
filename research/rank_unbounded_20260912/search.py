"""Small candidate-budget dictionary exploration with arbitrary integer generators."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import heapq
import json
from pathlib import Path
import time


def inverse(word):
    return tuple(-x for x in reversed(word))


def reduced(word):
    out = []
    for x in word:
        if type(x) is not int or not x:
            raise ValueError('letters must be nonzero signed integers')
        if out and out[-1] == -x:
            out.pop()
        else:
            out.append(x)
    return tuple(out)


def canonical(word):
    word = reduced(word)
    while len(word) > 1 and word[0] == -word[-1]:
        word = word[1:-1]
    if not word:
        return ()
    return min(w[k:] + w[:k] for w in (word, inverse(word)) for k in range(len(w)))


def normalize(words):
    return tuple(sorted(canonical(w) for w in words))


def length(words):
    return sum(map(len, words))


def parse_words(words):
    order = 'xyzuvw'
    used = sorted({c.lower() for w in words for c in w}, key=order.index)
    ids = {c: i + 1 for i, c in enumerate(used)}
    return tuple(tuple(ids[c.lower()] * (1 if c.islower() else -1) for c in w) for w in words), ids


def render(words):
    return [' '.join(('g' + str(abs(x))) + ('^-1' if x < 0 else '') for x in w) or '1' for w in words]


def tokenize(word, defining, helper):
    inverse_definition = inverse(defining)
    size = len(defining)
    best = [()] * (len(word) + 1)
    for i in range(len(word) - 1, -1, -1):
        choices = [(word[i],) + best[i + 1]]
        block = word[i:i + size]
        if block == defining:
            choices.append((helper,) + best[i + size])
        if block == inverse_definition:
            choices.append((-helper,) + best[i + size])
        best[i] = min(choices, key=lambda w: (len(w), w))
    return best[0]


def definitions(words):
    candidates = Counter()
    for word in words:
        doubled = word + word
        for size in range(2, len(word) + 1):
            for k in range(len(word)):
                w = doubled[k:k + size]
                candidates[min(w, inverse(w))] += 1
    # Every accepted edge needs at least two uses. Cyclic overlapping counts
    # are only an upper bound, so exact nonoverlapping tokenization follows.
    return sorted((w for w, count in candidates.items() if count >= 2),
                  key=lambda w: (-(candidates[w] * (len(w) - 1) - len(w) - 1), len(w), w))


def compress(words, defining):
    helper = 1 + max((abs(x) for w in words for x in w), default=0)
    templates, cuts = [], []
    for word in words:
        choices = [(tokenize(word[k:] + word[:k], defining, helper), k)
                   for k in range(max(1, len(word)))]
        template, cut = min(choices, key=lambda t: (len(t[0]), t[0], t[1]))
        templates.append(template)
        cuts.append(cut)
    raw = ((-helper,) + defining, *templates)
    count = sum(sum(abs(x) == helper for x in w) for w in templates)
    predicted = length(words) + len(defining) + 1 - count * (len(defining) - 1)
    if predicted != length(raw) or any(reduced(w) != w for w in raw):
        raise AssertionError('literal accounting failed')
    after = normalize(raw)
    return after, {'before': words, 'defining': defining, 'helper': helper,
                   'cuts': cuts, 'templates': templates, 'raw_after': raw,
                   'after': after, 'uses': count, 'literal_length': predicted,
                   'final_length': length(after)}


def greedy(words, budget):
    start_cpu, start_wall = time.process_time(), time.perf_counter()
    current, path, used, rounds, complete = normalize(words), [], 0, 0, True
    while used < budget:
        best = None
        candidates = definitions(current)
        complete = True
        rounds += 1
        for defining in candidates:
            if used == budget:
                complete = False
                break
            after, edge = compress(current, defining)
            used += 1
            if length(after) < length(current) and (best is None or (length(after), after) < (length(best[0]), best[0])):
                best = after, edge
        if best is None:
            break
        current, edge = best
        path.append(edge)
        if not complete:
            break
    return {'best': current, 'path': path, 'evaluations': used, 'rounds': rounds,
            'stop': 'no_strict_compression' if complete and used < budget else 'candidate_budget',
            'cpu_seconds': time.process_time() - start_cpu,
            'wall_seconds': time.perf_counter() - start_wall}


def explore(seeds, budget, ceiling, best_length):
    start_cpu, start_wall = time.process_time(), time.perf_counter()
    heap, records, seen = [], [], set()
    best, used, popped, edges = None, 0, 0, 0
    max_rank = 0
    for source, words in seeds:
        state = normalize(words)
        if state in seen:
            continue
        seen.add(state)
        records.append((state, None, None, source))
        heapq.heappush(heap, (length(state), len(state), len(records) - 1))
    while heap and used < budget:
        _, _, index = heapq.heappop(heap)
        words = records[index][0]
        popped += 1
        for defining in definitions(words):
            if used == budget:
                break
            after, edge = compress(words, defining)
            used += 1
            if length(after) > ceiling or edge['uses'] < 2:
                continue
            max_rank = max(max_rank, len(after))
            edges += 1
            if after in seen:
                continue
            seen.add(after)
            records.append((after, index, edge, records[index][3]))
            child = len(records) - 1
            heapq.heappush(heap, (length(after), len(after), child))
            if length(after) < best_length:
                best, best_length = child, length(after)
    path, source, endpoint = [], None, None
    if best is not None:
        endpoint, source = records[best][0], records[best][3]
        while records[best][1] is not None:
            path.append(records[best][2])
            best = records[best][1]
        path.reverse()
    return {'best': endpoint, 'source': source, 'path': path, 'evaluations': used,
            'popped_states': popped, 'accepted_edges': edges, 'discovered_states': len(records),
            'maximum_accepted_rank': max_rank, 'ceiling': ceiling,
            'stop': 'candidate_budget' if used == budget else 'frontier_exhausted',
            'cpu_seconds': time.process_time() - start_cpu,
            'wall_seconds': time.perf_counter() - start_wall}


def run_row(row, budget=1000):
    words, mapping = parse_words(row['best_words'])
    initial, initial_mapping = parse_words(row['starting_words'])
    descent = greedy(words, budget // 3)
    remaining = budget - descent['evaluations']
    branch = explore([('saved_best', words), ('saved_rank2', initial)], remaining,
                     ceiling=length(words) + 2, best_length=length(descent['best']))
    endpoint = branch['best'] if branch['best'] is not None else descent['best']
    return {'name': row['name'], 'source_pointer': row['source_certificate_pointer'],
            'input_length': length(words), 'input_rank': len(words), 'input': words,
            'input_generator_map': mapping, 'rank2_input': initial,
            'rank2_generator_map': initial_mapping, 'greedy': descent, 'branch': branch,
            'best': endpoint, 'best_rank': len(endpoint), 'best_length': length(endpoint),
            'additional_gain': length(words) - length(endpoint),
            'evaluations': descent['evaluations'] + branch['evaluations'],
            'budget': budget, 'rank_limit': None, 'fully_expanded_stable_certificate': False}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ids', nargs='*')
    parser.add_argument('--budget', type=int, default=1000)
    parser.add_argument('--output', required=True)
    parser.add_argument('--reuse')
    args = parser.parse_args()
    if not 1 <= args.budget <= 1000:
        raise ValueError('local candidate budget must be 1..1000')
    here = Path(__file__).resolve().parent
    source = here.parent / 'theory_patterns_20260912/u124_final_table.json'
    rows = json.loads(source.read_text())['rows']
    selected = set(args.ids) if args.ids else {r['name'] for r in rows}
    if selected - {r['name'] for r in rows}:
        raise ValueError('unknown presentation ID')
    previous = json.loads(Path(args.reuse).read_text()) if args.reuse else None
    if previous and (previous['source_sha256'] != sha(source) or previous['script_sha256'] != sha(Path(__file__)) or previous['budget'] != args.budget):
        raise ValueError('pilot provenance differs')
    reuse = {r['name']: r for r in previous['rows']} if previous else {}
    records = []
    for row in rows:
        if row['name'] not in selected:
            continue
        result = reuse.get(row['name'])
        if result is None:
            result = run_row(row, args.budget)
            time.sleep(0.05)
        records.append(result)
        print(row['name'], result['input_length'], result['best_length'], result['best_rank'], result['evaluations'], flush=True)
    report = {'source_sha256': sha(source), 'source_file': str(source), 'script_sha256': sha(Path(__file__)),
              'budget': args.budget, 'rank_limit': None, 'rows': records,
              'summary': {'rows': len(records), 'gain_ids': [r['name'] for r in records if r['additional_gain']],
                          'input_total': sum(r['input_length'] for r in records),
                          'best_total': sum(r['best_length'] for r in records),
                          'evaluations': sum(r['evaluations'] for r in records),
                          'cpu_seconds': sum(r[k]['cpu_seconds'] for r in records for k in ('greedy', 'branch')),
                          'wall_seconds': sum(r[k]['wall_seconds'] for r in records for k in ('greedy', 'branch')),
                          'best_ranks': dict(Counter(r['best_rank'] for r in records)),
                          'maximum_accepted_rank': max(r['branch']['maximum_accepted_rank'] for r in records)}}
    destination = Path(args.output)
    if destination.exists():
        raise ValueError('refusing to overwrite existing results')
    destination.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report['summary'], indent=2))


if __name__ == '__main__':
    main()
