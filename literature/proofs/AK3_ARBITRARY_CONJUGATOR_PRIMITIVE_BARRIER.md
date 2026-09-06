# Arbitrary-conjugator primitive barrier at the AK(3) compression root

Date: 2026-07-24

Status: the axis-alignment lemma, primitive-length lemma, and exact AK(3)
barrier theorem are **PROVEN**.  The finite rotation table is independently
machine-checked.

## 1. Exact scope

The proved one-stabilization corridor sends AK(3) to

\[
 P_0=\langle x,z\mid A,B\rangle,
\]

where

\[
\begin{aligned}
 A&=x^3zx^{-4}z^{-1}
   =\texttt{xxxzXXXXZ},\\
 B&=z^{-1}xzxz^{-1}
   =\texttt{ZxzxZ}.
\end{aligned}
\]

Consider one completely unrestricted relative-conjugator multiplication:

\[
 A\longmapsto A cB^\epsilon c^{-1}
 \quad\text{or}\quad
 B\longmapsto B cA^\epsilon c^{-1},
 \qquad c\in F(x,z),\quad\epsilon\in\{\pm1\}.
\tag{1.1}
\]

This is broader than a product of cyclic rotations.  Modulo a global
conjugation, it is the full result of independently conjugating the two
relators and multiplying one by the signed other relator.

## 2. Aligning conjugacy-class axes

Write \(\|g\|\) for cyclically reduced word length in the basis
\(\{x,z\}\), equivalently the translation length of \(g\) on the Cayley
tree.

### Lemma 2.1

For nontrivial cyclically reduced words \(P,Q\),

\[
 \min_{c\in F(x,z)}
 \left\|PcQc^{-1}\right\|
 =
 \min_{\substack{U\text{ a cyclic rotation of }P\\
                  V\text{ a cyclic rotation of }Q}}
 \left\|\overline{UV}\right\|.
\tag{2.1}
\]

### Proof

Let \(L_P,L_{cQc^{-1}}\) be the axes of the two factors in the Cayley tree.
If the axes are disjoint at distance \(d\), the bridge calculation for two
hyperbolic tree isometries gives

\[
 \|PcQc^{-1}\|=\|P\|+\|Q\|+2d.
\]

This cannot improve on \(c=1\), whose cyclic reduction has length at most
\(\|P\|+\|Q\|\).

It remains to consider intersecting axes.  Choose a vertex \(v\) in their
intersection and conjugate the complete product so that \(v\) becomes the
identity vertex.  Both factor axes now pass through the identity, so the
two conjugated factors are cyclically reduced.  A cyclically reduced
conjugate of a cyclically reduced free-group word is a cyclic rotation of
that word.  Thus the product has the right-hand form in (2.1).

Conversely, write \(U=a^{-1}Pa\) and \(V=b^{-1}Qb\).  Then \(UV\) is
globally conjugate to

\[
 P(ab^{-1})Q(ab^{-1})^{-1},
\]

so every rotation product occurs for a relative conjugator.  The two
minima agree.  \(\square\)

The same statement applies with \(Q^{-1}\).

## 3. Primitive length in rank two

### Lemma 3.1

Let \(W\in F(x,z)\) be primitive and cyclically reduced, with abelianization
vector

\[
 [W]_{\mathrm{ab}}=(p,q).
\]

Then

\[
 \|W\|=|p|+|q|.
\tag{3.1}
\]

### Proof

The Osborne--Zieschang classification of primitive conjugacy classes in
\(F_2\) identifies the class of \(W\) with the signed Christoffel word of
its primitive lattice vector \((p,q)\).  That cyclic word has exactly
\(|p|\) occurrences of one basis letter and \(|q|\) of the other, with
signs fixed by \(p,q\).  Its length is therefore (3.1).  \(\square\)

Reference: R. P. Osborne and H. Zieschang, “Primitives in the free group on
two generators,” *Inventiones Mathematicae* **63** (1981), 17--24.

## 4. Exact AK(3) calculation

The exponent vectors are

\[
 [A]_{\mathrm{ab}}=(-1,0),\qquad
 [B]_{\mathrm{ab}}=(2,-1).
\]

The complete rotation calculation is:

| target product | exponent vector | minimum cyclic length |
|---|---:|---:|
| \(A\,cBc^{-1}\) | \((1,-1)\) | 10 |
| \(A\,cB^{-1}c^{-1}\) | \((-3,1)\) | 10 |
| \(B\,cAc^{-1}\) | \((1,-1)\) | 10 |
| \(B\,cA^{-1}c^{-1}\) | \((3,-1)\) | 10 |

The last column first exhausts all cyclic rotations and then uses Lemma 2.1
to cover every \(c\in F(x,z)\).

If any product in the first or third row were primitive, Lemma 3.1 would
give cyclic length \(2\).  If a product in the second or fourth row were
primitive, it would give cyclic length \(4\).  Every actual minimum is
\(10\), a contradiction.

### Theorem 4.1

No one-edge move (1.1), with an arbitrary relative conjugator, creates a
primitive target relator from \(P_0\).

The conclusion is invariant under an ambient automorphism, relator
permutation, conjugation, and inversion.  It therefore holds on the complete
Aut(\(F_2\))-orbit of this compression root.

## 5. Meaning and limitation

A primitive relator in a balanced rank-two trivial-group presentation would
be decisive: straighten it by a stable ambient automorphism, remove its
generator, and the remaining one-generator trivial presentation has relator
exponent \(\pm1\).  Theorem 4.1 rules out that shortcut after one arbitrary
relative-conjugator edge from this exact stable compression orbit.

It does **not** show that every one-edge child has Aut-floor above \(12\),
does not cover two multiplications, and is not an obstruction to stable
AC-triviality.  Its negative statement is unbounded in the conjugator
length but local in the number of relator multiplications.

## 6. The standard AK3 pair has no fixed-donor primitive completion

This separate criterion concerns the original coordinates

\[
a=x^3y^{-4},\qquad b=xyxy^{-1}x^{-1}y^{-1}
\quad\text{in }F(x,y),
\]

not the compression coordinates of Section 1. An ACM replacement of a
recipient means any word conjugate to that recipient or its inverse in
the quotient by the retained donor. Thus it includes arbitrary finite
products of conjugates of that donor, not just one multiplication.

**Theorem 6.1.** No primitive word of $F(x,y)$ is conjugate to
$b^{\pm1}$ modulo $a$, or to $a^{\pm1}$ modulo $b$. Consequently no
single ACM replacement from the standard AK3 pair exposes a primitive
row. The same conclusion holds for a sequence that changes only one
recipient while retaining the other donor, allowing the donor's temporary
conjugation and inversion when it is restored.

**Proof, with the power row retained.** In
$G_a=\langle x,y\mid x^3=y^4\rangle$ use the homomorphism
$\chi(x)=4$, $\chi(y)=3$. A hypothetical primitive word $p$ conjugate
to $b^{\pm1}$ has $\chi(p)=\pm1$. Inverting $p$ if necessary, its
exponent vector must be

\[
(u,v)=(1+3k,-1-4k),\qquad k\in\mathbb Z.
\]

At $k=0$ its primitive cyclic representative is $xY$. Otherwise the
signs are opposite and $1<|v|/|u|\leq3/2$. The rank-two primitive-word
classification gives a cyclic representative with unit $x$-blocks all
of one sign and $y$-blocks of lengths one or two, also all of one sign.
Here and below capitals denote inverses. This uses the signed Christoffel
classification, not just coprimality of the exponent vector; see
[Gilman--Keen, Section 3 and the primitive enumeration](https://arxiv.org/pdf/0802.2731).

Pass to $C_3*C_4$ by imposing $x^3=y^4=1$. None of these blocks
vanishes, so the image is cyclically reduced and all its $C_3$ syllables
are the same element, either $x$ or $X$. In contrast, the cyclic word
$b$ has $C_3$ syllables $(x,x,X)$, and $b^{-1}$ has the opposite mixed
pattern. Since $x\neq X$ in $C_3$, no cyclic permutation can identify
either pattern with the primitive image. The free-product conjugacy
criterion rules out the proposed conjugacy already in this quotient.

**Proof, with the braid row retained.** In
$G_b=\langle x,y\mid xyx=yxy\rangle$, abelianization sends both
generators to one. The exponent sum of a hypothetical primitive
representative of $a^{\pm1}$ is therefore $\pm1$. Up to inversion and
interchanging $x,y$, its exponent vector is $(k,-k-1)$ with $k\geq0$.
The unique primitive conjugacy class of this vector is represented by

\[
p_k=(xY)^kY.
\]

These representatives are primitive directly: $(xY,Y)$ is a free basis,
and multiplying its second member by a power of the first is a Nielsen
move. Uniqueness is the same rank-two primitive classification.

Use the braid representation

\[
\rho(x)=\begin{pmatrix}1&1\\0&1\end{pmatrix},\qquad
\rho(y)=\begin{pmatrix}1&0\\-1&1\end{pmatrix}.
\]

It kills $b$, and $\operatorname{tr}\rho(a)=14$. Put
$M=\rho(xY)=\left(\begin{smallmatrix}2&1\\1&1\end{smallmatrix}\right)$
and $t_k=\operatorname{tr}(M^k\rho(Y))$. The identity
$M^2=3M-I$ gives

\[
t_0=2,\quad t_1=4,\quad
t_{k+2}=3t_{k+1}-t_k,
\qquad (t_0,t_1,t_2,t_3)=(2,4,10,26).
\]

The terms are positive and strictly increasing, by induction using
$t_{k+2}-t_{k+1}=2t_{k+1}-t_k>0$. Hence no term is fourteen.
Inversion preserves trace in $SL_2$, and exchanging $x,y$ is conjugation
by the braid half-twist $xyx$ in this representation. The allowed
normalizations therefore do not alter this obstruction. This proves
the second assertion. Successive fixed-donor operations still preserve
the recipient's conjugacy class up to inversion in its donor quotient,
which proves the sequence statement. $\square$

**Can-fail controls and scope.** The power-quotient test does not silently
exclude AK2: in $C_2*C_3$, the primitive word `xYYxYxY` equals the image
of $b$. With the basis $A=xY$, $B=Y$, that word is $ABA^2$, conjugate
to $BA^3$. Thus its primitivity is explicit, while $x=X$ in $C_2$
removes the mixed-syllable distinction. The literal transcript below now
strengthens this quotient control. For the matrix test, replacing
the lower-left entry of $\rho(y)$ by $+1$ fails the braid row; that
incorrect assignment is rejected before any trace is used.

The dependency-free tests in
`tests/stable_ac/test_ak3_fixed_donor_primitive_criterion.py` check the
finite word and matrix data. The all-slope statements follow from the
classification and recurrence arguments, not from a bounded enumeration.
This closes the direct fixed-donor primitive criterion only. It does not
obstruct paths changing both rows, any stabilized path, the MMS02 bridge,
stable AK3, or ordinary AK3. No further exclusion family is opened here.

### Literal AK2 positive control and the unsuccessful AK3 transfer

Put $r_n=x^ny^{-(n+1)}$ and $b=xyxYXY$, with $n\ge2$.
Retain $r_n$ as donor. Left-multiply the recipient $b$ successively by
the following signed conjugates, restoring the donor after every use:

| step | sign | conjugator |
| --- | --- | --- |
| 1 | $+1$ | $xyxYX$ |
| 2 | $+1$ | $xY^n$ |
| 3 | $-1$ | $xY^nx$ |
| 4 | $+1$ | $xY^nxY$ |
| 5 | $-1$ | $xY^nxYx^{n-1}$ |

The literal intermediate recipients, in order, are
\[
\begin{aligned}
 s_1&=xyxYx^{n-1}Y^{n+2},\\
 s_2&=xY^nx^{n+1}Yx^{n-1}Y^{n+2},\\
 s_3&=xY^nxy^nx^{n-1}Y^{n+2},\\
 s_4&=xY^nxYx^{2n-1}Y^{n+2},\\
 w_n&=xY^nxYx^{n-1}Y.
\end{aligned}
\]
These identities follow by the respective local replacements
$X\mapsto Xr_n$, $y\mapsto Y^nx^n$,
$x^n\mapsto y^{n+1}$, $y^n\mapsto Yx^n$, and
$x^n\mapsto y^{n+1}$ at the indicated prefixes. The table supplies the
literal donor factors; it does not treat a quotient equality as a move.

For $n=2$, use the free-basis notation $p=xY$, $q=Y$. Then
$r_2=pQpqq$ and $w_2=pqpp$. Conjugating the second row by $P$ gives
$z=qp^3$. In the free basis $(p,z)$, the first row is exactly
\[
 p^4z^{-1}p z p^{-3}z p^{-3}.
\]
Left-multiply it by ${}^{p^4}z$, then ${}^{p^5}z^{-1}$, then
${}^{p^2}z^{-1}$, with the second row restored each time. The successive
first rows are $p^5z p^{-3}z p^{-3}$, $p^2z p^{-3}$, and $p^{-1}$.
Invert the first row. Right-multiply the second row by $p^{-1}$ three
times to obtain $q$; right-multiply the first row by $q^{-1}$ to obtain
$x$, and invert the second row to obtain $y$.

Thus the transcript actually ends at $(x,y)$ using ordinary AC moves.
The free bases above are notation for words in $x,y$, not extra ambient
automorphism moves or stabilization. The [independent replay](../../tests/stable_ac/test_ak2_primitive_donor_transcript.py)
checks all five factors, the restored donor, both coordinate changes,
the final cleanup in the original generators, and a corrupted-sign control.

At $n=3$, the same five legal factors instead give
$w_3=\mathtt{xYYYxYxxY}$. This is only another representative modulo the
retained power row. The all-conjugator fixed-donor theorem above already
precludes its primitive completion, so the AK2 cleanup cannot be transferred
as a fixed-donor shortcut. No larger probe or residual family is attached
to this failed transfer. Its outcome is a fully literal positive control,
not a shorter AK3 terminal problem or an AK3 trivialization.

**The full both-row transfer was also checked once.** The preceding
fixed-donor stopping statement does not forbid applying the rest of the
AK2 move list to the actual AK3 recipient. Put $p=xY$ and
$d=p^{-1}w_3p=\mathtt{YYxYxxYxY}$; this row is not the AK2 word $z=Yp^3$.
The three cleanup macros, now donating $d$ rather than $z$, give
\[
 f={}^{p^2}d^{-1}\;{}^{p^5}d^{-1}\;{}^{p^4}d\;r_3
 =\mathtt{XyXyyxYXyXyyyXYYxYxyXyxxYYYY}.
\]
The actual first-row lengths are $22,27,28$. Apply the remaining moves
using the current rows: invert the first; right-multiply the second by
the current first inverse three times; right-multiply the first by the
current second inverse; invert the second. The exact endpoint is
\[
 (f^{-4}d^{-1},\ f^{-3}d^{-1}).
\]
Both rows are cyclically reduced and have lengths $121$ and $93$.
This is a legal ordinary-AC path changing both rows, not an application
of the fixed-donor obstruction. It produces no shorter endpoint than the
initial total length thirteen. The focused replay retains its literal
endpoint and distinguishes the actual donor from the AK2 coordinate word.
Freeze this full-transcript transfer without scaling it or attaching a new
residual category. Its failure to simplify is not an obstruction to other
both-row paths or to AK3.

## 7. Initial conjugations followed by arbitrary Nielsen row moves

This section concerns the **standard** rows
\(A_3=x^3y^{-4}=\mathtt{xxxYYYY}\) and
\(B_3=xyxy^{-1}x^{-1}y^{-1}=\mathtt{xyxYXY}\), not the
compression-root words of Section 1. Capital letters denote inverses.

**Theorem 7.1.** For every \(g\in F(x,y)\), the subgroup
\[
K_g=\langle A_3,gB_3g^{-1}\rangle
\]
contains no primitive element of the ambient free group. Consequently,
independently conjugating the two standard rows and then applying an
arbitrary finite sequence of Nielsen row operations cannot expose a
primitive row or reach a free basis.

**Proof.** Use the labelled Cayley tree. Every consecutive triple on the
axis of \(B_3\), in either orientation, alternates generator names.
No consecutive triple on the axis of \(A_3\) alternates generator names:
its cyclic runs have lengths three and four. Thus the axes of \(A_3\)
and \(gB_3g^{-1}\) have intersection length at most two.

If the axes are disjoint, join them by their shortest bridge and quotient
each axis by its own period. The result is a labelled barbell. If they
intersect, use their maximal intersection segment and quotient by the
two periods, obtaining a wedge or theta graph. These graphs are already
immersed: at the attachment endpoints, the shortest-bridge property or
maximality of the intersection gives distinct outgoing labels. Moreover,
the intersection is shorter than both periods, six and seven, so it
identifies only proper embedded arcs of the two circles. There are no
further folds or forced vertex identifications. The graph has rank two,
and its two period loops generate a subgroup conjugate to \(K_g\).
It therefore represents the core relevant to cyclic words of \(K_g\).

By the rank-two primitive classification used in Lemma 3.1, a cyclically
reduced primitive word uses at most one sign of each generator. Call
such a word sign-coherent. This necessary condition is also stated
explicitly in
[Carette--Francaviglia--Kapovich--Martino, p. 1481](https://msp.org/agt/2012/12-3/agt-v12-n3-p09-p.pdf).
For any choice of signs, retain only graph edges labelled with those
signs. Every nonempty closed walk in this directed graph decomposes into
directed simple cycles.

In a barbell a closed walk using the bridge traverses a bridge edge in
both directions, so cannot be sign-coherent. In a wedge the only simple
cycles are the two period circles. In a theta graph there is additionally
the mixed simple cycle, made from the complementary arcs of those
circles after deleting their common segment of length at most two.
Neither orientation of this mixed cycle is sign-coherent:

- Deleting at most two consecutive cyclic letters from either orientation
  of \(A_3\) leaves both x and Y, or both X and y, respectively. These
  determine the only possible sign choice for the mixed cycle.
- In \(B_3\), the letters offending the choice \(\{x,Y\}\) are y and X,
  three positions apart cyclically. A segment of length at most two
  cannot remove both. In \(B_3^{-1}\) there are four offending letters,
  also too many to remove. Inverting both words gives the other choice
  \(\{X,y\}\).

The \(B_3\)-circle itself is not sign-coherent. Hence in each signed
subgraph the only possible directed simple cycle is the appropriately
oriented \(A_3\)-circle. Every nonempty sign-coherent closed walk is
therefore a cyclic rotation of \(A_3^n\) or \(A_3^{-n}\), \(n\ge1\).
This also treats a word of \(K_g\) which is not initially cyclically
reduced: cyclic reduction moves the basepoint of its loop within the
core and leaves a nonempty closed path there.

For \(n>1\), the exponent vector \(\pm n(3,-4)\) is not primitive.
For \(n=1\), \(A_3\) is nonprimitive because
\(F(x,y)/\operatorname{Ncl}(A_3)\) surjects onto the nonabelian free
product \(C_3*C_4\), whereas quotienting by a primitive element would
give an infinite cyclic group. Primitivity is preserved by conjugation
and inversion. This proves the subgroup assertion.

Two independent initial conjugations reduce to the displayed form by
a common conjugation. Nielsen row operations preserve the generated
subgroup: these are row inversions, permutations, and multiplication by
another row or its inverse. The asserted consequence follows. \(\square\)

The three [focused finite-word checks](../../tests/stable_ac/test_ak3_conjugation_nielsen_axis_barrier.py)
verify the overlap and short-deletion facts, with can-fail controls.
They enumerate no conjugator words or AC histories; the immersed-core
argument supplies the all-conjugator conclusion.

This is a completed two-block theorem, not a new residual ledger. It
does not cover Nielsen changes before the independent conjugations,
interleaving further independent conjugations with row multiplications,
or stabilization. Those change the subgroup or the ambient rank to
which the argument applies. The MMS02 bridge, stable AK3, and ordinary
AK3 remain open.
