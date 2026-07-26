# AK(3) Relation-Split Primitive-Loop Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps
> use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove that the direct asymmetric construction of
\(qx^3q^{-1}t^{-4}q\) is a stable self-loop, and generalize the argument
to every relative-kernel automorphism \(\beta\) and every
\(U\in\langle\!\langle R\rangle\!\rangle\).

**Architecture:** Prove the universal quotient identity first. Pin the
AK(3) construction with literal products of conjugates, then replay all
free-word identities independently.

**Tech Stack:** Markdown proof and dependency-free Python word algebra.

## Global constraints

- Theory before implementation.
- No AC graph search.
- Separate stable primitive removal from the classical endpoint return.
- Do not claim closure of arbitrary productions of the same primitive
  word.
- AK(3) remains open.

---

### Task 1: Prove the universal loop theorem

**Files:**
- Create:
  `literature/proofs/AK3_RELATION_SPLIT_PRIMITIVE_SELF_LOOP.md`

- [x] Prove the fixed-\(q\) creation step.
- [x] Compute the primitive straightening quotient.
- [x] Prove survivor equality modulo the retained \(R\).
- [x] Apply the fixed-\(R\) lemma one survivor at a time.

### Task 2: Give the exact AK(3) certificate

**Files:**
- Create: `tests/stable_ac/test_relation_split_primitive_loop.py`
- Modify:
  `literature/proofs/AK3_RELATION_SPLIT_PRIMITIVE_SELF_LOOP.md`

- [x] Factor \(R^{-1}\beta(R)\) into two conjugates of \(q^{\pm1}\).
- [x] Produce \(V\) by one multiplication and one conjugation.
- [x] Replay \(\phi,\phi^{-1}\) and the quotient endpoint.
- [x] Factor \(B^{-1}B'\) and \(D^{-1}D'\) into two conjugates of
  \(R^{\pm1}\) each.

### Task 3: Verify, review, and checkpoint

**Files:**
- Modify: `results/stable_ac/theory/AK3_DIRECT_STABLE_THEORY.md`
- Modify: `AGENTS.md`

- [x] State Result 33 and the narrower live lead.
- [x] Run focused tests, syntax, placeholder, claim, and diff audits.
- [x] Complete an independent hostile review.
- [ ] Commit and push the verified checkpoint.
