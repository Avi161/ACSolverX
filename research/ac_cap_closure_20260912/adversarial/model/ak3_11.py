import sys, time
sys.path.insert(0,'/home/user/ACSolverX/research/ac_cap_closure_20260912'); sys.path.insert(0,'.')
import capbfs as F, capbfs_reference as ref, indep
for cap in (12,):
    t=time.time(); R=ref.bfs('xxxYYYY','xyxYXY',cap,2_000_000,False); tr=time.time()-t
    Fx=F.bfs('xxxYYYY','xyxYXY',cap,2_000_000,stop_when_solved=False,collect_states=True)
    Rs=set(ref.state_key_strings(R)); Fs=set(F.state_key_strings(Fx))
    print("cap=%d ref states=%d (closed=%s, %.1fs)  fast states=%d (closed=%s)  sets equal=%s"%(
        cap,R["states"],R["closed"],tr,Fx["states"],Fx["closed"],Rs==Fs), flush=True)
    if Rs!=Fs:
        print("  ref-only:",sorted(Rs-Fs)[:5]," fast-only:",sorted(Fs-Rs)[:5])
