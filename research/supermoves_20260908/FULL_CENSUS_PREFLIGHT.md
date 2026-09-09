# Full AC19 census preflight

This is the pre-run design audit. The implemented runner retains mixed states
and steps for every solve, while discarding expanded elementary arrays, so a
saved certificate can be decoded later without repeating the search. It clears
`_bs_patterns_for_length` at each finalized shard boundary. The implemented
contract and exact reproduction commands are in
[`AC19_FULL_CENSUS_ALGORITHM.md`](AC19_FULL_CENSUS_ALGORITHM.md).

## Input and policy contract

The run must read exactly 72,779 unique rows from `AC19_extended_aut_min.csv`
and verify the settled input SHA-256
`7e220253bd0d950378d6ca6944be46ff4b77e49f30067b9ff6c6c6da82f64ae2` before
search. `final_policy.search(pair,budget=1000)` enforces the total mixed-unit
limit internally. The stages share that limit: strict-donor image evaluations
and accepted maps, plain S20 prefix, then the original-input incumbent restart.
No relator-length cap is used. These units are not calibrated CPU-equivalent
heap pops.

Rows should run serially. A completed-row CPU batching limit and cooldown can
control heat, but neither is a per-row timeout. Resume metadata must retain the
next offset, input hash, source hashes, and exact count of completed rows.

## Long-lived memory audit

Search heaps, parent maps, paths, and strict-donor attempt records are local to
one row and become collectible after its record is reduced. Each row is limited
to 1,000 charged units, though uncapped words can make an individual state
large. Loading 72,779 short CSV rows and their unique-name set is modest; it is
not the main memory risk.

Persistent recognizer caches are:

- `bs_preflight`: LRU 16,384;
- `stable_power` and `splice_power_family`: LRU 16,384 each;
- `cheap_gates._canonical_two_block_row` and `one_occurrence_donor`: LRU
  16,384 each;
- `donor_template_registry`: ordered cache limited to 16 registries.

`cheap_gates._bs_patterns_for_length` is the exception: it uses
`lru_cache(maxsize=None)`. Its key is only a word length and each value is a
small fixed donor table, so the current AC19 risk is much smaller than a cache
of states, but it is formally unbounded for a long-lived uncapped process.
Clear recognizer caches at deterministic batch boundaries, or bound this cache,
and record that policy. Clearing between batches changes runtime only, not
search ordering or results.

Python may retain allocator arenas after a difficult row even when row-local
objects are dead. Record RSS/high-water telemetry per batch if available and
restart from the next offset on a declared threshold; do not treat retained RSS
alone as a logical state leak.

## Cheapest trustworthy coverage verification

Do not store full `elementary_moves` arrays in the census JSONL. Some verified
certificates contain thousands of moves, so retaining all arrays can dominate
disk, serialization time, and memory. For each solved row:

1. decode immediately with `certificate_decoder_compact_moves.decode_elementary`;
2. independently replay the returned moves with
   `certificate_decoder.replay_elementary` and require exact `(x,y)`;
3. record only the presentation name, solved flag, policy route, charged units,
   certificate move count, decode/replay clocks, and a SHA-256 of the canonical
   compact move JSON if an audit fingerprint is desired;
4. discard the moves, states, steps, and full `result` before the next row.

The compact decoder already performs the trusted fast decoder's internal replay;
the second replay uses the separate elementary implementation and is worth
retaining for a census claim. This has the same proof standard as the saved
development artifacts without writing the large move arrays. A later request
for selected certificates can rerun those exact names under the pinned input
and source hashes.

Write one minimal record for every input, including failures, then atomically
rename a same-directory `.partial` file only at a clean batch boundary. Validate
the final file for 72,779 unique names, exact source-name equality, every charge
at most 1,000, `solves == verified_certificates`, and summary totals recomputed
from the JSONL rather than trusted from mutable in-process counters.

## Existing runner caveat

`run_final_policy.py` currently writes the complete search result and full
elementary move array for every solve. That is appropriate for small audit
panels but unnecessarily expensive for census counting. Its serial execution,
source hashing, duplicate/alphabet validation, immediate two-decoder replay,
atomic partial output, and offset metadata are sound pieces to preserve in a
count-only runner.
