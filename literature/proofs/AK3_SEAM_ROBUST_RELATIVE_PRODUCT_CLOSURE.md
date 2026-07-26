# Seam-robust closure of arbitrary Q/carrier relative products

Date: 2026-07-26

Status: **PROVEN** for one arbitrary-relative-conjugator product
between a nonprimitive D-tail Q-row and one carrier A, W, or D, in
both target directions, followed by either direct primitive-pair
deletion or changed-row-first sequential deletion.

Result 49 classified only products of signed cyclic representatives.
Here the relative conjugator is an arbitrary word in
\(F(x,t,z,q)\), with no length bound.

For each of the six Q-rows, a row-specific basis change makes every
linear cut of the Q-word contain a spanning cycle in its Whitehead
graph. A Cayley-tree bridge argument then gives:

\[
\boxed{
\begin{gathered}
\text{a primitive arbitrary relative product must have intersecting
factor axes;}\\
\text{the intersecting-axis table produces exactly Result 49's six
primitive classes.}
\end{gathered}
}
\tag{0.1}
\]

Thus arbitrary relative conjugators create no additional primitive
changed row and no new endpoint in this one-edge stratum.

This is a Whitehead and tree-axis classification, not an AC graph
search. It does not prove AC or stable AC.

## 1. Linear-cut Whitehead graphs

Let \(F(X)\) be a finite-rank free group with signed basis
\(X^{\pm1}\). For a cyclically reduced word

\[
U=u_0u_1\cdots u_{n-1},
\tag{1.1}
\]

the cyclic Whitehead graph has an undirected edge from
\(u_i^{-1}\) to \(u_{i+1}\), with indices modulo n.

For a cut at i, rotate U to

\[
U_i=u_i\cdots u_{n-1}u_0\cdots u_{i-1}
\tag{1.2}
\]

and omit only the closing adjacency from the last letter of \(U_i\)
to its first. The resulting graph is the **linear-cut Whitehead
graph** \(\operatorname{Wh}^{\circ}_i(U)\).

Call U **seam-robust** if every
\(\operatorname{Wh}^{\circ}_i(U)\) contains a Hamiltonian cycle on
all vertices \(X^{\pm1}\).

The definition is stronger than asking the cyclic Whitehead graph to
have no cut vertex: it survives deletion of whichever one of U's
cyclic seams is opened by an external bridge.

## 2. The axis-bridge lemma

### Lemma 2.1

Let U and V be nontrivial cyclically reduced words in \(F(X)\), and
assume U is seam-robust. For any relative conjugator c, consider

\[
P=UcVc^{-1}.
\tag{2.1}
\]

If the translation axes of U and \(cVc^{-1}\) in the Cayley tree are
disjoint, P is nonprimitive.

#### Proof

Let a and b be the group elements represented by U and
\(cVc^{-1}\). Let p and q be the endpoints of the unique shortest
bridge from the axis of a to the axis of b. Conjugate both factors,
and hence their product, so p is the base vertex. This global
conjugation preserves primitivity. In this shortest-axis-bridge normal
form, the based word for a is a cyclic rotation \(U_i\); the based
word for b is \(b_0V_jb_0^{-1}\), where \(b_0\ne1\) labels the bridge
from p to q. Thus the product is represented by

\[
U_i\,b_0\,V_j\,b_0^{-1},
\tag{2.2}
\]

where \(U_i,V_j\) are cyclic rotations of U and V. Because \(b_0\)
is the shortest axis bridge, its
first and last edges leave the two axes. Therefore there is no free
cancellation at any of the four seams in (2.2), including the cyclic
last-to-first seam. Formula (2.2) is freely and cyclically reduced.

The internal adjacent pairs of the displayed \(U_i\)-block contribute
exactly \(\operatorname{Wh}^{\circ}_i(U)\) to
\(\operatorname{Wh}(P)\). By seam robustness this subgraph contains
a Hamiltonian cycle on all signed basis vertices. Any graph containing
such a cycle is connected and remains connected after deletion of any
one vertex.

Whitehead's cut-vertex lemma says that the graph of a cyclically
reduced primitive word of length greater than one is disconnected or
has a cut vertex. Hence P is nonprimitive. \(\square\)

### Lemma 2.2

If the two axes meet, the conjugacy class of P is represented by

\[
\operatorname{cyc\mbox{-}red}(U_iV_j)
\tag{2.3}
\]

for cyclic rotations \(U_i,V_j\). If the source orientation is free,
\(V_j\) ranges over signed cyclic rotations.

#### Proof

Choose a vertex in the axis intersection and conjugate both factors
to that base vertex. A cyclically reduced representative based at a
vertex of its axis is a cyclic rotation of its cyclic word. Reading
the two based translations consecutively gives (2.3), with any seam
cancellation handled by free and cyclic reduction. \(\square\)

Lemmas 2.1--2.2 split the infinite relative-conjugator problem
exactly:

- disjoint axes are rejected by one seam-robust factor;
- intersecting axes are a finite signed-rotation table.

The written case \(c=1\) necessarily belongs to the intersecting-axis
line. More generally, a nontrivial written c may normalize to bridge
\(b_0=1\); written conjugator length is not bridge length.

In the application below, this split is made in the standard Cayley
tree **after** applying the row-specific automorphism. An automorphism
need not preserve intersection of axes in the original standard
Cayley tree; no such invariance is assumed.

## 3. Six seam-robust coordinates

At the checkpoint, put

\[
\begin{aligned}
A&=qx^3q^{-1}t^{-4},\\
C&=qxq^{-1}tq,\\
W&=Az^{-1}C,\\
D&=t^{-1}zxz^{-1},\\
Q_{\eta,\epsilon,\delta}
&=q^\eta W^\epsilon D^\delta,
\end{aligned}
\tag{3.1}
\]

with

\[
(\eta,\epsilon)\in\{(+,+),(-,+),(-,-)\},
\qquad
\delta=\pm1.
\tag{3.2}
\]

Use the automorphisms

\[
\begin{array}{c|cccc}
&x&t&z&q\\
\hline
\alpha&q^{-1}xq&t&zq&q\\
\mu&txt^{-1}&t&tzt^{-1}&qt^{-1}\\
\nu&x&x^{-1}tx&zx&x^{-1}qx.
\end{array}
\tag{3.3}
\]

The notation \(\mu\alpha\) means first apply \(\alpha\), then
\(\mu\), and similarly for \(\nu\alpha\).

After the indicated map and a cyclic reorientation, the six Q-rows
become:

\[
\begin{array}{c|c|l|c|c}
(\eta,\epsilon,\delta)&\text{map}&U&
\text{distinct cut graphs}&\text{cycle cover}\\
\hline
(-,+,+)&\mathrm{id}&
\texttt{QTTTTZqxQtqTzxZxxx}&10&3\\
(-,+,-)&\mathrm{id}&
\texttt{QTTTTZqxQtqzXZtxxx}&10&3\\
(+,+,+)&\alpha&
\texttt{QTXzqttttXXXQzXZt}&13&4\\
(-,-,+)&\alpha&
\texttt{QQTXzqttttXXXTzxZ}&13&3\\
(+,+,-)&\mu\alpha&
\texttt{QXzTqttttXXXQzxZ}&12&3\\
(-,-,-)&\nu\alpha&
\texttt{QQTzqttttXXzXZXt}&14&3.
\end{array}
\tag{3.4}
\]

Every cut graph in (3.4) contains a spanning cycle. The following is
an exact compact certificate. Number cuts from zero, starting before
successive letters of the displayed U. Each `ids` entry selects one
of the cycles listed immediately above it.

```text
(-,+,+)
1 Q-T-q-t-z-x-Z-X-Q
2 Q-X-Z-t-T-q-z-x-Q
3 Q-T-q-z-t-Z-x-X-Q
ids 1 1 1 1 1 1 1 1 1 2 1 2 2 2 3 3 1 1

(-,+,-)
1 Q-X-Z-x-T-q-t-z-Q
2 Q-X-Z-t-z-q-T-x-Q
3 Q-X-x-Z-t-T-q-z-Q
ids 1 1 1 1 1 1 1 1 1 2 1 2 3 2 3 3 1 1

(+,+,+)
1 Q-t-T-X-Z-q-z-x-Q
2 Q-T-q-Z-X-t-z-x-Q
3 Q-T-X-x-Z-q-z-t-Q
4 Q-T-q-z-t-X-Z-x-Q
ids 1 1 1 3 4 2 1 1 1 2 1 1 3 2 3 1 1

(-,-,+)
1 Q-q-T-X-Z-x-z-t-Q
2 Q-t-T-q-Z-X-x-z-Q
3 Q-q-Z-x-X-T-t-z-Q
ids 1 2 3 1 3 1 3 1 1 1 2 1 1 1 2 2 3

(+,+,-)
1 Q-t-T-Z-X-q-z-x-Q
2 Q-x-Z-X-T-t-q-z-Q
3 Q-t-q-X-T-Z-x-z-Q
ids 1 2 2 2 1 2 1 1 1 1 1 1 3 3 1 3

(-,-,-)
1 Q-q-T-X-Z-x-z-t-Q
2 Q-T-q-Z-X-z-x-t-Q
3 Q-T-X-z-t-x-Z-q-Q
ids 1 2 3 2 1 3 1 1 1 2 1 3 3 2 1 1
```

For each cycle, consecutive vertices, including the closing pair,
are edges of the selected linear-cut graph. Each cycle visits

\[
x,X,t,T,z,Z,q,Q
\tag{3.5}
\]

exactly once. This proves all six transformed Q-rows seam-robust.

## 4. Complete intersecting-axis tables

The carrier is transformed by the same row map as Q. Put

\[
S_\phi=\operatorname{cyc\mbox{-}red}(\phi(S)),
\tag{4.1}
\]

choosing any cyclic orientation. The conjugating prefixes used to
cyclically reduce \(\phi(Q)\) and \(\phi(S)\) are absorbed into the
arbitrary transformed relative conjugator. For each row and each
carrier \(S\in\{A,W,D\}\), enumerate

\[
\operatorname{can}(U_i (S_\phi)_j^\tau),
\qquad
\tau=\pm1,
\tag{4.2}
\]

over every cyclic rotation of U and \(S_\phi\). This is exactly Lemma 2.2's
intersecting-axis image in the transformed basis.

In the table below, `N/G/P` means:

- N distinct cyclic child classes;
- G classes passing the connected/no-cut-vertex rejection gate;
- P primitive classes after complete minimization under all 504
  second-kind Whitehead maps of \(F_4\).

The final entry is the primitive class after applying the exact
inverse row map and canonicalizing in the original basis.

\[
\begin{array}{c|l|l|l}
(\eta,\epsilon,\delta)&A&W&D\\
\hline
(-,+,+)&
230/0/0&
394/1/1\to\texttt{QTzxZ}&
110/1/1\to\texttt{QTTTTZqxQtqxxx}\\
(-,+,-)&
230/0/0&
394/1/1\to\texttt{QzXZt}&
110/1/1\to\texttt{QTTTTZqxQtqxxx}\\
(+,+,+)&
160/1/1\to\texttt{QTqXQzQzXZt}&
290/1/1\to\texttt{QzXZt}&
102/1/1\to\texttt{QQQTqXQzttttqXXX}\\
(-,-,+)&
160/0/0&
290/1/1\to\texttt{QTzxZ}&
102/1/1\to\texttt{QQQTqXQzttttqXXX}\\
(+,+,-)&
154/1/1\to\texttt{QTqXQzQTzxZ}&
276/1/1\to\texttt{QTzxZ}&
96/1/1\to\texttt{QQQTqXQzttttqXXX}\\
(-,-,-)&
152/0/0&
250/1/1\to\texttt{QzXZt}&
144/1/1\to\texttt{QQQTqXQzttttqXXX}.
\end{array}
\tag{4.3}
\]

The inverse coordinates used in this replay are

\[
\begin{array}{c|cccc}
&x&t&z&q\\
\hline
\alpha^{-1}&qxq^{-1}&t&zq^{-1}&q\\
\mu^{-1}&t^{-1}xt&t&t^{-1}zt&qt\\
\nu^{-1}&x&xtx^{-1}&zx^{-1}&xqx^{-1}.
\end{array}
\tag{4.4}
\]

Thus (4.3) is not merely a comparison of transformed word lengths:
every positive is transported literally back to the original basis.
With the composition convention in (3.3),

\[
(\mu\alpha)^{-1}=\alpha^{-1}\mu^{-1},
\qquad
(\nu\alpha)^{-1}=\alpha^{-1}\nu^{-1}.
\tag{4.5}
\]

The primitive classes, carrier labels, and checkpoint signs in (4.3)
are exactly the six rows of Result 49's primitive-single table. There
is no seventh class.

## 5. Full-tuple and endpoint inheritance

Consider an arbitrary product

\[
T\longmapsto TuS^\sigma u^{-1},
\tag{5.1}
\]

where one of T,S is \(Q_{\eta,\epsilon,\delta}\), the other is A, W,
or D, and u is arbitrary in \(F(x,t,z,q)\). Target inversion, target
conjugation, and the opposite multiplication side do not add a child
conjugacy class.

Apply the row map \(\phi\) from (3.4), cyclically reduce
\(\phi(Q)\) and \(\phi(S)\), and absorb the reduction conjugators into
\(\phi(u)\). Compare their axes in the standard Cayley tree for this
transformed coordinate basis; no original-metric axis intersection is
being preserved. If those transformed axes are disjoint, Lemma 2.1
proves the changed row nonprimitive. If they meet, Lemma 2.2 and (4.3)
show that a primitive changed row maps back to one of Result 49's six
classes with the same checkpoint and carrier.

Only the target row was changed by (5.1); every other labeled relator
remains the fixed checkpoint word. Conjugating or inverting the
changed row to Result 49's canonical representative does not alter
the survivors. Hence the resulting full labeled tuple is exactly one
of the direction-tagged Result 49 states. Reversing target direction
changes the surviving source label, but Result 49 already transported
both directions separately.

The row-specific \(\phi\) is only an analytical primitivity coordinate
and is inverted before this original-tuple comparison. Identifying the
original changed row with its Result 49 representative uses only
relator inversion and conjugation; the later primitive coordinate
deletions are precisely the stable operations already certified in
Result 49.

Therefore all of Result 49's endpoint conclusions extend without a
relative-conjugator bound:

- the primitive changed-row conjugacy classes are exactly the same
  six classes;
- the 28 direction-tagged primitive class states are unchanged;
- the direct primitive-pair incidences still give only 18 floor-23
  and 12 floor-27 endpoints;
- the changed-row-first sequential branches still give only 20
  floor-23 and 12 floor-27 endpoints.

The witness set is now infinite, so Result 49's finite literal
multiplicities do not extend. The class-state and endpoint statements
do.

## 6. Conclusion and boundary

Every arbitrary relative conjugator in one Q/carrier product at the
six fixed D-tail checkpoints is now classified. Disjoint factor axes
are nonprimitive by the seam-robust bridge lemma. Intersecting axes
produce exactly the old finite primitive classes. Thus this infinite
extension creates no new direct-pair or changed-row-first endpoint.

The theorem does not classify:

- carrier/carrier products (Result 52 covers only the z-free A--W
  subfamily);
- unchanged-primitive-first deletion after a Q/carrier edge except
  the source-first gauge of Result 51;
- a nonprimitive changed row followed by another row-changing edge;
- two row-changing edges before the first deletion;
- a history that first changes a checkpoint.

AK(3), AC, and stable AC remain open.

## 7. Independent replay

The dependency-free verifier
`tests/stable_ac/test_d_tail_one_edge_primitive_creation.py`:

- verifies the maps and inverses (3.3), (4.4);
- reproduces all six transformed words in (3.4);
- checks every cycle edge and cut assignment in the exact certificate;
- reproduces every N/G/P entry in (4.3);
- completely minimizes every graph-positive child;
- maps every primitive child back through the exact inverse coordinate;
- compares the resulting checkpoint/carrier/class triples with Result
  49's table.

The unbounded step is Lemmas 2.1--2.2; the replay certifies their
finite six-row hypotheses and exceptional tables.
