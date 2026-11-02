"""Independent replay of the solved paths in a results/elliot_*/<bench>__<algo>.jsonl file.

Usage (a Python with both acx and ACSolverES's ac_final_paper importable):
    NUMBA_CACHE_DIR=/tmp/nc python -B benchmark/elliot/verify_paths.py results/elliot_10k/ms640__auto_dual.jsonl out.json

Checks per step: S-moves are seam-cancelling S-move children (own code and acx enumerate_moves/s_step);
auto_cov and single_cov steps stay in the Aut(F2) orbit (acx.aut.orbit_key) and rebuild from the logged map
or subword; triple complete_cov steps are produced by ACSolverES's own generator and leave the orbit.
Per row: path[0] is the start's canonical form, the end is trivial, len(moves) == path_length, abs det 1.
"""
import sys, json, collections, random
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parents[2]))
from acx.core.words import Presentation, canonical_rels, canonical_word, parse, reduce as areduce
from acx.core.moves import enumerate_moves, s_step
from acx.aut import orbit_key
from ac_final_paper.solvers.triple_gs import generate_non_automorphic_complete_cov_moves, _compact_triple_native
from ac_final_paper.solvers.ccov_gs_experiment import load_complete_cov_namespace
from ac_final_paper.solvers.dual_auto_cov_gs import AUTO_COV_MAPS

NS = load_complete_cov_namespace()
AUTO = {name: rep for name, rep, _ in AUTO_COV_MAPS}
INV = {'x': 'X', 'X': 'x', 'y': 'Y', 'Y': 'y', 'z': 'Z', 'Z': 'z'}
MAX_LEN = 65


def inv(w): return ''.join(INV[c] for c in reversed(w))
def free(w):
    s = []
    for c in w:
        if s and INV[s[-1]] == c: s.pop()
        else: s.append(c)
    return ''.join(s)
def cred(w):
    w = free(w)
    while len(w) > 1 and INV[w[0]] == w[-1]: w = w[1:-1]
    return w
def cw(w): return canonical_word(parse(w)) if w else ()
def canon(pair): return canonical_rels(tuple(parse(cred(r)) for r in pair))
def det(pair):
    m = [[sum((c == 'x') - (c == 'X') for c in r), sum((c == 'y') - (c == 'Y') for c in r)] for r in pair]
    return m[0][0] * m[1][1] - m[0][1] * m[1][0]
_ok = {}
def okey(pair):
    k = canon(pair)
    if k not in _ok: _ok[k] = orbit_key(Presentation(2, k), 'fast')
    return _ok[k]
def rot(w, k): return w[k:] + w[:k]


def sub_ok(fr, to, strict=True):
    """to = fr with r_i -> cred(rot(r_i)*rot(r_j^s)) (seam-cancelling if strict), the other relator unchanged."""
    tc = canon(to)
    for i in (0, 1):
        ri, rj = fr[i], fr[1 - i]
        keep = cw(rj)
        if keep == tc[0]: target = tc[1]
        elif keep == tc[1]: target = tc[0]
        else: continue
        L = len(target)
        for oj in (rj, inv(rj)):
            for k1 in range(len(ri)):
                a = rot(ri, k1)
                for k2 in range(len(oj)):
                    b = rot(oj, k2)
                    if strict and INV[a[-1]] != b[0]: continue
                    w = cred(a + b)
                    if len(w) == L and cw(w) == target: return True
    return False


def acx_child(fr, to):
    c = canonical_rels(tuple(parse(r) for r in fr)); p = Presentation(2, c); tc = canon(to)
    return any(s_step(p, m).rels == tc for m in enumerate_moves(c))


def relabel(w, t):
    s = 'y' if t == 'x' else 'x'
    mp = {s: 'x', INV[s]: 'X', 'z': 'y', 'Z': 'Y'}
    return ''.join(mp[c] for c in w)
def subst(w, t, e): return ''.join(e if c == t else inv(e) if c == INV[t] else c for c in w)


def single_cov_recon(fr, to, m):
    """Rebuild the dual's single CoV from (subword, target, replacement): some rotation of some relator starts with
    subword w; temp = z + rest has one target letter; solving gives replacement E; new state = relabel(other, defining)."""
    w, t, E = m['subword'], m['target'], m['replacement']; L = len(w); tc = canon(to)
    for si in (0, 1):
        src, other = fr[si], fr[1 - si]
        for k in range(len(src)):
            r = rot(src, k)
            if not r.startswith(w): continue
            temp = 'z' + r[L:]
            if sum(c in (t, INV[t]) for c in temp) != 1: continue
            pos = [i for i, c in enumerate(temp) if c in (t, INV[t])][0]
            pre, suf = temp[:pos], temp[pos + 1:]
            E2 = free(inv(pre) + inv(suf)) if temp[pos] == t else free(suf + pre)
            if E2 != E: continue
            if cred(subst(temp, t, E)) != '': continue
            dfn = cred('z' + inv(w))
            new = (relabel(cred(subst(other, t, E)), t), relabel(cred(subst(dfn, t, E)), t))
            if all(new) and canon(new) == tc: return True
    return False


def auto_recon(fr, to, name):
    rep = AUTO[name]
    img = tuple(cred(''.join(rep.get(c, c) for c in r)) for r in fr)
    return all(img) and canon(img) == canon(to)


def complete_gen(fr, to):
    recs, _ = generate_non_automorphic_complete_cov_moves(
        NS, tuple(fr), max_len=MAX_LEN,
        automorphic_key=lambda s: tuple(_compact_triple_native.automorphic_equivalence_key(s[0], s[1])))
    outs = [tuple(r['next_state']) for r in recs]
    return tuple(to) in outs, canon(to) in {canon(o) for o in outs}, len(outs)


def main(path, outp):
    random.seed(0)
    c = collections.Counter(); fails = collections.defaultdict(list)
    rows_nonorbit = []; rows_stable = []
    def fail(k, rid):
        c['FAIL:' + k] += 1
        if rid not in fails[k]: fails[k].append(rid)
    rows = [json.loads(l) for l in open(path)]
    c['rows'] = len(rows)
    for r in rows:
        if r.get('error'): fail('error_row', r['id'])
        if not r.get('solved'): continue
        rid = r['id']; c['solved'] += 1
        P = [tuple(s) for s in r['path']]; M = r['moves']
        if r['kind'] == 'stable_cert': rows_stable.append(rid)
        if not (len(M) == len(P) - 1 == r['path_length']): fail('length_mismatch', rid)
        if canon(P[0]) != canon((r['r1'], r['r2'])): fail('start_mismatch', rid)
        if not (all(len(x) == 1 for x in P[-1]) and {x.lower() for x in P[-1]} == {'x', 'y'}): fail('end_not_trivial', rid)
        for s in P:
            c['states'] += 1
            if abs(det(s)) != 1: fail('det_not_pm1', rid)
            if any(cred(x) != x or not x for x in s): fail('state_not_cyc_reduced', rid)
        kinds = collections.Counter(); nonorbit = False
        for i, m in enumerate(M):
            fr, to = P[i], P[i + 1]; mt = m['move_type']
            if mt == 'standard_substitution':
                k = 'sub'
                if sub_ok(fr, to): c['sub_ok'] += 1
                else:
                    fail('sub_not_Smove', rid)
                    c['sub_general_product' if sub_ok(fr, to, False) else 'sub_not_any_product'] += 1
                if random.random() < 1.0:  # cross-check against ACSolverX's own S-move enumerator
                    c['sub_acx_sampled'] += 1
                    if not acx_child(fr, to): fail('sub_acx_crosscheck', rid)
            elif mt == 'auto_cov' or (mt == 'complete_cov' and m.get('cov_variant') == 'single_cov'):
                k = 'auto_cov' if mt == 'auto_cov' else 'single_cov'
                same = okey(fr) == okey(to)
                c[k + '_in_orbit' if same else k + '_NOT_in_orbit'] += 1
                if not same: fail(k + '_not_in_orbit', rid); nonorbit = True
                recon = auto_recon(fr, to, m['automorphism']) if k == 'auto_cov' else single_cov_recon(fr, to, m)
                c[k + '_recon_ok' if recon else k + '_recon_FAIL'] += 1
                if not recon: fail(k + '_recon', rid)
            elif mt == 'complete_cov':
                k = 'complete_cov'
                same = okey(fr) == okey(to)
                c['complete_cov_in_orbit' if same else 'complete_cov_not_in_orbit'] += 1
                if not same: nonorbit = True
                exact, can, n = complete_gen(fr, to)
                c['complete_cov_gen_exact' if exact else ('complete_cov_gen_canon' if can else 'complete_cov_gen_FAIL')] += 1
                if not can: fail('complete_cov_not_generated', rid)
                if abs(det(to)) != 1: fail('complete_cov_det', rid)
            else:
                k = 'unknown'; fail('unknown_move_type', rid)
            kinds[k] += 1
        mk = r['move_kinds']; mk2 = {('sub' if a == 'standard_substitution' else a): b for a, b in mk.items()}
        if dict(kinds) != mk2: fail('move_kinds_mismatch', rid)
        if (r['kind'] == 'stable_cert') != bool(kinds.get('complete_cov')): fail('kind_label_mismatch', rid)
        if nonorbit: rows_nonorbit.append(rid)
    out = dict(file=path.split('/')[-1], counts=dict(c), failures={k: v for k, v in fails.items()},
               rows_with_nonorbit_step=len(rows_nonorbit), stable_cert_rows=len(rows_stable),
               nonorbit_rows_equal_stable_cert_rows=sorted(rows_nonorbit) == sorted(rows_stable))
    json.dump(out, open(outp, 'w'), indent=1)
    print(json.dumps(out))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
