import csv, sys, collections
import pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from experiments.equivalence_classes.lib.words import canon_rel, apply_hom, inv, cyc_reduce
from experiments.search.heuristic_1k import NIELSEN

def syllables(w):
    out = []
    for c in w:
        g = c.lower(); e = 1 if c.islower() else -1
        if out and out[-1][0] == g: out[-1][1] += e
        else: out.append([g, e])
    if len(out) > 1 and out[0][0] == out[-1][0]:
        out[0][1] += out[-1][1]; out.pop()
    return [tuple(s) for s in out]

def exps(w):
    return (w.count('x')-w.count('X'), w.count('y')-w.count('Y'))

def whitehead_descent(w, limit=200):
    """strictly length-decreasing Nielsen descent on the cyclic word; returns final canonical word and steps"""
    cur = canon_rel(w); steps = 0
    while steps < limit:
        best = None
        for t in NIELSEN:
            c = canon_rel(apply_hom(cur, t))
            if len(c) < len(cur) and (best is None or len(c) < len(best)): best = c
        if best is None: break
        cur = best; steps += 1
    return cur, steps

def power_conj(w):
    """return (stable gen, k, base gen, p, q) if cyclic word is g^k h^p g^-k h^q  (one generator has exactly two syllables of opposite exponent)"""
    s = syllables(w)
    if len(s) != 4: return None
    for off in (0, 1):
        g, k = s[off]; h, p = s[off+1]; g2, k2 = s[(off+2) % 4]; h2, q = s[(off+3) % 4]
        if k + k2 == 0:
            return (g, k, h, p, q)
    return None

rows = list(csv.DictReader(open(str(pathlib.Path(__file__).resolve().parents[2] / 'results/heuristic_search/ac19_final_policy_full_1k/unsolved.csv'))))
print(len(rows))
cats = collections.Counter(); prim = 0; examples = collections.defaultdict(list)
for r in rows:
    r1, r2 = r['r1'], r['r2']
    ws = [r1, r2]
    p = [whitehead_descent(w) for w in ws]
    is_prim = [len(c) == 1 for c, _ in p]
    if any(is_prim): prim += 1
    pcs = [power_conj(w) for w in ws]
    nsyl = [len(syllables(w)) for w in ws]
    key = ('prim' if any(is_prim) else 'noprim', 'pc' if any(pcs) else 'nopc', tuple(sorted(nsyl)))
    cats[key] += 1
    if len(examples[key]) < 4: examples[key].append((r['name'], r1, r2, pcs, exps(r1), exps(r2)))
print('rows with a primitive relator:', prim)
for k, v in sorted(cats.items(), key=lambda kv: -kv[1]):
    print(v, k)
    for e in examples[k]: print('   ', e)
# distribution of pc shapes
shapes = collections.Counter()
for r in rows:
    for w in (r['r1'], r['r2']):
        pc = power_conj(w)
        if pc: shapes[(abs(pc[1]), pc[3], pc[4])] += 1
print('pc shapes (|k|, p, q):', shapes.most_common(30))
