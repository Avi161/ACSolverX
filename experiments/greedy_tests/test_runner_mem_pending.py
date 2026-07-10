"""A guard-tripped presentation reaches disk before its serial retry runs.

The memory guard stops a search that is about to exhaust the machine, and the
parent retries it alone once the pool has drained. But the pool drains only
after every OTHER presentation finishes -- ~29 hours for 261 presentations at a
1M node budget, far longer than a Colab session survives. So the trip used to
leave no trace at all: no row, the id absent from ``done``, and the next resume
handing it straight back to the pool to trip again on the same 1/n share. The
expensive search was repeated every session and never landed.

Fix: write the row the instant the guard fires, flagged ``mem_abort_pending``.
Being on disk puts the id in ``done``, so the pool never sees it again; the
runner routes it to the serial retry instead, where it gets the whole machine.
``_finalize`` then overwrites that placeholder in place, so one pres_id keeps
exactly one row.

Three states a memory-aborted row can be in, and they must stay distinct:
  ``mem_abort_pending`` -> retry it serially, next session if need be
  ``mem_abort`` alone   -> terminal; it does not fit here even alone
  neither               -> a normal result

``N_WORKERS=1`` throughout, so no pool is built and ``greedy_search`` can be
monkeypatched in-process. The pool path is covered by ``test_runner_parallel``.
"""

import json

import pytest

from experiments.run_baseline import DEFAULT_CONFIG, run_dataset
import experiments.run_baseline as rb
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
            "use_path": False,
            **over}


def _rows(path):
    with open(path) as f:
        return [json.loads(ln) for ln in f if ln.strip()]


def _row(path, pres_id):
    hits = [r for r in _rows(path) if r["pres_id"] == pres_id]
    assert len(hits) == 1, f"pres {pres_id} has {len(hits)} rows, expected exactly 1"
    return hits[0]


def _trip(monkeypatch, on_pres, nodes=123, forever=False):
    """Make the guard fire for ``on_pres``. `forever` also fails the serial retry.

    The guard is RSS-driven, and macOS ``ru_maxrss`` never crosses a real
    threshold here (a forked child's resets, and the compressor hides the rest),
    so the trip is injected at the one seam that matters: ``greedy_search``
    raising ``_MemBudgetExceeded`` out of its progress callback.
    """
    real = rb.greedy_search
    calls = {"n": 0}

    def fake(r1, r2, budget, **kw):
        if kw.get("high_speedup") and _pid_of(r1, r2) == on_pres:
            calls["n"] += 1
            if forever or calls["n"] == 1:
                raise rb._MemBudgetExceeded(on_pres, nodes, 19.1, 15.9)
        return real(r1, r2, budget, **kw)

    monkeypatch.setattr(rb, "greedy_search", fake)
    return calls


_PIDS = {}


def _pid_of(r1, r2):
    return _PIDS.get((r1, r2), -1)


@pytest.fixture(autouse=True)
def _index_pids(tiny_dataset):
    _PIDS.clear()
    for pid, a, b in rb.load_dataset(tiny_dataset, None):
        _PIDS[(a, b)] = pid
    yield
    _PIDS.clear()


def _out_path(cfg):
    return rb._resolve_paths(cfg, BUDGET, 4)[0]


def _seed(cfg, rows):
    """Write a jsonl at the exact path the next run will resolve to."""
    import os
    out_path = _out_path(cfg)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    return out_path


def _pending_row(pres_id, r1, r2, cfg):
    return {"pres_id": pres_id, "r1": r1, "r2": r2, "node_budget": BUDGET,
            "max_relator_length_cap": cfg["MAX_RELATOR_LENGTH"],
            "solved": False, "nodes_explored": 123, "path_length": None,
            "mem_abort": True, "mem_abort_pending": True}


# --- the row lands the moment the guard fires -----------------------------

def test_a_guard_trip_is_on_disk_before_the_retry_can_finalise_it(
        tmp_path, tiny_dataset, monkeypatch):
    """The whole point: a session that dies mid-run still recorded the trip."""
    _trip(monkeypatch, on_pres=1, forever=True)

    # _finalize is what turns the placeholder into a terminal row. Killing it
    # simulates the session dying after the trip but before the retry resolves.
    def boom(*a, **k):
        raise RuntimeError("session died before the retry finished")
    monkeypatch.setattr(rb, "_update_row", boom)

    cfg = _cfg(tmp_path, tiny_dataset)
    with pytest.raises(RuntimeError):
        run_dataset(cfg, BUDGET)

    row = _row(_out_path(cfg), 1)
    assert row["mem_abort_pending"] is True
    assert row["mem_abort"] is True
    assert row["nodes_explored"] == 123, "must record where it got to, not the budget"
    assert row["solved"] is False


def test_the_trip_row_never_claims_to_have_searched_the_whole_budget(
        tmp_path, tiny_dataset, monkeypatch):
    _trip(monkeypatch, on_pres=1, nodes=77, forever=True)
    monkeypatch.setattr(rb, "_avail_ram_gb", lambda: 0.0)   # no serial retry
    out = run_dataset(_cfg(tmp_path, tiny_dataset), BUDGET)
    assert _row(out, 1)["nodes_explored"] == 77 != BUDGET


# --- resume routes it to the serial retry, not back into the pool ---------

def test_a_new_session_retries_a_pending_row_and_fills_it_in(
        tmp_path, tiny_dataset):
    """The bug this fixes: the id used to be re-searched and re-lost forever."""
    cfg = _cfg(tmp_path, tiny_dataset)
    pid, r1, r2 = 1, *_PIDS_inv(1)
    out_path = _seed(cfg, [_pending_row(pid, r1, r2, cfg)])

    out = run_dataset(cfg, BUDGET)
    assert out == out_path

    row = _row(out, 1)
    assert "mem_abort_pending" not in row, "placeholder was never resolved"
    assert "mem_abort" not in row, "a successful retry must not stay aborted"
    assert row["nodes_explored"] > 0
    assert row["path_length"] is None or row["solved"]


def test_a_pending_row_is_never_handed_back_to_the_worker_loop(
        tmp_path, tiny_dataset, monkeypatch):
    """It is in `done`, so `todo` excludes it; only the serial retry may run it."""
    cfg = _cfg(tmp_path, tiny_dataset)
    pid, r1, r2 = 1, *_PIDS_inv(1)
    _seed(cfg, [_pending_row(pid, r1, r2, cfg)])

    seen = []
    real_solve_one = rb._solve_one
    monkeypatch.setattr(rb, "_solve_one",
                        lambda job: (seen.append(job[0]), real_solve_one(job))[1])

    run_dataset(cfg, BUDGET)
    assert 1 not in seen, "the pool re-searched a presentation already on disk"
    assert sorted(seen) == [0, 2, 3]


def test_the_retried_row_is_rewritten_in_place_not_appended(
        tmp_path, tiny_dataset):
    """One pres_id, one row -- every consumer assumes it."""
    cfg = _cfg(tmp_path, tiny_dataset)
    pid, r1, r2 = 1, *_PIDS_inv(1)
    _seed(cfg, [_pending_row(pid, r1, r2, cfg)])

    out = run_dataset(cfg, BUDGET)
    ids = [r["pres_id"] for r in _rows(out)]
    assert sorted(ids) == [0, 1, 2, 3]
    assert len(ids) == len(set(ids)), f"duplicate rows: {ids}"


def test_a_resumed_retry_does_not_double_count_the_presentation(
        tmp_path, tiny_dataset):
    """`_read_done` already counted the placeholder; counting it again would
    push `processed` past `n_todo` and corrupt the solve-rate."""
    cfg = _cfg(tmp_path, tiny_dataset)
    pid, r1, r2 = 1, *_PIDS_inv(1)
    _seed(cfg, [_pending_row(pid, r1, r2, cfg)])

    run_dataset(cfg, BUDGET)   # must not raise; 3 in todo, 1 retried serially
    done, n_seen, _ = rb._read_done(_out_path(cfg))
    assert n_seen == 4 == len(done)


# --- the three states stay distinct ---------------------------------------

def test_a_terminal_mem_abort_row_is_never_retried(tmp_path, tiny_dataset, monkeypatch):
    """No `mem_abort_pending` means it did not fit even alone. Re-running it
    would burn the whole budget again to learn the same thing."""
    cfg = _cfg(tmp_path, tiny_dataset)
    pid, r1, r2 = 1, *_PIDS_inv(1)
    row = _pending_row(pid, r1, r2, cfg)
    del row["mem_abort_pending"]
    _seed(cfg, [row])

    seen = []
    real_solve_one = rb._solve_one
    monkeypatch.setattr(rb, "_solve_one",
                        lambda job: (seen.append(job[0]), real_solve_one(job))[1])

    out = run_dataset(cfg, BUDGET)
    assert 1 not in seen
    after = _row(out, 1)
    assert after["mem_abort"] is True
    assert after["nodes_explored"] == 123, "a terminal row must not be re-searched"


def test_a_failed_retry_burns_the_placeholder_to_a_terminal_row(
        tmp_path, tiny_dataset, monkeypatch):
    cfg = _cfg(tmp_path, tiny_dataset)
    pid, r1, r2 = 1, *_PIDS_inv(1)
    _seed(cfg, [_pending_row(pid, r1, r2, cfg)])
    _trip(monkeypatch, on_pres=1, nodes=456, forever=True)

    out = run_dataset(cfg, BUDGET)
    row = _row(out, 1)
    assert row["mem_abort"] is True
    assert "mem_abort_pending" not in row, "a retried-and-failed row must be terminal"
    assert row["nodes_explored"] == 456


def test_a_placeholder_that_cannot_be_retried_stays_pending(
        tmp_path, tiny_dataset, monkeypatch):
    """Unreadable RAM is not evidence the search does not fit. Keep the
    placeholder so a later session on a bigger machine retries it."""
    cfg = _cfg(tmp_path, tiny_dataset)
    pid, r1, r2 = 1, *_PIDS_inv(1)
    _seed(cfg, [_pending_row(pid, r1, r2, cfg)])
    monkeypatch.setattr(rb, "_avail_ram_gb", lambda: 0.0)

    out = run_dataset(cfg, BUDGET)
    row = _row(out, 1)
    assert row["mem_abort_pending"] is True, "burned a row we learned nothing about"


def test_a_vanished_placeholder_is_appended_not_silently_dropped(
        tmp_path, tiny_dataset, monkeypatch):
    """`_update_row` no-ops when the id is absent, and `_finalize` holds a result
    that exists nowhere else. Simulates the placeholder being dropped between the
    trip and the retry -- exactly what Colab's Drive mount did to rows 7 and 8."""
    cfg = _cfg(tmp_path, tiny_dataset)
    pid, r1, r2 = 1, *_PIDS_inv(1)
    _seed(cfg, [_pending_row(pid, r1, r2, cfg)])

    real = rb._update_row

    def vanishing(path, pres_id, row):
        keep = [ln for ln in open(path)
                if ln.strip() and json.loads(ln)["pres_id"] != pres_id]
        with open(path, "w") as f:
            f.writelines(keep)
        return real(path, pres_id, row)      # nothing to match now -> False

    monkeypatch.setattr(rb, "_update_row", vanishing)

    out = run_dataset(cfg, BUDGET)
    row = _row(out, 1)          # exactly one row, and it is the real result
    assert "mem_abort" not in row, "the retry's result was lost"
    assert "mem_abort_pending" not in row
    assert row["nodes_explored"] > 0


# --- _read_mem_pending itself ---------------------------------------------

def test_read_mem_pending_selects_only_the_unresolved_trips(tmp_path):
    p = tmp_path / "x.jsonl"
    p.write_text("".join(json.dumps(r) + "\n" for r in [
        {"pres_id": 0, "solved": True},
        {"pres_id": 1, "solved": False, "mem_abort": True, "mem_abort_pending": True},
        {"pres_id": 2, "solved": False, "mem_abort": True},
        {"pres_id": 3, "solved": True, "path_pending": True},
    ]))
    assert rb._read_mem_pending(str(p)) == {1}
    assert rb._read_pending(str(p)) == {3}


def test_read_mem_pending_is_empty_for_a_missing_file(tmp_path):
    assert rb._read_mem_pending(str(tmp_path / "nope.jsonl")) == set()


def _PIDS_inv(pid):
    for (a, b), p in _PIDS.items():
        if p == pid:
            return a, b
    raise KeyError(pid)
