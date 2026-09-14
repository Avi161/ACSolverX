import sys
sys.path.insert(0,"/home/user/ACSolverX/research/ac_cap_closure_20260912")
import capbfs as F, capbfs_reference as R
print("budget-exhausted runs: fast vs reference")
for ms in (5,10,50,200,1000):
    fa=F.bfs("xxxYYYY","xyxYXY",12,ms,False,collect_states=True)
    sl=R.bfs("xxxYYYY","xyxYXY",12,ms,False)
    a=set(F.state_key_strings(fa)); b=set(R.state_key_strings(sl))
    print("  max_states=%-5d fast: states=%-5d frontier=%-5d popped=%-5d | ref: states=%-5d frontier=%-5d popped=%-5d | sets_equal=%s"
          %(ms,fa["states"],fa["frontier_size_at_stop"],fa["popped"],
            sl["states"],sl["frontier_size_at_stop"],sl["popped"], a==b))
