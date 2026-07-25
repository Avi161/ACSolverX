# Every exactly-two-cross AK(3) route is a self-loop

Date: 2026-07-25

Status: **PROVEN** for exactly two \(B/D\) cross events, arbitrary
conjugators, either multiplication side, arbitrary fixed-\(R\) gauges, and
a final one-\(z\) generator isolator under the stated restoration
hypotheses. Together with the one-way theorem, this closes both same-target
and alternating-target orders. It does not trivialize AK(3).

## 1. Quotient setup

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

The one-way theorem already closes every two-event history in which both
cross events target the same slot. It remains to treat alternating target
roles.

Whole-relator AC1/AC3 moves let us normalize the orientation and cyclic
position of a slot before it is used in the next cross event. Their signs
are absorbed into the two source signs below. Fixed-\(R\) gauges vanish in
\(H\).

## 2. The exponent-feasible alternating order

First target the \(B\)-slot by a conjugate of \(D^\epsilon\), with
\(\epsilon\in\{1,-1\}\). Up to choosing left or right multiplication, its
quotient shadow is

\[
B_1
=
B\,uD^\epsilon u^{-1}
\quad\text{or}\quad
uD^\epsilon u^{-1}B.
\tag{2.1}
\]

Next use \(B_1^\eta\), \(\eta\in\{1,-1\}\), as the source of a
multiplication targeting the \(D\)-slot:

\[
D_1
=
D\,vB_1^\eta v^{-1}
\quad\text{or}\quad
vB_1^\eta v^{-1}D.
\tag{2.2}
\]

Suppose this second target is the final generator isolator. After a final
orientation and conjugation, write

\[
I
=
aD_1^\delta a^{-1}
=
z^{-1}e,
\qquad
\delta\in\{1,-1\},
\qquad
e\in F(x,t).
\tag{2.3}
\]

The conjugators \(u,v,a\) are arbitrary elements of \(H\). Equations
(2.1)--(2.3) also represent arbitrary free-group spellings before
projection, because every \(R\)-gauge difference vanishes in \(H\).

## 3. Quotient by the original \(D\)

The useful quotient is not the relative one-relator group obtained by
killing the modified survivor \(B_1\). Instead, kill the original
\(D\)-shadow:

\[
K_D
=
H/\langle\!\langle D\rangle\!\rangle
\cong
\langle G,z\mid zxz^{-1}=t\rangle.
\tag{3.1}
\]

This is the HNN extension from the one-way theorem. Britton's lemma embeds
\(G\), and its length-one Collins conjugacy classification is already
proved there.

In \(K_D\), the first cross event disappears:

\[
B_1=B.
\tag{3.2}
\]

The original \(D\)-factor in (2.2) also disappears, so \(D_1\) is conjugate
to \(B^\eta\). Consequently \(I\) is conjugate to

\[
B^{\eta\delta}.
\tag{3.3}
\]

The stable-letter exponents are

\[
\sigma_z(I)=-1,
\qquad
\sigma_z(B^{\eta\delta})=-\eta\delta.
\tag{3.4}
\]

Conjugacy preserves this exponent, hence

\[
\boxed{\delta=\eta.}
\tag{3.5}
\]

Thus \(I=z^{-1}e\) is conjugate to \(B=z^{-1}p\) in \(K_D\). The complete
HNN classification gives

\[
\boxed{
[e]_G=e_n:=t^{-n}px^n
}
\tag{3.6}
\]

for some \(n\in\mathbb Z\).

This quotient is the key feedback simplification: it erases the first
cross even though the modified first target is used as the second source.

## 4. Weight fixes the HNN parameter

Extend the torus-knot weight to \(H\) by

\[
\operatorname{wt}(x)=4,\qquad
\operatorname{wt}(t)=3,\qquad
\operatorname{wt}(z)=0.
\tag{4.1}
\]

Then

\[
\operatorname{wt}(B)=7,
\qquad
\operatorname{wt}(D)=1,
\qquad
\operatorname{wt}(R)=0.
\tag{4.2}
\]

Conjugation, multiplication side, and fixed-\(R\) gauges do not affect
weight. Equations (2.1)--(2.2) give

\[
\operatorname{wt}(B_1)=7+\epsilon,
\tag{4.3}
\]

and

\[
\operatorname{wt}(D_1)
=
1+\eta(7+\epsilon).
\tag{4.4}
\]

Using \(\delta=\eta\),

\[
\operatorname{wt}(e)
=
\operatorname{wt}(I)
=
\delta\operatorname{wt}(D_1)
=
7+\epsilon+\eta.
\tag{4.5}
\]

But

\[
\operatorname{wt}(e_n)=7+n.
\tag{4.6}
\]

Equality in \(G\) preserves weight, so

\[
\boxed{n=\epsilon+\eta.}
\tag{4.7}
\]

There is no unbounded residue left: the four sign pairs force
\(n\in\{-2,0,2\}\).

## 5. Evaluation identifies the actual survivor

Use \(I=z^{-1}e\) in the stable substitution-and-removal composite. Let

\[
C=B_1[z\mapsto e],
\qquad
Q=D[z\mapsto e]
=t^{-1}exe^{-1}.
\tag{5.1}
\]

Since \(I\) is a conjugate or inverse of \(D_1\),

\[
D_1[z\mapsto e]=1.
\tag{5.2}
\]

If the second multiplication in (2.2) is on the right, (5.2) is

\[
Q\,v_eC^\eta v_e^{-1}=1.
\tag{5.3}
\]

If it is on the left, it is

\[
v_eC^\eta v_e^{-1}Q=1.
\tag{5.4}
\]

Here \(v_e\in G\) is the evaluated conjugator. Either equation gives

\[
\boxed{
[C]_G
\ \text{is conjugate to}\
[Q]_G^{-\eta}.
}
\tag{5.5}
\]

Equation (3.6) gives

\[
[Q]_G
=
\left[t^{-1}e_nxe_n^{-1}\right]_G.
\tag{5.6}
\]

The exact identity from the one-way theorem is

\[
t^{-1}e_nxe_n^{-1}
=
t^{-n}D_pt^n,
\qquad
D_p=t^{-1}pxp^{-1}.
\tag{5.7}
\]

Thus \([C]_G\) is a conjugate of \(D_p^{-\eta}\). Choose a literal
free-group representative \(V\) of that conjugate. Then

\[
C^{-1}V\in\langle\!\langle R\rangle\!\rangle.
\tag{5.8}
\]

The fixed-relator normal-closure lemma replaces \(C\) by \(V\) through
classical AC1--AC3 moves. AC3 removes the conjugator and AC1 removes the
sign. Therefore

\[
\boxed{
(R,C)
\sim_{\mathrm{AC1-3}}
(R,D_p)
\sim_{\mathrm{AC3}}
\operatorname{AK}(3).
}
\tag{5.9}
\]

If the surviving \(B_1\)-slot undergoes later fixed-\(R\) gauges,
conjugation, or inversion, require its final quotient shadow to be restored
in the signed-conjugate orbit of \(B_1\). Evaluation then changes (5.5)
only by equality in \(G\), conjugation, or inversion, and the same proof
applies.

## 6. The four coupled sign rows

Equations (3.5), (4.7), and (5.5) give the complete table:

| \((\epsilon,\eta)\) | \(\delta\) | tail | survivor class |
|---|---:|---|---|
| \((+,+)\) | \(+1\) | \(e_2=t^{-2}px^2\) | conjugate of \(D_p^{-1}\) |
| \((+,-)\) | \(-1\) | \(e_0=p\) | conjugate of \(D_p\) |
| \((-,+)\) | \(+1\) | \(e_0=p\) | conjugate of \(D_p^{-1}\) |
| \((-,-)\) | \(-1\) | \(e_{-2}=t^2px^{-2}\) | conjugate of \(D_p\) |

\[
\tag{6.1}
\]

The exact aligned seams realize all four rows. The replay checks their
tails, evaluated survivors, endpoint conjugacies, and a nontrivial
\(R\)-gauge on the actual tail.

## 7. Every other alternating branch

### 7.1 Eliminate the first target \(B_1\)

In the order (2.1)--(2.2), suppose \(B_1\), the source of the second event,
is the final one-\(z\) isolator instead. Evaluation kills the entire
second-event factor in \(D_1\), leaving the baseline
\(D[z\mapsto e]\) up to the restoration gauges.

The first event is precisely one-way passive-\(D\) traffic targeting
\(B_1\). The one-way theorem returns the endpoint to AK(3).

### 7.2 Reverse the alternating order

First target \(D\) by a conjugate of \(B^\epsilon\), producing \(D_1\).
Then use \(D_1^\eta\) to target \(B\), producing \(B_2\). Their
stable-letter exponents are

\[
\sigma_z(D_1)=-\epsilon
\tag{7.1}
\]

and

\[
\sigma_z(B_2)
=
-1-\epsilon\eta
\in\{0,-2\}.
\tag{7.2}
\]

Whole-target inversion only changes the sign. Therefore the second target
\(B_2\) cannot normalize to a one-\(z\) isolator.

If the first target \(D_1\), now the source of the second event, is the
final isolator, evaluation kills its contribution to \(B_2\). The first
event is one-way passive-\(B\) traffic targeting \(D_1\), already closed by
the one-way theorem.

These cases exhaust both alternating target orders and both choices of
the eliminated slot.

## 8. Combined conclusion and scope

Same-target two-cross histories are closed by the one-way theorem.
Sections 2--7 close all alternating-target histories. Hence every
exactly-two-cross fixed-\(R\) route with a final one-\(z\) generator
isolator returns classically to AK(3), provided:

1. every cross source spelling has the quotient shadow specified by the
   two-event grammar after fixed-\(R\) gauges and AC1/AC3 normalization;
2. a surviving slot is restored to the signed-conjugate orbit of the
   spelling whose evaluation is used in the proof;
3. an eliminated source preserves the required quotient normal closure;
   and
4. all other changes are fixed-\(R\) gauges, conjugations, or inversions.

The stable deletion is the substitution-and-removal composite on the
rank-three trivial-group presentation, not a bare AC5 move. The resulting
rank-two equivalence (5.9) is classical.

The theorem does not cover three or more alternating cross events, a
source outside the required quotient shadow or normal closure, a changed
retained relator, a multi-\(z\) primitive eliminator, another
stabilization, or dual-source primitive-pair compression.

AK(3) remains open.
