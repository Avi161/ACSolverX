"""Recognizers, compilers and machine replay for the four-block completion rules.

Implements and *verifies* the rules stated in ``FOURBLOCK_THEORY.md``:

  F1  (four-block primitive merge)  -- proved.  If a relator's cyclic block
      tuple lies in the symmetry orbit of ``(1, b, 1, d)`` with ``|b-d| = 1``
      and the pair has |abelian_det| = 1, then ``min(|b|,|d|)`` copies of a
      single Nielsen map turn that relator into ``y^{2a} x^{+-1}`` -- a
      one-occurrence donor -- and the proved T3/T4 compiler finishes.
      The converse holds: no other four-block word is primitive.

  F3  (twin four-block row reduction) -- proved.  If both relators are
      four-block and share their y-block exponents ``(a,c)`` in matching cyclic
      positions, then one ordinary substitution move produces
      ``D = y^{-c} x^{b'-b} y^{c} x^{d'-d}``.  |det| = 1 forces
      ``|a+c| = 1`` and ``|(b'+d')-(b+d)| = 1``, so
        * if exactly one x-block differs, D is a single generator (terminal);
        * if |c| = 1, D is a consecutive BS(m,m+1) donor whose companion
          automatically has stable-letter exponent +-1, and the Britton
          preflight decides;
        * if |c| >= 2 the branch is dead by the stable-power impossibility
          lemma (N1).

Every certificate produced here is replayed from the ORIGINAL pair with
``words.replay_move`` / ``words.apply_pair`` (mixed path) plus
``two_block.replay`` for the elementary tail, and must end at ``('x','y')``.

Usage:
    PYTHONPATH=. python3 research/residual_20260909/theory/FOURBLOCK_verify.py
    PYTHONPATH=. python3 research/residual_20260909/theory/FOURBLOCK_verify.py --census
"""
from __future__ import annotations

import glob
import json
import os
import sys
from collections import Counter

from experiments.equivalence_classes.lib.words import (
    abelian_det, apply_hom, apply_pair, canon_pair, canon_rel, cyc_reduce,
    exp_sums, free_reduce, inv, replay_move, rot,
)
from experiments.search.heuristic_1k import NIELSEN
from research.supermoves_20260908 import consecutive_bs, primitive_completion, two_block
from research.supermoves_20260908.bs_preflight import donor_orientations, preflight
from research.supermoves_20260908.cheap_gates import bs_gate, one_occurrence_donor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from FOURBLOCK_mine import blocks, four_block_tuple, n_blocks, orbit, canon_tuple  # noqa: E402

ROWS_GLOB = "results/heuristic_search/ac19_final_policy_full_1k/rows_*.jsonl"
DEV_CSV = "research/residual_20260909/panels/dev.csv"

# The four Nielsen maps as (name, images); NIELSEN order is
# x->xy, x->xY, y->yx, y->yX.
MAP_NAME = {0: "x->xy", 1: "x->xY", 2: "y->yx", 3: "y->yX"}


def word_of_tuple(t):
    """y^a x^b y^c x^d as a cyclically reduced canonical word."""
    a, b, c, d = t
    p = lambda g, e: (g if e > 0 else g.upper()) * abs(e)   # noqa: E731
    return canon_rel(p("y", a) + p("x", b) + p("y", c) + p("x", d))


# --------------------------------------------------------------------------
# F1: the merge
# --------------------------------------------------------------------------

def merge_data(word):
    """How a four-block word can be merged to two blocks by one Nielsen map.

    Returns None, or a dict with

        gen        the generator whose two blocks merge ('y' or 'x')
        k          the exponent of the composite map (y -> y x^k, or x -> x y^k)
        map_index  index into NIELSEN of the elementary map applied |k| times
        merged     the resulting two-block cyclic word
        exponent   the surviving exponent of the OTHER generator
        primitive  True iff |exponent| == 1 (then ``merged`` is one-occurrence)

    Proof of the formula is in FOURBLOCK_THEORY.md section 2:
    with a = c = +-1, beta_k(y^a x^b y^c x^d) = y^a x^{b+ak} y^c x^{d+ak}
    (cyclically), so k = -a*b kills the first x-block and k = -a*d the second.
    """
    t = four_block_tuple(word)
    if t is None:
        return None
    a, b, c, d = t
    best = None
    if abs(a) == abs(c) == 1 and a == c:
        for kill_first in (True, False):
            k = -a * b if kill_first else -a * d
            if k == 0:
                continue
            e = (d - b) if kill_first else (b - d)
            cand = {"gen": "y", "k": k, "exponent": e,
                    "map_index": 2 if k > 0 else 3,       # y->yx / y->yX
                    "merged": canon_rel(("y" if a > 0 else "Y") * 2
                                        + ("x" if e > 0 else "X") * abs(e))}
            if best is None or abs(k) < abs(best["k"]):
                best = cand
    if abs(b) == abs(d) == 1 and b == d:
        for kill_first in (True, False):
            k = -b * c if kill_first else -b * a
            if k == 0:
                continue
            e = (a - c) if kill_first else (c - a)
            cand = {"gen": "x", "k": k, "exponent": e,
                    "map_index": 0 if k > 0 else 1,       # x->xy / x->xY
                    "merged": canon_rel(("x" if b > 0 else "X") * 2
                                        + ("y" if e > 0 else "Y") * abs(e))}
            if best is None or abs(k) < abs(best["k"]):
                best = cand
    if best is None:
        return None
    best["primitive"] = abs(best["exponent"]) == 1
    best["tuple"] = list(t)
    return best


def recognize_F1(pair):
    """Recognize the four-block primitive-merge rule.  O(total length)."""
    p = canon_pair(*pair)
    if abs(abelian_det(*p)) != 1:
        return None
    for index, word in enumerate(p):
        data = merge_data(word)
        if data is not None and data["primitive"]:
            return {"rule": "F1", "pair": list(p), "donor_index": index,
                    "donor": word, **data}
    return None


def compile_F1(pair, budget=100000):
    """Constructive certificate for F1: |k| Nielsen maps then the T3 compiler."""
    hit = recognize_F1(pair)
    if hit is None:
        return {"solved": False, "reason": "not_recognized", "work": 0}
    state = tuple(hit["pair"])
    images = NIELSEN[hit["map_index"]]
    states, steps = [list(state)], []
    work = 1                                   # the recognizer scan
    for _ in range(abs(hit["k"])):
        state = apply_pair(state, images)
        states.append(list(state))
        steps.append({"kind": "automorphism", "images": images})
        work += 1
    merged = canon_rel(hit["merged"])
    if merged not in state:
        return {"solved": False, "reason": "merge_missing", "work": work,
                "state": list(state), "expected": merged}
    if not one_occurrence_donor(merged):
        return {"solved": False, "reason": "not_one_occurrence", "work": work}
    tail = primitive_completion.complete(state, budget=budget, donor_word=merged)
    if not tail.get("solved"):
        return {"solved": False, "reason": "primitive_" + tail.get("reason", "?"),
                "work": work + tail.get("work", 0)}
    states.extend(s[:] for s in tail["states"][1:])
    steps.extend(tail["steps"])
    return {"solved": True, "rule": "F1", "root": list(canon_pair(*pair)),
            "nielsen_steps": abs(hit["k"]), "map": MAP_NAME[hit["map_index"]],
            "merged": merged, "states": states, "steps": steps,
            "elementary_tail": tail["elementary_tail"],
            "work": work + tail["work"]}


# --------------------------------------------------------------------------
# F3: the twin four-block row reduction
# --------------------------------------------------------------------------

def tuple_variants(word):
    """The (a,b,c,d) readings of a four-block word: 2 rotations x {w, w^-1}."""
    t = four_block_tuple(word)
    if t is None:
        return []
    a, b, c, d = t
    out = [((a, b, c, d), 1), ((c, d, a, b), 1)]
    ia, ib, ic, idd = (-c, -b, -a, -d)
    out += [((ia, ib, ic, idd), -1), ((ic, idd, ia, ib), -1)]
    return out


def recognize_F3(pair):
    """Recognize the twin four-block row reduction."""
    p = canon_pair(*pair)
    if any(four_block_tuple(w) is None for w in p):
        return None
    for t1, s1 in tuple_variants(p[0]):
        for t2, s2 in tuple_variants(p[1]):
            if t1[0] != t2[0] or t1[2] != t2[2] or t1 == t2:
                continue
            a, b, c, d = t1
            _, b2, _, d2 = t2
            det = abelian_det(*p)
            branch = ("terminal" if (b2 == b) != (d2 == d)
                      else "bs" if abs(c) == 1 else "dead_stable_power")
            return {"rule": "F3", "pair": list(p), "t1": list(t1), "t2": list(t2),
                    "a": a, "c": c, "p": b2 - b, "q": d2 - d, "det": det,
                    "branch": branch,
                    "difference": word_of_tuple((-c, b2 - b, c, d2 - d))}
    return None


def _find_move(state, want):
    """The engine move (target, jsign, k1, k2) producing ``want`` from ``state``."""
    want = canon_pair(*want)
    for target in (1, 2):
        for jsign in (1, -1):
            for k1 in range(len(state[target - 1])):
                for k2 in range(len(state[2 - target])):
                    move = (target, jsign, k1, k2)
                    if replay_move(tuple(state), move) == want:
                        return move
    return None


def compile_F3(pair, budget=10000):
    """Constructive certificate for F3: one substitution, then the proved gate."""
    hit = recognize_F3(pair)
    if hit is None:
        return {"solved": False, "reason": "not_recognized", "work": 0}
    if hit["branch"] == "dead_stable_power":
        return {"solved": False, "reason": "dead_stable_power", "work": 1, **hit}
    state = tuple(hit["pair"])
    target_pair = canon_pair(hit["difference"], hit["pair"][0])
    move = _find_move(state, target_pair)
    if move is None:
        # the difference may also be produced against the other relator
        target_pair = canon_pair(hit["difference"], hit["pair"][1])
        move = _find_move(state, target_pair)
    if move is None:
        return {"solved": False, "reason": "no_move_realizes_difference", "work": 1, **hit}
    states = [list(state), list(target_pair)]
    steps = [{"kind": "substitution", "move": "_".join(map(str, move))}]
    work = 2
    if hit["branch"] == "terminal":
        # D is a single generator: delete it from the companion, T3 with u = x.
        gen = [w for w in target_pair if len(w) == 1]
        if not gen:
            return {"solved": False, "reason": "difference_not_a_generator",
                    "work": work, "state": list(target_pair)}
        tail = primitive_completion.complete(target_pair, budget=budget, donor_word=gen[0])
        if not tail.get("solved"):
            return {"solved": False, "reason": "primitive_" + tail.get("reason", "?"),
                    "work": work + tail.get("work", 0)}
        states.extend(s[:] for s in tail["states"][1:])
        steps.extend(tail["steps"])
        return {"solved": True, "rule": "F3/terminal", "root": list(state),
                "states": states, "steps": steps,
                "elementary_tail": tail["elementary_tail"], "work": work + tail["work"],
                "branch": hit["branch"]}
    # BS branch
    if bs_gate(target_pair, general=True) is None:
        return {"solved": False, "reason": "difference_not_bs_donor", "work": work,
                "state": list(target_pair)}
    check = preflight(target_pair)
    work += 1
    if check.get("status") != "accept":
        return {"solved": False, "reason": "preflight_" + check.get("status", "?"),
                "work": work, "state": list(target_pair), "preflight": check}
    coll = consecutive_bs.collapse(target_pair, budget=min(10000, budget))
    if not coll["solved"]:
        return {"solved": False, "reason": "collapse_" + coll["reason"],
                "work": work + coll["rewrites"], "state": list(target_pair)}
    states.extend(s[:] for s in coll["states"][1:])
    steps.extend(coll["steps"])
    return {"solved": True, "rule": "F3/bs", "root": list(state),
            "states": states, "steps": steps, "elementary_tail": [],
            "work": work + coll["rewrites"], "branch": hit["branch"],
            "preflight": check}


# --------------------------------------------------------------------------
# machine replay of a certificate, from the original pair
# --------------------------------------------------------------------------

def replay_certificate(pair, cert):
    """Replay a mixed certificate independently; True iff it reaches ('x','y')."""
    if not cert.get("solved"):
        return False
    state = canon_pair(*pair)
    if list(state) != cert["states"][0]:
        raise AssertionError("certificate does not start at the canonical pair")
    for i, step in enumerate(cert["steps"]):
        if step["kind"] == "automorphism":
            if step["images"] not in NIELSEN:
                raise AssertionError("non-Nielsen ambient map")
            state = apply_pair(state, step["images"])
        else:
            target, jsign, k1, k2 = (int(v) for v in step["move"].split("_"))
            state = replay_move(state, (target, jsign, k1, k2))
        if list(state) != cert["states"][i + 1]:
            raise AssertionError(f"step {i} diverges: {state} != {cert['states'][i+1]}")
    if cert.get("elementary_tail"):
        final = two_block.replay(list(state), cert["elementary_tail"])
        return final == ["x", "y"]
    return len(state[0]) == len(state[1]) == 1 and state[0].lower() != state[1].lower()


# --------------------------------------------------------------------------
# planted examples and adversarial near misses
# --------------------------------------------------------------------------

def companions_for(donor, count=4):
    """A few reduced companions W with |det(donor, W)| = 1.

    Solves the Bezout condition ``P*s - Q*r = +-1`` for the companion exponent
    sums ``(r,s)`` (``(P,Q) = exp_sums(donor)``) and emits words realising them
    with a few different block shapes, so the planted set is not all two-block.
    """
    P, Q = exp_sums(donor)
    out = []
    lim = 6
    for r in range(-lim, lim + 1):
        for sgn in range(-lim, lim + 1):
            if abs(P * sgn - Q * r) != 1:
                continue
            shapes = [
                ("x" if r > 0 else "X") * abs(r) + ("y" if sgn > 0 else "Y") * abs(sgn),
                ("y" if sgn > 0 else "Y") * abs(sgn) + ("x" if r > 0 else "X") * abs(r),
                ("x" if r > 0 else "X") * abs(r) + "y" + ("y" if sgn > 0 else "Y") * abs(sgn) + "Y",
                "xy" + ("x" if r > 0 else "X") * abs(r) + ("y" if sgn > 0 else "Y") * abs(sgn) + "YX",
            ]
            for w in shapes:
                w = canon_rel(w)
                if not w or abs(abelian_det(donor, w)) != 1:
                    continue
                if w not in out:
                    out.append(w)
                if len(out) >= count:
                    return out
    return out


PLANTED_F1_TUPLES = [
    (1, 1, 1, 2), (1, 2, 1, 3), (-1, -2, -1, -3), (1, -2, 1, -1),
    (1, 3, 1, 2), (-1, 4, -1, 3), (2, 1, 3, 1), (-3, -1, -2, -1),
    (1, 5, 1, 4), (-1, -1, -1, -2), (1, -3, 1, -4), (4, 1, 5, 1),
]

ADVERSARIAL_F1 = [
    ((1, 1, 1, 3), "|b-d| = 2: merged word is y^2 x^2, never unimodular"),
    ((1, 1, 1, 4), "|b-d| = 3: merged word is the torus relator y^2 x^3"),
    ((1, 2, 1, 5), "|b-d| = 3: torus (2,3) again"),
    ((1, 2, -1, 3), "a = -c: a Baumslag-Solitar relator, not mergeable"),
    ((2, 1, 2, 2), "|a| = |c| = 2: no Nielsen map merges the y-blocks"),
    ((2, 1, 3, 2), "no matching pair of blocks of absolute value 1"),
    ((1, 1, -1, 2), "a = -c again (stable run 1)"),
    ((1, 1, 1, 6), "|b-d| = 5: torus (2,5)"),
]


def planted_report():
    rows = []
    for t in PLANTED_F1_TUPLES:
        donor = word_of_tuple(t)
        for w in companions_for(donor):
            pair = canon_pair(donor, w)
            cert = compile_F1(pair)
            ok = replay_certificate(pair, cert) if cert.get("solved") else False
            rows.append({"kind": "planted_F1", "tuple": list(t), "pair": list(pair),
                         "det": abelian_det(*pair),
                         "solved": bool(cert.get("solved")), "replayed": ok,
                         "work": cert.get("work"), "reason": cert.get("reason"),
                         "nielsen_steps": cert.get("nielsen_steps"),
                         "map": cert.get("map"), "merged": cert.get("merged"),
                         "elementary_moves": len(cert.get("elementary_tail", []))})
    for t, why in ADVERSARIAL_F1:
        donor = word_of_tuple(t)
        hits = [recognize_F1(canon_pair(donor, w)) is not None
                for w in companions_for(donor, count=6)]
        rows.append({"kind": "adversarial_F1", "tuple": list(t), "donor": donor,
                     "why": why, "companions_tested": len(hits),
                     "recognized": sum(hits),
                     "merge_data": merge_data(donor)})
    return rows


PLANTED_F3 = [
    ((-2, -2, 1, 1), (-2, -1, 1, -1)),     # both x-blocks differ, |c| = 1 -> BS
    ((-2, -2, 1, 1), (-2, -3, 1, 1)),      # only b differs -> terminal
    ((-2, -3, 1, 2), (-2, -3, 1, 1)),      # only d differs -> terminal
    ((-2, -2, 1, 2), (-2, -1, 1, 2)),      # only b differs -> terminal
    ((-2, -4, 1, 3), (-2, -3, 1, 3)),      # only b differs -> terminal
    ((-2, -2, 1, 1), (-2, -4, 1, 2)),      # both differ -> BS
    ((1, 2, -2, 1), (1, 1, -2, 2)),        # (a,c) = (1,-2) orientation
]

ADVERSARIAL_F3 = [
    (((-2, -2, 1, 1), (-1, -2, 1, 1)), "y-blocks differ (a = -2 vs -1)"),
    (((-3, -2, 2, 1), (-3, -1, 2, 2)), "min(|a|,|c|) = 2: dead stable power"),
    (((-2, -2, 1, 1), (-2, -2, 1, 1)), "identical relators"),
    (((-2, -2, 1, 1), (-2, -3, 1, 2)), "|det| != 1: block difference is 0"),
]


def planted_report_F3():
    rows = []
    for t1, t2 in PLANTED_F3:
        pair = canon_pair(word_of_tuple(t1), word_of_tuple(t2))
        det = abelian_det(*pair)
        hit = recognize_F3(pair)
        cert = compile_F3(pair)
        ok = replay_certificate(pair, cert) if cert.get("solved") else False
        rows.append({"kind": "planted_F3", "t1": list(t1), "t2": list(t2),
                     "pair": list(pair), "det": det,
                     "recognized": hit is not None,
                     "branch": (hit or {}).get("branch"),
                     "difference": (hit or {}).get("difference"),
                     "solved": bool(cert.get("solved")), "replayed": ok,
                     "work": cert.get("work"), "reason": cert.get("reason")})
    for (t1, t2), why in ADVERSARIAL_F3:
        pair = canon_pair(word_of_tuple(t1), word_of_tuple(t2))
        hit = recognize_F3(pair)
        cert = compile_F3(pair)
        rows.append({"kind": "adversarial_F3", "t1": list(t1), "t2": list(t2),
                     "pair": list(pair), "det": abelian_det(*pair), "why": why,
                     "recognized": hit is not None,
                     "branch": (hit or {}).get("branch"),
                     "solved": bool(cert.get("solved")), "reason": cert.get("reason")})
    return rows


# --------------------------------------------------------------------------
# panels
# --------------------------------------------------------------------------

def dev_report():
    import csv
    out = {"rows": 0, "four_block": 0, "F1": 0, "F1_solved": 0,
           "F3": 0, "F3_solved": 0, "hits": []}
    with open(DEV_CSV) as fh:
        for r in csv.DictReader(fh):
            out["rows"] += 1
            pair = canon_pair(r["r1"], r["r2"])
            if any(four_block_tuple(w) is not None for w in pair):
                out["four_block"] += 1
            if recognize_F1(pair) is not None:
                out["F1"] += 1
                cert = compile_F1(pair)
                ok = cert.get("solved") and replay_certificate(pair, cert)
                out["F1_solved"] += int(bool(ok))
                out["hits"].append({"name": r["name"], "rule": "F1",
                                    "solved": bool(ok), "work": cert.get("work")})
            if recognize_F3(pair) is not None:
                out["F3"] += 1
                cert = compile_F3(pair)
                ok = cert.get("solved") and replay_certificate(pair, cert)
                out["F3_solved"] += int(bool(ok))
                out["hits"].append({"name": r["name"], "rule": "F3",
                                    "solved": bool(ok), "work": cert.get("work")})
    return out


def census_report(shard_limit=None, compile_sample=400):
    files = sorted(glob.glob(ROWS_GLOB))
    if shard_limit:
        files = files[:shard_limit]
    stats = Counter()
    work_F1, work_F3, nodes_F1 = [], [], []
    compiled = 0
    for fn in files:
        for line in open(fn):
            row = json.loads(line)
            pair = canon_pair(*row["pair"])
            fb = any(four_block_tuple(w) is not None for w in pair)
            stats["rows"] += 1
            stats["solved"] += int(bool(row["solved"]))
            if fb:
                stats["four_block"] += 1
                stats["four_block_solved"] += int(bool(row["solved"]))
            h1 = recognize_F1(pair)
            h3 = recognize_F3(pair)
            if h1 is not None:
                stats["F1"] += 1
                stats["F1_solved_row"] += int(bool(row["solved"]))
                nodes_F1.append(row["nodes_explored"])
                if compiled < compile_sample:
                    compiled += 1
                    cert = compile_F1(pair)
                    ok = cert.get("solved") and replay_certificate(pair, cert)
                    stats["F1_compiled"] += 1
                    stats["F1_compiled_ok"] += int(bool(ok))
                    if ok:
                        work_F1.append(cert["work"])
            if h3 is not None:
                stats["F3"] += 1
                stats["F3_" + h3["branch"]] += 1
                stats["F3_solved_row"] += int(bool(row["solved"]))
                cert = compile_F3(pair)
                ok = cert.get("solved") and replay_certificate(pair, cert)
                stats["F3_compiled_ok"] += int(bool(ok))
                if ok:
                    work_F3.append(cert["work"])
                else:
                    stats["F3_fail_" + str(cert.get("reason"))] += 1
    def summarize(v):
        if not v:
            return None
        v = sorted(v)
        return {"n": len(v), "min": v[0], "median": v[len(v) // 2],
                "mean": round(sum(v) / len(v), 1), "max": v[-1]}
    return {"stats": dict(stats), "F1_compiler_work": summarize(work_F1),
            "F3_compiler_work": summarize(work_F3),
            "census_nodes_on_F1_rows": summarize(nodes_F1)}


def main(argv):
    report = {"planted_F1": planted_report(), "planted_F3": planted_report_F3(),
              "dev": dev_report()}
    bad = [r for r in report["planted_F1"]
           if r["kind"] == "planted_F1" and not (r["solved"] and r["replayed"])]
    bad += [r for r in report["planted_F1"]
            if r["kind"] == "adversarial_F1" and r["recognized"]]
    bad += [r for r in report["planted_F3"]
            if r["kind"] == "planted_F3" and not (r["solved"] and r["replayed"])]
    bad += [r for r in report["planted_F3"]
            if r["kind"] == "adversarial_F3" and r["solved"]]
    report["planted_failures"] = bad
    if "--census" in argv:
        limit = None
        for a in argv:
            if a.startswith("--shards="):
                limit = int(a.split("=")[1])
        report["census"] = census_report(limit)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "FOURBLOCK_verify.json")
    with open(out, "w") as fh:
        json.dump(report, fh, indent=1)
    print(json.dumps({k: v for k, v in report.items() if k != "planted_F1"}, indent=1)[:6000])
    print("\nplanted F1:", sum(1 for r in report["planted_F1"] if r["kind"] == "planted_F1"),
          "cases,",
          sum(1 for r in report["planted_F1"]
              if r["kind"] == "planted_F1" and r["solved"] and r["replayed"]),
          "solved+replayed")
    print("planted failures:", len(bad))
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv)
