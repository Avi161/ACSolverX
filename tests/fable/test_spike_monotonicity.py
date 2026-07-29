"""Tests for ``experiments/stable_ac/fable/spike_monotonicity.py``.

The load-bearing checks are:

* the recorded fixture ``("xyXY","xxy")`` gamma_N 0 vs ``("xyXY","yYxxy")`` gamma_N 1
  (reduction destroying non-thickenability), which pins both the sign convention and
  the halving convention;
* that spiked complexes really are decided by the CENSUS and not by the solver -- the
  R1c-v2 rank-n solver must fail closed (``UNSUPPORTED``) on the loop-bearing spiked
  word while the census returns ``OK``;
* that the fast numba census agrees with the audited ``gamma_N_factorial_n`` on a
  battery of loop-bearing and loopless words;
* determinism of every tier;
* coverage accounting: measured + skipped == attempted, everywhere.
"""

from __future__ import annotations

import json
import os

import pytest

from experiments.stable_ac.fable import spike_monotonicity as sm
from experiments.stable_ac.fable.neuwirth_rank_n import (
    UNSUPPORTED,
    gamma_N_factorial_n,
    solve_spherical_n,
)

FIXTURE_REDUCED = ("xyXY", "xxy")
FIXTURE_SPIKED = ("xyXY", "yYxxy")


# --------------------------------------------------------------------------------------
# spike mechanics
# --------------------------------------------------------------------------------------


def test_spike_inserts_a_cancelling_pair():
    assert sm.spike("xxy", 0, "y") == "yYxxy"
    assert sm.spike("xxy", 3, "x") == "xxyxX"
    assert sm.spike("xxy", 1, "Y") == "xYyxy"
    with pytest.raises(ValueError):
        sm.spike("xxy", 0, "z")
    with pytest.raises(ValueError):
        sm.spike("xxy", 4, "x")


def test_spike_is_the_inverse_of_one_free_reduction_step():
    from experiments.stable_ac.fable.ac_words import free_reduce
    for word in ("xxy", "xyXY", "xxxYYYY"):
        for pos in range(len(word) + 1):
            for c in sm.LETTERS:
                assert free_reduce(sm.spike(word, pos, c)) == free_reduce(word)


def test_spike_sites_and_variants_cover_everything():
    words = ("xyXY", "xxy")
    sites = sm.spike_sites(words)
    assert len(sites) == (len(words[0]) + 1) * 4 + (len(words[1]) + 1) * 4
    variants = sm.spiked_variants(words)
    # every distinct canonical variant is reachable from some enumerated site
    keys = {sm.canon_exact_pair(sm.apply_site(words, s)) for s in sites}
    assert set(variants) == keys


def test_canon_exact_does_not_reduce():
    # ac_words.canon_rel cyclically reduces; the exact key must not.
    from experiments.stable_ac.fable.ac_words import canon_rel
    assert canon_rel("yYxxy") == canon_rel("xxy")
    assert sm.canon_exact_rel("yYxxy") != sm.canon_exact_rel("xxy")
    assert len(sm.canon_exact_rel("yYxxy")) == 5


def test_canon_exact_pair_is_rotation_inversion_swap_invariant():
    from experiments.stable_ac.fable.ac_words import inverse
    a = ("xyXY", "yYxxy")
    assert sm.canon_exact_pair(a) == sm.canon_exact_pair(("yYxxy", "xyXY"))       # swap
    assert sm.canon_exact_pair(a) == sm.canon_exact_pair(("yXYx", "Yxxyy"))       # rotation
    assert sm.canon_exact_pair(a) == sm.canon_exact_pair((inverse("xyXY"), "yYxxy"))
    assert sm.canon_exact_pair(a) == sm.canon_exact_pair(("xyXY", inverse("yYxxy")))


# --------------------------------------------------------------------------------------
# the recorded fixture
# --------------------------------------------------------------------------------------


def test_recorded_fixture_reduction_destroys_non_thickenability():
    g_red, info_red = sm.gamma_N(FIXTURE_REDUCED)
    g_spk, info_spk = sm.gamma_N(FIXTURE_SPIKED)
    assert g_red == 0
    assert g_spk == 1
    assert info_red["minimum_defect"] == 0
    assert info_spk["minimum_defect"] == 2
    assert g_spk > g_red


def test_fixture_matches_the_audited_census_exactly():
    for words in (FIXTURE_REDUCED, FIXTURE_SPIKED):
        chk = sm.cross_check(words)
        assert chk["agree"], chk


# --------------------------------------------------------------------------------------
# the census, not the solver, is what decides spiked words
# --------------------------------------------------------------------------------------


def test_solver_fails_closed_on_the_spiked_word_but_the_census_decides_it():
    decision = solve_spherical_n(FIXTURE_SPIKED, ("x", "y"))
    assert decision.verdict == UNSUPPORTED
    assert "loop" in (decision.reason or "")
    census = gamma_N_factorial_n(FIXTURE_SPIKED, ("x", "y"), keep_accepting=False)
    assert census["status"] == "OK"
    assert census["minimum_defect"] == 2
    fast = sm.census_defects(FIXTURE_SPIKED)
    assert fast["status"] == "OK"
    assert fast["gamma_N"] == 1


def test_every_spike_of_a_reduced_pair_is_loop_bearing_and_solver_unsupported():
    base = ("xyXY", "xxy")
    variants = sm.spiked_variants(base)
    assert variants
    for _key, (words, _site) in list(sorted(variants.items()))[:8]:
        assert sm.presentation_profile(words)["has_A_loop"] is True
        assert solve_spherical_n(words, ("x", "y")).verdict == UNSUPPORTED
        assert sm.census_defects(words)["status"] == "OK"


# --------------------------------------------------------------------------------------
# engine agreement
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("words", [
    ("xyXY", "xxy"),
    ("xyXY", "yYxxy"),
    ("xxxYYYY", "xyxYXY"),
    ("xXxxxYYYY", "xyxYXY"),
    ("YYY", "YXyXX"),
    ("xXYYY", "YXyXX"),
    ("X", "YYXXYxx"),
    ("yYX", "YYXXYxx"),
])
def test_fast_census_agrees_with_audited_census(words):
    chk = sm.cross_check(words)
    assert chk["agree"], chk
    assert chk["fast"]["enumerated_cases"] == chk["fast"]["expected_cases"]


def test_engine_agreement_over_a_deterministic_battery():
    bases, _ = sm.enumerate_bases(5)
    assert bases
    checked = 0
    for base in bases:
        assert sm.cross_check(base)["agree"]
        checked += 1
        for _key, (words, _site) in list(sorted(sm.spiked_variants(base).items()))[:3]:
            assert sm.cross_check(words)["agree"]
            checked += 1
    assert checked > 100


def test_census_cap_is_respected_and_reported():
    info = sm.census_defects(("xxxYYYY", "xyxYXY"), cap=10)
    assert info["status"] == "SKIPPED_CAP"
    assert info["gamma_N"] is None
    assert info["expected_cases"] == 86400
    g, _ = sm.gamma_N(("xxxYYYY", "xyxYXY"), cap=10)
    assert g is None


# --------------------------------------------------------------------------------------
# tiers: determinism and coverage accounting
# --------------------------------------------------------------------------------------


def test_tier1_is_deterministic_and_accounts_for_every_case():
    a = sm.tier1(5)
    b = sm.tier1(5)
    assert a["bases_enumerated"] == b["bases_enumerated"] > 0
    assert a["distinct_spikes_attempted"] == b["distinct_spikes_attempted"] > 0
    assert a["delta_histogram"] == b["delta_histogram"]
    assert a["counterexamples"] == b["counterexamples"]
    for r in (a, b):
        assert r["spikes_measured"] + r["spikes_skipped_cap"] == \
            r["distinct_spikes_attempted"]
        assert r["coverage_ok"] is True
        assert r["odd_minimum_defects"] == 0
        assert r["cross_check_failures"] == []


def test_no_counterexample_below_total_length_seven():
    small = sm.tier1(6)
    assert small["counterexample_count"] == 0
    assert set(small["delta_histogram"]) <= {"0", "1"}


def test_recorded_counterexample_a_spike_can_lower_gamma_N():
    """("YYY","YXyXX") -> ("xXYYY","YXyXX") drops gamma_N from 2 to 1.

    The base is cyclically reduced, loopless, both relators have length >= 3, and the
    R1c-v2 solver decides it (NOT_SPHERICAL), so this is inside the solver's supported
    domain; only the spiked complex needs the census.
    """
    base = ("YYY", "YXyXX")
    spiked = ("xXYYY", "YXyXX")
    assert spiked == sm.apply_site(base, (0, 0, "x"))
    g_base, info_base = sm.gamma_N(base)
    g_spk, info_spk = sm.gamma_N(spiked)
    assert (g_base, g_spk) == (2, 1)
    assert info_base["minimum_defect"] == 4
    assert info_spk["minimum_defect"] == 2
    assert info_base["link_components"] == info_spk["link_components"] == 1
    prof = sm.presentation_profile(base)
    assert prof["cyclically_reduced"] is True
    assert prof["has_A_loop"] is False
    assert prof["min_relator_length"] >= 3
    assert sm._solver_verdict(base) == "NOT_SPHERICAL"
    assert sm._solver_verdict(spiked) == UNSUPPORTED
    assert sm.cross_check(base)["agree"] and sm.cross_check(spiked)["agree"]


def test_tier2_is_deterministic_and_accounts_for_every_case():
    bases, _ = sm.enumerate_bases(5)
    a = sm.tier2(bases, n_bases=6, max_pairs_per_base=25)
    b = sm.tier2(bases, n_bases=6, max_pairs_per_base=25)
    assert a["double_spikes_attempted"] == b["double_spikes_attempted"] > 0
    assert a["delta_histogram"] == b["delta_histogram"]
    assert a["counterexamples"] == b["counterexamples"]
    for r in (a, b):
        assert r["double_spikes_measured"] + r["double_spikes_skipped_cap"] == \
            r["double_spikes_attempted"]
        assert r["coverage_ok"] is True


def test_tier3_targets_and_coverage_accounting():
    got = sm.tier3(cap=100_000, members=0)
    names = [t["target"] for t in got["targets"]]
    assert names == ["AK3", "AK2"]
    ak3 = got["targets"][0]
    assert ak3["base_gamma_N"] == 2
    assert ak3["base_census_size"] == 86400
    for target in got["targets"]:
        assert target["spikes_measured"] + target["spikes_skipped_cap"] == \
            target["distinct_spikes_attempted"]
        assert target["coverage_ok"] is True
    # with a tiny cap every spike must be SKIPPED, never silently reported as monotone
    assert ak3["spikes_measured"] == 0
    assert ak3["spikes_skipped_cap"] == ak3["distinct_spikes_attempted"] > 0
    assert ak3["best_spiked_gamma_N"] is None


def test_smallest_census_members_are_sorted_and_exclude_ak3():
    if not os.path.exists(sm.AK3_MEMBERS):
        pytest.skip("ak3_matched_members.jsonl.gz not present")
    rows = sm.smallest_census_members(count=3, exclude=[sm.AK3])
    assert len(rows) == 3
    sizes = [r[0] for r in rows]
    assert sizes == sorted(sizes)
    ak3_key = sm.canon_exact_pair(sm.AK3)
    assert all(sm.canon_exact_pair(r[1]) != ak3_key for r in rows)


# --------------------------------------------------------------------------------------
# the committed result file
# --------------------------------------------------------------------------------------


def test_result_file_is_self_consistent():
    if not os.path.exists(sm.RESULT_PATH):
        pytest.skip("spike_monotonicity.json not generated yet")
    with open(sm.RESULT_PATH) as fh:
        report = json.load(fh)
    assert report["record"] == "spike_monotonicity"
    assert report["fixture"]["matches_recorded_fact"] is True
    t1 = report["tier1"]
    assert t1["spikes_measured"] + t1["spikes_skipped_cap"] == \
        t1["distinct_spikes_attempted"]
    assert t1["coverage_ok"] is True
    t2 = report["tier2"]
    assert t2["double_spikes_measured"] + t2["double_spikes_skipped_cap"] == \
        t2["double_spikes_attempted"]
    for target in report["tier3"]["targets"]:
        assert target["spikes_measured"] + target["spikes_skipped_cap"] == \
            target["distinct_spikes_attempted"]
    verdict = report["verdict"]
    assert (verdict["counterexamples"] > 0) == ("REFUTED" in verdict["line"])
