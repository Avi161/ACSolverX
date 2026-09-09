# AC19 full-census algorithm

## Scope

The census evaluates all 72,779 rows of `data/AC19_extended_aut_min.csv` with the
frozen `final_policy.search(pair, budget=1000)`. The input SHA-256 is
`7e220253bd0d950378d6ca6944be46ff4b77e49f30067b9ff6c6c6da82f64ae2`.
Each row receives at most 1,000 shared heterogeneous work units and no absolute
relator-length cap (`cap=None`). The donor-map transport still fails closed
before an image exceeding 100,000 symbols; `cap=None` removes the search
relator-length cutoff, not every internal resource guard. The charged units
combine image evaluations, accepted basis maps, macro work, and search pops;
they are not calibrated as CPU-equivalent heap pops.

This is a staged deterministic algorithm, not one scalar heuristic and not the
production `S20_MK2` recommendation described in the project `AGENTS.md`.

## Stage 1: strict individual-donor route, at most 250 units

Canonicalize the input pair. For each relator in order,
`strict_donor_route_fast.match` repeatedly applies the best strict
cyclic-length-reducing map among the four ordered Nielsen maps. Recognition is
limited to 64 image evaluations per attempt and the whole stage to
`min(250,budget-1)` units. Length-preserving Whitehead plateaus are not searched.
The ordered maps are `x -> xy`, `x -> xY`, `y -> yx`, and `y -> yX`,
with the other generator fixed and uppercase denoting inverse. The fast matcher
computes cyclic-length changes from signed adjacent-letter counts and builds
only strictly shortening donor images. A donor-shortening map can lengthen its
companion; it is applied to both relators and retained in the certificate.

At a strict donor endpoint, transport the entire pair through the accepted
maps. Continue only when `DONOR_NORMALIZED_BS.inspect` finds one of:

- a two-block pair with determinant `+1` or `-1`;
- a relator containing exactly one occurrence of one generator, with the
  companion satisfying the primitive compiler's unimodular abelianization
  test (determinant `+1` or `-1`);
- an accepted consecutive `BS(m,m+1)` preflight.

The remaining prepass allowance runs `mid_search.mixed_search` with general
consecutive-BS, two-block, primitive one-occurrence, and BS-preflight terminals.
This subsearch checks its terminals at popped states. A solve retains the basis
maps and mixed path. A failed route consumes its charged work.

The inspection result is only a cheap invitation to run a compiler. In
particular, BS recognition is terminal only when `bs_preflight.preflight`
finds companion stable-letter exponent `+1` or `-1` and its deterministic
cyclic Britton scan reduces every opposing stable-letter pair by an exact
divisibility pinch until one stable letter remains. Reject and integer-growth
`unknown` results are not solves.

The sufficient algebra behind accepted terminals is explicit. A unimodular
two-block exponent matrix is reduced by Euclidean row operations, each realized
by ordinary AC multiplication and conjugation. Under the determinant condition,
a one-occurrence relator is reduced to one basis letter and the companion is
cleared by conjugated donor uses. Consecutive-BS
pinches replace only exact relation factors and finish through a certified
primitive terminal. Detailed constructive proofs and replay contracts are in
[`primitive_patterns.md`](primitive_patterns.md),
[`two_block.py`](two_block.py), [`consecutive_bs.py`](consecutive_bs.py), and
[`bs_preflight.py`](bs_preflight.py).

## Stage 2: plain S20 prefix, nominally 872 units

If the donor route does not solve, restart from the original input.
`plain_search_fast.mixed_search` explores ordinary relator substitutions using

```text
L + 20*S + 2*MK
```

with no ambient Nielsen neighbors and no special terminal macros. Its allowance
is `min(872, 1000 - donor_charges)`. The restart discards the donor-stage
frontier but not its accounting. If the shared budget is exhausted here, the
row ends.

Here and in Stage 3, the score features are the rotation-invariant definitions
in [`experiments/search/heuristics.py`](../../experiments/search/heuristics.py)
and [`experiments/search/heuristic_1k.py`](../../experiments/search/heuristic_1k.py):

- `L` is the sum of the two cyclic relator lengths.
- For one relator, its knot count is zero if either generator is absent;
  otherwise it is the larger of its cyclic `x`-block and `y`-block counts.
  `MK` is the larger knot count of the two relators.
- Across both relators, collect cyclic run lengths separately for the `x/X`
  and `y/Y` generators, ignoring letter sign. `S` is the smaller of the two
  generator-wise mean run lengths (or the sole mean when one generator is
  absent).
- `W` is the minimum total-length change under the four ordered Nielsen maps,
  computed from cyclic signed-adjacency counts by `heuristic_1k.response`.
- `T` is donor-relative: it is `s-1` when a general BS donor is recognized,
  preflight rejects because no legal next pinch exists, and `s>1` stable
  letters remain; otherwise it is zero.

Thus the Stage 2 ordering is precisely the ordinary `S20_MK2` score. The later
route augments that same score with `W` and, conditionally, `T`.

## Stage 3: incumbent restart with the remaining budget

If work remains, restart from the original input again and call
`root_router.search(..., use_high_core_escape=True)` with exactly

```text
1000 - donor_charges - plain_charges
```

units. The router first computes the donor-relative stalled-BS feature.

- A positive stalled-BS feature selects ordinary substitution edges ordered by
  `L + 20*S + 2*MK + 1.5*W + 4*T`.
- Otherwise it selects the same base score without `T` and adds the four
  ambient Nielsen neighbors.

The incumbent checks every fresh generated state for a two-block terminal and
for general consecutive-BS recognition plus the exact BS preflight. When a
nonordinary route reaches a preflight-rejected BS core with at least seven
stable letters, it may spend up to 300 of the still-shared allowance on the
bounded high-core escape continuation. The continuation uses ordinary
substitutions, the same BS/two-block gates, and the `4*T` priority. Failed
continuations remain charged. Stable-power, splice-power, Christoffel,
commutator-shell, full-splice, torus, and other research gates are not enabled
by this frozen census policy.

All three stages use `cap=None`. Ordinary expansion still follows the engine's
finite neighbor construction from the current state; “no cap” does not mean an
infinite branching operation.
The input rows are Aut-minimal representatives. Search states use the engine's
cyclic/inverse relator and pair-order canonicalization; they are not projected
onto the full automorphism quotient after every move. The generator neighbors
therefore explore distinct representatives inside those equivalence classes.

## Certificates

Search paths may mix relator substitutions and ambient Nielsen maps. Ambient
maps are not silently treated as AC moves. The compact elementary decoder
carries the inverse cumulative automorphism, transports each later conjugator,
emits exact canonicalization witnesses, and Nielsen-reduces the terminal basis.
Its unary-block accumulator preserves the pair at every multiply boundary.

For each solved census row, the runner immediately calls
`certificate_decoder_compact_moves.decode_elementary`, then independently
replays the emitted ordinary invert/swap/conjugate/multiply sequence with
`certificate_decoder.replay_elementary`, requiring literal `(x,y)`. The mixed
states and steps are stored; the much larger expanded move array is discarded.
See [`CERTIFICATE_DECODER_COMPACT_MOVES.md`](CERTIFICATE_DECODER_COMPACT_MOVES.md)
and [`FULL_CENSUS_PREFLIGHT.md`](FULL_CENSUS_PREFLIGHT.md).

## Reproducing the census

The original execution used a private `.scratch` snapshot so edits could not
change a running interval. That snapshot is provenance only and is not shipped.
The published branch contains the 43 dependencies hashed in
[`FINAL_PORTABILITY_CHECK.json`](FINAL_PORTABILITY_CHECK.json), plus the census
runner itself. At invocation the runner verifies those 43 hashes and adds its
own hash, producing the same 44-file source manifest recorded by the original
execution.

The recorded interpreter was CPython 3.14.3. Create a virtual environment
and install the pinned minimal dependencies before running the commands below:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r research/supermoves_20260908/requirements-census.txt
```

From the published branch checkout, reproduce into a new directory. Published
manifests and shards deliberately refuse overwrites. One invocation can process
the complete census:

```bash
PYTHONPATH=. .venv/bin/python -m research.supermoves_20260908.run_full_ac19_final1k \
  --input data/AC19_extended_aut_min.csv \
  --out results/heuristic_search/ac19_final_policy_full_1k_reproduction \
  --offset 0 --limit 72779 --cpu-slice 2 --cooldown 6 --shard-size 1000
```

The recorded publication run used two invocations, a 250-row pilot followed by
the remaining 72,529 rows. This changes interval manifests and cooldown timing,
not the deterministic per-row policy.

Rows run serially with `NUMBA_NUM_THREADS`, `OMP_NUM_THREADS`, and
`OPENBLAS_NUM_THREADS` fixed to one. After approximately two process-CPU
seconds, the runner sleeps six wall seconds after the current row. Search and
certificate wall/CPU clocks exclude cooldown; invocation elapsed includes
cooldown and excludes separately recorded warmup. Each finalized shard is
atomically renamed and followed by a cumulative invocation summary.

After all shards finish, aggregate with the current research-tree verifier:

```bash
PYTHONPATH=. .venv/bin/python -m research.supermoves_20260908.summarize_full_ac19_final1k \
  --input data/AC19_extended_aut_min.csv \
  --result-dir results/heuristic_search/ac19_final_policy_full_1k_reproduction
```

Aggregation fails closed on gaps, overlaps, partial files, source disagreement,
errors, unverified solves, charge excess, or inconsistent terminal invocation
summaries. It writes `SUMMARY.json`, `unsolved.csv`, and the standalone final
report at
[`results/heuristic_search/ac19_final_policy_full_1k/RESULTS.md`](../../results/heuristic_search/ac19_final_policy_full_1k/RESULTS.md).

## Minimal publication bundle

The runtime beyond Python's standard library is NumPy, Numba, and llvmlite;
the audited local environment used NumPy 2.4.6, Numba 0.66.0, and llvmlite
0.48.0. A minimal reproducibility environment should pin those versions rather
than presenting the repository's broader `requirements.txt` as necessary for
this algorithm.

Publish the final three aggregate files (`SUMMARY.json`, `RESULTS.md`, and
`unsolved.csv`) from
`results/heuristic_search/ac19_final_policy_full_1k/`, every finalized
`results/heuristic_search/ac19_final_policy_full_1k/rows_*.jsonl` certificate
shard, every corresponding `rows_*.summary.json` terminal shard summary, and
every `manifest_*.json` interval manifest in that directory. Also publish the
byte-exact `data/AC19_extended_aut_min.csv` input and its
path-specific `.gitattributes` rule,
[`run_full_ac19_final1k.py`](run_full_ac19_final1k.py),
[`summarize_full_ac19_final1k.py`](summarize_full_ac19_final1k.py), and
[`FINAL_PORTABILITY_CHECK.json`](FINAL_PORTABILITY_CHECK.json). Also publish
this algorithm document and the
six certificate/proof dependencies linked above: `primitive_patterns.md`,
`two_block.py`, `consecutive_bs.py`, `bs_preflight.py`,
`CERTIFICATE_DECODER_COMPACT_MOVES.md`, and `FULL_CENSUS_PREFLIGHT.md`.
Raw expanded elementary move
arrays are unnecessary because every saved mixed certificate is reconstructible
and was independently replayed during the run. A publication report should
state the exact input hash, source hashes, 1,000-unit heterogeneous budget,
`cap=None`, verified-solve count, zero-error check, route counts, search and
certificate clocks, cooldown-inclusive elapsed time, and the fact that this is
a research-branch census rather than a change to the main production default.
