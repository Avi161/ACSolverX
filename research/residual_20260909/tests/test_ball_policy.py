"""Exactness, neutrality and dominance tests for the backward-ball tables and
the ball-aware cascade.

Four things are pinned here.

* THE TABLE IS EXACT.  ``build(6)`` is compared key for key against
  ``bruteforce_ball(6)``, which computes the true backward ball by expanding
  EVERY canonical pair with both relators of length <= 6 (6,903 of them) and
  running a reverse BFS -- no predecessor enumeration involved.  The forward
  verification is shown to actually reject candidates (16 of 6,084 at cap 8
  are full-product neighbours that the kernel does not emit) and to be what
  supplies the stored move.
* EVERY STORED EDGE REPLAYS.  Every entry of every shipped table is replayed
  with the pure-Python ``words.replay_move`` / ``words.apply_pair``, and the
  successor's depth is checked to be one less.
* THE BALL IS NEUTRAL WHEN EMPTY.  With ``table={}`` the ball cascade
  reproduces the frozen cascade on the smoke panel bit for bit: same solved
  flags, same ``nodes_explored``, same routes, same certificates.
* THE BALL DOMINATES.  With the cap-8 table every smoke row is solved at no
  more units than the frozen cascade spends, and every certificate decodes and
  independently replays to the trivial basis.

Run:  PYTHONPATH=. python3 -m pytest research/residual_20260909/tests/test_ball_policy.py
"""
import csv
import os
from pathlib import Path

import pytest

for _var in ('NUMBA_NUM_THREADS', 'OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
    os.environ.setdefault(_var, '1')

from experiments.equivalence_classes.lib.words import canon_pair
from experiments.search.heuristic_1k import pack
from research.residual_20260909 import backward_table as bt
from research.residual_20260909 import final_policy_ball
from research.supermoves_20260908 import final_policy
from research.supermoves_20260908.certificate_decoder import replay_elementary
from research.supermoves_20260908.certificate_decoder_compact_moves import decode_elementary

HERE = Path(__file__).resolve().parent
PANELS = HERE.parent / 'panels'
TABLES = HERE.parent / 'tables'
SMOKE = PANELS / 'smoke_solved.csv'

# the per-layer 'new' counts the pure-Python prototype printed for cap 8; the
# numba builder reproduces the prototype's table exactly (same 6,069 keys, same
# depths), so these are a regression pin on both.
CAP8_LAYERS = [4, 8, 40, 572, 1188, 1484, 1104, 656, 404, 272, 80, 144, 56, 40, 16]


def _rows(path):
    with open(path, newline='') as stream:
        return list(csv.DictReader(stream))


def _verify(pair, result):
    moves = decode_elementary(list(pair), result['states'], result['steps'],
                              result.get('elementary_tail'))
    return sorted(word.lower() for word in replay_elementary(list(pair), moves)) == ['x', 'y']


@pytest.fixture(scope='module')
def cap8():
    return bt.load(TABLES / 'ball_cap08.pkl')


# ---------------------------------------------------------------------------
# the table is exact
# ---------------------------------------------------------------------------
def test_build_cap6_equals_bruteforce_ball():
    """The full-product predecessor enumeration finds exactly the true ball."""
    built = bt.build(6)
    truth = bt.bruteforce_ball(6)
    assert set(built) == set(truth)
    assert len(built) == 317
    # depth is the BFS layer the state entered at, an upper bound on the true
    # backward distance -- never smaller than it.
    assert all(built[key][0] >= truth[key] for key in built)


def test_forward_verification_rejects_candidates():
    """The kernel check bites, and it is what supplies the stored move.

    At cap 8, 16 of the 6,084 full-product neighbours the enumeration proposes
    are not children the kernel emits and are dropped.  (They happen to be
    states the BFS reaches by another route, which is why the ball SET is the
    same either way -- but without the check there is no verified move, hence
    no replayable tail, which the second half asserts.)
    """
    stats = {}
    table = bt.build(8, stats=stats)
    rejected = stats['forward_verifications'] - (len(table) - 1)
    assert rejected == 16
    unchecked = bt.build(6, verify=False, stats={})
    assert all(move is None for _depth, _successor, move in unchecked.values())
    assert not bt.check_replay(unchecked)['ok']


def test_cap8_layers_match_the_prototype():
    stats = {}
    table = bt.build(8, stats=stats)
    assert len(table) == 6069
    assert [level['new'] for level in stats['levels'] if level['new']] == CAP8_LAYERS


def test_aut_closure_adds_states_and_keeps_the_plain_ball():
    plain = bt.build(8)
    closed = bt.build(8, aut_edges=True)
    assert set(plain) <= set(closed)
    assert len(closed) == 7613
    assert bt.has_automorphism_edges(closed)
    assert not bt.has_automorphism_edges(plain)


# ---------------------------------------------------------------------------
# every stored edge replays
# ---------------------------------------------------------------------------
@pytest.mark.parametrize('stem', ['ball_cap08', 'ball_cap10', 'ball_cap10_aut'])
def test_shipped_table_entries_replay(stem):
    path = TABLES / f'{stem}.pkl'
    if not path.exists():
        pytest.skip(f'{stem} not built')
    table = bt.load(path)
    report = bt.check_replay(table)
    assert report['ok'], report['failures']
    assert report['checked'] == len(table) - 1


def test_load_rejects_a_tampered_pickle(tmp_path):
    import shutil
    source = TABLES / 'ball_cap08.pkl'
    target = tmp_path / 'ball_cap08.pkl'
    shutil.copy(source, target)
    shutil.copy(bt.manifest_path(source), bt.manifest_path(target))
    bt.load(target)                                  # intact: fine
    blob = bytearray(target.read_bytes())
    blob[-1] ^= 0xFF
    target.write_bytes(bytes(blob))
    with pytest.raises(ValueError, match='sha256'):
        bt.load(target)


# ---------------------------------------------------------------------------
# negative: a state outside the table is not a hit
# ---------------------------------------------------------------------------
def test_state_outside_the_table_is_not_a_hit(cap8):
    outside = ('YYXXyx', 'YXXXXXXyxxxxx')             # dev row ac19_102
    assert pack(canon_pair(*outside)) not in cap8
    result = final_policy_ball.search(outside, budget=40, table=cap8)
    assert result['ball_hit'] is False
    assert result['ball_depth'] == 0
    assert result['ball_lookups'] > 0                # lookups happened, none hit


def test_empty_table_reproduces_the_frozen_cascade():
    """table={} keeps every lookup but can never hit, so nothing may move."""
    for row in _rows(SMOKE):
        pair = (row['r1'], row['r2'])
        frozen = final_policy.search(pair, budget=1000)
        ball = final_policy_ball.search(pair, budget=1000, table={})
        assert ball['solved'] == frozen['solved'], row['name']
        assert ball['nodes_explored'] == frozen['nodes_explored'], row['name']
        assert ball['policy_route'] == frozen['policy_route'], row['name']
        assert ball['states'] == frozen['states'], row['name']
        assert ball['steps'] == frozen['steps'], row['name']
        assert ball['ball_hit'] is False


def test_no_table_at_all_reproduces_the_frozen_cascade():
    pair = ('YYXXXyx', 'YXXXXXYxx')
    frozen = final_policy.search(pair, budget=1000)
    ball = final_policy_ball.search(pair, budget=1000, table=None)
    assert (ball['solved'], ball['nodes_explored'], ball['policy_route']) == \
           (frozen['solved'], frozen['nodes_explored'], frozen['policy_route'])
    assert ball['ball_lookups'] == 0


# ---------------------------------------------------------------------------
# dominance and certificates
# ---------------------------------------------------------------------------
def test_dominance_and_certificates_on_the_smoke_panel(cap8):
    for row in _rows(SMOKE):
        pair = (row['r1'], row['r2'])
        frozen = final_policy.search(pair, budget=1000)
        ball = final_policy_ball.search(pair, budget=1000, table=cap8)
        assert frozen['solved'] and ball['solved'], row['name']
        assert ball['nodes_explored'] <= frozen['nodes_explored'], (
            row['name'], ball['nodes_explored'], frozen['nodes_explored'])
        assert _verify(pair, ball), row['name']


def test_ball_tail_certificate_decodes_from_a_root_hit(cap8):
    """A row whose canonical root is already in the ball: the whole certificate
    is the stored tail, and it still decodes and replays."""
    key = sorted(k for k, (depth, _s, _m) in cap8.items() if depth == cap8[k][0] >= 6)[0]
    from experiments.search.heuristic_1k import unpack
    pair = unpack(key)
    result = final_policy_ball.search(pair, budget=1000, table=cap8)
    assert result['solved'] and result['ball_hit']
    assert _verify(pair, result)


def test_automorphism_tail_certificate_decodes():
    table = bt.build(8, aut_edges=True)
    from experiments.search.heuristic_1k import unpack
    key = sorted(k for k, (_d, _s, move) in table.items() if isinstance(move, dict))[0]
    states, steps = bt.tail(table, key)
    assert any(step['kind'] == 'automorphism' for step in steps)
    pair = unpack(key)
    moves = decode_elementary(list(pair), states, steps, None)
    assert sorted(word.lower() for word in replay_elementary(list(pair), moves)) == ['x', 'y']
