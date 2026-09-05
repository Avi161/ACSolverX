"""Equivalence pin for the numba canonicalizer: ``aut_min == aut_canon[:2]``
and ``relabel_min == words.relabel_key``, everywhere.

Four corpora, so a bug in one regime can't hide behind another: (1) all 124
class reps (the production inputs), (2) real CoV hop outputs (the production
call sites), (3) seeded random fuzz incl. degenerate words, (4) grown pairs
(random second-kind auto compositions — the long-word regime a deep ladder
enters), which double as an orbit-invariance check. On top of these,
``test_mu_ladder_big.py::test_climb_matches_mu_ladder`` compares whole fast
climbs against slow ``mu_ladder.climb_one`` rows, end to end.
"""

import csv
import os
import random

import pytest

from experiments.equivalence_classes.lib.autcanon import AUTOS, aut_canon
from experiments.equivalence_classes.lib.words import apply_hom, relabel_key
from experiments.stable_ac.cov.autcanon_fast import (
    aut_min,
    relabel_min,
    warm,
)


@pytest.fixture(scope="module", autouse=True)
def _warm():
    warm()


@pytest.fixture(scope="module")
def aca_pairs(repo_root):
    rows = list(csv.DictReader(
        open(os.path.join(repo_root, "data/ms_unsolved_reps/aca_124.csv"))))
    assert len(rows) == 124
    return [(r["r1"], r["r2"]) for r in rows]


def _agree(pairs):
    for p in pairs:
        t, rep, _ = aut_canon(p)
        assert aut_min(p) == (t, rep), p
        assert relabel_min(p) == relabel_key(p), p


def test_all_124_class_reps(aca_pairs):
    _agree(aca_pairs)


def test_real_hop_outputs(aca_pairs):
    # the production call sites: score actual CoV outputs of two classes
    from experiments.stable_ac.cov.mu_descent_scan import hop_outputs
    outs = []
    for p in (aca_pairs[115], aca_pairs[1]):     # aca_115 (AK3's class), aca_1
        outs.extend(op for _, op, _ in hop_outputs(*p, 24).values())
    assert outs
    _agree(outs[:80])


def test_fuzz_and_degenerate_words():
    random.seed(7)
    fz = [("x", "y"), ("xyXY", "x"), ("xx", "yy"), ("", "xy"), ("xYxy", ""),
          ("xX", "y"), ("xxxYYYY", "xyxYXY")]     # incl. a reduce-to-empty and AK(3)
    for _ in range(150):
        fz.append(("".join(random.choice("xXyY") for _ in range(random.randint(1, 18))),
                   "".join(random.choice("xXyY") for _ in range(random.randint(1, 18)))))
    _agree(fz)


def test_grown_pairs_and_orbit_invariance(aca_pairs):
    # push pairs up their orbit with random second-kind autos: the long-word
    # regime, and aut_min must stay constant along the way
    random.seed(11)
    for p in aca_pairs[:8]:
        base = aut_min(p)
        a, b = p
        for _ in range(5):
            au = random.choice(AUTOS[8:])
            a, b = apply_hom(a, au), apply_hom(b, au)
            assert aut_min((a, b)) == base
        t, rep, _ = aut_canon((a, b))
        assert base == (t, rep)


def test_relabel_min_refines_the_orbit(aca_pairs):
    # equal relabel keys must imply equal aut_min (the memo-key contract):
    # a signed-perm image shares the key AND the orbit result
    from experiments.equivalence_classes.lib.words import SIGNED_PERMS
    for p in aca_pairs[:10]:
        for _, img in SIGNED_PERMS:
            q = (apply_hom(p[0], img), apply_hom(p[1], img))
            assert relabel_min(q) == relabel_min(p)
            assert aut_min(q) == aut_min(p)


def test_ladder_actually_uses_the_fast_path():
    # a silent ImportError fallback would turn every speedup claim false
    from experiments.stable_ac.cov import mu_ladder_big
    assert mu_ladder_big.FAST_CANON is True
