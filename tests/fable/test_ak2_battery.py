"""Tests for battery (b) of the R3' program: the AK(2) control artifacts.

Everything asserted here is either recomputed on the spot or read from the committed
artifacts ``results/stable_ac/fable/ak2_members.jsonl`` /
``ak2_trivialization_path.json`` / ``ak2_battery_summary.json`` produced by
``experiments/stable_ac/fable/ak2_battery.py``.  The battery contract under test:

(a) the recorded trivialization path replays byte-identically from AK(2) and arrives
    at the standard class (arrival convention "canon" -- the twelve h-moves contain no
    relator inversion/swap, so the byte-exact arrival is ``final_state`` with
    ``canon_pair(final_state) == canon_pair(('x','y')) == ('Y','X')``);
(b) the endpoint censuses are exact anchors: AK(2)'s recorded ``minimum_defect`` is
    positive and re-derivable bin by bin; the standard pair has ``minimum_defect == 0``
    with ``link_components == 2`` -- decisive SPHERICAL by Theorem D of
    ``R1E_DISCONNECTED_LINK.md`` (the 2L-term general defect), NOT an
    unsupported/degenerate case;
(c) the member harvest is deterministic: a fresh 50-pop prefix run reproduces exactly
    the committed rows with ``first_seen_pop <= 50``, in discovery order;
(d) member verdicts are re-derivable: three deterministically sampled rows re-decide
    to identical verdict + method through the same pinned stack;
(e) budgets were respected: the harvest performed EXACTLY 1,000 pops, the path search
    at most 1,000 pops (hard session rule);
(f) the replay check actually fires: a deliberately corrupted path state raises.
"""

from __future__ import annotations

import copy
import json
import os

import pytest

from experiments.stable_ac.fable import ac_words as W
from experiments.stable_ac.fable import ak2_battery as AB
from experiments.stable_ac.fable import neuwirth_rank_n as RN
from experiments.stable_ac.fable.disconnected_split import decide_pair

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MEMBERS_PATH = os.path.join(REPO_ROOT, "results", "stable_ac", "fable",
                            "ak2_members.jsonl")
PATH_PATH = os.path.join(REPO_ROOT, "results", "stable_ac", "fable",
                         "ak2_trivialization_path.json")
SUMMARY_PATH = os.path.join(REPO_ROOT, "results", "stable_ac", "fable",
                            "ak2_battery_summary.json")


@pytest.fixture(scope="module")
def member_rows():
    rows = []
    with open(MEMBERS_PATH, encoding="utf-8") as fh:
        for line in fh:
            rows.append(json.loads(line))
    assert rows, "ak2_members.jsonl is empty"
    return rows


@pytest.fixture(scope="module")
def path_doc():
    with open(PATH_PATH, encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def summary():
    with open(SUMMARY_PATH, encoding="utf-8") as fh:
        return json.load(fh)


# --------------------------------------------------------------------------------------
# (a) byte-exact replay to the standard class
# --------------------------------------------------------------------------------------


def test_path_replays_byte_identically_to_standard(path_doc):
    assert path_doc["search"]["goal_found"] is True
    assert AB.verify_path_document(path_doc) is True
    # the same facts, asserted directly rather than through the helper:
    root = tuple(path_doc["root"])
    assert root == AB.AK2
    replayed = W.replay(root, path_doc["moves"], path_doc["relator_cap"])
    assert [list(s) for s in replayed] == path_doc["states"][1:]
    final = tuple(path_doc["final_state"])
    assert tuple(replayed[-1]) == final
    # arrival convention "canon": length-1/length-1 pair in the standard class
    assert len(final[0]) == 1 and len(final[1]) == 1
    assert W.canon_pair(*final) == W.canon_pair("x", "y") == ("Y", "X")


def test_path_states_respect_the_relator_cap_and_length_profile(path_doc):
    cap = path_doc["relator_cap"]
    for state in path_doc["states"]:
        assert len(state[0]) <= cap and len(state[1]) <= cap
    assert path_doc["length_profile"] == [len(s[0]) + len(s[1])
                                          for s in path_doc["states"]]
    assert path_doc["length_profile"][0] == 11          # AK(2) is length 11
    assert path_doc["length_profile"][-1] == 2          # the standard tail


# --------------------------------------------------------------------------------------
# (b) endpoint censuses (Theorem D reading for the disconnected standard pair)
# --------------------------------------------------------------------------------------


def test_ak2_endpoint_census_is_exact_and_positive(path_doc):
    recorded = path_doc["endpoint_censuses"]["ak2"]
    census = RN.gamma_N_factorial_n(AB.AK2, ("x", "y"),
                                    cap_rotations=2_000_000, keep_accepting=False)
    assert census["status"] == "OK"
    assert recorded["minimum_defect"] == census["minimum_defect"]
    assert census["minimum_defect"] > 0                 # AK(2) exact: NOT thickenable
    assert recorded["defect_histogram"] == {
        str(k): v for k, v in sorted(census["defect_histogram"].items())}
    assert recorded["enumerated_cases"] == census["enumerated_cases"]


def test_standard_pair_census_is_zero_with_two_link_components(path_doc):
    # Theorem D (R1E_DISCONNECTED_LINK.md): with the general defect
    # |A| - |C| + 2L - |AC|, minimum_defect == 0 is decisive SPHERICAL even for a
    # disconnected link -- the standard pair ("x", "y") has L = 2.
    census = RN.gamma_N_factorial_n(("x", "y"), ("x", "y"),
                                    cap_rotations=2_000_000, keep_accepting=False)
    assert census["status"] == "OK"
    assert census["minimum_defect"] == 0
    assert census["link_components"] == 2
    recorded = path_doc["endpoint_censuses"]["standard_xy"]
    assert recorded["minimum_defect"] == 0
    assert recorded["link_components"] == 2
    # the recorded arrival state's own tail-track row agrees
    last = path_doc["tail_track"][-1]
    assert last["census"]["status"] == "OK"
    assert last["census"]["minimum_defect"] == 0
    assert last["census"]["link_components"] == 2


def test_first_zero_defect_index_is_recorded_and_re_derivable(path_doc):
    zeros = [t["index"] for t in path_doc["tail_track"]
             if t["census"]["status"] == "OK" and t["census"]["minimum_defect"] == 0]
    assert zeros == path_doc["zero_defect_indices"]
    assert path_doc["first_zero_defect_index"] == zeros[0]
    assert (path_doc["first_zero_defect_state"]
            == path_doc["states"][zeros[0]])
    # the recomputation of the first zero state's census (small by construction)
    state = tuple(path_doc["first_zero_defect_state"])
    census = RN.gamma_N_factorial_n(state, ("x", "y"),
                                    cap_rotations=2_000_000, keep_accepting=False)
    assert census["status"] == "OK" and census["minimum_defect"] == 0


def test_tail_track_covers_every_state_and_caps_are_honest(path_doc):
    track = path_doc["tail_track"]
    assert [t["index"] for t in track] == list(range(len(path_doc["states"])))
    for t in track:
        assert t["state"] == path_doc["states"][t["index"]]
        if t["census"]["status"] == "OK":
            assert t["census"]["minimum_defect"] is not None
            assert sum(t["census"]["defect_histogram"].values()) \
                == t["census"]["enumerated_cases"]
        else:                                            # over the 2M rotation cap
            assert t["census"]["status"] == "UNKNOWN_SIZE"
            assert t["census"]["expected_cases"] > t["census"]["cap_rotations"]
            assert t["census"]["minimum_defect"] is None


# --------------------------------------------------------------------------------------
# (c) harvest determinism: 50-pop prefix identity
# --------------------------------------------------------------------------------------


def test_harvest_prefix_is_deterministic(member_rows):
    prefix = AB.harvest_members(AB.AK2, pops=50, cap=AB.CAP)
    fresh = sorted(prefix["members"].items(), key=lambda kv: kv[1]["order"])
    committed = [row for row in member_rows if row["first_seen_pop"] <= 50]
    committed.sort(key=lambda row: row["order"])
    assert len(fresh) == len(committed)
    for (key, rec), row in zip(fresh, committed):
        assert list(key) == row["canonical"]
        assert rec["order"] == row["order"]
        assert rec["first_seen_pop"] == row["first_seen_pop"]
        assert list(rec["first_exact"]) == row["provenance"]["first_exact"]


def test_full_harvest_seen_set_matches_the_committed_rows(member_rows):
    # the full 1,000-pop harvest is cheap (no decisions); regenerate and compare
    harvest = AB.harvest_members(AB.AK2, pops=AB.HARVEST_POPS, cap=AB.CAP)
    assert harvest["pops"] == AB.HARVEST_POPS
    assert harvest["distinct_members"] == len(member_rows)
    fresh = sorted(harvest["members"].items(), key=lambda kv: kv[1]["order"])
    for (key, rec), row in zip(fresh, member_rows):
        assert list(key) == row["canonical"]
        assert rec["order"] == row["order"]
        assert rec["first_seen_pop"] == row["first_seen_pop"]
        assert rec["encounters"] == row["provenance"]["encounters"]


# --------------------------------------------------------------------------------------
# (d) verdict re-derivability on three deterministic samples
# --------------------------------------------------------------------------------------


def _cheap(row):
    """Rows whose re-decision is guaranteed fast (no multi-minute census rerun)."""
    census = row.get("census")
    if row["method"].startswith("r1c_v2"):
        return True
    return census is not None and census["expected_cases"] <= 200_000


def test_three_sampled_verdicts_re_derive(member_rows):
    eligible = [row for row in member_rows if _cheap(row)]
    assert len(eligible) >= 3
    spherical = [r for r in eligible if r["verdict"] == "SPHERICAL"]
    not_spherical = [r for r in eligible if r["verdict"] == "NOT_SPHERICAL"]
    sample = []
    if not_spherical:
        sample.append(not_spherical[0])
    if spherical:
        sample.append(spherical[0])
    sample.append(eligible[len(eligible) // 2])
    while len(sample) < 3:
        sample.append(eligible[-1])
    for row in sample[:4]:
        verdict, _support = decide_pair(tuple(row["canonical"]))
        assert verdict.verdict == row["verdict"], row["canonical"]
        assert verdict.method == row["method"], row["canonical"]


# --------------------------------------------------------------------------------------
# (e) budget assertions (hard session rule: <= 1,000 nodes per search)
# --------------------------------------------------------------------------------------


def test_budgets_were_respected(summary, path_doc, member_rows):
    assert summary["budgets"]["harvest_pops"] == 1_000          # EXACTLY
    assert summary["budgets"]["harvest_pop_budget"] == 1_000
    assert summary["budgets"]["path_search_pops"] <= 1_000
    assert path_doc["search"]["pops"] <= path_doc["search"]["pop_budget"] <= 1_000
    assert summary["harvest"]["distinct_members"] == len(member_rows)
    assert summary["budgets"]["scheme_budget"] == 200_000       # pinned round-2 budgets
    assert summary["budgets"]["branch_budget"] == 2_000_000
    assert summary["budgets"]["census_cap"] == 2_000_000
    # no verdict was produced beyond the census cap
    for row in member_rows:
        if row["verdict"] in ("SPHERICAL", "NOT_SPHERICAL") \
                and row["method"] == "factorial_census":
            assert row["census"]["expected_cases"] <= 2_000_000


def test_undecided_rows_are_named_never_folded(member_rows, summary):
    undecided = [r for r in member_rows if r["verdict"] == "UNDECIDED_BUDGET"]
    assert len(undecided) == summary["undecided_budget_rows"]
    for row in undecided:
        assert row["census"] is None or row["census"]["status"] != "OK" \
            or row["census"]["minimum_defect"] is None


# --------------------------------------------------------------------------------------
# (f) deliberate-mismatch negative control
# --------------------------------------------------------------------------------------


def test_corrupted_path_state_fails_the_replay_check(path_doc):
    doc = copy.deepcopy(path_doc)
    middle = len(doc["states"]) // 2
    r1 = doc["states"][middle][0]
    # flip the case of the first letter: still a well-formed word, no longer the state
    doc["states"][middle][0] = r1[0].swapcase() + r1[1:]
    with pytest.raises(AB.PathVerificationError):
        AB.verify_path_document(doc)


def test_corrupted_move_list_fails_the_replay_check(path_doc):
    doc = copy.deepcopy(path_doc)
    doc["moves"][len(doc["moves"]) // 2] = 1 + (doc["moves"][len(doc["moves"]) // 2] % 12)
    with pytest.raises(AB.PathVerificationError):
        AB.verify_path_document(doc)


# --------------------------------------------------------------------------------------
# slow extras (skip-marked; the artifacts already carry the full data)
# --------------------------------------------------------------------------------------


@pytest.mark.skip(reason="full tail-track recomputation enumerates ~1.6M rotation "
                         "systems (~minutes); the committed track was produced by the "
                         "same code and its endpoints are re-derived above")
def test_full_tail_track_recomputes_bin_by_bin(path_doc):
    states = [tuple(s) for s in path_doc["states"]]
    track = AB.tail_track(states)
    assert track == path_doc["tail_track"]


@pytest.mark.skip(reason="re-deciding all distinct members takes several minutes; "
                         "three rows are re-derived above and the run is deterministic")
def test_every_member_verdict_re_derives(member_rows):
    for row in member_rows:
        verdict, _support = decide_pair(tuple(row["canonical"]))
        assert verdict.verdict == row["verdict"]
