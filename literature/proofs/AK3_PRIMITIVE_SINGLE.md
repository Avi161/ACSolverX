# Primitive-single-relator removal in rank-three AK(3) corridors

Date: 2026-07-24

Status: the removal and quotient-independence theorems are **PROVEN**. The
bounded floor-12 candidate is **UNVERIFIED** until its certificate is built
and replayed.

## 1. Primitive relator theorem

### Theorem 1.1 — PROVEN

Let

\[
 P=\langle a,b,c\mid A,B,C\rangle
\]

be a balanced presentation of the trivial group. If one relator conjugacy
class, say \([A]\), is primitive in \(F(a,b,c)\), then \(P\) is stably
AC-equivalent to a balanced rank-two presentation.

### Proof

Choose \(\phi\in\operatorname{Aut}(F(a,b,c))\) carrying \(A\) to a conjugate
of \(a^{\pm1}\). Realize \(\phi\) by the stable ambient automorphism theorem.
Conjugate and invert the first relator so it is exactly \(a\). Use it to
delete every \(a^{\pm1}\) occurrence from the other two relators, then remove
the generator-relator pair \((a,a)\) by inverse stabilization.

The two surviving relators over \(b,c\) give a balanced rank-two presentation,
and every step is stable AC. \(\square\)

## 2. Independence of the straightening

### Theorem 2.1 — PROVEN

The Aut(\(F_2\))-orbit of the rank-two quotient in Theorem 1.1 is independent
of the chosen automorphism straightening \([A]\).

### Proof

Normalize two choices \(\phi,\psi\) by inner automorphisms and inversion so
that both send \(A\) exactly to \(a\). Then

\[
 \theta=\psi\phi^{-1}
\]

fixes \(a\), hence preserves its normal closure. It descends to an
automorphism

\[
 \bar\theta\in
 \operatorname{Aut}(F(a,b,c)/\langle\!\langle a\rangle\!\rangle)
 \cong\operatorname{Aut}(F(b,c)).
\]

The two quotient relator pairs are related by \(\bar\theta\), together with
relator order, conjugation, and inversion. Therefore they have the same
complete rank-two Aut-orbit and the same Whitehead floor. \(\square\)

One certified straightening witness per primitive relator conjugacy class is
therefore complete for the floor decision.

## 3. Whitehead criterion

A nontrivial cyclic word is primitive exactly when its complete
Aut(\(F_3\))-minimum cyclic length is one. Whitehead's theorem makes strict
second-kind descent complete. The certificate carries the composed
automorphism and checks all 90 nonidentity rank-three Whitehead maps at the
endpoint.

## 4. Stable floor-12 implication

### Corollary 4.1 — PROVEN

If any primitive-single quotient has complete rank-two Aut-floor at most 12,
then AK(3) is stably AC-trivial.

### Proof

Compose the certified AK(3)-to-rank-three corridor, Theorem 1.1, the complete
rank-two ambient automorphism, and MM03 Theorem 1.1 as scoped in
`MU_CRITERION.md`. \(\square\)

## 5. Finite candidate

Use all 3,016 cyclic rank-three states in the certified two-stabilization
bounds. Reduce every distinct relator individually. For every primitive
occurrence:

1. apply its stored automorphism to all three relators;
2. cyclically normalize the primitive relator to one basis letter;
3. remove that generator and relator;
4. relabel the two surviving basis letters;
5. compute and certify the complete rank-two Aut-floor.

### Primitive-single floor-12 lemma — UNVERIFIED

At least one induced rank-two quotient has Aut-floor at most 12.

A positive proves stable AC-triviality. A negative refutes only this bounded
corridor lemma; it is not an obstruction for all stable representatives.
