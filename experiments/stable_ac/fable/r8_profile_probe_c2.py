"""R8 block D, complexity-2 case: is the census profile SUFFICIENT?  (new file)

Enumerates every presentation with the complexity-2 profile (3 generators, 3 relators,
each generator occurring exactly 3 times, hence total length 9) that presents the trivial
group, modulo the full census symmetry group (permute generators, invert generators,
rotate/invert relators, permute relators), and compares the count with what the census
actually realizes.  Result: 79 admissible vs at most 17 surfaces x 4 spanning trees = 68
realizable, so at least 11 profile-admissible trivial-group presentations are the
tree-collapse of NO complexity-2 contractible cellular fake surface -- the profile is
necessary but not sufficient.  Runtime ~2 min.  See R8_FAKE_SURFACE_COMPLEXITY.md 3.4.
"""

import sys, itertools, json
from collections import defaultdict
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r8_complexity_profile import occurrences, is_trivial_group, TARGETS

GENS='abc'; LET='aAbBcC'
def reduced_cyclic(L):
    out=[]
    for t in itertools.product(LET,repeat=L):
        w=''.join(t)
        if L>1:
            if any(x==y.swapcase() for x,y in zip(w,w[1:])): continue
            if w[-1]==w[0].swapcase(): continue
        out.append(w)
    return out
def occvec(w):
    c=occurrences([w]); return tuple(c.get(g,0) for g in GENS)
def rotkey(w):
    c=[]
    for var in (w, ''.join(x.swapcase() for x in reversed(w))):
        c.extend(var[i:]+var[:i] for i in range(len(var)))
    return min(c)
bylen={}
for L in range(1,8):
    d=defaultdict(list)
    for w in reduced_cyclic(L): d[occvec(w)].append(rotkey(w))
    bylen[L]={k:sorted(set(v)) for k,v in d.items()}
def canon_full(words, gens=GENS):
    best=None
    for perm in itertools.permutations(gens):
        for flips in itertools.product([0,1],repeat=len(gens)):
            table={}
            for src,dst,fl in zip(gens,perm,flips):
                table[src]= dst.upper() if fl else dst
                table[src.upper()] = dst if fl else dst.upper()
            k=tuple(sorted(rotkey(''.join(table[c] for c in w)) for w in words))
            if best is None or k<best: best=k
    return best
TARGET=(3,3,3)
parts=[p for p in itertools.combinations_with_replacement(range(1,8),3) if sum(p)==9]
raw=set()
for p in parts:
    l1,l2,l3=p
    for v1 in bylen[l1]:
        for v2 in bylen[l2]:
            v3=tuple(TARGET[i]-v1[i]-v2[i] for i in range(3))
            if min(v3)<0 or v3 not in bylen[l3]: continue
            for w1 in bylen[l1][v1]:
                for w2 in bylen[l2][v2]:
                    for w3 in bylen[l3][v3]:
                        raw.add(tuple(sorted((w1,w2,w3))))
print('raw rot/inv-canonical triples:',len(raw),flush=True)
cands={canon_full(list(t)) for t in raw}
print('profile-admissible canonical classes (before triviality):',len(cands),flush=True)
triv=[k for k in cands if is_trivial_group(list(k),cap=20000)[0]]
print('...presenting the TRIVIAL group:',len(triv),flush=True)
census=[t for t in json.load(open(TARGETS))['targets'] if t['complexity']==2]
ck={canon_full(t['relators']) for t in census}
print('census rows at complexity 2:',len(census),' canonical classes:',len(ck))
print('census subset of profile-admissible-trivial:',ck<=set(triv))
extra=sorted(set(triv)-ck)
print('profile-admissible+trivial but NOT realized in census:',len(extra))
for k in extra[:15]: print('   ',list(k))
