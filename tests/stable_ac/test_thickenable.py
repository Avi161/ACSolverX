"""Tests for the [unverified] Neuwirth thickenability PROTOTYPE.

These pin the *construction* (link graph corners, genus arithmetic) exactly, and
assert the ground-truth calibration verdicts and the degenerate-length handling.
They do NOT and cannot certify the verdicts topologically -- that is Regina's job
(Pipeline B, not built) -- they only lock the reconstructed criterion in place so
a later change is caught.

Run:
    .venv/bin/python3 -m pytest tests/stable_ac/test_thickenable.py -q
"""

import itertools

import pytest

from experiments.stable_ac.thickenable import calibration as C
from experiments.stable_ac.thickenable.check_thickenable import (
    LinkGraph,
    Presentation,
    _genus_of_rotation,
    build_link_graph,
    check_strings,
    cyclic_reduce,
    is_open_problem,
    parse_word,
    word_to_str,
)


# ---------------------------------------------------------------------------
# word encoding + reduction
# ---------------------------------------------------------------------------
def test_parse_and_str_roundtrip():
    assert parse_word("YXXyxYx") == [-2, -1, -1, 2, 1, -2, 1]
    assert word_to_str([-2, -1, -1, 2, 1, -2, 1]) == "YXXyxYx"


def test_cyclic_reduce():
    assert cyclic_reduce(parse_word("xXy")) == parse_word("y")       # free cancel
    assert cyclic_reduce(parse_word("xyX")) == parse_word("y")       # cyclic ends
    assert cyclic_reduce(parse_word("xyXY")) == parse_word("xyXY")   # already reduced


# ---------------------------------------------------------------------------
# link-graph construction, pinned on a HAND-COMPUTED example.
#
#   Presentation:  <x, y | r = xyXY>  (the commutator [x, y]).
#   Encoding:      x=+1  X=-1  y=+2  Y=-2.
#   Corner rule:   corner(a_i, a_{i+1}) = edge{ -a_i , a_{i+1} }  (arrive germ of
#                  a_i  <->  depart germ of a_{i+1}), read cyclically:
#       (x,y): {-x,y} = {X, y} = {-1, +2}
#       (y,X): {-y,X} = {Y, X} = {-2, -1}
#       (X,Y): {-X,Y} = {x, Y} = {+1, -2}
#       (Y,x): {-Y,x} = {y, x} = {+2, +1}      (cyclic wrap)
#   => L is the 4-cycle   +x -- -y -- -x -- +y -- +x   (every germ has degree 2).
# ---------------------------------------------------------------------------
def _corner_set(lg: LinkGraph):
    return sorted(tuple(sorted((lg.dart_vertex[2 * k], lg.dart_vertex[2 * k + 1])))
                  for k in range(lg.n_corners))


def test_link_graph_commutator_handcomputed():
    lg = build_link_graph(Presentation.from_strings("xyXY"))
    assert lg.n_corners == 4
    assert _corner_set(lg) == [(-2, -1), (-2, 1), (-1, 2), (1, 2)]
    # 4 germ vertices, each degree 2 (a 4-cycle)
    assert sorted(lg.vertices) == [-2, -1, 1, 2]
    assert {v: len(lg.vert_darts[v]) for v in lg.vertices} == {1: 2, -1: 2, 2: 2, -2: 2}


def test_link_graph_edge_count_equals_total_length():
    # one corner per letter of each cyclically-reduced relator
    lg = build_link_graph(Presentation.from_strings("xxxYYYY", "xyxYXY"))
    assert lg.n_corners == 7 + 6


def test_link_graph_no_self_loops_after_cyclic_reduction():
    # dunce-hat word aaA cyclically reduces to a single letter -> no ill corners
    lg = build_link_graph(Presentation.from_strings("xxX"))
    for k in range(lg.n_corners):
        assert lg.dart_vertex[2 * k] != lg.dart_vertex[2 * k + 1]


# ---------------------------------------------------------------------------
# genus arithmetic of the rotation-system surface, on the theta graph
# (2 vertices, 3 parallel edges): a planar rotation gives genus 0, a twisted one
# gives genus 1 -- both must be reachable, proving V-E+F is computed correctly.
# ---------------------------------------------------------------------------
def test_genus_engine_theta_graph():
    lg = LinkGraph(3, [1, -1, 1, -1, 1, -1], {1: [0, 2, 4], -1: [1, 3, 5]}, {}, [1, -1])
    genera = set()
    for a in itertools.permutations([0, 2, 4]):
        for b in itertools.permutations([1, 3, 5]):
            genera.add(_genus_of_rotation(lg, {1: list(a), -1: list(b)}, 1))
    assert min(genera) == 0   # planar embedding exists
    assert max(genera) == 1   # a rotation of genus 1 exists (the surface arith works)


# ---------------------------------------------------------------------------
# calibration: ground-truth cases (see calibration.py for sources)
# ---------------------------------------------------------------------------
def test_calibration_all_pass():
    rows = C.run_calibration()
    for case, verdict, ok in rows:
        assert ok, f"{case.label}: expected thickenable={case.expected}, got {verdict.status}"


def test_calibration_specific_verdicts():
    got = {c.label: v.status for c, v, _ in C.run_calibration()}
    assert got["std <x,y|x,y>"] == "TRIVIAL_COLLAPSE"
    assert got["commutator <x,y|[x,y]>"] == "THICKENABLE"
    assert got["trefoil spine <x,y|xyx=yxy>"] == "THICKENABLE"
    assert got["RP^2 <x|x^2>"] == "THICKENABLE"
    assert got["K3,3-link <x,y,z|XXYXZYYZZ>"] == "NOT_THICKENABLE"


def test_checker_is_discriminating():
    # it must produce BOTH verdicts, else it is a constant function and useless
    statuses = {v.status for _, v, _ in C.run_calibration()}
    assert "THICKENABLE" in statuses
    assert "NOT_THICKENABLE" in statuses


# ---------------------------------------------------------------------------
# degenerate-length handling (Lackenby Lemma 3.1 pre-collapse)
# ---------------------------------------------------------------------------
def test_len1_relators_collapse_to_ball():
    assert check_strings("x", "y").status == "TRIVIAL_COLLAPSE"
    assert check_strings("x", None).status == "TRIVIAL_COLLAPSE"     # <x|x>


def test_len2_relator_eliminates_a_generator():
    # <x,y | xY, xyx>: the len-2 relator xY sets x=y, then r2 -> yyy (len 3)
    v = check_strings("xY", "xyx")
    assert v.status in {"THICKENABLE", "NOT_THICKENABLE"}
    assert "len2" in v.precollapse_note


def test_redundant_empty_relator_is_degenerate_not_trivial():
    # <x,y|xy,xy> is really <y>=Z (a free factor), NOT the trivial group
    v = check_strings("xy", "xy")
    assert v.status == "DEGENERATE"
    assert v.thickenable is None


# ---------------------------------------------------------------------------
# negative side (>=3-gen, non-planar link) -- solid ground truth
# ---------------------------------------------------------------------------
def test_negative_k33_non_planar_link():
    v = check_strings("XXYXZYYZZ", None, name="K3,3")   # Whitehead graph = K3,3
    assert v.status == "NOT_THICKENABLE"
    assert v.thickenable is False


# ---------------------------------------------------------------------------
# targets + the open-problem SUSPECTED-BUG guard
# ---------------------------------------------------------------------------
def test_ak3_is_open_and_not_thickenable():
    pres = Presentation.from_strings("xxxYYYY", "xyxYXY", name="AK(3)")
    assert is_open_problem(pres)
    v = check_strings("xxxYYYY", "xyxYXY", name="AK(3)", mark_open=True)
    # a NEGATIVE is the safe/expected outcome here (settles nothing)
    assert v.status == "NOT_THICKENABLE"
    assert v.rotation_cost <= 2_000_000   # AK(3) at total length 13 is tractable


def test_ak3_orbit2_is_open():
    pres = Presentation.from_strings("YYXXyx", "YYYxyXX")
    assert is_open_problem(pres)


def test_positive_on_open_problem_emits_suspected_bug_warning():
    # force the guard: mark the (thickenable) commutator as an open target.
    v = check_strings("xyXY", None, name="fake-open", mark_open=True)
    assert v.thickenable is True
    assert v.warnings, "a THICKENABLE on an open-marked input MUST warn"
    assert any("SUSPECTED BUG" in w for w in v.warnings)


# ---------------------------------------------------------------------------
# size limit: a big search returns UNKNOWN_SIZE, never a false NOT_THICKENABLE
# ---------------------------------------------------------------------------
def test_size_cap_returns_unknown_not_no():
    v = check_strings("xxxYYYY", "xyxYXY", name="AK(3)", max_rotations=100)
    assert v.status == "UNKNOWN_SIZE"
    assert v.thickenable is None   # explicitly NOT False


def test_floor_reps_load_and_run():
    reps = C.load_floor_reps()
    assert len(reps) == 35
    # run one small check to make sure the target path executes
    name, r1, r2 = reps[0]
    v = check_strings(r1, r2, name=name, max_rotations=1000, mark_open=True)
    assert v.status in {"NOT_THICKENABLE", "THICKENABLE", "UNKNOWN_SIZE", "DEGENERATE"}
