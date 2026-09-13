import sys, time, resource
sys.path.insert(0,"/home/user/ACSolverX/research/ac_cap_closure_20260912")
import capbfs as F
F.bfs("xy","Xy",8,1000,True)   # warm
for cap in (12,13,14,15):
    w0=time.perf_counter()
    r=F.bfs("xxxYYYY","xyxYXY",cap,5_000_000,stop_when_solved=True)
    w1=time.perf_counter()
    print("cap=%2d states=%8d closed=%s internal=%.2fs wall(incl connectors)=%.2fs  internal n/s=%.0f  wall n/s=%.0f  peakRSS=%dMB"
          %(cap,r["states"],r["closed"],r["seconds"],w1-w0,r["nodes_per_second"],r["popped"]/(w1-w0),
            resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024))
