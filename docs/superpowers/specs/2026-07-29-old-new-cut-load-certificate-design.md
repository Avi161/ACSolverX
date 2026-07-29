# Old--New Cut Grouped-Load Certificate Design

Date: 2026-07-29

## 1. Purpose and theorem boundary

The next deliverable is a finite, independently replayable certificate for the
only unresolved positive-chamber identity in the period-two argument:

\[
  \mathbb B(A_{n+1,d},b_{n+1,d})
  =\mathbb B(A_{n,d},b_{n,d}) \qquad (n\ge 0,\ d\ge 1).
\]

The endpoint-potential reduction has already reduced this claim to six family
parities.  The certificate will materialize those parities as 9,408
source-fiber/cell loads carrying 17,760 old-occurrence histograms.  It will
bind raw provenance through integral collision fibers and compress the
1,491,840 active comparisons instead of serializing every pair as a separate
JSON object, which previously ran too slowly and overheated the machine.

This certificate is not, by itself, an AC or stable-AC trivialization of
AK(3).  It is one lemma in the current proof route.  It must not assert the
unproved formula `Q(A_(n,d))=[d=0]`, and it must not treat the `d=0` endpoint
branch as closed.

## 2. Considered approaches

### A. Grouped load histograms with independent replay (selected)

Aggregate the old source rows by integral collision fiber before parity, then
record one load row for each surviving source fiber and threshold cell.  For
every old occurrence in that load's exact footprint, store a complete
partition of its comparisons with the 84-token collision-first word
`T=b_(n,d)`.  Stable token masks and computed counts bind the compact
histograms to every underlying comparison.  A separate verifier reconstructs
the rows and comparisons without importing generator logic.

This approach retains every proof obligation while keeping the executable
artifact small enough for a guarded 30-second run.

### B. Full raw pair ledger (rejected)

Serialize every atomic comparison directly.  This is superficially simple,
but the prior attempt produced 1,491,840 records, serialized inside nested
loops, exceeded the safe runtime, and caused sustained CPU use.  It adds no
mathematical information beyond the grouped partition.

### C. Pure symbolic involution (rejected for the present route)

The residual P rays satisfy an exact conjugacy, but the conjugating map is
neither shortlex preserving nor shortlex reversing and does not preserve the
84-token occurrence action.  The three Q pairs likewise have unequal
contexts.  These exact counterexamples rule out the currently named uniform
involution ansatz; they do not rule out a future deeper theorem.

## 3. Artifacts and isolation

All implementation is new-file-only.

- `.scratch/period_two_old_new_cut_load_certificate.py` generates the
  canonical manifest from approved source artifacts.
- `.scratch/period_two_old_new_cut_load_verify.py` independently reconstructs
  and verifies the manifest.  It must not import the generator.
- `.scratch/test_period_two_old_new_cut_load_certificate.py` contains literal,
  hand-derived fixtures and end-to-end generator/verifier tests.
- `.scratch/period_two_old_new_cut_load_manifest.json` is the canonical
  certificate payload.
- `.scratch/period_two_old_new_cut_load_certificate.md` states the proved
  theorem, dependency hashes, replay command, and explicit non-claims.

The interrupted
`.scratch/period_two_old_new_cut_covariance_checker.py` is not a trusted
dependency.  It may be consulted for schema notation, but no zero failure
counter, claimed family value, or `d=0` assertion may be copied as evidence.

## 4. Source binding

The manifest starts with SHA-256 bindings for every executable source and
upstream data artifact used to reconstruct a row.  Loading fails if any
required path is missing or any expected source theorem status is not
verified.

Every old row records:

1. its stable row identifier and family;
2. the approved raw-manifest row or rows in its integral collision fiber;
3. every integer coefficient before reduction modulo two;
4. the computed integral fiber sum;
5. its exact parameter domain and `current_equality` flag; and
6. whether it survives or is absorbed, with the partner fiber when absorbed.

The doubled slot-zero anchor is bound to its 21 approved provenance rows.
Evenness is computed from those rows rather than asserted in prose.

## 5. Cell decomposition and pumping witnesses

Threshold cells use the states `0`, `1`, `2`, and `ge3`, with base value 3
for `ge3`.

- Fixed, base, singleton, and C families use the 16 `(a,n)` cells.
- P uses the 54 nonempty `(a,h,r)` cells in the domain `h+r>=a`.
- Q uses the 64 `(h,k,n)` cells with `a=h+k`.

For each powered schema and cell, the manifest records:

- nonempty, freely reduced, cyclically reduced primitive cores;
- the exact affine exponent at the base and every nonnegative slope;
- the tagged fully reduced base word;
- one surviving adjacent-copy boundary for every changing factor, including
  copy identifiers and reduced-word offsets;
- pairwise distinct selected boundaries;
- the pre- and post-`cvert` terminal-`c` branch; and
- the comparison discharge: strict affine length, identical normalized block
  list, or common pumped prefix followed by a fixed mismatch.

The only primitive cores expected in the concrete schemas are
`ctcTTTct` and `cTctttcT`, both of reduced cyclic length eight.  The verifier
rechecks this fact from letters and does not trust the recorded booleans.

The verifier also proves that the listed cells are disjoint and cover the
whole stated orthant.  It checks P-domain nonemptiness algebraically rather
than by sampling.

## 6. Load-row representation

The endpoint reduction predicts the following census.  These values remain
**[unverified]** until the new generator derives them from the bound sources
and the independent verifier reproduces them:

| family | rows/cell | cells | source loads | footprint/load | occurrence-loads | comparisons |
|---|---:|---:|---:|---:|---:|---:|
| fixed | 70 | 16 | 1,120 | 1 | 1,120 | 94,080 |
| base | 2 | 16 | 32 | 2 | 64 | 5,376 |
| singleton | 1 | 16 | 16 | 6 | 96 | 8,064 |
| P | 32 | 54 | 1,728 | 2 | 3,456 | 290,304 |
| C | 39 | 16 | 624 | 2 | 1,248 | 104,832 |
| Q | 92 | 64 | 5,888 | 2 | 11,776 | 989,184 |
| total |  |  | **9,408** |  | **17,760** | **1,491,840** |

Each source load names its integral collision fiber, cell, module/label
schema references, and complete old occurrence footprint.  A footprint entry
names its occurrence, polarity, literal AST leaf, module schema, and label
schema; a fixed entry instead names its literal leaf and has no occurrence.
Every footprint entry is compared with exactly 84 collision-first B-tokens,
giving the predicted **[unverified]** workload
`17,760 * 84 = 1,491,840` comparisons.

Raw provenance rows remain bound by the integral-fiber records in Section 4,
and bilinearity proves that even fiber sums contribute zero.  The compact
certificate need not serialize one object for every comparison: each grouped
load retains the source fiber, while one histogram per occurrence retains the
complete active comparison partition.  It must compute the raw-fiber, source
load, occurrence-load, and comparison censuses so a missing occurrence cannot
masquerade as compression.

For each footprint occurrence, the 84 comparisons are partitioned into
histogram buckets keyed by:

- stable B-token source class and coordinate;
- equality exclusion;
- occurrence polarity;
- unsigned module comparison method and result;
- polarity-adjusted chronology result;
- transported-label comparison method and result; and
- final contribution bit.

Each bucket stores its count and an 84-bit token mask.  Masks must be disjoint
and have union `(1<<84)-1` for each footprint occurrence.  The independent verifier
recomputes every mask and bucket key from the bound source data.  Thus the
histogram is compact, but omitting, duplicating, or reclassifying an atomic
comparison is detectable without storing 1.49 million JSON objects.

## 7. Family aggregation and success condition

All values are computed by xor from the load rows.  The endpoint reduction
predicts the following **[unverified]** family table; a mismatch is a failed
proof attempt, not a constant to update:

- fixed: zero on all 16 cells;
- base: zero on all 16 cells;
- singleton: one on all 16 cells;
- P: zero on all 54 admissible cells;
- C: one exactly on the four cells with `a=0`, zero on the other 12; and
- Q: zero on all 64 cells.

The generator exits nonzero and does not write a success memo if any source
binding, pumping witness, histogram partition, comparison replay, row count,
cell coverage, or family value fails.  There are no hard-coded zero failure
counters.

If every check passes, the manifest proves

\[
  \mathbb B(A_{n,d},b_{n,d})=1+[d=1]=[d>1]
  \quad(n\ge0,\ d\ge1),
\]

and therefore the positive-chamber old--new cut covariance identity.

## 8. Verification and resource contract

Development follows strict red-green-refactor cycles.  Expected values in
tests are literal hand-derived fixtures, never values computed through the
generator.  The independent verifier has separate free-reduction,
shortlex-comparison, affine, collision, and parity code paths.

Every proof/test command runs through `scripts/run_proof_guarded.py` with one
job, a 30-second deadline, and the guard's one-thread environment.  A timeout
is a design failure: profile or reduce allocation, do not rerun unchanged and
do not raise the timeout above 60 seconds.  No detached or background process
is permitted.

The final gate requires, in order:

1. focused unit tests;
2. canonical manifest generation;
3. byte-for-byte regeneration;
4. independent manifest replay;
5. mutation checks for a changed token mask, coefficient, boundary tag,
   family parity, and dependency digest;
6. a fresh stale-process scan; and
7. hostile mathematical review of the produced theorem claim.
