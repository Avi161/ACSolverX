# Matched four-arm 10,000-pop benchmark review

This reviewer may write only this Markdown artifact. Review is read-only:
no presentation searches, certificate replays, tests, CPU-heavy work, or
shared-source edits are performed by this reviewer.

## Current request and protocol

The user explicitly authorized 10,000 pops and then clarified that there
must be no timeout. The earlier timeout proposal is superseded. The public
1,000-pop exploratory entry point should retain its existing ceiling; the
new bounded benchmark may call `mixed_search` with its own validated fixed
10,000-pop configuration.

The four settings are length greedy, S20_MK2, L+40S with the four Nielsen
neighbors, and L+20S+1.5W with those neighbors. Every arm should use the same
60 inputs, cap 48, canonicalization, expansion kernel, Python heap/parent
capture, discovery policy, and pop-count convention. Generator-neighbor
arms have a different explicit move graph and mixed certificates.

The planned controls are one serial process, one library thread, warmed
compilation outside timing, cyclic arm-order rotation by row, and cooldown
at least max(0.5 seconds, preceding search wall time). With 60 rows and four
arms, rotation should put each arm in each position 15 times. macOS chooses
physical core/frequency; inherited priority must be recorded honestly if
lowering it is denied. Initialization and successful path reconstruction
belong to the timed search call; replay, output and cooldown do not.

## Required means and denominators

For each of the six distinct arm pairs A,B, form the exact ID set

    I_AB = {i: A solved i and B solved i}.

Both arithmetic mean search times must use precisely this same set and
denominator `len(I_AB)`: sum of A's recorded search times over I_AB divided
by its cardinality, and likewise for B. The denominator is not either arm's
individual solve count, the smaller solve count, or all 60 rows. Store the
IDs so this is auditable. CPU-time and pop-count means, if supplied, must use
the same intersection. An empty intersection means unavailable, not zero.

The all-four intersection is a separate set and must not replace pairwise
intersections. All-60 workload totals include failed budget-exhausted rows;
shared-solve means exclude them. These answer different cost questions and
should remain explicitly labelled. No geometric mean or mean of per-row
ratios should be substituted for the requested arithmetic mean times.

## Source preservation checkpoint

After the timeout-hook reversal, `heuristic_1k.py` has SHA256
`720ed144d5ccfa740ec1df7273e7dfe308cc01784612face6e3573e08ed1df1e`,
exactly matching the earlier feature-grid scorer. The source therefore
retains the already-reviewed behavior, with no timeout hook remaining.

## Benchmark driver inspection

Read `experiments/search/time_heuristic_10k.py` and its synthetic summary test
without executing either. No blocking issue found.

The four coefficient dictionaries match the intended methods, including
zero MK in both generator-neighbor candidates and zero W in S40. The driver
validates its budget in 1..10,000, cap in 1..128, unique 60-row source, optional
preflight IDs, and reduced-root cap bounds before calling `mixed_search`.
There is no timeout hook or timeout CLI argument; the manifest records null.
The public 1k entry point remains unchanged.

Every arm receives two five-pop warmups using the same parameters/types as
the timed calls. Input/reference loading and cap validation happen outside
per-run clocks. Both wall and process clocks surround the entire same
`mixed_search` call. Certificate replay, historical comparisons, JSON output,
explicit pre-run GC and cooldown are excluded. Source/history hashes,
runtime versions, thread settings, priority outcome, row positions and
method coefficients are recorded, and source hashes are rechecked at the
end. Existing output artifacts cause rejection rather than overwrite.

At cap 48, every method/input has a saved 1k reference. Where a prior run
already solved, increasing only the budget must preserve its exact solution
pop count, state path, move path and basis-evaluation count; the driver checks
all of these. Previously unsolved rows cannot terminate at fewer old pops,
and a new solve must occur after the old budget. These gates add no searches.

`summarize` first requires one unique record per method/ID and the same
nonempty row set for every method. It computes all six actual pairwise
solved-ID intersections, stores those IDs and their cardinalities, and uses
that cardinality for each arm's arithmetic mean wall time, CPU time and
pops. The all-four intersection is computed separately. Empty intersections
produce null means. All-row totals include unsolved searches. The synthetic
test specifically exercises a one-row pairwise intersection when each arm
solves two different rows, plus an empty all-four intersection, duplicates
and mismatched row sets; it is appropriate for this arithmetic requirement.

The final arithmetic, balanced-order, provenance and certificate-record audits
are complete; findings follow.


## Completed-run independent audit

The audit used Python standard-library JSON, sets, arithmetic, regular
expressions and SHA256 only. It did not import the solver, call the benchmark
summary function, run a search, replay a certificate, or run tests.

All 240 records are unique method/presentation pairs covering the exact 60
saved inputs and bins. Each method occurs 15 times in each of the four run
positions, in the declared row rotation. Every record has budget 10,000,
cap 48 and exactly the intended coefficients. The manifest has no timeout,
one repeat, capture enabled, one Numba thread and all five numerical-library
thread environment values equal to 1. All 14 current input, historical-data
and source hashes match the manifest. The search-engine source still matches
the earlier feature-grid checkpoint quoted above.

Every pop count is between 1 and 10,000. All 50 unsolved searches use exactly
10,000 pops and have no stored path. All 190 solved searches have a true
verification flag, a state path exactly one longer than the move path, a
valid distinct-generator singleton endpoint, and path words within cap 48.
Recorded substitutions and the four allowed Nielsen maps have the expected
formats. These are structural and recorded-verification checks; this reviewer
did not independently replay the moves. The parent benchmark performed that
replay outside the timed search.

Basis evaluations are exactly four per expanded nonterminal pop in generator
arms and zero in both controls. Of the successful paths, 41 S40 paths and 47
S20+1.5W paths actually contain generator moves (288 and 308 such steps,
respectively); the controls contain none.

All 163 saved 1k successes retain their exact pop count, state path, move path
and basis-evaluation count: 29 greedy, 37 S20_MK2, 49 S40 with generator moves,
and 48 S20+1.5W with generator moves. The new solves occur after 1,000 pops:
11 greedy, 15 S20_MK2, zero S40 and one S20+1.5W. Historical reference lookup
is unique for all 240 method/input settings.

## Independently recomputed coverage and total cost

| Method | Solves | Total wall seconds | Total CPU seconds | Total pops |
|---|---:|---:|---:|---:|
| greedy | 40 | 44.940204036 | 42.888042000 | 248227 |
| s20_mk2 | 52 | 23.371998211 | 23.284816000 | 141776 |
| s40_gen | 49 | 29.957705209 | 29.532629000 | 114318 |
| s20_w1p5_gen | 49 | 37.099650251 | 36.954880000 | 118508 |

Both generator methods solve precisely the same 49 IDs, a strict superset
of greedy's 40 and a strict subset of S20_MK2's 52. The three S20-only IDs
are 596, 605 and 610. There is no 10k coverage win by either new method.

## Independently recomputed pairwise arithmetic means

All six pairwise ID sets, side-only differences, totals and arithmetic means
match `summary.json`. Both sides of each row use the displayed intersection
cardinality, not the number solved by either method separately.

| A | B | Shared IDs | A wall ms | B wall ms | A CPU ms | B CPU ms | A mean pops | B mean pops |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| greedy | s20_mk2 | 40 | 209.493831 | 35.129743 | 181.455375 | 35.046600 | 1205.675000 | 280.100000 |
| greedy | s40_gen | 40 | 209.493831 | 15.172328 | 181.455375 | 15.080950 | 1205.675000 | 63.875000 |
| greedy | s20_w1p5_gen | 40 | 209.493831 | 27.721501 | 181.455375 | 27.657600 | 1205.675000 | 127.875000 |
| s20_mk2 | s40_gen | 49 | 130.608408 | 21.027961 | 130.075245 | 20.710041 | 853.346939 | 88.122449 |
| s20_mk2 | s20_w1p5_gen | 49 | 130.608408 | 39.476708 | 130.075245 | 39.228143 | 853.346939 | 173.632653 |
| s40_gen | s20_w1p5_gen | 49 | 21.027961 | 39.476708 | 20.710041 | 39.228143 | 88.122449 | 173.632653 |

The all-four intersection independently contains 40 IDs and equals greedy's
solved set. All four methods' means on that fixed set match the separate
`common_all` section; those are also the respective means in the three
pairwise rows involving greedy. The other three pairwise intersections all
contain the shared 49 generator-method successes.

## Timing and interpretation checks

All recorded clocks are finite and nonnegative. Total certificate time,
maximum single-search wall time, preserved-path and verification counts,
and the manifest/summary warmup agreement recompute correctly. Batch elapsed
cannot be reconstructed exactly from per-search records because gaps are not
timestamped; it exceeds the sum of recorded search times plus the prescribed
minimum cooldowns, as expected. Rotation and the sleep call are verified in
source; physical core placement and per-run thermal state are not measured.

The largest wall-minus-CPU gap on the all-four shared solves is greedy on
ms602: 2.482460375 seconds wall versus 1.399791000 seconds CPU, a 1.082669375-second
gap. This is compatible with scheduling or other non-CPU elapsed time, but
these two clocks alone do not establish the cause. The report appropriately
retains both clocks: greedy's common-40 mean is 209.493831 ms wall and
181.455375 ms CPU. No correction of measured wall time is warranted.

The final `RESULTS.md` matches the independently checked numbers and solved
sets, labels exact pairwise intersections and arithmetic means, and correctly
separates 10k coverage from speed on shared successes. It discloses the mixed
Aut/substitution move graph, in-sample selection, single timing pass, lack of
physical-core pinning, and unchanged production default. This is exploratory
budget extension evidence, not a fresh holdout or proof of broad superiority.

No blocking correctness, provenance, or reporting issue found.
