# Powered endpoint connectors for the old--new forest load

## Status and scope

This note proves a mod-two chain identity for the powered \(P,C,Q\) endpoint
families.  It is a chain-level consequence of the existing endpoint formulas
and injectivity of the boundary map on finite chains in a forest.  It couples
the previously separate \(P\)-ray, \(C\)-connector, and \(Q\)-rectangle
obligations into one outer connector evaluation.  It is useful for the
old--new load calculation, but it is not an independent Andrews--Curtis
result.

The terminal-incidence theorem below evaluates the combined powered
\(P,C,Q\) forest load as \([d=1]\).  It does not evaluate the finite old
terms or positive-chamber covariance, and it proves no period-two lift,
AK(3), stable Andrews--Curtis, or Andrews--Curtis claim.

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

## 4. Exact local forest overlap

Abbreviate \(K_h=K_Q(h)\) and identify a mod-two forest chain with its
collision-aggregated stored-edge support when taking cardinalities.  The
final \(Q\)-increment and (3.7) give

\[
 \boxed{\beta_E=C_Q(d-1)=K_Q(d-1)+K_Q(d)=K_{d-1}+K_d.}
 \tag{4.1}
\]

Its certified collision support has size

\[
 \boxed{
 |\beta_E|
 =|\mathcal S_2|+|\mathcal S_3|+|\mathcal S_4|
 =8+14+14=36.}
 \tag{4.2}
\]

For the long component connector, the exact word lengths are

\[
 |P_1|=|Q_1|=|Q_2|=14,\qquad
 P_*=P_3,\qquad |P_*|=18.
 \tag{4.3}
\]

Because \(C_1=P_1\) and \(C_3=P_3\), its two reduced common-root words are

\[
 W_1=P_1^{\,i+1}Q_1^h,\qquad
 W_3=P_*^{\,i+1}Q_2^h.
 \tag{4.4}
\]

Exact free reduction leaves these concatenations reduced, with

\[
 |W_1|=14(i+1)+14h,\qquad
 |W_3|=18(i+1)+14h.
 \tag{4.5}
\]

The words start with \(\texttt{aB}\) and \(\texttt{aG}\), respectively, so
their common rooted path is exactly the first edge.  Removing that common
edge twice gives

\[
 \boxed{
 |[v_1(h),v_3(h)]|
 =|W_1|+|W_3|-2
 =32(i+1)+28h-2.}
 \tag{4.6}
\]

The transported literal words in (3.8)--(3.10) give the exact short
connector lengths

\[
 |S_w^{(3)}(h)|=2,\qquad
 |S_z^{(3)}(h)|=3,\qquad
 |S_w^{(2)}(h)|=2.
 \tag{4.7}
\]

These three short paths are mutually interior-disjoint.  The first two
leave \(v_3(h)\) through the distinct initial letters \(\texttt a\) and
\(\texttt b\), so a later intersection would create a cycle in the forest;
the \((2,6)\) path lies in the other component.  They are also
interior-disjoint from the long connector.  At \(h=0\), the long path
leaves \(v_3(0)\) in the direction opposite the terminal
\(\texttt G\) of \(W_3\); for \(h>0\), it leaves in the direction opposite
the terminal \(\texttt b\).  The short paths leave through
\(\texttt a\) or positive \(\texttt b\), while the \((2,6)\) path remains
in the other component.  Distinct incident directions in a forest cannot
meet again without producing a cycle.  Thus the only shared endpoint is
the forced \(v_3(h)\) endpoint of the two short paths in its component.

Consequently (3.11) is a support-disjoint sum apart from endpoints, which
do not contribute edge support, and

\[
 \boxed{
 |K_Q(h)|
 =32(i+1)+28h-2+2+3+2
 =32(i+1)+28h+5.}
 \tag{4.8}
\]

Put

\[
 x=|K_d\setminus K_{d-1}|,\qquad
 y=|K_{d-1}\setminus K_d|.
 \tag{4.9}
\]

Equation (4.1), the certified support count (4.2), and the size formula
(4.8) give the ordinary-integer identities

\[
 x+y=36,\qquad
 x-y=|K_d|-|K_{d-1}|=28.
 \tag{4.10}
\]

Hence

\[
 x=32,\qquad y=4.
 \tag{4.11}
\]

The mod-two forest membership pairing is therefore

\[
\begin{aligned}
 \langle K_Q(d),\beta_E\rangle
 &=|K_d\cap(K_d\mathbin{\triangle}K_{d-1})|\pmod2\\
 &=|K_d\setminus K_{d-1}|\pmod2
 =32\pmod2,
\end{aligned}
\]

so

\[
 \boxed{\langle K_Q(d),\beta_E\rangle=0\in\mathbb F_2.}
 \tag{4.12}
\]

Taken alone, this section completely evaluates only the forest-overlap, or
membership, part of the combined powered \(P,C,Q\) outer load.  Its
tie/occurrence term is evaluated in the next section.  The finite old terms,
positive-chamber covariance, the period-two lift, AK(3), stable
Andrews--Curtis, and Andrews--Curtis remain open.

## 5. Exact terminal-incidence theorem

The terminal literal words needed for the outer connector are

\[
\begin{aligned}
 A&=Q_1=\texttt{GaGaGbABaGbbaG},\\
 B&=C=Q_2=\texttt{baGGaGaGbABaGb}.
\end{aligned}
 \tag{5.1}
\]

Let \(A_j,B_j,C_j\) be the vertex reached after the first \(j\) letters of
the corresponding transported terminal copy have been followed under the
anti-homomorphic path convention.  Thus \(A_j\) belongs to the \(A\)-copy,
and \(B_j,C_j\) retain the two distinct transported-copy names even though
\(B=C\) as literal words.  By the same letters \(A,B,C\), also denote the
resulting collision-aggregated mod-two terminal edge chains.

Write the old connectors from \(K_Q(d-1)\) and the new connectors from
\(K_Q(d)\) as

\[
\begin{aligned}
 z^-&=S_z^{(3)}(d-1),& z^+&=S_z^{(3)}(d),\\
 w_3^-&=S_w^{(3)}(d-1),& w_3^+&=S_w^{(3)}(d),\\
 w_2^-&=S_w^{(2)}(d-1),& w_2^+&=S_w^{(2)}(d).
\end{aligned}
 \tag{5.2}
\]

The old \(z^-\) starts at \(B_0\).  Its transported literal word
\(\texttt{baG}\) coincides with terminal \(B\)-edges \(0,1,2\), so those
three edges cancel coefficientwise in
\(\beta_E=K_Q(d-1)+K_Q(d)\).  The connectors
\(z^+,w_3^+,w_2^+\) are the three new short connectors contained in
\(K_Q(d)\).

The collision-aggregated adjacent-source block chains are exactly

\[
\begin{aligned}
 \Pi_1&=A+B+z^-+z^+,\\
 \Pi_2&=B+C+w_3^-+w_3^++w_2^-+w_2^+,\\
 \Pi_3&=B+C,
\end{aligned}
 \tag{5.3}
\]

and the established paired-boundary chains are

\[
 F_2=\Pi_1+\beta_2,\qquad
 G_3=\Pi_3+\beta_3.
 \tag{5.4}
\]

Put \(K=K_Q(d)\) and let \(K_s\) be its slot-\(s\) subchain.  The stored
selectors use the following literal incidence conventions:

- \(t_2\) selects the post-letter vertex for \(\texttt B\) and the
  pre-letter vertex for \(\texttt b\);
- \(h_3\) selects the post-letter vertex for \(\texttt G\) and the
  pre-letter vertex for \(\texttt g\); and
- the \(\bar b_4\) tail coordinate selects the pre-letter vertex for
  \(\texttt A\) and the post-letter vertex for \(\texttt a\).

These rules place the integral family and incidence signs before
collision aggregation and parity reduction.  The established head--tail
boundary identity, applied to \(K\), is

\[
\begin{aligned}
 \langle K,\omega_T\rangle
 ={}&\langle t_2K_2,\partial F_2\rangle
    +\langle h_3K_3,\partial G_3\rangle\\
   &+\langle\partial K_3,\partial\beta_4\rangle
    +\langle\partial K_4,\bar b_4\rangle.
\end{aligned}
 \tag{5.5}
\]

The following four rows audit every remaining parity.  Set brackets such
as \([d=1]\) and \([d>1]\) denote truth indicators, and each displayed
integer total is reduced modulo two only at the end.

First, the slot-two tail-selector row is

\[
\begin{aligned}
 \langle t_2K_2,\partial F_2\rangle
 &=\underbrace{|\{A_5,A_8,A_{10}\}|}_{A:\ 3}
   +\underbrace{|\{B_8,B_{11},B_{13}\}|}_{B/\text{new }z:\ 3}\\
 &=6=0\pmod2.
\end{aligned}
 \tag{5.6}
\]

Second, the slot-three head-selector row is

\[
\begin{aligned}
 \langle h_3K_3,\partial G_3\rangle
 &=\underbrace{5+[d>1]}_{A}
   +\underbrace{7+[d=1]}_{B/\text{new }z/w_3}
   +\underbrace{1}_{\text{component 2 new }w_2}\\
 &=14=0\pmod2.
\end{aligned}
 \tag{5.7}
\]

Here the predecessor of \(A_0\) is the final \(\texttt b\) of \(P_1\)
when \(d=1\), but the final \(\texttt G\) of the preceding \(Q_1\)-copy
when \(d>1\).  The predecessor of \(B_0\) is the final \(\texttt G\) of
\(P_*\) when \(d=1\), but the final \(\texttt b\) of the preceding
\(Q_2\)-copy when \(d>1\).  Since \(d\geq1\),
\([d=1]+[d>1]=1\), which gives the displayed total \(14\).

Third, the slot-three/slot-four boundary-incidence row is

\[
\begin{aligned}
 \langle\partial K_3,\partial\beta_4\rangle
 &=\underbrace{|\{A_1,A_2,A_3,A_4,A_9,A_{13}\}|}_{A:\ 6}\\
 &\quad+\underbrace{|\{B_4,B_5,B_6,B_7,B_{12}\}|}_{B:\ 5}
   +\underbrace{[d=1]}_{\text{old }w_3^-:\ B_0}\\
 &\quad+\underbrace{1+1+1}_{\text{new }z^+,w_3^+,w_2^+}\\
 &=14+[d=1]=[d=1]\pmod2.
\end{aligned}
 \tag{5.8}
\]

In this row the old \(z^-\) cancellation removes the
\(B_1\longrightarrow B_2\) slot-four edge along with the other two initial
\(B\)-edges.  The old \(w_3^-\) contributes \(B_0\) exactly when \(d=1\);
each of \(z^+,w_3^+,w_2^+\) contributes one.

Fourth, the slot-four tail-coordinate row is

\[
\begin{aligned}
 \langle\partial K_4,\bar b_4\rangle
 &=\underbrace{|\{A_2,A_4,A_6,A_9,A_{13}\}|}_{A:\ 5}
   +\underbrace{|\{B_5,B_7,B_9,B_{12}\}|}_{B:\ 4}\\
 &\quad+\underbrace{1+1+1}_{\text{new }z^+,w_3^+,w_2^+}\\
 &=12=0\pmod2.
\end{aligned}
 \tag{5.9}
\]

Substitution of (5.6)--(5.9) into (5.5) proves the exact outer load

\[
 \boxed{\langle K_Q(d),\omega_T\rangle=[d=1].}
 \tag{5.10}
\]

Together with the already proved forest-overlap identity (4.12) and
\(\omega_T=\beta_E+\tau_T\), this also gives

\[
 \boxed{\langle K_Q(d),\tau_T\rangle=[d=1].}
 \tag{5.11}
\]

Pairing the chain telescope (3.16) with \(\omega_T\) therefore closes the
combined powered \(P,C,Q\) forest load:

\[
 \boxed{
 \sum_{h=0}^{i-1}\langle C_P(h),\omega_T\rangle
 +\langle C_C(i),\omega_T\rangle
 +\sum_{h=0}^{d-1}\langle C_Q(h),\omega_T\rangle
 =[d=1].}
 \tag{5.12}
\]

This closes only the combined powered \(P,C,Q\) forest load.  The finite
old fixed, base, and singleton terms, positive-chamber covariance, the
period-two lift, AK(3), stable Andrews--Curtis, and Andrews--Curtis remain
open.

## 6. Cochain loads and the occurrence sweep

For any edge cochain
\(\omega\in C^1(\mathcal T;\mathbb F_2)\), pairing (3.16) with \(\omega\)
gives

\[
 \boxed{
 \sum_{h=0}^{i-1}\langle C_P(h),\omega\rangle
 +\langle C_C(i),\omega\rangle
 +\sum_{h=0}^{d-1}\langle C_Q(h),\omega\rangle
 =\langle K_Q(d),\omega\rangle.}
 \tag{6.1}
\]

Specialize now to the complete collision-aggregated old--new cochain
\(\omega_T=\beta_E+\tau_T\) from the occurrence sweep.  Its slot-four
restriction is the proved coboundary

\[
 \omega_T(E_4(v))=\bar b_4(v)+\bar b_4(tv),
 \tag{6.2}
\]

and its mixed-slot values have the exact occurrence-prefix and
head--tail boundary descriptions already established there.  Formula
(6.1) couples the previous separate powered \(P,C,Q\) program into the
single outer evaluation

\[
 \boxed{
 \sum_{h=0}^{i-1}\langle C_P(h),\omega_T\rangle
 +\langle C_C(i),\omega_T\rangle
 +\sum_{h=0}^{d-1}\langle C_Q(h),\omega_T\rangle
 =\langle K_Q(d),\omega_T\rangle.}
 \tag{6.3}
\]

The terminal-incidence theorem (5.10) evaluates the right-hand side of
(6.3) as \([d=1]\).  This still does not evaluate the finite old fixed,
base, and singleton terms or positive-chamber covariance, and it supplies
no period-two lift, AK(3), stable Andrews--Curtis, or Andrews--Curtis
conclusion.
