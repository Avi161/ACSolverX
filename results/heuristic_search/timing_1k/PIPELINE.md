# How the exploratory pipeline works

The implemented new ordering is `L + 20*S + 2*MK + 2*W`. The timing runner
compares it with length-only greedy and S20_MK2 using the same machinery.
The separate `aut_edges` candidate uses S20_MK2 and adds generator changes.

## Search loop

1. Freely and cyclically reduce both relators. Choose each relator's least
   rotation across the word and its inverse, then normalize the pair order.
   This is cyclic canonicalization, not Aut-minimization.
2. Put that pair in a min-heap, ordered by `(priority, depth, encoded_pair)`.
   Mark states seen on first discovery, storing their parent and move.
3. Pop the lowest-priority pair. This consumes one of the 1,000 nodes,
   including the initial state and any terminal state. A solution has two
   singleton relators representing different generators.
4. Generate the existing substitution neighbors: choose the target relator,
   choose the other relator or its inverse, and choose rotation cuts in both.
   Concatenate the rotated words, then reduce and canonicalize. The inherited
   generator requires cancellation at their joining seam; it does not
   enumerate unrestricted AC moves. Resulting relators must each fit cap 48.
   Moves can increase length despite the seam cancellation.
5. Score the children, discard previously seen pairs, and insert new pairs
   into the heap. Continue until a solution, 1,000 pops, or an empty heap.
   This retains a frontier of alternatives; it is not a single-path walk.
6. Reconstruct the successful path from parents. After timing stops, replay
   every certificate step from the original pair and verify the endpoint.

Canonical representatives use symbol order `Y < y < X < x`. The heap's key
tie-break preserves the original Python string ordering `X < Y < x < y`.
These are different orderings with different roles, preserved by all arms.

## The response feature W

Uppercase denotes inverse. For a pair P, use four simultaneous changes of
generators, respecting inverse letters and fixing the unmentioned generator:

    A = { x -> xy, x -> xY, y -> yx, y -> yX }
    W(P) = min_{a in A} ( L(cyclic_reduce(a(P))) - L(P) )

The change applies to both relators. Only their total reduced length matters
to W, so rotation and inversion canonicalization do not affect this value.
Identity and inner automorphisms are not included in this four-element set.

The implementation does not construct those four images for each candidate.
Let Nx and Ny count letters of each generator, ignoring sign, across both
relators. Let C_ab count directed cyclic adjacent letters a,b, counting each
relator's closing edge but never an edge between the two relators. The exact
length changes for the four maps above are:

    d1 = Nx - 2*(C_xY + C_yX)
    d2 = Nx - 2*(C_xy + C_YX)
    d3 = Ny - 2*(C_yX + C_xY)
    d4 = Ny - 2*(C_yx + C_XY)
    W = min(d1, d2, d3, d4)

These counts take a compiled O(L) scan. The extra work is one response scan
per emitted child, in addition to the common feature/scoring pass. It is
performed before global visited-set filtering, so repeated children can still
incur scoring work. There is no hidden BFS, DFS, rollout, or extra pop budget.

S20_MK2 sees cyclic block structure ignoring letter signs: S is the smaller
of the mean x-block and y-block lengths across the pair, and MK is the larger
relator knot count. A mixed cyclic relator's knot count is its number of
x-blocks (equivalently y-blocks); a pure power has zero knots. W introduces
signed adjacency information about cancellation after basis changes.

The new score prefers smaller W. On an Aut-minimal pair W cannot be negative,
but the searched states are not kept Aut-minimal, and W can become negative.
A positive value only says that these four moves individually increase
length. It does not measure a global escape barrier, AC distance, or an
Aut-invariant hardness classification.

| input | four changes | S20_MK2 | S20_MK2 + 2W |
|---|---|---:|---:|
| `YXyxYx / YYYYxxx` | 0, 4, 1, 5 | 49 | 49 |
| AK3 `YXYxyx / YYYYxxx` | 2, 2, 3, 3 | 49 | 53 |

The adjacency formulas were verified against actual word substitutions on
these inputs and 128 deterministic random pairs. Distinguishing this pair
does not establish a general predictor of hardness.

## The variant with extra moves

`aut_edges` retains S20_MK2's score. After ordinary substitution expansion,
it constructs the four images in A, canonicalizes them, applies the same cap,
and inserts unseen images into the same heap. All popped states share the
same 1,000-node counter. A pop can do more work because of these extra edges.
Its certificates record generator changes explicitly; they are mixed
Aut/substitution certificates, not claimed to be ordinary-AC-only paths.

## Which efficiency improvements are active

All timed methods use the optimized compiled expansion kernel. The cut-shift
test skips a candidate before construction when its canonical result repeats
an earlier candidate from the same expansion. A per-block bitmap ensures
that discovery order and stored parents remain unchanged. Canonicalization
uses packed two-bit words and integer rotations through length 64.

The experimental search still uses a Python heap, byte keys, and a Python
parent map. It does not yet use the large-campaign compact arena. Consequently
the two-bit persistent state store, in-place arena widening, optional capture
removal, and allocation governor from that engine are not part of these
timings. Integrating the new score there is separate work before scaling
to millions of nodes. Production defaults remain S20_MK2.

## Timing interpretation

Every arm uses the same 60 input pairs, cap 48, maximum 1,000 pops, expansion
kernel, heap, deduplication, tie breaks, and parent capture. The common kernel
computes its existing feature vector even for length-only greedy. This
compares ordering rules in one implementation, not separately optimized
implementations of each rule.

The four methods run sequentially in one warmed process. Arm order rotates
by row, placing each method in each of the four positions 15 times. Library
thread counts are one. macOS still chooses the physical CPU core and its
frequency; the process cannot promise fixed-core affinity. Lowering the
scheduling priority was denied by the desktop sandbox and is recorded in
the manifest; the inherited priority was retained.

Each timing includes input validation/canonicalization, search, and successful
path reconstruction. It excludes JIT warm-up, explicit garbage collection
before a run, certificate replay, file output, and cooldown. Cooldown after
each run is at least max(0.5 seconds, that run's wall time). Both wall time
and process CPU time are recorded. This is one balanced pass, not a repeated
performance study or a million-node throughput claim.
