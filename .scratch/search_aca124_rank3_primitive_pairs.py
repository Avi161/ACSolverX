#!/usr/bin/env python3
"""Primitive-pair scan of one-definition rank-three intermediates for aca_124."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from itertools import combinations
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
WT=ROOT/'.claude/worktrees/codex-proofs'
sys.path.insert(0,str(ROOT/'.scratch'));sys.path.insert(0,str(WT))
import exhaustive_single_cov as ex
import search_two_block_relative_basis as b
from experiments.stable_ac.cov.cov import substitute_word
from experiments.stable_ac.rank3_compression.one_edge import cyclic_reduce
from experiments.stable_ac.rank3_compression.rank3_whitehead import (
    apply_automorphism, canonical_cyclic_pair, check_reduction,
    is_primitive_pair, reduce_pair,
)


def quotient_word(word, killed):
    return b.text(b.cyc(tuple(a for a in b.parse(word) if abs(a) not in killed)))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data',required=True);ap.add_argument('--out',required=True)
    ap.add_argument('--min-word-len',type=int,default=1);ap.add_argument('--max-word-len',type=int)
    a=ap.parse_args(); cache={}; hits=[]; summaries=[]; trace=hashlib.sha256()
    totals={'classes':0,'words':0,'intermediates':0,'pairs':0,'distinct_pairs':0,'primitive':0,
            'primitive_no_old_isolator':0}
    with open(a.data,newline='') as f:
      for row in csv.DictReader(f):
        totals['classes']+=1;source=(b.parse(row['r1']),b.parse(row['r2']))
        words=[w for w in ex.all_cyclic_subwords(source) if len(w)>=a.min_word_len and
               (a.max_word_len is None or len(w)<=a.max_word_len)]
        local={'name':row['name'],'words':len(words),'intermediates':0,'pairs':0,'primitive':0,
               'primitive_no_old_isolator':0}
        totals['words']+=len(words)
        for w in words:
          r1,n1=substitute_word(source[0],w,z_sym=3);r2,n2=substitute_word(source[1],w,z_sym=3)
          if n1+n2==0:continue
          rels=(b.text(r1),b.text(r2),'Z'+b.text(w));local['intermediates']+=1;totals['intermediates']+=1
          for left,right in combinations(range(3),2):
            pair=canonical_cyclic_pair((rels[left],rels[right]));local['pairs']+=1;totals['pairs']+=1
            reduction=cache.get(pair)
            if reduction is None:
              reduction=reduce_pair(pair,generators=('x','y','z'));cache[pair]=reduction
            primitive=is_primitive_pair(reduction)
            trace.update(('\0'.join((row['name'],b.text(w),str(left),str(right),*pair,
              str(reduction.minimum_total),'1' if primitive else '0'))+'\n').encode())
            if not primitive:continue
            check_reduction(pair,reduction);local['primitive']+=1;totals['primitive']+=1
            no_old_isolator=all(sum(c.lower()==g for c in rels[i])!=1 for i in (left,right) for g in ('x','y'))
            local['primitive_no_old_isolator']+=int(no_old_isolator);totals['primitive_no_old_isolator']+=int(no_old_isolator)
            transformed=tuple(cyclic_reduce(apply_automorphism(r,reduction.phi)) for r in rels)
            letters=tuple(transformed[i].lower() for i in (left,right))
            if any(len(transformed[i])!=1 for i in (left,right)) or len(set(letters))!=2:
              raise AssertionError('primitive pair did not become two letters')
            killed={('x','y','z').index(g)+1 for g in letters}
            survivor_index=({0,1,2}-{left,right}).pop(); quotient=quotient_word(transformed[survivor_index],killed)
            hits.append({'name':row['name'],'source':[row['r1'],row['r2']],'word':b.text(w),
              'substitutions':n1+n2,'rank3':list(rels),'indices':[left,right],'pair':list(pair),
              'no_old_isolator':no_old_isolator,'minimum_total':reduction.minimum_total,
              'whitehead_steps':list(reduction.steps),'phi':reduction.phi,
              'transformed_rank3':list(transformed),'killed_generators':list(letters),
              'remaining_quotient':quotient})
        summaries.append(local);print(json.dumps(local),flush=True)
    totals['distinct_pairs']=len(cache)
    payload={'schema':'aca124-rank3-primitive-pairs-v1','bounds':{'min_word_len':a.min_word_len,
      'max_word_len':a.max_word_len},'totals':totals,'summaries':summaries,'hits':hits,
      'trace_sha256':trace.hexdigest()}
    Path(a.out).write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
    print(json.dumps(totals))

if __name__=='__main__':main()
