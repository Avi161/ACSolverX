"""Abelianization Gram / seam-sign split features (advisor REVISE 2026-07-30).

Mobility ``Mob = 2(Nx1·Nx2 + Ny1·Ny2)`` equals the pre-cap Def 2.1 child count
(verified). ``Mob/L²`` is blocked as an ordering feature: R² ≈ 0.92 vs the
shipped 17-dim vector (algebraic in ``ratio`` + x-fraction).

The surviving candidate from that redirect is the *sign split of seams by
jsign*, which collapses exactly to the abelianization Gram:

    num  = |⟨ab(r1), ab(r2)⟩| = |ex1·ex2 + ey1·ey2|
         = |m_same − m_opp|
    T    = Nx1·Nx2 + Ny1·Ny2 = Mob/2
    asym = num / T   ∈ [0,1]   (T=0 only at the trivial goal → 0.0)

On presentations of 1 (``|det|=1``): ``num = sqrt(|v1|²|v2|² − 1)``.

This *is* IDEAS.md idea 8 (abelianized-distance priority) in blended form —
not a new sign-channel mechanism. R²(asym vs 17) ≈ 0.31; R²(T vs 17) ≈ 0.98
so the normalised form must be scored separately from the numerator.

Packed codes (n_gen=2 only): 1=X, 2=Y, 3=x, 4=y.
``is_inv = (c >= 3)``; ``is_x = (c & 1) == 1``.
"""
from __future__ import annotations

import numpy as np
from numba import njit


@njit(cache=True)
def _bins_one(codes, off, n):
    """Return (p,q,u,v) = (#X, #x, #Y, #y) over codes[off:off+n]."""
    p = 0
    q = 0
    u = 0
    v = 0
    for i in range(n):
        c = codes[off + i]
        if c == 1:
            p += 1
        elif c == 3:
            q += 1
        elif c == 2:
            u += 1
        elif c == 4:
            v += 1
    return p, q, u, v


@njit(cache=True)
def pair_abel_gram(codes, off1, n1, off2, n2):
    """Pair-level abelianization Gram stats.

    Returns (num, T, asym, Mob) as float64.
    """
    p1, q1, u1, v1 = _bins_one(codes, off1, n1)
    p2, q2, u2, v2 = _bins_one(codes, off2, n2)
    Nx1 = p1 + q1
    Ny1 = u1 + v1
    Nx2 = p2 + q2
    Ny2 = u2 + v2
    ex1 = p1 - q1
    ey1 = u1 - v1
    ex2 = p2 - q2
    ey2 = u2 - v2
    gram = ex1 * ex2 + ey1 * ey2
    num = abs(gram)
    T = Nx1 * Nx2 + Ny1 * Ny2
    Mob = 2 * T
    if T == 0:
        asym = 0.0
    else:
        asym = num / T
    return float(num), float(T), float(asym), float(Mob)


@njit(cache=True)
def pair_asym_norm(codes, off1, n1, off2, n2):
    """``asym = num/T`` (scale-free)."""
    _num, _T, asym, _Mob = pair_abel_gram(codes, off1, n1, off2, n2)
    return asym


@njit(cache=True)
def pair_asym_raw(codes, off1, n1, off2, n2):
    """``num / L`` — numerator normalised by total length (not by T).

    Advisor: T is 98.5% linear in the shipped 17; num has the new DOF.
    Dividing by L keeps the heap term O(1) like other scale-free features.
    """
    num, _T, _asym, _Mob = pair_abel_gram(codes, off1, n1, off2, n2)
    L = n1 + n2
    if L == 0:
        return 0.0
    return num / L


@njit(cache=True)
def pair_mob_over_L2(codes, off1, n1, off2, n2):
    """Blocked candidate ``Mob / L²`` — kept for the negative-control arm only."""
    _num, _T, _asym, Mob = pair_abel_gram(codes, off1, n1, off2, n2)
    L = n1 + n2
    if L == 0:
        return 0.0
    return Mob / (L * L)


def pair_abel_gram_words(r1: str, r2: str) -> dict:
    """Python helper from strings (analysis / reports). Codes via X=1,Y=2,x=3,y=4."""
    tbl = {"X": 1, "Y": 2, "x": 3, "y": 4}
    c1 = np.array([tbl[c] for c in r1], dtype=np.uint8)
    c2 = np.array([tbl[c] for c in r2], dtype=np.uint8)
    codes = np.concatenate([c1, c2])
    num, T, asym, Mob = pair_abel_gram(codes, 0, len(c1), len(c1), len(c2))
    L = len(c1) + len(c2)
    return {
        "num": float(num),
        "T": float(T),
        "asym": float(asym),
        "Mob": float(Mob),
        "Mob_L2": float(Mob / (L * L)) if L else 0.0,
        "num_L": float(num / L) if L else 0.0,
        "L": float(L),
    }
