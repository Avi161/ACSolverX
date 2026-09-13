import sys, time
sys.path.insert(0, '/home/user/ACSolverX/research/ac_cap_closure_20260912')
sys.path.insert(0, '.')
import capbfs_reference as ref
import capbfs
import indep

STARTS = [("x","y"), ("xy","xY"), ("xxy","yxY"), ("xyxY","xxyy"), ("xyXY","xyy"), ("xy","xy")]
for cap in (5,6,7):
    for r1, r2 in STARTS:
        if max(len(indep.cr(r1)), len(indep.cr(r2))) > cap: continue
        t=time.time()
        B = indep.brute_bfs(r1, r2, cap, L=8)
        tb=time.time()-t
        R = ref.bfs(r1, r2, cap, max_states=500000, stop_when_solved=False)
        Rs = indep.recanon_set(tuple(ref.word_to_str(w) for w in s) for s in R["_states_set"])
        F = capbfs.bfs(r1, r2, cap, max_states=500000, stop_when_solved=False, collect_states=True)
        Fs = indep.recanon_set(tuple(s.split(",")) for s in F["_state_keys"])
        ok = (B==Rs==Fs)
        print("%s cap=%d start=%s,%s  brute=%d ref=%d fast=%d  (closed ref=%s fast=%s) %.1fs" % (
            "OK " if ok else "MISMATCH", cap, r1, r2, len(B), len(Rs), len(Fs),
            R["closed"], F["closed"], tb))
        if not ok:
            print("  brute-only:", sorted(B-Rs)[:6], " ref-only:", sorted(Rs-B)[:6],
                  " fast-only:", sorted(Fs-Rs)[:6], " ref\\fast:", sorted(Rs-Fs)[:6])
