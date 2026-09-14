import sys, json
sys.path.insert(0,'/home/user/ACSolverX/research/ac_cap_closure_20260912'); sys.path.insert(0,'.')
import capbfs as F, capbfs_reference as ref, indep
r1,r2 = 'xxYXYXYXYXyyxYxyy','xxYXYYXYYXyyxYxyy'
print("start:", r1, r2, "lengths", len(r1), len(r2), "cap 17")
fast = F.bfs(r1,r2,17,max_states=100000,stop_when_solved=False)
print("FAST   :", json.dumps({k:fast[k] for k in ('initial','cap','closed','solved','states','budget_exhausted','min_total_length_seen')}))
st = ref.canon_pair(ref.str_to_word(r1), ref.str_to_word(r2))
nb = ref.neighbour_set(st, 17)
print("REF    : neighbours of the start =", sorted(ref.word_to_str(a)+","+ref.word_to_str(b) for a,b in nb))
# independent brute force, arbitrary conjugator, no rotations, |u|<=3
bn = indep.brute_neighbours((r1,r2), 17, 3)
print("INDEP  : brute neighbours (|u|<=3)  =", sorted(a+","+b for a,b in bn))
