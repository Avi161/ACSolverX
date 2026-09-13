import sys, random, collections
sys.path.insert(0,'/home/user/ACSolverX/research/ac_cap_closure_20260912'); sys.path.insert(0,'.')
import capbfs as F, capbfs_reference as ref, indep
from numba import njit

@njit(cache=False)
def kernel_children(b0,m0,b1,m1,k0,k1,cap):
    """kernel inner loops, w = empty only (the slack<0 regime)."""
    outa = np.empty(4*32*32, np.int64); outb = np.empty(4*32*32, np.int64); n=0
    for i in range(2):
        if i==0:
            ri_b=b0; ri_n=m0; rj_b=b1; rj_n=m1; rj_key=k1
        else:
            ri_b=b1; ri_n=m1; rj_b=b0; rj_n=m0; rj_key=k0
        for e in range(2):
            if e==0: oj=rj_b
            else: oj=F._inv_bits(rj_b,rj_n)
            for a in range(ri_n):
                a_bits=F._rotl(ri_b,ri_n,a)
                for p in range(rj_n):
                    p_bits=F._rotl(oj,rj_n,p)
                    acc,alen=F._push(a_bits,ri_n,p_bits,rj_n)
                    acc,alen=F._cyc_reduce(acc,alen)
                    if alen<1 or alen>cap: continue
                    ck=F._canon_key(acc,alen)
                    if ck>rj_key: outa[n]=rj_key; outb[n]=ck
                    else: outa[n]=ck; outb[n]=rj_key
                    n+=1
    return outa[:n], outb[:n]
import numpy as np

random.seed(2024)
def rc(n):
    while True:
        w=""
        for _ in range(n):
            c=random.choice("xXyY")
            while w and w[-1]==indep.INV[c]: c=random.choice("xXyY")
            w+=c
        if indep.cr(w)==w and len(w)==n: return w

def fast_children(r1,r2,cap):
    b0,m0=F.str_to_bits(r1); b1,m1=F.str_to_bits(r2)
    k0,k1=F.canon_pair_keys(b0,m0,b1,m1)
    # kernel works on the canonical relators
    s0,s1=F.key_to_str(int(k0)),F.key_to_str(int(k1))
    b0,m0=F.str_to_bits(s0); b1,m1=F.str_to_bits(s1)
    A,B=kernel_children(b0,m0,b1,m1,int(k0),int(k1),cap)
    return {indep.cpair(F.key_to_str(int(a)),F.key_to_str(int(b))) for a,b in zip(A,B)}

def ref_children(r1,r2,cap):
    st=ref.canon_pair(ref.str_to_word(r1),ref.str_to_word(r2))
    return {indep.cpair(ref.word_to_str(a),ref.word_to_str(b)) for a,b in ref.neighbour_set(st,cap)}

bad=0; tested=0; overflowing=0
for trial in range(400):
    cap=random.choice([17,18,20,24,28,31])
    n1=random.randint(max(1,cap-6),cap); n2=random.randint(max(1,cap-6),cap)
    if n1+n2<33: continue
    r1,r2=rc(n1),rc(n2)
    if n1+n2>cap:   # slack<0 regime -> w empty, matches the probe
        tested+=1
        FF=fast_children(r1,r2,cap); RR=ref_children(r1,r2,cap)
        if FF!=RR:
            bad+=1
            if bad<=5:
                print("DIFF cap=%d %s %s  fast=%d ref=%d  ref-only=%s fast-only=%s"%(
                    cap,r1,r2,len(FF),len(RR),sorted(RR-FF)[:3],sorted(FF-RR)[:3]))
print("states tested (|r1|+|r2|>cap, sum>=33): %d ; child-set differences: %d"%(tested,bad))
