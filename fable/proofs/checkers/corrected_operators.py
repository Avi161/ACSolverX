"""W2k: `build_operators_exact` -- all five layer-1 columns, re-derived.

This file SUPERSEDES `period_two_baseline_liveness.build_operators_general`.
It does not modify it (repo discipline: supersede, never silently rewrite).

--------------------------------------------------------------------------
THE SETTING
--------------------------------------------------------------------------
`Q = <c, t | c^2> = C_2 * Z`, `F = F(c,t)`, `N = ker(F -> Q)`, `M = N/[N,N]`.
`N` is free on the Schreier basis `r_v = v c^2 v^-1`, `v in X = Q/<c>`, so
`M = Z[X]` with the LEFT `Q`-action, and the class map `[.] : N -> M` obeys

    [n n']    = [n] + [n']                       (M abelian)
    [w n w^-1] = q(w) . [n]     for all w in F   (q = F -> Q)
    [sigma(x)] = x                               (sigma = lift.lift_module_vector)

The period-two recurrence (1.8), with conjugators `h = (h0,h1,h2,h3,h4=g)`:

    r    = A . (h0 B^-1 h0^-1)                 write  X0 = h0 B^-1 h0^-1
    s    = B . (h1 r^-1 h1^-1)                 write  Y  = h1 r^-1 h1^-1
    u    = r . (h2 s^-1 h2^-1)                 write  W  = h2 s^-1 h2^-1
    z    = u^-1 . (h3 s h3^-1)                 write  V  = h3 s h3^-1
    tgt  = h4 t h4^-1
    D    = z . tgt^-1   in N            (the defect; `q(z) = q(tgt)` is asserted)

Layer 1 perturbs each conjugator by an element of `N`:  `h_i -> n_i h_i`,
`n_i = sigma(x_i)`, `x_i in M`.  Capital letters below are the QUOTIENT images
`A = q(A)`, `R = q(r)`, `S = q(s)`, `U = q(u)`, `B = q(B)`, `w = q(tgt)`, and
`hi = q(h_i)`.

--------------------------------------------------------------------------
THE DERIVATION -- ALL FIVE COLUMNS, ONE AT A TIME
--------------------------------------------------------------------------
Each step writes the perturbed word as `delta . (unperturbed)` with `delta`
in `N`, then reads `[delta]` off the three rules above.  Every factorisation
below is an EXACT identity in `F` -- nothing is truncated to first order, and
that is why the resulting operator identity

    [D(x)]  =  [D] + sum_{i=0..4} L_i x_i                                (*)

is exact, and why the literal free-group probe of `validate_columns` is a
sharp test rather than an approximation.

(0) r.   r(x) = A n0 X0 n0^-1 = (A n0 A^-1)(r n0^-1 r^-1) . r, so

        delta_r = (A n0 A^-1)(r n0^-1 r^-1),     [delta_r] = (A - R) x_0.

(1) s.   s(x) = B n1 Y (h1 delta_r^-1 h1^-1) n1^-1
              = (B n1 B^-1) . (BY (h1 delta_r^-1 h1^-1) (BY)^-1)
                            . (BY n1^-1 (BY)^-1) . s   ,   q(BY) = S, so

        [delta_s] = (B - S) x_1 - q(B Y h1) [delta_r]
                  = (B - S) x_1 - S.h1 [delta_r].

    `q(B Y h1) = B . h1 R^-1 h1^-1 . h1 = B h1 R^-1 = S h1` -- THE FACTOR THE
    SHIPPED BUILDER DROPS.  It is invisible exactly when `q(h1) = 1`, which is
    the codex witness's case (`H1 = ()`), i.e. the bug lives in the coordinate
    the reference example sets to zero.

(2) u.   u(x) = delta_r r n2 W (h2 delta_s^-1 h2^-1) n2^-1, and the same
    peeling with `q(rW) = U`, `q(rWh2) = U h2`:

        [delta_u] = [delta_r] + (R - U) x_2 - U.h2 [delta_s].

(3) z.   z(x) = u^-1 delta_u^-1 n3 (h3 delta_s h3^-1) V n3^-1, and
    `q(u^-1) = U^-1`, `q(u^-1 V) = q(z) = w`:

        [delta_z] = U^-1 ( -[delta_u] + x_3 + h3 [delta_s] ) - w x_3
                  = -U^-1 [delta_u] + U^-1 h3 [delta_s] + (U^-1 - w) x_3.

    The `x_3` coefficient uses `q(u^-1 V) = w`, which is EXACTLY the assertion
    `q(z) = q(tgt)` that `D in N` makes -- so `L3 = U^-1 - w` is not an
    approximation, it is the defect condition.

(4) tgt. tgt(x) = (n4 tgt n4^-1 tgt^-1) . tgt, so `[delta_t] = (1 - w) x_4`.

(*) D.   `D(x) = delta_z . D . delta_t^-1` and `q(D) = 1`, so
    `[D(x)] = [D] + [delta_z] - [delta_t]`.  Collecting:

    L4 = w - 1                                                    (from -delta_t)
    L3 = U^-1 - w
    L2 = -U^-1 (R - U) = 1 - U^-1 R = 1 - h2 S h2^-1        (slot identity)
    L1 = (h2 + U^-1 h3) (B - S)                             =: bridge (B - S)
    L0 = -( U^-1 + bridge . S . h1 ) (A - R)

    L2: the `x_2` coefficient is `-U^-1(R-U)`; `U = R h2 S^-1 h2^-1` gives
        `U^-1 R = h2 S h2^-1`, so both spellings agree identically.
    L1: `x_1` enters via `-U^-1 . (-U h2 [delta_s]) + U^-1 h3 [delta_s]
        = bridge [delta_s]`, and the `x_1` part of `[delta_s]` is `(B-S)`.
    L0: `x_0` enters through `[delta_r]` twice -- directly inside `[delta_u]`
        and again through `[delta_s]`'s `-S.h1 [delta_r]` term:
            -U^-1 [delta_u]      contributes  -U^-1 (A-R) + h2 S h1 (A-R)*(-1)... ;
        collecting the two paths gives exactly `-(U^-1 + bridge S h1)(A-R)`.

--------------------------------------------------------------------------
WHAT CHANGED versus `build_operators_general`
--------------------------------------------------------------------------
    column | shipped                             | exact              | same?
    -------+-------------------------------------+--------------------+------
      L0   | -(U^-1 + bridge*S) * (A-R)          | ...*S*h1*(A-R)     | NO
      L1   | bridge * (B-S)                      | identical          | yes
      L2   | 1 - h2 S h2^-1                      | identical          | yes
      L3   | U^-1 - w                            | identical          | yes
      L4   | w - 1                                | identical          | yes

Columns 1-4 are exact as shipped, and the derivation says WHY: `L1..L4` never
see `h1`, and `L2`/`L3`'s two spellings are forced by the slot identity
`U^-1 R = h2 S h2^-1` and by the defect condition `q(z) = q(tgt)` respectively.
`L0` is the only column on which the two `S`-paths through `[delta_s]` both
land, and it is the only one carrying `h1`.

--------------------------------------------------------------------------
HOW TO KNOW THIS IS RIGHT (never trust the calculus that produced it)
--------------------------------------------------------------------------
`validate_columns` puts `x_i = e_v` for a probe vertex `v`, one column at a
time, replays the recurrence LITERALLY in `F(c,t)` with `n_i = sigma(e_v)`,
and compares `relation_module(D(x))` against `[D] + L_i e_v` term by term.
That is (*) tested in the object it is about.  `broken_L0` re-breaks the
column on purpose (it reproduces the shipped one) and must FAIL the probes on
every chain with `q(h1) != 1`.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
sys.path.insert(0, str(HERE))

from experiments.stable_ac import (  # noqa: E402
    depth4_period_two_lift_certificate as lift,
)

C, T = lift.C, lift.T
QM, QI, QR = lift.quotient_multiply, lift.quotient_inverse, lift.quotient_reduce
GR, MGR, AGR = lift.group_ring, lift.multiply_group_ring, lift.add_group_ring

_LETTER = {"c": (C,), "C": (-C,), "t": (T,), "T": (-T,)}


def to_tuple(s):
    """Literal string -> free-group word (same convention as LV.to_tuple)."""
    if not isinstance(s, str):
        return s
    out = ()
    for ch in s:
        out = lift.multiply(out, _LETTER[ch])
    return out


# ------------------------------------------------------- the recurrence


def chain_words(h):
    """(r, s, u, z, tgt) of (1.8) at correction 0, from conjugator strings."""
    fh = [to_tuple(x) for x in h]
    r = lift.multiply(lift.SOURCE_A,
                      lift.conjugate(lift.inverse(lift.SOURCE_B), fh[0]))
    s = lift.multiply(lift.SOURCE_B, lift.conjugate(lift.inverse(r), fh[1]))
    u = lift.multiply(r, lift.conjugate(lift.inverse(s), fh[2]))
    z = lift.multiply(lift.inverse(u), lift.conjugate(s, fh[3]))
    tgt = lift.conjugate((T,), fh[4])
    return r, s, u, z, tgt


def defect_of(h):
    """(defect word D in N, its module class [D])."""
    _r, _s, _u, z, tgt = chain_words(h)
    dw = lift.multiply(z, lift.inverse(tgt))
    assert QR(dw) == (), "defect not in N"
    return dw, lift.relation_module(dw)


def residual(h, x):
    """R_can(x): the literal free-group residual of (1.5)+(1.7)+(1.8)."""
    lf = [lift.lift_module_vector(xi) for xi in x]
    fh = [to_tuple(t) for t in h]
    cj = [lift.multiply(lf[i], fh[i]) for i in range(4)]
    r = lift.multiply(lift.SOURCE_A,
                      lift.conjugate(lift.inverse(lift.SOURCE_B), cj[0]))
    s = lift.multiply(lift.SOURCE_B, lift.conjugate(lift.inverse(r), cj[1]))
    u = lift.multiply(r, lift.conjugate(lift.inverse(s), cj[2]))
    z = lift.multiply(lift.inverse(u), lift.conjugate(s, cj[3]))
    tgt = lift.conjugate((T,), lift.multiply(lf[4], fh[4]))
    return lift.multiply(z, lift.inverse(tgt))


# --------------------------------------------------------- the operators


def build_operators_exact(r, s, u, h1, h2, h3, target_w):
    """The five exact layer-1 columns `(L0, L1, L2, L3, L4)`.

    Signature mirrors `period_two_baseline_liveness.build_operators_general`
    with the missing `h1` slot inserted.  Arguments are words (free-group or
    already-quotient; everything is quotient-reduced here).
    """
    qa, qb = QR(lift.SOURCE_A), QR(lift.SOURCE_B)
    qr, qs, qu = QR(r), QR(s), QR(u)
    qw = QR(target_w)
    qh1, qh2, qh3 = QR(h1), QR(h2), QR(h3)
    one = GR((1, ()))
    d_r = GR((1, qa), (-1, qr))                       # A - R
    d_s1 = GR((1, qb), (-1, qs))                      # B - S
    d_s0 = MGR(GR((-1, QM(qs, qh1))), d_r)            # -S.h1 (A - R)
    bridge = GR((1, qh2), (1, QM(QI(qu), qh3)))       # h2 + U^-1 h3
    qx = QM(qh2, qs, QI(qh2))                         # h2 S h2^-1 = U^-1 R
    return (
        AGR(MGR(GR((-1, QI(qu))), d_r), MGR(bridge, d_s0)),
        MGR(bridge, d_s1),
        AGR(one, GR((-1, qx))),
        GR((1, QI(qu)), (-1, qw)),
        GR((1, qw), (-1, ())),
    )


def build_operators_broken_L0(r, s, u, h1, h2, h3, target_w):
    """The deliberately re-broken control: drop `h1` from `L0`.

    This reproduces `build_operators_general` exactly and MUST fail the
    literal probes on every chain with `q(h1) != 1`.
    """
    ops = list(build_operators_exact(r, s, u, (), h2, h3, target_w))
    return tuple(ops)


def operators_from_h(h):
    """Exact operators from the conjugator tuple `h = (h0,h1,h2,h3,g)`."""
    fh = [to_tuple(x) for x in h]
    r, s, u, _z, tgt = chain_words(h)
    return build_operators_exact(r, s, u, fh[1], fh[2], fh[3], tgt)


def operators_from_h_broken(h):
    fh = [to_tuple(x) for x in h]
    r, s, u, _z, tgt = chain_words(h)
    return build_operators_broken_L0(r, s, u, fh[1], fh[2], fh[3], tgt)


def q_h1(h):
    return QR(to_tuple(h[1]))


# ------------------------- the Omega-row shortcut, corrected (W2h Lemma 5')


def sigma_terms_exact(chain, h):
    """{i: [(group element, sign)]} realising `pi(L_i e_v)` in `Z[Gamma\\Q]`.

    Corrected form of `infinite_index_liveness.sigma_terms`.  Using
    `Gamma = <R, U, w>`, `h2 S = X h2` with `X = U^-1 R in Gamma`, and
    `U^-1 h3 S = w h3` with `w in Gamma`:

        Gamma . h2 S h1 = Gamma . h2 h1 ,   Gamma . U^-1 h3 S h1 = Gamma . h3 h1

    so the corrected `L0` row is the shipped row with `h2 -> h2 h1` and
    `h3 -> h3 h1` in the four bridge terms.  `L1` never sees `h1` and is
    unchanged.
    """
    R, S, _U = chain
    qR, qS = QR(to_tuple(R)), QR(to_tuple(S))
    qA, qB = QR(lift.SOURCE_A), QR(lift.SOURCE_B)
    qh1 = QR(to_tuple(h[1]))
    h2, h3 = QR(to_tuple(h[2])), QR(to_tuple(h[3]))
    h2a, h3a = QM(h2, qh1), QM(h3, qh1)
    beta = QM(QI(qS), qB)
    return {
        0: [(qR, +1), (QM(h2a, qR), +1), (QM(h3a, qR), +1),
            (qA, -1), (QM(h2a, qA), -1), (QM(h3a, qA), -1)],
        1: [(QM(h2, beta), +1), (QM(h3, beta), +1), (h2, -1), (h3, -1)],
    }


# -------------------------------------------------- the literal validation


def probe_vertices(maxlen=4, cap=20):
    """Distinct vertices of `X = Q/<c>` from the ball of radius `maxlen`.

    W2j's probe set had six vertices and established only that column 0 was
    wrong there.  This enumerates the whole ball so that a column that is
    right on six vertices and wrong on the seventh cannot hide.
    """
    out, seen = [], set()
    frontier = [()]
    seen_words = {()}
    for _ in range(maxlen + 1):
        nxt = []
        for w in frontier:
            v = lift.c_vertex(w)
            if v not in seen:
                seen.add(v)
                out.append(v)
                if len(out) >= cap:
                    return out
            for l in (C, T, -T):
                nw = QM(w, (l,))
                if nw not in seen_words:
                    seen_words.add(nw)
                    nxt.append(nw)
        frontier = nxt
    return out


def validate_columns(h, ops, probes=None):
    """Literal free-group probe of `[D(e_v at column i)] == [D] + L_i e_v`.

    Returns (checks, mismatches, columns_wrong).  This is the ground truth:
    it never uses `ops` to build the residual, only to predict it.
    """
    probes = probe_vertices() if probes is None else probes
    _dw, defect = defect_of(h)
    checks = bad = 0
    wrong = set()
    for i in range(5):
        for v in probes:
            x = [dict() for _ in range(5)]
            x[i] = {v: 1}
            got = lift.relation_module(residual(h, x))
            pred = {k: a for k, a in lift.add_vectors(
                defect, lift.apply_operator(ops[i], x[i])).items() if a}
            checks += 1
            if got != pred:
                bad += 1
                wrong.add(i)
    return checks, bad, sorted(wrong)


def verify_solution_literally(h, x):
    """The W2j ground-truth test: is `x` a layer-1 solution IN `F(c,t)`?

    Returns (ok, n_residual_module_terms).  `ok` iff `R_can(x)` is in [N,N].
    """
    rm = lift.relation_module(residual(h, x))
    return (not rm), len(rm)


def apply_all(ops, x):
    """`[D] + sum_i L_i x_i` residual vector, through the operators."""
    acc = {}
    for i in range(5):
        for k, a in lift.apply_operator(ops[i], x[i]).items():
            acc[k] = acc.get(k, 0) + a
    return {k: a for k, a in acc.items() if a}


__all__ = [
    "build_operators_exact", "build_operators_broken_L0",
    "operators_from_h", "operators_from_h_broken", "sigma_terms_exact",
    "validate_columns", "verify_solution_literally", "residual", "defect_of",
    "chain_words", "to_tuple", "probe_vertices", "apply_all", "q_h1",
]


def _selftest():
    """Codex-witness control: `h1 = ()` there, so exact == shipped == right."""
    import json
    codex_h = ("cTTcttt", "", "cTcttt", "t", "")
    ops = operators_from_h(codex_h)
    _dw, defect = defect_of(codex_h)
    checks, bad, wrong = validate_columns(codex_h, ops)
    brk = operators_from_h_broken(codex_h)
    same = [ops[i] == brk[i] for i in range(5)]
    out = {
        "codex_witness_defect": [len(defect),
                                 sum(abs(v) for v in defect.values()),
                                 sum(defect.values())],
        "literal_probe_checks": checks,
        "literal_probe_mismatches": bad,
        "columns_wrong": wrong,
        "exact_equals_shipped_at_h1_trivial": all(same),
    }
    print(json.dumps(out))
    ok = (out["codex_witness_defect"] == [21, 48, 0] and bad == 0
          and all(same))
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(_selftest())
