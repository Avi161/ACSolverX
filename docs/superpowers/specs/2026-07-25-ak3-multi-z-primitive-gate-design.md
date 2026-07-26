# AK(3) multi-\(z\) primitive-gate design

Date: 2026-07-25

## Objective

Replace the vague “multi-\(z\) primitive eliminator” escape route by a
rigorous first gate:

1. prove that no primitive word can hide entirely in the literal
   \(z\)-kernel unless it is conjugate to \(z^{\pm1}\);
2. identify and certify the smallest parity-relevant family whose
   specialization uses the retained AK(3) relator;
3. distinguish coherent ambient-automorphism use, which is an exact
   self-loop, from asymmetric use, which remains a genuine open route.

The retained relator is

\[
R=x^3t^{-4}.
\]

The new stabilizer is denoted \(q\) in this note to avoid confusing it
with earlier one-\(z\) corridor variables.

## Literal-kernel gate

Let

\[
\rho:F(X)*\langle q\rangle\longrightarrow F(X)
\]

kill \(q\). If a primitive word \(W\) satisfies \(\rho(W)=1\) literally,
then \(W\) is conjugate to \(q^{\pm1}\).

The proof compares the two rank-\(|X|\) free quotients

\[
F/\langle\!\langle W\rangle\!\rangle
\longrightarrow
F/\langle\!\langle q\rangle\!\rangle,
\]

uses Hopficity to show that the normal closures coincide, and then applies
the Magnus normal-closure theorem.

Consequently, a nontrivial multi-\(q\) primitive candidate specializing
to \(1\) in \(G=\langle x,t\mid R\rangle\) must specialize in
\(F(x,t)\) to a nontrivial element of
\(\langle\!\langle R\rangle\!\rangle\).

## Smallest three-\(q\) family

Write the reduced word \(R=xxxTTTT\) as \(A_kB_k\), where \(A_k\) is
the length-\(k\) prefix, \(1\leq k\leq6\). Define

\[
V_k=qA_kq^{-1}B_kq.
\]

Each \(V_k\) is cyclically reduced, contains three occurrences of
\(q^{\pm1}\), has \(q\)-exponent \(1\), and specializes literally to
\(R\).

The expected exact classification is:

\[
V_k\text{ primitive}\quad\Longleftrightarrow\quad k=3.
\]

For \(k\ne3\), a connected Whitehead graph with no cut vertex proves
non-primitivity. For \(k=3\), the automorphisms

\[
\alpha(q)=Rq,\qquad
\beta(x)=qxq^{-1}
\]

with all other basis generators fixed satisfy

\[
(\beta\alpha)(q)=V_3.
\]

## Fox certificate

For every \(k\), after \(q\mapsto1\),

\[
\left(
\frac{\partial V_k}{\partial x},
\frac{\partial V_k}{\partial t},
\frac{\partial V_k}{\partial q}
\right)
=
\left(
\frac{\partial R}{\partial x},
\frac{\partial R}{\partial t},
1-A_k+R
\right).
\]

In \(\mathbb Z[G]\), the last entry is \(2-A_k\). The replay will compute
these identities directly in the integral free-group ring rather than
assuming quotient simplification.

## Coherent versus asymmetric use

Let \(\phi=\beta\alpha\) and

\[
p=\rho\phi^{-1}.
\]

Then \(p(\phi(U))=U\) for every \(q\)-free word \(U\). Thus applying
\(\phi\) coherently to an entire tuple and then eliminating \(\phi(q)\)
is exactly a self-loop.

For the primitive candidate \(V_3\), however,

\[
p(x)=RxR^{-1},\qquad p(t)=t,\qquad p(q)=R^{-1}.
\]

The induced endomorphism

\[
\psi_R:x\mapsto RxR^{-1},\quad t\mapsto t
\]

is not an automorphism of \(F(x,t)\). Therefore an asymmetric AC history
that creates \(V_3\) without transporting every survivor coherently is
not dismissed by the self-loop calculation.

## Result boundary

This checkpoint does not construct such an asymmetric AC history and
does not prove stable AC triviality of AK(3). It turns the multi-\(z\)
escape route into one explicit production problem.

