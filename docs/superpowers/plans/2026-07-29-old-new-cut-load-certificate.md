# Old--New Cut Grouped-Load Certificate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate and independently replay a fail-closed, all-power certificate for the positive-chamber old--new cut identity using 9,408 collision-first load histograms.

**Architecture:** A generator reconstructs approved old rows and the 84-token B-factor from bound upstream artifacts, proves the threshold-three pumping comparisons, collision-aggregates over the integers, and writes canonical JSON. A second program reads the JSON and independently reconstructs every source row, cell, comparison, token mask, and parity without importing generator code.

**Tech Stack:** Python 3.9-compatible standard library, existing project-local period-two proof modules, pytest, Ruff 0.16.0, and `scripts/run_proof_guarded.py`.

## Global Constraints

- Create only new proof artifacts; do not modify solvers, runners, notebooks, or existing period-two certificate code.
- Never import `.scratch/period_two_old_new_cut_covariance_checker.py` as a trusted dependency.
- The independent verifier must not import the generator.
- Do not assert `Q(A_(n,d))=[d=0]`; the certificate domain is exactly `n>=0, d>=1`.
- Treat the 9,408-load census, 790,272 active comparisons, and six family values as `[unverified]` until both generator and independent replay pass.
- Run every test, checker, linter, compiler, or proof command in the foreground through `scripts/run_proof_guarded.py`, with one job and a 30-second deadline; never exceed 60 seconds.
- Never rerun an unchanged timed-out command. Reduce allocation or simplify the algorithm first.
- Never write temporary artifacts under `/tmp`; use `.scratch/test-artifacts/old-new-load/`.
- Keep Python 3.9 compatibility: no `zip(..., strict=True)` and no mode-0644 shebangs.
- Before each push, follow the two-commit timestamp/SHA log protocol in `AGENTS.md`.

---

## File Map

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

### Task 1: Cell Algebra and Complete 84-Token Masks

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

### Task 2: Bound Sources and Aggregate Integral Collision Fibers

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

### Task 3: Materialize All-Power Pumping and Shortlex Witnesses

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

### Task 4: Build the 9,408 Load Histograms and Family Ledger

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
assert summary["b_tokens_per_load"] == 84
assert summary["active_comparisons"] == 790272
```

- [ ] **Step 2: Run the new tests and verify RED**

Expected: FAIL because comparison histograms and family ledgers are absent.

- [ ] **Step 3: Implement comparison records and histogram partitioning**

For each active old `TokenRef`, compare all 84 B-tokens exactly once. The bucket key contains B source class/coordinate, equality exclusion, old polarity, module method/order, chronology order, label method/order, and contribution bit. Store sorted bucket records with count and 84-bit mask encoded as 21 lowercase hexadecimal digits.

Validate within each load: all masks are disjoint, their union is `2^84-1`, sum of bucket counts is 84, and each count equals the bit count of its mask.

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

### Task 5: Canonical Manifest CLI and Independent Verifier

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
3. one pumping boundary copy ID;
4. one family parity; and
5. one dependency digest.

The tests assert exception categories, not exact error prose.

- [ ] **Step 2: Run the verifier tests and verify RED**

Expected: FAIL because the independent verifier file does not exist.

- [ ] **Step 3: Implement generator CLI**

`--write` writes canonical JSON only after successful build. `--check` rebuilds in memory and requires byte equality with the requested path. `--summary` builds without writing and prints only computed counts/status. All writes use a sibling temporary file under the target's project-local directory followed by `Path.replace`.

- [ ] **Step 4: Implement the verifier independently**

Do not import the generator. Re-declare the JSON schema, free/cyclic reduction, cell algebra, tagged boundary checks, affine comparison checks, source adapters, collision grouping, chronology rule, bucketization, and family xor. Recompute every value from upstream sources and compare canonical structures to the manifest. A digest match alone is insufficient.

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

### Task 6: Materialize, Replay, and Document the Theorem Artifact

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

Include the six computed family tables, 9,408 load rows, 790,272 active comparisons, raw-fiber census, all-power witness counts, exact hashes, guarded replay commands, and independent verifier result. State explicitly that the d=0 endpoint, Q(A), covariance outside this cut, AC, and stable AC remain open.

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

### Task 7: Integrate the Cut Lemma and Resume the Proof Loop

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
