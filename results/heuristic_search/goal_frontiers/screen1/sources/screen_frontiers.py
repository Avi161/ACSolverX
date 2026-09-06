"""Serial, reproducible small-budget screening of declared search settings."""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
from pathlib import Path
import shutil
import time

import numba

from experiments.search.frontier_heuristics import search, verify
from experiments.search.heuristic_1k import ROOT

SCREEN = (0, 247, 203, 546, 538, 602, 565, 568, 596, 605, 634, 622, 637)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--settings', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--budget', type=int, default=1000)
    parser.add_argument('--cap', type=int, default=48)
    parser.add_argument('--full', action='store_true')
    parser.add_argument('--ids')
    args = parser.parse_args()
    if not 1 <= args.budget <= 10000 or not 1 <= args.cap <= 128:
        raise ValueError('budget/cap out of range')
    settings = json.loads(args.settings.read_text())
    assert isinstance(settings, dict) and settings
    source = ROOT / 'benchmark/subsets/benchmark_subset_60.json'
    rows = json.loads(source.read_text())['subset']
    wanted = set(map(int, args.ids.split(','))) if args.ids else (None if args.full else set(SCREEN))
    if wanted is not None:
        rows = [r for r in rows if r['pres_id'] in wanted]
        assert {r['pres_id'] for r in rows} == wanted
    if (args.out / 'manifest.json').exists():
        raise ValueError('Use a fresh result directory')
    args.out.mkdir(parents=True, exist_ok=True)
    snapshots = args.out / 'sources'
    snapshots.mkdir()
    paths = [source, args.settings, Path(__file__), ROOT / 'experiments/search/frontier_heuristics.py',
             ROOT / 'experiments/search/basis_moves.py', ROOT / 'experiments/search/heuristic_1k.py',
             ROOT / 'experiments/search/greedy_baseline.py', ROOT / 'experiments/search/heuristics.py',
             ROOT / 'experiments/equivalence_classes/lib/words.py']
    paths += sorted((ROOT / 'experiments/heuristic_search/core').glob('*.py'))
    hashes = {}
    for p in paths:
        hashes[str(p.resolve().relative_to(ROOT))] = hashlib.sha256(p.read_bytes()).hexdigest()
        shutil.copyfile(p, snapshots / p.name)
    numba.set_num_threads(1)
    try:
        priority = f'nice={os.nice(10)}'
    except PermissionError:
        priority = 'inherited; priority adjustment denied'
    start = time.perf_counter()
    for setting in settings.values():
        record = search(('YYXyx', 'Yx'), budget=5, cap=args.cap, **setting)
        if record['solved']:
            assert verify(('YYXyx', 'Yx'), record)
    manifest = dict(settings=settings, ids=[r['pres_id'] for r in rows], budget=args.budget,
                    cap=args.cap, source_sha256=hashes, warmup_seconds=time.perf_counter()-start,
                    priority=priority, threads=1, timeout=None,
                    search_timing='wall perf_counter and CPU process_time around search; normalization included',
                    excluded='warmup, explicit GC, verification, output, cooldown',
                    execution='serial; rotating settings per row; cooldown max(0.5s, preceding search wall)',
                    scope='exploratory subset60 selection; structurally different candidates may advance despite low1k count')
    (args.out / 'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    assert json.loads((args.out / 'manifest.json').read_text()) == manifest
    records = []
    names = tuple(settings)
    for i, row in enumerate(rows):
        shift = i % len(names)
        for name in names[shift:]+names[:shift]:
            gc.collect()
            cpu_start, wall_start = time.process_time(), time.perf_counter()
            result = search((row['r1'], row['r2']), budget=args.budget, cap=args.cap, **settings[name])
            wall, cpu = time.perf_counter()-wall_start, time.process_time()-cpu_start
            result.update(method=name, settings=settings[name], pres_id=row['pres_id'],
                          r1=row['r1'], r2=row['r2'], budget=args.budget, cap=args.cap,
                          wall_seconds=wall, cpu_seconds=cpu)
            result['certificate_verified'] = verify((row['r1'], row['r2']), result) if result['solved'] else None
            with (args.out / 'runs.jsonl').open('a') as f:
                f.write(json.dumps(result)+'\n')
            records.append(result)
            print(json.dumps({k:result[k] for k in ('method','pres_id','solved','nodes_explored','wall_seconds')}), flush=True)
            time.sleep(max(.5, wall))
    summary = {}
    for name in names:
        rs = [r for r in records if r['method'] == name]
        summary[name] = dict(n=len(rs), solved=sum(r['solved'] for r in rs),
                             solved_ids=[r['pres_id'] for r in rs if r['solved']],
                             pops=sum(r['nodes_explored'] for r in rs),
                             wall_seconds=sum(r['wall_seconds'] for r in rs),
                             cpu_seconds=sum(r['cpu_seconds'] for r in rs))
    assert all(hashlib.sha256(p.read_bytes()).hexdigest() == hashes[str(p.resolve().relative_to(ROOT))] for p in paths)
    (args.out / 'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps(summary), flush=True)


if __name__ == '__main__':
    main()
