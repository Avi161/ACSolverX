"""Any-rank rigid-support block-count obstruction; no factorial rotation search."""
from collections import Counter, defaultdict
import hashlib
import itertools
import json
from pathlib import Path
import time
import networkx as nx
from . import snapshot_neuwirth_permutation_certificate as source

HERE = Path(__file__).resolve().parent


def build(words):
    data = source.OccurrenceData.from_words(tuple(words))
    germ = {}
    for g, ends in data.positive_ends.items():
        for e in ends:
            germ[e] = g
            germ[data.B[e]] = g.upper()
    classes = {}
    for e in range(len(data.A)):
        classes[e] = tuple(sorted((germ[e], germ[data.A[e]])))
    counts = Counter(classes[e] for e in range(len(data.A)) if e < data.A[e])
    # Separate cyclic-word corner convention, independent of source A/B.
    independent = Counter(tuple(sorted((a.swapcase(), b))) for w in words
                          for a,b in zip(w, w[1:]+w[:1]))
    assert counts == independent
    graph = nx.Graph()
    graph.add_nodes_from(germ.values())
    graph.add_edges_from(counts)
    return data, germ, classes, counts, graph


def verify_kuratowski(graph):
    adjacency = {v:set(graph[v]) for v in graph}
    while any(len(n) == 2 for n in adjacency.values()):
        v = next(v for v,n in adjacency.items() if len(n) == 2)
        a,b = sorted(adjacency.pop(v))
        adjacency[a].remove(v)
        adjacency[b].remove(v)
        assert b not in adjacency[a]
        adjacency[a].add(b)
        adjacency[b].add(a)
    if len(adjacency) == 5 and all(len(n) == 4 for n in adjacency.values()):
        return 'K5_subdivision'
    assert len(adjacency) == 6 and all(len(n) == 3 for n in adjacency.values())
    colors = {next(iter(adjacency)):0}
    stack = list(colors)
    while stack:
        v = stack.pop()
        for u in adjacency[v]:
            if u not in colors:
                colors[u] = 1-colors[v]
                stack.append(u)
            assert colors[u] != colors[v]
    assert len(colors) == 6 and sum(colors.values()) == 3
    return 'K33_subdivision'


def evaluate(words):
    data, germ, classes, counts, graph = build(words)
    planar, embedding = nx.check_planarity(graph, counterexample=True)
    common = {'words':list(words), 'simple_edges':[''.join(e) for e in sorted(counts)],
              'simple_edge_count':len(counts), 'loops':nx.number_of_selfloops(graph)}
    if not planar:
        return {**common, 'status':'nonplanar_support', 'complete':True,
                'kuratowski_type':verify_kuratowski(embedding),
                'kuratowski_edges':[''.join(sorted(e)) for e in sorted(embedding.edges())]}
    if len(graph) < 4 or len(graph) != 2*len(data.positive_ends) or common['loops'] or not nx.is_connected(graph):
        return {**common, 'status':'unsupported', 'complete':False}
    # Independently check every deletion of zero, one or two support vertices.
    cuts = [s for k in range(3) for s in itertools.combinations(sorted(graph), k)]
    connected_after_cuts = [nx.is_connected(graph.subgraph(set(graph)-set(s))) for s in cuts]
    if not all(connected_after_cuts):
        return {**common, 'status':'unsupported_connectivity', 'complete':False}
    embedding.check_structure()
    rotation = {v:list(embedding.neighbors_cw_order(v)) for v in sorted(graph)}
    blocks = {v:[tuple(sorted((v,u))) for u in rotation[v] for _ in range(counts[tuple(sorted((v,u)))])]
              for v in graph}
    phase_sets = {}
    observations = {}
    mismatches = {}
    phase_checks = 0
    for g, ends in data.positive_ends.items():
        actual = Counter((classes[e], classes[data.B[e]]) for e in ends)
        positive, negative = blocks[g], blocks[g.upper()]
        d = len(positive)
        assert d == len(negative) == len(ends)
        valid, rejected = [], []
        for s in range(d):
            phase_checks += 1
            predicted = Counter((positive[j], negative[(-j-s)%d]) for j in range(d))
            if predicted == actual:
                valid.append(s)
            else:
                key = next(k for k in sorted(set(predicted)|set(actual)) if predicted[k] != actual[k])
                rejected.append({'phase':s,'class_pair':[''.join(e) for e in key],
                                 'actual':actual[key],'predicted':predicted[key]})
        phase_sets[g] = valid
        observations[g] = [{'class_pair':[''.join(e) for e in key], 'count':value}
                           for key,value in sorted(actual.items())]
        mismatches[g] = rejected
    blockers = [g for g,phases in phase_sets.items() if not phases]
    return {**common, 'status':'rigid_block_count_obstruction' if blockers else 'unknown_after_block_counts',
            'complete':bool(blockers), 'connectivity_deletion_checks':len(cuts),
            'macro_rotation':rotation, 'phase_sets':phase_sets, 'blocking_generators':blockers,
            'phase_checks':phase_checks, 'observed_class_pair_counts':observations,
            'phase_mismatch_witnesses':mismatches}


def positive_fixtures(rank=3):
    generators = 'xyz' if rank == 3 else 'xyzu'
    vertices = tuple(c for g in generators for c in (g,g.upper()))
    if rank == 3:
        graph = nx.Graph()
        graph.add_nodes_from(vertices)
        graph.add_edges_from((a,b) for a,b in itertools.combinations(vertices,2)
                             if a.swapcase() != b)
    else:
        graph = nx.relabel_nodes(nx.cubical_graph(),dict(enumerate(vertices)))
    planar, embedding = nx.check_planarity(graph)
    assert planar
    rotations = {v:[(v,u) for u in embedding.neighbors_cw_order(v)] for v in vertices}
    fixtures = []
    degree = len(rotations[generators[0]])
    for phases in itertools.product(range(degree), repeat=rank):
        B = {}
        for g,s in zip(generators,phases):
            for i,dart in enumerate(rotations[g]):
                mate = rotations[g.upper()][(-i-s)%degree]
                B[dart] = mate
                B[mate] = dart
        seen, words = set(), []
        for start in sorted(B):
            if start in seen:
                continue
            dart, letters = start, []
            while dart not in seen:
                letters.append(dart[0])
                seen.add(dart)
                seen.add(B[dart])
                dart = tuple(reversed(B[dart]))
            assert dart == start
            words.append(''.join(letters))
        result = evaluate(words)
        assert result['status'] == 'unknown_after_block_counts', (words,result)
        fixtures.append(words)
    return fixtures


def reflection_check(result):
    if 'macro_rotation' not in result:
        return
    _,_,_,counts,_ = build(result['words'])
    rotation = {v:list(reversed(order)) for v,order in result['macro_rotation'].items()}
    blocks = {v:[tuple(sorted((v,u))) for u in rotation[v] for _ in range(counts[tuple(sorted((v,u)))])]
              for v in rotation}
    for g,rows in result['observed_class_pair_counts'].items():
        actual = Counter({tuple(tuple(e) for e in r['class_pair']):r['count'] for r in rows})
        d = len(blocks[g])
        reflected = []
        for s in range(d):
            predicted = Counter((blocks[g][j],blocks[g.upper()][(-j-s)%d]) for j in range(d))
            if predicted == actual:
                reflected.append(s)
        assert bool(reflected) == bool(result['phase_sets'][g])


def main():
    start = time.process_time()
    report_path = HERE/'stable_neuwirth_report.json'
    raw = json.loads(report_path.read_text())
    rows = []
    nonplanar = []
    fixtures = positive_fixtures()
    rank4_fixtures = positive_fixtures(4)
    for r in raw['rows']:
        result = evaluate(r['words'])
        assert (result['status'] == 'nonplanar_support') == (r['status'] == 'nonplanar_link')
        reflection_check(result)
        if result['status'] == 'nonplanar_support':
            nonplanar.append({'name':r['name'], **result})
        if not r['complete']:
            rows.append({'name':r['name'],**result})
    recursive_path = HERE/'recursive_stable_compression_independent_audit.json'
    recursive = json.loads(recursive_path.read_text())
    rank4_rows = [{'name':r['name'], **evaluate(r['minimum_relators'])} for r in recursive['rows'] if r['additional_gain']]
    for r in rank4_rows:
        reflection_check(r)
    newer_aca24 = evaluate(['XXZYY','XXyxZ','XYzYZ'])
    output = {'status':'rigid_support_block_count_necessary_test', 'rows':rows,
              'rank4_rows':rank4_rows, 'rank4_source_audit_sha256':hashlib.sha256(recursive_path.read_bytes()).hexdigest(),
              'newer_aca24':newer_aca24,
              'source_report_sha256':hashlib.sha256(report_path.read_bytes()).hexdigest(),
              'source_module_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'source_corner_dictionaries_checked':len(raw['rows']),
              'independently_reduced_kuratowski_certificates':nonplanar,
              'positive_rigid_fixtures':fixtures,
              'positive_rigid_rank4_fixtures':rank4_fixtures, 'rank4_reflection_checks':sum('macro_rotation' in r for r in rank4_rows),
              'reflection_checks':len(rows),
              'exact_obstruction_ids':[r['name'] for r in rows if r['complete']],
              'unknown_ids':[r['name'] for r in rows if not r['complete']],
              'phase_checks':sum(r.get('phase_checks',0) for r in rows),
              'cpu_seconds':time.process_time()-start}
    (HERE/'rank3_neuwirth_extension.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({k:v for k,v in output.items() if k not in ('rows','rank4_rows','newer_aca24','independently_reduced_kuratowski_certificates','positive_rigid_fixtures','positive_rigid_rank4_fixtures')},indent=2))


if __name__ == '__main__':
    main()
