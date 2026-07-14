"""Verify the 136th edge, `21_3 == 21_29`, from its certificate alone.

`verify_proofs.py` re-proves the shipped 135 edges of the 126-partition. This checks the ONE edge
found later, at `max_total = 34`, which took that partition to 125 (EQUIVALENCE_FINDING.md 3b).
It is kept separate on purpose: the 126 artifacts are not renumbered (125 is not converged
either), so the 135-edge verifier must keep passing unchanged.

The check trusts nothing the search did. It replays each certificate step with the pure-Python
word algebra of `lib/words.py` -- `replay_move`, `apply_hom`, `canon_pair` -- which is a
deliberately independent implementation, not the numba solver that produced the paths. A step is

    (move, phi, claimed_rep):   apply the Definition 2.1 `move`, then the automorphism `phi`,
                                canonicalise, and you must land exactly on `claimed_rep`.

Both roots must land on the same Aut(F2)-class. That, plus `phi` being a genuine automorphism at
every step, is exactly what ACA-equivalence means: the two are the same problem.

Exits non-zero on any mismatch.
"""
import json
import os
import sys


def _repo_root():
    d = os.path.dirname(os.path.abspath(__file__))
    while d != os.path.dirname(d):
        if (os.path.isdir(os.path.join(d, "experiments"))
                and os.path.isdir(os.path.join(d, "data"))):
            return d
        d = os.path.dirname(d)
    raise RuntimeError("repo root (holding experiments/ and data/) not found")


ROOT = _repo_root()
sys.path.insert(0, ROOT)

from experiments.equivalence_classes.lib.autcanon import (  # noqa: E402
    aut_canon, is_automorphism, phi_str,
)
from experiments.equivalence_classes.lib.words import (  # noqa: E402
    apply_hom, canon_pair, replay_move,
)

PROBE = os.path.join(ROOT, "results", "equivalence_classes", "probe",
                     "probe_seam_34_1000.json")
MANIFEST = os.path.join(ROOT, "results", "equivalence_classes",
                        "classes_126_from_greedy_1000000_261_mrl48.jsonl")
EXPECTED = {"21_3", "21_29"}


def replay(root, path):
    """Start at the root's Aut-canonical rep; apply each (move, phi) and check the claim."""
    cur = aut_canon(root)[1]
    for i, (move, phi, claimed) in enumerate(path):
        move, claimed = tuple(move), tuple(claimed)
        if not is_automorphism(phi):
            raise AssertionError(f"step {i}: phi is not an automorphism of F2: {phi_str(phi)}")
        moved = replay_move(cur, move)
        got = canon_pair(apply_hom(moved[0], phi), apply_hom(moved[1], phi))
        if got != claimed:
            raise AssertionError(f"step {i}: replayed {got}, certificate claims {claimed}")
        cur = claimed
    return cur


def main():
    probe = json.load(open(PROBE))
    classes = {f"C{c['class_id']}": c for c in map(json.loads, open(MANIFEST))}

    edges = [m for m in probe["merges"] if m["kind"] == "aca" and len(m["path_a"] + m["path_b"])]
    edges = [m for m in edges
             if {n for side in ("a", "b") for n in classes[m[side]]["members"]} & EXPECTED]
    if len(edges) != 1:
        print(f"FAIL: expected exactly 1 new edge over {sorted(EXPECTED)}, found {len(edges)}")
        return 1
    edge = edges[0]

    members = {side: classes[edge[side]]["members"] for side in ("a", "b")}
    meeting = tuple(edge["at"])
    print(f"edge     : {edge['a']} == {edge['b']}   -> {members['a']} == {members['b']}")
    print(f"meets at : {meeting}   (Aut-minimal total length {len(meeting[0]) + len(meeting[1])})")

    for side in ("a", "b"):
        c = classes[edge[side]]
        end = replay((c["r1"], c["r2"]), edge[f"path_{side}"])
        steps = len(edge[f"path_{side}"])
        if end != meeting:
            print(f"FAIL: {edge[side]} replayed to {end}, not the meeting class")
            return 1
        print(f"  {edge[side]:>5} ({members[side][0]:>6}): {steps} step(s) -> MATCHES")

    # The whole point: the meeting class is ABOVE the cap the production sweep ran at, so no
    # budget at cap 28 could have reached it.
    total = len(meeting[0]) + len(meeting[1])
    if total <= 28:
        print(f"FAIL: meeting length {total} <= 28; the cap-28 story in section 3b is wrong")
        return 1

    print(f"\nEDGE 136 VERIFIES. {sorted(EXPECTED)} are ACA-equivalent: the same problem.")
    print(f"It meets at total length {total} > 28, the production cap -- which is why the "
          f"cap-28 sweep could never have found it.")
    print("The 261 unsolved presentations are at most 125 distinct problems.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
