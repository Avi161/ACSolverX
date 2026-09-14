import sys
sys.path.insert(0,'/home/user/ACSolverX/research/ac_cap_closure_20260912'); sys.path.insert(0,'.')
import capbfs as F, indep
r1,r2 = 'xxYXYXYXYXyyxYxyy','xxYXYYXYYXyyxYxyy'
b1,n1=F.str_to_bits(r1); b2,n2=F.str_to_bits(r2)
k1,k2=F.canon_pair_keys(b1,n1,b2,n2)
cb,cl,ci,cc=F.build_connectors(max(0,(17-2)//2))
out=F._bfs_kernel(int(k1),int(k2),17,12,cb,cl,ci,cc,False)
nk1,nk2,nl1,nl2,par,mvi,mve,mva,mvp,mvw=out[:10]
print("count",out[10],"popped",out[12])
for t in range(out[10]):
    print(t,"par",par[t],"i",mvi[t],"e",mve[t],"a",mva[t],"p",mvp[t],"w",mvw[t],
          F.key_to_str(int(nk1[t]))+","+F.key_to_str(int(nk2[t])))
print("conn count array:", cc[:5], "n connectors used for start: slack", 17-17-17)
