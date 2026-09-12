# Independent stable spelling audit — PASS

The frozen `theory_stable_metric.py` and `theory_stable_metric_v2.py` pass the
independent checks in `verification_stable_metric_checks.py/json`. The audit
uses the independent verifier's free reduction, expansion, normalization and
normal-product replay. It does not import the compiler's algebra helpers for
those checks. No census search was run.

For `h=y^p x y^q`, the positive atom has prefix/suffix `(p,q)` and the negative
atom `(-q,-p)`. Subtracting the current suffix and next prefix from each cyclic
gap makes the expanded packed word equal to `y^P W y^-P`, where `P` is the
first atom's prefix. The compiler correctly changes its cyclic frame from
`F` to `F y^-P`. All 160 signed bit-pattern identities pass; 60 would fail
without this compensation. Exhaustive enumeration checks 32 cyclic bit
optima. Sixteen full signed chains with generator labels above `10^24`
retain all four relators and replay through all 64 event boundaries.

The finite parameter bound is valid in the public no-pinch, rank-three
domain. The root row costs `|k|+1`, the new defining row costs
`2+c_k(p)+c_k(q)`, and the rewritten BS row has two stable atoms plus its
minimum gap cost. Its stable atoms cannot cancel together when both gaps
vanish unless `m=n`, which the recognized BS model excludes. Hence its cost
is at least two and strict improvement requires
`c_k(p)+c_k(q) <= L-|k|-t-6`. The coordinate bound follows because each power
token contributes at most `max(1,|k|)` to its exponent.

The v2 coefficient diamond contains every spelling of power cost at most
the ceiling; taking the minimum at each exponent gives exact costs. Its
`2D^2+2D+1` charge is exact. Twelve independent coefficient-cost comparisons
and 424 parameter pairs agree, and 21 truncated balls remain incomplete.
The family-complete flag is correctly conditional on finishing both the
parameter traversal and every attempted flow calculation. It is local to
one recognized donor/root configuration.

For each bit pattern, the old cyclic flow matrix acts on the shifted gap
vector. Zero cost means this vector is exactly canceled: Gaussian elimination
independently agrees with all 136 rational solves on the two planted probes,
including their integer decisions. Every emitted candidate is strictly shorter
and its full chain replays. These probes consumed 647 and 468 charged units
respectively; they are additional physical validation work, not reused
discovery work. Positive cost uses the previously audited finite-flow bound.
Singular systems remain incomplete.

The zero-cost residue pruning is necessary: at a positive/negative transition
the shift is `q(b_i-b_next)`, and at a negative/positive transition it is
`p(b_next-b_i)`. The original no-pinch residue is nonzero, so the bit-independent
gate correctly retains only the two nonzero offsets. Equal bits preserve that
residue, preventing cancellation of two identical inverse stable atoms after
packing. This justifies the endpoint cost used by the probe.

The stated one-sided exclusion for the 33 previously checked fixed metrics
is valid. The power metric triangle inequality gives donor overhead at least
two. When the old companion power cost is at most three, improvement therefore
requires old cost three and new cost zero. A one-sided helper leaves one of
the two opposite-sign transition residues unchanged and nonzero, so cannot
reach zero. This conclusion must be reconsidered after changing the metric
or donor rows.

Definition addition uses the established known-trivial stable lineage; the
subsequent repacking is explicit ordinary AC normal-product substitution.
Unimodularity alone is not substituted for the stable premise. These exact
family and certificate checks do not establish a global AC minimum or a
shortest word in an arbitrary quotient-group generating set.
