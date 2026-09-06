# Search for greater than 55/60 coverage within 10,000 pops

The requested target is ideally 60/60, with strictly more than 55/60 acceptable,
and runtime similar to greedy at the same budget. The active goal remains
open until a completed, certified full-subset run demonstrates the coverage
and measured speed requirement. Production defaults remain unchanged.

## Existing evidence

Fresh cap 48 controls at 10k: greedy40, S20_MK2 52, L+40S with generators49,
and L+20S+1.5W with generators49. Their union is52. S40's49 all solve by
pop402; S20 has15 additional successes after1k. Thus a low1k solve count
alone cannot reject every candidate with a different search mechanism.

The eight S20 failures all have aut_class 106 in the subset metadata. This
motivates general normalization and algebraic mechanisms, but no search
decision may use presentation IDs, class IDs, known solution paths or
previous outcomes. Every row is run independently from its own input.

## First screen

Run 14 declared settings at 1,000 pops on 13 rows: 0,247,203,546,538,602,565,
568,596,605,634,622,637. This extends earlier screens to include two inputs
from the remaining class. It is explicitly tuning on subset 60, not a holdout.

Settings include beam widths1/4/16 with and without the four generator moves;
deeper-first ties in best-first search; strict Nielsen length descent plus
signed permutations at pop time or after child generation; and combinations
of normalization with beam widths4/16. Initial priorities retain S20_MK2.
The exact parameter dictionaries are copied into each phase's manifest.

Nielsen descent is deterministic, always decreases total cyclically reduced
length, and ends with a normalization over eight signed permutations. It
does not enumerate length-preserving Nielsen plateaus, and is not claimed
to be a complete Aut-class representative. Every intermediate word is
preserved in a replayable certificate. Cap48 applies to those intermediate
states too; a normalization violating it is not used.

The beam deduplicates states retained or expanded; pruned unexpanded states
can be discovered again. Best-first order uses(score,depth,key), or
(score,-depth,key) for the explicitly declared deeper-first tie variant.

## Advancement and verification

Advance promising coverage/cost tradeoffs and reserve eligibility for a
structurally distinct candidate with delayed improvement, rather than
selecting only the maximum1k solve count. Complete full60 at 1k for strong
candidates before budget extension; use10k for selected finalists or a
small diagnostic of a new mechanism. All completed or failed screens stay
in the record. New mechanisms require separate source snapshots and manifests.

Any auxiliary AC expansion or sequential restart shares the total node
budget; do not reset10k per component. Cheap word transformations used for
normalization are logged separately, as are their response evaluations and
image applications, and their wall/CPU cost is inside the search timer.
Algebraic macros, if introduced, must expand into elementary legal moves
and report intermediate word lengths and charged work, not hide a large
search behind one node. Larger caps need explicit records and comparison.

The first implementation passed 22 focused tests, including fast image
substitution versus the independent word oracle, normalization certificates,
beam budgets, and unchanged best-first paths on toy controls. A14-setting
30-pop preflight on ms568 passed. All subsequent solves are replayed using
the independent word-level substitution and automorphism implementations.

One worker executes searches sequentially, one numerical-library thread,
with cooldown max(0.5 seconds, preceding search wall time). No timeout is
imposed. Warmup, explicit pre-search garbage collection, certificate replay,
file output and cooldown are excluded from search timing; normalization,
lookahead and reconstruction are included. Both wall and process CPU time
are recorded. macOS schedules physical cores.

Final evidence must include total60-row workload, exact pairwise shared-solve
means, total charged nodes across all components, replayable solutions, and
source/input hashes. This remains in-sample research; meeting this benchmark
does not establish a universal hardness predictor or independent generalization.
