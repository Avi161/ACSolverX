# AK(3) Central-Quotient Conjugacy Criterion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove and replay that weight plus projected conjugacy in
\(C_3*C_4\) exactly classifies conjugacy in the AK(3) torus-knot quotient.

**Architecture:** Use the existing exact amalgam normal form, discard its
central exponent to project, and implement the standard cyclic conjugacy
test for a free product of finite cyclic groups.

**Tech Stack:** Markdown proof, pure Python, repository amalgam normal
form, `runpy`.

## Global Constraints

- The criterion is for group conjugacy, not a new AC invariant.
- Failure of the criterion is not an AC obstruction.
- No AC graph search.
- AK(3) remains open.

---

### Task 1: Replay the quotient conjugacy criterion

**Files:**
- Create: `tests/stable_ac/test_central_quotient_conjugacy_criterion.py`

- [x] Implement projection, cyclic reduction, and conjugacy keys for
  \(C_3*C_4\).
- [x] Pin central shifts: same projection, weight difference \(12k\).
- [x] Pin positive and negative conjugacy examples.
- [x] Pin representative HNN endpoints against \(D_p\).
- [x] Replay through repository-root `runpy`.

### Task 2: State and apply the theorem

**Files:**
- Create: `literature/proofs/AK3_CENTRAL_QUOTIENT_CONJUGACY_CRITERION.md`
- Modify: `results/stable_ac/theory/AK3_DIRECT_STABLE_THEORY.md`
- Modify: `AGENTS.md`

- [x] Prove the kernel and central-weight lift.
- [x] Prove the \(C_3*C_4\) conjugacy decision procedure.
- [x] Apply it to weight-\(\pm1\) prefix-`DB` survivors.
- [x] State explicitly that criterion failure is not AC inequivalence.
- [x] Run related replays, diff checks, and two hostile reviews.
- [x] Commit and push the verified checkpoint.
