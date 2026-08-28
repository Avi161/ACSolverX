"""W2e: is layer-1 one-hop liveness a function of cyc(S) only?

W2D (b.1) proves a *collapse lemma*: from equation (3) onward the census
system sees S only through its conjugacy class cyc(S).  W2D (d.4) flags the
load-bearing open question the lemma does NOT settle: the layer-1 liveness
test of `period_two_baseline_liveness.py` is built from the literal words
(R, S, U), so two census chains sharing (R, cyc S, U) but differing in the S
representative could a priori get different verdicts.  If liveness factored
through cyc(S), a uniform argument would quantify over invariant triples (31
at cap 17) instead of representatives (unbounded).

This checker settles the question at the WINDOW level and pins the exact
algebraic obstruction to a proof.

METHOD
------
1. Partition the 17 cap-12 census chains by (R, cyc S, U) — the granularity
   of the collapse lemma — and by the coarser (R, cyc S, cyc U).

2. For every class with >= 2 members, find gamma with S_j = gamma S_0
   gamma^-1 (both S lie in B*Cl(R^-1), so gamma exists).

3. GAUGE WINDOWS, CENTRALIZER-INDEXED.  For a slot whose defining condition
   is `h * base * h^-1 == target`, the solution set is exactly
   h_base * C_Q(base), and C_Q(base) = <zeta> is infinite cyclic for the
   hyperbolic bases occurring here.  So the windows are indexed by an
   integer:  h(k) = h_base * zeta^k,  |k| <= K.

   This is the point of the rewrite: enumerating conjugators from a *ball*
   (as `analyze_reps` does) gives the two members of a class DIFFERENT
   numbers of representatives per slot — the h1 coset of one member can have
   3 short elements while the other has 2 — so an OR over that slot is a
   rigged comparison.  Indexing by k gives both members exactly 2K+1
   windows per slot.  A structural control asserts that every conjugator
   found in a ball really is h_base * zeta^k.

4. WINDOW ALIGNMENT.  Under S -> S' = gamma S gamma^-1 with R and U fixed:
       h0' = h0                 (h0's condition mentions R only)
       h2' = h2 gamma^-1        (h2 S^-1 h2^-1 = R^-1 U   is preserved)
       h3' = h3 gamma^-1        (h3 S h3^-1  = U g t g^-1 is preserved)
       g'  = g                  (g is found from U and cyc S alone)
   and the h1 slot has NO canonical image: h1 R^-1 h1^-1 = B^-1 S, and
   B^-1 (gamma S gamma^-1) is not a translate of B^-1 S.  Since the five
   lifting operators do not depend on h1 at all (only the defect does), h1
   is the residual gauge and the comparison is made on the h1-reduced
   predicate
       P(h0, k2, k3) = (some |k1| <= K makes this window solvable mod p)
   compared index-for-index, member0 at (h0, k2, k3) against member1 at
   (h0, h2(k2) gamma^-1, h3(k3) gamma^-1).  Both members get the same
   number of h1 windows, so neither side is handed extra chances.

   Because gamma is only defined modulo C_Q(S_0) = <zeta_S>, a different
   gamma shifts which k2, k3 indices get paired; --gamma-check re-runs the
   comparison with a second gamma and reports whether the verdict survives.

CONTROLS (any failure voids the run, exit 2)
  - codex fixed-h witness control: defect data (21, 48, 0), as in W2b.
  - centralizer control: for every slot of every chain, each conjugator in
    ball(CTRL_RADIUS) is verified to equal h_base * zeta^k.
  - non-vacuity + dynamic range: at least one aligned window pair per class,
    and BOTH solvable and unsolvable windows must occur in the run.
  - mutation control: the comparator is re-run against a corrupted copy of a
    member's window table (one mod-2 bit flipped) and MUST report a
    mismatch.  A comparator that cannot fail is not evidence.
  - alignment validity: every aligned h2'/h3' is re-verified as a genuine
    conjugator for the second member by direct string arithmetic.

NONCLAIMS
  - Chain-level "not live at tested windows" stays inconclusive (an untested
    window may solve), so a chain-level verdict difference is NOT a
    counterexample.  Only WINDOW-level comparisons — where the two sides ask
    the same decidable linear-algebra question — carry evidence either way.
  - K and cap 12 are ceilings, not budgets: they can only under-report.
  - No claim about the free-group depth-four class, the bridge, AK(3),
    stable AC, or AC.

EXIT CODES
  0  run completed, every control green.  A counterexample is a RESULT, not
     an error: it is reported in summary.verdict.
  2  a control failed — the run is void and none of its numbers may be used.

Usage (the guard caps wall clock at 60 s, so slice):
  # class comparison, five (R, cyc S, U) classes with >= 2 members
  python3 period_two_liveness_invariance.py --k 1 --classes 0:3 --json OUT
  python3 period_two_liveness_invariance.py --k 1 --classes 3:5 --json OUT
  # wider gauge range, h1 held fixed
  python3 period_two_liveness_invariance.py --k 2 --k1 0 --classes 2:3
  # gamma-independence control
  python3 period_two_liveness_invariance.py --k 1 --classes 0:2 --gamma-check
  # per-chain sweep: independent reproduction of W2b's six live chains
  python3 period_two_liveness_invariance.py --k 1 --chains 0:8
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

# `period_two_solution_census` parses sys.argv at import time (CAP/GPAD), so
# this checker's CLI flags must be hidden from it.
_ARGV = list(sys.argv)
sys.argv = sys.argv[:1]
import period_two_baseline_liveness as LV
from period_two_solution_census import (
    A as QA,
    B as QB,
    ball,
    cyc_form,
    inv as sinv,
    mul as smul,
)

sys.argv = _ARGV

CHAINS_FILE = Path(__file__).resolve().parent / "period_two_census_chains.json"
WITNESS = ("TTctcTctc", "TTTcttcTctt", "TTcttcTc")
CODEX_H = ("cTTcttt", "", "cTcttt", "t", "")
BASE_RADIUS = 10      # radius used to find the shortest conjugator of a slot
CTRL_RADIUS = 10      # radius over which the centralizer control is checked
PRIMES = ("2", "3", "5")


# ------------------------------------------------------- gauge machinery


def shortest_conjugator(base, target, radius=BASE_RADIUS):
    for h in ball(radius):
        if smul(h, base, sinv(h)) == target:
            return h
    return None


def cyc_decompose(w):
    """w = v * rho * v^-1 with rho cyclically reduced (reduced as written)."""
    v, s = "", smul(w)
    while len(s) >= 2 and smul(s[-1] + s[0]) == "":
        v = v + s[0]
        s = smul(s[1:-1])
    return v, s


def primitive_root(rho):
    """Shortest rho0 with rho = rho0^m (rho cyclically reduced)."""
    n = len(rho)
    for d in range(1, n + 1):
        if n % d:
            continue
        cand = rho[:d]
        if smul(*([cand] * (n // d))) == rho:
            return cand
    return rho


def centralizer_generator(w):
    """Generator of C_Q(w) for w of infinite order.

    In a free product, the centralizer of an element not conjugate into a
    factor is infinite cyclic, generated by the element's primitive root.
    Writing w = v rho v^-1 with rho cyclically reduced and rho = rho0^m,
    that generator is zeta = v rho0 v^-1.  Verified below by asserting it
    commutes and by the ball-wide `centralizer_control`.
    """
    v, rho = cyc_decompose(w)
    if len(rho) <= 1:
        return None  # trivial or conjugate into <c>: not handled here
    zeta = smul(v, primitive_root(rho), sinv(v))
    if not zeta or smul(zeta, w) != smul(w, zeta):
        return None
    return zeta


def power(z, k):
    if k == 0:
        return ""
    if k < 0:
        return power(sinv(z), -k)
    out = ""
    for _ in range(k):
        out = smul(out, z)
    return out


def slot(base, target, k_max):
    """Centralizer-indexed window list for one gauge slot."""
    h_b = shortest_conjugator(base, target)
    if h_b is None:
        return None
    zeta = centralizer_generator(base)
    if zeta is None:
        return None
    reps = {}
    for k in range(-k_max, k_max + 1):
        h = smul(h_b, power(zeta, k))
        assert smul(h, base, sinv(h)) == target, "slot index broke conjugacy"
        reps[k] = h
    return {"base": base, "target": target, "h_base": h_b, "zeta": zeta,
            "reps": reps}


def centralizer_control(sl):
    """Every conjugator in ball(CTRL_RADIUS) must be h_base * zeta^k."""
    found = [h for h in ball(CTRL_RADIUS)
             if smul(h, sl["base"], sinv(h)) == sl["target"]]
    powers = {}
    k = -40
    while k <= 40:
        powers[smul(sl["h_base"], power(sl["zeta"], k))] = k
        k += 1
    missing = [h for h in found if h not in powers]
    return {"found_in_ball": len(found), "not_a_zeta_power": missing}


def chain_slots(chain, k_max, k1_max=None):
    R, S, U = chain
    k1_max = k_max if k1_max is None else k1_max
    g = LV.find_target_conjugator(U, S)
    if g is None:
        return None
    s0 = slot(sinv(QB), smul(sinv(QA), R), k_max)
    s1 = slot(sinv(R), smul(sinv(QB), S), k1_max)
    s2 = slot(sinv(S), smul(sinv(R), U), k_max)
    s3 = slot(S, smul(U, smul(g, "t", sinv(g))), k_max)
    if None in (s0, s1, s2, s3):
        return None
    return {"h0": s0, "h1": s1, "h2": s2, "h3": s3, "g": g}


# --------------------------------------------------------- window solver


_WINDOW_CACHE = {}


def evaluate_window(h0, h1, h2, h3, g):
    """One-hop solvability of ONE gauge window, per prime.  No early exit."""
    ck = (h0, h1, h2, h3, g)
    if ck in _WINDOW_CACHE:
        return _WINDOW_CACHE[ck]
    _WINDOW_CACHE[ck] = rec = _evaluate_window(h0, h1, h2, h3, g)
    return rec


def _evaluate_window(h0, h1, h2, h3, g):
    fh = [LV.to_tuple(x) for x in (h0, h1, h2, h3, g)]
    r = LV.multiply(LV.SOURCE_A, LV.conjugate(LV.inverse(LV.SOURCE_B), fh[0]))
    s = LV.multiply(LV.SOURCE_B, LV.conjugate(LV.inverse(r), fh[1]))
    u = LV.multiply(r, LV.conjugate(LV.inverse(s), fh[2]))
    z = LV.multiply(LV.inverse(u), LV.conjugate(s, fh[3]))
    target_f = LV.conjugate((LV.T,), fh[4])
    defect_word = LV.multiply(z, LV.inverse(target_f))
    if LV.quotient_reduce(defect_word) != ():
        return {"status": "DEFECT_NOT_IN_N",
                "solvable": {p: False for p in PRIMES}}
    defect = LV.relation_module(defect_word)
    operators = LV.build_operators_general(r, s, u, fh[2], fh[3], target_f)
    aug = sum(defect.values())
    rec = {"defect_terms": len(defect),
           "defect_l1": sum(abs(v) for v in defect.values()),
           "defect_augmentation": aug}
    if aug != 0:
        rec["status"] = "DEAD_AUGMENTATION"
        rec["solvable"] = {p: False for p in PRIMES}
        return rec
    rows, rhs, n_vars = LV.one_hop_system(defect, operators)
    rec["one_hop_vars"] = n_vars
    rec["solvable"] = {p: bool(LV.solve_mod_p(rows, rhs, int(p)))
                       for p in PRIMES}
    rec["status"] = ("LIVE_AT_ONE_HOP_MOD_235"
                     if all(rec["solvable"].values()) else "UNSOLVABLE")
    return rec


def sweep(slots, k_max, h2_override=None, h3_override=None, k1_max=None):
    """Full window table keyed by (k0, k1, k2, k3).

    h2_override / h3_override replace the slot's own representative list by
    an externally supplied {k: word} map — this is how member1 is evaluated
    at member0's gamma-aligned windows, index for index.
    """
    ks = range(-k_max, k_max + 1)
    k1s = range(-(k_max if k1_max is None else k1_max),
                (k_max if k1_max is None else k1_max) + 1)
    h2reps = h2_override if h2_override is not None else slots["h2"]["reps"]
    h3reps = h3_override if h3_override is not None else slots["h3"]["reps"]
    table = {}
    for k0 in ks:
        for k1 in k1s:
            for k2 in ks:
                for k3 in ks:
                    table[(k0, k1, k2, k3)] = evaluate_window(
                        slots["h0"]["reps"][k0], slots["h1"]["reps"][k1],
                        h2reps[k2], h3reps[k3], slots["g"])
    return table


def reduce_over_h1(table):
    """OR over the residual (operator-free) h1 gauge -> P(k0, k2, k3)."""
    out = {}
    for (k0, k1, k2, k3), rec in table.items():
        cur = out.setdefault((k0, k2, k3),
                             {p: False for p in PRIMES}
                             | {"live": False, "n_h1": 0})
        cur["n_h1"] += 1
        for p in PRIMES:
            cur[p] = cur[p] or rec["solvable"][p]
        cur["live"] = cur["live"] or rec["status"] == "LIVE_AT_ONE_HOP_MOD_235"
    return out


# ------------------------------------------------- the transformation law


def _gr(*terms):
    return LV.group_ring(*terms)


def _mul(a, b):
    return LV.multiply_group_ring(a, b)


def _sub(a, b):
    return LV.add_group_ring(a, {w: -c for w, c in b.items()})


def _rmul(op, w):
    """Right multiplication of a group-ring element by a group element."""
    return LV.group_ring(*((c, LV.quotient_multiply(x, w))
                           for x, c in op.items()))


def transformation_law(R, S, U, h2, h3, g, gamma):
    """Machine check of the closed-form law for S -> gamma S gamma^-1.

    With R, U, g held fixed and the window aligned by h2 -> h2 gamma^-1,
    h3 -> h3 gamma^-1, write bridge = h2 + U^-1 h3 and d_r = A - R.  Then

        L0  = -(U^-1 + bridge*S) * d_r        L0' = -(U^-1 + bridge*S*gi) * d_r
        L1  =  bridge * (B - S)               L1' =  bridge * (gi*B - S*gi)
        L2' = L2,  L3' = L3,  L4' = L4                       (gi = gamma^-1)

    So the alignment right-multiplies the *bridge*S* summand of L0 and the
    *S* summand of L1 by gamma^-1, while left-multiplying the B summand of
    L1 by gamma^-1 and leaving L2, L3, L4 alone.  There is therefore no
    single unit u with L_i' = L_i u for all i (L2' = L2 forces u = 1) and no
    module automorphism of M carrying one system to the other unless
    gamma = 1.  Returns the verified booleans.
    """
    q = lambda w: LV.quotient_reduce(LV.to_tuple(w))
    gi = q(sinv(gamma))
    Sp = smul(gamma, S, sinv(gamma))
    h2p, h3p = smul(h2, sinv(gamma)), smul(h3, sinv(gamma))
    w = q(smul(g, "t", sinv(g)))
    O0 = LV.build_operators_general(q(R), q(S), q(U), q(h2), q(h3), w)
    O1 = LV.build_operators_general(q(R), q(Sp), q(U), q(h2p), q(h3p), w)
    bridge = _gr((1, q(h2)),
                 (1, LV.quotient_multiply(LV.quotient_inverse(q(U)), q(h3))))
    d_r = _gr((1, q(QA)), (-1, q(R)))
    uinv = _gr((1, LV.quotient_inverse(q(U))))
    bS = _mul(bridge, _gr((1, q(S))))
    pred_L0 = _mul(_sub(_gr(), LV.add_group_ring(uinv, _rmul(bS, gi))), d_r)
    pred_L1 = _mul(bridge, _sub(_gr((1, LV.quotient_multiply(gi, q(QB)))),
                                _rmul(_gr((1, q(S))), gi)))
    closed_L0 = _mul(_sub(_gr(), LV.add_group_ring(uinv, bS)), d_r)
    closed_L1 = _mul(bridge, _sub(_gr((1, q(QB))), _gr((1, q(S)))))
    units = {"1": q(""), "gamma^-1": gi, "gamma": q(gamma)}
    intertwiner = {name: all(O1[i] == _rmul(O0[i], u) for i in range(5))
                   for name, u in units.items()}
    return {
        "L2_L3_L4_unchanged": [O0[i] == O1[i] for i in (2, 3, 4)],
        "L0_closed_form": O0[0] == closed_L0,
        "L1_closed_form": O0[1] == closed_L1,
        "L0_prime_matches_law": O1[0] == pred_L0,
        "L1_prime_matches_law": O1[1] == pred_L1,
        "L0_changed": O0[0] != O1[0],
        "L1_changed": O0[1] != O1[1],
        "uniform_right_unit_intertwiner": intertwiner,
    }


def compare_strict(table0, table1):
    """Fully specified window comparison: no existential on either side.

    Both members are evaluated at the SAME index (k0,k1,k2,k3); member1's h2,
    h3 are member0's gamma-aligned words, and the h1 slot uses each member's
    own shortest base with the shared centralizer generator zeta_{R^-1}.
    Each entry is then a decidable yes/no about one concrete linear system,
    so a MISMATCH here is a hard counterexample to the claim that this
    alignment carries the solvable-window set across the class — it does not
    rest on "no tested window solved" on either side.
    """
    rows, mism = [], []
    for key in sorted(table0):
        a, b = table0[key], table1.get(key)
        if b is None:
            continue
        agree = all(a["solvable"][p] == b["solvable"][p] for p in PRIMES)
        row = {"k": list(key),
               "member0": a["solvable"], "member1": b["solvable"],
               "defect0": [a.get("defect_terms"), a.get("defect_l1")],
               "defect1": [b.get("defect_terms"), b.get("defect_l1")],
               "status": "AGREE" if agree else "MISMATCH"}
        rows.append(row)
        if not agree:
            mism.append(row)
    return rows, mism


def compare(red0, red1):
    """Index-for-index comparison of two h1-reduced window tables."""
    rows, mismatches = [], []
    for key in sorted(red0):
        a, b = red0[key], red1.get(key)
        if b is None:
            rows.append({"k": list(key), "status": "MISSING"})
            continue
        agree = all(a[p] == b[p] for p in PRIMES)
        row = {"k": list(key),
               "member0": {p: a[p] for p in PRIMES},
               "member1": {p: b[p] for p in PRIMES},
               "member0_live": a["live"], "member1_live": b["live"],
               "n_h1": [a["n_h1"], b["n_h1"]],
               "status": "AGREE" if agree else "MISMATCH"}
        rows.append(row)
        if not agree:
            mismatches.append(row)
    return rows, mismatches


def gammas_for(s_from, s_to, how_many=2, radius=BASE_RADIUS):
    out = []
    for h in ball(radius):
        if smul(h, s_from, sinv(h)) == s_to:
            out.append(h)
            if len(out) >= how_many:
                break
    return out


# ------------------------------------------------------------------ main


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=2,
                    help="gauge index range: k in [-K, K] per slot")
    ap.add_argument("--json", type=str, default="")
    ap.add_argument("--classes", type=str, default="",
                    help="slice of the multi-member class list, e.g. 0:2")
    ap.add_argument("--k1", type=int, default=-1,
                    help="separate gauge range for the h1 slot (default: --k)")
    ap.add_argument("--chains", type=str, default="",
                    help="instead of the class comparison, sweep this slice "
                         "of the 17 chains and report per-chain live counts")
    ap.add_argument("--gamma-check", action="store_true",
                    help="also compare under a second gamma (slow)")
    args = ap.parse_args()
    K = args.k
    K1 = args.k if args.k1 < 0 else args.k1
    if args.classes:
        lo, hi = args.classes.split(":")
        c_lo = int(lo) if lo else 0
        c_hi = int(hi) if hi else 10 ** 9
    else:
        c_lo, c_hi = 0, 10 ** 9

    chains = [tuple(c) for c in json.loads(CHAINS_FILE.read_text())]
    assert WITNESS in chains, "witness chain missing from census file"
    problems = []

    # --- control 1: codex fixed-h witness reproduces the published defect --
    ctl = LV.analyze(WITNESS, fixed_h=CODEX_H)
    ctl_data = (ctl["defect_terms"], ctl["defect_l1"],
                ctl["defect_augmentation"])
    print(json.dumps({"control": "fixed_h_witness", "defect": list(ctl_data),
                      "want": [21, 48, 0],
                      "result": "passed" if ctl_data == (21, 48, 0)
                      else "FAILED"}))
    if ctl_data != (21, 48, 0):
        return 2

    # --- partition ---------------------------------------------------------
    def part(key):
        d = {}
        for ch in chains:
            d.setdefault(key(ch), []).append(ch)
        return d

    fine = part(lambda c: (c[0], cyc_form(c[1]), c[2]))
    coarse = part(lambda c: (c[0], cyc_form(c[1]), cyc_form(c[2])))
    print(json.dumps({
        "chains": len(chains),
        "classes_R_cycS_U": len(fine),
        "classes_R_cycS_U_multi": sum(1 for v in fine.values() if len(v) > 1),
        "classes_R_cycS_cycU": len(coarse),
        "classes_R_cycS_cycU_multi": sum(1 for v in coarse.values()
                                         if len(v) > 1),
    }))

    # --- slots + centralizer control for every chain -----------------------
    slots = {}
    for ch in chains:
        sl = chain_slots(ch, K, K1)
        slots[ch] = sl
        if sl is None:
            problems.append(f"slots not found for {ch}")
            continue
        bad = {}
        for name in ("h0", "h1", "h2", "h3"):
            c = centralizer_control(sl[name])
            if c["not_a_zeta_power"]:
                bad[name] = c
        if bad:
            problems.append(f"centralizer control failed for {ch}: {bad}")
    print(json.dumps({"control": "centralizer_generates_every_conjugator",
                      "result": "passed" if not problems else "FAILED"}))

    # --- optional: per-chain sweep (independent reproduction of W2b) -------
    if args.chains:
        lo, hi = args.chains.split(":")
        lo = int(lo) if lo else 0
        hi = int(hi) if hi else len(chains)
        n_live = n_uns = 0
        for i, ch in enumerate(chains):
            if not (lo <= i < hi):
                continue
            t = sweep(slots[ch], K, k1_max=K1)
            lw = sum(1 for r in t.values()
                     if r["status"] == "LIVE_AT_ONE_HOP_MOD_235")
            n_live += lw
            n_uns += len(t) - lw
            print(json.dumps({
                "chain_index": i, "chain": list(ch),
                "is_witness": ch == WITNESS,
                "windows": len(t), "live_windows": lw,
                "cyc_S": cyc_form(ch[1]),
                "verdict": ("LIVE_AT_ONE_HOP_MOD_235" if lw
                            else "NOT_LIVE_AT_TESTED_WINDOWS")}))
        print(json.dumps({"summary": {
            "mode": "per_chain_sweep", "chain_slice": [lo, hi],
            "k_range": [-K, K], "k1_range": [-K1, K1],
            "windows_one_hop_live": n_live,
            "windows_one_hop_unsolvable": n_uns,
            "controls": {"fixed_h_witness": "passed",
                         "centralizer_generates_every_conjugator": True},
            "nonclaims": ["NOT_LIVE_AT_TESTED_WINDOWS is inconclusive"]}}))
        return 2 if problems else 0

    # --- comparisons over the (R, cyc S, U) classes ------------------------
    class_reports = []
    total_mismatch = 0
    total_aligned = 0
    total_strict = 0
    total_strict_mismatch = 0
    n_solv = n_unsolv = 0
    multi = [(k, v) for k, v in sorted(fine.items()) if len(v) > 1]
    for c_i, (key, members) in enumerate(multi):
        if not (c_lo <= c_i < c_hi):
            continue
        m0 = members[0]
        sl0 = slots[m0]
        table0 = sweep(sl0, K, k1_max=K1)
        red0 = reduce_over_h1(table0)
        n_solv += sum(1 for r in table0.values()
                      if r["status"] == "LIVE_AT_ONE_HOP_MOD_235")
        n_unsolv += sum(1 for r in table0.values()
                        if r["status"] != "LIVE_AT_ONE_HOP_MOD_235")
        rep = {"class_key": list(key),
               "members": [list(m) for m in members], "pairs": []}
        for m1 in members[1:]:
            sl1 = slots[m1]
            gams = gammas_for(m0[1], m1[1])
            if not gams:
                rep["pairs"].append({"member1": list(m1),
                                     "status": "GAMMA_NOT_FOUND"})
                continue
            entry = {"member1": list(m1), "gamma": gams[0],
                     "g_shared": sl0["g"] == sl1["g"],
                     "zeta_h1_shared": sl0["h1"]["zeta"] == sl1["h1"]["zeta"],
                     "by_gamma": []}
            for gi_word in (gams if args.gamma_check else gams[:1]):
                gi = sinv(gi_word)
                h2o = {k: smul(v, gi) for k, v in sl0["h2"]["reps"].items()}
                h3o = {k: smul(v, gi) for k, v in sl0["h3"]["reps"].items()}
                # alignment validity, checked by string arithmetic
                for k, h in h2o.items():
                    assert smul(h, sinv(m1[1]), sinv(h)) == \
                        smul(sinv(m1[0]), m1[2]), "h2' alignment failed"
                for k, h in h3o.items():
                    assert smul(h, m1[1], sinv(h)) == \
                        smul(m1[2], smul(sl1["g"], "t", sinv(sl1["g"]))), \
                        "h3' alignment failed"
                law = [transformation_law(
                    m0[0], m0[1], m0[2], sl0["h2"]["reps"][k],
                    sl0["h3"]["reps"][k], sl0["g"], gi_word)
                    for k in sl0["h2"]["reps"]]
                law_ok = all(
                    all(x["L2_L3_L4_unchanged"]) and x["L0_closed_form"]
                    and x["L1_closed_form"] and x["L0_prime_matches_law"]
                    and x["L1_prime_matches_law"] for x in law)
                no_intertwiner = all(
                    not any(x["uniform_right_unit_intertwiner"].values())
                    for x in law)
                if not law_ok:
                    problems.append(
                        f"transformation law failed for {m0} -> {m1}")
                table1 = sweep(sl1, K, h2_override=h2o,
                               h3_override=h3o, k1_max=K1)
                red1 = reduce_over_h1(table1)
                n_solv += sum(1 for r in table1.values()
                              if r["status"] == "LIVE_AT_ONE_HOP_MOD_235")
                n_unsolv += sum(1 for r in table1.values()
                                if r["status"] != "LIVE_AT_ONE_HOP_MOD_235")
                rows, mism = compare(red0, red1)
                srows, smism = compare_strict(table0, table1)
                aligned = [r for r in rows if r["status"] != "MISSING"]
                entry["by_gamma"].append({
                    "gamma": gi_word,
                    "aligned_windows": len(aligned),
                    "agree": sum(1 for r in aligned if r["status"] == "AGREE"),
                    "mismatch": len(mism),
                    "member0_live_windows": sum(1 for r in aligned
                                                if r["member0_live"]),
                    "member1_live_windows": sum(1 for r in aligned
                                                if r["member1_live"]),
                    "transformation_law_verified": law_ok,
                    "L0_L1_changed": [law[0]["L0_changed"],
                                      law[0]["L1_changed"]],
                    "no_uniform_right_unit_intertwiner": no_intertwiner,
                    "strict_windows": len(srows),
                    "strict_mismatch": len(smism),
                    "strict_member0_solvable": sum(
                        1 for r in srows if all(r["member0"].values())),
                    "strict_member1_solvable": sum(
                        1 for r in srows if all(r["member1"].values())),
                    "strict_example_mismatch": smism[0] if smism else None,
                    "rows": rows,
                    "strict_rows": srows,
                })
                if gi_word == gams[0]:
                    total_aligned += len(aligned)
                    total_mismatch += len(mism)
                    total_strict += len(srows)
                    total_strict_mismatch += len(smism)
                    entry["mismatch"] = len(mism)
                    entry["aligned_windows"] = len(aligned)
                    entry["agree"] = len(aligned) - len(mism)
                    entry["example_mismatch"] = mism[0] if mism else None
            gv = [b["mismatch"] > 0 for b in entry["by_gamma"]]
            entry["gamma_independent_verdict"] = len(set(gv)) == 1
            rep["pairs"].append(entry)
        class_reports.append(rep)
        print(json.dumps({
            "class_index": c_i,
            "class_key": list(key),
            "members": [list(m) for m in members],
            "pairs": [{k: v for k, v in p.items()
                       if k not in ("by_gamma",)}
                      | {"by_gamma": [{k: v for k, v in b.items()
                                       if k not in ("rows", "strict_rows")}
                                      for b in p.get("by_gamma", [])]}
                      for p in rep["pairs"]],
        }))

    # --- control 2: non-vacuity + dynamic range ----------------------------
    if total_aligned == 0:
        problems.append("no aligned window pair formed (vacuous run)")
    if n_solv == 0 or n_unsolv == 0:
        problems.append(f"no dynamic range: solvable={n_solv} "
                        f"unsolvable={n_unsolv}")

    # --- control 3: mutation — the comparator must be able to say MISMATCH -
    mut_ok = False
    for key, members in multi[c_lo:min(c_hi, len(multi))][:1]:
        m0, m1 = members[0], members[1]
        red0 = reduce_over_h1(sweep(slots[m0], K, k1_max=K1))
        gi = sinv(gammas_for(m0[1], m1[1])[0])
        red1 = {k: dict(v) for k, v in reduce_over_h1(sweep(
            slots[m1], K, k1_max=K1,
            h2_override={k: smul(v, gi)
                         for k, v in slots[m0]["h2"]["reps"].items()},
            h3_override={k: smul(v, gi)
                         for k, v in slots[m0]["h3"]["reps"].items()})).items()}
        _, base_m = compare(red0, red1)
        kk = next(iter(red1))
        red1[kk]["2"] = not red1[kk]["2"]
        _, mut_m = compare(red0, red1)
        mut_ok = len(mut_m) != len(base_m)
        break
    if not mut_ok:
        problems.append("mutation control: comparator did not react to a "
                        "flipped mod-2 bit")

    summary = {
        "k_range": [-K, K],
        "k1_range": [-K1, K1],
        "class_slice": [c_lo, min(c_hi, len(multi))],
        "gamma_check": bool(args.gamma_check),
        "windows_per_chain": (2 * K + 1) ** 3 * (2 * K1 + 1),
        "windows_evaluated": n_solv + n_unsolv,
        "windows_one_hop_live": n_solv,
        "windows_one_hop_unsolvable": n_unsolv,
        "aligned_window_pairs": total_aligned,
        "aligned_window_mismatches": total_mismatch,
        "strict_window_pairs": total_strict,
        "strict_window_mismatches": total_strict_mismatch,
        "verdict": ("WINDOW_ALIGNED_INVARIANCE_HOLDS_ON_ALL_TESTED_PAIRS"
                    if total_mismatch == 0 and total_strict_mismatch == 0
                    else "COUNTEREXAMPLE_TO_WINDOW_ALIGNED_INVARIANCE"),
        "controls": {
            "fixed_h_witness": "passed",
            "centralizer_generates_every_conjugator": True,
            "non_vacuity_and_dynamic_range": total_aligned > 0
            and n_solv > 0 and n_unsolv > 0,
            "transformation_law_verified": not any(
                "transformation law" in p for p in problems),
            "mutation_detects_flipped_bit": mut_ok,
        },
        "nonclaims": [
            "chain-level NOT_LIVE_AT_TESTED_WINDOWS stays inconclusive; only "
            "window-level comparisons carry evidence",
            "K and cap 12 are ceilings, not budgets",
            "no claim about the free-group class, AK(3), stable AC, or AC",
        ],
    }
    if problems:
        summary["control_problems"] = problems
    print(json.dumps({"summary": summary}))

    if args.json:
        Path(args.json).write_text(json.dumps({
            "summary": summary,
            "partition_R_cycS_U": [{"key": list(k),
                                    "members": [list(m) for m in v]}
                                   for k, v in sorted(fine.items())],
            "partition_R_cycS_cycU": [{"key": list(k),
                                       "members": [list(m) for m in v]}
                                      for k, v in sorted(coarse.items())],
            "class_reports": class_reports,
        }, indent=1))
    return 2 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
