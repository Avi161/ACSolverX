"""Post-sweep analysis of sweep_results.jsonl.

Two questions the raw rows don't answer directly:
  1. min_total distribution — how far below its start does each CoV'd greedy
     get, per stage? (13 = the AK(3) floor; < 13 would have been a HIT.)
  2. orbit of the floor — every min_pair with total 13: is it in AK(3)'s
     Aut(F₂)-orbit (i.e. the search merely undid the re-coordinatisation and
     slid back to the same hump floor), or did any CoV'd search reach a
     DIFFERENT Aut-orbit at 13? Exact check via equivalence_classes'
     Whitehead machinery (aut_canon carries its own certificate).

Run from the repo root:
    .venv/bin/python3 -m experiments.stable_ac.cov.ak_3_universal_test.analyze
"""

import json
import os
from collections import Counter

from experiments.equivalence_classes.lib.autcanon import aut_canon, check
from experiments.equivalence_classes.lib.words import canon_pair

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(HERE, "sweep_results.jsonl")

AK3 = ("xxxYYYY", "xyxYXY")


def main():
    rows = []
    with open(OUT_PATH) as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                rows.append(json.loads(ln))
    print(f"{len(rows)} rows")

    print("\nmin_total distribution per stage:")
    for stage in ("control", "d1", "c", "beam"):
        srows = [r for r in rows if r["stage"] == stage]
        if not srows:
            continue
        dist = Counter(r["min_total"] for r in srows)
        stuck = sum(1 for r in srows if r["min_total"] >= r["start_total"])
        print(f"  {stage:>7}: n={len(srows):>3} "
              f"dist={dict(sorted(dist.items()))} "
              f"(never below start: {stuck})")

    floors = {}
    for r in rows:
        if r["min_total"] == 13:
            key = canon_pair(r["min_pair"][0], r["min_pair"][1])
            floors.setdefault(key, []).append(r)
    print(f"\ndistinct length-13 floor states (canon up to rotation/inversion/"
          f"swap): {len(floors)}")

    _, ak3_rep, ak3_phi = aut_canon(AK3)
    assert check(AK3, ak3_rep, ak3_phi)
    print(f"AK(3) Aut-canonical rep: {ak3_rep}")

    orbits = {}
    for key, frs in sorted(floors.items(), key=lambda kv: -len(kv[1])):
        total, rep, phi = aut_canon(key)
        assert check(key, rep, phi), key
        orbits.setdefault(rep, []).append((key, len(frs)))
        same = "SAME orbit as AK(3)" if rep == ak3_rep else \
            f"*** DIFFERENT Aut-orbit (aut-min total {total}, rep {rep})"
        print(f"  {key[0]}|{key[1]}  reached by {len(frs):>3} rows  {same}")

    print(f"\n{len(orbits)} distinct Aut(F2)-orbit(s) at the floor")
    if len(orbits) == 1 and ak3_rep in orbits:
        print("every floor state is AK(3) up to change of variables — no CoV "
              "start escaped the orbit within 1000 nodes")


if __name__ == "__main__":
    main()
