# AK(3) Post-Primitive Traffic Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps
> use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove that arbitrary AC1--AC3 traffic away from a fixed
primitive slot commutes with straightening and deletion.

**Architecture:** Prove move-by-move functoriality under the quotient
homomorphism, then replay one mixed AK(3) history independently.

**Tech Stack:** Markdown proof and dependency-free exact word replay.

## Global constraints

- Theory before implementation.
- No AC graph search.
- Never allow an AC1 multiplication to target the primitive slot in the
  theorem; AC2 and AC3 on that slot are allowed.
- Treat use of the primitive slot as a source as a quotient no-op.
- AK(3) remains open.

---

### Task 1: Prove quotient functoriality

**Files:**
- Create:
  `literature/proofs/AK3_POST_PRIMITIVE_TRAFFIC_SELF_LOOP.md`

- [x] Prove naturality for AC1, AC2, and AC3.
- [x] Prove histories compose and deletion commutes.
- [x] Combine with the source-slot theorem.

### Task 2: Replay a mixed AK(3) history

**Files:**
- Create: `tests/stable_ac/test_post_primitive_traffic.py`
- Modify:
  `literature/proofs/AK3_POST_PRIMITIVE_TRAFFIC_SELF_LOOP.md`

- [x] Build the exact source-slot checkpoint.
- [x] Apply seven mixed post-manufacture moves.
- [x] Map the final tuple through \(\theta\).
- [x] Independently replay the descended quotient history.

### Task 3: Verify, review, and checkpoint

**Files:**
- Modify: `results/stable_ac/theory/AK3_DIRECT_STABLE_THEORY.md`
- Modify: `AGENTS.md`

- [x] State Result 36 and narrow the live lead.
- [x] Run focused tests, syntax, claim, placeholder, and diff audits.
- [x] Complete an independent hostile review.
- [x] Commit and push the verified checkpoint.
