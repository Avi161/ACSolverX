"""Independent explicit-set-partition audit of finite cyclic join complements."""
from collections import Counter, deque
from itertools import combinations, product
import hashlib
import json
from pathlib import Path
import time

from . import cyclic_complement as subject

HERE = Path(__file__).resolve().parent
ALPHABET = 'xXyY'
ROSE = tuple(sorted((0, c, 0) for c in ALPHABET))


def inverse(word):
    return ''.join({'x': 'X', 'X': 'x', 'y': 'Y', 'Y': 'y'}[c] for c in reversed(word))


def reduce_word(word):
    if any(c not in ALPHABET for c in word):
        raise ValueError('invalid free word')
    while True:
        before = word
        for cancellation in ('xX', 'Xx', 'yY', 'Yy'):
            word = word.replace(cancellation, '')
        if word == before:
            return word


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(1 << 20), b''):
            digest.update(chunk)
    return digest.hexdigest()


def partition_fold(edges, count, identify=None):
    blocks = [{i} for i in range(count)]
    if identify is not None:
        a, b = sorted(identify)
        blocks[a] |= blocks[b]
        del blocks[b]
    while True:
        labels = {v: i for i, block in enumerate(blocks) for v in block}
        targets = {}
        collision = None
        for u, c, v in edges:
            key, destination = (labels[u], c), labels[v]
            if key in targets and targets[key] != destination:
                collision = sorted((targets[key], destination))
                break
            targets[key] = destination
        if collision is None:
            break
        a, b = collision
        blocks[a] |= blocks[b]
        del blocks[b]
    start = labels[0]
    names, todo = {start: 0}, deque([start])
    while todo:
        u = todo.popleft()
        for c in ALPHABET:
            v = targets.get((u, c))
            if v is not None and v not in names:
                names[v] = len(names)
                todo.append(v)
    return tuple(sorted((names[u], c, names[v]) for (u, c), v in targets.items()))


def independent_graph(words):
    edges, count = [], 1
    for word in words:
        word = reduce_word(word)
        path = [0] + list(range(count, count + max(0, len(word) - 1))) + [0]
        count += max(0, len(word) - 1)
        for u, c, v in zip(path, word, path[1:]):
            edges.append((u, c, v))
            edges.append((v, inverse(c), u))
    return partition_fold(edges, count)


def root_paths(graph):
    arcs = {(u, c): v for u, c, v in graph}
    paths, todo = {0: ''}, deque([0])
    while todo:
        u = todo.popleft()
        for c in ALPHABET:
            v = arcs.get((u, c))
            if v is not None and v not in paths:
                paths[v] = paths[u] + c
                todo.append(v)
    return paths


def complement(graph, max_pairs=1000, *, shortest_first=False):
    if graph == ROSE:
        return {'status': 'already_generates', 'complement': '', 'pairs_checked': 0,
                'complete': True}
    paths = root_paths(graph)
    if len(paths) == 1:
        missing = [c for c in 'xy' if (0, c, 0) not in graph]
        return {'status': 'cyclic_complement' if len(missing) == 1 else 'no_cyclic_complement',
                **({'complement': missing[0]} if len(missing) == 1 else {}),
                'pairs_checked': 0, 'complete': True}
    pairs = list(combinations(sorted(paths), 2))
    if shortest_first:
        pairs.sort(key=lambda uv: (len(reduce_word(paths[uv[0]] + inverse(paths[uv[1]]))), uv))
    for checked, (u, v) in enumerate(pairs[:max_pairs], 1):
        if partition_fold(graph, len(paths), (u, v)) == ROSE:
            return {'status': 'cyclic_complement', 'complement': reduce_word(paths[u] + inverse(paths[v])),
                    'identified': [u, v], 'pairs_checked': checked, 'complete': True}
    count = min(max_pairs, len(pairs))
    complete = count == len(pairs)
    return {'status': 'no_cyclic_complement' if complete else 'unknown_pair_cap',
            'pairs_checked': count, 'complete': complete}


def audit():
    wall, cpu = time.perf_counter(), time.process_time()
    saved_path = HERE / 'cyclic_complement_u124.json'
    saved = json.loads(saved_path.read_text())
    counts, controls, records = Counter(), [], []
    words = [''] + [c for c in ALPHABET] + [''.join(p) for p in product(ALPHABET, repeat=2)
                                                   if p[0] != inverse(p[1])]
    planted = [([], 'no_cyclic_complement'), (['', ''], 'no_cyclic_complement'),
               (['x'], 'cyclic_complement'), (['Y'], 'cyclic_complement'),
               (['x', 'y'], 'already_generates'), (['xx', 'yy'], 'no_cyclic_complement'),
               (['xx', 'y'], 'cyclic_complement'), (['xyX', ''], 'cyclic_complement'),
               (['xYyX', 'y'], 'cyclic_complement')]
    for pair, expected in planted + [(list(p), None) for p in product(words, repeat=2)]:
        graph = independent_graph(pair)
        assert graph == subject.graph(pair), pair
        actual, other = complement(graph), subject.analyze(pair)
        assert actual['status'] == other['status'], (pair, actual, other)
        if expected is not None:
            assert actual['status'] == expected, (pair, expected, actual)
        if 'complement' in actual:
            assert independent_graph([*pair, actual['complement']]) == ROSE
            assert independent_graph([*pair, other['complement']]) == ROSE
            counts['positive_control_words_verified'] += 1
        if expected is not None:
            controls.append({'pair': pair, **actual})
        counts['control_graphs_and_decisions'] += 1
    for row in saved['records']:
        graph = independent_graph(row['pair'])
        assert graph == tuple(map(tuple, row['graph'])) == subject.graph(row['pair'])
        paths = root_paths(graph)
        pairs = list(combinations(sorted(paths), 2))
        for pair in pairs:
            child = partition_fold(graph, len(paths), pair)
            assert child == subject.folded(graph, len(paths), pair), (row['name'], pair)
            assert child != ROSE, (row['name'], pair)
        assert row['status'] == 'no_cyclic_complement' and row['complete']
        assert row['pairs_checked'] == len(pairs)
        records.append({'name': row['name'], 'vertices': len(paths), 'pairs_checked': len(pairs),
                        'status': 'no_cyclic_complement', 'complete': True})
        counts['root_graphs_checked'] += 1
        counts['root_identifications_crosschecked'] += len(pairs)
    assert len(records) == 124 and len({r['name'] for r in records}) == 124
    report = {'status': 'pass', 'algorithm': 'explicit disjoint set blocks; one fold collision per iteration; no union-find',
              'source': 'https://gcc.episciences.org/6059/pdf', 'source_result': 'Lemma 5.3; one-vertex case in Theorem 5.4',
              'scope': 'Exact cyclic join-complement absence for the 124 saved literal input subgroups only; no claim of group nontriviality or absence after AC moves.',
              'counts': dict(counts), 'controls': controls, 'records': records,
              'hashes': {p.name: sha256(p) for p in [saved_path, Path(subject.__file__), Path(__file__)]},
              'wall_seconds': time.perf_counter() - wall, 'cpu_seconds': time.process_time() - cpu}
    (HERE / 'complement_audit.json').write_text(json.dumps(report, indent=2) + '\n')
    (HERE / 'complement_audit.md').write_text(
        '# Independent cyclic-complement audit\n\n'
        'PASS. Explicit set partitions reproduce every saved root graph and all '
        f"{counts['root_identifications_crosschecked']:,} identified-vertex quotients across 124 inputs. "
        'None folds to the full x/y rose.\n\n'
        f"{counts['control_graphs_and_decisions']} small controls match the author implementation; "
        f"{counts['positive_control_words_verified']} positive control words independently generate the rose when adjoined. "
        'Controls cover the empty subgroup, one-loop and full bouquets, proper power subgroups, conjugated generators, and free cancellation.\n\n'
        'The independent folder explicitly merges sets of vertices and restarts after each collision; '
        'the author folder uses union-find. Both canonically label the resulting rooted graph.\n\n'
        'The exact negative conclusion applies to these literal subgroups only. It excludes neither '
        'a complement after ordinary AC changes nor stable AC-triviality by another route, and says nothing '
        'about nontriviality of the presented groups.\n\n'
        'Criterion: [Delgado–Silva, Lemma 5.3 and Theorem 5.4](https://gcc.episciences.org/6059/pdf). '
        'Detailed counts, source hashes, controls and timings are in `complement_audit.json`.\n')
    print(json.dumps({k: report[k] for k in ['status', 'counts', 'wall_seconds', 'cpu_seconds']}), flush=True)


if __name__ == '__main__':
    audit()
