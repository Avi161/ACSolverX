"""Tests for the R1e disconnected-split pipeline (``disconnected_split.py``).

Implements items (a)-(f) of the implementation contract in
``results/stable_ac/theory/fable/R1E_DISCONNECTED_LINK.md``:

(a) the standard complex ("x", "y", "z") as the degenerate positive control, plus the
    ILLEGAL-NEGATIVE regression pinning that the 2L term of the general defect is
    load-bearing (the naive connected formula gives exactly -4 there);
(b) the AK3+z root: joint rank-3 census == rank-2 census (minimum defect 4, i.e.
    gamma_N = 2 in the UNHALVED convention), verdict NOT_SPHERICAL, full histogram
    equality (Corollary Z);
(c) the histogram identity on the second census-affordable bucket state (967,680
    rotations) and on synthetic small stabilizations;
(d) a NON-degenerate disconnected positive, found by brute force over tiny rank-2
    pairs, deciding SPHERICAL through the split pipeline AND the joint census;
(e) straddle detection fail-closed (Lemma S exclusion);
(f) clean-shape verification on all 382 bucket rows, the 10 corpus-overlap pairs
    asserted against their stored verdicts, and codex's length-14 stable-class pair
    decided as an extra row (recorded, NOT asserted -- see the comment there).

Every number asserted here is recomputed or pinned as a literal; nothing depends on a
scratch directory.  Census work stays at the stated caps so the file runs in well
under five minutes.
"""

from __future__ import annotations

import json
import os

import pytest

from experiments.stable_ac.fable import disconnected_split as DS
from experiments.stable_ac.fable import neuwirth_cut_schemes as CS
from experiments.stable_ac.fable import neuwirth_rank_n as RN

from helpers_fable import cyclically_reduced_words  # noqa: E402  (tests/fable on sys.path)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HARVEST_PATH = os.path.join(REPO_ROOT, "results", "stable_ac", "fable",
                            "rank3_harvest_round2.jsonl")
TARGETS_PATH = os.path.join(REPO_ROOT, "results", "stable_ac", "fable",
                            "gamma_n_targets.jsonl")
OUTPUT_PATH = os.path.join(REPO_ROOT, "results", "stable_ac", "fable",
                           "disconnected_split_verdicts.jsonl")

RANK3 = ("x", "y", "z")
STANDARD = ("x", "y", "z")                     # the standard presentation of 1
AK3Z = ("Z", "YXYxyx", "YYYYxxx")              # the AK3+z harvest root (canonical)
SECOND_AFFORDABLE = ("Z", "YXYxx", "YYYYxyyyX")  # the only other bucket state with
#                                                  joint census size <= 2M (967,680)


@pytest.fixture(scope="module")
def bucket():
    return DS.load_bucket(HARVEST_PATH)


@pytest.fixture(scope="module")
def corpus():
    return DS.load_corpus_verdicts(TARGETS_PATH)


# --------------------------------------------------------------------------------------
# (a) the standard complex and the illegal-negative regression
# --------------------------------------------------------------------------------------


def test_standard_triple_structural_and_census_positive_control():
    report = DS.structural_report(STANDARD)
    assert report.link_components == 3          # own union-find, not build_link_n
    assert report.straddling == ()
    assert not report.clean                     # 3 components: not the bucket shape
    verdict = DS.census_verdict(STANDARD, RANK3)
    assert verdict.verdict == CS.SPHERICAL
    census = verdict.census
    assert census["status"] == "OK"
    assert census["expected_cases"] == 1        # all germ degrees are 1
    assert census["minimum_defect"] == 0        # UNHALVED defect convention pinned
    assert census["link_components"] == 3
    # and the independent component count agrees with the census oracle
    assert RN.build_link_n(STANDARD, RANK3).link_components == 3


def test_illegal_negative_regression_2l_term_is_load_bearing():
    census = DS.census_verdict(STANDARD, RANK3).census
    rotation = census["accepting_orders"][0]
    check = DS.check_witness_l_general(STANDARD, rotation, RANK3)
    # the naive CONNECTED formula |A| - |C| + 2 - |AC| is ILLEGAL at L = 3:
    assert check["naive_connected_defect"] == -4
    # the general formula |A| - |C| + 2L - |AC| of Theorem D gives exactly 0:
    assert check["defect"] == 0
    assert check["link_components"] == 3
    assert [c["defect"] for c in check["per_component"]] == [0, 0, 0]
    # transitivity audit is rescoped to L == 1, so it must NOT have been applied
    assert check["ac_bc_transitive"] is None


# --------------------------------------------------------------------------------------
# (b) the AK3+z root: joint == pair, minimum defect 4, NOT_SPHERICAL
# --------------------------------------------------------------------------------------


def test_ak3_plus_z_root_decides_not_spherical_with_full_histogram_identity():
    assert DS.project_pair(AK3Z) == ("YXYxyx", "YYYYxxx")
    row = DS.decide_split_state(AK3Z)
    assert row["structural"]["clean"]
    assert row["verdict"] == CS.NOT_SPHERICAL
    assert row["hit"] is False
    cc = row["cross_check"]
    assert cc["ran"]
    assert cc["joint_census_size"] == 86_400
    assert cc["pair_census_size"] == 86_400     # computed, not assumed
    assert cc["histograms_equal"]               # Corollary Z, bin by bin
    # minimum defect 4 (unhalved) on BOTH sides = gamma_N = 2, matching the
    # codex-certified gamma_N(AK(3)) = 2
    assert cc["joint_minimum_defect"] == 4
    assert cc["pair_minimum_defect"] == 4
    assert cc["joint_link_components"] == 2
    assert cc["pair_link_components"] == 1


def test_cross_check_raises_on_a_histogram_mismatch():
    # negative control: the Corollary-Z assert must actually fire on a wrong pair
    with pytest.raises(DS.SplitAuditError):
        DS.joint_cross_check(AK3Z, ("YX", "Yx"))


# --------------------------------------------------------------------------------------
# (c) the histogram identity on the second affordable state and on synthetics
# --------------------------------------------------------------------------------------


def test_histogram_identity_on_second_affordable_bucket_state(bucket):
    # the state is FOUND in the data, not trusted from this file's constant
    matches = [s for s in bucket if tuple(s["canonical"]) == SECOND_AFFORDABLE]
    assert len(matches) == 1
    pair = DS.project_pair(SECOND_AFFORDABLE)
    cc = DS.joint_cross_check(SECOND_AFFORDABLE, pair)
    assert cc["ran"]
    assert cc["joint_census_size"] == 967_680
    assert cc["pair_census_size"] == 967_680
    assert cc["histograms_equal"]
    assert cc["joint_link_components"] == 2
    assert cc["pair_minimum_defect"] == cc["joint_minimum_defect"] == 2


@pytest.mark.parametrize("triple", [
    ("xyXY", "yxYX", "z"),
    ("xxy", "xyy", "Z"),                        # inverse z-relator (AC1 variant)
    ("xy", "xY", "z"),
])
def test_histogram_identity_on_synthetic_stabilizations(triple):
    # the raw (uncanonicalised) pair isolates Corollary Z from the symmetry lemma
    pair = tuple(w for w in triple if w not in ("z", "Z"))
    cc = DS.joint_cross_check(triple, pair)
    assert cc["ran"]
    assert cc["sizes_equal"]                    # z contributes the factor (1-1)! = 1
    assert cc["histograms_equal"]
    assert cc["joint_link_components"] == cc["pair_link_components"] + 1


# --------------------------------------------------------------------------------------
# (d) a NON-degenerate disconnected positive through the whole pipeline
# --------------------------------------------------------------------------------------


def _first_nontrivial_spherical_pair():
    """Brute-force the census over tiny rank-2 pairs (deterministic product order)."""
    for l1 in range(2, 4):
        for l2 in range(l1, 4):
            for u in cyclically_reduced_words(l1):
                for v in cyclically_reduced_words(l2):
                    joined = (u + v).lower()
                    if joined.count("x") < 2 or joined.count("y") < 2:
                        continue                # both generators must have degree >= 2
                    if DS.structural_report((u, v), ("x", "y")).link_components != 1:
                        continue                # the triple must have EXACTLY 2
                    census = RN.gamma_N_factorial_n((u, v), ("x", "y"),
                                                    cap_rotations=2_000,
                                                    keep_accepting=False)
                    if census["status"] != "OK":
                        continue
                    if census["minimum_defect"] == 0:
                        return u, v
    return None


def test_nondegenerate_disconnected_positive_decides_spherical():
    found = _first_nontrivial_spherical_pair()
    assert found is not None
    u0, v0 = found
    triple = (u0, v0, "z")
    report = DS.structural_report(triple)
    assert report.clean
    assert report.link_components == 2
    assert report.straddling == ()

    row = DS.decide_split_state(triple)
    assert row["verdict"] == CS.SPHERICAL       # through the split pipeline
    assert row["hit"] is True
    assert DS.HIT_BANNER in row["HIT_REPLAY_PROTOCOL_REQUIRED"]
    cc = row["cross_check"]
    assert cc["ran"] and cc["histograms_equal"]
    assert cc["joint_minimum_defect"] == 0
    assert cc["joint_link_components"] == 2

    # ... AND through the joint census directly
    joint = DS.census_verdict(triple, RANK3)
    assert joint.verdict == CS.SPHERICAL
    assert joint.census["link_components"] == 2

    # the L-general witness checker verified the pair (L = 1) and the triple (L = 2)
    pair_check = row["pair_witness_check"]
    assert pair_check["link_components"] == 1
    assert pair_check["defect"] == 0
    joint_check = row["joint_witness_check"]
    assert joint_check["link_components"] == 2
    assert joint_check["defect"] == 0
    assert all(c["defect"] == 0 for c in joint_check["per_component"])
    # the hit protocol ran Todd-Coxeter on the pair (index recorded either way)
    assert row["todd_coxeter"]["status"] in ("COMPLETE", "CAP_EXCEEDED")


# --------------------------------------------------------------------------------------
# (e) straddle detection (fail-closed exclusion from Lemma S)
# --------------------------------------------------------------------------------------


def test_straddle_detection_excludes_states_from_the_split():
    # the R1E note's own example: relator "xy" makes BOTH generators straddle
    report = DS.structural_report(("xy", "z"))
    assert set(report.straddling) == {"x", "y"}
    assert not report.clean

    # a 3-relator state with the 2-letter relator shape is VERIFY_FAIL, never split
    report2 = DS.structural_report(("xy", "xy", "z"))
    assert set(report2.straddling) == {"x", "y"}
    assert report2.link_components == 3
    row = DS.decide_split_state(("xy", "xy", "z"))
    assert row["verdict"] == DS.VERIFY_FAIL
    assert row["method"] == "structural_verification"
    assert "pair" not in row                    # the projection never happened

    # the known fixture shape ("ZY", "xzXZxYY") is VERIFY_FAIL as well -- measured
    # here, its link is CONNECTED (1 component, so nothing straddles) and z occurs 3
    # times: the gate catches it on component count, z-count and the missing
    # z-relator rather than on straddle
    report3 = DS.structural_report(("ZY", "xzXZxYY"))
    assert not report3.clean
    assert report3.link_components == 1
    assert report3.straddling == ()
    assert report3.z_occurrences == 3
    row3 = DS.decide_split_state(("ZY", "xzXZxYY"))
    assert row3["verdict"] == DS.VERIFY_FAIL


# --------------------------------------------------------------------------------------
# (f) the 382-row bucket, the corpus overlap and the codex length-14 pair
# --------------------------------------------------------------------------------------


def test_all_382_bucket_rows_pass_clean_shape(bucket):
    assert len(bucket) == 382
    for state in bucket:
        words = tuple(state["canonical"])
        report = DS.verify_bucket_shape(words)
        assert report.clean, (words, report.reasons)
        assert report.link_components == 2
        assert report.straddling == ()
        assert report.z_occurrences == 1
        assert report.z_relator_indices and words[report.z_relator_indices[0]] == "Z"
        # the independent union-find agrees with build_link_n (the harvest's gate)
        assert RN.build_link_n(words, RANK3).link_components == 2


def test_bucket_projects_onto_382_distinct_pairs(bucket):
    pairs = {DS.project_pair(tuple(s["canonical"])) for s in bucket}
    assert len(pairs) == 382                    # measured: states map 1:1 onto pairs


def test_corpus_overlap_pairs_agree_with_stored_verdicts(bucket, corpus):
    pairs = sorted({DS.project_pair(tuple(s["canonical"])) for s in bucket})
    overlap = [p for p in pairs if p in corpus]
    assert len(overlap) == 10
    for pair in overlap:
        verdict, _support = DS.decide_pair(pair)
        assert verdict.verdict == corpus[pair], (pair, verdict.verdict, corpus[pair])


def test_codex_length14_pair_is_decided_and_recorded():
    # AK3_RANK3_COMPRESSION.md (codex, 2026-07-24) certifies ("YXXYx", "YYYYXyyyx")
    # as a rank-2 stable-class member of AK(3) with Aut-floor 14, but states NO
    # per-pair Neuwirth/gamma_N verdict, so per the task correction this row is
    # DECIDED AND RECORDED without asserting agreement against that note.  The only
    # assertions are pipeline properties: the pair decides inside the pinned budgets
    # (no UNDECIDED_BUDGET / UNSUPPORTED bucket).
    verdict, support = DS.decide_pair(DS.CODEX_LENGTH14_PAIR)
    assert verdict.verdict in (CS.SPHERICAL, CS.NOT_SPHERICAL)
    assert support.kind in (CS.IN_SCOPE, CS.NONPLANAR)


def test_emitted_verdicts_file_is_consistent_when_present(corpus):
    if not os.path.exists(OUTPUT_PATH):
        pytest.skip("disconnected_split_verdicts.jsonl not generated yet")
    rows = []
    with open(OUTPUT_PATH, encoding="utf-8") as fh:
        for line in fh:
            rows.append(json.loads(line))
    assert len(rows) == 382
    allowed = {CS.SPHERICAL, CS.NOT_SPHERICAL, DS.UNDECIDED_BUDGET, DS.VERIFY_FAIL}
    for row in rows:
        assert row["verdict"] in allowed
        # NOTE: histogram keys in the file are JSON strings; every histogram
        # COMPARISON happened in memory before serialisation (module docstring), so
        # this test only checks the recorded outcome flags, never re-compares dicts.
        for check in row.get("cross_check", ()):
            if check.get("ran"):
                assert check["histograms_equal"] is True
        if row["corpus_overlap"]:
            assert row["corpus_agrees"] is True
