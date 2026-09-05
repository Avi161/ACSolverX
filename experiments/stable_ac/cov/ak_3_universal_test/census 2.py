"""Orbit-census loop over the length-13 floor of AK(3)'s stable-AC class.

Every sweep row's min_pair with total 13 is a floor state; its Aut(F₂)-orbit
is computed exactly (equivalence_classes' Whitehead machinery, certificate
checked). Loop: sweep every floor state not yet used as a CoV base
(words 2..5, 1000-node greedy per start — the repo cap), recompute the orbit
set, repeat until a round adds no new floor state. Converging at N orbits is
the structural claim: within words ≤7 at depth 1 (+ iterated depth ≤5 beams)
and 1000-node greedy descents, the reachable floor of AK(3)'s stable class
decomposes into exactly N changes of variables.

Run from the repo root:
    PYTHONHASHSEED=0 .venv/bin/python3 -m \
        experiments.stable_ac.cov.ak_3_universal_test.census
"""

import time

from experiments.equivalence_classes.lib.autcanon import aut_canon, check
from experiments.equivalence_classes.lib.words import canon_pair
from experiments.stable_ac.cov.ak_3_universal_test import sweep as S

FLOOR = 13
MAX_ROUNDS = 8
TIME_BOX_S = 40 * 60
CENSUS_MAX_LEN = 5


def floor_orbits(rows, cache):
    """{aut_rep: {canonical floor pair}} over all rows' min_pair at FLOOR."""
    reps = {}
    for r in rows:
        if r["min_total"] != FLOOR:
            continue
        key = canon_pair(r["min_pair"][0], r["min_pair"][1])
        if key not in cache:
            _, rep, phi = aut_canon(key)
            assert check(key, rep, phi), key
            cache[key] = rep
        reps.setdefault(cache[key], set()).add(key)
    return reps


def main():
    cache = {}
    t_end = time.time() + TIME_BOX_S
    S.run_baseline._repair_jsonl(S.OUT_PATH)
    rows = S.load_rows()
    seen = {r["canon"] for r in rows}

    with open(S.OUT_PATH, "a") as out_f:
        for rnd in range(1, MAX_ROUNDS + 1):
            rows = S.load_rows()
            orbs = floor_orbits(rows, cache)
            swept = {S.canon_key(r["base_r1"], r["base_r2"]) for r in rows}
            todo = []
            for rep in sorted(orbs):
                for st in sorted(orbs[rep]):
                    if S.canon_key(*st) not in swept:
                        todo.append(st)
            n_states = sum(len(v) for v in orbs.values())
            print(f"[census] round {rnd}: {len(orbs)} orbits, "
                  f"{n_states} floor states, {len(todo)} unswept", flush=True)
            if not todo:
                print("[census] converged — every floor state swept", flush=True)
                break
            for b in todo:
                if time.time() > t_end:
                    print("[census] time box hit", flush=True)
                    return
                name = f"census:{b[0]}|{b[1]}"
                S.control_row(out_f, seen, name, tuple(b))
                S.sweep(out_f, seen, "census", name, tuple(b), CENSUS_MAX_LEN)

    rows = S.load_rows()
    orbs = floor_orbits(rows, cache)
    hits = [r for r in rows if r["solved"] or r["min_total"] < FLOOR]
    print(f"\n[census] FINAL: {len(rows)} rows, {len(hits)} hits, "
          f"{len(orbs)} Aut-orbit(s) at the {FLOOR}-floor:", flush=True)
    for rep in sorted(orbs):
        print(f"  rep {rep[0]}|{rep[1]}: {len(orbs[rep])} canonical floor "
              f"states", flush=True)


if __name__ == "__main__":
    main()
