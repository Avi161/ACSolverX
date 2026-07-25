# AK(3) three-cross killer reduction design

Date: 2026-07-25

## Objective

Analyze every exactly-three alternating \(B/D\) cross history in the
fixed-\(R\), one-\(z\)-eliminator corridor. Prove everything that follows
from exponent, torus weight, and the already-established two-cross theorem;
then give a complete finite certificate for the untwisted seam subcorridor.

The result must not claim that AK(3) is solved. Its purpose is to identify
the first genuinely new equation which survives all previous self-loop
theorems.

## Setup

Work in

\[
H=G*\langle z\rangle,\qquad
G=\langle x,t\mid x^3=t^4\rangle,
\]

with

\[
B=z^{-1}xt,\qquad D=t^{-1}zxz^{-1}.
\]

A cross event multiplies one current slot on either side by an arbitrary
conjugate of a signed current spelling of the other slot. Whole-slot
inversions, conjugations, and fixed-\(R\) gauges are absorbed into signs
and conjugators. The final eliminator must normalize to \(z^{-1}e\).

## Competing approaches

### A. Classify every weight-one normal generator as a meridian

Reject this approach. Silver--Whitten--Williams,
*Knot Groups with Many Killers*, Theorem 1.2 and Corollary 1.3
([arXiv:0909.3275](https://arxiv.org/abs/0909.3275)), proves that every
nontrivial torus-knot group has infinitely many inequivalent
pseudo-meridians. Normal generation and abelianization weight therefore
cannot identify the endpoint up to conjugacy or automorphism.

### B. Arithmetic reduction plus exact untwisted seam certificate

Use stable-letter exponent to close one alternating order completely and
reduce the other order from eight sign triples to six. Use torus weight to
pin the final tail weight and evaluated survivor weight for all six rows.
Then enumerate every signed cyclic rotation at each of the three
untwisted seams. This is finite because \(B,D\) are fixed and no relative
bridge or vertex-stabilizer twist is admitted.

This is the chosen approach. It produces a rigorous theorem and exposes
the precise remaining geometry without making a false global closure
claim.

### C. Bounded arbitrary-bridge census

Keep this as evidence only. A one-letter bridge in any single event
returned only the AK(3) endpoint in exploratory checks, but bounded bridge
failure is not a theorem about arbitrary conjugators. Do not include it in
the proved conclusion.

## The two alternating orders

For the order

\[
D\to B_1,\quad B_1\to D_1,\quad D_1\to B_2,
\]

the third target has stable-letter exponent

\[
\sigma_z(B_2)=-1-\eta\theta\in\{0,-2\}.
\]

It cannot be the final one-\(z\) eliminator. If \(D_1\), the source of the
third event, is eliminated instead, evaluation erases the third factor and
the existing two-cross theorem closes the endpoint.

For the reverse order

\[
B\to D_1,\quad D_1\to B_1,\quad B_1\to D_2,
\]

write the three source signs as
\(\epsilon,\eta,\theta\in\{\pm1\}\). Then

\[
\sigma_z(D_2)=-\epsilon-\theta-\epsilon\eta\theta.
\]

The all-positive and all-negative rows have absolute exponent \(3\) and
are impossible. The other six rows have absolute exponent \(1\), which
fixes the final orientation \(\delta=-\sigma_z(D_2)\).

With

\[
\operatorname{wt}(x)=4,\quad
\operatorname{wt}(t)=3,\quad
\operatorname{wt}(z)=0,
\]

the recurrence

\[
\begin{aligned}
\operatorname{wt}(D_1)&=1+7\epsilon,\\
\operatorname{wt}(B_1)&=7+\eta(1+7\epsilon),\\
\operatorname{wt}(D_2)&=1+7\epsilon+
  \theta\bigl(7+\eta(1+7\epsilon)\bigr)
\end{aligned}
\]

pins \(\operatorname{wt}(e)=\delta\operatorname{wt}(D_2)\).
After \(z=e\), the survivor \(C=B_1[e]\) has weight

\[
\operatorname{wt}(C)
=
\operatorname{wt}(B_1)+\sigma_z(B_1)\operatorname{wt}(e)
\in\{\pm1\}.
\]

Since the stable route leaves the trivial presentation \((R,C)\), \(C\)
normally generates \(G\): it is a torus-knot-group killer. This is a
reduction, not a meridian classification.

## Untwisted seam certificate

For a cyclically reduced free word \(W\), enumerate every cyclic rotation
of \(W\) and \(W^{-1}\). At each cross event, concatenate one signed
rotation of the target with one signed rotation of the source, freely and
cyclically reduce, and quotient the result by signed cyclic rotation.
Reversing multiplication order adds no case because \(uv\) and \(vu\)
are conjugate.

Starting from the reverse order above, the independent replay must pin:

- \(16\) first-target cyclic classes;
- \(416\) ordered intermediate \((D_1,B_1)\) class pairs;
- \(522\) final one-\(z\) triples;
- \(69\) final one-\(z\) target classes; and
- one evaluated survivor class, represented by
  `TXTxtx`, the signed cyclic class of
  \(D_p=t^{-1}(xt)x(xt)^{-1}\).

This certifies that every untwisted signed seam route returns classically
to AK(3). It does not cover a nonempty relative bridge, a nontrivial
vertex-stabilizer twist, or an \(R\)-gauge inserted as a literal
intermediate spelling.

## Deliverables

- `tests/stable_ac/test_three_cross_killer_reduction.py`
  independently replays the arithmetic table and finite seam certificate.
- `literature/proofs/AK3_THREE_CROSS_KILLER_REDUCTION.md`
  states and proves the scoped theorem.
- `results/stable_ac/theory/AK3_DIRECT_STABLE_THEORY.md`
  records the theorem and replaces the vague “at least three events” lead
  with the exact bridge/twist frontier.

## Verification and honesty constraints

- Dependency-free replay only; no AC graph search.
- No node-budget claim and no bounded negative promoted to a theorem.
- No unstable ambient automorphism principle.
- The stable deletion is the substitution-and-removal composite, not bare
  AC5.
- AK(3) remains open unless an independent stable trivialization
  certificate is actually produced.
