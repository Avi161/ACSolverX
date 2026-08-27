# `cov/ml/` — which change of variables is worth running?

Ranks a presentation's ~100 applicable z's **before** any search, so the CoV method can be used without the oracle sweep that week 5 priced it with. Reads the existing sweeps in `results/stable_ac/cov/`; runs no search of its own.

The finding and every number: [`results/stable_ac/cov/ml/COV_QUALITY.md`](COV_QUALITY.md).

| file | role |
|---|---|
| `cov_features.py` | sweep jsonl → 88-column feature table. Everything is computable before the search runs; only the label builders at the bottom read `solved` / `nodes_explored`. |
| `cov_rank.py` | trains the rankers, scores them against random / shortest / moved-only / oracle pickers, writes `rank_b{B}.json`. |
| `cov_figures.py` | `simpson.png`, `abelian_mass.png`, `picker.png`. |

```
.venv/bin/python3 experiments/stable_ac/cov/ml/cov_rank.py --out results/stable_ac/cov/ml/rank_b10000.json
.venv/bin/python3 experiments/stable_ac/cov/ml/cov_rank.py --path results/stable_ac/cov/covsweep_1000_66_subnc2pxysb_mrl24_cyc_s60r6_07_20_26.jsonl --out results/stable_ac/cov/ml/rank_b1000.json
.venv/bin/python3 experiments/stable_ac/cov/ml/cov_figures.py
```

Needs `scikit-learn` (added to `.venv` for this work; numpy and numba are unchanged at 2.4.6 / 0.66.0).

## Before you change anything here

- **Group by `aut_canon_orig`, never by `pres_id`.** The 66-row benchmark holds 51 distinct Aut(F₂)-orbits, so a `pres_id` split trains on a presentation's own relabelled twin and reports leakage as skill. `load_dataset` builds `ds.group` for exactly this and every model call uses `GroupKFold` over it.
- **Never score this task with a pooled correlation.** Choosing a z happens *inside* one presentation; pooled over rows, between-presentation difficulty swamps the ordering and inverts which feature looks predictive (pooled says length r=+0.46 vs mass r=+0.11; per presentation says mass ρ=+0.81 vs length ρ=+0.36). [[TRAP]](../../../lessons/pooled-correlation-inverts-within-group-ranking.md)
- **An unsolved row is data, not a missing value.** `cost()` charges it the full budget. Training on solved rows only would delete exactly the outcomes the ranker exists to avoid.
- **A presentation whose every CoV is unsolved has a constant cost column** and therefore no rank correlation. It is dropped from the ρ medians and counted in the printout (`n_pres_flat`) — never scored as ρ = 0.
- **Break ties randomly and average — never with a stable `argsort`.** Abelian mass is a small integer and a median of 6 candidates tie at each presentation's minimum, so a stable sort reports the sweep file's row order as the rule's skill. It did: the one-pick number read 52/66 that way and is 47.4/66 with random ties. `pick_table` draws `N_TIEBREAK = 200` random orders; a fractional solve count is the expected signature, not a bug.
- **Keep the untrained heuristics as first-class arms.** The abelian-mass rule cannot leak, so it is the more trustworthy number whenever it matches the trained models.
