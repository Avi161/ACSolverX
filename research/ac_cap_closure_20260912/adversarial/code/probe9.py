import sys
sys.path.insert(0,"/home/user/ACSolverX/research/ac_cap_closure_20260912")
import capbfs as F, capbfs_reference as R
def kernel_children(c1,c2,cap,max_states=400000):
    b1,n1=F.str_to_bits(c1); b2,n2=F.str_to_bits(c2)
    k1,k2=F.canon_pair_keys(b1,n1,b2,n2)
    cb,cl,ci,cc=F.build_connectors(max(0,(cap-2)//2))
    out=F._bfs_kernel(int(k1),int(k2),cap,max_states,cb,cl,ci,cc,False)
    nk1,nk2,par,count=out[0],out[1],out[4],out[10]
    return set("%s,%s"%(F.key_to_str(int(nk1[t])),F.key_to_str(int(nk2[t])))
               for t in range(1,count) if par[t]==0), out[16]
for r1,r2,cap in [("XyXXYYXXYxxyxyxY","xyXYXyyxyxYxYxxxY",17),
                  ("yyXXYXyXyXXyxyxyX","YYxYxyxxYYYXXXXYY",17)]:
    st=R.canon_pair(R.str_to_word(r1),R.str_to_word(r2))
    c1,c2=R.word_to_str(st[0]),R.word_to_str(st[1])
    kf,bud=kernel_children(c1,c2,cap)
    kr=set("%s,%s"%(R.word_to_str(x[0]),R.word_to_str(x[1])) for x in R.neighbour_set(st,cap))
    print("state %s , %s  cap=%d budget=%s"%(c1,c2,cap,bud))
    print("   kernel children %d, reference children %d, MISSED %d, SPURIOUS %d"%(len(kf),len(kr),len(kr-kf),len(kf-kr)))
    for m in sorted(kr-kf)[:5]: print("      MISSED:",m)
    for m in sorted(kf-kr)[:5]: print("      SPURIOUS:",m)
