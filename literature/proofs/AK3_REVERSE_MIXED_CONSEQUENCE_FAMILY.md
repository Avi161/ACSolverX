# The reverse-ordered mixed-consequence family for AK(3)

Date: 2026-07-24

Status: the stable construction and complete Aut(\(F_2\))-floor formula
are **PROVEN** for every \((n,m)\in\mathbb Z^2\).

## 1. Reverse the two retained consequences

At the \(k=1\) compression root, put

\[
 a=x^3,\qquad R=at^{-4},\qquad R'=t^{-4}a,
\]

and

\[
 K_m=t^{-1}a^mta^{-m}.
\]

The forward-ordered theorem treated \(t(R')^nK_m\).  Here fix the reverse
order

\[
 \widehat U_{n,m}=tK_m(R')^n
 =a^mta^{-m}(R')^n.
\tag{1.1}
\]

The factor \(K_m\) is an ordered product of \(2|m|\) conjugates of the
retained relator \(R^{\pm1}\), and \(R'\) is a cyclic rotation of \(R\).
Starting from \(B_0=z^{-1}xt\), multiply first by the conjugate
factorization of \(K_m\), then by \((R')^n\), restoring \(R\) after each
temporary signed conjugation.  The resulting relator is

\[
 \widehat B_{n,m}=z^{-1}x\widehat U_{n,m}.
\tag{1.2}
\]

Restore the original power relator with the defining relator
\(D=t^{-1}zxz^{-1}\), and remove \(z\) through

\[
 z=\widehat e_{n,m}:=x\widehat U_{n,m}.
\]

This gives the stable endpoint

\[
 \widehat P_{n,m}=
\left(
x^3\widehat e_{n,m}x^{-4}\widehat e_{n,m}^{-1},\
t^{-1}\widehat e_{n,m}x\widehat e_{n,m}^{-1}
\right)
\tag{1.3}
\]

and proves

\[
\mathrm{AK}(3)\sim_{\mathrm{st}}\widehat P_{n,m}
\qquad(n,m\in\mathbb Z).
\tag{1.4}
\]

## 2. Exact reduction scaffold

Relabel \(t\) as \(y\), put

\[
 N=|n|,\qquad M=|m|,\qquad p_m=x^{3m},
\]

and write

\[
 q_n=(y^{-4}x^3)^n=
\begin{cases}
 (y^{-4}x^3)^N,&n>0,\\
 (x^{-3}y^4)^N,&n<0.
\end{cases}
\tag{2.1}
\]

For \(nm\ne0\),

\[
 \widehat e_{n,m}
 =\operatorname{red}\!\left(xp_my p_m^{-1}q_n\right).
\tag{2.2}
\]

More explicitly, write the reduced word uniquely as

\[
 \widehat e_{n,m}=x^\pi d x^\sigma,
\tag{2.3}
\]

where \(d\) begins and ends in \(y^{\pm1}\).  The exact blocks are:

| parameter region | \(\pi\) | \(d\) | \(\sigma\) | \(|d|\) |
|---|---:|---|---:|---:|
| \(n>0,\ m\ne0\) | \(3m+1\) | \(yx^{-3m}(y^{-4}x^3)^{N-1}y^{-4}\) | \(3\) | \(7N+3M-2\) |
| \(n<0,\ m\ne-1\) | \(3m+1\) | \(yx^{-3(m+1)}y^4(x^{-3}y^4)^{N-1}\) | \(0\) | \(7N+3|m+1|-2\) |
| \(n<0,\ m=-1\) | \(-2\) | \(y^5(x^{-3}y^4)^{N-1}\) | \(0\) | \(7N-2\) |

The last row is where the middle \(x\)-block vanishes and two adjacent
\(y\)-blocks merge.

The terminal \(x^\sigma\)-block cancels completely from both endpoint
relators.  Before cyclic reduction they become

\[
\begin{aligned}
 \widehat r_1
 &=x^{\pi+3}d x^{-4}d^{-1}x^{-\pi},\\
 \widehat r_2
 &=y^{-1}x^\pi d x d^{-1}x^{-\pi}.
\end{aligned}
\tag{2.4}
\]

The first word is cyclically conjugate to

\[
 x^3d x^{-4}d^{-1}.
\tag{2.5}
\]

Thus

\[
 |\widehat r_1|_{\rm cyc}+|\widehat r_2|_{\rm cyc}
 =4|d|+2|\pi|+9.
\tag{2.6}
\]

Substituting the three rows above gives:

| parameter region | \(|\widehat W_1|\) | \(|\widehat W_2|\) | total |
|---|---:|---:|---:|
| \(n>0,\ m>0\) | \(14N+6M+3\) | \(14N+12M\) | \(28N+18M+3\) |
| \(n>0,\ m<0\) | \(14N+6M+3\) | \(14N+12M-4\) | \(28N+18M-1\) |
| \(n<0,\ m>0\) | \(14N+6M+9\) | \(14N+12M+6\) | \(28N+18M+15\) |
| \(n<0,\ m<0\) | \(14N+6M-3\) | \(14N+12M-10\) | \(28N+18M-13\) |

These are literal cyclically reduced lengths, not fitted numerical data.

## 3. Complete Whitehead table

Use the twelve second-kind Whitehead automorphisms in the order

\[
\begin{aligned}
 &y\mapsto yx,\ x^{-1}y,\ x^{-1}yx,\ yx^{-1},\ xy,\ xyx^{-1};\\
 &x\mapsto xy,\ y^{-1}x,\ y^{-1}xy,\ xy^{-1},\ yx,\ yxy^{-1}.
\end{aligned}
\tag{3.1}
\]

For every \(nm\ne0\), the total-length change of (2.4) is

\[
 (d_1,d_2,0,d_2,d_1,0,d_7,d_8,0,d_8,d_7,0).
\tag{3.2}
\]

Exact boundary counting gives the following values:

| parameter region | \(d_1\) | \(d_2\) | \(d_7\) | \(d_8\) |
|---|---:|---:|---:|---:|
| \(n>0,\ m>0\) | \(8N+5\) | \(16N-5\) | \(18M+4N-2\) | \(18M+12N-12\) |
| \(n>0,\ m<0\) | \(8N+3\) | \(16N-3\) | \(18M+4N-8\) | \(18M+12N-14\) |
| \(n<0,\ m>0\) | \(8N+1\) | \(16N-1\) | \(18M+4N+6\) | \(18M+12N+4\) |
| \(n<0,\ m=-1\) | \(8N+7\) | \(16N+1\) | \(4N+2\) | \(12N-4\) |
| \(n<0,\ m\le-2\) | \(8N+7\) | \(16N-7\) | \(18M+4N-16\) | \(18M+12N-30\) |

The \(m=-1\) row is a genuine boundary-cancellation stratum and must not
be extrapolated from \(M\ge2\).

Every entry is nonnegative on its stated domain.  The smallest
right-hand side in the final row occurs at \(N=1,M=2\) and is still
positive.  First-kind Whitehead maps preserve cyclic length, so
Whitehead's strict-reduction theorem for tuples of conjugacy classes
proves that (2.4) is already globally Aut(\(F_2\))-minimal.

## 4. Complete floor formula

On \(n=0\), this family is the power-conjugated recovery
\(a^mta^{-m}\).  On \(m=0\), it is the fixed-rotation family
\(t(R')^n\).  Combining those axis theorems with Sections 2--3 gives:

### Theorem 4.1

\[
\mu(\widehat P_{n,m})=
\begin{cases}
 28|n|+18|m|+3,&n>0,\ m>0,\\
 28|n|+18|m|-1,&n>0,\ m<0,\\
 28|n|+18|m|+15,&n<0,\ m>0,\\
 28|n|+18|m|-13,&n<0,\ m<0,\\
 28n-5,&n>0,\ m=0,\\
 28(-n)+15,&n<0,\ m=0,\\
 3m+14,&n=0,\ m>0,\\
 3(-m)+12,&n=0,\ m<0,\\
 14,&n=m=0.
\end{cases}
\tag{4.1}
\]

Thus

\[
\mu(\widehat P_{n,m})\ge14
\]

for all integer parameters.  The smallest genuinely mixed endpoint is
the \(n=m=-1\) case of floor \(33\).

## 5. Consequence

The two elementary consequence directions fail to approach floor \(12\)
in either collected order:

- \(t(R')^nK_m\) has mixed floor \(28|n|+12|m|+15\);
- \(tK_m(R')^n\) has the quadrant-dependent floors in (4.1).

Order matters, but neither order creates a cancellation corridor toward a
classical solution.  A new recovery in this source-relator sector must go
beyond concatenating these two exact blocks in either displayed order.
Unclassified possibilities include other rotations or conjugates of
\(R\), inverse or conjugated whole blocks, and interleavings of individual
factors.

## 6. Independent replay

`tests/stable_ac/test_reverse_mixed_consequence_family.py` checks:

1. the literal factor order in (1.1);
2. the complete piecewise floor formula on a signed
   two-dimensional grid;
3. both relator lengths in every nonzero quadrant; and
4. all twelve Whitehead changes, including the exceptional
   \(n<0,m=-1\) stratum.

The replay uses no AC graph search.  The finite grid guards transcription;
the exact boundary counts and Whitehead theorem prove the result for all
integer pairs.
