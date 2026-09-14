"""Large-connector regime: caps 10..14 with short relators, where the model's
|w| bound is doing real work.  Compare against arbitrary conjugators |u| <= L."""
import sys, time
sys.path.insert(0,'/home/user/ACSolverX/research/ac_cap_closure_20260912'); sys.path.insert(0,'.')
import capbfs_reference as ref, indep

def ref_nb(a,b,cap):
    st=ref.canon_pair(ref.str_to_word(a),ref.str_to_word(b))
    return {indep.cpair(ref.word_to_str(u),ref.word_to_str(v)) for u,v in ref.neighbour_set(st,cap)}

cases=[("x","y",10),("x","y",12),("xy","xY",12),("xxy","yxY",11),("xyxY","xxyy",12),
       ("x","y",14),("xxY","xy",13),("xyXY","x",13),("xxxYYYY","xyxYXY",14)]
for a,b,cap in cases:
    R=ref_nb(a,b,cap)
    budget=(cap-len(indep.canon(a))-len(indep.canon(b)))//2
    prev=None; sizes=[]
    L=0
    while True:
        t=time.time(); B=indep.brute_neighbours((a,b),cap,L); sizes.append(len(B))
        if prev is not None and len(B)==prev and L>=budget+max(len(indep.canon(a)),len(indep.canon(b)))+1:
            break
        prev=len(B); L+=1
        if L>9: break
    print("%s cap=%-3d %-8s|%-8s model-bound|w|<=%d  ref=%-6d brute(L=%d)=%-6d growth=%s"%(
        "OK " if B==R else "MISMATCH", cap,a,b,budget,len(R),L,len(B),sizes))
    if B!=R:
        print("   brute-only:",sorted(B-R)[:5]); print("   ref-only:",sorted(R-B)[:5])
