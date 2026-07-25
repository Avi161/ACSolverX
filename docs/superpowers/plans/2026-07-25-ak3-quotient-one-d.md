# AK(3) quotient one-\(D\) catalyst implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` (recommended) or
> `superpowers:executing-plans` to implement this plan task-by-task. Steps
> use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove that every fixed-\(R\), exactly-one-\(B/D\)-cross-event
route ending by eliminating the cross target as a generator isolator
returns classically to AK(3).

**Architecture:** Project to
\(G*\langle z\rangle\), use the Bass--Serre axis trichotomy, retain the
mandatory vertex-stabilizer twist, and exhaust its finite forcing tables.
Then combine exact quotient-shadow normalization with evaluation and the
fixed-relator normal-closure lemma.

**Tech Stack:** Bass--Serre theory, free-product normal forms, exact amalgam
normal form for \(\langle x,t\mid x^3=t^4\rangle\), Markdown proof,
dependency-free Python replay.

## Global Constraints

- Work only in the isolated `codex/proofs` worktree.
- Do not modify solver code.
- Do not claim pure rotations exhaust intersecting quotient axes.
- Do not use bounded conjugator enumeration as completeness evidence.
- Distinguish stable deletion from classical endpoint equivalence.
- State that AK(3) remains open.
- Commit and push `codex/proofs` after verification.

---

### Task 1: Exact quotient replay

**Files:**

- Create:
  `tests/stable_ac/test_quotient_one_d_catalyst_barrier.py`

- [x] Implement exact normal form in
  \(\langle x,t\mid x^3=t^4\rangle*\langle z\rangle\).
- [x] Pin the two literal signed-rotation classes.
- [x] Pin the sixteen unique \(G\)-vertex twist witnesses.
- [x] Pin the four \(z^k\)-vertex solutions for each sign.
- [x] Verify fixed-\(R\) pre-gauges leave both slot shadows unchanged.
- [x] Run every `test_*` function with dependency-free `runpy`.

### Task 2: Unbounded quotient theorem

**Files:**

- Create:
  `literature/proofs/AK3_QUOTIENT_ONE_D_CATALYST_SELF_LOOP.md`

- [x] Prove the Bass--Serre disjoint/shared-edge/shared-vertex trichotomy.
- [x] Exclude disjoint axes by weight and Bass--Serre translation length.
- [x] Display both \(G\)-vertex forcing tables and prove uniqueness cell by
  cell through normal-form equations.
- [x] Display both \(z^k\)-vertex solution tables and prove no other integer
  exponent works.
- [x] Normalize the final exact quotient shadow using free-product
  conjugacy and the nonzero weights of \(e_\pm\).
- [x] Apply quotient evaluation and the fixed-relator lemma to both target
  roles.
- [x] State exact scope exclusions.

### Task 3: Ledger, lessons, audit, checkpoint

**Files:**

- Modify: `results/stable_ac/theory/AK3_DIRECT_STABLE_THEORY.md`
- Modify: `AGENTS.md`

- [x] Add the quotient theorem to the theory ledger.
- [x] Record the vertex-stabilizer trap and the corrected twist-table
  method in `AGENTS.md`, then read it back.
- [x] Run all related proof replays and `git diff --check`.
- [x] Obtain two hostile reviews of the actual theorem and replay.
- [x] Inspect and prepare the verified checkpoint for commit and push.
