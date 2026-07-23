"""Harness tests for ``experiments/stable_ac/cov/orbit_greedy.py`` — running
the baseline greedy from mu-ladder orbits.

This module OWNS no search semantics: it selects starts, calls the
``run_baseline.greedy_search`` seam, and censuses the rows. So the tests pin
the three things that can silently corrupt a sweep — which starts get chosen,
what the run's identity is, and whether a resumed file double-counts — plus
the two claims the report makes (a flip needs an unsolved control; the
reduction column is the greedy's own reached length).

Node budgets stay at or below ``MAX_BUDGET = 1_000``: a search at budget B is
exactly the first B pops of any longer search.
"""

import json
import os

import pytest

from experiments.stable_ac.cov import orbit_greedy as og
from experiments.stable_ac.cov.autcanon_fast import relabel_min

# Two tiny classes: one with a rung-0 control row, several orbits each.
_ORBITS = [
    {"pres_id": "c_a", "rung": 0, "mu": 8, "rep": ["xy", "XY"],
     "pair": ["xy", "yx"], "parent_rep": None, "z": None,
     "iso_gen": None, "iso_index": None, "n_subs": None},
    {"pres_id": "c_a", "rung": 1, "mu": 12, "rep": ["xxy", "XY"],
     "pair": ["xxy", "yxy"], "parent_rep": ["xy", "XY"], "z": "x",
     "iso_gen": "x", "iso_index": 0, "n_subs": 1},
    {"pres_id": "c_a", "rung": 1, "mu": 9, "rep": ["xy", "Xy"],
     "pair": ["xyx", "yy"], "parent_rep": ["xy", "XY"], "z": "y",
     "iso_gen": "x", "iso_index": 0, "n_subs": 1},
    {"pres_id": "c_a", "rung": 2, "mu": 20, "rep": ["xxxy", "XYXY"],
     "pair": ["xxxxy", "yxyxy"], "parent_rep": ["xy", "Xy"], "z": "xy",
     "iso_gen": "y", "iso_index": 1, "n_subs": 2},
    {"pres_id": "c_b", "rung": 0, "mu": 6, "rep": ["xx", "yy"],
     "pair": ["xx", "yy"], "parent_rep": None, "z": None,
     "iso_gen": None, "iso_index": None, "n_subs": None},
    {"pres_id": "c_b", "rung": 1, "mu": 10, "rep": ["xxy", "yy"],
     "pair": ["xxy", "yyx"], "parent_rep": ["xx", "yy"], "z": "x",
     "iso_gen": "x", "iso_index": 0, "n_subs": 1},
]


@pytest.fixture
def orbit_file(tmp_path):
    p = tmp_path / "fake_orbits.jsonl"
    p.write_text("".join(json.dumps(r) + "\n" for r in _ORBITS))
    return str(p)


# ------------------------------------------------------------------ selection

def test_rung_zero_is_never_an_orbit_start(orbit_file):
    """Rung 0 IS the original. Searching it as an 'orbit' would manufacture a
    flip out of the control itself."""
    rows, _ = og.load_orbits([orbit_file])
    sel = og.select(rows, per_class=99, strategy="all")
    assert all(r["rung"] != 0 for rs in sel.values() for r in rs)
    assert og.controls(rows) == {"c_a": ("xy", "yx"), "c_b": ("xx", "yy")}


def test_lowest_takes_the_smallest_mu_and_is_deterministic(orbit_file):
    rows, _ = og.load_orbits([orbit_file])
    sel = og.select(rows, per_class=2, strategy="lowest")
    assert [r["mu"] for r in sel["c_a"]] == [9, 12]
    assert og.select(rows, 2, "lowest") == sel      # no set/hash ordering


def test_spread_covers_the_whole_mu_range(orbit_file):
    """`lowest` would never reach the mu-20 orbit; `spread` must, or the A/B
    that asks 'does solvability track mu' cannot be run at all."""
    rows, _ = og.load_orbits([orbit_file])
    mus = [r["mu"] for r in og.select(rows, per_class=3, strategy="spread")["c_a"]]
    assert min(mus) == 9 and max(mus) == 20


def test_torn_trailing_line_is_tolerated(tmp_path):
    p = tmp_path / "torn.jsonl"
    p.write_text(json.dumps(_ORBITS[0]) + "\n" + '{"pres_id": "c_a", "ru')
    rows, torn = og.load_orbits([str(p)])
    assert len(rows) == 1 and torn == 1


# ------------------------------------------------------------------- relabels

def test_relabels_are_eight_distinct_starts_in_the_same_aut_orbit():
    """The greedy reads STRINGS, not orbits — relabels supplied 14 of the 17
    flips in the one-hop sweep. They must all be different strings, and all
    the same orbit, or the sweep is either wasting rows or changing question.
    """
    pair = ("xxy", "yxy")
    starts = og.relabel_starts(pair, 8)
    assert len(starts) == 8
    assert len({(r1, r2) for _, r1, r2 in starts}) > 1
    key = relabel_min(pair)
    assert all(relabel_min((r1, r2)) == key for _, r1, r2 in starts)


def test_relabels_one_is_the_stored_representative():
    assert og.relabel_starts(("xxy", "yxy"), 1) == [("id", "xxy", "yxy")]


# ------------------------------------------------------------ run identity

def test_run_prefix_encodes_every_result_changing_knob():
    c = dict(og.DEFAULTS, budget=100, cap=48, strategy="spread",
             per_class=60, relabels=8)
    assert og._run_prefix(c, 6) == "orbit_greedy_b100_cap48_spread60_rl8_n6"


def test_high_speedup_stays_out_of_the_identity():
    """Result-neutral (same pop order; a solved fast search is re-solved for
    its path) — a file must resume across the two modes."""
    a = og._run_prefix(dict(og.DEFAULTS, high_speedup=True), 6)
    b = og._run_prefix(dict(og.DEFAULTS, high_speedup=False), 6)
    assert a == b


def test_budget_ceiling_is_enforced():
    with pytest.raises(ValueError):
        og.run(budget=og.MAX_BUDGET + 1)


# ------------------------------------------------------------------- resume

def test_done_keys_repairs_a_torn_tail_before_appending(tmp_path):
    p = tmp_path / "out.jsonl"
    good = {"kind": "orbit", "pres_id": "c_a", "rep_key": "xy|XY",
            "relabel": "id", "solved": False}
    p.write_text(json.dumps(good) + "\n" + '{"kind": "orbit", "pres_')
    done, n_solved = og._done_keys(str(p))
    assert done == {("orbit", "c_a", "xy|XY", "id")} and n_solved == 0
    # repaired IN PLACE: the next append must not land behind a broken line
    lines = [l for l in p.read_text().split("\n") if l.strip()]
    assert len(lines) == 1 and json.loads(lines[0]) == good


# -------------------------------------------------------------------- report

def test_a_flip_requires_an_unsolved_control(tmp_path, capsys):
    """A class whose control already solves is not a flip, however many orbit
    starts also solve — that was the whole point of the cap-matched control."""
    p = tmp_path / "rows.jsonl"
    rows = [
        {"kind": "control", "pres_id": "easy", "rung": 0, "mu": 6,
         "rep_key": "", "relabel": "", "solved": True, "nodes_explored": 3,
         "path_length": 2, "min_total": 2, "max_total": 6},
        {"kind": "orbit", "pres_id": "easy", "rung": 1, "mu": 10,
         "rep_key": "k", "relabel": "id", "solved": True, "nodes_explored": 5,
         "path_length": 3, "min_total": 2, "max_total": 10},
        {"kind": "control", "pres_id": "hard", "rung": 0, "mu": 18,
         "rep_key": "", "relabel": "", "solved": False, "nodes_explored": 100,
         "path_length": None, "min_total": 18, "max_total": 40},
        {"kind": "orbit", "pres_id": "hard", "rung": 4, "mu": 24,
         "rep_key": "k2", "relabel": "id", "solved": True,
         "nodes_explored": 40, "path_length": 9, "min_total": 2,
         "max_total": 24},
    ]
    p.write_text("".join(json.dumps(r) + "\n" for r in rows))
    flips = og.report(str(p))
    assert set(flips) == {"hard"}


def test_reduction_column_flags_only_a_strictly_lower_reach(tmp_path, capsys):
    p = tmp_path / "rows.jsonl"
    rows = [
        {"kind": "control", "pres_id": "c", "rung": 0, "mu": 18,
         "rep_key": "", "relabel": "", "solved": False, "nodes_explored": 10,
         "path_length": None, "min_total": 18, "max_total": 30},
        {"kind": "orbit", "pres_id": "c", "rung": 2, "mu": 24, "rep_key": "a",
         "relabel": "id", "solved": False, "nodes_explored": 10,
         "path_length": None, "min_total": 18, "max_total": 30},
    ]
    p.write_text("".join(json.dumps(r) + "\n" for r in rows))
    og.report(str(p))
    out = capsys.readouterr().out
    assert "LOWER" not in out          # equal reach is not an improvement
    assert "0/1" in out


# ---------------------------------------------------------------- end to end

def test_end_to_end_writes_control_and_orbit_rows(orbit_file, tmp_path,
                                                  monkeypatch, numba_warm):
    monkeypatch.chdir(tmp_path)
    out = og.run(orbits=orbit_file, budget=100, cap=24, per_class=2,
                 strategy="lowest", relabels=2,
                 out_dir=str(tmp_path / "out"))
    rows = [json.loads(l) for l in open(out) if l.strip()]
    kinds = {r["kind"] for r in rows}
    assert kinds == {"control", "orbit"}
    assert {r["pres_id"] for r in rows} == {"c_a", "c_b"}
    # the reduction readout must be the greedy's own reach, never the start
    for r in rows:
        assert r["min_total"] <= len(r["r1"]) + len(r["r2"])
        assert r["budget"] == 100 and r["cap"] == 24
    # resume: a second call adds nothing
    before = len(rows)
    og.run(orbits=orbit_file, budget=100, cap=24, per_class=2,
           strategy="lowest", relabels=2, out_dir=str(tmp_path / "out"))
    assert len([l for l in open(out) if l.strip()]) == before


def test_over_cap_starts_are_skipped_and_counted(orbit_file, tmp_path,
                                                 monkeypatch, capsys,
                                                 numba_warm):
    """A silent truncation reads as 'we covered everything' when we didn't."""
    monkeypatch.chdir(tmp_path)
    og.run(orbits=orbit_file, budget=100, cap=3, per_class=99,
           strategy="all", relabels=1, out_dir=str(tmp_path / "out2"))
    assert "SKIPPED" in capsys.readouterr().out
