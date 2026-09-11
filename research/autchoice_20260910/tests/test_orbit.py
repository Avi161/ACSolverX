"""Checks for the orbit-ball library.  Run from the repo root:

    python3 -m pytest research/autchoice_20260910/tests -q
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.equivalence_classes.lib.autcanon import check, is_automorphism  # noqa: E402
from experiments.equivalence_classes.lib.words import abelian_det, canon_pair, relabel_key  # noqa: E402
from research.autchoice_20260910.engine import verify_from_original  # noqa: E402
from research.autchoice_20260910.features import features  # noqa: E402
from research.autchoice_20260910.orbit import ROOT_STATE, apply_sequence, ball, compose_sequence  # noqa: E402

LEFTOVER = 'dab82a8412b007f23cffd35bee2727d977510de0'
ORIG_JSONL = 'results/heuristic_search/ac19_orig_10m/ac19_orig_10m_greedy_b10000000_mrl64.jsonl'
PAIRS = [('YYXXyxx', 'YYYYYYXYxYYYYX'),      # ac19_15507, level 9
         ('YXXXYxyxxxyXX', 'YXyXXXyXXXX'),   # ac19x_19903, its original
         ('YYXXYx', 'YYYxyyxyXyX'),          # ac19_12445
         ('XXyxy', 'Xyy')]


def test_every_image_carries_a_valid_witness():
    for pair in PAIRS:
        start = canon_pair(*pair)
        b = ball(pair, 2)
        assert b[0]['depth'] == 0 and (b[0]['r1'], b[0]['r2']) == start
        for node in b:
            img = (node['r1'], node['r2'])
            assert check(start, img, node['phi'])
            assert is_automorphism(node['phi'])
            assert node['phi'] == compose_sequence(node['seq'])
            assert apply_sequence(start, node['seq']) == img
            assert len(node['seq']) == node['depth']
            assert max(len(img[0]), len(img[1])) <= 48


def test_relabel_dedup_is_idempotent():
    """Every image of an image lies in the source's larger ball: ball(img, 1) at depth d is
    inside ball(src, d + 1), as relabel classes; and the keys in a ball are distinct."""
    for pair in PAIRS[:2]:
        b2 = ball(pair, 2)
        keys = [n['rkey'] for n in b2]
        assert len(keys) == len(set(keys))
        b3keys = {n['rkey'] for n in ball(pair, 3)}
        for node in b2:
            for m in ball((node['r1'], node['r2']), 1):
                assert m['rkey'] in b3keys
        assert set(keys) <= b3keys


def test_root_ball_size():
    """canon_pair('x','y') is ('Y','X'); its radius-1 ball has 2 relabel classes (the trivial
    pair and (x, xy)-type pairs of total length 3), radius 2 has 4."""
    assert ROOT_STATE == ('Y', 'X')
    b1 = ball(('x', 'y'), 1)
    assert len(b1) == 2, [(n['r1'], n['r2']) for n in b1]
    assert len(ball(('x', 'y'), 2)) == 4


def test_abelian_det_is_invariant_across_a_ball():
    """|det| is an Aut(F2)-invariant (automorphisms act by GL2(Z) on the abelianisation);
    it is 1 on every AC-trivialisable pair, 0 on the last (non-trivial) test pair."""
    for k, pair in enumerate(PAIRS):
        d0 = abs(abelian_det(*pair))
        assert d0 == (1 if k < 3 else 0)
        for node in ball(pair, 2):
            f = features(node['r1'], node['r2'])
            assert abs(f['abelian_det']) == abs(abelian_det(node['r1'], node['r2'])) == d0
            assert f['total_len'] == f['L'] == len(node['r1']) + len(node['r2'])
            assert abs(f['h_s20mk2'] - (f['L'] + 20 * f['S'] + 2 * f['MK'])) < 1e-9


def test_verify_from_original_accepts_committed_certificate():
    blob = subprocess.run(['git', 'show', f'{LEFTOVER}:{ORIG_JSONL}'], cwd=ROOT,
                          capture_output=True, text=True, check=True).stdout
    rec = json.loads(blob.splitlines()[0])
    assert rec['solved']
    assert verify_from_original((rec['r1'], rec['r2']), [], rec['path_moves'])
    assert not verify_from_original((rec['r1'], rec['r2']), [], rec['path_moves'][:-1])
    # the same moves after a non-trivial automorphism: the sequence is applied, so the
    # replay starts elsewhere, runs off-track (the guard in engine.replay stops the
    # doubling) and must not land on the trivial pair
    assert not verify_from_original((rec['r1'], rec['r2']), [8], rec['path_moves'][:12])


def test_relabel_key_of_run_representative_matches_record():
    for node in ball(PAIRS[0], 2):
        assert relabel_key((node['r1'], node['r2'])) == node['rkey']
