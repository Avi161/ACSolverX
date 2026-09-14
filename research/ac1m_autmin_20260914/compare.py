"""Compare Aut(F2)-minimal censuses: is the set of Aut-minimal representatives of AC1M the
same as that of AC19 (the 140,535-row `AC19.txt`) and of `AC19_extended.txt` (156,762 rows)?

    python3 research/ac1m_autmin_20260914/compare.py
"""
from __future__ import annotations

import collections
import csv
import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
R = HERE / 'records'


def load(path):
    opener = gzip.open if str(path).endswith('.gz') else open
    with opener(path, 'rt') as f:
        rows = list(csv.DictReader(f))
    return {(r['r1'], r['r2']): r for r in rows}


def main():
    shipped = load(ROOT / 'data/AC19_extended_aut_min.csv')
    ext = load(R / 'AC19_extended_aut_min_recomputed.csv.gz')
    ac19 = load(R / 'AC19_aut_min.csv.gz')
    ac1m = load(R / 'AC1M_aut_min.csv.gz')
    out = {}
    # 1. the recomputation reproduces the shipped census exactly
    same_keys = set(shipped) == set(ext)
    same_members = same_keys and all(shipped[k]['members'] == ext[k]['members'] for k in shipped)
    out['shipped_vs_recomputed'] = dict(shipped=len(shipped), recomputed=len(ext), same_rep_set=same_keys,
                                        same_member_lists=same_members)
    # 2. AC19.txt versus AC19_extended
    out['ac19_vs_extended'] = dict(ac19=len(ac19), extended=len(ext), ac19_subset_of_extended=set(ac19) <= set(ext),
                                   extended_only=len(set(ext) - set(ac19)))
    # 3. AC1M versus both
    s1m, s19, sx = set(ac1m), set(ac19), set(ext)
    rows1m = sum(int(r['n_members']) for r in ac1m.values())
    inter19 = s1m & s19
    interx = s1m & sx
    rows_in19 = sum(int(ac1m[k]['n_members']) for k in inter19)
    rows_inx = sum(int(ac1m[k]['n_members']) for k in interx)
    only1m = s1m - sx
    only19 = s19 - s1m
    onlyx = sx - s1m
    mu = lambda k: len(k[0]) + len(k[1])
    out['ac1m'] = dict(rows=rows1m, orbits=len(s1m),
                       orbits_shared_with_ac19=len(inter19), orbits_shared_with_extended=len(interx),
                       ac1m_rows_in_ac19_orbits=rows_in19, ac1m_rows_in_extended_orbits=rows_inx,
                       ac1m_only_orbits=len(only1m), ac19_only_orbits=len(only19), extended_only_orbits=len(onlyx),
                       equal_to_ac19=s1m == s19, equal_to_extended=s1m == sx,
                       ac1m_only_mu_hist=dict(sorted(collections.Counter(mu(k) for k in only1m).items())),
                       ac1m_only_rows=sum(int(ac1m[k]['n_members']) for k in only1m),
                       ac19_only_mu_hist=dict(sorted(collections.Counter(mu(k) for k in only19).items())),
                       ac19_only_rows=sum(int(ac19[k]['n_members']) for k in only19),
                       extended_only_mu_hist=dict(sorted(collections.Counter(mu(k) for k in onlyx).items())),
                       extended_only_rows=sum(int(ext[k]['n_members']) for k in onlyx))
    # where do the extended-only orbits live in AC19_extended.txt?  (first 634 = MS-640 rows,
    # then AC19.txt rows, then the length > 19 tail)
    lines = [l.strip() for l in open(ROOT / 'data/AC19_extended.txt') if l.strip()]
    def length(i):
        v = [int(t) for t in lines[i].strip('[]').split(',')]
        return sum(1 for t in v if t)
    src = collections.Counter()
    for k in onlyx:
        ms = [int(m) for m in ext[k]['members'].split()]
        kinds = {('ms634' if m < 634 else ('len<=19' if length(m) <= 19 else 'len>19')) for m in ms}
        src['+'.join(sorted(kinds))] += 1
    out['extended_only_orbits_by_source'] = dict(src)
    # examples
    out['examples'] = dict(ac1m_only=[k for k in sorted(only1m, key=lambda k: (mu(k), k))[:10]],
                           ac19_only=[k for k in sorted(only19, key=lambda k: (mu(k), k))[:10]])
    # member-count agreement on shared orbits: orbit sizes in AC1M vs AC19
    size_pairs = collections.Counter()
    for k in list(inter19)[:200000]:
        size_pairs[(int(ac19[k]['n_members']) > 1, int(ac1m[k]['n_members']) > 1)] += 1
    out['shared_orbit_size_pattern (ac19_multi, ac1m_multi)'] = {str(k): v for k, v in size_pairs.items()}
    (R / 'compare.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
