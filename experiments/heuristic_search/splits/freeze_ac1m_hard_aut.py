"""Freeze an Aut-disjoint train/holdout split of AC1M length-hard orbits.

AC1M has no parent-AC19 field; Aut-twins are detected via ``aut_min``.
We dedup length-hard screen rows by Aut-rep, exclude orbits already used
for S-selection (s_grid 800 + prior fresh_hard/l_stratified slices), then
stratify by L and freeze a write-once 2:1 train:holdout of orbits.

    python3 -m experiments.heuristic_search.splits.freeze_ac1m_hard_aut
"""
from __future__ import annotations

import json
import os
import random
import sys
from collections import defaultdict
from datetime import datetime, timezone

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

from experiments.stable_ac.cov.ladder.autcanon_fast import aut_min, warm  # noqa: E402

ROOT = _d
SCREEN = os.path.join(ROOT, "results", "heuristic_search", "campaign_12h",
                      "screen_length_ac1m.jsonl")
S_GRID = os.path.join(ROOT, "results", "heuristic_search", "campaign_12h",
                      "s_grid_hard.jsonl")
SLICE_H = os.path.join(ROOT, "results", "heuristic_search", "scale10k",
                       "slice_fresh_hard.json")
SLICE_L = os.path.join(ROOT, "results", "heuristic_search", "scale10k",
                       "slice_l_stratified.json")
OUT_DIR = os.path.join(ROOT, "results", "heuristic_search", "splits")
ORBITS = os.path.join(OUT_DIR, "ac1m_hard_orbits.jsonl")
SPLIT = os.path.join(OUT_DIR, "splits_ac1m_hard_aut.json")

SEED = 20260729
N_TRAIN = 120
N_HOLD = 60


def _rep_key(rep):
    return rep[0] + "\0" + rep[1]


def main():
    if os.path.exists(SPLIT):
        raise SystemExit(f"refusing to overwrite existing freeze: {SPLIT}")

    os.makedirs(OUT_DIR, exist_ok=True)
    warm()

    # Orbits already used for selection / scouts — exclude from BOTH sides.
    exclude_reps = set()
    for path in (S_GRID,):
        for line in open(path):
            r = json.loads(line)
            mu, rep = aut_min((r["r1"], r["r2"]))
            exclude_reps.add(_rep_key(rep))
    for path in (SLICE_H, SLICE_L):
        for r in json.load(open(path))["rows"]:
            mu, rep = aut_min((r["r1"], r["r2"]))
            exclude_reps.add(_rep_key(rep))
    print(f"[freeze] excluded orbits from prior selection: {len(exclude_reps)}",
          flush=True)

    # Stamp all length-hard screen rows; keep one per Aut-rep (min idx).
    best = {}  # rep_key -> row
    n_hard = 0
    if os.path.exists(ORBITS):
        print(f"[freeze] loading existing {ORBITS}", flush=True)
        for line in open(ORBITS):
            r = json.loads(line)
            best[_rep_key((r["aut_rep_r1"], r["aut_rep_r2"]))] = r
            n_hard += r.get("n_screen_dupes", 1)
    else:
        with open(ORBITS, "w") as out:
            for line in open(SCREEN):
                r = json.loads(line)
                if r.get("solved"):
                    continue
                n_hard += 1
                mu, rep = aut_min((r["r1"], r["r2"]))
                key = _rep_key(rep)
                prev = best.get(key)
                if prev is None or r["idx"] < prev["idx"]:
                    row = {
                        "idx": r["idx"],
                        "r1": r["r1"],
                        "r2": r["r2"],
                        "L": r["L"],
                        "mu": mu,
                        "aut_rep_r1": rep[0],
                        "aut_rep_r2": rep[1],
                        "n_screen_dupes": 1 if prev is None else prev["n_screen_dupes"] + 1,
                    }
                    # if replacing, bump dupe count from prev
                    if prev is not None:
                        row["n_screen_dupes"] = prev["n_screen_dupes"] + 1
                    best[key] = row
                else:
                    prev["n_screen_dupes"] = prev.get("n_screen_dupes", 1) + 1
                if n_hard % 500 == 0:
                    print(f"  stamped {n_hard} hard rows → {len(best)} orbits",
                          flush=True)
            for row in sorted(best.values(), key=lambda r: r["idx"]):
                out.write(json.dumps(row) + "\n")
        print(f"[freeze] wrote {ORBITS}: {len(best)} unique hard orbits "
              f"from {n_hard} screen rows", flush=True)

    # reload best from ORBITS for consistency
    best = {}
    for line in open(ORBITS):
        r = json.loads(line)
        best[_rep_key((r["aut_rep_r1"], r["aut_rep_r2"]))] = r

    pool = [r for k, r in best.items() if k not in exclude_reps]
    print(f"[freeze] pool after exclusion: {len(pool)} orbits", flush=True)
    if len(pool) < N_TRAIN + N_HOLD:
        raise RuntimeError(f"pool too small: {len(pool)} < {N_TRAIN+N_HOLD}")

    # Stratify by L, within-bucket shuffle, take ~2:1
    by_L = defaultdict(list)
    for r in pool:
        by_L[int(r["L"])].append(r)
    rng = random.Random(SEED)
    for L in by_L:
        rng.shuffle(by_L[L])

    train, hold = [], []
    # round-robin buckets largest-first for balance
    buckets = sorted(by_L.keys(), key=lambda L: -len(by_L[L]))
    # target ratio 2:1
    while len(train) < N_TRAIN or len(hold) < N_HOLD:
        progress = False
        for L in buckets:
            bucket = by_L[L]
            if not bucket:
                continue
            # prefer filling train 2:1
            if len(train) < N_TRAIN and (
                    len(hold) == 0 or len(train) / max(len(hold), 1) < 2.0
                    or len(hold) >= N_HOLD):
                train.append(bucket.pop())
                progress = True
            elif len(hold) < N_HOLD:
                hold.append(bucket.pop())
                progress = True
            if len(train) >= N_TRAIN and len(hold) >= N_HOLD:
                break
        if not progress:
            break

    train = train[:N_TRAIN]
    hold = hold[:N_HOLD]
    train_reps = {_rep_key((r["aut_rep_r1"], r["aut_rep_r2"])) for r in train}
    hold_reps = {_rep_key((r["aut_rep_r1"], r["aut_rep_r2"])) for r in hold}
    if train_reps & hold_reps:
        raise RuntimeError("Aut leak between train and holdout")
    if train_reps & exclude_reps or hold_reps & exclude_reps:
        raise RuntimeError("selection-set contamination")

    payload = {
        "seed": SEED,
        "kind": "ac1m_hard_aut_disjoint",
        "created": datetime.now(timezone.utc).isoformat(),
        "n_train": len(train),
        "n_holdout": len(hold),
        "train_idxs": [r["idx"] for r in train],
        "holdout_idxs": [r["idx"] for r in hold],
        "train_reps": [[r["aut_rep_r1"], r["aut_rep_r2"]] for r in train],
        "holdout_reps": [[r["aut_rep_r1"], r["aut_rep_r2"]] for r in hold],
        "train_rows": train,
        "holdout_rows": hold,
        "excluded_prior_selection_orbits": len(exclude_reps),
        "selected_on": "train_idxs only",
        "evaluated_on": "holdout_idxs only — one read after winner frozen",
        "note": "Aut-deduped AC1M length-hard; 2:1 train:holdout stratified by L; "
                "zero Aut overlap; prior s_grid/fresh_hard/l_stratified orbits excluded.",
    }
    with open(SPLIT, "w") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")
    print(f"[freeze] wrote {SPLIT}", flush=True)
    print(f"  train={len(train)} holdout={len(hold)} "
          f"overlap={len(train_reps & hold_reps)}", flush=True)
    print(f"  train L hist: "
          + str(sorted(Counter_L(train).items())), flush=True)
    print(f"  hold  L hist: "
          + str(sorted(Counter_L(hold).items())), flush=True)


def Counter_L(rows):
    from collections import Counter
    return Counter(int(r["L"]) for r in rows)


if __name__ == "__main__":
    main()
