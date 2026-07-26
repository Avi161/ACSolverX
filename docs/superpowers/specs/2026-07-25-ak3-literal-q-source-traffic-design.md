# AK(3) literal-q source traffic design

Date: 2026-07-25

## Objective

Decide the first q-dependent AC1 moves into the source-slot primitive:

\[
W\longmapsto Wq^{\pm1}.
\]

These moves lie outside the q-free retained-traffic theorem.

## General mechanism

Let \(F_0=F(X)\), let \(U\in F_0\) be primitive, and extend \(U\) to a
basis \((U,c_2,\ldots,c_n)\) of \(F_0\). Let

\[
\phi\in\operatorname{Aut}(F_0*\langle q\rangle),
\qquad
W=\phi(q),
\qquad
\phi^{-1}(q)=U^{-1}q.
\]

For the positive source orientation, define

\[
\delta_+(q)=qU^{-1}q,\qquad
\delta_+(U)=q,\qquad
\delta_+(c_i)=c_i.
\]

Its inverse is

\[
\delta_+^{-1}(q)=U,\qquad
\delta_+^{-1}(U)=Uq^{-1}U.
\]

Then

\[
Wq=\phi(qU^{-1}q)=(\phi\delta_+)(q).
\]

For the negative source orientation, let \(\delta_-\) swap \(q\) and
\(U\) and fix the complementary basis. Then

\[
Wq^{-1}=\phi(U)=(\phi\delta_-)(q).
\]

Thus both targets are primitive.

After straightening and deleting the new primitive, the surviving
literal \(q\)-relator becomes \(U^{-1}\) in the positive branch and
\(U\) in the negative branch. If

\[
\lambda:F_0*\langle q\rangle
\longrightarrow
F_0/\langle\!\langle U\rangle\!\rangle
\]

kills \(q\), then

\[
\lambda\delta_\pm^{-1}=\lambda.
\]

Every other new survivor therefore equals its old primitive-deletion
image modulo the surviving \(U^{\pm1}\)-source. The normal-closure
replacement lemma returns the old endpoint.

## AK(3) specialization

Take

\[
R=x^3t^{-4},\qquad
B=z^{-1}xt,\qquad
U=RB.
\]

The word \(U\) is primitive because it contains \(z^{-1}\) exactly once.
At the source-slot checkpoint

\[
(\beta(R),W,D,q),
\]

both \(Wq\) and \(Wq^{-1}\) are therefore primitive self-loops.

For the positive branch, the exact new quotient has

\[
q\mapsto U^{-1},\qquad
x\mapsto UxU^{-1},\qquad
z\mapsto zh,
\qquad
h=R^{-1}U^{-1}R.
\]

The changed \(D\)-survivor differs from the old one by two conjugates of
\(h^{\pm1}\), hence by two conjugates of the surviving \(U^{-1}\)-source.

## Boundary

This closes only multiplication by the surviving literal
\(q^{\pm1}\)-relator. It does not classify multiplication by a
nontrivial conjugate \(c q^{\pm1}c^{-1}\), by a changed q-source, or by
several interleaved q-dependent sources.
