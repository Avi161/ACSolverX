"""The held-out protocol: the split is honest, the fit sees only training data, nothing leaks.

A held-out accuracy is only worth its digits if the machinery producing it is correct, and the
failure modes here are silent -- a split that drifts the base rate, a threshold that peeks at the
test half, a direction chosen from the full data. Each is pinned below, plus the empirical leakage
control (shuffled labels must fall to the base rate) which is the one check that would catch a
mistake none of the structural tests anticipated.
"""
import os
import sys

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from experiments.clustering.holdout_eval import (  # noqa: E402
    PUBLISHED, TEST_FRAC, apply_threshold, evaluate, fit_threshold, shuffle_control,
    stratified_split,
)
from experiments.clustering.rank_signals import candidates  # noqa: E402
from experiments.clustering.run_cluster_237 import pop_tables  # noqa: E402


@pytest.fixture(scope="module")
def tables():
    return pop_tables()


def test_split_is_a_partition_and_holds_the_fraction():
    y = np.r_[np.zeros(113, int), np.ones(124, int)]
    tr, te = stratified_split(y, TEST_FRAC, np.random.default_rng(0))
    assert len(np.intersect1d(tr, te)) == 0, "train and test overlap -- the score is meaningless"
    assert sorted(np.r_[tr, te].tolist()) == list(range(len(y)))
    assert len(te) == 71 and len(tr) == 166


def test_split_is_stratified():
    """Each class contributes its own 30%, so the test base rate cannot drift off the population."""
    y = np.r_[np.zeros(113, int), np.ones(124, int)]
    for s in range(25):
        _, te = stratified_split(y, TEST_FRAC, np.random.default_rng(s))
        assert int((y[te] == 0).sum()) == 34      # round(0.3 * 113)
        assert int((y[te] == 1).sum()) == 37      # round(0.3 * 124)


def test_split_is_seed_deterministic_but_seeds_really_differ():
    y = np.r_[np.zeros(113, int), np.ones(124, int)]
    a = stratified_split(y, TEST_FRAC, np.random.default_rng(7))[1]
    b = stratified_split(y, TEST_FRAC, np.random.default_rng(7))[1]
    c = stratified_split(y, TEST_FRAC, np.random.default_rng(8))[1]
    assert np.array_equal(np.sort(a), np.sort(b)), "same seed gave two different splits"
    assert not np.array_equal(np.sort(a), np.sort(c)), "two seeds gave the same split"


def test_threshold_fit_recovers_a_planted_cut_and_its_direction():
    y = np.r_[np.zeros(50, int), np.ones(50, int)]
    v = np.r_[np.full(50, 1.0), np.full(50, 3.0)]
    up = fit_threshold(v, y)
    assert up["sign"] == 1 and 1.0 <= up["t"] < 3.0
    assert apply_threshold(v, up).sum() == 50
    # The direction is fitted, not assumed: flipping the feature must flip the sign, not the score.
    down = fit_threshold(-v, y)
    assert down["sign"] == -1
    assert apply_threshold(-v, down).sum() == 50
    assert up["bal_acc"] == down["bal_acc"] == 1.0


def test_fit_never_touches_the_test_half():
    """Corrupting the held-out rows must leave the fitted rule byte-identical."""
    rng = np.random.default_rng(3)
    y = np.r_[np.zeros(60, int), np.ones(60, int)]
    v = np.r_[rng.normal(0, 1, 60), rng.normal(2, 1, 60)]
    tr, te = stratified_split(y, TEST_FRAC, np.random.default_rng(1))
    base = fit_threshold(v[tr], y[tr])
    poisoned = v.copy()
    poisoned[te] = 1e6
    assert fit_threshold(poisoned[tr], y[tr]) == base


def test_published_threshold_is_refit_identically_from_every_training_half(tables):
    """1.25 is not a fitted parameter in any meaningful sense -- 200 training halves all pick it.

    That is why the refit-per-split column and the fixed-rule line report the same number: with a
    threshold this stable there is nothing for the training step to overfit.
    """
    y = np.array([r[1] for r in tables])
    v = np.array([candidates(r[2], r[3])[PUBLISHED[0]] for r in tables])
    for s in range(200):
        tr, _ = stratified_split(y, TEST_FRAC, np.random.default_rng(s))
        rule = fit_threshold(v[tr], y[tr])
        assert (rule["t"], rule["sign"]) == (PUBLISHED[1], 1), f"seed {s} fitted {rule}"


@pytest.mark.slow
def test_shuffled_labels_collapse_to_the_base_rate(tables):
    """The empirical leakage guard. 0.98 held-out is a bug report until this line comes back flat."""
    ctrl = shuffle_control(tables, n_seeds=40)
    assert ctrl["acc_mean"] <= ctrl["base_rate"] + 0.03, (
        f"shuffled labels scored {ctrl['acc_mean']:.3f} against a base rate of "
        f"{ctrl['base_rate']:.3f} -- something is leaking the labels into the fit")


@pytest.mark.slow
def test_headline_holdout_numbers_are_stable(tables):
    """Regression pin on the reported result: a moved number here is a result change."""
    res = evaluate("A", tables, n_seeds=50, verbose=False)
    by = {r["feature"]: r for r in res["features"]}
    assert by["ALL (logistic)"]["acc_mean"] == pytest.approx(0.981, abs=0.015)
    assert by[PUBLISHED[0]]["acc_mean"] == pytest.approx(0.945, abs=0.015)
    assert by["max_knots"]["acc_mean"] == pytest.approx(0.853, abs=0.020)
    # Refitting the cut every split must equal never fitting it -- see the threshold-stability test.
    assert res["fixed_rule"]["acc_mean"] == pytest.approx(by[PUBLISHED[0]]["acc_mean"], abs=1e-12)
