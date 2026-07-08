# CLAUDE.md — ACSolverX (repo-scoped)

Guidance and lessons specific to this repository. Global rules still apply; this file holds repo-local context and the traps hit while building the greedy baseline.

## Repo context

- AC-SolverX: JAX/flax RL solver for the Andrews–Curtis conjecture (Two-Hump paper). `envs/` (`ac_s.py`, `ac_moves.py`), `network.py`, `ppo_ac_s.py` are the JAX/GPU training stack.
- **This branch's experiment work is CPU + numba only** — no JAX, GPU, or PPO. The JAX code is a *spec to port from, never import*.
- Experiment code lives under `experiments/` (search core in `experiments/search/`); run outputs go to `results/` (repo root). Baseline greedy pipeline: `experiments/search/greedy_baseline.py` (solver, adapted from `greedy_search.ipynb`), `experiments/run_baseline.py` (jsonl + resume + W&B), `experiments/greedy_baseline.ipynb` (CONFIG/SETUP/RUN).
- **Do not modify existing code.** New files only; the notebook `greedy_search.ipynb` and `envs/` are read-only references.
- Active branch: `test/stable-ac-moves-w4`. Remote: `github.com/Avi161/ACSolverX.git`.

## Environment

- No `python` on the local machine — use `.venv/bin/python3` (numba 0.66, numpy 2.4 installed; **wandb is NOT in the venv by default** — `pip install wandb` to test W&B locally).
- W&B: project `acsolver`, **entity `avigyapaudel045-aisc`** (the account is org-managed under Caltech/AISC, so runs go to a *team* entity — the bare username `avigyapaudel045` is NOT a writable run namespace). Default team = `avigyapaudel045-aisc`; other team = `justinshenk-time`. Personal user API key is fine (from User settings → API keys, e.g. `model_analysis`), not a team service-account key.

## Lessons learned

### [2026-07-08] Colab Drive path — mount root is not writable [TRAP]
`os.makedirs("/content/drive/acsolverx_results")` → `OSError [Errno 95] Operation not supported`. The Drive FUSE mount root `/content/drive/` rejects directory creation. **Rule:** all Drive output paths must be under `/content/drive/MyDrive/...` (or a Shared drive), never `/content/drive/` directly.

### [2026-07-08] Colab SETUP cloned the repo nested (ACSolverX/ACSolverX/…) [TRAP]
Cause: SETUP did `os.chdir(REPO_ROOT)` into the repo, then a *re-run* checked `os.path.isdir(REPO_DIR)` with a **relative** `REPO_DIR` from inside the repo → clones again one level deeper each run. **Rule:** anchor to an absolute base first (`os.chdir("/content")`) and derive `REPO_ROOT = os.path.join("/content", REPO_DIR)`; make clone/pull idempotent. For local, walk *up* to the repo root (dir holding `experiments/` + `data/`), don't assume cwd.

### [2026-07-08] Pushing notebook changes does NOT update the user's running Colab cells [TRAP]
The notebook cells executing in Colab are the user's editor buffer, independent of the repo copy. Only `.py` files re-pulled by SETUP's `git reset --hard` auto-update; `cfg` comes from the user's CONFIG cell. **Rule:** when a fix touches a notebook cell, tell the user to re-open the notebook from GitHub (or hand-edit the cell) — a push alone won't reach them. Prefer putting logic in importable `.py` modules so fixes propagate via git.

### [2026-07-08] Notebook BRANCH must match the actual git branch [TRAP]
Set the notebook's `BRANCH` to `"master"` while the real branch was `test/stable-ac-moves-w4` — Colab would clone a branch without `experiments/`. **Rule:** before writing clone config, run `git rev-parse --abbrev-ref HEAD` and use that; confirm `git remote -v` matches `REPO_URL`.

### [2026-07-08] W&B auth in Colab — interactive login is flaky; default entity misleads [TRAP]
`wandb.login()` shows a 1/2/3 menu that Colab's stdin mangles ("Invalid choice"). **Rule:** source the key from a Colab Secret (`google.colab.userdata.get("WANDB_API_KEY")`) or a single `getpass` that sets `os.environ["WANDB_API_KEY"]`; then `wandb.login(key=..., verify=True)` for a real server check. Print the **pinned** target (`cfg entity/project`), not `Api().default_entity` — the default (`aisc`) is not where runs land and reads as if it were.

### [2026-07-08] W&B entity must be verified to exist before pinning [TRAP]
`wandb.init(entity="avigyapaudel045")` → `CommError: entity avigyapaudel045 not found during upsertBucket`. Root cause: the account is **org-managed** (Caltech/AISC), so the bare username is NOT a writable run entity — runs must target a **team** (`avigyapaudel045-aisc`). **Rule:** for org-managed W&B accounts, use the team entity (User settings → Default team), or `WANDB_ENTITY=None` to fall back to `api.default_entity`. A wrong entity only fails at `wandb.init`, not at `login(verify=True)` — verify the entity separately (`wandb.Api().default_entity`). Also: the API key must be a personal user key (User settings → API keys), not a team service-account key, or it can't write to your entities.

### [2026-07-08] numba split that works [WORKS]
`@njit` on the per-move math (neighbours, reduction, Booth canonicalisation, primitives); plain Python for the `heapq`/`dict` search orchestration (numba can't JIT those). Verified real: functions are `numba.core.registry.CPUDispatcher`, first call ~3s JIT then ~1e-4s (≈30000×). First ~10 presentations look slow purely from one-time JIT compile.

### [2026-07-08] zsh glob nomatch aborts a command chain [TRAP]
`rm -f results/*.jsonl && python …` — when the glob matches nothing, zsh errors on the glob and `&&` short-circuits, so the Python step silently never ran. **Rule:** use `find results -type f -delete` (or guard with `setopt null_glob`) instead of bare globs in `rm`.
