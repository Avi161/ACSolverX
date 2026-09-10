# Reference runs on `ladder_200`

Every run here was produced by `run_ladder.py` on this box (4 cores, 15 GB), every
solve replayed independently, zero errors. `report_200_reference/REPORT.md` is the
per-level report over all of them (`report_ladder.py`), with the anytime curves and
the pairwise McNemar tables.

| file | engine | budget | cap | workers | solved / 200 | run wall |
|---|---|---:|---:|---:|---:|---:|
| `ladder_200_greedy_b10000_c48.jsonl` | plain greedy | 10,000 pops | 48 | 2 | **40** | 115 s |
| `ladder_200_greedy_b100000_c48.jsonl` | plain greedy | 100,000 pops | 48 | 2 | **80** | 1,217 s |
| `ladder_200_s20_mk2_b10000_c48.jsonl` | S20_MK2 | 10,000 pops | 48 | 2 | **118** | 101 s |
| `ladder_200_s20_mk2_b100000_c48.jsonl` | S20_MK2 | 100,000 pops | 48 | 2 | **156** | 765 s |
| `ladder_200_K3p_notable_b1000.jsonl` | `K3p_notable` (table-free cascade) | 1,000 units | – | 2 | **158** | 35 s |
| `ladder_200_K3p_c14aut_b1000.jsonl` | `K3p_c14aut` (cap-14 table) | 1,000 units | – | 2 | **180** | 15 s |
| `ladder_200_frozen_b1000.jsonl` | `frozen` (table-free) | 1,000 units | – | 1 | **92** | 65 s |
| `ladder_200_frozen_reallocated_b1000.jsonl` | `frozen_reallocated` (table-free) | 1,000 units | – | 1 | **159** | 67 s |
| `ladder_200_incumbent_b1000.jsonl` | `incumbent` (table-free) | 1,000 units | – | 1 | **154** | 73 s |
| `ladder_200_plain_s20_b1000.jsonl` | `plain_s20` (S20_MK2 as a policy) | 1,000 units | – | 1 | **44** | 65 s |
| `ladder_200_aut_edges_s20_b1000.jsonl` | `aut_edges_s20` (table-free) | 1,000 units | – | 1 | **172** | 59 s |
| `ladder_200_ordinary_T_b1000.jsonl` | `ordinary_T` (table-free) | 1,000 units | – | 1 | **81** | 128 s |
| `ladder_200_donor_only_b1000.jsonl` | `donor_only` (table-free) | 1,000 units | – | 1 | **32** | 2 s |

Per level (solved of 20):

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
| 9 | 0 | 0 | 6 | 8 | 13 | 20 | 0 | 19 | 19 | 0 | 19 | 0 | 0 |
| 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **all** | **40** | **80** | **118** | **156** | **158** | **180** | **92** | **159** | **154** | **44** | **172** | **81** | **32** |

The anytime curves (one run read at smaller budgets): greedy solves 11 / 21 / 40 / 80
of the 200 at 100 / 1k / 10k / 100k pops; S20_MK2 11 / 44 / 118 / 156.

How to read it:

- **greedy @10k = levels 1–2 and greedy @100k = levels 1–4, exactly.** That is the
  sanity check of the grading, not a result: levels are bands of the plain greedy
  node count, so greedy at budget B solves precisely the rows graded below B (the
  100k run disagrees with the recorded grade on 0 of 200 rows).
- **S20_MK2's gains are spread over levels 3–9.** At 10k it already takes 6 of the 20
  level-9 rows — orbits plain greedy cannot solve at 10,000,000 pops — all six in
  4,900–6,100 pops; at 100k it holds levels 1–6 entirely and 14 / 14 / 8 of levels
  7 / 8 / 9. The ordering is worth more than three decades of budget there.
- **Units are not comparable across the two engine kinds.** Pops are pops; the
  cascades' 1,000 "units" charge macros and, under `K3p_c14aut`, count a table
  lookup as free (66,151 of the 72,779 census orbits resolve at 0 units). The table
  policy clearing levels 1–9 says the cap-14 ball reaches all of them, not that they
  are cheap.
- `K3p_notable` misses 3 rows at level 2 (rows greedy solves in a few thousand pops):
  the frozen 250 / 300 / rest split starves them at 1,000 units.
- The seven other policies are the table-free arms of `research/residual_20260909`
  (`policies.REGISTRY`), run so the ladder shows where each one stands: `frozen`
  (the frozen 250 / 300 / rest split) takes 0 of level 9, `frozen_reallocated` and
  `incumbent` 19 of 20, and `aut_edges_s20` — the strongest table-free arm here — 172
  of 200. `plain_s20` is S20_MK2 charged as a policy, so at 1,000 units it is the S20
  anytime curve read at 1k (44). `donor_only` and `ordinary_T` are single stages, not
  contenders.
- Level 10 is 0 for everything, as it should be.
- The summaries record the sha256 of `ladder_200.csv` as it was when they ran; the
  file was rebuilt afterwards with the S20 grading of the originals and MS-640 rows
  filled in (`s20_*` columns), which changes the hash but not one row name, word or
  level — `tests/test_ladder.py` and the greedy/S20 record checks in `LADDER.md` pin
  that.

Commands (from the repository root, `PYTHONPATH=.`):

```bash
python3 -m benchmark.ladder.run_ladder --subset 200 --engine greedy  --budget 10000  --cap 48 --workers 2
python3 -m benchmark.ladder.run_ladder --subset 200 --engine greedy  --budget 100000 --cap 48 --workers 2
python3 -m benchmark.ladder.run_ladder --subset 200 --engine s20_mk2 --budget 10000  --cap 48 --workers 2
python3 -m benchmark.ladder.run_ladder --subset 200 --engine s20_mk2 --budget 100000 --cap 48 --workers 2
python3 -m benchmark.ladder.run_ladder --subset 200 --engine policy --policy K3p_notable --budget 1000 --workers 2
python3 -m benchmark.ladder.run_ladder --subset 200 --engine policy --policy K3p_c14aut  --budget 1000 --workers 2
for p in frozen frozen_reallocated incumbent plain_s20 aut_edges_s20 ordinary_T donor_only; do
    python3 -m benchmark.ladder.run_ladder --subset 200 --engine policy --policy $p --budget 1000 --workers 1
done
python3 -m benchmark.ladder.report_ladder --out benchmark/ladder/runs/report_200_reference \
    --runs greedy10k=benchmark/ladder/runs/ladder_200_greedy_b10000_c48.jsonl \
           greedy100k=benchmark/ladder/runs/ladder_200_greedy_b100000_c48.jsonl \
           s20mk2_10k=benchmark/ladder/runs/ladder_200_s20_mk2_b10000_c48.jsonl \
           s20mk2_100k=benchmark/ladder/runs/ladder_200_s20_mk2_b100000_c48.jsonl \
           K3p_notable_1k=benchmark/ladder/runs/ladder_200_K3p_notable_b1000.jsonl \
           K3p_c14aut_1k=benchmark/ladder/runs/ladder_200_K3p_c14aut_b1000.jsonl
```

## The same runs on `ladder_200_s20hard`

The S20-hard family keeps, per level, the rows S20_MK2 finds hardest (`LADDER.md`).
Same commands with `--panel benchmark/ladder/ladder_200_s20hard.csv`; the report is
`report_200_s20hard_reference/REPORT.md`.

| file | engine | budget | cap | workers | solved / 200 | run wall |
|---|---|---:|---:|---:|---:|---:|
| `ladder_200_s20hard_greedy_b10000_c48.jsonl` | plain greedy | 10,000 pops | 48 | 2 | **40** | 129 s |
| `ladder_200_s20hard_greedy_b100000_c48.jsonl` | plain greedy | 100,000 pops | 48 | 2 | **80** | 1,330 s |
| `ladder_200_s20hard_s20_mk2_b10000_c48.jsonl` | S20_MK2 | 10,000 pops | 48 | 2 | **34** | 166 s |
| `ladder_200_s20hard_s20_mk2_b100000_c48.jsonl` | S20_MK2 | 100,000 pops | 48 | 2 | **141** | 1,158 s |
| `ladder_200_s20hard_K3p_notable_b1000.jsonl` | `K3p_notable` | 1,000 units | – | 1 | **162** | 61 s |
| `ladder_200_s20hard_K3p_c14aut_b1000.jsonl` | `K3p_c14aut` | 1,000 units | – | 1 | **180** | 28 s |
| `ladder_200_s20hard_frozen_b1000.jsonl` | `frozen` | 1,000 units | – | 1 | **90** | 67 s |
| `ladder_200_s20hard_frozen_reallocated_b1000.jsonl` | `frozen_reallocated` | 1,000 units | – | 1 | **161** | 61 s |
| `ladder_200_s20hard_incumbent_b1000.jsonl` | `incumbent` | 1,000 units | – | 1 | **161** | 67 s |
| `ladder_200_s20hard_plain_s20_b1000.jsonl` | `plain_s20` | 1,000 units | – | 1 | **0** | 75 s |
| `ladder_200_s20hard_aut_edges_s20_b1000.jsonl` | `aut_edges_s20` | 1,000 units | – | 1 | **170** | 58 s |
| `ladder_200_s20hard_ordinary_T_b1000.jsonl` | `ordinary_T` | 1,000 units | – | 1 | **53** | 154 s |
| `ladder_200_s20hard_donor_only_b1000.jsonl` | `donor_only` | 1,000 units | – | 1 | **52** | 3 s |

Per level (solved of 20):

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
| 9 | 0 | 0 | 0 | 0 | 17 | 20 | 0 | 18 | 18 | 0 | 18 | 0 | 0 |
| 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **all** | **40** | **80** | **34** | **141** | **162** | **180** | **90** | **161** | **161** | **0** | **170** | **53** | **52** |

- Greedy again solves exactly levels 1–2 at 10k and 1–4 at 100k (the levels are
  still greedy bands), and the 100k runs reproduce every recorded `greedy_nodes` and
  `s20_nodes` on these rows exactly.
- **S20_MK2 drops from 118 to 34 at 10k and from 156 to 141 at 100k**; the anytime
  curve at 100 / 1k / 10k / 100k pops is 0 / 0 / 34 / 141 against
  0 / 20 / 40 / 80 for greedy. At 10k it holds only level 1 (picks of 3k–7.7k pops), takes 12 of
  level 6 and 2 of level 7, and nothing else — that is what the selection is for.
- `plain_s20` at 1,000 units solves nothing: the cheapest level-1 pick needs 3,116
  pops. The cascades barely move (`K3p_c14aut` 180 → 180, `aut_edges_s20` 172 → 170,
  `K3p_notable` 158 → 162), so S20-hardness is not cascade-hardness: their automorphism
  and macro stages route around the ordering's bad starts.
