# Binary coset sieve for the repositioned minimum tail

Date: 2026-07-25

Status: **PROVEN**. The infinite-index subgroup

\[
P=\langle K,\gamma b\gamma^{-1}\rangle
\le
G=\langle x,t\mid x^3=t^4\rangle
\]

has an explicit nine-edge folded core in the central quotient
\(C_3*C_4\). The core, together with the central weight, gives an exact
membership test for \(P<G\).

A binary lift of the previous \(S_4\) quotient gives a stronger Fox
functional over \(\mathbb F_3\). It removes both the identity target and
the apparently natural target \(g=\gamma e^{-1}\). Every surviving
target must map into the single coset

\[
(-I)\rho(P)\subset GL_2(\mathbb F_3).
\]

The central target \(g=c^{-1}\), where \(c=x^3=t^4\), survives. Thus this
is a strict target sieve, not a proof of nonliftability. The integral
coset-module equation and the nonabelian free-kernel equation remain
open. AK(3) remains open.

## 1. The exact Fox problem

Retain the notation and candidate of
`AK3_MINIMUM_TAIL_FOX_COSET_SIEVE.md`. Put

\[
\begin{aligned}
q&=\gamma e^{-1},\\
L&=\gamma b\beta K^{-1},\\
H_0&=\gamma b\gamma^{-1},\\
P&=\langle K,H_0\rangle.
\end{aligned}
\tag{1.1}
\]

Over \(R=\mathbb Z[G]\), the Fox equation has already been reduced to

\[
\boxed{
\pi_P(A_0)+\pi_P(A_U)u=-[Pg]
}
\tag{1.2}
\]

for some \(u\in R\) and \(g\in G\), where

\[
\begin{aligned}
A_0&=(1+L)F_0+q,\\
A_U&=(1+L)(d-K),\\
F_0&=t^{-1}-d-d\alpha e^{-1}.
\end{aligned}
\tag{1.3}
\]

Here

\[
\pi_P:R\longrightarrow\mathbb Z[P\backslash G]
\tag{1.4}
\]

sends \(g\) to the left coset \([Pg]\).

For the target \(g=q\), (1.2) is exactly

\[
\boxed{
(1+L)\bigl(F_0+(d-K)u\bigr)=-2q
\quad\text{in }\mathbb Z[P\backslash G].
}
\tag{1.5}
\]

Exact normal forms also give

\[
\boxed{
q=c^{-1}L.
}
\tag{1.6}
\]

Equation (1.6) does not make \(1+L\) a right-module operator on
\(\mathbb Z[P\backslash G]\). Left multiplication by \(L\) is
well-defined on \(P\backslash G\) only if \(L\) normalizes \(P\), and in
fact the folded core below proves \(L\notin P\).

## 2. A folded core for the projected subgroup

Let

\[
\pi:G\longrightarrow\Gamma=C_3*C_4
\tag{2.1}
\]

be the central quotient. Use edge states

\[
\mathcal E=\{0,1,2,4,5,8,9,11,12\}.
\tag{2.2}
\]

Folding the two based loops \(\pi(K)\) and \(\pi(H_0)\) gives the
following partial factor actions:

\[
\begin{array}{c|c}
\text{\(x\)-orbits} & (0\,1\,2),\ (5\,8\,9),\ (4),\ (11),\ (12)\\
\hline
\text{\(t\)-orbits} & (1\,2\,4\,5),\ (8\,9\,11\,12),\ (0).
\end{array}
\tag{2.3}
\]

Parentheses of length one in (2.3) are boundary incidences, not
one-cycles for the corresponding factor action. A reduced syllable
which asks for that missing transition leaves the core and is rejected.

The two generator paths are

\[
\begin{aligned}
\pi(K)&=xtx:
&
0&\xrightarrow{x}1\xrightarrow{t}2\xrightarrow{x}0,\\
\pi(H_0)&=xtx^2t^3xtxtx^2:
&
0&\to1\to2\to1\to5\to8\to9\to5\to1\to0.
\end{aligned}
\tag{2.4}
\]

The associated bipartite core has nine edges and eight factor vertices,
so its rank is

\[
9-8+1=2.
\tag{2.5}
\]

The \(K\)-loop traverses the first simple cycle. After cancelling that
cycle, the path for \(K^{-1}H_0\) is

\[
0\to1\to5\to8\to9\to5\to1\to0,
\tag{2.6}
\]

which traverses the second simple cycle and its bridge. Thus \(K\) and
\(K^{-1}H_0\) are the two fundamental loops for a spanning tree of the
core. Consequently the partial deterministic automaton (2.3)
recognizes exactly \(\pi(P)\le C_3*C_4\).

### 2.1 Homology coordinates

Orient every core edge from its \(x\)-vertex to its \(t\)-vertex. For a
factor move from state \(a\) to state \(b\), add

\[
\frac{-e_a+e_b}{2}
\quad\text{for an \(x\)-move},
\qquad
\frac{e_a-e_b}{2}
\quad\text{for a \(t\)-move}.
\tag{2.7}
\]

Every accepted based loop has an integral total chain. In the state
order (2.2), the two named cycles are

\[
\begin{aligned}
\mathbf c_K&=(0,1,-1,0,0,0,0,0,0),\\
\mathbf c_H&=(0,1,-1,0,0,1,-1,0,0).
\end{aligned}
\tag{2.8}
\]

If \(\mathbf c\) is the chain of an accepted loop, its exponent sums in
the free basis \((K,H_0)\) are

\[
n=\mathbf c_8,
\qquad
m=\mathbf c_1-\mathbf c_8.
\tag{2.9}
\]

This uses only homology. It is enough for the central lift because the
torus weight

\[
\operatorname{wt}(x)=4,
\qquad
\operatorname{wt}(t)=3
\tag{2.10}
\]

is a homomorphism and

\[
\operatorname{wt}(K)=-1,
\qquad
\operatorname{wt}(H_0)=-2.
\tag{2.11}
\]

### 2.2 Exact membership theorem

For \(w\in G\), read the projected amalgam normal form of \(w\) through
(2.3).

Then

\[
\boxed{
w\in P
\iff
\begin{cases}
\pi(w)\text{ is an accepted based loop},\\
\operatorname{wt}(w)=-m-2n,
\end{cases}
}
\tag{2.12}
\]

where \((m,n)\) is obtained from (2.9).

Indeed, acceptance gives the unique element \(p\in P\) with
\(\pi(p)=\pi(w)\), because the central projection is injective on \(P\).
Its weight is \(-m-2n\). Thus \(wp^{-1}\) is central, and equality of
weights forces this central power to be zero. The converse is immediate.

Direct application gives

\[
K,H_0\in P,
\qquad
L,q\notin P,
\qquad
q=c^{-1}L.
\tag{2.13}
\]

The same core gives canonical keys for arbitrary left cosets: replace
the longest readable core prefix by a fixed core transversal, retain the
first unreadable tail, and record the residual central power using
(2.12). This is an exact normal form for \(P\backslash G\).

## 3. The binary \(S_4\) lift

Define

\[
\rho:G\longrightarrow GL_2(\mathbb F_3)
\tag{3.1}
\]

by

\[
\rho(x)=
\begin{pmatrix}
0&1\\
2&1
\end{pmatrix},
\qquad
\rho(t)=
\begin{pmatrix}
0&1\\
1&1
\end{pmatrix}.
\tag{3.2}
\]

Direct multiplication gives

\[
\rho(x)^3=\rho(t)^4=
\begin{pmatrix}
2&0\\
0&2
\end{pmatrix}
=-I,
\tag{3.3}
\]

so (3.2) respects \(x^3=t^4\). The two matrices generate all of
\(GL_2(\mathbb F_3)\), of order \(48\). A short certificate is

\[
\begin{aligned}
\rho(x^{-1}t)&=
\begin{pmatrix}2&0\\0&1\end{pmatrix},\\
\rho(t^{-2}x^{-1})&=
\begin{pmatrix}1&1\\0&1\end{pmatrix},\\
\rho(t^{-1}x^{-1}t^{-1})&=
\begin{pmatrix}1&0\\1&1\end{pmatrix}.
\end{aligned}
\tag{3.4}
\]

The two elementary transvections generate \(SL_2(\mathbb F_3)\), and
the first matrix supplies determinant \(-1\).

The projectivization

\[
GL_2(\mathbb F_3)/\{\pm I\}\cong S_4
\tag{3.5}
\]

explains the earlier four-coset sieve: it forgot the sign of the central
element. The present quotient retains that sign.

Exact evaluation gives

\[
\rho(K)=
\begin{pmatrix}
1&1\\
0&2
\end{pmatrix},
\qquad
\rho(H_0)=
\begin{pmatrix}
2&2\\
1&0
\end{pmatrix}.
\tag{3.6}
\]

Put

\[
\ell=(1,2).
\tag{3.7}
\]

Then

\[
\ell\rho(K)=\ell,
\qquad
\ell\rho(H_0)=\ell.
\tag{3.8}
\]

The first matrix in (3.6) has order two, the second has order three,
and their product has order two. They do not commute, so they generate
a copy of \(S_3\), of order \(6\).
The stabilizer of a nonzero row vector in \(GL_2(\mathbb F_3)\) also has
order \(48/8=6\). Hence

\[
\boxed{
\rho(P)=
\operatorname{Stab}_{GL_2(\mathbb F_3)}(\ell).
}
\tag{3.9}
\]

## 4. The separating Fox functional

Reduce the coset module modulo \(3\) and define

\[
\mathcal F:
\mathbb F_3[P\backslash G]\longrightarrow\mathbb F_3^2,
\qquad
\mathcal F([Pg])=\ell\rho(g).
\tag{4.1}
\]

This is well-defined by (3.8).

The exact coefficient images are

\[
\rho(A_0)=
\begin{pmatrix}
2&1\\
1&2
\end{pmatrix},
\qquad
\rho(A_U)=
\begin{pmatrix}
1&0\\
1&0
\end{pmatrix}.
\tag{4.2}
\]

Therefore

\[
\ell\rho(A_0)=\ell,
\qquad
\ell\rho(A_U)=(0,0).
\tag{4.3}
\]

Applying \(\mathcal F\) to (1.2) gives the necessary target condition

\[
\boxed{
\ell\rho(g)=-\ell.
}
\tag{4.4}
\]

By (3.9), this is equivalent to

\[
\boxed{
\rho(g)\in(-I)\rho(P).
}
\tag{4.5}
\]

Thus exactly one of the eight finite left cosets survives.

### 4.1 Two targets eliminated

For \(g=1\),

\[
\ell\rho(g)=\ell\ne-\ell,
\tag{4.6}
\]

so the identity target is impossible at the Fox level.

For \(q=\gamma e^{-1}\), exact evaluation gives

\[
\rho(q)=
\begin{pmatrix}
0&1\\
2&2
\end{pmatrix},
\qquad
\ell\rho(q)=\ell.
\tag{4.7}
\]

Hence the target \(g=q\), including the simplified equation (1.5), is
also impossible at the Fox level.

The central target survives:

\[
\rho(c^{-1})=-I,
\qquad
\ell\rho(c^{-1})=-\ell.
\tag{4.8}
\]

This is why (4.4) is not a nonlift certificate.

## 5. Scope and next exact question

The theorem proves:

1. an exact nine-edge folded-core membership test for \(P<G\);
2. \(L\notin P\), so no left-\(L\) action may be imposed on
   \(P\backslash G\);
3. a binary refinement of the \(S_4\) Fox sieve;
4. exclusion of the identity target and \(g=\gamma e^{-1}\); and
5. the necessary finite target condition
   \(\rho(g)\in(-I)\rho(P)\).

It does not exclude the central target \(c^{-1}\), solve the integral
cyclic-submodule equation, solve the nonabelian free-kernel equation, or
prove anything about AC-inequivalence of the candidate.

The next exact Fox question is

\[
-[Pc^{-1}]-\pi_P(A_0)
\stackrel{?}{\in}
\pi_P(A_U)R.
\tag{5.1}
\]

A negative answer may come from a second representation whose allowed
target orbit is disjoint from (4.5), or from an exact coloring of the
infinite folded coset graph. A positive answer would provide the first
full Fox solution for this candidate, after which the nonabelian
basis-letter equation would still remain.

The core cycles, central membership rule, matrix quotient, coefficient
images, stabilizer, and excluded targets are replayed by
`tests/stable_ac/test_prefix_db_evaluated_countermodel.py`.

AK(3) remains open.
