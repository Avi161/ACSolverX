# Fox coset sieve for the repositioned minimum tail

Date: 2026-07-25

Status: **PROVEN**. For the repositioned row-\((+,-,-)\) candidate, the
two bridge coefficients in the Fox equation generate the augmentation
right ideal of an explicit subgroup

\[
P\cong F_2
\]

of infinite index in \(G=\langle x,t\mid x^3=t^4\rangle\). The full Fox
problem therefore reduces exactly to one affine cyclic-submodule equation
in the infinite coset module \(\mathbb Z[P\backslash G]\).

An exact \(S_4\) quotient gives a genuine Fox restriction: the target
Schreier letter must map into the point stabilizer which is the image of
\(P\). This does not prove nonliftability, because six target residues,
including the identity, survive. The full infinite coset equation and
the nonabelian free-kernel equation remain open. AK(3) remains open.

## 1. Candidate and Fox equation

Use the repositioned candidate from
`AK3_MINIMUM_TAIL_REPOSITIONING_COUNTERMODEL.md`. Thus

\[
\begin{aligned}
C_0&=c^{-2}x^2t^3x^2,
&
s_0&=xtx^{-1},\\
C&=s_0C_0^{-1}s_0^{-1},
&
\rho&=s_0(xt^{-1})s_0^{-1},\\
\gamma&=xt^{-1}x^{-1},
&
\beta&=x,\\
b&=C\rho C\rho^{-1},
&
e&=xt\,b^{-1},\\
d&=t^{-1}exe^{-1},
&
K&=\gamma C\gamma^{-1},\qquad \alpha=t.
\end{aligned}
\tag{1.1}
\]

The exact evaluated equations are

\[
K=d\alpha b\alpha^{-1},
\qquad
C=b\beta K^{-1}\beta^{-1},
\qquad
1=K\gamma C^{-1}\gamma^{-1}.
\tag{1.2}
\]

Put

\[
R=\mathbb Z[G].
\tag{1.3}
\]

The abelianized free-kernel equation from Result 26 is

\[
\begin{aligned}
\mathbf X&=
\boldsymbol\Delta+d(1-r)\mathbf u+d\alpha\mathbf j,\\
\mathbf Y&=
\mathbf j+b(1-s)\mathbf v-b\beta K^{-1}\mathbf X,\\
\boldsymbol\Xi&=
\mathbf X+(K-1)\mathbf w-\gamma\mathbf Y,
\end{aligned}
\tag{1.4}
\]

where

\[
\begin{aligned}
\mathbf j&=-e^{-1},
&
\boldsymbol\Delta&=t^{-1}(1-exe^{-1}),\\
r&=\alpha b\alpha^{-1},
&
s&=\beta K^{-1}\beta^{-1}.
\end{aligned}
\tag{1.5}
\]

The Fox image of any legal lift must satisfy

\[
\boldsymbol\Xi=-g
\tag{1.6}
\]

for some \(g\in G\). This condition is necessary at the Fox level, not
sufficient for the nonabelian free-kernel equation.

## 2. Exact coefficient reduction

Let

\[
F_0=\boldsymbol\Delta+d\alpha\mathbf j
\tag{2.1}
\]

and

\[
L=\gamma b\beta K^{-1}.
\tag{2.2}
\]

Substituting the first two lines of (1.4) into the third gives

\[
\boxed{
\boldsymbol\Xi
=
A_0+A_U\mathbf u+A_V\mathbf v+A_W\mathbf w,
}
\tag{2.3}
\]

with

\[
\begin{aligned}
A_0&=(1+L)F_0-\gamma\mathbf j,\\
A_U&=(1+L)(d-K),\\
A_V&=-\gamma b(1-s),\\
A_W&=K-1.
\end{aligned}
\tag{2.4}
\]

The equality \(d(1-r)=d-K\) uses \(K=dr\).

Now put

\[
H_0=\gamma b\gamma^{-1}
\tag{2.5}
\]

and

\[
P=\langle K,H_0\rangle\le G.
\tag{2.6}
\]

Since \(C=bs\) and \(K=\gamma C\gamma^{-1}\),

\[
\begin{aligned}
A_V
&=\gamma b(s-1)\\
&=(KH_0^{-1}-1)\gamma b.
\end{aligned}
\tag{2.7}
\]

Right multiplication by the unit \(\gamma b\) does not change the
principal right ideal. Hence

\[
A_VR+A_WR
=
(KH_0^{-1}-1)R+(K-1)R.
\tag{2.8}
\]

The elements \(K\) and \(KH_0^{-1}\) generate \(P\), because

\[
(KH_0^{-1})^{-1}K=H_0.
\tag{2.9}
\]

The identities

\[
ab-1=(a-1)b+(b-1),
\qquad
a^{-1}-1=-(a-1)a^{-1}
\tag{2.10}
\]

therefore prove

\[
\boxed{
A_VR+A_WR
=
I_P
:=
\sum_{p\in P}(p-1)R.
}
\tag{2.11}
\]

Although \(R\) acts on the abelianized kernel on the left, the variables
\(\mathbf u,\mathbf v,\mathbf w\) range over all elements of \(R\), so
each fixed left coefficient produces the right ideal displayed above.

## 3. The subgroup \(P\) is free and infinite-index

Let

\[
\pi:G\longrightarrow
\Gamma=C_3*C_4
\tag{3.1}
\]

be the central quotient. Simultaneous conjugation by \(\gamma^{-1}\)
turns \(P\) into

\[
\langle C,b\rangle
=
\langle C,\rho C\rho^{-1}\rangle,
\tag{3.2}
\]

because

\[
C^{-1}b=\rho C\rho^{-1}.
\tag{3.3}
\]

Put

\[
A=\pi(C),
\qquad
B=\pi(\rho C\rho^{-1}).
\tag{3.4}
\]

Both \(A\) and \(B\) are hyperbolic of cyclic translation length \(2\)
in the Bass--Serre tree of \(C_3*C_4\). Their product is

\[
AB=\pi(b),
\tag{3.5}
\]

whose cyclic length is \(6\).

The axes of \(A\) and \(B\) are disjoint. If they shared a point \(v\),
then

\[
\begin{aligned}
d(v,ABv)
&\le
d(v,Av)+d(Av,ABv)\\
&=
\ell(A)+\ell(B)
=4,
\end{aligned}
\tag{3.6}
\]

contradicting \(\ell(AB)=6\). The disjoint-axis product formula now gives
distance \(1\) between the two axes.

The standard tree ping-pong argument for hyperbolic isometries with
disjoint axes gives

\[
\langle A,B\rangle
=
\langle A\rangle*\langle B\rangle
\cong F_2.
\tag{3.7}
\]

Indeed, the bridge between the two axes determines disjoint half-tree
domains, and every nonzero power of either translation sends the
complement of its domain into that domain. Thus every nonempty reduced
alternating word acts nontrivially.

The generators \(\pi(K),\pi(H_0)\) are the Nielsen basis
\((A,AB)\) after conjugation. Therefore they freely generate \(\pi(P)\),
and

\[
\pi|_P:P\longrightarrow\pi(P)
\tag{3.8}
\]

is an isomorphism. In particular,

\[
\boxed{
P\cong F_2,
\qquad
P\cap\langle c\rangle=1.
}
\tag{3.9}
\]

The subgroup has infinite index. If \(\pi(P)\) had finite index \(n\) in
\(\Gamma\), multiplicativity of Euler characteristic would give

\[
-1
=
\chi(F_2)
=
n\chi(C_3*C_4)
=
-\frac{5n}{12},
\tag{3.10}
\]

so \(n=12/5\), impossible. Hence \(\pi(P)\) has infinite index in
\(\Gamma\), and consequently

\[
\boxed{[G:P]=\infty.}
\tag{3.11}
\]

## 4. Exact Fox reduction to an infinite coset module

The quotient of the regular right module by (2.11) is

\[
\boxed{
R/I_P\cong\mathbb Z[P\backslash G],
}
\tag{4.1}
\]

where \(g\) maps to the left coset \([Pg]\), with right action

\[
[Pg]h=[Pgh].
\tag{4.2}
\]

Let

\[
\pi_P:R\longrightarrow\mathbb Z[P\backslash G]
\tag{4.3}
\]

be this quotient. Equations (1.6), (2.3), and (2.11) give an exact
necessary-and-sufficient criterion for Fox-level solvability:

\[
\boxed{
\exists\,\mathbf u\in R,\ g\in G:
\quad
\pi_P(A_0)+\pi_P(A_U)\mathbf u=-[Pg].
}
\tag{4.4}
\]

Equivalently,

\[
-[Pg]-\pi_P(A_0)
\in
\pi_P(A_U)R.
\tag{4.5}
\]

Thus the three-variable Fox equation has become one cyclic-submodule
membership problem in an infinite permutation module. The infinite index
in (3.11) is load-bearing: this module does not collapse to scalar
augmentation.

## 5. An exact \(S_4\) Fox restriction

There is a quotient

\[
\psi:\Gamma\longrightarrow S_4
\tag{5.1}
\]

defined on \(\{0,1,2,3\}\) by

\[
X\longmapsto(1\,2\,3),
\qquad
T\longmapsto(0\,1\,2\,3).
\tag{5.2}
\]

These permutations generate \(S_4\). Exact evaluation gives

\[
\psi(\pi(K))=(0\,2),
\qquad
\psi(\pi(H_0))=(0\,2\,1).
\tag{5.3}
\]

Therefore

\[
\psi(\pi(P))
=
P_0
:=
\operatorname{Stab}_{S_4}(3)
\cong S_3.
\tag{5.4}
\]

This is also a concrete properness certificate for \(P\).

Index the four left cosets \(P_0\backslash S_4\) by

\[
[P_0g]\longmapsto g^{-1}(3)\in\{0,1,2,3\}.
\tag{5.5}
\]

Let \(\mathbf e_i\) be the associated basis. Projecting the exact
coefficients (2.4) to this four-dimensional module gives

\[
\boxed{
\overline{A_0}
=
(0,-2,0,1),
\qquad
\overline{A_U}
=
(2,0,0,-2).
}
\tag{5.6}
\]

The right \(S_4\)-orbit of \(\overline{A_U}\) consists of

\[
2(\mathbf e_i-\mathbf e_j),
\qquad
i\ne j,
\tag{5.7}
\]

and therefore spans exactly twice the augmentation lattice.

For target coset \(i\), equation (4.4) requires

\[
-\mathbf e_i-\overline{A_0}
\in
2\ker(\operatorname{aug}:\mathbb Z^4\to\mathbb Z).
\tag{5.8}
\]

This holds exactly for \(i=3\):

\[
-\mathbf e_3-\overline{A_0}
=(0,2,0,-2).
\tag{5.9}
\]

For \(i=0,1,2\), at least one coordinate has odd parity. Consequently

\[
\boxed{
\text{the \(S_4\) Fox equation is solvable only if }
\psi(\pi(g))\in P_0.
}
\tag{5.10}
\]

This is a real restriction on the target Schreier letter. It is not a
nonlift certificate: \(g=1\) and all six residues in \(P_0\) survive.

## 6. Scope and next exact question

The theorem proves:

1. the \(V,W\) Fox variables generate exactly the augmentation ideal of
   \(P\);
2. \(P\) is a center-free, free rank-two subgroup of infinite index;
3. the full Fox equation is exactly the cyclic coset-module problem
   (4.4); and
4. an exact \(S_4\) projection restricts the target to the image of \(P\)
   but does not exclude all targets.

It does not solve the full infinite coset equation, the nonabelian
free-kernel equation, or AK(3). The axis lengths, \(S_4\) subgroup, exact
coefficient vectors, and target-parity restriction are replayed by
`tests/stable_ac/test_prefix_db_evaluated_countermodel.py`.

The tree product formula used in Section 3 is the standard axis formula
for hyperbolic isometries; see Proposition 4.1 of I. Kapovich,
G. Levitt, P. Schupp, and V. Shpilrain,
*Translation equivalence in free groups*, arXiv:math/0409284.

AK(3) remains open.
