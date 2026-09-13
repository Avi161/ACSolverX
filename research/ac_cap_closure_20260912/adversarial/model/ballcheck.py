"""Is the returned state set really order-independent (a ball)?  Shuffle the
move enumeration and the frontier order in the reference and compare."""
import sys, random
sys.path.insert(0,'/home/user/ACSolverX/research/ac_cap_closure_20260912'); sys.path.insert(0,'.')
import capbfs_reference as ref, capbfs as F, test_capbfs as T
orig = ref.neighbours
rng = random.Random(0)
def shuffled(state, cap):
    out = list(orig(state, cap)); rng.shuffle(out); return out
bad=0; n=0
for r1,r2 in T.PANEL[:12]:
    for cap in range(max(len(r1),len(r2)), 10):
        base=ref.bfs(r1,r2,cap,200000,True)
        ref.neighbours=shuffled
        try: shuf=ref.bfs(r1,r2,cap,200000,True)
        finally: ref.neighbours=orig
        fast=F.bfs(r1,r2,cap,200000,True,collect_states=True)
        a=set(ref.state_key_strings(base)); b=set(ref.state_key_strings(shuf)); c=set(F.state_key_strings(fast))
        n+=1
        if not(a==b==c) or base["solved"]!=shuf["solved"]:
            bad+=1; print("ORDER-DEPENDENT %s/%s cap=%d: %d vs %d vs %d"%(r1,r2,cap,len(a),len(b),len(c)))
        if base["solved"]: break
print("checked %d (presentation,cap) runs; order-dependence or engine disagreement: %d"%(n,bad))
