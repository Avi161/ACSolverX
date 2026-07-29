# Period-Two Tree-Flow Factorization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` task by task with independent
> specification and quality review.

**Goal:** Prove and certify unique linear forest flow, anchored single-source
decomposition, affine-quadratic fifteen-bit factorization, and the bounded
counterexample to the currently proposed finite Markov summary.

**Architecture:** Surgically repair source normalization and expose explicit
pair reconstruction, then build one theorem certificate over the approved
subgroup/source/census layers.  Integrate only after focused mathematical
review.

**Scope:** No depth-seven census, no claim that all finite automata fail, and
no claim about the period-two lift, stable AC, or AC.

## Task 1: Collision-safe source normalization and explicit pairing

**Files:**
- Modify: `experiments/stable_ac/depth4_period_two_source_flow_certificate.py`
- Modify: `tests/stable_ac/test_ak_depth_four_period_two_source_flow.py`

- [ ] Write failing tests showing `{(): 1, (C,): -1}` normalizes to zero and
  the magnitude-two collision sums correctly.
- [ ] Replace raw-source `clean_vector` normalization with
  `lift.add_vectors(source)`.
- [ ] Extract `build_l0_direction_from_pairs(source, pairs)` (or an equivalent
  narrowly named helper) from the existing edge replay.  Preserve exact path
  endpoint, edge-label, component-shift, and zero-image assertions.
- [ ] Keep `build_l0_direction(source)` behavior identical for canonical
  callers by delegating to the new helper after deterministic pairing.
- [ ] Add a crossed Result 153 pairing fixture: path metadata must change,
  while all five sparse variables remain identical.
- [ ] Run only the Task 1 source-flow/subgroup focused tests, self-review,
  commit, and push with the required UTC log sequence.

## Task 2: Tree-flow, anchoring, and affine-quadratic certificate

**Files:**
- Create: `experiments/stable_ac/depth4_period_two_tree_flow_factorization_certificate.py`
- Create: `tests/stable_ac/test_ak_depth_four_period_two_tree_flow_factorization.py`

- [ ] Write the failing theorem-certificate test with fields for the complete
  cover, parity-kernel/free ranks, $K$ index/rank, two tree components,
  pairing independence, raw-collision regressions, anchored fixtures,
  quadratic identities, and no-Markov fixture.
- [ ] Implement `source_scalar` and `anchored_direction` using anchor `T`.
  Assert every anchored boundary has zero sums and every direction has empty
  correction image.
- [ ] Implement exact direction addition/scaling helpers without raw-key
  overwrite.
- [ ] Verify anchored decomposition for `TT+tt`, `TTT-cTTT`, both published
  near-survivors, and representatives of the magnitude-two classes.
- [ ] Implement fifteen-bit `syndrome` using the tracked projected evaluator
  plus the full wedge sum, with `Phi_infinity` last.
- [ ] Implement `polarization`; pin the exact near-survivor constant/unary/
  cross bitstrings, a three-direction biadditivity identity, and one complete
  mod-four coefficient period.
- [ ] Implement the explicitly defined finite pair summary.  Assert the two
  near-survivors collide in this summary and their `c,t,T` extensions have the
  six pinned distinct syndromes.
- [ ] Keep all fixture sources at depth at most six.  Run the new focused test
  and Task 1 tests, self-review, commit, and push with UTC logging.

## Task 3: Proof and frontier integration

**Files:**
- Create: `literature/proofs/AK3_DEPTH4_PERIOD_TWO_TREE_FLOW_FACTORIZATION.md`
- Modify: `results/stable_ac/theory/AK3_DEPTH4_HANDOFF.md`
- Modify: `results/stable_ac/theory/AK3_DIRECT_STABLE_THEORY.md`
- Modify: `AGENTS.md` only for newly confirmed reusable lessons.

- [ ] Prove $K\cong F_3$ through the parity-kernel
  Reidemeister--Schreier argument, then prove free tree action and finite
  boundary injectivity by torsion and leaf removal.
- [ ] State flow uniqueness/linearity only for canonical module vectors;
  document the normalization repair and that paths are not invariant.
- [ ] Prove anchored decomposition and the general class-two affine-quadratic
  law, including the mod-four diagonal term.
- [ ] State the no-Markov fixture exactly and limit it to the defined summary.
  Do not claim no larger finite automaton exists.
- [ ] Replace the old transition target in both ledgers with the two open
  refined targets: support-order inversions for finite bits, and exact-prefix
  equality compression/non-regularity for `Phi_infinity`.
- [ ] Run the complete period-two wildcard suite once with retained JUnit and
  actual exit zero; run Markdown/diff checks; obtain independent mathematical
  and whole-range review.
- [ ] Force-add the new ignored proof note, commit `Prove period-two tree-flow
  factorization`, add the UTC log hash follow-up, and push `codex/proofs`.

## Acceptance criteria

- No tracked module imports `.scratch`.
- The collision regression fails before and passes after normalization repair.
- Pairing independence compares variables, not path metadata.
- The general theorem proof does not rely on bounded enumeration.
- Every bitstring is independently replayed from the tracked residual/wedge
  pipeline.
- The no-Markov conclusion names the exact refuted summary and nothing
  stronger.
- Existing 54 period-two tests plus the new tests pass with retained exit
  evidence.
- Final branch and origin are synchronized and no test/search process remains.
