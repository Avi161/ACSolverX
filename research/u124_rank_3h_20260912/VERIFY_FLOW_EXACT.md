# Cost-bounded cyclic flow audit: PASS

Let`M q=e'-e`, where row`i` has coefficients`-b_i` at`q_i` and`a_(i+1)`
at`q_(i+1)`, cyclically. The implementation's rational height-walk inverse
agrees with independent Gaussian elimination, including negative BS exponents.
It detects singular matrices and returns incomplete/outside this theorem;
singularity is not reported as absence of a useful flow.

If root`h=a^k` uses unit-cost tokens, every exponent block of packed cost`c`
has magnitude at most`K c`, where`K=max(1,abs(k))`. Therefore a complete flow
of total packed cost at most`C` satisfies`sum(abs(e_i'))<=K C`. For inverse
matrix row`v`,

`abs(q_i) <= abs(v·e) + K C max_j abs(v_j)`.

Taking the floor gives a sufficient integer bound. This is a proof of a finite
box for the declared cost ceiling, not a heuristic flow cutoff.

The sparse dynamic program enumerates each possible next exponent within the
remaining nonnegative cost budget. Divisibility of
`e_i'-e_i+b_i q_i` by`a_(i+1)` yields the next integer flow, including when
the divisor is negative. Prefixes reaching the same flow state can be compared
by cost, absolute-flow sum and lexicographic path; the discarded prefix cannot
improve any continuation. Since all block costs are nonnegative, pruning above
the remaining budget is sound. The final cyclic equation and total cost are
checked before admitting a candidate.

After a completed cyclic Britton scan, opposite stable neighbors have nonzero
exponent residues modulo their pinch divisor. A flow changes such an exponent
by a multiple of that divisor, even across the cyclic cut. It therefore cannot
create the first stable cancellation. Packed cost plus the unchanged stable
letter count then measures the packed target, so a strict cost reduction gives
a strict complete-tuple shortening. The exact ordinary-AC ledger independently
verifies every compiled change regardless of that length argument.

The donor-index remapping after normalization is valid under the public probe's
invariant: all nontarget donors were already normalized and remain unchanged.
Only their positions move. Internal prefix helpers should not be called on
arbitrary unnormalized donor tuples without additionally transporting their
orientation witnesses.

Independent controls compare six complete programs against exhaustive finite
boxes, check960 opposite-neighbor residue identities, and exercise negative
root and BS exponents. Thirteen truncated calls retain a valid completed flow
while correctly reporting`complete=False`. Singular and zero-budget cases are
also marked incomplete. A known-trivial BS(1,2) planted prefix independently
replays its Britton reduction to stable lengthone.

All seven saved pilot records pass and add no new gain. They cost3027 new
units and import no seeds. No census search was rerun. The finite-box theorem
does not assert a global AC minimum, complete detection in singular systems,
or an elementary expansion-size/runtime bound; work units count the stated
model, pinch and DP evaluations.

Reproduce with`verification_flow_exact_checks.py`. Full results and hashes are
in`verification_flow_exact.json`. No algebraic or finite-bound bug was found.
