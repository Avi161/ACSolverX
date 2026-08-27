"""Spectral-transform variants: the control IS `search_signlag`, and every variant reads a ring.

`scout_fftvar` ranks 13 spectral transforms against each other by swapping one term in the heap
priority. That ranking is interpretable only if the `lag345` arm reproduces the shipped
`search_signlag` exactly -- same solved flag *and* same `nodes_explored`, not merely a similar
score -- so that is the first test, in the same spirit as `test_hsearch`'s baseline control gate.

The rest guard the two properties a ring feature cannot be allowed to lose silently:

* **rotation invariance** -- states are stored Booth lex-min rotated, so a feature that depends on
  where the ring is cut is reading the canonicalisation, not the presentation. A violation does not
  raise; it just makes the arm meaningless.
* **the declared x<->X relabel set** -- `RELABEL_INVARIANT` is a *claim* about which variants
  respect that AC symmetry, and the claim was wrong the first time it was written (`lagall` was
  listed and is not invariant; `cplxlo` / `cplxpeak` were not listed and are). It is load-bearing
  for the scout's conclusion, so it is pinned here rather than trusted.
"""
import os
import sys

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from experiments.heuristic_search.core.fftvar_feats import (  # noqa: E402
    RELABEL_INVARIANT, VARIANTS, VIDX, codes_from_word, fvar_pair, fvar_pair_words,
)
from experiments.heuristic_search.core.search_fftvar import search_fftvar  # noqa: E402
from experiments.heuristic_search.core.search_signlag import search_signlag  # noqa: E402
from experiments.heuristic_search.core.signlag_feats import pair_sign_lag  # noqa: E402
from experiments.heuristic_search.core.hfast import _pack  # noqa: E402
from experiments.search.greedy_baseline import str_to_arr  # noqa: E402

MAX_BUDGET = 500          # the local ceiling; never raise it in a test
ALPHA = "XYxy"
RELABEL = {"X": "x", "x": "X", "Y": "Y", "y": "y"}
CFG_L = {"segments": [{"upto": None, "w": {"L": 1.0}}]}


def _rand_word(rng, lo=5, hi=24):
    n = int(rng.integers(lo, hi))
    return "".join(ALPHA[i] for i in rng.integers(0, 4, n))


def _pairs(seed, k=40, lo=5, hi=24):
    rng = np.random.default_rng(seed)
    return [(_rand_word(rng, lo, hi), _rand_word(rng, lo, hi)) for _ in range(k)]


# --------------------------------------------------------------- the control gate

@pytest.mark.parametrize("wF", [0.0, 4.0])
def test_lag345_arm_is_search_signlag_pop_for_pop(wF):
    """The control arm must BE the shipped search, not agree with it.

    Every number in `results/heuristic_search/fftvar_scout/` is a difference against this arm,
    so a divergence here silently rebases the entire comparison.
    """
    for r1, r2 in _pairs(11, k=12, lo=6, hi=18):
        ref = search_signlag(r1, r2, MAX_BUDGET, CFG_L, 32, wF=wF)
        got = search_fftvar(r1, r2, MAX_BUDGET, CFG_L, 32, wF=wF, variant="lag345")
        assert got["solved"] == ref["solved"]
        assert got["nodes_explored"] == ref["nodes_explored"]
        assert got["path_length"] == ref["path_length"]
        assert got["min_relator_length"] == ref["min_relator_length"]


def test_lag345_feature_equals_pair_sign_lag():
    """The variant-0 kernel reproduces the shipped feature exactly, not approximately."""
    for r1, r2 in _pairs(12):
        codes = np.concatenate([codes_from_word(r1), codes_from_word(r2)])
        ref = pair_sign_lag(codes, 0, len(r1), len(r1), len(r2), 3, 5)
        assert fvar_pair_words(r1, r2, "lag345") == pytest.approx(ref, abs=1e-12)


def test_codes_match_hfast_pack():
    """`codes_from_word` must use hfast's alphabet, or every feature reads the wrong letters."""
    rng = np.random.default_rng(13)
    for _ in range(80):
        w = _rand_word(rng, 1, 20)
        packed = _pack(str_to_arr(w), str_to_arr(w))
        assert bytes(codes_from_word(w)) == packed[:packed.index(0)]


# --------------------------------------------------------------- ring properties

@pytest.mark.parametrize("variant", VARIANTS)
def test_rotation_invariant(variant):
    """States are stored Booth-rotated; a cut-dependent feature is not a ring feature."""
    for r1, r2 in _pairs(14, k=25):
        base = fvar_pair_words(r1, r2, variant)
        for k in (1, 3, 7):
            k1, k2 = k % len(r1), k % len(r2)
            assert fvar_pair_words(r1[k1:] + r1[:k1], r2[k2:] + r2[:k2],
                                   variant) == pytest.approx(base, abs=1e-9)


@pytest.mark.parametrize("variant", VARIANTS)
def test_relabel_invariance_matches_declaration(variant):
    """`RELABEL_INVARIANT` is a claim about an AC symmetry; pin it in both directions."""
    worst = 0.0
    for r1, r2 in _pairs(15, k=25):
        a = fvar_pair_words(r1, r2, variant)
        b = fvar_pair_words("".join(RELABEL[c] for c in r1),
                            "".join(RELABEL[c] for c in r2), variant)
        worst = max(worst, abs(a - b))
    if variant in RELABEL_INVARIANT:
        assert worst < 1e-9, f"{variant} is declared x<->X invariant but deviates by {worst:.2e}"
    else:
        assert worst > 1e-9, (f"{variant} is invariant in fact but not declared -- add it to "
                              f"RELABEL_INVARIANT")


@pytest.mark.parametrize("variant", VARIANTS)
def test_range_is_unit_per_relator(variant):
    """Every variant is normalised to per-relator [0,1] so ONE weight is portable across arms.

    A variant that escapes the range makes the fixed-weight sweep compare scales, not transforms.
    """
    pw = np.empty(128, dtype=np.float64)
    v = VIDX[variant]
    for r1, r2 in _pairs(16, k=25, lo=2, hi=48):
        codes = np.concatenate([codes_from_word(r1), codes_from_word(r2)])
        val = fvar_pair(codes, 0, len(r1), len(r1), len(r2), v, False, pw)
        assert -1e-9 <= val <= 2.0 + 1e-9, f"{variant} pair value {val} outside [0,2]"


def test_parseval_normalisation():
    """The DFT power spectrum sums to 1 over all k -- the identity the [0,1] bands rely on.

    Holds for all three channels because every one of them maps a letter to a unit-modulus
    value, so sum_j |x_j|^2 = n exactly. Break that (an unnormalised channel, a letter mapped
    to 0) and the band fractions stop being fractions, which silently rescales every arm.
    """
    from experiments.heuristic_search.core.fftvar_feats import (
        CH_COMPLEX, CH_GEN, CH_SIGN, _power_spectrum,
    )
    rng = np.random.default_rng(17)
    for _ in range(20):
        w = _rand_word(rng, 6, 40)
        codes = codes_from_word(w)
        for channel in (CH_SIGN, CH_COMPLEX, CH_GEN):
            pw = np.empty(len(w) + 4, dtype=np.float64)
            non_dc = _power_spectrum(codes, 0, len(w), channel, pw)
            assert non_dc + pw[0] == pytest.approx(1.0, abs=1e-9)


def test_gen_channel_ignores_the_exponent_entirely():
    """The whole point of the generator channel: r -> r^-1 style sign changes are invisible.

    Stronger than the relabel test above -- this flips exponents letter by letter at random, not
    by a uniform relabel, and every ``gen*`` variant must still return the identical value.
    """
    rng = np.random.default_rng(21)
    gen_variants = [v for v in VARIANTS if v.startswith("gen")]
    assert gen_variants, "no generator-channel variants registered"
    for _ in range(25):
        r1, r2 = _rand_word(rng, 6, 24), _rand_word(rng, 6, 24)
        flip = {"X": "x", "x": "X", "Y": "y", "y": "Y"}
        f1 = "".join(flip[c] if rng.random() < 0.5 else c for c in r1)
        f2 = "".join(flip[c] if rng.random() < 0.5 else c for c in r2)
        for v in gen_variants:
            assert fvar_pair_words(r1, r2, v) == pytest.approx(
                fvar_pair_words(f1, f2, v), abs=1e-12), f"{v} reads the exponent"


# --------------------------------------------------------------- search plumbing

@pytest.mark.parametrize("variant", VARIANTS)
def test_every_variant_searches(variant):
    """No variant may raise mid-search or return a malformed record."""
    for r1, r2 in _pairs(18, k=3, lo=6, hi=16):
        res = search_fftvar(r1, r2, 200, CFG_L, 32, wF=4.0, variant=variant)
        assert res["nodes_explored"] <= 200
        assert isinstance(res["solved"], bool)
        if res["solved"]:
            assert res["path_length"] is not None


def test_agg_max_is_on_the_same_scale_as_the_sum():
    """`agg_max` uses 2*max, not max, so the sum-vs-max probe does not also change the weight."""
    pw = np.empty(128, dtype=np.float64)
    v = VIDX["lag345"]
    for r1, r2 in _pairs(19, k=20):
        codes = np.concatenate([codes_from_word(r1), codes_from_word(r2)])
        s = fvar_pair(codes, 0, len(r1), len(r1), len(r2), v, False, pw)
        m = fvar_pair(codes, 0, len(r1), len(r1), len(r2), v, True, pw)
        assert m >= s - 1e-12          # 2*max >= a + b
        assert m <= 2.0 + 1e-9
