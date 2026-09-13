"""For every move the model allows, is there an elementary-AC realisation whose
every intermediate *word* stays within the cap?  The only step that can break
the cap is the AC2 product itself and the conjugated donor, so we check:
  exists (a',p',w') with  |w'| <= floor((c-|ri|-|rj|)/2)   [donor conj: |rj|+2|w'| <= c-|ri|]
  and  |free_reduce(rot_a'(ri) . w' . rot_p'(rj^e) . w'^-1)| == |R|  (<= c)
  and  cyc_reduce(that) == R  (same cyclic word)
for every R that the model produces."""
import sys, random, itertools
sys.path.insert(0,'/home/user/ACSolverX/research/ac_cap_closure_20260912'); sys.path.insert(0,'.')
import indep

def conns(maxw):
    if maxw<0: return [""]
    out=[""]; cur=[""]
    for _ in range(maxw):
        nxt=[u+c for u in cur for c in "xXyY" if not(u and u[-1]==indep.INV[c])]
        out+=nxt; cur=nxt
    return out

def model_moves(ri,rj,cap):
    """yield (e,a,p,w,R,freelen)"""
    W=conns((cap-len(ri)-len(rj))//2)
    for e in (1,-1):
        oj=rj if e==1 else indep.inv(rj)
        for a in range(len(ri)):
            A=ri[a:]+ri[:a]
            for p in range(len(oj)):
                P=oj[p:]+oj[:p]
                for w in W:
                    pr=indep.fr(A+w+P+indep.inv(w))
                    R=indep.cr(pr)
                    if 1<=len(R)<=cap:
                        yield (e,a,p,w,R,len(pr))

random.seed(1)
def rc(n):
    while True:
        w=""
        for _ in range(n):
            c=random.choice("xXyY")
            while w and w[-1]==indep.INV[c]: c=random.choice("xXyY")
            w+=c
        if indep.cr(w)==w and len(w)==n: return w

fails=0; checked=0; moves=0
for trial in range(60):
    cap=random.choice([5,6,7,8,9,10])
    n1=random.randint(1,cap); n2=random.randint(1,cap)
    ri,rj=indep.canon(rc(n1)),indep.canon(rc(n2))
    # collect, per (e,R), whether some realisation has free length == |R|
    best={}
    for (e,a,p,w,R,fl) in model_moves(ri,rj,cap):
        moves+=1
        keyR=(e,indep.canon(R))
        prev=best.get(keyR)
        if prev is None or fl<prev[0]: best[keyR]=(fl,len(R),a,p,w)
    for (e,Rc),(fl,lR,a,p,w) in best.items():
        checked+=1
        if fl!=lR or lR>cap or len(rj)+2*len(w)>cap:
            fails+=1
            print("FAIL cap=%d ri=%s rj=%s e=%d R=%s |R|=%d best free-reduced product length=%d (a=%d p=%d w=%r)"%(
                cap,ri,rj,e,Rc,lR,fl,a,p,w))
print("states=60 moves enumerated=%d distinct (e,R) checked=%d  failures=%d"%(moves,checked,fails))
