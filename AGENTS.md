# AGENTS.md — ACSolverX

## Hard rules

### ⛔ Scout small, then scale only the winner (heuristic experiments)

Do **not** default to long wall-clock campaigns or huge node budgets.

1. **Scout** — short runs, small node budgets (agent local cap is still ≤1,000),
   small presentation subsets. Compare candidate arms / weights quickly.
2. **Pick the winner** on a pre-registered denominator (and check the control has
   dynamic range before reading a null).
3. **Scale only that winner** — raise budget or ship a Colab CONFIG/SETUP/RUN
   notebook so the user can run multi-CPU and hand jsonl results back.
4. Never burn hours at one huge `B` "to be sure": a search at budget `B` is the
   first `B` pops of any longer search, so the scout ranking is the prefix of the
   deep run.

Full note: [`experiments/lessons/scout-then-scale-budgets.md`](experiments/lessons/scout-then-scale-budgets.md).
Same rule in [`CLAUDE.md`](CLAUDE.md).

### ⛔ Live Colab hotfix = `.py` only (never edit the open notebook)

While the user has Colab sessions running: fix heartbeat / pops/s / ETA / mirror /
resume bugs only in importable `experiments/**/*.py` on the notebook's `BRANCH`.
Do **not** edit the `.ipynb`. User Restart → Run All pulls via `UPDATE_REPO` + module
purge; Drive jsonl resume continues. Touch the notebook only for a new CONFIG knob,
and say so. Full note: [`experiments/lessons/colab-live-hotfix-py-only.md`](experiments/lessons/colab-live-hotfix-py-only.md).

### ⛔ MANDATORY before every `git push` (do not skip)

Every push on this branch must be logged. Same-day pushes are frequent (often 100s), so a
date alone is not enough — each push needs its own **UTC time** and **tip commit short SHA**.

1. Append a new section to `logs/DD-MM-YYYY.md` (create the day file if missing).
2. Heading format (required): `## HH:MM:SS UTC · \`<shortsha>\``.
3. Body: 1–3 sentences on what changed, with simple links to files added/changed.
4. Commit the log section together with the work (or immediately after). Then set
   `<shortsha>` to that commit's `git rev-parse --short HEAD` in a **follow-up commit**
   (do not chase a self-hash with amend — a commit cannot contain its own SHA).
5. Push. Never push without a headed log section whose short SHA points at the commit
   that carries the log body for this push.

Same rule in [`CLAUDE.md`](CLAUDE.md). Example day file: [`logs/28-07-2026.md`](logs/28-07-2026.md).

# Lessons Learned

### 2026-07-14 Equivalence tutorial verification environment

- [TRAP] This checkout has no `ACSolverX/.venv/bin/python3`; commands copied from the proof-book documentation fail here.
- [WORKS] Run the independent certificate verifier without modifying the project environment via `uv run --with numba --with numpy python3 <absolute-path>/experiments/equivalence_classes/verify/verify_proofs.py`.
- [WORKS] Pass absolute input and output paths to Tectonic in this workspace; relative `--outdir` resolution was unreliable.

### 2026-07-14 CoV best-z: allow pure powers later

- [DEFERRED] Best-z / length-sweep should eventually allow pure-power `z` (`xx`, `yy`, …). First-z (`NAIVE_Z_FAMILY`) stays mixed-only so pure powers do not preempt the picker.
- Current pipeline: best-z candidates come from the presentation's own relator subwords (`subword_candidates` / `enumerate_cov`); that path still filters `len({abs(g)}) < 2`. Do not implement the pure-power change until asked.

## Cursor Cloud specific instructions

The environment is CPU + numba only (the JAX/GPU stack in the repo root is a read-only spec — no accelerator is provisioned here). The startup update script provisions Python **3.12** at `/workspace/.venv`, installs `requirements.txt`, and adds `pytest`. Run everything through `.venv/bin/python3` exactly as `CLAUDE.md` documents.

- **[TRAP] This branch requires Python 3.12, NOT the 3.10 that `requirements.txt`'s header and `.github/workflows/tests.yml` imply.** Files such as `experiments/stable_ac/cov/ladder/mu_ladder_big.py` and `experiments/heuristic_search/runners/gen_page.py` use PEP 701 f-strings (same-quote nesting, backslashes in the expression) that only *parse* on 3.12+. On 3.10 the `tests/stable_ac` suite fails to even collect (`SyntaxError: f-string`). These files are not on `main`, which is why the 3.10 CI never hits it. The pinned `numba==0.63.1` / `numpy==2.1.3` install and run fine on 3.12.
- **[TRAP] `pytest` is not in `requirements.txt`.** CI installs it explicitly (`pip install ... pytest`); the update script installs it into `.venv`. `.venv` and `.pytest_tmp/` are gitignored — never stage them (see the never-`git add -A` lesson in `CLAUDE.md`).
- **Tests:** `.venv/bin/python3 -m pytest -q` is the full default tier; set `WANDB_MODE=offline WANDB_SILENT=true` to keep the `wandb`-marked tests offline. The greedy `--runslow` tier and the equivalence verifier (`verify_proofs.py`, must print `ALL 137 EDGES VERIFY`) are mandatory gates — see `CLAUDE.md` for exact commands. Node budgets are capped at 1000 for anything run locally.
- **Running the app (CPU greedy solver):** drive `experiments.run_baseline.run_dataset(cfg, node_budget)` (canonical config is `experiments/greedy_baseline.ipynb`, CONFIG cell). For a quick local smoke test set `USE_WANDB=False`, `MOUNT_DRIVE=False`, a small `SUBSET`, `node_budget<=1000`, and point `LOCAL_OUT_DIR` at a scratch dir — never write into `results/greedy_baseline/`, which is a resume contract (`CLAUDE.md`). Solved rows can be independently re-checked with `-m experiments.stable_ac.verify_results <dir>`, but only when paths are inline (`PATH_IN_SEPARATE_FILE=False`); with the default separate `_paths.jsonl` the verifier reports the main rows as having no certificate.
