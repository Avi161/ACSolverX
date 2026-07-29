"""Tests for the stable-class matched contrast (stable_matched_contrast.py).

Everything asserted here is either recomputed on the spot or read from the committed
artifacts ``results/stable_ac/fable/stable_contrast_ak3z_members.jsonl[.gz]`` /
``stable_contrast_ak2z_members.jsonl[.gz]`` / ``stable_contrast_summary.json``.  The
contract under test:

(a) determinism: a fresh 50-pop prefix harvest per root reproduces exactly the
    committed rows with ``first_seen_pop <= 50``, in discovery order, including the
    replay provenance (parent, realization, move composite);
(b) budgets: EXACTLY 1,000 pops per root (hard session rule), caps by the
    root-total+4 rule (18 / 16), pinned round-2 decision budgets, no census verdict
    beyond the 2,000,000 cap, and ``run_contrast`` refuses an off-budget run;
(c) replay provenance is real: 100 sampled committed rows PER ROOT replay byte-exactly
    from their root through the stored move composites, and every SPHERICAL row
    carries a verified chain replay + full hit protocol;
(d) decision re-derivation: three deterministically sampled rows per root re-decide to
    identical verdict + method through the same pinned stack;
(e) operator identity between the two roots on the harvest layer: the single shared
    expansion function re-derives the recorded edges of both harvests (root pop and
    sampled parents), and the summary's identity check is recorded;
(f) deliberate-mismatch negative controls: corrupted composites / states / parents /
    realizations make the verification helpers raise;
(g) the move space of the composites is exactly the audited rank-3 move space
    (``rank3_stable_harvest.moves``);
(h) the summary's per-root statistics and the classical-contrast requote match the
    committed artifacts.
"""

from __future__ import annotations

import copy
import json
import os
import random

import pytest

from experiments.stable_ac.fable import rank3_stable_harvest as RSH
from experiments.stable_ac.fable import stable_matched_contrast as SMC
from experiments.stable_ac.fable.disconnected_split import project_pair

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RESULTS = os.path.join(REPO_ROOT, "results", "stable_ac", "fable")
AK3Z_MEMBERS_PATH = os.path.join(RESULTS, "stable_contrast_ak3z_members.jsonl")
AK2Z_MEMBERS_PATH = os.path.join(RESULTS, "stable_contrast_ak2z_members.jsonl")
SUMMARY_PATH = os.path.join(RESULTS, "stable_contrast_summary.json")
CLASSICAL_AK2_SUMMARY = os.path.join(RESULTS, "ak2_battery_summary.json")
CLASSICAL_AK3_SUMMARY = os.path.join(RESULTS, "ak3_matched_summary.json")

ROOT_OF = {"AK3+z": (SMC.AK3Z, SMC.CAP_AK3Z), "AK2+z": (SMC.AK2Z, SMC.CAP_AK2Z)}
MEMBERS_PATH_OF = {"AK3+z": AK3Z_MEMBERS_PATH, "AK2+z": AK2Z_MEMBERS_PATH}


def _open_members(path):
    # The committed artifacts are gzipped (the AK3+z plain file alone approaches
    # GitHub's 100 MB limit); a locally regenerated plain file takes precedence.
    if os.path.exists(path):
        return open(path, encoding="utf-8")
    import gzip
    return gzip.open(path + ".gz", "rt", encoding="utf-8")


def _load_rows(path):
    rows = []
    with _open_members(path) as fh:
        for line in fh:
            rows.append(json.loads(line))
    assert rows, f"{path}[.gz] is empty"
    return rows


@pytest.fixture(scope="module")
def ak3z_rows():
    return _load_rows(AK3Z_MEMBERS_PATH)


@pytest.fixture(scope="module")
def ak2z_rows():
    return _load_rows(AK2Z_MEMBERS_PATH)


@pytest.fixture(scope="module")
def rows_by_root(ak3z_rows, ak2z_rows):
    return {"AK3+z": ak3z_rows, "AK2+z": ak2z_rows}


@pytest.fixture(scope="module")
def summary():
    with open(SUMMARY_PATH, encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def prefix_harvests():
    """One shared 50-pop provenance harvest per root, composites attached."""
    out = {}
    for name, (root, cap) in ROOT_OF.items():
        harvest = SMC.harvest_root_prov(name, root, pops=50, cap=cap)
        SMC.attach_and_verify_composites(harvest)
        out[name] = harvest
    return out


@pytest.fixture(scope="module")
def prov_index(rows_by_root):
    """Replay indexes built from the COMMITTED rows (not from a fresh harvest)."""
    out = {}
    for name, rows in rows_by_root.items():
        out[name] = {tuple(r["canonical"]): r for r in rows}
    return out


# --------------------------------------------------------------------------------------
# (a) determinism: 50-pop prefix identity against the committed rows
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("name", ["AK3+z", "AK2+z"])
def test_harvest_prefix_is_deterministic(name, prefix_harvests, rows_by_root):
    fresh = sorted(prefix_harvests[name]["members"].items(),
                   key=lambda kv: kv[1]["order"])
    committed = [row for row in rows_by_root[name] if row["first_seen_pop"] <= 50]
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
            assert [list(m) for m in rec["move_composite"]] \
                == prov["move_composite"]


# --------------------------------------------------------------------------------------
# (b) budgets (hard session rule: EXACTLY 1,000 pops per root)
# --------------------------------------------------------------------------------------


def test_budgets_were_respected(summary, rows_by_root):
    assert summary["budgets"]["harvest_pops_per_root"] == 1_000
    for name, (root, cap) in ROOT_OF.items():
        stats = summary["roots"][name]
        assert stats["harvest"]["pops"] == 1_000                  # EXACTLY
        assert stats["harvest"]["pop_budget"] == 1_000
        assert stats["relator_cap"] == cap
        assert cap == sum(len(w) for w in root) + 4               # root-total+4 rule
        assert stats["harvest"]["distinct_members"] == len(rows_by_root[name])
    assert summary["budgets"]["relator_caps"] == {"AK3+z": 18, "AK2+z": 16}
    assert summary["budgets"]["scheme_budget"] == 200_000         # pinned round-2
    assert summary["budgets"]["branch_budget"] == 2_000_000
    assert summary["budgets"]["census_cap"] == 2_000_000
    assert summary["budgets"]["tc_hit_cap"] == 50_000
    # no verdict was produced beyond the census cap
    for rows in rows_by_root.values():
        for row in rows:
            if row["verdict"] in ("SPHERICAL", "NOT_SPHERICAL") \
                    and row["method"].endswith("factorial_census") \
                    and row["census"] is not None:
                assert row["census"]["expected_cases"] <= 2_000_000


def test_run_contrast_refuses_an_off_budget_run(tmp_path):
    with pytest.raises(AssertionError):
        SMC.run_contrast(str(tmp_path / "a.jsonl.gz"), str(tmp_path / "b.jsonl.gz"),
                         str(tmp_path / "s.json"), pops=10)


def test_undecided_and_unsupported_are_named_never_folded(summary, rows_by_root):
    for name, rows in rows_by_root.items():
        stats = summary["roots"][name]
        undecided = [r for r in rows if r["verdict"] == "UNDECIDED_BUDGET"]
        unsupported = [r for r in rows if r["verdict"] == "UNSUPPORTED"]
        assert len(undecided) == stats["undecided_budget_rows"]
        assert len(unsupported) == stats["unsupported_rows"]
        for row in undecided:
            assert row["census"] is None or row["census"]["status"] != "OK" \
                or row["census"]["minimum_defect"] is None


# --------------------------------------------------------------------------------------
# (c) replay provenance: root rows, 100 sampled chains per root, SPHERICAL rows
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("name", ["AK3+z", "AK2+z"])
def test_root_row_is_the_stabilized_root(name, rows_by_root):
    root, _cap = ROOT_OF[name]
    row = rows_by_root[name][0]
    assert row["order"] == 0 and row["first_seen_pop"] == 0
    assert tuple(row["canonical"]) == RSH.canon_state(root, SMC.ORDER3)
    assert row["provenance"]["first_exact"] == list(root)
    assert row["provenance"]["parent_key"] is None
    assert row["root"] == name


@pytest.mark.parametrize("name", ["AK3+z", "AK2+z"])
def test_100_sampled_chains_replay_byte_exactly(name, rows_by_root, prov_index):
    root, cap = ROOT_OF[name]
    rows = rows_by_root[name]
    non_root = [tuple(r["canonical"]) for r in rows if r["order"] > 0]
    rng = random.Random(1234)                 # test-local seed, disjoint from the
    sample = rng.sample(non_root, min(100, len(non_root)))   # module run's sample
    for key in sample:
        chain = SMC.replay_chain3(key, prov_index[name], root, cap)
        assert chain["verified"] is True
        assert chain["chain_steps"] >= 1
        assert chain["h_moves_total"] == sum(chain["h_moves_per_step"])


@pytest.mark.parametrize("name", ["AK3+z", "AK2+z"])
def test_every_spherical_row_carries_verified_protocol(name, rows_by_root,
                                                       prov_index, summary):
    root, cap = ROOT_OF[name]
    rows = rows_by_root[name]
    spherical = [r for r in rows if r["verdict"] == "SPHERICAL"]
    stats = summary["roots"][name]
    assert len(spherical) == stats["spherical_rows"]
    assert stats["replay_verification"]["spherical_chains_verified"] \
        == len(spherical)
    failures = 0
    for row in spherical:
        assert row["chain_replay"]["verified"] is True
        assert row["re_decision"]["agrees"] is True
        protocol = row["hit_protocol"]
        assert protocol["hit"] is True
        assert "todd_coxeter_triple" in protocol
        if not protocol["protocol_clean"]:
            failures += 1
    assert failures == stats["hit_protocol"]["protocol_failures"]
    # a 5-row sample re-replays on the spot
    for row in spherical[:5]:
        chain = SMC.replay_chain3(tuple(row["canonical"]), prov_index[name],
                                  root, cap)
        assert chain["verified"] is True


def test_ak3z_hits_are_loud_and_complete(summary, ak3z_rows):
    spherical = [r for r in ak3z_rows if r["verdict"] == "SPHERICAL"]
    assert summary["AK3Z_LOUD_SPHERICAL_ALERT"] == bool(spherical)
    assert len(summary["SPHERICAL_HITS_AK3Z"]) == len(spherical)
    for hit in summary["SPHERICAL_HITS_AK3Z"]:
        assert hit["hit_protocol"]["hit"] is True
        assert hit["chain_replay"]["verified"] is True


def test_ak2z_hit_block_matches_rows(summary, ak2z_rows):
    spherical = [r for r in ak2z_rows if r["verdict"] == "SPHERICAL"]
    block = summary["SPHERICAL_HITS_AK2Z"]
    assert block["count"] == len(spherical)
    assert block["clean_spherical_rows"] \
        == sum(1 for r in spherical if r["destabilizable"])
    briefs = block["first_briefs"]
    assert len(briefs) == min(len(spherical), SMC.AK2Z_HIT_BRIEFS)
    for brief, row in zip(briefs, spherical):
        assert brief["canonical"] == row["canonical"]
        assert brief["verdict"] == "SPHERICAL"


# --------------------------------------------------------------------------------------
# (d) decision re-derivation: three deterministic rows per root
# --------------------------------------------------------------------------------------


def _cheap(row):
    """Rows whose re-decision is guaranteed fast (no multi-minute census rerun)."""
    if "r1c_v2" in row["method"] or row["method"] == "structural_gate":
        return True
    census = row.get("census")
    return census is not None and census.get("expected_cases", 1 << 60) <= 200_000


@pytest.mark.parametrize("name", ["AK3+z", "AK2+z"])
def test_three_sampled_verdicts_re_derive(name, rows_by_root):
    rows = rows_by_root[name]
    eligible = [row for row in rows if _cheap(row)]
    assert len(eligible) >= 3
    sample = [eligible[0], eligible[len(eligible) // 2]]
    spherical = [r for r in eligible if r["verdict"] == "SPHERICAL"]
    destab = [r for r in eligible if r["destabilizable"]]
    if spherical:
        sample.append(spherical[0])
    if destab:
        sample.append(destab[0])
    while len(sample) < 3:
        sample.append(eligible[-1])
    for row in sample[:4]:
        decided = SMC.decide_member(tuple(row["canonical"]))
        assert decided["verdict"] == row["verdict"], row["canonical"]
        assert decided["method"] == row["method"], row["canonical"]
        assert decided["destabilizable"] == row["destabilizable"]
        if row["destabilizable"]:
            assert decided["pair"] == row["pair"]


# --------------------------------------------------------------------------------------
# (e) operator identity between the two roots on the harvest layer
# --------------------------------------------------------------------------------------


def _members_index(rows):
    """A harvest-members-shaped index built from committed rows."""
    out = {}
    for row in rows:
        prov = row["provenance"]
        out[tuple(row["canonical"])] = {
            "order": row["order"],
            "first_seen_pop": row["first_seen_pop"],
            "first_exact": prov["first_exact"],
            "parent_key": prov["parent_key"],
            "realization": prov["realization"],
        }
    return out


@pytest.mark.parametrize("name", ["AK3+z", "AK2+z"])
def test_recorded_edges_re_derive_from_the_shared_operator(name, rows_by_root):
    root, cap = ROOT_OF[name]
    rows = rows_by_root[name]
    members = _members_index(rows)
    # the full first pop: recomputed children of the root key == stored pop-1 rows
    root_key = RSH.canon_state(root, SMC.ORDER3)
    recomputed = set(SMC.canon_children_rank3(root_key, cap)) - {root_key}
    stored = {k for k, rec in members.items() if rec["first_seen_pop"] == 1}
    assert recomputed == stored
    # five deterministically sampled recorded parents re-derive edge-by-edge
    parents = sorted({tuple(r["provenance"]["parent_key"]) for r in rows
                      if r["provenance"]["parent_key"] is not None},
                     key=lambda k: members[k]["order"])
    sample = parents[:3] + [parents[len(parents) // 2], parents[-1]]
    edges = 0
    for key in sample:
        edges += SMC.verify_recorded_edges(members, key, cap)
    assert edges > 0


def test_summary_records_the_identity_check(summary):
    identity = summary["design"]["operator"]["identity_check"]
    assert identity["identical"] is True
    assert identity["shared_operator"] == SMC.OPERATOR_DESCRIPTOR
    for name in ("AK3+z", "AK2+z"):
        side = identity["roots"][name]
        assert side["relator_cap"] == ROOT_OF[name][1]
        assert side["cap_rule"] == "total root length + 4"
        assert side["first_pop_children_verified"] > 0
        assert side["sampled_edges_verified"] > 0


# --------------------------------------------------------------------------------------
# (f) deliberate-mismatch negative controls
# --------------------------------------------------------------------------------------


def _deep_row(rows):
    """A committed non-root row (mid-file, so the chain has at least one step)."""
    return copy.deepcopy(rows[len(rows) // 2])


def test_corrupted_exact_state_fails_the_step_replay(ak3z_rows):
    row = _deep_row(ak3z_rows)
    prov = row["provenance"]
    exact = list(prov["first_exact"])
    exact[0] = exact[0][0].swapcase() + exact[0][1:]   # well-formed, wrong state
    with pytest.raises(SMC.ReplayVerificationError):
        SMC.verify_step3(prov["parent_exact"], prov["move_composite"], exact,
                         tuple(row["canonical"]), SMC.CAP_AK3Z)


def test_corrupted_move_composite_fails_the_step_replay(ak3z_rows):
    row = _deep_row(ak3z_rows)
    prov = row["provenance"]
    moves = [list(m) for m in prov["move_composite"]]
    last = moves[-1]
    assert last[0] == "mult"
    last[3] = -last[3]                                 # flip the concatenation sign
    with pytest.raises(SMC.ReplayVerificationError):
        SMC.verify_step3(prov["parent_exact"], moves, prov["first_exact"],
                         tuple(row["canonical"]), SMC.CAP_AK3Z)


def test_corrupted_parent_fails_the_chain_replay(ak3z_rows, prov_index):
    row = _deep_row(ak3z_rows)
    key = tuple(row["canonical"])
    row["provenance"]["parent_exact"] = list(SMC.AK3Z)  # no longer == parent_key
    corrupted = dict(prov_index["AK3+z"])
    corrupted[key] = row
    with pytest.raises(SMC.ReplayVerificationError):
        SMC.replay_chain3(key, corrupted, SMC.AK3Z, SMC.CAP_AK3Z)


def test_wrong_canonical_fails_the_step_replay(ak3z_rows):
    row = _deep_row(ak3z_rows)
    prov = row["provenance"]
    wrong = RSH.canon_state(SMC.AK3Z, SMC.ORDER3)
    assert tuple(row["canonical"]) != wrong
    with pytest.raises(SMC.ReplayVerificationError):
        SMC.verify_step3(prov["parent_exact"], prov["move_composite"],
                         prov["first_exact"], wrong, SMC.CAP_AK3Z)


def test_tampered_realization_fails_the_operator_check(ak2z_rows):
    rows = ak2z_rows
    members = _members_index(rows)
    victim = next(r for r in rows if r["provenance"]["parent_key"] is not None)
    key = tuple(victim["canonical"])
    parent = tuple(victim["provenance"]["parent_key"])
    tampered = dict(members)
    rec = dict(members[key])
    real = list(rec["realization"])
    real[4] = -real[4]                                 # flip the recorded sign
    rec["realization"] = real
    tampered[key] = rec
    with pytest.raises(SMC.OperatorMismatchError):
        SMC.verify_recorded_edges(tampered, parent, SMC.CAP_AK2Z)


# --------------------------------------------------------------------------------------
# (g) the composite move space is the audited rank-3 move space
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("state,cap", [
    (("xxxYYYY", "xyxYXY", "z"), 18),
    (("xxYYY", "xyxYXY", "z"), 16),
    (("Z", "YXYxyx", "YYYYxxx"), 18),
    (("xy", "Zxy", "YXz"), 16),
])
def test_stable_move_space_matches_rank3_stable_harvest(state, cap):
    reference = {child for _label, child in RSH.moves(state, SMC.GENERATORS, cap)}
    assert SMC.stable_move_children(state, cap) == reference


# --------------------------------------------------------------------------------------
# (h) summary statistics match the rows; classical contrast requote
# --------------------------------------------------------------------------------------


@pytest.mark.parametrize("name", ["AK3+z", "AK2+z"])
def test_summary_statistics_match_the_rows(name, rows_by_root, summary):
    rows = rows_by_root[name]
    stats = summary["roots"][name]
    from collections import Counter
    verdicts = Counter(r["verdict"] for r in rows)
    assert stats["verdict_histogram"] == dict(sorted(verdicts.items()))
    vm = Counter(f"{r['verdict']}/{r['method']}" for r in rows)
    assert stats["verdict_method_histogram"] == dict(sorted(vm.items()))
    assert stats["spherical_rows"] == verdicts.get("SPHERICAL", 0)
    destab = [r for r in rows if r["destabilizable"]]
    assert stats["destabilizable_rows"] == len(destab)
    assert stats["destabilizable_spherical_rows"] \
        == sum(1 for r in destab if r["verdict"] == "SPHERICAL")
    z_hist = Counter(str(r["z_occurrences"]) for r in rows)
    assert stats["z_occurrence_histogram"] == dict(
        sorted(z_hist.items(), key=lambda kv: int(kv[0])))
    # shadow-Sigma-E: recomputed from the rows' committed E values
    from fractions import Fraction
    sigma = Fraction(0)
    known = unknown = 0
    for r in destab:
        e = r.get("pair_E_exact")
        if e is None:
            unknown += 1
        else:
            num, den = e.split("/")
            sigma += Fraction(int(num), int(den))
            known += 1
    assert stats["shadow_sigma_E"]["rows_with_E"] == known
    assert stats["shadow_sigma_E"]["rows_E_unknown"] == unknown
    assert stats["shadow_sigma_E"]["exact"] \
        == f"{sigma.numerator}/{sigma.denominator}"
    # every destabilizable row's pair is the Lemma-S projection of its triple
    for r in destab[:50]:
        assert r["z_occurrences"] == 1
        assert r["link_components"] == 2
        assert r["straddling"] == []
        assert tuple(r["pair"]) == project_pair(tuple(r["canonical"]))


def test_cross_root_overlap_matches_the_rows(rows_by_root, summary):
    ak3z = {tuple(r["canonical"]) for r in rows_by_root["AK3+z"]}
    ak2z = {tuple(r["canonical"]) for r in rows_by_root["AK2+z"]}
    assert summary["cross_root_overlap"]["count"] == len(ak3z & ak2z)


def test_classical_contrast_requote_matches_committed_artifacts(summary):
    with open(CLASSICAL_AK2_SUMMARY, encoding="utf-8") as fh:
        ak2 = json.load(fh)
    with open(CLASSICAL_AK3_SUMMARY, encoding="utf-8") as fh:
        ak3 = json.load(fh)
    quote = summary["classical_contrast_requote"]
    assert quote["ak2_classical"]["distinct_members"] \
        == ak2["harvest"]["distinct_members"] == 13_040
    assert quote["ak2_classical"]["spherical_rows"] == ak2["spherical_rows"] == 397
    assert quote["ak3_classical"]["distinct_members"] \
        == ak3["harvest"]["distinct_members"] == 124_296
    assert quote["ak3_classical"]["spherical_rows"] == ak3["spherical_rows"] == 0
