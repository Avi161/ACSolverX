# AK(3) z-free A--W conjugator design

Date: 2026-07-26

## Objective

Extend Result 50's finite signed-cyclic A--W census along an unbounded
family: one changed-row-first A--W multiplication whose normalized
relative conjugator lies in \(H=F(x,t,q)\).

## Structural normal form

Write

\[
W=Az^{-1}C,\qquad
V=uA^\sigma u^{-1},\qquad u\in H.
\]

After target inversion, cyclic target conjugation, and reversing the
multiplication side by cyclic reordering, every W-target product has
the form

\[
P=WV=Az^{-1}CV.
\]

For a W-target product, the changed row has exactly one z-letter,
hence is primitive. The coordinate

\[
z\longmapsto CVz^{-1}A
\]

sends P to z.

An A-target product is not the same literal word. Put
\(v=u^{-1}\) and \(V=vA^\sigma v^{-1}\). Its two straighteners are

\[
\begin{aligned}
\sigma=+1:\quad&z\longmapsto Cvz^{-1}Av^{-1}A,\\
\sigma=-1:\quad&z\longmapsto CvA^{-1}zv^{-1}A.
\end{aligned}
\]

Only after deletion do the two directions share the substitution
shadow \(K=CVA\), giving

\[
D_V=t^{-1}(CVA)x(CVA)^{-1},\qquad
Q_V=q^\eta V^{-\epsilon}D_V^\delta.
\]

The surviving source is A in the W-target direction and a conjugate
of \(A^{\pm1}\) in the A-target direction.

## Collapse

Because \(V\in\langle\!\langle A\rangle\!\rangle\), the fixed-source
normal-closure lemma gives

\[
(A,D_V,Q_V)
\sim_{\rm AC}
(A,D_0,q^\eta D_0^\delta),
\qquad
D_0=t^{-1}CxC^{-1}.
\]

The D0-row reduces the last row classically to q. Stable deletion of
q leaves

\[
(R,E)=(x^3t^{-4},\,t^{-1}(xt)x(xt)^{-1}),
\]

the known floor-13 AK(3) orbit.

## Scope

The theorem is unbounded in u but requires u to be z-free in the
chosen normalized product. It covers both target directions, both
source signs, both multiplication sides, and all six D-tail
checkpoints, followed immediately by deletion of the changed row.
It does not cover z-dependent relative conjugators, non-source-first
orders, or later row changes.

The whole branch is a stable self-loop. Only the fixed-source
rank-three collapse and the final rank-two identification are
classical.
