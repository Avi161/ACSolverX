# AK(3) A--D internal \(BS(3,4)\) flow module

## Statement

Let

\[
B=BS(3,4)=\langle x,y\mid yx^3y^{-1}=x^4\rangle,
\qquad
R_3=1+x+x^2,\quad R_4=1+x+x^2+x^3,
\]

let \(k\) be a commutative ring, and put \(R=k[B]\).  Define

\[
H=\langle x\rangle,\qquad C=\langle x^4\rangle.
\]

The cyclic right \(R\)-module

\[
\mathcal U_k
=R\big/\bigl((x^4-1)R+(yR_3-R_4)R\bigr)
\tag{1}
\]

has the following exact Bass--Serre description.  Let

\[
E=C\backslash B,\qquad V=H\backslash B,
\]

and write \(e_g\) for the basis vector of \(k[E]\) indexed by the
right coset \(Cg\).  For \(v=Hg\), set

\[
I(v)=\sum_{i=0}^{3}e_{x^ig},
\qquad
O(v)=\sum_{j=0}^{2}e_{yx^jg}.
\tag{2}
\]

Then both expressions are independent of the representative \(g\),
and there is a natural isomorphism of right \(R\)-modules

\[
\boxed{\quad
\mathcal U_k\ \cong\
\mathcal F_k:=
k[E]\big/
\left\langle O(v)-I(v):v\in V\right\rangle_k .
\quad}
\tag{3}
\]

Thus (3) is the universal cyclic module with the two displayed
relations; it is not merely a particular representation satisfying
them.

For \(b\in B\) and \(\sigma\in\{+1,-1\}\), adding the relation
\(b+\sigma R_4\) gives the further exact constraints

\[
e_{bg}=-\sigma I(Hg)
\qquad(g\in B).
\tag{4}
\]

Equivalently, for each vertex \(v=Hg\), every edge in the image

\[
\mathscr E_b(v):=\{\,Cbhg:h\in H\,\}\subseteq C\backslash B
\tag{5}
\]

of the double coset \(CbHg\) is set equal to the common value
\(-\sigma I(v)\).  Formula (5) is a double-coset constraint, not a
condition determined only by the \(y\)-exponent of \(b\).

Over \(k=\mathbb Q\), the quotient by (4) is zero whenever

\[
b\in H\quad\text{or}\quad b\in yH.
\tag{6}
\]

No conclusion about the remaining double cosets is asserted here.

## 1. Right-handed Bass--Serre incidence

We use right cosets throughout.  The right action is

\[
(Cg)\cdot a=Cga,\qquad (Hg)\cdot a=Hga.
\tag{7}
\]

Regard \(E=C\backslash B\) as the directed edge set of the
Bass--Serre tree of the HNN presentation of \(B\).  For the directed
edge \(Cg\), define

\[
\operatorname{ter}(Cg)=Hg,
\qquad
\operatorname{ini}(Cg)=Hy^{-1}g.
\tag{8}
\]

These maps are well-defined.  If \(Cg=Cx^{4n}g\), then

\[
Hx^{4n}g=Hg,
\]

and the defining relation gives

\[
y^{-1}x^{4n}=x^{3n}y^{-1}.
\]

Consequently

\[
Hy^{-1}x^{4n}g=Hx^{3n}y^{-1}g=Hy^{-1}g.
\tag{9}
\]

The edges terminating at \(Hg\) are

\[
Cx^ig,\qquad 0\leq i<4.
\tag{10}
\]

Indeed, \(\operatorname{ter}(Cq)=Hg\) exactly when \(q\in Hg\).
The four representatives in (10) are distinct because \(C\) has
index four in \(H\).

The edges beginning at \(Hg\) are

\[
Cyx^jg,\qquad 0\leq j<3.
\tag{11}
\]

Indeed, \(\operatorname{ini}(Cq)=Hg\) exactly when \(q\in yHg\).
Moreover

\[
Cyx^{j+3}g=Cx^4yx^jg=Cyx^jg.
\tag{12}
\]

The three classes in (11) are distinct.  This is also the standard
HNN incidence computation: by Britton normal form,

\[
yHy^{-1}\cap H=\langle x^4\rangle=C,
\qquad
y^{-1}Cy=\langle x^3\rangle,
\tag{13}
\]

so \(Cyx^i=Cyx^j\) holds exactly when \(i-j\) is divisible by \(3\).
Thus every vertex has four incoming and three outgoing directed
edges.  The sums in (2) are precisely its two half-stars.

## 2. The half-stars do not depend on representatives

Suppose \(Hg'=Hg\).  Then \(g'=x^ng\) for some \(n\in\mathbb Z\).
For the incoming half-star,

\[
\sum_{i=0}^{3}e_{x^ig'}
=\sum_{i=0}^{3}e_{x^{i+n}g}
=\sum_{i=0}^{3}e_{x^ig},
\tag{14}
\]

because the classes \(Cx^m\) are periodic with period four.

For the outgoing half-star, (12) gives period three:

\[
\sum_{j=0}^{2}e_{yx^jg'}
=\sum_{j=0}^{2}e_{yx^{j+n}g}
=\sum_{j=0}^{2}e_{yx^jg}.
\tag{15}
\]

This proves separately that both \(I(Hg)\) and \(O(Hg)\) are
well-defined.  Notice that the second verification uses
\(yx^3=x^4y\); treating the two sums as if they had the same cyclic
period would reverse the HNN indices.

Right multiplication preserves incidence:

\[
I(Hg)\cdot a=I(Hga),
\qquad
O(Hg)\cdot a=O(Hga).
\tag{16}
\]

Hence the span of all conservation vectors \(O(v)-I(v)\) is a right
\(R\)-submodule of \(k[E]\).

## 3. Edge stabilization gives the permutation module

Define a right \(R\)-module homomorphism

\[
\Phi:R\longrightarrow k[E],
\qquad
\Phi(g)=e_g
\quad(g\in B),
\tag{17}
\]

and extend \(k\)-linearly.  It is surjective.  Since

\[
e_1(x^4-1)=e_{x^4}-e_1=0,
\]

we have

\[
(x^4-1)R\subseteq\ker\Phi.
\tag{18}
\]

Equality holds.  One way to see this without invoking an induced
module convention is to group the finite support of an element of
\(R\) by the right cosets \(Cg\).  Its image under \(\Phi\) is zero
exactly when the coefficient sum in every such coset is zero.  Within
one coset, every difference has the form

\[
x^{4n}g-g=(x^{4n}-1)g.
\tag{19}
\]

For \(n>0\),

\[
x^{4n}-1=(x^4-1)(1+x^4+\cdots+x^{4(n-1)}),
\]

and the analogous finite telescoping identity for \(n<0\) has the
same left factor \(x^4-1\).  Thus every zero-sum coset combination
belongs to \((x^4-1)R\).  Therefore

\[
R/(x^4-1)R\ \xrightarrow{\ \sim\ }\ k[C\backslash B].
\tag{20}
\]

This is a right-module statement: the stabilizer relation is placed
on the left of its arbitrary right translate.

## 4. The HNN relation is exactly conservation

Under (20), for every \(g\in B\),

\[
\begin{aligned}
\Phi\bigl((yR_3-R_4)g\bigr)
&=
\left(e_y+e_{yx}+e_{yx^2}
-e_1-e_x-e_{x^2}-e_{x^3}\right)g\\
&=O(Hg)-I(Hg).
\end{aligned}
\tag{21}
\]

Every vertex is \(Hg\) for some \(g\), so the image of
\((yR_3-R_4)R\) in the quotient (20) is exactly

\[
\left\langle O(v)-I(v):v\in V\right\rangle_k.
\tag{22}
\]

Applying the quotient isomorphism theorem first to (20) and then to
(22) proves (3).  In particular, no additional edge relation has
been inserted, and every right translate of each defining group-ring
relation appears in the flow presentation.

## 5. The arbitrary internal relation

Let

\[
J_{b,\sigma}
=(x^4-1)R+(yR_3-R_4)R+(b+\sigma R_4)R.
\tag{23}
\]

In \(k[E]\),

\[
\Phi\bigl((b+\sigma R_4)g\bigr)
=e_{bg}+\sigma I(Hg).
\tag{24}
\]

It follows from (3) that \(R/J_{b,\sigma}\) is exactly
\(\mathcal F_k\) modulo all relations (4).

The double-coset formulation is also exact.  Fix \(v=Hg\).  Replacing
\(g\) in (24) by \(hg\), with \(h\in H\), does not change the
half-star:

\[
I(Hhg)=I(Hg).
\]

The edge term ranges through the image of the double coset:

\[
\{\,Cbhg:h\in H\,\}=\mathscr E_b(v).
\tag{25}
\]

Thus (24) implies the constraints described in (5).  Conversely,
the member \(Cbg\) of (25) recovers (24), so the double-coset
constraints imply all original right translates.  Possible repeated
representatives of an edge in \(\mathscr E_b(v)\) do not cause an
ambiguity: they all arise from representatives of the same vertex and
therefore have the same right-hand side \(-\sigma I(v)\).

Constraints attached to different vertices can overlap.  Such
overlap is part of the quotient and is why the exact double-coset
geometry of \(b\), rather than only \(e_y(b)\), matters.

## 6. The two canonical local collapses over \(\mathbb Q\)

Now take \(k=\mathbb Q\).

### 6.1. The incoming case \(b\in H\)

If \(b\in H\), then

\[
\mathscr E_b(v)=\{\,Cx^ig:0\leq i<4\,\},
\]

namely the four incoming edges at \(v=Hg\).
Equation (4) says that each of those four edges equals
\(-\sigma I(v)\).  Summing the four equations gives

\[
I(v)=-4\sigma I(v),
\qquad
(1+4\sigma)I(v)=0.
\tag{26}
\]

For \(\sigma=+1\) the coefficient is \(5\), and for \(\sigma=-1\)
it is \(-3\).  Hence \(I(v)=0\) in either case.  Equation (4) then
kills all four incoming edges at every vertex.  Every directed edge
has a terminal vertex, so the whole quotient is zero.

### 6.2. The outgoing case \(b\in yH\)

If \(b\in yH\), then

\[
\mathscr E_b(v)=\{\,Cyx^jg:0\leq j<3\,\},
\]

the three outgoing edges at \(v=Hg\).  Equation (4) makes each of
them equal to \(-\sigma I(v)\), and therefore

\[
O(v)=-3\sigma I(v).
\tag{27}
\]

Conservation gives \(O(v)=I(v)\), so

\[
(1+3\sigma)I(v)=0.
\tag{28}
\]

The coefficient is \(4\) for \(\sigma=+1\) and \(-2\) for
\(\sigma=-1\).  Thus \(I(v)=0\), after which (4) kills every outgoing
edge.  Every directed edge has an initial vertex, so this quotient is
also zero.

These vanishings show only that this particular right-module
obstruction fails on the two local double cosets.  They do not prove
that the relative product is primitive, and they do not supply an
Andrews--Curtis move sequence.

## 7. Exact remaining boundary

For the internal residue of the A--D argument, the still relevant
elements are

\[
\begin{array}{c|c}
\sigma=+1&e_y(b)=1\\
\sigma=-1&e_y(b)=1\text{ or }0.
\end{array}
\tag{29}
\]

Section 6 closes, for this module only, the subfamilies

\[
b\in yH\quad(e_y(b)=1),
\qquad
b\in H\quad(e_y(b)=0).
\tag{30}
\]

For \(b\notin yH\) in the exponent-one fibers and
\(b\notin H\) in the exponent-zero fiber, (3)--(5) give an exact
flow presentation but no propriety or vanishing conclusion.  Deciding
those noncanonical double cosets requires a separate global argument;
no bounded tree computation can replace it.  AK(3), AC, and stable AC
remain open.

## 8. Exact component reduction for the noncanonical problem

Over \(\mathbb Q\), dualize the edge presentation.  A scalar edge
current is a function

\[
F:C\backslash B\longrightarrow\mathbb Q.
\]

The quotient vector space is nonzero exactly when its algebraic dual
contains a nonzero functional, so nonzero currents annihilating every
displayed relation are equivalent to propriety of the right ideal.

Write

\[
\begin{aligned}
I_F(Hg)&=\sum_{i=0}^{3}F(Cx^ig),\\
O_F(Hg)&=\sum_{j=0}^{2}F(Cyx^jg).
\end{aligned}
\tag{31}
\]

The current annihilates the conservation relations exactly when
\(O_F(v)=I_F(v)\) for every vertex.  It annihilates the third
relations exactly when

\[
F(Cbg)=-\sigma I_F(Hg)
\qquad(g\in B).
\tag{32}
\]

Define

\[
K_b=\langle H,b^{-1}Cb\rangle\le B.
\tag{33}
\]

If two vertices are related by \(H\), their incoming sums agree
trivially.  If they differ by \(b^{-1}cb\), with \(c\in C\), then
they select the same edge:

\[
C\,b(b^{-1}cb)g=Ccbg=Cbg.
\]

Equation (32) therefore forces their incoming sums to agree as well.
Consequently there is a well-defined function

\[
s:K_b\backslash B\longrightarrow\mathbb Q,
\qquad
s(K_bg)=I_F(Hg).
\tag{34}
\]

Conversely, (32) determines the entire edge current from \(s\):

\[
F(Cq)=-\sigma s(K_bb^{-1}q).
\tag{35}
\]

This is well-defined on \(Cq\).  Replacing \(q\) by \(cq\) changes the
argument in (35) by the left factor \(b^{-1}cb\in K_b\).

Substituting (35) into (31) proves the exact criterion.  Nonzero dual
currents are in bijection with nonzero functions \(s\) satisfying,
for every \(g\in B\),

\[
\boxed{
\sum_{i=0}^{3}s(K_bb^{-1}x^ig)
=-\sigma s(K_bg),
}
\tag{36}
\]

\[
\boxed{
\sum_{j=0}^{2}s(K_bb^{-1}yx^jg)
=-\sigma s(K_bg).
}
\tag{37}
\]

Indeed, (36) makes \(I_F(Hg)=s(K_bg)\), while (37) makes
\(O_F(Hg)=s(K_bg)\); equation (32) then follows from (35).  If
\(s\ne0\), (35) gives \(F\ne0\).  Conversely, if \(s=0\), (32)
kills every edge because \(bg\) ranges over all of \(B\).

Since both generators of \(K_b\) have zero \(y\)-exponent,

\[
K_b\le\ker e_y.
\tag{38}
\]

Thus \(e_y(g)\) is a well-defined height on \(K_b\backslash B\).
When \(e_y(b)=0\), (36) stays within one height and (37) couples it
to the next height.  When \(e_y(b)=1\), (37) stays within one height
and (36) couples it to the preceding height.

Equations (36)--(37) are the exact remaining global problem.  They
must not be called ordinary Hecke recurrences: for a general left
coset \(K_bg\), the expression \(K_bag\) is not well-defined under a
change of representative \(g\).  The equations are required for every
\(g\in B\), and those additional translated constraints may contain
cycles.  No nonzero solution, acyclicity theorem, or collapse is
claimed here.
