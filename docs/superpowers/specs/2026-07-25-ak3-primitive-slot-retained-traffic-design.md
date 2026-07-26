# AK(3) primitive-slot retained-traffic design

Date: 2026-07-25

## Objective

Decide the first AC1 move excluded by post-primitive naturality:
multiplication of a coherently transported retained consequence into the
primitive slot itself.

## General mechanism

Let \(W=\phi(q)\), let

\[
L=\langle\!\langle R_1,\ldots,R_k\rangle\!\rangle_{F(X)},
\]

and assume a balanced trivial-group checkpoint (for example, one
reached from a stabilization of the original presentation by stable AC
moves) has retained source slots \(\phi(R_i)\). For any \(V\in L\),
source multiplications can replace \(W\) by

\[
W_V=W\phi(V)=\phi(qV).
\]

Because \(V\) is \(q\)-free, the transvection

\[
\delta_V(q)=qV,\qquad \delta_V|_{F(X)}=\mathrm{id}
\]

is an automorphism. Hence \(W_V=(\phi\delta_V)(q)\) is primitive.

Straightening by

\[
(\phi\delta_V)^{-1}=\delta_V^{-1}\phi^{-1}
\]

returns every retained \(\phi(R_i)\) literally to \(R_i\). Modulo \(L\),
\(\delta_V^{-1}\) is invisible because \(V=1\), so every survivor has
the same quotient class as in the original \(W\)-deletion. The retained
sources absorb the difference.

## AK(3) certificate

At the source-slot checkpoint

\[
(\beta(R),W,D,q),
\]

take \(V=R\). One AC1 move gives

\[
W_R=W\beta(R)=\phi(qR).
\]

The displayed word is primitive, has \(q\)-exponent one, and contains
seven \(q^{\pm1}\)-occurrences. The new quotient sends the surviving
\(q\)-relator to

\[
U^{-1}R^{-1}.
\]

With \(U=RB\),

\[
(U^{-1}R^{-1})R^2=B^{-1},
\]

so two retained-\(R\) multiplications and inversion recover \(B\).
Every other survivor is unchanged modulo \(R\) from the already closed
source-slot endpoint.

## Boundary

This closes primitive-slot target traffic by coherent images of
\(q\)-free retained consequences. It does not close a source whose
\(\phi^{-1}\)-image contains \(q\), a multiplier outside the retained
normal closure, or a new primitive target not expressible as
\(\phi(qV)\).
