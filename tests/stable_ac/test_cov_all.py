"""Brute-force CoV family (``cov_all``): completeness, soundness, class dedup."""

import ast
import random

import pytest

from experiments.equivalence_classes.lib.autcanon import aut_canon
from experiments.greedy_tests.spec.words import inverse, str_to_word, word_to_str
from experiments.stable_ac.cov import cov, cov_all

AK3 = (str_to_word("xyxYXY"), str_to_word("xxxYYYY"))


def _ms640(step):
    with open("data/ms640_solved.txt") as f:
        rows = [ast.literal_eval(line) for line in f if line.strip()]
    out = []
    for x in rows[::step]:
        h = len(x) // 2
        out.append((tuple(v for v in x[:h] if v), tuple(v for v in x[h:] if v)))
    return out


SAMPLE = [AK3] + _ms640(40)


def _exp(w, g):
    return sum((1 if v > 0 else -1) for v in w if abs(v) == g)


def test_class_key_is_invariant_under_the_search_symmetries():
    rng = random.Random(0)
    for r1, r2 in SAMPLE:
        key = cov_all.class_key(r1, r2)
        for sx, sy, swap in [(a, b, c) for a in (1, -1) for b in (1, -1)
                             for c in (False, True)]:
            m = {1: sx * (2 if swap else 1), 2: sy * (1 if swap else 2)}
            m[-1], m[-2] = -m[1], -m[2]
            a, b = tuple(m[g] for g in r1), tuple(m[g] for g in r2)
            k = rng.randrange(len(a))
            assert cov_all.class_key(b, inverse(a[k:] + a[:k])) == key


def test_class_key_separates_a_length_changing_automorphism():
    r1, r2 = AK3
    # x -> xy: an automorphism that is not a signed permutation
    phi = {1: (1, 2), -1: (-2, -1), 2: (2,), -2: (-2,)}
    a = tuple(s for g in r1 for s in phi[g])
    b = tuple(s for g in r2 for s in phi[g])
    assert cov_all.class_key(a, b) != cov_all.class_key(r1, r2)


def test_patterns_are_exactly_the_non_overlapping_subsets():
    cyc = str_to_word("xxxxy")
    occs = cov_all.occurrences(cyc, str_to_word("xx"))
    assert [s for s, _ in occs] == [0, 1, 2]
    got = {tuple(s for s, _ in p) for p in cov_all.patterns(occs, len(cyc), 2)}
    assert got == {(), (0,), (1,), (2,), (0, 2)}


def test_seam_occurrence_is_an_ordinary_position():
    cyc = str_to_word("yxxxy")  # yy exists only across the seam
    assert cov_all.occurrences(cyc, str_to_word("yy")) == ((4, 1),)
    assert cov_all.substitute_pattern(cyc, ((4, 1),), 2) == str_to_word("zxxx")


@pytest.mark.parametrize("pair", SAMPLE, ids=lambda p: word_to_str(p[0]))
def test_contains_every_start_of_the_single_pattern_family(pair):
    r1, r2 = pair
    own = cov_all.class_key(r1, r2)
    for proper in (True, False):
        family = cov_all.subwords(r1, r2, proper=proper)
        old = {cov_all.class_key(o.r1, o.r2)
               for o in cov.enumerate_cov(r1, r2, family=family)} - {own}
        new = {r.meta["class_key"]
               for r in cov_all.enumerate_classes(r1, r2, proper=proper)}
        assert old <= new


def test_proper_rule_drops_whole_relator_words():
    r1, r2 = str_to_word("xyxxy"), str_to_word("yxxy")
    lens = {len(w) for w in cov_all.subwords(r1, r2)}
    assert lens == {2, 3, 4}
    # yxxy is all of r2 and also sits inside r1: still dropped
    assert str_to_word("yxxy") not in cov_all.subwords(r1, r2)
    assert str_to_word("yxxy") in cov_all.subwords(r1, r2, proper=False)


@pytest.mark.parametrize("pair", SAMPLE, ids=lambda p: word_to_str(p[0]))
def test_outputs_are_balanced_and_classes_are_distinct(pair):
    r1, r2 = pair
    for res in cov_all.raw_covs(r1, r2):
        det = (_exp(res.r1, 1) * _exp(res.r2, 2)
               - _exp(res.r1, 2) * _exp(res.r2, 1))
        assert abs(det) == 1
    reps = cov_all.enumerate_classes(r1, r2)
    keys = [cov_all.class_key(r.r1, r.r2) for r in reps]
    assert len(set(keys)) == len(keys)
    assert cov_all.class_key(r1, r2) not in keys
    assert sum(r.meta["multiplicity"] for r in reps) <= sum(
        1 for _ in cov_all.raw_covs(r1, r2))


def test_single_substitution_stays_in_the_input_orbit():
    for r1, r2 in SAMPLE[:6]:
        rep = aut_canon((word_to_str(r1), word_to_str(r2)))[1]
        for res in cov_all.raw_covs(r1, r2):
            if res.n_subs == 1:
                out = (word_to_str(res.r1), word_to_str(res.r2))
                assert aut_canon(out)[1] == rep
