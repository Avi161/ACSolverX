"""Classical-AC certificate: AK(3) and ORBIT2 are AC-connected at height ≤ 17.

The bounded-ball experiment (ball.py) found that at total-length ceiling 17
the components of AK(3) and ORBIT2 in the full-move AC graph coincide — a
single 1000-state component. This script makes that finding airtight and
self-contained:

  1. CLOSURE: re-derive the component from AK(3) by BFS, then check that for
     EVERY member state, every child within the ceiling lies inside the set.
     A closed set containing the root IS the whole component — no pop cap,
     traversal order, or termination edge case can be hiding states.
  2. MEMBERSHIP: the ORBIT2 root's canonical form is a member.
  3. PATH: BFS parents give an explicit move path AK(3) → the nearest floor
     state in ORBIT2's Aut-orbit; every move is replayed through
     ``words.replay_move`` (pure Python — the implementation pairing OPPOSITE
     to the numba ``children`` that generated the graph).

Every move is a Definition 2.1 concatenation move up to a conjugation, and
conjugation of one relator is itself an AC move (Definition 2.1's h_{i,w}),
so the path certifies CLASSICAL AC-equivalence — no stabilisation involved.

Writes AC17_CERTIFICATE.json;  --verify re-checks it from the JSON alone.

Run from the repo root:
    PYTHONHASHSEED=0 .venv/bin/python3 -m \
        experiments.stable_ac.cov.ak_3_universal_test.certify_classical
    ... certify_classical --verify
"""

import argparse
import json
import os
from collections import deque

from experiments.equivalence_classes.lib.acmoves import canon, children
from experiments.equivalence_classes.lib.autcanon import aut_canon, check
from experiments.equivalence_classes.lib.words import canon_pair, replay_move
from experiments.stable_ac.cov.ak_3_universal_test.sweep import AK3, ORBIT2

HERE = os.path.dirname(os.path.abspath(__file__))
CERT_PATH = os.path.join(HERE, "AC17_CERTIFICATE.json")

CEILING = 17
POP_CAP = 1000                  # repo hard cap; the component fits inside it


def component(root, total_cap):
    """BFS component of root in the ≤total_cap full-move AC graph, with
    parents. Raises if the pop cap is hit — the caller expects completeness."""
    s0 = canon(*root)
    parents = {s0: None}
    q = deque([s0])
    pops = 0
    while q:
        if pops >= POP_CAP:
            raise RuntimeError(f"component exceeds the {POP_CAP}-pop cap")
        state = q.popleft()
        pops += 1
        for child, mv in children(state[0], state[1], cap=total_cap - 1,
                                  seam_only=False).items():
            if len(child[0]) + len(child[1]) > total_cap or child in parents:
                continue
            parents[child] = (state, mv)
            q.append(child)
    return parents


def build():
    parents = component(AK3, CEILING)
    comp = set(parents)
    print(f"component of AK(3) at ceiling {CEILING}: {len(comp)} states",
          flush=True)

    # 1. closure — every child of every member stays inside
    for state in comp:
        for child in children(state[0], state[1], cap=CEILING - 1,
                              seam_only=False):
            if len(child[0]) + len(child[1]) <= CEILING and child not in comp:
                raise RuntimeError(f"NOT CLOSED: {state} -> {child}")
    print("closure verified: the set is the entire component", flush=True)

    # 2. membership + floor census
    o2_root = canon(*ORBIT2)
    assert o2_root in comp, "ORBIT2 root not in the component"
    ak3_rep = aut_canon(AK3)[1]
    o2_rep = aut_canon(ORBIT2)[1]
    floors = sorted(s for s in comp if len(s[0]) + len(s[1]) == 13)
    floor_orbits = {s: aut_canon(s)[1] for s in floors}
    assert set(floor_orbits.values()) == {ak3_rep, o2_rep}

    # 3. explicit path to the nearest ORBIT2-orbit floor state
    target = min(s for s, rep in floor_orbits.items() if rep == o2_rep)
    path, moves = [target], []
    cur = target
    while parents[cur] is not None:
        prev, mv = parents[cur]
        path.append(prev)
        moves.append(mv)
        cur = prev
    path, moves = list(reversed(path)), list(reversed(moves))
    _, t_rep, t_phi = aut_canon(target)

    cert = {
        "claim": "AK(3) is classically AC-equivalent (Definition 2.1 moves + "
                 "relator conjugations) to a length-13 presentation outside "
                 "its Aut(F2)-orbit, through states of total length <= 17",
        "ak3": list(AK3),
        "orbit2_root": list(o2_root),
        "ceiling": CEILING,
        "component_size": len(comp),
        "floor_states": {f"{s[0]}|{s[1]}":
                         ("AK3-orbit" if floor_orbits[s] == ak3_rep
                          else "ORBIT2-orbit") for s in floors},
        "moves": [list(m) for m in moves],
        "states": [list(s) for s in path],
        "target": list(target),
        "target_aut_rep": list(t_rep),
        "target_aut_phi": t_phi,
        "ak3_aut_rep": list(ak3_rep),
    }
    with open(CERT_PATH, "w") as f:
        json.dump(cert, f, indent=1)
    print(f"path: {len(moves)} moves, max height "
          f"{max(len(a) + len(b) for a, b in path)}, target "
          f"{target[0]}|{target[1]} -> {CERT_PATH}", flush=True)
    return cert


def verify():
    with open(CERT_PATH) as f:
        cert = json.load(f)
    errs = []
    state = canon_pair(*cert["ak3"])
    states = [tuple(s) for s in cert["states"]]
    if states[0] != state:
        errs.append("path does not start at canon(AK3)")
    for i, mv in enumerate(cert["moves"]):
        state = replay_move(state, tuple(mv))
        if state != states[i + 1]:
            errs.append(f"move {i} lands on {state}, cert says {states[i+1]}")
            break
        if len(state[0]) + len(state[1]) > cert["ceiling"]:
            errs.append(f"state {i+1} exceeds ceiling")
    target = tuple(cert["target"])
    if state != target:
        errs.append("replay endpoint != target")
    if len(target[0]) + len(target[1]) != 13:
        errs.append("target is not length 13")
    if not check(target, tuple(cert["target_aut_rep"]),
                 cert["target_aut_phi"]):
        errs.append("target aut witness fails")
    if tuple(cert["target_aut_rep"]) == tuple(cert["ak3_aut_rep"]):
        errs.append("target in AK(3)'s own orbit — no finding")
    if errs:
        for e in errs:
            print("FAIL:", e)
        raise SystemExit(1)
    print(f"CLASSICAL AC CERTIFICATE VERIFIES: {len(cert['moves'])} moves "
          f"inside ceiling {cert['ceiling']}, endpoint "
          f"{target[0]}|{target[1]} in Aut-orbit "
          f"{tuple(cert['target_aut_rep'])} != AK(3)'s "
          f"{tuple(cert['ak3_aut_rep'])}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    verify() if args.verify else build()


if __name__ == "__main__":
    main()
