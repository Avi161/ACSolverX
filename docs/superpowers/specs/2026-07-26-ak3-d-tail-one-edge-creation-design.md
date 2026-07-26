# AK(3) D-tail one-edge primitive creation design

Date: 2026-07-26

## Objective

At each of the six nonprimitive first D-tail checkpoints

\[
(A,W,D,Q_{\eta,\epsilon,\delta}),
\]

classify every one-edge AC2 interaction between Q and one carrier
\(A,W,D\), in both target directions. Decide whether the changed row
is primitive, whether any displayed pair is primitive, and where every
positive deletion endpoint lands.

## Exhaustive edge model

For ordered target T and source S:

- cyclically rotate T;
- choose \(S\) or \(S^{-1}\);
- cyclically rotate that source orientation;
- replace T by the freely/cyclically reduced product;
- restore S and canonicalize the changed conjugacy class.

Target inversion need not be separate: the inverse of
\(T^{-1}S^\sigma\) is cyclically conjugate to
\(TS^{-\sigma}\). Thus target rotations, both source signs, and final
relator inversion cover every AC1/AC2/AC3 realization of one source
multiplication.

Run this model for Q-target/source-A, Q-target/source-W,
Q-target/source-D and the three reversed target directions.

## Method

- Deduplicate literal products by cyclic conjugation and inversion but
  retain one exact move witness per child.
- Use complete rank-four Whitehead descent for individual children and
  for every relevant two-relator tuple.
- For each positive child or pair, transport the full four-relator
  tuple through the stored automorphism and delete the primitive
  coordinate(s).
- Classify the resulting rank-two/rank-three endpoint symbolically or
  by a complete Whitehead certificate.
- Separate literal tail-cancellation backtracks from genuine
  row-changing children.

## Proven result

The complete signed-cyclic census and hostile audit find six primitive
changed-word classes. There are 30 direct primitive-pair incidences and
32 changed-row-first sequential primitive-single continuations. Every
such endpoint is either the known floor-23 compression orbit or the
known floor-27 qW backtrack orbit; none reaches a new rank-two orbit or
floor at most 12.

The literal count is recorded in both conventions: 12,992
representatives after quotienting the redundant target inversion, or
25,984 when that target orientation is separately indexed.

## Boundary

This theorem covers the signed cyclic-representative image of one AC2
edge involving Q. It does not classify an arbitrary relative
conjugator \(TuSu^{-1}\), an alternate first-deletion order, an edge
solely among A, W, and D, two consecutive row-changing edges, or
histories that first alter the checkpoint.
