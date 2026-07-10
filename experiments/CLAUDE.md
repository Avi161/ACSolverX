# CLAUDE.md — `experiments/`

This file loads only when Claude reads something under `experiments/`. It maps each source
file to the lessons that have already bitten someone there. Read the linked file *before*
changing the behaviour it describes — each one is a bug that shipped.

Full one-line index of every lesson: the root [`CLAUDE.md`](../CLAUDE.md).

## Before you edit…

**`run_baseline.py`** — resume identity and the W&B layer both live here.
- `_run_prefix` / `_resolve_paths` are the resume key. [identity](lessons/jsonl-filename-encodes-search-identity.md) · [no dates in the key](lessons/date-in-filename-broke-resume.md)
- `_repair_jsonl` runs before anything opens the jsonl for append, and is NOT gated on `RESUME`. Every other reader relies on it. [why a reader-side guard is not enough](lessons/run-baseline-two-known-bugs.md)
- The `HIGH_SPEEDUP` pool defers a solved row's *path* to a serial recovery re-solve, but writes the row itself up-front as `path_pending` and rewrites it in place — never park a result in RAM. [why deferred](lessons/high-speedup-boxing-and-memory.md) · [why persisted first](lessons/heavy-mode-defers-solved-rows.md) · [heavy ≡ normal](lessons/high-speedup-verified-locally.md) · [a worker can't print](lessons/heartbeat-worker-cannot-print.md) · [nor can a thread](lessons/no-print-from-background-thread.md) · [an unexplained hang](lessons/forked-workers-block-cause-unknown.md)
- Worker count is sized from measured memory, and a worker that OOMs is counted, not lost. [sizing + the `tracemalloc` trap + pickling an exception back](lessons/gb-per-pres-sized-from-measured-memory.md)
- Only the parent writes the jsonl, so a missing row is a result the pool never returned. [a hole is not a write race](lessons/jsonl-hole-is-not-a-write-race.md)
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
- A green default tier hides whatever it skipped. [[WORKS]](lessons/slow-tier-caught-broken-path-test.md)
  · [a vacuous guard makes a green test meaningless](lessons/cap-monotonicity-vacuous-guard.md)
  · [`-q` twice hides the summary](lessons/pytest-qq-suppresses-summary.md)
  · [rebase before you push](lessons/worktree-branch-drift-rebase.md)

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
