import json
import random
import numpy as np
import pytest

from experiments.search.heuristic_1k import ROOT, NIELSEN, pack, response, run, verify, score_key
from experiments.equivalence_classes.lib.words import apply_pair, canon_pair


def test_nielsen_length_response_matches_actual_word_substitution():
    rng = random.Random(719)
    pairs = [('YXyxYx', 'YYYYxxx'), ('YXYxyx', 'YYYYxxx')]
    pairs += [tuple(''.join(rng.choices('XYxy', k=rng.randrange(1,25))) for _ in range(2)) for _ in range(128)]
    for pair in pairs:
        pair = canon_pair(*pair)
        length = sum(map(len, pair))
        expected = tuple(sum(map(len, apply_pair(pair, a))) - length for a in NIELSEN)
        assert response(np.frombuffer(pack(pair), dtype=np.uint8)) == expected
    assert min(response(np.frombuffer(pack(pairs[0]), dtype=np.uint8))) == 0
    assert min(response(np.frombuffer(pack(pairs[1]), dtype=np.uint8))) == 2


@pytest.mark.parametrize('arm', ['greedy', 's20', 'whitehead2', 'aut_start', 'aut_edges', 'minK2'])
def test_small_solve_certificate_and_budget(arm):
    pair = ('YYXyx', 'Yx')
    result = run(pair, arm, budget=30)
    assert result['solved']
    assert result['nodes_explored'] <= 30
    assert verify(pair, result)


def test_local_budget_ceiling():
    with pytest.raises(ValueError):
        run(('x', 'y'), 'aut_edges', budget=1001)


@pytest.mark.parametrize('cap', [0, 129])
def test_cap_bounds(cap):
    with pytest.raises(ValueError, match='cap in 1..128'):
        run(('x', 'y'), 'aut_edges', cap=cap)


def test_reduced_root_bounds():
    with pytest.raises(ValueError, match='exceeds'):
        run(('xxx', 'y'), 'whitehead2', cap=2)


@pytest.mark.parametrize('weight', [0.0, 0.5, 1.0, 2.0, 4.0, 8.0])
def test_weighted_score_and_hybrid_budget(weight):
    codes = np.frombuffer(pack(canon_pair('YXYxyx', 'YYYYxxx')), dtype=np.uint8)
    assert score_key(codes, weight != 0, weight) == 49 + 2 * weight
    result = run(('YYXyx', 'Yx'), 'aut_edges', budget=30, w_weight=weight)
    assert result['nodes_explored'] <= 30
    if result['solved']:
        assert verify(('YYXyx', 'Yx'), result)
    terminal = run(('x', 'y'), 'aut_edges', budget=1, w_weight=weight)
    assert terminal['solved'] and verify(('x', 'y'), terminal)


@pytest.mark.parametrize('arm,weight', [('s20', 0.0), ('whitehead2', 2.0), ('aut_edges', 0.0)])
def test_weight_override_preserves_saved_search(arm, weight):
    path = ROOT / 'results/heuristic_search/timing_1k/runs.jsonl'
    if not path.exists():
        pytest.skip('historical timing artifact is not carried on this branch')
    saved = [json.loads(line) for line in path.read_text().splitlines()]
    expected = next(r for r in saved if r['arm'] == arm and r['pres_id'] == 568)
    result = run((expected['r1'], expected['r2']), arm, w_weight=weight)
    assert (result['solved'], result['nodes_explored']) == (expected['solved'], expected['nodes_explored'])
    if result['solved']:
        assert result['states'] == expected['states'] and result['steps'] == expected['steps']


@pytest.mark.parametrize('weight', [-1, float('nan'), float('inf')])
def test_invalid_weight(weight):
    with pytest.raises(ValueError, match='finite and nonnegative'):
        run(('x', 'y'), 'aut_edges', w_weight=weight)


def test_weight_requires_s20_arm():
    with pytest.raises(ValueError, match='S20-based'):
        run(('x', 'y'), 'greedy', w_weight=2)


@pytest.mark.parametrize('s,mk,w', [(0,0,.5), (10,0,0), (0,4,0), (10,4,.75)])
def test_independent_structural_coefficients(s, mk, w):
    from experiments.search.heuristics import phi
    pair = canon_pair('YXYxyx', 'YYYYxxx')
    f = phi(*pair)
    codes = np.frombuffer(pack(pair), dtype=np.uint8)
    assert score_key(codes, w != 0, w, s, mk) == f[0] + mk*f[5] + s*f[7] + w*min(response(codes))
    result = run(('x', 'y'), 'aut_edges', budget=1, s_weight=s, mk_weight=mk, w_weight=w)
    assert result['solved'] and verify(('x', 'y'), result)


def test_zero_structural_weights_reproduce_greedy():
    pair = ('YYXyx', 'Yx')
    assert run(pair, 's20', budget=30, s_weight=0, mk_weight=0, w_weight=0) == run(pair, 'greedy', budget=30)


@pytest.mark.parametrize('kw', [{'s_weight':-1}, {'mk_weight':float('nan')}])
def test_invalid_structural_weights(kw):
    with pytest.raises(ValueError, match='finite and nonnegative'):
        run(('x', 'y'), 's20', **kw)
