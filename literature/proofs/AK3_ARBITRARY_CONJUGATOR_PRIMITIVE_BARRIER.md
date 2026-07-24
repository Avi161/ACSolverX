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
