# Companion-identity preflight for the period-two Hessian

Date: 2026-07-29

Scope: theory only.  This note uses the exact complete-cover transducer and
the pushed Hessian certificate at `a1a411b`.  It runs no source-depth census
and makes no finite-state, period-two-lift, stable Andrews--Curtis, or
Andrews--Curtis claim.

## 1. Corrected status

Let
\[
p=tc,\qquad g=ctcTTTct,\qquad n_i=5+3i,
\]
and
\[
v=p^{-1}T,\qquad
w_i=p^{-1}g^{n_i}c g^{-(n_i-2)}t,\qquad
h_j=p^{-1}g^{-n_j}p.
\]
The source scalar of both \(h_jv\) and \(h_jw_i\) is \(-2\), so the
signed pair with coefficient \(-1\) is valid for every \(i,j\geq0\).
Modulo two its two slot-zero currents are singletons.

Write \(P_{ij}\) for the first slot-zero inversion term, and write
\(R_{ij}\) for the sum of the other 75 normalized kernels: four equality
terms, the other five inversion terms, and all 66 external-order terms.
The earlier anchored-ray note proves
\[
P_{ij}=\delta_{ij}
\tag{1.1}
\]
for every index.

This memo's previous claim
\[
R_{ij}=\delta_{ij},\qquad \beta_\infty(h_jv,h_jw_i)=0
\tag{1.2}
\]
is **withdrawn**.  Its ten-cell table is correct bounded evidence, but the
purported two-step induction omitted mandatory canonical module-vertex
normalization and did not prove the old--new and new--new order cancellations.
There is no bounded counterexample to (1.2), but there is also no all-index
proof here.

The strongest all-index result retained below is the exact complete-cover
factorization of all twelve endpoint paths.  The smallest unresolved cross
identity is the vanishing of the explicitly normalized two-step defects in
Section 4.  Claims of universal cancellation for the second and third
slot-zero candidates are also withdrawn.

## 2. Complete-cover path recurrence

Let \(\gamma=g^3\).  Let \(\kappa:K\to F(A,B,G)\) be the exact subgroup
rewrite supplied by the complete four-sheet cover, and let
\[
\Theta(k)=\operatorname{rev}(\kappa(k)).
\]
The reversal is present because source-flow paths record successive left
actions.  Hence
\[
\Theta(k\ell)=\operatorname{red}(\Theta(\ell)\Theta(k)).
\tag{2.1}
\]
The complete cover has all four signed transitions at every state, and the
Nielsen inverse used by `rewrite_k` is exact.  Therefore every formula below
is a group identity in \(F(A,B,G)\), not a pattern inferred from a radius.

Use the \(L_0\)-endpoint order
\[
(g_1,\ldots,g_6)=
(tc,cTTcttc,ctcTctc,ctcTcTctc,ctcTTTcttc,ctcTTTTcttc).
\tag{2.2}
\]
The component roots and right-\(c\) choices are
\[
(r_\nu)=(ct,1,ct,ct,ct,1),\qquad
(\epsilon_\nu)=(0,0,1,1,1,0).
\tag{2.3}
\]

### 2.0 Why the rewrite is an exact homomorphism

This step does not use a `proof_conclusion_*` Boolean.  Write
\[
Q=F(p,q)\rtimes\langle c\mid c^2=1\rangle,
\]
where conjugation by \(c\) exchanges \(p\) and \(q\).  The three subgroup
generators have semidirect images
\[
A=((p),0),\quad
B=((qPQp),1),\quad
G=((qPPq),1).
\tag{2.4}
\]
The parity-zero Reidemeister--Schreier words used by the implementation are
\[
\begin{aligned}
&p,\quad qPPqPqpQ,\quad qPQpqPqpQ,\\
&qPQppQPq,\quad qPQppQQp.
\end{aligned}
\tag{2.5}
\]
Folding these five loops gives a four-vertex, sixteen-directed-edge complete
cover of the \(p,q\)-rose.  It has eight unoriented edges and therefore free
rank \(8-4+1=5\).  Choose the deterministic spanning tree used by
`core_coordinates`.  In its five non-tree-edge basis, the five loops have
coordinates
\[
\begin{aligned}
(-1),\quad &(2,4,-5,3,-2),\quad (2,-3,-5,3,-2),\\
&(2,-3,-4,-3,2),\quad (2,-3,-4,-3,-1).
\end{aligned}
\tag{2.6}
\]
The recorded Nielsen reductions reduce this ordered tuple to the five signed
one-letter basis elements.  Reversing the same Nielsen moves gives the exact
inverse images
\[
\begin{aligned}
&(-1),\quad (1,-5,4),\\
&(1,-5,3,-2,1,-5,4),\\
&(-4,5,-1,2,-3,2,-3,5,-1),\\
&(1,-5,3,-2,-3,2,-3,5,-1).
\end{aligned}
\tag{2.7}
\]
Thus substitution by `CORE_IN_RS` is an inverse free-group homomorphism,
not a bounded membership oracle.  The Reidemeister--Schreier basis in the
\((A,B,G)\)-coordinates is
\[
(A),\quad (Gb),\quad (BAb),\quad (BB),\quad (BG).
\tag{2.8}
\]
These are the tuples `RS_IN_K`.  They are obtained from the transversal
\(\{1,B\}\), so adjoining the final \(B\) in the odd-parity case is the
usual Schreier reconstruction.  Composition of the core coordinate map,
the inverse Nielsen substitution, and (2.8) is therefore a homomorphism
\(\rho:K\to F(A,B,G)\).  Direct substitution in (2.4) gives
\(\rho(A)=A\), \(\rho(B)=B\), and \(\rho(G)=G\); conversely evaluation of
each of the five words in (2.8) gives the corresponding loop in (2.5).
Hence \(\rho\) and evaluation are inverse homomorphisms on all of \(K\).
The path readout \(\Theta=\operatorname{rev}\circ\rho\) is consequently the
exact anti-homomorphism (2.1) on arbitrary powers.

### 2.1 The six \(g_\nu h_jv\) paths

Put
\[
R=\texttt{BgAbaBgAgAggAB}.
\tag{2.9}
\]
The exact paths from the component roots are
\[
W^v_{\nu,j}=L_\nu R^{j+e_\nu}M_\nu,
\tag{2.10}
\]
and every displayed concatenation is freely reduced:

| \(\nu\) | \(L_\nu\) | \(e_\nu\) | \(M_\nu\) |
|---:|---|---:|---|
| 1 | `aGaG` | 1 | `BgAbaBgAgAg` |
| 2 | `agAB` | 1 | \(1\) |
| 3 | `aGaGbaBgAgAggAB` | 1 | \(1\) |
| 4 | `aGaGbaBgAgAggAB` | 1 | `aG` |
| 5 | `aGaGbaBgAgAggAB` | 0 | `BgAbaBgAgAg` |
| 6 | `agAB` | 1 | `aG` |

Equivalently, \(j\mapsto j+1\) inserts one \(R\) immediately before
\(M_\nu\):
\[
W^v_{\nu,j+1}=\operatorname{red}(W^v_{\nu,j}S_\nu),
\qquad S_\nu=M_\nu^{-1}RM_\nu,
\tag{2.11}
\]
where
\[
S_\nu=
\begin{cases}
\texttt{gABBgAbaBgAgAg},&\nu=1,5,\\
R,&\nu=2,3,\\
\texttt{gABgAbaBgAgAggABaG},&\nu=4,6.
\end{cases}
\tag{2.12}
\]

### 2.2 The six \(g_\nu h_jw_i\) paths

For all integers \(i,j\geq0\), including \(i<j\),
\[
\boxed{
W^w_{\nu,i,j}
=\operatorname{red}(P_\nu^i C_\nu Q_\nu^{i-j}).
}
\tag{2.13}
\]
The fixed words are:

| \(\nu\) | \(P_\nu=\Theta(Z_\nu)\) | \(C_\nu=\Theta(D_\nu)\) | \(Q_\nu=\Theta(X_\nu)\) |
|---:|---|---|---|
| 1 | `aBgAgAggABBgAb` | `aBgAgAggABBgAb` | `GaGaGbABaGbbaG` |
| 2 | `AgABBgAbaBgAgAga` | `AgABBgAbaBgAgAgBaGb` | `baGGaGaGbABaGb` |
| 3 | `aGbAAGaGbAAGaGbAAG` | `aGbAAGaGbAAGaGbAAG` | `baGGaGaGbABaGb` |
| 4 | `aGbAAGaGbAAGaGbAAG` | `aGbAAGaGbAAGaGbAAGaG` | `gAbaGGaGaGbABaGbaG` |
| 5 | `aGbAAGaGbAAGaGbAAG` | `aGbAAGaGbAAGaGbAAGbaG` | `GaGaGbABaGbbaG` |
| 6 | `AgABBgAbaBgAgAga` | `AgABBgAbaBgAgAgBaGbaG` | `gAbaGGaGaGbABaGbaG` |

Thus the radius-free increment rules are
\[
\begin{aligned}
W^w_{\nu,i,j+1}
 &=\operatorname{red}(W^w_{\nu,i,j}Q_\nu^{-1}),\\
W^w_{\nu,i+1,j}
 &=\operatorname{red}(P_\nu W^w_{\nu,i,j}Q_\nu),\\
W^w_{\nu,i+1,j+1}
 &=\operatorname{red}(P_\nu W^w_{\nu,i,j}).
\end{aligned}
\tag{2.14}
\]

The common block structure is clearer with
\[
u=\texttt{BgAb},\quad m=\texttt{BgAbaBgAgAg},\quad
z=\texttt{baG},\quad E=\texttt{aGbAAG}.
\]
Then
\[
\begin{aligned}
P_1&=u^{-1}Ru,&
P_2=P_6&=(ma)^{-1}R(ma),&
P_3=P_4=P_5&=E^3,\\
Q_1=Q_5&=z^{-1}R^{-1}z,&
Q_2=Q_3&=R^{-1},&
Q_4=Q_6&=(aG)^{-1}R^{-1}(aG).
\end{aligned}
\tag{2.15}
\]

To prove (2.13), set \(a_\nu=g_\nu p^{-1}\),
\(b_\nu=tc^{\epsilon_\nu}r_\nu^{-1}\), and
\[
X_\nu=a_\nu\gamma a_\nu^{-1},\quad
Z_\nu=b_\nu^{-1}\gamma^{-1}b_\nu,\quad
D_\nu=a_\nu c\gamma^{-1}b_\nu.
\]
The lifted endpoint ratio is identically
\[
k^w_{\nu,i,j}=X_\nu^{i-j}D_\nu Z_\nu^i.
\]
Applying the anti-homomorphism (2.1) gives (2.13), with
\(P_\nu=\Theta(Z_\nu)\), \(C_\nu=\Theta(D_\nu)\), and
\(Q_\nu=\Theta(X_\nu)\).  The proof of (2.10) is the same one-factor
specialization.  The six rows of the preceding table are the eighteen fixed
factor evaluations; each was obtained by the exact inverse-coordinate
homomorphism of Section 2.0.

## 3. From paths to the four anchored currents

For a rooted reduced path \(W\), let \(\mathsf E_s(W)\) be its mod-two
edge current in slot \(s\in\{2,3,4\}\), using exactly the certificate's
`B/b`, `G/g`, and `A/a` conventions.  Every edge label is stored at the
canonical module vertex returned by `c_vertex`; in particular a terminal
\(c\) is deleted only after quotient reduction.  Path concatenation gives
\[
\mathsf E_s(UV)=
\mathsf E_s(U)+u\,\mathsf E_s(V),
\tag{3.1}
\]
where \(u\) is the endpoint action of \(U\).  Inversion reverses the edge
chain and translates it by the inverse endpoint action.  These two rules
turn (2.10) and (2.13) into exact geometric-series formulas for every slot.

Because the source scalar is even, the doubled anchor disappears modulo two.
Therefore
\[
\begin{aligned}
J_0(x)&=e_x,\\
J_s(x)&=\sum_{\nu=1}^6\mathsf E_s(W_{\nu}(x)),
\qquad s=2,3,4.
\end{aligned}
\tag{3.2}
\]
Equations (2.10), (2.13), (3.1), and (3.2) are the promised radius-free
description of all twelve \(L_0\) endpoints and all four currents.

For a quotient action \(a\), define the exact occurrence translate
\[
(\tau_a f)_{\operatorname{cvert}(ax)}\mathrel{+}=f_x.
\tag{3.3}
\]
All equality, order, and inversion comparisons below are comparisons of
the canonical keys
\[
\operatorname{key}(x)=(|\operatorname{cvert}(x)|,
\operatorname{cvert}(x)).
\tag{3.4}
\]
Thus the twelve active occurrence currents are
\[
F_{r,j}=\tau_{a_r}J_{s_r}(h_jv),\qquad
G_{r,i,j}=\tau_{a_r}J_{s_r}(h_jw_i),
\tag{3.5}
\]
where \((s_r,a_r)\) is the exact active occurrence table at `a1a411b`.
For an inversion record with base action \(b\) and multiplier \(m\), its
arguments are first \(\tau_bJ_s\); every \(m\)-translate inside the
inversion predicate is again passed through `c_vertex`.  No raw
\(F(A,B,G)\)-vertex is ever compared directly.

## 4. Exact normalized difference identities still required

All primitive kernels are bilinear over \(\mathbb F_2\).  This gives an
exact way to state, rather than assume, the missing induction.

For a bilinear kernel \(B\) and normalized current families \(F_j,G_{i,j}\),
put
\[
\dot F_j=F_{j+2}+F_j,\quad
\dot G^{i}_{i,j}=G_{i+2,j}+G_{i,j},\quad
\dot G^{j}_{i,j}=G_{i,j+2}+G_{i,j}.
\tag{4.1}
\]
Every sum in (4.1) is taken after the occurrence action and the
`c_vertex` normalization in (3.3).  Then
\[
B(F_j,G_{i+2,j})+B(F_j,G_{i,j})
=B(F_j,\dot G^{i}_{i,j}),
\tag{4.2}
\]
and
\[
\begin{aligned}
B(F_{j+2},G_{i,j+2})+B(F_j,G_{i,j})
={}&B(\dot F_j,G_{i,j})+B(F_j,\dot G^{j}_{i,j})\\
&+B(\dot F_j,\dot G^{j}_{i,j}).
\end{aligned}
\tag{4.3}
\]
The first two terms on the right of (4.3) are the old--new contributions;
the third is the new--new contribution.  Equations (4.2)--(4.3) apply to
the four equality forms and all six polarized inversion forms, including
the second canonicalization after multiplying by the inversion multiplier.

For an external pair \(r<s\), let
\[
O_{rs}(i,j)=
\operatorname{LT}(F_{r,j},G_{s,i,j})+
\operatorname{LT}(G_{r,i,j},F_{s,j}).
\tag{4.4}
\]
Its exact \(i\)-difference is
\[
\begin{aligned}
O_{rs}(i+2,j)+O_{rs}(i,j)
={}&\operatorname{LT}(F_{r,j},\dot G^{i}_{s,i,j})\\
&+\operatorname{LT}(\dot G^{i}_{r,i,j},F_{s,j}),
\end{aligned}
\tag{4.5}
\]
and its exact \(j\)-difference is
\[
\begin{aligned}
O_{rs}(i,j+2)+O_{rs}(i,j)
={}&\operatorname{LT}(\dot F_{r,j},G_{s,i,j})
+\operatorname{LT}(F_{r,j},\dot G^{j}_{s,i,j})\\
&+\operatorname{LT}(\dot F_{r,j},\dot G^{j}_{s,i,j})\\
&+\operatorname{LT}(\dot G^{j}_{r,i,j},F_{s,j})
+\operatorname{LT}(G_{r,i,j},\dot F_{s,j})\\
&+\operatorname{LT}(\dot G^{j}_{r,i,j},\dot F_{s,j}).
\end{aligned}
\tag{4.6}
\]
This explicitly retains every old--new and new--new pair omitted by the
previous argument.

The path recurrences in Section 2 give exact finite-block expressions for
all dotted currents in (4.1), but the right sides of (4.2)--(4.6) have not
been proved zero after (3.3).  In particular, `c_vertex` can delete a
terminal \(c\) after an occurrence or inversion multiplier changes the
word.  Raw \(R/R^{-1}\)-block cancellation does not decide its shortlex
effect.

For a step whose two cells remain in the same strict open region, the
kernelwise identities required by the proposed two-periodic normal form are
\[
K(i+2,j)+K(i,j)=0,
\qquad K(i,j+2)+K(i,j)=0
\tag{4.7}
\]
for each of the 76 normalized kernels.  The first identity is required only
when both \((i,j)\) and \((i+2,j)\) lie in \(i<j\), or both lie in \(i>j\);
the second has the analogous restriction for \((i,j)\) and \((i,j+2)\).

The diagonal-crossing or diagonal-meeting cases are different.  An \(i\)-step
crosses or meets the diagonal at
\(i-j=-2,-1,0\), while a \(j\)-step crosses or meets it at
\(i-j=0,1,2\).  Their per-kernel values must be obtained by substituting
those six offsets into (4.2)--(4.6), not set to zero.  For example, the
proved primitive kernel \(P(i,j)=\delta_{ij}\) has \(i\)-step boundary
defects
\[
(1,0,1)\quad\text{at offsets }(-2,-1,0),
\tag{4.8}
\]
and \(j\)-step boundary defects
\[
(1,0,1)\quad\text{at offsets }(0,1,2).
\tag{4.9}
\]
Thus no constituent-wise boundary-zero statement is possible.

The smallest remaining cross proof obligation is consequently a finite
symbolic normal-form certificate with two kinds of output:

1. for steps staying in one strict open region, the 76 kernelwise zero
   identities (4.7); and
2. at the six crossing/meeting offsets, the exact 76-component defect
   vectors, with no componentwise-zero requirement.

If the future target is \(R=\delta\), the xor of the 75 companion components
at each boundary must equal the corresponding primitive defect in
(4.8)--(4.9).  Equivalently, for the full kernel \(\beta=P+R\), only the xor
of all 76 boundary defects must vanish.  The generator must enumerate
block-position vertices symbolically, apply `c_vertex(action * vertex)`, and
compare exact shortlex keys.  No such certificate exists in the current
files.

## 5. What the ten cells actually prove

For the ten representative cells ordered as
\[
<00,<01,<10,<11,=00,=11,>00,>01,>10,>11,
\tag{5.1}
\]
the exact normalized evaluator gives the following bounded signatures:

| kernels | representative signatures |
|---|---|
| equality slots \(0,2,3,4\) | `1111111111`, `0011010011`, `0011010011`, `1111111111` |
| inversion terms \(1,\ldots,6\) | `0000110000`, `0000000000`, `0000000000`, `0000000000`, `1010011010`, `0000000000` |
| equality xor \(\mathcal E\) | `0000000000` |
| inversion xor \(\mathcal I\) | `1010101010` |
| external xor \(\mathcal O\) | `1010101010` |

The first inversion row is the independently proved primitive identity
\(P_{ij}=\delta_{ij}\).  The other rows in this table are values at ten
representatives only.  They do not prove regional two-periodicity and are
not promoted to all-index formulas.

## 6. Retraction for the other two slot-zero candidates

The row-2 and row-3 aggregate ten-cell signatures from the previous draft
were bounded diagnostics.  Their six roots, eighteen fixed factors,
individual four equality rows, six inversion rows, 66 external rows, and
all-index primitive proofs were not displayed or proved.  All universal
claims for those two families are therefore deleted.  Their validity and
even source classes remain proved in the earlier memo, but their primitive
and companion matrices are open.

## 7. Base and unary terms

The base syndrome is
\[
C=(1,1,1,0,1,0,1,1,0,1,0,1,0,1,1).
\tag{7.1}
\]
It is constant under every diagonal-left context, so its translate matrix
has rank one (or rank zero after subtracting the base).

No unary-rank conclusion follows from the cross calculation.  Put
\[
U(D)=S(D)+S(0).
\]
On the first family the remaining unary matrix is
\[
\mathcal U_{ij}=U(H(h_jv))+U(H(h_jw_i)).
\tag{7.2}
\]
The first summand depends only on the row \(j\), hence has rank at most one.
The rank of the second summand is not proved finite or infinite here.
In particular, the fixed quotient-section defects
\[
\omega(q,r)=\widehat q\widehat r\widehat{qr}^{-1},
\]
the one-vertex transport defects, and the base--direction products cancel
from the four-corner Hessian but remain in (7.2).  Dropping them would give
an invalid unary argument.  Tensor-diagonal increments likewise have been
propagated through the complete circuit and are killed only at the final
exterior projection.

Separately from the unresolved cross defects in Section 4, the unary
question is the exact diagonal-left rank of
\[
(i,j)\longmapsto U(H(h_jw_i)),
\tag{7.3}
\]
with the complete typed-AST base, transport, and section defects retained.
The next finite proof obligation is to substitute (2.13) into the symbolic
unary evaluator and derive its one-step \(P_\nu/Q_\nu\) recurrence.  Because
the recurrence uses only the finitely many displayed fixed blocks, this is
a finite algebraic calculation; no source-depth census is needed.  Until
that calculation is done, neither finite nor infinite diagonal-left rank of
the complete validity-plus-syndrome function has been proved.

## 8. Verification boundary

The complete-cover homomorphism and the formal first-family endpoint
factorizations (2.10) and (2.13) are all-index statements.  The normalized
kernel signatures in Section 5 are bounded diagnostics only.  They check
transcription and supply no induction.

No source census, broad grid, or unbounded search was run in this fix round.
The single constant-size check printed the four-vertex/sixteen-edge core,
the five Reidemeister--Schreier loops, their five core-coordinate images,
the inverse Nielsen images, `RS_IN_K`, and the eighteen first-family values
\(\Theta(Z_\nu),\Theta(D_\nu),\Theta(X_\nu)\).  Its output is reproduced in
Section 2.0 and the fixed-factor table.

## Fix round 1

### Finding 1: missing `c_vertex(action*vertex)` normalization

Changed Sections 3 and 4 so that every current is stored at a canonical
module vertex, every occurrence translate is explicitly \(\tau_a\) from
(3.3), every shortlex key applies `c_vertex`, and every inversion multiplier
canonicalizes a second time.  The former raw-block comparison argument was
deleted.  **Proof status:** the formulation now agrees with the Task-2
certificate; the resulting all-index comparisons remain open.

### Finding 2: circular two-step invariance

Deleted the asserted ten-cell lemma and every all-index conclusion derived
from it.  Equations (4.2)--(4.6) are the exact bilinear differences, with all
old--new and new--new contributions displayed.  The six diagonal-crossing
offsets are listed separately.  **Proof status:** the regional zero identities
(4.7) are not proved, and the boundary defect vectors are not computed.
Together they are the smallest remaining cross certificate and must be
discharged symbolically, not by more samples.

### Finding 3: unsupported second/third families

Deleted their aggregate signatures as theorem data and retracted every
primitive, companion, and universal cancellation claim for those families.
**Proof status:** open; no conclusion is drawn without their full fixed
blocks and 76 individual normalized kernel records.

### Finding 4: missing exact Stallings/Nielsen proof

Added Section 2.0: the semidirect coordinates, five RS loops, complete core
size and rank, five core-coordinate images, five inverse Nielsen words,
`RS_IN_K`, the inverse-homomorphism argument, and all eighteen first-family
fixed-factor evaluations are displayed.  **Proof status:** repaired for the
first-family endpoint factorization.  Nothing from this finite algebraic
proof is used to revive the withdrawn comparison or row-2/row-3 claims.

### Bounded command and evidence

One project-local, bytecode-disabled Python command imported only the
subgroup/lift modules and printed the finite constants named above.  It
reported core `(base=0, vertices=4, directed_edges=16)` and exactly the
\(P_\nu,C_\nu,Q_\nu\) words in Section 2.2.  This verifies transcription of
the finite Stallings/Nielsen data; it is not evidence for (4.7).

## Fix round 2

The Section-4 boundary scope was corrected without new computation.

- Equation (4.7) now requires kernelwise two-periodicity only when both
  endpoints of the two-step move remain in the same strict region \(i<j\)
  or \(i>j\).
- The six crossing/meeting offsets are exact values to compute, not zero
  identities.  Equations (4.8)--(4.9) display the primitive kernel's
  nonzero boundary defects.
- A future companion proof must match the aggregate companion defect to the
  primitive defect; equivalently, a full-kernel proof requires only the xor
  of all 76 boundary defects to vanish.
- The smallest certificate obligation now separates regional kernelwise
  zeros from exact boundary defect vectors.  The withdrawn all-index theorem
  remains withdrawn.

No bounded replay, grid, census, or search was run in this fix round.
