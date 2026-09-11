# Reference runs on `ladder_200` and `ladder_200_s20hard`

Every run here was produced by `run_ladder.py` on this box (4 cores, 15 GB), every
solve replayed independently, zero errors. Both panels have **188 rows** (20 per level
for levels 1–8, then all 19 of level 9 and all 9 of level 10; see `LADDER.md`).
`report_200_reference/REPORT.md` and `report_200_s20hard_reference/REPORT.md` are the
per-level reports (`report_ladder.py`), with the anytime curves and the pairwise
McNemar tables.

The runs were first made on the 2026-09-10 panels (200 rows, with 20 unsolved MS classes
at level 10) and **resumed** on the 2026-09-11 panels: the 180 rows common to both kept
their records, the 8 new level-9/10 rows per panel were run fresh, and every summary was
recomputed from the full 188 records. The summaries' `run_wall` therefore covers only the
resumed rows; the original full-panel walls were 115 / 1,217 / 101 / 765 s for greedy
@10k / @100k and S20_MK2 @10k / @100k on the spread panel, 129 / 1,330 / 166 / 1,158 s on
the S20-hard one, and 2–155 s per policy.

## `ladder_200` (the spread family)

| file | engine | budget | cap | workers | solved / 188 |
|---|---|---:|---:|---:|---:|
| `ladder_200_greedy_b10000_c48.jsonl` | plain greedy | 10,000 pops | 48 | 2 | **40** |
| `ladder_200_greedy_b100000_c48.jsonl` | plain greedy | 100,000 pops | 48 | 2 | **80** |
| `ladder_200_s20_mk2_b10000_c48.jsonl` | S20_MK2 | 10,000 pops | 48 | 2 | **118** |
| `ladder_200_s20_mk2_b100000_c48.jsonl` | S20_MK2 | 100,000 pops | 48 | 2 | **156** |
| `ladder_200_K3p_notable_b1000.jsonl` | `K3p_notable` | 1,000 units | – | 1 | **164** |
| `ladder_200_K3p_c14aut_b1000.jsonl` | `K3p_c14aut` | 1,000 units | – | 1 | **188** |
| `ladder_200_frozen_b1000.jsonl` | `frozen` | 1,000 units | – | 1 | **92** |
| `ladder_200_frozen_reallocated_b1000.jsonl` | `frozen_reallocated` | 1,000 units | – | 1 | **166** |
| `ladder_200_incumbent_b1000.jsonl` | `incumbent` | 1,000 units | – | 1 | **161** |
| `ladder_200_plain_s20_b1000.jsonl` | `plain_s20` | 1,000 units | – | 1 | **44** |
| `ladder_200_aut_edges_s20_b1000.jsonl` | `aut_edges_s20` | 1,000 units | – | 1 | **179** |
| `ladder_200_ordinary_T_b1000.jsonl` | `ordinary_T` | 1,000 units | – | 1 | **81** |
| `ladder_200_donor_only_b1000.jsonl` | `donor_only` | 1,000 units | – | 1 | **32** |

Per level (solved of 20 for levels 1–8, of 19 at level 9, of 9 at level 10):

| level | greedy @10k | greedy @100k | S20_MK2 @10k | S20_MK2 @100k | `K3p_notable` @1k | `K3p_c14aut` @1k | `frozen` @1k | `frozen_reallocated` @1k | `incumbent` @1k | `plain_s20` @1k | `aut_edges_s20` @1k | `ordinary_T` @1k | `donor_only` @1k |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 8 |
| 2 | 20 | 20 | 20 | 20 | 17 | 20 | 13 | 17 | 16 | 10 | 18 | 11 | 5 |
| 3 | 0 | 20 | 13 | 20 | 16 | 20 | 3 | 14 | 13 | 1 | 19 | 9 | 6 |
| 4 | 0 | 20 | 16 | 20 | 17 | 20 | 8 | 16 | 13 | 3 | 19 | 4 | 6 |
| 5 | 0 | 0 | 12 | 20 | 20 | 20 | 14 | 16 | 16 | 7 | 20 | 10 | 6 |
| 6 | 0 | 0 | 18 | 20 | 19 | 20 | 10 | 20 | 20 | 3 | 20 | 13 | 0 |
| 7 | 0 | 0 | 7 | 14 | 18 | 20 | 11 | 19 | 19 | 0 | 19 | 9 | 1 |
| 8 | 0 | 0 | 6 | 14 | 18 | 20 | 13 | 18 | 18 | 0 | 18 | 5 | 0 |
| 9 | 0 | 0 | 6 | 8 | 12 | 19 | 0 | 19 | 19 | 0 | 19 | 0 | 0 |
| 10 | 0 | 0 | 0 | 0 | 7 | 9 | 0 | 7 | 7 | 0 | 7 | 0 | 0 |
| **all** | **40** | **80** | **118** | **156** | **164** | **188** | **92** | **166** | **161** | **44** | **179** | **81** | **32** |

The anytime curves (one run read at smaller budgets): greedy solves 11 / 21 / 40 / 80
of the 188 at 100 / 1k / 10k / 100k pops; S20_MK2 11 / 44 / 118 / 156.

How to read it:

- **greedy @10k = levels 1–2 and greedy @100k = levels 1–4, exactly.** That is the
  sanity check of the grading, not a result: levels are bands of the plain greedy
  node count, so greedy at budget B solves precisely the rows graded below B (the
  100k run disagrees with the recorded grade on 0 rows, and the S20_MK2 100k run
  reproduces every recorded `s20_nodes ≤ 100k`, 156/156).
- **S20_MK2's gains are spread over levels 3–9.** At 10k it already takes 6 of the 19
  level-9 rows — orbits plain greedy cannot solve at 10,000,000 pops — all six in
  4,900–6,100 pops; at 100k it holds levels 1–6 entirely and 14 / 14 / 8 of levels
  7 / 8 / 9. The ordering is worth more than three decades of budget there.
- **Level 10 is the nine rows S20_MK2 never solves**, so the pop engines score 0 there
  by construction; the cascades take 7 (table-free) and 9 (cap-14 table) of them.
- **Units are not comparable across the two engine kinds.** Pops are pops; the
  cascades' 1,000 "units" charge macros and, under `K3p_c14aut`, count a table
  lookup as free (66,151 of the 72,779 census orbits resolve at 0 units). The table
  policy clearing all 188 says the cap-14 ball reaches every ladder row, not that
  they are cheap.
- The seven other policies are the table-free arms of `research/residual_20260909`
  (`policies.REGISTRY`): `frozen` (the frozen 250 / 300 / rest split) takes 0 of
  levels 9–10, `frozen_reallocated` and `incumbent` 19 + 7, and `aut_edges_s20` — the
  strongest table-free arm here — 179 of 188. `plain_s20` is S20_MK2 charged as a
  policy, so at 1,000 units it is the S20 anytime curve read at 1k (44). `donor_only`
  and `ordinary_T` are single stages, not contenders.
- `K3p_notable` misses 3 rows at level 2 (rows greedy solves in a few thousand pops):
  the frozen 250 / 300 / rest split starves them at 1,000 units.

## `ladder_200_s20hard` (the S20-hard family)

The S20-hard family keeps, per level, the rows S20_MK2 finds hardest (`LADDER.md`);
levels 9 and 10 are the same 28 rows in both families, since the panel takes all of
them. Same commands with `--panel benchmark/ladder/ladder_200_s20hard.csv`.

| file | engine | budget | cap | workers | solved / 188 |
|---|---|---:|---:|---:|---:|
| `ladder_200_s20hard_greedy_b10000_c48.jsonl` | plain greedy | 10,000 pops | 48 | 2 | **40** |
| `ladder_200_s20hard_greedy_b100000_c48.jsonl` | plain greedy | 100,000 pops | 48 | 2 | **80** |
| `ladder_200_s20hard_s20_mk2_b10000_c48.jsonl` | S20_MK2 | 10,000 pops | 48 | 2 | **40** |
| `ladder_200_s20hard_s20_mk2_b100000_c48.jsonl` | S20_MK2 | 100,000 pops | 48 | 2 | **149** |
| `ladder_200_s20hard_K3p_notable_b1000.jsonl` | `K3p_notable` | 1,000 units | – | 1 | **164** |
| `ladder_200_s20hard_K3p_c14aut_b1000.jsonl` | `K3p_c14aut` | 1,000 units | – | 1 | **188** |
| `ladder_200_s20hard_frozen_b1000.jsonl` | `frozen` | 1,000 units | – | 1 | **90** |
| `ladder_200_s20hard_frozen_reallocated_b1000.jsonl` | `frozen_reallocated` | 1,000 units | – | 1 | **169** |
| `ladder_200_s20hard_incumbent_b1000.jsonl` | `incumbent` | 1,000 units | – | 1 | **169** |
| `ladder_200_s20hard_plain_s20_b1000.jsonl` | `plain_s20` | 1,000 units | – | 1 | **0** |
| `ladder_200_s20hard_aut_edges_s20_b1000.jsonl` | `aut_edges_s20` | 1,000 units | – | 1 | **178** |
| `ladder_200_s20hard_ordinary_T_b1000.jsonl` | `ordinary_T` | 1,000 units | – | 1 | **53** |
| `ladder_200_s20hard_donor_only_b1000.jsonl` | `donor_only` | 1,000 units | – | 1 | **52** |

Per level:

| level | greedy @10k | greedy @100k | S20_MK2 @10k | S20_MK2 @100k | `K3p_notable` @1k | `K3p_c14aut` @1k | `frozen` @1k | `frozen_reallocated` @1k | `incumbent` @1k | `plain_s20` @1k | `aut_edges_s20` @1k | `ordinary_T` @1k | `donor_only` @1k |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 20 | 20 | 20 | 20 | 17 | 20 | 11 | 20 | 20 | 0 | 20 | 10 | 8 |
| 2 | 20 | 20 | 0 | 20 | 20 | 20 | 17 | 20 | 20 | 0 | 20 | 20 | 8 |
| 3 | 0 | 20 | 0 | 20 | 20 | 20 | 12 | 17 | 17 | 0 | 20 | 3 | 13 |
| 4 | 0 | 20 | 0 | 20 | 16 | 20 | 12 | 18 | 18 | 0 | 20 | 10 | 10 |
| 5 | 0 | 0 | 0 | 20 | 19 | 20 | 13 | 15 | 15 | 0 | 19 | 0 | 12 |
| 6 | 0 | 0 | 12 | 20 | 20 | 20 | 8 | 20 | 20 | 0 | 20 | 6 | 0 |
| 7 | 0 | 0 | 2 | 12 | 19 | 20 | 7 | 19 | 19 | 0 | 19 | 4 | 1 |
| 8 | 0 | 0 | 0 | 9 | 14 | 20 | 10 | 14 | 14 | 0 | 14 | 0 | 0 |
| 9 | 0 | 0 | 6 | 8 | 12 | 19 | 0 | 19 | 19 | 0 | 19 | 0 | 0 |
| 10 | 0 | 0 | 0 | 0 | 7 | 9 | 0 | 7 | 7 | 0 | 7 | 0 | 0 |
| **all** | **40** | **80** | **40** | **149** | **164** | **188** | **90** | **169** | **169** | **0** | **178** | **53** | **52** |

- Greedy again solves exactly levels 1–2 at 10k and 1–4 at 100k (the levels are
  still greedy bands), and the 100k runs reproduce every recorded `greedy_nodes` and
  `s20_nodes` on these rows exactly (149/149 for S20_MK2).
- **S20_MK2 drops from 118 to 40 at 10k and from 156 to 149 at 100k**; the anytime
  curve at 100 / 1k / 10k / 100k pops is 0 / 0 / 40 / 149 against 0 / 20 / 40 / 80 for
  greedy. At 10k it holds only level 1 (picks of 3k–7.7k pops), takes 12 of level 6,
  2 of level 7 and the same 6 of level 9, and nothing else — that is what the
  selection is for.
- `plain_s20` at 1,000 units solves nothing: the cheapest level-1 pick needs 3,116
  pops. The cascades barely move (`K3p_c14aut` 188 → 188, `aut_edges_s20` 179 → 178,
  `K3p_notable` 164 → 164), so S20-hardness is not cascade-hardness: their
  automorphism and macro stages route around the ordering's bad starts.

## Commands (from the repository root, `PYTHONPATH=.`)

```bash
for fam in "--subset 200" "--panel benchmark/ladder/ladder_200_s20hard.csv"; do
    python3 -m benchmark.ladder.run_ladder $fam --engine greedy  --budget 10000  --cap 48 --workers 2
    python3 -m benchmark.ladder.run_ladder $fam --engine greedy  --budget 100000 --cap 48 --workers 2
    python3 -m benchmark.ladder.run_ladder $fam --engine s20_mk2 --budget 10000  --cap 48 --workers 2
    python3 -m benchmark.ladder.run_ladder $fam --engine s20_mk2 --budget 100000 --cap 48 --workers 2
    for p in K3p_notable K3p_c14aut frozen frozen_reallocated incumbent plain_s20 aut_edges_s20 ordinary_T donor_only; do
        python3 -m benchmark.ladder.run_ladder $fam --engine policy --policy $p --budget 1000 --workers 1
    done
done
python3 -m benchmark.ladder.report_ladder --out benchmark/ladder/runs/report_200_reference \
    --runs greedy10k=benchmark/ladder/runs/ladder_200_greedy_b10000_c48.jsonl \
           greedy100k=benchmark/ladder/runs/ladder_200_greedy_b100000_c48.jsonl \
           s20mk2_10k=benchmark/ladder/runs/ladder_200_s20_mk2_b10000_c48.jsonl \
           s20mk2_100k=benchmark/ladder/runs/ladder_200_s20_mk2_b100000_c48.jsonl \
           K3p_notable_1k=benchmark/ladder/runs/ladder_200_K3p_notable_b1000.jsonl \
           K3p_c14aut_1k=benchmark/ladder/runs/ladder_200_K3p_c14aut_b1000.jsonl
# same with the ladder_200_s20hard_* files and --out .../report_200_s20hard_reference
```
