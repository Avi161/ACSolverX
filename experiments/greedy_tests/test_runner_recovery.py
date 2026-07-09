"""Heavy-mode solved rows are durable BEFORE their path is recovered.

The heavy solver tracks no paths, so a solved presentation is re-solved by the
normal solver after the pool tears down. That recovery is the memory-hungry
step, and it runs serially in the parent at the end of the whole sweep -- the
most likely place for a run to die.

If the row were written only after recovery (as it once was), a crash there
would lose exactly the successes, and resume could not tell they had ever been
found: ``_read_done`` reads the file, so the multi-hour search would be repeated
and deferred again, never reaching disk. Hence: write the search result at once
as ``path_pending``, then fill the path in place.

``N_WORKERS=1`` throughout, so no pool is built and ``greedy_search`` can be
monkeypatched in-process. The pool path is covered by ``test_runner_parallel``.
"""

import json
import os

import pytest

from experiments.run_baseline import DEFAULT_CONFIG, run_dataset
import experiments.run_baseline as rb
from experiments.search.greedy_baseline import moves_to_states, str_to_move
from experiments.greedy_tests.fixtures.presentations import MS640, load_flat_lines

BUDGET = 500


@pytest.fixture
def tiny_dataset(tmp_path):
    lines = load_flat_lines(MS640)[:4]
    p = tmp_path / "tiny.txt"
    p.write_text("".join(repr(list(ln)) + "\n" for ln in lines))
    return str(p)


def _cfg(tmp_path, tiny_dataset, **over):
    return {**DEFAULT_CONFIG,
            "DATASET": tiny_dataset,
            "LOCAL_OUT_DIR": str(tmp_path / "out"),
            "USE_WANDB": False,
            "PROGRESS_EVERY": 100,
            "HIGH_SPEEDUP": True,
            "N_WORKERS": 1,
            **over}


def _rows(path):
    with open(path) as f:
        return [json.loads(ln) for ln in f if ln.strip()]


def _paths_of(out):
    p = out[: -len(".jsonl")] + "_paths.jsonl"
    return _rows(p) if os.path.exists(p) else []


def _break_recovery(monkeypatch, only=None):
    """Make the recovery re-solve (high_speedup=False) raise, as an OOM would."""
    real = rb.greedy_search

    def fake(r1, r2, budget, **kw):
        if not kw.get("high_speedup", False):
            raise MemoryError("simulated OOM during path recovery")
        return real(r1, r2, budget, **kw)

    def fake_one(r1, r2, budget, **kw):
        # `only` selects by relator pair, since the presentation id is not passed
        if not kw.get("high_speedup", False) and (r1, r2) == only:
            raise MemoryError("simulated OOM during path recovery")
        return real(r1, r2, budget, **kw)

    monkeypatch.setattr(rb, "greedy_search", fake_one if only else fake)
    return real


def test_a_solved_row_is_written_before_its_path_is_recovered(
        tmp_path, tiny_dataset, monkeypatch):
    """A dying recovery pass must not cost a single search result."""
    _break_recovery(monkeypatch)
    out = run_dataset(_cfg(tmp_path, tiny_dataset), BUDGET)   # must NOT raise

    rows = _rows(out)
    assert len(rows) == 4, "a failed recovery lost search rows"
    assert all(r["solved"] for r in rows)
    assert all(r["path_pending"] is True for r in rows)
    assert all(r["path_length"] is None for r in rows)
    assert all("path_recovered" not in r for r in rows)
    assert _paths_of(out) == [], "no path exists yet"


def test_a_failed_recovery_is_retried_on_resume_without_re_searching(
        tmp_path, tiny_dataset, monkeypatch):
    """Resume retries the cheap path recovery, never the expensive search."""
    real = _break_recovery(monkeypatch)
    cfg = _cfg(tmp_path, tiny_dataset)
    out = run_dataset(cfg, BUDGET)
    assert all(r["path_pending"] is True for r in _rows(out))

    heavy_calls = []
    monkeypatch.setattr(rb, "greedy_search", real)

    def counting(r1, r2, budget, **kw):
        if kw.get("high_speedup", False):
            heavy_calls.append((r1, r2))
        return real(r1, r2, budget, **kw)

    monkeypatch.setattr(rb, "greedy_search", counting)
    out2 = run_dataset(cfg, BUDGET)          # RESUME defaults to True

    assert out2 == out, "resume must reattach to the same file"
    assert heavy_calls == [], "the search was repeated; only the path was missing"

    rows = _rows(out2)
    assert len(rows) == 4, "resume duplicated rows"
    assert all("path_pending" not in r for r in rows)
    assert all(r["path_recovered"] is True for r in rows)
    assert all(r["path_length"] is not None for r in rows)

    paths = _paths_of(out2)
    assert len(paths) == 4
    for pr in paths:
        states = moves_to_states(pr["r1"], pr["r2"],
                                 [str_to_move(m) for m in pr["path_moves"]])
        assert [len(s) for s in states[-1]] == [1, 1]


def test_one_failed_recovery_does_not_abort_the_others(
        tmp_path, tiny_dataset, monkeypatch):
    """A single MemoryError must not take the remaining presentations with it."""
    lines = load_flat_lines(MS640)[:4]
    victim = rb.int_line_to_relators(list(lines[1]))
    _break_recovery(monkeypatch, only=victim)

    out = run_dataset(_cfg(tmp_path, tiny_dataset), BUDGET)
    by_id = {r["pres_id"]: r for r in _rows(out)}
    assert len(by_id) == 4

    assert by_id[1].get("path_pending") is True, "the victim keeps its search row"
    assert by_id[1]["path_length"] is None
    for pid in (0, 2, 3):
        assert by_id[pid].get("path_recovered") is True, \
            "one failure aborted the other recoveries"
        assert by_id[pid]["path_length"] is not None
    assert {p["pres_id"] for p in _paths_of(out)} == {0, 2, 3}


def test_recovery_replaces_the_pending_row_rather_than_appending(
        tmp_path, tiny_dataset):
    """One row per pres_id -- every consumer of the jsonl assumes it."""
    out = run_dataset(_cfg(tmp_path, tiny_dataset), BUDGET)
    ids = [r["pres_id"] for r in _rows(out)]
    assert ids == sorted(set(ids)), f"duplicate or unordered rows: {ids}"
    assert all(r["path_recovered"] is True for r in _rows(out))
    assert len(_paths_of(out)) == 4


def test_a_second_resume_after_full_recovery_is_a_no_op(tmp_path, tiny_dataset):
    """Nothing pending, nothing to search: the paths file must not grow."""
    cfg = _cfg(tmp_path, tiny_dataset)
    out = run_dataset(cfg, BUDGET)
    before = _rows(out), _paths_of(out)
    run_dataset(cfg, BUDGET)
    assert (_rows(out), _paths_of(out)) == before
