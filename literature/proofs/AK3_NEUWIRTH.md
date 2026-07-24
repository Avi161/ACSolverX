# The Neuwirth criterion used for the AK(3) certificate

## Scope and exact inputs

This note concerns the canonical one-vertex presentation complex \(K_P\) of a
finite **balanced** presentation

\[
P=\langle g_1,\ldots,g_n\mid w_1,\ldots,w_n\rangle .
\]

Every \(w_j\) is a specified nonempty cyclic word, and every \(g_k\) occurs in
at least one word.  The cells and attaching maps below are those of this exact
word-realized CW complex.  In particular, adjacent inverse letters are not
cancelled, words are not freely or cyclically reduced, and repeated
occurrences are never identified.

The two later certificate inputs are, verbatim,

\[
\begin{aligned}
P_{\mathrm{AK3}}
  &=\langle x,y\mid \mathtt{xxxYYYY},\mathtt{xyxYXY}\rangle,\\
P_{\mathrm{orb2}}
  &=\langle x,y\mid \mathtt{YYXXyx},\mathtt{YYYxyXX}\rangle ,
\end{aligned}
\]

where \(X=x^{-1}\) and \(Y=y^{-1}\).  Each has six unsigned occurrences of
\(x\) and seven of \(y\).  No thickenability decision, and no value of the
potential defined below, is asserted here.

Throughout, permutations act on the left and products are evaluated
right-to-left:

\[
(PQ)(e)=P(Q(e)).
\]

For a permutation \(Q\), \(|Q|\) denotes its number of cycles, including
one-cycles.

## The occurrence dictionary

Give every position in every relator its own occurrence \(o_i\), and let
\(a_i\in\{g_1^{\pm1},\ldots,g_n^{\pm1}\}\) be the letter at that position.
The indices immediately following an occurrence are taken cyclically within
the same relator.  Associate two distinct elements of a set \(E\) to \(o_i\):

- \(d_i\), the endpoint from which the oriented relator boundary departs
  along \(a_i\);
- \(h_i\), the endpoint at which it arrives.

Thus \(|E|\) is twice the total word length.  Define two fixed-point-free
involutions on \(E\) by

\[
B=\prod_i(d_i\ h_i)
\]

and, for every cyclic corner \(a_i a_{i+1}\),

\[
A(h_i)=d_{i+1},\qquad A(d_{i+1})=h_i.
\]

The \(B\)-transpositions are disjoint, as are the \(A\)-transpositions over
all corners.  The involution \(B\) follows one letter-occurrence through its
generator tube; \(A\) crosses the corner from one occurrence to the next.

For an unsigned generator \(g\), occurrence \(o_i\) contributes the following
endpoint at the positive end of the oriented \(g\)-cell:

\[
p_i=
\begin{cases}
d_i,&a_i=g,\\
h_i,&a_i=g^{-1}.
\end{cases}
\]

Its endpoint at the negative end is \(B(p_i)\).  Choose one cyclic order

\[
(p_1\ p_2\ \cdots\ p_m)
\]

at the positive end of \(g\).  The cycle at the negative end is required to
be

\[
(B(p_m)\ B(p_{m-1})\ \cdots\ B(p_1)).
\]

The product of these two cycles over all unsigned generators is \(C\).
Consequently \(|C|=2n\).  This reversal is essential: the two attaching discs
of an orientable 1-handle inherit opposite boundary orientations.  It is the
occurrence-language version of Neuwirth's

\[
(e_i^1\,e_i^2\,\ldots\,e_i^{r(i)})
(\bar e_i^{r(i)}\,\ldots\,\bar e_i^2\,\bar e_i^1)
\]

on pp. 605--606.

Conversely, an orientation-compatible ordering of the incident 2-cell strips
about the two ends of an oriented generator has exactly this form: read the
positive attaching disc in its boundary orientation and transport its
endpoints through the handle; the boundary orientation on the other disc
reverses the transported list.  Hence one positive cyclic order per unsigned
generator determines, and is determined by, Neuwirth's compatible local
ordering, modulo rotation of each written cycle.

### A two-letter corner

Suppose two consecutive positions in an exact relator are
\(\mathtt{xY}=xy^{-1}\), with occurrences \(o_i,o_{i+1}\).  The corner factor
of \(A\) is

\[
(h_i\ d_{i+1}).
\]

At the positive \(x\)-end, \(o_i\) contributes \(d_i\), and its negative
endpoint is \(B(d_i)=h_i\).  At the positive \(y\)-end, the inverse occurrence
\(o_{i+1}\) contributes \(h_{i+1}\), and its negative endpoint is
\(B(h_{i+1})=d_{i+1}\).  Thus the displayed \(A\)-edge joins precisely the
arrival of the \(x\)-traversal to the departure of the following
\(y^{-1}\)-traversal.  Even if the two letters cancel algebraically, these are
still two occurrences and this corner remains in \(A\).

## The rotation surface and the Euler equation

For a compatible \(C\), form the ribbon graph whose darts are \(E\), whose
edge involution is \(A\), and whose cyclic order at each vertex is a cycle of
\(C\).  Thicken its vertices to oriented discs and its \(A\)-pairs to
untwisted edge bands, then cap every boundary component with a disc.  Denote
the resulting closed orientable surface by \(\Sigma_C\).

Let

\[
L(C)=\#\operatorname{Orb}\langle A,C\rangle .
\]

These orbits are exactly the connected components of the underlying link
graph, hence of \(\Sigma_C\).

**Lemma 1 (Euler dictionary).**  The numbers of vertices, edges, and faces of
the induced cell structure on \(\Sigma_C\) are respectively

\[
|C|,\qquad |A|,\qquad |AC|.
\]

Consequently,

\[
\chi(\Sigma_C)=|C|-|A|+|AC|
\]

and, if the component genera are \(q_1,\ldots,q_{L(C)}\),

\[
\sum_{\ell=1}^{L(C)}q_\ell
  =\frac{2L(C)-\chi(\Sigma_C)}2
  =\frac{|A|-|C|+2L(C)-|AC|}{2}.
\]

**Proof.**  A cycle of the vertex rotation \(C\) is one ribbon-graph vertex.
Because \(A\) is a fixed-point-free involution, each of its cycles is one
edge.  To trace an oriented boundary component of the ribbon thickening,
start at \(e\), move around its vertex to \(C(e)\), and cross the edge band to
\(A(C(e))\).  Thus the boundary, and hence the cap that becomes a face, is a
cycle of \(AC\).  The Euler formula follows.  Each component is a closed
orientable surface, so
\(\chi(\Sigma_C)=\sum_\ell(2-2q_\ell)\), which gives the final equality.
\(\square\)

In particular, the displayed defect is always a nonnegative even integer.
When the link graph is connected, \(L(C)=1\), and \(\Sigma_C\) is a sphere
exactly when

\[
|A|-|C|+2=|AC|. \tag{E}
\]

There is no face-convention ambiguity here.  The products \(AC\) and \(CA\)
are conjugate:

\[
CA=A^{-1}(AC)A
\]

because \(A^{-1}=A\); hence they have the same cycle count.  This observation
does **not** make the boundary-transitivity expressions interchangeable.
Although \(BC\) and \(CB\) are themselves conjugate, the two groups
\(\langle AC,BC\rangle\) and \(\langle AC,CB\rangle\) keep the same first
generator and need not have the same orbits.

For example, take the exact one-relator word \(\mathtt{xxX}\), number its
occurrences \(0,1,2\), and set

\[
\begin{aligned}
A&=(h_0\ d_1)(h_1\ d_2)(h_2\ d_0),\\
B&=(d_0\ h_0)(d_1\ h_1)(d_2\ h_2),\\
C&=(d_0\ h_2\ d_1)(h_1\ d_2\ h_0).
\end{aligned}
\]

The second cycle of \(C\) is the reversed \(B\)-image of the first.
With the right-to-left convention,

\[
\begin{aligned}
AC&=(h_0\ d_2\ d_1\ h_2)(d_0)(h_1),\\
BC&=(d_0\ d_2)(h_0\ d_1)(h_1\ h_2),\\
CB&=(d_0\ h_1)(h_0\ h_2)(d_1\ d_2).
\end{aligned}
\]

Thus
\(\langle AC,BC\rangle\) has one orbit, while
\(\langle AC,CB\rangle\) has the two orbits

\[
\{d_0,h_1\},\qquad \{h_0,d_1,d_2,h_2\}.
\]

This also has \(|A|=3\), \(|C|=2\), and \(|AC|=3\), so (E) holds.
Neuwirth's Theorem 1 on p. 605 prints \(CB\); Theorem 2 on p. 606 and the
geometric proof on pp. 610--611 use \(BC\).  The \(BC\) expression used for
boundary audits in this project is derived rather than inferred
from Neuwirth's unstated permutation-product convention.  With this note's
right-to-left convention, a boundary trace on the 0-handle first follows the
local rotation \(C\) and then crosses a corner by \(A\), giving \(AC\).  On the
lateral boundary of a generator 1-handle it first follows \(C\) and then
crosses the occurrence strip by \(B\), giving \(BC\).  The orbits of
\(\langle AC,BC\rangle\) therefore trace the connected pieces of the
complement used on pp. 610--611.  The printed \(BC/CB\) discrepancy is
recorded, not silently normalized.

## Neuwirth genus potential

Let \(\mathcal C(P)\) be the finite set of all compatible permutations \(C\)
obtained from the positive-end cyclic orders above, and define

\[
\gamma_N(P)=
\min_{C\in\mathcal C(P)}
\frac{|A|-|C|+2L(C)-|AC|}{2}. \tag{1}
\]

By Lemma 1, the quantity minimized in (1) is the sum of the genera of the
components of \(\Sigma_C\).  Therefore \(\gamma_N(P)\) is a nonnegative
integer.  It is data of the exact word-realized presentation complex.  It is
a presentation-complex potential, not an Andrews--Curtis invariant available
to this argument: no AC-invariance theorem is proved or assumed, and it must
be recomputed after an Andrews--Curtis move.  In particular, neither its value
nor a negative thickenability verdict may be transported along an AC path
without a separate theorem.

## The connected-link thickenability theorem

**Theorem 2 (Euler-only Neuwirth criterion).**  Let \(P\) satisfy the scope
hypotheses above, and suppose its link graph is connected.  Then the exact
presentation complex \(K_P\) embeds in an orientable PL 3-manifold if and only
if there is a compatible occurrence ordering \(C\) satisfying (E).
Equivalently,

\[
K_P\text{ is orientably thickenable}
\quad\Longleftrightarrow\quad
\gamma_N(P)=0.
\]

The transitivity of \(\langle AC,BC\rangle\) is not an additional
thickenability condition.  In Neuwirth's balanced setting it is the
additional condition that the boundary of the constructed regular
neighbourhood be connected, hence a single 2-sphere that can be capped by one
3-cell.

**Proof: necessity.**  Suppose \(K_P\) is PL embedded in an orientable
3-manifold.  Take a sufficiently small regular ball \(R\) about its unique
vertex, transverse to the incident cells.  The intersection

\[
F=K_P\cap\partial R
\]

is the link graph embedded in the oriented 2-sphere \(\partial R\).
The sphere orientation gives a cyclic order at each of the two ends of every
generator.  Transport through an oriented regular neighbourhood of the
generator 1-cell identifies the endpoints by \(B\), and the induced
orientations on its two attaching discs are opposite; hence the two cycles
have exactly the reversal prescribed in the occurrence dictionary.  The
corners of the original, unreduced attaching words give exactly the
\(A\)-edges.

The link is connected by hypothesis.  Its embedding in the sphere realizes
the compatible rotation system \(C\), and its complementary discs are traced
by \(AC\).  Euler's formula for \(\partial R\) is therefore
\(|C|-|A|+|AC|=2\), which is (E).

**Proof: sufficiency and the regular neighbourhood.**  Suppose a compatible
\(C\) satisfies (E).  Lemma 1 identifies the associated rotation surface
\(\Sigma_C\) with \(S^2\).  Realize the link graph \(F\) cellularly on the
boundary of a PL 0-handle \(H^0\cong B^3\), with the prescribed rotations,
and cone its local corner pieces to an interior point.  This is the vertex
piece of \(K_P\).

For each generator \(g\), choose disjoint small discs \(D_g^+\) and \(D_g^-\)
about the corresponding positive and negative vertices of \(F\), and attach
an orientable 1-handle

\[
H_g^1=D^2\times[-1,1]
\]

along them.  Its generator core is
\(\{0\}\times[-1,1]\).  In a cross-sectional disc, draw one radial page for
each incident occurrence.  The page beginning at \(p_i\) is continued through
the product handle to \(B(p_i)\); all the pages meet in the generator core and
are otherwise disjoint.  Because the order on \(D_g^-\) is
\((B(p_m),\ldots,B(p_1))\), this book of pages agrees with the orientation of
the 0-handle at both ends.  A nonreversed order would twist or cross that
book.

The page for each occurrence, together with the coned \(A\)-corner pieces in
the 0-handle, embeds the part of every original 2-cell left after deleting a
small open disc from its interior.  Different sheets meet precisely where
the corresponding cells of the presentation complex meet: along generator
cores and at the single vertex.  The remaining boundary curves
\(\lambda_1,\ldots,\lambda_n\) are pairwise disjoint simple closed curves on
the boundary of the 0-/1-handlebody.

Attach, for each \(\lambda_j\), a PL 2-handle

\[
H_j^2=D^2\times[-1,1]
\]

along the two-sided annular neighbourhood
\(S^1\times[-1,1]\) of \(\lambda_j\).  Its core \(D^2\times\{0\}\) fills the
deleted disc.  Traversing its attaching strips encounters the generator
handles in precisely the occurrence order and with precisely the signs of
\(w_j\); the \(A\)-pairs join consecutive positions cyclically.  Thus the
embedded polyhedron is the original \(K_P\), not the complex of a reduced or
homotopy-equivalent presentation.

Let \(W\) be the union of these 0-, 1-, and 2-handles.  It is a compact
orientable PL 3-manifold containing the constructed copy of \(K_P\).  Inside
\(W\), take a sufficiently small closed PL regular neighbourhood \(N\) of
that copy, subordinate to the displayed handle products.  Its vertex, edge,
and face pieces are smaller 0-, 1-, and 2-handles around the corresponding
cell strata.

The local product coordinates make the retraction explicit.  In the
0-handle, cone each complementary face of the cellularly embedded \(F\) and
project radially to the coned boundary graph.  In a 1-handle, radially
project each cross-sectional disc to the star of occurrence pages and the
generator core.  In a 2-handle, project the normal interval to the core disc
and its attaching collar.  On every overlap the two projections agree; in
particular, the reversed \(B\)-coupling makes the page systems at the two ends
of a 1-handle identical under the product identification.  Thus they assemble
to a strong deformation retraction \(N\to K_P\).

Choose product triangulations and a common subdivision on the attaching
regions.  The PL regular-neighbourhood collapse theorem then realizes this
regular neighbourhood, after subdivision, as a simplicial collapse

\[
N\searrow K_P.
\]

The ambient construction of \(W\) is the construction in the proof of
Neuwirth's Theorem 2 on p. 611, stopped after he attaches and thickens the
remaining 2-discs; passing to \(N\) makes its exact regular-neighbourhood
content explicit.

Only after this point does Neuwirth use transitivity.  Read with the direct
right-to-left tracing above, his argument on pp. 610--611 identifies the
orbits of
\(\langle AC,BC\rangle\) with the components of the complement of the
attaching curves on the boundary of the 0-/1-handlebody, equivalently with
the boundary connectivity data after the 2-handles are attached.  In the
balanced case, transitivity makes \(\partial N\) connected and its Euler
characteristic is \(2\), so \(\partial N\cong S^2\); one may then cap it with
a single 3-cell.  None of this is needed for the already constructed
orientable thickening \(N\).  \(\square\)

## Balanced trivial-group consequence

**Corollary 3.**  Under the hypotheses of Theorem 2, suppose in addition that
\(\pi_1(K_P)=1\).  If an occurrence ordering passes (E), then its regular
neighbourhood is a 3-ball and \(P\) is classically Andrews--Curtis trivial.
Moreover, an Euler-passing ordering for which the right-to-left group
\(\langle AC,BC\rangle\) is not transitive is an audit contradiction, not a
new topological outcome.

**Proof.**  Balance gives

\[
\chi(K_P)=1-n+n=1.
\]

Since \(\pi_1(K_P)=1\), \(H_1(K_P;\mathbb Z)=0\).  The complex is
2-dimensional, and \(H_2(K_P;\mathbb Z)\), being a subgroup of the free
cellular group \(C_2(K_P;\mathbb Z)\), is free abelian.  The Euler equation
for homology therefore forces \(H_2(K_P;\mathbb Z)=0\).  Thus \(K_P\) is
acyclic.  A simply connected acyclic CW complex is contractible: if it had a
first nonzero homotopy group, the Hurewicz theorem would produce a nonzero
homology group, and Whitehead's theorem then finishes the argument.

Theorem 2 constructs a regular neighbourhood \(N\searrow K_P\), so \(N\) is
contractible.  Poincare--Lefschetz duality gives

\[
H_i(N,\partial N;\mathbb Z)\cong H^{3-i}(N;\mathbb Z).
\]

The long exact sequence of the pair now yields

\[
H_0(\partial N)\cong\mathbb Z,\qquad
H_1(\partial N)=0,\qquad
H_2(\partial N)\cong\mathbb Z.
\]

Hence \(\partial N\) is a connected homology 2-sphere.  It is a closed
orientable surface, so surface classification gives
\(\partial N\cong S^2\).

Cap \(\partial N\) with a PL 3-ball to form

\[
M=N\cup_{\partial N}B^3.
\]

Van Kampen gives \(\pi_1(M)=1\).  The 3-dimensional Poincare theorem gives
\(M\cong S^3\).  Using the equivalence and uniqueness of PL structures in
dimension three, this may be taken in the PL category; PL Schoenflies then
says that the PL sphere \(\partial N\) bounds a 3-ball on each side.  Therefore
\(N\cong B^3\).

Lackenby's Theorem 1.3 states that every thickenable balanced presentation of
the trivial group can be converted to a standard presentation by
Andrews--Curtis moves, without stabilization.  It applies to \(P\), so \(P\)
is classically AC-trivial.

Finally, the direct boundary tracing above, matching Neuwirth's geometric
argument on pp. 610--611, says that
\(\langle AC,BC\rangle\) must be transitive when this constructed
\(\partial N\) is connected.  Thus, on a balanced trivial-group target, the
combination “Euler pass, right-to-left-\(BC\) transitivity fail” contradicts
the proved topology.  It must be quarantined as an error in the occurrence
dictionary, composition convention, enumeration, or proof audit.
\(\square\)

## What the criterion does not imply

Neuwirth's 1968 construction is load-bearing for Theorem 2.  The compatible
spherical-link formulation in Fulek--Tóth is useful corroboration, but their
stated model has a loopless multigraph 1-skeleton and cyclic facets.  A
one-vertex presentation complex has loop 1-cells and may have repeated
occurrences in a facet.  Their theorem is not substituted for Neuwirth here
unless a homeomorphism-preserving PL subdivision bridge from the exact
presentation complex is supplied.

A negative census says only that the exact tested \(K_P\) is not
thickenable.  Neither thickenability of this word-realized base complex nor
the potential \(\gamma_N\) is carried along an Andrews--Curtis path by any
invariance theorem proved or assumed here.  Such a negative does not
propagate to another representative, does not obstruct a later thickenable
milestone, and does not make AK(3) a counterexample to either the classical
or stable Andrews--Curtis conjecture.

## Sources

1. L. Neuwirth, “An algorithm for the construction of 3-manifolds from
   2-complexes,” *Proceedings of the Cambridge Philosophical Society* 64
   (1968), 603--614, especially pp. 604--611.
2. M. Lackenby, “The stable Andrews-Curtis conjecture and thickenable
   presentations of the trivial group,” arXiv:2606.06122v1, Theorem 1.3,
   Remark 1.4, and Section 3.1.
3. R. Fulek and C. D. Tóth, “Atomic Embeddability, Clustered Planarity, and
   Thickenability,” arXiv:1907.13086v2, Theorem 3 (corroborative only here).
