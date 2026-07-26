# AK(3) minimum-tail binary coset design

Date: 2026-07-25

## Objective

Strengthen the \(S_4\) Fox sieve for the repositioned minimum-tail
candidate and replace ad hoc subgroup comparisons by an exact folded
coset core.

## Folded-core layer

Fold the projected \(K,H_0\) loops in \(C_3*C_4\). The resulting
nine-edge, eight-vertex core has rank two and recognizes
\(\pi(P)\). Its two fundamental chains recover the exponent sums in
\((K,H_0)\). Combining those sums with torus weight decides membership
in \(P<G\), including the central lift.

## Binary quotient layer

Use

\[
x\mapsto
\begin{pmatrix}0&1\\2&1\end{pmatrix},
\qquad
t\mapsto
\begin{pmatrix}0&1\\1&1\end{pmatrix}
\]

over \(\mathbb F_3\). Both defining powers equal \(-I\), so this retains
the central sign lost by the projective \(S_4\) quotient.

For \(\ell=(1,2)\), the image of \(P\) is the point stabilizer of
\(\ell\), while

\[
\ell\rho(A_U)=0,
\qquad
\ell\rho(A_0)=\ell.
\]

Fox solvability therefore forces

\[
\rho(g)\in(-I)\rho(P).
\]

This excludes \(g=1\) and \(g=\gamma e^{-1}\), but \(g=c^{-1}\)
survives.

## Scope

- Exact at the Fox level.
- No AC graph search.
- A surviving finite target means nonliftability is not proved.
- The integral coset-module and nonabelian kernel equations remain open.
- AK(3) remains open.
