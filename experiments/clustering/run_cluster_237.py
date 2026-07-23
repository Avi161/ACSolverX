"""Unsupervised clustering over minimal automorphic states: does anything separate solved
from unsolved?

Two populations are analysed, and the second one is the point.

**A. tables** -- the 113 Aut(F2)-orbit representatives of the solved Miller-Schupp cells and the
124 ACA-class representatives of the unsolved ones, from
``results/equivalence_classes/ms1190_tables/``.

**B. provenance-matched** -- the same question asked without a manufacturing confound. The two
sides of population A were *made by different processes*: the solved reps are raw MS cells pushed
to their Aut-minimal form, while the unsolved reps are raw MS cells that an upstream bounded AC
reduction had already rewritten (``EQUIVALENCE_FINDING.md`` Sec 1: "the 261 reps are local minima
of somebody else's bounded search", on average 2.74 letters shorter than the cells they name).
A classifier could separate those two populations by detecting *which pipeline emitted the word*
rather than anything about difficulty. Population B removes the difference: every state on both
sides is a raw MS cell mapped through ``aut_canon``, nothing else. If the separation survives here
it is a fact about the presentations; if it collapses, the population-A result was provenance.

The clustering never sees the label -- the label is only used to score a partition afterwards.
No AC moves anywhere: this is purely about patterns in the initial minimal automorphic states,
treated as pairs of cyclic words.

    python3 -m experiments.clustering.run_cluster_237
"""
import csv
import json
import os
import sys
import time

import numpy as np
from scipy.spatial.distance import pdist, squareform


def _repo_root():
    d = os.path.dirname(os.path.abspath(__file__))
    while d != os.path.dirname(d):
        if (os.path.isdir(os.path.join(d, "experiments"))
                and os.path.isdir(os.path.join(d, "data"))):
            return d
        d = os.path.dirname(d)
    raise RuntimeError("repo root (holding experiments/ and data/) not found")


ROOT = _repo_root()
sys.path.insert(0, ROOT)

from experiments.clustering import features as F                                  # noqa: E402
from experiments.clustering import sweep as S                                     # noqa: E402
from experiments.equivalence_classes.lib.autcanon import aut_canon                # noqa: E402
from experiments.equivalence_classes.lib.words import canon_pair, ms_presentation  # noqa: E402
from experiments.equivalence_classes.phases.phase0_provenance import load_grid    # noqa: E402

TABLES = os.path.join(ROOT, "results", "equivalence_classes", "ms1190_tables")
OUT = os.path.join(ROOT, "results", "clustering")

KS = (2, 3, 4, 5, 6)
METRICS = ("euclidean", "cosine", "correlation")
N_PERM = 1000
SEED = 0


# ------------------------------------------------------------------------------- populations

def pop_tables():
    """The 113 solved Aut(F2)-orbit reps + the 124 unsolved ACA-class reps. NOT the 261 reps.

    The 261 are the pre-quotient unsolved representatives; clustering them would count the same
    problem up to 34 times over (``13_1`` alone is carried by 34 (w, n) cells) and any structure
    found would be dominated by that multiplicity. The counts are asserted, not assumed.
    """
    rows = []
    with open(os.path.join(TABLES, "solved_640_aut_orbits.csv")) as f:
        for r in csv.DictReader(f):
            rows.append((r["aut_id"], 0, r["rep_r1"], r["rep_r2"]))
    n_solved = len(rows)
    with open(os.path.join(TABLES, "unsolved_124_aca_classes.csv")) as f:
        for r in csv.DictReader(f):
            rows.append((r["aca_id"], 1, r["rep_r1"], r["rep_r2"]))
    n_unsolved = len(rows) - n_solved
    if (n_solved, n_unsolved) != (113, 124):
        raise RuntimeError(
            f"population A must be 113 solved + 124 unsolved, got {n_solved} + {n_unsolved} "
            f"-- if this is 261 you are clustering the pre-quotient reps")
    # Both sides must BE their minimal automorphic state, not merely name one. Table A's reps are
    # aut_canon output by construction; table B's are an upstream artefact that happens to be
    # Aut-minimal -- so it is checked, for every row, on both sides.
    for name, lab, r1, r2 in rows:
        p = canon_pair(r1, r2)
        if aut_canon(p)[1] != p:
            raise RuntimeError(f"{name} is not its own minimal automorphic state: "
                               f"{p} -> {aut_canon(p)[1]}")
    return rows


def pop_provenance_matched():
    """Both sides identically produced: raw MS cell -> aut_canon -> unique orbits."""
    seen, rows = {}, []
    for (w, n, v) in load_grid():
        rep = aut_canon(canon_pair(*ms_presentation(n, w)))[1]
        lab = 0 if v == "trivial" else 1
        if rep in seen:
            if seen[rep] != lab:
                raise RuntimeError(f"orbit {rep} is both trivial and unsolved -- impossible")
            continue
        seen[rep] = lab
        rows.append((f"{'sol' if lab == 0 else 'uns'}_{w}@{n}", lab, rep[0], rep[1]))
    return rows


# ------------------------------------------------------------------ fast binary-label ARI null

def _auc(x, y):
    """Rank AUC for a single scalar feature: P(x[unsolved] > x[solved]), ties at 0.5.
    0.5 is no signal; distance from 0.5 in either direction is the effect, and the direction
    matters as much as the size -- it says which way the hypothesis actually points."""
    order = np.argsort(x, kind="mergesort")
    ranks = np.empty(len(x), dtype=float)
    ranks[order] = np.arange(1, len(x) + 1)
    xs = np.sort(x)
    i = 0
    while i < len(xs):                                   # average ranks within ties
        j = i
        while j + 1 < len(xs) and xs[j + 1] == xs[i]:
            j += 1
        if j > i:
            ranks[order[i:j + 1]] = ranks[order[i:j + 1]].mean()
        i = j + 1
    n1 = int((y == 1).sum())
    n0 = len(y) - n1
    return float((ranks[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def knot_hypothesis(pairs, y):
    """Test the stated hypothesis directly: do solved and unsolved differ in KNOT NUMBER --
    how many blocks of one generator sit squashed inside the other, counted cyclically?

    Reports the raw count and the length-free density separately, because the count is
    confounded with length and the density is not.
    """
    k1 = np.array([F.knot_number(a) for a, b in pairs], dtype=float)
    k2 = np.array([F.knot_number(b) for a, b in pairs], dtype=float)
    kmax, kmin = np.maximum(k1, k2), np.minimum(k1, k2)
    kn = k1 + k2
    ln = np.array([len(a) + len(b) for a, b in pairs], dtype=float)
    runs = [[n for _, n in F.gen_runs(a)] + [n for _, n in F.gen_runs(b)] for a, b in pairs]
    mean_b = np.array([np.mean(r) for r in runs])
    max_b = np.array([np.max(r) for r in runs])
    std_b = np.array([np.std(r) for r in runs])
    feats = {
        # per-relator, which is the right granularity: a single busy relator is the signal,
        # and summing the two rings blurs it away. max/min are swap-invariant, unlike (k1, k2).
        "max knots (1 relator)": kmax,
        "min knots (1 relator)": kmin,
        # length-confounded: these grow with the word
        "knot number (r1+r2)":  kn,
        "mean block length":    mean_b,
        "max block length":     max_b,
        "total length":         ln,
        # scale-free: these are the honest test of "is the BLOCK STRUCTURE different?"
        "knot density":         kn / ln,
        "max block / length":   max_b / ln,
        "max / mean block":     max_b / np.where(mean_b == 0, 1, mean_b),
        "block CV (std/mean)":  std_b / np.where(mean_b == 0, 1, mean_b),
    }
    out = []
    for name, v in feats.items():
        s, u = v[y == 0], v[y == 1]
        pooled = np.sqrt((s.var(ddof=1) + u.var(ddof=1)) / 2) or 1.0
        out.append({
            "feature": name,
            "solved_mean": float(s.mean()), "unsolved_mean": float(u.mean()),
            "solved_median": float(np.median(s)), "unsolved_median": float(np.median(u)),
            "auc": _auc(v, y), "cohens_d": float((u.mean() - s.mean()) / pooled),
            "direction": "unsolved higher" if u.mean() > s.mean() else "unsolved lower",
        })
    hist = {}
    for lab, tag in ((0, "solved"), (1, "unsolved")):
        c = {}
        for v in kmax[y == lab]:
            c[int(v)] = c.get(int(v), 0) + 1
        hist[tag] = dict(sorted(c.items()))

    # The explicit threshold rule: "some relator carries more than t knots" => call it unsolved.
    # Swept rather than assumed, so the proposed t=3 is scored against its neighbours instead of
    # being the only number anyone looks at.
    rule = []
    for t in range(1, 9):
        pred = (kmax > t).astype(int)
        tp = int(((pred == 1) & (y == 1)).sum()); fp = int(((pred == 1) & (y == 0)).sum())
        fn = int(((pred == 0) & (y == 1)).sum()); tn = int(((pred == 0) & (y == 0)).sum())
        rule.append({
            "threshold": t, "tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "precision": tp / (tp + fp) if tp + fp else 0.0,
            "recall": tp / (tp + fn) if tp + fn else 0.0,
            "accuracy": (tp + tn) / len(y),
            "bal_acc": 0.5 * ((tp / (tp + fn) if tp + fn else 0.0)
                              + (tn / (tn + fp) if tn + fp else 0.0)),
        })
    # max_knots as a standalone statistic: the value -> class breakdown, which is the form that
    # says whether it is a gradient or a threshold, and the (min, max) joint, which says whether
    # the second relator adds anything once the busiest one is known.
    unev = np.array([(lambda r: max(r) / (sum(r) / len(r)))(
        [n for _, n in F.gen_runs(a)] + [n for _, n in F.gen_runs(b)]) for a, b in pairs])
    # Enumerate the FULL range from 0, not just the values that occur -- an omitted bucket reads
    # as "not counted" when it means "empty", and whether knots=0 or 1 ever appears is a real
    # question about the data. knots=0 DOES occur at relator level: 7 relators are the bare pure
    # power ``X``, which kills a generator outright. It never survives to a presentation's
    # max_knots, though, because the partner relator always carries at least 2.
    table = []
    for v in range(0, int(kmax.max()) + 1):
        m = kmax == v
        ns, nu = int(((y == 0) & m).sum()), int(((y == 1) & m).sum())
        table.append({
            "max_knots": v, "n_solved": ns, "n_unsolved": nu,
            "pct_unsolved": nu / (ns + nu) if ns + nu else 0.0,
            # within-bucket drill-down: what still separates the states that share a max_knots?
            "unev_solved": float(unev[m & (y == 0)].mean()) if ns else None,
            "unev_unsolved": float(unev[m & (y == 1)].mean()) if nu else None,
            "len_solved": float(ln[m & (y == 0)].mean()) if ns else None,
            "len_unsolved": float(ln[m & (y == 1)].mean()) if nu else None,
        })
    # min_knots gets the same treatment: "BOTH relators are busy" turns out to be a second,
    # largely independent sufficient condition, so it is not just a passenger of max.
    table_min = []
    for v in range(0, int(kmax.max()) + 1):
        m = kmin == v
        ns, nu = int(((y == 0) & m).sum()), int(((y == 1) & m).sum())
        table_min.append({"min_knots": v, "n_solved": ns, "n_unsolved": nu,
                          "pct_unsolved": nu / (ns + nu) if ns + nu else 0.0})

    joint = []
    for vmin in range(0, int(kmax.max()) + 1):
        for vmax in range(0, int(kmax.max()) + 1):
            m = (kmin == vmin) & (kmax == vmax)
            if not m.any():
                continue
            joint.append({"min_knots": vmin, "max_knots": vmax,
                          "n_solved": int(((y == 0) & m).sum()),
                          "n_unsolved": int(((y == 1) & m).sum())})

    # The solved states occupy a tight box in (min_knots, max_knots). Anything outside it is
    # unsolved -- two sufficient conditions that overlap far less than they look like they should.
    rules2 = []
    conds = {
        "max_knots >= 4  (some relator is busy)": kmax >= 4,
        "min_knots >= 3  (BOTH relators are busy)": kmin >= 3,
        "either of the two": (kmax >= 4) | (kmin >= 3),
        "both of the two": (kmax >= 4) & (kmin >= 3),
    }
    for nm, c in conds.items():
        fs, fu = int(((y == 0) & c).sum()), int(((y == 1) & c).sum())
        rules2.append({"rule": nm, "n_solved": fs, "n_unsolved": fu,
                       "precision": fu / (fs + fu) if fs + fu else 0.0,
                       "recall": fu / max(int((y == 1).sum()), 1)})
    box = {"solved_max_range": [int(kmax[y == 0].min()), int(kmax[y == 0].max())],
           "solved_min_range": [int(kmin[y == 0].min()), int(kmin[y == 0].max())],
           "unsolved_max_range": [int(kmax[y == 1].min()), int(kmax[y == 1].max())],
           "unsolved_min_range": [int(kmin[y == 1].min()), int(kmin[y == 1].max())]}
    # Per-relator distribution too: whether knots=0 or 1 occurs at RELATOR level is a different
    # question from whether it occurs as a presentation's max.
    per_rel = []
    for v in range(0, int(kmax.max()) + 1):
        per_rel.append({
            "knots": v,
            "n_solved": int(((k1 == v) & (y == 0)).sum() + ((k2 == v) & (y == 0)).sum()),
            "n_unsolved": int(((k1 == v) & (y == 1)).sum() + ((k2 == v) & (y == 1)).sum()),
        })
    low = sorted({a for a, b in pairs if F.knot_number(a) <= 1}
                 | {b for a, b in pairs if F.knot_number(b) <= 1})
    return {"features": out, "knot_hist": hist, "rule": rule, "table": table,
            "table_min": table_min, "joint": joint, "rules2": rules2, "box": box,
            "per_relator": per_rel, "low_knot_relators": low,
            "kmax": kmax.tolist(), "kmin": kmin.tolist()}


def _ari_from_counts(m, nc, nA, n):
    """Vectorised ARI between a clustering (cluster sizes ``nc``, per-cluster class-1 counts ``m``)
    and a binary labelling with ``nA`` positives. ``m`` is (n_clusters, n_perm)."""
    c2 = lambda x: x * (x - 1) / 2.0
    sij = (c2(m) + c2(nc[:, None] - m)).sum(0)
    si = c2(nc).sum()
    sj = c2(nA) + c2(n - nA)
    exp = si * sj / c2(n)
    mx = (si + sj) / 2.0
    return np.where(mx == exp, 0.0, (sij - exp) / (mx - exp))


def analyse(tag, rows, rng, verbose=True):
    t0 = time.time()
    ids = [r[0] for r in rows]
    y = np.array([r[1] for r in rows])
    pairs = [(r[2], r[3]) for r in rows]
    n = len(rows)
    lens = np.array([len(a) + len(b) for a, b in pairs], dtype=float)
    say = print if verbose else (lambda *a, **k: None)
    say(f"\n{'=' * 78}\nPOPULATION {tag}: {n} states "
        f"({(y == 0).sum()} solved / {(y == 1).sum()} unsolved)\n{'=' * 78}")
    say(f"  length  solved  mean {lens[y == 0].mean():.1f}  median {np.median(lens[y == 0]):.0f}")
    say(f"  length  unsolv  mean {lens[y == 1].mean():.1f}  median {np.median(lens[y == 1]):.0f}")

    inv = F.rotation_invariance_report(pairs[:40], rng)
    bad = sorted(k for k, v in inv.items() if v > 1e-9)
    if bad:
        raise RuntimeError(f"representations are not rotation-invariant: {bad}")
    say(f"  [gate] rotation invariance: all {len(inv)} representations invariant "
        f"(max dev {max(inv.values()):.1e})")

    faithful = {}
    for name in F.REPRESENTATIONS:
        X = F.build(pairs, name)
        faithful[name] = len({tuple(np.round(v, 9)) for v in X})
    say(f"  [gate] faithfulness: " + ", ".join(
        f"{k} {v}/{n}" for k, v in sorted(faithful.items(), key=lambda kv: -kv[1])[:4]))

    grid, memberships = [], []
    for rep in F.REPRESENTATIONS:
        X0 = F.build(pairs, rep)
        for pname, pfun in S.PREPROC.items():
            Xp = pfun(X0, lens)
            for metric in METRICS:
                D = squareform(pdist(Xp, metric=metric))
                D[~np.isfinite(D)] = 0.0
                for (algo, k), lab in S.cluster_all(Xp, D, KS, seed=SEED).items():
                    if len(np.unique(lab)) < 2:
                        continue
                    grid.append({
                        "representation": rep, "preproc": pname, "metric": metric,
                        "algorithm": algo, "k": int(len(np.unique(lab))),
                        "ari": S.adjusted_rand(lab, y), "nmi": S.nmi(lab, y),
                        "bal_acc": S.balanced_accuracy(lab, y),
                        "_lab": lab.tolist(),
                    })
                    u = np.unique(lab)
                    M = np.zeros((len(u), n))
                    for i, c in enumerate(u):
                        M[i, lab == c] = 1.0
                    memberships.append(M)
    grid.sort(key=lambda r: -r["ari"])
    best = grid[0]

    # What the clustering found ON ITS OWN TERMS. Described by intrinsic quantities only; the
    # label column is appended last and is the single post-hoc line, not the basis of the split.
    blab = np.array(best["_lab"])
    kmx = np.array([max(F.knot_number(a), F.knot_number(b)) for a, b in pairs], dtype=float)
    unev = np.array([(lambda r: max(r) / (sum(r) / len(r)))(
        [n for _, n in F.gen_runs(a)] + [n for _, n in F.gen_runs(b)]) for a, b in pairs])
    profile = []
    for c in np.unique(blab):
        m = blab == c
        profile.append({
            "cluster": int(c), "n": int(m.sum()),
            "mean_length": float(lens[m].mean()),
            "mean_max_knots": float(kmx[m].mean()),
            "mean_unevenness": float(unev[m].mean()),
            "pct_unsolved": float((y[m] == 1).mean()),   # post-hoc only
        })
    for r in grid:
        r.pop("_lab", None)
    say(f"  [sweep] {len(grid)} clusterings   best ARI {best['ari']:.4f}  "
        f"bal_acc {best['bal_acc']:.3f}   ({best['representation']} / {best['preproc']} / "
        f"{best['metric']} / {best['algorithm']} k={best['k']})")

    Mall = np.vstack(memberships)
    ncl = Mall.sum(1)
    perms = np.column_stack([rng.permutation(y) for _ in range(N_PERM)]).astype(float)
    counts = Mall @ perms
    nA = int((y == 1).sum())
    off, best_null = 0, np.full(N_PERM, -np.inf)
    for M in memberships:
        h = M.shape[0]
        best_null = np.maximum(
            best_null, _ari_from_counts(counts[off:off + h], ncl[off:off + h], nA, n))
        off += h
    p_val = float((best_null >= best["ari"]).mean())
    say(f"  [null]  best-of-grid on {N_PERM} permuted labellings: mean {best_null.mean():.4f}  "
        f"p95 {np.percentile(best_null, 95):.4f}  max {best_null.max():.4f}  ->  p = {p_val:.4f}")

    ceiling = []
    for rep in F.REPRESENTATIONS:
        X = S.zscore(F.build(pairs, rep))
        Xr = S.zscore(S.residualize(X, lens))
        ceiling.append({
            "representation": rep,
            "knn5": S.knn_cv(X, y, 5, seed=SEED),
            "knn15": S.knn_cv(X, y, 15, seed=SEED),
            "logreg": S.logreg_cv(S.pca(X, min(30, X.shape[1])), y, seed=SEED),
            "logreg_nolen": S.logreg_cv(S.pca(Xr, min(30, Xr.shape[1])), y, seed=SEED),
        })
    ctrl = next(c for c in ceiling if c["representation"] == "shape (control)")
    bestc = max(ceiling, key=lambda c: c["logreg_nolen"])
    say(f"  [ceiling] length-only control: logreg {ctrl['logreg']:.3f}   |   "
        f"best with length removed: {bestc['representation']} {bestc['logreg_nolen']:.3f}")

    lo, hi = 13, 25
    band = (lens >= lo) & (lens <= hi)
    matched = []
    if band.sum() > 30 and (y[band] == 0).sum() > 5 and (y[band] == 1).sum() > 5:
        yb = y[band]
        sub = [pairs[i] for i in np.flatnonzero(band)]
        for rep in F.REPRESENTATIONS:
            Xb = S.zscore(F.build(sub, rep))
            Db = squareform(pdist(Xb, metric="cosine"))
            Db[~np.isfinite(Db)] = 0.0
            bb = max((S.adjusted_rand(lab, yb)
                      for lab in S.cluster_all(Xb, Db, KS, seed=SEED).values()
                      if len(np.unique(lab)) > 1), default=0.0)
            matched.append({"representation": rep, "best_ari": bb,
                            "knn5": S.knn_cv(Xb, yb, 5, seed=SEED)})
        mb = max(matched, key=lambda m: m["best_ari"])
        mc = next(m for m in matched if m["representation"] == "shape (control)")
        say(f"  [matched {lo}-{hi}] {int(band.sum())} states "
            f"({int((yb == 0).sum())}/{int((yb == 1).sum())})   best ARI {mb['best_ari']:+.4f} "
            f"({mb['representation']})   length-only control {mc['best_ari']:+.4f}")

    knot = knot_hypothesis(pairs, y)
    # The same features inside the matched length band. A scale-free block statistic that keeps
    # its AUC here is not length in disguise; one that collapses to 0.5 was.
    knot_m = knot_hypothesis([pairs[i] for i in np.flatnonzero(band)], y[band]) \
        if band.sum() > 30 else {"features": [], "knot_hist": {}}
    m_auc = {r["feature"]: r["auc"] for r in knot_m["features"]}
    for r in knot["features"]:
        r["auc_matched"] = m_auc.get(r["feature"])
    say("  [knots] cyclic block-count hypothesis (AUC 0.5 = no signal; matched = within band)")
    for r in knot["features"]:
        mm = f"{r['auc_matched']:.3f}" if r["auc_matched"] is not None else "  -  "
        say(f"     {r['feature']:23s} solved {r['solved_mean']:6.2f}  unsolved "
            f"{r['unsolved_mean']:6.2f}   AUC {r['auc']:.3f}  matched {mm}  "
            f"d {r['cohens_d']:+.2f}")
    say("  [rule] \"some relator has > t knots\" => unsolved")
    say(f"     {'t':>3} {'bal_acc':>8} {'prec':>6} {'recall':>7}   tp/fp/fn/tn")
    for r in knot["rule"]:
        star = "  <-- proposed" if r["threshold"] == 3 else ""
        say(f"     {r['threshold']:>3} {r['bal_acc']:8.3f} {r['precision']:6.3f} "
            f"{r['recall']:7.3f}   {r['tp']}/{r['fp']}/{r['fn']}/{r['tn']}{star}")
    say("  [max_knots] value -> class breakdown  (max over the two relators)")
    say(f"     {'v':>2} {'solved':>7} {'unsolved':>9} {'% unsolved':>11}   "
        f"{'unevenness s/u':>16}  {'length s/u':>12}")
    for r in knot["table"]:
        us = f"{r['unev_solved']:.2f}" if r["unev_solved"] is not None else "  - "
        uu = f"{r['unev_unsolved']:.2f}" if r["unev_unsolved"] is not None else "  - "
        ls = f"{r['len_solved']:.1f}" if r["len_solved"] is not None else "  - "
        lu = f"{r['len_unsolved']:.1f}" if r["len_unsolved"] is not None else "  - "
        empty = "   <-- EMPTY" if r["n_solved"] + r["n_unsolved"] == 0 else ""
        say(f"     {r['max_knots']:>2} {r['n_solved']:>7} {r['n_unsolved']:>9} "
            f"{r['pct_unsolved']*100:>10.1f}%   {us:>7} / {uu:<7} {ls:>5} / {lu:<5}{empty}")
    say("  [per relator] knot_number over all 474 relators "
        "(0 = a pure power: it kills a generator, nothing is squashed)")
    for r in knot["per_relator"]:
        tot = r["n_solved"] + r["n_unsolved"]
        say(f"     {r['knots']:>2} {tot:>6}   ({r['n_solved']} in solved, {r['n_unsolved']} in "
            f"unsolved){'   <-- EMPTY' if tot == 0 else ''}")
    say(f"     relators with knots <= 1: {knot['low_knot_relators']}")
    say("  [min_knots] BOTH relators at least this busy")
    for r in knot["table_min"]:
        tot = r["n_solved"] + r["n_unsolved"]
        say(f"     {r['min_knots']:>2} {r['n_solved']:>7} {r['n_unsolved']:>9} "
            f"{r['pct_unsolved']*100:>10.1f}%{'   <-- EMPTY' if tot == 0 else ''}")
    b = knot["box"]
    say(f"  [box] solved live in max_knots {b['solved_max_range']} and min_knots "
        f"{b['solved_min_range']}; unsolved reach max {b['unsolved_max_range']} / min "
        f"{b['unsolved_min_range']}")
    for r in knot["rules2"]:
        say(f"     {r['rule']:42s} {r['n_solved']:>3} solved / {r['n_unsolved']:>3} unsolved  "
            f"precision {r['precision']:.3f}  recall {r['recall']:.3f}")

    coords = {}
    for rep in ("ring_dual", "ring_autocorr", "kmer3", "all", "shape (control)"):
        P = S.pca(S.zscore(F.build(pairs, rep)), 2)
        coords[rep] = [[round(float(a), 4), round(float(b), 4)] for a, b in P]

    return {
        "tag": tag, "n": n, "n_solved": int((y == 0).sum()), "n_unsolved": int((y == 1).sum()),
        "len_solved_mean": float(lens[y == 0].mean()), "len_unsolved_mean": float(lens[y == 1].mean()),
        "n_clusterings": len(grid), "n_perm": N_PERM,
        "rotation_invariance": inv, "faithfulness": faithful,
        "best": best, "top": grid[:25], "grid": grid,
        "null": {"mean": float(best_null.mean()), "p95": float(np.percentile(best_null, 95)),
                 "max": float(best_null.max()), "p_value": p_val},
        "knots": knot, "profile": profile,
        "ceiling": ceiling, "matched": matched, "matched_band": [lo, hi],
        "matched_n": int(band.sum()), "matched_solved": int((y[band] == 0).sum()),
        "matched_unsolved": int((y[band] == 1).sum()),
        "labels": y.tolist(), "ids": ids, "lengths": lens.tolist(), "coords": coords,
        "seconds": round(time.time() - t0, 1),
    }


def main():
    t0 = time.time()
    rng = np.random.default_rng(SEED)
    out = {}
    for tag, rows in (("tables", pop_tables()),
                      ("provenance-matched", pop_provenance_matched())):
        out[tag] = analyse(tag, rows, rng)

    a, b = out["tables"], out["provenance-matched"]
    print(f"\n{'=' * 78}\nVERDICT\n{'=' * 78}")
    print(f"  tables            best ARI {a['best']['ari']:.4f}  (null max "
          f"{a['null']['max']:.4f}, p={a['null']['p_value']:.4f})")
    print(f"  provenance-matched best ARI {b['best']['ari']:.4f}  (null max "
          f"{b['null']['max']:.4f}, p={b['null']['p_value']:.4f})")
    print(f"  -> separation {'SURVIVES' if b['null']['p_value'] < 0.01 else 'COLLAPSES'} "
          f"the provenance control")

    os.makedirs(OUT, exist_ok=True)
    for tag, pay in out.items():
        slug = tag.replace(" ", "_")
        with open(os.path.join(OUT, f"cluster_grid_{slug}.csv"), "w", newline="") as f:
            cols = [c for c in pay["grid"][0].keys()]
            wtr = csv.DictWriter(f, fieldnames=cols)
            wtr.writeheader()
            wtr.writerows(pay["grid"])
        pay.pop("grid")
    with open(os.path.join(OUT, "cluster_report.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(f"\nwrote -> {os.path.relpath(OUT, ROOT)}/  ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
