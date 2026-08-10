"""Unit tests for abelianization-Gram / asym features (0 search nodes)."""
from __future__ import annotations

import math

import numpy as np
import pytest

from experiments.heuristic_search.core.abel_gram_feats import (
    pair_abel_gram,
    pair_abel_gram_words,
    pair_asym_norm,
    pair_asym_raw,
    pair_mob_over_L2,
)


def _codes(r1: str, r2: str):
    tbl = {"X": 1, "Y": 2, "x": 3, "y": 4}
    c1 = np.array([tbl[c] for c in r1], dtype=np.uint8)
    c2 = np.array([tbl[c] for c in r2], dtype=np.uint8)
    return np.concatenate([c1, c2]), len(c1), len(c2)


def test_gram_equals_msame_mopp():
    r1, r2 = "XxYy", "XYxy"
    codes, n1, n2 = _codes(r1, r2)
    num, T, asym, Mob = pair_abel_gram(codes, 0, n1, n1, n2)
    # manual bins
    # X=1,x=3,Y=2,y=4
    p1 = r1.count("X"); q1 = r1.count("x"); u1 = r1.count("Y"); v1 = r1.count("y")
    p2 = r2.count("X"); q2 = r2.count("x"); u2 = r2.count("Y"); v2 = r2.count("y")
    m_same = p1*p2 + q1*q2 + u1*u2 + v1*v2
    m_opp = p1*q2 + q1*p2 + u1*v2 + v1*u2
    assert m_same + m_opp == T
    assert abs(m_same - m_opp) == num
    assert Mob == 2 * T
    assert asym == pytest.approx(num / T)


def test_trivial_T_zero_guard():
    # standard presentation <x, y> up to inv — one pure-x, one pure-y, |exp|=1
    codes, n1, n2 = _codes("X", "Y")
    num, T, asym, Mob = pair_abel_gram(codes, 0, n1, n1, n2)
    assert T == 0
    assert num == 0
    assert asym == 0.0
    assert Mob == 0.0


def test_det1_lagrange_on_hand_pair():
    # freely chosen pair with |det|=1: <xy, x> → ab columns (1,1)/(1,0), det=-1
    g = pair_abel_gram_words("XY", "X")
    # ex1=1,ey1=1, ex2=1,ey2=0 → gram=1; |v1|^2=2, |v2|^2=1 → sqrt(2-1)=1
    assert g["num"] == pytest.approx(1.0)
    assert g["T"] == 1 * 1 + 1 * 0  # Nx1=1,Nx2=1,Ny1=1,Ny2=0 → T=1
    assert g["asym"] == pytest.approx(1.0)


def test_mode_helpers_agree():
    codes, n1, n2 = _codes("XYxyXY", "xYXy")
    num, T, asym, Mob = pair_abel_gram(codes, 0, n1, n1, n2)
    assert pair_asym_norm(codes, 0, n1, n1, n2) == pytest.approx(asym)
    L = n1 + n2
    assert pair_asym_raw(codes, 0, n1, n1, n2) == pytest.approx(num / L)
    assert pair_mob_over_L2(codes, 0, n1, n1, n2) == pytest.approx(Mob / (L * L))


def test_words_helper_matches_njit():
    r1, r2 = "xYXyX", "YYxx"
    g = pair_abel_gram_words(r1, r2)
    codes, n1, n2 = _codes(r1, r2)
    num, T, asym, Mob = pair_abel_gram(codes, 0, n1, n1, n2)
    assert g["num"] == num
    assert g["T"] == T
    assert g["asym"] == asym
    assert g["Mob"] == Mob
