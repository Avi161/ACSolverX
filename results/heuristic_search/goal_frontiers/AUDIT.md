# Cascade source and 1k record review

Reviewed `bs_collapse.py`, `cascade_heuristics.py`, `basis_moves.py`, the
frontier verifier, word-algebra oracle, screen driver and focused test source.
No searches, compilation, tests or certificate replays were executed by this
reviewer. Only this review artifact was written.

## Status

No blocking issue for the completed subset60 result. One generic tiny-budget
edge case was found, reported, and fixed by the parent before the new matched
benchmark. The reporting distinctions below are necessary.

## Generic recognition and legal rewrites

Recognition uses words only: either canonical relator must be a signed-
generator version of `b^-1 a b a^-2`, and the companion's exponent sum in b
must be ±1. It considers relator swap and both generator signs; canonical
rotation/inversion is handled by `canon_rel`. There is no presentation ID,
precomputed path, corpus access, or result lookup in either algorithm.
The fixed exponent 2 is a declared structural pattern, not recognition of
all possible presentations or all BS(m,n) relations.

The elementary pinch rules are consequences of the donor relation:
`b^-1 a -> a^2 b^-1` and `b a^2 -> a b`, with inverse-sign versions.
Every requested replacement is converted to a signed cyclic donor word
`lhs^-1 rhs`. The code finds its actual donor sign/cut, derives the target
cut even when canonicalization inverted the target, applies the ordinary
substitution and asserts equality with the independently constructed
intended replacement pair. It never assumes a recognized input is solved:
missing pinches, cap limits and budget limits return failure/prefixes.

After the companion reaches `b^-1 a^k`, eliminating b from the donor yields
`a^-1`; then donor substitutions erase the remaining a letters from the
companion. This explains the terminal criterion algebraically. A recognized
input that stalls is not an obstruction to triviality.

Normalization records each accepted Nielsen map and final signed relabel.
The successful macro certificate concatenates the original canonical root,
normalization states and macro states without duplicating the macro root.
Fallback searches restart at the original canonical input, so their solved
paths appropriately omit the abandoned normalization/macro branch while
retaining its cost in the presentation ledger.

The frontier verifier checks the original root, every canonical next state,
allowed automorphisms and a terminal pair of distinct singleton generators.
Its word oracle is independent of the compiled expansion and basis code.
The macro itself also uses `words.replay_move`, so that replay is not a second
implementation of the macro's word oracle. The focused macro tests provide
an additional replay implementation via `greedy_baseline.moves_to_states`
and the Numba word functions; this reviewer inspected but did not run them.
Do not overstate the independence of the per-record frontier replay.

## Budget and cap invariants

`bs_collapse` charges one root plus each actual elementary substitution.
It checks remaining budget before rewriting, and checks the canonical desired
child cap before storing a step. A failed recognition costs one. Reaching a
goal on the final permitted rewrite is consistent with the final state
already having its charged path-node count.

The cascade adds normalization trace length, macro charged nodes and each
fallback's actual pops. The starter receives at most 500 of the remaining
budget; S20 receives only what remains. Repeated roots from restarts are
charged again. The finishing assertion bounds the aggregate charge, not
just the winning component. Root-normalization work is bounded by strictly
decreasing total length plus at most one final signed permutation.

Precisely describe normalization accounting: accepted trace transformations
are charged; the initial identity application and seven other signed-image
evaluations are represented in `image_applications`, not additionally charged
as search nodes. Scalar response evaluation is also computation, not a pop.
All this work is inside measured search time. The aggregate counter mixes
frontier pops with explicit path steps; call it charged search work and state
its definition, rather than implying identical branching work per node.

The initial/fallback frontier cap is 48. The macro allows canonical relator
length 256 and tracks actual certificate peaks; unreduced temporary products
can be larger. This is an intentionally different admitted path space from
the cap48 controls and must remain explicit in every headline comparison.
It is user-authorized, but not an identical-cap ablation. A later cap study
can isolate this contribution without invalidating the present certificates.

## Tiny-budget correction and provenance

The initial normalization gate `budget >= total_length` failed statically
for `search(('', 'y'), budget=1)`: signed relabeling can consume one trace
step, leaving no root charge and tripping `normalization_cost < budget`.
The parent changed both matching conditions to `budget > total_length`,
conservatively reserving a root, and added a focused regression test. The
current source was read back. No local execution was needed by this reviewer.

The completed 1k run pins the pre-fix source hash
`f20f68cb1d189ba924537c6033da87694f23578d435dd0804fca697ea6788f36`.
Its `sources/cascade_heuristics.py` snapshot exactly matches that hash.
The current fixed source hash is
`71ff7e5d0bf39e452bdaa8d77250509b3640c6a88d5466f624de33d795b8e624`.
The other 16 manifest inputs/source files match their current versions.
The 1k artifact should cite its frozen snapshot; the new matched run should
pin the corrected source and verify unchanged saved1k paths/counts.

## Independent audit of completed 1k records

Read `results/heuristic_search/goal_frontiers/cascade_1k` using JSON and
arithmetic only. There are 60 unique presentation IDs, all solved with true
verification flags. Each record's component-node sum exactly equals its
aggregate nodes, bounded by 1,000. Every path has one more state than moves,
a distinct-generator singleton endpoint and recorded cap peak equal to the
maximum over its stored words.

- Solved: 60/60; total charged work: 6,286; maximum: 404 on ms581.
- Winners: 21 recognized rewrites, 39 S40 generator searches, no S20 fallback.
- Total search wall: 1.124607332 seconds; CPU: 1.070814000 seconds.
- Eleven certificates exceed48: ms596/ms605/ms610 peak67, and
  ms625/ms622/ms624/ms623/ms637/ms639/ms638/ms636 peak131.

The screen driver times the whole cascade call, including normalization,
macro recognition/rewrite, attempted branches and successful path assembly.
Compilation, explicit GC, replay, output and cooldown are excluded. Calls
are serial and numerical threads are set to one. A fresh alternating-order
matched greedy/cascade pass is appropriate for the requested runtime claim;
the earlier 1k/10k times alone are not a new matched measurement.

This is a general structural-rewrite/search hybrid specialized to a detected
relation shape. It is neither an initial scalar hardness classifier nor a
universal solver. The subset was used during discovery, so 60/60 is a strong
in-sample benchmark outcome that still needs independent-family validation.


## Final matched 10k audit

Completed read-only JSON/hash/arithmetic audit of `matched_10k`, without
solver imports, searches, tests or certificate replay. No blocker found.

All 120 records cover the exact 60 source inputs once per method. The stored
order alternates correctly: each method runs first on30 rows and second on30.
All18 current source/input hashes and all18 nested source snapshots match
the manifest. The corrected normalization guard is pinned for this run.

All120 old-trace flags are true and independently confirmed against saved
records: outcome, charged count, state path and move path match exactly.
All60 cascade attempt ledgers also match their1k predecessors. All100 solved
records have both certificate flags true, path cardinality and singleton
endpoints are valid, and all20 greedy failures stop at10,000 with no path.
The second decoder source uses the compiled greedy-baseline substitution
implementation, providing the additional macro replay implementation
recommended above; basis production is independently checked by literal
word substitution. This reviewer checked flags/source, not the replays.

| Method | Solved | Charges/pops | Total wall seconds | Total CPU seconds |
|---|---:|---:|---:|---:|
| Greedy |40/60|248227|40.565477909|40.289806000|
| Cascade |60/60|6286|1.060100705|1.054007000|

The exact pairwise intersection is40 presentations and equals greedy's
solved set. Both sides use those same40 IDs as their arithmetic-mean
denominator. Independently recomputed shared means match the summary:

| Method | Mean wall ms | Mean CPU ms | Mean charges/pops |
|---|---:|---:|---:|
| Greedy |163.049176970|162.117775000|1205.675|
| Cascade |12.797499978|12.679675000|57.450|

Cascade component charges sum to6286:119 accepted normalization transforms,
2724 rewrite-root/substitution charges and3443 S40 pops. Winners are21
rewrites and39 S40 searches. Maximum per-row charge is404; maximum canonical
certificate word length is131. The global10k allowance was never reset.

`goal_frontiers/RESULTS.md` and `CASCADE.md` correctly disclose the different
macro cap256/ordinary cap48, accepted-transform accounting versus candidate
image evaluations, complete search timing, double substitution decoding,
source snapshots, in-sample selection and unchanged production default.
Their final counts, totals, shared means and11 over48 certificates match the
records. The result meets the requested subset benchmark target; the reports
correctly avoid claiming a universal scalar hardness classifier or fresh
holdout validation. Existing code review above remains applicable.
