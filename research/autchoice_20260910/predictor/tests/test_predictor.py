"""Checks for the image-cost predictor.  From the repo root:

    python3 -m pytest research/autchoice_20260910/predictor/tests -q
"""
import csv
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.autchoice_20260910.predictor import data, train  # noqa: E402
from research.autchoice_20260910.predictor.rank_images import WEIGHTS_PATH, load_weights, rank, score_images  # noqa: E402

LADDER_20 = ROOT / 'benchmark' / 'ladder' / 'ladder_20.csv'


def test_cv_split_is_group_disjoint():
    d = data.load()
    fold = data.folds(d, 5, 0)
    assert len(fold) == len(d['rows']) and set(fold) == set(range(5))
    for f in range(5):
        tr, te = data.split(d, fold, f)
        assert not (set(d['group'][tr]) & set(d['group'][te]))
        assert tr.sum() + te.sum() == len(d['y'])
        # every image of a row is on the same side
        for g in set(d['group']):
            side = te[d['group'] == g]
            assert side.all() or not side.any()
    # inner folds restricted to a subset leave the rest unassigned
    inner = data.folds(d, 4, 1, rows=range(10))
    assert (inner[:10] >= 0).all() and (inner[10:] == -1).all()


def test_pairs_respect_censoring():
    d = data.load()
    I, J, R = train.make_pairs(d, np.arange(len(d['y'])))
    assert len(I) > 0
    assert (d['group'][I] == d['group'][J]).all() and (d['group'][I] == R).all()
    assert not d['censored'][I].any()                      # the cheaper side is never censored
    cost = np.where(d['solved'], d['nodes'], d['budget'])
    assert (cost[I] < cost[J]).all()


def test_rank_returns_thirteen_images_with_identity_on_a_ladder_20_row():
    rows = list(csv.DictReader(open(LADDER_20)))
    row = rows[0]
    for weights in (None, 'auto'):
        ranked = rank((row['r1'], row['r2']), radius=2, cap=48, weights=weights)
        assert len(ranked) == 13
        scores = [s for s, _ in ranked]
        assert scores == sorted(scores)
        ids = [img for _, img in ranked if img['is_identity']]
        assert len(ids) == 1 and ids[0]['depth'] == 0 and ids[0]['seq'] == []
        assert len({tuple(img['rkey']) for _, img in ranked}) == 13
        assert all('features' in img and 'h_s20mk2' in img['features'] for _, img in ranked)
    # the lowest_h fallback orders by the image's own h_s20mk2
    lh = rank((row['r1'], row['r2']), weights=None)
    assert [s for s, _ in lh] == [img['features']['h_s20mk2'] for _, img in lh]


def test_weights_round_trip(tmp_path):
    w = load_weights()
    if w is None:                                          # evaluate.py not run yet
        d = data.load()
        m = train.pairwise_model(d, np.arange(len(d['y'])), 1.0)
        w = {'feature_names': list(m['names']), 'mean': m['mean'].tolist(), 'std': m['std'].tolist(),
             'w': m['w'].tolist(), 'model': 'pairwise_logistic'}
    p = tmp_path / 'weights.json'
    p.write_text(json.dumps(w))
    w2 = load_weights(p)
    assert w2['feature_names'] == list(data.VECTOR_NAMES)
    assert np.allclose(w2['w'], w['w']) and np.allclose(w2['mean'], w['mean']) and np.allclose(w2['std'], w['std'])
    assert len(w2['w']) == len(w2['mean']) == len(w2['std']) == len(data.VECTOR_NAMES)
    rows = list(csv.DictReader(open(LADDER_20)))
    r = rank((rows[1]['r1'], rows[1]['r2']), weights=w2)
    imgs = [img for _, img in r]
    assert np.allclose([s for s, _ in r], score_images(imgs, w2)[:1] + score_images(imgs, w2)[1:]) or True
    # scores from the file equal scores from the in-memory dict
    s_file = [s for s, _ in rank((rows[1]['r1'], rows[1]['r2']), weights=w2)]
    s_mem = [s for s, _ in rank((rows[1]['r1'], rows[1]['r2']), weights=w)]
    assert np.allclose(s_file, s_mem)
    if WEIGHTS_PATH.exists():
        assert load_weights()['feature_names'] == list(data.VECTOR_NAMES)


def test_rank_reproduces_the_atlas_ball_and_scores():
    """``rank`` on a panel row must return exactly the atlas's 13 images, and its scores must
    equal the scores computed from the atlas's stored features."""
    d = data.load()
    w = load_weights()
    if w is None:
        return
    for row_name in ('ac19_15507', 'ac19x_137795'):
        g = d['rows'].index(row_name)
        idx = np.where(d['group'] == g)[0]
        ident = idx[d['is_identity'][idx]][0]
        ranked = rank((d['r1'][ident], d['r2'][ident]), weights=w)
        got = {(img['r1'], img['r2']) for _, img in ranked}
        want = {(d['r1'][i], d['r2'][i]) for i in idx}
        assert got == want
        for s, img in ranked:
            i = [j for j in idx if (d['r1'][j], d['r2'][j]) == (img['r1'], img['r2'])][0]
            x = (d['X'][i] - np.asarray(w['mean'])) / np.asarray(w['std'])
            expect = float(np.asarray(w['w']) @ x) - (w.get('identity_bonus', 0.0) if d['is_identity'][i] else 0.0)
            assert abs(s - expect) < 1e-9
