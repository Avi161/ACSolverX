# `experiments/notebooks/` — the Colab drivers

Every Colab notebook in the repo lives here, and nowhere else. They were previously scattered across five directories (`experiments/`, `heuristic_search/`, `stable_ac/cov/notebooks/`, `stable_ac/nocov/`, and a partial `notebooks/`), which meant the only way to find the driver for a pipeline was to already know where it was.

A notebook's location on disk does **not** affect what it runs: every one of them clones the repo in SETUP and `chdir`s to the repo root before importing anything, so all module paths inside are absolute-from-root regardless of where the `.ipynb` sits. Moving them is behaviourally inert — the only cost is that a bookmarked Colab link points at the old path and must be re-opened once from the new one.

## Launch table

| notebook | drives | writes to |
|---|---|---|
| [`greedy_baseline.ipynb`](greedy_baseline.ipynb) | `experiments.run_baseline` — the baseline greedy over a dataset × budget | `results/greedy_baseline/` |
| [`hsearch_ab.ipynb`](hsearch_ab.ipynb) | `experiments.heuristic_search.runners.run_ab` — the scaled A/B campaign over heap orderings | the Drive dir on Colab, `results/hsearch/` locally (`run_ab`'s cwd-relative default); the synthesised writeups land in `results/heuristic_search/` |
| [`stable_ac/stable_ac_nocov.ipynb`](stable_ac/stable_ac_nocov.ipynb) | `experiments.stable_ac.nocov.run_nocov` — Branch A (No-CoV), knobs in `nocov/config_nocov.yaml` | `results/stable_ac/nocov/` |
| [`stable_ac/cov_baseline.ipynb`](stable_ac/cov_baseline.ipynb) | `experiments.stable_ac.cov.run.run_cov` — Branch B (one-shot change of variables), knobs in `cov/run/config_cov.yaml` | `results/stable_ac/cov/` |
| [`stable_ac/cov_top3_ms640_abel.ipynb`](stable_ac/cov_top3_ms640_abel.ipynb) + [`_len`](stable_ac/cov_top3_ms640_len.ipynb) | `experiments.stable_ac.cov.run.cov_top3_run` — the two CoV top-3 rules (abelian mass / shortest transformed pair) over all 640 ms640 presentations at budget 100,000. **All 3 ranks run on every presentation**, including below a solve, so the per-rank means are over one set; the deployed early-exit cost is recovered as `first_solve_nodes`. **One notebook per parallel session, one rule each**; they differ only in `RULE`. Method + gates: [`COV_TOP3_MS640.md`](../stable_ac/cov/run/COV_TOP3_MS640.md) | `results/stable_ac/cov/cov_top3/` |
| [`stable_ac/nb2_big_ladder.ipynb`](stable_ac/nb2_big_ladder.ipynb) | `experiments.stable_ac.cov.ladder.mu_ladder` — the original iterated orbit-floor ladder (rungs 20, beam 32) | `results/stable_ac/mu_scan/` |
| [`stable_ac/mu_ladder_big.ipynb`](stable_ac/mu_ladder_big.ipynb) | `experiments.stable_ac.cov.ladder.mu_ladder_big` — the scaled chunked ladder + `verify.verify_mu_ladder` | `results/stable_ac/mu_scan/` |

The root-level [`greedy_search.ipynb`](../../greedy_search.ipynb) is **not** one of these. It is the upstream AC-SolverX prototype kept as a read-only reference for the numba solver, never run as a pipeline.

## The shape every notebook here follows

Three cells — **CONFIG / SETUP / RUN** — and a fourth only when there is a structural reason for it (`cov_baseline.ipynb` and `mu_ladder_big.ipynb` each carry a MERGE cell, which must run once after every parallel chunk session has finished and so cannot fold into RUN). Results are always `jsonl`. The full pattern, and why deviating from it has broken runs before, is in [`../lessons/colab-notebook-pattern.md`](../lessons/colab-notebook-pattern.md).

Two contracts every notebook here ships, both mandatory:

- **The heartbeat is TIME-based** — a 60 s in-search beat with instantaneous pops/s, plus a ~5 min cumulative done/solved/ETA line. Never event-based: a slow CPU must show up as a falling rate, not as silence. [`../lessons/notebook-heartbeat-and-restart-contract.md`](../lessons/notebook-heartbeat-and-restart-contract.md)
- **Restart → Run All continues an already-open notebook** — `UPDATE_REPO` resets the clone, the `experiments.*` modules are purged from `sys.modules`, the run seeds back from Drive, and `.py`-only hotfixes take effect.

## Before you run one

- `BRANCH` in the CONFIG cell must match the actual git branch, or SETUP clones code that does not contain the runner you are calling. [`../lessons/notebook-branch-must-match-git.md`](../lessons/notebook-branch-must-match-git.md)
- **Pushing a notebook change does not reach a running Colab session.** Re-open the notebook from GitHub after any push that touches it; this is why logic belongs in `.py` modules, not in cells. [`../lessons/notebook-push-does-not-reach-colab.md`](../lessons/notebook-push-does-not-reach-colab.md)
- `git pull` is not a module reload — a pulled `.py` stays stale in `sys.modules` until the purge runs. [`../lessons/git-pull-is-not-a-module-reload.md`](../lessons/git-pull-is-not-a-module-reload.md)
- Every output path goes under `/content/drive/MyDrive/...`; the mount root `/content/drive/` is not writable. [`../lessons/colab-drive-mount-root-not-writable.md`](../lessons/colab-drive-mount-root-not-writable.md)
- Anchor to an absolute base before cloning, or each re-run nests the repo one directory deeper. [`../lessons/colab-setup-nested-clone.md`](../lessons/colab-setup-nested-clone.md)

Production budgets are the user's to run here on Colab. Local runs are capped at a `node_budget` of 1,000 — see the root [`CLAUDE.md`](../../CLAUDE.md).
