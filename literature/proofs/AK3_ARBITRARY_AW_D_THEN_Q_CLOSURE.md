# Arbitrary A--W products close under D-then-Q deletion

Date: 2026-07-26

Status: **PROVEN** for an arbitrary relative conjugator, both A--W
target directions, both source signs, and the fixed order which
deletes unchanged D and then the mixed Q-row.

At any of the six nonprimitive D-tail checkpoints, perform

\[
T\longmapsto TuS^\sigma u^{-1},
\qquad
\{T,S\}=\{A,W\},
\quad
u\in F(x,t,z,q),
\quad
\sigma=\pm1.
\tag{0.1}
\]

Delete D first. Whenever the unchanged Q-image is primitive, delete
it next. Then

\[
\boxed{
\text{every endpoint lies stably in Result 47's floor-23 corridor.}
}
\tag{0.2}
\]

There is no length or alphabet restriction on u. This is a closure of
one deletion order, not a classification of all survivors after the
first deletion.

## 1. The unchanged mixed Q-row

Use the checkpoint words

\[
\begin{aligned}
A&=qx^3q^{-1}t^{-4},\\
W&=Az^{-1}C,\qquad C=qxq^{-1}tq,\\
D&=t^{-1}zxz^{-1},\\
Q_{\eta,\epsilon,\delta}
&=q^\eta W^\epsilon D^\delta.
\end{aligned}
\tag{1.1}
\]

The edge (0.1) changes only its target row. It changes neither D nor
the separately retained Q-word.

Let \(\rho\) be the fixed D-deletion quotient: apply

\[
x\longmapsto z^{-1}txz,
\qquad
t,z,q\text{ fixed},
\tag{1.2}
\]

which sends D to x, and then set \(x=1\). Since D and Q are untouched
by (0.1),

\[
\rho(Q_{\eta,\epsilon,\delta})
\tag{1.3}
\]

is literally its baseline image for every u, \(\sigma\), and target
direction.

Result 51's complete rank-three classification therefore applies
without any relative-conjugator census. Exactly

\[
(\eta,\epsilon)=(-1,+1),
\qquad
\delta=\pm1,
\tag{1.4}
\]

gives a primitive Q-image. Structurally, after D is killed,
\(q^{-1}W D^\delta\) is conjugate to

\[
S=Wq^{-1},
\tag{1.5}
\]

and Result 47 proves \((S,D)\) is a based primitive pair.

## 2. A fixed double quotient

For each \(\delta=\pm1\), write

\[
Q_{-1,+1,\delta}
=q^{-1}SqD^\delta.
\tag{2.1}
\]

The two normal closures agree:

\[
\langle\!\langle D,Q_{-1,+1,\delta}\rangle\!\rangle
=
\langle\!\langle D,S\rangle\!\rangle.
\tag{2.2}
\]

Indeed, the forward inclusion follows from (2.1), while

\[
qQ_{-1,+1,\delta}D^{-\delta}q^{-1}=S
\tag{2.3}
\]

gives the reverse inclusion.

Now use Result 47's fixed based-pair straightener for \((S,D)\) and
delete its two basis coordinates. By (2.2), this homomorphism factors
through exactly the quotient obtained by sequentially deleting D and
the mixed Q-image. It gives a fixed map

\[
\pi_\delta:F(x,t,z,q)\longrightarrow F_2
\tag{2.4}
\]

satisfying

\[
\pi_\delta(D)=\pi_\delta(Q)=1,
\qquad
\pi_\delta(A)=a,
\qquad
\pi_\delta(W)=w,
\tag{2.5}
\]

where

\[
\begin{aligned}
a&=\texttt{xYxYxYXyXyXyXy},\\
w&=\texttt{yXyXyXyxYYxxYxYxYXyXyXyXy}.
\end{aligned}
\tag{2.6}
\]

Both \(\delta\)-signs give the same literal pair (2.6). Result 47's
fixed rank-two ambient coordinate followed by independent relator
conjugation/inversion displays its Aut-orbit as

\[
\begin{aligned}
r&=\texttt{YXXXXyxxx},\\
s&=\texttt{YYXXXXyxxxYxyx},
\end{aligned}
\tag{2.7}
\]

with complete floor 23. The choice \(\pi_\delta\) is fixed before u
is chosen.

## 3. Both target directions

Put

\[
c=\pi_\delta(u).
\tag{3.1}
\]

If A is targeted, homomorphism naturality gives the exact endpoint

\[
\left(
a c w^\sigma c^{-1},
w
\right).
\tag{3.2}
\]

If W is targeted, it gives

\[
\left(
a,
w c a^\sigma c^{-1}
\right).
\tag{3.3}
\]

Each pair is classically AC-equivalent to \((a,w)\). Invert the
retained source if \(\sigma=-1\), conjugate it by c, multiply it into
the target, and undo the source conjugation and inversion. This is a
finite sequence of relator inversions, conjugations, and
multiplications; it places no bound on the word c.

The full rank-four route is nevertheless **stable**: it uses ambient
straighteners and two generator-relator deletions. Outputs obtained
from other straighteners are Aut\((F_2)\)-equivalent to the fixed
representatives (3.2)--(3.3), so they are stably in the same corridor.
The ambient coordinate carrying (2.6) to the floor-23 display (2.7)
is also a stable coordinate operation, so no classical identification
between the raw pair (2.6) and (2.7) is claimed.

## 4. Conclusion and boundary

Equations (1.3) and (3.2)--(3.3) prove (0.2) for arbitrary u in the
full rank-four free group.

The theorem does not classify:

- a changed A- or W-row which becomes primitive after D deletion;
- a primitive pair involving that changed carrier and Q;
- nonmixed Q-sign rows, whose unchanged Q-image is nonprimitive;
- intervening row traffic before either deletion;
- arbitrary z-dependent changed-row-first A--W deletion;
- another carrier pair.

In the A-target direction, deleting the unchanged W-source first is
already Result 51's arbitrary-conjugator quotient gauge. In the
W-target direction, the unchanged A-source is nonprimitive.

AK(3), AC, and stable AC remain open.

## 5. Independent replay

The dependency-free verifier
`tests/stable_ac/test_qw_d_tail_compression_merge.py`:

- reuses Result 47's exact based-pair automorphism and inverse;
- constructs the fixed double quotient at both \(\delta\)-signs;
- checks (3.2)--(3.3) on mixed, cancellation-heavy rank-four
  conjugators and both source signs;
- verifies both \(\delta\)-quotients have the same floor-23 baseline.

The arbitrary-u conclusion is homomorphism naturality in Section 3;
the finite replay exercises the exact quotient implementation.
