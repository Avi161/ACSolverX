# Inverse-\(Q\) powered connectors in the nonpositive chamber

## Status and scope

Let

\[
 e=j-i=-d\geq0,\qquad n=i\geq0.
 \tag{0.1}
\]

If \(A_{ij}\) denotes the complete collision-aggregated endpoint activity,
including the fixed tokens, define

\[
 A^-_{n,e}:=A_{n,n+e},
 \qquad
 b^-_{n,e}:=A^-_{n,e}+A^-_{n,e+1}.
 \tag{0.2}
\]

The corresponding \(j\)-edge bit is

\[
\begin{aligned}
 J^-_{n,e}
 &:=\Phi(A^-_{n,e+1})+\Phi(A^-_{n,e})\\
 &=L(b^-_{n,e})
   +\mathbb B(A^-_{n,e},b^-_{n,e})
   +Q(b^-_{n,e}).
\end{aligned}
 \tag{0.3}
\]

The desired nonpositive-chamber edge law would be

\[
 J^-_{n,e}=[e=0].
 \tag{0.4}
\]

This note does not prove (0.4).  It proves the exact inverse-\(Q\) powered
chain telescope, terminal topology, support count, and complete old--new
pairing

\[
 \boxed{
 \mathbb B(A^-_{n,e},b^-_{n,e})
 =1+[e=0]=[e\geq1].}
 \tag{0.5}
\]

No symmetry with the positive chamber is asserted or used.  The remaining
raw and new--new terms in (0.3) are not evaluated here.

All chains are collision-aggregated in the common stored-edge basis.
Integral family and incidence signs are placed before reduction modulo two.

## 1. Inverse endpoints and chain telescope

For \(\nu=1,\ldots,6\), put

\[
 W^-_\nu(n,e)
 :=\operatorname{red}(P_\nu^nC_\nu Q_\nu^{-e})
 \tag{1.1}
\]

and

\[
 \widetilde v_\nu(e)
 :=\operatorname{cvert}
   (q_\nu^{-e}c_\nu p_\nu^n r_\nu).
 \tag{1.2}
\]

The product in (1.2) is formed in the displayed order before the single
final canonicalization.  The literal forest word in (1.1) is evaluated
under the established anti-homomorphic path convention.

Define the inverse-\(Q\) increment

\[
 \widetilde C_Q(e)
 :=\sum_{\nu=1}^6
   [\widetilde v_\nu(e),\widetilde v_\nu(e+1)]
 \tag{1.3}
\]

and the two-component connector

\[
\boxed{
\begin{aligned}
 \widetilde K(e)
 :={}&[\widetilde v_1(e),\widetilde v_3(e)]
     +[\widetilde v_3(e),\widetilde v_4(e)]\\
    &+[\widetilde v_3(e),\widetilde v_5(e)]
     +[\widetilde v_2(e),\widetilde v_6(e)].
\end{aligned}}
 \tag{1.4}
\]

The families \(\{1,3,4,5\}\) lie in the
\(\texttt{ct}\)-component and \(\{2,6\}\) lie in the
\(\mathrm{eps}\)-component, so every displayed path is defined.

The boundary of \(\widetilde K(e)\) is

\[
 \partial\widetilde K(e)
 =\sum_{\nu=1}^6\delta_{\widetilde v_\nu(e)}.
 \tag{1.5}
\]

Therefore

\[
 \partial\widetilde C_Q(e)
 =\partial\bigl(\widetilde K(e)+\widetilde K(e+1)\bigr).
 \tag{1.6}
\]

The difference is a finite cycle in a forest and hence is zero.  Thus
finite-boundary injectivity proves

\[
 \boxed{
 \widetilde C_Q(e)=\widetilde K(e)+\widetilde K(e+1).}
 \tag{1.7}
\]

At the seam,

\[
 \boxed{\widetilde K(0)=K_Q(0),}
 \tag{1.8}
\]

because both sides use the same six endpoints
\(\operatorname{cvert}(c_\nu p_\nu^n r_\nu)\).  The established
\(P/C\) connector identities give

\[
 \sum_{h=0}^{n-1}C_P(h)+C_C(n)=K_Q(0)=\widetilde K(0),
 \tag{1.9}
\]

with an empty \(P\)-sum when \(n=0\).  Summing (1.7) for
\(0\leq h<e\) and using (1.9) yields the total powered old chain

\[
\boxed{
 \sum_{h=0}^{n-1}C_P(h)+C_C(n)
 +\sum_{h=0}^{e-1}\widetilde C_Q(h)
 =\widetilde K(e).}
 \tag{1.10}
\]

The inverse edge mask is

\[
 \boxed{
 \beta^-_e
 =\widetilde C_Q(e)
 =\widetilde K(e)+\widetilde K(e+1).}
 \tag{1.11}
\]

The separate reviewed raw slot-zero theorem is

\[
 \boxed{L((b^-_{n,e})^{(0)})=[e=0].}
 \tag{1.12}
\]

Equation (1.12) is only the slot-zero raw contribution; it is not the
complete value of \(L(b^-_{n,e})\) or \(J^-_{n,e}\).

## 2. Integer-power common blocks

Put

\[
 w=\texttt{aG},\qquad z=\texttt{baG},
 \qquad z^{-1}=\texttt{gAB}.
 \tag{2.1}
\]

For every integer \(Q\)-power, including the inverse powers in (1.1), the
exact common-block identities are

\[
\begin{aligned}
 W^-_4(n,e)&=\operatorname{red}(W^-_3(n,e)w),\\
 W^-_5(n,e)&=\operatorname{red}(W^-_3(n,e)z),\\
 W^-_6(n,e)&=\operatorname{red}(W^-_2(n,e)w).
\end{aligned}
 \tag{2.2}
\]

These are reduced-word identities and transported literal forest paths.
They do not identify \(w\) or \(z\) with a fixed right-deck action on
canonical vertices.

Define the short connector chains

\[
\begin{aligned}
 Z_e&=[\widetilde v_3(e),\widetilde v_5(e)],\\
 W_e&=[\widetilde v_3(e),\widetilde v_4(e)],\\
 U_e&=[\widetilde v_2(e),\widetilde v_6(e)].
\end{aligned}
 \tag{2.3}
\]

Thus \(Z_e,W_e,U_e\) are the transported literal paths
\(z,w,w\), of lengths \(3,2,2\), respectively.

## 3. Exact inverse words and lengths

The two inverse terminal words are

\[
\begin{aligned}
 \mathsf A^-&=Q_1^{-1}
  =\texttt{gABBgAbaBgAgAg},\\
 \mathsf B^-=\mathsf C^-&=Q_2^{-1}=Q_3^{-1}
  =\texttt{BgAbaBgAgAggAB}.
\end{aligned}
 \tag{3.1}
\]

Each has length \(14\).  Since \(C_1=P_1\), \(C_3=P_3=P_*\), and
\(|P_1|=14\), \(|P_*|=18\), the two rooted long words are

\[
\begin{aligned}
 \mathcal W_1^-(n,e)&=P_1^{n+1}(\mathsf A^-)^e,\\
 \mathcal W_3^-(n,e)&=P_*^{n+1}(\mathsf B^-)^e.
\end{aligned}
 \tag{3.2}
\]

They are reduced as displayed and share exactly their first forest edge.
For the long connector

\[
 L_e:=[\widetilde v_1(e),\widetilde v_3(e)]
 \tag{3.3}
\]

this gives

\[
\boxed{
 |L_e|
 =14(n+1)+14e+18(n+1)+14e-2
 =32(n+1)+28e-2.}
 \tag{3.4}
\]

The family-\(2\) word has the exact piecewise length

\[
\boxed{
 |W^-_2(n,e)|
 =\begin{cases}
 14n+19,&e=0,\\
 14n+14e+11,&e\geq1.
 \end{cases}}
 \tag{3.5}
\]

At the first inverse block, the four consecutive inverse-letter pairs
encoded by the terminal suffix \(\texttt{BaGb}\) cancel against the
initial \(\texttt{BgAb}\) of \(\mathsf B^-\), reducing the length by
\(8\).  The remaining inverse-word junctions are reduced, so no further
cancellation occurs.

## 4. Terminal topology and mask support

The exact reduced terminal graph has the following seam change.

- At \(e=0\), \(Z_0\) is edge-disjoint from \(L_0\) apart from their
  common endpoint.
- For every \(e\geq1\), \(Z_e\) is exactly the final three-edge retraced
  subpath of \(L_e\), with transported word
  \(z^{-1}=\texttt{gAB}\) in the long path and \(z=\texttt{baG}\) in the
  short path.

The paths \(W_e\) and \(U_e\) remain edge-disjoint from the surviving long
support and from each other, apart from prescribed endpoints.  Therefore

\[
\widetilde K(e)=L_e+Z_e+W_e+U_e
 \tag{4.1}
\]

has support size

\[
\boxed{
 |\widetilde K(e)|
 =\begin{cases}
 32(n+1)+5,&e=0,\\
 32(n+1)+28e-1,&e\geq1.
 \end{cases}}
 \tag{4.2}
\]

Indeed, at \(e=0\) the four paths are support-disjoint and contribute
\(|L_0|+3+2+2\).  For \(e\geq1\), addition of \(Z_e\) deletes the three
retraced long edges, while \(W_e\) and \(U_e\) add four edges.

Let

\[
\begin{aligned}
 A_e&=[\widetilde v_1(e),\widetilde v_1(e+1)],\\
 B_e&=[\widetilde v_3(e),\widetilde v_3(e+1)]
\end{aligned}
 \tag{4.3}
\]

be the two inverse-word increment paths, carrying
\(\mathsf A^-\) and \(\mathsf B^-\).  Finite-boundary injectivity gives

\[
 L_e+L_{e+1}=A_e+B_e.
 \tag{4.4}
\]

Expanding (1.11) now gives

\[
\boxed{
\begin{aligned}
 \beta^-_e
 ={}&A_e+B_e+Z_e+Z_{e+1}\\
    &+W_e+W_{e+1}+U_e+U_{e+1}.
\end{aligned}}
 \tag{4.5}
\]

The new short path \(Z_{e+1}\) cancels the terminal
\(\texttt{gAB}\) three-edge subpath of \(B_e\).  The old path \(Z_e\)
replaces the same one-edge-per-slot profile.  Every remaining summand in
(4.5) is edge-disjoint after collision aggregation.

Both \(\mathsf A^-\) and \(\mathsf B^-\) have slot profile

\[
 (|\cdot|_2,|\cdot|_3,|\cdot|_4)=(4,5,5).
 \tag{4.6}
\]

Removing the \((1,1,1)\) terminal profile of \(B_e\), replacing it with
the \((1,1,1)\) profile of \(Z_e\), and adding the two old/new copies of
each \(w\)-connector gives

\[
\boxed{
 |\beta^-_e|=36,\qquad
 (|\beta^-_{e,2}|,|\beta^-_{e,3}|,|\beta^-_{e,4}|)
 =(8,14,14).}
 \tag{4.7}
\]

Here the two \(W\)-copies and two \(U\)-copies each add one slot-three and
one slot-four edge; collisions have already been reduced in the common
stored basis.

## 5. Exact forest-membership pairing

Because

\[
 \beta^-_e=\widetilde K(e)+\widetilde K(e+1),
 \tag{5.1}
\]

the membership pairing with the old connector is the parity of the old
support removed at the increment:

\[
 \langle\widetilde K(e),\beta^-_e\rangle
 =|\operatorname{supp}\widetilde K(e)
   \setminus\operatorname{supp}\widetilde K(e+1)|\pmod2.
 \tag{5.2}
\]

At the seam \(e=0\), the removed old support is exactly

\[
 Z_0+W_0+U_0,
 \qquad 3+2+2=7,
 \tag{5.3}
\]

so its parity is one.  For \(e\geq1\), \(Z_e\) is already the retraced
portion deleted from \(\widetilde K(e)\); the removed old support is
exactly

\[
 W_e+U_e,
 \qquad 2+2=4,
 \tag{5.4}
\]

so its parity is zero.  Consequently

\[
 \boxed{
 \langle\widetilde K(e),\beta^-_e\rangle=[e=0].}
 \tag{5.5}
\]

This evaluates only the inverse-\(Q\) forest-overlap, or membership, part
of the total powered old--new load.

## 6. Exact inverse tie and finite-old terms

### 6.1 Terminal nodes and paired boundary chains

Fix \(e\geq0\), and give the three short paths their literal transported
nodes:

\[
\begin{aligned}
 Z_e:\quad&B_0=z_0\longrightarrow z_1\longrightarrow z_2
              \longrightarrow z_3,
              &&\text{word }\texttt{baG},\\
 W_e:\quad&B_0=w_0\longrightarrow w_1\longrightarrow w_2,
              &&\text{word }\texttt{aG},\\
 U_e:\quad&C_0=u_0\longrightarrow u_1\longrightarrow u_2,
              &&\text{word }\texttt{aG}.
\end{aligned}
 \tag{6.1}
\]

Here \(B_0=\widetilde v_3(e)\) and
\(C_0=\widetilde v_2(e)\).  Let \(A,B,C\) denote the three inverse-word
increment chains \(A_e,B_e,C_e\), where

\[
 C_e=[\widetilde v_2(e),\widetilde v_2(e+1)]
 \tag{6.2}
\]

and \(A_e,B_e\) are defined in (4.3).  The exact paired occurrence-block
chains are

\[
\begin{aligned}
 \Pi_1&=A+B+Z_e+Z_{e+1},\\
 \Pi_2&=B+C+W_e+W_{e+1}+U_e+U_{e+1},\\
 \Pi_3&=B+C.
\end{aligned}
 \tag{6.3}
\]

The associated boundary chains are

\[
 F_2=\Pi_1+\beta^-_{e,2},
 \qquad
 G_3=\Pi_3+\beta^-_{e,3}.
 \tag{6.4}
\]

In the collision-aggregated mask, \(Z_{e+1}\) cancels edges
\(11,12,13\) of the \(B\)-increment.  This is the terminal
\(\texttt{gAB}\) cancellation from Section 4.

Put \(K=\widetilde K(e)\), and let \(K_s\) be its slot-\(s\) subchain.
The established head--tail identity is

\[
\begin{aligned}
 \langle K,\omega^-_e\rangle
 ={}&\langle t_2K_2,\partial F_2\rangle
    +\langle h_3K_3,\partial G_3\rangle\\
   &+\langle\partial K_3,\partial\beta^-_{e,4}\rangle
    +\langle\partial K_4,\bar b^-_{e,4}\rangle,
\end{aligned}
 \tag{6.5}
\]

where

\[
 \omega^-_e=\beta^-_e+\tau^-_e.
 \tag{6.6}
\]

### 6.2 Four exact head--tail intersections

The four collision-first intersection rows are:

| pairing row | seam \(e=0\) intersection | stable \(e\geq1\) intersection | integer count | value in \(\mathbb F_2\) |
|:---|:---|:---|:---|:---|
| \(\langle t_2K_2,\partial F_2\rangle\) | \(\varnothing\) | \(\varnothing\) | \(0\) | \(0\) |
| \(\langle h_3K_3,\partial G_3\rangle\) | \(\{B_0,z_3,w_2,u_2\}\) | \(\{w_2,u_2\}\) | \(2+2[e=0]\) | \(0\) |
| \(\langle\partial K_3,\partial\beta^-_{e,4}\rangle\) | \(\{B_0,z_2,w_1,u_1\}\) | \(\{w_1,u_1\}\) | \(2+2[e=0]\) | \(0\) |
| \(\langle\partial K_4,\bar b^-_{e,4}\rangle\) | \(\{z_2,w_1,u_1\}\) | \(\{w_1,u_1\}\) | \(2+[e=0]\) | \([e=0]\) |

In the first row the only seam candidate is \(B_0\), but

\[
 (\partial F_2)(B_0)=0,
 \tag{6.7}
\]

so the intersection is empty.  The seam-only \(B_0\) entries in the second
and third rows arise from the old \(P_*\) terminal uppercase
\(\texttt G\), which is the stored slot-three head at \(B_0\).  They do
not arise from a lowercase terminal letter or from a symmetry convention.

For \(e\geq1\), the retraced \(Z_e\)-segment is absent from the support of
\(\widetilde K(e)\), because it cancels against the final three edges of
the long connector.  It nevertheless remains part of
\(\beta^-_e\) through the expansion (4.5).  This distinction is used in
the third and fourth rows and is why an incidence table for
\(\widetilde K(e)\) cannot replace the mask table for \(\beta^-_e\).

Substitution into (6.5) proves

\[
 \boxed{\langle\widetilde K(e),\omega^-_e\rangle=[e=0].}
 \tag{6.8}
\]

Together with the membership result (5.5),

\[
 \boxed{\langle\widetilde K(e),\beta^-_e\rangle=[e=0],}
 \tag{6.9}
\]

and (6.6), this gives the complete inverse tie/occurrence value

\[
 \boxed{\langle\widetilde K(e),\tau^-_e\rangle=0.}
 \tag{6.10}
\]

### 6.3 Fixed and base exclusion

The exact same-component radius separation is:

| chamber | minimum \(T\)-label radius in \(\texttt{ct}\) | minimum \(T\)-label radius in \(\mathrm{eps}\) | maximum fixed radius in \(\texttt{ct}\) | maximum fixed radius in \(\mathrm{eps}\) | base-core radius |
|:---|---:|---:|---:|---:|---:|
| \(e=0\) | \(14\) | \(19\) | \(9\) | \(6\) | \(2\) |
| \(e\geq1\) | \(28\) | \(25\) | \(9\) | \(6\) | \(2\) |

At \(e=0\), the individual \(C_e\)-path retraces four edges from radius
\(19\) to radius \(15\).  Those edges do not survive collision aggregation:
equation (4.5) shows that the complete \(\mathrm{eps}\)-component mask
support is exactly \(U_e+U_{e+1}\), with slot-zero endpoints included
separately.  Hence its surviving \(T\)-labels have radius at least \(19\)
at \(e=0\) and at least \(25\) for \(e\geq1\).  In the
\(\texttt{ct}\)-component, \(A_e,B_e\) move outward and \(Z_e\) retraces
only the stated three edges, giving the bounds \(14\) and \(28\).

All distances in one comparison are measured in the same source-tree
component.  The lower bounds already allow the exact short-connector
retracing, and collision aggregation can only delete edges.  Hence no fixed
label and no base-core label equals a label of \(T\).

The fixed tokens lie outside the correction blocks, and every complete
earlier occurrence block has even size

\[
 2,\ 8,\ 14,\ 14
 \tag{6.11}
\]

in slots \(0,2,3,4\), respectively.  Thus their chronology ranks and
equal-label ranks both vanish.  The base edges are also disjoint from the
mask support and have no equal-label incident token.  Therefore

\[
 \boxed{E^-_{\rm fixed}=0,\qquad E^-_{\rm base}=0.}
 \tag{6.12}
\]

This is a same-forest radius argument, not a comparison between forest-word
length and canonical quotient-label length.

### 6.4 Corrected singleton mask incidence

The singleton calculation must use incidence in the mask
\(\beta^-_e\), not incidence in \(\widetilde K(e)\).  For all \(e\geq0\),
the complete table is:

| slot-zero occurrence \(o\) | transported label | incident source in \(\beta^-_e\) | equal-label occurrence set | strictly earlier set | count |
|---:|:---|:---|:---|:---|---:|
| \(3\) | \(\widetilde v_1(e)\) | initial \(\texttt g\) of \(\mathsf A^-\) | \(\{9\}\) | \(\varnothing\) | \(0\) |
| \(4\) | \(\widetilde v_5(e)=z_3\) | final \(\texttt G\) of \(Z_e\) | \(\{9\}\) | \(\varnothing\) | \(0\) |
| \(7\) | \(\widetilde v_4(e)=w_2\) | final \(\texttt G\) of \(W_e\) | \(\{9\}\) | \(\varnothing\) | \(0\) |
| \(8\) | \(\widetilde v_6(e)=u_2\) | final \(\texttt G\) of \(U_e\) | \(\{9\}\) | \(\varnothing\) | \(0\) |
| \(11\) | \(\widetilde v_3(e)=B_0\) | initial \(\texttt B\) of \(\mathsf B^-\); initial \(\texttt b\) of \(Z_e\); initial \(\texttt a\) of \(W_e\) | \(\{1,6,15\}\) | \(\{1,6\}\) | \(2\) |
| \(12\) | \(\widetilde v_2(e)=C_0\) | initial \(\texttt a\) of \(U_e\) | \(\{15\}\) | \(\varnothing\) | \(0\) |

The chronology counts are exactly

\[
 (0,0,0,0,2,0),
 \tag{6.13}
\]

so every occurrence-prefix parity vanishes.  Thus the singleton
tie/occurrence contribution is zero.  Its slot-zero membership contribution
is one, and hence

\[
 \boxed{
 E^-_{\rm singleton,tie}=0,\qquad
 E^-_{\rm singleton,membership}=1,\qquad
 E^-_{\rm singleton}=1.}
 \tag{6.14}
\]

For \(e\geq1\), the initial-\(\texttt b\) row at \(B_0\) is still present
because \(Z_e\) is part of \(\beta^-_e\), even though that retraced segment
is absent from \(\widetilde K(e)\).

### 6.5 Complete inverse old--new value

The powered outer load is (6.8), and the three finite-old values are
(6.12) and (6.14).  Therefore

\[
\begin{aligned}
 \mathbb B(A^-_{n,e},b^-_{n,e})
 &=\langle\widetilde K(e),\omega^-_e\rangle
   +E^-_{\rm fixed}+E^-_{\rm base}+E^-_{\rm singleton}\\
 &=[e=0]+0+0+1\\
 &=1+[e=0]=[e\geq1].
\end{aligned}
 \tag{6.15}
\]

This completes the inverse old--new term only.  It is independent of
\(n\), but it is not the complete \(J^-_{n,e}\) edge law.

## 7. Exact joint pure-increment reduction

### 7.1 Equivalent remaining scalar

The pure-increment value is

\[
 \Phi(b^-_{n,e})=L(b^-_{n,e})+Q(b^-_{n,e}).
 \tag{7.1}
\]

By (0.3) and the proved old--new value (6.15), the inverse edge law

\[
 J^-_{n,e}=[e=0]
 \tag{7.2}
\]

is equivalent to

\[
 \boxed{\Phi(b^-_{n,e})=L(b^-_{n,e})+Q(b^-_{n,e})=1.}
 \tag{7.3}
\]

Write

\[
 L(b^-_{n,e})
 =L((b^-_{n,e})^{(0)})+L_{\ne0}(b^-_{n,e}).
 \tag{7.4}
\]

The reviewed slot-zero identity (1.12) then makes (7.3) equivalent to

\[
 \boxed{
 L_{\ne0}(b^-_{n,e})+Q(b^-_{n,e})=[e\geq1].}
 \tag{7.5}
\]

Equations (7.3)--(7.5) are equivalences, not evaluations of the displayed
pure-increment terms.

### 7.2 Exact slot-zero order

Put

\[
 y_e
 =\texttt{cT}\,\Gamma^{-e}\texttt c\,
   \Gamma^{-(n+1)}\texttt t,
 \qquad |\Gamma|=24.
 \tag{7.6}
\]

Exact free reduction gives

\[
 |y_0|=24(n+1)+4,
 \tag{7.7}
\]

and, for \(e\geq1\),

\[
 |y_e|=24(e+n+1)+2.
 \tag{7.8}
\]

Thus \(|y_1|-|y_0|=22\), while
\(|y_{e+1}|-|y_e|=24\) for \(e\geq1\).  Shortlex compares length first, so

\[
 \boxed{y_e<_{\rm sl}y_{e+1}\qquad(e\geq0).}
 \tag{7.9}
\]

Consequently the unique slot-zero coordinate-order predicate is

\[
 \pi_0(e):=[y_e<_{\rm sl}y_{e+1}]=1.
 \tag{7.10}
\]

### 7.3 The 36 nonzero-slot coordinates

For a literal path word \(X=X_0\cdots X_{r-1}\), define

\[
\boxed{
 V(\nu,h;X,k)
 :=\operatorname{cvert}\!\left(
 m_{X_k}E(X_{<k})q_\nu^{-h}c_\nu p_\nu^n r_\nu
 \right).}
 \tag{7.11}
\]

The full displayed product is formed before the final canonicalization.
The multiplier \(m_{X_k}\) and the incidence sign are those of the
authoritative stored-letter table.

Use the abbreviations

\[
\begin{aligned}
 A&=\mathsf A^-=\texttt{gABBgAbaBgAgAg},\\
 B&=\mathsf B^-=\texttt{BgAbaBgAgAggAB},\\
 Z&=\texttt{baG},\qquad W=U=\texttt{aG}.
\end{aligned}
 \tag{7.12}
\]

After collision aggregation, the slot-two coordinate set is

\[
\boxed{
\begin{aligned}
 \mathcal S_2={}&
 \{V(1,e;A,k):k\in\{2,3,6,8\}\}\\
 &{}\cup\{V(3,e;B,k):k\in\{0,3,5\}\}\\
 &{}\cup\{V(3,e;Z,0)\}.
\end{aligned}}
 \tag{7.13}
\]

The slot-three coordinate set is

\[
\boxed{
\begin{aligned}
 \mathcal S_3={}&
 \{V(1,e;A,k):k\in\{0,4,9,11,13\}\}\\
 &{}\cup\{V(3,e;B,k):k\in\{1,6,8,10\}\}\\
 &{}\cup\{V(3,e;Z,2)\}\\
 &{}\cup\{V(3,h;W,1):h\in\{e,e+1\}\}\\
 &{}\cup\{V(2,h;U,1):h\in\{e,e+1\}\}.
\end{aligned}}
 \tag{7.14}
\]

The slot-four coordinate set is

\[
\boxed{
\begin{aligned}
 \mathcal S_4={}&
 \{V(1,e;A,k):k\in\{1,5,7,10,12\}\}\\
 &{}\cup\{V(3,e;B,k):k\in\{2,4,7,9\}\}\\
 &{}\cup\{V(3,e;Z,1)\}\\
 &{}\cup\{V(3,h;W,0):h\in\{e,e+1\}\}\\
 &{}\cup\{V(2,h;U,0):h\in\{e,e+1\}\}.
\end{aligned}}
 \tag{7.15}
\]

The three omitted terminal \(B\)-positions cancel the new \(Z\)-copy:

\[
\begin{aligned}
 V(3,e;B,11)&=V(3,e+1;Z,2),\\
 V(3,e;B,12)&=V(3,e+1;Z,1),\\
 V(3,e;B,13)&=V(3,e+1;Z,0).
\end{aligned}
 \tag{7.16}
\]

They have even collision coefficients and do not belong to
\(\mathcal S_2\sqcup\mathcal S_3\sqcup\mathcal S_4\).  Hence

\[
 |\mathcal S_2|=8,\qquad
 |\mathcal S_3|=|\mathcal S_4|=14.
 \tag{7.17}
\]

Together with the two slot-zero coordinates \(y_e,y_{e+1}\), this gives
exactly \(38\) collision-aggregated module coordinates.

### 7.4 Raw cochain and endpoint potential

For the positive/negative occurrence pair

\[
 (o_2^+,o_2^-)=(1,6),\quad
 (o_3^+,o_3^-)=(9,14),\quad
 (o_4^+,o_4^-)=(15,16),
 \tag{7.18}
\]

define the paired raw bit

\[
 R_s(v)
 :=\rho_{o_s^+}(v)+\rho_{o_s^-}(v)
 \qquad(v\in X).
 \tag{7.19}
\]

Define the raw edge cochain \(\mathcal R\) by

\[
 \mathcal R(E_s(v))=R_s(v).
 \tag{7.20}
\]

The nonzero-slot raw term is exactly the sum of the 36 raw bits
obtained by restricting this global cochain to the current mask support:

\[
\boxed{
 L_{\ne0}(b^-_{n,e})
 =\sum_{s=2}^4\sum_{v\in\mathcal S_s}R_s(v)
 =\langle\beta^-_e,\mathcal R\rangle.}
 \tag{7.21}
\]

Choose one root in each source-tree component and set

\[
 \psi_R(x)
 :=\sum_{f\in[\mathrm{root},x]}\mathcal R(f),
 \qquad
 \Psi_n(h):=\sum_{\nu=1}^6\psi_R(\widetilde v_\nu(h)).
 \tag{7.22}
\]

The forest endpoint identity and
\(\beta^-_e=\widetilde C_Q(e)\) give the exact raw endpoint potential

\[
 \boxed{
 L_{\ne0}(b^-_{n,e})
 =\Psi_n(e)+\Psi_n(e+1).}
 \tag{7.23}
\]

This is a telescoping identity for the raw cochain.  It does not evaluate
either endpoint potential.

### 7.5 Source-tree matching and the joint target

Let \(C_{84}\) be the literal chronological list of decorated tokens of
\(b^-_{n,e}\).  Each of the two slot-zero coordinates has six occurrence
copies, while each of the 36 edge coordinates has its two slot occurrences:

\[
 2\cdot6+36\cdot2=84.
 \tag{7.24}
\]

Let \(M\) be the exact source-tree matching: boundary tokens are paired to
the first and last incident edge events, and consecutive edge events are
paired at their common canonical tree vertex along each unique source-tree
path.  At every integral collision fiber, retain one deterministic
provenance copy exactly when the aggregated coefficient is odd.  Pair all
other copies first across opposite signs and then in same-sign pairs, and
replicate those label-preserving cancellation edges at each occurrence.
The union of the virtual source matching and these cancellation edges is a
disjoint union of alternating cycles and paths.  Discard the cycles and
pair the two actual endpoints of every path.  The resulting collision-first
matching \(M\) is a fixed-point-free, label-preserving perfect matching of
\(C_{84}\).

For two chords of \(M\), call them crossing when their endpoints alternate
in \(C_{84}\), and let

\[
 \operatorname{cr}_{\ne}(C_{84},M)
 \tag{7.25}
\]

be the parity of crossings between chords with distinct canonical labels.
The heterochromatic chord formula gives

\[
 \boxed{
 Q(b^-_{n,e})=\operatorname{cr}_{\ne}(C_{84},M).}
 \tag{7.26}
\]

The slot-zero order predicate \(\pi_0\) is fixed by (7.10).  The remaining
same-occurrence module-order data are exactly the pairwise predicates within
the three nonzero slots:

\[
 \binom82+\binom{14}2+\binom{14}2
 =28+91+91=210.
 \tag{7.27}
\]

No value for those 210 predicates is asserted here.  Combining
(7.5), (7.21), and (7.26) gives the exact joint remaining scalar:

\[
\boxed{
 \sum_{s=2}^4\sum_{v\in\mathcal S_s}R_s(v)
 +\operatorname{cr}_{\ne}(C_{84},M)
 \stackrel{\rm open}{=}[e\geq1].}
 \tag{7.28}
\]

Equation (7.28) is equivalent to \(\Phi(b^-_{n,e})=1\) and hence to the
inverse edge law, but it is not proved.

### 7.6 Why topology does not finish the scalar

The source-tree topology determines the 38 module coordinates, the 84
decorated tokens, the matching \(M\), and the endpoint expression (7.23).
It does not determine the occurrence-wise raw weights \(R_s(v)\) or the
within-occurrence canonical shortlex order represented by the 210
predicates in (7.27).

In particular, the exact counterexample in
period_two_crossing_parity_induction.md, Section 5, equations (5.4)--(5.5),
shows that \(\rho_o(v)\) is not a function only of the central
post-\(\operatorname{cvert}\) label.  A label-preserving source-tree
matching therefore cannot erase the local raw mirrors.  Nor does path
distance determine canonical quotient shortlex.

Consequently

\[
 \boxed{\Phi(b^-_{n,e})=1}
 \tag{7.29}
\]

remains open.

## 8. Honest remaining boundary

The following terms are not evaluated here:

1. the joint raw/crossing identity (7.28), comprising the 36 raw bits and
   210 unresolved same-slot order predicates;
2. equivalently, \(Q(b^-_{n,e})\), the non-slot-zero raw term, and the
   required new--new contribution;
3. the complete target \(J^-_{n,e}=[e=0]\);
4. the diagonal defect and the unary delta identity; and
5. the period-two lift, AK(3), stable Andrews--Curtis, and
   Andrews--Curtis.

The exact chain, topology, tie, finite-old, and joint-reduction identities
above make no claim that the open scalar vanishes.  In particular, this
note is not a complete nonpositive-chamber edge-law proof and contains no
AK3 or Andrews--Curtis conclusion.
