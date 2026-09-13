"""Correct criterion: a model move (state -> {R, rj}) is realisable by elementary
AC moves that respect the cap iff some (a',p',w') with |rj|+2|w'| <= cap gives a
freely reduced AC2 product of length <= cap whose cyclic reduction is R."""
import sys, random
sys.path.insert(0,'/home/user/ACSolverX/research/ac_cap_closure_20260912'); sys.path.insert(0,'.')
import indep

def conns(maxw):
    if maxw<0: return [""]
    out=[""]; cur=[""]
    for _ in range(maxw):
        nxt=[u+c for u in cur for c in "xXyY" if not(u and u[-1]==indep.INV[c])]
        out+=nxt; cur=nxt
    return out

def scan(ri,rj,cap):
    """-> dict (e, canon R) -> min freely reduced product length"""
    W=conns((cap-len(ri)-len(rj))//2)
    best={}
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
                        k=(e,indep.canon(R))
                        if k not in best or len(pr)<best[k][0]: best[k]=(len(pr),a,p,w)
    return best

random.seed(17)
def rc(n):
    while True:
        w=""
        for _ in range(n):
            c=random.choice("xXyY")
            while w and w[-1]==indep.INV[c]: c=random.choice("xXyY")
            w+=c
        if indep.cr(w)==w and len(w)==n: return w

viol=0; tot=0
for trial in range(400):
    cap=random.choice([4,5,6,7,8,9,10,11,12])
    n1=random.randint(1,cap); n2=random.randint(1,cap)
    ri,rj=indep.canon(rc(n1)),indep.canon(rc(n2))
    for (e,R),(fl,a,p,w) in scan(ri,rj,cap).items():
        tot+=1
        if fl>cap:
            viol+=1
            if viol<=10:
                print("CAP VIOLATION cap=%d ri=%s rj=%s e=%d -> R=%s (|R|=%d) but the shortest"
                      " AC2 product word has length %d  (a=%d p=%d w=%r)"%(cap,ri,rj,e,R,len(R),fl,a,p,w))
print("distinct (e,R) model outcomes checked: %d ; not realisable within the cap by any rotation/connector: %d"%(tot,viol))
