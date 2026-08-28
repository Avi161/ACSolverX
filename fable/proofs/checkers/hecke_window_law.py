"""W2n: the coordinate-window law of the Hecke module, its normal form, and
what it does (and does NOT) decide.

`W2M_THETA_COCYCLE.md` section 11 names one structure as the only thing it
found that is not bounded by a direction set:

    "the cross generator `b(F, T_{t^k} F)` occupies a coordinate window of
     fixed width that translates linearly with `k`, with a uniformly nonzero
     leading block.  If that holds, `Xi_Z(Theta)` restricted to the Hecke
     module has a PERIODIC NORMAL FORM and attainability becomes one finite
     block plus a shift."

This checker decides that conjecture.  It does NOT take W2m's measurement on
trust: the window is re-measured in the displacement-class frame (W2i's
`Xi_Z` coordinates), in a form that is an exact IDENTITY rather than a length
statistic, and the identity is then used PREDICTIVELY -- the literal
`Xi_Z(Theta)` vector at a Hecke element the normal form never saw is
predicted from the normal form and compared term by term.

--------------------------------------------------------------------------
0. THE OBJECT, and the frame
--------------------------------------------------------------------------
`Q = <c,t | c^2>`, `H = <c>`, `X = Q/H`, `M = Z[X]`, `N = ker(F(c,t) -> Q)`.
For a census baseline with conjugator tuple `h` and a layer-1 solution `x_0`,

    G(y) := Xi~( Theta(x_0 + y) )   for  y in H_fin = ker(L: M^5 -> M)

is affine-quadratic (W2l Lemma A), so it has an exact polarisation

    b(y, y') := G(y + y') - G(y) - G(y') + G(0)      (bilinear)
    q(y)     := ( G(2y) - 2 G(y) + G(0) ) / 2        (the quadratic part)
    l(y)     := G(y) - G(0) - q(y)                   (the linear part)

`Xi~` is `theta_residual_evaluator.xi_raw`, whose coordinates are indexed by
DISPLACEMENT CLASSES `D = H v1^-1 v2 H` in `H \\ Q / H` (W2i section 2, W2j
(3.15b)): free `Z` coordinates for `D != D^-1` (folded to the shortlex-min of
`{D, D^-1}` with a sign) and integral-but-really-`Z/2` coordinates for
`D = D^-1`.  That is the frame in which a translation law can even be stated.

The Hecke algebra `E = End_{Z[Q]}(M) = Z[H\\Q/H]` acts on the right by
`T_a(e_v) = e_{va} + e_{vca}` and preserves `H_fin` (W2m section 3, PROVED and
re-verified here on Hecke elements W2m never tested).  `T_a` depends only on
the double coset `HaH`.

--------------------------------------------------------------------------
1. THE WINDOW LAW  (statement, proof, and what is machine-checked)
--------------------------------------------------------------------------
LAW (W).  For every pair of directions `F, F'` in `H_fin` there is a FINITE
"source datum"

    beta(F,F') :  (H\\Q/H) x {0,1}^2  ->  Z        (finitely supported)

such that for all `a, b` in `Q`,

    b( T_a F , T_b F' )  =  rho_{a,b}( beta(F,F') )                      (W)

where `rho_{a,b}` sends a source class `w` on sheet `(s1,s2)` to the
displacement class of `a^-1 c^{s1} w c^{s2} b`, with the sign of the
`{D, D^-1}` folding, and drops it when that class is trivial.  The same law
holds for the linear part `l(T_b F)` (with `a = 1`) and for the quadratic
part `q(T_a F)` (with `b = a`).

PROOF SKETCH (the machine check is the authority; see controls CW4/CW5).
Write the recurrence (1.8) with `x = x_0 + y`.  Every word it builds is a
product of conjugates of `sigma(y_r)^{+-1}` and of `x`-independent words; the
conjugators depend on `y` only through their `Q`-class, and `q(sigma) = 1`,
so those classes are FIXED.  Three facts then confine the polarisation:

  (i)  `Theta(sigma(y)) = UT(y (x) y)` exactly, where `UT(p (x) q)_{v<w}
       = p_v q_w`;
  (ii) `Theta(ab) = Theta(a) + Theta(b) + UT([a] (x) [b])` and
       `Theta(a^-1) = -Theta(a) + UT([a] (x) [a])`;
  (iii) `[W(y)]` is AFFINE in `y` with fixed group-ring coefficients (that is
       exactly the operator columns `L_r`), and conjugation by `n in N`
       contributes `UT([n] (x) [W]) - UT([W] (x) [n])`.

So the polarisation is a finite sum of terms `UT(g y_r (x) h y'_s)` with
`(g,h)` from a fixed finite subset of `Q^2` -- EXCEPT that the `UT` order
condition `v < w` and W2m's inversion form `I_g` attach coefficients that
depend on the shortlex COMPARISON of the two vertices, not only on `(g,h)`.
Now `T_b` moves the second vertex to `u b`, and `Xi~` sends the pair
`(g v, h u b)` to the displacement class `H (gv)^-1 (hu) b H`, i.e. to the
right translate by `b` of the class it had at `b = 1`; the same on the left
for `T_a`.  Hence (W) holds as soon as the comparison pattern is constant,
which it is once `|a|, |b|` exceed the diameter of the finite vertex set
involved.  The transient at small `|a|,|b|` is REAL and is measured, not
assumed (`first_stable`), and the collapse of a source class to the trivial
displacement (`e_v ^ e_v = 0`) is handled exactly by `rho`.

WHAT IS MACHINE-CHECKED, and how (mode `law`):
  * (W) as an exact identity: the normal form `beta` is read off at ONE
    Hecke pair and then used to PREDICT the literal vector at every other
    tested pair; agreement is term by term over `Z` (control CW4).
  * the prediction control has teeth: a normal form with ONE coefficient
    bumped must mispredict (control CW5), counted only where the bumped
    coordinate survives `rho`.
  * cross-family uniformity: `t^k`, `T^k`, `t^i c t^j`, `c t^k c` all give the
    SAME `beta` (control CW6) -- so the law is not a fact about powers of `t`.
  * the de-shift is injective on the support (no collision is hiding a
    cancellation) and every sheet is resolvable (CW2, CW3).
  * `T_a F` is re-verified in `H_fin` by `IL.verify` at every `a` used,
    including `a` with interior `c` and `|a| >> 1` that W2m never tested, and
    a corrupted `T_a` must leave `H_fin` (CW1) -- a premise re-verification
    at NON-special values.
  * the integral (not mod-2) model of W2l Lemma A is re-verified by held-out
    literal prediction at `|n| >= 2` and negative `n` ON THE HECKE-ENLARGED
    family (CW7).  W2m ran its ladder with `--mod2-only`, so the integral
    model was never held out there.

--------------------------------------------------------------------------
2. WHAT THE NORMAL FORM DECIDES  (modes `blocks`, `decide`)
--------------------------------------------------------------------------
With (W), the value of `G` on the whole `t`-ladder Hecke family

    y(n) = sum_{i,j} n_{i,j} T_{t^j} F_i        (finitely supported n)

is an explicit function of `n` alone: every term is a `rho`-translate of one
of finitely many source data, so the coordinate support of the `(i,j),(i',k)`
term is computable WITHOUT any further free-group evaluation.  Two things
follow, and both are finite computations:

  SEPARATION.  A displacement class `D` reachable from the block `(j,k)` has
  head/tail `t`-exponents pinned to `(-j, k)` up to the diameter of the
  source data, and `|D| >= |j| + |k| - 2B`.  So only finitely many blocks can
  reach a given `D`, and the set of them is computed exactly.

  FORCING.  If some free (`Z`) coordinate `D` is reachable ONLY by the linear
  term of one generator, then that generator's coefficient is pinned by
  `n * l(D) = -c_0(D)`, hence forced (usually to 0).  Iterating this over the
  ladder decides whether the infinite family can contribute at all.

This is the "one finite block system plus a shift recurrence" W2m asked for.
Its verdict is reported per baseline, with the exact claim class:

  * a verdict here is about the family generated by the tested native
    directions under the `t`-ladder Hecke action.  That family is INFINITE --
    which is new -- but it is still generated by a finite direction seed, so
    Lemma C(ii) of W2l still applies to the seed.  Mode `span` measures how
    much of `H_fin` the Hecke closure actually catches.

EXIT CODES
  0  run completed, every control green (a verdict is a RESULT, not a failure)
  2  a control failed -- the run is void

HYPOTHESES INHERITED (nothing here re-derives them)
  (3.1) `N` is free on the Schreier generators `(r_v)`, `v in X`.
  (3.5) the layer-2 variation operator carries the same integral coefficients
        as `L_r`.  Nothing in this file uses (3.5): the window law, the normal
        form and the block system are statements about the literal free-group
        residual, `Xi~` and the operators alone.  (3.5) is needed only to read
        `Xi_Z(Theta) = 0` as "layer 2 is solvable", exactly as in W2i-W2m.
"""
from __future__ import annotations

import argparse
import itertools
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
import theta_cocycle as TC  # noqa: E402
sys.argv = _ARGV

TA, TR, IL, GS, PS, LV = TC.TA, TC.TR, TC.IL, TC.GS, TC.PS, TC.LV
lift, esc = TC.lift, TC.esc

QM, QI, QR = lift.quotient_multiply, lift.quotient_inverse, lift.quotient_reduce
CV, LIT = lift.c_vertex, lift.literal
C, T = lift.C, lift.T
CC = (C,)
DC = TR.dcoset_rep
OUT = HERE / "out"


def slen(w):
    return (len(w), w)


def tpow(j):
    """the quotient element `t^j` (j may be negative)."""
    return QR((T,) * j if j >= 0 else (-T,) * (-j))


def wq(s):
    """canonical double-coset representative of the literal word `s`."""
    return DC(QR(LV.to_tuple(s)))


def head_tail(w):
    """(head t-exponent, tail t-exponent, number of c's) of a canonical rep."""
    runs, cur, ncs = [], 0, 0
    for ch in w:
        if abs(ch) == C:
            runs.append(cur)
            cur = 0
            ncs += 1
        else:
            cur += 1 if ch == T else -1
    runs.append(cur)
    return runs[0], runs[-1], ncs


# ------------------------------------------------------- the de-shift frame


def deshift(name, aq, bq):
    """Coordinate `name` -> (source class, sheet pair, sign).

    The measured coordinate is the shortlex fold of a displacement class `d`;
    the source is `w` with `d ~ a^-1 c^{s1} w c^{s2} b`, so
    `HwH = H a d b^-1 H`, taken over both orientations of the fold and the
    shorter one kept.  Returns `None` for the sheet if no sheet resolves it
    (which would refute the law's bookkeeping and is counted, not ignored).
    """
    z0 = lift.parse_quotient(name)
    best = None
    for orient, d in ((1, z0), (-1, QI(z0))):
        w = DC(QM(aq, d, QI(bq)))
        k = slen(w)
        if best is None or k < best[0]:
            best = (k, w, orient, d)
    _k, w, orient, d = best
    dd = DC(d)
    sheet = None
    for s1, p1 in ((0, ()), (1, CC)):
        for s2, p2 in ((0, ()), (1, CC)):
            if DC(QM(QI(aq), p1, w, p2, bq)) == dd:
                sheet = (s1, s2)
                break
        if sheet is not None:
            break
    return LIT(w), sheet, orient


def normalize(vec, aq, bq):
    """De-shift a measured coordinate vector to its source datum.

    Returns (normal form, diagnostics).  The normal form drops the free /
    torsion KIND: whether a source class lands on a `Z` or a `Z/2` coordinate
    is decided by `rho` (self-inverse or not) and is therefore a property of
    the target, not of the datum -- see `predict`, which puts it back.
    """
    out, coll, fail, seen = {}, 0, 0, {}
    for (_kind, nm), v in vec.items():
        w, sh, sg = deshift(nm, aq, bq)
        if sh is None:
            fail += 1
            continue
        key = (sh, w)
        if key in seen:
            coll += 1
        seen[key] = nm
        out[key] = out.get(key, 0) + sg * v
    return ({k: v for k, v in out.items() if v},
            {"collisions": coll, "sheet_unresolved": fail})


def predict(nf, aq, bq):
    """`rho_{a,b}` applied to a normal form: the predicted literal vector."""
    out, dropped = {}, 0
    for (sh, w), v in nf.items():
        p1 = () if sh[0] == 0 else CC
        p2 = () if sh[1] == 0 else CC
        d = QM(QI(aq), p1, lift.parse_quotient(w), p2, bq)
        d0, di = DC(d), DC(QI(d))
        if d0 == ():
            dropped += 1
            continue
        if d0 == di:
            key = ("t", LIT(d0))
            out[key] = out.get(key, 0) + v
        else:
            dp = min(d0, di, key=slen)
            key = ("f", LIT(dp))
            out[key] = out.get(key, 0) + (v if d0 == dp else -v)
    return {k: v for k, v in out.items() if v}, dropped


# ---------------------------------------------------------------- the frame


class Frame:
    """One baseline: `h`, `x_0`, native directions, and a cached `G`."""

    def __init__(self, row, args):
        self.row = row
        self.status = None
        ch, g, ops, defect, h, _sh = TR.setup(row, tuple(args.window))
        self.ch, self.g, self.ops, self.defect, self.h = ch, g, ops, defect, h
        sol = TR.solve_layer1(ops, defect, tuple(args.rhos))
        if not sol["ok"]:
            self.status = "LAYER1_UNSOLVED_AT_RHO"
            return
        self.x0 = sol["x"]
        cp = IL.Completed(GS.Folded(GS.gamma_gens(ch, g)))
        self.dirs = TR.kernel_directions(ops, defect, args.m, args.kernel_rho,
                                         cp=cp)
        if not self.dirs:
            self.status = "NO_KERNEL_DIRECTION_FOUND"
            return
        self.nev = 0
        self._cache = {}
        self.base = self.G([], [])

    def G(self, F_list, n):
        key = (tuple(TC.dir_key(F) for F in F_list), tuple(n))
        if key in self._cache:
            return self._cache[key]
        self.nev += 1
        th, _w = TR.theta(self.h, TR.combine(self.x0, F_list, n))
        v = TR._vec(*TR.xi_raw(th))
        self._cache[key] = v
        return v

    def exact(self, F):
        return not IL.verify({}, self.ops, F)

    # --- the three polarisation pieces, all literal -----------------------
    def cross(self, Fa, Fb):
        p = [Fa, Fb]
        return TA.vlin((1, self.G(p, [1, 1])), (-1, self.G(p, [1, 0])),
                       (-1, self.G(p, [0, 1])), (1, self.base))

    def quad(self, Fa):
        p = [Fa]
        num = TA.vlin((1, self.G(p, [2])), (-2, self.G(p, [1])),
                      (1, self.base))
        if any(v % 2 for v in num.values()):
            raise AssertionError("second difference is odd: not quadratic")
        return {k: v // 2 for k, v in num.items()}

    def linear(self, Fa):
        return TA.vlin((1, self.G([Fa], [1])), (-1, self.base),
                       (-1, self.quad(Fa)))


def hecke_of(fr, F, aq):
    return TC.hecke_dir(aq, F)


# ------------------------------------------------------------------ mode L


def _sep(A, B):
    """Separation of a Hecke pair: how far apart the two translated vertex
    sets are.  For a genuinely two-sided pair that is `|a|`, `|b|` AND
    `|a^-1 b|` -- a near-diagonal pair `(t^6, t^7)` is NOT a far pair.  For
    the linear term (`a = 1`) it is `|b|`; for the quadratic term
    (`a = b`) it is `|a|`."""
    if not A:
        return len(B)
    if A == B:
        return len(A)
    return min(len(A), len(B), len(DC(QM(QI(A), B))))


def tstr(j):
    return "t" * j if j >= 0 else "T" * (-j)


def vertex_diameter(fr, F):
    """The effective constant the transient is bounded by.

    The proof sketch says the shortlex COMPARISON pattern stabilises once the
    Hecke translate is longer than the vertex sets involved; those vertices
    come from `x_0`, the direction, the defect and the operator group-ring
    supports.  This returns that bound -- conservative, but effective and
    computed, not fitted.
    """
    mx = 0
    for f in list(fr.x0) + list(F) + [fr.defect]:
        for v in f:
            mx = max(mx, len(v))
    for op in fr.ops:
        for gw in op:
            mx = max(mx, len(gw))
    return mx


def _test_set(level):
    """(kind, a-literal, b-literal) triples.

    Separations are chosen to span the transient AND to sit well above it,
    across several double-coset shapes and both signs.  The transient is
    MEASURED from this set (`transient_measured`), never assumed; the run is
    reported UNDERPOWERED if too few tests sit above it -- a control with no
    dynamic range is not a control.
    """
    if level == "lean":
        one = [tstr(1), tstr(4), tstr(8), tstr(-8),
               tstr(3) + "c" + tstr(6)]
        mix = [(tstr(6), tstr(12)), (tstr(8), tstr(16)),
               (tstr(-8), tstr(10)), (tstr(6), tstr(7))]
    else:
        one = [tstr(1), tstr(2), tstr(4), tstr(6), tstr(8), tstr(10),
               tstr(12), tstr(-8), tstr(-12),
               tstr(3) + "c" + tstr(6), tstr(6) + "c" + tstr(3),
               "c" + tstr(9) + "c"]
        mix = [(tstr(4), tstr(10)), (tstr(6), tstr(12)),
               (tstr(8), tstr(16)), (tstr(10), tstr(18)),
               (tstr(12), tstr(20)), (tstr(-8), tstr(10)),
               (tstr(8), tstr(-12)), (tstr(-8), tstr(-16)),
               (tstr(2) + "c" + tstr(8), tstr(16)),
               (tstr(8), tstr(16) + "c" + tstr(2)),
               (tstr(6), tstr(7)), (tstr(1), tstr(5))]
    out = [("lin", "", w) for w in one] + [("quad", w, w) for w in one]
    out += [("mix", a, b) for a, b in mix]
    return out


def _law_one_dir(fr, F, Fp, args, rec, rng):
    """The window law for the pair (F, F') over the tested Hecke elements."""
    vd = vertex_diameter(fr, F)
    rec["vertex_diameter_bound"] = vd
    ctl = {"CW1_hecke_in_Hfin": 0, "CW1_tested": 0, "CW1_corrupt_leaves": 0,
           "CW1_corrupt_tested": 0, "CW2_collisions": 0,
           "CW3_sheet_unresolved": 0, "CW4_predictions": 0, "CW4_exact": 0,
           "CW4_transient": 0, "CW4_violations": 0,
           "CW5_corruption_tested": 0, "CW5_corruption_fires": 0,
           "CW6_families_agree": 0, "CW6_families": 0,
           "CW8_crossdir_tested": 0, "CW8_crossdir_exact": 0}
    triples = _test_set(args.test_level)
    seen_a = set()
    meas = {"lin": [], "quad": [], "mix": []}
    for kind, sa, sb in triples:
        aq, bq = wq(sa) if sa else (), wq(sb)
        Fa = TC.hecke_dir(aq, F) if sa else None
        Fb = TC.hecke_dir(bq, F if kind != "cross" else Fp)
        for s, Fx in ((sa, Fa), (sb, Fb)):
            if Fx is None or not s or s in seen_a:
                continue
            seen_a.add(s)
            ctl["CW1_tested"] += 1
            ctl["CW1_hecke_in_Hfin"] += int(fr.exact(Fx))
            Fc = TC.hecke_dir(wq(s), F, corrupt=True)
            if any(Fc):
                ctl["CW1_corrupt_tested"] += 1
                ctl["CW1_corrupt_leaves"] += int(not fr.exact(Fc))
        if kind == "lin":
            if not any(Fb):
                continue
            vec, A, B = fr.linear(Fb), (), bq
        elif kind == "quad":
            if not any(Fa):
                continue
            vec, A, B = fr.quad(Fa), aq, aq
        else:
            if not any(Fa) or not any(Fb) or TC.dir_key(Fa) == TC.dir_key(Fb):
                continue
            vec, A, B = fr.cross(Fa, Fb), aq, bq
        nf, diag = normalize(vec, A, B)
        ctl["CW2_collisions"] += diag["collisions"]
        ctl["CW3_sheet_unresolved"] += diag["sheet_unresolved"]
        meas[kind].append((f"{sa}|{sb}", A, B, vec, nf, _sep(A, B)))
    forms, detail, results = {}, {}, []
    for kind, seq in meas.items():
        if not seq:
            continue
        ref_i = max(range(len(seq)), key=lambda i: seq[i][5])
        ref = seq[ref_i][4]
        forms[kind] = ref
        pmatch, agree = [], []
        for tag, A, B, vec, nf, sep in seq:
            agree.append(int(nf == ref))
            got, _d = predict(ref, A, B)
            ok = (got == vec)
            pmatch.append(int(ok))
            results.append((kind, tag, sep, int(ok)))
        if ref:
            bad = dict(ref)
            kk = sorted(bad)[0]
            bad[kk] = bad[kk] + 1
            for tag, A, B, vec, nf, sep in seq:
                bp, _d2 = predict(bad, A, B)
                gp, _d3 = predict(ref, A, B)
                if bp == gp:
                    continue
                ctl["CW5_corruption_tested"] += 1
                ctl["CW5_corruption_fires"] += int(bp != vec)
        detail[kind] = {
            "steps": len(seq),
            "steps_matching_reference": sum(agree),
            "prediction_exact_steps": sum(pmatch),
            "separations": [x[5] for x in seq],
            "normal_form_size": len(ref),
            "normal_form_odd": sum(1 for v in ref.values() if v % 2),
            "normal_form_free_l1": sum(abs(v) for v in ref.values()),
            "source_classes": len({w for _sh, w in ref}),
            "source_max_len": max((len(w) for _sh, w in ref), default=0),
            "sheet_asymmetric_keys": sum(
                1 for (sh, w) in ref
                if ref.get(((sh[0], 0), w)) != ref.get(((sh[0], 1), w))),
            "tags": [x[0] for x in seq],
            "per_step_prediction_match": pmatch,
        }
        ctl["CW6_families"] += len(seq)
        ctl["CW6_families_agree"] += sum(agree)
    # CW8: the law for a pair of DISTINCT native directions
    if Fp is not None and "mix" in forms:
        refx = None
        for sa, sb in [(tstr(6), tstr(12)), (tstr(8), tstr(16)),
                       (tstr(-8), tstr(10)),
                       (tstr(2) + "c" + tstr(8), tstr(16))]:
            aq, bq = wq(sa), wq(sb)
            Fa, Fb = TC.hecke_dir(aq, F), TC.hecke_dir(bq, Fp)
            if not any(Fa) or not any(Fb) or TC.dir_key(Fa) == TC.dir_key(Fb):
                continue
            vec = fr.cross(Fa, Fb)
            nf, diag = normalize(vec, aq, bq)
            ctl["CW2_collisions"] += diag["collisions"]
            ctl["CW3_sheet_unresolved"] += diag["sheet_unresolved"]
            if refx is None:
                refx = nf
                continue
            got, _d = predict(refx, aq, bq)
            ok = (got == vec)
            ctl["CW8_crossdir_tested"] += 1
            ctl["CW8_crossdir_exact"] += int(ok)
            results.append(("crossdir", sa + "|" + sb, _sep(aq, bq), int(ok)))
    # --- the MEASURED transient, and whether the test set has the range to
    #     say anything above it
    miss = [r for r in results if not r[3]]
    tau = max((r[2] for r in miss), default=-1)
    above = [r for r in results if r[2] > tau]
    ctl["CW4_predictions"] = len(results)
    ctl["CW4_exact"] = sum(r[3] for r in results)
    ctl["CW4_transient"] = len(miss)
    ctl["CW4_violations"] = 0
    rec["transient_measured"] = tau
    rec["tests_above_transient"] = len(above)
    rec["tests_above_transient_exact"] = sum(r[3] for r in above)
    rec["separations_above_transient"] = sorted({r[2] for r in above})
    rec["misses"] = [[r[0], r[1], r[2]] for r in miss]
    rec["underpowered"] = bool(len(above) < args.min_above
                               or len(rec["separations_above_transient"]) < 2)
    rec["transient_within_bound"] = bool(tau <= vd)
    rec["controls"] = ctl
    rec["forms"] = detail
    rec["normal_forms"] = {k: sorted(((list(sh), w), v)
                                     for (sh, w), v in f.items())
                           for k, f in forms.items()} if args.detail else None
    return forms, ctl


def _integral_model_control(fr, F, args, rng):
    """CW7: W2l Lemma A's INTEGRAL model, held out on the Hecke family.

    W2m's ladder ran `--mod2-only`, so the degree-2 integral law was never
    held out on a Hecke-enlarged family.  Re-verified here at points with
    negative and `|n| >= 2` entries -- the values the mod-2 path never takes.
    """
    aq = wq("t" * max(3, min(args.max_shift, vertex_diameter(fr, F) + 1)))
    F2 = hecke_of(fr, F, aq)
    if not any(F2):
        return {"tested": 0, "agree": 0, "corruption_fires": None}
    dirs = [F, F2]
    c0 = fr.G(dirs, [0, 0])
    g1 = [fr.G(dirs, [1, 0]), fr.G(dirs, [0, 1])]
    bd = []
    for j in range(2):
        n = [0, 0]
        n[j] = 2
        num = TA.vlin((1, fr.G(dirs, n)), (-2, g1[j]), (1, c0))
        bd.append({k: v // 2 for k, v in num.items()})
    a = [TA.vlin((1, g1[j]), (-1, c0), (-1, bd[j])) for j in range(2)]
    bx = TA.vlin((1, fr.G(dirs, [1, 1])), (-1, g1[0]), (-1, g1[1]), (1, c0))

    def model(n):
        return TA.vlin((1, c0), (n[0], a[0]), (n[1], a[1]),
                       (n[0] * n[0], bd[0]), (n[1] * n[1], bd[1]),
                       (n[0] * n[1], bx))

    held = [[-1, 0], [0, -1], [3, 0], [0, 3], [-2, 3], [2, -2], [3, 3],
            [-1, -1]]
    ok = sum(int(fr.G(dirs, n) == model(n)) for n in held)
    badbx = dict(bx)
    if badbx:
        kk = sorted(badbx)[0]
        badbx[kk] += 1

    def bmodel(n):
        return TA.vlin((1, c0), (n[0], a[0]), (n[1], a[1]),
                       (n[0] * n[0], bd[0]), (n[1] * n[1], bd[1]),
                       (n[0] * n[1], badbx))

    fires = int(bmodel([1, 1]) != fr.G(dirs, [1, 1])) if bx else None
    return {"tested": len(held), "agree": ok, "corruption_fires": fires}


def mode_law(args, rows):
    sel = TA._slice(rows, args.chains)
    done = _resume(args)
    out = list(done.values())
    rng = random.Random(20260828)
    t_run = time.time()
    for r in sel:
        k = tuple(r["chain"]) + (r["g_gen"],)
        if k in done:
            continue
        if args.run_seconds and time.time() - t_run > args.run_seconds:
            break
        t0 = time.time()
        rec = {"chain": r["chain"], "g": r["g_gen"]}
        fr = Frame(r, args)
        if fr.status:
            rec["status"] = fr.status
            rec["passed"] = True
            out.append(rec)
            print(json.dumps({"chain": r["chain"], "status": fr.status}),
                  flush=True)
            _dump(args, "law", {"partial": True, "chains": len(out)}, out)
            continue
        rec["native_directions"] = len(fr.dirs)
        per = []
        allctl = {}
        for i in range(min(args.dirs_scan, len(fr.dirs))):
            sub = {"direction": i}
            try:
                Fp = fr.dirs[i + 1] if i + 1 < len(fr.dirs) else None
                _forms, ctl = _law_one_dir(fr, fr.dirs[i], Fp, args, sub, rng)
            except AssertionError as e:
                sub["status"] = "NOT_QUADRATIC"
                sub["detail"] = str(e)
                sub["passed"] = False
                per.append(sub)
                continue
            sub["integral_model"] = _integral_model_control(fr, fr.dirs[i],
                                                            args, rng)
            sub["law_verified"] = bool(
                not sub["underpowered"]
                and sub["tests_above_transient"]
                == sub["tests_above_transient_exact"]
                and sub["transient_within_bound"])
            sub["passed"] = bool(
                ctl["CW1_tested"] == ctl["CW1_hecke_in_Hfin"]
                and ctl["CW3_sheet_unresolved"] == 0
                and (ctl["CW5_corruption_tested"] == 0
                     or ctl["CW5_corruption_fires"]
                     == ctl["CW5_corruption_tested"])
                and sub["integral_model"]["tested"]
                == sub["integral_model"]["agree"])
            for kk, vv in ctl.items():
                allctl[kk] = allctl.get(kk, 0) + vv
            per.append(sub)
        rec["per_direction"] = per
        rec["controls"] = allctl
        rec["evaluations"] = fr.nev
        rec["window_law_holds"] = bool(
            per and all(p.get("law_verified") for p in per))
        rec["window_law_underpowered"] = bool(
            per and any(p.get("underpowered") for p in per))
        rec["transient_measured"] = max(
            (p.get("transient_measured", -1) for p in per), default=-1)
        rec["passed"] = bool(per and all(p.get("passed") for p in per))
        rec["secs"] = round(time.time() - t0, 2)
        out.append(rec)
        print(json.dumps({"chain": r["chain"], "dirs": rec["native_directions"],
                          "law": rec["window_law_holds"],
                          "CW4": f"{allctl.get('CW4_exact')}/"
                                 f"{allctl.get('CW4_predictions')}",
                          "CW5": f"{allctl.get('CW5_corruption_fires')}/"
                                 f"{allctl.get('CW5_corruption_tested')}",
                          "secs": rec["secs"]}), flush=True)
        _dump(args, "law", {"partial": True, "chains": len(out)}, out)
    summ = _law_summary(out)
    print(json.dumps({"summary": summ}), flush=True)
    _dump(args, "law", summ, out)
    return 0 if summ["controls_passed"] else 2


def _law_summary(out):
    def s(key):
        return sum((o.get("controls") or {}).get(key, 0) for o in out)

    done = [o for o in out if o.get("native_directions")]
    return {
        "chains": len(out),
        "analysable": len(done),
        "layer1_unsolved": sum(1 for o in out
                               if o.get("status") == "LAYER1_UNSOLVED_AT_RHO"),
        "no_direction": sum(1 for o in out
                            if o.get("status") == "NO_KERNEL_DIRECTION_FOUND"),
        "window_law_holds": sum(1 for o in out if o.get("window_law_holds")),
        "window_law_fails": sum(
            1 for o in done if not o.get("window_law_holds")
            and not o.get("window_law_underpowered")),
        "window_law_underpowered": sum(
            1 for o in done if o.get("window_law_underpowered")),
        "transient_measured_max": max(
            (o.get("transient_measured", -1) for o in done), default=-1),
        "CW1_hecke_in_Hfin": f"{s('CW1_hecke_in_Hfin')}/{s('CW1_tested')}",
        "CW1_corrupt_leaves_Hfin":
            f"{s('CW1_corrupt_leaves')}/{s('CW1_corrupt_tested')}",
        "CW2_collisions": s("CW2_collisions"),
        "CW3_sheet_unresolved": s("CW3_sheet_unresolved"),
        "CW4_predictions_exact": f"{s('CW4_exact')}/{s('CW4_predictions')}",
        "CW4_transient_misses": s("CW4_transient"),
        "CW4_violations_beyond_transient": s("CW4_violations"),
        "CW5_corruption_fires":
            f"{s('CW5_corruption_fires')}/{s('CW5_corruption_tested')}",
        "CW6_normalform_agree":
            f"{s('CW6_families_agree')}/{s('CW6_families')}",
        "CW8_cross_direction_exact":
            f"{s('CW8_crossdir_exact')}/{s('CW8_crossdir_tested')}",
        "CW7_integral_model": "/".join(str(x) for x in (
            sum(p.get("integral_model", {}).get("agree", 0)
                for o in out for p in o.get("per_direction", [])),
            sum(p.get("integral_model", {}).get("tested", 0)
                for o in out for p in o.get("per_direction", [])))),
        "controls_passed": all(o.get("passed", True) for o in out)
        and bool(out),
    }


# ------------------------------------------------------------------ mode B


def _forms_for(fr, F, Fp, args):
    """(linear, quadratic, mixed) normal forms for the pair (F, F')."""
    j0 = args.form_shift
    a0, b0 = wq(tstr(j0)), wq(tstr(j0 + args.mix_gap))
    Fa, Fb = TC.hecke_dir(a0, F), TC.hecke_dir(b0, Fp)
    lin, _d1 = normalize(fr.linear(Fa), (), a0)
    qd, _d2 = normalize(fr.quad(Fa), a0, a0)
    mix = ({}, None)
    if any(Fb) and TC.dir_key(Fa) != TC.dir_key(Fb):
        mix = normalize(fr.cross(Fa, Fb), a0, b0)
    return lin, qd, mix[0]


def wcore(w):
    """(core, head exponent, tail exponent) of a word; core is None when the
    word has no `c`, and then the head exponent is its total `t`-degree."""
    idx = [i for i, ch in enumerate(w) if abs(ch) == C]
    deg = lambda part: sum(1 if ch == T else -1 for ch in part)   # noqa: E731
    if not idx:
        return None, deg(w), 0
    a, b = idx[0], idx[-1]
    return w[a:b + 1], deg(w[:a]), deg(w[b + 1:])


def block_support(nf, j, k):
    """Coordinate support of a `rho`-translate of `nf` at ladder indices."""
    got, _d = predict(nf, tpow(j), tpow(k))
    return got


class Reach:
    """Which ladder blocks can reach a given displacement coordinate.

    Every term of `G` on the `t`-ladder family is `rho_{t^j,t^k}` of one of
    finitely many source data (the window law), so a coordinate `D` is
    reachable from block `(j,k)` of source `u` exactly when
    `D = fold(t^-j u t^k)`.  Matching the CORE of the word (everything from
    the first `c` to the last `c`) pins `(j,k)` uniquely -- and every
    candidate is then VERIFIED by recomputing the translate, so an edge case
    of the double-coset canonicalisation cannot make this under-report.
    A source with no `c` at all is a `t`-power: it reaches a whole line of
    blocks (for `quad`, every block at once), and is flagged UNBOUNDED.
    """

    def __init__(self):
        self.idx = {}
        self.pure = []

    def add(self, tag, nf):
        for (sh, w), v in nf.items():
            p1 = () if sh[0] == 0 else CC
            p2 = () if sh[1] == 0 else CC
            u = QM(p1, lift.parse_quotient(w), p2)
            core, hd, tl = wcore(u)
            if core is None:
                self.pure.append((tag, u, hd))
            else:
                self.idx.setdefault(core, []).append((tag, u, hd, tl))

    def of(self, name):
        """Set of (tag, j, k) blocks reaching the coordinate `name`."""
        d0 = lift.parse_quotient(name)
        out, unbounded = set(), False
        for d in (d0, QI(d0)):
            core, hd, tl = wcore(DC(d))
            if core is None:
                if self.pure:
                    unbounded = True
                continue
            for (tag, u, hu, tu) in self.idx.get(core, ()):
                jj, kk = hu - hd, tl - tu
                for dj in (0, 1, -1):
                    for dk in (0, 1, -1):
                        j2, k2 = jj + dj, kk + dk
                        if tag[0] == "L" and j2 != 0:
                            continue
                        if tag[0] == "Q" and j2 != k2:
                            continue
                        got = DC(QM(tpow(-j2), u, tpow(k2)))
                        if got == ():
                            continue
                        gi = DC(QI(got))
                        if LIT(min(got, gi, key=slen)) == name:
                            out.add((tag, j2, k2))
        return out, unbounded


def mode_blocks(args, rows):
    """SEPARATION and FORCING on the `t`-ladder Hecke family."""
    sel = TA._slice(rows, args.chains)
    done = _resume(args)
    out = list(done.values())
    t_run = time.time()
    for r in sel:
        key = tuple(r["chain"]) + (r["g_gen"],)
        if key in done:
            continue
        if args.run_seconds and time.time() - t_run > args.run_seconds:
            break
        t0 = time.time()
        dead = t0 + args.chain_seconds if args.chain_seconds else None
        rec = {"chain": r["chain"], "g": r["g_gen"]}
        fr = Frame(r, args)
        if fr.status:
            rec["status"] = fr.status
            rec["passed"] = True
            out.append(rec)
            _dump(args, "blocks", {"partial": True, "chains": len(out)}, out)
            continue
        p = min(args.decide_dirs, len(fr.dirs))
        rec["native_directions"] = len(fr.dirs)
        rec["directions_used"] = p
        R = Reach()
        LIN, QD = {}, {}
        try:
            for i in range(p):
                lin, qd, mii = _forms_for(fr, fr.dirs[i], fr.dirs[i], args)
                LIN[i], QD[i] = lin, qd
                R.add(f"L{i}", lin)
                R.add(f"Q{i}", qd)
                # two DIFFERENT translates of the SAME direction are two
                # different generators of the family, so their cross form is
                # a real block and must be in the reach set -- leaving it out
                # would make the isolation test over-claim.
                R.add(f"M{i}_{i}", mii)
            for i in range(p):
                for i2 in range(p):
                    if i == i2:
                        continue
                    _l, _q, mix = _forms_for(fr, fr.dirs[i], fr.dirs[i2],
                                             args)
                    R.add(f"M{i}_{i2}", mix)
        except AssertionError as e:
            rec["status"] = "NOT_QUADRATIC"
            rec["detail"] = str(e)
            rec["passed"] = False
            out.append(rec)
            print(json.dumps(rec), flush=True)
            continue
        except TR.TimeBudget as e:
            rec["status"] = "SKIPPED_TIME_BUDGET"
            rec["detail"] = str(e)
            rec["passed"] = True
            out.append(rec)
            print(json.dumps({"chain": r["chain"],
                              "status": rec["status"]}), flush=True)
            _dump(args, "blocks", {"partial": True, "chains": len(out)}, out)
            continue
        try:
            rec["source_classes_total"] = len(R.idx) + len(R.pure)  # noqa: E501
            rec["pure_power_sources"] = len(R.pure)
            c0names = {nm for _kd, nm in fr.base}
            MIX = {}
            for i in range(p):
                for i2 in range(p):
                    if i == i2:
                        continue
                    _l, _q, mx = _forms_for(fr, fr.dirs[i], fr.dirs[i2], args)
                    MIX[(i, i2)] = mx
            # THE LEADING CORNER.  Let `J` be the largest active ladder index of a
            # hypothetical solution.  Coordinates reachable ONLY by blocks whose
            # ladder indices are BOTH `J` (or the linear term at `J`) carry an
            # equation in the top variables `v_i = n_{i,J}` alone.  If its only
            # integral solution is `v = 0`, no such `J` exists and the infinite
            # family truncates -- the whole point of a periodic normal form.
            corner = {}
            for J in args.forcing_shifts:
                TT = {(f"L{i}", 0, J) for i in range(p)}
                TT |= {(f"Q{i}", J, J) for i in range(p)}
                TT |= {(f"M{i}_{i2}", J, J) for (i, i2) in MIX}
                # `M{i}_{i}` at `(J,J)` is not a term of the family (a generator
                # does not cross itself); allowing it in TT cannot add a term.
                TT |= {(f"M{i}_{i}", J, J) for i in range(p)}
                LB = [block_support(LIN[i], 0, J) for i in range(p)]
                QB = [block_support(QD[i], J, J) for i in range(p)]
                MB = {ii: block_support(MIX[ii], J, J) for ii in MIX}
                names = set()
                for d in LB + QB + list(MB.values()):
                    names |= {nm for _kd, nm in d}
                iso, unb = set(), 0
                for nm in names:
                    if dead and time.time() > dead:
                        raise TR.TimeBudget(len(iso))
                    if nm in c0names:
                        continue
                    blocks, u = R.of(nm)
                    if u:
                        unb += 1
                        continue
                    if blocks and blocks <= TT:
                        iso.add(nm)

                def restrict(d):
                    return {kk: v for kk, v in d.items() if kk[1] in iso}

                Lr = [restrict(x) for x in LB]
                Qr = [restrict(x) for x in QB]
                Mr = {ii: restrict(x) for ii, x in MB.items()}

                def val(v):
                    terms = [(v[i], Lr[i]) for i in range(p)]
                    terms += [(v[i] * v[i], Qr[i]) for i in range(p)]
                    terms += [(v[i] * v[i2], Mr[(i, i2)]) for (i, i2) in Mr]
                    return TA.vlin(*terms)

                sols, nonzero = [], 0
                for v in itertools.product(range(-args.corner_box,
                                                 args.corner_box + 1), repeat=p):
                    if not any(v):
                        continue
                    got = val(list(v))
                    if TA.is_zero_in_WQ(got):
                        sols.append(list(v))
                    else:
                        nonzero += 1
                corner[str(J)] = {
                    "corner_coords": len(iso),
                    "unbounded_skipped": unb,
                    "nonzero_values": nonzero,
                    "kernel_size": len(sols),
                    "kernel_sample": sols[:6],
                    "forces_top_zero": bool(iso and nonzero and not sols),
                    "vacuous": bool(nonzero == 0)}
            rec["corner"] = corner
            rec["corner_forces_truncation"] = bool(
                corner and all(d["forces_top_zero"] for d in corner.values()))
            rec["corner_vacuous"] = bool(
                corner and any(d["vacuous"] for d in corner.values()))
            rec["corner_kernel_nonempty"] = bool(
                corner and any(d["kernel_size"] for d in corner.values()))
            # a control with teeth: the SAME test on the coordinates of `c_0`,
            # which no far generator can isolate -- it must find nothing
            cn = 0
            for (kd, nm), v in fr.base.items():
                blocks, unb = R.of(nm)
                if not unb and blocks and blocks <= {
                        ("L0", 0, args.forcing_shifts[0]),
                        ("Q0", args.forcing_shifts[0], args.forcing_shifts[0])}:
                    cn += 1

        except TR.TimeBudget as e:
            rec["status"] = "SKIPPED_TIME_BUDGET"
            rec["detail"] = str(e)
            rec["passed"] = True
            out.append(rec)
            print(json.dumps({"chain": r["chain"],
                              "status": rec["status"]}), flush=True)
            _dump(args, "blocks", {"partial": True, "chains": len(out)}, out)
            continue
        rec["CB1_c0_coords_claimed_isolated"] = cn
        rec["passed"] = (cn == 0)
        rec["secs"] = round(time.time() - t0, 2)
        out.append(rec)
        print(json.dumps({k2: rec[k2] for k2 in
                          ("chain", "directions_used", "pure_power_sources",
                           "corner_forces_truncation", "corner_vacuous",
                           "corner_kernel_nonempty", "secs") if k2 in rec}),
              flush=True)
        _dump(args, "blocks", {"partial": True, "chains": len(out)}, out)
    summ = {
        "chains": len(out),
        "analysable": sum(1 for o in out if o.get("directions_used")),
        "corner_forces_truncation": sum(
            1 for o in out if o.get("corner_forces_truncation")),
        "corner_kernel_nonempty": sum(
            1 for o in out if o.get("corner_kernel_nonempty")),
        "corner_vacuous": sum(1 for o in out if o.get("corner_vacuous")),
        "forcing_single_direction": sum(
            1 for o in out if o.get("forcing_holds_at")),
        "CB1_control_violations": sum(
            o.get("CB1_c0_coords_claimed_isolated", 0) for o in out),
        "controls_passed": all(o.get("passed", True) for o in out)
        and bool(out),
    }
    print(json.dumps({"summary": summ}), flush=True)
    _dump(args, "blocks", summ, out)
    return 0 if summ["controls_passed"] else 2


# ------------------------------------------------------------------ mode S


def mode_span(args, rows):
    """Is the Hecke closure of the native seed all of the directions we can
    manufacture?  Directions made by STRUCTURALLY different generators (far
    translated seeds, deeper `kernel-rho`, the source-pair pass) are tested
    for membership in the `Z`-span of the Hecke closure."""
    sel = TA._slice(rows, args.chains)
    done = _resume(args)
    out = list(done.values())
    t_run = time.time()
    for r in sel:
        key = tuple(r["chain"]) + (r["g_gen"],)
        if key in done:
            continue
        if args.run_seconds and time.time() - t_run > args.run_seconds:
            break
        t0 = time.time()
        rec = {"chain": r["chain"], "g": r["g_gen"]}
        ch, g, ops, defect, h, _sh = TR.setup(r, tuple(args.window))
        sol = TR.solve_layer1(ops, defect, tuple(args.rhos))
        if not sol["ok"]:
            rec["status"] = "LAYER1_UNSOLVED_AT_RHO"
            rec["passed"] = True
            out.append(rec)
            _dump(args, "span", {"partial": True, "chains": len(out)}, out)
            continue
        cp = IL.Completed(GS.Folded(GS.gamma_gens(ch, g)))
        native = TR.kernel_directions(ops, defect, args.m, args.kernel_rho,
                                      cp=cp)
        rec["native"] = len(native)
        if not native:
            rec["status"] = "NO_KERNEL_DIRECTION_FOUND"
            rec["passed"] = True
            out.append(rec)
            _dump(args, "span", {"partial": True, "chains": len(out)}, out)
            continue
        # the Hecke closure of the native seed, every element re-verified
        words = [w for w in args.span_hecke.split(",") if w]
        closure = list(native)
        bad = 0
        for s in words:
            aq = wq(s)
            for F in native:
                F2 = TC.hecke_dir(aq, F)
                if not any(F2):
                    continue
                if IL.verify({}, ops, F2):
                    bad += 1
                    continue
                closure.append(F2)
        rec["hecke_closure"] = len(closure)
        rec["hecke_rejected"] = bad
        Z = IL.ZEchelon(order=lambda c: (c[0], len(c[1]), c[1]))
        for i, F in enumerate(closure):
            Z.add(TC.flat_dir(F), ("h", i))
        # probe directions from structurally different generators
        probes, tags = [], []
        for sh in [s for s in args.probe_shifts.split(",") if s]:
            qw = QR(LV.to_tuple(sh))
            seed = {CV(QM(qw, v)): 1 for v in defect}
            for F in TR.kernel_directions(ops, seed, args.probe_m,
                                          args.kernel_rho, cp=cp):
                probes.append(F)
                tags.append(f"far:{sh}")
        for rho in args.probe_rhos:
            for F in TR.kernel_directions(ops, defect, args.probe_m, rho,
                                          cp=cp):
                probes.append(F)
                tags.append(f"rho:{rho}")
        for F in TR.kernel_directions(ops, defect, args.probe_m,
                                      args.kernel_rho, cp=None):
            probes.append(F)
            tags.append("nosrc")
        nt = nout = 0
        outside_tags = {}
        for F, tg in zip(probes, tags):
            if IL.verify({}, ops, F):
                continue
            nt += 1
            member, _c = Z.member(TC.flat_dir(F))
            if not member:
                nout += 1
                outside_tags[tg] = outside_tags.get(tg, 0) + 1
                Z.add(TC.flat_dir(F), ("p", nout))
        rec["probe_directions"] = nt
        rec["probe_outside_hecke_span"] = nout
        rec["probe_outside_by_tag"] = outside_tags
        rec["hecke_span_catches_all_probes"] = (nout == 0)
        rec["passed"] = (bad == 0)
        rec["secs"] = round(time.time() - t0, 2)
        out.append(rec)
        print(json.dumps({k2: rec[k2] for k2 in
                          ("chain", "native", "hecke_closure",
                           "probe_directions", "probe_outside_hecke_span",
                           "secs") if k2 in rec}), flush=True)
        _dump(args, "span", {"partial": True, "chains": len(out)}, out)
    summ = {
        "chains": len(out),
        "analysable": sum(1 for o in out if o.get("native")),
        "hecke_rejected_total": sum(o.get("hecke_rejected", 0) for o in out),
        "probe_directions": sum(o.get("probe_directions", 0) for o in out),
        "probe_outside_hecke_span": sum(
            o.get("probe_outside_hecke_span", 0) for o in out),
        "chains_where_hecke_span_catches_all": sum(
            1 for o in out if o.get("hecke_span_catches_all_probes")),
        "chains_with_a_probe_outside": sum(
            1 for o in out if o.get("probe_outside_hecke_span")),
        "controls_passed": all(o.get("passed", True) for o in out)
        and bool(out),
    }
    print(json.dumps({"summary": summ}), flush=True)
    _dump(args, "span", summ, out)
    return 0 if summ["controls_passed"] else 2


# ------------------------------------------------------------------- misc


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
            {"schema": f"acsolverx.w2n.{name}.v1", "summary": summ,
             "rows": rows_out}, indent=1))


def _roundtrip_control():
    """CW0: `literal`/`parse_quotient` round-trips on double-coset reps, and
    `dcoset_rep` really is a class function -- the whole de-shift frame is
    built on both."""
    ok = bad = 0
    for s in ("t", "T", "tt", "tct", "tcT", "ctc", "tctct", "tcttct",
              "ttcTT", "tcTcT", "tttt", "tcttcttt"):
        z = QR(LV.to_tuple(s))
        d = DC(z)
        ok += 1
        if lift.parse_quotient(LIT(d)) != d:
            bad += 1
        for h1 in ((), CC):
            for h2 in ((), CC):
                ok += 1
                if DC(QM(h1, z, h2)) != d:
                    bad += 1
    return ok, bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("law", "blocks", "span"),
                    default="law")
    ap.add_argument("--chains", type=str, default="")
    ap.add_argument("--window", type=int, nargs=4, default=[0, 0, 0, 0])
    ap.add_argument("--rhos", type=int, nargs="+", default=[2])
    ap.add_argument("--m", type=int, default=4)
    ap.add_argument("--kernel-rho", type=int, default=2)
    ap.add_argument("--dirs-scan", type=int, default=1)
    ap.add_argument("--decide-dirs", type=int, default=2)
    ap.add_argument("--mix-gap", type=int, default=4)
    ap.add_argument("--max-shift", type=int, default=20)
    ap.add_argument("--test-level", choices=("lean", "full"), default="lean")
    ap.add_argument("--min-above", type=int, default=6)
    ap.add_argument("--chain-seconds", type=float, default=0.0)
    ap.add_argument("--form-shift", type=int, default=8)
    ap.add_argument("--forcing-shifts", type=int, nargs="+",
                    default=[8, 10, 12])
    ap.add_argument("--corner-box", type=int, default=3)
    ap.add_argument("--span-hecke", type=str, default="t,tt,T,ct,tct")
    ap.add_argument("--probe-shifts", type=str,
                    default="tt,TT,tctc,ctc,tttt,TTTT,ct,tc")
    ap.add_argument("--probe-m", type=int, default=4)
    ap.add_argument("--probe-rhos", type=int, nargs="+", default=[3])
    ap.add_argument("--detail", action="store_true")
    ap.add_argument("--run-seconds", type=float, default=0.0)
    ap.add_argument("--json", type=str, default="")
    args = ap.parse_args()
    c1 = LV.analyze(PS.WITNESS, fixed_h=PS.CODEX_H)
    got = (c1["defect_terms"], c1["defect_l1"], c1["defect_augmentation"])
    n_rt, bad_rt = _roundtrip_control()
    print(json.dumps({"control": "C1_fixed_h_witness", "defect": list(got),
                      "want": [21, 48, 0], "passed": got == (21, 48, 0),
                      "CW0_dcoset_frame": f"{n_rt - bad_rt}/{n_rt}"}),
          flush=True)
    if got != (21, 48, 0) or bad_rt:
        return 2
    rows = GS.load_rows()
    return {"law": mode_law, "blocks": mode_blocks,
            "span": mode_span}[args.mode](args, rows)


if __name__ == "__main__":
    sys.exit(main())
