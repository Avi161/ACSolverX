"""Build the atlas panel: which presentations get an orbit ball searched.

    level 3, 4, 5 rows of benchmark/ladder/ladder_200.csv        20 each
    all level-9 rows of benchmark/ladder/ladder_all.csv          28 (form=autmin)
        (levels 9 + 10 since the 2026-09-11 split; panel.csv is frozen)
    all form=original rows of benchmark/ladder/ladder_all.csv    45

Rows are deduplicated by name (some of the level-3/4 picks of ladder_200 are themselves
originals; the brief's count of 133 counts those twice) and sorted by
``(level, form, name)``.  Columns are the ladder's own:
``name,r1,r2,level,source,form,orbit,pair_id,greedy_nodes,s20_nodes``.

    PYTHONPATH=. python3 -m research.autchoice_20260910.build_panel
"""
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
LADDER = ROOT / 'benchmark' / 'ladder'
COLS = ['name', 'r1', 'r2', 'level', 'source', 'form', 'orbit', 'pair_id', 'greedy_nodes', 's20_nodes']


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build():
    sub = list(csv.DictReader(open(LADDER / 'ladder_200.csv')))
    pool = list(csv.DictReader(open(LADDER / 'ladder_all.csv')))
    picked = {}
    reasons = {}
    for r in sub:
        if r['level'] in ('3', '4', '5'):
            picked.setdefault(r['name'], r)
            reasons.setdefault(r['name'], []).append('ladder_200_L345')
    for r in pool:
        if r['level'] == '9':
            picked.setdefault(r['name'], r)
            reasons.setdefault(r['name'], []).append('level9_rep')
        if r['form'] == 'original':
            picked.setdefault(r['name'], r)
            reasons.setdefault(r['name'], []).append('original')
    rows = sorted(picked.values(), key=lambda r: (int(r['level']), r['form'], r['name']))
    return rows, reasons


def main():
    rows, reasons = build()
    with open(HERE / 'panel.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=COLS, extrasaction='ignore')
        w.writeheader()
        w.writerows(rows)
    manifest = {
        'inputs': {p: sha256(LADDER / p) for p in ('ladder_200.csv', 'ladder_all.csv')},
        'rows': len(rows),
        'per_level': {lv: sum(1 for r in rows if r['level'] == lv) for lv in sorted({r['level'] for r in rows}, key=int)},
        'per_form': {fm: sum(1 for r in rows if r['form'] == fm) for fm in sorted({r['form'] for r in rows})},
        'pair_rows': sum(1 for r in rows if r['form'] == 'original' or r['level'] == '9'),
        'dup_dropped': sum(1 for n, why in reasons.items() if len(why) > 1),
        'multi_reason': {n: why for n, why in reasons.items() if len(why) > 1},
    }
    json.dump(manifest, open(HERE / 'panel_manifest.json', 'w'), indent=1)
    print(json.dumps({k: v for k, v in manifest.items() if k != 'multi_reason'}, indent=1))


if __name__ == '__main__':
    main()
