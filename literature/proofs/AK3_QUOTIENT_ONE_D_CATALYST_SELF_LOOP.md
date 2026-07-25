# The quotient one-\(D\) catalyst is an unbounded AK(3) self-loop

Date: 2026-07-25

Status: **PROVEN** for exactly one cross multiplication between the
\(B\)- and \(D\)-slots, with arbitrary fixed-\(R\) gauge moves before and
after it, arbitrary conjugators, either target role, a restored source
shadow, and elimination of the cross target as a final generator isolator.
This is a mechanism theorem, not a trivialization of AK(3).

## 1. The fixed-\(R\) quotient

At the rank-three compression root, put

\[
R=x^3t^{-4},\qquad
B=z^{-1}xt,\qquad
D=t^{-1}zxz^{-1}.
\tag{1.1}
\]

The tuple \((R,B,D)\) presents the trivial group and is stably
AC-equivalent to AK(3).

Let

\[
G=\langle x,t\mid x^3=t^4\rangle,
\qquad
H=G*\langle z\rangle .
\tag{1.2}
\]

Because \(R\) contains no \(z\)-letter,

\[
F(x,t,z)/\langle\!\langle R\rangle\!\rangle
\cong H.
\tag{1.3}
\]

Every fixed-\(R\) gauge multiplication vanishes in \(H\), even when the
conjugating word contains \(z^{\pm1}\). Thus arbitrary gauge moves may be
projected away before classifying the single \(B/D\) cross multiplication.

Write

\[
p=xt.
\tag{1.4}
\]

In free-product syllables,

\[
B=z^{-1}\cdot p,
\qquad
D=t^{-1}\cdot z\cdot x\cdot z^{-1}.
\tag{1.5}
\]

Both words are cyclically reduced hyperbolic elements of \(H\), of cyclic
syllable lengths \(2\) and \(4\).

## 2. The Bass--Serre bridge with vertex stabilizers

Consider a product of arbitrary conjugates and orientations of \(B\) and
\(D\). After a global conjugation, target inversion, and cyclic factor
reordering, fix \(B\) positively oriented and put the relative sign on
\(D\).

Let the two conjugated axes act on the Bass--Serre tree of
\(H=G*\langle z\rangle\). There are three cases.

### 2.1 Disjoint axes

Let \(\ell\) denote translation length in the Bass--Serre tree. Then

\[
\ell(B)=2,\qquad \ell(D)=4.
\tag{2.1}
\]

If the two axes are disjoint at distance \(d>0\), the standard tree product
formula gives

\[
\ell(gh)=\ell(B)+\ell(D)+2d=6+2d\ge8
\tag{2.2}
\]

for either choice of orientations. Geometrically, a fundamental segment
traverses one translation segment on each axis and the bridge twice.

On the other hand, extend the torus-knot weight by

\[
\operatorname{wt}(x)=4,\qquad
\operatorname{wt}(t)=3,\qquad
\operatorname{wt}(z)=0.
\tag{2.3}
\]

The normalized signed products have weights

\[
\operatorname{wt}(B D^{\pm1})
=7\pm1\in\{6,8\}.
\tag{2.4}
\]

Thus a one-\(z\) shadow is conjugate to \(z^{-1}e\) with
\(e\ne1\) in \(G\), and its translation length is \(2\). This contradicts
(2.2). A one-\(z\) target cannot come from disjoint axes.

### 2.2 A shared edge

Move a common edge to the fundamental edge. Its stabilizer is trivial, so
the residual relative element is \(1\). The target is the cyclic reduction
of a signed syllable-rotation product \(UV\).

### 2.3 A shared vertex

If the axes share a vertex but no edge, move that vertex to a fundamental
vertex. Its stabilizer is one of the two free factors. The residual target
has the form

\[
UhVh^{-1},
\qquad
h\in G
\quad\text{or}\quad
h\in\langle z\rangle .
\tag{2.5}
\]

This vertex twist is essential. Unlike a free-group Cayley tree, the
Bass--Serre tree has nontrivial vertex stabilizers. Therefore intersecting
axes are not exhausted by literal rotation products.

Sections 3--4 exhaust (2.5). The shared-edge case is included by \(h=1\).

## 3. The \(G\)-vertex forcing tables

Use the syllable rotations

\[
\begin{aligned}
B_0&=z^{-1}\cdot p,
&
B_1&=p\cdot z^{-1},\\
D_0^+&=t^{-1}\cdot z\cdot x\cdot z^{-1},
&
D_1^+&=z\cdot x\cdot z^{-1}\cdot t^{-1},\\
D_2^+&=x\cdot z^{-1}\cdot t^{-1}\cdot z,
&
D_3^+&=z^{-1}\cdot t^{-1}\cdot z\cdot x,
\end{aligned}
\tag{3.1}
\]

and

\[
\begin{aligned}
D_0^-&=z\cdot x^{-1}\cdot z^{-1}\cdot t,
&
D_1^-&=x^{-1}\cdot z^{-1}\cdot t\cdot z,\\
D_2^-&=z^{-1}\cdot t\cdot z\cdot x^{-1},
&
D_3^-&=t\cdot z\cdot x^{-1}\cdot z^{-1}.
\end{aligned}
\tag{3.2}
\]

Let \(h\in G\). Before reduction, every word

\[
B_i h D_j^\pm h^{-1}
\tag{3.3}
\]

has three \(z^{\pm1}\)-syllables. The positive \(z\) in \(D_j^\pm\) cannot
cancel the negative \(z\) from that same factor: the intervening
\(G\)-syllable is \(x^{\pm1}\ne1\). Therefore a one-\(z\) result forces the
positive \(z\) to cancel the negative \(z\) belonging to \(B_i\).

For each signed rotation cell, the intervening \(G\)-syllable must be the
identity. This gives one equation containing one occurrence of
\(h^{\pm1}\), hence a unique solution in \(G\).

For positive \(D\), the complete table is

|  | \(D_0^+\) | \(D_1^+\) | \(D_2^+\) | \(D_3^+\) |
|---|---|---|---|---|
| \(B_0\) | \(ph\,t^{-1}=1\Rightarrow h=t^{-1}x^{-1}t\) | \(ph=1\Rightarrow h=t^{-1}x^{-1}\) | \(h^{-1}=1\Rightarrow h=1\) | \(xh^{-1}=1\Rightarrow h=x\) |
| \(B_1\) | \(h\,t^{-1}=1\Rightarrow h=t\) | \(h=1\) | \(h^{-1}p=1\Rightarrow h=xt\) | \(xh^{-1}p=1\Rightarrow h=xtx\) |

\[
\tag{3.4}
\]

For negative \(D\), it is

|  | \(D_0^-\) | \(D_1^-\) | \(D_2^-\) | \(D_3^-\) |
|---|---|---|---|---|
| \(B_0\) | \(ph=1\Rightarrow h=t^{-1}x^{-1}\) | \(h^{-1}=1\Rightarrow h=1\) | \(x^{-1}h^{-1}=1\Rightarrow h=x^{-1}\) | \(ph\,t=1\Rightarrow h=t^{-1}x^{-1}t^{-1}\) |
| \(B_1\) | \(h=1\) | \(h^{-1}p=1\Rightarrow h=xt\) | \(x^{-1}h^{-1}p=1\Rightarrow h=xtx^{-1}\) | \(ht=1\Rightarrow h=t^{-1}\) |

\[
\tag{3.5}
\]

These equations are identities in \(G\), but none uses a special property
of \(G\): each solves directly by group multiplication. Thus the displayed
solution is unique, not a bounded word search.

Substituting any solution in (3.4), free-product reduction gives

\[
\operatorname{cyc}(z^{-1}t^{-1}px)
=\operatorname{cyc}(z^{-1}t^{-1}xtx).
\tag{3.6}
\]

Every solution in (3.5) gives

\[
\operatorname{cyc}(z^{-1}tpx^{-1})
=\operatorname{cyc}(z^{-1}txtx^{-1}).
\tag{3.7}
\]

If \(h\) differs from the displayed solution, the forced intervening
\(G\)-syllable is nontrivial, so the positive \(z\) cannot meet the
\(B_i\)-syllable. At least three \(z\)-syllables remain. Therefore
(3.4)--(3.5) are complete for \(G\)-vertex twists.

## 4. The \(\langle z\rangle\)-vertex forcing tables

Now let

\[
h=z^k,\qquad k\in\mathbb Z.
\tag{4.1}
\]

Adjacent \(\langle z\rangle\)-syllables combine by adding their exponents.
In every rotation cell, the two unwanted exponents are affine functions of
\(k\). If a nontrivial \(G\)-syllable separates them, no value of \(k\)
can give a one-\(z\) result. The nonempty cells below are the complete
solutions:

| positive sign | \(D_0^+\) | \(D_1^+\) | \(D_2^+\) | \(D_3^+\) |
|---|---:|---:|---:|---:|
| \(B_0\) | \(\nu_z\ge3\) | \(2|k+1|+1\) | \(2|k|+1\) | \(\nu_z\ge3\) |
| \(B_1\) | \(\nu_z\ge3\) | \(2|k|+1\) | \(2|k-1|+1\) | \(\nu_z\ge3\) |

\[
\tag{4.2}
\]

| negative sign | \(D_0^-\) | \(D_1^-\) | \(D_2^-\) | \(D_3^-\) |
|---|---:|---:|---:|---:|
| \(B_0\) | \(2|k+1|+1\) | \(2|k|+1\) | \(\nu_z\ge3\) | \(\nu_z\ge3\) |
| \(B_1\) | \(2|k|+1\) | \(2|k-1|+1\) | \(\nu_z\ge3\) | \(\nu_z\ge3\) |

\[
\tag{4.3}
\]

For example, the first nonempty positive cell has the cyclic product

\[
B_0z^kD_1^+z^{-k}
=
z^{-1}\cdot p\cdot z^{k+1}\cdot x\cdot z^{-1}
\cdot t^{-1}\cdot z^{-k}.
\tag{4.4}
\]

Cyclically combining the final \(z^{-k}\) with the initial \(z^{-1}\)
gives

\[
\nu_z
=|k+1|+1+|-k-1|
=2|k+1|+1.
\tag{4.5}
\]

Thus one-\(z\) incidence forces \(k=-1\). The other seven affine cells in
(4.2)--(4.3) force respectively the unique centers of their absolute-value
expressions. In every remaining cell, two fixed nonzero
\(\langle z\rangle\)-syllables are separated by a nontrivial
\(G\)-syllable, while the cyclic boundary contributes at least one further
unit of \(z\)-incidence. Hence \(\nu_z\ge3\) for every integer \(k\), as
displayed, and no unlisted integer can work.

All four positive cells reduce to (3.6), and all four negative cells reduce
to (3.7). The \(k=0\) entries are precisely the four literal
signed-rotation witnesses from the shared-edge case.

Combining Sections 2--4 proves the quotient classification:

### Theorem 4.1

Every product of arbitrary conjugates and orientations of \(B\) and \(D\)
whose cyclic normal form in \(H\) has exactly one
\(z^{\pm1}\)-occurrence lies in one of exactly two unoriented cyclic
classes:

\[
\boxed{
\operatorname{cyc}(z^{-1}t^{-1}xtx),
\qquad
\operatorname{cyc}(z^{-1}txtx^{-1}).
}
\tag{4.6}
\]

## 5. From a quotient class to an exact isolator shadow

Put

\[
e_+=t^{-1}xtx,
\qquad
e_-=txtx^{-1}.
\tag{5.1}
\]

The abelianization of \(G\) is infinite cyclic under

\[
\operatorname{wt}(x)=4,
\qquad
\operatorname{wt}(t)=3.
\tag{5.2}
\]

Therefore

\[
\operatorname{wt}(e_+)=8,
\qquad
\operatorname{wt}(e_-)=6.
\tag{5.3}
\]

Both elements are nontrivial in \(G\), so
\(z^{-1}e_\pm\) are cyclically reduced words of free-product syllable
length \(2\).

Suppose the actual target after all gauge moves is a generator isolator.
Invert and cyclically conjugate that relator to the exact linear form

\[
I=z^{-1}e,
\qquad e\in F(x,t).
\tag{5.4}
\]

Theorem 4.1 says that its quotient shadow is conjugate, up to inversion, to
one of \(z^{-1}e_\pm\). Choose the orientation with leading
\(z^{-1}\). The free-product conjugacy theorem says that two conjugate
cyclically reduced words of syllable length at least \(2\) differ by a
cyclic syllable rotation. Of the two rotations of
\(z^{-1}e_\pm\), only \(z^{-1}e_\pm\) begins in the
\(\langle z\rangle\)-factor. Hence

\[
[e]_G=[e_\pm]_G.
\tag{5.5}
\]

Thus target normalization gives an exact standard quotient shadow, not
merely an unspecified conjugate.

## 6. Arbitrary fixed-\(R\) interleavings

Start from \((R,B,D)\). Before the unique \(B/D\) cross multiplication,
apply any finite fixed-\(R\) gauge modifications to either non-\(R\) slot.
They preserve the two quotient shadows \(B,D\) in \(H\).

Perform one multiplication between arbitrary conjugates and orientations
of the two slots, with either slot as the cross target, and restore the
source shadow. Afterward, apply any further fixed-\(R\) gauge modifications
to either slot. Suppose that same cross-target slot is the final generator
isolator (5.4), and eliminate it.

Projection to \(H\) removes every gauge factor. Sections 2--5 give

\[
[e]_G=[e_\pm]_G.
\tag{6.1}
\]

Let \(J\) be the final survivor and \(J_0\) the restored standard survivor:

\[
J_0=
\begin{cases}
D,&\text{if the \(B\)-slot was targeted},\\
B,&\text{if the \(D\)-slot was targeted}.
\end{cases}
\tag{6.2}
\]

The gauge hypothesis gives

\[
[J]_H=[J_0]_H.
\tag{6.3}
\]

Evaluation at \(z=e\) and \(z=e_\pm\) therefore gives

\[
\bigl[J[z\mapsto e]\bigr]_G
=
\bigl[J_0[z\mapsto e_\pm]\bigr]_G.
\tag{6.4}
\]

By the fixed-relator normal-closure lemma,

\[
\left(R,J[z\mapsto e]\right)
\sim_{\mathrm{AC1-3}}
\left(R,J_0[z\mapsto e_\pm]\right).
\tag{6.5}
\]

The two existing one-\(D\) catalyst theorems prove that every standard pair
on the right of (6.5), for both signs and both target roles, is classically
AC-equivalent to AK(3). Consequently,

\[
\boxed{
\left(R,J[z\mapsto e]\right)
\sim_{\mathrm{AC1-3}}
\operatorname{AK}(3).
}
\tag{6.6}
\]

The rank-three tuple presents the trivial group throughout. Removing the
final isolator and making the substitutions is therefore the proved stable
substitution-and-removal composite, not a bare AC5 move. The classical
equivalence (6.6) concerns the resulting rank-two endpoint.

There is no bound on the number of fixed-\(R\) gauge factors, their
conjugators, or the relative conjugator in the cross multiplication.

## 7. Scope

The theorem closes every ordering with:

1. the retained relator \(R=x^3t^{-4}\) fixed in normal closure;
2. exactly one cross multiplication between the \(B\)- and \(D\)-slots;
3. every other multiplication an \(R\)-gauge move;
4. the source quotient shadow restored after the cross event; and
5. the cross target becoming the final generator isolator and being
   eliminated.

It permits gauge moves on both slots, before and after the cross event, with
conjugators containing arbitrary \(z^{\pm1}\)-letters.

It does not cover eliminating the restored source instead of the cross
target, a second \(B/D\) cross multiplication, a changed retained normal
closure, a final primitive eliminator with several
\(z^{\pm1}\)-occurrences, another stabilization, or dual-source
primitive-pair compression.

AK(3) remains open.
