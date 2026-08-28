# W3b: the AK(3) μ-ladder orbit set carries no spherical link — 12,064/12,064 decided or declared

Date: 2026-08-28 · Checkers: `checkers/ak3_orbit_regen.py` (phase 1),
`checkers/ak3_orbit_thickenability.py` (phase 2) · all runs guarded
(`scripts/run_proof_guarded.py`, 60 s slices, resumable).

Complete sweep of the certified planarity dispatch over every orbit of
AK(3)'s CoV μ-ladder, in all eight signed relabels. **Zero spherical
verdicts. Zero tripwire events.**

---

## Method

**Phase 1 — the orbit set, persisted.** The committed AK(3) ladder rows
(`results/stable_ac/mu_scan/mu_ladder_ak3_only_r20_b32_mrl24.jsonl`) are
single *summary* rows; the per-orbit representatives were never persisted.
`ak3_orbit_regen.py` calls `experiments/stable_ac/cov/mu_ladder_big.climb_one_big`
— imported, unmodified — on AK(3)'s canonical rep `(YXYxyx, YYYYxxx)` at
`rungs=20, beam=32, cap=24, stop_mu=12`, deterministic budgets only
(`time_per_class_s=0`, so the run is machine-independent), and writes the
1,508 orbit rows with full provenance to
`checkers/out/ak3_orbits_r20_b32_c24.jsonl`.

The regeneration agrees with the committed summary on **every quantity that
summary persists**: `n_orbits_seen = 1,508`, `mu_in = 13`, `best_mu = 13`,
`hits_stop = false`, and the full rung-by-rung `new_orbits` vector

```
1, 10, 44, 101, 74, 80, 79, 74, 92, 85, 75, 80, 89, 102, 90, 93, 81, 99, 81, 77
```

reproduced element for element (plus rung 0, the original). This is
agreement on all recorded counts, **not** a byte comparison of
representatives — the representatives did not previously exist on disk, so
there is nothing older to diff them against. The 1,508 rows carry 1,508
distinct `rep`s and 1,508 distinct pairs; rungs 0–20, μ ∈ [13, 50], total
relator length ∈ [13, 90].

**Phase 2 — the dispatch.** Every orbit pair enters as its **8 signed
permutation relabels** (`x↔y` swap × invert `x` × invert `y`), because the
Neuwirth/greedy machinery reads strings, not orbits. Each of the 12,064
resulting states goes through the PROVEN solver ladder of the two-hop
certificate, imported unmodified as
`two_hop_cov_thickenability_certificate._dispatch`:

| order | solver | decides |
|---:|---|---|
| 1 | `neuwirth_rank_solver.solve_spherical` | connected loopless **K4, K4−e, C4** links |
| 2 | `neuwirth_p4_solver.solve_four_germ_spherical` | **P4** central-gap schemes |
| 3 | `neuwirth_one_loop_solver.solve_one_loop_spherical` | **one loop** over a positive parallel K4/K4−e core |
| 4 | `neuwirth_paw_one_loop_solver.solve_paw_one_loop_spherical` | one-loop **parallel paw** |

Each solver **fails closed** outside its proved support class. A state no
solver covers is recorded `UNSUPPORTED` — never guessed, and counted as a
headline number below. The sweep is sliced and resumable: results append to
`checkers/out/ak3_orbit_thick_results.jsonl` keyed by `(orbit, relabel)`,
and reruns skip done keys, so the 60 s guard kill mid-slice is a pause, not
a loss.

**Tripwire.** A `SPHERICAL_REQUIRES_REGINA` verdict halts the sweep and is
quarantined as a *suspected bug* per
`experiments/stable_ac/thickenable/NEUWIRTH_FEASIBILITY.md` — Pipeline B
(the independent Regina `isBall` validator) does not exist, and that memo's
riskiest-step finding is that a sign or consistency error in Pipeline A
"does not fail loudly — it silently prints a proof". **No such verdict
occurred.**

---

## Results

| quantity | value |
|---|---:|
| orbits swept | **1,508 / 1,508** |
| relabels per orbit | 8 |
| decisions | **12,064 / 12,064** (100 % coverage) |
| `NOT_SPHERICAL` | **12,016** (99.60 %) |
| `UNSUPPORTED` | **48** (0.40 %) |
| `SPHERICAL_REQUIRES_REGINA` | **0** |
| distinct deduped pairs | **12,064** (every relabel string distinct; no cache hits) |
| orbits fully decided (8/8 `NOT_SPHERICAL`) | **1,502** |
| orbits fully undecided (8/8 `UNSUPPORTED`) | **6** |
| orbits with a *mixed* verdict | **0** |

### UNSUPPORTED is the headline number

**48 of 12,064 decisions — 6 orbits — are not decided by anything. They are
not negatives.** The verdict is exactly "no proved solver covers this link's
support class", and the honest reading is that the ladder's coverage, not
the geometry, ran out. The six:

| orbit | rung | μ | relator lengths | representative relabel (index 0) |
|---:|---:|---:|---|---|
| 164 | 5 | 15 | 9 + 10 | `YXYxYxyXy`, `YxyXyxYxYX` |
| 373 | 7 | 17 | 9 + 10 | `XYXyXyxYx`, `YXYXyxYxyx` |
| 864 | 13 | 20 | 21 + 6 | `YXyXYXYXyXYxyxyxYxyxy`, `YxYXYX` |
| 398 | 8 | 21 | 13 + 10 | `YXyxYXyXYxyXy`, `YXYxyxYXyx` |
| 143 | 4 | 26 | 19 + 14 | `XyXYXyxYXyxYxyXYxYx`, `YXyxYXyxYXyxYx` |
| 172 | 5 | 28 | 23 + 12 | `XXyxyXyxyXyxyxYXYxxYXYx`, `YYXYxyxyXyxy` |

That the six are undecided on **all 8** relabels and no orbit is mixed is a
consistency check that fell out of the sweep rather than being asserted: the
signed relabel group permutes germ labels and cannot change the link graph's
isomorphism type, so support-class coverage must be a relabel invariant, and
it is — 0 mixed orbits out of 1,508.

### Per-μ census of decided orbits

| μ | decided | undecided | decisions |
|---:|---:|---:|---:|
| 13 | 2 | 0 | 16 |
| 14 | 5 | 0 | 40 |
| 15 | 34 | 1 | 280 |
| 16 | 35 | 0 | 280 |
| 17 | 137 | 1 | 1,104 |
| 18 | 74 | 0 | 592 |
| 19 | 217 | 0 | 1,736 |
| 20 | 103 | 1 | 832 |
| 21 | 223 | 1 | 1,792 |
| 22 | 89 | 0 | 712 |
| 23 | 144 | 0 | 1,152 |
| 24 | 56 | 0 | 448 |
| 25 | 100 | 0 | 800 |
| 26 | 37 | 1 | 304 |
| 27 | 55 | 0 | 440 |
| 28 | 24 | 1 | 200 |
| 29 | 37 | 0 | 296 |
| 30 | 18 | 0 | 144 |
| 31 | 32 | 0 | 256 |
| 32 | 10 | 0 | 80 |
| 33 | 15 | 0 | 120 |
| 34 | 10 | 0 | 80 |
| 35 | 11 | 0 | 88 |
| 36 | 4 | 0 | 32 |
| 37 | 8 | 0 | 64 |
| 38 | 3 | 0 | 24 |
| 39 | 6 | 0 | 48 |
| 40 | 4 | 0 | 32 |
| 41 | 3 | 0 | 24 |
| 42 | 1 | 0 | 8 |
| 43 | 1 | 0 | 8 |
| 44 | 1 | 0 | 8 |
| 46 | 1 | 0 | 8 |
| 47 | 1 | 0 | 8 |
| 50 | 1 | 0 | 8 |
| **total** | **1,502** | **6** | **12,064** |

Coverage is uniform across the ladder: the μ = 13 floor (AK(3)'s own two
orbits) is fully decided, and so is every shell up to μ = 50. The six
undecided orbits sit at μ ∈ {15, 17, 20, 21, 26, 28}, in the crowded middle
of the distribution, with no concentration at either end.

---

## What this does not establish

**The Aut-coverage gap.** Eight signed relabels are *not* the Aut(F₂)-orbit
of a pair. They are the subgroup generated by the generator swap and the two
generator inversions — order 8 — inside an infinite group. Every orbit in
this sweep was tested at 8 points of an infinite set, so "the orbit carries
no spherical link" is **not** what was measured; what was measured is "these
8 strings carry no spherical link". A different automorphism of the same
orbit could present a different link graph, including one in a support class
the ladder decides. This gap is the sweep's main limitation and no result
here should be read past it.

**One-sidedness: a null is a bounded null.** Per NEUWIRTH_FEASIBILITY §(a),
the payoff is one-sided. A *positive* (thickenable) settles a state by
Lackenby Thm 1.3; a *negative* settles nothing, because stable-ACC only
requires that some state reachable by stable AC moves be thickenable, and
one is explicitly allowed to pass through non-thickenable states. The
12,016 `NOT_SPHERICAL` verdicts therefore prune, and do not decide. Adding
the 48 `UNSUPPORTED`, the result is a **bounded null**: no spherical link was
found *within* the 8-relabel window of these 1,508 orbits, *within* the four
proved support classes. Only a validated positive decides anything, and
there was none.

**The exact nonclaim.** No AK(3) claim, no stable AC claim, no AC claim is
made here. In particular: nothing here says AK(3) is not AC-trivial, not
stably AC-trivial, or not thickenable. Had the sweep produced a
`SPHERICAL_REQUIRES_REGINA` verdict, it would first have been quarantined as
a suspected Pipeline-A bug pending independent rotation replay and Regina
`isBall` on a separately built `N(K)` (Pipeline B is absent); and *only if
validated* would it have proved AK(3) **stably** AC-trivial — stably, never
unstably, because the states here are reached from AK(3) by CoV μ-ladder
steps, which are stable moves, and a solve or certificate from a transformed
start proves the original stably AC-trivial and nothing sharper (per the
`orbit_greedy` rule in `experiments/CLAUDE.md`).

---

## Reproduce

```bash
# phase 1 (needs python >= 3.12 + numba/numpy; deterministic)
python3 fable/proofs/checkers/ak3_orbit_regen.py 20 32 24

# phase 2, sliced and resumable; repeat until the results file reaches 12,064 lines
python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- \
  python3 fable/proofs/checkers/ak3_orbit_thickenability.py START END
```

Artifacts: `checkers/out/ak3_orbits_r20_b32_c24.jsonl` (1,508 orbit rows,
full provenance) and `checkers/out/ak3_orbit_thick_results.jsonl` (12,064
decision rows, one per `(orbit, relabel)`).
