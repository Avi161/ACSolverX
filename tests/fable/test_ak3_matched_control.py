"""Tests for the matched-operator AK(3) control (ak3_matched_control.py).

Everything asserted here is either recomputed on the spot or read from the committed
artifacts ``results/stable_ac/fable/ak3_matched_members.jsonl`` /
``ak3_matched_summary.json``.  The control's contract under test:

(a) the harvest operator is BYTE-IDENTICAL to the AK(2) battery's: a fresh 50-pop
    prefix run of ``ak2_battery.harvest_members`` on the AK(3) root reproduces the
    provenance harvest's member stream exactly (keys, orders, first_seen_pop, first
    exact realizations, encounter counts);
(b) the harvest is deterministic: the same 50-pop prefix reproduces exactly the
    committed rows with ``first_seen_pop <= 50``, in discovery order, including the
    replay provenance fields;
(c) budgets were respected: the harvest performed EXACTLY 1,000 pops (hard session
    rule), the decision budgets are the pinned round-2 values, and no census verdict
    was produced beyond the 2,000,000 cap;
(d) replay provenance is real: a seeded sample of committed rows replays byte-exactly
    from the AK(3) root through the stored h-move composites, and EVERY SPHERICAL row
    (if any) replays and carries the full hit protocol;
(e) member verdicts are re-derivable: three deterministically sampled rows re-decide
    to identical verdict + method through the same pinned stack;
(f) deliberate-mismatch negative controls: corrupted composites / states / parents
    make the replay checks raise;
(g) the summary's AK(2) comparison side matches the committed AK(2) artifacts.
"""

from __future__ import annotations

import copy
import json
import os
import random

import pytest

from experiments.stable_ac.fable import ac_words as W
from experiments.stable_ac.fable import ak2_battery as AB
from experiments.stable_ac.fable import ak3_matched_control as M
from experiments.stable_ac.fable.disconnected_split import decide_pair

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MEMBERS_PATH = os.path.join(REPO_ROOT, "results", "stable_ac", "fable",
                            "ak3_matched_members.jsonl")
SUMMARY_PATH = os.path.join(REPO_ROOT, "results", "stable_ac", "fable",
                            "ak3_matched_summary.json")
AK2_SUMMARY_PATH = os.path.join(REPO_ROOT, "results", "stable_ac", "fable",
                                "ak2_battery_summary.json")
AK2_MEMBERS_PATH = os.path.join(REPO_ROOT, "results", "stable_ac", "fable",
                                "ak2_members.jsonl")


@pytest.fixture(scope="module")
def member_rows():
    rows = []
    with open(MEMBERS_PATH, encoding="utf-8") as fh:
        for line in fh:
            rows.append(json.loads(line))
    assert rows, "ak3_matched_members.jsonl is empty"
    return rows


@pytest.fixture(scope="module")
def member_index(member_rows):
    return {tuple(r["canonical"]): r for r in member_rows}


@pytest.fixture(scope="module")
def summary():
    with open(SUMMARY_PATH, encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def prefix_harvest():
    """One shared 50-pop provenance harvest (used by both (a) and (b))."""
    return M.harvest_members_prov(M.AK3, pops=50, cap=M.CAP)


# --------------------------------------------------------------------------------------
# (a) operator identity with the AK(2) battery's harvest
# --------------------------------------------------------------------------------------


def test_operator_is_byte_identical_to_ak2_battery_on_a_prefix(prefix_harvest):
    ref = AB.harvest_members(M.AK3, pops=50, cap=M.CAP)
    assert set(prefix_harvest["members"]) == set(ref["members"])
    assert prefix_harvest["children_generated"] == ref["children_generated"]
    assert prefix_harvest["queue_remaining"] == ref["queue_remaining"]
    for key, rec in prefix_harvest["members"].items():
        other = ref["members"][key]
        assert rec["order"] == other["order"]
        assert rec["first_seen_pop"] == other["first_seen_pop"]
        assert rec["first_exact"] == other["first_exact"]
        assert rec["encounters"] == other["encounters"]


def test_summary_records_the_full_run_identity_check(summary):
    identity = summary["design"]["operator"]["identity_check"]
    assert identity["identical"] is True
    assert identity["pops"] == 1_000
    assert identity["relator_cap"] == 17
    assert identity["members_compared"] == summary["harvest"]["distinct_members"]


# --------------------------------------------------------------------------------------
# (b) harvest determinism: 50-pop prefix identity against the committed rows
# --------------------------------------------------------------------------------------


def test_harvest_prefix_is_deterministic(prefix_harvest, member_rows):
    fresh = sorted(prefix_harvest["members"].items(), key=lambda kv: kv[1]["order"])
    committed = [row for row in member_rows if row["first_seen_pop"] <= 50]
    committed.sort(key=lambda row: row["order"])
    assert len(fresh) == len(committed)
    for (key, rec), row in zip(fresh, committed):
        assert list(key) == row["canonical"]
        assert rec["order"] == row["order"]
        assert rec["first_seen_pop"] == row["first_seen_pop"]
        prov = row["provenance"]
        assert list(rec["first_exact"]) == prov["first_exact"]
        if rec["parent_key"] is None:
            assert prov["parent_key"] is None
            assert prov["move_composite"] is None
        else:
            assert list(rec["parent_key"]) == prov["parent_key"]
            assert prov["parent_exact"] == prov["parent_key"]
            assert list(rec["realization"]) == prov["realization"]
            assert rec["concat_move"] == prov["concat_move"]


# --------------------------------------------------------------------------------------
# (c) budget assertions (hard session rule: EXACTLY 1,000 pops)
# --------------------------------------------------------------------------------------


def test_budgets_were_respected(summary, member_rows):
    assert summary["budgets"]["harvest_pops"] == 1_000            # EXACTLY
    assert summary["budgets"]["harvest_pop_budget"] == 1_000
    assert summary["harvest"]["pops"] == 1_000
    assert summary["budgets"]["relator_cap"] == 17                # root total 13 + 4
    assert summary["budgets"]["scheme_budget"] == 200_000         # pinned round-2
    assert summary["budgets"]["branch_budget"] == 2_000_000
    assert summary["budgets"]["census_cap"] == 2_000_000
    assert summary["budgets"]["tc_hit_cap"] == 50_000
    assert summary["harvest"]["distinct_members"] == len(member_rows)
    # no verdict was produced beyond the census cap
    for row in member_rows:
        if row["verdict"] in ("SPHERICAL", "NOT_SPHERICAL") \
                and row["method"] == "factorial_census":
            assert row["census"]["expected_cases"] <= 2_000_000


def test_run_control_refuses_an_off_budget_run(tmp_path):
    with pytest.raises(AssertionError):
        M.run_control(str(tmp_path / "m.jsonl"), str(tmp_path / "s.json"), pops=10)


def test_undecided_rows_are_named_never_folded(member_rows, summary):
    undecided = [r for r in member_rows if r["verdict"] == "UNDECIDED_BUDGET"]
    assert len(undecided) == summary["undecided_budget_rows"]
    for row in undecided:
        assert row["census"] is None or row["census"]["status"] != "OK" \
            or row["census"]["minimum_defect"] is None


# --------------------------------------------------------------------------------------
# (d) replay provenance: sampled chains + every SPHERICAL member
# --------------------------------------------------------------------------------------


def test_root_row_is_the_ak3_root(member_rows):
    root = member_rows[0]
    assert root["order"] == 0 and root["first_seen_pop"] == 0
    assert tuple(root["canonical"]) == W.canon_pair(*M.AK3)
    assert root["provenance"]["first_exact"] == list(M.AK3)
    assert root["provenance"]["parent_key"] is None


def test_sampled_chains_replay_byte_exactly_from_the_root(member_index, member_rows):
    non_root = [tuple(r["canonical"]) for r in member_rows if r["order"] > 0]
    rng = random.Random(1234)                     # test-local seed, disjoint from the
    sample = rng.sample(non_root, 10)             # module run's 100-member sample
    for key in sample:
        chain = M.replay_chain(key, member_index, M.AK3, M.CAP)
        assert chain["verified"] is True
        assert chain["chain_steps"] >= 1
        assert chain["h_moves_total"] == sum(chain["h_moves_per_step"])


def test_summary_records_the_100_chain_sample(summary):
    sample = summary["replay_verification"]["chain_sample"]
    assert sample["seed"] == M.REPLAY_SEED
    assert sample["requested"] == 100
    assert sample["verified"] == 100
    assert len(sample["chains"]) == 100
    steps = summary["replay_verification"]["single_steps"]
    assert steps["single_step_composites_verified"] == steps["members_total"] - 1


def test_every_spherical_row_replays_and_carries_the_hit_protocol(member_rows,
                                                                  member_index,
                                                                  summary):
    spherical = [r for r in member_rows if r["verdict"] == "SPHERICAL"]
    assert len(spherical) == summary["spherical_rows"]
    assert summary["LOUD_SPHERICAL_ALERT"] == bool(spherical)
    assert len(summary["SPHERICAL_HITS"]) == len(spherical)
    assert summary["replay_verification"]["spherical_chains_verified"] \
        == len(spherical)
    if not spherical:
        return
    for row in spherical:
        # the artifacts must carry the full protocol ...
        assert row["chain_replay"]["verified"] is True
        assert row["re_decision"]["agrees"] is True
        protocol = row["hit_protocol"]
        assert protocol["hit"] is True
        assert "todd_coxeter" in protocol
        # ... and the chain must re-replay on the spot
        chain = M.replay_chain(tuple(row["canonical"]), member_index, M.AK3, M.CAP)
        assert chain["verified"] is True


# --------------------------------------------------------------------------------------
# (e) verdict re-derivability on three deterministic samples
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
# (f) deliberate-mismatch negative controls
# --------------------------------------------------------------------------------------


def _first_deep_row(member_rows):
    """A committed non-root row (mid-file, so the chain has at least one step)."""
    return copy.deepcopy(member_rows[len(member_rows) // 2])


def test_corrupted_exact_state_fails_the_step_replay(member_rows):
    row = _first_deep_row(member_rows)
    prov = row["provenance"]
    exact = list(prov["first_exact"])
    exact[0] = exact[0][0].swapcase() + exact[0][1:]   # well-formed, wrong state
    with pytest.raises(M.ReplayVerificationError):
        M.verify_step(prov["parent_exact"], prov["move_composite"], exact,
                      tuple(row["canonical"]), M.CAP)


def test_corrupted_move_composite_fails_the_step_replay(member_rows):
    row = _first_deep_row(member_rows)
    prov = row["provenance"]
    moves = list(prov["move_composite"])
    moves[0] = 1 + (moves[0] % 12)
    with pytest.raises(M.ReplayVerificationError):
        M.verify_step(prov["parent_exact"], moves, prov["first_exact"],
                      tuple(row["canonical"]), M.CAP)


def test_corrupted_parent_fails_the_chain_replay(member_index, member_rows):
    row = _first_deep_row(member_rows)
    key = tuple(row["canonical"])
    row["provenance"]["parent_exact"] = list(M.AK3)    # no longer == parent_key
    corrupted = dict(member_index)
    corrupted[key] = row
    with pytest.raises(M.ReplayVerificationError):
        M.replay_chain(key, corrupted, M.AK3, M.CAP)


def test_wrong_canonical_fails_the_step_replay(member_rows):
    row = _first_deep_row(member_rows)
    prov = row["provenance"]
    with pytest.raises(M.ReplayVerificationError):
        M.verify_step(prov["parent_exact"], prov["move_composite"],
                      prov["first_exact"], W.canon_pair(*M.AK3), M.CAP)


# --------------------------------------------------------------------------------------
# (g) the comparison block against the committed AK(2) artifacts
# --------------------------------------------------------------------------------------


def test_comparison_ak2_side_matches_the_committed_artifacts(summary):
    with open(AK2_SUMMARY_PATH, encoding="utf-8") as fh:
        ak2_summary = json.load(fh)
    side = summary["comparison"]["ak2"]
    assert side["distinct_members"] == ak2_summary["harvest"]["distinct_members"]
    assert side["spherical_rows"] == ak2_summary["spherical_rows"]
    assert side["relator_cap"] == ak2_summary["budgets"]["relator_cap"] == 15
    assert side["harvest_pops"] == ak2_summary["budgets"]["harvest_pops"] == 1_000
    assert side["committed_verdict_method_histogram"] \
        == ak2_summary["member_verdicts"]
    # spot totals quoted in the calibration note
    assert side["distinct_members"] == 13_040
    assert side["spherical_rows"] == 397
    assert side["non_degenerate_spherical_rows"] == 227


def test_comparison_ak3_side_matches_the_member_rows(summary, member_rows):
    side = summary["comparison"]["ak3"]
    fresh = M.spherical_stats(member_rows)
    assert side["distinct_members"] == fresh["distinct_members"] == len(member_rows)
    assert side["verdict_histogram"] == fresh["verdict_histogram"]
    assert side["spherical_rows"] == fresh["spherical_rows"]
    assert side["spherical_by_total_length"] == fresh["spherical_by_total_length"]
    assert side["non_degenerate_spherical_rows"] \
        == fresh["non_degenerate_spherical_rows"]
    assert side["undecided_budget_rows"] == fresh["undecided_budget_rows"]
    assert summary["member_verdicts"] == fresh["verdict_method_histogram"]
    assert side["relator_cap"] == 17 and side["root"] == list(M.AK3)


# --------------------------------------------------------------------------------------
# slow extras (skip-marked; the artifacts already carry the full data)
# --------------------------------------------------------------------------------------


@pytest.mark.skip(reason="the full 1,000-pop harvest regeneration takes ~2x17s and "
                         "re-verifying every single-step composite ~1 minute; the "
                         "50-pop prefix is asserted above and the module run "
                         "recorded a full-run operator-identity check")
def test_full_harvest_and_composites_regenerate(member_rows):
    harvest = M.harvest_members_prov(M.AK3, pops=M.HARVEST_POPS, cap=M.CAP)
    assert harvest["distinct_members"] == len(member_rows)
    M.attach_and_verify_composites(harvest)
    ordered = sorted(harvest["members"].items(), key=lambda kv: kv[1]["order"])
    for (key, rec), row in zip(ordered, member_rows):
        assert list(key) == row["canonical"]
        assert rec["order"] == row["order"]
        assert rec["encounters"] == row["provenance"]["encounters"]
        if rec["parent_key"] is not None:
            assert list(rec["move_composite"]) \
                == row["provenance"]["move_composite"]


@pytest.mark.skip(reason="re-deciding all members takes many minutes; three rows are "
                         "re-derived above and the run is deterministic")
def test_every_member_verdict_re_derives(member_rows):
    for row in member_rows:
        verdict, _support = decide_pair(tuple(row["canonical"]))
        assert verdict.verdict == row["verdict"]


@pytest.mark.skip(reason="replaying every member's full chain from the root takes "
                         "several minutes; the module run verified every single-step "
                         "composite plus a seeded 100-chain sample, and 10 chains "
                         "are re-verified above")
def test_every_chain_replays(member_index, member_rows):
    for row in member_rows[1:]:
        chain = M.replay_chain(tuple(row["canonical"]), member_index, M.AK3, M.CAP)
        assert chain["verified"] is True
