# AK(3) multi-source primitive-loop design

Date: 2026-07-25

## Objective

Extend the relation-split self-loop from one retained relator \(R\) to
an arbitrary retained source subtuple. This decides the first
cross-coupled primitive construction, where the AK(3) relator \(B\) is
used essentially together with \(R\).

## General theorem

Let

\[
\mathcal P
=
\langle X\mid R_1,\ldots,R_k,S_1,\ldots,S_m\rangle
\]

be a balanced presentation of the trivial group. Stabilize by \(q\), let
\(\rho(q)=1\), and take

\[
\beta(q)=q,\qquad \rho\beta=\rho.
\]

For any

\[
U\in
\langle\!\langle R_1,\ldots,R_k\rangle\!\rangle_{F(X)},
\]

put

\[
\alpha_U(q)=Uq,\qquad
\phi=\beta\alpha_U,\qquad
W=\beta(U)q.
\]

Use \(q\) to replace every retained source \(R_i\) by \(\beta(R_i)\).
Then use the \(\beta(R_i)\)-subtuple to replace \(q\) by
\(q\beta(U)\), and conjugate to \(W\).

After primitive straightening and deletion, the retained sources return
literally to \(R_i\). Every other survivor has the same image as its
baseline word modulo
\(\langle\!\langle R_1,\ldots,R_k\rangle\!\rangle\), so a multi-source
normal-closure lemma returns the endpoint classically.

## AK(3) cross-coupled certificate

At the rank-three root, take retained sources

\[
R=x^3t^{-4},
\qquad
B=z^{-1}xt,
\]

the remaining survivor

\[
D=t^{-1}zxz^{-1},
\]

and \(U=RB\). With

\[
\beta(x)=qxq^{-1}
\]

and \(t,z,q\) fixed,

\[
W=\beta(RB)q
\]

is primitive and contains five \(q^{\pm1}\)-occurrences before any
accidental boundary reduction.

Exact certificates will:

1. replace both \(R\) and \(B\) by their \(\beta\)-images using only
   conjugates of \(q^{\pm1}\);
2. build \(W\) by two target multiplications and one conjugation;
3. compute
   \[
   p(x)=UxU^{-1};
   \]
4. return
   \[
   D'=t^{-1}zUxU^{-1}z^{-1}
   \]
   to \(D\) by four conjugates of \(R^{\pm1},B^{\pm1}\).

## Boundary

This closes cross-coupling through any retained, coherently transported
source subtuple. It does not close a history that deletes one of the
source relators used in \(U\), fails to retain its normal closure, or
leaves a survivor outside its baseline class modulo the retained
subtuple.

