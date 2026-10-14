# Follow-up adversarial review — 14 October 2026

Base: [`a7174816`](https://github.com/Avi161/ACSolverX/commit/a7174816c9bf6876b4434478e0ba1995e3485750), after the merged
review (#29), packed search (#30), documentation/speed checks (#31), runner memory work (#32) and hybrid kernels (#33).
This report records additional experiment-integrity and avoidable-work findings. The earlier report remains in
[REVIEW.md](REVIEW.md). The new changes preserve the optimized engines and the intentional JAX reward-normalizer order.

P2 denotes a reproducible defect or missing safeguard in a supported workflow. Each finding includes impact, the
change and checks. This is a bounded engineering review, not a claim that every possible defect has been found.

## Findings and fixes

### 1. P2 — CoV generated all alternatives before checking the control

`run_cov` materialized the complete CoV family before its first search. Even an immediate control solve or a total
budget of one pop paid for every substitution, image and equivalence-class calculation. Exhaustive families made
this particularly expensive.

`iter_images` now generates the same ordered, deduplicated stream on demand; `enumerate_images` remains the complete
tuple API backed by that one implementation. The runner does not prefetch after exhausting its total budget. Tests
make unused generation fail, retain complete-family digest pins and compare search/cap results. On 20 easy MS640
rows on this branch, an alternating warmed comparison measured 25.9 ms eager versus 4.37 ms streamed for the default
family, and 473 ms versus 4.57 ms for the exhaustive family. These are local wall times for control-solvable rows, not a claim
about the full dataset; see the measurements below.

Compatibility: `stats.images` now counts the generated prefix, and `stats.images_exhausted` says whether generation
finished. Use `enumerate_images` when the full family count is the intended research measurement.

### 2. P2 — the rank-n sweep retained work and memory it never used

Every start captured/replayed a certificate, although the default retains only a deterministic 0.2% sample of solved
paths. The sweep also kept a dictionary for every cell before converting to arrays, cached every word-index
combination, repeatedly recomputed the same pool hash, and decompressed unused certificates while summarizing.
For 6,560 words and three added generators, the eager combination table alone would contain 47,071,588,320 tuples.

Sampling now decides capture before searching, the null stabilisation skips capture, and the control still keeps
its path. Results fill their NumPy columns directly. An indexable lazy combination sequence preserves itertools
order and supports verifier/summary access without constructing preceding combinations; small exhaustive tests pin
every cell index. The pool digest is cached by pool parameters, and archive readers can load selected members.

A preliminary comparison before integration with #30–#33 covered 320 starts and found equality in every stored
field except time. Its three-run
median was 11.57 s before and 11.69 s after, so it does **not** establish an overall runtime improvement. The tests
establish skipped certificate work and bounded combination storage independently. Word pools, per-start arrays and
per-row checkpoint granularity remain scaling limits. `combos` now returns an indexable sequence rather than a tuple;
wrap it in `tuple(...)` only when explicitly materializing a small pool.

### 3. P2 — PPO minibatch boundaries produced NaNs or extra optimizer steps

With one environment, one rollout step and one minibatch, sample standard deviation is undefined; advantage
normalization produced NaNs and optimization corrupted the parameters before the loss check raised. Dividing the
batch size by `minibatches` and stepping by the quotient also produced extra minibatches when division left a
remainder. More minibatches than samples produced a zero range step. Misspelled settings were silently ignored.

The trainer partitions into exactly the requested number of nonempty groups, skips normalization for a singleton,
and rejects unknown/range-invalid settings and invalid initial-state shapes before optimization. Tests use a
seven-sample batch and three minibatches to verify each sample is used once per epoch, exactly six optimizer steps
over two epochs, and equal final parameters across microbatch sizes. A real one-sample training update stays finite.

### 4. P2 — experiment selectors changed literal identifiers or ignored the intended method

`--solved-from` joined ids with commas, so an id `one,two` became two rows and `0:1` became a positional slice. Both
CLIs interpolated `--rows` through a TOML string, corrupting ids containing quotes; an empty `--rows` did not clear
the config's slice. The dedicated sweep CLI also accepted a hybrid config but executed a rank-n experiment with
defaults, and `--verify -1` silently skipped all requested cell rechecks.

Selection now accepts a literal list of ids, decode-later uses that list, and CLI row strings bypass TOML reparsing.
Empty `--rows` explicitly selects every row. The sweep requires `method = 'rankn'` and a nonnegative recheck count
before writing. CLI tests exercise custom punctuation/whitespace ids, invalid options and absence of output on refusal.

### 5. P2 — resume could silently combine results from different implementations

`config.json` equality does not detect changes to solver code, dependency versions or the RL checkpoint. A resumed
folder could therefore mix incompatible implementations while appearing to be one reproducible experiment.

Shared `runner/provenance.py` now records source content and relevant runtime identity plus each invocation's git,
host, thread, worker and selection context. Both drivers check it before changing result files. Fresh runs replace
the history; old folders without it explicitly mark prior results as untracked. Tests cover drift refusal without
mutation, resume extension, fresh reset, absent git metadata and output symlinks. The manifest does not claim old
records' provenance, pin dependencies, track direct PPO training calls or guarantee identical timings across hosts.
The worked [experiment guide](EXPERIMENTS.md) explains how to retain complete evidence and avoid selection bias.

### 6. P2 — cyclic normalization always repeated an already complete pass

`Presentation.normal(cyclic=True)` reduced and canonicalized the presentation, then repeated both operations merely
to discover the result was unchanged. Every search paid for extra word processing and validated object allocations.
Rotations and inverses of a cyclically reduced word are cyclically reduced, so this mode now returns after one pass.
The fixed-point loop remains for `cyclic=False`, where a canonical rotation can expose further free cancellation.
Core and spec/fast parity checks cover both modes; no search ordering or state representation changes.

### 7. P2 — the RL beam accumulated past value bonuses as log probabilities

With nonzero `alpha`, `top_children` added the value heuristic to ranking scores, then the beam reused those scores
as the next step's cumulative log probability. A probability-one path with value 7 and alpha 1 had cumulative values
`0, 7, 14` instead of `0, 0, 0`, so past state values continued biasing later selections contrary to the documented score.

Ranking scores and cumulative log probabilities are now separate; only log probabilities carry forward. An analytic
beam test checks the probability-one case, and a nonzero-alpha policy solve retains capture parity and replay.
Default `alpha=0` behavior and checkpoint weights are unchanged. Nonzero-alpha experiments need to be rerun.

### 8. P2 — duplicate records gave different counts in resume and reports

Resume retained the last record for each id in a dictionary while reports counted both duplicate rows. The same
file could therefore produce different solved counts. The shared reader now refuses duplicate ids with both line
locations, without silently deleting evidence. A regression checks the same refusal in reports and resume.

### 9. P2 — identity checks did not cover a three-run comparison

Two-run head-to-head and `--common` comparisons checked presentation witnesses, but an ordinary comparison of three
runs bypassed both checks. Reusing a dataset path/id for different words could therefore appear as one benchmark.
The common table entry point now checks identities for any number of runs. Historical records without `pres` remain
limited to id-only matching; no missing identity is inferred.

### 10. P2 — failed workloads could be accepted as performance improvements

The ordinary runner records per-row exceptions and can exit successfully with `summary.errors > 0`. The speed gate
read only the time, so an early solver failure could appear faster and pass. Empty/skipped workloads and non-finite
times were not rejected, and `--repeat 0` could produce infinite times with a NaN ratio that evaded the slowdown check.

The harness now refuses errors, skips, zero rows, missing/nonpositive/non-finite times and invalid repetition or
tolerance settings. Tests simulate a successful subprocess that writes each invalid summary, plus valid ordinary
and rank-n summaries. The report also labels rank-n's recorded wall time explicitly rather than describing it as CPU
time. Search correctness remains established by replay and parity checks; the timing gate alone
does not prove semantic equivalence or identical solve sets. The existing 2% slowdown threshold is unchanged.

## Limits and evidence

New runs have source/runtime manifests, but older runs and direct training calls do not. Archive input files and
an environment lock separately. Dataset selection still materializes the input; rank-n word pools/result arrays
remain resident and a row checkpoints only when complete. Replay and spec/fast parity share definitions. Historical
summary-only studies, GPU/cluster execution and concurrent writers are not revalidated by these changes.

The [experiment guide](EXPERIMENTS.md) covers setup, matched comparisons, resume, certificate reruns and retained
evidence. Current-main validation and pipeline performance results are recorded in the PR. The CoV microbenchmark
uses MS640 rows 0–19, cap 24, per-leg/total budgets 1,000 and capture disabled; it alternates eager materialization
and streaming on the same implementation, discards a warm pair and reports six-run medians. It ran on a shared
x86-64 host with Python 3.12.14, NumPy 2.1.3 and Numba 0.63.1 while tests were running. Its outcomes and pop counts
matched. These easy-row measurements isolate generation overhead and cannot predict a full-dataset speed-up.
