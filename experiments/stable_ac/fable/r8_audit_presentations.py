"""ADVERSARIAL AUDIT of R8's presentation-level claims (A2, D1/D2/D + Q8, section 3.4,
section 4's correction to R3 section R5).  NEW FILE; re-derives everything with its own
free-group arithmetic.

Blocks:
  J  the certified-target JSON really is a tree-collapse of the upstream CSV row it
     claims (validates the data block A of r8_complexity_profile.py trusts).
  B  Theorem A2: replay both complexity-1 chains move by move, naming the AC move used
     at each step and checking the free-group identity independently.
  C  Theorem D: rebuild the Tietze-split chain from AK(3) from scratch; check every
     substitution as a free-group identity; check Q8's profile; certify the group two
     ways (Todd-Coxeter, and by an independent hand reduction back to AK(3)).
  E  section 4's correction to R3 section R5: compute the occurrence vector of the
     (6,18) state reached by 4 AC4 + 1 AC2 from AK(3).
  F  section 3.4: count the profile-admissible trivial-group classes at the complexity-2
     profile AND the classes actually realized by (census surface, spanning tree) pairs,
     in the SAME canonical quotient.
  G  a Todd-Coxeter sanity ladder, so the triviality verdicts are not taken on trust.

Usage: python3 experiments/stable_ac/fable/r8_audit_presentations.py [--skip-f]
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import sys
from collections import Counter, defaultdict

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from coset_enum import enumerate_cosets, COMPLETE                       # noqa: E402
from r8_audit_a1_trees import (load_census, reconstruct_skeleton,        # noqa: E402
                               spanning_trees, collapse, free_reduce,
                               cyclic_reduce, occ)

REPO = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
TARGETS = os.path.join(REPO, "results", "stable_ac", "fable",
                       "certified_trivial_targets.json")
CSV = ("/tmp/claude-0/-home-user-ACSolverX/3b1e6f55-9c29-53f6-95b5-fd7ded7bcafc/"
       "scratchpad/Fake-Surfaces/fakesurfaces.csv")

AK3 = ["aaaBBBB", "abaBAB"]


def inv(word: str) -> str:
    return "".join(c.swapcase() for c in reversed(word))


def mul(*words) -> str:
    return free_reduce("".join(words))


def gens_of(words):
    return sorted({c.lower() for w in words for c in w})


def trivial(words, cap=200_000):
    ws = [w for w in words if w]
    gs = gens_of(ws)
    if not gs:
        return True, 1, COMPLETE
    res = enumerate_cosets(gs, ws, (), cap=cap)
    return (res["status"] == COMPLETE and res["index"] == 1), res.get("index"), \
        res["status"]


# ------------------------------------------------------------------ G: TC ladder

def block_G():
    print("[G] Todd-Coxeter sanity ladder (the triviality oracle used below)")
    cases = [
        (["a", "b"], True, "standard rank 2"),
        (["ab"], False, "Z"),
        (["a", "bb"], False, "Z/2"),
        (["aB", "ba"], False, "not trivial (Z)"),
        (AK3, True, "AK(3) -- known to present the trivial group"),
        (["aaaBBBB", "abaBAB", "c"], True, "AK(3)+z"),
    ]
    ok = True
    for words, want, label in cases:
        got, index, status = trivial(words)
        flag = "OK" if got == want else "MISMATCH"
        ok = ok and got == want
        print(f"[G]   {label:48s} index={index} status={status} -> {got} ({flag})")
    print(f"[G] {'PASS' if ok else 'FAIL'}")
    return ok


# ------------------------------------------------------------------ J: JSON vs CSV

def block_J():
    rows = load_census(CSV)
    payload = json.load(open(TARGETS, encoding="utf-8"))["targets"]
    print(f"[J] census CSV rows {len(rows)}, JSON targets {len(payload)}")
    if len(rows) != len(payload):
        print("[J] FAIL count mismatch")
        return False
    misaligned = 0
    unrealizable = 0
    for r, entry in zip(rows, payload):
        if r["V"] != entry["complexity"] or r["skeleton"] != entry["skeleton"]:
            misaligned += 1
            continue
        endpoints, nverts, _ = reconstruct_skeleton(r["V"], r["disks"])
        variants = set()
        for T in spanning_trees(r["V"], endpoints):
            variants.add(tuple(collapse(r["disks"], T, 2 * r["V"])))
        if tuple(entry["relators"]) not in variants:
            unrealizable += 1
            if unrealizable <= 4:
                print(f"[J]   line {r['line']}: JSON {entry['relators']} is NOT any "
                      f"tree-collapse of this row; e.g. {sorted(variants)[:2]}")
    print(f"[J] rows whose (complexity, skeleton) disagree with the CSV : {misaligned}")
    print(f"[J] rows whose JSON relators are NOT a tree-collapse        : {unrealizable}")
    ok = misaligned == 0 and unrealizable == 0
    print(f"[J] {'PASS' if ok else 'FAIL'}  the target JSON is a faithful tree-collapse "
          f"of the upstream census")
    return ok


# ------------------------------------------------------------------ B: Theorem A2

def block_B():
    """Replay both chains of Theorem A2, checking each move against FRAMING's move set:
    AC1 r_i -> r_i^-1 ; AC2 r_i -> r_i r_j (j != i) ; AC3 r_i -> w r_i w^-1."""
    print("[B] Theorem A2 -- both complexity-1 census presentations, unstable chains")
    census1 = [t["relators"] for t in json.load(open(TARGETS, encoding="utf-8"))["targets"]
               if t["complexity"] == 1]
    print(f"[B] complexity-1 rows in the census: {len(census1)} -> {census1}")

    def step(words, spec):
        kind, arg = spec
        r = list(words)
        if kind == "AC1":                       # invert relator arg
            r[arg] = inv(r[arg])
        elif kind == "AC2":                     # r_0 -> r_0 . r_arg
            r[0] = mul(r[0], r[arg])
        elif kind == "AC2inv":                  # r_0 -> r_0 . r_arg^-1  (AC1,AC2,AC1)
            r[0] = mul(r[0], inv(r[arg]))
        elif kind == "AC2left":                 # r_0 -> r_arg^-1 . r_0  (AC1,AC2,AC1)
            r[0] = mul(inv(r[arg]), r[0])
        elif kind == "AC3":                     # r_0 -> arg r_0 arg^-1
            r[0] = mul(arg, r[0], inv(arg))
        else:
            raise ValueError(kind)
        return r

    chains = {
        ("baaBA", "b"): [("AC2left", 1), ("AC3", "A"), ("AC2", 1)],
        ("bbaBa", "a"): [("AC2inv", 1), ("AC3", "B"), ("AC2inv", 1)],
    }
    ok = True
    for start, chain in chains.items():
        words = list(start)
        trace = [list(words)]
        for spec in chain:
            words = step(words, spec)
            trace.append(list(words))
        good = sorted(words) == ["a", "b"]
        ok = ok and good and list(start) in census1
        print(f"[B]   {list(start)} in census: {list(start) in census1}")
        for spec, state in zip(chain, trace[1:]):
            print(f"[B]     {spec[0]:8s} arg={spec[1]!r:5s} -> {state}")
        print(f"[B]   reaches the standard presentation: {good}")
    print(f"[B] {'PASS' if ok else 'FAIL'}  A2: both are AC-trivial in 3 moves, no "
          f"stabilisation used")
    return ok


# ------------------------------------------------------------------ C: Theorem D

def split_step(words, target, fresh):
    """One Tietze split: adjoin `fresh` with relator fresh^-1 . target (Lemma D1), then
    move d-2 occurrences of `target` off onto `fresh` (Lemma D2).  Every substitution is
    certified as an exact free-group identity here."""
    d = occ(words)[target]
    rho = fresh.upper() + target
    words = list(words) + [rho]
    k = d - 2
    moved = 0
    certificates = []
    positions = [(i, p) for i in range(len(words) - 1)
                 for p, c in enumerate(words[i]) if c.lower() == target]
    for (i, p) in reversed(positions):
        if moved == k:
            break
        w = words[i]
        u, letter, v = w[:p], w[p], w[p + 1:]
        new = fresh.upper() if letter.isupper() else fresh
        after = w[:p] + new + w[p + 1:]
        if letter.islower():
            # r -> r . (v^-1 rho^-1 v):  AC3 on rho, AC1, AC2, AC3 back
            witness = mul(w, inv(v), inv(rho), v)
            justification = "AC2 by conjugate v^-1.rho^-1.v"
        else:
            # r -> (u rho u^-1) . r:  AC1,AC2,AC1 composite for left multiplication
            witness = mul(u, rho, inv(u), w)
            justification = "AC2left by conjugate u.rho.u^-1"
        certificates.append({"relator": i, "pos": p, "letter": letter,
                             "identity_holds": free_reduce(after) == witness,
                             "reduced_spelling_stable": free_reduce(after) == after,
                             "justification": justification})
        words[i] = after
        moved += 1
    assert moved == k, "not enough occurrences to move"
    return words, rho, certificates


def block_C():
    print("[C] Theorem D -- rebuilding the split chain from AK(3) independently")
    words = list(AK3)
    n0, L0 = len(gens_of(words)), sum(map(len, words))
    print(f"[C] AK(3) {words} n={n0} L={L0} occ={dict(sorted(occ(words).items()))}")
    fresh = iter("cdefghijklmnopqrstuvwxyz")
    steps = 0
    all_certs = []
    while True:
        o = occ(words)
        target = next((g for g in sorted(o) if o[g] >= 4), None)
        if target is None:
            break
        words, rho, certs = split_step(words, target, next(fresh))
        all_certs.extend(certs)
        steps += 1
        print(f"[C]   step {steps}: split {target!r} (was {o[target]}x), new relator "
              f"{rho!r} -> {words}")
    n1, L1 = len(gens_of(words)), sum(map(len, words))
    o1 = occ(words)
    doc_Q8 = ["aacBBDD", "cfeFEH", "Ga", "Hb", "Gc", "Id", "Ge", "If", "Ih"]
    checks = {
        "matches_document_Q8": words == doc_Q8,
        "generators_9": n1 == 9,
        "relators_9": len(words) == 9,
        "length_27": L1 == 27,
        "every_gen_3x": all(v == 3 for v in o1.values()),
        "formula_n'=L-2n": n1 == L0 - 2 * n0,
        "formula_steps=L-3n": steps == L0 - 3 * n0,
        "V0=L-2n-1": n1 - 1 == L0 - 2 * n0 - 1,
        "all_words_cyclically_reduced": all(cyclic_reduce(w) == w for w in words),
        "all_substitution_identities": all(c["identity_holds"] for c in all_certs),
        "no_hidden_free_reduction": all(c["reduced_spelling_stable"]
                                       for c in all_certs),
        "substitutions_performed": len(all_certs),
    }
    triv, index, status = trivial(words)
    checks["todd_coxeter_index_1"] = triv
    # independent hand certificate: the 7 short relators are z^-1 g, so eliminating
    # them by Tietze must return AK(3) on {g, i}
    elim = {"a": "g", "c": "g", "e": "g", "b": "i", "d": "i", "f": "i", "h": "i",
            "g": "g", "i": "i"}
    rewritten = ["".join(elim[c.lower()].upper() if c.isupper() else elim[c.lower()]
                         for c in w) for w in words[:2]]
    checks["hand_elimination_gives_AK3"] = [free_reduce(w) for w in rewritten] == \
        ["gggiiii".replace("i", "I"), "gigIGI"]
    print(f"[C] Q  = {words}")
    print(f"[C] occ={dict(sorted(o1.items()))} n={n1} rel={len(words)} L={L1} "
          f"steps={steps}")
    print(f"[C] Todd-Coxeter: index={index} status={status}")
    print(f"[C] hand elimination of the 7 short relators -> {rewritten}")
    for k, v in checks.items():
        print(f"[C]   {k:34s} {v}")
    ok = all(v is True for k, v in checks.items() if k != "substitutions_performed")
    print(f"[C] {'PASS' if ok else 'FAIL'}")
    return ok


# ------------------------------------------------------------------ E: R3 correction

def block_E():
    print("[E] R8 section 4 item 4: the (6,18) state reached from AK(3) by stabilisation")
    words = list(AK3)
    print(f"[E] AK(3) occ={dict(sorted(occ(words).items()))} n=2 L={sum(map(len, words))}")
    for g in "pqrs":                                     # 4 x AC4
        words = words + [g]
    n, L = len(gens_of(words)), sum(map(len, words))
    print(f"[E] after 4 AC4     : n={n} L={L} occ={dict(sorted(occ(words).items()))}")
    if L != 17:
        print("[E] FAIL 4 AC4 should give L=17")
    # AC2: multiply relator 0 by the fresh stabiliser relator p (index 2)
    variants = {}
    for j, label in ((2, "r0 <- r0.p"), (3, "r0 <- r0.q")):
        w2 = list(words)
        w2[0] = mul(w2[0], w2[j])
        variants[label] = w2
    for label, w2 in variants.items():
        o = occ(w2)
        vec = tuple(o[g] for g in gens_of(w2))
        print(f"[E] after AC2 {label:12s}: n={len(gens_of(w2))} L={sum(map(len, w2))} "
              f"relators={len(w2)} occ={dict(sorted(o.items()))} vector={vec} "
              f"sum={sum(vec)}")
    claimed = (7, 7, 2, 1, 1, 1)
    actual = tuple(occ(variants["r0 <- r0.p"])[g]
                   for g in gens_of(variants["r0 <- r0.p"]))
    print(f"[E] R3/R8 correction text claims occurrence vector {claimed} (sum "
          f"{sum(claimed)}); actual is {actual} (sum {sum(actual)})")
    print(f"[E] vector as printed matches the state: {claimed == actual}")
    print(f"[E] but the SUBSTANCE (not the all-3s profile) holds either way: "
          f"{set(actual) != {3}}")
    # can any AC1 change the length?  AC1 is inversion, length preserving.
    print(f"[E] AC1 (inversion) is length-preserving on every relator: "
          f"{all(len(inv(w)) == len(w) for w in words)}")
    print(f"[E] pure stabilisation arithmetic 13+k = 3(2+k) -> k = {(13 - 6) / 2}")
    return claimed == actual, actual


# ------------------------------------------------------------------ F: section 3.4

GENS3 = "abc"


def rotkey(w):
    cands = []
    for var in (w, inv(w)):
        cands.extend(var[i:] + var[:i] for i in range(len(var)))
    return min(cands)


def canon_full(words, gens=GENS3):
    best = None
    for perm in itertools.permutations(gens):
        for flips in itertools.product((0, 1), repeat=len(gens)):
            table = {}
            for src, dst, fl in zip(gens, perm, flips):
                table[src] = dst.upper() if fl else dst
                table[src.upper()] = dst if fl else dst.upper()
            k = tuple(sorted(rotkey("".join(table[c] for c in w)) for w in words))
            if best is None or k < best:
                best = k
    return best


def block_F():
    print("[F] section 3.4 -- profile-admissible vs REALIZED at the complexity-2 profile")
    letters = "aAbBcC"

    def reduced_cyclic(length):
        out = []
        for tup in itertools.product(letters, repeat=length):
            w = "".join(tup)
            if length > 1:
                if any(x == y.swapcase() for x, y in zip(w, w[1:])):
                    continue
                if w[-1] == w[0].swapcase():
                    continue
            out.append(w)
        return out

    bylen = {}
    for length in range(1, 8):
        d = defaultdict(set)
        for w in reduced_cyclic(length):
            o = occ([w])
            d[tuple(o[g] for g in GENS3)].add(rotkey(w))
        bylen[length] = {k: sorted(v) for k, v in d.items()}
    raw = set()
    for parts in itertools.combinations_with_replacement(range(1, 8), 3):
        if sum(parts) != 9:
            continue
        l1, l2, l3 = parts
        for v1 in bylen[l1]:
            for v2 in bylen[l2]:
                v3 = tuple(3 - v1[i] - v2[i] for i in range(3))
                if min(v3) < 0 or v3 not in bylen[l3]:
                    continue
                for w1 in bylen[l1][v1]:
                    for w2 in bylen[l2][v2]:
                        for w3 in bylen[l3][v3]:
                            raw.add(tuple(sorted((w1, w2, w3))))
    print(f"[F] rotation/inversion-canonical triples with the profile: {len(raw)}")
    classes = {canon_full(list(t)) for t in raw}
    print(f"[F] canonical classes before the triviality test        : {len(classes)}")
    triv_classes = {k for k in classes if trivial(list(k), cap=20_000)[0]}
    print(f"[F] ...presenting the TRIVIAL group                      : "
          f"{len(triv_classes)}")
    # realized classes: EVERY spanning tree of EVERY complexity-2 census surface
    rows = [r for r in load_census(CSV) if r["V"] == 2]
    realized = set()
    pairs = 0
    for r in rows:
        endpoints, _, _ = reconstruct_skeleton(2, r["disks"])
        for T in spanning_trees(2, endpoints):
            pairs += 1
            realized.add(canon_full(collapse(r["disks"], T, 4)))
    print(f"[F] complexity-2 census surfaces {len(rows)}, (surface,tree) pairs {pairs}, "
          f"distinct realized classes {len(realized)}")
    print(f"[F] realized subset of profile-admissible-trivial: "
          f"{realized <= triv_classes}")
    print(f"[F] profile-admissible + trivial but NOT realized : "
          f"{len(triv_classes - realized)}")
    print(f"[F] R8 says >= 11 (via 17 x 4 = 68 >= realized); the exact count is "
          f"{len(triv_classes)} - {len(realized)} = {len(triv_classes) - len(realized)}")
    return len(triv_classes), len(realized), pairs


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-f", action="store_true")
    args = ap.parse_args(argv)
    out = {}
    print("=" * 78)
    out["G"] = block_G()
    print("-" * 78)
    out["J"] = block_J()
    print("-" * 78)
    out["B"] = block_B()
    print("-" * 78)
    out["C"] = block_C()
    print("-" * 78)
    out["E"] = block_E()[0]
    if not args.skip_f:
        print("-" * 78)
        out["F"] = block_F()
    print("=" * 78)
    print(f"summary: {out}")


if __name__ == "__main__":
    main()
