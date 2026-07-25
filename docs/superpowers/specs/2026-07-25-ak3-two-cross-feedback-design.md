# AK(3) alternating two-cross feedback design

Date: 2026-07-25

## Objective

Close the minimal cross-feedback history not covered by the one-way theorem:
one slot is targeted, then that modified slot is used as the source of a
cross event targeting the other slot.

The proof must cover arbitrary conjugators, either multiplication side,
both source signs, fixed-\(R\) gauges, and both choices of final
one-\(z\) eliminator under the established restoration hypotheses.

## Feasible alternating order

Start with

\[
B=z^{-1}xt,\qquad
D=t^{-1}zxz^{-1}.
\]

First target \(B\) by a conjugate of \(D^\epsilon\), obtaining \(B_1\).
Then target \(D\) by a conjugate of \(B_1^\eta\), obtaining \(D_1\).

If \(D_1\) normalizes, after a final orientation
\(\delta\in\{\pm1\}\), to \(z^{-1}e\), quotient by the original
\(D\)-normal closure. The first cross disappears:

\[
B_1=B,\qquad
D_1\sim B^\eta
\]

in

\[
K_D=\langle G,z\mid zxz^{-1}=t\rangle.
\]

Stable-letter exponent forces \(\delta=\eta\). The existing
Britton--Collins classification therefore gives

\[
[e]_G=e_n=t^{-n}(xt)x^n.
\]

Torus weight gives

\[
n=\epsilon+\eta.
\]

After evaluation at \(z=e\), let \(C=B_1[e]\) be the survivor and
\(Q=D[e]\). The relation \(D_1[e]=1\) forces

\[
C\sim Q^{-\eta}.
\]

Since \(Q\) is quotient-equal to
\(D(e_n)=t^{-n}D(xt)t^n\), the endpoint is classically AC-equivalent to
AK(3).

## Other branches

- If \(B_1\), the source of the second event, is eliminated, the second
  event vanishes after evaluation and the one-way \(D\to B\) theorem
  closes the endpoint.
- In the opposite order, first target \(D\) by \(B^\epsilon\), then target
  \(B\) by the modified \(D_1^\eta\). The second target has
  \(z\)-exponent \(-1-\epsilon\eta\in\{0,-2\}\), up to final inversion, so
  it cannot be a one-\(z\) isolator.
- If the first target \(D_1\) is instead eliminated in that order, its
  later source contribution vanishes and the one-way \(B\to D\) theorem
  closes the endpoint.

Thus every exactly-two-cross history with a final one-\(z\) eliminator is
closed under the same source-restoration conditions as the one-way theorem.

## Verification

The replay should pin:

- \(\delta=\eta\) from stable-letter exponent;
- \(n=\epsilon+\eta\) from weight;
- all four aligned feedback histories;
- the evaluated survivor relation \(C\sim D(e_n)^{-\eta}\);
- the four signed endpoint classes; and
- the opposite-order exponent obstruction.

Unbounded completeness comes from quotienting by the original \(D\), the
HNN classification, and the evaluation equation, not from the finite
replay.

## Scope

The theorem fixes \(R=x^3t^{-4}\) in normal closure and assumes the usual
restoration condition for whichever slot survives or is eliminated. It
does not cover three or more alternating cross events, a source spelling
outside the required normal closure, a multi-\(z\) primitive eliminator,
another stabilization, or dual-source compression.

AK(3) remains open.
