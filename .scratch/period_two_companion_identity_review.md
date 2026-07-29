# Hostile referee review: period-two companion identity

Date: 2026-07-29

## Verdict

**REFUTED.**  This verdict is about the claimed proof, not an assertion that
the displayed identity is false.  The bounded values I replayed are
consistent with the identity.  The memo nevertheless does not prove the
load-bearing all-index comparison lemma, and it gives still less proof for
the second and third families.

## Load-bearing findings

### 1. The comparison argument omits the certificate's mandatory `c_vertex` normalization

The certificate does not order raw elements of `Q`.  It orders canonical
module vertices.  In
`depth4_period_two_phi_infinity_hessian_certificate.py`, `_shortlex_key`
first calls `lift.c_vertex`; `_polarized_inversion` canonicalizes every
multiplier translate; and `_action` canonicalizes occurrence translates.
The map `c_vertex` is not a group homomorphism: after quotient reduction it
deletes a terminal `c`.

This operation is active on the claimed family, not a harmless convention.
At the authoritative raw-group point `(i,j)=(3,0)`, an exact current replay
finds, for active occurrence 4 in slot 2,

- on the left, `cT -> ctcTcTc -> ctcTcT` after translation and
  canonicalization;
- on the right, `cTct -> ctcTc -> ctcT`.

Section 4 instead argues with translated copies of free `A,B,G`-path
blocks and says that fixed-multiplier translation leaves the paired
shortlex comparisons in cancelling pairs.  It never inserts or classifies
the intervening `c_vertex` operation.  Consequently raw free-word prefix
cancellation does not imply the comparison identities used by the exact
kernel.  The primitive diagonal calculation in the earlier memo also
demonstrates that left multiplication can reverse shortlex order, so no
unspoken left-invariance principle is available.

Smallest repair: formulate every old/new block vertex as
`c_vertex(action * vertex)` and prove a finite normal-form lemma covering
terminal-`c` deletion and boundary cancellation for every one of the 12
occurrence actions and six inversion multipliers.  A checked symbolic
transition table with its generator would also suffice.  Raw path words
alone do not.

### 2. The ten-cell lemma assumes the all-index statement it is meant to prove

The table is an exact table for ten representatives.  It is not a proof
that each equality, inversion, and external kernel depends only on

\[
(\operatorname{cmp}(i,j), i\bmod2, j\bmod2).
\]

The only proposed induction is the paragraph saying that two inserted
copies have the same comparisons against every old block and that the
new-new comparisons occur twice.  Neither assertion is derived from
(2.10).  The two copies occur at different translated vertices, old
suffixes are translated when a block is inserted, shortlex is not
translation-invariant, and the canonicalization issue in Finding 1 can
change lengths.  Equality cancellation of identical mod-two edge chains
does not establish cancellation of the bilinear order predicates between
those chains and all pre-existing chains.

Thus the leap from the ten finite cells to (4.3), (5.1), the five companion
rows of (5.3), and finally `R_ij = delta_ij` is circular: the table
checks the boundary values only after the unproved two-step invariance has
been declared.

Smallest repair: for every kernel `K`, derive exact difference identities

\[
K(i+2,j)+K(i,j)=0,\qquad K(i,j+2)+K(i,j)=0
\]

inside each open region, with separate diagonal-crossing boundary formulas.
The derivation must expand all old-new and new-new pairs after occurrence
translation and `c_vertex`, not merely state that they are doubled.  Once
those identities are proved, the ten representatives become a valid base
case.

### 3. The second and third universal cancellations have no auditable proof data

Section 6 displays only five aggregate ten-bit signatures for each family.
It does not display the six roots and right-`c` choices, the six triples
`(P_nu,C_nu,Q_nu)`, the individual four equality signatures, the six
inversion signatures, or the 66 external signatures.  This omission is
material: row 2 already has a different fixed middle power
`g^(-(n_0-2)) = g^-2`, so “identical in form” does not identify the actual
boundary words whose shortlex behavior must be proved.

The earlier anchored-ray memo explicitly says that even the all-index
primitive identity proof for these two candidates “has not been carried
through.”  The companion memo supplies neither those three length cases nor
a replacement proof.  Ten-cell aggregate agreement cannot establish the
primitive identity, individual-kernel periodicity, or universal
cancellation.

Smallest repair: provide, for each family, the full raw-to-canonical endpoint
factorization, all fixed blocks, an all-index primitive proof, and either the
76 individual signatures plus the repaired two-step lemma or a reproducible
symbolic certificate producing them.  Aggregate signatures alone are not
checkable evidence.

### 4. The memo treats recorded proof-conclusion flags as executable all-index certificates

The subgroup code structurally builds a complete folded core and the
anti-homomorphism is plausible, but the executable certificate's explicit
round-trip audit is bounded to 127 depth-six canonical vertices.
`depth4_period_two_tree_flow_factorization_certificate.py` is even more
explicit: its module docstring says that `proof_conclusion_*` fields record
conclusions of accompanying abstract arguments and that the executable
fixtures alone are not proofs.  The booleans asserting injectivity, Cayley
trees, and unique finite flow are assigned as conclusions, not proved by
their truth values.

For the first family, the displayed factorization could close this gap by
a short exact algebraic proof, but the memo does not show the evaluations
of all `(X_nu,D_nu,Z_nu)` to the displayed `(P_nu,C_nu,Q_nu)`, nor a
formal basis-inverse argument establishing that `rewrite_k` is the required
homomorphism on arbitrary powers.  For rows 2 and 3, even the fixed words
are absent.

Smallest repair: cite and restate the finite Stallings/Nielsen argument that
makes `rewrite_k` an exact inverse-coordinate homomorphism, then display the
18 generator evaluations per family.  This is a finite algebraic repair;
no radius search is needed.

## Bounded evidence audit

The following checks passed and therefore are not counterexamples to the
identity:

1. At the exact raw-group point `(3,0)`, the authoritative tuple is
   reproduced exactly:
   equality `(1,1,1,1)`, inversion `(0,0,0,0,1,0)`, external xor `1`,
   total `0`.
2. The family words were formed as raw `Q` products and only then passed
   through `c_vertex` for module-current evaluation.  All six `v`-paths
   and all six `w`-paths matched (2.5) and (2.8) at each
   of `(5,0)` and `(0,5)`.  This supports the anti-homomorphism and the
   displayed first-family fixed-block recurrence.
3. For the ten representative cells in the stated column order, the exact
   first-family replay gave equality signatures
   `1111111111`, `0011010011`, `0011010011`, `1111111111`; inversion
   signatures `0000110000`, `0000000000`, `0000000000`, `0000000000`,
   `1010011010`, `0000000000`; and aggregate signatures
   `E=0000000000`, `I=1010101010`, `O=1010101010`.
4. The displayed external table covers each of the 66 unordered active
   occurrence pairs exactly once.  Pair-by-pair comparison against all ten
   exact representative evaluations found zero signature mismatches, and
   xoring all 66 rows gives `1010101010`.
5. Limited same-cell two-step probes also passed termwise, including
   `(1,0)` versus `(3,0)` and `(5,0)`, `(0,1)` versus `(0,3)` and `(0,5)`,
   and `(1,1)` versus `(3,3)`.  These are diagnostics, not the missing
   induction.
6. The base tuple (7.1) is exactly the certificate's
   `111010110101011`.  As a genuinely constant matrix it has rank one
   (rank zero after base subtraction).  The memo correctly makes no rank
   claim for `U(H(h_jw_i))`; its unary boundary is conservative.  The
   row-only term `U(H(h_jv))` has rank at most one componentwise.

## Referee conclusion

The first-family formulas and every requested bounded table survive exact
replay, so there is no bounded counterexample to the proposed identity.
What fails is the proof of all-index invariance, especially after the
canonical module normalization required by the certificate.  The universal
claims for the other two families are additionally unsupported by displayed
data.  The memo should not state `R_ij = delta_ij` or universal
three-family cancellation until Findings 1--4 are repaired.

## Re-review round 1

### Verdict

**REVISE.** The revised memo rigorously withdraws the unsupported all-index
companion identity and the row-2/row-3 universal claims. All four original
findings are addressed under that deliberately narrowed scope. One new
load-bearing error remains in the statement of the open boundary obligation
in Section 4.

### Original findings

1. **Finding 1 — ADDRESSED.** Sections 3 and 4 now define occurrence
   translation by accumulation at `c_vertex(action * vertex)`, define every
   shortlex key after canonicalization, and explicitly include the second
   canonicalization inside inversion kernels. The raw-block cancellation
   argument and its all-index conclusion are withdrawn.
2. **Finding 2 — ADDRESSED.** The ten-cell lemma and all conclusions based
   on it are deleted. Equations (4.2)--(4.3) are the exact bilinear
   differences for equality and polarized inversion kernels. Equations
   (4.5)--(4.6) exactly expand both external `LT` monomials and retain every
   old--new and new--new term. Because the dotted currents are defined only
   after occurrence action and `c_vertex` accumulation, canonicalization
   and collisions are included rather than treated as raw-word
   cancellation. The memo correctly says these right sides have not been
   proved zero in the open regions.
3. **Finding 3 — ADDRESSED.** Section 6 retracts the second- and
   third-family primitive, companion, and universal-cancellation claims and
   labels those matrices open. Their omitted fixed data are no longer
   demanded as support for a theorem the memo does not state.
4. **Finding 4 — ADDRESSED.** Section 2.0 supplies the exact finite
   Stallings/Nielsen argument: the complete four-vertex core has rank five;
   the five loop-coordinate words form a free basis via the displayed
   Nielsen inverse; the five `RS_IN_K` words are the
   Reidemeister--Schreier basis; and evaluation sends that basis to the five
   core loops. This makes evaluation and `rewrite_k` inverse homomorphisms,
   so reversal is an anti-homomorphism on arbitrary powers. The displayed
   finite constants agree with the certificate, including
   `rewrite_k(A)=A`, `rewrite_k(B)=B`, and `rewrite_k(G)=G`. This closes the
   exactness issue for the retained first-family endpoint factorization.

### New open finding

1. **[NEW] The six diagonal-boundary defects must not be required to vanish
   kernel-by-kernel.** After correctly saying that the six offsets must be
   evaluated separately, Section 4 states that the remaining lemma should
   make “every right side of (4.2)--(4.6), including the six boundary
   offsets,” zero and should emit 76 identities. This is false even for the
   independently proved primitive kernel `P(i,j) = delta(i,j)`. At the
   `i`-boundary offset `i-j=-2`,

   \[
   P(i+2,j)+P(i,j)=P(j,j)+P(j-2,j)=1,
   \]

   and at `i-j=0` the same `i`-difference is also one. Likewise the
   `j`-difference is one at offsets `i-j=0` and `i-j=2`. Hence
   (4.2)--(4.6) are exact expansions, but their boundary right sides are
   values to compute, not 76 zero identities.

   Smallest repair: restrict the kernel-by-kernel zero requirement (4.7) to
   steps staying inside an open region. At the six boundary offsets, emit
   exact defect values. If the future target is `R=delta`, require the
   aggregate companion boundary defects to equal the corresponding delta
   defects; equivalently, for the full `beta=P+R`, require only the xor of
   all 76 boundary defects to vanish. Do not require each constituent
   kernel defect to vanish.

### Bounded evidence

No grid or search was run. A constant-size replay confirmed the five
core-coordinate images, five inverse Nielsen words, five `RS_IN_K` words,
their exact evaluations to the five core loops, and
`rewrite_k(A,B,G)=(A,B,G)`. The new boundary counterexample uses only the
retained exact identity `P_ij=delta_ij`.

## Re-review round 2

### Verdict

**APPROVE.** The sole open finding from round 1 is addressed.

Section 4 now imposes kernelwise zero defects only when both endpoints of a
two-step move remain in the same strict region `i<j` or `i>j`. It separately
identifies the six diagonal-crossing or diagonal-meeting offsets and
requires exact 76-component defect values there, with no componentwise-zero
claim. Equations (4.8)--(4.9) correctly record the primitive delta kernel's
boundary defects as `(1,0,1)` for both ordered offset triples.

The future aggregate targets are also stated correctly: a companion proof
of `R=delta` must match the xor of the 75 companion defects to the primitive
defect, while a proof for the full `beta=P+R` requires only the xor of all 76
boundary defects to vanish. Fix round 2 preserves the withdrawal of the
all-index theorem and claims no new computation.

### Remaining findings

None within the scoped re-review.
