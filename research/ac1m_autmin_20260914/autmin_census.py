"""Aut(F2)-minimal census of a presentation file: one row per Aut-orbit.

Reads a flat integer file (one presentation per line, 2k slots = two relators of k
slots, letters 1/-1/2/-2 = x/X/y/Y, 0 = padding; `.gz` accepted), canonicalises every
row with `autcanon_fast.aut_min` (Whitehead peak reduction, then the lex-min of the
BFS-closed minimal level set: a complete invariant of the Aut(F2)-orbit, the same
function that built `data/AC19_extended_aut_min.csv`) and writes a CSV in that file's
schema: name,r1,r2,n_members,members (0-based line indices), plus a summary JSON with
the distribution of the Aut-minimal total length `mu`.

    python3 research/ac1m_autmin_20260914/autmin_census.py data/AC1M.txt.gz --prefix ac1m \
        --out research/ac1m_autmin_20260914/records/AC1M_aut_min.csv.gz
"""
from __future__ import annotations

import argparse
import collections
import csv
import gzip
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

LETTER = {1: 'x', -1: 'X', 2: 'y', -2: 'Y'}


def line_to_pair(line):
    v = [int(t) for t in line.strip().strip('()[]').split(',') if t.strip()]
    h = len(v) // 2
    assert 2 * h == len(v), len(v)
    return ''.join(LETTER[t] for t in v[:h] if t), ''.join(LETTER[t] for t in v[h:] if t)


def _init():
    global aut_min
    from experiments.stable_ac.cov.ladder.autcanon_fast import aut_min, warm
    warm()


def job(chunk):
    out = []
    for index, line in chunk:
        pair = line_to_pair(line)
        try:
            mu, rep = aut_min(pair)
            out.append((index, len(pair[0]) + len(pair[1]), mu, rep[0], rep[1]))
        except RuntimeError as exc:          # minimal level set above the cap
            out.append((index, len(pair[0]) + len(pair[1]), -1, '', str(exc)))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('src', type=Path)
    ap.add_argument('--out', type=Path, required=True, help='.csv or .csv.gz')
    ap.add_argument('--prefix', default='row')
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--chunk', type=int, default=500)
    ap.add_argument('--limit', type=int, default=0)
    args = ap.parse_args()
    opener = gzip.open if args.src.suffix == '.gz' else open
    with opener(args.src, 'rt') as f:
        lines = [l for l in f if l.strip()]
    if args.limit:
        lines = lines[:args.limit]
    chunks = [list(enumerate(lines))[i:i + args.chunk] for i in range(0, len(lines), args.chunk)]
    t0 = time.perf_counter()
    orbits = {}            # rep -> [first_index, members]
    mu_hist = collections.Counter()
    len_hist = collections.Counter()
    failures = []
    done = 0
    with mp.Pool(args.workers, initializer=_init) as pool:
        for out in pool.imap(job, chunks):
            for index, length, mu, a, b in out:
                if mu < 0:
                    failures.append((index, b))
                    continue
                mu_hist[mu] += 1
                len_hist[length] += 1
                row = orbits.get((a, b))
                if row is None:
                    orbits[(a, b)] = [index, [index]]
                else:
                    row[1].append(index)
            done += len(out)
            if done % 100000 < args.chunk or done == len(lines):
                print(json.dumps(dict(rows=done, orbits=len(orbits), failures=len(failures),
                                      elapsed=round(time.perf_counter() - t0, 1))), flush=True)
    ordered = sorted(orbits.items(), key=lambda kv: kv[1][0])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    wopen = gzip.open if args.out.suffix == '.gz' else open
    with wopen(args.out, 'wt', newline='') as f:
        w = csv.writer(f)
        w.writerow(['name', 'r1', 'r2', 'n_members', 'members'])
        for i, ((a, b), (first, members)) in enumerate(ordered):
            w.writerow([f'{args.prefix}_{i}', a, b, len(members), ' '.join(map(str, members))])
    summary = dict(src=str(args.src), rows=len(lines), orbits=len(ordered), failures=failures,
                   mu_hist=dict(sorted(mu_hist.items())), length_hist=dict(sorted(len_hist.items())),
                   elapsed=round(time.perf_counter() - t0, 1))
    base = args.out.name.replace('.csv.gz', '').replace('.csv', '')
    (args.out.parent / (base + '.summary.json')).write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({k: v for k, v in summary.items() if k not in ('mu_hist', 'length_hist')}))


if __name__ == '__main__':
    main()
