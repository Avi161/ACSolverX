"""acx.core: words, canonical forms, encodings, moves, priorities, config."""
import itertools
import random

import numpy as np
import pytest

from acx.core.config import SearchConfig, parse_override
from acx.core.moves import (Move, apply_raw, destabilize, elementary_step, enumerate_moves,
                            from_legacy, s_step, seam_cancels, stabilize, to_legacy)
from acx.core.priority import features, length, s20_mk2
from acx.core.words import (Presentation, canonical_rels, canonical_word, fmt, inverse,
                            is_cyclically_reduced, parse, reduce, rotate, state_key, to_bool_array,
                            from_bool_array, to_codes)

RNG = random.Random(7)


def rand_word(n, gens=2):
    return tuple(RNG.choice([g for g in range(-gens, gens + 1) if g]) for _ in range(n))


def booth(g):
    return (-abs(g), g > 0)


def test_parse_format_roundtrip():
    assert parse("xYyX") == (1, -2, 2, -1)
    assert fmt((1, -2, 3, -3)) == "xYzZ"
    assert inverse(parse("xyY")) == parse("yYX")


def test_rotate_is_np_roll_of_main_encoding():
    for _ in range(50):
        w = rand_word(RNG.randint(1, 9))
        k = RNG.randint(0, 20)
        assert from_bool_array(np.roll(to_bool_array(w), 2 * k)) == rotate(w, k)


def test_reduce():
    assert reduce(parse("xyYX")) == ()
    assert reduce(parse("Xyx")) == parse("y")
    assert reduce(parse("Xyx"), cyclic=False) == parse("Xyx")
    for _ in range(300):
        w = rand_word(RNG.randint(0, 14))
        r = reduce(w)
        assert is_cyclically_reduced(r)
        assert reduce(r) == r
        ex = lambda u: (sum((g == 1) - (g == -1) for g in u), sum((g == 2) - (g == -2) for g in u))
        assert ex(r) == ex(w)


def test_canonical_word_is_the_booth_least_orbit_element():
    for _ in range(300):
        w = reduce(rand_word(RNG.randint(1, 10), RNG.choice([2, 3])))
        orbit = [rotate(u, k) for u in (w, inverse(w)) for k in range(len(w))]
        want = min(orbit, key=lambda u: [booth(g) for g in u]) if w else w
        assert canonical_word(w) == want


def test_canonical_pair_sorted_by_length_then_booth():
    assert canonical_rels((parse("yX"), parse("x"))) == (parse("X"), parse("Yx"))
    assert canonical_rels((parse("x"), parse("Y"))) == (parse("Y"), parse("X"))


def test_codes_and_state_key_sort_like_main_string_keys():
    assert list(to_codes(parse("XYxy"))) == [1, 2, 3, 4]
    assert to_bool_array(parse("xXyY")).tolist() == [[1, 1], [1, 0], [0, 1], [0, 0]]
    pairs = [(rand_word(RNG.randint(0, 5)), rand_word(RNG.randint(0, 5))) for _ in range(300)]
    by_key = sorted(pairs, key=state_key)
    by_str = sorted(pairs, key=lambda p: (fmt(p[0]), fmt(p[1])))
    assert [state_key(p) for p in by_key] == [state_key(p) for p in by_str]


def test_presentation():
    p = Presentation.from_flat([-2, -2, -1, 2, 1, 0, 0, -2, 1, 0])
    assert p.strs == ("YYXyx", "Yx") and p.n_gen == 2
    assert Presentation.parse("Y", "yxY").is_trivial()
    assert not Presentation.parse("x", "x").is_trivial()
    with pytest.raises(ValueError):
        Presentation(2, ((3,),))


def test_enumerate_moves_is_every_cancelling_seam_in_main_order():
    for n_rel in (2, 3):
        rels = tuple(reduce(rand_word(RNG.randint(1, 6), 3)) or (1,) for _ in range(n_rel))
        brute = [Move(i, j, s, k1, k2)
                 for i in range(n_rel) for j in range(n_rel) if i != j for s in (1, -1)
                 for k1 in range(len(rels[i])) for k2 in range(len(rels[j]))
                 if seam_cancels(rels, Move(i, j, s, k1, k2))]
        assert list(enumerate_moves(rels)) == brute


def test_legacy_moves_and_s_step():
    m = from_legacy(2, -1, 3, 1)
    assert m == Move(1, 0, -1, 3, 1) and to_legacy(m) == (2, -1, 3, 1)
    p = Presentation.parse("Yx", "YYXyx").canonical()
    for mv in enumerate_moves(p.rels):
        child = s_step(p, mv)
        assert child == Presentation(2, apply_raw(p.rels, mv)).reduced().canonical()
    bad = next(Move(0, 1, 1, a, b) for a, b in itertools.product(range(2), range(5))
               if not seam_cancels(p.rels, Move(0, 1, 1, a, b)))
    with pytest.raises(ValueError):
        s_step(p, bad)


def test_elementary_and_stable_moves():
    p = Presentation.parse("xy", "y")
    assert elementary_step(p, {"op": "invert", "target": 2}).strs == ("xy", "Y")
    assert elementary_step(p, {"op": "swap"}).strs == ("y", "xy")
    assert elementary_step(p, {"op": "conjugate", "target": 1, "by": "x"}).strs == ("yx", "y")
    q = elementary_step(elementary_step(p, {"op": "invert", "target": 2}),
                        {"op": "multiply", "target": 1, "source": 2})
    assert q.strs == ("x", "Y")
    s = stabilize(p)
    assert s.n_gen == 3 and s.strs == ("xy", "y", "z")
    assert destabilize(s) == p
    with pytest.raises(ValueError):
        destabilize(Presentation.parse("xz", "y", "z"))
    with pytest.raises(ValueError):
        elementary_step(p, {"op": "multiply", "target": 1, "source": 1})


@pytest.mark.parametrize("rels, L, mk, s, score", [
    (("xxY", "yyyX"), 7, 1, 1.5, 39.0),     # knots 1 each; mx = 3/2, my = 4/2
    (("xxx", "y"), 4, 0, 1.0, 24.0),         # pure powers have no knots
    (("xyx", "y"), 4, 1, 1.0, 26.0),         # x-run wraps the seam: blocks x2, y1
    (("xx", "X"), 3, 0, 1.5, 33.0),          # y absent: S is the x mean
])
def test_s20_mk2(rels, L, mk, s, score):
    words = tuple(map(parse, rels))
    assert features(words) == (L, mk, s)
    assert s20_mk2(words) == score and length(words) == L


def test_config(tmp_path):
    c = SearchConfig()
    assert (c.priority, c.cap, c.backend, c.capture_path) == ("length", 24, "spec", True)
    f = tmp_path / "c.toml"
    f.write_text('[search]\npriority = "s20_mk2"\ncap = 48\nbudget = 500\n')
    c = SearchConfig.load(f, ["cap=none", "backend=fast", "trace=true"])
    assert (c.priority, c.cap, c.budget, c.backend, c.trace) == ("s20_mk2", None, 500, "fast", True)
    f.write_text("budget = 7\n")
    assert SearchConfig.load(f).budget == 7
    assert parse_override("priority=s20_mk2") == ("priority", "s20_mk2")
    for bad in (["nope=1"], ["cap=-1"], ["priority=recommended"], ["backend=gpu"], ["budget=0"]):
        with pytest.raises(ValueError):
            SearchConfig().with_overrides(bad)
