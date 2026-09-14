import sys, random
sys.path.insert(0,"/home/user/ACSolverX/research/ac_cap_closure_20260912")
import capbfs as F, capbfs_reference as R

def kernel_children(r1,r2,cap,max_states=500000):
    b1,n1=F.str_to_bits(F._cyc_reduce_str(r1)); b2,n2=F.str_to_bits(F._cyc_reduce_str(r2))
    k1,k2=F.canon_pair_keys(b1,n1,b2,n2)
    cb,cl,ci,cc=F.build_connectors(max(0,(cap-2)//2))
    out=F._bfs_kernel(int(k1),int(k2),cap,max_states,cb,cl,ci,cc,False)
    nk1,nk2,par,count=out[0],out[1],out[4],out[10]
    return set("%s,%s"%(F.key_to_str(int(nk1[t])),F.key_to_str(int(nk2[t])))
               for t in range(1,count) if par[t]==0), out[16]

r1="xyxyxyxyxyxyxyXYXY"; r2="XYXYYXYXYXYXYXYXYX"
st=R.canon_pair(R.str_to_word(r1),R.str_to_word(r2))
print("start:", R.pair_to_strs(st))
for cap in range(16,21):
    if max(len(st[0]),len(st[1]))>cap: continue
    kf,bud=kernel_children(r1,r2,cap)
    kr=set("%s,%s"%(R.word_to_str(c[0]),R.word_to_str(c[1])) for c in R.neighbour_set(st,cap))
    miss=kr-kf; spur=kf-kr
    print("cap=%2d  kernel_children=%4d  ref_children=%4d  MISSED=%3d  SPURIOUS=%3d (budget=%s)"
          %(cap,len(kf),len(kr),len(miss),len(spur),bud))
    for m in sorted(miss, key=len)[:3]:
        print("      missed by capbfs.py:", m)
