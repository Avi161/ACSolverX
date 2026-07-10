"""The contract every solver must satisfy, for every presentation it supports.

This module is the reason the suite survives the stable-AC port. It never names
``greedy_search``; it iterates ``adapters.ALL_ADAPTERS`` and skips what an
adapter declares unsupported. Adding a solver that handles three generators
means writing one adapter and appending it to that list -- these tests then run
against it, at ``n_gen = 3``, unchanged.

What is asserted here holds for *any* correct best-first AC search. What is
**not** asserted is anything about the trace: a different solver may explore a
different number of nodes and still be correct. Trace equality is a property of
the normal/heavy pair alone (``test_solver_parity.py``).
"""

import pytest

from experiments.greedy_tests.adapters import ALL_ADAPTERS, replay_moves
from experiments.greedy_tests.fixtures.presentations import (
    MMS02_LEN14, ak, ms640, ms_unsolved,
)
from experiments.greedy_tests.spec.invariants import abs_det
from experiments.greedy_tests.spec.moves import seam_cancels
from experiments.greedy_tests.spec.presentation import trivial

#: (presentation, budget, id). Mixes solvable, budget-capped and stabilized cases.
CASES = [
    (ms640([0])[0], 500, "ms640-0-solvable"),
    (ms640([5])[0], 500, "ms640-5-solvable"),
    (ms_unsolved([0])[0], 300, "unsolved-rep-0"),
    (ak(3), 300, "AK(3)"),
    (MMS02_LEN14, 300, "MMS02-len14"),
    (trivial(2), 10, "trivial-2gen"),
    # Forward-compat: only the spec adapter supports these today.
    (trivial(3), 10, "trivial-3gen"),
    (ms640([0])[0].stabilize(), 500, "ms640-0-stabilized"),
    (ak(3).stabilize(), 300, "AK(3)-stabilized"),
]

ADAPTER_IDS = [a.name for a in ALL_ADAPTERS]


def _run(adapter, pres, budget):
    if not adapter.supports(pres):
        pytest.skip(f"{adapter.name} does not support "
                    f"n_gen={pres.n_gen}, n_rel={pres.n_rel}")
    return adapter.search(pres, budget, cap=24, cyclic=True)


@pytest.fixture(params=ALL_ADAPTERS, ids=ADAPTER_IDS)
def adapter(request):
    return request.param


@pytest.mark.parametrize("pres,budget,_id", CASES, ids=[c[2] for c in CASES])
def test_budget_is_respected(adapter, pres, budget, _id):
    s = _run(adapter, pres, budget)
    assert 1 <= s.nodes_explored <= budget


@pytest.mark.parametrize("pres,budget,_id", CASES, ids=[c[2] for c in CASES])
def test_search_is_deterministic(adapter, pres, budget, _id):
    a = _run(adapter, pres, budget)
    b = _run(adapter, pres, budget)
    assert (a.solved, a.nodes_explored, a.path_length) == \
           (b.solved, b.nodes_explored, b.path_length)
    assert (a.min_total, a.max_total, a.max_expanded_total) == \
           (b.min_total, b.max_total, b.max_expanded_total)


@pytest.mark.parametrize("pres,budget,_id", CASES, ids=[c[2] for c in CASES])
def test_length_statistics_are_ordered(adapter, pres, budget, _id):
    s = _run(adapter, pres, budget)
    assert s.min_total <= s.max_total
    assert s.max_expanded_total <= s.max_total
    assert s.min_total == sum(len(r) for r in s.min_relators)
    assert s.max_total == sum(len(r) for r in s.max_relators)
    assert s.max_expanded_total == sum(len(r) for r in s.max_expanded_relators)


@pytest.mark.parametrize("pres,budget,_id", CASES, ids=[c[2] for c in CASES])
def test_an_unsolved_run_reports_no_path(adapter, pres, budget, _id):
    s = _run(adapter, pres, budget)
    if s.solved:
        pytest.skip("this case solves")
    assert s.path_length is None
    assert s.path_moves == ()


@pytest.mark.parametrize("pres,budget,_id", CASES, ids=[c[2] for c in CASES])
def test_a_solved_run_ends_on_single_letter_relators(adapter, pres, budget, _id):
    s = _run(adapter, pres, budget)
    if not s.solved:
        pytest.skip("this case does not solve within budget")
    if not adapter.yields_path:
        assert s.path_moves == () and s.path_length is not None
        pytest.skip(f"{adapter.name} does not reconstruct paths by design")
    final = s.path_states[-1]
    assert final.all_relators_are_single_letters()
    assert final.is_trivial()


@pytest.mark.parametrize("pres,budget,_id", CASES, ids=[c[2] for c in CASES])
def test_a_solved_path_replays_from_the_start_presentation(adapter, pres, budget, _id):
    s = _run(adapter, pres, budget)
    if not s.solved or not adapter.yields_path:
        pytest.skip("no path to replay")
    replayed = replay_moves(pres, s.path_moves)
    assert len(replayed) == s.path_length + 1
    assert [p.relators for p in replayed] == [p.relators for p in s.path_states]
    assert replayed[-1].is_trivial()


@pytest.mark.parametrize("pres,budget,_id", CASES, ids=[c[2] for c in CASES])
def test_every_path_step_is_a_valid_move_and_preserves_abs_det(adapter, pres, budget, _id):
    s = _run(adapter, pres, budget)
    if not s.solved or not adapter.yields_path:
        pytest.skip("no path to check")
    d = abs_det(pres)
    for state, mv in zip(s.path_states, s.path_moves):
        assert seam_cancels(state.relators, mv)
        assert abs_det(state) == d
    assert abs_det(s.path_states[-1]) == d == 1


@pytest.mark.parametrize("pres,budget,_id", CASES, ids=[c[2] for c in CASES])
def test_progress_callback_does_not_change_the_result(adapter, pres, budget, _id):
    quiet = _run(adapter, pres, budget)
    seen = []
    if not adapter.supports(pres):
        pytest.skip("unsupported")
    loud = adapter.search(pres, budget, cap=24, cyclic=True, progress=seen.append)
    assert (quiet.solved, quiet.nodes_explored, quiet.path_length) == \
           (loud.solved, loud.nodes_explored, loud.path_length)
    assert all(n % 1024 == 0 for n in seen)


def test_every_adapter_declares_support_honestly():
    """An adapter that claims a presentation must not raise on it."""
    for a in ALL_ADAPTERS:
        for pres, budget, _id in CASES:
            if a.supports(pres):
                a.search(pres, min(budget, 20), cap=24, cyclic=True)


def test_the_numba_adapters_are_two_generator_only_today():
    """When the stable solver lands, this test is the one that must be updated."""
    from experiments.greedy_tests.adapters import HEAVY, NORMAL, SPEC

    assert NORMAL.supports(trivial(2)) and HEAVY.supports(trivial(2))
    assert not NORMAL.supports(trivial(3))
    assert not HEAVY.supports(trivial(3))
    assert SPEC.supports(trivial(3)), "the spec must already cover n_gen=3"
