# Colab: AC19_extended Aut-min difficulty screen @ budget 1,000

Branch: **`cursor/heur-12h-anti-overfit-a42e`**

**ac-advisor:** REVISE (2026-07-30) — notebooks OK to run after contract patches below; write-up must follow the caveats.

## What it runs

| | |
|---|---|
| Dataset | `data/AC19_extended_aut_min.csv` — **72,779 Aut-minimal representatives** |
| Arms | `baseline` (length / hcompact) · `s20_mk2` (L+20S+2MK) |
| Budget | **1,000** nodes · cap 48 |
| Engine | `hcompact` + `N_WORKERS="auto"` |

Claim scope: difficulty of the **Aut-minimal representative**, not of the Aut-orbit and not of the 156,762 raw AC19_extended rows. Unstable Aut transfer of difficulty is **not** a theorem (advisor Red lines 2 & 4).

## Notebooks (5 chunks, run in parallel)

| # | file | CHUNK_INDEX |
|---:|---|---:|
| 1 | `experiments/heuristic_search/hsearch_colab_ac19_autmin_1k_c1.ipynb` | 1 |
| 2 | `experiments/heuristic_search/hsearch_colab_ac19_autmin_1k_c2.ipynb` | 2 |
| 3 | `experiments/heuristic_search/hsearch_colab_ac19_autmin_1k_c3.ipynb` | 3 |
| 4 | `experiments/heuristic_search/hsearch_colab_ac19_autmin_1k_c4.ipynb` | 4 |
| 5 | `experiments/heuristic_search/hsearch_colab_ac19_autmin_1k_c5.ipynb` | 5 |

Drive: `/content/drive/MyDrive/acsolverx/hsearch_ac19_autmin_1k/`

Stride sharding: chunk *k* gets rows where `i % 5 == k-1` (~14,556 reps × 2 arms ≈ **29k searches** / notebook).

## Realistic wall time

| setup | estimate |
|---|---|
| **5 Colabs in parallel** | **~10–25 min** wall |
| conservative (+ Drive I/O) | budget **~30–45 min** |
| 1× Colab | ~20–60 min (depends on 2 vs 8 vCPU) |

`N_WORKERS="auto"` = `os.cpu_count()` here (memory unbound at budget 1k). Free Colab ≈ 2 vCPU; Pro ≈ 8. Bulk solves are fast (~35–50/s serial); L>19 tail (~5.6k rows) is ~3–4/s and dominates the clock.

## Write-up rules (advisor — do before publishing counts)

1. **Stratify:** headline **L>19** (5,591) separately from **L≤19** (67,188). Bulk saturates for both arms @1k — pooled Δ≈0 is not “no difference”.
2. **Selection overlap:** 142 Aut-reps from `splits_ac1m_hard_aut` (96 train + 46 holdout that selected `s20_mk2`) sit in this CSV. Report a second column with those names excluded; state `(selected_on=ac1m_hard_aut train, evaluated_on=AC19 aut-min ∖ 142)`.
3. **Degenerates:** 261 rows have a relator of length ≤1 (free solves). Separate or drop before difficulty claims (effect gate: no relator below 3).
4. **Checkpoints** include 5/10/25/50/100/…/1000 — anytime curves are free from `solved_at`; no re-run needed.
5. Before publishing, add an AC19 replay verifier (solved1hop pattern keyed on the CSV). `KEEP_PATH=False` is **inert under hcompact** — solved rows still get recovered certificates.

## After the run

Merge the five chunk jsonls, then report anytime curves on complete rows, stratified as above.
