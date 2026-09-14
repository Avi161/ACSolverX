import sys
sys.path.insert(0,'/home/user/ACSolverX/research/ac_cap_closure_20260912'); sys.path.insert(0,'.')
import capbfs as F, indep
r1,r2 = 'xxYXYXYXYXyyxYxyy','xxYXYYXYYXyyxYxyy'
res = F.bfs(r1,r2,17,max_states=12,stop_when_solved=False,collect_states=True)
print(res["states"], res["budget_exhausted"], res["closed"])
for s in res["_state_keys"]: print("   ", s, [len(t) for t in s.split(",")])
