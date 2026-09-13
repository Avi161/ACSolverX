"""Render RESULTS tables from the JSONL records.

    python3 make_results.py records/ladder_p2000.jsonl records/u124_p2000.jsonl > RESULTS_TABLES.md
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict


def load(files):
    recs = []
    for fn in files:
        with open(fn) as f:
            for line in f:
                recs.append(json.loads(line))
    return recs


def auc(pos, neg):
    """P(score(pos) > score(neg)) + 0.5 P(equal); pos = U124, neg = solved."""
    if not pos or not neg:
        return float('nan')
    wins = 0.0
    for a in pos:
        for b in neg:
            wins += 1.0 if a > b else 0.5 if a == b else 0.0
    return wins / (len(pos) * len(neg))


def main(files):
    recs = load(files)
    ladder = [r for r in recs if r['panel'] == 'ladder']
    u124 = [r for r in recs if r['panel'] == 'u124']
    arms = sorted({r['arm'] for r in recs})
    thresholds = [100, 300, 1000, 2000]
    out = []
    if ladder:
        pops_budget = max(r['params']['pops'] for r in ladder)
        out.append(f'## Solved ladder (60 rows), solves by difficulty bin and pop budget (max {pops_budget})\n')
        out.append('Cell = rows solved within that many heap pops (best-first is deterministic, so one run at the '
                   'largest budget gives every smaller budget).\n')
        bins = sorted({r['bin'] for r in ladder})
        for arm in arms:
            rows = [r for r in ladder if r['arm'] == arm]
            if not rows:
                continue
            out.append(f'\n### arm `{arm}`\n')
            out.append('| bin | rows | ' + ' | '.join(f'<= {t} pops' for t in thresholds) + ' | unsolved | verified | mean states (solved) | CPU s |')
            out.append('|---:|---:|' + '---:|' * len(thresholds) + '---:|---:|---:|---:|')
            tot = defaultdict(int)
            for b in bins:
                rr = [r for r in rows if r['bin'] == b]
                cells = []
                for t in thresholds:
                    c = sum(1 for r in rr if r['solved'] and r['pops'] <= t)
                    cells.append(c)
                    tot[t] += c
                uns = sum(1 for r in rr if not r['solved'])
                ver = sum(1 for r in rr if r['solved'] and r['verified'])
                st = [r['states'] for r in rr if r['solved']]
                cpu = sum(r['cpu_seconds'] for r in rr)
                tot['rows'] += len(rr); tot['uns'] += uns; tot['ver'] += ver; tot['cpu'] += cpu
                out.append(f'| {b} | {len(rr)} | ' + ' | '.join(str(c) for c in cells) +
                           f' | {uns} | {ver} | {sum(st)/len(st):,.0f} | {cpu:,.1f} |' if st else
                           f'| {b} | {len(rr)} | ' + ' | '.join(str(c) for c in cells) + f' | {uns} | {ver} | - | {cpu:,.1f} |')
            out.append(f'| **all** | {tot["rows"]} | ' + ' | '.join(str(tot[t]) for t in thresholds) +
                       f' | {tot["uns"]} | {tot["ver"]} | | {tot["cpu"]:,.1f} |')
        # per-row table
        out.append('\n### Per row (pops to solve; `-` = unsolved at the budget)\n')
        out.append('| row | bin | r1, r2 | L | greedy nodes (1M budget) | ' + ' | '.join(arms) + ' | dyn min L | dyn path (defs/elims/prods, max rank) |')
        out.append('|---|---:|---|---:|---:|' + '---:|' * len(arms) + '---:|---|')
        by = defaultdict(dict)
        for r in ladder:
            by[r['name']][r['arm']] = r
        order = sorted(by, key=lambda n: (by[n][arms[0]]['bin'], int(n)))
        for n in order:
            d = by[n]
            any_r = next(iter(d.values()))
            cells = []
            for arm in arms:
                r = d.get(arm)
                cells.append('-' if r is None else (str(r['pops']) if r['solved'] else '-'))
            dyn = d.get('dyn')
            cert = ''
            if dyn and dyn['solved'] and dyn.get('certificate'):
                c = dyn['certificate']
                cert = f"{c['steps']} ({c['defines']}/{c['eliminates']}/{c['products']}, {c['max_rank']})"
            out.append(f"| {n} | {any_r['bin']} | `{any_r['r1']}`, `{any_r['r2']}` | {any_r['root_length']} | "
                       f"{any_r['greedy_nodes_1M'] if any_r['greedy_nodes_1M'] is not None else '-'} | " + ' | '.join(cells) +
                       f" | {dyn['min_total_length'] if dyn else '-'} | {cert} |")
    if u124:
        out.append('\n## U124 rows\n')
        for arm in sorted({r['arm'] for r in u124}):
            rows = [r for r in u124 if r['arm'] == arm]
            solved = [r for r in rows if r['solved']]
            out.append(f'arm `{arm}`: {len(rows)} rows, solved {len(solved)}, pops budget {max(r["params"]["pops"] for r in rows)}, '
                       f'total CPU {sum(r["cpu_seconds"] for r in rows):,.0f} s')
            if solved:
                out.append('\n**SOLVED U124 ROWS (verify independently before believing):** ' +
                           ', '.join(f"{r['name']} (verified={r['verified']})" for r in solved))
        out.append('\n| row | r1, r2 | L | arm | pops | states | min total length | max rank | CPU s |')
        out.append('|---|---|---:|---|---:|---:|---:|---:|---:|')
        for r in sorted(u124, key=lambda r: (int(r['name'].split('_')[1]), r['arm'])):
            out.append(f"| {r['name']} | `{r['r1']}`, `{r['r2']}` | {r['root_length']} | {r['arm']} | {r['pops']} | {r['states']:,} | "
                       f"{r['min_total_length']} | {r['max_rank']} | {r['cpu_seconds']:.1f} |")
    if ladder and u124:
        out.append('\n## Separation: U124 vs solved ladder rows under the same arm and budget\n')
        out.append('AUC = probability that a U124 row scores above a solved row (0.5 = no separation).\n')
        out.append('| arm | feature | AUC vs all solved | AUC vs solved bins 6-9 | mean U124 | mean solved | mean solved 6-9 |')
        out.append('|---|---|---:|---:|---:|---:|---:|')
        for arm in sorted({r['arm'] for r in u124} & {r['arm'] for r in ladder}):
            ur = [r for r in u124 if r['arm'] == arm]
            lr = [r for r in ladder if r['arm'] == arm]
            hard = [r for r in lr if r['bin'] >= 6]
            feats = {
                'unsolved at budget (1/0)': lambda r: 0 if r['solved'] else 1,
                'pops used': lambda r: r['pops'],
                'min total length / L': lambda r: r['min_total_length'] / r['root_length'],
                'min total length': lambda r: r['min_total_length'],
                'states': lambda r: r['states'],
                'max rank': lambda r: r['max_rank'],
                'root length L': lambda r: r['root_length'],
            }
            for name, f in feats.items():
                a = [f(r) for r in ur]; b = [f(r) for r in lr]; c = [f(r) for r in hard]
                out.append(f'| {arm} | {name} | {auc(a, b):.4f} | {auc(a, c):.4f} | {sum(a)/len(a):.2f} | {sum(b)/len(b):.2f} | '
                           f'{(sum(c)/len(c)) if c else float("nan"):.2f} |')
            ratio = lambda r: r['min_total_length'] / r['root_length']
            out.append(f'\n### Threshold on `min total length / L` (arm `{arm}`)\n')
            out.append('| threshold t | solved rows with ratio < t (of %d) | solved bins 6-9 with ratio < t (of %d) | U124 rows with ratio < t (of %d) |' % (len(lr), len(hard), len(ur)))
            out.append('|---:|---:|---:|---:|')
            for t in (0.70, 0.75, 0.78, 0.80, 0.81, 0.85, 0.90, 1.00):
                out.append(f'| {t:.2f} | {sum(ratio(r) < t for r in lr)} | {sum(ratio(r) < t for r in hard)} | {sum(ratio(r) < t for r in ur)} |')
            out.append(f'\nU124 ratio range: {min(map(ratio, ur)):.3f} .. {max(map(ratio, ur)):.3f}; '
                       f'solved-ladder ratio range: {min(map(ratio, lr)):.3f} .. {max(map(ratio, lr)):.3f} '
                       f'(unsolved solved-ladder rows only: {min(ratio(r) for r in lr if not r["solved"]):.3f} .. {max(ratio(r) for r in lr if not r["solved"]):.3f}).')
            out.append('\nU124 shortening `L - min total length` histogram: ' +
                       ', '.join(f'{k}: {v}' for k, v in sorted(__import__("collections").Counter(r["root_length"] - r["min_total_length"] for r in ur).items())))
    print('\n'.join(out))


if __name__ == '__main__':
    main(sys.argv[1:])
