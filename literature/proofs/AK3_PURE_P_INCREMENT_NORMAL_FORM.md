# Diagonal pure-\(P\) increment normal form

## Status and scope

Let

\[
 A_i^\Delta:=A_{i,i},\qquad
 q_i:=A_{i+1,i+1}+A_{i,i}.
 \tag{0.1}
\]

This note proves exact all-power word, integral-collision, and forest-chain
normal forms for \(q_i\). The completed \(j\)-edge theorem and the
four-corner identity already give

\[
 \mathcal D_{ij}=c_{i+1}+c_i
 \qquad\text{and}\qquad
 u_{ij}=c_i+[j=i].
 \tag{0.2}
\]

Consequently

\[
 \mathscr C(A_i^\Delta,q_i)
 =\Phi(A_{i+1,i+1})+\Phi(A_{i,i})
 =\mathcal D_{i,i}
 =c_{i+1}+c_i.
 \tag{0.3}
\]

The specialization \(j=i\) is the narrowest diagonal target: its source
words contain powers of \(P_\nu\), but no \(Q_\nu\)-factor. The slot-zero
raw contribution is already zero. The joint nonzero-raw, old--new, and
new--new xor remains open. No diagonal identity, unary delta identity,
period-two lift, AK(3), stable Andrews--Curtis, or Andrews--Curtis claim is
made.

## 1. Exact diagonal source words

Use the fixed reduced words

\[
 R=\texttt{BgAbaBgAgAggAB},\qquad
 w=\texttt{aG},\qquad z=\texttt{baG},\qquad
 E=\texttt{aGbAAG}.
 \tag{1.1}
\]

The exact complete-cover factorization gives

\[
 P_2=P_6,\qquad
 P_3=P_4=P_5=E^3=:P_*,
 \tag{1.2}
\]

and

\[
 W^w_{\nu,i,j}
 =\operatorname{red}\bigl(P_\nu^iC_\nu Q_\nu^{\,i-j}\bigr).
 \tag{1.3}
\]

See <code>.scratch/period_two_companion_identity.md</code>, equations
(2.13)--(2.15). Put

\[
 X_{\nu,i}:=W^w_{\nu,i,i}
 =\operatorname{red}(P_\nu^iC_\nu).
 \tag{1.4}
\]

Because \(C_1=P_1\), \(C_3=P_3=P_*\), and the fixed common-block
identities hold at every integer \(Q\)-power, including exponent zero,

\[
\boxed{
\begin{aligned}
 X_{1,i}&=P_1^{\,i+1},&
 X_{3,i}&=P_*^{\,i+1},\\
 X_{4,i}&=\operatorname{red}(X_{3,i}w),&
 X_{5,i}&=\operatorname{red}(X_{3,i}z),\\
 X_{6,i}&=\operatorname{red}(X_{2,i}w).
\end{aligned}}
 \tag{1.5}
\]

These are reduced-word identities for every \(i\geq0\), not bounded-cell
observations. In particular, the two surviving long rays are the pure
powers \(P_1^{i+1}\) and \(P_*^{i+1}\); there is no fixed inverse-\(Q\)
tail and no inverse seam.

## 2. Integral six-family collision

Let \(\mathsf E_s(X)\) be the signed oriented integral edge current of a
reduced source-tree path and let \([X]\) be its right-deck endpoint
operator. Path concatenation gives

\[
 \mathsf E_s(Xr)=\mathsf E_s(X)+[X]\mathsf E_s(r).
 \tag{2.1}
\]

Retain the integral source signs

\[
 (\epsilon_1,\ldots,\epsilon_6)=(1,-1,1,1,-1,-1).
 \tag{2.2}
\]

Substituting (1.5) into (2.1) gives

\[
\boxed{
\begin{aligned}
 \sum_{\nu=1}^6\epsilon_\nu\mathsf E_s(X_{\nu,i})
 ={}&\mathsf E_s(X_{1,i})-2\mathsf E_s(X_{2,i})
     +\mathsf E_s(X_{3,i})\\
 &+[X_{3,i}]
   \bigl(\mathsf E_s(w)-\mathsf E_s(z)\bigr)
   -[X_{2,i}]\mathsf E_s(w).
\end{aligned}}
 \tag{2.3}
\]

Thus families \(2,6\) collide with coefficient \(-2\), while families
\(3,4,5\) leave one long prefix and three transported short-connector
terms. This is an integral identity. The coefficient \(-2\) and the doubled
fixed anchors may disappear only after the complete integral current has
been assembled and collision-aggregated.

For one newly added \(P\)-block, the exact family cancellations leave the
\(14\) positions of \(P_1\) and the \(18\) positions of \(P_3\), hence
\(32\) active parity rows. Their slot profile is

\[
 (7,11,14).
 \tag{2.4}
\]

The corresponding module schema at zero-based position \(k\) and power
level \(h\) is

\[
 x^P_{\nu,h,k}
 =\operatorname{cvert}\!\left(
 m_{\nu k}E(P_{\nu,<k})p_\nu^h r_\nu
 \right),
 \qquad \nu\in\{1,3\}.
 \tag{2.5}
\]

The fixed prefixes in (2.5) vary with \((\nu,k)\). Existing inverse-\(Q\)
raw certificates do not evaluate these \(P\)-rows, and raw pumping alone
would prove eventual stability rather than the required aggregate value.
No raw-zero conclusion is inferred from (2.4).

## 3. Exact connector normal form

Let \(x_{\nu,i}\) be the source-forest endpoint represented by \(X_{\nu,i}\).
Define

\[
\begin{aligned}
 S^{(3)}_{w,i}&=[x_{3,i},x_{4,i}],&
 S^{(3)}_{z,i}&=[x_{3,i},x_{5,i}],&
 S^{(2)}_{w,i}&=[x_{2,i},x_{6,i}],\\
 K_i&=[x_{1,i},x_{3,i}]
     +S^{(3)}_{w,i}+S^{(3)}_{z,i}+S^{(2)}_{w,i}.
\end{aligned}
 \tag{3.1}
\]

The three \(S\)-chains are the transported literal paths \(w,z,w\), of
lengths \(2,3,2\). The chain \(K_i\) is exactly the seam connector
\(K_Q^{(i)}(0)=\widetilde K_i(0)\) from the powered and inverse connector
theorems.

Let \(\beta_i\) be the collision-aggregated mod-two forest current of
\(q_i\). The six endpoint pairs give

\[
 \partial\beta_i=\partial(K_i+K_{i+1}).
 \tag{3.2}
\]

The boundary map is injective on finite forest chains, hence

\[
 \boxed{\beta_i=K_i+K_{i+1}.}
 \tag{3.3}
\]

The existing \(h=0\) connector identity is

\[
 K_i
 =K_P(i+1)
  +S^{(3)}_{w,i}+S^{(3)}_{z,i}+S^{(2)}_{w,i}.
 \tag{3.4}
\]

Since \(C_P(h)=K_P(h)+K_P(h+1)\), equations (3.3)--(3.4) give the sharper
normal form

\[
\boxed{
\begin{aligned}
 \beta_i={}&C_P(i+1)
 +\Delta S^{(3)}_{w,i}
 +\Delta S^{(3)}_{z,i}
 +\Delta S^{(2)}_{w,i},\\
 \Delta S_{r,i}&:=S_{r,i}+S_{r,i+1}.
\end{aligned}}
 \tag{3.5}
\]

Thus the complete forest increment is one two-ray powered-\(P\) connector
plus three differences of fixed literal connectors. Formula (3.5) removes
the inverse-\(Q\) terminal block, seam cancellation, and retraced-\(z\)
topology from the proof target. It is a constant-number powered-template
interface; all edge collisions are still performed in the common stored
basis.

The terminal connector has exact support

\[
 |C_P(i+1)|=|P_1|+|P_3|=14+18=32.
 \tag{3.6}
\]

Before cross-collision, the two copies of the three short words contribute
\(2(2+3+2)=14\) edges. There is one uniform intersection. The old
\(S^{(3)}_{w,i}\) is exactly the first two edges of the new terminal
\(P_3\)-block in \(C_P(i+1)\), because

\[
 P_3=\texttt{aGbAAGaGbAAGaGbAAG},
 \qquad w=\texttt{aG}.
 \tag{3.7}
\]

Those two stored edges occur twice and cancel. There are no other
intersections: the \(z\)-path leaves the old \(P_3\) endpoint through
\(\texttt b\), the new short paths start beyond the terminal block, the
family-\(2\) path lies in the other component, and a later meeting of
distinct reduced branches would create a cycle in the forest. Therefore

\[
 \boxed{|\beta_i|=32+14-2\cdot2=42.}
 \tag{3.8}
\]

The pre-collision slot profile is \((9,17,20)\). The duplicated
\(\texttt{aG}\) removes two copies of one slot-three and one slot-four
edge, giving

\[
 \boxed{
 (|\beta_{i,2}|,|\beta_{i,3}|,|\beta_{i,4}|)
 =(9,15,18).}
 \tag{3.9}
\]

The two slot-zero endpoint coordinates give twelve decorated tokens, and
every forest edge gives its positive/negative occurrence pair. Hence the
increment has the uniform decorated size

\[
 \boxed{|q_i|_{\rm dec}=12+2|\beta_i|=96.}
 \tag{3.10}
\]

Equations (3.8)--(3.10) are all-power word/forest consequences. They do not
evaluate a raw, old--new, new--new, or complete scalar term.

## 4. Slot-zero raw term

The all-power slot-zero theorem is

\[
 R_0(Y(d,m))=[d<0].
 \tag{4.1}
\]

Both endpoints in (0.1) lie on \(d=i-j=0\). Their slot-zero raw values are
therefore zero, and

\[
 \boxed{L_0(q_i)=0+0=0.}
 \tag{4.2}
\]

No nonzero-slot raw value follows from (4.2). At \(d=0\), the raw
provenance contains no \(Q\)-block rows; after the common old \(P\)-levels
cancel, only the terminal \(P\)-block and the two adjacent \(C\)-boundary
copies remain. These are finite powered-template families, but their joint
raw parity is not evaluated here.

Before family aggregation, this is

\[
 100\ \text{terminal-\(P\) rows}
 +2\cdot113\ \text{\(C\)-boundary rows}
 =326
 \tag{4.3}
\]

signed provenance rows. The terminal \(P\)-copy reduces to the \(32\) rows
in (2.4). At either \(C\)-endpoint, the exact identities
\(C_1=P_1\), \(C_3=P_3\),
\(C_4=C_3w\), \(C_5=C_3z\), and \(C_6=C_2w\) reduce the active rows to at
most \(14+18+2+3+2=39\). Thus

\[
 \boxed{32+39+39=110}
 \tag{4.4}
\]

is a uniform collision-first provenance bound before cross-endpoint
coordinate aggregation. Formula (4.4), together with the \(96\)-token
theorem (3.10), bounds the exact proof interface; it supplies no parity
value.

## 5. Why transport alone cannot close the increment

After integral collision and parity, the two surviving long actions are

\[
 \mathfrak p_1=[P_1],\qquad \mathfrak p_*=[P_*].
 \tag{5.1}
\]

They are distinct: \(P_1\) and \(P_*\) are freely reduced words of lengths
\(14\) and \(18\) in the exact free deck group. Therefore (3.5) is not one
global deck translate.

Nor does right-deck transport preserve shortlex order. For example,
\(\mathrm{eps}<_{\rm sl}\texttt T\), but right multiplication by
\(\texttt t\) sends the pair to \(\texttt t,\mathrm{eps}\), reversing its
order. The raw weight is not a function of transported central label:
\((q,v)=(\texttt{tc},\texttt{cT})\) and
\((q,v)=(\mathrm{eps},\mathrm{eps})\) have the same central label and raw
weights one and zero.

Finally, a collision-aggregated forest boundary need not have zero
quadratic value. The approved adjacent inverse-\(Q\) masks are source-tree
boundaries but satisfy \(Q(b^-_{n,e})=1\). Hence no boundary-only,
single-transport, central-label, or familywise involution proves the target.

## 6. Exact head--tail interface

For \(o\in\{3,4,7,8,11,12\}\), let \(\pi_{o,i}\) be the unique path
between the two transported occurrence endpoints belonging to
\(A_i^\Delta\) and \(A_{i+1}^\Delta\). Put

\[
 \Pi_{1,i}=\pi_{3,i}+\pi_{4,i},\qquad
 \Pi_{2,i}=\pi_{7,i}+\pi_{8,i},\qquad
 \Pi_{3,i}=\pi_{11,i}+\pi_{12,i}.
 \tag{6.1}
\]

Finite forest injectivity gives

\[
 \beta_i=\Pi_{1,i}+\Pi_{2,i}+\Pi_{3,i},
 \qquad
 \partial\Pi_{r,i}=Z_{r,i}\quad(r=1,2,3).
 \tag{6.2}
\]

Define

\[
 F_{i,2}=\Pi_{1,i}+\beta_{i,2},
 \qquad
 G_{i,3}=\Pi_{3,i}+\beta_{i,3}.
 \tag{6.3}
\]

Applying the proved occurrence-sweep identity to the old powered chain
\(K_i\) gives

\[
\boxed{
\begin{aligned}
 \langle K_i,\omega_i\rangle
 ={}&\langle t_2K_{i,2},\partial F_{i,2}\rangle
    +\langle h_3K_{i,3},\partial G_{i,3}\rangle\\
   &+\langle\partial K_{i,3},\partial\beta_{i,4}\rangle
    +\langle\partial K_{i,4},\bar q_{i,4}\rangle.
\end{aligned}}
 \tag{6.4}
\]

Here \(\omega_i\) is the complete old--new edge load induced by \(q_i\);
the last vertex function is the unsymmetrized slot-four activity of
\(q_i\). All chains are collision-aggregated in one stored basis and all
integral incidence signs are placed before reduction modulo two.

## 7. Smallest remaining lemma

Let \(E_{{\rm fixed},i},E_{{\rm base},i},E_{{\rm singleton},i}\) be the
finite-old contributions to \(\mathbb B(A_i^\Delta,q_i)\). They are not
imported from the positive-\(j\) or inverse-\(Q\) increments. Combining
(4.2) and (6.4), the remaining joint two-ray \(P\)-period lemma is

\[
\boxed{
\begin{aligned}
0={}&L_{\ne0}(q_i)+Q(q_i)
 +E_{{\rm fixed},i}+E_{{\rm base},i}+E_{{\rm singleton},i}\\
 &+\langle t_2K_{i,2},\partial F_{i,2}\rangle
  +\langle h_3K_{i,3},\partial G_{i,3}\rangle\\
 &+\langle\partial K_{i,3},\partial\beta_{i,4}\rangle
  +\langle\partial K_{i,4},\bar q_{i,4}\rangle,
 \qquad i\geq0.
\end{aligned}}
 \tag{7.1}
\]

Equivalently,

\[
 \boxed{
 L_{\ne0}(q_i)+\mathbb B(A_i^\Delta,q_i)+Q(q_i)=0.}
 \tag{7.2}
\]

Formula (3.5) makes (7.1) a constant-number, collision-first
powered-template proof interface. It does not evaluate any summand.
All cross terms between \(C_P(i+1)\) and the three short-connector
differences remain inside \(Q(q_i)\). A valid proof may group the displayed
terms jointly; no termwise vanishing is asserted.

Proving (7.1) makes all \(c_i\) equal. The exact seed \(u_{00}=1\) gives
\(c_0=0\), so the diagonal identity and unary delta would then follow from
the already proved reductions. Until (7.1) is proved, those conclusions and
every period-two/AK3/AC conclusion remain open.
