#!/usr/bin/env python3
"""Exhaust every one-definition literal-substitution CoV on one rank-two pair.

Unlike cov.py's deterministic maximal pass, this enumerates every subset of
pairwise-disjoint occurrences of w or w^-1 in every cyclic rotation of each
relator.  It therefore covers all literal one-stabilizer substitution choices.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WT = ROOT / '.claude/worktrees/codex-proofs'
sys.path.insert(0, str(ROOT / '.scratch'))
sys.path.insert(0, str(WT))
import search_two_block_relative_basis as b
from experiments.stable_ac.cov.cov import isolate, relabel, substitute_generator
from experiments.stable_ac.cov.cov import word_to_str
from experiments.equivalence_classes.lib.autcanon import aut_canon, check, phi_str


def linear_variants(word, pattern):
    pinv = b.inv(pattern)
    size = len(pattern)
    found = set()
    def visit(i, out, count):
        if i >= len(word):
            found.add((b.red(out), count))
            return
        visit(i+1, out+(word[i],), count)
        chunk = word[i:i+size]
        if len(chunk) == size and chunk == pattern:
            visit(i+size, out+(3,), count+1)
        elif len(chunk) == size and chunk == pinv:
            visit(i+size, out+(-3,), count+1)
    visit(0, (), 0)
    return found


def cyclic_variants(word, pattern):
    found = set()
    for shift in range(len(word)):
        rotated = word[shift:]+word[:shift]
        found.update(linear_variants(rotated, pattern))
    return found


def all_cyclic_subwords(words):
    """All nonempty freely reduced cyclic intervals, including conjugate-shaped words."""
    found=set()
    for word in words:
        word=b.cyc(word); n=len(word); doubled=word+word
        for size in range(1,n+1):
            for start in range(n):
                u=tuple(doubled[start:start+size])
                # A cyclic interval in a cyclically reduced word is linearly reduced.
                assert b.red(u)==u
                found.add(max(u,b.inv(u)))
    return sorted(found,key=lambda u:(len(u),u))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--name',required=True);ap.add_argument('--r1',required=True);ap.add_argument('--r2',required=True)
    ap.add_argument('--target-r1');ap.add_argument('--target-r2');ap.add_argument('--out',required=True)
    a=ap.parse_args()
    source=(b.parse(a.r1),b.parse(a.r2))
    source_s=(a.r1,a.r2)
    source_mu,source_rep,source_phi=aut_canon(source_s)
    target_rep=None
    if a.target_r1:
        target_rep=aut_canon((a.target_r1,a.target_r2))[1]
    words=all_cyclic_subwords(source)
    endpoints={}
    attempts=0
    for w in words:
        variants=[cyclic_variants(r,w) for r in source]
        definition=(-3,)+w
        for r1,n1 in variants[0]:
            for r2,n2 in variants[1]:
                if n1+n2==0: continue
                for gen_name,gen in [('x',1),('y',2)]:
                    for idx,(iso,other) in enumerate(((r1,r2),(r2,r1))):
                        attempts+=1
                        ok,expr=isolate(iso,x=gen,z=3)
                        if not ok: continue
                        kept=substitute_generator(other,gen,expr)
                        defined=substitute_generator(definition,gen,expr)
                        if not kept or not defined: continue
                        out=(word_to_str(relabel(kept,gen_name)),word_to_str(relabel(defined,gen_name)))
                        mu,rep,phi=aut_canon(out)
                        key=(rep,mu)
                        row={'w':b.text(w),'n_subs':n1+n2,'iso_gen':gen_name,'iso_index':idx,
                             'intermediate':[b.text(r1),b.text(r2),b.text(definition)],
                             'expr':b.text(expr),'target':list(out),'mu':mu,'rep':list(rep),
                             'phi':phi,'phi_check':check(out,rep,phi)}
                        if key not in endpoints:endpoints[key]=row
    rows=list(endpoints.values())
    payload={'schema':'exhaustive-single-cov-v1','name':a.name,'source':list(source_s),
             'source_mu':source_mu,'source_rep':list(source_rep),'cyclic_words':len(words),
             'variant_attempts':attempts,'distinct_endpoint_orbits':len(rows),
             'minimum_endpoint_mu':min((r['mu'] for r in rows),default=None),
             'target_rep':list(target_rep) if target_rep else None,
             'target_orbit_hits':sum(tuple(r['rep'])==target_rep for r in rows) if target_rep else None,
             'endpoints':rows}
    Path(a.out).write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:payload[k] for k in ('name','source_mu','cyclic_words','variant_attempts',
          'distinct_endpoint_orbits','minimum_endpoint_mu','target_orbit_hits')}))

if __name__=='__main__':main()
