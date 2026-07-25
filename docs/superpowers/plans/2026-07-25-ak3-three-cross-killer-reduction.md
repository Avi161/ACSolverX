# AK(3) Three-Cross Killer Reduction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove the exact arithmetic reduction for every alternating
three-cross history and certify that every untwisted seam realization
returns to the AK(3) endpoint.

**Architecture:** Separate the unbounded algebra from the finite
certificate. Stable-letter exponent and torus weight handle arbitrary
conjugators; a dependency-free signed-rotation enumerator handles only the
explicitly scoped untwisted seams.

**Tech Stack:** Markdown proofs, pure Python word reduction, repository
word utilities, `runpy` replay.

## Global Constraints

- Theory before implementation.
- CPU only; no AC graph search.
- New theorem and test files only; modify only the theory ledger and the
  required project lessons.
- Every negative is explicitly scoped.
- AK(3) remains open.

---

### Task 1: Pin the arithmetic reduction

**Files:**
- Create: `tests/stable_ac/test_three_cross_killer_reduction.py`

**Interfaces:**
- Consumes: `free_reduce`, `cyc_reduce`, and `inv` from
  `experiments.equivalence_classes.lib.words`.
- Produces: dependency-free `test_*` functions callable through `runpy`.

- [x] Enumerate both alternating target orders and assert the exact
  stable-letter exponent formulas.
- [x] Assert that one order has no third-target one-\(z\) row and that the
  reverse order has exactly six.
- [x] Pin \(\delta\), \(\operatorname{wt}(e)\),
  \(\sigma_z(B_1)\), and evaluated survivor weight in all six rows.
- [x] Run the new test functions through repository-root `runpy`.

### Task 2: Pin the untwisted seam certificate

**Files:**
- Modify: `tests/stable_ac/test_three_cross_killer_reduction.py`

**Interfaces:**
- Consumes: signed cyclic rotations of literal free words.
- Produces: exact counts and the unique evaluated endpoint class.

- [x] Implement minimal helpers for signed rotations, cyclic keys, cross
  products, one-\(z\) normalization, and substitution.
- [x] Assert the exact counts \(16,416,522,69\).
- [x] Assert that every evaluated survivor has the signed cyclic class of
  `TxtxTX`.
- [x] Re-run the complete new test file.

### Task 3: State the theorem without a scope jump

**Files:**
- Create: `literature/proofs/AK3_THREE_CROSS_KILLER_REDUCTION.md`
- Modify: `results/stable_ac/theory/AK3_DIRECT_STABLE_THEORY.md`
- Modify: `AGENTS.md`

**Interfaces:**
- Consumes: the arithmetic identities and finite certificate from Tasks
  1-2.
- Produces: a theorem which separates the arbitrary-conjugator reduction
  from the untwisted finite closure.

- [x] Prove the first alternating order closes using exponent plus the
  two-cross theorem.
- [x] Give the six-row reverse-order exponent/weight table.
- [x] Prove that every feasible endpoint is a weight-\(\pm1\) killer, but
  explicitly reject “killer implies meridian.”
- [x] Prove completeness of the untwisted seam replay and state its exact
  exclusions.
- [x] Update the theory ledger and project lesson.
- [x] Run all related proof replays, placeholder scans, and diff checks.
- [ ] Perform two independent hostile self-review passes: one on algebra,
  one on scope/completeness.
- [ ] Commit and push the verified checkpoint.
