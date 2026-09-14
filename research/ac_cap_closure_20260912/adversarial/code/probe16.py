import sys, random
sys.path.insert(0,"/home/user/ACSolverX/research/ac_cap_closure_20260912")
import capbfs as F, capbfs_reference as R
def fast_move(ri,rj,e,a,p):
    bi,ni=F.str_to_bits(ri); bj,nj=F.str_to_bits(rj)
    oj=bj if e==1 else F._inv_bits(bj,nj)
    acc,al=F._push(F._rotl(bi,ni,a),ni,F._rotl(oj,nj,p),nj)
    acc,al=F._cyc_reduce(acc,al)
    return None if al<1 else F.bits_to_str(int(acc)&((1<<(2*int(al)))-1),int(al))
def ref_move(ri,rj,e,a,p):
    wi=R.str_to_word(ri); wj=R.str_to_word(rj)
    oj=wj if e==1 else R.inv_word(wj)
    prod=R.cyc_reduce(R.free_reduce(R.rot(wi,a)+R.rot(oj,p)))
    return R.word_to_str(prod) if prod else None
AL="xXyY"; rng=random.Random(5)
def rc(n):
    while True:
        w="".join(rng.choice(AL) for _ in range(n))
        if R.word_to_str(R.cyc_reduce(R.str_to_word(w)))==w: return w
for target_sum,cap in [(32,16),(31,16),(30,16),(33,17),(34,17)]:
    bad=0; tot=0; ex=None
    for _ in range(1500):
        n1=target_sum//2; n2=target_sum-n1
        if n1>cap or n2>cap: continue
        c1,c2=rc(n1),rc(n2)
        for i in(0,1):
            ri,rj=(c1,c2) if i==0 else (c2,c1)
            for e in(1,-1):
                for a in range(len(ri)):
                    for p in range(len(rj)):
                        h=ref_move(ri,rj,e,a,p); g=fast_move(ri,rj,e,a,p)
                        hok=h is not None and 1<=len(h)<=cap
                        gok=g is not None and 1<=len(g)<=cap
                        tot+=1
                        if (hok or gok) and g!=h:
                            bad+=1
                            if ex is None: ex=(c1,c2,i,e,a,p,h,g)
        if bad: break
    print("|ri|+|rj|=%d cap=%d : %d/%d diverging accepted-or-accepted moves"%(target_sum,cap,bad,tot))
    if ex: print("    ", ex)
