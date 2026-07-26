# AK(3) signed-HNN Fox master-lemma design

Date: 2026-07-25

## Objective

Factor the abelianized free-kernel equation for every signed three-cross
history and identify the exact HNN incidence operator left after the two
bridge variables are quotiented out.

## Symbolic factorization

For

\[
D_1=D\,uB^\epsilon u^{-1},\qquad
B_1=B\,vD_1^\eta v^{-1},\qquad
D_2=D_1\,wB_1^\theta w^{-1},
\]

derive the kernel recurrence in
\(N_{\mathrm{ab}}\rtimes G\), with
\(N_{\mathrm{ab}}\cong\mathbb Z[G]\). For every sign triple, prove

\[
\Xi=A_0+A_U\mathbf u+A_V\mathbf v+A_W\mathbf w
\]

with

\[
\begin{aligned}
A_0&=(1+mL)F_\epsilon+M_\theta\mathbf j,\\
A_U&=(1+mL)(d-K),\\
A_V&=-mL(K-1)\beta^{-1},\\
A_W&=K-1,
\end{aligned}
\qquad
m=\eta\theta.
\]

The \(\mathbf v,\mathbf w\) coefficients generate the augmentation
right ideal of

\[
P=\langle K,LKL^{-1}\rangle.
\]

## Signed HNN theorem

Assume \(J=\langle K,L\rangle\cong F(K,L)\). In the quotient
\(\mathbb Z[P\backslash G]\), the remaining operator is

\[
\mathcal B_m(z)=\pi_P((1+mL)z).
\]

After quotienting the domain by \((K-1)\mathbb Z[G]\), this is:

- unsigned edge incidence on the HNN forest when \(m=+1\);
- oriented edge incidence when \(m=-1\).

Both incidence maps are injective on finite-support edge chains, so both
operators have exact kernel \((K-1)\mathbb Z[G]\). Their image criteria
are respectively zero bipartite signed sum and zero ordinary component
sum.

## Scope

- Unbounded symbolic theorem for all eight sign triples.
- No word-radius or AC graph search.
- Does not supply evaluated candidates in the other rows.
- Does not make Result 30's later \(QJ\) double-coset obstruction
  sign-uniform.
- AK(3) and the general conjectures remain open.
