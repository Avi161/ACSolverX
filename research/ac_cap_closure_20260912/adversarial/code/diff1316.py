import sys, random, time
sys.path.insert(0,"/home/user/ACSolverX/research/ac_cap_closure_20260912")
import capbfs as F, capbfs_reference as R
rng=random.Random(20260913)
AL="xXyY"
def cyc(s): return R.word_to_str(R.cyc_reduce(R.str_to_word(s)))==s
def rc(n):
    while True:
        w="".join(rng.choice(AL) for _ in range(n))
        if cyc(w): return w
n=0; bad=0; t0=time.time()
while time.time()-t0 < 800:
    cap=rng.randint(13,16)
    n1=rng.randint(cap-3,cap); n2=rng.randint(cap-3,cap)
    r1,r2=rc(n1),rc(n2)
    try:
        fa=F.bfs(r1,r2,cap,4000,stop_when_solved=False,collect_states=True)
    except ValueError: continue
    if not fa["closed"] or fa["states"]<3: continue
    sl=R.bfs(r1,r2,cap,4000,stop_when_solved=False)
    n+=1
    a=F.state_key_strings(fa); b=R.state_key_strings(sl)
    if not (a==b and fa["states"]==sl["states"] and fa["closed"]==sl["closed"]
            and fa["solved"]==sl["solved"] and fa["min_total_length_seen"]==sl["min_total_length_seen"]):
        bad+=1
        print("MISMATCH",r1,r2,cap,fa["states"],sl["states"],fa["closed"],sl["closed"])
        A,B=set(a),set(b); print("  fast-only",sorted(A-B)[:3],"ref-only",sorted(B-A)[:3])
        if bad>3: break
print("caps 13-16, closed components fully compared fast vs reference: %d cases, mismatches=%d"%(n,bad))
