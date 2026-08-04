"""Tests for ``experiments/stable_ac/fable/split_bracket.py`` (task A13).

The property under test is not "the number is small" but **the bound direction**: a
certified split may only ever bound ``gamma_N`` of the base from ABOVE, and the code must
refuse (loudly) any situation in which that reading would be inverted or unsound.
"""

from __future__ import annotations

import math
import os
import random
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments.stable_ac.fable import gateway_scan as GS
from experiments.stable_ac.fable import high_rank_refine as HR
from experiments.stable_ac.fable import neuwirth_rank_n as RN
from experiments.stable_ac.fable import split_bracket as SB

AK3 = ("YXYxyx", "YYYYxxx")            # exact minimum_defect 4 (gamma_N = 2), S3 pin
ACA117 = ("YYYXyyx", "YXXXyxx")        # exact minimum_defect 2 (gamma_N = 1), S9
SHORT = ("YYXXyx", "YYxyXXX")          # a length-13 AK(2) gateway used as a small fixture


# ---------------------------------------------------------------------------------
# shapes
# ---------------------------------------------------------------------------------


def test_split_shapes_never_leaves_a_degree_one_generator():
    """GAP-S8-2: a shape with ``a0 + k < 2`` would make the split degenerate."""
    for d in range(3, 12):
        for k, a0, sizes, _factor in SB.split_shapes(d, 5):
            assert a0 + k >= 2
            assert all(s >= 1 for s in sizes)
            assert a0 + sum(sizes) == d


def test_split_shape_factor_is_the_realised_census_factor():
    """The predicted ``(a0+k-1)! * prod sizes!`` must equal the true census shrinkage."""
    pair = ACA117
    rng = random.Random(1)
    base = SB.census_of(pair)
    other = math.factorial(SB.degrees_of(pair)["y"] - 1)
    for k, a0, sizes, factor in SB.split_shapes(SB.degrees_of(pair)["x"], 3)[:6]:
        pattern = SB.bucket_pattern(SB.degrees_of(pair)["x"], a0, sizes, rng, "block")
        ref = HR.split_generator(pair, ("x", "y"), gen="x", buckets=pattern)
        assert SB.census_of(ref.words, ref.generators) == factor * other
    assert base == math.factorial(6) * math.factorial(6)


def test_bucket_pattern_styles_share_a_label_multiset():
    rng = random.Random(2)
    sizes = (3, 2)
    got = {}
    for style in ("block", "roundrobin", "random"):
        pattern = SB.bucket_pattern(7, 2, sizes, rng, style)
        assert sorted(pattern) == [0, 0, 1, 1, 1, 2, 2]
        got[style] = pattern
    assert got["block"] == (0, 0, 1, 1, 1, 2, 2)
    assert got["block"] != got["roundrobin"]


def test_bucket_pattern_offset_rotates():
    rng = random.Random(3)
    a = SB.bucket_pattern(7, 2, (3, 2), rng, "block", offset=0)
    b = SB.bucket_pattern(7, 2, (3, 2), rng, "block", offset=3)
    assert sorted(a) == sorted(b)
    assert b == a[3:] + a[:3]


def test_bucket_pattern_rejects_a_shape_of_the_wrong_size():
    with pytest.raises(ValueError):
        SB.bucket_pattern(7, 2, (2, 2), random.Random(0), "block")


# ---------------------------------------------------------------------------------
# plans, and the REPLAY certificate
# ---------------------------------------------------------------------------------


def test_plan_family_is_deterministic_and_fits_the_cap():
    a = SB.plan_family(ACA117, ("x", "y"), census_cap=200_000, n_plans=5)
    b = SB.plan_family(ACA117, ("x", "y"), census_cap=200_000, n_plans=5)
    assert [p.as_row() for p in a] == [p.as_row() for p in b]
    assert a
    for plan in a:
        words, generators = SB.apply_plan(ACA117, ("x", "y"), plan)
        assert SB.census_of(words, generators) <= 200_000


def test_certify_plan_replays_the_split_back_to_the_base():
    plan = SB.plan_family(ACA117, ("x", "y"), census_cap=200_000, n_plans=1)[0]
    built = SB.certify_plan(ACA117, ("x", "y"), plan)
    assert built["rank"] > 2
    assert len(built["words"]) == built["rank"]                 # balanced
    assert set(built["certificate"]["relations"]) <= {
        "identical", "rotation", "inversion", "rotation+inversion"}


def test_a_tampered_split_fails_certification():
    """Corrupting one letter of a residual relator must be caught by the replay."""
    plan = SB.plan_family(ACA117, ("x", "y"), census_cap=200_000, n_plans=1)[0]
    words, generators = SB.apply_plan(ACA117, ("x", "y"), plan)
    bad = list(words)
    victim = max(range(len(bad)), key=lambda i: len(bad[i]))
    bad[victim] = bad[victim][:-1] + ("y" if bad[victim][-1] != "y" else "x")
    with pytest.raises((HR.CertificationError, SB.SplitContradiction)):
        HR.certify_refinement(HR.Presentation(ACA117, ("x", "y")),
                              HR.Presentation(tuple(bad), generators))


def test_single_step_plans_carry_the_link_minor_certificate():
    """S8's structural claim, checked instance by instance."""
    plans = [p for p in SB.plan_family(ACA117, ("x", "y"), census_cap=200_000,
                                       n_plans=8) if len(p.steps) == 1]
    assert plans, "expected at least one single-generator plan"
    built = SB.certify_plan(ACA117, ("x", "y"), plans[0])
    minor = built["minor_certificate"]
    assert minor is not None and minor["is_contraction"] is True
    assert minor["contracted_edges"] == minor["expected_contracted_edges"]


# ---------------------------------------------------------------------------------
# the independent defect recomputation
# ---------------------------------------------------------------------------------


def test_independent_defect_agrees_with_gateway_scan_on_a_known_state():
    rng = random.Random(5)
    defect, orders = GS.sampled_min_defect(SHORT, 4_000, rng)
    assert orders is not None
    rot = {int(k): v for k, v in orders.items()}
    assert GS.verify_witness(SHORT, rot) == defect
    assert SB.independent_defect(SHORT, rot)["defect"] == defect


def test_independent_defect_agrees_with_the_exact_census_minimum():
    """On AK(3) the census minimum is the pinned 4; a witness at 4 must recompute to 4."""
    census = RN.gamma_N_factorial_n(AK3, ("x", "y"), cap_rotations=200_000,
                                    keep_accepting=False)
    assert census["minimum_defect"] == 4
    rng = random.Random(7)
    defect, orders = GS.sampled_min_defect(AK3, 6_000, rng)
    assert defect >= census["minimum_defect"]
    rot = {int(k): v for k, v in orders.items()}
    assert SB.independent_defect(AK3, rot)["defect"] == defect


def test_independent_defect_rejects_a_broken_rotation():
    rng = random.Random(9)
    _defect, orders = GS.sampled_min_defect(SHORT, 2_000, rng)
    rot = {int(k): list(v) for k, v in orders.items()}
    victim = next(k for k, v in rot.items() if len(v) >= 2)
    rot[victim][0], rot[victim][1] = rot[victim][1], rot[victim][0]
    with pytest.raises(SB.SplitContradiction):
        SB.independent_defect(SHORT, rot)


def test_independent_defect_rebuilds_the_link_component_count():
    rng = random.Random(11)
    _defect, orders = GS.sampled_min_defect(AK3, 2_000, rng)
    rot = {int(k): v for k, v in orders.items()}
    data = RN.build_link_n(AK3, ("x", "y"))
    assert SB.independent_defect(AK3, rot)["link_components"] == data.link_components


# ---------------------------------------------------------------------------------
# scoring, and the bound direction
# ---------------------------------------------------------------------------------


def test_evaluate_split_exact_path_matches_a_direct_census():
    plan = SB.plan_family(ACA117, ("x", "y"), census_cap=60_000, n_plans=1)[0]
    words, generators = SB.apply_plan(ACA117, ("x", "y"), plan)
    score = SB.evaluate_split(words, generators, census_cap=200_000, want_witness=False)
    direct = RN.gamma_N_factorial_n(words, generators, cap_rotations=200_000,
                                    keep_accepting=False)
    assert score["method"] == "exact_census"
    assert score["exhaustive_on_split"] is True
    assert score["min_defect"] == direct["minimum_defect"]


def test_every_certified_split_of_a_known_state_lands_at_or_above_it():
    """The S8 direction, measured: a split never scores BELOW its base's exact value."""
    for pair, exact_defect in ((ACA117, 2), (AK3, 4)):
        for plan in SB.plan_family(pair, ("x", "y"), census_cap=60_000, n_plans=4):
            words, generators = SB.apply_plan(pair, ("x", "y"), plan)
            SB.certify_plan(pair, ("x", "y"), plan)
            score = SB.evaluate_split(words, generators, census_cap=200_000,
                                      want_witness=False)
            assert score["min_defect"] >= exact_defect, (
                f"split {words} of {pair} scored {score['min_defect']} < {exact_defect}: "
                "Conjecture S8 would be refuted")


def test_bracket_row_reports_an_upper_bound_never_a_lower_one():
    row = SB.bracket_row(ACA117, lower_bound=1, census_cap=60_000, n_plans=4,
                         time_cap=30.0)
    assert row["split_gamma_N_upper"] is not None
    assert row["split_gamma_N_upper"] >= row["gamma_N_lower"]
    assert "UPPER" in row["bound_direction"]
    assert "Conjecture S8" in row["conditional_on"]
    # nothing in the row claims a lower bound derived from a split
    assert row["gamma_N_lower"] == 1


def test_bracket_row_raises_when_a_split_undercuts_a_known_exact_value():
    """The guard that makes this instrument safe: a violation is raised, never scored."""
    with pytest.raises(SB.MonotonicityViolation):
        SB.bracket_row(ACA117, lower_bound=None, census_cap=60_000, n_plans=3,
                       time_cap=30.0, known_gamma=99)


def test_bracket_row_raises_when_a_split_undercuts_a_certified_lower_bound():
    with pytest.raises(SB.SplitContradiction):
        SB.bracket_row(ACA117, lower_bound=99, census_cap=60_000, n_plans=3,
                       time_cap=30.0)


def test_bracket_row_uses_the_base_census_when_it_fits_and_calls_it_exact():
    row = SB.bracket_row(AK3, lower_bound=None, census_cap=200_000, n_plans=2,
                         time_cap=30.0)
    assert row["base_exact_gamma_N"] == 2                      # AK(3), pinned
    assert row["split_gamma_N_upper"] == 2


def test_bracket_row_closes_the_bracket_on_a_certified_gateway():
    row = SB.bracket_row(ACA117, lower_bound=1, census_cap=200_000, n_plans=8,
                         time_cap=45.0)
    assert row["split_gamma_N_upper"] == 1
    assert row["bracket_closed"] is True
    assert row["base_exact_gamma_N"] in (None, 1)


# ---------------------------------------------------------------------------------
# summary plumbing
# ---------------------------------------------------------------------------------


def test_summarise_merges_upper_bounds_by_taking_the_minimum():
    sweep = [
        {"name": "r1", "pair": ["YXXXyxx", "AAA"], "total_length": 10,
         "gamma_N_lower": 1, "gamma_N_upper": 3},
        {"name": "r2", "pair": ["ABC", "DEF"], "total_length": 6,
         "gamma_N_lower": 1, "gamma_N_upper": 2},
    ]
    rows = [{"name": "r1", "pair": ["YXXXyxx", "AAA"], "total_length": 10,
             "split_gamma_N_upper": 1, "a9_gamma_N_upper": 3, "bracket_closed": True,
             "n_fresh_used": 2, "best_method": "exact_census",
             "best_split_words": ["x"], "split_min_defect": 2}]
    doc = SB.summarise(rows, sweep, 0.0, 1000, 4, 2, 100, 1, "open")
    merged = {r["name"]: r for r in doc["merged_ranking"]}
    assert merged["r1"]["gamma_N_upper"] == 1
    assert merged["r1"]["upper_source"] == "split"
    assert merged["r2"]["gamma_N_upper"] == 2
    assert doc["brackets_closed"] == 1
    assert doc["new_gamma_N_1_gateways"] == 1
    enr = doc["baumslag_solitar_enrichment"]
    assert enr["rows_with_relator"] == 1
    assert enr["certified_gamma_1_with_relator"] == 1
    assert "no_p_value" in enr


def test_summarise_never_lowers_a_bound_it_did_not_measure():
    sweep = [{"name": "r1", "pair": ["AB", "CD"], "total_length": 4,
              "gamma_N_lower": 1, "gamma_N_upper": 2}]
    rows = [{"name": "r1", "pair": ["AB", "CD"], "total_length": 4,
             "split_gamma_N_upper": 4, "a9_gamma_N_upper": 2, "bracket_closed": False,
             "n_fresh_used": 3, "best_method": "sampled", "best_split_words": ["x"],
             "split_min_defect": 8}]
    doc = SB.summarise(rows, sweep, 0.0, 1000, 4, 2, 100, 1, "open")
    merged = doc["merged_ranking"][0]
    assert merged["gamma_N_upper"] == 2                # the worse split bound is ignored
    assert merged["upper_source"] == "A9 sampler"
    assert doc["rows_improved_over_A9"] == 0


def test_calibration_ladder_rungs_all_carry_an_exact_gamma():
    ladder = SB.calibration_ladder(per_length_cap=1, extra_cap=2)
    assert ladder
    for rung in ladder:
        assert isinstance(rung["known_gamma_N"], int)
        assert rung["known_gamma_N"] >= 0
        assert rung["source"]
    assert any(r["known_gamma_N"] == 0 for r in ladder)
    assert any(r["known_gamma_N"] >= 1 for r in ladder)


def test_module_documents_the_bound_direction_and_the_conjecture():
    doc = SB.__doc__
    assert "UPPER" in doc
    assert "Conjecture S8" in doc
    assert "says NOTHING" in doc
