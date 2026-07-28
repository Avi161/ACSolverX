# Heur-selected CoV vs greedy-oracle best-CoV at budget 1,000

For each of the 60 benchmark presentations, pick the subword CoV with the **lowest RECOMMENDED start priority** (static `phi` score — no search to select `z`), then run length-only and `RECOMMENDED` searches at budget 1,000 on that start. Compare to the shipped greedy-oracle best-CoV arms (`b1k_covgreedy` 45/60, `b1k_covheur` 43/60).

```text
prio = L + 2.53·K + 6.418·MK + 8.458·S + 3.292·xyimb   # min-heap, lower better
```

## Solve counts

| arm | start selection | ordering | solved / 60 |
|---|---|---|---:|
| `b1k_covgreedy` (shipped) | greedy-oracle bestcov | length-only | **45** |
| `b1k_covheur` (shipped) | greedy-oracle bestcov | RECOMMENDED | **43** |
| `hsel_covgreedy` | min RECOMMENDED start prio | length-only | **36** |
| `hsel_covheur` | min RECOMMENDED start prio | RECOMMENDED | **43** |

Heur-selected recipe equals shipped bestcov on **6/60** rows (differs on 54).

## Does selecting for RECOMMENDED help the ordering?

- `hsel_covheur` vs shipped `b1k_covheur`: **43** vs **43**
- `hsel_covgreedy` vs shipped `b1k_covgreedy`: **36** vs **45**
- New solves under hsel+RECOMMENDED (not in shipped covheur): none
- Lost vs shipped covheur: none
- New under hsel+length-only (not in shipped covgreedy): none
- Lost vs shipped covgreedy: ['543', '549', '581', '586', '602', '606', '632', '634', '635']

Hsel nestedness: `hsel_covgreedy` ⊂ `hsel_covheur` is True (shipped: `b1k_covheur` ⊂ `b1k_covgreedy` is True).

## Verdict

Selecting the CoV with the lowest RECOMMENDED **start** priority does **not** beat the greedy-oracle best-CoV on the heuristic arm (43/60 = 43/60, identical solved set). It does make the start look better on paper (mean prio 52.1 vs 70.9) and flips the ordering comparison: on these starts, RECOMMENDED strictly contains length-only (43 ⊃ 36), whereas under greedy-selected bestcov the opposite held (43 ⊂ 45). Length-only on the heur-picked start is much weaker (36/60 vs 45/60). Rows 634/635 stay unsolved under both selection rules at budget 1,000 with RECOMMENDED.

## Start priorities

- Mean hsel prio: 52.05 (median 53.30)
- Mean bestcov prio: 70.90 (median 64.16)
- Rows where hsel prio < bestcov prio: 54/60 (equal 6, higher 0)

## The two rows shipped covheur lost (634, 635)

- `ms634`: same_as_bestcov=False; hsel_covheur=False (1000); shipped covheur=False (1000)
- `ms635`: same_as_bestcov=False; hsel_covheur=False (1000); shipped covheur=False (1000)

## Source

- Input: [`cov_heur_b1k_subset60.csv`](cov_heur_b1k_subset60.csv)
- Table: [`cov_heur_select_b1k_subset60.csv`](cov_heur_select_b1k_subset60.csv)
- Runner: `experiments/heuristic_search/runners/cov_heur_select_b1k.py`
