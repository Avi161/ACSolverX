# AK(3) source-slot primitive-exchange design

Date: 2026-07-25

## Objective

Decide whether the multi-source primitive word can escape the previous
self-loop by replacing and deleting one of the source relator slots
instead of the stabilizing \(q\)-slot.

## General setup

Let

\[
\mathcal P
=
\langle X\mid R_1,\ldots,R_k,S_1,\ldots,S_m\rangle
\]

be balanced and trivial, and let

\[
L_0=\langle\!\langle R_1,\ldots,R_{k-1}\rangle\!\rangle.
\]

Choose \(U\in F(X)\) satisfying

\[
R_k^{-1}U\in L_0.
\]

Thus \(U\) and \(R_k\) are equal modulo the other retained sources.
For a relative-kernel automorphism \(\beta\), define

\[
\alpha_U(q)=Uq,\qquad
\phi=\beta\alpha_U,\qquad
W=\beta(U)q.
\]

## Proposed source-slot theorem

After replacing every \(R_i\) by \(\beta(R_i)\), the relation

\[
\beta(R_k)^{-1}\beta(U)
\in
\langle\!\langle
\beta(R_1),\ldots,\beta(R_{k-1})
\rangle\!\rangle
\]

allows the \(R_k\)-slot to be changed to \(\beta(U)\), then to
\(W=\beta(U)q\), while the stabilizing \(q\)-slot survives.

Straightening \(W\) and deleting its generator-relator pair sends that
surviving \(q\)-relator to \(U^{-1}\). Modulo \(L_0\),
\(U^{-1}=R_k^{-1}\), so the other retained sources recover the lost
\(R_k\)-slot. Once the full source normal closure is restored, all
remaining quotient distortions are absorbed as before.

## AK(3) certificate

Take

\[
R=x^3t^{-4},\qquad
B=z^{-1}xt,\qquad
D=t^{-1}zxz^{-1},\qquad
U=RB.
\]

Target the \(\beta(B)\)-slot:

\[
\beta(B)
\longmapsto
\beta(R)\beta(B)
\longmapsto
\beta(R)\beta(B)q=W.
\]

After primitive deletion the endpoint is

\[
(R,D',U^{-1}).
\]

The exact identity

\[
U^{-1}R=B^{-1}
\]

recovers \(B\) by one AC1 move and inversion. The four-factor retained
\((R,B)\)-certificate then returns \(D'\) to \(D\).

## Boundary

This closes source-slot deletion when \(U\) is quotient-equal to that
source modulo the other retained sources. It does not close a target
whose replacement \(U\) changes the joint source normal closure, a
surviving stabilizer that has already been modified, or a primitive word
outside the relative-transvection family.

