# AK(3) all-integer D-tail primitivity design

Date: 2026-07-26

## Objective

Classify, for every integer k, primitivity of

\[
Q_{\eta,\epsilon,k}
=
q^\eta W^\epsilon D^k,
\qquad
\eta,\epsilon\in\{+1,-1\}.
\]

This must be a symbolic all-k theorem, not an inference from a bounded
power sweep.

## Method

- Reuse the proved \(k=0\) qW source theorem.
- Reuse the based \((Wq^{-1},D)\) primitive-pair coordinate for the
  \((\eta,\epsilon)=(+,-)\) row.
- For the other three orientations and \(k\ne0\), apply one common
  rank-four Whitehead automorphism.
- Express the cyclic image as one fixed boundary block followed by
  \(D^k\).
- Exhibit a spanning cycle on all eight signed basis vertices for each
  orientation and sign of k. Repetition of the D-block may add edges
  but cannot destroy the cycle.
- Apply Whitehead's cut-vertex lemma.

## Verified claim

The independent replay and hostile audit establish:

\[
Q_{\eta,\epsilon,k}\text{ is primitive}
\quad\Longleftrightarrow\quad
k=0
\ \text{or}\
(\eta,\epsilon)=(+,-).
\]

## Boundary

This is an individual-relator primitivity theorem. A nonprimitive row
cannot itself belong to a primitive pair. The theorem does not classify
primitive-pair creation after an AC product changes a row, or histories
containing more than one \(Wq^{-1}\)-type block.
