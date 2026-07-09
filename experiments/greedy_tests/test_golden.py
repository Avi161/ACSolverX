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

The slow tier reproduces the two searches ``CLAUDE.md`` records by hand
(ms640 621 -> 15,371 nodes / 500 moves; 630 -> 12,429 / 79) and the 620-639
sweep it records as 10 solved of 20.
"""

import json
import os

import pytest

from experiments.search.greedy_baseline import greedy_search
from experiments.greedy_tests.fixtures.presentations import load_dataset

GOLDEN = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      "golden", "greedy_golden.json")

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
        if high_speedup and field == "path_length":
            continue          # the heavy solver never reports a path
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


def test_the_recorded_anchor_searches_match_claude_md():
    """These two numbers are quoted in CLAUDE.md; keep the file and the doc in step."""
    anchors = {(621, 24): (15371, 500), (630, 24): (12429, 79),
               (621, 48): (15371, 500), (630, 48): (12429, 79)}
    found = {}
    for e in SLOW:
        key = (e["pres_id"], e["cap"])
        if key in anchors:
            found[key] = (e["nodes_explored"], e["path_length"])
            assert e["solved"] is True
    assert found == anchors, found


def test_the_620_639_sweep_solves_exactly_half():
    """CLAUDE.md: 10 solved / 10 budget-capped at 30k. An unsolved row is not a bug."""
    sweep = [e for e in SLOW
             if e["cap"] == 24 and 620 <= e["pres_id"] <= 639 and e["budget"] == 30000]
    assert len(sweep) == 20
    assert sum(e["solved"] for e in sweep) == 10
    assert all(e["nodes_explored"] == 30000 for e in sweep if not e["solved"])


def test_no_hash_dependent_field_was_recorded():
    """``min_relator``/``max_relator`` vary with PYTHONHASHSEED; they must not be pinned."""
    for e in ENTRIES:
        assert "min_relator" not in e
        assert "max_relator" not in e
