"""Extra arms on the frozen L-stratified slice (scale10k companion)."""
from __future__ import annotations
import json, os, sys, time
from datetime import datetime, timezone
_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(os.path.isdir(os.path.join(_d, s)) for s in ("experiments","data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)
from experiments.heuristic_search.core.hcompact import greedy_search_hcompact
from experiments.heuristic_search.core.hsolve import RECOMMENDED

ROOT=_d
OUT=os.path.join(ROOT,"results","heuristic_search","scale10k","extra_arms_b10k.jsonl")
SLICE=os.path.join(ROOT,"results","heuristic_search","scale10k","slice_l_stratified.json")
STATE=os.path.join(ROOT,"results","heuristic_search","scale10k","state.json")
BUDGET=10_000
ARMS={
  "s8": {"segments":[{"upto":None,"w":{"L":1.0,"S":8.0}}]},
  "s16": {"segments":[{"upto":None,"w":{"L":1.0,"S":16.0}}]},
  "s28": {"segments":[{"upto":None,"w":{"L":1.0,"S":28.0}}]},
  "mk8": {"segments":[{"upto":None,"w":{"L":1.0,"MK":8.0}}]},
  "k8": {"segments":[{"upto":None,"w":{"L":1.0,"K":8.0}}]},
  "s20_k2": {"segments":[{"upto":None,"w":{"L":1.0,"S":20.0,"K":2.53}}]},
  "s20_neg_xy": {"segments":[{"upto":None,"w":{"L":1.0,"S":20.0,"xyimb":-3.0}}]},
}

def rem():
    if not os.path.exists(STATE):
        return 9999
    return (datetime.fromisoformat(json.load(open(STATE))["wall_end"])-datetime.now(timezone.utc)).total_seconds()

def done():
    s=set()
    if not os.path.exists(OUT): return s
    for l in open(OUT):
        r=json.loads(l)
        s.add((r["arm"], r["idx"]))
    return s

def main():
    rows=json.load(open(SLICE))["rows"]
    seen=done()
    print(f"[extra] {len(rows)} rows x {len(ARMS)} arms; remain={rem()/3600:.2f}h", flush=True)
    greedy_search_hcompact("X","Y",50,max_relator_length=48,config=ARMS["s16"],reserve_states=5000)
    n=0
    for rec in rows:
        for arm,cfg in ARMS.items():
            if rem()<180: return
            if (arm, rec["idx"]) in seen: continue
            t0=time.perf_counter()
            res=greedy_search_hcompact(rec["r1"],rec["r2"],BUDGET,max_relator_length=48,config=cfg,reserve_states=120*BUDGET)
            dt=time.perf_counter()-t0
            row={"arm":arm,"idx":rec["idx"],"L":rec["L"],"solved":bool(res["solved"]),
                 "solved_at":res["nodes_explored"] if res["solved"] else None,
                 "nodes":res["nodes_explored"],"secs":round(dt,3),
                 "pops_s":round(res["nodes_explored"]/max(dt,1e-9),1),
                 "budget":BUDGET,"cap":48,"ts":datetime.now(timezone.utc).isoformat()}
            for c in (1000,2000,5000,10000):
                row[f"solved_le_{c}"]=bool(row["solved_at"] is not None and row["solved_at"]<=c)
            os.makedirs(os.path.dirname(OUT),exist_ok=True)
            with open(OUT,"a") as f:
                f.write(json.dumps(row)+"\n"); f.flush(); os.fsync(f.fileno())
            seen.add((arm,rec["idx"])); n+=1
            if n%10==0:
                print(f"  +{n} {arm}/idx={rec['idx']} solved={row['solved']}", flush=True)
    print(f"[extra] done new={n}", flush=True)
if __name__=="__main__":
    main()
