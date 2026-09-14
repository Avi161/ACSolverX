import sys
sys.path.insert(0,"/home/user/ACSolverX/research/ac_cap_closure_20260912")
import numpy as np, capbfs as F, capbfs_reference as R

r1="YXyXXyXXXXYXXyyx"; r2="XXYxyXXyyxYXyyyxYY"; cap=18
b1,n1=F.str_to_bits(r1); b2,n2=F.str_to_bits(r2)
k1,k2=F.canon_pair_keys(b1,n1,b2,n2)
start=R.canon_pair(R.str_to_word(r1),R.str_to_word(r2))
print("start canon:", R.pair_to_strs(start), "keys", int(k1),int(k2))

w_max=max(0,(cap-2)//2)
cb,cl,ci,cc=F.build_connectors(w_max)
out=F._bfs_kernel(int(k1),int(k2),cap,200000,cb,cl,ci,cc,False)
nk1,nk2,nl1,nl2,par = out[0],out[1],out[2],out[3],out[4]
count=out[10]; budget=out[16]
print("kernel: count=%d budget_exhausted=%s"%(count,budget))
kids_fast=set()
for t in range(1,count):
    if par[t]==0:
        kids_fast.add((F.key_to_str(int(nk1[t])), F.key_to_str(int(nk2[t]))))
kids_ref=set(tuple(R.word_to_str(w) for w in c) for c in R.neighbour_set(start,cap))
print("children(start): fast=%d ref=%d"%(len(kids_fast),len(kids_ref)))
missing = kids_ref - kids_fast
spurious = kids_fast - kids_ref
print("MISSING from fast (%d):"%len(missing))
for m in sorted(missing)[:10]: print("   ",m)
print("SPURIOUS in fast (%d):"%len(spurious))
for m in sorted(spurious)[:10]: print("   ",m)
