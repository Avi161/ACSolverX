import sys, random, collections
sys.path.insert(0,'/home/user/ACSolverX/research/ac_cap_closure_20260912'); sys.path.insert(0,'.')
import capbfs as F, indep
exec(open('overflow.py').read().split('random.seed')[0].split('import indep')[1])
random.seed(99)
def rc(n):
    while True:
        w=""
        for _ in range(n):
            c=random.choice("xXyY")
            while w and w[-1]==indep.INV[c]: c=random.choice("xXyY")
            w+=c
        if indep.cr(w)==w and len(w)==n: return w
st=collections.Counter(); ex={}
for trial in range(60000):
    cap=31
    n1=random.choice([17,18,16,19]); n2=33-n1 if random.random()<0.5 else 34-n1
    if n1>cap or n2>cap or n2<1: continue
    ri,rj=rc(n1),rc(n2); a=random.randrange(n1); p=random.randrange(n2); e=random.choice([1,-1])
    A=ri[a:]+ri[:a]; o=rj if e==1 else indep.inv(rj); P=o[p:]+o[:p]
    fl=len(indep.fr(A+P))
    if fl<33: st['(no overflow)']+=1; continue
    acc,alen=kernel_product(ri,rj,a,p,e)
    T=indep.cr(A+P)
    ka=1<=alen<=cap; ta=1<=len(T)<=cap
    ks=F.bits_to_str(acc&((1<<(2*alen))-1),alen) if 0<alen<=31 else None
    if ka and not ta: tag='SPURIOUS'
    elif ka and ta and ks!=T: tag='WRONGWORD'
    elif ta and not ka: tag='MISSED'
    elif ka and ta: tag='ok-accept'
    else: tag='ok-reject'
    st[tag]+=1; ex.setdefault(tag,(ri,rj,a,p,e,alen,ks,T))
for k in sorted(st): print("%-14s %d"%(k,st[k]))
print()
for k in ('SPURIOUS','WRONGWORD','MISSED'):
    if k in ex: print(k, ex[k])
