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
words contain powers of \(P_\nu\), but no \(Q_\nu\)-factor.  The all-power
certificate in Section 4 proves the complete raw contribution zero, Section
6 proves the old--new value one, and the independently replayed certificate
in Section 7 proves the new--new value one.  Consequently the complete
increment vanishes, which proves the diagonal identity and
\(u_{ij}=\delta_{ij}\).  The free-group period-two lift, AK(3), stable
Andrews--Curtis, and Andrews--Curtis remain open.

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

After cross-endpoint aggregation, the exact raw interface is smaller. For
a path word \(Y\), letter position \(k\), powered base \(a\), and component
root \(r\), put

\[
 \mathcal V(Y,k;a,r)
 :=\operatorname{cvert}\!\left(
 m_{Y_k}E(Y_{<k})\,a\,r
 \right).
 \tag{4.4a}
\]

The integral \(P/C\) cancellation gives precisely the following five
families:

\[
\begin{array}{c|c|c}
\text{family}&\text{domain}&\text{slot profile}\\ \hline
\mathcal V(P_1,k;p_1^{i+1},r_1)&0\le k<14&(4,5,5)\\
\mathcal V(P_*,k;p_*^{i+1},r_3)&2\le k<18&(3,5,8)\\
\mathcal V(z,k;p_*^{i+1},r_3),\
\mathcal V(z,k;p_*^{i+2},r_3)&0\le k<3&(2,2,2)\\
\mathcal V(w,k;p_*^{i+2},r_3)&0\le k<2&(0,1,1)\\
\mathcal V(w,k;c_2p_2^i,r_2),\
\mathcal V(w,k;c_2p_2^{i+1},r_2)&0\le k<2&(0,2,2).
\end{array}
 \tag{4.4b}
\]

Indeed, for \(\nu=1,3\), the terminal \(P\)-copy cancels the old
\(C_\nu=P_\nu\) boundary and leaves the new shifted \(P\)-copy. The old
component-\(3\) \(w=\texttt{aG}\) copy then cancels positions \(0,1\) of
the surviving \(P_*\)-block. Families \(2,6\) and \(4,5\) reduce by the
same integral identities used in (2.3). The five row counts are

\[
 14+16+6+2+4=42,
 \qquad
 (4,5,5)+(3,5,8)+(2,2,2)+(0,1,1)+(0,2,2)
 =(9,15,18).
 \tag{4.4c}
\]

Thus (4.4b) is the minimal collision-first raw template list. Its fixed
prefixes remain row-specific, so the displayed cancellations do not pair
their raw weights.

There is also an exact endpoint reduction after collision aggregation.
For a stored edge put

\[
 \mathcal R(E_s(v))
 :=R_s(v)
 :=\rho_{o_s^+}(v)+\rho_{o_s^-}(v).
 \tag{4.5}
\]

For the literal occurrence table, these are

\[
\boxed{
\begin{aligned}
 R_2&=\rho_{\mathrm{eps}}+\rho_{\texttt{ctcTcTctc}},\\
 R_3&=\rho_{\texttt{ctcTTctt}}+\rho_{\texttt t},\\
 R_4&=\rho_{\texttt t}+\rho_{\mathrm{eps}}.
\end{aligned}}
 \tag{4.5a}
\]

Choose a root in each forest component and integrate this edge cochain:

\[
 \psi_R(x):=\sum_{e\in[\mathrm{root},x]}\mathcal R(e),
 \qquad
 \Psi_i:=\sum_{\nu=1}^6\psi_R(x_{\nu,i}).
 \tag{4.6}
\]

Equations (3.2)--(3.3) and finite forest Stokes give

\[
\boxed{
\begin{aligned}
 L_{\ne0}(q_i)
 &=\langle\beta_i,\mathcal R\rangle\\
 &=\langle K_i+K_{i+1},\mathcal R\rangle
 =\Psi_i+\Psi_{i+1}.
\end{aligned}}
 \tag{4.7}
\]

Thus the raw term may be represented either by the at-most-\(110\)
collision-safe provenance rows before final aggregation, by the \(42\)
active coordinate bits \(R_s(v)\), or by twelve endpoint-potential values.
Each of the \(42\) coordinate bits still contains its two literal
occurrence weights, so an atomic raw ledger has \(84\) evaluations.
Formula (4.7) is a telescope, not an evaluation of \(\Psi_i\).

### 4.1 Raw boundary-locality pump

The all-power extension of a literal raw record uses the following
finite-prefix lemma.  Fix a raw occurrence action \(q\), and let
\(\rho_q(v)\) be the raw weight obtained from the exact branch word
\(zccz^{-1}\) for the canonical module word \(v\).  Suppose a common-phase
canonical template has one changing intact block

\[
 v_m=A R^{r m+s}B,\qquad m\geq m_0,
 \tag{4.8}
\]

where \(R\) is cyclically reduced, \(r>0\), and the two boundary copies of
\(R\) survive quotient reduction.  Let \(d\) be the insertion split before
the next \(r\) copies.  Assume

\[
 d+r|R|>|q|+1.
 \tag{4.9}
\]

Assume also that direct expansion at \(m_0\) and \(m_0+1\) gives the same
complete raw signature

\[
 (\text{ordered first-half labels},
   \text{central-equality bits},\rho),
 \tag{4.10}
\]

that every displayed first-half label is noncentral, and that the central
label is strictly longer than all of them and has positive affine length
slope.

Then the signature (4.10), and hence \(\rho_q(v_m)\), is constant for every
\(m\geq m_0\).

Indeed, the overlap branch for \(qv_m\) consumes at most \(|q|\) initial
letters of \(v_m\).  After those cancellations, the remaining part of
\(v_m\) is a canonical quotient suffix: it has no negative \(c\), and no
two positive \(c\)'s are adjacent.  By the literal event rule, that suffix
creates no first-half raw event.  Thus every such event lies in the
surviving finite action prefix or at its first boundary with \(v_m\).
The possible terminal-\(c\) deletion is determined by the terminal letter
of the fixed suffix \(B\), or by the fixed terminal letter of \(R\) when
\(B\) is empty, and is unchanged by adding whole copies of \(R\).

Inequality (4.9) places every future insertion beyond the complete
event-producing boundary.  An event label is the canonical quotient prefix
at that event, so letters inserted later cannot change it.  The exact first
transition (4.10) verifies the protected boundary state and the
terminal-\(c\) case at the pump base.  The intact common-phase form preserves
both on every later insertion.  Hence induction fixes the ordered first-half
list.  Its equality bits stay false because the list is fixed while the
central length increases.  This proves the claim.

For the five families in (4.4b), the exact all-power interface is therefore
the four disjoint cells

\[
 i=0,\qquad i=1,\qquad i=2,\qquad i\geq3.
 \tag{4.11}
\]

In the unbounded cell each of the \(84\) literal occurrence records has one
positive affine core.  A valid certificate must replay the module word at
\(i=3,4\), verify (4.9), compare the full signatures (4.10), and check the
strict central-length conditions record by record.  The bounded cells are
evaluated by direct expansion.  This lemma extends those exact records; it
does not supply their xor.

### 4.2 All-power raw theorem

The frozen primary certificate evaluates the 46 signed source traversals,
their 44 collision fibers, the 42 active coordinates of profile
\((9,15,18)\), and all 84 literal raw observables in every cell (4.11).
The computed values are

\[
 L_{\ne0}(q_i)=0
 \qquad(i=0,1,2,\text{ and }i\geq3).
 \tag{4.12}
\]

An independent replay reconstructs the complete source selection, factor
order, powered schemas, collision partition, raw observables, and every
hypothesis of the pump in Section 4.1 without importing the producing
checker or assuming the xor.  Its nine hostile mutations are rejected.
Guarded primary generation, canonical replay, and both mutation suites pass.
The final bindings and review record are in
.scratch/period_two_diagonal_pure_p_raw_certificate.md.

Together with the slot-zero identity (4.2), this proves

\[
\boxed{L(q_i)=L_0(q_i)+L_{\ne0}(q_i)=0\qquad(i\geq0).}
 \tag{4.13}
\]

Equivalently, (4.7) now gives \(\Psi_i=\Psi_{i+1}\).  This is an exact raw
theorem only; it evaluates neither the old--new term nor \(Q(q_i)\).

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

### 5.1 Deterministic 48-chord matching

Apply the source-tree matching construction to the exact path sum (3.5):
pair each boundary token with the first or last incident edge event and pair
consecutive edge events at their common canonical forest vertex.  At the
unique two-edge collision, first pair the opposite-sign old-\(w\) and
terminal-\(P_*\) provenance copies, separately at the \(a\)-occurrences
\((15,16)\) and the \(G\)-occurrences \((9,14)\).  Splicing the resulting
alternating paths is deterministic after the literal source rows have been
ordered.

The surviving source pieces and their chord counts are

\[
\begin{array}{c|c|c}
\text{piece}&\text{edge length}&\text{chords}\\ \hline
\text{terminal }P_1&14&15\\
\text{old and new component-2 }w&2+2&6\\
\text{old component-3 }z&3&4\\
\text{residual terminal }P_*&16&17\\
\text{new component-3 }w,z&2+3&6.
\end{array}
 \tag{5.2}
\]

For the last row, the two terminal boundary chords and the \(1+2\)
internal adjacency chords are supplemented by one chord pairing the two
initial \(w,z\) edge events at their common vertex.  Thus the
collision-first matching \(M_i\) has

\[
 \boxed{|M_i|=15+6+4+17+6=48}
 \tag{5.3}
\]

label-preserving chords on the 96 decorated tokens.

### 5.2 Exact chord-label separation

All vertices below are vertices of the common canonical source forest
\(X\).  Hence two distinct reduced source-tree vertices in one component,
or vertices in distinct components, have distinct transported canonical
labels; there is no further quotient identification after
\(\operatorname{cvert}\).

The terminal \(P_1\) piece lies in the reduced prefix cone
\(\texttt{aB}\), whereas every component-3 piece lies in the cone
\(\texttt{aG}\).  The component-2 pieces lie in the other forest
component.  To separate the two component-2 copies without ignoring free
reduction, put

\[
 D=\texttt{gABBgAbaBgAgAg}.
 \tag{5.4}
\]

The exact literal words are

\[
 P_2=\texttt A\,D\,\texttt a,\qquad
 C_2=\texttt A\,D\,\texttt{BaGb},
 \tag{5.5}
\]

and cancellation of the intervening \(\texttt{aA}\) seams gives, uniformly
for \(i\geq0\),

\[
\boxed{
 X_{2,i}
 =\operatorname{red}(P_2^iC_2)
 =\texttt A\,D^{\,i+1}\texttt{BaGb}.}
 \tag{5.6}
\]

Thus \(X_{2,i}\) and \(X_{2,i+1}\) have maximal common prefix
\(\texttt A\,D^{i+1}\), after which the old word continues through
\(\texttt B\) and the new word through \(\texttt g\).  Appending
\(w=\texttt{aG}\) creates no backtracking to that fork.  The two
component-2 \(w\)-paths therefore have disjoint vertex sets.

In component 3, the canceled old \(w=\texttt{aG}\) is exactly positions
zero and one of the newly added \(P_*\)-block.  The residual path consists
of positions \(2,\ldots,17\), from
\(X_{3,i}\texttt{aG}=X_{4,i}\) to

\[
 B:=X_{3,i+1}=P_*^{\,i+2}.
 \tag{5.7}
\]

The old \(z\)-path leaves \(X_{3,i}\) through \(\texttt b\), while the
canceled \(w/P_*\) branch starts through \(\texttt a\); the residual path
does not contain the fork vertex.  At \(B\), the residual terminal branch
and the new \(w,z\) branches are incident through the three distinct
literal directions \(\texttt G,\texttt a,\texttt b\).  Forest uniqueness
therefore gives no further meeting.

Consequently \(B\) is the only source-tree vertex which supports two
chords of \(M_i\).  They are the residual-\(P_*\) boundary chord of
occurrence type \((9,11)\) and the new-\(w\)/new-\(z\) initial-incidence
chord of type \((6,15)\).  Since

\[
 6<9<11<15,
 \tag{5.8}
\]

the sole equal-label chord pair is nested and does not cross.  Every
crossing pair is therefore heterochromatic, and the heterochromatic chord
formula simplifies to

\[
 \boxed{Q(q_i)=\operatorname{cr}(M_i).}
 \tag{5.9}
\]

This removes the transported-label equality predicates, but it does not
evaluate the crossing parity.

### 5.3 Remaining order predicates

The twelve boundary-chord occurrence types are

\[
\begin{gathered}
(1,3),\ (3,15),\ 2(4,9),\ (6,11),\ (6,7),\ (9,11),\\
(7,9),\ 2(8,9),\ 2(12,15),
\end{gathered}
 \tag{5.10}
\]

and the thirty-six adjacency-chord types are

\[
\begin{gathered}
4(1,16),\ 4(6,9),\ 11(14,16),\ 4(9,15),\ (9,14),\\
3(1,15),\ (1,6),\ 2(6,15),\ 3(15,16),\ 3(14,15).
\end{gathered}
 \tag{5.11}
\]

Among the \(\binom{48}{2}=1128\) chord pairs, literal occurrence order
forces 148 crossings and 472 noncrossings.  The remaining 508 pairs share
an occurrence block.  Indeed, the occurrence degrees give

\[
 d_1=d_6=9,\quad d_9=d_{14}=15,\quad d_{15}=d_{16}=18,
 \quad
 d_3=d_4=d_7=d_8=d_{11}=d_{12}=2,
 \tag{5.12}
\]

and therefore

\[
 \sum_o\binom{d_o}{2}=594,
 \tag{5.13}
\]

while pairs of identical occurrence type contribute
\(\sum_\theta\binom{m_\theta}{2}=86\); hence 422 pairs share exactly one
block and 86 share both.

Partner polarity reverses module order at the negative occurrence, so the
594 atomic within-block comparisons reduce to

\[
 |y_{i,i}|=24(i+1)+4,\qquad
 |y_{i+1,i+1}|=24(i+2)+4.
\]

Thus the single slot-zero predicate is fixed:
\([y_{i,i}<_{\rm sl}y_{i+1,i+1}]=1\).  The complete order inventory is

\[
\boxed{
 \binom92+\binom{15}2+\binom{18}2+1
 =294+1}
 \tag{5.14}
\]

order predicates.  The last predicate is the single slot-zero order, fixed
by the displayed endpoint lengths; the 294 nonzero-slot module-shortlex
predicates remain unevaluated.  Thus (5.9)--(5.14) are a finite
all-power proof interface, not a value of \(Q(q_i)\).

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

### 6.1 Exact head--tail comparison inventory

Put \(m=i+1\).  Expanding the literal run boundaries in (3.5) and (6.1)
gives the following componentwise support counts:

\[
\begin{array}{c|cc}
\text{vertex chain or function}&\mathrm{ct}&\mathrm{eps}\\ \hline
t_2K_{i,2}&7m+1&0\\
\partial F_{i,2}&18&0\\
h_3K_{i,3}&11m+2&1\\
\partial G_{i,3}&24&6\\
\partial K_{i,3}&20m+4&2\\
\partial\beta_{i,4}&26&4\\
\partial K_{i,4}&22m&2\\
\bar q_{i,4}&16&2.
\end{array}
 \tag{6.5}
\]

Vertices in different forest components cannot pair.  Therefore the four
terms in (6.4) have the following exact uncompressed same-component
comparison-ledger sizes:

\[
\begin{aligned}
 H_1&=(7m+1)18=126m+18,\\
 H_2&=(11m+2)24+1\cdot6=264m+54,\\
 H_3&=(20m+4)26+2\cdot4=520m+112,\\
 H_4&=(22m)16+2\cdot2=352m+4.
\end{aligned}
 \tag{6.6}
\]

Thus the complete literal head--tail ledger has

\[
 \boxed{H_1+H_2+H_3+H_4=1262m+188}
 \tag{6.7}
\]

candidate vertex-equality predicates.  Formula (6.7) is an exhaustive
inventory before equality collisions or parity cancellations; it is not a
minimal predicate count and supplies no value for any term in (6.4).

### 6.2 Exact finite-old subtotal

Only four occurrence blocks of \(q_i\) have odd cardinality:

\[
 |S_2|=9\quad(o=1,6),\qquad
 |S_3|=15\quad(o=9,14).
 \tag{6.8}
\]

The slot-zero blocks have size two, the slot-four blocks size eighteen, and
slot one is empty.  The authoritative literal AST places the seventy fixed
events in the strict intervals cut by \(1,6,9,14\) as follows:

\[
\begin{array}{c|ccccc}
\text{interval}
&\text{before }1&(1,6)&(6,9)&(9,14)&\text{after }14\\ \hline
\text{fixed events}&0&28&18&24&0\\
R^\chi_{q_i}&0&1&0&1&0.
\end{array}
 \tag{6.9}
\]

Thus their total chronology rank is

\[
 \sum_{f\in\mathcal F_{\rm tok}}R^\chi_{q_i}(f)
 =28+24=52=0\pmod2.
 \tag{6.10}
\]

The exact fixed-label table has maximum source-forest radius nine in the
\(\mathrm{ct}\)-component and six in the \(\mathrm{eps}\)-component.
Every label of \(q_i\) lies on the support or boundary of (3.5).  Its
minimum radii, including \(i=0\), are fourteen at
\(X_{1,0}=P_1\) in the first component and nineteen at
\(X_{2,0}=\texttt A\,D\,\texttt{BaGb}\) in the second.  Therefore

\[
 H_{q_i}(f)=0\qquad(f\in\mathcal F_{\rm tok}).
 \tag{6.11}
\]

The even transported-label-fiber theorem identifies the remaining
transported-label rank with this equal-label prefix:
\(R^\rho_{q_i}(f)=H_{q_i}(f)\).  Combining (6.10)--(6.11) gives

\[
 \boxed{E_{{\rm fixed},i}=0.}
 \tag{6.12}
\]

The two base edges are
\(E_3(\texttt{TTct})\) and \(E_4(\texttt{Tct})\), forming the core path

\[
 \texttt{ct}-\texttt{Tct}-\texttt{ctcT}
 \tag{6.13}
\]

at radii \(0,1,2\).  The same separation excludes both membership in
\(\beta_i\) and every equal-label tie at these three vertices.  Hence

\[
 \boxed{E_{{\rm base},i}=0.}
 \tag{6.14}
\]

Finally, the old singleton coordinate \(y_{i,i}\) belongs to the
two-point slot-zero support
\(\{y_{i,i},y_{i+1,i+1}\}\), so its membership bit is one.  In occurrence
order \((3,4,7,8,11,12)\), its incident partner occurrences and strict
prefix bits are

\[
\begin{array}{c|rrrrrr}
o&3&4&7&8&11&12\\ \hline
\text{partner}&15&9&6&9&6&15\\
H_{q_i}(\iota_o(y_{i,i}))&0&0&1&0&1&0.
\end{array}
 \tag{6.15}
\]

The prefix xor is zero.  Therefore

\[
 \boxed{E_{{\rm singleton},i}=1.}
 \tag{6.16}
\]

Equations (6.12), (6.14), and (6.16) prove the finite-old subtotal

\[
 \boxed{
 E_{{\rm fixed},i}+E_{{\rm base},i}+E_{{\rm singleton},i}=1.}
 \tag{6.17}
\]

This does not evaluate the powered head--tail load in (6.4).

### 6.3 Exact powered head--tail value

Index the two terminal blocks by

\[
 A_j=X_{1,i}P_{1,<j}\quad(0\leq j\leq14),\qquad
 B_j=X_{3,i}P_{*,<j}\quad(0\leq j\leq18).
 \tag{6.18}
\]

Thus \(A_0=X_{1,i}\), \(B_0=X_{3,i}\), and
\(B_{18}=X_{3,i+1}\).  Put

\[
\begin{aligned}
 z_j&=B_0z_{<j},&z'_j&=B_{18}z_{<j}&&(0\leq j\leq3),\\
 w'_j&=B_{18}w_{<j}&&(0\leq j\leq2),\\
 u_j&=X_{2,i}w_{<j},&u'_j&=X_{2,i+1}w_{<j}
 &&(0\leq j\leq2).
\end{aligned}
 \tag{6.19}
\]

The active pieces of \(\beta_i\) are the full \(A\)-block, the residual
\(B\)-block \(B_2,\ldots,B_{18}\), the old and new \(z\)-paths, the new
component-3 \(w\)-path, and the old and new component-2 \(w\)-paths.
This is exactly the two-edge cancellation in (3.7)--(3.9).

For the first term of (6.4), literal slot-two run boundaries give

\[
\begin{aligned}
\operatorname{supp}\partial F_{i,2}
=\{&
A_0,A_1,A_2,A_9,A_{11},A_{13},\\
&B_0,B_2,B_3,B_8,B_9,B_{14},B_{15},B_{18},
z_1,z_3,z'_1,z'_3\}.
\end{aligned}
 \tag{6.20}
\]

The tail selector \(t_2K_{i,2}\) meets this set only at \(B_0\), supplied
by the initial old-\(z\) letter \(\texttt b\).  In particular, the
terminal \(P_1\) \(\texttt b\)-edge selects its prevertex rather than
\(A_0\), and \(B_2\) is selected by the canceled old-\(w\)
\(\texttt G\)-edge through \(h_3\), not by \(t_2\).  Hence

\[
 H_1=\langle t_2K_{i,2},\partial F_{i,2}\rangle=1.
 \tag{6.21}
\]

For the second term, the componentwise support is

\[
\begin{aligned}
\operatorname{supp}_{\rm ct}\partial G_{i,3}
=\{&
A_2,A_3,A_4,A_5,A_6,A_8,A_{11},A_{12},\\
&B_0,B_5,B_6,B_7,B_8,B_{11},B_{12},B_{13},B_{14},B_{17},\\
&z_2,z_3,z'_2,z'_3,w'_1,w'_2\},\\
\operatorname{supp}_{\rm eps}\partial G_{i,3}
=\{&X_{2,i},X_{2,i+1},u_1,u_2,u'_1,u'_2\}.
\end{aligned}
 \tag{6.22}
\]

The residual terminal-\(\texttt G\) boundary at \(B_{18}\) cancels the
\(Z_3\)-endpoint there, leaving \(B_0\).  The head selector \(h_3K_{i,3}\)
meets (6.22) exactly at

\[
 \{B_0,z_3,u_2\}.
\]

These are the postvertices of the final uppercase-\(\texttt G\) edges in
the old terminal \(P_*\), old \(z\), and old component-2 \(w\) paths.
Therefore

\[
 H_2=\langle h_3K_{i,3},\partial G_{i,3}\rangle=3=1.
 \tag{6.23}
\]

For the third term,

\[
\begin{aligned}
\operatorname{supp}_{\rm ct}\partial\beta_{i,4}
=\{&
A_0,A_1,A_3,A_4,A_5,A_6,A_8,A_9,A_{12},A_{13},\\
&B_3,B_5,B_6,B_7,B_9,B_{11},B_{12},B_{13},B_{15},B_{17},\\
&z_1,z_2,z'_1,z'_2,B_{18},w'_1\},\\
\operatorname{supp}_{\rm eps}\partial\beta_{i,4}
=\{&X_{2,i},u_1,X_{2,i+1},u'_1\}.
\end{aligned}
 \tag{6.24}
\]

Its intersection with \(\operatorname{supp}\partial K_{i,3}\) is exactly
\(\{z_2,u_1\}\): each vertex is the prevertex of a final old
\(\texttt G\)-edge and an endpoint of the old \(\texttt a\)-edge.
Consequently \(H_3=2=0\).

Finally, the unsymmetrized slot-four tail support is

\[
\begin{aligned}
\operatorname{supp}_{\rm ct}\bar q_{i,4}
=\{&
A_1,A_3,A_5,A_8,A_{12},\\
&B_3,B_4,B_7,B_9,B_{10},B_{13},B_{15},B_{16},\\
&z_2,z'_2,w'_1\},\\
\operatorname{supp}_{\rm eps}\bar q_{i,4}
=\{&u_1,u'_1\}.
\end{aligned}
 \tag{6.25}
\]

Here the slot-four tail convention selects the prevertex for uppercase
\(\texttt A\) and the postvertex for lowercase \(\texttt a\).
The intersection with \(\operatorname{supp}\partial K_{i,4}\) is again
exactly \(\{z_2,u_1\}\), so \(H_4=2=0\).

There are no omitted intersections.  The terminal \(P_1\) piece meets old
\(K_i\) only at \(A_0\); after cancellation the residual \(P_*\) piece
meets it only at \(B_2\).  The old \(z\) and old component-2 \(w\) paths
are the only active short paths already contained in \(K_i\).  The new
component-3 branches leave \(B_{18}\) in directions distinct from the
residual terminal direction, and the old/new component-2 paths are
separated by the exact \(\texttt B/\texttt g\) fork in (5.6).  Different
components cannot meet.  These cone arguments include \(i=0\).

Thus

\[
\boxed{
(H_1,H_2,H_3,H_4)=(1,1,0,0),\qquad
\langle K_i,\omega_i\rangle=0.}
 \tag{6.26}
\]

Together with (6.17), this proves the complete old--new value

\[
\boxed{\mathbb B(A_i^\Delta,q_i)=1\qquad(i\geq0).}
 \tag{6.27}
\]

No value of \(Q(q_i)\) is used or inferred.

## 7. Smallest remaining lemma

Combining the complete raw theorem (4.13) with the old--new theorem (6.27),
the remaining two-ray \(P\)-period lemma is exactly

\[
\boxed{Q(q_i)=1\qquad(i\geq0).}
 \tag{7.1}
\]

Equivalently,

\[
 \boxed{
 \mathbb B(A_i^\Delta,q_i)+Q(q_i)=0.}
 \tag{7.2}
\]

Equations (5.9)--(5.14) reduce (7.1) to the 294 nonzero-slot
module-shortlex order predicates of the deterministic 48-chord matching.
All cross terms between \(C_P(i+1)\) and the three short-connector
differences remain inside \(Q(q_i)\); no familywise value is asserted.

### 7.1 Minimal quadratic certificate interface

The same common-phase normal forms partition the remaining order problem
into the four exhaustive cells

\[
 i=0,\qquad i=1,\qquad i=2,\qquad i\geq3.
 \tag{7.3}
\]

Within one cell, it is enough to certify the three total module-shortlex
orders on the active slot sets of sizes \(9,15,18\).  Transitivity reduces
this to

\[
 (9-1)+(15-1)+(18-1)=39
 \tag{7.4}
\]

adjacent order witnesses.  Partner polarity supplies the negative
occurrence order by reversal:

\[
 r^-_{c,s}(v)=|S_s|-1-r^+_{c,s}(v).
 \tag{7.5}
\]

The exact all-power comparison census is sharper still: among the 362
same-slot provenance pairs in a cell, 359 are decided by strict affine
length, two are the canceled equality fibers, and one uses a fixed-prefix
first mismatch.  Thus the ranked active lists require at most one genuine
lexical witness per cell; all other adjacent witnesses are affine integer
inequalities.

The occurrence-type multisets (5.10)--(5.11) do not determine crossing
parity by themselves.  A valid certificate must instantiate the
coordinate-to-chord assignment.  Order its 48 deterministic chord rows as
\(C_k=(a_k,b_k)\).  For each \(k\), put

\[
 \lambda_k
 :=\sum_{j<k}
 \left(
 [a_j\in(a_k,b_k)]+[b_j\in(a_k,b_k)]
 \right).
 \tag{7.6}
\]

Exactly one endpoint of \(C_j\) lies in the open chronological interval of
\(C_k\) precisely when the two chords cross.  Therefore

\[
 \boxed{
 Q(q_i)=\operatorname{cr}(M_i)
 =\sum_{k=1}^{48}\lambda_k\pmod2.}
 \tag{7.7}
\]

Each \(\lambda_k\) is obtained from fixed whole-occurrence counts and at
most two prefix-rank lookups in the ranked boundary blocks.  The smallest
remaining certificate therefore consists of 48 coordinate-bound chord
rows, the three ranked slot lists in each cell, 39 adjacent witnesses per
cell, and the 48 prefix-sweep parities.  Its computed value is not imposed;
until it gives one on every cell, (7.1) remains open.

Proving (7.1) makes all \(c_i\) equal. The exact seed \(u_{00}=1\) gives
\(c_0=0\), so the diagonal identity and unary delta would then follow from
the already proved reductions. Until (7.1) is proved, those conclusions and
every period-two/AK3/AC conclusion remain open.

<!-- AK3_PURE_P_Q_SECTION_7_1_END -->

### 7.2 Quadratic theorem and diagonal closure

The primary all-power certificate and a genuinely independent replay are
frozen in
<code>.scratch/period_two_diagonal_pure_p_quadratic_certificate.md</code>.
Neither artifact imposes an expected value of \(Q\).  They reconstruct the
four exhaustive cells

\[
 i=0,\qquad i=1,\qquad i=2,\qquad i\geq3
 \tag{7.8}
\]

from the low-level source rows.  In every cell the 48 prefix parities in
(7.6) have integer sum 21.  The independent replay also reconstructs the
96-token stream directly and obtains the same parity from all
\(\binom{96}{2}=4560\) kernel pairs.  Thus (7.7) gives

\[
 \boxed{Q(q_i)=1\qquad(i\geq0).}
 \tag{7.9}
\]

Combining (7.9) with the complete raw theorem (4.13) and old--new theorem
(6.27) gives

\[
\begin{aligned}
 \mathscr C(A_i^\Delta,q_i)
 &=L(q_i)+\mathbb B(A_i^\Delta,q_i)+Q(q_i)\\
 &=0+1+1=0.
\end{aligned}
 \tag{7.10}
\]

Equation (0.3) therefore yields

\[
 c_{i+1}=c_i\qquad(i\geq0).
 \tag{7.11}
\]

The exact seed \(u_{00}=1\), together with
\(u_{00}=c_0+1\), gives \(c_0=0\).  Hence

\[
 \boxed{c_i=0,\qquad u_{ij}=[j=i]=\delta_{ij}.}
 \tag{7.12}
\]

It follows at once that

\[
 \boxed{\mathcal D_{ij}=0}
 \qquad\text{and}\qquad
 \boxed{I_{ij}=[i-j=-1]+[i-j=0]}
 \tag{7.13}
\]

for all \(i,j\geq0\).  These are complete-cover unary identities.  They do
not solve the nonabelian free-group lifting defect, the unresolved companion
cross kernels, AK(3), stable Andrews--Curtis, or Andrews--Curtis.
