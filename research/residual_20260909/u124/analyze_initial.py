"""Gap-to-ladder table for the 36 mu-ladder-reduced classes, starting from the
UNREDUCED (initial) pairs: for each method, the best total length reached by a
replayed AC-move path (raw, and Whitehead-minimal mu where the method computes
it), against the ladder's floor ``mu_out``."""
import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name):
    p = HERE / name
    return [json.loads(l) for l in open(p)] if p.exists() else []


def main():
    mu = {r['name']: r for r in csv.DictReader(open(HERE / 'aca36_initial.csv'))}
    best = defaultdict(dict)   # name -> method -> best total (raw or mu)
    for r in load('aca36_initial_reduce_10000.jsonl'):
        if r['path_replayed']:
            best[r['name']][f"raw:{r['arm']}"] = r['best_total']
    for r in load('aca36_initial_mu_10000.jsonl'):
        if r['path_replayed']:
            best[r['name']][f"mu:{r['arm']}"] = r['best_mu']
    orbit_file = 'aca36_initial_orbit_10000_v2.jsonl' if (HERE / 'aca36_initial_orbit_10000_v2.jsonl').exists() else 'aca36_initial_orbit_10000.jsonl'
    for r in load(orbit_file):
        if r['path_replayed']:
            best[r['name']]['mu:orbit'] = r['best_mu']
    autstart = defaultdict(list)
    for r in load('aca36_initial_autstart_1000.jsonl'):
        autstart[r['name']].append(r)
    for name, rs in autstart.items():
        best[name]['raw:autstart'] = min(r['best_total'] for r in rs)
        best[name]['mu:autstart'] = min(r['best_mu'] for r in rs)
    for r in load('aca36_initial_K3p_c14aut_10000.jsonl'):
        if r.get('min_total_length_seen') is not None:
            best[r['name']]['raw:cascade'] = r['min_total_length_seen']
    ref = {}
    for r in load('ref_u124_10m_s20_mk2_b10000000_mrl64.jsonl'):
        if r.get('name') in mu and (r['name'] not in ref or r.get('nodes_explored', 0) >= ref[r['name']].get('nodes_explored', 0)):
            ref[r['name']] = r
    for name, r in ref.items():
        best[name]['ref:10M_s20'] = int(r['min_relator_length'])
    methods = ['raw:s20', 'raw:aut_edges', 'raw:cascade', 'raw:autstart', 'mu:s20', 'mu:aut_edges', 'mu:orbit', 'mu:autstart', 'ref:10M_s20']
    present = [m for m in methods if any(m in b for b in best.values())]
    print('name      init ladder | ' + ' | '.join(f'{m:13s}' for m in present) + ' | best  gap')
    gaps = []
    reached = defaultdict(int)
    for name, row in mu.items():
        mi, mo = int(row['mu_in']), int(row['mu_out'])
        vals = {m: best[name].get(m) for m in present}
        ours = {m: v for m, v in vals.items() if not m.startswith('ref:') and v is not None}
        b = min(ours.values()) if ours else mi
        gaps.append(b - mo)
        for m, v in vals.items():
            if v is not None and v <= mo:
                reached[m] += 1
        cells = ' | '.join(f"{(str(v) + ('*' if v is not None and v < mi else '')) if v is not None else '-':13s}" for v in vals.values())
        print(f'{name:9s} {mi:3d} {mo:5d}  | {cells} | {b:4d}  {b - mo:+d}')
    n = len(mu)
    print()
    print('rows where the best AC-move path reaches the ladder floor:', sum(g <= 0 for g in gaps), 'of', n,
          '; total gap (letters above the ladder floors):', sum(max(0, g) for g in gaps),
          '; initial excess over the floors:', sum(int(r['mu_in']) - int(r['mu_out']) for r in mu.values()))
    print('rows reaching the floor, by method:', dict(reached))
    print('rows strictly reduced (any method):', sum(1 for name, row in mu.items() if any(v is not None and v < int(row['mu_in']) for v in best[name].values())))
    print('* = strictly below the initial length')


if __name__ == '__main__':
    main()
