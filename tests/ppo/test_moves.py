"""The S-move port, against the scalar transliteration of the JAX source.

`experiments/ppo/acs_spec.py` is a literal transcription of `envs/ac_moves.py`
that shares no structure with the batched implementation, so agreement between
them is evidence rather than tautology. It also runs without JAX, which is what
lets this gate close on a laptop instead of waiting for a GPU.
"""

import random

import pytest

torch = pytest.importorskip("torch")

from experiments.ppo import acs_data, acs_spec                       # noqa: E402
from experiments.ppo.acs_moves import (                              # noqa: E402
    booth_rotation_index, concatenate, cyclic_reduce, decode_action,
    encode_action, lex_min_rotation_index, reverse_nonzero, rotate_k, s_move)
from experiments.ppo.booth_spec import (                             # noqa: E402
    booth_lex_min_rotation_masked, lex_min_rotation_index_ref)

L = 24
ALPHA = (-2, -1, 1, 2)


def random_words(n, seed, lo=0, hi=L):
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        k = rng.randint(lo, hi)
        out.append([rng.choice(ALPHA) for _ in range(k)] + [0] * (L - k))
    return out


def test_batched_booth_matches_the_jax_transliteration():
    words = random_words(4000, seed=11)
    for base in ([1], [1, 2], [1, 2, -1], [2, 2, 2], [1, -2, 1, -2], [-2, -2, 1]):
        for reps in range(1, L // len(base) + 1):
            w = base * reps
            words.append(w + [0] * (L - len(w)))
    got = booth_rotation_index(torch.tensor(words, dtype=torch.int64))
    assert [int(v) for v in got] == [booth_lex_min_rotation_masked(w) for w in words]


def test_upstream_booth_is_not_lex_min():
    """Pins WHY the O(L^2) brute force cannot replace it.

    `booth_lex_min_rotation_masked` compares `s2[i] != s2[k]` where textbook
    Booth compares `s2[i] != s2[k + j + 1]`, so it returns a rotation that is
    genuinely not the lexicographic minimum on a few percent of words. Swapping
    in the correct algorithm would change the canonical form of those states and
    silently break parity with the shipped checkpoint.
    """
    words = random_words(4000, seed=12, lo=4)
    differing = 0
    for w in words:
        n = sum(1 for v in w if v != 0)
        prefix = w[:n]
        kb, kr = booth_lex_min_rotation_masked(w), lex_min_rotation_index_ref(w)
        rot = lambda k: prefix[k % n:] + prefix[:k % n]                # noqa: E731
        differing += rot(kb) != rot(kr)
    assert differing > 0, "if this ever passes, re-check the port against upstream"

    brute = lex_min_rotation_index(torch.tensor(words, dtype=torch.int64))
    assert [int(v) for v in brute] == [lex_min_rotation_index_ref(w) for w in words]


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_primitives_match_the_spec(seed):
    words = random_words(400, seed=seed)
    t = torch.tensor(words, dtype=torch.int64)
    assert reverse_nonzero(t).tolist() == [acs_spec.reverse_nonzero(w) for w in words]
    assert cyclic_reduce(t).tolist() == [acs_spec.cyclic_reduce(w, L) for w in words]

    other = torch.tensor(random_words(400, seed=seed + 100), dtype=torch.int64)
    assert concatenate(t, other).tolist() == [
        acs_spec.concatenate(a, b, L) for a, b in zip(words, other.tolist())]

    rng = random.Random(seed)
    ks = [rng.randint(-3 * L, 3 * L) for _ in words]
    assert rotate_k(t, torch.tensor(ks)).tolist() == [
        acs_spec.rotate_k(w, k, L) for w, k in zip(words, ks)]


def test_action_packing_round_trips():
    flat = torch.arange(2 * 2 * L * L, dtype=torch.int64)
    i, j, k1, k2 = decode_action(flat, L)
    assert torch.equal(encode_action(i, j, k1, k2, L), flat)
    assert int(k1.min()) == 1 and int(k1.max()) == L
    assert int(k2.min()) == -L and int(k2.max()) == L - 1


def test_rollout_matches_the_spec_state_for_state():
    """Random *and* masked actions, so no-ops and over-length rejections fire."""
    pres = acs_data.load_presentations("AC19_extended", L)
    rng = random.Random(5)
    torch.manual_seed(5)
    rows = rng.sample(range(len(pres)), 96)
    x = torch.tensor(pres[rows], dtype=torch.int64)
    spec = [list(map(int, r)) for r in x.tolist()]

    saw_noop = False
    for _ in range(12):
        a = torch.randint(0, 2 * 2 * L * L, (len(rows),))
        i, j, k1, k2 = decode_action(a, L)
        new_x = s_move(x, i, j, k1, k2, L)
        saw_noop |= bool((new_x == x).all(-1).any())
        spec = [acs_spec.s_move(s, *acs_spec.decode_action(int(v), L), L)
                for s, v in zip(spec, a)]
        assert new_x.tolist() == spec
        x = new_x
    assert saw_noop, "random actions should produce at least one no-op"
