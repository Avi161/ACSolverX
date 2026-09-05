# Exact unary recurrence on the first period-two raw ray

Date: 2026-07-29

Scope: exact algebra for the diagonal-left unary function, followed by one
constant-size symbolic replay.  The derivation uses the literal typed AST and
the raw complete-cover path recurrences.  It does not assume the all-index
cross cancellation theorem from the companion note.  It runs no source
census, parameter grid, or unbounded search.

## 1. Exact conclusion

Let
\[
p=tc,\qquad g=ctcTTTct,\qquad \gamma=g^3,\qquad n_i=5+3i,
\]
and
\[
y_{ij}=h_jw_i
=p^{-1}g^{n_i-n_j}c g^{-(n_i-2)}t
=p^{-1}\gamma^{i-j}c\gamma^{-(i+1)}t.
\tag{1.1}
\]
The product in (1.1) is a product in the raw quotient group and is
canonicalized only after the whole product has been formed.  In particular,
the factor ending in `c` is never passed to `parse_quotient`.

Write
\[
D_{ij}=H(y_{ij}),\qquad
U_{ij}=U(D_{ij})=S(D_{ij})+S(0)\in\mathbb F_2^{15}.
\tag{1.2}
\]
The exact result proved here is an explicit recurrence for the complete
matrix \(U_{ij}\).  It has two layers:

1. six raw path states obey the displayed \(P_\nu/Q_\nu\) cocycle recurrence
   in Section 3 and reconstruct all five currents of \(D_{ij}\), including
   the fixed doubled anchor currents; and
2. the crossed class-two coordinate recurrence in Section 4 evaluates the
   literal residual AST at \(B+D_{ij}\).  It includes every base--direction
   product, one-vertex transport term, and quotient-section defect.  Tensor
   diagonals are retained at every internal gate; for an integral
   homogeneous input they cancel in the final residual tensor before the
   implementation's exterior reader is called.

This is a finite *rule*, but not a finite-state theorem: its state contains
unbounded sparse currents and tensors.  Neither finite-index periodicity nor
infinite rank is proved.

For the last, full-wedge coordinate
\[
u_{ij}=U_{ij}^{(\infty)},
\]
one exact integral scalar increment identity is
\[
\boxed{
u_{i,j+1}+u_{ij}
=u_\infty(\widetilde\Delta^j_{ij})
+\beta_\infty(D_{ij},\widetilde\Delta^j_{ij}),
}
\tag{1.3}
\]
where
\(\widetilde\Delta^j_{ij}=D_{i,j+1}-D_{ij}\) is an integral homogeneous
direction whose five currents are given explicitly in (5.2).  Formula (1.3)
does not delete the unary defects: they occur in
\(u_\infty(\widetilde\Delta^j_{ij})\).  The second term is evaluated by the
exact sixteen-internal/120-external mixed formula and therefore needs no
cross-cancellation hypothesis.  This identity still invokes the complete
unary evaluator on its increment; it is not asserted to be a smaller closed
recurrence.

One exact replay on the ten comparison/parity representatives gave
\[
u_{ij}=\delta_{ij}
\tag{1.4}
\]
on those ten representatives.  This is bounded evidence only.  An
all-index proof of (1.4) would give an infinite identity submatrix in the
last unary coordinate, but the required fixed-block cancellation in the
right side of (1.3) is not proved here.

## 2. The exact anchored direction, with the doubled fixed part retained

Use the six \(L_0\)-terms and signs
\[
(\epsilon_1,\ldots,\epsilon_6)=(+1,-1,+1,+1,-1,-1).
\tag{2.1}
\]
Let \(a=T\) be the fixed anchor.  The finite action computation gives
\(\lambda(y_{ij})=-2\) for all \(i,j\).  Thus the integral slot-zero current
is
\[
D_{ij,0}=e_{y_{ij}}+2e_a,
\qquad D_{ij,1}=0.
\tag{2.2}
\]

For \(s\in\{2,3,4\}\), let \(\mathsf E_s(W)\) be the signed oriented
\(B/G/A\)-edge current of a reduced complete-cover path \(W\), with exactly
the conventions of `build_l0_direction_from_pairs`.  Let \(W_\nu(a)\) be
the fixed root path to the endpoint \(g_\nu a\), and put
\[
A_s=\sum_{\nu=1}^6\epsilon_\nu\mathsf E_s(W_\nu(a)).
\tag{2.3}
\]
The unique finite tree flow gives the exact integral currents
\[
\boxed{
D_{ij,s}
=\sum_{\nu=1}^6\epsilon_\nu
  \mathsf E_s(W^w_{\nu,i,j})+2A_s,
\qquad s=2,3,4.
}
\tag{2.4}
\]
Coefficientwise reduction of (2.2)--(2.4) gives the parity shadow
\[
\overline D_{ij}
=\left(e_{y_{ij}},0,
\sum_\nu\mathsf E_2(W^w_{\nu,i,j}),
\sum_\nu\mathsf E_3(W^w_{\nu,i,j}),
\sum_\nu\mathsf E_4(W^w_{\nu,i,j})\right).
\tag{2.5}
\]

Equation (2.5) is recorded only as a parity shadow of the exact tree flow.
It is not substituted into \(M_B\) or \(u_\infty\) anywhere below.  Every
AST evaluation in this memo uses the integral currents (2.2)--(2.4).  In
particular, this memo does not assume that the class-two coordinate descends
to an untyped coefficientwise mod-two representative.

## 3. Raw six-path recurrence

The exact complete-cover factorization is
\[
W^w_{\nu,i,j}=\operatorname{red}(P_\nu^iC_\nu Q_\nu^{i-j})
\qquad(i,j\ge0),
\tag{3.1}
\]
where negative powers are allowed.  The fixed words are

| \(\nu\) | \(P_\nu\) | \(C_\nu\) | \(Q_\nu\) |
|---:|---|---|---|
| 1 | `aBgAgAggABBgAb` | `aBgAgAggABBgAb` | `GaGaGbABaGbbaG` |
| 2 | `AgABBgAbaBgAgAga` | `AgABBgAbaBgAgAgBaGb` | `baGGaGaGbABaGb` |
| 3 | `aGbAAGaGbAAGaGbAAG` | `aGbAAGaGbAAGaGbAAG` | `baGGaGaGbABaGb` |
| 4 | `aGbAAGaGbAAGaGbAAG` | `aGbAAGaGbAAGaGbAAGaG` | `gAbaGGaGaGbABaGbaG` |
| 5 | `aGbAAGaGbAAGaGbAAG` | `aGbAAGaGbAAGaGbAAGbaG` | `GaGaGbABaGbbaG` |
| 6 | `AgABBgAbaBgAgAga` | `AgABBgAbaBgAgAgBaGbaG` | `gAbaGGaGaGbABaGbaG` |

The stored word is read by successive left actions.  If
\(W=w_1\cdots w_m\), define its ordinary left endpoint multiplier by
\[
\operatorname{ev}_L(W)=w_m\cdots w_1.
\tag{3.2}
\]
Thus
\(\operatorname{ev}_L(UV)=\operatorname{ev}_L(V)
\operatorname{ev}_L(U)\).

To transport an appended path, use the right deck action, not ordinary left
multiplication.  In a rooted component every vertex is uniquely \(ko\) with
\(k\in K\).  For \(h\in K\), define
\[
R_h(ko)=(kh)o.
\tag{3.3}
\]
An oriented edge \(ko\to zko\), with
\(z\in\{A^{\pm1},B^{\pm1},G^{\pm1}\}\), is sent to
\(kho\to zkho\).  Hence \(R_h\) preserves its label and orientation.  Via
the code's fixed bijection between oriented \(B/G/A\)-edges and the stored
slot-\(2/3/4\) basis coordinates, this defines linear operators
\(R_h^{(s)}\) on each stored edge-current slot.  Write
\[
[W]=R_{\operatorname{ev}_L(W)}
\tag{3.4}
\]
on vertices and use the corresponding \(R^{(s)}\) on slot \(s\).

Operator multiplication means composition, acting on the rightmost
argument first.  From (3.3),
\[
(R_h\circ R_k)(xo)=R_h((xk)o)=(xkh)o=R_{kh}(xo),
\]
so \(R_hR_k=R_{kh}\): the right factors are appended first \(k\), then
\(h\).  The needed instance is
\[
[U][V]
=R_{\operatorname{ev}_L(U)}\circ R_{\operatorname{ev}_L(V)}
=R_{\operatorname{ev}_L(V)\operatorname{ev}_L(U)}
=[UV].
\tag{3.5}
\]
The appended \(V\)-segment visits
\(v_r\cdots v_1\operatorname{ev}_L(U)o
=R_{\operatorname{ev}_L(U)}(v_r\cdots v_1o)\).  Therefore the exact
right-deck cocycle is
\[
[UV]=[U][V],\qquad
\mathsf E_s(UV)=\mathsf E_s(U)+[U]\mathsf E_s(V).
\tag{3.6}
\]
Free reduction does not change either side.  Define
\[
a_{\nu,ij}=[W^w_{\nu,i,j}],\qquad
x^s_{\nu,ij}=\mathsf E_s(W^w_{\nu,i,j}),\qquad
p_\nu=[P_\nu],\quad q_\nu=[Q_\nu].
\tag{3.7}
\]
Here \(a_{\nu,ij},p_\nu,q_\nu\) are right deck operators, not ordinary
left endpoint multipliers.  Applying (3.6) separately to
\(WQ_\nu^{-1}\), \(P_\nu WQ_\nu\), and \(P_\nu W\) gives
\[
\begin{aligned}
[WQ_\nu^{-1}]&=[W]q_\nu^{-1},&
\mathsf E_s(WQ_\nu^{-1})
 &=\mathsf E_s(W)+[W]\mathsf E_s(Q_\nu^{-1}),\\
[P_\nu WQ_\nu]&=p_\nu[W]q_\nu,&
\mathsf E_s(P_\nu WQ_\nu)
 &=\mathsf E_s(P_\nu)+p_\nu\mathsf E_s(W)
   +p_\nu[W]\mathsf E_s(Q_\nu),\\
[P_\nu W]&=p_\nu[W],&
\mathsf E_s(P_\nu W)
 &=\mathsf E_s(P_\nu)+p_\nu\mathsf E_s(W).
\end{aligned}
\tag{3.8}
\]
Using the three raw word identities in (2.9) of the companion memo now
gives all six one-step recurrences
\[
\boxed{
\begin{aligned}
a_{\nu,i,j+1}&=a_{\nu,ij}q_\nu^{-1},\\
x^s_{\nu,i,j+1}
 &=x^s_{\nu,ij}
   +a_{\nu,ij}\mathsf E_s(Q_\nu^{-1}),\\[2mm]
a_{\nu,i+1,j}&=p_\nu a_{\nu,ij}q_\nu,\\
x^s_{\nu,i+1,j}
 &=\mathsf E_s(P_\nu)+p_\nu x^s_{\nu,ij}
   +p_\nu a_{\nu,ij}\mathsf E_s(Q_\nu),\\[2mm]
a_{\nu,i+1,j+1}&=p_\nu a_{\nu,ij},\\
x^s_{\nu,i+1,j+1}
 &=\mathsf E_s(P_\nu)+p_\nu x^s_{\nu,ij}.
\end{aligned}}
\tag{3.9}
\]
These are identities of finite edge chains for every index.  They are not
patterns inferred from a bounded radius.

Equations (2.2), (2.4), and (3.9) are the exact recurrence for the five
input currents.  Notice that the fixed doubled anchor currents remain in
every \(D_{ij}\), although they cancel from a difference between adjacent
indices.

## 4. Full typed-AST unary evaluator

This section records the recurrence actually needed for the unary term.  It
is stronger than the occurrence-table mixed Hessian because it retains the
fixed and linear defects.

Represent a literal or AST node by its crossed class-two coordinate
\[
X=(q,a,A),
\tag{4.1}
\]
where \(q\in Q\), \(a\in V\), and \(A\in V\otimes V\).  All three
coordinates are integral until the final readout.

For a current \(f\), the positive canonical correction section is
\[
K(f)=(1,f,\sigma(f)),
\tag{4.2}
\]
with
\[
\sigma(f)=
\sum_x\binom{f_x}{2}e_x\otimes e_x
+\sum_{x<y}f_xf_y e_x\otimes e_y.
\tag{4.3}
\]
Thus tensor diagonals are present already at a correction leaf.

For a fixed quotient word \(q\) and module vertex \(x\), let
\(T_q(x)\) be the complete tensor coordinate of the literal word
\[
\widehat q\,r_x\,\widehat q^{-1}.
\tag{4.4}
\]
Its linear coordinate is \(e_{qx}\).  The difference between (4.4) and
pure tensor translation is the one-vertex transport defect.  Set
\[
\tau_q(b)=\sum_xb_xT_q(x).
\tag{4.5}
\]
Also let
\[
\Omega(q,r)=(1,o_{q,r},O_{q,r})
\tag{4.6}
\]
be the complete coordinate of the quotient-section defect
\[
\omega(q,r)=\widehat q\widehat r\widehat{qr}^{-1}.
\tag{4.7}
\]

If \(X=(q,a,A)\) and \(Y=(r,b,B)\), the exact product used by the
certificate is
\[
\boxed{
\begin{aligned}
X\star Y={}&(qr,c,C),\\
c={}&a+qb+o_{q,r},\\
C={}&A+qB+\tau_q(b)+a\otimes(qb)\\
 &\quad+O_{q,r}+(a+qb)\otimes o_{q,r}.
\end{aligned}}
\tag{4.8}
\]
The two terms containing \(o_{q,r},O_{q,r}\) are the fixed section defect;
\(\tau_q(b)\) is the full one-vertex transport term; and
\(a\otimes(qb)\) contains the fixed-base--direction products when one of
the factors is fixed.

The inverse is not formed by deleting those terms.  If
\(\Lambda(q^{-1})\) is the literal coordinate of the inverse canonical
quotient word, then
\[
\boxed{
\operatorname{Inv}(q,a,A)
=\Lambda(q^{-1})\star
  (1,-a,-A+a\otimes a).
}
\tag{4.9}
\]
A conjugation node is evaluated as
\[
\operatorname{Conj}(X,Y)=X\star Y\star\operatorname{Inv}(X),
\tag{4.10}
\]
with the AST's actual conjugator/payload order.  Product, inverse, literal,
and correction nodes using (4.2)--(4.10) are exactly the typed evaluator.

Let \(B=(B_0,\ldots,B_4)\) be the fixed tracked correction.  Evaluate the
fixed residual AST with correction leaves \(K(B_s+F_s)\), and write its
final coordinate as
\[
\mathcal R_B(F)=(1,0,M_B(F)).
\tag{4.11}
\]
For homogeneous \(F\), the final tensor is checked to be diagonal-free and
opposite-orientation antisymmetric before conversion to a wedge.  Let
\(\Pi\) denote that final wedge conversion followed by the fourteen finite
readouts and the full-wedge sum.  Then the exact unary matrix is
\[
\boxed{
U_{ij}=\Pi\bigl(M_B(D_{ij})-M_B(0)\bigr).
}
\tag{4.12}
\]
Equations (2.2)--(3.9) and (4.2)--(4.12) are a complete, radius-free
definition and recurrence for every entry of the requested matrix.  No
quotient-section or transport term has been inferred from the mixed Hessian
or discarded.

## 5. An exact scalar proof obligation on the integral lattice

All directions in this section are integral.  Define the three adjacent
increments by
\[
\begin{aligned}
\widetilde\Delta^j_{ij}&=D_{i,j+1}-D_{ij},\\
\widetilde\Delta^i_{ij}&=D_{i+1,j}-D_{ij},\\
\widetilde\Delta^\diag_{ij}&=D_{i+1,j+1}-D_{ij}.
\end{aligned}
\tag{5.1}
\]
Each is homogeneous because it is the difference of two integral
homogeneous directions.  The fixed doubled anchor cancels from these
differences, but it remains present in each \(D_{ij}\) evaluated by (4.12).

The right-deck path recurrence (3.9) gives the exact five components of the
\(j\)-increment:
\[
\boxed{
\begin{aligned}
\widetilde\Delta^j_{ij,0}
 &=e_{y_{i,j+1}}-e_{y_{ij}},\\
\widetilde\Delta^j_{ij,1}&=0,\\
\widetilde\Delta^j_{ij,s}
 &=\sum_{\nu=1}^6\epsilon_\nu
   a_{\nu,ij}\mathsf E_s(Q_\nu^{-1}),
   \qquad s=2,3,4.
\end{aligned}}
\tag{5.2}
\]
Here every sign is retained, and \(a_{\nu,ij}\) is the right deck operator
defined in (3.4).

The other two integral increments are
\[
\boxed{
\begin{aligned}
\widetilde\Delta^i_{ij,0}
 &=e_{y_{i+1,j}}-e_{y_{ij}},\\
\widetilde\Delta^i_{ij,1}&=0,\\
\widetilde\Delta^i_{ij,s}
 &=\sum_{\nu=1}^6\epsilon_\nu\bigl(
 \mathsf E_s(P_\nu)+p_\nu x^s_{\nu,ij}
 +p_\nu a_{\nu,ij}\mathsf E_s(Q_\nu)
 -x^s_{\nu,ij}
 \bigr),\\[1mm]
\widetilde\Delta^\diag_{ij,0}
 &=e_{y_{i+1,j+1}}-e_{y_{ij}},\\
\widetilde\Delta^\diag_{ij,1}&=0,\\
\widetilde\Delta^\diag_{ij,s}
 &=\sum_{\nu=1}^6\epsilon_\nu\bigl(
 \mathsf E_s(P_\nu)+p_\nu x^s_{\nu,ij}
 -x^s_{\nu,ij}
 \bigr),
\qquad s=2,3,4.
\end{aligned}}
\tag{5.3}
\]

For an integral homogeneous direction \(F\), define
\[
u_\infty(F)=
\Pi_\infty\bigl(M_B(F)-M_B(0)\bigr)\in\mathbb F_2.
\tag{5.4}
\]
The corrected residual has zero linear coordinate, so its class-two tensor
is the degree-two Magnus coordinate of a word in the commutator subgroup of
the free relation-kernel group.  Modulo degree three that subgroup is
generated by commutators, and
\([r_x,r_y]\) has tensor
\(e_x\otimes e_y-e_y\otimes e_x\).  Hence the final tensor is a sum of
opposite-orientation pairs and has zero diagonal before
`_residual_tensor_to_wedge` is called, exactly as that function's
precondition requires.  Internal diagonals from (4.3), transport, and
section multiplication have been carried through the AST and cancel in the
final residual tensor; the wedge reader does not perform that cancellation.

On the integral homogeneous lattice, the affine-quadratic AST theorem gives
\[
u_\infty(F+G)
=u_\infty(F)+u_\infty(G)+\beta_\infty(F,G)
\tag{5.5}
\]
for integral homogeneous \(F,G\).  Take
\(F=D_{ij}\) and
\(G=\widetilde\Delta^j_{ij}=D_{i,j+1}-D_{ij}\).  Then \(F+G=D_{i,j+1}\),
so (5.5) proves the exact increment identity (1.3).  The substitutions with
\(\widetilde\Delta^i\) and \(\widetilde\Delta^\diag\) are typed in the same
way.  No coefficientwise mod-two representative is supplied to the AST.

The mixed term in (5.5) is the fixed sixteen-internal/120-external formula.
In contrast, \(u_\infty(\widetilde\Delta)\) is evaluated by the full
base-dependent recurrence (4.8); it contains the fixed base products,
\(\tau\)-terms, and \(\Omega\)-terms.  Replacing it by the normalized mixed
kernel would be the invalid unary cancellation warned about in the
preflight.

The bounded replay suggests the candidate identity
\[
u_{ij}=\delta_{ij}.
\tag{5.6}
\]
An exact scalar proof obligation for its \(j\)-increments is
\[
\boxed{
u_\infty(\widetilde\Delta^j_{ij})
+\beta_\infty(D_{ij},\widetilde\Delta^j_{ij})
=\delta_{i,j+1}+\delta_{ij}
\quad(i,j\ge0).
}
\tag{5.7}
\]
The analogous \(i\)-increment obligation and the seed \(u_{00}=1\) would
prove (5.6).  The raw recurrence expresses each direction in (5.7) using the
fixed \(P_\nu,C_\nu,Q_\nu\) blocks, but the first term still invokes the
complete base-dependent unary evaluator.  Thus (5.7) is an evaluator-level
polarization obligation, not a closed recurrence of smaller proved
complexity.  No minimality claim is made.

## 6. One bounded replay

Exactly one constant-size replay was run.  It used the symbolic typed AST,
the exact integral `anchored_direction`, and the base subtraction in
(4.12).  The ten cells are the representatives of
\((\operatorname{cmp}(i,j),i\bmod2,j\bmod2)\); they were chosen before
evaluation.  The base syndrome was
\[
S(0)=\texttt{111010110101011}.
\tag{6.1}
\]
The complete unary vectors were

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

The final bit is one in the two diagonal cells and zero in all eight open
cells, giving (1.4) on this fixed set.  The other fourteen coordinates are
not functions of just equality versus inequality on these representatives.

This table checks the raw substitution and shows that an identity-matrix
unary witness is plausible.  It does not prove that a cell type is invariant
under increasing either exponent by two.  No such invariance was assumed in
Sections 2--5.

## 7. Rank and Andrews--Curtis boundary

### Proved algebra

- the all-index raw group identity (1.1), with canonicalization only after
  the complete product;
- the exact integral anchored currents (2.2)--(2.4);
- the six all-index edge-current recurrences (3.9), using the explicit right
  deck action (3.3)--(3.6);
- the complete base-dependent crossed-coordinate recurrence (4.8)--(4.12),
  retaining quotient-section, one-vertex transport, base--direction, and
  internal tensor-diagonal terms through their cancellation in the final
  residual before wedge conversion; and
- the exact final-scalar increment identity (1.3)/(5.5).

### Bounded evidence only

- the ten unary vectors in Section 6; and
- the identity pattern of their final coordinates.

### Not proved

- (5.6) for all indices;
- a finite-state or finite-index-periodicity theorem for the complete unary
  matrix;
- finite or infinite diagonal-left rank of the complete
  validity-plus-syndrome function; and
- a period-two lift, stable Andrews--Curtis, or Andrews--Curtis conclusion.

If (5.6) is later proved, adding the row-only term \(U(H(h_jv))\) changes
the matrix by rank at most one, so the complete unary contribution still
has unbounded rank.  That would obstruct a finite linear diagonal-left
state for this function.  It would not by itself prove either stable
Andrews--Curtis or Andrews--Curtis.

## Fix round 1

Proof status: all three referee findings have been repaired in the exact
algebra above; the all-index delta identity remains an explicit open proof
obligation.

1. **Successive-left path convention.**  Section 3 now distinguishes the
   ordinary anti-homomorphic endpoint multiplier
   \(\operatorname{ev}_L\) from the right deck operator \(R_h\).  The
   action of \(R_h\) is defined on component vertices and on each oriented
   \(B/G/A\)-edge basis, (3.5)--(3.6) prove the operator concatenation law,
   and (3.8) rederives every endpoint and current line in (3.9).  Equations
   (5.2)--(5.3) use those right deck operators.
2. **Integral typing.**  Section 5 now uses only the integral homogeneous
   differences
   \(D_{i,j+1}-D_{ij}\), \(D_{i+1,j}-D_{ij}\), and
   \(D_{i+1,j+1}-D_{ij}\), with all \(\epsilon_\nu\)-signs retained.
   The parity shadow (2.5) is not passed to the AST.  Internal diagonals are
   propagated, and the final commutator tensor is shown to be diagonal-free
   before the implementation's wedge reader.
3. **No minimality claim.**  Section 5 calls (5.7) an exact scalar proof
   obligation and states explicitly that it still invokes the complete
   unary evaluator and is not a smaller closed recurrence.

Bounded evidence: no additional replay, grid, census, or search was run in
this fix round.  The single ten-cell replay in Section 6 is unchanged: its
last unary bit is one at \((0,0),(1,1)\) and zero at the eight off-diagonal
representatives.  It remains bounded evidence only.
