# Arbitrary z-free q-source traffic is a stable self-loop

Date: 2026-07-25

Status: **PROVEN** for arbitrary finite target traffic at the fixed
AK(3) source-slot checkpoint whose total multiplier lies in

\[
\langle\!\langle q\rangle\!\rangle_{F(x,t,q)}.
\]

Every target

\[
Wv,
\qquad
v\in\langle\!\langle q\rangle\!\rangle_{F(x,t,q)},
\]

contains \(z^{-1}\) exactly once and is therefore primitive. Its
unique-z deletion, followed by deletion of the unchanged q-relator,
has a double quotient independent of the length, signs, conjugators, and
factorization of \(v\). That quotient returns to the standard rank-two
AK(3) presentation by two retained-\(R\) source factors.

This includes the first literal \(x\)-conjugator branches, arbitrary
products of z-free conjugates of \(q^{\pm1}\), and unbounded
q-dependent z-free traffic. It does not include multipliers containing
\(z^{\pm1}\), and it does not prove AK(3) stably AC-trivial.

## 1. Fixed checkpoint

Put

\[
\begin{aligned}
R&=x^3t^{-4},\\
p&=xt,\\
B&=z^{-1}p,\\
D&=t^{-1}zxz^{-1},\\
U&=RB.
\end{aligned}
\tag{1.1}
\]

Let

\[
\beta(x)=qxq^{-1},
\qquad
\beta(t)=t,
\qquad
\beta(z)=z,
\qquad
\beta(q)=q,
\tag{1.2}
\]

and put

\[
W=\beta(U)q.
\tag{1.3}
\]

The source-slot exchange theorem gives the stable AC checkpoint

\[
(R,B,D,q)
\sim_{\mathrm{AC1-3}}
(\beta(R),W,D,q).
\tag{1.4}
\]

It is a balanced presentation of the trivial group.

Since

\[
U=Rz^{-1}p,
\]

the primitive word has the exact factorization

\[
\boxed{
W
=
\beta(R)z^{-1}\beta(p)q.
}
\tag{1.5}
\]

## 2. Arbitrary z-free q-normal-closure traffic

Choose a freely reduced

\[
v\in
\langle\!\langle q\rangle\!\rangle_{F(x,t,q)}.
\tag{2.1}
\]

Equivalently, \(v\) is any z-free word whose image under \(q\mapsto1\)
is trivial. The single-source normal-closure replacement lemma, applied
with the unchanged q-slot as source, changes the target to

\[
T_v
=
Wv.
\tag{2.2}
\]

Define

\[
A=\beta(R)
\tag{2.3}
\]

and

\[
C_v
=
\beta(p)qv.
\tag{2.4}
\]

Then

\[
\boxed{
T_v
=
A z^{-1}C_v.
}
\tag{2.5}
\]

Both \(A\) and \(C_v\) lie in \(F(x,t,q)\). Free reduction
cannot remove the displayed \(z^{-1}\), because neither adjacent factor
contains a z-letter. Thus (2.5) has exactly one
\(z^{\pm1}\)-occurrence.

### Theorem 2.1 (z-free q-traffic closure)

For every
\(v\in\langle\!\langle q\rangle\!\rangle_{F(x,t,q)}\), the target
\(T_v\) is primitive. Straighten and delete it, then delete the
surviving q-relator. The endpoint is

\[
\boxed{
(R,E_R),
\qquad
E_R=t^{-1}(pR)x(pR)^{-1}.
}
\tag{2.6}
\]

It is independent of \(v\).

#### Proof

Define an endomorphism of \(F(x,t,z,q)\) by

\[
\begin{aligned}
\gamma_v(z)
&=
A z^{-1}C_v,\\
\gamma_v(x)&=x,\\
\gamma_v(t)&=t,\\
\gamma_v(q)&=q.
\end{aligned}
\tag{2.7}
\]

Because \(A,C_v\) contain no z-letter, the inverse is

\[
\begin{aligned}
\gamma_v^{-1}(z)
&=
C_vz^{-1}A,\\
\gamma_v^{-1}(x)&=x,\\
\gamma_v^{-1}(t)&=t,\\
\gamma_v^{-1}(q)&=q.
\end{aligned}
\tag{2.8}
\]

Indeed,

\[
\begin{aligned}
\gamma_v
\bigl(C_vz^{-1}A\bigr)
&=
C_v
\bigl(Az^{-1}C_v\bigr)^{-1}
A\\
&=z,
\end{aligned}
\]

and the reverse composition is identical with \(A\) and \(C\)
interchanged. Therefore \(\gamma_v\) is an automorphism and

\[
T_v
=
\gamma_v(z)
\]

is primitive.

Straighten the full checkpoint by
\(\gamma_v^{-1}\) and delete the z-generator with its
relator. Stable ambient straightening and primitive deletion are valid
because (1.4) is balanced and presents the trivial group.

The q-relator is unchanged:

\[
\gamma_v^{-1}(q)=q.
\tag{2.9}
\]

Delete this second generator-relator pair. Let

\[
\rho:F(x,t,z,q)\longrightarrow F(x,t)
\tag{2.10}
\]

kill \(z\) and \(q\). The double quotient is

\[
\kappa_v
=
\rho\gamma_v^{-1}.
\tag{2.11}
\]

It fixes \(x,t\), kills \(q\), and sends

\[
\begin{aligned}
z
&\longmapsto
\rho(C_v)\rho(A)\\
&=
p\,\rho(v)R\\
&=
pR.
\end{aligned}
\tag{2.12}
\]

Here \(\rho\beta\) is the identity on \(F(x,t,z)\), and
\(\rho(v)=1\) by (2.1). Thus no part of the finite q-source history
survives.

It follows that

\[
\kappa_v(\beta(R))=R
\tag{2.13}
\]

and

\[
\kappa_v(D)
=
t^{-1}(pR)x(pR)^{-1}
=E_R.
\tag{2.14}
\]

This proves (2.6). \(\square\)

## 3. Exact return to rank-two AK(3)

Deleting the original primitive

\[
B=z^{-1}p
\]

sends \(z\mapsto p\) and gives the standard rank-two endpoint

\[
(R,E_0),
\qquad
E_0=t^{-1}pxp^{-1}.
\tag{3.1}
\]

The difference between the new and standard second relators is

\[
\boxed{
E_0^{-1}E_R
=
\bigl((px^{-1})R(xp^{-1})\bigr)
\bigl(pR^{-1}p^{-1}\bigr).
}
\tag{3.2}
\]

Both factors are conjugates of \(R^{\pm1}\). Holding the R-slot fixed,
the single-source normal-closure lemma returns \(E_R\) to \(E_0\).
Consequently every branch in Theorem 2.1 is a stable self-loop.

For reference,

\[
E_0=t^{-1}xtxt^{-1}x^{-1},
\tag{3.3}
\]

the standard rank-two AK(3) second relator used throughout the project.

## 4. Conjugates, products, and arbitrary q-dependence

Taking

\[
v=xq^\epsilon x^{-1}
\]

gives the first uncovered literal-basis conjugator targets from Result
39:

\[
Wxqx^{-1}
\qquad\text{and}\qquad
Wxq^{-1}x^{-1}.
\tag{4.1}
\]

They are covered without simplifying their pullbacks under the earlier
automorphism \(\phi\). More generally, \(v\) may be any finite product

\[
v=\prod_{j=1}^N c_jq^{\epsilon_j}c_j^{-1},
\qquad
c_j\in F(x,t,q),
\qquad
\epsilon_j\in\{+1,-1\}.
\tag{4.2}
\]

The theorem depends only on the resulting membership
\(v\in\langle\!\langle q\rangle\!\rangle\), not on this factorization.
There is no bound on \(N\), word length, or q-occurrence count.

## 5. Boundary

The theorem closes arbitrary finite target traffic

\[
W\longmapsto Wv
\qquad
\left(
v\in
\langle\!\langle q\rangle\!\rangle_{F(x,t,q)}
\right)
\tag{5.1}
\]

at the fixed checkpoint (1.4). It does not close:

- a final multiplier containing \(z^{\pm1}\);
- a z-free multiplier whose image after \(q\mapsto1\) is nontrivial;
- a changed spelling of the q-source;
- a different pre-target primitive checkpoint;
- primitive-pair compression.

The literal conjugator \(c=z\) is the first basis conjugator outside the
theorem. This is a scope boundary, not a non-primitivity claim. AK(3)
and stable AC remain open.

## 6. Independent replay

The dependency-free verifier
`tests/stable_ac/test_z_free_q_traffic.py` checks:

- both compositions of every stored \(\gamma_v\);
- finite products using both source orientations and q-dependent
  conjugators;
- the literal \(c=x\) targets;
- the unique-z occurrence;
- the exact multiplier-independent quotient (2.12)--(2.14);
- the two-factor return (3.2).
