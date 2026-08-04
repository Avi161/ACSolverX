"""S19 -- exact / bounded computation of the Lemma-11 number ``m`` = algebraic area.

NEW FILE.  Nothing here modifies or imports-and-mutates existing code; the only import
from the repo is the read-only Todd--Coxeter verifier ``coset_enum.is_trivial_group``.

Context: arXiv:2408.15332 Lemma 11 ("Substitution and Removal") eliminates a stabilized
generator ``y`` defined by the relator ``y^{-1} w`` by writing

    w = u_1 (r'_{i_1})^{e_1} u_1^{-1} ... u_m (r'_{i_m})^{e_m} u_m^{-1}      (in F(X))

and the authors state that no bound on ``m`` is known.  S19 identifies the minimal such
``m`` with the algebraic area ``Area_{P'}(w)``.  This script supplies the numbers for
S19 section 4:

  (a) an EXHAUSTIVE check that Area = 2 for w = [x,y] over the standard rank-2
      presentation <x,y | x, y> (a balanced presentation of the trivial group), and
      Area = k for w = x^k over <x | x>;
  (b) a rigorous LOWER bound on Area via finite-quotient sweeps: for ANY homomorphism
      phi : F(X) -> H (H finite; phi need not kill the relators), an expression with m
      factors maps to a product of m elements of
          S = (conjugacy class of phi(r_i)) union (class of phi(r_i)^{-1}),  i = 1..n,
      so  m >= dist_S(1, phi(w))  computed by BFS in H.  This bounds m from BELOW.
  (c) a bounded free-group BFS for an UPPER bound on Area (a witness expression).
      Bound direction: (b) is a lower bound, (c) is an upper bound.  They are NOT
      interchangeable -- see experiments/lessons/parallel-runs-and-bound-direction.md.

Word convention (matches the rest of the fable line): lowercase letter = generator,
uppercase = its inverse; the empty string is the identity.
"""

from __future__ import annotations

import argparse
import itertools
import json
import random
import sys
from collections import deque

sys.path.insert(0, __file__.rsplit("/experiments/", 1)[0])

from experiments.stable_ac.fable.coset_enum import is_trivial_group  # noqa: E402


# --------------------------------------------------------------------------- free group


def inv(word: str) -> str:
    return "".join(c.lower() if c.isupper() else c.upper() for c in reversed(word))


def reduce_word(word: str) -> str:
    out: list[str] = []
    for c in word:
        if out and out[-1] == (c.lower() if c.isupper() else c.upper()):
            out.pop()
        else:
            out.append(c)
    return "".join(out)


def mul(*words: str) -> str:
    return reduce_word("".join(words))


def ball(gens: str, radius: int) -> list[str]:
    """All reduced words of length <= radius over ``gens`` and their inverses."""
    letters = list(gens) + [g.upper() for g in gens]
    out = [""]
    frontier = [""]
    for _ in range(radius):
        nxt = []
        for w in frontier:
            for c in letters:
                cand = reduce_word(w + c)
                if len(cand) == len(w) + 1:
                    nxt.append(cand)
        out.extend(nxt)
        frontier = nxt
    return out


# --------------------------------------------------------------- permutation-group side


def perm_mul(a: tuple, b: tuple) -> tuple:
    """(a*b)(i) = a(b(i))."""
    return tuple(a[b[i]] for i in range(len(a)))


def perm_inv(a: tuple) -> tuple:
    out = [0] * len(a)
    for i, ai in enumerate(a):
        out[ai] = i
    return tuple(out)


def perm_eval(word: str, images: dict) -> tuple:
    n = len(next(iter(images.values())))
    acc = tuple(range(n))
    for c in word:
        g = images[c.lower()]
        acc = perm_mul(acc, g if c.islower() else perm_inv(g))
    return acc


def conj_class(elt: tuple, group: list[tuple]) -> set:
    return {perm_mul(perm_mul(g, elt), perm_inv(g)) for g in group}


def quotient_lower_bound(relators, w, gens, group, homs, verbose=False):
    """max over sampled homs phi of dist_S(1, phi(w)).  A LOWER bound on Area(w)."""
    best = 0
    best_hom = None
    stats = {"homs_tried": 0, "bfs_nodes": 0}
    ident = tuple(range(len(group[0])))
    for images in homs:
        stats["homs_tried"] += 1
        imap = dict(zip(gens, images))
        target = perm_eval(w, imap)
        if target == ident:
            continue
        S = set()
        for r in relators:
            rho = perm_eval(r, imap)
            if rho == ident:
                continue
            S |= conj_class(rho, group)
            S |= conj_class(perm_inv(rho), group)
        if not S:
            continue
        # BFS in H from the identity along right multiplication by S.
        dist = {ident: 0}
        q = deque([ident])
        while q:
            cur = q.popleft()
            stats["bfs_nodes"] += 1
            if cur == target:
                break
            for s in S:
                nxt = perm_mul(cur, s)
                if nxt not in dist:
                    dist[nxt] = dist[cur] + 1
                    q.append(nxt)
        d = dist.get(target)
        if d is not None and d > best:
            best, best_hom = d, images
            if verbose:
                print(f"    new lower bound {d} from hom {images}")
    return best, best_hom, stats


def sym_group(n: int) -> list[tuple]:
    return [tuple(p) for p in itertools.permutations(range(n))]


def quotient_detection_ceiling(relators, gens, group, homs):
    """Largest value the finite-quotient LOWER bound could EVER return on this H.

    This is the calibration required by
    experiments/lessons/calibrate-one-sided-hunts-on-a-positive-ladder.md: the bound is
    capped by the eccentricity of the identity in the S-Cayley graph of H, so a value
    equal to the ceiling means the instrument SATURATED and carries no information about
    how much larger the true area is.
    """
    ident = tuple(range(len(group[0])))
    best = 0
    for images in homs:
        imap = dict(zip(gens, images))
        S = set()
        for r in relators:
            rho = perm_eval(r, imap)
            if rho == ident:
                continue
            S |= conj_class(rho, group)
            S |= conj_class(perm_inv(rho), group)
        if not S:
            continue
        dist = {ident: 0}
        q = deque([ident])
        while q:
            cur = q.popleft()
            for s in S:
                nxt = perm_mul(cur, s)
                if nxt not in dist:
                    dist[nxt] = dist[cur] + 1
                    q.append(nxt)
        best = max(best, max(dist.values()))
    return best


# ------------------------------------------------------------------ free-group BFS (UB)


def area_upper_bound_bfs(relators, w, conj_radius=1, length_cap=24, node_cap=1000):
    """BFS from w, right-multiplying by u r^{+-1} u^{-1}, aiming at the identity.

    Returns (m, witness, nodes_popped) or (None, None, nodes_popped) if the budget ran
    out.  Any m returned is an UPPER bound on Area(w) (an explicit expression exists).
    """
    gens = sorted({c.lower() for r in relators for c in r} | {c.lower() for c in w})
    moves = []
    for u in ball("".join(gens), conj_radius):
        for r in relators:
            for rr in (r, inv(r)):
                mv = mul(u, rr, inv(u))
                if mv:
                    moves.append((mv, (u, rr)))
    start = reduce_word(w)
    seen = {start: (0, None)}
    q = deque([start])
    nodes = 0
    while q and nodes < node_cap:
        cur = q.popleft()
        nodes += 1
        d, _ = seen[cur]
        if cur == "":
            path = []
            node, (dd, back) = cur, seen[cur]
            while back is not None:
                prev, lab = back
                path.append(lab)
                node = prev
                dd, back = seen[prev]
            return d, list(reversed(path)), nodes
        for mv, lab in moves:
            nxt = mul(cur, mv)
            if len(nxt) > length_cap or nxt in seen:
                continue
            seen[nxt] = (d + 1, (cur, lab))
            q.append(nxt)
    return (0, [], nodes) if start == "" else (None, None, nodes)


# ------------------------------------------------------------------------------- checks


def check_standard_rank2():
    """Exhaustive: Area_{<x,y|x,y>}([x,y]) = 2."""
    relators = ["x", "y"]
    w = "xyXY"
    # Upper bound: exhibit an explicit 2-factor expression.
    witness = mul("x", mul("y", "X", "Y"))
    ok_ub = witness == w
    # Lower bound: no single conjugate u g^{+-1} u^{-1} equals w, because every such
    # element is conjugate to a generator, hence has cyclically reduced length 1,
    # while w is cyclically reduced of length 4.  Verified exhaustively out to |u| <= 6.
    found1 = None
    for u in ball("xy", 6):
        for g in ("x", "X", "y", "Y"):
            if mul(u, g, inv(u)) == w:
                found1 = (u, g)
    return {
        "presentation": "<x,y | x, y>",
        "w": w,
        "explicit_2_factor_expression": "x * (y x^{-1} y^{-1})",
        "expression_checks_out": ok_ub,
        "one_factor_expression_found_|u|<=6": found1,
        "Area": 2 if (ok_ub and found1 is None) else None,
    }


def check_rank1_powers(kmax=8):
    """Exhaustive-in-principle: Area_{<x|x>}(x^k) = k (abelianization is exact here)."""
    rows = []
    for k in range(1, kmax + 1):
        w = "x" * k
        ub, wit, nodes = area_upper_bound_bfs(["x"], w, conj_radius=1,
                                              length_cap=k + 2, node_cap=1000)
        rows.append({"k": k, "w": w, "bfs_upper_bound": ub, "nodes": nodes,
                     "abelianization_lower_bound": k})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--node-cap", type=int, default=1000)
    ap.add_argument("--s5-homs", type=int, default=1500)
    ap.add_argument("--seed", type=int, default=1919)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    random.seed(args.seed)

    report = {}

    print("== (0) triviality certificates (Todd-Coxeter, trivial subgroup) ==")
    triv = {}
    for name, words in [
        ("std2  <x,y | x, y>", ["x", "y"]),
        ("AK(2) <x,y | xyxYXY, xxYYY>", ["xyxYXY", "xxYYY"]),
    ]:
        res = is_trivial_group(words, generators=("x", "y"), cap=20000)
        triv[name] = res
        print(f"  {name}: {res}")
    report["triviality"] = {k: str(v) for k, v in triv.items()}

    print("\n== (1) standard rank-2, w = [x,y] (exact) ==")
    r = check_standard_rank2()
    report["standard_rank2_commutator"] = r
    print(" ", json.dumps(r))

    print("\n== (2) rank-1 <x|x>, w = x^k (exact) ==")
    rows = check_rank1_powers()
    report["rank1_powers"] = rows
    for row in rows:
        print(f"  k={row['k']:2d}  UB(bfs)={row['bfs_upper_bound']}  "
              f"LB(abelianization)={row['abelianization_lower_bound']}  "
              f"nodes={row['nodes']}")

    print("\n== (3) AK(2) = <x,y | xyxYXY, xxYYY>, w = x ==")
    ak2 = ["xyxYXY", "xxYYY"]
    S4 = sym_group(4)
    homs4 = [(a, b) for a in S4 for b in S4]
    lb4, hom4, st4 = quotient_lower_bound(ak2, "x", "xy", S4, homs4)
    print(f"  S4 sweep: {st4['homs_tried']} homs, {st4['bfs_nodes']} BFS nodes"
          f"  ->  Area(x) >= {lb4}   (witness hom {hom4})")
    S5 = sym_group(5)
    homs5 = [(random.choice(S5), random.choice(S5)) for _ in range(args.s5_homs)]
    lb5, hom5, st5 = quotient_lower_bound(ak2, "x", "xy", S5, homs5)
    print(f"  S5 sample: {st5['homs_tried']} homs, {st5['bfs_nodes']} BFS nodes"
          f"  ->  Area(x) >= {lb5}   (witness hom {hom5})")
    ub, wit, nodes = area_upper_bound_bfs(ak2, "x", conj_radius=1, length_cap=26,
                                          node_cap=args.node_cap)
    print(f"  free-group BFS (|u|<=1, len<=26, {nodes} nodes popped):"
          f"  Area(x) <= {ub if ub is not None else 'NOT FOUND within budget'}")
    report["ak2_area_x"] = {
        "lower_bound_S4": lb4, "S4_homs": st4["homs_tried"],
        "lower_bound_S5_sample": lb5, "S5_homs": st5["homs_tried"],
        "upper_bound_bfs": ub, "bfs_nodes_popped": nodes,
        "bfs_witness": wit,
    }

    ceil4 = quotient_detection_ceiling(ak2, "xy", S4, homs4)
    ceil5 = quotient_detection_ceiling(ak2, "xy", S5, homs5)
    print(f"  DETECTION CEILINGS (max value the method could return):"
          f" S4 = {ceil4}, S5 sample = {ceil5}")
    print("  -> a returned value equal to the ceiling means the instrument SATURATED.")
    report["ak2_area_x"]["ceiling_S4"] = ceil4
    report["ak2_area_x"]["ceiling_S5_sample"] = ceil5

    print("\n== (4) sanity: same lower-bound machine on the standard rank-2 pair ==")
    lb_std, hom_std, st_std = quotient_lower_bound(["x", "y"], "xyXY", "xy", S4, homs4)
    print(f"  S4 sweep on <x,y|x,y>, w=[x,y]: Area >= {lb_std}"
          f"  (true value 2; the quotient bound is allowed to be slack)")
    report["standard_rank2_quotient_lb"] = lb_std

    if args.out:
        with open(args.out, "w") as fh:
            json.dump(report, fh, indent=2, default=str)
        print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
