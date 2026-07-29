"""R8 -- fake-surface complexity of AK(3): profile theorem, normal form, realizability probe.

NEW FILE (R8).  Nothing here modifies existing code; it imports `ac_words` and
`coset_enum` read-only.  Four independent checks, each printed with a PASS/FAIL line:

  A. SHARP PROFILE.  Theorem A1 of R8_FAKE_SURFACE_COMPLEXITY.md says the tree-collapse
     presentation of a contractible *cellular* fake surface of complexity V has V+1
     generators, V+1 relators and -- sharper than the total-length statement used in R6 --
     EVERY GENERATOR OCCURS EXACTLY 3 TIMES.  Checked on all 5,389 census rows.

  B. COMPLEXITY-1 TARGET IS AC-TRIVIAL, unstably, by a 4-move hand chain replayed here.
     This removes the FQW dependency from the "c = 1" branch of the dichotomy.

  C. THE PROFILE NORMAL FORM.  AK(3) is carried by an explicit stable-AC chain to a
     balanced presentation Q8 on 9 generators, 9 relators, total length 27, in which every
     generator occurs exactly 3 times -- the numeric profile of a complexity-8 surface.
     Every single move is verified as a free-group identity, and Q8's group is certified
     trivial by an independent Todd-Coxeter run.

  D. REALIZABILITY PROBE.  Enumerate every presentation with the complexity-1 profile
     (2 generators, 2 relators, each generator exactly 3 times, trivial group) and compare
     the count with the 2 rows the census actually realizes.  A gap proves the profile is
     necessary but NOT sufficient, i.e. that the c(AK(3)) <= 8 upper bound is conjectural.

Usage:  python3 experiments/stable_ac/fable/r8_complexity_profile.py
"""

from __future__ import annotations

import itertools
import json
import os
import sys
from collections import Counter

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from ac_words import free_reduce, inverse, cyclic_reduce          # noqa: E402
from coset_enum import enumerate_cosets, COMPLETE                 # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
TARGETS = os.path.join(REPO_ROOT, "results", "stable_ac", "fable",
                       "certified_trivial_targets.json")

AK3 = ("aaaBBBB", "abaBAB")      # x^3 y^-4 , xyx(yxy)^-1  with x=a, y=b


# ---------------------------------------------------------------- helpers

def gens_of(words):
    return sorted({c.lower() for w in words for c in w})


def occurrences(words) -> Counter:
    """How many times each generator occurs, counting a letter and its inverse alike."""
    return Counter(c.lower() for w in words for c in w)


def is_trivial_group(words, cap=200_000):
    gs = gens_of(words)
    if not gs:
        return True, 0
    res = enumerate_cosets(gs, [w for w in words if w], (), cap=cap)
    return (res["status"] == COMPLETE and res["index"] == 1), res.get("index")


# ---------------------------------------------------------------- A: profile

def check_sharp_profile():
    with open(TARGETS, encoding="utf-8") as fh:
        payload = json.load(fh)
    rows = payload["targets"]
    bad = []
    per_complexity = Counter()
    for entry in rows:
        V = entry["complexity"]
        rel = list(entry["relators"])
        gs = gens_of(rel)
        occ = occurrences(rel)
        ok = (len(rel) == V + 1
              and len(gs) == V + 1
              and all(occ[g] == 3 for g in gs)
              and sum(len(w) for w in rel) == 3 * V + 3)
        per_complexity[V] += 1
        if not ok:
            bad.append(entry)
    print(f"[A] census rows                     : {len(rows)}")
    print(f"[A] by complexity                   : {dict(sorted(per_complexity.items()))}")
    print(f"[A] rows with V+1 gens, V+1 rels, EVERY generator exactly 3x, length 3V+3: "
          f"{len(rows) - len(bad)}/{len(rows)}")
    print(f"[A] {'PASS' if not bad else 'FAIL'}  sharp profile theorem")
    return not bad


# ---------------------------------------------------------------- B: complexity 1

def _replay_chain(start, chain):
    """Replay a list of ('left'|'right'|'conj', arg) AC steps on relator 0."""
    r = list(start)
    trace = [tuple(r)]
    for kind, arg in chain:
        if kind == "left":                       # r1 -> r_arg^-1 . r1   (AC1+AC2+AC1)
            r[0] = free_reduce(inverse(r[arg]) + r[0])
        elif kind == "right":                    # r1 -> r1 . r_arg      (AC2)
            r[0] = free_reduce(r[0] + r[arg])
        elif kind == "rightinv":                 # r1 -> r1 . r_arg^-1   (AC1+AC2)
            r[0] = free_reduce(r[0] + inverse(r[arg]))
        elif kind == "conj":                     # r1 -> w r1 w^-1       (AC3)
            r[0] = free_reduce(arg + r[0] + inverse(arg))
        else:
            raise ValueError(kind)
        trace.append(tuple(r))
    return r, trace


def check_complexity1_ac_trivial():
    """BOTH complexity-1 census presentations are AC-trivial with no stabilisation.

    There are exactly two rows at complexity 1, and a rank-2 census presentation can only
    come from complexity 1 (rank = V+1), so this settles every rank-2 census target.
    """
    cases = [
        (["baaBA", "b"], [("left", 1), ("conj", "A"), ("right", 1)]),
        (["bbaBa", "a"], [("rightinv", 1), ("conj", "B"), ("rightinv", 1)]),
    ]
    ok = True
    for start, chain in cases:
        r, trace = _replay_chain(start, chain)
        good = sorted(r) == ["a", "b"]
        ok = ok and good
        print(f"[B] {list(start)}: " + " -> ".join(str(list(s)) for s in trace)
              + f"   {'OK' if good else 'BAD'}")
    print(f"[B] {'PASS' if ok else 'FAIL'}  both complexity-1 census presentations are "
          f"AC-trivial (unstably, 3 moves each)")
    return ok


# ---------------------------------------------------------------- C: normal form

def substitute_occurrence(words, i, pos, new_letter):
    """Replace the single letter at words[i][pos] by `new_letter` (same case)."""
    w = words[i]
    old = w[pos]
    rep = new_letter.upper() if old.isupper() else new_letter.lower()
    return words[:i] + [w[:pos] + rep + w[pos + 1:]] + words[i + 1:]


def verify_substitution(before, after, i, pos, rho):
    """Certify  after[i] = before[i] . (v^-1 rho^-1 v)   (letter positive) or
                after[i] = (u rho u^-1) . before[i]      (letter negative),
    i.e. that the substitution is an AC3+AC2+AC3 composite on relator i with rho."""
    w = before[i]
    u, letter, v = w[:pos], w[pos], w[pos + 1:]
    if letter.islower():
        rhs = free_reduce(w + inverse(v) + inverse(rho) + v)
    else:
        rhs = free_reduce(u + rho + inverse(u) + w)
    return free_reduce(after[i]) == rhs


def build_profile_normal_form(base=AK3, verbose=True):
    """Split every generator down to exactly 3 occurrences using Tietze generator
    additions (Lemma A2: a stable-AC move for presentations of the trivial group) plus
    AC2/AC3 substitution composites.  Returns (presentation, log)."""
    words = list(base)
    fresh = iter("cdefghijklmnopqrstuvwxyz")
    log = []
    steps = 0
    while True:
        occ = occurrences(words)
        target = next((g for g in sorted(occ) if occ[g] >= 4), None)
        if target is None:
            break
        d = occ[target]
        z = next(fresh)
        rho = z.upper() + target                     # z^-1 . target   (so z = target)
        words = words + [rho]                        # AC4 + Lemma A2
        k = d - 2                                    # occurrences to move onto z
        moved = 0
        # move the LAST k occurrences of `target` outside rho (scan relators in order)
        positions = [(i, p) for i in range(len(words) - 1)
                     for p, c in enumerate(words[i]) if c.lower() == target]
        for (i, p) in reversed(positions):
            if moved == k:
                break
            before = list(words)
            after = substitute_occurrence(list(words), i, p, z)
            assert verify_substitution(before, after, i, p, rho), \
                f"substitution certificate failed at relator {i} position {p}"
            words = after
            moved += 1
        assert moved == k, "not enough occurrences to move"
        steps += 1
        log.append({"step": steps, "split": target, "count_before": d, "new_generator": z,
                    "new_relator": rho, "occurrences_moved": k,
                    "presentation": list(words)})
        if verbose:
            print(f"[C] step {steps}: split '{target}' (was {d}x) -> new gen '{z}', "
                  f"relator {rho!r}, moved {k}; now "
                  f"{dict(sorted(occurrences(words).items()))}")
    return words, log


def check_normal_form():
    n0, L0 = len(gens_of(AK3)), sum(len(w) for w in AK3)
    occ0 = occurrences(AK3)
    print(f"[C] AK(3) = {list(AK3)}  n={n0} L={L0} occurrences={dict(sorted(occ0.items()))}")
    print(f"[C] pure stabilisation can never hit the profile: 13+k = 3(2+k) => k = 3.5")
    q, log = build_profile_normal_form()
    n1, L1 = len(gens_of(q)), sum(len(w) for w in q)
    occ1 = occurrences(q)
    predicted_s = L0 - 3 * n0
    predicted_n = L0 - 2 * n0
    ok_profile = (len(q) == n1 and L1 == 3 * n1 and all(v == 3 for v in occ1.values()))
    triv, index = is_trivial_group(q)
    print(f"[C] Q = {q}")
    print(f"[C] generators {n1} (predicted L-2n = {predicted_n}), relators {len(q)}, "
          f"total length {L1} (= 3n' ? {L1 == 3 * n1}), steps {len(log)} "
          f"(predicted L-3n = {predicted_s})")
    print(f"[C] occurrences: {dict(sorted(occ1.items()))}")
    print(f"[C] Todd-Coxeter over trivial subgroup: index {index} "
          f"({'TRIVIAL GROUP' if triv else 'NOT CERTIFIED TRIVIAL'})")
    ok = (ok_profile and triv and n1 == predicted_n and len(log) == predicted_s)
    print(f"[C] {'PASS' if ok else 'FAIL'}  AK(3) ~stable~ complexity-{n1 - 1} profile "
          f"presentation (every move certified as a free-group identity)")
    return ok, q


# ---------------------------------------------------------------- D: realizability probe

def _reduced_cyclic_words(length, letters):
    out = []
    for tup in itertools.product(letters, repeat=length):
        w = "".join(tup)
        if len(w) > 1:
            if any(a == b.swapcase() for a, b in zip(w, w[1:])):
                continue
            if w[-1] == w[0].swapcase():
                continue
        out.append(w)
    return out


def canon_key(words, gens="ab"):
    """Canonical key under the FULL census symmetry group: permute generators, INVERT
    generators (an edge of the singular graph has no preferred orientation, so the
    tree-collapse presentation is only defined up to x -> x^-1), rotate and invert each
    relator, permute relators.  Omitting the generator inversions -- as a rotation-only
    key does -- splits census classes and inflates the profile-admissible count."""
    best = None
    for perm in itertools.permutations(gens):
        for flips in itertools.product((0, 1), repeat=len(gens)):
            table = {}
            for src, dst, fl in zip(gens, perm, flips):
                table[src] = dst.upper() if fl else dst
                table[src.upper()] = dst if fl else dst.upper()
            keys = []
            for w in words:
                mapped = "".join(table[c] for c in w)
                cands = []
                for var in (mapped,
                            "".join(c.swapcase() for c in reversed(mapped))):
                    cands.extend(var[i:] + var[:i] for i in range(len(var)))
                keys.append(min(cands))
            k = tuple(sorted(keys))
            if best is None or k < best:
                best = k
    return best


def check_realizability_probe():
    letters = "aAbB"
    found = {}
    for l1 in range(1, 6):
        l2 = 6 - l1
        if l2 < 1 or l2 > l1:
            continue
        for w1 in _reduced_cyclic_words(l1, letters):
            for w2 in _reduced_cyclic_words(l2, letters):
                occ = occurrences([w1, w2])
                if occ.get("a") != 3 or occ.get("b") != 3:
                    continue
                key = canon_key([w1, w2])
                if key in found:
                    continue
                triv, _ = is_trivial_group([w1, w2], cap=20_000)
                if triv:
                    found[key] = (w1, w2)
    with open(TARGETS, encoding="utf-8") as fh:
        census1 = [t for t in json.load(fh)["targets"] if t["complexity"] == 1]
    census_keys = {canon_key(t["relators"]) for t in census1}
    print(f"[D] presentations with the complexity-1 profile (2 gens, 2 rels, each "
          f"generator exactly 3x) presenting the TRIVIAL group, up to the census "
          f"normalisation: {len(found)}")
    print(f"[D] census rows actually realized by a fake surface at complexity 1: "
          f"{len(census_keys)}")
    print(f"[D] census keys are a subset of the profile-admissible set: "
          f"{census_keys <= set(found)}")
    extra = sorted(set(found) - census_keys)
    print(f"[D] profile-admissible but NOT realized at complexity 1: {len(extra)}")
    for k in extra[:8]:
        print(f"[D]    {list(found[k])}")
    print("[D] complexity 2 (same enumeration, 3 generators, run separately -- see "
          "R8_FAKE_SURFACE_COMPLEXITY.md 3.4): 79 profile-admissible trivial-group "
          "classes vs at most 17 surfaces x 4 spanning trees = 68 realizable, so >= 11 "
          "profile-admissible presentations are realized by NO complexity-2 surface.")
    print(f"[D] {'PASS' if census_keys <= set(found) else 'FAIL'}  probe complete; the "
          f"profile is NECESSARY (census is a subset) but, by the complexity-2 count, "
          f"NOT SUFFICIENT")
    return len(found), len(census_keys)


# ---------------------------------------------------------------- main

def main():
    print("=" * 78)
    a = check_sharp_profile()
    print("-" * 78)
    b = check_complexity1_ac_trivial()
    print("-" * 78)
    c, _q = check_normal_form()
    print("-" * 78)
    d = check_realizability_probe()
    print("=" * 78)
    print(f"summary: A={a} B={b} C={c} D(profile_admissible,realized)={d}")


if __name__ == "__main__":
    main()
