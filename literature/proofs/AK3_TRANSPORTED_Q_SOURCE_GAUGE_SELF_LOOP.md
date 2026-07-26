# Coherently transported q-source changes are gauges

Date: 2026-07-26

Status: **PROVEN**. Let \(\beta\) fix q and become the identity after q
is killed. If \(V\) is a consequence of q-free retained sources, then
the q-dependent source

\[
Q=\beta(qV)=q\beta(V)
\]

is primitive. At a checkpoint carrying the coherently transported
source slots, deleting \(Q\) gives the ordinary q-deletion endpoint
modulo those sources. Arbitrary later traffic from \(Q\) disappears.

For AK(3), this closes \(Q=q\beta(R)\) and all later \(Q\)-source
traffic. It does not prove AK(3) stably AC-trivial.

## 1. Transported-source gauge theorem

Let

\[
F=F(X)*\langle q\rangle,
\qquad
\rho:F\longrightarrow F(X)
\]

with \(\rho(q)=1\) and \(\rho|_{F(X)}=\operatorname{id}\). Choose
q-free words \(R_1,\ldots,R_k\), put

\[
L=
\langle\!\langle R_1,\ldots,R_k\rangle\!\rangle_{F(X)},
\tag{1.1}
\]

and take \(V\in L\). Suppose

\[
\beta\in\operatorname{Aut}(F),
\qquad
\beta(q)=q,
\qquad
\rho\beta=\rho.
\tag{1.2}
\]

Assume a balanced trivial-group checkpoint has relator tuple

\[
\mathcal C
=
(\beta(R_1),\ldots,\beta(R_k),A_1,\ldots,A_m,q).
\tag{1.3}
\]

Define the right transvection

\[
\delta_V(q)=qV,
\qquad
\delta_V(a)=a\quad(a\in X),
\tag{1.4}
\]

and use the convention

\[
\tau=\beta\delta_V,
\qquad
\tau(w)=\beta(\delta_V(w)).
\tag{1.5}
\]

Then

\[
Q:=\tau(q)=\beta(qV)=q\beta(V).
\tag{1.6}
\]

Because

\[
\beta(V)\in
\langle\!\langle
\beta(R_1),\ldots,\beta(R_k)
\rangle\!\rangle_F,
\]

the multi-source normal-closure lemma manufactures \(Q\) in the q-slot.
The word is primitive, with straightening map

\[
\tau^{-1}=\delta_V^{-1}\beta^{-1},
\qquad
\delta_V^{-1}(q)=qV^{-1}.
\tag{1.7}
\]

After manufacturing \(Q\), keep it unchanged and use it as a source to
make arbitrary changes

\[
\begin{aligned}
\beta(R_i)&\longmapsto\beta(R_i)g_i,\\
A_j&\longmapsto A_jh_j,
\end{aligned}
\qquad
g_i,h_j\in\langle\!\langle Q\rangle\!\rangle_F.
\tag{1.8}
\]

### Theorem 1.1

Straightening and deleting \(Q\) gives an endpoint classically
AC-equivalent to ordinary q-deletion of (1.3).

#### Proof

All preceding changes are classical AC moves, so the current tuple
remains balanced and presents the trivial group. Primitive straightening
and destabilization are therefore legal.

The deletion evaluation is

\[
\sigma
:=
\rho\delta_V^{-1}\beta^{-1}.
\tag{1.9}
\]

It kills \(Q\), so every \(g_i,h_j\) in (1.8) vanishes. The coherent
carrier slots return literally:

\[
\boxed{
\sigma(\beta(R_i)g_i)=R_i.
}
\tag{1.10}
\]

Let

\[
\pi:F(X)\longrightarrow F(X)/L,
\qquad
\lambda=\pi\rho.
\]

Because \(V\in L\),

\[
\lambda\delta_V^{-1}=\lambda.
\tag{1.11}
\]

Equation (1.2) implies \(\rho\beta^{-1}=\rho\), hence

\[
\lambda\beta^{-1}=\lambda.
\tag{1.12}
\]

Combining (1.9)--(1.12),

\[
\boxed{
\pi\sigma=\pi\rho.
}
\tag{1.13}
\]

Thus

\[
\rho(A_j)^{-1}\sigma(A_j)\in L.
\tag{1.14}
\]

Hold the returned \(R_i\)-slots fixed and use the multi-source
normal-closure lemma to replace every \(\sigma(A_j)\) by
\(\rho(A_j)\). This is the ordinary-q deletion endpoint. \(\square\)

## 2. Exact AK(3) source \(q\beta(R)\)

Put

\[
\begin{aligned}
R&=x^3t^{-4},&
B&=z^{-1}xt,\\
D&=t^{-1}zxz^{-1},&
U&=RB,
\end{aligned}
\tag{2.1}
\]

and define

\[
\beta(x)=qxq^{-1},
\qquad
\beta(t)=t,
\qquad
\beta(z)=z,
\qquad
\beta(q)=q.
\tag{2.2}
\]

At the fixed checkpoint,

\[
(\beta(R),W,D,q),
\qquad
W=\beta(U)q.
\tag{2.3}
\]

Take \(V=R\). One target multiplication by the first source changes

\[
q\longmapsto
Q=q\beta(R)=\beta(qR).
\tag{2.4}
\]

Keep \(Q\) fixed, permit arbitrary \(Q\)-normal-closure traffic into
any of the other three slots, and delete \(Q\) first.

For \(\tau=\beta\delta_R\), the deletion map
\(\sigma=\rho\tau^{-1}\) has exact generator images

\[
\boxed{
\begin{aligned}
\sigma(x)&=RxR^{-1},\\
\sigma(t)&=t,\\
\sigma(z)&=z,\\
\sigma(q)&=R^{-1}.
\end{aligned}
}
\tag{2.5}
\]

It follows that

\[
\boxed{
\begin{aligned}
\sigma(\beta(R))&=R,\\
\sigma(W)&=UR^{-1}=RBR^{-1},\\
\sigma(D)&=D_R:=t^{-1}zRxR^{-1}z^{-1}.
\end{aligned}
}
\tag{2.6}
\]

Every traffic multiplier vanishes, so the endpoint is exactly

\[
(R,RBR^{-1},D_R).
\tag{2.7}
\]

## 3. Exact return

Conjugate the middle relator by \(R^{-1}\):

\[
R^{-1}(RBR^{-1})R=B.
\tag{3.1}
\]

For the last relator,

\[
\boxed{
D^{-1}D_R
=
\bigl((zx^{-1})R(xz^{-1})\bigr)
\bigl(zR^{-1}z^{-1}\bigr).
}
\tag{3.2}
\]

Writing the two factors as \(f_1,f_2\), the reverse source-factor order

\[
D_Rf_2^{-1}f_1^{-1}=D
\tag{3.3}
\]

returns \(D_R\) to \(D\). Hence

\[
\boxed{
(R,RBR^{-1},D_R)
\sim_{\mathrm{AC1-3}}
(R,B,D).
}
\tag{3.4}
\]

The q-dependent changed source \(q\beta(R)\), with arbitrary later
traffic from that source into the other slots, gives no new classical
endpoint.

## 4. Boundary

The general theorem requires:

- coherent carrier slots \(\beta(R_i)\) with q-free ancestors \(R_i\);
- \(V\) in their old joint normal closure;
- \(\beta(q)=q\) and \(\rho\beta=\rho\);
- a changed source exactly \(Q=\beta(qV)\), kept unchanged and deleted
  first;
- later target multipliers only from
  \(\langle\!\langle Q\rangle\!\rangle\).

It does not cover an arbitrary q-dependent source word, incoherent
transport, loss of the returned carrier normal closure, a second change
to \(Q\), another traffic source with nontrivial deletion image, or
primitive-pair compression. AK(3) and stable AC remain open.

## 5. Independent replay

The dependency-free verifier
`tests/stable_ac/test_transported_q_source_gauge.py` checks:

- \(\tau,\tau^{-1}\) on every generator in both composition orders;
- the exact deletion map (2.5);
- representative \(Q\)-normal-closure traffic in all three other slots;
- the endpoint (2.6)--(2.7);
- the conjugation (3.1);
- the two retained-R factors and reverse return (3.2)--(3.3).
