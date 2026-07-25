# Strictly alternating three-cross AK(3) routes reduce to a killer equation

Date: 2026-07-25

Status: **PROVEN** for the exponent and torus-weight reduction with
arbitrary conjugators, either multiplication side, intermediate
orientations, and fixed-\(R\) gauges. The first alternating order is a
self-loop under the established restoration hypotheses. In the reverse
order, exactly six arithmetic rows survive and every endpoint is a
weight-\(\pm1\) normal generator of the \((3,4)\)-torus-knot group.
The untwisted signed-seam subcorridor is completely enumerated and is a
self-loop. The arbitrary-bridge/twist case remains open. This theorem does
not trivialize AK(3).

## 1. Setup and canonical grammar

Put

\[
R=x^3t^{-4},
\qquad
G=\langle x,t\mid R\rangle,
\qquad
H=G*\langle z\rangle,
\tag{1.1}
\]

and

\[
p=xt,
\qquad
B=z^{-1}p,
\qquad
D=t^{-1}zxz^{-1}.
\tag{1.2}
\]

The stable-letter exponent and torus weight are the homomorphisms

\[
\sigma_z:H\longrightarrow\mathbb Z
\tag{1.3}
\]

and

\[
\operatorname{wt}(x)=4,\qquad
\operatorname{wt}(t)=3,\qquad
\operatorname{wt}(z)=0.
\tag{1.4}
\]

Thus

\[
\begin{array}{c|cc}
&\sigma_z&\operatorname{wt}\\ \hline
B&-1&7\\
D&0&1.
\end{array}
\tag{1.5}
\]

Both maps kill \(R\). Conjugation, multiplication side, and fixed-\(R\)
gauges do not affect either calculation.

At each event, whole-slot inversion can be moved into the sign of the
source and, when the inverted slot is the target, into inversion of the
new target plus a reversal of multiplication side. Whole-slot conjugation
is absorbed into the event conjugator. Consequently the signed recurrences
below cover arbitrary AC1/AC3 normalization between events. They make no
restriction on the event conjugators.

This theorem treats **strictly alternating** target roles. Histories with
two consecutive events targeting the same slot are not silently folded
into this statement.

## 2. The \(D\to B\to D\to B\) order closes

First let \(D^\epsilon\) target \(B\), producing \(B_1\). Next let
\(B_1^\eta\) target \(D\), producing \(D_1\). Finally let
\(D_1^\theta\) target \(B_1\), producing \(B_2\). Here

\[
\epsilon,\eta,\theta\in\{1,-1\}.
\tag{2.1}
\]

The exponent recurrence is

\[
\sigma_z(B_1)=-1,
\qquad
\sigma_z(D_1)=-\eta,
\tag{2.2}
\]

and

\[
\boxed{
\sigma_z(B_2)=-1-\eta\theta\in\{0,-2\}.
}
\tag{2.3}
\]

Target inversion changes only the sign. Therefore \(B_2\), the third
target, cannot normalize to a one-\(z\) generator isolator.

The only other final slot is \(D_1\), the source of the third event. If
that slot is the final isolator, evaluation at \(z=e\) kills the entire
third-event factor in \(B_2\). What remains is precisely the endpoint of
the first two alternating events, up to the stated fixed-\(R\) gauges,
conjugations, and inversions. The exactly-two-cross theorem returns that
endpoint classically to AK(3).

Hence this alternating order is completely closed under the restoration
hypotheses of
`literature/proofs/AK3_TWO_CROSS_FEEDBACK_SELF_LOOP.md`.

## 3. The \(B\to D\to B\to D\) order

Now let \(B^\epsilon\) target \(D\), producing \(D_1\); let
\(D_1^\eta\) target \(B\), producing \(B_1\); and let
\(B_1^\theta\) target \(D_1\), producing \(D_2\). In quotient-shadow
notation one may write

\[
\begin{aligned}
D_1&=
D\,uB^\epsilon u^{-1}
\quad\text{or}\quad
uB^\epsilon u^{-1}D,\\
B_1&=
B\,vD_1^\eta v^{-1}
\quad\text{or}\quad
vD_1^\eta v^{-1}B,\\
D_2&=
D_1\,wB_1^\theta w^{-1}
\quad\text{or}\quad
wB_1^\theta w^{-1}D_1,
\end{aligned}
\tag{3.1}
\]

where \(u,v,w\in H\) are arbitrary.

Suppose the third target is the final isolator. After final conjugation
and orientation, write

\[
I=aD_2^\delta a^{-1}=z^{-1}e,
\qquad
\delta\in\{1,-1\},
\qquad
e\in F(x,t).
\tag{3.2}
\]

The stable-letter exponents are

\[
\begin{aligned}
\sigma_z(D_1)&=-\epsilon,\\
\sigma_z(B_1)&=-1-\epsilon\eta,\\
\sigma_z(D_2)&=-\epsilon-\theta-\epsilon\eta\theta.
\end{aligned}
\tag{3.3}
\]

Thus the all-positive and all-negative sign rows have exponent \(-3\)
and \(3\), respectively, and cannot produce a one-\(z\) isolator. The
other six rows have exponent \(\pm1\), and

\[
\boxed{
\delta=-\sigma_z(D_2).
}
\tag{3.4}
\]

The alternative final slot \(B_1\), which is the source of the third
event, has exponent \(0\) or \(-2\) by (3.3). It cannot be a one-\(z\)
isolator. Therefore (3.2) is the only exponent-feasible deletion in this
order.

## 4. Weight gives the complete six-row table

The weight recurrence is

\[
\begin{aligned}
\operatorname{wt}(D_1)
&=1+7\epsilon,\\
\operatorname{wt}(B_1)
&=7+\eta(1+7\epsilon),\\
\operatorname{wt}(D_2)
&=1+7\epsilon+
  \theta\bigl(7+\eta(1+7\epsilon)\bigr).
\end{aligned}
\tag{4.1}
\]

Equation (3.2) gives

\[
\operatorname{wt}(e)
=
\delta\operatorname{wt}(D_2).
\tag{4.2}
\]

Let

\[
C=B_1[z\mapsto e]
\tag{4.3}
\]

be the surviving relator. Substitution changes weight by stable-letter
exponent:

\[
\operatorname{wt}(C)
=
\operatorname{wt}(B_1)
+\sigma_z(B_1)\operatorname{wt}(e).
\tag{4.4}
\]

The complete arithmetic is:

| \((\epsilon,\eta,\theta)\) | \(\sigma_z(D_2)\) | \(\delta\) | \(\operatorname{wt}(e)\) | \(\sigma_z(B_1)\) | \(\operatorname{wt}(C)\) |
|---|---:|---:|---:|---:|---:|
| \((+,+,+)\) | \(-3\) | -- | -- | \(-2\) | blocked |
| \((+,+,-)\) | \(1\) | \(-1\) | \(7\) | \(-2\) | \(1\) |
| \((+,-,+)\) | \(-1\) | \(1\) | \(7\) | \(0\) | \(-1\) |
| \((+,-,-)\) | \(-1\) | \(1\) | \(9\) | \(0\) | \(-1\) |
| \((-,+,+)\) | \(1\) | \(-1\) | \(5\) | \(0\) | \(1\) |
| \((-,+,-)\) | \(1\) | \(-1\) | \(7\) | \(0\) | \(1\) |
| \((-,-,+)\) | \(-1\) | \(1\) | \(7\) | \(-2\) | \(-1\) |
| \((-,-,-)\) | \(3\) | -- | -- | \(-2\) | blocked |

\[
\tag{4.5}
\]

There is no remaining arithmetic obstruction in the six middle rows.

## 5. The endpoint is a torus-knot killer, not necessarily a meridian

The rank-three tuple \((R,B,D)\) presents the trivial group. Cross events,
fixed-\(R\) gauges, and the substitution-and-removal composite preserve
the presented group. After deleting (3.2), the endpoint is

\[
(R,C).
\tag{5.1}
\]

It therefore presents the trivial group. Equivalently,

\[
\boxed{
\langle\!\langle C\rangle\!\rangle_G=G.
}
\tag{5.2}
\]

Thus \(C\) is a normal generator, or *killer*, of the
\((3,4)\)-torus-knot group \(G\). Equation (4.5) additionally pins its
abelianization class to \(\pm1\).

This conclusion must not be strengthened to “\(C\) is a meridian.”
Silver, Whitten, and Williams prove that every nontrivial torus-knot group
contains infinitely many pairwise inequivalent pseudo-meridians:
weight-one normal generators which are not automorphic images of a
meridian; see *Knot Groups with Many Killers*, Theorem 1.2 and
Corollary 1.3,
[arXiv:0909.3275](https://arxiv.org/abs/0909.3275).

Consequently normal generation and weight cannot close the six rows.
One must use the three-cross word equations or additional geometry.

## 6. Complete untwisted signed-seam certificate

There is one finite subcorridor in which the word equations can be solved
completely. Work now with the literal free words in \(F(x,t,z)\), without
an inserted \(R\)-gauge, relative bridge, or vertex-stabilizer twist at
any event.

For a cyclically reduced word \(W\), let

\[
\mathcal S(W)
\tag{6.1}
\]

be the finite set of cyclic rotations of \(W\) and \(W^{-1}\). Define

\[
\mathcal P(U,V)
=
\left\{
\operatorname{cyc}(uv):
u\in\mathcal S(U),\
v\in\mathcal S(V)
\right\}
\big/
\text{signed cyclic rotation}.
\tag{6.2}
\]

This covers either multiplication side because \(uv\) and \(vu\) are
conjugate. It also covers arbitrary whole-factor orientations and cyclic
phases. By definition, an untwisted seam event has trivial relative
conjugator after those choices, so (6.2) is complete for this subcorridor.

Starting in the order of Section 3, form

\[
\begin{aligned}
\mathcal D_1&=\mathcal P(D,B),\\
\mathcal Q&=
\{(D_1,B_1):D_1\in\mathcal D_1,\
  B_1\in\mathcal P(B,D_1)\},\\
\mathcal T&=
\{(D_1,B_1,D_2):(D_1,B_1)\in\mathcal Q,\
  D_2\in\mathcal P(D_1,B_1),\
  \nu_z(D_2)=1\}.
\end{aligned}
\tag{6.3}
\]

Here \(\nu_z\) counts occurrences, not exponent. Every \(D_2\) in
\(\mathcal T\) has a unique orientation and cyclic phase

\[
D_2=z^{-1}e.
\tag{6.4}
\]

Direct finite reduction gives

\[
\boxed{
|\mathcal D_1|=16,\qquad
|\mathcal Q|=416,\qquad
|\mathcal T|=522,
}
\tag{6.5}
\]

with \(69\) distinct final target classes. For every one of the \(522\)
triples,

\[
\boxed{
B_1[z\mapsto e]
\ \text{is freely conjugate to}\
D_p^{\pm1},
}
\tag{6.6}
\]

where

\[
D_p=t^{-1}(xt)x(xt)^{-1}
=\texttt{TxtxTX}.
\tag{6.7}
\]

The unique signed cyclic key is `TXTxtx`. Hence the fixed-\(R\) endpoint
is classically AC-equivalent to

\[
(R,D_p)=\operatorname{AK}(3)
\tag{6.8}
\]

by AC3 and, if needed, AC1.

The dependency-free verifier

```text
tests/stable_ac/test_three_cross_killer_reduction.py
```

reconstructs the sets in (6.3), checks every count in (6.5), performs all
\(522\) substitutions, and checks (6.6). The computation is a finite
decision-procedure certificate for the explicitly defined untwisted
grammar; it is not evidence about omitted bridges or twists.

## 7. Combined conclusion and scope

Under the restoration hypotheses already used by the one-way and
two-cross theorems:

1. the strictly alternating order \(D\to B\to D\to B\) is a self-loop for
   arbitrary event conjugators;
2. the reverse order has exactly six exponent-feasible sign rows;
3. every endpoint in those rows is a weight-\(\pm1\) killer of \(G\); and
4. every untwisted signed-seam realization of those rows is a classical
   AK(3) self-loop.

Therefore a new endpoint in the reverse strictly alternating
three-cross corridor must use at least one nontrivial relative bridge,
vertex-stabilizer twist, or literal intermediate \(R\)-gauge. Its endpoint
must solve the six-row killer equation rather than merely pass exponent
or abelianization.

The theorem does not cover non-strict target orders, arbitrary bridge or
twist geometry in the reverse order, a changed retained relator, a
multi-\(z\) primitive eliminator, another stabilization, or dual-source
primitive-pair compression.

AK(3) remains open.
