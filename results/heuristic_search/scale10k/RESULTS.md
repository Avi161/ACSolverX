# scale10k mini-research — RESULTS

Updated: `2026-07-29T10:23:36.340478+00:00` · wall end `2026-07-29T16:12:20.673566+00:00` · remaining `5.81 h`

Budgets ≤10,000; ≤1h/search; advisor-REVISE'd slices. **Colab handoff only after wall.**

## Slice `fresh_hard`

| arm | n | @1k | @2k | @5k | @10k | mean pops/s |
|---|---:|---:|---:|---:|---:|---:|
| `length` | 60 | 0 | 15 | 30 | 36 | 3548 |
| `s12` | 60 | 24 | 29 | 37 | 43 | 3509 |
| `s20` | 60 | 21 | 26 | 36 | 43 | 3360 |
| `recommended` | 60 | 12 | 18 | 25 | 31 | 2701 |

## Slice `l_stratified`

| arm | n | @1k | @2k | @5k | @10k | mean pops/s |
|---|---:|---:|---:|---:|---:|---:|
| `length` | 80 | 62 | 69 | 73 | 75 | 5092 |
| `s12` | 80 | 69 | 74 | 75 | 76 | 5101 |
| `s20` | 80 | 71 | 71 | 75 | 76 | 4962 |
| `recommended` | 80 | 67 | 70 | 73 | 74 | 4809 |

## Slice `unsolved124`

| arm | n | @1k | @2k | @5k | @10k | mean pops/s |
|---|---:|---:|---:|---:|---:|---:|
| `length` | 124 | 0 | 0 | 0 | 0 | 1933 |
| `s12` | 124 | 0 | 0 | 0 | 0 | 1648 |
| `s20` | 124 | 0 | 0 | 0 | 0 | 1467 |
| `recommended` | 124 | 0 | 0 | 0 | 0 | 1065 |

## Cost profile (local pops/s)

- `length` `L1296` b=1000: 6821.9 pops/s  solved=True
- `length` `L1296` b=5000: 3194.6 pops/s  solved=True
- `length` `L1296` b=10000: 8212.6 pops/s  solved=True
- `s20` `L1296` b=1000: 5336.9 pops/s  solved=True
- `s20` `L1296` b=5000: 2966.0 pops/s  solved=True
- `s20` `L1296` b=10000: 5119.8 pops/s  solved=True
- `recommended` `L1296` b=1000: 8625.5 pops/s  solved=True
- `recommended` `L1296` b=5000: 7248.3 pops/s  solved=True
- `recommended` `L1296` b=10000: 5852.5 pops/s  solved=True
- `length` `L152166` b=1000: 7123.6 pops/s  solved=True
- `length` `L152166` b=5000: 6131.7 pops/s  solved=True
- `length` `L152166` b=10000: 4451.8 pops/s  solved=True
- `s20` `L152166` b=1000: 5630.7 pops/s  solved=True
- `s20` `L152166` b=5000: 4885.6 pops/s  solved=True
- `s20` `L152166` b=10000: 4756.9 pops/s  solved=True
- `recommended` `L152166` b=1000: 5926.3 pops/s  solved=True
- `recommended` `L152166` b=5000: 5217.8 pops/s  solved=True
- `recommended` `L152166` b=10000: 5158.7 pops/s  solved=True
- `length` `H220504` b=1000: 5627.5 pops/s  solved=False
- `length` `H220504` b=5000: 5460.2 pops/s  solved=True
- `length` `H220504` b=10000: 5443.2 pops/s  solved=True
- `s20` `H220504` b=1000: 6070.1 pops/s  solved=True
- `s20` `H220504` b=5000: 5636.9 pops/s  solved=True
- `s20` `H220504` b=10000: 5217.0 pops/s  solved=True
- `recommended` `H220504` b=1000: 4846.4 pops/s  solved=True
- `recommended` `H220504` b=5000: 4435.7 pops/s  solved=True
- `recommended` `H220504` b=10000: 4165.6 pops/s  solved=True
- `length` `H220551` b=1000: 4578.0 pops/s  solved=False
- `length` `H220551` b=5000: 3979.1 pops/s  solved=False
- `length` `H220551` b=10000: 3831.0 pops/s  solved=False
- `s20` `H220551` b=1000: 4187.1 pops/s  solved=False
- `s20` `H220551` b=5000: 3810.9 pops/s  solved=True
- `s20` `H220551` b=10000: 3805.8 pops/s  solved=True
- `recommended` `H220551` b=1000: 3487.0 pops/s  solved=False
- `recommended` `H220551` b=5000: 2997.3 pops/s  solved=False
- `recommended` `H220551` b=10000: 2945.2 pops/s  solved=True

## Portfolio (matched total nodes, fresh hard)

- single s20 @10k: 20/30
- portfolio {12,20,32} @3333 each: 16/30 (oracle best-of-3; runnable = first-hit order not claimed)

## Method notes

- Headline slice is L-stratified / outcome-unconditioned ([`slice_l_stratified.json`](slice_l_stratified.json)).
- Fresh hard reach slice never touched by s_grid ([`slice_fresh_hard.json`](slice_fresh_hard.json)).
- Cap 48 AC1M; cap 64 unsolved124. `solved`/`solved_at` only for anytime.
- Do not pre-commit Colab arm until wall; lean S may plateau (EXP-16).

