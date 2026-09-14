import sys
sys.path.insert(0,"/home/user/ACSolverX/research/ac_cap_closure_20260912")
import capbfs as F
# independent monotonicity check across the whole admissible cap range, AK(3)
prev=None
for cap in range(9,15):
    r=F.bfs("xxxYYYY","xyxYXY",cap,5_000_000,stop_when_solved=False,collect_states=True)
    s=set(F.state_key_strings(r))
    assert r["closed"] and not r["budget_exhausted"]
    assert len(s)==r["states"]
    ok = prev is None or prev<=s
    print("cap=%2d states=%7d closed=%s  component(cap-1) subset: %s"%(cap,r["states"],r["closed"],ok if prev is not None else "-"))
    assert ok
    prev=s
