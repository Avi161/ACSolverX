# scale10k mini-research — RESULTS

Updated: `2026-07-29T06:12:45.926092+00:00` · wall end `2026-07-29T16:12:20.673566+00:00` · remaining `10.00 h`

Budgets ≤10,000; ≤1h/search; advisor-REVISE'd slices. **Colab handoff only after wall.**

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

## Method notes

- Headline slice is L-stratified / outcome-unconditioned ([`slice_l_stratified.json`](slice_l_stratified.json)).
- Fresh hard reach slice never touched by s_grid ([`slice_fresh_hard.json`](slice_fresh_hard.json)).
- Cap 48 AC1M; cap 64 unsolved124. `solved`/`solved_at` only for anytime.
- Do not pre-commit Colab arm until wall; lean S may plateau (EXP-16).

