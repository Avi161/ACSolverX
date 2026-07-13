"""Phase 1 gate B: the search rediscovers things we already know to be true.

Three checks, all cheap, all must pass before any big run:

  A. **Provenance.** Hypothesis: the upstream 550 -> 261 dedup was an AC-reduction, i.e. each
     unsolved MS(n, w) cell AC-reduces to the rep whose name the grid gives it. If a two-source
     search (the MS cell, and its rep) merges them, the hypothesis holds for that cell -- and
     the machine is validated against 550 independently-produced AC-equivalences.

  B. **The 2 known merges** (19_52 = 18_9, 19_46 = 18_11) must come back out.

  C. **Throughput**, so the big run's wall clock can be projected instead of guessed.
"""
import csv
import os
import random
import sys
import time

# The repo root, found by walking up rather than by counting directory levels. A
# dirname chain encodes this file's depth, so it silently repoints at the wrong
# directory the moment the file moves -- and every path below is then wrong.
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

from experiments.equivalence_classes.search.aca_search import multi_source_search  # noqa: E402
from experiments.equivalence_classes.lib.words import canon_pair, ms_presentation  # noqa: E402

D = os.path.join(ROOT, "data", "ms_unsolved_reps")


def load():
    reps = {r["name"]: (r["r1"], r["r2"])
            for r in csv.DictReader(open(os.path.join(D, "ms_reps_unsolved.csv")))}
    rows = list(csv.reader(open(os.path.join(D, "ms_solved_grid.csv"))))
    ns = [c for c in rows[0][1:] if c.strip()]
    cells = [(r[0], int(n), r[1 + j].strip())
             for r in rows[1:] if r[0]
             for j, n in enumerate(ns)
             if r[1 + j].strip() and r[1 + j].strip() != "trivial"]
    return reps, cells


def main():
    reps, cells = load()
    rng = random.Random(7)

    # --- A: provenance, on cells where the rep is NOT already the canonical MS pair ---
    print("=== A. provenance: does MS(n,w) AC-reduce to the rep the grid names? ===")
    hard = [c for c in cells if canon_pair(*ms_presentation(c[1], c[0])) != canon_pair(*reps[c[2]])]
    print(f"    cells whose rep differs from the raw MS pair: {len(hard)}/{len(cells)}")
    trials = rng.sample(hard, 12)
    ok = 0
    for (w, n, name) in trials:
        ms = ms_presentation(n, w)
        rp = reps[name]
        tot = max(len(ms[0]) + len(ms[1]), len(rp[0]) + len(rp[1]))
        t0 = time.time()
        dsu, merges, _, stats = multi_source_search(
            [(f"MS({n},{w})", ms[0], ms[1]), (name, rp[0], rp[1])],
            nodes_per_source=600, max_total=tot + 2, seam_only=False)
        merged = dsu.find(0) == dsu.find(1)
        ok += merged
        print(f"    MS({n},{w:<7s}) -> {name:<6s} : "
              f"{'MERGED' if merged else 'not found':<10s} "
              f"({stats['popped']} pops, {stats['states']} states, {time.time()-t0:.1f}s)")
    print(f"    => {ok}/{len(trials)} confirmed\n")

    # --- B: the two known merges ---
    print("=== B. the 2 merges the 1M-node sweep found by accident ===")
    for (a, b) in [("19_52", "18_9"), ("19_46", "18_11")]:
        pa, pb = reps[a], reps[b]
        tot = max(len(pa[0]) + len(pa[1]), len(pb[0]) + len(pb[1]))
        t0 = time.time()
        dsu, merges, _, stats = multi_source_search(
            [(a, pa[0], pa[1]), (b, pb[0], pb[1])],
            nodes_per_source=800, max_total=tot + 2, seam_only=False)
        merged = dsu.find(0) == dsu.find(1)
        kinds = {m["kind"] for m in merges}
        print(f"    {a} = {b} : {'MERGED' if merged else 'NOT FOUND':<10s} {kinds}"
              f" ({stats['popped']} pops, {stats['states']} states, {time.time()-t0:.1f}s)")

    # --- C: throughput ---
    print("\n=== C. throughput ===")
    names = list(reps)[:20]
    for seam_only in (True, False):
        t0 = time.time()
        _, mg, _, stats = multi_source_search(
            [(n, *reps[n]) for n in names],
            nodes_per_source=300, max_total=28, seam_only=seam_only)
        dt = time.time() - t0
        lbl = "seam" if seam_only else "full"
        print(f"    {lbl}: {stats['popped']} pops in {dt:.1f}s "
              f"= {stats['popped']/dt:.0f} pops/s, {stats['states']} states "
              f"({stats['states']/max(stats['popped'],1):.1f} new states/pop), "
              f"{len(mg)} merges")


if __name__ == "__main__":
    main()
