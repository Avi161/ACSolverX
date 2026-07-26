# AK(3) Complement-Conjugator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps
> use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove that conjugating the surviving q-source by any coherent
complement word still gives a primitive stable self-loop.

**Architecture:** Treat primitive \(U\) as a basis letter. Each target
pullback contains \(U^{\pm1}\) once, so straighten it by a one-letter
automorphism, delete \(U\), delete the resulting conjugate of \(q\), and
compare the double quotient literally.

**Tech Stack:** Markdown proof and dependency-free exact word replay.

## Global constraints

- Theory before implementation.
- No AC graph search.
- Require the conjugator pullback to lie in a stated free-factor
  complement to \(U\).
- Carry the balanced-trivial/reachable checkpoint hypothesis explicitly.
- Do not broaden to pullbacks involving \(U\).
- AK(3) remains open.

---

### Task 1: Prove the abstract complement theorem

**Files:**
- Create:
  `literature/proofs/AK3_COMPLEMENT_CONJUGATED_Q_TRAFFIC_SELF_LOOP.md`

- [x] Construct and invert both one-\(U\) automorphisms.
- [x] Compute the surviving conjugate of \(q^{\mp1}\).
- [x] Prove the double-quotient identity.
- [x] State the exact complement boundary.

### Task 2: Certify the AK(3) \(a=t\) branch

**Files:**
- Create: `tests/stable_ac/test_complement_conjugated_q_traffic.py`
- Modify:
  `literature/proofs/AK3_COMPLEMENT_CONJUGATED_Q_TRAFFIC_SELF_LOOP.md`

- [x] Replay both target identities and inverse automorphisms.
- [x] Replay both first deletion quotients.
- [x] Verify equality of the two double quotients.
- [x] Return the rank-two endpoint with two \(R\)-factors.

### Task 3: Verify, review, and checkpoint

**Files:**
- Modify: `results/stable_ac/theory/AK3_DIRECT_STABLE_THEORY.md`
- Modify: `AGENTS.md` only if the work reveals a reusable lesson.

- [x] State Result 39 and narrow the live lead.
- [x] Run focused tests, syntax, claim, placeholder, and diff audits.
- [x] Complete an independent hostile review.
- [ ] Commit and push the verified checkpoint.
