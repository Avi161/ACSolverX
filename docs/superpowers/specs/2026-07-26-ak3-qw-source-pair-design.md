# AK(3) qW changed-source pair design

Date: 2026-07-26

## Objective

Decide all four incoherent changed sources

\[
Q_{\eta,\epsilon}=q^\eta W^\epsilon,
\qquad
\eta,\epsilon\in\{+1,-1\},
\]

at the fixed AK source-slot checkpoint, including arbitrary later
traffic from \(Q_{\eta,\epsilon}\).

## Structure

Write

\[
A=\beta(R),
\qquad
C=\beta(xt)q,
\qquad
W=Az^{-1}C.
\]

Every \(Q_{\eta,\epsilon}\) contains z exactly once, so it is primitive.
For \(\epsilon=+1\), it has form

\[
(q^\eta A)z^{-1}C;
\]

for \(\epsilon=-1\), it has form

\[
(q^\eta C^{-1})zA^{-1}.
\]

Explicit orientation-reversing or orientation-preserving z-coordinate
automorphisms straighten these words.

## Expected deletion chain

After deleting the z-coordinate, the surviving W-slot becomes literal:

\[
W\longmapsto q^{-\eta\epsilon}.
\]

Delete that q-slot next. In every sign branch,

\[
\beta(R)\longmapsto R,
\qquad
D\longmapsto
E_R=t^{-1}(xtR)x(xtR)^{-1}.
\]

The usual two retained-R factors return \(E_R\) to the standard
rank-two AK endpoint.

## Boundary

The theorem requires the fixed factorization \(W=Az^{-1}C\), a changed
source exactly \(q^\eta W^\epsilon\), that source kept unchanged and
deleted first, and later traffic only from its normal closure. It does
not cover a longer mixed source word, a second source change, deletion
of W before the changed source, or primitive-pair compression.
