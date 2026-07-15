# AK(3) universal-CoV sweep — results (2026-07-14)

**Question** (user): from AK(3) `xxxYYYY | xyxYXY` (total 13) and its worked-example-C
re-coordinatisation (`z = xyy`, `x = zYY` → `yXXyXXyXXXXXX | yXyXYX`, total 19), does any
universal change of variables `w(z,y)` for x / `w(z,x)` for y — or a chain of them — let a
1,000-node greedy trivialize or reach total length < 13?

**Answer: no.** 390 distinct searches (every universal CoV word of length ≤ 8, both
elimination targets, depth-2 chains through xyy, two beam rounds, an orbit census loop) —
0 solved, 0 states below total 13. Every descent saturates at exactly 13.

**But the floor is not one thing.** The sweep surfaced, and two verified certificates plus an
exhaustive ball enumeration pin down, the following structure:

## Findings

1. **Pure CoV cannot start below 13.** 189 distinct CoV starts exist at word length ≤ 7
   (245 at ≤ 8); the shortest is 13 (`z=xyX, iso=y`). Matches the known Aut-minimum
   (`aut_min_rep_total_length = 13` in `reach_tier_1.csv`).

2. **Two Aut(F₂)-orbits at the 13-floor.** The floor states reached across all 390 searches
   form 12 canonical presentations: 4 in AK(3)'s orbit (rep `YXYxyx|YYYYxxx`) and 8 in a
   second orbit with rep **`YYXXyx | YYYxyXX`** (as relations: `yx = x²y²`, `xy = y³x²`;
   |abelian det| = 1). The census loop (census.py) converged: sweeping every floor state
   yields no third orbit. Orbit-2 is NOT a change of variables of AK(3) (Whitehead canonical
   forms differ; witnesses checked by substitution) — it is not the mirror either, since
   AK(3) is reversal-symmetric.

3. **Certificate 1 — via the universal move** (`ORBIT2_CERTIFICATE.json`, certify.py):
   φ: y ↦ xy (the z = Xy defining-relator isolation, an elementary Nielsen automorphism),
   then **10 Definition-2.1 AC moves** descend canon(φ(AK3)) (16) → `YYxyXX|YYXXXyx` (13),
   never exceeding total 17. Verified end to end by the opposite implementation pairing
   (`words.replay_move`, pure Python) — the same discipline as `verify_proofs.py`.

4. **Certificate 2 — classical, no stabilisation** (`AC17_CERTIFICATE.json`,
   certify_classical.py): AK(3)'s component in the full-move AC graph restricted to total
   length ≤ 17 is **exactly 1,000 states** — enumerated, then **closure-verified** (every
   child of every member stays inside; no pop cap or traversal order in the argument). It
   contains the orbit-2 root, and an explicit **17-move path AK(3) → `YYXXyx|YYYxyXX`**
   inside ceiling 17 verifies by replay. So orbit-2 sits in AK(3)'s *classical* AC class;
   the universal move is a shortcut, not the only door.

5. **Height 17 is exactly the bridge.** At ceiling ≤ 16 the components of AK(3) and orbit-2
   are tiny (≤ 40 and ≤ 33 states), fully exhausted, and **disjoint** — no classical AC path
   of height ≤ 16 joins them. At 17 they merge into the single 1,000-state component.
   AK(3) is an isolated vertex below ceiling 15.

6. **Any trivialization must climb to ≥ 18.** The closed ≤ 17 component has height
   distribution {13: 6, 14: 12, 15: 156, 16: 150, 17: 676} — minimum 13, no trivial pair.
   Self-contained, exhaustive lower bound on the two-hump wall.

7. **Why the 1M-node baseline saw "zero progress".** The seam-only (baseline) move set
   reaches the same 6 floor states at ceiling 17, so the production greedy *visits* orbit-2;
   `min_relator_length` simply cannot distinguish a new Aut-orbit at the same length. The
   floor looked featureless only because length was the only ruler — the orbit census is the
   right instrument (same lesson as the ms640 equivalence work).

8. **Example C specifically:** the greedy from the xyy pair (19) descends back to the floor
   in AK(3)'s own orbit (`YXYxyx|YYYxxxx`, x↔y-swapped AK3) within 1,000 nodes — no better
   than 13, and no orbit escape from that particular start's control row.

## Anatomy of the ≤17 component (Aut-quotient)

The 1,000 states decompose into **168 Aut(F₂)-orbits**; per-orbit Whitehead minimum
(`aut_min`, exact by peak reduction):

| aut_min | 13 | 14 | 15 | 16 | 17 |
|---|---|---|---|---|---|
| orbits | **2** | 5 | 30 | 32 | 99 |

The two aut_min-13 orbits are exactly AK(3)'s and orbit-2's. **No orbit dips below 13**, so
one change of variables applied at ANY state of the ≤17 component still cannot beat the bar
— beating 13 needs height ≥ 18 or ≥ 2 alternating (AC, CoV) phases through states outside
this component. The five aut_min-14 orbits are fresh low-height coordinates for
production-budget searches: `YYXyXyx|YXYXyxx`, `YYXYxyx|YXyXyxx`, `YYXyXyx|YXyxxyX`,
`YYXXXyx|YYxyxyX`, `YXXYx|YYYYXyyyx`.

## Literature fit

- [Havas–Ramsay 2003](https://www.worldscientific.com/doi/10.1142/S0218196703001365):
  every length-13 normally-generating pair is AC-equivalent to (x,y) or to the *unique*
  minimum potential counterexample AK(3). Certificate 2 constructively reproduces a small
  piece of this: orbit-2's rep is length-13 and AC-equivalent to AK(3) — the same AC class.
  The two-Aut-orbit split at that class's floor is a refinement *within* their unique class;
  not stated in the sources checked.
- [Myasnikov–Myasnikov](https://arxiv.org/abs/math/0304305): all length ≤ 12 balanced
  presentations of the trivial group satisfy AC — which is why any state of total ≤ 12 would
  have been decisive.
- **AK(3) is stably AC-trivializable** — proved by Shehper et al. 2024 (the Two-Hump
  paper's group), re-proved by automated deduction in
  [arXiv:2501.18601](https://arxiv.org/abs/2501.18601). So the stable escape exists; this
  experiment shows it is invisible below height 18 in 2-generator moves even after any
  single re-coordinatisation — the third generator (or real height) is doing essential work.

## Files

| file | what |
|---|---|
| `sweep.py` | stages: scan / control / d1 / c / beam / o2 / o2beam (budget hard-capped 1,000) |
| `census.py` | floor-orbit census loop (converged: 2 orbits) |
| `analyze.py` | min_total distributions + per-floor-state orbit attribution |
| `certify.py` / `ORBIT2_CERTIFICATE.json` | φ = (y↦xy) + 10 AC moves, verified |
| `certify_classical.py` / `AC17_CERTIFICATE.json` | closure proof + 17-move classical path, verified |
| `ball.py` | bounded-ball separation (disjoint ≤ 16, merged at 17) |
| `sweep_results.jsonl` | all 390 rows (resume-keyed by canonical start) |
| `test_ak3.py` | 8 checks incl. the solved branch (never hit by the 390 unsolved rows) + both certificates |

Repro (repo root, all ≤ 1,000 nodes):
`PYTHONHASHSEED=0 .venv/bin/python3 -m experiments.stable_ac.cov.ak_3_universal_test.<sweep|census|analyze|ball>`
and `... .certify --verify`, `... .certify_classical --verify`.

## Next steps (production budgets — Colab, user's call)

- **Greedy at 50k–1M nodes from the orbit-2 rep and its 8 floor states.** These coordinates
  were never explored at scale; the 1M-node "zero progress" fact is about the AK(3)-orbit
  start only. Orbit-2 is classically AC-equivalent to AK(3), so trivializing it trivializes
  AK(3) — no stable caveat.
- **Ceiling-18/19 component enumeration** (grows past 1,243 states at 18): does a third
  orbit, or a 12-state, appear? This is the exhaustive version of "what does the wall look
  like one level up".
- **Case (ii) CoV** (mid-search re-coordinatisation) in the cov pipeline: the certificate
  shows orbit switches happen through height-17 saddles; a CoV applied at the floor is the
  cheap way to hop orbits without climbing.
