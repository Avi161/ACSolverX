import sys, random, collections
sys.path.insert(0,'/home/user/ACSolverX/research/ac_cap_closure_20260912'); sys.path.insert(0,'.')
import capbfs as F, indep
exec(open('overflow.py').read().split('random.seed')[0].split('import indep')[1])
random.seed(5)
def rc(n):
    while True:
        w=""
        for _ in range(n):
            c=random.choice("xXyY")
            while w and w[-1]==indep.INV[c]: c=random.choice("xXyY")
            w+=c
        if indep.cr(w)==w and len(w)==n: return w
# group by the length of the freely reduced concatenation (= alen after _push)
res=collections.Counter()
for trial in range(200000):
    n1=random.randint(10,20); n2=random.randint(10,20)
    ri,rj=rc(n1),rc(n2); a=random.randrange(n1); p=random.randrange(n2); e=random.choice([1,-1])
    A=ri[a:]+ri[:a]; o=rj if e==1 else indep.inv(rj); P=o[p:]+o[:p]
    fl=len(indep.fr(A+P))
    acc,alen=kernel_product(ri,rj,a,p,e)
    T=indep.cr(A+P)
    ok = (alen==len(T)) and (alen==0 or alen>31 or F.bits_to_str(acc&((1<<(2*alen))-1),alen)==T)
    res[(fl, 'ok' if ok else 'BAD')]+=1
for fl in sorted(set(k[0] for k in res)):
    print("free-reduced concat length %2d : ok=%6d bad=%6d" % (fl, res[(fl,'ok')], res[(fl,'BAD')]))
