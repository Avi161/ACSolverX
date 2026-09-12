# Theory wave 2 (coordinator recovery)

The assigned theory agent timed out before writing this file. Contents
below are only identities and negatives already machine-checked on this
branch, plus one new bounded C15 probe. Status labels match the catalogue.

This is not a U124 solve.

## Killed or stalled routes (do not repeat)

### K1. Adjoin `t^{-1} x^{nδ}` and isolate `t` from the same Q relator — ROUND-TRIP

After replacing the displayed power by `t`, the second relator is an
isolator of `t`. Solving for `t` and substituting back into the defining
relator returns a rewrite of the original pair (or the C11 peel if the
common tail was used as the defining word). Same-relator isolation after
adjoining a displayed block is not a new theorem.

### K2. Unconjugated second Q peel — does not induct on `n`

C11: `R2 ← R2 R1^{-1}` yields `u x^{(n-1)δ} v [y^{-1},x^{-1}]`, 14/14.
Repeating the same multiply does not restore suffix `v`. An n-fold peel
that reached `uv = y^{-1}` would finish; that restoration is
counterfactual. Advisor: C11 APPROVE as an identity, not a descent.

### K3. Orientation second peels as μ-progress — REFUTED on `Q_{2,±1}`

Some AC1/AC3 reorientations drop raw length relative to the inflated
post-peel pair, or drop the longest x-run. Independently, remainder
`YXyxYYXyx` is ordinary-AC legal and raises `μ: 14 → 18`. An x-run drop
is not a well-founded measure.

### K4. Family A common-prefix core — raises μ

`R2 R1^{-1}` is a conjugate of `B A^{-1}`. After AC3, keeping `(R1, core)`
raises μ for `n=2..7`.

### K5. Cyclic `v`-power Bézout shape on Q’s first relator — recognizer negative

For `v = y^{-1}x^{-2}`, no cyclic conjugate of `R1` is `v^{±m}` times a
v-free word (`q_r1_v_power_shape_hits = 0`). AK3’s `A = a v^{-m}` is not
visible on that spelling.

### K6. Rank-3 isolator census on Q — recognizer negative

`|w|≤2`, template `≤4`: 0 accepted corridors. Not an obstruction.

### K7. Cyclic complement on Q / Aut image / Aut-min floors — does not fire

Join corank ≥ 2. Not an obstruction (AK2 control).

### K8. Primitive displayed relator / stored product / depth-1 child — recognizer negative

C12 is a valid **conditional** stable finish line (Sol REVISE applied).
Hits: 0/248 relators, 0/248 products, 0/11,686 unique new depth-1 AC2
relators. Whitehead minima start at 5, which is not a C12 hit.

## Live theorems (already in the catalogue)

- C11 common-suffix peel: PROVEN identity, not a solve.
- C12 primitive relator: CONDITIONAL on C1, non-effective Aut step;
  step 4 is elementary and replayed.
- C13 depth-1 AC2 length neighbourhood: exact bounded negative.
- C15 named BS(m,m+1) stall with companion `YXXXyxYx`.

## Proposed C15 lemma (now checked, see `c15_divisibility_scan.py`)

**Hypothesis.** `W = y^{-1}x^{-3} y x y^{-1} x` and
`B = y^{-(m+1)} x^{±1} y^m x^{∓1}`, `m≥3`.

**Claim A (AC3 by a y-power) — REFUTED for `k ∈ [-(m+2), m+2]`.**

**Claim B (length-preserving Whitehead) — REFUTED on the 20 Whitehead maps.**

**Claim A result.** For `m=3..7`, `y^{-(m-1)} W y^{m-1}` begins with a
y-run of length `m` and still has interior runs not divisible by `m`.
Sample `m=3`: `YYYXXXyxYxyy`, runs `(3,1,1,2)`. AC3 by `y^k` for
`k ∈ [-(m+2), m+2]`, all cyclic orientations of `W`, and all 20
Whitehead automorphisms of each of the ten rows: **0** images in which
every y-run is a multiple of `m`. After the `m=3` leading-run conjugate,
depth-1 AC2 on `(YYYXXXyxYxyy, YYYYxyyyX)` has 432 children and 0
length-drop / one-occurrence / two-block / divisibility hits. These are
exact negatives for those move lists, not Britton obstructions.

## What would count as a U124 finish from here

A displayed conjugator that restores `u x^{kδ} v` after C11; a
divisibility-clearing identity that makes Britton fire on C15 with an
AC1–AC5 expansion; a materialized C1/Lemma-11 witness plus C12; or a
cyclic-complement witness on a spelling other than Q/Aut-min/floor.
Quotient equalities and bounded misses remain ineligible.
