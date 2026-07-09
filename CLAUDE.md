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

### ⛔ MANDATORY after ANY change to the greedy pipeline

**Any** edit to `experiments/search/greedy_baseline.py`, `experiments/run_baseline.py`, `experiments/greedy_baseline.ipynb`, or anything under `experiments/greedy_tests/` **must** be followed by:

```bash
.venv/bin/python3 -m pytest experiments/greedy_tests -q            # after every change (~1–2 min)
.venv/bin/python3 -m pytest experiments/greedy_tests -q --runslow  # before any push or result claim (~2–3 min)
```

- **Do not report a change as working, and do not commit, until the default tier is green.** A green default tier says nothing about what it *skipped* — `--runslow` carries the multiprocessing path, the golden regressions, and the deep parity matrix. [[WORKS]](experiments/lessons/slow-tier-caught-broken-path-test.md)
- **A golden failure is a RESULT CHANGE, not a stale fixture.** The search is deterministic, so a moved number means something altered it. Diagnose first; only then `python3 -m experiments.greedy_tests.tools.regen_golden`, and say why in the commit message.
- **No test may use a node budget above `MAX_BUDGET = 1_000`** — a search at budget `B` is exactly the first `B` pops of any longer search, so a bigger budget buys slower tests, not different behaviour. [[WORKS]](experiments/lessons/test-budget-ceiling.md)
- **Never assert `min_relator` / `max_relator` strings** — both are tie-broken over a `set`, so they follow `PYTHONHASHSEED`. Their lengths are deterministic.
- `test_known_gaps.py` holds two real `run_baseline.py` bugs as `xfail(strict=True)`. If one XPASSes, someone fixed it — delete the marker, don't mute the test. [[TRAP]](experiments/lessons/run-baseline-two-known-bugs.md)

**Adding the stable-AC solver** (extra generator + relator, change of variables): implement a `SolverAdapter` in `experiments/greedy_tests/adapters.py` and append it to `ALL_ADAPTERS`. The contract, abelianization-invariant and packed-key suites then run against it at `n_gen = 3` **with no test rewriting** — they already run there today against the pure-Python `SpecAdapter`. See `experiments/greedy_tests/README.md`.

### Other suites

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

### Testing
- Test the search against a general-`n` spec **and** against an invariant it never computes (`abs(det)` of the exponent-sum matrix); never build an oracle that must reproduce `nodes_explored` — it becomes a near-copy of the implementation and would reject a correct stable-AC solver. [[WORKS]](experiments/lessons/greedy-test-suite-three-layers.md)
- Node budgets are capped at 1,000: a search at budget `B` is the first `B` pops of any longer search, so a bigger budget buys slower tests, not different behaviour. Want a deeper anchor? Find a presentation that solves in *fewer* nodes. [[WORKS]](experiments/lessons/test-budget-ceiling.md)
- A green default tier proves nothing about what it skipped — check the skip count, never push behind one, and when a new test fails on an already-documented bug the *test* is wrong, not the bug. [[WORKS]](experiments/lessons/slow-tier-caught-broken-path-test.md)
- When the repo forbids touching existing code, park a known defect in `xfail(strict=True)`: it stays green, documents the bug, and fails loudly the moment someone fixes it. [[TRAP]](experiments/lessons/run-baseline-two-known-bugs.md)
- Before building a test on a derived invariant, check its precondition actually fires on the fixtures — a guard that is always false makes a green test meaningless. [[TRAP]](experiments/lessons/cap-monotonicity-vacuous-guard.md)
- Never put `-q`/`-v` in `pytest.ini`'s `addopts` if the documented command also passes one: pytest sums them, and `-qq` silently suppresses the pass/fail summary. [[TRAP]](experiments/lessons/pytest-qq-suppresses-summary.md)
- `EnterWorktree` branches from `origin/main`, not the active branch; re-check `git log` on the target before pushing, and test the *seam* when a neighbouring module already has its own tests. [[TRAP]](experiments/lessons/worktree-branch-drift-rebase.md)

### Colab / notebook
- The Drive mount root `/content/drive/` is not writable — every output path goes under `/content/drive/MyDrive/...`. [[TRAP]](experiments/lessons/colab-drive-mount-root-not-writable.md)
- Anchor to an absolute base before cloning, or each re-run nests the repo one level deeper. [[TRAP]](experiments/lessons/colab-setup-nested-clone.md)
- Pushing notebook changes does NOT update the user's running Colab cells; they must re-open it from GitHub. Put logic in `.py` modules. [[TRAP]](experiments/lessons/notebook-push-does-not-reach-colab.md)
- The notebook's `BRANCH` must match the actual git branch — check `git rev-parse --abbrev-ref HEAD` before writing clone config. [[TRAP]](experiments/lessons/notebook-branch-must-match-git.md)

### Shell
- zsh aborts a `&&` chain when a glob matches nothing — use `find … -delete`, not a bare `rm results/*.jsonl`. [[TRAP]](experiments/lessons/zsh-glob-nomatch-aborts-chain.md)
