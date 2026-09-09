"""The 10k re-run of the whole Aut-min screen: its inputs and its oracle.

This file exists to run at 10,000 nodes over 72,779 orbits and then be SPLICED
onto the surviving 100k/1M/5M rungs. The splice is only legitimate if three
things hold, and each is checked here rather than asserted in a docstring:

  * the cap is the one the higher rungs ran at (a different corridor is a
    different search, not a cheaper prefix of the same one);
  * the row list is the screen itself, whole;
  * the archived failure lists really are what `verify` treats them as -- rows
    judged at exactly this budget, which ran it out.
"""
import csv
import os

import pytest

from experiments.search import run_ac19_autmin_10k as r10k
from experiments.search.run_leftovers_1m import ARMS, MAX_RELATOR_LENGTH


@pytest.fixture(scope="module")
def rows():
    return r10k.load_rows()


def test_row_list_is_the_whole_screen(rows):
    assert len(rows) == r10k.N_ROWS == 72_779
    names = [r["name"] for r in rows]
    assert len(set(names)) == len(names)
    assert all(r["r1"] and r["r2"] for r in rows)


def test_cap_matches_the_rungs_this_file_splices_onto():
    # 48 is not a preference. The 100k/1M/5M rungs ran at it, and a search at
    # another cap could not be read as a prefix of theirs.
    assert r10k.MRL == MAX_RELATOR_LENGTH == 48
    assert r10k.BUDGET == 10_000


def test_arms_are_the_shipped_ones_and_recommended_is_still_refused():
    assert set(r10k.ARM_CHOICES) <= set(ARMS)
    assert "hybrid_10m" not in r10k.ARM_CHOICES      # a different experiment
    for withdrawn in ("RECOMMENDED", "s20", "mk20"):
        with pytest.raises((ValueError, KeyError)):
            r10k.resolve_arm(withdrawn)


def test_out_path_names_the_campaign_budget_and_cap():
    p = r10k.out_path("greedy", "/tmp/x")
    assert os.path.basename(p) == "ac19_autmin_10k_greedy_b10000_mrl48.jsonl"
    # A chunk tag only appears when there is more than one chunk, so a
    # single-chunk run and a resumed one agree on the filename.
    assert r10k.out_path("greedy", "/tmp/x", 1, 1) == p
    assert r10k.out_path("s20_mk2", "/tmp/x", 4, 3).endswith(
        "ac19_autmin_10k_s20_mk2_b10000_mrl48_part3of4.jsonl")


@pytest.mark.parametrize("chunks", [1, 4, 16])
def test_chunks_partition_the_screen(rows, chunks):
    parts = [r10k.stride_chunk(rows, chunks, i) for i in range(1, chunks + 1)]
    assert sum(len(p) for p in parts) == len(rows)
    seen = set()
    for part in parts:
        names = {r["name"] for r in part}
        assert not (names & seen)            # disjoint
        seen |= names
    assert seen == {r["name"] for r in rows}  # and covering


@pytest.mark.parametrize("arm,csv_name", sorted(r10k.ORACLE_CSV.items()))
def test_oracle_is_a_subset_of_the_screen_judged_at_this_budget(rows, arm, csv_name):
    with open(os.path.join(r10k.SCREEN_DIR, csv_name), newline="") as fh:
        oracle = list(csv.DictReader(fh))
    assert oracle
    names = {r["name"] for r in rows}
    assert {r["name"] for r in oracle} <= names
    # Every archived failure ran the budget out. That is what makes it an
    # oracle for BOTH the verdict and the node count: a re-run that stops
    # anywhere else on these rows is not the same search.
    assert all(int(r["nodes_explored"]) == r10k.BUDGET for r in oracle)


def test_the_two_oracles_overlap_but_neither_contains_the_other():
    """s20_mk2 is the stronger arm, and it is NOT uniformly stronger.

    Pinned because the intuition runs the other way and the numbers are load
    bearing. Of greedy's 831 failures and s20_mk2's 259, exactly 225 are shared
    -- and 225 is precisely the row count the week-9 deck's three-arm
    head-to-head rests on, because a mutual failure is the only row for which
    the archive holds a real cost for BOTH arms. 34 rows go the other way:
    greedy solves them inside 10,000 nodes and s20_mk2 does not.
    """
    def names(csv_name):
        with open(os.path.join(r10k.SCREEN_DIR, csv_name), newline="") as fh:
            return {r["name"] for r in csv.DictReader(fh)}
    greedy, s20 = names(r10k.ORACLE_CSV["greedy"]), names(r10k.ORACLE_CSV["s20_mk2"])
    assert (len(greedy), len(s20)) == (831, 259)
    assert len(greedy & s20) == 225
    assert len(s20 - greedy) == 34
    assert len(greedy - s20) == 606


def test_run_refuses_a_silent_python_fallback(monkeypatch):
    # A 72,779-row sweep on the reference implementation is a different cost
    # and a different provenance. It must be a decision someone made, not one
    # a failed import made for them.
    monkeypatch.setattr(r10k, "HAVE_HCOMPACT", False)
    with pytest.raises(SystemExit, match="hcompact"):
        r10k.run("greedy", "/tmp/should-not-be-created", log=lambda *_: None)


# --------------------------------------------------- the coverage-gap residue

def test_unescalated_lists_re_derive():
    """The 13 rows are derived from the jsonls, never stored and trusted."""
    from experiments.search import make_ac19_unescalated_lists as mk
    assert mk.check() == []
    derived = mk.build()
    assert len(derived["greedy"]) == 12
    assert len(derived["s20_mk2"]) == 1


def test_the_one_s20_row_is_the_documented_coverage_gap():
    """`ac19_33435` is not a random gap row.

    `run_leftovers_1m` names it as the single orbit outside the 70,723 both arms
    searched at 10k. It reaching the never-escalated list from the other end --
    failing s20_mk2's 10k screen with no rung above it -- is the same fact, and
    pinning the identity keeps the two halves from drifting apart.
    """
    from experiments.search import make_ac19_unescalated_lists as mk
    from experiments.search.run_leftovers_1m import COMMON_DENOMINATOR_EXCLUDED
    assert [r["name"] for r in mk.build()["s20_mk2"]] == ["ac19_33435"]
    assert COMMON_DENOMINATOR_EXCLUDED["greedy"] == ("ac19_33435",)


def test_every_unescalated_row_is_now_closed():
    """All 13 solve on the rung they were escalated to, and none below its floor.

    Each of these rows failed at exactly 10,000 nodes on its own arm. A solve at
    or below 10,000 in the re-run at the same cap would mean the search that ran
    is not the search that built the list, exactly as the 10k oracle checks from
    the other direction.
    """
    import json
    out = os.path.join(r10k.ROOT, "results", "heuristic_search", "ac19_unescalated")
    closed = {}
    for stem in ("leftovers_1m_greedy_b100000_mrl48.jsonl",
                 "leftovers_1m_greedy_b1000000_mrl48.jsonl",
                 "leftovers_1m_s20_mk2_b100000_mrl48.jsonl"):
        path = os.path.join(out, stem)
        assert os.path.exists(path), f"{stem} missing -- the rung has not been run"
        for line in open(path):
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec.get("solved"):
                assert rec["nodes_explored"] > r10k.BUDGET, (
                    f"{rec['name']} solved at {rec['nodes_explored']} <= "
                    f"{r10k.BUDGET}, which its 10k run says is impossible")
                closed.setdefault(rec["arm"], set()).add(rec["name"])
    assert len(closed["greedy"]) == 12
    assert len(closed["s20_mk2"]) == 1
