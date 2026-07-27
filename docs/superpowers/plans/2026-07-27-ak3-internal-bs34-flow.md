# AK(3) internal \(BS(3,4)\) flow-module implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development to implement this plan
> task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Decide the internal \(BS(3,4)\) right-ideal obstruction by
turning its first two relations into an exact Bass--Serre flow module.

**Architecture:** Identify the universal cyclic module with directed
edge chains modulo conservation at every Bass--Serre vertex.  Translate
the arbitrary internal element \(b\) into a double-coset edge
constraint, close the two canonical local double cosets, then attack
all noncanonical double cosets by Britton geodesics and boundary
currents.

**Tech Stack:** Markdown proof, Bass--Serre tree normal forms,
dependency-free Python, exact rational linear algebra, pytest.

## Global constraints

- Theory before implementation; no AC graph search.
- Do not replace arbitrary \(b\) by \(1\) or \(y\).
- A finite tree ball is a replay, not a universal proof.
- A whole group-ring ideal means only that this obstruction fails.
- Keep AK(3), AC, and stable AC open.

---

### Task 1: Prove the universal flow model

**Files:**
- Create: `literature/proofs/AK3_AD_INTERNAL_BS34_FLOW_MODULE.md`

- [ ] Define the right-coset edge and vertex sets with consistent
  handedness.
- [ ] Prove the two half-star sums are representative-independent.
- [ ] Identify \(x^4-1\) with edge stabilization.
- [ ] Identify every right translate of \(yR_3-R_4\) with conservation
  at one vertex.
- [ ] Prove the resulting quotient is exactly the universal cyclic
  module, not merely one representation of it.

---

### Task 2: Close the canonical double cosets

**Files:**
- Modify: `literature/proofs/AK3_AD_INTERNAL_BS34_FLOW_MODULE.md`
- Create: `experiments/stable_ac/verify_internal_bs34_flow.py`
- Create: `tests/stable_ac/test_internal_bs34_flow.py`

- [ ] Write failing incidence and local-collapse tests.
- [ ] Implement the exact \(4\)-incoming/\(3\)-outgoing replay.
- [ ] Prove zero quotient for \(b\in H\), both signs.
- [ ] Prove zero quotient for \(b\in yH\), both signs.
- [ ] State that these are module failures, not primitive certificates.

---

### Task 3: Decide the noncanonical double cosets

**Files:**
- Modify: `literature/proofs/AK3_AD_INTERNAL_BS34_FLOW_MODULE.md`
- Modify: `results/stable_ac/theory/AK3_DIRECT_STABLE_THEORY.md`

- [ ] Parameterize \(CbH\) by Britton-reduced normal form without a
  syllable bound.
- [ ] Dualize the quotient to conserved scalar edge assignments.
- [ ] Prove that an acyclic recurrence admits a nonzero boundary
  current.
- [ ] Classify any cyclic recurrences by exact double-coset geometry.
- [ ] Conclude propriety uniformly on (7), or state the exact
  unresolved double-coset residue.

---

### Task 4: Verify, review, and checkpoint

- [ ] Run focused flow tests and all Result 55--59 regressions.
- [ ] Run syntax compilation and both whitespace checks.
- [ ] Obtain independent handedness, tree-geometry, and scope reviews.
- [ ] Resolve every Critical or Important finding.
- [ ] Force-add the proof, inspect staged scope, commit, and push
  `codex/proofs`.
- [ ] Continue the proof loop from the exact residual condition.
