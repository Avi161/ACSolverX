"""Pins for the unsolved124 × s20_mk2 census runner (budget-capped)."""
from __future__ import annotations

import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from experiments.heuristic_search.runners import run_unsolved124_s20mk2 as ru  # noqa: E402

MAX_BUDGET = 200


def test_autmin_freeze_r1_equals_rep():
    assert ru.assert_autmin_freeze() is True


def test_load_rows_start_total():
    rows = ru.load_rows()
    assert len(rows) == 124
    for r in rows[:5]:
        assert r["start_total"] == len(r["r1"]) + len(r["r2"])


def test_stride_four_covers_all():
    rows = ru.load_rows()
    seen = []
    for i in range(1, 5):
        chunk, tag = ru._stride_chunk(rows, 4, i)
        assert tag == f"_c{i}of4"
        assert len(chunk) == 31
        seen.extend(r["name"] for r in chunk)
    assert len(seen) == 124
    assert len(set(seen)) == 124


def test_smoke_s20mk2_enriched_keys(tmp_path):
    cfg = dict(
        ARMS=["s20_mk2"],
        CHUNKS=4,
        CHUNK_INDEX=1,
        ENGINE="hcompact",
        N_WORKERS=1,
        KEEP_PATH=False,
        NODE_BUDGET=MAX_BUDGET,
        CHECKPOINTS=[MAX_BUDGET],
        MAX_RELATOR_LENGTH=64,
        RESUME=False,
        OUT_STEM="smoke_u124",
        SUBSET=None,
    )
    out = ru.run_unsolved124_s20mk2(cfg, out_dir=str(tmp_path),
                                    heartbeat_secs=3600, progress_secs=3600)
    assert os.path.exists(out)
    assert "_dpos_" in os.path.basename(out)
    rows = [json.loads(l) for l in open(out) if l.strip()]
    assert len(rows) == 31
    for r in rows:
        for k in ("arm", "name", "r1", "r2", "start_total",
                  "min_relator_length", "min_relator", "min_delta", "improved",
                  "nodes_explored", "depth_tie", "path_pending"):
            assert k in r, k
        assert r["arm"] == "s20_mk2"
        assert r["depth_tie"] == "+depth"
        assert r["start_total"] == len(r["r1"]) + len(r["r2"])
        assert r["min_delta"] == r["start_total"] - r["min_relator_length"]
        assert r["improved"] == (r["min_delta"] > 0)
        mr = r["min_relator"]
        assert isinstance(mr, list) and len(mr) == 2
        assert len(mr[0]) + len(mr[1]) == r["min_relator_length"]
        if r["solved"]:
            assert r["path_pending"] is False
            assert r.get("path_moves")


def test_progress_callback_receives_min_total(monkeypatch):
    """hcompact progress may take (nodes, min_total); one-arg still works."""
    import experiments.heuristic_search.core.hcompact as hc
    # Default check interval is 1024 pops — drag it under the test budget ceiling.
    monkeypatch.setattr(hc, "_HB_CHECK_EVERY", 8)
    seen = []

    def one(n):
        seen.append(("one", n))

    def two(n, min_total=None):
        seen.append(("two", n, min_total))

    cfg = ru.run_ab.ARMS["s20_mk2"]
    row = ru.load_rows()[0]  # aca_0 burns the budget (does not solve in <1k)
    hc.greedy_search_hcompact(row["r1"], row["r2"], 64, max_relator_length=64,
                              config=cfg, progress=one)
    hc.greedy_search_hcompact(row["r1"], row["r2"], 64, max_relator_length=64,
                              config=cfg, progress=two)
    assert any(t[0] == "one" for t in seen)
    twos = [t for t in seen if t[0] == "two"]
    assert twos and all(t[2] is not None for t in twos)
    assert all(isinstance(t[2], int) and t[2] >= 2 for t in twos)


def test_heartbeat_drop_tracking_logic():
    """Simulate progress ticks: DROP only when min_len fell since last beat."""
    start = 18
    state = {"min_len": start, "min_at_beat": start}
    events = []

    def on_beat(cur, prev_beat):
        drop = prev_beat - cur
        events.append((cur, drop))

    state["min_len"] = 16
    on_beat(state["min_len"], state["min_at_beat"])
    state["min_at_beat"] = state["min_len"]
    on_beat(state["min_len"], state["min_at_beat"])
    assert events[0] == (16, 2)
    assert events[1] == (16, 0)


def test_rejects_non_s20mk2_arms(tmp_path):
    cfg = dict(
        ARMS=["baseline"],
        CHUNKS=1,
        CHUNK_INDEX=1,
        ENGINE="hcompact",
        N_WORKERS=1,
        NODE_BUDGET=50,
        MAX_RELATOR_LENGTH=64,
        RESUME=False,
        OUT_STEM="nope",
    )
    with pytest.raises(ValueError, match="s20_mk2-only"):
        ru.run_unsolved124_s20mk2(cfg, out_dir=str(tmp_path))
