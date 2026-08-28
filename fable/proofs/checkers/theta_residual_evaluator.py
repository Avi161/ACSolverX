"""W2j: the layer-2 residual class Xi_Z(Theta(F)) for arbitrary census chains.

WHAT THIS COMPUTES.  For a period-two census chain (R, S, U) with target
conjugator g and quotient conjugators h = (h0, h1, h2, h3, g), and for a
first-layer correction x = (x_0, ..., x_4) in M^5:

  1. LITERALLY, in F(c,t): put n_r = sigma(x_r) = prod_v r_v^{x_r(v)} (the
     canonical shortlex section (1.5) of the source, computed by the
     unmodified `lift.lift_module_vector`), set h_r(x) = n_r h_r, replay the
     recurrence (1.8) and form the residual (1.9)/(1.11)

         R_can(x) = Z_x * (n_4 (g t g^-1) n_4^-1)^-1 .

  2. ASSERT R_can(x) in [N,N] by `lift.relation_module(R_can) == {}`.  This
     is the layer-1 equation verified in the free group itself, not through
     the operator calculus -- it is the effective control that catches a
     wrong operator (and it did; see THE L0 DEFECT below).

  3. Theta(x) = [R_can(x)] in W = gamma_2 N / gamma_3 N = Lambda^2 M, via the
     UNMODIFIED codex primitives `esc.schreier_word` (Reidemeister-Schreier
     rewriting into the free basis (r_v)) and `esc.degree_two` (the degree-two
     Magnus/wedge coefficients).  Nothing is forked: the witness evaluator is
     imported and reused verbatim, so a witness-vs-general disagreement is
     impossible to hide.

  4. Xi_Z(Theta) in W_Q = (+)_{D_2} Z (+) (+)_{D_1} Z/2, source (3.15a)/(3.15b):
     e_{v1} ^ e_{v2} |-> +-z_{D} with D = H v1^-1 v2 H, sign by the chosen
     orientation of the inversion orbit {D, D^-1}, and a Z/2 coordinate when
     D = D^-1.

By W2I_LAYER2_D2.md section 3.3, Xi_Z : C_2 -> W_Q is an ISOMORPHISM on the 44
finite-index chains, so for those chains "layer 2 is solvable for this F"
is EXACTLY "Xi_Z(Theta(F)) = 0" -- equation (3.8).  On the other 23 the
same is the source's (3.18) necessary condition, EVIDENCED to be sufficient.

HYPOTHESES (nothing here re-derives them).
  * (3.1) N is free on the Schreier generators (r_v), v in X = Q/<c>.
  * (3.5) the second-layer variation operator L_r^{(2)} carries the SAME
    integral coefficients a_{r,g} as L_r.  Every statement about C_2, and
    hence every "layer 2 is solvable" reading of Xi_Z(Theta) = 0, is
    conditional on (3.5).  Xi_Z(Theta(F)) itself is NOT: it is a function of
    the literal free-group residual alone, and (3.16) -- that the layer-2
    corrections cannot move it -- is re-verified here on the real operators
    (control K4b) rather than assumed.

THE L0 DEFECT (found by control K6, reported, not silently patched).
`period_two_baseline_liveness.build_operators_general` builds the x_0 column as

    L0 = -U^-1 (A - R)  +  bridge * (-S)(A - R)

but the exact variation of (1.8) gives

    [delta_S] = (B - S) x_1  -  S*h1 [delta_R]        (h1 = the second conjugator)

so the second term must be  bridge * (-S*h1)(A - R).  The two agree iff
q(h1) = 1, which is the codex witness's case (H1 = ()) and 8 of the 67 census
chains -- and they differ on the other 59.  Verified by the literal
free-group computation on every probe (mode `opcheck`): with the shipped L0 a
"verified layer-1 solution" leaves R_can OUTSIDE [N,N]; with the exact L0 it
lands inside, every time.  This checker therefore builds its own exact
operators (`exact_operators`) and imports the rest of the machinery
unmodified.  W2b/W2e/W2f/W2g/W2h/W2i layer-1 statements that ran through L0
on an h1 != 1 chain need re-checking; that is NOT done here.

MODES
  opcheck   K6: every operator column against the literal residual, shipped
            vs exact, over a probe set.  Quantifies the L0 defect.
  validate  K2/K3/K4: reproduce the codex witness certificate through the
            general path, and the Theta / Xi_Z algebra controls.
  theta     (b) per chain: an exact layer-1 solution x, then Theta(x) and
            Xi_Z(Theta(x)); zero/nonzero, free and torsion parts.
  family    (c) per chain: kernel directions F_j of the layer-1 map, the
            affine-quadratic law for n |-> Xi_Z(Theta(x + sum n_j F_j))
            verified by held-out prediction, and the attainability of 0 on
            the whole sublattice via the mod-2 reduction (2^m classes --
            complete over Z^m, not a box search).

EXIT CODES
  0  run completed, every control green (a verdict is a RESULT, not a failure)
  2  a control failed -- the run is void
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
import infinite_index_liveness as IL  # noqa: E402
sys.argv = _ARGV

GS, PS, LV = IL.GS, IL.PS, IL.LV

from experiments.stable_ac import (  # noqa: E402
    depth4_period_two_lift_certificate as lift,
)
from experiments.stable_ac import (  # noqa: E402
    depth4_period_two_degree_two_escape_certificate as esc,
)

QM, QI, QR = lift.quotient_multiply, lift.quotient_inverse, lift.quotient_reduce
GR, MGR, AGR = lift.group_ring, lift.multiply_group_ring, lift.add_group_ring
LIT, CV = lift.literal, lift.c_vertex
C, T = lift.C, lift.T
CC = (C,)


# --------------------------------------------------------- the operators


def chain_words(h):
    """(r, s, u, z, target) of the recurrence (1.8) at correction 0."""
    fh = [LV.to_tuple(t) for t in h]
    r = lift.multiply(lift.SOURCE_A,
                      lift.conjugate(lift.inverse(lift.SOURCE_B), fh[0]))
    s = lift.multiply(lift.SOURCE_B, lift.conjugate(lift.inverse(r), fh[1]))
    u = lift.multiply(r, lift.conjugate(lift.inverse(s), fh[2]))
    z = lift.multiply(lift.inverse(u), lift.conjugate(s, fh[3]))
    tgt = lift.conjugate((T,), fh[4])
    return r, s, u, z, tgt


def exact_operators(h):
    """The five layer-1 operators, derived exactly from (1.7)/(1.8).

    Identical to `build_operators_general` except for the x_0 column, which
    carries the q(h1) factor the exact variation of S produces (see the
    module docstring).  Control K6 pins every column against the literal
    free-group residual.
    """
    fh = [LV.to_tuple(t) for t in h]
    r, s, u, _z, tgt = chain_words(h)
    qa, qb = QR(lift.SOURCE_A), QR(lift.SOURCE_B)
    qr, qs, qu, qw = QR(r), QR(s), QR(u), QR(tgt)
    qh1, qh2, qh3 = QR(fh[1]), QR(fh[2]), QR(fh[3])
    one = GR((1, ()))
    d_r = GR((1, qa), (-1, qr))
    d_s1 = GR((1, qb), (-1, qs))
    d_s0 = MGR(GR((-1, QM(qs, qh1))), d_r)
    bridge = GR((1, qh2), (1, QM(QI(qu), qh3)))
    qx = QM(qh2, qs, QI(qh2))
    return (AGR(MGR(GR((-1, QI(qu))), d_r), MGR(bridge, d_s0)),
            MGR(bridge, d_s1),
            AGR(one, GR((-1, qx))),
            GR((1, QI(qu)), (-1, qw)),
            GR((1, qw), (-1, ())))


# ------------------------------------------------- the literal residual


def residual(h, x):
    """R_can(x): the literal free-group residual (1.9) of (1.5)+(1.7)."""
    lf = [lift.lift_module_vector(xi) for xi in x]
    fh = [LV.to_tuple(t) for t in h]
    cj = [lift.multiply(lf[i], fh[i]) for i in range(4)]
    r = lift.multiply(lift.SOURCE_A,
                      lift.conjugate(lift.inverse(lift.SOURCE_B), cj[0]))
    s = lift.multiply(lift.SOURCE_B, lift.conjugate(lift.inverse(r), cj[1]))
    u = lift.multiply(r, lift.conjugate(lift.inverse(s), cj[2]))
    z = lift.multiply(lift.inverse(u), lift.conjugate(s, cj[3]))
    tgt = lift.conjugate((T,), lift.multiply(lf[4], fh[4]))
    return lift.multiply(z, lift.inverse(tgt))


class TimeBudget(Exception):
    """the per-chain wall budget ran out mid-evaluation"""


class NotInCommutator(Exception):
    """R_can(x) is not in [N,N]: x is not a layer-1 solution."""


def theta(h, x):
    """Theta(x) = [R_can(x)] in Lambda^2 M, or raise NotInCommutator."""
    w = residual(h, x)
    rm = lift.relation_module(w)
    if rm:
        raise NotInCommutator(len(rm))
    return esc.degree_two(esc.schreier_word(w)), w


# ------------------------------------------------------------- Xi_Z


def dcoset_rep(z):
    """Canonical (shortlex) representative of the double coset HzH, H=<c>."""
    return min({QR(z), QM(CC, z), QM(z, CC), QM(CC, z, CC)},
               key=lambda w: (len(w), w))


def xi_coord(v1, v2):
    """(coordinate name, sign, is_torsion) of e_{v1} ^ e_{v2}, per (3.15b)."""
    z = QM(QI(v1), v2)
    d = dcoset_rep(z)
    di = dcoset_rep(QI(z))
    if d == ():
        raise AssertionError("diagonal wedge has no displacement coordinate")
    if d == di:
        return LIT(d), 0, True
    dp = min(d, di, key=lambda w: (len(w), w))
    return LIT(dp), (1 if d == dp else -1), False


def xi_raw(th):
    """(free part, INTEGRAL self-inverse part) of the Xi_Z coordinates.

    Both halves are Z-linear functionals of the wedge vector, so both are
    affine-quadratic in the correction whenever Theta is.  The self-inverse
    half is only a W_Q coordinate after reduction mod 2 (its sign is killed
    by the endpoint swap, (3.15b)); it is kept integral here purely so the
    polynomial fit of mode `family` is exact, and reduced by `xi_z`.
    """
    free, tors = {}, {}
    for (a, b), cf in th.items():
        key, sign, is_t = xi_coord(a, b)
        if is_t:
            tors[key] = tors.get(key, 0) + cf
        else:
            free[key] = free.get(key, 0) + sign * cf
    return ({k: v for k, v in free.items() if v},
            {k: v for k, v in tors.items() if v})


def xi_z(th):
    """(free part over Z, torsion part over Z/2) of Xi_Z(th)."""
    free, tors = xi_raw(th)
    return free, {k: v % 2 for k, v in tors.items() if v % 2}


def xi_is_zero(fr, to):
    return (not fr) and (not to)


def act_wedge(gq, th):
    """The diagonal Q-action (3.4) on a wedge vector."""
    out = {}
    for (a, b), cf in th.items():
        ga, gb = CV(QM(gq, a)), CV(QM(gq, b))
        if ga == gb:
            continue
        key, sgn = ((ga, gb), 1) if (len(ga), ga) < (len(gb), gb) \
            else ((gb, ga), -1)
        out[key] = out.get(key, 0) + sgn * cf
    return {k: v for k, v in out.items() if v}


def op2_apply(op, th):
    """L_r^{(2)} acting on a wedge vector, source (3.5)."""
    acc = {}
    for gw, a in op.items():
        for k, v in act_wedge(gw, th).items():
            acc[k] = acc.get(k, 0) + a * v
    return {k: v for k, v in acc.items() if v}


# ---------------------------------------------------------- chain setup


def setup(row, window=(0, 0, 0, 0)):
    """(chain, g, ops_exact, defect, h) at a window, with the exact ops."""
    ch = tuple(row["chain"])
    g = row["g_gen"]
    k = max(abs(w) for w in window)
    sl = PS.chain_slots_g(ch, g, k, k)
    _ops_shipped, defect, h = GS.window_data(ch, g, sl, window)
    return ch, g, exact_operators(h), defect, h, _ops_shipped


def solve_layer1(ops, defect, rhos=(2, 3, 4)):
    for rho in rhos:
        sol = IL.solve_module(ops, defect, rho)
        if sol["ok"] and sol["residual"] == 0:
            sol["rho"] = rho
            return sol
    return {"ok": False, "x": None, "rho": None, "variables": None,
            "x_terms": None, "residual": None}


# ------------------------------------------- the affine family (kernel)


def _columns(ops, defect, rho):
    frontier = set(defect)
    seen, variables = set(), []
    for _ in range(rho):
        if len(variables) > 12000:
            break
        new_v = []
        for i in range(5):
            for gw in ops[i]:
                gi = QI(gw)
                for u in frontier:
                    v = CV(QM(gi, u))
                    if (i, v) not in seen:
                        seen.add((i, v))
                        new_v.append((i, v))
        variables.extend(new_v)
        frontier = set()
        for (i, v) in new_v:
            frontier.update(lift.apply_operator(ops[i], {v: 1}))
    return variables


def _source_directions(ops, cp, variables, want, rho):
    """Directions that really move the source pair (f_0, f_1).

    A single source column is never in the image of L2/L3/L4, so the column
    scan alone finds none.  The right level is Omega = Gamma\\Q/<c>: by W2g's
    Lemma 2, ker(pi : M -> Z[Omega]) = L2 M + L3 M + L4 M exactly, so a
    source COMBINATION s with pi(sum_i L_i s_i) = 0 is finishable by the
    telescoping operators alone.  Those combinations are exactly the linear
    dependencies among the Omega-rows of the source columns, which is one
    more Hermite echelon -- and the Omega-rows are read straight off the
    operators this checker builds (`IL.row_direct`), never off the shipped
    sigma-tuple shortcut.
    """
    src = [(i, v) for (i, v) in variables if i < 2]
    Z = IL.ZEchelon(order=IL.DEEP_FIRST)
    out, tries = [], 0
    for (i, v) in src:
        if tries >= 60:
            break
        row = IL.row_direct(cp, ops[i], IL.wstr(v))
        if not row:
            continue
        member, combo = Z.member(row)
        if not member:
            Z.add(row, (i, v))
            continue
        srcvec = [dict() for _ in range(5)]
        srcvec[i][v] = srcvec[i].get(v, 0) + 1
        for (j, w), cf in combo.items():
            srcvec[j][w] = srcvec[j].get(w, 0) - cf
        srcvec = [{k: a for k, a in fj.items() if a} for fj in srcvec]
        if not any(srcvec):
            continue
        b = IL.verify({}, ops, srcvec)
        tries += 1
        sol = IL.solve_module_from(ops, b, rho, [], (2, 3, 4))
        if not sol["ok"]:
            continue
        F = [dict(fj) for fj in srcvec]
        for j in (2, 3, 4):
            for k, a in sol["x"][j].items():
                F[j][k] = F[j].get(k, 0) + a
        F = [{k: a for k, a in fj.items() if a} for fj in F]
        if IL.verify({}, ops, F):
            continue
        out.append(F)
        if len(out) >= want:
            break
    return out


def kernel_directions(ops, defect, want, rho=2, cp=None):
    """Directions F with sum_r L_r F_r = 0, from dependent columns.

    H_fin (source section 2) is exactly the space of such F.  The generator
    is basis-free: expand the same hop neighbourhood the layer-1 solver
    uses, feed the columns L_i e_v into a Hermite echelon one at a time, and
    every column already an integer combination of the earlier ones yields a
    kernel vector  e_{(i,v)} - sum combo.  Two passes are run so the family
    is not all of one kind:

      pass B  the L2/L3/L4 columns are loaded first and the SOURCE columns
              (i = 0, 1) are then scanned, so a dependent one gives a
              direction that really moves f_0 or f_1 -- the source pair the
              source doc's section 3.2 parametrizes H_fin by;
      pass A  natural order, which finds the telescoping relations.

    Every direction is re-verified to satisfy sum_r L_r F_r = 0 exactly with
    the unmodified `apply_operator`; one that fails is dropped, never used.
    """
    variables = _columns(ops, defect, rho)
    out, seen_key = [], set()
    if cp is not None:
        out.extend(_source_directions(ops, cp, variables, want, rho))
        seen_key.update(tuple(tuple(sorted(fj.items())) for fj in F)
                        for F in out)
    for order in ("sources_last", "natural"):
        if len(out) >= want:
            break
        if order == "sources_last":
            cols = ([c for c in variables if c[0] >= 2]
                    + [c for c in variables if c[0] < 2])
        else:
            cols = variables
        Z = IL.ZEchelon(order=lambda w: (-len(w), w))
        for (i, v) in cols:
            img = lift.apply_operator(ops[i], {v: 1})
            if not img:
                continue
            member, combo = Z.member(img)
            if not member:
                Z.add(img, (i, v))
                continue
            F = [dict() for _ in range(5)]
            F[i][v] = F[i].get(v, 0) + 1
            for (j, w), cf in combo.items():
                F[j][w] = F[j].get(w, 0) - cf
            F = [{k: a for k, a in fj.items() if a} for fj in F]
            if not any(F) or IL.verify({}, ops, F):
                continue
            key = tuple(tuple(sorted(fj.items())) for fj in F)
            if key in seen_key:
                continue
            seen_key.add(key)
            out.append(F)
            if len(out) >= want:
                break
    return out


def add_x(x, F, n):
    out = []
    for xi, fi in zip(x, F):
        d = dict(xi)
        for k, a in fi.items():
            d[k] = d.get(k, 0) + n * a
        out.append({k: a for k, a in d.items() if a})
    return out


def combine(x, dirs, ns):
    out = list(x)
    for F, n in zip(dirs, ns):
        if n:
            out = add_x(out, F, n)
    return out


def _vec(fr, to):
    """One flat dict for polynomial bookkeeping: free coords + torsion."""
    d = {("f", k): v for k, v in fr.items()}
    d.update({("t", k): v for k, v in to.items()})
    return d


def _is_zero_in_WQ(vec):
    """A raw coordinate vector is 0 in W_Q iff free = 0 and torsion is even."""
    for (kind, _k), v in vec.items():
        if kind == "f" and v:
            return False
        if kind == "t" and v % 2:
            return False
    return True


def _sub(a, b, sc=1):
    out = dict(a)
    for k, v in b.items():
        out[k] = out.get(k, 0) - sc * v
    return {k: v for k, v in out.items() if v}


def _lin(*terms):
    out = {}
    for co, d in terms:
        for k, v in d.items():
            out[k] = out.get(k, 0) + co * v
    return {k: v for k, v in out.items() if v}


def _mod2(d):
    return {k: v % 2 for k, v in d.items() if v % 2}


# --------------------------------------------------------------- modes


def mode_opcheck(args, rows):
    """K6: every operator column against the literal residual."""
    sel = _slice(rows, args)
    probes = [(), (T,), (-T,), (C, T), (-T, C), (C, -T, C)]
    out, ok = [], True
    tot_c = tot_e = bad_c = bad_e = 0
    for r in sel:
        ch, g, ops, defect, h, shipped = setup(r)
        rec = {"chain": r["chain"], "g": g, "h1": h[1],
               "h1_trivial": h[1] == "", "shipped_wrong": [], "exact_wrong": []}
        for i in range(5):
            for p in probes:
                v = CV(p)
                x = [dict() for _ in range(5)]
                x[i] = {v: 1}
                got = lift.relation_module(residual(h, x))
                for tag, op in (("s", shipped[i]), ("e", ops[i])):
                    pred = {k: a for k, a in LV.add_vectors(
                        defect, lift.apply_operator(op, x[i])).items() if a}
                    if tag == "s":
                        tot_c += 1
                        if got != pred:
                            bad_c += 1
                            if i not in rec["shipped_wrong"]:
                                rec["shipped_wrong"].append(i)
                    else:
                        tot_e += 1
                        if got != pred:
                            bad_e += 1
                            if i not in rec["exact_wrong"]:
                                rec["exact_wrong"].append(i)
        rec["passed"] = not rec["exact_wrong"]
        ok = ok and rec["passed"]
        out.append(rec)
        print(json.dumps(rec))
    summ = {"chains": len(out), "probe_checks_each": tot_e,
            "exact_ops_mismatches": bad_e,
            "shipped_ops_mismatches": bad_c,
            "chains_with_h1_trivial": sum(1 for o in out if o["h1_trivial"]),
            "chains_where_shipped_L0_wrong": sum(
                1 for o in out if 0 in o["shipped_wrong"]),
            "shipped_columns_wrong": sorted(
                {i for o in out for i in o["shipped_wrong"]}),
            "all_exact_ops_verified": ok and bool(out)}
    print(json.dumps({"summary": summ}))
    _dump(args, "opcheck", summ, out)
    return 0 if summ["all_exact_ops_verified"] else 2


def mode_validate(args, _rows):
    """K2/K3/K4: codex reproduction plus the Theta / Xi_Z algebra."""
    out = {}
    # --- K2: the codex witness, through the general path
    cert = esc.period_two_degree_two_escape_certificate()
    base = esc.variables_from_entries(lift.CORRECTION)
    a10 = esc.variables_from_entries(esc.ALTERNATE_10)
    a01 = esc.variables_from_entries(esc.ALTERNATE_01)
    k0 = esc.subtract_variables(a10, base)
    k1 = esc.subtract_variables(a01, base)
    classes = (base, a10, a01, esc.add_variables(base, k0, k1))
    gen_len, gen_kw, gen_obs, gen_xi = [], [], [], []
    for V in classes:
        w = residual(PS.CODEX_H, list(V))
        assert not lift.relation_module(w), "codex residual left [N,N]"
        kw = esc.schreier_word(w)
        th = esc.degree_two(kw)
        assert th == esc.degree_two(esc.schreier_word(esc.corrected_residual(V)))
        gen_len.append(len(w))
        gen_kw.append(len(kw))
        gen_obs.append(list(esc.degree_two_obstructions(th)))
        fr, to = xi_z(th)
        gen_xi.append({"free": fr, "tors": to, "zero": xi_is_zero(fr, to)})
    out["K2_codex_reproduction"] = {
        "residual_lengths_general": gen_len,
        "residual_lengths_certificate": list(cert.residual_lengths),
        "kernel_lengths_general": gen_kw,
        "kernel_lengths_certificate": list(cert.kernel_lengths),
        "obstructions_general": gen_obs,
        "obstructions_certificate": [list(o)
                                     for o in cert.degree_two_obstructions],
        "passed": (gen_len == list(cert.residual_lengths)
                   and gen_kw == list(cert.kernel_lengths)
                   and gen_obs == [list(o)
                                   for o in cert.degree_two_obstructions])}
    out["K2_codex_xi"] = gen_xi
    # --- K3: Theta is the gamma_2/gamma_3 invariant
    rng = random.Random(20260828)
    verts = [CV(LV.to_tuple(s)) for s in PS.ball(2)]
    verts = sorted({v for v in verts}, key=lambda w: (len(w), w))[:6]

    def rgen(v):
        return lift.relation_generator(v)

    def th_of(w):
        assert not lift.relation_module(w)
        return esc.degree_two(esc.schreier_word(w))

    n_comm = n_comm_ok = 0
    for a in verts:
        for b in verts:
            if a == b:
                continue
            w = lift.multiply(rgen(a), rgen(b),
                              lift.inverse(rgen(a)), lift.inverse(rgen(b)))
            want = {(a, b): 1} if (len(a), a) < (len(b), b) else {(b, a): -1}
            n_comm += 1
            n_comm_ok += int(th_of(w) == want)
    n_add = n_add_ok = n_eq = n_eq_ok = n_tri = n_tri_ok = 0
    words = []
    for _ in range(8):
        a, b = rng.sample(verts, 2)
        words.append(lift.multiply(rgen(a), rgen(b),
                                   lift.inverse(rgen(a)), lift.inverse(rgen(b))))
    for i in range(len(words)):
        for j in range(len(words)):
            w1, w2 = words[i], words[j]
            n_add += 1
            lhs = th_of(lift.multiply(w1, w2))
            rhs = _lin((1, th_of(w1)), (1, th_of(w2)))
            n_add_ok += int(lhs == rhs)
    for w in words:
        for gs in ("", "c", "t", "T", "ct", "cT", "tc", "Tc", "ctc"):
            gw = LV.to_tuple(gs)
            n_eq += 1
            n_eq_ok += int(th_of(lift.conjugate(w, gw))
                           == act_wedge(QR(gw), th_of(w)))
        for v in verts[:3]:
            n_tri += 1
            n_tri_ok += int(th_of(lift.multiply(
                w, rgen(v), lift.inverse(w), lift.inverse(rgen(v)))) == {})
    out["K3_theta_algebra"] = {
        "commutator_basis_checks": n_comm, "commutator_ok": n_comm_ok,
        "additivity_checks": n_add, "additivity_ok": n_add_ok,
        "Q_equivariance_checks": n_eq, "Q_equivariance_ok": n_eq_ok,
        "gamma3_vanishing_checks": n_tri, "gamma3_vanishing_ok": n_tri_ok,
        "passed": bool(n_comm == n_comm_ok and n_add == n_add_ok
                       and n_eq == n_eq_ok and n_tri == n_tri_ok
                       and n_comm and n_add and n_eq and n_tri)}
    # --- K4: Xi_Z is diagonally Q-invariant and kills every operator image
    rows = GS.load_rows()
    n_inv = n_inv_ok = n_op = n_op_ok = 0
    n_cor = n_cor_fires = 0
    th_pool = [th_of(w) for w in words[:4]]
    for r in rows[:args.xi_chains]:
        _ch, _g, ops, _d, _h, _sh = setup(r)
        for th in th_pool:
            for gs in ("c", "t", "T", "ct", "Tc"):
                n_inv += 1
                n_inv_ok += int(xi_z(act_wedge(QR(LV.to_tuple(gs)), th))
                                == xi_z(th))
            for i in range(5):
                n_op += 1
                fr, to = xi_z(op2_apply(ops[i], th))
                n_op_ok += int(xi_is_zero(fr, to))
                bad = dict(ops[i])
                bad.pop(sorted(bad)[0])
                n_cor += 1
                fr2, to2 = xi_z(op2_apply(bad, th))
                n_cor_fires += int(not xi_is_zero(fr2, to2))
    out["K4_xi_z"] = {
        "diagonal_Q_invariance_checks": n_inv, "invariance_ok": n_inv_ok,
        "operator_image_checks_3_16": n_op, "operator_image_zero": n_op_ok,
        "corruption_checks": n_cor, "corruption_fires": n_cor_fires,
        "passed": bool(n_inv == n_inv_ok and n_op == n_op_ok
                       and n_cor_fires == n_cor and n_inv and n_op)}
    ok = all(out[k]["passed"] for k in
             ("K2_codex_reproduction", "K3_theta_algebra", "K4_xi_z"))
    out["all_controls_passed"] = ok
    print(json.dumps(out, indent=1))
    _dump(args, "validate", out, [])
    return 0 if ok else 2


def mode_theta(args, rows):
    """(b): Theta and Xi_Z at an exact layer-1 solution, per chain."""
    sel = _slice(rows, args)
    out, ok, corrupted = [], True, 0
    for r in sel:
        t0 = time.time()
        ch, g, ops, defect, h, _sh = setup(r, tuple(args.window))
        sol = solve_layer1(ops, defect, tuple(args.rhos))
        rec = {"chain": r["chain"], "g": g, "h1_trivial": h[1] == "",
               "window": list(args.window), "defect_terms": len(defect),
               "layer1_solved": sol["ok"], "rho": sol.get("rho"),
               "x_terms": sol.get("x_terms")}
        if not sol["ok"]:
            rec["status"] = "LAYER1_UNSOLVED_AT_RHO"
            rec["passed"] = True
            out.append(rec)
            print(json.dumps(rec))
            continue
        th, w = theta(h, sol["x"])
        fr, to = xi_z(th)
        rec.update({
            "residual_length": len(w),
            "schreier_length": len(esc.schreier_word(w)),
            "wedge_terms": len(th),
            "wedge_l1": sum(abs(v) for v in th.values()),
            "xi_free_terms": len(fr), "xi_tors_terms": len(to),
            "xi_free_l1": sum(abs(v) for v in fr.values()),
            "xi_zero": xi_is_zero(fr, to),
            "xi_free": fr if args.detail else None,
            "xi_tors": to if args.detail else None,
            "status": "THETA_EVALUATED"})
        # K5 corruption: a broken correction must leave [N,N]
        if corrupted < args.corrupt_n:
            bad = [dict(xi) for xi in sol["x"]]
            for xi in bad:
                if xi:
                    kk = sorted(xi)[0]
                    xi[kk] += 1
                    break
            try:
                theta(h, bad)
                rec["corruption_detected"] = False
                ok = False
            except NotInCommutator:
                rec["corruption_detected"] = True
            corrupted += 1
        rec["passed"] = True
        rec["secs"] = round(time.time() - t0, 2)
        out.append(rec)
        print(json.dumps({k: v for k, v in rec.items()
                          if v is not None or args.detail}))
    ev = [o for o in out if o.get("status") == "THETA_EVALUATED"]
    summ = {"chains": len(out), "theta_evaluated": len(ev),
            "layer1_unsolved": sum(1 for o in out
                                   if o.get("status") ==
                                   "LAYER1_UNSOLVED_AT_RHO"),
            "xi_zero": sum(1 for o in ev if o["xi_zero"]),
            "xi_nonzero": sum(1 for o in ev if not o["xi_zero"]),
            "with_free_part_nonzero": sum(1 for o in ev if o["xi_free_terms"]),
            "with_torsion_part_nonzero": sum(1 for o in ev
                                             if o["xi_tors_terms"]),
            "corruption_controls_run": corrupted,
            "corruption_controls_fired": sum(
                1 for o in out if o.get("corruption_detected")),
            "controls_passed": ok and bool(out)}
    print(json.dumps({"summary": summ}))
    _dump(args, "theta", summ, out)
    return 0 if summ["controls_passed"] else 2


def _fit_quadratic(G, m):
    """Coefficients of the degree-<=2 fit of n |-> G(n) on Z^m."""
    z = [0] * m
    c0 = G(z)
    a, b = {}, {}
    for j in range(m):
        ej = list(z)
        ej[j] = 1
        e2 = list(z)
        e2[j] = 2
        g1, g2 = G(ej), G(e2)
        num = _lin((1, g2), (-2, g1), (1, c0))
        if any(v % 2 for v in num.values()):
            return None, "diagonal second difference is odd"
        bjj = {k: v // 2 for k, v in num.items()}
        b[(j, j)] = bjj
        a[j] = _lin((1, g1), (-1, c0), (-1, bjj))
    for j in range(m):
        for k in range(j + 1, m):
            ejk = list(z)
            ejk[j] = 1
            ejk[k] = 1
            ej = list(z)
            ej[j] = 1
            ek = list(z)
            ek[k] = 1
            b[(j, k)] = _lin((1, G(ejk)), (-1, G(ej)), (-1, G(ek)), (1, c0))
    return (c0, a, b), None


def _eval_fit(fit, n):
    c0, a, b = fit
    terms = [(1, c0)]
    for j, aj in a.items():
        if n[j]:
            terms.append((n[j], aj))
    for (j, k), bjk in b.items():
        co = n[j] * n[k]
        if co:
            terms.append((co, bjk))
    return _lin(*terms)


def mode_family(args, rows):
    """(c): the affine family, its quadratic law, and attainability of 0."""
    sel = _slice(rows, args)
    out, ok = [], True
    t_run = time.time()
    for r in sel:
        t0 = time.time()
        if args.run_seconds and time.time() - t_run > args.run_seconds:
            out.append({"chain": r["chain"], "g": r["g_gen"],
                        "status": "NOT_ATTEMPTED_RUN_BUDGET", "passed": True})
            continue
        ch, g, ops, defect, h, _sh = setup(r, tuple(args.window))
        if args.witness_dirs:
            # the codex certificate's own kernel directions are directions
            # only at the codex conjugator tuple, so pin it
            assert ch == PS.WITNESS, "--witness-dirs needs the witness chain"
            h = PS.CODEX_H
            ops = exact_operators(h)
            _r, _s2, _u, _z, tgt = chain_words(h)
            defect = lift.relation_module(lift.multiply(_z, lift.inverse(tgt)))
        sol = solve_layer1(ops, defect, tuple(args.rhos))
        rec = {"chain": r["chain"], "g": g, "layer1_solved": sol["ok"],
               "h": list(h)}
        if not sol["ok"]:
            rec["status"] = "LAYER1_UNSOLVED_AT_RHO"
            rec["passed"] = True
            out.append(rec)
            print(json.dumps(rec))
            continue
        if args.witness_dirs:
            dirs = _codex_dirs()
            sol = {"ok": True, "x": list(esc.variables_from_entries(
                lift.CORRECTION)), "rho": None, "x_terms": None}
            assert not IL.verify(defect, ops, sol["x"]), "codex x not a solution"
        else:
            cp = IL.Completed(GS.Folded(GS.gamma_gens(ch, g)))
            dirs = kernel_directions(ops, defect, args.m, args.kernel_rho,
                                     cp=cp)
        m = len(dirs)
        rec["directions"] = m
        rec["direction_secs"] = round(time.time() - t0, 2)
        if args.chain_seconds and time.time() - t0 > args.chain_seconds:
            rec["status"] = "SKIPPED_TIME_BUDGET_AFTER_DIRECTIONS"
            rec["passed"] = True
            out.append(rec)
            print(json.dumps(rec))
            continue
        if m == 0:
            rec["status"] = "NO_KERNEL_DIRECTION_FOUND"
            rec["passed"] = True
            out.append(rec)
            print(json.dumps(rec))
            continue
        rec["direction_terms"] = [[len(f) for f in F] for F in dirs]
        cache = {}

        deadline = (t0 + args.chain_seconds * 8) if args.chain_seconds else None

        def G(n):
            key = tuple(n)
            if key not in cache:
                if deadline and time.time() > deadline:
                    raise TimeBudget(len(cache))
                th, _w = theta(h, combine(sol["x"], dirs, n))
                cache[key] = _vec(*xi_raw(th))
            return cache[key]

        try:
            fit, why = _fit_quadratic(G, m)
        except TimeBudget as e:
            rec["status"] = "SKIPPED_TIME_BUDGET_IN_FIT"
            rec["evaluations"] = str(e)
            rec["passed"] = True
            out.append(rec)
            print(json.dumps(rec))
            continue
        except NotInCommutator as e:
            rec["status"] = "FAMILY_LEFT_COMMUTATOR"
            rec["detail"] = str(e)
            rec["passed"] = False
            ok = False
            out.append(rec)
            print(json.dumps(rec))
            continue
        if fit is None:
            rec["status"] = "NOT_AFFINE_QUADRATIC"
            rec["detail"] = why
            rec["passed"] = False
            ok = False
            out.append(rec)
            print(json.dumps(rec))
            continue
        # K7: held-out prediction, including |n| >= 2 and negative n
        rng = random.Random(4242 + len(rec["chain"][0]))
        held = set()
        for j in range(m):
            e = [0] * m
            e[j] = -1
            held.add(tuple(e))
            e = [0] * m
            e[j] = 3
            held.add(tuple(e))
        for _ in range(args.holdout):
            held.add(tuple(rng.randint(-2, 3) for _ in range(m)))
        n_h = n_h_ok = 0
        try:
            for n in sorted(held):
                n_h += 1
                n_h_ok += int(G(list(n)) == _eval_fit(fit, list(n)))
        except TimeBudget:
            n_h -= 1
        rec["holdout_checks"] = n_h
        rec["holdout_agree"] = n_h_ok
        rec["affine_quadratic_verified"] = (n_h == n_h_ok and n_h >= 2)
        ok = ok and rec["affine_quadratic_verified"]
        # attainability of 0 -- complete over the whole sublattice via mod 2
        classes = []
        zero_mod2 = []
        for eps in itertools.product((0, 1), repeat=m):
            v = _mod2(_eval_fit(fit, list(eps)))
            classes.append({"eps": list(eps), "nonzero_coords": len(v)})
            if not v:
                zero_mod2.append(list(eps))
        rec["mod2_classes"] = len(classes)
        rec["mod2_classes_that_vanish"] = zero_mod2
        rec["distinct_mod2_values"] = len({
            tuple(sorted(_mod2(_eval_fit(fit, list(eps))).items()))
            for eps in itertools.product((0, 1), repeat=m)})
        # sanity: the mod-2 reduction really is a function of n mod 2
        n_m2 = n_m2_ok = 0
        for n in sorted(held):
            if tuple(n) not in cache:
                continue
            n_m2 += 1
            n_m2_ok += int(_mod2(G(list(n)))
                           == _mod2(_eval_fit(fit, [x % 2 for x in n])))
        rec["mod2_periodicity_checks"] = n_m2
        rec["mod2_periodicity_ok"] = n_m2_ok
        ok = ok and (n_m2 == n_m2_ok)
        base = _vec(*xi_raw(theta(h, sol["x"])[0]))
        rec["xi_at_base_zero"] = _is_zero_in_WQ(base)
        if not zero_mod2:
            rec["status"] = "ZERO_UNATTAINABLE_ON_SUBLATTICE"
        else:
            # integral search inside the classes that vanish mod 2
            found = None
            for eps in [] if deadline and time.time() > deadline else zero_mod2:
                for k in itertools.product(
                        range(-args.box, args.box + 1), repeat=m):
                    n = [e + 2 * kk for e, kk in zip(eps, k)]
                    if _is_zero_in_WQ(_eval_fit(fit, n)):
                        th, _w = theta(h, combine(sol["x"], dirs, n))
                        fr, to = xi_z(th)
                        if xi_is_zero(fr, to):
                            found = n
                            break
                if found:
                    break
            rec["integral_witness"] = found
            rec["status"] = ("ZERO_ATTAINED" if found
                             else "ZERO_POSSIBLE_MOD2_NO_INTEGRAL_WITNESS")
        rec["passed"] = rec["affine_quadratic_verified"] and n_m2 == n_m2_ok
        rec["secs"] = round(time.time() - t0, 2)
        out.append(rec)
        print(json.dumps(rec))
    summ = {"chains": len(out),
            "with_directions": sum(1 for o in out if o.get("directions")),
            "affine_quadratic_verified": sum(
                1 for o in out if o.get("affine_quadratic_verified")),
            "zero_unattainable_on_sublattice": sum(
                1 for o in out
                if o.get("status") == "ZERO_UNATTAINABLE_ON_SUBLATTICE"),
            "zero_attained": sum(1 for o in out
                                 if o.get("status") == "ZERO_ATTAINED"),
            "families_non_constant_mod2": sum(
                1 for o in out if (o.get("distinct_mod2_values") or 0) > 1),
            "mod2_open": sum(
                1 for o in out if o.get("status") ==
                "ZERO_POSSIBLE_MOD2_NO_INTEGRAL_WITNESS"),
            "controls_passed": ok and bool(out)}
    print(json.dumps({"summary": summ}))
    _dump(args, "family", summ, out)
    return 0 if summ["controls_passed"] else 2


def _codex_dirs():
    base = esc.variables_from_entries(lift.CORRECTION)
    return [list(esc.subtract_variables(
                esc.variables_from_entries(alt), base))
            for alt in (esc.ALTERNATE_10, esc.ALTERNATE_01)]


def _slice(rows, args):
    sel = rows
    if args.h1_trivial_only:
        sel = [r for r in sel if setup(r)[4][1] == ""]
    if args.chains:
        a, b = args.chains.split(":")
        sel = sel[int(a or 0):int(b or len(sel))]
    return sel


def _dump(args, name, summ, rows):
    if args.json:
        Path(args.json).write_text(json.dumps(
            {"schema": f"acsolverx.w2j.{name}.v1",
             "summary": summ, "rows": rows}, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("opcheck", "validate", "theta",
                                       "family"), default="validate")
    ap.add_argument("--chains", type=str, default="")
    ap.add_argument("--h1-trivial-only", action="store_true")
    ap.add_argument("--window", type=int, nargs=4, default=[0, 0, 0, 0])
    ap.add_argument("--rhos", type=int, nargs="+", default=[2, 3])
    ap.add_argument("--detail", action="store_true")
    ap.add_argument("--corrupt-n", type=int, default=3)
    ap.add_argument("--xi-chains", type=int, default=3)
    ap.add_argument("--m", type=int, default=3, help="kernel directions")
    ap.add_argument("--kernel-rho", type=int, default=3)
    ap.add_argument("--seed-len", type=int, default=2)
    ap.add_argument("--holdout", type=int, default=8)
    ap.add_argument("--box", type=int, default=2)
    ap.add_argument("--chain-seconds", type=float, default=0.0,
                    help="skip a chain whose direction search exceeds this")
    ap.add_argument("--run-seconds", type=float, default=0.0,
                    help="stop starting new chains after this many seconds")
    ap.add_argument("--witness-dirs", action="store_true",
                    help="use the codex certificate's own kernel directions")
    ap.add_argument("--json", type=str, default="")
    args = ap.parse_args()

    c1 = LV.analyze(PS.WITNESS, fixed_h=PS.CODEX_H)
    got = (c1["defect_terms"], c1["defect_l1"], c1["defect_augmentation"])
    print(json.dumps({"control": "K1_fixed_h_witness", "defect": list(got),
                      "want": [21, 48, 0], "passed": got == (21, 48, 0)}))
    if got != (21, 48, 0):
        return 2

    rows = GS.load_rows()
    return {"opcheck": mode_opcheck, "validate": mode_validate,
            "theta": mode_theta, "family": mode_family}[args.mode](args, rows)


if __name__ == "__main__":
    sys.exit(main())
