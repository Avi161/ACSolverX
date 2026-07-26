# AK(3) z-free q-normal-closure traffic design

Date: 2026-07-25

## Objective

Close every finite primitive-slot multiplication by z-free consequences
of the surviving q-source.

## Unique-z mechanism

At the source-slot checkpoint, write

\[
W=\beta(R)z^{-1}\beta(p)q,
\qquad
p=xt.
\]

For arbitrary

\[
v\in
\ker\bigl(F(x,t,q)\longrightarrow F(x,t)\bigr)
=
\langle\!\langle q\rangle\!\rangle_{F(x,t,q)},
\]

put

\[
T_v
=
Wv
=
A z^{-1}C_v,
\]

where

\[
A=\beta(R),
\qquad
C_v=\beta(p)qv.
\]

Both \(A\) and \(C_v\) avoid \(z\), so \(T_v\)
has exactly one \(z^{-1}\). The automorphism

\[
\gamma_v(z)=Az^{-1}C_v
\]

fixing \(x,t,q\) proves it primitive. Its inverse is

\[
\gamma_v^{-1}(z)
=
C_vz^{-1}A.
\]

After straightening and deleting \(z\), the surviving q-relator remains
literal \(q\), so it also deletes. Projecting \(q,z\mapsto1\) gives

\[
\gamma_v^{-1}(z)\longmapsto pR
\]

because \(v\) dies when \(q\) is killed. The double quotient is
independent of the length and normal-closure factorization of \(v\).

## Endpoint

Every such z-free q-consequence gives

\[
(R,E_R),
\qquad
E_R=t^{-1}(xtR)x(xtR)^{-1}.
\]

The standard AK endpoint replaces \(xtR\) by \(xt\), and their
difference is two conjugates of \(R^{\pm1}\).

## Boundary

This is arbitrary finite target traffic from the unchanged literal
q-source at the fixed checkpoint. It does not cover a final multiplier
containing \(z\), a z-free multiplier with nontrivial image after
\(q\mapsto1\), or a changed q-source. A q-source conjugated by literal
\(z\) is the first basis case outside the theorem.
