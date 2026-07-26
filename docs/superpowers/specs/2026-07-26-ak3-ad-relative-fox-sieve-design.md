# AK(3) A--D relative-product Fox sieve design

Date: 2026-07-26

## Objective

For an arbitrary relative conjugator \(c\in F(x,t,z,q)\), obstruct
primitivity of

\[
P_{\sigma}(c)=A\,cD^\sigma c^{-1},
\qquad \sigma=\pm1,
\]

without bounding the length or alphabet of \(c\).

## Structural reduction

At a torus character with \(x=t=1\), both \(A\) and \(D\) evaluate to
one. The conjugator-derivative term in the abelianized Fox row therefore
vanishes. With \(q=4z/3\), all four derivatives of \(P_\sigma(c)\)
vanish exactly when

\[
c(1,1,z,4z/3)=-4\sigma.
\]

If \(e_q,e_z\) are the exponent sums of \(q,z\) in \(c\), this becomes

\[
(4/3)^{e_q}z^{e_q+e_z}=-4\sigma.
\]

It has a solution over an algebraically closed characteristic-zero
field whenever \(e_q+e_z\ne0\). On the hyperplane
\(e_q+e_z=0\), reduction modulo a prime other than \(2,3\) supplies a
solution except for

\[
(\sigma,e_q)=(+1,1),\quad(-1,0),\quad(-1,1).
\]

Since a primitive word has a unimodular abelianized Fox row, a common
torus zero proves nonprimitivity.

## Replay

The dependency-free verifier will:

- evaluate Fox derivatives directly from words;
- verify the exact A, D, and relative-product slice formulas on
  cancellation-heavy conjugators;
- construct the elementary finite-characteristic witnesses on the
  zero-total-exponent hyperplane;
- confirm that the only failures of this particular character slice
  are the three displayed exponent classes.

## Boundary

This is a necessary-condition sieve, not a classification of the three
residual exponent classes. It does not handle arbitrary A--W or W--D
products, prove stable AC, or prove AC.
