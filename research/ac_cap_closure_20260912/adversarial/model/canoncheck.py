import sys, collections
sys.path.insert(0,'/home/user/ACSolverX/research/ac_cap_closure_20260912'); sys.path.insert(0,'.')
import capbfs as F, capbfs_reference as ref, indep

def gen(n):
    cur=[""]
    for _ in range(n):
        cur=[u+c for u in cur for c in "xXyY" if not(u and u[-1]==indep.INV[c])]
    return [w for w in cur if indep.cr(w)==w]

allw=[w for n in range(1,10) for w in gen(n)]
print("cyclically reduced words of length 1..9:", len(allw))
m_ref={}; m_fast={}; m_ind={}; bad=[]
for w in allw:
    rw=ref.word_to_str(ref.canon_rel(ref.str_to_word(w)))
    b,n=F.str_to_bits(w); fw=F.key_to_str(int(F._canon_key(b,n)))
    iw=indep.canon(w)
    m_ref.setdefault(rw,set()).add(iw); m_ind.setdefault(iw,set()).add(rw)
    m_fast.setdefault(fw,set()).add(iw)
    # invariance: canon must be a rotation of w or of w^-1, same length
    cls={ (u[k:]+u[:k]) for u in (w, indep.inv(w)) for k in range(len(w)) }
    if rw not in cls or fw not in cls or iw not in cls: bad.append(("not-in-class",w,rw,fw,iw))
    if rw!=fw: bad.append(("ref!=fast",w,rw,fw))
    # idempotence
    if ref.word_to_str(ref.canon_rel(ref.str_to_word(rw)))!=rw: bad.append(("not idempotent",w,rw))
print("ref classes:",len(m_ref)," fast classes:",len(m_fast)," indep classes:",len(m_ind))
print("ref->indep well defined (each ref key maps to 1 indep key):",all(len(v)==1 for v in m_ref.values()))
print("indep->ref well defined:",all(len(v)==1 for v in m_ind.values()))
print("fast->indep well defined:",all(len(v)==1 for v in m_fast.values()))
print("anomalies:",len(bad), bad[:5])
# pair canon symmetry
import random
random.seed(4)
sym=0
for _ in range(3000):
    a=random.choice(allw); b=random.choice(allw)
    p1=ref.canon_pair(ref.str_to_word(a),ref.str_to_word(b))
    p2=ref.canon_pair(ref.str_to_word(b),ref.str_to_word(a))
    if p1!=p2: sym+=1
    ba,na=F.str_to_bits(a); bb,nb=F.str_to_bits(b)
    k1=F.canon_pair_keys(ba,na,bb,nb); k2=F.canon_pair_keys(bb,nb,ba,na)
    if k1!=k2: sym+=1
    if tuple(ref.word_to_str(t) for t in p1)!=tuple(F.key_to_str(int(t)) for t in k1): sym+=1
print("pair canon asymmetries / ref-fast pair disagreements:",sym)
