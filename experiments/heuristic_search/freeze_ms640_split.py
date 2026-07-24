"""Freeze a tune/eval split over the never-seen ms640 presentations, before anything is tuned on them.

EXP-26 established that 75 decidable-band presentations in ``data/ms640_solved.txt`` were never
read by any stage of this program, and scored the incumbent orderings on all 75. That was a clean
*evaluation*, and it used the rows up for that purpose only -- nothing was selected on them.

The next question needs them split. Every weight vector in this program was tuned on 40-45 rows of
the benchmark; that is a small training set, which is part of why a best-of-320 pick carried 1.65
presentations of optimism and why the search space saturated. With fresh presentations available,
a re-tune on *different and larger* data is worth trying -- but only if what it produces can be
judged on rows it did not see.

So: split the 75 into a tuning half and an evaluation half **now**, by presentation id, seeded and
write-once, before any config is fitted to any of them. Stratified by difficulty bin so both halves
span the range. The eval half is not read until a winner exists.

    python3 -m experiments.heuristic_search.freeze_ms640_split
"""
import json
import os
import sys
import collections

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import numpy as np                                                  # noqa: E402
from experiments.heuristic_search.hlab import LOGS                  # noqa: E402
from experiments.heuristic_search.exp26_clean_holdout import clean_rows  # noqa: E402

SEED = 20260724
OUT = os.path.join(LOGS, "splits_ms640.json")
TUNE_FRACTION = 2 / 3


def main():
    if os.path.exists(OUT):
        raise SystemExit(f"{OUT} exists -- frozen, must not be regenerated")

    rows = clean_rows()
    by_bin = collections.defaultdict(list)
    for r in rows:
        by_bin[r["bin"]].append(r["name"])

    rng = np.random.default_rng(SEED)
    tune, ev = [], []
    for b in sorted(by_bin):
        names = sorted(by_bin[b])            # deterministic before the seeded shuffle
        rng.shuffle(names)
        k = int(round(len(names) * TUNE_FRACTION))
        k = min(max(k, 1), len(names) - 1) if len(names) > 1 else len(names)
        tune += names[:k]
        ev += names[k:]

    payload = {
        "seed": SEED, "source": "data/ms640_solved.txt minus the 66-row benchmark",
        "note": ("Presentations no stage of this program read before EXP-26. Split BEFORE any "
                 "config was fitted to them. The eval half must not be read until a winner "
                 "exists, and never used to choose one."),
        "bins": [4, 5, 6, 7],
        "tune": sorted(tune), "eval": sorted(ev),
        "n_tune": len(tune), "n_eval": len(ev),
    }
    assert not (set(tune) & set(ev)), "tune/eval overlap"
    with open(OUT, "w") as f:
        json.dump(payload, f, indent=1)

    per = collections.Counter()
    for r in rows:
        per[(r["bin"], "tune" if r["name"] in set(tune) else "eval")] += 1
    print(f"tune {len(tune)}  eval {len(ev)}  (of {len(rows)})")
    for b in sorted(by_bin):
        print(f"  bin {b}: tune {per[(b,'tune')]}  eval {per[(b,'eval')]}")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
