# Depth-six balanced (L_0) census after Result 157

## Status

This is an exact bounded census, not a theorem about all homogeneous
syzygies.  It records the first finite source depth at which the current
fifteen degree-two functionals have no surviving balanced two-source
(L_0) direction.

## Census

Enumerate every reduced quotient word through length six.  There are 127
source vertices.  For each unordered pair with opposite orbit-boundary
signature, choose the coefficient in ({1,-1}) which balances both finite
orbits.  This gives 4,671 balanced source pairs.

For every pair, the complete four-sheet Stallings cover rewrites the six
boundary pairs into exact forest paths.  Their signed edge flow gives a
homogeneous vector (d) satisfying

\[
\sum_{i=0}^4L_i d_i=0.
\]

Projecting the corresponding degree-two residual through the fifteen
Result 157 functionals gives no zero syndrome among all 4,671 pairs.

Fourteen projected finite-action bits leave exactly two near-survivors:

\[
e_{TT}+e_{TTTct},
\qquad
e_{Tctt}+e_{Tctct}.
\]

For both, the remaining full wedge-sum functional is

\[
\Phi_\infty=1\pmod2.
\]

Thus neither is a twelfth direction.

## Consequence and next step

Results 153--157 found new directions successively inside this same
balanced (L_0) family.  The complete depth-six failure is therefore a
meaningful change in the frontier, but it is bounded evidence only.

The next exact tasks are:

1. promote the complete Stallings-cover path rewrite and orbit-signature
   classifier from research scratch into a stable certificate module;
2. prove a finite-state recursion for the fifteen-bit syndrome under source
   word extension; or
3. scan depth seven only after the recursion state and reproducible checker
   are pinned.

No claim is made for depth seven or for arbitrary balanced source flows.
