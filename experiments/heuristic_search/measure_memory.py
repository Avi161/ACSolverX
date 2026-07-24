"""How much memory ``hsolve`` needs, and therefore the largest budget it can be given.

The recommendation document twice said that ``greedy_search_h`` "will want more RAM than
``high_speedup`` mode -- size accordingly". That is not actionable: a user planning a 10^6-node run
needs a number, and whether that run is possible at all depends on it.

So this measures the real containers rather than RSS. The repo already learned not to trust
``ru_maxrss`` on macOS -- the memory compressor makes apparent bytes/state *fall* as states grow, so
RSS reports a number that gets rosier the worse the situation actually is. Instead the search loop
is re-stated here with the two structures that dominate (``parent``, the state dict, and ``pq``, the
heap) sized directly via ``sys.getsizeof`` over their keys and values.

One subtlety in the accounting: a ``parent`` value is ``(key_ref, move_tuple)`` where ``key_ref``
points at a bytes object already counted as a dict key, so only the tuple overhead is new. Counting
the key twice would inflate the estimate by roughly a third.

Measured on the hardest decidable rows (bins 6-7), which climb furthest and so give the honest
figure for the tier that matters rather than an optimistic one from easy rows.

    python3 -m experiments.heuristic_search.measure_memory
"""
import sys, heapq
sys.path.insert(0,"/Users/avigyapaudel/Documents/Obsidian Vault/surf/ACSolverX/.claude/worktrees/hsearch-hyper")
import numpy as np
from experiments.heuristic_search.hlab import bench66, N_FEAT
from experiments.heuristic_search.hsolve import RECOMMENDED
from experiments.heuristic_search.perbin import bin_of
from experiments.heuristic_search.hfast import (_pack,_arrs,_feats_nj,compile_config,
                                                expand_and_score_nj,_SEP)
from experiments.search.greedy_baseline import str_to_arr,reduce_relator_nj,canonical_pair_nj

def sized_run(r1,r2,b,mrl,cfg):
    """hsolve's loop, instrumented to size `parent` + `pq` at their peak."""
    su,sw,sd=compile_config(cfg)
    a1,a2=str_to_arr(r1),str_to_arr(r2)
    ca,cb=canonical_pair_nj(reduce_relator_nj(a1,True),reduce_relator_nj(a2,True))
    k0=_pack(ca,cb)
    f=np.empty(N_FEAT); ri=np.empty(2*mrl+2,dtype=np.bool_); rl=np.empty(2*mrl+2,dtype=np.int64)
    c0=np.frombuffer(k0.replace(_SEP,b""),dtype=np.uint8)
    _feats_nj(c0,0,len(ca),len(cb),ri,rl,f)
    pq=[((0,float(sum(sw[0,d]*f[d] for d in range(N_FEAT)))),0,k0)]
    parent={k0:None}; nodes=0
    while pq and nodes<b:
        _,dep,key=heapq.heappop(pq); nodes+=1
        i=key.index(0)
        if i==1 and len(key)-i-1==1: break
        p1,p2=_arrs(key)
        blob,offs,kl,si,sc,tt,kn,mv,cnt=expand_and_score_nj(p1,p2,mrl,True,su,sw)
        if cnt==0: continue
        raw=blob.tobytes(); nd=dep+1
        for c in range(cnt):
            o=int(offs[c]); kk=raw[o:o+int(kl[c])]
            if kk not in parent:
                parent[kk]=(key,(int(mv[c,0]),int(mv[c,1]),int(mv[c,2]),int(mv[c,3])))
                heapq.heappush(pq,((int(si[c]),float(sc[c])),nd,kk))
    # Size the real containers. sys.getsizeof on the dict gives the table; keys and
    # values must be added explicitly. Parent VALUES are (key_ref, move_tuple): the key
    # is a reference to a string already counted, so only the tuple overhead is new.
    b_parent=sys.getsizeof(parent)
    for kk,v in parent.items():
        b_parent+=sys.getsizeof(kk)
        if v is not None:
            b_parent+=sys.getsizeof(v)+sys.getsizeof(v[1])
    b_pq=sys.getsizeof(pq)+sum(sys.getsizeof(e)+sys.getsizeof(e[0]) for e in pq)
    return len(parent),b_parent+b_pq,nodes

rows=[r for r in bench66() if r['source']=='ladder' and bin_of(r['name']) in (6,7)][:5]
print(f"{'budget':>7} {'states':>9} {'bytes':>12} {'B/state':>9} {'B/node':>9}")
prev=None
for b in (250,500,1000):
    S=B=N=0
    for r in rows:
        s,by,n=sized_run(r['r1'],r['r2'],b,48,RECOMMENDED); S+=s; B+=by; N+=n
    print(f"{b:>7} {S:>9d} {B:>12,d} {B/max(S,1):>9.0f} {B/max(N,1):>9.0f}")
    prev=(S,B,N)
S,B,N=prev
bpn=B/N
print()
for gb in (12, 25, 50):
    print(f"  {gb:>2d} GB RAM  ->  max safe budget ~{int(gb*1e9*0.75/bpn):,} nodes"
          f"   (75% of RAM, {bpn:.0f} B/node)")
