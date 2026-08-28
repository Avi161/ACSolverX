"""W2d: the six-parameter normal form generates the period-two census exactly.

`W2_PERIOD_TWO_BASELINE_CENSUS.md` enumerates the essential chains (R,S,U)
of the period-two backward system by conjugate enumeration. W2d claims that
the same set is produced by a CLOSED-FORM generator: every step of the
recurrence has the shape

    NEW = P * (a conjugate of Q^-1),        (P,Q) = (A,B), (B,R), (R,S)

and writing that conjugate canonically as u*rho*u^-1 (reduced as written,
rho a letter-rotation of cyc(Q^-1), k = |u|) gives the length identity

    |NEW| = |P| + |cyc(Q^-1)| + 2k - 2d,    d = |lcp(u rho u^-1, P^-1)|,

so a cap |NEW| <= L forces d >= k - m with
m = max(0, (L - |P| - |cyc Q^-1|) // 2). For m = 0 this pins u to be a
LITERAL PREFIX of P^-1 — the conjugator is not a free ball element, it is a
prefix of a word already in the problem. Applied at all three levels, a
chain is then indexed by six integers (k1,p1,k2,p2,k3,p3) plus a terminal
conjugator g.

This checker runs that normal form as a GENERATOR and set-compares its
output against the census enumeration.

  census side    : the census generator's own conjugate enumeration
                   (`conjugates()` from period_two_solution_census),
  generator side : this file's prefix/rotation enumeration, written
                   independently — it never calls `conjugates()`.

Both sides share only the primitive word arithmetic (reduce/mul/inv/
cyc_form), so an agreement is a real cross-check of the enumeration, not a
tautology.

Controls (both can fail; a run whose controls fail proves nothing):

  C1 witness parametrization: the tuple (k1,p1,k2,p2,k3,p3,g)
     = (2,1,0,2,1,1,"") must emit exactly the codex witness chain
     (TTctcTctc, TTTcttcTctt, TTcttcTc). Pins the parameter conventions.
  C2 non-vacuity at cap 19: STRICT pinning (m = 0) is asserted at level 1
     at cap 19, where the length identity says it must FAIL. The control
     passes only if the strict model genuinely MISSES census R values
     there. Without C2, "the model agrees" could mean the model is simply
     enumerating everything.

Caps are ceilings, not budgets: every count is a lower bound, and the
terminal conjugator search is bounded by GPAD (the census's own ceiling).

Usage:  period_two_normal_form.py CAP [GPAD]
Exit 0 only if the two sides agree exactly AND both controls pass.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Shared primitive word arithmetic + the CENSUS side's own enumerator.
from period_two_solution_census import (
    A,
    B,
    ball,
    conjugates,
    cyc_form,
    cyc_reduce,
    inv,
    mul,
    reduce_w,
)

CAP = int(sys.argv[1]) if len(sys.argv) > 1 else 12
GPAD = int(sys.argv[2]) if len(sys.argv) > 2 else 5

WITNESS = ("TTctcTctc", "TTTcttcTctt", "TTcttcTc")
WITNESS_PARAMS = (2, 1, 0, 2, 1, 1, "")

_CF = {}


def cf(w):
    """Memoized conjugacy-class normal form (hot in the terminal test)."""
    v = _CF.get(w)
    if v is None:
        v = cyc_form(w)
        _CF[w] = v
    return v


# ---------------------------------------------------------------------------
# generator side: prefix/rotation enumeration (independent of conjugates())
# ---------------------------------------------------------------------------

def rotations(w):
    """The letter-rotations of cyc(w), in a fixed deterministic order.

    Returns (sorted rotation list, the cyclic core). Rotation index p_i in
    the normal form is the position in this sorted list.
    """
    core = cyc_reduce(w)
    if not core:
        return [], core
    rots = {reduce_w(core[i:] + core[:i]) for i in range(len(core))}
    return sorted(rots), core


def pinned_step(base, cl_of, cap, m=0):
    """One level of the normal form.

    Emits (new_word, k, p) for NEW = base * u*rho*u^-1 with

        u   = (base^-1)[0:k]          -- PINNED prefix (strict form, m = 0)
        rho = rotations(cl_of)[p]     -- letter rotation of the core
        |u rho u^-1| = |core| + 2k    -- canonical (no seam cancellation)
        0 < |NEW| <= cap

    `m > 0` relaxes the pinning to "u agrees with base^-1 on its first
    k - m letters", which the length identity says is the correct form once
    cap exceeds |base| + |core|. m = 0 is the strict form the draft claims
    for caps <= 18.
    """
    pref = inv(base)
    rots, core = rotations(cl_of)
    if not core:
        return
    out = []
    for k in range(0, len(pref) + 1):
        heads = [pref[:k]] if m == 0 else _relaxed_heads(pref, k, m)
        for u in heads:
            ui = inv(u)
            for p, rho in enumerate(rots):
                x = mul(u, rho, ui)
                if len(x) != len(core) + 2 * k:
                    continue  # not the canonical form for this k
                new = mul(base, x)
                if 0 < len(new) <= cap:
                    out.append((new, k, p))
    yield from out


def _relaxed_heads(pref, k, m):
    """u's with u[0:k-m] = pref[0:k-m] and the last m letters free."""
    fixed = k - m
    if fixed < 0:
        fixed = 0
    if fixed > len(pref):
        return []
    head = pref[:fixed]
    tails = [w for w in ball(k - fixed) if len(w) == k - fixed]
    out = []
    for tl in tails:
        u = reduce_w(head + tl)
        if len(u) == k:
            out.append(u)
    return out


def generate(cap, gpad):
    """All chains (R,S,U) emitted by the six-parameter normal form."""
    gballs = [(g, inv(g)) for g in ball(gpad)]
    chains = {}
    for R, k1, p1 in pinned_step(A, inv(B), cap):
        for S, k2, p2 in pinned_step(B, inv(R), cap):
            cf_s = cf(S)
            # dedupe U before the (expensive) terminal test
            us = {}
            for U, k3, p3 in pinned_step(R, inv(S), cap):
                us.setdefault(U, (k3, p3))
            for U, (k3, p3) in us.items():
                for g, gi in gballs:
                    if cf(mul(U, g, "t", gi)) == cf_s:
                        chains.setdefault(
                            (R, S, U), (k1, p1, k2, p2, k3, p3, g)
                        )
                        break
    return chains


def emit_from_params(params, cap, gpad):
    """Control C1: rebuild one chain from an explicit parameter tuple."""
    k1, p1, k2, p2, k3, p3, g = params
    r_rots, _ = rotations(inv(B))
    u1 = inv(A)[:k1]
    R = mul(A, mul(u1, r_rots[p1], inv(u1)))
    s_rots, _ = rotations(inv(R))
    u2 = inv(B)[:k2]
    S = mul(B, mul(u2, s_rots[p2], inv(u2)))
    u_rots, _ = rotations(inv(S))
    u3 = inv(R)[:k3]
    U = mul(R, mul(u3, u_rots[p3], inv(u3)))
    ok = cf(mul(U, g, "t", inv(g))) == cf(S)
    return (R, S, U), ok


# ---------------------------------------------------------------------------
# census side: the census generator's own enumeration
# ---------------------------------------------------------------------------

def census_r_set(cap):
    rs = {mul(A, x) for x in conjugates(inv(B), cap + len(A))}
    return sorted(r for r in rs if 0 < len(r) <= cap)


def census_chains(cap, gpad):
    gballs = [(g, inv(g)) for g in ball(gpad)]
    chains = set()
    for R in census_r_set(cap):
        s_set = {mul(B, y) for y in conjugates(inv(R), cap + len(B))}
        for S in sorted(s for s in s_set if 0 < len(s) <= cap):
            cf_s = cf(S)
            u_set = {mul(R, w) for w in conjugates(inv(S), cap + len(R))}
            for U in sorted(u for u in u_set if 0 < len(u) <= cap):
                for g, gi in gballs:
                    if cf(mul(U, g, "t", gi)) == cf_s:
                        chains.add((R, S, U))
                        break
    return chains


# ---------------------------------------------------------------------------
# controls
# ---------------------------------------------------------------------------

def control_witness():
    """C1: the recorded witness parametrization emits the witness chain."""
    chain, terminal_ok = emit_from_params(WITNESS_PARAMS, CAP, GPAD)
    return {
        "params": list(WITNESS_PARAMS[:6]) + [WITNESS_PARAMS[6]],
        "emitted": list(chain),
        "equals_witness": chain == WITNESS,
        "terminal_satisfied": terminal_ok,
        "passed": chain == WITNESS and terminal_ok,
    }


def control_cap19_strict_pinning_fails():
    """C2 (non-vacuity): strict pinning MUST miss R values at cap 19.

    The length identity gives m = (19 - |A| - |cyc B^-1|)//2 = 1 at cap 19,
    so the strict (m = 0) model cannot be complete there. If this control
    ever reports zero missed, the pinning predicate is enumerating
    everything and the agreement at lower caps is vacuous.
    """
    cap = 19
    truth = set(census_r_set(cap))
    strict = {r for r, _, _ in pinned_step(A, inv(B), cap, m=0)}
    missed_strict = truth - strict
    return {
        "cap": cap,
        "census_R": len(truth),
        "strict_pinning_R": len(strict),
        "strict_missed": len(missed_strict),
        "strict_is_subset": strict <= truth,
        # passes only if strict genuinely under-covers (non-vacuity)
        "passed": len(missed_strict) > 0 and strict <= truth,
    }


def main():
    c1 = control_witness()
    c2 = control_cap19_strict_pinning_fails()

    gen = generate(CAP, GPAD)
    generated = set(gen)
    truth = census_chains(CAP, GPAD)
    missed = sorted(truth - generated)
    spurious = sorted(generated - truth)

    summary = {
        "caps": {"CAP": CAP, "GPAD": GPAD},
        "census_chains": len(truth),
        "generated": len(generated),
        "hits": len(truth & generated),
        "missed": len(missed),
        "spurious": len(spurious),
        "exact": not missed and not spurious,
        "witness_in_census": WITNESS in truth,
        "witness_in_generated": WITNESS in generated,
        "controls": {"C1_witness_params": c1, "C2_cap19_nonvacuity": c2},
    }
    print(json.dumps(summary))
    for ch in missed[:10]:
        print(json.dumps({"MISSED": list(ch)}))
    for ch in spurious[:10]:
        print(json.dumps({"SPURIOUS": list(ch)}))

    if not c1["passed"]:
        print("CONTROL C1 FAILURE: the recorded witness parametrization does "
              "not emit the witness chain — parameter conventions are wrong. "
              "No conclusion may be drawn.")
        return 3
    if not c2["passed"]:
        print("CONTROL C2 FAILURE: strict pinning did NOT under-cover at cap "
              "19. The pinning predicate is vacuous (it enumerates "
              "everything), so agreement at lower caps proves nothing.")
        return 4
    if missed or spurious:
        print(f"DISAGREEMENT: {len(missed)} missed, {len(spurious)} spurious "
              f"at CAP={CAP}. The normal form does not generate the census.")
        return 2
    print(f"NORMAL FORM EXACT at CAP={CAP}, GPAD={GPAD}: "
          f"{len(truth)} census chains, {len(generated)} generated, "
          f"0 missed, 0 spurious; controls C1 and C2 passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
