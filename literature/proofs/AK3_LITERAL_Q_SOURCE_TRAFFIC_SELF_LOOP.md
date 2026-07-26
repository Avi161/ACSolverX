# Literal surviving-q traffic into the primitive slot is a stable self-loop

Date: 2026-07-25

Status: **PROVEN** when the pullback \(U\) is primitive in the
unstabilized free group. At a balanced trivial-group checkpoint with

\[
W=\phi(q),
\qquad
\phi^{-1}(q)=U^{-1}q,
\]

both AC1 targets

\[
Wq
\quad\text{and}\quad
Wq^{-1}
\]

are primitive. Deleting either one leaves \(U^{-1}\) or \(U\) in the
surviving \(q\)-slot. That source absorbs every change in the other
survivors, so both branches return to the original \(W\)-deletion
endpoint.

For AK(3), \(U=RB\) is primitive because it contains \(z^{-1}\) exactly
once. Thus both orientations of the first literal q-source
multiplication into the five-q primitive slot are stable self-loops.
This does not prove AK(3) stably AC-trivial.

## 1. Abstract two-sign theorem

Let

\[
F_0=F(X),
\qquad
F=F_0*\langle q\rangle,
\]

and let

\[
\rho:F\longrightarrow F_0
\tag{1.1}
\]

fix \(F_0\) and kill \(q\). Choose a primitive element \(U\in F_0\).
Extend it to a basis

\[
(U,c_2,\ldots,c_n)
\tag{1.2}
\]

of \(F_0\).

Suppose \(\phi\in\operatorname{Aut}(F)\) satisfies

\[
W=\phi(q),
\qquad
\phi^{-1}(q)=U^{-1}q.
\tag{1.3}
\]

Assume the checkpoint

\[
\mathcal C=(A_1,\ldots,A_m,W,q)
\tag{1.4}
\]

is a balanced presentation of the trivial group. This holds, in
particular, when \(\mathcal C\) is reached from a stabilization of a
balanced trivial-group presentation by stable AC moves.

Put

\[
p=\rho\phi^{-1}.
\tag{1.5}
\]

Straightening and deleting the \(W\)-slot gives the old endpoint

\[
\mathcal E
=
(p(A_1),\ldots,p(A_m),U^{-1}).
\tag{1.6}
\]

### Theorem 1.1 (literal-q source traffic)

For each \(\epsilon\in\{+1,-1\}\), one AC1 target multiplication gives

\[
\mathcal C_\epsilon
=
(A_1,\ldots,A_m,Wq^\epsilon,q).
\tag{1.7}
\]

For \(\epsilon=-1\), invert the q-source by AC2 before the
multiplication and restore it by AC2 afterward.

The target \(Wq^\epsilon\) is primitive. Straighten it, delete its
generator-relator pair, and call the endpoint
\(\mathcal E_\epsilon\). Then

\[
\boxed{
\mathcal E_\epsilon
\sim_{\mathrm{AC1-3}}
\mathcal E.
}
\tag{1.8}
\]

Consequently, whenever the old endpoint \(\mathcal E\) has a stable or
classical return certificate, the same certificate closes both literal
q-source branches.

#### Proof: the positive orientation

Define an endomorphism on the basis

\[
(U,c_2,\ldots,c_n,q)
\]

by

\[
\begin{aligned}
\delta_+(q)&=qU^{-1}q,\\
\delta_+(U)&=q,\\
\delta_+(c_i)&=c_i.
\end{aligned}
\tag{1.9}
\]

It is an automorphism. An explicit inverse is

\[
\begin{aligned}
\delta_+^{-1}(q)&=U,\\
\delta_+^{-1}(U)&=Uq^{-1}U,\\
\delta_+^{-1}(c_i)&=c_i.
\end{aligned}
\tag{1.10}
\]

Indeed,

\[
\delta_+(Uq^{-1}U)
=
q(qU^{-1}q)^{-1}q
=U,
\]

and the other composition identities are immediate.

Equation (1.3) gives

\[
\begin{aligned}
\phi^{-1}(Wq)
&=q\,\phi^{-1}(q)\\
&=qU^{-1}q\\
&=\delta_+(q).
\end{aligned}
\tag{1.11}
\]

Thus

\[
Wq=(\phi\delta_+)(q)
\tag{1.12}
\]

is primitive. Put

\[
p_+=\rho\delta_+^{-1}\phi^{-1}.
\tag{1.13}
\]

After straightening by
\((\phi\delta_+)^{-1}\) and deleting the new primitive slot, the
surviving literal \(q\)-relator becomes

\[
\begin{aligned}
p_+(q)
&=\rho\delta_+^{-1}(U^{-1}q)\\
&=\rho\bigl((Uq^{-1}U)^{-1}U\bigr)\\
&=\rho(U^{-1}q)\\
&=U^{-1}.
\end{aligned}
\tag{1.14}
\]

#### Proof: the negative orientation

Let \(\delta_-\) swap \(U\) and \(q\) and fix the complementary basis:

\[
\delta_-(q)=U,
\qquad
\delta_-(U)=q,
\qquad
\delta_-(c_i)=c_i.
\tag{1.15}
\]

It is an involutive automorphism. Again by (1.3),

\[
\begin{aligned}
\phi^{-1}(Wq^{-1})
&=q\,\phi^{-1}(q)^{-1}\\
&=q(U^{-1}q)^{-1}\\
&=q q^{-1}U\\
&=U\\
&=\delta_-(q).
\end{aligned}
\tag{1.16}
\]

Hence

\[
Wq^{-1}=(\phi\delta_-)(q)
\tag{1.17}
\]

is primitive. Put

\[
p_-=\rho\delta_-\phi^{-1}.
\tag{1.18}
\]

The surviving \(q\)-relator becomes

\[
\begin{aligned}
p_-(q)
&=\rho\delta_-(U^{-1}q)\\
&=\rho(q^{-1}U)\\
&=U.
\end{aligned}
\tag{1.19}
\]

#### Proof: both endpoints return

Let

\[
\pi:F_0\longrightarrow
F_0/\langle\!\langle U\rangle\!\rangle
\]

be the quotient map and put

\[
\lambda=\pi\rho.
\tag{1.20}
\]

The map \(\lambda\) kills both \(U\) and \(q\). Inspection on the basis
\((U,c_2,\ldots,c_n,q)\) gives

\[
\lambda\delta_+^{-1}=\lambda,
\qquad
\lambda\delta_-=\lambda.
\tag{1.21}
\]

Therefore, for every \(A_i\),

\[
\pi(p_\epsilon(A_i))
=
\pi(p(A_i)).
\tag{1.22}
\]

The positive endpoint contains the literal source \(U^{-1}\) by
(1.14). The negative endpoint contains \(U\) by (1.19), which one AC2
move inverts. Hold that source fixed and apply the single-source
normal-closure replacement lemma to the other slots one at a time.
Equation (1.22) changes every \(p_\epsilon(A_i)\) exactly to
\(p(A_i)\), proving (1.8).

Stable ambient straightening and primitive deletion are valid because
the checkpoint (1.4) is balanced and presents the trivial group.
\(\square\)

## 2. The AK(3) source-slot checkpoint

Put

\[
\begin{aligned}
R&=x^3t^{-4},\\
p_0&=xt,\\
B&=z^{-1}p_0,\\
D&=t^{-1}zxz^{-1},\\
U&=RB.
\end{aligned}
\tag{2.1}
\]

The element \(U\) is primitive in \(F(x,t,z)\). Indeed, define

\[
\nu(z)=Rz^{-1}p_0,
\qquad
\nu(x)=x,
\qquad
\nu(t)=t.
\tag{2.2}
\]

Its inverse is

\[
\nu^{-1}(z)=p_0z^{-1}R,
\qquad
\nu^{-1}(x)=x,
\qquad
\nu^{-1}(t)=t.
\tag{2.3}
\]

Thus \(\nu(z)=U\). This is the automorphism form of the
unique-\(z^{-1}\)-occurrence criterion.

Let

\[
\begin{aligned}
\alpha_U(q)&=Uq,
&
\alpha_U(x)&=x,
&
\alpha_U(t)&=t,
&
\alpha_U(z)&=z,\\
\beta(x)&=qxq^{-1},
&
\beta(t)&=t,
&
\beta(z)&=z,
&
\beta(q)&=q,
\end{aligned}
\tag{2.4}
\]

and put

\[
\phi=\beta\alpha_U,
\qquad
W=\phi(q)=\beta(U)q.
\tag{2.5}
\]

Then

\[
\phi^{-1}(q)=U^{-1}q.
\tag{2.6}
\]

The source-slot exchange certificate gives the balanced trivial-group
checkpoint

\[
(R,B,D,q)
\sim_{\mathrm{AC1-3}}
(\beta(R),W,D,q).
\tag{2.7}
\]

Theorem 1.1 applies to both

\[
Wq
\qquad\text{and}\qquad
Wq^{-1}.
\tag{2.8}
\]

In reduced letters,

\[
\begin{aligned}
Wq
&=
qxxxq^{-1}t^{-4}z^{-1}qxq^{-1}tqq,\\
Wq^{-1}
&=
qxxxq^{-1}t^{-4}z^{-1}qxq^{-1}t.
\end{aligned}
\tag{2.9}
\]

Their pullbacks are respectively

\[
qU^{-1}q
=
qt^{-1}x^{-1}zt^4x^{-3}q
\tag{2.10}
\]

and \(U\). The first has a strict Whitehead descent to one letter, but
the basis automorphism (1.9) proves primitivity without enumeration.

## 3. Exact positive quotient

For an exact comparison with the preceding source-slot endpoint, put

\[
Y=UxU^{-1},
\qquad
h=R^{-1}U^{-1}R.
\tag{3.1}
\]

In the original basis, the positive automorphism and its inverse include

\[
\begin{aligned}
\delta_+(z)&=p_0q^{-1}R,\\
\delta_+^{-1}(z)&=p_0U^{-1}qU^{-1}R.
\end{aligned}
\tag{3.2}
\]

The quotient

\[
\theta_+
=
\rho\delta_+^{-1}\phi^{-1}
\tag{3.3}
\]

satisfies

\[
\boxed{
\begin{aligned}
\theta_+(\beta(R))&=R,\\
\theta_+(Wq)&=1,\\
\theta_+(q)&=U^{-1},\\
\theta_+(x)&=Y,\\
\theta_+(t)&=t,\\
\theta_+(z)&=zh.
\end{aligned}
}
\tag{3.4}
\]

Therefore deletion produces

\[
(R,D_+,U^{-1}),
\qquad
D_+=t^{-1}(zh)Y(zh)^{-1}.
\tag{3.5}
\]

The old \(W\)-deletion endpoint was

\[
(R,D',U^{-1}),
\qquad
D'=t^{-1}zYz^{-1}.
\tag{3.6}
\]

Their exact difference is

\[
\boxed{
(D')^{-1}D_+
=
\bigl((zY^{-1})h(Yz^{-1})\bigr)
\bigl(zh^{-1}z^{-1}\bigr).
}
\tag{3.7}
\]

Since

\[
h=R^{-1}U^{-1}R,
\]

both factors in (3.7) are conjugates of the surviving
\(U^{\pm1}\)-relator. Two source multiplications return \(D_+\) to
\(D'\). The existing source-slot certificate then returns

\[
(R,D',U^{-1})
\sim_{\mathrm{AC1-3}}
(R,B,D).
\tag{3.8}
\]

## 4. Exact negative quotient

Let

\[
Y_-=U^{-1}xU,
\qquad
h_-=R^{-1}UR.
\tag{4.1}
\]

The negative quotient

\[
\theta_-=\rho\delta_-\phi^{-1}
\tag{4.2}
\]

satisfies

\[
\boxed{
\begin{aligned}
\theta_-(\beta(R))&=R,\\
\theta_-(Wq^{-1})&=1,\\
\theta_-(q)&=U,\\
\theta_-(x)&=Y_-,\\
\theta_-(t)&=t,\\
\theta_-(z)&=zh_-=p_0R.
\end{aligned}
}
\tag{4.3}
\]

Thus

\[
(R,D_-,U),
\qquad
D_-=t^{-1}(zh_-)Y_-(zh_-)^{-1}.
\tag{4.4}
\]

The abstract proof already returns this endpoint to (3.6). For a literal
AK word certificate, put

\[
K=Y^{-1}Y_-.
\]

The identity

\[
K
=
U(x^{-1}U^{-1}x)(x^{-1}U^{-1}x)U
\tag{4.5}
\]

gives the six-factor normal-closure expansion

\[
\boxed{
\begin{aligned}
(D')^{-1}D_-
={}&
\bigl((zY^{-1})h_-(Yz^{-1})\bigr)\\
&\cdot(zUz^{-1})\\
&\cdot((zx^{-1})U^{-1}(xz^{-1}))\\
&\cdot((zx^{-1})U^{-1}(xz^{-1}))\\
&\cdot(zUz^{-1})\\
&\cdot(zh_-^{-1}z^{-1}).
\end{aligned}
}
\tag{4.6}
\]

Every factor is a conjugate of \(U^{\pm1}\), because \(h_-\) is itself
a conjugate of \(U\). This is the concrete version of (1.22).

## 5. Boundary

The theorem closes the two literal-source moves

\[
W\longmapsto Wq^{\pm1}.
\]

It does not close:

- \(W\mapsto Wc q^{\pm1}c^{-1}\) for an arbitrary nontrivial \(c\);
- multiplication by a q-source that was itself changed first;
- several interleaved q-dependent source factors;
- a pullback word not controlled modulo a surviving primitive \(U\);
- primitive-pair compression.

Thus the simplest q-dependent primitive-slot traffic is not an escape,
but AK(3) and stable AC remain open.

## 6. Independent replay

The dependency-free verifier
`tests/stable_ac/test_literal_q_source_traffic.py` checks:

- \(\nu,\nu^{-1}\), proving \(U\) primitive;
- both \(\delta_\pm\) and their inverses;
- both identities \(Wq^{\pm1}=(\phi\delta_\pm)(q)\);
- every quotient image in (3.4) and (4.3);
- the two-factor positive return (3.7);
- the six-factor negative return (4.6).
