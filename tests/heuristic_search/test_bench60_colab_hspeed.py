"""Bench60 Colab HIGH_SPEEDUP plumbing — chunking, arms, memory cap.

No search above budget 1000. The 1M figure is passed only into
``_est_gb`` / ``_resolve_workers`` (pure arithmetic), never into a solver.
"""
from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

import experiments.heuristic_search.runners.run_ab as ra  # noqa: E402
from experiments.heuristic_search.runners import run_s24_scale as rs  # noqa: E402

COLAB_ARMS = ["baseline", "s12", "s28", "s20_mk2", "s24_k1_mk2"]


def test_colab_arms_registered():
    for arm in COLAB_ARMS:
        assert arm in ra.ARMS, f"missing arm {arm!r} — import run_s24_scale first"


def test_bench60_stride_chunks_partition():
    rows = ra.load_rows("bench66", 60)
    assert len(rows) == 60
    seen = []
    tags = []
    for ci in range(1, 6):
        picked, tag = rs._stride_chunk(rows, 5, ci)
        assert len(picked) == 12, (ci, len(picked))
        assert tag == f"_c{ci}of5"
        seen.extend(r["name"] for r in picked)
        tags.append(tag)
    assert len(set(tags)) == 5
    assert len(seen) == 60
    assert len(set(seen)) == 60
    assert set(seen) == {r["name"] for r in rows}


def test_resolve_workers_8cores_50gb_caps_below_ram_at_1m(monkeypatch):
    """Colab shape: 8 cores, ~50 GB. hcompact @1M ≈7.6 GB → 6 workers, not 8."""
    monkeypatch.setattr(ra, "_avail_gb", lambda: 50.0)
    monkeypatch.setattr(os, "cpu_count", lambda: 8)

    nw, per = ra._resolve_workers(
        {"N_WORKERS": "auto"}, 1_000_000, 48, "hcompact", True)
    assert per == pytest.approx(7.6, abs=0.3)
    assert nw == 6, f"expected memory cap 6, got {nw} (per={per:.2f})"
    assert nw * per + 2.0 <= 50.0 + 0.5

    # hsolve+keep_path at 1M must NOT claim 8 workers on 50 GB
    nw_hs, per_hs = ra._resolve_workers(
        {"N_WORKERS": "auto"}, 1_000_000, 48, "hsolve", True)
    assert nw_hs == 1
    assert per_hs > 30


def test_resolve_workers_never_exceeds_cores(monkeypatch):
    monkeypatch.setattr(ra, "_avail_gb", lambda: 500.0)  # RAM not binding
    monkeypatch.setattr(os, "cpu_count", lambda: 8)
    nw, _ = ra._resolve_workers(
        {"N_WORKERS": "auto"}, 1000, 48, "hcompact", True)
    assert nw == 8


def test_hcompact_mandatory_for_parallel_at_1m(monkeypatch):
    """Documented Colab contract: only hcompact enables multi-worker @1M/50GB."""
    monkeypatch.setattr(ra, "_avail_gb", lambda: 50.0)
    monkeypatch.setattr(os, "cpu_count", lambda: 8)
    nw_h, _ = ra._resolve_workers(
        {"N_WORKERS": "auto"}, 1_000_000, 48, "hcompact", True)
    nw_s, _ = ra._resolve_workers(
        {"N_WORKERS": "auto"}, 1_000_000, 48, "hsolve", True)
    assert nw_h >= 4
    assert nw_s == 1
