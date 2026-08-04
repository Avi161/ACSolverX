"""Tiny mock: 2 presentations, budget 50, check min_relator_length preserved."""
from __future__ import annotations

import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# allow running from /workspace or as experiments/... path
if not os.path.isdir(os.path.join(ROOT, "experiments")):
    ROOT = "/workspace"
sys.path.insert(0, ROOT)

from experiments.heuristic_search.runners import run_unsolved124_s20mk2 as ru  # noqa: E402
from experiments.heuristic_search.core.hcompact import greedy_search_hcompact  # noqa: E402


def main():
    tmpdir = tempfile.mkdtemp(prefix="u124mini_")
    cfg = dict(
        ARMS=["s20_mk2"], CHUNKS=1, CHUNK_INDEX=1,
        ENGINE="hcompact", N_WORKERS=1, KEEP_PATH=False,
        NODE_BUDGET=50, CHECKPOINTS=[50], MAX_RELATOR_LENGTH=64,
        RESUME=False, OUT_STEM="mini_u124", SUBSET=2,
    )
    out = ru.run_unsolved124_s20mk2(
        cfg, out_dir=tmpdir, heartbeat_secs=3600, progress_secs=3600)
    rows = [json.loads(l) for l in open(out)]
    print("jsonl", out)
    print("n_rows", len(rows))
    assert len(rows) == 2, rows
    for r in rows:
        direct = greedy_search_hcompact(
            r["r1"], r["r2"], 50, max_relator_length=64,
            config=ru.run_ab.ARMS["s20_mk2"])
        print(r["name"],
              "start", r["start_total"],
              "min_len", r["min_relator_length"],
              "min_pair", r["min_relator"],
              "delta", r["min_delta"],
              "improved", r["improved"],
              "oracle_min", direct["min_relator_length"],
              "oracle_pair", direct["min_relator"])
        assert r["min_relator_length"] == direct["min_relator_length"]
        assert r["min_relator"] == list(direct["min_relator"])
        assert r["min_delta"] == r["start_total"] - r["min_relator_length"]
        assert r["improved"] == (r["min_delta"] > 0)
        assert len(r["min_relator"][0]) + len(r["min_relator"][1]) == r["min_relator_length"]
        assert r["depth_tie"] == "+depth"
    print("MINI MOCK OK — min_relator_length + pair match hcompact oracle")


if __name__ == "__main__":
    main()
