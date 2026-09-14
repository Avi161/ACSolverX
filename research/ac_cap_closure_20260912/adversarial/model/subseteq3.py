import sys, itertools
sys.path.insert(0,'/home/user/ACSolverX/research/ac_cap_closure_20260912'); sys.path.insert(0,'.')
import indep
exec(open('subseteq2.py').read().split('random.seed')[0].split("import indep")[1])

# all canonical cyclic-word classes up to length 7
classes=set()
def gen(n):
    cur=[""]
    for _ in range(n):
        cur=[u+c for u in cur for c in "xXyY" if not(u and u[-1]==indep.INV[c])]
    return [w for w in cur if indep.cr(w)==w]
for n in range(1,8):
    for w in gen(n): classes.add(indep.canon(w))
classes=sorted(classes,key=lambda w:(len(w),w))
print("canonical classes of length <=7:", len(classes))

viol=0; tot=0; states=0
for cap in (4,5,6,7,8):
    C=[c for c in classes if len(c)<=cap]
    for ri in C:
        for rj in C:
            if (len(rj),rj)<(len(ri),ri): continue
            states+=1
            for (e,R),(fl,a,p,w) in scan(ri,rj,cap).items():
                tot+=1
                if fl>cap:
                    viol+=1
                    if viol<=10: print("CAP VIOLATION cap=%d %s %s e=%d R=%s fl=%d"%(cap,ri,rj,e,R,fl))
print("states scanned=%d  outcomes=%d  not cap-realisable=%d"%(states,tot,viol))
