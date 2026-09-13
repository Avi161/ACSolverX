import sys, itertools
sys.path.insert(0, '/home/user/ACSolverX/research/ac_cap_closure_20260912')
sys.path.insert(0, '.')
import capbfs_reference as ref
import indep

def ref_nb(st_strs, cap):
    s = (ref.str_to_word(st_strs[0]), ref.str_to_word(st_strs[1]))
    s = ref.canon_pair(*s)
    out = set()
    for _, ch in ref.neighbours(s, cap):
        out.add(indep.cpair(ref.word_to_str(ch[0]), ref.word_to_str(ch[1])))
    return out

STATES = [("x","y"), ("xy","xY"), ("xxy","yxY"), ("xyxY","xxyy"), ("xxxYY","xyxY"),
          ("xyXY","xyy"), ("xxyy","xyxy"), ("xyxyy","XYxy"), ("x","xy"), ("xy","xy"),
          ("xxxYYYY","xyxYXY")]
bad = 0
for cap in (5,6,7,8):
    for st in STATES:
        if max(len(indep.canon(st[0])), len(indep.canon(st[1]))) > cap:
            continue
        R = ref_nb(st, cap)
        prev = None
        sizes = []
        for L in range(0, 9):
            B = indep.brute_neighbours(st, cap, L)
            sizes.append(len(B))
        B = indep.brute_neighbours(st, cap, 8)
        status = "OK " if B == R else "MISMATCH"
        if B != R: bad += 1
        print("%s cap=%-2d %-18s ref=%-5d brute(L=8)=%-5d growth=%s" % (
            status, cap, "%s,%s"%st, len(R), len(B), sizes))
        if B != R:
            print("   brute-only:", sorted(B-R)[:8])
            print("   ref-only:  ", sorted(R-B)[:8])
print("mismatches:", bad)
