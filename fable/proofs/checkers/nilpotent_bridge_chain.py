"""W5 I3 — INFINITE, NON-BASE-KILLING quotients: the free nilpotent tower.

This is the regime the W1 vacuity theorem leaves alive (phi(A), phi(B)
nontrivial) and that BLM 2005 does not reach (G infinite).  Model: the Magnus
truncation

    F3 -> U_d = { 1 + sum_{1<=|m|<=d} c_m X_m } in Z<<X1,X2,X3>>/(deg > d),
    x_i -> 1 + X_i ,

whose kernel is gamma_{d+1}(F3); U_d is the free nilpotent group of class d on
three generators -- infinite and nonabelian for every d >= 2.

Rather than searching an infinite orbit (forbidden and impossible), the checker
CONSTRUCTS a finite chain of projected AC moves and verifies every move
literally:

  phase A  elementary row operations matching the abelianised matrices
           (adds = AC2 with trivial conjugator, negations = AC1);
  phase L  for L = 2..d the residual multipliers r_i^-1 v_i all lie in
           gamma_L, hence are central and additive modulo gamma_{L+1}.  A pool
           of composite gadgets -- each an explicit short AC move word whose
           net effect is a gamma_L multiplication -- is evaluated numerically
           and a single exact integer solve over all three rows at once picks
           the multiplicities.

  Gadget kinds (all built from literal AC1/AC2 moves):
    local(i,j,w,prep)  r_i -> r_i [w, r_j], optionally after r_j -> r_j r_l^m
                       and undone afterwards (l the third index);
    transfer(i,j,w,e)  r_j -> r_j r_i^e ; r_i -> r_i [w, r_j] ; r_j -> r_j r_i^-e.
                       This one moves a gamma_L element from row j to row i and
                       supplies exactly the bracket directions [., a_i] that no
                       row-local gadget can reach.

Controls:
  (+) certified positive: image(Txy) must connect to image(x,y,z) -- Txy IS
      AC-trivial (134-move repo certificate), so its image is connected in
      EVERY quotient; a method that fails here is too weak and licenses no null.
  (-) adversarial: image(x,y,zz) must NOT connect to image(x,y,z) (|det| = 2).
  (-) a corrupted move must be rejected by the move verifier.

Run:
  python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- \
      python3 fable/proofs/checkers/nilpotent_bridge_chain.py --degree 2
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from w5_words import A, B, K_PUB, K_XY, abelianize, inv, reduce_word  # noqa: E402
from w5_linalg import (  # noqa: E402
    apply_ops_to_matrix, invert_ops, reduce_to_identity, solve_int,
)

FAILS: list[str] = []
Elem = dict[tuple[int, ...], int]
Move = tuple                      # ("AC2", i, j, e, conjugator_word) | ("AC1", i)


def check(name: str, cond: bool, detail: str = "") -> None:
    print(f"{'PASS' if cond else 'FAIL'}  {name}" + (f"   {detail}" if detail else ""))
    if not cond:
        FAILS.append(name)


# ------------------------------------------------- truncated Magnus algebra --

class Magnus:
    def __init__(self, deg: int) -> None:
        self.d = deg

    def one(self) -> Elem:
        return {(): 1}

    def mul(self, a: Elem, b: Elem) -> Elem:
        out: Elem = {}
        for m1, c1 in a.items():
            for m2, c2 in b.items():
                if len(m1) + len(m2) > self.d:
                    continue
                m = m1 + m2
                out[m] = out.get(m, 0) + c1 * c2
                if out[m] == 0:
                    del out[m]
        return out

    def inv(self, a: Elem) -> Elem:
        assert a.get((), 0) == 1, "not a 1-unit"
        n = {m: c for m, c in a.items() if m != ()}
        out, power, sign = self.one(), self.one(), 1
        for _ in range(self.d):
            power = self.mul(power, n)
            if not power:
                break
            sign = -sign
            for m, c in power.items():
                out[m] = out.get(m, 0) + sign * c
                if out[m] == 0:
                    del out[m]
        return out

    def gen(self, i: int) -> Elem:
        return {(): 1, (i,): 1}

    def word(self, w: str) -> Elem:
        out = self.one()
        for ch in w:
            g = self.gen("xyz".index(ch.lower()))
            out = self.mul(out, g if ch.islower() else self.inv(g))
        return out

    def comm(self, a: Elem, b: Elem) -> Elem:
        return self.mul(self.mul(self.inv(a), self.inv(b)), self.mul(a, b))

    def degree_part(self, a: Elem, L: int) -> dict[tuple[int, ...], int]:
        return {m: c for m, c in a.items() if len(m) == L}

    def min_degree(self, a: Elem) -> int:
        nz = [len(m) for m, c in a.items() if m != () and c]
        return min(nz) if nz else self.d + 1


def monomials(L: int) -> list[tuple[int, ...]]:
    return list(itertools.product(range(3), repeat=L))


# ------------------------------------------------------- projected AC moves --

def ac2(M: Magnus, st: list[Elem], i: int, j: int, e: int, cw: Elem) -> list[Elem]:
    assert i != j and e in (1, -1)
    rj = st[j] if e == 1 else M.inv(st[j])
    new = list(st)
    new[i] = M.mul(st[i], M.mul(M.mul(cw, rj), M.inv(cw)))
    return new


def ac1(M: Magnus, st: list[Elem], i: int) -> list[Elem]:
    new = list(st)
    new[i] = M.inv(st[i])
    return new


def apply_move(M: Magnus, st: list[Elem], mv: Move) -> list[Elem]:
    if mv[0] == "AC1":
        return ac1(M, st, mv[1])
    _, i, j, e, cw = mv
    return ac2(M, st, i, j, e, M.word(cw))


def verify_move(M: Magnus, before: list[Elem], after: list[Elem], mv: Move) -> bool:
    """Independent re-derivation of the move from its recorded parameters."""
    if mv[0] == "AC1":
        i = mv[1]
        return all(after[k] == (M.inv(before[i]) if k == i else before[k]) for k in range(3))
    _, i, j, e, cw = mv
    if i == j or e not in (1, -1):
        return False
    rj = before[j] if e == 1 else M.inv(before[j])
    c = M.mul(M.mul(M.word(cw), rj), M.inv(M.word(cw)))
    return all(after[k] == (M.mul(before[i], c) if k == i else before[k]) for k in range(3))


class Chain:
    def __init__(self, M: Magnus, state: list[Elem]) -> None:
        self.M, self.state, self.moves, self.bad = M, list(state), [], 0

    def do(self, mv: Move) -> None:
        nxt = apply_move(self.M, self.state, mv)
        if not verify_move(self.M, self.state, nxt, mv):
            self.bad += 1
        self.state = nxt
        self.moves.append(mv)

    def run(self, mvs: list[Move]) -> None:
        for mv in mvs:
            self.do(mv)


# ------------------------------------------------------------------ gadgets --

def gadget_moves(kind: str, i: int, j: int, cw: str, s: int, param) -> list[Move]:
    """Composite whose net effect is a single gamma_L multiplication."""
    if kind == "local":
        l, m = param
        pre = [("AC2", j, l, 1 if m > 0 else -1, "")] * abs(m)
        post = [("AC2", j, l, -1 if m > 0 else 1, "")] * abs(m)
        return pre + [("AC2", i, j, s, cw), ("AC2", i, j, -s, "")] + post
    if kind == "transfer":
        e = param
        return [("AC2", j, i, e, ""),
                ("AC2", i, j, s, cw), ("AC2", i, j, -s, ""),
                ("AC2", j, i, -e, "")]
    raise ValueError(kind)


def net_value(M: Magnus, st: list[Elem], mvs: list[Move]) -> list[Elem]:
    cur = st
    for mv in mvs:
        cur = apply_move(M, cur, mv)
    return [M.mul(M.inv(st[k]), cur[k]) for k in range(3)]


def conjugators(L: int) -> list[str]:
    """Conjugator words w with [w, r] in gamma_L."""
    if L == 2:
        return ["x", "y", "z"]
    if L == 3:
        return [reduce_word(inv(a) + inv(b) + a + b)
                for a, b in itertools.permutations("xyz", 2)]
    if L == 4:
        out = []
        for a, b in itertools.permutations("xyz", 2):
            c2 = reduce_word(inv(a) + inv(b) + a + b)
            for c in "xyz":
                out.append(reduce_word(inv(c2) + inv(c) + c2 + c))
        return out
    raise NotImplementedError(L)


def gadget_pool(M: Magnus, st: list[Elem], L: int) -> tuple[list[list[int]], list]:
    """Columns of the layer-L correction system (concatenated over the 3 rows)."""
    mons = monomials(L)
    dim = 3 * len(mons)
    cols: list[list[int]] = []
    tags: list = []
    specs: list[tuple] = []
    for i in range(3):
        for j in range(3):
            if i == j:
                continue
            l = ({0, 1, 2} - {i, j}).pop()
            for cw in conjugators(L):
                for m in (0, 1, -1):
                    specs.append(("local", i, j, cw, (l, m)))
                for e in (1, -1):
                    specs.append(("transfer", i, j, cw, e))
    for kind, i, j, cw, param in specs:
        pos = net_value(M, st, gadget_moves(kind, i, j, cw, 1, param))
        if any(M.min_degree(v) < L for v in pos):
            continue
        vec = []
        for k in range(3):
            dp = M.degree_part(pos[k], L)
            vec.extend(dp.get(m, 0) for m in mons)
        if not any(vec):
            continue
        neg = net_value(M, st, gadget_moves(kind, i, j, cw, -1, param))
        if any(M.min_degree(v) < L for v in neg):
            continue
        nvec = []
        for k in range(3):
            dp = M.degree_part(neg[k], L)
            nvec.extend(dp.get(m, 0) for m in mons)
        if nvec != [-v for v in vec]:
            continue          # sign-flipped gadget is not the exact inverse here
        assert len(vec) == dim
        cols.append(vec)
        tags.append((kind, i, j, cw, param))
    return cols, tags


# --------------------------------------------------------------- the driver --

def abelianize_elem(M: Magnus, e: Elem) -> list[int]:
    return [e.get((k,), 0) for k in range(3)]


def connect(M: Magnus, src_words: tuple[str, str, str],
            tgt_words: tuple[str, str, str]) -> dict:
    d = M.d
    src = [M.word(w) for w in src_words]
    tgt = [M.word(w) for w in tgt_words]
    Ms = [list(abelianize(w)) for w in src_words]
    Mt = [list(abelianize(w)) for w in tgt_words]
    rep: dict = {"degree": d, "src": list(src_words), "tgt": list(tgt_words),
                 "ab_src": Ms, "ab_tgt": Mt}

    ops_s, ops_t = reduce_to_identity(Ms), reduce_to_identity(Mt)
    if ops_s is None or ops_t is None:
        rep["status"] = "refused: abelianised matrix not in GL3(Z)"
        return rep
    ops = list(ops_s) + invert_ops(list(ops_t))
    if apply_ops_to_matrix(Ms, ops) != Mt:
        rep["status"] = "refused: elementary chain does not match abelianisations"
        return rep

    ch = Chain(M, src)
    for op in ops:                                          # ---------- phase A
        if op[0] == "neg":
            ch.do(("AC1", op[1]))
        else:
            _, i, j, k = op
            ch.run([("AC2", i, j, 1 if k > 0 else -1, "")] * abs(k))
    rep["phase_A_moves"] = len(ch.moves)
    if [abelianize_elem(M, e) for e in ch.state] != Mt:
        rep["status"] = "phase A did not reach the target abelianisation"
        return rep

    layers = []
    for L in range(2, d + 1):                                # ---------- phase L
        mons = monomials(L)
        resid = [M.mul(M.inv(ch.state[i]), tgt[i]) for i in range(3)]
        if any(M.min_degree(r) < L for r in resid):
            rep["status"] = f"layer {L}: a residual is not in gamma_{L}"
            return rep
        target: list[int] = []
        for i in range(3):
            dp = M.degree_part(resid[i], L)
            target.extend(dp.get(m, 0) for m in mons)
        if not any(target):
            layers.append({"layer": L, "correction": "none"})
            continue
        cols, tags = gadget_pool(M, ch.state, L)
        if not cols:
            rep["status"] = f"layer {L}: empty gadget pool"
            return rep
        Mx = [[cols[t][r] for t in range(len(cols))] for r in range(len(target))]
        sol = solve_int(Mx, target)
        if sol is None:
            rep["status"] = (f"layer {L}: integer solve failed "
                             f"({len(cols)} gadget columns, dim {len(target)})")
            rep["unsolved_layer"] = L
            return rep
        used = []
        for t, mlt in enumerate(sol):
            if not mlt:
                continue
            kind, i, j, cw, param = tags[t]
            for _ in range(abs(mlt)):
                ch.run(gadget_moves(kind, i, j, cw, 1 if mlt > 0 else -1, param))
            used.append([kind, i, j, cw, param, mlt])
        layers.append({"layer": L, "columns": len(cols), "gadgets": used})
    rep["layers"] = layers
    rep["total_moves"] = len(ch.moves)
    rep["bad_moves"] = ch.bad
    rep["exact_match"] = ch.state == tgt
    rep["status"] = "connected" if rep["exact_match"] else "chain did not reach the target"
    return rep


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--degree", type=int, default=2)
    args = ap.parse_args()
    d = args.degree
    M = Magnus(d)

    Txy, Tpub, STD = (A, B, K_XY), (A, B, K_PUB), ("x", "y", "z")

    check(f"I3: phi(A) != 1 in the class-{d} quotient (NOT base-killing)",
          M.word(A) != M.one())
    check(f"I3: phi(B) != 1 in the class-{d} quotient (NOT base-killing)",
          M.word(B) != M.one())
    check("I3: the quotient is infinite (x^n -> 1 + nX)",
          M.word("xxxxx").get((0,), 0) == 5)
    check("I3: the quotient is nonabelian for d >= 2",
          d < 2 or M.comm(M.word("x"), M.word("y")) != M.one())

    results = {}
    rep = connect(M, Tpub, Txy)
    results["Tpub->Txy"] = rep
    print(f"\n[bridge]   class-{d} connect(Tpub -> Txy): {rep['status']}"
          f"  moves={rep.get('total_moves')}")
    rep_pos = connect(M, Txy, STD)
    results["Txy->STD"] = rep_pos
    print(f"[control+] class-{d} connect(Txy  -> std): {rep_pos['status']}"
          f"  moves={rep_pos.get('total_moves')}")
    rep_neg = connect(M, ("x", "y", "zz"), STD)
    results["zz->STD"] = rep_neg
    print(f"[control-] class-{d} connect((x,y,zz) -> std): {rep_neg['status']}\n")

    check("I3 control(+): Txy (CERTIFIED AC-trivial, so connected in EVERY "
          "quotient) is connected to (x,y,z) by the constructed chain",
          rep_pos.get("exact_match") is True, rep_pos["status"])
    check("I3 control(-): (x,y,zz) is REFUSED (|det| = 2): the method can fail",
          rep_neg.get("exact_match") is not True, rep_neg["status"])
    st = [M.word(w) for w in Tpub]
    good = ac2(M, st, 0, 2, 1, M.word("xy"))
    check("I3 control(-): corrupted move parameters rejected by the verifier",
          verify_move(M, st, good, ("AC2", 0, 2, 1, "xy"))
          and not verify_move(M, st, good, ("AC2", 0, 2, 1, "xz"))
          and not verify_move(M, st, good, ("AC2", 0, 1, 1, "xy")))
    if rep_pos.get("exact_match") is True:
        check(f"I3 BRIDGE: image(Tpub) and image(Txy) are connected in the free "
              f"class-{d} nilpotent quotient (=> that quotient is BLIND)",
              rep.get("exact_match") is True, rep["status"])
        check("I3: every move of the bridge chain verified",
              rep.get("bad_moves") == 0)
    else:
        print("  (bridge verdict withheld: the positive control failed, so a "
              "negative result here would be a weakness of the method, not an "
              "obstruction)")

    dest = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "out", f"w5_nilpotent_class{d}.json")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w") as fh:
        json.dump(results, fh, indent=1, default=str)
    print(f"\nwrote {dest}")
    print("\n" + ("ALL CHECKS PASS" if not FAILS else f"FAILURES: {FAILS}"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    raise SystemExit(main())
