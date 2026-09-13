import sys, random, collections
sys.path.insert(0, '/home/user/ACSolverX/research/ac_cap_closure_20260912')
sys.path.insert(0, '.')
import capbfs as F
import indep
exec(open('overflow.py').read().split('random.seed')[0].split('import indep')[1])
random.seed(3)
def rand_cycred(n):
    while True:
        w = ""
        for _ in range(n):
            ch = random.choice("xXyY")
            while w and w[-1]==indep.INV[ch]: ch = random.choice("xXyY")
            w += ch
        if indep.cr(w)==w and len(w)==n: return w
cap = 31
stats = collections.Counter(); ex = {}
for n1,n2 in [(17,17),(18,17),(20,18),(25,20),(31,31),(17,16)]:
  for trial in range(3000):
    ri, rj = rand_cycred(n1), rand_cycred(n2)
    a = random.randrange(n1); p = random.randrange(n2); e = random.choice([1,-1])
    acc, alen = kernel_product(ri, rj, a, p, e)
    T = truth(ri, rj, a, p, e)
    ka = 1 <= alen <= cap
    ta = 1 <= len(T) <= cap
    ks = F.bits_to_str(acc & ((1<<(2*alen))-1), alen) if (0 < alen <= 31) else None
    tag = 'ok'
    if ka and not ta: tag='SPURIOUS'
    elif ka and ta and ks != T: tag='WRONGWORD'
    elif ta and not ka: tag='MISSED'
    stats[(n1,n2,tag)] += 1
    if tag!='ok': ex.setdefault((n1,n2,tag),(ri,rj,a,p,e,ks,T))
for k in sorted(stats): print(k, stats[k])
print()
for k,v in sorted(ex.items()): print(k,v)
