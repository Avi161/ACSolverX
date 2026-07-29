"""Word/move replay, Todd-Coxeter controls, and an end-to-end runner smoke test."""

from __future__ import annotations

import json
import os

import pytest

from experiments.stable_ac.fable import ac_words as W
from experiments.stable_ac.fable import coset_enum as CE
from experiments.stable_ac.fable import run_targets as RT

FIXTURE = os.path.join(RT.repo_root(), RT.DEFAULT_FIXTURE)


# =====================================================================================
# word algebra
# =====================================================================================


def test_free_and_cyclic_reduction():
    assert W.free_reduce("xXyY") == ""
    assert W.free_reduce("xyYX") == ""
    assert W.free_reduce("xxYyX") == "x"
    assert W.free_reduce("xyxYXY") == "xyxYXY"
    assert W.cyclic_reduce("YXXyxyy") == "XXyxy"
    assert W.cyclic_reduce("YYXXyxyyy") == "XXyxy"
    assert W.inverse("xyXY") == "yxYX"
    assert W.inverse(W.inverse("XYxYXyxYYxyXy")) == "XYxYXyxYYxyXy"
    assert W.is_cyclically_reduced("xxxYYYY")
    assert not W.is_cyclically_reduced("YXXyxyy")


def test_move_table_matches_the_latex_definitions():
    expected = {
        1: "r2 -> r2 r1",
        2: "r1 -> r1 r2^-1",
        3: "r2 -> r2 r1^-1",
        4: "r1 -> r1 r2",
        5: "r2 -> X r2 x",
        6: "r1 -> Y r1 y",
        7: "r2 -> Y r2 y",
        8: "r1 -> x r1 X",
        9: "r2 -> x r2 X",
        10: "r1 -> y r1 Y",
        11: "r2 -> y r2 Y",
        12: "r1 -> X r1 x",
    }
    assert {m: W.move_description(m) for m in W.MOVES} == expected
    assert W.MOVE_COUNT == 12


def test_relator_cap_makes_a_move_a_no_op():
    state = ("xxx", "yyy")
    assert W.apply_move(state, 4, cap=6) == ("xxxyyy", "yyy")
    assert W.apply_move(state, 4, cap=5) == state          # 6 > cap -> no-op
    # h8 conjugates r1 by x; on x^3 the seams cancel and nothing changes
    assert W.apply_move(state, 8, cap=3) == state
    assert W.apply_move(("xxy", "yyy"), 8, cap=5) == ("xxxyX", "yyy")
    assert W.apply_move(("xxy", "yyy"), 8, cap=4) == ("xxy", "yyy")   # 5 > cap


def test_children_are_twelve_in_move_order():
    state = ("xxxYYYY", "xyxYXY")
    kids = W.children(state, 15)
    assert len(kids) == 12
    assert kids == [W.apply_move(state, m, 15) for m in range(1, 13)]


# =====================================================================================
# the published 53-move path
# =====================================================================================


def test_path_replay_reaches_ak3_with_the_published_length_trace():
    result = RT.derive_path(FIXTURE)
    assert result["endpoint"] == ("xxxYYYY", "xyxYXY")
    assert tuple(result["trace"]) == RT.PUBLISHED_TRACE
    assert len(result["trace"]) == 53
    assert result["fixture_byte_identical"] is True
    assert result["non_cyclically_reduced_indices"] == (23, 24)


def test_path_states_match_the_committed_fixture_exactly():
    with open(FIXTURE, encoding="utf-8") as fh:
        fixture = json.load(fh)
    states = RT.derive_path(FIXTURE)["states"]
    assert [list(s) for s in states] == fixture["path"]
    assert [list(s) for s in sorted(set(states))] == fixture["unique"]
    assert len(set(states)) == 54


def test_every_path_transition_is_one_of_the_twelve_children():
    states = RT.derive_path(FIXTURE)["states"]
    for i, (prev, nxt) in enumerate(zip(states, states[1:])):
        kids = W.children(prev, RT.PATH_CAP)
        assert nxt in kids, i
        assert kids[RT.PATH_MOVES[i] - 1] == nxt, i


def test_canonical_form_agrees_with_the_repo_word_library():
    """canon_pair here is independent code; pin it against the repo implementation."""
    repo = pytest.importorskip("experiments.equivalence_classes.lib.words")
    states = RT.derive_path(FIXTURE)["states"]
    for state in states:
        assert W.canon_pair(*state) == repo.canon_pair(*state)
    assert W.canon_pair("xxxYYYY", "xyxYXY") == ("YXYxyx", "YYYYxxx")


# =====================================================================================
# Todd-Coxeter controls
# =====================================================================================


@pytest.mark.parametrize(
    "label,generators,relators,index",
    [
        ("A5", ("a", "b"), ("aaaaa", "bbb", "abab"), 60),
        ("S3", ("a", "b"), ("aa", "bbb", "abab"), 6),
        ("Z/5", ("a",), ("aaaaa",), 5),
        ("Z/2 x Z/2", ("a", "b"), ("aa", "bb", "abAB"), 4),
        ("S4", ("a", "b"), ("aa", "bbb", "abababab"), 24),
        ("trivial", ("a",), ("a",), 1),
        ("AK(2)", ("x", "y"), ("xxYYY", "xyxYXY"), 1),
        ("AK(3)", ("x", "y"), ("xxxYYYY", "xyxYXY"), 1),
        ("orbit-2", ("x", "y"), ("YYXXyx", "YYYxyXX"), 1),
    ],
)
def test_todd_coxeter_controls(label, generators, relators, index):
    result = CE.enumerate_cosets(generators, relators, cap=200_000)
    assert result["status"] == CE.COMPLETE, label
    assert result["index"] == index, label


def test_todd_coxeter_hits_the_cap_on_an_infinite_group():
    result = CE.enumerate_cosets(("x", "y"), ("y",), cap=2_000)
    assert result["status"] == CE.CAP_EXCEEDED
    assert result["index"] is None
    assert result["cosets_defined"] >= 2_000
    with pytest.raises(ValueError):
        CE.coset_index(("x", "y"), ("y",), cap=2_000)
    report = CE.is_trivial_group(("y",), cap=2_000)   # <x, y | y> = Z, infinite
    assert report["status"] == CE.CAP_EXCEEDED
    assert report["trivial"] is None          # undetermined, never guessed


def test_todd_coxeter_certifies_the_targets_trivial():
    for words in (RT.P25, RT.Q, RT.AK3):
        report = CE.is_trivial_group(words, cap=200_000)
        assert report["status"] == CE.COMPLETE
        assert report["trivial"] is True
        assert report["index"] == 1


def test_subgroup_index_control():
    # <a, b | a^5, b^3, (ab)^2> with H = <a> has index 12 in A5
    result = CE.enumerate_cosets(("a", "b"), ("aaaaa", "bbb", "abab"), ("a",),
                                 cap=200_000)
    assert result["status"] == CE.COMPLETE
    assert result["index"] == 12


# =====================================================================================
# runner smoke test
# =====================================================================================


def test_run_targets_quick_mode(tmp_path, capsys):
    output = tmp_path / "gamma_n_targets.jsonl"
    code = RT.main(["--quick", "--output", str(output),
                    "--component-json", str(tmp_path / "missing.json")])
    assert code == 0
    rows = [json.loads(line) for line in output.read_text().splitlines()]
    assert len(rows) == 58            # P25 + Q + 54 exact path states + 2 reduced
    verdicts = {}
    for row in rows:
        verdicts[row["verdict"]] = verdicts.get(row["verdict"], 0) + 1
    assert verdicts == {"NOT_SPHERICAL": 56, "UNSUPPORTED": 2}
    by_target = {(r["target"], r["role"]): r for r in rows}
    assert by_target[("P25", "exact")]["support"]["kind"] == "K4-e"
    assert by_target[("Q", "exact")]["support"]["kind"] == "K4"
    for i in (23, 24):
        assert by_target[(f"path[{i}]", "exact")]["verdict"] == "UNSUPPORTED"
        assert by_target[(f"path[{i}]", "cyclically_reduced")]["verdict"] == "NOT_SPHERICAL"
    out = capsys.readouterr().out
    assert "verdict table" in out
