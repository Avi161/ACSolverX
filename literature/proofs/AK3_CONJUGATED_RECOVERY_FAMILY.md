# The conjugated-recovery family at the AK(3) compression root

Date: 2026-07-24

Status: the stable construction and the complete
Aut(\(F_2\))-floor formulas are **PROVEN** for every integer parameter.

## 1. Compression and the retained consequence

At the compression root put

\[
 v=zxz^{-1},\qquad a=x^3.
\]

The relators are

\[
 A=av^{-4},\qquad B=z^{-1}xv.
\]

Adjoin \(t=v\), with defining relator

\[
 D=t^{-1}v.
\]

Using \(D\), replace \(A\) and \(B\) by

\[
 R=at^{-4},\qquad B_0=z^{-1}xt.
\tag{1.1}
\]

For \(m\in\mathbb Z\), define

\[
 K_m=t^{-1}a^mta^{-m},\qquad
 U_m=tK_m=a^mta^{-m}.
\tag{1.2}
\]

The point is not merely that \(K_m=1\) modulo \(R\).  It has a literal
factorization into conjugates of the retained relator, so multiplying
\(B_0\) by it is a signed AC sequence.

Put

\[
 C=K_1=t^{-1}ata^{-1}.
\]

Since \(R=at^{-4}\),

\[
 C=(t^{-1}Rt)R^{-1}.
\tag{1.3}
\]

The commutator-power identity

\[
 K_{r+s}=K_r\left(a^rK_sa^{-r}\right)
\tag{1.4}
\]

gives

\[
 K_m=\prod_{j=0}^{m-1}a^jCa^{-j}
 \qquad(m>0)
\tag{1.5+}
\]

and, in the displayed order,

\[
 K_{-q}=\prod_{j=1}^{q}a^{-j}C^{-1}a^j
 \qquad(q>0).
\tag{1.5-}
\]

Every factor in these products splits into two conjugates of \(R^{\pm1}\):

\[
\begin{aligned}
 a^jCa^{-j}
 &=
 \bigl[(ta^{-j})^{-1}R(ta^{-j})\bigr]
 \bigl[a^jR^{-1}a^{-j}\bigr],\\
 a^{-j}C^{-1}a^j
 &=
 \bigl[a^{-j}Ra^j\bigr]
 \bigl[(ta^j)^{-1}R^{-1}(ta^j)\bigr].
\end{aligned}
\tag{1.6}
\]

Thus \(K_m\) is an explicit ordered product of exactly \(2|m|\)
conjugates of \(R\) or \(R^{-1}\).

To multiply \(B_0\) by one displayed factor, conjugate and, if necessary,
invert the \(R\)-relator, apply one relator multiplication to \(B_0\), and
undo the changes to \(R\).  Repeating this operation gives

\[
 B_m=z^{-1}x\,tK_m=z^{-1}xU_m.
\tag{1.7}
\]

Restore \(A\) from \(R\) using \(D\), and remove \(z\) from \(B_m\) via

\[
 z=e_m:=xU_m=xa^mta^{-m}.
\tag{1.8}
\]

The surviving pair over \(x,t\) is

\[
 P_m=
 \left(
 x^3e_mx^{-4}e_m^{-1},\
 t^{-1}e_mxe_m^{-1}
 \right).
\tag{1.9}
\]

This proves

\[
 \mathrm{AK}(3)\sim_{\mathrm{st}}P_m
 \qquad(m\in\mathbb Z).
\tag{1.10}
\]

## 2. Positive and zero parameters

Relabel \(t\) as \(y\).  For \(m\ge0\), put

\[
 k=3m+1
\]

and apply the basis automorphism

\[
 \phi_m^+(x)=x,\qquad
 \phi_m^+(y)=x^{-k}y^{-1}.
\tag{2.1}
\]

This is a signed Nielsen automorphism.  Direct free and cyclic reduction
of (1.9), followed only by cyclic rotation, gives

\[
\begin{aligned}
 W^+_{m,1}&=x^3y^{-1}x^{-4}y,\\
 W^+_{m,2}&=yx^ky^{-1}xy.
\end{aligned}
\tag{2.2}
\]

Consequently,

\[
 |W^+_{m,1}|+|W^+_{m,2}|
 =9+(k+4)=3m+14.
\tag{2.3}
\]

Unlike a numerical interpolation, (2.2) is an exact block identity for
every \(m\ge0\).

## 3. Negative parameters

Write \(m=-q\), where \(q\ge1\), and put

\[
 h=3q-1.
\]

Apply

\[
 \phi_q^-(x)=x,\qquad
 \phi_q^-(y)=yx^h.
\tag{3.1}
\]

Cyclic reduction and rotation give

\[
\begin{aligned}
 W^-_{q,1}&=yx^{-4}y^{-1}x^3,\\
 W^-_{q,2}&=y^{-1}x^{-h}yxy^{-1}.
\end{aligned}
\tag{3.2}
\]

Hence

\[
 |W^-_{q,1}|+|W^-_{q,2}|
 =9+(h+4)=3q+12.
\tag{3.3}
\]

## 4. Symbolic Whitehead minimality

First-kind Whitehead automorphisms preserve cyclic length.  In the order
used below, the twelve second-kind maps have the following exact total
length changes on (2.2) and (3.2):

| second-kind image | \(\Delta_+(m)\), \(m\ge0\) | \(\Delta_-(q)\), \(q\ge1\) |
|---|---:|---:|
| \(y\mapsto yx\) | \(1\) | \(1\) |
| \(y\mapsto x^{-1}y\) | \(1\) | \(1\) |
| \(y\mapsto x^{-1}yx\) | \(0\) | \(0\) |
| \(y\mapsto yx^{-1}\) | \(1\) | \(1\) |
| \(y\mapsto xy\) | \(1\) | \(1\) |
| \(y\mapsto xyx^{-1}\) | \(0\) | \(0\) |
| \(x\mapsto xy\) | \(3m+5\) | \(3q+3\) |
| \(x\mapsto y^{-1}x\) | \(3m+5\) | \(3q+3\) |
| \(x\mapsto y^{-1}xy\) | \(0\) | \(0\) |
| \(x\mapsto xy^{-1}\) | \(3m+5\) | \(3q+3\) |
| \(x\mapsto yx\) | \(3m+5\) | \(3q+3\) |
| \(x\mapsto yxy^{-1}\) | \(0\) | \(0\) |

The unmentioned generator is fixed in each row.  These formulas follow
directly by cancellation against the fixed nine-letter first relator and
the one long \(x\)- or \(x^{-1}\)-block in the second relator.

All twelve changes are nonnegative throughout their stated parameter
ranges.  Whitehead's strict-reduction theorem for tuples of conjugacy
classes therefore proves that (2.2) and (3.2) are global
Aut(\(F_2\))-minima.  The zero rows are level moves, not concealed
descents.

### Theorem 4.1

For every \(m\in\mathbb Z\), the complete Aut-floor of the stable endpoint
\(P_m\) is

\[
 \mu(P_m)=
 \begin{cases}
 3m+14,&m>0,\\
 14,&m=0,\\
 3(-m)+12,&m<0.
 \end{cases}
\tag{4.1}
\]

In particular,

\[
 \mu(P_m)\ge14
\]

for every \(m\).  No member of this infinite conjugated-recovery family
reaches the length-\(12\) theorem.

## 5. Scope

This theorem closes the whole consequence direction

\[
 U_m=a^mta^{-m},
\]

including the floor-\(17\) two-rotation example
\(U_1=x^3tx^{-3}\).  It does not classify products or interleavings of
this commutator consequence with the rotation powers
\(t(t^{-4}x^3)^n\), nor consequences involving both \(R\) and \(D\) after
another relator multiplication.  Those remain distinct mechanisms.

## 6. Independent replay

`tests/stable_ac/test_conjugated_recovery_family.py` independently checks:

1. the ordered \(2|m|\)-factor decomposition into conjugates of
   \(R^{\pm1}\);
2. the exact identity \(tK_m=a^mta^{-m}\);
3. the endpoint construction (1.8)--(1.9);
4. the complete floor formula on both sides of zero; and
5. every symbolic row of the twelve-move Whitehead table.

The finite signed grid guards transcription.  Identities
(1.5)--(1.6), the block forms (2.2) and (3.2), and Whitehead's theorem
prove the result for all integers.
