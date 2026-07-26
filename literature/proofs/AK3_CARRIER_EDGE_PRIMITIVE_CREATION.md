# Cyclic carrier-edge primitive creation at the D-tail checkpoints

Date: 2026-07-26

Status: **PROVEN** for the stated signed-cyclic, changed-row-first
stratum.

At each of the six nonprimitive D-tail checkpoints

\[
(A,W,D,Q_{\eta,\epsilon,\delta}),
\qquad
Q_{\eta,\epsilon,\delta}
=q^\eta W^\epsilon D^\delta,
\tag{0.1}
\]

where

\[
(\eta,\epsilon)\in\{(+,+),(-,+),(-,-)\},
\qquad
\delta\in\{+1,-1\},
\]

take one relator multiplication between signed cyclic representatives
of two carriers in \(\{A,W,D\}\), in either target direction.

Every A--W child is primitive, while the A--D image has no primitive
child and the W--D image has four. Nevertheless:

\[
\boxed{
\begin{gathered}
\text{no changed child forms a direct primitive pair;}\\
\text{only 12 of 2,280 primitive-child states admit}\\
\text{a changed-row-first second primitive-single deletion;}\\
\text{all 12 are stable self-loops to AK(3) at floor 13.}
\end{gathered}
}
\tag{0.2}
\]

Thus no new endpoint, and no endpoint of Aut-floor at most 12, occurs
in this finite carrier-edge stratum.

## 1. Notation and exact image

At the checkpoint,

\[
\begin{aligned}
A&=qx^3q^{-1}t^{-4},\\
C&=qxq^{-1}tq,\\
W&=Az^{-1}C,\\
D&=t^{-1}zxz^{-1}.
\end{aligned}
\tag{1.1}
\]

Uppercase letters in machine words denote inverses.

For target T and retained source S, enumerate

\[
\operatorname{can}(T_iS_j^\sigma),
\qquad
0\le i<|T|,
\quad
0\le j<|S|,
\quad
\sigma\in\{+1,-1\}.
\tag{1.2}
\]

As in Result 49, target inversion is redundant after final inversion
and cyclic rotation. Formula (1.2) is the exact signed-cyclic image,
not the image with an arbitrary relative conjugator.

Across the three unordered carrier pairs, both target directions, and
six labeled Q-checkpoints, (1.2) gives

\[
\begin{array}{c|c|c}
&\text{target inversion quotiented}&
\text{fully oriented}\\
\hline
\text{literal realizations}&5{,}544&11{,}088.
\end{array}
\tag{1.3}
\]

There are 4,104 checkpoint-direction-child states and 342 global
changed conjugacy classes:

\[
\begin{array}{c|c}
\text{carrier pair}&\text{global child classes}\\
\hline
A\text{--}W&186\\
A\text{--}D&58\\
W\text{--}D&98.
\end{array}
\tag{1.4}
\]

The child class is independent of Q, but the labeled endpoint is not,
so all six checkpoints remain separate during transport.

## 2. Primitive children

### 2.1. The A--W family is symbolically primitive

A is z-free and every signed cyclic representative of W contains
exactly one \(z^{\pm1}\). Multiplication by a signed cyclic
representative of A cannot remove that letter. Hence every one of the
186 A--W child classes has the form

\[
Lz^\tau R,
\qquad
\tau\in\{+1,-1\},
\qquad
L,R\in F(x,t,q),
\tag{2.1}
\]

with exactly one z-letter.

The coordinate fixing \(x,t,q\) and sending z to (2.1) is an
automorphism. Its inverse sends

\[
z\longmapsto
\begin{cases}
L^{-1}zR^{-1},&\tau=+1,\\
Rz^{-1}L,&\tau=-1.
\end{cases}
\tag{2.2}
\]

Thus all 186 classes are primitive without a Whitehead search. At six
checkpoints and in two target directions they give 2,232 primitive
changed-row states.

### 2.2. The A--D and W--D images

The Whitehead-graph cut-vertex gate followed by complete strict descent
under all 504 second-kind maps of \(F_4\) gives

\[
\begin{array}{c|c|c|l}
\text{family}&\text{children}&\text{primitive children}&
\text{minimum-length distribution}\\
\hline
A\text{--}D&58&0&9^{(11)},11^{(11)},13^{(36)}\\
W\text{--}D&98&4&
1^{(4)},13^{(3)},14^{(7)},15^{(14)},16^{(28)},
17^{(18)},18^{(24)}.
\end{array}
\tag{2.3}
\]

The four W--D classes are

```text
QQTqXQTzxttttqXXX
QQTqXQtzXttttqXXX
QTTTTZqxQtqXZtzqxxx
QTTTTZqxQtqxZTzqxxx
```

Their strict descent length chains are

\[
\begin{array}{c|l}
\text{first W--D word}&
17,14,13,12,11,10,9,8,7,5,4,3,2,1\\
\text{second W--D word}&
17,14,13,11,10,8,7,6,5,4,3,2,1\\
\text{third W--D word}&
19,15,14,13,12,11,9,7,6,5,4,2,1\\
\text{fourth W--D word}&
19,15,14,13,11,10,8,7,6,5,4,3,2,1.
\end{array}
\tag{2.4}
\]

They occur at every checkpoint in both target directions, giving 48
more primitive states. Equations (2.1)--(2.3) therefore account for
all 2,280 primitive-child states.

## 3. No direct primitive pair

The unchanged A-row is nonprimitive. Result 48 proves every unchanged
Q-row in (0.1) nonprimitive. Neither can be a component of a primitive
pair.

The possible pair of two unchanged carriers is also never primitive:
when A, W, or D is changed, the surviving carrier-pair minimum is,
respectively,

\[
\mu(W,D)=16,
\qquad
\mu(A,D)=11,
\qquad
\mu(A,W)=8.
\tag{3.1}
\]

For an A--W child, the only remaining candidates are the surviving W
when A is the target, and D in either target direction. Complete
Whitehead descent gives minimum 9 for all 186 child/W pairs. For the
186 child/D pairs, the complete minimum distribution is

\[
\begin{array}{c|rrrrrrrrr}
\text{minimum}&7&17&18&19&20&21&22&23&25\\
\hline
\text{classes}&1&4&2&6&4&16&6&31&116.
\end{array}
\tag{3.2}
\]

When W is the target, the surviving A is already excluded by its
individual nonprimitivity; complete pair descent gives minimum 8 for
all 186 child/A classes.

For each of the four primitive W--D children, the child/D minimum in
the `W <- D` direction is 16, and the child/W minimum in the
`D <- W` direction is 26. The child/A minimum is 8 in all four
classes, agreeing with A's individual exclusion.

No minimum is 2. Hence the direct primitive-pair count is exactly zero.
This calculation uses conjugacy-class pairs throughout; it does not
replace a cyclic child/source pair by an unjustified aligned Nielsen
pair.

## 4. Changed-row-first sequential deletion

Straighten each of the 2,280 primitive children in the full labeled
four-relator tuple and delete its terminal coordinate. For the A--W
family the straightener is the explicit map (2.2); for the four W--D
classes it is the stored complete Whitehead composite.

Classify every survivor under all 90 second-kind maps of the remaining
rank-three free group. The exact result is

\[
\begin{array}{c|c|c}
\text{primitive survivors}&\text{quotient states}&
\text{primitive survivor pairs}\\
\hline
0&2{,}268&0\\
1&12&0.
\end{array}
\tag{4.1}
\]

In particular, all 48 W--D primitive-child quotients stop immediately.
Of the 2,232 A--W quotients, 2,220 stop immediately.

### 4.1. The sole second-deletion class

The remaining child is

\[
H=\operatorname{can}(A^{-1}W)
=\operatorname{can}(z^{-1}C)
=\texttt{QTqXQz}
=C^{-1}z.
\tag{4.2}
\]

It occurs at all six checkpoints in both target directions. The simple
straightener

\[
z\longmapsto Cz
\tag{4.3}
\]

fixing \(x,t,q\) sends H to z. Put

\[
D_0=t^{-1}CxC^{-1}.
\tag{4.4}
\]

After (4.3) and \(z=1\), both target directions give the same labeled
rank-three tuple

\[
\left(
A,\ D_0,\ q^\eta A^\epsilon D_0^\delta
\right).
\tag{4.5}
\]

Now apply

\[
\beta^{-1}:
\qquad
x\longmapsto q^{-1}xq,
\quad
t\longmapsto t,
\quad
q\longmapsto q.
\tag{4.6}
\]

Exact free reduction gives

\[
\beta^{-1}(A)=R=x^3t^{-4},
\qquad
\beta^{-1}(C)=xtq,
\qquad
\beta^{-1}(D_0)=E=t^{-1}xtxt^{-1}x^{-1}.
\tag{4.7}
\]

Therefore the last row of (4.5) becomes

\[
q^\eta R^\epsilon E^\delta.
\tag{4.8}
\]

Both R and E are q-free, so (4.8) contains exactly one
\(q^{\pm1}\). It is an explicit unique-q coordinate for every sign
row, with the same inverse formula as (2.2). This proves uniformly,
without six unrelated descents, that it is the unique primitive
survivor in every positive quotient.

Straighten (4.8) and delete q. Because R and E are q-free, every sign
row leaves literally the same raw rank-two pair

\[
(R,E)=(\texttt{xxxTTTT},\texttt{TxtxTX}).
\tag{4.9}
\]

Relabeling t as y and taking cyclic canonical forms gives, in all 12
cases,

\[
\mathcal F_{13}
=
(\texttt{XXXXYYY},\texttt{XYxYXy}).
\tag{4.10}
\]

This is the canonical representative labeled `13_1` in the independent
equivalence-class table, hence the original rank-two AK(3) Aut-orbit.
The stable ambient-automorphism principle applies each coordinate to
the full relator tuple, and the primitive generator-relator deletion is
the stable deletion move. Thus the apparent A--W cancellation is a
stable self-loop to the starting problem, not a claim that the
intermediate rank-two pair was identified by an ordinary classical AC
sequence.

## 5. Conclusion and boundary

The signed-cyclic carrier image contains many primitive changed rows,
but no direct primitive pair. Its only changed-row-first second
deletions are the 12 copies of the literal A-block cancellation (4.2),
and every one is a stable self-loop to AK(3)'s floor-13 orbit. This
proves (0.2).

The theorem does not classify:

- an arbitrary relative-conjugator product \(TuSu^{-1}\);
- deletion of an unchanged primitive row before the changed row;
- a Q/carrier edge beyond Result 49's signed-cyclic image;
- two row-changing edges before deletion;
- a history that first changes the checkpoint.

AK(3), AC, and stable AC remain open.

## 6. Independent replay

The dependency-free verifier
`tests/stable_ac/test_d_tail_one_edge_primitive_creation.py`:

- enumerates all counts in (1.3)--(1.4);
- verifies the unique-z condition for every A--W child;
- generates all 504, 90, and 12 second-kind maps in ranks four, three,
  and two;
- reproduces (2.3)--(2.4), the four exceptional words, and
  (3.1)--(3.2);
- tests every direct pair with an actually eligible surviving row;
- applies each child straightener to all labeled survivors;
- proves the quotient distribution (4.1);
- replays (4.3)--(4.9) and all six unique-q coordinates literally;
- closes every rank-two minimum level under first- and second-kind
  maps;
- reproduces (4.10) twelve times and finds no new endpoint.
