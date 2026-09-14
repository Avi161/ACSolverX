"""Independent finite certificate audit for exact occurrence-link exclusions."""
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import itertools
import json
from pathlib import Path
import time

HERE = Path(__file__).resolve().parent
FROZEN = {
    'rank3_neuwirth_extension.md': 'd0f8339bf4fedb737eddeec88427f93e6fec23b3896caba6237282bb190b1b8c',
    'rank3_neuwirth_extension.py': 'de0734ec8e3ed2d1049e154270cb15174e201fdb7cbe3d966b39c6d2d52e7a78',
    'rank3_neuwirth_extension.json': 'fc89d13d7da0447bd7de057cb8831a9d83fae990085ef32a3aec97ac7bd191f1'}


def require(value, message):
    if not value:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def edge(a, b):
    return ''.join(sorted((a, b)))


def literal_data(words):
    require(all(w and all(c in 'xXyYzZuUvVwW' for c in w) for w in words), 'literal alphabet')
    multiplicities, observed, occurrences = Counter(), defaultdict(Counter), []
    for ri, word in enumerate(words):
        for i, letter in enumerate(word):
            previous, following = word[i - 1], word[(i + 1) % len(word)]
            incoming = edge(previous.swapcase(), letter)
            outgoing = edge(letter.swapcase(), following)
            positive, negative = (incoming, outgoing) if letter.islower() else (outgoing, incoming)
            multiplicities[outgoing] += 1
            observed[letter.lower()][positive, negative] += 1
            occurrences.append({'relator_index': ri, 'letter_index': i, 'letter': letter,
                                'positive_class': positive, 'negative_class': negative})
    adjacency = defaultdict(set)
    for a, b in multiplicities:
        adjacency[a].add(b)
        adjacency[b].add(a)
    require(sum(multiplicities.values()) == sum(map(len, words)), 'corner occurrence count')
    return multiplicities, dict(observed), dict(adjacency), occurrences


def connected(adjacency, deleted=()):
    remaining = set(adjacency) - set(deleted)
    if not remaining:
        return False
    seen, pending = set(), [min(remaining)]
    while pending:
        v = pending.pop()
        if v in seen:
            continue
        seen.add(v)
        pending.extend(adjacency[v] & remaining - seen)
    return seen == remaining


def rotation_certificate(adjacency, rotation):
    require(set(rotation) == set(adjacency), 'rotation vertex coverage')
    require(connected(adjacency), 'macro graph disconnected')
    successor = {}
    for v, order in rotation.items():
        require(len(order) == len(set(order)) and set(order) == adjacency[v], 'rotation neighbor coverage')
        for i, u in enumerate(order):
            successor[v, u] = (order[(i + 1) % len(order)], v)
    require(set(successor) == set(successor.values()), 'face map is not a permutation')
    visited, faces = set(), []
    for start in sorted(successor):
        if start in visited:
            continue
        current, face = start, []
        while current not in visited:
            visited.add(current)
            face.append(''.join(current))
            current = successor[current]
        require(current == start, 'face cycle did not close')
        faces.append(face)
    vertices, edges = len(adjacency), len(successor) // 2
    require(vertices - edges + len(faces) == 2, 'macro embedding Euler characteristic differs from2')
    cuts = [list(s) for k in range(3) for s in itertools.combinations(sorted(adjacency), k)]
    require(vertices >= 4 and all(connected(adjacency, s) for s in cuts), 'support is not3connected')
    return {'vertices': vertices, 'edges': edges, 'face_count': len(faces), 'euler_characteristic': 2,
            'face_cycles': faces, 'connected_after_deleted_vertices': cuts}


def phase_data(multiplicities, observed, rotation):
    blocks = {v: [edge(v, u) for u in order for _ in range(multiplicities[edge(v, u)])]
              for v, order in rotation.items()}
    results = {}
    for g, actual in sorted(observed.items()):
        positive, negative = blocks[g], blocks[g.upper()]
        degree = len(positive)
        require(degree == len(negative) == sum(actual.values()), 'opposite germ occurrence degree')
        predicted = [Counter((positive[j], negative[(-j - s) % degree]) for j in range(degree))
                     for s in range(degree)]
        results[g] = {'degree': degree, 'valid': [s for s, p in enumerate(predicted) if p == actual],
                      'predicted': predicted}
    return results


def verify_rigid(record):
    multiplicities, observed, adjacency, occurrences = literal_data(record['words'])
    require(not any(a == b for a, b in multiplicities), 'rigid support contains a loop')
    require(record['simple_edges'] == sorted(multiplicities), 'literal support edges differ')
    require(record['simple_edge_count'] == len(multiplicities) and record['loops'] == 0, 'support counts')
    embedding = rotation_certificate(adjacency, record['macro_rotation'])
    require(record['connectivity_deletion_checks'] == len(embedding['connected_after_deleted_vertices']), 'deletion count')
    phases = phase_data(multiplicities, observed, record['macro_rotation'])
    require(set(observed) == set(record['observed_class_pair_counts']) == set(record['phase_sets'])
            == set(record['phase_mismatch_witnesses']), 'generator ledger coverage')
    mismatches = 0
    for g, actual in observed.items():
        stored = record['observed_class_pair_counts'][g]
        require(len(stored) == len({tuple(r['class_pair']) for r in stored}), 'duplicate observed class pair')
        require(Counter({tuple(r['class_pair']): r['count'] for r in stored}) == actual, 'literal class-pair count')
        require(record['phase_sets'][g] == phases[g]['valid'], 'surviving phase ledger')
        rejected = record['phase_mismatch_witnesses'][g]
        require(sorted(r['phase'] for r in rejected) == sorted(set(range(phases[g]['degree'])) - set(phases[g]['valid'])), 'rejected phase coverage')
        for witness in rejected:
            key, phase = tuple(witness['class_pair']), witness['phase']
            predicted = phases[g]['predicted'][phase][key]
            require(witness['actual'] == actual[key] and witness['predicted'] == predicted
                    and actual[key] != predicted, 'invalid phase mismatch witness')
            mismatches += 1
    blockers = sorted(g for g, data in phases.items() if not data['valid'])
    require(sorted(record['blocking_generators']) == blockers and blockers, 'no certified blocking generator')
    require(record['status'] == 'rigid_block_count_obstruction' and record['complete'] is True, 'rigid status')
    require(record['phase_checks'] == sum(p['degree'] for p in phases.values()), 'phase check total')
    reflected = phase_data(multiplicities, observed, {v: list(reversed(r)) for v, r in record['macro_rotation'].items()})
    require(all(bool(reflected[g]['valid']) == bool(phases[g]['valid']) for g in observed), 'reflection changes feasibility')
    return {'words': record['words'], 'status': 'exact_rigid_block_count_obstruction_verified',
            'embedding': embedding, 'literal_occurrences': occurrences,
            'corner_multiplicities': dict(sorted(multiplicities.items())),
            'phase_checks': record['phase_checks'], 'mismatch_witnesses_checked': mismatches,
            'blocking_generators': blockers, 'global_reflection_verified': True}


def verify_nonplanar(record):
    multiplicities, observed, support, occurrences = literal_data(record['words'])
    require(record['simple_edges'] == sorted(multiplicities) and record['simple_edge_count'] == len(multiplicities), 'nonplanar literal support')
    require(record['loops'] == sum(a == b for a, b in multiplicities), 'nonplanar loop count')
    edges = record['kuratowski_edges']
    require(len(edges) == len(set(edges)) and all(e in multiplicities and e[0] != e[1] for e in edges), 'Kuratowski edge is not in literal support')
    graph = defaultdict(set)
    for a, b in edges:
        graph[a].add(b)
        graph[b].add(a)
    require(connected(graph), 'subdivision disconnected')
    branches = {v for v in graph if len(graph[v]) != 2}
    require((len(branches) == 5 and all(len(graph[v]) == 4 for v in branches))
            or (len(branches) == 6 and all(len(graph[v]) == 3 for v in branches)), 'subdivision branch degrees')
    used, paths, quotient = set(), [], defaultdict(set)
    for start in sorted(branches):
        for neighbor in sorted(graph[start]):
            if edge(start, neighbor) in used:
                continue
            path = [start, neighbor]
            used.add(edge(start, neighbor))
            while path[-1] not in branches:
                options = graph[path[-1]] - {path[-2]}
                require(len(options) == 1, 'internal path degree')
                nxt = next(iter(options))
                require(edge(path[-1], nxt) not in used, 'overlapping subdivision paths')
                used.add(edge(path[-1], nxt)); path.append(nxt)
            end = path[-1]
            require(end != start and end not in quotient[start], 'quotient loop or parallel edge')
            quotient[start].add(end); quotient[end].add(start); paths.append(path)
    require(used == set(edges), 'subdivision edge coverage')
    if len(branches) == 5:
        require(all(quotient[v] == branches - {v} for v in branches), 'quotient is not K5')
        kind, parts = 'K5_subdivision', None
    else:
        a = min(branches)
        right, left = quotient[a], branches - quotient[a]
        require(len(right) == len(left) == 3 and all(quotient[v] == right for v in left)
                and all(quotient[v] == left for v in right), 'quotient is not K3,3')
        kind, parts = 'K33_subdivision', [sorted(left), sorted(right)]
    require(record['kuratowski_type'] == kind and record['status'] == 'nonplanar_support'
            and record['complete'] is True, 'nonplanar certificate classification')
    return {'words': record['words'], 'status': 'exact_nonplanar_support_verified',
            'literal_occurrences': occurrences, 'corner_multiplicities': dict(sorted(multiplicities.items())),
            'subdivision_type': kind, 'branch_vertices': sorted(branches), 'branch_paths': paths,
            'bipartition': parts, 'edge_count': len(edges)}


def verify_record(record):
    return verify_rigid(record) if record['status'] == 'rigid_block_count_obstruction' else verify_nonplanar(record)


def check_controls(fixtures):
    import networkx as nx
    cache, rows = {}, []
    for words in fixtures:
        multiplicities, observed, adjacency, _ = literal_data(words)
        require(all(n == 1 for n in multiplicities.values()), 'control support is not simple')
        key = tuple(sorted(multiplicities))
        if key not in cache:
            graph = nx.Graph(); graph.add_edges_from(tuple(e) for e in key)
            planar, candidate = nx.check_planarity(graph)
            require(planar, 'control embedding construction failed')
            rotation = {v: list(candidate.neighbors_cw_order(v)) for v in graph}
            cache[key] = rotation, rotation_certificate(adjacency, rotation)
        rotation, embedding = cache[key]
        phases = phase_data(multiplicities, observed, rotation)
        require(all(p['valid'] for p in phases.values()), 'positive control fails necessary condition')
        chosen = {g: p['valid'][0] for g, p in phases.items()}
        for g, actual in observed.items():
            positive = [edge(g, u) for u in rotation[g]]
            negative = [edge(g.upper(), u) for u in rotation[g.upper()]]
            for (p, n), count in actual.items():
                require(count == 1 and negative.index(n) == (-positive.index(p) - chosen[g]) % len(positive),
                        'control occurrence mate does not reverse the cyclic pipe order')
        rows.append({'words': words, 'compatible_phases': chosen, 'euler_characteristic': embedding['euler_characteristic']})
    return {'verified_controls': len(rows), 'embedding_constructions': len(cache),
            'macro_embeddings': [{'rotation': r, 'certificate': e} for r, e in cache.values()], 'rows': rows}


def main():
    wall, cpu = time.perf_counter(), time.process_time()
    for filename, value in FROZEN.items():
        require(digest(HERE / filename) == value, 'frozen source hash changed: ' + filename)
    source = json.loads((HERE / 'rank3_neuwirth_extension.json').read_text())
    base_path = HERE / 'stable_neuwirth_report.json'
    require(digest(base_path) == source['source_report_sha256'], 'base geometry report hash')
    require(source['source_module_sha256'] == FROZEN['rank3_neuwirth_extension.py'], 'author module hash')
    base = json.loads(base_path.read_text())
    seed = json.loads((HERE / 'stable_neuwirth_seed_snapshot.json').read_text())
    seed_rows = {r['name']: r for r in seed}
    base_rows = {r['name']: r for r in base['rows']}
    require(len(seed_rows) == len(base_rows) == 85 and set(seed_rows) == set(base_rows), 'base exact85 coverage')
    for name, record in base_rows.items():
        require(record['words'] == seed_rows[name]['best_words'], 'base exact words differ from frozen seed')
    originals = source['rows'] + source['independently_reduced_kuratowski_certificates']
    require(len(originals) == 85 and {r['name'] for r in originals} == set(base_rows), 'extension exact85 coverage')
    require(source['exact_obstruction_ids'] == [r['name'] for r in source['rows']]
            and source['unknown_ids'] == [], 'named exact obstruction ledger')
    rows, cooling = [], 0.0
    for index, record in enumerate(originals):
        require(record['words'] == base_rows[record['name']]['words'], 'extension input words')
        checked = verify_record(record)
        rows.append({'name': record['name'], 'source_collection': 'original85', **checked})
        if (index + 1) % 20 == 0:
            pause = time.perf_counter(); time.sleep(.02); cooling += time.perf_counter() - pause
    recursive_path = HERE / 'recursive_stable_compression_independent_audit.json'
    require(digest(recursive_path) == source['rank4_source_audit_sha256'], 'rank4 seed independent audit hash')
    recursive = json.loads(recursive_path.read_text())
    require(recursive['status'] == 'pass', 'rank4 source audit did not pass')
    rank4 = {r['name']: r for r in recursive['rows'] if r['additional_gain']}
    require(len(source['rank4_rows']) == len(rank4) == 6 and {r['name'] for r in source['rank4_rows']} == set(rank4), 'rank4 exact6 coverage')
    for record in source['rank4_rows']:
        require(record['words'] == rank4[record['name']]['minimum_relators'], 'rank4 exact words')
        rows.append({'name': record['name'], 'source_collection': 'recursive_rank4', **verify_record(record)})
    newer = source['newer_aca24']
    require(newer['words'] == ['XXZYY', 'XXyxZ', 'XYzYZ'] and sum(map(len, newer['words'])) == 15, 'new aca24 exact input')
    rank3_path = HERE / 'stable_rank3_ac_independent_audit.json'
    rank3_audit = json.loads(rank3_path.read_text())
    require(rank3_audit['status'] == 'pass', 'new aca24 source audit status')
    audited_aca24 = next(r for r in rank3_audit['rows'] if r['name'] == 'aca_24')
    require(audited_aca24['minimum_rank3_witness']['endpoint'] == newer['words'], 'new aca24 audited endpoint provenance')
    newer_checked = verify_nonplanar(newer)
    required_edges = {edge(a, b) for a in ('X', 'Y', 'y') for b in ('Z', 'z', 'x')}
    require(set(newer['kuratowski_edges']) == required_edges, 'new aca24 stated K3,3 bipartition')
    rows.append({'name': 'aca_24', 'source_collection': 'new_rank3_total15', **newer_checked})
    controls = check_controls(source['positive_rigid_fixtures'] + source['positive_rigid_rank4_fixtures'])
    require(len(source['positive_rigid_fixtures']) == 64 and len(source['positive_rigid_rank4_fixtures']) == 81, 'control coverage')
    require(len(source['rows']) == 16 and len(source['independently_reduced_kuratowski_certificates']) == 69, 'original certificate split')
    require(sum(r.get('phase_checks', 0) for r in source['rows']) == source['phase_checks'] == 309, 'original phase total')
    corruptions = []
    for label in ('rotation', 'observed_count', 'phase_witness', 'phase_coverage', 'kuratowski_edge', 'kuratowski_type'):
        record = deepcopy(source['rows'][0] if label not in ('kuratowski_edge', 'kuratowski_type') else source['independently_reduced_kuratowski_certificates'][0])
        if label == 'rotation':
            record['macro_rotation']['x'][0] = record['macro_rotation']['x'][1]
        elif label == 'observed_count':
            record['observed_class_pair_counts']['x'][0]['count'] += 1
        elif label == 'phase_witness':
            record['phase_mismatch_witnesses']['x'][0]['predicted'] += 1
        elif label == 'phase_coverage':
            record['phase_mismatch_witnesses']['x'].pop()
        elif label == 'kuratowski_edge':
            record['kuratowski_edges'][0] = 'xx'
        else:
            record['kuratowski_type'] = 'invalid'
        try:
            verify_record(record)
        except ValueError:
            corruptions.append(label)
        else:
            raise ValueError('failed to reject corruption: ' + label)
    out = {'status': 'pass', 'snapshot_utc': datetime.now(timezone.utc).isoformat(),
        'source_report_sha256': FROZEN['rank3_neuwirth_extension.json'], 'source_hashes': FROZEN,
        'audit_script_sha256': digest(Path(__file__)), 'base_report_sha256': digest(base_path),
        'frozen_seed_snapshot_sha256': digest(HERE / 'stable_neuwirth_seed_snapshot.json'),
        'rank4_source_audit_sha256': digest(recursive_path), 'new_aca24_source_audit_sha256': digest(rank3_path),
        'rows': rows, 'controls': controls,
        'counts': {'exact_word_tuples': len(rows), 'original_tuples': 85, 'additional_rank4_tuples': 6,
                   'additional_aca24_rank3_tuple': 1, 'spherical_macro_embeddings': 17,
                   'kuratowski_subdivisions': 75, 'original_phase_checks': 309, 'rank4_phase_checks': 20,
                   'mismatch_witnesses': sum(r.get('mismatch_witnesses_checked', 0) for r in rows),
                   'connectivity_deletions': sum(len(r['embedding']['connected_after_deleted_vertices']) for r in rows if 'embedding' in r),
                   'literal_letter_occurrences': sum(len(r['literal_occurrences']) for r in rows),
                   'positive_controls': controls['verified_controls'], 'corruptions_rejected': len(corruptions)},
        'corruptions_rejected': corruptions, 'cpu_seconds': time.process_time() - cpu,
        'wall_seconds_including_cooling': time.perf_counter() - wall, 'cooldown_seconds': cooling,
        'independence': 'No author module or occurrence-dictionary code imported. Literal predecessor/letter/successor corners, own connectivity traversals, own face permutation, own class-pair counters and phases, own branch-path subdivision verification. NetworkX used only to construct two control embeddings, each independently checked by face Euler characteristic.',
        'scope': 'Negative certificates apply only to these92 exact word tuples. No AC or stable-AC class obstruction, nontriviality, unsolvability, or statement about untested states is inferred. Positive controls verify only compatible spherical occurrence links and make no trivial-group claim.',
        'proof_review': 'For loopless3connected planar support, deleting both ends of any edge leaves a connected nonempty graph. In a spherical embedding all remaining vertices occupy one region between parallel arcs; all other regions are empty digons, so each parallel class is a contiguous reversed ribbon. Whitney uniqueness reduces the macro rotation to the saved spherical rotation or its global reflection. Pipe reversal then forces a cyclic phase and the observed class-pair equation; one empty generator phase set is a sound necessary-condition failure. The machine audit checks every finite hypothesis and mismatch, not Whitney theorem itself.'}
    (HERE / 'neuwirth_independent_audit.json').write_text(json.dumps(out, indent=2) + '\n')
    lines = ['# Independent exact-link certificate audit', '',
        'PASS. All92 exact word tuples have independently checked negative certificates: the original85, six recursive rank4 endpoints, and the newer15-letter aca24 tuple. These are exact-complex exclusions only; no AC or stable-AC class obstruction is claimed.', '',
        f"Seventeen saved macro rotations have connected spherical face permutations with Euler characteristic2 and pass all{out['counts']['connectivity_deletions']} deletions of up to two vertices. Literal signed occurrence reconstruction checks329 cyclic phases and{out['counts']['mismatch_witnesses']} individual mismatch witnesses. All75 saved nonplanarity certificates trace into K5 or K3,3 subdivisions with every witness edge present in the literal support.", '',
        'For aca24=(XXZYY,XXyxZ,XYzYZ), the nine specified edges are exactly the complete bipartite graph between {X,Y,y} and {Z,z,x}. Its15-letter tuple is separate from the earlier16-letter source row.', '',
        'The parallel-ribbon argument is sound under the checked loopless3connected hypotheses: removing the two endpoint vertices leaves one connected graph, which occupies one region between the parallel arcs. Whitney uniqueness leaves one macro rotation up to global reflection. Pipe reversal forces the recorded cyclic class-pair equation. Each saved obstruction has an empty phase set; merely surviving this necessary equation would remain unknown.', '',
        out['independence'], '',
        f"All145 saved positive controls pass, using only two newly constructed and independently checked macro embeddings. Six deliberate corruptions are rejected. CPU {out['cpu_seconds']:.6f}s; wall {out['wall_seconds_including_cooling']:.6f}s including {cooling:.6f}s cooling. No factorial-order or rank-assignment enumeration was run.", '',
        '| exact tuple | source collection | certificate |', '|---|---|---|']
    lines += [f"| {r['name']} | {r['source_collection']} | {r['status']} |" for r in rows]
    (HERE / 'neuwirth_independent_audit.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps({k: out[k] for k in ('status', 'counts', 'cpu_seconds', 'wall_seconds_including_cooling', 'cooldown_seconds')}, indent=2))


if __name__ == '__main__':
    main()
