"""Tune a multi-feature heap priority on subset-60, then score it on presentations never tuned on.

The single-feature arms each fix their weight by hand. This searches the weights instead:

    priority(r1, r2) = (0, L)                                    if L <= T
                       (1, L + a1*knots + a2*max_knots + a3*smb) otherwise

which **subsumes** the arms already tested -- a1 large is lexicographic knots-first, a1 = 4 with
a2 = a3 = 0 is ``length+4.0*knots``, and all weights 0 with T = 0 is the baseline. The zero vector
is deliberately kept in the candidate pool so the tuner is always free to return "the baseline was
best"; a search space that cannot express the control will always seem to beat it.

Why this needs a held-out split at all: with four free parameters and 30 training presentations,
the tuner can fit the training set's accidents. The reported number is therefore always the
**test** score of the configuration chosen on train, averaged over several stratified splits, and
``train - test`` is printed as the overfitting gap rather than left for the reader to compute.

Splits are stratified by the benchmark's difficulty ``bin``, so a split cannot hand one side the
easy presentations -- with 17/60 solvable at budget 100, an unstratified split would swing the
achievable score by more than any heuristic does.

    python3 -m experiments.heuristic_search.tune_multi
"""
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.heuristic_search.hsearch import ROOT, feats, hsearch    # noqa: E402
from experiments.heuristic_search.run_sweep import (                     # noqa: E402
    MRL, OUT, SUBSETS, load, _sign_test,
)

BUDGET = 100                 # the user's screening budget; the local ceiling is 1,000
N_SPLITS = 5
N_CANDIDATES = 200
WORKERS = 8
LOCAL_MAX_WORKERS = int(os.environ.get("ACSOLVERX_MAX_WORKERS", "1"))
BASELINE = (0.0, 0.0, 0.0, 0.0)          # T, a1, a2, a3 -- exactly the length ordering


def make_priority(params):
    T, a1, a2, a3 = params

    def p(r1, r2):
        L, K, MK, S = feats(r1, r2)
        if L <= T:
            return (0, L)
        return (1, L + a1 * K + a2 * MK + a3 * S)
    return p


def evaluate(args):
    """Module-level so a spawn pool can pickle it. Returns (n_solved, total_nodes_on_solved)."""
    params, pres, budget = args
    p = make_priority(params)
    n, nodes = 0, 0
    for r1, r2 in pres:
        r = hsearch(r1, r2, budget, p, max_relator_length=MRL)
        if r["solved"]:
            n += 1
            nodes += r["nodes_explored"]
    return n, nodes


def candidates(rng, n):
    """Random search, with the baseline and the known single-feature winners always included.

    Random search rather than a grid: four parameters at even a coarse 6 levels is 1,296 configs,
    and the weights are continuous with no reason to sit on grid points. Random search spends the
    same budget on distinct values of every coordinate.
    """
    fixed = [BASELINE, (16.0, 4.0, 0.0, 0.0), (16.0, 40.0, 0.0, 0.0), (0.0, 4.0, 0.0, 0.0),
             (0.0, 0.0, 0.0, 4.0), (16.0, 0.0, 0.0, 4.0)]
    out = list(fixed)
    while len(out) < n:
        out.append((float(rng.choice([0, 8, 12, 16, 20, 24])),
                    float(rng.uniform(0, 10)), float(rng.uniform(0, 10)),
                    float(rng.uniform(0, 10))))
    return out[:n]


def stratified_split(rows, rng):
    """Half of each difficulty bin to train, half to test."""
    tr, te = [], []
    bins = {}
    for r in rows:
        bins.setdefault(r["bin"], []).append(r)
    for b in sorted(bins):
        idx = list(bins[b])
        rng.shuffle(idx)
        k = len(idx) // 2
        te += idx[:k]
        tr += idx[k:]
    return tr, te


def main():
    with open(os.path.join(SUBSETS, "benchmark_subset_60.json")) as f:
        rows = json.load(f)["subset"]
    by = {p: (r1, r2) for p, r1, r2 in load([r["pres_id"] for r in rows])}

    # WORKERS is capped at 1 locally: a pool's children outlive a reaped parent, and eighteen such
    # orphans once drove this machine into swap under a live editing session. Raise it only on
    # Colab, where the fleet is visible and disposable.
    report, pool = [], ProcessPoolExecutor(max_workers=min(WORKERS, LOCAL_MAX_WORKERS))
    try:
        for seed in range(N_SPLITS):
            rng = np.random.default_rng(seed)
            trr, ter = stratified_split(rows, rng)
            tr = [by[r["pres_id"]] for r in trr]
            te = [by[r["pres_id"]] for r in ter]
            cands = candidates(rng, N_CANDIDATES)

            scored = list(pool.map(evaluate, [(c, tr, BUDGET) for c in cands], chunksize=4))
            # Rank by solves, then by nodes spent -- a tie broken toward the cheaper search.
            order = sorted(range(len(cands)), key=lambda i: (-scored[i][0], scored[i][1]))
            best = cands[order[0]]

            tr_base = evaluate((BASELINE, tr, BUDGET))
            te_base = evaluate((BASELINE, te, BUDGET))
            te_best = evaluate((best, te, BUDGET))
            report.append({
                "seed": seed, "n_train": len(tr), "n_test": len(te),
                "params": {"T": best[0], "a_knots": best[1], "a_maxknots": best[2],
                           "a_smb": best[3]},
                "train_best": scored[order[0]][0], "train_baseline": tr_base[0],
                "test_best": te_best[0], "test_baseline": te_base[0],
                "test_gain": te_best[0] - te_base[0],
                "train_gain": scored[order[0]][0] - tr_base[0],
            })
            r = report[-1]
            print(f"  seed {seed}  T={best[0]:>4.0f} a_knots={best[1]:5.2f} "
                  f"a_maxknots={best[2]:5.2f} a_smb={best[3]:5.2f}   "
                  f"train {r['train_best']:>2d}/{len(tr)} (base {r['train_baseline']:>2d}, "
                  f"{r['train_gain']:+d})   "
                  f"TEST {r['test_best']:>2d}/{len(te)} (base {r['test_baseline']:>2d}, "
                  f"{r['test_gain']:+d})", flush=True)
    finally:
        pool.shutdown()

    tg = [r["test_gain"] for r in report]
    trg = [r["train_gain"] for r in report]
    w = sum(1 for g in tg if g > 0)
    l = sum(1 for g in tg if g < 0)
    print(f"\n{'=' * 88}\nMULTI-FEATURE TUNING  ·  subset-60, budget {BUDGET}, "
          f"{N_SPLITS} stratified splits, {N_CANDIDATES} configs each\n{'=' * 88}")
    print(f"  mean gain on TRAIN (what tuning bought): {np.mean(trg):+.1f} presentations")
    print(f"  mean gain on TEST  (what generalised)  : {np.mean(tg):+.1f} presentations")
    print(f"  overfitting gap                        : {np.mean(trg) - np.mean(tg):.1f}")
    print(f"  splits where the tuned model beat the baseline on test: {w}/{N_SPLITS} "
          f"(lost {l}), sign p={_sign_test(w, l):.3f}")
    print(f"  test gains per split: {tg}")

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "tune_multi.json"), "w") as f:
        json.dump({"budget": BUDGET, "n_splits": N_SPLITS, "n_candidates": N_CANDIDATES,
                   "splits": report, "mean_test_gain": float(np.mean(tg)),
                   "mean_train_gain": float(np.mean(trg))}, f, indent=1)
    print(f"\nwrote -> {os.path.relpath(OUT, ROOT)}/tune_multi.json")


if __name__ == "__main__":
    main()
