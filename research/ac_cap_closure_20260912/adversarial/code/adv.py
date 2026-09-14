import sys
sys.path.insert(0,"/home/user/ACSolverX/research/ac_cap_closure_20260912")
import capbfs as F, capbfs_reference as R
cases = [
 ("x","y",4), ("x","y",1), ("x","x",4), ("x","X",4), ("xy","yx",6),
 ("xyXY","xyXY",6), ("xyXY","YXyx",6), ("xxxx","yyyy",4), ("xxxx","yyyy",8),
 ("xyxYXY","YXYxyx",6), ("xY","Yx",5), ("x","xy",3),
]
for r1,r2,cap in cases:
    try:
        fa=F.bfs(r1,r2,cap,200000,True,collect_states=True)
    except Exception as ex:
        fa=("EXC",type(ex).__name__,str(ex))
    try:
        sl=R.bfs(r1,r2,cap,200000,True)
    except Exception as ex:
        sl=("EXC",type(ex).__name__,str(ex))
    if isinstance(fa,tuple) or isinstance(sl,tuple):
        print("%-10s %-10s cap=%d  fast=%s  ref=%s"%(r1,r2,cap,fa,sl)); continue
    ok = F.state_key_strings(fa)==R.state_key_strings(sl)
    print("%-10s %-10s cap=%2d  fast:%6d closed=%-5s solved=%-5s | ref:%6d closed=%-5s solved=%-5s | sets_equal=%s"
          %(r1,r2,cap,fa["states"],fa["closed"],fa["solved"],sl["states"],sl["closed"],sl["solved"],ok))
    if not ok:
        A=set(F.state_key_strings(fa)); B=set(R.state_key_strings(sl))
        print("    fast-only:",sorted(A-B)[:5]," ref-only:",sorted(B-A)[:5])
# degenerate max_states
for ms in (0,1,2):
    try:
        r=F.bfs("xyxYXY","xxxYYYY",12,ms,True); print("max_states=%d -> states=%d closed=%s budget=%s"%(ms,r["states"],r["closed"],r["budget_exhausted"]))
    except Exception as e:
        print("max_states=%d -> %s: %s"%(ms,type(e).__name__,e))
