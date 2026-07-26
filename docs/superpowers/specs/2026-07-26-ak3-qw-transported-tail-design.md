# AK(3) qW transported-tail design

Date: 2026-07-26

## Objective

Decide the longer changed-source family

\[
Q_{\eta,\epsilon,V}
=
q^\eta W^\epsilon\beta(V),
\qquad
V\in\langle\!\langle R\rangle\!\rangle_{F(x,t)},
\]

for all source signs.

## First deletion: tail transfer

Write \(A=\beta(R)\), \(C=\beta(xt)q\), and \(W=Az^{-1}C\).
Every \(Q_{\eta,\epsilon,V}\) contains z exactly once and is primitive.
Its z-coordinate deletion transfers the coherent tail into the surviving
W-slot:

\[
W\longmapsto
\bigl(\beta(V)q^\eta\bigr)^{-\epsilon}.
\]

Arbitrary later traffic from \(Q_{\eta,\epsilon,V}\) vanishes in this
deletion.

## Second deletion: left transported source

The word

\[
P_{\eta,V}=\beta(V)q^\eta
\]

is primitive via \(\theta=\beta\ell_{V,\eta}\), where

\[
\ell_{V,\eta}(q)=Vq^\eta.
\]

Deleting the surviving \(P_{\eta,V}^{-\epsilon}\)-slot sends the
remaining tuple to

\[
\left(
R,\;
t^{-1}K_{\eta,V}xK_{\eta,V}^{-1}
\right).
\]

Here

\[
K_{\eta,V}=xtV^{-\eta}RV^\eta.
\]

The word \(V^{-\eta}RV^\eta\) is one conjugate of R, so exactly two
retained-R source factors return this endpoint to the standard
rank-two AK endpoint.

## Exact V=R specialization

For \(V=R\), both eta orientations give

\[
K_{\eta,R}=xtR.
\]

Thus both land at the same \(E_R\) endpoint already seen in Results
40--41, and the same two retained-R factors return it.

## Boundary

The theorem requires a coherent right tail \(\beta(V)\) with
\(V\in\langle\!\langle R\rangle\!\rangle\), the unique-z changed source
kept unchanged and deleted first, and the transferred W-slot kept for
the second deletion. It does not cover a z-dependent tail, an
incoherent q-dependent tail, a second source change, or primitive-pair
compression.
