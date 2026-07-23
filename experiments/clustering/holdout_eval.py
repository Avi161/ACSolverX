"""Held-out evaluation: fit the cut on 70%, score it on the untouched 30%, over many seeds.

Every accuracy this project has quoted so far -- including the headline ``smaller mean block >
1.25`` at 0.945 balanced accuracy -- was fitted and scored on the *same* 237 states. That number
is an upper bound on what the rule does, not an estimate of it: the threshold was chosen by
scanning every value in the data, so some of the fit is the data's noise. This refits the cut on
a stratified 70% and scores it on a 30% the fit never saw.

Two things the sweep is deliberately built to keep separate:

  * **Which seed wins is not a result.** With 71 test points, one split's accuracy has a standard
    error of roughly 0.05, so the best of 200 seeds sits ~2 sigma above the truth *by
    construction* -- the same garden-of-forking-paths that ``run_cluster_237`` corrects with a
    permutation null. The best seed is reported because it was asked for, next to the mean it
    inflates, and ``seed_selection_gain`` names the size of the illusion.
  * **Refit-per-split and fixed-rule are different questions.** ``holdout`` refits the threshold
    on each train half (honest generalisation of the *method*). ``fixed`` scores the already
    published cut with no fitting at all (honest generalisation of the *rule*). The second needs
    no correction for threshold search, so it is the number to quote.

    python3 -m experiments.clustering.holdout_eval
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

from experiments.clustering.rank_signals import YARDSTICK, candidates       # noqa: E402
from experiments.clustering.run_cluster_237 import (                        # noqa: E402
    pop_provenance_matched, pop_tables,
)

OUT = os.path.join(ROOT, "results", "clustering")
TEST_FRAC = 0.30
N_SEEDS = 200
PUBLISHED = ("smaller mean block", 1.25)     # the cut rank_signals found, fitted on all 237

# Multivariate models, as feature lists. ``ALL`` is 11 columns -- the 10 candidates AND total
# length, which is the yardstick when it is competing but a legitimate predictor once it is only a
# term in a model. The small models are here because the full one is not using eleven things:
# ``forward_selection`` prices each column by what it CONTRIBUTES out-of-sample.
#
# Both small models are kept because the comparison between them is the result. The 2-feature one
# is what forward selection picks on population A, where it matches all eleven columns (0.980 vs
# 0.981) -- and it is precisely the pairing the knot hypothesis predicts. But on the
# provenance-matched population it scores 0.745, BELOW ``smaller mean block`` alone at 0.787: the
# knot count stops carrying independent information once both sides are produced the same way, and
# a second column that adds nothing still costs variance. Forward selection on B agrees, picking
# ``mean block length`` second instead. The 3-feature model is the one that survives both (0.975 /
# 0.857), so a selection run on one population is a hypothesis about the other, never a result for
# it -- delete either model and that lesson disappears from the table.
MODELS = {
    "ALL (logistic)": None,                  # None = every candidate, length included
    "3-feature (logistic)": ["smaller mean block", "max_knots", YARDSTICK],
    "2-feature (logistic)": ["smaller mean block", "knot number (sum)"],
}


def stratified_split(y, frac, rng):
    """Hold out ``frac`` of EACH class, so a split cannot shift the base rate it is scored against."""
    test = []
    for lab in (0, 1):
        idx = np.flatnonzero(y == lab)
        rng.shuffle(idx)
        test.append(idx[:int(round(frac * len(idx)))])
    te = np.concatenate(test)
    tr = np.setdiff1d(np.arange(len(y)), te)
    return tr, te


def _score(pred, y):
    tp = int((pred & (y == 1)).sum()); fp = int((pred & (y == 0)).sum())
    fn = int((~pred & (y == 1)).sum()); tn = int((~pred & (y == 0)).sum())
    return {
        "accuracy": (tp + tn) / len(y),
        "bal_acc": 0.5 * ((tp / (tp + fn) if tp + fn else 0.0)
                          + (tn / (tn + fp) if tn + fp else 0.0)),
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
    }


def fit_threshold(v, y):
    """Best cut AND its direction, chosen on the training half only.

    The direction is fitted rather than assumed: hard-coding ``v > t`` because that is how the
    feature pointed on the full data would leak the answer back into the training step.
    """
    best = None
    for t in np.unique(np.round(v, 4)):
        for sign in (1, -1):
            s = _score((v > t) if sign > 0 else (v <= t), y)
            if best is None or s["bal_acc"] > best["bal_acc"]:
                best = {"t": float(t), "sign": sign, "bal_acc": s["bal_acc"]}
    return best


def apply_threshold(v, rule):
    return (v > rule["t"]) if rule["sign"] > 0 else (v <= rule["t"])


def _logistic(Xtr, ytr, lam=1.0, iters=2000, lr=0.5):
    """L2 logistic by gradient descent -- a multivariate ceiling, standardised on TRAIN stats."""
    mu, sd = Xtr.mean(0), Xtr.std(0)
    sd = np.where(sd == 0, 1.0, sd)
    A = np.column_stack([np.ones(len(Xtr)), (Xtr - mu) / sd])
    w = np.zeros(A.shape[1])
    for _ in range(iters):
        p = 1.0 / (1.0 + np.exp(-np.clip(A @ w, -30, 30)))
        w -= lr * (A.T @ (p - ytr) / len(A) + lam * np.r_[0.0, w[1:]] / len(A))
    return lambda X: (np.column_stack([np.ones(len(X)), (X - mu) / sd]) @ w) > 0


def _logistic_w(Xtr, ytr, lam=1.0, iters=2000, lr=0.5):
    """Same fit, but returning the standardised weights -- comparable across features by units."""
    mu, sd = Xtr.mean(0), Xtr.std(0)
    sd = np.where(sd == 0, 1.0, sd)
    A = np.column_stack([np.ones(len(Xtr)), (Xtr - mu) / sd])
    w = np.zeros(A.shape[1])
    for _ in range(iters):
        p = 1.0 / (1.0 + np.exp(-np.clip(A @ w, -30, 30)))
        w -= lr * (A.T @ (p - ytr) / len(A) + lam * np.r_[0.0, w[1:]] / len(A))
    return w[1:]


def forward_selection(rows, n_seeds=40, max_k=5):
    """Which of the 11 columns the model is actually using -- greedily, scored out-of-sample.

    A weight table alone cannot answer this: the candidates are heavily collinear (knot number is
    max_knots + min_knots; block CV and max/mean block measure one thing twice), so L2 splits a
    shared effect across correlated columns and each looks individually modest. Adding features one
    at a time and scoring on held-out data prices each one by what it CONTRIBUTES rather than by
    what it correlates with, which is the question "which features matter" actually asks.
    """
    y = np.array([r[1] for r in rows])
    feats = [candidates(r[2], r[3]) for r in rows]
    names = list(feats[0])
    V = np.column_stack([[f[n] for f in feats] for n in names])
    splits = [stratified_split(y, TEST_FRAC, np.random.default_rng(s)) for s in range(n_seeds)]

    def score(cols):
        a = []
        for tr, te in splits:
            X = V[:, cols]
            a.append(_score(_logistic(X[tr], y[tr].astype(float))(X[te]), y[te])["accuracy"])
        return float(np.mean(a))

    chosen, path = [], []
    while len(chosen) < max_k:
        cand = [(score(chosen + [i]), i) for i in range(len(names)) if i not in chosen]
        best_acc, best_i = max(cand)
        path.append({"added": names[best_i], "n_features": len(chosen) + 1, "acc": best_acc,
                     "gain": best_acc - (path[-1]["acc"] if path else 0.0)})
        chosen.append(best_i)
    full = score(list(range(len(names))))
    w = np.abs(_logistic_w(V, y.astype(float))).tolist()
    return {"path": path, "all_features": full,
            "weights": sorted(({"feature": n, "abs_weight": wi} for n, wi in zip(names, w)),
                              key=lambda d: -d["abs_weight"])}


def shuffle_control(rows, n_seeds=50):
    """Same pipeline, labels destroyed. A 0.98 held-out accuracy is a leak until this says 0.5.

    Returned against the base rate rather than against 0.5, because always-predicting the majority
    class already scores the base rate -- that, not a coin flip, is the floor to clear.
    """
    y = np.array([r[1] for r in rows])
    feats = [candidates(r[2], r[3]) for r in rows]
    X = np.column_stack([[f[c] for f in feats] for c in feats[0]])
    acc = []
    for s in range(n_seeds):
        rng = np.random.default_rng(10_000 + s)
        yy = y.copy()
        rng.shuffle(yy)
        tr, te = stratified_split(yy, TEST_FRAC, rng)
        acc.append(_score(_logistic(X[tr], yy[tr].astype(float))(X[te]), yy[te])["accuracy"])
    return {"acc_mean": float(np.mean(acc)), "base_rate": float(max(y.mean(), 1 - y.mean()))}


def evaluate(tag, rows, n_seeds=N_SEEDS, verbose=True):
    y = np.array([r[1] for r in rows])
    feats = [candidates(r[2], r[3]) for r in rows]
    names = list(feats[0])
    V = {n: np.array([f[n] for f in feats], dtype=float) for n in names}
    XM = {m: np.column_stack([V[n] for n in (cols or names)]) for m, cols in MODELS.items()}

    acc = {n: np.zeros(n_seeds) for n in list(names) + list(MODELS)}
    bal = {n: np.zeros(n_seeds) for n in list(names) + list(MODELS)}
    thr = {n: [] for n in names}
    fixed_acc, fixed_bal = np.zeros(n_seeds), np.zeros(n_seeds)
    n_test = None

    for s in range(n_seeds):
        tr, te = stratified_split(y, TEST_FRAC, np.random.default_rng(s))
        n_test = len(te)
        for n in names:
            rule = fit_threshold(V[n][tr], y[tr])
            sc = _score(apply_threshold(V[n][te], rule), y[te])
            acc[n][s], bal[n][s] = sc["accuracy"], sc["bal_acc"]
            thr[n].append((rule["t"], rule["sign"]))
        for m, X in XM.items():
            sc = _score(_logistic(X[tr], y[tr].astype(float))(X[te]), y[te])
            acc[m][s], bal[m][s] = sc["accuracy"], sc["bal_acc"]
        # The published rule, unfitted: same test half, no training step at all.
        pf = _score(V[PUBLISHED[0]][te] > PUBLISHED[1], y[te])
        fixed_acc[s], fixed_bal[s] = pf["accuracy"], pf["bal_acc"]

    out = []
    for n in acc:
        a, b = acc[n], bal[n]
        modal = None
        if n in thr:
            vals, cnt = np.unique([f"{t:.4g}|{sg}" for t, sg in thr[n]], return_counts=True)
            modal = {"rule": str(vals[cnt.argmax()]), "share": float(cnt.max() / n_seeds)}
        out.append({
            "feature": n,
            "acc_mean": float(a.mean()), "acc_std": float(a.std()),
            "acc_min": float(a.min()), "acc_max": float(a.max()),
            "best_seed": int(a.argmax()),
            "seed_selection_gain": float(a.max() - a.mean()),
            "bal_mean": float(b.mean()), "bal_std": float(b.std()),
            "modal_threshold": modal,
        })
    out.sort(key=lambda r: -r["acc_mean"])

    fixed = {"acc_mean": float(fixed_acc.mean()), "acc_std": float(fixed_acc.std()),
             "acc_min": float(fixed_acc.min()), "acc_max": float(fixed_acc.max()),
             "best_seed": int(fixed_acc.argmax()),
             "bal_mean": float(fixed_bal.mean()), "bal_std": float(fixed_bal.std())}
    ctrl = shuffle_control(rows)
    fwd = forward_selection(rows)

    if verbose:
        print(f"\n{'=' * 100}\n{tag}   ({int((y == 0).sum())} solved / {int((y == 1).sum())} "
              f"unsolved)   {n_seeds} seeds x {int(100 * TEST_FRAC)}% test = {n_test} held out"
              f"\n{'=' * 100}")
        print(f"  {'statistic':21s} {'test acc':>18} {'min':>6} {'max':>6} {'@seed':>6} "
              f"{'bal acc':>14}  fitted cut (train)")
        for r in out:
            mt = "" if r["modal_threshold"] is None else (
                f"  {r['modal_threshold']['rule']}  in {r['modal_threshold']['share'] * 100:.0f}% "
                f"of splits")
            print(f"  {r['feature']:21s} {r['acc_mean']:>10.3f} ± {r['acc_std']:.3f} "
                  f"{r['acc_min']:>6.3f} {r['acc_max']:>6.3f} {r['best_seed']:>6d} "
                  f"{r['bal_mean']:>8.3f} ± {r['bal_std']:.3f}{mt}")
        print(f"\n  published rule, NOT refitted ({PUBLISHED[0]} > {PUBLISHED[1]}):"
              f"  {fixed['acc_mean']:.3f} ± {fixed['acc_std']:.3f}   "
              f"[{fixed['acc_min']:.3f}, {fixed['acc_max']:.3f}]   best seed {fixed['best_seed']}")
        print(f"  leakage control, labels shuffled:  {ctrl['acc_mean']:.3f}   "
              f"(base rate {ctrl['base_rate']:.3f} -- anything above it would mean a leak)")
        print(f"\n  which columns the model is actually using (greedy, scored out-of-sample; "
              f"all 11 = {fwd['all_features']:.3f}):")
        for p in fwd["path"]:
            print(f"    {p['n_features']}. + {p['added']:22s} -> {p['acc']:.3f}   ({p['gain']:+.3f})")
    return {"features": out, "fixed_rule": fixed, "shuffle_control": ctrl,
            "forward_selection": fwd, "n_test": n_test, "n_seeds": n_seeds}


def main():
    res = {}
    for tag, rows in (("A  tables", pop_tables()),
                      ("B  provenance-matched", pop_provenance_matched())):
        res[tag.split()[0]] = evaluate(tag, rows)

    print(f"\n{'=' * 100}\nWHAT THE SEED SWEEP ACTUALLY SHOWS\n{'=' * 100}")
    for tag in ("A", "B"):
        best = res[tag]["features"][0]
        solo = next(r for r in res[tag]["features"] if r["feature"] not in MODELS)
        print(f"  {tag}: best overall {best['feature']:22s} {best['acc_mean']:.3f} ± "
              f"{best['acc_std']:.3f}   best single stat {solo['feature']} "
              f"{solo['acc_mean']:.3f} ± {solo['acc_std']:.3f}")
    a = res["A"]["features"][0]
    print(f"\n  seed sweep, on {a['feature']} over {res['A']['n_seeds']} splits:")
    print(f"    honest estimate   {a['acc_mean']:.3f} ± {a['acc_std']:.3f}")
    print(f"    best seed ({a['best_seed']:>3d})     {a['acc_max']:.3f}   "
          f"{a['seed_selection_gain']:+.3f} over the mean -- that gap is the selection, not the rule")
    print(f"    worst seed        {a['acc_min']:.3f}")
    print("  a seed is a property of the SPLIT, not of the model: the best-seed number does not "
          "transfer\n  to the next 30% you have not seen, so the mean is the estimate to quote.")

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "holdout_eval.json"), "w") as f:
        json.dump({"populations": res, "test_frac": TEST_FRAC,
                   "published_rule": {"feature": PUBLISHED[0], "threshold": PUBLISHED[1]}},
                  f, indent=1)
    print(f"\nwrote -> {os.path.relpath(OUT, ROOT)}/holdout_eval.json")


if __name__ == "__main__":
    main()
