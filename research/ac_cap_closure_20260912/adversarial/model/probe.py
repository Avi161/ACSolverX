import sys
sys.path.insert(0,'/home/user/ACSolverX/research/ac_cap_closure_20260912'); sys.path.insert(0,'.')
import capbfs as F, indep
from numba import njit

@njit(cache=False)
def probe(ri_b, ri_n, rj_b, rj_n, a, p, e, cap):
    """exactly the kernel's inner body for w = empty"""
    if e == 0:
        oj = rj_b
    else:
        oj = F._inv_bits(rj_b, rj_n)
    a_bits = F._rotl(ri_b, ri_n, a)
    pre_acc = a_bits
    pre_len = ri_n
    p_bits = F._rotl(oj, rj_n, p)
    acc, alen = F._push(pre_acc, pre_len, p_bits, rj_n)
    acc, alen = F._cyc_reduce(acc, alen)
    if alen < 1 or alen > cap:
        return -1, alen, 0
    ck = F._canon_key(acc, alen)
    return ck, alen, 1

r1,r2 = 'xxYXYXYXYXyyxYxyy','xxYXYYXYYXyyxYxyy'
b1,n1=F.str_to_bits(r1); b2,n2=F.str_to_bits(r2)
ck,alen,acc = probe(b1,n1,b2,n2,0,0,0,17)
print("njit-inlined probe  (i=0,e=+1,a=0,p=0):  accepted=%d alen=%d key=%s" %
      (acc, alen, F.key_to_str(int(ck)) if ck>0 else "-"))
# same thing via python-level calls of the same njit primitives
oj=b2
ab=F._rotl(b1,n1,0); pb=F._rotl(oj,n2,0)
a2,l2=F._push(ab,n1,pb,n2); a3,l3=F._cyc_reduce(a2,l2)
print("python-level calls :                     alen=%d" % l3)
print("truth              : len=%d" % len(indep.cr(r1+r2)))
