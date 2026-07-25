# AK(3) one-way cross-traffic implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` (recommended) or
> `superpowers:executing-plans` to implement this plan task-by-task. Steps
> use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove that every finite one-way \(B/D\) cross history ending in a
one-\(z\) elimination is a classical AK(3) self-loop.

**Architecture:** Quotient by the passive source. The \(D\)-source quotient
is an HNN extension and gives a complete tail family by Britton--Collins
conjugacy. The \(B\)-source quotient eliminates \(z\) outright and makes
the surviving relator a conjugate or inverse of the braid endpoint.

**Tech Stack:** HNN normal forms, Britton's lemma, Collins conjugacy,
normal closures, evaluation, Markdown proof, dependency-free Python
replay.

## Constraints

- Work only in the isolated `codex/proofs` worktree.
- Do not use a pairwise three-axis argument.
- Do not use a bounded conjugator census as completeness evidence.
- Require per-event membership in the passive source normal closure.
- Require a surviving source shadow to be restored up to conjugation and
  inversion.
- Require an eliminated passive source to preserve its baseline quotient
  normal closure.
- Separate stable deletion from the classical endpoint theorem.
- State that AK(3) remains open.
- Commit and push `codex/proofs` after verification.

---

### Task 1: \(D\to B\) HNN classification

**Files:**

- Create:
  `literature/proofs/AK3_ONE_WAY_CROSS_TRAFFIC_SELF_LOOP.md`

- [x] Identify the quotient as
  \(\langle G,z\mid zxz^{-1}=t\rangle\).
- [x] Prove \(G\) embeds and classify every length-one conjugate of \(B\).
- [x] Derive \(e_n=t^{-n}(xt)x^n\).
- [x] Prove \(D(e_n)=t^{-n}D(xt)t^n\).
- [x] Derive the signed two-event table by weight.

### Task 2: \(B\to D\) quotient and replay

**Files:**

- Create:
  `tests/stable_ac/test_one_way_cross_traffic.py`

- [x] Identify \(H/\langle\!\langle B\rangle\!\rangle\cong G\).
- [x] Derive the evaluated survivor formula.
- [x] Pin the exact \(e_n\) seam recurrences.
- [x] Pin all four signed two-\(D\) histories and endpoint conjugacies.
- [x] Pin the two-\(B\)-factor exponent obstruction.

### Task 3: Ledger, audit, checkpoint

**Files:**

- Modify: `results/stable_ac/theory/AK3_DIRECT_STABLE_THEORY.md`
- Modify: `AGENTS.md`

- [x] Add the one-way theorem and narrow the live frontier to feedback.
- [x] Record the quotient-by-passive-source method in `AGENTS.md`, then
  read it back.
- [x] Run all related replays and diff checks.
- [x] Obtain two hostile reviews of the actual theorem and replay.
- [ ] Commit and push the verified checkpoint.
