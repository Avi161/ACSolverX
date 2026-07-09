"""Properties of a single search run: budget, determinism, paths, callbacks.

The path assertions are the important ones. A stored move is relative to the
*canonical parent*, so a path is validated by replaying it -- never by diffing
the stored states, which have been rotated, inverted and possibly swapped by
canonicalisation.
"""

import pytest

from experiments.search.greedy_baseline import (
    GreedyBaselineSolver, _HB_CHECK_EVERY, greedy_search, moves_to_states,
    str_to_move,
)
from experiments.greedy_tests.fixtures.presentations import (
    MMS02_LEN14, ak, ms640, ms_unsolved,
)
from experiments.greedy_tests.spec import search as spec_search
from experiments.greedy_tests.spec.invariants import abs_det
from experiments.greedy_tests.spec.moves import legacy_to_move, seam_cancels
from experiments.greedy_tests.spec.presentation import Presentation

HIGH = [False, True]
SOLVED_IDS = [0, 3, 5, 7, 11]


def _moves(stats):
    return [str_to_move(m) for m in stats["path_moves"]]


# -- budget ------------------------------------------------------------------


@pytest.mark.parametrize("high", HIGH)
def test_nodes_explored_never_exceeds_the_budget(high):
    for pres in ms640(range(0, 5)) + ms_unsolved(range(0, 2)) + [ak(3)]:
        for budget in (1, 7, 500):
            s = greedy_search(*pres.to_strs(), budget, high_speedup=high)
            assert 1 <= s["nodes_explored"] <= budget


@pytest.mark.parametrize("high", HIGH)
def test_a_budget_of_one_pops_exactly_one_node(high):
    s = greedy_search(*ms_unsolved([0])[0].to_strs(), 1, high_speedup=high)
    assert s["nodes_explored"] == 1
    assert s["solved"] is False


# -- determinism -------------------------------------------------------------


@pytest.mark.parametrize("high", HIGH)
def test_repeated_calls_return_identical_stats(high):
    for pres in ms640(range(0, 4)) + ms_unsolved(range(0, 1)):
        a = greedy_search(*pres.to_strs(), 900, high_speedup=high)
        b = greedy_search(*pres.to_strs(), 900, high_speedup=high)
        assert a == b


# -- the progress callback ---------------------------------------------------


@pytest.mark.parametrize("high", HIGH)
def test_progress_callback_is_result_neutral(high):
    """``HEARTBEAT_EVERY_S`` must not be able to change a result."""
    pres = ms_unsolved([0])[0]
    quiet = greedy_search(*pres.to_strs(), 2500, high_speedup=high)
    seen = []
    loud = greedy_search(*pres.to_strs(), 2500, high_speedup=high,
                         progress=seen.append)
    assert quiet == loud
    assert seen, "the callback never fired; the test proves nothing"


@pytest.mark.parametrize("high", HIGH)
def test_progress_fires_only_on_multiples_of_the_check_interval(high):
    seen = []
    greedy_search(*ms_unsolved([0])[0].to_strs(), 2500, high_speedup=high,
                  progress=seen.append)
    assert seen == [_HB_CHECK_EVERY, 2 * _HB_CHECK_EVERY]
    assert seen == sorted(set(seen))


@pytest.mark.parametrize("high", HIGH)
def test_progress_never_fires_below_the_check_interval(high):
    seen = []
    greedy_search(*ms_unsolved([0])[0].to_strs(), _HB_CHECK_EVERY - 1,
                  high_speedup=high, progress=seen.append)
    assert seen == []


# -- solved runs -------------------------------------------------------------


@pytest.mark.parametrize("idx", SOLVED_IDS)
def test_solved_path_replays_to_a_trivial_state(idx):
    pres = ms640([idx])[0]
    s = greedy_search(*pres.to_strs(), 5000)
    assert s["solved"]
    states = moves_to_states(*pres.to_strs(), _moves(s))
    assert states == s["path"]
    assert [len(x) for x in states[-1]] == [1, 1]


@pytest.mark.parametrize("idx", SOLVED_IDS)
def test_path_lengths_are_consistent(idx):
    s = greedy_search(*ms640([idx])[0].to_strs(), 5000)
    assert s["path_length"] == len(s["path_moves"]) == len(s["path"]) - 1


@pytest.mark.parametrize("idx", SOLVED_IDS)
def test_every_path_step_is_a_valid_definition_2_1_move(idx):
    """Checked against the spec's seam condition, not against the code's own filter."""
    pres = ms640([idx])[0]
    s = greedy_search(*pres.to_strs(), 5000)
    states = [Presentation.from_strs(*st) for st in s["path"]]
    for state, raw in zip(states, s["path_moves"]):
        mv = legacy_to_move(*str_to_move(raw))
        assert seam_cancels(state.relators, mv), (idx, raw)


@pytest.mark.parametrize("idx", SOLVED_IDS)
def test_the_whole_path_preserves_the_abelianization_invariant(idx):
    s = greedy_search(*ms640([idx])[0].to_strs(), 5000)
    for st in s["path"]:
        assert abs_det(Presentation.from_strs(*st)) == 1


def test_the_initial_state_is_reduced_and_canonicalised_before_search():
    """A non-reduced input must land on the same state as its reduction."""
    a = greedy_search("xyYX" + "xy", "xY", 500)
    b = greedy_search("xy", "xY", 500)
    assert a["nodes_explored"] == b["nodes_explored"]
    assert a["solved"] == b["solved"]


# -- unsolved runs -----------------------------------------------------------


@pytest.mark.parametrize("high", HIGH)
def test_unsolved_runs_report_no_path(high):
    s = greedy_search(*ms_unsolved([0])[0].to_strs(), 600, high_speedup=high)
    assert s["solved"] is False
    assert s["path"] == [] and s["path_moves"] == []
    assert s["path_length"] is None


# -- statistics --------------------------------------------------------------


@pytest.mark.parametrize("high", HIGH)
def test_min_le_max_and_expanded_le_discovered(high):
    for pres in ms640(range(0, 6)) + ms_unsolved(range(0, 2)):
        s = greedy_search(*pres.to_strs(), 1500, high_speedup=high)
        assert s["min_relator_length"] <= s["max_relator_length"]
        assert s["max_relator_length_expanded"] <= s["max_relator_length"]


# -- cap behaviour -----------------------------------------------------------


@pytest.mark.parametrize("high", HIGH)
def test_no_discovered_child_exceeds_the_per_relator_cap(high):
    """The cap bounds *children*. It is a filter on successors, not on the state space."""
    for pres in ms640(range(0, 4)) + ms_unsolved(range(0, 1)):
        s = greedy_search(*pres.to_strs(), 800, max_relator_length=24,
                          high_speedup=high)
        for field in ("min_relator", "max_relator", "max_relator_expanded"):
            assert all(len(x) <= 24 for x in s[field])


@pytest.mark.parametrize("high", HIGH)
@pytest.mark.parametrize("pres,init_total", [(ms640([3])[0], 8),
                                             (ms_unsolved([0])[0], 13)],
                         ids=["ms640-3", "unsolved-0"])
def test_the_initial_state_is_exempt_from_the_cap(high, pres, init_total):
    """The cap filters children only; the root is pushed unchecked.

    With a cap of 2 these two presentations enqueue no child at all, so the
    search pops the root, exhausts the heap and stops -- while still reporting a
    discovered total far above ``2 * cap``, which is only possible because the
    root bypassed the filter. (``ms640[0]`` is *not* usable here: it reduces to
    ``YYXyx`` / ``Yx`` and still has a child within a cap of 2.)
    """
    s = greedy_search(*pres.to_strs(), 500, max_relator_length=2, high_speedup=high)
    assert s["nodes_explored"] == 1
    assert s["solved"] is False
    assert s["max_relator_length"] == s["min_relator_length"] == init_total
    assert init_total > 2 * 2, "the root must exceed 2*cap for this to prove anything"


@pytest.mark.slow
@pytest.mark.parametrize("idx,nodes,plen", [(621, 15371, 500), (630, 12429, 79)])
def test_cap_24_and_48_give_identical_traces_on_the_measured_cases(idx, nodes, plen):
    """Measured, not derived.

    The tempting theorem -- "if no popped state exceeded the smaller cap, the
    traces coincide" -- has a guard that cannot be checked from the reported
    statistics: ``max_relator_length_expanded`` is a *total* over both relators
    (25 and 31 here) while the cap is *per relator* (24). So the guard never
    fires on exactly the cases worth checking, and these pairs are pinned as
    measurements instead.
    """
    pres = ms640([idx])[0]
    a = greedy_search(*pres.to_strs(), 30000, max_relator_length=24)
    b = greedy_search(*pres.to_strs(), 30000, max_relator_length=48)
    assert a["solved"] and b["solved"]
    assert a["nodes_explored"] == b["nodes_explored"] == nodes
    assert a["path_length"] == b["path_length"] == plen
    assert a["max_relator_length_expanded"] == b["max_relator_length_expanded"]


# -- solver object reuse -----------------------------------------------------


def test_solve_twice_on_one_instance_resumes_rather_than_restarting():
    """Characterization of a sharp edge: ``solve()`` does not reset its state.

    The first call solves in a handful of pops; the second re-pushes the initial
    state into a heap that already holds the first call's frontier, burns the
    whole budget and reports unsolved. Always construct a fresh solver.
    """
    solver = GreedyBaselineSolver(*ms640([0])[0].to_strs(), max_nodes=3000)
    path, _, first_nodes, _ = solver.solve()
    assert path is not None and first_nodes < 100
    seen_after_first = len(solver.visited)

    path2, _, second_nodes, _ = solver.solve()
    assert path2 is None
    assert second_nodes == 3000
    assert len(solver.visited) > seen_after_first


# -- the spec reproduces the trace (a bonus check on the 2-generator solvers) --


@pytest.mark.parametrize("cyclic", [True, False])
def test_the_spec_search_reproduces_the_solver_trace_exactly(cyclic):
    """Because the heap key ``(total, depth, key)`` is a strict total order.

    Pop order therefore cannot depend on push order, and ``depth`` is fixed by
    the enumeration order, which the spec matches. This is a *bonus* check on
    the two 2-generator solvers, **not** a contract: a correct stable-AC solver
    may explore in a different order and must not be held to this.
    """
    # An unsolved case is included so the comparison covers a real node count
    # rather than the handful of pops the easy ms640 entries need.
    cases = [(p, 500) for p in ms640(range(0, 5))] + [(ms_unsolved([0])[0], 400)]
    for pres, budget in cases:
        got = greedy_search(*pres.to_strs(), budget, cyclic_reduce=cyclic)
        want = spec_search.search(pres, budget, cap=24, cyclic=cyclic)
        for field in ("solved", "nodes_explored", "path_length",
                      "min_relator_length", "max_relator_length",
                      "max_relator_length_expanded"):
            assert got[field] == want[field], (field, pres.to_strs(), budget)
    assert want["nodes_explored"] == 400, "the unsolved case must burn its budget"
