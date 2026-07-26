# AK(3) Multi-Source Primitive-Loop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps
> use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove the multi-source relation-split self-loop and certify the
first \(B\)-coupled AK(3) primitive word with \(U=RB\).

**Architecture:** Generalize the fixed-relator lemma to a retained
subtuple, then give a literal four-relator AK(3) certificate.

**Tech Stack:** Markdown proof and dependency-free exact word replay.

## Global constraints

- Theory before implementation.
- No AC graph search.
- Require a balanced trivial-group presentation for stable ambient
  straightening.
- Do not claim closure when a source used in \(U\) is deleted or its
  normal closure is not retained.
- AK(3) remains open.

---

### Task 1: Prove the multi-source theorem

**Files:**
- Create:
  `literature/proofs/AK3_MULTISOURCE_PRIMITIVE_SELF_LOOP.md`

- [x] Prove the multi-source normal-closure replacement lemma.
- [x] Prove classical manufacture of \(W=\beta(U)q\).
- [x] Compute the primitive quotient.
- [x] Return every survivor modulo the retained source subtuple.

### Task 2: Certify the \(U=RB\) AK(3) branch

**Files:**
- Create: `tests/stable_ac/test_multisource_primitive_loop.py`
- Modify:
  `literature/proofs/AK3_MULTISOURCE_PRIMITIVE_SELF_LOOP.md`

- [x] Replace \(R,B\) by \(\beta(R),\beta(B)\) with exact
  \(q\)-factorizations.
- [x] Build the five-\(q\) primitive word exactly.
- [x] Replay the automorphism inverse and quotient endpoint.
- [x] Return \(D'\) by four retained-source conjugates.

### Task 3: Verify, review, and checkpoint

**Files:**
- Modify: `results/stable_ac/theory/AK3_DIRECT_STABLE_THEORY.md`
- Modify: `AGENTS.md`

- [x] State Result 34 and narrow the live lead.
- [x] Run focused tests, syntax, claim, placeholder, and diff audits.
- [x] Complete an independent hostile review.
- [ ] Commit and push the verified checkpoint.
