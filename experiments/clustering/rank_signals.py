"""Head-to-head: which single statistic separates solved from unsolved best?

Every candidate this project turned up was measured somewhere different -- ``max_knots`` on the
full population, ``smaller mean block`` only inside the max_knots = 2 bucket, ``max/mean block``
in the matched length band. Those numbers are not comparable, and picking a winner from them
would be picking a winner from four different experiments. This puts all of them on one footing:

  * both populations (tables, and the provenance-matched control),
  * raw AUC, AUC with total length regressed out, and AUC inside the matched length band,
  * the same 237 / 272 states, the same direction convention.

**Total length is included as the yardstick, not as a candidate.** It is the confound every other
statistic has to beat, so a feature that scores below it has explained nothing new.

One numerical trap this file handles explicitly: regressing total length out of *itself* leaves
floating-point residue whose ordering is preserved, so its "length-removed" AUC comes back at
roughly the raw value (0.811 against a raw 0.809) rather than the 0.5 it should be. That column
is therefore reported as None for length, never as a number -- it would otherwise look like the
confound survives its own removal.

    python3 -m experiments.clustering.rank_signals
"""
import json
import os
import sys

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

from experiments.clustering.features import knot_number                              # noqa: E402
from experiments.clustering.signed_knots import signed_blocks                        # noqa: E402
from experiments.clustering.run_cluster_237 import (                                 # noqa: E402
    _auc, pop_provenance_matched, pop_tables,
)

OUT = os.path.join(ROOT, "results", "clustering")
BAND = (13, 25)
YARDSTICK = "total length"


def candidates(r1, r2):
    bl = signed_blocks(r1) + signed_blocks(r2)
    runs = [n for _, n, _ in bl]
    xs = [n for g, n, _ in bl if g == "x"]
    ys = [n for g, n, _ in bl if g == "y"]
    mx = float(np.mean(xs)) if xs else 0.0
    my = float(np.mean(ys)) if ys else 0.0
    k1, k2 = knot_number(r1), knot_number(r2)
    mean_b = float(np.mean(runs))
    L = float(len(r1) + len(r2))
    return {
        "smaller mean block": min(mx, my),
        "larger mean block": max(mx, my),
        "max_knots": float(max(k1, k2)),
        "min_knots": float(min(k1, k2)),
        "knot number (sum)": float(k1 + k2),
        "knot density": (k1 + k2) / L,
        "max / mean block": max(runs) / mean_b,
        "block CV": float(np.std(runs)) / mean_b,
        "max block length": float(max(runs)),
        "mean block length": mean_b,
        YARDSTICK: L,
    }


def best_threshold(v, y):
    """Best single cut, scored by balanced accuracy so the class imbalance cannot flatter it."""
    best = None
    for t in np.unique(np.round(v, 4)):
        p = v > t
        tp = int((p & (y == 1)).sum()); fp = int((p & (y == 0)).sum())
        fn = int((~p & (y == 1)).sum()); tn = int((~p & (y == 0)).sum())
        ba = 0.5 * ((tp / (tp + fn) if tp + fn else 0) + (tn / (tn + fp) if tn + fp else 0))
        if best is None or ba > best["bal_acc"]:
            best = {"threshold": float(t), "bal_acc": ba, "tp": tp, "fp": fp, "fn": fn, "tn": tn,
                    "precision": tp / (tp + fp) if tp + fp else 0.0,
                    "recall": tp / (tp + fn) if tp + fn else 0.0}
    return best


def analyse(tag, rows):
    y = np.array([r[1] for r in rows])
    feats = [candidates(r[2], r[3]) for r in rows]
    names = list(feats[0])
    L = np.array([f[YARDSTICK] for f in feats])
    band = (L >= BAND[0]) & (L <= BAND[1])
    A = np.column_stack([np.ones(len(L)), L])

    out = []
    for n in names:
        v = np.array([f[n] for f in feats], dtype=float)
        resid = v - A @ np.linalg.lstsq(A, v, rcond=None)[0]
        out.append({
            "feature": n,
            "auc": _auc(v, y),
            # See the module docstring: length's own residual is numerical noise, not a result.
            "auc_length_removed": None if n == YARDSTICK else _auc(resid, y),
            "auc_matched_band": _auc(v[band], y[band]),
            "solved_mean": float(v[y == 0].mean()), "unsolved_mean": float(v[y == 1].mean()),
            "rule": best_threshold(v, y),
        })
    out.sort(key=lambda r: -abs(r["auc"] - 0.5))
    print(f"\n{'=' * 96}\n{tag}   ({int((y == 0).sum())} solved / {int((y == 1).sum())} unsolved)"
          f"\n{'=' * 96}")
    print(f"  {'statistic':21s} {'AUC':>6} {'len-removed':>12} {'matched':>8} "
          f"{'best rule':>22} {'bal acc':>8}")
    yard = next(r for r in out if r["feature"] == YARDSTICK)
    for r in out:
        lr = "     —" if r["auc_length_removed"] is None else f"{r['auc_length_removed']:6.3f}"
        beats = "" if r["feature"] == YARDSTICK else (
            "  <-- beats length" if abs(r["auc"] - .5) > abs(yard["auc"] - .5) else "")
        print(f"  {r['feature']:21s} {r['auc']:>6.3f} {lr:>12} {r['auc_matched_band']:>8.3f} "
              f"{'> ' + format(r['rule']['threshold'], '.3f'):>22} {r['rule']['bal_acc']:>8.3f}"
              f"{beats}")
    return out


def main():
    res = {}
    for tag, rows in (("A  tables", pop_tables()),
                      ("B  provenance-matched", pop_provenance_matched())):
        res[tag.split()[0]] = analyse(tag, rows)

    a = {r["feature"]: r for r in res["A"]}
    b = {r["feature"]: r for r in res["B"]}
    # The winner must hold up on BOTH populations AND after length removal -- a statistic that
    # tops one column and collapses in another has found the confound, not the signal.
    robust = sorted(
        (f for f in a if f != YARDSTICK),
        key=lambda f: -min(abs(a[f]["auc_length_removed"] - .5),
                           abs(b[f]["auc_length_removed"] - .5)))
    print(f"\n{'=' * 96}\nMOST ROBUST (ranked by the WEAKER of the two length-removed scores)"
          f"\n{'=' * 96}")
    for f in robust[:5]:
        print(f"  {f:21s} A {a[f]['auc_length_removed']:.3f}   B {b[f]['auc_length_removed']:.3f}"
              f"   worst {min(abs(a[f]['auc_length_removed'] - .5), abs(b[f]['auc_length_removed'] - .5)) + .5:.3f}")
    win = robust[0]
    print(f"\n  winner: {win}")
    print(f"    A: AUC {a[win]['auc']:.3f}  rule > {a[win]['rule']['threshold']:.2f} -> "
          f"bal acc {a[win]['rule']['bal_acc']:.3f} "
          f"({a[win]['rule']['tp']}/{a[win]['rule']['fp']}/{a[win]['rule']['fn']}/{a[win]['rule']['tn']})")
    print(f"    B: AUC {b[win]['auc']:.3f}  rule > {b[win]['rule']['threshold']:.2f} -> "
          f"bal acc {b[win]['rule']['bal_acc']:.3f}")

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "signal_ranking.json"), "w") as f:
        json.dump({"populations": res, "winner": win, "band": list(BAND)}, f, indent=1)
    print(f"\nwrote -> {os.path.relpath(OUT, ROOT)}/signal_ranking.json")


if __name__ == "__main__":
    main()
