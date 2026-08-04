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
import gzip
import json
import os
import random
import sys
import time
from collections import Counter
from itertools import combinations
from math import factorial

import numpy as np

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
                max_children=260, deadline=None, provenance="?", diversity=0.25,
                deep_pool=None, deep_threshold=4, pool_sink=None):
    """Stochastic beam search with a plateau-aware cost.

    ``diversity`` is the fraction of each beam filled by a uniform random sample of the
    non-best children rather than by the cost ranking.  That is the escape from the T-S11
    parity plateau: leaving ``sum|delta| = 2`` provably requires a temporarily
    cost-increasing move, so a pure ranking beam can never do it.

    ``deep_pool`` collects near-cubic states (``sum|delta| <= deep_threshold``) for the
    post-hoc high-cap gamma_N scan; the in-search scan uses ``scanner``'s own small cap,
    because a near-cubic state at rank N has census 2^N and cannot be tested at every node.
    """
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
                c = cost(child, mode)
                sd = sum(abs(x) for x in delta(child).values())
                if sd <= deep_threshold:
                    if deep_pool is not None:
                        deep_pool.append((sd, len(child), child,
                                          f"{provenance}|d{d + 1}"))
                    if pool_sink is not None:
                        pool_sink({"words": list(child), "sum_delta": sd,
                                   "rank": len(child), "census": census_size(child),
                                   "provenance": f"{provenance}|d{d + 1}",
                                   "root": list(root), "trace": tr + [rec]})
                pool.append((c, child, tr + [rec]))
            if deadline is not None and time.time() > deadline:
                break
        if not pool:
            return {"status": "DEAD_END", "best_cost": list(best[0]), "nodes": nodes,
                    "depth_reached": d}
        pool.sort(key=lambda e: (e[0], rng.random()))
        if pool[0][0] < best[0]:
            best = pool[0]
        n_rank = max(1, int(beam * (1.0 - diversity)))
        chosen = pool[:n_rank]
        rest = pool[n_rank:]
        if rest and len(chosen) < beam:
            chosen += rng.sample(rest, min(beam - len(chosen), len(rest)))
        frontier = chosen
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
    search_deadline = time.time() + args.budget
    deadline = search_deadline
    out = args.out
    results = []
    deep_pool = []
    solved = 0
    attempts = 0
    pool_fh = None
    pool_written = 0
    if args.pool_out:
        os.makedirs(os.path.dirname(args.pool_out), exist_ok=True)
        pool_fh = gzip.open(args.pool_out, "at")

    def pool_sink(row):
        nonlocal pool_written
        if pool_fh is None:
            return
        pool_fh.write(json.dumps(row) + "\n")
        pool_written += 1
        if pool_written % 2000 == 0:
            pool_fh.flush()
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
                              provenance=prov, diversity=args.diversity,
                              deep_pool=deep_pool, deep_threshold=args.deep_threshold,
                              pool_sink=pool_sink if pool_fh is not None else None)
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
            res.pop("trace", None) if res["status"] not in ("CUBIC", "GAMMA0") else None
            results.append(res)
            _emit(out, res)
        if time.time() > deadline:
            break
    if pool_fh is not None:
        pool_fh.flush()
        pool_fh.close()
        print(f"pool persisted: {pool_written} near-cubic rows -> {args.pool_out}",
              flush=True)

    # --- post-hoc deep gamma_N scan on the near-cubic states reached -------------------
    deep = {}
    for sd, rank, st, prov in deep_pool:
        key = canon_state(st)
        if key not in deep:
            deep[key] = (sd, rank, st, prov)
    ordered = sorted(deep.values(), key=lambda e: (e[0], census_size(e[2])))
    deep_deadline = time.time() + args.deep_budget
    deep_tested = 0
    deep_hist = Counter()
    for sd, rank, st, prov in ordered:
        if time.time() > deep_deadline or deep_tested >= args.deep_max:
            break
        if census_size(st) > args.deep_cap:
            continue
        r = gamma_N_factorial_n(st, cap_rotations=args.deep_cap, keep_accepting=False)
        if r["status"] != "OK":
            continue
        deep_tested += 1
        deep_hist[r["minimum_defect"]] += 1
        if r["minimum_defect"] == 0:
            hit = {"words": list(st), "minimum_defect": 0,
                   "census": r["expected_cases"], "provenance": prov + "|deep",
                   "sum_delta": sd, "rank": rank}
            scanner.hits.append(hit)
            print(f"  *** GAMMA_N=0 DEEP HIT: {hit}", flush=True)
            _emit(out, {"kind": "deep_hit", **hit})

    summary = {"kind": "summary", "tag": tag, "attempts": attempts, "solved": solved,
               "mode": args.mode, "beam": args.beam, "depth": args.depth,
               "diversity": args.diversity,
               "gamma_tested": scanner.tested, "gamma_skipped": scanner.skipped,
               "gamma_hist": dict(scanner.hist), "gamma_hits": scanner.hits,
               "deep_pool_unique": len(deep), "deep_tested": deep_tested,
               "deep_hist": dict(deep_hist), "deep_cap": args.deep_cap,
               "best_costs": sorted(r.get("best_cost", [99])[0] for r in results)[:10],
               "min_sum_delta_reached": min([e[0] for e in ordered], default=None),
               "pool_written": pool_written, "pool_out": args.pool_out,
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
    # fast kernel must agree with the audited oracle EXACTLY, on cubic and near-cubic
    probes = [("kAe", "Xgb", "aXH", "bxH", "cYY", "ydJ", "eid", "IfC", "gKF", "hAe",
               "igb", "jfC", "kdJ"),
              ("Xbc", "hEg", "aYX", "JbA", "YCk", "dIk", "eYj", "xfD", "gfi", "hfD",
               "ibA", "jCh", "kEg"),
              pub, AK3]
    rngp = random.Random(7)
    st = triangulate(AK3, rngp)
    for child, _rec in split_children(st, rngp, max_children=8):
        probes.append(child)
        for gc, _r2 in split_children(child, rngp, max_children=4):
            probes.append(gc)
    nchk = 0
    for w in probes:
        if census_size(w) > 300_000:
            continue
        o = gamma_N_factorial_n(w, cap_rotations=300_000, keep_accepting=False)
        if o["status"] != "OK":
            continue
        f = fast_min_defect(w)
        assert f == o["minimum_defect"], (w, f, o["minimum_defect"])
        nchk += 1
    assert nchk >= 8, nchk
    print(f"fast kernel agrees with the oracle on {nchk} states (numba={_HAVE_NUMBA})")
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


# ----------------------------------------------------------------------------------------
# fast EXACT census for the near-cubic regime (numba), validated against the oracle
# ----------------------------------------------------------------------------------------

try:
    from numba import njit
    _HAVE_NUMBA = True
except Exception:                                             # pragma: no cover
    _HAVE_NUMBA = False

    def njit(*a, **k):
        def deco(f):
            return f
        return deco


@njit(cache=True)
def _census_kernel(A, cand_pos, cand_neg, germ_off, germ_ncand, germ_k,
                   n_darts, nA, nC, twoL):
    """Exact minimum defect over every compatible rotation system.

    Mixed-radix enumeration over the per-germ cyclic orders.  ``cand_pos``/``cand_neg``
    hold, for positive germ ``i`` and candidate ``j``, the ``germ_k[i]`` darts of the
    positive resp. negative end, flattened at ``germ_off[i] + j * germ_k[i]``.
    Returns ``(min_defect, argmin_encoded, n_enumerated)``.
    """
    ng = germ_ncand.shape[0]
    total = 1
    for i in range(ng):
        total *= germ_ncand[i]
    C = np.empty(n_darts, dtype=np.int64)
    seen = np.empty(n_darts, dtype=np.uint8)
    best = 1 << 60
    best_idx = -1
    for combo in range(total):
        rem = combo
        for i in range(ng):
            nc = germ_ncand[i]
            j = rem % nc
            rem //= nc
            k = germ_k[i]
            base = germ_off[i] + j * k
            for t in range(k):
                C[cand_pos[base + t]] = cand_pos[base + (t + 1) % k]
                C[cand_neg[base + t]] = cand_neg[base + (t + 1) % k]
        for d in range(n_darts):
            seen[d] = 0
        nAC = 0
        for start in range(n_darts):
            if seen[start] == 1:
                continue
            nAC += 1
            cur = start
            while seen[cur] == 0:
                seen[cur] = 1
                cur = A[C[cur]]
        defect = nA - nC + twoL - nAC
        if defect < best:
            best = defect
            best_idx = combo
            if best == 0:
                return best, best_idx, combo + 1
    return best, best_idx, total


def fast_min_defect(state):
    """Exact ``min_C defect(C)`` via the numba kernel.  Same value as
    ``gamma_N_factorial_n(...)['minimum_defect']`` — asserted in ``selftest``."""
    from experiments.stable_ac.fable.neuwirth_rank_n import build_link_n
    gens = gens_of(state)
    data = build_link_n(state, gens)
    B = data.B
    pos_germs = [2 * k for k in range(len(gens)) if data.vertex_darts[2 * k]]
    cand_pos, cand_neg, germ_off, germ_ncand, germ_k = [], [], [], [], []
    from itertools import permutations as _perm
    for g in pos_germs:
        darts = data.vertex_darts[g]
        k = len(darts)
        orders = [(darts[0],) + p for p in _perm(darts[1:])]
        germ_off.append(len(cand_pos))
        germ_ncand.append(len(orders))
        germ_k.append(k)
        for o in orders:
            neg = tuple(B[p] for p in reversed(o))
            cand_pos.extend(o)
            cand_neg.extend(neg)
    best, idx, enumerated = _census_kernel(
        np.asarray(data.A, dtype=np.int64),
        np.asarray(cand_pos, dtype=np.int64), np.asarray(cand_neg, dtype=np.int64),
        np.asarray(germ_off, dtype=np.int64), np.asarray(germ_ncand, dtype=np.int64),
        np.asarray(germ_k, dtype=np.int64),
        data.n_darts, data.n_occurrences, len(data.present_germs),
        2 * data.link_components)
    return int(best)


def cmd_decide(args):
    """Decide EVERY persisted near-cubic state by exact census; report the histogram."""
    seen = set()
    rows = []
    for path in args.pool_in.split(","):
        opener = gzip.open if path.endswith(".gz") else open
        with opener(path, "rt") as fh:
            for line in fh:
                if not line.strip():
                    continue
                d = json.loads(line)
                st = tuple(d["words"])
                key = canon_state(st)
                if key in seen:
                    continue
                seen.add(key)
                rows.append(d)
    print(f"pool: {len(rows)} distinct near-cubic states (deduped on canonical cyclic form)",
          flush=True)
    by_rank = Counter((r["rank"], r["sum_delta"]) for r in rows)
    print("  (rank, sum|delta|) ->", dict(sorted(by_rank.items())), flush=True)

    out = args.decide_out
    if out:
        os.makedirs(os.path.dirname(out), exist_ok=True)
    fh = gzip.open(out, "wt") if out else None
    hist = Counter()
    hist_by_sd = {}
    hist_by_src = {}
    hits = []
    decided = 0
    skipped = 0
    t0 = time.time()
    deadline = t0 + args.decide_budget
    for r in rows:
        if time.time() > deadline:
            break
        st = tuple(r["words"])
        if census_size(st) > args.deep_cap:
            skipped += 1
            continue
        d = fast_min_defect(st)
        decided += 1
        hist[d] += 1
        hist_by_sd.setdefault(r["sum_delta"], Counter())[d] += 1
        if args.by_source:
            prov = r.get("provenance", "")
            src = next((t for t in prov.split("|") if t.startswith("src")), "src?")
            hist_by_src.setdefault(src, Counter())[d] += 1
        if fh is not None:
            fh.write(json.dumps({"words": r["words"], "rank": r["rank"],
                                 "sum_delta": r["sum_delta"], "census": r["census"],
                                 "minimum_defect": d,
                                 "provenance": r.get("provenance")}) + "\n")
        if d == 0:
            print("\n" + "=" * 70, flush=True)
            print("*** GAMMA_N = 0 HIT — THICKENABLE MEMBER OF AK(3)'s STABLE CLASS ***",
                  flush=True)
            print(json.dumps(r), flush=True)
            print("=" * 70 + "\n", flush=True)
            hits.append(r)
            if fh is not None:
                fh.flush()
            if out:
                with open(out.replace(".jsonl.gz", "_HIT.json"), "w") as hf:
                    json.dump(r, hf, indent=1)
        if decided % 2000 == 0:
            print(f"  decided {decided}/{len(rows)}  {time.time() - t0:.0f}s  "
                  f"hist={dict(sorted(hist.items()))}", flush=True)
    if fh is not None:
        fh.close()
    summary = {"kind": "decide_summary", "pool_rows": len(rows), "decided": decided,
               "skipped_over_cap": skipped, "elapsed_s": round(time.time() - t0, 1),
               "defect_histogram": dict(sorted(hist.items())),
               "by_sum_delta": {k: dict(sorted(v.items()))
                                for k, v in sorted(hist_by_sd.items())},
               "by_source": {k: dict(sorted(v.items()))
                             for k, v in sorted(hist_by_src.items())},
               "gamma0_hits": len(hits), "deep_cap": args.deep_cap}
    print(json.dumps(summary), flush=True)
    if out:
        with open(out.replace(".jsonl.gz", "_summary.json"), "w") as sf:
            json.dump(summary, sf, indent=1)
    return summary


def triangulate_traced(words, rng, max_rank: int = 26):
    """As ``triangulate`` but returns every intermediate presentation."""
    words = tuple(words)
    used = {c.lower() for w in words for c in w}
    fresh = [c for c in ALPHABET if c not in used]
    steps = [words]
    while any(len(w) >= 4 for w in words):
        if not fresh or len(words) >= max_rank:
            return None
        cand = [i for i, w in enumerate(words) if len(w) >= 4]
        i = rng.choice(cand)
        k = rng.randrange(len(words[i]))
        words = chord_refine(words, i, k, fresh.pop(0),
                             rng.choice(["pos", "neg"]),
                             rng.choice(["prefix", "suffix"]))
        steps.append(words)
    if not (is_triangular(words) and is_nondegenerate(words) and is_balanced(words)):
        return None
    return steps


def thickenable_sources(rng, n, total_length=13, min_len=4, cap=200_000,
                        want_defect=0, tries_max=400_000, deadline=None):
    """Random AC-trivial rank-2 presentations with a PRESCRIBED rank-2 defect.

    ``want_defect = 0`` gives the positive control: presentations that provably HAVE a
    thickenable member (themselves).  By `S3_AUDIT` Lemma S3' every chord triangulation of
    such a source is still gamma_N = 0, so the rank-9 root of the pipeline is thickenable
    by construction -- which is exactly what makes this a positive control for the
    rank-12/13 region.
    """
    out, seen, tries = [], set(), 0
    while len(out) < n and tries < tries_max:
        tries += 1
        if deadline is not None and time.time() > deadline:
            break
        p = random_ac_trivial(rng, total_length=total_length, min_len=min_len)
        if p is None or p in seen:
            continue
        seen.add(p)
        g = gamma_N_factorial_n(p, cap_rotations=cap, keep_accepting=False)
        if g["status"] != "OK" or g["minimum_defect"] != want_defect:
            continue
        r = triangulate(p, rng)
        if r is None or len(r) != 9:
            continue
        if sum(abs(v - 3) for v in multiplicities(r).values()) != 14:
            continue
        out.append(p)
    return out


def cmd_control(args):
    """POSITIVE CONTROL: run the identical pipeline on rank-2 sources with gamma_N = 0.

    Matched to AK(3) on every axis the pipeline sees: AC-trivial, rank 2, total length 13,
    both relators >= 4 so the chord triangulation lands at rank 9 with sum|delta| = 14.
    The only difference is the rank-2 defect (0 instead of 4).
    """
    rng = random.Random(args.seed)
    srcs = thickenable_sources(rng, args.ladder, want_defect=args.want_defect,
                               deadline=time.time() + args.source_budget)
    print(f"control: {len(srcs)} AC-trivial rank-2 sources with defect "
          f"{args.want_defect}, L=13, -> rank-9 roots with sum|delta|=14", flush=True)
    for p in srcs:
        print("   source", p, flush=True)
    if not srcs:
        print("NO SOURCES FOUND", flush=True)
        return {}
    return run_roots(srcs, args, f"control{args.want_defect}")


def cmd_chaintrace(args):
    """Track gamma_N along the whole chain: base -> chord refinements -> SPLITs.

    Two live checks in one: (a) S3/`S3_AUDIT` Lemma S3' predicts the defect is CONSTANT
    across every chord refinement; (b) any change along the SPLIT tail is attributable to
    SPLIT alone.
    """
    rng = random.Random(args.seed)
    rows = []
    deadline = time.time() + args.budget
    bases = [("AK3", AK3)]
    for i, p in enumerate(thickenable_sources(rng, args.ladder, want_defect=0,
                                              deadline=time.time() + args.source_budget)):
        bases.append((f"thick{i}", p))
    for name, base in bases:
        for rep in range(args.roots_per_source):
            if time.time() > deadline:
                break
            steps = triangulate_traced(base, rng)
            if steps is None or len(steps[-1]) != 9:
                continue
            tri_defects = []
            ok_tri = True
            for st in steps:
                if census_size(st) > args.deep_cap:
                    ok_tri = False
                    tri_defects.append(None)
                    continue
                tri_defects.append(fast_min_defect(st))
            state = steps[-1]
            split_defects = []
            trace = []
            for d in range(args.split_steps):
                kids = split_children(state, rng, max_children=args.max_children)
                if not kids:
                    break
                # follow the cost-guided child, as the real search does
                kids.sort(key=lambda e: (cost(e[0], args.mode), rng.random()))
                state, rec = kids[0]
                trace.append(rec)
                split_defects.append(fast_min_defect(state)
                                     if census_size(state) <= args.deep_cap else None)
            row = {"base_name": name, "base": list(base), "rank2_defect": tri_defects[0],
                   "chord_defects": tri_defects,
                   "chord_constant": (ok_tri and len(set(tri_defects)) == 1),
                   "root": list(steps[-1]), "split_defects": split_defects,
                   "final_rank": len(state),
                   "final_sum_delta": sum(abs(v - 3)
                                          for v in multiplicities(state).values())}
            rows.append(row)
            _emit(args.out, row)
            print(f"  {name} rep{rep}: chord {tri_defects} constant="
                  f"{row['chord_constant']} | SPLIT {split_defects}", flush=True)
    n_const = sum(1 for r in rows if r["chord_constant"])
    drops = [r for r in rows if r["split_defects"] and r["rank2_defect"] is not None
             and min([d for d in r["split_defects"] if d is not None],
                     default=99) < r["rank2_defect"]]
    rises = [r for r in rows if r["split_defects"] and r["rank2_defect"] is not None
             and max([d for d in r["split_defects"] if d is not None],
                     default=-1) > r["rank2_defect"]]
    summary = {"kind": "chaintrace_summary", "chains": len(rows),
               "chord_defect_constant": f"{n_const}/{len(rows)}",
               "split_chains_that_lowered": len(drops),
               "split_chains_that_raised": len(rises),
               "by_base": {n: [r["split_defects"] for r in rows if r["base_name"] == n]
                           for n in {r["base_name"] for r in rows}}}
    _emit(args.out, summary)
    print(json.dumps({k: v for k, v in summary.items() if k != "by_base"}), flush=True)
    for n, v in summary["by_base"].items():
        print(f"  {n}: {v}", flush=True)
    return summary


def cmd_flips(args):
    """SPLIT flip census, in the format of `S6_MOVE_CLASSIFICATION.md` Sec 1.

    For a corpus of triangular states (triangulations of short rank-2 presentations, plus
    triangulations of AK(3) itself), apply single SPLITs and record whether `gamma_N = 0`
    is created or destroyed.  This decides whether the SPLIT route can carry a certificate
    at all: if SPLIT never creates, the whole cubic route is a gamma_N no-op and the search
    can only ever be about the normal form, never about settling AK(3).
    """
    rng = random.Random(args.seed)
    deadline = time.time() + args.budget
    table = Counter()          # (parent_gamma0, child_gamma0) -> count
    per_k = Counter()
    parents_done = 0
    creates, destroys = [], []
    hist_pairs = Counter()

    def gam(st, cap):
        r = gamma_N_factorial_n(st, cap_rotations=cap, keep_accepting=False)
        return r["minimum_defect"] if r["status"] == "OK" else None

    def ac2_children(state, rng, limit):
        """CONTROL ARM: a general AC2 slide r_i <- freered(r_i r_j^{+-1}).

        Leaves the triangular world (lengths become 6-2k), which is exactly the point:
        S6 measures AC2 as the only creator of thickenability, so this arm calibrates
        whether the instrument can see a creation at all on THIS corpus.  Without it a
        'SPLIT never creates' null bounds nothing (lesson
        `calibrate-one-sided-hunts-on-a-positive-ladder.md`).
        """
        out = []
        n = len(state)
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                for eps in (1, -1):
                    other = state[j] if eps == 1 else inv_word(state[j])
                    w = cyc_reduce(free_reduce(state[i] + other))
                    if not w:
                        continue
                    child = tuple(list(state[:i]) + [w] + list(state[i + 1:]))
                    if any(not x for x in child):
                        continue
                    out.append((child, {"arm": "ac2", "i": i, "j": j, "eps": eps}))
        rng.shuffle(out)
        return out[:limit]

    # corpus of short rank-2 sources, triangulated (cheap census), both gamma classes
    sources = []
    seen = set()
    tries = 0
    while len(sources) < args.corpus and tries < 400_000 and time.time() < deadline:
        tries += 1
        p = random_ac_trivial(rng, total_length=args.source_length, min_len=3)
        if p is None or p in seen:
            continue
        seen.add(p)
        sources.append(p)
    if args.include_ak3:
        sources.append(AK3)
    print(f"flip census: {len(sources)} sources (length {args.source_length}"
          f"{', + AK(3)' if args.include_ak3 else ''})", flush=True)

    arms = {"split": Counter(), "ac2": Counter()}
    arm_pairs = {"split": Counter(), "ac2": Counter()}
    for src in sources:
        if time.time() > deadline:
            break
        root = triangulate(src, rng)
        if root is None or census_size(root) > args.deep_cap:
            continue
        d0 = gam(root, args.deep_cap)
        if d0 is None:
            continue
        parents_done += 1
        batches = [("split", split_children(root, rng, max_children=args.flip_children)),
                   ("ac2", ac2_children(root, rng, args.flip_children))]
        for arm, kids in batches:
            for child, rec in kids:
                if time.time() > deadline:
                    break
                if census_size(child) > args.deep_cap:
                    continue
                d1 = gam(child, args.deep_cap)
                if d1 is None:
                    continue
                arms[arm][(d0 == 0, d1 == 0)] += 1
                arm_pairs[arm][(d0, d1)] += 1
                if arm == "split":
                    table[(d0 == 0, d1 == 0)] += 1
                    hist_pairs[(d0, d1)] += 1
                    per_k[(rec.get("k"), d0 == 0, d1 == 0)] += 1
                if d0 != 0 and d1 == 0:
                    row = {"arm": arm, "parent": list(root), "child": list(child),
                           "record": rec, "parent_defect": d0}
                    (creates if arm == "split" else creates).append(row)
                    print(f"  *** {arm.upper()} CREATED gamma_N=0: {list(child)} "
                          f"from {list(root)}", flush=True)
                    _emit(args.out, {"kind": "create", **row})
                if d0 == 0 and d1 != 0 and arm == "split":
                    destroys.append({"parent": list(root), "child": list(child),
                                     "child_defect": d1})

    def arm_summary(a):
        t = arms[a]
        return {
            "pairs": sum(t.values()),
            "thickenable_parent_pairs": sum(v for (p, _c), v in t.items() if p),
            "nonthickenable_parent_pairs": sum(v for (p, _c), v in t.items() if not p),
            "created": sum(v for (p, c), v in t.items() if (not p) and c),
            "destroyed": sum(v for (p, c), v in t.items() if p and (not c)),
            "preserved_0": t[(True, True)], "preserved_pos": t[(False, False)],
            "defect_pairs": {f"{p}->{c}": v for (p, c), v in sorted(arm_pairs[a].items())},
        }

    summary = {
        "kind": "flip_summary",
        "sources": len(sources), "parents_measured": parents_done,
        "split": arm_summary("split"),
        "ac2_control": arm_summary("ac2"),
        "split_per_k": {f"k={k},{p}->{c}": v for (k, p, c), v in sorted(
            per_k.items(), key=lambda e: str(e[0]))},
        "source_length": args.source_length, "seed": args.seed,
    }
    _emit(args.out, summary)
    print(json.dumps(summary), flush=True)
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", choices=["selftest", "ak3", "ladder", "flips", "decide",
                                    "control", "chaintrace"])
    ap.add_argument("--corpus", type=int, default=120)
    ap.add_argument("--source-length", type=int, default=8)
    ap.add_argument("--flip-children", type=int, default=40)
    ap.add_argument("--include-ak3", action="store_true")
    ap.add_argument("--budget", type=float, default=60.0, help="wall-clock seconds")
    ap.add_argument("--per-root", type=float, default=25.0)
    ap.add_argument("--roots-per-source", type=int, default=40)
    ap.add_argument("--ladder", type=int, default=12)
    ap.add_argument("--mode", default="tiebreak",
                    choices=["sumdelta", "tiebreak", "lex", "spread"])
    ap.add_argument("--beam", type=int, default=40)
    ap.add_argument("--depth", type=int, default=18)
    ap.add_argument("--max-children", type=int, default=260)
    ap.add_argument("--diversity", type=float, default=0.25,
                    help="fraction of the beam filled at random (T-S11 plateau escape)")
    ap.add_argument("--gamma-cap", type=int, default=2_000,
                    help="in-search gamma_N census cap (kept small: cubic states have "
                         "census 2^N, so a full scan is unaffordable)")
    ap.add_argument("--deep-threshold", type=int, default=4,
                    help="collect states with sum|delta| <= this for the deep scan")
    ap.add_argument("--deep-cap", type=int, default=1_500_000)
    ap.add_argument("--deep-budget", type=float, default=120.0)
    ap.add_argument("--deep-max", type=int, default=4000)
    ap.add_argument("--pool-out", default=None,
                    help="gzipped jsonl: persist EVERY near-cubic state as it is found")
    ap.add_argument("--pool-in", default=None)
    ap.add_argument("--decide-out", default=None)
    ap.add_argument("--decide-budget", type=float, default=480.0)
    ap.add_argument("--want-defect", type=int, default=0,
                    help="rank-2 defect the control sources must have (0 = thickenable)")
    ap.add_argument("--source-budget", type=float, default=90.0)
    ap.add_argument("--split-steps", type=int, default=5)
    ap.add_argument("--by-source", action="store_true",
                    help="decide: break the histogram down per source presentation")
    ap.add_argument("--seed", type=int, default=20260804)
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    if args.out:
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
    fns = {"selftest": cmd_selftest, "ak3": cmd_ak3, "ladder": cmd_ladder,
           "flips": cmd_flips, "decide": cmd_decide,
           "control": cmd_control, "chaintrace": cmd_chaintrace}
    fns[args.cmd](args)
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
