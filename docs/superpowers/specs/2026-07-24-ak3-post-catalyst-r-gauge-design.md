# AK(3) post-catalyst \(R\)-gauge closure design

Date: 2026-07-24

## Objective

Close the collected order in which an arbitrary AK(3) recovery is followed
by one \(B_U/D\) cross multiplication and then by an arbitrary finite tail
of moves that preserves each non-\(R\) relator modulo
\(\langle\!\langle R\rangle\!\rangle\), before a one-\(z\) isolator is
removed.

This is a mechanism theorem, not a trivialization of AK(3).

## Chosen approach

Work in

\[
G=F(x,t)/\langle\!\langle R\rangle\!\rangle
\quad\text{and}\quad
\widehat G=G*\langle z\rangle .
\]

For two quotient-equal isolators

\[
I=z^{-1}e,\qquad I_0=z^{-1}e_0,
\]

equality in \(\widehat G\) forces \(e=e_0\) in \(G\). If survivor words
\(J,J_0\) are also equal in \(\widehat G\), the evaluation maps
\(z\mapsto e\) and \(z\mapsto e_0\) coincide. Hence the eliminated
survivors \(J[z=e]\) and \(J_0[z=e_0]\) are equal modulo \(R\). The proved
fixed-relator normal-closure lemma then gives classical AC equivalence of
the two rank-two endpoints.

This avoids a case-by-case seam census. It is also stronger than a passive
eliminator projection because it permits \(R\)-gauge modifications of both
the future isolator and the future survivor.

## AK(3) application

Start from the arbitrary recovery tuple

\[
(R,B_U,D),\qquad
B_U=z^{-1}w,\quad
D=t^{-1}zxz^{-1}.
\]

The two existing one-\(D\) theorems classify every one-\(z\) target from
the single cross multiplication, for either target/source role. Take that
post-catalyst tuple as the baseline \((R,I_0,J_0)\).

Allow any finite suffix replacing \(I_0,J_0\) by quotient-equal
\(I,J\), while holding \(R\) fixed. In particular, this includes arbitrary
multiplication by conjugates of \(R^{\pm1}\), with \(R\) restored after use.
If the final \(I\) is a one-\(z\) isolator, the quotient-shadow lemma makes
its eliminated endpoint classically equivalent to the baseline, hence to
AK(3).

Taking the recovery prefix to be literal closes the \(D\)-then-\(R\)
collected order for both target roles.

## Verification

A dependency-free replay will use cancellation-heavy recovery words and
normal-closure factors with conjugators both with and without \(z\).
It will modify the isolator, the survivor, or both, substitute the resulting
isolator expression, and verify equality of the final survivor modulo
\(R=x^3t^{-4}\) using the exact amalgam normal form.

The replay is illustrative. Completeness comes from the quotient/evaluation
proof, not from a length bound.

## Scope

The theorem will not cover:

- changing or targeting \(R\);
- a second \(B_U/D\) cross multiplication;
- pre-catalyst \(R\)-moves that change \(D\)'s quotient shadow rather than
  only producing the recovery \(B_U\);
- a final primitive eliminator with several \(z^{\pm1}\)-occurrences;
- net survivor changes not quotient-equal modulo \(R\);
- additional stabilizations or dual-source compression.
