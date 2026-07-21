"""Cross-presentation Aut-orbit collision scan over the CoV sweep jsonls.

Every CoV row is a stable-AC equivalence between its input's orbit
(``aut_canon_orig``) and its output's orbit (``aut_canon_cov``) — the
transform is stabilize/substitute/isolate/destabilize, and Aut-equivalence
implies stable equivalence (the stable ambient principle, the only proved
form). Union-find over orbit canonical strings therefore groups orbits that
are provably stably AC-equivalent, using nothing but data the sweeps already
computed. Trivializable seed orbits: every subset-tier presentation (drawn
from ``ms640_solved.txt``) plus the output orbit of every solved CoV row —
any presentation whose component holds a seed is stably AC-trivializable.

Findings for the 50k aca124 + 10k s60r6 sweeps:
``results/stable_ac/cov/STABLE_ORBIT_LINKS.md``.

Usage: .venv/bin/python3 -m experiments.stable_ac.cov.orbit_links [jsonl ...]
(defaults to the two files above).
"""
import json
import os
import sys
from collections import defaultdict


def find_repo_root(start):
    d = start
    while True:
        if all(os.path.isdir(os.path.join(d, s)) for s in ("experiments", "data")):
            return d
        up = os.path.dirname(d)
        if up == d:
            raise RuntimeError("repo root not found")
        d = up


ROOT = find_repo_root(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_FILES = [
    os.path.join(ROOT, "results/stable_ac/cov",
                 "covsweep_50000_124_subnc2pxysb_mrl24_cyc_aca124_07_21_26.jsonl"),
    os.path.join(ROOT, "results/stable_ac/cov",
                 "covsweep_10000_66_subnc2pxysb_mrl24_cyc_s60r6_07_20_26.jsonl"),
]


def main(paths):
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    orbit_in, kind, covs = {}, {}, defaultdict(set)
    triv_orbits, solved_pres = set(), set()
    for path in paths:
        with open(path) as f:
            for ln in f:
                r = json.loads(ln)
                pid = r["pres_id"]
                if pid not in kind:
                    kind[pid] = ("aca" if isinstance(pid, str)
                                 and pid.startswith("aca_")
                                 else "subset" if isinstance(pid, int)
                                 else "reach")
                if r.get("z_word") is None:
                    if r["solved"]:
                        solved_pres.add(pid)
                    continue
                o, c = r.get("aut_canon_orig"), r.get("aut_canon_cov")
                if not o or not c:
                    continue
                if pid in orbit_in:
                    assert orbit_in[pid] == o, f"inconsistent orbit for {pid}"
                else:
                    orbit_in[pid] = o
                union(o, c)
                covs[pid].add(c)
                if r["solved"]:
                    triv_orbits.add(c)
                    solved_pres.add(pid)

    for pid, o in orbit_in.items():
        # subset tier = rows of ms640_solved.txt: AC-trivializable by data
        if kind[pid] == "subset" or pid in solved_pres:
            triv_orbits.add(o)

    n_kind = {k: sum(1 for p in orbit_in if kind[p] == k)
              for k in ("aca", "subset", "reach")}
    print(f"presentations: {len(orbit_in)} {n_kind} | orbits: {len(parent)} | "
          f"trivializable seeds: {len(triv_orbits)}")

    comp_pres = defaultdict(list)
    for pid, o in orbit_in.items():
        comp_pres[find(o)].append(pid)
    comp_triv = {find(o) for o in triv_orbits}

    merges = {c: ps for c, ps in comp_pres.items() if len(ps) > 1}
    print(f"components holding >1 presentation: {len(merges)}")
    for c, ps in sorted(merges.items(), key=lambda x: -len(x[1])):
        kinds = ",".join(sorted(set(kind[p] for p in ps)))
        flag = " [TRIVIALIZABLE]" if c in comp_triv else ""
        same_orbit = len(set(orbit_in[p] for p in ps)) == 1
        via = "same input orbit" if same_orbit else "via CoV edges"
        print(f"  {len(ps)} pres ({kinds}, {via}){flag}: "
              f"{sorted(map(str, ps))}")

    aca = [p for p in orbit_in if kind[p] == "aca"]
    aca_triv = [p for p in aca if find(orbit_in[p]) in comp_triv]
    print(f"aca classes in a trivializable component: "
          f"{sorted(map(str, aca_triv)) or 'none'}")


if __name__ == "__main__":
    main(sys.argv[1:] or DEFAULT_FILES)
