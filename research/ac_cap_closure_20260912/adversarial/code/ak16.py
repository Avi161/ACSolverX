import sys, resource
sys.path.insert(0,"/home/user/ACSolverX/research/ac_cap_closure_20260912")
import capbfs as F
for cap in (16,):
    r=F.bfs("xxxYYYY","xyxYXY",cap,5_000_000,stop_when_solved=True)
    print("cap=%d states=%d closed=%s solved=%s budget=%s frontier=%d min_total=%d %.1fs %.0f n/s peakRSS=%dMB"
      %(cap,r["states"],r["closed"],r["solved"],r["budget_exhausted"],r["frontier_size_at_stop"],
        r["min_total_length_seen"],r["seconds"],r["nodes_per_second"],
        resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024))
