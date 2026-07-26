# AK(3) Z-Free Q-Traffic Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps
> use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove that arbitrary finite z-free traffic from the unchanged
q-source produces a primitive stable self-loop.

**Architecture:** Write the full multiplier as an arbitrary z-free
element of the normal closure of q, factor the target around its unique
\(z^{-1}\), delete z and the unchanged q-relator, and calculate the
multiplier-independent double quotient.

**Tech Stack:** Markdown proof and dependency-free exact word replay.

## Global constraints

- Theory before implementation.
- No AC graph search.
- Require \(v\in\langle\!\langle q\rangle\!\rangle_{F(x,t,q)}\).
- Keep the fixed balanced-trivial source-slot checkpoint explicit.
- Do not broaden to z-containing multipliers or changed q-sources.
- AK(3) remains open.

---

### Task 1: Prove the unique-z theorem

**Files:**
- Create:
  `literature/proofs/AK3_Z_FREE_Q_TRAFFIC_SELF_LOOP.md`

- [x] Factor every target \(Wv\) as \(Az^{-1}C_v\).
- [x] Construct and invert the unique-z automorphism.
- [x] Delete z and the unchanged q-relator.
- [x] Prove the double quotient is independent of \(v\).

### Task 2: Build the exact replay

**Files:**
- Create: `tests/stable_ac/test_z_free_q_traffic.py`
- Modify:
  `literature/proofs/AK3_Z_FREE_Q_TRAFFIC_SELF_LOOP.md`

- [x] Replay both automorphism compositions.
- [x] Test finite products of both source orientations.
- [x] Include the literal \(c=x\) branch.
- [x] Verify the endpoint and two-\(R\)-factor return.

### Task 3: Verify, review, and checkpoint

**Files:**
- Modify: `results/stable_ac/theory/AK3_DIRECT_STABLE_THEORY.md`
- Modify: `AGENTS.md` only if the work reveals a reusable lesson.

- [x] State Result 40 and narrow the live lead.
- [x] Run focused tests, syntax, claim, placeholder, and diff audits.
- [x] Complete an independent hostile review.
- [ ] Commit and push the verified checkpoint.
