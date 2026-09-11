"""Per-level report over one or more ``run_ladder`` outputs, with A/B per level.

    PYTHONPATH=. python3 -m benchmark.ladder.report_ladder \\
        --runs greedy=benchmark/ladder/runs/ladder_60_greedy_b10000_c48.jsonl \\
               s20=benchmark/ladder/runs/ladder_60_s20_mk2_b10000_c48.jsonl \\
        --out benchmark/ladder/runs/report_60_10k

For every run: per level, rows / solved / verified, and -- for the pop engines only --
the median pops on the solved rows and the anytime curve ``solved@B`` (a search at
budget B is the first B pops of any longer search, so one run at budget ``N`` grades
every ``B <= N``).  Policy runs are reported by solves only; their charged units are a
budget, not a difficulty (under a table policy a lookup is free -- AGENTS.md section 5),
so they never share a column or a curve with pops.

For every pair of runs sharing rows: gained / lost per level and overall, with the
continuity-corrected McNemar test from ``research/residual_20260909/compare.py``.

Writes ``<out>/REPORT.md`` and ``<out>/report.json``.
"""
import argparse
import json
import statistics
import sys
from collections import OrderedDict
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from research.residual_20260909.compare import _mcnemar, load_run  # noqa: E402

POP_ENGINES = ('greedy', 's20_mk2')
CHECKPOINTS = (100, 1_000, 10_000, 100_000, 1_000_000, 10_000_000)


def _label(spec):
    if '=' in spec:
        label, path = spec.split('=', 1)
        return label, Path(path)
    return Path(spec).stem, Path(spec)


def _level(rec):
    lvl = rec.get('level')
    if lvl in (None, ''):
        return 0            # no level column ("all")
    try:
        return int(lvl)
    except ValueError:
        return str(lvl)     # e.g. 'unsolved' (the unsolved_*.csv panels)


def _level_order(lvl):
    return (isinstance(lvl, str), lvl)


def _med(xs):
    return statistics.median(xs) if xs else None


def describe(records):
    recs = list(records.values())
    engine = recs[0].get('engine') if recs else None
    budget = recs[0].get('budget') if recs else None
    pop = engine in POP_ENGINES
    levels = sorted({_level(r) for r in recs}, key=_level_order)
    checkpoints = [b for b in CHECKPOINTS if budget and b <= budget] if pop else []
    per_level = OrderedDict()
    for lvl in levels + ['all']:
        rs = recs if lvl == 'all' else [r for r in recs if _level(r) == lvl]
        solved = [r for r in rs if r.get('solved')]
        entry = OrderedDict(rows=len(rs), solved=len(solved),
                            verified=sum(1 for r in rs if r.get('verified')),
                            errors=sum(1 for r in rs if r.get('error')))
        if pop:
            entry['median_pops_solved'] = _med([r['nodes'] for r in solved])
            entry['mean_pops_solved'] = round(statistics.fmean([r['nodes'] for r in solved]), 1) if solved else None
            entry['solved_at'] = OrderedDict((str(b), sum(1 for r in solved if r['nodes'] <= b)) for b in checkpoints)
        else:
            entry['median_charged_solved'] = _med([r['nodes'] for r in solved])
            entry['routes'] = OrderedDict(sorted(
                ((k, v) for k, v in _count(r.get('route') for r in solved).items()), key=lambda kv: -kv[1]))
        per_level[str(lvl)] = entry
    return OrderedDict(engine=engine, policy=recs[0].get('policy') if recs else None, budget=budget,
                       cap=recs[0].get('cap') if recs else None,
                       units='pops' if pop else 'charged units (table lookups free)',
                       rows=len(recs), checkpoints=checkpoints, per_level=per_level)


def _count(items):
    out = {}
    for it in items:
        if it is None:
            continue
        out[it] = out.get(it, 0) + 1
    return out


def ab(label_a, a, label_b, b):
    common = [n for n in a if n in b]
    levels = sorted({_level(a[n]) for n in common}, key=_level_order)
    per_level = OrderedDict()
    for lvl in levels + ['all']:
        names = common if lvl == 'all' else [n for n in common if _level(a[n]) == lvl]
        gained = [n for n in names if b[n].get('solved') and not a[n].get('solved')]
        lost = [n for n in names if a[n].get('solved') and not b[n].get('solved')]
        both = sum(1 for n in names if a[n].get('solved') and b[n].get('solved'))
        per_level[str(lvl)] = OrderedDict(rows=len(names), solved_a=sum(1 for n in names if a[n].get('solved')),
                                          solved_b=sum(1 for n in names if b[n].get('solved')),
                                          both=both, gained=len(gained), lost=len(lost),
                                          gained_names=gained[:15], lost_names=lost[:15],
                                          mcnemar=_mcnemar(len(lost), len(gained)))
    return OrderedDict(a=label_a, b=label_b, common_rows=len(common), per_level=per_level)


def markdown(summaries, pairs):
    out = ['# Ladder report', '']
    for label, s in summaries.items():
        arm = s['policy'] or s['engine']
        out.append(f"## `{label}` — {arm}, budget {s['budget']:,}" + (f", cap {s['cap']}" if s['cap'] else '')
                   + f" ({s['units']})")
        out.append('')
        if s['engine'] in POP_ENGINES:
            cps = s['checkpoints']
            out.append('| level | rows | solved | verified | median pops (solved) | ' +
                       ' | '.join(f'solved@{b:,}' for b in cps) + ' |')
            out.append('|---|---:|---:|---:|---:|' + '---:|' * len(cps))
            for lvl, e in s['per_level'].items():
                out.append(f"| {lvl} | {e['rows']} | {e['solved']} | {e['verified']} | "
                           f"{_fmt(e['median_pops_solved'])} | " +
                           ' | '.join(str(e['solved_at'][str(b)]) for b in cps) + ' |')
        else:
            out.append('| level | rows | solved | verified | median charged (solved; lookups free) | routes |')
            out.append('|---|---:|---:|---:|---:|---|')
            for lvl, e in s['per_level'].items():
                routes = ', '.join(f'{k} {v}' for k, v in e['routes'].items())
                out.append(f"| {lvl} | {e['rows']} | {e['solved']} | {e['verified']} | "
                           f"{_fmt(e['median_charged_solved'])} | {routes} |")
        out.append('')
    for p in pairs:
        out.append(f"## `{p['a']}` → `{p['b']}` ({p['common_rows']} common rows)")
        out.append('')
        out.append('| level | rows | solved A | solved B | both | gained (B only) | lost (A only) | McNemar χ² | p |')
        out.append('|---|---:|---:|---:|---:|---:|---:|---:|---:|')
        for lvl, e in p['per_level'].items():
            m = e['mcnemar']
            out.append(f"| {lvl} | {e['rows']} | {e['solved_a']} | {e['solved_b']} | {e['both']} | "
                       f"{e['gained']} | {e['lost']} | {m['statistic']:.2f} | {m['p_value']:.3g} |")
        allp = p['per_level']['all']
        if allp['gained_names'] or allp['lost_names']:
            out.append('')
            if allp['gained_names']:
                out.append('- gained: ' + ', '.join(f'`{n}`' for n in allp['gained_names']) +
                           (' …' if allp['gained'] > len(allp['gained_names']) else ''))
            if allp['lost_names']:
                out.append('- lost: ' + ', '.join(f'`{n}`' for n in allp['lost_names']) +
                           (' …' if allp['lost'] > len(allp['lost_names']) else ''))
        out.append('')
    return '\n'.join(out) + '\n'


def _fmt(x):
    if x is None:
        return '–'
    return f'{x:,.0f}' if isinstance(x, (int, float)) else str(x)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--runs', nargs='+', required=True, help='label=path.jsonl (label optional)')
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args(argv)
    runs = OrderedDict()
    for spec in args.runs:
        label, path = _label(spec)
        if label in runs:
            sys.exit(f'duplicate label {label!r}')
        runs[label] = load_run(path)
    summaries = OrderedDict((label, describe(recs)) for label, recs in runs.items())
    pairs = [ab(la, runs[la], lb, runs[lb]) for la, lb in combinations(runs, 2)
             if set(runs[la]) & set(runs[lb])]
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / 'report.json').write_text(json.dumps(OrderedDict(runs=summaries, pairs=pairs), indent=1) + '\n')
    (args.out / 'REPORT.md').write_text(markdown(summaries, pairs))
    print(f'wrote {args.out / "REPORT.md"}')
    for label, s in summaries.items():
        a = s['per_level']['all']
        print(f"  {label:20} {a['solved']}/{a['rows']} solved, {a['verified']} verified, {a['errors']} errors")


if __name__ == '__main__':
    main()
