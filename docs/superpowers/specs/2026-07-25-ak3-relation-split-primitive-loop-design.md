# AK(3) relation-split primitive-loop design

Date: 2026-07-25

## Objective

Decide the most direct asymmetric production of the primitive word

\[
V=qx^3q^{-1}t^{-4}q.
\]

The construction uses the stabilizing relator \(q\) to replace the
retained relator \(R=x^3t^{-4}\) by its partial-conjugation image, then
multiplies that image into \(q\). The desired result is an unbounded
theorem showing that this whole architecture is a stable self-loop.

## General setup

Assume

\[
F=F(X)*\langle q\rangle,\qquad
\rho:F\to F(X)
\]

kills \(q\), and that
\(\langle X\mid R,S_1,\ldots,S_m\rangle\) is a balanced
trivial-group presentation. Choose

\[
U\in\langle\!\langle R\rangle\!\rangle_{F(X)}.
\]

Let
\(\beta\in\operatorname{Aut}(F)\) satisfy

\[
\beta(q)=q,\qquad \rho\beta=\rho.
\]

Define

\[
\alpha_U(q)=Uq,\quad \alpha_U|_{F(X)}=\mathrm{id},
\qquad
\phi=\beta\alpha_U,
\qquad
W=\phi(q)=\beta(U)q.
\]

## Proposed theorem

Starting from the stabilized tuple

\[
(R,S_1,\ldots,S_m,q),
\]

the fixed-\(q\) normal-closure lemma replaces \(R\) by \(\beta(R)\).
Because \(\beta(U)\in\langle\!\langle\beta(R)\rangle\!\rangle\), the
fixed-\(\beta(R)\) lemma and a conjugation replace \(q\) by \(W\).

Straighten \(W\) by \(\phi^{-1}\) and delete \(q\). The endpoint is

\[
(R,p(S_1),\ldots,p(S_m)),
\qquad
p=\rho\phi^{-1}.
\]

In the quotient \(F(X)/\langle\!\langle R\rangle\!\rangle\), both
\(\alpha_U\) and \(\beta\) induce the identity after \(q=1\). Therefore

\[
p(S_i)=S_i
\pmod{\langle\!\langle R\rangle\!\rangle}.
\]

The fixed-\(R\) normal-closure lemma then returns every survivor to
\(S_i\) by classical AC moves.

## AK(3) specialization

Take \(X=(x,t,z)\),

\[
R=x^3t^{-4},\qquad
B=z^{-1}xt,\qquad
D=t^{-1}zxz^{-1},
\]

Take \(U=R\) and

\[
\beta(x)=qxq^{-1},\qquad
\beta(t)=t,\qquad
\beta(z)=z,\qquad
\beta(q)=q.
\]

Then

\[
\beta(R)=qx^3q^{-1}t^{-4},
\qquad
W=\beta(R)q=V.
\]

The primitive quotient is

\[
\begin{aligned}
p(x)&=RxR^{-1},&
p(t)&=t,&
p(z)&=z,&
p(q)&=R^{-1},
\end{aligned}
\]

so

\[
\begin{aligned}
B'&=z^{-1}RxR^{-1}t,\\
D'&=t^{-1}zRxR^{-1}z^{-1}.
\end{aligned}
\]

Exact two-conjugate factorizations will certify
\(B^{-1}B',D^{-1}D'\in\langle\!\langle R\rangle\!\rangle\).

## Result boundary

This closes every production of the displayed form for every
\(U\in\langle\!\langle R\rangle\!\rangle\), including the obvious direct
construction of \(V\). It does not close histories whose use of \(B\) or
\(D\) leaves a survivor outside its baseline class modulo \(R\), changes
the retained normal closure, or creates a primitive multi-\(q\) word
outside this relative-automorphism family.
