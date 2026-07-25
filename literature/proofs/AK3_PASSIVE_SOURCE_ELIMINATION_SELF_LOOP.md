# Passive-source elimination absorbs every cross factor

Date: 2026-07-25

Status: **PROVEN** for an arbitrary finite number of cross multiplications
whose source spellings stay in the normal closure of the eventual
one-\(z\) isolator. For AK(3), this closes the remaining exactly-one-cross
role and, more strongly, every finite passive-\(B\)-source sequence. It does
not trivialize AK(3).

## 1. Quotient setup

Let \(X\) be a two-element free basis, let \(R\in F(X)\), and put

\[
G=F(X)/\langle\!\langle R\rangle\!\rangle,
\qquad
H=G*\langle z\rangle .
\tag{1.1}
\]

Write

\[
\pi:F(X,z)\longrightarrow H
\tag{1.2}
\]

for the quotient map. For \(e\in F(X)\), evaluation at \(z=e\) induces

\[
\operatorname{ev}_e:H\longrightarrow G.
\tag{1.3}
\]

This is well defined because \(R\) has no \(z\)-letter.

Fix a baseline isolator and survivor

\[
I_0=z^{-1}e_0,
\qquad
J_0\in F(X,z).
\tag{1.4}
\]

Let the final isolator be

\[
I=z^{-1}e.
\tag{1.5}
\]

The relevant invariant is not the literal spelling of the source slot but
its normal closure in \(H\).

## 2. The passive-source evaluation theorem

### Theorem 2.1

Suppose

\[
L
=
\langle\!\langle\pi(I_0)\rangle\!\rangle_H
=
\langle\!\langle\pi(I)\rangle\!\rangle_H.
\tag{2.1}
\]

Let

\[
q:H\longrightarrow H/L
\tag{2.2}
\]

be the quotient map. Suppose the final survivor \(J\in F(X,z)\) satisfies

\[
q(\pi(J))
=
q\!\left(a\,\pi(J_0)^\delta a^{-1}\right)
\tag{2.3}
\]

for some \(a\in H\) and \(\delta\in\{1,-1\}\).

After eliminating \(I\), put

\[
C=J[z\mapsto e],
\qquad
C_0=J_0[z\mapsto e_0].
\tag{2.4}
\]

Then

\[
\boxed{
(R,C)\sim_{\mathrm{AC1-3}}(R,C_0).
}
\tag{2.5}
\]

No trivial-group hypothesis is needed for the classical equivalence
(2.5).

#### Proof

Evaluation at \(z=e\) kills the final isolator:

\[
\operatorname{ev}_e(\pi(I))
=[e]^{-1}_G[e]_G
=1.
\tag{2.6}
\]

Its kernel is normal, so (2.1) gives

\[
L\subseteq\ker(\operatorname{ev}_e).
\tag{2.7}
\]

In particular, evaluation also kills \(I_0\):

\[
1
=
\operatorname{ev}_e(\pi(I_0))
=[e]^{-1}_G[e_0]_G.
\tag{2.8}
\]

Therefore

\[
[e]_G=[e_0]_G,
\qquad
\operatorname{ev}_e=\operatorname{ev}_{e_0}.
\tag{2.9}
\]

By (2.7), evaluation factors through \(q\). Applying it to (2.3) yields

\[
[C]_G
=
\bar a\,[C_0]_G^\delta\bar a^{-1},
\qquad
\bar a=\operatorname{ev}_e(a).
\tag{2.10}
\]

Choose \(A\in F(X)\) representing \(\bar a\), and put

\[
V=A C_0^\delta A^{-1}.
\tag{2.11}
\]

Equation (2.10) says

\[
C^{-1}V\in\langle\!\langle R\rangle\!\rangle_{F(X)}.
\tag{2.12}
\]

The fixed-relator normal-closure lemma replaces \(C\) by \(V\) through
AC1--AC3 moves while restoring \(R\) after every factor. One AC3 move
removes the conjugator \(A\), and AC1 removes the sign \(\delta\). This
proves (2.5). \(\square\)

The trivial-group hypothesis enters only when \(I\) is actually deleted
from a balanced rank-three trivial-group presentation by the stable
substitution-and-removal composite. It is not part of the rank-two
classical theorem.

## 3. Why arbitrary passive-source histories satisfy the theorem

Start the survivor with shadow \(\pi(J_0)\). Allow any finite sequence of:

1. left or right multiplication by a conjugate of a source spelling
   \(S^{\pm1}\) satisfying
   \[
   \pi(S)\in L;
   \tag{3.1}
   \]
2. fixed-\(R\) gauge modifications;
3. conjugation of the whole survivor; and
4. inversion of the whole survivor.

Modulo \(L\), every factor in item 1 is trivial. Every factor in item 2 is
already trivial in \(H\). Induction over the sequence therefore leaves
exactly

\[
q(\pi(J))
=
q\!\left(a\,\pi(J_0)^\delta a^{-1}\right)
\tag{3.2}
\]

for some accumulated \(a\) and sign \(\delta\). Theorem 2.1 applies.

There is no bound on:

- the number of source factors;
- the lengths of their conjugators;
- the number of fixed-\(R\) factors; or
- the occurrence of \(z^{\pm1}\) in any conjugator.

The condition (3.1) is essential. Merely restoring the final source is not
enough. A temporary source may leave \(L\), be multiplied into the target,
and later return; its nontrivial image in \(H/L\) then remains in the
survivor. Thus the theorem requires the source slot to stay passive in
normal closure at every cross event.

Fixed-\(R\) gauges, conjugations, and inversions of the source preserve
(3.1). A cross multiplication targeting the eventual source need not
preserve it and is outside the theorem.

## 4. The AK(3) passive-\(B\) corollary

At the rank-three compression root, put

\[
R=x^3t^{-4},
\qquad
p=xt,
\qquad
B=z^{-1}p,
\qquad
D=t^{-1}zxz^{-1}.
\tag{4.1}
\]

Use the \(B\)-slot as the eventual isolator source and the \(D\)-slot as
the survivor target. Permit arbitrary fixed-\(R\) gauges on both slots,
arbitrary conjugations and inversions, and any finite number of
multiplications of the \(D\)-slot by source spellings whose quotient
shadows lie in

\[
L=\langle\!\langle\pi(B)\rangle\!\rangle_H.
\tag{4.2}
\]

Suppose the final \(B\)-slot normalizes to \(I=z^{-1}e\), has normal closure
\(L\), and is eliminated. Theorem 2.1 gives the baseline endpoint

\[
\left(R,D[z\mapsto p]\right).
\tag{4.3}
\]

Directly,

\[
\begin{aligned}
D[z\mapsto p]
&=t^{-1}pxp^{-1}\\
&=t^{-1}xtxt^{-1}x^{-1}.
\end{aligned}
\tag{4.4}
\]

If

\[
S=xtxt^{-1}x^{-1}t^{-1}
\tag{4.5}
\]

is the AK(3) braid relator, then

\[
D[z\mapsto p]=t^{-1}St.
\tag{4.6}
\]

Hence

\[
\boxed{
\left(R,D[z\mapsto p]\right)
\sim_{\mathrm{AC3}}
(R,S)
=\operatorname{AK}(3).
}
\tag{4.7}
\]

This closes the source-eliminated branch of the exactly-one-cross
quotient theorem. More strongly, it closes every finite sequence in which
the \(B\)-slot remains the passive eventual isolator and all cross events
target the other slot.

## 5. Exact one-event formulas

The abstract theorem has a useful direct check. Since the final
\(B\)-type isolator is \(z^{-1}e\), put

\[
r=e^{-1}p.
\tag{5.1}
\]

Equation (2.9) gives \(r\in\langle\!\langle R\rangle\!\rangle\), and

\[
e=pr^{-1}.
\tag{5.2}
\]

Write

\[
D_e=t^{-1}exe^{-1},
\qquad
D_p=t^{-1}pxp^{-1}.
\tag{5.3}
\]

Then

\[
D_eD_p^{-1}
=
(t^{-1}p)
\left(r^{-1}xrx^{-1}\right)
(t^{-1}p)^{-1}
\in\langle\!\langle R\rangle\!\rangle.
\tag{5.4}
\]

If one cross event right-multiplies \(D\) by a conjugate of \(B^\epsilon\),
its evaluated endpoint has the exact form

\[
E_\epsilon
=
D_e\,c_e r^\epsilon c_e^{-1},
\qquad
\epsilon\in\{1,-1\},
\tag{5.5}
\]

where \(c_e\) is the evaluated conjugator. Thus

\[
E_\epsilon D_p^{-1}
=
\left(D_ec_er^\epsilon c_e^{-1}D_e^{-1}\right)
\left(D_eD_p^{-1}\right)
\in\langle\!\langle R\rangle\!\rangle.
\tag{5.6}
\]

Left multiplication gives the same conclusion with the first
normal-closure factor already on the left. Equations (5.4)--(5.6) exhibit
both signs and every conjugator without enumeration.

## 6. The opposite role is vacuous

Suppose instead that the \(D\)-slot is the restored passive source and is
meant to become the final one-\(z\) isolator.

The \(z\)-exponent homomorphism

\[
\sigma_z:H\longrightarrow\mathbb Z
\tag{6.1}
\]

is zero on \(G\) and sends \(z\) to \(1\). It gives

\[
\sigma_z(\pi(D))=0.
\tag{6.2}
\]

Fixed-\(R\) gauges do not change the quotient shadow. Conjugation preserves
\(\sigma_z\), and inversion only changes its sign, which remains zero.
Consequently every allowed passive \(D\)-source spelling has
\(z\)-exponent zero.

A normalized one-\(z\) isolator has the form

\[
z^{-1}e
\quad\text{or}\quad
ze,
\qquad e\in F(x,t),
\tag{6.3}
\]

and therefore has \(z\)-exponent \(-1\) or \(1\). It cannot be a passive
\(D\)-source shadow. Equivalently,
\(\langle\!\langle\pi(D)\rangle\!\rangle\) lies inside
\(\ker\sigma_z\), while the normal closure of a one-\(z\) isolator does
not.

Thus the role with \(B\) targeted and a restored \(D\)-source eliminated
has no endpoint in this mechanism.

## 7. Scope

The theorem closes arbitrary finite histories satisfying:

1. the retained relator \(R=x^3t^{-4}\) stays fixed in normal closure;
2. the eventual \(B\)-type isolator remains passive at every cross event;
3. every source spelling used against the survivor lies in the final
   isolator normal closure;
4. arbitrary fixed-\(R\) gauges, source factors, conjugators, survivor
   conjugations, and survivor inversions are allowed; and
5. the final source is a one-\(z\) generator isolator and is removed by the
   stable substitution-and-removal composite.

It does not cover a cross event targeting the eventual isolator, a source
spelling which temporarily leaves its final normal closure, a changed
retained relator, a multi-\(z\) primitive eliminator, another
stabilization, or dual-source primitive-pair compression.

AK(3) remains open.
