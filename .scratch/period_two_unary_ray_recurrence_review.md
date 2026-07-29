# Hostile referee review: period-two unary ray recurrence

Date: 2026-07-29

## Verdict

**REFUTED as written.**  This verdict concerns the claim that the displayed
formulas already constitute an exact, typed recurrence.  The bounded unary
values are correct, and the crossed AST formulas agree with the implementation.
The failure is at the interface between the left-action path implementation,
the path cocycle used to derive all current increments, and the unproved
passage from integral homogeneous directions to mod-two current classes.

## Findings

### 1. The path cocycle (3.2), hence every displayed current increment, uses the wrong action unless an unstated right deck action is substituted

`build_l0_direction_from_pairs` advances a path letter by

```python
target = escape.act(generators[name], current)
```

and `escape.act(k, x)` is `c_vertex(quotient_multiply(k, x))`.  Path letters
therefore act successively on the **left**.  If

\[
\operatorname{ev}_L(w_1\cdots w_m)=w_m\cdots w_1
\]

denotes the endpoint multiplier used by that loop, then the exact literal
concatenation law is

\[
\operatorname{ev}_L(UV)=\operatorname{ev}_L(V)\operatorname{ev}_L(U),
\]

not the memo's `[UV]=[U][V]` for ordinary endpoint group elements.

An exact two-letter counterexample is `U=A`, `V=B`.  Starting at a component
root, the implementation visits `A root` and then `B A root`; the ordinary
left endpoint action `[A][B]` gives `A B root`.  The two vertices are distinct
in the free `A,B,G` tree.  This is the same reversal for which the companion
factorization explicitly introduced `Theta = rev(kappa)`.

Consequently (3.4), (5.2), and (5.3) do not follow from the stated meaning of
`[W]`.  They become correct only if `[W]` is redefined to mean the **right
deck-translation operator** `R_evL(W)` on rooted tree coordinates, with
`[W] E(V)` defined by that right translation.  Under that operator convention,
operator composition reverses the underlying endpoint multipliers and the
displayed algebra can be recovered.  The memo neither defines this operator
nor gives its action on the stored `B/G/A` currents.

Smallest repair: replace "endpoint action" by an explicit definition of the
right deck action on vertices and each of the three stored edge-current slots;
prove `[UV]=[U][V]` in that operator convention; then rederive all six lines of
(3.4) and all components of (5.2)--(5.3).  If `[W]` is intended to remain the
ordinary left endpoint multiplier, reverse every product and use the
corresponding right-translation transport formulas instead.

### 2. The step from integral directions to (5.5) is not typed, and the implementation does not kill diagonal tensors at wedge conversion

Sections 2 and 4 define `M_B(F)` using integral canonical sections.  Section 5
then substitutes the mod-two classes `Dbar_ij` and `Delta_ij` into the same
notation.  No integral homogeneous lift is selected, and no theorem is proved
there that `M_B` or `u_infinity` descends to those classes.

The obstruction is real at the coordinate level.  For a single vertex `x`,

\[
\sigma(2e_x)=e_x\otimes e_x,
\qquad
\sigma(0)=0,
\]

although `2e_x = 0` modulo two.  Thus replacing an integral direction by its
coefficientwise mod-two representative changes the AST tensor.  One must
prove, not assume, that the resulting diagonal increments stay in an invariant
subspace and become invisible in the final syndrome.

The claimed implementation match is also misstated.  The actual wedge reader
at `_residual_tensor_to_wedge` does **not** quotient out or "kill" a diagonal:
it asserts `all(left != right for left, right in tensor)` and aborts if any
diagonal remains.  Therefore lines 122--128 cannot themselves justify the
substitution in line 357.  For the family, the only automatically homogeneous
increment is the integral difference

\[
\widetilde\Delta^j_{ij}=D_{i,j+1}-D_{ij},
\]

not an arbitrary `0/1` representative of its mod-two class.

Smallest repair: keep (5.5) on the integral homogeneous lattice and use
`F=D_ij`, `G=D_i,j+1-D_ij`.  Alternatively, define `u_infinity([F])` using an
integral homogeneous lift and add a gate-by-gate proof that changing the lift
by twice a homogeneous direction leaves every final bit unchanged.  That proof
must finish by showing the residual diagonal cancels **before** the implemented
wedge reader, or by defining a separate mathematical exterior projection and
proving it agrees with the certificate on admissible inputs.

### 3. "Smallest surviving scalar recurrence" is not established; (5.7) is an evaluator-level polarization restatement

Even after Findings 1--2 are repaired, (1.3)/(5.7) still contains
`u_infinity(Delta)`, which the memo says must be evaluated by the full
base-dependent typed AST with all transport and section defects.  No state-size,
term-count, or logical partial order is defined under which this is the
"smallest" remaining recurrence.  The formula is the universal polarization
identity applied to one increment; it does not reduce the unary evaluator to a
strictly smaller closed recurrence.

There is also no unique scalar obligation: the integral `j` increment, the
integral `i` increment, and the diagonal increment give equally exact
polarization identities once their domains are repaired.  The seed plus both
axis identities would prove the candidate delta pattern, but this does not make
(5.7) minimal.

Smallest repair: rename (1.3)/(5.7) "an exact scalar proof obligation after
choosing integral homogeneous increments" and delete "smallest" unless a
precise complexity/minimality criterion and proof are supplied.

## Audits that passed

1. **Raw `p=tc` and `y_ij`.**  Forming `p` as the raw two-letter word, forming
   the entire product, and only then applying `c_vertex` gives
   `h_j w_i = p^-1 g^(n_i-n_j) c g^(-(n_i-2)) t`.  Since
   `n_i-n_j=3(i-j)` and `n_i-2=3(i+1)`, (1.1) is exact.  Passing `p=tc`
   through `parse_quotient` separately would delete its terminal `c`; the memo
   correctly forbids that operation.
2. **Integral anchor signs.**  The implementation uses
   `e_y - source_scalar(y)e_T`.  The replay confirmed
   `source_scalar(y_ij)=-2`, so slot zero is exactly `e_y+2e_T`, slot one is
   zero, and linearity gives the `+2 A_s` sign in (2.4).
3. **Crossed AST convention.**  `_coordinate_product` composes, in order, the
   left kernel coordinate, the transported right coordinate, and `omega`.
   Expanding `_kernel_product` gives exactly (4.8): `qB`, the complete
   one-vertex `tau_q(b)`, `a tensor qb`, `O_qr`, and
   `(a+qb) tensor o_qr`, each once.  `_coordinate_inverse` gives (4.9), and
   `_evaluate_ast_coordinate` uses the stated conjugator/payload order.  No
   transport or quotient-section defect is missing or double-counted.
4. **Ten complete unary vectors.**  One fixed ten-cell replay used the raw
   product for `y_ij`, `tree.anchored_direction`, and
   `hessian.symbolic_syndrome`.  It reproduced `S(0)=111010110101011` and all
   ten vectors in Section 6 exactly.  Every replayed vertex had source scalar
   `-2`; every integral direction had slot zero `e_y+2e_T`, slot one zero, and
   exact zero correction image.  The final bit was one precisely at `(0,0)`
   and `(1,1)`.  This verifies the stated bounded evidence, not an all-index
   delta identity.

## Referee conclusion

The raw ray, anchor, typed AST, defect accounting, inverse, and ten bounded
outputs survive audit.  The memo nevertheless cannot claim an exact all-index
recurrence until it reconciles the path recurrence with the implementation's
left-action convention and supplies a well-typed integral-to-mod-two descent.
After those repairs, (5.7) should be presented as a surviving polarization
obligation, not as a proved minimal recurrence.

## Re-review round 1

**Verdict: APPROVE.**  All three original findings are addressed.  This
round used textual/algebraic review only; no replay, grid, census, or broad
computation was run.

1. **Finding 1 — ADDRESSED.**  Revised Section 3 explicitly distinguishes
   the anti-homomorphic ordinary endpoint multiplier
   `ev_L(UV) = ev_L(V)ev_L(U)` from the right deck operator
   `R_h(ko) = (kh)o`.  It defines the latter on oriented edges and hence on
   each stored slot-2/3/4 current, fixes the operator-composition convention,
   proves `[UV]=[U][V]`, and rederives each endpoint/current line in (3.8)--
   (3.9).  The signed integral increments (5.2)--(5.3) follow from those
   rederived recurrences.  The original `A,B` reversal counterexample no
   longer applies because `[W]` is no longer identified with the ordinary
   left endpoint multiplier.
2. **Finding 2 — ADDRESSED.**  Revised Section 5 uses only the integral
   homogeneous differences `D(i,j+1)-D(i,j)`, `D(i+1,j)-D(i,j)`, and
   `D(i+1,j+1)-D(i,j)`; it retains every `epsilon_nu` sign and never passes
   the parity shadow (2.5) to the AST.  It also correctly places diagonal
   cancellation before `_residual_tensor_to_wedge`: zero relation-module
   coordinate puts the residual in the commutator subgroup of the free
   relation-kernel group, whose degree-two tensor is a sum of antisymmetric
   commutator tensors and therefore has zero diagonal.  Equation (5.5) is
   now applied to typed integral homogeneous inputs with
   `F+G=D(i,j+1)`.
3. **Finding 3 — ADDRESSED.**  The revised memo calls (5.7) an exact scalar
   proof obligation, explicitly says that it still invokes the complete
   unary evaluator, and disclaims both a smaller closed recurrence and any
   minimality claim.

**Open findings: none within the scoped fixes.**  The all-index identity
`u_ij = delta_ij` remains explicitly unproved, as it should; the unchanged
ten-cell table remains bounded evidence only.
