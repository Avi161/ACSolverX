import sys, random
sys.path.insert(0,"/home/user/ACSolverX/research/ac_cap_closure_20260912")
import capbfs as F, capbfs_reference as R

def fast_children(c1,c2,cap):
    """Exactly what the njit kernel computes (same primitives), slack<0 => w=empty."""
    kids=set()
    for i in(0,1):
        ri,rj=(c1,c2) if i==0 else (c2,c1)
        bi,ni=F.str_to_bits(ri); bj,nj=F.str_to_bits(rj)
        rjkey=F._canon_key(bj,nj)
        for e in(0,1):
            oj = bj if e==0 else F._inv_bits(bj,nj)
            for a in range(ni):
                ab=F._rotl(bi,ni,a)
                for p in range(nj):
                    acc,al=F._push(ab,ni,F._rotl(oj,nj,p),nj)
                    acc,al=F._cyc_reduce(acc,al)
                    if al<1 or al>cap: continue
                    ck=F._canon_key(acc,al)
                    k1,k2=(int(ck),int(rjkey)) if ck<=rjkey else (int(rjkey),int(ck))
                    kids.add((F.key_to_str(k1),F.key_to_str(k2)))
    return kids

AL="xXyY"; rng=random.Random(31337)
def rc(n):
    while True:
        w="".join(rng.choice(AL) for _ in range(n))
        if R.word_to_str(R.cyc_reduce(R.str_to_word(w)))==w: return w

found=[]; nstates=0
for _ in range(60000):
    cap=rng.randint(17,24)
    n1=rng.randint(max(1,cap-3),cap); n2=rng.randint(max(1,cap-3),cap)
    st=R.canon_pair(R.str_to_word(rc(n1)),R.str_to_word(rc(n2)))
    c1,c2=R.word_to_str(st[0]),R.word_to_str(st[1])
    if max(len(c1),len(c2))>cap or cap-len(c1)-len(c2)>=0: continue
    nstates+=1
    kf=fast_children(c1,c2,cap)
    kr=set(tuple(R.word_to_str(w) for w in x) for x in R.neighbour_set(st,cap))
    if kf!=kr:
        found.append((cap,c1,c2,sorted(kr-kf),sorted(kf-kr)))
        if len(found)>=3: break
print("canonical states examined: %d ; with DIVERGENT CHILD SETS: %d"%(nstates,len(found)))
for cap,c1,c2,miss,spur in found:
    print("\ncap=%d  state = (%s , %s)"%(cap,c1,c2))
    print("   children reference finds, capbfs MISSES (%d): %s"%(len(miss),miss[:4]))
    print("   children capbfs invents, reference rejects (%d): %s"%(len(spur),spur[:4]))
