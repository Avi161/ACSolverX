"""Tests for the S12 Stable Certificate Hunt instrument (orchestrator, fable line).

Covers ``experiments/stable_ac/fable/s12_hunt.py``.  The properties asserted here are the
ones whose failure would silently corrupt a verdict:

* the decision stack never converts out-of-scope or over-budget into a NO;
* the seen-set key collapses relator order, cyclic rotation and inversion (filed trap
  ``experiments/lessons/harvest-dedup-on-reduced-forms.md``);
* proposed moves are legal AC2 slides that keep the presentation balanced;
* the search actually spends its node budget (three bugs in the first revision each caused
  it to stall at a few dozen pops against a 1,500-node budget);
* the length caps are RELATIVE to the root, so a long base is not mechanically starved.

Anchors that are NOT adjusted by this file: AK(3) = ("xyxYXY","xxxYYYY") is NOT_SPHERICAL,
and ("xyXY","xxy") is SPHERICAL.
"""

from __future__ import annotations

import random

import pytest

from experiments.stable_ac.fable import s12_hunt as H


# --------------------------------------------------------------------------- words

def test_freered_and_cyclered():
    assert H.freered("xXy") == "y"
    assert H.freered("xyYX") == ""
    assert H.cyclered("xyxYXY") == "xyxYXY"          # AK(3) r1 is cyclically reduced
    assert H.cyclered("xyyX") == "yy"                 # conjugation peels off
    assert H.inv("xyX") == "xYX"


def test_canon_collapses_order_rotation_inversion():
    base = ("xyxYXY", "xxxYYYY")
    assert H.canon(base) == H.canon(base[::-1])                       # relator order
    rot = (base[0][2:] + base[0][:2], base[1])
    assert H.canon(base) == H.canon(rot)                              # cyclic rotation
    assert H.canon(base) == H.canon((H.inv(base[0]), base[1]))         # inversion
    assert H.canon(base) != H.canon(("xyxYXY", "xxYYYY"))              # genuinely different


# --------------------------------------------------------------------------- decide

def test_decide_anchors():
    assert H.decide(("xyxYXY", "xxxYYYY"))["verdict"] == "NOT_SPHERICAL"
    assert H.decide(("xyXY", "xxy"))["verdict"] == "SPHERICAL"


def test_decide_never_returns_a_false_no():
    """A disconnected link is out of the solver's scope; it must be UNDECIDED, not a NO."""
    d = H.decide(("xyxYXY", "xxxYYYY", "z"))
    assert d["verdict"] in {H.UNDECIDED, "SPHERICAL", "NOT_SPHERICAL"}
    if d["verdict"] == H.UNDECIDED:
        assert "method" in d
    # a single generator is degenerate, never a verdict
    assert H.decide(("xxx", "xx"))["verdict"] == H.UNDECIDED


def test_decide_census_cap_yields_undecided_not_no():
    d = H.decide(("xyxYXY", "xxxYYYY"), census_cap=1)
    assert d["verdict"] != "SPHERICAL"          # cap must never manufacture a positive


# --------------------------------------------------------------------------- moves

def test_slides_are_balanced_and_within_caps():
    rng = random.Random(0)
    base = ("xyxYXY", "xxxYYYY")
    gens = ("x", "y")
    for nb in H.slides(base, gens, rng, max_rel=12, max_tot=26, k=60):
        assert len(nb) == len(base)                        # balanced
        assert all(w == H.cyclered(w) for w in nb)         # cyclically reduced
        assert max(len(w) for w in nb) <= 12
        assert sum(len(w) for w in nb) <= 26


def test_slides_change_exactly_one_relator():
    rng = random.Random(3)
    base = ("xyxYXY", "xxxYYYY")
    for nb in H.slides(base, ("x", "y"), rng, max_rel=14, max_tot=30, k=40):
        differing = [i for i in range(2) if nb[i] != base[i]]
        assert len(differing) == 1


# --------------------------------------------------------------------------- search

def test_hunt_spends_its_node_budget():
    """Regression for the stall: reseeding from the root exhausted `seen` and the hunt
    stopped at a few dozen pops.  It must now reach the budget (or find a hit first)."""
    rng = random.Random(11)
    state, _, stats = H.hunt(("xyxYXY", "xxxYYYY"), 0, 250, rng)
    assert state is None or stats["spherical"] == 1
    if state is None:
        assert stats["pops"] == 250
    assert stats["decided"] > 0


def test_hunt_caps_are_relative_to_the_root():
    """A long root must get proportionally more room, not the same absolute box."""
    short = ("xyxYXY", "xxxYYYY")                       # total 13
    long_ = ("xyxYXYxyxYXY", "xxxYYYYxxxYYYY")          # total 26
    rng = random.Random(5)
    seen_short, seen_long = set(), set()
    for _ in range(40):
        for nb in H.slides(short, ("x", "y"), rng, max_rel=None or 13 + 8,
                           max_tot=13 + 8, k=5):
            seen_short.add(sum(len(w) for w in nb))
        for nb in H.slides(long_, ("x", "y"), rng, max_rel=26 + 8, max_tot=26 + 8, k=5):
            seen_long.add(sum(len(w) for w in nb))
    assert seen_long and max(seen_long) > max(seen_short)


def test_hunt_reports_a_root_that_already_carries_the_certificate():
    """Regression: the first revision decided only CHILDREN, so a root that was already
    SPHERICAL was silently missed — a false negative at every kstab, and at kstab = 0 the
    root IS the input presentation."""
    state, dec, stats = H.hunt(("xyXY", "xxy"), 0, 50, random.Random(0))
    assert state == ("xyXY", "xxy")
    assert dec["verdict"] == "SPHERICAL"
    assert stats["pops"] == 0            # found before expanding anything


def test_hunt_can_fire_from_a_non_thickenable_root():
    """A hunter that can never hit makes every null worthless.  From a NOT_SPHERICAL root
    that is AC-trivial, some seed must reach a certificate."""
    assert H.decide(("xxYYY", "xyxYXY"))["verdict"] == "NOT_SPHERICAL"     # AK(2), a root
    hits = 0
    for seed in range(8):
        state, dec, _ = H.hunt(("xxYYY", "xyxYXY"), 0, 900, random.Random(seed),
                               headroom=4)
        if state is not None:
            assert dec["verdict"] == "SPHERICAL"
            assert H.decide(state)["verdict"] == "SPHERICAL"     # independent re-check
            assert state != ("xxYYY", "xyxYXY")
            hits += 1
    assert hits > 0, "the hunter never fired on any seed; its nulls would be uninformative"


# --------------------------------------------------------------------------- data

def test_ladder_members_are_balanced_and_long_enough():
    lad = H.load_ladder(6, random.Random(1))
    assert len(lad) == 6
    for w in lad:
        assert len(w) == 2
        assert all(len(x) >= 3 for x in w)
        assert 13 <= sum(len(x) for x in w) <= 25


@pytest.mark.parametrize("kstab", [0, 1])
def test_hunt_stabilizes_the_requested_number_of_times(kstab):
    rng = random.Random(7)
    _, _, stats = H.hunt(("xyxYXY", "xxxYYYY"), kstab, 20, rng)
    assert stats["pops"] <= 20
