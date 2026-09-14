# Dynamic-rank AC search: results

Question: does re-expressing a presentation at higher rank with short relators,
and letting the rank move by "substitution moves", (a) solve presentations more
effectively, (b) separate the 124 unsolved representatives (U124) from solved
presentations, including the hard ones?  Method, moves and what a certificate
proves are in `README.md`; every number below comes from the JSONL records in
`records/` (rendered by `make_results.py` into `RESULTS_TABLES.md`), and every
solved certificate and shortening witness was replayed by the independent
`verify.py` (182 certificates, 13 witnesses, 0 failures).

## Headline

* **(a) Yes, but only when the dictionary is free to change.**  Same engine, same
  priority, same 2,000-pop budget on the 60-row solved ladder
  (`benchmark/subsets/benchmark_subset_60.csv`, difficulty bins 0–9):

  | arm | what | solved / 60 | bins 0–4 | bin 5 | bin 6 | bin 7 | bin 8 | bin 9 |
  |---|---|---:|---:|---:|---:|---:|---:|---:|
  | `ctrl` | rank two only (ordinary products, unit peeling) | **34** | 30/30 | 4/6 | 0/6 | 0/6 | 0/6 | 0/6 |
  | `tri` | all-triangle root (every relator ≤ 3), fixed dictionary, eliminate allowed | **25** | 25/30 | 0/6 | 0/6 | 0/6 | 0/6 | 0/6 |
  | `dyn_norelabel` | define + eliminate + products, no renaming canonicalisation | **39** | 29/30 | 2/6 | 2/6 | 4/6 | 0/6 | 2/6 |
  | `dyn` | define + eliminate + products (cap 8, ceiling L+8) | **42** | 30/30 | 2/6 | 3/6 | 5/6 | 0/6 | 2/6 |
  | `dyn_c10s12` | as `dyn` with cap 10, ceiling L+12 | **42** | 30/30 | 3/6 | 3/6 | 4/6 | 0/6 | 2/6 |

  Twelve rows in bins 5–9 are solved by `dyn` and by nothing at rank two at this
  budget (538, 606; 573, 602, 632; 568, 578, 583, 628, 633; 634, 635), among
  them two bin-9 rows for which plain greedy needs about 574,000 nodes: `dyn`
  solves 634 at pop 650 (73,388 states, a 69-step certificate: 20 definitions,
  22 eliminations, 27 products, rank never above 5) and 635 at pop 612.  Four
  bin-5 rows go the other way (543, 544, 549, 565: solved by `ctrl`, not by
  `dyn`).  On the 30 rows both arms solve, `dyn` needs fewer pops on 22 and
  fewer states on 23.  Bin 8 (six rows) resists every arm.

  Triangulating first and then searching with the dictionary frozen is *worse*
  than not triangulating at all (25 against 34), consistent with the
  fixed-rank negative results of `research/ac19_triangle_theory_20260913`.  The
  gain comes from definitions and eliminations interleaved with products, i.e.
  from changing the generating set along the way, not from short relators as
  such.

* **(b) A near-perfect empirical separator, hard rows included.**  Run the
  `dyn` arm for the same 2,000 pops on all 124 U124 rows: **0/124 solve**
  (5,229 CPU s).  Record for every row the shortest total length reached
  divided by the root length, `min L / L`:

  | rows | `min L / L` range | rows with ratio < 0.78 | < 0.80 | < 0.81 |
  |---|---|---:|---:|---:|
  | U124 (124) | 0.800 .. 1.000 | 0 | 0 | 5 |
  | solved ladder, all (60) | 0.000 .. 0.800 | 56 | 59 | 60 |
  | solved ladder, bins 6–9 (24) | 0.000 .. 0.762 | 24 | 24 | 24 |
  | solved ladder rows that `dyn` did *not* solve (18) | 0.680 .. 0.800 | 14 | 17 | 18 |

  AUC (probability a U124 row scores above a solved row) is 0.9999: the only
  contact is a tie at exactly 0.80 between ladder row 565 (20 → 16) and
  aca_101–104 (25 → 20).  The three rows the rank-two cap-closure separator
  (`research/ac_cap_closure_20260912`) could not tell from U124 (596, 605, 610,
  bins 7–8) sit at 0.727, 0.739 and 0.696 here.  U124 rows shorten by 0–5
  letters (histogram 0: 28, 1: 29, 2: 40, 3: 19, 4: 4, 5: 4), never below 80 %
  of their length; every solved row, solved or not within the budget, reaches
  80 % or less.  The same 0.80 floor, on the same four rows, is where the
  3-hour arbitrary-rank shortening campaign (`research/u124_rank_3h_20260912`,
  best totals 2,162 letters) stopped, so it is not an artefact of this budget.
  Nothing here proves a U124 row is *not* stably AC-trivial: the exhaustive
  dynamic-rank closure is not a usable ladder (see below), and the separator
  is a bounded-search statistic.

## Other measurements

**Certificates use the rank freely.**  In the 12 hard certificates 67–93 % of
the steps are at rank ≥ 3 (maximum rank 4 or 5); each passes through rank-two
waypoints, and on every one of them the shortest rank-two presentation met
before the end has total length 9.  The rank-two waypoints are on changing
generating pairs (an original generator is eliminated early in most paths), so
they are related to the root by stable, not necessarily rank-two, AC moves.

**Renaming canonicalisation matters.**  Quotienting states by permutations of
the generators (`dyn` against `dyn_norelabel`) turns 39/60 into 42/60 and
roughly halves the states per solve.

**Parameters are not tuned to the ladder.**  `dyn_c10s12` (cap 10, ceiling
L+12) also solves 42/60 with 1.7× the CPU: it gains 544 and loses 633; the
union of the two settings is 43/60.  The four `ctrl`-only bin-5 rows stall at
`min L / L` 0.79–0.80 under both settings.

**Thirteen new shortest states for U124.**  As a by-product the 2,000-pop
`dyn` runs reach shorter presentations than the earlier campaign's best totals
on 13 rows (aca_5, 6, 8, 15, 25, 26, 28, 29, 30, 31, 35, 53, 66; each 1–2
letters shorter, all at rank 3; aggregate 2,162 → 2,154 over the 124 rows,
with 6 rows worse and 105 equal).  Their replayed witnesses are in
`records/u124_shortening_witnesses.jsonl` (`min_state`, `min_path`,
`min_verified`).  These are shorter presentations in the *stable* class of
each row, not solves.

**Exhaustive dynamic-rank closure is not a practical ladder.**  With cap 8 and
total-length slack 0 (`records/closure_pilot_cap8_100k.txt`) bins 0–3 solve
inside 20–30k states, bins 4–5 exceed 100,000 states without solving (about
300 s each), and aca_115 closes at slack 0/1/2 with 1/6/12,656 states (57 s at
slack 2).  Definitions with three or more uses are length-neutral or better,
so the component under a length ceiling is large even at zero slack; the
minimal-slack analogue of the rank-two cap ladder was not pursued further.

## Scope and caveats

* Certificates are *stable* AC certificates with `define`/`eliminate` taken as
  primitive composites (each is one stabilisation or destabilisation plus AC
  moves whose existence follows from the trivial-group hypothesis and is not
  expanded).  Products are elementary and replayed literally.  On the solved
  ladder this proves nothing new about AC-triviality; it measures search.
* `ctrl` is this engine held at rank two, not the repository's `S20_MK2`
  heuristic; the comparison is like for like in moves, priority and budget.
  The `greedy nodes (1M budget)` column of the per-row table gives the
  repository's plain-greedy cost for orientation only (nodes and pops are
  different units).
* Budget is 2,000 pops per row and arm; the U124 verdict and the separator are
  statements at that budget.  The 0.80 floor agrees with a much larger earlier
  campaign, but it is an observation, not a theorem.
* States that differ only by inverting generators are not identified.
* Total CPU: ladder 1,132 s (`ctrl`) + 967 s (`dyn`) + 640 s (`dyn_norelabel`)
  + 927 s (`tri`) + 1,642 s (`dyn_c10s12`); U124 5,229 s; witnesses 13 rows
  rerun; closure pilot about 15 min.

## Files

Per-bin, per-row, U124 and separation tables: `RESULTS_TABLES.md`.  Records:
`records/ladder_p2000.jsonl` (ctrl, dyn, dyn_norelabel), `records/ladder_tri_p2000.jsonl`,
`records/ladder_c10s12_p2000.jsonl`, `records/u124_dyn_p2000.jsonl`,
`records/u124_shortening_witnesses.jsonl`, with the runner logs beside them.
