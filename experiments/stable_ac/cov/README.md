# `experiments/stable_ac/cov/` — Branch B, one-shot change of variables

`cov.py` is the transform itself (the S-move-preserving re-coordinatisation, imported everywhere); everything else is grouped by what it does with it. The method walkthrough, with worked examples and the family-tag rules, is [`PIPELINE.md`](PIPELINE.md); the automorphism/relabel analysis of the sweep is [`AUTOMORPHISMS_COV.md`](AUTOMORPHISMS_COV.md).

| dir | holds |
|---|---|
| `run/` | the runners and their reviewed config — `run_cov.py` (+ `config_cov.yaml`), `orbit_greedy.py`, `run_mitm_aut.py`, `run_restart_tree.py` |
| `ladder/` | the μ-ladder family — `mu_ladder.py`, `mu_ladder_big.py` (scaled) + `mu_ladder_big_report.py`, `mu_descent_scan.py`, `export_mu_descents.py`, `orbit_links.py`, and `autcanon_fast.py` (the numba twin of `aut_canon`) |
| `escape/` | escalation of the CoV-resistant rows — `allcov_escalate.py`, `allcov_escape_report.py`, `restart_planner.py` |
| `figures/` | figure and table builders — `make_escape_fig.py`, `make_nodes_comparison_fig.py`, `rebuild_comparison_tables.py` |
| `verify/` | `verify_mu_ladder.py` — replays every accepted ladder orbit against slow `aut_canon`, so each row is a fast-vs-slow cross-check |
| `notebooks/` | the Colab drivers — `cov_baseline.ipynb`, `mu_ladder_big.ipynb` |
| `ak3/` | the AK(3) universal-CoV experiment (code only) — `sweep.py`, `census.py`, `analyze.py`, `ball.py`, `certify.py`, `certify_classical.py`. Its results and write-up live in `results/stable_ac/ak3/` |

Run everything as a module from the repo root, e.g. `.venv/bin/python3 -m experiments.stable_ac.cov.run.run_cov --config experiments/stable_ac/cov/run/config_cov.yaml`. Tests: `.venv/bin/python3 -m pytest tests/stable_ac -q`.
