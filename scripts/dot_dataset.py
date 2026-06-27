#!/usr/bin/env python3
"""Dataset prep for the d-o-t regressor: load archive -> features + class split.

Reads `data/dot_archive.jsonl` (one row per canonical class) and provides:
  - load_archive(path)         -> (labelled rows, censored rows)
  - featurize(rows)            -> (X float array, feature_names, keys)
  - make_splits(n, seed, frac) -> dict of train/val/test index arrays

Split is **by canonical class** (each archive row is already one class, so a row
split is a class split -- no two representatives of the same equivalence class
leak across folds). A fraction of the HARDEST classes (largest min d-o-t) is held
out as a frozen test band so we can measure generalization to the hard hump
separately (PLAN.md sec 6).

Scalar features only (cheap, the companion paper shows they carry signal); the
DRT model will instead consume the int8 presentation. Stdlib + numpy only.

Run standalone to materialize the split + a summary:
    ../.venv/bin/python scripts/dot_dataset.py
"""

import json
import os

import numpy as np

ARCHIVE = "data/dot_archive.jsonl"
SPLIT_NPZ = "data/dot_splits.npz"


def load_archive(path=ARCHIVE):
    """Return (labelled, censored) lists of dict rows."""
    labelled, censored = [], []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            (censored if r["censored"] else labelled).append(r)
    return labelled, censored


def _relator_feats(r):
    """(length, x-exponent-sum, y-exponent-sum, #x-letters, #y-letters)."""
    nx, nX, ny, nY = r.count("x"), r.count("X"), r.count("y"), r.count("Y")
    return [len(r), nx - nX, ny - nY, nx + nX, ny + nY]


FEATURE_NAMES = [
    "len_r1", "xexp_r1", "yexp_r1", "nx_r1", "ny_r1",
    "len_r2", "xexp_r2", "yexp_r2", "nx_r2", "ny_r2",
    "total_len", "len_diff", "len_max", "len_min",
]


def featurize(rows):
    """rows -> (X [n, F] float32, feature_names, keys list of 'r1|r2')."""
    X, keys = [], []
    for r in rows:
        f1 = _relator_feats(r["r1"])
        f2 = _relator_feats(r["r2"])
        l1, l2 = f1[0], f2[0]
        X.append(f1 + f2 + [l1 + l2, abs(l1 - l2), max(l1, l2), min(l1, l2)])
        keys.append(r["r1"] + "|" + r["r2"])
    return np.asarray(X, dtype=np.float32), list(FEATURE_NAMES), keys


def make_splits(dots, seed=0, val_frac=0.1, test_frac=0.1, hard_frac=0.05):
    """Index arrays for train / val / test / hard_test (by class = by row).

    The top `hard_frac` of classes by d-o-t become a frozen `hard_test` band
    (never trained on); the rest is shuffled into train/val/test.
    """
    dots = np.asarray(dots)
    n = len(dots)
    rng = np.random.default_rng(seed)

    order = np.argsort(-dots, kind="stable")        # hardest first
    n_hard = int(round(hard_frac * n))
    hard_test = order[:n_hard]
    rest = order[n_hard:]
    rng.shuffle(rest)

    n_test = int(round(test_frac * n))
    n_val = int(round(val_frac * n))
    test = rest[:n_test]
    val = rest[n_test:n_test + n_val]
    train = rest[n_test + n_val:]
    return {"train": np.sort(train), "val": np.sort(val),
            "test": np.sort(test), "hard_test": np.sort(hard_test)}


def main():
    if not os.path.exists(ARCHIVE):
        raise SystemExit(f"not found: {ARCHIVE} (run build_dot_archive.py first)")
    labelled, censored = load_archive()
    X, names, keys = featurize(labelled)
    dots = np.asarray([r["min_dot"] for r in labelled], dtype=np.float32)
    total_len = np.asarray([r["total_len"] for r in labelled], dtype=np.float32)
    splits = make_splits(dots)

    np.savez_compressed(
        SPLIT_NPZ, X=X, dot=dots, total_len=total_len,
        feature_names=np.array(names),
        train=splits["train"], val=splits["val"],
        test=splits["test"], hard_test=splits["hard_test"],
        keys=np.array(keys),
    )
    print(f"labelled classes : {len(labelled)}   censored: {len(censored)}")
    print(f"features         : {len(names)}  -> {names}")
    for k, v in splits.items():
        d = dots[v]
        print(f"  {k:10s}: {len(v):6d}   d-o-t mean {d.mean():5.2f}  "
              f"median {np.median(d):4.0f}  max {int(d.max())}")
    print(f"wrote {SPLIT_NPZ}")


if __name__ == "__main__":
    main()
