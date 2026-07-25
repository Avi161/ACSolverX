# Quotient-B cyclic-length gap for every three-cross killer row

Date: 2026-07-25

Status: **PROVEN** for every one of the six exponent-feasible prefix-\(DB\)
three-cross rows, with arbitrary event conjugators, multiplication sides,
intermediate orientations, vertex twists, and fixed-\(R\) gauges. Four
commutator rows either return directly to the braid class or have quotient
cyclic length at least \(8\). The two same-orientation rows have quotient
cyclic length at least \(6\). The positive-length cases remain open.

## 1. Setup

Put

\[
R=x^3t^{-4},
\qquad
G=\langle x,t\mid R\rangle,
\qquad
H=G*\langle z\rangle,
\qquad
p=xt,
\tag{1.1}
\]

and

\[
B=z^{-1}p,
\qquad
D=t^{-1}zxz^{-1},
\qquad
D_p=D[z\mapsto p].
\tag{1.2}
\]

Use the \(DBD\) representative of the final-target-switch pair. In
canonical right-product notation, its three events have quotient shadows

\[
\begin{aligned}
D_1&=D\,uB^\epsilon u^{-1},\\
B_1&=B\,vD_1^\eta v^{-1},\\
D_2&=D_1\,wB_1^\theta w^{-1},
\end{aligned}
\qquad
\epsilon,\eta,\theta\in\{1,-1\}.
\tag{1.3}
\]

Opposite multiplication sides change these target words only by
conjugacy. Whole-slot conjugations, orientations, and fixed-\(R\) gauges
are absorbed into the displayed conjugators and signs.

Suppose a final orientation and conjugation produce a legal isolator

\[
D_2^\delta\sim_H z^{-1}e,
\qquad
\delta\in\{1,-1\}.
\tag{1.4}
\]

Define

\[
b=e^{-1}p.
\tag{1.5}
\]

## 2. Quotient by the original \(B\)

Let

\[
q_B:H\longrightarrow H/\langle\!\langle B\rangle\!\rangle\cong G.
\tag{2.1}
\]

This quotient sets \(z=p\). Put

\[
A=q_B(D)=D_p.
\tag{2.2}
\]

The first source factor in (1.3) dies, so \(D_1\) maps to a conjugate of
\(A\). After choosing that conjugate as representative, \(B_1\) maps to
a conjugate of \(A^\eta\). Therefore \(D_2\) maps, up to conjugacy, to

\[
\boxed{
W_m(h)=AhA^mh^{-1},
\qquad
m=\eta\theta,
}
\tag{2.3}
\]

for some \(h\in G\). Reversing multiplication side or changing the
chosen representative replaces (2.3) only by a conjugate. Every
whole-slot inversion has already been absorbed into
\(\epsilon,\eta,\theta,\delta\); there is no residual inverse ambiguity
after those canonical signs are fixed.

The isolator has quotient shadow

\[
q_B(z^{-1}e)=p^{-1}e=b^{-1}.
\tag{2.4}
\]

Thus (1.4) forces

\[
W_m(h)^\delta\sim_G b^{-1},
\tag{2.5}
\]

or equivalently

\[
\boxed{
b\sim_GW_m(h)^{-\delta}.
}
\tag{2.6}
\]

This is a necessary condition for literal one-\(z\) liftability. It is
strictly stronger than the equations obtained only after substituting
\(z=e\).

## 3. The six rows

The exponent and weight recurrences give:

| \((\epsilon,\eta,\theta)\) | \(\delta\) | \(\operatorname{wt}(e)\) | \(\operatorname{wt}(b)\) | \(m=\eta\theta\) | required class |
|---|---:|---:|---:|---:|---|
| \((+,+,-)\) | \(-1\) | \(7\) | \(0\) | \(-1\) | \(W_{-1}\) |
| \((+,-,+)\) | \(1\) | \(7\) | \(0\) | \(-1\) | \(W_{-1}^{-1}\) |
| \((+,-,-)\) | \(1\) | \(9\) | \(-2\) | \(1\) | \(W_1^{-1}\) |
| \((-,+,+)\) | \(-1\) | \(5\) | \(2\) | \(1\) | \(W_1\) |
| \((-,+,-)\) | \(-1\) | \(7\) | \(0\) | \(-1\) | \(W_{-1}\) |
| \((-,-,+)\) | \(1\) | \(7\) | \(0\) | \(-1\) | \(W_{-1}^{-1}\) |

\[
\tag{3.1}
\]

The four \(m=-1\) rows are commutator rows:

\[
W_{-1}(h)=[A,h].
\tag{3.2}
\]

The other two are same-orientation product rows.

## 4. Complete Bass--Serre length spectra

Project to

\[
\Gamma
=
G/\langle x^3\rangle
\cong
C_3*C_4
=
\langle X,T\mid X^3=T^4=1\rangle.
\tag{4.1}
\]

Write a bar for projection. The cyclically reduced alternating form of
\(\bar A\) has syllable length

\[
\ell_{\mathrm{cyc}}(\bar A)=6.
\tag{4.2}
\]

### Theorem 4.1

For arbitrary \(h\in\Gamma\),

\[
\boxed{
\begin{aligned}
m=-1:\quad&
\ell_{\mathrm{cyc}}(W_{-1}(h))
\in\{0,8,10,12\}
\ \text{or equals }12+2d\ge14,\\
m=1:\quad&
\ell_{\mathrm{cyc}}(W_1(h))
\in\{6,10,12\}
\ \text{or equals }12+2d\ge14,
\end{aligned}
}
\tag{4.3}
\]

where the second alternative occurs when the two relevant axes are
disjoint at distance \(d\ge1\).

### Proof

Regard \(W_m(h)\) as the product of \(\bar A\) and the conjugate
\(h\bar A^mh^{-1}\), and compare their axes in the Bass--Serre tree.

If the axes are disjoint at distance \(d\ge1\), the cyclically reduced
product traverses one length-six translation segment on each axis and
the bridge twice. Hence

\[
\ell_{\mathrm{cyc}}(W_m(h))
=
6+6+2d
=
12+2d
\ge14.
\tag{4.4}
\]

Suppose the axes intersect. If they share an edge, its stabilizer is
trivial. Base at an overlap endpoint: the product is represented by
\(UV\), where \(U\) is one of the six syllable rotations of \(\bar A\)
and \(V\) is one of the six rotations of \(\bar A^m\). Cyclic reduction
includes every positive overlap, ray, or identical-axis case.

If the axes meet only at a vertex, the residual frame ambiguity is an
element of that vertex stabilizer. The overcomplete union of the two
possible stabilizers is

\[
\mathcal K
=
\{1,X,X^2,T,T^2,T^3\}.
\tag{4.5}
\]

It is therefore enough to cyclically reduce

\[
UkVk^{-1}
\tag{4.6}
\]

for the \(6\cdot6\cdot6=216\) triples \((U,V,k)\). The exact
distributions are:

\[
\begin{array}{c|rrrrr}
&0&6&8&10&12\\ \hline
m=-1&18&0&40&28&130\\
m=1&0&52&0&42&122.
\end{array}
\tag{4.7}
\]

For reference, the \(k=1\) template slice, which covers every shared-edge
case, has counts

\[
\begin{array}{c|rrrrr}
&0&6&8&10&12\\ \hline
m=-1&6&0&8&4&18\\
m=1&0&12&0&6&18.
\end{array}
\tag{4.8}
\]

The remaining \(180\) nonidentity-twist templates supply the difference
between (4.7) and (4.8). These are an overcomplete encoding, not a count
of geometrically distinct vertex-only configurations. This exhausts the
axis trichotomy and proves
Theorem 4.1. \(\square\)

## 5. Consequences for the six rows

Conjugation and inversion preserve cyclic length. Equations (2.6) and
(4.3) give the necessary spectra

\[
\boxed{
\begin{aligned}
\eta\theta=-1:\quad&
\ell_{\mathrm{cyc}}(\bar b)
\in\{0,8,10,12\}
\ \text{or }\ell_{\mathrm{cyc}}(\bar b)\ge14,\\
\eta\theta=1:\quad&
\ell_{\mathrm{cyc}}(\bar b)
\in\{6,10,12\}
\ \text{or }\ell_{\mathrm{cyc}}(\bar b)\ge14.
\end{aligned}
}
\tag{5.1}
\]

In particular:

1. no commutator row can have quotient cyclic length \(2,4,\) or \(6\);
2. no same-orientation row can have length \(0,2,4,\) or \(8\); and
3. every liftable prefix-\(DB\) route with \(\bar b\ne1\) has quotient
   cyclic length at least \(6\).

### 5.1 The minimum same-orientation classes

The \(52\) length-six templates in the \(m=1\) row split equally between
exactly two conjugacy classes:

\[
\begin{aligned}
L_1&=TX T^2X^2T^3X^2,\\
L_2&=TX^2T^3X^2T^2X.
\end{aligned}
\tag{5.2}
\]

Here adjacent symbols denote alternating syllables in
\(C_3*C_4\). Each class occurs in \(26\) templates.

Choose the positive-word lifts

\[
\begin{aligned}
\widetilde L_1&=txt^2x^2t^3x^2,\\
\widetilde L_2&=tx^2t^3x^2t^2x.
\end{aligned}
\tag{5.3}
\]

Both have torus weight \(38\). The unique weight-two \(G\)-conjugacy class
above each \(L_j\) is represented by

\[
\lambda_j=c^{-3}\widetilde L_j,
\qquad
\operatorname{wt}(\lambda_j)=2.
\tag{5.4}
\]

For a route satisfying the necessary quotient equation (2.6), quotient
length six in either \(m=1\) row is therefore equivalent to

\[
\boxed{
b^{-\delta}\sim_G\lambda_j
\quad
\text{for some }j\in\{1,2\}.
}
\tag{5.5}
\]

Since \(b=e^{-1}p\), this gives the exact tail classes

\[
\boxed{
[e]_G
=
[p\,g\lambda_j^\delta g^{-1}]_G
}
\tag{5.6}
\]

for some \(g\in G\).

These minimum classes do not by themselves force the survivor to the
braid class. Put

\[
C_0=c^{-2}x^2t^3x^2.
\tag{5.7}
\]

It is the weight-one non-braid killer from the evaluated countermodel.
In the row \((\epsilon,\eta,\theta)=(-,+,+)\), take

\[
C=C_0,
\qquad
K=C^{-1},
\qquad
\gamma=1,
\qquad
\rho=\beta\in\{xt^3,xt^2\},
\tag{5.8}
\]

and define

\[
b=C\rho C\rho^{-1}.
\tag{5.9}
\]

The two choices of \(\rho\) give \(L_1,L_2\), respectively, and solve the
last two evaluated equations exactly. For the dual row \((+,-,-)\), take
\(C=C_0^{-1}\), \(K=C\), and the same two choices of \(\rho\); then
\(b^{-1}\) gives \(L_1,L_2\).

Thus neither the length-six quotient class nor the last two evaluated
equations close the endpoint. The unresolved conditions are the first
equation

\[
K=d\alpha b^\epsilon\alpha^{-1}
\tag{5.10}
\]

and literal free-kernel liftability.

## 6. Length zero is a self-loop

Length zero can occur only in a commutator row. Every such row has

\[
\operatorname{wt}(e)=7,
\qquad
\operatorname{wt}(b)=0.
\tag{6.1}
\]

If

\[
\ell_{\mathrm{cyc}}(\bar b)=0,
\tag{6.2}
\]

then \(\bar b=1\), so

\[
b=c^q,
\qquad
c=x^3=t^4
\tag{6.3}
\]

for some \(q\in\mathbb Z\). Since
\(\operatorname{wt}(c)=12\), equation (6.1) forces

\[
q=0,
\qquad
b=1.
\tag{6.4}
\]

Now \(b=e^{-1}p\) gives

\[
e=p
\tag{6.5}
\]

in \(G\). Evaluate the first two target equations. The evaluated
original \(D\)-slot is \(D_p\); because \(b^\epsilon=1\),

\[
K=D_p.
\tag{6.6}
\]

The survivor is

\[
C=\beta K^\eta\beta^{-1},
\tag{6.7}
\]

so it is conjugate to \(D_p^\eta\). The fixed-\(R\) lemma, AC3, and if
needed AC2 return

\[
(R,C)\sim_{\mathrm{AC1-3}}\operatorname{AK}(3).
\tag{6.8}
\]

Thus the zero-length branch is a classical self-loop. A non-braid
liftable commutator row must satisfy

\[
\boxed{
\ell_{\mathrm{cyc}}(\bar b)\ge8.
}
\tag{6.9}
\]

## 7. Scope

The theorem gives an unbounded necessary condition: arbitrary bridges
are handled by the Bass--Serre axis trichotomy, not by bounding their word
length. It closes the zero-length branch and excludes three further
short lengths in each sign family.

It does not prove that every allowed positive-length class is liftable,
does not classify its evaluated survivor, and does not give an AC
obstruction. The remaining three-cross problem begins at quotient length
\(8\) in the four commutator rows and at length \(6\) in the two
same-orientation rows.

The dependency-free replay

```text
tests/stable_ac/test_prefix_db_evaluated_countermodel.py
```

checks both \(216\)-case distributions and the complete six-row table.

AK(3) remains open.
