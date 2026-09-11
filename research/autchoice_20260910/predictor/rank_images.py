"""Rank the radius-``r`` Aut(F2)-images of a presentation, cheapest-looking first.

    from research.autchoice_20260910.predictor.rank_images import rank
    ranked = rank(pair, radius=2, cap=48)      # -> [(score, image_dict), ...], best first

``image_dict`` is the ``orbit.ball`` node (``r1, r2, seq, phi, depth, rkey``) plus
``features`` (``features.features(r1, r2)``) and ``is_identity``.  ``score`` is *lower =
predicted cheaper*; it is only comparable inside one ball.

If ``weights.json`` (written by ``evaluate.py``) exists beside this file the score is the
learned linear model ``w . standardise(x)`` minus an ``identity_bonus`` on the row as given
(the pick deviates from it only when an image beats it by more than the bonus); otherwise
it falls back to the ``lowest_h`` rule
(the image's own ``h_s20mk2``, i.e. the S20_MK2 priority of the start state).  Ties are broken
by ``(depth, seq)`` so the ordering is deterministic.

    PYTHONPATH=. python3 -m research.autchoice_20260910.predictor.rank_images R1 R2 [--radius 2] [--cap 48]
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.autchoice_20260910.features import features  # noqa: E402
from research.autchoice_20260910.orbit import ball  # noqa: E402
from research.autchoice_20260910.predictor.data import image_vector  # noqa: E402

HERE = Path(__file__).resolve().parent
WEIGHTS_PATH = HERE / 'weights.json'


def load_weights(path=WEIGHTS_PATH):
    """The learned model ``{feature_names, mean, std, w, ...}`` or None when absent."""
    if not Path(path).exists():
        return None
    with open(path) as fh:
        return json.load(fh)


def score_images(images, weights=None):
    """Scores (lower = cheaper) for a list of image dicts that already carry ``features``."""
    row_total_len = images[0]['features']['total_len']
    if weights is None:
        return [float(img['features']['h_s20mk2']) for img in images]
    names, mean, std, w = (weights['feature_names'], np.asarray(weights['mean'], float),
                           np.asarray(weights['std'], float), np.asarray(weights['w'], float))
    bonus = float(weights.get('identity_bonus', 0.0))
    out = []
    for img in images:
        x, xnames = image_vector(img['features'], img['seq'], img['depth'], img['is_identity'],
                                 row_total_len)
        assert list(xnames) == list(names), 'weights.json feature names do not match data.py'
        out.append(float(w @ ((x - mean) / std)) - (bonus if img['is_identity'] else 0.0))
    return out


def rank(pair, radius=2, cap=48, weights='auto'):
    """``[(score, image_dict), ...]`` over ``orbit.ball(pair, radius, cap)``, best first."""
    if weights == 'auto':
        weights = load_weights()
    images = []
    for node in ball(pair, radius, cap):
        img = dict(node)
        img['features'] = features(img['r1'], img['r2'])
        img['is_identity'] = (img['depth'] == 0)
        images.append(img)
    scores = score_images(images, weights)
    order = sorted(range(len(images)),
                   key=lambda i: (scores[i], images[i]['depth'], tuple(images[i]['seq'])))
    return [(scores[i], images[i]) for i in order]


def main(argv):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('r1')
    ap.add_argument('r2')
    ap.add_argument('--radius', type=int, default=2)
    ap.add_argument('--cap', type=int, default=48)
    ap.add_argument('--lowest-h', action='store_true', help='ignore weights.json, use h_s20mk2')
    a = ap.parse_args(argv)
    w = None if a.lowest_h else load_weights()
    print(f"model: {'lowest_h' if w is None else w.get('model', 'learned')}")
    for k, (s, img) in enumerate(rank((a.r1, a.r2), a.radius, a.cap, weights=w), 1):
        seq = ' '.join(map(str, img['seq'])) or 'id'
        print(f"{k:>2} score={s:9.3f} depth={img['depth']} seq={seq:<6} len={img['features']['total_len']:>3} "
              f"h={img['features']['h_s20mk2']:>6.1f}  {img['r1']} {img['r2']}")


if __name__ == '__main__':
    main(sys.argv[1:])
