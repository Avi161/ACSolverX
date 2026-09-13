import sys
sys.path.insert(0,'/home/user/ACSolverX/research/ac_cap_closure_20260912'); sys.path.insert(0,'.')
import capbfs as F, capbfs_reference as ref, indep
exec(open('overflow.py').read().split('random.seed')[0].split('import indep')[1])

r = F.bfs('xxxYYYY','xyxYXY',17,max_states=300000,stop_when_solved=False,collect_states=True)
cands=[s.split(",") for s in r["_state_keys"]]
cands=[c for c in cands if len(c[0])+len(c[1])>=33]
print("example cap-17 states with |r1|+|r2|>=33:", cands[:3])
cap=17
for st in cands[:3]:
    ri_,rj_=st
    missed=[]
    for i in (0,1):
        A,B=(ri_,rj_) if i==0 else (rj_,ri_)
        for e in (1,-1):
            for a in range(len(A)):
                for p in range(len(B)):
                    acc,alen=kernel_product(A,B,a,p,e)
                    o=B if e==1 else indep.inv(B)
                    T=indep.cr(A[a:]+A[:a]+o[p:]+o[:p])
                    k_ok = 1<=alen<=cap
                    t_ok = 1<=len(T)<=cap
                    if k_ok!=t_ok or (k_ok and t_ok and F.bits_to_str(acc&((1<<(2*alen))-1),alen)!=T):
                        missed.append((i,e,a,p,alen,T))
    # reference neighbours of this state
    rst=ref.canon_pair(ref.str_to_word(ri_),ref.str_to_word(rj_))
    nb=ref.neighbour_set(rst,cap)
    print("state %s,%s : reference neighbours=%d ; kernel/truth mismatching (i,e,a,p) triples=%d"
          % (ri_,rj_,len(nb),len(missed)))
    for m in missed[:3]:
        print("    i=%d e=%d a=%d p=%d : kernel len=%d (rejected, >cap)  truth=%s (len %d, ACCEPTED)"%(m[0],m[1],m[2],m[3],m[4],m[5],len(m[5])))
