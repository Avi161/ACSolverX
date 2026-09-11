"""How fast each method reaches its reductions on the 36 unreduced classes.

For every class and method: the best total (raw) or mu reached, and the pop
count at which that best state was first generated (``pops_to_best``).  The
10M S20_MK2 reference run recorded only its final minimum (no pop index).
Methods: reduce_search s20 / aut_edges (raw, replayed paths), mu_probe
(Whitehead-minimal mu of visited states), orbit_search (mu, re-rooted at the
orbit rep), aut_start (best over starting automorphisms; pops counted inside
the winning start's own search)."""
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
    cols = {}
    for r in load('aca36_initial_reduce_10000.jsonl'):
        if r['path_replayed']:
            cols.setdefault(f"raw:{r['arm']}", {})[r['name']] = (r['best_total'], r.get('pops_to_best'))
    for r in load('aca36_initial_mu_10000.jsonl'):
        if r['path_replayed']:
            cols.setdefault(f"mu:{r['arm']}", {})[r['name']] = (r['best_mu'], r.get('pops_to_best'))
    orbit = 'aca36_initial_orbit_10000_v2.jsonl' if (HERE / 'aca36_initial_orbit_10000_v2.jsonl').exists() else 'aca36_initial_orbit_10000.jsonl'
    for r in load(orbit):
        if r['path_replayed']:
            cols.setdefault('mu:orbit', {})[r['name']] = (r['best_mu'], r.get('pops_to_best'))
    starts = defaultdict(list)
    for r in load('aca36_initial_autstart_1000.jsonl'):
        starts[r['name']].append(r)
    for name, rs in starts.items():
        b = min(r['best_mu'] for r in rs)
        cols.setdefault('mu:autstart', {})[name] = (b, min(r['pops_to_best'] for r in rs if r['best_mu'] == b))
    ref = {}
    for r in load('ref_u124_10m_s20_mk2_b10000000_mrl64.jsonl'):
        if r.get('name') in mu and (r['name'] not in ref or r.get('nodes_explored', 0) >= ref[r['name']].get('nodes_explored', 0)):
            ref[r['name']] = r
    order = [c for c in ['raw:s20', 'raw:aut_edges', 'mu:s20', 'mu:aut_edges', 'mu:orbit', 'mu:autstart'] if c in cols]
    print('class     init ladder 10M | ' + ' | '.join(f'{c:>16s}' for c in order) + '   (best@pops)')
    firsts = defaultdict(list)
    for name, row in mu.items():
        mi, mo = int(row['mu_in']), int(row['mu_out'])
        r10 = int(ref[name]['min_relator_length']) if name in ref else None
        cells = []
        for c in order:
            v = cols[c].get(name)
            cells.append('              -' if v is None else f"{v[0]:3d}@{v[1] if v[1] is not None else '?':>6}" + ('*' if v[0] < mi else ' '))
            if v is not None and v[0] < mi:
                firsts[c].append(v[1] or 0)
        print(f"{name:9s} {mi:3d} {mo:5d} {str(r10) if r10 else '-':>4} | " + ' | '.join(f'{x:>16s}' for x in cells))
    print()
    for c in order:
        n = len(firsts[c])
        if n:
            print(f"{c:13s} reduced {n:2d} of 36; pops to the reducing state: median {sorted(firsts[c])[n // 2]}, max {max(firsts[c])}")
    if ref:
        print('10M S20_MK2  reduced', sum(1 for n, r in ref.items() if int(r['min_relator_length']) < int(mu[n]['mu_in'])), 'of 36 (pop index not recorded; budget 10,000,000)')
    print('* = strictly below the initial length')


if __name__ == '__main__':
    main()
