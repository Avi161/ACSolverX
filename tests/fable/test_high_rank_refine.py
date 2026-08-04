"""Calibration suite for the high-rank refinement stack (tasks A3 + A4, fable line).

Covers ``experiments/stable_ac/fable/high_rank_refine.py`` (the two refinement families
and the replay certifier) and ``experiments/stable_ac/fable/high_rank_gamma_sweep.py``
(the exact-census driver).

Every number asserted here is either recomputed inside the test or is the KNOWN-GOOD
ANCHOR of the task: the linear left-peel triangulation of ``AK(3)`` at rank 9 is

    ("aYX", "bXA", "cyB", "cXY", "dXX", "eXD", "fyE", "gyF", "gYY")

with census size 86,400, germ degrees ``a..g = 2, x = 6, y = 7``, and exact
``minimum_defect = 4``.  Nothing in this file adjusts the anchor.

The suite deliberately re-derives the anchor's *rank-2* census too, because the single
most informative number the sweep produces is that the two defect histograms are equal.
"""

from __future__ import annotations

import json
import os

import pytest

from experiments.stable_ac.fable import ac_words as W
from experiments.stable_ac.fable import high_rank_refine as HR
from experiments.stable_ac.fable import high_rank_gamma_sweep as SW
from experiments.stable_ac.fable.neuwirth_rank_n import gamma_N_factorial_n

AK3 = ("xyxYXY", "xxxYYYY")
ANCHOR = ("aYX", "bXA", "cyB", "cXY", "dXX", "eXD", "fyE", "gyF", "gYY")
ANCHOR_DEGREES = {"a": 2, "b": 2, "c": 2, "d": 2, "e": 2, "f": 2, "g": 2, "x": 6, "y": 7}
ANCHOR_CENSUS = 86_400
ANCHOR_MIN_DEFECT = 4
SEED = 20260804

CHEAP = ("xxxxY", "yXXX")          # AC-trivial, rank-2 gamma_N = 0, census 720


# --------------------------------------------------------------------------------------
# (a) word algebra
# --------------------------------------------------------------------------------------


def test_free_reduction_cancels_only_adjacent_inverse_pairs():
    assert HR.free_reduce("xX") == ""
    assert HR.free_reduce("xyYX") == ""
    assert HR.free_reduce("xyYx") == "xx"
    assert HR.free_reduce("xxxYYYY") == "xxxYYYY"
    assert HR.free_reduce("") == ""
    # free reduction is idempotent and never lengthens a word
    for w in ("xyxYXY", "aYXxb", "xXyYzZ", "abABba"):
        once = HR.free_reduce(w)
        assert HR.free_reduce(once) == once
        assert len(once) <= len(w)
        assert HR.is_freely_reduced(once)


def test_inverse_and_rotation_are_involutive_and_cyclic():
    for w in ("xyxYXY", "aYX", "gYY"):
        assert HR.inverse(HR.inverse(w)) == w
        assert HR.free_reduce(w + HR.inverse(w)) == ""
        for k in range(len(w)):
            assert len(HR.rotate(w, k)) == len(w)
            assert HR.rotate(HR.rotate(w, k), len(w) - k) == w
    assert HR.rotate("abcd", 1) == "bcda"
    assert HR.rotate("abcd", 4) == "abcd"


def test_cyclic_reduction_gate_rejects_non_cyclically_reduced_input():
    assert HR.is_cyclically_reduced("xyxYXY")
    assert not HR.is_cyclically_reduced("yxYY")
    with pytest.raises(HR.RefinementError):
        HR.triangulate(("yxYY", "yyyXY"))


# --------------------------------------------------------------------------------------
# (b) the KNOWN-GOOD ANCHOR
# --------------------------------------------------------------------------------------


def test_ak3_linear_left_triangulation_reproduces_the_anchor_word_for_word():
    ref = HR.triangulate(AK3, bracket="linear", end="left", rot=0)
    assert ref.words == ANCHOR
    assert ref.generators == tuple("abcdefgxy")
    assert ref.rank == 9 == len(ref.words)
    # the Triangulation Lemma's terminal rank: n + sum max(0, |r_i| - 3)
    assert ref.rank == 2 + max(0, 6 - 3) + max(0, 7 - 3)
    assert max(len(w) for w in ref.words) == 3


def test_anchor_germ_degrees_and_census_size():
    assert HR.germ_degrees(ANCHOR) == ANCHOR_DEGREES
    assert HR.census_of(ANCHOR) == ANCHOR_CENSUS


def test_anchor_exact_gamma_N_is_defect_four_and_equals_ak3s_own_census():
    high = gamma_N_factorial_n(ANCHOR, keep_accepting=False)
    low = gamma_N_factorial_n(AK3, keep_accepting=False)
    assert high["status"] == "OK"
    assert high["minimum_defect"] == ANCHOR_MIN_DEFECT
    assert high["expected_cases"] == ANCHOR_CENSUS
    assert high["link_components"] == 1
    # the finding the sweep is built to expose: triangulation changes nothing at all
    assert low["status"] == "OK"
    assert high["expected_cases"] == low["expected_cases"]
    assert high["defect_histogram"] == low["defect_histogram"]
    assert high["minimum_defect"] == low["minimum_defect"]


def test_anchor_substitutes_back_to_ak3_exactly():
    ref = HR.triangulate(AK3, bracket="linear", end="left", rot=0)
    cert = HR.certify_refinement(AK3, ANCHOR, ref.trace)
    assert set(cert.relations) == {"identical"}
    assert tuple(cert.substituted) == AK3 or set(cert.substituted) == set(AK3)
    assert dict(cert.expansions)["g"] == "xxxYY"
    assert dict(cert.definition_words)["a"] == "xy"
    assert cert.trace_consistent is True
    # the anchor is genuinely ambiguous to read back: c and g each lead two relators
    assert dict(cert.ambiguous_definitions) == {"c": 2, "g": 2}


# --------------------------------------------------------------------------------------
# (c) the certifier accepts correct refinements ...
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("params", [
    {"bracket": "linear", "end": "left", "rot": 0},
    {"bracket": "linear", "end": "right", "rot": 0},
    {"bracket": "linear", "end": "left", "rot": 3},
    {"bracket": "linear", "end": "right", "rot": 5, "share": True},
    {"bracket": "balanced", "rot": 0},
    {"bracket": "balanced", "rot": 2, "share": True},
    {"bracket": "balanced", "rot": 4, "order": (1, 0), "share": True},
])
def test_certifier_accepts_every_triangulation_scheme(params):
    ref = HR.triangulate(AK3, **params)
    cert = HR.certify_refinement(ref.source, ref.presentation, ref.trace)
    assert cert.balanced and cert.all_cyclically_reduced
    assert len(cert.definition_order) == ref.rank - 2
    assert set(cert.relations) <= {"identical", "rotation", "inversion",
                                   "rotation+inversion"}
    assert cert.trace_consistent is True
    assert max(len(w) for w in ref.words) <= 3


def test_certifier_accepts_generator_splittings():
    for ref in HR.enumerate_splits(AK3, limit=6, seed=SEED, certify=False):
        cert = HR.certify_refinement(ref.source, ref.presentation, ref.trace)
        assert cert.balanced
        assert set(cert.relations) <= {"identical", "rotation", "inversion",
                                       "rotation+inversion"}
        assert cert.trace_consistent is True


# --------------------------------------------------------------------------------------
# ... and REJECTS corrupted ones (five kinds)
# --------------------------------------------------------------------------------------


def test_certifier_rejects_an_unbalanced_refinement():
    broken = ANCHOR[:-1]                      # 9 generators, 8 relators
    with pytest.raises(HR.CertificationError, match="not balanced"):
        HR.certify_refinement(AK3, broken)


def test_certifier_rejects_a_corrupted_definition_relator():
    broken = ("aYY",) + ANCHOR[1:]            # a = yy instead of a = xy
    with pytest.raises(HR.CertificationError, match="does not reproduce"):
        HR.certify_refinement(AK3, broken)


def test_certifier_rejects_a_relator_that_is_not_cyclically_reduced():
    broken = ANCHOR[:4] + ("dXXD",) + ANCHOR[5:]
    with pytest.raises(HR.CertificationError, match="not cyclically reduced"):
        HR.certify_refinement(AK3, broken)


def test_certifier_rejects_an_undefined_fresh_generator():
    broken = ("xaY",) + ANCHOR[1:]            # nothing of the form a * (word)^-1
    with pytest.raises(HR.CertificationError, match="no relator of the form"):
        HR.certify_refinement(AK3, broken)


def test_certifier_rejects_a_cyclic_definition_layering():
    base = ("xx", "yy")
    broken = ("aB", "bA", "xx", "yy")         # a = b and b = a: no legal order
    with pytest.raises(HR.CertificationError, match="no legal definition layering"):
        HR.certify_refinement(base, broken)


def test_certifier_rejects_a_residual_that_replays_to_the_wrong_word():
    broken = ANCHOR[:3] + ("cXX",) + ANCHOR[4:]
    with pytest.raises(HR.CertificationError):
        HR.certify_refinement(AK3, broken)


# --------------------------------------------------------------------------------------
# (d) enumeration: distinct, certified, deterministic
# --------------------------------------------------------------------------------------


def test_enumerate_triangulations_returns_distinct_certified_outputs():
    family = HR.enumerate_triangulations(AK3, limit=8, seed=SEED)
    assert len(family) == 8
    keys = [HR.canonical_form(r.words) for r in family]
    assert len(set(keys)) == len(keys)
    for ref in family:
        assert ref.certificate is not None
        assert ref.certificate.balanced
        assert max(len(w) for w in ref.words) <= 3
        assert len(ref.words) == len(ref.generators)
        # re-certifying from the words alone must also succeed
        HR.certify_refinement(AK3, ref.words)


def test_enumeration_is_deterministic_under_a_fixed_seed():
    a = HR.enumerate_triangulations(AK3, limit=6, seed=SEED)
    b = HR.enumerate_triangulations(AK3, limit=6, seed=SEED)
    assert [r.words for r in a] == [r.words for r in b]
    assert [r.params for r in a] == [r.params for r in b]
    c = HR.enumerate_triangulations(AK3, limit=6, seed=SEED + 1)
    assert [r.words for r in c] != [r.words for r in a]      # the seed does something
    for ref in c:
        assert ref.certificate is not None

    s1 = HR.enumerate_splits(AK3, limit=5, seed=SEED)
    s2 = HR.enumerate_splits(AK3, limit=5, seed=SEED)
    assert [r.words for r in s1] == [r.words for r in s2]


def test_enumeration_covers_both_brackets_and_both_share_settings():
    family = HR.enumerate_triangulations(AK3, limit=8, seed=SEED)
    assert {r.params["bracket"] for r in family} == {"linear", "balanced"}
    assert {r.params["share"] for r in family} == {False, True}


def test_enumeration_is_bounded_by_the_family_on_a_small_input():
    family = HR.enumerate_triangulations(("xxxx", "yyyy"), limit=1000, seed=0)
    assert 0 < len(family) < 1000
    assert len({HR.canonical_form(r.words) for r in family}) == len(family)


# --------------------------------------------------------------------------------------
# (e) link structure: subdivision (triangulation) and vertex split (generator split)
# --------------------------------------------------------------------------------------


def test_smooth_vertices_suppresses_a_degree_two_vertex():
    edges = [("a", "z"), ("z", "b"), ("a", "b")]
    assert HR.smooth_vertices(edges, ["z"]) == [("a", "b"), ("a", "b")]
    with pytest.raises(HR.RefinementError):
        HR.smooth_vertices([("a", "z"), ("z", "b"), ("z", "c")], ["z"])


def test_triangulation_without_sharing_is_a_link_subdivision():
    for params in ({"bracket": "linear", "end": "left", "rot": 0},
                   {"bracket": "linear", "end": "right", "rot": 4},
                   {"bracket": "balanced", "rot": 0},
                   {"bracket": "balanced", "rot": 3}):
        ref = HR.triangulate(AK3, **params)
        cert = HR.link_smoothing_certificate(ref.source, ref.presentation)
        assert cert["is_subdivision"], (params, cert["reason"])
        assert set(cert["fresh_degrees"].values()) == {2}
        # a subdivision cannot change the census size
        assert HR.census_of(ref.words, ref.generators) == HR.census_of(AK3)


def test_sharing_can_leave_a_fresh_germ_of_degree_three():
    ref = HR.triangulate(AK3, bracket="balanced", rot=0, share=True)
    degrees = HR.germ_degrees(ref.words, ref.generators)
    assert ref.rank == 8 < 9                       # a shared definition saves a generator
    assert max(degrees[g] for g in "abcdef") == 3
    cert = HR.link_smoothing_certificate(ref.source, ref.presentation)
    assert cert["is_subdivision"] is False
    assert HR.census_of(ref.words, ref.generators) < HR.census_of(AK3)
    HR.certify_refinement(ref.source, ref.presentation, ref.trace)


def test_generator_splitting_makes_the_input_link_a_minor():
    for ref in HR.enumerate_splits(AK3, limit=8, seed=SEED):
        cert = HR.split_minor_certificate(ref)
        assert cert["is_contraction"], (ref.params, cert)
        assert cert["contracted_edges"] == cert["expected_contracted_edges"]


def test_splitting_a_generator_never_makes_a_non_planar_support_planar():
    # rank-3 presentations whose SIMPLE support is certified non-planar
    nonplanar = (("xxyzx", "ZyzyyZ", "ZXYY"), ("ZyyZ", "XzYxY", "xzzy"))
    for words in nonplanar:
        assert HR.support_planarity(words, budget=300_000) == "NONPLANAR"
        seen = 0
        for ref in HR.enumerate_splits(words, limit=4, seed=3):
            assert HR.split_minor_certificate(ref)["is_contraction"]
            status = HR.support_planarity(ref.words, ref.generators, budget=300_000)
            assert status != "PLANAR", (ref.params, status)
            seen += status == "NONPLANAR"
        assert seen > 0                            # not every check was budget-limited


def test_splitting_never_lowers_gamma_N_on_the_cheap_input():
    base = gamma_N_factorial_n(CHEAP, keep_accepting=False)
    assert base["status"] == "OK"
    for ref in HR.enumerate_splits(CHEAP, limit=6, seed=SEED):
        got = gamma_N_factorial_n(ref.words, ref.generators, keep_accepting=False)
        assert got["status"] == "OK"
        assert got["minimum_defect"] >= base["minimum_defect"], ref.params


def test_triangulation_preserves_the_whole_defect_histogram_on_the_cheap_input():
    base = gamma_N_factorial_n(CHEAP, keep_accepting=False)
    for ref in HR.enumerate_triangulations(CHEAP, limit=6, seed=SEED):
        cert = HR.link_smoothing_certificate(ref.source, ref.presentation)
        got = gamma_N_factorial_n(ref.words, ref.generators, keep_accepting=False)
        assert got["status"] == "OK"
        if cert["is_subdivision"]:
            assert got["expected_cases"] == base["expected_cases"], ref.params
            assert got["defect_histogram"] == base["defect_histogram"], ref.params
        else:                                       # sharing: still never an improvement
            assert got["minimum_defect"] >= base["minimum_defect"], ref.params


# --------------------------------------------------------------------------------------
# (f) the sweep driver
# --------------------------------------------------------------------------------------


def test_sweep_inputs_are_cyclically_reduced_and_the_ladder_provenance_replays():
    for name, spec in SW.INPUTS.items():
        words = tuple(spec["words"])
        for w in words:
            assert HR.is_cyclically_reduced(w), (name, w)
        if spec["moves"] is not None:
            got = W.replay(("x", "y"), spec["moves"], 9)[-1]
            assert got == words, (name, got, words)


@pytest.mark.parametrize("name", ["pos_a", "pos_b", "pos_c", "pos_d"])
def test_positive_ladder_really_has_gamma_N_zero(name):
    words = tuple(SW.INPUTS[name]["words"])
    report = gamma_N_factorial_n(words, keep_accepting=False)
    assert report["status"] == "OK"
    assert report["minimum_defect"] == 0, name


def test_sweep_writes_rows_and_a_readable_summary(tmp_path):
    out = str(tmp_path / "sweep.json")
    summary = SW.sweep(["pos_a"], limit=2, seed=SEED, cap_rotations=200_000,
                       item_timeout=30, max_seconds=90.0,
                       schemes=("triangulate", "split"), out_path=out)
    assert summary["rows"] > 0
    assert summary["rows_decided"] == summary["rows"]
    assert os.path.exists(out)
    with open(out, encoding="utf-8") as handle:
        payload = json.load(handle)
    assert payload["summary"]["record"] == "high_rank_gamma_sweep"
    rows = payload["rows"]
    assert len(rows) == summary["rows"]
    for row in rows:
        assert row["certificate"] is not None
        assert row["status"] in ("OK", "UNKNOWN_SIZE", "TIMEOUT")
        assert row["output_rank"] == len(row["output_words"])
        assert sorted(row["germ_degrees"].values()) == row["germ_degree_multiset"]
    jsonl = os.path.splitext(out)[0] + ".jsonl"
    with open(jsonl, encoding="utf-8") as handle:
        assert sum(1 for line in handle if line.strip()) == len(rows)
    ladder = summary["positive_ladder_detection"]
    assert ladder["inputs_with_gamma_N_zero"] == ["pos_a"]
    assert ladder["detection_rate"] is not None


def test_sweep_census_helper_skips_an_oversized_family_instead_of_running_it():
    report = SW.census(AK3, HR.generators_of(AK3), cap_rotations=100, item_timeout=30)
    assert report["status"] == "UNKNOWN_SIZE"
    assert report["expected_cases"] == ANCHOR_CENSUS
    assert report["minimum_defect"] is None
