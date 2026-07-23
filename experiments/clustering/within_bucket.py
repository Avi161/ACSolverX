"""Within a max_knots bucket, what separates solved from unsolved?

max_knots splits the 237 well but leaves two mixed buckets: 101 solved / 23 unsolved at
max_knots = 2, and 12 / 87 at max_knots = 3. This asks what is left once that variable is held
fixed, using the two things ``knot_number`` throws away -- the exponent sign and the block sizes.

**The bucket is small and the feature list is long, so a naive best-AUC scan will find something
on noise.** With 23 unsolved states at max_knots = 2, a single feature reaching AUC 0.70 is
unremarkable if you looked at fourteen. Every bucket therefore gets a permutation null over the
*maximum* AUC across the whole feature list, and the reported p-value is against that maximum, not
against the individual feature.

    python3 -m experiments.clustering.within_bucket
"""
import csv
import json
import os
import sys
from collections import Counter

import numpy as np


def _repo_root():
    d = os.path.dirname(os.path.abspath(__file__))
    while d != os.path.dirname(d):
        if (os.path.isdir(os.path.join(d, "experiments"))
                and os.path.isdir(os.path.join(d, "data"))):
            return d
        d = os.path.dirname(d)
    raise RuntimeError("repo root not found")


ROOT = _repo_root()
sys.path.insert(0, ROOT)

from experiments.clustering.features import knot_number                    # noqa: E402
from experiments.clustering.signed_knots import (                          # noqa: E402
    FEATURE_NAMES, block_signature, sig_str, signed_features,
)
from experiments.clustering.run_cluster_237 import _auc, pop_tables        # noqa: E402

OUT = os.path.join(ROOT, "results", "clustering")
N_PERM = 2000
SEED = 0


def main():
    rows = pop_tables()
    y = np.array([r[1] for r in rows])
    pairs = [(r[2], r[3]) for r in rows]
    kmax = np.array([max(knot_number(a), knot_number(b)) for a, b in pairs])
    X = np.vstack([signed_features(a, b) for a, b in pairs])
    rng = np.random.default_rng(SEED)
    report = {}

    for bucket in sorted(set(kmax.tolist())):
        m = kmax == bucket
        yb, Xb = y[m], X[m]
        ns, nu = int((yb == 0).sum()), int((yb == 1).sum())
        print(f"\n{'=' * 76}\nmax_knots = {bucket}:  {ns} solved / {nu} unsolved\n{'=' * 76}")
        if ns == 0 or nu == 0:
            print("  pure bucket -- nothing to separate")
            report[str(bucket)] = {"n_solved": ns, "n_unsolved": nu, "pure": True}
            continue

        # Length still varies inside a bucket (15.8 vs 20.1 at max_knots = 2), so every feature is
        # also scored with total length regressed out. A block statistic that only works because
        # long words have long blocks must not be reported as a separate discovery.
        lb = np.array([len(a) + len(b) for a, b in
                       (pairs[i] for i in np.flatnonzero(m))], dtype=float)
        A = np.column_stack([np.ones(len(lb)), lb])
        resid = Xb - A @ np.linalg.lstsq(A, Xb, rcond=None)[0]
        auc_len = _auc(lb, yb)
        aucs = [_auc(Xb[:, j], yb) for j in range(Xb.shape[1])]
        aucs_r = [_auc(resid[:, j], yb) for j in range(Xb.shape[1])]
        print(f"  [length control] total length alone: AUC {auc_len:.3f}"
              f"  (solved {lb[yb == 0].mean():.1f}, unsolved {lb[yb == 1].mean():.1f})")
        # Null over the MAXIMUM |AUC-0.5| across all 14 features, which is the quantity actually
        # being selected on. Anything less would understate how easy it is to find one by chance.
        null = np.empty(N_PERM)
        for t in range(N_PERM):
            yp = rng.permutation(yb)
            null[t] = max(abs(_auc(Xb[:, j], yp) - 0.5) for j in range(Xb.shape[1]))
        obs = max(abs(a - 0.5) for a in aucs)
        p = float((null >= obs).mean())
        thresh = float(np.percentile(null, 95))

        order = sorted(range(len(aucs)), key=lambda j: -abs(aucs[j] - 0.5))
        print(f"  {'feature':24s} {'solved':>8} {'unsolved':>9} {'AUC':>7} {'AUC|len':>8}   verdict")
        feats = []
        for j in order:
            s, u = Xb[yb == 0, j].mean(), Xb[yb == 1, j].mean()
            sig = abs(aucs[j] - 0.5) >= thresh
            beats = abs(aucs_r[j] - 0.5) > abs(auc_len - 0.5)
            print(f"  {FEATURE_NAMES[j]:24s} {s:>8.2f} {u:>9.2f} {aucs[j]:>7.3f} "
                  f"{aucs_r[j]:>8.3f}   {'survives null' if sig else '-'}"
                  f"{'; beats length' if sig and beats else ''}")
            feats.append({"feature": FEATURE_NAMES[j], "solved_mean": float(s),
                          "unsolved_mean": float(u), "auc": aucs[j],
                          "auc_length_removed": aucs_r[j], "survives": bool(sig),
                          "beats_length": bool(beats)})
        print(f"\n  best |AUC-0.5| = {obs:.3f};  null 95th pct = {thresh:.3f}, "
              f"max = {null.max():.3f}  ->  p = {p:.4f}")
        print(f"  {'SIGNAL' if p < 0.05 else 'NOT DISTINGUISHABLE'} at this bucket")

        sigs = {0: Counter(), 1: Counter()}
        for i in np.flatnonzero(m):
            sigs[int(y[i])][sig_str(block_signature(*pairs[i]))] += 1
        print(f"\n  most common block signatures (x/y block sizes between knots)")
        for lab, tag in ((0, "solved"), (1, "unsolved")):
            top = sigs[lab].most_common(4)
            print(f"    {tag:9s} " + "   ".join(f"{s} ({c})" for s, c in top))

        report[str(bucket)] = {
            "n_solved": ns, "n_unsolved": nu, "features": feats,
            "best_abs_auc": obs, "null_p95": thresh, "null_max": float(null.max()),
            "p_value": p, "significant": bool(p < 0.05), "n_perm": N_PERM,
            "auc_length_alone": auc_len,
            "len_solved": float(lb[yb == 0].mean()), "len_unsolved": float(lb[yb == 1].mean()),
            "signatures": {t: sigs[l].most_common(6) for l, t in ((0, "solved"), (1, "unsolved"))},
        }

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "within_bucket.json"), "w") as f:
        json.dump(report, f, indent=1)
    print(f"\nwrote -> {os.path.relpath(OUT, ROOT)}/within_bucket.json")


if __name__ == "__main__":
    main()
