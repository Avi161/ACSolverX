# Arbitrary recovery followed by one \(D\)-catalyst is an AK(3) self-loop

Date: 2026-07-24

Status: **PROVEN** for every quotient-equal recovery word and every relative
conjugator in the subsequent one-\(D\) multiplication.  There is no
word-length or conjugator-length bound.  This is a mechanism-closing
theorem, not a trivialization of AK(3).

## 1. Setup

Put

\[
R=x^3t^{-4},\qquad
D=t^{-1}zxz^{-1}.
\tag{1.1}
\]

Let \(U(x,t)\) be any word satisfying

\[
U=t
\quad\text{in}\quad
\langle x,t\mid R\rangle,
\tag{1.2}
\]

and put

\[
w=\overline{xU},\qquad
B_U=z^{-1}w.
\tag{1.3}
\]

The bar denotes free reduction.  In string notation,

```text
R   = xxxTTTT
B_U = Z w
D   = TzxZ
```

The arbitrary-recovery construction reaches the rank-three tuple

\[
(R,B_U,D)
\tag{1.4}
\]

from AK(3) by stable moves.  It presents the trivial group.  The relator
\(B_U\) has exactly one \(z^{\pm1}\), while \(D\) has two.

The direct unrestored elimination \(z=w\) gives

\[
Q(U)=(R,S_0(U)),
\qquad
S_0(U)=t^{-1}wxw^{-1}.
\tag{1.5}
\]

The arbitrary-recovery self-loop theorem proves

\[
Q(U)\sim_{\mathrm{AC1-3}}\operatorname{AK}(3).
\tag{1.6}
\]

We now allow one multiplication targeting \(B_U\) by an arbitrary conjugate
of \(D^{\pm1}\) before eliminating \(z\).

## 2. Statement

### Theorem 2.1

Choose arbitrary conjugates and orientations of \(B_U,D\), perform one
relator multiplication with \(B_U\) as target and \(D\) as source, and
freely and cyclically reduce the target.  If the new target contains exactly
one \(z^{\pm1}\), then its cyclic word is one of the two templates

\[
\operatorname{cyc}(z^{-1}t^{-1}wx),
\qquad
\operatorname{cyc}(z^{-1}twx^{-1}).
\tag{2.1}
\]

After solving either target for \(z\) and applying the
substitution-and-removal stable composite, the surviving rank-two pair is
classically AC-equivalent to \(Q(U)\), hence to AK(3).

Thus arbitrary recovery followed by one arbitrary-relative-conjugator
\(D\)-catalyst is a classical self-loop after elimination.

## 3. Removing the arbitrary relative conjugator

Both \(B_U\) and \(D^{\pm1}\) are cyclically reduced.  Apply the bridge
normal form from
`literature/proofs/AK3_ONE_D_CATALYST_BARRIER.md`, Lemma 3.1, to their
arbitrarily conjugated representatives.

If the two axes are disjoint, the product has a cyclically reduced spelling

\[
V_BcV_Dc^{-1},
\tag{3.1}
\]

where \(c\ne1\) is the shortest axis bridge and \(V_B,V_D\) are signed
cyclic rotations.  Therefore

\[
\nu_z(V_BcV_Dc^{-1})
=\nu_z(B_U)+\nu_z(D)+2\nu_z(c)
=3+2\nu_z(c)
\ge3.
\tag{3.2}
\]

It cannot be a one-\(z\) target.

Consequently the axes intersect.  Choose a common vertex, so the normalized
bridge is empty.  The target is now the cyclic reduction of a product

\[
V_BV_D
\tag{3.3}
\]

of signed rotations.  This reduction is finite in the two factor seams even
though the word \(U\) is unbounded.

Whole-target inversion causes no additional case.  Up to inversion and
cyclic reordering,

\[
(V_B^{-1}V_D)^{-1}=V_D^{-1}V_B
\]

is the positive-\(B_U\) case with the sign of \(D\) reversed.  Factor order
is likewise cyclic reordering.  Hence we may orient \(B_U\) positively and
put the sign only on \(D\).

## 4. The forced \(Zz\) seam

Before reduction, the two factors in (3.3) have three
\(z^{\pm1}\)-letters.  A final incidence of one requires exactly one
inverse \(z\)-pair to cancel.

Each factor is cyclically reduced.  Thus cancellation in their cyclic
product occurs across one of the two factor seams.  The unique positive
\(z\), which lies in \(D^{\pm1}\), cannot cancel the \(z^{-1}\) from that
same factor.  The shorter cyclic arc between those two letters contains the
single nonempty letter \(x^{\pm1}\), so it cannot reduce away by itself.
The other arc contains the unique \(z^{-1}\) from \(B_U\) but no second
positive \(z\), so that arc cannot reduce away either.  Equivalently, the
noncrossing free-cancellation pairing cannot match the two \(D\)-letters.

Therefore the positive \(z\) must cancel the unique \(z^{-1}\) in \(B_U\).
If preceding \(x,t\)-letters cancel first, rotate both factors across this
eventual \(z^{-1}z\) pair.  As in the cancelling-seam normal form, this gives
the same reduced cyclic word with that pair at the displayed seam.

The phases are now forced.  For positive \(D\),

\[
\begin{aligned}
(wz^{-1})(z x z^{-1}t^{-1})
&\longrightarrow wxz^{-1}t^{-1}\\
&\sim_{\mathrm{cyc}}z^{-1}t^{-1}wx.
\end{aligned}
\tag{4.1}
\]

For \(D^{-1}\),

\[
\begin{aligned}
(wz^{-1})(z x^{-1}z^{-1}t)
&\longrightarrow wx^{-1}z^{-1}t\\
&\sim_{\mathrm{cyc}}z^{-1}twx^{-1}.
\end{aligned}
\tag{4.2}
\]

Additional free or cyclic cancellation may occur among the displayed
\(x,t\)-letters, but there is no remaining \(z\) which can cancel the single
\(z^{-1}\).  Equations (4.1)--(4.2) therefore prove that (2.1) is complete.

The two equations isolate

\[
e_+(U)=t^{-1}wx,\qquad
e_-(U)=twx^{-1}.
\tag{4.3}
\]

## 5. The catalyst only conjugates the direct endpoint

Substitute (4.3) in the surviving relator \(D\).  Put

\[
S_\pm(U)=t^{-1}e_\pm(U)x e_\pm(U)^{-1}.
\tag{5.1}
\]

The first branch has the exact free reduction

\[
\begin{aligned}
S_+(U)
&=t^{-1}(t^{-1}wx)x(t^{-1}wx)^{-1}\\
&=t^{-2}wxw^{-1}t\\
&=t^{-1}S_0(U)t.
\end{aligned}
\tag{5.2}
\]

The second branch gives

\[
\begin{aligned}
S_-(U)
&=t^{-1}(twx^{-1})x(twx^{-1})^{-1}\\
&=wxw^{-1}t^{-1}\\
&=tS_0(U)t^{-1}.
\end{aligned}
\tag{5.3}
\]

Thus the two post-catalyst endpoints are

\[
(R,t^{-1}S_0(U)t)
\quad\text{and}\quad
(R,tS_0(U)t^{-1}).
\tag{5.4}
\]

Each differs from \(Q(U)=(R,S_0(U))\) by one AC3 conjugation of the second
relator.  Combining (5.4) with (1.6) proves Theorem 2.1.

The stable substitution-and-removal step is legitimate because (1.4)
presents the trivial group.  It is not being treated as a bare AC5 move,
and no elementary move-count bound is claimed.

## 6. Scope

The theorem is unbounded simultaneously in the recovery word \(U\) and in
the relative conjugator used by the \(D\)-multiplication.  The two symbolic
seams in (4.1)--(4.2), rather than a finite word census, give completeness.

It covers the order:

1. change \(B=z^{-1}xt\) to an arbitrary
   \(B_U=z^{-1}xU\) using \(R\)-consequences;
2. apply one \(D^{\pm1}\)-multiplication targeting \(B_U\); and
3. eliminate \(z\) through the resulting generator isolator.

It does not cover a different interleaving of \(R\)- and \(D\)-factors, two
or more \(D\)-factors, reversing the target/source roles so that \(D\) is
removed and \(B_U\) survives, a changed retained relator, a primitive
eliminator with several \(z\)-letters, dual-source compression, or another
stabilization architecture.

AK(3) remains open.
