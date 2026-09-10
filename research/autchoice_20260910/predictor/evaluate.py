"""Evaluate every ranker under group-disjoint cross-validation and write ``results.json``,
``weights.json`` and (via ``report.py``) ``PREDICTOR.md``.  Every number in the report
comes from here.

    PYTHONPATH=. python3 -m research.autchoice_20260910.predictor.evaluate

Protocol
  * 124 rows x 13 images from ``atlas.jsonl``; a row is the CV group.  5 outer folds by
    row, stratified by level, seed 0 (``data.folds``); asserted disjoint in ``data.split``.
  * Baselines need no training and are scored on every row (each row is held out of
    nothing); ``random`` is the per-row mean over 20 seeds.
  * Learned rankers are fitted on the 4 training folds and scored on the 5th.  The L2
    strength of a pairwise model is chosen INSIDE the training folds by a 4-fold inner
    group CV (seed 1) on mean top1_regret over ``train.LAMS``; a fixed-lambda sweep is also
    reported as a sensitivity check (it is not the selection procedure).  The rule search
    and the seq prior are likewise fitted on the training folds only.
  * Primary metric, declared before looking: mean top1_regret; secondary: top1_solved.
    The shipped ``weights.json`` is the pairwise variant with the best outer-CV primary
    metric, refitted on all 124 rows with the median of its per-fold chosen lambdas (and,
    for the hedge variant, the median of the per-fold identity bonuses).
  * ``pairwise_rownorm_hedge``: the same weights as ``pairwise_rownorm`` plus an *identity
    bonus* -- the row as given is kept unless an image beats it by more than the bonus --
    chosen on the inner out-of-fold scores (``train.BONUSES``), never on the test fold.
  * ``hedged_k``: identity + top-(k-1) non-identity images at budget//k each.
    Choosing among the handful of variants on the same outer folds is a small selection
    step; the report says so.
  * The portfolio rows: top-k images at budget//k pops each, rescored from the atlas.
"""
import json
import sys
from collections import Counter, OrderedDict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.equivalence_classes.lib.autcanon import AUTOS  # noqa: E402
from research.autchoice_20260910.predictor import data, train  # noqa: E402
from research.autchoice_20260910.predictor.baselines import BASELINES, random_ranker, row_view  # noqa: E402
from research.autchoice_20260910.predictor.metrics import KS, METRIC_NAMES, aggregate, oracle_row_metrics, row_metrics  # noqa: E402

HERE = Path(__file__).resolve().parent
K_OUTER, K_INNER, SEED_OUTER, SEED_INNER, N_RANDOM = 5, 4, 0, 1, 20
VARIANTS = OrderedDict([
    ('pairwise', dict(subset='all', rownorm=False)),
    ('pairwise_rownorm', dict(subset='all', rownorm=True)),
    ('pairwise_state_only', dict(subset='state', rownorm=False)),
    ('pairwise_gen_only', dict(subset='gen', rownorm=False)),
])
HEDGE_BASE, HEDGE = 'pairwise_rownorm', 'pairwise_rownorm_hedge'   # base + identity bonus


def rows_of(d):
    return {g: np.where(d['group'] == g)[0] for g in range(len(d['rows']))}


def score_rows(ranker, d, groups, views):
    """Per-row metric dicts of ``ranker`` on the rows ``groups``."""
    out = {}
    for g in groups:
        view, idx = views[g]
        ident = int(np.where(view['is_identity'])[0][0])
        out[g] = row_metrics(ranker(view), d['nodes'][idx], d['solved'][idx], d['budget'], identity=ident)
    return out


def cv_lambda(d, train_rows, views, cfg):
    """Inner group-CV choice of lambda on the training rows (mean top1_regret).  Also
    returns, for the chosen lambda, the identity bonus with the smallest mean top1_regret
    on the inner out-of-fold scores (``train.BONUSES``) and the regret of every bonus."""
    inner = data.folds(d, K_INNER, SEED_INNER, rows=train_rows)
    score, bonus_score = {}, {}
    for lam in train.LAMS:
        regret = {b: [] for b in train.BONUSES}
        for f in range(K_INNER):
            te = [g for g in train_rows if inner[g] == f]
            tr = [g for g in train_rows if inner[g] != f and inner[g] >= 0]
            tri = np.concatenate([views[g][1] for g in tr])
            m = train.pairwise_model(d, tri, lam, **cfg)
            for b in train.BONUSES:
                per = score_rows(train.ranker_from_weights(m, b), d, te, views)
                regret[b] += [v['top1_regret'] for v in per.values()]
        score[lam] = float(np.mean(regret[0.0]))
        bonus_score[lam] = {b: float(np.mean(v)) for b, v in regret.items()}
    best = min(train.LAMS, key=lambda l: (score[l], l))
    best_bonus = min(train.BONUSES, key=lambda b: (bonus_score[best][b], b))
    return best, score, best_bonus, bonus_score[best]


def summarise(per_row, groups, lev, frm):
    groups = list(groups)
    out = {'all': aggregate([per_row[g] for g in groups])}
    out['by_level'] = {l: aggregate([per_row[g] for g in groups if lev[g] == l])
                       for l in sorted(set(lev.values()), key=int)}
    out['by_form'] = {f: aggregate([per_row[g] for g in groups if frm[g] == f])
                      for f in sorted(set(frm.values()))}
    return out


def paired_vs(per_a, per_b, groups, metric='top1_solved'):
    wins = sum(1 for g in groups if per_a[g][metric] > per_b[g][metric])
    losses = sum(1 for g in groups if per_a[g][metric] < per_b[g][metric])
    return {'wins': wins, 'losses': losses}


def generator_counts(d, views, lev):
    """Which sequences / AUTOS indices are the cheapest image of a row (ties -> BFS-first,
    as in ATLAS.md); rows whose ball is entirely censored have no cheapest image."""
    seq_count, first, second, by_level = Counter(), Counter(), Counter(), {}
    n_rows, n_unique, same, diff, single, ident = 0, 0, 0, 0, 0, 0
    for g, (view, idx) in views.items():
        cost = np.where(d['solved'][idx], d['nodes'][idx], d['budget'])
        if not d['solved'][idx].any():
            continue
        n_rows += 1
        b = int(np.argmin(cost))
        n_unique += int((cost == cost[b]).sum() == 1)
        s = tuple(d['seq'][idx[b]])
        seq_count[s] += 1
        by_level.setdefault(lev[g], Counter())[s] += 1
        if len(s) == 0:
            ident += 1
        elif len(s) == 1:
            single += 1
            first[s[0]] += 1
        else:
            first[s[0]] += 1
            second[s[1]] += 1
            same += int(s[0] == s[1])
            diff += int(s[0] != s[1])
    fmt = lambda s: ' '.join(map(str, s)) or 'id'  # noqa: E731
    return {
        'rows_with_a_cheapest_image': n_rows, 'rows_with_unique_minimum': n_unique,
        'expected_per_seq_if_uniform': n_rows / 13.0,
        'cheapest_seq': OrderedDict((fmt(s), c) for s, c in seq_count.most_common()),
        'cheapest_seq_by_level': {l: OrderedDict((fmt(s), c) for s, c in cnt.most_common())
                                  for l, cnt in sorted(by_level.items(), key=lambda kv: int(kv[0]))},
        'first_generator': OrderedDict((str(i), c) for i, c in first.most_common()),
        'second_generator': OrderedDict((str(i), c) for i, c in second.most_common()),
        'autos': {str(i): f"x->{AUTOS[i]['x']}, y->{AUTOS[i]['y']}" for i in sorted(set(first) | set(second))},
        'depth2_same_generator': same, 'depth2_different_generators': diff,
        'depth1': single, 'identity': ident,
    }


def main():
    d = data.load()
    lev, frm = data.row_level_form(d)
    all_rows = list(range(len(d['rows'])))
    views = {g: (row_view(d, idx), idx) for g, idx in rows_of(d).items()}
    fold = data.folds(d, K_OUTER, SEED_OUTER)
    for f in range(K_OUTER):
        data.split(d, fold, f)                      # asserts row-disjointness
    results = {'protocol': {'rows': len(all_rows), 'images': int(len(d['y'])),
                            'features': int(d['X'].shape[1]), 'budget': d['budget'],
                            'k_outer': K_OUTER, 'k_inner': K_INNER, 'seed_outer': SEED_OUTER,
                            'seed_inner': SEED_INNER, 'n_random_seeds': N_RANDOM,
                            'lambda_grid': list(train.LAMS), 'primary_metric': 'top1_regret',
                            'fold_sizes_rows': np.bincount(fold).tolist(),
                            'solved_images': int(d['solved'].sum()),
                            'censored_images': int(d['censored'].sum())},
               'rankers': OrderedDict(), 'oracle': None, 'model': {}, 'rules': {},
               'generators': None}
    per = OrderedDict()

    # oracle
    per['oracle'] = {g: oracle_row_metrics(d['nodes'][idx], d['solved'][idx], d['budget'],
                                           identity=int(np.where(view['is_identity'])[0][0]))
                     for g, (view, idx) in views.items()}
    # baselines
    for name, fn in BASELINES.items():
        per[name] = score_rows(fn, d, all_rows, views)
    rnd = [score_rows(random_ranker(s), d, all_rows, views) for s in range(N_RANDOM)]
    per['random'] = {g: {m: float(np.mean([r[g][m] for r in rnd])) for m in METRIC_NAMES}
                     for g in all_rows}

    # learned rankers, outer CV
    model_info = {name: {'per_fold': []} for name in VARIANTS}
    per.update({name: {} for name in VARIANTS})
    per[HEDGE] = {}
    model_info[HEDGE] = {'per_fold': []}
    per['seq_prior'], per['rule'] = {}, {}
    fixed = {lam: {} for lam in train.LAMS}
    rule_info = {'per_fold': []}
    seq_prior_info = {'per_fold': []}
    for f in range(K_OUTER):
        tr_mask, te_mask = data.split(d, fold, f)
        tr_rows = [g for g in all_rows if fold[g] != f]
        te_rows = [g for g in all_rows if fold[g] == f]
        tri = np.where(tr_mask)[0]
        for name, cfg in VARIANTS.items():
            lam, inner, bonus, bonus_inner = cv_lambda(d, tr_rows, views, cfg)
            m = train.pairwise_model(d, tri, lam, **cfg)
            per_f = score_rows(train.ranker_from_weights(m), d, te_rows, views)
            per[name].update(per_f)
            agg = aggregate(list(per_f.values()))
            model_info[name]['per_fold'].append({
                'fold': f, 'test_rows': len(te_rows), 'lambda': lam,
                'inner_regret_by_lambda': {str(k): v for k, v in inner.items()},
                'n_pairs': m['n_pairs'], 'top1_regret': agg['top1_regret'],
                'top1_solved': agg['top1_solved'], 'top3_solved': agg['top3_solved'],
                'rank_of_best': agg['rank_of_best']})
            if name == HEDGE_BASE:
                per_h = score_rows(train.ranker_from_weights(m, bonus), d, te_rows, views)
                per[HEDGE].update(per_h)
                agg_h = aggregate(list(per_h.values()))
                model_info[HEDGE]['per_fold'].append({
                    'fold': f, 'test_rows': len(te_rows), 'lambda': lam, 'identity_bonus': bonus,
                    'inner_regret_by_bonus': {str(k): v for k, v in bonus_inner.items()},
                    'n_pairs': m['n_pairs'], 'top1_regret': agg_h['top1_regret'],
                    'top1_solved': agg_h['top1_solved'], 'top3_solved': agg_h['top3_solved'],
                    'rank_of_best': agg_h['rank_of_best']})
            if name == 'pairwise':
                for lam2 in train.LAMS:
                    m2 = train.pairwise_model(d, tri, lam2, **cfg)
                    fixed[lam2].update(score_rows(train.ranker_from_weights(m2), d, te_rows, views))
        prior = train.fit_seq_prior(d, tri)
        per['seq_prior'].update(score_rows(train.seq_prior_ranker(prior), d, te_rows, views))
        seq_prior_info['per_fold'].append({'fold': f, 'prior': {' '.join(map(str, k)) or 'id': v
                                                                 for k, v in sorted(prior.items(), key=lambda kv: kv[1])}})
        rule, info = train.fit_rule(d, tri, {g: (views[g][0], d['nodes'][views[g][1]], d['solved'][views[g][1]])
                                             for g in tr_rows})
        per_f = score_rows(train.rule_ranker(rule), d, te_rows, views)
        per['rule'].update(per_f)
        agg = aggregate(list(per_f.values()))
        rule_info['per_fold'].append({'fold': f, 'rule': train.rule_name(rule), **info,
                                      'test_top1_regret': agg['top1_regret'],
                                      'test_top1_solved': agg['top1_solved']})
        print(f"fold {f}: {len(te_rows)} test rows; "
              + '; '.join(f"{n} lam={model_info[n]['per_fold'][-1]['lambda']} regret={model_info[n]['per_fold'][-1]['top1_regret']:.3f}"
                          for n in VARIANTS)
              + f"; rule={train.rule_name(rule)} regret={agg['top1_regret']:.3f}", flush=True)

    # summaries
    for name, p in per.items():
        assert sorted(p) == all_rows, name
        s = summarise(p, all_rows, lev, frm)
        s['vs_identity_top1_solved'] = paired_vs(p, per['identity'], all_rows)
        s['vs_lowest_h_top1_solved'] = paired_vs(p, per['lowest_h'], all_rows)
        s['vs_depth2_first_top1_solved'] = paired_vs(p, per['depth2_first'], all_rows)
        s['portfolio'] = {str(k): {'solved': s['all'][f'portfolio_{k}_count'],
                                   'by_level': {l: s['by_level'][l][f'portfolio_{k}_count'] for l in s['by_level']}}
                          for k in KS}
        s['hedged'] = {str(k): {'solved': s['all'][f'hedged_{k}_count'],
                                'by_level': {l: s['by_level'][l][f'hedged_{k}_count'] for l in s['by_level']}}
                       for k in KS}
        if name == 'oracle':
            results['oracle'] = s
        else:
            results['rankers'][name] = s
    results['fixed_lambda_sweep'] = {str(lam): summarise(p, all_rows, lev, frm)['all'] for lam, p in fixed.items()}
    results['model'] = model_info
    results['rules'] = rule_info
    results['seq_prior'] = seq_prior_info
    results['generators'] = generator_counts(d, views, lev)

    # gap closed relative to the oracle, per ranker
    idn, orc = results['rankers']['identity'], results['oracle']
    for name, s in results['rankers'].items():
        s['gap_closed'] = {}
        for key, sub in (('all', s['all']), ('level_9', s['by_level'].get('9'))):
            base = idn['all'] if key == 'all' else idn['by_level']['9']
            top = orc['all'] if key == 'all' else orc['by_level']['9']
            s['gap_closed'][key] = {
                m: ((sub[m + '_count'] - base[m + '_count']) / max(1, top[m + '_count'] - base[m + '_count']))
                for m in ('top1_solved', 'top1_solved_5k')}

    # choose and ship (the hedge shares HEDGE_BASE's weights and adds the median inner-chosen bonus)
    order = sorted(list(VARIANTS) + [HEDGE], key=lambda n: (results['rankers'][n]['all']['top1_regret'],
                                                            -results['rankers'][n]['all']['top1_solved']))
    ship = order[0]
    bonus_ship = 0.0
    if ship == HEDGE:
        bonuses = [pf['identity_bonus'] for pf in model_info[HEDGE]['per_fold']]
        bonus_ship = float(np.median(bonuses))
        ship = HEDGE_BASE
    lams = [pf['lambda'] for pf in model_info[ship]['per_fold']]
    lam_ship = float(np.median(lams))
    if lam_ship not in train.LAMS:                       # median of an even count: nearest grid value
        lam_ship = min(train.LAMS, key=lambda l: abs(np.log10(l) - np.log10(lam_ship)))
    full = train.pairwise_model(d, np.arange(len(d['y'])), lam_ship, **VARIANTS[ship])
    weights = {'model': 'pairwise_logistic', 'variant': order[0], 'lambda': lam_ship,
               'identity_bonus': bonus_ship,
               'trained_on_rows': len(all_rows), 'trained_on_pairs': full['n_pairs'],
               'score': 'w . ((x - mean) / std); lower = predicted cheaper; compare inside one ball only',
               'feature_names': list(full['names']), 'mean': full['mean'].tolist(),
               'std': full['std'].tolist(), 'w': full['w'].tolist(),
               'cv': {m: results['rankers'][order[0]]['all'][m] for m in ('top1_regret', 'top1_solved', 'top3_solved', 'rank_of_best')},
               'atlas': str(data.ATLAS.name), 'budget': d['budget']}
    assert list(full['names']) == list(data.VECTOR_NAMES)
    with open(HERE / 'weights.json', 'w') as fh:
        json.dump(weights, fh, indent=1)
    top = sorted(zip(full['names'], full['w']), key=lambda t: -abs(t[1]))
    results['shipped'] = {'variant': order[0], 'weights_variant': ship, 'lambda': lam_ship,
                          'identity_bonus': bonus_ship, 'variant_order_by_primary': order,
                          'top_weights': [(n, float(w)) for n, w in top if w != 0][:25],
                          'all_weights': {n: float(w) for n, w in zip(full['names'], full['w'])}}
    # a sanity check that rank_images reproduces the atlas ordering on one row
    from research.autchoice_20260910.predictor.rank_images import score_images
    g0 = all_rows[0]
    view, idx = views[g0]
    imgs = [{'features': {k: d['X'][i][data.VECTOR_NAMES.index(k)] for k in data.FEATURE_KEYS},
             'seq': list(d['seq'][i]), 'depth': int(d['depth'][i]), 'is_identity': bool(d['is_identity'][i])}
            for i in idx]
    s_api = np.asarray(score_images(imgs, weights))
    s_fit = train.pairwise_scores(full, d['X'][idx]) - bonus_ship * d['is_identity'][idx]
    assert np.allclose(s_api, s_fit), 'rank_images.score_images disagrees with train.pairwise_scores'

    with open(HERE / 'results.json', 'w') as fh:
        json.dump(results, fh, indent=1)
    from research.autchoice_20260910.predictor.report import write_report
    write_report(results, HERE / 'PREDICTOR.md')
    print('shipped', ship, 'lambda', lam_ship)
    for name in list(BASELINES) + ['random', 'seq_prior', 'rule'] + list(VARIANTS) + [HEDGE, 'oracle']:
        s = results['oracle'] if name == 'oracle' else results['rankers'][name]
        a = s['all']
        print(f"{name:>20} regret={a['top1_regret']:.3f} top1={a['top1_solved_count']:>3} top3={a['top3_solved_count']:>3} "
              f"@5k={a['top1_solved_5k_count']:>3} rank={a['rank_of_best']:.2f} L9={s['by_level']['9']['top1_solved_count']}")


if __name__ == '__main__':
    main()
