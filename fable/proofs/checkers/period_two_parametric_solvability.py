"""W2f: layer-1 one-hop solvability as an explicit function of the
six-parameter normal form.

W2d (c.2) gives a closed-form normal form for the whole period-two census
family: a chain is `(k1,p1,k2,p2,k3,p3,g)` with pinned prefixes
`u1 = A^-1[0:k1]`, `u2 = B^-1[0:k2]`, `u3 = R^-1[0:k3]` and rotation indices
`p_i`.  W2e refutes the cheap reduction ("liveness factors through cyc(S)"),
so the honest index set for a uniform layer-1 argument is the PARAMETER
FAMILY itself.  This checker computes the map

    (t, w)  ->  one-hop solvable?          t = (k1,p1,k2,p2,k3,p3,g)
                                           w = a centralizer-indexed window

for every census chain at caps 12-15 and every window with |k| <= K, records
the verdict PER PRIME (2, 3, 5) rather than only their conjunction, and then
hunts for structure that holds uniformly across the family:

  * the live fraction as the cap grows (rising / falling / stable — each is a
    different theorem target);
  * parameter coordinates that DETERMINE liveness on the tested family (an
    exact, checkable predicate: no value of the coordinate tuple carries both
    a live and a dead chain);
  * whether any parametric stratum is dead at every tested window, and
    whether a mechanism can be read off the closed-form operators
    (W2e section 4.1:  L0 = -(U^-1 + bridge*S)(A-R),  L1 = bridge*(B-S),
    L2 = 1 - U^-1 R,  L3 = U^-1 - w,  L4 = w - 1).

WINDOWS.  Identical family to W2e: each gauge slot's conjugator set is
h_base * C_Q(base) with C_Q(base) = <zeta> infinite cyclic, so windows are
indexed by four integers (k0,k1,k2,k3) in [-K,K].  Optionally a fifth axis
over alternative terminal conjugators g (--g-alts), since W2d (d.5) notes g
enters L3 and L4 directly.

NESTING.  The census at cap L is nested (verified here): chains(12) subset
chains(13) subset chains(14) subset chains(15).  So one sweep at cap 15
supplies every smaller cap by filtering on max(|R|,|S|,|U|), and the cap
columns are exact, not re-searched.

CONTROLS (any failure voids the run, exit 2)
  C1 fixed-h witness: the codex conjugators must reproduce the published
     defect data (21 terms, l1 48, augmentation 0).
  C2 fast-path equivalence: this file memoizes the one-hop system build for
     speed; the first --control-samples windows of every run are recomputed
     with the UNMODIFIED reference path of `period_two_liveness_invariance`
     and must agree on the whole record (defect stats and all three primes).
  C3 mutation control: an operator system is deliberately corrupted at a
     window where the witness is solvable, and the verdict MUST flip.  Two
     differently-shaped corruptions are used -- deleting one term of L0, and
     flipping one coefficient's sign in L3 -- and both must flip.  A pipeline
     that cannot report DEAD is not evidence.  The mutations live only inside
     the control function; the production path never sees them.
  C4 dynamic range: both outcomes must be producible in the run.  A slice
     restricted to a dead stratum has no live window of its own, so the live
     half may instead be supplied by C3's clean (uncorrupted) reference
     window, which is a real live verdict from the same code path.
  C5 closed-form conjugator vs ball: wherever the ball search finds a slot
     conjugator, the closed-form one must lie in the same coset h_ball*<zeta>,
     so the fallback of `slot2` cannot silently change the window family.
  Plus: the cap-12 chain set must equal the committed census file, the caps
     must be nested, and (report mode) the witness chain must come out LIVE.

NONCLAIMS
  - "NOT_LIVE_AT_TESTED_WINDOWS" is inconclusive at chain level (W2b
    doctrine): K, GPAD 5, ball(10) and the cap are CEILINGS, so every dead
    verdict can only be under-reporting.
  - A "determining coordinate set" is a statement about the tested family at
    the tested windows.  It is a predicate found by exhaustive search over
    the tested data, not a theorem, unless a mechanism is exhibited.
  - No claim about the free-group depth-four class, the bridge, AK(3),
    stable AC, or AC.

USAGE (the guard caps wall clock at 60 s; sweep mode is resumable)
  # 1. parameter table (one run, all caps)
  python3 period_two_parametric_solvability.py --mode chains \
      --json out/w2f_chains.json
  # 2. sweep, resumable: re-run until "remaining": 0
  python3 period_two_parametric_solvability.py --mode sweep --k 1 \
      --state out/w2f_sweep_k1.json --budget-seconds 45
  # slice explicitly instead, if preferred
  python3 period_two_parametric_solvability.py --mode sweep --k 1 \
      --chains 0:10 --state out/w2f_sweep_k1.json
  # 3. aggregate
  python3 period_two_parametric_solvability.py --mode report \
      --state out/w2f_sweep_k1.json --json out/w2f_report_k1.json
  # deep probe of a dead stratum (wider windows, alternative g)
  python3 period_two_parametric_solvability.py --mode sweep --k 2 --k1 1 \
      --g-alts 2 --only-dead out/w2f_sweep_k1.json \
      --state out/w2f_deep_k2.json --budget-seconds 45

EXIT CODES
  0  run completed, every control green (a dead stratum is a RESULT).
  2  a control failed — the run is void.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Both imported modules parse sys.argv at import time; hide this CLI.
_ARGV = list(sys.argv)
sys.argv = sys.argv[:1]
import period_two_baseline_liveness as LV
import period_two_liveness_invariance as INV
import period_two_normal_form as NF
from period_two_solution_census import (
    A as QA,
    B as QB,
    ball,
    cyc_form,
    inv as sinv,
    mul as smul,
)
sys.argv = _ARGV

from experiments.stable_ac.depth4_period_two_lift_certificate import (
    c_vertex,
    quotient_inverse,
    quotient_multiply,
    quotient_reduce,
)

HERE = Path(__file__).resolve().parent
CHAINS_FILE = HERE / "period_two_census_chains.json"
WITNESS = ("TTctcTctc", "TTTcttcTctt", "TTcttcTc")
CODEX_H = ("cTTcttt", "", "cTcttt", "t", "")
PRIMES = ("2", "3", "5")
CAPS = (12, 13, 14, 15)
GPAD = 5
G_RADIUS = 6


# ---------------------------------------------------------------- chains


def all_params(cap, gpad=GPAD):
    """Every (chain -> set of parameter tuples) at this cap.

    Written directly on `period_two_normal_form.pinned_step` (W2d's own
    generator) but WITHOUT its first-wins dedupe, so parametrization
    multiplicity is measured rather than assumed away.
    """
    gballs = [(g, sinv(g)) for g in ball(gpad)]
    out = {}
    for R, k1, p1 in NF.pinned_step(QA, sinv(QB), cap):
        for S, k2, p2 in NF.pinned_step(QB, sinv(R), cap):
            cs = NF.cf(S)
            for U, k3, p3 in NF.pinned_step(R, sinv(S), cap):
                for g, gi in gballs:
                    if NF.cf(smul(U, g, "t", gi)) == cs:
                        out.setdefault((R, S, U), {"params": set(),
                                                   "g": g})
                        out[(R, S, U)]["params"].add((k1, p1, k2, p2, k3, p3))
                        break
    return out


def chain_table():
    """Parameter table for every chain at cap 15, with cap nesting checks."""
    sets = {}
    for cap in CAPS:
        sets[cap] = all_params(cap)
    nested = all(set(sets[a]) <= set(sets[b])
                 for a, b in zip(CAPS, CAPS[1:]))
    census12 = set(tuple(c) for c in json.loads(CHAINS_FILE.read_text()))
    rows = []
    top = sets[CAPS[-1]]
    for ch in sorted(top):
        ps = sorted(top[ch]["params"])
        R, S, U = ch
        rows.append({
            "chain": list(ch),
            "params": list(ps[0]),
            "n_parametrizations": len(ps),
            "g_gen": top[ch]["g"],
            "lens": [len(R), len(S), len(U)],
            "maxlen": max(len(R), len(S), len(U)),
            "cyc_S": cyc_form(S),
            "is_witness": ch == WITNESS,
        })
    return rows, {
        "cap_counts": {str(c): len(sets[c]) for c in CAPS},
        "caps_nested": nested,
        "cap12_equals_committed_census": set(sets[CAPS[0]]) == census12,
        "unique_parametrization": all(r["n_parametrizations"] == 1
                                      for r in rows),
    }


# ------------------------------------------------------- fast window path
#
# Semantically identical to `period_two_liveness_invariance._evaluate_window`
# (control C2 asserts record-for-record equality on sampled windows); the
# only difference is memoization, which is what makes a 67-chain sweep fit
# inside the 60 s guard.

_MULV = {}      # (a, b) -> c_vertex(a*b)
_COL = {}       # (ops_id, i, vertex) -> column image


def _cvm(a, b):
    k = (a, b)
    v = _MULV.get(k)
    if v is None:
        v = _MULV[k] = c_vertex(quotient_multiply(a, b))
    return v


def _clear_caches():
    _MULV.clear()
    _COL.clear()
    INV._WINDOW_CACHE.clear()


def fast_one_hop(defect, operators, ops_id, op_invs):
    supp = list(defect)
    cands = set()
    for i, gis in enumerate(op_invs):
        for gi in gis:
            for d in supp:
                cands.add((i, _cvm(gi, d)))
    cands = sorted(cands, key=lambda t: (t[0], t[1]))
    row_vertices = set(supp)
    columns = {}
    for (i, v) in cands:
        key = (ops_id, i, v)
        img = _COL.get(key)
        if img is None:
            acc = {}
            for g, gc in operators[i].items():
                dest = _cvm(g, v)
                acc[dest] = acc.get(dest, 0) + gc
            img = _COL[key] = {w: c for w, c in acc.items() if c}
        columns[(i, v)] = img
        row_vertices.update(img)
    row_list = sorted(row_vertices, key=lambda w: (len(w), w))
    ridx = {w: k for k, w in enumerate(row_list)}
    rows = [dict() for _ in row_list]
    for var, img in columns.items():
        for w, cf in img.items():
            rows[ridx[w]][var] = rows[ridx[w]].get(var, 0) + cf
    rhs = {k: -defect.get(w, 0) for k, w in enumerate(row_list)}
    return rows, rhs, len(cands), row_list, columns, cands


def t_exponent(word):
    return sum(1 if x == LV.T else -1 for x in word if abs(x) == LV.T)


def abelian_collapse(defect, row_list, columns, cands):
    """Image of the one-hop system under the module map

        phi : M = Z[Q/<c>] -> Z[x, x^-1],   q<c>  |->  x^(t-exponent of q),

    which is well defined because c has t-exponent 0, and is a map of left
    Z[Q]-modules for the action of Q through Q -> Z, t |-> x, c |-> 1.

    A solution (c_v) of the full system pushes to xi_n = sum_{e(v)=n} c_v of
    the collapsed one, so SOLVABLE(full) => SOLVABLE(collapsed): the
    collapsed system is a NECESSARY condition and its failure is a genuine
    obstruction.  The collapsed matrix has one row per t-exponent, so it is
    the "strictly finer than augmentation" invariant W2D (d.3) asks for --
    augmentation is exactly its specialisation at x = 1.
    """
    exps = sorted({t_exponent(w) for w in row_list})
    ridx = {e: i for i, e in enumerate(exps)}
    reps = {}
    for (i, v) in cands:
        reps.setdefault((i, t_exponent(v)), (i, v))
    crows = [dict() for _ in exps]
    for key, (i, v) in reps.items():
        for w, cf in columns[(i, v)].items():
            r = ridx[t_exponent(w)]
            crows[r][key] = crows[r].get(key, 0) + cf
    crhs = {k: 0 for k in range(len(exps))}
    for w, cf in defect.items():
        crhs[ridx[t_exponent(w)]] -= cf
    return crows, crhs, len(reps)


def eval_window(h0, h1, h2, h3, g, ops_pack, mutate=None,
                abelian=False):
    """One gauge window.  `ops_pack` carries the (h2,h3,g)-only operator
    system so that the 2K+1 squared (k0,k1) windows sharing it reuse both the
    operators and their column images."""
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
    operators, ops_id, op_invs = ops_pack
    if mutate is not None:
        operators, ops_id, op_invs = mutate(operators)
    aug = sum(defect.values())
    rec = {"defect_terms": len(defect),
           "defect_l1": sum(abs(v) for v in defect.values()),
           "defect_augmentation": aug}
    if aug != 0:
        rec["status"] = "DEAD_AUGMENTATION"
        rec["solvable"] = {p: False for p in PRIMES}
        return rec
    rows, rhs, n_vars, row_list, columns, cands = fast_one_hop(
        defect, operators, ops_id, op_invs)
    rec["one_hop_vars"] = n_vars
    rec["solvable"] = {p: bool(LV.solve_mod_p(rows, rhs, int(p)))
                       for p in PRIMES}
    rec["status"] = ("LIVE_AT_ONE_HOP_MOD_235"
                     if all(rec["solvable"].values()) else "UNSOLVABLE")
    if abelian:
        crows, crhs, n_cvars = abelian_collapse(defect, row_list, columns,
                                                cands)
        rec["abelian_vars"] = n_cvars
        rec["abelian_rows"] = len(crows)
        rec["abelian_solvable"] = {
            p: bool(LV.solve_mod_p(crows, crhs, int(p))) for p in PRIMES}
    return rec


_OPS_SERIAL = itertools.count()


def ops_pack_for(R, S, U, h2, h3, g):
    q = lambda w: quotient_reduce(LV.to_tuple(w))
    w = q(smul(g, "t", sinv(g)))
    ops = LV.build_operators_general(q(R), q(S), q(U), q(h2), q(h3), w)
    ops_id = next(_OPS_SERIAL)
    op_invs = [[quotient_inverse(x) for x in op] for op in ops]
    return (ops, ops_id, op_invs)


# ------------------------------------------------------------ gauge slots


def target_conjugators(U, S, how_many=1, radius=G_RADIUS):
    """Terminal conjugators g with cyc(U g t g^-1) = cyc(S), DEDUPED by the
    word w = g t g^-1 they produce.

    Only w enters the operators (L3 = U^-1 - w, L4 = w - 1) and the lift
    target, and C_Q(t) = <t>, so the whole coset g<t> gives one and the same
    w: enumerating raw ball elements would return g, gt, gT... and pretend
    they were three different terminal conjugators.  Deduping by w makes the
    --g-alts axis a real axis.
    """
    out, seen = [], set()
    for g in ball(radius):
        if cyc_form(smul(U, g, "t", sinv(g))) == cyc_form(S):
            w = smul(g, "t", sinv(g))
            if w in seen:
                continue
            seen.add(w)
            out.append(g)
            if len(out) >= how_many:
                break
    return out


def exact_conjugator(base, target):
    """Closed-form conjugator in the free product, no ball search.

    Write base = v rho v^-1 and target = v' rho' v'^-1 with rho, rho'
    cyclically reduced.  They are conjugate iff rho' is a letter-rotation
    rho' = tau*sigma of rho = sigma*tau, and then rho' = sigma^-1 rho sigma,
    so h = v' sigma^-1 v^-1 conjugates base to target.  Asserted, not
    assumed: the returned h is checked by string arithmetic.

    W2e's ball(10) search returns the SHORTEST conjugator but fails outright
    when the coset's shortest element is longer than 10 — which happens for
    15 of the 67 chains at cap 15 (and for none at cap 12, which is why W2e
    never saw it).  A ball miss must be reported as NO_WINDOW, never as a
    dead chain; this formula removes the miss instead.
    """
    v, rho = INV.cyc_decompose(base)
    vp, rhop = INV.cyc_decompose(target)
    if len(rho) != len(rhop) or not rho:
        return None
    for i in range(len(rho)):
        if NF.reduce_w(rho[i:] + rho[:i]) == rhop:
            h = smul(vp, sinv(rho[:i]), sinv(v))
            if smul(h, base, sinv(h)) != target:
                return None
            return h
    return None


def coset_shortest(h, zeta, span=20):
    """Shortest element of the coset h*<zeta> over |k| <= span."""
    best = h
    for k in range(-span, span + 1):
        cand = smul(h, INV.power(zeta, k))
        if len(cand) < len(best):
            best = cand
    return best


_SLOT_STATS = {"ball": 0, "exact_fallback": 0, "coset_agree": 0,
               "coset_checked": 0}


def slot2(base, target, k_max):
    """INV.slot, with the closed-form conjugator as fallback origin.

    When the ball search succeeds the origin is byte-identical to W2e's, so
    the window family is unchanged for every chain W2e could see.
    """
    h_ball = INV.shortest_conjugator(base, target)
    h_exact = exact_conjugator(base, target)
    zeta = INV.centralizer_generator(base)
    if zeta is None:
        return None
    if h_ball is not None:
        _SLOT_STATS["ball"] += 1
        if h_exact is not None:
            _SLOT_STATS["coset_checked"] += 1
            _SLOT_STATS["coset_agree"] += int(
                any(smul(h_exact, INV.power(zeta, k)) == h_ball
                    for k in range(-30, 31)))
        h_b = h_ball
    elif h_exact is not None:
        _SLOT_STATS["exact_fallback"] += 1
        h_b = coset_shortest(h_exact, zeta)
    else:
        return None
    reps = {}
    for k in range(-k_max, k_max + 1):
        h = smul(h_b, INV.power(zeta, k))
        assert smul(h, base, sinv(h)) == target, "slot index broke conjugacy"
        reps[k] = h
    return {"base": base, "target": target, "h_base": h_b, "zeta": zeta,
            "reps": reps}


def chain_slots_g(chain, g, k_max, k1_max):
    """INV.chain_slots with the terminal conjugator supplied explicitly."""
    R, S, U = chain
    s0 = slot2(sinv(QB), smul(sinv(QA), R), k_max)
    s1 = slot2(sinv(R), smul(sinv(QB), S), k1_max)
    s2 = slot2(sinv(S), smul(sinv(R), U), k_max)
    s3 = slot2(S, smul(U, smul(g, "t", sinv(g))), k_max)
    if None in (s0, s1, s2, s3):
        return None
    return {"h0": s0, "h1": s1, "h2": s2, "h3": s3, "g": g}


def sweep_chain(chain, K, K1, g_alts, control_hook=None,
                abelian=False):
    R, S, U = chain
    gs = target_conjugators(U, S, how_many=g_alts)
    if not gs:
        return {"chain": list(chain), "status": "TARGET_CONJUGATOR_NOT_FOUND"}
    ks = range(-K, K + 1)
    k1s = range(-K1, K1 + 1)
    tally = {p: 0 for p in PRIMES}
    ab_tally = {p: 0 for p in PRIMES}
    ab_violations = 0
    live = n_win = 0
    d_terms = []
    per_g = []
    for gi_, g in enumerate(gs):
        sl = chain_slots_g(chain, g, K, K1)
        if sl is None:
            per_g.append({"g": g, "status": "SLOT_NOT_FOUND"})
            continue
        g_live = 0
        for k2 in ks:
            for k3 in ks:
                pack = ops_pack_for(R, S, U, sl["h2"]["reps"][k2],
                                    sl["h3"]["reps"][k3], g)
                for k0 in ks:
                    for k1 in k1s:
                        rec = eval_window(sl["h0"]["reps"][k0],
                                          sl["h1"]["reps"][k1],
                                          sl["h2"]["reps"][k2],
                                          sl["h3"]["reps"][k3], g, pack,
                                          abelian=abelian)
                        n_win += 1
                        if abelian and "abelian_solvable" in rec:
                            for p in PRIMES:
                                ab_tally[p] += int(rec["abelian_solvable"][p])
                                if (rec["solvable"][p]
                                        and not rec["abelian_solvable"][p]):
                                    ab_violations += 1
                        d_terms.append(rec.get("defect_terms", -1))
                        for p in PRIMES:
                            tally[p] += int(rec["solvable"][p])
                        if rec["status"] == "LIVE_AT_ONE_HOP_MOD_235":
                            live += 1
                            g_live += 1
                        if control_hook is not None:
                            control_hook(chain, (k0, k1, k2, k3, gi_),
                                         (sl["h0"]["reps"][k0],
                                          sl["h1"]["reps"][k1],
                                          sl["h2"]["reps"][k2],
                                          sl["h3"]["reps"][k3], g), rec)
        per_g.append({"g": g, "live_windows": g_live})
    return {
        "chain": list(chain),
        "g_used": gs,
        "n_g_axis": len(gs),
        "windows": n_win,
        "live_windows": live,
        "per_prime_windows": {p: tally[p] for p in PRIMES},
        "any": {p: tally[p] > 0 for p in PRIMES} | {"all": live > 0},
        "defect_terms": [min(d_terms), max(d_terms)] if d_terms else [],
        "per_g": per_g,
        "abelian_windows": {p: ab_tally[p] for p in PRIMES} if abelian else {},
        "abelian_violations": ab_violations,
        "status": ("LIVE_AT_ONE_HOP_MOD_235" if live else
                   "NOT_LIVE_AT_TESTED_WINDOWS" if n_win
                   else "NO_WINDOW"),
    }


# ----------------------------------------------------------- the controls


def control_fixed_h_witness():
    rec = LV.analyze(WITNESS, fixed_h=CODEX_H)
    got = (rec["defect_terms"], rec["defect_l1"], rec["defect_augmentation"])
    return {"control": "fixed_h_witness", "defect": list(got),
            "want": [21, 48, 0], "passed": got == (21, 48, 0)}


def control_fast_path(samples):
    """Every sampled window recomputed with the reference path."""
    bad = []
    for chain, idx, hs, rec in samples:
        ref = INV._evaluate_window(*hs)
        keys = ("status", "defect_terms", "defect_l1", "defect_augmentation")
        same = (all(ref.get(k) == rec.get(k) for k in keys)
                and ref["solvable"] == rec["solvable"])
        if not same:
            bad.append({"chain": chain, "k": list(idx),
                        "fast": rec, "reference": ref})
    return {"control": "fast_path_equals_reference",
            "samples": len(samples), "disagreements": len(bad),
            "detail": bad[:3], "passed": not bad and len(samples) > 0}


def control_mutation(K=1):
    """A corrupted operator system MUST flip a solvable verdict."""
    R, S, U = WITNESS
    g = target_conjugators(U, S)[0]
    sl = chain_slots_g(WITNESS, g, K, K)
    found = None
    for k2 in range(-K, K + 1):
        for k3 in range(-K, K + 1):
            pack = ops_pack_for(R, S, U, sl["h2"]["reps"][k2],
                                sl["h3"]["reps"][k3], g)
            for k0 in range(-K, K + 1):
                for k1 in range(-K, K + 1):
                    hs = (sl["h0"]["reps"][k0], sl["h1"]["reps"][k1],
                          sl["h2"]["reps"][k2], sl["h3"]["reps"][k3], g)
                    rec = eval_window(*hs, pack)
                    if rec["status"] == "LIVE_AT_ONE_HOP_MOD_235":
                        found = (hs, pack, rec)
                        break
                if found:
                    break
            if found:
                break
        if found:
            break
    if found is None:
        return {"control": "mutation_flips_verdict",
                "passed": False, "reason": "no live window to corrupt"}
    hs, pack, clean = found

    def _wrap(f):
        def mutate(ops):
            ops2 = f(list(ops))
            return (tuple(ops2), next(_OPS_SERIAL),
                    [[quotient_inverse(x) for x in op] for op in ops2])
        return mutate

    def _drop_L0(ops):                 # delete one term of L0
        d = dict(ops[0])
        d.pop(sorted(d)[0])
        ops[0] = d
        return ops

    def _sign_L3(ops):                 # flip one coefficient's sign in L3
        d = dict(ops[3])
        k = sorted(d)[0]
        d[k] = -d[k]
        ops[3] = d
        return ops

    out = {"control": "mutation_flips_verdict", "clean": clean["solvable"]}
    ok = True
    for name, f in (("drop_term_L0", _drop_L0), ("sign_flip_L3", _sign_L3)):
        dirty = eval_window(*hs, pack, mutate=_wrap(f))
        flipped = clean["solvable"] != dirty["solvable"]
        out[name] = {"mutated": dirty["solvable"], "flipped": flipped}
        ok = ok and flipped
    out["passed"] = ok
    return out


# ---------------------------------------------------------------- report


COORD_NAMES = ("k1", "p1", "k2", "p2", "k3", "p3", "gnorm")
DERIVED_NAMES = ("lenR", "lenS", "lenU", "total_len", "maxlen",
                 "min_defect_terms")


def coords_of(row):
    k1, p1, k2, p2, k3, p3 = row["params"]
    return (k1, p1, k2, p2, k3, p3, len(row["g_gen"]))


def derived_of(row):
    R, S, U = row["chain"]
    return (len(R), len(S), len(U), len(R) + len(S) + len(U),
            row["maxlen"], row.get("min_defect_terms", -1))


def tail_strata(rows):
    """For each coordinate: the largest value carrying a live chain, and the
    dead-only tail above it (an exact predicate over the tested family)."""
    out = {}
    live = [r for r in rows if r["live"]]
    for names, fn in ((COORD_NAMES, coords_of), (DERIVED_NAMES, derived_of)):
        for i, name in enumerate(names):
            lv = sorted({fn(r)[i] for r in live})
            if not lv:
                continue
            hi = lv[-1]
            tail = [r for r in rows if fn(r)[i] > hi]
            out[name] = {
                "live_values": lv,
                "max_live_value": hi,
                "chains_strictly_above": len(tail),
                "all_dead_above": all(not r["live"] for r in tail),
            }
    return out


def determining_sets(rows, max_size=3):
    """Coordinate subsets whose value DETERMINES liveness on this family.

    A subset determines liveness iff no value of the coordinate tuple carries
    both a live and a dead chain.  Reported as an exact predicate over the
    tested data, not a theorem.
    """
    idx = range(len(COORD_NAMES))
    out = []
    for size in range(1, max_size + 1):
        for sub in itertools.combinations(idx, size):
            buckets = {}
            for r in rows:
                c = coords_of(r)
                key = tuple(c[i] for i in sub)
                buckets.setdefault(key, set()).add(r["live"])
            if all(len(v) == 1 for v in buckets.values()):
                out.append({
                    "coords": [COORD_NAMES[i] for i in sub],
                    "n_values": len(buckets),
                    "n_chains": len(rows),
                    # a determining set with ~one value per chain is vacuous:
                    # it merely re-indexes the family
                    "vacuous": len(buckets) > len(rows) // 2,
                    "live_values": sorted(
                        [list(k) for k, v in buckets.items() if True in v]),
                })
        if out:
            break        # report the smallest determining size only
    return out


def coordinate_table(rows):
    tab = {}
    for names, fn in ((COORD_NAMES, coords_of), (DERIVED_NAMES, derived_of)):
        for i, name in enumerate(names):
            d = {}
            for r in rows:
                v = fn(r)[i]
                e = d.setdefault(str(v), {"n": 0, "live": 0})
                e["n"] += 1
                e["live"] += int(r["live"])
            tab[name] = d
    return tab


def build_report(state, chain_rows):
    by_chain = {tuple(v["chain"]): v for v in state["results"].values()}
    rows = []
    no_window = []
    for cr in chain_rows:
        ch = tuple(cr["chain"])
        sw = by_chain.get(ch)
        if sw is None:
            continue
        if sw["status"] == "NO_WINDOW" or not sw.get("windows"):
            no_window.append(cr["chain"])
            continue
        rows.append(dict(cr, live=sw["any"]["all"],
                         live_p={p: sw["any"][p] for p in PRIMES},
                         live_windows=sw["live_windows"],
                         windows=sw["windows"],
                         per_prime_windows=sw["per_prime_windows"],
                         min_defect_terms=(sw["defect_terms"] or [-1])[0],
                         max_defect_terms=(sw["defect_terms"] or [-1, -1])[1],
                         status=sw["status"]))
    cap_table = {}
    for cap in CAPS:
        sel = [r for r in rows if r["maxlen"] <= cap]
        if not sel:
            continue
        cap_table[str(cap)] = {
            "chains": len(sel),
            "live_all": sum(1 for r in sel if r["live"]),
            "live_frac": round(sum(1 for r in sel if r["live"]) / len(sel), 4),
            "live_per_prime": {p: sum(1 for r in sel if r["live_p"][p])
                               for p in PRIMES},
            "live_frac_per_prime": {
                p: round(sum(1 for r in sel if r["live_p"][p]) / len(sel), 4)
                for p in PRIMES},
        }
    dead = [r for r in rows if not r["live"]]
    live = [r for r in rows if r["live"]]
    return {
        "n_chains_swept": len(rows),
        "n_chains_no_window": len(no_window),
        "no_window_chains": no_window,
        "cap_table": cap_table,
        "determining_sets": determining_sets(rows, max_size=4),
        "tail_strata": tail_strata(rows),
        "coordinate_table": coordinate_table(rows),
        "live_chains": [{"chain": r["chain"], "params": r["params"],
                         "g": r["g_gen"], "live_windows": r["live_windows"],
                         "windows": r["windows"],
                         "per_prime_windows": r["per_prime_windows"]}
                        for r in live],
        "dead_param_projection": {
            name: sorted({coords_of(r)[i] for r in dead})
            for i, name in enumerate(COORD_NAMES)},
        "live_param_projection": {
            name: sorted({coords_of(r)[i] for r in live})
            for i, name in enumerate(COORD_NAMES)},
        "per_prime_disagreements": [
            {"chain": r["chain"], "live_p": r["live_p"]}
            for r in rows if len(set(r["live_p"].values())) > 1],
    }


# ------------------------------------------------------------------ main


def load_state(path, meta):
    if path.exists():
        st = json.loads(path.read_text())
        if st.get("meta") != meta:
            raise SystemExit(
                f"state file {path} was written with meta {st.get('meta')} "
                f"!= {meta}; use a different --state path")
        return st
    return {"meta": meta, "results": {}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("chains", "sweep", "report",
                                       "controls"), default="sweep")
    ap.add_argument("--k", type=int, default=1)
    ap.add_argument("--k1", type=int, default=-1)
    ap.add_argument("--g-alts", type=int, default=1)
    ap.add_argument("--cap", type=int, default=15)
    ap.add_argument("--chains", type=str, default="")
    ap.add_argument("--only-g", type=str, default="",
                    help="comma-separated terminal conjugators g to keep "
                         "(use _ for the empty word), e.g. Tc,cTTc")
    ap.add_argument("--only-dead", type=str, default="",
                    help="sweep only chains NOT live in this state file")
    ap.add_argument("--state", type=str, default="")
    ap.add_argument("--json", type=str, default="")
    ap.add_argument("--budget-seconds", type=float, default=45.0)
    ap.add_argument("--control-samples", type=int, default=4)
    ap.add_argument("--abelian", action="store_true",
                    help="also evaluate the t-exponent (Z[x,x^-1]) image of "
                         "the one-hop system: a necessary condition, so its "
                         "failure is a genuine obstruction")
    args = ap.parse_args()
    K = args.k
    K1 = args.k if args.k1 < 0 else args.k1
    t_start = time.time()

    c1 = control_fixed_h_witness()
    print(json.dumps(c1))
    if not c1["passed"]:
        return 2

    chain_rows, chain_meta = chain_table()
    print(json.dumps({"control": "chain_table", **chain_meta}))
    if not (chain_meta["caps_nested"]
            and chain_meta["cap12_equals_committed_census"]):
        print("CONTROL FAILURE: cap nesting or census agreement broken")
        return 2

    if args.mode == "chains":
        out = {"schema": "acsolverx.w2f.chains.v1",
               "meta": chain_meta, "chains": chain_rows}
        if args.json:
            Path(args.json).write_text(json.dumps(out, indent=1))
        print(json.dumps({"mode": "chains", "n": len(chain_rows),
                          "written": args.json}))
        return 0

    if args.mode == "controls":
        cm = control_mutation(K=1)
        print(json.dumps(cm))
        return 0 if cm["passed"] else 2

    if args.mode == "report":
        state = json.loads(Path(args.state).read_text())
        rep = build_report(state, chain_rows)
        rep["schema"] = "acsolverx.w2f.report.v1"
        rep["window_meta"] = state["meta"]
        wit = [r for r in rep["live_chains"]
               if tuple(r["chain"]) == WITNESS]
        rep["control_witness_live"] = bool(wit)
        rep["nonclaims"] = [
            "NOT_LIVE_AT_TESTED_WINDOWS is inconclusive at chain level",
            "K, GPAD=5, ball(10), cap are ceilings and can only under-report",
            "no claim about the free group class, AK(3), stable AC, or AC",
        ]
        if args.json:
            Path(args.json).write_text(json.dumps(rep, indent=1))
        print(json.dumps({k: rep[k] for k in
                          ("n_chains_swept", "n_chains_no_window",
                           "cap_table", "determining_sets",
                           "control_witness_live")}))
        print(json.dumps({"tail_strata": rep["tail_strata"]}))
        print(json.dumps({"coordinate_table": rep["coordinate_table"]}))
        print(json.dumps({"dead_param_projection":
                          rep["dead_param_projection"],
                          "live_param_projection":
                          rep["live_param_projection"]}))
        print(json.dumps({"per_prime_disagreements":
                          rep["per_prime_disagreements"]}))
        if not rep["control_witness_live"]:
            print("CONTROL FAILURE: witness chain is not live in the sweep")
            return 2
        return 0

    # ------------------------------------------------------------- sweep
    meta = {"K": K, "K1": K1, "g_alts": args.g_alts, "cap": args.cap,
            "abelian": bool(args.abelian)}
    if not args.state:
        raise SystemExit("--mode sweep needs --state")
    st_path = Path(args.state)
    state = load_state(st_path, meta)

    todo = [r for r in chain_rows if r["maxlen"] <= args.cap]
    if args.only_dead:
        prev = json.loads(Path(args.only_dead).read_text())
        deadset = {tuple(v["chain"]) for v in prev["results"].values()
                   if not v["any"]["all"]}
        todo = [r for r in todo if tuple(r["chain"]) in deadset]
    if args.only_g:
        keep = {("" if x == "_" else x) for x in args.only_g.split(",")}
        todo = [r for r in todo if r["g_gen"] in keep]
    if args.chains:
        lo, hi = args.chains.split(":")
        todo = todo[int(lo) if lo else 0: int(hi) if hi else len(todo)]
    pending = [r for r in todo
               if "|".join(r["chain"]) not in state["results"]]

    samples = []

    def hook(chain, idx, hs, rec):
        if len(samples) < args.control_samples:
            samples.append((list(chain), idx, hs, rec))

    done = 0
    for r in pending:
        if time.time() - t_start > args.budget_seconds:
            break
        _clear_caches()
        sw = sweep_chain(tuple(r["chain"]), K, K1, args.g_alts,
                         control_hook=hook, abelian=args.abelian)
        sw["params"] = r["params"]
        sw["maxlen"] = r["maxlen"]
        state["results"]["|".join(r["chain"])] = sw
        done += 1
        print(json.dumps({"chain": r["chain"], "params": r["params"],
                          "maxlen": r["maxlen"],
                          "windows": sw.get("windows"),
                          "live_windows": sw.get("live_windows"),
                          "per_prime": sw.get("per_prime_windows"),
                          "status": sw["status"]}))
    st_path.parent.mkdir(parents=True, exist_ok=True)
    st_path.write_text(json.dumps(state))

    c2 = control_fast_path(samples)
    print(json.dumps({k: c2[k] for k in
                      ("control", "samples", "disagreements", "passed")}))
    c3 = control_mutation(K=1)
    print(json.dumps(c3))
    solv = sum(v["live_windows"] for v in state["results"].values())
    tot = sum(v["windows"] for v in state["results"].values()
              if "windows" in v)
    # Dynamic range: BOTH outcomes must be producible in this run.  A
    # deliberately dead-stratum slice has no live window of its own, so the
    # live half may also be supplied by the mutation control's clean
    # (uncorrupted) reference window, which is a real live verdict computed
    # by the same code path.
    live_ref = all(c3.get("clean", {}).values())
    c4 = {"control": "dynamic_range", "live_windows": solv,
          "unsolvable_windows": tot - solv,
          "live_from_mutation_reference": bool(live_ref),
          "passed": (solv > 0 or live_ref) and tot - solv > 0}
    print(json.dumps(c4))
    c5 = {"control": "closed_form_conjugator_agrees_with_ball",
          **_SLOT_STATS,
          "passed": _SLOT_STATS["coset_agree"] == _SLOT_STATS["coset_checked"]}
    print(json.dumps(c5))
    state["slot_stats"] = dict(_SLOT_STATS)
    st_path.write_text(json.dumps(state))
    print(json.dumps({"summary": {
        "mode": "sweep", "meta": meta,
        "chains_done_this_run": done,
        "chains_in_state": len(state["results"]),
        "remaining": len(pending) - done,
        "elapsed_s": round(time.time() - t_start, 1),
        "controls_passed": all(c["passed"] for c in (c1, c2, c3, c4, c5)),
    }}))
    if not all(c["passed"] for c in (c2, c3, c4, c5)):
        print("CONTROL FAILURE: run is void")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
