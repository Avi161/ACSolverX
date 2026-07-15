"""Certificate that AK(3)'s stable-AC class contains a second Aut(F₂)-orbit
at the length-13 floor.

Claim being certified:  there is an automorphism φ of F₂ and a sequence of
Definition 2.1 AC moves such that

    AC-moves( canon(φ(AK3)) )  ∋  F,   |F| = 13,
    aut_canon(F) = ('YYXXyx', 'YYYxyXX')  ≠  aut_canon(AK3) = ('YXYxyx', 'YYYYxxx')

i.e. the greedy's floor state F is a length-13 presentation in AK(3)'s
stable-AC class (φ is realised by the universal stable move: stabilise with
z = w(x,y), AC-isolate, destabilise) that is NOT a change of variables of
AK(3).

Search side (writes the certificate): best-first on total length over
``acmoves.children`` (the baseline seam move set), parent-tracked, hard pop
cap 1000 (repo rule), trying each iso_index=2 orbit-2 d1 row's (z, iso_gen)
in provenance order until one start connects.

Verify side (``--verify``, reads ONLY the JSON): the opposite implementation
pairing from the search —
  * φ is an automorphism: classical Nielsen reduction (local ``is_basis``,
    after verify_proofs.py's);
  * φ carries AK(3) onto the start: pure substitution (``words.apply_hom``);
  * every move replayed by ``words.replay_move`` (pure Python canon_pair;
    the search generated children with numba ``canonical_pair_nj``);
  * endpoint total length 13, abelian det 1;
  * both aut_canon witnesses re-checked by substitution (``autcanon.check``).
Orbit *distinctness* additionally rests on Whitehead's algorithm being a
complete orbit invariant (autcanon's level-set BFS) — stated, not re-proved.

Run from the repo root:
    PYTHONHASHSEED=0 .venv/bin/python3 -m \
        experiments.stable_ac.cov.ak_3_universal_test.certify        # search
    ... certify --verify                                             # check
"""

import argparse
import heapq
import json
import os

from experiments.equivalence_classes.lib.acmoves import canon, children
from experiments.equivalence_classes.lib.autcanon import aut_canon, check
from experiments.equivalence_classes.lib.words import (
    abelian_det,
    apply_hom,
    canon_pair,
    free_reduce,
    inv,
    replay_move,
)
from experiments.greedy_tests.spec.words import str_to_word, word_to_str
from experiments.stable_ac.cov import cov
from experiments.stable_ac.cov.ak_3_universal_test.sweep import AK3, ORBIT2

HERE = os.path.dirname(os.path.abspath(__file__))
CERT_PATH = os.path.join(HERE, "ORBIT2_CERTIFICATE.json")

POP_CAP = 1000                  # repo hard cap — never raise
RELATOR_CAP = 27                # matches the d1 rows: max(24, 11 + 16)

# iso_index=2 d1 rows that reached orbit 2, simplest z first (sweep_results)
CANDIDATE_ZS = [("Xy", "y"), ("XXy", "y"), ("Xyy", "x"), ("xYx", "y"),
                ("XXXy", "y"), ("XXyy", "y"), ("Xyyy", "x")]


def is_basis(u, v):
    """True iff (u, v) is a basis of F2 — Nielsen reduction, as in
    verify_proofs.py (copied so the verifier imports no search-side code)."""
    u, v = free_reduce(u), free_reduce(v)
    changed = True
    while changed:
        changed = False
        if not u or not v:
            return False
        for a_is_u, (a, b) in ((True, (u, v)), (False, (v, u))):
            for cand in (free_reduce(a + b), free_reduce(a + inv(b)),
                         free_reduce(inv(b) + a), free_reduce(b + a)):
                if len(cand) < len(a):
                    if a_is_u:
                        u = cand
                    else:
                        v = cand
                    changed = True
                    break
            if changed:
                break
    return len(u) == 1 and len(v) == 1 and u.lower() != v.lower()


_INT_TO_CHAR = {1: "x", -1: "X", 2: "y", -2: "Y", 3: "z", -3: "Z"}


def phi_of_cov(z_str, iso_gen):
    """The composite automorphism a defining-relator CoV applies to the pair.

    apply_cov_once with iso_index 2: substitute iso_gen = expr(other, z),
    then relabel the survivors back to (x, y). As one endomorphism of
    F₂(x, y): iso_gen ↦ relabel(expr), other ↦ relabel(other)."""
    res = cov.apply_cov_once(
        str_to_word(AK3[0]), str_to_word(AK3[1]), str_to_word(z_str),
        allow_defining_iso=True, iso_gen=iso_gen)
    if res is None or res.iso_index != 2:
        return None, None
    relabeled = cov.relabel(res.expr, iso_gen)
    expr_str = word_to_str(relabeled)
    if iso_gen == "x":
        # survivors (y, z) -> (x, y): the old y is now called x
        phi = {"x": expr_str, "y": "x"}
    else:
        # survivors (x, z) -> (x, y): x keeps its name
        phi = {"x": "x", "y": expr_str}
    return phi, (word_to_str(res.r1), word_to_str(res.r2))


def find_path(start_pair, o2_rep):
    """Best-first (total length, then lex) over the seam move set from
    start_pair until a total-13 state in the o2_rep Aut-orbit pops."""
    s0 = canon(*start_pair)
    heap = [(len(s0[0]) + len(s0[1]), s0)]
    parents = {s0: None}
    pops = 0
    aut_cache = {}
    while heap and pops < POP_CAP:
        _, state = heapq.heappop(heap)
        pops += 1
        if len(state[0]) + len(state[1]) == 13:
            if state not in aut_cache:
                aut_cache[state] = aut_canon(state)[1]
            if aut_cache[state] == o2_rep:
                path, moves = [state], []
                cur = state
                while parents[cur] is not None:
                    prev, mv = parents[cur]
                    path.append(prev)
                    moves.append(mv)
                    cur = prev
                return list(reversed(path)), list(reversed(moves)), pops
        for child, mv in children(state[0], state[1],
                                  cap=RELATOR_CAP, seam_only=True).items():
            if child in parents:
                continue
            parents[child] = (state, mv)
            heapq.heappush(heap, (len(child[0]) + len(child[1]), child))
    return None, None, pops


def build():
    _, ak3_rep, ak3_phi = aut_canon(AK3)
    _, o2_rep, o2_phi_rep = aut_canon(ORBIT2)
    assert ak3_rep != o2_rep
    for z_str, iso_gen in CANDIDATE_ZS:
        phi, start = phi_of_cov(z_str, iso_gen)
        if phi is None:
            continue
        if not is_basis(phi["x"], phi["y"]):
            continue
        print(f"trying z={z_str} iso={iso_gen} phi=x->{phi['x']},"
              f"y->{phi['y']} start={start[0]}|{start[1]}", flush=True)
        path, moves, pops = find_path(start, o2_rep)
        if path is None:
            print(f"  no orbit-2 floor state within {pops} pops", flush=True)
            continue
        floor = path[-1]
        _, floor_rep, floor_phi = aut_canon(floor)
        assert floor_rep == o2_rep and check(floor, floor_rep, floor_phi)
        cert = {
            "claim": "AK(3)'s stable-AC class contains a length-13 "
                     "presentation outside AK(3)'s Aut(F2)-orbit",
            "ak3": list(AK3),
            "z_word": z_str, "iso_gen": iso_gen,
            "phi": phi,
            "start": list(start),
            "moves": [list(m) for m in moves],
            "states": [list(s) for s in path],
            "floor_state": list(floor),
            "pops_used": pops, "pop_cap": POP_CAP,
            "relator_cap": RELATOR_CAP,
            "ak3_aut_rep": list(ak3_rep),
            "ak3_aut_phi": ak3_phi,
            "floor_aut_rep": list(floor_rep),
            "floor_aut_phi": floor_phi,
        }
        with open(CERT_PATH, "w") as f:
            json.dump(cert, f, indent=1)
        print(f"certificate written: {len(moves)} AC moves, floor "
              f"{floor[0]}|{floor[1]}, {pops} pops -> {CERT_PATH}", flush=True)
        return cert
    raise SystemExit("no candidate start connected within the pop cap")


def verify():
    with open(CERT_PATH) as f:
        cert = json.load(f)
    errs = []
    phi = cert["phi"]
    if not is_basis(phi["x"], phi["y"]):
        errs.append("phi is not an automorphism")
    ak3 = tuple(cert["ak3"])
    if ak3 != AK3:
        errs.append("certificate is not about AK(3)")
    start = canon_pair(apply_hom(ak3[0], phi), apply_hom(ak3[1], phi))
    if start != canon_pair(*cert["start"]):
        errs.append("phi(AK3) != start")
    state = canon_pair(*cert["start"])
    states = [tuple(s) for s in cert["states"]]
    if states[0] != state:
        errs.append("state[0] != canon(start)")
    for i, mv in enumerate(cert["moves"]):
        state = replay_move(state, tuple(mv))
        if state != states[i + 1]:
            errs.append(f"move {i} lands on {state}, cert says {states[i+1]}")
            break
    floor = tuple(cert["floor_state"])
    if state != floor:
        errs.append("replay endpoint != floor_state")
    if len(floor[0]) + len(floor[1]) != 13:
        errs.append("floor state is not length 13")
    if abs(abelian_det(*floor)) != 1:
        errs.append("floor |abelian det| != 1")
    ak3_rep = tuple(cert["ak3_aut_rep"])
    floor_rep = tuple(cert["floor_aut_rep"])
    if not check(ak3, ak3_rep, cert["ak3_aut_phi"]):
        errs.append("AK3 aut witness fails")
    if not check(floor, floor_rep, cert["floor_aut_phi"]):
        errs.append("floor aut witness fails")
    if ak3_rep == floor_rep:
        errs.append("aut reps are equal — same orbit, no finding")
    if errs:
        for e in errs:
            print("FAIL:", e)
        raise SystemExit(1)
    print(f"CERTIFICATE VERIFIES: phi = (x->{phi['x']}, y->{phi['y']}), "
          f"{len(cert['moves'])} AC moves, floor "
          f"{floor[0]}|{floor[1]} in Aut-orbit {floor_rep} != AK(3)'s "
          f"{ak3_rep}\n(orbit distinctness rests on Whitehead completeness)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    verify() if args.verify else build()


if __name__ == "__main__":
    main()
