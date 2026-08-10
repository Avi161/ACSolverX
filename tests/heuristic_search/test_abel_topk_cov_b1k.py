"""Pins the budget-1,000 abel top-K CoV re-ranking.

The runner explores 0 nodes — it re-reads a frozen sweep — so these tests are cheap and
deterministic. They cover three things the report leans on:

* the ranking keys are search-free (a key that could read ``solved`` would invalidate every
  arm at once), and the statistics helpers are right;
* the four fatal data gates actually fire on corrupted input rather than passing silently;
* the headline numbers are pinned, including the cross-implementation agreement with the
  live-search ``abel_double_cov_b1k`` runner.
"""
from __future__ import annotations

import csv
import json
import os

import pytest

from experiments.heuristic_search.runners import abel_topk_cov_b1k as R


# ------------------------------------------------------------------ the key itself

def test_exponent_sums_counts_case_as_sign():
    assert R.exponent_sums("xxXy") == (1, 1)
    assert R.exponent_sums("XYYY") == (-1, -3)
    assert R.exponent_sums("") == (0, 0)


def test_abel_magnitude_is_the_documented_formula():
    # |1-0| + |0-1| over r1, |0-2| + |1-0| over r2
    assert R.abel_magnitude("xY", "XXy") == 1 + 1 + 2 + 1


def test_abel_magnitude_is_blind_to_a_trivially_abelianized_pair():
    """The documented failure mode: cancelling exponents score 0 regardless of length."""
    assert R.abel_magnitude("xXyY", "yYxX") == 0
    assert R.abel_magnitude("xxXXyyYY", "x") == 1


def test_every_key_ignores_the_solved_flag():
    """The load-bearing property: no ranking key may read the search outcome."""
    row = {"r1": "xxy", "r2": "Yx", "solved": True, "nodes_explored": 7,
           "z_word": "x", "iso_gen": "y", "iso_index": 0}
    flipped = dict(row, solved=False, nodes_explored=999_999, path_length=3)
    for name, key in R.KEYS.items():
        assert key(row) == key(flipped), f"{name} changed when the search outcome changed"


# ------------------------------------------------------------------------ helpers

def _cand(r1, r2, solved, nodes, z="z", gen="x", idx=0):
    return {"r1": r1, "r2": r2, "solved": solved, "nodes_explored": nodes,
            "z_word": z, "iso_gen": gen, "iso_index": idx}


def test_rank_tie_modes_bracket_each_other():
    """Two candidates with an identical key, one solving: the tie mode decides the order."""
    a = _cand("xy", "xy", False, 1000, z="a")
    b = _cand("xy", "xy", True, 4, z="b")
    cands = [a, b]
    assert R.solves_within(R.rank(cands, R.KEYS["abel"], "optimistic"), 1)
    assert not R.solves_within(R.rank(cands, R.KEYS["abel"], "adversarial"), 1)
    # ident is name-ordered, so "a" (unsolved) comes first — reproducible, not favourable
    assert R.rank(cands, R.KEYS["abel"], "ident")[0] is a


def test_cumulative_nodes_stops_at_the_first_solve():
    cands = [_cand("x", "x", False, 1000, z="a"), _cand("x", "x", True, 12, z="b"),
             _cand("x", "x", True, 3, z="c")]
    assert R.cumulative_nodes(cands, 3) == 1012
    assert R.cumulative_nodes(cands, 1) is None


def test_random_exact_matches_a_hand_computed_probability():
    """4 candidates, 1 solving, K=2 -> 1 - C(3,2)/C(4,2) = 1 - 3/6 = 0.5."""
    cov = {0: [_cand("x", "x", i == 0, 1, z=str(i)) for i in range(4)]}
    saved, R.KS = R.KS, (2,)
    try:
        assert R.random_exact(cov)[2] == pytest.approx(0.5)
    finally:
        R.KS = saved


def test_mcnemar_uses_only_the_discordant_rows():
    only_a, only_b, p = R.mcnemar({1, 2, 3}, {3, 4})
    assert (only_a, only_b) == ([1, 2], [4])
    assert p == pytest.approx(1.0)                     # 2 vs 1 is nowhere near significant
    assert R.mcnemar({1, 2}, set())[2] == pytest.approx(0.5)      # 2-0: still not evidence
    assert R.mcnemar(set(), set())[2] == 1.0
    assert R.mcnemar(set(range(10)), set())[2] < 0.01            # 10-0 is


def test_orbit_view_collapses_a_duplicated_class_and_reports_splits():
    auts = {1: 7, 2: 7, 3: 9}
    n, full, split = R.orbit_view(auts, {1, 2, 3}, [1, 2, 3])
    assert (n, full, split) == (2, 2, [])
    n, full, split = R.orbit_view(auts, {1, 3}, [1, 2, 3])       # class 7 half-solved
    assert (n, full, split) == (2, 1, [7])


# -------------------------------------------------------------------- data gates

def _sweep_rows():
    with open(os.path.join(R.ROOT, R.SWEEP)) as fh:
        return [json.loads(line) for line in fh]


def test_the_sweep_is_at_the_stated_budget_and_never_exceeds_it():
    rows = _sweep_rows()
    assert rows, "sweep is empty"
    assert all(d["node_budget"] == R.BUDGET for d in rows)
    assert all(d["nodes_explored"] <= R.BUDGET for d in rows)


def test_r1_r2_are_the_start_strings_so_no_key_can_read_the_search():
    """Gate 2, checked directly on the file rather than through the runner."""
    assert all(len(d["r1"]) + len(d["r2"]) == d["start_total_length_cov"]
               for d in _sweep_rows())


def test_truncation_gate_holds_against_the_independent_10k_sweep():
    n = R.gate_truncation()
    assert n == 6788


def test_truncation_gate_fires_when_a_solved_flag_is_wrong(tmp_path, monkeypatch):
    """A gate that never fails is decoration. Corrupt one row and it must raise."""
    rows = _sweep_rows()
    for d in rows:                       # flip the first row that the 10k run solved late
        if not d["solved"]:
            d["solved"] = True
            break
    bad = tmp_path / "corrupt.jsonl"
    bad.write_text("".join(json.dumps(d) + "\n" for d in rows))
    monkeypatch.setattr(R, "SWEEP", str(bad))
    monkeypatch.setattr(R, "ROOT", R.ROOT)
    with pytest.raises(AssertionError, match="solved@1k"):
        R.gate_truncation()


def test_subset60_covers_sixty_presentations_each_with_candidates_and_a_control():
    ids60, bins, auts, cov, control = R.load()
    assert len(ids60) == 60 and len(set(ids60)) == 60
    assert set(cov) == set(ids60) and set(control) == set(ids60)
    assert all(cov[p] for p in ids60)
    assert all(d.get("n_cov", 0) > 0 for v in cov.values() for d in v)


def test_subset60_is_fortyfive_aut_classes_not_sixty():
    """Row counts double-count duplicated orbits; the report has to say both."""
    _, _, auts, _, _ = R.load()
    assert len(set(auts.values())) == 45


# -------------------------------------------------------------- headline numbers

@pytest.fixture(scope="module")
def arms():
    ids60, bins, auts, cov, control = R.load()
    oracle = R.oracle_set(cov)
    greedy = {p for p, c in control.items() if c["solved"]}
    hits = {name: R.arm_hits(cov, R.KEYS[name], "ident", R.HEADLINE_K)
            for name in ("abel", "abel_len_lex", "len_only", "len_then_abel")}
    return ids60, auts, cov, oracle, greedy, hits


def test_the_headline_counts_are_pinned(arms):
    _, _, _, oracle, greedy, hits = arms
    assert len(greedy) == 29, "untransformed greedy baseline @1000"
    assert len(oracle) == 45, "best-CoV oracle @1000"
    assert len(hits["abel"]) == 41, "abel top-3, bare key"
    assert len(hits["len_only"]) == 39, "length-only top-3 control"


def test_abel_top3_agrees_with_the_live_search_runner(arms):
    """Gate 5: two independent code paths — re-ranking a frozen sweep here, and running
    real searches in abel_double_cov_b1k — must land on the same number."""
    _, _, _, _, _, hits = arms
    assert len(hits["abel_len_lex"]) == R.LIVE_HOP1_TOPK == 41


def test_random_top3_is_the_floor_and_the_oracle_the_ceiling(arms):
    _, _, cov, oracle, greedy, hits = arms
    exact = R.random_exact(cov)[R.HEADLINE_K]
    assert 36.0 < exact < 36.5, "random top-3 exact expectation"
    assert len(greedy) < exact < len(hits["len_only"]) < len(hits["abel"]) < len(oracle)


def test_no_arm_can_claim_a_row_the_oracle_misses(arms):
    """Gate 6 — an arm outside the oracle means the arm is reading something it shouldn't."""
    _, _, _, oracle, _, hits = arms
    for name, h in hits.items():
        assert h <= oracle, f"{name} claims {sorted(h - oracle)}"


def test_abel_leads_the_length_control_at_every_k(arms):
    _, _, cov, _, _, _ = arms
    a = R.arm_counts(cov, R.KEYS["abel"], "ident")
    lo = R.arm_counts(cov, R.KEYS["len_only"], "ident")
    assert all(a[k] > lo[k] for k in R.KS), f"abel {a} vs len_only {lo}"


def test_the_abel_lead_over_length_is_underpowered_not_significant(arms):
    """The report must not claim a separation it cannot support; pin the honest p."""
    _, _, _, _, _, hits = arms
    only_abel, only_len, p = R.mcnemar(hits["abel"], hits["len_only"])
    assert (only_abel, only_len) == ([602, 632], [])
    assert p == pytest.approx(0.5)


def test_abel_is_not_merely_a_length_proxy_but_adds_nothing_within_a_length_stratum(arms):
    """Both halves of the null result the report reports."""
    _, _, _, _, _, hits = arms
    assert len(hits["abel"]) > len(hits["len_only"])          # not a proxy: it beats length
    assert len(hits["len_then_abel"]) == len(hits["len_only"])  # but adds 0 at fixed length


def test_the_ranking_survives_an_adversarial_tie_break(arms):
    _, _, cov, _, _, hits = arms
    adv = R.arm_counts(cov, R.KEYS["abel"], "adversarial")
    assert adv[R.HEADLINE_K] == 39
    assert adv[R.HEADLINE_K] > R.random_exact(cov)[R.HEADLINE_K]


def test_orbit_level_ordering_matches_the_row_level_ordering(arms):
    """Guards the duplicate-orbit trap: the headline must not be one big Aut class."""
    ids60, auts, _, oracle, greedy, hits = arms
    n, orb_abel, _ = R.orbit_view(auts, hits["abel"], ids60)
    _, orb_len, _ = R.orbit_view(auts, hits["len_only"], ids60)
    _, orb_oracle, _ = R.orbit_view(auts, oracle, ids60)
    _, orb_greedy, _ = R.orbit_view(auts, greedy, ids60)
    assert n == 45
    assert orb_greedy < orb_len < orb_abel < orb_oracle == 41


def test_the_stratified_probe_is_flat_except_for_one_row_at_k1(arms):
    """The report says "identical at every K except K=1". Pin both halves — an
    unqualified "identical everywhere" would be an overclaim, and the section that
    argues against overclaiming is the worst place to make one."""
    _, _, cov, _, _, _ = arms
    lex = R.arm_counts(cov, R.KEYS["len_lex"], "ident")
    then = R.arm_counts(cov, R.KEYS["len_then_abel"], "ident")
    assert [k for k in R.KS if lex[k] != then[k]] == [1]
    assert (lex[1], then[1]) == (36, 37)


# ---------------------------------------------------- the same test at PR #14's budget

@pytest.fixture(scope="module")
def tenk(arms):
    return R.tenk_arms(arms[0])


def test_pr14_headline_numbers_reproduce_from_the_10k_sweep(tenk):
    """Independent confirmation that PR #14's 52 vs 49 is what its own file says."""
    _, greedy, oracle, hits, _ = tenk
    assert len(greedy) == 40
    assert len(oracle) == 52
    assert len(hits["abel"]) == len(hits["abel_len_lex"]) == 52, "PR #14's abel top-3"
    assert len(hits["len_only"]) == 49, "PR #14's length-only control"


def test_pr14_abel_over_length_is_also_underpowered_at_10k(tenk):
    """The 1k caveat is not an artefact of the tighter budget — the same paired test on
    PR #14's own data is 3-0, p = 0.25. Neither budget separates abel from length."""
    _, _, _, hits, _ = tenk
    only_abel, only_len, p = R.mcnemar(hits["abel"], hits["len_only"])
    assert (only_abel, only_len) == ([573, 634, 635], [])
    assert p == pytest.approx(0.25)


def test_the_10k_band_is_narrower_so_1k_is_the_more_discriminating_test(tenk, arms):
    """At 10k random top-3 already reaches ~48.6 of a 52 ceiling; the headline rests on
    a much smaller effect there than the 1k run's."""
    t_cov, _, t_oracle, _, t_rnd = tenk
    _, _, cov, oracle, _, _ = arms
    assert t_rnd == pytest.approx(48.6, abs=0.1)
    assert len(t_oracle) - t_rnd < len(oracle) - R.random_exact(cov)[R.HEADLINE_K]


def test_the_written_csv_matches_the_computed_arms(arms, tmp_path, monkeypatch):
    """The report is only as good as the table under it."""
    ids60, _, cov, oracle, _, hits = arms
    out = tmp_path / "out.csv"
    monkeypatch.setattr(R, "OUT_CSV", os.path.relpath(out, R.ROOT))
    _, bins, auts, cov2, control = R.load()
    R.write_csv(ids60, bins, auts, cov2, control, oracle,
                R.rank_all(cov2, R.KEYS["abel"]),
                R.rank_all(cov2, R.KEYS["abel_len_lex"]),
                R.rank_all(cov2, R.KEYS["len_only"]))
    with open(out) as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 60
    assert sum(r["abel_top3_solved"] == "True" for r in rows) == len(hits["abel"])
    assert sum(r["len_top3_solved"] == "True" for r in rows) == len(hits["len_only"])
    assert sum(r["oracle_solved"] == "True" for r in rows) == len(oracle)
    assert all(int(r["n_solving_cand"]) > 0 for r in rows if r["oracle_solved"] == "True")
