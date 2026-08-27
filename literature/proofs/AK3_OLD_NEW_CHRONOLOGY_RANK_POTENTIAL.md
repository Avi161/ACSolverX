# Old--new chronology as an exact rank potential

## Status and scope

This note gives an exact algebraic reduction for the chronology kernel used
in the period-two old--new cut.  It includes transported-label ties and the
prescribed zero diagonal.  It does not prove the remaining endpoint
identities, the positive-chamber covariance lemma, the period-two lift, or
Andrews--Curtis.

The reduction applies to the collision-aggregated token set.  It must not be
applied to virtual provenance rows before their integral coefficients have
been summed.

## 1. Two orders and the tie term

Let \(T\) be the full 84-token parity support obtained after integral
collision aggregation: twelve slot-zero tokens and two occurrence copies of
each of the 36 odd path fibers.  The literal AST chronology gives a strict
total order \(<_\chi\) on the global decorated token coordinates.  A
correction coordinate includes its AST occurrence; a fixed literal token
uses its literal leaf/position coordinate.  Equal module vertices in
different AST occurrences are therefore distinct coordinates.  Write
\(\lambda(x)\) for the transported-label word and use canonical shortlex
order on labels.

For distinct token coordinates define
\[
 \kappa(x,t)=
 \begin{cases}
 [\lambda(x)<\lambda(t)],&x<_\chi t,\\
 [\lambda(t)<\lambda(x)],&t<_\chi x.
 \end{cases}
 \tag{1.1}
\]
As in the old--new cut, put \(\kappa(x,x)=0\).  All brackets take values in
\(\mathbb F_2\).

For \(t\ne x\), put
\[
 a=[t<_\chi x],\qquad
 b=[\lambda(t)<\lambda(x)],\qquad
 e=[\lambda(t)=\lambda(x)].
\]
Shortlex trichotomy gives the pointwise identity
\[
 \boxed{\kappa(x,t)=1+a+b+e(1+a).}
 \tag{1.2}
\]
Indeed, if \(a=1\), the right side is \(b\).  If \(a=0\), it is
\(1+b+e=[\lambda(x)<\lambda(t)]\).

## 2. Exact rank-potential formula

Let \(T_x=T\setminus\{x\}\) when \(x\in T\), and \(T_x=T\) otherwise.
Define
\[
\begin{aligned}
 N_x&=|T_x|\bmod2,\\
 C_\chi(x)&=\#\{t\in T_x:t<_\chi x\}\bmod2,\\
 C_\lambda(x)&=\#\{t\in T_x:\lambda(t)<\lambda(x)\}\bmod2,\\
 E^+_\lambda(x)&=\#\{t\in T_x:x<_\chi t,
                 \ \lambda(t)=\lambda(x)\}\bmod2.
\end{aligned}
\tag{2.1}
\]
Then summing (1.2) gives
\[
 \boxed{
 \Lambda_T(x):=\sum_{t\in T}\kappa(x,t)
 =N_x+C_\chi(x)+C_\lambda(x)+E^+_\lambda(x).}
\tag{2.2}
\]

In this application \(|T|=84\) is even, so
\[
 N_x=|T_x|\bmod2=[x\in T].
 \tag{2.3}
\]
Thus the constant part of the kernel disappears globally, but the exact
diagonal-membership bit remains.

This is an identity, not a generic-position assertion.  The fourth term is
exactly the correction that is lost if equal transported labels are treated
as though the label order were strict.  Removing \(x\) before taking all
four counts is exactly the zero-diagonal rule.

For an integral old current \(C=\sum_r c_r e_{x_r}\), first aggregate over
\(\mathbb Z\) at each old coordinate, and let \(r\) range over the resulting
distinct occurrence-decorated coordinates.  Collision-first bilinearity then
gives
\[
 \boxed{
 \mathbb B(C,T)=
 \sum_r(c_r\bmod2)
 \bigl(N_{x_r}+C_\chi(x_r)+C_\lambda(x_r)
              +E^+_\lambda(x_r)\bigr).}
 \tag{2.4}
\]
If several old rows have the same coordinate, their integral coefficients
must first be added.  Formula (2.4) then agrees with collision aggregation:
an even integral fiber disappears, and a surviving coordinate excludes its
own token from every count.

## 3. Compression to two total orders

Define a second strict total order on the same global decorated-token
universe by
\[
 x<_\rho t
 \quad\Longleftrightarrow\quad
 \lambda(x)>_{\rm sl}\lambda(t)
 \quad\hbox{or}\quad
 \bigl(\lambda(x)=\lambda(t)\hbox{ and }x<_\chi t\bigr).
 \tag{3.1}
\]
Thus \(<_\rho\) is decreasing transported-label shortlex with literal
chronology as its tie-breaker.  For distinct \(x,t\), direct inspection of
the two chronology cases gives
\[
 \boxed{
 \kappa(x,t)=[t<_\chi x]+[t<_\rho x].}
 \tag{3.2}
\]
If \(x<_\chi t\), the first term is zero and the second is exactly
\([\lambda(x)<\lambda(t)]\).  If \(t<_\chi x\), the first term is one;
the second toggles it precisely when
\(\lambda(t)\geq\lambda(x)\).  This leaves
\([\lambda(t)<\lambda(x)]\), including zero in the equal-label case.

For either total order \(\prec\), put
\[
 R_T^\prec(x)=\#\{t\in T:t\prec x\}\bmod2.
 \tag{3.3}
\]
The diagonal token, when present, belongs to neither strict initial segment.
Summing (3.2) therefore gives the exact two-rank formula
\[
 \boxed{\Lambda_T(x)=R_T^\chi(x)+R_T^\rho(x).}
 \tag{3.4}
\]
This is exactly equivalent to (2.2): partitioning \(T_x\) into labels below,
above, and equal to \(\lambda(x)\) gives
\[
 R_T^\rho(x)=N_x+C_\lambda(x)+E^+_\lambda(x).
 \tag{3.5}
\]
Hence (3.4) absorbs, rather than discards, diagonal membership and the
equal-label chronology tail.

For \(x,y\) and either total order \(\prec\), define the half-open interval
parity
\[
 I_T^\prec(x,y)=
 \#\bigl(T\cap
 [\min_\prec(x,y),\max_\prec(x,y))_\prec\bigr)\bmod2.
 \tag{3.6}
\]
The symmetric difference of the two strict initial segments is exactly this
half-open interval, so
\[
 \boxed{
 \Lambda_T(x)+\Lambda_T(y)
 =I_T^\chi(x,y)+I_T^\rho(x,y).}
 \tag{3.7}
\]
The half-open convention is load-bearing: it includes a token at the lesser
endpoint and excludes one at the greater endpoint, reproducing the exact
membership correction from (2.3).  No separate membership or tie term may
be added after passing to (3.7).

Both orders in (3.4)--(3.7) are global orders against the full 84-token mask:
replacing \(T\) by a same-slot subset would discard genuine cross-occurrence
comparisons.  More explicitly, for every correction occurrence \(o\) of
slot \(s\), let
\(\iota_o(v)\) be the decorated token whose module vertex is \(v\), whose
label is
\[
 \lambda(\iota_o(v))=\operatorname{cvert}(q_ov),
 \tag{3.8}
\]
and whose chronological position uses the literal AST leaf and the
polarity-adjusted module order at \(o\).  Here \(q_o\) is the raw occurrence
prefix; a terminal `c` is retained until the displayed `cvert` operation.
Put
\[
 \overline\Lambda_T(s,v)
 =\sum_{o:s_o=s}\Lambda_T(\iota_o(v)).
 \tag{3.9}
\]
Then any two module endpoints \(v,w\) in slot \(s\) satisfy
\[
 \boxed{
 \overline\Lambda_T(s,v)+\overline\Lambda_T(s,w)
 =\sum_{o:s_o=s}
 \left(
 I_T^\chi(\iota_o(v),\iota_o(w))
 +I_T^\rho(\iota_o(v),\iota_o(w))
 \right).}
 \tag{3.10}
\]
This is the exact two-atom load formula.  It applies after integral
aggregation has produced two module atoms in the same slot.  It is not a
claim that a multi-edge forest path is determined by the loads of its two
forest endpoints.

### 3.1 Exact reduction of the chronology rank

Let \(S_s\) be the collision-aggregated module support of the \(b\)-mask in
slot \(s\).  Every occurrence of slot \(s\) contains one decorated copy of
the same \(S_s\).  The literal occurrence pairs are
\[
\begin{aligned}
 s=0:&\quad (3^+,4^-),(7^+,8^-),(11^+,12^-),\\
 s=2:&\quad (1^+,6^-),\\
 s=3:&\quad (9^+,14^-),\\
 s=4:&\quad (15^+,16^-).
\end{aligned}
\tag{3.11}
\]
The bound delta-zero collision table has
\[
 |S_0|=2,\qquad |S_2|=8,\qquad |S_3|=14,\qquad |S_4|=14.
 \tag{3.12}
\]
For slot zero these are the two anchored corner tokens.  For slots
\(2,3,4\), they are respectively the 8, 14, and 14 odd integral fibers among
the 36 active path fibers.  The source binding proves that these supports are
the same at every occurrence copy.  Thus every occurrence block of \(T\)
has even size, and \(T\) has no fixed literal token.

Since all complete earlier occurrence blocks have even size, the chronology
rank of a lifted atom is just its within-occurrence rank.  Within a positive
occurrence this counts \(S_s\)-vertices below \(v\); within a negative
occurrence it counts \(S_s\)-vertices above \(v\).  For every pair in
(3.11), their xor is
\[
 \#\{t\in S_s:t<v\}+
 \#\{t\in S_s:t>v\}
 =|S_s|-[v\in S_s]=[v\in S_s]\pmod2.
 \tag{3.13}
\]
There is one pair for slots \(2,3,4\) and three pairs for slot zero.  Hence
\[
 \boxed{
 \sum_{o:s_o=s}R_T^\chi(\iota_o(v))=[v\in S_s]
 \qquad(s\in\{0,2,3,4\}).}
 \tag{3.14}
\]
Combining (3.14) with (3.4) gives the exact one-atom load formula
\[
 \boxed{
 \overline\Lambda_T(s,v)
 =[v\in S_s]+
 \sum_{o:s_o=s}R_T^\rho(\iota_o(v)).}
 \tag{3.15}
\]

For completeness, the corresponding two-atom chronology interval also
localizes.  Within a positive occurrence, \(<_\chi\) is increasing module shortlex;
within a negative occurrence it is decreasing module shortlex.  Both
endpoints \(\iota_o(v),\iota_o(w)\) lie in the same occurrence block, so
their global chronology interval contains no token from another occurrence.

Suppose first that \(v<_{\rm sl}w\).  In a positive occurrence the module
vertices contributing to the half-open interval are
\[
 \{t\in S_s:v\leq t<w\},
\]
whereas in its negative partner they are
\[
 \{t\in S_s:v<t\leq w\}.
\]
Their symmetric difference consists exactly of the endpoints that belong to
\(S_s\).  The case \(w<_{\rm sl}v\) is symmetric, and the case \(v=w\) is
empty on both sides.  Consequently every positive/negative pair satisfies
\[
 I_T^\chi(\iota_{o^+}(v),\iota_{o^+}(w))
 +I_T^\chi(\iota_{o^-}(v),\iota_{o^-}(w))
 =[v\in S_s]+[w\in S_s].
 \tag{3.16}
\]

There is one pair for slots \(2,3,4\), and three pairs for slot zero.  Since
three is odd, summing (3.16) over the complete occurrence footprint gives,
for every \(s\in\{0,2,3,4\}\),
\[
 \boxed{
 \sum_{o:s_o=s}I_T^\chi(\iota_o(v),\iota_o(w))
 =[v\in S_s]+[w\in S_s].}
 \tag{3.17}
\]
Thus (3.10) sharpens to
\[
 \boxed{
 \overline\Lambda_T(s,v)+\overline\Lambda_T(s,w)
 =[v\in S_s]+[w\in S_s]
 +\sum_{o:s_o=s}I_T^\rho(\iota_o(v),\iota_o(w)).}
 \tag{3.18}
\]
The global chronology contribution is now closed exactly.  No analogous
localization is asserted for \(<_\rho\): labels transported from every AST
occurrence can interleave in that global order.

### 3.2 Correct forest endpoint potential

Let \(e\) be an oriented source-tree edge, so
\(s(e)\in\{2,3,4\}\).  Its certified incidence rule emits a module atom
\((s(e),v(e))\).  Its complete signed occurrence footprint is
\[
 \eta(e)=\sum_{o:s_o=s(e)}\epsilon_{e,o}
 e_{\iota_o(v(e))},
 \qquad \epsilon_{e,o}\in\{+1,-1\}.
 \tag{3.19}
\]
After integral aggregation, reduction modulo two sends every displayed sign
to one.  Formula (3.15) therefore gives the edge's old--new load as
\[
 \omega_T(e)=\mathbb B(\eta(e),T)
 =[v(e)\in S_{s(e)}]
 +\sum_{o:s_o=s(e)}R_T^\rho(\iota_o(v(e))).
 \tag{3.20}
\]
Choose a root in each source-tree component and integrate the two summands
of (3.20) separately along the unique root path, obtaining potentials
\(\psi_T^{\rm mem}\) and \(\psi_T^\rho\).  Then
\[
 \psi_T=\psi_T^{\rm mem}+\psi_T^\rho,
 \tag{3.21}
\]
and for any forest vertices \(x,y\) in the same source-tree component,
\[
 \boxed{
 \mathbb B(\eta([x,y]),T)
 =\psi_T^{\rm mem}(x)+\psi_T^{\rm mem}(y)
  +\psi_T^\rho(x)+\psi_T^\rho(y).}
 \tag{3.22}
\]
This is the valid endpoint reduction: it integrates every edge atom.  It
does not replace a multi-edge path by two hypothetical module atoms.

## 4. Consequence for the existing endpoint program

The endpoint-potential reduction leaves the exact obligations
\(E_P=0\), \(E_Q=0\), and \(E_C=[d=1]\) unchanged, but replaces each
edge-atom evaluation by the module-support bit and global \(\rho\)-rank in
(3.20), then integrates those exact values as in (3.22).  For the
positive-chamber powered words, each edge value is decided by:

- membership/equality with one of the 84 canonical token coordinates;
- chronology position, which is fixed first by occurrence and then by the
  polarity-adjusted module shortlex order;
- transported-label shortlex rank; and
- the equal-label fiber followed by chronology rank inside that fiber.

Equivalently, the module-support term is the already-closed \(\chi\)-part,
and the remaining edge load is a sum of global \(\rho\)-initial-segment
ranks.  When two emitted atoms are paired, (3.18) rewrites their difference
as endpoint membership plus a half-open \(\rho\)-interval; the half-open
interval already supplies its membership convention and must not receive a
second correction.  The intact-boundary pumping lemma applies directly to
the equality and shortlex comparisons defining these ranks and intervals.
Hence a certificate may pair tagged crossings or group them by common
comparison outcome and parity-count the groups; it need not materialize all
old-row/token pairs.  This is a strict reduction of the remaining arithmetic
interface, not a proof that its parities vanish.

After (3.14), the \(\chi\)-rank need not be enumerated at all: it is the
module-support membership bit in (3.15).  The remaining rank/crossing problem
is global only in the \(\rho\)-order.

For example, if \(x^P_{\nu,h}\), \(x^C_{\nu,0/1}\), and
\(x^Q_{\nu,h}\) denote the forest endpoints already fixed in the endpoint
program, evaluate the two potentials in (3.22) at those endpoints.  The
two-ray \(P\) target is the xor over the surviving classes \(\nu=1,*\); the
\(Q\) target is the xor of the three paired rectangles
\((1,5),(2,3),(4,6)\).  Individual edges, rays, occurrences, orders, or
rectangles need not vanish.

## 5. Fail-closed boundary

Formula (2.2) is useful only after all of the following have been fixed
exactly: collision aggregation over \(\mathbb Z\) before occurrence
expansion and parity, occurrence orientation, canonical module vertices,
literal transported-label actions, shortlex normalization, and diagonal
equality of the final occurrence-decorated coordinate.  A digest, a bounded
grid, or a generic no-tie assumption cannot replace any of them.

The next theorem obligation is to apply (3.20)--(3.22) to the two surviving
\(P\)-rays and the three paired \(Q\)-rectangles, evaluate the integrated
module-support potential, and pair the complete set of global
\(\rho\)-rank crossings along their edge paths.
If cancellation is incomplete, the honest survivor is the
collision-aggregated symmetric-difference set of tagged crossings, not
merely its scalar parity or a digest.  Until that is done, AK(3), stable
Andrews--Curtis, and Andrews--Curtis remain open.
