"""Benchmark: does retained-rank triangular expansion make hard AC19 rows easier?

Panels are the frozen ones from ``research/ac19_triangle_expansion_20260912``:
four hard-but-solved rows (each exhausted plain greedy at 100,000 nodes and
later acquired a replayable certificate) and the twelve easy controls.

Every run reports *all* work: the triangulation preprocessing charge, the heap
pops, the rotation products formed, and the states discovered.  Triangulation is
preprocessing, never a solve: a run counts as exposing structure only when it
reaches a relator of length two (bigon) or one (unit) at unchanged rank.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path[:0] = [str(HERE), str(ROOT / 'research/rank_unbounded_20260912'),
                str(ROOT / 'research/u124_high_rank_ac_20260912'),
                str(ROOT / 'research/u124_rank_3h_20260912')]

import search                                   # noqa: E402
import theory                                   # noqa: E402
import coupling_search                          # noqa: E402
from high_rank_triangles import triangulate     # noqa: E402

PANEL = ROOT / 'research/ac19_triangle_expansion_20260912/hard_solved_panel.jsonl'
EASY = ROOT / 'research/ac19_triangle_expansion_20260912/easy_control_panel.jsonl'
LETTERS = {'x': 1, 'X': -1, 'y': 2, 'Y': -2}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def parse_pair(r1, r2):
    return (tuple(LETTERS[c] for c in r1), tuple(LETTERS[c] for c in r2))


def load_rows():
    hard = [json.loads(line) for line in PANEL.read_text().splitlines()]
    easy = [json.loads(line) for line in EASY.read_text().splitlines()]
    rows = [{'name': r['name'], 'panel': 'hard', 'pair': (r['r1'], r['r2'])} for r in hard]
    rows += [{'name': r['name'], 'panel': 'easy', 'pair': tuple(r['pair'])} for r in easy]
    return rows


def run(caps, pop_budget, beam, orderings):
    rows = load_rows()
    out = []
    for row in rows:
        rank2 = search.normalize(parse_pair(*row['pair']))
        cpu, wall = time.process_time(), time.perf_counter()
        tri, events, prep_units = triangulate(rank2)
        prep_cpu = time.process_time() - cpu
        prep_wall = time.perf_counter() - wall
        base = {
            'name': row['name'], 'panel': row['panel'],
            'rank2_pair': row['pair'], 'rank2_length': search.length(rank2),
            'triangle_state': tri, 'rank': len(tri),
            'triangle_length': search.length(tri),
            'definitions': len(events),
            'preprocessing_units': prep_units,
            'preprocessing_cpu_seconds': prep_cpu,
            'preprocessing_wall_seconds': prep_wall,
            'root_digram_disjoint': theory.is_digram_disjoint(tri),
            'root_coupling': theory.coupling(tri),
            'all_relators_at_most_three': not any(len(w) > 3 for w in tri),
            'arms': [],
        }
        for cap in caps:
            for ordering in orderings:
                cpu, wall = time.process_time(), time.perf_counter()
                res = coupling_search.search_row(
                    tri, ordering=ordering, pop_budget=pop_budget,
                    relator_cap=cap, beam=beam, stop_on_bigon=False)
                res['cpu_seconds'] = time.process_time() - cpu
                res['wall_seconds'] = time.perf_counter() - wall
                res.pop('initial', None)
                base['arms'].append(res)
        out.append(base)
        marks = ''.join('U' if a['unit_found'] else ('B' if a['bigon_found'] else '.')
                        for a in base['arms'])
        print(f"{row['name']:14s} {row['panel']:5s} rank {base['rank']:2d} "
              f"disjoint {str(base['root_digram_disjoint']):5s} arms[{marks}]", flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--caps', default='4,5,6')
    ap.add_argument('--pops', type=int, default=200)
    ap.add_argument('--beam', type=int, default=64)
    ap.add_argument('--orderings', default='coupling,structural')
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    caps = [int(c) for c in args.caps.split(',')]
    orderings = args.orderings.split(',')
    output = Path(args.out)
    if output.exists():
        raise SystemExit('refusing to overwrite ' + str(output))
    started = time.perf_counter()
    rows = run(caps, args.pops, args.beam, orderings)
    report = {
        'schema': 'ac19_triangle_coupling_benchmark_v1',
        'panel_sha256': sha(PANEL), 'easy_sha256': sha(EASY),
        'theory_sha256': sha(HERE / 'theory.py'),
        'search_sha256': sha(HERE / 'coupling_search.py'),
        'script_sha256': sha(Path(__file__)),
        'parameters': {'caps': caps, 'pop_budget': args.pops, 'beam': args.beam,
                       'orderings': orderings},
        'summary': {
            'rows': len(rows),
            'hard_rows': sum(r['panel'] == 'hard' for r in rows),
            'easy_rows': sum(r['panel'] == 'easy' for r in rows),
            'roots_digram_disjoint': sum(r['root_digram_disjoint'] for r in rows),
            'hard_roots_digram_disjoint': sum(r['root_digram_disjoint'] for r in rows if r['panel'] == 'hard'),
            'rows_with_bigon': sum(any(a['bigon_found'] for a in r['arms']) for r in rows),
            'hard_rows_with_bigon': sum(any(a['bigon_found'] for a in r['arms']) for r in rows if r['panel'] == 'hard'),
            'rows_with_unit': sum(any(a['unit_found'] for a in r['arms']) for r in rows),
            'preprocessing_units': sum(r['preprocessing_units'] for r in rows),
            'rotation_products': sum(a['rotation_products'] for r in rows for a in r['arms']),
            'heap_pops': sum(a['heap_pops'] for r in rows for a in r['arms']),
            'discovered_states': sum(a['discovered_states'] for r in rows for a in r['arms']),
            'search_cpu_seconds': sum(a['cpu_seconds'] for r in rows for a in r['arms']),
            'total_wall_seconds': time.perf_counter() - started,
        },
        'scope': ('fixed-rank ordinary AC normal-product substitutions only; '
                  'triangulation counted as preprocessing, never as a solve'),
        'rows': rows,
    }
    output.write_text(json.dumps(report, indent=2, default=list) + '\n')
    print(json.dumps(report['summary'], indent=2))


if __name__ == '__main__':
    main()
