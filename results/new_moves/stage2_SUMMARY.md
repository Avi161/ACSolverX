# New moves on subset-60 at tiny budgets — stage 2

One 1,000-node run per arm per presentation (`solved_at` gives every smaller budget); cap 24, cyclic reduction on. Solve counts include ONLY independently verified paths (`certify.verify_solution` for certificate arms, `moves_to_states` replay for plain arms — for cov arms the verified object is the Whitehead image's path; the portal supplies the rest of the claim); unverified solves are listed separately and count as failures. The `claim` column is load-bearing: an `AC_TRIVIAL_IFF` solve proves the original presentation AC-trivial without materialising a path for it, and must never be pooled with `AC_EQ path` counts as if it were one.

| arm | moves | ordering | claim | @100 | @250 | @500 | @1000 | median nodes | median path | macro-edge solves | wall s | nodes/s |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| greedy | sub | L | AC_EQ path | 17 | 20 | 26 | 29 | 61 | 16 | - | 37.7 | 958 |
| s20_mk2 | sub | s20_mk2 | AC_EQ path | 21 | 28 | 35 | 37 | 52 | 22 | - | 57.6 | 497 |
| ncrw_L | sub+goal+ncrw | L | AC_EQ path | 17 | 20 | 26 | 29 | 60 | 15 | 28 | 84.7 | 426 |
| ncrw_s20_mk2 | sub+goal+ncrw | s20_mk2 | AC_EQ path | 21 | 28 | 35 | 37 | 51 | 20 | 36 | 56.6 | 505 |
| cov_L | Whitehead reduce, then sub | L | AC_TRIVIAL_IFF portal | 20 | 24 | 32 | 36 | 65.5 | 16.0 | - | 43.4 | 710 |
| cov_s20_mk2 | Whitehead reduce, then sub | s20_mk2 | AC_TRIVIAL_IFF portal | 22 | 30 | 35 | 37 | 45 | 19 | - | 43.7 | 642 |

Total wall time for the whole grid: 109 s. Node budgets are pop counts; the macro arms pay more wall time per pop (see nodes/s), so read the table twice — once at equal nodes, once at equal time via the nodes/s column.

Regenerate: `python -m experiments.search.bench_new_moves --budget 1000 --stage2`.
