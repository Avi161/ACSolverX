# [2026-07-24] `git add -A` swept runtime `.log`/`.pid` files into a reorg commit [TRAP]

Second occurrence of the `git add -A` failure mode, in a different disguise from the first.

## What happened

During a directory reorganisation I staged with `git add -A` and committed as "reorg: 81 result files were living inside tests/ — move them to results/". The commit's own `--stat` says **101 files changed**. The extra twenty were whatever else happened to be dirty, and six of them were runtime artifacts sitting untracked in `results/`:

```
results/comparison/three_way_b10k.{log,pid}
results/stable_ac/cov/allcov_escape/run_b20000.{log,pid}
results/stable_ac/cov/allcov_escape/run_b100000.{log,pid}
```

A `.pid` file containing the pid of a process that exited days ago is now repo history. The commit message describes a move of results files and says nothing about any of this, so nobody reading the log would know to look.

It was caught only because a subagent was later briefed that those six files were *untracked* and, on `git status`, found them reported as `D` (deleted-from-tracked) rather than simply absent. The brief was wrong because I had made it wrong two commits earlier.

## Why the obvious fix does not work on its own

The instinct is to add the paths to `.gitignore`. **`.gitignore` has no effect on a path git already tracks.** Ignoring them changes nothing until the tracked copies are deleted in a commit; until then every future `git add -A` keeps updating them. The fix is two steps, in order: delete the tracked files, *then* the ignore rule keeps them out.

## The related trap in the ignore rule itself

The reflex rule is `results/**/*.log`. That would have been wrong here: `results/equivalence_classes/logs/` and `results/equivalence_classes/probe/overnight_logs/` track real `.log` files **as evidence**, not as process scratch. A blanket pattern would have silently shadowed them the next time one changed. Checking `git ls-files` first showed `.pid` is safe repo-wide (nothing tracked anywhere matches) while `.log` had to be scoped to the two directories that actually produce scratch.

## Rule

**Stage named paths. Never `git add -A`, and never `git add .`** — this is already the rule for worktrees ([the first occurrence](never-git-add-all-from-a-worktree.md), where it committed a `.venv` symlink that destroyed the real virtualenv on merge); it is the rule everywhere. A reorganisation is exactly when the working tree is fullest of unrelated debris, so it is the worst moment to sweep.

Two checks that cost nothing:

- Before committing, `git diff --cached --stat | tail -1` and compare the file count against what the commit message claims. A message about 81 files and a stat reading 101 is the whole bug, visible in one line.
- Before writing an ignore rule, `git ls-files` against the pattern. If it matches something already tracked, the rule is either ineffective or actively harmful — narrow it.

And when a brief hands you a fact about repo state ("these files are untracked"), verify it rather than assume it. That is what surfaced this.
