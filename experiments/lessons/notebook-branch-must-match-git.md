# [2026-07-08] Notebook BRANCH must match the actual git branch [TRAP]
Set the notebook's `BRANCH` to `"master"` while the real branch was `test/stable-ac-moves-w4` — Colab would clone a branch without `experiments/`. **Rule:** before writing clone config, run `git rev-parse --abbrev-ref HEAD` and use that; confirm `git remote -v` matches `REPO_URL`.
