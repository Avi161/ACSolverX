# Cyclic one-edge primitive creation from every nonprimitive D-tail

Date: 2026-07-26

Status: **PROVEN** for the stated signed-cyclic one-edge stratum.

At each of the six nonprimitive first-tail checkpoints

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

take one AC2 multiplication between signed cyclic representatives of
Q and one of A, W, D, in either target direction. This allows AC1
inversion and the AC3 prefix conjugations that choose cyclic rotations.
It does not allow an arbitrary relative conjugator between the two
factors.

The complete image contains primitive changed rows, so the stronger
hope that one edge never creates a coordinate is false. Nevertheless:

\[
\boxed{
\begin{gathered}
\text{there are exactly six primitive changed conjugacy classes,}\\
\text{30 direct primitive-pair incidences, and}\\
\text{32 sequential primitive-single deletion branches;}\\
\text{every direct-pair or changed-row-first endpoint is known.}
\end{gathered}
}
\tag{0.2}
\]

Eighteen direct pair deletions and twenty sequential deletions reach
the known floor-23 compression orbit. The other twelve of each reach
the known floor-27 backtrack orbit. No new endpoint remains in this
signed-cyclic, changed-row-first stratum.

This is a finite Whitehead classification, not an AC graph search.

## 1. Notation

At the fixed rank-four checkpoint,

\[
\begin{aligned}
A&=qx^3q^{-1}t^{-4},\\
C&=qxq^{-1}tq,\\
W&=Az^{-1}C,\\
D&=t^{-1}zxz^{-1}.
\end{aligned}
\tag{1.1}
\]

Uppercase letters in machine words denote inverses. Result 48 proves
that all six rows in (0.1) are nonprimitive.

## 2. The exact signed-cyclic image

Let T be the target word and S the retained source word. Rotating T
and taking every signed rotation of S gives

\[
\operatorname{can}(T_i S_j^\sigma),
\qquad
0\le i<|T|,
\quad
0\le j<|S|,
\quad
\sigma\in\{+1,-1\},
\tag{2.1}
\]

where `can` means free reduction, cyclic reduction, and minimization
over cyclic rotation and inversion.

This already includes target inversion. Indeed,

\[
(T^{-1}S^\sigma)^{-1}=S^{-\sigma}T,
\]

and \(S^{-\sigma}T\) is cyclically conjugate to
\(TS^{-\sigma}\), which occurs in (2.1). Thus (2.1) is the exact
symmetry quotient of all signed cyclic-representative realizations of
one multiplication.

Across six roots, three carriers, and two target directions, it has

\[
12{,}992
\tag{2.2}
\]

literal representatives. Counting the redundant target orientation
as a separately indexed realization gives 25,984 oriented literals.
The quotient has 9,480 direction-tagged child states and 4,720
distinct changed conjugacy classes globally.

The retained rows are tracked by label. Reversing the target direction
does not change the child class, because UV and VU are conjugate, but
it changes which original row survives. The endpoint calculation
therefore keeps the two directions separate.

## 3. Complete primitive-single census

The rank-four Whitehead graph rejects every connected, no-cut-vertex
child of length greater than one. This leaves 88 direction-tagged
states. Every survivor of that necessary gate is minimized under all
504 second-kind Whitehead automorphisms of \(F_4\).

Exactly six canonical words have minimum length one:

\[
\begin{array}{c|c|c|c|c}
\text{carrier}&(\eta,\epsilon,\delta)&
\text{primitive child}&
\text{states}&
\text{literals}\\
\hline
A&(+,+,+)&\texttt{QTqXQzQzXZt}&2&20\\
A&(+,+,-)&\texttt{QTqXQzQTzxZ}&2&20\\
W&(+,+,+),(-,+,-),(-,-,-)&\texttt{QzXZt}&6&98\\
W&(+,+,-),(-,+,+),(-,-,+)&\texttt{QTzxZ}&6&100\\
D&(+,+,\pm),(-,-,\pm)&\texttt{QQQTqXQzttttqXXX}&8&40\\
D&(-,+,\pm)&\texttt{QTTTTZqxQtqxxx}&4&20
\end{array}
\tag{3.1}
\]

The state count includes both target directions. The literal count
uses the symmetry quotient (2.1); it doubles if target inversion is
indexed separately.

The exact strict length descents for the six rows are

\[
\begin{array}{c|l}
\text{row in (3.1)}&\text{lengths}\\
\hline
\texttt{QQQTqXQzttttqXXX}&
16,12,11,10,9,8,6,5,4,3,2,1\\
\texttt{QTTTTZqxQtqxxx}&
14,10,9,7,6,5,4,3,2,1\\
\texttt{QTqXQzQTzxZ}&
11,8,7,6,4,3,2,1\\
\texttt{QTqXQzQzXZt}&
11,8,6,5,4,3,2,1\\
\texttt{QTzxZ},\ \texttt{QzXZt}&
5,3,2,1.
\end{array}
\tag{3.2}
\]

The replay stores and applies the actual automorphism at every step;
(3.2) is not merely a length heuristic.

Consequently there are 28 primitive direction-tagged states and 298
literal witnesses in the quotient model. No other changed row is
primitive: the graph gate plus complete Whitehead minimization covers
all 4,720 child classes.

## 4. Direct primitive pairs

A primitive pair can contain only primitive individual words. It is
therefore enough to pair each of the 28 positive child states with
each of its three actually surviving labeled rows.

For completeness, the unchanged carrier pairs have complete
rank-four Whitehead minima

\[
\mu(A,W)=8,\qquad
\mu(A,D)=11,\qquad
\mu(W,D)=16,
\tag{4.1}
\]

and no pair containing one of the six unchanged nonprimitive Q-rows
is primitive.

Complete pair descent gives exactly 30 direct incidences:

\[
\begin{array}{c|c|c}
\text{primitive child family}&
\text{primitive partner}&
\text{incidences}\\
\hline
\text{A-child rows}&D&4\\
\text{W-child rows}&D&12\\
\text{same-sign D-child rows}&W&8\\
\text{mixed-sign D-child rows}&W&4\\
\text{mixed-sign Q-target rows only}&D&2
\end{array}
\tag{4.2}
\]

The first, second, and last lines give 18 copies of the known
floor-23 orbit. The two W-partner lines give 12 copies of the known
floor-27 orbit.

Transporting the complete ambient automorphism, deleting the two
basis coordinates, relabeling the remaining basis, and closing the
minimum level set gives the lexicographic representatives

\[
\begin{aligned}
\mathcal F_{23}
&=
(\texttt{XXXXYYxyxYxxxy},\texttt{XXXXYxxxy}),\\
\mathcal F_{27}
&=
(\texttt{XXXXYYY},\texttt{XXXXYYYxYXyXyyyxxxxY}).
\end{aligned}
\tag{4.3}
\]

These are respectively the same Aut-orbits as the previously
displayed representatives

\[
\begin{aligned}
(\texttt{YXXXXyxxx},\texttt{YYXXXXyxxxYxyx}),\\
(\texttt{YYYXXXX},\texttt{YYYXXXXYxxxxyyyXyXYx}).
\end{aligned}
\tag{4.4}
\]

Result 47 merges the first orbit into the old stable floor-14
compression corridor. Result 44 identifies the second orbit as the
qW zero-tail backtrack.

## 5. Sequential primitive-single deletions

For each of the 28 primitive children, apply its stored rank-four
straightener to the entire labeled tuple and kill the terminal basis
coordinate. This gives a rank-three quotient with three survivors.
Complete minimization under all 90 second-kind maps of \(F_3\) gives:

- 24 quotients have exactly one primitive survivor;
- four quotients have exactly two primitive survivors;
- none has a primitive pair of survivors.

There are therefore 32 primitive-child-then-primitive-survivor
branches. Applying the second stored straightener, deleting again,
and taking the complete rank-two level-set canonical form gives

\[
20\mathcal F_{23}+12\mathcal F_{27}.
\tag{5.1}
\]

The four two-choice quotients are precisely the mixed-sign D-child
states. The W-survivor choice gives \(\mathcal F_{27}\). The other
choice gives \(\mathcal F_{23}\): it is D when Q was the target, and
the original Q when D was the target.

This explains why the sequential count 32 exceeds the direct-pair
count 30. In the two mixed-sign `D <- Q` states, the original Q is
nonprimitive in \(F_4\), and its direct pair with the changed D-row
has complete minimum 28 rather than 2. After the changed row is
deleted, the quotient image of Q becomes primitive.

There is no contradiction with the primitive pair in the other target
direction. The D-child is a cyclic conjugate of the qW zero-tail
coordinate; pair reduction treats its two components as independently
conjugated conjugacy classes. It does not align that conjugator with
the literal D-factor inside the original Q-word. Quotient primitivity
does not automatically lift to a based primitive pair in \(F_4\).

## 6. Conclusion and boundary

Every direct primitive-pair deletion in (2.1), and every sequential
deletion which removes the newly primitive changed row first, lands in
one of the two already certified orbits (4.3). In particular, no
endpoint of Aut-floor at most 12 is created in this stratum.

The theorem does not classify:

- an edge solely between two of A, W, D;
- a relative-conjugator product \(TuSu^{-1}\) with arbitrary u;
- deleting an unchanged primitive survivor before the changed row;
- sequential deletion beginning with a nonprimitive changed row;
- two consecutive row-changing edges before the first deletion;
- a history that first changes the six checkpoints;
- a different stabilization or primitive slot.

AK(3), AC, and stable AC remain open.

## 7. Independent replay

The dependency-free verifier
`tests/stable_ac/test_d_tail_one_edge_primitive_creation.py`:

- enumerates (2.1) in both target directions;
- verifies the 12,992/25,984 literal counts, all state counts, and
  every row of (3.1);
- constructs the Whitehead graph gate directly;
- generates exactly 504, 90, and 12 second-kind maps in ranks four,
  three, and two;
- computes complete strict minima and stores their ambient composite
  maps;
- transports every positive through the full labeled tuple;
- verifies (4.1), all 30 direct incidences, and all 32 sequential
  branches;
- closes each rank-two minimum level under second- and first-kind
  Whitehead maps;
- reproduces (4.3) and proves that the new-endpoint count is zero.
