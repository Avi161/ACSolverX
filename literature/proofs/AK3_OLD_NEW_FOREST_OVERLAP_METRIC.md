# Old--new forest overlap as a boundary metric

## Status and scope

This note closes the abstract evaluation of the local membership term in the
period-two old--new rank potential.  That term is the mod-two coefficient
pairing of two finite chains in the two-component module forest.  A general
tree identity expresses the pairing using only their vertex boundaries and
the tree metric.  It also gives exact telescoping formulas for the two
surviving \(P\)-rays and the three paired \(Q\)-rectangles.

The boundary-distance parities are not evaluated here.  The global
transported-label order \(<_\rho\) is untouched.  Consequently this note
does not prove the endpoint identities, positive-chamber covariance, the
period-two lift, AK(3), stable Andrews--Curtis, or Andrews--Curtis.

## 1. Finite chains in an oriented forest

Let

\[
 \mathcal T=\mathcal T_0\sqcup\mathcal T_1
 \tag{1.1}
\]

be the two Cayley-tree components from the period-two relation-module
factorization.  Fix one orientation of every unoriented edge.  For finite
integral edge chains

\[
 z=\sum_e z_e e,\qquad w=\sum_e w_e e,
 \tag{1.2}
\]

put

\[
 \alpha=\partial z,\qquad \beta=\partial w,
 \qquad
 \langle z,w\rangle_E=\sum_e z_ew_e.
 \tag{1.3}
\]

Both boundaries have coefficient sum zero on each component.  Write
\(d_j\) for the ordinary edge metric on \(\mathcal T_j\).

**Theorem 1.1 (boundary metric for forest overlap).** One has the exact
integer identity

\[
 \boxed{
  2\langle z,w\rangle_E
  =-\sum_{j=0}^1\ \sum_{x,y\in\mathcal T_j}
        \alpha_x\beta_y d_j(x,y).}
 \tag{1.4}
\]

In particular, the double sum is even.  Its value modulo four determines
the edge pairing modulo two.

### Proof

Fix an oriented edge \(e\) in one component and delete its underlying
unoriented edge.  Let \(C_e\) be the side containing the head of \(e\).
Only \(e\) crosses this cut, with positive incidence into \(C_e\), so

\[
 z_e=\sum_{x\in C_e}\alpha_x,
 \qquad
 w_e=\sum_{y\in C_e}\beta_y.
 \tag{1.5}
\]

For vertices \(x,y\) in the component, the contribution of \(e\) to their
distance is

\[
 [e\subseteq[x,y]]
 =[x\in C_e]+[y\in C_e]-2[x,y\in C_e].
 \tag{1.6}
\]

Multiply (1.6) by \(\alpha_x\beta_y\) and sum over \(x,y\).  The first
two terms vanish because the total coefficient of each boundary is zero
on the component.  The final term is
\(-2z_ew_e\) by (1.5).  Summing over all edges and then over the two
components proves (1.4).  All effective sums are finite because the
boundaries are finitely supported.  \(\square\)

The formula is independent of the initially chosen edge orientations:
reversing one edge changes both coefficients at that edge by a sign and
leaves their product fixed.

## 2. Path and four-endpoint forms

For vertices \(x,y\) in the same component, let \([x,y]\) be the oriented
geodesic chain from \(x\) to \(y\).  Its boundary is

\[
 \partial[x,y]=\delta_y-\delta_x.
 \tag{2.1}
\]

Applying Theorem 1.1 with \(z=[x,y]\) gives

\[
 \boxed{
 \langle[x,y],w\rangle_E
 =-\frac12\sum_u\beta_u
       \bigl(d(y,u)-d(x,u)\bigr).}
 \tag{2.2}
\]

The sum is over the component containing \(x,y\).  The numerator is even;
the division takes place in \(\mathbb Z\), before reduction modulo two.

If also \(w=[u,v]\), then (2.2) is the symmetric four-endpoint formula

\[
 \boxed{
 \langle[x,y],[u,v]\rangle_E
 =\frac{d(x,v)+d(y,u)-d(x,u)-d(y,v)}2.}
 \tag{2.3}
\]

Thus signed overlap of two oriented tree paths is a boundary invariant.
Modulo two, orientations disappear and (2.3) is the parity of their common
unoriented edges.

Define the mod-two boundary potential of \(w\) by

\[
 \mu_w(x,y)
 :=\langle[x,y],w\rangle_E\pmod2.
 \tag{2.4}
\]

Finite-boundary injectivity gives the cocycle identity

\[
 \mu_w(x,y)+\mu_w(y,z)=\mu_w(x,z)
 \tag{2.5}
\]

whenever \(x,y,z\) lie in one component.  Equivalently, (2.5) follows
directly by cancelling the two occurrences of every edge in the symmetric
difference of the paths.  Iterating it gives the exact telescope

\[
 \sum_{h=r}^{s-1}\mu_w(x_h,x_{h+1})=\mu_w(x_r,x_s).
 \tag{2.6}
\]

## 3. The exact de-occurrenced edge current

Let \(b=b_{n,d}\), and let

\[
 w_b=(d_2^b,d_3^b,d_4^b)
 \in C_1^{\rm fin}(\mathcal T;\mathbb Z)
 \tag{3.1}
\]

be its unique canonical forest flow under the certified edge-coordinate
identification.  If \(s_b\) is its canonical source, then

\[
 \beta_b:=\partial w_b=-L_0s_b.
 \tag{3.2}
\]

The edge-coordinate convention is load-bearing.  With

\[
 A=t,\qquad B=X_0,\qquad G=U^{-1}t^{-1},
 \tag{3.3}
\]

the stored coordinates are

\[
\begin{array}{c|c|c}
 s&E_s(v)&\partial E_s(v)\\ \hline
 2&Bv\longrightarrow v&(1-B)e_v\\
 3&tv\longrightarrow U^{-1}v=Gtv&(U^{-1}-t)e_v\\
 4&v\longrightarrow tv=Av&(t-1)e_v.
\end{array}
\tag{3.4}
\]

In particular, the \(t\)-shift in the slot-three edge is retained.  The
same table is used for the old current and for \(b\).  Traversing an edge
backwards gives coefficient \(-1\) on the same stored coordinate, not a new
positive coordinate.  Since \(K=\langle A,B,G\rangle\) is free on the
displayed basis and acts freely on the module vertices, the coordinate map
is injective within each labelled edge family, and two distinct slots do
not name one geometric edge.

Every raw module word is first canonicalized in
\(X=Q/\langle c\rangle\), and all integral coefficients at the resulting
coordinate \((s,v)\) are summed before reduction modulo two.  Define the
de-occurrenced parity edge current

\[
 \beta_E:=w_b\pmod2
 =\sum_{s=2}^4\sum_v(d_s^b(v)\bmod2)E_s(v).
 \tag{3.5}
\]

This current does not contain the twelve slot-zero tokens.  Nor is it the
sum of the 72 decorated path-token copies: those copies occur only after
each underlying edge coordinate has been duplicated across its
positive/negative occurrence footprint.  The slot-zero tokens remain in
the full global mask used by the \(\rho\)-ranks and are handled separately
in the non-forest terms.

For \(s\in\{2,3,4\}\), the collision-aggregated module support \(S_s\)
used in the chronology-rank theorem is exactly

\[
 S_s=\{v:d_s^b(v)\equiv1\pmod2\}.
 \tag{3.6}
\]

Indeed, integral coefficients in the canonical \(b\)-flow are aggregated
before parity and occurrence expansion, and the edge-coordinate
identification sends the coordinate \((s,v)\) to that single oriented
forest edge.  The later positive/negative occurrence copies do not change
the underlying coefficient.  The chronology-rank theorem derives the bit
in (3.6) only after retaining the exact paired occurrence footprints,
using the same \(S_s\) at both copies, using the even cardinality of every
\(S_s\), excluding fixed literal tokens from those blocks, and reducing
the occurrence signs after integral aggregation.

## 4. Identification and Green reciprocity

Let \(z=\sum_ez_e e\) be any finite old forest chain and let \(v(e)\) and
\(s(e)\) denote the stored module coordinate of \(e\).  The local
membership summand in the old--new rank formula is

\[
\begin{aligned}
 M_b(z)
 &:=\sum_e(z_e\bmod2)[v(e)\in S_{s(e)}]\\
 &=\sum_e z_e(w_b)_e\pmod2\\
 &=\boxed{\langle z\bmod2,\beta_E\rangle_E
          =\langle z,w_b\rangle_E\pmod2.}
\end{aligned}
\tag{4.1}
\]

If \(\alpha=\partial z\), Theorem 1.1 sharpens this to the boundary-only
formula

\[
 \boxed{
 M_b(z)
 =-\frac12\sum_{j=0}^1\ \sum_{x,y\in\mathcal T_j}
       \alpha_x(\beta_b)_y d_j(x,y)\pmod2.}
 \tag{4.2}
\]

This is the promised identification of the integrated membership
potential.  In particular, for one old path,

\[
 \boxed{
 M_b([x,y])=\mu_{w_b}(x,y)
 =-\frac12\sum_u(\beta_b)_u
       \bigl(d(y,u)-d(x,u)\bigr)\pmod2.}
 \tag{4.3}
\]

Consequently a claimed zero in (4.3) is precisely a divisibility-by-four
claim for the displayed distance numerator.  No support enumeration along
the interior of \([x,y]\) is needed.

There is also an intrinsic mod-two form.  For any finitely supported
component-balanced vertex boundary
\(a\in C_0^{\rm fin}(\mathcal T;\mathbb F_2)\), let
\(D(a)\in C_1^{\rm fin}(\mathcal T;\mathbb F_2)\) be the unique finite
forest chain with boundary \(a\), and put

\[
 G(a,a'):=\langle D(a),D(a')\rangle_E.
 \tag{4.4}
\]

In (4.4)--(4.5), \(a,a',z_b,D,G\), and the edge pairing are all over
\(\mathbb F_2\).  This is a symmetric bilinear Green pairing.  If
\(z_b:=\partial\beta_E\), then for every such boundary \(a\),

\[
 \boxed{
  \langle D(a),\beta_E\rangle_E=G(a,z_b)=G(z_b,a).}
 \tag{4.5}
\]

No choice of root or endpoint pairing enters (4.5): finite-boundary
injectivity makes \(D\) unique.  Applied to an old family chain, its
boundary determines that chain in exactly this common edge basis.

## 5. The two rays and three rectangles

Retain the endpoint notation
\(x^P_{\nu,h},x^C_{\nu,0/1},x^Q_{\nu,h}\) from the old--new endpoint
program, and write \(*\) for the surviving common class
\(\nu\in\{3,4,5\}\).  The membership parts of its exact obligations are

\[
 \boxed{
 E_P^{\rm mem}(h)
 =\mu_{w_b}(x^P_{1,h},x^P_{1,h+1})
  +\mu_{w_b}(x^P_{*,h},x^P_{*,h+1}),}
 \tag{5.1}
\]

and, for

\[
 \mathcal R=\{(1,5),(2,3),(4,6)\},
 \tag{5.2}
\]

\[
 \boxed{
 E_Q^{\rm mem}(h)
 =\sum_{(\nu,\nu')\in\mathcal R}
 \left(
  \mu_{w_b}(x^Q_{\nu,h},x^Q_{\nu,h+1})
 +\mu_{w_b}(x^Q_{\nu',h},x^Q_{\nu',h+1})
 \right).}
 \tag{5.3}
\]

Each summand in (5.1) and (5.3) has the finite boundary-distance form
(4.3).  Across any consecutive range for which all displayed endpoints
are admissible, (2.6) gives

\[
 \boxed{
 \sum_{h=r}^{s-1}E_P^{\rm mem}(h)
 =\mu_{w_b}(x^P_{1,r},x^P_{1,s})
  +\mu_{w_b}(x^P_{*,r},x^P_{*,s}),}
 \tag{5.4}
\]

and

\[
 \boxed{
 \sum_{h=r}^{s-1}E_Q^{\rm mem}(h)
 =\sum_{(\nu,\nu')\in\mathcal R}
 \left(
  \mu_{w_b}(x^Q_{\nu,r},x^Q_{\nu,s})
 +\mu_{w_b}(x^Q_{\nu',r},x^Q_{\nu',s})
 \right).}
 \tag{5.5}
\]

Thus the local part of every paired rectangle and every finite ray segment
depends only on its outer endpoints and the finite boundary
\(\beta_b\).  Equations (5.4)--(5.5) prove telescoping, not pointwise
vanishing.  In particular, neither a single ray nor a single rectangle has
been declared zero.

One may flip a paired four-endpoint chain to its two cross sides only after
checking that the corresponding cross endpoints lie in the same
\(K\)-orbit.  Equality of two powered ray-action words alone does not prove
that component condition.  No such unverified rectangle flip is used in
(5.3) or (5.5).

The \(C\)-membership term has the analogous closed form

\[
 E_C^{\rm mem}
 =\sum_{\nu=1}^6
   \mu_{w_b}(x^C_{\nu,0},x^C_{\nu,1}).
 \tag{5.6}
\]

## 6. Exact combined cochain identities

Define the global transported-label-rank/tie cochain on a stored edge by

\[
 r_T(E_s(v))
 :=\sum_{o:s_o=s}R_T^\rho(\iota_o(v)),
 \qquad s\in\{2,3,4\},
 \tag{6.1}
\]

where \(<_\rho\) is decreasing transported-label shortlex with chronology
as its tie-breaker and \(T\) is the full global 84-token mask.  For a
finite chain \(C\), write

\[
 \langle C,r_T\rangle
 :=\sum_e(C_e\bmod2)r_T(e).
 \tag{6.2}
\]

Set

\[
\begin{aligned}
 C_P(h)&=[x^P_{1,h},x^P_{1,h+1}]
       +[x^P_{*,h},x^P_{*,h+1}],\\
 C_Q^{\nu,\nu'}(h)&=[x^Q_{\nu,h},x^Q_{\nu,h+1}]
       +[x^Q_{\nu',h},x^Q_{\nu',h+1}].
\end{aligned}
\tag{6.3}
\]

The chronology-rank theorem and (4.1) give the complete all-index forest
identities

\[
 \boxed{
 E_P(h)=\langle C_P(h),\beta_E\rangle_E
       +\langle C_P(h),r_T\rangle,}
 \tag{6.4}
\]

and

\[
 \boxed{
 E_Q(h)=\sum_{(\nu,\nu')\in\mathcal R}
 \left(
  \langle C_Q^{\nu,\nu'}(h),\beta_E\rangle_E
 +\langle C_Q^{\nu,\nu'}(h),r_T\rangle
 \right).}
 \tag{6.5}
\]

The first term is the explicit mod-four tree-distance expression in
(4.2)--(5.6).  The second is the integrated sum of global
\(<_\rho\)-initial-segment ranks.  It is not an edge-overlap pairing and no
local tree-metric formula for it is asserted.  The chronology tie-break is
part of \(r_T\); calling it a strict-label crossing count would omit that
case.

Tree geometry reorganizes both cochain evaluations but does not force
either one to vanish.  The next exact step is therefore twofold: evaluate
the finite \(\beta_b\)-weighted distance congruences for the outer
\(P,C,Q\) endpoints, and construct a complete parity pairing for the
transported-label-rank/tie contributions.  Both parts are required before
any endpoint identity or covariance theorem can be claimed.
