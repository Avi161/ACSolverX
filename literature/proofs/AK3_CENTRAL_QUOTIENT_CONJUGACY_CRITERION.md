# Central-quotient conjugacy criterion for the AK(3) torus-knot group

Date: 2026-07-25

Status: **PROVEN**. Weight together with conjugacy in \(C_3*C_4\) exactly
classifies conjugacy in
\(G=\langle x,t\mid x^3=t^4\rangle\). Consequently projected conjugacy to
the braid endpoint is an exact fixed-\(R\) finish criterion for every
weight-\(\pm1\) survivor of the remaining three-cross killer equation.
Failure of this criterion is not an AC obstruction and does not settle
AK(3).

## 1. The central quotient

Put

\[
G=\langle x,t\mid x^3=t^4\rangle
\tag{1.1}
\]

and

\[
c=x^3=t^4.
\tag{1.2}
\]

The element \(c\) is central. It commutes with \(x\) because \(c=x^3\),
and with \(t\) because \(c=t^4\). Hence \(\langle c\rangle\) is normal in
\(G\).

Quotienting by this subgroup gives

\[
\begin{aligned}
\Gamma
&=
G/\langle c\rangle\\
&\cong
\langle \bar x,\bar t
\mid \bar x^3=1,\ \bar t^4=1\rangle\\
&\cong C_3*C_4.
\end{aligned}
\tag{1.3}
\]

Let

\[
\pi:G\longrightarrow\Gamma
\tag{1.4}
\]

be the quotient map. By construction,

\[
\ker\pi=\langle c\rangle.
\tag{1.5}
\]

The torus weight

\[
\operatorname{wt}:G\longrightarrow\mathbb Z,
\qquad
\operatorname{wt}(x)=4,\quad
\operatorname{wt}(t)=3
\tag{1.6}
\]

is well defined because both sides of \(x^3=t^4\) have weight \(12\).
In particular,

\[
\operatorname{wt}(c)=12.
\tag{1.7}
\]

This also proves that \(c\) has infinite order.

## 2. Exact conjugacy lifting

### Theorem 2.1

For any \(U,V\in G\),

\[
\boxed{
U\sim_G V
\iff
\left(
\operatorname{wt}(U)=\operatorname{wt}(V)
\ \text{and}\
\pi(U)\sim_\Gamma\pi(V)
\right),
}
\tag{2.1}
\]

where \(\sim\) denotes conjugacy.

### Proof

The forward implication follows because homomorphisms preserve conjugacy
and weight is constant on conjugacy classes.

Conversely, suppose the two conditions on the right hold. Choose
\(\bar g\in\Gamma\) with

\[
\pi(U)=\bar g\pi(V)\bar g^{-1},
\tag{2.2}
\]

and lift \(\bar g\) to \(g\in G\). Then

\[
U(gVg^{-1})^{-1}\in\ker\pi.
\tag{2.3}
\]

By (1.5), there is \(k\in\mathbb Z\) such that

\[
U=c^k gVg^{-1}.
\tag{2.4}
\]

Apply weight:

\[
\operatorname{wt}(U)
=
12k+\operatorname{wt}(V).
\tag{2.5}
\]

The assumed weight equality forces \(k=0\). Equation (2.4) now says that
\(U\) and \(V\) are conjugate in \(G\). \(\square\)

The theorem also gives a signed version. For \(s\in\{1,-1\}\),

\[
U\sim_G V^s
\iff
\operatorname{wt}(U)=s\operatorname{wt}(V)
\ \text{and}\
\pi(U)\sim_\Gamma\pi(V^s).
\tag{2.6}
\]

## 3. The quotient test is decidable by cyclic normal form

Every element of

\[
\Gamma=C_3*C_4
\tag{3.1}
\]

has a unique reduced alternating normal form

\[
s_1s_2\cdots s_r,
\tag{3.2}
\]

where each \(x\)-syllable is \(\bar x\) or \(\bar x^2\), each
\(t\)-syllable is \(\bar t,\bar t^2,\) or \(\bar t^3\), and adjacent
syllables lie in different factors.

Cyclically reduce (3.2) by combining its first and last syllables whenever
they lie in the same cyclic factor. For cyclically reduced length at least
two, the conjugacy theorem for free products says that two elements are
conjugate exactly when one normal form is a cyclic rotation of the other.
At length one, conjugacy reduces to conjugacy inside a factor; the factors
are abelian, so the syllables must be equal. The identity is its own class.

Thus the following finite key decides conjugacy in \(\Gamma\):

1. reduce the alternating normal form;
2. cyclically reduce its ends; and
3. take the least cyclic rotation.

The amalgam normal form

\[
c^k s_1\cdots s_r
\tag{3.3}
\]

already used in the AK(3) recovery proofs computes both parts of
Theorem 2.1: \(s_1\cdots s_r\) is the projected word, while

\[
12k+\sum_i\operatorname{wt}(s_i)
\tag{3.4}
\]

is its weight.

## 4. Exact finish criterion for a three-cross survivor

Put

\[
R=x^3t^{-4},
\qquad
p=xt,
\qquad
S=pxp^{-1}t^{-1},
\qquad
D_p=t^{-1}St=t^{-1}pxp^{-1}.
\tag{4.1}
\]

Since conjugation has zero effect on weight,

\[
\operatorname{wt}(D_p)=1.
\tag{4.2}
\]

Let \(C\in F(x,t)\) be an actual survivor from one of the six feasible
rows of the remaining prefix-\(DB\) three-cross killer equation. The
target-word classification proves

\[
\operatorname{wt}(C)=s
\qquad
\text{for some }s\in\{1,-1\}.
\tag{4.3}
\]

If

\[
\pi(C)\sim_\Gamma\pi(D_p^s),
\tag{4.4}
\]

then Theorem 2.1 gives

\[
[C]_G
\sim_G
[D_p^s]_G.
\tag{4.5}
\]

Choose a literal free-group representative \(V\) of the conjugate in
(4.5). Then

\[
C^{-1}V\in\langle\!\langle R\rangle\!\rangle.
\tag{4.6}
\]

The fixed-relator normal-closure lemma, AC3, and AC1 give

\[
\boxed{
(R,C)
\sim_{\mathrm{AC1-3}}
(R,D_p)
\sim_{\mathrm{AC3}}
(R,S)
=
\operatorname{AK}(3).
}
\tag{4.7}
\]

Condition (4.4) is therefore an exact, decidable finish test for the
direct fixed-\(R\) conjugacy route. It replaces an equality search in the
infinite central extension \(G\) by cyclic conjugacy in the virtually free
group \(C_3*C_4\) plus the already-known weight.

## 5. What failure means

If (4.4) fails, then \(C\) is not conjugate to \(D_p^s\) in \(G\). This
rules out only the direct fixed-\(R\) conjugacy finish (4.7).

It does **not** prove that \((R,C)\) and \((R,D_p)\) are AC-inequivalent:
an AC path may change both relators, and projected conjugacy of the second
relator is not an AC invariant. It is likewise not a stable-AC obstruction
and cannot certify a counterexample.

The theorem does not prove that every prefix-\(DB\) survivor satisfies
(4.4). Establishing or refuting that universal statement is the next word
equation.

AK(3) remains open.
