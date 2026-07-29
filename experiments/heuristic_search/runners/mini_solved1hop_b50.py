"""Mini plumbing check: solved_1hop_autclean @ budget 50 (not a ranking).

Uses a strided 8-orbit subset (mix of seed + moved_cov), 5 arms, hcompact,
presentation-major runner, then certificate replay on any solves.

    PYTHONPATH=. python3 -m experiments.heuristic_search.runners.mini_solved1hop_b50
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

from experiments.heuristic_search.core.hcompact import greedy_search_hcompact  # noqa: E402
from experiments.heuristic_search.runners.run_solved1hop_scale import (  # noqa: E402
    run_solved1hop_scale, load_frozen, DATASET_NAME, _stride_chunk,
)
from experiments.heuristic_search.verify.verify_solved1hop_certs import (  # noqa: E402
    verify_file, _load_starts,
)

ARMS = ["baseline", "s12", "s28", "s20_mk2", "s24_k1_mk2"]
BUDGET = 50
N_ORBITS = 8


def _strided_subset(rows, n):
    """Spread across the freeze (not the first n lowest-μ seeds)."""
    if len(rows) <= n:
        return list(rows)
    step = max(len(rows) // n, 1)
    out = [rows[(i * step) % len(rows)] for i in range(n)]
    # de-dup if wrap collided
    seen = set()
    uniq = []
    for r in out:
        if r["name"] in seen:
            continue
        seen.add(r["name"])
        uniq.append(r)
    i = 0
    while len(uniq) < n and i < len(rows):
        if rows[i]["name"] not in seen:
            uniq.append(rows[i])
            seen.add(rows[i]["name"])
        i += 1
    return uniq


def main():
    rows = load_frozen()
    assert len(rows) >= N_ORBITS
    kinds = {r["kind"] for r in _strided_subset(rows, N_ORBITS)}
    print(f"frozen n={len(rows)} dataset={DATASET_NAME} "
          f"mini_kinds={sorted(kinds)}", flush=True)
    greedy_search_hcompact("X", "Y", 20, max_relator_length=32, config=None)

    tmp = Path(tempfile.mkdtemp(prefix="solved1hop_mini_"))
    try:
        # Write a tiny freeze-override by patching load_frozen via SUBSET on a
        # custom freeze is hard; instead pass SUBSET after replacing rows order
        # through a temp freeze file? Simpler: monkeypatch load_frozen.
        import experiments.heuristic_search.runners.run_solved1hop_scale as rs
        subset = _strided_subset(rows, N_ORBITS)
        _orig = rs.load_frozen
        rs.load_frozen = lambda: subset
        try:
            cfg = dict(
                DATASET=DATASET_NAME,
                ARMS=ARMS,
                NODE_BUDGET=BUDGET,
                CHECKPOINTS=[BUDGET],
                MAX_RELATOR_LENGTH=48,
                ENGINE="hcompact",
                KEEP_PATH=True,
                RESUME=False,
                OUT_STEM="mini_solved1hop",
                N_WORKERS=2,
                STAGE_DIR=str(tmp / "stage"),
            )
            t0 = time.perf_counter()
            out = run_solved1hop_scale(
                cfg, out_dir=str(tmp), heartbeat_secs=10**6,
                progress_secs=10**6)
            dt = time.perf_counter() - t0
        finally:
            rs.load_frozen = _orig

        got = [json.loads(l) for l in open(out) if l.strip()]
        print(f"wall={dt:.2f}s rows={len(got)} expected={N_ORBITS*len(ARMS)}",
              flush=True)
        assert len(got) == N_ORBITS * len(ARMS)
        # presentation-major: first len(ARMS) rows share one name
        first_name = got[0]["name"]
        assert all(got[i]["name"] == first_name for i in range(len(ARMS)))
        assert {got[i]["arm"] for i in range(len(ARMS))} == set(ARMS)
        for r in got:
            assert "nodes_explored" in r and "path_length" in r
            assert "path_moves" in r
            assert r["dataset"] == DATASET_NAME
            assert r["budget"] == BUDGET

        starts = {r["name"]: (r["r1"], r["r2"]) for r in subset}
        n_s, n_ok, fails = verify_file(out, starts)
        assert not fails, fails
        print(f"certs {n_ok}/{n_s} OK", flush=True)

        sizes = []
        for ci in range(1, 6):
            picked, tag = _stride_chunk(rows, 5, ci)
            sizes.append(len(picked))
            assert tag == f"_c{ci}of5"
        assert sum(sizes) == len(rows)
        print(f"chunk sizes {sizes} OK", flush=True)
        print("MINI OK", flush=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
