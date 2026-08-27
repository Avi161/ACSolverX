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
chain telescope, terminal topology, support count, and forest-membership
pairing needed for its old--new term.  No symmetry with the positive
chamber is asserted or used.

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

## 6. Honest remaining boundary

The following terms are not evaluated here:

1. the inverse tie/occurrence load
   \(\langle\widetilde K(e),\tau^-_e\rangle\);
2. the fixed, base, and singleton old terms at the seam and in the negative
   chamber;
3. the remaining non-slot-zero part of \(L(b^-_{n,e})\);
4. \(Q(b^-_{n,e})\) and the required new--new contributions;
5. the complete target \(J^-_{n,e}=[e=0]\);
6. the diagonal defect and the unary delta identity; and
7. the period-two lift, AK(3), stable Andrews--Curtis, and
   Andrews--Curtis.

The exact chain, topology, and membership identities above make no claim
that any of these remaining terms vanishes.  In particular, this note is
not a nonpositive-chamber covariance proof and contains no AK3 or
Andrews--Curtis conclusion.
