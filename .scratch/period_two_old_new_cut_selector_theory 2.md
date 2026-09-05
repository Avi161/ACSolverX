# Old--new cut: exact selector schema and translation no-go

Date: 2026-07-29

## 0. Status

This note does not prove or refute

\[
 \mathbb B(A_{n+1,d},b_{n+1,d})
 =\mathbb B(A_{n,d},b_{n,d})
 \qquad(n\ge0,\ d\ge1).
 \tag{0.1}
\]

It gives the exact collision-safe one-selector formula for (0.1), an
exhaustive seed partition for the old repetition selector, and a narrow
no-go theorem for a proof by one common order-preserving diagonal
translation.  The remaining obligation is a materialized Presburger
comparison partition and modulo-two fiber count.  No finite grid is used.

## 1. Collision-first activity and linear expansion

Let \(\mathcal T_\delta(a,n)\) be the certified activity-token set of
\(b_{n+\delta,d}\), where \(a=d-1\) and \(\delta\in\{0,1\}\).  The approved
certificate constructs it only after integral aggregation.  It has 84
pairwise distinct token coordinates: twelve slot-zero tokens and 72 tokens
from 53 path collision fibers, 36 of them odd.

For a current coordinate \((s,v)\), put

\[
 \Lambda_\delta(s,v)
 =\sum_{o:s_o=s}
   \sum_{\substack{t\in\mathcal T_\delta\\
                    \operatorname{coord}(t)\ne(o,v)}}
   \xi((o,v),t).
 \tag{1.1}
\]

The label of \((o,v)\) is
\(\tau_o(v)=\operatorname{cvert}(q_ov)\), with the literal raw action
\(q_o\); in particular `tc` is not parsed through the module interface.
Different occurrences use literal AST order.  At a common positive
occurrence module order is increasing shortlex, and at a common negative
occurrence it is decreasing shortlex.  The exclusion in (1.1) is the exact
zero diagonal of \(\mathbb B\).

Suppose an integral old current is presented by signed provenance rows

\[
 C_s=\sum_r c_r e_{v_r}.
 \tag{1.2}
\]

Although activity is formed after collision aggregation, bilinearity gives

\[
 \boxed{
 \mathbb B(a_C,b_{n+\delta,d})
 =\sum_r(c_r\bmod2)\Lambda_\delta(s_r,v_r).}
 \tag{1.3}
\]

Indeed, rows at a common coordinate sum first in \(\mathbb Z\), and both
sides use that sum modulo two.  Equal rows therefore cancel twice in the
right side.  If an old row equals a token of \(b\) at the same occurrence,
the corresponding summand is zero on both sides by the exclusion in (1.1).
Thus (1.3) is not virtual rowwise activity; it is a linear expansion of the
already aggregated old factor against the already aggregated \(b\)-factor.

## 2. Exact positive-chamber row formula

Put \(i=n+d=a+n+1\).  For a fixed literal token \(p\), define

\[
 \Lambda_\delta^{\rm fix}(p)
 =\sum_{t\in\mathcal T_\delta}\xi(p,t).
 \tag{2.1}
\]

Use the 100 stored \(P\)-positions, 113 stored \(C\)-positions, and 92
stored \(Q\)-positions from the approved source manifest.  Their exact
positive-chamber vertices are

\[
\begin{aligned}
 v^P_R(h)
 &=\operatorname{cvert}
   (m_RE(P_{\nu,<k})p_\nu^h r_\nu),
 &&0\le h<i+\delta,\\
 v^C_R(i+\delta)
 &=\operatorname{cvert}
   (m_RE(C_{\nu,<k})p_\nu^{i+\delta}r_\nu),\\
 v^{Q,+}_R(i+\delta,h)
 &=\operatorname{cvert}
   (m_RE(Q_{\nu,<k})q_\nu^h c_\nu
     p_\nu^{i+\delta}r_\nu),
 &&0\le h<d.
\end{aligned}
\tag{2.2}
\]

Let \(c_R\) retain the integral source and incidence signs.  The negative
\(Q\)-row domains are empty on \(d\ge1\).  The doubled anchors and the
coefficient \(2e_T\) are even.  Consequently

\[
\boxed{
\begin{aligned}
 H_\delta
 :={}&\mathbb B(A_{n+\delta,d},b_{n+\delta,d})\\
 ={}&\sum_{p\in F_{70}}\Lambda_\delta^{\rm fix}(p)
 +\sum_{s,v}(B_s(v)\bmod2)\Lambda_\delta(s,v)
 +\Lambda_\delta(0,y_{i+\delta,j+\delta})\\
 &+\sum_{R\in P}\sum_{0\le h<i+\delta}
     c_R\Lambda_\delta(s_R,v^P_R(h))\\
 &+\sum_{R\in C}c_R\Lambda_\delta(s_R,v^C_R(i+\delta))\\
 &+\sum_{R\in Q^+}\sum_{0\le h<d}
     c_R\Lambda_\delta(s_R,v^{Q,+}_R(i+\delta,h)).
\end{aligned}}
\tag{2.3}
\]

Equation (0.1) is exactly \(H_0+H_1=0\).

The common \(P\)-row domains telescope syntactically to

\[
 \sum_{h=0}^{i-1}c_R
 \bigl(\Lambda_0(s_R,v_R^P(h))
      +\Lambda_1(s_R,v_R^P(h))\bigr)
 +c_R\Lambda_1(s_R,v_R^P(i)).
 \tag{2.4}
\]

The \(C\)-rows give one translated pair, and each \(Q^+\)-row gives \(d\)
translated pairs.  Hence every comparison record in (2.3)--(2.4) has at
most one unbounded old selector.

## 3. Exact selector coordinates and seed partition

For a common \(P\)-selector put

\[
 u=h,\qquad v=i-1-h=a+n-h.
 \tag{3.1}
\]

Then \(u,v\ge0\) and \(u+v=a+n\).  The terminal shifted row in (2.4) is
the separate boundary \(h=i=a+n+1\).  For a \(Q^+\)-selector put

\[
 u=h,\qquad v=d-1-h=a-h,
 \tag{3.2}
\]

so \(u,v\ge0\) and \(u+v=a\).

An exhaustive disjoint *seed* partition is obtained by putting every
nonnegative coordinate among \(a,n,u,v\) in

\[
 0,\quad1,\quad2,\quad\ge3,
 \tag{3.3}
\]

and intersecting with (3.1) for \(P\), or (3.2) for \(Q^+\).  The bounded
fixed/base/singleton/\(C\) queries use the approved sixteen
\((a,n)\)-seeds.  This is only an exhaustive starting partition.  The
threshold-three theorem proved for the 84 \(b\)-tokens does not by itself
prove that (3.3) is a final normal-form partition for an old row.

For each old-row/\(b\)-token query, the generic restricted powered-product
normalizer must refine the seed by the following exact predicates:

1. the selected canonical quotient template and terminal-`c` branch for
   the old module word and both transported labels;
2. equality of module coordinates, to implement the exclusion in (1.1);
3. module shortlex order at a common occurrence;
4. transported-label shortlex order; and
5. the resulting chronology bit, with polarity reversing the module order
   at a negative occurrence.

The generic theorem makes this a finite disjoint Presburger partition, but
it explicitly permits congruence and general semilinear cells.  Therefore a
claim that (3.3) alone is sufficient would be unproved.

On the emitted cells the remaining scalar is the exact modulo-two fiber
count

\[
 \#_2\{(u,v):u+v=a+n,\ \mathsf{Bit}_{R,t}(a,n,u,v)=1\}
 \tag{3.4}
\]

for \(P\), and the analogous count with \(u+v=a\) for \(Q^+\), together
with the finite terms in (2.3).  Computing (3.4) from the semilinear cell
representation is the first unproved step.

## 4. Narrow no-go for one common translation

The six diagonal right-deck actions reduce literally to

\[
\begin{array}{c|l}
\nu&P_\nu\\ \hline
1&\texttt{cTctttcTcTctttcTcTctttcT}\\
2,6&\texttt{TTctttcTcTctttcTcTctttcTct}\\
3,4,5&\texttt{ctcTTctttcTcTctttcTcTctttcTctcTc}.
\end{array}
\tag{4.1}
\]

These are three distinct canonical quotient words.  Hence there is no
single left action \(T\) whose restriction simultaneously realizes all six
diagonal source translations.  In particular, a proof that pairs every
record by applying one common order-preserving map to both of its module
vertices and labels cannot exist.

This is a narrow no-go only.  It does not exclude a provenance-dependent
involution or a parity pairing that mixes families.  Under the common-action
ansatz, the smallest possible old-family blocks are exactly

\[
 \{1\},\qquad\{2,6\},\qquad\{3,4,5\},
 \tag{4.2}
\]

because these are the equality classes of the literal \(P_\nu\) actions.
The \(b\)-side cannot be split by virtual provenance: its 36 active path
fibers must remain collision-aggregated.  Thus an exact parity proof must
either construct a pairing among the three blocks (4.2), the finite
fixed/base/slot-zero block, and the terminal \(P\)-boundary in (2.4), or
evaluate their combined Presburger counts.

## 5. Relation to the endpoint quadratic

The approved \(Q(b_{n,d})=1\) gives

\[
 H_{n,d}
 =Q(A_{n,d-1})+Q(A_{n,d})+1.
 \tag{5.1}
\]

Therefore the stronger identity

\[
 Q(A_{n,d})=[d=0]\qquad(d\ge0)
 \tag{5.2}
\]

would imply \(H_{n,d}=[d>1]\), hence (0.1).  No all-power proof of (5.2)
is presently available; representative endpoint values cannot be used to
establish it.

## 6. Exact proof boundary

Proved here:

1. collision-safe integral row expansion (1.3);
2. the complete positive-chamber one-selector formula (2.3);
3. the start/end selector coordinates (3.1)--(3.2);
4. an exhaustive seed partition, with no claim that it is already final;
5. the common-translation no-go and its three minimal action classes.

Still open:

1. materializing the old-row/\(b\)-token canonical templates and exact
   Presburger refinements;
2. evaluating the modulo-two fibers (3.4);
3. a cross-family parity involution or a symbolic countercell to (0.1);
4. the seven-family xor, positive-chamber covariance, and all unary-delta
   consequences.

Nothing here proves or refutes Andrews--Curtis or stable Andrews--Curtis.
