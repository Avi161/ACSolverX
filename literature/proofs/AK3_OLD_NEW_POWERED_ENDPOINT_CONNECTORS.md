# Powered endpoint connectors for the old--new forest load

## Status and scope

This note proves a mod-two chain identity for the powered \(P,C,Q\) endpoint
families.  It is a chain-level consequence of the existing endpoint formulas
and injectivity of the boundary map on finite chains in a forest.  It couples
the previously separate \(P\)-ray, \(C\)-connector, and \(Q\)-rectangle
obligations into one outer connector evaluation.  It is useful for the
old--new load calculation, but it is not an independent Andrews--Curtis
result.

The identity does not evaluate the outer connector, the finite old terms, or
positive-chamber covariance.  It proves no period-two lift, AK(3), stable
Andrews--Curtis, or Andrews--Curtis claim.

## 1. Parameters and endpoint conventions

Work in the positive chamber with

\[
 a=d-1,\qquad n\geq 0,\qquad i=a+n+1,\qquad d=a+1.
 \tag{1.1}
\]

Thus \(a\geq0\), \(d\geq1\), and \(i=d+n\).  Retain the authoritative
endpoint elements

\[
 p_\nu=E(P_\nu),\qquad c_\nu=E(C_\nu),\qquad q_\nu=E(Q_\nu)
 \tag{1.2}
\]

and component roots

\[
 (r_1,\ldots,r_6)
 =(\texttt{ct},\mathrm{eps},\texttt{ct},\texttt{ct},
   \texttt{ct},\mathrm{eps}).
 \tag{1.3}
\]

For \(h\geq0\), define

\[
 u_\nu(h)=\operatorname{cvert}(p_\nu^h r_\nu),
 \qquad
 v_\nu(h)=\operatorname{cvert}
   (q_\nu^h c_\nu p_\nu^i r_\nu).
 \tag{1.4}
\]

The order in (1.4) is literal and essential.  Each full quotient product is
formed in the displayed order before the single final application of
\(\operatorname{cvert}\).  No factor may be separately canonicalized,
parsed as a module vertex, or commuted past another factor.  In particular,
the live anti-homomorphic endpoint map \(E\) has already fixed the product
order in (1.2).

For vertices \(x,y\) in one component of the source forest \(\mathcal T\),
write \([x,y]\) for the unique finite path between them, viewed as a chain in
\(C_1^{\mathrm{fin}}(\mathcal T;\mathbb F_2)\), and put \([x,x]=0\).  Then

\[
 \partial[x,y]=\delta_x+\delta_y.
 \tag{1.5}
\]

Everything below is mod two.  This does not discard the integral placement
rules: the integral source-family coefficients and oriented-letter incidence
signs are placed in the common stored edge basis first, coincident edges are
aggregated integrally, and only then is the resulting chain reduced modulo
two.  The displayed chains are those collision-aggregated parity chains, not
sums of independently active virtual rows.

## 2. Powered chains and outer connectors

Define the three collision-aggregated family chains by

\[
 C_P(h)=\sum_{\nu=1}^6[u_\nu(h),u_\nu(h+1)]
 \qquad(h\geq0),
 \tag{2.1}
\]

where the powered \(P\)-sum uses \(0\leq h<i\), while the adjacent value
\(C_P(i)\) will enter the common-block connector below.

\[
 C_C(i)=\sum_{\nu=1}^6[u_\nu(i),v_\nu(0)],
 \tag{2.2}
\]

and

\[
 C_Q(h)=\sum_{\nu=1}^6[v_\nu(h),v_\nu(h+1)]
 \qquad(0\leq h<d).
 \tag{2.3}
\]

The literal \(P\)-families satisfy

\[
 P_2=P_6,qquad P_3=P_4=P_5,
 \tag{2.4}
\]

and the corresponding roots in (1.3) agree.  Hence

\[
 u_2(h)=u_6(h),qquad
 u_3(h)=u_4(h)=u_5(h).
 \tag{2.5}
\]

Define the \(P\)-connector

\[
 K_P(h)=[u_1(h),u_3(h)].
 \tag{2.6}
\]

The endpoint families indexed by \(\{1,3,4,5\}\) lie in the component
rooted at \(\texttt{ct}\), while those indexed by \(\{2,6\}\) lie in the
component rooted at \(\mathrm{eps}\).  Consequently every path in

\[
 \boxed{
 K_Q(h)=[v_1(h),v_3(h)]+[v_3(h),v_4(h)]
       +[v_3(h),v_5(h)]+[v_2(h),v_6(h)]}
 \tag{2.7}
\]

is defined inside one source-tree component.  This also proves that (2.7)
is a genuine two-component connector: the first three summands connect the
four \(\texttt{ct}\)-component endpoints, and the last connects the two
\(\mathrm{eps}\)-component endpoints.

## 3. Connector identities

The boundary map is injective on finite mod-two edge chains in a forest:

\[
 z\in C_1^{\mathrm{fin}}(\mathcal T;\mathbb F_2),
 \qquad \partial z=0
 \quad\Longrightarrow\quad z=0.
 \tag{3.1}
\]

Indeed, a nonzero finite chain would have a finite nonempty support forest;
a leaf of that support contributes a nonzero boundary coefficient.  This is
the finite-boundary injectivity used below.

From (2.5),

\[
 \partial K_P(h)
 =\delta_{u_1(h)}+\delta_{u_3(h)}
 =\sum_{\nu=1}^6\delta_{u_\nu(h)}.
 \tag{3.2}
\]

The four paths in (2.7) similarly give

\[
 \partial K_Q(h)
 =\sum_{\nu=1}^6\delta_{v_\nu(h)}.
 \tag{3.3}
\]

The three family boundaries are therefore

\[
\begin{aligned}
 \partial C_P(h)
 &=\partial\bigl(K_P(h)+K_P(h+1)\bigr),\\
 \partial C_C(i)
 &=\partial\bigl(K_P(i)+K_Q(0)\bigr),\\
 \partial C_Q(h)
 &=\partial\bigl(K_Q(h)+K_Q(h+1)\bigr).
\end{aligned}
 \tag{3.4}
\]

Each difference between the two sides of the corresponding chain equation
is finite and has zero boundary.  Applying (3.1) proves the pointwise chain
identities

\[
 \boxed{C_P(h)=K_P(h)+K_P(h+1),}
 \tag{3.5}
\]

\[
 \boxed{C_C(i)=K_P(i)+K_Q(0),}
 \tag{3.6}
\]

and

\[
 \boxed{C_Q(h)=K_Q(h)+K_Q(h+1).}
 \tag{3.7}
\]

### 3.1 Common-block short connectors

Take the approved common block and transported literal words

\[
 q=R^{-1},\qquad w=\texttt{aG},\qquad z=\texttt{baG}.
 \tag{3.8}
\]

The exact common-block path identities are

\[
 W_4=\operatorname{red}(W_3w),\qquad
 W_5=\operatorname{red}(W_3z),\qquad
 W_6=\operatorname{red}(W_2w).
 \tag{3.9}
\]

Define

\[
\begin{aligned}
 S_w^{(3)}(h)&=[v_3(h),v_4(h)],\\
 S_z^{(3)}(h)&=[v_3(h),v_5(h)],\\
 S_w^{(2)}(h)&=[v_2(h),v_6(h)].
\end{aligned}
 \tag{3.10}
\]

The chain \(S_w^{(3)}(h)\) is the collision-aggregated mod-two edge chain
of the unique reduced forest path obtained by following the transported
literal word \(w\) under the anti-homomorphic path convention.  The chain
\(S_z^{(3)}(h)\) is the collision-aggregated mod-two edge chain of the
unique reduced forest path obtained by following the transported literal
word \(z\) under the same convention.  The chain \(S_w^{(2)}(h)\) is the
collision-aggregated mod-two edge chain of the unique reduced forest path
obtained by following the transported literal word \(w\) under that
convention.  These statements use transported literal paths; they do not
identify a fixed right-deck action.

With this notation, (2.7) is

\[
 \boxed{
 K_Q(h)=[v_1(h),v_3(h)]
        +S_w^{(3)}(h)+S_z^{(3)}(h)+S_w^{(2)}(h).}
 \tag{3.11}
\]

At \(h=0\), the exact identities \(C_1=P_1\) and \(C_3=P_3\), with the
full products formed before canonicalization as in (1.4), give

\[
 [v_1(0),v_3(0)]
 =[u_1(i+1),u_3(i+1)]
 =K_P(i+1).
 \tag{3.12}
\]

Consequently

\[
 \boxed{
 K_Q(0)=K_P(i+1)
 +S_w^{(3)}(0)+S_z^{(3)}(0)+S_w^{(2)}(0).}
 \tag{3.13}
\]

Combining (3.13) with (3.5)--(3.6), including (3.5) at \(h=i\), yields

\[
 \boxed{
 C_C(i)=C_P(i)
 +S_w^{(3)}(0)+S_z^{(3)}(0)+S_w^{(2)}(0).}
 \tag{3.14}
\]

This isolates one powered long connector plus three fixed-letter short
connectors.  It does not evaluate the \(\omega\)-load of any of them.

At \(h=0\), (1.3) gives

\[
 u_1(0)=\operatorname{cvert}(\texttt{ct})=u_3(0),
\]

so

\[
 \boxed{K_P(0)=0.}
 \tag{3.15}
\]

Summing (3.5) for \(0\leq h<i\), then (3.6), and then (3.7) for
\(0\leq h<d\), all internal connectors occur twice.  Using (3.15) yields
the complete powered-chain telescope

\[
 \boxed{
 \sum_{h=0}^{i-1}C_P(h)+C_C(i)
 +\sum_{h=0}^{d-1}C_Q(h)=K_Q(d).}
 \tag{3.16}
\]

## 4. Cochain loads and the occurrence sweep

For any edge cochain
\(\omega\in C^1(\mathcal T;\mathbb F_2)\), pairing (3.16) with \(\omega\)
gives

\[
 \boxed{
 \sum_{h=0}^{i-1}\langle C_P(h),\omega\rangle
 +\langle C_C(i),\omega\rangle
 +\sum_{h=0}^{d-1}\langle C_Q(h),\omega\rangle
 =\langle K_Q(d),\omega\rangle.}
 \tag{4.1}
\]

Specialize now to the complete collision-aggregated old--new cochain
\(\omega_T=\beta_E+\tau_T\) from the occurrence sweep.  Its slot-four
restriction is the proved coboundary

\[
 \omega_T(E_4(v))=\bar b_4(v)+\bar b_4(tv),
 \tag{4.2}
\]

and its mixed-slot values have the exact occurrence-prefix and
head--tail boundary descriptions already established there.  Formula
(4.1) couples the previous separate powered \(P,C,Q\) program into the
single outer evaluation

\[
 \boxed{
 \sum_{h=0}^{i-1}\langle C_P(h),\omega_T\rangle
 +\langle C_C(i),\omega_T\rangle
 +\sum_{h=0}^{d-1}\langle C_Q(h),\omega_T\rangle
 =\langle K_Q(d),\omega_T\rangle.}
 \tag{4.3}
\]

This connector theorem does not evaluate \(\langle K_Q(d),\omega_T\rangle\).
It also does not evaluate the finite old terms or positive-chamber
covariance, and it supplies no AK(3), stable Andrews--Curtis, or
Andrews--Curtis conclusion.  Its exact contribution is the chain-level
replacement of three powered interior programs by one explicit outer
connector load.
