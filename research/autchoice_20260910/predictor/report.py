"""Render ``PREDICTOR.md`` from ``results.json`` (every number comes from ``evaluate.py``).

    PYTHONPATH=. python3 -m research.autchoice_20260910.predictor.report   # re-render only
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.autchoice_20260910.predictor.data import FEATURE_KEYS  # noqa: E402
from research.autchoice_20260910.predictor.train import rule_candidates  # noqa: E402

BASE = ('identity', 'shortest', 'lowest_h', 'depth2_first', 'random')
LEARNED = ('seq_prior', 'rule', 'pairwise_gen_only', 'pairwise_state_only', 'pairwise', 'pairwise_rownorm', 'pairwise_rownorm_hedge')
LEVELS = ('1', '2', '3', '4', '5', '9')
FORMS = ('autmin', 'ms_raw', 'original')


def f2(v):
    return f'{v:.2f}' if isinstance(v, float) else str(v)


def f3(v):
    return f'{v:.3f}'


def table(header, rows):
    out = ['| ' + ' | '.join(header) + ' |', '|' + '|'.join('---' if i == 0 else '---:' for i in range(len(header))) + '|']
    out += ['| ' + ' | '.join(str(c) for c in r) + ' |' for r in rows]
    return '\n'.join(out)


def write_report(R, path):
    P = R['protocol']
    rk, orc = R['rankers'], R['oracle']
    n = P['rows']
    names = list(BASE) + list(LEARNED)

    def sec(name):
        return orc if name == 'oracle' else rk[name]

    def cnt(name, m, sub='all', key=None):
        s = sec(name)
        a = s['all'] if sub == 'all' else s[sub][key]
        return a.get(m + '_count', a.get(m))

    L = []
    L.append('# Can anything cheap predict which Aut(F2)-image is cheapest to search from?')
    L.append('')
    L.append(f"Data: `atlas.jsonl` -- {P['rows']} rows x 13 radius-2 images = {P['images']} S20_MK2 runs at budget "
             f"{P['budget']:,} ({P['solved_images']} solved, {P['censored_images']} censored at {P['budget']:,}).  "
             f"Built by `evaluate.py` (numbers) and `report.py` (this file); `results.json` holds every value below.")
    L.append('')
    L.append('## Protocol')
    L.append('')
    L.append(f"- **Group-disjoint CV.** {P['k_outer']} outer folds by *row* (a row's 13 images are never split; "
             f"`data.split` asserts it), stratified by level, seed {P['seed_outer']}; fold sizes {P['fold_sizes_rows']} rows.")
    L.append(f"- **Baselines** need no fitting and are scored on all {n} rows; `random` is the per-row mean over {P['n_random_seeds']} seeds.")
    L.append(f"- **Learned rankers** are fitted on the 4 training folds and scored on the held-out fold only.  The L2 strength of a "
             f"pairwise model is chosen inside the training folds by a {P['k_inner']}-fold inner group CV (seed {P['seed_inner']}) on "
             f"mean top1_regret over the grid {P['lambda_grid']}; the rule search and the seq prior are fitted on the training folds only.")
    L.append("- **Primary metric** (declared before looking): mean `top1_regret` = log10(cost of the pick) - log10(cost of the best image "
             "in the ball), censored = 20,000.  `top1_solved` / `top3_solved` / `top1_solved@5k`: the pick (best of the top 3; the pick at "
             "5,000 pops) solves.  `rank_of_best`: position the ranker gives the truly cheapest image (1 = perfect; ties at the minimum "
             "take the best-placed one, so an all-censored ball scores 1 for everyone).")
    L.append("- **Portfolio at equal compute**: the top-k images are run with 20,000/k pops each; a row is solved iff some top-k image "
             "has atlas cost <= 20,000 // k.")
    L.append("- **Selection caveat.** Picking the shipped variant among the four pairwise variants on the same outer folds is a small "
             "selection step (4 candidates, 124 rows); the per-fold table shows the spread.")
    L.append('')
    L.append('## Rankers')
    L.append('')
    L.append('| ranker | what it does |')
    L.append('|---|---|')
    L.append('| identity | the row as given first ("do nothing"), then the atlas BFS order |')
    L.append('| shortest | smallest total length, ties by the relator strings |')
    L.append('| lowest_h | smallest `h_s20mk2 = L + 20 S + 2 MK` of the image itself, ties by (depth, seq) |')
    L.append('| depth2_first | depth-2 images, then depth-1, then the identity; ties by lowest_h |')
    L.append('| random | a seeded permutation |')
    L.append('| seq_prior | order the 13 sequences by their mean within-row cost rank on the training rows (no state feature) |')
    L.append(f'| rule | the best of {len(rule_candidates()):,} one- and two-feature orderings on the training rows (single feature either sign, with/without depth-2 priority; two-feature within-row rank sums) |')
    L.append('| pairwise | logistic regression on standardised feature differences of every (cheaper, dearer) image pair inside a row, L2, Newton; score = w.x, lower first |')
    L.append('| pairwise_rownorm | the same with every row given total pair weight 1 |')
    L.append(f'| pairwise_state_only | pairwise on the {len(FEATURE_KEYS)} state features only (no depth / generator columns) |')
    L.append('| pairwise_gen_only | pairwise on depth, is_identity, same_gen and the generator one-hots only (no state feature) |')
    L.append('| pairwise_rownorm_hedge | pairwise_rownorm plus an *identity bonus*: keep the row as given unless an image scores lower by more than the bonus (bonus chosen on inner out-of-fold scores) |')
    L.append('')
    L.append(f'## Held-out metrics, all {n} rows')
    L.append('')
    hdr = ['ranker', 'top1_regret', f'top1_solved /{n}', f'top3_solved /{n}', f'top1_solved@5k /{n}', 'rank_of_best',
           'vs identity (top1 solved) W/L', 'vs lowest_h W/L', 'vs depth2_first W/L']
    rows = []
    for name in names + ['oracle']:
        s = sec(name)
        a = s['all']
        vs = lambda k: f"{s[k]['wins']}/{s[k]['losses']}" if k in s else '-'  # noqa: E731
        rows.append([name, f3(a['top1_regret']), f2(a['top1_solved_count']), f2(a['top3_solved_count']),
                     f2(a['top1_solved_5k_count']), f2(a['rank_of_best']),
                     vs('vs_identity_top1_solved'), vs('vs_lowest_h_top1_solved'), vs('vs_depth2_first_top1_solved')])
    L.append(table(hdr, rows))
    L.append('')
    L.append('`random` counts are means over seeds, hence fractional.')
    L.append('')
    L.append('### Top-1 solves at 20,000 by level (rows solved / rows)')
    L.append('')
    nlev = {l: orc['by_level'][l]['n'] for l in LEVELS}
    hdr = ['ranker'] + [f'L{l} /{nlev[l]}' for l in LEVELS] + ['all']
    rows = [[name] + [f2(cnt(name, 'top1_solved', 'by_level', l)) for l in LEVELS] + [f2(cnt(name, 'top1_solved'))]
            for name in names + ['oracle']]
    L.append(table(hdr, rows))
    L.append('')
    L.append('### Top-1 regret by level (mean log10 cost above the best image)')
    L.append('')
    rows = [[name] + [f3(sec(name)['by_level'][l]['top1_regret']) for l in LEVELS] + [f3(sec(name)['all']['top1_regret'])]
            for name in names]
    L.append(table(['ranker'] + [f'L{l}' for l in LEVELS] + ['all'], rows))
    L.append('')
    L.append('### Top-1 solves at 5,000 by level')
    L.append('')
    rows = [[name] + [f2(cnt(name, 'top1_solved_5k', 'by_level', l)) for l in LEVELS] + [f2(cnt(name, 'top1_solved_5k'))]
            for name in names + ['oracle']]
    L.append(table(['ranker'] + [f'L{l} /{nlev[l]}' for l in LEVELS] + ['all'], rows))
    L.append('')
    L.append('### By form: top-1 solves at 20,000 / regret')
    L.append('')
    nf = {f: orc['by_form'][f]['n'] for f in FORMS}
    rows = [[name] + [f"{f2(cnt(name, 'top1_solved', 'by_form', f))} / {f3(sec(name)['by_form'][f]['top1_regret'])}" for f in FORMS]
            for name in names + ['oracle']]
    L.append(table(['ranker'] + [f'{f} (n={nf[f]})' for f in FORMS], rows))
    L.append('')
    L.append('### Portfolio at equal compute (rows solved with the top-k images at 20,000/k pops each)')
    L.append('')
    ks = list(orc['portfolio'].keys())
    rows = [[name] + [f2(sec(name)['portfolio'][k]['solved']) for k in ks] for name in names + ['oracle']]
    L.append(table(['ranker'] + [f'k={k} ({20000 // int(k):,} pops each)' for k in ks], rows))
    L.append('')
    L.append('Level 9 only (28 representatives plain greedy cannot solve at 10M):')
    L.append('')
    rows = [[name] + [f2(sec(name)['portfolio'][k]['by_level']['9']) for k in ks] for name in names + ['oracle']]
    L.append(table(['ranker'] + [f'k={k}' for k in ks], rows))
    L.append('')
    L.append('### Hedged portfolio: the row as given plus the top k-1 predicted images, 20,000/k pops each')
    L.append('')
    L.append('(k=1 is the identity alone; k=13 is the whole ball.  For the oracle the k-1 extra images are the truly cheapest ones.)')
    L.append('')
    rows = [[name] + [f2(sec(name)['hedged'][k]['solved']) for k in ks] for name in names + ['oracle']]
    L.append(table(['ranker'] + [f'k={k} ({20000 // int(k):,} pops each)' for k in ks], rows))
    L.append('')
    L.append('Level 9 only:')
    L.append('')
    rows = [[name] + [f2(sec(name)['hedged'][k]['by_level']['9']) for k in ks] for name in names + ['oracle']]
    L.append(table(['ranker'] + [f'k={k}' for k in ks], rows))
    L.append('')
    L.append('### Share of the identity-to-oracle gap closed (top-1 pick)')
    L.append('')
    rows = []
    for name in names:
        g = rk[name]['gap_closed']
        rows.append([name, f3(g['all']['top1_solved']), f3(g['all']['top1_solved_5k']), f3(g['level_9']['top1_solved']),
                     f3(g['level_9']['top1_solved_5k'])])
    L.append(table(['ranker', 'all @20k', 'all @5k', 'level 9 @20k', 'level 9 @5k'], rows))
    L.append('')
    idc, oc = cnt('identity', 'top1_solved'), cnt('oracle', 'top1_solved')
    L.append(f"(gap = oracle {oc} - identity {idc} = {oc - idc} rows at 20k; at 5k oracle {cnt('oracle', 'top1_solved_5k')} - "
             f"identity {cnt('identity', 'top1_solved_5k')}; level 9: {cnt('oracle', 'top1_solved', 'by_level', '9')} - "
             f"{cnt('identity', 'top1_solved', 'by_level', '9')}.)")
    L.append('')
    # ---- model details
    L.append('## The pairwise model')
    L.append('')
    S = R['shipped']
    L.append(f"Shipped variant: **{S['variant']}** (best outer-CV primary metric; order {S['variant_order_by_primary']}), "
             f"weights of `{S['weights_variant']}` refitted on all {n} rows with lambda = {S['lambda']} and identity bonus "
             f"{S['identity_bonus']} (medians of the per-fold choices) -> `weights.json`.")
    L.append('')
    L.append('### Per outer fold')
    L.append('')
    rows = []
    for name in ('pairwise', 'pairwise_rownorm', 'pairwise_rownorm_hedge', 'pairwise_state_only', 'pairwise_gen_only'):
        for pf in R['model'][name]['per_fold']:
            rows.append([name, pf['fold'], pf['test_rows'], pf['n_pairs'], pf['lambda'], pf.get('identity_bonus', '-'),
                         f3(pf['top1_regret']), f3(pf['top1_solved']), f3(pf['top3_solved']), f2(pf['rank_of_best'])])
    L.append(table(['variant', 'fold', 'test rows', 'train pairs', 'chosen lambda', 'identity bonus', 'top1_regret', 'top1_solved', 'top3_solved', 'rank_of_best'], rows))
    L.append('')
    L.append('Inner out-of-fold regret by identity bonus (variant `pairwise_rownorm`, training rows of each fold; the chosen bonus is the minimum):')
    L.append('')
    bs = list(R['model']['pairwise_rownorm_hedge']['per_fold'][0]['inner_regret_by_bonus'].keys())
    rows = [[pf['fold']] + [f3(pf['inner_regret_by_bonus'][b]) for b in bs] for pf in R['model']['pairwise_rownorm_hedge']['per_fold']]
    L.append(table(['fold'] + [f'bonus {b}' for b in bs], rows))
    L.append('')
    L.append('### Fixed-lambda sensitivity (variant `pairwise`, held-out folds; NOT the selection procedure)')
    L.append('')
    rows = [[lam, f3(a['top1_regret']), a['top1_solved_count'], a['top3_solved_count'], a['top1_solved_5k_count'], f2(a['rank_of_best'])]
            for lam, a in R['fixed_lambda_sweep'].items()]
    L.append(table(['lambda', 'top1_regret', 'top1_solved', 'top3_solved', 'top1_solved@5k', 'rank_of_best'], rows))
    L.append('')
    L.append('### Weights (standardised features; negative = the image looks cheaper when the feature is larger)')
    L.append('')
    rows = [[k + 1, nme, f'{w:+.3f}'] for k, (nme, w) in enumerate(S['top_weights'])]
    L.append(table(['#', 'feature', 'w'], rows))
    L.append('')
    L.append('Columns absent from the table have weight exactly 0 (constant in the atlas: the AUTOS indices other than 8, 9, 14, 15 never occur, `Bmin` and `once_gen` are constant).  '
             '`delta_len` and `total_len` are collinear inside a row (the row offset cancels in a pairwise difference) so the L2 penalty splits their weight; likewise `is_identity` and `depth`.')
    L.append('')
    L.append('## Rule search and seq prior (per fold)')
    L.append('')
    rows = [[pf['fold'], pf['rule'], f3(pf['train_top1_regret']), f3(pf['test_top1_regret']), f3(pf['test_top1_solved'])]
            for pf in R['rules']['per_fold']]
    L.append(table(['fold', 'rule selected on the training rows', 'train regret', 'held-out regret', 'held-out top1_solved'], rows))
    L.append('')
    L.append('Seq prior (mean within-row cost rank of each sequence, training rows of each fold; lower = cheaper):')
    L.append('')
    seqs = list(R['seq_prior']['per_fold'][0]['prior'].keys())
    allseq = sorted({s for pf in R['seq_prior']['per_fold'] for s in pf['prior']}, key=lambda s: R['seq_prior']['per_fold'][0]['prior'].get(s, 99))
    rows = [[pf['fold']] + [f2(pf['prior'].get(s, float('nan'))) for s in allseq] for pf in R['seq_prior']['per_fold']]
    L.append(table(['fold'] + allseq, rows))
    L.append('')
    # ---- generators
    G = R['generators']
    L.append('## Which generators produce the cheapest image?')
    L.append('')
    L.append(f"Over the {G['rows_with_a_cheapest_image']} rows with at least one solved image (ties at the minimum go to the BFS-first image, as in "
             f"`ATLAS.md`; the minimum is unique on {G['rows_with_unique_minimum']} of them).  Under a uniform choice each of the 13 sequences "
             f"would win {G['expected_per_seq_if_uniform']:.1f} rows.")
    L.append('')
    rows = [[s, c] + [G['cheapest_seq_by_level'].get(l, {}).get(s, 0) for l in LEVELS] for s, c in G['cheapest_seq'].items()]
    L.append(table(['seq (AUTOS indices, applied left to right)', 'rows'] + [f'L{l}' for l in LEVELS], rows))
    L.append('')
    L.append(f"Repeated generator at depth 2: {G['depth2_same_generator']}; two different generators: {G['depth2_different_generators']}; "
             f"depth 1: {G['depth1']}; identity: {G['identity']}.")
    L.append('')
    rows = [[i, G['autos'][i], G['first_generator'].get(i, 0), G['second_generator'].get(i, 0)] for i in sorted(G['autos'], key=int)]
    L.append(table(['AUTOS index', 'automorphism', 'first in the cheapest seq', 'second in the cheapest seq'], rows))
    L.append('')
    L.append('The labels are relative to each row\'s canonical naming (a relabelling swaps 8 with 9 and 14 with 15 as cyclic words), so the '
             'split between 8/9 and between 14/15 is not meaningful; the split between the y-family (8, 9) and the x-family (14, 15) is.')
    L.append('')
    # ---- verdict
    L.append('## Verdict')
    L.append('')
    best_simple = min(('identity', 'lowest_h', 'depth2_first', 'shortest'), key=lambda nme: rk[nme]['all']['top1_regret'])
    V = S['variant']
    pw = rk[V]['all']
    beats = {nme: (pw['top1_regret'] < rk[nme]['all']['top1_regret'] and pw['top1_solved_count'] > rk[nme]['all']['top1_solved_count'])
             for nme in ('identity', 'lowest_h', 'depth2_first', 'rule', 'seq_prior')}
    L.append(f"- The best hand-written rule by the primary metric is **{best_simple}** (regret {f3(rk[best_simple]['all']['top1_regret'])}, "
             f"{cnt(best_simple, 'top1_solved')}/{n} top-1 solves).  `lowest_h` ({f3(rk['lowest_h']['all']['top1_regret'])}, {cnt('lowest_h', 'top1_solved')}) and "
             f"`depth2_first` ({f3(rk['depth2_first']['all']['top1_regret'])}, {cnt('depth2_first', 'top1_solved')}) both lose to the identity on the pick, "
             f"though they place the best image higher (rank_of_best {f2(rk['lowest_h']['all']['rank_of_best'])} / {f2(rk['depth2_first']['all']['rank_of_best'])} vs {f2(rk['identity']['all']['rank_of_best'])}).")
    base = rk['pairwise_rownorm']['all']
    L.append(f"- The pairwise model without the hedge (`pairwise_rownorm`): regret {f3(base['top1_regret'])}, top-1 solves {base['top1_solved_count']}/{n}, "
             f"top-1@5k {base['top1_solved_5k_count']}/{n}, W/L vs identity {rk['pairwise_rownorm']['vs_identity_top1_solved']['wins']}/{rk['pairwise_rownorm']['vs_identity_top1_solved']['losses']}.")
    L.append(f"- The shipped pairwise model (`{S['variant']}`) on held-out rows: regret {f3(pw['top1_regret'])}, top-1 solves {pw['top1_solved_count']}/{n}, "
             f"top-3 solves {pw['top3_solved_count']}/{n}, top-1@5k {pw['top1_solved_5k_count']}/{n}, rank_of_best {f2(pw['rank_of_best'])}.  "
             f"Beats the identity: {'yes' if beats['identity'] else 'no'} (W/L on top-1 solves {rk[S['variant']]['vs_identity_top1_solved']['wins']}/{rk[S['variant']]['vs_identity_top1_solved']['losses']}); "
             f"beats lowest_h: {'yes' if beats['lowest_h'] else 'no'}; beats depth2_first: {'yes' if beats['depth2_first'] else 'no'}; "
             f"beats the in-fold rule search: {'yes' if beats['rule'] else 'no'}; beats the seq prior: {'yes' if beats['seq_prior'] else 'no'}.")
    gc = rk[S['variant']]['gap_closed']
    hd = rk['pairwise_rownorm_hedge']['all']
    L.append(f"- The identity-bonus hedge (deviate from the row as given only on a clear margin) does not help: held-out regret "
             f"{f3(hd['top1_regret'])} vs {f3(base['top1_regret'])} without it, {hd['top1_solved_count']} vs {base['top1_solved_count']} top-1 solves; "
             f"the inner CV picks a bonus of {[pf['identity_bonus'] for pf in R['model']['pairwise_rownorm_hedge']['per_fold']]} per fold, so the shipped bonus is {S['identity_bonus']}.")
    bf = lambda nme, f: cnt(nme, 'top1_solved', 'by_form', f)  # noqa: E731
    L.append(f"- Where it wins and loses (top-1 solves at 20k, model vs identity vs oracle): autmin {bf(V, 'autmin')} vs {bf('identity', 'autmin')} vs {bf('oracle', 'autmin')}; "
             f"ms_raw {bf(V, 'ms_raw')} vs {bf('identity', 'ms_raw')} vs {bf('oracle', 'ms_raw')}; original {bf(V, 'original')} vs {bf('identity', 'original')} vs {bf('oracle', 'original')}.  "
             f"The gain is on the Aut-minimal representatives; on the dataset originals, which the identity already solves {bf('identity', 'original')}/{nf['original']}, "
             f"the model gives back {bf('identity', 'original') - bf(V, 'original')} rows at 20k "
             f"(at 5k it is {cnt(V, 'top1_solved_5k', 'by_form', 'original')} vs {cnt('identity', 'top1_solved_5k', 'by_form', 'original')}).")
    L.append(f"- Gap closed by the single pick: {gc['all']['top1_solved']:.0%} of the identity-to-oracle gap at 20k over all rows "
             f"({gc['all']['top1_solved_5k']:.0%} at 5k); on level 9, {gc['level_9']['top1_solved']:.0%} at 20k "
             f"({cnt(S['variant'], 'top1_solved', 'by_level', '9')} vs identity {cnt('identity', 'top1_solved', 'by_level', '9')} vs oracle {cnt('oracle', 'top1_solved', 'by_level', '9')}).")
    so, go = rk['pairwise_state_only']['all'], rk['pairwise_gen_only']['all']
    L.append(f"- Where the signal is: state features alone give regret {f3(so['top1_regret'])} ({so['top1_solved_count']} solves), the "
             f"generator/depth columns alone {f3(go['top1_regret'])} ({go['top1_solved_count']}), the seq prior {f3(rk['seq_prior']['all']['top1_regret'])} "
             f"({cnt('seq_prior', 'top1_solved')}), both together {f3(pw['top1_regret'])} ({pw['top1_solved_count']}).")
    # portfolio recommendation
    ks_int = [int(k) for k in ks]
    port = {('top', k): rk[V]['portfolio'][str(k)]['solved'] for k in ks_int}
    port.update({('hedged', k): rk[V]['hedged'][str(k)]['solved'] for k in ks_int})
    port9 = {('top', k): rk[V]['portfolio'][str(k)]['by_level']['9'] for k in ks_int}
    port9.update({('hedged', k): rk[V]['hedged'][str(k)]['by_level']['9'] for k in ks_int})
    kbest = max(port, key=lambda t: (port[t], -t[1]))
    kbest9 = max(port9, key=lambda t: (port9[t], -t[1]))
    id_port = rk['identity']['portfolio']['1']['solved']
    id_port9 = rk['identity']['portfolio']['1']['by_level']['9']
    desc = lambda t: f"{'top-' + str(t[1]) if t[0] == 'top' else 'identity + top-' + str(t[1] - 1)} at {20000 // t[1]:,} pops each"  # noqa: E731
    top_all = ', '.join('k=%d: %d' % (k, port[('top', k)]) for k in ks_int)
    hed_all = ', '.join('k=%d: %d' % (k, port[('hedged', k)]) for k in ks_int)
    top_9 = ', '.join('k=%d: %d' % (k, port9[('top', k)]) for k in ks_int)
    hed_9 = ', '.join('k=%d: %d' % (k, port9[('hedged', k)]) for k in ks_int)
    L.append(f"- Equal compute with the shipped ranking, all rows: pure top-k solves {top_all}; "
             f"hedged (identity + top k-1) {hed_all} (identity alone {id_port}; oracle single pick "
             f"{orc['portfolio']['1']['solved']}).  Level 9: pure {top_9}; hedged {hed_9} (identity alone {id_port9}; "
             f"oracle {orc['portfolio']['1']['by_level']['9']}).  "
             f"Best over all rows: **{desc(kbest)}** ({port[kbest]}); on level 9: **{desc(kbest9)}** ({port9[kbest9]}).")
    L.append(f"- depth2_first, the best hand rule on level 9 alone ({cnt('depth2_first', 'top1_solved', 'by_level', '9')} top-1 solves, "
             f"hedged k=2 {rk['depth2_first']['hedged']['2']['by_level']['9']}), is not usable blind: it costs "
             f"{cnt('identity', 'top1_solved') - cnt('depth2_first', 'top1_solved')} rows over the whole panel.")
    L.append('')
    L.append('**For B3.** ' + (
        f"Use `rank_images.rank` (learned weights).  Single pick: the top-1 image beats running the row as given "
        f"({pw['top1_solved_count']} vs {cnt('identity', 'top1_solved')} at 20k, {pw['top1_solved_5k_count']} vs {cnt('identity', 'top1_solved_5k')} at 5k), "
        f"and it is the best recipe at equal compute over the whole panel (**{desc(kbest)}**, {port[kbest]} rows).  "
        f"On hard rows the best is **{desc(kbest9)}** ({port9[kbest9]} of {nlev['9']} level-9 rows).  "
        f"Insurance: identity + top-1 at 10,000 each solves {port[('hedged', 2)]} rows overall and {port9[('hedged', 2)]} on level 9, never fewer than the identity at 10,000 "
        f"({rk['identity']['portfolio']['2']['solved']}), so use it when a run must not be worse than the row as given at the reduced budget.  "
        f"Do not use the pick on inputs that are dataset originals if the budget is generous: there the row as given is already the best single start.  "
        if beats['identity'] else
        f"The learned model does not beat the identity on the pick; keep the row as given for a single run and use `rank_images.rank` only "
        f"to order the alternatives for a portfolio (best: {desc(kbest)}).  ")
        + "`rank` is deterministic, numpy-only, 13 images per call at radius 2, and falls back to `lowest_h` if `weights.json` is missing.")
    L.append('')
    L.append('## Files')
    L.append('')
    L.append('| file | role |')
    L.append('|---|---|')
    L.append('| `data.py` | atlas -> arrays, feature vector (`image_vector`), stratified group folds, standardisation |')
    L.append('| `baselines.py` | identity / shortest / lowest_h / depth2_first / random / bfs rankers |')
    L.append('| `metrics.py` | per-row metrics and aggregation |')
    L.append('| `train.py` | pairwise logistic ranker (Newton, L2), seq prior, rule search |')
    L.append('| `evaluate.py` | the CV driver; writes `results.json`, `weights.json`, this report |')
    L.append('| `report.py` | renders this file from `results.json` |')
    L.append('| `rank_images.py` | `rank(pair, radius=2, cap=48) -> [(score, image), ...]`, best first; CLI prints a ranking |')
    L.append('| `weights.json` | feature names, means, stds, weights, lambda, CV summary |')
    L.append('| `tests/test_predictor.py` | group-disjoint split, `rank` on a ladder_20 row, weights round-trip |')
    L.append('')
    Path(path).write_text('\n'.join(L) + '\n')


if __name__ == '__main__':
    with open(HERE / 'results.json') as fh:
        write_report(json.load(fh), HERE / 'PREDICTOR.md')
    print('wrote', HERE / 'PREDICTOR.md')
