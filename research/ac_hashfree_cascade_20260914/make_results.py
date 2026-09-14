"""Summarise run_census.py records into markdown tables (stdout)."""
from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(path):
    return [json.loads(line) for line in open(path)]


def quantiles(values, qs=(0, 0.25, 0.5, 0.75, 0.9, 1.0)):
    v = sorted(values)
    if not v:
        return ['-'] * len(qs)
    return [v[min(len(v) - 1, int(q * (len(v) - 1)))] for q in qs]


def summarise(name, rows):
    solved = [r for r in rows if r['solved']]
    stages = Counter(r['stage'] for r in solved)
    line = dict(run=name, rows=len(rows), solved=len(solved),
                verified=sum(1 for r in solved if r.get('verified')),
                le100=sum(1 for r in solved if r['units'] <= 100),
                le300=sum(1 for r in solved if r['units'] <= 300),
                stages=' '.join('%s:%d' % (k, stages[k]) for k in ('A', 'B', 'C', 'D') if stages[k]),
                units_q=quantiles([r['units'] for r in solved]),
                path_q=quantiles([r['path_length'] for r in solved]),
                maxrel_q=quantiles([r['max_relator'] for r in solved]),
                seconds=sum(r['seconds'] for r in rows))
    return line


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('records', nargs='+')
    ap.add_argument('--census-solved', help='optional: policy unsolved.csv to cross-tabulate')
    args = ap.parse_args()
    print('| run | rows | solved | verified | <=100 | <=300 | stage of solve | units q(0,25,50,75,90,100) | path q | max relator q | wall s |')
    print('|---|---:|---:|---:|---:|---:|---|---|---|---|---:|')
    for path in args.records:
        rows = load(path)
        s = summarise(Path(path).stem, rows)
        print('| %s | %d | %d | %d | %d | %d | %s | %s | %s | %s | %.0f |' % (
            s['run'], s['rows'], s['solved'], s['verified'], s['le100'], s['le300'], s['stages'],
            ' '.join(map(str, s['units_q'])), ' '.join(map(str, s['path_q'])),
            ' '.join(map(str, s['maxrel_q'])), s['seconds']))


if __name__ == '__main__':
    main()
