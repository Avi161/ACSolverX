# AK(3) final-target switch duality design

Date: 2026-07-25

## Objective

Prove that the choice of target in the final cross event does not change
the classical endpoint class after a one-\(z\) deletion. Apply the lemma
to identify the two remaining three-cross killer words `DBB` and `DBD`.

## Abstract lemma

Fix a retained relator \(R\) and two current non-\(R\) slots \(A,B\).
Up to multiplication side, a final cross target has the form

\[
T_A=A\,uB^\theta u^{-1},
\qquad
\theta\in\{\pm1\}.
\]

Cyclically rotate it to

\[
T_B=B^\theta u^{-1}Au.
\]

This is a legal final cross with the other slot as target after orienting
that target by \(\theta\). The two words are conjugate, so the same final
conjugation/orientation makes either one the identical isolator
\(z^{-1}e\).

After substituting \(z=e\), the target equation gives

\[
A_e\sim B_e^{-\theta}
\]

in \(G=F/\langle\!\langle R\rangle\!\rangle\). Therefore the two possible
surviving relators are equal up to quotient conjugacy and inversion. The
fixed-relator normal-closure lemma converts this equality to classical
AC1--AC3 equivalence.

## Scope

The lemma allows arbitrary words, arbitrary conjugator, either
multiplication side, either source sign, and fixed-\(R\) quotient gauges.
It assumes:

- the event is the final cross before deletion;
- the same target cyclic class is normalized to a one-\(z\) isolator;
- the retained relator remains \(R\); and
- final survivor spellings satisfy the usual quotient-restoration
  condition.

It does not identify the survivor with \(D_p\). It only proves that
switching the final target leaves the endpoint classical class unchanged.

## Consequence

Target words which differ only in their last letter have the same endpoint
classes:

\[
BBB\leftrightarrow BBD,\quad
BDD\leftrightarrow BDB,\quad
DBB\leftrightarrow DBD,\quad
DDB\leftrightarrow DDD.
\]

Hence the complete exactly-three classification has one, not two,
arbitrary bridge/twist killer mechanisms: the prefix `DB`. The unresolved
case may be represented by `DBD`.

AK(3) remains open.
