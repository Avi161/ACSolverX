# Unchanged-primitive-first closure after one carrier edge

Date: 2026-07-26

Status: **PROVEN** with two explicit scopes:

- source-first deletion is unbounded in the relative conjugator;
- non-source deletion is complete for the signed-cyclic carrier image.

At each of the six nonprimitive D-tail checkpoints, perform one relator
multiplication between two carriers A, W, D, then delete an unchanged
primitive carrier before the changed row.

If the deleted row is the retained source, the edge is an exact
quotient gauge for every relative conjugator. The only non-source
choices in the signed-cyclic image reduce to 2,928 rank-three states.
Exactly 744 have a primitive survivor, but every second deletion is
represented in Result 47's fixed double-deletion coordinate by a
multiplication by a conjugate from the known floor-23 compression
corridor. The displayed relation is a short classical AC sequence;
arbitrary straightener outputs are stably equivalent to that
representative. Their complete Aut-floors are at least 14.

Thus:

\[
\boxed{
\text{within the two stated scopes, no unchanged-primitive-first
carrier edge creates a new low endpoint.}
}
\tag{0.1}
\]

This is a stable closure statement. It is not a proof of AC or stable
AC.

## 1. Checkpoint and primitive carriers

Use

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

with

\[
(\eta,\epsilon)\in\{(+,+),(-,+),(-,-)\},
\qquad
\delta\in\{+1,-1\}.
\tag{1.2}
\]

Result 48 proves every Q-row in (1.2) nonprimitive. Result 50 verifies
that A is nonprimitive while W and D are primitive.

Two particularly simple straighteners are

\[
\begin{aligned}
\phi_W:\quad&
z\longmapsto Cz^{-1}A,
&&x,t,q\text{ fixed},\\
\phi_D:\quad&
x\longmapsto z^{-1}txz,
&&t,z,q\text{ fixed}.
\end{aligned}
\tag{1.3}
\]

Direct substitution gives

\[
\phi_W(W)=z,
\qquad
\phi_D(D)=x.
\tag{1.4}
\]

The stable ambient-automorphism principle applies these maps to the
entire tuple before primitive generator-relator deletion.

## 2. Arbitrary-conjugator source-first theorem

### Lemma 2.1

Let S be a primitive relator in a balanced trivial-group tuple, let
\(\phi(S)=p\) be a basis letter, and let

\[
\theta=\rho_p\phi,
\qquad
\rho_p(p)=1
\tag{2.1}
\]

be the primitive-deletion quotient. For arbitrary target T,
conjugator u, and sign \(\sigma\),

\[
T'=TuS^\sigma u^{-1}
\tag{2.2}
\]

satisfies

\[
\boxed{\theta(T')=\theta(T).}
\tag{2.3}
\]

#### Proof

The quotient homomorphism kills S, so

\[
\theta(T')
=
\theta(T)\theta(u)\theta(S)^\sigma\theta(u)^{-1}
=
\theta(T).
\]

All other survivors have the same quotient images as before the edge.
Hence source-first deletion after (2.2) is literally the baseline
source deletion. \(\square\)

This proves an unbounded statement: u may have arbitrary length and
may involve every generator.

### Corollary 2.2

At the Q/carrier checkpoints of Result 49, Lemma 2.1 applies to

\[
Q\leftarrow QuW^{\pm1}u^{-1},
\qquad
Q\leftarrow QuD^{\pm1}u^{-1}.
\tag{2.4}
\]

At the carrier/carrier checkpoints of Result 50, it applies to

\[
\begin{aligned}
A&\leftarrow AuW^{\pm1}u^{-1},\\
A&\leftarrow AuD^{\pm1}u^{-1},\\
W&\leftarrow WuD^{\pm1}u^{-1},\\
D&\leftarrow DuW^{\pm1}u^{-1}.
\end{aligned}
\tag{2.5}
\]

Deleting the displayed retained source first erases the edge exactly.
No relative-conjugator census is needed.

## 3. The only non-source deletion cases

Within Result 50's signed-cyclic image, an unchanged primitive carrier
can instead be deleted without being the edge source only in two
families:

1. multiply A and W in either target direction, then delete D;
2. multiply A and D in either target direction, then delete W.

There are

\[
\begin{array}{c|c}
\text{ordered edge and deletion}&
\text{labeled rank-three states}\\
\hline
A\leftarrow W;\ D\text{ first}&1{,}116\\
W\leftarrow A;\ D\text{ first}&1{,}116\\
A\leftarrow D;\ W\text{ first}&348\\
D\leftarrow A;\ W\text{ first}&348.
\end{array}
\tag{3.1}
\]

The total is 2,928. These are child states, not multiplicity-weighted
literal witnesses.

Apply the appropriate full-tuple straightener in (1.3), kill its basis
letter, use the Whitehead-graph gate, and then minimize every survivor
under all 90 second-kind Whitehead maps of the remaining \(F_3\).
The complete result is

\[
\begin{array}{c|c}
\text{primitive survivors}&\text{states}\\
\hline
0&2{,}184\\
1&744.
\end{array}
\tag{3.2}
\]

No quotient has a primitive survivor pair.

Every A--D/W-first quotient occurs in the zero row. In the A--W/D-first
family, the only positive survivor is Q, and positivity occurs exactly
at

\[
(\eta,\epsilon)=(-,+),
\qquad
\delta=\pm1.
\tag{3.3}
\]

There are \(186\cdot2=372\) positive states in each target direction.
This also follows structurally from Result 47: after D is killed,
\(q^{-1}W D^\delta\) becomes a conjugate of
\(S=Wq^{-1}\), and \((S,D)\) is a based primitive pair.

## 4. A fixed-coordinate representative returns to the old corridor

Result 47's based-pair straightener sends

\[
S=Wq^{-1}\longmapsto z^{-1},
\qquad
D\longmapsto t^{-1}.
\tag{4.1}
\]

After deleting the mixed-sign Q-row and D, the unchanged A--W baseline
becomes the known pair

\[
\begin{aligned}
r&=\texttt{YXXXXyxxx},\\
s&=\texttt{YYXXXXyxxxYxyx},
\end{aligned}
\tag{4.2}
\]

whose complete Aut-floor is 23.

It remains to track the carrier edge. Let

\[
T_i=u^{-1}Tu,
\qquad
S_j=v^{-1}S_0^\sigma v
\tag{4.3}
\]

be the two signed cyclic representatives multiplied before deletion,
and let \(\pi\) be the double-deletion quotient. Conjugating the target
image by \(\pi(u)\) changes

\[
\pi(T_iS_j)
\quad\text{to}\quad
\pi(T)c\,\pi(S_0)^\sigma c^{-1},
\qquad
c=\pi(uv^{-1}).
\tag{4.4}
\]

Equation (4.4) is a multiplication by a conjugate. It is realized by
inverting the source if needed, conjugating it by \(c\), multiplying
the target by that source, and undoing the source conjugation and
inversion. Thus, for every endpoint Aut-orbit, the representative in
the fixed \(\pi\)-coordinate is classically AC-equivalent to the
floor-23 pair. The verifier's arbitrary straightener outputs are
Aut-equivalent to these representatives and hence stably lie in the
same corridor. This does not identify those outputs classically.

## 5. Complete endpoint floors

The 372 final pairs in each target direction collapse to 154 distinct
cyclic-normalized raw pairs per direction. Complete rank-two Whitehead
descent gives:

\[
\begin{array}{c|c|c|c}
\text{original target}&
\text{minimum floor}&
\text{states at minimum}&
\text{minimum representative}\\
\hline
A&19&8&
\texttt{XXXXYYxyxYxxxy | XYXyy}\\
W&14&8&
\texttt{XXXXYxxxy | XYXyy}.
\end{array}
\tag{5.1}
\]

The verifier records the exact full floor histograms for all 744
states. In particular,

\[
\boxed{\text{no endpoint has Aut-floor at most }12.}
\tag{5.2}
\]

The floors do not decide classical AC equivalence. Equation (4.4)
decides it only for the fixed-coordinate representative in each
endpoint Aut-orbit. The 308 distinct normalized raw pairs need not be
one Aut-orbit and are not claimed to be classically identified.

## 6. Conclusion and boundary

Combining Lemma 2.1 with Sections 3--5 closes every order in which an
unchanged primitive carrier is deleted first after one signed-cyclic
carrier edge:

- source-first edges are quotient gauges, even for arbitrary relative
  conjugators;
- the two non-source families either stop in rank three or have a
  fixed-coordinate representative returning classically to the old
  floor-23 corridor, while arbitrary straightener outputs return
  stably;
- no endpoint reaches floor at most 12.

The arbitrary-conjugator conclusion does not extend here to non-source
deletion. Also outside scope are changed-row-first orders (Result 50),
two row changes before deletion, and histories that first alter the
checkpoint.

AK(3), AC, and stable AC remain open.

## 7. Independent replay

The dependency-free verifier
`tests/stable_ac/test_d_tail_one_edge_primitive_creation.py`:

- checks the exact W and D straighteners in (1.3);
- exercises Lemma 2.1 on every eligible ordered checkpoint with
  mixed-generator conjugators and both signs;
- enumerates every state in (3.1);
- reproduces (3.2)--(3.3) and the absence of survivor pairs;
- transports all 744 second deletions to rank two;
- records the complete direction-specific floor distributions;
- verifies the 154 distinct raw pairs per direction, the minimum
  representatives in (5.1), and the zero count in (5.2).
