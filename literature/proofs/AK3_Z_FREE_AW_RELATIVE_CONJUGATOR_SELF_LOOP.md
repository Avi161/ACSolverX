# Unbounded z-free A--W relative-conjugator self-loop

Date: 2026-07-26

Status: **PROVEN** for both ordered A--W target directions, both
source signs, both multiplication sides, and all six D-tail
checkpoints, under the normalized z-free-conjugator hypothesis.

Let \(H=F(x,t,q)\). At a nonprimitive D-tail checkpoint, perform one
relative multiplication between A and W whose normalized conjugator
is an arbitrary \(u\in H\), then delete the changed row first.
There is no length bound on u.

The changed row is a one-z coordinate. Its deletion leaves a shadow
\(V\) lying in the normal closure of A, so a fixed-source classical
AC argument erases V before a second stable deletion. The final pair
is the known floor-13 AK(3) pair:

\[
\boxed{
\text{every normalized z-free A--W changed-row-first branch is a
stable self-loop.}
}
\tag{0.1}
\]

This is a strict infinite enlargement beyond the finite cyclic census,
not a proof of AC or stable AC.

## 1. Checkpoint and exact scope

Put

\[
\begin{aligned}
A&=qx^3q^{-1}t^{-4},\\
C&=qxq^{-1}tq,\\
W&=Az^{-1}C,\\
D&=t^{-1}zxz^{-1},\\
Q_{\eta,\epsilon,\delta}
&=q^\eta W^\epsilon D^\delta,
\end{aligned}
\tag{1.1}
\]

where

\[
(\eta,\epsilon)\in\{(+,+),(-,+),(-,-)\},
\qquad
\delta\in\{+1,-1\}.
\tag{1.2}
\]

For arbitrary \(u\in H\) and \(\sigma\in\{+1,-1\}\), the two literal
normalized products are

\[
\begin{aligned}
P_W&=WuA^\sigma u^{-1}
&&\text{(W targeted)},\\
P_A&=AuW^\sigma u^{-1}
&&\text{(A targeted)}.
\end{aligned}
\tag{1.3}
\]

Target inversion is redundant: invert the changed row and cyclically
reorder it, which flips the source sign in (1.3). Left multiplication
is likewise a cyclic reordering of the right product. Arbitrary
conjugation of the whole changed row is harmless. Thus (1.3) covers
both target orientations and both multiplication sides.

The hypothesis is that u is z-free in the chosen normal form (1.3).
It is not a claim about every re-expression using arbitrary signed
cyclic representatives: moving a z-containing prefix of W into u can
leave \(H\).

## 2. W targeted: one-z deletion

Write

\[
V=uA^\sigma u^{-1}\in H,
\qquad
P_W=WV=Az^{-1}CV.
\tag{2.1}
\]

The freely reduced cyclic word for \(P_W\) has exactly one
\(z^{\pm1}\). Any word \(Lz^\tau R\), with L and R z-free and
\(\tau=\pm1\), is primitive: fixing H and sending z to that word is
an automorphism, with the elementary inverse obtained by solving for
z. Hence \(P_W\) is primitive.

For the full-tuple transport, use the explicit coordinate

\[
\Theta_V:
\qquad
z\longmapsto CVz^{-1}A,
\qquad
x,t,q\text{ fixed}.
\tag{2.2}
\]

This is an automorphism of \(H*\langle z\rangle\), and direct
substitution gives

\[
\Theta_V(P_W)=z.
\tag{2.3}
\]

Delete the resulting generator-relator pair. Equivalently, solve
\(P_W=1\):

\[
z=CVA.
\tag{2.4}
\]

Put

\[
K_V=CVA,
\qquad
D_V=t^{-1}K_VxK_V^{-1}.
\tag{2.5}
\]

The old W-word and Q-row descend exactly as

\[
W\longmapsto V^{-1},
\qquad
Q_{\eta,\epsilon,\delta}
\longmapsto
Q_V=q^\eta V^{-\epsilon}D_V^\delta.
\tag{2.6}
\]

Because W was the changed row, the surviving labeled tuple is

\[
(A,D_V,Q_V).
\tag{2.7}
\]

Equations (2.2)--(2.7) hold for an arbitrary-length u.

## 3. A targeted: the reverse direction is literal

The reverse target direction needs \(u\mapsto u^{-1}\); it is not
silently identified with Section 2. Put

\[
v=u^{-1},
\qquad
V=vA^\sigma v^{-1},
\qquad
B=V^{-1}=vA^{-\sigma}v^{-1}.
\tag{3.1}
\]

For \(\sigma=+1\), define

\[
\Theta_+(z)=Cvz^{-1}Av^{-1}A.
\tag{3.2}
\]

For \(\sigma=-1\), define

\[
\Theta_-(z)=CvA^{-1}zv^{-1}A.
\tag{3.3}
\]

Both coordinates fix H. Literal free reduction gives

\[
\Theta_\sigma(P_A)=z.
\tag{3.4}
\]

After \(z=1\), both signs have the same form

\[
K_V=CVA,
\qquad
D\longmapsto D_V=t^{-1}K_VxK_V^{-1},
\tag{3.5}
\]

while

\[
W\longmapsto B=V^{-1},
\qquad
Q_{\eta,\epsilon,\delta}
\longmapsto
q^\eta B^\epsilon D_V^\delta
=q^\eta V^{-\epsilon}D_V^\delta.
\tag{3.6}
\]

Thus the surviving tuple is

\[
(B,D_V,Q_V).
\tag{3.7}
\]

If \(\sigma=+1\), invert B; in either sign, conjugate the first
relator by \(v^{-1}\). This changes B to the literal A and leaves the
other two relator words untouched. Therefore (3.7) has exactly the
same normal-closure reduction problem as (2.7).

This proves both ordered directions without invoking an unproved
target symmetry.

## 4. The arbitrary shadow is a classical gauge

Set

\[
D_0=t^{-1}CxC^{-1}.
\tag{4.1}
\]

Since V is a conjugate of \(A^{\pm1}\),

\[
V\in\langle\!\langle A\rangle\!\rangle.
\tag{4.2}
\]

In \(H/\langle\!\langle A\rangle\!\rangle\), both V and A vanish, so

\[
K_V=CVA=C,
\qquad
D_V=D_0,
\qquad
Q_V=q^\eta D_0^\delta.
\tag{4.3}
\]

The fixed-relator normal-closure lemma says that, with A held fixed,
any other relator may be replaced by a quotient-equal word through a
finite sequence of relator inversions, conjugations, and
multiplications, restoring A after every normal-closure factor.
Apply it independently to the last two rows:

\[
\boxed{
(A,D_V,Q_V)
\sim_{\rm AC}
(A,D_0,q^\eta D_0^\delta).
}
\tag{4.4}
\]

This is the unbounded step. Its existence follows from (4.2); it
places no uniform bound on the normal-closure factorization or on u.

The D0-row now reduces the last relator to q while restoring D0. If
\(\eta=+1\), right-multiply \(qD_0^\delta\) by
\(D_0^{-\delta}\). If \(\eta=-1\), invert the row, conjugate it by
\(D_0^\delta\), and right-multiply by \(D_0^\delta\). Hence

\[
(A,D_0,q^\eta D_0^\delta)
\sim_{\rm AC}
(A,D_0,q).
\tag{4.5}
\]

No ambient automorphism or stabilization is hidden in
(4.4)--(4.5).

## 5. The second stable deletion returns to AK(3)

Delete the primitive q generator-relator pair in (4.5). Substitution
\(q=1\) gives

\[
\begin{aligned}
A&\longmapsto R=x^3t^{-4},\\
C&\longmapsto xt,\\
D_0&\longmapsto
E=t^{-1}(xt)x(xt)^{-1}.
\end{aligned}
\tag{5.1}
\]

Therefore the final pair is

\[
(R,E)
=
(\texttt{xxxTTTT},\texttt{TxtxTX}).
\tag{5.2}
\]

If

\[
B_0=xtxt^{-1}x^{-1}t^{-1}
\tag{5.3}
\]

is the standard AK(3) braid relator, then

\[
E=t^{-1}B_0t.
\tag{5.4}
\]

Thus (5.2) is classically AC-equivalent to the standard AK(3) pair
and has independently certified Aut-floor 13.

The full route is a **stable** self-loop: (2.2) or
(3.2)--(3.3) is applied to the full tuple before primitive deletion,
and q is later deleted as a generator-relator pair. Only the
rank-three gauge (4.4)--(4.5) and the final identification (5.4) are
classical.

## 6. This is genuinely unbounded

Take

\[
u=q^n,\qquad
P_n=Wq^nAq^{-n}.
\tag{6.1}
\]

For \(n\ge1\), the freely reduced word has length \(24+2n\).
Its first q cancels cyclically with the final \(q^{-1}\), and no
second cyclic cancellation is possible, so

\[
|P_n|_{\rm cyclic}=22+2n.
\tag{6.2}
\]

These cyclic lengths are pairwise distinct. For \(n\ge2\) they exceed
24, the maximum length of a product of signed cyclic representatives
of A and W. Hence the theorem contains infinitely many primitive
children outside Result 50's finite signed-cyclic image.

## 7. Boundary

The proof requires:

- one A--W relative multiplication in a normal form (1.3) with
  \(u\in F(x,t,q)\);
- immediate changed-row-first primitive deletion;
- one of the six fixed D-tail checkpoints (1.2).

If u contains z, the changed row can contain several z-letters and
need not be primitive; equations (2.2)--(2.4) no longer follow. This
is a real obstruction, not merely a gap in the proof. For example,
take \(\sigma=+1\) and \(u=xz\). The W-target child is

```text
qxxxQTTTTZqxQtqxzqxxxQTTTTZX
```

Complete rank-four Whitehead descent has length chain

\[
28,23,21,20,19,18,17,15,14
\tag{7.1}
\]

and terminates at

```text
QXzQzXttttXXZT
```

whose Whitehead graph is connected and remains connected after every
single vertex deletion. The child is therefore nonprimitive.

Moving a z-containing prefix of a signed cyclic W-representative into
u is therefore outside the theorem. Also outside scope are
unchanged-row-first deletion, a later row change before deletion,
traffic that first changes A or W, and relative products involving D
or Q.

AK(3), AC, and stable AC remain open.

## 8. Independent replay

The dependency-free verifier
`tests/stable_ac/test_d_tail_one_edge_primitive_creation.py`:

- checks both exact W-target and A-target straighteners;
- transports W, D, and all six Q-rows literally through deletion;
- verifies both source signs on cancellation-heavy z-free
  conjugators;
- checks that the A-target survivor is a conjugate of
  \(A^{\pm1}\);
- replays the q reduction and the exact pair (5.2);
- verifies (6.2) for a growing family outside the cyclic census;
- independently reduces the z-dependent counterexample (7.1) and
  verifies its cut-vertex obstruction.
