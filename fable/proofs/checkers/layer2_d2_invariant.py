"""W2i: d2 -- the layer-2 double-coset invariant of Gamma = <R, U, w> on Lambda^2 M.

W2H_INFINITE_INDEX_LIVENESS.md section 7 poses this as the decisive next
question.  The module identification comes from
literature/proofs/AK3_DEPTH4_PERIOD_TWO_FULL_LIFT_BOUNDARY.md section 3:

    W := gamma_2 N / gamma_3 N = [N,N]/[[N,N],N] ~= Lambda^2 M        (3.1)
    g . (m ^ n) = (g m) ^ (g n)                                       (3.4)
    L_r^{(2)}(m ^ n) := sum_g a_{r,g} (g m ^ g n)                     (3.5)
    [R(F;k)] = Theta(F) + sum_r L_r^{(2)} Y_r                         (3.6)
    I_2 := sum_r im L_r^{(2)},   C_2 := Lambda^2 M / I_2              (3.7)

so L_r^{(2)} is exactly the group-ring element L_r acting on the left
Z[Q]-module Lambda^2 M, W2g's Lemmas 1 and 2 transfer verbatim, and

    L2^(2) + L3^(2) + L4^(2) images = I_Gamma . Lambda^2 M
    A_2 := Lambda^2 M / I_Gamma Lambda^2 M   (the Gamma-coinvariants)
    C_2 = A_2 / image(L0^(2), L1^(2)).

THE STRUCTURE THIS CHECKER USES (and proves effectively)
--------------------------------------------------------
Write X = Q/H, H = <c>.  For u, v in Q with uH != vH,

    the Gamma-orbit of the ORDERED pair (uH, vH) is classified exactly by
        kappa(u,v) := min over h1,h2 in H of  ( h1^-1 u^-1 v h2 ,  Gamma u h1 )

because Gamma \\ (Q x Q) -> Gamma\\Q x Q, (u,v) |-> (Gamma u, u^-1 v) is a
bijection, and the H x H action is (u,v) -> (u h1, v h2).  Two consequences
drive everything:

  * z = u^-1 v is a DIAGONAL INVARIANT: g.(u,v) has the same z.  So every
    operator row is supported inside one "displacement block", indexed by
    the H-double coset D = H z H.  This is exactly the index set D of the
    source doc's (3.12)/(3.15): reduced form t^{n0} c t^{n1} c ... c t^{nk},
    n_j != 0, modulo D ~ D^-1.
  * inside a block the remaining coordinate is Gamma u in Gamma\\Q, so for
    the 44 finite-index chains a block has EXACTLY |Gamma\\Q| = 4 ordered
    classes and the whole computation is finite and exact.

Signs.  Lambda^2 M is a SIGNED permutation module, so the coinvariants are
    A_2 = (+) Z  over ordered-pair orbits not fixed by reversal
        (+) Z/2 over orbits some gamma in Gamma reverses,
the Z/2 summands being the layer-2 2-torsion W2h predicted structurally.
Reversal is kappa(v,u), computable; a fixed class is certified with an
explicit gamma = v h u^-1 checked to lie in Gamma by Stallings folding.

The augmentation analogue, and why "d2 = 1" cannot mean what it meant at
layer 1.  The source doc's (3.16) proves every L_r^(2) dies in the FULL
Q-coinvariants W_Q = Lambda^2 M / I_Q, because Xi(g.w) = Xi(w) and
eps(L_r) = 0.  So there is a canonical surjection Xi : A_2 ->> W_Q killing
the whole operator image, and by (3.15a)

    W_Q = (+)_{D2} Z  (+)  (+)_{D1} Z/2,      D2, D1 both infinite.

Hence "the image is everything" is IMPOSSIBLE at layer 2 and C_2 is always
infinite: the honest layer-2 analogue of W2g's "d = 1" is instead

        image(L0^(2), L1^(2))  ==  ker( Xi : A_2 ->> W_Q ),

block by block.  d2(D) = 1 means the block adds nothing beyond the
Q-coinvariant obstruction the codex note already has -- equivalently
Xi_Z : C_2(D) -> W_Q(D) is an ISOMORPHISM, not merely onto.

The uniform reduction (--mode uniform).  Inside a block, s |-> kappa(s, z)
is a bijection Gamma\\Q -> {generators}, and in those coordinates the row of
L_r^(2) is  sum_g a_{r,g} e_{rho(sigma(g))}  in Z[Gamma\\Q] -- with no z in
it.  So for every D != D^-1 the layer-2 question is W2g's layer-1
computation run one level finer, on Gamma\\Q instead of Omega =
Gamma\\Q/<c>, and it is the SAME group for every such D; for D = D^-1 the
reversal is right multiplication by z h, i.e. some rho in P, so looping
over the involutions of P covers every self-inverse D.  Both loops are
finite: on the 44 finite-index chains the verdict is a theorem about ALL
displacement classes, not a truncated sample.

MODES
  identity  effective controls: the L2/L3/L4 layer-2 rows vanish identically
            (W2g Lemma 2' at layer 2), Xi(row) = 0 for every row, the pair
            class is Gamma-invariant while a non-Gamma element moves it, the
            base coset is pinned, and corrupting one operator term breaks
            the vanishing.
  lambda1   finite specialization: the same Frame/sigma/P machinery run on M
            (layer 1) must reproduce out/w2g_omega_all.json exactly.
  d2        per finite-index chain and per sampled displacement class D:
            A_2(D), its torsion classes with explicit gamma-swap witnesses,
            the operator image, C_2(D) and d2(D).
  uniform   the same, for EVERY D at once, by the reduction above; the
            sampled blocks must agree with the uniform prediction.
  torsion   is A_2 free?  A reversing gamma is forced to be an involution,
            so the torsion is nonempty iff Gamma has torsion iff its
            Stallings core has a c-fixed vertex.  POSITIVE control:
            Gamma' = <R, U, w, c> has torsion by construction, so torsion
            classes MUST appear there, each with a verified swap witness.
  probe     POSITIVE control on a SYNTHETIC system (L0, L1 doubled), whose
            image lies in 2 A_2 and so cannot contain a primitive ker-Xi
            vector; on the real system that vector IS in the image with a
            re-multiplied witness, and the echelon and Smith-normal-form
            paths must agree.
  inf       the 23 infinite-index chains: Gamma\\Q is infinite, so coverage
            of the state differences is measured over a ball (optionally
            W2h's aligned family) with the W2h margin discipline.

EXIT CODES
  0  run completed with every control green (any verdict is a RESULT).
  2  a control failed -- the run is void.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
sys.path.insert(0, str(HERE))

_ARGV = list(sys.argv)
sys.argv = sys.argv[:1]
import g_stratum_death as GS  # noqa: E402
import infinite_index_liveness as IIL  # noqa: E402
sys.argv = _ARGV

from experiments.stable_ac.depth4_period_two_lift_certificate import (  # noqa
    quotient_inverse,
    quotient_multiply,
    quotient_reduce,
)

PS, LV = GS.PS, GS.LV
C, T = LV.C, LV.T
HH = ((), (C,))
OMEGA_JSON = HERE / "out" / "w2g_omega_all.json"


# ------------------------------------------------------------- words / z


def zkey(z):
    return (len(z), z)


def dcoset(z):
    """canonical representative of the H-double coset H z H."""
    return min((quotient_multiply(h1, z, h2) for h1 in HH for h2 in HH),
               key=zkey)


def dclass(z):
    """canonical name of {H z H, H z^-1 H} and whether the two coincide."""
    a = dcoset(z)
    b = dcoset(quotient_inverse(z))
    return (min(a, b, key=zkey), a == b)


def z_family(kmax, nmax):
    """reduced displacement reps t^{n0} c t^{n1} c ... c t^{nk}, n_j != 0.

    Exactly the source doc's (3.15) normal form for (H\\Q/H) \\ {H}; the
    inversion identification (n_0..n_k) ~ (-n_k..-n_0) is applied so each
    class is emitted once.
    """
    out, seen = [], set()
    exps = [n for n in range(-nmax, nmax + 1) if n]
    def rec(pref, k):
        if pref:
            inv = tuple(-n for n in reversed(pref))
            key = min(pref, inv)
            if key not in seen:
                seen.add(key)
                w = []
                for j, n in enumerate(pref):
                    if j:
                        w.append(C)
                    w.extend([T] * n if n > 0 else [-T] * (-n))
                out.append(quotient_reduce(tuple(w)))
        if k == kmax:
            return
        for n in exps:
            rec(pref + (n,), k + 1)
    rec((), 0)
    return sorted(out, key=zkey)


# --------------------------------------------- ordered pair classes


class Frame:
    """A state space with a right Q-action: finite coset table or completed.

    `step(s, letter)` and `walk(s, word)` are the only things the pair
    machinery needs, so the finite (CosetTable) and infinite (Completed)
    cases run through one code path -- which is what makes `--mode lambda1`
    a real cross-check rather than a second implementation.
    """

    def __init__(self, gens, finite):
        self.finite = finite
        if finite:
            self.ct = GS.CosetTable(gens)
            self.ok = self.ct.ok
            if not self.ok:
                return
            self.base = self.ct.base
            self.states = list(range(self.ct.n))
            self.P = self.ct.P
        else:
            self.cp = IIL.Completed(GS.Folded(gens))
            self.ok = True
            self.base = self.cp.base
            self.states = None
            self.P = None

    def walk(self, s, word):
        if self.finite:
            return self.ct.trace_from(s, word)
        return self.cp.walk(s, IIL.wstr(word) if not isinstance(word, str)
                            else word)

    def trace(self, word):
        return self.walk(self.base, word)


def ocls(fr, s, z):
    """kappa: canonical name of the Gamma-orbit of the ordered pair (s, z)."""
    best = None
    for h1 in HH:
        for h2 in HH:
            zz = quotient_multiply(quotient_inverse(h1), z, h2)
            key = (zkey(zz), fr.walk(s, h1))
            if best is None or key < best:
                best = key
    return best


def ocls_rev(fr, s, z):
    """the class of the REVERSED ordered pair."""
    return ocls(fr, fr.walk(s, z), quotient_inverse(z))


def signed_gen(fr, s, z):
    """(generator, sign, is_torsion) for the wedge class of (s, z)."""
    a = ocls(fr, s, z)
    b = ocls_rev(fr, s, z)
    if a == b:
        return a, 1, True
    return (a, 1, False) if a < b else (b, -1, False)


def xi_sign(z, dplus):
    """Xi : A_2 ->> W_Q, the source doc's (3.15b) coinvariant map."""
    return 1 if dcoset(z) == dplus else -1


# ------------------------------------------------------- integer linalg


def snf(mat, ncols):
    """invariant factors of the lattice spanned by `mat` inside Z^ncols.

    Returns (rank, [d1..dr]) with d1 | d2 | ... ; the cokernel Z^ncols / L
    is then Z^{ncols-rank} (+) (+) Z/di.
    """
    A = [list(r) for r in mat if any(r)]
    facs = []
    r0, c0 = 0, 0
    while r0 < len(A) and c0 < ncols:
        piv = None
        for i in range(r0, len(A)):
            if A[i][c0]:
                if piv is None or abs(A[i][c0]) < abs(A[piv][c0]):
                    piv = i
        if piv is None:
            c0 += 1
            continue
        A[r0], A[piv] = A[piv], A[r0]
        again = False
        for i in range(r0 + 1, len(A)):
            if A[i][c0]:
                f = A[i][c0] // A[r0][c0]
                for j in range(ncols):
                    A[i][j] -= f * A[r0][j]
                if A[i][c0]:
                    again = True
        if again:
            continue
        # clear the pivot row's other columns by column ops (column ops do
        # not change the lattice's isomorphism type of the cokernel)
        for j in range(c0 + 1, ncols):
            if A[r0][j]:
                f = A[r0][j] // A[r0][c0]
                if f:
                    for i in range(r0, len(A)):
                        A[i][j] -= f * A[i][c0]
        if any(A[r0][j] for j in range(c0 + 1, ncols)):
            # residual entries smaller than the pivot: swap and retry
            for j in range(c0 + 1, ncols):
                if A[r0][j] and abs(A[r0][j]) < abs(A[r0][c0]):
                    for i in range(r0, len(A)):
                        A[i][c0], A[i][j] = A[i][j], A[i][c0]
                    break
            continue
        facs.append(abs(A[r0][c0]))
        r0 += 1
        c0 += 1
    # make the chain divisible (small matrices: bubble the gcds)
    from math import gcd
    changed = True
    while changed:
        changed = False
        for i in range(len(facs) - 1):
            a, b = facs[i], facs[i + 1]
            g = gcd(a, b)
            l = a * b // g if g else 0
            if (g, l) != (a, b):
                facs[i], facs[i + 1] = g, l
                changed = True
    return len(facs), facs


def cokernel(rows, gens, extra):
    """structure of Z^gens / <rows, extra> as (free_rank, torsion list)."""
    idx = {g: i for i, g in enumerate(gens)}
    mat = []
    for row in rows:
        v = [0] * len(gens)
        for g, a in row.items():
            v[idx[g]] += a
        mat.append(v)
    mat.extend(extra)
    rank, facs = snf(mat, len(gens))
    return len(gens) - rank, [f for f in facs if f != 1]


# ------------------------------------------------------------ the rows


def sigma_map(fr, ops):
    """{operator index: {group word: state of Gamma g}}."""
    return {i: {gw: fr.trace(gw) for gw in ops[i]} for i in range(len(ops))}


def block_rows(fr, ops, sig, z, which=(0, 1)):
    """every layer-2 row in the displacement block of z, exactly.

    W2g Lemma 3 lifted: the row of L_r^(2) (e_u ^ e_{uz}) has terms
    kappa(sigma(g) . u, z), so it depends on u only through rho(u) in P.
    Looping over P therefore enumerates ALL rows of the block at once.
    """
    out = []
    for rho in fr.P:
        for i in which:
            acc = {}
            for gw, a in ops[i].items():
                st = rho[sig[i][gw]]
                gen, sg, _t = signed_gen(fr, st, z)
                acc[gen] = acc.get(gen, 0) + a * sg
            acc = {k: a for k, a in acc.items() if a}
            if acc:
                out.append((i, acc))
    return out


def block_gens(fr, z):
    """generators of A_2 in the block, and which of them are 2-torsion."""
    gens, tor = [], set()
    for s in fr.states:
        g, _sg, t = signed_gen(fr, s, z)
        if g not in gens:
            gens.append(g)
        if t:
            tor.add(g)
    return sorted(gens), tor


# ------------------------------------------------- gamma-swap witnesses


def in_gamma(folded, word):
    """membership in Gamma by Stallings folding: the word must close up."""
    s = folded.find(0)
    for l in word:
        if abs(l) == C:
            nxt = folded.cm.get(s)
        elif l == T:
            nxt = folded.tout.get(s)
        else:
            nxt = folded.tin.get(s)
        if nxt is None:
            return False
        s = folded.find(nxt)
    return s == folded.find(0)


def swap_witness(folded, u, z):
    """gamma in Gamma with gamma.uH = vH and gamma.vH = uH, v = u z."""
    v = quotient_multiply(u, z)
    for h in HH:
        gam = quotient_multiply(v, h, quotient_inverse(u))
        if not in_gamma(folded, gam):
            continue
        gu = quotient_multiply(gam, u)
        gv = quotient_multiply(gam, v)
        ok1 = quotient_multiply(quotient_inverse(gu), v) in (
            (), (C,))
        ok2 = quotient_multiply(quotient_inverse(gv), u) in ((), (C,))
        if ok1 and ok2:
            return gam
    return None


def realise(fr, target_gen, z, radius=8):
    """a concrete u whose ordered pair (u, uz) has class `target_gen`."""
    for w in IIL.reduced_words(radius):
        u = LV.to_tuple(w)
        if signed_gen(fr, fr.trace(u), z)[0] == target_gen:
            return u
    return None


# ------------------------------------------------------------- helpers


def setup(row, window=(0, 0, 0, 0), k=0):
    ch = tuple(row["chain"])
    g = row["g_gen"]
    gens = GS.gamma_gens(ch, g)
    folded = GS.Folded(gens)
    fr = Frame(gens, folded.complete())
    sl = PS.chain_slots_g(ch, g, k, k)
    ops, defect, h = GS.window_data(ch, g, sl, window)
    return ch, g, folded, fr, ops, defect, h


def sel_rows(rows, args, finite):
    out = []
    for r in rows:
        f = GS.Folded(GS.gamma_gens(r["chain"], r["g_gen"]))
        if f.complete() == finite:
            out.append(r)
    if args.stratum_only:
        out = [r for r in out if r["stratum"]]
    if args.chains:
        a, b = args.chains.split(":")
        out = out[int(a or 0):int(b or len(out))]
    return out


def _dump(args, name, summ, rows):
    if args.json:
        Path(args.json).write_text(json.dumps(
            {"schema": f"acsolverx.w2i.{name}.v1",
             "summary": summ, "rows": rows}, indent=1))


# ------------------------------------------------------------- modes


def mode_identity(args, rows):
    """EFFECTIVE controls for every algebraic fiat this note uses."""
    sel = rows
    if args.chains:
        a, b = args.chains.split(":")
        sel = sel[int(a or 0):int(b or len(sel))]
    zs = z_family(args.zk, args.zn)[:args.zmax]
    out, ok = [], True
    for r in sel:
        ch, g, folded, fr, ops, _d, _h = setup(r)
        sig = sigma_map(fr, ops)
        gens_gamma = GS.gamma_gens(ch, g)
        base_ok = all(fr.trace(GS.q(x)) == fr.base for x in gens_gamma)
        n234, bad234, nxi, badxi = 0, 0, 0, 0
        us = [LV.to_tuple(w) for w in IIL.reduced_words(args.radius)]
        for z in zs:
            dplus, _self = dclass(z)
            for u in us:
                s = fr.trace(u)
                for i in (2, 3, 4):
                    n234 += 1
                    acc = {}
                    for gw, a in ops[i].items():
                        st = fr.walk(fr.trace(gw), u)
                        gen, sg, _t = signed_gen(fr, st, z)
                        acc[gen] = acc.get(gen, 0) + a * sg
                    if any(acc.values()):
                        bad234 += 1
                for i in (0, 1):
                    nxi += 1
                    tot = 0
                    for gw, a in ops[i].items():
                        st = fr.walk(fr.trace(gw), u)
                        gen, sg, _t = signed_gen(fr, st, z)
                        zz = gen[0][1]
                        tot += a * sg * xi_sign(zz, dplus)
                    # W_Q's summand is Z when D != D^-1 and Z/2 when D = D^-1
                    # (source doc (3.15a)), so the self-inverse blocks are
                    # tested modulo 2 -- there the orientation sign is 1.
                    if (tot % 2 if _self else tot):
                        badxi += 1
                del s
        # Gamma-invariance of the pair class, with a non-Gamma control
        n_inv, bad_inv, moved = 0, 0, 0
        gam_words = [GS.q(x) for x in gens_gamma]
        gam_words += [quotient_multiply(gam_words[0], gam_words[1]),
                      quotient_multiply(gam_words[2], gam_words[0])]
        # the corruption control needs a witness OUTSIDE Gamma; find one by
        # folding membership rather than assuming any fixed letter works
        # (w = g t g^-1 is t itself on the g = "" chains, so t is in Gamma).
        outside = [GS.q(w) for w in IIL.reduced_words(4)
                   if not in_gamma(folded, GS.q(w))][:4]
        for z in zs[:4]:
            for u in us[:12]:
                s = fr.trace(u)
                k0 = ocls(fr, s, z)
                for gam in gam_words:
                    n_inv += 1
                    if ocls(fr, fr.walk(fr.trace(gam), u), z) != k0:
                        bad_inv += 1
                for dlt in outside:
                    if ocls(fr, fr.walk(fr.trace(dlt), u), z) != k0:
                        moved += 1
        # corruption of one L2 term must break the layer-2 vanishing
        bad_ops = list(ops)
        d2 = dict(bad_ops[2])
        d2.pop(sorted(d2)[0])
        bad_ops[2] = d2
        broke = False
        for z in zs[:4]:
            for u in us[:12]:
                acc = {}
                for gw, a in bad_ops[2].items():
                    st = fr.walk(fr.trace(gw), u)
                    gen, sg, _t = signed_gen(fr, st, z)
                    acc[gen] = acc.get(gen, 0) + a * sg
                if any(acc.values()):
                    broke = True
                    break
            if broke:
                break
        rec = {"chain": r["chain"], "g": g, "finite_index": fr.finite,
               "base_pinned": base_ok,
               "l234_layer2_row_checks": n234,
               "l234_layer2_nonvanishing": bad234,
               "xi_row_checks": nxi, "xi_nonzero": badxi,
               "gamma_invariance_checks": n_inv,
               "gamma_invariance_failures": bad_inv,
               "non_gamma_element_moves_class": moved,
               "corruption_breaks_l234_vanishing": broke}
        rec["passed"] = (base_ok and bad234 == 0 and badxi == 0
                         and bad_inv == 0 and moved > 0 and broke)
        ok = ok and rec["passed"]
        out.append(rec)
        print(json.dumps(rec))
    summ = {"chains": len(out), "all_passed": ok and bool(out),
            "l234_layer2_row_checks": sum(o["l234_layer2_row_checks"]
                                          for o in out),
            "l234_layer2_nonvanishing": sum(o["l234_layer2_nonvanishing"]
                                            for o in out),
            "xi_row_checks": sum(o["xi_row_checks"] for o in out),
            "xi_nonzero": sum(o["xi_nonzero"] for o in out),
            "gamma_invariance_checks": sum(o["gamma_invariance_checks"]
                                           for o in out),
            "gamma_invariance_failures": sum(o["gamma_invariance_failures"]
                                             for o in out),
            "z_classes": len(zs), "radius": args.radius}
    print(json.dumps({"summary": summ}))
    _dump(args, "identity", summ, out)
    return 0 if summ["all_passed"] else 2


def mode_lambda1(args, rows):
    """finite specialization: the same machinery on M must reproduce W2g."""
    want = {}
    for rec in json.loads(OMEGA_JSON.read_text())["rows"]:
        if rec.get("gamma_index"):
            want[(tuple(rec["chain"]), rec["g"])] = rec
    from math import gcd
    out, ok = [], True
    for r in sel_rows(rows, args, True):
        ch, g, _f, fr, ops, defect, _h = setup(r)
        sig = sigma_map(fr, ops)
        d, nonvanishing = 0, 0
        for rho in fr.P:
            for i in range(5):
                row = [0] * fr.ct.n_omega
                for gw, a in ops[i].items():
                    row[fr.ct.omega[rho[sig[i][gw]]]] += a
                if i >= 2 and any(row):
                    nonvanishing += 1
                if i < 2:
                    for x in row:
                        d = gcd(d, abs(x))
        m = sum(cf for v, cf in defect.items()
                if fr.ct.omega[fr.ct.trace(v)] == 0)
        ref = want.get((ch, g))
        rec = {"chain": r["chain"], "g": g, "d": d, "m": m,
               "n_omega": fr.ct.n_omega, "|P|": len(fr.P),
               "l234_rows_nonvanishing": nonvanishing,
               "w2g_d": ref["d"] if ref else None,
               "w2g_m": ref["m"] if ref else None,
               "w2g_n_omega": ref["n_omega"] if ref else None}
        rec["agrees_with_w2g"] = bool(
            ref and [d] == ref["d"] and rec["n_omega"] == ref["n_omega"]
            and len(fr.P) == ref["|P|"] and nonvanishing == 0
            and m in ref["m"])
        ok = ok and rec["agrees_with_w2g"]
        out.append(rec)
    summ = {"finite_index_chains": len(out), "reference_rows": len(want),
            "agree_with_w2g_omega_all": sum(1 for o in out
                                            if o["agrees_with_w2g"]),
            "d_values": sorted({o["d"] for o in out}),
            "all_agree": ok and len(out) == len(want) and bool(out)}
    print(json.dumps({"summary": summ}))
    _dump(args, "lambda1", summ, out)
    return 0 if summ["all_agree"] else 2


def block_report(fr, folded, ops, sig, z, double=False):
    """A_2(D), the operator image, and d2(D) for one displacement block."""
    gens, tor = block_gens(fr, z)
    dplus, self_inv = dclass(z)
    rows = block_rows(fr, ops, sig, z)
    if double:
        rows = [(i, {k: 2 * a for k, a in row.items()}) for i, row in rows]
    idx = {g: i for i, g in enumerate(gens)}
    extra = []
    for g in gens:
        if g in tor:
            v = [0] * len(gens)
            v[idx[g]] = 2
            extra.append(v)
    support_ok = all(set(row) <= set(gens) for _i, row in rows)
    # the whole group A_2(D)
    a2_free, a2_tor = cokernel([], gens, extra)
    # C_2(D) = A_2(D) / image
    c2_free, c2_tor = cokernel([row for _i, row in rows], gens, extra)
    # W_Q(D): Z when D != D^-1, Z/2 when D = D^-1  (source doc (3.15a))
    wq_free, wq_tor = (0, [2]) if self_inv else (1, [])
    blind = (c2_free, c2_tor) == (wq_free, wq_tor)
    # d2: the extra invariant factors beyond W_Q
    return {"z": LV.literal(z), "d_plus": LV.literal(dplus),
            "self_inverse": self_inv,
            "n_gens": len(gens), "n_torsion_gens": len(tor),
            "A2": {"free": a2_free, "torsion": a2_tor},
            "rows": len(rows), "row_support_inside_block": support_ok,
            "C2": {"free": c2_free, "torsion": c2_tor},
            "WQ": {"free": wq_free, "torsion": wq_tor},
            "image_is_ker_xi": blind,
            "d2": 1 if blind else [c2_free - wq_free, c2_tor],
            "torsion_gens": [g for g in gens if g in tor]}


def mode_d2(args, rows):
    """main mode: d2 per finite-index chain and displacement class."""
    zs = z_family(args.zk, args.zn)[:args.zmax]
    out, ok = [], True
    for r in sel_rows(rows, args, True):
        ch, g, folded, fr, ops, _d, _h = setup(r)
        sig = sigma_map(fr, ops)
        blocks, wit_ok, wit_n, wit_missing = [], True, 0, 0
        for z in zs:
            b = block_report(fr, folded, ops, sig, z)
            ok = ok and b["row_support_inside_block"]
            # explicit gamma-swap witness for every torsion generator
            for tg in b["torsion_gens"]:
                u = realise(fr, tg, z, args.radius)
                gam = swap_witness(folded, u, z) if u is not None else None
                wit_n += 1
                if gam is None:
                    wit_missing += 1
                    wit_ok = False
            b.pop("torsion_gens")
            blocks.append(b)
        rec = {"chain": r["chain"], "g": g,
               "blocks": len(blocks),
               "blocks_image_is_ker_xi": sum(1 for b in blocks
                                             if b["image_is_ker_xi"]),
               "blocks_with_extra_obstruction": sum(
                   1 for b in blocks if not b["image_is_ker_xi"]),
               "self_inverse_blocks": sum(1 for b in blocks
                                          if b["self_inverse"]),
               "torsion_gens_total": sum(b["n_torsion_gens"]
                                         for b in blocks),
               "swap_witnesses": wit_n, "swap_witnesses_missing": wit_missing,
               "C2_shapes": sorted({json.dumps(b["C2"]) for b in blocks}),
               "d2_values": sorted({json.dumps(b["d2"]) for b in blocks}),
               "detail": blocks if args.detail else None}
        ok = ok and wit_ok
        out.append(rec)
        print(json.dumps({k: v for k, v in rec.items() if k != "detail"}))
    summ = {"chains": len(out), "z_classes": len(zs),
            "chains_fully_blind": sum(
                1 for o in out if o["blocks_with_extra_obstruction"] == 0),
            "blocks_total": sum(o["blocks"] for o in out),
            "blocks_with_extra_obstruction": sum(
                o["blocks_with_extra_obstruction"] for o in out),
            "torsion_gens_total": sum(o["torsion_gens_total"] for o in out),
            "swap_witnesses": sum(o["swap_witnesses"] for o in out),
            "swap_witnesses_missing": sum(o["swap_witnesses_missing"]
                                          for o in out),
            "d2_values_seen": sorted({v for o in out for v in o["d2_values"]}),
            "controls_passed": ok and bool(out)}
    summ["verdict"] = ("BLIND_THROUGH_LAYER_2_BEYOND_XI"
                       if summ["blocks_with_extra_obstruction"] == 0
                       else "EXTRA_LAYER2_OBSTRUCTION_CANDIDATE")
    print(json.dumps({"summary": summ}))
    _dump(args, "d2", summ, out)
    return 0 if summ["controls_passed"] else 2


def primitive_ker_xi(gens, dplus):
    """a primitive vector of ker(Xi) inside the block, or None."""
    if len(gens) < 2:
        return None
    a, b = gens[0], gens[1]
    return {a: xi_sign(b[0][1], dplus), b: -xi_sign(a[0][1], dplus)}


def mode_probe(args, rows):
    """POSITIVE control: a synthetic system whose d2 is 2 by construction.

    On the real systems the image turns out to contain ker Xi, so nothing
    can ever be certified -- a detector that never fires is not evidence.
    The synthetic system doubles L0 and L1 (L2, L3, L4 untouched), so its
    image lies in 2 A_2 and cannot contain a PRIMITIVE ker-Xi vector.  The
    membership is decided by exact integer echelon (ZEchelon), which is a
    different code path from the Smith-normal-form cokernel used by
    --mode d2, and every positive answer is re-multiplied out and compared
    term by term.
    """
    zs = z_family(args.zk, args.zn)[:args.zmax]
    out, ok, fired = [], True, 0
    for r in sel_rows(rows, args, True):
        ch, g, folded, fr, ops, _d, _h = setup(r)
        sig = sigma_map(fr, ops)
        n, real_in, syn_in, reverified, snf_agree = 0, 0, 0, 0, 0
        for z in zs:
            dplus, _self = dclass(z)
            gens, _tor = block_gens(fr, z)
            v = primitive_ker_xi(gens, dplus)
            if v is None:
                continue
            n += 1
            rws = block_rows(fr, ops, sig, z)
            Zr = IIL.ZEchelon(order=lambda c: c)
            Zs = IIL.ZEchelon(order=lambda c: c)
            for j, (_i, row) in enumerate(rws):
                Zr.add(row, j)
                Zs.add({k: 2 * a for k, a in row.items()}, j)
            mr, combo = Zr.member(v)
            ms, _ = Zs.member(v)
            real_in += int(mr)
            syn_in += int(ms)
            if mr:
                acc = {}
                for j, cf in combo.items():
                    for k, a in rws[j][1].items():
                        acc[k] = acc.get(k, 0) + cf * a
                reverified += int({k: a for k, a in acc.items() if a} == v)
            # cross-check against the independent SNF path
            br = block_report(fr, folded, ops, sig, z)
            bs = block_report(fr, folded, ops, sig, z, double=True)
            snf_agree += int(br["image_is_ker_xi"] == mr
                             and bs["image_is_ker_xi"] == ms)
        rec = {"chain": r["chain"], "g": g, "blocks_tested": n,
               "primitive_in_real_image": real_in,
               "primitive_in_synthetic_image": syn_in,
               "real_witness_reverified": reverified,
               "snf_agrees_with_echelon": snf_agree}
        rec["detector_fires_on_synthetic"] = syn_in == 0 and n > 0
        rec["detector_silent_on_real"] = real_in == n
        rec["witnesses_reverified"] = reverified == real_in
        rec["independent_paths_agree"] = snf_agree == n
        rec["passed"] = (rec["detector_fires_on_synthetic"]
                         and rec["detector_silent_on_real"]
                         and rec["witnesses_reverified"]
                         and rec["independent_paths_agree"])
        fired += int(rec["detector_fires_on_synthetic"])
        ok = ok and rec["passed"]
        out.append(rec)
        print(json.dumps(rec))
    summ = {"chains": len(out), "detector_fired": fired,
            "blocks_tested": sum(o["blocks_tested"] for o in out),
            "all_controls_passed": ok and bool(out),
            "note": "the synthetic system doubles L0 and L1, so its image "
                    "lies in 2 A_2 and cannot contain a primitive ker-Xi "
                    "vector; on the real system the same vector IS in the "
                    "image, with a witness re-multiplied out term by term, "
                    "and the Smith-normal-form path agrees with the echelon "
                    "path on every block"}
    print(json.dumps({"summary": summ}))
    _dump(args, "probe", summ, out)
    return 0 if summ["all_controls_passed"] else 2


def mode_uniform(args, rows):
    """d2 for EVERY displacement class at once, on the finite-index chains.

    In the block of z the map  s |-> kappa(s, z)  is a bijection
    Gamma\\Q -> {generators of A_2(D)} (the z-part of kappa is the same for
    every s), and the orientation sign is constant on the block.  So in
    those coordinates the row of L_r^(2) is

        sum_g a_{r,g} e_{rho(sigma(g))}   in  Z[Gamma\\Q],

    which does not mention z at all.  Hence

      * D != D^-1 :  A_2(D) = Z[Gamma\\Q],  Xi = the augmentation, and
        C_2(D) = Z[Gamma\\Q] / <L0, L1 columns>  -- ONE group, the same for
        every such D.  This is W2g's layer-1 computation run one level
        finer: on Gamma\\Q instead of Omega = Gamma\\Q/<c>.
      * D = D^-1 :  reversal acts as right multiplication by z h for some
        h in H, i.e. as some rho in P, so A_2(D) = Z[Gamma\\Q] modulo
        e_{iota s} = -e_s for that involution iota, and looping over the
        involutions of P covers every self-inverse D.

    Both loops are finite, so the verdict is a theorem about all D, not a
    truncated measurement.  The control ties it to the concrete side: for
    every z in the sampled family the concrete block report must equal the
    uniform prediction.
    """
    zs = z_family(args.zk, args.zn)[:args.zmax]
    out, ok = [], True
    for r in sel_rows(rows, args, True):
        ch, g, folded, fr, ops, _d, _h = setup(r)
        sig = sigma_map(fr, ops)
        n = fr.ct.n
        rows_s, dead234 = [], 0
        for rho in fr.P:
            for i in range(5):
                v = [0] * n
                for gw, a in ops[i].items():
                    v[rho[sig[i][gw]]] += a
                if i >= 2:
                    dead234 += int(any(v))
                else:
                    rows_s.append(v)
        free_ck = snf([list(v) for v in rows_s], n)
        free_coker = (n - free_ck[0], [f for f in free_ck[1] if f != 1])
        # self-inverse blocks: every fixed-point-free involution in P
        inv_results = {}
        for rho in fr.P:
            if any(rho[rho[s]] != s for s in range(n)):
                continue
            if any(rho[s] == s for s in range(n)):
                continue        # a fixed point would be a torsion class
            rep, sgn = {}, {}
            k = 0
            for s in range(n):
                if s in rep:
                    continue
                rep[s], sgn[s] = k, 1
                rep[rho[s]], sgn[rho[s]] = k, -1
                k += 1
            mat = []
            for v in rows_s:
                w = [0] * k
                for s in range(n):
                    w[rep[s]] += sgn[s] * v[s]
                mat.append(w)
            rk, fs = snf(mat, k)
            inv_results[str(rho)] = [k - rk, [f for f in fs if f != 1]]
        # control: the concrete blocks must match the uniform prediction
        mism = 0
        for z in zs:
            b = block_report(fr, folded, ops, sig, z)
            want = ([0, [2]] if b["self_inverse"]
                    else [free_coker[0], free_coker[1]])
            got = [b["C2"]["free"], b["C2"]["torsion"]]
            if b["self_inverse"]:
                if got != [0, [2]]:
                    mism += 1
            elif got != want:
                mism += 1
        shapes = sorted({json.dumps(v) for v in inv_results.values()})
        rec = {"chain": r["chain"], "g": g, "gamma_cosets": n,
               "|P|": len(fr.P),
               "l234_rows_nonvanishing_in_Z[Gamma\\Q]": dead234,
               "C2_generic_block": {"free": free_coker[0],
                                    "torsion": free_coker[1]},
               "generic_d2_is_1": free_coker == (1, []),
               "involutions_in_P": len(inv_results),
               "C2_self_inverse_shapes": shapes,
               "self_inverse_d2_is_1": shapes in ([], ['[0, [2]]']),
               "concrete_blocks_checked": len(zs),
               "concrete_mismatches": mism}
        rec["passed"] = (rec["generic_d2_is_1"] and rec["self_inverse_d2_is_1"]
                         and mism == 0 and dead234 == 0)
        ok = ok and rec["passed"]
        out.append(rec)
        print(json.dumps(rec))
    summ = {"chains": len(out),
            "generic_d2_is_1": sum(1 for o in out if o["generic_d2_is_1"]),
            "self_inverse_d2_is_1": sum(1 for o in out
                                        if o["self_inverse_d2_is_1"]),
            "concrete_mismatches": sum(o["concrete_mismatches"] for o in out),
            "gamma_cosets": sorted({o["gamma_cosets"] for o in out}),
            "C2_generic_shapes": sorted({json.dumps(o["C2_generic_block"])
                                         for o in out}),
            "all_passed": ok and bool(out),
            "verdict": ("D2_IS_1_FOR_EVERY_DISPLACEMENT_CLASS" if ok and out
                        else "MIXED")}
    print(json.dumps({"summary": summ}))
    _dump(args, "uniform", summ, out)
    return 0 if summ["all_passed"] else 2


def has_c_loop(folded):
    """does the Stallings core of Gamma have a c-fixed vertex?

    An involution of Q = C2 * Z is a conjugate p c p^-1 (finite subgroups of
    a free product are conjugate into a factor), and p c p^-1 lies in Gamma
    exactly when the path spelling p ends at a vertex whose c-edge is a
    loop.  So this predicate decides whether Gamma has torsion.
    """
    return any(s in folded.cm and folded.find(folded.cm[s]) == s
               for s in folded.states())


def torsion_scan(fr, zs, us):
    """(count, [(z, u)]) of 2-torsion classes found over a ball of u.

    Works for finite and infinite index alike: a class is 2-torsion exactly
    when its reversal is the same class, which is a property of (state, z).
    """
    n, hits, seen = 0, [], set()
    for z in zs:
        for u in us:
            gen, _sg, t = signed_gen(fr, fr.trace(u), z)
            if t and (z, gen) not in seen:
                seen.add((z, gen))
                n += 1
                hits.append((z, u))
    return n, hits


def mode_torsion(args, rows):
    """Is A_2 free?  Census + POSITIVE control that the torsion path fires.

    A_2 = (Lambda^2 M)_Gamma has a Z/2 summand exactly at the orbits some
    gamma in Gamma reverses, and such a gamma is forced to be an INVOLUTION
    (gamma = v h u^-1 with z h z in H gives gamma^2 = 1; an element of order
    4 does not exist in C2 * Z).  So the torsion is nonempty iff Gamma has
    torsion iff its Stallings core has a c-fixed vertex.  The control is
    Gamma' = <R, U, w, c>, which contains the involution c by construction:
    the torsion classes MUST appear there and each MUST ship an explicit
    verified gamma-swap witness.
    """
    zs = z_family(args.zk, args.zn)[:args.zmax]
    sel = rows
    if args.chains:
        a, b = args.chains.split(":")
        sel = sel[int(a or 0):int(b or len(sel))]
    out, ok = [], True
    n_loop, n_ctl_ok = 0, 0
    for r in sel:
        ch, g, folded, fr, ops, _d, _h = setup(r)
        loop = has_c_loop(folded)
        n_loop += int(loop)
        us = [LV.to_tuple(w) for w in IIL.reduced_words(args.radius)]
        real_tor = torsion_scan(fr, zs, us)[0]
        # POSITIVE control: Gamma' = Gamma + <c> has torsion by construction
        gens2 = GS.gamma_gens(ch, g) + ["c"]
        f2 = GS.Folded(gens2)
        fr2 = Frame(gens2, f2.complete())
        ctl_loop = has_c_loop(f2)
        ctl_tor, hits = torsion_scan(fr2, zs, us)
        ctl_wit, ctl_missing = 0, 0
        for z, u in hits:
            gam = swap_witness(f2, u, z)
            if gam is None:
                ctl_missing += 1
            else:
                ctl_wit += 1
        rec = {"chain": r["chain"], "g": g,
               "finite_index": fr.finite,
               "gamma_core_has_c_loop": loop,
               "gamma_has_torsion": loop,
               "torsion_gens_real": real_tor,
               "control_gamma_plus_c_index_finite": fr2.finite,
               "control_core_has_c_loop": ctl_loop,
               "control_torsion_gens": ctl_tor,
               "control_swap_witnesses": ctl_wit,
               "control_swap_witnesses_missing": ctl_missing}
        rec["control_fired"] = (ctl_loop and ctl_tor > 0
                                and ctl_missing == 0)
        rec["passed"] = (rec["control_fired"]
                         and (real_tor == 0) == (not loop))
        n_ctl_ok += int(rec["control_fired"])
        ok = ok and rec["passed"]
        out.append(rec)
        print(json.dumps(rec))
    summ = {"chains": len(out),
            "chains_with_gamma_torsion": n_loop,
            "torsion_gens_real_total": sum(o["torsion_gens_real"]
                                           for o in out),
            "control_fired": n_ctl_ok,
            "control_torsion_gens": sum(o["control_torsion_gens"]
                                        for o in out),
            "control_swap_witnesses": sum(o["control_swap_witnesses"]
                                          for o in out),
            "control_swap_witnesses_missing": sum(
                o["control_swap_witnesses_missing"] for o in out),
            "all_passed": ok and bool(out),
            "verdict": ("A2_IS_FREE_NO_LAYER2_TORSION" if n_loop == 0
                        else "SOME_CHAIN_CARRIES_LAYER2_TORSION")}
    print(json.dumps({"summary": summ}))
    _dump(args, "torsion", summ, out)
    return 0 if summ["all_passed"] else 2


def mode_inf(args, rows):
    """The 23 infinite-index chains, with the W2h margin discipline.

    The uniform reduction of --mode uniform is index-free: in the block of z
    the generators are Gamma\\Q and the row of L_r^(2) is

        sum_g a_{r,g} e_{sigma(g) . u}   in  Z[Gamma\\Q],

    with no z in it.  So for every displacement class D != D^-1 the layer-2
    question is exactly W2h's layer-1 question run one level finer -- on
    Gamma\\Q (the completed Stallings graph) instead of Omega = Gamma\\Q/<c>.
    Gamma\\Q is infinite here, so the same discipline applies: a ball of u
    gives a lattice, coverage of the state differences [s] - [base] is
    measured per depth, and the margin L - (fully covered depth) is the
    honest statistic.  A negative answer at radius L is "not found at this
    radius", never death.

    The self-inverse classes D = D^-1 are handled concretely per z, since
    the reversal involution does depend on z.
    """
    Ls = [int(x) for x in args.radii.split(",")]
    zs = [z for z in z_family(args.zk, args.zn)[:args.zmax] if dclass(z)[1]]
    out, ok = [], True
    for r in sel_rows(rows, args, False):
        ch, g, folded, fr, ops, _d, _h = setup(r)
        sig = sigma_map(fr, ops)
        base = fr.base
        rec = {"chain": r["chain"], "g": g, "n_core": fr.cp.n_core,
               "levels": [], "self_inverse_blocks": []}
        dead234 = 0
        st_shape = {i: [(sig[i][gw], 1) for gw in ops[i]] for i in (0, 1)}
        for L in Ls:
            t0 = time.time()
            us = [LV.to_tuple(w) for w in
                  IIL.word_family(fr.cp, st_shape, L, args.align)]
            rws, per = {}, {}
            for u in us:
                for i in range(5):
                    acc = {}
                    for gw, a in ops[i].items():
                        acc[fr.walk(sig[i][gw], u)] = acc.get(
                            fr.walk(sig[i][gw], u), 0) + a
                    acc = {k: v for k, v in acc.items() if v}
                    if i >= 2:
                        dead234 += int(bool(acc))
                    elif acc:
                        rws[(i, tuple(sorted(acc.items())))] = acc
            Z = IIL.ZEchelon(order=lambda c: (-len(c[1]), c[0], c[1]))
            for tag, row in rws.items():
                Z.add(row, tag)
            states = {s for row in rws.values() for s in row}
            for s in states:
                d = len(s[1])
                okc = True if s == base else Z.member({s: 1, base: -1})[0]
                a, b = per.get(d, (0, 0))
                per[d] = (a + int(okc), b + 1)
            full = -1
            for d in sorted(per):
                if per[d][0] == per[d][1]:
                    full = d
                else:
                    break
            rec["levels"].append({
                "L": L, "rows": len(rws), "pivots": len(Z.piv),
                "states_reached": len(states),
                "state_differences_covered_up_to_depth": full,
                "margin": L - full,
                "covered": sum(v[0] for v in per.values()),
                "total": sum(v[1] for v in per.values()),
                "depth_profile": {str(d): list(per[d]) for d in sorted(per)},
                "secs": round(time.time() - t0, 2)})
        margins = {lv["margin"] for lv in rec["levels"]}
        rec["margin_constant"] = len(margins) == 1
        rec["margins"] = sorted(margins)
        rec["coverage_growth"] = [
            [lv["L"], lv["state_differences_covered_up_to_depth"]]
            for lv in rec["levels"]]
        rec["l234_rows_nonvanishing"] = dead234
        # the self-inverse displacement classes, concretely
        us = [LV.to_tuple(w) for w in IIL.reduced_words(Ls[-1])]
        for z in zs[:args.zmax]:
            gens, tor, rws2 = [], set(), []
            gset = set()
            for u in us:
                for i in (0, 1):
                    acc = {}
                    for gw, a in ops[i].items():
                        st = fr.walk(sig[i][gw], u)
                        gg, sgn, tt = signed_gen(fr, st, z)
                        if gg not in gset:
                            gset.add(gg)
                            gens.append(gg)
                        if tt:
                            tor.add(gg)
                        acc[gg] = acc.get(gg, 0) + a * sgn
                    acc = {k: a for k, a in acc.items() if a}
                    if acc:
                        rws2.append(acc)
            Z2 = IIL.ZEchelon(order=lambda c: c)
            for j, row in enumerate(rws2):
                Z2.add(row, j)
            dplus = dclass(z)[0]
            g0 = gens[0]
            cov = sum(1 for gg in gens[1:]
                      if Z2.member({gg: xi_sign(g0[0][1], dplus),
                                    g0: -xi_sign(gg[0][1], dplus)})[0])
            rec["self_inverse_blocks"].append({
                "z": LV.literal(z), "gens_reached": len(gens),
                "torsion_gens": len(tor), "rows": len(rws2),
                "xi_kernel_directions": len(gens) - 1, "covered": cov})
        ok = ok and dead234 == 0
        rec["torsion_gens_total"] = sum(b["torsion_gens"]
                                        for b in rec["self_inverse_blocks"])
        out.append(rec)
        print(json.dumps({k: v for k, v in rec.items()
                          if k not in ("levels", "self_inverse_blocks")}))
    summ = {"chains": len(out), "radii": Ls,
            "l234_rows_nonvanishing": sum(o["l234_rows_nonvanishing"]
                                          for o in out),
            "margin_constant": sum(1 for o in out if o["margin_constant"]),
            "margins": sorted({m for o in out for m in o["margins"]}),
            "torsion_gens_total": sum(o["torsion_gens_total"] for o in out),
            "coverage_growth": [o["coverage_growth"] for o in out],
            "controls_passed": ok and bool(out),
            "note": "Gamma\\Q is infinite here, so a ball of u reaches only "
                    "finitely many states; the margin L - covered_depth is "
                    "the statistic, and a miss at radius L is a truncation "
                    "statement, never a death certificate"}
    print(json.dumps({"summary": summ}))
    _dump(args, "inf", summ, out)
    return 0 if summ["controls_passed"] else 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("identity", "lambda1", "d2",
                                       "probe", "torsion", "uniform",
                                       "inf"), default="identity")
    ap.add_argument("--radius", type=int, default=5)
    ap.add_argument("--radii", type=str, default="4,5,6",
                    help="comma-separated |u| ceilings for --mode inf")
    ap.add_argument("--align", type=int, default=0,
                    help="radius of W2h's aligned word family (0 = ball)")
    ap.add_argument("--zk", type=int, default=2, help="max c-blocks in z")
    ap.add_argument("--zn", type=int, default=2, help="max |t-exponent| in z")
    ap.add_argument("--zmax", type=int, default=24)
    ap.add_argument("--chains", type=str, default="")
    ap.add_argument("--stratum-only", action="store_true")
    ap.add_argument("--detail", action="store_true")
    ap.add_argument("--json", type=str, default="")
    args = ap.parse_args()

    c1 = LV.analyze(PS.WITNESS, fixed_h=PS.CODEX_H)
    got = (c1["defect_terms"], c1["defect_l1"], c1["defect_augmentation"])
    print(json.dumps({"control": "fixed_h_witness", "defect": list(got),
                      "want": [21, 48, 0], "passed": got == (21, 48, 0)}))
    if got != (21, 48, 0):
        return 2

    rows = GS.load_rows()
    return {"identity": mode_identity, "lambda1": mode_lambda1,
            "d2": mode_d2, "probe": mode_probe,
            "torsion": mode_torsion, "uniform": mode_uniform,
            "inf": mode_inf}[args.mode](args, rows)


if __name__ == "__main__":
    sys.exit(main())
