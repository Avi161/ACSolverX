"""Load ``../atlas.jsonl`` into numpy arrays for the image-ranking experiments.

One record per (row, image); 124 rows x 13 radius-2 images.  ``load()`` returns a dict

    rows        list of row names (group ids), sorted; ``group[i]`` indexes into it
    level, form per image (strings), ``row_index`` per image (position in the atlas row)
    X           (n, p) float feature matrix, columns ``names`` (see ``image_vector``)
    y           log10(nodes); ``censored`` True where the run did not solve at 20,000
                (nodes == budget and not solved); ``solved`` the raw solve flag
    nodes       raw pop count (censored runs carry the budget, 20,000)
    seq         list of AUTOS-index tuples, ``depth``, ``is_identity``, ``r1``, ``r2``

Feature vector of an image (``image_vector``): every numeric entry of ``features.features``
(17 ``heuristics.phi`` features, ``h_s20mk2``, exponent sums, det, lengths, once-counts),
then ``depth``, ``is_identity``, ``delta_len = total_len - row_total_len``, ``same_gen``
(depth-2 image whose two generators coincide), and one-hot of the first and of the second
AUTOS index of ``seq`` (20 slots each; all zero when absent).  Only indices 8, 9, 14, 15
ever occur (the other second-kind autos are relabel-equivalent to these, and the first-kind
ones are relabellings), so the unused one-hot columns are constant and get zero weight.

``folds(rows, k, seed)`` assigns each ROW to one of ``k`` folds, stratified by level, with a
seeded permutation; every image of a row shares the row's fold.  ``standardise(X_train)``
returns ``(mean, std)`` from the training rows only (std of a constant column is set to 1).
"""
import json
import sys
from collections import OrderedDict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

HERE = Path(__file__).resolve().parent
ATLAS = HERE.parent / 'atlas.jsonl'
BUDGET = 20000
N_AUTOS = 20
FEATURE_KEYS = ('L', 'Lmin', 'Lmax', 'imbal', 'K', 'MK', 'mK', 'S', 'Bmax', 'B1', 'Bmin', 'nb',
                'xyimb', 'Bmaxrun', 'Bspread', 'ratio', 'density', 'h_s20mk2', 'ex1', 'ey1',
                'ex2', 'ey2', 'abelian_det', 'min_len', 'max_len', 'total_len', 'once_gen',
                'once_letter')
EXTRA_KEYS = ('depth', 'is_identity', 'delta_len', 'same_gen')
VECTOR_NAMES = tuple(FEATURE_KEYS) + EXTRA_KEYS + tuple(f'gen1_{i}' for i in range(N_AUTOS)) \
    + tuple(f'gen2_{i}' for i in range(N_AUTOS))


def image_vector(feats, seq, depth, is_identity, row_total_len):
    """``(x, VECTOR_NAMES)`` for one image; ``feats`` is ``features.features(r1, r2)``."""
    x = [float(feats[k]) for k in FEATURE_KEYS]
    seq = list(seq)
    same = 1.0 if (len(seq) == 2 and seq[0] == seq[1]) else 0.0
    x += [float(depth), 1.0 if is_identity else 0.0,
          float(feats['total_len']) - float(row_total_len), same]
    g1 = [0.0] * N_AUTOS
    g2 = [0.0] * N_AUTOS
    if len(seq) >= 1:
        g1[seq[0]] = 1.0
    if len(seq) >= 2:
        g2[seq[1]] = 1.0
    x += g1 + g2
    return np.asarray(x, float), VECTOR_NAMES


def load(path=ATLAS, budget=BUDGET):
    recs = [json.loads(line) for line in open(path)]
    by_row = OrderedDict()
    for r in recs:
        by_row.setdefault(r['row'], []).append(r)
    rows = sorted(by_row)
    X, y, cens, solved, nodes, group, level, form, seq, depth, ident, ridx, r1s, r2s = ([] for _ in range(14))
    for gi, row in enumerate(rows):
        imgs = sorted(by_row[row], key=lambda r: r['image_index'])
        assert imgs[0]['is_identity'] and imgs[0]['depth'] == 0
        row_total_len = imgs[0]['features']['total_len']
        for r in imgs:
            x, _ = image_vector(r['features'], r['seq'], r['depth'], r['is_identity'], row_total_len)
            X.append(x)
            n = int(r['s20']['nodes'])
            s = bool(r['s20']['solved'])
            c = (not s) and n >= budget
            assert s or c, (row, r['image_index'], n, s)
            y.append(np.log10(n))
            cens.append(c)
            solved.append(s)
            nodes.append(n)
            group.append(gi)
            level.append(str(r['level']))
            form.append(r['form'])
            seq.append(tuple(r['seq']))
            depth.append(int(r['depth']))
            ident.append(bool(r['is_identity']))
            ridx.append(int(r['image_index']))
            r1s.append(r['r1'])
            r2s.append(r['r2'])
    return {'rows': rows, 'names': VECTOR_NAMES, 'X': np.asarray(X), 'y': np.asarray(y),
            'censored': np.asarray(cens), 'solved': np.asarray(solved),
            'nodes': np.asarray(nodes), 'group': np.asarray(group), 'level': np.asarray(level),
            'form': np.asarray(form), 'seq': seq, 'depth': np.asarray(depth),
            'is_identity': np.asarray(ident), 'row_index': np.asarray(ridx), 'r1': r1s, 'r2': r2s,
            'budget': budget}


def row_level_form(d):
    """Per-row level and form (from the row's identity image)."""
    lev, frm = {}, {}
    for g, l, f, i in zip(d['group'], d['level'], d['form'], d['is_identity']):
        if i:
            lev[int(g)] = l
            frm[int(g)] = f
    return lev, frm


def folds(d, k=5, seed=0, rows=None):
    """Fold id per ROW (length = number of rows), stratified by level, seeded permutation.
    With ``rows`` (a set of row ids) only those rows get a fold; the others carry -1."""
    lev, _ = row_level_form(d)
    rng = np.random.RandomState(seed)
    fold = np.full(len(d['rows']), -1, int)
    keep = set(range(len(d['rows']))) if rows is None else set(int(r) for r in rows)
    for l in sorted(set(lev.values())):
        members = np.array(sorted(g for g in lev if lev[g] == l and g in keep))
        if len(members) == 0:
            continue
        members = members[rng.permutation(len(members))]
        for pos, g in enumerate(members):
            fold[g] = pos % k
    assert all(fold[g] >= 0 for g in keep)
    return fold


def split(d, fold, f):
    """Boolean image masks ``(train, test)`` for outer fold ``f``; row-disjoint by construction."""
    test_rows = np.where(fold == f)[0]
    test = np.isin(d['group'], test_rows)
    train = ~test
    assert not (set(d['group'][train]) & set(d['group'][test]))
    return train, test


def standardise(X):
    mean = X.mean(axis=0)
    std = X.std(axis=0)
    std[std == 0] = 1.0
    return mean, std


if __name__ == '__main__':
    d = load()
    print(f"{len(d['rows'])} rows, {len(d['y'])} images, {d['X'].shape[1]} features")
    print(f"solved {int(d['solved'].sum())}, censored {int(d['censored'].sum())}")
    fold = folds(d)
    print('fold sizes (rows):', np.bincount(fold).tolist())
    const = [n for n, s in zip(d['names'], d['X'].std(axis=0)) if s == 0]
    print('constant columns:', const)
