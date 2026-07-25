# AK(3) alternating two-cross implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` (recommended) or
> `superpowers:executing-plans` to implement this plan task-by-task. Steps
> use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove that every exactly-two-cross \(B/D\) history with a final
one-\(z\) eliminator returns classically to AK(3).

**Architecture:** For the only coupled exponent-feasible branch, quotient
by the original \(D\)-normal closure. This erases the first cross and
reduces the final target to the proved HNN tail family. Evaluation of the
second cross identifies the actual survivor with a signed conjugate of the
standard endpoint.

**Tech Stack:** HNN quotients, stable-letter exponent, torus weight,
evaluation, fixed-relator normal-closure lifting, Markdown proof,
dependency-free Python replay.

## Constraints

- Work only in the isolated `codex/proofs` worktree.
- Do not quotient by the modified \(B_1\); quotient by original \(D\).
- Do not use bounded conjugator search as completeness evidence.
- Cover both multiplication sides and all four sign pairs.
- Preserve the one-way theorem's source-restoration hypotheses.
- Distinguish stable deletion from classical endpoint equivalence.
- State that AK(3) remains open.
- Commit and push after verification.

---

### Task 1: Coupled quotient theorem

**Files:**

- Create:
  `literature/proofs/AK3_TWO_CROSS_FEEDBACK_SELF_LOOP.md`

- [x] Derive the two alternating target orders.
- [x] Prove only “\(D\) targets \(B\), then \(B_1\) targets \(D\)” with
  the second target eliminated is a new exponent-feasible branch.
- [x] Quotient by original \(D\) and invoke the HNN classification.
- [x] Prove \(\delta=\eta\) and \(n=\epsilon+\eta\).
- [x] Evaluate the second cross and identify the survivor.

### Task 2: Exact replay

**Files:**

- Create:
  `tests/stable_ac/test_two_cross_feedback.py`

- [x] Pin all four aligned sign histories and tails.
- [x] Pin each survivor as a signed conjugate of \(D(e_n)\).
- [x] Pin the exact endpoint conjugacy to \(D(xt)\).
- [x] Pin the opposite-order exponent obstruction.

### Task 3: Audit and checkpoint

**Files:**

- Modify: `results/stable_ac/theory/AK3_DIRECT_STABLE_THEORY.md`
- Modify: `AGENTS.md`

- [x] Add the theorem and narrow the cross frontier to at least three
  alternating events.
- [x] Record the original-source quotient trick in `AGENTS.md`, then read
  it back.
- [x] Run all related proof replays and diff checks.
- [x] Obtain two hostile reviews of the actual theorem and replay.
- [x] Commit and push the verified checkpoint.
