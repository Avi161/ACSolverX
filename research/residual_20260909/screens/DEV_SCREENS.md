# Dev / regression60 screens

Generated from harness runs at commit `98f719e2ad9ce98cac1525c0984555f4711e412b`. Python 3.11.15, NumPy 2.1.3, Numba 0.63.1, llvmlite 0.46.0. One thread (`NUMBA_NUM_THREADS=OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=1`), warmup on for every run (`research.residual_20260909.harness`'s default), each screen run serially, one at a time.

Panels: `research/residual_20260909/panels/dev.csv` (102 rows, drawn from the 727-row residual the frozen census policy left unsolved at budget 1000 -- so 0/102 at budget 1000 is the panel construction working, not a search regression) and `research/residual_20260909/panels/regression60.csv` (60 rows the census already solved, sampled near the 1000-unit budget limit, mostly via `incumbent_restart`). `val.csv`, `test.csv` and `rest.csv` were not read or run, per instructions.

## 1. Reachability curve (dev.csv, 102 rows)

`frozen` (the published census policy: donor prepass -> plain-S20 prefix -> incumbent restart, sharing one heterogeneous work-unit budget) at increasing budgets, plus two single-arm reference points at higher budget.

| budget | policy | solved / 102 | total nodes | search wall sum (s) |
|---:|---|---:|---:|---:|
| 1000 | frozen | 0 | 102000 | 34.70 |
| 2000 | frozen | 87 | 131578 | 57.69 |
| 3000 | frozen | 94 | 141720 | 69.28 |
| 5000 | frozen | 98 | 151708 | 77.94 |
| 10000 | frozen | 98 | 171708 | 113.12 |
| 10000 | plain_s20 (single arm) | 88 | 418581 | 158.11 |
| 3000 | aut_edges_s20 (single arm) | 96 | 60024 | 48.96 |

`frozen` plateaus at 98/102 from budget 5000 onward (10000 adds no further solves over 5000 on this panel). Note the budget-1000 anomaly explained in section 2: `frozen` at budget 1000 gets 0/102 here only because its own donor+plain prefix (up to 1122 of the 1000-unit budget nominally, capped by the shared budget) leaves the incumbent stage little or no budget on rows already known to be hard for the donor/plain stages; `incumbent` run alone with the same 1000-unit budget gets 87/102 (section 2).

## 2. Stage-isolation table (dev.csv, budget 1000)

Each policy run alone with the full 1000-unit budget from the original input (no shared prefix charged against it by another stage).

| policy | solved / 102 | verified | total nodes | search wall sum (s) | search cpu sum (s) |
|---|---:|---:|---:|---:|---:|
| frozen | 0 | 0 | 102000 | 34.70 | 34.70 |
| donor_only | 1 | 1 | 1539 | 0.07 | 0.07 |
| plain_s20 | 4 | 4 | 101676 | 31.60 | 31.60 |
| incumbent | 87 | 87 | 39336 | 28.53 | 28.52 |
| aut_edges_s20 | 86 | 86 | 39788 | 29.91 | 29.91 |
| ordinary_T | 50 | 50 | 79881 | 56.81 | 56.79 |
| frozen_reallocated | 87 | 87 | 40714 | 27.56 | 27.56 |

`donor_only` solves only 1/102: the strict-donor route almost never matches on this panel by construction (these rows already failed the census donor+plain+incumbent chain at budget 1000, and the donor stage is the cheapest/most restrictive of the three). `incumbent` and `frozen_reallocated` (donor stage, then incumbent gets the rest of the budget) land within one solve of each other (87 vs 87) and mostly agree on *which* rows (see the pairwise section of `compare_dev_1000.json`: 0 gained/0 lost between them). `ordinary_T` (the `s20` arm with the donor-relative T bonus, no generator neighbors) is the weakest of the routed arms here (50/102).

## 3. Union of dev rows solved by any 1000-unit policy

91/102 dev rows are solved by at least one of the 7 policies above at budget 1000; 11 are solved by none of them at this budget.

Never solved by any 1000-unit single-policy run: `ac19_11753`, `ac19_18413`, `ac19_26598`, `ac19_30433`, `ac19_31106`, `ac19_38222`, `ac19_45684`, `ac19_49255`, `ac19_54337`, `ac19_60781`, `ac19_62145`.

Rows by how many of the 7 policies solved them: 5 policies: 2 rows, 4 policies: 46 rows, 3 policies: 39 rows, 1 policies: 4 rows.

<details><summary>Full union table (name, policies that solved it)</summary>

| name | # policies | policies |
|---|---:|---|
| ac19_109 | 5 | aut_edges_s20, donor_only, frozen_reallocated, incumbent, ordinary_T |
| ac19_2376 | 5 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T, plain_s20 |
| ac19_102 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_10820 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_11261 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_12112 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_14165 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_15047 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_16343 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_18516 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_19132 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_22112 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_22628 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_230 | 4 | aut_edges_s20, frozen_reallocated, incumbent, plain_s20 |
| ac19_28253 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_30535 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_3175 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_31971 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_3566 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_36375 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_37661 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_3794 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_38100 | 4 | aut_edges_s20, frozen_reallocated, incumbent, plain_s20 |
| ac19_41186 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_41336 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_41890 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_45464 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_45920 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_46402 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_46703 | 4 | aut_edges_s20, frozen_reallocated, incumbent, plain_s20 |
| ac19_46895 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_47367 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_47899 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_48114 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_49785 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_50491 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_53119 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_54243 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_5478 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_60157 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_64188 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_65754 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_66662 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_70762 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_70877 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_72274 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_8222 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_8984 | 4 | aut_edges_s20, frozen_reallocated, incumbent, ordinary_T |
| ac19_16098 | 3 | aut_edges_s20, frozen_reallocated, incumbent |
| ac19_1880 | 3 | aut_edges_s20, frozen_reallocated, incumbent |
| ac19_20172 | 3 | aut_edges_s20, frozen_reallocated, incumbent |
| ac19_25075 | 3 | aut_edges_s20, frozen_reallocated, incumbent |
| ac19_27787 | 3 | aut_edges_s20, frozen_reallocated, incumbent |
| ac19_28281 | 3 | aut_edges_s20, frozen_reallocated, incumbent |
| ac19_28696 | 3 | frozen_reallocated, incumbent, ordinary_T |
| ac19_28930 | 3 | aut_edges_s20, frozen_reallocated, incumbent |
| ac19_32128 | 3 | aut_edges_s20, frozen_reallocated, incumbent |
| ac19_32315 | 3 | aut_edges_s20, frozen_reallocated, incumbent |
| ac19_35248 | 3 | aut_edges_s20, frozen_reallocated, incumbent |
| ac19_35367 | 3 | aut_edges_s20, frozen_reallocated, incumbent |
| ac19_37610 | 3 | aut_edges_s20, frozen_reallocated, incumbent |
| ac19_41092 | 3 | aut_edges_s20, frozen_reallocated, incumbent |
| ac19_43158 | 3 | aut_edges_s20, frozen_reallocated, incumbent |
| ac19_46302 | 3 | aut_edges_s20, frozen_reallocated, incumbent |
| ac19_46649 | 3 | aut_edges_s20, frozen_reallocated, incumbent |
| ac19_47160 | 3 | aut_edges_s20, frozen_reallocated, incumbent |
| ac19_47717 | 3 | aut_edges_s20, frozen_reallocated, incumbent |
| ac19_48604 | 3 | aut_edges_s20, frozen_reallocated, incumbent |
| ac19_4894 | 3 | aut_edges_s20, frozen_reallocated, incumbent |
| ac19_50043 | 3 | aut_edges_s20, frozen_reallocated, incumbent |
| ac19_50926 | 3 | aut_edges_s20, frozen_reallocated, incumbent |
| ac19_51462 | 3 | frozen_reallocated, incumbent, ordinary_T |
| ac19_5250 | 3 | aut_edges_s20, frozen_reallocated, incumbent |
| ac19_5652 | 3 | aut_edges_s20, frozen_reallocated, incumbent |
| ac19_56843 | 3 | aut_edges_s20, frozen_reallocated, incumbent |
| ac19_58416 | 3 | aut_edges_s20, frozen_reallocated, incumbent |
| ac19_59576 | 3 | aut_edges_s20, frozen_reallocated, incumbent |
| ac19_64447 | 3 | aut_edges_s20, frozen_reallocated, incumbent |
| ac19_65140 | 3 | aut_edges_s20, frozen_reallocated, incumbent |
| ac19_65325 | 3 | aut_edges_s20, frozen_reallocated, incumbent |
| ac19_6678 | 3 | aut_edges_s20, frozen_reallocated, incumbent |
| ac19_67055 | 3 | aut_edges_s20, frozen_reallocated, incumbent |
| ac19_67450 | 3 | aut_edges_s20, frozen_reallocated, incumbent |
| ac19_68563 | 3 | aut_edges_s20, frozen_reallocated, incumbent |
| ac19_69707 | 3 | aut_edges_s20, frozen_reallocated, incumbent |
| ac19_7037 | 3 | aut_edges_s20, frozen_reallocated, incumbent |
| ac19_70826 | 3 | aut_edges_s20, frozen_reallocated, incumbent |
| ac19_20055 | 1 | aut_edges_s20 |
| ac19_20074 | 1 | ordinary_T |
| ac19_63094 | 1 | ordinary_T |
| ac19_67699 | 1 | ordinary_T |

</details>

## 4. regression60.csv loss table (already-solved hard rows, budget 1000)

`regression60.csv` holds 60 rows the census already solved near the 1000-unit budget limit (mostly via `incumbent_restart`). `reg60_frozen_1000` reproduces the census exactly: 60/60 solved and verified, with `nodes_explored`, `policy_route`, and `elementary_count` matching the census records byte-for-byte on all 60 rows (checked directly against the `nodes_explored`/`route`/`elementary_count` columns carried in `regression60.csv` itself -- zero mismatches).

| policy | solved / 60 | lost vs frozen | gained vs frozen | mean nodes delta vs frozen |
|---|---:|---:|---:|---:|
| aut_edges_s20 | 60 | 0 | 0 | -886.2 |
| incumbent | 60 | 0 | 0 | -886.2 |
| frozen_reallocated | 60 | 0 | 0 | -872.0 |

No alternative policy loses any of the 60 already-solved regression rows at budget 1000 (0 lost in every row above); all three actually use far fewer nodes per row than `frozen` because they get the full 1000-unit budget directly instead of paying the donor/plain charges first.

## 5. Per-run wall / CPU sums (all 17 screens)

| tag | rows | solved | verified | nodes | search wall sum (s) | search wall max (s) | search cpu sum (s) | certificate wall sum (s) | warmup wall (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| dev_frozen_1000 | 102 | 0 | 0 | 102000 | 34.701 | 0.482 | 34.699 | 0.0000 | 0.128 |
| dev_frozen_2000 | 102 | 87 | 87 | 131578 | 57.689 | 1.619 | 57.416 | 0.5688 | 0.115 |
| dev_frozen_3000 | 102 | 94 | 94 | 141720 | 69.279 | 3.140 | 67.943 | 0.6710 | 0.113 |
| dev_frozen_5000 | 102 | 98 | 98 | 151708 | 77.940 | 5.213 | 77.931 | 0.6712 | 0.120 |
| dev_frozen_10000 | 102 | 98 | 98 | 171708 | 113.120 | 13.885 | 112.394 | 0.7071 | 0.111 |
| dev_plain_s20_10000 | 102 | 88 | 88 | 418581 | 158.112 | 6.064 | 158.064 | 0.9474 | 0.131 |
| dev_donor_only_1000 | 102 | 1 | 1 | 1539 | 0.068 | 0.044 | 0.068 | 0.0871 | 0.128 |
| dev_plain_s20_1000 | 102 | 4 | 4 | 101676 | 31.597 | 0.513 | 31.595 | 0.0430 | 0.169 |
| dev_incumbent_1000 | 102 | 87 | 87 | 39336 | 28.527 | 1.100 | 28.523 | 0.6027 | 0.117 |
| dev_aut_edges_s20_1000 | 102 | 86 | 86 | 39788 | 29.912 | 1.118 | 29.907 | 0.5817 | 0.130 |
| dev_ordinary_T_1000 | 102 | 50 | 50 | 79881 | 56.805 | 1.152 | 56.786 | 0.4678 | 0.143 |
| dev_frozen_reallocated_1000 | 102 | 87 | 87 | 40714 | 27.561 | 1.042 | 27.558 | 0.6321 | 0.125 |
| dev_aut_edges_s20_3000 | 102 | 96 | 96 | 60024 | 48.955 | 3.610 | 48.946 | 0.6632 | 0.111 |
| reg60_frozen_1000 | 60 | 60 | 60 | 57166 | 16.782 | 0.440 | 16.771 | 0.3330 | 0.134 |
| reg60_aut_edges_s20_1000 | 60 | 60 | 60 | 3996 | 1.538 | 0.063 | 1.538 | 0.3173 | 0.112 |
| reg60_incumbent_1000 | 60 | 60 | 60 | 3996 | 1.659 | 0.057 | 1.659 | 0.3513 | 0.132 |
| reg60_frozen_reallocated_1000 | 60 | 60 | 60 | 4846 | 1.493 | 0.056 | 1.490 | 0.3344 | 0.116 |

## 6. Path statistics for the 98 rows `frozen` solves at budget 10000

For every dev row solved by `frozen` at budget 10000: charged nodes, number of mixed-path steps stored in the certificate (substitution + automorphism), the maximum total relator length (`len(r1)+len(r2)`) seen anywhere on the stored path, the minimum total length seen on the path *before* the terminal state (the terminal itself is a length-2 basis by construction, so it is excluded to make this number informative), and how many of the mixed steps are ambient-automorphism (`kind: automorphism`) steps rather than ordinary relator substitutions.

- nodes_explored: min 1002, median 1106.5, max 3851, mean 1344.0
- mixed steps: min 13, median 30.0, max 256, mean 34.8
- max total length on path: min 18, median 24.5, max 255, mean 28.1
- min total length before terminal: min 3, median 3.0, max 16, mean 3.6
- automorphism steps: min 0, median 8.0, max 21, mean 8.3 (93/98 rows use at least one automorphism step)

<details><summary>Full per-row table (98 rows)</summary>

| name | nodes_explored | mixed steps | max total length | min total length before terminal | automorphism steps |
|---|---:|---:|---:|---:|---:|
| ac19_102 | 1488 | 37 | 26 | 14 | 0 |
| ac19_10820 | 1043 | 28 | 26 | 3 | 6 |
| ac19_109 | 1379 | 256 | 255 | 3 | 0 |
| ac19_11261 | 1533 | 32 | 25 | 3 | 13 |
| ac19_12112 | 1039 | 31 | 25 | 3 | 11 |
| ac19_14165 | 1132 | 24 | 21 | 3 | 6 |
| ac19_15047 | 1058 | 27 | 21 | 3 | 7 |
| ac19_16098 | 1299 | 34 | 22 | 3 | 9 |
| ac19_16343 | 1717 | 28 | 21 | 3 | 7 |
| ac19_18413 | 2347 | 61 | 31 | 3 | 21 |
| ac19_18516 | 1025 | 26 | 25 | 3 | 9 |
| ac19_1880 | 1329 | 36 | 24 | 3 | 12 |
| ac19_19132 | 1051 | 21 | 21 | 3 | 5 |
| ac19_20055 | 3064 | 66 | 34 | 14 | 0 |
| ac19_20074 | 2162 | 29 | 23 | 3 | 7 |
| ac19_20172 | 1089 | 30 | 20 | 3 | 7 |
| ac19_22112 | 1014 | 21 | 21 | 3 | 4 |
| ac19_22628 | 1578 | 36 | 33 | 3 | 7 |
| ac19_230 | 1037 | 28 | 22 | 3 | 12 |
| ac19_2376 | 1036 | 29 | 22 | 3 | 8 |
| ac19_25075 | 1180 | 25 | 22 | 3 | 9 |
| ac19_26598 | 2349 | 56 | 31 | 3 | 19 |
| ac19_27787 | 1006 | 78 | 65 | 3 | 7 |
| ac19_28253 | 1578 | 35 | 33 | 3 | 7 |
| ac19_28281 | 1148 | 39 | 24 | 3 | 8 |
| ac19_28696 | 1131 | 34 | 28 | 10 | 0 |
| ac19_28930 | 1022 | 29 | 27 | 3 | 10 |
| ac19_30433 | 3434 | 51 | 29 | 3 | 15 |
| ac19_30535 | 1035 | 28 | 21 | 3 | 7 |
| ac19_31106 | 2382 | 41 | 26 | 3 | 12 |
| ac19_3175 | 1036 | 25 | 22 | 3 | 6 |
| ac19_31971 | 1307 | 32 | 26 | 3 | 6 |
| ac19_32128 | 1067 | 25 | 19 | 3 | 8 |
| ac19_32315 | 1301 | 27 | 30 | 3 | 7 |
| ac19_35248 | 1309 | 30 | 22 | 3 | 7 |
| ac19_35367 | 1043 | 35 | 25 | 3 | 12 |
| ac19_3566 | 1169 | 27 | 25 | 3 | 5 |
| ac19_36375 | 1051 | 33 | 23 | 3 | 10 |
| ac19_37610 | 1075 | 31 | 24 | 3 | 9 |
| ac19_37661 | 1009 | 21 | 21 | 3 | 4 |
| ac19_3794 | 1101 | 22 | 28 | 13 | 6 |
| ac19_38100 | 1494 | 34 | 26 | 3 | 7 |
| ac19_41092 | 1046 | 26 | 24 | 3 | 8 |
| ac19_41186 | 1112 | 33 | 27 | 3 | 7 |
| ac19_41336 | 1051 | 32 | 24 | 3 | 10 |
| ac19_41890 | 1081 | 24 | 29 | 3 | 5 |
| ac19_43158 | 1072 | 24 | 19 | 3 | 7 |
| ac19_45464 | 1121 | 31 | 23 | 3 | 10 |
| ac19_45684 | 3639 | 44 | 38 | 3 | 7 |
| ac19_45920 | 1038 | 26 | 23 | 3 | 8 |
| ac19_46302 | 1075 | 24 | 19 | 3 | 8 |
| ac19_46402 | 1034 | 25 | 22 | 3 | 7 |
| ac19_46649 | 1072 | 30 | 20 | 3 | 7 |
| ac19_46703 | 1584 | 38 | 25 | 3 | 12 |
| ac19_46895 | 1035 | 22 | 21 | 3 | 4 |
| ac19_47160 | 1077 | 31 | 23 | 3 | 10 |
| ac19_47367 | 1016 | 24 | 25 | 3 | 9 |
| ac19_47717 | 1041 | 27 | 28 | 3 | 10 |
| ac19_47899 | 1071 | 32 | 26 | 3 | 8 |
| ac19_48114 | 1087 | 24 | 19 | 3 | 7 |
| ac19_48604 | 1044 | 74 | 63 | 3 | 7 |
| ac19_4894 | 1071 | 23 | 19 | 3 | 7 |
| ac19_49255 | 2346 | 59 | 31 | 3 | 20 |
| ac19_49785 | 1048 | 27 | 22 | 3 | 8 |
| ac19_50043 | 1364 | 37 | 26 | 3 | 12 |
| ac19_50491 | 1075 | 23 | 19 | 3 | 6 |
| ac19_50926 | 1291 | 36 | 31 | 3 | 12 |
| ac19_51462 | 1084 | 49 | 31 | 11 | 0 |
| ac19_5250 | 1309 | 30 | 22 | 3 | 9 |
| ac19_53119 | 1022 | 29 | 27 | 3 | 9 |
| ac19_54243 | 1035 | 23 | 23 | 3 | 5 |
| ac19_5478 | 1112 | 33 | 27 | 3 | 7 |
| ac19_5652 | 1051 | 25 | 22 | 3 | 8 |
| ac19_56843 | 1303 | 27 | 30 | 3 | 7 |
| ac19_58416 | 1068 | 22 | 18 | 3 | 7 |
| ac19_59576 | 1205 | 32 | 23 | 3 | 10 |
| ac19_60157 | 1189 | 32 | 22 | 3 | 12 |
| ac19_60781 | 3851 | 43 | 29 | 3 | 9 |
| ac19_63094 | 2278 | 32 | 23 | 3 | 9 |
| ac19_64188 | 1212 | 35 | 33 | 3 | 2 |
| ac19_64447 | 1075 | 24 | 19 | 3 | 8 |
| ac19_65140 | 1206 | 45 | 35 | 3 | 5 |
| ac19_65325 | 1363 | 50 | 35 | 3 | 13 |
| ac19_65754 | 1190 | 34 | 23 | 3 | 12 |
| ac19_66662 | 1133 | 27 | 24 | 3 | 9 |
| ac19_6678 | 1083 | 32 | 24 | 3 | 10 |
| ac19_67055 | 1199 | 31 | 27 | 3 | 13 |
| ac19_67450 | 1059 | 35 | 23 | 3 | 10 |
| ac19_67699 | 2278 | 32 | 23 | 3 | 9 |
| ac19_68563 | 1059 | 31 | 22 | 3 | 8 |
| ac19_69707 | 1026 | 24 | 24 | 3 | 11 |
| ac19_7037 | 1506 | 28 | 25 | 3 | 10 |
| ac19_70762 | 1027 | 13 | 29 | 16 | 4 |
| ac19_70826 | 1448 | 48 | 28 | 3 | 14 |
| ac19_70877 | 1002 | 22 | 28 | 3 | 6 |
| ac19_72274 | 1515 | 30 | 25 | 3 | 12 |
| ac19_8222 | 1518 | 29 | 25 | 3 | 11 |
| ac19_8984 | 1164 | 27 | 25 | 3 | 5 |

</details>

## 7. compare.py runs

- `research/residual_20260909/screens/compare_dev_1000.json` -- all 7 dev budget-1000 policies, pairwise (21 pairs): gained/lost names, McNemar discordant counts + continuity-corrected chi-square and p-value, mean elementary count and mean nodes delta on common solved+verified rows.
- `research/residual_20260909/screens/compare_reg60_1000.json` -- `frozen`, `aut_edges_s20`, `incumbent`, `frozen_reallocated` on regression60 (6 pairs): all six pairs show 0 gained / 0 lost -- every policy solves the same 60/60 rows, with `frozen` costing markedly more nodes per row (mean nodes delta vs frozen: aut_edges_s20 -886.2, incumbent -886.2, frozen_reallocated -872.0) because it pays the donor/plain charges before the incumbent stage even starts.

Headline pairwise result on dev (budget 1000, from `compare_dev_1000.json`): every routed or single-arm alternative (`incumbent`, `aut_edges_s20`, `ordinary_T`, `frozen_reallocated`) strictly dominates `frozen` on this panel at equal budget -- 0 rows lost, 50-87 rows gained, McNemar p well below 1e-7 in every case. This is a budget-allocation artifact of `frozen`s fixed 250/872/remainder split, not evidence these arms out-search the routed incumbent in general (see the reg60 table above, where the routed incumbent alone matches `frozen` exactly once it is not competing with donor/plain for shared budget).

