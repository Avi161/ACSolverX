"""Exhaustive bounded AC balls around AK(3) and the orbit-2 rep.

Question: is the second Aut-orbit at the 13-floor (ORBIT2, reached via the
universal stable move + 10 AC moves from φ(AK3)) reachable from AK(3) by
CLASSICAL AC moves through presentations of small total length — or did the
stabilisation cross a genuine wall?

Method: BFS the full inverse-closed move set (``seam_only=False`` — each move
is a Definition 2.1 move up to conjugation, and the set is closed under
inverses, so reachability within a ceiling is symmetric) from each root,
keeping every state with total length ≤ L. If the frontier empties before the
1000-pop cap (repo hard rule), the ball is EXHAUSTED: it is the entire
connected component of the root in the ≤L subgraph of the AC graph. Two
exhausted, disjoint balls PROVE no classical AC path ≤ L joins the roots.

Run from the repo root:
    PYTHONHASHSEED=0 .venv/bin/python3 -m \
        experiments.stable_ac.cov.ak_3_universal_test.ball
"""

from experiments.equivalence_classes.lib.acmoves import canon, children
from experiments.equivalence_classes.lib.autcanon import aut_canon
from experiments.stable_ac.cov.ak_3_universal_test.sweep import AK3, ORBIT2

POP_CAP = 1000                  # repo hard cap — never raise
CEILINGS = (13, 14, 15, 16, 17, 18, 19, 20)

_aut_cache = {}


def orbit_rep(state):
    if state not in _aut_cache:
        _aut_cache[state] = aut_canon(state)[1]
    return _aut_cache[state]


def ball(root, total_cap):
    s0 = canon(*root)
    seen = {s0}
    frontier = [s0]
    pops = 0
    exhausted = True
    while frontier:
        if pops >= POP_CAP:
            exhausted = False
            break
        state = frontier.pop()
        pops += 1
        for child in children(state[0], state[1], cap=total_cap - 1,
                              seam_only=False):
            if len(child[0]) + len(child[1]) > total_cap or child in seen:
                continue
            seen.add(child)
            frontier.append(child)
    return seen, exhausted, pops


def main():
    ak3_rep = aut_canon(AK3)[1]
    o2_rep = aut_canon(ORBIT2)[1]
    for cap in CEILINGS:
        balls = {}
        for name, root in (("AK3", AK3), ("ORBIT2", ORBIT2)):
            seen, exhausted, pops = ball(root, cap)
            floors = sorted(s for s in seen if len(s[0]) + len(s[1]) == 13)
            by_orbit = {}
            for s in floors:
                rep = orbit_rep(s)
                tag = ("AK3-orbit" if rep == ak3_rep else
                       "ORBIT2" if rep == o2_rep else f"OTHER:{rep}")
                by_orbit[tag] = by_orbit.get(tag, 0) + 1
            balls[name] = seen
            print(f"cap {cap} {name}: {len(seen)} states, "
                  f"{'EXHAUSTED' if exhausted else 'TRUNCATED'} "
                  f"at {pops} pops; 13-floor by orbit: {by_orbit}", flush=True)
        inter = balls["AK3"] & balls["ORBIT2"]
        print(f"cap {cap}: ball intersection = {len(inter)} states"
              + (" — DISJOINT" if not inter else f" e.g. {sorted(inter)[0]}"),
              flush=True)


if __name__ == "__main__":
    main()
