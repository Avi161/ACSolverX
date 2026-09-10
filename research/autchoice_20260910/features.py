"""Cheap, pure state features for the orbit-cost atlas.

``features(r1, r2)`` returns an ``OrderedDict``: the 17 rotation-invariant features of
``experiments.search.heuristics.phi`` under their ``FEATURES`` names, then

    h_s20mk2      L + 20*S + 2*MK, the shipped heap priority (CLAUDE.md, section 1)
    ex1, ey1      exponent sums of x and y in r1          ex2, ey2   the same for r2
    abelian_det   ex1*ey2 - ey1*ex2  (+-1 for every AC-trivialisable pair)
    min_len, max_len, total_len
    once_gen      number of (relator, generator) pairs where the generator occurs exactly
                  once in that relator, sign ignored (x and X both count) -- 0..4
    once_letter   the same counting each signed letter xXyY separately -- 0..8

Everything is a plain int/float so a record can go straight into JSON.
"""
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.equivalence_classes.lib.words import exp_sums  # noqa: E402
from experiments.search.heuristics import FEATURES, phi  # noqa: E402

_L, _S, _MK = FEATURES.index('L'), FEATURES.index('S'), FEATURES.index('MK')


def h_s20mk2(r1, r2):
    """The S20_MK2 priority of a state: ``L + 20*S + 2*MK``."""
    v = phi(r1, r2)
    return v[_L] + 20.0 * v[_S] + 2.0 * v[_MK]


def _once(word):
    gen = sum(1 for g in 'xy' if sum(1 for c in word if c.lower() == g) == 1)
    let = sum(1 for g in 'xXyY' if word.count(g) == 1)
    return gen, let


def features(r1, r2):
    v = phi(r1, r2)
    out = OrderedDict((name, float(val)) for name, val in zip(FEATURES, v))
    out['h_s20mk2'] = v[_L] + 20.0 * v[_S] + 2.0 * v[_MK]
    ex1, ey1 = exp_sums(r1)
    ex2, ey2 = exp_sums(r2)
    out['ex1'], out['ey1'], out['ex2'], out['ey2'] = ex1, ey1, ex2, ey2
    out['abelian_det'] = ex1 * ey2 - ey1 * ex2
    out['min_len'] = min(len(r1), len(r2))
    out['max_len'] = max(len(r1), len(r2))
    out['total_len'] = len(r1) + len(r2)
    g1, l1 = _once(r1)
    g2, l2 = _once(r2)
    out['once_gen'] = g1 + g2
    out['once_letter'] = l1 + l2
    return out


FEATURE_NAMES = tuple(features('YYXXyxx', 'YYYYYYXYxYYYYX').keys())
