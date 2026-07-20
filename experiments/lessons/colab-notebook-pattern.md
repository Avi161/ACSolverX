# [2026-07-20] Colab notebooks follow the greedy_baseline 3-cell pattern [WORKS]

`cov_baseline.ipynb` was rebuilt for the chunked 10k sweep and the shape that works is exactly `greedy_baseline.ipynb`'s: **three cells — CONFIG / SETUP / RUN — and a fourth only when structurally necessary.** (cov's MERGE cell qualifies: it must run ONCE after every parallel chunk session has finished, and each session holds only its own chunk locally, so folding it into RUN would error at the end of every session.)

What each cell owns:

- **CONFIG** — every knob as a plain constant with an inline comment; header says "edit ONLY this cell". Knobs override the reviewed yaml (`config_cov.yaml` etc.), never replace it. `BRANCH` must match the actual git branch (a mismatch clones the wrong code silently).
- **SETUP** — clone-or-`reset --hard` from `BRANCH`; pip installs; local repo-root walk-up (never dirname counting); **purge `experiments.*` from `sys.modules`** (a pull rewrites .py files but keeps old module objects — pull ≠ reload); when `MOUNT_DRIVE`, mount Drive and **seed back** Drive→local with bigger-file-wins so a fresh VM resumes where the last session stopped.
- **RUN** — import the runner and call `run(...)` with the CONFIG knobs. The runner writes its jsonl **locally, never by appending onto the Drive FUSE mount** (slow/flaky — the same reason `run_baseline` stages locally); a daemon mirror thread (which must never print) copies `*.jsonl` → Drive every ~3 min, plus a final sync after `run()` returns.

Invariants: results are **always jsonl** — one file per budget (per chunk when chunked), filename = resume identity, jsonl is the source of truth; W&B or any other sink only mirrors it.

Editing/verifying a notebook: edit the raw JSON with a script and `compile()` every cell's source; then **verify by exec'ing the actual cells locally with the runner stubbed AFTER the SETUP cell has run** — SETUP's module purge evicts a stub installed before it (confirmed 2026-07-20: a pre-SETUP stub silently let the RUN cell call the real pipeline). And remember a push never reaches an already-open Colab — re-open the notebook from GitHub.

**Rule:** new Colab notebooks = CONFIG / SETUP / RUN (+ an extra cell only with a structural reason), knobs-over-yaml in CONFIG, module purge + Drive seed-back in SETUP, local-jsonl-writes + background Drive mirror in RUN, jsonl always; verify by exec'ing the real cells with a post-SETUP stub.
