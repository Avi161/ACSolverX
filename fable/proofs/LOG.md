# Fable lane log

## 2026-08-28 · cycle 1 (setup)

Lane created on branch `fable/proofs`. Charter in `PROGRAM.md`. W1 selected as the
opening workstream: finite AC-graph decision for the MMS02 bridge — decisive in both
outcomes, complete-closure (not budgeted-search) methodology, and disjoint from the
codex class-two tower. Opus agents launched: plan review (ac-advisor), independent
derivation of the A5 data, and a known-results sweep on AC-graphs of finite groups.
No AK(3), stable AC, or AC claim is made.

## 2026-08-28 · cycle 1 · `1e8d86b`

W1 first theorem: complete A5 closure proves the A5 obstruction blind for the full
bridge (all 6 nontrivial hom classes connect; surjective orbits are all of A5^3 minus
the frozen identity tuple; controls green). Note: `W1_BRIDGE_FINITE_TEST.md`. Next:
generator-reduced move set, larger quotients (W1b), and rank-3 greedy preflight on
Tpub within the 1,000-node cap.

## 2026-08-28 · cycle 2 · `6a9a257`

ac-advisor BLOCK on W1 sustained and repaired: the finite test was theorem-forced
(vacuity lemma; BLM 2005). W1 closed as a method-closure result with full retraction
of the earlier inferences; five lessons recorded; W3 repointed at the Lackenby
thickenability lever (thickenable => unstable AC-trivializable), pending its own
advisor gate. No AK(3), stable AC, or AC claim.

## 2026-08-28 · cycle 3 · `f7a696d`

Composed the MMS02 corridor with the mu/orbit machinery (own idea): mu(Q)=21 (new
orbit), Tpub floor state proved a disguised AK(3) self-loop (W1c downgraded), and a
second elimination yields a new mu=14 stable rep. All basins drain to the 13-floor.
Note: W4_CORRIDOR_REPS.md. No AK(3), stable AC, or AC claim.

## 2026-08-28 · cycle 4 · `975a5ba`

W2 census: the period-two backward system has 17 essential gauge-free solutions at
caps (12,12,12,g5) — the witness plus 16 others, all hyperbolic-S, independently
verified. Quantifies the uniqueness gap: the codex anchored family (1.10) covers one
of 17. Next: layer-1 liveness per extra baseline (W2b). Note:
W2_PERIOD_TWO_BASELINE_CENSUS.md. No AK(3), stable AC, or AC claim.

## 2026-08-28 · cycle 5 · `1b982fe`

W2b liveness sweep: six of the 17 baselines are live at the relation-module layer
(witness + 5; four share the witness R,S). Eleven inconclusive, zero dead. The
gauge-representative dependence of one-hop windows was caught by the witness control
and absorbed into the method. Note: W2B_BASELINE_LIVENESS.md.

## 2026-08-28 · cycle 6 · `6f72ee0`

W2c cap curve: 17 -> 36 -> 55 -> 67 essential baselines at caps 12-15, strictly
growing. With W2b (6 live at cap 12), the period-two route needs a uniform argument;
per-baseline towers cannot terminate. Addendum in W2_PERIOD_TWO_BASELINE_CENSUS.md.

## 2026-08-28 · cycle 7 · `cbe0d8c`

W3a: independent component probe cross-validates the certified ceiling-17 closure
(1,000 states exactly) and proves ceiling 18 exceeds the local pop law (>=1,243).
Colab handoff recorded. Note: W3A_COMPONENT_CEILING.md.

## 2026-08-28 · cycle 8 · `bb29a0e`

W3b orbit sweep: all 1,508 AK(3) μ-ladder orbits × 8 signed relabels decided —
12,064/12,064, of which 12,016 NOT_SPHERICAL and 48 UNSUPPORTED (6 orbits, none
mixed). Zero SPHERICAL verdicts, so the Pipeline-B tripwire never fired. The orbit
representatives are now a first-class artifact, reproducing every count the committed
ladder summary holds. Bounded null: 8 relabels are not the Aut(F₂)-orbit, and only a
validated positive decides. Note: W3B_ORBIT_THICKENABILITY.md. No AK(3), stable AC, or
AC claim.

## 2026-08-28 · cycle 9 · `1721718`

W2d uniform structure: the growing period-two baseline family collapses to a
six-parameter normal form. Each step `NEW = P·(conj of Q^-1)` obeys
`|NEW| = |P| + |cyc Q^-1| + 2k - 2d`, so a length cap PINS the conjugator to a
literal prefix of `P^-1` — one lemma at all three levels, indexing a chain by three
prefix lengths, three rotation indices and a terminal conjugator. New checker
`period_two_normal_form.py` runs it as a generator against the census enumeration:
exact at caps 12–17 (17/36/55/67/91/106, 0 missed, 0 spurious), with a non-vacuity
control that asserts strict pinning at cap 19 where it must fail (64 census R, 32
pinned, 32 missed). Also: the U-fiber depends on S only through `cyc(S)` (proved from
the verifier's conditions), so 17 chains are 9 invariant triples and one of W2b's six
live baselines is the witness's own class at a different S representative; the R-count
is exponential, not linear. Note: `W2D_UNIFORM_STRUCTURE_DRAFT.md` (DRAFT; only the
normal form is checker-backed). Limits: nothing claimed past cap 18, GPAD ceiling 5
under-counts, pinning lemma unproved. No AK(3), stable AC, or AC claim.
