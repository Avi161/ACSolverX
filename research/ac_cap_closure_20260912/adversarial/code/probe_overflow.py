import sys, random
sys.path.insert(0,"/home/user/ACSolverX/research/ac_cap_closure_20260912")
import capbfs as F, capbfs_reference as R

def fast_move(ri, rj, e, a, p, w):
    """Replicate the capbfs kernel inner computation exactly, using its njit primitives."""
    bi, ni = F.str_to_bits(ri); bj, nj = F.str_to_bits(rj); bw, nw = F.str_to_bits(w)
    oj = bj if e==1 else F._inv_bits(bj, nj)
    a_bits = F._rotl(bi, ni, a)
    if nw==0:
        pre, pl = a_bits, ni
    else:
        pre, pl = F._push(a_bits, ni, bw, nw)
    p_bits = F._rotl(oj, nj, p)
    acc, al = F._push(pre, pl, p_bits, nj)
    if nw:
        wi_b,_ = F.str_to_bits(F._cyc_reduce_str("")) if False else (0,0)
        iw = "".join(c.swapcase() for c in reversed(w))
        b2,n2 = F.str_to_bits(iw)
        acc, al = F._push(acc, al, b2, n2)
    acc, al = F._cyc_reduce(acc, al)
    if al < 1: return None
    return F.bits_to_str(int(acc) & ((1<<(2*int(al)))-1), int(al))

def ref_move(ri, rj, e, a, p, w):
    wi = R.str_to_word(ri); wj = R.str_to_word(rj); ww = R.str_to_word(w)
    oj = wj if e==1 else R.inv_word(wj)
    prod = R.cyc_reduce(R.free_reduce(R.rot(wi,a)+ww+R.rot(oj,p)+R.inv_word(ww)))
    if not prod: return None
    return R.word_to_str(prod)

rng = random.Random(7)
AL = "xXyY"
def rand_cycred(n):
    while True:
        w = "".join(rng.choice(AL) for _ in range(n))
        if R.word_to_str(R.cyc_reduce(R.str_to_word(w))) == w:
            return w

bad = []
tested = 0
for trial in range(200000):
    n1 = rng.randint(14, 20); n2 = rng.randint(14, 20)
    r1 = rand_cycred(n1); r2 = rand_cycred(n2)
    a = rng.randrange(n1); p = rng.randrange(n2); e = rng.choice([1,-1])
    tested += 1
    g = fast_move(r1, r2, e, a, p, "")
    h = ref_move(r1, r2, e, a, p, "")
    if g != h:
        bad.append((r1, r2, e, a, p, g, h))
        if len(bad) >= 5: break
print("tested", tested, "mismatches found:", len(bad))
for b in bad:
    r1,r2,e,a,p,g,h = b
    print("  r1=%s r2=%s e=%d a=%d p=%d" % (r1,r2,e,a,p))
    print("    fast -> %r (len %s)" % (g, len(g) if g else None))
    print("    ref  -> %r (len %s)" % (h, len(h) if h else None))
