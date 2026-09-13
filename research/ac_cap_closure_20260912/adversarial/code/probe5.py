import sys, random
sys.path.insert(0,"/home/user/ACSolverX/research/ac_cap_closure_20260912")
import capbfs as F, capbfs_reference as R

def fast_move(ri,rj,e,a,p):
    bi,ni=F.str_to_bits(ri); bj,nj=F.str_to_bits(rj)
    oj = bj if e==1 else F._inv_bits(bj,nj)
    acc,al = F._push(F._rotl(bi,ni,a), ni, F._rotl(oj,nj,p), nj)
    acc,al = F._cyc_reduce(acc,al)
    if al<1: return None
    return F.bits_to_str(int(acc)&((1<<(2*int(al)))-1), int(al))
def ref_move(ri,rj,e,a,p):
    wi=R.str_to_word(ri); wj=R.str_to_word(rj)
    oj = wj if e==1 else R.inv_word(wj)
    prod=R.cyc_reduce(R.free_reduce(R.rot(wi,a)+R.rot(oj,p)))
    return R.word_to_str(prod) if prod else None

def scan(r1,r2,cap,verbose=False):
    st=R.canon_pair(R.str_to_word(r1),R.str_to_word(r2))
    c1,c2=R.word_to_str(st[0]),R.word_to_str(st[1])
    if max(len(c1),len(c2))>cap or (cap-len(c1)-len(c2))>=0: return []
    out=[]
    for i in(0,1):
        ri,rj=(c1,c2) if i==0 else (c2,c1)
        for e in(1,-1):
            for a in range(len(ri)):
                for p in range(len(rj)):
                    h=ref_move(ri,rj,e,a,p); g=fast_move(ri,rj,e,a,p)
                    hok = h is not None and 1<=len(h)<=cap
                    gok = g is not None and 1<=len(g)<=cap
                    if (hok or gok) and g!=h:
                        out.append((cap,c1,c2,i,e,a,p,h,g))
    return out

# constructed example
u="xyxyxyxyxyxyxy"; s="XYXY"; t="XYXY"
r1=u+s; r2=t+"".join(ch.swapcase() for ch in reversed(u))
print("constructed r1=%s(%d) r2=%s(%d)"%(r1,len(r1),r2,len(r2)))
for cap in (18,19,20):
    d=scan(r1,r2,cap)
    print("  cap",cap,"divergences",len(d))
    for x in d[:3]: print("    ",x)

AL="xXyY"
rng=random.Random(99)
def rand_cycred(n):
    while True:
        w="".join(rng.choice(AL) for _ in range(n))
        if R.word_to_str(R.cyc_reduce(R.str_to_word(w)))==w: return w
tot=0; found=[]
for _ in range(6000):
    cap=rng.randint(17,24)
    n1=rng.randint(max(1,cap-4),cap); n2=rng.randint(max(1,cap-4),cap)
    d=scan(rand_cycred(n1),rand_cycred(n2),cap); tot+=1
    found.extend(d)
print("\nrandom canonical-state scan: %d states, %d diverging (i,e,a,p) moves"%(tot,len(found)))
for x in found[:6]:
    cap,c1,c2,i,e,a,p,h,g=x
    print("  cap=%d ri/rj=%s | %s  i=%d e=%d a=%d p=%d"%(cap,c1,c2,i,e,a,p))
    print("      ref R=%r len=%s   fast R=%r len=%s"%(h,h and len(h),g,g and len(g)))
