import sys, random
sys.path.insert(0,"/home/user/ACSolverX/research/ac_cap_closure_20260912")
exec(open("/tmp/claude-0/-home-user-ACSolverX/bb9b8f6b-3f21-5a5d-83e9-f34cbf1c43ae/scratchpad/probe_overflow.py").read().split("rng = random.Random(7)")[0])
import capbfs as F, capbfs_reference as R
import random
rng = random.Random(11)
AL="xXyY"
def rand_cycred(n):
    while True:
        w="".join(rng.choice(AL) for _ in range(n))
        if R.word_to_str(R.cyc_reduce(R.str_to_word(w)))==w: return w

hits=[]
for trial in range(400000):
    cap = rng.randint(17,20)
    n1 = rng.randint(cap-2,cap); n2 = rng.randint(cap-2,cap)
    if n1+n2 <= 32: continue
    r1=rand_cycred(n1); r2=rand_cycred(n2)
    for e in (1,-1):
        for a in range(n1):
            for p in range(n2):
                h = ref_move(r1,r2,e,a,p,"")
                if h is None or len(h)>cap: continue
                g = fast_move(r1,r2,e,a,p,"")
                if g!=h:
                    hits.append((cap,r1,r2,e,a,p,g,h))
    if hits: break
print("hits:",len(hits))
for cap,r1,r2,e,a,p,g,h in hits[:6]:
    print("cap=%d r1=%s(%d) r2=%s(%d) e=%d a=%d p=%d"%(cap,r1,n1,r2,n2,e,a,p))
    print("   REF accepted R = %r  (len %d)"%(h,len(h)))
    print("   FAST         R = %r  (len %s)"%(g, len(g) if g else None))
