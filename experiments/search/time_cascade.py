"""Fresh matched greedy/cascade10k comparison with two certificate decoders."""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import time

import numba

from experiments.equivalence_classes.lib.words import apply_pair
from experiments.search.cascade_heuristics import search
from experiments.search.frontier_heuristics import verify
from experiments.search.greedy_baseline import moves_to_states, str_to_move
from experiments.search.heuristic_1k import ROOT, mixed_search


def verify_second(pair, result):
    states = moves_to_states(*pair, [])
    assert states[0] == result['states'][0]
    for i, step in enumerate(result['steps']):
        if step['kind'] == 'automorphism':
            state = list(apply_pair(states[-1], step['images']))
        else:
            state = moves_to_states(*states[-1], [str_to_move(step['move'])])[-1]
        assert state == result['states'][i+1]
        states.append(state)
    assert len(states) == len(result['states'])
    a, b = states[-1]
    assert len(a) == len(b) == 1 and a.lower() != b.lower()
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    if (args.out/'manifest.json').exists():
        raise ValueError('Use a fresh result directory')
    source = ROOT/'benchmark/subsets/benchmark_subset_60.json'
    rows = json.loads(source.read_text())['subset']
    assert len(rows) == len({r['pres_id'] for r in rows}) == 60
    prior_cascade = ROOT/'results/heuristic_search/goal_frontiers/cascade_1k/runs.jsonl'
    prior_greedy = ROOT/'results/heuristic_search/timing_10k/runs.jsonl'
    expected = {}
    for source_file, method in ((prior_cascade,'cascade'),(prior_greedy,'greedy')):
        for line in source_file.read_text().splitlines():
            r = json.loads(line)
            if method == 'cascade' or r['method'] == 'greedy':
                expected[method,r['pres_id']] = r
    assert len(expected) == 120
    sources = [source, prior_cascade, prior_greedy, Path(__file__)]
    sources += [ROOT/'experiments/search'/p for p in ('cascade_heuristics.py','bs_collapse.py',
                'basis_moves.py','frontier_heuristics.py','heuristic_1k.py','greedy_baseline.py','heuristics.py')]
    sources += [ROOT/'experiments/equivalence_classes/lib/words.py']
    sources += sorted((ROOT/'experiments/heuristic_search/core').glob('*.py'))
    hashes = {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    (args.out/'sources').mkdir()
    for p in sources:
        target = args.out/'sources'/p.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, target)
    numba.set_num_threads(1)
    try:
        priority = f'nice={os.nice(10)}'
    except PermissionError:
        priority = 'inherited; adjustment denied'
    warmup = time.perf_counter()
    for arm in ('greedy','s20','aut_edges'):
        mixed_search(('xyX','yyx'),arm,budget=5,cap=48)
    for pair in (('YYXyx','Yx'),('YxyXX','YYYXyyx')):
        r = search(pair,budget=50)
        if r['solved']:
            assert verify(pair,r) and verify_second(pair,r)
    warmup = time.perf_counter()-warmup
    manifest = dict(budget=10000, timeout=None, ids=[r['pres_id'] for r in rows],
                    methods=['greedy','cascade'], ordinary_search_cap=48, macro_intermediate_cap=256,
                    cascade_settings=dict(starter_budget=500,rewrite_budget=1000,intermediate_cap=256),
                    order='alternate which method goes first per row;30 starts each',
                    clocks='perf_counter wall and process_time CPU around complete search call',
                    excluded='warmup, explicit GC, both certificate decoders, output, cooldown',
                    cooldown='max(0.5 seconds, preceding search wall seconds)',
                    threads=1, pinning='OS schedules physical cores', priority=priority,
                    platform=platform.platform(), warmup_seconds=warmup, source_sha256=hashes,
                    budget_accounting='cascade sums accepted normalization path transforms, macro root+primitive rewrites, and all search/restart pops; normalization candidate image evaluations separately counted and timed')
    (args.out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    assert json.loads((args.out/'manifest.json').read_text()) == manifest
    records = []
    batch_start = time.perf_counter()
    for i,row in enumerate(rows):
        for method in (('greedy','cascade') if i%2 == 0 else ('cascade','greedy')):
            gc.collect()
            pair = row['r1'],row['r2']
            cpu_start, wall_start = time.process_time(),time.perf_counter()
            r = search(pair,budget=10000) if method=='cascade' else mixed_search(pair,'greedy',budget=10000,cap=48)
            wall,cpu = time.perf_counter()-wall_start,time.process_time()-cpu_start
            old = expected[method,row['pres_id']]
            assert all(r[k] == old[k] for k in ('solved','nodes_explored','states','steps'))
            if method=='cascade':
                assert sum(a['nodes'] for a in r['attempts']) == r['nodes_explored'] <= 10000
                assert r['max_certificate_relator_length'] <= 256
            r.update(method=method,pres_id=row['pres_id'],r1=pair[0],r2=pair[1],budget=10000,
                     wall_seconds=wall,cpu_seconds=cpu,previous_trace_match=True)
            r['certificate_verified'] = verify(pair,r) if r['solved'] else None
            r['second_decoder_verified'] = verify_second(pair,r) if r['solved'] else None
            records.append(r)
            with (args.out/'runs.jsonl').open('a') as f:
                f.write(json.dumps(r)+'\n')
            time.sleep(max(.5,wall))
        if (i+1)%10 == 0:
            print(json.dumps({'rows':i+1,'solved':{m:sum(r['solved'] for r in records if r['method']==m)
                                                       for m in ('greedy','cascade')}}),flush=True)
    by_method = {m:{r['pres_id']:r for r in records if r['method']==m} for m in ('greedy','cascade')}
    shared = sorted(set.intersection(*[{i for i,r in rs.items() if r['solved']} for rs in by_method.values()]))
    summary = dict(total={},shared_ids=shared,shared_count=len(shared),shared={},
                   batch_elapsed_including_cooldown_seconds=time.perf_counter()-batch_start)
    for m,rs in by_method.items():
        summary['total'][m] = dict(solved=sum(r['solved'] for r in rs.values()),
            nodes=sum(r['nodes_explored'] for r in rs.values()),
            wall_seconds=sum(r['wall_seconds'] for r in rs.values()),
            cpu_seconds=sum(r['cpu_seconds'] for r in rs.values()))
        summary['shared'][m] = dict(n=len(shared),
            mean_wall_seconds=sum(rs[i]['wall_seconds'] for i in shared)/len(shared),
            mean_cpu_seconds=sum(rs[i]['cpu_seconds'] for i in shared)/len(shared),
            mean_nodes=sum(rs[i]['nodes_explored'] for i in shared)/len(shared))
    assert all(hashlib.sha256(p.read_bytes()).hexdigest()==hashes[str(p.relative_to(ROOT))] for p in sources)
    (args.out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    assert json.loads((args.out/'summary.json').read_text()) == summary
    print(json.dumps(summary),flush=True)


if __name__ == '__main__':
    main()
