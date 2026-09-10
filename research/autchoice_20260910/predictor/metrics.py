"""Per-row ranking metrics for the image-choice problem, and their aggregation.

A *ranker* gives every row an ordering of its 13 images (best first).  For one row with
costs ``nodes`` (a censored image carries the budget, 20,000) and ``solved`` flags:

    top1_regret     log10(nodes[top1]) - log10(min nodes in the ball)
    top1_solved     the top-1 image solves within the budget
    top3_solved     some image among the top 3 solves within the budget
    top1_solved_5k  the top-1 image solves within 5,000 pops
    rank_of_best    1 + position of the cheapest image in the ranking; when several images
                    tie at the minimum (e.g. an all-censored ball) the best-placed one counts
    portfolio_k     for k in KS: the top-k images run with budget//k pops each solve the row
                    iff some top-k image has nodes <= budget // k (rescored from the atlas)
    hedged_k        the identity plus the top k-1 non-identity images, budget//k each

``aggregate`` averages the per-row values over a set of rows (fractions for the booleans,
mean for the regret and the rank) and also returns the raw solve counts.
"""
import numpy as np

KS = (1, 2, 3, 5, 13)
METRIC_NAMES = ('top1_regret', 'top1_solved', 'top3_solved', 'top1_solved_5k', 'rank_of_best') \
    + tuple(f'portfolio_{k}' for k in KS) + tuple(f'hedged_{k}' for k in KS)


def row_metrics(order, nodes, solved, budget=20000, small=5000, identity=None):
    """``identity``: position of the identity image (needed for ``hedged_k``; default: the
    image whose cost the caller marks, else position 0 of the row)."""
    order = [int(i) for i in order]
    nodes = np.asarray(nodes, float)
    solved = np.asarray(solved, bool)
    assert len(order) == len(nodes) and sorted(order) == list(range(len(nodes)))
    cost = np.where(solved, nodes, float(budget))
    best = cost.min()
    t1 = order[0]
    out = {
        'top1_regret': float(np.log10(cost[t1]) - np.log10(best)),
        'top1_solved': bool(solved[t1] and cost[t1] <= budget),
        'top3_solved': bool(any(solved[i] and cost[i] <= budget for i in order[:3])),
        'top1_solved_5k': bool(solved[t1] and cost[t1] <= small),
        'rank_of_best': int(min(pos + 1 for pos, i in enumerate(order) if cost[i] == best)),
    }
    for k in KS:
        b = budget // k
        out[f'portfolio_{k}'] = bool(any(solved[i] and cost[i] <= b for i in order[:k]))
    ident = 0 if identity is None else int(identity)
    rest = [i for i in order if i != ident]
    for k in KS:
        b = budget // k
        picks = [ident] + rest[:k - 1]
        out[f'hedged_{k}'] = bool(any(solved[i] and cost[i] <= b for i in picks))
    return out


def oracle_row_metrics(nodes, solved, budget=20000, small=5000, identity=None):
    """The metrics of a ranker that knows the costs (best image first)."""
    cost = np.where(np.asarray(solved, bool), np.asarray(nodes, float), float(budget))
    return row_metrics(list(np.argsort(cost, kind='stable')), nodes, solved, budget, small, identity)


def aggregate(per_row, rows=None):
    """``per_row``: list of metric dicts (one per row).  Mean of every metric over ``rows``
    (indices; default all) plus ``n`` and integer solve counts for the boolean metrics."""
    if rows is None:
        rows = range(len(per_row))
    rows = list(rows)
    out = {'n': len(rows)}
    if not rows:
        return out
    for m in METRIC_NAMES:
        vals = np.asarray([per_row[i][m] for i in rows], float)
        out[m] = float(vals.mean())
        if m.startswith('top') and m != 'top1_regret' or m.startswith(('portfolio', 'hedged')):
            out[m + '_count'] = int(vals.sum())
    return out
