import sys, random
sys.path.insert(0,"/home/user/ACSolverX/research/ac_cap_closure_20260912")
import capbfs as F, capbfs_reference as R
def fast_move(ri,rj,e,a,p):
    bi,ni=F.str_to_bits(ri); bj,nj=F.str_to_bits(rj)
    oj=bj if e==1 else F._inv_bits(bj,nj)
    acc,al=F._push(F._rotl(bi,ni,a),ni,F._rotl(oj,nj,p),nj)
    acc,al=F._cyc_reduce(acc,al)
    if al<1: return None
    return F.bits_to_str(int(acc)&((1<<(2*int(al)))-1),int(al)), int(F._canon_key(acc,al))
def ref_move(ri,rj,e,a,p):
    wi=R.str_to_word(ri); wj=R.str_to_word(rj)
    oj=wj if e==1 else R.inv_word(wj)
    prod=R.cyc_reduce(R.free_reduce(R.rot(wi,a)+R.rot(oj,p)))
    if not prod: return None
    c=R.canon_rel(prod)
    b,n=F.str_to_bits(R.word_to_str(c))
    return R.word_to_str(prod), (1<<(2*n))|b
AL="xXyY"; rng=random.Random(777)
def cyc(s): return R.word_to_str(R.cyc_reduce(R.str_to_word(s)))==s
def inv(s): return "".join(c.swapcase() for c in reversed(s))
# DELIBERATELY heavy cyclic reduction: r1 = u+s, r2 = t+inv(u), |u| = m
bad=0; tot=0; built=0
for _ in range(400000):
    m=rng.randint(8,15); ls=16-m; lt=16-m
    if ls<1 or lt<1: continue
    u="".join(rng.choice(AL) for _ in range(m))
    s="".join(rng.choice(AL) for _ in range(ls))
    t="".join(rng.choice(AL) for _ in range(lt))
    r1,r2=u+s, t+inv(u)
    if len(r1)!=16 or len(r2)!=16: continue
    if not cyc(r1) or not cyc(r2): continue
    built+=1
    for e in(1,-1):
        for a in range(16):
            for p in range(16):
                h=ref_move(r1,r2,e,a,p); g=fast_move(r1,r2,e,a,p)
                hok=h is not None and 1<=len(h[0])<=16
                gok=g is not None and 1<=len(g[0])<=16
                tot+=1
                if hok!=gok or (hok and (h[0]!=g[0] or h[1]!=g[1])):
                    bad+=1
                    if bad<4: print("DIVERGE r1=%s r2=%s e=%d a=%d p=%d ref=%s fast=%s"%(r1,r2,e,a,p,h,g))
    if built>=400: break
print("cap-16 boundary stress: %d constructed 16/16 pairs, %d moves compared (word AND canonical key), divergences=%d"%(built,tot,bad))
