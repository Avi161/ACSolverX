"""Adversarial audit of results/stable_ac/theory/fable/R7_SPELLING_SPACE.md.

Every check re-derives the quantity from the definitions in ``audit_r7_core`` (written
independently of ``neuwirth_rank_n``) and, where a committed tool exists, cross-checks
against it.  Run with a subcommand name; ``all`` runs the cheap ones.
"""

from __future__ import annotations

import itertools
import sys
from collections import Counter

from audit_r7_core import (Dict0, all_spikes, dart_pre2post, restrict, ribbon_def,
                           spike_layout, spike_words, gens_of)
from neuwirth_rank_n import build_link_n, census_size, gamma_N_factorial_n

ALPHA2 = ("x", "X", "y", "Y")


def cyc_canon(seq):
    """Canonical representative of a cyclic order: rotate so the minimum dart leads."""
    i = seq.index(min(seq))
    return seq[i:] + seq[:i]


def orders_key(orders):
    return tuple(sorted((v, cyc_canon(seq)) for v, seq in orders.items()))


def cyc_reduced_words(n, alpha=ALPHA2):
    out = []
    for t in itertools.product(alpha, repeat=n):
        ok = all(t[(i + 1) % n] != t[i].swapcase() for i in range(n)) if n > 1 else True
        if n == 1:
            ok = True
        if ok:
            out.append("".join(t))
    return out


def all_words(n, alpha=ALPHA2):
    return ["".join(t) for t in itertools.product(alpha, repeat=n)]


# ---------------------------------------------------------------------------------
# 0. cross-check my dictionary against the committed one
# ---------------------------------------------------------------------------------


def check_dictionary_agreement(verbose=True):
    fails = []
    checked = 0
    battery = [
        ("xxxYYYY", "xyxYXY"),          # AK(3)
        ("xyXY", "xxy"), ("xyXY", "yYxxy"),
        ("xx", "yy"), ("yYxx", "yy"), ("xyxy", "xy"), ("xyxXxy", "xy"),
        ("x", "y"), ("xy", "y"), ("yxx", "y"), ("yxxy", "y"),
        ("xxYYY", "xyxYXY"),
        ("x", "y", "z"), ("xyz", "zzy", "xXy"),
        ("xxXyxYXY",), ("xXxX",),
    ]
    # plus every pair of total length <= 6 over {x,y}, reduced or not
    for n1 in range(1, 6):
        for n2 in range(1, 7 - n1):
            for w1 in all_words(n1):
                for w2 in all_words(n2):
                    battery.append((w1, w2))
    for words in battery:
        gens = gens_of(words)
        d = Dict0(words, gens)
        ld = build_link_n(words, gens)
        checked += 1
        if d.n_occ != ld.n_occurrences or d.n_darts != ld.n_darts:
            fails.append(("counts", words))
            continue
        if tuple(d.A) != tuple(ld.A) or tuple(d.B) != tuple(ld.B):
            fails.append(("A/B", words))
        if tuple(d.germ) != tuple(ld.germ):
            fails.append(("germ", words))
        if tuple(d.present) != tuple(ld.present_germs):
            fails.append(("present", words))
        if d.L != ld.link_components:
            fails.append(("L", words, d.L, ld.link_components))
        if d.census_size() != census_size(ld, gens):
            fails.append(("census", words))
        if bool(d.loops) != bool(ld.has_loop) or len(d.loops) != len(ld.loop_edges):
            fails.append(("loops", words, len(d.loops), len(ld.loop_edges)))
        if d.census_size() <= 30000:
            mine = d.histogram()
            theirs = gamma_N_factorial_n(words, gens, cap_rotations=200000)
            if theirs["status"] == "OK":
                th = {int(k): v for k, v in theirs["defect_histogram"].items()}
                if mine != th:
                    fails.append(("histogram", words, mine, th))
    if verbose:
        print(f"[0] dictionary agreement: {checked} presentations, {len(fails)} failures")
        for f in fails[:10]:
            print("    FAIL", f)
    return fails


# ---------------------------------------------------------------------------------
# 1. S1 bookkeeping (including the loop count claim S1(6))
# ---------------------------------------------------------------------------------


def check_S1(bases, verbose=True):
    res = Counter()
    fails = []
    loop_counterexamples = []
    for words in bases:
        gens = gens_of(words)
        if len(gens) < 2:
            continue
        pre = Dict0(words, gens)
        for (j, k, u) in all_spikes(words, gens):
            if u.lower() not in gens:
                continue
            post_words = spike_words(words, j, k, u)
            post = Dict0(post_words, gens)
            lay = spike_layout(words, j, k, u)
            s, t, Xg, Yg = lay["s"], lay["t"], lay["X"], lay["Y"]
            res["spikes"] += 1
            # (1) lengths / darts / corners
            if post.n_occ != pre.n_occ + 2 or post.n_darts != pre.n_darts + 4:
                fails.append(("S1.1 counts", words, j, k, u))
            # corner-set identity  A' = A - e_0 + {J1, l, J2}
            m = dart_pre2post(words, j, k, u)
            e0 = frozenset((lay["pre_h_km1"], lay["pre_d_k"]))
            pre_corners = {frozenset((m[a], m[b])) for a, b in pre.corners}
            post_corners = {frozenset(c) for c in post.corners}
            e0_post = frozenset((m[lay["pre_h_km1"]], m[lay["pre_d_k"]]))
            J1 = frozenset((lay["post_h_km1"], lay["d_p"]))
            ell = frozenset((lay["h_p"], lay["d_q"]))
            J2 = frozenset((lay["h_q"], lay["post_d_k"]))
            expect = (pre_corners - {e0_post}) | {J1, ell, J2}
            if expect != post_corners:
                fails.append(("S1.1 corner identity", words, j, k, u))
            if e0_post not in pre_corners:
                fails.append(("S1.1 e0 not a pre corner", words, j, k, u))
            # germ placement of the four new darts
            if not (post.germ[lay["d_p"]] == s and post.germ[lay["h_p"]] == t
                    and post.germ[lay["d_q"]] == t and post.germ[lay["h_q"]] == s):
                fails.append(("S1 germ placement", words, j, k, u))
            # (2) degrees
            for g in range(pre.n_germs):
                want = pre.degree(g) + (2 if g in (s, t) else 0)
                if post.degree(g) != want:
                    fails.append(("S1.2 degree", words, j, k, u, g))
            # (3) present germs / |C|
            if tuple(post.present) != tuple(pre.present):
                fails.append(("S1.3 present", words, j, k, u))
            # (4) components
            delta = 0 if pre.comp_of.get(s) == pre.comp_of.get(Xg) else 1
            if post.L != pre.L - delta:
                fails.append(("S1.4 L", words, j, k, u, pre.L, post.L, delta))
            res[f"delta={delta}"] += 1
            # (5) census ratio
            D = pre.degree(2 * gens.index(u.lower()))
            if post.census_size() != pre.census_size() * D * (D + 1):
                fails.append(("S1.5 census", words, j, k, u))
            # (6) loops
            nl_pre, nl_post = len(pre.loops), len(post.loops)
            res[f"new_loops={nl_post - nl_pre}"] += 1
            if nl_post - nl_pre != 1:
                loop_counterexamples.append((words, j, k, u, post_words,
                                             nl_pre, nl_post))
    if verbose:
        print(f"[1] S1 bookkeeping over {res['spikes']} spikes: {len(fails)} failures")
        print("    delta histogram:", {k: v for k, v in res.items() if k.startswith("delta")})
        print("    NEW LOOPS per spike:",
              {k: v for k, v in sorted(res.items()) if k.startswith("new_loops")})
        print(f"    S1(6) 'exactly one new loop' counterexamples: "
              f"{len(loop_counterexamples)}")
        for c in loop_counterexamples[:6]:
            print("      ", c)
        for f in fails[:10]:
            print("    FAIL", f)
    return fails, loop_counterexamples, res


# ---------------------------------------------------------------------------------
# 2/3. S2 fibration, S4 master formula, S5 pointwise floor
# ---------------------------------------------------------------------------------


def interpolate(words, j, k, u, orders_post):
    """The four-op walk of R7 Theorem S4.  Returns (defs, deltas, info)."""
    lay = spike_layout(words, j, k, u)
    post = Dict0(spike_words(words, j, k, u), gens_of(words))
    pre = Dict0(words, gens_of(words))
    m = dart_pre2post(words, j, k, u)
    e0 = frozenset((m[lay["pre_h_km1"]], m[lay["pre_d_k"]]))
    J1 = frozenset((lay["post_h_km1"], lay["d_p"]))
    ell = frozenset((lay["h_p"], lay["d_q"]))
    J2 = frozenset((lay["h_q"], lay["post_d_k"]))
    full_edges = {frozenset(c) for c in post.corners}
    assert {J1, ell, J2} <= full_edges and e0 not in full_edges

    stages = [
        (full_edges - {J1, ell, J2}) | {e0},   # R0  (= ribbon graph of (P, rho(C')))
        full_edges - {J1, ell, J2},            # R1  (delete e_0)
        (full_edges - {J1, J2}),               # R2  (insert the loop l)
        (full_edges - {J2}),                   # R3  (insert J1)
        full_edges,                            # R4
    ]
    defs = []
    for edges in stages:
        darts = set()
        for e in edges:
            darts |= set(e)
        orders = {}
        for v, seq in orders_post.items():
            kept = tuple(d for d in seq if d in darts)
            if kept:
                orders[v] = kept
        dv, _ = ribbon_def(orders, edges)
        defs.append(dv)
    deltas = [defs[i + 1] - defs[i] for i in range(4)]
    return defs, deltas


def check_fibration_and_master(bases, cap=6000, verbose=True):
    fails = []
    stats = Counter()
    op_hist = [Counter() for _ in range(4)]
    delta_hist = Counter()
    for words in bases:
        gens = gens_of(words)
        if len(gens) < 2:
            continue
        pre = Dict0(words, gens)
        pre_orders = list(pre.compatible_orders())
        pre_set = {orders_key(o) for o in pre_orders}
        for (j, k, u) in all_spikes(words, gens):
            post_words = spike_words(words, j, k, u)
            post = Dict0(post_words, gens)
            if post.census_size() > cap:
                stats["skipped_cap"] += 1
                continue
            D = pre.degree(2 * gens.index(u.lower()))
            fib = Counter()
            for op in post.compatible_orders():
                stats["rotations"] += 1
                # --- S2: rho well defined
                r = restrict(op, words, j, k, u)
                if not pre.is_compatible(r):
                    fails.append(("S2 rho not compatible", words, j, k, u))
                key = orders_key(r)
                if key not in pre_set:
                    fails.append(("S2 rho outside census", words, j, k, u))
                fib[key] += 1
                # --- S4: interpolation
                defs, deltas = interpolate(words, j, k, u, op)
                if defs[0] != pre.defect(r):
                    fails.append(("S4 def(R0)", words, j, k, u, defs[0], pre.defect(r)))
                if defs[4] != post.defect(op):
                    fails.append(("S4 def(R4)", words, j, k, u, defs[4], post.defect(op)))
                for i, dd in enumerate(deltas):
                    op_hist[i][dd] += 1
                if deltas[0] not in (0, -2):
                    fails.append(("S4 op1 range", words, j, k, u, deltas[0]))
                for i in (1, 2, 3):
                    if deltas[i] not in (0, 2):
                        fails.append((f"S4 op{i+1} range", words, j, k, u, deltas[i]))
                # --- S5 pointwise floor
                dd = post.defect(op) - pre.defect(r)
                delta_hist[dd] += 1
                if dd < -2:
                    fails.append(("S5 POINTWISE FLOOR VIOLATED", words, j, k, u, dd))
                # --- face identity |A'C'| - |AC| = 2 - 2delta + 2X^- - 2X^+
                lay = spike_layout(words, j, k, u)
                delta_comp = 0 if pre.comp_of.get(lay["s"]) == pre.comp_of.get(lay["X"]) else 1
                Xminus = 1 if deltas[0] == -2 else 0
                Xplus = sum(1 for i in (1, 2, 3) if deltas[i] == 2)
                nAC_pre = pre.n_occ - len(pre.present) + 2 * pre.L - pre.defect(r)
                nAC_post = post.n_occ - len(post.present) + 2 * post.L - post.defect(op)
                if nAC_post - nAC_pre != 2 - 2 * delta_comp + 2 * Xminus - 2 * Xplus:
                    fails.append(("S4 face identity", words, j, k, u))
            # fibre uniformity + surjectivity
            if set(fib) != pre_set:
                fails.append(("S2 not surjective", words, j, k, u,
                              len(fib), len(pre_set)))
            if any(v != D * (D + 1) for v in fib.values()):
                fails.append(("S2 fibre size", words, j, k, u, set(fib.values()),
                              D * (D + 1)))
            stats["spikes"] += 1
    if verbose:
        print(f"[2/3] fibration+master over {stats['spikes']} spikes, "
              f"{stats['rotations']} post rotations "
              f"({stats['skipped_cap']} spikes skipped at cap): {len(fails)} failures")
        for i, h in enumerate(op_hist):
            print(f"    op{i+1} delta histogram:", dict(sorted(h.items())))
        print("    pointwise defect' - defect(rho) histogram:",
              dict(sorted(delta_hist.items())))
        for f in fails[:10]:
            print("    FAIL", f)
    return fails, stats


# ---------------------------------------------------------------------------------
# 3b. global spike ceiling sweep gamma_N(spike) >= gamma_N - 1
# ---------------------------------------------------------------------------------


def check_ceiling(bases, cap=200000, verbose=True):
    fails = []
    rows = []
    hist = Counter()
    skipped = 0
    for words in bases:
        gens = gens_of(words)
        if len(gens) < 2:
            continue
        pre = Dict0(words, gens)
        if pre.census_size() > cap:
            continue
        gpre = pre.gamma_N()
        for (j, k, u) in all_spikes(words, gens):
            post_words = spike_words(words, j, k, u)
            post = Dict0(post_words, gens)
            if post.census_size() > cap:
                skipped += 1
                continue
            gpost = post.gamma_N()
            hist[gpost - gpre] += 1
            if gpost < gpre - 1:
                fails.append(("CEILING VIOLATED", words, post_words, gpre, gpost))
            if gpost == 0 and gpre > 0:
                fails.append(("SR VIOLATED", words, post_words, gpre, gpost))
            rows.append((words, post_words, gpre, gpost))
    if verbose:
        print(f"[3b] ceiling sweep: {len(rows)} spiked complexes "
              f"({skipped} skipped at cap): {len(fails)} failures")
        print("    delta gamma_N histogram:", dict(sorted(hist.items())))
        for f in fails[:10]:
            print("    FAIL", f)
    return fails, rows, hist


# ---------------------------------------------------------------------------------
# 5. S10 (reduction under unnesting) and Conjectures U / SR
# ---------------------------------------------------------------------------------


def check_S10(bases, cap=20000, verbose=True):
    fails = []
    stats = Counter()
    u_counterexamples = []
    sr_counterexamples = []
    for words in bases:
        gens = gens_of(words)
        if len(gens) < 2:
            continue
        pre = Dict0(words, gens)
        if pre.census_size() > cap:
            continue
        gpre = pre.gamma_N()
        for (j, k, u) in all_spikes(words, gens):
            post_words = spike_words(words, j, k, u)
            post = Dict0(post_words, gens)
            if post.census_size() > cap:
                stats["skipped"] += 1
                continue
            lay = spike_layout(words, j, k, u)
            s = lay["s"]
            d_p, h_q = lay["d_p"], lay["h_q"]
            has_zero = False
            has_unnested_zero = False
            for op in post.compatible_orders():
                if post.defect(op) != 0:
                    continue
                has_zero = True
                seq = op[s]
                i_dp, i_hq = seq.index(d_p), seq.index(h_q)
                M = len(seq)
                unnested = (i_hq - i_dp) % M == 1 or (i_dp - i_hq) % M == 1
                r = restrict(op, words, j, k, u)
                dr = pre.defect(r)
                if unnested:
                    has_unnested_zero = True
                    stats["unnested_zero_rows"] += 1
                    if dr != 0:
                        fails.append(("S10 VIOLATED", words, post_words, dr))
                else:
                    stats["nested_zero_rows"] += 1
                    stats[f"nested_restricts_to_{dr}"] += 1
            if has_zero:
                stats["spiked_gamma0"] += 1
                if not has_unnested_zero:
                    u_counterexamples.append((words, post_words, gpre))
                if gpre != 0:
                    sr_counterexamples.append((words, post_words, gpre))
            stats["spikes"] += 1
    if verbose:
        print(f"[5] S10/U/SR over {stats['spikes']} spikes "
              f"({stats['skipped']} skipped): {len(fails)} S10 violations")
        print("    ", dict(sorted(stats.items())))
        print(f"    Conjecture U counterexamples: {len(u_counterexamples)}")
        for c in u_counterexamples[:6]:
            print("      U-CE", c)
        print(f"    Conjecture SR counterexamples: {len(sr_counterexamples)}")
        for c in sr_counterexamples[:6]:
            print("      SR-CE", c)
        for f in fails[:8]:
            print("    FAIL", f)
    return fails, stats, u_counterexamples, sr_counterexamples


# ---------------------------------------------------------------------------------
# base families
# ---------------------------------------------------------------------------------


def bases_reduced(total):
    out = []
    for n1 in range(1, total):
        n2 = total - n1
        if n2 < 1:
            continue
        for w1 in cyc_reduced_words(n1):
            for w2 in cyc_reduced_words(n2):
                out.append((w1, w2))
    return out


def bases_all(total):
    out = []
    for n1 in range(1, total):
        n2 = total - n1
        if n2 < 1:
            continue
        for w1 in all_words(n1):
            for w2 in all_words(n2):
                out.append((w1, w2))
    return out


def canonical(words):
    """lex-min over relator rotations x inversions x relator permutations."""
    def variants(w):
        vs = []
        for r in range(len(w)):
            rot = w[r:] + w[:r]
            vs.append(rot)
            vs.append("".join(c.swapcase() for c in reversed(rot)))
        return vs
    best = None
    for perm in itertools.permutations(range(len(words))):
        pools = [variants(words[i]) for i in perm]
        for combo in itertools.product(*pools):
            key = tuple(combo)
            if best is None or key < best:
                best = key
    return best


def canon_bases(bases):
    seen = {}
    for b in bases:
        seen.setdefault(canonical(b), b)
    return sorted(seen.values())


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("0", "all"):
        check_dictionary_agreement()
    if which in ("1", "all"):
        check_S1(canon_bases(bases_reduced(4) + bases_reduced(5) + bases_reduced(6)))
    if which in ("2", "all"):
        check_fibration_and_master(canon_bases(bases_reduced(4) + bases_reduced(5)))
    if which == "3":
        check_ceiling(canon_bases(bases_reduced(6) + bases_reduced(7)))
    if which == "5":
        check_S10(canon_bases(bases_reduced(6)))
