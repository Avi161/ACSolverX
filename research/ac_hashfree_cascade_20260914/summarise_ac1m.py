"""Statistics of the AC1M runs (Aut-minimal representatives and raw rows) at 1,000 units.

    python3 research/ac_hashfree_cascade_20260914/summarise_ac1m.py
"""
from __future__ import annotations

import collections
import csv
import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
R = HERE / 'records'


def load(path):
    with gzip.open(path, 'rt') as f:
        return [json.loads(l) for l in f]


def stats(recs):
    n = len(recs)
    units = sorted(r['units'] for r in recs)
    solved = [r for r in recs if r['solved']]
    out = dict(rows=n, solved=len(solved), verified=sum(1 for r in recs if r.get('verified')),
               unsolved=[r['name'] for r in recs if not r['solved']][:50],
               units_median=units[n // 2], units_p99=units[int(0.99 * n)], units_p999=units[int(0.999 * n)],
               units_max=units[-1], rows_over_500=sum(1 for u in units if u > 500),
               stages=dict(collections.Counter(r['stage'] for r in recs)),
               rank_two=sum(1 for r in solved if r['explicit_rank2']),
               stable=sum(1 for r in solved if r['explicit_rank2'] is False),
               max_rank=dict(collections.Counter(str(r.get('max_rank')) for r in solved)),
               search_seconds=round(sum(r['seconds'] for r in recs), 1),
               seconds_max=round(max(r['seconds'] for r in recs), 3))
    by_len = collections.defaultdict(lambda: [0, 0, 0])
    for r in recs:
        b = by_len[r['length']]
        b[0] += 1
        b[1] += r['solved']
        b[2] = max(b[2], r['units'])
    out['by_length (rows, solved, max units)'] = {k: v for k, v in sorted(by_len.items())}
    return out


def main():
    report = {}
    reps = load(R / 'final3_ac1m_reps.jsonl.gz')
    report['aut_min_reps'] = stats(reps)
    raw_path = R / 'final3_ac1m_raw.jsonl.gz'
    if raw_path.exists():
        raw = load(raw_path)
        report['raw_rows'] = stats(raw)
        # link raw rows to their orbit's representative
        rep_of = {}
        with gzip.open(ROOT / 'research/ac1m_autmin_20260914/records/AC1M_aut_min.csv.gz', 'rt') as f:
            for row in csv.DictReader(f):
                for m in row['members'].split():
                    rep_of[int(m)] = row['name']
        rep_rec = {r['name']: r for r in reps}
        raw_stable = [r for r in raw if r['solved'] and r['explicit_rank2'] is False]
        stable_rep_orbits = {r['name'] for r in reps if r['solved'] and r['explicit_rank2'] is False}
        report['raw_vs_reps'] = dict(
            raw_stable_rows=len(raw_stable),
            raw_stable_rows_whose_rep_is_stable=sum(1 for r in raw_stable if rep_of[int(r['name'].rsplit('_', 1)[1])] in stable_rep_orbits),
            rows_in_orbits_with_stable_rep=sum(1 for r in raw if rep_of[int(r['name'].rsplit('_', 1)[1])] in stable_rep_orbits),
            unsolved_raw_rows=[(r['name'], rep_of[int(r['name'].rsplit('_', 1)[1])],
                                rep_rec[rep_of[int(r['name'].rsplit('_', 1)[1])]]['solved'])
                               for r in raw if not r['solved']][:50])
    (R / 'ac1m_summary_stats.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
