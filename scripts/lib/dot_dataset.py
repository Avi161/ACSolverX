#!/usr/bin/env python3
"""Dataset prep for the d-o-t regressor: load archive -> features + class split.

Reads `data/dot_archive.jsonl` (one row per canonical class) and provides:
  - load_archive(path)         -> (labelled rows, censored rows)
  - featurize(rows)            -> (X float array, feature_names, keys)
  - make_splits(n, seed, frac) -> dict of train/val/test index arrays   (v1, legacy)
  - make_splits_v2(rows, ...)  -> dict of the 5 v2 folds                 (Phase 7)
  - emit_splits_v2(...)        -> write data/derived/labels/dot_splits_v2.npz

Split is **by canonical class** (each archive row is already one class, so a row
split is a class split -- no two representatives of the same equivalence class
leak across folds). A fraction of the HARDEST classes (largest min d-o-t) is held
out as a frozen test band so we can measure generalization to the hard hump
separately (PLAN.md sec 6).

Scalar features only (cheap, the companion paper shows they carry signal); the
DRT model will instead consume the int8 presentation. Stdlib + numpy only.

Run standalone to materialize the split + a summary:
    ../.venv/bin/python scripts/lib/dot_dataset.py        # v1 (legacy) -> dot_splits.npz
    ../.venv/bin/python scripts/lib/dot_dataset.py v2     # Phase 7     -> dot_splits_v2.npz

v1 (`make_splits` / `main`) is UNTOUCHED -- `dot_splits.npz` stays byte-identical.
v2 is purely additive (4.0.DETAILED_STEPS_DATA_CRAFTING.md Phase 7).
"""

import json
import os

import numpy as np

ARCHIVE = "data/derived/labels/dot_archive.jsonl"
SPLIT_NPZ = "data/derived/labels/dot_splits.npz"

# Phase 7: the look-alike probe (solved, d-o-t 12) pinned to TRAIN -- canon_key of
# ("YXyxYx","xxxYYYY"); regression-pinned to match build_training_archive / test_phase1.
# Differs from AK(3) "YXYxyx|YYYYxxx" only in r1 (Finding 2). numpy-only module, so the
# key is a literal here rather than importing canon.
LOOKALIKE_KEY = "YXyxYx|YYYYxxx"


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


# ---------------------------------------------------------------------------
# Phase 7 -- v2 splits (additive; make_splits above is untouched)
# ---------------------------------------------------------------------------

def _load_rows_in_order(path):
    """All v2-archive rows as dicts, in FILE order (deterministic npz row order)."""
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def make_splits_v2(rows, *, seed=0, hard_frac=0.05, val_frac=0.10, test_frac=0.10,
                   lookalike_key=LOOKALIKE_KEY):
    """Five frozen folds over the v2 archive rows (one canonical class per row, file order).

    Folds (4.0.DETAILED_STEPS_DATA_CRAFTING.md Phase 7):
      counterexample_eval = tier=="named" ONLY (the 8 AK(n)+Length-14 anchors). Frozen,
                            never trained. SUPERSEDES 3-§5 ("named + 8 cousins"): USER DECISION.
      hard_test           = top `hard_frac` of LABELLED rows by d-o-t (upper-bound label).
                            Frozen; ranking-only metric (loose-label + heteroscedastic -- lead
                            with Spearman, never MAE).
      train pins          = the look-alike probe + ALL group=="short_hard" cousins, forced to
                            TRAIN so short_hard x3 actually fires and the assertion is
                            deterministic. Cost: every val/test censored row is then len 14-17
                            (held-out short-hard hinge calibration forgone; only 8 cousins exist).
      train/val/test      = 80/10/10 of the REMAINDER (all rows minus the two frozen folds),
                            pinned rows appended to train.

    Deterministic: the shuffle pool is built in file/index order before rng.shuffle; hard_test
    ranks labelled-only by (-d-o-t, index) so NaN/None never enters the sort. Returns a dict of
    five sorted int64 index arrays that exhaustively partition range(len(rows)).
    """
    n = len(rows)
    keys = [f"{r['r1']}|{r['r2']}" for r in rows]
    tiers = [r["tier"] for r in rows]
    groups = [r.get("group", "") for r in rows]
    censored = [bool(r["censored"]) for r in rows]
    dots = [r["min_dot"] for r in rows]   # int for labelled, None for censored/named

    # counterexample_eval: the named anchors only
    eval_idx = [i for i in range(n) if tiers[i] == "named"]

    # hard_test: top hard_frac of LABELLED rows by d-o-t (None never enters the key)
    labelled_idx = [i for i in range(n) if not censored[i]]            # file order
    lab_ranked = sorted(labelled_idx, key=lambda i: (-dots[i], i))     # hardest first, tie by idx
    n_hard = int(round(hard_frac * len(labelled_idx)))
    hard_test = lab_ranked[:n_hard]

    frozen = set(eval_idx) | set(hard_test)                            # eval/hard_test disjoint

    # remainder = everything except the two frozen folds, in file/index order
    remainder = [i for i in range(n) if i not in frozen]
    n_rem = len(remainder)

    # pin to train: look-alike probe + every short_hard cousin (all live in the remainder)
    pin = [i for i in remainder if keys[i] == lookalike_key or groups[i] == "short_hard"]
    pin_set = set(pin)
    pool = np.array([i for i in remainder if i not in pin_set], dtype=np.int64)  # index order

    rng = np.random.default_rng(seed)
    rng.shuffle(pool)

    # 80/10/10 of the REMAINDER (not of n): keeps the documented fractions exact
    n_test = int(round(test_frac * n_rem))
    n_val = int(round(val_frac * n_rem))
    test = pool[:n_test]
    val = pool[n_test:n_test + n_val]
    train = np.concatenate([pool[n_test + n_val:], np.array(pin, dtype=np.int64)])

    return {
        "train": np.sort(train),
        "val": np.sort(val),
        "test": np.sort(test),
        "hard_test": np.sort(np.array(hard_test, dtype=np.int64)),
        "counterexample_eval": np.sort(np.array(eval_idx, dtype=np.int64)),
    }


def emit_splits_v2(archive=None, out=None, seed=None):
    """Featurize the v2 archive (file order) + make_splits_v2 -> write dot_splits_v2.npz.

    Aligned per-row arrays (same row order as X): dot (NaN for censored/named), total_len,
    weight, bound_B (NaN for null), loss_type/tier/group (str), keys; plus the 5 fold index
    arrays. Returns (splits, rows) for tests. dot_splits.npz (v1) is never touched.
    """
    try:                                              # package import (tests / build scripts)
        from scripts.lib import dot_config as cfg
    except ImportError:                               # flat import (run as a script from scripts/lib)
        import dot_config as cfg
    archive = archive or cfg.ARCHIVE_V2
    out = out or cfg.SPLIT_NPZ_V2
    seed = cfg.SEED if seed is None else seed

    if not os.path.exists(archive):
        raise SystemExit(f"not found: {archive} (run build_training_archive.py first)")

    rows = _load_rows_in_order(archive)
    X, names, keys = featurize(rows)
    dot = np.asarray([r["min_dot"] if r["min_dot"] is not None else np.nan
                      for r in rows], dtype=np.float32)
    total_len = np.asarray([r["total_len"] for r in rows], dtype=np.float32)
    weight = np.asarray([r["weight"] for r in rows], dtype=np.float32)
    bound_B = np.asarray([r["bound_B"] if r["bound_B"] is not None else np.nan
                          for r in rows], dtype=np.float32)
    loss_type = np.asarray([r["loss_type"] for r in rows])
    tier = np.asarray([r["tier"] for r in rows])
    group = np.asarray([r.get("group", "") for r in rows])

    splits = make_splits_v2(rows, seed=seed)

    np.savez_compressed(
        out, X=X, dot=dot, total_len=total_len,
        feature_names=np.array(names), keys=np.array(keys),
        train=splits["train"], val=splits["val"], test=splits["test"],
        hard_test=splits["hard_test"], counterexample_eval=splits["counterexample_eval"],
        weight=weight, bound_B=bound_B, loss_type=loss_type, tier=tier, group=group,
    )
    print(f"v2 rows          : {len(rows)}   features: {len(names)}")
    for k in ("train", "val", "test", "hard_test", "counterexample_eval"):
        v = splits[k]
        d = dot[v]
        finite = d[np.isfinite(d)]
        med = f"{np.median(finite):.0f}" if finite.size else "--"
        mx = f"{int(np.max(finite))}" if finite.size else "--"
        print(f"  {k:20s}: {len(v):6d}   labelled {finite.size:6d}  median {med:>4}  max {mx:>4}")
    print(f"wrote {out}")
    return splits, rows


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
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "v2":
        emit_splits_v2()                              # Phase 7 -> dot_splits_v2.npz
    else:
        main()                                        # v1 (legacy) -> dot_splits.npz
