# Old--new cut as an endpoint-potential problem

Date: 2026-07-29

## 0. Status

This note proves a collision-safe discrete-Stokes reduction for the old
(P,C,Q) rows.  It reduces 305 source positions to one two-ray (P)
identity, one six-family (C) endpoint identity, and three paired (Q)
rectangles.  It does not prove those endpoint-potential identities.

## 1. The chronology kernel is an inversion kernel

Let (chi) be the certified literal chronology: AST order between distinct
correction occurrences, increasing module shortlex within a positive
occurrence, and decreasing module shortlex within a negative occurrence.
For a token (x), let (lambda(x)) be its transported label.  For distinct
tokens put

\[
 kappa(x,y)=
 \begin{cases}
 [\lambda(x)<_{\rm sl}\lambda(y)],&x<_{\chi}y,\\
 [\lambda(y)<_{\rm sl}\lambda(x)],&y<_{\chi}x,
 \end{cases}
 \tag{1.1}
\]

and put (kappa(x,x)=0).  This is the inversion indicator between
chronology and decreasing transported-label shortlex, with chronology as a
tie-breaker.  Therefore, for collision-aggregated masks (u,v),

\[
 Q(u+v)+Q(u)+Q(v)=\mathbb B(u,v).
 \tag{1.2}
\]

The statement includes the zero diagonal and the negative-occurrence order
reversal; neither is added later.

## 2. Forest Stokes lemma

Fix the already collision-aggregated 84-token mask
(T=b_{n,d}): twelve slot-zero tokens and two occurrence copies of each of
the 36 odd path fibers among the 53 integral fibers.

For an oriented edge (e) of a source tree, let (eta(e)) be its complete
occurrence footprint after the signed incidence rule.  Define

\[
 omega_T(e)=\mathbb B(\eta(e),T).
 \tag{2.1}
\]

Choose a base vertex in each tree component and set

\[
 psi_T(x)=\sum_{e\in[\mathrm{base},x]}\omega_T(e).
 \tag{2.2}
\]

**Lemma 2.1 (forest Stokes).** For every two vertices (x,y) in one
component,

\[
 \boxed{
 mathbb B(\eta([x,y]),T)=\psi_T(x)+\psi_T(y).
 }
 \tag{2.3}
\]

### Proof

The two base paths have the common initial segment from the base vertex to
the branch point of (x) and (y).  Those edges occur twice and vanish in
(mathbb F_2), leaving the unique path ([x,y]).  Apply bilinearity in the
first argument.  This remains valid when provenance rows collide because
the collision-safe row expansion first sums integral coefficients and then
uses the same mod-two linear functional against the already aggregated
(T).  \(square\)

## 3. Exact endpoint obligations

Put (a=d-1) and (i=a+n+1).  For the six approved source paths define

\[
\begin{aligned}
 x^P_{\nu,h}&=\operatorname{cvert}(p_\nu^h r_\nu),\\
 x^C_{\nu,0}&=\operatorname{cvert}(p_\nu^i r_\nu),&
 x^C_{\nu,1}&=\operatorname{cvert}(c_\nu p_\nu^i r_\nu),\\
 x^Q_{\nu,h}&=\operatorname{cvert}(q_\nu^h c_\nu p_\nu^i r_\nu).
\end{aligned}
 \tag{3.1}
\]

Since every (epsilon_\nu) becomes one modulo two, Lemma 2.1 gives

\[
 E_P(h)=\sum_{\nu=1}^6
 \bigl(\psi_T(x^P_{\nu,h+1})+\psi_T(x^P_{\nu,h})\bigr),
 \tag{3.2}
\]

\[
 E_C=\sum_{\nu=1}^6
 \bigl(\psi_T(x^C_{\nu,1})+\psi_T(x^C_{\nu,0})\bigr),
 \tag{3.3}
\]

and

\[
 E_Q(h)=\sum_{\nu=1}^6
 \bigl(\psi_T(x^Q_{\nu,h+1})+\psi_T(x^Q_{\nu,h})\bigr).
 \tag{3.4}
\]

The occurrence footprint in (omega_T) is exactly

\[
 \text{slot }2:(o_1^+,o_6^-),\qquad
 \text{slot }3:(o_9^+,o_{14}^-),\qquad
 \text{slot }4:(o_{15}^+,o_{16}^-).
 \tag{3.5}
\]

Thus the negative-order rule is already inside (psi_T).

## 4. Finite family collapse

The literal source paths give

\[
 P_2=P_6,qquad P_3=P_4=P_5=:P_*.
 \tag{4.1}
\]

The paired terms (2,6) vanish and three copies of (P_*) leave one.
Consequently (3.2) is exactly the two-ray obligation

\[
 \boxed{
 E_P(h)=
 \Delta_{p_1}\psi_T(p_1^h\texttt{ct})
 +\Delta_{p_*}\psi_T(p_*^h\texttt{ct}).
 }
 \tag{4.2}
\]

Likewise

\[
 Q_1=Q_5,qquad Q_2=Q_3,qquad Q_4=Q_6,
 \tag{4.3}
\]

so (3.4) is the xor of three four-endpoint rectangles, one for each
pair ((1,5),(2,3),(4,6)).

No analogous common-action collapse proves (4.2): (P_1) and (P_*) are
distinct canonical quotient actions.  Shortlex is not invariant under
arbitrary deck multiplication, and the (b)-mask cannot be split into its
virtual pre-collision path provenance.

### 4.1 Exact integral cancellations before comparison

The approved raw rows give the following collision-first reductions.

1. Six base atoms and the slot-zero anchor have even integral coefficients.
   Only ((s_3,\texttt{TTct},-1)) and
   ((s_4,\texttt{Tct},+1)) remain.
2. In (P), rows ((P_2,k)) and ((P_6,k)) pair for
   (0\le k<16), while ((P_4,k)) and ((P_5,k)) pair for
   (0\le k<18).  The residual is
   (P_1[0..13]\sqcup P_3[0..17]), hence 32 rows.
3. In (C), the same pairs cancel for (k<19) and (k<18),
   respectively.  The residual is
   (C_1[0..13]\sqcup C_3[0..17]\sqcup
     C_4[18..19]\sqcup C_5[18..20]\sqcup C_6[19..20]),
   hence 39 rows.
4. No full-schema collision pairs the 92 positive (Q)-rows.  Equal raw
   (Q)-words have different following (C/P/)root contexts.

The singleton is exactly the `g0:00` slot-zero footprint inside (T).  Its
self-block vanishes: diagonal pairs are zero and the two orders of every
off-diagonal pair cancel by symmetry.  The claimed singleton value one must
therefore arise in its remaining block against `g0:01` and the 72 path
tokens.

### 4.2 Smallest collision-safe comparison table

After the reductions above, a direct certificate needs at most 9,408 old-row
loads rather than 1,491,840 raw pair records:

\[
\begin{array}{c|r|r|r}
\text{family}&\text{rows/cell}&\text{cells}&\text{loads}\\\hline
\text{fixed}&70&16&1120\\
\text{base}&2&16&32\\
\text{singleton}&1&16&16\\
P&32&54&1728\\
C&39&16&624\\
Q^+&92&64&5888\\\hline
&&&9408.
\end{array}
 \tag{4.4}
\]

The 54 (P)-cells are the nonempty seed intersections with
(h+r=a+n); the 64 (Q)-cells use (a=h+k).  Each load row must name its
integral collision fiber, occurrence footprint, equality exclusions, signed
module order, transported-label comparison method and outcome, and the
parity count of each comparison histogram.  Counts must cover all 84 tokens
of (T) at every footprint occurrence.  Aggregate digests without these
histograms are not an auditable parity proof.

## 5. Exact remaining theorem

It is sufficient to prove the endpoint-potential identities

\[
 E_P(h)=0,qquad E_Q(h)=0,qquad E_C=[a=0],
 \tag{5.1}
\]

for every admissible parameter, together with the finite identities

\[
 E_{\rm fixed}=0,qquad E_{\rm base}=0,qquad
 E_{\rm singleton}=1.
 \tag{5.2}
\]

Then

\[
 \mathbb B(A_{n,d},b_{n,d})
 =1+[a=0]=[d>1],
 \tag{5.3}
\]

which is independent of (n) and proves the remaining positive-chamber
covariance lemma.

The certified terminal crossing in the first (Q)-family shows why a
rowwise pairing cannot prove (5.1).  Cancellation must occur after the
family endpoint collapse, across the other endpoint potentials or the
collision-aggregated (b)-fibers.  Equations (4.2)--(4.3), rather than all
305 interior rows, are the narrow theory target.
