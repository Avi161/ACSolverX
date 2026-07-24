# An all-integer consequence-twist family at the AK(3) compression root

Date: 2026-07-24

Status: the stable construction, the complete Aut(\(F_2\))-floor formulas,
and the Whitehead-minimality proof are **PROVEN** for every
\(n\in\mathbb Z\).

## 1. Construction

At the compression root put

\[
 v=zxz^{-1},
\]

so the relators are

\[
 A=x^3v^{-4},\qquad B=z^{-1}xv.
\]

Adjoin \(t=v\), with defining relator

\[
 D=t^{-1}v.
\]

Using \(D\), compress the power relator to

\[
 R=x^3t^{-4}.
\]

Let

\[
 R'=t^{-4}x^3
\]

be its displayed cyclic rotation.  For an arbitrary integer \(n\), define

\[
 U_n=t(R')^n.
\tag{1.1}
\]

First compress \(B\) to \(z^{-1}xt\).  While \(R\) is retained as the other
relator, multiply the compressed \(B\) by \(R'\), or by \((R')^{-1}\),
\(|n|\) times according to the sign of \(n\).  This gives

\[
 B_n=z^{-1}xU_n.
\]

Restore \(A\) from \(R\) using \(D\).  Now \(B_n\) contains one
\(z^{-1}\), so remove \(z\) with

\[
 z=e_n:=xU_n.
\tag{1.2}
\]

The surviving rank-two pair over \(x,t\) is

\[
 P_n=
 \left(
 x^3e_nx^{-4}e_n^{-1},\
 t^{-1}e_nxe_n^{-1}
 \right).
\tag{1.3}
\]

Every step is an AC1--AC3 move, a reversible displayed substitution using
\(D\), or the substitution-and-removal lemma.  Hence

\[
 \mathrm{AK}(3)\sim_{\mathrm{st}}P_n
\qquad(n\in\mathbb Z).
\tag{1.4}
\]

The case \(n=0\) is the canonical \(k=1\) Bézout endpoint of floor \(14\).
The case \(n=1\) is the floor-23 counterexample showing that quotient
recovery words are not unique.

## 2. Reduced Whitehead coordinates

Relabel \(t\) as \(y\).  For \(m\ge1\), apply

\[
\phi_+(x)=y^{-1},\qquad \phi_+(y)=x
\]

to \(P_m\), and cyclically reduce.  The resulting pair is

\[
\begin{aligned}
 W^+_{m,1}
 &=Y^3X^3(Y^3X^4)^{m-1}
   y^4(x^4y^3)^{m-1}x^3,\\
 W^+_{m,2}
 &=XYX^3(Y^3X^4)^{m-1}
   Y(x^4y^3)^{m-1}x^3y.
\end{aligned}
\tag{2.1+}
\]

Here \(X=x^{-1}\) and \(Y=y^{-1}\).  Direct counting gives

\[
 |W^+_{m,1}|+|W^+_{m,2}|=28m-5.
\tag{2.2+}
\]

For the negative parameter, apply

\[
\phi_-(x)=y,\qquad \phi_-(y)=x^{-1}
\]

to \(P_{-m}\).  Cyclic reduction gives

\[
\begin{aligned}
 W^-_{m,1}
 &=y^3X(Y^3X^4)^m
   Y^4(x^4y^3)^mx,\\
 W^-_{m,2}
 &=xyX(Y^3X^4)^m
   y(x^4y^3)^mxY,
\end{aligned}
\tag{2.1-}
\]

and hence

\[
 |W^-_{m,1}|+|W^-_{m,2}|=28m+15.
\tag{2.2-}
\]

## 3. Symbolic Whitehead minimality

In rank two, first-kind Whitehead automorphisms preserve length.  Up to
those signed permutations, the twelve second-kind automorphisms are the
ones in the table below.  Substituting into (2.1+) and (2.1-), freely and
cyclically reducing, gives the exact total-length changes:

| second-kind image | \(\Delta_+(m)\) | \(\Delta_-(m)\) |
|---|---:|---:|
| \(y\mapsto yx\) or \(y\mapsto xy\) | \(12m-6\) | \(12m+4\) |
| \(y\mapsto x^{-1}y\) or \(y\mapsto yx^{-1}\) | \(4m\) | \(4m+6\) |
| \(y\mapsto x^{-1}yx\) or \(y\mapsto xyx^{-1}\) | \(0\) | \(0\) |
| \(x\mapsto xy\) or \(x\mapsto yx\) | \(16m-7\) | \(16m-1\) |
| \(x\mapsto y^{-1}x\) or \(x\mapsto xy^{-1}\) | \(8m-1\) | \(8m+1\) |
| \(x\mapsto y^{-1}xy\) or \(x\mapsto yxy^{-1}\) | \(0\) | \(0\) |

The unmentioned generator is fixed in each row.  The table is a symbolic
count: each extra copy of the two seven-letter blocks in (2.1+) or (2.1-)
adds the displayed coefficient of \(m\), and the fixed prefix and suffix
give the constant term.

Every entry is nonnegative for \(m\ge1\).  Whitehead's length-reduction
theorem therefore shows that both \(W^+_m\) and \(W^-_m\) have globally
minimal total length in their complete Aut(\(F_2\))-orbits.  The zero rows
are length-preserving plateau moves, not hidden descents.

### Theorem 3.1

For every \(n\in\mathbb Z\), the complete Aut-floor of the stable endpoint
\(P_n\) is

\[
 \mu(P_n)=
 \begin{cases}
 28(-n)+15,&n<0,\\
 14,&n=0,\\
 28n-5,&n>0.
 \end{cases}
\tag{3.1}
\]

In particular,

\[
 \mu(P_n)\ge14
\]

for all \(n\), with equality only at \(n=0\).  No member of this unbounded
consequence-twist family reaches the length-\(12\) theorem.

## 4. Scope

The theorem closes all powers of one fixed cyclic rotation \(R'\) inserted
on the right of the canonical recovery word \(t\).  It does not classify:

- products of different rotations or conjugates of \(R\);
- insertions on both sides of \(t\);
- consequences involving the defining relator \(D\) in a nontrivial
  interleaving; or
- recovery words obtained after first changing \(A\) or \(B\) by another
  relator multiplication.

Those are genuine additional mechanisms, not cases of (1.1).

## 5. Independent replay

`tests/stable_ac/test_consequence_twist_family.py` checks:

1. the exact signed powers in (1.1);
2. the endpoint construction (1.2)--(1.3);
3. the complete floor formula (3.1) on both sides of zero; and
4. every affine entry in the twelve-move Whitehead table.

The finite signed grid guards the transcription.  The block count and
Whitehead theorem prove the result for all integers \(n\).
