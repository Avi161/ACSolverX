"""Scaled SPLIT search for a cubic triangular form of AK(3) — task A6 follow-up (S4B).

Implements the `SPLIT` move of `results/stable_ac/theory/fable/S4_CUBIC_NORMAL_FORM.md`
Lemma S4.4 and searches the reachable space from many triangulations of AK(3).

Two goals, run simultaneously, and the second is NOT gated on the first:

1. **cubic form** — reach a state with every relator of length 3 and every generator
   occurring exactly 3 times (Q-red: all relators cyclically reduced);
2. **gamma_N = 0 certificate** — every state visited is a legal member of the source
   presentation's stable class (AC4 + AC1-AC3 only), so a `gamma_N = 0` hit anywhere in the
   search settles the source via Lackenby Thm 1.3 (S12).  Because every state is triangular
   the census size is `prod_g (m_g - 1)!`, which is small exactly when the state is near
   cubic, so the scan is cheapest where it is most wanted (S10).

Conventions: a lowercase letter is a generator, the matching uppercase letter its inverse
(repo convention, `ac_words.py`).  Every state is a tuple of length-3 cyclically reduced
words; `SPLIT` preserves both properties (Lemma S4.4), which is asserted on every child.

Nothing here modifies existing modules.  Checkpoints are appended as JSONL so a container
restart cannot lose a hit.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from collections import Counter
from itertools import combinations
from math import factorial

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))

from experiments.stable_ac.fable.neuwirth_rank_n import gamma_N_factorial_n  # noqa: E402
from experiments.stable_ac.fable.coset_enum import is_trivial_group  # noqa: E402

ALPHABET = "abcdefghijklmnopqrstuvwxyz"

# AK(3), repo spelling (FRAMING Sec 1).
AK3 = ("xyxYXY", "xxxYYYY")


# ----------------------------------------------------------------------------------------
# words
# ----------------------------------------------------------------------------------------


def inv_letter(c: str) -> str:
    return c.swapcase()


def inv_word(w: str) -> str:
    return w[::-1].swapcase()


def rot_word(w: str, k: int) -> str:
    k %= len(w)
    return w[k:] + w[:k]


def free_reduce(w: str) -> str:
    out: list = []
    for c in w:
        if out and out[-1] == c.swapcase():
            out.pop()
        else:
            out.append(c)
    return "".join(out)


def cyc_reduce(w: str) -> str:
    w = free_reduce(w)
    while len(w) > 1 and w[0] == w[-1].swapcase():
        w = free_reduce(w[1:-1])
    return w


def is_cyc_reduced(w: str) -> bool:
    return bool(w) and free_reduce(w) == w and (len(w) == 1 or w[0] != w[-1].swapcase())


def canon_cyclic(w: str) -> str:
    """Canonical form of a relator as an unoriented cyclic word."""
    cands = [rot_word(w, k) for k in range(len(w))]
    iw = inv_word(w)
    cands += [rot_word(iw, k) for k in range(len(iw))]
    return min(cands)


def canon_state(state) -> tuple:
    return tuple(sorted(canon_cyclic(w) for w in state))


def gens_of(state) -> tuple:
    return tuple(sorted({c.lower() for w in state for c in w}))


def multiplicities(state) -> dict:
    return Counter(c.lower() for w in state for c in w)


def delta(state) -> dict:
    return {g: m - 3 for g, m in multiplicities(state).items()}


def census_size(state) -> int:
    tot = 1
    for m in multiplicities(state).values():
        tot *= factorial(m - 1)
    return tot


def is_triangular(state) -> bool:
    return all(len(w) == 3 for w in state)


def is_cubic(state) -> bool:
    return all(m == 3 for m in multiplicities(state).values())


def is_nondegenerate(state) -> bool:
    return all(is_cyc_reduced(w) for w in state)


def is_balanced(state) -> bool:
    return len(state) == len(gens_of(state))


# ----------------------------------------------------------------------------------------
# triangulation (chord refinement) -- the roots
# ----------------------------------------------------------------------------------------


def chord_refine(words, i: int, k: int, z: str, convention: str = "pos",
                 end: str = "prefix"):
    """One elementary chord refinement (S3 Sec 1 / S1 Sec 4.2, choice family S1 Sec 4.5)."""
    r = words[i]
    if len(r) < 4:
        raise ValueError("relator too short to refine")
    if end == "suffix":
        rr = rot_word(r, k - 2)
        a1, a2, body = rr[-2], rr[-1], rr[:-2]
        if convention == "pos":
            D, shortened = z + inv_letter(a2) + inv_letter(a1), body + z
        else:
            D, shortened = z + a1 + a2, body + inv_letter(z)
    else:
        rr = rot_word(r, k)
        a1, a2, body = rr[0], rr[1], rr[2:]
        if convention == "pos":
            D, shortened = z + inv_letter(a2) + inv_letter(a1), z + body
        else:
            D, shortened = z + a1 + a2, inv_letter(z) + body
    new = list(words)
    new[i] = shortened
    new.append(D)
    return tuple(new)


def triangulate(words, rng, max_rank: int = 26):
    """A random member of the triangulation family: all relators down to length 3."""
    words = tuple(words)
    used = {c.lower() for w in words for c in w}
    fresh = [c for c in ALPHABET if c not in used]
    while any(len(w) >= 4 for w in words):
        if not fresh or len(words) >= max_rank:
            return None
        cand = [i for i, w in enumerate(words) if len(w) >= 4]
        i = rng.choice(cand)
        k = rng.randrange(len(words[i]))
        words = chord_refine(words, i, k, fresh.pop(0),
                             rng.choice(["pos", "neg"]),
                             rng.choice(["prefix", "suffix"]))
    if not (is_triangular(words) and is_nondegenerate(words) and is_balanced(words)):
        return None
    return words


# ----------------------------------------------------------------------------------------
# the SPLIT move (S4 Lemma S4.4)
# ----------------------------------------------------------------------------------------


def fresh_generator(state):
    used = {c.lower() for w in state for c in w}
    for c in ALPHABET:
        if c not in used:
            return c
    return None


def split_apply(state, i: int, invert: bool, rot: int, positions, t: str):
    """Apply SPLIT to relator ``i``.

    ``R' = rot_word(inv_word(r_i) if invert else r_i, rot) = lam u v``; the definition
    relator ``D = t u v`` is appended; the occurrences listed in ``positions`` (pairs
    ``(j, p)`` with ``j != i``, each carrying the letter ``lam`` or ``lam^{-1}``) are
    rewritten to ``t`` resp. ``t^{-1}``.  Returns ``(child, record)`` or ``None`` if the
    child would be degenerate.
    """
    base = inv_word(state[i]) if invert else state[i]
    r2 = rot_word(base, rot)
    lam, u, v = r2[0], r2[1], r2[2]
    ilam = inv_letter(lam)
    new = list(state)
    new[i] = r2
    for (j, p) in positions:
        if j == i:
            return None
        c = new[j][p]
        if c == lam:
            rep = t
        elif c == ilam:
            rep = inv_letter(t)
        else:
            return None
        new[j] = new[j][:p] + rep + new[j][p + 1:]
    D = t + u + v
    new.append(D)
    child = tuple(new)
    if not (is_triangular(child) and is_nondegenerate(child) and is_balanced(child)):
        return None
    # Lemma S4.4 step 3, asserted on every application: D R'^{-1} = t lam^{-1} freely.
    if free_reduce(D + inv_word(r2)) != free_reduce(t + ilam):
        raise AssertionError("S4.4 step-3 identity failed")
    record = {"relator": i, "invert": invert, "rot": rot, "lam": lam, "u": u, "v": v,
              "t": t, "k": len(positions), "positions": [list(p) for p in positions]}
    return child, record


def split_children(state, rng, max_children: int = 260, k_values=(1, 2, 3),
                   subsets_per_k: int = 6):
    """Candidate SPLIT children.

    ``Delta delta = -k e_{g_lam} + e_{g_u} + e_{g_v} + (k-2) e_t`` depends only on
    ``(g_lam, g_u, g_v, k)``, so the (relator, rotation, k) triples are ranked by their
    exact cost effect first and only the promising ones have their occurrence subsets
    sampled — the subset choice does not move the cost but does change the words, which is
    what the gamma_N scan needs.
    """
    t = fresh_generator(state)
    if t is None:
        return []
    d = delta(state)
    plans = []
    for i, r in enumerate(state):
        for invert in (False, True):
            base = inv_word(r) if invert else r
            for rot in range(3):
                r2 = rot_word(base, rot)
                lam, u, v = r2[0], r2[1], r2[2]
                gl, gu, gv = lam.lower(), u.lower(), v.lower()
                pos = [(j, p) for j, w in enumerate(state) if j != i
                       for p, c in enumerate(w) if c.lower() == gl]
                for k in k_values:
                    if k > len(pos):
                        continue
                    nd = dict(d)
                    nd[gl] = nd.get(gl, 0) - k
                    nd[gu] = nd.get(gu, 0) + 1
                    nd[gv] = nd.get(gv, 0) + 1
                    nd[t] = k - 2
                    plans.append((sum(abs(x) for x in nd.values()),
                                  i, invert, rot, k, tuple(pos)))
    if not plans:
        return []
    plans.sort(key=lambda p: p[0])
    out = []
    for score, i, invert, rot, k, pos in plans:
        if len(out) >= max_children:
            break
        combos = list(combinations(range(len(pos)), k))
        rng.shuffle(combos)
        for combo in combos[:subsets_per_k]:
            got = split_apply(state, i, invert, rot,
                              tuple(pos[c] for c in combo), t)
            if got is not None:
                out.append(got)
            if len(out) >= max_children:
                break
    return out


# ----------------------------------------------------------------------------------------
# cost functions -- T-S11 says a plain sum|delta| greedy stalls on a parity plateau
# ----------------------------------------------------------------------------------------


def useful_moves(state) -> int:
    """Number of (relator, rotation) choices satisfying Lemma S4.6, i.e. a SPLIT that
    strictly reduces ``sum|delta|``.  Used as the plateau tie-break: a state one move from
    done scores better than a state with the same ``sum|delta|`` and no exit."""
    d = delta(state)
    n = 0
    for r in state:
        for base in (r, inv_word(r)):
            for rot in range(3):
                r2 = rot_word(base, rot)
                a, b, c = r2[0].lower(), r2[1].lower(), r2[2].lower()
                da, db, dc = d.get(a, 0), d.get(b, 0), d.get(c, 0)
                if a != b and a != c and b != c:
                    if da > 0 and db < 0 and dc < 0:
                        n += 1
                elif b == c and a != b:
                    if da >= 2 and db <= -2:
                        n += 1
                elif a == b and a != c:          # content {a,a,c}, lam = a: parity transfer
                    if da > 0 > dc:
                        n += 1
                elif a == c and a != b:
                    if da > 0 > db:
                        n += 1
    return n


def cost(state, mode: str):
    d = delta(state)
    sd = sum(abs(x) for x in d.values())
    n_over = sum(1 for x in d.values() if x > 0)
    spread = max(d.values()) - min(d.values()) if d else 0
    if mode == "sumdelta":
        return (sd,)
    if mode == "tiebreak":                  # sum|delta|, plateau broken by exits available
        return (sd, -useful_moves(state))
    if mode == "lex":                       # coordinator's suggestion 1
        return (n_over, sd, -useful_moves(state))
    if mode == "spread":                    # multiplicity-multiset tie-break
        return (sd, spread, -useful_moves(state))
    raise ValueError(f"unknown mode {mode!r}")


# ----------------------------------------------------------------------------------------
# gamma_N scan
# ----------------------------------------------------------------------------------------


class GammaScanner:
    """Tests every state whose compatible-rotation census fits the cap, and remembers."""

    def __init__(self, cap: int = 30_000):
        self.cap = cap
        self.seen = set()
        self.tested = 0
        self.skipped = 0
        self.hist = Counter()
        self.hits = []

    def test(self, state, provenance):
        key = canon_state(state)
        if key in self.seen:
            return None
        self.seen.add(key)
        if census_size(state) > self.cap:
            self.skipped += 1
            return None
        res = gamma_N_factorial_n(state, cap_rotations=self.cap, keep_accepting=False)
        if res["status"] != "OK":
            self.skipped += 1
            return None
        self.tested += 1
        md = res["minimum_defect"]
        self.hist[md] += 1
        if md == 0:
            hit = {"words": list(state), "minimum_defect": 0,
                   "census": res["expected_cases"], "provenance": provenance}
            self.hits.append(hit)
            return hit
        return None


# ----------------------------------------------------------------------------------------
# replay certificate (T-S3): the retraction check for one SPLIT
# ----------------------------------------------------------------------------------------


def verify_split(parent, child, record) -> bool:
    """Machine check that ``child`` really is a SPLIT of ``parent``.

    Substituting ``t -> lam`` in every relator of ``child`` must return, as a multiset of
    canonical cyclic words, exactly ``parent`` plus one extra copy of the rotated relator
    ``R'`` (the definition relator ``D = t u v`` retracts onto ``R' = lam u v``).
    """
    t, lam = record["t"], record["lam"]
    it, ilam = inv_letter(t), inv_letter(lam)
    back = []
    for w in child:
        s = "".join(lam if c == t else (ilam if c == it else c) for c in w)
        s = cyc_reduce(s)
        if s:
            back.append(canon_cyclic(s))
    base = inv_word(parent[record["relator"]]) if record["invert"] else parent[record["relator"]]
    r2 = rot_word(base, record["rot"])
    want = sorted([canon_cyclic(w) for w in parent] + [canon_cyclic(r2)])
    return sorted(back) == want


def verify_chain(root, trace) -> bool:
    state = root
    for step in trace:
        got = split_apply(state, step["relator"], step["invert"], step["rot"],
                          [tuple(p) for p in step["positions"]], step["t"])
        if got is None:
            return False
        child, rec = got
        if not verify_split(state, child, rec):
            return False
        state = child
    return True


# ----------------------------------------------------------------------------------------
# the search
# ----------------------------------------------------------------------------------------


def beam_search(root, rng, scanner, mode="tiebreak", beam=40, depth=18,
                max_children=260, deadline=None, provenance="?"):
    """Stochastic beam search with a plateau-aware cost.  Returns a result dict."""
    frontier = [(cost(root, mode), root, [])]
    seen = {canon_state(root)}
    best = (cost(root, mode), root, [])
    nodes = 0
    scanner.test(root, provenance + "|root")
    for d in range(depth):
        if deadline is not None and time.time() > deadline:
            return {"status": "TIMEOUT", "best_cost": list(best[0]), "nodes": nodes,
                    "depth_reached": d}
        pool = []
        for _c, st, tr in frontier:
            for child, rec in split_children(st, rng, max_children=max_children):
                nodes += 1
                key = canon_state(child)
                if key in seen:
                    continue
                seen.add(key)
                hit = scanner.test(child, f"{provenance}|d{d + 1}")
                if hit is not None:
                    return {"status": "GAMMA0", "hit": hit, "trace": tr + [rec],
                            "nodes": nodes, "depth_reached": d + 1}
                if is_cubic(child):
                    return {"status": "CUBIC", "words": list(child),
                            "trace": tr + [rec], "nodes": nodes, "depth_reached": d + 1}
                pool.append((cost(child, mode), child, tr + [rec]))
            if deadline is not None and time.time() > deadline:
                break
        if not pool:
            return {"status": "DEAD_END", "best_cost": list(best[0]), "nodes": nodes,
                    "depth_reached": d}
        pool.sort(key=lambda e: (e[0], rng.random()))
        if pool[0][0] < best[0]:
            best = pool[0]
        frontier = pool[:beam]
    return {"status": "EXHAUSTED_DEPTH", "best_cost": list(best[0]), "nodes": nodes,
            "depth_reached": depth}


# ----------------------------------------------------------------------------------------
# ladder generation (calibration)
# ----------------------------------------------------------------------------------------


def random_ac_trivial(rng, total_length: int = 13, steps: int = 60, min_len: int = 4):
    """A random AC-trivial rank-2 presentation of the given total length.

    Random AC1/AC2/AC3 walk from the standard presentation, so AC-triviality is by
    construction; matched to AK(3) by total length 13 with both relators of length >= 4,
    which triangulates to rank 9 with sum|delta| = 14 exactly as AK(3) does.
    """
    w = ["x", "y"]
    for _ in range(steps):
        m = rng.randrange(2)
        o = 1 - m
        t = rng.random()
        if t < 0.2:
            w[m] = inv_word(w[m])
        elif t < 0.7:
            cand = cyc_reduce(free_reduce(w[m] + w[o]))
            if cand and len(cand) + len(w[o]) <= total_length + 4:
                w[m] = cand
        else:
            u = rng.choice(["x", "y", "X", "Y"])
            cand = cyc_reduce(free_reduce(u + w[m] + inv_word(u)))
            if cand and len(cand) + len(w[o]) <= total_length + 4:
                w[m] = cand
        if not w[m]:
            return None
    if len(w[0]) + len(w[1]) != total_length:
        return None
    if min(len(w[0]), len(w[1])) < min_len:
        return None
    return tuple(w)


# ----------------------------------------------------------------------------------------
# drivers
# ----------------------------------------------------------------------------------------


def _emit(path, row):
    if path:
        with open(path, "a") as fh:
            fh.write(json.dumps(row) + "\n")
            fh.flush()


def run_roots(sources, args, tag):
    """Run the search over triangulations of each source presentation."""
    rng = random.Random(args.seed)
    scanner = GammaScanner(cap=args.gamma_cap)
    deadline = time.time() + args.budget
    out = args.out
    results = []
    solved = 0
    attempts = 0
    for si, src in enumerate(sources):
        for ri in range(args.roots_per_source):
            if time.time() > deadline:
                break
            root = triangulate(src, rng)
            if root is None:
                continue
            attempts += 1
            prov = f"{tag}|src{si}|root{ri}"
            res = beam_search(root, rng, scanner, mode=args.mode, beam=args.beam,
                              depth=args.depth, max_children=args.max_children,
                              deadline=min(deadline, time.time() + args.per_root),
                              provenance=prov)
            res.update(source=list(src), root=list(root), provenance=prov,
                       mode=args.mode, rank_root=len(root))
            if res["status"] == "CUBIC":
                solved += 1
                ok = verify_chain(root, res["trace"])
                res["chain_verified"] = ok
                res["trivial_group"] = is_trivial_group(
                    tuple(res["words"]), generators=gens_of(res["words"]))["trivial"]
                g = gamma_N_factorial_n(tuple(res["words"]),
                                        cap_rotations=200_000, keep_accepting=False)
                res["gamma"] = {"status": g["status"],
                                "minimum_defect": g["minimum_defect"],
                                "census": g["expected_cases"]}
                print(f"  *** CUBIC {prov}: {res['words']} verified={ok} "
                      f"gamma={res['gamma']}", flush=True)
            if res["status"] == "GAMMA0":
                ok = verify_chain(root, res["trace"])
                res["chain_verified"] = ok
                print(f"  *** GAMMA_N=0 HIT {prov}: {res['hit']['words']} "
                      f"verified={ok}", flush=True)
            results.append(res)
            _emit(out, res)
        if time.time() > deadline:
            break
    summary = {"kind": "summary", "tag": tag, "attempts": attempts, "solved": solved,
               "mode": args.mode, "beam": args.beam, "depth": args.depth,
               "gamma_tested": scanner.tested, "gamma_skipped": scanner.skipped,
               "gamma_hist": dict(scanner.hist), "gamma_hits": scanner.hits,
               "best_costs": sorted(r.get("best_cost", [0])[0] for r in results)[:10],
               "seed": args.seed}
    _emit(out, summary)
    print(json.dumps({k: v for k, v in summary.items() if k != "gamma_hits"}), flush=True)
    print(f"GAMMA0 HITS: {len(scanner.hits)}", flush=True)
    for h in scanner.hits:
        print("  HIT", h, flush=True)
    return summary


def cmd_selftest(args):
    rng = random.Random(1)
    root = triangulate(AK3, rng)
    assert root and is_triangular(root) and is_nondegenerate(root) and is_balanced(root)
    assert len(root) == 9, len(root)
    m = multiplicities(root)
    assert sum(m.values()) == 27
    assert sum(abs(v - 3) for v in m.values()) == 14, m
    # S4 Sec 6's published triangulation reproduces the published numbers
    pub = ("pYX", "qXP", "ryQ", "rXY", "sXX", "tXS", "uyT", "vyU", "vYY")
    mp = multiplicities(pub)
    assert mp["x"] == 6 and mp["y"] == 7 and all(mp[g] == 2 for g in "pqrsuv")
    assert sum(abs(v - 3) for v in mp.values()) == 14
    assert is_trivial_group(pub, generators=gens_of(pub))["trivial"]
    # SPLIT legality + replay certificate on 200 random children
    n = 0
    for _ in range(40):
        st = triangulate(AK3, rng)
        if st is None:
            continue
        for child, rec in split_children(st, rng, max_children=5):
            assert verify_split(st, child, rec), (st, child, rec)
            assert is_triangular(child) and is_nondegenerate(child) and is_balanced(child)
            assert len(child) == len(st) + 1
            n += 1
    assert n >= 100, n
    # occurrence bookkeeping of S4 Sec 5.3
    st = triangulate(AK3, rng)
    for child, rec in split_children(st, rng, max_children=12):
        d0, d1 = delta(st), delta(child)
        k = rec["k"]
        gl, gu, gv, t = rec["lam"].lower(), rec["u"].lower(), rec["v"].lower(), rec["t"]
        pred = dict(d0)
        pred[gl] = pred.get(gl, 0) - k
        pred[gu] = pred.get(gu, 0) + 1
        pred[gv] = pred.get(gv, 0) + 1
        pred[t] = k - 2
        assert pred == d1, (pred, d1, rec)
    # gamma oracle agrees with the published AK(3) value, and a chord triangulation
    # preserves it (S3_AUDIT Lemma S3')
    g0 = gamma_N_factorial_n(AK3, cap_rotations=200_000, keep_accepting=False)
    g1 = gamma_N_factorial_n(pub, cap_rotations=200_000, keep_accepting=False)
    assert g0["minimum_defect"] == 4 and g1["minimum_defect"] == 4, (g0, g1)
    # ladder generator produces matched-difficulty inputs
    made = 0
    for _ in range(4000):
        p = random_ac_trivial(rng)
        if p is None:
            continue
        r = triangulate(p, rng)
        if r is None or len(r) != 9:
            continue
        if sum(abs(v - 3) for v in multiplicities(r).values()) != 14:
            continue          # needs m_x, m_y >= 3 in the source; filtered, not asserted
        assert is_trivial_group(r, generators=gens_of(r))["trivial"], r
        made += 1
        if made >= 5:
            break
    assert made >= 5, made
    # a tiny live search, same code path as the real runs
    sc = GammaScanner(cap=args.gamma_cap)
    res = beam_search(triangulate(AK3, rng), rng, sc, mode="tiebreak", beam=6, depth=3,
                      max_children=30, deadline=time.time() + 20, provenance="selftest")
    print("selftest search:", res["status"], "nodes", res["nodes"],
          "gamma tested", sc.tested, "hist", dict(sc.hist))
    print("SELFTEST OK")
    return 0


def cmd_ak3(args):
    return run_roots([AK3], args, "ak3")


def cmd_ladder(args):
    rng = random.Random(args.seed ^ 0x5EED)
    srcs = []
    seen = set()
    tries = 0
    while len(srcs) < args.ladder and tries < 400_000:
        tries += 1
        p = random_ac_trivial(rng)
        if p is None or p in seen:
            continue
        r = triangulate(p, random.Random(rng.randrange(1 << 30)))
        if r is None or len(r) != 9:
            continue
        if sum(abs(v - 3) for v in multiplicities(r).values()) != 14:
            continue
        seen.add(p)
        srcs.append(p)
    print(f"ladder: {len(srcs)} matched-difficulty AC-trivial sources "
          f"(rank-2, L=13, triangulate to rank 9, sum|delta|=14)", flush=True)
    return run_roots(srcs, args, "ladder")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", choices=["selftest", "ak3", "ladder"])
    ap.add_argument("--budget", type=float, default=60.0, help="wall-clock seconds")
    ap.add_argument("--per-root", type=float, default=25.0)
    ap.add_argument("--roots-per-source", type=int, default=40)
    ap.add_argument("--ladder", type=int, default=12)
    ap.add_argument("--mode", default="tiebreak",
                    choices=["sumdelta", "tiebreak", "lex", "spread"])
    ap.add_argument("--beam", type=int, default=40)
    ap.add_argument("--depth", type=int, default=18)
    ap.add_argument("--max-children", type=int, default=260)
    ap.add_argument("--gamma-cap", type=int, default=30_000)
    ap.add_argument("--seed", type=int, default=20260804)
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    if args.out:
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
    return {"selftest": cmd_selftest, "ak3": cmd_ak3, "ladder": cmd_ladder}[args.cmd](args) and 0


if __name__ == "__main__":
    sys.exit(main() or 0)
