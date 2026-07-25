# AK(3) Prefix-DB Evaluated Countermodel Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps
> use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove that the evaluated prefix-\(DB\) equations have a
weight-one killer solution outside the braid conjugacy class, and prove
that the explicit solution fails the literal one-\(z\) liftability test.

**Architecture:** Derive the evaluated three-cross system abstractly,
give one exact central-power lift of a \(C_3*C_4\) solution, and use the
original-\(B\) quotient plus Bass--Serre cyclic length to exclude its
realization in \(G*\langle z\rangle\).

**Tech Stack:** Markdown proof, pure Python, repository amalgam normal
form, `runpy`.

## Global Constraints

- This is not a realized stable-AC move sequence.
- Failure of braid conjugacy is not AC inequivalence.
- The explicit countermodel is nonliftable; other literal one-\(z\)
  solutions remain unresolved.
- No AC graph search.
- AK(3) remains open.

---

### Task 1: Replay the exact countermodel

**Files:**
- Create: `tests/stable_ac/test_prefix_db_evaluated_countermodel.py`

- [x] Encode the explicit central-power lifts.
- [x] Check the tail, first-cross, second-cross, and final equations.
- [x] Check the feasible weight row.
- [x] Check projected cyclic-length nonconjugacy.
- [x] Check the \(216\)-case quotient-\(B\) commutator sieve.
- [x] Replay through repository-root `runpy`.

### Task 2: State the theorem and its exact limitation

**Files:**
- Create: `literature/proofs/AK3_PREFIX_DB_EVALUATED_COUNTERMODEL.md`
- Modify: `results/stable_ac/theory/AK3_DIRECT_STABLE_THEORY.md`
- Modify: `AGENTS.md`

- [x] Derive the general evaluated prefix-\(DB\) equation.
- [x] Prove the explicit \(G\) solution and killer property.
- [x] Prove nonconjugacy to \(D_p^{\pm1}\).
- [x] Isolate literal one-\(z\) liftability as the missing hypothesis.
- [x] Prove the explicit countermodel is not liftable.
- [x] Correct two older literal-equality endpoint statements.
- [x] Run related replays, diff checks, and two hostile reviews.
- [x] Commit and push the verified checkpoint.
