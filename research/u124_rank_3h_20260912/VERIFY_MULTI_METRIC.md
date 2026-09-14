# Triangular two-denomination metric: PASS

For 2<=l<k, a shortest power spelling has cost
`c_(l,k)(e)=min_b (|b|+c_l(e-kb))`. Collecting signed exponent counts gives a
lower bound attained by concatenating the selected powers. The old one-helper
spelling bounds |b| by c_l(e), so the finite coefficient loop is complete.
The implementation can tighten its incumbent during that loop without losing
any unvisited coefficient because Python fixes the loop range at entry.

The retained triangular definitions cost l+2+c_l(k). Both nonzero BS powers
cost at least one token each. If v opposite-sign stable transitions survive
the no-pinch check, their nonzero residues force at least v power tokens in
every flow. Writing d=c_l(k)>=2 therefore gives endpoint length at least
`l+d+t+v+6`. A strict improvement over L implies
`l<=L-t-v-9`, `d<=L-t-v-l-7`, and `k<=l*(L-t-v-l-7)`.
The code enumerates this finite superset with the correct inclusive bounds.
Its exact-cost pruning only removes pairs that cannot meet the target length.

Every token represents a power of magnitude at most k. Hence total power cost
at most C implies sum|e_i'|<=kC. The previously audited rational inverse bound
and sparse divisibility dynamic program remain valid with this metric.
Completeness is per tested pair and completed flow; the shared budget can
stop before all mathematically feasible pairs have been evaluated.

Compilation first uses the old root/BS donors, then shears the old helper,
adds the lower-power helper with all old rows unchanged, and rewrites the
upper defining row using only the lower donor. The upper power is reconstructed
as a product of these two retained definitions. Repacking the other two rows
therefore never uses its own target as a donor. The independent normal-product
checker validates this claim directly, not just in the quotient.

Controls compare42 power costs with an independent integer BFS, four complete
flow optima with finite-box enumeration,12 truncated calls, and eight signed
rank3→4 certificate chains using generator IDs above10²⁵. All six events in
each chain independently replay. Public probe assumptions are 2<=l<k and a
nonnegative ceiling; direct arbitrary-argument helper calls are outside scope.
No module algebra or finite-bound bug was found.

The large-label control did reveal an inherited auditor allocation bug:
the frozen `rank_unbounded_20260912/audit.py` built a map with range(1,helper).
Only the stalled audit process was stopped. The frozen file remains unchanged;
current `verify.py` now checks defining events with a sparse actual-basis map.
The same large-label chains then completed successfully. This changes auditor
resource behavior, not saved census certificate outcomes.

Reproduce with `verification_multi_metric_checks.py`; results and hashes are
in `verification_multi_metric.json`. No census search was run.
