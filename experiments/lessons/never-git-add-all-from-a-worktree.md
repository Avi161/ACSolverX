# [2026-07-24] `git add -A` from a worktree committed a `.venv` symlink and destroyed the real venv on merge [TRAP]

An early commit in the heuristic-search push (`8603a23`) was staged with `git add -A`. That swept in `.venv`, which in a git worktree is not a directory but a **symlink to the main checkout's** `.venv`:

```
.venv -> /Users/.../surf/ACSolverX/.venv        (mode 120000)
```

Committing it was silent and harmless *in the worktree* — the link resolved to a real virtualenv one level up, and `.venv/bin/python3` kept working for the whole session, through 27 experiments and 115,000 searches.

The damage landed on **merge**. When the branch was merged into `research/w5/stable-ac-escape` inside the main checkout, git checked the tracked symlink out at `ACSolverX/.venv` — where its target is *itself*. The real virtualenv directory at that path was replaced by a self-referential link:

```
$ ./.venv/bin/python3 -c "import numba"
zsh: too many levels of symbolic links: ./.venv/bin/python3
```

No `pyvenv.cfg` survived anywhere under `surf/`, so the environment had to be rebuilt from scratch (`python3 -m venv .venv && pip install numba numpy wandb` — the repo's `requirements.txt` is an unrelated JAX/PPO stack). Nothing else was lost: all results were committed data, and the Colab path never touches `.venv`.

Two aggravating details worth remembering:

- **`git rm --cached .venv` does not fix it.** That only untracks; the broken symlink stays in the working tree, and the real directory is already gone.
- **Removing it from the merge target is not enough.** The symlink stayed tracked on the source branch, so a second merge of that branch would recreate the breakage. It has to be untracked *at the source* and gitignored.

## Rule

**Never `git add -A` (or `git add .`) from inside a git worktree — stage named paths.** A worktree's tree contains links pointing outside it, and `.venv` is the common one; committing such a link is invisible locally and destructive to whoever merges. This repo already required "new files only"; the concrete operational form of that is *name the files*.

More generally: before committing, check for symlinks in what you staged —

```bash
git diff --cached --raw | awk '$1 ~ /120000/ {print $NF}'
```

Any mode `120000` entry pointing outside the repo is a landmine for the next person to check it out. Related: [literature/ is gitignored so a proof .tex was silently skipped](literature-dir-is-gitignored.md) — the mirror image, where `git add` silently *omitted* something instead of silently including it. Both say the same thing: verify what was actually staged, never trust the shorthand.
