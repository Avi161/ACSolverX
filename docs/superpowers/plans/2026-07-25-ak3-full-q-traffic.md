# AK(3) Full Q-Traffic Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps
> use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove all target traffic from the restored literal q-source is
a stable self-loop, and prove the four first literal-z targets
nonprimitive.

**Architecture:** Delete q before the changed target, then delete the
primitive recovery word \(U\). Separately replay strict Whitehead
automorphisms and spanning-cycle certificates for the four literal-z
targets.

**Tech Stack:** Markdown proof and dependency-free exact word replay.

## Global constraints

- Theory before implementation.
- No AC graph search.
- Require the final q-source relator to be literal and distinct.
- Require the final target multiplier to lie in the full normal closure
  of q.
- Check all four sign pairs.
- Use nonprimitivity language only for the exact displayed targets.
- Do not infer an obstruction to later traffic.
- AK(3) remains open.

---

### Task 1: Prove the full q-traffic self-loop

**Files:**
- Create:
  `literature/proofs/AK3_FULL_Q_TRAFFIC_SELF_LOOP.md`

- [x] Delete the restored literal q-slot before the changed target.
- [x] Prove q-killing sends every \(Wv\) to \(U\).
- [x] Delete primitive \(U\) and compute the rank-two endpoint.
- [x] Return the endpoint by two retained-\(R\) factors.

### Task 2: Prove the four-target obstruction

**Files:**
- Modify:
  `literature/proofs/AK3_FULL_Q_TRAFFIC_SELF_LOOP.md`

- [x] Replay the first Whitehead automorphism on all four targets.
- [x] Replay the second reduction for the positive-z conjugator pair.
- [x] Exhibit both common spanning cycles.
- [x] Apply the cut-vertex lemma with exact scope.

### Task 3: Build the independent replay

**Files:**
- Create: `tests/stable_ac/test_full_q_traffic_self_loop.py`
- Modify:
  `literature/proofs/AK3_FULL_Q_TRAFFIC_SELF_LOOP.md`

- [x] Test full q-normal-closure multipliers containing z.
- [x] Replay q-first and U-second deletion.
- [x] Verify both automorphisms and inverses.
- [x] Verify all word images and strict length drops.
- [x] Verify both exact Whitehead edge sets.
- [x] Verify connectedness and absence of cut vertices.

### Task 4: Verify, review, and checkpoint

**Files:**
- Modify: `results/stable_ac/theory/AK3_DIRECT_STABLE_THEORY.md`
- Modify: `AGENTS.md` only if the work reveals a reusable lesson.

- [x] State Result 41 and narrow the live lead.
- [x] Run focused tests, syntax, claim, placeholder, and diff audits.
- [x] Complete an independent hostile review.
- [x] Commit and push the verified checkpoint.
