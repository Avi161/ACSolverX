import sys, random, json
sys.path.insert(0,"/home/user/ACSolverX/research/ac_cap_closure_20260912")
import capbfs as F, capbfs_reference as R
exec(open("/tmp/claude-0/-home-user-ACSolverX/bb9b8f6b-3f21-5a5d-83e9-f34cbf1c43ae/scratchpad/probe5.py").read().split("# constructed")[0].split("import capbfs as F")[1].replace(", capbfs_reference as R",""))

r1="xyxyxyxyxyxyxyXYXY"; r2="XYXYYXYXYXYXYXYXYX"
res=F.bfs(r1,r2,18,5_000_000,stop_when_solved=False,collect_states=True)
print("capbfs cap=18: states=%d closed=%s budget=%s solved=%s min_total=%d"
      %(res["states"],res["closed"],res["budget_exhausted"],res["solved"],res["min_total_length_seen"]))
print("  discovered set:", res["_state_keys"])
st=R.canon_pair(R.str_to_word(r1),R.str_to_word(r2))
kr=sorted("%s,%s"%(R.word_to_str(c[0]),R.word_to_str(c[1])) for c in R.neighbour_set(st,18))
print("  reference neighbours of the start (%d):"%len(kr))
for k in kr: print("     ",k, "  IN-FAST-SET" if k in set(res["_state_keys"]) else "  *** MISSING FROM CLOSED COMPONENT ***")
