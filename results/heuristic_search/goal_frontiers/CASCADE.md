# A short-relator rewrite followed by heuristic search

The fixed candidate first reached **60/60 at a 1,000-unit budget**, using
6,286 charged units in total, at most 404 for one presentation, in 1.124607s
wall/1.070814s CPU across all 60 rows. The rewrite solved 21 rows and the
L+40S generator search solved39; no row needed the S20 fallback.
Every solution has a replayable state/move certificate.

This is a structural rewrite/search hybrid. It is not a single new scalar
score and is not evidence of a universal initial-state hardness classifier.

## Fixed procedure

1. Canonically reduce the input and apply strictly length-decreasing Nielsen
   basis changes, then normalize over eight signed generator permutations.
   Preserve every accepted basis change and its intermediate state.
2. Look for a relator that, up to cyclic rotation/inversion and signed
   generator choice, is `b^-1 a b a^-2`. Check that the companion has
   exponent sum+1 or-1 in b. No presentation or class identifier is read.
3. Use that short relator as a donor for explicit rewrites of the companion.
   The identity `b^-1 a b = a^2` permits moving powers across b. The code
   chooses a concrete substring replacement, derives the corresponding
   rotation/sign substitution move, and checks its resulting canonical state.
   Repeated rewrites aim to leave one occurrence of b in the companion.
4. When that happens, the companion expresses b as a power of a. Use it as
   donor to remove b from the short relator, producing an inverse generator.
   Use that generator relator to finish the companion. These are ordinary
   substitution moves after the initial basis change, not an asserted group
   equality substituted for a move certificate.
5. If recognition or rewriting does not solve within its allowance, restart
   from the original input with L+40S and four Nielsen neighbors for up
   to500 pops. S20_MK2 receives the remaining global budget if needed.

There is no lookup of benchmark IDs, automorphism-class IDs, solved states,
previous paths or previous outcomes inside this solver. Each presentation
is solved independently. The benchmark was used to select mechanisms, so
the measured60/60 remains in-sample research, not an independent holdout.

## Budget and length accounting

Accepted normalization path transforms each cost one unit. The rewrite
component costs one root plus one unit per elementary substitution. Every
failed attempt and every pop in each fallback is added to the same budget;
there is no fresh1k or10k allowance per component. Rewrite allowance is
min(1,000, remaining budget), and the S40 starter is capped at500.

The normalization routine also evaluates alternative images to choose its
path. Those candidate evaluations are separately counted and their cost
is included in search timing; they are not charged as additional heap pops.
This is analogous to generating several neighbors per pop in the controls.
There is no hidden auxiliary AC tree search inside the rewrite.

Ordinary search retains cap 48. Rewriting has an explicit intermediate cap256.
**The measured maximum canonical relator length is 131.** Eleven successful
certificates exceed 48: three reach 67, and the eight formerly unsolved rows
reach 131. Larger temporary words are part of this result. It must not be
reported as60/60 under the previous cap 48 restriction.

## Why it crosses the plateau

The previous S40 generator search solved its49 successful rows by pop402
and gained no new solve by10k. The missing eight rows from S20's52-solve
set share one listed Aut class, and three additional S20-only rows form
another difficult part of the S40 failure set. The rewrite solves all11.

For the illustrative family with companion
`b^{-(n+1)} a^-1 b^n a`, the short donor enables a sequence leading to
`b^-1 a^{1-2^n}`. This temporarily grows a relator while eliminating the
stable-letter conjugations. At n=7, the standalone verified rewrite uses
257 charged states, with peak canonical length131. This family is a
description of the rewrite mechanism, not an input table in the solver.

## Verification and provenance

The BS rewrite passed29 focused tests, including signed generators,
rotation/inversion/swap, several n values, nonfamily companions, and clean
budget/cap failure prefixes. Those tests replay ordinary substitutions using
the separate greedy-baseline decoder. The cascade adds six focused tests
for path composition, shared budgets, terminal input and a tiny-budget edge
case. The final combined35-test run passed.

The 1k benchmark replayed all 60 solutions through word-level moves. Macro
construction uses that same word-level move oracle, so the final matched
run additionally replays every solution with the separate compiled
greedy-baseline substitution decoder. Basis transformations are checked
through literal word substitution, separately from their compiled producer.

`cascade_1k/sources` retains the exact1k source snapshot. A subsequent fix
changes a tiny-budget normalization guard from>=input length to>input length;
it cannot affect these1k rows, and the 10k verification explicitly checks
the exact same paths and charged counts. Each benchmark stores source/input
hashes, component accounting, clocks, settings and complete certificates.
