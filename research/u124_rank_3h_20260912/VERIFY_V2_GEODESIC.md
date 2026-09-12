# Dictionary geodesic audit: PASS after the completion-flag fix

The finite automaton has one loop per signed old-generator/helper token, whose
edge labels spell its old-generator image. Only the first edge charges that
token. Thus closed paths at state0 correspond exactly to dictionary words with
their correct token cost; splitting a helper across internal states does not
make its remaining letters free tokens.

The variables`E[p,q]` represent automaton paths whose letter labels freely
reduce to the identity. Empty paths, concatenation of identity paths, and
wrapping an identity path between inverse-labeled edges generate all such
paths. This follows by the usual first-cancellation/nesting decomposition of a
freely trivial word. The implementation carries full edge witnesses, so it
can reconstruct and check the actual path as well as its cost.

Its agenda uses additive nonnegative cost pairs. For length mode the pair is
`(0,token_length)`; for elimination mode it is
`(chosen_old_generator_occurrences,token_length)`, ordered lexicographically.
Both orderings are well founded and translation invariant. Every deduction's
cost is at least each antecedent's cost. When a variable is settled, combining
it with already settled partners processes the deduction whose last
antecedent just became available; a later strictly cheaper derivation would
therefore contradict the agenda's minimum. Zero-cost interior edges can tie
but cannot create a cheaper unprocessed derivation.

Once saturation is complete, any path reducing to a fixed reduced target
decomposes into identity subpaths separated by the surviving target letters.
Query dynamic programming alternates those epsilon closures and exact target
letters. Keeping the cheapest prefix at each state is sound because all future
costs depend only on that state and unread suffix. Completed queries therefore
give exact dictionary geodesics for their **selected exact orientation and
fixed objective**. The wrapper's choice among cyclic orientations is heuristic;
the result does not minimize over every orientation, dictionary or stable move.

Independent tests compare the agenda with a separate global fixed-point
relaxation on the tiny weighted grammar. They also replay every epsilon witness
edge by edge and compare106 completed queries with exhaustive signed-token
words. The lexicographic control with`z=a³b³` and target`aab` returns`A z B B`,
cost`(1,4)`, while length mode retains a length3 representative. Exhaustive
words through length4 agree. No zero-`a` template exists at any length, since
words over`b,z` have`a`-exponent divisible by3 while the target exponent is2.
A full v2 defining-template event independently checks its orientation,
expansion, retained donors, normalization and cost metadata.

## Found and fixed bug

Calling`saturate()` a second time on a previously completed engine replaced its
epsilon table with partial data but did not clear`saturation_complete`.
For the lexicographic control, complete saturation found`A z B B`; a subsequent
zero-budget saturation followed by a large query returned`aab` while falsely
marking it complete. The author fixed this by clearing the flag at saturation
entry. The independent reproducer now returns a valid incomplete candidate and
`complete=False`.

The old source is preserved as
`exchange_v2_geodesic_snapshot_before_reset.py`. The current wrappers create a
fresh engine and saturate it once, so their recorded pilots did not exercise
this reuse bug. Both source hashes are pinned in
`verification_v2_geodesic.json`.

The nine-row v2 pilot independently replays and adds **zero new strict gains
beyond its plateau seeds**. Its9000 new units exclude historical seed
discovery. The summary's three gains versus2180 are the imported
`aca_75`, `aca_83` and `aca_84` paths. No census search was rerun by this audit.

Truncated saturation or queries yield only checked candidate templates. A
complete exact-word flag must not be promoted to complete orientation search,
minimum total presentation length, or a claim about elementary expansion cost.
