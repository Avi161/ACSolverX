# CLAUDE.md — `experiments/`

This file loads only when Claude reads something under `experiments/`. It maps each source
file to the lessons that have already bitten someone there. Read the linked file *before*
changing the behaviour it describes — each one is a bug that shipped.

Full one-line index of every lesson: the root [`CLAUDE.md`](../CLAUDE.md).

## Before you edit…

**`run_baseline.py`** — resume identity and the W&B layer both live here.
- `_run_prefix` / `_resolve_paths` are the resume key. [identity](lessons/jsonl-filename-encodes-search-identity.md) · [no dates in the key](lessons/date-in-filename-broke-resume.md)
- The `HIGH_SPEEDUP` pool defers solved rows to a serial recovery re-solve. [why](lessons/high-speedup-boxing-and-memory.md) · [a worker can't print](lessons/heartbeat-worker-cannot-print.md) · [nor can a thread](lessons/no-print-from-background-thread.md) · [an unexplained hang](lessons/forked-workers-block-cause-unknown.md)
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

**`greedy_baseline.ipynb`** — CONFIG / SETUP / RUN.
- [a push does not reach a running Colab](lessons/notebook-push-does-not-reach-colab.md) · [`git pull` is not a module reload](lessons/git-pull-is-not-a-module-reload.md)
- [`BRANCH` must match git](lessons/notebook-branch-must-match-git.md) · [don't nest the clone](lessons/colab-setup-nested-clone.md) · [Drive mount root isn't writable](lessons/colab-drive-mount-root-not-writable.md)
- [Colab login is flaky](lessons/wandb-colab-login-flaky.md) · [promptless auth needs a Colab Secret](lessons/wandb-auto-auth-colab-secret.md)

## Adding a lesson

Write the full entry as `lessons/<slug>.md`, then add **one line** to the index in the root
`CLAUDE.md` and, if it is file-specific, a pointer above. Keep `[WORKS]` / `[TRAP]` tags; be
specific (file paths, function names, exact error text); never delete an entry — mark a
superseded one `[SUPERSEDED]` in place.
