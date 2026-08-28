"""W2m: the translation cocycle of the canonical section, and what it does
(and does NOT) do for the layer-2 attainability question.

W2K section 12 and W2L section 12 name one missing lemma as the fork of the
whole W2 chain:

    "`g sigma(x) g^-1 = sigma(g.x) kappa(g,x)` with `kappa(g,x) in [N,N]`, and
     `Theta(kappa(g,x))` is a bilinear correction in `(g,x)`.  If that cocycle
     can be written down, then `lambda(g.F)` is `g.lambda(F)` plus an explicit
     term, `V_{H_fin}` becomes a module with finitely many generators up to
     the `Q`-action, and both branches of Lemma C become decidable on the
     complete family."

This checker writes the cocycle down (it is PROVED, in closed form, and
machine-verified here), and then shows that the *consequence* conjectured
above is FALSE, for a reason the conjecture never checked.

--------------------------------------------------------------------------
0. CONVENTIONS (W2l's, adopted verbatim)
--------------------------------------------------------------------------
`Q = <c,t | c^2>`, `F = F(c,t)`, `N = ker(F -> Q)`, `M = N_ab = Z[X]` with
`X = Q/<c>` (hypothesis (3.1): `N` is free on the Schreier basis
`r_v = v c^2 v^-1`, `v in X`).  `sigma(y) = prod_v r_v^{y_v}` in SHORTLEX
order of `v` -- literally `lift.lift_module_vector`, unmodified.

`Theta` is `esc.degree_two(esc.schreier_word(.))`, unmodified.  On a word it
is the UPPER-TRIANGULAR part of the ordered degree-two tensor; on `[N,N]`
that is the class in `gamma_2 N / gamma_3 N = Lambda^2 M`, and it satisfies

    Theta(ab) = Theta(a) + Theta(b) + UT([a] (x) [b]) ,
    UT(p (x) q)_{v<w} = p_v q_w ,   Theta(a^-1) = -Theta(a) + UT([a](x)[a]).

Order convention: `v < w` means `(len(v), v) < (len(w), w)` on the integer
tuple -- the same key `lift.lift_module_vector` sorts by and the same key
`esc.degree_two` antisymmetrises by.  `Theta([r_a, r_b]) = +e_a ^ e_b` for
`a < b` (control K3 of `theta_residual_evaluator`, re-run here as L0).

The cocycle uses W2l section 12's own order:

    kappa(g, y) := sigma(g.y)^-1 . g sigma(y) g^-1  ,   g in F(c,t).

`[kappa] = -(g.y) + g.[sigma(y)] = 0`, so `kappa in [N,N]` unconditionally --
which is asserted literally on every evaluation, not assumed.

--------------------------------------------------------------------------
1. THE LEMMA (proved; verified by mode `lemma`)
--------------------------------------------------------------------------
For `g in F(c,t)` and a vertex `v in X` write `u = g.v` (the left action on
`X`), and `eps(g,v) in {0,1}` for the exponent with `g v = u c^eps` in `Q`.
Put

    n(g,v) := g v c^-eps u^-1   in  N ,       nu(g,v) := [n(g,v)] in M.     (1)

Then, LITERALLY in `F(c,t)`,

    g r_v g^-1 = n(g,v) . r_{g.v} . n(g,v)^-1                              (2)

and therefore, for every finitely supported `y in M`,

    Theta(kappa(g,y))
      =  SUM_v  y_v  ( nu(g,v) ^ e_{g.v} )                       [LINEAR]
       -  SUM_{v<w, g.w < g.v}  y_v y_w ( e_{g.w} ^ e_{g.v} )    [BILINEAR] (3)

-- an inhomogeneous quadratic form in `y` whose linear part is the
conjugation defect (1) and whose quadratic part is supported exactly on the
INVERSION SET of the shortlex order under left translation by `g`.  Its
polarisation is bilinear in `(y,y')` and depends only on `g` and the pair of
vertices, so it is computable without any free-group work once (1) is known.

`kappa` is a genuine (nonabelian) 1-cocycle,

    kappa(gh, y) = kappa(g, h.y) . g kappa(h,y) g^-1 ,
    Theta(kappa(gh,y)) = Theta(kappa(g,h.y)) + g . Theta(kappa(h,y)) ,      (4)

with `g.` the diagonal action (3.4) (`theta_residual_evaluator.act_wedge`).

Both (2), (3) and (4) are checked here on literal free-group elements, with
corruption controls that fire.

--------------------------------------------------------------------------
2. WHY IT DOES NOT DECIDE LAYER 2 (mode `action`, mode `ladder`)
--------------------------------------------------------------------------
The conjectured consequence needs a `Q`-action on `H_fin = ker(L)`.  There is
none.  `L_r` is LEFT multiplication by `lambda_r in Z[Q]` on `M = Z[Q/<c>]`;
left multiplication by `g` commutes with it only if `g lambda_r = lambda_r g`
for every `r`.  Mode `action` measures both halves:

  * `g.F` for `F in H_fin` and `g` a nontrivial group element: NOT in `H_fin`
    (measured, exhaustively over the tested directions and baselines);
  * the joint centralizer `{g : g lambda_r = lambda_r g, all r}` in `Q`:
    trivial on every baseline tested.

So there is no `Q`-action for `V_{H_fin}` to be "finitely generated over".
Worse for the conjecture, the target space cannot see one either:
`Xi_Z` is exactly diagonally `Q`-invariant (W2j control K4), because
`Xi_Z(e_v ^ e_w)` depends only on the double coset `H v^-1 w H`.  Hence
"finitely generated up to the `Q`-action" is, in `W_Q`, just "finitely
generated".

What DOES act is the Hecke algebra

    E := End_{Z[Q]}(M) = (Z[Q/H])^H = Z[ H \\ Q / H ] ,
    T_a(e_v) := e_{v a} + e_{v c a}          (a in Q, H = <c>)             (5)

acting on the RIGHT.  `T_a` commutes with every left multiplication, so
`T_a(H_fin) subset H_fin` -- proved, and verified exactly here with
`infinite_index_liveness.verify` on real directions, against a CORRUPTED
Hecke operator (`e_v |-> e_{va}` only) that must leave `H_fin`.

`T_a` is not a permutation of the basis, and `Theta . sigma` (an ordered
product) is functorial only for order-preserving basis permutations, so the
cocycle (3) says nothing about `Theta(T_a F)`.  The Hecke action is therefore
a *generator of provably valid new elements of `H_fin`*, not a symmetry of
`Theta` -- and that is exactly what settles F3 in the negative.

--------------------------------------------------------------------------
3. F3 IS FALSE (mode `ladder`, mode `growth`)
--------------------------------------------------------------------------
W2l section 6.1 reported the direction generator SATURATING on census chain 7
at 20 directions, `rank V = 63`, universe 556, residual `{z_TT}`, unchanged
under eight far-translate seed families.  That is reproduced here as the
calibration.  Feeding the SAME baseline the Hecke translates `T_a` of a
handful of native directions -- every one of them verified in `H_fin` --
takes `rank V` far past 63 and the coordinate universe far past 556.  So
`V_S != V_{H_fin}` at W2l's saturated `S`: the saturation was a property of
`kernel_directions`, not of `H_fin`.

Mode `growth` makes the refutation effective rather than empirical: for
`a = t^k`, the cross generator `b(F, T_a F)` carries `Xi_Z` coordinates whose
double-coset length grows with `k`, so infinitely many pairwise distinct
coordinates occur and `rank V_{H_fin} = infinity`.

--------------------------------------------------------------------------
4. CONTROLS (each can fail; a failure sets exit 2 and voids the run)
--------------------------------------------------------------------------
  L0  the imported Theta is the codex one: `Theta([r_a,r_b]) = e_a ^ e_b`.
  L1  every `kappa` lands in `[N,N]` literally (`relation_module == {}`), and
      a CORRUPTED section (one exponent bumped) must leave it.
  L2  identity (2) holds for every tested `(g,v)`, and a corrupted `n(g,v)`
      must break it.
  L3  the closed form (3) matches `Theta(kappa)` exactly, and a corrupted
      closed form must mismatch.
  L4  the cocycle identity (4).
  L5  `T_a F` is in `H_fin` exactly, and the corrupted Hecke operator must
      leave it.
  L6  the model / direction / x0 controls of `theta_attainability.analyse`
      (C2, C3, C4, C4b, C5, C8, C9) are inherited unchanged.
  C1  the imported lifting calculus is the codex one: defect (21,48,0).

HYPOTHESES INHERITED (nothing here re-derives them)
  (3.1) `N` is free on the Schreier generators `(r_v)`.
  (3.5) the second-layer variation operator carries the same integral
        coefficients as `L_r`; every reading of `Xi_Z(Theta) = 0` as
        "layer 2 is solvable" is conditional on it (and through W2i on that
        note's `d_2 = 1`).  Nothing in this file depends on (3.5): the
        cocycle, the Hecke action and the rank ladder are statements about
        the literal free-group residual and the operators alone.

EXIT CODES
  0  run completed, every control green (a verdict is a RESULT, not a failure)
  2  a control failed -- the run is void
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
sys.path.insert(0, str(HERE))

_ARGV = list(sys.argv)
sys.argv = sys.argv[:1]
import theta_attainability as TA  # noqa: E402
sys.argv = _ARGV

TR, IL, GS, PS, LV = TA.TR, TA.IL, TA.GS, TA.PS, TA.LV
lift, esc = TA.lift, TA.esc

QM, QI, QR, CV = (lift.quotient_multiply, lift.quotient_inverse,
                  lift.quotient_reduce, lift.c_vertex)
C, T = lift.C, lift.T
OUT = HERE / "out"


def key(v):
    """The shortlex order both `lift_module_vector` and `degree_two` use."""
    return (len(v), v)


def word(s):
    a = {"c": C, "C": -C, "t": T, "T": -T}
    return tuple(a[ch] for ch in s)


# ------------------------------------------------------- the section side


def sigma(y):
    return lift.lift_module_vector(y)


def act_vec(gq, y):
    out = {}
    for v, k in y.items():
        u = CV(QM(gq, v))
        out[u] = out.get(u, 0) + k
    return {k: v for k, v in out.items() if v}


def kappa(gw, y):
    """kappa(g,y) = sigma(g.y)^-1 . g sigma(y) g^-1  (W2l section 12 order)."""
    return lift.multiply(lift.inverse(sigma(act_vec(QR(gw), y))),
                         lift.conjugate(sigma(y), gw))


def theta_of(w):
    """Theta on an element of [N,N] -- the unmodified codex primitives."""
    return esc.degree_two(esc.schreier_word(w))


def wedge_add(acc, a, b, co):
    if a == b or not co:
        return
    if key(a) < key(b):
        acc[(a, b)] = acc.get((a, b), 0) + co
    else:
        acc[(b, a)] = acc.get((b, a), 0) - co


def n_of(gw, v, corrupt=False):
    """(n(g,v), g.v) with  g r_v g^-1 = n r_{g.v} n^-1;  n = g v c^-eps u^-1.

    NOTE on the eps ambiguity: `c` commutes with `c^2`, so replacing eps by
    1 - eps gives the SAME conjugate -- flipping it is not a corruption and
    must not be used as one.  The corruption used by control L2 multiplies
    `n` by a relation generator at a DIFFERENT vertex, which leaves the
    centralizer `<r_{g.v}>` of the conjugated element and therefore must
    break (2).
    """
    gv = QM(QR(gw), v)
    u = CV(gv)
    eps = 1 if (gv and abs(gv[-1]) == C) else 0
    n = lift.multiply(gw, v, lift.inverse(lift.power(C, eps)),
                      lift.inverse(u))
    if corrupt:
        bad_v = next(x for x in (CV(word("t")), CV(word("T")), CV(word("tt")))
                     if x != u)
        n = lift.multiply(n, lift.relation_generator(bad_v))
    return n, u


def nu(gw, v):
    n, u = n_of(gw, v)
    return lift.relation_module(n), u


def predict_parts(gw, y):
    """(linear part, bilinear part) of the closed form (3), separately."""
    gq = QR(gw)
    lin, bil = {}, {}
    for v, yv in y.items():
        p, u = nu(gw, v)
        for a, pa in p.items():
            wedge_add(lin, a, u, yv * pa)
    vs = sorted(y, key=key)
    for i in range(len(vs)):
        for j in range(i + 1, len(vs)):
            v, w = vs[i], vs[j]
            gv, gwv = CV(QM(gq, v)), CV(QM(gq, w))
            if key(gwv) < key(gv):
                wedge_add(bil, gwv, gv, -y[v] * y[w])
    return ({k: c for k, c in lin.items() if c},
            {k: c for k, c in bil.items() if c})


def predict(gw, y):
    lin, bil = predict_parts(gw, y)
    return TR._lin((1, lin), (1, bil))


def reorder_element(gw, y):
    """R(g,y) := sigma(g.y)^-1 . PROD_v r_{g.v}^{y_v}  (v in the order of X).

    The second factor is `sigma(g.y)` written in the g-PULLED-BACK order, so
    `[R] = 0` and `R in [N,N]`; `Theta(R)` isolates the pure REORDERING half
    of the cocycle -- the inversion form -- with the conjugation defect (1)
    absent.  It is what grounds the direction-translation law

        Theta_sigma(g.y) = g . Theta_sigma(y) - 2 Theta(R(g,y))              (6)

    in the free group instead of in a formula.
    """
    gq = QR(gw)
    prod = ()
    for v in sorted(y, key=key):
        prod = lift.multiply(prod, lift.power_word(
            lift.relation_generator(CV(QM(gq, v))), y[v]))
    return lift.multiply(lift.inverse(sigma(act_vec(gq, y))), prod)


# ------------------------------------------------------- the Hecke action


def hecke(a, f, corrupt=False):
    """T_a(e_v) = e_{va} + e_{vca}  (5).  `corrupt` drops the second coset."""
    out = {}
    for v, k in f.items():
        pres = ((),) if corrupt else ((), (C,))
        for pre in pres:
            u = CV(QM(v, pre, a))
            out[u] = out.get(u, 0) + k
    return {k: v for k, v in out.items() if v}


def hecke_dir(a, F, corrupt=False):
    return [hecke(a, f, corrupt) for f in F]


def commutes(zq, op):
    l, r = {}, {}
    for gw, x in op.items():
        k = QM(zq, gw)
        l[k] = l.get(k, 0) + x
        k = QM(gw, zq)
        r[k] = r.get(k, 0) + x
    return ({k: v for k, v in l.items() if v}
            == {k: v for k, v in r.items() if v})


def centralizer_words(ops, maxlen):
    return [w for w in IL.reduced_words(maxlen)
            if all(commutes(QR(LV.to_tuple(w)), o) for o in ops)]


# ------------------------------------------------------ direction plumbing


def ser_dir(F):
    return [sorted((lift.literal(v), a) for v, a in f.items()) for f in F]


def deser_dir(S):
    return [{lift.parse_quotient(s): a for s, a in f} for f in S]


def dir_key(F):
    return tuple(tuple(sorted(f.items())) for f in F)


def hecke_close(ops, dirs, words, corrupt=False):
    """T_a translates of `dirs`, each verified exactly against `H_fin`."""
    extra, bad, seen = [], 0, {dir_key(F) for F in dirs}
    for s in words:
        a = QR(LV.to_tuple(s))
        for F in dirs:
            F2 = hecke_dir(a, F, corrupt)
            if not any(F2):
                continue
            if IL.verify({}, ops, F2):
                bad += 1
                continue
            k = dir_key(F2)
            if k in seen:
                continue
            seen.add(k)
            extra.append(F2)
    return extra, bad


def flat_dir(F):
    return {(i, v): a for i, f in enumerate(F) for v, a in f.items() if a}


def lattice_growth(base_dirs, new_dirs):
    """How many of `new_dirs` are OUTSIDE the Z-span of `base_dirs`.

    Independent of the `Xi_Z` side entirely: it is a statement about
    `H_fin` itself, so it confirms the rank growth of `V` by a second route.
    """
    Z = IL.ZEchelon(order=lambda c: (c[0], len(c[1]), c[1]))
    for i, F in enumerate(base_dirs):
        Z.add(flat_dir(F), i)
    out = 0
    for F in new_dirs:
        member, _c = Z.member(flat_dir(F))
        if not member:
            out += 1
            Z.add(flat_dir(F), ("new", out))
    return out


def hecke_commutation_control(ops, args, rng):
    """T_a . (left mult by lambda) == (left mult by lambda) . T_a, and a
    CORRUPTED T_a (one coset dropped) must break it on some probe."""
    verts = [CV(LV.to_tuple(s)) for s in ("", "t", "T", "ct", "tc", "tt")]
    n = n_ok = nc = nc_fire = 0
    for s in [w for w in args.hecke.split(",") if w]:
        a = QR(LV.to_tuple(s))
        for op in ops:
            for v in verts:
                f = {v: 1}
                n += 1
                n_ok += int(hecke(a, lift.apply_operator(op, f))
                            == lift.apply_operator(op, hecke(a, f)))
                nc += 1
                nc_fire += int(hecke(a, lift.apply_operator(op, f), True)
                               != lift.apply_operator(
                                   op, hecke(a, f, True)))
    return n, n_ok, nc, nc_fire


def sub_args(args, m, **kw):
    ns = argparse.Namespace(
        m=m, kernel_rho=args.kernel_rho, holdout=args.holdout, box=2,
        points=50, cap_bits=args.cap_bits, mod2_only=True, pair_sample=0,
        elim_cap=args.elim_cap, window=list(args.window), rhos=list(args.rhos),
        far_shifts=args.far_shifts, m_far=args.m_far, no_source_dirs=False,
        detail=False)
    for k, v in kw.items():
        setattr(ns, k, v)
    return ns


STEP_KEYS = ("directions", "status", "model_verified", "universe_coords",
             "mod2_V_rank", "mod2_residual_weight", "mod2_residual_support",
             "mod2_residual_order_invariant", "c0_support", "cross_pairs",
             "cross_pairs_odd", "evaluations", "minus_c0_in_V",
             "coordinate_certificates", "mod2_classes_enumerated",
             "mod2_distinct_values", "mod2_enumeration_truncated",
             "mod2_zero_class", "C9_positive_control_fires",
             "no_mod2_linear_certificate", "passed")


# --------------------------------------------------------------- mode L


def mode_lemma(args, rows):
    """(a) the cocycle: (2), (3), (4), with corruption controls."""
    rng = random.Random(20260828)
    verts = sorted({CV(word(s)) for s in
                    ("", "t", "T", "c", "ct", "cT", "tc", "Tc", "tt", "TT",
                     "ctc", "ctt", "cTT", "tct", "TcT", "tcT", "ttc", "ttt",
                     "TTT", "tcTc", "cttc")}, key=key)
    gs_list = [s for s in args.gwords.split(",") if s]

    # ---- L0: the imported Theta is the codex one
    l0 = 0
    for a in verts[:5]:
        for b in verts[:5]:
            if a == b:
                continue
            w = lift.multiply(lift.relation_generator(a),
                              lift.relation_generator(b),
                              lift.inverse(lift.relation_generator(a)),
                              lift.inverse(lift.relation_generator(b)))
            want = {(a, b): 1} if key(a) < key(b) else {(b, a): -1}
            l0 += int(theta_of(w) == want)
    n_l0 = len(verts[:5]) * (len(verts[:5]) - 1)

    # ---- L2: identity (2), and a corrupted n(g,v) must break it
    n2 = n2_ok = n2c = n2c_fire = 0
    for s in gs_list:
        gw = word(s)
        for v in verts:
            n, u = n_of(gw, v)
            lhs = lift.conjugate(lift.relation_generator(v), gw)
            n2 += 1
            n2_ok += int(lhs == lift.conjugate(lift.relation_generator(u), n))
            nb, ub = n_of(gw, v, corrupt=True)
            n2c += 1
            n2c_fire += int(lhs != lift.conjugate(
                lift.relation_generator(ub), nb))

    # ---- L1/L3: kappa in [N,N], and the closed form
    ys = []
    for _ in range(args.samples):
        k = rng.randint(1, 4)
        sup = rng.sample(verts, k)
        ys.append({v: rng.choice([-2, -1, 1, 1, 2, 3]) for v in sup})
    # real chain data: x_0 components and kernel directions of a few chains
    real = 0
    for r in TA._slice(rows, args.chains)[:args.real_chains]:
        ch, g, ops, defect, h, _sh = TR.setup(r, tuple(args.window))
        sol = TR.solve_layer1(ops, defect, tuple(args.rhos))
        if not sol["ok"]:
            continue
        cp = IL.Completed(GS.Folded(GS.gamma_gens(ch, g)))
        ds = TR.kernel_directions(ops, defect, 3, args.kernel_rho, cp=cp)
        for vec in [xi for xi in sol["x"] if xi] + \
                   [f for F in ds for f in F if f]:
            ys.append(dict(vec))
            real += 1
    n1 = n1_ok = n1c = n1c_fire = 0
    n3 = n3_ok = n3c = n3c_fire = 0
    n_lin = n_bil = 0
    n_nonzero = n_even = n_xi_zero = 0
    for s in gs_list:
        gw = word(s)
        for y in ys:
            kap = kappa(gw, y)
            n1 += 1
            if lift.relation_module(kap):
                continue
            n1_ok += 1
            th = theta_of(kap)
            lin, bil = predict_parts(gw, y)
            n3 += 1
            n3_ok += int(th == predict(gw, y))
            assert predict(gw, y) == TR._lin((1, lin), (1, bil))
            # L3 corruption, counted ONLY when the dropped piece is nonzero
            # (a guard that cannot fire is not a control)
            if lin:
                n_lin += 1
                n3c += 1
                n3c_fire += int(TR._lin((1, bil)) != th)
            if bil:
                n_bil += 1
                n3c += 1
                n3c_fire += int(TR._lin((1, lin)) != th)
            if th:
                n_nonzero += 1
                n_even += int(all(x % 2 == 0 for x in th.values()))
                fr, to = TR.xi_z(th)
                n_xi_zero += int(TR.xi_is_zero(fr, to))
            # L1 corruption: a bumped section exponent must leave [N,N]
            if n1c < args.corrupt_n:
                bad = dict(y)
                kk = sorted(bad, key=key)[0]
                bad[kk] += 1
                n1c += 1
                kb = lift.multiply(
                    lift.inverse(sigma(act_vec(QR(gw), y))),
                    lift.conjugate(sigma(bad), gw))
                n1c_fire += int(bool(lift.relation_module(kb)))

    # ---- L7: the pure reordering half, grounded in F(c,t)  (6)
    n7 = n7_ok = n7_nz = 0
    for s in gs_list:
        gw = word(s)
        for y in ys:
            R = reorder_element(gw, y)
            if lift.relation_module(R):
                continue
            _lin_p, bil = predict_parts(gw, y)
            n7 += 1
            n7_ok += int(theta_of(R) == bil)
            n7_nz += int(bool(bil))

    # ---- L4: the cocycle identity (4)
    n4 = n4_ok = 0
    for s1 in gs_list[:args.pair_words]:
        for s2 in gs_list[:args.pair_words]:
            g1, g2 = word(s1), word(s2)
            g12 = lift.multiply(g1, g2)
            for y in ys[:args.cocycle_ys]:
                lhs = theta_of(kappa(g12, y))
                rhs = TR._lin(
                    (1, theta_of(kappa(g1, act_vec(QR(g2), y)))),
                    (1, TR.act_wedge(QR(g1), theta_of(kappa(g2, y)))))
                n4 += 1
                n4_ok += int(lhs == rhs)

    summ = {
        "L0_theta_is_codex": f"{l0}/{n_l0}",
        "L2_conjugation_identity": f"{n2_ok}/{n2}",
        "L2_corruption_fires": f"{n2c_fire}/{n2c}",
        "L1_kappa_in_commutator": f"{n1_ok}/{n1}",
        "L1_corruption_fires": f"{n1c_fire}/{n1c}",
        "L3_closed_form": f"{n3_ok}/{n3}",
        "L3_corruption_fires": f"{n3c_fire}/{n3c}",
        "evaluations_with_nonzero_linear_part": n_lin,
        "evaluations_with_nonzero_bilinear_part": n_bil,
        "L4_cocycle_identity": f"{n4_ok}/{n4}",
        "L7_reordering_half_grounded": f"{n7_ok}/{n7}",
        "L7_nonvacuous_cases": n7_nz,
        "group_words": gs_list, "vertices": len(verts),
        "y_samples": len(ys), "y_from_real_chain_data": real,
        "theta_kappa_nonzero": n_nonzero,
        "theta_kappa_2_divisible": n_even,
        "xi_z_of_theta_kappa_zero": n_xi_zero,
        "controls_passed": bool(
            l0 == n_l0 and n2 == n2_ok and n2c == n2c_fire
            and n1 == n1_ok and n1c == n1c_fire and n3 == n3_ok
            and n3c == n3c_fire and n4 == n4_ok and n7 == n7_ok
            and n7_nz and n1 and n3 and n4),
    }
    print(json.dumps(summ, indent=1), flush=True)
    _dump(args, "lemma", summ, [])
    return 0 if summ["controls_passed"] else 2


# --------------------------------------------------------------- mode A


def mode_action(args, rows):
    """(b0) which group acts on H_fin: Q (no), the Hecke algebra E (yes)."""
    sel = TA._slice(rows, args.chains)
    done = _resume(args)
    out, ok = list(done.values()), True
    t_run = time.time()
    qwords = [s for s in args.gwords.split(",") if s]
    hwords = [s for s in args.hecke.split(",") if s]
    for r in sel:
        if tuple(r["chain"]) + (r["g_gen"],) in done:
            continue
        if args.run_seconds and time.time() - t_run > args.run_seconds:
            break
        ch, g, ops, defect, h, _sh = TR.setup(r, tuple(args.window))
        sol = TR.solve_layer1(ops, defect, tuple(args.rhos))
        rec = {"chain": r["chain"], "g": r["g_gen"]}
        if not sol["ok"]:
            rec["status"] = "LAYER1_UNSOLVED_AT_RHO"
            rec["passed"] = True
            out.append(rec)
            print(json.dumps(rec), flush=True)
            continue
        cp = IL.Completed(GS.Folded(GS.gamma_gens(ch, g)))
        dirs = TR.kernel_directions(ops, defect, args.m, args.kernel_rho, cp=cp)
        rec["directions"] = len(dirs)
        rec["directions_exact"] = all(not IL.verify({}, ops, F) for F in dirs)
        # Q-translation
        nq = nq_in = 0
        for s in qwords:
            gq = QR(LV.to_tuple(s))
            if gq == ():
                continue
            for F in dirs:
                F2 = [act_vec(gq, f) for f in F]
                nq += 1
                nq_in += int(not IL.verify({}, ops, F2))
        rec["Q_translates_tested"] = nq
        rec["Q_translates_still_in_H_fin"] = nq_in
        # Hecke translation, and the corrupted Hecke operator (L5)
        nh = nh_in = nhc = nhc_out = 0
        for s in hwords:
            a = QR(LV.to_tuple(s))
            for F in dirs:
                F2 = hecke_dir(a, F)
                if any(F2):
                    nh += 1
                    nh_in += int(not IL.verify({}, ops, F2))
                F3 = hecke_dir(a, F, corrupt=True)
                if any(F3):
                    nhc += 1
                    nhc_out += int(bool(IL.verify({}, ops, F3)))
        rec["hecke_translates_tested"] = nh
        rec["hecke_translates_in_H_fin"] = nh_in
        rec["L5_corrupt_hecke_tested"] = nhc
        rec["L5_corrupt_hecke_leaves_H_fin"] = nhc_out
        nk, nk_ok, nkc, nkc_f = hecke_commutation_control(
            ops, args, random.Random(11))
        rec["hecke_commutation_checks"] = nk
        rec["hecke_commutation_ok"] = nk_ok
        rec["hecke_commutation_corruption_tested"] = nkc
        rec["hecke_commutation_corruption_fires"] = nkc_f
        rec["centralizer_words"] = centralizer_words(ops, args.central_len)
        rec["passed"] = bool(rec["directions_exact"] and nh == nh_in
                             and (nhc == 0 or nhc_out > 0)
                             and nk == nk_ok and nkc_f
                             and rec["centralizer_words"] == [""])
        ok = ok and rec["passed"]
        out.append(rec)
        print(json.dumps(rec), flush=True)
        _dump(args, "action", {"partial": True, "chains": len(out)}, out)
    summ = {
        "chains": len(out),
        "with_directions": sum(1 for o in out if o.get("directions")),
        "Q_translates_tested": sum(o.get("Q_translates_tested", 0)
                                   for o in out),
        "Q_translates_still_in_H_fin": sum(
            o.get("Q_translates_still_in_H_fin", 0) for o in out),
        "hecke_translates_tested": sum(o.get("hecke_translates_tested", 0)
                                       for o in out),
        "hecke_translates_in_H_fin": sum(o.get("hecke_translates_in_H_fin", 0)
                                         for o in out),
        "L5_corrupt_hecke_tested": sum(o.get("L5_corrupt_hecke_tested", 0)
                                       for o in out),
        "L5_corrupt_hecke_leaves_H_fin": sum(
            o.get("L5_corrupt_hecke_leaves_H_fin", 0) for o in out),
        "hecke_commutation_checks": sum(
            o.get("hecke_commutation_checks", 0) for o in out),
        "hecke_commutation_ok": sum(o.get("hecke_commutation_ok", 0)
                                    for o in out),
        "hecke_commutation_corruption_fires": sum(
            o.get("hecke_commutation_corruption_fires", 0) for o in out),
        "chains_with_trivial_centralizer": sum(
            1 for o in out if o.get("centralizer_words") == [""]),
        "controls_passed": ok and bool(out)}
    print(json.dumps({"summary": summ}), flush=True)
    _dump(args, "action", summ, out)
    return 0 if summ["controls_passed"] else 2


# --------------------------------------------------------------- mode G


def mode_growth(args, rows):
    """F3 refuted EFFECTIVELY: new Xi_Z coordinates of unbounded length."""
    r = TA._slice(rows, args.chains)[0]
    ch, g, ops, defect, h, _sh = TR.setup(r, tuple(args.window))
    sol = TR.solve_layer1(ops, defect, tuple(args.rhos))
    if not sol["ok"]:
        print(json.dumps({"status": "LAYER1_UNSOLVED_AT_RHO"}))
        return 2
    cp = IL.Completed(GS.Folded(GS.gamma_gens(ch, g)))
    dirs = TR.kernel_directions(ops, defect, args.m, args.kernel_rho, cp=cp)
    if not dirs:
        print(json.dumps({"status": "NO_KERNEL_DIRECTION_FOUND"}))
        return 2
    dirs = dirs[:args.dirs_scan]

    def G(F_list, n):
        th, _w = TR.theta(h, TR.combine(sol["x"], F_list, n))
        return TR._vec(*TR.xi_raw(th))

    base = G([], [])
    rows_out, seen, seenZ, ok = [], set(), set(), True
    sups, supsZ = {}, {}
    for k in range(1, args.kmax + 1):
        a = QR(LV.to_tuple("t" * k))
        odd, full = set(), set()
        for F in dirs:
            F2 = hecke_dir(a, F)
            if not any(F2):
                continue
            exact = not IL.verify({}, ops, F2)
            ok = ok and exact
            pair = [F, F2]
            g10, g01, g11 = (G(pair, [1, 0]), G(pair, [0, 1]),
                             G(pair, [1, 1]))
            cross = TA.vlin((1, g11), (-1, g10), (-1, g01), (1, base))
            odd |= {kk for kk, v in cross.items() if v % 2}
            full |= set(cross)
        lens = sorted({len(nm) for _kind, nm in odd})
        lensZ = sorted({len(nm) for _kind, nm in full})
        rec = {"k": k, "hecke_word": "t" * k, "directions_paired": len(dirs),
               "cross_support_Z": len(full), "cross_odd_support": len(odd),
               "max_coordinate_length": max(lens) if lens else 0,
               "min_coordinate_length": min(lens) if lens else 0,
               "max_coordinate_length_Z": max(lensZ) if lensZ else 0,
               "min_coordinate_length_Z": min(lensZ) if lensZ else 0,
               "new_coordinates_vs_previous_k": len(odd - seen),
               "new_coordinates_Z_vs_previous_k": len(full - seenZ)}
        seen |= odd
        seenZ |= full
        sups[k] = odd
        supsZ[k] = full
        rows_out.append(rec)
        print(json.dumps(rec), flush=True)
    # a pairwise-DISJOINT subfamily of nonzero generators is linearly
    # independent over F_2, so its size is a lower bound on rank V_{H_fin}
    keep, keepZ = [], []
    for k in sorted(sups):
        if sups[k] and all(not (sups[k] & sups[j]) for j in keep):
            keep.append(k)
        if supsZ[k] and all(not (supsZ[k] & supsZ[j]) for j in keepZ):
            keepZ.append(k)
    ml = [o["max_coordinate_length"] for o in rows_out]
    mn = [o["min_coordinate_length"] for o in rows_out]
    mlZ = [o["max_coordinate_length_Z"] for o in rows_out]
    mnZ = [o["min_coordinate_length_Z"] for o in rows_out]
    summ = {"chain": r["chain"], "g": r["g_gen"], "kmax": args.kmax,
            "max_coordinate_length_ladder": ml,
            "min_coordinate_length_ladder": mn,
            "max_length_strictly_grows": all(
                ml[i] < ml[i + 1] for i in range(len(ml) - 1)),
            "min_length_strictly_grows_eventually": all(
                mn[i] < mn[i + 1] for i in range(2, len(mn) - 1)),
            "max_coordinate_length_ladder_Z": mlZ,
            "min_coordinate_length_ladder_Z": mnZ,
            "min_length_Z_strictly_grows_eventually": all(
                mnZ[i] < mnZ[i + 1] for i in range(2, len(mnZ) - 1)),
            "cumulative_distinct_odd_coordinates": len(seen),
            "cumulative_distinct_coordinates_Z": len(seenZ),
            "pairwise_disjoint_subfamily": keep,
            "rank_lower_bound_from_disjoint_support": len(keep),
            "pairwise_disjoint_subfamily_Z": keepZ,
            "rank_lower_bound_over_Z": len(keepZ),
            "all_translates_exact": ok,
            "controls_passed": ok and bool(rows_out)}
    print(json.dumps({"summary": summ}), flush=True)
    _dump(args, "growth", summ, rows_out)
    return 0 if summ["controls_passed"] else 2


# --------------------------------------------------------------- mode D


def _ladder_step(rec_steps, r, ops, defect, h, x0, dirs, args, tag, rng,
                 cap_bits=None):
    sub = {"chain": r["chain"], "g": r["g_gen"]}
    a2 = sub_args(args, len(dirs))
    if cap_bits is not None:
        a2.cap_bits = cap_bits
    try:
        TA.analyse(sub, h, x0, dirs, a2, rng)
    except TR.NotInCommutator as e:
        sub["status"] = "FAMILY_LEFT_COMMUTATOR"
        sub["detail"] = str(e)
        sub["passed"] = False
    step = {"tag": tag}
    step.update({k: sub.get(k) for k in STEP_KEYS})
    rec_steps.append(step)
    print(json.dumps(step), flush=True)
    return sub


def mode_ladder(args, rows):
    """(b)+(c): the Hecke ladder against W2l's saturated calibration."""
    sel = TA._slice(rows, args.chains)
    done = _resume(args)
    out, ok = list(done.values()), True
    rng = random.Random(20260828)
    t_run = time.time()
    ladder = [w for w in args.hecke_ladder.split("|") if w]
    for r in sel:
        k = tuple(r["chain"]) + (r["g_gen"],)
        if k in done:
            continue
        if args.run_seconds and time.time() - t_run > args.run_seconds:
            break
        rec = {"chain": r["chain"], "g": r["g_gen"], "steps": []}
        ch, g, ops, defect, h, _sh = TR.setup(r, tuple(args.window))
        sol = TR.solve_layer1(ops, defect, tuple(args.rhos))
        if not sol["ok"]:
            rec["status"] = "LAYER1_UNSOLVED_AT_RHO"
            rec["passed"] = True
            out.append(rec)
            print(json.dumps({"chain": r["chain"], "status": rec["status"]}),
                  flush=True)
            _dump(args, "ladder", {"partial": True, "chains": len(out)}, out)
            continue
        cp = IL.Completed(GS.Folded(GS.gamma_gens(ch, g)))
        native = TR.kernel_directions(ops, defect, args.m, args.kernel_rho,
                                      cp=cp)
        for sh in [s for s in (args.far_shifts or "").split(",") if s]:
            qw = QR(LV.to_tuple(sh))
            seed = {CV(QM(qw, v)): 1 for v in defect}
            for Fx in TR.kernel_directions(ops, seed, args.m_far,
                                           args.kernel_rho, cp=cp):
                if Fx not in native:
                    native.append(Fx)
        rec["native_directions"] = len(native)
        if not native:
            rec["status"] = "NO_KERNEL_DIRECTION_FOUND"
            rec["passed"] = True
            out.append(rec)
            print(json.dumps({"chain": r["chain"], "status": rec["status"]}),
                  flush=True)
            continue
        _ladder_step(rec["steps"], r, ops, defect, h, sol["x"], native, args,
                     "native", rng)
        cur = list(native)
        hecke_bad, outside = 0, 0
        for words in ladder:
            ws = [w for w in words.split(",") if w]
            extra, bad = hecke_close(ops, native, ws)
            hecke_bad += bad
            cur = native + [F for F in extra]
            if len(cur) > args.max_dirs:
                cur = cur[:args.max_dirs]
            outside = lattice_growth(native, cur[len(native):])
            _ladder_step(rec["steps"], r, ops, defect, h, sol["x"], cur, args,
                         "hecke:" + words, rng)
            if args.run_seconds and time.time() - t_run > args.run_seconds:
                rec["truncated_run_budget"] = True
                break
        # the exact 2^m mod-2 decision on a capped slice of the ENLARGED
        # family (complete over Z^m by (P); C9 must fire on it)
        if args.decide_dirs:
            nd = min(args.decide_dirs, len(cur))
            _ladder_step(rec["steps"], r, ops, defect, h, sol["x"],
                         cur[:nd], args, f"decide:{nd}", rng, cap_bits=nd)
        rec["hecke_translates_rejected"] = hecke_bad
        rec["hecke_dirs_outside_native_Z_span"] = outside
        cc = [(s.get("coordinate_certificates") or {}).get("2^1")
              for s in rec["steps"]]
        rec["mod2_coordinate_certificate_ladder"] = cc
        rec["coordinate_certificates_destroyed"] = bool(
            cc and cc[0] and any(x is not None and x < cc[0] for x in cc[1:]))
        ranks = [s.get("mod2_V_rank") for s in rec["steps"]
                 if s.get("mod2_V_rank") is not None]
        rec["rank_ladder"] = ranks
        rec["universe_ladder"] = [s.get("universe_coords")
                                  for s in rec["steps"]]
        rec["rank_grew_beyond_native"] = bool(
            len(ranks) > 1 and max(ranks[1:]) > ranks[0])
        rec["residuals"] = [s.get("mod2_residual_support")
                            for s in rec["steps"]]
        rec["any_mod2_zero"] = any(s.get("mod2_zero_class") is not None
                                   for s in rec["steps"])
        dec = [s for s in rec["steps"] if str(s.get("tag", "")).startswith(
            "decide")]
        rec["decision_status"] = dec[-1]["status"] if dec else None
        rec["C9_fires"] = dec[-1].get(
            "C9_positive_control_fires") if dec else None
        rec["minus_c0_in_V_ever"] = any(
            (s.get("minus_c0_in_V") or {}).get("2^1") is True
            for s in rec["steps"])
        rec["passed"] = bool(hecke_bad == 0
                             and all(s.get("passed") for s in rec["steps"]))
        ok = ok and rec["passed"]
        out.append(rec)
        _dump(args, "ladder", {"partial": True, "chains": len(out)}, out)
    summ = {
        "chains": len(out),
        "with_directions": sum(1 for o in out if o.get("native_directions")),
        "rank_grew_beyond_native": sum(1 for o in out
                                       if o.get("rank_grew_beyond_native")),
        "hecke_translates_rejected": sum(o.get("hecke_translates_rejected", 0)
                                         for o in out),
        "hecke_dirs_outside_native_Z_span": sum(
            o.get("hecke_dirs_outside_native_Z_span", 0) for o in out),
        "chains_with_hecke_dirs_outside_native_span": sum(
            1 for o in out if o.get("hecke_dirs_outside_native_Z_span")),
        "chains_with_coordinate_certificates_destroyed": sum(
            1 for o in out if o.get("coordinate_certificates_destroyed")),
        "chains_with_a_native_coordinate_certificate": sum(
            1 for o in out
            if (o.get("mod2_coordinate_certificate_ladder") or [None])[0]),
        "any_mod2_zero": sum(1 for o in out if o.get("any_mod2_zero")),
        "decision_MOD2_UNATTAINABLE_ON_S": sum(
            1 for o in out if o.get("decision_status")
            == "MOD2_UNATTAINABLE_ON_S"),
        "decision_MOD2_ATTAINABLE": sum(
            1 for o in out if o.get("decision_status") in
            ("MOD2_ATTAINABLE_NO_INTEGRAL_WITNESS", "WITNESS")),
        "C9_positive_control_fires": sum(1 for o in out if o.get("C9_fires")),
        "C9_positive_control_run": sum(1 for o in out
                                       if o.get("C9_fires") is not None),
        "minus_c0_in_V_ever": sum(1 for o in out
                                  if o.get("minus_c0_in_V_ever")),
        "controls_passed": ok and bool(out)}
    print(json.dumps({"summary": summ}), flush=True)
    _dump(args, "ladder", summ, out)
    return 0 if summ["controls_passed"] else 2


# ------------------------------------------------------------------ misc


def _resume(args):
    if not args.json or not Path(args.json).exists():
        return {}
    try:
        d = json.loads(Path(args.json).read_text())
    except json.JSONDecodeError:
        return {}
    return {tuple(r["chain"]) + (r.get("g", ""),): r for r in d.get("rows", [])}


def _dump(args, name, summ, rows_out):
    if args.json:
        Path(args.json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json).write_text(json.dumps(
            {"schema": f"acsolverx.w2m.{name}.v1", "summary": summ,
             "rows": rows_out}, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("lemma", "action", "growth", "ladder"),
                    default="lemma")
    ap.add_argument("--chains", type=str, default="")
    ap.add_argument("--window", type=int, nargs=4, default=[0, 0, 0, 0])
    ap.add_argument("--rhos", type=int, nargs="+", default=[2])
    ap.add_argument("--m", type=int, default=6)
    ap.add_argument("--kernel-rho", type=int, default=2)
    ap.add_argument("--holdout", type=int, default=3)
    ap.add_argument("--cap-bits", type=int, default=0)
    ap.add_argument("--elim-cap", type=int, default=3000)
    ap.add_argument("--far-shifts", type=str, default="")
    ap.add_argument("--m-far", type=int, default=4)
    ap.add_argument("--gwords", type=str,
                    default="c,t,T,ct,tc,cT,Tc,ctc,tt,TT,tct,ctct")
    ap.add_argument("--hecke", type=str, default="t,T,tt,ct,tc")
    ap.add_argument("--hecke-ladder", type=str, default="t|t,tt|t,tt,T")
    ap.add_argument("--max-dirs", type=int, default=34)
    ap.add_argument("--kmax", type=int, default=6)
    ap.add_argument("--dirs-scan", type=int, default=1,
                    help="pair this many native directions with their Hecke translates in mode growth")
    ap.add_argument("--decide-dirs", type=int, default=0,
                    help="run the exact 2^m mod-2 decision on "
                         "this many directions of the enlarged "
                         "family (C9 fires there)")
    ap.add_argument("--samples", type=int, default=6)
    ap.add_argument("--real-chains", type=int, default=2)
    ap.add_argument("--pair-words", type=int, default=4)
    ap.add_argument("--cocycle-ys", type=int, default=4)
    ap.add_argument("--corrupt-n", type=int, default=8)
    ap.add_argument("--central-len", type=int, default=4)
    ap.add_argument("--run-seconds", type=float, default=0.0)
    ap.add_argument("--json", type=str, default="")
    args = ap.parse_args()

    c1 = LV.analyze(PS.WITNESS, fixed_h=PS.CODEX_H)
    got = (c1["defect_terms"], c1["defect_l1"], c1["defect_augmentation"])
    print(json.dumps({"control": "C1_fixed_h_witness", "defect": list(got),
                      "want": [21, 48, 0], "passed": got == (21, 48, 0)}),
          flush=True)
    if got != (21, 48, 0):
        return 2
    rows = GS.load_rows()
    return {"lemma": mode_lemma, "action": mode_action,
            "growth": mode_growth, "ladder": mode_ladder}[args.mode](
                args, rows)


if __name__ == "__main__":
    sys.exit(main())
