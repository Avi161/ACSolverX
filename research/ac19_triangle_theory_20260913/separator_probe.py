"""Can rank-raising separate solved-but-hard MS rows from the unsolved U124 cheaply?

Both groups go through the identical pipeline: rank-two pair -> greedy
triangulation -> static root features -> a small coupling search (cap 5, 30 pops).
Groups: the 60-row solved MS benchmark ladder (difficulty bins 0-9, from the
1,000,000-node greedy campaign) and the 124 unsolved U124 representatives.
For every feature the report gives the AUC of "U124 vs solved bins 6-9" and
"U124 vs all solved": 0.5 is no separation, 1.0 (or 0.0) is perfect.
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path[:0] = [str(HERE), str(ROOT / 'research/rank_unbounded_20260912'),
                str(ROOT / 'research/u124_high_rank_ac_20260912'),
                str(ROOT / 'research/u124_rank_3h_20260912')]

import search                                   # noqa: E402
import theory                                   # noqa: E402
import coupling_search                          # noqa: E402
from high_rank_triangles import triangulate     # noqa: E402

SUBSET = ROOT / 'benchmark/subsets/benchmark_subset_60.csv'
U124 = ROOT / 'data/ms_unsolved_reps/aca_124_best.csv'
LETTERS = {'x': 1, 'X': -1, 'y': 2, 'Y': -2}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def features(r1, r2, pops, cap, beam):
    pair = search.normalize((tuple(LETTERS[c] for c in r1), tuple(LETTERS[c] for c in r2)))
    tri, events, used = triangulate(pair)
    kids, attempted = theory.one_step_products(tri, relator_cap=4)
    pairs, total = theory.coupling(tri)
    res = coupling_search.search_row(tri, ordering='coupling', pop_budget=pops,
                                     relator_cap=cap, beam=beam, stop_on_bigon=True)
    return {
        'rank2_length': search.length(pair),
        'rank': len(tri), 'definitions': len(events), 'prep_units': used,
        'root_min_relator': min(map(len, tri)),
        'root_all_triangle': int(all(len(w) == 3 for w in tri)),
        'root_digram_disjoint': int(theory.is_digram_disjoint(tri)),
        'root_coupling_pairs': pairs, 'root_coupling_digrams': total,
        'cap4_children': len(kids), 'cap4_distinct_quartics': len({k[-1] for k in kids if len(k[-1]) == 4}),
        'search_bigon': int(res['bigon_found']), 'search_unit': int(res['unit_found']),
        'search_best_coupling_pairs': res['best_coupling_pairs'],
        'search_states': res['discovered_states'], 'search_pops': res['heap_pops'],
        'search_rotation_products': res['rotation_products'],
        'search_shortest_relator': res['shortest_relator_seen'],
    }


def auc(pos, neg):
    """P(score(pos) > score(neg)) + 0.5 P(equal), by counting."""
    if not pos or not neg:
        return None
    wins = ties = 0
    for p in pos:
        for n in neg:
            wins += p > n
            ties += p == n
    return (wins + 0.5 * ties) / (len(pos) * len(neg))


def main():
    pops, cap, beam = 30, 5, 32
    out = HERE / 'separator_probe.json'
    if out.exists():
        raise SystemExit('refusing to overwrite ' + str(out))
    rows = []
    t0 = time.perf_counter()
    with SUBSET.open(newline='') as f:
        for r in csv.DictReader(f):
            rows.append({'group': 'solved', 'name': 'ms640_' + r['pres_id'], 'bin': int(r['bin']),
                         'nodes_1M': int(r['nodes_1M']), 'r1': r['r1'], 'r2': r['r2']})
    with U124.open(newline='') as f:
        for r in csv.DictReader(f):
            rows.append({'group': 'u124', 'name': r['name'], 'bin': None, 'nodes_1M': None,
                         'r1': r['r1'], 'r2': r['r2']})
    for row in rows:
        cpu = time.process_time()
        row.update(features(row['r1'], row['r2'], pops, cap, beam))
        row['cpu_seconds'] = time.process_time() - cpu
        print(f"{row['name']:12s} {row['group']:6s} bin {str(row['bin']):4s} rank {row['rank']:2d} "
              f"disj {row['root_digram_disjoint']} minrel {row['root_min_relator']} "
              f"B {row['search_bigon']} U {row['search_unit']} coup {row['search_best_coupling_pairs']}", flush=True)
    feats = [k for k in rows[0] if isinstance(rows[0][k], (int, float)) and k not in ('bin', 'nodes_1M', 'cpu_seconds')]
    u = [r for r in rows if r['group'] == 'u124']
    s_all = [r for r in rows if r['group'] == 'solved']
    s_hard = [r for r in s_all if r['bin'] >= 6]
    table = []
    for k in feats:
        table.append({'feature': k,
                      'auc_u124_vs_solved_hard': auc([r[k] for r in u], [r[k] for r in s_hard]),
                      'auc_u124_vs_solved_all': auc([r[k] for r in u], [r[k] for r in s_all]),
                      'mean_u124': sum(r[k] for r in u) / len(u),
                      'mean_solved_hard': sum(r[k] for r in s_hard) / len(s_hard),
                      'mean_solved_all': sum(r[k] for r in s_all) / len(s_all)})
    report = {'schema': 'triangle_separator_probe_v1',
              'subset_sha256': sha(SUBSET), 'u124_sha256': sha(U124),
              'parameters': {'pops': pops, 'cap': cap, 'beam': beam},
              'counts': {'u124': len(u), 'solved_all': len(s_all), 'solved_hard_bins_6_9': len(s_hard)},
              'wall_seconds': time.perf_counter() - t0,
              'separability': table, 'rows': rows}
    out.write_text(json.dumps(report, indent=2) + '\n')
    print()
    print(f"{'feature':32s} {'AUC vs hard':>12s} {'AUC vs all':>11s} {'mean U124':>10s} {'mean hard':>10s} {'mean all':>9s}")
    for t in table:
        print(f"{t['feature']:32s} {t['auc_u124_vs_solved_hard']:12.3f} {t['auc_u124_vs_solved_all']:11.3f} "
              f"{t['mean_u124']:10.2f} {t['mean_solved_hard']:10.2f} {t['mean_solved_all']:9.2f}")


if __name__ == '__main__':
    main()
