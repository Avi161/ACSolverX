# The old--new tie cochain as an occurrence sweep

## Status and scope

This note sharpens the even-label tie-cochain theorem for the actual
collision-aggregated 84-token mask \(T=b_{n,d}\).  At any correction
coordinate, the equal-label chronology rank is exactly the parity of the
tokens in earlier literal AST occurrences.  There is no remaining
same-occurrence module-order comparison.  The 42-chord normal form therefore
collapses, on every forest edge atom, to a finite occurrence-prefix sweep.

The sweep gives explicit formulas for the slot-two, slot-three, and
slot-four edge loads.  In slot four the complete old--new load is the
mod-two coboundary of the collision-aggregated slot-four activity:

\[
 \omega_T(E_4(v))=\bar b_4(v)+\bar b_4(tv).
\]

This does not evaluate the mixed-slot \(P,C,Q\) endpoint chains, the finite
old terms, or positive-chamber covariance.  It proves no period-two lift,
AK(3), stable Andrews--Curtis, or Andrews--Curtis claim.

## 1. Transported occurrence activities

Let

\[
 X=Q/\langle c\rangle
\]

be the canonical module-vertex set.  For
\(s\in\{0,2,3,4\}\), let

\[
 \bar b_s:X\longrightarrow\mathbb F_2
 \tag{1.1}
\]

be the collision-aggregated parity activity of the actual \(b\)-mask in
slot \(s\).  Thus integral coefficients at one canonical coordinate are
summed first and only then reduced modulo two.  For \(s=2,3,4\),
\(\bar b_s(v)\) is also the coefficient of the stored edge \(E_s(v)\) in
the de-occurrenced parity current \(\beta_E\).  No assertion below uses a
raw provenance coefficient in place of \(\bar b_s(v)\).

The active residual occurrences, in literal AST order, are

\[
 \mathcal O_T=(1,3,4,6,7,8,9,11,12,14,15,16).
 \tag{1.2}
\]

The omitted occurrences have slot one, whose \(b\)-activity is zero.  The
mask difference has no fixed-literal tokens.  For an active occurrence
\(o\), write \(s_o\) for its slot, \(q_o\) for its raw quotient prefix, and

\[
 \tau_o(v)=\operatorname{cvert}(q_ov).
 \tag{1.3}
\]

The raw prefix is retained until the displayed canonicalization.  Left
multiplication by \(q_o\) is a bijection of the coset set \(X\), and
\(\operatorname{cvert}\) only selects its canonical representative.
Consequently

\[
 \boxed{\tau_o:X\longrightarrow X\text{ is a bijection},}
 \tag{1.4}
\]

with inverse induced by left multiplication by \(q_o^{-1}\).

Define the transported activity at occurrence \(o\) by

\[
 a_o(\ell)
 :=\bar b_{s_o}\bigl(\tau_o^{-1}(\ell)\bigr).
 \tag{1.5}
\]

Equivalently, \(a_o(\ell)=1\) exactly when the actual decorated token of
label \(\ell\) is active in occurrence \(o\).  In particular, one label
names at most one token in one occurrence.  The even transported-label
fiber theorem is the pointwise identity

\[
 \boxed{
  \sum_{o\in\mathcal O_T}a_o(\ell)=0
  \qquad(\ell\in X).}
 \tag{1.6}
\]

## 2. Equal-label rank is an AST prefix

For a residual occurrence \(o\), put

\[
 A_{<o}(\ell)
 :=\sum_{\substack{o'\in\mathcal O_T\\o'<o}}a_{o'}(\ell).
 \tag{2.1}
\]

Recall that

\[
 H_T(x)=\#\{t\in T:\lambda(t)=\lambda(x),\ t<_\chi x\}
 \pmod2
 \tag{2.2}
\]

is the equal-label chronology prefix left after every strict
transported-label rank has vanished.

**Theorem 2.1 (occurrence-prefix rank).** For every
\(o\in\mathcal O_T\) and \(v\in X\),

\[
 \boxed{
 H_T(\iota_o(v))=A_{<o}(\tau_o(v)).}
 \tag{2.3}
\]

### Proof

Let \(\ell=\tau_o(v)\).  A token of label \(\ell\) in occurrence
\(o'<o\) lies before \(\iota_o(v)\) because distinct correction blocks use
literal AST order.  A token in occurrence \(o'>o\) lies after it.

It remains to consider occurrence \(o\) itself.  By bijectivity of
\(\tau_o\), a token \(\iota_o(w)\) has label \(\ell\) only when \(w=v\).
If that token is active, the strict diagonal rule excludes it from (2.2).
Thus no same-occurrence token contributes.  Polarity reverses the module
order inside a negative occurrence, but there is no second equal-label
coordinate whose order could matter.  The surviving count is exactly
(2.1).  \(\square\)

Formula (2.3) removes both transported-label shortlex and same-occurrence
module shortlex from every forest-edge evaluation.  It is an identity on
the collision-aggregated decorated coordinates, not on virtual rows.

## 3. The explicit edge sweep

Use the stored oriented edges

\[
\begin{aligned}
 E_2(v)&:Bv\longrightarrow v,\\
 E_3(v)&:tv\longrightarrow U^{-1}v,\\
 E_4(v)&:v\longrightarrow tv.
\end{aligned}
 \tag{3.1}
\]

Their positive/negative occurrence pairs are respectively

\[
 (1,6),\qquad(9,14),\qquad(15,16).
 \tag{3.2}
\]

The transported labels at the positive and negative occurrences are the
head and tail of the displayed stored edge.  Combining Theorem 2.1 with the
definition of the tie cochain gives the uniform formula

\[
 \boxed{
 \tau_T(E_s(v))
 =A_{<o_s^+}(\operatorname{head}E_s(v))
  +A_{<o_s^-}(\operatorname{tail}E_s(v)).}
 \tag{3.3}
\]

Expanding the literal occurrence order gives, in slot two,

\[
 \boxed{
 \tau_T(E_2(v))=(a_1+a_3+a_4)(Bv).}
 \tag{3.4}
\]

In slot three one obtains

\[
\boxed{
\begin{aligned}
 \tau_T(E_3(v))={}&
 (a_1+a_3+a_4+a_6+a_7+a_8)(U^{-1}v)\\
 &+(a_1+a_3+a_4+a_6+a_7+a_8
     +a_9+a_{11}+a_{12})(tv).
\end{aligned}}
 \tag{3.5}
\]

Finally, put

\[
 P=a_1+a_3+a_4+a_6+a_7+a_8+a_9+a_{11}+a_{12}+a_{14}.
 \tag{3.6}
\]

The slot-four formula is

\[
 \boxed{
 \tau_T(E_4(v))=P(tv)+P(v)+a_{15}(v).}
 \tag{3.7}
\]

Indeed, \(P=A_{<15}\), while
\(A_{<16}=P+a_{15}\).  Equations (3.4)--(3.7) retain all earlier active
occurrences, including the six slot-zero blocks.  No occurrence has been
discarded because its slot is not an edge slot.

## 4. Exact slot-four coboundary

Since occurrences 15 and 16 are the final active occurrences, the even
fiber identity (1.6) and (3.6) give

\[
 \boxed{P(\ell)=a_{15}(\ell)+a_{16}(\ell).}
 \tag{4.1}
\]

Their raw actions are \(q_{15}=t\) and \(q_{16}=1\).  Hence

\[
 a_{15}(\ell)=\bar b_4(t^{-1}\ell),
 \qquad
 a_{16}(\ell)=\bar b_4(\ell).
 \tag{4.2}
\]

Substitute (4.1)--(4.2) into (3.7).  At the head \(tv\),

\[
 P(tv)=\bar b_4(v)+\bar b_4(tv),
 \tag{4.3}
\]

and at the tail \(v\),

\[
 P(v)+a_{15}(v)=a_{16}(v)=\bar b_4(v).
 \tag{4.4}
\]

The two copies of \(\bar b_4(v)\) cancel, proving

\[
 \boxed{
 \tau_T(E_4(v))=\bar b_4(tv).}
 \tag{4.5}
\]

The forest-overlap term on the same stored edge is

\[
 \beta_E(E_4(v))=\bar b_4(v).
 \tag{4.6}
\]

Therefore the complete old--new edge load is

\[
 \boxed{
 \omega_T(E_4(v))
 =\bar b_4(v)+\bar b_4(tv).}
 \tag{4.7}
\]

Thus \(\omega_T\) restricted to the slot-four subgraph is the coboundary of
the vertex function \(\bar b_4\).  Regard \(\bar b_4\) as a vertex
zero-cochain over \(\mathbb F_2\), so that
\(\partial E_4(v)=\delta_{tv}+\delta_v\).  More explicitly, for every
\(z\in C_1^{\rm fin}(\mathcal T;\mathbb F_2)\) supported on slot-four
edges,

\[
 \boxed{
 \langle z,\omega_T\rangle
 =\langle\partial z,\bar b_4\rangle.}
 \tag{4.8}
\]

In particular, a consecutive slot-four path telescopes to the two values of
\(\bar b_4\) at its outer endpoints.  This is a pointwise all-index identity;
it is not inferred from a bounded support enumeration.

## 5. Paired occurrence blocks are forest boundaries

Group the twelve active occurrence activities into the six
positive/negative occurrence pairs

\[
\begin{aligned}
 Z_1&=a_3+a_4,& D_2&=a_1+a_6,\\
 Z_2&=a_7+a_8,& D_3&=a_9+a_{14},\\
 Z_3&=a_{11}+a_{12},& D_4&=a_{15}+a_{16}.
\end{aligned}
\tag{5.1}
\]

These pairs are not consecutive blocks in AST order: the slot-two pair
encloses \(Z_1\), and the slot-three pair encloses \(Z_3\).  Formula (5.1)
groups matching slot occurrences, not adjacent chronology positions.

The \(Z_j\) are the three slot-zero occurrence-pair activities.  For an
edge slot, put

\[
 \beta_s=\sum_v\bar b_s(v)E_s(v)
 \in C_1^{\rm fin}(\mathcal T;\mathbb F_2).
 \tag{5.2}
\]

**Theorem 5.1 (paired-block boundary).** The functions \(D_s\) are exactly
the vertex coefficient functions of \(\partial\beta_s\):

\[
 \boxed{D_s(\ell)=[e_\ell](\partial\beta_s)
 \qquad(s=2,3,4).}
 \tag{5.3}
\]

More explicitly,

\[
\begin{aligned}
 D_2(\ell)
 &=\sum_v\bar b_2(v)
   \bigl([\ell=v]+[\ell=Bv]\bigr),\\
 D_3(\ell)
 &=\sum_v\bar b_3(v)
   \bigl([\ell=U^{-1}v]+[\ell=tv]\bigr),\\
 D_4(\ell)
 &=\sum_v\bar b_4(v)
   \bigl([\ell=tv]+[\ell=v]\bigr).
\end{aligned}
 \tag{5.4}
\]

### Proof

At the positive occurrence of a stored edge, its transported label is the
head in (3.1); at the negative occurrence it is the tail.  Thus the two
pushforwards of \(\bar b_s\) contribute exactly the two endpoint indicators
in (5.4).  Over \(\mathbb F_2\), the integral incidence signs reduce to
one, so (5.4) is the coefficient formula for the displayed edge boundary.
\(\square\)

Regrouping the even-fiber equation (1.6) now gives the pointwise
source-boundary law

\[
 \boxed{
 Z_1+D_2+Z_2+D_3+Z_3+D_4=0.}
 \tag{5.5}
\]

Define the two partial AST cuts

\[
 R_2=Z_1+D_2,
 \qquad
 R_3=Z_1+D_2+Z_2.
 \tag{5.6}
\]

The occurrence sweep then gives the complete edge loads in the sharper
form

\[
 \boxed{
 \omega_T(E_2(v))=R_2(Bv),}
 \tag{5.7}
\]

\[
 \boxed{
 \omega_T(E_3(v))
 =R_3(U^{-1}v)+D_4(tv),}
 \tag{5.8}
\]

and

\[
 \boxed{
 \omega_T(E_4(v))=D_4(tv).}
 \tag{5.9}
\]

For (5.7), formula (3.4) supplies
\((a_1+Z_1)(Bv)\), while the forest-overlap coefficient is
\(\bar b_2(v)=a_6(Bv)\).  Their sum is \(R_2(Bv)\).

For slot three, the two chronology prefixes in (3.5) are
\(R_3(U^{-1}v)\) and
\((R_3+a_9+Z_3)(tv)\).  Adding
\(\bar b_3(v)=a_{14}(tv)\) gives

\[
 R_3(U^{-1}v)+(R_3+D_3+Z_3)(tv).
 \tag{5.10}
\]

Equation (5.5) says \(R_3+D_3+Z_3=D_4\), proving (5.8).
Equation (5.9) is (4.7), rewritten using (5.4).

There is also a useful slot-three tail-residual form.  For a vertex function
\(f\), write

\[
 \delta f(E_s(v))
 :=f(\operatorname{head}E_s(v))
  +f(\operatorname{tail}E_s(v)).
 \tag{5.11}
\]

Then (5.8) and (5.5) are equivalently

\[
 \boxed{
 \omega_T(E_3(v))
 =\delta R_3(E_3(v))+(D_3+Z_3)(tv).}
 \tag{5.12}
\]

Thus the slot-three load is an explicit coboundary plus one tail-supported
residual associated with the occurrence-block cut.  It is not supported
only where an old path changes edge labels.  Equations (5.7) and (5.12),
rather than an unspecified tree potential, identify the exact terms which
still require evaluation.

## 6. Chain-level tail-boundary identity

Let

\[
 C=C_2+C_3+C_4
 \in C_1^{\rm fin}(\mathcal T;\mathbb F_2),
 \qquad
 C_s=\sum_v C_s(v)E_s(v),
 \tag{6.1}
\]

be any finite mixed forest chain, decomposed in the stored edge basis.
For an edge chain \(z\) and edge cochain \(r\), and for a vertex chain
\(q\) and vertex function \(f\), use the pairings

\[
 \langle z,r\rangle=\sum_e z_e r(e),
 \qquad
 \langle q,f\rangle=\sum_xq_xf(x).
 \tag{6.2}
\]

Summing (5.7), (5.12), and (4.8) proves

\[
\boxed{
\begin{aligned}
 \langle C,\omega_T\rangle
 ={}&\sum_v C_2(v)R_2(Bv)
    +\langle\partial C_3,R_3\rangle\\
   &+\sum_v C_3(v)(D_3+Z_3)(tv)
    +\langle\partial C_4,\bar b_4\rangle.
\end{aligned}}
 \tag{6.3}
\]

Every pairing in (6.3) is over \(\mathbb F_2\).  The second and fourth
terms depend only on the boundaries of the slot-three and slot-four
subchains.  All failure of those two parts to telescope is therefore
concentrated in the displayed slot-two tail values and slot-three switch
values.  Here “switch” refers only to the occurrence-block cut in (5.12),
not to a change of edge label along \(C\).  Formula (6.3) is exact for
arbitrary finite chains; it is not a claim that either tail sum vanishes.

For a path chain, \(\partial C_3\) and \(\partial C_4\) record the vertices
where the path enters or leaves the corresponding labelled edge strata.
The first sum is nevertheless evaluated at the tail of every supported
slot-two edge, and the third at the tail of every supported slot-three edge.
Thus (6.3) replaces part of the interior chronology calculation by stratum-
boundary values while retaining two explicit interior tail sums.  This is
the chain interface to use for the powered \(P,C,Q\) endpoint program.

## 7. Adjacent-source block paths

Fix the positive chamber

\[
 i,j\geq 0,\qquad d=i-j\geq 1,
 \qquad y_0=y_{ij},\quad y_1=y_{i,j+1}.
 \tag{7.1}
\]

For each slot-zero occurrence
\(o\in\{3,4,7,8,11,12\}\), the approved adjacent-ray
complete-cover factorization places \(\tau_o(y_0)\) and \(\tau_o(y_1)\)
in one source-tree component.  Let

\[
 \pi_o=\operatorname{path}_{\mathcal T}
   \bigl(\tau_o(y_0),\tau_o(y_1)\bigr)
 \tag{7.2}
\]

be the unique reduced path between them, collision-aggregated in the common
stored edge basis, and put

\[
 \Pi_1=\pi_3+\pi_4,\qquad
 \Pi_2=\pi_7+\pi_8,\qquad
 \Pi_3=\pi_{11}+\pi_{12}.
 \tag{7.3}
\]

In the exact endpoint-family order of the companion identity, the
occurrences are

\[
 3\mapsto\nu=1,\quad 4\mapsto\nu=5,\quad
 7\mapsto\nu=4,\quad 8\mapsto\nu=6,\quad
 11\mapsto\nu=3,\quad 12\mapsto\nu=2.
\]

Consequently \(\Pi_1\), \(\Pi_2\), and \(\Pi_3\) are respectively the
paired \((1,5)\), \((4,6)\), and \((3,2)\) inverse-\(Q\) blocks from the
exact adjacent-\(j\) recurrence.  This pairing statement is collision-safe
only after all six paths have been aggregated in the common stored basis.

Write \(\beta=\beta_2+\beta_3+\beta_4\) for the collision-aggregated
forest current of this adjacent increment.  The approved factorization and
finite forest-flow uniqueness give

\[
 \boxed{\beta=\Pi_1+\Pi_2+\Pi_3,\qquad
        \partial\Pi_j=Z_j\quad(j=1,2,3).}
 \tag{7.4}
\]

Indeed, the boundary of \(\pi_o\) is the sum of its two transported
endpoints.  Pairing the occurrences as in (7.3) therefore gives exactly
the three functions \(Z_j\) from (5.1).  The sum of the six paths has the
same source boundary as \(\beta\); uniqueness of a finite flow with a
prescribed boundary in a forest identifies the two currents.  Shared path
edges cancel coefficientwise in the common stored basis.

Define

\[
 F_2=\Pi_1+\beta_2,
 \qquad
 G_3=\Pi_3+\beta_3.
 \tag{7.5}
\]

Theorem 5.1 and (7.4) now give the exact boundary identities

\[
 \boxed{R_2=\partial F_2,
 \qquad W_3:=D_3+Z_3=\partial G_3.}
 \tag{7.6}
\]

## 8. Head--tail boundary identity

On stored edge atoms define the vertex-chain selectors

\[
 t_2(E_2(v))=\delta_{Bv},\qquad
 t_3(E_3(v))=\delta_{tv},\qquad
 h_3(E_3(v))=\delta_{U^{-1}v},
 \tag{8.1}
\]

extended linearly over \(\mathbb F_2\).  Thus

\[
 \partial C_3=t_3C_3+h_3C_3.
 \tag{8.2}
\]

By (5.5), (5.3), and (7.6),

\[
 R_3=W_3+D_4,
 \qquad D_4=\partial\beta_4,
 \qquad W_3=\partial G_3.
 \tag{8.3}
\]

Substitute (7.6) and (8.3) into (6.3).  Using (8.2), the two copies of
\(\langle t_3C_3,W_3\rangle\) cancel, and one obtains

\[
\boxed{
\begin{aligned}
 \langle C,\omega_T\rangle
 ={}&\langle t_2C_2,\partial F_2\rangle
    +\langle h_3C_3,\partial G_3\rangle\\
   &+\langle\partial C_3,\partial\beta_4\rangle
    +\langle\partial C_4,\bar b_4\rangle.
\end{aligned}}
 \tag{8.4}
\]

All chains in (7.2)--(8.4) are collision-aggregated in the same stored
edge basis.  Orientation signs are not suppressed in the integral
currents: head and tail are fixed by (3.1), and reduction to
\(\mathbb F_2\) occurs only after those oriented currents have been placed
in that basis.  The last term of (8.4) deliberately retains the
unsymmetrized function \(\bar b_4\); it is not claimed to be a boundary.

**Corollary 8.1 (powered increment reduction).** Applying (8.4) to each
fixed \(P\)-, \(C\)-, or \(Q\)-increment reduces its complete old--new
load to a finite xor of canonical powered endpoint equalities and labelled-
stratum switches.  Formula (8.4) does not evaluate those equalities or
switches, so this reduction proves no endpoint identity or vanishing
claim.

## 9. Remaining exact boundary

The old--new forest load now has four complementary descriptions:

1. the forest-overlap plus tie decomposition
   \(\omega_T=\beta_E+\tau_T\); and
2. the occurrence-prefix formulas (3.4)--(3.7), with the complete slot-four
   collapse (4.7); and
3. the chain-level tail-boundary identity (6.3); and
4. the adjacent-source head--tail identity (8.4).

The two surviving \(P\)-rays, the six-family \(C\)-chain, and the three
paired \(Q\)-rectangles contain mixed slot-two, slot-three, and slot-four
edges.  Equation (8.4) rewrites their remaining loads as paired-block
boundary values, slot-three/four stratum-boundary values, and the retained
unsymmetrized slot-four endpoint function.  It does not evaluate those data
on all powered endpoints.  The available coboundaries alone do not force a
mixed path or rectangle to vanish.

The exact next obligation is to evaluate (8.4) on the two powered
\(P\)-rays, the six-family \(C\)-chain, and the three paired
\(Q\)-rectangles.  If the boundary and tail-residual values do not pair, the
honest remainder is their exact collision-aggregated symmetric difference,
with its powered endpoint schemas retained.  Until those values are
evaluated, the endpoint identities, finite old terms, positive-chamber
covariance, the period-two lift, AK(3), stable Andrews--Curtis, and
Andrews--Curtis remain open.
