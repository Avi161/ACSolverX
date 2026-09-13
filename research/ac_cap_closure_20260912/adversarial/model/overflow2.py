import sys, random, collections
sys.path.insert(0, '/home/user/ACSolverX/research/ac_cap_closure_20260912')
sys.path.insert(0, '.')
import capbfs as F
import indep
exec(open('overflow.py').read().split('random.seed')[0].split('import indep')[1])
random.seed(11)
def rand_cycred(n):
    while True:
        w = ""
        for _ in range(n):
            ch = random.choice("xXyY")
            while w and w[-1]==indep.INV[ch]: ch = random.choice("xXyY")
            w += ch
        if indep.cr(w)==w and len(w)==n: return w
stats = collections.Counter()
examples = {}
for n in (14,15,16,17,18,20,24,31):
    cap = n
    for trial in range(4000):
        ri, rj = rand_cycred(n), rand_cycred(n)
        a = random.randrange(n); p = random.randrange(n); e = random.choice([1,-1])
        acc, alen = kernel_product(ri, rj, a, p, e)
        T = truth(ri, rj, a, p, e)
        kernel_accepts = 1 <= alen <= cap
        true_accepts = 1 <= len(T) <= cap
        kstr = F.bits_to_str(acc & ((1<<(2*alen))-1), alen) if (0 < alen <= 31) else None
        if kernel_accepts and (not true_accepts):
            stats[(n,'SPURIOUS')] += 1
            examples.setdefault((n,'SPURIOUS'), (ri,rj,a,p,e,kstr,T))
        elif kernel_accepts and true_accepts and kstr != T:
            stats[(n,'WRONGWORD')] += 1
            examples.setdefault((n,'WRONGWORD'), (ri,rj,a,p,e,kstr,T))
        elif (not kernel_accepts) and true_accepts:
            stats[(n,'MISSED')] += 1
            examples.setdefault((n,'MISSED'), (ri,rj,a,p,e,kstr,T))
        else:
            stats[(n,'ok')] += 1
for k in sorted(stats): print(k, stats[k])
print()
for k,v in sorted(examples.items()): print(k, v)
