# Every signed qW changed source cancels with the surviving W-slot

Date: 2026-07-26

Status: **PROVEN**. At the fixed AK(3) source-slot checkpoint, all four
changed stabilizer sources

\[
Q_{\eta,\epsilon}=q^\eta W^\epsilon,
\qquad
\eta,\epsilon\in\{+1,-1\},
\]

are primitive by a unique-z coordinate. Deleting the changed source
first turns the surviving W-slot into the literal word
\(q^{-\eta\epsilon}\). Deleting that slot gives the same rank-two
endpoint in every sign branch. Arbitrary later traffic from
\(Q_{\eta,\epsilon}\) disappears.

This does not prove AK(3) stably AC-trivial.

## 1. The four primitive changed sources

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
\beta(q)=q.
\tag{1.2}
\]

Write

\[
A=\beta(R),
\qquad
C=\beta(p)q.
\tag{1.3}
\]

Then the surviving primitive source is

\[
W=\beta(U)q=Az^{-1}C.
\tag{1.4}
\]

At the checkpoint

\[
(A,W,D,q),
\tag{1.5}
\]

invert q and/or W as needed, multiply the q-target by the W-source, and
restore W. This manufactures every

\[
Q_{\eta,\epsilon}=q^\eta W^\epsilon
\tag{1.6}
\]

in the final slot while W remains unchanged.

### Positive W orientation

For \(\epsilon=+1\), put

\[
L_\eta=q^\eta A.
\tag{1.7}
\]

Then

\[
Q_{\eta,+}=L_\eta z^{-1}C.
\tag{1.8}
\]

The orientation-reversing automorphism

\[
\tau_{\eta,+}(z)=L_\eta z^{-1}C
\tag{1.9}
\]

fixes \(x,t,q\). Its inverse is

\[
\tau_{\eta,+}^{-1}(z)=Cz^{-1}L_\eta.
\tag{1.10}
\]

### Negative W orientation

For \(\epsilon=-1\), put

\[
H_\eta=q^\eta C^{-1},
\qquad
M=A^{-1}.
\tag{1.11}
\]

Then

\[
Q_{\eta,-}=H_\eta zM.
\tag{1.12}
\]

The orientation-preserving automorphism

\[
\tau_{\eta,-}(z)=H_\eta zM
\tag{1.13}
\]

fixes \(x,t,q\). Its inverse is

\[
\tau_{\eta,-}^{-1}(z)=H_\eta^{-1}zM^{-1}.
\tag{1.14}
\]

Thus all four changed sources are primitive.

## 2. The surviving W-slot becomes literal q

Keep \(Q_{\eta,\epsilon}\) unchanged and permit arbitrary later changes

\[
A\longmapsto Ag_A,
\qquad
W\longmapsto Wg_W,
\qquad
D\longmapsto Dg_D,
\tag{2.1}
\]

where each \(g_*\) lies in
\(\langle\!\langle Q_{\eta,\epsilon}\rangle\!\rangle\).

All preceding operations are classical AC moves, so the tuple remains
balanced and presents the trivial group. Straighten
\(Q_{\eta,\epsilon}\) with the appropriate inverse automorphism and
delete z. Every \(g_*\) vanishes.

For \(\epsilon=+1\), equation (1.10) gives

\[
\begin{aligned}
\tau_{\eta,+}^{-1}(W)
&=
A(L_\eta^{-1}zC^{-1})C\\
&=
q^{-\eta}z.
\end{aligned}
\tag{2.2}
\]

After \(z\mapsto1\), this is \(q^{-\eta}\).

For \(\epsilon=-1\), equation (1.14) gives

\[
\begin{aligned}
\tau_{\eta,-}^{-1}(W)
&=
A(Mz^{-1}H_\eta)C\\
&=
z^{-1}q^\eta.
\end{aligned}
\tag{2.3}
\]

After \(z\mapsto1\), this is \(q^\eta\).

Therefore, uniformly,

\[
\boxed{
W\longmapsto q^{-\eta\epsilon}.
}
\tag{2.4}
\]

The surviving W-slot is a literal q-relator up to inversion and can be
deleted next.

## 3. The common endpoint

The A-slot is z-free, so it is unchanged by the first straightening.
After the second deletion,

\[
A=\beta(R)\longmapsto R.
\tag{3.1}
\]

For \(\epsilon=+1\), straightening and z-deletion send D to

\[
t^{-1}(CL_\eta)x(CL_\eta)^{-1}.
\tag{3.2}
\]

For \(\epsilon=-1\), they send D to

\[
t^{-1}(H_\eta^{-1}M^{-1})
x(H_\eta^{-1}M^{-1})^{-1}.
\tag{3.3}
\]

Killing q sends both conjugating words to

\[
pR.
\tag{3.4}
\]

Indeed,

\[
\rho(CL_\eta)=pR,
\qquad
\rho(H_\eta^{-1}M^{-1})=pR.
\]

Hence all four sign branches give

\[
\boxed{
(R,E_R),
\qquad
E_R=t^{-1}(pR)x(pR)^{-1}.
}
\tag{3.5}
\]

With

\[
E_0=t^{-1}pxp^{-1},
\]

the exact difference is

\[
\boxed{
E_0^{-1}E_R
=
\bigl((px^{-1})R(xp^{-1})\bigr)
\bigl(pR^{-1}p^{-1}\bigr).
}
\tag{3.6}
\]

Writing the two factors as \(f_1,f_2\),

\[
E_Rf_2^{-1}f_1^{-1}=E_0.
\tag{3.7}
\]

Thus two retained-R source multiplications return every branch to the
standard rank-two AK endpoint.

## 4. Boundary

The theorem requires:

- the fixed source-slot factorization \(W=Az^{-1}C\);
- a changed final source exactly \(q^\eta W^\epsilon\);
- that changed source kept unchanged and deleted through z first;
- later target multipliers only from its normal closure;
- the surviving W-slot kept distinct until the first deletion.

It does not cover a longer mixed source word, a second change to
\(Q_{\eta,\epsilon}\), traffic from another source with nontrivial
first-deletion image, deletion of W before the changed source, or
primitive-pair compression. AK(3) and stable AC remain open.

## 5. Independent replay

The dependency-free verifier
`tests/stable_ac/test_qw_source_pair_cancellation.py` checks:

- all four exact source words and unique-z factorizations;
- every z-coordinate automorphism and inverse in both composition
  orders;
- representative changed-source traffic in all three survivor slots;
- the literal W images \(q^{-\eta\epsilon}\);
- both sign-dependent D images before q-deletion;
- the common endpoint (3.5);
- the exact two-factor return (3.6)--(3.7).
