# AK(3) Literal-q Source-Traffic Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps
> use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove that both literal surviving-q source orientations
\(W\mapsto Wq^{\pm1}\) are primitive stable self-loops.

**Architecture:** Use \(U\) as a basis element, construct two explicit
basis automorphisms taking \(q\) to the two pullback targets, and compare
the new deletion maps with the old one modulo the surviving
\(U^{\pm1}\)-relator.

**Tech Stack:** Markdown proof and dependency-free exact word replay.

## Global constraints

- Theory before implementation.
- No AC graph search.
- Require \(U\) to be primitive in the unstabilized free group.
- Carry the balanced-trivial/reachable checkpoint hypothesis explicitly.
- Do not broaden literal \(q^{\pm1}\) to arbitrary conjugates.
- AK(3) remains open.

---

### Task 1: Prove the abstract two-sign theorem

**Files:**
- Create:
  `literature/proofs/AK3_LITERAL_Q_SOURCE_TRAFFIC_SELF_LOOP.md`

- [x] Prove both basis maps \(\delta_\pm\) are automorphisms.
- [x] Identify \(Wq^{\pm1}\) as their transported basis images.
- [x] Compute the surviving q-relator in both deletion quotients.
- [x] Compare every survivor modulo \(\langle\!\langle U\rangle\!\rangle\).

### Task 2: Certify the AK(3) specialization

**Files:**
- Create: `tests/stable_ac/test_literal_q_source_traffic.py`
- Modify:
  `literature/proofs/AK3_LITERAL_Q_SOURCE_TRAFFIC_SELF_LOOP.md`

- [x] Prove \(U=RB\) primitive from its unique \(z^{-1}\)-occurrence.
- [x] Replay the positive and negative straightening automorphisms.
- [x] Verify the positive quotient and its two-factor \(D\)-return.
- [x] Check the negative endpoint agrees with the abstract quotient.

### Task 3: Verify, review, and checkpoint

**Files:**
- Modify: `results/stable_ac/theory/AK3_DIRECT_STABLE_THEORY.md`
- Modify: `AGENTS.md` only if the work reveals a reusable lesson.

- [x] State Result 38 and narrow the live lead.
- [x] Run focused tests, syntax, claim, placeholder, and diff audits.
- [x] Complete an independent hostile review.
- [ ] Commit and push the verified checkpoint.
