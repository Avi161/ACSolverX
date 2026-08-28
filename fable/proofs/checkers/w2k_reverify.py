"""W2k: re-run every suspended W2 layer-1 result on the CORRECTED operators.

`corrected_operators.build_operators_exact` supersedes
`period_two_baseline_liveness.build_operators_general` (wrong `L0` column on
the 59 of 67 census chains with `q(h1) != 1`; see W2J_THETA_RESIDUAL.md and
the derivation in `corrected_operators.py`).  This driver reproduces, in
dependency order, each computation that ran through `L0`, with the old and
the new number side by side.

NOTHING EXISTING IS MODIFIED.  The downstream checkers are imported and their
operator SOURCE is rebound at run time (`GS.window_data`, `IL.sigma_terms`),
so every mode below is the published checker's own code path, its own
controls included, fed exact operators.  `--shipped` re-runs the same mode on
the shipped operators for the side-by-side.

THE GROUND TRUTH IS NEVER THE OPERATORS.  Every mode that produces or uses a
layer-1 solution cross-checks it the W2j way: put `n_r = sigma(x_r)`, replay
the recurrence literally in `F(c,t)`, and assert the residual lands in
`[N,N]` (`corrected_operators.verify_solution_literally`).  A solution
verified only by re-applying the operators that produced it is not verified.

MODES
  opcheck    (a) all five columns vs the literal residual, all 67 chains,
             widened probe set; exact / shipped / deliberately re-broken L0.
  theta      (a) the exact builder IS W2j's `exact_operators`, chain by chain.
  sweep      (b.1) W2b/W2f: one-hop liveness, 81 windows x 67 chains, per
             prime, exact vs shipped; the five dead strata re-tallied.
  invariance (b.2) W2e: the aligned class-pair comparison and the corrected
             transformation law.
  omega      (b.3) W2g: d on the 44 finite-index chains, plus which operator
             row supplies d = 1, plus literal re-verification of the lifts.
  inf        (b.4) W2h: the 23 infinite-index chains -- identity control,
             margin law, explicit lifts, literally re-verified.
  d2         (b.5) W2i: d2 and the Xi_Z isomorphism on the corrected image.

EXIT CODES  0 run completed and every control green; 2 a control failed.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
import time
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
sys.path.insert(0, str(HERE))

_ARGV = list(sys.argv)
sys.argv = sys.argv[:1]
import corrected_operators as CO           # noqa: E402
import g_stratum_death as GS               # noqa: E402
import infinite_index_liveness as IL       # noqa: E402
import layer2_d2_invariant as L2           # noqa: E402
sys.argv = _ARGV

PS, LV = GS.PS, GS.LV
lift = CO.lift
OUT = HERE / "out"

PRIMES = (2, 3, 5)
_SHIPPED_WINDOW_DATA = GS.window_data
_SHIPPED_SIGMA_TERMS = IL.sigma_terms


# ------------------------------------------------------ operator rebinding


def _window_h(sl, g, k):
    k0, k1, k2, k3 = k
    return (sl["h0"]["reps"][k0], sl["h1"]["reps"][k1],
            sl["h2"]["reps"][k2], sl["h3"]["reps"][k3], g)


def window_data_exact(chain, g, sl, k):
    """`GS.window_data` with the exact `L0` (the only change)."""
    h = _window_h(sl, g, k)
    fh = [CO.to_tuple(x) for x in h]
    r, s, u, z, tgt = CO.chain_words(h)
    dw = lift.multiply(z, lift.inverse(tgt))
    assert lift.quotient_reduce(dw) == (), "defect not in N"
    return (CO.build_operators_exact(r, s, u, fh[1], fh[2], fh[3], tgt),
            lift.relation_module(dw), h)


def use_exact(on=True):
    """Rebind the operator source of the imported checkers."""
    GS.window_data = window_data_exact if on else _SHIPPED_WINDOW_DATA
    IL.sigma_terms = CO.sigma_terms_exact if on else _SHIPPED_SIGMA_TERMS


class NS(dict):
    __getattr__ = dict.get


def _args_for(**kw):
    base = dict(mode="", radius=6, radii="8,10,12", align=0, resid_rho=0,
                rho=6, k=1, chains="", stratum_only=False, json="",
                index=0, cap_len=6, depth=4, degree=4, control_samples=2,
                zk=2, zn=2, zmax=24, detail=False)
    base.update(kw)
    return NS(base)


def _dump(args, name, summ, rows):
    if not args.json:
        return
    Path(args.json).write_text(json.dumps(
        {"schema": f"acsolverx.w2k.{name}.v1", "exact_operators":
         not args.shipped, "summary": summ, "rows": rows}, indent=1))


def _slice(seq, spec):
    if not spec:
        return seq
    a, b = spec.split(":")
    return seq[int(a or 0):int(b or len(seq))]


# --------------------------------------------------- (a) column validation


def mode_opcheck(args, rows):
    """All five columns against the literal free-group residual."""
    probes = CO.probe_vertices()
    sel = _slice(rows, args.chains)
    out = []
    tot = bad_e = bad_s = bad_b = 0
    ok = True
    for r in sel:
        ch, g = tuple(r["chain"]), r["g_gen"]
        sl = PS.chain_slots_g(ch, g, 0, 0)
        h = _window_h(sl, g, (0, 0, 0, 0))
        ops_e = CO.operators_from_h(h)
        ops_s = CO.operators_from_h_broken(h)
        assert ops_s == _SHIPPED_WINDOW_DATA(ch, g, sl, (0, 0, 0, 0))[0], \
            "broken-L0 control is not the shipped operator"
        n, be, we = CO.validate_columns(h, ops_e, probes)
        _n, bs, ws = CO.validate_columns(h, ops_s, probes)
        tot += n
        bad_e += be
        bad_s += bs
        bad_b += bs
        rec = {"chain": r["chain"], "g": g, "h1": h[1],
               "h1_trivial": lift.quotient_reduce(CO.to_tuple(h[1])) == (),
               "checks": n, "exact_mismatches": be, "exact_wrong": we,
               "shipped_mismatches": bs, "shipped_wrong": ws}
        rec["passed"] = (be == 0
                         and (bs == 0) == rec["h1_trivial"])
        ok = ok and rec["passed"]
        out.append(rec)
        print(json.dumps(rec))
    summ = {"chains": len(out), "probe_vertices": len(probes),
            "checks_per_operator_set": tot,
            "exact_mismatches": bad_e,
            "shipped_mismatches": bad_s,
            "rebroken_L0_mismatches": bad_b,
            "columns_wrong_exact": sorted({i for o in out
                                           for i in o["exact_wrong"]}),
            "columns_wrong_shipped": sorted({i for o in out
                                             for i in o["shipped_wrong"]}),
            "chains_h1_trivial": sum(1 for o in out if o["h1_trivial"]),
            "chains_shipped_L0_wrong": sum(1 for o in out
                                           if 0 in o["shipped_wrong"]),
            "rebroken_control_fires_iff_h1_nontrivial": ok,
            "all_exact_columns_verified": bad_e == 0 and bool(out)}
    print(json.dumps({"summary": summ}))
    _dump(args, "opcheck", summ, out)
    return 0 if (ok and summ["all_exact_columns_verified"]) else 2


def mode_theta(args, rows):
    """W2j reconciliation: its `exact_operators` IS `build_operators_exact`."""
    import theta_residual_evaluator as TR
    sel = _slice(rows, args.chains)
    out, ok = [], True
    same = 0
    for r in sel:
        ch, g = tuple(r["chain"]), r["g_gen"]
        sl = PS.chain_slots_g(ch, g, 0, 0)
        h = _window_h(sl, g, (0, 0, 0, 0))
        a = CO.operators_from_h(h)
        b = TR.exact_operators(h)
        eq = [a[i] == b[i] for i in range(5)]
        same += int(all(eq))
        ok = ok and all(eq)
        out.append({"chain": r["chain"], "g": g,
                    "columns_equal": eq, "identical": all(eq)})
    summ = {"chains": len(out), "identical_to_w2j_exact_operators": same,
            "all_identical": ok and bool(out)}
    print(json.dumps({"summary": summ}))
    _dump(args, "theta", summ, out)
    return 0 if summ["all_identical"] else 2


# -------------------------------------------- (b.1) W2b / W2f liveness sweep


_OPS_ID = itertools.count()


def _window_systems(h, exact):
    """(defect, one-hop rows, rhs) for one window, cached by conjugators."""
    fh = [CO.to_tuple(x) for x in h]
    r, s, u, z, tgt = CO.chain_words(h)
    dw = lift.multiply(z, lift.inverse(tgt))
    if lift.quotient_reduce(dw) != ():
        return None
    defect = lift.relation_module(dw)
    if exact:
        ops = CO.build_operators_exact(r, s, u, fh[1], fh[2], fh[3], tgt)
    else:
        ops = LV.build_operators_general(r, s, u, fh[2], fh[3], tgt)
    return defect, ops


_PACK = {}


def _pack_for(h, exact):
    key = ((h[1] if exact else ""), h[2], h[3], h[4], exact)
    p = _PACK.get(key)
    if p is None:
        _PACK[key] = p = [None, next(_OPS_ID)]
    return p


def _solve_window(h, exact):
    got = _window_systems(h, exact)
    if got is None:
        return None
    defect, ops = got
    if sum(defect.values()) != 0:
        return {"aug": sum(defect.values()),
                "solvable": {p: False for p in PRIMES}}
    p = _pack_for(h, exact)
    if p[0] is None:
        p[0] = [[lift.quotient_inverse(x) for x in op] for op in ops]
    rows, rhs, _n, _rl, _cols, _cands = PS.fast_one_hop(defect, ops, p[1], p[0])
    return {"aug": 0,
            "solvable": {q: bool(LV.solve_mod_p(rows, rhs, q))
                         for q in PRIMES}}


def _resume(args):
    """Rows already computed in `--json` (this driver is sliced+resumable)."""
    if not args.json or not Path(args.json).exists():
        return {}
    try:
        d = json.loads(Path(args.json).read_text())
    except json.JSONDecodeError:
        return {}
    return {tuple(r["chain"]) + (r.get("g", ""),): r for r in d.get("rows", [])}


def mode_sweep(args, rows):
    """W2b/W2f: one-hop liveness over the 81 windows of `K = 1`.

    The OLD column is W2f's own per-chain record (`w2f_sweep_k1.json`), not a
    recomputation -- with a control that recomputes the shipped arm on the
    first `--shipped-control` chains of each slice and requires the published
    per-prime window counts back, exactly.
    """
    K = args.k
    sel = _slice(rows, args.chains)
    ref = _w2f_reference()
    done = _resume(args)
    out, ok = list(done.values()), True
    n_ctl = 0
    t0 = time.time()
    for r in sel:
        ch, g = tuple(r["chain"]), r["g_gen"]
        if ch + (g,) in done:
            continue
        sl = PS.chain_slots_g(ch, g, K, K)
        w2f = ref.get(ch, {})
        rec = {"chain": r["chain"], "g": g, "stratum_S": _strata(r),
               "w2f_live": bool(w2f.get("any", {}).get("all")),
               "w2f_live_windows": w2f.get("live_windows"),
               "w2f_per_prime": w2f.get("per_prime_windows")}
        if sl is None:
            rec["status"] = "NO_SLOT"
            out.append(rec)
            print(json.dumps(rec))
            continue
        arms = [("exact", True)]
        if n_ctl < args.shipped_control:
            arms.append(("shipped", False))
            n_ctl += 1
        for tag, exact in arms:
            n_win, live = 0, 0
            per = {p: 0 for p in PRIMES}
            for k in itertools.product(range(-K, K + 1), repeat=4):
                res = _solve_window(_window_h(sl, g, k), exact)
                if res is None:
                    continue
                n_win += 1
                for p in PRIMES:
                    per[p] += int(res["solvable"][p])
                live += int(all(res["solvable"].values()))
            rec[tag] = {"windows": n_win, "live_windows": live,
                        "per_prime": {str(p): per[p] for p in PRIMES},
                        "chain_live": live > 0}
        if "shipped" in rec and rec["w2f_per_prime"]:
            rec["shipped_reproduces_w2f"] = (
                rec["shipped"]["per_prime"] == rec["w2f_per_prime"]
                and rec["shipped"]["live_windows"] == rec["w2f_live_windows"])
            ok = ok and rec["shipped_reproduces_w2f"]
        rec["verdict_changed"] = (rec["exact"]["chain_live"]
                                  != rec["w2f_live"])
        rec["live_windows_delta"] = (rec["exact"]["live_windows"]
                                     - (rec["w2f_live_windows"] or 0))
        out.append(rec)
        print(json.dumps(rec))
        _dump(args, "sweep", {"partial": True, "chains": len(out)}, out)
        if args.run_seconds and time.time() - t0 > args.run_seconds:
            break
    ex = [o for o in out if "exact" in o]
    dead_str = {s: {"chains": 0, "exact_live": 0, "exact_windows_35": 0}
                for s in ("S1", "S2", "S3", "S4", "S5")}
    for o in ex:
        for s in o["stratum_S"]:
            dead_str[s]["chains"] += 1
            dead_str[s]["exact_live"] += int(o["exact"]["chain_live"])
            dead_str[s]["exact_windows_35"] += (o["exact"]["per_prime"]["3"]
                                                + o["exact"]["per_prime"]["5"])
    summ = {"chains": len(out), "K": K,
            "exact_live_chains": sum(1 for o in ex if o["exact"]["chain_live"]),
            "w2f_live_chains": sum(1 for o in ex if o["w2f_live"]),
            "exact_live_windows": sum(o["exact"]["live_windows"] for o in ex),
            "w2f_live_windows": sum(o["w2f_live_windows"] or 0 for o in ex),
            "exact_per_prime": {str(p): sum(o["exact"]["per_prime"][str(p)]
                                            for o in ex) for p in PRIMES},
            "w2f_per_prime": {str(p): sum((o["w2f_per_prime"] or {}).get(
                str(p), 0) for o in ex) for p in PRIMES},
            "dead_to_live": sum(1 for o in ex if o["verdict_changed"]
                                and o["exact"]["chain_live"]),
            "live_to_dead": sum(1 for o in ex if o["verdict_changed"]
                                and not o["exact"]["chain_live"]),
            "strata": dead_str,
            "shipped_control_runs": sum(1 for o in out if "shipped" in o),
            "shipped_reproduces_w2f": sum(
                1 for o in out if o.get("shipped_reproduces_w2f")),
            "controls_passed": ok}
    print(json.dumps({"summary": summ}))
    _dump(args, "sweep", summ, out)
    return 0 if ok else 2


def mode_abelian(args, rows):
    """W2f section 5: is the `t`-exponent abelianization still inert?

    `phi : M -> Z[x,x^-1]` is a `Z[Q]`-map, so `solvable(full) =>
    solvable(collapsed)` for ANY operators; what changes with the corrected
    `L0` is the collapsed system itself --

        phi(L0) = -( x^{-e(U)} + bridge_x * x^{e(S)+e(h1)} )( x^{e(A)} - x^{e(R)} )

    (the shipped form omitted `e(h1)`).  This re-measures the inertness.
    """
    sel = _slice(rows, args.chains)
    done = _resume(args)
    out, ok = list(done.values()), True
    t0 = time.time()
    for r in sel:
        ch, g = tuple(r["chain"]), r["g_gen"]
        if ch + (g,) in done:
            continue
        sl = PS.chain_slots_g(ch, g, args.k, args.k)
        rec = {"chain": r["chain"], "g": g, "windows": 0,
               "collapsed_solvable": {str(p): 0 for p in PRIMES},
               "full_solvable": 0, "implication_violations": 0}
        if sl is None:
            out.append(rec)
            continue
        for k in itertools.product(range(-args.k, args.k + 1), repeat=4):
            h = _window_h(sl, g, k)
            got = _window_systems(h, not args.shipped)
            if got is None:
                continue
            defect, ops = got
            if sum(defect.values()) != 0:
                continue
            p = _pack_for(h, not args.shipped)
            if p[0] is None:
                p[0] = [[lift.quotient_inverse(x) for x in op] for op in ops]
            rws, rhs, _n, rl, cols, cands = PS.fast_one_hop(
                defect, ops, p[1], p[0])
            crows, crhs, _nc = PS.abelian_collapse(defect, rl, cols, cands)
            rec["windows"] += 1
            full = all(LV.solve_mod_p(rws, rhs, q) for q in PRIMES)
            rec["full_solvable"] += int(full)
            for q in PRIMES:
                c = bool(LV.solve_mod_p(crows, crhs, q))
                rec["collapsed_solvable"][str(q)] += int(c)
                if full and not c:
                    rec["implication_violations"] += 1
        rec["collapsed_inert"] = all(
            rec["collapsed_solvable"][str(q)] == rec["windows"]
            for q in PRIMES)
        ok = ok and rec["implication_violations"] == 0
        out.append(rec)
        print(json.dumps(rec))
        _dump(args, "abelian", {"partial": True, "chains": len(out)}, out)
        if args.run_seconds and time.time() - t0 > args.run_seconds:
            break
    summ = {"chains": len(out),
            "windows": sum(o["windows"] for o in out),
            "collapsed_solvable": {str(p): sum(
                o["collapsed_solvable"][str(p)] for o in out) for p in PRIMES},
            "full_solvable": sum(o["full_solvable"] for o in out),
            "chains_collapsed_inert": sum(1 for o in out
                                          if o.get("collapsed_inert")),
            "implication_violations": sum(o["implication_violations"]
                                          for o in out),
            "controls_passed": ok}
    print(json.dumps({"summary": summ}))
    _dump(args, "abelian", summ, out)
    return 0 if ok else 2


def _w2f_reference():
    p = OUT / "w2f_sweep_k1.json"
    if not p.exists():
        return {}
    sweep = json.loads(p.read_text())
    return {tuple(v["chain"]): v for v in sweep["results"].values()}


def _strata(r):
    """W2f section 4's five dead strata, as predicates on the parameters."""
    par = r.get("params") or [-1] * 6          # (k1, p1, k2, p2, k3, p3)
    k1, _p1, k2, _p2, k3, p3 = par
    g = r["g_gen"]
    out = []
    if k1 >= 6:
        out.append("S1")
    if g not in ("", "TTc"):
        out.append("S2")
    if p3 >= 4:
        out.append("S3")
    if k3 >= 7:
        out.append("S4")
    if k2 >= 7:
        out.append("S5")
    return out


# ------------------------------------------------ (b.2) W2e class invariance


def _q(w):
    return lift.quotient_reduce(CO.to_tuple(w))


def _rmul(op, u):
    out = {}
    for k, a in op.items():
        kk = lift.quotient_multiply(k, u)
        out[kk] = out.get(kk, 0) + a
    return {k: a for k, a in out.items() if a}


def transformation_law_exact(R, S, U, h1, h2, h3, g, gamma, h1p):
    """The corrected law for `S -> gamma S gamma^-1`, `h2,h3 -> h2,h3 gamma^-1`.

    With `bridge' = bridge gamma^-1` and `S' = gamma S gamma^-1`,

        bridge' S' h1'  =  bridge S (gamma^-1 h1')

    so the corrected `L0'` is `L0` with `q(h1)` replaced by
    `q(gamma^-1 h1')` -- member 1 keeps its OWN `h1`, and the alignment
    enters only through that one right factor.  `L1', L2', L3', L4'` are
    unchanged from W2e's law (none of them sees `h1`).
    """
    gi = _q(GS.sinv(gamma) if isinstance(gamma, str) else gamma)
    Sp = GS.smul(gamma, S, GS.sinv(gamma))
    h2p, h3p = GS.smul(h2, GS.sinv(gamma)), GS.smul(h3, GS.sinv(gamma))
    w = _q(GS.smul(g, "t", GS.sinv(g)))
    O0 = CO.build_operators_exact(_q(R), _q(S), _q(U), _q(h1), _q(h2),
                                  _q(h3), w)
    O1 = CO.build_operators_exact(_q(R), _q(Sp), _q(U), _q(h1p), _q(h2p),
                                  _q(h3p), w)
    bridge = lift.add_group_ring(
        lift.group_ring((1, _q(h2))),
        lift.group_ring((1, lift.quotient_multiply(
            lift.quotient_inverse(_q(U)), _q(h3)))))
    d_r = lift.group_ring((1, lift.quotient_reduce(lift.SOURCE_A)),
                          (-1, _q(R)))
    uinv = lift.group_ring((1, lift.quotient_inverse(_q(U))))
    eff = lift.quotient_multiply(gi, _q(h1p))
    pred_L0 = lift.multiply_group_ring(
        lift.add_group_ring(
            uinv,
            lift.multiply_group_ring(
                bridge, lift.group_ring((1, lift.quotient_multiply(
                    _q(S), eff))))),
        d_r)
    pred_L0 = {k: -a for k, a in pred_L0.items()}
    pred_L1 = lift.multiply_group_ring(
        bridge,
        lift.add_group_ring(
            lift.group_ring((1, lift.quotient_multiply(
                gi, lift.quotient_reduce(lift.SOURCE_B)))),
            {k: -a for k, a in _rmul(lift.group_ring((1, _q(S))), gi).items()}))
    # the intertwiner probe: is there a unit u with L_i' = L_i u for all i?
    units = {"1": _q(""), "gamma^-1": gi, "gamma": _q(gamma)}
    inter = {nm: all(O1[i] == _rmul(O0[i], u) for i in range(5))
             for nm, u in units.items()}
    return {
        "L0_prime_matches_law": O1[0] == pred_L0,
        "L1_prime_matches_law": O1[1] == pred_L1,
        "L2_L3_L4_unchanged": [O1[i] == O0[i] for i in (2, 3, 4)],
        "L0_moves": O0[0] != O1[0],
        "L1_moves": O0[1] != O1[1],
        "no_uniform_right_unit_intertwiner": not any(inter.values()),
        "intertwiner_probe": inter,
        "h1_effective_factor_member0": lift.literal(_q(h1)),
        "h1_effective_factor_member1": lift.literal(eff),
        "h1_factor_moves": _q(h1) != eff,
    }


def mode_invariance(args, _rows):
    """W2e: the aligned class-pair window comparison, on exact operators."""
    INV = PS.INV
    census = [tuple(c) for c in json.loads(
        (HERE / "period_two_census_chains.json").read_text())]
    classes = {}
    for ch in census:
        classes.setdefault((ch[0], INV.cyc_form(ch[1]), ch[2]), []).append(ch)
    pairs = [v for v in classes.values() if len(v) >= 2]
    pairs = _slice(pairs, args.chains)
    K = args.k
    out, ok = [], True
    for members in pairs:
        m0, m1 = members[0], members[1]
        gam = INV.gammas_for(m0[1], m1[1], how_many=1)
        if not gam:
            continue
        gamma = gam[0]
        sl0 = INV.chain_slots(m0, K, K)
        sl1 = INV.chain_slots(m1, K, K)
        if sl0 is None or sl1 is None:
            continue
        gi = GS.sinv(gamma)
        h2o = {k: GS.smul(v, gi) for k, v in sl0["h2"]["reps"].items()}
        h3o = {k: GS.smul(v, gi) for k, v in sl0["h3"]["reps"].items()}
        law = transformation_law_exact(
            m0[0], m0[1], m0[2], sl0["h1"]["reps"][0], sl0["h2"]["reps"][0],
            sl0["h3"]["reps"][0], sl0["g"], gamma, sl1["h1"]["reps"][0])
        n = agree = mism = live0 = live1 = 0
        for k in itertools.product(range(-K, K + 1), repeat=4):
            k0, k1, k2, k3 = k
            r0 = _solve_window((sl0["h0"]["reps"][k0], sl0["h1"]["reps"][k1],
                                sl0["h2"]["reps"][k2], sl0["h3"]["reps"][k3],
                                sl0["g"]), not args.shipped)
            r1 = _solve_window((sl1["h0"]["reps"][k0], sl1["h1"]["reps"][k1],
                                h2o[k2], h3o[k3], sl1["g"]), not args.shipped)
            if r0 is None or r1 is None:
                continue
            n += 1
            a = all(r0["solvable"].values())
            b = all(r1["solvable"].values())
            live0 += int(a)
            live1 += int(b)
            agree += int(a == b)
            mism += int(a != b)
        rec = {"member0": list(m0), "member1": list(m1), "gamma": gamma,
               "aligned_windows": n, "agree": agree, "mismatch": mism,
               "member0_live_windows": live0, "member1_live_windows": live1,
               **law}
        rec["passed"] = (law["L0_prime_matches_law"]
                         and law["L1_prime_matches_law"]
                         and all(law["L2_L3_L4_unchanged"])
                         and law["no_uniform_right_unit_intertwiner"])
        ok = ok and rec["passed"]
        out.append(rec)
        print(json.dumps(rec))
    summ = {"class_pairs": len(out),
            "aligned_windows": sum(o["aligned_windows"] for o in out),
            "agree": sum(o["agree"] for o in out),
            "mismatch": sum(o["mismatch"] for o in out),
            "member0_live_windows": sum(o["member0_live_windows"]
                                        for o in out),
            "member1_live_windows": sum(o["member1_live_windows"]
                                        for o in out),
            "pairs_with_mismatch": sum(1 for o in out if o["mismatch"]),
            "transformation_law_verified": all(
                o["L0_prime_matches_law"] and o["L1_prime_matches_law"]
                for o in out),
            "no_uniform_right_unit_intertwiner": all(
                o["no_uniform_right_unit_intertwiner"] for o in out),
            "h1_factor_moves": sum(1 for o in out if o["h1_factor_moves"]),
            "window_level_refutation_survives": any(o["mismatch"]
                                                    for o in out),
            "controls_passed": ok and bool(out)}
    print(json.dumps({"summary": summ}))
    _dump(args, "invariance", summ, out)
    return 0 if summ["controls_passed"] else 2


# --------------------------------------------------------- (b.3) W2g omega


def mode_omega(args, rows):
    """W2g's own `--mode omega`, plus the source of `d` and a literal lift."""
    use_exact(not args.shipped)
    rc = GS.mode_omega(_args_for(mode="omega", k=args.k, chains=args.chains,
                                 stratum_only=args.stratum_only,
                                 json=args.json or ""), rows)
    return rc


def mode_dsource(args, rows):
    """Which operator row supplies `d = 1` -- L0 (h1-sensitive) or L1 (not)?

    `L1 = bridge (B - S)` never sees `h1`, so any chain whose `d = 1` is
    already witnessed by an `L1` row is IMMUNE to the `L0` correction.  This
    mode separates the two, and re-derives `d` from each column alone.
    """
    sel = _slice(rows, args.chains)
    out, ok = [], True
    for r in sel:
        ch, g = tuple(r["chain"]), r["g_gen"]
        ct = GS.CosetTable(GS.gamma_gens(ch, g))
        rec = {"chain": r["chain"], "g": g}
        if not ct.ok:
            rec["gamma_index"] = None
            out.append(rec)
            continue
        sl = PS.chain_slots_g(ch, g, args.k, args.k)
        d_ex = {0: 0, 1: 0}
        d_sh = {0: 0, 1: 0}
        for k2 in range(-args.k, args.k + 1):
            for k3 in range(-args.k, args.k + 1):
                for tag, wd, acc in (("e", window_data_exact, d_ex),
                                     ("s", _SHIPPED_WINDOW_DATA, d_sh)):
                    ops, _dfc, _h = wd(ch, g, sl, (0, 0, k2, k3))
                    for row in GS.omega_row_set(ct, ops):
                        if row[0] in (0, 1):
                            for x in row[1:]:
                                acc[row[0]] = gcd(acc[row[0]], abs(x))
        # h1 also moves L0 -- scan k1 too, at the base (k2,k3)
        d_ex_k1 = 0
        sl1 = PS.chain_slots_g(ch, g, args.k, args.k)
        for k1 in range(-args.k, args.k + 1):
            ops, _dfc, _h = window_data_exact(ch, g, sl1, (0, k1, 0, 0))
            for row in GS.omega_row_set(ct, ops):
                if row[0] == 0:
                    for x in row[1:]:
                        d_ex_k1 = gcd(d_ex_k1, abs(x))
        rec.update({
            "gamma_index": ct.n, "n_omega": ct.n_omega,
            "d_exact_L0": d_ex[0], "d_exact_L1": d_ex[1],
            "d_exact": gcd(d_ex[0], d_ex[1]),
            "d_shipped_L0": d_sh[0], "d_shipped_L1": d_sh[1],
            "d_shipped": gcd(d_sh[0], d_sh[1]),
            "d_exact_L0_over_k1": d_ex_k1,
            "L1_alone_gives_1": d_ex[1] == 1,
            "L0_column_changed": d_ex[0] != d_sh[0],
        })
        rec["d_unchanged"] = rec["d_exact"] == rec["d_shipped"]
        ok = ok and rec["d_exact"] >= 1
        out.append(rec)
        print(json.dumps(rec))
    fin = [o for o in out if o.get("gamma_index")]
    summ = {"chains": len(out), "finite_index": len(fin),
            "d_exact_is_1": sum(1 for o in fin if o["d_exact"] == 1),
            "d_shipped_is_1": sum(1 for o in fin if o["d_shipped"] == 1),
            "d_unchanged": sum(1 for o in fin if o["d_unchanged"]),
            "L1_alone_gives_1": sum(1 for o in fin if o["L1_alone_gives_1"]),
            "L0_column_changed": sum(1 for o in fin if o["L0_column_changed"]),
            "d_exact_values": sorted({o["d_exact"] for o in fin}),
            "d_exact_L0_values": sorted({o["d_exact_L0"] for o in fin}),
            "d_exact_L1_values": sorted({o["d_exact_L1"] for o in fin}),
            "controls_passed": ok and bool(fin)}
    print(json.dumps({"summary": summ}))
    _dump(args, "dsource", summ, out)
    return 0 if summ["controls_passed"] else 2


# --------------------------------------- the literal cross-check of a lift


def mode_literal(args, rows):
    """THE decisive control: layer-1 solutions verified in `F(c,t)` itself.

    For each chain: build the exact operators, solve `D + sum L_i x_i = 0`
    over Z by IL's own hop expansion, then verify the solution the W2j way --
    `n_r = sigma(x_r)`, replay the recurrence, assert `R_can in [N,N]`.
    Also runs the same solve on the SHIPPED operators and shows the literal
    test rejecting it (that is the defect, made visible per chain).
    """
    sel = _slice(rows, args.chains)
    done = _resume(args)
    out, ok = list(done.values()), True
    t0 = time.time()
    for r in sel:
        ch, g = tuple(r["chain"]), r["g_gen"]
        if ch + (g,) in done:
            continue
        sl = PS.chain_slots_g(ch, g, 0, 0)
        h = _window_h(sl, g, (0, 0, 0, 0))
        rec = {"chain": r["chain"], "g": g, "h1": h[1],
               "h1_trivial": _q(h[1]) == ()}
        for tag, wd in (("exact", window_data_exact),
                        ("shipped", _SHIPPED_WINDOW_DATA)):
            ops, defect, _h = wd(ch, g, sl, (0, 0, 0, 0))
            sol = None
            for rho in (1, 2):
                s = IL.solve_module(ops, defect, rho)
                if s["ok"] and s["residual"] == 0:
                    sol = s
                    sol["rho"] = rho
                    break
            if sol is None:
                rec[tag] = {"solved": False}
                continue
            lit_ok, n_rm = CO.verify_solution_literally(h, sol["x"])
            rec[tag] = {"solved": True, "rho": sol["rho"],
                        "x_terms": sol["x_terms"],
                        "operator_residual": sol["residual"],
                        "literal_in_NN": lit_ok,
                        "literal_residual_module_terms": n_rm}
        e, s = rec.get("exact", {}), rec.get("shipped", {})
        rec["exact_solution_literally_verified"] = bool(e.get("literal_in_NN"))
        rec["shipped_solution_literally_rejected"] = bool(
            s.get("solved") and not s.get("literal_in_NN"))
        if e.get("solved"):
            ok = ok and e["literal_in_NN"]
        out.append(rec)
        print(json.dumps(rec))
        _dump(args, "literal", {"partial": True, "chains": len(out)}, out)
        if args.run_seconds and time.time() - t0 > args.run_seconds:
            break
    solved = [o for o in out if o.get("exact", {}).get("solved")]
    shipped_solved = [o for o in out if o.get("shipped", {}).get("solved")]
    summ = {"chains": len(out),
            "exact_solved": len(solved),
            "exact_literally_verified": sum(
                1 for o in solved if o["exact_solution_literally_verified"]),
            "shipped_solved": len(shipped_solved),
            "shipped_literally_verified": sum(
                1 for o in shipped_solved if o["shipped"]["literal_in_NN"]),
            "shipped_literally_rejected": sum(
                1 for o in out if o["shipped_solution_literally_rejected"]),
            "h1_trivial_chains": sum(1 for o in out if o["h1_trivial"]),
            "controls_passed": ok and bool(solved)}
    print(json.dumps({"summary": summ}))
    _dump(args, "literal", summ, out)
    return 0 if summ["controls_passed"] else 2


# ------------------------------------------------ (b.4) W2h infinite index


def mode_inflit(args, rows):
    """W2h's constructive lifts, cross-checked LITERALLY in `F(c,t)`.

    W2h verified `x` by re-applying the same operators that produced it.
    Here the same `seeded_lift` output is re-tested the W2j way: `n_r =
    sigma(x_r)`, replay the recurrence, assert `R_can in [N,N]`.  The
    shipped arm is run alongside so the rejection is visible per chain.
    """
    use_exact(True)
    sel = [r for r in rows if not IL.Completed(
        GS.Folded(GS.gamma_gens(r["chain"], r["g_gen"]))).finite]
    sel = _slice(sel, args.chains)
    done = _resume(args)
    out, ok = list(done.values()), True
    t0 = time.time()
    a = _args_for(rho=args.rho, resid_rho=args.resid_rho, radius=args.radius,
                  radii=args.radii, align=args.align, k=0)
    for r in sel:
        ch, g = tuple(r["chain"]), r["g_gen"]
        if ch + (g,) in done:
            continue
        rec = {"chain": r["chain"], "g": g}
        for tag, wd in (("exact", window_data_exact),
                        ("shipped", _SHIPPED_WINDOW_DATA)):
            use_exact(tag == "exact")
            _ch, _g, cp, _o, _d, _h, sl = IL.chain_setup(r, k=0)
            ops, dfc, h = wd(ch, g, sl, (0, 0, 0, 0))
            sol = IL.seeded_lift(cp, ch, h, ops, dfc, a)
            if not (sol["ok"] and sol["residual"] == 0):
                rec[tag] = {"solved": False}
                continue
            lit, n_rm = CO.verify_solution_literally(h, sol["x"])
            rec[tag] = {"solved": True, "x_terms": sol["x_terms"],
                        "operator_residual": sol["residual"],
                        "literal_in_NN": lit,
                        "literal_residual_module_terms": n_rm}
        use_exact(True)
        rec["h1_trivial"] = _q(_window_h(sl, g, (0, 0, 0, 0))[1]) == ()
        e = rec.get("exact", {})
        if e.get("solved"):
            ok = ok and e["literal_in_NN"]
        out.append(rec)
        print(json.dumps(rec))
        _dump(args, "inflit", {"partial": True, "chains": len(out)}, out)
        if args.run_seconds and time.time() - t0 > args.run_seconds:
            break
    solved = [o for o in out if o.get("exact", {}).get("solved")]
    ship = [o for o in out if o.get("shipped", {}).get("solved")]
    summ = {"chains": len(out), "exact_solved": len(solved),
            "exact_literally_verified": sum(
                1 for o in solved if o["exact"]["literal_in_NN"]),
            "shipped_solved": len(ship),
            "shipped_literally_verified": sum(
                1 for o in ship if o["shipped"]["literal_in_NN"]),
            "shipped_literally_rejected": sum(
                1 for o in ship if not o["shipped"]["literal_in_NN"]),
            "controls_passed": ok and bool(solved)}
    print(json.dumps({"summary": summ}))
    _dump(args, "inflit", summ, out)
    return 0 if summ["controls_passed"] else 2


def mode_inf(args, rows):
    if args.sub == "liftlit":
        return mode_inflit(args, rows)
    use_exact(not args.shipped)
    sub = args.sub or "image"
    a = _args_for(mode=sub, radius=args.radius, radii=args.radii,
                  align=args.align, rho=args.rho, k=args.k,
                  resid_rho=args.resid_rho,
                  chains=args.chains, stratum_only=args.stratum_only,
                  json=args.json or "")
    fn = {"identity": IL.mode_identity, "image": IL.mode_image,
          "lift": IL.mode_lift, "finite": IL.mode_finite}[sub]
    return fn(a, rows)


# ---------------------------------------------------------- (b.5) W2i d2


def mode_d2(args, rows):
    use_exact(not args.shipped)
    sub = args.sub or "uniform"
    a = _args_for(mode=sub, radius=args.radius, radii=args.radii,
                  align=args.align, zk=args.zk, zn=args.zn, zmax=args.zmax,
                  chains=args.chains, stratum_only=args.stratum_only,
                  json=args.json or "")
    fn = {"identity": L2.mode_identity, "d2": L2.mode_d2,
          "uniform": L2.mode_uniform, "inf": L2.mode_inf,
          "probe": L2.mode_probe}[sub]
    return fn(a, rows)


# ------------------------------------------------------------------- main


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True,
                    choices=("opcheck", "theta", "sweep", "invariance",
                             "omega", "dsource", "literal", "inf", "d2",
                             "abelian"))
    ap.add_argument("--sub", type=str, default="")
    ap.add_argument("--chains", type=str, default="")
    ap.add_argument("--k", type=int, default=1)
    ap.add_argument("--rho", type=int, default=6)
    ap.add_argument("--radius", type=int, default=6)
    ap.add_argument("--radii", type=str, default="8,10,12")
    ap.add_argument("--align", type=int, default=0)
    ap.add_argument("--resid-rho", type=int, default=0)
    ap.add_argument("--zk", type=int, default=2)
    ap.add_argument("--zn", type=int, default=2)
    ap.add_argument("--zmax", type=int, default=24)
    ap.add_argument("--stratum-only", action="store_true")
    ap.add_argument("--shipped", action="store_true",
                    help="re-run on the DEFECTIVE operators (comparison arm)")
    ap.add_argument("--run-seconds", type=float, default=0.0)
    ap.add_argument("--shipped-control", type=int, default=2,
                    help="chains per slice whose SHIPPED arm is recomputed "
                         "and required to reproduce W2f exactly")
    ap.add_argument("--json", type=str, default="")
    args = ap.parse_args()

    # control C0: the codex witness certificate, through the exact builder
    ctl = CO.validate_columns(PS.CODEX_H, CO.operators_from_h(PS.CODEX_H))
    _dw, dfc = CO.defect_of(PS.CODEX_H)
    got = (len(dfc), sum(abs(v) for v in dfc.values()), sum(dfc.values()))
    print(json.dumps({"control": "codex_witness_exact_builder",
                      "defect": list(got), "want": [21, 48, 0],
                      "literal_probe_mismatches": ctl[1],
                      "passed": got == (21, 48, 0) and ctl[1] == 0}))
    if got != (21, 48, 0) or ctl[1]:
        return 2

    rows = GS.load_rows()
    return {"opcheck": mode_opcheck, "theta": mode_theta, "sweep": mode_sweep,
            "invariance": mode_invariance, "omega": mode_omega,
            "dsource": mode_dsource, "literal": mode_literal,
            "inf": mode_inf, "d2": mode_d2,
            "abelian": mode_abelian}[args.mode](args, rows)


if __name__ == "__main__":
    sys.exit(main())
