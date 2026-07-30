# Family winners on benchmark_subset_60 @ budget 1,000

Updated `2026-07-30T03:52:54.708624+00:00`

**evaluated_on** = `benchmark/subsets/benchmark_subset_60.json` (difficulty-binned ladder; not the Aut hard holdout)
**selected_on** = ac1m_hard_aut train 120 (arms fixed from smk_f_grid)

| family | arm | train | spent 60 | fresh 60 | **bench60 @1k** | mean nodes |
|---|---|---:|---:|---:|---:|---:|
| **length** | `length` | 0/120 | 0/60 | 0/60 | **29/60** | 176 |
| **pure S** | `S20` | 49/120 | 30/60 | 27/60 | **36/60** | 161 |
| **pure MK** | `MK6_418` | 16/120 | 5/60 | 9/60 | **37/60** | 257 |
| **pure F** | `F4` | 30/120 | 10/60 | 15/60 | **26/60** | 195 |
| **S+MK** | `S20_MK2` | 54/120 | 33/60 | 27/60 | **37/60** | 153 |
| **S+F** | `S16_F4` | 48/120 | 29/60 | 23/60 | **36/60** | 201 |
| **MK+F** | `MK6_418_F8` | 31/120 | 11/60 | 11/60 | **35/60** | 284 |
| **S+MK+F** | `S28_MK2_F8` | 57/120 | 28/60 | 22/60 | **38/60** | 218 |

### Per-bin solves (bench60)

| arm | b0 | b1 | b2 | b3 | b4 | b5 | b6 | b7 | b8 | b9 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `length` | 6/6 | 6/6 | 6/6 | 6/6 | 5/6 | 0/6 | 0/6 | 0/6 | 0/6 | 0/6 |
| `S20` | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 | 5/6 | 1/6 | 0/6 | 0/6 | 0/6 |
| `MK6_418` | 6/6 | 6/6 | 6/6 | 6/6 | 4/6 | 5/6 | 2/6 | 2/6 | 0/6 | 0/6 |
| `F4` | 6/6 | 6/6 | 6/6 | 6/6 | 2/6 | 0/6 | 0/6 | 0/6 | 0/6 | 0/6 |
| `S20_MK2` | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 | 5/6 | 2/6 | 0/6 | 0/6 | 0/6 |
| `S16_F4` | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 | 4/6 | 2/6 | 0/6 | 0/6 | 0/6 |
| `MK6_418_F8` | 6/6 | 6/6 | 6/6 | 6/6 | 4/6 | 3/6 | 2/6 | 2/6 | 0/6 | 0/6 |
| `S28_MK2_F8` | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 | 5/6 | 3/6 | 0/6 | 0/6 | 0/6 |

## Notes

- Bench60 is an easy→hard ladder (many bin-0/1 presentations). Length solves a large fraction here; it scored 0 on the Aut-hard 60s.
- Do not re-rank from this set alone — selection stayed on Aut train.
- Unsolved = unsolved within budget 1000.

