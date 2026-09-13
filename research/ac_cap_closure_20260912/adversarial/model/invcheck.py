"""Does taking the OTHER representative of the cyclic word (r_i^-1) add children?
The model enumerates only rotations of r_i (plus e = +-1); this checks that the
set built from r_i^-1 with arbitrary conjugators is the same."""
import sys
sys.path.insert(0,'/home/user/ACSolverX/research/ac_cap_closure_20260912'); sys.path.insert(0,'.')
import capbfs_reference as ref, indep

def brute(state, cap, L, use_inverse):
    us = indep.freely_reduced_words(L)
    r=(indep.canon(state[0]), indep.canon(state[1]))
    out=set()
    for i in (0,1):
        ri,rj=r[i],r[1-i]
        if use_inverse: ri=indep.inv(ri)
        for e in (1,-1):
            oj=rj if e==1 else indep.inv(rj)
            for u in us:
                R=indep.cr(ri+u+oj+indep.inv(u))
                if 1<=len(R)<=cap: out.add(indep.cpair(R,rj))
    return out
def refnb(a,b,cap):
    st=ref.canon_pair(ref.str_to_word(a),ref.str_to_word(b))
    return {indep.cpair(ref.word_to_str(u),ref.word_to_str(v)) for u,v in ref.neighbour_set(st,cap)}
for (a,b,cap) in [("xxy","yxY",8),("xyxY","xxyy",9),("xxxYY","xyxY",10),("xy","xY",10),
                  ("xxxYYYY","xyxYXY",14),("xyyXYxY","xyyXYxYY",9)]:
    P=brute((a,b),cap,6,False); Q=brute((a,b),cap,6,True); R=refnb(a,b,cap)
    print("%-9s|%-9s cap=%-3d  r_i-only=%-5d r_i^-1-only=%-5d model=%-5d  all equal=%s"%(
        a,b,cap,len(P),len(Q),len(R),P==Q==R))
