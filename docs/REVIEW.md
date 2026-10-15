# Adversarial review of main, 13 October 2026

**TL;DR.** An engineering review of [`f4d5d211`](https://github.com/Avi161/ACSolverX/commit/f4d5d211eb747031b23430c0b6c545d8834474da)
(the `acx` consolidation and the two stored stable-AC studies) found **1 high-impact (P1) and 10 reproducible (P2)
defects**, all fixed with boundary tests in [`tests/test_review_regressions.py`](../tests/test_review_regressions.py);
one suspected bug (PPO's reward normaliser) is kept on purpose. It is not a proof of the
Andrews-Curtis conjecture, nor an audit of every presentation.

**Scope.** Input parsing, word and move semantics, spec/fast search, cap accounting, automorphisms and transport, CoV,
hybrid and n-generator search, rank-n persistence, policy inference and PPO, runner and report, packaging, CI and the
docs. Adversarial cases targeted what the ordinary examples miss: path-shaped identifiers, interrupted writes, changed
inputs, malformed types, optional verification and episode ends. **P1**: a high-impact correctness or data-loss issue;
**P2**: a reproducible defect or missing safeguard in a supported workflow.

## Findings and fixes

| # | | problem | fix |
|---:|---|---|---|
| 1 | P1 | **Output names could escape their directory.** `name=".."`, absolute names and separators were accepted, and `rankn --fresh` then ran `rmtree` on the joined path. `row_path(run, "../outside")` wrote outside `rows/`; an id containing `.npz.tmp` was written but skipped as an interrupted file | `runner/storage.py` checks a name is one component and the run folder has no symlinks, before any write, in both drivers and the CLI; the runner rejects symlinked output files. Rank-n row ids are percent-encoded (dots included) and decoded on listing; `rows/` symlinks are refused. Numeric file names are unchanged; older custom names need a new folder |
| 2 | P2 | **Rank-n `--fresh` deleted its own input**: `--pres ... --fresh` wrote `input.txt`, then deleted the run folder, breaking resume and verification | fresh clears only known result files and `rows/`, keeping `input.txt` and unrelated files |
| 3 | P2 | **A sliced rank-n resume could mix datasets**: after changing row `b` and resuming only `a`, the summary still used the old `b` | every stored row is checked against the full input and sweep identity before results change (reading only each archive's metadata member); a changed or removed row needs a new name or `--fresh` |
| 4 | P2 | **Reruns and comparisons matched ids, not presentations** (`--solved-from`, `compare.py --common`, head-to-head) | they compare stored `pres`; decode-later refuses a mismatch before writing. Records without `pres` keep id-only matching (their identity cannot be established afterwards) |
| 5 | P2 | **Interrupted records meant different things** to resume and reports (a last line without its newline counted as a solve in reports) | one streaming reader, `iter_records`, defines completeness, blank lines and minimal schema checks (`read_records` wraps it); only an incomplete final record is repaired, an earlier broken line or bad identity/status type raises with its location |
| 6 | P2 | **Interrupted metadata writes** could leave invalid `config.json`, blocking resume | configs, summaries, rewritten records and inline input are replaced atomically (written and flushed first); one process owns a run folder, `workers` parallelise inside it |
| 7 | P2 | **CoV and RL ignored `path=false`**: they captured, transported and replayed paths anyway, then hid them | CoV honours `search.capture_path`, uses the search depth for `sub_moves` and still types a solve by orbit; RL skips action histories; both skip replay, and verifying a pathless CoV outcome raises. CoV start dedup uses the search's fixed-point `normal(cyclic)` |
| 8 | kept | **PPO's normaliser clears the return with the current step's `done` before adding its reward** (rewards `1, 2 (terminal), 3`, gamma `0.5`: moments see `1, 2, 4`, not `1, 2.5, 3`) | this is the JAX trainer's `NormalizeVecReward` (`experiments/ppo`, `wrappers.py`) that trained the shipped weights, with its other quirk (each update weighs the observation length); changing it would stop training reproducing the checkpoint, so a three-step test pins the order |
| 9 | P2 | **`path_len` was `int16`** while `SweepConfig` accepts 65,535 pops: a path over 32,767 raised `OverflowError` and lost the row | `int32`, `-1` still unsolved; old files stay readable; the test injects a 40,000-step result |
| 10 | P2 | **Malformed symbols changed the input**: `Presentation(2, ((1.9,), ("2",)))` became `<x,y \| x,y>`; bools and any rank were accepted | rank must be a nonnegative integer and symbols integral (NumPy integers allowed); plain ints skip the `Integral` check, without which replay was 2.5 times slower (with it, replay takes about a quarter less time than before). Rank zero stays for destabilisation |
| 11 | P2 | **`nan` and `inf` passed** as `rl.alpha` and `hybrid.dyn_ratio` | one finite-number check; the RL entry point also checks width, steps, capture and alpha |
| 12 | P2 | **Optional RL code was absent from CI**, and the docs overstated verification (replay shares words and moves with the reference engine; `path=false` skips verification) | a CPU PyTorch CI job runs policy/JAX parity, legal moves and cap behaviour, beam replay, PPO, runner integration and the review regressions; the docs state those limits |

## 14 October follow-up

On [`a7174816`](https://github.com/Avi161/ACSolverX/commit/a7174816c9bf6876b4434478e0ba1995e3485750) (after #29 to #33),
ten more P2 defects, each fixed with a test:

| # | problem | fix |
|---:|---|---|
| 1 | **CoV built the whole family before its first search**, even when the control solved | `iter_images` streams the same ordered family (`enumerate_images` wraps it); `stats.images` now counts the generated prefix, `images_exhausted` says whether it finished. 20 easy MS640 rows: 25.9 → 4.4 ms (default family), 473 → 4.6 ms (exhaustive) |
| 2 | **The rank-n sweep did unused work**: captured every path for a 0.2% sample, cached every combination (47,071,588,320 tuples for 6,560 words and three generators), rehashed the pool | capture is decided before the search; `combos` is a lazy indexable sequence in itertools order; results fill NumPy columns; the pool digest is cached. Runtime is unchanged (11.57 vs 11.69 s on 320 starts) |
| 3 | **PPO minibatches**: one sample gave NaN advantages, a remainder gave extra steps, unknown settings were ignored | exactly `minibatches` nonempty groups, no normalisation of a singleton, unknown or out-of-range settings and bad initial states refused |
| 4 | **Selectors changed ids**: `--solved-from` split `one,two`, `--rows` went through TOML, an empty `--rows` kept the slice, the sweep CLI ran a hybrid config as rank-n, `--verify -1` skipped every recheck | literal id lists, no TOML reparse, empty `--rows` selects all, the sweep requires `method = 'rankn'` and a nonnegative recheck |
| 5 | **Resume could mix implementations**: `config.json` misses solver code, dependencies and the RL checkpoint | `runner/provenance.py` records source, runtime and each invocation; both drivers refuse drift before writing. Older folders are marked untracked; direct PPO calls are not tracked |
| 6 | **Cyclic `normal` always ran a second, unchanged pass** | one pass for `cyclic=True` (rotations and inverses of a cyclically reduced word stay reduced); the loop stays for `cyclic=False` |
| 7 | **The RL beam carried the value bonus** into the next step's log probability (`0, 7, 14` instead of `0, 0, 0`) | ranking scores and log probabilities are separate; `alpha=0` is unchanged, nonzero-alpha runs need a rerun |
| 8 | **Duplicate record ids** counted differently in resume and reports | the shared reader refuses duplicates with both line numbers |
| 9 | **A three-run comparison skipped the identity check** | the table checks `pres` for any number of runs |
| 10 | **The speed gate passed failed workloads** (errors, skips, zero rows, non-finite times, `--repeat 0`) | it refuses them; rank-n's time is labelled wall time; the 2% threshold is unchanged |

## Limits left open

- **Run provenance**: new runs carry source and runtime manifests (follow-up 5); older runs and direct training calls do
  not, and the dependency lock and input files must be archived separately.
- **Independent assurance**: spec/fast parity and replay share definitions; a separate checker or a formalisation
  would catch common-mode errors.
- **Scale**: `data.rows` materialises a dataset before `--rows`, and rank-n word pools are materialised; large AC1M
  loads and high-rank pools need a streaming or sharded API.
- **Historical evidence**: summary-only runs carry no replayable paths, and the study manifests list raw files not in
  this checkout; this review does not reproduce every multi-million-search study.
- **Deployment**: local CPU runs are validated; GPU training, clusters and simultaneous writers to one folder are not.

The package already separates words, search, transforms, transport, runs and reports into small modules; the useful
change was consolidating persistence rules, not a broad search rewrite.

## Validation

The unmodified base passed **1,250 tests** (**8 skipped**, **95 slow deselected**) without PyTorch; the adversarial
reproductions then failed against it. The fixes were validated by the boundary tests, the default and slow selections,
CPU PyTorch integration, the checkpoint's JAX references, a fresh CLI smoke run, compilation and `git diff --check`.
Final counts are in the pull request.
