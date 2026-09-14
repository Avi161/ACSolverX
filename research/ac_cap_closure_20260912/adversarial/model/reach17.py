import sys
sys.path.insert(0,'/home/user/ACSolverX/research/ac_cap_closure_20260912')
import capbfs
r = capbfs.bfs('xxxYYYY','xyxYXY',17,max_states=300000,stop_when_solved=False,collect_states=True)
sums = [len(a)+len(b) for a,b in (s.split(",") for s in r["_state_keys"])]
print("states:", r["states"], "budget_exhausted:", r["budget_exhausted"])
print("max |r1|+|r2| seen:", max(sums), " #states with sum>=33:", sum(1 for s in sums if s>=33))
