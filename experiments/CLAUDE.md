# CLAUDE.md — `experiments/`

This file loads only when Claude reads something under `experiments/`. It maps each source
file to the lessons that have already bitten someone there. Read the linked file *before*
changing the behaviour it describes — each one is a bug that shipped.

Full one-line index of every lesson: the root [`CLAUDE.md`](../CLAUDE.md).
What each directory here *is*: [`README.md`](README.md).

## Layout

| dir | role | README |
|---|---|---|
| `search/` | the two solvers (heavy + compact) — they pop identically | — |
| `stable_ac/` | shared core (`solvern.py`, `word_families.py`) + one folder per pipeline: `nocov/` (Branch A) and `cov/` (Branch B), each with runner + yaml + notebook + colocated tests | [→](stable_ac/README.md) |
| `analysis/` | the stable-AC benchmark (difficulty ladder + reach tier + combined) | [→](analysis/README.md) |
| `equivalence_classes/` | `lib/` `search/` `pipeline/` `verify/` `phases/` + `test_equivalence.py` | [→](equivalence_classes/README.md) |
| `greedy_tests/` | the pipeline's test suite | [→](greedy_tests/README.md) |
| `lessons/` | 38 shipped bugs. Read via the index, not by browsing. | [→](lessons/README.md) |

**Scripts here find the repo root by walking up until they see `experiments/` + `data/` — never by
counting `os.path.dirname()` levels.** A dirname chain encodes the file's depth, so it silently
repoints at the wrong directory the moment the file moves, and every `results/` path below it is then
wrong *without raising*. Keep the walk-up.

## Before you edit…

**`run_baseline.py`** — resume identity and the W&B layer both live here.
- `_run_prefix` / `_resolve_paths` are the resume key. [identity](lessons/jsonl-filename-encodes-search-identity.md) · [no dates in the key](lessons/date-in-filename-broke-resume.md)
- `_repair_jsonl` runs before anything opens the jsonl for append, and is NOT gated on `RESUME`. Every other reader relies on it. [why a reader-side guard is not enough](lessons/run-baseline-two-known-bugs.md)
- The `HIGH_SPEEDUP` pool defers a solved row's *path* to a serial recovery re-solve, but writes the row itself up-front as `path_pending` and rewrites it in place — never park a result in RAM. [why deferred](lessons/high-speedup-boxing-and-memory.md) · [why persisted first](lessons/heavy-mode-defers-solved-rows.md) · [heavy ≡ normal](lessons/high-speedup-verified-locally.md) · [a worker can't print](lessons/heartbeat-worker-cannot-print.md) · [nor can a thread](lessons/no-print-from-background-thread.md) · [an unexplained hang](lessons/forked-workers-block-cause-unknown.md)
- Worker count is sized from measured memory, and a worker that OOMs is counted, not lost. [sizing + the `tracemalloc` trap + pickling an exception back](lessons/gb-per-pres-sized-from-measured-memory.md)
- Only the parent writes the jsonl. Output on a Drive mount (`_is_remote`) is appended to a local `_stage` copy and mirrored whole-file; `_seed_stage` rebuilds the stage from the mirror on a fresh VM. Everything fsyncs via `_persist`; `_report_lost_rows` is the backstop. [a hole is not a write race](lessons/jsonl-hole-is-not-a-write-race.md)
- A guard trip writes its row at once as `mem_abort_pending` and `_finalize` overwrites it in place after the serial retry; `mem_abort` without the flag is terminal. `out_f` must be closed before either retry loop — `_update_row` does `os.replace`. [a deferred result must reach disk](lessons/mem-abort-pending-row.md)
- `greedy_search` here is a *dispatcher* over `SOLVER` ("compact" | "heavy"), and the single seam every search and every test monkeypatch goes through. `SOLVER` is result-neutral, so it must never enter `_run_prefix`; `_est_gb_per_pres` is solver-aware. [why the solvers agree](lessons/compact-solver-arena-heap.md)
- Heartbeat cadence has two separate phases. [first emission ≠ period](lessons/heartbeat-first-emission-phase-bug.md)

**`wandb_tracking.py`** — run identity, panels, live metrics.
- [group by sweep; the charts that matter](lessons/wandb-group-by-sweep-and-better-charts.md)
- [never pass `step=` on a resumable run](lessons/wandb-step-must-be-monotonic.md)
- [verify the entity exists before pinning](lessons/wandb-entity-must-exist.md)

**`search/greedy_baseline.py`** — the numba solver. Treat `envs/` as a read-only spec.
- [stack-based reduce; guard every `rel[i+1]` peek](lessons/reduce-relator-empty-word-oob.md)
- [paths are Definition 2.1 moves; replay, don't diff](lessons/store-paths-as-definition-2-1-moves.md)
- [never lower `MAX_RELATOR_LENGTH` for speed](lessons/max-relator-length-is-inert.md)
- [hoist k1-independent rotations](lessons/hoist-rotation-out-of-inner-loop.md) · [what to `@njit` and what not to](lessons/numba-jit-split.md)

**`search/greedy_compact.py`** — the same search in numpy. Imports `expand_node_nj` verbatim.
- Keys are unique, so `(total, depth, row)` is a strict total order and the heap implementation
  cannot change the pop sequence. The nibble row must `memcmp`-sort like `pack_key`; a naive
  back-to-back or LSB-first packing does not. Arrays are reserved once and never copied.
  [[WORKS]](lessons/compact-solver-arena-heap.md)
- `_run_chunk` runs ≤ `_HB_CHECK_EVERY` pops then returns, because an `@njit` loop cannot call
  the Python `progress` callback the memory guard rides on.
- numba: cast **both** ternary branches to `int64`; never round-trip a `uint64` through Python.

**`greedy_tests/`** — the pipeline's test suite. **Run it after ANY change to the three files above**
(`pytest experiments/greedy_tests -q`; `--runslow` before a push). See its `README.md`.
- Three layers, so a bug in one can't hide a bug in another: a general-`n` spec, the abelianization
  invariant the solver never computes, and a `SolverAdapter` seam the stable-AC port plugs into.
  [[WORKS]](lessons/greedy-test-suite-three-layers.md)
- Budgets are capped at `MAX_BUDGET = 1_000`; never raise one to reach a deeper search.
  [[WORKS]](lessons/test-budget-ceiling.md)
- `test_crash_resume.py` guards the two `run_baseline.py` resume bugs this suite found (both fixed:
  a torn trailing line is repaired before any append; the pool block is guarded with `jobs`).
  [[TRAP]](lessons/run-baseline-two-known-bugs.md)
- `test_runner_recovery.py` pins the durability of heavy-mode solved rows: the row is written
  before the path is recovered, and a dying recovery is retried on resume without re-searching.
  [[TRAP]](lessons/heavy-mode-defers-solved-rows.md)
- `test_runner_mem_pending.py` does the same for guard-tripped rows. Both fixes are
  mutation-checked; if a suite passes on the first run, mutate the fix and watch it fail.
  [[TRAP]](lessons/mem-abort-pending-row.md)
- `test_solver_compact.py` + the nibble-row half of `test_packed_keys.py` guard the compact
  solver. The sort corpus must be full-width, prefix-heavy and last-symbol-differing — the
  shallow 7225-pair corpus passes for a *wrong* packer. `tools/bytes_per_state.py` derives
  `_BYTES_PER_STATE*` without ever running a search above 1,000 nodes.
  [[WORKS]](lessons/compact-solver-arena-heap.md)
- A green default tier hides whatever it skipped. [[WORKS]](lessons/slow-tier-caught-broken-path-test.md)
  · [a vacuous guard makes a green test meaningless](lessons/cap-monotonicity-vacuous-guard.md)
  · [`-q` twice hides the summary](lessons/pytest-qq-suppresses-summary.md)
  · [rebase before you push](lessons/worktree-branch-drift-rebase.md)

**`stable_ac/solvern.py`** — the general-`n` numba solver. Two symbol orders coexist and must never
be conflated: canonicalisation/relator-sort uses BOOTH order `(-abs(g), g>0)`; the heap tie-break
uses ASCII order `(g>0, abs(g))`. Trace equality with `greedy_tests/spec/` at `n_gen≤3` is what
`test_solvern.py` pins — any change that survives it is safe. Same reduce/Booth lessons as
`search/greedy_baseline.py` apply.

**`stable_ac/nocov/run_nocov.py`** — Branch-A runner. Same laws as `run_baseline.py`: the filename
prefix is the resume key (no dates, no result-neutral knobs); row identity is `(name, z_word)`;
`_repair_jsonl` runs before any append, not gated on `RESUME`; `search_n` is the module-global seam
tests monkeypatch. Budgets > 1000 refuse to run without `ACSOLVERX_ALLOW_BIG=1` (the notebook sets
it — local runs must not). Harness tests are colocated: `pytest experiments/stable_ac -q`.

**`stable_ac/cov/`** — Branch-B one-shot change of variables (`cov.py` transform + `run_cov.py`
runner, which reuses `run_baseline`'s `greedy_search`/`_repair_jsonl`/`_read_done`/`_build_row` by
import). `Z_FAMILY_TAG` is part of the filename identity — bump it whenever `NAIVE_Z_FAMILY`
changes. The length sweep (`experiment_length: true`) brute-forces every subword-derived CoV
(`enumerate_cov`) plus a control row per presentation; sweep rows are keyed `(pres_id, z_word)`
like Branch A's, and the file prefix is `covsweep_..._sub{K}p_` where K = `subword_max_len` (the
family is derived from the presentation, so K is its only identity knob; the `p` suffix is the
family-rule version — pure-power subwords included; suffix-less `sub{K}` files are the old
mixed-only rule and never share a resume file). `z_source: universe` swaps the sweep family for
EVERY reduced word of length 2..`universe_max_len` (`universe_candidates`) with defining-relator
isolation allowed (`iso_index 2` — z solves to an elementary Nielsen automorphism, so it need not
occur in the presentation); prefix `covsweep_..._uni{n}_`. Tests are colocated
(`cov/test_cov.py`), same command as above.

**`stable_ac/verify_results.py`** — the certificate verifier: replays every solved row's path
through `greedy_tests/spec/` ONLY (never a solver — the independence is the point; a solver bug or
a gamed test suite cannot self-certify). Treat any edit here with the same suspicion as an edit to
`spec/`. `test_verify_results.py` tampers with real certificates and requires it to fail. Run it on
any results jsonl before believing the numbers: `-m experiments.stable_ac.verify_results`. Both
runners stamp `git_commit` into every row (provenance only — NEVER part of the resume identity).

**`greedy_baseline.ipynb`** — CONFIG / SETUP / RUN.
- [a push does not reach a running Colab](lessons/notebook-push-does-not-reach-colab.md) · [`git pull` is not a module reload](lessons/git-pull-is-not-a-module-reload.md)
- [`BRANCH` must match git](lessons/notebook-branch-must-match-git.md) · [don't nest the clone](lessons/colab-setup-nested-clone.md) · [Drive mount root isn't writable](lessons/colab-drive-mount-root-not-writable.md)
- [Colab login is flaky](lessons/wandb-colab-login-flaky.md) · [promptless auth needs a Colab Secret](lessons/wandb-auto-auth-colab-secret.md)

## Adding a lesson

**Never paste a full entry into a CLAUDE.md** — both are loaded into context, so an entry
costs its tokens on every session forever, and a bloated CLAUDE.md gets ignored. Three steps:

1. **The entry** → a new `lessons/<slug>.md`, `<slug>` being a short kebab-case name of the rule:

   ```markdown
   # [YYYY-MM-DD] What you learned, stated as a claim [TRAP|WORKS]
   What happened, what the root cause turned out to be, and the evidence (measurements,
   file paths, function names, exact error text). End with **Rule:** what to do next time.
   ```

2. **The hook** → one line in the root [`CLAUDE.md`](../CLAUDE.md) index, under the right heading.
   State the **rule**, not the story, and link the tag to the file:
   `- Never lower the cap to buy speed: it only shrinks the search space. [[WORKS]](experiments/lessons/max-relator-length-is-inert.md)`
   Someone who reads only that line must avoid the trap; the file is for the evidence behind it.

3. **The pointer** → if the lesson is tied to a source file, add it to that file's list above.

Prefer promoting on the **second** occurrence: a one-off bug narrative is noise, a repeated
failure is a rule. Never delete an entry — mark a superseded one `[SUPERSEDED]` in place, and
correct any index line it makes stale.
