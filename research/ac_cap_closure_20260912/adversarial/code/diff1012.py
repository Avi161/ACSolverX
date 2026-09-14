import sys, random, time
sys.path.insert(0,"/home/user/ACSolverX/research/ac_cap_closure_20260912")
import capbfs as F, capbfs_reference as R

rng=random.Random(20260913)
def rand_trivial(maxlen, moves):
    st=R.TRIVIAL
    for _ in range(rng.randint(1,moves)):
        nb=[c for _,c in R.neighbours(st,maxlen) if len(c[0])<=maxlen and len(c[1])<=maxlen]
        st=rng.choice(nb)
    return R.word_to_str(st[0]), R.word_to_str(st[1])

bad=0; n=0; t0=time.time()
for trial in range(200):
    r1,r2=rand_trivial(rng.choice([6,7,8]), 7)
    for cap in (10,11,12):
        if max(len(r1),len(r2))>cap: continue
        if time.time()-t0>900: break
        try:
            fa=F.bfs(r1,r2,cap,400000,True,collect_states=True)
            sl=R.bfs(r1,r2,cap,400000,True)
        except Exception as e:
            print("EXC",r1,r2,cap,e); bad+=1; continue
        n+=1
        a=F.state_key_strings(fa); b=R.state_key_strings(sl)
        same = (a==b and fa["states"]==sl["states"] and fa["solved"]==sl["solved"]
                and fa["closed"]==sl["closed"] and fa["min_total_length_seen"]==sl["min_total_length_seen"])
        if not same:
            bad+=1
            print("MISMATCH %s %s cap=%d: states %d/%d solved %s/%s closed %s/%s mt %d/%d"
                  %(r1,r2,cap,fa["states"],sl["states"],fa["solved"],sl["solved"],
                    fa["closed"],sl["closed"],fa["min_total_length_seen"],sl["min_total_length_seen"]))
            A,B=set(a),set(b); print("   fast-only",sorted(A-B)[:3],"ref-only",sorted(B-A)[:3])
            if bad>3: break
    if bad>3 or time.time()-t0>900: break
print("compared %d (presentation,cap) pairs at caps 10-12 in %.0fs ; mismatches=%d"%(n,time.time()-t0,bad))
