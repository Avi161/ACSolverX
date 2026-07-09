"""Forward compatibility: stable AC moves (AC4/AC5) and the general S-move.

These tests run **today**, against the spec, at ``n_gen`` up to 4. They are the
acceptance criteria for the stable-AC solver, not placeholders waiting for it.

Scope. AC4/AC5 are presentation operations and are tested as such. The general
``(i, j, s, k1, k2)`` substitution is tested at three relators, where the source
index ``j`` becomes real. The full *change of variables* procedure
(stabilize -> substitute -> isolate -> Lemma-11 removal) is **not** reimplemented:
its "isolate" step needs AC1-3 conjugation and its Lemma-11 step is proved with
an unbounded number of substitutions, so it is research work, not a test. What
is covered is the mechanism it is built from -- that AC4, the general S-move, and
AC5 each preserve the invariants -- which is what a solver using it must respect.

AK(3) and the MMS02 instance appear only as structural fixtures. Their
AC-triviality is open; asserting that the search solves them would be asserting
an open conjecture, and a pass would be luck rather than evidence.
"""

import pytest

from experiments.greedy_tests.adapters import SPEC
from experiments.greedy_tests.fixtures.presentations import MMS02_LEN14, ak, ms640
from experiments.greedy_tests.spec import search as spec_search
from experiments.greedy_tests.spec.invariants import (
    abs_det, exponent_sum_matrix, is_perfect_abelianization,
)
from experiments.greedy_tests.spec.moves import (
    Move, apply_move, enumerate_moves, neighbours, seam_cancels,
)
from experiments.greedy_tests.spec.presentation import Presentation, trivial
from experiments.greedy_tests.spec.words import reduce_word

pytestmark = pytest.mark.stable

BASE = [ms640([0])[0], ms640([5])[0], ak(3), MMS02_LEN14]


# -- AC4 / AC5 ---------------------------------------------------------------


@pytest.mark.parametrize("pres", BASE, ids=lambda p: "".join(p.to_strs())[:12])
def test_ac4_adds_one_generator_and_the_trivial_relator(pres):
    s = pres.stabilize()
    assert s.n_gen == pres.n_gen + 1
    assert s.n_rel == pres.n_rel + 1
    assert s.relators[:-1] == pres.relators
    assert s.relators[-1] == (pres.n_gen + 1,)
    assert s.is_balanced


@pytest.mark.parametrize("pres", BASE, ids=lambda p: "".join(p.to_strs())[:12])
def test_ac5_inverts_ac4(pres):
    assert pres.stabilize().destabilize() == pres


def test_ac5_refuses_when_the_generator_is_still_in_use():
    p = Presentation(3, ((1, 3), (2,), (3,)))
    with pytest.raises(ValueError, match="still occurs"):
        p.destabilize()


def test_ac5_refuses_without_a_trivial_relator():
    with pytest.raises(ValueError, match="no trivial relator"):
        Presentation(2, ((1, 2), (2, 1))).destabilize()


def test_repeated_stabilization_reaches_four_generators():
    p = ms640([0])[0].stabilize().stabilize()
    assert (p.n_gen, p.n_rel) == (4, 4)
    assert abs_det(p) == 1
    assert p.relators[-2:] == ((3,), (4,))


def test_the_trivial_presentation_after_stabilization_is_x_y_z():
    assert trivial(2).stabilize() == trivial(3)
    assert trivial(3).stabilize() == trivial(4)


@pytest.mark.parametrize("n", [2, 3, 4])
def test_the_trivial_presentation_is_recognised_at_any_n_gen(n):
    t = trivial(n)
    assert t.is_trivial()
    assert t.all_relators_are_single_letters()
    assert abs_det(t) == 1


def test_single_letter_relators_are_not_sufficient_for_triviality():
    """``<x,y | x, x>`` passes the solver's test but presents Z, not 1.

    The solver's ``len(r1) == 1 and len(r2) == 1`` is sound only because AC moves
    preserve the presented group, so this state is unreachable from a trivial
    presentation. A stable solver must keep that argument intact.
    """
    degenerate = Presentation(2, ((1,), (1,)))
    assert degenerate.all_relators_are_single_letters()
    assert not degenerate.is_trivial()
    assert abs_det(degenerate) == 0        # unreachable: abs(det) is preserved at 1


# -- the general S-move ------------------------------------------------------


def test_at_two_relators_the_source_index_is_forced():
    p = ms640([0])[0]
    for mv in enumerate_moves(p):
        assert {mv.i, mv.j} == {0, 1}


def test_at_three_relators_the_move_carries_a_real_source_index():
    """``r_{3-i}`` of Definition 2.1 has no meaning here: ``j`` must be enumerated.

    A presentation whose three relators genuinely interact, so that more than the
    two ``{0,1}`` pairings survive the seam condition.
    """
    p = Presentation(3, ((1, 2), (-2, 3), (-3, -1)))
    sources = {(mv.i, mv.j) for mv in enumerate_moves(p)}
    for i, j in sources:
        assert i != j and 0 <= i < 3 and 0 <= j < 3
    assert len(sources) > 2, sources
    assert any(j == 2 for _, j in sources), "the third relator must be usable as a source"
    assert any(i == 2 for i, _ in sources), "...and as a target"


def test_a_disconnected_trivial_relator_supplies_no_moves():
    """After AC4 the new ``z`` shares no letter with the old relators, so no seam cancels.

    This is why stabilization alone does not change the search: ``z`` sits inert
    until a change of variables injects it into another relator.
    """
    p = ms640([0])[0].stabilize()
    sources = {(mv.i, mv.j) for mv in enumerate_moves(p)}
    assert sources == {(0, 1), (1, 0)}


def test_the_general_move_applies_to_the_target_and_reads_the_source():
    p = Presentation(3, ((1, 2), (-2, 1), (3,)))
    mv = Move(i=0, j=1, s=1, k1=0, k2=0)
    assert seam_cancels(p.relators, mv)
    out = apply_move(p.relators, mv)
    assert out[0] == (1, 2, -2, 1)
    assert out[1] == p.relators[1] and out[2] == p.relators[2]
    assert reduce_word(out[0]) == (1, 1)


@pytest.mark.parametrize("n_gen", [2, 3, 4])
def test_every_general_neighbour_preserves_abs_det(n_gen):
    p = ms640([0])[0]
    for _ in range(n_gen - 2):
        p = p.stabilize()
    d = abs_det(p)
    children = neighbours(p, cap=24, cyclic=True)
    assert children, "the fixture must actually generate neighbours"
    for child, _ in children:
        assert child.n_gen == n_gen and child.n_rel == n_gen
        assert abs_det(child) == d


def test_stabilization_preserves_both_invariants():
    for p in BASE:
        s = p.stabilize()
        assert abs_det(s) == abs_det(p)
        assert is_perfect_abelianization(s) == is_perfect_abelianization(p)
        m = exponent_sum_matrix(s)
        assert m[-1] == [0] * p.n_gen + [1]          # the bordered unit row
        assert all(row[-1] == 0 for row in m[:-1])   # ...and unit column


# -- the change-of-variables mechanism ---------------------------------------


def test_ac4_then_general_move_then_ac5_is_invariant_preserving():
    """The skeleton of change of variables: grow, substitute, shrink.

    Not the full procedure -- the isolate step needs AC1-3 conjugation and
    Lemma 11's removal is proved with an unbounded number of substitutions.
    What a solver built on it must preserve is exactly this.
    """
    p = ms640([0])[0]
    d = abs_det(p)

    grown = p.stabilize()
    assert abs_det(grown) == d

    child, mv = neighbours(grown, cap=24, cyclic=True)[0]
    assert abs_det(child) == d
    assert child.n_gen == 3

    back = trivial(3).destabilize()
    assert back == trivial(2) and abs_det(back) == d


# -- the spec solver at three generators -------------------------------------


@pytest.mark.parametrize("idx", [0, 5, 12])
def test_a_stabilized_solvable_presentation_still_solves(idx):
    """AC4 must not make an easy presentation harder: ``z`` is already a single letter."""
    p = ms640([idx])[0]
    plain = spec_search.search(p, 1000)
    stabilized = spec_search.search(p.stabilize(), 1000)
    assert plain["solved"] and stabilized["solved"]
    assert stabilized["nodes_explored"] == plain["nodes_explored"]
    assert spec_search.replay(p.stabilize(), stabilized["path_moves"])[-1].is_trivial()


def test_the_spec_adapter_solves_at_three_generators():
    s = SPEC.search(ms640([0])[0].stabilize(), 1000, cap=24, cyclic=True)
    assert s.solved
    assert s.path_states[-1].n_gen == 3
    assert s.path_states[-1].is_trivial()


@pytest.mark.parametrize("pres", [ak(3), ak(3).stabilize(), MMS02_LEN14],
                         ids=["AK(3)", "AK(3)-stabilized", "MMS02"])
def test_open_presentations_respect_the_budget_without_crashing(pres):
    """Deliberately asserts nothing about solvability -- that question is open."""
    s = spec_search.search(pres, 200, cap=16)
    assert 1 <= s["nodes_explored"] <= 200
    assert abs_det(pres) == 1
