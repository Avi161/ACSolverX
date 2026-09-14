import sys, random
sys.path.insert(0,"/home/user/ACSolverX/research/ac_cap_closure_20260912")
import capbfs as F, capbfs_reference as R

def fast_move(ri,rj,e,a,p):
    bi,ni=F.str_to_bits(ri); bj,nj=F.str_to_bits(rj)
    oj = bj if e==1 else F._inv_bits(bj,nj)
    acc,al=F._push(F._rotl(bi,ni,a),ni,F._rotl(oj,nj,p),nj)
    acc,al=F._cyc_reduce(acc,al)
    return None if al<1 else F.bits_to_str(int(acc)&((1<<(2*int(al)))-1),int(al))
def ref_move(ri,rj,e,a,p):
    wi=R.str_to_word(ri); wj=R.str_to_word(rj)
    oj=wj if e==1 else R.inv_word(wj)
    prod=R.cyc_reduce(R.free_reduce(R.rot(wi,a)+R.rot(oj,p)))
    return R.word_to_str(prod) if prod else None

def scan(c1,c2,cap):
    n=0
    for i in(0,1):
        ri,rj=(c1,c2) if i==0 else (c2,c1)
        for e in(1,-1):
            for a in range(len(ri)):
                for p in range(len(rj)):
                    h=ref_move(ri,rj,e,a,p); g=fast_move(ri,rj,e,a,p)
                    hok=h is not None and 1<=len(h)<=cap
                    gok=g is not None and 1<=len(g)<=cap
                    if (hok or gok) and g!=h: n+=1
    return n

def kernel_children(c1,c2,cap,max_states=300000):
    b1,n1=F.str_to_bits(c1); b2,n2=F.str_to_bits(c2)
    k1,k2=F.canon_pair_keys(b1,n1,b2,n2)
    cb,cl,ci,cc=F.build_connectors(max(0,(cap-2)//2))
    out=F._bfs_kernel(int(k1),int(k2),cap,max_states,cb,cl,ci,cc,False)
    nk1,nk2,par,count=out[0],out[1],out[4],out[10]
    return set("%s,%s"%(F.key_to_str(int(nk1[t])),F.key_to_str(int(nk2[t])))
               for t in range(1,count) if par[t]==0)

AL="xXyY"; rng=random.Random(4242)
def rand_cycred(n):
    while True:
        w="".join(rng.choice(AL) for _ in range(n))
        if R.word_to_str(R.cyc_reduce(R.str_to_word(w)))==w: return w

nstates=0; ndiv=0; nchilddiff=0; examples=[]
for _ in range(40000):
    cap=rng.randint(17,26)
    n1=rng.randint(max(1,cap-4),cap); n2=rng.randint(max(1,cap-4),cap)
    st=R.canon_pair(R.str_to_word(rand_cycred(n1)),R.str_to_word(rand_cycred(n2)))
    c1,c2=R.word_to_str(st[0]),R.word_to_str(st[1])
    if max(len(c1),len(c2))>cap or cap-len(c1)-len(c2)>=0: continue
    nstates+=1
    d=scan(c1,c2,cap)
    if not d: continue
    ndiv+=1
    kf=kernel_children(c1,c2,cap)
    kr=set("%s,%s"%(R.word_to_str(x[0]),R.word_to_str(x[1])) for x in R.neighbour_set(st,cap))
    if kf!=kr:
        nchilddiff+=1
        if len(examples)<4: examples.append((cap,c1,c2,sorted(kr-kf),sorted(kf-kr)))
    if nchilddiff>=4: break
print("states scanned %d ; states with diverging moves %d ; states with DIFFERENT CHILD SETS %d"%(nstates,ndiv,nchilddiff))
for cap,c1,c2,miss,spur in examples:
    print("\ncap=%d  state = %s , %s"%(cap,c1,c2))
    print("   reference children not found by capbfs (%d): %s"%(len(miss),miss[:3]))
    print("   capbfs children not in reference   (%d): %s"%(len(spur),spur[:3]))
