"""Focused checks for the two lemmas and the coupling search (no census search)."""
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path[:0] = [str(HERE), str(ROOT / 'research/rank_unbounded_20260912'),
                str(ROOT / 'research/u124_high_rank_ac_20260912'),
                str(ROOT / 'research/u124_rank_3h_20260912')]

import search          # noqa: E402
import theory          # noqa: E402


def random_triangle_state(rng, rank):
    while True:
        words = []
        for _ in range(rank):
            w = search.canonical(tuple(rng.choice([g, -g]) for g in rng.choices(range(1, rank + 1), k=3)))
            if len(w) != 3:
                break
            words.append(w)
        else:
            state = search.normalize(tuple(words))
            if len(state) == rank and all(len(w) == 3 for w in state):
                return state


def test_parity_lemma_on_random_states():
    rng = random.Random(1)
    for _ in range(300):
        state = random_triangle_state(rng, rng.randint(2, 4))
        assert theory.check_parity_lemma(state) == []


def test_bigon_necessity_and_degenerate_sufficiency():
    rng = random.Random(2)
    seen_positive = False
    for _ in range(1500):
        state = random_triangle_state(rng, rng.randint(2, 4))
        result = theory.check_bigon_criterion(state)
        assert not result['necessity_violated']
        if result['shared_digram_pairs'] and not result['bigons']:
            assert result['degenerate_equal_relators']
        if result['bigons']:
            seen_positive = True
            assert not result['digram_disjoint']
    assert seen_positive


def test_inv2_is_an_involution_and_matches_inversion():
    for d in [(1, 2), (-3, 1), (2, 2), (-1, -1)]:
        assert theory.inv2(theory.inv2(d)) == d
    w = (1, 2, -3)
    inv_digrams = theory.cyclic_digrams(search.inverse(w))
    assert {theory.inv2(d) for d in theory.cyclic_digrams(w)} == inv_digrams


def test_digram_disjoint_root_has_empty_cap3_neighbourhood():
    rng = random.Random(3)
    checked = 0
    for _ in range(400):
        state = random_triangle_state(rng, rng.randint(3, 4))
        if theory.is_digram_disjoint(state):
            products, _ = theory.one_step_products(state, relator_cap=3)
            assert products == []
            checked += 1
    assert checked > 0


def test_coupling_search_exposes_bigon_on_sharing_control():
    import coupling_search
    # ac19_44's triangulated root, which shares digrams (from the frozen easy panel)
    root = ((-5, -4, 2), (-5, 2, -1), (-5, 3, -1), (-4, -3, 2), (-3, -1, -1))
    assert not theory.is_digram_disjoint(root)
    res = coupling_search.search_row(root, ordering='coupling', relator_cap=4, pop_budget=5)
    assert res['bigon_found'] and len(res['events']) == 1
    assert res['rank'] == 5 and len(res['endpoint']) == 5
