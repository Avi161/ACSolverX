"""acx.aut: Whitehead canonical form (pure vs numba parity), orbit pairs, certificate transport."""
import csv
import itertools
import os
import random

import pytest

from acx.aut import (AUTOS, are_automorphic, aut_canon, automorphism, check, images, invert, orbit_key,
                     solve_via_aut_min, transport)
from acx.aut.whitehead import IDENTITY, apply_pres
from acx.core.words import Presentation
from acx.search import search
from acx.verify import replay

from conftest import ROOT, dataset

# benchmark/ladder/ladder_pairs.csv (origin/claude/ac19-theorem-strength-8v1wp6): an easy original
# and its Aut-minimal ladder representative (levels 9-10). These 8 rows are used when the CSV is absent.
PAIRS = [
    ("YXXyxYXXXYxxx", "YXyXXyxxx", "YYXXXyx", "YXyxxxxxyXyxx"),
    ("YXXXYxyXXYxxx", "YXXXyxYxx", "YYXXXyx", "YXyxxxxxyXyxx"),
    ("YYXYxxxYXyXX", "YXyXXXyxxxx", "YXXXXyxYx", "YXXYXXyXYxYXXX"),
    ("YYxxxYXXyXX", "YXyXXXyxxxx", "YYXXXXyx", "YYXXXYXXyXX"),
    ("YXXXyXXYxxxx", "YXyXXXyxxxx", "YYXXXXyx", "YXXyXXXYx"),
    ("YXXXyXXYxxxx", "YXyxYXXXyxx", "YYXXXyXX", "YXyxYXXXyxx"),
    ("YYxYXXYxYx", "YYxxyXX", "YXXyXyxx", "YYYxxxYYx"),
    ("YYYXyyyxx", "YYYxyxyxyyxx", "YXXXyXyxxx", "YYYXYxYxxxx"),
]


def _pairs():
    path = os.path.join(ROOT, "benchmark", "ladder", "ladder_pairs.csv")
    if not os.path.exists(path):
        return PAIRS
    with open(path) as f:
        return [(r["orig_r1"], r["orig_r2"], r["rep_r1"], r["rep_r2"]) for r in csv.DictReader(f)]


def _p(*strs):
    return Presentation.parse(*strs, n_gen=2)


def _walk(pres, rng, steps=6):
    """``pres`` pushed up its orbit by random second-kind Whitehead autos."""
    return apply_pres(pres, tuple(rng.randrange(8, len(AUTOS)) for _ in range(steps)))


# --- pure Whitehead -------------------------------------------------------------------------------

def test_known_orbits():
    a, b, c = (aut_canon(_p(*s)) for s in [("YYYYXyyyx", "YYXYxYx"), ("XXXXXXYxxxyxx", "YXXYxyxx"),
                                             ("YXYxyx", "YYYYxxx")])
    assert a.rep == b.rep != c.rep
    assert a.total == sum(map(len, a.rep.rels))
    assert aut_canon(_p("xyxYXY", "xxxYYYY")).rep == c.rep.canonical()     # AK(3) written two ways
    assert c.rep.strs == ("YXYxyx", "YYYYxxx")
    assert aut_canon(_p("xyX", "x")).rep.strs == ("Y", "X")


def test_witness_and_inverse():
    rng = random.Random(3)
    for pres in dataset("data/ms640_solved.txt")[:60]:
        ac = aut_canon(pres)
        assert check(pres, ac.rep, ac.phi)
        assert aut_canon(ac.rep) == (ac.total, ac.rep, ())          # the rep is its own canonical form
        assert aut_canon(_walk(pres, rng))[:2] == ac[:2]           # orbit invariant
    for _ in range(50):
        phi = tuple(rng.randrange(len(AUTOS)) for _ in range(rng.randint(0, 8)))
        assert images(phi + invert(phi)) == IDENTITY == images(invert(phi) + phi)


def test_level_cap_raises():
    with pytest.raises(RuntimeError, match="level_cap"):
        aut_canon(_p("YYYYXyyyx", "YYXYxYx"), level_cap=1)


def test_ladder_pairs_are_automorphic():
    pairs = _pairs()
    reps = []
    for o1, o2, q1, q2 in pairs:
        orig, rep = _p(o1, o2), _p(q1, q2)
        assert aut_canon(orig).rep == rep.canonical()             # the ladder rep IS the Aut-min form
        phi = automorphism(orig, rep)
        assert apply_pres(orig, phi).reduced().canonical() == rep.canonical()
        reps.append(rep.canonical())
    distinct = {r: o for r, o in zip(reps, pairs)}
    assert len(distinct) >= 5
    a, b = list(distinct.values())[:2]
    assert not are_automorphic(_p(*a[:2]), _p(*b[:2]))


def test_reps_match_the_published_orbit_table():
    """data/AC19_extended_aut_min.csv is the source branch's own output: same reps, in its string order."""
    path = os.path.join(ROOT, "data", "AC19_extended_aut_min.csv")
    if not os.path.exists(path):
        pytest.skip("data/AC19_extended_aut_min.csv not shipped")
    rows = dataset("data/AC19_extended.txt")
    checked = 0
    with open(path) as f:
        for rec in itertools.islice(csv.DictReader(f), 120):
            rep = _p(rec["r1"], rec["r2"]).canonical()
            for m in map(int, rec["members"].split()[:2]):
                assert aut_canon(rows[m]).rep == rep
                checked += 1
    assert checked >= 200


# --- pure vs numba --------------------------------------------------------------------------------

def test_fast_matches_pure_on_ac19_extended():
    pytest.importorskip("numba")
    rows = dataset("data/AC19_extended.txt")
    sample = rows[::len(rows) // 2000][:2000]
    assert len(sample) == 2000
    rng = random.Random(11)
    sample += [_walk(p, rng) for p in sample[:100]]                        # the long-word regime
    sample += [_p(*s) for s in [("x", "y"), ("xyXY", "x"), ("xx", "yy"), ("", "xy"), ("xYxy", ""),
                                ("xX", "y"), ("xxxYYYY", "xyxYXY")]]       # degenerate words
    for _ in range(200):
        sample.append(_p(*("".join(rng.choice("xXyY") for _ in range(rng.randint(1, 18))) for _ in "ab")))
    for pres in sample:
        assert orbit_key(pres, "fast") == orbit_key(pres, "spec"), pres


# --- transport ------------------------------------------------------------------------------------

def test_transport_round_trip_on_ac19_extended():
    """Search the Aut-min rep, transport the path, replay it on the original row."""
    done = 0
    for pres in dataset("data/AC19_extended.txt")[::997]:
        if not aut_canon(pres).phi:
            continue
        res, path = solve_via_aut_min(pres, budget=100)
        if path is None:
            continue
        states = replay(pres, path, normalize=False)
        assert states[0] == pres and states[-1].is_trivial()
        assert all(isinstance(m, dict) for m in path)
        done += 1
        if done == 20:
            break
    assert done == 20


def test_transport_carries_an_easy_original_onto_its_hard_representative():
    o1, o2, q1, q2 = PAIRS[0]                                             # level 1 -> level 9
    orig, rep = _p(o1, o2), _p(q1, q2)
    res = search(orig, budget=2000)
    assert res.solved
    path = transport(rep, automorphism(rep, orig), res.path, res.start)
    assert replay(rep, path, normalize=False)[-1].is_trivial()


def test_transport_of_mixed_and_noncyclic_paths():
    pres = dataset("data/AC19_extended.txt")[997]
    ac = aut_canon(pres)
    assert ac.phi
    res = search(ac.rep, budget=2000)
    mixed = [{"op": "conjugate", "target": 1, "by": "x"}, {"op": "conjugate", "target": 1, "by": "X"},
             {"op": "invert", "target": 2}, {"op": "swap"}] + list(res.path)
    replay(pres, transport(pres, ac.phi, mixed, res.start), normalize=False)
    _, path = solve_via_aut_min(pres, budget=2000, cyclic=False)
    replay(pres, path, cyclic=False, normalize=False)


def test_transport_on_already_trivial_and_unreduced_rows():
    rng, solved = random.Random(2), 0
    for strs in [("x", "y"), ("y", "x"), ("xy", "y"), ("Xyx", "x"), ("yXx", "xyY")]:
        pres = _p(*strs)
        res, path = solve_via_aut_min(pres, budget=50)
        assert res.solved and replay(pres, path, normalize=False)[-1].is_trivial()
    for pres in dataset("data/ms640_solved.txt")[:30]:                      # conjugated, inverted, shuffled input
        rels = [(g,) + (r[k:] + r[:k] if rng.random() < .5 else tuple(-a for a in reversed(r))) + (-g,)
                for r, g, k in ((r, rng.choice((1, -1, 2, -2)), rng.randrange(len(r))) for r in pres.rels)]
        raw = apply_pres(Presentation(2, tuple(rels)), tuple(rng.randrange(8, len(AUTOS)) for _ in range(5)))
        _, path = solve_via_aut_min(raw, budget=500)
        if path is not None:
            assert replay(raw, path, normalize=False)[-1].is_trivial()
            solved += 1
    assert solved >= 15


def test_transport_rejects_a_wrong_frame():
    pres = dataset("data/AC19_extended.txt")[997]
    ac = aut_canon(pres)
    res = search(ac.rep, budget=2000)
    with pytest.raises(ValueError, match="matches"):
        transport(pres, (), res.path, res.start)                           # identity is not the witness
