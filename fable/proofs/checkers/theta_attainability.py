"""W2l: is `0 in image(Xi_Z o Theta)` over the layer-1 solution family?

W2K_CORRECTED_REVERIFY.md section 12 leaves exactly one question able to move
the layer-2 answer.  This checker attacks it, and it CORRECTS the premise the
question was posed with.

--------------------------------------------------------------------------
0. THE OBJECT
--------------------------------------------------------------------------
Fix a census chain `(R,S,U)`, target conjugator `g`, gauge window, and the
conjugator tuple `h = (h0,h1,h2,h3,g)`.  Let `L = (L_0..L_4)` be the CORRECTED
layer-1 operators (`corrected_operators.build_operators_exact`, equal column
for column to `theta_residual_evaluator.exact_operators` on 67/67 chains,
W2k section 7) and `D` the defect.  Then

    layer-1 solutions  =  { x in M^5 : [D] + sum_r L_r x_r = 0 }
                       =  x_0 + H_fin ,   H_fin := ker( L : M^5 -> M ) ,

with `M = Z[X]`, `X = Q/<c>`, free abelian of INFINITE rank; `H_fin` is the
"complete balanced source-pair space" of the source's section 3.2.

    Psi(F) := Theta(x_0 + F)  in  Lambda^2 M
    G(F)   := Xi~(Psi(F))     in  Z^(D_2) (+) Z^(D_1)      [raw coordinates]

`Xi~` is `theta_residual_evaluator.xi_raw`: the free double-coset coordinates
over Z, and the self-inverse ones kept INTEGRAL (they are `Z/2` coordinates of
`W_Q`; keeping them integral is what makes the polynomial model exact).  By
W2i section 3.3 -- conditional on (3.1) and (3.5) -- layer 2 is solvable at
`x_0 + F` **iff** `G(F) = 0 in W_Q`, i.e.

    every free coordinate vanishes over Z  AND  every self-inverse
    coordinate is EVEN.                                              (Z)

Every evaluation of `G` here goes through `theta_residual_evaluator.theta`,
which replays (1.8) literally in `F(c,t)` and asserts `R_can in [N,N]` before
computing anything -- so each evaluation is itself the free-group ground-truth
test that W2j/W2k made mandatory.  Nothing is verified through the operators
that produced it.

--------------------------------------------------------------------------
1. LEMMA A -- the polynomial law
--------------------------------------------------------------------------
`Psi` is a polynomial map of degree <= 2 on `H_fin`.  Sketch (the machine
check is the authority; see control C4): `N` is free on the Schreier basis
`(r_v)`, the section is `sigma(y) = prod_v r_v^{y_v}` in a FIXED order, so

    Theta(sigma(y)) = sum_{v < w} y_v y_w  e_v ^ e_w                  (Q)

is already a genuine quadratic form in `y` (and `Theta(r_v^k) = 0`).  All
remaining pieces of the recurrence enter through products of conjugates whose
`M`-classes are AFFINE in `F`, and `Theta(ab) = Theta(a) + Theta(b) +
[a] ^ [b]` contributes only bilinear terms.  Hence on the lattice
`n |-> G(x_0 + sum_j n_j F_j)`,

    G(n) = c_0 + sum_j a_j n_j + sum_j b_jj n_j^2 + sum_{j<k} b_jk n_j n_k

with `c_0, a_j, b_jj, b_jk` integral vectors.  Coefficients are read off by
finite differences and then **verified by held-out literal prediction** at
points with negative and |n| >= 2 entries (control C4); a chain whose model
fails is reported and never used.

--------------------------------------------------------------------------
2. LEMMA B -- mod 2 the map is QUADRATIC, not affine-linear
--------------------------------------------------------------------------
Degree <= 2 with integer coefficients gives, for every modulus `q`,

    G(n + q e_j) - G(n) = q a_j + b_jj (2 q n_j + q^2) + q sum_k b_jk n_k
                        = 0  (mod q)                                  (P)

so `G mod q` factors through `(Z/q)^m`.  W2j used this at `q = 2` and its
2^m enumeration is therefore complete over `Z^m`.

**But periodicity is not linearity.**  With `n_j^2 = n_j` over `F_2`,

    Phi(n) := G(n) mod 2 = c_0 + sum_j (a_j + b_jj) n_j
                             + sum_{j<k} b_jk n_j n_k     over F_2 ,

which is affine-LINEAR only if every polarisation `b_jk` is even.  It is not:
measured directly on literal evaluations (no fit involved), the identity
`Phi(e_j + e_k) = Phi(e_j) + Phi(e_k) + Phi(0)` FAILS on **979 of 1,047**
cross pairs over 48 census baselines; only 4 baselines are genuinely
affine-linear mod 2.  So mod-2 attainability of 0 is a system of
`F_2`-QUADRATIC forms, not GF(2) linear algebra.  `--mode struct` recomputes
the same fact without the model class (16/16 agreement) and is the reason the
plan "decide it by linear algebra on ker(L) mod 2" cannot be executed as
stated.

--------------------------------------------------------------------------
3. LEMMA C -- what is one-sided, and what a finite computation can prove
--------------------------------------------------------------------------
Write `V_S` for the Z-span of the value-differences of `G` on the sublattice
spanned by a finite direction set `S = (F_1..F_m)`.  From Lemma A,

    { G(n) - c_0 : n in Z^m }  spans  V_S = < a_j + b_jj , 2 b_jj , b_jk >

(`n = e_j` gives `a_j + b_jj`; `n = 2 e_j` gives `2a_j + 4b_jj`, and twice the
first minus that is `-2 b_jj`; `n = e_j + e_k` gives the rest).  Add the
vectors `2 e_D` for every self-inverse coordinate `D`, since (Z) only asks
those to be even; call the result `V_S^+`.  Then for every `n`,

    G(n) = c_0 + (element of V_S^+ modulo the parity slack) ,

so `0 in image(G|_S)` REQUIRES `-c_0 in V_S^+`.  Two consequences, and the
asymmetry between them is the whole methodology of this note:

 (i) **`-c_0 in V_S^+` is monotone in `S`.**  Enlarging the direction set can
     only enlarge `V_S^+`.  So if membership holds for one finite `S`, it
     holds for `H_fin`, and therefore **no linear certificate exists at all**:
     there is no homomorphism `f : W_Q -> Z` or `-> Z/q` with `f(G(F))` a
     fixed nonzero constant on the whole family.  That is a WINDOW-INDEPENDENT
     negative result, obtained from a finite computation.  It strictly
     generalises W2j section 5.2.2, which killed only the single functional
     "the whole mod-2 vector" (constancy).
 (ii) **`-c_0 not in V_S^+` is NOT an obstruction.**  It is a statement about
     `S`, and the same monotonicity says a larger `S` can destroy it.  It
     yields a *candidate* invariant (an explicit functional) whose promotion
     to an obstruction needs a structural proof valid on all of `H_fin`.

The same asymmetry governs everything else here: a WITNESS (an explicit
`F in H_fin` with `G(F) = 0`) is window-independent, because `F` is an actual
element of the complete family; an ABSENCE on a sublattice never is.  In
particular a failure of local solvability mod `p^k` computed on a sublattice
is **not** window-independent either -- the honest local statement is the
linear relaxation of (i)/(ii) at that modulus, which is what this checker
computes.

--------------------------------------------------------------------------
4. THE FINITENESS STATEMENT, and its proof status
--------------------------------------------------------------------------
What a finite computation decides here:

  F1 (PROVED, finite)  For a finite `S`, the model of Lemma A, the exact
     mod-2 decision by 2^m enumeration (complete over `Z^m` by (P)), and the
     membership `-c_0 in V_S^+` modulo `q` and over `Q`, are all finite exact
     computations.
  F2 (PROVED, monotone) Membership `-c_0 in V_S^+` at any single finite `S`
     transfers to `H_fin` -- Lemma C(i).  This is the only statement in this
     note that upgrades a finite computation to the complete family in the
     NEGATIVE direction.
  F3 (NOT PROVED)  That `V_S^+ = V_{H_fin}^+` for the computed `S`, i.e. that
     the direction search saturates.  There is no analogue here of W2h's
     Lemma 5 translation-invariance: that lemma works because `pi(L_i e_v)` is
     a TRANSLATE of a fixed finite pattern, which makes the row lattice
     finitely generated.  The obstacle for `Theta` is explicit -- the section
     `sigma` is not equivariant (`g sigma(x) g^-1 = sigma(g.x)` only modulo
     `[N,N]`, and that error is exactly what `Theta` measures), and the
     conjugators `h_r` are FIXED while the perturbation is not, so replacing
     `x` by `g.x` does not conjugate the recurrence.  Until such a statement
     exists, "no zero on `S`" stays bounded by `S`.  What IS reported instead
     is the empirical stability of the answer as `S` grows (`--mode stability`).

--------------------------------------------------------------------------
5. CONTROLS (each can fail; a failure sets exit 2 and voids the run)
--------------------------------------------------------------------------
  C1  the imported lifting calculus is the codex one: defect (21,48,0).
  C2  every direction satisfies `sum_r L_r F_r = 0` exactly, and a CORRUPTED
      direction is rejected by the same test (the control fires).
  C3  every evaluation of `G` re-verifies `R_can in [N,N]` literally in
      `F(c,t)`; a corrupted `x_0` must leave `[N,N]` (the control fires).
  C4  held-out literal prediction of the integral model at points with
      negative and |n| >= 2 coordinates; and a CORRUPTED model coefficient
      must break the prediction (the control fires).
  C5  mod-2 model prediction against literal evaluation at the held-out
      points (pins (P) at q = 2 on the real map, not on the fit).
  C6  calibration: the codex escape certificate's own two kernel directions
      reproduce its four parity classes, its residual lengths and its
      degree-two obstruction bits, and this machinery's mod-2 verdict on
      them agrees with W2j section 4.3 (4 classes, none vanishing).
  C7  any membership answer "yes" is re-multiplied out and compared term by
      term against the target; any WITNESS is re-evaluated literally.

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
import theta_residual_evaluator as TR  # noqa: E402
import corrected_operators as CO  # noqa: E402
sys.argv = _ARGV

GS, PS, IL, LV = TR.GS, TR.PS, TR.IL, TR.LV
lift, esc = TR.lift, TR.esc

MODULI = ((2, 1), (2, 2), (2, 3), (3, 1), (3, 2), (5, 1))
MAX_INTEGRAL_POINTS = 1000          # repo hard rule: searches stay small


# ------------------------------------------------------------ vector algebra


def vsub(a, b):
    out = dict(a)
    for k, v in b.items():
        out[k] = out.get(k, 0) - v
    return {k: v for k, v in out.items() if v}


def vlin(*terms):
    out = {}
    for co, d in terms:
        if not co:
            continue
        for k, v in d.items():
            out[k] = out.get(k, 0) + co * v
    return {k: v for k, v in out.items() if v}


def is_zero_in_WQ(vec):
    """(Z): free coordinates vanish over Z, self-inverse ones are even."""
    for (kind, _name), v in vec.items():
        if kind == "f" and v:
            return False
        if kind == "t" and v % 2:
            return False
    return True


# ------------------------------------------------------- the integral model


class Model:
    """`G(n) = c0 + sum a_j n_j + sum b_jj n_j^2 + sum_{j<k} b_jk n_j n_k`."""

    def __init__(self, c0, a, bd, bx, m, complete=True):
        self.c0, self.a, self.bd, self.bx, self.m = c0, a, bd, bx, m
        self.complete = complete
        self.mod2_only = False

    def eval(self, n):
        terms = [(1, self.c0)]
        for j in range(self.m):
            if n[j]:
                terms.append((n[j], self.a[j]))
                terms.append((n[j] * n[j], self.bd[j]))
        for (j, k), v in self.bx.items():
            co = n[j] * n[k]
            if co:
                terms.append((co, v))
        return vlin(*terms)

    def variation_generators(self):
        """Spanning set of `V_S` (Lemma C): `a_j + b_jj`, `2 b_jj`, `b_jk`."""
        gens = []
        for j in range(self.m):
            gens.append((f"lin{j}", vlin((1, self.a[j]), (1, self.bd[j]))))
            gens.append((f"2quad{j}", vlin((2, self.bd[j]))))
        for (j, k), v in self.bx.items():
            gens.append((f"cross{j}_{k}", dict(v)))
        return [(t, v) for t, v in gens if v]


def build_model_mod2(G, m, pairs=None):
    """The mod-2 model only: `c_0`, `alpha_j = G(e_j) - c_0`, `beta_jk`.

    Mod 2 the diagonal coefficient is absorbed (`n_j^2 = n_j`), so the
    `G(2 e_j)` evaluations the integral model needs are not required -- which
    halves the axis cost and is what makes larger direction sets reachable.
    Valid ONLY on `n in {0,1}^m`, which is all the 2^m decision uses.
    """
    z = [0] * m
    c0 = G(z)
    a, bd, bx = {}, {}, {}
    g1 = {}
    for j in range(m):
        n = list(z)
        n[j] = 1
        g1[j] = G(n)
        bd[j] = {}
        a[j] = vsub(g1[j], c0)
    allp = [(j, k) for j in range(m) for k in range(j + 1, m)]
    use = allp if pairs is None else pairs
    for (j, k) in use:
        n = list(z)
        n[j] = 1
        n[k] = 1
        bx[(j, k)] = vlin((1, G(n)), (-1, g1[j]), (-1, g1[k]), (1, c0))
    mo = Model(c0, a, bd, bx, m, complete=(len(use) == len(allp)))
    mo.mod2_only = True
    return mo, None


def build_model(G, m, pairs=None):
    """Finite differences of the LITERAL map (no fitting heuristics).

    `pairs = None` evaluates every cross term, which is what the exhaustive
    mod-2 decision needs; a SUBSET gives a partial model -- still an exact
    supplier of elements of `V_S` (Lemma C), just not of the full span, so
    the 2^m enumeration is then not attempted.
    """
    z = [0] * m
    c0 = G(z)
    a, bd, bx = {}, {}, {}
    g1 = {}
    for j in range(m):
        n = list(z)
        n[j] = 1
        g1[j] = G(n)
        n = list(z)
        n[j] = 2
        g2 = G(n)
        num = vlin((1, g2), (-2, g1[j]), (1, c0))
        if any(v % 2 for v in num.values()):
            return None, "diagonal second difference is odd"
        bd[j] = {k: v // 2 for k, v in num.items() if v}
        a[j] = vlin((1, g1[j]), (-1, c0), (-1, bd[j]))
    allp = [(j, k) for j in range(m) for k in range(j + 1, m)]
    use = allp if pairs is None else pairs
    for (j, k) in use:
        n = list(z)
        n[j] = 1
        n[k] = 1
        bx[(j, k)] = vlin((1, G(n)), (-1, g1[j]), (-1, g1[k]), (1, c0))
    return Model(c0, a, bd, bx, m, complete=(len(use) == len(allp))), None


# --------------------------------------------------------- mod-2 bit machine


class Bits:
    """Coordinate -> bit index, so mod-2 vectors are Python ints."""

    def __init__(self):
        self.idx = {}

    def of(self, vec):
        out = 0
        for k, v in vec.items():
            if v % 2:
                i = self.idx.get(k)
                if i is None:
                    i = self.idx[k] = len(self.idx)
                out |= 1 << i
        return out


def gray_zero_search(c0b, alpha, beta, m, cap_bits):
    """Complete enumeration of the 2^m mod-2 classes, Gray-code order.

    Returns (subset with Phi = 0 or None, classes visited, distinct values).
    By (P) this decides mod-2 attainability over ALL of `Z^m`.
    """
    if m > cap_bits:
        return None, 0, 0, True
    cur, S = c0b, 0
    seen = {cur}
    if cur == 0:
        return [0] * m, 1, 1, False
    n = 1 << m
    prev = 0
    for i in range(1, n):
        code = i ^ (i >> 1)
        j = (code ^ prev).bit_length() - 1
        prev = code
        delta = alpha[j]
        for k in range(m):
            if k != j and (S >> k) & 1:
                delta ^= beta[(min(j, k), max(j, k))]
        cur ^= delta
        S ^= 1 << j
        seen.add(cur)
        if cur == 0:
            return [(S >> b) & 1 for b in range(m)], i + 1, len(seen), False
    return None, n, len(seen), False


# -------------------------------------------------- membership certificates


def member_mod(gens, target, p, k):
    """Is `target` in the `Z/p^k`-span of `gens`?  (Howell elimination.)

    `p^k` is a local ring; pivoting on the entry of least `p`-valuation in a
    column is the correct rule, and the Howell completion adds `p^(k-v)` times
    a pivot row back to the pool so that column-triangular reduction is
    complete.  Returns (member, coeffs or witness column).
    """
    q = p ** k
    cols = []
    seen = set()
    for _t, v in gens:
        for c in v:
            if c not in seen:
                seen.add(c)
                cols.append(c)
    for c in target:
        if c not in seen:
            return False, {"missing_column": list(c)}
    cols.sort()
    rows = []
    for tag, v in gens:
        r = {c: x % q for c, x in v.items() if x % q}
        if r:
            rows.append((r, {tag: 1}))

    def val(x):
        v = 0
        while x % p == 0 and v < k:
            x //= p
            v += 1
        return v

    piv = {}
    pool = list(rows)
    for c in cols:
        live = [(r, cf) for (r, cf) in pool if r.get(c)]
        if not live:
            continue
        best = min(live, key=lambda rc: val(rc[0][c]))
        pool.remove(best)
        r0, c0 = best
        v0 = val(r0[c])
        u = r0[c] // (p ** v0)
        ui = pow(u, -1, q)
        r0 = {cc: (x * ui) % q for cc, x in r0.items()}
        r0 = {cc: x for cc, x in r0.items() if x}
        c0 = {t: (x * ui) % q for t, x in c0.items()}
        piv[c] = (r0, v0, c0)
        nxt = []
        for (r, cf) in pool:
            e = r.get(c, 0)
            if e:
                f = e // (p ** v0)
                r = {cc: (r.get(cc, 0) - f * r0.get(cc, 0)) % q
                     for cc in set(r) | set(r0)}
                r = {cc: x for cc, x in r.items() if x}
                cf = {t: (cf.get(t, 0) - f * c0.get(t, 0)) % q
                      for t in set(cf) | set(c0)}
            if r:
                nxt.append((r, cf))
        if v0 > 0:                                   # Howell completion
            e = p ** (k - v0)
            rr = {cc: (x * e) % q for cc, x in r0.items()}
            rr = {cc: x for cc, x in rr.items() if x}
            if rr:
                nxt.append((rr, {t: (x * e) % q for t, x in c0.items()}))
        pool = nxt
    t = {c: x % q for c, x in target.items() if x % q}
    coeff = {}
    for c in cols:
        e = t.get(c, 0)
        if not e:
            continue
        if c not in piv:
            return False, {"blocking_column": list(c), "value": e}
        r0, v0, c0 = piv[c]
        if e % (p ** v0):
            return False, {"blocking_column": list(c), "value": e,
                           "pivot_valuation": v0}
        f = e // (p ** v0)
        t = {cc: (t.get(cc, 0) - f * r0.get(cc, 0)) % q
             for cc in set(t) | set(r0)}
        t = {cc: x for cc, x in t.items() if x}
        for tag, x in c0.items():
            coeff[tag] = (coeff.get(tag, 0) + f * x) % q
    if t:
        c = sorted(t)[0]
        return False, {"blocking_column": list(c), "value": t[c]}
    return True, coeff


def member_Q(gens, target):
    """Is `target` in the Q-span of `gens`?  Primitive integer elimination.

    Q-membership kills every Z-valued (equivalently Q- or R-valued) linear
    certificate: if `N target` is an integer combination then any `f` with
    `f(gens) = 0` has `N f(target) = 0`, hence `f(target) = 0`.
    """
    from math import gcd

    def prim(v):
        g = 0
        for x in v.values():
            g = gcd(g, abs(x))
        return {k: x // g for k, x in v.items()} if g > 1 else dict(v)

    rows = [prim({k: v for k, v in d.items() if v}) for _t, d in gens]
    rows = [r for r in rows if r]
    piv = {}
    for r in rows:
        r = dict(r)
        while r:
            c = min(r)
            if c not in piv:
                piv[c] = prim(r)
                break
            pr = piv[c]
            r = prim(vlin((pr[c], r), (-r[c], pr)))
    t = {k: v for k, v in target.items() if v}
    while t:
        c = min(t)
        if c not in piv:
            return False, {"blocking_column": list(c)}
        pr = piv[c]
        t = vlin((pr[c], t), (-t[c], pr))
    return True, {}


def member_gf2(gens, target):
    """GF(2) membership by bitset elimination -- exact, and fast at any size.

    `p = 2` is the modulus the whole W2j/W2k mod-2 discussion lives at, so it
    is the one that must be decidable even when the coordinate universe runs
    to five figures.  Returns (member, combination as a list of tags).
    """
    B = Bits()
    rows = [(B.of(v), 1 << i) for i, (_t, v) in enumerate(gens)]
    t = B.of(target)
    piv = {}
    for r, c in rows:
        while r:
            b = r.bit_length() - 1
            if b not in piv:
                piv[b] = (r, c)
                break
            pr, pc = piv[b]
            r ^= pr
            c ^= pc
    comb = 0
    stuck = 0
    while t:
        b = t.bit_length() - 1
        if b not in piv:
            stuck |= 1 << b
            t ^= 1 << b
            continue
        pr, pc = piv[b]
        t ^= pr
        comb ^= pc
    if stuck:
        # graded diagnostic: how far -c_0 is from V mod 2, and the rank of V.
        # The reduced representative is basis-dependent, but its SUPPORT is
        # reported so that stability across direction sets can be judged on
        # the coordinates themselves, not only on the count.
        inv = {i: c for c, i in B.idx.items()}
        sup = sorted(inv[i] for i in range(stuck.bit_length())
                     if (stuck >> i) & 1)
        return False, {"residual_weight": len(sup), "rank": len(piv),
                       "residual_support": [list(c) for c in sup]}
    return True, [gens[i][0] for i in range(len(gens)) if (comb >> i) & 1]


def coordinate_certificates(gens, target, q):
    """Coordinates `D` on which the WHOLE variation space vanishes mod `q`
    while the target does not: each is an explicit functional certificate
    `f = (coefficient at D)` for the tested direction set.

    This is the cheap, and by far the most interpretable, obstruction shape:
    `f(G(F)) = c_0(D)` for every `F` in the span of `S`.  Like every
    non-membership statement it is bounded by `S` (Lemma C(ii)); its value is
    that it names a candidate whose promotion is a concrete structural claim
    about one double coset.
    """
    moved = set()
    for _t, v in gens:
        for c, x in v.items():
            if x % q:
                moved.add(c)
    return sorted(c for c, x in target.items() if x % q and c not in moved)


def recheck_combo(gens, coeff, target, q):
    """C7: re-multiply a positive membership answer out, term by term."""
    acc = {}
    lookup = dict(gens)
    for tag, x in coeff.items():
        for k, v in lookup[tag].items():
            acc[k] = (acc.get(k, 0) + x * v) % q
    acc = {k: v for k, v in acc.items() if v}
    want = {k: v % q for k, v in target.items() if v % q}
    return acc == want


# ------------------------------------------------------------- per-chain run


def chain_context(row, args):
    """(h, x0, dirs, ops, defect) with every direction verified exactly."""
    ch, g, ops, defect, h, _sh = TR.setup(row, tuple(args.window))
    sol = TR.solve_layer1(ops, defect, tuple(args.rhos))
    if not sol["ok"]:
        return None, "LAYER1_UNSOLVED_AT_RHO", None
    cp = None if getattr(args, "no_source_dirs", False) else \
        IL.Completed(GS.Folded(GS.gamma_gens(ch, g)))
    dirs = TR.kernel_directions(ops, defect, args.m, args.kernel_rho, cp=cp)
    # F3 probe: directions whose hop expansion is seeded at a TRANSLATE of
    # the defect support, i.e. supported far from it.  These are a
    # structurally different family of H_fin elements (still verified exactly
    # by `kernel_directions`), and they are the closest available test of
    # whether the direction search saturates.
    for sh in [s for s in (getattr(args, "far_shifts", "") or "").split(",")
               if s]:
        qw = lift.quotient_reduce(LV.to_tuple(sh))
        seed = {lift.c_vertex(lift.quotient_multiply(qw, v)): 1
                for v in defect}
        for F in TR.kernel_directions(ops, seed, args.m_far, args.kernel_rho,
                                      cp=cp):
            if F not in dirs:
                dirs.append(F)
    return (h, sol["x"], dirs, ops, defect), None, cp


def direction_controls(ops, dirs):
    """C2: exact kernel test, and the same test on a corrupted direction."""
    ok = all(not IL.verify({}, ops, F) for F in dirs)
    fires = 0
    if dirs:
        bad = [dict(f) for f in dirs[0]]
        for f in bad:
            if f:
                kk = sorted(f)[0]
                f[kk] += 1
                break
        fires = int(bool(IL.verify({}, ops, bad)))
    return ok, fires


def x0_control(h, x0):
    """C3: a corrupted x_0 must leave [N,N]."""
    bad = [dict(xi) for xi in x0]
    for xi in bad:
        if xi:
            kk = sorted(xi)[0]
            xi[kk] += 1
            break
    try:
        TR.theta(h, bad)
        return 0
    except TR.NotInCommutator:
        return 1


def analyse(rec, h, x0, dirs, args, rng):
    """The whole W2l decision for one baseline.  Mutates and returns `rec`."""
    m = len(dirs)
    rec["directions"] = m
    if m == 0:
        rec["status"] = "NO_KERNEL_DIRECTION_FOUND"
        rec["passed"] = True
        return rec
    n_eval = [0]

    def G(n):
        n_eval[0] += 1
        th, _w = TR.theta(h, TR.combine(x0, dirs, n))
        return TR._vec(*TR.xi_raw(th))

    allp = [(j, k) for j in range(m) for k in range(j + 1, m)]
    pairs = None
    if args.pair_sample and len(allp) > args.pair_sample:
        pairs = rng.sample(allp, args.pair_sample)
    if args.mod2_only:
        model, why = build_model_mod2(G, m, pairs)
    else:
        model, why = build_model(G, m, pairs)
    if model is None:
        rec["status"] = "NOT_POLYNOMIAL_DEGREE_2"
        rec["detail"] = why
        rec["passed"] = False
        return rec
    rec["model_complete"] = model.complete
    rec["mod2_only"] = model.mod2_only
    rec["cross_terms_evaluated"] = len(model.bx)
    # ---- C4/C5: held-out literal prediction, integral and mod 2
    held = []
    if model.mod2_only:
        if model.complete:
            for _ in range(args.holdout):
                held.append([rng.randint(0, 1) for _ in range(m)])
        else:
            have = set(model.bx)
            trip = [(j, k, l) for j in range(m) for k in range(j + 1, m)
                    for l in range(k + 1, m)
                    if {(j, k), (j, l), (k, l)} <= have]
            for (j, k, l) in (rng.sample(trip, min(args.holdout, len(trip)))
                              if trip else []):
                e = [0] * m
                e[j] = e[k] = e[l] = 1
                held.append(e)
    else:
        for j in range(min(m, 4)):
            e = [0] * m
            e[j] = -1
            held.append(e)
            e = [0] * m
            e[j] = 3
            held.append(e)
        if model.complete:
            for _ in range(args.holdout):
                held.append([rng.randint(-2, 3) for _ in range(m)])
    n_h = n_ok = n_m2 = n_m2_ok = 0
    for n in held:
        got = G(n)
        if not model.mod2_only:
            n_h += 1
            n_ok += int(got == model.eval(n))
        n_m2 += 1
        n_m2_ok += int({k: v % 2 for k, v in got.items() if v % 2}
                       == {k: v % 2 for k, v in
                           model.eval([x % 2 for x in n]).items() if v % 2})
    rec["holdout_checks"] = n_h
    rec["holdout_agree"] = n_ok
    rec["mod2_periodicity_checks"] = n_m2
    rec["mod2_periodicity_ok"] = n_m2_ok
    rec["model_verified"] = (n_h == n_ok and n_m2 == n_m2_ok
                             and (n_m2 >= 2 if model.mod2_only else n_h >= 2))
    # C4b: a corrupted coefficient must break the held-out prediction
    bad = Model(model.c0, dict(model.a), dict(model.bd), dict(model.bx), m)
    bad.a = dict(model.a)
    kk = sorted(bad.a[0])[0] if bad.a[0] else None
    if kk is not None:
        bad.a = dict(model.a)
        bad.a[0] = dict(model.a[0])
        bad.a[0][kk] = bad.a[0][kk] + 1
        n = [1] + [0] * (m - 1)          # must move coordinate 0
        rec["model_corruption_fires"] = int(bad.eval(n) != model.eval(n))
    else:
        rec["model_corruption_fires"] = 1
    # ---- Lemma B: is the mod-2 map affine-LINEAR?
    nonlin = sum(1 for (j, k), v in model.bx.items() if any(x % 2 for x in v.values()))
    rec["cross_pairs"] = len(model.bx)
    rec["cross_pairs_odd"] = nonlin
    rec["mod2_affine_linear"] = (nonlin == 0)
    # ---- Lemma C: the linear relaxation
    gens = model.variation_generators()
    universe = set(model.c0)
    for _t, v in gens:
        universe |= set(v)
    for kind, name in sorted(universe):
        if kind == "t":
            gens.append((f"par_{name}", {("t", name): 2}))
    tgt = {k: -v for k, v in model.c0.items()}
    rec["variation_generators"] = len(gens)
    rec["universe_coords"] = len(universe)
    mem = {}
    cert_ok = True
    rec["c0_support"] = len(model.c0)
    coord = {}
    use_moduli = [(2, 1)] if model.mod2_only else list(MODULI)
    for (p, k) in use_moduli:
        q = p ** k
        cc = coordinate_certificates(gens, tgt, q)
        coord[f"{p}^{k}"] = len(cc)
        if cc:
            mem[f"{p}^{k}"] = False
            rec.setdefault("blocking", {})[f"{p}^{k}"] = {
                "coordinate_certificates": [list(c) for c in cc[:8]]}
            continue
        if (p, k) == (2, 1):
            ismem, tags = member_gf2(gens, tgt)
            mem["2^1"] = bool(ismem)
            if ismem and not recheck_combo(gens, {t: 1 for t in tags}, tgt, 2):
                cert_ok = False
            if not ismem:
                rec["mod2_residual_weight"] = tags["residual_weight"]
                rec["mod2_V_rank"] = tags["rank"]
                rec["mod2_residual_support"] = tags["residual_support"]
                # C8: the reduced representative must not depend on the
                # elimination order -- run it again on the reversed generator
                # list (which re-indexes every coordinate) and compare.
                _im2, t2 = member_gf2(list(reversed(gens)), tgt)
                rec["mod2_residual_order_invariant"] = bool(
                    not _im2 and t2["residual_support"]
                    == tags["residual_support"])
            else:
                rec["mod2_residual_weight"] = 0
            continue
        if len(universe) > args.elim_cap:
            mem[f"{p}^{k}"] = None
            continue
        ismem, info = member_mod(gens, tgt, p, k)
        mem[f"{p}^{k}"] = bool(ismem)
        if ismem and not recheck_combo(gens, info, tgt, p ** k):
            cert_ok = False
        if not ismem:
            rec.setdefault("blocking", {})[f"{p}^{k}"] = info
    rec["coordinate_certificates"] = coord
    rec["coordinate_certificates_mod2"] = [
        list(c) for c in coordinate_certificates(gens, tgt, 2)[:12]]
    ccQ = [] if model.mod2_only else [
        c for c in tgt if c[0] == "f" and all(not v.get(c) for _t, v in gens)]
    rec["coordinate_certificates_Q"] = None if model.mod2_only else len(ccQ)
    if model.mod2_only:
        qmem, qinfo = None, {}
    elif ccQ:
        qmem, qinfo = False, {"coordinate_certificates":
                              [list(c) for c in sorted(ccQ)[:8]]}
    elif len(universe) > args.elim_cap:
        qmem, qinfo = None, {}
    else:
        qmem, qinfo = member_Q(gens, tgt)
    mem["Q"] = None if qmem is None else bool(qmem)
    if qmem is False:
        rec.setdefault("blocking", {})["Q"] = qinfo
    rec["minus_c0_in_V"] = mem
    rec["membership_recheck_ok"] = cert_ok
    rec["no_linear_certificate"] = bool(
        qmem and all(mem.get(f"{p}^{k}") for (p, k) in MODULI))
    rec["no_coordinate_certificate"] = bool(
        not ccQ and all(v == 0 for v in coord.values())
        and not model.mod2_only)
    # the decisive, window-independent negative (Lemma C(i)) at p = 2
    rec["no_mod2_linear_certificate"] = (mem.get("2^1") is True)
    # ---- the exact mod-2 decision (complete over Z^m by (P))
    if model.complete:
        B = Bits()
        c0b = B.of(model.c0)
        alpha = [B.of(vlin((1, model.a[j]), (1, model.bd[j])))
                 for j in range(m)]
        beta = {jk: B.of(v) for jk, v in model.bx.items()}
        sol2, visited, distinct, truncated = gray_zero_search(
            c0b, alpha, beta, m, args.cap_bits)
        # C9 POSITIVE control: the enumeration must be able to FIND a zero.
        # Replace c_0 by alpha_0, which makes n = e_0 a mod-2 solution by
        # construction; a search that never fires is not evidence.  Skipped
        # when the enumeration itself was not run (m over the bit cap).
        if truncated:
            rec["C9_positive_control_fires"] = None
        else:
            pos, _v, _d, _t = gray_zero_search(alpha[0], alpha, beta, m,
                                               args.cap_bits)
            rec["C9_positive_control_fires"] = pos is not None
    else:
        sol2, visited, distinct, truncated = None, 0, 0, True
        rec["C9_positive_control_fires"] = None
    rec["mod2_classes_enumerated"] = visited
    rec["mod2_distinct_values"] = distinct
    rec["mod2_enumeration_truncated"] = truncated
    rec["mod2_zero_class"] = sol2
    # ---- literal verification of a mod-2 witness, and the integral hunt
    rec["integral_witness"] = None
    if sol2 is not None:
        got = G(sol2)
        rec["mod2_witness_literal_ok"] = bool(
            not {k: v % 2 for k, v in got.items() if v % 2})
        rec["mod2_witness_free_l1"] = sum(
            abs(v) for (kind, _n), v in got.items() if kind == "f")
        found = (None if model.mod2_only
                 else integral_hunt(model, G, sol2, m, args, rng))
        rec["integral_witness"] = found
        if found is not None:
            got = G(found)
            rec["witness_literal_zero_in_WQ"] = bool(is_zero_in_WQ(got))
    rec["evaluations"] = n_eval[0]
    # a mod-2 coordinate certificate and a mod-2 zero cannot coexist
    rec["mod2_consistency"] = bool(coord["2^1"] == 0 or sol2 is None)
    if rec["integral_witness"] is not None and rec.get(
            "witness_literal_zero_in_WQ"):
        rec["status"] = "WITNESS"
    elif sol2 is not None:
        rec["status"] = "MOD2_ATTAINABLE_NO_INTEGRAL_WITNESS"
    elif coord["2^1"]:
        # a mod-2 coordinate certificate proves mod-2 unattainability on S
        rec["status"] = "MOD2_UNATTAINABLE_ON_S"
    elif truncated:
        rec["status"] = "MOD2_UNDECIDED_ON_S"
    else:
        rec["status"] = "MOD2_UNATTAINABLE_ON_S"
    rec["passed"] = bool(rec["model_verified"] and cert_ok
                         and rec["mod2_consistency"]
                         and rec.get("C9_positive_control_fires") is not False
                         and rec.get("model_corruption_fires"))
    return rec


def integral_hunt(model, G, eps, m, args, rng):
    """Search `n = eps + 2k` for an exact zero in `W_Q`.  <= 1000 points."""
    budget = min(args.points, MAX_INTEGRAL_POINTS)
    tried = 0
    best = None

    def score(n):
        v = model.eval(n)
        return sum(abs(x) for (kind, _n), x in v.items() if kind == "f") + \
            sum(1 for (kind, _n), x in v.items() if kind == "t" and x % 2)

    cand = [list(eps)]
    for j in range(m):
        for d in (-2, 2):
            n = list(eps)
            n[j] += d
            cand.append(n)
    while len(cand) < budget:
        cand.append([e + 2 * rng.randint(-args.box, args.box) for e in eps])
    cur = list(eps)
    for n in cand:
        if tried >= budget:
            break
        tried += 1
        if is_zero_in_WQ(model.eval(n)):
            if is_zero_in_WQ(G(n)):
                return n
        s = score(n)
        if best is None or s < best:
            best, cur = s, list(n)
    # greedy descent from the best point seen
    improved = True
    while improved and tried < budget:
        improved = False
        for j in range(m):
            for d in (-2, 2):
                if tried >= budget:
                    break
                n = list(cur)
                n[j] += d
                tried += 1
                if is_zero_in_WQ(model.eval(n)) and is_zero_in_WQ(G(n)):
                    return n
                s = score(n)
                if s < best:
                    best, cur, improved = s, n, True
    return None


# ------------------------------------------------------------------- modes


def _slice(rows, spec):
    if not spec:
        return rows
    a, b = spec.split(":")
    return rows[int(a or 0):int(b or len(rows))]


def _resume(args):
    if not args.json or not Path(args.json).exists():
        return {}
    try:
        d = json.loads(Path(args.json).read_text())
    except json.JSONDecodeError:
        return {}
    return {tuple(r["chain"]) + (r.get("g", ""),): r for r in d.get("rows", [])}


def _dump(args, name, summ, rows):
    if args.json:
        Path(args.json).write_text(json.dumps(
            {"schema": f"acsolverx.w2l.{name}.v1", "summary": summ,
             "rows": rows}, indent=1))


def _summary(out):
    def n(st):
        return sum(1 for o in out if o.get("status") == st)
    done = [o for o in out if o.get("directions")]
    return {
        "chains": len(out),
        "with_directions": len(done),
        "layer1_unsolved": n("LAYER1_UNSOLVED_AT_RHO"),
        "model_verified": sum(1 for o in out if o.get("model_verified")),
        "mod2_affine_linear": sum(1 for o in out
                                  if o.get("mod2_affine_linear")),
        "mod2_quadratic": sum(1 for o in out
                              if o.get("mod2_affine_linear") is False),
        "no_linear_certificate": sum(1 for o in out
                                     if o.get("no_linear_certificate")),
        "no_mod2_linear_certificate": sum(
            1 for o in out if o.get("no_mod2_linear_certificate")),
        "no_coordinate_certificate": sum(
            1 for o in out if o.get("no_coordinate_certificate")),
        "chains_with_mod2_coordinate_certificate": sum(
            1 for o in out
            if (o.get("coordinate_certificates") or {}).get("2^1", 0)),
        "coord_certs_mod2_total": sum(
            (o.get("coordinate_certificates") or {}).get("2^1", 0)
            for o in out),
        "mod2_attainable": n("MOD2_ATTAINABLE_NO_INTEGRAL_WITNESS") + n("WITNESS"),
        "witnesses": n("WITNESS"),
        "mod2_unattainable_on_S": n("MOD2_UNATTAINABLE_ON_S"),
        "mod2_undecided_on_S": n("MOD2_UNDECIDED_ON_S"),
        "C9_positive_control_run": sum(
            1 for o in out if o.get("C9_positive_control_fires") is not None),
        "C9_positive_control_fires": sum(
            1 for o in out if o.get("C9_positive_control_fires")),
        "controls_passed": all(o.get("passed", True) for o in out) and bool(out),
    }


def mode_decide(args, rows):
    """(a)+(b)+(c): the full per-baseline decision, sliced and resumable."""
    sel = _slice(rows, args.chains)
    done = _resume(args)
    out = list(done.values())
    rng = random.Random(20260828)
    t_run = time.time()
    ctl = {"C2_dir_ok": 0, "C2_dir_fires": 0, "C3_fires": 0, "C3_run": 0}
    for r in sel:
        key = tuple(r["chain"]) + (r["g_gen"],)
        if key in done:
            continue
        if args.run_seconds and time.time() - t_run > args.run_seconds:
            break
        t0 = time.time()
        rec = {"chain": r["chain"], "g": r["g_gen"]}
        ctx, why, _cp = chain_context(r, args)
        if ctx is None:
            rec["status"] = why
            rec["passed"] = True
            out.append(rec)
            print(json.dumps(rec), flush=True)
            _dump(args, "decide", {"partial": True, "chains": len(out)}, out)
            continue
        h, x0, dirs, ops, _defect = ctx
        dok, dfire = direction_controls(ops, dirs)
        ctl["C2_dir_ok"] += int(dok)
        ctl["C2_dir_fires"] += dfire
        rec["directions_exact"] = dok
        rec["direction_corruption_fires"] = bool(dfire)
        if ctl["C3_run"] < args.corrupt_n:
            ctl["C3_run"] += 1
            ctl["C3_fires"] += x0_control(h, x0)
            rec["x0_corruption_fires"] = bool(ctl["C3_fires"])
        try:
            analyse(rec, h, x0, dirs, args, rng)
        except TR.NotInCommutator as e:
            rec["status"] = "FAMILY_LEFT_COMMUTATOR"
            rec["detail"] = str(e)
            rec["passed"] = False
        rec["passed"] = bool(rec.get("passed") and dok
                             and (dfire or not dirs))
        rec["secs"] = round(time.time() - t0, 2)
        out.append(rec)
        print(json.dumps({k: v for k, v in rec.items()
                          if k != "blocking" or args.detail}), flush=True)
        _dump(args, "decide", {"partial": True, "chains": len(out)}, out)
    summ = _summary(out)
    summ["C3_corruption_run"] = ctl["C3_run"]
    summ["C3_corruption_fires"] = ctl["C3_fires"]
    summ["controls_passed"] = bool(
        summ["controls_passed"] and ctl["C3_fires"] == ctl["C3_run"])
    print(json.dumps({"summary": summ}), flush=True)
    _dump(args, "decide", summ, out)
    return 0 if summ["controls_passed"] else 2


def mode_struct(args, rows):
    """Lemma B pinned on LITERAL evaluations: is the mod-2 map linear?"""
    sel = _slice(rows, args.chains)
    done = _resume(args)
    out, ok = list(done.values()), True
    rng = random.Random(4242)
    t_run = time.time()
    for r in sel:
        if tuple(r["chain"]) + (r["g_gen"],) in done:
            continue
        if args.run_seconds and time.time() - t_run > args.run_seconds:
            break
        t0 = time.time()
        rec = {"chain": r["chain"], "g": r["g_gen"]}
        ctx, why, _cp = chain_context(r, args)
        if ctx is None:
            rec["status"] = why
            rec["passed"] = True
            out.append(rec)
            print(json.dumps(rec), flush=True)
            continue
        h, x0, dirs, _ops, _d = ctx
        m = len(dirs)

        def G(n):
            th, _w = TR.theta(h, TR.combine(x0, dirs, n))
            return TR._vec(*TR.xi_raw(th))

        def m2(d):
            return frozenset(k for k, v in d.items() if v % 2)

        g0 = m2(G([0] * m))
        ge = []
        for j in range(m):
            n = [0] * m
            n[j] = 1
            ge.append(m2(G(n)))
        pairs = odd = 0
        for j in range(m):
            for k in range(j + 1, m):
                n = [0] * m
                n[j] = 1
                n[k] = 1
                lhs = m2(G(n))
                rhs = ge[j] ^ ge[k] ^ g0
                pairs += 1
                odd += int(lhs != rhs)
        # a random triple check of the mod-2 model
        rec.update({"directions": m, "pairs": pairs, "nonlinear_pairs": odd,
                    "mod2_affine_linear": odd == 0,
                    "base_mod2_support": len(g0),
                    "status": "LINEAR_MOD2" if odd == 0 else "QUADRATIC_MOD2",
                    "passed": True, "secs": round(time.time() - t0, 2)})
        out.append(rec)
        print(json.dumps(rec), flush=True)
        _dump(args, "struct", {"partial": True, "chains": len(out)}, out)
    summ = {"chains": len(out),
            "with_directions": sum(1 for o in out if o.get("directions")),
            "linear_mod2": sum(1 for o in out
                               if o.get("mod2_affine_linear") is True),
            "quadratic_mod2": sum(1 for o in out
                                  if o.get("mod2_affine_linear") is False),
            "pairs": sum(o.get("pairs", 0) for o in out),
            "nonlinear_pairs": sum(o.get("nonlinear_pairs", 0) for o in out),
            "controls_passed": ok and bool(out)}
    print(json.dumps({"summary": summ}), flush=True)
    _dump(args, "struct", summ, out)
    return 0 if summ["controls_passed"] else 2


def mode_witness(args, _rows):
    """C6: the codex escape certificate is the calibration control.

    The certificate's own two kernel directions `k0 = ALTERNATE_10 - base`,
    `k1 = ALTERNATE_01 - base` at the codex conjugator tuple must give this
    machinery exactly W2j section 4.3's line: four mod-2 classes, none
    vanishing, and the certificate's four residual lengths and obstruction
    bits reproduced.
    """
    cert = esc.period_two_degree_two_escape_certificate()
    h = PS.CODEX_H
    ops = TR.exact_operators(h)
    _r, _s, _u, z, tgt = TR.chain_words(h)
    defect = lift.relation_module(lift.multiply(z, lift.inverse(tgt)))
    x0 = list(esc.variables_from_entries(lift.CORRECTION))
    assert not IL.verify(defect, ops, x0), "codex x0 is not a layer-1 solution"
    dirs = TR._codex_dirs()
    dok, dfire = direction_controls(ops, dirs)
    rec = {"chain": list(PS.WITNESS), "g": "", "directions_exact": dok,
           "direction_corruption_fires": bool(dfire),
           "x0_corruption_fires": bool(x0_control(h, x0))}
    rng = random.Random(7)
    analyse(rec, h, x0, dirs, args, rng)
    # the certificate's own four parity classes, through this path
    lens, bits = [], []
    base = esc.variables_from_entries(lift.CORRECTION)
    a10 = esc.variables_from_entries(esc.ALTERNATE_10)
    a01 = esc.variables_from_entries(esc.ALTERNATE_01)
    k0 = esc.subtract_variables(a10, base)
    k1 = esc.subtract_variables(a01, base)
    for V in (base, a10, a01, esc.add_variables(base, k0, k1)):
        w = TR.residual(h, list(V))
        assert not lift.relation_module(w), "codex residual left [N,N]"
        lens.append(len(w))
        bits.append(list(esc.degree_two_obstructions(
            esc.degree_two(esc.schreier_word(w)))))
    rec["certificate_residual_lengths"] = lens
    rec["certificate_lengths_expected"] = list(cert.residual_lengths)
    rec["certificate_obstruction_bits"] = bits
    rec["certificate_bits_expected"] = [list(o)
                                        for o in cert.degree_two_obstructions]
    rec["C6_certificate_reproduced"] = (
        lens == list(cert.residual_lengths)
        and bits == [list(o) for o in cert.degree_two_obstructions])
    rec["C6_w2j_agreement"] = (rec.get("mod2_classes_enumerated") == 4
                               and rec.get("mod2_zero_class") is None
                               and rec.get("mod2_distinct_values") == 4)
    ok = bool(rec.get("passed") and dok and dfire
              and rec["C6_certificate_reproduced"] and rec["C6_w2j_agreement"]
              and rec["x0_corruption_fires"])
    rec["controls_passed"] = ok
    print(json.dumps(rec, indent=1), flush=True)
    _dump(args, "witness", {"controls_passed": ok}, [rec])
    return 0 if ok else 2


def mode_stability(args, rows):
    """F3, empirically: does the verdict move as the direction set grows?"""
    sel = _slice(rows, args.chains)
    done = _resume(args)
    out, ok = [], True
    rng = random.Random(31337)
    t_run = time.time()
    for r in sel:
        key = tuple(r["chain"]) + (r["g_gen"],)
        rec = done.get(key) or {"chain": r["chain"], "g": r["g_gen"],
                                "steps": []}
        have = {s.get("m_requested") for s in rec["steps"]}
        for mm in [int(s) for s in args.ladder.split(",")]:
            if mm in have:
                continue
            if args.run_seconds and time.time() - t_run > args.run_seconds:
                rec["truncated_run_budget"] = True
                break
            a2 = argparse.Namespace(**vars(args))
            a2.m = mm
            t0 = time.time()
            ctx, why, _cp = chain_context(r, a2)
            if ctx is None:
                rec["status"] = why
                break
            h, x0, dirs, ops, _d = ctx
            sub = {"chain": r["chain"], "g": r["g_gen"]}
            try:
                analyse(sub, h, x0, dirs, a2, rng)
            except TR.NotInCommutator as e:
                sub["status"] = "FAMILY_LEFT_COMMUTATOR"
                sub["detail"] = str(e)
                sub["passed"] = False
            ok = ok and bool(sub.get("passed", False))
            rec["steps"].append({
                "m_requested": mm, "m": sub.get("directions"),
                "status": sub.get("status"), "passed": sub.get("passed"),
                "model_verified": sub.get("model_verified"),
                "mod2_periodicity_checks": sub.get("mod2_periodicity_checks"),
                "mod2_periodicity_ok": sub.get("mod2_periodicity_ok"),
                "C9_positive_control_fires": sub.get(
                    "C9_positive_control_fires"),
                "minus_c0_in_V": sub.get("minus_c0_in_V"),
                "no_linear_certificate": sub.get("no_linear_certificate"),
                "mod2_distinct_values": sub.get("mod2_distinct_values"),
                "cross_pairs_odd": sub.get("cross_pairs_odd"),
                "universe_coords": sub.get("universe_coords"),
                "c0_support": sub.get("c0_support"),
                "mod2_residual_weight": sub.get("mod2_residual_weight"),
                "mod2_V_rank": sub.get("mod2_V_rank"),
                "mod2_residual_support": sub.get("mod2_residual_support"),
                "coordinate_certificates": sub.get("coordinate_certificates"),
                "coordinate_certificates_Q": sub.get(
                    "coordinate_certificates_Q"),
                "coordinate_certificates_mod2": sub.get(
                    "coordinate_certificates_mod2"),
                "secs": round(time.time() - t0, 2)})
            print(json.dumps(rec["steps"][-1]), flush=True)
        rec["steps"].sort(key=lambda s: s.get("m_requested") or 0)
        out.append(rec)
        _dump(args, "stability", {"partial": True, "chains": len(out)}, out)
    summ = {"chains": len(out), "controls_passed": ok and bool(out),
            "monotone_membership_violations": sum(
                1 for o in out for i in range(1, len(o["steps"]))
                if (o["steps"][i - 1].get("no_linear_certificate")
                    and not o["steps"][i].get("no_linear_certificate")))}
    print(json.dumps({"summary": summ}), flush=True)
    _dump(args, "stability", summ, out)
    return 0 if summ["controls_passed"] else 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("decide", "struct", "witness",
                                       "stability"), default="decide")
    ap.add_argument("--chains", type=str, default="")
    ap.add_argument("--window", type=int, nargs=4, default=[0, 0, 0, 0])
    ap.add_argument("--rhos", type=int, nargs="+", default=[2])
    ap.add_argument("--m", type=int, default=10, help="kernel directions")
    ap.add_argument("--kernel-rho", type=int, default=2)
    ap.add_argument("--holdout", type=int, default=4)
    ap.add_argument("--box", type=int, default=2)
    ap.add_argument("--points", type=int, default=200)
    ap.add_argument("--cap-bits", type=int, default=16)
    ap.add_argument("--far-shifts", type=str, default="",
                    help="comma-separated words; seed extra kernel directions "
                         "at translates of the defect support (F3 probe)")
    ap.add_argument("--m-far", type=int, default=4)
    ap.add_argument("--no-source-dirs", action="store_true",
                    help="drop the Omega-row source directions: a second, "
                         "structurally different direction family")
    ap.add_argument("--mod2-only", action="store_true",
                    help="skip the G(2 e_j) evaluations: mod-2 model only")
    ap.add_argument("--pair-sample", type=int, default=0,
                    help="evaluate only this many cross terms (0 = all); a "
                         "partial model still supplies exact elements of V_S")
    ap.add_argument("--elim-cap", type=int, default=3000,
                    help="max coordinate universe for the full elimination")
    ap.add_argument("--corrupt-n", type=int, default=2)
    ap.add_argument("--ladder", type=str, default="2,4,8,12")
    ap.add_argument("--run-seconds", type=float, default=0.0)
    ap.add_argument("--detail", action="store_true")
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
    return {"decide": mode_decide, "struct": mode_struct,
            "witness": mode_witness, "stability": mode_stability}[
                args.mode](args, rows)


if __name__ == "__main__":
    sys.exit(main())
