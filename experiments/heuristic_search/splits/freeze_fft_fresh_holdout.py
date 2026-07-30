"""Carve a fresh Aut-disjoint 60-orbit holdout for the FFT/sign-lag scout.

Disjoint from spent ``splits_ac1m_hard_aut`` train+holdout (180) and from
``solved_1hop_autclean`` Aut reps. Write-once.

    python3 -m experiments.heuristic_search.splits.freeze_fft_fresh_holdout
"""
from __future__ import annotations

import json
import os
import random
import sys
from datetime import datetime, timezone

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

from experiments.stable_ac.cov.ladder.autcanon_fast import aut_min, warm  # noqa: E402

ROOT = _d
ORBITS = os.path.join(ROOT, "results", "heuristic_search", "splits",
                      "ac1m_hard_orbits.jsonl")
SPENT = os.path.join(ROOT, "results", "heuristic_search", "splits",
                     "splits_ac1m_hard_aut.json")
AUTCLEAN = os.path.join(ROOT, "results", "heuristic_search", "splits",
                        "solved_1hop_autclean.json")
OUT = os.path.join(ROOT, "results", "heuristic_search", "splits",
                   "splits_fft_fresh_holdout60.json")
SEED = 20260730
N_HOLD = 60


def _rep_key(r1, r2):
    return r1 + "\0" + r2


def main():
    if os.path.exists(OUT):
        raise SystemExit(f"refusing to overwrite {OUT}")
    warm()
    exclude = set()
    sp = json.load(open(SPENT))
    for side in ("train_rows", "holdout_rows"):
        for r in sp[side]:
            exclude.add(_rep_key(r["aut_rep_r1"], r["aut_rep_r2"]))
    for r in json.load(open(AUTCLEAN))["rows"]:
        exclude.add(_rep_key(r["aut_rep_r1"], r["aut_rep_r2"]))

    pool = []
    seen = set()
    for line in open(ORBITS):
        r = json.loads(line)
        key = _rep_key(r["aut_rep_r1"], r["aut_rep_r2"])
        if key in exclude or key in seen:
            continue
        seen.add(key)
        pool.append(r)
    rng = random.Random(SEED)
    rng.shuffle(pool)
    # stratify lightly by L buckets
    by_L = {}
    for r in pool:
        by_L.setdefault(int(r["L"]) // 5, []).append(r)
    hold = []
    keys = sorted(by_L)
    i = 0
    while len(hold) < N_HOLD and keys:
        b = keys[i % len(keys)]
        if by_L[b]:
            hold.append(by_L[b].pop())
        else:
            keys.remove(b)
            continue
        i += 1
    assert len(hold) == N_HOLD
    out = {
        "kind": "fft_fresh_holdout60",
        "created": datetime.now(timezone.utc).isoformat(),
        "seed": SEED,
        "n_holdout": N_HOLD,
        "n_pool_available": len(pool),
        "excluded_spent_ac1m_aut": 180,
        "note": ("Virgin Aut-disjoint holdout for FFT/sign-lag scout. "
                 "Selection stays on ac1m_hard_aut train 120."),
        "selected_on": "splits_ac1m_hard_aut train_rows (120)",
        "evaluated_on": "this freeze",
        "holdout_rows": hold,
    }
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    print(f"[freeze] wrote {OUT}: {N_HOLD} rows from pool {len(pool)}",
          flush=True)


if __name__ == "__main__":
    main()
