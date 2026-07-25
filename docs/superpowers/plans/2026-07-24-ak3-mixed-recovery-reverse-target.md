# AK(3) mixed-recovery reverse-target self-loop plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` (recommended) or
> `superpowers:executing-plans` to implement this plan task-by-task. Steps
> use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Decide the exact endpoint obtained when one arbitrary-conjugator
\(B_U^{\pm1}\)-multiplication targets \(D\), the modified \(D\)-slot is used
as a one-\(z\) isolator, and the surviving \(B_U\)-slot is retained.

**Architecture:** Reuse the already proved Cayley-tree bridge and forced-seam
classification, which concerns cyclic product classes and is symmetric in
the two factors. Treat the survivor separately because target/source order
is not symmetric after elimination. Pin the two survivor identities by an
independent dependency-free replay.

**Tech Stack:** Free-group word identities, Markdown proof, dependency-free
Python replay through the existing word library.

## Global Constraints

- Work only in the isolated `codex/proofs` worktree.
- Create new proof and replay files; modify only the theory ledger and the
  project `AGENTS.md` lesson section.
- Do not run an AC graph search above 1000 nodes.
- Distinguish substitution-and-removal from bare AC5.
- Do not claim that the result trivializes AK(3); it closes one mechanism.
- Commit and push `codex/proofs` after verification.

---

### Task 1: Independent reverse-survivor replay

**Files:**

- Create:
  `tests/stable_ac/test_mixed_recovery_reverse_target_self_loop.py`

**Interfaces:**

- Consumes: `free_reduce`, `inv`, `cyc_reduce`, and
  `recoveries_up_to(9)`.
- Produces: replay of the complete signed cyclic residue for selected
  cancellation-heavy recoveries and exact survivor identities for all 61
  recoveries through length 9.

- [ ] Write the replay before the theorem.
- [ ] Check that the signed rotation products yield only
  \(\operatorname{cyc}(Zt^{-1}wx)\) and
  \(\operatorname{cyc}(Ztwx^{-1})\).
- [ ] Check
  \(C_+=w^{-1}S_0^{-1}w\) and
  \(C_-=(Tw)^{-1}S_0(Tw)\) by literal free reduction.
- [ ] Run every `test_*` function under system Python using `runpy.run_path`.

### Task 2: Reverse-target theorem

**Files:**

- Create:
  `literature/proofs/AK3_MIXED_RECOVERY_REVERSE_TARGET_SELF_LOOP.md`

**Interfaces:**

- Consumes:
  `AK3_MIXED_RECOVERY_ONE_D_SELF_LOOP.md` and
  `AK3_ARBITRARY_RECOVERY_SELF_LOOP.md`.
- Produces: an unbounded theorem for one multiplication targeting \(D\),
  followed by removing that modified \(D\)-slot.

- [ ] State the arbitrary recovery and arbitrary relative-conjugator
  hypotheses.
- [ ] Explain why cyclic product classification transfers when factor order
  is reversed.
- [ ] Require restoration of the temporarily conjugated or inverted source
  \(B_U\).
- [ ] Display both exact conjugacy identities for the surviving relator.
- [ ] Invoke substitution-and-removal with its trivial-group hypothesis.
- [ ] State the exact scope exclusions.

### Task 3: Ledger, lesson, and verification

**Files:**

- Modify: `results/stable_ac/theory/AK3_DIRECT_STABLE_THEORY.md`
- Modify: `AGENTS.md`

**Interfaces:**

- Produces: Proven result 14 and an updated live lead that preserves other
  interleavings and multi-factor mechanisms as open.

- [ ] Add Proven result 14 without making an Aut-floor claim.
- [ ] Remove only the now-closed reverse-target role from the live lead.
- [ ] Record the conjugacy identities and the remaining order-scope trap in
  `AGENTS.md`, then read the changed section back.
- [ ] Run both mixed-recovery replays and `git diff --check`.
- [ ] Obtain hostile proof review of the actual theorem file.
- [ ] Inspect the final diff, commit, and push `codex/proofs`.

