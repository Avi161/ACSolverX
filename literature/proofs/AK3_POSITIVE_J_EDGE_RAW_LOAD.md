# Positive-chamber \(j\)-edge raw load

## 0. Statement and scope

Fix

\[
 i,j\geq0,\qquad d=i-j\geq1,\qquad n=j,\qquad a=d-1\geq0.
 \tag{0.1}
\]

Let \(A_{n,d}\) denote the complete endpoint activity at \((i,j)\), and let

\[
 b_{n,d}:=A(i,j)+A(i,j+1)
 \tag{0.2}
\]

be the collision-aggregated increment along the positive-chamber
\(j\)-edge. Thus \(i\) is fixed and \(j\) increases by one. This note proves

\[
 \boxed{L(b_{n,d})=0\qquad(n\geq0,\ d\geq1)}
 \tag{0.3}
\]

from the approved all-power raw certificate, and combines it with the
already proved values

\[
 Q(b_{n,d})=1,
 \qquad
 \mathbb B(A_{n,d},b_{n,d})=[d>1]
 \tag{0.4}
\]

to obtain the positive \(j\)-edge law

\[
 \boxed{J_{n,d}=[d=1].}
 \tag{0.5}
\]

No assertion is made here about a diagonal edge, an \(i\)-edge, another
chamber, the unary delta identity, the period-two lift, AK(3), stable
Andrews--Curtis, or Andrews--Curtis.

## 1. Exact certificate interface

Let \(\mathcal R\) be the set of the \(92\) positive-\(Q\) provenance rows
\(r=(\nu,k)\). For a row \(r\), let \(s(r)\in\{2,3,4\}\) be its slot and put

\[
 \mathcal O_2=\{1,6\},\qquad
 \mathcal O_3=\{9,14\},\qquad
 \mathcal O_4=\{15,16\}.
 \tag{1.1}
\]

The raw companion certificate uses the unshifted positive edge and its
diagonal \(n\)-shift, indexed by \(\epsilon\in\{0,1\}\).  Write their
canonical module vertices as
\(v_{\epsilon,r}(a,n)\), and define the certified paired raw bit

\[
 \delta_{\epsilon,r}(a,n)
 :=\sum_{o\in\mathcal O_{s(r)}}
   \rho_o\bigl(v_{\epsilon,r}(a,n)\bigr)
 \in\{0,1\}.
 \tag{1.2}
\]

This is exactly the construction in
<code>.scratch/period_two_residual_augmented_defect_raw_checker.py</code>:
the literal raw observable and \(\rho\) are defined at lines 25--54; the
row loop, the two endpoint values delta0 and delta1, and the paired
occurrence sum are at lines 57--80. The full observable record used by the
all-power pump is at lines 83--109.

Define the integer, not mod-two, count

\[
 C_a(n):=\sum_{r\in\mathcal R}\delta_{0,r}(a,n).
 \tag{1.3}
\]

The endpoint shift is exact row by row:

\[
 \boxed{\delta_{1,r}(a,n)=\delta_{0,r}(a,n+1).}
 \tag{1.4}
\]

Indeed, the two schemas differ only by
\(p_{\rm offset}=1+\epsilon\) in
<code>.scratch/period_two_inverse_q_companion_checker.py</code>, lines
195--207, and the tagged powered word uses exponent
\(p_{\rm mult}(a+n+p_{\rm offset})\) at lines 212--216. Increasing
\(\epsilon\) from zero to one is therefore literally the same powered word
as increasing \(n\) by one; the final c_vertex operation is the same on
both sides (lines 244--248). No sampled equality or chamber symmetry is
used.

Consequently the integer number of ones in the complete \(184\)-bit row
list is

\[
 \sum_{r\in\mathcal R}
 \bigl(\delta_{0,r}(a,n)+\delta_{1,r}(a,n)\bigr)
 =C_a(n)+C_a(n+1).
 \tag{1.5}
\]

## 2. Certified integer total

The approved raw certificate gives the exact all-power total

\[
 C_a(n)+C_a(n+1)=N_a,
 \qquad
 N_a=
 \begin{cases}
 84,&a=0,\\
 80,&a\geq1,
 \end{cases}
 \tag{2.1}
\]

for every \(a,n\geq0\). The exhaustive representatives
\(0,1,2,\geq3\) in both parameters are declared at
<code>.scratch/period_two_residual_augmented_defect_raw_checker.py</code>,
lines 223--228. The certificate forms the \(184\) bits, checks zero parity,
and checks the exact integer totals \(84\) and \(80\) at lines 229--246.
Its rowwise frontier transitions are lines 248--292, and the intact
primitive-core pump witnesses extending those representatives to all
powers are lines 294--331. Thus (2.1) records an approved all-power
certificate statement, not an inference from the sixteen base points
alone.

## 3. The integer recurrence forces constant half-counts

At fixed \(a\in\{0,1,2,3\}\), the certificate compares every full raw
observable at \(n=3\) with the corresponding observable at \(n=4\): see
<code>.scratch/period_two_residual_augmented_defect_raw_checker.py</code>,
lines 271--280. It compares the complete tuple consisting of first-half
labels, central-equality bits, and \(\rho\), rather than only the final xor.
The absence of transition and central-stability failures is asserted at
lines 291--292. The \(a\)-pump at lines 251--270 and the primitive-core
witnesses at lines 294--331 extend the same rowwise statement to every
\(a\geq0\). Hence

\[
 \delta_{0,r}(a,3)=\delta_{0,r}(a,4)
 \quad(r\in\mathcal R),
 \qquad
 C_a(3)=C_a(4).
 \tag{3.1}
\]

Putting \(n=3\) in (2.1) now gives an equality of ordinary integers:

\[
 2C_a(3)=N_a,
 \qquad
 C_a(3)=
 \begin{cases}
 42,&a=0,\\
 40,&a\geq1.
 \end{cases}
 \tag{3.2}
\]

The approved forward \(n\)-pump preserves each rowwise observable after
the \(3\to4\) frontier, so

\[
 C_a(n)=C_a(3)\qquad(n\geq3).
 \tag{3.3}
\]

For the finite values below the pump frontier, solve (2.1) backwards:

\[
 C_a(n)=N_a-C_a(n+1).
 \tag{3.4}
\]

Since \(C_a(3)=N_a/2\), equation (3.4) successively gives the same value at
\(n=2,1,0\). Therefore

\[
 \boxed{
 C_a(n)=\frac{N_a}{2}
 =\begin{cases}
 42,&a=0,\\
 40,&a\geq1
 \end{cases}
 \qquad(a,n\geq0).}
 \tag{3.5}
\]

This backward step is why the integer totals in (2.1), rather than their
parities alone, are retained.

## 4. Collision aggregation and the nonzero-slot raw load

The raw functional is linear over \(\mathbb F_2\). If several signed source
rows collide at one stored coordinate \((s,v)\), then

\[
 \sum_{r\mapsto(s,v)} c_r R_s(v)
 =\left(\sum_{r\mapsto(s,v)}c_r\right)R_s(v),
 \tag{4.1}
\]

first over the integers and then modulo two. Every authoritative family
and incidence coefficient is \(\pm1\); their fields are retained in
<code>.scratch/period_two_inverse_q_companion_checker.py</code>, lines
177--194. Thus signs reduce to one modulo two, while an even collision fiber
cancels. Evaluating the virtual rows and then aggregating is exactly the
same as first forming the \(36\) odd collision fibers and evaluating their
two occurrence copies. The established collision-aggregated mask contains
twelve slot-zero tokens and two copies of each of those \(36\) path fibers;
see <code>.scratch/period_two_old_new_cut_endpoint_potential.md</code>,
lines 41--45.

The actual positive-edge mask \(b_{n,d}\) is the unshifted
\(\epsilon=0\) copy.  It follows from (1.3) and (3.5) that its
nonzero-slot raw load is

\[
\begin{aligned}
 L_{\ne0}(b_{n,d})
 &=\sum_{r\in\mathcal R}\delta_{0,r}(a,n)\pmod2\\
 &=C_a(n)\pmod2=0,
\end{aligned}
 \tag{4.2}
\]

No cancellation is being claimed row by row before collision aggregation;
(4.1) is the collision-linearity justification for using the certified
provenance sum.

## 5. Slot-zero raw load

The complete slot-zero raw theorem is

\[
 R_0(Y(e,m))=[e<0].
 \tag{5.1}
\]

Its six raw prefixes, exact chamber table, and finite boundary-cascade proof
are in <code>.scratch/period_two_complete_cochain_identity.md</code>, lines
443--496; the theorem itself is lines 498--503. The two slot-zero
coordinates of the \(j\)-edge mask are \(y_{i,j}\) and \(y_{i,j+1}\), as
recorded in
<code>literature/proofs/AK3_OLD_NEW_SINGLETON_TERMINAL_INCIDENCE.md</code>,
lines 31--36. Their exponents in (5.1) are \(d\) and \(d-1\). Because
\(d\geq1\), neither exponent is negative. Hence

\[
 L_0(b_{n,d})=0.
 \tag{5.2}
\]

Combining (4.2) and (5.2) proves (0.3):

\[
 \boxed{L(b_{n,d})=L_0(b_{n,d})+L_{\ne0}(b_{n,d})=0.}
 \tag{5.3}
\]

## 6. Positive \(j\)-edge law

For this increment, exact polarization gives

\[
 J_{n,d}
 =L(b_{n,d})
  +\mathbb B(A_{n,d},b_{n,d})
  +Q(b_{n,d}).
 \tag{6.1}
\]

This identity is the established edge expansion in
<code>.scratch/period_two_seven_family_covariance.md</code>, lines 155--160.
The all-power quadratic theorem

\[
 Q(b_{n,d})=1
 \tag{6.2}
\]

is stated and scoped at lines 7--34 and listed among the proved results at
lines 261--270 of that note. Its checker constructs all \(84\) tokens and
all \(3486\) pairs in
<code>.scratch/period_two_seven_family_covariance_checker.py</code>, lines
653--710, and independently replays every base cell at lines 716--723.

The complete positive-chamber old--new theorem

\[
 \mathbb B(A_{n,d},b_{n,d})=[d>1]
 \tag{6.3}
\]

is stated in
<code>literature/proofs/AK3_OLD_NEW_SINGLETON_TERMINAL_INCIDENCE.md</code>,
lines 15--19, and derived from the powered and finite terms at lines
437--461. Substitution of (5.3), (6.2), and (6.3) into (6.1) gives

\[
 \boxed{
 J_{n,d}=0+[d>1]+1=[d=1]
 \qquad(n\geq0,\ d\geq1).}
 \tag{6.4}
\]

This closes only the positive-chamber \(j\)-edge. It does not prove a
diagonal or \(i\)-edge identity, does not transport the result to another
chamber, and gives no period-two lift, AK(3), stable Andrews--Curtis, or
Andrews--Curtis conclusion.
