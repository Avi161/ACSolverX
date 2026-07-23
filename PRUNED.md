# PRUNED — what this branch dropped, and where it still lives

`research/w5/stable-ac-escape` is a clean restart cut from `research/stable-ac-escape` at **`e57d8b4`**. Nothing below is gone: that branch is pushed and complete, so `git show e57d8b4:<path>` or `git checkout research/stable-ac-escape -- <path>` brings any of it back verbatim.

The overnight escape push (2026-07-20 → 07-21, [`experiments/stable_ac/ESCAPE_PLAN.md`](experiments/stable_ac/ESCAPE_PLAN.md)) shipped six Colab notebooks. Five did not produce a solve or a lead worth continuing; **nb2 (the orbit-floor μ-ladder) is the one that did**, so it and its toolchain are all that survive here.

## Removed

| arm | notebook | code | results | test |
|---|---|---|---|---|
| T1 portfolio on the 124 | `nb1_floors_portfolio`, `nb4_portfolio_124`, `idea_bench/portfolio_124.ipynb` | `experiments/stable_ac/idea_bench/` (harness, run_sweep, run_portfolio, 18 strategies) | `results/stable_ac/{portfolio,idea_bench}/` | `test_portfolio.py` |
| T2 static rank-4/5 | `nb5_static_rank`, `nocov/static_rank.ipynb` | `nocov/run_static_rank.py`, `config_static_rank.yaml`, `verify_static_rank.py` | `results/stable_ac/static_rank/` | `test_run_static_rank.py` |
| T3 descent-probe ranking | — | `cov/descent_probe.py` | `results/stable_ac/mu_scan/descent_probe_*.jsonl` | — |
| T4 stall-triggered CoV escape | `nb3_stall_escape` | `cov/stall_escape.py` | `results/stable_ac/stall_escape/` | `test_stall_escape.py` |
| T6 Prover9 ATP oracle | — | `experiments/stable_ac/atp/` | `results/stable_ac/atp/` | — |
| inflate-and-descend | `nb6_inflate_descend` | `cov/inflate_descend.py` | `results/stable_ac/inflate/` | `test_inflate_descend.py` |

Also dropped: `experiments/stable_ac/RUN_ME_MORNING.md` (launch instructions for the five deleted notebooks; the plan record itself stays in `ESCAPE_PLAN.md`).

`cov/descent_probe.py` was not one of the six arms — it went because `idea_bench.harness` was its only bench loader, so the prune broke its CLI and nothing surviving drives it.

## Kept deliberately

- **nb2 and its chain**: `experiments/notebooks/nb2_big_ladder.ipynb` → `cov/mu_ladder.py` + `cov/mu_descent_scan.py` + `cov/export_mu_descents.py`, results in `results/stable_ac/mu_scan/`.
- **All CoV work**: `experiments/stable_ac/cov/` (transform, runner, sweep, MITM, restart tree, `ak_3_universal_test/`) and all 33 MB of `results/stable_ac/cov/`.
- **All lessons**: `experiments/lessons/` in full — the memory of everything tried, including the arms deleted above.
- **The evidence the deleted code produced**: idea_bench's 16-strategy race moved to [`results/stable_ac/IDEA_BENCH_RESULTS.md`](results/stable_ac/IDEA_BENCH_RESULTS.md) rather than deleted with its package. Theory notes (`results/stable_ac/theory/`) and `MU_SCAN_FINDINGS.md` untouched.
- `nocov/` (Branch A), `thickenable/`, the greedy baseline pipeline, `equivalence_classes/`, and the upstream JAX/PPO stack.
