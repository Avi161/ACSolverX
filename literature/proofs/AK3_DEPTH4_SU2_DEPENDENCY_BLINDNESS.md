# Scalar SU(2) dependency blindness at the hardest AK depth-four class

## 1. Scope

For the unresolved signature \((8,3,5,-3,5)\), the exact row recurrence is

\[
\begin{aligned}
R&=A h_0B^{-1}h_0^{-1},\\
S&=B h_1R^{-1}h_1^{-1},\\
U&=R h_2S^{-1}h_2^{-1},\\
Z&=U^{-1}h_3Sh_3^{-1}.
\end{aligned}
\tag{1}
\]

This note proves that the local shared-angle relaxation (4), which retains
the repeated scalar angle variables but forgets simultaneous matrix
compatibility, gives no stronger obstruction than the already exhausted
flat product of three \(A\)-classes and five \(B\)-classes.

The conclusion concerns scalar conjugacy angles only. It does not identify
the axes of repeated matrices, restrict conjugators to the image of the
free group, or solve (1).

## 2. The rank-one class hypergroup

Normalize every quaternion angle by \(\pi\). Thus all angles lie in
\([0,1]\). Write

\[
\Delta(x,y,z)
\]

when the \(SU(2)\) class of angle \(z\) occurs in the product of the classes
of angles \(x,y\). The standard two-class formula is

\[
|x-y|\le z\le\min(x+y,2-x-y).
\tag{2}
\]

Equivalently, \(\Delta(x,y,z)\) is cut out by four linear inequalities:

\[
\begin{array}{rcl}
P(x,y,z):&x+y+z&\le2,\\
Z(x,y,z):&-x-y+z&\le0,\\
Y(x,y,z):&-x+y-z&\le0,\\
X(x,y,z):&x-y-z&\le0.
\end{array}
\tag{3}
\]

Let \(a,b,t\) be the angles of the images of \(A,B,T\), where
\(T=\operatorname{Chr}(-4,7)\). Forgetting axes but retaining the shared
intermediate angles gives

\[
\Delta(a,b,r),\qquad
\Delta(b,r,s),\qquad
\Delta(r,s,u),\qquad
\Delta(u,s,t).
\tag{4}
\]

Denote the projection of this polytope to \((a,b,t)\) by \(D\).

## 3. The flat three-A, five-B interval

The flat product contains angle \(t\) precisely when the identity class is
in the product with angle multiset

\[
(a,a,a,b,b,b,b,b,t).
\]

Successive elimination using (3) gives the rank-one polygon inequalities

\[
(2i-3)a+(2j-5)b+(2k-1)t\le i+j+k-1,
\tag{5}
\]

where

\[
0\le i\le3,\qquad 0\le j\le5,\qquad
k\in\{0,1\},\qquad i+j+k\ \hbox{is odd}.
\]

There are 24 rows. Formula (5) follows inductively from (3): eliminating one
intermediate product angle pairs its positive and negative coefficient rows,
and adjoining a new leaf switches the subset parity.

On the unit cube these 24 rows are equivalent to four non-box facets:

\[
\begin{aligned}
-3a-5b+t&\le0,\\
 3a-5b-t&\le2,\\
-3a+5b-t&\le4,\\
 3a+5b+t&\le8.
\end{aligned}
\tag{6}
\]

Each row of (6) is one of (5). Conversely, the polytope defined by (6) and
the unit-cube bounds has exactly the twelve vertices

\[
\begin{array}{c|c|c}
a&b&t\\ \hline
0&0&0\\
0&1/5&1\\
0&4/5&0\\
0&1&1\\
1/3&0&1\\
1/3&1&0\\
2/3&0&0\\
2/3&1&1\\
1&0&1\\
1&1/5&0\\
1&4/5&1\\
1&1&0.
\end{array}
\tag{7}
\]

Substitution of these vertices into all 24 rows (5) verifies every row.
Since a bounded polytope is the convex hull of its vertices, (6) implies all
of (5). The exact common flat interval is therefore

\[
\begin{aligned}
L(a,b)&=\max(0,\,3a-5b-2,\,5b-3a-4),\\
U(a,b)&=\min(1,\,3a+5b,\,8-3a-5b).
\end{aligned}
\tag{8}
\]

## 4. The dependency projection has the same facets

Label the four occurrences of \(\Delta\) in (4) by subscripts
\(1,2,3,4\). Every row in (6) is a nonnegative integer combination of
the sixteen stage inequalities:

\[
\begin{array}{c|l}
\text{facet}&\text{exact combination}\\ \hline
-3a-5b+t\le0&3Z_1+2Z_2+Z_3+Z_4,\\
 3a-5b-t\le2&3X_1+2Y_2+P_3+Y_4,\\
-3a+5b-t\le4&3Y_1+2P_2+X_3+X_4,\\
 3a+5b+t\le8&3P_1+2X_2+Y_3+P_4.
\end{array}
\tag{9}
\]

In each line the coefficients of \(r,s,u\) cancel exactly. Hence

\[
D\subseteq P,
\tag{10}
\]

where \(P\) is the flat polytope defined by (6) and the box bounds.

For the reverse containment, lift the twelve vertices (7) to:

\[
\begin{array}{ccc|ccc}
a&b&t&r&s&u\\ \hline
0&0&0&0&0&0\\
0&1/5&1&1/5&2/5&3/5\\
0&4/5&0&4/5&2/5&2/5\\
0&1&1&1&0&1\\
1/3&0&1&1/3&1/3&2/3\\
1/3&1&0&2/3&1/3&1/3\\
2/3&0&0&2/3&2/3&2/3\\
2/3&1&1&1/3&2/3&1/3\\
1&0&1&1&1&0\\
1&1/5&0&4/5&3/5&3/5\\
1&4/5&1&1/5&3/5&2/5\\
1&1&0&0&1&1.
\end{array}
\tag{11}
\]

Direct substitution proves that every row satisfies all four triangle
systems (4). The dependency polytope and its projection are convex, so the
lifts of all vertices imply

\[
P\subseteq D.
\tag{12}
\]

Combining (10) and (12) gives the exact equality

\[
\boxed{D=P}.
\tag{13}
\]

Thus the shared-angle recurrence realizes the whole flat product interval
(8).

In unnormalized angles, the interval is

\[
\begin{aligned}
L_\pi(a,b)&=\max(0,\,3a-5b-2\pi,\,5b-3a-4\pi),\\
U_\pi(a,b)&=\min(\pi,\,3a+5b,\,8\pi-3a-5b).
\end{aligned}
\tag{14}
\]

## 5. Consequence for the AK overlap

There is an exact connected flat fatgraph whose boundary is

\[
T+3A+5B^{-1}.
\]

Equivalently, \(T\) is a product of three conjugates of \(A^{-1}\) and five
conjugates of \(B\) in the free group. Under every representation to
\(SU(2)\), its angle therefore lies in the flat interval (8). Equality
(13) proves that the same angle always passes the dependency recurrence
(4).

Consequently, within the scalar relaxation (4), no obstruction using only
the six angle variables and the four local class-product constraints can
close this class. This does not rule out additional scalar relations obtained
by first enforcing simultaneous matrix compatibility and then eliminating
axes, mixed traces, or restrictions imposed by the actual image subgroup.

The exact rational replay is

\[
\texttt{experiments/stable\_ac/depth4\_su2\_dependency\_certificate.py}.
\]

It verifies all 24 polygon rows, the raw dependency elimination counts
\(28,32,60,278\), the four combinations (9), the complete vertex set (7),
and all lifts (11).

The signature, source depth four, and the Andrews--Curtis conjecture remain
open.
