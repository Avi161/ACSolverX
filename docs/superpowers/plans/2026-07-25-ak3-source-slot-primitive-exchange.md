# AK(3) Source-Slot Primitive-Exchange Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps
> use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove that targeting and deleting a quotient-equal source slot
with \(W=\beta(U)q\) is still a stable self-loop.

**Architecture:** Track the surviving \(q\)-relator through
\(\phi^{-1}\), prove that it recovers the deleted source, then reuse the
multi-source endpoint return.

**Tech Stack:** Markdown proof and dependency-free exact word replay.

## Global constraints

- Theory before implementation.
- No AC graph search.
- Keep the quotient-equality hypothesis
  \(R_k^{-1}U\in L_0\) explicit.
- Do not broaden to source replacements that change joint normal
  closure.
- AK(3) remains open.

---

### Task 1: Prove the source-slot theorem

**Files:**
- Create:
  `literature/proofs/AK3_SOURCE_SLOT_PRIMITIVE_EXCHANGE_SELF_LOOP.md`

- [x] Manufacture \(W\) in the \(R_k\)-slot.
- [x] Track the surviving \(q\)-relator to \(U^{-1}\).
- [x] Recover \(R_k\) modulo the other retained sources.
- [x] Restore every remaining survivor modulo the full source tuple.

### Task 2: Certify the AK(3) \(B\)-target branch

**Files:**
- Create: `tests/stable_ac/test_source_slot_primitive_exchange.py`
- Modify:
  `literature/proofs/AK3_SOURCE_SLOT_PRIMITIVE_EXCHANGE_SELF_LOOP.md`

- [x] Replay the exact \(\beta(B)\to W\) target moves.
- [x] Replay \(\phi^{-1}\) and the endpoint \((R,D',U^{-1})\).
- [x] Verify \(U^{-1}R=B^{-1}\).
- [x] Verify the four-source-factor return of \(D'\).

### Task 3: Verify, review, and checkpoint

**Files:**
- Modify: `results/stable_ac/theory/AK3_DIRECT_STABLE_THEORY.md`
- Modify: `AGENTS.md`

- [x] State Result 35 and narrow the live lead.
- [x] Run focused tests, syntax, claim, placeholder, and diff audits.
- [x] Complete an independent hostile review.
- [ ] Commit and push the verified checkpoint.
