# Adversarial review of main — 13 October 2026

Reviewed base: [`f4d5d211eb747031b23430c0b6c545d8834474da`](https://github.com/Avi161/ACSolverX/commit/f4d5d211eb747031b23430c0b6c545d8834474da).
The review includes the `acx` consolidation and the two stored stable-AC studies.

The review traced input parsing, word/move semantics, spec/fast search, cap accounting, automorphisms and certificate
transport, CoV, hybrid and n-generator search, rank-n persistence, policy inference and PPO, runner/report behavior,
packaging, CI and the documentation. Adversarial cases targeted boundaries the ordinary examples did not exercise:
path-shaped identifiers, interrupted writes, changed inputs, malformed types, optional verification and episode ends.
This is an engineering review with executable checks, not a proof of the Andrews–Curtis conjecture or an exhaustive
audit of every possible presentation.

## Findings and fixes

P1 means a high-impact correctness or data-loss issue; P2 means a reproducible defect or a missing safeguard in a
supported workflow. All fixes below are included in this change. The new boundary cases are in
[`tests/test_review_regressions.py`](../tests/test_review_regressions.py); existing method, runner and report tests
check compatibility with normal inputs.

### 1. P1 — output identifiers could escape their directory

`load_config` accepted `name=".."`, absolute names and path separators. `rankn --fresh` then called `rmtree` on the
joined path, potentially deleting the parent or a different directory. Separately, `row_path(run, "../outside")`
produced `run/rows/../outside.npz`; an absolute CSV/JSONL id escaped the run entirely. An id containing `.npz.tmp`
could be written but silently omitted by `finished_rows`, which treated it as an interrupted temporary file.

`runner/storage.py` now validates a name as one component, checks the run directory for symlinks, and is used by both
drivers and the CLI before writes. The ordinary runner also rejects symlinked output files. Rank-n row ids are
percent-encoded, including dots, and decoded on listing; `rows/` symlinks are refused before writes. The regression
tests use temporary directories and verify round-trip identity and containment. Numeric benchmark filenames are
unchanged. Older custom filenames containing encoded characters need regeneration in a new folder.

### 2. P2 — rank-n fresh runs deleted their own input

`run.py --pres ... --fresh` wrote `input.txt`, loaded the rows, then recursively deleted that same run folder in the
rank-n driver. The completed config referenced a missing input, breaking later resume and verification. Fresh now
clears only known result files and `rows/`, preserving `input.txt` and unrelated files. A regression performs a run,
a fresh rerun and a resume and checks that the input remains readable.

### 3. P2 — a sliced rank-n resume could mix different datasets

The sweep checked the identity of selected row files, but its summary included every stored row. After running rows
`a,b`, changing `b` in the input and resuming only `a` silently included the old `b` results under the current input.
The driver now checks every stored row against the full input and sweep identity before changing results. A removed
or changed row is refused with instructions to use a new name or `--fresh`. Unchanged rows outside the selection still
contribute to the run summary, preserving incremental execution.
Identity checks read only the metadata member of each row archive, without decompressing search arrays or paths.

### 4. P2 — reruns and comparisons matched ids without checking presentations

`--solved-from` selected ids even when the new input gave those ids different words. `compare.py --common` and the
head-to-head report checked the benchmark name/path, but files at that path can change. Both workflows now compare
stored `pres` values. Decode-later rejects a mismatch before writing its inline input. Reports retain `pres` in their
compact records and refuse invalid pairings. Legacy records without `pres` retain id-only compatibility; their
identity cannot be established retrospectively, and this limitation is documented.

### 5. P2 — interrupted records had different meanings to resume and reports

A last line `{"id":"b","solved":true}` without a newline was ignored by resume but counted as a solve by the
report. The duplicate parsers also differed on blank lines and accepted malformed record shapes. A shared streaming
`iter_records` now defines completeness, blank-line handling and minimal schema validation. `read_records` is its
materializing wrapper. Reports discard large path payloads as they stream. Only an incomplete final record is
repairable; an earlier broken line or an invalid identity/status type is rejected with its location.

### 6. P2 — interrupted metadata writes could make expensive runs unresumable

Configs, summaries and the record rewrite after changed inputs used truncating writes. A process interrupted during
`config.json` replacement could leave invalid JSON, so the next resume failed before it could use intact row files.
Shared atomic replacement writes and flushes a temporary file before replacing the destination. It is used for those
documents and inline input. An injected replacement failure verifies that the old JSON remains intact and temporary
files are cleaned up. This is atomic replacement of individual files, not a multi-file transaction or a concurrency
lock; one process must own a run folder, using `workers` for parallel rows.

### 7. P2 — CoV and RL ignored the high-speed verification contract

CoV forced `capture_path=True` in every search leg, transported paths and called `verify` even when the runner had
`path=false`. RL likewise built action histories, converted them to S-moves and replayed them. The final record hid
the certificate, so it looked like a high-speed run despite doing the costly work. The README, method docstrings and
usage guide disagreed about this exception.

CoV now honors `search.capture_path`, uses the search depth for `sub_moves`, and retains orbit classification without
transporting a certificate. RL now accepts `capture_path`, avoids allocating action histories when false, and retains
the solution depth/final state. Both skip replay in that mode; explicit verification of a pathless CoV outcome raises
an error. Default certificate behavior remains enabled. Tests replace certificate functions with failures to prove
they are not called; existing runner tests compare solves, costs, kinds and counters between both modes. CoV start
deduplication also uses the same fixed-point `normal(cyclic)` state as the search.

### 8. Kept — PPO's reward normalizer resets the return before adding the terminal step's reward

`VecEnv._normalise` clears the accumulated return with the *current* step's `done` before adding its reward, so for
rewards `1, 2 (terminal), 3` with gamma `0.5` its running moments observe `1, 2, 4`, not the textbook `1, 2.5, 3`.
This is the JAX trainer's `NormalizeVecReward` (`experiments/ppo`, `wrappers.py`), the one that trained the shipped
weights, reproduced exactly with its other quirk (each update weighs the observation length). Changing it would make
the trainer stop reproducing the checkpoint's training, so it stays; a three-step test pins the order and the docs
say why.

### 9. P2 — supported sweep budgets exceeded the path-length storage range

`SweepConfig` accepts 65,535 pops, but `path_len` was `int16`. A legitimate path length above 32,767 raised
`OverflowError` with the pinned NumPy, losing the row's work at serialization. Path lengths now use `int32`, retaining
`-1` for unsolved; old int16 row files remain readable. The boundary test injects a 40,000-step result into the row
serializer, avoiding an artificial long search merely to test storage.

### 10. P2 — malformed generator symbols silently changed mathematical input

`Presentation(2, ((1.9,), ("2",)))` became `<x,y | x,y>` because construction called `int` on every symbol. Bools
were also accepted, and rank had no type/range check. The constructor now requires a nonnegative integral rank and
integral symbols, preserving NumPy integer support while rejecting floats, strings and bools before coercion. Tests
cover both rejection and the legitimate array-scalar API. Rank zero remains available for stable destabilization.
Plain in-range ints, which every search and replay step builds, skip the `Integral` check: without that fast path the
check made replay 2.5 times slower; with it, replay takes about a quarter less time than before.

### 11. P2 — non-finite numeric settings were accepted

TOML accepts `nan` and `inf`. `rl.alpha=nan/inf` passed configuration loading, producing undefined beam scores;
`hybrid.dyn_ratio=inf` was also accepted. A shared finite-number predicate now validates these parameters. The public
RL solve entry point also checks width, steps, capture and alpha, so direct library use gets the same basic contract.

### 12. P2 — optional RL code was absent from CI; verification claims overstated independence

The only CI job installed `.[dev]`; all PyTorch checks were skipped. A separate CPU job now runs policy/JAX reference
parity, legal moves and cap behavior, beam replay, PPO, runner integration and the review regressions. The default
minimal job remains available without PyTorch.

The methods guide claimed replay shared nothing with the solver and that every recorded solve was verified. Replay
shares Python words/moves with the reference engine, and `path=false` deliberately omits verification. The docs now
state those boundaries, the capture behavior, output naming, resume identity, encoded row filenames, storage range
and the PPO normalizer's order. The architecture guide names the new persistence boundary rather than leaving duplicated
behavior hidden in CLI/report code.

## Architecture and research limits

The `acx` package already separates word operations, search engines, transforms, certificate transport, run management
and reporting into small modules. The useful modularization change here is consolidating persistence rules; a broad
search rewrite would make mathematical regression review harder without addressing an observed fault.

Further work, distinct from the fixed defects:

- **Run provenance:** configs and per-row words identify settings and input, but do not record the executing source
  revision, dependency lock, device or hardware. Reproduction across revisions should use a new run name and record
  those externally. A versioned provenance manifest would make this machine-checkable.
- **Independent assurance:** spec/fast parity and replay catch many defects, but share underlying definitions.
  A separately implemented checker or formalization would reduce common implementation errors.
- **Scale:** `data.rows` materializes a complete dataset before `--rows` selection, and rank-n word pools/combinations
  are materialized. Large AC1M loads and high-rank exhaustive pools need a streaming/sharded API, not larger defaults.
- **Historical evidence:** summary-only published runs do not contain replayable per-row paths. The two study
  manifests explicitly list raw artifacts that are not in this checkout. Tests can check shipped data and selected
  reruns, but this review does not independently reproduce every historical multi-million-search study.
- **Deployment scope:** local CPU execution is validated. GPU training, cluster execution and simultaneous writers
  to one output directory are not covered by this change.

## Validation

The unmodified base's default suite passed **1,250 tests**, with **8 skipped** and **95 slow tests deselected** in
the initial environment without PyTorch. Adversarial reproductions then failed against that base. Validation of the
fixes includes the dedicated boundary tests, default and slow selections, CPU PyTorch integration, the checkpoint's
JAX references, a fresh CLI smoke run, compilation and `git diff --check`. Final command outcomes and counts are
recorded in the pull request, so this report does not claim a test run before it has completed.
