# Every post-catalyst \(R\)-gauge tail is an AK(3) self-loop

Date: 2026-07-24

Status: **PROVEN** for an arbitrary recovery prefix, one classified
\(B_U/D\) cross multiplication, and an arbitrary finite fixed-\(R\) gauge
suffix which ends in a one-\(z\) isolator. There is no bound on the recovery
word, the catalyst conjugator, the number of gauge factors, or their
conjugators. This is a mechanism-closing theorem, not a trivialization of
AK(3).

## 1. Quotient shadows and evaluation

Let \(X\) be a two-element free basis, let \(R\in F(X)\), and put

\[
G=F(X)/\langle\!\langle R\rangle\!\rangle .
\tag{1.1}
\]

Because \(R\) has no \(z\)-letter,

\[
F(X,z)/\langle\!\langle R\rangle\!\rangle
\cong
G*\langle z\rangle .
\tag{1.2}
\]

Write

\[
\pi:F(X,z)\longrightarrow G*\langle z\rangle
\tag{1.3}
\]

for the quotient map. For \(e\in F(X)\), let

\[
\operatorname{ev}_e:G*\langle z\rangle\longrightarrow G
\tag{1.4}
\]

be the homomorphism which is the identity on \(G\) and sends \(z\) to the
class of \(e\). If \(J\in F(X,z)\), then

\[
\operatorname{ev}_e(\pi(J))
=
\bigl[J[z\mapsto e]\bigr]_G.
\tag{1.5}
\]

Here every \(z^{-1}\) is replaced by \(e^{-1}\), followed by free
reduction.

## 2. The quotient-shadow lemma

### Lemma 2.1

Let

\[
I_0=z^{-1}e_0,\qquad I=z^{-1}e,
\qquad e_0,e\in F(X),
\tag{2.1}
\]

and let \(J_0,J\in F(X,z)\). Suppose

\[
\pi(I)=\pi(I_0),
\qquad
\pi(J)=\pi(J_0).
\tag{2.2}
\]

Define the two eliminated survivors

\[
C_0=J_0[z\mapsto e_0],
\qquad
C=J[z\mapsto e].
\tag{2.3}
\]

Then

\[
[C]_G=[C_0]_G.
\tag{2.4}
\]

Consequently,

\[
(R,C)\sim_{\mathrm{AC1-3}}(R,C_0).
\tag{2.5}
\]

#### Proof

The first equality in (2.2) says

\[
z^{-1}[e]_G=z^{-1}[e_0]_G
\quad\text{in}\quad
G*\langle z\rangle .
\]

Multiplication on the left by \(z\) gives

\[
[e]_G=[e_0]_G.
\tag{2.6}
\]

Therefore the two evaluation homomorphisms in (1.4) coincide:

\[
\operatorname{ev}_e=\operatorname{ev}_{e_0}.
\tag{2.7}
\]

Using the second equality in (2.2) and then (1.5),

\[
\begin{aligned}
[C]_G
&=\operatorname{ev}_e(\pi(J))\\
&=\operatorname{ev}_{e_0}(\pi(J_0))\\
&=[C_0]_G.
\end{aligned}
\tag{2.8}
\]

Thus \(C^{-1}C_0\in\langle\!\langle R\rangle\!\rangle\) in \(F(X)\).
The fixed-relator normal-closure lemma from
`literature/proofs/AK3_ARBITRARY_RECOVERY_SELF_LOOP.md`, Lemma 2.1,
replaces the second relator by a finite product of conjugates of
\(R^{\pm1}\), while restoring \(R\) after each factor. This proves (2.5).
\(\square\)

No trivial-group hypothesis enters Lemma 2.1. It is a statement about
classical AC equivalence of its two rank-two endpoints.

## 3. Fixed-\(R\) gauge tails

Call a replacement \(W\rightsquigarrow W'\) of a non-\(R\) relator an
\(R\)-gauge modification if

\[
\pi(W')=\pi(W).
\tag{3.1}
\]

Every multiplication of \(W\) by a conjugate of \(R^{\pm1}\), on either
side, is an \(R\)-gauge modification. The conjugating word may contain
\(z^{\pm1}\). Arbitrary finite products of such factors are allowed.
Conversely, (3.1) means that \(W^{-1}W'\) lies in the normal closure of
\(R\), so the same fixed-relator construction realizes the replacement by
AC1--AC3 moves with \(R\) held fixed.

Temporary conjugations or inversions used to implement a factor may be
arbitrary. The definition requires only that the final quotient shadow of
each slot be restored. A net conjugation or inversion which changes that
shadow is outside (3.1).

### Theorem 3.1

Let

\[
(R,I_0,J_0),
\qquad
I_0=z^{-1}e_0,
\tag{3.2}
\]

be a balanced presentation of the trivial group. Apply arbitrary finite
\(R\)-gauge modifications to either non-\(R\) slot, reaching

\[
(R,I,J),
\qquad
I=z^{-1}e.
\tag{3.3}
\]

Use \(I\) as a generator isolator, apply the substitution-and-removal stable
composite, and retain

\[
(R,C),
\qquad C=J[z\mapsto e].
\tag{3.4}
\]

Then

\[
(R,C)
\sim_{\mathrm{AC1-3}}
(R,J_0[z\mapsto e_0]).
\tag{3.5}
\]

#### Proof

The gauge hypothesis is exactly (2.2), so Lemma 2.1 gives (3.5). The
trivial-group hypothesis is used only to justify the stable
substitution-and-removal step producing (3.4). It is not a bare AC5 move,
and no elementary move-count bound is asserted. \(\square\)

Theorem 3.1 permits simultaneous changes to the future isolator and the
future survivor. It is stronger than a projection statement in which the
eliminator must remain passive.

## 4. Application after one AK(3) catalyst

Return to

\[
R=x^3t^{-4},
\qquad
B_U=z^{-1}w,
\qquad
D=t^{-1}zxz^{-1},
\tag{4.1}
\]

where

\[
w=\overline{xU},
\qquad
U=t
\quad\text{in}\quad
\langle x,t\mid R\rangle .
\tag{4.2}
\]

The tuple \((R,B_U,D)\) presents the trivial group and is stably reached
from AK(3).

Perform one multiplication between arbitrary conjugates and orientations
of \(B_U\) and \(D\), with either slot as target, and restore the source.
The two mixed-recovery one-\(D\) theorems show that every one-\(z\) target
may be normalized by target inversion and cyclic conjugation to one of

\[
I_{0,+}=z^{-1}e_+,
\qquad
I_{0,-}=z^{-1}e_-,
\tag{4.3}
\]

where

\[
e_+=t^{-1}wx,
\qquad
e_-=twx^{-1}.
\tag{4.4}
\]

If \(B_U\) was the target, the baseline survivor is \(J_0=D\).
If \(D\) was the target, the baseline survivor is \(J_0=B_U\).
In all four cases, eliminating \(I_{0,\pm}\) gives a rank-two pair
classically AC-equivalent to AK(3).

Now append any finite \(R\)-gauge tail modifying either the isolator slot,
the survivor slot, or both. Require the final chosen linear spelling of the
isolator slot to be

\[
I=z^{-1}e.
\tag{4.5}
\]

By the definition of a gauge tail, its quotient shadow is still exactly the
shadow of \(I_{0,\pm}\). Theorem 3.1 makes the final eliminated endpoint
classically AC-equivalent to the corresponding baseline endpoint, hence

\[
\boxed{
\text{every such endpoint is classically AC-equivalent to AK(3).}
}
\tag{4.6}
\]

There is no bound on \(U\), on the relative conjugator in the catalyst, on
the number of \(R\)-gauge factors, or on their conjugators.

Taking \(U=t\) closes the collected order

\[
\text{one \(D\)-event}
\quad\longrightarrow\quad
\text{arbitrary fixed-\(R\) gauge tail}
\quad\longrightarrow\quad
\text{one-\(z\) elimination}
\tag{4.7}
\]

for both choices of target slot. More generally, (4.6) permits an arbitrary
recovery prefix before the \(D\)-event and an arbitrary \(R\)-gauge suffix
after it.

## 5. Scope

The proof is an exact quotient argument, not a bounded enumeration. It
closes every suffix whose two final non-\(R\) slots have the same quotient
shadows as the classified post-catalyst baseline.

It does not cover:

- targeting or changing the retained relator \(R\);
- a second multiplication between the \(B_U\)- and \(D\)-slots;
- pre-catalyst \(R\)-moves that change \(D\)'s quotient shadow instead of
  only producing the recovery \(B_U\);
- a net conjugation or inversion whose quotient shadow is not restored;
- a final primitive eliminator with several \(z^{\pm1}\)-occurrences;
- another stabilization or dual-source compression.

AK(3) remains open.
