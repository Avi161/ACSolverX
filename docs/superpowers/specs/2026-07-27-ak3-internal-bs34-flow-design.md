# AK(3) internal \(BS(3,4)\) flow-module design

Date: 2026-07-27

## Objective

Attack the exact internal residue left by Result 59.  With

\[
B=BS(3,4)=\langle x,y\mid yx^3y^{-1}=x^4\rangle,
\qquad
R_3=1+x+x^2,\quad R_4=1+x+x^2+x^3,
\]

the remaining right-module problem is to decide, for
\(b\in B\), whether

\[
\langle x^4-1,\ yR_3-R_4,\ b+\sigma R_4\rangle_{\rm right}
\tag{1}
\]

is proper.  Result 59 leaves precisely

\[
\begin{array}{c|c}
\sigma=+1&e_y(b)=1\\
\sigma=-1&e_y(b)=1\text{ or }0.
\end{array}
\]

The first attack will replace ad hoc function modules by the exact
Bass--Serre edge-flow quotient represented by the first two
generators in (1).

## Exact edge-flow model

Put

\[
H=\langle x\rangle,\qquad C=\langle x^4\rangle.
\]

Let \(E=C\backslash B\) be the right-coset edge set and
\(V=H\backslash B\) the vertex set.  In the permutation module
\(k[E]\), write \(e_g\) for the basis vector \(C g\).  At the vertex
\(Hg\), define the two directed half-stars

\[
I(Hg)=\sum_{i=0}^{3}e_{x^ig},\qquad
O(Hg)=\sum_{j=0}^{2}e_{yx^jg}.
\tag{2}
\]

Both are independent of the representative \(g\):
\(C\) has index four in \(H\), while
\(Cyx^3=Cy\) follows from \(x^4y=yx^3\).

For \(w=e_1\),

\[
w(x^4-1)=0,\qquad
w(yR_3-R_4)g=O(Hg)-I(Hg).
\]

Therefore the universal cyclic module for the first two relations is

\[
\mathcal F_k
=k[E]/\langle O(v)-I(v):v\in V\rangle.
\tag{3}
\]

This is the directed flow module on the Bass--Serre tree: at every
vertex, total outgoing value equals total incoming value.

## Internal relation as a double-coset constraint

Adding the third generator in (1) imposes

\[
e_{bg}=-\sigma I(Hg)
\qquad(g\in B).
\tag{4}
\]

For a fixed vertex \(Hg\), all representatives \(x^ng\) must be used.
Thus (4) makes every edge in

\[
C b H g
\tag{5}
\]

equal to the same half-star value.  The geometry depends on the exact
double coset \(CbH\), not merely on \(e_y(b)\).  This is the structural
reason the three exponent classes did not collapse to three literal
representatives in Results 56--59.

## Canonical double-coset collapse

Over \(k=\mathbb Q\), two local double cosets force the entire module
to vanish.

If \(b\in H\), then \(CbH=H\), so (4) assigns the same value
\(-\sigma I(v)\) to all four incoming edges at every vertex.  Summing
them gives

\[
(1+4\sigma)I(v)=0.
\]

For either sign this forces \(I(v)=0\), hence every incoming edge is
zero.  Every oriented edge is incoming at one vertex, so the quotient
is zero.

If \(b\in yH\), then \(CbH=CyH\), so (4) assigns
\(-\sigma I(v)\) to all three outgoing edges.  Conservation and
summation give

\[
(1+3\sigma)I(v)=0.
\]

Again both signs force \(I(v)=0\), hence every outgoing edge and
therefore every edge is zero.

Thus the flow module cannot obstruct

\[
e_y(b)=0,\ b\in H,
\qquad\text{or}\qquad
e_y(b)=1,\ b\in yH.
\tag{6}
\]

This includes the literal internal representatives \(b=1\) and
\(b=y\), but is an unbounded double-coset statement.

## Noncanonical attack

For

\[
e_y(b)=0,\ b\notin H,
\qquad\text{or}\qquad
e_y(b)=1,\ b\notin yH,
\tag{7}
\]

the selected set \(CbHg\) is not a complete local incoming or
outgoing half-star.  The next proof attempt is:

1. express \(CbH\) by Britton-reduced normal form and identify the
   geodesic from \(Hg\) to the selected edges;
2. dualize (3)--(4) to scalar edge assignments satisfying conservation
   plus the double-coset recurrence;
3. construct a nonzero boundary current when that recurrence is
   acyclic; or
4. if recurrence cycles occur, classify their exact double cosets and
   solve the finite characteristic polynomial rather than bounding
   word length.

A proof must work for every element of (7), or state the exact
remaining double-coset condition.  A finite ball in the tree is only a
replay fixture.

## Verification

A dependency-free verifier will pin:

- the \(4\)-incoming and \(3\)-outgoing incidence rows;
- independence of the displayed half-stars under the cyclic
  representative changes;
- the exact local linear collapse for \(CbH=H\) and \(CbH=CyH\) for
  both signs;
- at least one noncanonical Britton word whose selected edge is not a
  member of either local half-star.

The universal flow identification and any noncanonical conclusion
remain theorem-level arguments in Markdown.

## Boundary

Showing that (1) is proper obstructs the corresponding evaluated Fox
row.  Showing that (1) is the whole group ring only defeats this
particular module obstruction; it does not prove the original
relative product primitive.  AK(3), AC, and stable AC remain open.
