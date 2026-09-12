"""Independent maximum-flow and handwritten unit-path sharpness certificates."""
from collections import Counter
import json
from pathlib import Path
import verify as v

HERE = Path(__file__).resolve().parent


def main():
    score_path = HERE / 'exchange_rank4_sharp_aut.json'
    score = json.loads(score_path.read_text())
    v.require(v.sha(HERE / score['source']) == score['source_sha256'], 'sharp score source changed')
    v.require(score['before'] == score['after'] and score['events'] == [] and score['charged_units'] == 8, 'sharp score boundary differs')
    v.coupled_whitehead_metadata(score)
    flow_path = HERE / 'exchange_rank4_sharp_flows.json'
    flow = json.loads(flow_path.read_text())
    v.require(v.sha(HERE / flow['source']) == flow['source_sha256'], 'sharp unit-path source changed')
    edges = Counter()
    for row in score['before']:
        for i, x in enumerate(row):
            edges[tuple(sorted((x, -row[(i + 1) % len(row)])))] += 1
    v.require(dict(edges) == {tuple(r['edge']): r['capacity'] for r in flow['capacities']}, 'handwritten graph differs')
    basis = {abs(x) for row in score['before'] for x in row}
    v.require({r['source'] for r in flow['unit_paths']} == basis and len(flow['unit_paths']) == 4, 'unit-path sources incomplete')
    count = 0
    for family in flow['unit_paths']:
        source, sink = family['source'], family['sink']
        v.require(sink == -source, 'unit-path sink differs')
        used = Counter()
        for path in family['paths']:
            v.require(path[0] == source and path[-1] == sink and len(path) == len(set(path)), 'invalid unit path')
            used.update(tuple(sorted((a, b))) for a, b in zip(path, path[1:]))
            count += 1
        degree = sum(capacity for edge, capacity in edges.items() if source in edge)
        v.require(len(family['paths']) == family['value'] == degree and all(used[edge] <= edges[edge] for edge in used), 'unit-path capacity proof differs')
    output = {'status': 'PASS', 'independent_signed_minimum_cuts': 8,
              'all_deltas': [r['delta'] for r in score['coupled_whitehead_score']['signed_multipliers']],
              'whole_Aut_minimum_length': 16, 'handwritten_unit_paths_checked': count,
              'unit_path_values': [r['value'] for r in flow['unit_paths']],
              'source_hashes': {path.name: v.sha(path) for path in (score_path, flow_path)},
              'scope': 'Both an independent dense flow oracle and16 explicit unit paths certify the minimum cut values. Reverse paths handle negative multipliers. Whitehead length reduction gives whole-Aut minimality; the separate ordinary AC escape remains available.'}
    (HERE / 'verification_sharp_rank4_aut.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
