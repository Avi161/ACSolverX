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
| `stable_ac/` | shared core (`solvern.py`, `word_families.py`) + one folder per pipeline: `nocov/` (Branch A) and `cov/` (Branch B), each with runner + yaml + notebook (tests in `tests/stable_ac/`) | [→](stable_ac/README.md) |
| `analysis/` | the stable-AC benchmark (difficulty ladder + reach tier + combined) | [→](analysis/README.md) |
| `equivalence_classes/` | `lib/` `search/` `pipeline/` `verify/` `phases/` (tests in `tests/equivalence_classes/`) | [→](equivalence_classes/README.md) |
| `greedy_tests/` | the greedy test SUPPORT code — `spec/` `fixtures/` `adapters.py` `tools/` `golden/` (imported by production too); the tests live in `tests/greedy/` | [→](greedy_tests/README.md) |
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
- `expand_node_topk_nj` screens each child's reduced length from the seam alone and materialises only the kept `topk` — bit-identical to `expand_node_nj` + a stable top-k, which is what keeps written rows resumable. [why, and the 21.5× measurement](lessons/screen-child-length-before-materialising.md)

**`search/greedy_compact.py`** — the same search in numpy. Imports `expand_node_nj` verbatim.
- Keys are unique, so `(total, depth, row)` is a strict total order and the heap implementation
  cannot change the pop sequence. The nibble row must `memcmp`-sort like `pack_key`; a naive
  back-to-back or LSB-first packing does not. Arrays are reserved once and never copied.
  [[WORKS]](lessons/compact-solver-arena-heap.md)
- `_run_chunk` runs ≤ `_HB_CHECK_EVERY` pops then returns, because an `@njit` loop cannot call
  the Python `progress` callback the memory guard rides on.
- numba: cast **both** ternary branches to `int64`; never round-trip a `uint64` through Python.

**`greedy_tests/`** — the greedy test SUPPORT code (`spec/`, `fixtures/`, `adapters.py`, `tools/`, `golden/`);
the tests themselves are in `tests/greedy/`. **Run them after ANY change to the three files above or to this
support code** (`pytest tests/greedy -q`; `--runslow` before a push). See its `README.md`.
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

**`stable_ac/solvern_fast.py`** — `search_n_fast`, the HIGH_SPEEDUP twin: fused kernel + packed
bytes as heap-tiebreak-AND-state, parent/move pointers kept, so it owes `search_n` **whole-dict
equality, paths included** (`test_solvern_fast.py`). Two traps its docstring names: the child
relator sort is length-first (booth-lex alone misorders `x` vs `ZZ`), and unpacking must cast
uint8→signed before negating. HIGH_SPEEDUP is result-neutral — never in a filename identity.

**`stable_ac/nocov/run_nocov.py`** — Branch-A runner. Same laws as `run_baseline.py`: the filename
prefix is the resume key (no dates, no result-neutral knobs); row identity is `(name, z_word)`;
`_repair_jsonl` runs before any append, not gated on `RESUME`; `search_n` is the module-global seam
tests monkeypatch. Budgets > 1000 refuse to run without `ACSOLVERX_ALLOW_BIG=1` (the notebook sets
it — local runs must not). Harness tests: `pytest tests/stable_ac -q`.

**`stable_ac/cov/`** — Branch-B one-shot change of variables (`cov.py` transform + `run_cov.py`
runner, which reuses `run_baseline`'s `greedy_search`/`_repair_jsonl`/`_read_done`/`_build_row` by
import). Full method walkthrough with worked examples: [`cov/PIPELINE.md`](stable_ac/cov/PIPELINE.md). `Z_FAMILY_TAG` is part of the filename identity — bump it whenever `NAIVE_Z_FAMILY`
*or* substitution semantics change (zf3 = zf2 word list + cyclic-seam matches in
`substitute_word`; zf2 = every canonical freely+cyclically reduced word of length 2..4;
zf1 was 17 hand-picked mixed words). Destabilization may eliminate **x or y** (`iso_gen`, part of
the sweep row key) — the two are tied by an exact x↔y swap symmetry that `test_xy_symmetry_oracle`
pins. The length sweep (`experiment_length: true`) brute-forces every valid CoV per z under BOTH
targets (`enumerate_cov`) plus a control row per presentation; sweep rows are keyed
`(pres_id, z_word, iso_gen, iso_index)` and the file prefix is
`covsweep_..._subnc2pxysb_` (`cov.SUBWORD_FAMILY_TAG`, a constant — never rebuilt from config).
**`iso_index` is KEY, not a passenger**: both r1' and r2' can isolate one (z, iso_gen) into two
different pairs, so `enumerate_cov` walks `cov_branches` (not `apply_cov_once`, whose first-wins
default exists only for single-transform callers) and the resume key carries all four fields — a
3-field key collides the branches and loses one silently. Enumerating branches is +104 rows and
+75 Aut-orbits on the 66-row benchmark, so first-wins was not a rounding error. **The subword family has NO
`|w|` knob**: every length is enumerated and the only length rule is the no-collapse gate — drop a
z that substitutes SOME relator below `cov.MIN_TRANSFORMED_LEN`, judged by effect on *both*
relators, not by which one w was read from (a w interior to r1 can still collapse r2; see
`test_subword_no_collapse_gate_is_cross_relator`). A relator collapsed to length 2 is the
two-letter isolator the factorization theorem proves is ordinary AC + a rename, so it is not a new
coordinate system. `subword_max_len` is GONE, not renamed — a yaml resurrecting it would silently
read as a bound (`test_subword_family_has_no_length_knob`). Suffix = family-rule version: `nc2`
no-collapse, `p` pure powers in, `xy` both isolation targets, `s` cyclic-seam substitution;
`sub{K}*` files bounded `|w|` by a fixed global K and never share a resume file. `reject_len` is a
structural
ceiling only (239 = fast-solver relator cap 255 − headroom 16), never a length prior — long
starts are admitted because sweep evidence says some presentations solve only from them.
`z_source: universe` swaps the sweep family for EVERY reduced word of length
2..`universe_max_len` (`universe_candidates`) with defining-relator isolation allowed
(`iso_index 2` — z solves to an elementary Nielsen automorphism of either generator, so it need
not occur in the presentation); prefix `covsweep_..._uni{n}xys_`. `high_speedup` (production
yaml true) routes searches through `run_baseline.greedy_search(high_speedup=True)` and
re-solves solved rows with the normal solver for their path — result-neutral (rows identical,
~2.9× measured), so it stays OUT of `_run_prefix` and files resume across modes. Both runners
`flock`-claim their jsonl before appending (a live holder is an orphaned worker from a superseded
run — it gets killed), and the chunk heartbeat counts unique row keys, never lines.
[[TRAP]](lessons/orphaned-workers-double-compute.md) Tests:
`tests/stable_ac/test_cov.py`, same command as above.

**`stable_ac/verify_results.py`** — the certificate verifier: replays every solved row's path
through `greedy_tests/spec/` ONLY (never a solver — the independence is the point; a solver bug or
a gamed test suite cannot self-certify). Treat any edit here with the same suspicion as an edit to
`spec/`. `test_verify_results.py` tampers with real certificates and requires it to fail. Run it on
any results jsonl before believing the numbers: `-m experiments.stable_ac.verify_results`. Both
runners stamp `git_commit` into every row (provenance only — NEVER part of the resume identity).

**`greedy_baseline.ipynb`** — CONFIG / SETUP / RUN. This 3-cell shape is THE pattern for every
Colab notebook in the repo (cov_baseline.ipynb follows it; extra cells only with a structural
reason; results always jsonl). [[WORKS]](lessons/colab-notebook-pattern.md)
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
