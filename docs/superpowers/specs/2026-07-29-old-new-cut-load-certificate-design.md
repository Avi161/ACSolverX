# Old--New Cut Grouped-Load Certificate Design

Date: 2026-07-29

## 1. Purpose and theorem boundary

The next deliverable is a finite, independently replayable certificate for the
only unresolved positive-chamber identity in the period-two argument:

\[
  \mathbb B(A_{n+1,d},b_{n+1,d})
  =\mathbb B(A_{n,d},b_{n,d}) \qquad (n\ge 0,\ d\ge 1).
\]

The endpoint-potential reduction has already reduced this claim to six family
parities.  The certificate will materialize those parities as 9,408
source-fiber/cell loads carrying 17,760 old-occurrence histograms.  It will
bind raw provenance through integral collision fibers and compress the
1,491,840 active comparisons instead of serializing every pair as a separate
JSON object, which previously ran too slowly and overheated the machine.

This certificate is not, by itself, an AC or stable-AC trivialization of
AK(3).  It is one lemma in the current proof route.  It must not assert the
unproved formula `Q(A_(n,d))=[d=0]`, and it must not treat the `d=0` endpoint
branch as closed.

## 2. Considered approaches

### A. Grouped load histograms with independent replay (selected)

Aggregate the old source rows by integral collision fiber before parity, then
record one load row for each surviving source fiber and threshold cell.  For
every old occurrence in that load's exact footprint, store a complete
partition of its comparisons with the 84-token collision-first word
`T=b_(n,d)`.  Stable token masks and computed counts bind the compact
histograms to every underlying comparison.  A separate verifier reconstructs
the rows and comparisons without importing generator logic.

This approach retains every proof obligation while keeping the executable
artifact small enough for a guarded 30-second run.

### B. Full raw pair ledger (rejected)

Serialize every atomic comparison directly.  This is superficially simple,
but the prior attempt produced 1,491,840 records, serialized inside nested
loops, exceeded the safe runtime, and caused sustained CPU use.  It adds no
mathematical information beyond the grouped partition.

### C. Pure symbolic involution (rejected for the present route)

The residual P rays satisfy an exact conjugacy, but the conjugating map is
neither shortlex preserving nor shortlex reversing and does not preserve the
84-token occurrence action.  The three Q pairs likewise have unequal
contexts.  These exact counterexamples rule out the currently named uniform
involution ansatz; they do not rule out a future deeper theorem.

## 3. Artifacts and isolation

All implementation remains isolated to the existing new scratch files and
package-v2 output boundary.

- `.scratch/period_two_old_new_cut_load_certificate.py` streams the canonical
  root index and seven content-addressed shards from approved source
  artifacts.
- `.scratch/period_two_old_new_cut_load_verify.py` independently reconstructs
  and verifies package v2.  It must not import the generator.
- `.scratch/test_period_two_old_new_cut_load_certificate.py` contains literal,
  hand-derived fixtures and bounded generator/verifier tests.
- `.scratch/period-two-old-new-cut-package-v2/index.json` is the production
  package root.  Its seven shards live under its sibling `objects/` directory.
- `.scratch/period_two_old_new_cut_load_certificate.md` may state the proved
  theorem, dependency hashes, replay command, and explicit nonclaims only
  after independent production replay in Task 6.

The interrupted
`.scratch/period_two_old_new_cut_covariance_checker.py` is not a trusted
dependency.  It may be consulted for schema notation, but no zero failure
counter, claimed family value, or `d=0` assertion may be copied as evidence.

Task 2 implements only generator-side iterators, bounded two-phase family
generation, the JSONL stream writer, a deterministic generator-only resource
projection, and a pure generation-receipt payload constructor.  Task 2 tests
write no production package, receipt file, attestation, theorem memo, or
promise-ledger entry.  Independent semantic replay belongs to Task 3,
coordinator-owned durable receipt writing belongs to Task 4, the actual
preflight and combined gate belong to Task 5, and the production run belongs
to Task 6.

## 4. Source binding

The shared shard carries SHA-256 bindings for every executable source and
upstream data artifact used to reconstruct a row.  Loading fails if any
required path is missing or any expected source theorem status is not
verified.  The canonical `source_bindings` value has exact fields `format`,
`old`, `b`, and `sha256`.  Its format is
`task4-source-bindings-v1`; `sha256` is the SHA-256 of canonical JSON for the
other three fields.

The `old` object is the complete proof object returned by `build_old_rows()`.
It contains `raw_family_rows`, `active_family_fibers`, `integral_fibers`,
`one_member_sources`, `anchor_rows`, `anchor_integral_sum`,
`anchor_provenance`, `missing_raw_provenance`, `raw_provenance_counts`,
`raw_ids_unique`, and `source_digests`.  `integral_fibers` has the exact
families `base`, `P`, `C`, and `Q`, including inactive fibers.  Every fiber
stores `collision_key`, aligned `member_ids` and `coefficients`, a `members`
table whose rows contain `id`, integer `coefficient`, exact `domain`, and exact
`current_equality`, then `integral_sum`, `parity`, `active`, and the
`label_equality_witness`.  The redundant aligned arrays and member table must
agree exactly.  `one_member_sources` has the exact families `fixed` and
`singleton`; every record contains its stable `identity`, one `member_id`,
integer `coefficient`, exact `domain`, and exact `current_equality`.  Active
load rows alone are not a source certificate.

The `b` object is the complete proof object returned by `build_b_catalog()`.
It contains `occurrences`, `path_fibers`, `active_path_fibers`,
`slot_zero_tokens`, `bound_cells`, `collision_fibers`, and `source_digests`.
All 53 B collision fibers are present, including inactive fibers.  Every one
stores sorted `members`, aligned integer `coefficients`, explicit
`member_coefficients` pairs, `integral_sum`, `parity`, `active`, `slot`,
`canonical_module_schema`, and the complete `label_equality_witness`.

The doubled slot-zero anchor binds all 21 approved provenance rows as exact
`id`/integer-`coefficient` pairs, their computed integral sum, the raw V/W/A
provenance counts, raw-ID uniqueness, and the exact empty
missing-provenance result.  Evenness and completeness are computed from those
rows rather than asserted in prose.

## 5. Cell decomposition and pumping witnesses

Threshold cells use the states `0`, `1`, `2`, and `ge3`, with base value 3
for `ge3`.

- Fixed, base, singleton, and C families use the 16 `(a,n)` cells.
- P uses the 54 nonempty `(a,h,r)` cells in the domain `h+r>=a`.
- Q uses the 64 `(h,k,n)` cells with `a=h+k`.

The package binds every one of the 48,252 powered schema/cell identities but
does not repeat its full tagged word.  Each family catalog stores:

- one ASCII-sorted schema table containing schema IDs, variables, and blocks;
- one ASCII-sorted cell table containing names, states, and base values;
- a first-seen-in-identity-order table of distinct compact witnesses;
- one witness-table index for every schema-major/cell-minor identity; and
- exact identity, replay, and catalog SHA-256 values with versioned ordering
  and typed-encoding declarations.

The exact catalog fields are `format`, `typed_encoding`, `family`,
`field_orders`, `identity_order`, `schema_count`, `cell_count`,
`template_count`, `witness_count`, `schema_table`, `cell_table`,
`witness_table`, `identity_witness_ids`, `identity_sha256`, `replay_sha256`,
and `catalog_sha256`.  `typed_encoding` is
`task4-typed-sha256-v1`.  Unknown or missing fields fail closed.  Schema and
cell IDs must be nonempty ASCII strings in strict ASCII order.  Every witness
must be used, and `witness_table` must equal the distinct witnesses in their
first-seen schema-major/cell-minor identity order; a semantic-preserving table
permutation and reindexing is noncanonical and is rejected.

The validator checks the complete positional grammar before any digest.
Schema variables are lists of strings.  Each block is exactly
`[block_name, word, affine]`, with a string name, a list of non-boolean
integers, and either `null` or an aligned list of non-boolean integers.  Cell
names are lists of strings; states are aligned lists over `0,1,2,null` with
booleans rejected; base values are aligned non-boolean integers and equal the
state, or three for `null`.  Each witness is exactly
`[terminal, terminal_deleted, pumps]`, where the terminal is a non-boolean
integer or `null`, the deletion field is an actual boolean, and pumps is a
list.  Each pump has exactly eight fields in the declared order; every scalar
is a non-boolean integer and slopes is an aligned list of non-boolean
integers.  Pump block indices, affine values, slopes, copy IDs, core offsets,
split ordering, and schema/cell variable alignment are checked against the
dereferenced schema and cell.  Recomputing all hashes cannot authenticate a
malformed nested record.

For the typed encoder `E`, `N` encodes `None`; `B` followed by byte `00` or
`01` encodes a boolean; `I || len4 || payload` encodes a signed integer using
its canonical ASCII decimal spelling; and `S || len4 || payload` encodes a
UTF-8 string.  `L || count4 || E(item)...` encodes a list.  A mapping has only
string keys and is encoded as `M || count4 || E(key) || E(value)...`, with
keys ordered by their UTF-8 bytes.  Every `len4` and `count4` is an unsigned
four-byte big-endian integer.  Tuples are encoded as lists.  No other Python
type is accepted.

Let `||` denote byte concatenation.  Both rolling hashes begin with this exact
ordered prefix:

```text
E(format) || E(typed_encoding) || E(family) || E(field_orders) ||
E(identity_order) || E(schema_count) || E(cell_count) ||
E(template_count) || E(witness_count) || E(schema_table) ||
E(cell_table) || E(witness_table)
```

For identity position `i`, let
`schema_index,cell_index = divmod(i, cell_count)`, let `witness_id` be
`identity_witness_ids[i]`, let
`M_i = E([schema_index, cell_index, witness_id])`, and let
`D_i = E(witness_table[witness_id])`.  Then `identity_sha256` is SHA-256 of
the prefix followed by `M_0 || ... || M_(template_count-1)`, while
`replay_sha256` is SHA-256 of the prefix followed by
`M_0 || D_0 || ... || M_(template_count-1) || D_(template_count-1)`.
`catalog_sha256` is SHA-256 of canonical JSON for every catalog field except
`catalog_sha256` itself.

A compact witness contains the full pre-`cvert` terminal letter, the
terminal-`c` deletion branch, and for every changing block its block index,
base copy count, slopes, split position, consecutive copy IDs, and boundary
core offsets.  Schemas and cells are stored once; each of the 48,252
identities stores only its witness index.

The independent verifier reconstructs, for every identity, the nonempty,
reduced, cyclically reduced primitive cores, affine exponents and nonnegative
slopes, tagged fully reduced base word, normalized blocks, intact and distinct
boundaries, and terminal branch.  It then requires the reconstructed compact
witness and ordered replay digest to match.  A digest match alone is not a
proof: reconstruction and every structural check precede digest comparison.

The load histograms separately record each comparison discharge: strict
affine length, identical normalized block list, or common pumped prefix
followed by a fixed mismatch.

The only primitive cores expected in the concrete schemas are
`ctcTTTct` and `cTctttcT`, both of reduced cyclic length eight.  The verifier
rechecks this fact from letters and does not trust the recorded booleans.

The verifier also proves that the listed cells are disjoint and cover the
whole stated orthant.  It checks P-domain nonemptiness algebraically rather
than by sampling.

The exact family identity counts are 3,072 fixed, 2,048 base, 2,064
singleton, 11,772 P, 3,824 C, and 25,472 Q, totaling 48,252.  Dropping one
identity, redirecting it to another valid witness, or changing a schema, cell,
boundary, or terminal field must be rejected after all enclosing digests are
recomputed.

## 6. Load-row representation

The endpoint reduction predicts the following census.  These values remain
**[unverified]** until the new generator derives them from the bound sources
and the independent verifier reproduces them:

| family | rows/cell | cells | source loads | footprint/load | occurrence-loads | comparisons |
|---|---:|---:|---:|---:|---:|---:|
| fixed | 70 | 16 | 1,120 | 1 | 1,120 | 94,080 |
| base | 2 | 16 | 32 | 2 | 64 | 5,376 |
| singleton | 1 | 16 | 16 | 6 | 96 | 8,064 |
| P | 32 | 54 | 1,728 | 2 | 3,456 | 290,304 |
| C | 39 | 16 | 624 | 2 | 1,248 | 104,832 |
| Q | 92 | 64 | 5,888 | 2 | 11,776 | 989,184 |
| total |  |  | **9,408** |  | **17,760** | **1,491,840** |

Each source load names its integral collision fiber, cell, module/label
schema references, and complete old occurrence footprint.  A footprint entry
names its occurrence, polarity, literal AST leaf, module schema, and label
schema; a fixed entry instead names its literal leaf and has no occurrence.
Every footprint entry is compared with exactly 84 collision-first B-tokens,
giving the predicted **[unverified]** workload
`17,760 * 84 = 1,491,840` comparisons.

Raw provenance rows remain bound by the integral-fiber records in Section 4,
and bilinearity proves that even fiber sums contribute zero.  The compact
certificate need not serialize one object for every comparison: each grouped
load retains the source fiber, while one histogram per occurrence retains the
complete active comparison partition.  It must compute the raw-fiber, source
load, occurrence-load, and comparison censuses so a missing occurrence cannot
masquerade as compression.

For each footprint occurrence, the 84 comparisons are partitioned into
histogram buckets keyed by:

- stable B-token source class and coordinate;
- equality exclusion;
- occurrence polarity;
- unsigned module comparison method and result;
- polarity-adjusted chronology result;
- transported-label comparison method and result; and
- final contribution bit.

Each bucket stores its count and an 84-bit token mask.  Masks must be disjoint
and have union `(1<<84)-1` for each footprint occurrence.  The independent verifier
recomputes every mask and bucket key from the bound source data.  Thus the
histogram is compact, but omitting, duplicating, or reclassifying an atomic
comparison is detectable without storing 1.49 million JSON objects.

## 7. Family aggregation and success condition

All values are computed by xor from the load rows.  The endpoint reduction
predicts the following **[unverified]** family table; a mismatch is a failed
proof attempt, not a constant to update:

- fixed: zero on all 16 cells;
- base: zero on all 16 cells;
- singleton: one on all 16 cells;
- P: zero on all 54 admissible cells;
- C: one exactly on the four cells with `a=0`, zero on the other 12; and
- Q: zero on all 64 cells.

The generator exits nonzero and does not write a success memo if any source
binding, pumping witness, histogram partition, comparison replay, row count,
cell coverage, or family value fails.  There are no hard-coded zero failure
counters.

If every generator check passes and Task 3 independently reconstructs the
same values, the replayed package proves

\[
  \mathbb B(A_{n,d},b_{n,d})=1+[d=1]=[d>1]
  \quad(n\ge0,\ d\ge1),
\]

and therefore the positive-chamber old--new cut covariance identity.

## 8. Verification and resource contract

Development follows strict red-green-refactor cycles.  Expected values in
tests are literal hand-derived fixtures, never values computed through the
generator.  The independent verifier has separate free-reduction,
shortlex-comparison, affine, collision, and parity code paths.

Every proof/test command runs through `scripts/run_proof_guarded.py` with one
job, a 30-second deadline, and the guard's one-thread environment.  A timeout
is a design failure: profile or reduce allocation, do not rerun unchanged and
do not raise the timeout above 60 seconds.  No detached or background process
is permitted.

The final gate requires, in order:

1. focused unit tests;
2. canonical package generation;
3. byte-for-byte regeneration;
4. independent package replay;
5. mutation checks for a changed token mask, coefficient, boundary tag,
   family parity, and dependency digest;
6. a fresh stale-process scan; and
7. hostile mathematical review of the produced theorem claim.

The compact overhead scout samples every eighth ASCII-sorted schema plus
**every** schema attaining that family's maximum pump count.  It reports the
complete sorted maximum-ID list; selecting only the first tied maximum is not
an approved projection because tied schemas can intern different witnesses
and emit different byte counts.

## 9. Package-v2 replacement boundary

The monolithic logical-v1 JSON object is retired as a production transport.
Its computation completed all 1,491,840 comparisons and atomically wrote
371,878,372 bytes, but the enclosing guarded test timed out.  It must not be
run again.  Package v2 preserves the logical-v1 value while replacing only its
wire layout and publication protocol.

The wire format is `period-two-old-new-cut-package-v2`.  A package consists of
one canonical root-index JSON line and seven content-addressed canonical JSONL
objects.  The shard order is exactly:

    shared, fixed, base, singleton, P, C, Q

The family order is exactly:

    fixed, base, singleton, P, C, Q

Production uses scope `production-full` and status
`generated-awaiting-independent-replay`.  Preflight uses scope
`preflight-sample` and status `preflight-sample-not-a-certificate`.  A
preflight package is never a proof artifact, even if all of its local checks
pass.

The canonical line encoding is `canonical-json-ascii-lines-v1`: JSON is
serialized with `ensure_ascii=True`, sorted object keys, separators
`(",", ":")`, and exactly one terminal LF.  The maximum canonical line is
16,777,216 bytes including LF.  Package size is the sum of all seven actual
shard byte lengths and the actual root-index byte length.  Production
publication is forbidden above 100,000,000 bytes.

Objects live beside the index under `objects/<sha256>.jsonl`, where the name is
64 lowercase hexadecimal digits and the digest covers the complete object,
including every LF.  Production uses
`.scratch/period-two-old-new-cut-package-v2/index.json`.  Preflight and tests
use project-local sibling directories and never `/tmp`.

## 10. Root index and descriptor grammar

The root object has exactly these fields:

    format
    scope
    logical_v1_format
    canonical_encoding
    mask_encoding
    domain
    status
    shard_order
    shards
    shard_bytes_total
    emitted_summary
    full_summary
    source_bindings_sha256
    b_identity_digest
    template_catalogs
    root_sha256

Their fixed values include logical format
`period-two-old-new-cut-load-v1` and mask format
`uint84-be11-base64url-nopad-v1`.  `shards` is a seven-entry array in
`shard_order`.  A shared descriptor has role `shared` and family `null`; a
family descriptor has role `family` and its exact family name.  Each
descriptor has exactly:

    role, family, path, sha256, total_bytes, record_count, record_counts

`path` is exactly `objects/<descriptor sha256>.jsonl`.  `total_bytes` includes
all LFs.  `record_counts` contains every allowed tag for that shard, including
zero counts, no other key, and sums to `record_count`.
`shard_bytes_total` is the descriptor-byte sum.  `source_bindings_sha256` is
the digest inside the exact source-binding object and `b_identity_digest` is
the logical-v1 digest.  `template_catalogs` maps every family to an exact
ten-field catalog summary:

    format, typed_encoding, identity_order, schema_count, cell_count,
    template_count, witness_count, identity_sha256, replay_sha256,
    catalog_sha256

The summary schema for both `emitted_summary` and `full_summary` is exactly:

    load_rows, total_load_rows, footprint_sizes, occurrence_loads,
    total_occurrence_loads, b_tokens_per_occurrence, active_comparisons,
    template_counts, total_templates

Every family-valued subobject has all six family keys.  Production requires
`emitted_summary == full_summary`.  Preflight records the actually emitted
subset in the former and the deterministic full projection in the latter.

`root_sha256` is SHA-256 of the canonical root-index line with that one field
omitted.  The SHA-256 of the actual index file is separately computed over the
complete canonical line with `root_sha256` present.  Neither digest is a
self-hash.

## 11. Shared-shard positional grammar

The six shared tags, exact field orders, and total widths are:

    shared_header 9 =
      tag, format, scope, logical_v1_format, canonical_encoding,
      mask_encoding, domain, status, shard_order
    dependency 3 =
      tag, path, sha256
    source_bindings 2 =
      tag, value
    b_identity 11 =
      tag, token_index, token_id, source_class, coefficient, slot,
      occurrence, polarity, module_schema, label_schema, source_members
    b_coordinate 4 =
      tag, token_index, source_class, coordinate
    shared_footer 4 =
      tag, coordinate_count, records_before_footer, bytes_before_footer

The header is first and the footer is last.  Dependencies are in strict ASCII
path order.  The source-binding row contains the exact existing
`task4-source-bindings-v1` object, not a projection.  B identities are in
complete token-index order and retain the current ten logical fields after
the tag.  B coordinates follow token-index order and bind the source class and
coordinate used when token masks are expanded.  `coordinate_count` is the
number of coordinate rows.  `records_before_footer` and
`bytes_before_footer` count the complete prefix before encoding the footer.

The descriptor's `record_counts` has exactly all six shared tag keys.  Token
indices are exact integers, not booleans, cover `0..83` in production, and
match the identity/coordinate bijection.

## 12. Family-shard positional grammar

There are exactly thirteen family tags.  Their field orders and widths are:

    family_header 14 =
      tag, family, variables, source_cell_count, selected_old_indices,
      old_load_count, footprint_count, bucket_class_count, b_token_count,
      comparison_methods, chronologies, histogram_key_fields,
      template_field_orders, source_cell_order
    old_load 8 =
      tag, old_index, old_token_id, coefficient, source_members,
      source_slot, footprint_start, footprint_count
    footprint 9 =
      tag, footprint_index, old_index, occurrence, occurrence_slot,
      polarity, leaf, module_schema, label_schema
    bucket_class 11 =
      tag, b_source_class, b_coordinate, equality_exclusion,
      module_method, module_order, chronology, chronology_order,
      label_method, label_order, contribution_bit
    load 5 =
      tag, old_index, footprint_index, bucket_class_index, mask
    cell_footer 7 =
      tag, source_cell_index, compact_cell_index, cell_id,
      odd_old_indices, value, load_record_count
    template_header 10 =
      tag, format, typed_encoding, family, field_orders, identity_order,
      schema_count, cell_count, template_count, witness_count
    template_schema 5 =
      tag, schema_index, schema_id, variables, blocks
    template_cell 6 =
      tag, compact_cell_index, cell_id, names, states, base_values
    template_witness 5 =
      tag, witness_id, terminal_full_letter, terminal_c_deleted, pumps
    template_identity_chunk 3 =
      tag, start_identity_index, witness_id_list
    template_footer 4 =
      tag, identity_sha256, replay_sha256, catalog_sha256
    family_footer 8 =
      tag, source_cell_count, old_load_count, load_rows, occurrence_loads,
      comparisons, records_before_footer, bytes_before_footer

`comparison_methods` is exactly:

    null
    strict_affine_length
    identical_pumped_blocks
    fixed_mismatch_after_pumped_prefix

`chronologies` is exactly:

    fixed_vs_correction_literal_leaf_order
    distinct_occurrences_literal_AST_order
    equal_coordinate_excluded
    same_occurrence_increasing
    same_occurrence_decreasing

`histogram_key_fields` is exactly the current logical-v1 order:

    old_occurrence, old_leaf, b_source_class, b_coordinate,
    equality_exclusion, old_polarity, module_method, module_order,
    chronology, chronology_order, label_method, label_order,
    contribution_bit

`template_field_orders` is exactly:

    schema = schema_id, variables, blocks
    block = block_name, word, affine
    cell = cell_id, names, states, base_values
    witness = terminal_full_letter, terminal_c_deleted, pumps
    pump = block_index, base_copies, slopes, split_position, left_copy_id,
           right_copy_id, left_core_offset, right_core_offset

The source-cell order declaration is
`product-order-with-P-domain-filter`.  `source_cell_index` is that ledger
order.  `compact_cell_index` is ASCII catalog order.  They are distinct
domains; the checked cell-ID bijection is the only conversion.  Treating one
index as the other is invalid even when they happen to agree.

Old loads are ordered by `old_index`.  Their footprint intervals are
contiguous, disjoint, start at zero, and cover the complete footprint table.
`source_slot` is null if and only if the family is `fixed`.  In a footprint,
`occurrence`, `occurrence_slot`, `polarity`, and `module_schema` are all null
if and only if the family is `fixed`.  `leaf` and `label_schema` are always
present.  Production `selected_old_indices` is exactly
`[0, 1, ..., old_load_count-1]`; preflight may use a strict increasing subset.

Family generation is bounded and two-phase because the canonical
`bucket_class` table precedes every `load` record on the wire.

1. In production, Phase A traverses the exact full family domain in
   source-cell, old-index, footprint-index, and B-token order.  It derives only
   the final family-header fields, complete source/occurrence/comparison
   censuses, per-cell footer parity metadata, and the unique bucket-class
   keys.  It then freezes the bucket-class table in canonical-JSON byte order.
   It retains no load record, token mask, comparison row, logical-v1 object,
   or complete family ledger.  The registered preflight runs the same phase
   over only its literal selected-old subdomain for projection and is never a
   production certificate.
2. Phase B deterministically repeats the same comparisons, resolves each
   bucket key through the frozen table, streams nonzero load masks and cell
   footers, then streams template records and the family footer.  A missing or
   newly discovered bucket key is fatal.

There is no spool file, external sort, whole-family JSON object, or top-level
canonical JSON serialization in either phase.

Production selected-old indices are the complete ranges.  Preflight selected
old indices are the following literal arrays and no others:

    fixed     [0,8,15,23,31,38,46,54,61,69]
    base      [0,1]
    singleton [0]
    P         [0,3,5,8,10,13,16,18,21,23,26,28,31]
    C         [0,19,38]
    Q         [0,15,30,46,61,76,91]

Across the full family cell domains the sampled arithmetic is:

| family | sampled source-load/cell rows | sampled occurrence histograms | sampled comparisons |
|---|---:|---:|---:|
| fixed | 160 | 160 | 13,440 |
| base | 32 | 64 | 5,376 |
| singleton | 16 | 96 | 8,064 |
| P | 702 | 1,404 | 117,936 |
| C | 48 | 96 | 8,064 |
| Q | 448 | 896 | 75,264 |
| total | **1,406** | **2,716** | **228,144** |

Thus the selected old indices produce exactly 1,406 source-load/cell rows,
2,716 occurrence histograms, and `2,716 * 84 = 228,144` comparisons.  The
shared shard is always complete:
preflight includes every dependency, the complete source-binding object, all
84 B identities, and all 84 B coordinates.

Template serialization samples zero-based indices in each ASCII-sorted schema
table: `0,8,16,...` below that family's schema count, union every schema that
attains the family's maximum pump count.  The selection record contains the
strictly increasing selected indices and the complete sorted list of tied
maximum-pump schema IDs; selecting only one tied maximum is invalid.  Before
this filter is applied, each cold preflight fully loads sources and constructs
the complete catalog of 1,304 schemas and 48,252 schema/cell identities.  That
full fixed-cost precompute is not a serialization sample.

Bucket classes are unique and sorted by their canonical JSON encoding.
`bucket_class_index` indexes that table.  Within each source cell, load rows
are ordered by old index, footprint index, then bucket-class index.  Every
load mask is nonzero.  A cell footer closes the preceding load rows and is the
only cell boundary.  Source-cell indices are consecutive from zero in a full
package.  `odd_old_indices` and `value` are recomputed, never trusted.

Template schemas and cells are in strict ASCII ID order with consecutive
indices.  Witnesses are in first-seen schema-major/cell-minor order.  Identity
chunks contain 4,096 IDs except for one final nonempty shorter chunk; empty
catalogs contain no chunks.  Chunk starts are exact, consecutive identity
indices.  Blocks and pumps use the compact nested positional grammar already
specified in Sections 5 and 10.  The descriptor `record_counts` has all
thirteen keys and no others.

## 13. Logical-v1 reconstruction

Decoding is a pure, exact inverse of encoding.  It does not run the proof
ledger.

For one cell and one old load, combine the old-load row with each row in its
footprint interval.  Expand each `load` record through its bucket class and
decode its 84-bit mask.  The reconstructed logical-v1 bucket key inserts
`old_occurrence`, `old_leaf`, and `old_polarity` from the footprint and the
remaining ten fields from the bucket class.  Its logical-v1 `count` is the
mask population count and its logical-v1 `mask` is the 21-digit lowercase
hexadecimal spelling.

For every footprint:

    comparison_count = 84
    one_count = sum(popcount(mask) for contribution_bit == 1)
    histogram.value = one_count mod 2

Its nonzero masks must be disjoint and their union must be `(1 << 84) - 1`.
The load value is xor of its footprint histogram values.  The cell value is
xor of its selected load values.  Logical IDs are reconstructed as
`family|cell_id|old_token_id`.  The logical footprint binding is:

    token_id, source_slot, source_members, module_schema, occurrence,
    occurrence_slot, polarity, leaf, label_schema

The logical cell counts are derived:

    load_count = number of selected old loads
    occurrence_load_count = sum of selected footprint counts
    comparison_count = occurrence_load_count * 84

The template catalog is reconstructed by dropping positional tags and indices
from schema, cell, witness, and identity-chunk rows, concatenating identity
chunks, and restoring the three footer digests.  The family summary is the
three count fields from the family footer.  The top-level logical-v1 object is:

    format = logical_v1_format
    domain = root domain
    status = root status
    summary = emitted_summary
    dependency_digests = shared dependency rows
    source_bindings = shared source-binding value
    b_identity_table = shared B identities
    b_identity_digest = root b_identity_digest
    family_ledgers = six reconstructed family ledgers

Only the independent Task 3 verifier reconstructs this top-level object and
the six complete family ledgers.  Task 2 generation computes the exact values
needed by the wire records but never builds either object in memory.

The generator's tiny fixture encoder and the verifier's independent decoder
must satisfy:

    logical_v1(v2_encode(v1_fixture)) == v1_fixture

Production additionally requires emitted and full summaries to agree.

## 14. Strict canonical decoders

The generator and verifier separately implement the codecs; neither imports
the other.  Each canonical line is read incrementally in binary mode.  A
decoder rejects non-ASCII bytes, CR, blank lines, missing final LF, bytes
after a terminal footer or root record, a line above the cap, duplicate object
keys, floating-point numbers, NaN, Infinity, negative zero, and any spelling
whose re-encoding is not byte-identical.

Root decoding accepts exactly one canonical line and the exact root fields.
Shard decoding validates the tag state machine while streaming, so an unknown
tag, wrong array width, misplaced tag, record after the footer, or missing
footer fails before reconstruction.  Nested object fields are exact wherever
the schema declares them.  All integer fields use `type(value) is int`;
booleans are never accepted as integers.  Hashes, paths, IDs, enums, null
domains, and all cross-record references are validated before use.

No v2 API performs a whole production `read_text`, `read_bytes`, global
`json.loads`, `deepcopy`, or top-level canonical serialization.  Per-line JSON
decoding and bounded chunk comparisons are permitted.

## 15. Mask encoding

The wire mask is exactly fifteen characters matching
`[A-Za-z0-9_-]{15}`, with no padding.  Decode by appending exactly one `=`,
using strict URL-safe base64 validation, and requiring exactly eleven bytes.
The high four bits of the first byte are zero.  Decode/re-encode equality is
mandatory, which also rejects noncanonical unused base64 bits.  The integer is
unsigned big-endian and less than `2^84`.  Token index `i` is bit `1 << i`.
Packing is the inverse.

For every histogram fixture and production footprint, masks are nonzero,
pairwise disjoint, and cover `(1 << 84) - 1`.  The logical count is the
population count.  Reversing token-bit orientation is a mutation, not another
encoding.

## 16. Publication state machine

Publication has two explicit states.

`PREPARED` lasts until the root-index replacement.  Each shard is first
encoded to a project-local temporary object while its byte count, SHA-256,
record counts, footer prefix count, and footer prefix bytes are computed
incrementally.  A new object is flushed and fsynced, renamed to its content
address, and followed by an objects-directory fsync.  If the target object
already exists, its size and SHA-256 are verified and its bytes are compared
with the temporary object in bounded chunks.  A disagreement fails closed.
An identical object is marked reused and only the temporary is removed.

The index temporary is flushed and fsynced.  Production's actual package size
is checked before replacement.  `os.replace(temp_index, index)` is the sole
`PREPARED -> COMMITTED` transition.

Any failure before that transition preserves the prior index, removes every
temporary and only the content-addressed objects created by the current
attempt, then fsyncs each affected directory.  Reused or unrelated objects
are never removed.  Any failure after replacement leaves every object and the
new complete index in place; no object is deleted.  A post-replace directory
fsync failure returns nonzero and writes no receipt or attestation.  This is a
committed-but-unacknowledged package, not a prepared rollback.

Failure injection is defined at every boundary:

    object_temp_fsynced
    object_replaced
    objects_dir_fsynced
    index_temp_fsynced
    before_index_replace
    index_replaced
    index_dir_fsynced

Tests require prior-index survival and cleanup for every pre-replace failure,
and a complete new package with no dangling descriptor for every post-replace
failure.

## 17. Metrics, receipts, and coordinator

Metrics are opt-in and never enter package bytes.  The fixed stages are:

    encode_shared, encode_family, write_objects, publish_index, verify_package

The fixed record tags are the six shared tags, thirteen family tags, and
`root_index`.  The metrics schema contains only its format, elapsed duration
per fixed stage, and deterministic record-count and byte-count maps per fixed
tag.  It contains no command, PID, timestamp, environment value, secret, path
payload, or proof payload.  Instrumented and uninstrumented packages must be
byte- and hash-identical.

The later production CLI requires an explicit `--run-id`; it never invents
one from time or process state.  Task 2 provides a pure constructor for a
canonical generation-receipt payload with exact fields:

    format, run_id, scope, index_path, index_sha256, root_sha256, state,
    package_bytes, created_objects, reused_objects, generator_sha256, metrics

The constructor performs no filesystem operation.  Task 4 owns atomic receipt
serialization, coordinator sequencing, and the rule that a receipt may be
written only after a fully fsynced commit.  The receipt format is
`period-two-old-new-cut-generation-receipt-v1`.

The independent verifier receives the same run ID and, only after semantic
replay, may write an attestation with exact fields:

    format, run_id, index_path, index_sha256, root_sha256, logical_v1_sha256,
    status, verifier_sha256, metrics

The integrated coordinator owns the fixed run ID, production paths, receipt,
and attestation.  It rejects a stale or mismatched receipt, a preflight status,
an index/root mismatch, or any verifier output not bound to the same run.
Task 1 implements none of these production artifacts beyond the frozen
interfaces.

## 18. Projection and execution gates

Task 2 defines a deterministic `GenerationProjection` containing exact
integer nanoseconds, byte counts, schema/identity/comparison denominators,
literal selections, and projected totals.  It reports generator-only time and
package bytes.  Its format is
`period-two-old-new-cut-generation-projection-v1`.  It does not report or
estimate verifier time.

For nonnegative integers `x`, `n`, and positive `d`, the only scaling
operation is exact ceiling division:

    ceil_ratio(x, n, d) = (x * n + d - 1) // d

For each family `f`, the preflight records separate sample measurements for
the two complete comparison/generation passes and for template
serialization.  Let `C_f` and `c_f` be full and sampled comparison counts,
`I_f` and `i_f` full and sampled identity counts,
`G_f` the sampled two-pass comparison/generation nanoseconds,
`L_f` the sampled variable bucket/load bytes, `T_f` the sampled template
serialization nanoseconds, and `S_f` the sampled template bytes.  The variable
projections are exactly:

    generation_ns_f = ceil_ratio(G_f, C_f, c_f)
    load_bucket_bytes_f = ceil_ratio(L_f, C_f, c_f)
    template_ns_f = ceil_ratio(T_f, I_f, i_f)
    template_bytes_f = ceil_ratio(S_f, I_f, i_f)

All denominators must be positive and have dynamic range:
`0 < c_f < C_f` and `0 < i_f < I_f`.  Counts and bytes are never derived
through floating-point arithmetic.

The following are measured or encoded at their full size and are fixed
charges, never ratio-scaled: cold source loading and complete catalog
construction for all 1,304 schemas and 48,252 identities; the complete shared
shard time and bytes; every family header, complete old-load table, complete
footprint table, cell footers, and family footer; and the projected root-index
encoding time and bytes.  After every per-shard variable component has been
upward-rounded and added to that shard's fixed bytes, but before the final
factor-two margin, the projected index-size oracle uses the actual root
schema, those undoubled projected record counts and shard byte totals, and
valid fixed-length 64-lowercase-hex placeholders for every content digest,
object path digest, catalog digest, and `root_sha256`.  Because canonical
digest spellings have fixed length, its encoded canonical line length is the
exact projected index cost rather than an estimate.

Let `F_ns` and `F_bytes` be the sums of those fixed charges.  Task 2 computes:

    generation_ns_before_margin =
        F_ns + sum(generation_ns_f + template_ns_f for every family f)
    package_bytes_before_margin =
        F_bytes + sum(load_bucket_bytes_f + template_bytes_f for every family f)
    projected_generation_ns = 2 * generation_ns_before_margin
    projected_package_bytes = 2 * package_bytes_before_margin

The factor two is applied once, after every fixed and upward-rounded variable
component has been summed.  No component is doubled separately.

Task 3 supplies an independent verifier-time projection.  Task 5 runs the
actual 60-second preflight and blocks production unless Task 2's projected
generator time plus Task 3's projected verifier time is at most
`600_000_000_000` integer nanoseconds and Task 2's projected package bytes,
including the exact projected index, are at most 100,000,000.  No
floating-point conversion participates in either gate.  The immutable actual
package cap remains separately enforced at publication.

Only the procedural root launcher may run the later long gate.  Before any
production experiment, the implementation, tests, design, plan, and bounded
preflight result must be committed, entered in the UTC push log, and pushed.
The 600-second run uses the proof guard's authorized long mode after the exact
preflight succeeds.  A timeout or nonzero result is a bounded failure, not a
mathematical negative.

Cleanup removes preflight indexes, their current-created unreferenced objects,
test directories, and stale temporary files by exact path.  It never
garbage-collects the production object store or donor artifacts.

## 19. Required mutations and reviews

Foundation mutations cover every declared field/tag/width/order, zero-count
descriptor keys, bool-as-int, source/compact index confusion, selected-index
gaps, footprint overlap/gaps, reference ranges, identity chunk sizes, root and
object hashes, descriptor paths/counts/bytes, duplicate JSON keys, floats,
constants, negative zero, whitespace, CR, blank/missing/trailing bytes, line
caps, every mask malformation, token-bit reversal, object reuse mismatch,
every publication boundary, cap enforcement, and metrics byte identity.

Streaming-generation mutations fail closed after resealing enclosing digests
for every Section 4 source-binding obligation:

- raw family rows, exact raw provenance and counts, raw-ID uniqueness, and the
  exact empty missing-provenance result;
- every inactive and active old integral fiber; aligned member IDs,
  coefficients, and member tables; integer sums before parity; parity and
  activity; exact domains and `current_equality` values; complete label
  witnesses; and every fixed/singleton one-member record;
- all 21 anchor ID/coefficient pairs, their integral sum, and their exact
  V/W/A provenance;
- all 53 B collision fibers including inactive fibers; aligned members,
  coefficients, and member-coefficient pairs; integer sums, parity, activity,
  slot, canonical module schema, and complete label witness;
- the complete 84-token identity/coordinate bijection, including token
  indices, IDs, source classes, coefficients, slots, occurrences, polarities,
  module schemas, label schemas, source members, coordinates, and all source,
  chronology, identity, and catalog digests; and
- every exact domain, cell coverage relation, current equality, family
  census, and derived parity.

Every generated footprint is independently mutation-tested for exactly 84
token comparisons, nonzero masks, pairwise disjointness, full union
`(1<<84)-1`, count/popcount equality, bit-`i` orientation as `1<<i`,
recomputed bucket key and contribution bit, and the derived family/census
parity.  A bounded test monkeypatches `build_manifest` to raise and requires
every Task 2 adapter, iterator, projection path, and receipt-payload
constructor to continue to pass.

Independent verification repeats semantic reconstruction without generator
imports.  Whole-package review checks source binding, integer-before-parity
aggregation, all-power pumping, mask completeness, family arithmetic,
resource projections, receipt binding, and theorem scope.

## 20. Preserved nonclaims

Package v2 is a transport and replay boundary, not new mathematics.  The tiny
fixture proves only codec and publication mechanics.  A preflight package is
not a certificate.  A production package with status
`generated-awaiting-independent-replay` is not independently verified.  A
receipt is not an attestation, and an attestation is not an AC move sequence.

Nothing here proves `Q(A_(n,d))=[d=0]`, closes the `d=0` endpoint, extends the
cut outside `n>=0,d>=1`, proves full covariance without integration, or proves
AC or stable-AC triviality of AK(3).  Donor artifacts and the proof guard are
outside this package and remain unchanged.  The MMS02 donor route remains
separate and untouched.
