# Synchronized planarity for the four-germ Neuwirth link

## Purpose and scope

This note gives a finite, non-factorial criterion for the compatible
spherical rotations that occur in the two-generator case of
[`AK3_NEUWIRTH.md`](AK3_NEUWIRTH.md).  It proves specialized theorems only for
connected, loopless support graphs isomorphic to

\[
K_4,\qquad K_4-e,\qquad\text{or}\qquad C_4.
\]

The statements concern the exact word-realized presentation complex.  No
free or cyclic reduction is performed, no letter occurrences are identified,
and no conclusion is transported through an Andrews--Curtis move.  In
particular, the Neuwirth genus potential is not assumed to be an
Andrews--Curtis invariant.

The specialized theorem below is not the general Synchronized Planarity
theorem.  The latter is a separate polynomial-time fallback for loop-free
multigraphs with arbitrary support.  Inputs outside the three proved support
types must be reported as unsupported by the specialized criterion, not as
non-spherical and not as non-thickenable.

## The exact \(D,A,B\) dictionary

We retain the occurrence dictionary of `AK3_NEUWIRTH.md` literally.  For each
letter occurrence \(o_i\), let \(d_i\) and \(h_i\) be its departure and arrival
endpoints.  Write

\[
D=\{d_i,h_i:i\text{ is an occurrence}\}.
\]

This set \(D\) is the set denoted \(E\) in `AK3_NEUWIRTH.md` and in
Neuwirth's permutation notation; the new letter only avoids confusing that
endpoint set with the edge set of a graph.  The two fixed-point-free
involutions are

\[
B=\prod_i(d_i\ h_i)
\]

and, for every cyclic corner \(a_i a_{i+1}\) in one specified relator,

\[
A(h_i)=d_{i+1},\qquad A(d_{i+1})=h_i.
\]

Let

\[
V=\{x^+,x^-,y^+,y^-\}
\]

be the four generator germs, and let

\[
\tau=(x^+\ x^-)(y^+\ y^-)
\]

be the involution that exchanges the two germs of each unsigned generator.
Define the germ map \(\nu:D\to V\) occurrence by occurrence:

\[
\begin{array}{c|cc}
a_i & \nu(d_i)&\nu(h_i)\\ \hline
x   &x^+&x^-\\
X   &x^-&x^+\\
y   &y^+&y^-\\
Y   &y^-&y^+
\end{array}
\]

Thus

\[
\nu(Bd)=\tau(\nu(d)).
\]

The **support multigraph** \(G_A\) has vertex set \(V\).  Every
\(A\)-transposition \((d\ A(d))\) is one labeled edge with endpoint darts
\(d\) and \(A(d)\).  An \(A\)-orbit will therefore also be called an
\(A\)-edge.  The hypotheses in this note include

\[
\nu(d)\ne \nu(A(d))
\]

for every \(d\), so \(G_A\) is loopless, although it may have parallel edges.
For distinct \(u,v\in V\), write

\[
P_{uv}=\{e\in E(G_A):e\text{ has endpoints }u,v\},
\qquad
m_{uv}=|P_{uv}|.
\]

The simple support is obtained by replacing every nonempty \(P_{uv}\) by one
edge.

Write

\[
D_v=\nu^{-1}(v),\qquad n_v=|D_v|.
\]

Since \(B\) maps \(D_v\) bijectively to \(D_{\tau v}\),

\[
n_v=n_{\tau v}. \tag{2.0}
\]

A Neuwirth-compatible permutation \(C\) is a product of one cyclic rotation
\(C_v\) of the darts at every \(v\in V\).  The occurrence rule in
`AK3_NEUWIRTH.md` is equivalently

\[
C_{\tau v}=B\,C_v^{-1}\,B^{-1}=B\,C_v^{-1}\,B. \tag{2.1}
\]

In words, the rotation at the other end of a generator is the reversed
\(B\)-image of the first rotation.  The decision problem in this note is:

> Does \(G_A\) have a spherical rotation system satisfying (2.1)?

By the Euler dictionary in `AK3_NEUWIRTH.md`, a positive answer is exactly a
compatible \(C\) whose rotation surface has genus zero.  This note does not
repeat the separate proof that such a \(C\) is equivalent to an orientable
thickening of the exact presentation complex.

## Spherical \(K_4\) multigraphs

Fix the vertex labels \(0,1,2,3\) temporarily.  One tetrahedral rotation of
the simple \(K_4\) is

\[
\begin{aligned}
0&:(1,2,3),&
1&:(0,3,2),\\
2&:(0,1,3),&
3&:(0,2,1).
\end{aligned} \tag{3.1}
\]

The other is obtained by reversing all four cyclic orders.

### Theorem 3.1 (complete \(K_4\)-bundle classification)

Let \(G\) be a finite loopless labeled multigraph on
\(\{0,1,2,3\}\), and assume \(m_{uv}\ge 1\) for every \(u<v\).  A rotation
system \(\rho\) of \(G\) is spherical if and only if all of the following
conditions hold.

1. At every vertex \(u\), the darts belonging to each \(P_{uv}\) form one
   cyclic interval.  Hence \(\rho_u\) is a concatenation of three
   neighbor-blocks.
2. Replacing every \(P_{uv}\)-block by the symbol \(v\) gives (3.1) at all
   four vertices, or gives the simultaneous reversal of (3.1).
3. For every \(u<v\), if the linear order of the \(P_{uv}\)-block at \(u\)
   is
   \[
   (e_1,\ldots,e_{m_{uv}}),
   \]
   then its order at \(v\) is
   \[
   (e_{m_{uv}},\ldots,e_1).
   \]

Consequently, the exact number of labeled spherical rotation systems is

\[
2\prod_{u<v}m_{uv}!. \tag{3.2}
\]

#### Proof: necessity

Fix \(u,v\), and consider only the embedded subgraph consisting of the
\(m=m_{uv}\) parallel \(uv\)-edges.  The complement of these arcs in
\(S^2\) has \(m\) regions, interpreted as one region when \(m=1\); every
region meets \(u\) and \(v\) in the angular gaps between consecutive
\(uv\)-darts.

Let \(r,s\) be the other two vertices.  The simple support is \(K_4\), so an
\(rs\)-edge joins them without meeting a \(uv\)-edge.  Therefore \(r\) and
\(s\) lie in the same component \(R\) of the complement of the parallel
\(uv\)-edges.  Every edge from \(u\) or \(v\) to \(r\) or \(s\) also has its
interior in \(R\): after it leaves its endpoint through an angular gap, it
cannot change complementary regions without crossing a \(uv\)-edge.
Accordingly, all non-\(uv\) darts at \(u\) lie in the single angular gap
belonging to \(R\), and the same holds at \(v\).  The complementary cyclic
interval at each endpoint consists of all \(uv\)-darts.  This proves the
block condition.

All complementary regions other than \(R\) are empty digons.  Reading their
boundaries shows that consecutive \(uv\)-edges at \(u\) occur in the reverse
order at \(v\).  This proves condition 3.

Delete all but one edge from each parallel class.  The surviving embedded
simple graph is \(K_4\), and the block condition makes its vertex rotations
independent of which representatives were retained.  Starting with any
chosen rotation at vertex \(0\), the four triangular faces force the
rotations at the other three vertices.  This gives exactly (3.1) and its
simultaneous reversal, proving condition 2.

#### Proof: sufficiency

Embed the simple \(K_4\) using the selected tetrahedral rotation.  Replace
each simple \(uv\)-edge by a narrow ribbon and draw the labeled members of
\(P_{uv}\) across that ribbon in their prescribed linear order.  The order
seen from the other end is reversed, exactly as condition 3 requires.  The
six ribbons can be chosen with pairwise disjoint interiors.

Equivalently, consecutive members of every \(P_{uv}\) bound empty digons.
There are

\[
\sum_{u<v}(m_{uv}-1)=|E(G)|-6
\]

such digons, together with the four triangular macrofaces of the tetrahedral
embedding.  Hence

\[
F=|E(G)|-2,\qquad
\chi=4-|E(G)|+F=2.
\]

The resulting orientable rotation surface is connected and has Euler
characteristic two, so it is \(S^2\).

For each of the two macro-rotations, an arbitrary linear order may be chosen
independently in every parallel class, and the other endpoint order is then
forced.  The block boundaries distinguish the first and last member of each
linear order, so there is no cyclic overcount.  This proves (3.2).
\(\square\)

### Parallel copies on both sides of a skeleton edge

The block statement is local at the endpoints; it does not put all parallel
copies on one side of a chosen physical skeleton edge.  Suppose a selected
representative \(s\in P_{uv}\) has position \(k\) in the total block order

\[
(e_1,\ldots,e_{k-1},s,e_{k+1},\ldots,e_m).
\]

The first \(k-1\) copies lie in one of the two triangular faces incident to
\(s\), and the remaining \(m-k\) copies lie in the other.  Both sets may be
nonempty.  At the other endpoint the total order reverses.  Thus the
intrinsic datum is one total linear order; choosing a particular physical
copy as a skeleton merely cuts that order into the two sides.

## Signed ranks and the \(B\)-reversal equations

Theorem 3.1 replaces six factorial order choices by six all-different rank
families coupled through modular equations.

Fix the first tetrahedral macro-rotation (3.1).  This loses no solutions:
reflecting a spherical embedding reverses every vertex rotation, and if
(2.1) holds then

\[
B(C_v^{-1})^{-1}B=B C_v B=(B C_v^{-1}B)^{-1},
\]

so the reflected rotations still satisfy (2.1).

For each unordered pair \(\{u,v\}\), choose one endpoint as the reference
endpoint.  Give every labeled edge \(e\in P_{uv}\) a rank

\[
z_e\in\{0,\ldots,m_{uv}-1\}. \tag{4.1}
\]

Require the ranks in \(P_{uv}\) to be pairwise distinct.  Because there are
exactly \(m_{uv}\) variables and \(m_{uv}\) available values, this
all-different condition says precisely that the ranks form a permutation.

Let \(n_v=\deg(v)\).  For the fixed macro-rotation, let \(b_{v,u}\) be the
number of darts in the blocks preceding the \(P_{uv}\)-block at \(v\).  If
\(d\) is the dart of \(e\in P_{uv}\) at \(v\), define its within-block rank

\[
r_d(z_e)=
\begin{cases}
z_e,&v\text{ is the reference endpoint of }P_{uv},\\
m_{uv}-1-z_e,&v\text{ is the other endpoint},
\end{cases}
\]

and its endpoint slot

\[
P_d(z_e)=b_{v,u}+r_d(z_e)\pmod {n_v}. \tag{4.2}
\]

For each vertex, the all-different constraints make the slot values of its
incident darts a bijection with \(\mathbb Z/n_v\).  Increasing slots give the
vertex rotation.  Formula (4.2) builds in both the macro-block order and the
reversal of each parallel class.

### Lemma 4.1 (the two cyclic phases)

Let \(g\in\{x,y\}\), put \(v=g^+\), and let \(\tau v=g^-\).  The rotations
defined by endpoint slots satisfy the Neuwirth reversal (2.1) if and only if
there is one phase

\[
s_g\in\mathbb Z/n_v
\]

such that, for every \(d\in D_v\),

\[
P_d(z_{e(d)})+
P_{Bd}(z_{e(Bd)})+
s_g
\equiv 0\pmod {n_v}. \tag{4.3}
\]

Here \(e(d)\) is the \(A\)-edge containing \(d\).  It is enough to write
(4.3) once for each \(B\)-transposition.

#### Proof

Two cyclic orders are reverses under \(B\) exactly when some choice of cyclic
origins makes the slot of \(Bd\) equal to the negative of the slot of \(d\).
With origins fixed by the written schemes, this equality may differ by one
constant \(\kappa_g\), independent of \(d\):

\[
P_{Bd}(z_{e(Bd)})\equiv
\kappa_g-P_d(z_{e(d)})\pmod {n_v}.
\]

Taking \(s_g=-\kappa_g\) gives (4.3).  Conversely, (4.3) says exactly that
the \(B\)-image reverses the increasing cyclic slot order.  Applying the
same equation to \(Bd\) duplicates the same \(B\)-transposition and adds no
condition.
\(\square\)

Thus there are only two phase variables, \(s_x\) and \(s_y\), rather than one
independent alignment for every edge or block.

### Lemma 4.2 (the contracted constraint cycles)

Construct a multigraph \(H_{A,B}\) as follows:

- its vertices are the \(A\)-orbits, equivalently the labeled edges of
  \(G_A\);
- every \(B\)-transposition \(\{d,Bd\}\) gives one constraint edge joining
  \(e(d)\) to \(e(Bd)\).

Then \(H_{A,B}\) is 2-regular, with loops and parallel constraint edges
allowed.  Its connected components are in canonical bijection with the
specified cyclic relators.  For a balanced two-generator presentation with
two nonempty relators, it is the disjoint union of two cycles.

#### Proof

Every \(A\)-orbit contains two darts, and each dart belongs to exactly one
\(B\)-transposition.  Hence every contracted \(A\)-orbit has degree two,
counting a constraint loop twice.

Within one relator, traversal

\[
d_i\xrightarrow{B}h_i\xrightarrow{A}d_{i+1}
\]

moves from occurrence \(i\) to the next occurrence, with the index taken
cyclically in that relator.  Neither \(A\) nor \(B\) joins endpoints from
different relators.  The alternating \(A,B\)-components are therefore
exactly the relator cycles, and contracting the \(A\)-pairs preserves those
components.  A one-letter relator becomes a constraint loop and a two-letter
relator may become a 2-cycle; both remain covered by the 2-regular
multigraph statement.
\(\square\)

### Theorem 4.3 (rank propagation is exact for \(K_4\))

Assume the simple support of \(G_A\) is \(K_4\).  A
Neuwirth-compatible spherical rotation exists if and only if there are

- phases \(s_x,s_y\);
- ranks satisfying (4.1);
- every equation (4.3); and
- the all-different condition in every \(P_{uv}\).

For fixed phases, all solutions can be found without enumerating a
factorial family: on each component of \(H_{A,B}\), choose one seed
\(A\)-edge \(e\), try its possible ranks, and propagate uniquely around the
cycle using (4.3).  Retain exactly the assignments that close consistently
and satisfy the per-class all-different constraints.  With two relators,
combine one retained assignment from each cycle and reject precisely when
their used-rank sets overlap in some parallel class.  An accepted combination
must additionally have

\[
\left|\bigcup_{\text{two relator cycles}}
  \{z_e:e\in P_{uv}\text{ on that cycle}\}\right|
=m_{uv} \tag{4.4}
\]

for every class \(P_{uv}\).  Since every class edge lies on exactly one of
the two cycles, (4.4) follows mathematically from global distinctness, but it
is an explicit completeness condition on a finite certificate.

#### Proof

For a constraint edge represented by \(\{d,Bd\}\), suppose
\(z_{e(d)}\) is known.  Equation (4.3) determines the required endpoint slot
of \(Bd\).  The slot map \(P_{Bd}\) is injective on the finite rank domain,
so there is at most one possible value of \(z_{e(Bd)}\).  If the required
slot is outside its image, that seed fails.  Repeating this step walks around
the entire 2-regular component.  The final constraint either agrees with the
seed or rejects it.  A constraint loop simply tests its seed, and both
constraint edges of a 2-cycle must be tested.

Every solution of (4.3) appears in this propagation because its seed value
is among the values tried and every subsequent value is forced.  Conversely,
every closed propagation satisfies all phase equations on that component.
Once the two phases are fixed, the only constraints shared by distinct
relator cycles are the all-different rank conditions.  Enforcing uniqueness
within each cycle, disjoint used-rank sets between the two cycles, and the
cardinality check (4.4) is therefore equivalent to the global all-different
condition.  Since a class has \(m_{uv}\) variables and a domain of size
\(m_{uv}\), global distinctness proves (4.4), and (4.4) proves that every
rank is used exactly once.

Given a compatible spherical rotation, Theorem 3.1 supplies its macro-order
and the six reversed linear block orders.  Reflect globally if necessary,
read their ranks, and apply Lemma 4.1 to obtain the phases.  This proves
necessity.  Conversely, ranks and phases satisfying the displayed
conditions reconstruct the rotations of Theorem 3.1 through (4.2);
Lemma 4.1 gives Neuwirth compatibility, and Theorem 3.1 gives sphericity.
\(\square\)

For \(K_4\), the slot maps are genuinely signed affine maps
\(z\mapsto b+z\) or \(z\mapsto b+m-1-z\).  The \(K_4-e\) extension below
has the same modular phase equations and the same cycle propagation, but the
split central class uses injective, piecewise slot lookup maps after a finite
cut choice.  It should not be described as one unqualified system of linear
congruences.

## Spherical \(K_4-e\) multigraphs

Let the simple support be \(K_4-cd\), where \(c,d\) are the two degree-two
vertices.  Let \(a,b\) be the degree-three vertices.  The class \(P_{ab}\) is
the **central class**.  Put \(m=m_{ab}\).

There are \(m+2\) \(\{a,b\}\)-bridges:

1. every individual central edge in \(P_{ab}\) is a trivial bridge;
2. \(\mathsf C\) is the nontrivial bridge consisting of \(c\) and all edges
   in \(P_{ac}\cup P_{bc}\);
3. \(\mathsf D\) is the analogous bridge through \(d\).

The symbols \(\mathsf C,\mathsf D\) name bridges and are unrelated to
Neuwirth's rotation permutation \(C\).

### Lemma 5.1 (bridge order)

In every spherical embedding, the darts of each \(\{a,b\}\)-bridge form one
interval at \(a\) and one interval at \(b\), and the cyclic order of the
bridges at \(b\) is the reverse of their order at \(a\).  Conversely, every
cyclic bridge order at \(a\), with its reverse at \(b\), can be realized
spherically after choosing planar embeddings of \(\mathsf C\) and
\(\mathsf D\) in their bridge discs.

#### Proof

First consider \(P_{ac}\).  After deleting \(a,c\), the remaining vertices
\(b,d\) are joined by every edge of the nonempty class \(P_{bd}\).  Apply the
complementary-region argument from Theorem 3.1 to the parallel
\(ac\)-edges: \(b,d\), and hence all non-\(ac\) material, lie in one
complementary region.  Therefore the \(P_{ac}\)-darts form one cyclic block
at both endpoints, with reversed endpoint orders.  The same argument, using
the opposite leg that joins the two remaining vertices, applies to

\[
P_{bc},\qquad P_{ad},\qquad P_{bd}. \tag{5.0}
\]

The only incidences of bridge \(\mathsf C\) at \(a,b\) are respectively the
\(P_{ac}\)- and \(P_{bc}\)-blocks, so \(\mathsf C\) has one interval at each
pole.  Similarly, \(\mathsf D\) has the \(P_{ad}\)- and \(P_{bd}\)-blocks.
Every central edge is a singleton interval.  This proves bridge
consecutivity without assuming it.

Now delete all but one edge from each of the four leg classes in (5.0).
The two nontrivial bridges become the paths \(a-c-b\) and \(a-d-b\).
Suppress the degree-two vertices \(c,d\).  The resulting embedded graph is a
dipole consisting of the \(m\) central edges and one virtual edge for each
of \(\mathsf C,\mathsf D\).  Consecutive edges of an embedded dipole bound
empty digons, so their cyclic orders at \(a\) and \(b\) are opposite.  Since
deletion did not change the cyclic order of the bridge intervals, the
original bridge order at \(b\) is the reverse of its order at \(a\).

For the converse, draw \(m+2\) disjoint strips between the two boundary
circles in the prescribed opposite orders.  A trivial strip contains its
central edge.  The graph \(\mathsf C\) consists of two parallel-edge bundles
meeting at \(c\); it has a planar embedding in a disc with its \(a\)- and
\(b\)-incidences in the two prescribed boundary intervals.  The same holds
for \(\mathsf D\).  Inserting those two disc embeddings into their strips
produces the claimed spherical embedding.
\(\square\)

Inside \(\mathsf C\), the \(P_{ac}\)-darts form a block and reverse between
\(a\) and \(c\), while the \(P_{bc}\)-darts form a block and reverse between
\(b\) and \(c\).  The two blocks concatenate at \(c\).  Their cyclic
two-block order has no further orientation choice: reversing a chosen
linear order on either leg is already among the arbitrary permutations for
that leg.  The same description applies to \(\mathsf D\).

### Theorem 5.2 (complete \(K_4-e\) classification)

Fix an orientation of the sphere, read the bridge order at \(a\), and use
\(\mathsf C\) as its cyclic origin.  Every spherical bridge order is written
uniquely as

\[
\mathsf C,\quad
L[:i],\quad
\mathsf D,\quad
L[i:] \qquad (0\le i\le m), \tag{5.1}
\]

where \(L=(e_1,\ldots,e_m)\) is a linear order of the labeled central edges.
The bridge order at \(b\) is the reverse cyclic order.  Together with
arbitrary reversed endpoint orders in the four leg classes

\[
P_{ac},P_{bc},P_{ad},P_{bd},
\]

these data describe every spherical rotation system, and only spherical
rotation systems.

The number of labeled spherical rotation systems is

\[
(m+1)!\,
m_{ac}!\,m_{bc}!\,m_{ad}!\,m_{bd}!. \tag{5.2}
\]

#### Proof

Lemma 5.1 reduces a spherical embedding to a cyclic permutation of the two
nontrivial bridges and the \(m\) labeled trivial bridges.  Start reading at
\(\mathsf C\).  The central edges encountered before \(\mathsf D\) form a
prefix; those encountered after \(\mathsf D\) form a suffix.  Concatenating
them defines \(L\), and the prefix length defines \(i\).  Both are uniquely
recoverable from the oriented cyclic order, proving uniqueness in (5.1).
The reverse bridge order at \(b\) is forced by Lemma 5.1.

Conversely, (5.1), its reverse at \(b\), and planar bridge-disc embeddings
give a spherical embedding by the converse part of Lemma 5.1.  The discussion
of the two leg bundles inside each nontrivial bridge proves that the four
leg permutations are independent and complete.

Fixing the orientation only tells us which direction is used to read the
cyclic order; (5.1) does **not** quotient reflected rotation systems.  Both
an oriented rotation and its global reflection occur in the family,
generally as different pairs \((L,i)\).  For example, when \(m=1\), the
cuts \(i=0\) and \(i=1\) are the two reflected rotations of the simple
\(K_4-e\).  There is no additional binary reflection flag because both
orders are already present in the \((L,i)\) family.  Fixing \(\mathsf C\)
removes cyclic rotation.  There are \((m+1)!\) cyclic orders of the remaining
\(m+1\) bridge items after that origin is fixed, and the independent leg
orders give (5.2).
\(\square\)

The central class need not be a block.  For example, the valid bridge order

\[
\mathsf C,e_1,\mathsf D,e_2,\ldots,e_m
\]

when \(m\ge2\) places central edges in both complementary intervals between
the two nontrivial bridges.  Applying the \(K_4\) one-block rule to this
central class would therefore create false negatives.

### Slot schemes and rank propagation for \(K_4-e\)

For each cut \(i\in\{0,\ldots,m\}\), define one slot scheme \(Q_i\).  Let the
central rank \(z_e\) be the position of \(e\) in \(L\).  At \(a\), expand
(5.1) into

\[
P_{ac},\quad
L[:i],\quad
P_{ad},\quad
L[i:].
\]

At \(b\), start again at the \(\mathsf C\)-interval and expand the reverse
bridge order:

\[
P_{bc},\quad
\operatorname{rev}(L[i:]),\quad
P_{bd},\quad
\operatorname{rev}(L[:i]).
\]

At \(c\), concatenate the reversed endpoint blocks for \(P_{ac}\) and
\(P_{bc}\); do the analogous thing at \(d\).  These expanded sequences
define, for every incident dart \(d\), an injective slot map.  Here
\(\operatorname{class}(d)\) is the parallel class
\(P_{\nu(d),\nu(A(d))}\) of the \(A\)-edge containing \(d\):

\[
P_d^{Q_i}:\{0,\ldots,|\operatorname{class}(d)|-1\}
\longrightarrow \mathbb Z/\deg(\nu(d)).
\]

The images of the incident class maps are disjoint and partition all slots
at each vertex.  The four leg maps have the signed affine form of (4.2).
The central maps are affine on the two rank intervals separated by \(i\),
with gaps occupied by the two nontrivial bridge blocks.

Replace \(P_d\) by \(P_d^{Q_i}\) in (4.3).  Every map remains injective, so
the proof of Theorem 4.3 applies verbatim: a known rank determines at most one
rank across a constraint edge by inverse slot lookup.  Enumerating the
\(m+1\) cuts, the two phases, and the seed ranks on the two relator cycles is
therefore necessary and sufficient.  No permutation \(L\) is enumerated;
the all-different central ranks encode it.

## Spherical \(C_4\) multigraphs

### Theorem 6.1 (complete \(C_4\) classification)

Let \(G\) be a loopless multigraph whose simple support is a 4-cycle, with
every support class nonempty.  A rotation system is spherical if and only if
every parallel class is one block and its orders at the two endpoints are
reversed.

There is no additional macro-rotation choice.  Consequently, the labeled
spherical rotations are counted by

\[
\prod_{uv\in E(C_4)}m_{uv}!. \tag{6.1}
\]

#### Proof

Fix a support edge \(uv\).  After deleting \(u,v\), the other two vertices
are joined by the opposite edge of the 4-cycle.  The complementary-region
argument from the necessity proof of Theorem 3.1 therefore applies:
all non-\(uv\) material lies in one gap of the parallel \(uv\)-edges, so
\(P_{uv}\) is a block, and the empty digons force reversed endpoint orders.

After all blocks are contracted, every support vertex has degree two.  A
cyclic order of two neighbor symbols is unique, so the simple \(C_4\) has no
remaining macro-rotation choice.  Conversely, embed the simple cycle and
replace every edge by a narrow parallel ribbon with the prescribed reversed
orders.  This is spherical.  The independent linear orders in the four
classes give (6.1).
\(\square\)

Choose either written concatenation of the two neighbor-blocks at every
vertex; cyclically they describe the same macro-order.  The usual ranks and
reversed endpoint ranks define injective slot maps.  Equations (4.3), the two
phase enumeration, and the relator-cycle propagation of Theorem 4.3 are
therefore necessary and sufficient with a single \(C_4\) slot scheme.

## Relation to general Synchronized Planarity

The exact problem above is an instance of the Synchronized Planarity problem
of Bläsius, Fink, and Rutter.  Their input is a loop-free multigraph together
with **pipes** that pair equal-degree vertices by bijections of incident
edges.  A pipe is satisfied when the paired rotations are opposite under its
bijection.

For the Neuwirth link, use \(G_A\) as their multigraph.  For \(v\in V\), let
\(E(v)\) denote the set of labeled \(A\)-edges incident with \(v\).  Because
\(G_A\) is loopless, each edge in \(E(v)\) has a unique dart in \(D_v\).
Thus, for \(g\in\{x,y\}\), the map \(d\mapsto Bd\) induces a well-defined
bijection

\[
\phi_g:E(g^+)\longrightarrow E(g^-),\qquad
e(d)\longmapsto e(Bd).
\]

Its inverse is induced by \(B\) in the other direction; looplessness also
prevents two darts at one germ from naming the same incident edge.
The two pipes are

\[
(x^+,x^-,\phi_x),\qquad (y^+,y^-,\phi_y).
\]

They form a matching on the four germ vertices, as required.  Their
opposite-rotation condition is exactly (2.1).  There are no additional
Q-constraints.  Thus the general theorem decides the same compatibility
question.  Theorem 9 of the official ESA paper gives an \(O(m^2)\)-time
algorithm, where \(m\) is the number of multigraph edges.  Its full proof
appears in the 2023 *ACM Transactions on Algorithms* journal version cited
below.

The specialized results in this note do something narrower:

- Theorems 3.1, 5.2, and 6.1 replace the general planar-embedding machinery
  by explicit schemes for the only three connected supports in scope.
- Lemma 4.2 uses the exact presentation dictionary to exploit the two
  relator cycles.
- Theorem 4.3 reduces the remaining P-node permutations to seed propagation
  and six all-different rank families.

This is not plain 2-SAT.  A parallel bond permits an arbitrary permutation,
not only a binary flip.  Nor is an independent consecutive-ones or PQ-tree
test at each pipe sufficient: local block contiguity alone does not enforce
the reversed orders shared at the two ends of every \(A\)-edge class.
Simultaneous PQ-ordering, and in full generality Synchronized Planarity, is
the appropriate general framework.

## Fail-closed boundary

The specialized criterion may return YES or NO only after all of the
following have been established for the exact input:

1. the endpoint data are exactly the \(D,A,B\) data above;
2. the \(A\)-link is loopless;
3. the support is connected and isomorphic to \(K_4\), \(K_4-e\), or \(C_4\);
4. every slot map is injective, and its images partition every vertex's
   slots;
5. each \(B\)-transposition contributes exactly one modular equation;
6. constraint loops and 2-cycles are checked rather than simplified away;
7. the per-cycle and cross-cycle rank tests together enforce global
   all-different constraints and verify union cardinality
   \(m_{uv}\) in every class;
8. before returning NO, the search has exhausted every pair
   \((s_x,s_y)\in\mathbb Z/n_{x^+}\times\mathbb Z/n_{y^+}\), every seed
   rank on every component of \(H_{A,B}\), every retained component-solution
   combination, and, for \(K_4-e\), every cut \(i=0,\ldots,m_{ab}\);
   \(K_4\) uses the one fixed macro-orientation justified by global
   reflection, while \(C_4\) has its single scheme; and
9. an accepted witness reconstructs the four rotations, replays (2.1), and
   independently has spherical Euler characteristic.

Any other loopless support, including a disconnected one, must return an
unsupported verdict from the specialized criterion and be routed to a proved
general Synchronized Planarity implementation.  A disconnected planar link
can be placed in one sphere, but its rotation system canonically caps its
components separately; relative nesting in the common sphere is not recorded
by the component rotations.  The connected cellular face arguments in
Theorems 3.1, 5.2, and 6.1 must not be copied to that case.  The two
\(B\)-pipes may also couple rotations belonging to different link
components.

The cited general theorem is stated for loop-free multigraphs.  A link with
an \(A\)-loop remains unsupported: it is outside both this specialized proof
and that statement as used here unless a separate, proved loop
transformation is supplied.

A positive compatible spherical rotation remains subject to the independent
regular-neighbourhood validation required by the AK(3) project.  A negative
applies only to the exact word-realized presentation complex tested.  Neither
verdict supplies an Andrews--Curtis invariant.

## Independently census-derived support inventory

An independent finite census of the known 1,000-state AK(3) height-17
component reported the following support counts:

\[
720\ K_4,\qquad
278\ K_4-e,\qquad
2\ C_4.
\]

The \(278\) cases split into \(139\) missing the \(x^+x^-\) edge and \(139\)
missing the \(y^+y^-\) edge.  These are census outputs, not consequences of
the theorems in this note, and none of the proofs above depends on them.
They must be re-authenticated by the later component certificate before they
are used as result claims.

## Proof-audit status

A hostile review specifically attempted to produce:

- a \(K_4\) embedding with a noncontiguous parallel class;
- a missing \(K_4-e\) scheme with a genuinely split central class;
- an extra flip inside either nontrivial \(K_4-e\) bridge;
- a phase assignment not represented by (4.3); and
- a rank solution lost by the contracted-cycle propagation.

No counterexample was found for the connected loopless support types stated
here.  The split-central-class objection is real but is exactly the cut
parameter \(i\) in (5.1); it refutes a naive extension of the \(K_4\) block
rule, not Theorem 5.2.  The review also identified implementation hazards
that are retained in the fail-closed list: duplicate \(B\)-pair equations,
constraint loops, 2-cycles, repeated visits to the same rank variable, and
slot maps that fail to partition a vertex, as well as a false NO from
incomplete phase, cut, seed, or component-combination enumeration.

No theorem is asserted for any support outside the stated scope.

## Sources

1. L. Neuwirth, “An algorithm for the construction of 3-manifolds from
   2-complexes,” *Proceedings of the Cambridge Philosophical Society* 64
   (1968), 603--614.  The exact occurrence dictionary and its application
   here are proved in [`AK3_NEUWIRTH.md`](AK3_NEUWIRTH.md).
2. T. Bläsius, S. D. Fink, and I. Rutter, “Synchronized Planarity with
   Applications to Constrained Planarity Problems,” in *29th Annual European
   Symposium on Algorithms (ESA 2021)*, LIPIcs 204, Article 19, especially
   the definition on pp. 19:3--19:4 and Theorem 9.
   [Official paper and DOI](https://doi.org/10.4230/LIPIcs.ESA.2021.19).
3. T. Bläsius, S. D. Fink, and I. Rutter, “Synchronized Planarity with
   Applications to Constrained Planarity Problems,” *ACM Transactions on
   Algorithms* 19(4) (2023), Article 34, 34:1--34:23.  This is the full
   journal version.
   [Official journal DOI](https://doi.org/10.1145/3607474);
   [author preprint](https://arxiv.org/abs/2007.15362).
