import sys, random
sys.path.insert(0,"/home/user/ACSolverX/research/ac_cap_closure_20260912")
import capbfs_reference as R
def brute(state,cap,max_u):
    out=set(); conns=R.connectors(max_u)
    for i in(0,1):
        ri,rj=state[i],state[1-i]
        for si in(1,-1):
            wi=ri if si==1 else R.inv_word(ri)
            for a in range(len(wi)):
                A=R.rot(wi,a)
                for e in(1,-1):
                    oj=rj if e==1 else R.inv_word(rj)
                    for p in range(len(oj)):
                        P=R.rot(oj,p)
                        for u in conns:
                            X=R.cyc_reduce(A+u+P+R.inv_word(u))
                            if 1<=len(X)<=cap: out.add(R.canon_pair(X,rj))
    return out
cases=[("xxxYYYY","xyxYXY",12),("xxxYYYY","xyxYXY",16),("xy","Xy",10),("x","y",12),
       ("xxyy","xyXY",10),("xxyXY","xyyxY",9),("xyxyxY","xxy",13),("xxxx","yyyy",12)]
for r1,r2,cap in cases:
    st=R.canon_pair(R.str_to_word(r1),R.str_to_word(r2))
    model=R.neighbour_set(st,cap)
    line=[]
    for mu in range(0,7):
        b=brute(st,cap,mu)
        line.append("|u|<=%d:%s%s"%(mu,"sub" if b<=model else "ESCAPES","=" if b==model else ""))
        if not b<=model:
            print("  ESCAPE at |u|<=%d:"%mu, sorted(R.pair_to_strs(x) for x in (b-model))[:3])
    print("%-9s %-9s cap=%2d model=%4d  %s"%(r1,r2,cap,len(model)," ".join(line)))
