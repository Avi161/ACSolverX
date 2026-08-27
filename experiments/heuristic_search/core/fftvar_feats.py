"""Spectral-transform variants for cyclic relators — a family around ``signlag_feats``.

``signlag_feats.sign_lag_mean`` is *one* point in a large design space: the exponent-sign
channel, read through a flat band of circular autocorrelation lags 3..5. That choice was made
because a real ``np.fft`` is unavailable in numba and a naive DFT was assumed too slow. This
module holds the alternatives, so the choice can be measured rather than assumed.

Three axes are varied:

  * **channel** — what real (or complex) signal a ring of letters becomes.
  * **transform** — which functional of that signal's spectrum is read.
  * **band** — which part of the spectrum, or equivalently which lags.

Every variant returns a **per-relator scalar in [0, 1]**, and the pair value is the sum over the
two relators (house convention, as ``K = k1 + k2``), so the pair lands in [0, 2] and a *fixed*
heap weight means the same thing across variants. Without that normalisation an arm sweep at
one weight compares scales, not transforms.

Code layout (verified against ``hfast._pack`` / ``hfast._arrs``, table ``(2, 4, 1, 3)`` over
``(is_x, is_inv)``, and ``_CODE_TO_CHAR = {1:'X', 2:'Y', 3:'x', 4:'y'}``)::

    generator bit  g = (c & 1)      1 -> x-family (X, x) ; 0 -> y-family (Y, y)
    exponent sign  s = -1 if c >= 3 else +1

The 17 heap features read only ``g``. Everything here that reads ``s`` is, in principle, new
information — whether it is *useful* information is what the scout measures.

Channels
--------
``sign``     s_j in {+1, -1}                         — the exponent ring alone (current work).
``gen``      g_j = +1 for x, X ; -1 for y, Y         — the generator ring, inverses ignored.
``complex``  c_j = s_j if g_j else i * s_j           — generator AND sign in one ring.

The **generator** channel is the one an AC argument actually motivates: r -> r^-1 is a symmetry of
the problem, so which letters are inverted carries no invariant information, while which generator
they are does. It was set aside earlier as redundant, but that verdict rests on two Parseval
identities — ``A[1] = L - 4K`` and ``P[0] = (L * xyimb)^2`` — which pin only the **DC and k=1**
content to features the heap already has. They say nothing about the peak, the flatness, the
centroid, or the high band, so most of this channel's spectrum was never actually screened. Hence
``genlo`` … ``genlag345`` below: the identities predict ``genlo`` is largely redundant and predict
nothing at all about the rest.

The **complex** channel matters for the opposite reason: the redundancy argument is a statement
about a *real* +-1 signal. A complex ring has no conjugate symmetry, so |C[k]| and |C[n-k]| are
independent and it carries roughly twice the content of either real channel.

Transforms
----------
Band energies over lags are the cheap face of band energies over frequencies (Wiener-Khinchin),
which is what ``sign_lag_mean`` exploits. But three spectral functionals have **no** short-lag
form and were therefore never tried: the spectral **peak** (is there one dominant period?), the
**centroid** (where does the energy sit?) and the **flatness** (tonal or noise-like?). Those need
the whole spectrum. At ``mrl = 48`` a direct DFT is <= 48*48 terms per relator, which is small
enough to simply measure instead of rule out.

Relabel invariance
------------------
``sign_lag_mean`` is *not* invariant under the generator-inversion relabel x <-> X — a documented
wart, since that relabel is an AC symmetry and the feature therefore scores two identical states
differently. Splitting the autocorrelation by whether the two positions share a generator repairs
it exactly:

    A_same[d] = (1/n) sum over i with g_i == g_{i+d} of s_i s_{i+d}
    A_diff[d] = (1/n) sum over i with g_i != g_{i+d} of s_i s_{i+d}

Under x <-> X both factors of every same-generator term flip, so ``A_same`` is *unchanged*; every
cross-generator term flips once, so ``|A_diff|`` is unchanged. Both are invariant where the
current feature is not, and they decompose it: A_sign[d] = A_same[d] + A_diff[d].

The complex channel earns the same invariance for free, which was not the reason it was added.
Writing c_j = a_j + i b_j with ``a`` carrying the x-generator signs and ``b`` the y-generator
signs, the relabel sends a -> -a and fixes b, i.e. c -> -conj(c), whose transform is
|C_new[k]| = |C[n-k]|. The relabel therefore *reverses* the spectrum rather than changing it, so
**every functional symmetric in k <-> n-k is invariant** — which covers ``cplxpeak`` (a max over
all k) and ``cplxlo`` (a band that already contains both k and n-k). No real channel has this
property: for a real signal the spectrum is already its own reverse, so the reversal argument is
vacuous there and the relabel bites. That makes the complex-ring variants the only *spectral*
ones that respect the symmetry.
"""
from __future__ import annotations

import math

import numpy as np
from numba import njit

# ---------------------------------------------------------------- variant registry

#: Variant name -> integer code passed into the njit kernels. Order is the report order.
VARIANTS = (
    "lag345",    # 0  CURRENT: mean_{d=3..5} |A_sign[d]|                      (control)
    "lag12",     # 1  mean_{d=1..2} |A_sign[d]|          — local alternation / high band
    "lag68",     # 2  mean_{d=6..8} |A_sign[d]|          — longer-period band
    "lagall",    # 3  mean_{d=1..n/2} |A_sign[d]|        — whole-lag average
    "dftlo",     # 4  low-frequency energy fraction, k in {1,2,3} + mirrors
    "dfthi",     # 5  high-frequency energy fraction, |k| > n/4
    "dftpeak",   # 6  max_{k>=1} P[k] / (1 - P[0])       — strength of the single best period
    "dftcent",   # 7  spectral centroid, normalised to [0,1]
    "dftflat",   # 8  spectral flatness (geometric / arithmetic mean)
    "cplxlo",    # 9  complex 4-letter ring, low-frequency energy fraction
    "cplxpeak",  # 10 complex 4-letter ring, spectral peak
    "same",      # 11 mean_{d=3..5} |A_same[d]|          — x<->X invariant
    "diff",      # 12 mean_{d=3..5} |A_diff[d]|          — x<->X invariant
    # generator ring: x, X -> +1 ; y, Y -> -1. Inverses ignored entirely, which is what the
    # r -> r^-1 symmetry argues for. Every one of these is x<->X invariant by construction —
    # the channel cannot see the exponent — so the relabel wart cannot arise here at all.
    "genlo",     # 13 low-frequency energy fraction      — the one Parseval predicts is redundant
    "genhi",     # 14 high-frequency energy fraction
    "genpeak",   # 15 max_{k>=1} P[k] / (1 - P[0])
    "gencent",   # 16 spectral centroid
    "genflat",   # 17 spectral flatness
    "genlag345",  # 18 mean_{d=3..5} |A_gen[d]| — direct analogue of the shipped sign feature
)
VIDX = {v: i for i, v in enumerate(VARIANTS)}
N_VARIANT = len(VARIANTS)

#: Variants that are exactly invariant under the generator-inversion relabel x <-> X, verified
#: empirically by the scout's preflight and pinned by ``tests/heuristic_search/test_fftvar.py``
#: (both fail if this set is wrong). All variants are rotation-invariant; these also respect the
#: relabel — the six ``gen*`` ones trivially, since that channel never reads the exponent.
RELABEL_INVARIANT = (
    "cplxlo", "cplxpeak", "same", "diff",
    "genlo", "genhi", "genpeak", "gencent", "genflat", "genlag345",
)

#: Channel codes for ``_power_spectrum``.
CH_SIGN, CH_COMPLEX, CH_GEN = 0, 1, 2

_EPS = 1e-12


# ---------------------------------------------------------------- autocorrelation kernels

@njit(cache=True)
def _acorr_band(codes, off, n, lo, hi):
    """mean over d in [lo, hi] of |A_sign[d]|, A_sign[d] = (1/n) sum_i s_i s_{i+d}."""
    if n < 2:
        return 0.0
    acc = 0.0
    n_lag = 0
    for d in range(lo, hi + 1):
        if d >= n:
            break
        t = 0.0
        for i in range(n):
            c0 = codes[off + i]
            c1 = codes[off + ((i + d) % n)]
            s0 = -1.0 if c0 >= 3 else 1.0
            s1 = -1.0 if c1 >= 3 else 1.0
            t += s0 * s1
        acc += abs(t / n)
        n_lag += 1
    if n_lag == 0:
        return 0.0
    return acc / n_lag


@njit(cache=True)
def _acorr_split(codes, off, n, lo, hi, want_same):
    """mean over d in [lo, hi] of |A_same[d]| (want_same) or |A_diff[d]|.

    Both are invariant under the x <-> X relabel; see the module docstring.
    """
    if n < 2:
        return 0.0
    acc = 0.0
    n_lag = 0
    for d in range(lo, hi + 1):
        if d >= n:
            break
        t = 0.0
        for i in range(n):
            c0 = codes[off + i]
            c1 = codes[off + ((i + d) % n)]
            g0 = c0 & 1
            g1 = c1 & 1
            hit = (g0 == g1) if want_same else (g0 != g1)
            if hit:
                s0 = -1.0 if c0 >= 3 else 1.0
                s1 = -1.0 if c1 >= 3 else 1.0
                t += s0 * s1
        acc += abs(t / n)
        n_lag += 1
    if n_lag == 0:
        return 0.0
    return acc / n_lag


# ---------------------------------------------------------------- direct DFT kernels

@njit(cache=True)
def _power_spectrum(codes, off, n, channel, pw):
    """Fill ``pw[0:n]`` with P[k] = |F[k]|^2 / n^2 and return sum_{k>=1} P[k].

    channel 0 (sign)    : x_j = s_j,  s = -1 if the letter is inverted else +1.
    channel 1 (complex) : x_j = s_j        for an x-generator
                                 i * s_j   for a y-generator.
    channel 2 (gen)     : x_j = +1 for x, X ;  -1 for y, Y  — the exponent is never read.

    All three have |x_j| = 1, so Parseval gives sum_k P[k] = 1 exactly and every band fraction
    below is a genuine proportion of the ring's energy. That is what makes a single heap
    weight portable across these variants.
    """
    two_pi_n = 2.0 * math.pi / n
    for k in range(n):
        re = 0.0
        im = 0.0
        for j in range(n):
            c = codes[off + j]
            ang = two_pi_n * k * j
            ca = math.cos(ang)
            sa = math.sin(ang)
            if channel == 2:
                g = 1.0 if (c & 1) == 1 else -1.0
                re += g * ca
                im -= g * sa
            else:
                s = -1.0 if c >= 3 else 1.0
                if channel == 1 and (c & 1) == 0:
                    # x_j = i * s  ->  x_j * e^{-i ang} = s * (sin + i cos)
                    re += s * sa
                    im += s * ca
                else:
                    re += s * ca
                    im -= s * sa
        pw[k] = (re * re + im * im) / (n * n)
    tot = 0.0
    for k in range(1, n):
        tot += pw[k]
    return tot


@njit(cache=True)
def _acorr_gen(codes, off, n, lo, hi):
    """mean over d in [lo, hi] of |A_gen[d]|, on the generator ring (exponent ignored)."""
    if n < 2:
        return 0.0
    acc = 0.0
    n_lag = 0
    for d in range(lo, hi + 1):
        if d >= n:
            break
        t = 0.0
        for i in range(n):
            g0 = 1.0 if (codes[off + i] & 1) == 1 else -1.0
            g1 = 1.0 if (codes[off + ((i + d) % n)] & 1) == 1 else -1.0
            t += g0 * g1
        acc += abs(t / n)
        n_lag += 1
    if n_lag == 0:
        return 0.0
    return acc / n_lag


@njit(cache=True)
def _dft_stat(codes, off, n, which, channel, pw):
    """Spectral functional of the ring, in [0, 1].

    which:   0 = low-band fraction, 1 = high-band, 2 = peak, 3 = centroid, 4 = flatness.
    channel: 0 = sign, 1 = complex, 2 = generator (see ``_power_spectrum``).
    All are taken over k >= 1 and normalised by the non-DC energy, so a constant ring (no DC
    structure to speak of) cannot dominate the scale.
    """
    if n < 4:
        return 0.0
    tot = _power_spectrum(codes, off, n, channel, pw)
    if tot <= _EPS:
        return 0.0

    if which == 0:                       # low band: |k| in {1, 2, 3}
        acc = 0.0
        for k in range(1, n):
            kk = k if k <= n - k else n - k
            if kk <= 3:
                acc += pw[k]
        return acc / tot

    if which == 1:                       # high band: |k| > n/4
        acc = 0.0
        thr = n * 0.25
        for k in range(1, n):
            kk = k if k <= n - k else n - k
            if kk > thr:
                acc += pw[k]
        return acc / tot

    if which == 2:                       # spectral peak
        best = 0.0
        for k in range(1, n):
            if pw[k] > best:
                best = pw[k]
        return best / tot

    if which == 3:                       # centroid, normalised by the Nyquist index n/2
        acc = 0.0
        for k in range(1, n):
            kk = k if k <= n - k else n - k
            acc += kk * pw[k]
        return acc / tot / (0.5 * n)

    # which == 4: spectral flatness = geometric mean / arithmetic mean over k >= 1
    log_acc = 0.0
    for k in range(1, n):
        log_acc += math.log(pw[k] + _EPS)
    geo = math.exp(log_acc / (n - 1))
    ari = tot / (n - 1)
    if ari <= _EPS:
        return 0.0
    v = geo / ari
    return v if v <= 1.0 else 1.0


# ---------------------------------------------------------------- dispatch

@njit(cache=True)
def fvar_one(codes, off, n, variant, pw):
    """One relator -> scalar in [0, 1]. ``pw`` is a scratch buffer of length >= n."""
    if variant == 0:
        return _acorr_band(codes, off, n, 3, 5)
    if variant == 1:
        return _acorr_band(codes, off, n, 1, 2)
    if variant == 2:
        return _acorr_band(codes, off, n, 6, 8)
    if variant == 3:
        return _acorr_band(codes, off, n, 1, max(1, n // 2))
    if variant == 4:
        return _dft_stat(codes, off, n, 0, 0, pw)
    if variant == 5:
        return _dft_stat(codes, off, n, 1, 0, pw)
    if variant == 6:
        return _dft_stat(codes, off, n, 2, 0, pw)
    if variant == 7:
        return _dft_stat(codes, off, n, 3, 0, pw)
    if variant == 8:
        return _dft_stat(codes, off, n, 4, 0, pw)
    if variant == 9:
        return _dft_stat(codes, off, n, 0, 1, pw)
    if variant == 10:
        return _dft_stat(codes, off, n, 2, 1, pw)
    if variant == 11:
        return _acorr_split(codes, off, n, 3, 5, True)
    if variant == 12:
        return _acorr_split(codes, off, n, 3, 5, False)
    if variant == 13:
        return _dft_stat(codes, off, n, 0, 2, pw)
    if variant == 14:
        return _dft_stat(codes, off, n, 1, 2, pw)
    if variant == 15:
        return _dft_stat(codes, off, n, 2, 2, pw)
    if variant == 16:
        return _dft_stat(codes, off, n, 3, 2, pw)
    if variant == 17:
        return _dft_stat(codes, off, n, 4, 2, pw)
    if variant == 18:
        return _acorr_gen(codes, off, n, 3, 5)
    return 0.0


@njit(cache=True)
def fvar_pair(codes, off1, n1, off2, n2, variant, agg_max, pw):
    """Pair value in [0, 2].

    ``agg_max`` swaps the house sum for ``2 * max`` over the two relators — the same move that
    made MK beat K in the shipped heuristic, kept on the same scale so one weight still fits.
    """
    a = fvar_one(codes, off1, n1, variant, pw)
    b = fvar_one(codes, off2, n2, variant, pw)
    if agg_max:
        return 2.0 * (a if a > b else b)
    return a + b


# ---------------------------------------------------------------- numpy side (analysis only)

_TBL = {'X': 1, 'Y': 2, 'x': 3, 'y': 4}


def codes_from_word(w):
    """Word string -> packed uint8 codes, matching ``hfast._pack``'s alphabet."""
    return np.array([_TBL[c] for c in w], dtype=np.uint8)


def fvar_pair_words(r1, r2, variant, agg_max=False):
    """Convenience wrapper for reports and redundancy fits (not used mid-search)."""
    v = VIDX[variant] if isinstance(variant, str) else int(variant)
    c1 = codes_from_word(r1)
    c2 = codes_from_word(r2)
    codes = np.concatenate([c1, c2])
    pw = np.empty(max(len(c1), len(c2), 4) + 1, dtype=np.float64)
    return float(fvar_pair(codes, 0, len(c1), len(c1), len(c2), v, agg_max, pw))
