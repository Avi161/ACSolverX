"""Hand-written rankers for the 13 images of a row.

Every ranker is ``f(row) -> order`` where ``row`` is the dict built by ``row_view`` (raw,
un-standardised features and bookkeeping, never the costs) and ``order`` lists the row's
image positions best first.

    identity      the row as given first ("do nothing"), then the atlas BFS order
    shortest      smallest total length, ties by the relator strings
    lowest_h      smallest ``h_s20mk2`` of the image itself, ties by (depth, seq)
    random        a seeded permutation (``random_ranker(seed)``); evaluate.py averages 20 seeds
    depth2_first  depth-2 images first, then depth 1, then the identity; ties by lowest_h
    bfs           the atlas order itself (identity, depth 1 in AUTOS order, depth 2)
"""
import numpy as np

from research.autchoice_20260910.predictor.data import VECTOR_NAMES

COL = {n: i for i, n in enumerate(VECTOR_NAMES)}


def row_view(d, idx):
    """The ranker-visible view of the images at positions ``idx`` (one row) of dataset ``d``."""
    idx = np.asarray(idx)
    return {'X': d['X'][idx], 'seq': [d['seq'][i] for i in idx], 'depth': d['depth'][idx],
            'is_identity': d['is_identity'][idx], 'image_index': d['row_index'][idx],
            'r1': [d['r1'][i] for i in idx], 'r2': [d['r2'][i] for i in idx]}


def _order(row, key):
    n = len(row['depth'])
    return sorted(range(n), key=key)


def _tie(row, i):
    return (int(row['depth'][i]), tuple(row['seq'][i]))


def identity(row):
    return _order(row, lambda i: (0 if row['is_identity'][i] else 1, int(row['image_index'][i])))


def bfs(row):
    return _order(row, lambda i: int(row['image_index'][i]))


def shortest(row):
    tl = row['X'][:, COL['total_len']]
    return _order(row, lambda i: (tl[i], row['r1'][i], row['r2'][i]))


def lowest_h(row):
    h = row['X'][:, COL['h_s20mk2']]
    return _order(row, lambda i: (h[i],) + _tie(row, i))


def depth2_first(row):
    h = row['X'][:, COL['h_s20mk2']]
    return _order(row, lambda i: (-int(row['depth'][i]), h[i]) + _tie(row, i))


def random_ranker(seed):
    rng = np.random.RandomState(seed)

    def f(row):
        return list(rng.permutation(len(row['depth'])))
    return f


def score_order(row, scores):
    """Order by a score vector (lower first), ties by (depth, seq)."""
    return _order(row, lambda i: (float(scores[i]),) + _tie(row, i))


BASELINES = {'identity': identity, 'shortest': shortest, 'lowest_h': lowest_h,
             'depth2_first': depth2_first, 'bfs': bfs}
