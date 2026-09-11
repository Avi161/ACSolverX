"""Learned rankers, fitted on training rows only, numpy throughout.

**Pairwise logistic ranking** (``fit_pairwise``).  For every training row take all ordered
pairs (i, j) of its images with cost_i < cost_j -- a censored image counts as dearer than
every solved one, two censored images give no pair, two solved images with equal pops give
no pair.  With ``d = x_i - x_j`` (features standardised on the training images) fit the
score ``s(x) = w . x`` (lower = cheaper) by minimising

    sum_p  omega_p * log(1 + exp(w . d_p))  +  lam/2 * |w|^2

i.e. logistic regression without intercept on the differences, ``P(i cheaper) = sigma(-w.d)``.
Newton's method (p = 72 columns, at most ~9k pairs; a dozen iterations).  ``omega_p = 1``
in the plain variant; ``rownorm`` gives each row total weight 1 so rows with many solved
images (78 pairs) do not dominate rows with few.  Per-row centring of the features would
be a no-op here (differences inside a row cancel any row-level offset).

**Identity bonus** (``ranker_from_weights(model, identity_bonus)``): a scalar subtracted from
the identity's score, chosen by ``evaluate.py`` on inner out-of-fold scores over ``BONUSES``;
the pick deviates from the row as given only when some image beats it by more than the bonus.

**Feature subsets** let the report say where the signal is: ``all``, ``state`` (the 28
numeric state features only), ``gen`` (depth / identity / same_gen / generator one-hots).

**seq prior** (``fit_seq_prior``): the mean within-row cost rank of each of the 13
sequences over the training rows; a test row's images are ordered by that prior.  It uses
no state feature at all.

**Rule search** (``fit_rule``): a small dictionary of orderings selected on the training
rows by mean top1_regret -- single feature (either sign, with or without depth-2 priority)
and two-feature within-row rank sums.  ``rule_order`` applies a rule to a row.

``ranker_from_weights`` turns fitted weights into the ``f(row) -> order`` shape used by
``baselines``; every learned ranker breaks ties like ``baselines.score_order``.
"""
import itertools

import numpy as np

from research.autchoice_20260910.predictor.baselines import COL, score_order
from research.autchoice_20260910.predictor.data import EXTRA_KEYS, FEATURE_KEYS, VECTOR_NAMES, standardise
from research.autchoice_20260910.predictor.metrics import row_metrics

SUBSETS = {
    'all': tuple(VECTOR_NAMES),
    'state': tuple(FEATURE_KEYS),
    'gen': tuple(EXTRA_KEYS) + tuple(n for n in VECTOR_NAMES if n.startswith('gen')),
}
LAMS = (0.01, 0.1, 1.0, 10.0, 100.0)


# ------------------------------------------------------------------ pairwise logistic
def make_pairs(d, image_idx, budget=None):
    """Indices ``(I, J, row)`` with cost_I < cost_J inside each row among ``image_idx``."""
    budget = budget or d['budget']
    I, J, R = [], [], []
    for g in sorted(set(d['group'][image_idx])):
        idx = image_idx[d['group'][image_idx] == g]
        cost = np.where(d['solved'][idx], d['nodes'][idx], budget)
        cens = d['censored'][idx]
        for a, b in itertools.permutations(range(len(idx)), 2):
            if cens[a] or (cens[b] and cens[a]):
                continue
            if cost[a] < cost[b]:
                I.append(idx[a])
                J.append(idx[b])
                R.append(g)
    return np.asarray(I), np.asarray(J), np.asarray(R)


def fit_pairwise(D, lam, weights=None, iters=25, tol=1e-9):
    """Newton minimisation of the weighted pairwise logistic loss; returns ``w``."""
    m, p = D.shape
    om = np.ones(m) if weights is None else np.asarray(weights, float)
    w = np.zeros(p)
    prev = np.inf
    for _ in range(iters):
        z = D @ w
        s = 1.0 / (1.0 + np.exp(-z))                       # sigma(w.d): P(pair violated)
        loss = float((om * np.logaddexp(0, z)).sum() + 0.5 * lam * w @ w)
        grad = D.T @ (om * s) + lam * w
        H = (D * (om * s * (1 - s))[:, None]).T @ D + lam * np.eye(p)
        step = np.linalg.solve(H, grad)
        # backtracking so the loss never increases
        t = 1.0
        while t > 1e-6:
            w_new = w - t * step
            z_new = D @ w_new
            l_new = float((om * np.logaddexp(0, z_new)).sum() + 0.5 * lam * w_new @ w_new)
            if l_new <= loss:
                break
            t *= 0.5
        w = w_new
        if abs(prev - l_new) < tol * max(1.0, abs(l_new)):
            break
        prev = l_new
    return w


def pairwise_model(d, train_idx, lam, subset='all', rownorm=False):
    """Fit on the images ``train_idx``; returns ``{w, mean, std, cols, names, lam, n_pairs}``."""
    cols = np.array([COL[n] for n in SUBSETS[subset]])
    mean, std = standardise(d['X'][train_idx][:, cols])
    I, J, R = make_pairs(d, train_idx)
    Xs = (d['X'][:, cols] - mean) / std
    D = Xs[I] - Xs[J]
    om = None
    if rownorm:
        counts = {g: int((R == g).sum()) for g in set(R)}
        om = np.array([1.0 / counts[g] for g in R])
    w = fit_pairwise(D, lam, om)
    return {'w': w, 'mean': mean, 'std': std, 'cols': cols, 'names': list(SUBSETS[subset]),
            'lam': lam, 'subset': subset, 'rownorm': rownorm, 'n_pairs': int(len(I))}


def pairwise_scores(model, X):
    return ((X[:, model['cols']] - model['mean']) / model['std']) @ model['w']


def ranker_from_weights(model, identity_bonus=0.0):
    """``identity_bonus`` is subtracted from the identity's score: the ranker leaves the row
    as given unless some image scores lower by more than the bonus (a hedge against
    deviating on rows the identity already solves cheaply)."""
    def f(row):
        s = pairwise_scores(model, row['X']) - identity_bonus * row['is_identity']
        return score_order(row, s)
    return f


BONUSES = (0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0)


# ------------------------------------------------------------------ seq prior
def _cost_ranks(cost):
    """Average ranks (1 = cheapest) with ties averaged."""
    order = np.argsort(cost, kind='mergesort')
    r = np.empty(len(cost))
    sc = cost[order]
    i = 0
    while i < len(cost):
        j = i
        while j + 1 < len(cost) and sc[j + 1] == sc[i]:
            j += 1
        r[order[i:j + 1]] = (i + j) / 2.0 + 1
        i = j + 1
    return r


def fit_seq_prior(d, train_idx):
    """``{seq_tuple: mean within-row cost rank}`` over the training rows."""
    acc = {}
    for g in sorted(set(d['group'][train_idx])):
        idx = train_idx[d['group'][train_idx] == g]
        cost = np.where(d['solved'][idx], d['nodes'][idx], d['budget']).astype(float)
        for i, r in zip(idx, _cost_ranks(cost)):
            acc.setdefault(d['seq'][i], []).append(r)
    return {k: float(np.mean(v)) for k, v in acc.items()}


def seq_prior_ranker(prior, default=7.0):
    def f(row):
        return score_order(row, [prior.get(tuple(s), default) for s in row['seq']])
    return f


# ------------------------------------------------------------------ rule search
def _within_row_ranks(v):
    return _cost_ranks(np.asarray(v, float))


def rule_order(rule, row):
    """Apply ``rule`` = (kind, spec) to a row view; returns an order."""
    kind, spec = rule
    X = row['X']
    h = X[:, COL['h_s20mk2']]
    if kind == 'single':
        feat, sign, d2 = spec
        v = sign * X[:, COL[feat]]
        key = (-row['depth'] if d2 else np.zeros(len(v)))
        scores = list(zip(key, v, h))
        return sorted(range(len(v)), key=lambda i: (scores[i], int(row['depth'][i]), tuple(row['seq'][i])))
    if kind == 'ranksum':
        (f1, s1), (f2, s2) = spec
        v = _within_row_ranks(s1 * X[:, COL[f1]]) + _within_row_ranks(s2 * X[:, COL[f2]])
        return score_order(row, v)
    raise ValueError(kind)


def rule_candidates(features=FEATURE_KEYS):
    feats = [f for f in features]
    out = []
    for f in feats:
        for sign in (1, -1):
            for d2 in (False, True):
                out.append(('single', (f, sign, d2)))
    for (f1, f2) in itertools.combinations(feats, 2):
        for s1 in (1, -1):
            for s2 in (1, -1):
                out.append(('ranksum', ((f1, s1), (f2, s2))))
    return out


def fit_rule(d, train_idx, rows_view, candidates=None):
    """Pick the candidate with the smallest mean top1_regret (then most top-1 solves) on
    the training rows.  ``rows_view`` maps row id -> (row_view, nodes, solved)."""
    candidates = candidates or rule_candidates()
    groups = sorted(set(d['group'][train_idx]))
    best = None
    for rule in candidates:
        regret, solved = 0.0, 0
        for g in groups:
            view, nodes, sol = rows_view[g]
            m = row_metrics(rule_order(rule, view), nodes, sol, d['budget'])
            regret += m['top1_regret']
            solved += m['top1_solved']
        key = (regret / len(groups), -solved)
        if best is None or key < best[0]:
            best = (key, rule)
    return best[1], {'train_top1_regret': best[0][0], 'train_top1_solved': -best[0][1]}


def rule_ranker(rule):
    return lambda row: rule_order(rule, row)


def rule_name(rule):
    kind, spec = rule
    if kind == 'single':
        f, s, d2 = spec
        return f"{'depth2_first, then ' if d2 else ''}{'low' if s > 0 else 'high'} {f}"
    (f1, s1), (f2, s2) = spec
    return f"ranksum({'low' if s1 > 0 else 'high'} {f1}, {'low' if s2 > 0 else 'high'} {f2})"
