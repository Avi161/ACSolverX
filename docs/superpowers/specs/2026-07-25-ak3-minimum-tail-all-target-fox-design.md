# AK(3) minimum-tail all-target Fox design

Date: 2026-07-25

## Objective

Decide the exact Fox coset equation for every target \(g\in G\) in the
repositioned row-\((+,-,-)\) minimum-tail candidate.

## HNN path classification

Write

\[
\mathcal B(z)=\pi_P((1+L)z),
\qquad
q=c^{-1}L,
\qquad
J=\langle K,L\rangle.
\]

After quotienting the domain by \((K-1)R\), \(\mathcal B\) is unsigned
edge incidence on the HNN Bass--Serre forest. Therefore

\[
\mathcal B(z)=-[Pg]-[Pq]
\]

is solvable precisely when the two vertices are in the same component
and have opposite bipartite colors. Every solvable right-hand side has
a unique alternating odd-path preimage modulo \((K-1)R\).

## Support separation

Every edge in the component of \(Pq\) has a representative in
\(Jc^{-1}\). Hence the unique path chain \(z_g\) satisfies

\[
\operatorname{supp}(z_gc)\subset J.
\]

The residual Fox equation is

\[
\pi_Q(z_g)=\pi_Q(F_0),
\qquad
Q=\langle d,K\rangle.
\]

After right multiplication by \(c\),

\[
\pi_Q(F_0)c=[Qt^3]-[Qc]-[Qxt].
\]

It is enough to prove that \(Qc\notin QJ\) and that \(Qc\) is distinct
from the other two displayed cosets.

## Exact double-coset certificate

Compute the based folded fiber product of the projected \(Q\)- and
\(J\)-cores. Its core has rank two and free basis

\[
\bar Q\cap\bar J=\langle\bar K,\bar h\rangle.
\]

The unique lifts of both basis elements through \(Q\) and through \(J\)
agree in the central extension. Therefore the central lift-defect
homomorphism on the intersection is zero. This rules out
\(c\in QJ\), hence \(Qc\notin QJ\).

## Scope

- Exact obstruction for every target \(g\in G\) in this Fox equation.
- No bounded word search and no AC graph search.
- This closes the repositioned minimum-tail candidate, not the full
  stable Andrews--Curtis move space.
- The Andrews--Curtis conjecture and the remaining stable mechanisms
  stay open.
