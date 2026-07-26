# All-target Fox obstruction for the repositioned AK(3) minimum tail

Date: 2026-07-25

Status: **PROVEN**. For the repositioned row-\((+,-,-)\) minimum-tail
candidate, no target \(g\in G\) solves the exact Fox coset equation.

This is not a bounded search. The HNN Bass--Serre forest first
classifies every target for which the two-point right-hand side has an
edge-chain preimage. Every such preimage has moving support in one
translate of

\[
J=\langle K,L\rangle.
\]

A folded-core fiber product then proves that a fixed central coset in
the residual \(Q=\langle d,K\rangle\) module lies outside all of that
moving support.

The theorem closes this particular minimum-tail lift. It does not close
the full AC4/AC5 move space, and it does not prove or disprove the
Andrews--Curtis conjecture.

## 1. The arbitrary-target equation

Use the notation and exact identities proved in
`AK3_MINIMUM_TAIL_CENTRAL_TARGET_OBSTRUCTION.md`. In particular,

\[
\begin{aligned}
R&=\mathbb Z[G],\\
c&=x^3=t^4,\\
P&=\langle K,H\rangle
  =\langle K,LKL^{-1}\rangle,\\
J&=\langle P,L\rangle=\langle K,L\rangle,\\
q&=\gamma e^{-1}=c^{-1}L=Lc^{-1},\\
F_0&=t^{-1}-d-dte^{-1},\\
A_0&=(1+L)F_0+q,\\
A_U&=(1+L)(d-K).
\end{aligned}
\tag{1.1}
\]

The target \(g\in G\) solves the Fox equation precisely when some
\(u\in R\) satisfies

\[
\pi_P(A_0)+\pi_P(A_Uu)=-[Pg].
\tag{1.2}
\]

Define

\[
\mathcal B:R\longrightarrow\mathbb Z[P\backslash G],
\qquad
\mathcal B(z)=\pi_P((1+L)z).
\tag{1.3}
\]

Substituting (1.1) into (1.2) gives

\[
\boxed{
\mathcal B\bigl(F_0+(d-K)u\bigr)
=-[Pg]-[Pq].
}
\tag{1.4}
\]

The earlier HNN theorem proved

\[
J=
\left\langle
P,L
\ \middle|\
LKL^{-1}=HK^{-1}
\right\rangle
\tag{1.5}
\]

and

\[
\boxed{\ker\mathcal B=(K-1)R.}
\tag{1.6}
\]

We now need the image, not only the kernel, of \(\mathcal B\).

## 2. Exact HNN path classification

Modulo \((K-1)R\), the map \(\mathcal B\) is the unsigned
edge-incidence map on a forest:

\[
\begin{aligned}
\text{vertices}&=P\backslash G,\\
\text{edges}&=\langle K\rangle\backslash G,\\
[\langle K\rangle r]&\longmapsto[Pr]+[PLr].
\end{aligned}
\tag{2.1}
\]

Its components are indexed by \(J\backslash G\). Each component is a
copy of the Bass--Serre tree of (1.5).

### 2.1 Bipartite color

Because \(J=F(K,L)\), define

\[
\chi:J\longrightarrow\mathbb Z/2,
\qquad
\chi(K)=0,\quad\chi(L)=1.
\tag{2.2}
\]

Both generators \(K\) and \(LKL^{-1}\) of \(P\) have color zero, so
\(\chi(P)=0\). Hence

\[
\operatorname{color}(Pjr)=\chi(j)
\tag{2.3}
\]

is well-defined on every component. The endpoints in (2.1) have
opposite colors.

For a finite vertex chain in a bipartite graph, unsigned incidence has
zero signed color-sum:

\[
\sum_v(-1)^{\operatorname{color}(v)}a_v=0.
\tag{2.4}
\]

On a tree, this is the only obstruction. For the two-point chain needed
here, the statement is immediate from the unique path: alternating
coefficients on its edges produce the two endpoint coefficients if and
only if the endpoints have opposite colors.

### 2.2 Target parameterization

The vertices \(Pg\) and \(Pq\) lie in the same component precisely when

\[
Jg=Jq=Jc^{-1},
\tag{2.5}
\]

or equivalently

\[
g=jc^{-1}
\quad\text{for some }j\in J.
\tag{2.6}
\]

The start vertex is

\[
Pq=PLc^{-1},
\tag{2.7}
\]

of color one. The target \(Pjc^{-1}\) has color \(\chi(j)\). Therefore
the two-point chain in (1.4) lies in the image of \(\mathcal B\) if and
only if

\[
\boxed{
g=jc^{-1},
\qquad
j\in J,
\qquad
\chi(j)=0.
}
\tag{2.8}
\]

This is a necessary-and-sufficient classification over the infinite
group \(G\).

### 2.3 The unique preimage

Suppose (2.8) holds. Let

\[
v_0=Pq,\ v_1,\ldots,v_{2m+1}=Pg
\tag{2.9}
\]

be the unique geodesic in the HNN tree, and let

\[
e_i=\langle K\rangle r_i
\tag{2.10}
\]

be its successive edges. The path has odd length because its endpoints
have opposite colors.

The unique finite edge chain with incidence
\(-[Pg]-[Pq]\) is

\[
\bar z_g=-e_1+e_2-\cdots-e_{2m+1}.
\tag{2.11}
\]

Indeed, the coefficient at \(v_0\) forces the first edge coefficient
to be \(-1\); every internal vertex forces the next coefficient to
change sign; and odd length gives coefficient \(-1\) at the terminal
vertex. Uniqueness also follows from injectivity of finite-support
incidence on a tree.

Choose representatives \(r_i\in G\) and put

\[
z_g=-r_1+r_2-\cdots-r_{2m+1}\in R.
\tag{2.12}
\]

Changing an edge representative changes \(z_g\) by an element of
\((K-1)R\), and every preimage of the two-point chain differs from
\(z_g\) by an element of \((K-1)R\).

## 3. The residual \(Q\)-coset criterion

Equation (1.4) is solvable if and only if

\[
F_0+(d-K)u-z_g\in(K-1)R
\tag{3.1}
\]

for some \(u\in R\). Equivalently,

\[
z_g-F_0\in(d-K)R+(K-1)R.
\tag{3.2}
\]

Since

\[
d-K=(d-1)-(K-1),
\tag{3.3}
\]

the right-hand side is

\[
I_Q=(d-1)R+(K-1)R,
\qquad
Q=\langle d,K\rangle.
\tag{3.4}
\]

Thus the exact remaining condition is

\[
\boxed{
\pi_Q(z_g)=\pi_Q(F_0)
\quad\text{in }\mathbb Z[Q\backslash G].
}
\tag{3.5}
\]

### 3.1 Support of every moving path

The entire path (2.9) lies in the component indexed by \(Jc^{-1}\).
Every edge therefore has a representative

\[
r_i=s_i c^{-1},
\qquad
s_i\in J.
\tag{3.6}
\]

Using these representatives in (2.12) gives

\[
\boxed{
\operatorname{supp}(z_gc)\subset J.
}
\tag{3.7}
\]

Consequently

\[
\operatorname{supp}\bigl(\pi_Q(z_g)c\bigr)
\subset
\{Qj:j\in J\}
=:QJ.
\tag{3.8}
\]

Here \(QJ\) denotes a set of left \(Q\)-cosets, not a claim that the
setwise product \(QJ\) is a subgroup.

### 3.2 The fixed vector

Right multiplication by \(c\) sends the other side of (3.5) to

\[
F_0c=t^{-1}c-dc-dte^{-1}c.
\tag{3.9}
\]

The exact identities

\[
t^{-1}c=t^3,
\qquad
dte^{-1}=c^{-1}xt
\tag{3.10}
\]

and \(d\in Q\) give

\[
\boxed{
\pi_Q(F_0)c
=[Qt^3]-[Qc]-[Qxt].
}
\tag{3.11}
\]

The proof will be complete once \(Qc\) is shown to lie outside \(QJ\)
and outside the other two support cosets in (3.11).

## 4. The projected \(Q\)-\(J\) intersection

Let

\[
\varpi:G\longrightarrow
\Gamma=C_3*C_4
\tag{4.1}
\]

be the quotient by the central subgroup \(\langle c\rangle\), and use
bars for projected elements and subgroups.

The earlier folded-core theorems proved that

\[
Q=F(d,K),
\qquad
J=F(K,L),
\tag{4.2}
\]

and that \(\varpi\) is injective on each of \(Q\) and \(J\). We now
compute \(\bar Q\cap\bar J\).

### 4.1 Based fiber-product core

The folded \(Q\)-core has root \(0\) and partial factor cycles

\[
\begin{aligned}
x:\;&(0\,1\,2),\ (3\,5\,6),\ (8\,10\,11),\\
t:\;&(1\,2\,3\,4),\ (5\,7\,8\,9),\ (11\,12\,13\,0).
\end{aligned}
\tag{4.3}
\]

The folded \(J\)-core has root \(3\) and cycles

\[
x:(3\,0\,1),
\qquad
t:(0\,1\,2\,3),
\tag{4.4}
\]

with the unused incidences treated as boundary incidences rather than
loops.

Form the based fiber product at \((0,3)\) and prune its hanging
edges. Its nine core edge-pairs are

\[
\begin{array}{c|ccccccccc}
\text{index}
&0&1&2&3&4&5&6&7&8\\ \hline
\text{pair}
&(2,1)&(8,1)&(3,1)&(11,0)&(0,3)
&(2,0)&(1,0)&(5,3)&(1,3).
\end{array}
\tag{4.5}
\]

They meet four \(x\)-factor vertices

\[
\{0,4,6\},\quad
\{1,3\},\quad
\{2,7\},\quad
\{5,8\},
\tag{4.6}
\]

and four \(t\)-factor vertices

\[
\{0,6\},\quad
\{1,7\},\quad
\{2,5,8\},\quad
\{3,4\}.
\tag{4.7}
\]

Thus the connected core has

\[
E=9,\qquad V=8,\qquad E-V+1=2.
\tag{4.8}
\]

By the folded fiber-product theorem, its based fundamental group is
\(\bar Q\cap\bar J\).

### 4.2 A free basis from the two chords

The seven edges

\[
\{0,1,2,3,4,5,7\}
\tag{4.9}
\]

form a spanning tree. The chords are edge \(6=(1,0)\) and edge
\(8=(1,3)\).

The common loop

\[
\bar K=xtx
\tag{4.10}
\]

has edge-state path

\[
(0,3)\to(1,0)\to(2,1)\to(0,3).
\tag{4.11}
\]

It crosses chord \(6\) once and never crosses chord \(8\).

Define

\[
\bar h=
t\,x\,t^2x^2t^2x\,t\,x\,t^2x^2t^3.
\tag{4.12}
\]

At syllable boundaries its edge-state path is

\[
\begin{aligned}
(0,3)&\to(11,0)\to(8,1)\to(5,3)\to(3,1)\to(1,3)\\
&\to(2,0)\to(3,1)\to(5,3)\to(8,1)\to(11,0)\to(0,3).
\end{aligned}
\tag{4.13}
\]

It crosses chord \(8\) once in the negative direction and never
crosses chord \(6\). Collapsing the spanning tree in (4.9) therefore
sends \(\bar K,\bar h\) exactly to the two oriented chord loops, not
merely to two homologically independent elements. Hence

\[
\boxed{
\bar Q\cap\bar J
=F(\bar K,\bar h).
}
\tag{4.14}
\]

## 5. Vanishing of the central lift defect

Because the restrictions of \(\varpi\) to \(Q\) and \(J\) are
injective, every \(w\in\bar Q\cap\bar J\) has unique lifts

\[
s_Q(w)\in Q,
\qquad
s_J(w)\in J.
\tag{5.1}
\]

Their discrepancy lies in the central kernel:

\[
s_Q(w)s_J(w)^{-1}=c^{\delta(w)}
\tag{5.2}
\]

for a homomorphism

\[
\delta:\bar Q\cap\bar J\longrightarrow\mathbb Z.
\tag{5.3}
\]

The lift of \(\bar K\) is literally \(K\) in both subgroups. For the
second basis element, define

\[
\begin{aligned}
h_Q&=d^{-1}K^{-1}d,\\
h_J&=
L^{-1}K^{-1}LK^{-2}LKL^{-1}KL.
\end{aligned}
\tag{5.4}
\]

Amalgam normal form gives the exact equality

\[
\boxed{
h_Q=h_J
=
c^{-5}
t\,x\,t^2x^2t^2x\,t\,x\,t^2x^2t^3.
}
\tag{5.5}
\]

Therefore \(\delta\) vanishes on the free basis in (4.14), and hence

\[
\boxed{\delta=0.}
\tag{5.6}
\]

### 5.1 The central double coset is absent

Suppose for contradiction that

\[
Qc\in QJ.
\tag{5.7}
\]

Then \(Qc=Qj\) for some \(j\in J\), so

\[
c=qj
\tag{5.8}
\]

for some \(q\in Q\). Projection to \(\Gamma\) gives

\[
\bar q=\bar j^{-1}\in\bar Q\cap\bar J.
\tag{5.9}
\]

Since the two lift sections agree on the entire intersection by
(5.6), the elements \(q\) and \(j^{-1}\) are equal in \(G\).
Equation (5.8) would then give \(c=1\), a contradiction. Thus

\[
\boxed{Qc\notin QJ.}
\tag{5.10}
\]

In fact the same proof gives the well-typed coset statement

\[
\{Qc^n:n\in\mathbb Z\}
\cap
\{Qj:j\in J\}
=\{Q\}.
\tag{5.11}
\]

## 6. The fixed coefficient cannot cancel

It remains only to make sure the other two terms in (3.11) do not
represent \(Qc\). In the folded \(Q\)-core, the shadow of \(c\) is the
identity and remains at the root \(0\), while

\[
t^3:0\longmapsto13,
\qquad
xt:0\longmapsto1\longmapsto2.
\tag{6.1}
\]

Neither endpoint is the root. Therefore

\[
Qc\ne Qt^3,
\qquad
Qc\ne Qxt.
\tag{6.2}
\]

The coefficient of \(Qc\) in (3.11) is consequently exactly \(-1\).
By (5.10), the coefficient of \(Qc\) in
\(\pi_Q(z_g)c\) is zero for every HNN-admissible target.

Hence (3.5) fails for every target satisfying (2.8). Targets not
satisfying (2.8) already fail the first HNN incidence equation. We
obtain the all-target theorem:

\[
\boxed{
\text{For every }g\in G,\quad
-[Pg]-\pi_P(A_0)
\notin
\pi_P(A_U R).
}
\tag{6.3}
\]

Equivalently, the repositioned minimum-tail candidate has no exact Fox
lift for any final target.

## 7. Independent finite double-coset certificate

There is also a shorter independent certificate for the support
separation. Define

\[
\sigma:G\longrightarrow S_5
\tag{7.1}
\]

by

\[
\sigma(x)=(0\,1\,2),
\qquad
\sigma(t)=(1\,2\,3\,4).
\tag{7.2}
\]

Both defining powers map to the identity, so \(\sigma(c)=1\). Exact
evaluation gives

\[
\begin{aligned}
\sigma(K)&=(1\,3\,4\,2),\\
\sigma(d)&=(2\,3),\\
\sigma(L)&=(0\,3)(1\,2).
\end{aligned}
\tag{7.3}
\]

Put

\[
Q_0=\sigma(Q),
\qquad
J_0=\sigma(J).
\tag{7.4}
\]

Direct subgroup closure gives

\[
|Q_0|=8,
\qquad
|J_0|=20,
\qquad
|Q_0J_0|=40,
\tag{7.5}
\]

and the exact membership check gives

\[
\boxed{\sigma(t^{-1})\notin Q_0J_0.}
\tag{7.6}
\]

The three left \(Q_0\)-cosets

\[
Q_0\sigma(t^{-1}),
\qquad
Q_0,
\qquad
Q_0\sigma(xt)
\tag{7.7}
\]

are pairwise distinct. Thus the finite image of (3.11) has coefficient
\(+1\) at \(Q_0\sigma(t^{-1})\), while every image of the moving support
in (3.8) is contained in \(Q_0J_0\). This proves the same all-target
contradiction without using the stronger assertion \(Qc\notin QJ\).

## 8. Verification boundary

The executable replay checks:

1. the nine-edge based fiber-product core and its rank;
2. the two spanning-tree chord paths in (4.11) and (4.13);
3. the exact equality of the \(Q\)- and \(J\)-lifts in (5.5);
4. the normal-form identities used in (3.10);
5. the separation of \(Qc\) from the other support cosets;
6. the independent \(S_5\) product-set certificate (7.5)--(7.7).

The infinite conclusions are the tree-incidence theorem, the standard
folded fiber-product theorem, and the central lift-defect argument.
No finite radius, word-length cutoff, or AC graph cap enters (6.3).

What is closed:

- every target in this exact Fox equation;
- therefore the repositioned row-\((+,-,-)\) minimum-tail candidate.

What remains open:

- non-minimum and other sign-row recovery mechanisms;
- histories outside this fixed-\(R\), one-\(z\) finish;
- the full AC4/AC5 move space;
- the Andrews--Curtis conjecture.
