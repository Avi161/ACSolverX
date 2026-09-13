import sys, random
sys.path.insert(0,"/home/user/ACSolverX/research/ac_cap_closure_20260912")
import numpy as np, capbfs as F, capbfs_reference as R

AL="xXyY"
def rand_cycred(rng,n):
    while True:
        w="".join(rng.choice(AL) for _ in range(n))
        if R.word_to_str(R.cyc_reduce(R.str_to_word(w)))==w: return w

def kernel_children(r1,r2,cap,max_states=400000):
    b1,n1=F.str_to_bits(r1); b2,n2=F.str_to_bits(r2)
    k1,k2=F.canon_pair_keys(b1,n1,b2,n2)
    cb,cl,ci,cc=F.build_connectors(max(0,(cap-2)//2))
    out=F._bfs_kernel(int(k1),int(k2),cap,max_states,cb,cl,ci,cc,False)
    nk1,nk2,par,count=out[0],out[1],out[4],out[10]
    kids=set()
    for t in range(1,count):
        if par[t]==0:
            kids.add((F.key_to_str(int(nk1[t])),F.key_to_str(int(nk2[t]))))
    return kids, out[16]

rng=random.Random(2026)
CONN={}
bad=[]
trials=0
for _ in range(4000):
    cap=rng.randint(17,20)
    n1=rng.randint(cap-3,cap); n2=rng.randint(cap-3,cap)
    if n1+n2<=32: continue
    r1=rand_cycred(rng,n1); r2=rand_cycred(rng,n2)
    trials+=1
    start=R.canon_pair(R.str_to_word(r1),R.str_to_word(r2))
    if max(len(start[0]),len(start[1]))>cap: continue
    kr=set(tuple(R.word_to_str(w) for w in c) for c in R.neighbour_set(start,cap))
    kf,bud=kernel_children(r1,r2,cap)
    if bud: continue
    if kf!=kr:
        bad.append((cap,r1,r2,R.pair_to_strs(start),sorted(kr-kf),sorted(kf-kr)))
        if len(bad)>=3: break
print("real-kernel trials:",trials," divergent states:",len(bad))
for cap,r1,r2,st,miss,spur in bad:
    print("cap=%d  start(canonical)=%s"%(cap,st))
    print("   from r1=%s r2=%s"%(r1,r2))
    print("   MISSED by capbfs (%d): %s"%(len(miss),miss[:4]))
    print("   SPURIOUS in capbfs (%d): %s"%(len(spur),spur[:4]))
