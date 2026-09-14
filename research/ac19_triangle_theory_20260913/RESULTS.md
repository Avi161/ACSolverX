# Does retained-rank triangular expansion make hard AC19 rows easier? No — and here is the mechanism

Frozen inputs: the four hard-but-solved AC19 rows of
`research/ac19_triangle_expansion_20260912/hard_solved_panel.jsonl` (each exhausted
plain greedy at 100,000 nodes; saved certificates need 1.5–8.2 M greedy nodes or
17,369–37,682 `S20_MK2` nodes at rank two) and its twelve easy controls.
Preprocessing: `triangulate` (greedy digram compression) to rank 7–9 with every
relator of length at most three; counted, never a solve. Search: rank-preserving
ordinary AC normal-product substitutions only, relator caps [4, 5, 6], 60 heap pops,
beam 48, two orderings — the incumbent `structural` score and the `coupling`
score of `THEORY.md`. A run *exposes* structure when it reaches a relator of length
two (B) or one (U) at unchanged rank. Every path below was replayed independently
(`verify.py`), and the tables are generated from the JSON records (`make_results.py`).

## Headline

* **Hard panel: 0 of 4 rows expose a bigon or a unit** under either ordering at any
  cap. All four roots are all-triangle and digram-disjoint, so by Lemma 2 no single
  substitution can make a length-two relator and by Lemma 1 none can make a unit;
  Corollary 3 puts a bigon at least three moves away at cap 4. The searches explored
  well past that depth and still found nothing.
* **Easy controls: 6 of 12 expose a unit** (6 a bigon). Of the ten
  all-triangle easy roots, 4 expose a unit by search; the two roots that already
  carry a length-two relator after preprocessing (ac19_45, ac19_46) are credited to
  preprocessing, not search. The two sharing roots (`ac19_44`, `ac19_48`) expose a
  bigon in a single pop, exactly as Lemma 2 predicts.
* **Census:** of 400 random AC19 rows, 255 triangulate to an all-triangle root and
  **all 255 of those are digram-disjoint**; the remaining 145 already contain a
  relator of length at most two straight out of preprocessing.
* **Work:** 829 preprocessing units, 5,760 pops, 6,095,052 rotation products,
  598 CPU-seconds across all arms. None of it moved a hard row.

So the answer to the question this directory was opened for is **no**: making
every relator length three does not make the hard rows easier at fixed rank.
The lift study (`../ac19_triangle_expansion_20260912/lift/`) already showed the
known rank-two certificates cannot be shadowed at fixed rank; this study shows
the fixed-rank search cannot even take a first useful step from these roots,
and says exactly why.

## What the theory adds

* **Lemma 1 (parity).** Triangle x triangle is even, quartic x triangle is odd.
  A triangulated root has *no* odd-length one-move child, which is why the
  frozen engine's cap-3 neighbourhood is empty.
* **Lemma 2 (bigon necessity).** A one-move bigon needs two relators sharing a
  cyclic digram modulo `(u,v) -> (v^-1,u^-1)`. Machine-checked: 0 violations in
  11,774 + 4,077 random balanced all-triangle states; the only sharing states
  without a bigon have two equal relators.
* **Corollary 3.** From a digram-disjoint root at cap 4: no bigon in fewer than
  three moves, no unit in fewer than two.
* **Coupling ordering.** Rank by `(no unit, no bigon, -shared pairs, -shared
  digrams, length, ...)`. It is a real gradient where total length is flat
  (`3r` at every all-triangle state, `3r+1` at every cap-4 child). On the
  sharing controls it finds a bigon in one pop. On the digram-disjoint easy
  roots it is not uniformly better than the incumbent at this budget (see the
  per-arm table: each ordering wins some rows), and on the hard roots neither
  ordering finds anything.

## Per-row arms

Cells read `mark (pops/rotation products)`: `U` unit exposed, `B` bigon only, `.` nothing.

| row | panel | rank-2 L | rank | defs | prep units | root min relator | root disjoint | coupling@4 | structural@4 | coupling@5 | structural@5 | coupling@6 | structural@6 |
|---|---|---:|---:|---:|---:|---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| ac19_15866 | hard | 17 | 8 | 6 | 74 | 3 | yes | . (60p/92,644rp) | . (60p/66,404rp) | . (60p/147,200rp) | . (60p/66,404rp) | . (60p/194,512rp) | . (60p/66,404rp) |
| ac19_25244 | hard | 16 | 8 | 6 | 79 | 3 | yes | . (60p/91,880rp) | . (60p/66,404rp) | . (60p/136,484rp) | . (60p/66,404rp) | . (60p/200,620rp) | . (60p/66,404rp) |
| ac19_44158 | hard | 20 | 9 | 7 | 92 | 3 | yes | . (60p/121,228rp) | . (60p/84,524rp) | . (60p/169,180rp) | . (60p/84,524rp) | . (60p/261,744rp) | . (60p/84,524rp) |
| ac19_66724 | hard | 19 | 7 | 5 | 60 | 3 | yes | . (60p/70,244rp) | . (60p/51,052rp) | . (60p/96,516rp) | . (60p/51,052rp) | . (60p/150,416rp) | . (60p/51,052rp) |
| ac19_41 | easy | 13 | 6 | 4 | 45 | 3 | yes | . (60p/49,996rp) | . (60p/35,760rp) | . (60p/74,820rp) | . (60p/35,760rp) | . (60p/107,724rp) | . (60p/35,760rp) |
| ac19_42 | easy | 13 | 6 | 4 | 45 | 3 | yes | . (60p/50,228rp) | . (60p/35,760rp) | . (60p/77,252rp) | . (60p/35,760rp) | . (60p/108,144rp) | . (60p/35,760rp) |
| ac19_43 | easy | 13 | 5 | 3 | 32 | 3 | yes | U (60p/23,416rp) | U (60p/5,804rp) | . (60p/50,896rp) | U (60p/5,804rp) | . (60p/75,148rp) | U (60p/5,804rp) |
| ac19_44 | easy | 13 | 5 | 3 | 31 | 3 | no | U (60p/18,316rp) | U (60p/4,688rp) | U (60p/26,196rp) | U (60p/4,688rp) | U (60p/35,716rp) | U (60p/4,688rp) |
| ac19_45 | easy | 14 | 6 | 4 | 43 | 2 | yes | U (60p/37,516rp) | B (60p/30,776rp) | B (60p/69,680rp) | B (60p/30,776rp) | B (60p/89,320rp) | B (60p/30,776rp) |
| ac19_46 | easy | 14 | 6 | 4 | 43 | 2 | yes | B (60p/43,040rp) | U (60p/7,532rp) | B (60p/68,800rp) | U (60p/7,532rp) | B (60p/85,032rp) | U (60p/7,532rp) |
| ac19_47 | easy | 14 | 5 | 3 | 32 | 3 | yes | . (60p/33,820rp) | . (60p/24,384rp) | U (60p/39,912rp) | . (60p/24,384rp) | . (60p/73,320rp) | . (60p/24,384rp) |
| ac19_48 | easy | 14 | 5 | 3 | 31 | 3 | no | U (60p/21,020rp) | U (60p/5,172rp) | B (60p/42,368rp) | U (60p/5,172rp) | U (60p/38,784rp) | U (60p/5,172rp) |
| ac19_50 | easy | 14 | 6 | 4 | 45 | 3 | yes | . (60p/48,016rp) | . (60p/37,412rp) | . (60p/77,840rp) | . (60p/37,412rp) | . (60p/109,584rp) | . (60p/37,412rp) |
| ac19_51 | easy | 15 | 7 | 5 | 59 | 3 | yes | . (60p/71,252rp) | . (60p/50,748rp) | . (60p/102,264rp) | . (60p/50,748rp) | . (60p/147,668rp) | . (60p/50,748rp) |
| ac19_52 | easy | 15 | 7 | 5 | 59 | 3 | yes | . (60p/66,548rp) | . (60p/49,392rp) | . (60p/107,436rp) | . (60p/49,392rp) | . (60p/149,520rp) | . (60p/49,392rp) |
| ac19_54 | easy | 15 | 7 | 5 | 59 | 3 | yes | . (60p/68,448rp) | . (60p/49,104rp) | . (60p/101,996rp) | . (60p/49,104rp) | . (60p/156,600rp) | . (60p/49,104rp) |

| cap | ordering | panel | rows | bigon exposed | unit exposed | pops | rotation products | states | CPU s |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|
| 4 | coupling | easy | 10 | 3 | 3 | 600 | 451,060 | 9,945 | 9.9 |
| 4 | coupling | easy (short root) | 2 | 2 | 1 | 120 | 80,556 | 2,974 | 2.7 |
| 4 | coupling | hard | 4 | 0 | 0 | 240 | 375,996 | 4,642 | 9.3 |
| 4 | structural | easy | 10 | 3 | 3 | 600 | 298,224 | 15,726 | 12.8 |
| 4 | structural | easy (short root) | 2 | 2 | 1 | 120 | 38,308 | 5,512 | 4.1 |
| 4 | structural | hard | 4 | 0 | 0 | 240 | 268,384 | 5,878 | 10.2 |
| 5 | coupling | easy | 10 | 3 | 2 | 600 | 700,980 | 12,088 | 14.8 |
| 5 | coupling | easy (short root) | 2 | 2 | 0 | 120 | 138,480 | 3,154 | 3.6 |
| 5 | coupling | hard | 4 | 0 | 0 | 240 | 549,380 | 6,677 | 14.4 |
| 5 | structural | easy | 10 | 3 | 3 | 600 | 298,224 | 22,407 | 18.4 |
| 5 | structural | easy (short root) | 2 | 2 | 1 | 120 | 38,308 | 9,202 | 6.8 |
| 5 | structural | hard | 4 | 0 | 0 | 240 | 268,384 | 9,968 | 16.2 |
| 6 | coupling | easy | 10 | 2 | 2 | 600 | 1,002,208 | 24,027 | 28.8 |
| 6 | coupling | easy (short root) | 2 | 2 | 0 | 120 | 174,352 | 4,531 | 5.2 |
| 6 | coupling | hard | 4 | 0 | 0 | 240 | 807,292 | 18,189 | 35.0 |
| 6 | structural | easy | 10 | 3 | 3 | 600 | 298,224 | 165,785 | 148.5 |
| 6 | structural | easy (short root) | 2 | 2 | 1 | 120 | 38,308 | 31,318 | 23.5 |
| 6 | structural | hard | 4 | 0 | 0 | 240 | 268,384 | 158,032 | 234.0 |

Note: the `structural` arm forms the same rotation products at every cap, because
its score ranks by maximum relator length and never pops a state containing a
relator longer than four within 60 pops; the `coupling` arm does climb into
longer relators.


## Can rank-raising separate solved-but-hard rows from U124? No

`separator_probe.py` pushes the 60-row solved MS benchmark ladder
(`benchmark/subsets/benchmark_subset_60.csv`, difficulty bins 0–9, 24 rows in
bins 6–9) and the 124 U124 representatives through the identical pipeline:
triangulate, static root features, coupling search at cap 5 with
30 pops and beam 32. AUC is the probability that a U124 row scores
above a solved row (0.5 = no separation).

| feature | AUC U124 vs solved bins 6–9 | AUC U124 vs all solved | mean U124 | mean solved 6–9 | mean all solved |
|---|---:|---:|---:|---:|---:|
| `rank2_length` | 0.114 | 0.450 | 19.00 | 23.04 | 19.32 |
| `rank` | 0.556 | 0.741 | 9.45 | 9.17 | 8.10 |
| `definitions` | 0.556 | 0.741 | 7.45 | 7.17 | 6.10 |
| `prep_units` | 0.560 | 0.758 | 105.50 | 99.54 | 79.37 |
| `root_min_relator` | 0.500 | 0.533 | 3.00 | 3.00 | 2.92 |
| `root_all_triangle` | 0.500 | 0.533 | 1.00 | 1.00 | 0.93 |
| `root_digram_disjoint` | 0.500 | 0.500 | 1.00 | 1.00 | 1.00 |
| `root_coupling_pairs` | 0.500 | 0.500 | 0.00 | 0.00 | 0.00 |
| `root_coupling_digrams` | 0.500 | 0.500 | 0.00 | 0.00 | 0.00 |
| `cap4_children` | 0.620 | 0.759 | 130.55 | 120.17 | 106.53 |
| `cap4_distinct_quartics` | 0.620 | 0.761 | 32.64 | 30.04 | 26.40 |
| `search_bigon` | 0.500 | 0.467 | 0.00 | 0.00 | 0.07 |
| `search_unit` | 0.500 | 0.492 | 0.00 | 0.00 | 0.02 |
| `search_best_coupling_pairs` | 0.490 | 0.666 | 32.60 | 32.62 | 26.15 |
| `search_states` | 0.608 | 0.707 | 1207.23 | 1097.75 | 936.63 |
| `search_pops` | 0.500 | 0.533 | 30.00 | 30.00 | 28.07 |
| `search_rotation_products` | 0.519 | 0.725 | 93780.35 | 89663.33 | 67738.27 |
| `search_shortest_relator` | 0.500 | 0.533 | 3.00 | 3.00 | 2.92 |

Every root feature is identical across the two groups: 124 of 124 U124 roots and
24 of 24 hard solved roots are all-triangle, digram-disjoint, with zero coupling and
no bigon or unit within the search. The only features with AUC away from 0.5
(`rank`, `cap4_children`, `search_states`) track total length, and on that axis
U124 is *shorter* than the hard solved rows (`rank2_length` AUC 0.114). Nothing
produced by raising rank distinguishes an unsolved row from a solved-but-hard one.
Wall time 574 s for all 184 rows.

## Honest limits

* Budgets are deliberately small (60 pops, beam 48); the earlier campaign
  already ran 1,000 pops at cap 6 (2.15 M states, 4.76 M rotation products) on
  the same hard roots with the same outcome. Nothing here is an obstruction to
  longer paths, to stable moves, or to AC-triviality.
* The census sample is 400 of 72,779 AC19 rows (seed 3).
* Lemma 2 is exact only for all-triangle states; roots with a shorter relator
  are reported separately and their exposure is credited to preprocessing.

## Reproduce

```sh
python3 run_panel.py --caps 4,5 --pops 60 --beam 48 --out bench_cap45_p60.json
python3 run_panel.py --caps 6   --pops 60 --beam 48 --out bench_cap6_p60.json
python3 census_digram_disjoint.py --out census_digram_disjoint_s3_n400.json
python3 verify.py bench_cap45_p60.json bench_cap6_p60.json
python3 -m pytest -q test_theory.py
python3 write_results.py bench_cap45_p60.json bench_cap6_p60.json census_digram_disjoint_s3_n400.json > RESULTS.md
```

