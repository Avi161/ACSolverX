# A two-parameter mixed-consequence family for AK(3)

Date: 2026-07-24

Status: the stable construction and the complete
Aut(\(F_2\))-floor formula are **PROVEN** for every
\((n,m)\in\mathbb Z^2\).

## 1. The ordered mixed recovery

At the \(k=1\) compression root, write

\[
 a=x^3,\qquad
 R=at^{-4},\qquad
 R'=t^{-4}a.
\]

Here \(R'\) is a cyclic rotation of the retained relator \(R\).  For
\(m\in\mathbb Z\), put

\[
 K_m=t^{-1}a^mta^{-m}.
\]

The preceding one-parameter theorems prove:

1. every power \((R')^n\) can be multiplied into the compressed second
   relator while \(R\) is retained; and
2. \(K_m\) is an ordered product of \(2|m|\) conjugates of \(R^{\pm1}\).

Fix the order and define

\[
 U_{n,m}=t(R')^nK_m.
\tag{1.1}
\]

Starting with the compressed relator \(B_0=z^{-1}xt\), first multiply by
\((R')^n\), then by the displayed conjugate factorization of \(K_m\),
restoring \(R\) after every temporary conjugation or inversion.  This is a
literal signed AC sequence and gives

\[
 B_{n,m}=z^{-1}xU_{n,m}.
\tag{1.2}
\]

Restore the original power relator using the defining relator
\(D=t^{-1}zxz^{-1}\), and remove \(z\) through

\[
 z=e_{n,m}:=xU_{n,m}.
\]

The rank-two endpoint is

\[
 P_{n,m}=
\left(
x^3e_{n,m}x^{-4}e_{n,m}^{-1},\
t^{-1}e_{n,m}xe_{n,m}^{-1}
\right).
\tag{1.3}
\]

Therefore

\[
\mathrm{AK}(3)\sim_{\mathrm{st}}P_{n,m}
\qquad(n,m\in\mathbb Z).
\tag{1.4}
\]

The order in (1.1) is part of the theorem.  Reversing the two consequence
factors gives a different family.

## 2. Exact block form off the coordinate axes

Assume \(n\ne0\) and \(m\ne0\).  Define the freely reduced corridor

\[
 S_n=\operatorname{red}\!\left(t(R')^nt^{-1}\right),
\qquad p_m=a^m.
\tag{2.1}
\]

If \(N=|n|\), then

\[
 S_n=
\begin{cases}
 t^{-3}a(t^{-4}a)^{N-1}t^{-1},&n>0,\\
 ta^{-1}(t^4a^{-1})^{N-1}t^3,&n<0.
\end{cases}
\tag{2.2}
\]

In particular,

\[
 |S_n|=7N,\qquad |p_m|=3|m|.
\tag{2.3}
\]

Equation (1.1) reduces exactly to

\[
 U_{n,m}=S_np_mtp_m^{-1}.
\tag{2.4}
\]

Relabel \(t\) as \(y\).  Substitution in (1.3), free reduction, and one
cyclic rotation of the first relator give

\[
\begin{aligned}
 W_{n,m,1}
 &=x^3S_np_myx^{-4}y^{-1}p_m^{-1}S_n^{-1},\\
 W_{n,m,2}
 &=y^{-1}xS_np_m yxy^{-1}p_m^{-1}S_n^{-1}x^{-1}.
\end{aligned}
\tag{2.5}
\]

There is no hidden cancellation in these displayed words.  Their lengths
are

\[
\begin{aligned}
 |W_{n,m,1}|&=14N+6|m|+9,\\
 |W_{n,m,2}|&=14N+6|m|+6.
\end{aligned}
\tag{2.6}
\]

Thus their total length is

\[
 28|n|+12|m|+15.
\tag{2.7}
\]

## 3. All-quadrant Whitehead certificate

Put

\[
 N=|n|\ge1,\qquad M=|m|\ge1.
\]

For the twelve second-kind Whitehead automorphisms in the order

\[
\begin{aligned}
 &y\mapsto yx,\ x^{-1}y,\ x^{-1}yx,\ yx^{-1},\ xy,\ xyx^{-1};\\
 &x\mapsto xy,\ y^{-1}x,\ y^{-1}xy,\ xy^{-1},\ yx,\ yxy^{-1},
\end{aligned}
\tag{3.1}
\]

the exact total-length change of (2.5) has the form

\[
 (d_1,d_2,0,d_2,d_1,0,d_7,d_8,0,d_8,d_7,0).
\tag{3.2}
\]

Direct cancellation in the two blocks of (2.5) gives:

| parameter region | \(d_1\) | \(d_2\) | \(d_7\) | \(d_8\) |
|---|---:|---:|---:|---:|
| \(n>0,\ m\ne0\) | \(8N-5\) | \(16N-3\) | \(12M+4N\) | \(12M+12N+2\) |
| \(n<0,\ m>0\) | \(8N+1\) | \(16N-9\) | \(12M+4N+6\) | \(12M+12N-4\) |
| \(n<0,\ m<0\) | \(8N-7\) | \(16N-1\) | \(12M+4N-2\) | \(12M+12N+4\) |

Every entry is nonnegative for \(N,M\ge1\).  First-kind Whitehead
automorphisms preserve cyclic length.  Whitehead's strict-reduction
theorem for tuples of conjugacy classes therefore proves that (2.5) is
globally Aut(\(F_2\))-minimal in every nonzero quadrant.  The four zero
entries in (3.2) are length-preserving level moves, not hidden descents.

Consequently,

\[
\mu(P_{n,m})=28|n|+12|m|+15
\qquad(nm\ne0).
\tag{3.3}
\]

## 4. Coordinate axes and the complete formula

When \(n=0\), (1.1) is the power-conjugated recovery

\[
 U_{0,m}=a^mta^{-m}.
\]

When \(m=0\), it is the fixed-rotation family

\[
 U_{n,0}=t(R')^n.
\]

Combining the symbolic one-parameter theorems on these axes with (3.3)
gives the full result.

### Theorem 4.1

For all \((n,m)\in\mathbb Z^2\),

\[
\mu(P_{n,m})=
\begin{cases}
 28|n|+12|m|+15,&nm\ne0,\\
 28n-5,&n>0,\ m=0,\\
 28(-n)+15,&n<0,\ m=0,\\
 3m+14,&n=0,\ m>0,\\
 3(-m)+12,&n=0,\ m<0,\\
 14,&n=m=0.
\end{cases}
\tag{4.1}
\]

In particular,

\[
\mu(P_{n,m})\ge14
\]

throughout this entire ordered two-parameter family.  Every genuinely
mixed endpoint has floor at least \(55\).

## 5. Meaning and remaining scope

The two simplest infinite consequence directions do not cancel each
other in the order (1.1).  On the contrary, leaving either coordinate
axis adds a positive linear penalty, and the untransformed endpoint is
already Whitehead-minimal.

This does not classify:

- the reverse order \(tK_m(R')^n\);
- alternating or conjugated interleavings of the individual factors;
- consequences using the defining relator \(D\) nontrivially; or
- recoveries after changing the compressed source relator first.

Those are separate mechanisms.

## 6. Independent replay

`tests/stable_ac/test_mixed_consequence_family.py` checks:

1. the exact signed recovery order in (1.1);
2. every endpoint and the complete piecewise floor formula on a signed
   two-dimensional grid;
3. the block identities (2.1)--(2.5) by rotation-only comparison; and
4. all twelve symbolic Whitehead length changes in every nonzero
   quadrant.

The replay uses no AC graph search.  The finite grid guards transcription;
the displayed word identities and Whitehead theorem prove the result for
all integer pairs.
