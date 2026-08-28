# Complete finite old terms and positive-chamber old--new covariance

## Status and scope

This note proves all three positive-chamber finite old-term identities and
combines them with the powered endpoint theorem:

\[
 \boxed{
 E_{\rm fixed}=0,\qquad E_{\rm base}=0,\qquad
 E_{\rm singleton}=1,}
 \tag{0.1}
\]

\[
 \boxed{
 \mathbb B(A_{n,d},b_{n,d})
 =1+[d=1]=[d>1]\qquad(d\geq1).}
 \tag{0.2}
\]

The singleton old row is the collision-aggregated slot-zero module atom
\(y_0=y_{ij}\), named \(\texttt{g0:00}\).  Its decorated footprint consists
of the six slot-zero occurrence copies

\[
 \mathcal O_0=\{3,4,7,8,11,12\}.
 \tag{0.3}
\]

The actual mask \(T=b\) has collision-aggregated slot-zero support

\[
 S_0=\{y_0,y_1\},
 \qquad y_1=y_{i,j+1}.
 \tag{0.4}
\]

All statements are over \(\mathbb F_2\) after integral coefficients have
been aggregated at their canonical coordinates.  Equation (0.2) proves only
the positive-chamber old--new covariance lemma.  Other chambers, boundary
values, and the later unary calculation are outside this note and are
treated in subsequent documents.  No period-two free-group lift, AK(3),
stable Andrews--Curtis, or Andrews--Curtis conclusion follows here.

## 1. Reduction to six chronology prefixes

Work in the positive chamber

\[
 i,j\geq0,\qquad d=i-j\geq1.
 \tag{1.1}
\]

For an active occurrence \(o\), retain the raw prefix until the final
canonicalization,

\[
 \tau_o(v)=\operatorname{cvert}(q_ov).
 \tag{1.2}
\]

Let \(\iota_o(v)\) denote the decorated occurrence token.  The
occurrence-prefix theorem gives

\[
 H_T(\iota_o(v))
 =\#\{t\in T:\lambda(t)=\tau_o(v),\
              \operatorname{occ}(t)<o\}\pmod2.
 \tag{1.3}
\]

There is no same-occurrence contribution: \(\tau_o\) is bijective, so one
label names at most one coordinate in occurrence \(o\), and the strict
diagonal rule excludes the queried token itself.

The exact one-atom singleton load is therefore

\[
\begin{aligned}
 E_{\rm singleton}
 &=[y_0\in S_0]
   +\sum_{o\in\mathcal O_0}H_T(\iota_o(y_0))\\
 &=1+\Theta_0,
\end{aligned}
 \tag{1.4}
\]

where

\[
 \Theta_0
 :=\sum_{o\in\mathcal O_0}H_T(\iota_o(y_0)).
 \tag{1.5}
\]

It remains only to evaluate these six equal-label occurrence prefixes.

## 2. The six new outer labels

Use the powered endpoint notation

\[
 v_\nu(h)
 =\operatorname{cvert}(q_\nu^h c_\nu p_\nu^i r_\nu),
 \tag{2.1}
\]

with the full quotient product formed before
\(\operatorname{cvert}\).  The exact adjacent-source factorization gives
the following occurrence-to-endpoint map:

| slot-zero occurrence \(o\) | transported singleton label \(\tau_o(y_0)\) |
|---:|:---|
| \(3\) | \(v_1(d)\) |
| \(4\) | \(v_5(d)\) |
| \(7\) | \(v_4(d)\) |
| \(8\) | \(v_6(d)\) |
| \(11\) | \(v_3(d)\) |
| \(12\) | \(v_2(d)\) |

Put

\[
 K_d=K_Q(d),\qquad
 \beta_E=K_Q(d-1)+K_Q(d)=K_{d-1}+K_d.
 \tag{2.2}
\]

The exact reduced terminal graph has six pairwise distinct new endpoints
\(v_\nu(d)\).  They are also distinct from all six old endpoints
\(v_\nu(d-1)\).  Its collision-first edge reduction shows that no
unlisted old or cross-connector edge is incident at a new endpoint.

Consequently, apart from the queried slot-zero token, the same-label
\(T\)-tokens at \(v_\nu(d)\) are precisely the occurrence copies of the
\(\beta_E\)-edges incident there.  Indeed, every supported stored edge
contributes its head label at its positive occurrence and its tail label
at its negative occurrence.  The other five \(y_0\)-copies have distinct
new labels, while the six \(y_1\)-copies have the distinct old labels.
Within the queried occurrence, bijectivity of \(\tau_o\) also gives
\(\tau_o(y_1)\ne\tau_o(y_0)\).

Thus the six values in (1.5) can be read solely from the terminal incidence
of \(K_d\).

## 3. Exact terminal-incidence table

For the stored edge pairs, the head occurrence is positive and the tail
occurrence is negative:

\[
\begin{array}{c|c|c}
\text{slot}&\text{head occurrence}&\text{tail occurrence}\\\hline
2&1&6\\
3&9&14\\
4&15&16
\end{array}
 \tag{3.1}
\]

The relevant stored-letter cases are as follows.  A terminal
\(\texttt G\) in each displayed \(Q\)- or short-connector word places the
new endpoint at the slot-three head, hence occurrence \(9\).  At
\(v_3(d)\), the terminal \(\texttt b\) of the long \(Q_2\)-word places
that endpoint at the slot-two head, while the initial \(\texttt b\) of
\(z^+\) places it at the slot-two tail.  The initial \(\texttt a\) of
\(w_3^+\) and \(w_2^+\) places the corresponding new endpoint at the
slot-four head.

With

\[
 z^+=S_z^{(3)}(d),\qquad
 w_3^+=S_w^{(3)}(d),\qquad
 w_2^+=S_w^{(2)}(d),
 \tag{3.2}
\]

the complete incidence audit is:

| new endpoint | incident edge source in \(K_d\) | stored endpoint case | equal-label occurrence set |
|:---|:---|:---|:---|
| \(v_1(d)\) | long connector, terminal \(Q_1\) letter \(\texttt G\) | slot-three head | \(\{9\}\) |
| \(v_5(d)\) | \(z^+=\texttt{baG}\), final \(\texttt G\) | slot-three head | \(\{9\}\) |
| \(v_4(d)\) | \(w_3^+=\texttt{aG}\), final \(\texttt G\) | slot-three head | \(\{9\}\) |
| \(v_6(d)\) | \(w_2^+=\texttt{aG}\), final \(\texttt G\) | slot-three head | \(\{9\}\) |
| \(v_3(d)\) | long connector, terminal \(Q_2\) letter \(\texttt b\) | slot-two head | \(\{1\}\) |
| \(v_3(d)\) | \(z^+=\texttt{baG}\), initial \(\texttt b\) | slot-two tail | \(\{6\}\) |
| \(v_3(d)\) | \(w_3^+=\texttt{aG}\), initial \(\texttt a\) | slot-four head | \(\{15\}\) |
| \(v_2(d)\) | \(w_2^+=\texttt{aG}\), initial \(\texttt a\) | slot-four head | \(\{15\}\) |

After union at each collision-aggregated endpoint, this is

\[
\begin{aligned}
 I(v_1(d))&=\{9\},&
 I(v_5(d))&=\{9\},\\
 I(v_4(d))&=\{9\},&
 I(v_6(d))&=\{9\},\\
 I(v_3(d))&=\{1,6,15\},&
 I(v_2(d))&=\{15\}.
\end{aligned}
 \tag{3.3}
\]

No occurrence \(14\) or \(16\) appears because none of the listed new
endpoints is the tail of its incident slot-three or slot-four stored edge.

## 4. Chronology-prefix parity

For the singleton copy at boundary occurrence \(o\), formula (1.3) counts
only members of the corresponding set \(I(\tau_o(y_0))\) whose occurrence
number is strictly smaller than \(o\).  The six rows are:

| boundary occurrence \(o\) | new label | incident occurrence set | strictly earlier set | integer count | \(H_T(\iota_o(y_0))\) |
|---:|:---|:---|:---|---:|---:|
| \(3\) | \(v_1(d)\) | \(\{9\}\) | \(\varnothing\) | \(0\) | \(0\) |
| \(4\) | \(v_5(d)\) | \(\{9\}\) | \(\varnothing\) | \(0\) | \(0\) |
| \(7\) | \(v_4(d)\) | \(\{9\}\) | \(\varnothing\) | \(0\) | \(0\) |
| \(8\) | \(v_6(d)\) | \(\{9\}\) | \(\varnothing\) | \(0\) | \(0\) |
| \(11\) | \(v_3(d)\) | \(\{1,6,15\}\) | \(\{1,6\}\) | \(2\) | \(0\) |
| \(12\) | \(v_2(d)\) | \(\{15\}\) | \(\varnothing\) | \(0\) | \(0\) |

The earlier-occurrence counts are therefore exactly

\[
 (0,0,0,0,2,0).
 \tag{4.1}
\]

Every entry is even, so

\[
 \boxed{\Theta_0=0.}
 \tag{4.2}
\]

Substitution into (1.4) proves

\[
 \boxed{E_{\rm singleton}=1.}
 \tag{4.3}
\]

## 5. Exact base exclusion

The two residual base atoms are the stored edges
\(E_3(\texttt{TTct})\) and \(E_4(\texttt{Tct})\).  The occurrence-sweep
formulas give

\[
\begin{aligned}
 E_{\rm base}
 &=\omega_T(E_3(\texttt{TTct}))
   +\omega_T(E_4(\texttt{Tct}))\\
 &=R_3(\texttt{ctcT})
   +D_4(\texttt{Tct})
   +D_4(\texttt{ct}).
\end{aligned}
 \tag{5.1}
\]

Here the first edge has slot-three head \(\texttt{ctcT}\) and tail
\(\texttt{Tct}\), while the second joins \(\texttt{Tct}\) to
\(\texttt{ct}\).  Equivalently, the two atoms form the radius-two core
path

\[
 \texttt{ct}
 \mathbin{-}^{E_4(\texttt{Tct})}
 \texttt{Tct}
 \mathbin{-}^{E_3(\texttt{TTct})}
 \texttt{ctcT}.
 \tag{5.2}
\]

The paired-boundary identities are

\[
 R_3=\partial(\Pi_1+\Pi_2+\beta_2),
 \qquad
 D_4=\partial\beta_4.
 \tag{5.3}
\]

It is therefore enough to show that the contributing chains avoid all
three vertices of (5.2).  The exact reduced path forms give the following
same-forest distance bounds.

- The rooted word \(W_1(d-1)\) has length at least \(28\) and begins
  \(\texttt{aB}\).  It therefore shares exactly the first core edge
  \(\texttt a\), and its contributing terminal segment remains at distance
  at least \(27\) from the radius-two core.
- The rooted word \(W_3(d-1)\) has length at least \(36\) and begins
  \(\texttt{aG}\), so the two-edge core is its initial prefix before the
  word diverges.  Families \(4\) and \(5\) may retrace their short \(w\)-
  and \(z\)-connectors, but only as far as this basepoint, which is at
  distance at least \(34\) from the core.
- Family \(6\) lies in the other forest component.  It may retrace its
  short \(w\)-connector, but only as far as \(W_2(d-1)\).  Its exact reduced
  word is

  \[
   W_2=P_2^iC_2Q_2^h,
   \qquad
   |W_2|=14i+19+14h\geq33.
   \tag{5.4}
  \]

These are bounds after the allowed retracing.  The argument does not assume
that the paths are monotone outward: the short connectors may be traversed
back toward their common block, but the stated nearest vertices are still
far outside the radius-two core.

The subchains \(\beta_2\) and \(\beta_4\) are obtained by
collision-aggregating these same family edges.  Collision aggregation can
delete coincident edges but cannot create a new core edge or vertex.
Consequently \(\Pi_1,\Pi_2,\beta_2,\beta_4\) all avoid
\(\texttt{ct}\), \(\texttt{Tct}\), and \(\texttt{ctcT}\).  Hence their
three relevant boundary coefficients vanish:

\[
 R_3(\texttt{ctcT})=0,\qquad
 D_4(\texttt{Tct})=0,\qquad
 D_4(\texttt{ct})=0.
 \tag{5.5}
\]

Substitution into (5.1) proves

\[
 \boxed{E_{\rm base}=0.}
 \tag{5.6}
\]

## 6. Exact fixed-core exclusion

Let \(\mathcal F_{\rm tok}\) be the authoritative set of 70 fixed-token
coordinates, and let \(\mathcal L_{\rm fix}\) be its set of 27 distinct
canonical quotient labels.  Their multiplicities, component roots, and
exact reduced source-forest paths are:

| canonical label | multiplicity | component root | exact reduced path | distance |
|:---|---:|:---|:---|---:|
| \(\mathrm{eps}\) | \(4\) | \(\mathrm{eps}\) | empty | \(0\) |
| \(\texttt t\) | \(4\) | \(\mathrm{eps}\) | \(\texttt A\) | \(1\) |
| \(\texttt{cT}\) | \(2\) | \(\texttt{ct}\) | \(\texttt{aGaGb}\) | \(5\) |
| \(\texttt{ct}\) | \(1\) | \(\texttt{ct}\) | empty | \(0\) |
| \(\texttt{Tct}\) | \(2\) | \(\texttt{ct}\) | \(\texttt a\) | \(1\) |
| \(\texttt{cTT}\) | \(2\) | \(\texttt{ct}\) | \(\texttt{aGaGaGb}\) | \(7\) |
| \(\texttt{Tctt}\) | \(2\) | \(\texttt{ct}\) | \(\texttt g\) | \(1\) |
| \(\texttt{cTct}\) | \(2\) | \(\texttt{ct}\) | \(\texttt{aGb}\) | \(3\) |
| \(\texttt{ctcT}\) | \(5\) | \(\texttt{ct}\) | \(\texttt{aG}\) | \(2\) |
| \(\texttt{cTTct}\) | \(2\) | \(\mathrm{eps}\) | \(\texttt{BaGb}\) | \(4\) |
| \(\texttt{cTctt}\) | \(2\) | \(\mathrm{eps}\) | \(\texttt{BgAb}\) | \(4\) |
| \(\texttt{ctcTT}\) | \(4\) | \(\mathrm{eps}\) | \(\texttt{aG}\) | \(2\) |
| \(\texttt{cTTctt}\) | \(2\) | \(\texttt{ct}\) | \(\texttt{BaGb}\) | \(4\) |
| \(\texttt{ctcTTT}\) | \(4\) | \(\texttt{ct}\) | \(\texttt{aGaGbaG}\) | \(7\) |
| \(\texttt{ctcTcT}\) | \(2\) | \(\texttt{ct}\) | \(\texttt{aGaG}\) | \(4\) |
| \(\texttt{ctcTct}\) | \(4\) | \(\mathrm{eps}\) | \(\texttt{BgA}\) | \(3\) |
| \(\texttt{ctcTTTT}\) | \(2\) | \(\texttt{ct}\) | \(\texttt{aGaGaGbaG}\) | \(9\) |
| \(\texttt{ctcTTct}\) | \(4\) | \(\mathrm{eps}\) | \(\texttt G\) | \(1\) |
| \(\texttt{ctcTTTct}\) | \(2\) | \(\texttt{ct}\) | \(\texttt{aGbaG}\) | \(5\) |
| \(\texttt{ctcTTctt}\) | \(2\) | \(\mathrm{eps}\) | \(\texttt{AG}\) | \(2\) |
| \(\texttt{ctcTcTct}\) | \(4\) | \(\mathrm{eps}\) | \(\texttt B\) | \(1\) |
| \(\texttt{ctcTTTTct}\) | \(2\) | \(\mathrm{eps}\) | \(\texttt{BaGbaG}\) | \(6\) |
| \(\texttt{ctcTTTctt}\) | \(2\) | \(\mathrm{eps}\) | \(\texttt{BgAbaG}\) | \(6\) |
| \(\texttt{ctcTcTctt}\) | \(2\) | \(\texttt{ct}\) | \(\texttt B\) | \(1\) |
| \(\texttt{ctcTTTTctt}\) | \(2\) | \(\texttt{ct}\) | \(\texttt{BaGbaG}\) | \(6\) |
| \(\texttt{ctcTcTcTct}\) | \(2\) | \(\mathrm{eps}\) | \(\texttt{BaG}\) | \(3\) |
| \(\texttt{ctcTcTcTctt}\) | \(2\) | \(\texttt{ct}\) | \(\texttt{BaG}\) | \(3\) |

Here an empty path denotes the listed component root.  The multiplicities
sum to \(70\).  Every displayed forest word is visibly reduced, and direct
application of that word in the listed source-tree component gives the
displayed canonical label.  Thus every fixed label lies at exact
source-forest distance at most \(9\) from its component root.

This finite table came from one guarded authoritative subgroup rewrite.
Each row is independently readable and verifiable as an exact reduced path;
the table is a finite premise, not a sampled assertion about a powered
family.

Every label of \(T\) is either a transported slot-zero boundary vertex or
the head or tail of a supported \(\beta_E\)-edge.  The reviewed terminal
decomposition in AK3_OLD_NEW_POWERED_ENDPOINT_CONNECTORS.md, Sections 4--5,
together with the same-forest \(W_2\) bound proved in Section 5 above, keeps
every such label at source-forest distance at least \(28\) in the
\(\texttt{ct}\)-component and at least \(33\) in the
\(\mathrm{eps}\)-component, after all permitted short-connector retracing.
Collision aggregation can delete coincident edges but cannot create a
nearer label.  Comparing distances inside the same source-tree component
therefore gives

\[
 \boxed{H_T(x)=0\qquad(x\in\mathcal F_{\rm tok}).}
 \tag{6.1}
\]

The fixed tokens lie outside the correction blocks.  Each complete earlier
\(T\)-occurrence block has one of the even collision-aggregated support
sizes

\[
 |S_0|=2,\qquad |S_2|=8,\qquad
 |S_3|=14,\qquad |S_4|=14.
 \tag{6.2}
\]

Hence the literal-chronology rank of every fixed token is

\[
 \boxed{R_T^\chi(x)=0\qquad(x\in\mathcal F_{\rm tok}).}
 \tag{6.3}
\]

The exact two-rank formula (3.4) from
AK3_OLD_NEW_CHRONOLOGY_RANK_POTENTIAL.md, Section 3, and the
any-decorated-coordinate identity (4.3) from
AK3_OLD_NEW_EVEN_LABEL_TIE_COCHAIN.md, Section 4, give

\[
 \Lambda_T(x)=R_T^\chi(x)+H_T(x)=0
 \qquad(x\in\mathcal F_{\rm tok}).
 \tag{6.4}
\]

Summing with the fixed multiplicities therefore proves

\[
 \boxed{
 E_{\rm fixed}
 =\sum_{x\in\mathcal F_{\rm tok}}\Lambda_T(x)=0.}
 \tag{6.5}
\]

## 7. Positive-chamber old--new covariance

AK3_OLD_NEW_POWERED_ENDPOINT_CONNECTORS.md, Section 5, proves that the
combined powered \(P,C,Q\) forest load is

\[
 E_{P/C/Q}=[d=1].
 \tag{7.1}
\]

The finite terms are (4.3), (5.6), and (6.5).  Therefore

\[
\begin{aligned}
 \mathbb B(A_{n,d},b_{n,d})
 &=E_{\rm fixed}+E_{\rm base}+E_{\rm singleton}+E_{P/C/Q}\\
 &=0+0+1+[d=1]\\
 &=1+[d=1]=[d>1]
 \qquad(d\geq1).
\end{aligned}
 \tag{7.2}
\]

The result is independent of \(n\).  This proves the positive-chamber
old--new covariance lemma and nothing beyond it.

## 8. Remaining boundary and hostile audit

Other chambers, boundary values, and the unary calculation are outside this
note and are treated in subsequent documents.  The period-two free-group
lift, AK(3), stable Andrews--Curtis, and Andrews--Curtis are not proved
here.

**Hostile-audit note.**  No proof above uses the rejected cross-metric
annulus argument.  The singleton proof uses only the collision-aggregated
terminal forest, exact head/tail occurrence labels, bijectivity of each
\(\tau_o\), and literal AST occurrence order.  The base proof uses
same-forest reduced-path distances and explicitly permits the short
connector retracing described in Section 5.  The fixed proof compares only
exact distances inside the same source-tree component; its 27-row table is
a finite exact premise, not evidence extrapolated from sampled powers.
