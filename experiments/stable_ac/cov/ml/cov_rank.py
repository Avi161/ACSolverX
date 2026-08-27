"""Can a model tell a good change of variables from a bad one, before running the search?

Protocol
--------
Every CoV row costs `nodes if solved else budget` (an unsolved start is not missing data — it
burned a full budget and returned nothing). The deployable question is a RANKING one: given a
presentation's ~100 applicable z's, order them so the first one you run is cheap.

Splitting is GroupKFold over the Aut(F2)-orbit of the original presentation, never over pres_id:
the 66-row benchmark holds 51 distinct orbits, so a pres_id split trains on a presentation's own
relabelled twin and reports leakage as skill.

Scored against four references on each held-out presentation:
    random     exact expectation over that presentation's own candidates (no sampling)
    shortest   pick the z minimising the resulting total relator length — the obvious heuristic
    moved      pick at random among non-automorphic z's only (week-5's finding as a picker)
    oracle     the best z, i.e. what week 5's "best CoV per presentation" diamond costs

Two model variants, because within one presentation the original-presentation features are
constant and a tree can use them to memorise which presentation it is looking at:
    raw        target = log10(cost)
    centred    target = log10(cost) - mean log10(cost) of that presentation
               (difficulty removed; the model can only learn what makes a z relatively good)

    .venv/bin/python3 experiments/stable_ac/cov/ml/cov_rank.py [--path SWEEP.jsonl]
"""
import argparse
import json
import os
import sys

import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor, HistGradientBoostingClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression, RidgeCV
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cov_features import load_dataset, cost, default_path  # noqa: E402

SEED = 0
N_FOLDS = 8


# ---------------------------------------------------------------- helpers

def drop_constant(ds):
    keep = [i for i in range(ds.X.shape[1]) if ds.X[:, i].std() > 0]
    return ds.X[:, keep], [ds.names[i] for i in keep]


def geo_mean(v):
    v = np.asarray(v, dtype=float)
    return float(np.exp(np.mean(np.log(np.maximum(v, 1.0)))))


def spearman(a, b):
    """Rank correlation without scipy's tie handling differences — average ranks on ties."""
    def rank(v):
        order = np.argsort(v, kind="mergesort")
        r = np.empty(len(v), dtype=float)
        r[order] = np.arange(len(v), dtype=float)
        # average ties
        _, inv, cnt = np.unique(v, return_inverse=True, return_counts=True)
        sums = np.zeros(len(cnt))
        np.add.at(sums, inv, r)
        return (sums / cnt)[inv]
    ra, rb = rank(np.asarray(a, float)), rank(np.asarray(b, float))
    if ra.std() == 0 or rb.std() == 0:
        return np.nan
    return float(np.corrcoef(ra, rb)[0, 1])


# ---------------------------------------------------------------- cross-validated scores

def oof_scores(X, y, groups, model_fn):
    """Out-of-fold predictions from a GroupKFold over Aut-orbits."""
    oof = np.full(len(y), np.nan)
    gkf = GroupKFold(n_splits=N_FOLDS)
    for tr, te in gkf.split(X, y, groups):
        m = model_fn()
        m.fit(X[tr], y[tr])
        oof[te] = m.predict(X[te]) if not hasattr(m, "predict_proba") else \
            m.predict_proba(X[te])[:, 1]
    return oof


def reg():
    return HistGradientBoostingRegressor(
        max_iter=400, learning_rate=0.06, max_leaf_nodes=31, min_samples_leaf=20,
        l2_regularization=1.0, random_state=SEED)


def clf():
    return HistGradientBoostingClassifier(
        max_iter=400, learning_rate=0.06, max_leaf_nodes=31, min_samples_leaf=20,
        l2_regularization=1.0, random_state=SEED)


def linear_reg():
    """A regularised linear ranker. Kept as a first-class arm, not a footnote: on grouped folds
    it is the honest yardstick for whether the trees are learning structure or memorising
    presentations."""
    return make_pipeline(StandardScaler(), RidgeCV(alphas=np.logspace(-2, 4, 25)))


def linear_clf():
    return make_pipeline(StandardScaler(),
                         LogisticRegression(max_iter=3000, C=1.0, random_state=SEED))


# ---------------------------------------------------------------- per-presentation picking

N_TIEBREAK = 200


def pick_table(ds, c, score_by_name, k_list=(1, 3, 5)):
    """For each presentation, what does each picker cost? Lower score = picked first.

    Ties are broken RANDOMLY and averaged over N_TIEBREAK draws, never by array order. This is
    not a detail: `abelian mass` is integer-valued and a median of 6 candidates sit tied at a
    presentation's minimum, so a stable argsort would silently report the quality of the sweep's
    file ordering as the quality of the rule. (It did: file order gave the mass rule 52/66 at
    k=1, a random tie-break gives 47.4.) Continuous scores have no ties, so this is a no-op for
    the trained models and the comparison becomes like-for-like.
    """
    out = {}
    pres_ids = sorted(set(ds.pres.tolist()))
    for name, score in score_by_name.items():
        rng = np.random.default_rng(SEED)
        rows = []
        for p in pres_ids:
            m = ds.pres == p
            cp, sp, sol = c[m], score[m], ds.solved[m]
            rec = {"pres": str(p), "n_cand": int(m.sum()),
                   "oracle": float(cp.min()), "solved_frac": float(sol.mean()),
                   "n_tied_at_min": int((sp == sp.min()).sum())}
            acc = {k: {"cost": [], "solved": []} for k in k_list}
            for _ in range(N_TIEBREAK):
                order = np.lexsort((rng.random(len(sp)), sp))
                for k in k_list:
                    take = order[:k]
                    acc[k]["cost"].append(float(cp[take].min()))
                    acc[k]["solved"].append(bool(sol[take].any()))
            for k in k_list:
                rec[f"top{k}"] = float(np.mean(acc[k]["cost"]))
                rec[f"top{k}_solved"] = float(np.mean(acc[k]["solved"]))
                # the arithmetic mean the slides quote is over solved picks only, so a picker
                # that misses a presentation contributes nothing there rather than a 10,000
                rec[f"top{k}_cost_when_solved"] = (
                    float(np.mean([x for x, s in zip(acc[k]["cost"], acc[k]["solved"]) if s]))
                    if any(acc[k]["solved"]) else None)
            rec["rho"] = spearman(sp, cp)
            rows.append(rec)
        out[name] = rows
    return out


def random_reference(ds, c):
    """Exact expectation of a single uniform-random pick, per presentation. No sampling."""
    rows = []
    for p in sorted(set(ds.pres.tolist())):
        m = ds.pres == p
        cp = c[m]
        rows.append({"pres": str(p), "exp_cost": float(cp.mean()),
                     "geo_cost": geo_mean(cp), "median_cost": float(np.median(cp)),
                     "p_solve": float(ds.solved[m].mean()), "oracle": float(cp.min())})
    return rows


def summarise(name, rows, k=1, common=None):
    """`common` = the presentations EVERY picker solves. Without it, "mean nodes over the ones
    I solved" is scored on a different set per row — the weaker picker gets to drop exactly the
    presentations it failed, which are the expensive ones. Both columns are reported."""
    picks = np.array([r[f"top{k}"] for r in rows])
    solved = np.array([r[f"top{k}_solved"] for r in rows])
    own = [r[f"top{k}_cost_when_solved"] for r in rows if r[f"top{k}_cost_when_solved"] is not None]
    s = {"picker": name, "k": k, "n_pres": len(rows),
         "solve_rate": float(solved.mean()),
         "n_solved": float(solved.sum()),
         "mean_nodes_own_solved": float(np.mean(own)) if own else None,
         "n_own_solved": len(own),
         "geo_nodes": geo_mean(picks), "median_nodes": float(np.median(picks)),
         "mean_nodes_all": float(picks.mean())}
    if common:
        cm = [r[f"top{k}_cost_when_solved"] for r in rows if r["pres"] in common]
        cm = [x for x in cm if x is not None]
        s["mean_nodes_common"] = float(np.mean(cm)) if cm else None
        s["n_common"] = len(common)
    return s


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    path = args.path or default_path()

    ds = load_dataset(path)
    X, names = drop_constant(ds)
    c = cost(ds)
    logc = np.log10(np.maximum(c, 1.0))

    print(f"{len(ds)} CoV rows · {len(set(ds.pres))} presentations · "
          f"{len(set(ds.group))} Aut-orbits · budget {ds.budget:,} · {len(names)} features")
    print(f"solved {ds.solved.sum()} / {len(ds)} ({100 * ds.solved.mean():.1f}%)\n")

    # ---- will this z solve at all?  (classification)
    p_solve = oof_scores(X, ds.solved.astype(int), ds.group, clf)
    p_solve_lin = oof_scores(X, ds.solved.astype(int), ds.group, linear_clf)
    auc = roc_auc_score(ds.solved, p_solve)
    auc_lin = roc_auc_score(ds.solved, p_solve_lin)
    print(f"solve classifier   AUC {auc:.3f}   (linear baseline {auc_lin:.3f})")

    # ---- how expensive will it be?  (ranking)
    pred_raw = oof_scores(X, logc, ds.group, reg)

    centre = np.zeros(len(logc))
    for p in set(ds.pres.tolist()):
        m = ds.pres == p
        centre[m] = logc[m].mean()
    pred_ctr = oof_scores(X, logc - centre, ds.group, reg)
    pred_lin = oof_scores(X, logc - centre, ds.group, linear_reg)

    for nm, v in [("raw", pred_raw), ("centred", pred_ctr), ("ridge", pred_lin),
                  ("p_solve", p_solve)]:
        if np.isnan(v).any():
            raise RuntimeError(f"{nm}: {np.isnan(v).sum()} rows never landed in a test fold")

    # ---- reference pickers, all computable without running a search
    rng = np.random.default_rng(SEED)
    shortest = X[:, names.index("cov_total_len")].astype(float)
    is_relabel = X[:, names.index("is_relabel")]
    # total |exponent sum| of the transformed pair. The trivial presentation <x, y> has
    # abelian mass 2, so this is "how far from trivial does the abelianisation sit". Within one
    # presentation it ranks identically to d_exp_l1, the feature the model leans on hardest.
    abelian = (X[:, names.index("cov_r1_exp_l1")] + X[:, names.index("cov_r2_exp_l1")]).astype(float)
    # "moved" picker: random among non-automorphic z's, relabels pushed to the back
    moved = is_relabel * 1e6 + rng.random(len(ds))
    rand = rng.random(len(ds))

    scores = {"GBT · raw": pred_raw, "GBT · centred": pred_ctr,
              "ridge · centred": pred_lin,
              "heuristic · abelian mass": abelian,
              "heuristic · shortest result": shortest,
              "heuristic · moved only": moved,
              "random": rand}
    tab = pick_table(ds, c, scores)

    ref = random_reference(ds, c)
    oracle_geo = geo_mean([r["oracle"] for r in ref])
    rand_geo = geo_mean([r["geo_cost"] for r in ref])

    oracle_solve = float(np.mean([r["p_solve"] > 0 for r in ref]))
    print(f"\nreferences over {len(ref)} presentations")
    print(f"  oracle (best z)                geo {oracle_geo:9.1f}   "
          f"solve rate {oracle_solve:.3f}  ({int(round(oracle_solve * len(ref)))}/{len(ref)})")
    print(f"  random pick, exact expectation geo {rand_geo:9.1f}   "
          f"P(solve) {np.mean([r['p_solve'] for r in ref]):.3f}")

    print(f"\n{'picker':32s} {'k':>2s} {'solved':>8s} {'mean nodes':>11s} "
          f"{'(common)':>10s} {'geo':>9s} {'capture':>8s}")
    summ = []
    # ONE common subset, fixed across every k and every picker: the presentations that even the
    # weakest picker solves on its FIRST try. Recomputing it per k would let the k=5 column quietly
    # include harder presentations than the k=1 column, which makes best-of-5 look worse than
    # best-of-1 — a denominator artifact, not a result.
    common = set.intersection(*[
        {r["pres"] for r in tab[nm] if r["top1_cost_when_solved"] is not None}
        for nm in scores])
    for k in (1, 3, 5):
        for nm in scores:
            s = summarise(nm, tab[nm], k, common)
            # fraction of the log-space gap from a random pick to the oracle that is captured
            s["capture"] = (np.log10(rand_geo) - np.log10(s["geo_nodes"])) / \
                           (np.log10(rand_geo) - np.log10(oracle_geo))
            summ.append(s)
            mn = s["mean_nodes_own_solved"]
            mc = s["mean_nodes_common"]
            print(f"{nm:32s} {k:2d} {s['n_solved']:6.1f}/{s['n_pres']:<2d} "
                  f"{mn if mn is None else round(mn, 1):>11} {mc if mc is None else round(mc, 1):>10} "
                  f"{s['geo_nodes']:9.1f} {s['capture']:8.2f}")
        print(f"   ^ mean nodes = arithmetic mean over that picker's OWN solved picks; "
              f"(common) = the {len(common)} presentations every picker solves\n")

    # ---- within-presentation rank correlation: the ranking skill, difficulty removed.
    # A presentation whose every CoV is unsolved has a constant cost column and no rank
    # correlation to report; it is dropped from the median, not scored as zero.
    n_flat = int(np.isnan(np.array([x["rho"] for x in tab["random"]], dtype=float)).sum())
    print(f"within-presentation Spearman rho (score vs actual cost), median over "
          f"{len(ref) - n_flat} presentations ({n_flat} dropped — every CoV unsolved):")
    rho_med = {}
    for nm in scores:
        r = np.array([x["rho"] for x in tab[nm]], dtype=float)
        r = r[~np.isnan(r)]
        rho_med[nm] = float(np.median(r))
        print(f"  {nm:32s} {np.median(r):+.3f}   (mean {np.mean(r):+.3f}, "
              f"{100 * np.mean(r > 0):.0f}% of presentations positive)")

    # ---- why it works: split the abelian-mass signal into "does it solve" and "how fast".
    # Pooling across presentations destroys both (Simpson's paradox — between-presentation
    # difficulty swamps the within-presentation ordering), so every number here is per
    # presentation and only then aggregated.
    aucs = []
    for p in sorted(set(ds.pres.tolist())):
        m = ds.pres == p
        s = ds.solved[m]
        if s.all() or not s.any():
            continue
        aucs.append(roc_auc_score(s, -abelian[m]))
    rn, rp, rl = [], [], []
    for p in sorted(set(ds.pres.tolist())):
        m = (ds.pres == p) & ds.solved
        if m.sum() < 8:
            continue
        rn.append(spearman(abelian[m], ds.nodes[m]))
        rp.append(spearman(abelian[m], ds.path[m]))
        rl.append(spearman(shortest[m], ds.nodes[m]))
    mech = {
        "auc_solve_within_pres": float(np.median(aucs)) if aucs else None,
        "n_mixed_pres": len(aucs),
        "rho_nodes_solved_only": float(np.nanmedian(rn)) if rn else None,
        "rho_path_solved_only": float(np.nanmedian(rp)) if rp else None,
        "rho_nodes_len_solved_only": float(np.nanmedian(rl)) if rl else None,
        "n_pres_solved_only": len(rn),
        "pooled_corr_abelian": float(np.corrcoef(logc, abelian)[0, 1]),
        "pooled_corr_length": float(np.corrcoef(logc, shortest)[0, 1]),
    }
    print(f"\nabelian mass, decomposed (per presentation, never pooled):")
    print(f"  picks the solvers          AUC {mech['auc_solve_within_pres']:.3f} "
          f"(median over {mech['n_mixed_pres']} presentations with both outcomes)")
    print(f"  among solved rows, ranks   nodes {mech['rho_nodes_solved_only']:+.3f}   "
          f"path {mech['rho_path_solved_only']:+.3f}   "
          f"(total length ranks nodes {mech['rho_nodes_len_solved_only']:+.3f})")
    print(f"  POOLED across presentations it vanishes: r(log cost, abelian) = "
          f"{mech['pooled_corr_abelian']:+.3f} vs r(log cost, length) = "
          f"{mech['pooled_corr_length']:+.3f}")

    # ---- what is the model using?  permutation importance on held-out folds
    print("\npermutation importance (centred ranker, held-out folds, top 15):")
    gkf = GroupKFold(n_splits=N_FOLDS)
    imp = np.zeros(len(names))
    for tr, te in gkf.split(X, logc, ds.group):
        m = reg()
        m.fit(X[tr], (logc - centre)[tr])
        pi = permutation_importance(m, X[te], (logc - centre)[te], n_repeats=5,
                                    random_state=SEED, scoring="r2")
        imp += pi.importances_mean
    imp /= N_FOLDS
    top = np.argsort(imp)[::-1][:15]
    for i in top:
        print(f"  {names[i]:26s} {imp[i]:+.4f}")

    if args.out:
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        with open(args.out, "w") as f:
            json.dump({
                "source": os.path.basename(path), "budget": ds.budget,
                "n_rows": len(ds), "n_pres": len(set(ds.pres.tolist())),
                "n_orbits": len(set(ds.group.tolist())),
                "solve_rate_rows": float(ds.solved.mean()),
                "auc_solve": auc, "auc_solve_linear": auc_lin,
                "oracle_geo": oracle_geo, "random_geo": rand_geo,
                "oracle_solve_rate": oracle_solve,
                "summary": summ, "mechanism": mech,
                "n_pres_flat": n_flat, "rho_median": rho_med,
                "importance": {names[i]: float(imp[i]) for i in np.argsort(imp)[::-1][:25]},
                "per_pres": {nm: tab[nm] for nm in scores},
                "reference": ref,
            }, f, indent=1)
        print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
