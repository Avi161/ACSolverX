"""Colab-scale runner for the scout-winning L+w·S arm (and length control).

Wraps ``run_ab`` without modifying it: registers S-arms into ``run_ab.ARMS`` at
import time, supports optional stride chunking for multi-session Colab, then
delegates to ``run_ab.run_ab``.

Agent-local use stays at NODE_BUDGET ≤ 1000. Production budgets are Colab-only.

    from experiments.heuristic_search.runners.run_s24_scale import run_s24_scale
    run_s24_scale(cfg, out_dir=...)
"""
from __future__ import annotations

import os
import sys

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

from experiments.heuristic_search.core.hsolve import RECOMMENDED  # noqa: E402
from experiments.heuristic_search.runners import run_ab  # noqa: E402


def _cfg(**w):
    return {"segments": [{"upto": None, "w": dict(w)}]}


# Register without editing run_ab.py (new-files-only rule).
run_ab.ARMS.update({
    "s12": _cfg(L=1.0, S=12.0),
    "s20": _cfg(L=1.0, S=20.0),   # S-grid holdout peak on 800 hard
    "s24": _cfg(L=1.0, S=24.0),   # campaign hard-recovery leader
    "s28": _cfg(L=1.0, S=28.0),
    "s8": _cfg(L=1.0, S=8.0),
    "s20_mk2": _cfg(L=1.0, S=20.0, MK=2.0),   # Aut-tune interim S+MK leader
    "s20_mk8": _cfg(L=1.0, S=20.0, MK=8.0),
    "s24_k1_mk2": _cfg(L=1.0, S=24.0, K=1.0, MK=2.0),  # interim S+K+MK
    "recommended": RECOMMENDED,
    "baseline": None,
})


def _stride_chunk(rows, chunks, chunk_index):
    """1-based chunk_index; None = all rows (single session)."""
    if not chunks or chunks <= 1 or chunk_index is None:
        return rows, ""
    if not (1 <= int(chunk_index) <= int(chunks)):
        raise ValueError(f"CHUNK_INDEX must be 1..{chunks}, got {chunk_index}")
    i = int(chunk_index) - 1
    n = int(chunks)
    picked = [r for k, r in enumerate(rows) if k % n == i]
    return picked, f"_c{chunk_index}of{chunks}"


def run_s24_scale(cfg, out_dir="results/hsearch", heartbeat_secs=60,
                  progress_secs=300):
    """Like ``run_ab``, plus optional CHUNKS / CHUNK_INDEX stride split."""
    chunks = cfg.get("CHUNKS") or 1
    chunk_index = cfg.get("CHUNK_INDEX")
    rows = run_ab.load_rows(cfg["DATASET"], cfg.get("SUBSET"))
    rows, tag = _stride_chunk(rows, chunks, chunk_index)
    cfg = dict(cfg)
    stem = cfg.get("OUT_STEM", "hsearch_s_scale")
    if tag:
        cfg["OUT_STEM"] = f"{stem}{tag}"
    # Temporarily narrow load_rows via SUBSET replacement: monkeypatch rows.
    _orig = run_ab.load_rows

    def _load(dataset, subset=None):
        # ignore dataset reload; return the already-chunked list
        return rows

    run_ab.load_rows = _load
    try:
        return run_ab.run_ab(cfg, out_dir=out_dir, heartbeat_secs=heartbeat_secs,
                            progress_secs=progress_secs)
    finally:
        run_ab.load_rows = _orig
