# Retained-source traffic into the primitive slot is a stable self-loop

Date: 2026-07-25

Status: **PROVEN**. Let \(W=\phi(q)\) be a primitive relator and let
\(\phi(R_1),\ldots,\phi(R_k)\) be retained source slots. Multiplying any
coherently transported consequence \(\phi(V)\), with

\[
V\in\langle\!\langle R_1,\ldots,R_k\rangle\!\rangle_{F(X)},
\]

into the \(W\)-slot produces another primitive relator

\[
W_V=\phi(qV).
\]

Its quotient differs from the original primitive quotient only by
consequences of the retained sources, so it returns classically.

For AK(3), this closes the first primitive-target multiplication
\(W\mapsto W\beta(R)\), which produces a seven-\(q\) primitive word.

## 1. General theorem

Let

\[
\mathcal P
=
\langle X\mid
R_1,\ldots,R_k,S_1,\ldots,S_m
\rangle
\tag{1.1}
\]

be a balanced presentation of the trivial group, and let

\[
F=F(X)*\langle q\rangle.
\]

Suppose \(\phi\in\operatorname{Aut}(F)\), put

\[
W=\phi(q),
\tag{1.2}
\]

and assume the checkpoint

\[
\mathcal C
=
(\phi(R_1),\ldots,\phi(R_k),A_1,\ldots,A_m,W)
\tag{1.3}
\]

is a balanced presentation of the trivial group. This holds, in
particular, when \(\mathcal C\) is reached from a stabilization of
\(\mathcal P\) by stable AC moves. Its retained slots are

\[
\phi(R_1),\ldots,\phi(R_k)
\tag{1.4}
\]

together with arbitrary other survivor slots \(A_1,\ldots,A_m\) and the
primitive \(W\)-slot.

Let

\[
L
=
\langle\!\langle
R_1,\ldots,R_k
\rangle\!\rangle_{F(X)}
\tag{1.5}
\]

and choose \(V\in L\). Define the right transvection

\[
\delta_V(q)=qV,
\qquad
\delta_V(a)=a\quad(a\in X).
\tag{1.6}
\]

### Theorem 1.1 (primitive-slot retained traffic)

There is a classical AC sequence, using the retained slots (1.4) as
sources, which changes

\[
W\longmapsto
W_V:=W\phi(V)=\phi(qV).
\tag{1.7}
\]

The word \(W_V\) is primitive. Put

\[
\chi=\phi\delta_V,
\qquad
\theta=\rho\phi^{-1},
\qquad
\theta_V=\rho\chi^{-1}
=\rho\delta_V^{-1}\phi^{-1},
\tag{1.8}
\]

where \(\rho(q)=1\). Primitive deletion of \(W_V=\chi(q)\) produces

\[
\mathcal E_V
=
(R_1,\ldots,R_k,
\theta_V(A_1),\ldots,\theta_V(A_m)).
\tag{1.9}
\]

If

\[
\mathcal E
=
(R_1,\ldots,R_k,
\theta(A_1),\ldots,\theta(A_m))
\tag{1.10}
\]

is the original \(W\)-quotient, then

\[
\boxed{
\mathcal E_V
\sim_{\mathrm{AC1-3}}
\mathcal E.
}
\tag{1.11}
\]

#### Proof

Since \(V\in L\),

\[
\phi(V)
\in
\langle\!\langle
\phi(R_1),\ldots,\phi(R_k)
\rangle\!\rangle_F.
\]

The multi-source normal-closure lemma right-multiplies the \(W\)-target
by a finite product of conjugates of the retained source relators and
changes it exactly to \(W\phi(V)\). Equation (1.7) follows because
\(\phi\) is a homomorphism.

The map \(\delta_V\) is an automorphism: its inverse fixes \(X\) and
sends

\[
q\longmapsto qV^{-1}.
\]

Thus

\[
W_V=\phi(\delta_V(q))=(\phi\delta_V)(q)=\chi(q)
\]

is primitive.

Straightening by
\(\chi^{-1}=\delta_V^{-1}\phi^{-1}\) returns every retained source
literally:

\[
\chi^{-1}(\phi(R_i))
=\delta_V^{-1}(R_i)
=R_i.
\tag{1.12}
\]

Stable primitive deletion is valid by the balanced trivial-group
hypothesis, which proves (1.9).

Let

\[
\lambda:F\longrightarrow F(X)/L
\]

kill \(q\). Because \(V\in L\),

\[
\lambda\delta_V^{-1}=\lambda.
\tag{1.13}
\]

Consequently, for every survivor \(A_j\),

\[
\theta_V(A_j)
=\theta(A_j)
\pmod L.
\tag{1.14}
\]

Hold the returned \(R_i\)-slots fixed and apply the multi-source
normal-closure lemma to the other slots one at a time. This proves
(1.11). \(\square\)

The theorem has no bound on the length of \(V\), its normal-closure
factorization, or the conjugators used in the target multiplications.

## 2. Seven-\(q\) AK(3) target

Use the source-slot checkpoint

\[
(\beta(R),W,D,q),
\tag{2.1}
\]

where

\[
\begin{aligned}
R&=x^3t^{-4},\\
B&=z^{-1}xt,\\
D&=t^{-1}zxz^{-1},\\
U&=RB,\\
\alpha_U(q)&=Uq,\\
\beta(x)&=qxq^{-1},\\
\phi&=\beta\alpha_U,\\
W&=\phi(q)=\beta(U)q.
\end{aligned}
\tag{2.2}
\]

Take \(V=R\). Since

\[
\phi(R)=\beta(R),
\]

one AC1 target multiplication gives

\[
\boxed{
W_R
=
W\beta(R)
=
\phi(qR).
}
\tag{2.3}
\]

In letters,

\[
W_R
=
qxxxQTTTTZqxQtq\,qxxxQTTTT.
\tag{2.4}
\]

There is no free or cyclic cancellation. The word has
\(q\)-exponent \(1\), contains four positive and three negative
\(q\)-letters, and therefore has exactly seven
\(q^{\pm1}\)-occurrences. It is primitive by Theorem 1.1.

## 3. Exact new quotient

Put

\[
\delta_R(q)=qR,
\qquad
\chi=\phi\delta_R.
\]

Then

\[
\chi^{-1}=\delta_R^{-1}\phi^{-1},
\qquad
\delta_R^{-1}(q)=qR^{-1}.
\tag{3.1}
\]

Write

\[
Y=UxU^{-1}.
\tag{3.2}
\]

The new quotient \(\theta_R=\rho\chi^{-1}\) satisfies

\[
\boxed{
\begin{aligned}
\theta_R(\beta(R))&=R,\\
\theta_R(W_R)&=1,\\
\theta_R(q)&=U^{-1}R^{-1},\\
\theta_R(x)&=RYR^{-1},\\
\theta_R(t)&=t,\\
\theta_R(z)&=z.
\end{aligned}
}
\tag{3.3}
\]

Therefore deletion produces

\[
(R,D_R',U^{-1}R^{-1}),
\qquad
D_R'=t^{-1}zRYR^{-1}z^{-1}.
\tag{3.4}
\]

The missing \(B\)-source is recovered literally:

\[
\boxed{
(U^{-1}R^{-1})R^2
=U^{-1}R
=B^{-1}.
}
\tag{3.5}
\]

Two right multiplications by the retained \(R\)-slot followed by
inversion recover \(B\).

The new \(D\)-survivor differs from the old

\[
D'=t^{-1}zYz^{-1}
\tag{3.6}
\]

by two conjugates of \(R^{\pm1}\):

\[
\boxed{
(D')^{-1}D_R'
=
\bigl((zY^{-1})R(Yz^{-1})\bigr)
\bigl(zR^{-1}z^{-1}\bigr).
}
\tag{3.7}
\]

Thus the retained \(R\)-slot changes \(D_R'\) back to \(D'\), and the
source-slot theorem returns

\[
(R,B,D')
\sim_{\mathrm{AC1-3}}
(R,B,D).
\tag{3.8}
\]

This is an exact stable self-loop despite the AC1 move targeting the
primitive slot.

## 4. Boundary

The theorem closes target multiplications of the form

\[
W\longmapsto W\phi(V),
\qquad
V\in L\subset F(X).
\]

It includes arbitrary finite products of conjugates whose pullback
under \(\phi^{-1}\) is a \(q\)-free normal-closure factorization over
the retained \(R_i\).

It does not close:

- a multiplier whose pullback under \(\phi^{-1}\) contains \(q\);
- a \(q\)-free pullback outside the retained joint normal closure;
- a primitive target not expressible as \(\phi(qV)\);
- a changed retained source subtuple;
- primitive-pair compression.

Within this retained-traffic family, AC1 into the primitive slot is not
an escape. AK(3) and stable AC remain open.

## 5. Independent replay

The dependency-free verifier
`tests/stable_ac/test_primitive_slot_retained_traffic.py` checks:

- \(W_R=W\beta(R)=\phi(qR)\);
- the exact seven-\(q\) occurrence and exponent counts;
- both compositions of \(\chi,\chi^{-1}\);
- every quotient image in (3.3);
- the recovery identity (3.5);
- the two-factor difference (3.7).
