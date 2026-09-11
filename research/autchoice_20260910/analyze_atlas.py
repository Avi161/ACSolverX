"""Summarise atlas.jsonl: which Aut-image of a presentation is cheapest to search from.

Reads every record of ``atlas.jsonl`` (one per (row, image)); a run that did not solve at
the atlas budget ``B`` is *censored* and counted as costing ``B``.  Writes ``ATLAS.md``
(plain markdown tables, every number computed here) and ``atlas_summary.json``.

Per row (S20_MK2 arm; the plain-greedy arm likewise on the 73 pair rows):
    min / median / max cost over the radius-2 ball, the identity's cost and its rank in
    the ball (1 + number of images strictly cheaper), the shortest image's cost and rank,
    ``cheapest_is_identity`` (no image strictly cheaper than the identity) and
    ``cheapest_is_shortest`` (no image strictly cheaper than the shortest image; ties in
    length go to the lowest image index, so the identity when it is shortest).
Aggregates per level and per form; solve counts at 5k / 10k / 20k read off by rescoring
(``solved and nodes <= b``) for the identity, the shortest image and the best image of
the ball; Spearman rank correlation (numpy, average ranks for ties) between image total
length and log10 cost, per row and pooled; per depth-1 Whitehead generator the median
log10 cost ratio image/identity and the fraction of rows it strictly improves; and for
the 45 original/representative pairs the original's cost against the best image of the
representative's ball, plus the smallest radius (<= 4) at which the original's relabel
class appears in the representative's ball.

    PYTHONPATH=. python3 -m research.autchoice_20260910.analyze_atlas
"""
import csv
import json
import math
import sys
from collections import OrderedDict, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.equivalence_classes.lib.autcanon import AUTOS  # noqa: E402
from experiments.equivalence_classes.lib.words import relabel_key  # noqa: E402
from research.autchoice_20260910.orbit import ball  # noqa: E402

HERE = Path(__file__).resolve().parent
RESCORE = (5000, 10000, 20000)
ARMS = ('s20', 'greedy')


# ----------------------------------------------------------------------------- helpers
def spearman(x, y):
    """Spearman rank correlation with average ranks for ties; None if either side is constant."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3:
        return None

    def ranks(v):
        order = np.argsort(v, kind='mergesort')
        r = np.empty(len(v))
        sv = v[order]
        i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and sv[j + 1] == sv[i]:
                j += 1
            r[order[i:j + 1]] = (i + j) / 2.0 + 1
            i = j + 1
        return r
    rx, ry = ranks(x), ranks(y)
    if rx.std() == 0 or ry.std() == 0:
        return None
    return float(np.corrcoef(rx, ry)[0, 1])


def median(v):
    v = sorted(v)
    if not v:
        return None
    n = len(v)
    return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2.0


def fmt(v, nd=2):
    if v is None:
        return '-'
    if isinstance(v, float):
        return f'{v:.{nd}f}'
    return f'{v:,}' if isinstance(v, int) and abs(v) >= 10000 else str(v)


def cost_of(run, B):
    return run['nodes'] if run and run['solved'] else B


def solved_at(run, b):
    return bool(run and run['solved'] and run['nodes'] <= b)


# ----------------------------------------------------------------------------- per row
def analyse_row(name, recs, arm, B):
    recs = sorted(recs, key=lambda r: r['image_index'])
    if any(r[arm] is None for r in recs):
        return None
    costs = [cost_of(r[arm], B) for r in recs]
    lens = [r['features']['total_len'] for r in recs]
    ident = recs[0]
    assert ident['is_identity']
    c_id = costs[0]
    i_short = min(range(len(recs)), key=lambda i: (lens[i], i))
    c_short = costs[i_short]
    c_min = min(costs)
    i_min = min(range(len(recs)), key=lambda i: (costs[i], lens[i], i))
    rank_id = 1 + sum(1 for c in costs if c < c_id)
    rank_short = 1 + sum(1 for c in costs if c < c_short)
    out = OrderedDict(
        row=name, level=int(ident['level']), form=ident['form'], pair_id=ident['pair_id'],
        n_images=len(recs), start_len=lens[0],
        min=c_min, median=median(costs), max=max(costs),
        identity=c_id, identity_rank=rank_id, identity_solved=bool(ident[arm]['solved']),
        shortest_index=i_short, shortest_len=lens[i_short], shortest=c_short, shortest_rank=rank_short,
        cheapest_index=i_min, cheapest_len=lens[i_min], cheapest_depth=recs[i_min]['depth'],
        cheapest_seq=recs[i_min]['seq'], cheapest_phi=recs[i_min]['phi'],
        cheapest_pair=[recs[i_min]['r1'], recs[i_min]['r2']],
        cheapest_is_identity=(c_id == c_min), cheapest_is_shortest=(c_short == c_min),
        n_strictly_cheaper_than_identity=sum(1 for c in costs if c < c_id),
        n_solved=sum(1 for r in recs if r[arm]['solved']),
        n_verified=sum(1 for r in recs if r[arm]['verified']),
        n_rejected=sum(1 for r in recs if r[arm].get('rejected')),
        log_gain=math.log10(c_id / c_min) if c_min > 0 else None,
        spearman_len_logcost=spearman(lens, [math.log10(c) for c in costs]),
        solved_at={str(b): {'identity': solved_at(ident[arm], b),
                            'shortest': solved_at(recs[i_short][arm], b),
                            'best': any(solved_at(r[arm], b) for r in recs)} for b in RESCORE},
        depth1={},
    )
    for r in recs:
        if r['depth'] == 1:
            c = cost_of(r[arm], B)
            out['depth1'][str(r['seq'][0])] = {'cost': c, 'log_ratio': math.log10(c / c_id),
                                              'improves': c < c_id, 'len': r['features']['total_len']}
    return out


# ----------------------------------------------------------------------------- aggregates
def aggregate(rows_stats, key):
    groups = defaultdict(list)
    for s in rows_stats:
        groups[s[key]].append(s)
    table = OrderedDict()
    for g in sorted(groups, key=lambda v: (isinstance(v, str), v)):
        ss = groups[g]
        n = len(ss)
        table[str(g)] = OrderedDict(
            rows=n,
            identity_solved=sum(1 for s in ss if s['identity_solved']),
            any_image_solved=sum(1 for s in ss if s['n_solved'] > 0),
            cheapest_is_identity=sum(1 for s in ss if s['cheapest_is_identity']),
            cheapest_is_shortest=sum(1 for s in ss if s['cheapest_is_shortest']),
            some_image_strictly_cheaper=sum(1 for s in ss if s['n_strictly_cheaper_than_identity'] > 0),
            median_identity=median([s['identity'] for s in ss]),
            median_min=median([s['min'] for s in ss]),
            median_log_gain=median([s['log_gain'] for s in ss if s['log_gain'] is not None]),
            median_identity_rank=median([s['identity_rank'] for s in ss]),
            median_spearman=median([s['spearman_len_logcost'] for s in ss if s['spearman_len_logcost'] is not None]),
            solved_at={str(b): {k: sum(1 for s in ss if s['solved_at'][str(b)][k]) for k in ('identity', 'shortest', 'best')}
                       for b in RESCORE},
        )
    return table


def depth1_table(rows_stats):
    gens = defaultdict(list)
    for s in rows_stats:
        for g, d in s['depth1'].items():
            gens[g].append(d)
    out = OrderedDict()
    for g in sorted(gens, key=int):
        ds = gens[g]
        a = AUTOS[int(g)]
        out[g] = OrderedDict(auto=f"x->{a['x']}, y->{a['y']}", rows=len(ds),
                             median_log_ratio=median([d['log_ratio'] for d in ds]),
                             frac_improves=sum(1 for d in ds if d['improves']) / len(ds),
                             frac_worsens=sum(1 for d in ds if d['log_ratio'] > 0) / len(ds))
    return out


def pair_table(rows_stats, recs_by_row, panel, B, arm):
    stats = {s['row']: s for s in rows_stats}
    out = []
    for name, s in sorted(stats.items()):
        if s['form'] != 'original' or s['pair_id'] not in stats:
            continue
        rep = stats[s['pair_id']]
        orig_key = list(relabel_key((panel[name]['r1'], panel[name]['r2'])))
        rep_pair = (panel[rep['row']]['r1'], panel[rep['row']]['r2'])
        rep_keys2 = {tuple(r['rkey']) for r in recs_by_row[rep['row']]}
        in_r2 = tuple(orig_key) in rep_keys2
        radius = None
        for r in range(1, 5):
            if any(tuple(n['rkey']) == tuple(orig_key) for n in ball(rep_pair, r, cap=64)):
                radius = r
                break
        out.append(OrderedDict(
            original=name, rep=rep['row'], orig_level=s['level'], orig_len=s['start_len'], rep_len=rep['start_len'],
            orig_cost=s['identity'], orig_best=s['min'], rep_cost=rep['identity'], rep_best=rep['min'],
            rep_best_len=rep['cheapest_len'], rep_best_depth=rep['cheapest_depth'],
            orig_in_rep_ball2=in_r2, orig_in_rep_ball_radius=radius,
            orig_beats_rep_ball=s['identity'] < rep['min'],
        ))
    return out


# ----------------------------------------------------------------------------- markdown
def md_table(headers, rows):
    lines = ['| ' + ' | '.join(headers) + ' |', '|' + '|'.join('---:' if i else '---' for i in range(len(headers))) + '|']
    for r in rows:
        lines.append('| ' + ' | '.join(str(v) for v in r) + ' |')
    return '\n'.join(lines)


def write_md(summary, out_path):
    B = summary['budget']
    L = []
    L.append('# The orbit-cost atlas\n')
    L.append(f"Every radius-2 Aut(F2)-image (relabel-deduplicated, cap 48) of {summary['rows']} panel rows, "
             f"searched with `S20_MK2` at budget {B:,} ({summary['records']} images; the {summary['pair_rows']} "
             f"pair rows also with plain greedy).  A run that did not solve is *censored* at {B:,}.  "
             f"Every solve replayed independently: {summary['verified_s20']}/{summary['solved_s20']} S20 solves and "
             f"{summary['verified_greedy']}/{summary['solved_greedy']} greedy solves verified, "
             f"{summary['rejected']} rejected.  Built by `analyze_atlas.py` from `atlas.jsonl`.\n")
    L.append('## Headline findings\n')
    for b in summary['headlines']:
        L.append(f'- {b}')
    L.append('')
    for arm in ARMS:
        agg = summary[arm]
        if not agg['rows']:
            continue
        L.append(f"## {'S20_MK2' if arm == 's20' else 'Plain greedy'} arm\n")
        L.append(f"### Per level ({len(agg['rows'])} rows)\n")
        hdr = ['level', 'rows', 'identity solved', 'any image solved', 'cheapest = identity', 'cheapest = shortest',
               'image strictly cheaper', 'median identity', 'median best', 'median log10 gain', 'median identity rank',
               'median Spearman(len, log cost)']
        L.append(md_table(hdr, [[g, a['rows'], a['identity_solved'], a['any_image_solved'], a['cheapest_is_identity'],
                                 a['cheapest_is_shortest'], a['some_image_strictly_cheaper'], fmt(a['median_identity']),
                                 fmt(a['median_min']), fmt(a['median_log_gain']), fmt(a['median_identity_rank']),
                                 fmt(a['median_spearman'])] for g, a in agg['per_level'].items()]))
        L.append('')
        L.append('### Per form\n')
        L.append(md_table(['form'] + hdr[1:], [[g, a['rows'], a['identity_solved'], a['any_image_solved'], a['cheapest_is_identity'],
                                 a['cheapest_is_shortest'], a['some_image_strictly_cheaper'], fmt(a['median_identity']),
                                 fmt(a['median_min']), fmt(a['median_log_gain']), fmt(a['median_identity_rank']),
                                 fmt(a['median_spearman'])] for g, a in agg['per_form'].items()]))
        L.append('')
        L.append('### Solves at smaller budgets (rescored), identity / shortest image / best of ball\n')
        rows = []
        for g, a in agg['per_level'].items():
            rows.append([f'level {g}', a['rows']] + [f"{a['solved_at'][str(b)]['identity']} / {a['solved_at'][str(b)]['shortest']} / {a['solved_at'][str(b)]['best']}" for b in RESCORE])
        for g, a in agg['per_form'].items():
            rows.append([f'form {g}', a['rows']] + [f"{a['solved_at'][str(b)]['identity']} / {a['solved_at'][str(b)]['shortest']} / {a['solved_at'][str(b)]['best']}" for b in RESCORE])
        a = agg['all']
        rows.append(['all', a['rows']] + [f"{a['solved_at'][str(b)]['identity']} / {a['solved_at'][str(b)]['shortest']} / {a['solved_at'][str(b)]['best']}" for b in RESCORE])
        L.append(md_table(['slice', 'rows'] + [f'@{b:,}' for b in RESCORE], rows))
        L.append('')
        L.append('### Length vs cost\n')
        sp = agg['spearman']
        L.append(f"Spearman(image total length, log10 cost): pooled over all {sp['pooled_n']} images "
                 f"{fmt(sp['pooled'])}; pooled on length relative to the row's identity {fmt(sp['pooled_relative'])}; "
                 f"per row median {fmt(sp['per_row_median'])} over {sp['per_row_n']} rows with a defined value "
                 f"({sp['per_row_positive']} positive, {sp['per_row_negative']} negative).\n")
        L.append('### Depth-1 Whitehead generators (image cost / identity cost)\n')
        L.append('The generator label is the first AUTOS index that reaches the relabel class from the row\'s own '
                 'representative, so `y->yx` vs `y->Xy` is relative to that representative\'s naming.\n')
        L.append(md_table(['AUTOS index', 'automorphism', 'rows', 'median log10 ratio', 'fraction strictly cheaper', 'fraction dearer'],
                          [[g, d['auto'], d['rows'], fmt(d['median_log_ratio'], 3), fmt(d['frac_improves']), fmt(d['frac_worsens'])]
                           for g, d in agg['depth1'].items()]))
        L.append('')
        if agg['pairs']:
            L.append('### The original / representative pairs\n')
            L.append('`orig cost` is the original searched as-is (identity of its own ball), `rep best` the cheapest image '
                     'in the representative\'s radius-2 ball; `orig in rep ball` is the smallest radius (up to 4) at which '
                     'the original\'s relabel class appears in the representative\'s ball.\n')
            p = agg['pairs']
            L.append(md_table(['original', 'rep', 'orig len', 'rep len', 'orig cost', 'orig best', 'rep cost', 'rep best',
                               'rep best len', 'rep best depth', 'orig in rep ball'],
                              [[q['original'], q['rep'], q['orig_len'], q['rep_len'], fmt(q['orig_cost']), fmt(q['orig_best']),
                                fmt(q['rep_cost']), fmt(q['rep_best']), q['rep_best_len'], q['rep_best_depth'],
                                q['orig_in_rep_ball_radius'] or '>4'] for q in p]))
            L.append('')
            L.append(f"{sum(1 for q in p if q['orig_beats_rep_ball'])}/{len(p)} originals are strictly cheaper than the best "
                     f"image of their representative's ball; {sum(1 for q in p if q['orig_in_rep_ball2'])}/{len(p)} originals "
                     f"lie in the representative's radius-2 ball, {sum(1 for q in p if q['orig_in_rep_ball_radius'] is not None)}/{len(p)} "
                     f"within radius 4.\n")
        L.append('### Per row\n')
        L.append(md_table(['row', 'level', 'form', 'len', 'images', 'min', 'median', 'max', 'identity', 'rank', 'shortest', 'rank',
                           'cheapest len', 'cheapest depth', 'cheapest seq', 'Spearman'],
                          [[s['row'], s['level'], s['form'], s['start_len'], s['n_images'], fmt(s['min']), fmt(s['median']),
                            fmt(s['max']), fmt(s['identity']), s['identity_rank'], fmt(s['shortest']), s['shortest_rank'],
                            s['cheapest_len'], s['cheapest_depth'], ''.join(str(i) + ' ' for i in s['cheapest_seq']).strip() or 'id',
                            fmt(s['spearman_len_logcost'])] for s in agg['rows']]))
        L.append('')
    Path(out_path).write_text('\n'.join(L))


def headlines(summary):
    B = summary['budget']
    s = summary['s20']
    a = s['all']
    n = a['rows']
    H = []
    empty = {'rows': 0, 'identity_solved': 0, 'any_image_solved': 0}
    lv9 = s['per_level'].get('9', empty)
    H.append(f"Choosing the best of the {summary['median_ball']} radius-2 images (an oracle) raises S20_MK2 solves at "
             f"{B:,} pops from {a['identity_solved']}/{n} (the row as given) to {a['any_image_solved']}/{n}; at 5,000 pops from "
             f"{a['solved_at']['5000']['identity']}/{n} to {a['solved_at']['5000']['best']}/{n}.  On the {lv9['rows']} "
             f"level-9 representatives (plain greedy fails at 10M): identity {lv9['identity_solved']}, best image "
             f"{lv9['any_image_solved']}.")
    H.append(f"The row as given is the cheapest image of its ball on {a['cheapest_is_identity']}/{n} rows; some image is strictly "
             f"cheaper on {a['some_image_strictly_cheaper']}/{n}, by a median factor of 10^{fmt(a['median_log_gain'])} where it "
             f"is (median identity rank {fmt(a['median_identity_rank'])} of {summary['median_ball']}).  The shortest image is the cheapest on "
             f"{a['cheapest_is_shortest']}/{n} rows.")
    sp = s['spearman']
    H.append(f"Inside a ball, longer images are somewhat dearer but length is not the ordering: Spearman(total length, "
             f"log cost) pooled {fmt(sp['pooled'])}, per-row median {fmt(sp['per_row_median'])} ({sp['per_row_positive']} rows "
             f"positive, {sp['per_row_negative']} negative); the shortest image is the cheapest on only {a['cheapest_is_shortest']}/{n} rows.")
    d1 = s['depth1']
    best_gen = min(d1.items(), key=lambda kv: kv[1]['median_log_ratio']) if d1 else None
    if best_gen:
        H.append(f"No single depth-1 Whitehead generator helps on average: the best one ({best_gen[1]['auto']}) has median log10 "
                 f"cost ratio {fmt(best_gen[1]['median_log_ratio'], 3)} and is strictly cheaper than the identity on "
                 f"{fmt(best_gen[1]['frac_improves'])} of rows; across the four, the fraction strictly cheaper is "
                 f"{', '.join(fmt(d['frac_improves']) for d in d1.values())}.")
    p = s['pairs']
    g = summary['greedy']
    if p and g.get('pairs') and 'original' in g['per_form'] and '9' in g['per_level']:
        gp = g['pairs']
        H.append(f"The {len(p)} originals whose representative is in the panel (S20): the original as given beats the best image of the "
                 f"representative's radius-2 ball on {sum(1 for q in p if q['orig_beats_rep_ball'])}/{len(p)} pairs; the original's "
                 f"relabel class lies in the representative's radius-2 ball on {sum(1 for q in p if q['orig_in_rep_ball2'])}/{len(p)}, "
                 f"within radius 4 on {sum(1 for q in p if q['orig_in_rep_ball_radius'] is not None)}/{len(p)}.  Plain greedy at "
                 f"{B:,}: identity {g['per_form']['original']['identity_solved']}/{g['per_form']['original']['rows']} originals and "
                 f"{g['per_level']['9']['identity_solved']}/{g['per_level']['9']['rows']} representatives solve; best-of-ball "
                 f"{g['per_form']['original']['any_image_solved']} and {g['per_level']['9']['any_image_solved']}; the original beats the rep's "
                 f"ball on {sum(1 for q in gp if q['orig_beats_rep_ball'])}/{len(gp)} pairs.")
    return H


def main():
    recs = [json.loads(l) for l in open(HERE / 'atlas.jsonl') if l.strip()]
    panel = {r['name']: r for r in csv.DictReader(open(HERE / 'panel.csv'))}
    B = recs[0]['budget']
    by_row = defaultdict(list)
    for r in recs:
        by_row[r['row']].append(r)
    complete = {}
    for name, rs in by_row.items():
        exp = len(ball((panel[name]['r1'], panel[name]['r2']), 2, recs[0]['cap']))
        if len(rs) == exp:
            complete[name] = rs
    summary = OrderedDict(budget=B, cap=recs[0]['cap'], rows=len(complete), rows_partial=len(by_row) - len(complete),
                          records=sum(len(v) for v in complete.values()),
                          pair_rows=sum(1 for n in complete if panel[n]['form'] == 'original' or panel[n]['level'] == '9'),
                          median_ball=int(median([len(v) for v in complete.values()])))
    for arm in ARMS:
        runs = [r[arm] for rs in complete.values() for r in rs if r[arm]]
        summary[f'solved_{arm}'] = sum(1 for u in runs if u['solved'])
        summary[f'verified_{arm}'] = sum(1 for u in runs if u['verified'])
    summary['rejected'] = sum(1 for rs in complete.values() for r in rs for arm in ARMS if r[arm] and r[arm].get('rejected'))
    for arm in ARMS:
        stats = [s for s in (analyse_row(n, rs, arm, B) for n, rs in sorted(complete.items())) if s]
        stats.sort(key=lambda s: (s['level'], s['form'], s['row']))
        if not stats:
            summary[arm] = {'rows': []}
            continue
        pooled_len, pooled_rel, pooled_cost = [], [], []
        for s in stats:
            for r in complete[s['row']]:
                pooled_len.append(r['features']['total_len'])
                pooled_rel.append(r['features']['total_len'] - s['start_len'])
                pooled_cost.append(math.log10(cost_of(r[arm], B)))
        per_row = [s['spearman_len_logcost'] for s in stats if s['spearman_len_logcost'] is not None]
        agg = OrderedDict(
            rows=stats, per_level=aggregate(stats, 'level'), per_form=aggregate(stats, 'form'),
            spearman=OrderedDict(pooled=spearman(pooled_len, pooled_cost), pooled_relative=spearman(pooled_rel, pooled_cost),
                                 pooled_n=len(pooled_len), per_row_median=median(per_row), per_row_n=len(per_row),
                                 per_row_positive=sum(1 for v in per_row if v > 0), per_row_negative=sum(1 for v in per_row if v < 0)),
            depth1=depth1_table(stats),
            pairs=pair_table(stats, complete, panel, B, arm),
        )
        for s in stats:
            s['_all'] = 'all'
        agg['all'] = aggregate(stats, '_all')['all']
        for s in stats:
            del s['_all']
        summary[arm] = agg
    summary['headlines'] = headlines(summary)
    json.dump(summary, open(HERE / 'atlas_summary.json', 'w'), indent=1)
    write_md(summary, HERE / 'ATLAS.md')
    print(f"{summary['rows']} complete rows ({summary['rows_partial']} partial skipped), {summary['records']} records")
    for h in summary['headlines']:
        print('-', h)


if __name__ == '__main__':
    main()
