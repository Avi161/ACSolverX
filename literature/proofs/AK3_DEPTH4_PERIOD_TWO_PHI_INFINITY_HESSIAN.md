# Period-two \(\Phi_\infty\) Hessian: exact documented rank boundary

## Status

This note closes Task 3 only as a documented-open boundary.  It records the
exact crossed Fox--Magnus Hessian, its pullback through the anchored tree-flow
map, the surviving first-family ray identities, and the exact unary
recurrence.  It does **not** decide finite versus infinite diagonal-left rank.

The status split is essential.

- The sixteen-occurrence crossed Hessian and the twelve-occurrence anchored
  normal form are universal proved formulas.
- The first ray family's primitive kernel satisfies
  \(P_{ij}=\delta_{ij}\) for every \(i,j\geq0\), and its complete-cover paths
  obey exact all-index recurrences.
- The ten cross cells and ten unary cells below are exact bounded fixtures.
- The former all-index companion identity, the row-2/row-3 primitive and
  companion identities, and all conclusions derived from them are withdrawn.
- Finite rank, infinite rank, the period-two lift, stable
  Andrews--Curtis, and Andrews--Curtis all remain open.

The executable source is
[`depth4_period_two_phi_infinity_hessian_certificate.py`](../../experiments/stable_ac/depth4_period_two_phi_infinity_hessian_certificate.py),
and the independent assertions are in
[`test_ak_depth_four_period_two_phi_infinity_hessian.py`](../../tests/stable_ac/test_ak_depth_four_period_two_phi_infinity_hessian.py).
The universal source-to-flow theorem used here is
[`AK3_DEPTH4_PERIOD_TWO_TREE_FLOW_FACTORIZATION.md`](AK3_DEPTH4_PERIOD_TWO_TREE_FLOW_FACTORIZATION.md).

## 1. Exact crossed occurrence theorem

Let the five correction slots be numbered \(0,\ldots,4\).  Expanding the
literal typed residual AST, while retaining inverse polarity, gives exactly
the following sixteen correction occurrences.  Prefixes are reduced quotient
words and \(1\) denotes the empty prefix.

| residual order | slot | polarity | quotient prefix |
|---:|---:|---:|---|
| 1 | 2 | \(+1\) | \(1\) |
| 2 | 1 | \(+1\) | `tc` |
| 3 | 0 | \(+1\) | `tc` |
| 4 | 0 | \(-1\) | `ctcTTTcttc` |
| 5 | 1 | \(-1\) | `ctcTctt` |
| 6 | 2 | \(-1\) | `ctcTcTctc` |
| 7 | 0 | \(+1\) | `ctcTcTctc` |
| 8 | 0 | \(-1\) | `ctcTTTTcttc` |
| 9 | 3 | \(+1\) | `ctcTTctt` |
| 10 | 1 | \(+1\) | `ctcTctc` |
| 11 | 0 | \(+1\) | `ctcTctc` |
| 12 | 0 | \(-1\) | `cTTcttc` |
| 13 | 1 | \(-1\) | `tt` |
| 14 | 3 | \(-1\) | `t` |
| 15 | 4 | \(+1\) | `t` |
| 16 | 4 | \(-1\) | \(1\) |

Thus the slot counts are
\[
(6,4,2,2,2).
\]
There are eight positive internal terms, eight negative internal terms, 120
external occurrence pairs, and sixteen propagated tensor-diagonal terms.
The independent pinned table and AST expansion agree, every signed prefix
reproduces the corresponding first-derivative operator, and the complete
coefficient-record digest is

```text
854992f8a84a26ede55b22cd6a6a413c706101170766b59a33ea6c86b596a9a8
```

Positive and inverse correction leaves have the polarity-correct section
jets \(\Gamma_+\) and \(\Gamma_-\).  The symbolic raw mixed tensor, including
all propagated diagonals, agrees with an independent direct four-corner raw
tensor before exterior projection.  Tensor diagonals are propagated through
the quotient action and the complete residual circuit; they are killed only
by the final exterior projection, never deleted at a correction leaf.

## 2. Exact anchored normal form

For an anchored direction \(H(v)\), slot one is identically zero.  Removing
only the four slot-one occurrences leaves these twelve active occurrences.

| active order | residual order | slot | polarity | action |
|---:|---:|---:|---:|---|
| 1 | 1 | 2 | \(+1\) | \(1\) |
| 2 | 3 | 0 | \(+1\) | `tc` |
| 3 | 4 | 0 | \(-1\) | `ctcTTTcttc` |
| 4 | 6 | 2 | \(-1\) | `ctcTcTctc` |
| 5 | 7 | 0 | \(+1\) | `ctcTcTctc` |
| 6 | 8 | 0 | \(-1\) | `ctcTTTTcttc` |
| 7 | 9 | 3 | \(+1\) | `ctcTTctt` |
| 8 | 11 | 0 | \(+1\) | `ctcTctc` |
| 9 | 12 | 0 | \(-1\) | `cTTcttc` |
| 10 | 14 | 3 | \(-1\) | `t` |
| 11 | 15 | 4 | \(+1\) | `t` |
| 12 | 16 | 4 | \(-1\) | \(1\) |

The anchored slot counts are \((6,0,2,2,2)\).  Exact normalization of the
mixed full-wedge bit gives

\[
\boxed{\beta_\infty=\mathcal E+\mathcal I+\mathcal O}
\tag{2.1}
\]

with four equality forms, six polarized inversion forms, and 66 unordered
external occurrence pairs.  The external pairs contribute 132 oriented
monomials.  Before reduction modulo two their occurrence signs are 30
positive and 36 negative; after reduction every external coefficient is one.
There are no duplicate external type keys and no generic transpose pair.

The equality records are

| slot | negative active orders | integral multiplicity | mod-two coefficient |
|---:|---|---:|---:|
| 0 | \((3,6,9)\) | 3 | 1 |
| 2 | \((4)\) | 1 | 1 |
| 3 | \((10)\) | 1 | 1 |
| 4 | \((12)\) | 1 | 1 |

The inversion records are

| slot | active pair | base action | paired action | multiplier |
|---:|---|---|---|---|
| 0 | \((2,3)\) | `tc` | `ctcTTTcttc` | `ctcTTTct` |
| 0 | \((5,6)\) | `ctcTcTctc` | `ctcTTTTcttc` | `ctcTTTTctctctcTc` |
| 0 | \((8,9)\) | `ctcTctc` | `cTTcttc` | `cTTctctcTc` |
| 2 | \((1,4)\) | \(1\) | `ctcTcTctc` | `ctcTcTctc` |
| 3 | \((7,10)\) | `ctcTTctt` | `t` | `TcttcTc` |
| 4 | \((11,12)\) | `t` | \(1\) | `T` |

Every inversion coefficient is one.  In particular the last record is the
coefficient-one term
\[
\operatorname{PInv}_T(tJ_4(v),tJ_4(w)).
\]
The external-order reversal identity follows from homogeneity, and the
pullback uses the unique linear forest flow rather than a bounded census.
The anchored normal-form digest is

```text
c044b3d7d3dbeb430f8d27c89f69d85aeedbf058363892e2b19acc4c4aaefdef
```

## 3. The retained first ray family

Put
\[
p=tc,\qquad g=ctcTTTct,\qquad \gamma=g^3,\qquad n_i=5+3i,
\]
and
\[
v=p^{-1}T,\qquad
w_i=p^{-1}g^{n_i}cg^{-(n_i-2)}t,\qquad
h_j=p^{-1}g^{-n_j}p.
\tag{3.1}
\]
Both \(h_jv\) and \(h_jw_i\) have source scalar \(-2\), so
\(e_{h_jv}-e_{h_jw_i}\) is component-balanced for every \(i,j\geq0\).
Modulo two, each slot-zero current is a singleton.

Let \(P_{ij}\) denote the first slot-zero inversion term in Section 2, the
record with base action `tc` and multiplier `ctcTTTct`.  The exact anchored
ray argument proves
\[
\boxed{P_{ij}=\delta_{ij}\qquad(i,j\geq0).}
\tag{3.2}
\]
This is the only retained all-index primitive identity.  No analogous
row-2 or row-3 primitive theorem is stated here.

### 3.1 Exact complete-cover factorization

Let \(\kappa:K\to F(A,B,G)\) be the inverse-coordinate homomorphism supplied
by the complete four-sheet Stallings cover and its displayed Nielsen inverse,
and set
\[
\Theta(k)=\operatorname{rev}(\kappa(k)).
\]
Then, for arbitrary powers,
\[
\Theta(k\ell)=\operatorname{red}(\Theta(\ell)\Theta(k)).
\tag{3.3}
\]
This is an exact anti-homomorphism, not a bounded membership replay.

For the six \(L_0\) endpoints, in the order
\[
(tc,cTTcttc,ctcTctc,ctcTcTctc,ctcTTTcttc,ctcTTTTcttc),
\]
put
\[
R=\texttt{BgAbaBgAgAggAB}.
\]
The \(h_jv\) paths are
\[
W^v_{\nu,j}=L_\nu R^{j+e_\nu}M_\nu,
\tag{3.4}
\]
with freely reduced factors

| \(\nu\) | \(L_\nu\) | \(e_\nu\) | \(M_\nu\) |
|---:|---|---:|---|
| 1 | `aGaG` | 1 | `BgAbaBgAgAg` |
| 2 | `agAB` | 1 | \(1\) |
| 3 | `aGaGbaBgAgAggAB` | 1 | \(1\) |
| 4 | `aGaGbaBgAgAggAB` | 1 | `aG` |
| 5 | `aGaGbaBgAgAggAB` | 0 | `BgAbaBgAgAg` |
| 6 | `agAB` | 1 | `aG` |

The \(h_jw_i\) paths are, including when \(i<j\),
\[
\boxed{W^w_{\nu,i,j}=\operatorname{red}(P_\nu^iC_\nu Q_\nu^{i-j}).}
\tag{3.5}
\]
Here the path words \(P_\nu\) are unrelated to the primitive scalar
\(P_{ij}\) in (3.2), and the fixed factors are

| \(\nu\) | \(P_\nu\) | \(C_\nu\) | \(Q_\nu\) |
|---:|---|---|---|
| 1 | `aBgAgAggABBgAb` | `aBgAgAggABBgAb` | `GaGaGbABaGbbaG` |
| 2 | `AgABBgAbaBgAgAga` | `AgABBgAbaBgAgAgBaGb` | `baGGaGaGbABaGb` |
| 3 | `aGbAAGaGbAAGaGbAAG` | `aGbAAGaGbAAGaGbAAG` | `baGGaGaGbABaGb` |
| 4 | `aGbAAGaGbAAGaGbAAG` | `aGbAAGaGbAAGaGbAAGaG` | `gAbaGGaGaGbABaGbaG` |
| 5 | `aGbAAGaGbAAGaGbAAG` | `aGbAAGaGbAAGaGbAAGbaG` | `GaGaGbABaGbbaG` |
| 6 | `AgABBgAbaBgAgAga` | `AgABBgAbaBgAgAgBaGbaG` | `gAbaGGaGaGbABaGbaG` |

Thus
\[
\begin{aligned}
W^w_{\nu,i,j+1}&=\operatorname{red}(W^w_{\nu,i,j}Q_\nu^{-1}),\\
W^w_{\nu,i+1,j}&=\operatorname{red}(P_\nu W^w_{\nu,i,j}Q_\nu),\\
W^w_{\nu,i+1,j+1}&=\operatorname{red}(P_\nu W^w_{\nu,i,j}).
\end{aligned}
\tag{3.6}
\]

### 3.2 Exact right-deck and current recurrence

Stored path letters act successively on the left.  If
\(W=w_1\cdots w_m\), define the ordinary endpoint multiplier
\[
\operatorname{ev}_L(W)=w_m\cdots w_1.
\]
For a rooted component vertex \(ko\), the right deck action is
\[
R_h(ko)=(kh)o.
\tag{3.7}
\]
It preserves every oriented \(A/B/G\)-edge label.  Write
\([W]=R_{\operatorname{ev}_L(W)}\), and let \(\mathsf E_s(W)\) be the
integral edge current in slot \(s\in\{2,3,4\}\).  Then
\[
[UV]=[U][V],\qquad
\mathsf E_s(UV)=\mathsf E_s(U)+[U]\mathsf E_s(V).
\tag{3.8}
\]

Set
\[
a_{\nu,ij}=[W^w_{\nu,i,j}],\quad
x^s_{\nu,ij}=\mathsf E_s(W^w_{\nu,i,j}),\quad
p_\nu=[P_\nu],\quad q_\nu=[Q_\nu].
\]
The six all-index state/current recurrences are
\[
\boxed{
\begin{aligned}
a_{\nu,i,j+1}&=a_{\nu,ij}q_\nu^{-1},\\
x^s_{\nu,i,j+1}
 &=x^s_{\nu,ij}+a_{\nu,ij}\mathsf E_s(Q_\nu^{-1}),\\
a_{\nu,i+1,j}&=p_\nu a_{\nu,ij}q_\nu,\\
x^s_{\nu,i+1,j}
 &=\mathsf E_s(P_\nu)+p_\nu x^s_{\nu,ij}
   +p_\nu a_{\nu,ij}\mathsf E_s(Q_\nu),\\
a_{\nu,i+1,j+1}&=p_\nu a_{\nu,ij},\\
x^s_{\nu,i+1,j+1}
 &=\mathsf E_s(P_\nu)+p_\nu x^s_{\nu,ij}.
\end{aligned}}
\tag{3.9}
\]
These are identities of finite edge chains, not finite-state claims: their
states are unbounded sparse currents and deck operators.

## 4. Exact cross-Hessian boundary

All occurrence translates and all inversion-multiplier translates must be
accumulated at
\[
\operatorname{cvert}(ax),
\tag{4.1}
\]
and every order comparison uses the canonical shortlex key
\[
(|\operatorname{cvert}(x)|,\operatorname{cvert}(x)).
\tag{4.2}
\]
The map `c_vertex` is not a group homomorphism: quotient reduction may
delete a terminal \(c\).  Raw free-word block cancellation therefore cannot
prove an order identity.

Let \(F_{r,j}\) and \(G_{r,i,j}\) be the twelve normalized occurrence
currents for \(H(h_jv)\) and \(H(h_jw_i)\).  Define
\[
\dot F_j=F_{j+2}+F_j,quad
\dot G^i_{i,j}=G_{i+2,j}+G_{i,j},quad
\dot G^j_{i,j}=G_{i,j+2}+G_{i,j},
\tag{4.3}
\]
only after occurrence action and canonical accumulation.

For each of the four equality and six inversion bilinear forms \(B\), the
exact two-step defects are
\[
B(F_j,G_{i+2,j})+B(F_j,G_{i,j})
=B(F_j,\dot G^i_{i,j}),
\tag{4.4}
\]
and
\[
\begin{aligned}
B(F_{j+2},G_{i,j+2})+B(F_j,G_{i,j})
={}&B(\dot F_j,G_{i,j})+B(F_j,\dot G^j_{i,j})\\
&+B(\dot F_j,\dot G^j_{i,j}).
\end{aligned}
\tag{4.5}
\]
For each external pair \(r<s\), put
\[
O_{rs}(i,j)=\operatorname{LT}(F_{r,j},G_{s,i,j})
+\operatorname{LT}(G_{r,i,j},F_{s,j}).
\]
Its exact defects are
\[
\begin{aligned}
O_{rs}(i+2,j)+O_{rs}(i,j)
={}&\operatorname{LT}(F_{r,j},\dot G^i_{s,i,j})\\
&+\operatorname{LT}(\dot G^i_{r,i,j},F_{s,j}),
\end{aligned}
\tag{4.6}
\]
and
\[
\begin{aligned}
O_{rs}(i,j+2)+O_{rs}(i,j)
={}&\operatorname{LT}(\dot F_{r,j},G_{s,i,j})
+\operatorname{LT}(F_{r,j},\dot G^j_{s,i,j})\\
&+\operatorname{LT}(\dot F_{r,j},\dot G^j_{s,i,j})
+\operatorname{LT}(\dot G^j_{r,i,j},F_{s,j})\\
&+\operatorname{LT}(G_{r,i,j},\dot F_{s,j})
+\operatorname{LT}(\dot G^j_{r,i,j},\dot F_{s,j}).
\end{aligned}
\tag{4.7}
\]
These formulas retain every old--new and new--new contribution.

Equations (4.4)--(4.7) define the exact 76 canonical two-step defect
obligations: four equality components, six inversion components, and 66
external components.  For a step whose endpoints stay in the same strict
region \(i<j\) or \(i>j\), the proposed two-periodic normal form requires
each component defect to vanish.  At the diagonal-crossing or
diagonal-meeting offsets, the components are values to compute, not zeros:

- the \(i\)-step offsets are \(i-j=-2,-1,0\);
- the \(j\)-step offsets are \(i-j=0,1,2\).

For the proved primitive \(P_{ij}=\delta_{ij}\), both ordered boundary
defect triples are
\[
(1,0,1).
\tag{4.8}
\]
A future proof of a companion equality \(R=\delta\) would have to make the
xor of the 75 companion boundary components equal these primitive defects.
Equivalently, a proof for the full \(\beta=P+R\) would require only the xor
of all 76 boundary components to vanish.  No such all-index certificate is
present.

### 4.1 Exact ten-cell cross fixture

Order the representative cells as
\[
<00,<01,<10,<11,=00,=11,>00,>01,>10,>11.
\tag{4.9}
\]
The exact normalized bounded signatures are

| kernels | ten-bit signatures |
|---|---|
| equality slots \(0,2,3,4\) | `1111111111`, `0011010011`, `0011010011`, `1111111111` |
| inversion terms \(1,\ldots,6\) | `0000110000`, `0000000000`, `0000000000`, `0000000000`, `1010011010`, `0000000000` |
| equality xor \(\mathcal E\) | `0000000000` |
| inversion xor \(\mathcal I\) | `1010101010` |
| external xor \(\mathcal O\) | `1010101010` |

The first inversion row is the proved primitive identity.  Every other row
in this table is a bounded diagnostic only.  The table does not prove
regional two-periodicity.

### 4.2 Withdrawn companion and other-family claims

Writing \(R_{ij}\) for the xor of the other 75 normalized kernels, the
former assertions
\[
R_{ij}=\delta_{ij},\qquad
\beta_\infty(H(h_jv),H(h_jw_i))=0
\quad\text{for all }i,j
\tag{4.10}
\]
are withdrawn.  The attempted induction omitted the mandatory
`c_vertex(action * vertex)` normalization and did not prove the old--new and
new--new order cancellations.  The ten-cell table is consistent with
(4.10), but it is not an all-index proof.

The former row-2 and row-3 aggregate signatures were also bounded
diagnostics.  Their all-index primitive, companion, and cancellation claims
are withdrawn and are not revived here.  Their matrices remain open.

## 5. Universal coboundary, but not universal vanishing

Let \(s_\infty(D)\) be the final full-wedge syndrome bit, let
\[
C_\infty=s_\infty(0),\qquad
q_\infty(D)=s_\infty(D)+C_\infty.
\]
For all finitely supported homogeneous mod-two directions,
\[
\boxed{
\beta_\infty(D,E)
=q_\infty(D+E)+q_\infty(D)+q_\infty(E)
=(\delta q_\infty)(D,E).
}
\tag{5.1}
\]
The affine-quadratic and period-two theorems make this form symmetric,
biadditive, and alternating.  Its ordinary group-cohomology class is zero.
Pointwise vanishing does not follow: a quadratic one-cochain can have a
nonzero alternating polarization in characteristic two.

The retained anchored counterexample is
\[
D=H(TTT),\qquad E=H(cTTT).
\]
The exact four syndrome corners, in the order \(0,D,E,D+E\), are
\[
(1,1,0,1),
\]
so
\[
\boxed{\beta_\infty(H(TTT),H(cTTT))=1.}
\tag{5.2}
\]
The independent normalized subtotals are
\[
(\mathcal E,\mathcal I,\mathcal O)=(0,1,0),
\]
and give the same total.  Thus \(\beta_\infty\) does not vanish on the
anchored image and does not vanish on all of \(\ker L\).  Coboundary or
alternation alone cannot prove the withdrawn ray-family cancellation.

## 6. Exact integral unary recurrence

The complete rank target includes the base and unary syndrome, not just the
cross Hessian.  Let
\[
y_{ij}=h_jw_i
=p^{-1}\gamma^{i-j}c\gamma^{-(i+1)}t,
\qquad D_{ij}=H(y_{ij}),
\tag{6.1}
\]
where the raw quotient product is formed before canonicalization.  With
anchor \(a=T\) and the six \(L_0\)-signs
\[
(\epsilon_1,\ldots,\epsilon_6)=(+1,-1,+1,+1,-1,-1),
\]
the exact integral currents are
\[
\begin{aligned}
D_{ij,0}&=e_{y_{ij}}+2e_a,&D_{ij,1}&=0,\\
D_{ij,s}&=\sum_{\nu=1}^6\epsilon_\nu
\mathsf E_s(W^w_{\nu,i,j})+2A_s,
&&s=2,3,4,
\end{aligned}
\tag{6.2}
\]
where \(A_s\) is the fixed anchor flow.  The doubled terms vanish in the
parity shadow but must remain in the integral unary evaluator.

### 6.1 Base, transport, and section terms

Represent a typed AST node by a crossed class-two coordinate
\[
X=(q,a,A)\in Q\ltimes(V\oplus V\otimes V).
\]
For an integral current \(f\), the canonical positive correction section is
\[
K(f)=(1,f,\sigma(f)),
\]
where
\[
\sigma(f)=\sum_x\binom{f_x}{2}e_x\otimes e_x
+\sum_{x<y}f_xf_y e_x\otimes e_y.
\tag{6.3}
\]
For a quotient word \(q\), let \(\tau_q(b)\) be the sum of the complete
one-vertex transport tensors, and let
\[
\Omega(q,r)=(1,o_{q,r},O_{q,r})
\]
be the complete coordinate of the section defect
\(\widehat q\widehat r\widehat{qr}^{-1}\).  Then
\[
\boxed{
\begin{aligned}
(q,a,A)\star(r,b,B)&=(qr,c,C),\\
c&=a+qb+o_{q,r},\\
C&=A+qB+\tau_q(b)+a\otimes(qb)+O_{q,r}
 +(a+qb)\otimes o_{q,r}.
\end{aligned}}
\tag{6.4}
\]
The terms \(a\otimes(qb)\), \(\tau_q(b)\), and
\((o_{q,r},O_{q,r})\) are respectively the base--direction products,
one-vertex transport defects, and quotient-section defects.  None may be
dropped from a unary calculation.  Inversion is
\[
\operatorname{Inv}(q,a,A)
=\Lambda(q^{-1})\star(1,-a,-A+a\otimes a),
\tag{6.5}
\]
and conjugation uses the literal AST order
\(X\star Y\star\operatorname{Inv}(X)\).

Let \(B\) be the fixed tracked correction and let \(M_B(F)\) be the final
tensor of the literal residual AST evaluated at \(B+F\).  The exact unary
syndrome is
\[
\boxed{U_{ij}=\Pi\bigl(M_B(D_{ij})-M_B(0)\bigr)\in\mathbb F_2^{15}.}
\tag{6.6}
\]
Every internal tensor diagonal from (6.3)--(6.5) is carried through the
AST.  For an integral homogeneous input, the final residual lies in the
commutator subgroup, so its degree-two tensor is antisymmetric and
diagonal-free before the implementation's wedge reader is called.

### 6.2 Integral increments

Define
\[
\widetilde\Delta^j_{ij}=D_{i,j+1}-D_{ij}.
\]
It is an integral homogeneous direction, and the right-deck recurrence gives
\[
\begin{aligned}
\widetilde\Delta^j_{ij,0}&=e_{y_{i,j+1}}-e_{y_{ij}},
&\widetilde\Delta^j_{ij,1}&=0,\\
\widetilde\Delta^j_{ij,s}
&=\sum_{\nu=1}^6\epsilon_\nu
a_{\nu,ij}\mathsf E_s(Q_\nu^{-1}),
&&s=2,3,4.
\end{aligned}
\tag{6.7}
\]
Let \(u_\infty(F)\) denote the final coordinate of the complete unary
evaluator on an integral homogeneous direction \(F\), and put
\(u_{ij}=U_{ij}^{(\infty)}\).  Affine quadraticity gives the exact scalar
increment identity
\[
\boxed{
u_{i,j+1}+u_{ij}
=u_\infty(\widetilde\Delta^j_{ij})
+\beta_\infty(D_{ij},\widetilde\Delta^j_{ij}).
}
\tag{6.8}
\]
The first term retains all fixed-base, transport, and section defects.  The
second is evaluated by the exact mixed formula.  Equation (6.8) is an exact
evaluator-level recurrence, not a smaller closed recurrence and not a
finite-state theorem.  The \(i\)- and diagonal-increment identities follow
from the other two lines of (3.9) in the same integral typing.

### 6.3 Exact ten-cell unary fixture

In the cell order (4.9), the complete unary vectors are

| cell | \((i,j)\) | \(U_{ij}\) |
|---|---:|---|
| `<00` | \((0,2)\) | `000110100110010` |
| `<01` | \((0,1)\) | `111111101101010` |
| `<10` | \((1,2)\) | `110111111010110` |
| `<11` | \((1,3)\) | `111111110011110` |
| `=00` | \((0,0)\) | `010111100110111` |
| `=11` | \((1,1)\) | `101110110001011` |
| `>00` | \((2,0)\) | `010110101100110` |
| `>01` | \((2,1)\) | `101110101111110` |
| `>10` | \((1,0)\) | `100110111010010` |
| `>11` | \((3,1)\) | `011111110010110` |

Their final-bit signature is

```text
0000110000
```

and therefore matches \(\delta_{ij}\) on these ten representatives only.
The other fourteen coordinates already show that the complete unary vector
is not determined merely by equality versus inequality on this fixture.
No two-step invariance or all-index unary delta identity follows.

## 7. Exact rank and Andrews--Curtis boundary

The base syndrome is
\[
S(0)=111010110101011.
\]
As a constant diagonal-left matrix it has rank one, or rank zero after base
subtraction.  On the first family, the term \(U(H(h_jv))\) depends only on
the row \(j\), so each coordinate has rank at most one.  The rank of
\[
(i,j)\longmapsto U(H(h_jw_i))
\]
is not decided.

The exact evidence points in incompatible directions unless the missing
identities are supplied:

- the primitive cross kernel is an infinite identity matrix;
- its 75-kernel companion is not proved to cancel it or preserve it;
- the universal mixed kernel is a nonzero coboundary on the anchored image;
- the ten unary final bits form an identity pattern, but no all-index proof
  exists; and
- the exact path/unary recurrences have unbounded sparse state.

Consequently neither finite nor infinite diagonal-left rank of the complete
validity-plus-fifteen-bit-syndrome function has been proved.  In particular,
there is no proved finite quotient, no proved reversible finite
\(c,t,T\)-transition system, and no proved infinite-Hankel-rank family in the
complete anchored image.

Task 3 is therefore an **exact documented-open boundary**, not a completed
rank decision.  The period-two lift problem, stable Andrews--Curtis, and
Andrews--Curtis remain open.  No claim in this note converts a bounded source
census or the ten representative cells into an all-index theorem.

## 8. Focused verification

The retained focused suite is

```bash
uv run pytest -q \
  tests/stable_ac/test_ak_depth_four_period_two_phi_infinity_hessian.py \
  tests/stable_ac/test_ak_depth_four_period_two_tree_flow_factorization.py \
  tests/stable_ac/test_ak_depth_four_period_two_source_flow.py \
  tests/stable_ac/test_ak_depth_four_period_two_subgroup_rewrite.py
```

It jointly checks the independent AST and pinned occurrence table, exact
operators, tensor and wedge oracles, anchored normal form, unique tree flow,
source reconstruction, and complete-cover subgroup rewriting.  These tests
verify the finite certificate and the inputs to the abstract arguments; they
do not decide the open all-index cross or unary rank obligations.
