"""Render RESULTS.md tables from the benchmark JSON records (never by hand)."""
from __future__ import annotations

import json
import sys
from pathlib import Path


def load(paths):
    reports = [json.loads(Path(p).read_text()) for p in paths]
    rows = {}
    for rep in reports:
        for row in rep['rows']:
            entry = rows.setdefault(row['name'], {
                'panel': row['panel'], 'rank2_length': row['rank2_length'],
                'rank': row['rank'], 'definitions': row['definitions'],
                'preprocessing_units': row['preprocessing_units'],
                'root_digram_disjoint': row['root_digram_disjoint'],
                'root_min_relator': min(len(w) for w in row['triangle_state']),
                'root_coupling': tuple(row['root_coupling']), 'arms': []})
            entry['arms'].extend(row['arms'])
    return reports, rows


def mark(arm):
    if arm['unit_found']:
        return 'U'
    if arm['bigon_found']:
        return 'B'
    return '.'


def render(paths):
    reports, rows = load(paths)
    caps = sorted({a['relator_cap'] for r in rows.values() for a in r['arms']})
    orderings = []
    for r in rows.values():
        for a in r['arms']:
            if a['ordering'] not in orderings:
                orderings.append(a['ordering'])
    pops = sorted({a['pop_budget'] for r in rows.values() for a in r['arms']})
    out = []
    out.append('| row | panel | rank-2 L | rank | defs | prep units | root min relator | root disjoint | ' +
               ' | '.join(f'{o}@{c}' for c in caps for o in orderings) + ' |')
    out.append('|---|---|---:|---:|---:|---:|---:|:---:|' + '|'.join(':---:' for _ in caps for _ in orderings) + '|')
    for name, r in sorted(rows.items(), key=lambda kv: (kv[1]['panel'] != 'hard', kv[0])):
        cells = []
        for c in caps:
            for o in orderings:
                arms = [a for a in r['arms'] if a['relator_cap'] == c and a['ordering'] == o]
                if not arms:
                    cells.append('n/a')
                    continue
                a = arms[0]
                cells.append(f"{mark(a)} ({a['heap_pops']}p/{a['rotation_products']:,}rp)")
        out.append(f"| {name} | {r['panel']} | {r['rank2_length']} | {r['rank']} | {r['definitions']} | "
                   f"{r['preprocessing_units']} | {r['root_min_relator']} | {'yes' if r['root_digram_disjoint'] else 'no'} | " + ' | '.join(cells) + ' |')
    # totals
    tot = {}
    for r in rows.values():
        for a in r['arms']:
            k = (a['relator_cap'], a['ordering'], r['panel'] + ('' if r['root_min_relator'] == 3 else ' (short root)'))
            t = tot.setdefault(k, {'rows': 0, 'bigon': 0, 'unit': 0, 'pops': 0, 'rp': 0, 'states': 0, 'cpu': 0.0})
            t['rows'] += 1; t['bigon'] += a['bigon_found']; t['unit'] += a['unit_found']
            t['pops'] += a['heap_pops']; t['rp'] += a['rotation_products']
            t['states'] += a['discovered_states']; t['cpu'] += a['cpu_seconds']
    out.append('')
    out.append('| cap | ordering | panel | rows | bigon exposed | unit exposed | pops | rotation products | states | CPU s |')
    out.append('|---:|---|---|---:|---:|---:|---:|---:|---:|---:|')
    for (c, o, p), t in sorted(tot.items()):
        out.append(f"| {c} | {o} | {p} | {t['rows']} | {t['bigon']} | {t['unit']} | {t['pops']:,} | {t['rp']:,} | {t['states']:,} | {t['cpu']:.1f} |")
    return '\n'.join(out), reports


if __name__ == '__main__':
    text, reports = render(sys.argv[1:])
    print(text)
