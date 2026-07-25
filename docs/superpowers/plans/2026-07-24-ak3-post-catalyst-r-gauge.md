# AK(3) post-catalyst \(R\)-gauge closure implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` (recommended) or
> `superpowers:executing-plans` to implement this plan task-by-task. Steps
> use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove that arbitrary fixed-\(R\) gauge moves after one classified
\(B_U/D\) catalyst cannot change the post-elimination classical AC class.

**Architecture:** Prove a general quotient-shadow/evaluation lemma in
\((F(x,t)/\langle\!\langle R\rangle\!\rangle)*\langle z\rangle\), apply the
fixed-relator normal-closure lemma after evaluation, and specialize it to
both one-\(D\) target roles.

**Tech Stack:** Free products, quotient evaluation, Markdown proof, exact
amalgam normal form, dependency-free Python replay.

## Global Constraints

- Work only in the isolated `codex/proofs` worktree.
- Do not modify solver code.
- Do not use a bounded computation as completeness evidence.
- Invoke substitution-and-removal only with the trivial-group hypothesis.
- State that AK(3) remains open.
- Commit and push `codex/proofs` after verification.

---

### Task 1: Quotient-shadow theorem

**Files:**

- Create: `literature/proofs/AK3_POST_CATALYST_R_GAUGE_SELF_LOOP.md`

- [x] Define \(G\), \(G*\langle z\rangle\), and evaluation at \(z=e\).
- [x] Prove quotient-equal isolators give the same evaluation map.
- [x] Prove quotient-equal survivors evaluate equally modulo \(R\).
- [x] Apply the fixed-relator normal-closure lemma.
- [x] Separate classical endpoint equivalence from stable deletion.

### Task 2: AK(3) corollary and replay

**Files:**

- Create: `tests/stable_ac/test_post_catalyst_r_gauge_self_loop.py`

- [x] Apply the lemma to both catalyst target roles and both signs.
- [x] State the exact \(D\)-then-\(R\) collected-order consequence.
- [x] Replay isolator and survivor gauge factors for cancellation-heavy
  recoveries.
- [x] Verify every replay endpoint modulo \(R\) with exact amalgam normal
  form.

### Task 3: Ledger, audit, and checkpoint

**Files:**

- Modify: `results/stable_ac/theory/AK3_DIRECT_STABLE_THEORY.md`
- Modify: `AGENTS.md`

- [x] Add the theorem to the theory ledger without overstating interleaving
  scope.
- [x] Record the quotient-evaluation method and its exact scope trap.
- [x] Read back the `AGENTS.md` change.
- [x] Run all related dependency-free replays and diff checks.
- [x] Obtain hostile review of the actual theorem and replay.
- [x] Inspect and prepare the verified checkpoint for commit and push.
