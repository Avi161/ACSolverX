# Every direct recovery endpoint is a classical AK(3) self-loop

Date: 2026-07-24

Status: **PROVEN** for every quotient-equal recovery word, with no
word-length bound.  The conclusion is classical AC equivalence, not merely
stable AC equivalence.  It does not trivialize AK(3).

## 1. Statement

Put

\[
R=x^3t^{-4}
\tag{1.1}
\]

and let \(U(x,t)\) be any word satisfying

\[
U=t
\quad\text{in}\quad
\langle x,t\mid R\rangle .
\tag{1.2}
\]

Define

\[
e_U=xU,\qquad
Y_U=e_Uxe_U^{-1},\qquad
S_U=t^{-1}Y_U,
\tag{1.3}
\]

and consider the two direct-recovery endpoints

\[
\begin{aligned}
P(U)&=(A_U,S_U),
& A_U&=x^3Y_U^{-4},\\
Q(U)&=(R,S_U).
\end{aligned}
\tag{1.4}
\]

The pair \(P(U)\) is the endpoint obtained after restoring the original
power relator before eliminating the old generator.  The pair \(Q(U)\)
is obtained by leaving the compressed torus-knot relator \(R\) untouched.

### Theorem 1.1

For every solution of (1.2),

\[
\boxed{
P(U)\sim_{\mathrm{AC1-3}}Q(U)
\sim_{\mathrm{AC1-3}}\operatorname{AK}(3).
}
\tag{1.5}
\]

Thus every restored or unrestored direct recovery in this one-source
architecture is a classical AC self-loop.  The stable construction that
discovers these endpoints does not escape the classical AC class of
AK(3).

## 2. A fixed-relator normal-closure lemma

### Lemma 2.1

Let \(W,V,V'\) be elements of a free group.  If

\[
V^{-1}V'\in\langle\!\langle W\rangle\!\rangle,
\tag{2.1}
\]

then

\[
(W,V)\sim_{\mathrm{AC1-3}}(W,V').
\tag{2.2}
\]

Equivalently, with one relator \(W\) held fixed, the other relator may be
replaced by any word representing the same element in
\(F/\langle\!\langle W\rangle\!\rangle\).

#### Proof

By the definition of normal closure, there is a finite expression

\[
V^{-1}V'
=
\prod_{i=1}^m g_iW^{\varepsilon_i}g_i^{-1},
\qquad \varepsilon_i\in\{1,-1\}.
\tag{2.3}
\]

For each factor, temporarily invert \(W\) if
\(\varepsilon_i=-1\), conjugate it by \(g_i\), right-multiply the other
relator by the resulting conjugate, and then undo the conjugation and
inversion of \(W\).  These are AC1--AC3 moves, and \(W\) is restored after
every factor.  After all factors, the second relator is

\[
V(V^{-1}V')=V'.
\]

This proves (2.2). \(\square\)

No trivial-group hypothesis, stabilization, ambient automorphism, or move
bound is used in this lemma.  The factorization in (2.3) is finite but
need not have a uniform length bound.

## 3. The first side of the diamond: restored to unrestored

The words in (1.3) satisfy the exact free equality

\[
Y_U=tS_U.
\tag{3.1}
\]

Consequently,

\[
\begin{aligned}
A_U^{-1}R
&=Y_U^4t^{-4}\\
&=(tS_U)^4t^{-4}\\
&=(tS_Ut^{-1})
  (t^2S_Ut^{-2})
  (t^3S_Ut^{-3})
  (t^4S_Ut^{-4}).
\end{aligned}
\tag{3.2}
\]

This is an explicit product of four conjugates of \(S_U\).  Applying
Lemma 2.1 with the two relators interchanged gives

\[
(A_U,S_U)\sim_{\mathrm{AC1-3}}(R,S_U).
\tag{3.3}
\]

In other words,

\[
P(U)\sim_{\mathrm{AC1-3}}Q(U)
\tag{3.4}
\]

for every word \(U\), even before imposing the quotient equation (1.2).
Restoring the original power relator is therefore a four-factor classical
AC gauge operation after elimination.

## 4. The second side: every recovery returns to the literal one

Let

\[
e_t=xt,\qquad
Y_t=(xt)x(xt)^{-1},\qquad
S_t=t^{-1}Y_t.
\tag{4.1}
\]

Equation (1.2) implies

\[
e_U=e_t,\qquad
Y_U=Y_t,\qquad
S_U=S_t
\quad\text{in}\quad
F(x,t)/\langle\!\langle R\rangle\!\rangle.
\tag{4.2}
\]

Hence

\[
S_U^{-1}S_t\in\langle\!\langle R\rangle\!\rangle.
\tag{4.3}
\]

Lemma 2.1 now gives

\[
Q(U)=(R,S_U)
\sim_{\mathrm{AC1-3}}
(R,S_t)=Q(t).
\tag{4.4}
\]

This is the unbounded step.  It uses only the defining meaning of
\(U=t\) in the one-relator quotient; no grammar or bound on a
normal-closure factorization is asserted.

## 5. The literal endpoint is AK(3)

Write the AK(3) braid relator as

\[
B=xtxt^{-1}x^{-1}t^{-1}.
\tag{5.1}
\]

Direct free reduction gives

\[
\begin{aligned}
S_t
&=t^{-1}(xt)x(xt)^{-1}\\
&=t^{-1}xtxt^{-1}x^{-1}\\
&=t^{-1}Bt.
\end{aligned}
\tag{5.2}
\]

Thus \(S_t\) is a conjugate of \(B\), while the other relator is already

\[
R=x^3t^{-4}.
\]

One AC3 move therefore gives

\[
Q(t)=(R,S_t)
\sim_{\mathrm{AC3}}
(R,B)=\operatorname{AK}(3).
\tag{5.3}
\]

Combining (3.4), (4.4), and (5.3) proves Theorem 1.1.

## 6. Consequences and scope

The unbounded floor theorem in
`literature/proofs/AK3_ARBITRARY_RECOVERY_FLOOR_BARRIER.md` remains true:
every restored endpoint \(P(U)\) has complete Aut(\(F_2\))-floor at least
\(14\), sharply.  The present theorem closes the mechanism more strongly.
Those high-floor endpoints are simply nonminimal states inside the
classical AC class of AK(3).

The theorem includes all consequence-twisted, power-conjugated, and mixed
recovery families previously studied, because it assumes only (1.2).
It also covers the branch which never restores the source relator.

It does not say that arbitrary change-of-variables moves are classical
self-loops.  Its exact hypotheses are essential: one retained relator is
\(R\), the final isolator is \(z^{-1}xU\), and \(U=t\) modulo \(R\).
A route can evade the theorem by changing the retained relator or the
recovery equation, using the defining relator while constructing a
different final isolator, compressing both source relators into a primitive
pair before either old generator is removed, or using a different
stabilization architecture.

The theorem neither proves nor disproves AC or stable AC for AK(3).
