# AK(3) Quotient-B Length-Gap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps
> use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove a quotient cyclic-length gap for every feasible
prefix-\(DB\) three-cross row.

**Architecture:** Quotient by the original \(B\), reduce the third target
to \(AhA^{\eta\theta}h^{-1}\), and classify its Bass--Serre axis geometry
by a finite intersecting-axis census plus an unbounded disjoint-axis
formula.

**Tech Stack:** Markdown proof, pure Python, amalgam normal form, `runpy`.

## Global Constraints

- The theorem gives necessary liftability conditions, not an AC
  obstruction.
- Length-zero closes only the four \(\eta\theta=-1\) rows.
- The positive-length spectra remain open.
- No AC graph search.
- AK(3) remains open.

---

### Task 1: Replay both length spectra

**Files:**
- Modify: `tests/stable_ac/test_prefix_db_evaluated_countermodel.py`

- [x] Replay the \(m=-1\) distribution.
- [x] Replay the \(m=+1\) distribution.
- [x] Pin the complete six-row sign/weight/orientation table.
- [x] Pin the two minimum same-orientation classes.
- [x] Replay their non-braid last-two-equation solutions.
- [x] Replay through repository-root `runpy`.

### Task 2: State and apply the length-gap theorem

**Files:**
- Create: `literature/proofs/AK3_QUOTIENT_B_LENGTH_GAP.md`
- Modify: `results/stable_ac/theory/AK3_DIRECT_STABLE_THEORY.md`
- Modify: `AGENTS.md`

- [x] Derive the quotient-\(B\) product equation.
- [x] Prove the disjoint-axis formula.
- [x] Prove the intersecting-axis spectra.
- [x] Classify the minimum same-orientation classes and exact tail lifts.
- [x] Prove length zero is a classical self-loop.
- [x] State the positive-length frontier without overclaim.
- [x] Run related replays, diff checks, and two hostile reviews.
- [x] Commit and push the verified checkpoint.
