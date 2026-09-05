"""Signed block structure: the pure-power theorem, and the invariances the features rely on.

The headline claim is structural, not statistical, so it is pinned here: in a freely reduced word
a maximal same-generator block can never change sign, which is why every "exponent alternates
inside a block" feature measured exactly 0.00 on all 237 presentations. That is a fact about
reduced words, not a property of this dataset.
"""
import itertools
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from experiments.clustering.signed_knots import (  # noqa: E402
    block_signature, signed_blocks, signed_features,
)

ALPHA = "xXyY"
INV = {"x": "X", "X": "x", "y": "Y", "Y": "y"}


def _reduced_cyclic(w):
    return bool(w) and all(INV[w[i]] != w[(i + 1) % len(w)] for i in range(len(w)))


def _words(nmax):
    for n in range(1, nmax + 1):
        for t in itertools.product(ALPHA, repeat=n):
            w = "".join(t)
            if _reduced_cyclic(w):
                yield w


def test_every_block_of_a_reduced_word_is_a_pure_power():
    """THEOREM. In a freely+cyclically reduced word, |exponent sum| == block length, always.

    Two adjacent letters inside one block share a generator; if their signs differed the word
    would contain ``xX`` or ``Xx`` and would not be reduced. So a block is x^k or X^k, never
    mixed -- there is no within-block exponent freedom to exploit.
    """
    checked = 0
    for w in _words(9):
        for gen, n, exp in signed_blocks(w):
            assert abs(exp) == n, f"{w}: block ({gen}, {n}, {exp}) is not a pure power"
            checked += 1
    assert checked > 50_000, f"only {checked} blocks checked -- corpus too thin"


def test_blocks_partition_the_word():
    """Block lengths must sum to |w|, or the decomposition is dropping or duplicating letters."""
    for w in _words(8):
        assert sum(n for _, n, _ in signed_blocks(w)) == len(w)


def test_signed_blocks_alternate_generators():
    for w in _words(8):
        b = signed_blocks(w)
        if len(b) > 1:
            for i in range(len(b)):
                assert b[i][0] != b[(i + 1) % len(b)][0], f"{w}: adjacent blocks share a generator"


def test_features_and_signature_are_rotation_invariant():
    """The whole point of reading blocks cyclically: the canonicaliser's cut must be invisible."""
    import numpy as np
    for w in _words(7):
        base_f = signed_features(w, "xy")
        base_s = block_signature(w, "xy")
        for k in range(1, len(w)):
            rot = w[k:] + w[:k]
            assert np.abs(signed_features(rot, "xy") - base_f).max() < 1e-12, f"{w} rot {k}"
            assert block_signature(rot, "xy") == base_s, f"{w} rot {k}"


def test_signature_is_relator_swap_invariant():
    for a in _words(5):
        for b in ("xy", "xxyy", "xYxy"):
            assert block_signature(a, b) == block_signature(b, a)


def test_mixed_block_features_are_identically_zero_on_reduced_input():
    """The three 'sign alternates inside a block' features are structurally dead, not just quiet."""
    import numpy as np
    for w in _words(8):
        f = signed_features(w, "xy")
        assert f[0] == 0.0 and f[1] == 0.0 and f[2] == 0.0, f"{w}: mixed-block feature fired"
        blocks = signed_blocks(w) + signed_blocks("xy")
        lens = np.array([n for _, n, _ in blocks], float)
        exps = np.array([abs(e) for _, _, e in blocks], float)
        # mean |exponent| and mean block length are therefore the SAME statistic.
        assert abs(lens.mean() - exps.mean()) < 1e-12
