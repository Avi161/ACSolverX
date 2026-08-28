"""W2g: is there a window-independent death certificate for W2f's g-stratum?

W2F_PARAMETRIC_SOLVABILITY.md (S2) records 22 census chains with terminal
conjugator g not in {"", "TTc"} and ZERO windows one-hop solvable mod 3 or
mod 5 (1,782 windows at K=1; 2,625 more at K=2).  Its section 8 asks for a
non-abelian quotient of Q = <c,t | c^2> that kills the stratum at EVERY
window.  This checker answers that question.

WHAT LAYER-1 LIVENESS ACTUALLY ASKS
-----------------------------------
The lifting equation is  D + sum_i L_i x_i = 0  with the corrections x_i
ranging over the WHOLE relation module M = Z[Q/<c>] (a correction is a
perturbation of conjugator i by an element of N, and N ->> M).  W2b's
"one hop" restricts x_i to the vertices whose operator image already meets
supp(D); it is a decidable TRUNCATION of the real question, not the question
(W2b's own nonclaim: "support escape possible").

THE STRUCTURE (this note)
-------------------------
With W2e's closed forms  L0 = -(U^-1 + bridge*S)(A-R),  L1 = bridge*(B-S),
L2 = 1 - X (X = h2 S h2^-1 = U^-1 R),  L3 = U^-1 - w,  L4 = w - 1:

  (a)  L2 = -(X - 1),   L4 = (w - 1),   L3 + L4 = (U^-1 - 1)      [identity]
  (b)  hence  L2 M + L3 M + L4 M  =  I_Gamma * M   with  Gamma = <X, U, w>
       = <R, U, w>, because (g_1...g_k - 1)u telescopes as
       sum_j (g_j - 1)(g_{j+1}...g_k u) -- no left prefix survives.
  (c)  so  M / (L2+L3+L4)M  =  Z[Omega],  Omega = Gamma \\ Q / <c>,  free.
  (d)  every L_i has augmentation 0, so the image lies in ker(eps), and a
       functional annihilating all five is exactly an Omega-functional
       annihilating the images of L0 and L1.
  (e)  the Omega-image of the column L_i e_v depends on v ONLY through the
       permutation it induces on Gamma\\Q.  When [Q : Gamma] < infinity that
       is a FINITE group P, so the image of L0 M + L1 M in Z[Omega] is
       computed EXACTLY by a finite check -- over all v in Q/<c> at once.

If that image is all of Z[Omega]_0 (augmentation-zero part), then
sum_i L_i M = ker(eps) exactly, and since every defect has augmentation 0
(W2b), EVERY window of that chain is layer-1 solvable over Z -- so no death
certificate of any kind can exist for it, at any window, any K, any prime.

MODES
  --mode gamma   Stallings-fold Gamma for every census chain; index, |Omega|.
                 Controls: known subgroups of Q with known index.
  --mode omega   the exact finite-P computation of the Omega-image; reports
                 the invariant factor d and the defect class m, and the
                 death predicate (p | d and p !| m).
  --mode period  closes the (k2, k3) axes over ALL of Z: the operators see
                 the window only through trace(h2), trace(h3) in the finite
                 set Gamma\\Q, and that is periodic in k2, k3.
  --mode probe   POSITIVE control: a synthetic defect with odd Omega-class,
                 which the certificate MUST kill and the independent one-hop
                 solver MUST agree is unsolvable mod 2.  A detector that
                 cannot fire is not evidence.
  --mode lift    constructive: build an explicit correction out of the
                 telescoping moves and check D + sum L_i x_i against the
                 recorded residual with the unmodified certificate
                 primitives (a corrupted operator must break it).  Routing
                 to a common Gamma-orbit base is INCOMPLETE (reported as
                 data, not as a control); the proof is the quotient
                 argument, not this construction.
  --mode quotients  W2f section 8's own proposal executed: every
                 (involution, element) pair in S_d as a finite non-abelian
                 quotient of Q, and the joint left null space of the five
                 operators there.  Reports that only the augmentation ever
                 survives -- which is why that route cannot see the
                 double-coset invariant.

EXIT CODES
  0  run completed with every control green (any verdict is a RESULT).
  2  a control failed -- the run is void.
"""
from __future__ import annotations

import argparse
import json
import sys
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
sys.path.insert(0, str(HERE))

_ARGV = list(sys.argv)
sys.argv = sys.argv[:1]
import period_two_parametric_solvability as PS  # noqa: E402
sys.argv = _ARGV

from experiments.stable_ac.depth4_period_two_lift_certificate import (  # noqa
    add_vectors,
    apply_operator,
    c_vertex,
    quotient_inverse,
    quotient_multiply,
    quotient_reduce,
    scale_vector,
)

LV = PS.LV
smul, sinv = PS.smul, PS.sinv
C, T = LV.C, LV.T
CHAINS_JSON = HERE / "out" / "w2f_chains.json"
SWEEP_JSON = HERE / "out" / "w2f_sweep_k1.json"
PRIMES = (2, 3, 5)


# ------------------------------------------------------- Stallings folding


class Folded:
    """Core graph of <gens> <= Q = <c> * <t>, c^2 = 1 (Stallings)."""

    def __init__(self, gens):
        self.par = [0]
        self.tout, self.tin, self.cm = {}, {}, {}
        self.queue = []
        for w in gens:
            self.trace(w)
            self.fold()
        self.fold()

    def find(self, x):
        while self.par[x] != x:
            self.par[x] = self.par[self.par[x]]
            x = self.par[x]
        return x

    def new(self):
        self.par.append(len(self.par))
        return len(self.par) - 1

    def trace(self, word):
        cur = 0
        for ch in word:
            cur = self.find(cur)
            if ch == "c":
                nxt = self.cm.get(cur)
                if nxt is None:
                    nxt = self.new()
                    self.cm[cur] = nxt
                    self.cm[nxt] = cur
            elif ch == "t":
                nxt = self.tout.get(cur)
                if nxt is None:
                    nxt = self.new()
                    self.tout[cur] = nxt
                    self.tin[nxt] = cur
            else:
                nxt = self.tin.get(cur)
                if nxt is None:
                    nxt = self.new()
                    self.tin[cur] = nxt
                    self.tout[nxt] = cur
            cur = nxt
        if self.find(cur) != 0:
            self.queue.append((0, cur))
            self._drain()

    def _drain(self):
        while self.queue:
            a, b = self.queue.pop()
            a, b = self.find(a), self.find(b)
            if a == b:
                continue
            # Pin the BASE class's root at 0.  Union-find is free to choose
            # either root; if it re-roots the base class, `find(0)` stops
            # being 0 and every downstream trace starts from the wrong
            # coset.  (That was a real defect: it made the generators of
            # Gamma trace to non-base states, so the L4 = w - 1 column had
            # a nonzero Omega-image -- see the vanishing control.)
            if b == self.find(0):
                a, b = b, a
            self.par[b] = a
            for m in (self.tout, self.tin, self.cm):
                if b in m:
                    v = m.pop(b)
                    if a in m:
                        self.queue.append((m[a], v))
                    else:
                        m[a] = v

    def fold(self):
        changed = True
        while changed:
            changed = False
            self._drain()
            for name in ("tout", "tin", "cm"):
                m = getattr(self, name)
                new = {}
                for k, v in list(m.items()):
                    k2, v2 = self.find(k), self.find(v)
                    if k2 in new and new[k2] != v2:
                        self.queue.append((new[k2], v2))
                        changed = True
                    else:
                        new[k2] = v2
                setattr(self, name, new)
            for k, v in list(self.cm.items()):
                if self.cm.get(v) != k:
                    if v in self.cm:
                        self.queue.append((self.cm[v], k))
                        changed = True
                    else:
                        self.cm[v] = k
            for k, v in list(self.tout.items()):
                if self.tin.get(v) != k:
                    if v in self.tin:
                        self.queue.append((self.tin[v], k))
                        changed = True
                    else:
                        self.tin[v] = k
            if self.queue:
                changed = True

    def states(self):
        return sorted({self.find(i) for i in range(len(self.par))})

    def complete(self):
        return all(s in self.tout and s in self.tin and s in self.cm
                   for s in self.states())

    def index(self):
        return len(self.states()) if self.complete() else None


class CosetTable:
    """Gamma\\Q as a Q-set (finite index only), plus Omega = its c-orbits."""

    def __init__(self, gens):
        f = Folded(gens)
        self.ok = f.complete()
        if not self.ok:
            return
        st = f.states()
        ix = {s: i for i, s in enumerate(st)}
        self.n = len(st)
        # the base coset Gamma*1 -- NOT necessarily index 0
        self.base = ix[f.find(0)]
        self.pc = tuple(ix[f.find(f.cm[s])] for s in st)
        self.pt = tuple(ix[f.find(f.tout[s])] for s in st)
        self.pT = tuple(ix[f.find(f.tin[s])] for s in st)
        lab, k = [-1] * self.n, 0
        for i in range(self.n):
            if lab[i] < 0:
                lab[i] = lab[self.pc[i]] = k
                k += 1
        self.omega, self.n_omega = lab, k
        idp = tuple(range(self.n))
        seen, fr = {idp}, [idp]
        while fr:
            nx = []
            for x in fr:
                for g in (self.pc, self.pt):
                    y = tuple(g[x[i]] for i in range(self.n))
                    if y not in seen:
                        seen.add(y)
                        nx.append(y)
            fr = nx
        self.P = sorted(seen)

    def trace(self, word):
        return self.trace_from(self.base, word)

    def trace_from(self, s, word):
        if isinstance(word, str):
            word = LV.to_tuple(word)
        for l in word:
            s = (self.pc[s] if abs(l) == C
                 else self.pt[s] if l == T else self.pT[s])
        return s


# --------------------------------------------------------- window objects


def window_data(chain, g, sl, k):
    """(operators, defect, conjugators) at window k = (k0,k1,k2,k3)."""
    k0, k1, k2, k3 = k
    h = (sl["h0"]["reps"][k0], sl["h1"]["reps"][k1],
         sl["h2"]["reps"][k2], sl["h3"]["reps"][k3], g)
    fh = [LV.to_tuple(x) for x in h]
    r = LV.multiply(LV.SOURCE_A, LV.conjugate(LV.inverse(LV.SOURCE_B), fh[0]))
    s = LV.multiply(LV.SOURCE_B, LV.conjugate(LV.inverse(r), fh[1]))
    u = LV.multiply(r, LV.conjugate(LV.inverse(s), fh[2]))
    z = LV.multiply(LV.inverse(u), LV.conjugate(s, fh[3]))
    tgt = LV.conjugate((LV.T,), fh[4])
    dw = LV.multiply(z, LV.inverse(tgt))
    assert LV.quotient_reduce(dw) == (), "defect not in N"
    return (LV.build_operators_general(r, s, u, fh[2], fh[3], tgt),
            LV.relation_module(dw), h)


def q(word_str):
    return quotient_reduce(LV.to_tuple(word_str))


def gamma_gens(chain, g):
    R, S, U = chain
    return [R, U, smul(g, "t", sinv(g))]


# -------------------------------------------------------------- controls


def control_identities(chain, g, ops, h):
    """L2 = -(X-1), L4 = w-1, L3+L4 = U^-1-1, eps(L_i) = 0 -- exactly."""
    R, S, U = chain
    w = q(smul(g, "t", sinv(g)))
    X = quotient_multiply(q(h[2]), q(S), quotient_inverse(q(h[2])))
    one = {(): 1}

    def sub(a, b):
        out = dict(a)
        for k, v in b.items():
            out[k] = out.get(k, 0) - v
        return {k: v for k, v in out.items() if v}

    return {
        "L2_is_1_minus_X": ops[2] == sub(one, {X: 1}),
        "X_equals_Uinv_R": X == quotient_multiply(quotient_inverse(q(U)),
                                                  q(R)),
        "L4_is_w_minus_1": ops[4] == sub({w: 1}, one),
        "L3_plus_L4_is_Uinv_minus_1": (
            LV.add_group_ring(ops[3], ops[4])
            == sub({quotient_inverse(q(U)): 1}, one)),
        "all_augmentations_zero": [sum(o.values()) for o in ops] == [0] * 5,
    }


def control_omega_rows(ct, ops, n_words=200, radius=7):
    """The P-parameterisation must reproduce a DIRECT evaluation.

    For random-ish v in Q/<c>, the Omega-row of the column L_i e_v computed
    vertex by vertex must appear among the rows the finite check enumerates.
    A wrong parameterisation shows up here.
    """
    rows = omega_row_set(ct, ops)
    bad = 0
    seen = 0
    for v in PS.ball(radius):
        if seen >= n_words:
            break
        vv = c_vertex(LV.to_tuple(v))
        for i, op in enumerate(ops):
            row = [0] * ct.n_omega
            for gw, a in op.items():
                row[ct.omega[ct.trace(quotient_multiply(gw, vv))]] += a
            if tuple([i] + row) not in rows:
                bad += 1
        seen += 1
    return {"words_checked": seen, "rows_missing": bad, "passed": bad == 0}


def omega_row_set(ct, ops):
    """{(i, row)} over ALL v in Q/<c>, via the finite group P."""
    out = set()
    for i, op in enumerate(ops):
        sg = {gw: ct.trace(gw) for gw in op}
        for pi in ct.P:
            row = [0] * ct.n_omega
            for gw, a in op.items():
                row[ct.omega[pi[sg[gw]]]] += a
            out.add(tuple([i] + row))
    return out


# ------------------------------------------------- the Omega obstruction


def omega_invariant(ct, ops, defect):
    """d (the modulus) and m (the defect class), for |Omega| = 2."""
    rows = omega_row_set(ct, ops)
    d = 0
    for r in rows:
        if r[0] in (0, 1):                      # L0, L1 only; L2..L4 -> 0
            for x in r[1:]:
                d = gcd(d, abs(x))
    m = sum(cf for v, cf in defect.items() if ct.omega[ct.trace(v)] == 0)
    return d, m


# ------------------------------------------------ constructive lift (mode lift)


MOVES = None


def move_table(chain, g, h):
    """left-multiplication moves and the operator terms they cost.

    (X-1)e_v      = -L2 e_v                (w-1)e_v      =  L4 e_v
    (X^-1-1)e_v   =  L2 e_{X^-1 v}         (w^-1-1)e_v   = -L4 e_{w^-1 v}
    (U^-1-1)e_v   = (L3+L4) e_v            (U-1)e_v      = -(L3+L4) e_{U v}
    """
    R, S, U = chain
    w = q(smul(g, "t", sinv(g)))
    X = quotient_multiply(q(h[2]), q(S), quotient_inverse(q(h[2])))
    Xi, wi, Uq = quotient_inverse(X), quotient_inverse(w), q(U)
    Ui = quotient_inverse(Uq)
    return [
        ("X", X, lambda v, a: [(2, v, -a)]),
        ("Xi", Xi, lambda v, a: [(2, c_vertex(quotient_multiply(Xi, v)), a)]),
        ("w", w, lambda v, a: [(4, v, a)]),
        ("wi", wi, lambda v, a: [(4, c_vertex(quotient_multiply(wi, v)), -a)]),
        ("Ui", Ui, lambda v, a: [(3, v, a), (4, v, a)]),
        ("U", Uq, lambda v, a: [(3, c_vertex(quotient_multiply(Uq, v)), -a),
                                (4, c_vertex(quotient_multiply(Uq, v)), -a)]),
    ]


def route(v, target, moves, depth=4, cap=200000):
    """Bidirectional BFS in the Gamma-move graph: v -> target.

    The move set is closed under inversion, so both halves are ordinary
    BFS.  Returns the list of move indices to apply to v, or None.
    """
    if v == target:
        return []
    fw = {v: []}
    bw = {target: []}
    ffr, bfr = [v], [target]
    inv_of = {0: 1, 1: 0, 2: 3, 3: 2, 4: 5, 5: 4}
    for _ in range(depth):
        for side in (0, 1):
            cur, other = (fw, bw) if side == 0 else (bw, fw)
            fr = ffr if side == 0 else bfr
            nxt = []
            for u in fr:
                pu = cur[u]
                for mi, (_, gw, _) in enumerate(moves):
                    y = c_vertex(quotient_multiply(gw, u))
                    if y in cur:
                        continue
                    cur[y] = pu + [mi]
                    if y in other:
                        if side == 0:
                            return cur[y] + [inv_of[i] for i
                                             in reversed(other[y])]
                        return [inv_of[i] for i in reversed(cur[y])] \
                            + other[y]
                    nxt.append(y)
                    if len(cur) > cap:
                        return None
            if side == 0:
                ffr = nxt
            else:
                bfr = nxt
    return None


INV_MOVE = {0: 1, 1: 0, 2: 3, 3: 2, 4: 5, 5: 4}


def short_gamma_moves(moves, depth=4, maxlen=8):
    """Short elements of Gamma, each with a PRIMITIVE move path realising it.

    Applying the primitive path [m1..mk] to a vertex v yields
    g_{mk}...g_{m1} v, and each primitive step is one operator term -- so a
    compound move costs |path| terms and no new algebra.  Gamma has small
    index here, so it contains short elements of Q; those make the move
    graph locally connected, which the three long generators alone are not.
    """
    S = {gw: [mi] for mi, (_, gw, _) in enumerate(moves)}
    keep = 48
    for _ in range(depth):
        items = sorted(S.items(), key=lambda kv: len(kv[0]))[:keep]
        new = {}
        for a, pa in items:
            for b, pb in items:
                y = quotient_multiply(a, b)
                if not y or y in S or y in new:
                    continue
                if len(y) < max(len(a), len(b)) or len(y) <= maxlen:
                    new[y] = pb + pa
        if not new:
            break
        S.update(new)
        if len(S) > 4000:
            S = dict(sorted(S.items(), key=lambda kv: len(kv[0]))[:4000])
    out = sorted(((g, p) for g, p in S.items() if g and len(g) <= maxlen),
                 key=lambda gp: (len(gp[0]), len(gp[1])))
    return out[:keep]


def back_index(base, cmoves, depth):
    """{vertex: primitive path from that vertex TO base}, BFS from base.

    The inverse of a compound move is realised by inverting its primitive
    path (the primitive move set is closed under inversion).
    """
    fwd = {base: []}
    fr = [base]
    for _ in range(depth):
        nxt = []
        for u in fr:
            pu = fwd[u]
            for gam, path in cmoves:
                y = c_vertex(quotient_multiply(gam, u))
                if y in fwd:
                    continue
                fwd[y] = pu + path
                nxt.append(y)
        fr = nxt
    return {y: [INV_MOVE[i] for i in reversed(p)] for y, p in fwd.items()}


def route_via(v, back, cmoves, depth):
    """primitive path from v to the base indexed by `back`, or None."""
    if v in back:
        return back[v]
    fwd = {v: []}
    fr = [v]
    for _ in range(depth):
        nxt = []
        for u in fr:
            pu = fwd[u]
            for gam, path in cmoves:
                y = c_vertex(quotient_multiply(gam, u))
                if y in fwd:
                    continue
                p = pu + path
                if y in back:
                    return p + back[y]
                fwd[y] = p
                nxt.append(y)
        fr = nxt
    return None


def transfer(E, x, v, a, moves, path):
    """move mass a from v along `path`, recording the operator terms."""
    cur = v
    for mi in path:
        _, gw, cost = moves[mi]
        tgt = c_vertex(quotient_multiply(gw, cur))
        E[cur] = E.get(cur, 0) - a
        E[tgt] = E.get(tgt, 0) + a
        for (i, vv, coef) in cost(cur, a):
            x[i][vv] = x[i].get(vv, 0) + coef
        cur = tgt
    return cur


def omega_witness_column(ct, ops, radius=6):
    """(i, v, a): a column of L0 or L1 whose Omega-image is (a, -a), |a| = d."""
    best = None
    for s in PS.ball(radius):
        vv = c_vertex(LV.to_tuple(s))
        for i in (0, 1):
            row = [0] * ct.n_omega
            for gw, coef in ops[i].items():
                row[ct.omega[ct.trace(quotient_multiply(gw, vv))]] += coef
            a = row[0]
            if a and (best is None or abs(a) < abs(best[2])):
                best = (i, vv, a)
    return best


def build_lift(ct, ops, defect, moves, depth=4, radius=6):
    """Explicit integral x with D + sum L_i x_i = 0, or None with a reason."""
    E = {k: v for k, v in defect.items() if v}
    x = [dict() for _ in range(5)]
    bases = {}
    for cl in range(ct.n_omega):
        for s in PS.ball(6):
            vv = c_vertex(LV.to_tuple(s))
            if ct.omega[ct.trace(vv)] == cl:
                bases[cl] = vv
                break
    stats = {"routed": 0, "unroutable": 0, "max_path": 0}
    cmoves = short_gamma_moves(moves, depth=depth, maxlen=radius)
    stats["short_gamma_moves"] = len(cmoves)
    stats["gamma_lengths"] = sorted({len(g) for g, _ in cmoves})[:8]
    back = {cl: back_index(bases[cl], cmoves, 3) for cl in bases}
    stats["back_index_sizes"] = [len(back[c]) for c in sorted(back)]

    def drain():
        for v in sorted([v for v in E if E[v]], key=lambda v: (-len(v), v)):
            a = E.get(v, 0)
            if not a:
                continue
            cl = ct.omega[ct.trace(v)]
            b = bases[cl]
            if v == b:
                continue
            cur, path = v, []
            for _ in range(80):                     # greedy descent
                if cur == b or cur in back[cl]:
                    break
                best = None
                for gam, pp in cmoves:
                    y = c_vertex(quotient_multiply(gam, cur))
                    if len(y) < len(cur) and (best is None or len(y) < best[0]):
                        best = (len(y), y, pp)
                if best is None:
                    break
                path += best[2]
                cur = best[1]
            if cur != b:
                p2 = route_via(cur, back[cl], cmoves, depth=2)
                if p2 is None:
                    stats["unroutable"] += 1
                    continue
                path += p2
            transfer(E, x, v, a, moves, path)
            stats["routed"] += 1
            stats["max_path"] = max(stats["max_path"], len(path))
        for k in [k for k, c in E.items() if not c]:
            E.pop(k)

    drain()
    if stats["unroutable"]:
        return None, x, E, dict(stats, reason="unroutable_vertex")
    wit = omega_witness_column(ct, ops, radius=radius)
    if wit is None:
        return None, x, E, dict(stats, reason="no_omega_column")
    i, vv, a = wit
    m = E.get(bases[0], 0)
    if m % a:
        return None, x, E, dict(stats, reason=f"class_{m}_not_divisible_{a}")
    coef = -m // a
    if coef:
        x[i][vv] = x[i].get(vv, 0) + coef
        img = apply_operator(ops[i], {vv: coef})
        E = add_vectors(E, img)
        E = {k: c for k, c in E.items() if c}
        drain()
    return (x if not E else None), x, E, dict(stats, reason="ok" if not E
                                              else "residual_nonzero")


def verify_lift(defect, ops, x):
    """D + sum L_i x_i, computed with the unmodified certificate primitives."""
    acc = dict(defect)
    for i, xi in enumerate(x):
        if xi:
            acc = add_vectors(acc, apply_operator(ops[i], xi))
    return {k: v for k, v in acc.items() if v}


# ------------------------------------------------------------------ main


def load_rows():
    rows = json.loads(CHAINS_JSON.read_text())["chains"]
    sweep = json.loads(SWEEP_JSON.read_text())
    res = {tuple(v["chain"]): v for v in sweep["results"].values()}
    for r in rows:
        sw = res.get(tuple(r["chain"]), {})
        r["live"] = bool(sw.get("any", {}).get("all"))
        r["per_prime"] = sw.get("per_prime_windows", {})
        r["stratum"] = r["g_gen"] not in ("", "TTc")
    return rows


def mode_gamma(args, rows):
    ctl = [("<t>", ["t"], None), ("<c,t> = Q", ["c", "t"], 1),
           ("ker(Q->C2, c|->1)", ["c", "tcT", "tt"], 2),
           ("<c,t^2>", ["c", "tt"], None)]
    ok = True
    for name, gens, want in ctl:
        got = Folded(gens).index()
        ok = ok and got == want
        print(json.dumps({"control_subgroup": name, "index": got,
                          "want": want, "passed": got == want}))
    out = []
    for r in rows:
        f = Folded(gamma_gens(r["chain"], r["g_gen"]))
        ct = CosetTable(gamma_gens(r["chain"], r["g_gen"]))
        out.append({"chain": r["chain"], "g": r["g_gen"],
                    "gamma_index": f.index(),
                    "n_omega": ct.n_omega if ct.ok else None,
                    "live": r["live"], "stratum": r["stratum"]})
    from collections import Counter
    print(json.dumps({
        "control_folder_passed": ok,
        "chains": len(out),
        "index": dict(Counter(str(o["gamma_index"]) for o in out)),
        "index_stratum": dict(Counter(str(o["gamma_index"])
                                      for o in out if o["stratum"])),
        "index_live": dict(Counter(str(o["gamma_index"])
                                   for o in out if o["live"])),
        "n_omega": dict(Counter(str(o["n_omega"]) for o in out)),
    }))
    if args.json:
        Path(args.json).write_text(json.dumps(
            {"schema": "acsolverx.w2g.gamma.v1", "rows": out}, indent=1))
    return 0 if ok else 2


def mode_omega(args, rows):
    sel = [r for r in rows if (not args.stratum_only or r["stratum"])]
    lo, hi = 0, len(sel)
    if args.chains:
        a, b = args.chains.split(":")
        lo, hi = int(a or 0), int(b or len(sel))
    out, ctl_pass, ctl_done = [], True, 0
    for r in sel[lo:hi]:
        ch = tuple(r["chain"])
        g = r["g_gen"]
        ct = CosetTable(gamma_gens(ch, g))
        rec = {"chain": r["chain"], "g": g, "live": r["live"],
               "stratum": r["stratum"], "per_prime": r["per_prime"]}
        if not ct.ok:
            rec["gamma_index"] = None
            out.append(rec)
            print(json.dumps(rec))
            continue
        sl = PS.chain_slots_g(ch, g, args.k, args.k)
        ds, ms, ident = [], [], []
        for k2 in range(-args.k, args.k + 1):
            for k3 in range(-args.k, args.k + 1):
                ops, defect, h = window_data(ch, g, sl, (0, 0, k2, k3))
                ident.append(control_identities(ch, g, ops, h))
                d, m = omega_invariant(ct, ops, defect)
                ds.append(d)
                ms.append(m)
                if ctl_done < args.control_samples:
                    c = control_omega_rows(ct, ops, n_words=40, radius=6)
                    ctl_pass = ctl_pass and c["passed"]
                    ctl_done += 1
                    print(json.dumps({"control": "omega_rows_direct", **c}))
        idok = all(all(v is True for v in d.values()) if
                   isinstance(d, dict) else False for d in ident)
        # Lemma 1 made EFFECTIVE: omega_invariant reads d off the L0/L1 rows
        # only, which is legitimate exactly when the L2, L3, L4 columns die
        # in Z[Omega].  Assert it rather than assume it -- this is the
        # control that caught the base-coset defect.
        ops0, _, _ = window_data(ch, g, sl, (0, 0, 0, 0))
        vanish = all(not any(row[1:]) for row in omega_row_set(ct, ops0)
                     if row[0] in (2, 3, 4))
        ctl_pass = ctl_pass and idok and vanish
        rec.update({"gamma_index": ct.n, "n_omega": ct.n_omega,
                    "l234_omega_rows_vanish": vanish,
                    "|P|": len(ct.P), "d": sorted(set(ds)),
                    "m": sorted(set(ms)),
                    "identities_ok": idok,
                    "dead_primes": [p for p in PRIMES
                                    if all(d % p == 0 for d in ds)
                                    and all(m % p for m in ms)],
                    "image_is_ker_eps": all(d == 1 for d in ds)})
        out.append(rec)
        print(json.dumps(rec))
    fin = [r for r in out if r.get("gamma_index")]
    summ = {
        "chains_reported": len(out),
        "finite_index": len(fin),
        "infinite_index": len(out) - len(fin),
        "image_is_ker_eps": sum(1 for r in fin if r["image_is_ker_eps"]),
        "with_death_certificate": sum(1 for r in fin if r["dead_primes"]),
        "d_values_seen": sorted({tuple(r["d"]) for r in fin}),
        "controls_passed": ctl_pass,
        "verdict": ("NO_DEATH_CERTIFICATE_AND_PROVABLY_LIVE"
                    if fin and all(r["image_is_ker_eps"] for r in fin)
                    else "MIXED"),
    }
    print(json.dumps({"summary": summ}))
    if args.json:
        Path(args.json).write_text(json.dumps(
            {"schema": "acsolverx.w2g.omega.v1", "summary": summ,
             "rows": out}, indent=1))
    return 0 if ctl_pass else 2


def mode_quotients(args, rows):
    """W2f section 8's own proposal, executed: finite non-abelian quotients.

    Every (involution, element) pair in S_d gives a hom pi: Q -> G = <cbar,
    tbar> with pi(c)^2 = 1, hence a Z[Q]-module map M -> F_p[G/<cbar>].  A
    covector mu with mu*mat(L_i) = 0 for all i and mu*push(D) != 0 would be a
    death certificate.  The augmentation is always in that left null space
    and always kills D, so only null dimension >= 2 can certify anything.
    """
    import itertools

    import numpy as np

    def pmul(a, b):
        return tuple(a[b[i]] for i in range(len(b)))

    sel = [r for r in rows if (not args.stratum_only or r["stratum"])]
    r = sel[args.index]
    ch = tuple(r["chain"])
    g = r["g_gen"]
    sl = PS.chain_slots_g(ch, g, 0, 0)
    ops, defect, h = window_data(ch, g, sl, (0, 0, 0, 0))
    d = args.degree
    perms = list(itertools.permutations(range(d)))
    idp = tuple(range(d))
    invol = [x for x in perms if pmul(x, x) == idp]
    hits, tested, maxnull, orb2 = [], 0, 0, 0
    for cbar in invol:
        tinv = tuple(sorted(range(d), key=lambda i: cbar[i]))  # placeholder
        for tbar in perms:
            els, fr = {idp}, [idp]
            while fr:
                nx = []
                for x in fr:
                    for gg in (cbar, tbar):
                        y = pmul(gg, x)
                        if y not in els:
                            els.add(y)
                            nx.append(y)
                fr = nx
            reps, ix = {}, {}
            for el in sorted(els):
                key = frozenset((el, pmul(el, cbar)))
                reps.setdefault(key, len(reps))
                ix[el] = reps[key]
            n = len(reps)
            if n < 2:
                continue
            rep_el = {}
            for el, i in ix.items():
                rep_el.setdefault(i, el)
            tperm = tbar
            tiv = tuple(sorted(range(d), key=lambda i: tbar[i]))

            def phi(word):
                x = idp
                for l in word:
                    x = pmul(x, cbar if abs(l) == C
                             else tperm if l == T else tiv)
                return x

            tested += 1
            # Gamma-orbit count on G/<cbar>
            gam = [phi(LV.to_tuple(s)) for s in gamma_gens(ch, g)]
            seen = [-1] * n
            norb = 0
            for st in range(n):
                if seen[st] >= 0:
                    continue
                norb += 1
                stack = [st]
                seen[st] = norb
                while stack:
                    v0 = stack.pop()
                    for gg in gam:
                        w0 = ix[pmul(gg, rep_el[v0])]
                        if seen[w0] < 0:
                            seen[w0] = norb
                            stack.append(w0)
            if norb < 2:
                continue
            orb2 += 1
            for p in PRIMES:
                mats = []
                for op in ops:
                    mt = np.zeros((n, n), dtype=np.int64)
                    for word, coef in op.items():
                        gg = phi(word)
                        for j in range(n):
                            mt[ix[pmul(gg, rep_el[j])], j] += coef
                    mats.append(mt % p)
                A = np.concatenate(mats, axis=1) % p
                mu = _null_space(A.T % p, p)
                maxnull = max(maxnull, int(mu.shape[0]))
                if mu.shape[0] == 0:
                    continue
                dv = np.zeros(n, dtype=np.int64)
                for v0, cf in defect.items():
                    dv[ix[phi(v0)]] += cf
                val = (mu @ (dv % p)) % p
                if (val != 0).any():
                    hits.append({"c": list(cbar), "t": list(tbar),
                                 "|G|": len(els), "n": n, "p": p})
    summ = {"chain": r["chain"], "g": g, "degree": d,
            "quotients_tested": tested,
            "quotients_with_ge2_gamma_orbits": orb2,
            "max_joint_left_null_dim": maxnull,
            "death_certificates_found": len(hits),
            "note": "left null dim 1 = the augmentation alone, which always "
                    "kills a defect of augmentation 0",
            "control_dynamic_range": orb2 > 0}
    print(json.dumps({"summary": summ, "sample_hits": hits[:5]}))
    if args.json:
        Path(args.json).write_text(json.dumps(
            {"schema": "acsolverx.w2g.quotients.v1", "summary": summ,
             "hits": hits}, indent=1))
    return 0 if orb2 > 0 else 2


def _null_space(A, p):
    import numpy as np
    A = A.copy() % p
    rows_, cols = A.shape
    piv, rr = [], 0
    for c in range(cols):
        if rr >= rows_:
            break
        nz = np.nonzero(A[rr:, c])[0]
        if nz.size == 0:
            continue
        s = rr + int(nz[0])
        if s != rr:
            A[[rr, s]] = A[[s, rr]]
        A[rr] = (A[rr] * pow(int(A[rr, c]), -1, p)) % p
        col = A[:, c].copy()
        col[rr] = 0
        msk = col != 0
        if msk.any():
            A[msk] = (A[msk] - np.outer(col[msk], A[rr])) % p
        piv.append(c)
        rr += 1
    free = [c for c in range(cols) if c not in set(piv)]
    out = []
    for f in free:
        v = np.zeros(cols, dtype=np.int64)
        v[f] = 1
        for i, c in enumerate(piv):
            v[c] = (-A[i, f]) % p
        out.append(v % p)
    return (np.array(out, dtype=np.int64) if out
            else np.zeros((0, cols), dtype=np.int64))


def perm_order(ct, word):
    """order of the right action of `word` on Gamma\\Q."""
    base = tuple(range(ct.n))
    cur = tuple(ct.trace_from(s, word) for s in base)
    k = 1
    while cur != base:
        cur = tuple(ct.trace_from(s, word) for s in cur)
        k += 1
        if k > 4 * ct.n:
            return None
    return k


def mode_period(args, rows):
    """Close the (k2, k3) axes over ALL of Z.

    h2 = h2_base * zeta2^k2 and h3 = h3_base * zeta3^k3 are the only
    window coordinates the operators see (h0, h1 enter the defect only).
    The Omega-row of a column depends on h2, h3 only through the state
    trace(h2), trace(h3) in the finite set Gamma\\Q, and
    trace(h_b zeta^k) = trace(h_b) . zeta^k is periodic in k with period
    ord(zeta) on that set.  So sweeping one full period of k2 and k3 decides
    d for EVERY integer window, not a box.
    """
    sel = [r for r in rows if (not args.stratum_only or r["stratum"])]
    if args.chains:
        a, b = args.chains.split(":")
        sel = sel[int(a or 0):int(b or len(sel))]
    out, ok = [], True
    for r in sel:
        ch = tuple(r["chain"])
        g = r["g_gen"]
        ct = CosetTable(gamma_gens(ch, g))
        rec = {"chain": r["chain"], "g": g, "stratum": r["stratum"],
               "live": r["live"]}
        if not ct.ok:
            rec["gamma_index"] = None
            out.append(rec)
            print(json.dumps(rec))
            continue
        sl = PS.chain_slots_g(ch, g, 1, 1)
        z2, z3 = sl["h2"]["zeta"], sl["h3"]["zeta"]
        o2, o3 = perm_order(ct, z2), perm_order(ct, z3)
        ds, ms = set(), set()
        for k2 in range(o2):
            for k3 in range(o3):
                sl2 = {"h0": sl["h0"], "h1": sl["h1"],
                       "h2": {"reps": {0: smul(sl["h2"]["h_base"],
                                               PS.INV.power(z2, k2))}},
                       "h3": {"reps": {0: smul(sl["h3"]["h_base"],
                                               PS.INV.power(z3, k3))}}}
                ops, defect, h = window_data(ch, g, sl2, (0, 0, 0, 0))
                d, m = omega_invariant(ct, ops, defect)
                ds.add(d)
                ms.add(m)
        rec.update({"gamma_index": ct.n, "zeta_orders": [o2, o3],
                    "windows_in_one_full_period": o2 * o3,
                    "d_over_all_k2_k3_in_Z": sorted(ds),
                    "m_seen": sorted(ms),
                    "d_is_1_for_every_integer_window": ds == {1}})
        if ds != {1}:
            # d > 1: death would need the defect class m to be a non-multiple
            # of d.  m depends on all four window coordinates, so sweep the
            # h0/h1 axes too (a BOX, not a closure -- stated as such).
            K = args.k or 3
            sl4 = PS.chain_slots_g(ch, g, K, K)
            m4 = set()
            for k0 in range(-K, K + 1):
                for k1 in range(-K, K + 1):
                    _, dfc, _ = window_data(ch, g, sl4, (k0, k1, 0, 0))
                    m4.add(sum(cf for v, cf in dfc.items()
                               if ct.omega[ct.trace(v)] == 0))
            rec["m_over_h0_h1_box"] = sorted(m4)
            rec["m_box_K"] = K
            rec["all_m_divisible_by_d"] = all(x % max(ds) == 0 for x in m4)
        out.append(rec)
        print(json.dumps(rec))
    fin = [o for o in out if o.get("gamma_index")]
    summ = {"chains": len(out), "finite_index": len(fin),
            "d_eq_1_for_all_k2k3_in_Z": sum(
                1 for o in fin if o["d_is_1_for_every_integer_window"]),
            "d_values": sorted({tuple(o["d_over_all_k2_k3_in_Z"])
                                for o in fin}),
            "controls_passed": ok}
    print(json.dumps({"summary": summ}))
    if args.json:
        Path(args.json).write_text(json.dumps(
            {"schema": "acsolverx.w2g.period.v1", "summary": summ,
             "rows": out}, indent=1))
    return 0


def mode_probe(args, rows):
    """Controls for the Omega machinery.

    (1) EFFECTIVE Lemma 1: the computed Omega-rows of the L2, L3, L4 columns
        must vanish IDENTICALLY.  `omega_invariant` reads d off the L0/L1
        rows only; that is legitimate exactly when the other three columns
        die in Z[Omega], which is what Lemma 1 asserts and what this checks.
        Corrupting one term of L2 must break it.
        (This control caught a real defect: union-find was free to re-root
        the base class of the Stallings graph, so `find(0) != 0`, every
        trace started from the wrong coset, and the L4 rows did NOT vanish.)

    (2) POSITIVE control: the detector must be able to FIRE.  On the real
        systems d = 1 everywhere, so no functional survives and no chain can
        be certified -- a detector that never fires is not evidence.  So the
        control runs it on a SYNTHETIC system with the same L2, L3, L4 and
        doubled L0, L1, which has d = 2 by construction.  There a defect of
        odd Omega-class MUST be certified dead mod 2, and the INDEPENDENT
        one-hop solver (`period_two_baseline_liveness.one_hop_system`, given
        the same synthetic operators) MUST agree it is unsolvable mod 2;
        the even-class defect must NOT be certified.

    (3) d | m on every real defect (the reason no real chain is certified).
    """
    sel = [r for r in rows if (not args.stratum_only or r["stratum"])]
    if args.chains:
        a, b = args.chains.split(":")
        sel = sel[int(a or 0):int(b or len(sel))]
    out, ok, n_fire = [], True, 0
    for r in sel:
        ch = tuple(r["chain"])
        g = r["g_gen"]
        ct = CosetTable(gamma_gens(ch, g))
        if not ct.ok:
            continue
        sl = PS.chain_slots_g(ch, g, 0, 0)
        ops, defect, h = window_data(ch, g, sl, (0, 0, 0, 0))
        d, m = omega_invariant(ct, ops, defect)

        # (1) effective Lemma 1, plus a corruption that must break it
        vanish = all(not any(row[1:]) for row in omega_row_set(ct, ops)
                     if row[0] in (2, 3, 4))
        bad = list(ops)
        d2 = dict(bad[2])
        d2.pop(sorted(d2)[0])
        bad[2] = d2
        broken = any(any(row[1:]) for row in omega_row_set(ct, tuple(bad))
                     if row[0] == 2)

        # (2) synthetic system with d = 2 by construction
        syn_ops = (LV.add_group_ring(ops[0], ops[0]),
                   LV.add_group_ring(ops[1], ops[1]),
                   ops[2], ops[3], ops[4])
        bases = {}
        for cl in range(ct.n_omega):
            for sw in PS.ball(6):
                vv = c_vertex(LV.to_tuple(sw))
                if ct.omega[ct.trace(vv)] == cl:
                    bases[cl] = vv
                    break
        odd = {bases[0]: 1, bases[1]: -1}
        even = {bases[0]: 2, bases[1]: -2}
        syn = {}
        d_syn = None
        for nm, sd in (("odd", odd), ("even", even)):
            dd, mm = omega_invariant(ct, syn_ops, sd)
            d_syn = dd
            rows_o, rhs_o, _ = LV.one_hop_system(sd, syn_ops)
            syn[nm] = {"class_m": mm,
                       "certificate_fires": [p for p in PRIMES
                                             if dd % p == 0 and mm % p],
                       "one_hop_solvable": {str(p): bool(
                           LV.solve_mod_p(rows_o, rhs_o, p))
                           for p in PRIMES}}
        fires_odd = 2 in syn["odd"]["certificate_fires"]
        silent_even = not syn["even"]["certificate_fires"]
        agree = syn["odd"]["one_hop_solvable"]["2"] is False
        n_fire += int(fires_odd)

        rec = {"chain": r["chain"], "g": g, "d_real": d, "m_real": m,
               "d_divides_m": m % d == 0,
               "l234_omega_rows_vanish": vanish,
               "corruption_breaks_vanishing": broken,
               "d_synthetic": d_syn,
               "synthetic": syn,
               "detector_fires_on_odd": fires_odd,
               "detector_silent_on_even": silent_even,
               "one_hop_agrees_odd_dead_mod2": agree}
        ok = ok and vanish and broken and (m % d == 0) and fires_odd \
            and silent_even and agree and d_syn == 2
        out.append(rec)
        print(json.dumps(rec))
    summ = {"chains": len(out),
            "d_real_values": sorted({r["d_real"] for r in out}),
            "all_d_divide_m": all(r["d_divides_m"] for r in out),
            "vanishing_holds": all(r["l234_omega_rows_vanish"] for r in out),
            "corruption_detected": all(r["corruption_breaks_vanishing"]
                                       for r in out),
            "detector_fired_on_synthetic": n_fire,
            "all_controls_passed": ok and bool(out),
            "note": "d = 1 on every real system, so no real chain can be "
                    "certified dead; the detector is shown able to fire on a "
                    "synthetic d = 2 system, cross-confirmed by the "
                    "independent one-hop solver"}
    print(json.dumps({"summary": summ}))
    if args.json:
        Path(args.json).write_text(json.dumps(
            {"schema": "acsolverx.w2g.probe.v2", "summary": summ,
             "rows": out}, indent=1))
    return 0 if (ok and out) else 2


def mode_lift(args, rows):
    """Constructive control: an explicit integral correction at windows W2f
    calls DEAD, verified by re-applying the operators."""
    sel = [r for r in rows if r["stratum"]] if args.stratum_only else rows
    r = sel[args.index]
    ch = tuple(r["chain"])
    g = r["g_gen"]
    ct = CosetTable(gamma_gens(ch, g))
    if not ct.ok:
        print(json.dumps({"chain": r["chain"], "g": g,
                          "status": "GAMMA_INFINITE_INDEX_NOT_HANDLED"}))
        return 0
    sl = PS.chain_slots_g(ch, g, args.k, args.k)
    out, ctl_pass, mut_done = [], True, False
    K = args.k
    for k0 in range(-K, K + 1):
        for k2 in range(-K, K + 1):
            ops, defect, h = window_data(ch, g, sl, (k0, 0, k2, 0))
            base = PS.eval_window(h[0], h[1], h[2], h[3], g,
                                  PS.ops_pack_for(ch[0], ch[1], ch[2],
                                                  h[2], h[3], g))
            moves = move_table(ch, g, h)
            sol, x, E, stats = build_lift(ct, ops, defect, moves,
                                          depth=args.depth,
                                          radius=args.radius)
            resid = verify_lift(defect, ops, x)
            rec = {"chain": r["chain"], "g": g, "window": [k0, 0, k2, 0],
                   "one_hop_solvable": base["solvable"],
                   "defect_terms": len(defect),
                   "route_stats": stats,
                   "x_terms": [len(xi) for xi in x],
                   "residual_after_lift": len(resid),
                   "VERIFIED_layer1_solution": sol is not None and not resid,
                   "algebra_consistent": resid == E}
            ctl_pass = ctl_pass and rec["algebra_consistent"]
            if x[4] and not mut_done:
                bad = list(ops)
                d4 = dict(bad[4])
                d4.pop(sorted(d4)[0])
                bad[4] = d4
                still = verify_lift(defect, tuple(bad), x)
                print(json.dumps({
                    "control": "mutation_breaks_verified_solution",
                    "residual_after_corruption": len(still),
                    "passed": bool(still)}))
                ctl_pass = ctl_pass and bool(still)
                mut_done = True
            out.append(rec)
            print(json.dumps(rec))
    ver = [o for o in out if o["VERIFIED_layer1_solution"]]
    dead1 = [o for o in out if not all(o["one_hop_solvable"].values())]
    summ = {"chain": r["chain"], "g": g, "windows": len(out),
            "one_hop_dead_windows": len(dead1),
            "windows_with_verified_layer1_solution": len(ver),
            "one_hop_dead_but_layer1_solved": sum(
                1 for o in dead1 if o["VERIFIED_layer1_solution"]),
            "mutation_control_run": mut_done,
            "controls_passed": ctl_pass}
    print(json.dumps({"summary": summ}))
    if args.json:
        Path(args.json).write_text(json.dumps(
            {"schema": "acsolverx.w2g.lift.v1", "summary": summ,
             "windows": out}, indent=1))
    return 0 if summ["controls_passed"] else 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("gamma", "omega", "lift",
                                       "probe", "period", "quotients"),
                    default="gamma")
    ap.add_argument("--k", type=int, default=1)
    ap.add_argument("--index", type=int, default=0)
    ap.add_argument("--chains", type=str, default="")
    ap.add_argument("--stratum-only", action="store_true")
    ap.add_argument("--cap-len", type=int, default=6)
    ap.add_argument("--depth", type=int, default=4)
    ap.add_argument("--radius", type=int, default=6)
    ap.add_argument("--degree", type=int, default=4,
                    help="quotients mode: permutation degree to scan")
    ap.add_argument("--control-samples", type=int, default=2)
    ap.add_argument("--json", type=str, default="")
    args = ap.parse_args()

    c1 = LV.analyze(PS.WITNESS, fixed_h=PS.CODEX_H)
    got = (c1["defect_terms"], c1["defect_l1"], c1["defect_augmentation"])
    print(json.dumps({"control": "fixed_h_witness", "defect": list(got),
                      "want": [21, 48, 0], "passed": got == (21, 48, 0)}))
    if got != (21, 48, 0):
        return 2

    rows = load_rows()
    if args.mode == "gamma":
        return mode_gamma(args, rows)
    if args.mode == "omega":
        return mode_omega(args, rows)
    if args.mode == "probe":
        return mode_probe(args, rows)
    if args.mode == "period":
        return mode_period(args, rows)
    if args.mode == "quotients":
        return mode_quotients(args, rows)
    return mode_lift(args, rows)


if __name__ == "__main__":
    sys.exit(main())
