# Old--New Cut Grouped-Load Certificate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the retired monolithic logical-v1 transport with a fail-closed, independently replayable package-v2 root index and seven streaming content-addressed shards, then use it to certify the positive-chamber old--new cut identity.

**Architecture:** A streaming generator reconstructs approved old rows and the 84-token B-factor, emits one shared plus six family JSONL shards, and commits a canonical root index through a PREPARED/COMMITTED state machine. A separately implemented verifier decodes the same wire grammar, reconstructs the exact logical-v1 object and every semantic obligation, and produces an attestation only after independent replay.

**Tech Stack:** Python 3.9-compatible standard library, existing project-local period-two proof modules, pytest, Ruff 0.16.0, and `scripts/run_proof_guarded.py`.

## Global Constraints

- Modify only the design, plan, generator, verifier, focused test, and the old--new promise-ledger section authorized by the package-v2 task; do not modify solvers, proof guard, notebooks, donor artifacts, or canonical production manifests during foundation work.
- Never import `.scratch/period_two_old_new_cut_covariance_checker.py` as a trusted dependency.
- The independent verifier must not import the generator.
- Do not assert `Q(A_(n,d))=[d=0]`; the certificate domain is exactly `n>=0, d>=1`.
- Treat the 9,408 source-load census, 17,760 occurrence-load census, 1,491,840 active comparisons, and six family values as `[unverified]` until both generator and independent replay pass.
- Run every test, checker, linter, compiler, or proof command in the foreground through `scripts/run_proof_guarded.py`, with one job and a 30-second deadline; never exceed 60 seconds.
- Never rerun an unchanged timed-out command. Reduce allocation or simplify the algorithm first.
- Never write temporary artifacts under `/tmp`; use `.scratch/test-artifacts/old-new-load/`.
- Keep Python 3.9 compatibility: no `zip(..., strict=True)` and no mode-0644 shebangs.
- Before each push, follow the two-commit timestamp/SHA log protocol in `AGENTS.md`.
- Package v2 is `period-two-old-new-cut-package-v2`; logical reconstruction is `period-two-old-new-cut-load-v1`.
- Shard order is `shared, fixed, base, singleton, P, C, Q`; family order is `fixed, base, singleton, P, C, Q`.
- Production is `production-full / generated-awaiting-independent-replay`; preflight is `preflight-sample / preflight-sample-not-a-certificate`.
- Canonical lines are ASCII JSON with sorted object keys, compact separators, and exactly one LF; reject lines above 16,777,216 bytes including LF.
- Masks use `uint84-be11-base64url-nopad-v1`; package size, including the actual index, is capped at 100,000,000 bytes before production replacement.
- Generator and verifier codecs are independent and neither module imports the other.

---

## Package-v2 File Map

- Modify `.scratch/period_two_old_new_cut_load_certificate.py`: independent
  generator-side wire constants/codecs, streaming generator, publication, and
  pure generation-receipt payload construction. Durable receipt writing is
  Task 4.
- Modify `.scratch/period_two_old_new_cut_load_verify.py`: independently
  declared wire constants/codecs, package reconstruction, semantic replay, and
  verifier attestation. It never imports the generator.
- Modify `.scratch/test_period_two_old_new_cut_load_certificate.py`: literal
  wire vectors, fixture round-trip, atomicity injection, production adapters,
  verifier mutations, and coordinator tests.
- Modify `docs/superpowers/specs/2026-07-29-old-new-cut-load-certificate-design.md`:
  frozen package-v2 architecture and preserved nonclaims.
- Modify this plan: executable seven-checkpoint v2 sequence.
- Task 2 does not modify `docs/AK3_PROMISE_LEDGER.md`. Later durable-evidence
  and theorem checkpoints may modify only its old--new section; preserve the
  MMS02 section byte-for-byte.
- Create during later checkpoints:
  `.scratch/period-two-old-new-cut-package-v2/index.json`,
  its `objects/*.jsonl` shards, one generation receipt, one independent
  attestation, and the existing theorem memo only after replay.

The root index exposes exact fields `format, scope, logical_v1_format,
canonical_encoding, mask_encoding, domain, status, shard_order, shards,
shard_bytes_total, emitted_summary, full_summary,
source_bindings_sha256, b_identity_digest, template_catalogs, root_sha256`.
Descriptors expose exact fields `role, family, path, sha256, total_bytes,
record_count, record_counts`.

---

### Task 1: Package-v2 Wire and Publication Foundation

**Files:**
- Modify: `docs/superpowers/specs/2026-07-29-old-new-cut-load-certificate-design.md`
- Modify: `docs/superpowers/plans/2026-07-29-old-new-cut-load-certificate.md`
- Modify: `.scratch/test_period_two_old_new_cut_load_certificate.py`
- Modify: `.scratch/period_two_old_new_cut_load_certificate.py`
- Modify: `.scratch/period_two_old_new_cut_load_verify.py`
- Modify after GREEN: old--new section only of `docs/AK3_PROMISE_LEDGER.md`

**Interfaces:**
- Consumes: one literal minimal logical-v1 fixture; no full source ledger.
- Generator produces: `canonical_json_line`, `iter_canonical_json_lines`,
  `decode_root_index`, `pack_mask`, `unpack_mask`,
  `validate_mask_partition`, `encode_tiny_v2_package`,
  `publish_v2_package`, `PublicationResult`, `PublicationFailure`, and
  opt-in `PhaseMetrics`.
- Verifier independently produces: `canonical_json_line`,
  `iter_canonical_json_lines`, `decode_root_index`, `pack_mask`,
  `unpack_mask`, `decode_v2_package`, and `verify_v2_package`.
- Neither codec module imports the other; both expose the same literal
  package constants, root/descriptor fields, six shared tag declarations, and
  thirteen family tag declarations.

- [ ] **Step 1: Persist the complete v2 design and executable plan**

Freeze the root/shared/family grammars, strict domains, source/compact cell
indices, logical-v1 inverse formulas, mask encoding, canonical decoder,
PREPARED/COMMITTED publication, metrics, receipts, coordinator, projection
gates, cleanup, mutations, and nonclaims before editing Python.

- [ ] **Step 2: Write focused failing tests**

Add these named behavior tests with hand-derived expected values:

    test_package_v2_constants_and_tag_grammars_are_exact
    test_package_v2_generator_and_verifier_literals_agree
    test_package_v2_masks_round_trip_and_reject_malformed_tokens
    test_package_v2_histogram_masks_cover_token_bits_without_reversal
    test_package_v2_canonical_decoder_rejects_noncanonical_lines
    test_package_v2_tag_decoders_reject_width_field_and_order_mutations
    test_package_v2_source_and_compact_cell_indices_are_distinct_strict_ints
    test_package_v2_tiny_logical_v1_round_trip
    test_package_v2_content_addresses_and_rejects_reuse_mismatch
    test_package_v2_prepared_failures_preserve_prior_index_and_clean
    test_package_v2_committed_failures_leave_complete_package
    test_package_v2_cap_blocks_production_index_replacement
    test_package_v2_metrics_do_not_change_package_bytes

Each test names the production mutation it catches.  Duplicate-key fixtures
are written as literal bytes, not Python dictionaries.  Expected masks and
hashes are literal.

- [ ] **Step 3: Run the focused selector and record RED**

Run:

    UV_CACHE_DIR=.scratch/uv-cache PYTHONPYCACHEPREFIX=.scratch/pycache \
    PYTHONDONTWRITEBYTECODE=1 python3 scripts/run_proof_guarded.py \
    --timeout-seconds 30 -- uv run --with pytest python3 -m pytest -q \
    .scratch/test_period_two_old_new_cut_load_certificate.py \
    -k 'package_v2'

Expected: collection succeeds and the first missing v2 constant/API assertion
fails.  A parse error is repaired and rerun until the failure is caused only
by missing foundation behavior.

- [ ] **Step 4: Implement strict independent codecs**

Implement exact line serialization, bounded streaming parsing with duplicate
key and numeric hooks, root and tagged-array state machines, strict integer
typing, mask pack/unpack, every cross-reference check needed by the tiny
fixture, and no whole-package read/serialization API.  Copy declarations and
codec logic independently into the verifier; do not import or alias generator
objects.

- [ ] **Step 5: Implement the tiny inverse and publication state machine**

Encode all seven shard roles, including grammar-valid empty family shards.
Reconstruct the exact literal logical-v1 fixture in the verifier.  Content
address each shard, distinguish created from reused objects, compare reused
objects in bounded chunks, fsync files/directories, enforce the production
cap before replacement, and inject all seven named object/index boundaries.
Before replacement, preserve the prior index and delete current-created
objects/temps only.  After replacement, retain the complete package and emit
no receipt on failure.

- [ ] **Step 6: Implement opt-in metrics**

Use only fixed stage/tag names.  Record elapsed stage durations and
deterministic record/byte counts.  Keep command, PID, timestamp, environment,
secrets, paths, and proof payload out.  Metrics are returned out of band and
never enter root or shard bytes.

- [ ] **Step 7: Run focused GREEN and compact-v2 regressions**

Run the package-v2 selector from Step 3.  Then run:

    UV_CACHE_DIR=.scratch/uv-cache PYTHONPYCACHEPREFIX=.scratch/pycache \
    PYTHONDONTWRITEBYTECODE=1 python3 scripts/run_proof_guarded.py \
    --timeout-seconds 30 -- uv run --with pytest python3 -m pytest -q \
    .scratch/test_period_two_old_new_cut_load_certificate.py \
    -k 'compact_v2 or typed_sha256'

Expected: every selected test passes in under 30 seconds; no full generator or
logical-v1 manifest build runs.

- [ ] **Step 8: Run lint, Python 3.9 compilation, and bounded audits**

Run Ruff 0.16.0 and `py_compile` as separate guarded 30-second commands over
the three Python files.  Set `PYTHONPYCACHEPREFIX=.scratch/pycache` for
compilation.  Run `git diff --check`, verify the proof lock is absent, and use
the permitted exact-basename process scan for Python, pytest, uv, Numba, and
the proof guard.

- [ ] **Step 9: Update the promise ledger, report, and commit**

Update only the old--new ledger section with foundation status and explicit
nonclaims.  Write the ignored Task 1 report with RED/GREEN evidence, APIs,
mutation matrix, atomicity, metrics identity, audits, and the statement that
no full proof generation/replay occurred.  Stage only authorized exact paths,
inspect cached names/diff, and commit:

    git commit -m "Build old-new package v2 foundation"

Do not push and do not commit the ignored report.

---

### Task 2: Streaming Production Generator

**Files:**
- Modify: `.scratch/period_two_old_new_cut_load_certificate.py`
- Modify: `.scratch/test_period_two_old_new_cut_load_certificate.py`
- Modify before implementation only: this plan and
  `docs/superpowers/specs/2026-07-29-old-new-cut-load-certificate-design.md`
  for the advisor-approved two-phase correction
- Do not modify: verifier, promise ledger, proof guard, solver, notebook,
  theorem memo, production package path, receipt file, attestation file, or
  any `.superpowers` artifact during implementation

**Interfaces:**
- Consumes: `load_source_context`, `build_task4_schema_catalog`, existing
  source bindings, old/B token identities, compact templates, and comparison
  witnesses without calling `build_manifest`.
- Produces these exact immutable records:

```python
@dataclass(frozen=True)
class CellFooterMetadata:
    source_cell_index: int
    compact_cell_index: int
    cell_id: str
    odd_old_indices: tuple[int, ...]
    value: int
    load_record_count: int


@dataclass(frozen=True)
class FamilyGenerationDiscovery:
    family: str
    variables: tuple[str, ...]
    selected_old_indices: tuple[int, ...]
    source_cell_count: int
    old_load_count: int
    footprint_count: int
    bucket_classes: tuple[tuple[Any, ...], ...]
    cell_footers: tuple[CellFooterMetadata, ...]
    load_rows: int
    occurrence_loads: int
    comparisons: int


@dataclass(frozen=True)
class StreamedObject:
    path: Path
    sha256: str
    total_bytes: int
    record_count: int
    record_counts: Mapping[str, int]


@dataclass(frozen=True)
class FamilyProjectionInput:
    family: str
    selected_old_indices: tuple[int, ...]
    selected_schema_indices: tuple[int, ...]
    tied_max_schema_ids: tuple[str, ...]
    full_schema_count: int
    full_comparisons: int
    sampled_comparisons: int
    sampled_two_pass_ns: int
    sampled_load_bucket_bytes: int
    full_identity_count: int
    sampled_identity_count: int
    sampled_template_ns: int
    sampled_template_bytes: int
    fixed_family_ns: int
    fixed_family_bytes: int


@dataclass(frozen=True)
class FamilyGenerationProjection:
    family: str
    selected_old_indices: tuple[int, ...]
    selected_schema_indices: tuple[int, ...]
    tied_max_schema_ids: tuple[str, ...]
    full_schema_count: int
    full_comparisons: int
    sampled_comparisons: int
    sampled_two_pass_ns: int
    projected_two_pass_ns: int
    sampled_load_bucket_bytes: int
    projected_load_bucket_bytes: int
    full_identity_count: int
    sampled_identity_count: int
    sampled_template_ns: int
    projected_template_ns: int
    sampled_template_bytes: int
    projected_template_bytes: int
    fixed_family_ns: int
    fixed_family_bytes: int


@dataclass(frozen=True)
class GenerationProjection:
    format: str
    family_order: tuple[str, ...]
    full_schema_count: int
    full_identity_count: int
    sampled_source_loads: int
    sampled_occurrence_loads: int
    sampled_comparisons: int
    source_catalog_precompute_ns: int
    shared_ns: int
    shared_bytes: int
    projected_index_ns: int
    projected_index_bytes: int
    families: tuple[FamilyGenerationProjection, ...]
    generation_ns_before_margin: int
    package_bytes_before_margin: int
    projected_generation_ns: int
    projected_package_bytes: int
```

- Produces these exact APIs:

```text
def discover_family_generation(
    catalog: Task4SchemaCatalog,
    family: str,
    *,
    selected_old_indices: Sequence[int],
) -> FamilyGenerationDiscovery

def iter_shared_records(
    catalog: Task4SchemaCatalog,
    *,
    scope: str,
    status: str,
) -> Iterator[tuple[Any, ...]]

def iter_family_records(
    catalog: Task4SchemaCatalog,
    discovery: FamilyGenerationDiscovery,
    *,
    scope: str,
    selected_template_schema_indices: Sequence[int] | None = None,
) -> Iterator[tuple[Any, ...]]

def write_jsonl_stream(
    records: Iterable[tuple[Any, ...]],
    destination: Path,
    *,
    metrics: PhaseMetrics | None = None,
) -> StreamedObject

def preflight_template_selection(
    family_catalog: Task4FamilyCatalog,
) -> tuple[tuple[int, ...], tuple[str, ...]]

def project_generation(
    *,
    source_catalog_precompute_ns: int,
    shared_ns: int,
    shared_bytes: int,
    projected_index_ns: int,
    projected_index_bytes: int,
    families: Sequence[FamilyProjectionInput],
) -> GenerationProjection

def build_generation_receipt_payload(
    *,
    run_id: str,
    scope: str,
    index_path: str,
    index_sha256: str,
    root_sha256: str,
    state: str,
    package_bytes: int,
    created_objects: Sequence[str],
    reused_objects: Sequence[str],
    generator_sha256: str,
    metrics: Mapping[str, Any],
) -> dict[str, Any]
```

`discover_family_generation` is Phase A. `iter_family_records` is Phase B:
it recomputes comparisons, emits records against the frozen bucket table, and
fails if it sees a new key. `write_jsonl_stream` streams one object and returns
metadata; it never constructs a complete object `bytes` value.

- [ ] **Step 1: Write RED selection, cold-precompute, and boundary tests**

Add these named tests:

    test_task2_preflight_old_selection_and_sample_censuses_are_literal
    test_task2_production_selected_old_indices_are_complete_ranges
    test_task2_template_selection_is_zero_based_every_eighth_union_all_tied_maxima
    test_task2_cold_full_catalog_precompute_precedes_template_filter
    test_task2_shared_iterator_emits_complete_source_and_84_token_tables
    test_task2_adapters_pass_when_build_manifest_is_monkeypatched_to_raise

The first test contains these literal fixtures:

```python
expected = {
    "fixed": (0, 8, 15, 23, 31, 38, 46, 54, 61, 69),
    "base": (0, 1),
    "singleton": (0,),
    "P": (0, 3, 5, 8, 10, 13, 16, 18, 21, 23, 26, 28, 31),
    "C": (0, 19, 38),
    "Q": (0, 15, 30, 46, 61, 76, 91),
}
assert module.PREFLIGHT_SELECTED_OLD_INDICES == expected
assert module.PREFLIGHT_SOURCE_LOADS == 1_406
assert module.PREFLIGHT_OCCURRENCE_LOADS == 2_716
assert module.PREFLIGHT_COMPARISONS == 228_144
assert 2_716 * 84 == 228_144
```

Use a literal synthetic schema table with maxima tied at non-eighth indices to
require `(0, 2, 5, 8, 16)` and the complete sorted tied-max ID tuple.  The
cold-precompute test spies on `load_source_context` and
`build_task4_schema_catalog` and requires the observed full counts
`1_304` schemas and `48_252` identities before
`preflight_template_selection` is called.  The shared test requires all
dependency rows, the full `task4-source-bindings-v1` value, token indices
`0..83`, and 84 aligned coordinates.  The monkeypatch test replaces
`build_manifest` with a function that raises `AssertionError`, then exercises
every Task 2 adapter, iterator, projection calculation, stream writer, and
receipt-payload constructor on bounded fixtures.

- [ ] **Step 2: Run the first selector and record intended RED**

Run:

    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
    NUMBA_NUM_THREADS=1 UV_CACHE_DIR=.scratch/uv-cache \
    PYTHONPYCACHEPREFIX=.scratch/pycache PYTHONDONTWRITEBYTECODE=1 \
    python3 scripts/run_proof_guarded.py --timeout-seconds 30 -- \
    uv run --offline --with pytest python3 -m pytest -q \
    .scratch/test_period_two_old_new_cut_load_certificate.py \
    -k 'task2_preflight_old_selection or task2_production_selected_old or task2_template_selection or task2_cold_full_catalog or task2_shared_iterator or task2_adapters_pass'

Expected: collection succeeds; failures name missing
`PREFLIGHT_SELECTED_OLD_INDICES`, `preflight_template_selection`,
`iter_shared_records`, production-range validation, and the remaining Task 2
APIs.  Repair collection errors before accepting RED.

- [ ] **Step 3: Implement the immutable selection and adapter boundary**

Add the six literal selected-old tuples; do not generate them from spacing
rules.  Reject a production selection unless it is exactly
`tuple(range(old_load_count))` for that family.  For a schema at zero-based
ASCII index `j`, define its pump count as the maximum `len(witness[2])` across
all of that schema's cells.  Return every `j % 8 == 0` index union every
schema whose pump count equals the family-wide maximum.  Return the selected
indices strictly increasing and every tied maximum schema ID in complete
ASCII order.

`load_source_context` and `build_task4_schema_catalog` run once, cold, before
selection.  Validate the full `1_304`/`48_252` counts before filtering.  Build
the shared iterator from the complete catalog and `build_source_bindings`;
never route through `build_manifest`.

- [ ] **Step 4: Write RED two-phase, source-binding, and footprint mutations**

Add these named tests:

    test_task2_phase_a_freezes_canonical_bucket_table_before_any_load
    test_task2_phase_a_retains_no_rows_masks_or_family_ledger
    test_task2_phase_b_recomputes_and_rejects_bucket_not_in_frozen_table
    test_task2_family_iterator_order_and_footer_prefixes_are_exact
    test_task2_old_raw_rows_and_provenance_mutations_fail_closed
    test_task2_old_integral_fiber_mutations_fail_closed
    test_task2_old_member_alignment_domain_and_equality_mutations_fail_closed
    test_task2_one_member_and_anchor_mutations_fail_closed
    test_task2_b_all_fiber_and_activity_mutations_fail_closed
    test_task2_b_identity_coordinate_and_schema_mutations_fail_closed
    test_task2_every_footprint_partition_mutation_fails_closed
    test_task2_derived_family_census_and_parity_mutations_fail_closed
    test_task2_stream_writer_is_incremental_and_bounded

The source tests are parametrized with these explicit mutation IDs, reseal
every enclosing digest, and require `CertificateFailure`:

    raw-row, raw-provenance, raw-provenance-count, raw-id-duplicate,
    missing-provenance, inactive-old-fiber, active-old-fiber,
    member-id-order, coefficient-order, member-table-row, integral-sum,
    parity, activity, domain, current-equality, label-witness,
    fixed-one-member, singleton-one-member, anchor-pair, anchor-sum,
    anchor-provenance, inactive-b-fiber, active-b-fiber, b-member-order,
    b-coefficient-order, b-member-coefficient-pair, b-integral-sum, b-parity,
    b-activity, b-slot, b-module-schema, b-label-witness, token-index,
    token-id, source-class, token-coefficient, token-slot, occurrence,
    polarity, module-schema, label-schema, source-members, coordinate,
    source-digest, chronology-digest, b-identity-digest, catalog-digest

The fixture covers all 21 anchor pairs, all 53 B fibers including inactive
ones, and all 84 identity/coordinate pairs.  The footprint test mutates, one
at a time: comparison count `83`/`85`, zero mask, overlapping masks, missing
union bit, token-bit reversal, stored count, mask popcount, bucket key,
contribution bit, occurrence parity, cell parity, family parity, and every
source/occurrence/comparison census.  Each untouched footprint must have
exactly 84 comparisons, nonzero disjoint masks, union `(1<<84)-1`, count equal
to popcount, and token `i` encoded by `1<<i`.

- [ ] **Step 5: Run the two-phase and mutation selector and record RED**

Run:

    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
    NUMBA_NUM_THREADS=1 UV_CACHE_DIR=.scratch/uv-cache \
    PYTHONPYCACHEPREFIX=.scratch/pycache PYTHONDONTWRITEBYTECODE=1 \
    python3 scripts/run_proof_guarded.py --timeout-seconds 30 -- \
    uv run --offline --with pytest python3 -m pytest -q \
    .scratch/test_period_two_old_new_cut_load_certificate.py \
    -k 'task2_phase_a or task2_phase_b or task2_family_iterator or task2_old_ or task2_one_member or task2_b_ or task2_every_footprint or task2_derived_family or task2_stream_writer'

Expected: fixture construction succeeds; tests fail because
`discover_family_generation`, `iter_family_records`, and
`write_jsonl_stream` are absent.  A mutation that fails before the intended
semantic check is repaired before implementation.

- [ ] **Step 6: Implement bounded Phase A, Phase B, and the stream writer**

Phase A traverses every source cell, and in `production-full` every old index,
footprint, and token in the frozen order.  The bounded preflight fixture uses
only its literal selected-old indices and cannot enter production status.
Keep only a set of hashable bucket keys, exact integer censuses, xor/parity
accumulators, and one `CellFooterMetadata` per cell.  Freeze
`bucket_classes` by canonical-JSON bytes.  Assert that
`FamilyGenerationDiscovery` has no field capable of storing a comparison,
load row, mask, logical-v1 object, or family ledger.

Phase B emits exactly: family header; complete old-load and footprint tables;
the frozen bucket-class table; recomputed load masks and cell footers;
template records; and the family footer.  Recompute every comparison through
`comparison_record`, rebuild each footprint partition, require all 84 token
indices and every mask invariant, and look up every bucket key in the frozen
table.  Do not append a new class in Phase B.

`write_jsonl_stream` accepts an iterator, writes each
`canonical_json_line(record)` immediately, and incrementally updates SHA-256,
bytes, tag counts, record count, and `PhaseMetrics`.  It never calls
`tuple(records)`, `list(records)`, `read_text`, `read_bytes`, `deepcopy`, or a
whole-object serializer.  Tests write only bounded synthetic/preflight
objects under `.scratch/test-artifacts/old-new-load/`.

- [ ] **Step 7: Write RED exact-projection and receipt-boundary tests**

Add these named tests:

    test_task2_projection_uses_integer_ceiling_and_separate_denominators
    test_task2_projection_charges_full_precompute_shared_and_family_tables
    test_task2_projected_index_oracle_uses_actual_root_and_64_hex_fields
    test_task2_projection_applies_one_final_factor_two
    test_task2_generation_projection_is_deterministic_and_has_no_floats
    test_task2_generation_receipt_payload_constructor_is_pure
    test_task2_writes_no_production_package_or_durable_evidence

The arithmetic fixture requires:

```python
assert module.ceil_ratio(5, 11, 3) == 19
assert module.ceil_ratio(7, 13, 4) == 23
assert module.ceil_ratio(17, 11, 3) == 63
assert module.ceil_ratio(19, 13, 4) == 62
assert projection.generation_ns_before_margin == 142
assert projection.projected_generation_ns == 284
assert projection.package_bytes_before_margin == 725
assert projection.projected_package_bytes == 1_450
```

Those totals use fixed time charges `10 + 20 + 30 + 40` and fixed byte
charges `100 + 200 + 300`.  Assert separately that source/catalog precompute,
complete shared data, full family header/old/footprint/cell/footer records,
and projected index are never multiplied by either ratio.  Build the index
oracle with the actual root fields, projected descriptor counts/bytes, and
`"0" * 64` in every digest position; require its canonical encoded length to
equal `projected_index_bytes`.  Reject zero/equal/oversized denominators,
booleans, floats, negative counts, missing families, incomplete tied-max IDs,
and non-literal selected-old arrays.

Patch `Path.write_text`, `Path.write_bytes`, `open`, `os.replace`, and receipt/
attestation helpers to raise while calling
`build_generation_receipt_payload`.  Require the exact payload dictionary and
no filesystem call.  Record `git status --short` before and after the bounded
Task 2 suite and require no production index, receipt, attestation, theorem
memo, or promise-ledger change.

- [ ] **Step 8: Run the projection selector and record intended RED**

Run:

    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
    NUMBA_NUM_THREADS=1 UV_CACHE_DIR=.scratch/uv-cache \
    PYTHONPYCACHEPREFIX=.scratch/pycache PYTHONDONTWRITEBYTECODE=1 \
    python3 scripts/run_proof_guarded.py --timeout-seconds 30 -- \
    uv run --offline --with pytest python3 -m pytest -q \
    .scratch/test_period_two_old_new_cut_load_certificate.py \
    -k 'task2_projection or task2_projected_index or task2_generation_projection or task2_generation_receipt or task2_writes_no_production'

Expected: collection succeeds; failures are missing `ceil_ratio`,
`project_generation`, projected-index oracle behavior, and
`build_generation_receipt_payload`.  No RED command creates a package.

- [ ] **Step 9: Implement exact generator-only projection and pure payload**

Implement `ceil_ratio(x, numerator, denominator)` as
`(x * numerator + denominator - 1) // denominator` after exact non-boolean
integer validation.  For every family, independently scale sampled two-pass
nanoseconds and variable bucket/load bytes by full/sample comparisons, and
sampled template nanoseconds/bytes by full/sample identities.  Add the full
cold source/catalog precompute, complete shared shard, complete fixed family
records, and exactly encoded projected index once.  Sum all fixed and
upward-rounded variable components, then multiply final generation
nanoseconds and package bytes by two.

Keep all `GenerationProjection` fields as exact integers or immutable string/
tuple records; reject any float recursively.  Task 2 reports no verifier
projection.  Set `format` to
`period-two-old-new-cut-generation-projection-v1`.  The receipt constructor
validates and returns only the fields frozen in design Section 17, with format
`period-two-old-new-cut-generation-receipt-v1`; it does not serialize or
publish them.

- [ ] **Step 10: Run bounded GREEN and foundation regressions**

Run these as separate foreground guarded commands:

    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
    NUMBA_NUM_THREADS=1 UV_CACHE_DIR=.scratch/uv-cache \
    PYTHONPYCACHEPREFIX=.scratch/pycache PYTHONDONTWRITEBYTECODE=1 \
    python3 scripts/run_proof_guarded.py --timeout-seconds 30 -- \
    uv run --offline --with pytest python3 -m pytest -q \
    .scratch/test_period_two_old_new_cut_load_certificate.py -k 'task2_'

    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
    NUMBA_NUM_THREADS=1 UV_CACHE_DIR=.scratch/uv-cache \
    PYTHONPYCACHEPREFIX=.scratch/pycache PYTHONDONTWRITEBYTECODE=1 \
    python3 scripts/run_proof_guarded.py --timeout-seconds 30 -- \
    uv run --offline --with pytest python3 -m pytest -q \
    .scratch/test_period_two_old_new_cut_load_certificate.py \
    -k 'package_v2 or compact_v2 or typed_sha256'

Expected: every selected test passes below 30 seconds.  No command calls
`build_manifest`, writes the production path, performs independent replay, or
runs an actual preflight.

- [ ] **Step 11: Run lint, compile, document self-review, and scope audits**

Run Ruff 0.16.0 and Python 3.9 compilation as separate guarded commands:

    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
    NUMBA_NUM_THREADS=1 UV_CACHE_DIR=.scratch/uv-cache \
    PYTHONPYCACHEPREFIX=.scratch/pycache PYTHONDONTWRITEBYTECODE=1 \
    python3 scripts/run_proof_guarded.py --timeout-seconds 30 -- \
    uv run --offline --with ruff==0.16.0 ruff check \
    .scratch/period_two_old_new_cut_load_certificate.py \
    .scratch/test_period_two_old_new_cut_load_certificate.py

    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
    NUMBA_NUM_THREADS=1 PYTHONPYCACHEPREFIX=.scratch/pycache \
    PYTHONDONTWRITEBYTECODE=1 python3 scripts/run_proof_guarded.py \
    --timeout-seconds 30 -- python3 -m py_compile \
    .scratch/period_two_old_new_cut_load_certificate.py \
    .scratch/test_period_two_old_new_cut_load_certificate.py

Then perform these read-only checks:

    awk '/^### Task 2:/{task=1} /^### Task 3:/{task=0} \
      task && $0 !~ /rg -n.*TODO/ {print}' \
      docs/superpowers/plans/2026-07-29-old-new-cut-load-certificate.md |
      rg -n 'TODO|TBD|implement later|test(s)? above|Similar to Task|: \.\.\.'
    rg -n 'one-pass|spool|external sort|build_manifest|logical-v1 object|receipt file|attestation|promise-ledger' \
      docs/superpowers/specs/2026-07-29-old-new-cut-load-certificate-design.md \
      docs/superpowers/plans/2026-07-29-old-new-cut-load-certificate.md
    git diff --check
    git status --short
    git diff --name-only
    test ! -e .scratch/process-guard/active.json
    test ! -e .scratch/period-two-old-new-cut-package-v2/index.json
    ps -axo pid=,ppid=,pgid=,%cpu=,state=,comm=

The placeholder scan must have no match.  Inspect every contradiction-scan
hit in context: only explicit prohibitions and the monkeypatch regression may
remain.  `git diff --name-only` must list only the generator and focused test.
The lock and production-index predicates must exit zero.  Review the safe
`ps` fields only for stale project Python, pytest, uv, Numba, or proof-guard
processes; never request or print process arguments.

- [ ] **Step 12: Stage the exact implementation and commit**

Run:

    git add -f \
      .scratch/period_two_old_new_cut_load_certificate.py \
      .scratch/test_period_two_old_new_cut_load_certificate.py
    git diff --cached --check
    git diff --cached --name-only
    git commit -m "Stream old-new package v2 generation"
    git show --stat --oneline --decorate=short HEAD
    git status --short

The cached name list must contain exactly the two files above.  Do not stage a
production object, receipt, attestation, theorem memo, promise ledger,
verifier, guard, solver, notebook, report, or `.superpowers` artifact.  Do not
push.

---

### Task 3: Independent Streaming Verifier

**Files:**
- Modify: `.scratch/period_two_old_new_cut_load_verify.py`
- Modify: `.scratch/test_period_two_old_new_cut_load_certificate.py`

**Interfaces:**
- Consumes: package-v2 index and seven content-addressed shards plus approved
  upstream dependencies.
- Produces: `verify_v2_package(index_path, run_id)`,
  `IndependentReplayResult`, deterministic `VerificationProjection`, and the
  frozen attestation payload builder.

- [ ] **Step 1: Add RED package and semantic mutations**

Mutate one dependency, source row, coefficient, cell map, footprint, mask,
comparison class, family value, compact schema/cell/witness/identity, footer,
descriptor, and root field at a time.  Reseal all enclosing hashes so each
test reaches the intended independent semantic check.

- [ ] **Step 2: Implement independent source adapters and replay**

Without generator imports, reconstruct source rows, B identities/coordinates,
compact templates, comparison methods, chronologies, histograms, load/cell
parities, six family ledgers, summaries, and exact logical-v1 bytes.  Digest
matches never replace semantic reconstruction.

- [ ] **Step 3: Implement bounded verifier projection**

Verify the registered preflight subset with independently computed exact
integer denominators and fixed charges.  Produce verifier-only
`VerificationProjection` time; do not overwrite, fold into, or restate Task
2's generator-only `GenerationProjection`.  Reject a generator projection
whose selected-old, selected-schema, tied-max-ID, full-count, or sampled-count
denominators differ from independently observed values.

- [ ] **Step 4: Verify and commit**

Run focused verifier/mutation tests, generator regressions, Ruff 0.16.0,
compile, diff/lock/process audits under 30 seconds.  Commit as
`Independently replay old-new package v2`.  Do not create an attestation for a
preflight package.

---

### Task 4: Fixed-Run Coordinator and Durable Evidence

**Files:**
- Modify: `.scratch/period_two_old_new_cut_load_certificate.py`
- Modify: `.scratch/period_two_old_new_cut_load_verify.py`
- Modify: `.scratch/test_period_two_old_new_cut_load_certificate.py`

**Interfaces:**
- Consumes: explicit `--run-id`, production index path, generation receipt,
  independent attestation, and both projections.
- Produces: one integrated CLI which sequences generation then verification
  and binds every artifact to the same run/index/root digests.

- [ ] **Step 1: Add RED coordinator state tests**

Require fixed run ID, reject stale/mismatched receipt or attestation, reject
preflight status, verify no receipt before a fully fsynced commit, and verify
no attestation before independent semantic replay.

- [ ] **Step 2: Implement generator receipt and verifier attestation**

Consume Task 2's pure generation-receipt payload constructor and Task 3's
pure attestation payload constructor.  Serialize only the exact design
fields and write each atomically after its own success boundary.  Post-index
fsync failure is committed but produces neither artifact.

- [ ] **Step 3: Implement coordinator**

Pass the explicit run ID to both sides, check executable hashes, package/root
digests, status, scope, logical-v1 digest, metrics schema, and exit
classification.  Cleanup only exact preflight/test paths.

- [ ] **Step 4: Verify and commit**

Run bounded coordinator injection tests plus the focused foundation/generator/
verifier suites, lint, compile, diff/lock/process audits.  Commit as
`Coordinate old-new package v2 replay`.  Do not run production.

---

### Task 5: Whole-Package Hostile Review

**Files:**
- Modify only files with a reproduced failing test first.
- Update: old--new section of `docs/AK3_PROMISE_LEDGER.md`.

**Interfaces:**
- Consumes: Tasks 1--4 commits and fresh bounded outputs.
- Produces: reviewed preflight configuration, exact mutation coverage matrix,
  and an approved production command/run ID.

- [ ] **Step 1: Run the 60-second preflight under the proof guard**

The procedural root launcher runs the exact preflight.  Require all tied
maximum schemas, the literal Task 2 selected-old arrays, full shared data, the
cold 1,304-schema/48,252-identity precompute, fixed denominators with dynamic
range, and seven shard roles.  Require independent denominator agreement,
Task 2 `projected_generation_ns` plus Task 3
`projected_verification_ns` at most `600_000_000_000`, and Task 2
`projected_package_bytes` at most `100_000_000`.  Use exact integer
comparisons, not converted floating-point seconds or megabytes.  This is the
first actual preflight; Task 2 tests only bounded adapters and synthetic
streams.

- [ ] **Step 2: Perform independent code and mathematical reviews**

Review wire grammar, canonical rejection, reference domains, logical inverse,
atomicity, source binding, integer-before-parity aggregation, pumping,
chronology, masks, family arithmetic, metrics, receipt/attestation, resource
projection, cleanup, and all nonclaims.

- [ ] **Step 3: Resolve every substantive finding with RED/GREEN**

Critical or important findings receive a focused failing mutation before any
implementation edit.  Rerun the affected bounded suite and the whole preflight
after a material algorithm/input change.

- [ ] **Step 4: Commit, log, and push before experiment**

Commit the reviewed checkpoint, append the mandatory UTC/SHA log entry in its
two-commit binding, verify clean status and exact artifact hashes, then push
`codex/proofs`.  No production experiment starts before this succeeds.

---

### Task 6: Guarded Production Experiment

**Files:**
- Create: canonical package-v2 index and seven referenced objects.
- Create: generation receipt and independent attestation.
- Modify: theorem memo only after independent replay.

**Interfaces:**
- Consumes: the pushed reviewed checkpoint, approved fixed run ID, successful
  60-second preflight, and exact integrated coordinator command.
- Produces: one production package below 100 MB, one receipt, one attestation,
  and exact guarded audit evidence.

- [ ] **Step 1: Run the coordinator once in authorized long mode**

Only the procedural root launcher runs the exact preflight then the production
coordinator with timeout at most 600 seconds and one CPU thread.  Never rerun
an unchanged timeout or unsuccessful command.

- [ ] **Step 2: Audit durable package state**

Require a finalized proof-guard audit, absent singleton lock, exact process
absence, canonical index/object hashes, no dangling descriptors, package cap,
receipt/attestation run binding, and byte-for-byte logical-v1 reconstruction.

- [ ] **Step 3: Record the bounded outcome**

On success, write the theorem memo with only the independently replayed
positive-chamber cut statement.  On any failure, record the bounded failure
and preserve all mathematical nonclaims; do not describe it as evidence
against AC or stable AC.

- [ ] **Step 4: Commit, log, and push**

Commit the exact outcome, bind the UTC/SHA log in the required follow-up
commit, and push before any further proof computation.

---

### Task 7: Theorem Integration and Review

**Files:**
- Modify only the tracked seven-family theorem note resolved with `rg --files`.
- Modify/add a replay test only when integration changes a theorem status.
- Update only the old--new promise-ledger section.

**Interfaces:**
- Consumes: production package plus independent attestation.
- Produces: exact substitution of the cut lemma and the next residual theorem
  obligation; never an unsupported AC/stable-AC claim.

- [ ] **Step 1: Integrate only the attested domain**

Substitute `B(A_(n,d),b_(n,d))=[d>1]` for `n>=0,d>=1` into the owning
seven-family derivation.  Recompute signs, parity, and endpoint domains.

- [ ] **Step 2: Hostile theorem review**

Check every dependency/run digest, integer-to-parity transition, lowercase/
uppercase word spelling, stable move hypothesis, and use-site domain.  Keep
`d=0`, the unary `Q(A)` law, covariance outside the cut, AC, and stable AC
explicitly open unless separately proved.

- [ ] **Step 3: State the next exact proof obligation**

If covariance closes, name the remaining edge/unary law.  Otherwise isolate
the smallest surviving family or endpoint formula.  A verified finite lemma
is one proof-loop checkpoint, not completion of AK(3).

- [ ] **Step 4: Verify, commit, log, and push**

Run only the focused integration replay and documentation/diff audits, obtain
hostile review, commit the exact theorem increment, bind the UTC/SHA log, and
push.

---

## Historical Logical-v1 Plan (Superseded; Do Not Execute)

The remainder of this file is retained only to explain the already completed
logical-v1 work and its source/proof contracts.  Its monolithic generation
steps, paths, tasks, commands, and production artifact instructions are
superseded by Tasks 1--7 above and must not be run.

### Historical File Map

- Create `.scratch/period_two_old_new_cut_load_certificate.py`: generator, source binding, cell/pumping logic, collision aggregation, histograms, canonical JSON CLI.
- Create `.scratch/period_two_old_new_cut_load_verify.py`: independent JSON/source replay and mutation-rejecting CLI.
- Create `.scratch/test_period_two_old_new_cut_load_certificate.py`: literal unit fixtures plus generator/verifier integration tests.
- Create `.scratch/period_two_old_new_cut_load_manifest.json`: deterministic certificate output.
- Create `.scratch/period_two_old_new_cut_load_certificate.md`: theorem statement, hashes, replay evidence, and non-claims.

The generator owns these public interfaces: `make_cells(variables) -> tuple[Cell,
...]`, `p_domain_nonempty(cell) -> bool`, `aggregate_integral_fibers(rows,
templates, cell) -> CollisionResult`, `comparison_record(old, new, templates,
cell) -> ComparisonRecord`, `histogram_for_load(old, b_tokens, templates,
cell) -> tuple[HistogramBucket, ...]`, `build_manifest() -> dict[str, object]`,
and `write_manifest(path=MANIFEST_PATH) -> dict[str, object]`.

The verifier owns `verify_manifest(path) -> dict[str, object]` and shares no
generator objects.

---

### Historical Stage 1: Cell Algebra and Complete 84-Token Masks

**Files:**
- Create: `.scratch/test_period_two_old_new_cut_load_certificate.py`
- Create: `.scratch/period_two_old_new_cut_load_certificate.py`

**Interfaces:**
- Consumes: no new code.
- Produces: `Cell`, `HistogramBucket`, `make_cells`, `p_domain_nonempty`, `bucketize_records`, and `canonical_json`.

- [ ] **Step 1: Write the failing structural test**

Create the test loader and literal tests. The production mutation each test catches is stated in its name.

```python
import functools
import importlib.util
import operator
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / ".scratch/period_two_old_new_cut_load_certificate.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_generator():
    return load_module("old_new_load_generator", GENERATOR)


def test_generator_file_exists_before_loading() -> None:
    assert GENERATOR.exists(), "grouped-load generator is not implemented"


def test_cells_cover_exact_threshold_states_and_p_domain() -> None:
    module = load_module("load_generator", GENERATOR)
    assert len(module.make_cells(("a", "n"))) == 16
    assert len(module.make_cells(("h", "k", "n"))) == 64
    p_cells = tuple(
        cell
        for cell in module.make_cells(("a", "h", "r"))
        if module.p_domain_nonempty(cell)
    )
    assert len(p_cells) == 54
    assert "age3_h0_r0" not in {cell.cell_id for cell in p_cells}
    assert "age3_h0_rge3" in {cell.cell_id for cell in p_cells}


def test_bucket_masks_form_one_exact_84_token_partition() -> None:
    module = load_module("load_generator_masks", GENERATOR)
    records = tuple(
        {"token_index": index, "bit": index % 2, "chronology": "fixed"}
        for index in range(84)
    )
    buckets = module.bucketize_records(records, key_fields=("bit", "chronology"))
    assert sum(bucket.count for bucket in buckets) == 84
    assert sum(bin(bucket.mask).count("1") for bucket in buckets) == 84
    assert functools.reduce(operator.or_, (bucket.mask for bucket in buckets), 0) == (1 << 84) - 1
```

- [ ] **Step 2: Run the test and verify RED**

Run:

```bash
UV_CACHE_DIR=.scratch/uv-cache PYTHONPYCACHEPREFIX=.scratch/pycache python3 scripts/run_proof_guarded.py --timeout-seconds 30 -- uv run --with pytest python3 -m pytest -q .scratch/test_period_two_old_new_cut_load_certificate.py::test_generator_file_exists_before_loading
```

Expected: FAIL with `grouped-load generator is not implemented`.

- [ ] **Step 3: Implement the minimal cell and mask primitives**

Use immutable dataclasses. Cell IDs use `0`, `1`, `2`, and `ge3`; the stored
state for `ge3` is `None` and its base value is 3. Implement P-domain
intersection exactly:

```python
def p_domain_nonempty(cell: Cell) -> bool:
    a, h, r = cell.states
    if a is None:
        if h is None or r is None:
            return True
        return h + r >= 3
    if h is None or r is None:
        return True
    return h + r >= a
```

`bucketize_records` must reject token indices outside `0..83`, duplicates, and missing indices. It sorts serialized keys, computes each bitmask with `mask |= 1 << token_index`, and asserts disjoint union `(1 << 84) - 1`.

- [ ] **Step 4: Run all Task 1 tests and verify GREEN**

Use the guarded command from Step 2 without the test selector. Expected: all Task 1 tests PASS in under 30 seconds.

- [ ] **Step 5: Commit Task 1**

```bash
git add -f .scratch/test_period_two_old_new_cut_load_certificate.py .scratch/period_two_old_new_cut_load_certificate.py
git diff --cached --check
git commit -m "Build grouped-load certificate primitives"
```

---

### Historical Stage 2: Bound Sources and Aggregate Integral Collision Fibers

**Files:**
- Modify: `.scratch/test_period_two_old_new_cut_load_certificate.py`
- Modify: `.scratch/period_two_old_new_cut_load_certificate.py`

**Interfaces:**
- Consumes: `Cell`, `make_cells`, `canonical_json`.
- Produces: `SourceContext`, `TokenRef`, `Template`, `CollisionFiber`, `load_source_context`, `build_b_catalog`, `build_old_rows`, and `aggregate_integral_fibers`.

- [ ] **Step 1: Add failing tests for source binding and integer-first cancellation**

Use a literal three-row fixture whose two equal coordinates have coefficients `+1,-1` and whose third coordinate has coefficient `+3`. Assert two fibers, one absorbed zero-sum fiber, one active fiber with integral sum 3, and parity 1. Then add an actual-source test with literal expected counts:

```python
def test_bound_source_has_84_collision_first_b_tokens() -> None:
    module = load_generator()
    context = module.load_source_context()
    tokens, proof = module.build_b_catalog(context)
    assert len(tokens) == 84
    assert proof["occurrences"] == 16
    assert proof["active_path_fibers"] == 36
    assert proof["slot_zero_tokens"] == 12
```

The production mutations caught are: grouping after mod two, omitting a source digest, changing a source row coefficient, or rebuilding the B-side before collision aggregation.

- [ ] **Step 2: Run the two new tests and verify RED**

Expected: FAIL because `aggregate_integral_fibers` and `load_source_context` are absent.

- [ ] **Step 3: Implement source loading and collision records**

Load only these upstream files directly: raw-stream generator and JSON, inverse-Q checker and JSON, new--new aggregate checker and JSON, seven-family covariance checker and JSON, selector note, endpoint-potential note, and pumping lemma. Record SHA-256 for every path. Do not load the interrupted old--new checker.

For each collision key, serialize all member IDs and integer coefficients, the integral sum, parity, label-equality witness, and `active = (sum % 2 != 0)`. Reject a fiber if equal canonical module keys have unequal transported labels. Bind every raw row's typed domain and `current_equality` expression from the raw manifest.

- [ ] **Step 4: Build old-family rows without trusting summary counts**

Reconstruct fixed rows from the approved fixed-token source, base rows from the literal Hessian base variables, singleton from `g0:00`, and P/C/Q rows from `build_w_rows()`. Filter Q to positive orientation on `d>=1`. Expand slot actions to occurrence-specific `TokenRef` values before collision aggregation. Record the 21 anchor rows and compute their even integral sum.

- [ ] **Step 5: Run Task 2 tests and verify GREEN**

Expected: literal fiber fixture PASS; actual B catalog PASS with 84 tokens; raw-row provenance has no missing domain/equality field.

- [ ] **Step 6: Commit Task 2**

```bash
git add -f .scratch/test_period_two_old_new_cut_load_certificate.py .scratch/period_two_old_new_cut_load_certificate.py
git diff --cached --check
git commit -m "Bind old-new load sources and collision fibers"
```

---

### Historical Stage 3: Materialize All-Power Pumping and Shortlex Witnesses

**Files:**
- Modify: `.scratch/test_period_two_old_new_cut_load_certificate.py`
- Modify: `.scratch/period_two_old_new_cut_load_certificate.py`

**Interfaces:**
- Consumes: source schemas, cells, `Template`.
- Produces: `build_template`, `verify_intact_boundaries`, `compare_templates`, and serialized `PumpingWitness`/`ComparisonWitness` records.

- [ ] **Step 1: Add failing literal pumping tests**

Pin the two primitive cores as integer-letter tuples and assert both are nonempty, reduced, cyclically reduced, and length eight. Add a synthetic schema with two changing powered blocks whose selected adjacent-copy boundaries are distinct. Assert that expansion at the `ge3` base and after one increment equals direct full-word reduction, and that terminal-`c` deletion takes the same branch.

Add three comparison fixtures, one for each accepted discharge:

1. strict affine length with fixed sign;
2. identical normalized pumped block lists; and
3. identical pumped prefix with a fixed first mismatching letter.

- [ ] **Step 2: Run the new tests and verify RED**

Expected: FAIL because pumping witnesses are not implemented.

- [ ] **Step 3: Implement tagged reduction and witness serialization**

Tag each powered letter by `(block_name, block_index, copy_index, core_offset)`. Fully reduce the base word first. For every changing block, require a surviving adjacent pair with offsets `(len(core)-1, 0)` and consecutive copy IDs. Store the split position and both copy IDs. Reject coincident selected split positions. Store the full reduced terminal letter before `cvert` and verify insertions are internal to the retained word.

`compare_templates` must return exactly one of three record shapes:

- `strict_affine_length`: nonzero `order` and the complete affine
  `difference` coefficient list;
- `identical_pumped_blocks`: zero `order` and the complete normalized block
  list; or
- `fixed_mismatch_after_pumped_prefix`: nonzero `order`, the full affine
  prefix-length list, and the two fixed mismatch letters.

No sampled-grid comparison is accepted as an all-power witness.

- [ ] **Step 4: Run Task 3 tests and verify GREEN**

Expected: all literal pumping/comparison tests PASS and all real schema/cell templates build without a missing boundary.

- [ ] **Step 5: Commit Task 3**

```bash
git add -f .scratch/test_period_two_old_new_cut_load_certificate.py .scratch/period_two_old_new_cut_load_certificate.py
git diff --cached --check
git commit -m "Certify old-new all-power comparisons"
```

---

### Historical Stage 4: Build the 9,408 Load Histograms and Family Ledger

**Files:**
- Modify: `.scratch/test_period_two_old_new_cut_load_certificate.py`
- Modify: `.scratch/period_two_old_new_cut_load_certificate.py`

**Interfaces:**
- Consumes: active collision fibers, 84 B-tokens, templates, comparison witnesses.
- Produces: `comparison_record`, `histogram_for_load`, `family_ledger`, and `build_manifest`.

- [ ] **Step 1: Add failing comparison and census tests**

Use literal comparison fixtures to pin:

- fixed-vs-correction literal leaf chronology;
- distinct-occurrence AST chronology;
- equal-coordinate exclusion;
- positive same-occurrence module order; and
- negative same-occurrence reversal.

Add a manifest-summary test with hand-written expected counts:

```python
assert summary["load_rows"] == {
    "fixed": 1120, "base": 32, "singleton": 16,
    "P": 1728, "C": 624, "Q": 5888,
}
assert summary["total_load_rows"] == 9408
assert summary["occurrence_loads"] == {
    "fixed": 1120, "base": 64, "singleton": 96,
    "P": 3456, "C": 1248, "Q": 11776,
}
assert summary["total_occurrence_loads"] == 17760
assert summary["b_tokens_per_occurrence"] == 84
assert summary["active_comparisons"] == 1491840
```

- [ ] **Step 2: Run the new tests and verify RED**

Expected: FAIL because comparison histograms and family ledgers are absent.

- [ ] **Step 3: Implement comparison records and histogram partitioning**

For each source-fiber/cell load, iterate its exact old occurrence footprint and
compare every occurrence with all 84 B-tokens exactly once.  The bucket key
contains the old occurrence/leaf, B source class/coordinate, equality
exclusion, old polarity, module method/order, chronology order, label
method/order, and contribution bit. Store sorted bucket records with count
and 84-bit mask encoded as 21 lowercase hexadecimal digits.

Validate independently for every footprint occurrence: all masks are
disjoint, their union is `2^84-1`, the sum of bucket counts is 84, and each
count equals the bit count of its mask.  Then derive each grouped load's bit
as the xor of all contributions over its complete footprint.

- [ ] **Step 4: Implement family xor and fail-closed expectations**

Derive counts from active fibers. Assert, rather than assign, the expected family/cell values: fixed 0, base 0, singleton 1, P 0, C equal to `int(a==0)`, Q 0. On mismatch raise `CertificateFailure` containing the family, cell, and first odd load IDs. The manifest status remains `unverified` until every assertion and source check passes; only then set `status = "proved-positive-chamber-old-new-cut"`.

- [ ] **Step 5: Run Task 4 tests and verify GREEN**

Expected: all census and family tests PASS within 30 seconds. If the run times out, replace repeated word expansion with caches keyed by `(schema_id, cell_id)` and comparison caches keyed by `(left_schema, right_schema, cell_id)`; do not rerun unchanged.

- [ ] **Step 6: Commit Task 4**

```bash
git add -f .scratch/test_period_two_old_new_cut_load_certificate.py .scratch/period_two_old_new_cut_load_certificate.py
git diff --cached --check
git commit -m "Materialize old-new grouped load ledger"
```

---

### Historical Stage 5: Canonical Manifest CLI and Independent Verifier

**Files:**
- Modify: `.scratch/test_period_two_old_new_cut_load_certificate.py`
- Modify: `.scratch/period_two_old_new_cut_load_certificate.py`
- Create: `.scratch/period_two_old_new_cut_load_verify.py`

**Interfaces:**
- Consumes: canonical manifest schema and upstream bound artifacts.
- Produces: generator `--write/--check/--summary` CLI and verifier `verify_manifest(Path)` plus `--check PATH` CLI.

- [ ] **Step 1: Add failing end-to-end and mutation tests**

Write the generated manifest to `.scratch/test-artifacts/old-new-load/manifest.json`. Verify byte-for-byte regeneration. Copy the JSON object in memory, mutate one field at a time, write a distinct project-local file, and require the verifier to reject:

1. one token mask bit;
2. one raw coefficient;
3. one pumping boundary copy ID or terminal field;
4. one dropped or redirected schema/cell identity mapping;
5. one schema or cell table entry;
6. one family parity; and
7. one dependency digest.

The tests assert exception categories, not exact error prose.

- [ ] **Step 2: Run the verifier tests and verify RED**

Expected: FAIL because the independent verifier file does not exist.

- [ ] **Step 3: Implement generator CLI**

`--write` writes canonical JSON only after successful build. `--check` rebuilds in memory and requires byte equality with the requested path. `--summary` builds without writing and prints only computed counts/status. All writes use a sibling temporary file under the target's project-local directory followed by `Path.replace`.

The template catalog uses format `task4-template-catalog-v2`.  Per family it
stores an ASCII-sorted `schema_table`, ASCII-sorted `cell_table`, a compact
first-seen `witness_table`, and one `identity_witness_ids` integer per
schema-major/cell-minor identity.  Witness fields are terminal letter,
terminal deletion, and compact pump tuples `(block_index, base_copies, slopes,
split, left_copy, right_copy, left_offset, right_offset)`.  Declare all field
orders and use a Python 3.9 standard-library typed encoder with explicit type
tags and four-byte big-endian lengths for rolling `identity_sha256` and
`replay_sha256`.  Compute canonical JSON and `catalog_sha256` once per compact
family catalog, never once per template.

Before a second full run, benchmark extraction/intering and final compact
serialization on every eighth sorted schema in every family plus the
complete sorted set of schemas attaining that family's maximum pump count.
Report every tied maximum schema ID.  Project by exact family schema ratios
and emitted byte counts; proceed only when twice the projection is below
three seconds.
The full generator must measure less than six seconds of catalog overhead and
less than 30 seconds total.  Do not call `Template.to_record`, canonical JSON,
or SHA-256 separately for all 48,252 identities in the hot ledger pass.

- [ ] **Step 3A: Bind complete sources before implementing the verifier**

Add canonical `source_bindings` with format `task4-source-bindings-v1` and
exact fields `format`, `old`, `b`, and `sha256`.  Retain the complete proof
objects returned by `build_old_rows()` and `build_b_catalog()` in
`Task4SchemaCatalog`, then serialize those exact objects.  The old proof binds
every active and inactive base/P/C/Q integral fiber, aligned member IDs and
integer coefficients, integral sum, parity/active state, collision key,
label-equality witness, and each member's exact domain and
`current_equality`.  It separately stores complete one-member fixed and
singleton source records.  Bind all 21 anchor `id`/coefficient rows, their
computed sum, V/W/A raw provenance counts, raw-ID uniqueness, and the empty
missing-provenance result.  The B proof binds all 53 active and inactive
collision fibers, aligned member/coefficient pairs, sum/parity/active state,
slot/module schema, and complete label-equality witness.

Declare `typed_encoding = task4-typed-sha256-v1`.  Implement the design's
exact typed encoder and rolling preimage: format, typed-encoding version,
family, field orders, identity order, the four declared counts, complete
sorted schema table, complete sorted cell table, complete first-seen witness
table, and then every schema-major/cell-minor mapping.  The identity hash adds
`[schema_index, cell_index, witness_id]`; the replay hash additionally adds
the dereferenced witness after each mapping.  The catalog hash binds every
catalog field except itself.  Reject unknown/missing fields, non-ASCII or
unsorted IDs, unused witnesses, and a witness table that is not canonical
first-seen order.

Before checking hashes, validate the complete positional grammar: schema
variables and cell names are string lists; every block has exact width three,
a string name, a non-boolean-integer word list, and `null` or an aligned
non-boolean-integer affine list; cell states are aligned int-or-null lists with
booleans rejected and base values are aligned non-boolean integers.  Every
witness has exact width three, an int-or-null non-boolean terminal, an exact
boolean deletion flag, and a pump list.  Every pump has exact width eight,
non-boolean integer scalar fields, and a non-boolean-integer slope list.
Validate block indices, affine/base/slopes, consecutive in-range copy IDs,
core offsets, distinct ordered splits, and schema/cell variable alignment
against each dereferenced identity.  Add fully rehashed mutations for an
extra pump field and a non-boolean deletion value.

Use strict TDD.  Freeze literal typed-encoding and SHA-256 vectors for `None`,
both booleans, signed integers, UTF-8 strings, nested lists, and sorted
mappings.  Add focused mutations for an inactive old-fiber coefficient, old
member domain, old member `current_equality`, inactive B-fiber coefficient or
member alignment, anchor provenance, an appended unused witness, and a
semantic-preserving witness-table permutation/reindexing with all hashes
recomputed.  Run only these compact/source-binding tests through the 30-second
foreground guard with one CPU thread.  Leave the two-line verifier stub
unchanged and preserve status `generated-awaiting-independent-replay`.

- [ ] **Step 4: Implement the verifier independently**

Do not import the generator. Re-declare the JSON schema, free/cyclic reduction, cell algebra, tagged boundary checks, affine comparison checks, source adapters, collision grouping, chronology rule, bucketization, and family xor. Reconstruct all 48,252 schema/cell templates from the compact schema/cell/witness catalogs, then recompute every load and family value from upstream sources and compare canonical structures to the manifest. A digest match alone is insufficient.

- [ ] **Step 5: Run end-to-end and all mutation tests and verify GREEN**

Expected: pristine PASS; every mutation is rejected; no file remains in `.scratch/test-artifacts/old-new-load/` after test cleanup.

- [ ] **Step 6: Run Ruff and compilation through the guard**

Run:

```bash
UV_CACHE_DIR=.scratch/uv-cache PYTHONDONTWRITEBYTECODE=1 python3 scripts/run_proof_guarded.py --timeout-seconds 30 -- uv run --with ruff==0.16.0 ruff check .scratch/period_two_old_new_cut_load_certificate.py .scratch/period_two_old_new_cut_load_verify.py .scratch/test_period_two_old_new_cut_load_certificate.py
```

Then run `python3 -m py_compile` through the same guard with `PYTHONPYCACHEPREFIX=.scratch/pycache`.

- [ ] **Step 7: Commit Task 5**

```bash
git add -f .scratch/period_two_old_new_cut_load_certificate.py .scratch/period_two_old_new_cut_load_verify.py .scratch/test_period_two_old_new_cut_load_certificate.py
git diff --cached --check
git commit -m "Independently replay old-new load certificate"
```

---

### Historical Stage 6: Materialize, Replay, and Document the Theorem Artifact

**Files:**
- Create: `.scratch/period_two_old_new_cut_load_manifest.json`
- Create: `.scratch/period_two_old_new_cut_load_certificate.md`
- Modify only if a discovered bug has a failing test first: the three Task 5 code/test files.

**Interfaces:**
- Consumes: generator and verifier CLIs.
- Produces: committed manifest and proof memo.

- [ ] **Step 1: Generate the canonical manifest under the guard**

Run the generator `--write`, then `--check`, then the independent verifier `--check .scratch/period_two_old_new_cut_load_manifest.json`, each as a separate guarded foreground command. Expected: all three exit zero within 30 seconds.

- [ ] **Step 2: Audit hashes and prohibited claims**

Compute SHA-256 for generator, verifier, test, manifest, every upstream binding, and design spec. Search generator, verifier, manifest, and memo for `Q(A_(n,d))=[d=0]`, `d0_endpoint_branch": true`, hard-coded failure counters, and imports of `period_two_old_new_cut_covariance_checker`; every search must be empty.

- [ ] **Step 3: Write the proof memo**

State only the theorem actually replayed:

```text
B(A_(n,d), b_(n,d)) = [d>1] for n>=0 and d>=1,
so B(A_(n+1,d), b_(n+1,d)) = B(A_(n,d), b_(n,d)).
```

Include the six computed family tables, 9,408 source loads, 17,760
occurrence-loads, 1,491,840 active comparisons, raw-fiber census, all-power
witness counts, exact hashes, guarded replay commands, and independent
verifier result. State explicitly that the d=0 endpoint, Q(A), covariance
outside this cut, AC, and stable AC remain open.

- [ ] **Step 4: Run the complete focused suite and deterministic replay**

Run all focused pytest tests, Ruff, compile, generator `--check`, and independent verifier. Expected: every command exits zero, no warning, no timeout, and no guard lock remains.

- [ ] **Step 5: Hostile mathematical review**

Give a reviewer only the design, manifest, memo, upstream proof notes, generator, verifier, and fresh command output. Require APPROVE/REVISE/BLOCK on source binding, integral-before-parity logic, pumping hypotheses, mask completeness, family arithmetic, and theorem scope. Any substantive finding gets a failing regression test before a code change.

- [ ] **Step 6: Commit the materialized certificate**

```bash
git add -f .scratch/period_two_old_new_cut_load_manifest.json .scratch/period_two_old_new_cut_load_certificate.md .scratch/period_two_old_new_cut_load_certificate.py .scratch/period_two_old_new_cut_load_verify.py .scratch/test_period_two_old_new_cut_load_certificate.py
git diff --cached --check
git commit -m "Prove the positive old-new cut identity"
```

Do not use this commit message if the verifier or hostile review fails; instead commit the bounded failed attempt with an explicit non-proof status.

---

### Historical Stage 7: Integrate the Cut Lemma and Resume the Proof Loop

**Files:**
- Modify only the existing period-two proof note that owns the seven-family theorem, after resolving its exact tracked path with `rg --files`.
- Create a new integration test or replay artifact if the lemma changes a theorem status.

**Interfaces:**
- Consumes: independently verified cut lemma.
- Produces: the next exact residual theorem obligation toward AK(3), never an unsupported AC/stable-AC claim.

- [ ] **Step 1: Substitute the verified cut formula into the seven-family derivation**

Check every hypothesis and domain (`n>=0,d>=1`) at the use site. Recompute the residual equation symbolically; do not infer that the separate `d=0` endpoint or unary delta law follows.

- [ ] **Step 2: Try to falsify the integrated derivation**

Audit signs, lower/uppercase generator spellings, stable-vs-unstable move status, and every transition from integer coefficients to parity. If a new computational replay is needed, add its failing test first and run it only through the guard.

- [ ] **Step 3: State the next proof obligation**

If integration closes covariance, identify the exact remaining edge/unary law needed for the stable-AC resolution. If it does not, isolate the smallest surviving family or endpoint formula. Continue the understand -> proof -> verify -> new-proof loop; do not mark the goal complete.

- [ ] **Step 4: Commit, log, and push the verified increment**

Follow the mandatory two-commit log protocol with UTC time and the log-body commit short SHA, verify a clean status, then push only `codex/proofs`.
