# AK(3) passive-source elimination design

Date: 2026-07-25

## Objective

Close the remaining exactly-one-\(B/D\)-cross role from the quotient
one-\(D\) theorem: preserve the cross target, eliminate the restored source,
and determine the resulting rank-two endpoint.

The intended result is stronger. If the eventual generator isolator remains
a passive source, every finite number of uses of its source slot against the
other relator should vanish after substitution.

## General quotient mechanism

Let

\[
G=F(X)/\langle\!\langle R\rangle\!\rangle,
\qquad
H=G*\langle z\rangle,
\]

and let \(I_0=z^{-1}e_0\) be a baseline isolator. Suppose a final isolator
\(I=z^{-1}e\) has the same normal closure as \(I_0\) in \(H\).

Evaluation at \(z=e\) kills \(I\), hence its entire normal closure. It
therefore kills \(I_0\) as well, which forces \(e=e_0\) in \(G\).

Let \(J_0\) be the baseline survivor. If the final survivor \(J\), after
projection to \(H\), differs from \(J_0\) only by:

- multiplication by elements in the normal closure of \(I\);
- conjugation; and
- inversion,

then evaluation at \(z=e\) makes \(J\) conjugate, up to inversion, to
\(J_0[z\mapsto e_0]\) in \(G\). The fixed-relator normal-closure lemma and
AC1/AC3 give classical AC equivalence of the two rank-two endpoints.

This statement includes arbitrary source conjugators, arbitrary finite
products of source factors, and fixed-\(R\) gauges. It does not require a
bounded enumeration.

## AK(3) application

Use

\[
R=x^3t^{-4},\qquad
B=z^{-1}xt,\qquad
D=t^{-1}zxz^{-1}.
\]

If the \(B\)-slot is the passive source and final isolator, then
\(e_0=xt\). Any number of multiplications of the \(D\)-slot by conjugates
of \(B\)-source spellings disappears after evaluation. The baseline
survivor becomes

\[
D[z\mapsto xt]
=t^{-1}(xt)x(xt)^{-1},
\]

which is a conjugate of the AK(3) braid relator.

If the \(D\)-slot is the restored source, the proposed one-\(z\)
elimination is impossible. The \(z\)-exponent of \(D\) is zero, and
fixed-\(R\) gauges, conjugation, and inversion preserve zero. A one-\(z\)
isolator has \(z\)-exponent \(\pm1\).

## Verification

The replay should pin:

- a final \(B\)-type linear isolator changed by a nontrivial \(R\)-gauge;
- several left and right target multiplications by conjugates of distinct
  \(B\)-source spellings;
- conjugators containing \(z^{\pm1}\);
- fixed-\(R\) gauges on the survivor;
- equality of the evaluated survivor with the baseline endpoint in the
  quotient by \(R\); and
- the \(z\)-exponent obstruction for the opposite target role.

The replay illustrates the identities. Completeness comes from the
normal-closure/evaluation theorem.

## Scope

The theorem covers arbitrarily many cross events provided the eventual
isolator slot is used only as a source and its quotient normal closure is
preserved. It does not cover:

- a cross event targeting the eventual isolator slot;
- failure to preserve that slot's quotient normal closure;
- a changed retained relator;
- a multi-\(z\) primitive eliminator;
- another stabilization; or
- dual-source primitive-pair compression.

AK(3) remains open.
