# AK(3) Final-Target Switch Duality Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove that switching the target of the final cross event preserves
the classical endpoint class after one-\(z\) elimination.

**Architecture:** Use a cyclic factor rotation before deletion and the
evaluated target equation after deletion. Keep the proof abstract, then
apply it to the four pairs of length-three target words.

**Tech Stack:** Markdown proof, pure Python free-word replay, `runpy`.

## Global Constraints

- No AC graph search.
- Do not claim the remaining killer corridor closes.
- Preserve the fixed-\(R\) restoration hypotheses.
- AK(3) remains open.

---

### Task 1: Replay the factor-switch identity

**Files:**
- Create: `tests/stable_ac/test_final_target_switch_duality.py`

- [x] Pin both multiplication sides, both signs, and several nontrivial
  conjugators.
- [x] Assert the two target spellings are cyclic conjugates.
- [x] Choose one-\(z\) examples and assert the two evaluated survivors are
  signed conjugates.
- [x] Replay through repository-root `runpy`.

### Task 2: State and apply the abstract theorem

**Files:**
- Create: `literature/proofs/AK3_FINAL_TARGET_SWITCH_DUALITY.md`
- Modify: `results/stable_ac/theory/AK3_DIRECT_STABLE_THEORY.md`
- Modify: `AGENTS.md`

- [x] Prove the cyclic target reinterpretation.
- [x] Prove evaluated survivor equivalence through the fixed-\(R\) lemma.
- [x] Pair all eight three-cross target words by their final letter.
- [x] Reduce `DBB` and `DBD` to one open prefix-`DB` killer mechanism.
- [x] Run related replays, diff checks, and two hostile reviews.
- [ ] Commit and push the verified checkpoint.
