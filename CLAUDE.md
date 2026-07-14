# CLAUDE.md — ACSolverX (repo-scoped)

Repo-local context and hard rules. Global rules still apply.

Each lesson below is one sentence carrying the operative rule, linked to its own file with the
full evidence. Read a linked file only when you need the detail behind that specific rule.
**Adding a lesson: write the full entry as a new `experiments/lessons/<slug>.md`, and add one
line here.** Never paste a full entry into this file — it is loaded in full on every session,
and a bloated CLAUDE.md gets ignored.

## Hard rules

- **Never open a PR.** Work lands by merging into the active branch. A worktree merges back
  into the branch it was created from (e.g. `test/stable-ac-moves-w4`), never `main`.
- **Never run a search above a `node_budget` of 1,000 yourself — no exceptions.** Any search
  Claude launches (local shell, test, repro, scratch script) is capped at **1,000 nodes** and
  ~10-20 presentations. Production budgets are the user's to run, on Colab. A search at budget
  `B` is exactly the first `B` pops of any longer search, so a bigger budget buys a slower
  repro, never a different behaviour. Prove the pipeline is budget-agnostic instead of
  brute-forcing one budget. [[TRAP]](experiments/lessons/local-run-budget-cap.md)

## Repo context

- AC-SolverX: JAX/flax RL solver for the Andrews–Curtis conjecture (Two-Hump paper). `envs/` (`ac_s.py`, `ac_moves.py`), `network.py`, `ppo_ac_s.py` are the JAX/GPU training stack.
- **This branch's experiment work is CPU + numba only** — no JAX, GPU, or PPO. The JAX code is a *spec to port from, never import*.
- Experiment code lives under `experiments/` ([map](experiments/README.md)); run outputs go to `results/` ([map](results/README.md)). Baseline greedy pipeline: `experiments/search/greedy_baseline.py` (solver, adapted from `greedy_search.ipynb`), `experiments/run_baseline.py` (jsonl + resume + W&B), `experiments/wandb_tracking.py` (W&B identity + charts), `experiments/greedy_baseline.ipynb` (CONFIG/SETUP/RUN). Also `experiments/analysis/` (the benchmark) and `experiments/equivalence_classes/` (`lib`/`search`/`pipeline`/`verify`/`phases`).
- **`results/greedy_baseline/` is a resume contract, not just data.** `run_baseline.py` globs it to find a run to continue and `difficulty_bins.py` does a non-recursive `os.listdir` on it — moving a `.jsonl` into a subfolder does not raise, it silently restarts a multi-day run. Never rename anything in there.
- **Scripts under `experiments/` find the repo root by walking up** until they see `experiments/` + `data/` — never by counting `os.path.dirname()` levels. A dirname chain encodes the file's depth and silently repoints at the wrong directory the moment the file moves.
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
- `test_crash_resume.py` guards the two `run_baseline.py` resume bugs that were once pinned as `xfail(strict=True)` and are now fixed. Never weaken it back to an xfail. [[TRAP]](experiments/lessons/run-baseline-two-known-bugs.md)

**Adding the stable-AC solver** (extra generator + relator, change of variables): implement a `SolverAdapter` in `experiments/greedy_tests/adapters.py` and append it to `ALL_ADAPTERS`. The contract, abelianization-invariant and packed-key suites then run against it at `n_gen = 3` **with no test rewriting** — they already run there today against the pure-Python `SpecAdapter`. See `experiments/greedy_tests/README.md`.

### ⛔ MANDATORY after ANY change to `experiments/equivalence_classes/`

```bash
.venv/bin/python3 -m pytest experiments/equivalence_classes -q          # 35 tests, ~65 s
.venv/bin/python3 experiments/equivalence_classes/verify/verify_proofs.py   # must exit 0
```

The verifier must print `ALL 135 EDGES VERIFY`. This suite was missing from `pytest.ini`'s `testpaths`
for a while, so nothing ran it by default and a change here could break it silently — it is collected
by a bare `pytest` now. It is also the safety net any refactor of that package leans on.

### Other suites

- `.venv/bin/python3 tests/wandb_tracking_test.py` — pure, offline, no wandb server needed.
- `.venv/bin/python3 tests/wandb_offline_integration.py <phase>` — phases: `cum_nodes identity fresh panels resume_full resume_partial heavy`.

## Lessons index

### Equivalence classes (the 261 unsolved reps)
- **Before calling a search converged, list the knobs and say which ones the evidence actually varied.** Five ACA configs agreed on 126 — and all five held the `max_total` ceiling at ≤28. Raising it to 34 found a new merge (`21_3 ≡ 21_29`, meeting at length 30) → **125**. Budget saturates and its saturation is real evidence; a ceiling defines the *space*, so raising it can expose states unreachable **at any budget**. But do not maximise it either: cap 40 contains that merge and still missed it, because a wider cap buys fewer pops/sec. [[TRAP]](experiments/lessons/ceiling-not-budget-was-binding.md)
- The 261 are **not** 261 problems: 168 up to change of variables (`Aut(F₂)`, exact — a wall), and fewer still under AC moves. Before searching for AC merges, quotient by every symmetry that preserves the *question* and re-measure the hump in the quotient — raw length is the wrong ruler, and the raw AC ball is exhausted below the hump. Never key on the peak-reduced form (not confluent: 259 classes, not 168), and never let the certificate verifier share the search's canonicalisation. A change-of-variables merge is one substitution (`canon(ψ(A)) == canon(B)`); that equality is **false by construction** on an AC merge, so never assert it there. [[WORKS]](experiments/lessons/search-the-aut-quotient-not-raw-length.md) · [the finding](results/equivalence_classes/EQUIVALENCE_FINDING.md) · [every class, derived step by step](results/equivalence_classes/PROOFS.md) — re-check with `experiments/equivalence_classes/verify/verify_proofs.py`

### Search correctness (numba)
- Before rewriting a priority queue, ask whether its keys are unique: if they are, pop order follows from the comparison alone and the heap implementation is free to change. That is why `greedy_compact` (nibble arena + int32 heap + open-addressing table, ~75 B/state vs ~220) pops identically. Assert the *first-seen* min/max relator strings — they pin discovery order. Size the memory constant at peak, not floor. [[WORKS]](experiments/lessons/compact-solver-arena-heap.md)
- In numba, a `uint8`/`int64` ternary silently unifies to `float64`, and a `uint64` returned to Python cannot be passed back into an `@njit` function. [[TRAP]](experiments/lessons/compact-solver-arena-heap.md)
- Stack-based free reduction is the safe form; any `rel[i+1]` peek in numba needs a bounds guard, and `str_to_arr('')` must return a 2-D `(0,2)`. [[TRAP]](experiments/lessons/reduce-relator-empty-word-oob.md)
- Store solved paths as Definition 2.1 moves `(i,j,k1,k2)`, not string pairs — the move inverts the **other** relator, so decode by replay, never by diffing states. [[WORKS]](experiments/lessons/store-paths-as-definition-2-1-moves.md)
- Never lower `MAX_RELATOR_LENGTH` to buy speed: it strictly shrinks the search space and can only reduce the solve rate. Cut `SUBSET` or `BUDGET` instead. [[WORKS]](experiments/lessons/max-relator-length-is-inert.md)
- Hoist any roll/transform that doesn't depend on the outer index out of nested rotation loops: O(L³) → O(L²). [[WORKS]](experiments/lessons/hoist-rotation-out-of-inner-loop.md)
- `@njit` the per-move math; leave the `heapq`/`dict` search orchestration in plain Python. [[WORKS]](experiments/lessons/numba-jit-split.md)

### HIGH_SPEEDUP / multiprocessing
- A hole in the jsonl is never a raced write — only the parent writes it. Grep `memory guard tripped` first (a deferred row lands only after the pool finishes); then suspect the filesystem. `flush()` is not durability: never append to a Drive mount, append to local disk and mirror whole-file. Resume self-heals, so a lost row is only fatal when it is lost *every* attempt. [[TRAP]](experiments/lessons/jsonl-hole-is-not-a-write-race.md)
- A computed result must reach disk before anything else is attempted with it: heavy mode parked every **solved** row in a RAM-only `deferred` list until the run ended, so a crash lost exactly the successes and resume re-searched them forever. Persist, then enrich in place. [[TRAP]](experiments/lessons/heavy-mode-defers-solved-rows.md)
- Same defect, second occurrence: a guard-tripped row waited ~29 h for its serial retry, so a dying session left no trace and the pool re-tripped it forever. Persist it at once as `mem_abort_pending`; `mem_abort` alone is terminal. An in-place update that cannot find its row must say so, not no-op. [[TRAP]](experiments/lessons/mem-abort-pending-row.md)
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
- An append-only log needs its torn trailing line **repaired before the first append**, never merely tolerated at read time; a crash-recovery test that exercises only the reader tests nothing. [[TRAP]](experiments/lessons/run-baseline-two-known-bugs.md)
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
