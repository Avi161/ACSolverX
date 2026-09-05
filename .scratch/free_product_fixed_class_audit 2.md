# Free-product audit of the fixed-class residue

## Verdict

No obstruction was found in cyclic free products or in the tested nearby
virtually free groups.

More strongly, every relator-killing map discovered with nontrivial
\(c=yx^{-1}\) realizes the fixed-entry commutator equation exactly.  Most
discovered maps lie in a uniform blind branch:

\[
u=(yx)y(yx)^{-1}=x.
\]

In that branch \(a=x^{-1}\), and one explicit commutator works in every
target group, not just within the search bound.

A hypothetical noncollapsed free-product image is forced into a sharply
defined \(C_2*C_3\) braid subgroup and an external-connector equation.  I
exclude the case in which the connector lies inside the braid subgroup, but
I do not have a proof excluding every external connector.  Thus this is an
exact negative diagnostic and reduction, not a theorem that all virtually
free quotients are blind.

## 1. The quotient criterion

For a homomorphism

\[
\pi:G_b\longrightarrow Q,
\]

write

\[
X=\pi(x),\quad Y=\pi(y),\quad
A=\pi(a),\quad C=\pi(c).
\]

The quotient obstructs the Result 134 residue exactly when, for both signs,

\[
\operatorname{Cl}_Q(A)\cap
A\operatorname{Cl}_Q(C^\eta)=\varnothing.
\tag{1}
\]

Equivalently there must be no \(h,k\in Q\) satisfying

\[
A^{-1}hAh^{-1}=kC^\eta k^{-1}.
\tag{2}
\]

All computations below used exact reduced syllable normal forms and exact
cyclic conjugacy in the free product.

## 2. A uniform blind branch

Set

\[
G=YX,\qquad U=GYG^{-1}.
\]

The relator \(b\) says precisely that

\[
XUX=UXU.
\tag{3}
\]

Suppose \(U=X\).  Then

\[
A=X^3U^{-4}=X^{-1}.
\]

Moreover \(U=GYG^{-1}=X\), so

\[
Y=G^{-1}XG
\quad\text{and}\quad
C=YX^{-1}=G^{-1}XGX^{-1}.
\]

With \(h=G^{-1}\) and the convention
\([v,w]=v^{-1}wvw^{-1}\),

\[
\begin{aligned}
[A,G^{-1}]
&=XG^{-1}X^{-1}G\\
&=C^{-1}.
\end{aligned}
\tag{4}
\]

Thus every quotient with \(U=X\) is rigorously blind to (1), with no bound
on the possible conjugators.

## 3. Braid-pair dichotomy in \(C_m*C_n\)

Let \(Q=C_m*C_n\), and let

\[
\Delta=XUX.
\]

The braid relation gives

\[
\Delta X\Delta^{-1}=U,\qquad
\Delta U\Delta^{-1}=X.
\]

Hence \(\Delta^2\) centralizes both \(X\) and \(U\).

Centralizers of nontrivial elements in a free product of cyclic groups are
cyclic: an elliptic element has the conjugate cyclic factor as its
centralizer, and a hyperbolic element has an infinite cyclic centralizer.
Therefore, if \(\Delta^2\ne1\), then \(X,U\) lie in one cyclic centralizer.
They commute, and (3) immediately reduces to \(X=U\).

Consequently every noncollapsed braid pair must satisfy

\[
\Delta^2=1.
\tag{5}
\]

Put

\[
s=\Delta,\qquad v=XU.
\]

Since

\[
(XU)^3=(XUX)(UXU)=\Delta^2,
\]

a noncyclic pair has

\[
s^2=1,\qquad v^3=1.
\]

The two torsion elements cannot lie in the same conjugate factor, since that
would make the pair cyclic.  Free-product normal form therefore gives

\[
K=\langle X,U\rangle
=\langle s\rangle*\langle v\rangle
\cong C_2*C_3.
\tag{6}
\]

The original elements are

\[
X=v^2s,\qquad U=sv^2.
\tag{7}
\]

Finally, from \(G=YX\) and \(U=GYG^{-1}\),

\[
G^2=UGX.
\]

Using (7), every hypothetical noncollapsed image must solve

\[
\boxed{
G^2=sv^2Gv^2s
}
\tag{8}
\]

in the ambient free product.

This is the exact remaining Bass--Serre connector problem.  It is much
smaller than an arbitrary search over \(X,Y\).

## 4. The connector cannot lie in the braid subgroup

Equation (8) has no solution \(G\in K=C_2*C_3\).

Use the faithful realization \(C_2*C_3=\mathrm{PSL}(2,\mathbb Z)\) with
lifts

\[
S=
\begin{pmatrix}0&-1\\1&0\end{pmatrix},
\qquad
V=
\begin{pmatrix}0&-1\\1&-1\end{pmatrix}.
\]

Here \(S^2=-I\) and \(V^3=I\), so their projective images have orders two
and three.  If

\[
M=\begin{pmatrix}\alpha&\beta\\\gamma&\delta\end{pmatrix}
\in\mathrm{SL}(2,\mathbb Z)
\]

represented a solution of (8), then for some
\(\epsilon\in\{\pm1\}\),

\[
M^2=\epsilon\,SV^2MV^2S.
\tag{9}
\]

The right side before multiplying by \(\epsilon\) is

\[
\begin{pmatrix}
\alpha&\alpha+\beta\\
-\alpha+\gamma&-\alpha-\beta+\gamma+\delta
\end{pmatrix}.
\]

Let \(T=\alpha+\delta\).  Cayley--Hamilton gives
\(M^2=TM-I\).  Comparing the upper-left entry in (9) yields

\[
\alpha(T-\epsilon)=1.
\]

Thus \(\alpha=\pm1\) and \(T-\epsilon=\alpha\).  The upper-right entry then
gives \(\beta=\epsilon\), hence \(\delta=\epsilon\).  The determinant
condition gives \(\gamma=\alpha-\epsilon\).  But the lower-left entry of
(9) becomes

\[
T\gamma=0
\qquad\text{and}\qquad
\epsilon(-\alpha+\gamma)=-1,
\]

a contradiction.

Therefore any noncollapsed free-product image would require

\[
G\notin K.
\tag{10}
\]

Geometrically, the unresolved case is a genuinely external connector
between the \(C_2*C_3\) braid subtree and one of its translates.  No bounded
search below produced such a solution of the defining relator.

## 5. Exact cyclic-free-product census

For every \(2\le m\le n\le6\), all reduced candidates \(X,Y\in C_m*C_n\)
of syllable length at most four were enumerated.  The only parameter pairs
with relator-killing maps and \(C\ne1\) were:

| \((m,n)\) | Maps with \(C\ne1\) |
|---|---:|
| \((2,3)\) | 12 |
| \((3,4)\) | 16 |
| \((2,6)\) | 32 |
| \((3,6)\) | 36 |
| \((4,6)\) | 52 |
| \((5,6)\) | 32 |
| \((6,6)\) | 144 |
| all other pairs through \(6\) | 0 |

Every listed map has an exact realization of (2), with positive sign and a
one-syllable \(h\).  Hence none is even a candidate obstruction.

For example, in

\[
C_2*C_3=\langle p,q\mid p^2=q^3=1\rangle,
\]

take

\[
X=pq,\qquad Y=qp.
\]

Exact normal-form reduction gives

\[
A=q^2p=X^{-1},\qquad
C=qpq^2p,\qquad
[A,p]=pCp^{-1}.
\tag{11}
\]

The longer \(C_2*C_3\) census used every \(X,Y\) of syllable length at most
ten.  Among 422 relator-killing pairs, 204 had \(C\ne1\).  Every one of
those 204 satisfies \(U=X\), so (4), rather than the finite search, proves
its blindness.

Additional deeper exact scans gave:

| Target | image-length bound | relator pairs | pairs with \(C\ne1\) | pairs with \(U\ne X\) |
|---|---:|---:|---:|---:|
| \(C_2*C_3\) | 8 | 190 | 84 | 0 |
| \(C_3*C_4\) | 5 | 348 | 48 | 0 |
| \(C_2*C_4\) | 7 | 239 | 0 | 0 |
| \(C_3*C_3\) | 6 | 253 | 0 | 0 |
| \(C_2*C_5\) | 6 | 274 | 0 | 0 |

These figures overlap the first census but independently check the
structural collapse \(U=X\), rather than only checking for a short \(h\).

## 6. Nearby virtually free diagnostics

The same exact normal-form scan was run in free products with noncyclic
finite factors.  Images \(X,Y\) had syllable length at most three.

| Target | candidates per image | relator pairs | pairs with \(C\ne1\) | pairs with \(U\ne X\) |
|---|---:|---:|---:|---:|
| \(S_3*C_2\) | 47 | 83 | 36 | 0 |
| \(S_3*C_3\) | 98 | 176 | 78 | 0 |
| \(S_3*C_4\) | 159 | 211 | 52 | 0 |
| \(A_4*C_2\) | 167 | 407 | 240 | 0 |
| \(S_3*S_3\) | 311 | 575 | 264 | 0 |

Thus every nontrivial candidate in these bounds is also rigorously blind by
the universal identity (4).  This is a bounded census of maps followed by
an unbounded proof for each discovered map; it is not a classification of
all homomorphisms to those targets.

## 7. Side check: \(a\) is not conjugate to \(x^{-1}\)

If \(a\) were conjugate to \(x^{-1}\), the explicit identity
\(c=[r,x]\) would solve the projected residue, because

\[
[x^{-1},r]=rcr^{-1}.
\]

Equivalently, after absorbing the stable-letter height, the kernel equation
would be

\[
q=w\Phi^{-1}(w^{-1}).
\tag{12}
\]

This route is closed by an exact \(S_5\) quotient.  Compose permutations
right-to-left and set

\[
X=(0\,1\,2\,3\,4),\qquad
Y=(0\,1\,3\,4\,2).
\]

The assignment \(x\mapsto X,y\mapsto Y\) kills \(b\).  But

\[
\pi(a)=(1\,2\,4)
\]

is a 3-cycle, whereas

\[
\pi(x^{-1})=(0\,4\,3\,2\,1)
\]

is a 5-cycle.  Hence

\[
a\not\sim_{G_b}x^{-1},
\]

and equation (12) has no solution.

## Status

- Free-product obstruction found: **no**.
- Every enumerated nontrivial cyclic-free-product map: **exactly blind**.
- Uniform theorem for the \(U=X\) branch: **proved**.
- Noncollapsed braid-pair reduction to (8): **proved**.
- Connector \(G\in\langle X,U\rangle\): **excluded exactly**.
- Arbitrary external connector in every \(C_m*C_n\): **open**.
- Proposed solution through \(a\sim x^{-1}\): **disproved by \(S_5\)**.

The standard free-product conjugacy and centralizer facts used in Section 3
can also be checked directly from unique reduced normal forms; a modern
reference is Dan Burghelea, *Note on the conjugacy classes of elements and
their centralizers for the free product of two groups* (2023),
https://arxiv.org/abs/2301.10683.
