# CLAUDE.md — ACSolverX (repo-scoped)

Repo-local context and hard rules. Global rules still apply.

Each lesson below is one sentence carrying the operative rule, linked to its own file with the
full evidence. Read a linked file only when you need the detail behind that specific rule.
**Adding a lesson: write the full entry as a new `experiments/lessons/<slug>.md`, and add one
line here.** Never paste a full entry into this file — it is loaded in full on every session,
and a bloated CLAUDE.md gets ignored.

## Repo context

- AC-SolverX: JAX/flax RL solver for the Andrews–Curtis conjecture (Two-Hump paper). `envs/` (`ac_s.py`, `ac_moves.py`), `network.py`, `ppo_ac_s.py` are the JAX/GPU training stack.
- **This branch's experiment work is CPU + numba only** — no JAX, GPU, or PPO. The JAX code is a *spec to port from, never import*.
- Experiment code lives under `experiments/` (search core in `experiments/search/`); run outputs go to `results/` (repo root). Baseline greedy pipeline: `experiments/search/greedy_baseline.py` (solver, adapted from `greedy_search.ipynb`), `experiments/run_baseline.py` (jsonl + resume + W&B), `experiments/wandb_tracking.py` (W&B identity + charts), `experiments/greedy_baseline.ipynb` (CONFIG/SETUP/RUN).
- **Do not modify existing code.** New files only; the notebook `greedy_search.ipynb` and `envs/` are read-only references.
- Active branch: `test/stable-ac-moves-w4`. Remote: `github.com/Avi161/ACSolverX.git`.

## Environment

- No `python` on the local machine — use `.venv/bin/python3` (numba 0.66, numpy 2.4, wandb 0.28 installed).
- W&B: project `acsolver`, **entity `avigyapaudel045-aisc`** (the account is org-managed under Caltech/AISC, so runs go to a *team* entity — the bare username `avigyapaudel045` is NOT a writable run namespace). Default team = `avigyapaudel045-aisc`; other team = `justinshenk-time`. Personal user API key is fine (from User settings → API keys), not a team service-account key.

## Tests

- `.venv/bin/python3 tests/wandb_tracking_test.py` — pure, offline, no wandb server needed.
- `.venv/bin/python3 tests/wandb_offline_integration.py <phase>` — phases: `cum_nodes identity fresh panels resume_full resume_partial heavy`.

## Lessons index

### Search correctness (numba)
- Stack-based free reduction is the safe form; any `rel[i+1]` peek in numba needs a bounds guard, and `str_to_arr('')` must return a 2-D `(0,2)`. [[TRAP]](experiments/lessons/reduce-relator-empty-word-oob.md)
- Store solved paths as Definition 2.1 moves `(i,j,k1,k2)`, not string pairs — the move inverts the **other** relator, so decode by replay, never by diffing states. [[WORKS]](experiments/lessons/store-paths-as-definition-2-1-moves.md)
- Never lower `MAX_RELATOR_LENGTH` to buy speed: it strictly shrinks the search space and can only reduce the solve rate. Cut `SUBSET` or `BUDGET` instead. [[WORKS]](experiments/lessons/max-relator-length-is-inert.md)
- Hoist any roll/transform that doesn't depend on the outer index out of nested rotation loops: O(L³) → O(L²). [[WORKS]](experiments/lessons/hoist-rotation-out-of-inner-loop.md)
- `@njit` the per-move math; leave the `heapq`/`dict` search orchestration in plain Python. [[WORKS]](experiments/lessons/numba-jit-split.md)

### HIGH_SPEEDUP / multiprocessing
- Boxing was the cost and memory was the cap; a packed `bytes` key must sort identically to `(str, str)` or the heap tie-break shifts. Memory reduction is what unlocks parallelism. [[WORKS]](experiments/lessons/high-speedup-boxing-and-memory.md)
- Heavy ≡ normal on `solved`/`nodes_explored`, ~2.8× faster; ms640 legitimately leaves several idx unsolved, so an unsolved row there is not a bug. [[WORKS]](experiments/lessons/high-speedup-verified-locally.md)
- Size a search's RAM from the node budget (`discovered ≈ 82.9·b^0.981` states × 214 B, both measured), never one constant: 9.0 was too high at 50k *and* too low at 1M (~14 GB). [[WORKS]](experiments/lessons/gb-per-pres-sized-from-measured-memory.md)
- A memory guard must trip on real system pressure (`MemAvailable`), never on a worker exceeding its `1/n` share — at 1M a search legitimately exceeds it, and a share-based guard would abort every presentation. [[TRAP]](experiments/lessons/gb-per-pres-sized-from-measured-memory.md)
- Never calibrate memory on macOS `ru_maxrss` — the compressor makes bytes/state *fall* as states grow, and a forked child's resets. Measure the real data structures instead. [[TRAP]](experiments/lessons/gb-per-pres-sized-from-measured-memory.md)
- An exception pickled back from a pool worker must have `args` equal to its ctor args, or unpickling raises `TypeError` inside `_handle_results`. [[TRAP]](experiments/lessons/gb-per-pres-sized-from-measured-memory.md)
- Forked workers once blocked inside `greedy_search` and the cause was **never established** — the numba-deadlock hypothesis is unproven. Get a stack from the failing environment; don't re-test a clean local one. [[TRAP]](experiments/lessons/forked-workers-block-cause-unknown.md)
- A pool worker's `print()` is silently dropped in Jupyter/Colab — route samples through an `mp.Queue` and drain them in the parent. [[TRAP]](experiments/lessons/heartbeat-worker-cannot-print.md)
- Never rely on a background thread for user-visible output in a notebook; poll with a timeout from the main thread. [[WORKS]](experiments/lessons/no-print-from-background-thread.md)
- A rate-limiter's *first* emission is a separate design decision from its steady-state period, and never advance a "last fired" timestamp on a tick that printed nothing. Test periodic code at the production interval. [[TRAP]](experiments/lessons/heartbeat-first-emission-phase-bug.md)

### Run identity & resume
- The jsonl filename / `run_id` stem must encode every knob that changes the result — and no knob that doesn't (`use_*`, `HIGH_SPEEDUP`, `HEARTBEAT_*`, `WANDB_*` stay out of `_run_prefix`). [[TRAP]](experiments/lessons/jsonl-filename-encodes-search-identity.md)
- Never put a wall-clock date in a filename that also serves as a resume key. [[TRAP]](experiments/lessons/date-in-filename-broke-resume.md)
- `git pull` is NOT a module reload — a pulled `.py` stays stale in `sys.modules`. Prove *which* code is loaded before diagnosing "my fix didn't take". [[TRAP]](experiments/lessons/git-pull-is-not-a-module-reload.md)

### W&B
- Group by **sweep**, not by date. `pres_id` is just a line number and was never a useful x-axis; chart the anytime solve-rate profile and the two-hump path curve instead. [[WORKS]](experiments/lessons/wandb-group-by-sweep-and-better-charts.md)
- Never pass a domain index (`pres_id`) as `step=` on a resumable run — declare a `define_metric(step_metric=...)` instead. [[TRAP]](experiments/lessons/wandb-step-must-be-monotonic.md)
- Verify the entity exists before pinning it: a wrong entity fails only at `wandb.init`, not at `login(verify=True)`. [[TRAP]](experiments/lessons/wandb-entity-must-exist.md)
- Colab's interactive `wandb.login()` menu is mangled by stdin; source the key from a Colab Secret or a single `getpass`, and always pass `relogin=True`. [[TRAP]](experiments/lessons/wandb-colab-login-flaky.md)
- Promptless auth *requires* a Colab Secret; sanitize and format-validate a pasted key before hitting the server. [[TRAP]](experiments/lessons/wandb-auto-auth-colab-secret.md)

### Colab / notebook
- The Drive mount root `/content/drive/` is not writable — every output path goes under `/content/drive/MyDrive/...`. [[TRAP]](experiments/lessons/colab-drive-mount-root-not-writable.md)
- Anchor to an absolute base before cloning, or each re-run nests the repo one level deeper. [[TRAP]](experiments/lessons/colab-setup-nested-clone.md)
- Pushing notebook changes does NOT update the user's running Colab cells; they must re-open it from GitHub. Put logic in `.py` modules. [[TRAP]](experiments/lessons/notebook-push-does-not-reach-colab.md)
- The notebook's `BRANCH` must match the actual git branch — check `git rev-parse --abbrev-ref HEAD` before writing clone config. [[TRAP]](experiments/lessons/notebook-branch-must-match-git.md)

### Shell
- zsh aborts a `&&` chain when a glob matches nothing — use `find … -delete`, not a bare `rm results/*.jsonl`. [[TRAP]](experiments/lessons/zsh-glob-nomatch-aborts-chain.md)
