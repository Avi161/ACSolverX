# A signed-HNN Fox master lemma for all three-cross rows

Date: 2026-07-25

Status: **PROVEN**. The abelianized free-kernel equation for every
signed three-cross history has one uniform factorization. After the two
bridge variables are quotiented out, the only sign dependence is

\[
1+\eta\theta L.
\]

Whenever \(J=\langle K,L\rangle\) is free on \((K,L)\), the positive
case is unsigned incidence on an HNN Bass--Serre forest and the negative
case is oriented incidence on the same forest. Under that hypothesis,
both operators have exact kernel \((K-1)\mathbb Z[G]\).

This theorem generalizes the HNN half of the all-target minimum-tail
obstruction. It does not generalize that proof's later
support-versus-double-coset certificate, which depends on the specific
evaluated candidate.

## 1. Abelianized semidirect-product calculus

Let

\[
H=G*\langle z\rangle,
\qquad
r_e:H\longrightarrow G
\tag{1.1}
\]

be an evaluation retraction, and put \(N=\ker r_e\). After
abelianization, identify

\[
N_{\mathrm{ab}}\cong R:=\mathbb Z[G]
\tag{1.2}
\]

as a left \(G\)-module. Write an element of
\(N_{\mathrm{ab}}\rtimes G\) as \((\mathbf x,g)\). Then

\[
\begin{aligned}
(\mathbf x,g)(\mathbf y,h)
&=(\mathbf x+g\mathbf y,gh),\\
(\mathbf x,g)^{-1}
&=(-g^{-1}\mathbf x,g^{-1}),\\
(\mathbf u,a)(\mathbf x,h)(\mathbf u,a)^{-1}
&=((1-aha^{-1})\mathbf u+a\mathbf x,aha^{-1}).
\end{aligned}
\tag{1.3}
\]

For a sign \(\sigma\in\{+1,-1\}\), the kernel part of a signed
power of \((\mathbf x,h)\) is

\[
\mathbf x^{[+]}=\mathbf x,
\qquad
\mathbf x^{[-]}=-h^{-1}\mathbf x.
\tag{1.4}
\]

## 2. The general signed history

Take

\[
\begin{aligned}
D_1&=D\,uB^\epsilon u^{-1},\\
B_1&=B\,vD_1^\eta v^{-1},\\
D_2&=D_1\,wB_1^\theta w^{-1},
\end{aligned}
\qquad
\epsilon,\eta,\theta\in\{+1,-1\}.
\tag{2.1}
\]

Write

\[
B=(\mathbf j,b),
\qquad
D=(\boldsymbol\Delta,d),
\tag{2.2}
\]

and parameterize the bridge lifts by

\[
u=(\mathbf u,\alpha),
\qquad
v=(\mathbf v,\beta),
\qquad
w=(\mathbf w,\gamma).
\tag{2.3}
\]

Their evaluated recurrence is

\[
\begin{aligned}
r&=\alpha b^\epsilon\alpha^{-1},
&
K&=dr,\\
s&=\beta K^\eta\beta^{-1},
&
C&=bs,\\
\tau&=\gamma C^\theta\gamma^{-1},
&
1&=K\tau.
\end{aligned}
\tag{2.4}
\]

Thus

\[
\tau=K^{-1}.
\tag{2.5}
\]

For the AK(3) free-kernel application,

\[
\mathbf j=-e^{-1},
\qquad
\boldsymbol\Delta=t^{-1}(1-exe^{-1}),
\tag{2.6}
\]

but the factorization below does not use those special values.

Define

\[
\mathbf j_+=\mathbf j,
\qquad
\mathbf j_-=-b^{-1}\mathbf j,
\tag{2.7}
\]

and the signed monomial coefficients

\[
\begin{aligned}
N_+&=b\beta,
&
N_-&=-b\beta K^{-1},\\
M_+&=K\gamma,
&
M_-&=-\gamma.
\end{aligned}
\tag{2.8}
\]

The minus sign in \(M_-\) follows from

\[
-K\gamma C^{-1}=-\gamma,
\tag{2.9}
\]

which is exactly the \(\theta=-1\) instance of the final evaluated
equation in (2.4).

## 3. Uniform kernel recurrence

Apply (1.3)--(1.4) to the three lines of (2.1). If

\[
D_1=(\mathbf X,K),
\qquad
B_1=(\mathbf Y,C),
\qquad
D_2=(\boldsymbol\Xi,1),
\tag{3.1}
\]

then

\[
\boxed{
\begin{aligned}
\mathbf X&=
\boldsymbol\Delta+d(1-r)\mathbf u+d\alpha\mathbf j_\epsilon,\\
\mathbf Y&=
\mathbf j+b(1-s)\mathbf v+N_\eta\mathbf X,\\
\boldsymbol\Xi&=
\mathbf X+(K-1)\mathbf w+M_\theta\mathbf Y.
\end{aligned}
}
\tag{3.2}
\]

The two variable identities

\[
d(1-r)=d-K,
\qquad
K(1-\tau)=K-1
\tag{3.3}
\]

use (2.4)--(2.5).

Put

\[
F_\epsilon=
\boldsymbol\Delta+d\alpha\mathbf j_\epsilon.
\tag{3.4}
\]

Substitution in (3.2) gives

\[
\begin{aligned}
\boldsymbol\Xi={}&
(1+M_\theta N_\eta)F_\epsilon\\
&+(1+M_\theta N_\eta)(d-K)\mathbf u\\
&+M_\theta\mathbf j
+M_\theta b(1-s)\mathbf v
+(K-1)\mathbf w.
\end{aligned}
\tag{3.5}
\]

## 4. The sign product is the only operator choice

Let

\[
m=\eta\theta.
\tag{4.1}
\]

For each pair \((\eta,\theta)\), define the group element

\[
\begin{array}{c|c}
(\eta,\theta)&L\\ \hline
(+,+)&K\gamma b\beta\\
(+,-)&\gamma b\beta\\
(-,+)&K\gamma b\beta K^{-1}\\
(-,-)&\gamma b\beta K^{-1}.
\end{array}
\tag{4.2}
\]

Direct multiplication of (2.8) gives

\[
\boxed{M_\theta N_\eta=mL.}
\tag{4.3}
\]

The other bridge coefficient satisfies

\[
\boxed{
M_\theta b(1-s)
=-mL(K-1)\beta^{-1}.
}
\tag{4.4}
\]

For \(\eta=+1\), use

\[
1-\beta K\beta^{-1}
=-\beta(K-1)\beta^{-1}.
\tag{4.5}
\]

For \(\eta=-1\), use

\[
1-\beta K^{-1}\beta^{-1}
=\beta K^{-1}(K-1)\beta^{-1}
\tag{4.6}
\]

together with \(N_-=-b\beta K^{-1}\). These are the two cases of
(4.4).

Equations (3.5), (4.3), and (4.4) prove the master factorization

\[
\boxed{
\boldsymbol\Xi
=A_0+A_U\mathbf u+A_V\mathbf v+A_W\mathbf w,
}
\tag{4.7}
\]

where

\[
\boxed{
\begin{aligned}
A_0&=(1+mL)F_\epsilon+M_\theta\mathbf j,\\
A_U&=(1+mL)(d-K),\\
A_V&=-mL(K-1)\beta^{-1},\\
A_W&=K-1.
\end{aligned}
}
\tag{4.8}
\]

### 4.1 Complete sign table

\[
\begin{array}{c|c|c|c|c|c|c}
(\epsilon,\eta,\theta)&F_\epsilon&m&M_\theta&N_\eta&L&1+mL\\ \hline
(+,+,+)&F_+&+&K\gamma&b\beta&K\gamma b\beta&1+L\\
(+,+,-)&F_+&-&-\gamma&b\beta&\gamma b\beta&1-L\\
(+,-,+)&F_+&-&K\gamma&-b\beta K^{-1}
  &K\gamma b\beta K^{-1}&1-L\\
(+,-,-)&F_+&+&-\gamma&-b\beta K^{-1}
  &\gamma b\beta K^{-1}&1+L\\
(-,+,+)&F_-&+&K\gamma&b\beta&K\gamma b\beta&1+L\\
(-,+,-)&F_-&-&-\gamma&b\beta&\gamma b\beta&1-L\\
(-,-,+)&F_-&-&K\gamma&-b\beta K^{-1}
  &K\gamma b\beta K^{-1}&1-L\\
(-,-,-)&F_-&+&-\gamma&-b\beta K^{-1}
  &\gamma b\beta K^{-1}&1+L.
\end{array}
\tag{4.9}
\]

The all-positive and all-negative rows are stable-letter
exponent-infeasible for a one-\(z\) AK(3) isolator, but the algebraic
factorization remains valid.

## 5. The bridge ideal

Put

\[
M=LKL^{-1},
\qquad
P=\langle K,M\rangle.
\tag{5.1}
\]

The identity

\[
L(K-1)\beta^{-1}
=(M-1)L\beta^{-1}
\tag{5.2}
\]

shows that right multiplication by the unit \(L\beta^{-1}\) converts
the \(A_V\)-ideal into \((M-1)R\). Hence

\[
A_VR+A_WR
=(M-1)R+(K-1)R.
\tag{5.3}
\]

The elementary group-ring identities

\[
ab-1=(a-1)b+(b-1),
\qquad
a^{-1}-1=-(a-1)a^{-1}
\tag{5.4}
\]

then give

\[
\boxed{
A_VR+A_WR
=I_P
:=\sum_{p\in P}(p-1)R.
}
\tag{5.5}
\]

Thus the two bridge variables always quotient the Fox equation to

\[
R/I_P\cong\mathbb Z[P\backslash G].
\tag{5.6}
\]

## 6. The signed-HNN incidence theorem

Assume now that

\[
J:=\langle K,L\rangle\cong F(K,L).
\tag{6.1}
\]

Then

\[
P=F(K,M),
\qquad
M=LKL^{-1},
\tag{6.2}
\]

and \(J\) has the HNN presentation

\[
J=
\left\langle
P,L
\ \middle|\
LKL^{-1}=M
\right\rangle.
\tag{6.3}
\]

For \(m\in\{+1,-1\}\), define

\[
\mathcal B_m:R\longrightarrow\mathbb Z[P\backslash G],
\qquad
\mathcal B_m(z)=\pi_P((1+mL)z).
\tag{6.4}
\]

Since \(LK=ML\),

\[
(K-1)R\subseteq\ker\mathcal B_m.
\tag{6.5}
\]

After quotienting the domain,

\[
R/(K-1)R
\cong
\mathbb Z[\langle K\rangle\backslash G],
\tag{6.6}
\]

the induced map is

\[
\boxed{
[\langle K\rangle r]
\longmapsto
[Pr]+m[PLr].
}
\tag{6.7}
\]

This is well-defined: replacing \(r\) by \(Kr\) changes the second
endpoint from \(PLr\) to

\[
PLKr=PMLr=PLr.
\tag{6.8}
\]

On every component indexed by \(J\backslash G\), the vertices
\(P\backslash J\) and edges \(\langle K\rangle\backslash J\) in (6.7)
form the Bass--Serre tree of (6.3).

### 6.1 Oriented incidence: \(m=-1\)

For \(m=-1\), (6.7) is oriented edge incidence. Every image has
ordinary coefficient sum zero on each component:

\[
\sum_{v\in T}a_v=0.
\tag{6.9}
\]

Conversely, let a finitely supported vertex chain satisfy (6.9).
Take the finite convex hull of its support, choose a root, and, for each
edge, assign the sum of the vertex coefficients in the component cut
off away from the root, with sign adjusted to the fixed edge
orientation. The resulting finite edge chain has the prescribed
boundary.

The edge chain is unique. A nonempty finite edge support in a tree has
a leaf, and its incident nonzero edge coefficient cannot cancel at that
leaf. Therefore oriented incidence is injective on finite-support edge
chains.

### 6.2 Unsigned incidence: \(m=+1\)

The HNN tree is bipartite. Give \(Pjr\) the color

\[
\chi(j)\in\mathbb Z/2,
\qquad
\chi(K)=0,\quad\chi(L)=1.
\tag{6.10}
\]

Multiplying each vertex coordinate by
\((-1)^{\operatorname{color}(v)}\) converts unsigned incidence into
oriented incidence. Hence the exact image condition is

\[
\sum_{v\in T}
(-1)^{\operatorname{color}(v)}a_v=0
\tag{6.11}
\]

on every component. Unsigned incidence is also injective on
finite-support edge chains.

### 6.3 Exact kernels

The induced maps in (6.7) are injective for both signs. Combining this
with (6.5)--(6.6) gives

\[
\boxed{
\ker\mathcal B_+
=\ker\mathcal B_-
=(K-1)R.
}
\tag{6.12}
\]

For \(m=-1\), a two-point chain has a preimage exactly when its
coefficients are opposite and its vertices are in the same component;
the preimage is the unique oriented geodesic path. For \(m=+1\), the
corresponding criterion is zero signed bipartite sum; equal endpoint
coefficients require opposite colors and produce the unique alternating
path.

## 7. Relation to the minimum-tail obstruction

The repositioned row-\((+,-,-)\) has

\[
m=\eta\theta=+1,
\qquad
L=\gamma b\beta K^{-1}.
\tag{7.1}
\]

Thus (4.8), (5.5), and (6.12) specialize exactly to the unsigned HNN
factorization used in
`AK3_MINIMUM_TAIL_ALL_TARGET_FOX_OBSTRUCTION.md`.

The present theorem also exposes the first nonuniform step. After the
unique signed path is chosen, the residual equation depends on the
candidate-specific vector

\[
\pi_Q(F_\epsilon a),
\qquad
Q=\langle d,K\rangle,
\tag{7.2}
\]

and on the candidate-specific double-coset geometry of \(Q\) and \(J\).
The special identities which put an uncancellable coset outside \(QJ\)
in the row-\((+,-,-)\) candidate do not follow from the sign triple.

In particular, this theorem does not claim an all-row obstruction.
The four \(m=-1\) rows have quotient-\(B\) minimum length at least eight,
so they do not occur at the global minimum-tail length six. The only
other length-six sign row is \((-,+,+)\); its four old literal
representatives fail the first evaluated bridge equation, and no
repositioned exact candidate in that row has yet been certified.

## 8. Verification boundary

The independent replay checks:

1. all eight signed semidirect recurrences in a nonabelian finite group;
2. every factor \(M_\theta N_\eta=mL\);
3. every \(A_V=-mL(K-1)\beta^{-1}\) identity;
4. the bridge-ideal conjugation identity (5.2);
5. oriented and unsigned incidence, reconstruction, and uniqueness on
   finite trees.

The infinite theorem uses only the displayed semidirect-product
calculation and the Bass--Serre tree of the exact HNN presentation. No
word-radius cutoff, finite AC graph, or search budget enters the proof.

What remains open:

- construct a repositioned evaluated candidate in the other length-six
  row \((-,+,+)\);
- decide its candidate-specific \(Q\)-\(J\) double-coset equation;
- primitive multi-\(z\) eliminators and other mechanisms outside the
  one-\(z\) finish;
- AK(3) and the Andrews--Curtis conjecture.
