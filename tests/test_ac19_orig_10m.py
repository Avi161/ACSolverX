"""The pre-aut-min originals list: re-derived, not trusted.

Lucas Fagan's question only has an answer if these rows really are the
originals of the orbits the arms failed at 10M, and if the arms really do no
basis work of their own. Both are checked here rather than asserted in a
docstring.
"""
import csv
import os

import pytest

from experiments.search import make_ac19_orig_10m_lists as mk
from experiments.search.run_leftovers_1m import SCREEN_DIR
from experiments.search.run_leftovers_5m import CAMPAIGNS, load_rows_5m

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope="module")
def derived():
    return mk.build()


def test_lists_match_the_derivation():
    assert mk.check() == []


def test_counts(derived):
    assert len(derived["greedy"]) == 40
    assert len(derived["s20_mk2"]) == 18
    assert len({r["orbit"] for r in derived["greedy"]}) == 28
    assert len({r["orbit"] for r in derived["s20_mk2"]}) == 9


def test_s20_mk2_originals_are_a_subset_of_greedy(derived):
    """The 9 orbits are a subset of the 28, so the arms meet head-to-head."""
    g = {r["name"] for r in derived["greedy"]}
    s = {r["name"] for r in derived["s20_mk2"]}
    assert s < g


def test_every_original_canonicalizes_to_its_orbit(derived):
    """The join is real: aut_canon(original) == the orbit's representative."""
    from experiments.equivalence_classes.lib.autcanon import aut_canon
    seen = 0
    for rows in derived.values():
        for r in rows:
            assert aut_canon((r["r1"], r["r2"]))[1] == (r["rep_r1"], r["rep_r2"]), r
            seen += 1
    assert seen == 58


def test_originals_are_not_their_representatives(derived):
    """If a row already equalled its rep there would be nothing to test."""
    differ = sum(1 for rows in derived.values() for r in rows
                 if (r["r1"], r["r2"]) != (r["rep_r1"], r["rep_r2"]))
    assert differ == 58


def test_orbits_are_exactly_the_unsolved_at_10m():
    for arm in ("greedy", "s20_mk2"):
        from experiments.search.run_leftovers_1m import read_rows
        recs = read_rows(mk.JSONL_10M[arm])
        assert sorted(r["name"] for r in recs if not r["solved"]) \
            == mk.unsolved_orbits(arm)


def test_campaign_entry():
    c = CAMPAIGNS["ac19_orig_10m"]
    ten = CAMPAIGNS["ac19_10m"]
    assert c["budget"] == 10_000_000
    # The control is the ac19_10m record on the representative; a different
    # cap would compare two different searches.
    assert c["mrl"] == ten["mrl"] == 64
    # No floor: these rows have never been searched by this arm, so an early
    # solve is the result rather than a wrong-search alarm.
    assert c["floor"] is None and c["floor_mrl"] is None
    assert c["track_path"] is True
    assert c["states_per_node"] == ten["states_per_node"]
    # Must never write over the representatives' campaign.
    assert c["prefix"] != ten["prefix"] and c["ids_stem"] != ten["ids_stem"]


def test_rows_load_through_the_campaign():
    for arm, n in (("greedy", 40), ("s20_mk2", 18)):
        rows, path = load_rows_5m(arm, campaign="ac19_orig_10m")
        assert len(rows) == n
        assert os.path.basename(path) == mk.OUT_CSV[arm]
        assert all(set(r["r1"] + r["r2"]) <= set("xXyY") for r in rows)


def test_relator_lengths_are_within_the_cap(derived):
    """Truett's constraint: length must never be why a row is dropped."""
    cap = CAMPAIGNS["ac19_orig_10m"]["mrl"]
    for rows in derived.values():
        for r in rows:
            assert max(len(r["r1"]), len(r["r2"])) <= cap, r


def test_the_greedy_path_does_no_basis_work():
    """The experiment is void if the arm normalizes its own input."""
    banned = ("aut_canon", "reduce_basis", "basis_moves", "canon_pair",
              "bs_collapse")
    targets = [os.path.join(ROOT, "experiments", "search", f) for f in
               ("greedy_compact.py", "greedy_baseline.py", "run_leftovers_5m.py")]
    core = os.path.join(ROOT, "experiments", "heuristic_search", "core")
    for base, _, files in os.walk(core):
        targets += [os.path.join(base, f) for f in files if f.endswith(".py")]
    for path in targets:
        if not os.path.exists(path):
            continue
        text = open(path).read()
        for token in banned:
            assert token not in text, f"{path} mentions {token}"
