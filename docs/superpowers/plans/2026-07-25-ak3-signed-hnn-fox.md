# AK(3) Signed-HNN Fox Master-Lemma Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps
> use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove one coefficient factorization and one exact HNN
incidence theorem covering all eight signed three-cross histories.

**Architecture:** Derive the recurrence in the abelianized semidirect
product, isolate the sign product \(m=\eta\theta\), quotient the two
augmentation-ideal coefficients, and identify the remaining operator
with signed incidence on an HNN forest.

**Tech Stack:** Markdown proof, pure Python replay, group rings,
semidirect products, HNN extensions, Bass--Serre trees.

## Global Constraints

- Every sign and multiplication side must be explicit.
- Group-ring coefficients act on the left and generate right ideals as
  variables range over the regular module.
- Incidence arguments apply only to finite-support chains.
- The theorem is conditional on the evaluated bridge equations and on
  \(J=\langle K,L\rangle\) being free.
- No AC graph search.

---

### Task 1: Derive the eight-row factorization

- [x] Derive signed powers and conjugation in
  \(N_{\mathrm{ab}}\rtimes G\).
- [x] Obtain the general \((X,Y,\Xi)\) recurrence.
- [x] Define \(M_\theta,N_\eta\) and prove
  \(M_\theta N_\eta=\eta\theta L\).
- [x] Prove the displayed \(A_0,A_U,A_V,A_W\) formulas.
- [x] Replay all eight formal sign rows.

### Task 2: Identify the bridge ideal

- [x] Rewrite \(L(K-1)\) through \(LKL^{-1}-1\).
- [x] Prove
  \(A_VR+A_WR=I_{\langle K,LKL^{-1}\rangle}\).

### Task 3: Prove the signed-HNN theorem

- [x] Realize \(J\) as the HNN extension of
  \(P=\langle K,LKL^{-1}\rangle\).
- [x] Identify \(1+L\) with unsigned incidence.
- [x] Identify \(1-L\) with oriented incidence.
- [x] Prove both exact image criteria and finite-support injectivity.
- [x] Deduce
  \(\ker\mathcal B_\pm=(K-1)R\).

### Task 4: Verify and checkpoint

- [x] Add independent finite-group and tree-incidence replays.
- [x] Run the focused verification and inspect the diff.
- [x] Obtain hostile review.
- [ ] Commit and push the verified branch checkpoint.
