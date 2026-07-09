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
- Heavy ≡ normal on `solved`/`nodes_explored`, ~2.8× faster. `GB_PER_PRES` calibrated at 1M/mrl48 silently under-provisions workers at small budgets. [[WORKS]](experiments/lessons/high-speedup-verified-locally.md)
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

### [2026-07-09] GB_PER_PRES was wrong in BOTH directions; size it from measured memory [WORKS]
`GB_PER_PRES = 9.0` was a single constant calibrated at 1M/mrl=48 and applied at **every** budget. Two independent errors: at 50k a search needs **<1 GB** (so auto gave 4 workers where 8 fit), and at 1M it needs **~15 GB, not 9** (so 4 workers on a 51 GB Colab high-RAM runtime is **over-subscribed** — 4x15 = 60 GB). The under-provisioning was the harmless one; the over-provisioning is an OOM.
**Measured, not assumed.** (a) *bytes/state*: `tracemalloc` on the heavy solver gives **185 B/state live AND 185 B/state marginal** (`0.368 GB @ 1,994,777` states → `0.756 GB @ 4,093,805`), i.e. the packed key + `visited` set entry + `(total, depth, key)` heap tuple + list slot. Ship **220 B** = +19% for allocator fragmentation and the set-resize transient (CPython allocates the new table before freeing the old); it matches the 213 B/state seen from real RSS on Colab. (b) *discovered/node*: fit `discovered = A·budget^p`. **mrl=48 → p=0.997 (LINEAR, A=69.3)** across 25k…**600k** (anchor: 600k → 36,959,150 states, ratio 61.6); **mrl=24 → p=0.772**, it bends *below* the line once the cap starts pruning (1M anchor → 29,656,838, ratio 29.7). The two are field-identical up to 100k. ⇒ the uncapped mrl=48 line is an **upper envelope for every cap**, so one linear constant (`70 states/node`) covers all mrl and over-provisions (safely) for small caps. Per-presentation spread is ~1.3× (ratio 44.4…81.9 at 50k) — absorbed by the 0.8 RAM safety and caught by the guard.
**[TRAP] Never calibrate memory on macOS RSS.** `ru_maxrss` reported bytes/state *falling* 204→162→135→113 B as states grew — structurally impossible. macOS's memory compressor evicts cold heap pages from the resident set, so peak RSS undercounts and grows sublinearly; a 1M/mrl48 probe sat at 0.59 GB resident for a ~14 GB working set while thrashing. Production is Linux. `tracemalloc` is the honest, platform-independent instrument (it counts CPython allocations, not resident pages). The internal inconsistency (marginal ΔRSS/Δstate = 35 B, below one bytes object) is what exposed it — **when a measured constant moves in a direction physics forbids, suspect the instrument, not the model.**
**Shipped** (all HIGH_SPEEDUP-only; the normal path runs one search in-process with no guard): `_avail_ram_gb()` = min(SC_PHYS_PAGES, `/proc/meminfo` MemAvailable, cgroup v2/v1 memory limit) — the old `SC_PHYS_PAGES` alone is the **host's total** and is blind to both the parent's footprint and a container cap; `_usable_cores()` = min(`sched_getaffinity`, `cpu_count`, cgroup `cpu.max` quota); `_est_gb_per_pres()` (`"auto"`, a positive number still pins it); `_MemGuard` on the existing 1024-node progress tick (checks every 8th → ~8k nodes).
**Guard semantics.** A worker over its allowance raises out of the *plain-Python* solve loop (the callback is invoked from the `while` loop, not from numba), the parent retries that presentation **serially with the whole budget** (usually enough — the pool slice was the constraint), and only if that also fails writes a row with `mem_abort: true` and the **truncated** `nodes_explored`. No presentation is silently lost and the runtime never OOMs. Two semantics worth knowing: (1) **a `mem_abort` row is terminal under `RESUME`** — `done` skips it forever; delete those rows to retry on a bigger machine; (2) on Colab (fork) a worker's `/proc/self/statm` resident **includes COW-shared parent pages** (numba/numpy/dataset), so the guard charges ~1–2 GB of shared footprint to each worker's private allowance — conservative (trips early), harmless at 1M/high-RAM, but it can cost throughput at small allowances.
**[TRAP] An exception crossing a pool boundary must have `args == its ctor args`.** `_MemBudgetExceeded.__init__` called `super().__init__(f"...")`; unpickling replays `cls(*args)` → `TypeError: missing 3 required positional arguments` **inside `multiprocessing.pool._handle_results`**, killing the result thread. Only the test that actually exercised the pool caught it; a serial test never pickles. Fix: `super().__init__(pres_id, nodes, rss_gb, limit_gb)` + `__str__`.
**Rules:** `GB_PER_PRES`/`N_WORKERS`/`HIGH_SPEEDUP` are result-neutral and stay OUT of `_run_prefix` (verified). A guard that never fires must be result-neutral — verified bit-identical stats on 5 presentations × both solvers. When you add a new terminal path through `run_dataset`, wire it into `logger.on_result()` too, or the cumulative `run/*` W&B counters silently lose those presentations. And **`pkill -9 -f <script>` while a probe is mid-run destroys the only expensive datapoint you have** — check for completed output first.
