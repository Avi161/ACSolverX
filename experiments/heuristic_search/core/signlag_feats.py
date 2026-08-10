"""Sign-channel spectral / lag features for cyclic relators (mentor FFT idea).

Mentor: map X/Y letters → Fourier. Relators are rings; the DFT magnitude of a
letter/sign channel is rotation-invariant (common phase cancels).

Advisor REVISE (2026-07-30):
  * Generator-bipolar DFT's low-order content *is* K / xyimb (Parseval identities).
  * The heap's 17 features use only the generator bit (``codes & 1``) — signs are new.
  * Prefer **sign-channel** short-lag circular autocorrelations (lags ≥3) over a
    mid-search ``np.fft`` (unsupported in numba; naive DFT is 4–15× ``_feats_nj``).
  * Band energy of the power spectrum ≡ fixed-weight sum of autocorrelations.

Identities (generator bipolar s∈{+1,−1}):
  A[1] = L − 4K ;  P[0] = (L·xyimb)² ; Laplacian moment ∝ K.

This module exposes:
  * ``fft_scalars_numpy`` — didactic FFT view (analysis / reports)
  * ``sign_lag_nj`` — O(L) lag-3..5 mean |autocorr| on the sign channel (search)
"""
from __future__ import annotations

import numpy as np
from numba import njit

# packed letter codes match greedy_baseline / hfast: X=0? check str_to_arr
# hfast _CODE_TO_CHAR and packing: we work from string side for numpy FFT,
# and from uint8 packed codes for njit (2*gen + sign bits as in _arrs).


def _sign_seq_from_word(w: str) -> np.ndarray:
    """Exponent-sign ring: X,Y → +1 ; x,y → −1. Length L."""
    out = np.empty(len(w), dtype=np.float64)
    for i, c in enumerate(w):
        out[i] = 1.0 if c in "XY" else -1.0
    return out


def _gen_seq_from_word(w: str) -> np.ndarray:
    """Generator bipolar: x-gen → +1, y-gen → −1 (ignores exponent sign)."""
    out = np.empty(len(w), dtype=np.float64)
    for i, c in enumerate(w):
        out[i] = 1.0 if c.lower() == "x" else -1.0
    return out


def fft_scalars_numpy(w: str, channel: str = "sign") -> dict:
    """Didactic FFT scalars on one ring. Not used mid-search."""
    if len(w) < 2:
        return {"Fhf": 0.0, "Fpeak": 0.0, "FspecK": 0.0, "L": float(len(w))}
    s = _sign_seq_from_word(w) if channel == "sign" else _gen_seq_from_word(w)
    L = len(s)
    mag = np.abs(np.fft.rfft(s))
    # Parseval: sum mag[k]^2 related to energy; use mag[1:] 
    power = mag ** 2
    # normalize Fhf by total energy L^2 (Parseval for ±1 signal: sum s^2 = L,
    # but rfft scaling — use sum of power over k>0 plus careful DC)
    tot = float(np.sum(power))  # includes DC
    if tot <= 0:
        return {"Fhf": 0.0, "Fpeak": 0.0, "FspecK": 0.0, "L": float(L)}
    # high-frequency = upper half of positive freqs
    n = len(mag)
    hi0 = max(1, n // 2)
    Fhf = float(np.sum(power[hi0:]) / tot)
    Fpeak = float(np.max(mag[1:]) / L) if n > 1 else 0.0
    ks = np.arange(n, dtype=np.float64)
    FspecK = float(np.sum(ks[1:] * power[1:]) / max(np.sum(power[1:]), 1e-12) / max(L, 1))
    return {"Fhf": Fhf, "Fpeak": Fpeak, "FspecK": FspecK, "L": float(L)}


def pair_fft_scalars(r1: str, r2: str, channel: str = "sign") -> dict:
    """Sum of per-ring FFT scalars (house convention like K = k1+k2)."""
    a, b = fft_scalars_numpy(r1, channel), fft_scalars_numpy(r2, channel)
    return {k: a[k] + b[k] for k in ("Fhf", "Fpeak", "FspecK")}


@njit(cache=True)
def _sign_from_codes(codes, off, n, out_s):
    """Packed uint8 letter codes → ±1 exponent signs. code layout from hfast._arrs:
    gen bit = codes&1 (0=x-family?); check: X=(False,False)? 

    From hfast._arrs:
      np.stack(((c1 & 1) == 1, c1 >= 3), axis=1)
    and str_to_arr in greedy uses is_y, is_inv.

    Safer: use the same table as _pack inverse. Codes in blob are 1..4 via tbl.
    Actually expand returns blob of packed keys — children keys are bytes.

    We'll pass is_inv bit array instead from caller.
    """
    for i in range(n):
        # codes[off+i] in {1,2,3,4} after pack table (2,4,1,3) from (is_y, is_inv)
        # Inverse of tbl (2,4,1,3): 1→(0,0)? Let's map by bit convention used in feats:
        # In _feats_nj, r_isx from runs — different path.
        #
        # For sign: is_inv True → −1. From stack: col1 = (c>=3) is is_inv in _arrs.
        c = codes[off + i]
        out_s[i] = -1.0 if c >= 3 else 1.0


@njit(cache=True)
def sign_lag_mean(codes, off, n, lags_lo=3, lags_hi=5):
    """Mean |circular autocorr| of exponent-sign channel at lags lags_lo..lags_hi.

    A[d] = (1/n) * sum_i s[i]*s[(i+d) mod n],  s=±1.
    Returns mean over d in [lags_lo, lags_hi] of |A[d]|  (scale-free in ±1).
    """
    if n < 2:
        return 0.0
    # signs
    # packed codes from key bytes: values are 1,2,3,4 (see _pack tbl)
    # _arrs: is_inv = (c >= 3)
    acc = 0.0
    n_lags = 0
    for d in range(lags_lo, lags_hi + 1):
        if d >= n:
            break
        s = 0.0
        for i in range(n):
            c0 = codes[off + i]
            c1 = codes[off + ((i + d) % n)]
            sg0 = -1.0 if c0 >= 3 else 1.0
            sg1 = -1.0 if c1 >= 3 else 1.0
            s += sg0 * sg1
        acc += abs(s / n)
        n_lags += 1
    if n_lags == 0:
        return 0.0
    return acc / n_lags


@njit(cache=True)
def pair_sign_lag(codes, off1, n1, off2, n2, lags_lo=3, lags_hi=5):
    """Sum of per-ring sign-lag means (like K = k1+k2)."""
    return (sign_lag_mean(codes, off1, n1, lags_lo, lags_hi)
            + sign_lag_mean(codes, off2, n2, lags_lo, lags_hi))
