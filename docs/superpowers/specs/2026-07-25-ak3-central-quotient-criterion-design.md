# AK(3) central-quotient conjugacy criterion design

Date: 2026-07-25

## Objective

Give an exact, decidable conjugacy criterion in the torus-knot group

\[
G=\langle x,t\mid x^3=t^4\rangle
\]

and apply it to the remaining prefix-`DB` three-cross killer equation.

## Algebra

Put

\[
c=x^3=t^4.
\]

The element \(c\) is central and

\[
G/\langle c\rangle
\cong
C_3*C_4
=
\langle \bar x,\bar t\mid \bar x^3=\bar t^4=1\rangle.
\]

The quotient kernel is exactly \(\langle c\rangle\). Let

\[
\operatorname{wt}(x)=4,\qquad
\operatorname{wt}(t)=3,
\]

so \(\operatorname{wt}(c)=12\).

For \(U,V\in G\):

\[
U\text{ is conjugate to }V
\iff
\operatorname{wt}(U)=\operatorname{wt}(V)
\text{ and }
\bar U\text{ is conjugate to }\bar V\text{ in }C_3*C_4.
\]

The forward implication is immediate. For the reverse implication, lift a
quotient conjugator \(g\). Then

\[
U=c^k gVg^{-1}
\]

for some \(k\in\mathbb Z\). Equal weight forces \(12k=0\), hence \(k=0\).

Conjugacy in \(C_3*C_4\) is decidable by cyclically reducing its alternating
normal form and comparing cyclic rotations. This produces a small exact
certificate, not a heuristic invariant.

## AK(3) consequence

Let

\[
D_p=t^{-1}(xt)x(xt)^{-1}.
\]

Every feasible three-cross prefix-`DB` survivor \(C\) already has
\(\operatorname{wt}(C)=s\in\{\pm1\}\). Therefore

\[
\bar C\sim\overline{D_p^s}
\quad\Longrightarrow\quad
C\sim D_p^s\text{ in }G.
\]

The fixed-\(R\) lemma then proves

\[
(R,C)\sim_{\mathrm{AC1-3}}(R,D_p).
\]

Thus projected conjugacy is an exact finish criterion for any candidate
from the remaining killer equation. Failure of the criterion does not
prove AC inequivalence; it only shows that this direct fixed-\(R\)
conjugacy finish is unavailable.

## Verification

The replay independently implements:

- the amalgam normal form \(c^k s_1\cdots s_r\);
- projection to \(C_3*C_4\);
- cyclic reduction and conjugacy keys there;
- central shifts with identical projection but distinct weights; and
- representative HNN endpoints \(D(e_n)=t^{-n}D_pt^n\) for
  \(-12\le n\le12\).

No AC graph search is used. AK(3) remains open.
