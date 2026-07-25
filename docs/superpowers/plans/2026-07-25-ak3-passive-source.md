# AK(3) passive-source elimination implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` (recommended) or
> `superpowers:executing-plans` to implement this plan task-by-task. Steps
> use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove that eliminating an eventual passive source annihilates
every use of that source against the survivor, and apply this to close the
remaining one-cross AK(3) role.

**Architecture:** State the mechanism in the quotient
\(G*\langle z\rangle\), factor evaluation through the quotient by the
isolator's normal closure, and use the fixed-\(R\) lemma to lift quotient
equality to classical AC equivalence.

**Tech Stack:** Free-product quotients, normal closures, evaluation
homomorphisms, Markdown proof, dependency-free Python replay.

## Constraints

- Work only in the isolated `codex/proofs` worktree.
- Prefer the unbounded normal-closure theorem to a conjugator census.
- Distinguish stable substitution-and-removal from classical endpoint
  equivalence.
- Do not claim the theorem covers feedback into the eventual source slot.
- State that AK(3) remains open.
- Commit and push `codex/proofs` after verification.

---

### Task 1: General passive-source theorem

**Files:**

- Create:
  `literature/proofs/AK3_PASSIVE_SOURCE_ELIMINATION_SELF_LOOP.md`

- [x] State the quotient-normal-closure hypotheses.
- [x] Prove evaluation kills all passive-source factors.
- [x] Prove the final tail is conjugate or inverse to the baseline tail
  modulo \(R\).
- [x] Lift this equality to a classical AC equivalence.
- [x] Separate the stable deletion from the rank-two conclusion.

### Task 2: AK(3) application and replay

**Files:**

- Create:
  `tests/stable_ac/test_passive_source_elimination.py`

- [x] Apply the theorem with \(I_0=B\) and \(J_0=D\).
- [x] Show the baseline endpoint is the AK(3) braid relator up to
  conjugacy.
- [x] Exclude a \(D\)-type one-\(z\) source by \(z\)-exponent.
- [x] Replay representative multiple source factors and fixed-\(R\)
  gauges.

### Task 3: Audit and checkpoint

**Files:**

- Modify: `results/stable_ac/theory/AK3_DIRECT_STABLE_THEORY.md`
- Modify: `AGENTS.md`

- [x] Add the theorem and narrowed live frontier to the theory ledger.
- [x] Record the passive-source normal-closure principle in `AGENTS.md`,
  then read it back.
- [x] Run all related dependency-free proof tests and diff checks.
- [x] Obtain two hostile reviews of the actual theorem and replay.
- [x] Commit and push the verified checkpoint to `codex/proofs`.
