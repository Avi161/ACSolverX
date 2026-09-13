"""How often does greedy triangulation of an AC19 row give a digram-disjoint root?

Samples rows of ``data/AC19_extended_aut_min.csv`` with a fixed seed, triangulates
each, and records whether the root is digram-disjoint, its rank, and the one-step
product length histogram (which by Lemma 1 must contain only even lengths and,
at a digram-disjoint root, no length two).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path[:0] = [str(HERE), str(ROOT / 'research/rank_unbounded_20260912'),
                str(ROOT / 'research/u124_rank_3h_20260912')]

import search                                   # noqa: E402
import theory                                   # noqa: E402
from high_rank_triangles import triangulate     # noqa: E402

AC19 = ROOT / 'data/AC19_extended_aut_min.csv'
LETTERS = {'x': 1, 'X': -1, 'y': 2, 'Y': -2}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sample', type=int, default=400)
    ap.add_argument('--seed', type=int, default=3)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    out = Path(args.out)
    if out.exists():
        raise SystemExit('refusing to overwrite ' + str(out))
    with AC19.open(newline='') as stream:
        rows = list(csv.DictReader(stream))
    random.seed(args.seed)
    sample = random.sample(rows, args.sample)
    records, disjoint, ranks, hist = [], 0, Counter(), Counter()
    all_triangle_count = short_root = 0
    for row in sample:
        state = search.normalize((tuple(LETTERS[c] for c in row['r1']),
                                  tuple(LETTERS[c] for c in row['r2'])))
        tri, events, used = triangulate(state)
        if any(len(w) > 3 for w in tri):
            records.append({'name': row['name'], 'triangulated': False})
            continue
        products, attempted = theory.one_step_products(tri, relator_cap=6)
        lengths = Counter(len(p[-1]) for p in products)
        all_triangle = all(len(w) == 3 for w in tri)
        dd = theory.is_digram_disjoint(tri)
        if all_triangle:
            # Lemma 1 and Lemma 2 are statements about all-triangle states only.
            assert all(n % 2 == 0 for n in lengths), 'parity lemma violated'
            if dd:
                assert 2 not in lengths, 'Lemma 2 violated'
            all_triangle_count += 1
            disjoint += dd
        else:
            short_root += 1
        ranks[len(tri)] += 1
        hist.update(lengths)
        records.append({'name': row['name'], 'triangulated': True, 'rank': len(tri),
                        'definitions': len(events), 'preprocessing_units': used,
                        'all_triangle': all_triangle,
                        'shortest_root_relator': min(map(len, tri)),
                        'digram_disjoint': dd, 'shared_pairs': theory.coupling(tri)[0],
                        'one_step_length_histogram': dict(sorted(lengths.items())),
                        'rotation_products': attempted})
    triangulated = sum(r['triangulated'] for r in records)
    report = {
        'schema': 'ac19_triangulation_digram_census_v1',
        'ac19_sha256': hashlib.sha256(AC19.read_bytes()).hexdigest(),
        'theory_sha256': hashlib.sha256((HERE / 'theory.py').read_bytes()).hexdigest(),
        'parameters': {'sample': args.sample, 'seed': args.seed},
        'summary': {'sampled': len(sample), 'triangulated': triangulated,
                    'all_triangle_roots': all_triangle_count,
                    'roots_with_a_relator_shorter_than_three': short_root,
                    'all_triangle_and_digram_disjoint': disjoint,
                    'rank_histogram': dict(sorted(ranks.items())),
                    'one_step_length_histogram': dict(sorted(hist.items()))},
        'rows': records,
    }
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report['summary'], indent=2))


if __name__ == '__main__':
    main()
