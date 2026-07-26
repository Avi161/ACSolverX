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

- [ ] Delete the restored literal q-slot before the changed target.
- [ ] Prove q-killing sends every \(Wv\) to \(U\).
- [ ] Delete primitive \(U\) and compute the rank-two endpoint.
- [ ] Return the endpoint by two retained-\(R\) factors.

### Task 2: Prove the four-target obstruction

**Files:**
- Modify:
  `literature/proofs/AK3_FULL_Q_TRAFFIC_SELF_LOOP.md`

- [ ] Replay the first Whitehead automorphism on all four targets.
- [ ] Replay the second reduction for the positive-z conjugator pair.
- [ ] Exhibit both common spanning cycles.
- [ ] Apply the cut-vertex lemma with exact scope.

### Task 3: Build the independent replay

**Files:**
- Create: `tests/stable_ac/test_full_q_traffic_self_loop.py`
- Modify:
  `literature/proofs/AK3_FULL_Q_TRAFFIC_SELF_LOOP.md`

- [ ] Test full q-normal-closure multipliers containing z.
- [ ] Replay q-first and U-second deletion.
- [ ] Verify both automorphisms and inverses.
- [ ] Verify all word images and strict length drops.
- [ ] Verify both exact Whitehead edge sets.
- [ ] Verify connectedness and absence of cut vertices.

### Task 4: Verify, review, and checkpoint

**Files:**
- Modify: `results/stable_ac/theory/AK3_DIRECT_STABLE_THEORY.md`
- Modify: `AGENTS.md` only if the work reveals a reusable lesson.

- [ ] State Result 41 and narrow the live lead.
- [ ] Run focused tests, syntax, claim, placeholder, and diff audits.
- [ ] Complete an independent hostile review.
- [ ] Commit and push the verified checkpoint.
