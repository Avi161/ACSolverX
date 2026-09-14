# Universal root metric and rank peeling: PASS

The universal metric preserves rank and applies the explicit helper shear
before repacking every other row using only the retained root donor. All
nontarget rows are visited once; normalization permutations transport the
pending row indices and root factors. No BS recognizer is needed for these
exact free-word and normal-product identities.

If expanded canonical cores contain N nonbase letters, any selected positive
denomination d has retained-definition cost d+1 and at least N other letters.
A nonincreasing endpoint therefore requires d<=L-N-1. This gives the stated
finite ceiling at arbitrary rank. The exact predicted cost sums independent
power-block costs over every remaining relator. Canonical cyclic representatives
do not split a base block across their cut: if they start with that generator,
lexicographic minimality chooses the beginning of its maximal initial run.
Thus the cyclic repacking has the predicted length. Explicit endpoint checks
guard this accounting in every emitted candidate.

Eight signed direct chains at ranks3 and11 independently replay and match
separate coefficient-based power costs. The known-trivial (Zyyyy,xz,y) plant
respects budgets0,1,4,100,1000; the latter two both use31 units and retain four
nonincreasing endpoints. Completion metadata refers to denomination costs for
one recognized root, not global presentation minimization. Returned tuples can
be equal-length changes; their utility is a separate search question.

Rank peeling orders pivots by the proved degree/length upper bound, computes
the actual endpoint, and accepts only nonincreasing removals. Positive-bound
pivots are still tested because free cancellation can make them useful. Every
accepted event drops rank, so neutral removals cannot produce an infinite
plateau. A completed negative scan means every available pivot at that endpoint
was tested; stopping on the budget reports incomplete. An empty tuple is
complete even at zero budget.

Saved rank1/2/6/11 chains all independently replay to empty with one charge per
removal. Three truncated controls and the empty boundary pass. The dispatcher
now verifies occurrence metadata and actual change against both zero and its
computed bound; a corrupted degree is rejected. Normalization is explicit and
not charged as a removal attempt. Stable legality retains known-trivial lineage.

No implementation bug was found. Results and hashes are in
`verification_universal_root_peeling.json`; reproduce with
`verification_universal_checks.py`. No census search was run.
