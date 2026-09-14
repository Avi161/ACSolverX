"""Fast-vs-slow cross-check of the canonicaliser on samples of AC1M and AC19_extended:
`autcanon_fast.aut_min` (numba, used for the censuses) against `autcanon.aut_canon`
(pure Python, ships a witnessing automorphism that `check` verifies by substitution).

    python3 research/ac1m_autmin_20260914/crosscheck.py --ac1m 2000 --ext 1000 --seed 1
"""
from __future__ import annotations

import argparse
import gzip
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.equivalence_classes.lib.autcanon import aut_canon, check, is_automorphism  # noqa: E402
from experiments.stable_ac.cov.ladder.autcanon_fast import aut_min, warm  # noqa: E402
from research.ac1m_autmin_20260914.autmin_census import line_to_pair  # noqa: E402


def sample(path, n, rng):
    opener = gzip.open if str(path).endswith('.gz') else open
    with opener(path, 'rt') as f:
        lines = [l for l in f if l.strip()]
    idx = sorted(rng.sample(range(len(lines)), n))
    return [(i, line_to_pair(lines[i])) for i in idx]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--ac1m', type=int, default=2000)
    ap.add_argument('--ext', type=int, default=1000)
    ap.add_argument('--seed', type=int, default=1)
    args = ap.parse_args()
    warm()
    rng = random.Random(args.seed)
    report = {}
    for name, path, n in (('AC1M', ROOT / 'data/AC1M.txt.gz', args.ac1m),
                          ('AC19_extended', ROOT / 'data/AC19_extended.txt', args.ext)):
        rows = sample(path, n, rng)
        t = time.perf_counter()
        mismatch = witness_fail = 0
        for i, pair in rows:
            mu, rep = aut_min(pair)
            t_slow, rep_slow, phi = aut_canon(pair)
            if (mu, tuple(rep)) != (t_slow, tuple(rep_slow)):
                mismatch += 1
            if not (is_automorphism(phi) and check(pair, rep_slow, phi)):
                witness_fail += 1
        report[name] = dict(rows=n, fast_vs_slow_mismatches=mismatch, witness_failures=witness_fail,
                            seconds=round(time.perf_counter() - t, 1))
        print(name, report[name], flush=True)
    (HERE / 'records' / 'crosscheck.json').write_text(json.dumps(dict(seed=args.seed, **report), indent=2) + '\n')


if __name__ == '__main__':
    main()
