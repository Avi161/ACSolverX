# Hard residual after budget 10k → single Colab @ 100k

## What to run

**Primary dataset (hard-tail A/B):** [`hard_residual_10k_union.csv`](hard_residual_10k_union.csv)

- **1183 presentations** = every name that **any** of the 4 arms failed on at budget 10k
- Run **all 4 arms** on this same list (common denominator) so you can see who wins on the hard residual
- Searches: 1183 × 4 = **4732** @ budget 100000, cap 48

### Per-arm unsolved @10k (own rows)

| arm | unsolved | csv |
|---|---:|---|
| `baseline` | 831 | [`unsolved_10k_baseline.csv`](unsolved_10k_baseline.csv) |
| `s20_mk2` | 259 | [`unsolved_10k_s20_mk2.csv`](unsolved_10k_s20_mk2.csv) |
| `s20_mk2_mK2` | 507 | [`unsolved_10k_s20_mk2_mK2.csv`](unsolved_10k_s20_mk2_mK2.csv) |
| `s20_f4` | 753 | [`unsolved_10k_s20_f4.csv`](unsolved_10k_s20_f4.csv) |
| **union (any fail)** | **1183** | [`hard_residual_10k_union.csv`](hard_residual_10k_union.csv) |

### Failure patterns on the union

| failed arms | count |
|---|---:|
| `s20_f4` | 246 |
| `baseline` | 212 |
| `baseline,s20_mk2,s20_mk2_mK2,s20_f4` | 192 |
| `baseline,s20_f4` | 183 |
| `baseline,s20_mk2_mK2` | 106 |
| `baseline,s20_mk2_mK2,s20_f4` | 105 |
| `s20_mk2_mK2` | 66 |
| `s20_mk2` | 23 |
| `baseline,s20_mk2,s20_mk2_mK2` | 23 |
| `baseline,s20_mk2,s20_f4` | 10 |
| `s20_mk2,s20_mk2_mK2,s20_f4` | 9 |
| `s20_mk2_mK2,s20_f4` | 6 |
| `s20_mk2,s20_f4` | 2 |

### Coverage guarantee

- Every name in each `unsolved_10k_<arm>.csv` appears in the union CSV (asserted).
- Complete 10k intersection was 69,224; union includes 41 extra names that some arm failed on outside that intersection (resume-skewed rows).

## Optional gap fill (NOT hard — do not mix into hard-tail headline)

[`gap_fill_10k.csv`](gap_fill_10k.csv) — **3514** names that never failed at 10k but are incomplete (3425) or never-run (89). Only needed if you want a 100% 10k census; they will dilute the hard-tail comparison.

## Colab CONFIG sketch

```python
DATASET = 'results/heuristic_search/ac19_autmin_screen/hard_residual_10k_union.csv'
ARMS = ['baseline', 's20_mk2', 's20_mk2_mK2', 's20_f4']
BUDGET = 100_000
CAP = 48
CHUNK_INDEX = 1; N_CHUNKS = 1  # single Colab
```

Resume by `(arm, name)` so a restart cannot drop rows. After the run, score on the **same 1142-or-whatever union denominator** — do not drop to per-arm unsolved lists when comparing.

