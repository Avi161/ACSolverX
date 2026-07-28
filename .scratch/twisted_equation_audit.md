# Audit of the Result 134 residual equation

## Verdict

I found an exact simplification and a reusable obstruction criterion, but no
obstruction and no solution.

Let

\[
H=F(z_0,z_1,z_2,z_3)\rtimes_\Phi\langle t\rangle,
\qquad tft^{-1}=\Phi(f),
\]

and put \(a=qt^{-1}\), \(c=z_0\).  Then equation (106) is equivalent to

\[
\boxed{\text{there exists }h\in H\text{ such that }
       [a,h]=a^{-1}hah^{-1}\text{ is conjugate in }H
       \text{ to }c^{\pm1}.}
\tag{A}
\]

Thus the apparent parameters \(n\) and \(j\) are not independent extra
phenomena: they are respectively the \(t\)-heights of \(h\) and of the
conjugator in \(H\).

## Exact verification

Write elements of \(H\) as pairs \((f,m)=ft^m\), with

\[
(f,m)(g,n)=(f\Phi^m(g),m+n).
\]

For \(h=wt^n\), direct multiplication gives

\[
a^{-1}=(\Phi(q^{-1}),1)
\]

and hence

\[
[a,h]
=\Phi(q^{-1})\Phi(w)\Phi^{n+1}(q)w^{-1}
=C(w,n).
\]

On the other hand, every conjugator in \(H\) has the form \(kt^j\), and

\[
(kt^j)c^\eta(kt^j)^{-1}
=k\Phi^j(c^\eta)k^{-1}.
\]

These two identities prove (A), including the sign and both integer
parameters.

There is also an exact conjugacy-class-product formulation.  If

\([a,h]=sc^\eta s^{-1}\), then

\[
hah^{-1}=a s c^\eta s^{-1}.
\]

Conversely this identity recovers the commutator equation.  Therefore (106)
is equivalent to

\[
\boxed{
\operatorname{Cl}_H(a)\cap
a\operatorname{Cl}_H(c^\eta)\ne\varnothing
\quad\text{for at least one }\eta\in\{\pm1\}.
}
\tag{B}
\]

This is sharper than calling (106) merely a twisted-conjugacy equation: it is
an intersection of an ordinary conjugacy class with a left translate of
another ordinary conjugacy class in the mapping torus.

For fixed \(n,j,\eta\), the original free-group form can equivalently be
written as

\[
\operatorname{TC}_\Phi(\Phi^{n+1}(q))
\cap
\Phi(q)\operatorname{Cl}_F(\Phi^j(z_0^\eta))
\ne\varnothing,
\tag{C}
\]

where

\[
\operatorname{TC}_\Phi(B)
=\{\Phi(w)Bw^{-1}:w\in F\}.
\]

Indeed \(C(w,n)=\Phi(q^{-1})D\), so conjugacy of \(C(w,n)\) to the target
is exactly membership of \(D\) in the second set in (C).

## Finite-quotient obstruction criterion

Formula (B) immediately gives a rigorous certificate format.  It is enough
to find a finite quotient \(\pi:H\to Q\) for which, for both signs,

\[
\operatorname{Cl}_Q(\pi(a))\cap
\pi(a)\operatorname{Cl}_Q(\pi(c)^\eta)=\varnothing.
\tag{D}
\]

Unlike a quotient of the free kernel alone, a quotient of \(H=G_b\) already
incorporates all \(n\) and \(j\), so no separate period bounds are needed.

I checked (D) exhaustively for every permutation representation

\[
G_b=\langle x,y\mid b\rangle\longrightarrow S_d,
\qquad 2\le d\le6,
\]

using

\[
a=\texttt{xxxyxYYYYXY},\qquad
b=\texttt{xyxyXYxyxYXYXyxYXY},\qquad
c=\texttt{yX}.
\]

For every pair \(x,y\in S_d\) satisfying \(b=1\), I formed the actual image
subgroup \(Q=\langle x,y\rangle\), enumerated every

\[
a^{-1}hah^{-1}\quad(h\in Q),
\]

and compared it with both \(Q\)-conjugacy classes of \(c\) and \(c^{-1}\).
The numbers of relator-satisfying ordered pairs were

\[
2,\ 12,\ 96,\ 840,\ 13680
\]

for \(d=2,3,4,5,6\), respectively.  None satisfies (D).  As an independent
non-permutation-family check, all representations into

\[
\mathrm{SL}(2,p),\qquad p=2,3,5,7,
\]

were also exhausted; the respective numbers of relator-satisfying pairs were

\[
12,\ 72,\ 960,\ 4704,
\]

and again none satisfies (D).

These are bounded negative diagnostics only.  They prove neither that all
finite quotients are blind nor that (106) has a solution.

## Most useful next theoretical target

The clean target is now separability of the two sets in (B), not a search for
the three integer/word parameters separately.  There are two honest ways
forward:

1. construct a quotient of \(G_b\) separating
   \(\operatorname{Cl}(a)\) from \(a\operatorname{Cl}(z_0^{\pm1})\); or
2. prove the intersection in (B) nonempty by solving a conjugacy-class-product
   equation in the free-by-cyclic group.

A homogeneous quasimorphism gives another rigorous obstruction format.  If
\(f:H\to\mathbb R\) is homogeneous with defect \(D(f)\), then conjugacy
invariance and the defect inequality give

\[
|f([a,h])|\le D(f).
\]

Consequently any \(f\) with

\[
|f(z_0)|>D(f)
\]

would close the residue.  Equivalently, the coarser sufficient condition
\(\operatorname{scl}_H(z_0)>1/2\) would obstruct even being a single
commutator.  I did not establish such a bound; it is recorded only as a
precise non-nilpotent invariant target.

## Status

- Exact reduction: **proved**.
- Finite-quotient certificate format: **proved**.
- Exhaustive small-quotient diagnostics: **no obstruction found**.
- Explicit free-group or mapping-torus solution: **not found**.
- Resolution of the Result 132 survivor: **open**.
