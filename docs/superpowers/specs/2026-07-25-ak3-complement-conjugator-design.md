# AK(3) complement-conjugator q-traffic design

Date: 2026-07-25

## Objective

Extend the literal-q closure theorem to genuinely nontrivial conjugates
of the surviving q-source.

## General mechanism

Use a free-product basis

\[
F=F(K)*\langle U\rangle*\langle q\rangle
\]

with \(U\) primitive, and suppose

\[
W=\phi(q),
\qquad
\phi^{-1}(q)=U^{-1}q.
\]

For \(a\in F(K)\), put \(c=\phi(a)\). The pullbacks of the two target
moves are

\[
\begin{aligned}
\phi^{-1}(Wcqc^{-1})
&=qaU^{-1}qa^{-1},\\
\phi^{-1}(Wcq^{-1}c^{-1})
&=qaq^{-1}Ua^{-1}.
\end{aligned}
\]

Each word contains the basis letter \(U^{\pm1}\) exactly once. Define an
automorphism \(\delta_{a,\epsilon}\) by sending \(U\) to the appropriate
word and fixing \(F(K)\) and \(q\). The new target is
\((\phi\delta_{a,\epsilon})(U)\).

After straightening and deleting \(U\), the surviving q-relator is

\[
a^{-1}q^{-\epsilon}a.
\]

Conjugate, invert when necessary, and delete it. If \(\lambda\) kills
both \(U\) and \(q\), then

\[
\lambda\delta_{a,\epsilon}^{-1}=\lambda.
\]

The final quotient is therefore literally the old quotient obtained by
deleting \(W\) and then the surviving primitive \(U^{-1}\).

## AK(3) specialization

For

\[
U=RB=x^3t^{-4}z^{-1}xt,
\]

take the complementary factor \(K=F(x,t)\). Since \(\phi(t)=t\), the
choice \(a=t\) gives the first nontrivial literal conjugator:

\[
Wtq^{\pm1}t^{-1}.
\]

Both targets are primitive. Both two-stage deletions give

\[
(R,E_R),
\qquad
E_R=t^{-1}(xtR)x(xtR)^{-1}.
\]

This differs from the standard rank-two AK endpoint

\[
E_0=t^{-1}(xt)x(xt)^{-1}
\]

by two conjugates of \(R^{\pm1}\).

## Boundary

The theorem covers exactly conjugators \(c\) with
\(\phi^{-1}(c)\in F(K)\). It does not cover pullbacks involving \(U\),
including the literal AK conjugators \(x\) and \(z\), nor changed
q-sources, arbitrary iteration, or interleaved q-dependent source
products.
