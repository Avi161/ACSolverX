# AK(3) Multi-\(z\) Primitive-Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps
> use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove the literal-kernel obstruction, certify the smallest
three-\(q\) relation-dependent primitive candidate, and isolate coherent
self-loop use from the remaining asymmetric production problem.

**Architecture:** Keep the theorem group-theoretic. Use a dependency-free
exact replay for free reduction, Whitehead graphs, the explicit
automorphism, and Fox derivatives.

**Tech Stack:** Markdown proofs, pure Python finite-word algebra, `runpy`
replay.

## Global constraints

- Theory before implementation.
- CPU only; no AC graph search.
- Do not classify words outside the stated six-member family.
- Do not infer stable AC triviality from primitivity alone.
- State asymmetric production as open.
- AK(3) remains open.

---

### Task 1: Prove the literal-kernel and Fox gates

**Files:**
- Create: `literature/proofs/AK3_MULTI_Z_PRIMITIVE_GATE.md`

- [x] Prove the normal-closure theorem using equal-rank Hopficity and
  Magnus's theorem.
- [x] Derive the retained-relator corollary.
- [x] State the evaluated Fox-row certificate for arbitrary primitive
  eliminators.

### Task 2: Certify the six-word family

**Files:**
- Create: `tests/stable_ac/test_multi_z_primitive_gate.py`
- Modify: `literature/proofs/AK3_MULTI_Z_PRIMITIVE_GATE.md`

- [x] Replay every specialization \(V_k(q=1)=R\).
- [x] Prove \(V_k\) nonprimitive for \(k\ne3\) by exact Whitehead graphs.
- [x] Verify an explicit automorphism taking \(q\) to \(V_3\).
- [x] Replay the three Fox derivatives for every \(k\).

### Task 3: Separate coherent and asymmetric use

**Files:**
- Modify: `tests/stable_ac/test_multi_z_primitive_gate.py`
- Modify: `literature/proofs/AK3_MULTI_Z_PRIMITIVE_GATE.md`
- Modify: `results/stable_ac/theory/AK3_DIRECT_STABLE_THEORY.md`
- Modify: `AGENTS.md`

- [x] Verify \(\phi^{-1}\), the quotient map \(p=\rho\phi^{-1}\), and
  coherent cancellation on sample free words.
- [x] Prove the asymmetric survivor endomorphism is not in
  \(\operatorname{Aut}(F_2)\).
- [x] Update the theory ledger and lessons.
- [x] Run focused replay, syntax, placeholder, claim, and diff audits.
- [x] Complete an independent hostile review.
- [x] Commit and push the verified checkpoint.
