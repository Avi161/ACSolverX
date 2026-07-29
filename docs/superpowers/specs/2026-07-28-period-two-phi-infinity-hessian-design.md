# Period-Two Phi-Infinity Hessian Design

## Goal

Derive the exact crossed Fox--Magnus Hessian of the fixed period-two
`corrected_residual` circuit without expanding its long free words, pull that
formula back to the anchored tree-flow directions, and use the resulting
kernel to attack the remaining finite-state alternative:

1. prove finite-index periodicity of the validity-plus-syndrome function and
   construct a reversible finite state; or
2. exhibit an explicit infinite diagonal-left Hankel-rank family inside the
   actual anchored $L_0$ image.

The first deliverable is the exact coefficient theorem and replayable
certificate.  It is an intermediate theorem, not a substitute for the rank
decision and not a claim about the period-two lift, stable AC, or AC.

## Why this is the next theorem

The tree-flow theorem reduces every balanced two-source direction modulo two
to

\[
H(v)+H(w),
\]

and proves that the final fifteen-bit syndrome is affine quadratic with
alternating polarization.  Ambient exact-equality and shortlex-inversion
kernels have infinite rank, but that does not decide their pullback through
the coupled five-slot map $H$.  Conversely, static endpoint automata do not
give a diagonal-left Markov state because repeated cancellation is a stack
pop.  The missing datum is the exact coefficient with which each primitive
kernel survives the fixed recurrence.

No new depth census can supply that datum.  The fixed word circuit can.

## Exact circuit representation

Represent the residual by a typed AST with fixed literal leaves, five
canonical correction leaves, products, inverses, and conjugations.  Expand
only the AST nodes, never the fixed source words.  A correction occurrence is
a record

```text
(slot, polarity, quotient_prefix)
```

where the prefix is the exact canonical $Q=C_2*\mathbb Z$ word before the
occurrence.  The complete residual has sixteen records with slot counts

```text
(6, 4, 2, 2, 2).
```

Their signed prefix sums must equal the five tracked `build_operators`
group-ring values exactly, including coefficients.  On the anchored $L_0$
family slot one is zero, leaving twelve active occurrences.

The occurrence list must be produced in two independent ways:

- generic AST traversal; and
- a pinned literal table reviewed against the exact recurrence.

Agreement is the structural guard against a missing inverse, wrong prefix,
or silent quotient normalization.

The same typed AST must also evaluate the complete crossed class-two
coordinate of the fixed base plus one direction.  Fixed literal leaves carry
their exact quotient, linear, and raw tensor coordinates; correction leaves
carry the full canonical-section coordinate, not only its mixed Hessian.
This supplies the base and unary functions needed by the diagonal-left rank
gate without constructing the long residual word.

## Crossed class-two jets

For finitely supported currents $D,E$, the positive canonical shortlex leaf
has mixed raw tensor

\[
\Gamma_+(D,E)=
\sum_{x<y}(D_xE_y+E_xD_y)e_x\otimes e_y
+\sum_xD_xE_xe_x\otimes e_x.
\]

The inverse leaf is not the same jet:

\[
\Gamma_-(D,E)=
-\Gamma_+(D,E)+D\otimes E+E\otimes D.
\]

If the sixteen occurrence records are
$((i_a,\varepsilon_a,p_a))_{a=1}^{16}$, the exact mixed tensor is

\[
\begin{aligned}
\mu_R^{DE}
={}&\sum_a p_a\Gamma_{\varepsilon_a}(D_{i_a},E_{i_a})\\
&+\sum_{a<b}\varepsilon_a\varepsilon_b
\bigl[(p_aD_{i_a})\otimes(p_bE_{i_b})
+(p_aE_{i_a})\otimes(p_bD_{i_b})\bigr].
\end{aligned}
\tag{H}
\]

Thus the exact table consists of sixteen internal terms and 120 external
terms.  It must be generated from the crossed product/inverse rules rather
than copied as 136 hand-written coefficients.

## Section defects and tensor diagonals

Literal words in $F(c,t)$ remain literal through the AST.  If an evaluator
normalizes a quotient prefix, it must carry the nonmultiplicative section
defect

\[
\omega(g,h)=\widehat g\widehat h\widehat{gh}^{-1}.
\]

Fixed section defects and one-vertex transport defects are constant or unary
in a four-corner mixed difference, so they do not enter (H).  They remain in
the constant and unary syndrome functions and may not be discarded there.

Likewise, a period-two diagonal increment is propagated, not cancelled.  If
a conjugator changes by $\delta$ and the payload quotient is $q$, the tensor
change is $\delta+q\delta$.  The tensor-diagonal subspace is $Q$-stable, so
the full recurrence preserves it and only final exterior projection kills
it.

## Final readout and kernel normal form

For a final zero-linear tensor $M$, define

\[
\Theta(M)=\sum_{x<y}M_{x,y}\pmod2.
\]

The full-wedge Hessian is $\Theta(\mu_R^{DE})$.  Normalize every translated
module vertex before comparing tensor keys.  Expose five subtotals:

1. positive internal section terms;
2. negative internal section terms;
3. external ordered-pair terms;
4. paired orientations rewritten as
   \[
   \operatorname{LT}(\alpha,\beta)+
   \operatorname{LT}(\beta,\alpha)
   =\varepsilon(\alpha)\varepsilon(\beta)+
   \langle\alpha,\beta\rangle;
   \]
5. propagated tensor-diagonal terms killed at final exterior projection.

The remaining unpaired oriented terms are explicit shortlex-order kernels.
The normal form must be deterministic and carry a digest, but the digest is
evidence for the finite table only, not a theorem about all sources.

Tensor-to-wedge conversion is defined only after checking the actual
homogeneity contract.  Both input directions must have zero correction image.
The final mixed tensor must have zero diagonal and opposite-orientation
antisymmetry over the integers before it is converted to a wedge.  A helper
that accepts arbitrary module variables and silently takes their upper
triangle is invalid.

## Complete diagonal-left function

The Hessian alone cannot decide the rank of the actual function.  The
symbolic AST evaluator must also expose

\[
C= S(0),\qquad U(D)=S(D)+S(0),
\]

including fixed sources, the base correction, base--direction products,
one-vertex transport defects, and quotient-section defects.  It must compute
all fourteen finite-action bits as pushforwards of the same exact symbolic
wedge, followed by $\Phi_\infty$.

For a signed source pair $p=(v,w,\epsilon)$ define

\[
F(p)=
\begin{cases}
(1,S(D(e_v+\epsilon e_w))),&L_0(e_v+\epsilon e_w)
\text{ is component-balanced},\\
(0,0^{15}),&\text{otherwise}.
\end{cases}
\]

The certificate must provide $F(gp)$ for an exact diagonal-left context
$g\in Q$.  A finite-branch certificate records a common finite quotient and
its reversible transitions.  An infinite-branch certificate records sources,
contexts, the selected validity/syndrome coordinate, the exact Hankel matrix,
and its symbolic rank proof.  No branch may ignore $C$, $U$, or the validity
bit.

## Independent raw-tensor oracle

The existing `degree_two` helper deliberately discards diagonal and lower-
triangular entries, so it cannot detect premature diagonal deletion.  Add an
independent direct oracle that streams a literal kernel word and returns its
complete raw degree-two tensor before exterior projection.  The oracle may
expand the residual only in bounded tests/certificate construction; the
symbolic path may not call it.

Pin a nontrivial-payload fixture.  The oracle must retain the complete integer
raw tensor.  For a doubled canonical lift with mod-two diagonal increment
$\delta=e_x\otimes e_x$ and a literal payload of quotient $q\ne1$, the
quotient-trivial commutator word's raw tensor must reduce modulo two exactly to

\[
\delta+q\delta.
\]

Choose $x$ so $qx\ne x$, record the complete integer tensor and the two
surviving mod-two diagonal labels, assert the mod-two tensor is nonzero, and
assert its mod-two exterior wedge is zero.  Even integral linear/off-diagonal
terms are retained by the oracle and vanish only in this stated reduction.
This fixture fails if a diagonal is deleted at the conjugation gate even
though every wedge/bit test would still pass.

## Anchored pullback

Substitute the exact tree-flow direction

\[
H(v)=D(e_v-\lambda(v)e_T).
\]

Its active slots are zero, two, three, and four.  Slot zero is the anchored
source atom; slots two, three, and four are the unique finite forest current.
The pulled-back cross kernel is

\[
\beta_\infty(v,w)=
\Theta\bigl(\mu_R^{H(v),H(w)}\bigr).
\]

The coefficient theorem must turn this into a finite sum of exact equality
and shortlex-order pairings of translated source atoms and endpoint-defined
tree currents.  Do not infer a Markov state from static recognizability.

## Rank-decision gate

Use the normalized pulled-back formula to pursue both sides of one exact
alternative.

### Finite branch

Prove that every unary and cross term is invariant under one common
finite-index normal subgroup $N\triangleleft Q$.  Record the finite quotient,
give reversible matrices/permutations for `c,t,T`, verify

```text
c*c = 1, t*T = 1, T*t = 1,
```

and replay all tracked syndrome fixtures.  Ordinary forward automata or
regular relations are insufficient.

### Infinite-rank branch

Give actual balanced anchored sources $p_i$ and diagonal-left contexts $g_j$
for which one syndrome coordinate has an identity or unbounded-rank Hankel
submatrix.  Prove that all other coefficient-table terms cancel on the
family.  Ambient singleton-current rank witnesses do not count unless they
are realized inside $H(v)$ and the complete five-slot Hessian.

If neither branch is proved after the exact table is available, the honest
output is the fully explicit uncancelled kernel and its smallest remaining
symbolic identity.  The proof loop then continues from that identity; a
bounded scan is not an alternative.

## Certificate interface

Create
`experiments/stable_ac/depth4_period_two_phi_infinity_hessian_certificate.py`
and a focused test.  The module should expose narrow pure interfaces:

```python
residual_occurrences() -> tuple[Occurrence, ...]
occurrence_operator(slot) -> lift.GroupRing
gamma_positive(left, right) -> Tensor
gamma_negative(left, right) -> Tensor
raw_tensor_from_kernel_word(word) -> Tensor  # direct oracle only
symbolic_residual_tensor(direction) -> Tensor
symbolic_unary_tensor(direction) -> Tensor
symbolic_syndrome(direction) -> tuple[int, ...]
symbolic_mixed_tensor(left, right) -> Tensor  # homogeneous inputs required
symbolic_mixed_wedge(left, right) -> WedgeVector  # asserts alternation
phi_infinity_hessian(left, right) -> int  # homogeneous inputs required
anchored_pair_value(left, right, epsilon) -> tuple[int, tuple[int, ...]]
diagonal_left_pair_value(context, left, right, epsilon) -> tuple[int, tuple[int, ...]]
kernel_normal_form() -> KernelNormalForm
phi_infinity_hessian_certificate() -> Certificate
```

The direct four-corner oracle may call the existing residual pipeline and the
new independent raw-tensor streamer in tests/certificate construction.  The
symbolic evaluator itself must not build the long residual word.

## Verification

Tests must independently establish:

1. exact sixteen-row table, slot counts, and quotient itinerary;
2. signed prefix sums equal all five tracked operators;
3. polarity-sensitive $\Gamma_+$/$\Gamma_-$ fixtures fail if inverse jets
   are conflated;
4. the independent raw commutator fixture retains its complete integer
   tensor, whose mod-two reduction has nonzero diagonal support exactly
   $\delta+q\delta$ and zero exterior image;
5. the symbolic mixed raw tensor equals the independent direct four-corner
   raw tensor on the existing `ALTERNATE_10`/`ALTERNATE_01` square;
6. nonhomogeneous inputs are rejected, while homogeneous mixed tensors have
   zero diagonal and exact opposite-orientation antisymmetry before wedge
   conversion;
7. symbolic base, unary, and all fifteen syndrome bits match the direct
   oracle on independent fixtures;
8. the exact `Phi_infinity` bit matches near-survivor cross and
   three-direction biadditivity fixtures;
9. self-polarization vanishes on the tracked anchored and homogeneous
   fixtures;
10. equality/order/diagonal subtotals xor to the direct result;
11. validity and diagonal-left pair evaluation agree with direct source-flow
    construction on balanced and unbalanced examples;
12. no symbolic path imports `.scratch` or expands the long residual word;
13. existing tree-flow/source/census tests remain green; and
14. every broad conclusion is proved abstractly rather than inferred from
    bounded fixtures.

## Documentation boundary

Create a proof note for (H) and update the tree-flow proof, handoff, and direct
theory ledger.  State separately:

- the exact Hessian theorem;
- the normalized anchored kernel;
- the result, if any, of the finite-versus-infinite rank gate; and
- the remaining consequence for the period-two lift.

Do not claim AC or stable AC from a degree-two obstruction alone.
