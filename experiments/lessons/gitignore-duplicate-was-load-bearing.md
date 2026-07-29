# [2026-07-29] A repeated `.gitignore` line after a negation is not a duplicate — it is the rule doing the work [TRAP]

A repo-organization audit flagged `.DS_Store` as appearing twice in `.gitignore` (lines 3 and 19) and called the second one "a harmless but redundant duplicate". It was removed. The merge then immediately surfaced a new untracked file:

```
?? ppo_checkpoints/610model/.DS_Store
```

`.gitignore` is **order-sensitive, last-match-wins**. The file contains a negation that re-includes an entire directory:

```
ppo_checkpoints/*
!ppo_checkpoints/610model/
!ppo_checkpoints/610model/**      <- re-includes EVERYTHING under 610model, .DS_Store included
...
.DS_Store                          <- line 19: the only rule that re-ignored it
```

Line 3's `.DS_Store` is overridden for that path by the line-8 negation. Line 19 came *after* the negation, so it was the rule that actually ignored `ppo_checkpoints/610model/.DS_Store`. The two lines are textually identical and semantically different.

`git check-ignore -v` says exactly which rule decides a path, and it distinguishes the two cases in one command:

```
# with the old file:  .gitignore:19:.DS_Store    ppo_checkpoints/610model/.DS_Store   (ignored)
# after the delete:   .gitignore:8:!ppo_checkpoints/610model/**  ...                  (NOT ignored)
```

The generalisation: in any last-match-wins config (`.gitignore`, `.dockerignore`, `.npmignore`, ESLint overrides, nginx `location` blocks), **a repeated entry is only redundant if no rule between the two occurrences can flip the outcome for some path.** A negation in between makes the later copy load-bearing. Textual de-duplication is not a safe refactor there.

The line is now restored with a comment saying it is not a duplicate, because the next audit would otherwise flag it again.

**Rule:** never delete a repeated `.gitignore` entry on the strength of it looking identical. Run `git check-ignore -v <a path the rule targets>` before and after, and confirm the deciding rule did not change. If a negation sits between the two occurrences, keep the later one and comment why.
