# Source-slot primitive exchange is a stable self-loop

Date: 2026-07-25

Status: **PROVEN** when the primitive transvection word \(U\) is equal
to the target source relator modulo the other retained sources. The
primitive word \(W=\beta(U)q\) may replace that source slot while the
stabilizing \(q\)-relator survives. After straightening, the surviving
\(q\)-relator becomes \(U^{-1}\), which recovers the deleted source.

For AK(3), this closes the branch in which the five-\(q\) word
\(\beta(RB)q\) replaces the \(B\)-slot rather than the \(q\)-slot.
It does not prove AK(3) stably AC-trivial.

## 1. Setup

Let

\[
\mathcal P
=
\langle X\mid
R_1,\ldots,R_k,S_1,\ldots,S_m
\rangle
\tag{1.1}
\]

be a balanced presentation of the trivial group. Put

\[
F=F(X)*\langle q\rangle
\]

and let

\[
\rho:F\longrightarrow F(X)
\tag{1.2}
\]

fix \(X\) and kill \(q\).

Write

\[
L_0
=
\langle\!\langle
R_1,\ldots,R_{k-1}
\rangle\!\rangle_{F(X)}
\tag{1.3}
\]

and choose \(U\in F(X)\) satisfying

\[
R_k^{-1}U\in L_0.
\tag{1.4}
\]

Thus \(U=R_k\) in \(F(X)/L_0\). In particular,

\[
U\in
L:=
\langle\!\langle
R_1,\ldots,R_k
\rangle\!\rangle_{F(X)}.
\tag{1.5}
\]

Take \(\beta\in\operatorname{Aut}(F)\) with

\[
\beta(q)=q,
\qquad
\rho\beta=\rho,
\tag{1.6}
\]

and define

\[
\alpha_U(q)=Uq,
\qquad
\alpha_U(a)=a\quad(a\in X),
\tag{1.7}
\]

\[
\phi=\beta\alpha_U,
\qquad
W=\phi(q)=\beta(U)q.
\tag{1.8}
\]

## 2. Source-slot exchange theorem

### Theorem 2.1

There is a classical AC sequence

\[
\begin{aligned}
(&R_1,\ldots,R_k,S_1,\ldots,S_m,q)\\
&\sim_{\mathrm{AC1-3}}
(\beta(R_1),\ldots,\beta(R_{k-1}),
W,S_1,\ldots,S_m,q).
\end{aligned}
\tag{2.1}
\]

Straighten the primitive \(W\)-slot by \(\phi^{-1}\) and delete the
resulting generator-relator pair. The endpoint is

\[
\mathcal E
=
(R_1,\ldots,R_{k-1},U^{-1},
p(S_1),\ldots,p(S_m)),
\qquad
p=\rho\phi^{-1}.
\tag{2.2}
\]

It returns classically:

\[
\boxed{
\mathcal E
\sim_{\mathrm{AC1-3}}
(R_1,\ldots,R_k,S_1,\ldots,S_m).
}
\tag{2.3}
\]

Thus manufacture in, and deletion of, the quotient-equal source slot is
a stable self-loop.

#### Proof

First use the surviving \(q\)-relator and the multi-source replacement
lemma to change every \(R_i\)-slot to \(\beta(R_i)\). Equation (1.4)
gives

\[
\beta(R_k)^{-1}\beta(U)
=
\beta(R_k^{-1}U)
\in
\langle\!\langle
\beta(R_1),\ldots,\beta(R_{k-1})
\rangle\!\rangle_F.
\tag{2.4}
\]

Holding the first \(k-1\) transformed sources fixed, replace the
\(\beta(R_k)\)-slot by \(\beta(U)\). Right-multiply that target by the
unchanged \(q\)-relator:

\[
\beta(U)\longmapsto\beta(U)q=W.
\tag{2.5}
\]

This proves the classical manufacture (2.1).

Apply

\[
\phi^{-1}=\alpha_U^{-1}\beta^{-1}.
\]

For \(i<k\),

\[
\phi^{-1}(\beta(R_i))=R_i,
\]

and \(\phi^{-1}(W)=q\). The surviving \(q\)-relator becomes

\[
\phi^{-1}(q)
=\alpha_U^{-1}(q)
=U^{-1}q.
\tag{2.6}
\]

After deleting the straightened \(q\)-slot and setting \(q=1\), this
surviving relator is \(U^{-1}\), while each \(S_j\) becomes \(p(S_j)\).
This proves (2.2). Stable ambient straightening and primitive deletion
are valid because (1.1) is balanced and presents the trivial group.

Now (1.4) gives

\[
U R_k^{-1}
=
R_k(R_k^{-1}U)R_k^{-1}
\in L_0.
\tag{2.7}
\]

Since

\[
(U^{-1})^{-1}R_k^{-1}=UR_k^{-1},
\]

the fixed-\(L_0\) multi-source lemma replaces the \(U^{-1}\)-slot by
\(R_k^{-1}\). One AC2 inversion recovers \(R_k\).

It remains to restore the other survivors. Let

\[
\lambda:F\longrightarrow F(X)/L
\]

kill \(q\). Because \(U\in L\) and \(\rho\beta=\rho\),

\[
\lambda\alpha_U^{-1}=\lambda,
\qquad
\lambda\beta^{-1}=\lambda.
\]

Thus

\[
S_j^{-1}p(S_j)\in L
\tag{2.8}
\]

for every \(j\). After recovering the full retained source tuple, the
multi-source lemma replaces every \(p(S_j)\) by \(S_j\). This proves
(2.3). \(\square\)

## 3. Exact AK(3) target switch

At the rank-three compression root, put

\[
\begin{aligned}
R&=x^3t^{-4},\\
B&=z^{-1}xt,\\
D&=t^{-1}zxz^{-1},
\end{aligned}
\qquad
U=RB.
\tag{3.1}
\]

Here \(k=2\), \(R_1=R\), \(R_2=B\), and

\[
B^{-1}U=B^{-1}RB
\in\langle\!\langle R\rangle\!\rangle.
\tag{3.2}
\]

Use the relative automorphism

\[
\beta(x)=qxq^{-1},
\qquad
\beta(t)=t,
\qquad
\beta(z)=z,
\qquad
\beta(q)=q.
\tag{3.3}
\]

The preceding multi-source certificate first gives

\[
(R,B,D,q)
\sim_{\mathrm{AC1-3}}
(\beta(R),\beta(B),D,q).
\tag{3.4}
\]

### Proposition 3.1 (literal \(B\)-target manufacture)

The next two target moves are

\[
\begin{aligned}
\beta(B)
&\longmapsto
\beta(B)
\bigl(\beta(B)^{-1}\beta(R)\beta(B)\bigr)
=\beta(R)\beta(B)=\beta(U),\\
\beta(U)
&\longmapsto
\beta(U)q=W.
\end{aligned}
\tag{3.5}
\]

Therefore

\[
\boxed{
(R,B,D,q)
\sim_{\mathrm{AC1-3}}
(\beta(R),W,D,q).
}
\tag{3.6}
\]

The first move multiplies the \(B\)-target by a conjugate of the
\(\beta(R)\)-source; the second uses the untouched \(q\)-source.

## 4. Exact quotient return

The word \(W\) is the same five-\(q\) primitive word as in the retained
multi-source theorem:

\[
W
=
qx^3q^{-1}t^{-4}z^{-1}qxq^{-1}tq.
\tag{4.1}
\]

Straightening and deleting the \(W\)-slot in (3.6) gives

\[
(R,D',U^{-1}),
\qquad
D'=t^{-1}zUxU^{-1}z^{-1}.
\tag{4.2}
\]

The deleted \(B\)-source is recovered by the literal identity

\[
\boxed{
U^{-1}R
=(RB)^{-1}R
=B^{-1}.
}
\tag{4.3}
\]

Right-multiply the \(U^{-1}\)-slot by the retained \(R\)-slot and invert
it. After reordering, the tuple is

\[
(R,B,D').
\tag{4.4}
\]

As proved by the exact four-factor certificate,

\[
\begin{aligned}
D^{-1}D'
&=
\bigl((zx^{-1})R(xz^{-1})\bigr)
\bigl((zx^{-1})B(xz^{-1})\bigr)\\
&\qquad
\bigl(zB^{-1}z^{-1}\bigr)
\bigl(zR^{-1}z^{-1}\bigr).
\end{aligned}
\tag{4.5}
\]

The retained \((R,B)\)-subtuple therefore returns \(D'\) to \(D\) by
four source multiplications. This completes an exact self-loop
certificate for the source-slot branch.

## 5. Boundary

The theorem requires

\[
R_k^{-1}U
\in
\langle\!\langle R_1,\ldots,R_{k-1}\rangle\!\rangle.
\]

Equivalently, the relation \(U^{-1}\) left by the surviving stabilizer
recovers the deleted source modulo the other retained sources.

It does not close:

- a replacement \(U\) that changes the joint source normal closure;
- a stabilizing \(q\)-slot modified before straightening so that its
  quotient is not \(U^{-1}\);
- a survivor outside its baseline class modulo the recovered full source
  tuple;
- a primitive word outside the relative-transvection family;
- primitive-pair compression.

Within this source-slot family, deleting the apparent source does not
remove its normal closure: the stabilizer relator carries it through the
primitive quotient. AK(3) and stable AC remain open.

## 6. Independent replay

The dependency-free verifier
`tests/stable_ac/test_source_slot_primitive_exchange.py` checks:

- the exact \(\beta(B)\to\beta(U)\to W\) target moves;
- \(\phi,\phi^{-1}\), and every quotient image;
- the endpoint \((R,D',U^{-1})\);
- the literal recovery \(U^{-1}R=B^{-1}\);
- the four retained-source factors returning \(D'\) to \(D\).

