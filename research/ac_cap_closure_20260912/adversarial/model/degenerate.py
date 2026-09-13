import sys
sys.path.insert(0,'/home/user/ACSolverX/research/ac_cap_closure_20260912'); sys.path.insert(0,'.')
import capbfs as F, capbfs_reference as ref, indep
for (a,b,cap) in [("x","x",6),("x","X",6),("xy","xy",6),("xy","YX",6),("xxy","xxy",7)]:
    try:
        f=F.bfs(a,b,cap,200000,stop_when_solved=False,collect_states=True)
        r=ref.bfs(a,b,cap,200000,stop_when_solved=False)
        same=set(F.state_key_strings(f))==set(ref.state_key_strings(r))
        # does the TRUE move set contain an empty-relator child?
        empt=False
        for i in (0,1):
            st=(indep.canon(a),indep.canon(b))
            ri,rj=st[i],st[1-i]
            for e in (1,-1):
                oj=rj if e==1 else indep.inv(rj)
                for u in indep.freely_reduced_words(3):
                    if len(indep.cr(ri+u+oj+indep.inv(u)))==0: empt=True
        print("%s,%s cap=%d : fast=%d ref=%d equal=%s  det=%s  true move to an EMPTY relator exists=%s"%(
            a,b,cap,f["states"],r["states"],same,
            (len([c for c in indep.canon(a) if c=='x'])-len([c for c in indep.canon(a) if c=='X']))*0 or 'n/a',empt))
    except Exception as exc:
        print("%s,%s cap=%d : EXCEPTION %r"%(a,b,cap,exc))
for cap in (32,0,-1):
    try: F.bfs("xy","xY",cap,10)
    except Exception as exc: print("cap=%s -> %r"%(cap,exc))
try: F.bfs("xX","xy",6,10)
except Exception as exc: print("empty after cyclic reduction -> %r"%(exc,))
try: ref.bfs("xX","xy",6,10)
except Exception as exc: print("reference, same -> %r"%(exc,))
