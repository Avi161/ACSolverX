# A literal-kernel gate and a primitive multi-\(q\) AK(3) word

Date: 2026-07-25

Status: **PROVEN**. A primitive word in
\(F(X)*\langle q\rangle\) that becomes literally trivial when \(q=1\)
is conjugate to \(q^{\pm1}\). Thus a genuinely new primitive
multi-\(q\) eliminator for AK(3) must use the retained relation
\(x^3=t^4\) essentially. In the natural three-\(q\) split family over
\(R=x^3t^{-4}\), exactly one of the six seam words is primitive. Its
coherent ambient-automorphism use is an exact self-loop, while its
asymmetric production remains open.

This does not prove that AK(3) is stably AC-trivial.

## 1. The literal free-kernel barrier

Let \(X\) be a finite basis, let

\[
F=F(X)*\langle q\rangle,
\]

and let

\[
\rho:F\longrightarrow F(X)
\tag{1.1}
\]

fix \(X\) and kill \(q\).

### Theorem 1.1 (primitive literal-kernel barrier)

If \(W\in F\) is primitive and \(\rho(W)=1\), then \(W\) is conjugate
in \(F\) to \(q\) or \(q^{-1}\).

#### Proof

Put

\[
M=\langle\!\langle W\rangle\!\rangle_F,
\qquad
N=\langle\!\langle q\rangle\!\rangle_F=\ker\rho.
\]

The hypothesis \(\rho(W)=1\) gives \(M\subseteq N\), hence a natural
surjection

\[
F/M\longrightarrow F/N.
\tag{1.2}
\]

Because \(W\) is primitive, it belongs to a free basis of \(F\).
Killing \(W\) therefore leaves a free group of rank \(|X|\). Killing
\(q\) also leaves the free group \(F(X)\), of rank \(|X|\).

A surjection between two finite-rank free groups of the same rank is an
isomorphism: choose an abstract isomorphism in the reverse direction and
compose to obtain a surjective endomorphism of a finite-rank free group,
then use Hopficity. Thus (1.2) is an isomorphism and

\[
M=N.
\tag{1.3}
\]

The Magnus normal-closure theorem says that two elements of a free group
with the same normal closure are conjugate up to inversion. Applying it
to \(W\) and \(q\) proves the claim. \(\square\)

Magnus's original one-relator paper is:
Wilhelm Magnus, “Über diskontinuierliche Gruppen mit einer definierenden
Relation (Der Freiheitssatz),” *Journal für die reine und angewandte
Mathematik* **163** (1930), 141–165,
<https://doi.org/10.1515/crll.1930.163.141>.

### Corollary 1.2 (the retained relation is unavoidable)

Let

\[
G=\langle X\mid\mathcal R\rangle
\]

and suppose that a primitive \(W\in F(X)*\langle q\rangle\) becomes
trivial after \(q\mapsto1\) and passage to \(G\). If \(W\) is not
conjugate to \(q^{\pm1}\), then

\[
\rho(W)\ne1\quad\text{in }F(X),
\qquad
\rho(W)\in\langle\!\langle\mathcal R\rangle\!\rangle_{F(X)}.
\tag{1.4}
\]

Thus a genuine multi-\(q\) primitive eliminator cannot merely hide
inside the free kernel of \(q\mapsto1\). It must consume a nontrivial
consequence of the retained relators.

For the AK(3) torus-knot quotient used below,

\[
G=\langle x,t\mid R\rangle,
\qquad
R=x^3t^{-4}.
\tag{1.5}
\]

## 2. The universal Fox certificate

Let

\[
\eta:F(X)*\langle q\rangle\longrightarrow G
\]

kill \(q\), and suppose \(\eta(W)=1\). Write

\[
D_a=\eta_*\left(\frac{\partial W}{\partial a}\right)
\in\mathbb Z[G]
\tag{2.1}
\]

for the evaluated left Fox derivatives.

### Proposition 2.1 (primitive Fox row)

If \(W\) is primitive, then the row

\[
(D_a)_{a\in X\cup\{q\}}
\tag{2.2}
\]

is right-unimodular over \(\mathbb Z[G]\). It also satisfies

\[
\sum_{a\in X}D_a(a-1)=0.
\tag{2.3}
\]

Moreover, in

\[
H=G*\langle q\rangle
\quad\text{and}\quad
K=\ker(H\to G),
\]

the standard left \(G\)-module isomorphism

\[
K_{\mathrm{ab}}\cong\mathbb Z[G],
\qquad
[gqg^{-1}]\longmapsto g,
\tag{2.4}
\]

sends the class of the image of \(W\) to \(D_q\).

#### Proof

Choose \(\Phi\in\operatorname{Aut}(F)\) with \(\Phi(q)=W\). The Fox
chain rule applied to \(\Phi\) and \(\Phi^{-1}\) makes the Fox Jacobian
of \(\Phi\) invertible over \(\mathbb Z[F]\), with the usual
automorphism twist in the inverse. The row belonging to
\(\Phi(q)=W\) is therefore right-unimodular. Applying
\(\eta_*:\mathbb Z[F]\to\mathbb Z[G]\) preserves its Bézout identity.

Fox's fundamental formula is

\[
W-1=\sum_{a\in X\cup\{q\}}
\frac{\partial W}{\partial a}(a-1).
\tag{2.5}
\]

After applying \(\eta\), both \(W-1\) and \(q-1\) vanish, giving (2.3).

Finally, read a word in \(G*\langle q\rangle\) from left to right.
A positive \(q\) contributes its evaluated prefix to \(K_{\rm ab}\);
a negative \(q^{-1}\) contributes minus its evaluated prefix after that
letter. This is exactly the left Fox rule for
\(\partial/\partial q\), proving (2.4). \(\square\)

Right-unimodularity is necessary for primitivity, not sufficient. The
point of Proposition 2.1 is to attach an exact module class to every
candidate before attempting a stable history.

## 3. The smallest parity-relevant split family

Use uppercase letters for inverses:

\[
T=t^{-1},
\qquad
Q=q^{-1},
\qquad
R=xxxTTTT.
\]

For \(1\le k\le6\), let \(A_k\) be the length-\(k\) prefix of \(R\)
and let \(B_k\) be the complementary suffix, so \(R=A_kB_k\). Define

\[
V_k=qA_kQ B_kq.
\tag{3.1}
\]

Every \(V_k\) is cyclically reduced, has three \(q^{\pm1}\)-occurrences
and \(q\)-exponent \(1\), and satisfies

\[
V_k\big|_{q=1}=A_kB_k=R.
\tag{3.2}
\]

An eliminator with \(q\)-exponent \(\pm1\) contains an odd number of
\(q^{\pm1}\)-occurrences. After excluding the one-\(q\) stratum, three
is therefore the smallest possible occurrence count. Equation (3.1)
does not classify all three-\(q\) words; it is the complete seam-split
family obtained by inserting \(q,Q,q\) around two nonempty consecutive
pieces of the fixed reduced spelling of \(R\).

### Theorem 3.1 (exact split-family classification)

\[
\boxed{
V_k\text{ is primitive in }F(x,t,q)
\quad\Longleftrightarrow\quad
k=3.
}
\tag{3.3}
\]

#### Proof

For a cyclic word \(w\), use the Whitehead graph whose vertices are

\[
x,X,t,T,q,Q
\]

and whose cyclic adjacent pair \(ab\) contributes the undirected edge
from \(a^{-1}\) to \(b\). Exact construction gives:

| seam | word | connected? | cut vertices |
|---:|---|---|---|
| \(1,2\) | \(qA_kQB_kq\) | yes | none |
| \(3\) | \(qxxxQTTTTq\) | yes | \(q,Q\) |
| \(4,5,6\) | \(qA_kQB_kq\) | yes | none |

The classical Whitehead cut-vertex lemma says that the Whitehead graph
of a cyclically reduced primitive word of length greater than one has a
cut vertex whenever the graph is connected. Hence \(V_k\) is not
primitive for \(k\ne3\).

For \(k=3\), define two elementary automorphisms:

\[
\begin{aligned}
\alpha(q)&=Rq,
&
\alpha(x)&=x,
&
\alpha(t)&=t,\\
\beta(x)&=qxq^{-1},
&
\beta(q)&=q,
&
\beta(t)&=t.
\end{aligned}
\tag{3.4}
\]

Then free reduction gives

\[
\begin{aligned}
(\beta\alpha)(q)
&=\beta(R)q\\
&=(qxq^{-1})^3t^{-4}q\\
&=qx^3q^{-1}t^{-4}q\\
&=V_3.
\end{aligned}
\tag{3.5}
\]

Thus \(V_3\) is the image of a basis element under an automorphism and
is primitive. \(\square\)

The cut-vertex criterion comes from J. H. C. Whitehead,
“On Certain Sets of Elements in a Free Group,” *Proceedings of the
London Mathematical Society* s2-41 (1936), 48–56,
<https://doi.org/10.1112/plms/s2-41.1.48>.

### Proposition 3.2 (exact Fox row of the family)

After \(q\mapsto1\), in the integral group ring of \(F(x,t)\),

\[
\boxed{
\left(
\frac{\partial V_k}{\partial x},
\frac{\partial V_k}{\partial t},
\frac{\partial V_k}{\partial q}
\right)
=
\left(
\frac{\partial R}{\partial x},
\frac{\partial R}{\partial t},
1-A_k+R
\right).
}
\tag{3.6}
\]

In \(\mathbb Z[G]\), where \(R=1\), the last coordinate is

\[
D_q(V_k)=2-A_k.
\tag{3.7}
\]

#### Proof

The first two coordinates follow either by the Fox chain rule applied to
(3.2), or by differentiating (3.1) and then setting \(q=1\). For the
last coordinate,

\[
\frac{\partial(qA_kq^{-1}B_kq)}{\partial q}
=1-qA_kq^{-1}+qA_kq^{-1}B_k.
\tag{3.8}
\]

Setting \(q=1\) and using \(A_kB_k=R\) gives (3.6); passage to \(G\)
gives (3.7). \(\square\)

For \(k=3\), the augmentation of \(2-x^3\) is \(1\), as required by
primitivity. More importantly, \(2-x^3\) is the exact free-kernel
module class that any proposed asymmetric AC production must carry.

## 4. Coherent use is a self-loop

Put

\[
\phi=\beta\alpha
\tag{4.1}
\]

with \(\alpha,\beta\) from (3.4), and again let
\(\rho(q)=1\). Straightening the primitive word
\(\phi(q)=V_3\) to \(q\) and eliminating it induces the quotient map

\[
p=\rho\phi^{-1}:F(x,t,q)\longrightarrow F(x,t).
\tag{4.2}
\]

### Proposition 4.1 (coherent cancellation)

For every \(U\in F(x,t)\),

\[
p(\phi(U))=U.
\tag{4.3}
\]

Hence applying \(\phi\) coherently to every relator and then removing
the primitive relator \(\phi(q)\) returns the original tuple exactly.

#### Proof

\[
p(\phi(U))
=\rho\phi^{-1}\phi(U)
=\rho(U)
=U.
\qquad\square
\]

This is a statement about coherent ambient transport. It does not apply
to an AC history that creates \(V_3\) in one slot while the surviving
slots are not the corresponding \(\phi\)-images.

## 5. The asymmetric survivor is genuinely non-automorphic

The explicit inverses are

\[
\alpha^{-1}(q)=R^{-1}q,
\qquad
\beta^{-1}(x)=q^{-1}xq,
\tag{5.1}
\]

with the other basis elements fixed. Therefore (4.2) gives

\[
\boxed{
p(x)=RxR^{-1},
\qquad
p(t)=t,
\qquad
p(q)=R^{-1}.
}
\tag{5.2}
\]

Let

\[
\psi_R:F(x,t)\longrightarrow F(x,t),
\qquad
x\longmapsto RxR^{-1},
\quad
t\longmapsto t.
\tag{5.3}
\]

### Proposition 5.1

\(\psi_R\) is not an automorphism.

#### Proof

Its action on abelianization is the identity. If \(\psi_R\) were an
automorphism, Nielsen's rank-two theorem

\[
\ker\bigl(\operatorname{Aut}(F_2)\to GL(2,\mathbb Z)\bigr)
=\operatorname{Inn}(F_2)
\tag{5.4}
\]

would make it conjugation by some \(c\in F(x,t)\).

Because \(\psi_R(t)=t\), the element \(c\) centralizes \(t\), so
\(c=t^m\) for some \(m\in\mathbb Z\). Comparing the two images of \(x\)
then gives

\[
RxR^{-1}=t^mxt^{-m},
\]

so \(t^{-m}R\) centralizes \(x\). Hence

\[
R=t^m x^n
\tag{5.5}
\]

for some \(n\in\mathbb Z\). But the reduced word
\(R=x^3t^{-4}\) is not of that form. This contradiction proves the
claim. \(\square\)

Thus the coherent construction is a self-loop, but asymmetry is not
cosmetic: eliminating \(V_3\) against untransported survivors can apply
a genuine non-automorphic quotient endomorphism.

## 6. Exact boundary and next equation

The proved conclusions are:

1. literal free-kernel multi-\(q\) primitivity gives nothing beyond a
   conjugate of the stabilizer;
2. among the six consecutive seam splits of \(R\), the unique primitive
   word is

   \[
   V_3=qx^3q^{-1}t^{-4}q;
   \]

3. its exact Fox \(q\)-coordinate is \(2-x^3\);
4. coherent ambient use is an exact self-loop;
5. its asymmetric quotient map is not an automorphism of \(F_2\).

The next proof problem is therefore concrete:

> Can classical AC moves on a one-stabilized AK(3) tuple produce
> \(V_3\) as a relator while leaving at least one survivor outside the
> coherent \(\phi\)-orbit?

No such AC history is constructed here, and no invariant excluding all
such histories is proved here. Stable AC for AK(3), and the general
stable Andrews--Curtis conjecture, remain open.

## 7. Independent exact replay

The dependency-free verifier
`tests/stable_ac/test_multi_z_primitive_gate.py` independently checks:

- free reduction and all six specializations \(V_k|_{q=1}=R\);
- connectedness and the exact cut-vertex set of every Whitehead graph;
- both compositions of the displayed automorphism and its inverse;
- all three evaluated Fox derivatives for all six words;
- the quotient values in (5.2);
- coherent cancellation (4.3) on several independent survivor words.
