# Family winners + recommended portfolio — holdout @ budget 1,000

Updated `2026-07-30T03:32:44.694274+00:00`

**selected_on** = ac1m_hard_aut train 120 (family winners from `smk_f_grid`; recommended = Aut-tune Colab portfolio)
**evaluated_on** = spent Aut holdout 60 + virgin fft fresh holdout 60

## Family winners

| family | arm | train | spent 60 | fresh 60 | mean nodes (spent) |
|---|---|---:|---:|---:|---:|
| **length** | `length` | 0/120 | **0/60** | **0/60** | — |
| **pure S** | `S20` | 49/120 | **30/60** | **27/60** | 449 |
| **pure MK** | `MK6_418` | 16/120 | **5/60** | **9/60** | 507 |
| **pure F** | `F4` | 30/120 | **10/60** | **15/60** | 393 |
| **S+MK** | `S20_MK2` | 54/120 | **33/60** | **27/60** | 453 |
| **S+F** | `S16_F4` | 48/120 | **29/60** | **23/60** | 420 |
| **MK+F** | `MK6_418_F8` | 31/120 | **11/60** | **11/60** | 534 |
| **S+MK+F** | `S28_MK2_F8` | 57/120 | **28/60** | **22/60** | 429 |

## Recommended portfolio (shipped Colab arms)

| arm | spent 60 | fresh 60 | mean nodes (spent) |
|---|---:|---:|---:|
| `length` | **0/60** | **0/60** | — |
| `S12` | **31/60** | **26/60** | 538 |
| `S28` | **29/60** | **23/60** | 421 |
| `S20_MK2` | **33/60** | **27/60** | 453 |
| `S24_K1_MK2` | **23/60** | **22/60** | 621 |

## Full arm table

| arm | S | K | MK | F | train | spent | fresh |
|---|---:|---:|---:|---:|---:|---:|---:|
| `length` | 0 | 0 | 0 | 0 | 0/120 | **0/60** | **0/60** |
| `S20` | 20 | 0 | 0 | 0 | 49/120 | **30/60** | **27/60** |
| `MK6_418` | 0 | 0 | 6.418 | 0 | 16/120 | **5/60** | **9/60** |
| `F4` | 0 | 0 | 0 | 4 | 30/120 | **10/60** | **15/60** |
| `S20_MK2` | 20 | 0 | 2 | 0 | 54/120 | **33/60** | **27/60** |
| `S16_F4` | 16 | 0 | 0 | 4 | 48/120 | **29/60** | **23/60** |
| `MK6_418_F8` | 0 | 0 | 6.418 | 8 | 31/120 | **11/60** | **11/60** |
| `S28_MK2_F8` | 28 | 0 | 2 | 8 | 57/120 | **28/60** | **22/60** |
| `S12` | 12 | 0 | 0 | 0 | — | **31/60** | **26/60** |
| `S28` | 28 | 0 | 0 | 0 | — | **29/60** | **23/60** |
| `S24_K1_MK2` | 24 | 1 | 2 | 0 | — | **23/60** | **22/60** |

## Notes

- Fixed arms — no re-tuning on either holdout.
- Spent holdout was used in prior S+K+MK selection (confirmatory).
- Fresh holdout is Aut-disjoint from train + spent.
- `S24_K1_MK2` is the only K>0 arm (shipped portfolio).

