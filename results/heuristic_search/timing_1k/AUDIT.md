# Same-engine 1k timing review

Read-only code review; no presentation searches or CPU-heavy tests run by this reviewer.

The new `greedy` and `s20` branches in `heuristic_1k.py` share the same root
canonicalization, Python heap and parent table, optimized expansion kernel,
cap, path capture, duplicate admission, terminal test, and 1,000-pop ceiling
as `whitehead2`. `greedy` correctly uses total length for the root and
`BASELINE_CONFIG` for children; `s20` uses the existing S20 expression and
configuration. All configurations have one segment, so omitting segment zero
from the Python heap does not change their ordering.

The heap key is `(score, depth, encoded_pair)`. Symbol bytes
`X=1, Y=2, x=3, y=4` reproduce Python string ordering, and the zero separator
makes a first-relator prefix sort shorter first before comparing the second
relator. This heap order is distinct from the `Y < y < X < x` order used to
select canonical relator representatives; the implementation preserves both.
First-discovery admission and terminal checking after the pop are shared.

`W` is the minimum total cyclic-length change among four simultaneous Nielsen
substitutions: `x->xy`, `x->xY`, `y->yx`, and `y->yX`, each fixing the other
generator and respecting inverses. Its adjacency formula counts inserted
letters minus twice the corresponding cancelling seams. It is a signed
one-step response, not a distance lower bound or an Aut-invariant hardness
classification. The input and subsequent states are cyclically reduced and
canonicalized; the `whitehead2` arm does not Aut-minimize them or add basis
changes to the search graph. Negative `W` values are consequently legitimate.

Required timing controls: warm every arm before timing; same fixed 60 rows,
cap 48 and 1,000 pops; rotate four-arm order across rows; sequential execution;
one library thread; recorded scheduling priority; cooldown outside timing;
wall and process clocks surrounding exactly `run`; certificate replay and
output writing outside both clocks. Compare every new greedy/S20 outcome
and pop count with its saved record before publishing timing conclusions.

Interpretation limits: this measures the same implementation with different
ordering rules, not separately optimized implementations of each rule.
The common expansion kernel computes the full feature vector even for pure
length. The experimental heap stores byte keys in Python rather than using
the compact engine's full two-bit state arena. macOS scheduling does not
guarantee a fixed physical core or equal frequencies, so report warmed serial
local timings rather than a pinned-core benchmark. One pass has timing noise;
do not report confidence intervals or extrapolate to million-pop throughput.

`aut_edges` must remain separately labelled because it adds four transformed
neighbors per expanded state, and its certificates can contain basis changes.

## Final driver inspection

Inspected `experiments/search/time_heuristic_1k.py` after its creation. It
implements the controls above: all four arms receive two five-pop warmups;
each arm occupies each order position exactly 15 times; both clocks surround
the same `run` call; garbage collection, certificate replay, writing, and
cooldown are outside the clocks. `numba.set_num_threads(1)` is explicit, with
external library thread settings captured in the manifest. The initial
`nice(10)` attempt was denied by the desktop sandbox before presentation
searches. The final driver catches that denial and records that inherited
priority was retained; it does not claim the process priority was lowered.
The driver rejects an existing run file, hashes its inputs and implementation,
records the macOS core-affinity limitation, and asserts all 240 saved solve/pop
outcomes individually before writing each record. No blocking protocol or
search-order defect found in this static inspection.

`run` includes input validation/canonicalization and successful path
reconstruction inside the reported search interval. The timing label should
retain that meaning rather than claiming isolated kernel CPU time. Certificate
replay gets its own recorded wall time and is not included in search totals.
No presentation searches were run by this reviewer.

## Completed result arithmetic audit

Reviewed `results/heuristic_search/timing_1k/PIPELINE.md`: its description
matches the current code, including the seam-cancellation restriction, both
symbol orderings, precise adjacency formulas, absence of Aut-minimization,
mixed-move distinction, compact-arena exclusion, and timing boundaries. No
blocking accuracy defect found.

Independently parsed the completed JSON files using only standard-library
arithmetic. Confirmed all 240 unique `(arm, pres_id)` records, exact input
pairs and bins, cap 48, budget 1,000, observed pops in 1..1,000, all saved
per-row outcomes and pop counts, verified-certificate flags on every solve,
and every successful path's state/step cardinality. Each arm has 60 rows and
occurs exactly 15 times in each order position, with the specified rotation
matching every record. Every recorded time is finite and nonnegative.

Recomputed all totals from records; they equal `summary.json` exactly:

| arm | solves | pops | wall seconds | CPU seconds | replay seconds |
|---|---:|---:|---:|---:|---:|
| greedy | 29 | 36,090 | 5.049893504 | 5.010289000 | 0.007239707 |
| s20 | 37 | 28,658 | 4.490181249 | 4.402835000 | 0.012136249 |
| whitehead2 | 42 | 27,952 | 5.357633163 | 5.290297000 | 0.014912078 |
| aut_edges | 43 | 18,961 | 4.712571374 | 4.593535000 | 0.011919376 |

Maximum single search wall time was 0.361609583 seconds. The manifest records
one Numba thread, all five library thread environment variables set to `1`,
and `priority adjustment denied; inherited priority retained`. This arithmetic
audit checks logged evidence and flags; it does not independently rerun
certificates or presentation searches.
