"""Score ALL length-hard AC1M screen rows with pre-registered arms (resume-safe).

Writes ``arms_hard_full.jsonl`` (separate from the campaign's capped hard sample).

    python3 -m experiments.heuristic_search.runners.campaign_12h_hard_expand
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

from experiments.heuristic_search.runners.campaign_12h_anti_overfit import (  # noqa: E402
    ARMS, BUDGET, CAP, OUT_DIR, WALL_END, _append, _load_done, _remaining_s, _search,
)

SCREEN = os.path.join(OUT_DIR, "screen_length_ac1m.jsonl")
OUT = os.path.join(OUT_DIR, "arms_hard_full.jsonl")


def main():
    hard = []
    with open(SCREEN) as f:
        for line in f:
            r = json.loads(line)
            if not r["solved"]:
                hard.append(r)
    done = _load_done(OUT, ("arm", "src", "idx"))
    print(f"[hard-expand] {len(hard)} hard rows; {len(done)} cells done; "
          f"remain={_remaining_s()/3600:.2f}h", flush=True)
    _search("X", "Y", ARMS["length"])
    n_new = 0
    t0 = time.time()
    for rec in hard:
        if _remaining_s() <= 300:
            break
        for arm_name, cfg in ARMS.items():
            key = (arm_name, rec["src"], rec["idx"])
            if key in done:
                continue
            res = _search(rec["r1"], rec["r2"], cfg)
            row = {
                "arm": arm_name,
                "src": rec["src"],
                "idx": rec["idx"],
                "r1": rec["r1"],
                "r2": rec["r2"],
                "L": rec["L"],
                "band": "hard",
                "length_nodes": rec["nodes"],
                "length_solved": False,
                "solved": bool(res["solved"]),
                "nodes": int(res["nodes_explored"]),
                "path": int(res["path_length"]) if res["solved"] else None,
                "budget": BUDGET,
                "cap": CAP,
                "ts": datetime.now(timezone.utc).isoformat(),
            }
            _append(OUT, row)
            done.add(key)
            n_new += 1
            if n_new % 20 == 0:
                print(f"  +{n_new} {n_new/max(time.time()-t0,1e-6):.2f}/s "
                      f"remain={_remaining_s()/3600:.2f}h", flush=True)
    print(f"[hard-expand] done new={n_new} total_cells={len(done)}", flush=True)


if __name__ == "__main__":
    main()
