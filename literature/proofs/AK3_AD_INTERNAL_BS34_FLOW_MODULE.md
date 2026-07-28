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

## 9. Exact one-\(y\) reduction in the exponent-one fibers

The quotient defined by (4) depends only on the double coset \(CbH\).
Indeed, replacing \(b\) by \(cbh\), with \(c\in C\) and \(h\in H\),
does not change any selected set \(CbHg\).

Suppose \(b\) has a representative with one positive stable letter:

\[
b=x^r yx^s.
\tag{39}
\]

The right \(H\)-factor removes \(s\), and the left \(C\)-factor reduces
\(r\) modulo four.  Thus there are exactly four one-\(y\) double
cosets

\[
Cx^r yH,\qquad r\in\{0,1,2,3\}.
\tag{40}
\]

These four classes are distinct.  An equality
\(Cx^ryH=Cx^{r'}yH\) would give integers \(m,n\) with

\[
x^{4m+r}yx^ny^{-1}x^{-r'}=1.
\]

Britton reduction forces \(n=3k\); the defining relation then gives
\(4m+r+4k-r'=0\), so \(r\equiv r'\pmod4\).

The case \(r=0\) is the canonical double coset \(CyH\) from
Section 6.2.  The three values \(r=1,2,3\) are noncanonical.

For every value of \(r\), put

\[
A=\langle x^3\rangle,\qquad
u=y^{-1}xy,\qquad H'=y^{-1}Hy.
\]

Since \(y^{-1}Cy=A\),

\[
b^{-1}Cb=A
\quad\text{and hence}\quad
K_b=\langle H,A\rangle=H.
\tag{41}
\]

Moreover,

\[
H\cap H'=A=\langle u^4\rangle,
\qquad x^3=u^4.
\]

The Bass--Serre normal-form theorem for the two adjacent vertex
stabilizers gives

\[
J:=\langle H,H'\rangle
\cong H*_{A}H'.
\tag{42}
\]

Now specialize (36)--(37), absorbing the left factor \(x^{-s}\) into
the left \(H\)-coset.  Equation (37) stays within one height and
becomes

\[
\boxed{
\sum_{j=0}^{2}s(Hu^{-r}x^jg)
=-\sigma s(Hg).
}
\tag{43}
\]

Equation (36) couples the preceding height to the current one:

\[
\boxed{
\sum_{i=0}^{3}s(Hy^{-1}x^{i-r}g)
=-\sigma s(Hg).
}
\tag{44}
\]

For a fixed right \(J\)-coset \(Jg\), the intralayer equation (43) is
the eigenvalue equation

\[
T_rs=-\sigma s,
\qquad
(T_rs)(Hq)=\sum_{j=0}^{2}s(Hu^{-r}x^jq)
\tag{45}
\]

on the \(H\)-type vertices of the Bass--Serre tree of
\(H*_{A}H'\).  Unlike the general left-prefix expressions discussed
at the end of Section 8, this operator is genuinely well-defined.
Indeed,

\[
\begin{aligned}
Hu^{-r}x^{m+3}q
 &=Hu^{-r}x^3x^mq\\
 &=Hu^{4-r}x^mq\\
 &=Hu^{-r}x^mq,
\end{aligned}
\tag{46}
\]

where \(x^3=u^4\) and the last equality absorbs \(x^3\) on the left.
Thus replacing \(q\) by \(x^nq\) only permutes the three summands in
(45).  The four-term window in (44) has the analogous structural
periodicity

\[
Hy^{-1}x^{m+4}q
=Hx^3y^{-1}x^mq
=Hy^{-1}x^mq.
\tag{47}
\]

At each of the three adjacent \(H'\)-vertices, the
operator takes the branch obtained by the fixed nonzero turn
\(-r\pmod4\).  The values \(r=1,2,3\) are therefore three explicit
fixed-turn operators, not an unbounded family of words.

For \(r=0\), every term in (43) is \(s(Hg)\), and the equation forces
\((3+\sigma)s(Hg)=0\), recovering the rational canonical collapse.
For \(r=1,2,3\), neither a nonzero eigenfunction compatible with
(44) nor a collapse has been proved.  Equations (43)--(45) are the
exact next subproblem; no conclusion from a finite truncation is
claimed here.

## 10. The noncanonical one-\(y\) ideals are proper

We now solve that subproblem.  Fix \(r\in\{1,2,3\}\).  Let
\(\delta_v\) denote the basis vector at \(v\) in
\(\mathbb Q[H\backslash B]\).  The primal relation vectors dual to
(44) and (43) are, respectively,

\[
\begin{aligned}
A_{Hg}
 &=\sigma\delta_{Hg}
   +\sum_{i=0}^{3}\delta_{Hy^{-1}x^{i-r}g},\\
B_{Hg}
 &=\sigma\delta_{Hg}
   +\sum_{j=0}^{2}\delta_{Hu^{-r}x^jg}.
\end{aligned}
\tag{48}
\]

Equations (46)--(47) show that these vectors are independent of the
representative \(g\), so we write them as \(A_v,B_v\).

We use the underlying unoriented Bass--Serre tree \(\mathcal T\) from
Section 1.  Its vertices are \(H\backslash B\), every vertex has four
incoming predecessors and three outgoing successors, and an oriented
edge runs from \(Hy^{-1}g\) to \(Hg\).

For an outgoing successor

\[
c_j=Hyx^jg
\]

of \(v=Hg\), cyclically label its four incoming predecessors by

\[
p_k(c_j)=Hy^{-1}x^kyx^jg=Hu^kx^jg,
\qquad k\in\mathbb Z/4.
\tag{49}
\]

Thus \(p_0(c_j)=v\).  Let \(\rho_{c_j}\) send \(p_k(c_j)\) to
\(p_{k+1}(c_j)\).  The second relation in (48) is exactly

\[
B_v=\sigma\delta_v+
\sum_{\substack{c\text{ outgoing}\\\text{from }v}}
\delta_{\rho_c^{-r}(v)}.
\tag{50}
\]

Because \(r\ne0\pmod4\), every target
\(\rho_c^{-r}(v)\) is a predecessor of \(c\) distinct from \(v\).
This nontrivial turn is the only fact needed in the following
finite-support argument.

### 10.1 Outside-target lemma

Let \(K\) be a subtree of \(\mathcal T\), let \(v\in K\) have degree
at most one in \(K\), and suppose all relation centers under
consideration lie in \(K\).

Choose an outgoing edge \(v\longrightarrow c\) outside \(K\), and put

\[
t=\rho_c^{-r}(v).
\]

Then \(t\notin K\), and the only relation centered in \(K\) which can
contain \(\delta_t\) is \(B_v\).  Indeed, a relation centered at \(t\)
is excluded.  If \(A_w\) contains \(t\), then \(t\) is an incoming
predecessor of \(w\); unless \(w=c\), the path from \(w\) to \(K\)
passes through \(t,c,v\), and \(c\notin K\) as well.  If \(B_w\)
contains \(t\) through the successor \(c\), bijectivity of
\(\rho_c^{-r}\) forces \(w=v\).  If it contains \(t\) through another
successor, the unique path from \(w\) to \(K\) again passes through
\(t,c,v\).

There is a slightly subtler incoming version.  At least three of the
four incoming predecessors of \(v\) lie outside \(K\).  If the unique
possible neighbor \(w_0\in K\) of \(v\) is itself another incoming
predecessor of \(v\), exclude the one vertex

\[
p_0=\rho_v^{-r}(w_0).
\tag{51}
\]

Choose any other incoming predecessor \(p\) of \(v\) outside \(K\);
at least two choices remain.  Then the only relation centered in
\(K\) which contains \(\delta_p\) is \(A_v\).

To verify the last assertion, an \(A_w\)-contribution requires
\(p\longrightarrow w\).  Besides \(w=v\), every such \(w\) lies
beyond \(p\) outside \(K\).  A \(B_w\)-contribution makes \(p,w\)
incoming predecessors of a common successor \(d\).  If \(d=v\), the
only possible center is \(w=\rho_v^r(p)\); it could lie in \(K\) only
as \(w_0\), precisely the case excluded by (51).  If \(d\ne v\), the
path from \(w\) to \(K\) passes through \(d,p,v\).

### 10.2 Leaf elimination

Suppose that a finite Bézout certificate existed:

\[
\lambda\delta_o
=\sum_v\alpha_vA_v+\sum_v\beta_vB_v,
\tag{52}
\]

where only finitely many \(\alpha_v,\beta_v\) are nonzero.  Let \(S\)
be their joint support and let \(K\) be the finite convex hull of
\(S\cup\{o\}\).

If \(S=\varnothing\), equation (52) already forces \(\lambda=0\), so
assume \(S\ne\varnothing\).
If \(K\) has more than one vertex, it has a leaf \(v\in S\): its
leaves lie in \(S\cup\{o\}\), and at most one of them is the separately
adjoined point \(o\).  If \(K=\{o\}\), take \(v=o\).  Thus in either
case \(v\in S\) and \(v\) has degree at most one in \(K\).

At least two outgoing edges at \(v\) leave \(K\).  Choose one and form
\(t=\rho_c^{-r}(v)\).  The coefficient of \(\delta_t\) on the left of
(52) is zero, while the outside-target lemma says that its coefficient
on the right is exactly \(\beta_v\).  Hence \(\beta_v=0\).

Next choose \(p\) by the incoming part of the lemma.  Its coefficient
on the left of (52) is again zero, and its coefficient on the right is
exactly \(\alpha_v\).  Hence \(\alpha_v=0\), contradicting \(v\in S\).
Therefore (52) forces \(S=\varnothing\) and \(\lambda=0\).

In particular,

\[
\delta_o\notin
\operatorname{span}_{\mathbb Q}
\{A_v,B_v:v\in H\backslash B\}.
\tag{53}
\]

The span in (53) is proper.  Linear-functional separation gives a
function \(s:H\backslash B\to\mathbb Q\), with \(s(o)=1\), which
annihilates every \(A_v,B_v\).  It is a nonzero solution of
(43)--(44).  Section 8 then gives the nonzero edge current

\[
F(Cq)=-\sigma s(Hb^{-1}q).
\tag{54}
\]

Consequently, for both signs \(\sigma\), the right ideal

\[
(x^4-1)R+(yR_3-R_4)R+(x^ry+\sigma R_4)R
\]

is proper for \(r=1,2,3\).  The proof deliberately excludes \(r=0\):
then every turn in (50) fixes \(v\) and
\(B_v=(3+\sigma)\delta_v\), recovering the canonical collapse.

## 11. Exact Britton turn codes and the first multi-syllable fold

Every double coset in \(C\backslash B/H\) other than \(H\) has a
Britton-reduced representative

\[
x^{r_0}y^{\epsilon_1}x^{r_1}\cdots
y^{\epsilon_{n-1}}x^{r_{n-1}}y^{\epsilon_n},
\qquad n\geq1,
\tag{55}
\]

with the following normalized turn code:

\[
0\leq r_0<4,
\qquad
\begin{cases}
0\leq r_i<3,&\epsilon_i=+1,\\
0\leq r_i<4,&\epsilon_i=-1,
\end{cases}
\quad 1\leq i<n,
\tag{56}
\]

and with \(r_i\ne0\) whenever
\(\epsilon_{i+1}=-\epsilon_i\).  The exponent sum is

\[
e_y(b)=\sum_{i=1}^n\epsilon_i.
\tag{57}
\]

This is the standard HNN normal form with fixed right transversals.
After a positive stable letter, use
\(yx^{3k}=x^{4k}y\) to reduce the following exponent modulo three;
after a negative stable letter, use
\(y^{-1}x^{4k}=x^{3k}y^{-1}\) to reduce it modulo four.  A zero residue
between opposite stable letters is exactly a Britton pinch.  Left
multiplication by \(C\) reduces the initial exponent modulo four, and
right multiplication by \(H\) removes the final base coefficient.

The normalized code need not be unique.  Right multiplication by a
base-group element can carry from the final end through several stable
letters and change internal residues.  For example,

\[
Cy^2H=CyxyH,
\tag{58}
\]

because

\[
y^2x^3=yx^4y=x^4yxy.
\]

There is nevertheless an exact parameterization.  On the set of codes
(55)--(56), let \(T_m\) multiply the represented word on the right by
\(x^m\), restore the fixed-transversal HNN normal form by the two carry
rules

\[
yx^{3k}=x^{4k}y,
\qquad
y^{-1}x^{4k}=x^{3k}y^{-1},
\]

normalize the final base coefficient with the transversal appropriate
to the last stable letter, discard the remaining final coefficient by
the right-\(H\) quotient, and finally reduce the initial exponent
modulo four.  These maps do not form a \(\mathbb Z\)-action.  The exact
equivalence is instead

\[
\mathfrak c'\sim\mathfrak c
\quad\Longleftrightarrow\quad
\mathfrak c'=T_m(\mathfrak c)
\text{ for some }m\in\mathbb Z.
\]

Surjectivity is the normal-form reduction above; the converse and
completeness follow by normalizing an equality
\(w'=x^{4k}wx^m\).  Thus the double-coset space is parameterized by
endpoint-carry equivalence classes, not by individual turn strings.

Endpoint carry preserves the number and signs of the stable letters.
At an opposite-sign turn, the carried increment is a multiple of the
applicable transversal modulus: a multiple of three in
\(yx^ry^{-1}\), and a multiple of four in
\(y^{-1}x^ry\).  Its nonzero residue therefore cannot become a
Britton pinch.  Same-sign turns never form a pinch.  Hence \(n\) and
the sequence \((\epsilon_1,\ldots,\epsilon_n)\) are invariants of the
endpoint-carry class.

Consequently, the exact multi-syllable residue is

\[
\begin{array}{c|c}
e_y(b)=1& n\geq3,\ \sum\epsilon_i=1,\\
e_y(b)=0& n\geq2,\ \sum\epsilon_i=0.
\end{array}
\tag{59}
\]

The length-one exponent-one codes are precisely \(x^ryH\): \(r=0\)
is the canonical collapse and \(r=1,2,3\) are covered by Section 10.

For multi-syllable codes, even an outward target need not be unique.
There are universal adjacent-center collisions in the exact
\(K_b\backslash B\) scalar system.  For every \(v=Hg\),

\[
\underbrace{K_bb^{-1}yx^jg}_{\text{a target of (37) at }Hg}
=
\underbrace{K_bb^{-1}(yx^jg)}_{
\text{the }i=0\text{ target of (36) at }Hyx^jg},
\tag{60}
\]

and

\[
\underbrace{K_bb^{-1}x^ig}_{\text{a target of (36) at }Hg}
=
\underbrace{K_bb^{-1}y(y^{-1}x^ig)}_{
\text{the }j=0\text{ target of (37) at }Hy^{-1}x^ig}.
\tag{61}
\]

Thus an exposed coordinate must, after projection, be separated from
every relation center whose stencil can hit it; lying outside the
lifted coefficient hull is not enough.

The local leaf lemma from Section 10 does not extend verbatim to
(59).  A shortest exponent-one countergeometry is

\[
b=y^2xy^{-1},
\qquad e_y(b)=1,
\qquad b^{-1}=yx^{-1}y^{-2}.
\tag{62}
\]

It is Britton reduced and has the minimum possible stable-letter
length three beyond the length-one stratum.  At the root \(H\), the
lifts of all targets in the two scalar relation vectors are

\[
Hyx^{-1}y^{-2}x^i\quad(0\leq i<4),
\qquad
Hyx^{-1}y^{-1}x^j\quad(0\leq j<3).
\tag{63}
\]

Every word in (63) is Britton reduced and its geodesic begins through
the same neighbor

\[
c=Hyx^{-1}.
\tag{64}
\]

Thus, if a finite coefficient hull has the edge \([H,c]\) as its sole
edge at the leaf \(H\), neither scalar stencil supplies an unused
outward branch there.  At this point this did not prove collapse or
propriety for (62).  It proved only that the one-\(y\) leaf argument
needed a new ingredient: targets must be separated after projection to
\(K_b\backslash B\), rather than merely lying off a chosen lifted tree
branch.  Section 15 below settles this class by a folded outgoing-port
argument instead.

The universal collision (60) is already visible in the shortest
exponent-zero code

\[
b_0=yxy^{-1}.
\tag{65}
\]

Here \(b_0^{-1}x^4b_0=x^4\), so \(K_{b_0}=H\).  If
\(c_j=Hyx^j\), the corresponding target of (37) is

\[
d_j=Hb_0^{-1}yx^j=Hyx^{j-1}.
\tag{66}
\]

The vertex \(d_j\) lies in an outgoing branch different from
\(c_j\), but it is simultaneously the \(i=0\) target of (36) centered
at \(c_j\).  Hence even for \(K_b=H\), and even when the target is
genuinely outward from the hull edge \([H,c_j]\), outwardness alone
does not imply uniqueness.

## 12. The positive--negative exponent-zero family is proper

The collision in (66) does not force collapse.  In fact it is bypassed
by a second Bass--Serre decomposition.  Put

\[
a=yxy^{-1},
\qquad L=\langle a\rangle,
\qquad A=\langle x^4\rangle=\langle a^3\rangle,
\qquad J_-:=\langle H,L\rangle.
\tag{67}
\]

The adjacent-stabilizer normal-form theorem gives

\[
J_-\cong H*_{A}L
=\langle x,a\mid x^4=a^3\rangle.
\tag{68}
\]

Fix \(\ell\in\{0,1,2,3\}\), \(r\in\{1,2\}\), and

\[
b=x^\ell yx^ry^{-1}=x^\ell a^r,
\qquad \lambda=-\sigma\in\{+1,-1\}.
\tag{69}
\]

Since both \(x\) and \(a\) centralize \(A\), one has

\[
b^{-1}Cb=C,
\qquad K_b=H.
\tag{70}
\]

Equations (36)--(37) therefore become

\[
\boxed{
\sum_{i=0}^{3}s(Ha^{-r}x^ig)=\lambda s(Hg),
}
\tag{71}
\]

\[
\boxed{
\sum_{j=0}^{2}s(Ha^{-r}x^{-\ell}a^jyg)=\lambda s(Hg).
}
\tag{72}
\]

In (71), the shift \(i\mapsto i-\ell\) in (36) disappears by the
four-periodicity.  Formula (72) follows from
\(b^{-1}=a^{-r}x^{-\ell}\) and \(yx^j=a^jy\).

### 12.1 Local interpolation in \(J_-\)

The Bass--Serre tree of (68) is \((4,3)\)-biregular.  Its
\(H\)-vertices are \(H\backslash J_-\), its \(L\)-vertices are
\(L\backslash J_-\), and an \(H\)-vertex \(Hq\) has the four adjacent
\(L\)-vertices

\[
Lx^iq,\qquad i\in\mathbb Z/4.
\]

At the block \(Lx^iq\), the three adjacent \(H\)-vertices are

\[
Ha^kx^iq,\qquad k\in\mathbb Z/3.
\]

Thus the left side of (71) takes, in each of the four adjacent
\(L\)-blocks, the branch obtained from \(Hq\) by the fixed turn
\(-r\pmod3\).  Since \(r=1,2\), this turn has no fixed point.

For either value of \(\lambda\), the following two interpolation
statements hold:

1. an eigenfunction satisfying (71) may be prescribed arbitrarily at
   one \(H\)-vertex;
2. any nonzero rational linear functional supported on at most three
   \(H\)-vertices may be prescribed arbitrarily.

To prove the first statement, root the internal bipartite tree at the
chosen \(H\)-vertex and assign its value.  When an \(H\)-vertex \(v\)
is processed, its unique already exposed parent block contributes a
known value \(c\); the root has \(c=0\).  Every other incident block is
fresh.  In one fresh block assign the turned target the residual

\[
\lambda s(v)-c,
\]

and assign zero to the turned target in the other fresh blocks and to
all remaining new \(H\)-vertices.  The equation at \(v\) now holds.
The nonzero turn ensures that every assigned target is new, and the
tree ensures that distinct fresh blocks do not conflict.  Recursion on
distance assigns every \(H\)-vertex exactly once.

For the second statement, combine repeated coordinates and let \(S\)
be the resulting support, so \(1\leq|S|\leq3\).  Choose a leaf \(v\)
of the finite convex hull of \(S\) in the internal bipartite tree.
Prescribe value one at \(v\) and value zero at every other
\(H\)-vertex of that hull.  Process the hull outward from \(v\).  At a
nonroot \(H\)-vertex, at most two of its three fresh \(L\)-blocks lead
toward the other members of \(S\); at the root, at most one of its
four fresh blocks does.  There is therefore always a fresh block off
the hull in which to place the residual required by (71).  Put zero
on every new vertex in the hull-facing blocks.  In the selected
off-hull block put the residual on its turned target and zero on every
other new \(H\)-vertex.  Assign zero to every new \(H\)-vertex in all
remaining fresh blocks as well.  Continue by the unrestricted
recursion from the first statement outside the hull.  The resulting
eigenfunction is one at \(v\) and zero on \(S\setminus\{v\}\), so the
functional takes the nonzero coefficient of \(v\).  Scaling gives any
prescribed rational value.  All assignments remain rational.

### 12.2 The macro HNN tree

There is an equivalent presentation

\[
B=\langle J_-,y\mid yxy^{-1}=a\rangle.
\tag{73}
\]

Indeed, eliminating \(a\) from (68) and (73) recovers
\(yx^3y^{-1}=x^4\).  The macro Bass--Serre tree has vertices
\(J_-\backslash B\) and edges \(H\backslash B\).  For an edge \(Hq\),
use the right-coset endpoints

\[
\operatorname{ini}(Hq)=J_-q,
\qquad
\operatorname{ter}(Hq)=J_-yq.
\tag{74}
\]

They are well-defined: if \(Hq=Hx^nq\), then
\(J_-yx^nq=J_-a^nyq=J_-yq\).

The source port of (74) is the individual \(H\)-vertex \(Hq\) in the
fiber over \(J_-q\).  In the target fiber over \(J_-yq\), define the
three-slot functional

\[
P_{\ell,r,q}(s)
:=\sum_{j=0}^{2}s(Ha^{-r}x^{-\ell}a^jyq).
\tag{75}
\]

All three coordinates lie in that target fiber because their prefixes
before \(yq\) belong to \(J_-\).  After repeated coordinates are
combined, \(P_{\ell,r,q}\) is a nonzero rational functional supported
on at most three \(H\)-vertices.  It depends only on the edge \(Hq\):
replacing \(q\) by \(x^nq\) shifts \(j\) modulo three, and the period
three is explicit:

\[
Ha^{-r}x^{-\ell}a^{j+3}yq
=Hx^4a^{-r}x^{-\ell}a^jyq
=Ha^{-r}x^{-\ell}a^jyq,
\]

because \(x^4=a^3\) is central in \(J_-\).  Equation (72) is exactly
the macro-edge condition

\[
P_{\ell,r,q}(s)=\lambda s(Hq).
\tag{76}
\]

### 12.3 Global current

Because \(H\leq J_-\), the map
\(H\backslash B\to J_-\backslash B\) partitions the global vertex set
into the disjoint fibers \(H\backslash J_-q\).  A local function on
each macro vertex therefore defines one global function with no
overlap ambiguity.

Root the macro tree.  In its root fiber choose a nonzero local
solution of (71), prescribing value one at one \(H\)-vertex.  Decorate
the remaining macro vertices by increasing distance from the root.

Across an edge oriented from a decorated fiber to a new fiber,
equation (76) prescribes one three-slot target functional in the new
fiber; use the second local interpolation statement.  Across an edge
oriented from a new fiber to a decorated fiber, (76) prescribes one
\(H\)-vertex value in the new fiber; use the first statement.  The
macro graph is a tree, so a new fiber has exactly one edge back to the
decorated ball and receives exactly one scalar prescription.  There
are no compatibility cycles.

The resulting nonzero function \(s:H\backslash B\to\mathbb Q\)
satisfies (71)--(72), hence (36)--(37).  Section 8 reconstructs a
nonzero edge current.  Therefore, for
\(\ell=0,1,2,3\), \(r=1,2\), and both signs \(\sigma\),

\[
(x^4-1)R+(yR_3-R_4)R+
(x^\ell yx^ry^{-1}+\sigma R_4)R
\tag{77}
\]

is a proper right ideal of \(R=\mathbb Q[B]\).  In the A--D residue,
this closes the entire positive--negative, stable-letter-length-two
family for the relevant sign \(\sigma=-1\).  It does not cover the
inverse sign sequence \(y^{-1}x^ry\) or longer endpoint-carry classes.

## 13. The negative--positive length-two flow module collapses

The inverse turn sequence has the opposite outcome for this module.
Put

\[
u=y^{-1}xy,
\qquad
J_+=\langle x,u\mid x^3=u^4\rangle,
\qquad
D=\langle x^3\rangle=\langle u^4\rangle.
\tag{78}
\]

The subgroup \(D\) is central in the amalgam \(J_+\).  Fix

\[
\ell\in\{0,1,2,3\},
\qquad r\in\{1,2,3\},
\qquad b=x^\ell u^r=x^\ell y^{-1}x^ry.
\tag{79}
\]

Let \(K=K_b\).  Since \(C=\langle x^4\rangle\) and
\(x^4=xx^3\),

\[
b^{-1}x^4b
=u^{-r}x^4u^r
=(u^{-r}xu^r)x^3.
\tag{80}
\]

The left side generates \(b^{-1}Cb\), while \(x^3\in H\leq K\).
Therefore

\[
h_r:=u^{-r}xu^r\in K.
\tag{81}
\]

For every integer \(n\),

\[
u^{-r}x^n=h_r^n u^{-r}.
\tag{82}
\]

Since \(b^{-1}=u^{-r}x^{-\ell}\), all four terms on the left of
(36) are consequently the same \(K\)-coset:

\[
Kb^{-1}x^ig
=Ku^{-r}x^{i-\ell}g
=Ku^{-r}g.
\tag{83}
\]

Write \(\lambda=-\sigma\).  Equation (36) alone reduces to

\[
4s(Ku^{-r}g)=\lambda s(Kg)
\qquad(g\in B).
\tag{84}

Let

\[
m=\frac4{\gcd(4,r)}.
\]

Applying (84) successively at
\(g,u^{-r}g,\ldots,u^{-(m-1)r}g\) gives

\[
4^m s(Ku^{-rm}g)=\lambda^m s(Kg).
\tag{85}

But \(4\mid rm\), so

\[
u^{-rm}=(u^4)^{-rm/4}=x^{-3rm/4}\in H\leq K.
\]

Thus (85) is

\[
(4^m-\lambda^m)s(Kg)=0.
\tag{86}

For \(\lambda=\pm1\), the rational coefficient in (86) is nonzero.
Hence \(s=0\).  Section 8 gives a bijection between such scalar
solutions and dual edge currents, so the flow quotient has zero
algebraic dual.  A nonzero vector space over \(\mathbb Q\) always has
a nonzero linear functional; therefore the quotient itself is zero.
Equivalently, for every \(\ell,r\) in (79) and both signs \(\sigma\),

\[
(x^4-1)R+(yR_3-R_4)R+
(x^\ell y^{-1}x^ry+\sigma R_4)R
=R.
\tag{87}
\]

This is a complete failure theorem for the chosen flow obstruction,
not a primitivity theorem and not an Andrews--Curtis sequence.  In the
relevant negative exponent-zero fiber, the negative--positive
length-two classes therefore require a different invariant.  Together
with Section 12, this classifies the flow module on every
stable-letter-length-two exponent-zero double coset.

## 14. A finite-interface turn-transfer theorem

The previous three sections use two different mechanisms: open turns
are solved by interpolation on a tree, while a completely folded turn
is killed by nontrivial monodromy.  This section isolates the exact
linear statement common to both mechanisms.  Its hypotheses are not
asserted for every Britton word.

For fixed \(b\) and \(\sigma\), form the coefficient hypergraph
\(\mathscr X_{b,\sigma}\).  Its variable nodes are the cosets \(K_bg\).
It has two relation nodes \(I_g,O_g\), indexed by \(Hg\), with relation
vectors

\[
\sum_{i=0}^{3}[K_bb^{-1}x^ig]+\sigma[K_bg],
\qquad
\sum_{j=0}^{2}[K_bb^{-1}yx^jg]+\sigma[K_bg].
\tag{88}
\]

Repeated variable nodes in a stencil are retained with their
multiplicity.  The two vectors in (88) are independent of the chosen
representative of \(Hg\).  For the first vector, replacing \(g\) by
\(xg\) permutes the four targets modulo
\(b^{-1}Cb\leq K_b\); for the second it permutes the three targets by
\(yx^3=x^4y\), using the same subgroup inclusion.  By Section 8,
functions on the variable nodes annihilating every relation node of
\(\mathscr X_{b,\sigma}\) are exactly the scalar currents (36)--(37).

There is an unconditional finite object behind the subgroup \(K_b\),
although it does not by itself make the coefficient hypergraph finite.
Let \(T\) be the ordinary Bass--Serre tree, let \(v_0\) be the vertex
fixed by \(H\), and let \(e_0\) be the edge fixed by \(C\).  Let \(P_b\)
be the finite convex hull of \(v_0\) and \(b^{-1}e_0\), and put

\[
S_b=K_bP_b.
\]

This is connected.  A translate \(hP_b\), with \(h\in H\), meets
\(P_b\) at \(v_0\), while a translate \(qP_b\), with
\(q\in b^{-1}Cb\), meets \(P_b\) at \(b^{-1}e_0\).  Induction on a
word in the two generating subgroups joins every translate to
\(P_b\).  Therefore

\[
\Gamma_b=K_b\backslash S_b
\]

is a finite graph of cyclic groups covered by the image of the one
finite path \(P_b\), and Bass--Serre reconstruction gives
\(\pi_1(\Gamma_b)\cong K_b\).  Replacing \(b\) by \(cbh\), with
\(c\in C\) and \(h\in H\), leaves \(K_b\) unchanged and moves the
terminal marked edge within its \(K_b\)-orbit.  Thus the pointed
folded core is an invariant of the double coset \(CbH\).  It must be
decorated by the two stencils in (88): the abstract graph
\(\Gamma_b\) alone loses their placement.

The collisions internal to each stencil have an exact arithmetic
description.  Define

\[
\begin{aligned}
D_I(b)&=\{n\in\mathbb Z:b^{-1}x^nb\in K_b\}
       =d_I\mathbb Z,\\
D_O(b)&=\{n\in\mathbb Z:b^{-1}yx^ny^{-1}b\in K_b\}
       =d_O\mathbb Z.
\end{aligned}
\tag{89}
\]

Both are subgroups of \(\mathbb Z\).  Moreover \(4\mathbb Z\leq
D_I(b)\), directly from the definition of \(K_b\), and
\(3\mathbb Z\leq D_O(b)\), because
\(yx^3y^{-1}=x^4\).  Hence

\[
d_I\mid4,\qquad d_O\mid3.
\]

Two incoming targets with exponents \(i,j\) are equal precisely when
\(i-j\in D_I(b)\); two outgoing targets are equal precisely when
\(i-j\in D_O(b)\).  Combining equal terms, (36)--(37) therefore
become

\[
\frac4{d_I}\sum_{r=0}^{d_I-1}
s(K_bb^{-1}x^rg)=\lambda s(K_bg),
\tag{90}
\]

\[
\frac3{d_O}\sum_{r=0}^{d_O-1}
s(K_bb^{-1}yx^rg)=\lambda s(K_bg),
\qquad \lambda=-\sigma.
\tag{91}
\]

Thus an incoming stencil has exactly \(1,2\), or \(4\) distinct ports,
and an outgoing stencil has exactly \(1\) or \(3\).  These fold indices
are read from the endpoint stabilizers in the decorated
\(\Gamma_b\).  This proves all identifications *within* a stencil; it
does not remove the cross-stencil and adjacent-center collisions
(60)--(61).

Equations (90)--(91) also give an unconditional scalar-collapse
certificate.  If one fold index is \(1\), write its unique target as
\(K_bag\), and let \(q=4\) for the incoming stencil or \(q=3\) for the
outgoing stencil.  The corresponding equation is

\[
q\,s(K_bag)=\lambda s(K_bg).
\]

If \(a^m\in K_b\) for some \(m>0\), apply the equation successively at
\(g,ag,\ldots,a^{m-1}g\).  It follows that

\[
(q^m-\lambda^m)s(K_bg)=0.
\]

The coefficient is nonzero over \(\mathbb Q\), so every scalar current
vanishes and the flow ideal collapses.  Section 13 is the incoming
case \(a=u^{-r}\), \(q=4\), and
\(m=4/\gcd(4,r)\); the canonical cases in Section 6 are the length-one
returns.  When \(d_I=2\) or \(4\), or \(d_O=3\), a closed return is
intrinsically multiport unless further identifications are proved.

Here is the abstract elimination statement.  It is phrased as a
certificate so that none of the necessary finiteness is hidden.

**Finite-interface transfer lemma.**  Let \(\mathscr X\) be a linear
coefficient hypergraph over \(\mathbb Q\).  Suppose a decomposition of
\(\mathscr X\) supplies:

1. a finite-dimensional core-coordinate space \(Q_0\);
2. exterior full sub-hypergraphs \(U_\alpha\), each meeting the rest of
   the system only through a finite-dimensional port space
   \(P_{t(\alpha)}\), with only finitely many port types;
3. for each exterior piece, its solution space \(E_\alpha\), trace map
   \(\tau_\alpha:E_\alpha\to P_{t(\alpha)}\), and zero-trace space
   \(Z_\alpha=\ker\tau_\alpha\); and
4. a finite-rank factorization of all core equations and all port
   identifications as one linear map

\[
M:W\longrightarrow R_0,
\tag{92}
\]

   where \(W\) is a finite-dimensional space of core coordinates and
   surviving port coordinates.

Assume every required exterior trace lies in
\(\operatorname{im}\tau_\alpha\).  Equivalently, after replacing a
port by the subspace actually required in (92), every
\(\tau_\alpha\) is onto.  Then restriction to the finite interface
gives an exact sequence

\[
0\longrightarrow\prod_\alpha Z_\alpha
\longrightarrow \operatorname{Sol}(\mathscr X)
\longrightarrow\ker M\longrightarrow0.
\tag{93}
\]

The product in (93), rather than a direct sum, is essential: dual
currents are arbitrary functions and need not have finite support.

To prove the lemma, restrict a global solution to its core and port
coordinates.  The remaining equations say exactly that the resulting
finite vector lies in \(\ker M\).  A solution with zero finite trace
is an independent choice in \(Z_\alpha\) on every exterior piece,
which gives the kernel in (93).  Conversely, take a vector in
\(\ker M\).  Trace surjectivity chooses a lift in every \(E_\alpha\);
the exterior pieces share no relation away from their recorded ports,
so those lifts and the core vector glue to a global solution.  This
proves exactness.

Consequently, when \(\mathscr X=\mathscr X_{b,\sigma}\), the flow
ideal is proper if some \(Z_\alpha\ne0\) or \(\ker M\ne0\).  It
collapses if all \(Z_\alpha\) vanish and \(M\) is injective.  This is
an exact criterion for any exhibited finite-interface certificate; it
is not a claim that every \(\mathscr X_{b,\sigma}\) has such a
certificate.

There is also a useful open-tree form which does not require a finite
interface.  Suppose blocks are indexed by a rooted tree, a parent
block prescribes one finite-dimensional port datum in each child, and
the corresponding child trace is onto.  Any chosen solution in the
root block extends recursively to the whole tree.  This follows by
choosing one lift at each successive distance from the root.  Thus a
nonzero root solution gives a nonzero global current.  This is exactly
the logical form of the macro-tree construction in Section 12.

For a closed component with a one-dimensional surviving port, let
\(\mu_1,\ldots,\mu_m\) be the successive transfer scalars.  Its return
block in (92) is

\[
1-\prod_{i=1}^{m}\mu_i.
\tag{94}
\]

For a \(d\)-dimensional port it is instead
\(I-T_m\cdots T_1\).  Hence scalar monodromy is a special case; an
arbitrary closed fold need not reduce to one scalar recurrence.

The earlier results are consistent checks on the theorem.  For
\(b\in H\), all four targets in (36) fold to the center and the
one-dimensional return coefficient is \(4+\sigma\), which is
nonzero.  For Section 10, the outside-target lemma supplies the
required open one-parent interpolation and leaves a free root mode.
In Section 12, the direct ports collide, but the \(J_-\)-fiber
interpolation is onto for an individual value or any nonzero
functional on at most three vertices; the macro graph is a tree, so
again a free root mode extends.  In Section 13, the surviving port is
one-dimensional and (84) has transfer factor \(\lambda/4\).  The
return length is \(m=4/\gcd(4,r)\), so (94), after clearing
denominators, is \(4^m-\lambda^m\ne0\).

Two independent facts remain to be proved before this becomes an
arbitrary-Britton-word decision theorem:

1. the representative-indexed hypergraph \(\mathscr X_{b,\sigma}\)
   must have a finite-interface or finite-rank port decomposition;
   finite generation of \(K_b\) alone does not imply this, because the
   equations are indexed by \(H\backslash B\), not
   \(K_b\backslash B\);
2. every open exterior block in that decomposition must have the
   asserted trace-surjectivity property.

The second point already fails for the naive branch proof at the
length-three word \(b=y^2xy^{-1}\): Section 11 shows that both stencils
at the root lie behind the same hull edge, and (60)--(61) create
adjacent-center collisions.  This is a failure of that proposed proof,
not evidence of flow collapse.  Finally, an undecorated subgroup core
cannot decide the problem: \(b=1\) and \(b=yxy^{-1}\) both have
\(K_b=H\), but Sections 6 and 12 give opposite flow outcomes.  Any
successful corridor theorem must retain the two stencils and their
turn labels, not merely \(K_b\).  The necessity of this decoration
already appears at stable-letter length one: \(b=y\) and \(b=xy\)
both have \(K_b=H\), but Section 6 gives collapse for the first while
Section 10 gives propriety for the second.

## 15. A length-three same-sign family has scalar outgoing collapse

The countergeometry (62) does not require an open-port interpolation
theorem.  Its outgoing stencil folds completely.  This extends across
the first same-sign turn.  Put

\[
a=yxy^{-1},\qquad u=y^{-1}xy,
\]

and consider every normalized sign-\((+,+,-)\) code

\[
b_{\ell,p,r}
=x^\ell yx^pyx^ry^{-1}
=x^\ell a^pya^r,
\tag{95}
\]

where \(0\leq\ell<4\), \(0\leq p<3\), and \(r=1,2\).
The values \(r=0\bmod3\) Britton-reduce to the length-one stratum.
Define

\[
z_r=a^{-r}xa^r.
\tag{96}
\]

The subgroup \(K_b\) is independent of \(\ell\) and \(p\).  Indeed,
\(C=\langle x^4\rangle=\langle a^3\rangle\) is central in

\[
J_-=\langle x,a\mid x^4=a^3\rangle.
\]

Since \(x^\ell a^p\in J_-\), it centralizes \(C\), and hence

\[
b_{\ell,p,r}^{-1}Cb_{\ell,p,r}
=a^{-r}y^{-1}Cy a^r
=\langle a^{-r}x^3a^r\rangle
=\langle z_r^3\rangle.
\tag{97}
\]

Moreover \(z_r^4=a^{-r}x^4a^r=x^4\).  Therefore

\[
z_r=z_r^4(z_r^3)^{-1}\in K_b,
\qquad
K_b=\langle x,z_r\rangle.
\]

The exact subgroup presentation is

\[
K_b\cong
\langle x\rangle*_{\langle x^4=z_r^4\rangle}\langle z_r\rangle
=\langle x,z_r\mid x^4=z_r^4\rangle.
\tag{98}
\]

To prove this, use the Bass--Serre tree of
\(J_-=\langle x\rangle*_{\langle x^4=a^3\rangle}\langle a\rangle\).
The groups \(\langle x\rangle\) and
\(a^{-r}\langle x\rangle a^r=\langle z_r\rangle\) stabilize two
distinct \(H\)-vertices adjacent to the same
\(\langle a\rangle\)-vertex.  Their intersection is exactly
\(\langle x^4\rangle=\langle z_r^4\rangle\); amalgam normal form
proves (98).

The incoming fold index is always four.  Direct calculation gives

\[
b_{\ell,p,r}^{-1}x^nb_{\ell,p,r}
=a^{-r}x^{-p}u^nx^pa^r.
\tag{99}
\]

The infinite-line graph-of-groups normal form gives

\[
\langle u\rangle\cap J_-=\langle u^4\rangle
=\langle x^3\rangle.
\]

Thus (99) can lie in \(K_b\leq J_-\) only if \(4\mid n\).
Conversely \(u^{4k}=x^{3k}\), so the value for \(n=4k\) is
\(z_r^{3k}\in K_b\).  Hence

\[
d_I(b_{\ell,p,r})=4.
\tag{100}
\]

For the outgoing fold, one has

\[
b_{\ell,p,r}^{-1}yx^ny^{-1}b_{\ell,p,r}
=a^{-r}x^{-p}
\bigl(u^{-\ell}x^nu^\ell\bigr)
x^pa^r.
\tag{101}
\]

If \(4\mid\ell\), then \(u^\ell=x^{3\ell/4}\), so (101) is
\(z_r^n\in K_b\) for every \(n\).  If \(4\nmid\ell\), multiples of
three still work because \(x^3=u^4\) is central in
\(J_+=\langle x,u\mid x^3=u^4\rangle\).  For \(3\nmid n\), however,
\(u^{-\ell}x^nu^\ell\) is a reduced non-\(H\) word in \(J_+\).
The line-of-groups normal form

\[
\langle J_-,J_+\rangle=J_-*_{H}J_+
\]

then shows that (101) is not in \(J_-\), and hence not in \(K_b\).
Consequently

\[
d_O(b_{\ell,p,r})=
\begin{cases}
1,&\ell=0,\\
3,&\ell=1,2,3.
\end{cases}
\tag{102}
\]

Equations (36)--(37) themselves take the explicit form

\[
\sum_{i=0}^{3}
s(K_ba^{-r}x^{-p}u^{\,i-\ell}y^{-1}g)
=\lambda s(K_bg),
\tag{103}
\]

\[
\sum_{j=0}^{2}
s(K_ba^{-r}x^{-p}u^{-\ell}x^jg)
=\lambda s(K_bg),
\qquad\lambda=-\sigma.
\tag{104}
\]

The parameter \(p\) disappears from the entire scalar system.  For
every suffix \(q\in B\),

\[
K_ba^{-r}x^{-p}q
=K_bz_r^{-p}a^{-r}q
=K_ba^{-r}q.
\]

Thus the twenty-four normalized codes (95) yield only eight distinct
systems, indexed by \((\ell,r)\); the eighteen multiport codes below
yield only six.

When \(\ell=0\), the three targets in (104) are all
\(K_ba^{-r}g\), because
\(a^{-r}x^{j-p}=z_r^{\,j-p}a^{-r}\).  Thus

\[
3s(K_ba^{-r}g)=\lambda s(K_bg).
\]

Apply this successively at
\(g,a^{-r}g,a^{-2r}g\).  Since
\(a^{-3r}=x^{-4r}\in H\leq K_b\), one obtains

\[
(27-\lambda^3)s(K_bg)=0.
\]

The coefficient is \(26\) for \(\lambda=1\) and \(28\) for
\(\lambda=-1\).  Hence \(s=0\) over \(\mathbb Q\).  By the exact
duality in Section 8, for \(p=0,1,2\), \(r=1,2\), and both signs,

\[
(x^4-1)R+(yR_3-R_4)R+
(yx^pyx^ry^{-1}+\sigma R_4)R
=R.
\tag{105}
\]

This closes all six normalized sign-\((+,+,-)\) codes with
\(\ell=0\), representing two scalar systems, including (62).  For the
remaining eighteen codes, representing six scalar systems,
\(\ell=1,2,3\), the exact fold pair is \((d_I,d_O)=(4,3)\); neither
stencil is scalar, so this argument proves neither collapse nor
propriety.  As before, flow collapse is not a primitivity theorem and
not an Andrews--Curtis reduction.

## 16. Affine coinduction is blind to the exponent-one internal fiber

The standard affine action which starts the relative-free obstruction
cannot detect any internal element of \(y\)-exponent one, even after a
constant coefficient twist.  This is a representation-level no-go
theorem, independent of the fold calculation above.

Let \(V\) be a \(\mathbb Q\)-vector space and let
\(A\in\operatorname{GL}(V)\).  On the space \(V^{\mathbb Q}\) of all
functions \(f:\mathbb Q\to V\), define

\[
(f\cdot x)(t)=f(t-1),
\qquad
(f\cdot y)(t)=A f\!\left(\frac43t\right).
\tag{106}
\]

These operators give a right \(B\)-module.  Indeed,
right multiplication by \(y^{-1}\) sends \(f(t)\) to
\(A^{-1}f(3t/4)\), and direct substitution gives

\[
f\cdot(yx^3y^{-1})(t)=f(t-4)=f\cdot x^4(t).
\]

Equivalently, (106) is the coinduced action from the right affine
\(B\)-set

\[
t\cdot x=t+1,\qquad t\cdot y=\frac34t,
\]

with the \(y\)-action on values twisted by \(A\).

Let \(b\in B\) satisfy \(e_y(b)=1\).  Its affine action has the form

\[
t\cdot b=\frac34t+c_b
\]

for some \(c_b\in\mathbb Q\).  Therefore there is
\(d_b\in\mathbb Q\) such that

\[
(f\cdot b)(t)=A f\!\left(\frac43t+d_b\right).
\tag{107}
\]

More generally, induction on a word \(w\) gives
\[
(f\cdot w)(t)
=A^{e_y(w)}
f\!\left((4/3)^{e_y(w)}t+d_w\right)
\]
for a rational \(d_w\).  The coefficient factors are all powers of
the single operator \(A\), so their order introduces no additional
hypothesis on \(A\).

Suppose \(f\) satisfies the three module relations

\[
f\cdot(x^4-1)=0,\qquad
f\cdot(yR_3-R_4)=0,\qquad
f\cdot(b+\sigma R_4)=0.
\tag{108}
\]

Put

\[
S(t)=\sum_{k=0}^{3}f(t-k).
\]

The first relation makes \(f\) four-periodic and hence makes \(S\)
one-periodic.  The other two relations are

\[
A\sum_{k=0}^{2}
f\!\left(\frac43(t-k)\right)=S(t),
\tag{109}
\]

\[
A f\!\left(\frac43t+d_b\right)+\sigma S(t)=0.
\tag{110}
\]

Compare (110) at \(t\) and \(t+1\).  The right-hand values of \(S\)
are equal, \(A\) is invertible, and
\((4/3)t+d_b\) ranges over all of \(\mathbb Q\).  Consequently

\[
f(v+4/3)=f(v)
\qquad(v\in\mathbb Q).
\tag{111}
\]

All three summands on the left of (109) now coincide, so, with
\(v=4t/3\),

\[
S(t)=3A f(v).
\]

Substitution in (110) and cancellation of \(A\) give

\[
f(v+d_b)=-3\sigma f(v).
\tag{112}
\]

Because \(d_b\) is rational, there is an integer \(m>0\) such that
\(md_b\in(4/3)\mathbb Z\).  Iterating (112) \(m\) times and using
(111) yields

\[
\bigl(1-(-3\sigma)^m\bigr)f(v)=0.
\tag{113}
\]

The rational coefficient in (113) is nonzero, so \(f=0\).

Thus, for every \(b\in B\) with \(e_y(b)=1\), both signs \(\sigma\),
every coefficient space \(V\), and every invertible constant twist
\(A\), the module (106) contains no nonzero vector satisfying (108).
This does not say that the universal flow quotient is zero: it says
that the full affine coinduced family cannot witness its propriety.
In particular, changing the seed function, taking all functions
instead of finitely supported functions, or adding a constant
\(y\)-character cannot resolve the six multiport scalar systems left
open in Section 15.

## 17. The remaining multiport systems have infinite cross-incidence

Fix one of the six systems left open in Section 15:

\[
\ell\in\{1,2,3\},\qquad r\in\{1,2\}.
\]

The parameter \(p\) has already disappeared.  Put

\[
h=a^{-r},\qquad K=K_b=\langle x,z_r\rangle.
\]

The Bass--Serre normal form used in (98) also gives

\[
K\cap\langle a\rangle
=\langle a^3\rangle=\langle x^4\rangle.
\tag{114}
\]

The incoming equation (103) also loses its apparent \(\ell\)-shift.
Indeed,

\[
u^my^{-1}=y^{-1}x^m,
\]

and the four incoming targets are periodic modulo four by
\(d_I=4\).  Thus the two equations may be written

\[
\sum_{i=0}^{3}s(Khy^{-1}x^ig)=\lambda s(Kg),
\tag{115}
\]

\[
\sum_{j=0}^{2}s(Khu^{-\ell}x^jg)=\lambda s(Kg),
\qquad\lambda=-\sigma.
\tag{116}
\]

The system is not indexed by \(K\backslash B\).  Equations
(114)--(115) are required at every center \(Hg\).  In particular,
the centers \(Hkg\), with \(k\in K\), all have the same scalar value
\(s(Kg)\) but generally have different stencils.

Distinct \(H\)-centers over one \(K\)-center have no same-type
collisions.  More precisely, for \(k,k'\in K\), the outgoing stencils

\[
\{Khu^{-\ell}x^jkg:0\leq j<3\},
\qquad
\{Khu^{-\ell}x^jk'g:0\leq j<3\}
\]

intersect only if \(Hkg=Hk'g\), in which case they are the same
stencil with its usual modulo-three permutation.  To see this, an
equality of two targets forces

\[
hu^{-\ell}wu^\ell h^{-1}\in K,
\qquad
w=x^jkk'^{-1}x^{-j'}\in J_-.
\]

In the amalgam
\[
\langle J_-,J_+\rangle=J_-*_{H}J_+,
\]
if \(w\notin H\), the displayed word is reduced across the two vertex
groups and cannot lie in \(K\leq J_-\).  If \(w=x^n\), membership
forces \(3\mid n\), giving precisely the modulo-three permutation and
\(kk'^{-1}\in H\).

The incoming stencils over \(Hkg\) and \(Hk'g\) satisfy the analogous
statement with period four.  Here an equality reduces to

\[
y^{-1}x^ikk'^{-1}x^{-i'}y\in h^{-1}Kh\leq J_-.
\]

Since \(y^{-1}J_-y=J_+\), amalgam normal form forces
\[
x^ikk'^{-1}x^{-i'}\in K\cap\langle a\rangle
=\langle a^3\rangle=\langle x^4\rangle.
\]
Thus \(kk'^{-1}\in H\), and the two stencils differ only by their
usual modulo-four permutation.

The full cross-incidence can be classified exactly.  Return for a
moment to the original notation

\[
A_i(g)=Kb^{-1}x^ig,
\qquad
B_j(g)=Kb^{-1}yx^jg.
\tag{117}
\]

Every outgoing-relation center whose stencil contains \(A_i(g)\) is

\[
H\,y^{-1}bkb^{-1}x^ig
\qquad(k\in K).
\tag{118}
\]

Indeed, using the \(j=0\) representative of an outgoing stencil, the
condition is

\[
Kb^{-1}yq=Kb^{-1}x^ig.
\]

Solving this left-coset equality gives
\(q=y^{-1}bkb^{-1}x^ig\), and every \(k\in K\) gives a solution.
Similarly, every incoming-relation center whose stencil contains
\(B_j(g)\) is

\[
H\,bkb^{-1}yx^jg
\qquad(k\in K).
\tag{119}
\]

The repetitions in these two parameterizations are also exact.  Two
values \(k,k'\) in (117) give the same \(H\)-center precisely when

\[
kk'^{-1}\in K\cap b^{-1}\langle a\rangle b,
\]

while in (118) the condition is

\[
kk'^{-1}\in K\cap b^{-1}Hb.
\]

The fold equalities \(d_O=3\) and \(d_I=4\), respectively, give

\[
K\cap b^{-1}\langle a\rangle b
=K\cap b^{-1}Hb
=b^{-1}\langle x^4\rangle b
=\langle z_r^3\rangle.
\tag{120}
\]

Consequently every port in (116) belongs to an infinite family of
opposite-stencil equations indexed by

\[
\langle z_r^3\rangle\backslash K.
\tag{121}
\]

This coset space is infinite.  Quotienting the amalgam presentation
\(K=\langle x,z_r\mid x^4=z_r^4\rangle\) by its central subgroup
\(\langle x^4\rangle\) gives \(C_4*C_4\), in which the cyclic image
of \(\langle z_r^3\rangle\) has infinite index.

The adjacent-center identities (60)--(61) are only the \(k=1\)
members of (118)--(119).  Thus a local interpolation argument which
checks one adjacent relation, or even one finite family of adjacent
relations, is insufficient.  It must solve simultaneous compatibility
over the entire family (121).  Equations (114)--(121) are an exact
reduction of the remaining six systems, not a propriety or collapse
result.

## 18. Every finite-dimensional characteristic-zero module is blind

The affine no-go in Section 16 is a special case of a
representation-independent fact.  Let \(k\) be any field of
characteristic zero, let \(V\) be finite-dimensional over \(k\), and
let \(X,Y\in\operatorname{GL}(V)\) satisfy

\[
YX^3Y^{-1}=X^4.
\tag{122}
\]

Suppose a row vector \(v\in V\) satisfies the first two internal
relations

\[
v(X^4-I)=0,
\qquad
v\bigl(YR_3(X)-R_4(X)\bigr)=0.
\tag{123}
\]

Then necessarily

\[
vX=v,\qquad vY=\frac43v.
\tag{124}
\]

To prove this, extend scalars to an algebraic closure and list the
eigenvalues of \(X\), with multiplicity, as
\(\lambda_1,\ldots,\lambda_n\).  Similarity of \(X^3\) and \(X^4\)
gives a permutation \(\pi\) such that

\[
\lambda_i^3=\lambda_{\pi(i)}^4.
\]

If \(i\) lies on a \(\pi\)-cycle of length \(m\), iteration gives

\[
\lambda_i^{3^m}=\lambda_i^{4^m},
\qquad
\lambda_i^{\,4^m-3^m}=1.
\tag{125}
\]

The integer \(4^m-3^m\) is odd and congruent to \(1\pmod3\).
Consequently \(X\) has neither a nontrivial fourth root nor a
nontrivial cube root of unity as an eigenvalue.  Therefore both

\[
R_4(X)=I+X+X^2+X^3,
\qquad
R_3(X)=I+X+X^2
\]

are invertible.

Their determinants are already nonzero in \(k\), because they remain
nonzero after extension to the algebraic closure.  Hence the two
matrices are invertible over the original field, and all vector
equalities obtained after scalar extension descend along the
injective map \(V\to V\otimes_k\overline{k}\).

The first equation in (123) factors as

\[
0=v(X-I)R_4(X),
\]

so \(vX=v\).  Equation (122) also gives

\[
vY(X^3-I)=v(X^4-I)Y=0.
\]

Since \(X^3-I=(X-I)R_3(X)\), invertibility of \(R_3(X)\) gives
\(vYX=vY\).  The second equation in (123) now reduces to

\[
3vY=4v,
\]

which proves (124).

It follows that \(v\) affords the one-dimensional character

\[
x\longmapsto1,\qquad y\longmapsto4/3.
\]

Hence, for every \(b\in B\),

\[
vb=(4/3)^{e_y(b)}v.
\tag{126}
\]

If \(e_y(b)=1\), the third internal relation would require

\[
0=v\bigl(b+\sigma R_4(X)\bigr)
=\left(\frac43+4\sigma\right)v.
\tag{127}
\]

The coefficient is \(16/3\) for \(\sigma=+1\) and \(-8/3\) for
\(\sigma=-1\).  Thus \(v=0\).

Therefore no finite-dimensional characteristic-zero representation of
\(B\) contains a nonzero vector annihilated by the three internal
relations for any \(b\) with \(e_y(b)=1\).  This includes all six open
systems in Section 17, but it does not prove their flow quotients
collapse: Result 61 gives proper exponent-one ideals whose annihilating
currents are necessarily infinite-dimensional.

## 19. Exact three-phase correspondence over the \(C_4*C_4\) tree

The infinite cross-incidence in Section 17 has a canonical operator
form.  Fix one of its six systems and write

\[
z=z_r,\qquad
c=x^4=z^4,\qquad
C=\langle c\rangle,\qquad
L=\langle z^3\rangle=b^{-1}Cb.
\]

Then

\[
K=\langle x\rangle*_{C}\langle z\rangle.
\tag{128}
\]

Define three coset spaces

\[
V=K\backslash B,\qquad
W=H\backslash B,\qquad
\Omega=L\backslash B
\]

and maps

\[
\begin{aligned}
p:\Omega&\longrightarrow V,&p(Ld)&=Kd,\\
\rho:W&\longrightarrow V,&\rho(Hg)&=Kg,\\
q_I:\Omega&\longrightarrow W,&q_I(Ld)&=Hbd,\\
q_O:\Omega&\longrightarrow W,&q_O(Ld)&=Hy^{-1}bd.
\end{aligned}
\tag{129}
\]

These maps are well-defined.  The first two use \(L,H\leq K\).  For
the other two,

\[
bLb^{-1}=C\leq H,
\qquad
y^{-1}bLb^{-1}y
=y^{-1}Cy=\langle x^3\rangle\leq H.
\]

The two \(q\)-maps have finite fibers:

\[
q_I^{-1}(Hg)
=\{Lb^{-1}x^ig:0\leq i<4\},
\tag{130}
\]

\[
q_O^{-1}(Hg)
=\{Lb^{-1}yx^jg:0\leq j<3\}.
\tag{131}
\]

The entries in each displayed fiber are distinct by
\([H:C]=4\) and
\([H:\langle x^3\rangle]=3\), respectively.  In contrast,

\[
p^{-1}(Kd)=\{Lkd:k\in K\}
\cong L\backslash K
\tag{132}
\]

is infinite.

For a finite-fiber map \(q\), write \(q_!\) for summation over its
fibers, and write \(p^*,\rho^*\) for pullback of arbitrary
\(\mathbb Q\)-valued functions.  Equations (36)--(37) are exactly

\[
\mathcal A_\lambda(s)=0,
\tag{133}
\]

where

\[
\mathcal A_\lambda:
\mathbb Q^V\longrightarrow\mathbb Q^W\oplus\mathbb Q^W,
\qquad
\mathcal A_\lambda(s)=
\bigl(q_{I!}p^*s-\lambda\rho^*s,\,
      q_{O!}p^*s-\lambda\rho^*s\bigr).
\tag{134}
\]

Indeed, (130)--(131) give

\[
(q_{I!}p^*s)(Hg)
=\sum_{i=0}^{3}s(Kb^{-1}x^ig),
\]

\[
(q_{O!}p^*s)(Hg)
=\sum_{j=0}^{2}s(Kb^{-1}yx^jg).
\]

Consequently

\[
\operatorname{Sol}_{\ell,r,\sigma}
=\ker\mathcal A_{-\sigma}.
\tag{135}
\]

The correspondence (129) has a canonical decorated-tree
interpretation.  Quotienting (128) by the central subgroup \(C\)
gives

\[
K/C\cong C_4*C_4.
\]

The Bass--Serre tree \(T\) is the \((4,4)\)-biregular tree with

\[
V_X(T)=H\backslash K,\qquad
V_Z(T)=\langle z\rangle\backslash K,\qquad
E(T)=C\backslash K.
\tag{136}
\]

The cross-index set in (132) maps to the \(Z\)-vertices:

\[
L\backslash K\longrightarrow\langle z\rangle\backslash K.
\tag{137}
\]

Every fiber has three elements because
\([\langle z\rangle:L]=3\).  Moreover,

\[
C\cap L=\langle c^3\rangle.
\]

Right multiplication by \(c\) therefore fixes the underlying
\(Z\)-vertex and cyclically permutes the three points above it.
Thus (137) is a canonical three-phase decoration of the \(Z\)-vertex
set.  Forgetting the phase merges distinct relation centers.

All of Section 17's cross-incidences are retained in (129).  For each
\(v=Kd\), both \(q_I\) and \(q_O\) restrict injectively to
\(p^{-1}(v)\).  This is exactly the pair of intersection equalities

\[
K\cap b^{-1}Hb
=K\cap b^{-1}\langle a\rangle b
=L
\]

from (120).  Evaluating \(q_O\) on
\(Lk\,b^{-1}x^ig\) gives every center in (118), while evaluating
\(q_I\) on \(Lk\,b^{-1}yx^jg\) gives every center in (119).

The operator (134) is row-finite, but it has infinite column
incidence: every retained variable is seen by all phases over all
vertices in (137).  There is no algebraic pushforward \(p_!\) on
arbitrary currents, because the fibers (132) are infinite.  Therefore
one cannot obtain a legitimate finite return operator by simply
composing the four maps in (129), and every finite tree truncation
omits infinitely many equations incident to each retained port.

The remaining problem is now the exact alternative

\[
\ker\mathcal A_\lambda\ne0
\quad\text{or}\quad
\mathcal A_\lambda\text{ is injective}.
\tag{138}
\]

This correspondence theorem proves neither side of (138).  It isolates
the missing step as an infinite-dimensional kernel problem on a
three-phase decorated \((4,4)\)-tree, with no finite-truncation
inference.

## 20. Coinduction and the exact finite-support target

For a subgroup \(S\leq B\), distinguish the all-functions and
finite-support permutation modules

\[
\mathscr C_S=\mathbb Q^{S\backslash B}
=\operatorname{Coind}_S^B(\mathbf1),
\qquad
\mathscr I_S=\mathbb Q[S\backslash B]
=\operatorname{Ind}_S^B(\mathbf1).
\tag{139}
\]

The maps \(q_{I!},q_{O!}\) in Section 19 are the conjugated
corestriction maps from \(\mathscr C_L\) to \(\mathscr C_H\), of
degrees four and three.  Thus \(\mathcal A_\lambda\) is a pair of
restriction--corestriction Mackey operators, not an endomorphism of
one ordinary Hecke module.

Under the natural pairings

\[
\mathscr I_S\times\mathscr C_S\longrightarrow\mathbb Q,
\]

the algebraic transpose of \(\mathcal A_\lambda\) is the
finite-support map

\[
D_\lambda:
\mathscr I_H\oplus\mathscr I_H\longrightarrow\mathscr I_K
\tag{140}
\]

defined on basis vectors by

\[
D_\lambda([Hg],0)
=\sum_{i=0}^{3}[Kb^{-1}x^ig]-\lambda[Kg],
\tag{141}
\]

\[
D_\lambda(0,[Hg])
=\sum_{j=0}^{2}[Kb^{-1}yx^jg]-\lambda[Kg].
\tag{142}
\]

Therefore

\[
\ker\mathcal A_\lambda
\cong\bigl(\operatorname{coker}D_\lambda\bigr)^\vee.
\tag{143}
\]

In particular, \(\mathcal A_\lambda\) is injective exactly when
\(D_\lambda\) is surjective.  The right \(B\)-action is transitive on
\(K\backslash B\), so surjectivity is equivalent to the single
condition

\[
[K]\in\operatorname{im}D_\lambda.
\tag{144}
\]

Condition (144) is one explicit finite-support identity.  It asks for
finitely supported functions

\[
\alpha,\beta:H\backslash B\longrightarrow\mathbb Q
\]

such that, for every \(d\in B\),

\[
\begin{aligned}
&\sum_{Lk\in L\backslash K}\alpha(Hbkd)
+\sum_{Lk\in L\backslash K}\beta(Hy^{-1}bkd)\\
&\qquad
-\lambda\sum_{Hk\in H\backslash K}
\bigl(\alpha(Hkd)+\beta(Hkd)\bigr)
=\mathbf1_{\{Kd=K\}}.
\end{aligned}
\tag{145}
\]

Every sum in (145) is finite despite its infinite index set, because
\(\alpha,\beta\) have finite support.  The first two sums enumerate
all target-row incidences through the \(p\)-fiber
\(L\backslash K\); the last sum enumerates all relation centers whose
center variable is \(Kd\).  Thus (145) retains every \(H\)-row and
every phase from Section 19.

If (145) is impossible, the class of \([K]\) is nonzero in
\(\operatorname{coker}D_\lambda\).  Choose a linear functional
\(\varphi\) on that cokernel with

\[
\varphi([K])=1.
\]

Then

\[
s(Kd)=\varphi([Kd])
\]

is a nonzero algebraic current in \(\ker\mathcal A_\lambda\).  No
summability is required.  Conversely, a solution of (145) proves
\(D_\lambda\) surjective and hence \(\ker\mathcal A_\lambda=0\).

Thus the six remaining flow problems are exactly the question whether
the finite identity (145) exists.  The three-phase tree specifies all
of its incidences but does not by itself decide membership (144).
No outcome is claimed here.

## 21. The amalgam resolution makes the target locally finite

The infinite column incidence in Section 20 can be removed without
discarding any equation.  Put

\[
Z=\langle z\rangle,
\qquad K=H*_C Z,
\qquad C=\langle x^4\rangle=\langle z^4\rangle.
\tag{146}
\]

The cellular chain complex of the Bass--Serre tree of (146), summed
over the right \(K\)-cosets in \(B\), is the exact sequence of right
\(B\)-modules

\[
0\longrightarrow \mathscr I_C
\xrightarrow{\partial}
\mathscr I_H\oplus\mathscr I_Z
\xrightarrow{\varepsilon}
\mathscr I_K\longrightarrow0,
\tag{147}
\]

where

\[
\partial[Cg]=([Hg],-[Zg]),
\qquad
\varepsilon([Hg],0)=\varepsilon(0,[Zg])=[Kg].
\tag{148}
\]

Define two finite-fiber maps

\[
\begin{aligned}
P_I[Hg]&=\sum_{i=0}^{3}[Zb^{-1}x^ig],\\
P_O[Hg]&=\sum_{j=0}^{2}[Zb^{-1}yx^jg].
\end{aligned}
\tag{149}
\]

They are well-defined on \(H\backslash B\).  In the first line, a
change \(g\mapsto xg\) permutes the four terms because
\(b^{-1}x^4b=z^3\in Z\).  In the second, it permutes the three terms
because \(yx^3=x^4y\) and again \(b^{-1}x^4b=z^3\).

The map \(D_\lambda\) from (140) lifts through (147) as

\[
\widetilde D_\lambda(\alpha,\beta)
=\bigl(-\lambda(\alpha+\beta),\,
P_I\alpha+P_O\beta\bigr),
\qquad
\varepsilon\widetilde D_\lambda=D_\lambda.
\tag{150}
\]

Since \(\lambda=\pm1\), the first coordinate in (150) can be
eliminated exactly.  If

\[
\pi_H:\mathscr I_C\to\mathscr I_H,
\qquad
\pi_Z:\mathscr I_C\to\mathscr I_Z
\]

are the natural projections, define

\[
E_\lambda:\mathscr I_H\oplus\mathscr I_C
\longrightarrow\mathscr I_Z
\tag{151}
\]

by

\[
E_\lambda(\mu,\nu)
=(P_I-P_O)\mu
+(P_I\pi_H-\lambda\pi_Z)\nu.
\tag{152}
\]

Then elementary elimination in the cokernel of
\((\partial,\widetilde D_\lambda)\) gives a canonical isomorphism

\[
\operatorname{coker}D_\lambda
\cong\operatorname{coker}E_\lambda.
\tag{153}
\]

Explicitly, the relation
\((-\lambda[Hg],P_I[Hg])=0\) replaces the \(H\)-coordinate by
\(\lambda^{-1}P_I[Hg]\).  The second \(H\)-row then becomes
\((P_O-P_I)[Hg]\), and the edge relation in (148) becomes, after
clearing the unit \(\lambda\),
\((P_I\pi_H-\lambda\pi_Z)[Cg]\).  This proves (153), including its
signs.  Under (153), the class of \([K]\) is the class of \([Z]\).

Consequently the six open systems have the equivalent finite-support
target

\[
[Z]\stackrel{?}{\in}\operatorname{im}E_\lambda.
\tag{154}
\]

Unlike \(D_\lambda\), the presentation (151)--(152) is locally finite
in both directions.  Its two kinds of rows have respectively seven
and five terms.  A fixed variable \([Zd]\) occurs in only finitely
many rows.  Indeed, (120) gives

\[
Z\cap b^{-1}Hb
=Z\cap b^{-1}yHy^{-1}b
=L=\langle z^3\rangle.
\tag{155}
\]

Thus the \(P_I\)-rows containing \([Zd]\) are
\(Hbz^nd\), and the \(P_O\)-rows are
\(Hy^{-1}bz^nd\), with \(n\bmod3\).  For the second summand of
(152), each of the three \(P_I\)-centers has four lifts from
\(H\backslash B\) to \(C\backslash B\), while the center term has
the four lifts \(Cz^qd\), \(q\bmod4\).  Hence a column meets at most
six rows of the first kind and sixteen of the second.

Writing (154) coefficientwise gives a completely fixed-valence
identity.  It asks for finitely supported

\[
\mu:H\backslash B\to\mathbb Q,
\qquad
\nu:C\backslash B\to\mathbb Q
\]

such that, for every \(d\in B\),

\[
\begin{aligned}
&\sum_{n=0}^{2}\mu(Hbz^nd)
-\sum_{n=0}^{2}\mu(Hy^{-1}bz^nd)\\
&\quad
+\sum_{n=0}^{2}\sum_{q=0}^{3}
  \nu(Cx^qbz^nd)
-\lambda\sum_{q=0}^{3}\nu(Cz^qd)
=\mathbf1_{\{Zd=Z\}}.
\end{aligned}
\tag{156}
\]

All four sums in (156) have fixed finite ranges; no hidden
\(L\backslash K\) fiber remains.  Thus a finite-support
leaf-elimination, leading-term, or matching proof may now be carried
out on an honest locally finite coefficient hypergraph.  Equations
(153)--(156) do not decide whether that proof yields a separator or a
certificate, so they prove neither propriety nor collapse by
themselves.

## 22. Leaf elimination decides all six locally finite systems

The locally finite presentation does admit a global leaf argument.
It proves propriety for every system left open in Section 15.

Recall \(h=a^{-r}\), so \(z=hxh^{-1}\) and
\(Z=hHh^{-1}\).  There is a right \(B\)-equivariant bijection

\[
\Theta:Z\backslash B\longrightarrow H\backslash B,
\qquad
\Theta(Zd)=Hh^{-1}d=Ha^rd.
\tag{157}
\]

Use the directed Bass--Serre tree \(\mathcal T\) of \(B\), with

\[
\operatorname{ini}(Cg)=Hy^{-1}g,
\qquad
\operatorname{ter}(Cg)=Hg.
\tag{158}
\]

Every vertex has four incoming predecessors and three outgoing
successors.  For the general representative

\[
b=x^\ell a^pya^r
\]

from (95), one has

\[
h^{-1}b^{-1}
=x^{-p}y^{-1}x^{-\ell}.
\]

The initial \(x^{-p}\) is absorbed by the left \(H\)-coset.  Therefore

\[
\Theta(Zb^{-1}x^ig)
=Hy^{-1}x^{i-\ell}g,
\tag{159}
\]

and these are exactly the four incoming predecessors of \(Hg\).
Similarly,

\[
\Theta(Zb^{-1}yx^jg)
=Hu^{-\ell}x^jg.
\tag{160}
\]

For each outgoing successor

\[
s_j=Hyx^jg
\]

of \(v=Hg\), its four incoming predecessors are
\(Hu^kx^jg\), \(k\bmod4\).  The vertex \(v\) is phase \(k=0\), while
the target in (160) is the nontrivial phase \(k=-\ell\).  It is
different from \(v\) because \(\ell\in\{1,2,3\}\).

Thus, after applying \(\Theta\), a row
\((P_I-P_O)[Hg]\), centered at \(v\), has:

1. coefficient \(+1\) at all four incoming predecessors of \(v\);
2. for each of the three outgoing successors \(s\) of \(v\),
   coefficient \(-1\) at one fixed nontrivial-phase predecessor of
   \(s\).

The edge rows have an equally local description.  Let \(e=Cg\), with

\[
q=\operatorname{ini}(e)=Hy^{-1}g,
\qquad
v=\operatorname{ter}(e)=Hg.
\]

The \(P_I\pi_H\)-part is \(+1\) at all four incoming predecessors of
\(v\).  The remaining target is

\[
\Theta(Zg)=Ha^rg.
\tag{161}
\]

The three outgoing successors of \(q\) are \(Ha^jg\),
\(j\bmod3\).  The vertex \(v\) is phase zero and (161) is the
nontrivial phase \(r\in\{1,2\}\).  Consequently a row
\((P_I\pi_H-\lambda\pi_Z)[Cg]\) has:

1. coefficient \(+1\) at all four incoming predecessors of
   \(\operatorname{ter}(e)\);
2. coefficient \(-\lambda\) at one fixed nontrivial-phase outgoing
   successor of \(\operatorname{ini}(e)\).

We now rule out a finite certificate.  Suppose

\[
E_\lambda(\mu,\nu)=[Z]
\tag{162}
\]

for finitely supported \(\mu,\nu\), and put

\[
o=\Theta(Z)=Ha^r.
\]

Let \(Q\subset\mathcal T\) be the finite convex hull of \(o\), every
vertex on which \(\mu\) is nonzero, and both endpoints of every edge
on which \(\nu\) is nonzero.

Assume first that \(Q\) has a leaf \(v\ne o\).  Choose an outgoing
edge \(v\to s\) outside \(Q\).  At least two such edges exist.  Let
\(w\ne v\) be the fixed phase-\(-\ell\) predecessor of \(s\) used by
the \(\mu(v)\)-row.  Then \(w\notin Q\).  Among rows whose centers or
edge endpoints lie in \(Q\), only the row centered at \(v\) contains
\(w\): a positive vertex contribution would be centered beyond
\(w\); a negative vertex contribution through \(s\) has center \(v\)
by injectivity of the four-phase turn; a positive edge contribution
has terminal beyond \(w\); and a negative edge contribution is based
at a predecessor of \(w\), again outside \(Q\).  Taking the
\(w\)-coefficient in (162) gives

\[
-\mu(v)=0.
\tag{163}
\]

It remains to eliminate the only possible supported edge incident to
the leaf \(v\).

If that edge is \(e:q\to v\), then the other three incoming
predecessors of \(v\) lie outside \(Q\).  At most one is the
phase-\(-\ell\) target of a possible row centered at \(q\).  Choose
another, \(w\).  The only supported contribution at \(w\), after
(163), is the positive occurrence in the \(e\)-row.  Hence

\[
\nu(e)=0.
\tag{164}
\]

If instead the edge is \(e:v\to q\), let \(w\) be the fixed
nontrivial phase-\(r\) successor of \(v\) selected by its negative
term.  The turn is nontrivial, so \(w\) lies outside \(Q\).  Its only
supported contributor is the \(e\)-row, and therefore

\[
-\lambda\nu(e)=0.
\tag{165}
\]

Since \(\lambda=\pm1\), (164)--(165) both kill the edge coefficient.
Every leaf of the convex hull belongs to its defining finite set.
Thus a non-target leaf would support \(\mu\) or be an endpoint of a
supported edge, contradicting (163)--(165).

A finite tree with more than one vertex has at least two leaves, only
one of which can be \(o\).  Hence \(Q=\{o\}\).  Then \(\nu=0\) and
\(\mu\) can be supported only at \(o\).  Applying the same outward
target argument at \(o\) gives \(\mu(o)=0\), contradicting (162).
We have proved

\[
[Z]\notin\operatorname{im}E_\lambda
\tag{166}
\]

for every \(\ell=1,2,3\), \(r=1,2\), and
\(\lambda=\pm1\).

By (153), \(D_\lambda\) is not surjective.  Equations (143) and (135)
then give

\[
\ker\mathcal A_\lambda\ne0.
\tag{167}
\]

Therefore, for all \(p=0,1,2\), all \(\ell=1,2,3\), all \(r=1,2\),
and both signs \(\sigma\), the right ideal

\[
(x^4-1)R+(yR_3-R_4)R
+(b_{\ell,p,r}+\sigma R_4)R
\]

is proper.  Together with the scalar collapse at \(\ell=0\), this
decides the internal flow quotient for every normalized
sign-\((+,+,-)\) length-three code in (95).  Flow collapse proves
only failure of this obstruction.  The next section records the
separate implication from flow propriety to nonprimitivity in the
A--D application; neither outcome is itself an Andrews--Curtis
theorem.

## 23. Exact return from internal flow to the A--D Fox row

For completeness, propriety of the internal flow ideal is not merely
an analogy to the earlier relative-free obstruction.  It supplies the
same nonprimitivity certificate without the relative-free hypothesis.

Let

\[
J_{b,\sigma}
=(x^4-1)\mathbb Q[B]
+(yR_3-R_4)\mathbb Q[B]
+(b+\sigma R_4)\mathbb Q[B].
\tag{168}
\]

Suppose \(J_{b,\sigma}\ne\mathbb Q[B]\), and put

\[
W=\mathbb Q[B]/J_{b,\sigma},
\qquad w=1+J_{b,\sigma}\ne0.
\]

Then

\[
w(x^4-1)=0,\qquad
w(yR_3-R_4)=0,\qquad
w(b+\sigma R_4)=0.
\tag{169}
\]

Let \(G=B*\langle z\rangle\) and induce \(W\) to a right
\(\mathbb Q[G]\)-module:

\[
M=W\otimes_{\mathbb Q[B]}\mathbb Q[G].
\tag{170}
\]

The group ring \(\mathbb Q[G]\) is free as a left
\(\mathbb Q[B]\)-module on right-coset representatives.  Hence
\(W\to M\), \(w\mapsto w\otimes1\), is injective; retain the notation
\(w\ne0\) for its image.

Set

\[
t=zxz^{-1},\qquad q=zy,\qquad
g=zbz^{-1},\qquad v=wz^{-1}.
\tag{171}
\]

Right multiplication by \(z^{-1}\) is invertible, so \(v\ne0\).
The three relations (169) give

\[
v(t^4-1)=0,
\qquad
v\bigl(g+\sigma R_4(t)\bigr)=0,
\tag{172}
\]

\[
v\bigl(qR_3-R_4(t)z\bigr)=0.
\tag{173}
\]

The literal evaluated A--D Fox row is

\[
\left(
qR_3+\sigma gt^{-1}z,\;
-R_4(t)-\sigma gt^{-1},\;
\sigma g(t^{-1}-1),\;
1-t^4
\right).
\tag{174}
\]

Equation (172) gives \(vt^{-1}=vt^3\), and therefore
\(vR_4(t)t^{-1}=vR_4(t)\).  Using (172)--(173), the four coordinates
of (174) annihilate \(v\), exactly as in the noninternal
relative-free calculation.  Thus (174) is not right-unimodular over
\(\mathbb Q[G]\).

If an A--D relative product \(P_\sigma(c)\) is primitive, its Fox row
is right-unimodular over the integral free-group ring, and every
evaluation of that row remains right-unimodular after scalar
extension.  Consequently, whenever its evaluated internal parameter
is

\[
g=zbz^{-1}
\]

and \(J_{b,\sigma}\) is proper, \(P_\sigma(c)\) is nonprimitive.
This implication applies in particular to the proper families in
Sections 10, 12, and 22.  A collapsed flow quotient gives no converse:
it neither proves primitivity nor supplies an Andrews--Curtis
reduction.

## 24. The positive--negative--positive length-three stratum

Consider the other normalized exponent-one length-three family

\[
b_{\ell,p,q}
=x^\ell yx^py^{-1}x^qy,
\qquad
0\leq\ell<4,\quad
p=1,2,\quad q=1,2,3.
\tag{175}
\]

Put \(a=yxy^{-1}\).  Then

\[
b_{\ell,p,q}=x^\ell a^px^qy=ny,
\qquad
n=x^\ell a^px^q\in
J_-=\langle x\rangle*_{C}\langle a\rangle.
\]

The subgroup \(C=\langle x^4\rangle=\langle a^3\rangle\) is central
in \(J_-\).  Hence

\[
b^{-1}Cb
=y^{-1}n^{-1}Cny
=y^{-1}Cy
=\langle x^3\rangle,
\]

and therefore

\[
K_b=\langle H,b^{-1}Cb\rangle=H.
\tag{176}
\]

Both stencil folds are open.  For the incoming one,

\[
b^{-1}x^mb
=y^{-1}
\bigl(x^{-q}a^{-p}x^ma^px^q\bigr)y.
\tag{177}
\]

The value in (177) lies in \(H\) exactly when the parenthesized word
lies in \(\langle a\rangle\).  If \(4\nmid m\), it is a reduced
five-syllable word in
\(\langle x\rangle*_{C}\langle a\rangle\), since
\(p\not\equiv0\pmod3\) and \(q\not\equiv0\pmod4\).  If \(4\mid m\),
centrality of \(C\) gives membership.  Thus \(d_I=4\).

Similarly,

\[
b^{-1}yx^my^{-1}b
=y^{-1}
\bigl(
x^{-q}a^{-p}x^{-\ell}a^mx^\ell a^px^q
\bigr)y.
\tag{178}
\]

If \(3\mid m\), the middle power \(a^m\) lies in the central subgroup
\(C\).  If \(3\nmid m\), the inner word is reduced and does not lie in
\(\langle a\rangle\); when \(\ell=0\), it reduces only to
\(x^{-q}a^mx^q\), which has the same conclusion.  Hence

\[
(d_I,d_O)=(4,3).
\tag{179}
\]

Since \(K_b=H\), the exact scalar equations are, for every \(g\in B\),

\[
\sum_{i=0}^{3}
s\!\left(
Hy^{-1}x^{-q}yx^{-p}y^{-1}x^{i-\ell}g
\right)
=\lambda s(Hg),
\tag{180}
\]

\[
\sum_{j=0}^{2}
s\!\left(
Hy^{-1}x^{-q}yx^{-p}y^{-1}x^{-\ell}yx^jg
\right)
=\lambda s(Hg),
\qquad\lambda=-\sigma.
\tag{181}
\]

Their geometry in the ordinary Bass--Serre tree is exact.  Every
target in (180) is at distance three from its center, one in each
incoming branch.  Reading from the center outward, the internal turns
are the nonzero phases \(p\bmod3\) and \(q\bmod4\).

If \(\ell\ne0\), every target in (181) is at distance four, one in
each outgoing branch; all three internal phases
\(\ell\bmod4\), \(p\bmod3\), and \(q\bmod4\) are nonzero.  If
\(\ell=0\), the middle \(y^{-1}y\) cancels and (181) becomes

\[
\sum_{j=0}^{2}
s\!\left(
Hy^{-1}x^{-q}yx^{j-p}g
\right)
=\lambda s(Hg).
\tag{182}
\]

Its three targets are at distance two, one in each outgoing branch,
and the \(q\)-turn is nontrivial.

This distance separation gives a finite-support leaf proof.  Let

\[
D_\lambda:
\mathbb Q[H\backslash B]^2
\longrightarrow\mathbb Q[H\backslash B]
\]

be the transpose of (180)--(181), and suppose

\[
D_\lambda(\alpha,\beta)=[H]
\tag{183}
\]

with finite support.  Let \(Q\) be the finite convex hull of the
target \(H\) and all centers supporting \(\alpha\) or \(\beta\).
Choose a non-target leaf \(v\), with inward neighbor \(u\).

If \(\ell\ne0\), choose an outward outgoing branch of \(v\) and its
distance-four target from the \(\beta(v)\)-row.  Every other supported
center is at least distance five from that target, while every row has
radius at most four.  Its coefficient in (183) is therefore
\(\beta(v)\), so \(\beta(v)=0\).  Next choose a distance-three
incoming target of the \(\alpha(v)\)-row.  Only a radius-four row at
\(u\) could also reach it, and that row can use at most one of the at
least three outward incoming branches.  Choosing another branch
forces \(\alpha(v)=0\).

If \(\ell=0\), first choose a distance-three incoming target.  Every
other center is at least distance four from it and all rows have
radius at most three, so \(\alpha(v)=0\).  Then choose a distance-two
outgoing target.  A radius-three row at \(u\) can collide through at
most one outgoing branch of \(v\).  Another outward branch exists and
isolates \(\beta(v)\), forcing \(\beta(v)=0\).

Thus no non-target leaf can belong to the defining support of \(Q\).
A nontrivial finite tree has at least two leaves, so \(Q=\{H\}\).
The same maximum-radius argument at \(H\) first kills the longer row
and then the shorter one, contradicting (183).  Consequently

\[
[H]\notin\operatorname{im}D_\lambda.
\tag{184}
\]

It follows that, for all twenty-four normalized words (175) and both
signs,

\[
(x^4-1)\mathbb Q[B]
+(yR_3-R_4)\mathbb Q[B]
+(b_{\ell,p,q}+\sigma R_4)\mathbb Q[B]
\ne\mathbb Q[B].
\tag{185}
\]

The bridge in Section 23 therefore obstructs the corresponding
internal A--D relative products from being primitive.  This closes
the flow and Fox-primitivity questions for the whole
sign-\((+,-,+)\) length-three stratum, not the Andrews--Curtis
conjecture.

## 25. The negative--positive--positive three-phase reduction

The remaining exponent-one length-three sign pattern has normalized
representatives

\[
b_{\ell,p,q}
=x^\ell y^{-1}x^pyx^qy,
\qquad
0\leq\ell<4,\quad
p=1,2,3,\quad q=0,1,2.
\tag{186}
\]

Put \(u=y^{-1}xy\), \(a=yxy^{-1}\), and define

\[
t=b^{-1}xb,\qquad
w=b^{-1}ab,\qquad
s=b^{-1}x^4b=t^4=w^3.
\tag{187}
\]

The relevant cyclic intersections have a larger index than in the
previous two strata.  Since

\[
b=x^\ell u^px^qy
\]

and \(x^3=u^4\) is central in

\[
J_+=\langle x\rangle*_{\langle x^3=u^4\rangle}\langle u\rangle,
\]

amalgam normal form gives

\[
H\cap\langle t\rangle
=\langle t^{12}\rangle
=\langle x^9\rangle.
\tag{188}
\]

Indeed, collapsing the \(u^{-p}x^mu^p\) turn first requires
\(3\mid m\), and entering \(yHy^{-1}\cap H=\langle x^4\rangle\)
then requires \(4\mid m\).  For \(m=12k\), centrality gives

\[
t^{12k}=b^{-1}x^{12k}b=x^{9k}.
\]

Let

\[
J'=b^{-1}J_-b
=\langle t\rangle*_{\langle s\rangle}\langle w\rangle,
\qquad
J_-=\langle x\rangle*_{\langle x^4=a^3\rangle}\langle a\rangle.
\]

The exact combination statement needed below is

\[
\langle H,J'\rangle
=H*_{\langle x^9\rangle}J'.
\tag{189}
\]

To verify it, conjugate by \(y\).  The first factor becomes
\(\langle a\rangle\), while the second becomes
\(n^{-1}J_-n\), where \(n=x^\ell u^px^q\).  In the Bass--Serre tree
of \(J_-*_{H}J_+\), the two \(J_-\)-vertices are distinct because
\(u^p\notin H\).  Their path stabilizer is
\(\langle x^3\rangle\), and

\[
\langle a\rangle\cap\langle x^3\rangle
=\langle x^{12}\rangle
=\langle a^9\rangle.
\]

Every alternating word whose factors lie outside this intersection
retains a nonedge syllable on each side of that path and is therefore
reduced.  This proves the corresponding amalgam normal form;
conjugating back gives (189).

Put

\[
L=\langle s\rangle,
\qquad
A_9=\langle x^9\rangle=\langle s^3\rangle.
\]

Since \(A_9\leq L\leq J'\), (189) implies

\[
K_b=\langle H,L\rangle
=H*_{A_9}L
=\langle x,s\mid x^9=s^3\rangle.
\tag{190}
\]

It also gives

\[
K_b\cap\langle t\rangle
=\langle t^4\rangle=L,
\qquad
K_b\cap\langle w\rangle
=\langle w^3\rangle=L.
\tag{191}
\]

Thus all thirty-six codes (186) have the exact fold pair

\[
(d_I,d_O)=(4,3);
\tag{192}
\]

there is no scalar-fold subfamily.  The scalar equations are

\[
\sum_{i=0}^{3}
s(K_bt^ib^{-1}g)
=\lambda s(K_bg),
\tag{193}
\]

\[
\sum_{j=0}^{2}
s(K_bw^jb^{-1}yg)
=\lambda s(K_bg),
\qquad\lambda=-\sigma.
\tag{194}
\]

The amalgam in (190) again removes the infinite column incidence.
Its tree resolution is

\[
0\longrightarrow\mathscr I_{A_9}
\longrightarrow\mathscr I_H\oplus\mathscr I_L
\longrightarrow\mathscr I_{K_b}
\longrightarrow0.
\tag{195}
\]

Define

\[
P_I[Hg]=\sum_{i=0}^{3}[Lb^{-1}x^ig],
\qquad
P_O[Hg]=\sum_{j=0}^{2}[Lb^{-1}yx^jg].
\tag{196}
\]

The same exact elimination as in Section 21 gives

\[
\operatorname{coker}D_\lambda
\cong\operatorname{coker}E_\lambda,
\tag{197}
\]

where

\[
E_\lambda:
\mathscr I_H\oplus\mathscr I_{A_9}
\longrightarrow\mathscr I_L,
\]

\[
E_\lambda(\mu,\nu)
=(P_I-P_O)\mu
+(P_I\pi_H-\lambda\pi_L)\nu.
\tag{198}
\]

The distinguished class \([K_b]\) corresponds to \([L]\).

There is a useful second geometric identification:

\[
\Theta:L\backslash B\longrightarrow C\backslash B,
\qquad
\Theta(Ld)=Cbd.
\tag{199}
\]

It is well-defined because \(L=b^{-1}Cb\), and it gives

\[
\Theta P_I[Hg]=I(Hg),
\qquad
\Theta P_O[Hg]=O(Hg).
\tag{200}
\]

Consequently a \(\mu\)-row is exactly the ordinary
incoming-minus-outgoing conservation star.  A \(\nu\)-row indexed by
\(A_9d\) is

\[
I(Hd)-\lambda e_{bd},
\tag{201}
\]

where \(e_{bd}=Cbd\) is the terminal edge of the fixed
nonbacktracking length-three path represented by (186), starting at
\(Hd\).  The target \([L]\) in (197) is the edge \(Cb\), not the base
edge \(C\).

This presentation is row- and column-finite.  An edge occurs in its
two conservation stars, in the nine incoming-star lifts over an
\(H\)-center, and in the three remote-edge lifts over an \(L\)-target.
Those three remote lifts are the remaining phase collision.

The two zero-sum phase modes can nevertheless be removed exactly.
For each \(Ld\), define the equal-phase section

\[
j[Ld]
=\frac13\bigl([A_9d]+[A_9sd]+[A_9s^2d]\bigr).
\tag{202}
\]

Every finite \(\nu\) decomposes uniquely as

\[
\nu=j(\alpha)+\delta,
\qquad
\alpha=\pi_L\nu,
\qquad
\pi_L\delta=0.
\tag{203}
\]

Exactness of the \((9,3)\)-tree resolution gives

\[
\pi_H:\ker\pi_L
\overset{\cong}{\longrightarrow}
\ker\bigl(\rho:\mathscr I_H\to\mathscr I_{K_b}\bigr).
\tag{204}
\]

In particular, the two rational zero-sum vectors on each three-phase
fiber map to the corresponding differences of its three neighboring
\(H\)-vertices; no scalar extension and no phase quotient are hidden.

Pure zero modes have no finite homogeneous cancellation.  Suppose
\(\alpha=0\) and

\[
E_\lambda(\mu,\delta)=0.
\]

Put \(\eta=\pi_H\delta\) and \(f=\mu+\eta\).  The equation is

\[
P_If=P_O\mu.
\tag{205}
\]

Under (199), the coefficient of a directed edge \(e:q\to v\) in
(205) is

\[
f(v)-\mu(q)=0.
\tag{206}
\]

For each pair of adjacent heights, these equations are constancy on
components of an infinite \((3,4)\)-biregular forest.  Finite support
forces \(f=\mu=0\), then \(\eta=0\), and (204) forces
\(\delta=0\).

Thus the three-phase zero modes cannot themselves form a finite
certificate.  For a fixed aggregate \(\alpha\) and target, a finite
zero-mode completion is unique if it exists.  The unresolved part is
now aggregate-only.  With

\[
\tau=\pi_Hj,
\]

a certificate is equivalent to finite
\(\alpha\in\mathscr I_L\) and \(f,\mu\in\mathscr I_H\) satisfying,
for every directed edge \(e:q\to v\),

\[
f(v)-\mu(q)
=\mathbf1_{\{e=Cb\}}
+\lambda\,\Theta(\alpha)(e),
\tag{207}
\]

and the single compatibility equation

\[
\rho(f-\mu)=\varepsilon_L(\alpha).
\tag{208}
\]

Equations (207)--(208) retain the full target and all phases.  They
prove neither a finite certificate nor a separator.  They are the
exact remaining flow problem for the sign-\((-,+,+)\) length-three
stratum.

## 26. Aggregate weights and spherical boundary charges are blind

The aggregate residue cannot be decided by an ordinary weighted leaf
functional.  This failure is exact.

Under \(\Theta\), write

\[
\alpha_e=\Theta(\alpha)(e),
\qquad
T(Cd)=K_bb^{-1}d.
\tag{209}
\]

Then (207)--(208) become

\[
f(\operatorname{ter}e)-\mu(\operatorname{ini}e)
-\mathbf1_{\{e=Cb\}}-\lambda\alpha_e=0,
\tag{210}
\]

\[
\sum_{\rho(v)=c}(f(v)-\mu(v))
-\sum_{T(e)=c}\alpha_e=0
\qquad(c\in K_b\backslash B).
\tag{211}
\]

Suppose one takes a linear combination of (210)--(211), with edge
weights \(\psi(e)\) and \(K_b\)-coset weights \(\chi(c)\).  Cancellation
of every \(\alpha_e\)-coefficient forces

\[
-\lambda\psi(e)-\chi(T(e))=0,
\qquad
\psi(e)=-\lambda\chi(T(e)).
\tag{212}
\]

Thus the edge weight is constant on each complete \(T\)-fiber and
cannot distinguish an ordinary-tree leaf edge from its remote phase
collisions.  Cancellation of the \(f(Hg)\)- and \(\mu(Hg)\)-
coefficients then gives

\[
\sum_{i=0}^{3}\chi(K_bb^{-1}x^ig)
=\lambda\chi(K_bg),
\tag{213}
\]

\[
\sum_{j=0}^{2}\chi(K_bb^{-1}yx^jg)
=\lambda\chi(K_bg).
\tag{214}
\]

These are exactly the unresolved scalar current equations
(193)--(194).  The value of the weighted combination on the target is
\(\lambda\chi(K_b)\).  Therefore a separating weighted functional
exists exactly when the missing current already exists.  No
lexicographic or scalar edge weighting that respects (211) is a
strictly weaker proof target.

The same circularity has a boundary interpretation.  A dual separator
may be written as a rational edge flow

\[
J:C\backslash B\longrightarrow\mathbb Q
\]

with

\[
I_J(Hg)=O_J(Hg)=m(Hg),
\qquad
m(Hkg)=m(Hg)\quad(k\in K_b),
\tag{215}
\]

\[
J(Cbd)=\lambda m(Hd).
\tag{216}
\]

After antisymmetrizing the two orientations of the Bass--Serre tree,
(215) is zero divergence.  Such algebraic flows are finitely additive
rational charges on the tree boundary; no summability is required.
The desired current is therefore a boundary martingale satisfying the
additional \(K_b\)-fiber and remote-cylinder conditions
(215)--(216).

Two natural boundary ansatzes vanish.  First, if \(J\) is radial in
height and has value \(c_n\) on edges terminating at height \(n\),
conservation gives

\[
c_{n+1}=\frac43c_n.
\]

The remote condition, since \(e_y(b)=1\), instead gives

\[
c_{n+1}=4\lambda c_n.
\]

For \(\lambda=\pm1\), these force \(c_n=0\).

Second, one cannot collapse the internal \((9,3)\)-tree to the larger
subgroup

\[
P=\langle H,b^{-1}J_-b\rangle.
\]

If a current factors through \(P\backslash B\), then
\(t,w\in P\) collapse (193)--(194) to

\[
4S(Pb^{-1}g)=\lambda S(Pg),
\qquad
3S(Pb^{-1}yg)=\lambda S(Pg).
\tag{217}
\]

Write \(b=ny\), where \(n=x^\ell u^px^q\) has height zero.
Comparing the two equations gives

\[
S(Pyg)=\frac43S(Pg),
\qquad
S(Pn^{-1}g)=\frac{\lambda}{3}S(Pg).
\]

Because \(H\leq P\) and \(x,y\) generate \(B\), the first recurrence
forces

\[
S(Pg)=c(4/3)^{e_y(g)}.
\]

The second then gives \(c=\lambda c/3\), so \(c=0\).

Hence any successful separator must be genuinely nonradial and must
retain the boundary modes of the internal \((9,3)\)-tree.  This is a
no-go theorem for the displayed compressions, not a decision of the
aggregate compatibility.

## 27. A radius-one-gap theorem for arbitrary positive-start words

The leaf arguments above have an unbounded form which is independent
of the internal word length.

**Radius-one-gap leaf lemma.**  Let \(\mathcal T\) be a directed tree
in which every vertex has at least three incoming and at least three
outgoing branches.  At every vertex \(v\), suppose there are two
finite row vectors:

1. an incoming row, with one target at geodesic distance \(r_I\) in
   every incoming branch of \(v\), plus an arbitrary center
   coefficient at \(v\);
2. an outgoing row, with one target at geodesic distance \(r_O\) in
   every outgoing branch of \(v\), plus an arbitrary center
   coefficient at \(v\).

Assume

\[
|r_I-r_O|=1.
\tag{218}
\]

Then no basis vector lies in the span of a finite set of these rows.

Indeed, suppose a finite combination were one basis vector and take a
non-target leaf \(v\) of the convex hull of the target and all row
centers.  Choose an outward branch of the longer row type.  Its target
is farther from every other supported center than either row radius,
so it isolates and kills the longer-row coefficient at \(v\).

Now choose an outward branch of the shorter row type.  Only the longer
row at the unique inward neighbor can reach its target: every other
center is too far away.  That one row uses at most one branch of the
required orientation.  A leaf has at most one inward branch, so at
least two outward branches of either orientation remain; choose one
which avoids the possible collision.  This kills the shorter-row
coefficient.  Thus no non-target leaf belongs to the defining support.
A nontrivial finite tree has two leaves, and the singleton-hull case
is disposed of by killing the longer and then the shorter coefficient
at the target itself.

Apply the lemma to a normalized Britton word whose first stable letter
is positive:

\[
b=x^\ell yx^{r_1}y^{\epsilon_2}\cdots
x^{r_{n-1}}y^{\epsilon_n},
\qquad n\geq1.
\tag{219}
\]

Assume

\[
K_b=H,
\qquad
(d_I,d_O)=(4,3).
\tag{220}
\]

The inverse word is Britton-reduced.  Thus the four incoming targets
\(Hb^{-1}x^ig\) are geodesic distance \(n\) from \(Hg\), one in each
incoming branch.

If \(\ell\ne0\bmod4\), the appended positive stable letter in
\(b^{-1}yx^jg\) cannot pinch the final \(y^{-1}\).  The three outgoing
targets are geodesic distance \(n+1\), one in each outgoing branch.
All internal turns remain those of the normalized Britton word, so
the radius-one-gap lemma applies.

If \(\ell=0\), the final \(y^{-1}y\) cancels.  When \(n\geq2\) and
\(\epsilon_2=-1\), the new final stable letter is positive.  The
three targets are then geodesic distance \(n-1\), one in each outgoing
branch, and the same lemma applies with the incoming row longer.

Consequently, under (220), the internal flow ideal is proper for every
word (219) satisfying either

\[
\ell\ne0
\quad\text{or}\quad
\bigl(\ell=0,\ n\geq2,\ \epsilon_2=-1\bigr).
\tag{221}
\]

This single theorem contains the noncanonical one-positive-letter
family, the positive--negative length-two family, and the complete
positive--negative--positive length-three family.  It also applies at
arbitrary stable-letter length whenever the exact subgroup and fold
hypotheses (220) hold.  It deliberately excludes endpoint
cancellation with \(\epsilon_2=+1\), which puts the shortened stencil
back in the incoming branch family, and it says nothing when
\(K_b\ne H\) or a stencil folds.

By Section 23, every proper ideal in this radius-one-gap family gives
an A--D Fox nonprimitivity obstruction for the corresponding internal
parameter.  The theorem is an unbounded primitivity sieve, not an
Andrews--Curtis proof.

## 28. Exact classification of the \(K_b=H\) stratum

The hypotheses of Section 27 can be recognized directly from the
stable-letter signs.  Let

\[
b=x^{r_0}y^{\epsilon_1}x^{r_1}\cdots
x^{r_{n-1}}y^{\epsilon_n}
\tag{222}
\]

be any Britton-reduced representative with \(n\geq1\) and no trailing
\(H\)-factor.

Use the standard conjugate-peeling form of Britton's lemma.  To decide
whether \(b^{-1}x^mb\) lies in \(H\), start with the central power
\(x^m\) and process the stable letters of \(b\) from left to right.
Base powers do not change \(m\).  A positive stable letter can pinch
exactly when \(4\mid m\), and then

\[
y^{-1}x^my=x^{3m/4}.
\tag{223}
\]

A negative stable letter can pinch exactly when \(3\mid m\), and then

\[
yx^my^{-1}=x^{4m/3}.
\tag{224}
\]

At the first failed divisibility, the two central stable letters
survive.  The remaining outer syllables of the reduced word (222) are
separated by that reduced core and cannot create a later pinch.
Therefore membership in \(H\) is equivalent to success of every
transition (223)--(224).

Apply this with \(m=4\).  The first sign must be positive and sends
\(4\) to \(3\).  The next sign must be negative and sends \(3\) back
to \(4\), and so on.  Consequently

\[
\boxed{
K_b=H
\quad\Longleftrightarrow\quad
(\epsilon_1,\ldots,\epsilon_n)
=(+,-,+,-,\ldots).
}
\tag{225}
\]

The same peeling calculation determines the folds throughout this
stratum.  For an alternating positive-start word, an arbitrary
\(b^{-1}x^mb\) survives all transitions exactly when \(4\mid m\).
Hence

\[
d_I=4.
\tag{226}
\]

For the outgoing fold, write

\[
b=x^{r_0}yc,
\qquad a=yxy^{-1}.
\]

If \(r_0\ne0\bmod4\), amalgam normal form in
\(\langle x\rangle*_{\langle x^4=a^3\rangle}\langle a\rangle\)
shows

\[
x^{-r_0}a^mx^{r_0}\in\langle a\rangle
\quad\Longleftrightarrow\quad
3\mid m.
\tag{227}
\]

For \(3\mid m\), centrality reduces the conjugate to \(a^m\);
conjugating by \(y^{-1}\) gives \(x^m\), and the remaining sign string
of \(c\) alternates beginning with a negative sign, so every later
pinch succeeds.  Thus \(d_O=3\).

If \(r_0=0\) and \(n\geq2\), the same first cancellation gives
\(x^m\), while \(c\) begins with a negative stable letter.  Its first
pinch succeeds exactly when \(3\mid m\), and all later alternating
pinches then succeed.  Again \(d_O=3\).  The only exception is
\(n=1,r_0=0\), where \(b\in yH\) and every outgoing port folds:

\[
d_O=1.
\tag{228}
\]

Combining (225)--(228) with the radius-one-gap theorem gives a complete
flow classification for \(K_b=H\):

\[
\begin{array}{c|c}
b\in H&\text{flow collapse},\\
b\in yH&\text{flow collapse},\\
K_b=H,\ b\notin H\cup yH&\text{flow ideal proper}.
\end{array}
\tag{229}
\]

The last line contains every Britton length, not a bounded list.  By
Section 23, every word in that line obstructs the corresponding
internal A--D relative product from being primitive.  The two
canonical collapse rows still require a different invariant and are
not claimed primitive.

## 29. A cyclotomic current closes the negative--positive--positive aggregate

The aggregate system left open in Section 25 has a separator.  In
fact the construction does not require normalized endpoint exponents.

**Cyclotomic separator theorem.**  Let

\[
b=x^\ell y^{-1}x^pyx^qy,
\qquad
\ell,q\in\mathbb Z,\quad p\in\{1,2,3\},
\quad\lambda\in\{+1,-1\}.
\tag{230}
\]

Then the right ideal

\[
J_\lambda
=(x^4-1)\mathbb Q[B]
+(yR_3-R_4)\mathbb Q[B]
+(b-\lambda R_4)\mathbb Q[B]
\tag{231}
\]

is proper.  For the subgroup \(K_b\) of Section 25 this gives

\[
[K_b]\notin\operatorname{im}D_\lambda,
\qquad
[L]\notin\operatorname{im}E_\lambda.
\tag{232}
\]

Use row-vector right actions, so \(u\cdot x=uX\) and
\(u\cdot y=uY\).  Let \(\mu_\infty\) be the complex roots of unity
and put

\[
V=\bigoplus_{\zeta\in\mu_\infty}V_\zeta,
\tag{233}
\]

where every \(V_\zeta\) is countably infinite-dimensional over
\(\mathbb C\), and let \(X\) act on \(V_\zeta\) as multiplication by
\(\zeta\).  For \(c\in\mu_\infty\), define

\[
D_c=\bigoplus_{\zeta^4=c}V_\zeta,
\qquad
\mathcal R_c=\bigoplus_{\eta^3=c}V_\eta.
\tag{234}
\]

Both spaces have countably infinite dimension, and both displayed
families decompose \(V\).  Choose isomorphisms
\(Y_c:D_c\to\mathcal R_c\) and put \(Y=\bigoplus_cY_c\).  If
\(d\in D_c\), then

\[
(dY)X^3=c(dY)=(dX^4)Y.
\tag{235}
\]

Hence \(YX^3=X^4Y\), so \(X,Y\) give a right \(B\)-action.  Moreover,
any finite injective prescription inside one block extends to such a
\(Y_c\): extend its independent source and image lists to bases.
Prescriptions in different \(c\)-blocks cannot conflict.

Fix nonzero vectors

\[
v_+,u_+\in V_1,\qquad
v_-,u_-\in V_{-1},\qquad z\in V_\omega,
\tag{236}
\]

where each displayed pair is independent and \(\omega\) is a
primitive cube root of unity.  Put \(v=v_++v_-\) and prescribe

\[
vY=\frac43v_++z.
\tag{237}
\]

This is a \(D_1\)-to-\(\mathcal R_1\) prescription.  It gives

\[
vX^4=v,\qquad
vR_4(X)=4v_+,\qquad
vYR_3(X)=4v_+,
\tag{238}
\]

because \(R_3(1)=3\) and \(R_3(\omega)=0\).

First suppose \(p\) is odd.  Write

\[
\epsilon=(-1)^{\ell+q},
\qquad
a_+=\frac{u_++\epsilon u_-}{4\lambda}\in D_1.
\tag{239}
\]

Choose \(\delta^4=-1\), nonzero
\(h_1\in V_\delta\), \(h_2\in V_{-\delta}\), and put
\(a_-=h_1+h_2\in D_{-1}\).  In addition to (237), prescribe

\[
\begin{aligned}
a_+Y&=v_+,&(a_+X^p)Y&=u_+,\\
a_-Y&=v_-,&(a_-X^p)Y&=u_-.
\end{aligned}
\tag{240}
\]

These are injective partial maps in the indicated blocks.  Indeed,

\[
a_+X^p=\frac{u_+-\epsilon u_-}{4\lambda},
\qquad
a_-X^p=\delta^p(h_1-h_2).
\tag{241}
\]

The first two sources, together with \(v\), are independent because
\((v_+,u_+)\) and \((v_-,u_-)\) are independent; their images are
independent because \(z\) lies in the separate \(V_\omega\)-summand.
The second source pair has determinant \(-2\delta^p\ne0\), and its
image pair is independent.  Thus (240) extends blockwise to \(Y\).
Now

\[
\begin{aligned}
vb
&=vX^\ell Y^{-1}X^pYX^qY\\
&=(u_++(-1)^\ell u_-)X^qY\\
&=(u_++\epsilon u_-)Y\\
&=4\lambda a_+Y
=4\lambda v_+
=\lambda vR_4(X).
\end{aligned}
\tag{242}
\]

It remains to treat \(p=2\).  Keep \(\epsilon,\delta\) and choose a
nonzero \(h\in V_\delta\).  Put

\[
a_+=\frac{v_++\epsilon\delta^2v_-}{4\lambda}\in D_1
\tag{243}
\]

and prescribe

\[
a_+Y=v_+,\qquad
vY=\frac43v_++z,\qquad
hY=v_-.
\tag{244}
\]

The two \(D_1\)-sources \(a_+,v\) are independent because
\(\epsilon\delta^2=\pm i\ne1\), and their images are independent
because \(z\ne0\).  The \(D_{-1}\)-prescription is nonzero.  Since
\(a_+X^2=a_+\) and \(hX^2=\delta^2h\),

\[
\begin{aligned}
vb
&=(a_++(-1)^\ell h)X^2YX^qY\\
&=(v_++(-1)^\ell\delta^2v_-)X^qY\\
&=(v_++\epsilon\delta^2v_-)Y\\
&=4\lambda a_+Y
=4\lambda v_+
=\lambda vR_4(X).
\end{aligned}
\tag{245}
\]

Equations (238), (242), and (245) show that \(v\ne0\) annihilates
all three generators of (231).  Restricting scalars makes \(V\) a
right \(\mathbb Q[B]\)-module.  If \(1\in J_\lambda\), applying that
identity to \(v\) would give \(v=0\).  This proves propriety.

There is also a direct normalized scalar current.  Put

\[
m=vR_4=4v_+,\qquad
s_0=b^{-1}x^4b,\qquad
K_b=\langle x,s_0\rangle.
\]

Then \(mX=m\), and \(vb=\lambda m\) gives

\[
ms_0
=\lambda^{-1}vbb^{-1}X^4b
=\lambda^{-1}vX^4b
=m.
\tag{246}
\]

Thus \(m\) is fixed by \(K_b\).  Choose a
\(\mathbb Q\)-linear functional \(\psi:V\to\mathbb Q\) with
\(\psi(m)=1\), and define

\[
S(K_bg)=\psi(mg).
\tag{247}
\]

This is well-defined and \(S(K_b)=1\).  Since
\(mb^{-1}=\lambda v\), equation (238) yields

\[
mb^{-1}R_4=\lambda m,
\qquad
mb^{-1}yR_3=\lambda m.
\tag{248}
\]

Using

\[
t^ib^{-1}=b^{-1}x^i,
\qquad
w^jb^{-1}y=b^{-1}yx^j,
\]

equation (248) is exactly (193)--(194).  Hence pairing with \(S\)
annihilates \(\operatorname{im}D_\lambda\) but sends \([K_b]\) to
\(1\), proving the first assertion in (232); (197) gives the second.

In particular, all thirty-six normalized codes (186), for both
signs, have proper internal flow ideals.  Section 23 turns this into
evaluated A--D Fox-row non-unimodularity and nonprimitivity.  This
closes the length-three aggregate problem, not the Andrews--Curtis
conjecture.

## 30. Finite-characteristic currents survive the canonical rational collapse

Section 6 proves that the canonical flow quotient vanishes over
\(\mathbb Q\).  The same calculation exposes torsion rather than
integral collapse.  Over the characteristics dividing its scalar
coefficient, a nonzero current exists.

For a field \(k\), write

\[
J^{(k)}_{b,\sigma}
=(x^4-1)k[B]
+(yR_3-R_4)k[B]
+(b+\sigma R_4)k[B].
\tag{249}
\]

**Finite-characteristic canonical-current theorem.**

1. If \(b\in yH\) and
   \(\operatorname{char}k\mid(1+3\sigma)\), then
   \(J^{(k)}_{b,\sigma}\ne k[B]\).
2. If \(b\in H\) and
   \(\operatorname{char}k\mid(1+4\sigma)\), then
   \(J^{(k)}_{b,\sigma}\ne k[B]\).

Here divisibility refers to the integer represented in the prime
field.  In particular, characteristic two works for \(b\in yH\) and
both signs; characteristic five works for \(b\in H,\sigma=+1\), and
characteristic three works for \(b\in H,\sigma=-1\).

There are two canonical \(0\)-\(1\) currents on the directed tree.
Choose an end \(\xi_-\) represented by a ray which always moves from
a vertex to an incoming predecessor, and put

\[
m_-(v)=
\begin{cases}
1,&\text{if the ray from \(v\) to \(\xi_-\) always uses incoming
predecessors},\\
0,&\text{otherwise}.
\end{cases}
\]

If \(m_-(v)=1\), exactly one predecessor \(u\to v\) continues that
ray and has \(m_-(u)=1\); every other predecessor first moves toward
\(v\) on its ray to \(\xi_-\).  Conversely, a predecessor with value
one forces the ray from \(v\) to begin with that predecessor.  Hence,
over every field,

\[
m_-(v)=\sum_{u\to v}m_-(u).
\tag{250}
\]

Dually, choose a positive directed end \(\xi_+\).  Its indicator
\(m_+\) satisfies

\[
m_+(u)=\sum_{u\to v}m_+(v).
\tag{251}
\]

First let \(b\in yH\).  On the directed Bass--Serre tree, write an
edge as \(e:u\to v\).  Put \(m=m_-\) and define

\[
F(e)=-\sigma m(u).
\tag{252}
\]

This is exactly the third canonical relation: every outgoing edge at
\(u\) has value \(-\sigma I_F(u)\), provided
\(I_F(u)=m(u)\).  Its outgoing sum is

\[
O_F(u)=-3\sigma m(u)=m(u)
\tag{253}
\]

in the stated characteristic.  The remaining condition
\(I_F(v)=m(v)\) is
exactly (250), because \(-\sigma=1\) in characteristic two.  Thus
(252) is a nonzero current satisfying conservation and every relation
in (249).

Now let \(b\in H\).  Fix a Busemann function \(\beta\) for
\(\xi_+\), normalized so that \(\beta(v)=\beta(u)+1\) when the
positive ray uses \(u\to v\), and put

\[
m(v)=(-\sigma)^{\beta(v)}m_+(v).
\]

Define

\[
F(e)=-\sigma m(v).
\tag{254}
\]

This is the incoming canonical relation.  Its incoming sum is

\[
I_F(v)=-4\sigma m(v)=m(v)
\tag{255}
\]

in the stated characteristic.  Conservation is therefore equivalent
to

\[
m(u)=-\sigma\sum_{u\to v}m(v).
\]

If \(m_+(u)=1\), exactly one outgoing neighbor \(v\) has value
\((-\sigma)m(u)\), so the right side is
\((-\sigma)^2m(u)=m(u)\).  If \(m_+(u)=0\), no outgoing neighbor has
nonzero value.  Thus (254) is again a nonzero global current.  For
the relevant negative sign over \(\mathbb F_3\), the Busemann weight
is identically one; the alternating weight is needed only for the
optional positive-sign case over \(\mathbb F_5\).

In either case, pairing finite-support edge vectors with \(F\)
annihilates the presentation relations but not the entire edge
module.  Hence the quotient and the right ideal (249) are proper.
No analytic convergence or finite-support assumption is imposed on
the dual current.

The Fox bridge of Section 23 is characteristic-free.  Indeed, for
any field \(k\), put

\[
W=k[B]/J^{(k)}_{b,\sigma}
\]

and induce it to \(G=B*\langle z\rangle\).  The group ring \(k[G]\)
is free as a left \(k[B]\)-module, so the nonzero cyclic vector
remains nonzero after induction.  Equations (169)--(173) and the
four-coordinate annihilation of (174) use only integral group-ring
identities and remain valid over \(k\).  Therefore the evaluated Fox
row is not right-unimodular over \(k[G]\).

If \(P_\sigma(c)\) were primitive in the free group, its integral Fox
row would have a right Bezout identity.  Evaluation followed by
reduction to \(k[G]\) would preserve that identity, contradicting the
nonzero annihilator.  Since the evaluated row depends on \(c\) only
through

\[
\rho(c)=zbz^{-1},
\tag{256}
\]

the conclusion covers every free-kernel lift of each canonical
internal parameter:

\[
\boxed{
\begin{array}{c|c|c}
\sigma&b&\text{obstructing field}\\ \hline
+1&yH&\mathbb F_2\\
-1&yH&\mathbb F_2\\
-1&H&\mathbb F_3.
\end{array}
}
\tag{257}
\]

The unused case \(\sigma=+1,b\in H\) is likewise obstructed over
\(\mathbb F_5\).  Thus the canonical double-coset residue of each of
Result 56's three internal projection classes is nonprimitive for
every conjugator \(c\), even though its rational flow quotient is
zero.  Noncanonical internal double cosets outside the families
already decided above remain a separate problem.
