# `experiments/lessons/`

38 write-ups. **Each one is a bug that already shipped, or an approach that was measured and worked.**

You are not meant to browse this folder. The operative rules — one sentence each, which is all you
need to avoid the trap — are indexed in the two `CLAUDE.md` files, and those are loaded automatically:

- [`../../CLAUDE.md`](../../CLAUDE.md) — every lesson, grouped by subsystem
- [`../CLAUDE.md`](../CLAUDE.md) — mapped onto the **source file** each one bites

Open a file here only when you need the evidence behind a rule you have already read.

`[TRAP]` = a bug that shipped. `[WORKS]` = an approach that was measured and held.

## Search correctness (numba)

| | lesson |
|---|---|
| `WORKS` | [Unique keys make the heap implementation free to change](compact-solver-arena-heap.md) |
| `WORKS` | [MAX_RELATOR_LENGTH is nearly INERT under best-first search](max-relator-length-is-inert.md) |
| `WORKS` | [Store solved paths as Definition 2.1 moves, not string pairs](store-paths-as-definition-2-1-moves.md) |
| `WORKS` | [Hoist k1-independent rotation out of the inner loop](hoist-rotation-out-of-inner-loop.md) |
| `WORKS` | [The numba split that works](numba-jit-split.md) |
| `TRAP` | [`reduce_relator_nj` empty-word OOB; `str_to_arr('')` malformed](reduce-relator-empty-word-oob.md) |

## Equivalence classes (the 261 unsolved reps)

| | lesson |
|---|---|
| `WORKS` | [To find AC merges, search modulo Aut(F₂) — raw length is the wrong ruler](search-the-aut-quotient-not-raw-length.md) |

## HIGH_SPEEDUP / multiprocessing

| | lesson |
|---|---|
| `WORKS` | [Boxing was the cost, memory was the cap](high-speedup-boxing-and-memory.md) |
| `WORKS` | [GB_PER_PRES was wrong in BOTH directions; size it from measured memory](gb-per-pres-sized-from-measured-memory.md) |
| `WORKS` | [HIGH_SPEEDUP re-verified locally; measured nodes/s](high-speedup-verified-locally.md) |
| `WORKS` | [Don't print from a background thread in Colab](no-print-from-background-thread.md) |
| `TRAP` | [A deferred result must reach disk before it is deferred](mem-abort-pending-row.md) |
| `TRAP` | [HIGH_SPEEDUP held every SOLVED row in RAM until the run ended](heavy-mode-defers-solved-rows.md) |
| `TRAP` | [A hole in the jsonl is never a write race](jsonl-hole-is-not-a-write-race.md) |
| `TRAP` | [Forked workers block inside `greedy_search` — cause NOT established](forked-workers-block-cause-unknown.md) |
| `TRAP` | [A pool worker cannot print into a notebook](heartbeat-worker-cannot-print.md) |
| `TRAP` | [Heartbeat silent for 2× the interval — tested at 2s, shipped at 90s](heartbeat-first-emission-phase-bug.md) |

## Run identity & resume

| | lesson |
|---|---|
| `TRAP` | [The jsonl filename must encode the full search identity](jsonl-filename-encodes-search-identity.md) |
| `TRAP` | [A date in the filename broke cross-day resume](date-in-filename-broke-resume.md) |
| `TRAP` | [`git pull` is NOT a module reload](git-pull-is-not-a-module-reload.md) |

## Testing

| | lesson |
|---|---|
| `WORKS` | [Three layers, so one bug can't hide another](greedy-test-suite-three-layers.md) |
| `WORKS` | [Test budgets are capped at 1,000 nodes — and that costs nothing](test-budget-ceiling.md) |
| `WORKS` | [The slow tier caught a test that asserted a known-broken path](slow-tier-caught-broken-path-test.md) |
| `TRAP` | [Never run a search above budget 1,000 yourself](local-run-budget-cap.md) |
| `TRAP` | [Two real bugs in `run_baseline.py`: pinned as xfail, then fixed](run-baseline-two-known-bugs.md) |
| `TRAP` | [Cap-monotonicity: the tempting theorem has a vacuous guard](cap-monotonicity-vacuous-guard.md) |
| `TRAP` | [`-q` twice is `-qq` and hides the summary](pytest-qq-suppresses-summary.md) |
| `TRAP` | [The branch moved under a long-running worktree — rebase before you push](worktree-branch-drift-rebase.md) |

## W&B

| | lesson |
|---|---|
| `WORKS` | [Group by SWEEP, not by date; `pres_id` was never a useful x-axis](wandb-group-by-sweep-and-better-charts.md) |
| `TRAP` | [Never pass a domain index as `step=` on a resumable run](wandb-step-must-be-monotonic.md) |
| `TRAP` | [Verify the entity exists before pinning it](wandb-entity-must-exist.md) |
| `TRAP` | [Colab login is flaky; the default entity misleads](wandb-colab-login-flaky.md) |
| `TRAP` | [Promptless auth needs a Colab Secret](wandb-auto-auth-colab-secret.md) |

## Colab / notebook / shell

| | lesson |
|---|---|
| `TRAP` | [The Drive mount root is not writable](colab-drive-mount-root-not-writable.md) |
| `TRAP` | [SETUP cloned the repo nested (`ACSolverX/ACSolverX/…`)](colab-setup-nested-clone.md) |
| `TRAP` | [A push does not reach a running Colab](notebook-push-does-not-reach-colab.md) |
| `TRAP` | [The notebook's `BRANCH` must match the actual git branch](notebook-branch-must-match-git.md) |
| `TRAP` | [zsh aborts a `&&` chain when a glob matches nothing](zsh-glob-nomatch-aborts-chain.md) |

---

## Adding one

**Never paste a full entry into a `CLAUDE.md`** — it is loaded in full every session, so the entry
costs its tokens forever and a bloated `CLAUDE.md` gets ignored.

1. **The entry** → a new `<slug>.md` here. H1: `# [YYYY-MM-DD] The claim [TRAP|WORKS]`, then what
   happened, the root cause, the evidence (paths, function names, exact error text), and **Rule:**.
2. **The hook** → one line in [`../../CLAUDE.md`](../../CLAUDE.md), stating the **rule**, not the story.
3. **The pointer** → if it's tied to a source file, add it to that file's list in [`../CLAUDE.md`](../CLAUDE.md).
4. Add a row above.

Promote on the **second** occurrence: a one-off bug narrative is noise, a repeated failure is a rule.
Never delete an entry — mark a superseded one `[SUPERSEDED]` in place.
