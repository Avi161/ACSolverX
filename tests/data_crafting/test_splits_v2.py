"""Gate-style tests for Phase 7 of the data-crafting pipeline (dot_dataset.make_splits_v2 /
emit_splits_v2). No pytest; matches the scripts/tests/test_phase1.py +
test_build_training_archive.py idiom.

Run from the repo root:
    ../.venv/bin/python tests/data_crafting/test_splits_v2.py

Prints each check; exits non-zero with 'SPLITS-V2 TESTS FAILED' on any failure, else prints
'SPLITS-V2 TESTS PASS'. The five folds are **re-derived independently** of make_splits_v2 for
the deterministic parts (named eval, top-5% hard_test, the train pins, sizes, partition,
disjointness); the only stochastic part (the train/val/test shuffle) is checked for structure
(pins forced to train, fractions on the REMAINDER base) and self-consistent reproducibility.
dot_splits.npz (v1) is hashed before/after to prove emit_splits_v2 never touches it.

Phase-7 acceptance (4.0.DETAILED_STEPS_DATA_CRAFTING.md §7 + Field-Advisor d.5):
  counterexample_eval = tier=="named" ONLY (8); hard_test = top-5% labelled by d-o-t (frozen);
  look-alike + 8 short_hard cousins pinned to TRAIN; train/val/test = 80/10/10 of the REMAINDER
  (36,705), pins removed from the pool before the cut; no key in two folds; mean(weight)~1;
  byte-identical re-emit; dot_splits.npz unchanged.
"""
import os
import sys
import json
import hashlib
import itertools

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))  # repo root
from scripts.lib import canon              # noqa: E402
from scripts.lib import dot_config as cfg  # noqa: E402
from scripts.lib import dot_dataset as dd  # noqa: E402

AK3_KEY = "YXYxyx|YYYYxxx"
LOOKALIKE_KEY = "YXyxYx|YYYYxxx"

failures = []


def check(name, cond, extra=""):
    ok = bool(cond)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"   -- {extra}" if extra else ""))
    if not ok:
        failures.append(name)


def _sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def _independent_folds(rows, seed=0, hard_frac=0.05, val_frac=0.10, test_frac=0.10):
    """Re-derive the frozen structure WITHOUT calling make_splits_v2 (own code path).

    Returns (eval_idx, hard_test, pins, n_rem, n_test, n_val, n_hard) -- the deterministic
    pieces. The train/val/test shuffle itself is reproducible only via the same rng, so it is
    cross-checked structurally in the caller, not re-derived here.
    """
    n = len(rows)
    keys = [f"{r['r1']}|{r['r2']}" for r in rows]
    eval_idx = sorted(i for i in range(n) if rows[i]["tier"] == "named")
    labelled = [i for i in range(n) if not rows[i]["censored"]]
    ranked = sorted(labelled, key=lambda i: (-rows[i]["min_dot"], i))
    n_hard = int(round(hard_frac * len(labelled)))
    hard_test = sorted(ranked[:n_hard])
    frozen = set(eval_idx) | set(hard_test)
    remainder = [i for i in range(n) if i not in frozen]
    n_rem = len(remainder)
    pins = sorted(i for i in remainder
                  if keys[i] == LOOKALIKE_KEY or rows[i].get("group", "") == "short_hard")
    n_test = int(round(test_frac * n_rem))
    n_val = int(round(val_frac * n_rem))
    return eval_idx, hard_test, pins, n_rem, n_test, n_val, n_hard


def run_tests():
    print("== Phase 7: make_splits_v2 / emit_splits_v2 ==")

    archive = cfg.ARCHIVE_V2
    rows = dd._load_rows_in_order(archive)
    n = len(rows)
    keys = [f"{r['r1']}|{r['r2']}" for r in rows]
    check("v2 archive loads (38,384 rows in file order)", n == 38384, f"n={n}")

    sp = dd.make_splits_v2(rows, seed=cfg.SEED)
    folds = ("train", "val", "test", "hard_test", "counterexample_eval")
    fset = {f: set(sp[f].tolist()) for f in folds}
    kset = {f: {keys[i] for i in sp[f]} for f in folds}

    # --- exhaustive partition + pairwise index-disjoint ---
    allidx = np.concatenate([sp[f] for f in folds])
    check("folds exhaustively partition range(n) (union == n, all unique)",
          len(allidx) == n and len(set(allidx.tolist())) == n)
    idx_overlap = {f"{a}&{b}": len(fset[a] & fset[b])
                   for a, b in itertools.combinations(folds, 2) if fset[a] & fset[b]}
    check("no row index in two folds", not idx_overlap, str(idx_overlap))
    key_overlap = {f"{a}&{b}": len(kset[a] & kset[b])
                   for a, b in itertools.combinations(folds, 2) if kset[a] & kset[b]}
    check("no canonical key in two folds", not key_overlap, str(key_overlap))

    # --- independent re-derivation of the frozen structure + sizes (FA d.5: correct base) ---
    ev, ht, pins, n_rem, n_test, n_val, n_hard = _independent_folds(rows, seed=cfg.SEED)
    check("counterexample_eval == independently-derived named set", fset["counterexample_eval"] == set(ev))
    check("hard_test == independently-derived top-5% labelled-by-dot", fset["hard_test"] == set(ht))
    check("eval size == 8", len(sp["counterexample_eval"]) == 8, f"got {len(sp['counterexample_eval'])}")
    check("hard_test size == round(.05*labelled) == 1671",
          len(sp["hard_test"]) == n_hard == 1671, f"n_hard={n_hard}")
    check("remainder base == 36705 (n - eval - hard_test)", n_rem == 36705, f"n_rem={n_rem}")
    check("val/test sized on the REMAINDER (10% of 36705 == 3670), not on n",
          len(sp["val"]) == n_val == 3670 and len(sp["test"]) == n_test == 3670,
          f"val={len(sp['val'])} test={len(sp['test'])} n_val={n_val}")
    check("train size == n_rem - n_test - n_val == 29365 (pins net-zero: removed then re-added)",
          len(sp["train"]) == n_rem - n_test - n_val == 29365, f"train={len(sp['train'])}")

    # --- pins forced to train and EXCLUDED from the val/test draw (FA d.5) ---
    pin_keys = {keys[i] for i in pins}
    check("9 pins identified (look-alike + 8 short_hard cousins)", len(pins) == 9, f"pins={len(pins)}")
    check("every pin is in train", set(pins) <= fset["train"])
    check("no pin leaked into val/test/hard_test/eval (was removed from the shuffle pool)",
          not any(set(pins) & fset[f] for f in ("val", "test", "hard_test", "counterexample_eval")))

    # --- look-alike trap + AK(3) placement (Finding 2) ---
    def where_key(k):
        return [f for f in folds if k in kset[f]]
    check("AK(3) in counterexample_eval ONLY (frozen, never trained)",
          where_key(AK3_KEY) == ["counterexample_eval"], str(where_key(AK3_KEY)))
    check("look-alike in train ONLY (pinned, not eval/hard_test)",
          where_key(LOOKALIKE_KEY) == ["train"], str(where_key(LOOKALIKE_KEY)))
    trap = json.load(open(cfg.TRAP_SET_JSON))
    named_keys = set(trap["groups"]["named"].values())
    cousin_keys = set(trap["groups"]["short_hard"])
    check("all 8 named keys in counterexample_eval", named_keys <= kset["counterexample_eval"])
    check("all 8 short_hard cousins in train (and nowhere else)",
          cousin_keys <= kset["train"]
          and not any(cousin_keys & kset[f] for f in folds if f != "train"))

    # --- counterexample_eval is all named tier; hard_test all labelled ---
    check("every counterexample_eval row has tier=='named'",
          all(rows[i]["tier"] == "named" for i in sp["counterexample_eval"]))
    check("every hard_test row is labelled (censored==False, finite d-o-t)",
          all((not rows[i]["censored"]) and rows[i]["min_dot"] is not None for i in sp["hard_test"]))

    # --- censored present in train, val, test (the hinge is trained AND measured) ---
    cens_in = {f: sum(1 for i in sp[f] if rows[i]["censored"]) for f in ("train", "val", "test")}
    check("censored rows present in train, val, AND test", all(c > 0 for c in cens_in.values()), str(cens_in))

    # --- mean(weight) ~ 1 over the FULL archive (Phase-5 invariant, NOT a per-fold property) ---
    w = np.asarray([r["weight"] for r in rows], dtype=np.float64)
    check("mean(weight) ~ 1.0 over the full archive (Phase-5 invariant)",
          abs(w.mean() - 1.0) < 0.01, f"mean={w.mean():.5f}")
    check("all weights finite and > 0", np.all(np.isfinite(w)) and np.all(w > 0))

    # --- the emitted npz: aligned-array lengths + dtypes + null encoding ---
    print("[emit + npz schema]")
    os.makedirs(".scratch", exist_ok=True)
    out_a = os.path.join(".scratch", "splits_v2_a.npz")
    out_b = os.path.join(".scratch", "splits_v2_b.npz")
    try:
        sha_v1_pre = _sha("data/derived/labels/dot_splits.npz")
        sp_a, rows_a = dd.emit_splits_v2(out=out_a)
        sha_v1_post = _sha("data/derived/labels/dot_splits.npz")
        check("emit_splits_v2 does NOT touch dot_splits.npz (v1 byte-unchanged)",
              sha_v1_pre == sha_v1_post)

        z = np.load(out_a, allow_pickle=False)
        expected_arrays = {"X", "dot", "total_len", "feature_names", "keys", "train", "val",
                           "test", "hard_test", "counterexample_eval", "weight", "bound_B",
                           "loss_type", "tier", "group"}
        check("npz has exactly the 15 expected arrays", set(z.files) == expected_arrays,
              str(set(z.files) ^ expected_arrays))
        nX = z["X"].shape[0]
        aligned = ["dot", "total_len", "keys", "weight", "bound_B", "loss_type", "tier", "group"]
        check("X is (n, 14)", z["X"].shape == (n, 14), str(z["X"].shape))
        check("every aligned per-row array has length n == X.shape[0]",
              all(z[a].shape[0] == nX == n for a in aligned),
              str({a: z[a].shape[0] for a in aligned if z[a].shape[0] != n}))
        check("feature_names has 14 entries", z["feature_names"].shape[0] == 14)

        # null encoding: dot NaN iff censored/named; bound_B NaN iff labelled
        dot = z["dot"]; bB = z["bound_B"]; tier = z["tier"]
        cens = np.array([r["censored"] for r in rows_a])
        check("dot is NaN exactly for censored/named rows",
              np.array_equal(np.isnan(dot), cens))
        check("bound_B is NaN exactly for labelled rows",
              np.array_equal(np.isnan(bB), ~cens))
        check("bound_B == 150 for named, == 48 for generic censored",
              np.all(bB[tier == "named"] == cfg.B_HARD_EXPECTED)
              and np.all(bB[(cens) & (tier != "named")] == cfg.B_SOFT_EXPECTED))

        # --- determinism: byte-identical re-emit (FA: numpy fixed zip ts), array fallback ---
        dd.emit_splits_v2(out=out_b)
        byte_ok = _sha(out_a) == _sha(out_b)
        if byte_ok:
            check("re-emit is BYTE-identical (7.5 strong gate)", True)
        else:
            zb = np.load(out_b, allow_pickle=False)
            check("re-emit is ARRAY-identical (byte-identity not held in-env; fallback)",
                  all(np.array_equal(z[k], zb[k]) for k in z.files))

        # --- the committed on-disk artifact matches a fresh emit (not stale) ---
        if os.path.exists(cfg.SPLIT_NPZ_V2):
            check("committed dot_splits_v2.npz is byte-identical to a fresh emit",
                  _sha(cfg.SPLIT_NPZ_V2) == _sha(out_a))
        z.close()
    finally:
        import shutil
        shutil.rmtree(".scratch", ignore_errors=True)

    print()
    if failures:
        print(f"  {len(failures)} check(s) failed: {failures}")
        raise SystemExit("SPLITS-V2 TESTS FAILED")
    print("SPLITS-V2 TESTS PASS")


if __name__ == "__main__":
    run_tests()
