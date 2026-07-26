# A coherent tail on qW transfers into a deletable left q-source

Date: 2026-07-26

Status: **PROVEN**. At the fixed AK(3) source-slot checkpoint, every

\[
Q_{\eta,\epsilon,V}
=
q^\eta W^\epsilon\beta(V),
\qquad
\eta,\epsilon\in\{+1,-1\},
\qquad
V\in\langle\!\langle R\rangle\!\rangle_{F(x,t)},
\]

is a unique-z primitive word. Its deletion transfers the tail into the
surviving W-slot as

\[
\bigl(\beta(V)q^\eta\bigr)^{-\epsilon}.
\]

That word is a coherently transported left q-source and is also
primitive. Deleting it gives a rank-two endpoint equal to the standard
AK endpoint modulo the retained R-source.

This does not prove AK(3) stably AC-trivial.

## 1. Setup and manufacture

Put

\[
\begin{aligned}
R&=x^3t^{-4},&
p&=xt,\\
B&=z^{-1}p,&
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

and write

\[
A=\beta(R),
\qquad
C=\beta(p)q,
\qquad
W=Az^{-1}C.
\tag{1.3}
\]

The fixed checkpoint is

\[
(A,W,D,q).
\tag{1.4}
\]

Choose \(V\in\langle\!\langle R\rangle\!\rangle_{F(x,t)}\). Then

\[
\beta(V)\in\langle\!\langle A\rangle\!\rangle.
\]

First manufacture \(q^\eta W^\epsilon\) in the q-slot while restoring
W. Then use the A-slot normal closure to right-multiply that target by
\(\beta(V)\). This gives

\[
Q_{\eta,\epsilon,V}
=q^\eta W^\epsilon\beta(V)
\tag{1.5}
\]

while A and W remain unchanged.

## 2. Unique-z deletion transfers the tail

Put

\[
S=\beta(V).
\tag{2.1}
\]

For \(\epsilon=+1\), define

\[
L_\eta=q^\eta A,
\qquad
\tau_{\eta,+}(z)=L_\eta z^{-1}CS.
\tag{2.2}
\]

This fixes \(x,t,q\) and has inverse

\[
\tau_{\eta,+}^{-1}(z)=CSz^{-1}L_\eta.
\tag{2.3}
\]

For \(\epsilon=-1\), define

\[
H_\eta=q^\eta C^{-1},
\qquad
M=A^{-1}S,
\qquad
\tau_{\eta,-}(z)=H_\eta zM.
\tag{2.4}
\]

Its inverse, again fixing \(x,t,q\), is

\[
\tau_{\eta,-}^{-1}(z)=H_\eta^{-1}zM^{-1}.
\tag{2.5}
\]

These are triangular one-z automorphisms whose z-images are exactly
\(Q_{\eta,\epsilon,V}\). Thus every changed source is primitive.

Keep that source fixed and allow arbitrary later traffic from its normal
closure into A, W, or D. Straighten
\(Q_{\eta,\epsilon,V}\) with the appropriate inverse and delete z.
All such traffic vanishes.

For \(\epsilon=+1\),

\[
\tau_{\eta,+}^{-1}(W)
=
q^{-\eta}zS^{-1},
\tag{2.6}
\]

while for \(\epsilon=-1\),

\[
\tau_{\eta,-}^{-1}(W)
=
Sz^{-1}q^\eta.
\tag{2.7}
\]

Consequently,

\[
\boxed{
W\longmapsto
P_{\eta,V}^{-\epsilon},
\qquad
P_{\eta,V}:=Sq^\eta=\beta(V)q^\eta.
}
\tag{2.8}
\]

The first deletion also leaves A unchanged. Its D-image has the uniform
form

\[
t^{-1}(CP_{\eta,V}^{\epsilon}A)
x(CP_{\eta,V}^{\epsilon}A)^{-1}.
\tag{2.9}
\]

## 3. The transferred word is primitive

Define the left q-coordinate automorphism on \(F(x,t,q)\) by

\[
\ell_{V,\eta}(q)=Vq^\eta,
\qquad
\ell_{V,\eta}(x)=x,
\qquad
\ell_{V,\eta}(t)=t.
\tag{3.1}
\]

For \(\eta=+1\), its inverse sends

\[
q\longmapsto V^{-1}q.
\tag{3.2}
\]

For \(\eta=-1\), its inverse sends

\[
q\longmapsto q^{-1}V.
\tag{3.3}
\]

Set

\[
\theta_{\eta,V}=\beta\ell_{V,\eta}.
\tag{3.4}
\]

Because \(\beta(q)=q\),

\[
\theta_{\eta,V}(q)
=
\beta(V)q^\eta
=P_{\eta,V}.
\tag{3.5}
\]

Thus the surviving word \(P_{\eta,V}^{-\epsilon}\) is primitive up to
inversion. Invert that relator when necessary, straighten by
\(\theta_{\eta,V}^{-1}=\ell_{V,\eta}^{-1}\beta^{-1}\), and delete q.

## 4. Exact second-deletion endpoint

The A-slot returns literally:

\[
\theta_{\eta,V}^{-1}(A)=R.
\tag{4.1}
\]

Moreover,

\[
\rho\theta_{\eta,V}^{-1}(C)
=
pV^{-\eta},
\tag{4.2}
\]

where \(\rho\) kills q. The x-image is also nontrivial:

\[
\rho\theta_{\eta,V}^{-1}(x)
=
V^\eta xV^{-\eta}.
\tag{4.3}
\]

Indeed, \(\beta^{-1}(x)=q^{-1}xq\), and applying the appropriate inverse
in (3.2)--(3.3) gives (4.3). This transported x-image is essential.

Equation (2.9), together with
\(\theta_{\eta,V}^{-1}(P_{\eta,V})=q\), therefore gives

\[
\boxed{
\left(
R,\;
E_{V,\eta}
\right),
\qquad
E_{V,\eta}
=
t^{-1}(pH_{V,\eta})
x(pH_{V,\eta})^{-1},
\qquad
H_{V,\eta}=V^{-\eta}RV^\eta.
}
\tag{4.4}
\]

The result is independent of \(\epsilon\).

The word \(H_{V,\eta}\) is one conjugate of R. Put

\[
E_0
:=
t^{-1}pxp^{-1}
\tag{4.5}
\]

The exact difference is

\[
\boxed{
E_0^{-1}E_{V,\eta}
=
\bigl((px^{-1}V^{-\eta})R(V^\eta xp^{-1})\bigr)
\bigl((pV^{-\eta})R^{-1}(V^\eta p^{-1})\bigr).
}
\tag{4.6}
\]

Thus exactly two retained-R source factors return
\(E_{V,\eta}\) classically to \(E_0\), independently of the
factorization or length of V.

## 5. Exact V=R specialization

For \(V=R\), both eta orientations give

\[
H_{R,+}=R^{-1}RR=R,
\qquad
H_{R,-}=RRR^{-1}=R.
\tag{5.1}
\]

Thus all four sign branches reach the same familiar endpoint

\[
\boxed{
(R,E_R),
\qquad
E_R=t^{-1}(pR)x(pR)^{-1}.
}
\tag{5.2}
\]

Equation (4.6) reduces to the two-factor return already used in Results
40--41.

## 6. Boundary

The theorem requires:

- the fixed factorization \(W=Az^{-1}C\);
- a coherent z-free right tail \(S=\beta(V)\) with
  \(V\in\langle\!\langle R\rangle\!\rangle\);
- a changed source exactly \(q^\eta W^\epsilon S\), kept unchanged and
  deleted first;
- the transferred W-slot kept distinct for the second deletion;
- later first-stage traffic only from the changed source.

It does not cover a z-dependent tail, an incoherent q-dependent tail, a
second source change, traffic with nontrivial first-deletion image, loss
of the A-carrier normal closure, or primitive-pair compression. AK(3)
and stable AC remain open.

## 7. Independent replay

The dependency-free verifier
`tests/stable_ac/test_qw_transported_tail.py` checks:

- several nontrivial V words in the normal closure of R;
- all four sign pairs and both unique-z automorphism inverses;
- the exact tail-transfer identity (2.8);
- representative first-source traffic in every survivor slot;
- both left q-coordinate automorphisms and inverses;
- the exact D-image (2.9), transported x-image (4.3), and endpoint
  (4.4);
- the exact two-factor return (4.6) and the common V=R endpoint (5.2).
