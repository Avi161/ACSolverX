# The AC difficulty ladder

Ten levels of Andrews–Curtis presentations, from "solved in a few heap pops" to
"only the cascades solve it", with nested subsets of 20 / 40 / 60 / 100 / 200 / 300 /
500 rows and a tester that runs any arm or policy over them and reports per level.
**Every row on the ladder is solved by something on record**; the 124 unsolved
Miller–Schupp classes are kept apart in [`unsolved_124.csv`](unsolved_124.csv) (below).
**Subsets 60, 100 and 200 are the main testers.**

Built 2026-09-10 by [`build_ladder.py`](build_ladder.py) (levels 9/10 split and the
unsolved rows moved off the ladder on 2026-09-11); nothing in it was searched for this
ladder except the 21 rows of [`grade_extra.py`](grade_extra.py) and the S20_MK2 grading
of the originals and MS-640 rows (below).

## Difficulty = plain greedy node count on record

The grading axis is the node count `g` of the **plain length-ordered greedy search**
(`config=None`, the baseline every heuristic is measured against), taken from the
committed large-budget runs:

| rows | run | budget | cap |
|---|---|---:|---:|
| all 72,779 AC19 aut-min orbits | `ac19_autmin_10k` (leftover branch) | 10k | 48 |
| the 843 greedy left unsolved there | escalation rungs `hsearch_ac19_hard100k` → `leftovers_1m` → `leftovers_5m` → `ac19_10m` | 100k → 1M → 5M → 10M | 48, 48, 64, 64 |
| 12 of those 843 the record never escalated + 1 for S20 | `sources/unescalated_*` (`grade_extra.py`, this box) | 100k, 1M | 48 |
| the 40 originals of the hard orbits | `ac19_orig_10m` | 10M | 64 |
| 8 more originals (`ac19_orig_cascade`) | `sources/open8_greedy_mrl64.jsonl` (`grade_extra.py`) | 100k | 64 |
| all 640 MS-640 rows | `greedy_1000000_640_mrl24` (blob `525050dd`) | 1M | 24 |

So `g` is exact for every row that solved, and censored at 10,000,000 for the 28 AC19
orbits that did not. The caps differ across runs (24 for MS-640, 48 up to 1M, 64
above) exactly as they did historically; each row carries its own `greedy_budget`,
`greedy_cap` and `greedy_run`, and the cap caveat from `CLAUDE.md` applies: read
solves as primary, node ratios across caps as indicative.

Levels 7–9 are **graded by record**: a 10M-pop greedy run needs ~50 GB, so they are
not re-derivable on a 15 GB box. Everything at or below 1M can be re-run
(`run_ladder.py` refuses larger budgets unless `LADDER_ALLOW_BIG=1`).

## The levels

| level | rule (`g` = plain greedy pops) | AC19 orbits | originals | MS-640 |
|---|---|---:|---:|---:|
| 1 | `g < 1,000` | 66,082 | 6 | 554 |
| 2 | `1,000 ≤ g < 10,000` | 5,854 | 24 | 52 |
| 3 | `10,000 ≤ g < 31,623` | 394 | 2 | 20 |
| 4 | `31,623 ≤ g < 100,000` | 226 | 13 | 8 |
| 5 | `100,000 ≤ g < 316,228` | 98 | | 4 |
| 6 | `316,228 ≤ g < 1,000,000` | 37 | | 2 |
| 7 | `1,000,000 ≤ g < E` | 30 | | |
| 8 | `E ≤ g ≤ 10,000,000` | 30 | | |
| 9 | plain greedy **unsolved at 10,000,000**; S20_MK2 solves it | 19 | | |
| 10 | plain greedy **and** S20_MK2 unsolved at 10,000,000; only the cascades solve it | 9 | | |

`E = 2,253,802` is the log-median of the 60 AC19 rows in [1M, 10M], so levels 7 and 8
hold 30 each (a fixed half-decade edge at 3.16M would leave level 8 with 15). It is
written into every subset's JSON under `E` and `levels`, so a file is readable on its
own.

Levels 1–2 together are the "< 10k" band; the split at 1k is so the easy end is graded
too (subset-60's bins 0–6 all sit below 15k).

**Levels 9 and 10** are the residue of the whole greedy escalation, 28 orbits, split by
whether S20_MK2 gets them. **Level 9** (19): S20_MK2 solves them — `s20_mk2@10k` 6,
`@100k` 2, `@1M` 8, `@5M` 3. **Level 10** (9): S20_MK2 fails at 10M too, only the cascades
solve them — `K3p_notable@1k` 7 (the table-free cascade), `K3p_c14aut@1k` 2 (only with
the cap-14 backward table): `ac19_16286, 27254, 28131, 44381, 50841, 51034, 59576,
65753, 7284`. `solved_by` says which on every row.

### The unsolved set (not on the ladder)

The 124 unsolved Miller–Schupp classes are **not ladder rows**: a benchmark row has to
be a problem somebody has solved, so a failure on it means something. They ship next
to the ladder, same columns, `level = unsolved`, `solved_by = none`:

- [`unsolved_124.csv`](unsolved_124.csv) — the 124 classes **in the form they were first
  found, before any μ-ladder reduction** (`data/ms_unsolved_reps/aca_124_initial.csv`,
  names `aca_0..aca_123`). This is "the u124".
- [`unsolved_all_forms.csv`](unsolved_all_forms.csv) — the same classes as `aca_best`
  (the μ-reduced pairs the u124 probes ran on, `acabest_N`), the 261 A-equivalent reps
  (`msrep_<name>`) and the 550 raw unsolved MS cells (`msraw_<line>`), 1,059 rows with
  `form` set, for anyone who wants a different starting representation.

The evidence for "unsolved by everything": 0/261 reps at 1M greedy (cap 48), 0/124 at
10M S20_MK2 (cap 64, `research/residual_20260909/u124/`), 0/124 by every cascade probe
at 10,000 units, and 0/124 from any automorphic image within two Whitehead moves at 20k
(`research/autchoice_20260910/applied/`). The tester runs on them like on any panel:
`run_ladder --subset unsolved124 …` (or `--panel benchmark/ladder/unsolved_all_forms.csv`).

## The originals: same orbit, different start

45 rows have `form = original`: the pre-Aut-min dataset presentations
(`ac19x_<row>` = line of `data/AC19_extended.txt`) of hard orbits. They are graded by
**their own** greedy cost and land in levels 1–4 (509–52,143 pops), while their
aut-min representatives sit in levels 9–10 (40 of them, greedy-unsolved at 10M) or
level 8 (the 5 open-8 reps, 2.3M–5M pops). That split is the finding
of `ORIGINALS_AT_10M.md` on the leftover branch — Aut-minimising a presentation can
make it dramatically harder to search — and the reason the second campaign
(`research/autchoice_20260910/`) exists. [`ladder_pairs.csv`](ladder_pairs.csv) lists
every pair side by side; `pair_id` links the rows in every CSV. Three of the
`ac19_orig_cascade` originals are also among the 40 and are graded by the 10M run.

## Row schema (every CSV, identical columns)

| column | meaning |
|---|---|
| `name` | `ac19_N` (aut-min orbit), `ac19x_N` (original), `ms_NNN` (MS-640 line); in the unsolved files `aca_N` / `acabest_N` / `msrep_*` / `msraw_N` |
| `r1, r2` | the relators, over `xXyY` (uppercase = inverse) |
| `level` | 1–10 as above (`unsolved` in the two unsolved files) |
| `source, form` | `ac19/autmin`, `ac19/original`, `ms640/ms_raw`; unsolved files: `ms_unsolved/{aca_initial,aca_best,ms_rep261,ms_raw}` |
| `orbit, pair_id` | the aut-min orbit an original belongs to; `pair_id` links original ↔ representative |
| `greedy_solved, greedy_nodes, greedy_budget, greedy_cap, greedy_run` | the grading number and where it came from (`10k`, `100k`, `1M`, `5M`, `10M`, `extra100k`, `orig10M`, `open8_100k`, `ms640_1M`; `unsolved@10M` for level 9) |
| `s20_solved, s20_nodes, s20_run` | the S20_MK2 cost: the AC19 escalation on record (`10k`, `100k`, `1M`, `5M`, `extra100k`; `unsolved@10M` for the 9 level-9 rows nothing but the cascades solve) and, for the 45 originals and the 640 MS-640 rows, `ladder100k` — `run_ladder.py` at 100,000 pops, cap 48, run for this ladder (`sources/s20_ms640_originals_b100000_c48.jsonl`, 685/685 solved and replayed) |
| `start_len` | `len(r1) + len(r2)` |
| `hump, hump_source` | peak total length − start along the cheapest **plain-greedy certificate on record** (100k rung `path_moves` replayed; 5M/10M `path`; the originals); blank where the record holds no path (all MS-640, AC19 levels 1–2 and 6) |
| `climb` | `max_relator_length_expanded − start_len` from the grading record — present on every graded row; the within-level spread axis |
| `solved_by` | cheapest solver on record: `greedy@…`, `s20_mk2@…`, `K3p_notable@1k`, `K3p_c14aut@1k`, `none` |
| `aut_class` | dedup key: the orbit for AC19, `ms_aut_<k>` (the 113 Whitehead classes) for MS-640 |

`ladder_all.csv` is the full pool (73,464 rows, all solvable). Levels 1–2 of it are the census; the
subsets are where the ladder is meant to be used.

## The nested subsets

`ladder_{20,40,60,100,200,300,500}.csv` (+ `.json`), `size/10` rows per level.
**Nested by construction**: `ladder_20 ⊂ ladder_40 ⊂ … ⊂ ladder_500`, because every
subset takes the first `k` of one fixed ranked list per level. Ranking inside a level:

1. rows solved at the root pop are left out (one such row, `ac19_347 = (Y, X)`);
2. **no `Aut(F₂)`-class dedup** — deliberately, unlike `subsets/`. Two automorphic
   presentations are two different search problems with different costs (the whole
   point of the original/representative pairs), so both are legitimate test rows;
   `aut_class` stays in the CSV as information;
3. round-robin over the strata `ac19/original`, `ac19/autmin`, `ms640/ms_raw` — so
   every source is present from k = 2 up, and the paired originals come first;
4. inside a stratum, **farthest-point order** over the rows sorted by
   `(log10 g, climb, name)`: the median first, then both endpoints, then the midpoint
   of the largest remaining gap. Every prefix is a near-uniform grid over the level's
   difficulty range, which is what lets one list serve k = 2 and k = 50.
   Level 9 sorts by S20_MK2 cost; level 10 (no pop cost at all) by `climb`, then start length.

Deterministic, no seed. Populations cap the top: levels 6 / 7 / 8 / 9 / 10 hold
39 / 30 / 30 / 19 / 9 rows, so subsets up to 60 are exact, 100 has 99 rows, 200 has
188, 300 has 268 and 500 has 377 — the JSON's `per_level_actual` says so, the old
ladder's "no subset-80" convention.

### The S20-hard variant: `ladder_{20,40,60,100,200,300}_s20hard`

Same levels, same strata, same exclusions, but inside a level the `k` rows kept are
the ones **S20_MK2 finds hardest** (largest `s20_nodes`; the 9 level-9 rows S20_MK2
cannot solve at 10M first; ties by plain greedy cost, then name) — no round-robin
over strata, so a level's picks come from whichever source holds its hardest rows
(level 3's top four are MS-640 rows; level 4 has two; everything else is AC19).
Levels stay the greedy bands; the nine rows S20_MK2 never solves are level 10 by
definition (`build_ladder.py` asserts every S20-unsolved row is greedy-unsolved too),
and level 10 has no S20 cost, so it keeps the spread ladder's rows. Nested:
`ladder_20_s20hard ⊂ … ⊂ ladder_300_s20hard`, with the same shortfalls as the spread
family (100 → 99, 200 → 188, 300 → 268). The JSON's `variant: "s20hard"` tells the two
families apart.

This is the tester for a technique that already beats S20_MK2: on the spread ladder
S20_MK2 clears levels 1–8 at 100k pops (its mean pops per level are in the hundreds
to low tens of thousands), so the spread rows do not separate a stronger ordering
from it. S20_MK2 pops on the S20-hard picks, mean (cheapest pick), per level and size:

| level | 20 (2/level) | 40 (4/level) | 60 (6/level) | 100 (10/level) | 200 (20/level) | 300 (30/level) |
|---|---|---|---|---|---|---|
| 1 | 7,665 (7,656) | 7,614 (7,563) | 7,595 (7,548) | 7,574 (7,537) | 5,781 (3,116) | 4,872 (3,018) |
| 2 | 15,784 (15,781) | 15,431 (14,377) | 15,080 (14,376) | 14,793 (14,362) | 12,955 (10,275) | 12,038 (10,168) |
| 3 | 33,834 (33,834) | 33,801 (33,768) | 33,648 (32,914) | 33,354 (32,913) | 28,720 (19,922) | 24,222 (13,770) |
| 4 | 38,131 (38,131) | 38,112 (38,089) | 36,816 (34,221) | 35,680 (33,976) | 34,533 (33,238) | 34,101 (33,238) |
| 5 | 89,220 (89,179) | 81,742 (64,874) | 74,219 (53,670) | 65,397 (48,090) | 43,629 (13,967) | 32,495 (8,713) |
| 6 | 95,928 (95,912) | 77,217 (43,912) | 60,348 (20,234) | 41,564 (6,132) | 23,135 (3,192) | 16,467 (3,092) |
| 7 | 1,383,279 (1,383,279) | 796,277 (158,725) | 583,316 (156,376) | 383,348 (30,933) | 202,113 (7,353) | 136,888 (2,378) |
| 8 | 252,412 (181,300) | 211,037 (169,589) | 195,853 (161,384) | 178,895 (149,792) | 119,954 (16,681) | 83,294 (6,988) |
| 9 | 1,298,683 (1,297,772) | 1,177,878 (816,736) | 1,045,835 (770,382) | 772,074 (229,165) | 422,461 (4,944), all 19 | 422,461 (4,944), all 19 |
| 10 | 2 rows | 4 rows | 6 rows | all 9 | all 9 | all 9 |

Levels 1–2 are still "greedy under 10k": the S20-hard rows there are the ones where
the ordering is *worse* than plain length order (greedy a few hundred pops, S20_MK2
7,500–15,000). Levels 6–8 run out of hard rows quickly (39 / 30 / 30 in the pool), so
from 100 rows up their cheapest picks fall to a few thousand pops; at 300 those levels
are the whole pool. Reference runs on `ladder_200_s20hard` are in `runs/README.md`.

## Running the tester

```bash
PYTHONPATH=. python3 -m benchmark.ladder.run_ladder --subset 60  --engine greedy  --budget 10000
PYTHONPATH=. python3 -m benchmark.ladder.run_ladder --subset 200 --engine s20_mk2 --budget 100000 --workers 4
PYTHONPATH=. python3 -m benchmark.ladder.run_ladder --subset 200 --engine policy --policy K3p_notable --budget 1000 --workers 4
PYTHONPATH=. python3 -m benchmark.ladder.report_ladder --runs greedy=runs/ladder_60_greedy_b10000_c48.jsonl \
    s20=runs/ladder_60_s20_mk2_b10000_c48.jsonl --out runs/report_60
```

- `greedy` / `s20_mk2` run the compact engine (`experiments/heuristic_search/core/hcompact`,
  pop-identical to `heuristics.greedy_search_h`) and count **heap pops**; `--cap`
  defaults to 48; `--cap 24` reproduces the MS-640 grading pop for pop.
- `policy` runs any name registered in `research/residual_20260909/policies.py`
  through `harness.run_row` and counts the policy's **charged units**. Under a table
  policy a lookup is free, so those units are a budget, not a difficulty
  (`AGENTS.md` §5): the report never puts pops and units on one curve.
- Every pop-engine solve is replayed independently (`words.canon_pair`, then
  `words.replay_move` over the recorded moves — never the engine's replay); a row is
  `verified` only if that ends on two distinct single letters. Policy rows carry
  `run_row`'s two-decoder verification. The tester exits non-zero if any solve fails
  to verify.
- Any `name,r1,r2` CSV works as `--panel`; `--levels 3-9`, `--names`, `--limit` filter.
  Runs are resumable by row name; `--force` restarts one.
- The report gives, per level, solved / verified and (pop engines) the median pops on
  solved rows plus the anytime curve `solved@B` for B ≤ budget — one run at budget N
  grades every smaller budget, since a search at B is the first B pops of any longer
  search — and, for every pair of runs, gained / lost per level with the
  continuity-corrected McNemar test from `research/residual_20260909/compare.py`.

## Reference runs

`runs/` ships baselines on `ladder_200` (188 rows) and on `ladder_200_s20hard` so a new
technique has something to stand next to (`runs/README.md` has the files, commands, the
S20-hard tables and the reading guide). Solved of 20 per level, of 19 at level 9 and of 9
at level 10:

| level | greedy @10k | greedy @100k | S20_MK2 @10k | S20_MK2 @100k | K3p_notable @1k units | K3p_c14aut @1k units |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 20 | 20 | 20 | 20 | 20 | 20 |
| 2 | 20 | 20 | 20 | 20 | 17 | 20 |
| 3 | 0 | 20 | 13 | 20 | 16 | 20 |
| 4 | 0 | 20 | 16 | 20 | 17 | 20 |
| 5 | 0 | 0 | 12 | 20 | 20 | 20 |
| 6 | 0 | 0 | 18 | 20 | 19 | 20 |
| 7 | 0 | 0 | 7 | 14 | 18 | 20 |
| 8 | 0 | 0 | 6 | 14 | 18 | 20 |
| 9 | 0 | 0 | 6 | 8 | 12 | 19 |
| 10 | 0 | 0 | 0 | 0 | 7 | 9 |
| **all** | **40** | **80** | **118** | **156** | **164** | **188** |

Greedy solving exactly levels 1–2 at 10k and 1–4 at 100k is the grading's sanity
check, not a result. Pops (first four columns) and charged units (last two) are not
comparable (see `runs/README.md`).

## Checks

- `tests/test_ladder.py`: words over `xXyY`, levels follow the bands, 7/8 split at
  `E`, every pool row is solvable, levels 9 (19, S20-solved) and 10 (the 9 named rows,
  cascade-only) are the greedy residue, the unsolved files hold exactly the 124 classes
  (four forms, 1,059 rows) and none of their names is in the pool, pairs link original ↔
  representative (originals ≤ level 4, reps at level ≥ 7), subsets nest and match
  `per_level_actual` (20/40/60/99/188/268/377), rows are pool rows verbatim, only the
  three strata and no trivial root, prefixes are spread, manifest hashes match the tree.
- Grading regression: `run_ladder --subset 60 --engine greedy --budget 10000` at
  `--cap 24` on the MS rows and `--cap 48` on the AC19 rows reproduces every recorded
  `greedy_nodes ≤ 10k` exactly and solves none of the rows recorded above 10k.
- A rebuild is byte-identical (`ladder_manifest.json` modulo timestamp and git head).
- S20-hard: every eligible row below level 10 carries an S20 grade; in each level of
  every `ladder_N_s20hard` no eligible row left behind has a larger S20 cost than the
  cheapest pick; level 9's picks are sorted by S20 cost; the six sizes nest; level 10
  equals the spread ladder's; every S20-unsolved row is at level 10. The tester's
  S20_MK2 runs at 100k on both 200-row panels reproduce every recorded
  `s20_nodes ≤ 100k` exactly.

## Provenance

Three inputs live on research branches, which are never merged
(`docs/BRANCH_MAP.md`); `build_ladder.py` reads them with `git show <sha>:<path>` at
`dab82a84` (`claude/ac19-leftover-solver-notebook-6yan6d`), `9033f13e`
(`claude/summer-results-docs-scoring-u6klsb`) and `525050dd` (the MS-640 greedy blob),
and records every blob's sha256 in `ladder_manifest.json`. Four inputs were produced
here with the repo's own engines and live under `sources/` (the three escalation rungs
the record lacked, `grade_extra.py`; and the S20_MK2 grading of the originals and
MS-640, `run_ladder.py`); they are hashed the same way. Rebuilding needs those
refs fetched: `git fetch origin claude/ac19-leftover-solver-notebook-6yan6d
claude/summer-results-docs-scoring-u6klsb`.
