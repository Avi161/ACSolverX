# AK(3) z-dependent D-tail primitivity design

Date: 2026-07-26

## Objective

Classify the eight first z-dependent changed sources

\[
Q_{\eta,\epsilon,\delta}
=
q^\eta W^\epsilon D^\delta,
\qquad
\eta,\epsilon,\delta\in\{+1,-1\}.
\]

These lie outside the unique-z transported-tail theorem because D
contains two z-letters.

## Method

Use exact Whitehead theory in \(F(x,t,z,q)\), not AC graph search.

- For primitive rows, provide a strict sequence of explicit
  second-kind Whitehead automorphisms ending at one basis letter.
- For nonprimitive rows, reduce to a cyclic word whose Whitehead graph
  contains a spanning cycle on all eight signed basis vertices.
  Whitehead's cut-vertex lemma then obstructs primitivity.
- Replay every word, automorphism, length drop, graph edge, and cycle
  independently.

## Expected classification

The two rows

\[
qW^{-1}D,
\qquad
qW^{-1}D^{-1}
\]

are primitive.

The other six sign rows are nonprimitive. Their certificates use one
common first automorphism

\[
x\mapsto q^{-1}xq,
\qquad
z\mapsto zq,
\]

with one additional Whitehead move in two rows.

## Boundary

This classifies primitive-single deletion of the changed source only.
It does not compute the deletion endpoints of the two primitive
exceptions, classify primitive-pair creation after an AC2 product
changes a row, or classify longer z-dependent tails.

The six nonprimitive rows cannot themselves be components of a
primitive pair. What remains open is primitive-pair creation after an
AC product changes one of the displayed rows.
