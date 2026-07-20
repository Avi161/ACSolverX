"""Regression against a committed baseline.

A failure here is a **result change**, not a stale fixture. The search is
deterministic -- no RNG, fixed enumeration order, a strict total order on the
heap -- so these numbers are reproducible across machines and processes. If one
moves, some change altered the search. Find out which, and why, before running
``tools/regen_golden.py``.

Only deterministic fields are stored. ``min_relator`` and ``max_relator`` are
selected by ``min()``/``max()`` over a ``set`` in the normal solver, so their tie
breaks depend on ``PYTHONHASHSEED``; their lengths do not, and only the lengths
are recorded.

Every budget is capped at ``MAX_BUDGET`` (1,000). That is not a weakening: a
search at budget ``B`` is exactly the first ``B`` pops of a search at any larger
budget, because the heap key is a strict total order. 554 of the 640 ms640
presentations solve inside it; the deepest costs 990 nodes (551) and the longest
path is 101 moves (466), and
``test_solver_properties.py::test_a_deep_solved_run_is_also_unchanged_by_raising_the_budget``
asserts that those statistics do not move when the budget is raised.
"""

import json
import os

import pytest

from experiments.search.greedy_baseline import greedy_search
from experiments.greedy_tests.fixtures.presentations import load_dataset
from experiments.greedy_tests.tools.regen_golden import GOLDEN, MAX_BUDGET

CHECKED = ("solved", "nodes_explored", "path_length", "min_relator_length",
           "max_relator_length", "max_relator_length_expanded",
           "max_relator_expanded")


def _load():
    with open(GOLDEN) as f:
        return json.load(f)["entries"]


ENTRIES = _load()
FAST = [e for e in ENTRIES if e["tier"] == "fast"]
SLOW = [e for e in ENTRIES if e["tier"] == "slow"]
_CACHE = {}


def _pres(dataset, pid):
    if dataset not in _CACHE:
        _CACHE[dataset] = load_dataset(dataset)
    return _CACHE[dataset][pid]


def _check(entry, high_speedup=False):
    pres = _pres(entry["dataset"], entry["pres_id"])
    stats = greedy_search(*pres.to_strs(), entry["budget"],
                          max_relator_length=entry["cap"],
                          cyclic_reduce=entry["cyclic"],
                          high_speedup=high_speedup)
    for field in CHECKED:
        assert stats[field] == entry[field], (
            f"{field} changed for {entry['dataset']} pres {entry['pres_id']} "
            f"(budget={entry['budget']}, cap={entry['cap']}, "
            f"cyclic={entry['cyclic']}): golden={entry[field]!r} "
            f"now={stats[field]!r}")


def _ident(e):
    return f"{os.path.basename(e['dataset'])[:6]}-{e['pres_id']}-b{e['budget']}-c{e['cap']}"


def test_the_golden_file_is_populated():
    assert len(ENTRIES) >= 40
    assert FAST and SLOW


@pytest.mark.parametrize("entry", FAST, ids=[_ident(e) for e in FAST])
def test_fast_golden_entries(entry):
    _check(entry)


@pytest.mark.parametrize("entry", FAST[:6], ids=[_ident(e) for e in FAST[:6]])
def test_the_heavy_solver_reproduces_the_golden_entries(entry):
    _check(entry, high_speedup=True)


@pytest.mark.slow
@pytest.mark.parametrize("entry", SLOW, ids=[_ident(e) for e in SLOW])
def test_slow_golden_entries(entry):
    _check(entry)


def test_no_golden_entry_exceeds_the_budget_ceiling():
    """Keeps the suite fast. Sound because a small budget is a prefix of a large one."""
    assert all(e["budget"] <= MAX_BUDGET for e in ENTRIES)


@pytest.mark.parametrize("pres_id,nodes,plen", [(551, 990, 69), (466, 614, 101)],
                         ids=["deepest-search", "longest-path"])
def test_the_deep_solved_anchors(pres_id, nodes, plen):
    """551 costs the most nodes of any solve under the ceiling; 466 has the longest path."""
    deep = [e for e in SLOW if e["pres_id"] == pres_id]
    assert {e["cap"] for e in deep} == {24, 48}, "recorded at both caps"
    for e in deep:
        assert e["solved"] is True
        assert e["nodes_explored"] == nodes
        assert e["path_length"] == plen


def test_the_620_639_sweep_records_a_solved_and_capped_mix():
    """ms640 is only ~606/640 greedy-solvable, so an unsolved row is not a bug."""
    sweep = [e for e in SLOW
             if e["cap"] == 24 and 620 <= e["pres_id"] <= 639
             and e["budget"] == MAX_BUDGET]
    assert len(sweep) == 20
    solved = [e["pres_id"] for e in sweep if e["solved"]]
    assert solved == [627, 631]
    assert all(e["nodes_explored"] == MAX_BUDGET for e in sweep if not e["solved"])
    assert all(e["nodes_explored"] < MAX_BUDGET for e in sweep if e["solved"])


def test_no_hash_dependent_field_was_recorded():
    """``min_relator``/``max_relator`` vary with PYTHONHASHSEED; they must not be pinned."""
    for e in ENTRIES:
        assert "min_relator" not in e
        assert "max_relator" not in e
