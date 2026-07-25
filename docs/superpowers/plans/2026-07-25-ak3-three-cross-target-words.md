# AK(3) Three-Cross Target-Word Classification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Classify all eight three-event target words and reduce the full
exactly-three-cross frontier to two explicit killer corridors.

**Architecture:** Use exponent and the existing quotient theorems for
unbounded closure. Add a dependency-free replay only for the newly exposed
untwisted `DBB` seam corridor.

**Tech Stack:** Markdown proofs, pure Python word reduction, repository
word utilities, `runpy` replay.

## Global Constraints

- Theory before implementation.
- CPU only; no AC graph search.
- Do not infer that a killer is a meridian.
- State arbitrary bridge/twist cases as open.
- AK(3) remains open.

---

### Task 1: Replay the target-word arithmetic

**Files:**
- Create: `tests/stable_ac/test_three_cross_target_words.py`

- [x] Pin the `BBD`, `BDD`, and `DDB` exponent identities.
- [x] Pin the six feasible `DBB` sign rows, orientations, tail weights,
  survivor exponents, and survivor weights.
- [x] Replay the test functions through repository-root `runpy`.

### Task 2: Replay the untwisted `DBB` seams

**Files:**
- Modify: `tests/stable_ac/test_three_cross_target_words.py`

- [x] Reconstruct the signed cyclic cross sets without importing the
  strict-corridor verifier.
- [x] Assert the exact counts \(16,416,522,69\).
- [x] Assert the unique evaluated survivor class \(D_p^{\pm1}\).
- [x] Replay the complete new test file.

### Task 3: Prove and report the classification

**Files:**
- Create: `literature/proofs/AK3_THREE_CROSS_TARGET_WORD_CLASSIFICATION.md`
- Modify: `results/stable_ac/theory/AK3_DIRECT_STABLE_THEORY.md`
- Modify: `AGENTS.md`

- [x] Prove `BBD`, `BDD`, and `DDB` close with arbitrary conjugators.
- [x] State the `DBB` killer reduction and untwisted closure.
- [x] Combine with the one-way and strict alternating theorems to classify
  all eight target words.
- [x] Update the theory ledger and lessons without broadening scope.
- [x] Run all related proof replays, placeholder scans, and diff checks.
- [x] Complete separate algebra and scope hostile reviews.
- [ ] Commit and push the verified checkpoint.
