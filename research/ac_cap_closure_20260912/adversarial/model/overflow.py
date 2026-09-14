import sys, random
sys.path.insert(0, '/home/user/ACSolverX/research/ac_cap_closure_20260912')
sys.path.insert(0, '.')
import capbfs as F
import indep

def kernel_product(ri, rj, a, p, e):
    """Reproduce EXACTLY what _bfs_kernel computes for connector w = empty."""
    bi, ni = F.str_to_bits(ri)
    bj, nj = F.str_to_bits(rj)
    oj = bj if e == 1 else F._inv_bits(bj, nj)
    ab = F._rotl(bi, ni, a)
    pb = F._rotl(oj, nj, p)
    acc, alen = F._push(ab, ni, pb, nj)
    acc, alen = F._cyc_reduce(acc, alen)
    return acc, alen

def truth(ri, rj, a, p, e):
    A = ri[a:]+ri[:a]
    o = rj if e==1 else indep.inv(rj)
    P = o[p:]+o[:p]
    return indep.cr(A+P)

random.seed(7)
def rand_cycred(n):
    while True:
        w = ""
        for _ in range(n):
            ch = random.choice("xXyY")
            while w and w[-1]==indep.INV[ch]: ch = random.choice("xXyY")
            w += ch
        if indep.cr(w) == w and len(w)==n: return w

bad = []
for n1, n2 in [(16,16),(16,15),(20,20),(31,31),(17,16),(12,12),(15,15),(14,14)]:
    for trial in range(300):
        ri, rj = rand_cycred(n1), rand_cycred(n2)
        a = random.randrange(n1); p = random.randrange(n2); e = random.choice([1,-1])
        acc, alen = kernel_product(ri, rj, a, p, e)
        T = truth(ri, rj, a, p, e)
        if alen != len(T):
            bad.append((n1,n2,ri,rj,a,p,e,alen,len(T)))
            continue
        if alen <= 31:
            got = F.bits_to_str(acc & ((1<<(2*alen))-1), alen) if alen else ""
            if got != T:
                bad.append((n1,n2,ri,rj,a,p,e,got,T))
print("total bad:", len(bad))
for b in bad[:6]: print(b)
