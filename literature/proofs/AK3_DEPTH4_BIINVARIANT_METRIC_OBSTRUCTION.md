# A bi-invariant metric obstruction for 19 AK depth-four classes

## 1. Statement

Put

\[
A=x^3y^{-4},\qquad B=xyxy^{-1}x^{-1}y^{-1}\in F(x,y).
\]

Signed source-leaf provenance associates to a depth-four row a signature

\[
(N,n_A,n_B,c_A,c_B),
\]

where the row is an ordered product of \(n_A\) arbitrary conjugates of
\(A^{\pm1}\) and \(n_B\) arbitrary conjugates of \(B^{\pm1}\), while
\(c_A,c_B\) are the signed source coefficients. Its exponent vector is

\[
(p,q)=(3c_A+c_B,-4c_A-c_B).
\tag{0}
\]

The exact depth-four census has 30 new signatures with three minority
leaves.

**Theorem.** Nineteen of those 30 signatures cannot contain a primitive
row. The eleven signatures not decided here are

\[
\begin{gathered}
(7,3,4,-3,2),\ (7,3,4,-3,4),\ (7,3,4,-1,-2),\\
(7,4,3,-2,-3),\ (8,3,5,-3,1),\ (8,3,5,-3,5),\\
(8,3,5,-1,-1),\ (8,3,5,-1,3),\ (8,5,3,-3,1),\\
(8,5,3,-1,-1),\ (8,5,3,-1,3).
\end{gathered}
\]

The obstruction retains both source relators. It does not factor
through a quotient which kills \(A\) or \(B\).

## 2. The metric leaf-budget lemma

For a unit quaternion \(Q\in SU(2)\), let

\[
d(Q)=\arccos(\operatorname{Re}Q)\in[0,\pi].
\]

This is the geodesic distance from \(1\) in the standard bi-invariant
metric on \(SU(2)\). Consequently

\[
d(PQ)\le d(P)+d(Q),\qquad
d(GQG^{-1})=d(Q),\qquad d(Q^{-1})=d(Q).
\tag{1}
\]

Let \(\rho:F(x,y)\to SU(2)\) be any homomorphism. If a row with
signature \((N,n_A,n_B,c_A,c_B)\) were primitive, the rank-two primitive
classification and (0) would make it conjugate, up to inversion, to the
signed Christoffel word \(W_{3c_A+c_B,-4c_A-c_B}\). Applying (1) to its
source-leaf factorization would give the necessary inequality

\[
d(\rho(W_{3c_A+c_B,-4c_A-c_B}))
\le n_A d(\rho(A))+n_B d(\rho(B)).
\tag{2}
\]

Thus one representation violating (2) excludes every ordering,
orientation, and choice of the source-leaf conjugators at once.

## 3. Rational quaternion family

For rational \(t,u,m,n\) satisfying \(m^2+n^2=1\), define

\[
X=\left(\frac{1-t^2}{1+t^2},0,0,\frac{2t}{1+t^2}\right),
\]

\[
Y=\left(\frac{1-u^2}{1+u^2},
         \frac{2un}{1+u^2},0,
         \frac{2um}{1+u^2}\right).
\tag{3}
\]

Both are unit quaternions and every word in \(X,Y\) has rational
coordinates. Three choices suffice:

| identifier | \(t\) | \(u\) | \(m\) | \(n\) |
|---|---:|---:|---:|---:|
| P | \(8/15\) | \(5/13\) | \(312/313\) | \(25/313\) |
| M | \(1/2\) | \(7/15\) | \(-20/101\) | \(99/101\) |
| N | \(15/26\) | \(12/29\) | \(-28/197\) | \(195/197\) |

The P, M, and N representations certify respectively 5, 5, and 9
signatures.

## 4. Exact angle bounds

No floating-point approximation is used in the certificate. Suppose a
source image has scalar part \(s>0\), and put

\[
R=\frac{1-s^2}{s^2}.
\]

All source values below satisfy \(0\le R\le1\). Its angle is
\(\arctan\sqrt R\), and the alternating series gives

\[
\arccos s
<\sqrt R\left(1-\frac R3+\frac{R^2}{5}\right).
\tag{4}
\]

For \(S=10^{15}\), set

\[
U(R)=\frac{\lfloor S\sqrt R\rfloor+1}{S}.
\]

The integer in this formula is obtained by an exact integer square root,
so (4) remains a strict rational upper bound after replacing \(\sqrt R\)
by \(U(R)\).

Let \(w\) be the scalar part of the target image. The classical bound
\(\pi>333/106\) and \(\arcsin z\ge z\) give, for \(w<0\),

\[
\arccos w=\frac\pi2+\arcsin(-w)>
\frac{333}{212}-w.
\tag{5}
\]

For \(0\le w<1\), use
\(\arcsin w\le w/\sqrt{1-w^2}\) instead:

\[
\arccos w>
\frac{333}{212}
-U\!\left(\frac{w^2}{1-w^2}\right).
\tag{6}
\]

Equations (3)--(6) turn the reverse of (2) into a comparison of two
explicit rational numbers.

## 5. Certificate allocation

The representation identifiers assigned to the 19 signatures are:

    P: (7,3,4,-3,-4) (7,4,3,-4,-3) (8,3,5,-3,-5)
       (8,5,3,-5,-3) (8,5,3,-5,3)

    M: (7,3,4,-3,-2) (7,3,4,-1,2) (8,3,5,-3,-1)
       (8,3,5,-1,-3) (8,3,5,-1,1)

    N: (7,3,4,-1,0) (7,4,3,-4,3) (7,4,3,-2,-1)
       (7,4,3,-2,1) (7,4,3,-2,3) (7,4,3,0,-1)
       (8,5,3,-3,-1) (8,5,3,-1,-3) (8,5,3,-1,1)

For every listed signature the exact rational target lower bound minus
the exact rational weighted source upper bound is greater than \(1/100\).
The smallest margin occurs for \((7,4,3,0,-1)\); it is greater than
\(0.0256\), but the proof test compares its full rational value with
\(1/100\).

The independently replayable certificate is
experiments/stable_ac/depth4_metric_certificates.py; its regression test
is tests/stable_ac/test_ak_depth_four_metric_barrier.py.

## 6. Scope

Together with the 24 low-minority free-product certificates, this proves
nonprimitivity for 43 of the 54 new depth-four source-leaf classes. It
does not by itself prove original-source depth-four closure. The eleven
signatures displayed in Section 1 still require a different exact
argument. In particular, all six survivors of the earlier
majority-killing \(SU(2)\) screen remain unresolved here.
