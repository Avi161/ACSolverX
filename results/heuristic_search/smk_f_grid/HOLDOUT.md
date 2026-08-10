# S×MK×F holdout read — budget 1,000

Updated `2026-07-30T03:29:30.103661+00:00`

**selected_on** = ac1m_hard_aut train 120 (grid winner `S28_MK2_F8`)
**evaluated_on (primary)** = ac1m_hard_aut holdout 60 (spent — used in prior S/K/MK tune)
**evaluated_on (virgin)** = fft fresh holdout 60

## Spent Aut holdout 60

| arm | S | MK | F | solved | mean nodes |
|---|---:|---:|---:|---:|---:|
| `length` | 0 | 0 | 0 | **0/60** | — |
| `S20` | 20 | 0 | 0 | **30/60** | 449 |
| `S20_MK2` | 20 | 2 | 0 | **33/60** | 453 |
| `S20_MK2_F4` | 20 | 2 | 4 | **27/60** | 361 |
| `S28_MK2_F8` | 28 | 2 | 8 | **28/60** | 429 |

## Fresh holdout 60

| arm | S | MK | F | solved | mean nodes |
|---|---:|---:|---:|---:|---:|
| `length` | 0 | 0 | 0 | **0/60** | — |
| `S20` | 20 | 0 | 0 | **27/60** | 496 |
| `S20_MK2` | 20 | 2 | 0 | **27/60** | 449 |
| `S20_MK2_F4` | 20 | 2 | 4 | **29/60** | 480 |
| `S28_MK2_F8` | 28 | 2 | 8 | **22/60** | 422 |

## Notes

- Fixed arms from train selection — no re-tuning on holdout.
- Spent holdout was already used for earlier S+K+MK selection; treat as confirmatory.
- Fresh holdout is Aut-disjoint from train + spent (see split note).

