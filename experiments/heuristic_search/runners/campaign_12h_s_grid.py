"""Pre-registered S-weight grid on AC1M hard band with held-out half.

Weights frozen before any AC1M hard peek: {4, 8.458, 12, 16, 20, 24, 32, 40}.
Even idx → select half (report only); odd idx → holdout (verdict).
No fitting beyond reading which frozen weight wins on select; holdout is the number.

    python3 -m experiments.heuristic_search.runners.campaign_12h_s_grid
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

from experiments.heuristic_search.core.hfast import search_fast  # noqa: E402
from experiments.heuristic_search.runners.campaign_12h_anti_overfit import (  # noqa: E402
    BUDGET, CAP, OUT_DIR, WALL_END, _append, _load_done, _remaining_s,
)

SCREEN = os.path.join(OUT_DIR, "screen_length_ac1m.jsonl")
OUT = os.path.join(OUT_DIR, "s_grid_hard.jsonl")
WEIGHTS = (4.0, 8.458, 12.0, 16.0, 20.0, 24.0, 32.0, 40.0)


def cfg(w):
    return {"segments": [{"upto": None, "w": {"L": 1.0, "S": float(w)}}]}


def main():
    hard = []
    with open(SCREEN) as f:
        for line in f:
            r = json.loads(line)
            if not r["solved"]:
                hard.append(r)
    # use first 800 hard for speed if huge; deterministic
    hard = sorted(hard, key=lambda r: r["idx"])[:800]
    done = _load_done(OUT, ("w", "idx"))
    print(f"[s-grid] {len(hard)} hard; {len(done)} done; remain={_remaining_s()/3600:.2f}h",
          flush=True)
    search_fast("X", "Y", 20, cfg(24.0), CAP)
    n_new = 0
    t0 = time.time()
    for rec in hard:
        if _remaining_s() <= 400:
            break
        for w in WEIGHTS:
            key = (w, rec["idx"])
            if key in done:
                continue
            res = search_fast(rec["r1"], rec["r2"], BUDGET, cfg(w), CAP)
            half = "select" if (rec["idx"] % 2 == 0) else "holdout"
            row = {
                "w": w,
                "idx": rec["idx"],
                "half": half,
                "r1": rec["r1"],
                "r2": rec["r2"],
                "L": rec["L"],
                "solved": bool(res["solved"]),
                "nodes": int(res["nodes"]),
                "path": res["path_length"],
                "budget": BUDGET,
                "cap": CAP,
                "ts": datetime.now(timezone.utc).isoformat(),
            }
            if int(res["nodes"]) > BUDGET:
                raise RuntimeError("budget")
            _append(OUT, row)
            done.add(key)
            n_new += 1
            if n_new % 40 == 0:
                print(f"  +{n_new} {n_new/max(time.time()-t0,1e-6):.2f}/s "
                      f"remain={_remaining_s()/3600:.2f}h", flush=True)
    print(f"[s-grid] done new={n_new}", flush=True)


if __name__ == "__main__":
    main()
