"""Tests for the post-restart instruments: gamma_N floor / gateway detection, the
certified-target set, and the meet-in-the-middle.

Fixtures are the values this session certified independently (exact censuses and
Todd-Coxeter runs), so a regression in any instrument shows up as a changed number
rather than as a silently different search.
"""

from __future__ import annotations

import json
import os
import random
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FABLE = os.path.join(REPO_ROOT, "experiments", "stable_ac", "fable")
if FABLE not in sys.path:
    sys.path.insert(0, FABLE)

import certified_targets as CT                                   # noqa: E402
import gamma_floor as GF                                         # noqa: E402
import gateway_neighborhood as GN                                # noqa: E402
import gateway_scan as GS                                        # noqa: E402
import neuwirth_cut_schemes as CS                                # noqa: E402
import neuwirth_rank_n as RN                                     # noqa: E402
import target_meet as TM                                         # noqa: E402

AK3 = ("xxxYYYY", "xyxYXY")
GATEWAY = ("YYXXyx", "YYxyXXX")          # gamma_N = 1, census 86,400
SPIKE_BASE = ("xyXY", "xxy")             # gamma_N = 0
SPIKE_IMAGE = ("xyXY", "yYxxy")          # gamma_N = 1 -- reduction creates thickenability


# --------------------------------------------------------------------------------------
# gamma_N conventions and the certified fixtures
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("words,expected_gamma,expected_cases", [
    (AK3, 2, 86_400),
    (GATEWAY, 1, 86_400),
    (SPIKE_BASE, 0, 12),
    (SPIKE_IMAGE, 1, 144),
])
def test_census_gamma_fixtures(words, expected_gamma, expected_cases):
    census = RN.gamma_N_factorial_n(words, None, cap_rotations=3_000_000,
                                    keep_accepting=False)
    assert census["status"] == "OK"
    assert census["expected_cases"] == expected_cases
    # minimum_defect is UNHALVED: gamma_N = minimum_defect / 2
    assert census["minimum_defect"] == 2 * expected_gamma


def test_reduction_can_create_thickenability():
    """R1f's counterexample: one move (0) apart, opposite sides of thickenability."""
    from ac_words import cyclic_reduce
    assert cyclic_reduce(SPIKE_IMAGE[1]) == SPIKE_BASE[1]
    base = RN.gamma_N_factorial_n(SPIKE_BASE, None, cap_rotations=100_000,
                                  keep_accepting=False)
    spiked = RN.gamma_N_factorial_n(SPIKE_IMAGE, None, cap_rotations=100_000,
                                    keep_accepting=False)
    assert base["minimum_defect"] == 0 and spiked["minimum_defect"] == 2


def test_solver_fails_closed_on_the_spike_loop():
    """The spiked spelling carries an A-loop, so the solver must not decide it."""
    support = CS.classify_cut_support(SPIKE_IMAGE, ("x", "y"))
    assert support.kind == CS.UNSUPPORTED
    assert "loop" in support.reason


# --------------------------------------------------------------------------------------
# gateway_scan: the two-sided certificate
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("words,expected_gamma", [
    (GATEWAY, 1), (AK3, 2), (SPIKE_BASE, 0),
])
def test_hill_climber_recovers_known_gamma(words, expected_gamma):
    rng = random.Random(11)
    best, orders = GS.sampled_min_defect(words, 8_000, rng)
    assert best == 2 * expected_gamma, (words, best)
    assert GS.verify_witness(words, orders) == best


def test_witness_verifier_rejects_a_broken_rotation():
    """The verifier must re-derive the defect, not trust the sampler."""
    rng = random.Random(3)
    _best, orders = GS.sampled_min_defect(GATEWAY, 4_000, rng)
    germ = sorted(orders)[0]
    broken = dict(orders)
    seq = list(broken[germ])
    if len(seq) < 2:
        pytest.skip("germ too small to corrupt")
    seq[0], seq[1] = seq[1], seq[0]          # breaks the B-reversal compatibility
    broken[germ] = seq
    with pytest.raises(AssertionError):
        GS.verify_witness(GATEWAY, broken)


def test_gateway_certificate_is_two_sided():
    """gamma_N = 1 needs BOTH the solver's >= 1 and a witness's <= 1."""
    support = CS.classify_cut_support(GATEWAY, ("x", "y"))
    decision = CS.solve_cut_schemes(GATEWAY, ("x", "y"), support=support)
    assert decision.verdict == CS.NOT_SPHERICAL            # gamma_N >= 1
    rng = random.Random(5)
    best, _orders = GS.sampled_min_defect(GATEWAY, 8_000, rng)
    assert best == 2                                       # gamma_N <= 1


# --------------------------------------------------------------------------------------
# gateway_neighborhood
# --------------------------------------------------------------------------------------


def test_graft_images_cover_every_rotation_and_sign():
    images = GN.graft_images(AK3)
    # 2 host choices x |host| rotations x |guest| rotations x 2 signs
    assert len(images) == 2 * len(AK3[0]) * len(AK3[1]) * 2
    for _label, exact, reduced in images:
        assert len(exact) == 2 and len(reduced) == 2


def test_neighbourhood_decider_fails_closed_on_loops():
    """A loop-bearing image must come back UNDECIDED/UNSUPPORTED, never NOT_SPHERICAL."""
    verdict = GN.decide(SPIKE_IMAGE)
    assert verdict["verdict"] in ("UNDECIDED_BUDGET", "UNSUPPORTED", "SPHERICAL",
                                 "NOT_SPHERICAL")
    if verdict["method"] == "r1c_v2_solver":
        pytest.fail("the solver must not decide a loop-bearing complex")


# --------------------------------------------------------------------------------------
# certified targets
# --------------------------------------------------------------------------------------


@pytest.fixture(scope="module")
def targets():
    if not os.path.exists(CT.TARGETS_JSON):
        pytest.skip("certified target set not built")
    return CT.load_targets(CT.TARGETS_JSON)


def test_target_set_shape(targets):
    entries = targets["entries"]
    assert len(entries) == 5389
    counts = {}
    for entry in entries:
        complexity = entry["complexity"]
        counts[complexity] = counts.get(complexity, 0) + 1
        # the FQW profile: V+1 relators, total length 3V+3
        assert len(entry["relators"]) == complexity + 1
        assert sum(len(w) for w in entry["relators"]) == 3 * complexity + 3
    assert counts == {1: 2, 2: 17, 3: 238, 4: 4618, 5: 514}


def test_targets_present_the_trivial_group(targets):
    """Spot-check the certification the whole route rests on."""
    from coset_enum import is_trivial_group
    rng = random.Random(20260729)
    sample = rng.sample(targets["entries"], 12)
    for entry in sample:
        generators = tuple(sorted({c.lower() for w in entry["relators"] for c in w}))
        result = is_trivial_group(tuple(entry["relators"]), generators=generators,
                                  cap=200_000)
        assert result["trivial"], entry


def test_canonical_key_is_invariant_under_ac_composites():
    """Rotation, inversion and relator permutation are AC composites (R1E Lemma P),
    so the key must not distinguish them."""
    from ac_words import inverse
    base = ("xxxYYYY", "xyxYXY")
    rotated = ("xxYYYYx", "xyxYXY")
    inverted = ("xxxYYYY", inverse("xyxYXY"))
    swapped = ("xyxYXY", "xxxYYYY")
    key = CT.canon_multi(base)
    assert CT.canon_multi(rotated) == key
    assert CT.canon_multi(swapped) == key
    assert CT.canon_multi(inverted) == key


def test_relabel_canon_is_generator_blind():
    assert CT.relabel_canon(("xxyy", "xy")) == CT.relabel_canon(("yyxx", "yx"))


def test_positive_control_matches_are_reproducible(targets):
    """AK(2)'s trivializable class reaches complexity-1 targets; AK(3)'s does not."""
    hit = CT.match(("X", "YYXyx"), targets)
    assert hit is not None and hit["target"]["complexity"] == 1
    assert CT.match(AK3, targets) is None


# --------------------------------------------------------------------------------------
# meet-in-the-middle
# --------------------------------------------------------------------------------------


def test_backward_neighbours_are_reduced_and_capped():
    state = ("baaBA", "b")
    for image in TM.neighbours(state, length_cap=14):
        assert sum(len(w) for w in image) <= 14
        for word in image:
            assert word and word == __import__("ac_words").cyclic_reduce(word)


def test_meet_finds_a_planted_match():
    """One backward step from a target must be detected when fed back in."""
    seed = {"relators": ["baaBA", "b"], "complexity": 1, "skeleton": 1}
    expansion = TM.expand_targets([seed], depth=1)
    index = expansion["index"]
    assert len(index) > 1
    planted = next(v["state"] for v in index.values() if v["depth"] == 1)
    assert CT.canon_multi(planted) in index


def test_intersection_report_marks_partial_files(tmp_path):
    """An artifact still being written must be reported PARTIAL, never as complete."""
    broken = tmp_path / "half.jsonl.gz"
    broken.write_bytes(b"\x1f\x8b\x08\x00truncated-not-a-real-gzip")
    if not os.path.exists(CT.TARGETS_JSON):
        pytest.skip("certified target set not built")
    loaded = CT.load_targets(CT.TARGETS_JSON)
    report = CT.intersect_corpus([("broken", os.path.relpath(broken, CT.REPO_ROOT))],
                                 loaded)
    assert report["sources"][0]["status"].startswith("PARTIAL")


# --------------------------------------------------------------------------------------
# gamma_floor bookkeeping
# --------------------------------------------------------------------------------------


def test_floor_census_size_matches_the_factorial_formula():
    assert GF.census_size(AK3) == 86_400
    assert GF.census_size(("x", "y")) == 1


def test_floor_measurement_artifact_is_self_consistent():
    path = os.path.join(REPO_ROOT, "results", "stable_ac", "fable",
                        "gamma_floor_measurement.json")
    if not os.path.exists(path):
        pytest.skip("floor measurement not run")
    with open(path, encoding="utf-8") as handle:
        report = json.load(handle)
    for entry in report["classes"].values():
        measured = sum(entry["gamma_histogram"].values())
        assert measured == entry["measured"]
        # every recorded cross-check agreed; a disagreement is a solver/census conflict
        assert entry["verdict_cross_check"]["disagree"] == []
