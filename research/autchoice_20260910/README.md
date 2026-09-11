# autchoice: which Aut(F2)-image of a presentation is cheapest to search from?

**Question.** `ORIGINALS_AT_10M.md` (leftover branch, `dab82a84`) and the figure
"The same AC moves, seen from both starting points" show that the identical AC-move
sequence has a flat length profile from the ORIGINAL dataset presentation and a mountainous
one from its Aut-minimal representative: at 10M greedy nodes 40/40 originals solve, 0/28
representatives do.  "Shortest under Aut(F2)" is therefore not "easiest to search from".
This directory is the DATA for learning which automorphic image is cheapest: the
orbit-cost atlas, the shared library, and a reproducible version of the figure.

Git head at build: `460904f9850ee20e3fe7772704a17db36f44f707` on
`claude/ac19-theorem-strength-8v1wp6` (working tree; nothing here is committed).
Everything lives in this directory; nothing outside it was modified.

## Files

| file | what it does |
|---|---|
| `orbit.py` | `ball(pair, radius, cap=48)`: BFS over `autcanon.AUTOS` (fixed order) from `canon_pair(pair)`, nodes deduplicated by `words.relabel_key`, images with a relator longer than `cap` dropped; every node carries `seq` (AUTOS indices, application order), the composite `phi` (built with `autcanon.compose`, checked with `autcanon.check`), `depth`, `rkey`.  The representative *run* is the first image discovered in BFS order (the identity is the pair exactly as the ladder ran it).  Also `apply_sequence`, `compose_sequence`, `find_relabel`, `greedy_descent` (strict length descent by AC moves), `ball_sizes`.  `python3 -m research.autchoice_20260910.orbit` prints ball sizes for `ladder_20`. |
| `features.py` | `features(r1, r2) -> OrderedDict`: the 17 `heuristics.phi` features by name, `h_s20mk2 = L + 20 S + 2 MK`, exponent sums `ex1 ey1 ex2 ey2`, `abelian_det`, `min_len`, `max_len`, `total_len`, `once_gen` (generator occurring exactly once in a relator, sign ignored, 0..4), `once_letter` (signed letters, 0..8). |
| `engine.py` | `cost(pair, budget, cap, config) -> {solved, nodes, path_moves, max_expanded}` around `hcompact.greedy_search_hcompact` with an independent `words.replay_move` replay (raises `ReplayError` if a claimed solve does not replay); `verify_from_original(orig_pair, seq, path_moves)` applies the automorphism sequence one Whitehead automorphism at a time with `apply_pair`, replays the moves, and demands the trivial pair; `replay` stops at 512 letters (a replay from the wrong start doubles every move). |
| `tests/test_orbit.py` | witnesses on every radius-2 image, relabel dedup idempotence (ball of an image inside the source's larger ball), the root ball, |det| invariance, `verify_from_original` on a committed certificate.  `python3 -m pytest research/autchoice_20260910/tests -q` (6 tests, ~1 s). |
| `build_panel.py` -> `panel.csv`, `panel_manifest.json` | the atlas panel (below). |
| `time_budget.py` -> `timing.json` | the budget measurement (below). |
| `run_atlas.py` -> `atlas.jsonl`, `atlas_run.log`, `atlas_rejects.log` | the atlas run (below); resumable. |
| `analyze_atlas.py` -> `ATLAS.md`, `atlas_summary.json` | per-row and aggregate tables, Spearman, depth-1 generators, the pairs; headline findings at the top of `ATLAS.md`. |
| `plot_pairs.py` -> `pairs_length_profiles.png`, `pairs_length_profiles.json` | the figure, from the committed 40-pair data read with `git show`. |

## Commands (from the repo root)

```bash
python3 -m pytest research/autchoice_20260910/tests -q
PYTHONPATH=. python3 -m research.autchoice_20260910.build_panel
OMP_NUM_THREADS=1 NUMBA_NUM_THREADS=1 PYTHONPATH=. python3 -m research.autchoice_20260910.time_budget --budgets 5000 10000 20000 40000
OMP_NUM_THREADS=1 NUMBA_NUM_THREADS=1 PYTHONPATH=. python3 -m research.autchoice_20260910.run_atlas --budget 20000 --workers auto
PYTHONPATH=. python3 -m research.autchoice_20260910.analyze_atlas
OMP_NUM_THREADS=1 NUMBA_NUM_THREADS=1 PYTHONPATH=. python3 -m research.autchoice_20260910.plot_pairs
```

`matplotlib` was not installed on the box; `pip install matplotlib` (3.11.1) was run for
`plot_pairs.py`.  No scipy/sklearn anywhere (Spearman is a 15-line numpy function).

## Inputs and their hashes

| input | sha256 |
|---|---|
| `benchmark/ladder/ladder_200.csv` (after the 2026-09-10 rebuild) | `3e68646c927475ca291094a1cce41b059f9318a1ea70586a834768956524a34c` |
| `benchmark/ladder/ladder_all.csv` (same rebuild) | `c8db8a749d1cd17e25a7deff247a2f807637f98e63274317bf514d0601d2d032` |
| `dab82a84:results/heuristic_search/ac19_autmin_screen/unsolved_10m_orig_baseline.csv` | `2b4e6debe916a4a769f2798382c59df6fcc3fc7a4a4f9a58e902ed53bc9453de` |
| `dab82a84:results/heuristic_search/ac19_orig_10m/ac19_orig_10m_greedy_b10000000_mrl64.jsonl` | `4e40d3d60ff14fb50ff4a5a057b029852c3db8e13f459e5f148ec75dd67c065e` |

The two leftover-branch blobs are read with `git show` and never copied into the tree.

## The panel (`panel.csv`)

Level 3, 4, 5 rows of `ladder_200.csv` (20 each) + all 28 level-9 rows of `ladder_all.csv`
(the aut-min representatives plain greedy cannot solve at 10M) + all 45 `form=original`
rows.  **124 rows, not the brief's 133**: nine of the level-3/4 picks of `ladder_200` are
themselves originals, so they are one row each (`panel_manifest.json` lists them under
`multi_reason`).  Per level 1:6, 2:24, 3:20, 4:26, 5:20, 9:28; per form autmin 60,
ms_raw 19, original 45; 73 pair rows (28 reps + 45 originals) get the plain-greedy arm too.
The ladder was rebuilt while this campaign was being set up (the subsets no longer
deduplicate by Aut class); the panel was built after the rebuild from the files hashed above.

## Ball sizes

`orbit.ball` at cap 48, relabel-deduplicated, on every row of `ladder_20`:

| radius | images (incl. identity) |
|---:|---|
| 1 | 5 on every row |
| 2 | 13 on every row |
| 3 | 21–29 (29 on 15/20 rows; fewer where the cap prunes) |

Why so small: under relabelling the 12 second-kind Whitehead automorphisms collapse to
four classes (`y->yx` ~ `y->xy`, `y->Xy` ~ `y->yX`, `x->xy` ~ `x->yx`, `x->Yx` ~ `x->xY`;
the pairs differ by an inner automorphism, invisible on cyclic words) and the four
conjugation-type ones (`y->Xyx`, ...) are inner, i.e. the identity on cyclic words.  So the
ball is 1 + 4 + 8 + 16 ... (each step has one backtracking direction).  Across the panel:
1,612 images for 124 rows (13 each).

## Budget choice (`time_budget.py`, `timing.json`)

Sample: identity + last radius-2 image of 10 panel rows spanning levels 3/4/5/9 and the
originals, both arms, one worker, while two ladder workers were running on the other cores:

| budget | runs | censored | s/run (censored) | pops/s (censored) | s/run (all) | worst-case atlas h @2w | sample-rate atlas h @2w |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 5000 | 2561 | 31/40 | 1.06 | 4,714 | 0.87 | 0.38 | 0.31 |
| 10000 | 2561 | 30/40 | 2.45 | 4,081 | 1.91 | 0.87 | 0.68 |
| 20000 | 2561 | 26/40 | 5.54 | 3,611 | 3.91 | 1.97 | 1.39 |
| 40000 | 2561 | 23/40 | 12.48 | 3,204 | 7.87 | 4.44 | 2.80 |

**B = 20,000**: the largest of the brief's 5k / 10k / 20k that fits 2 wall-hours at 2
workers even if every run is censored (1.97 h; 1.39 h at the sample's solve rate); 40k was
timed for reference and does not fit.  Per-pop cost rises with the budget because the
state arena grows (~100 discovered states per pop).  Smaller budgets are read off by
rescoring (`solved and nodes <= b`), so `ATLAS.md` reports 5k / 10k / 20k from one run.

## The atlas run

**Budget B = 20,000 pops, cap 48, radius 2.**  `S20_MK2` on all 1612 images of the 124 rows;
plain greedy additionally on the 949 images of the 73 pair rows: 2,561 searches.

| phase | workers | records | wall |
|---|---:|---:|---:|
| `time_budget.py` (160 sample runs, 1 worker, ladder jobs alive) | 1 | – | ~10 min |
| atlas part 1, 19:26:25–19:41:47 UTC (two ladder jobs alive; log `atlas_run_part1_2workers.log`) | 2 | 362 | 15.4 min |
| atlas part 2 (resumed after the ladder jobs ended; log `atlas_run.log`), done 20:13:34 UTC | 4 | 1,250 | 31.7 min |
| `plot_pairs.py`, `analyze_atlas.py` | 1 | – | ~1 min each |

Atlas wall 47 min (≈1.6 core-hours), well inside the 2 h projection because most images
solve early.  The resume lost only the records in flight at the stop (re-run).

**Verification.** 715/1612 S20 runs solved, 715 verified; 201/949 greedy runs solved,
201 verified; 0 rejected (`atlas_rejects.log` is empty).  Every solve passed both the replay from
the image (`engine.cost`) and the replay from the row's own pair through the elementary
automorphism sequence (`engine.verify_from_original`).

**Consistency with the ladder.** On every panel row whose ladder record is at most 20,000
pops the atlas identity reproduces it exactly: `s20_nodes` on 37/37 rows and `greedy_nodes` on
30/30 originals (both cap 48).  So the atlas engine is pop-identical to the ladder's grading
and an atlas cost is on the ladder's scale.

### Headline findings (from `ATLAS.md`, every number computed from `atlas.jsonl`)

- Choosing the best of the 13 radius-2 images (an oracle) raises S20_MK2 solves at 20,000 pops from 94/124 (the row as given) to 119/124; at 5,000 pops from 64/124 to 101/124.  On the 28 level-9 representatives (plain greedy fails at 10M): identity 6, best image 26.
- The row as given is the cheapest image of its ball on 10/124 rows; some image is strictly cheaper on 114/124, by a median factor of 10^0.67 where it is (median identity rank 3.00 of 13).  The shortest image is the cheapest on 10/124 rows.
- Inside a ball, longer images are somewhat dearer but length is not the ordering: Spearman(total length, log cost) pooled 0.22, per-row median 0.31 (91 rows positive, 27 negative); the shortest image is the cheapest on only 10/124 rows.
- No single depth-1 Whitehead generator helps on average: the best one (x->Yx, y->y) has median log10 cost ratio 0.000 and is strictly cheaper than the identity on 0.26 of rows; across the four, the fraction strictly cheaper is 0.18, 0.23, 0.24, 0.26.
- The 40 originals whose representative is in the panel (S20): the original as given beats the best image of the representative's radius-2 ball on 29/40 pairs; the original's relabel class lies in the representative's radius-2 ball on 17/40, within radius 4 on 40/40.  Plain greedy at 20,000: identity 30/45 originals and 0/28 representatives solve; best-of-ball 44 and 13; the original beats the rep's ball on 15/40 pairs.

The cheapest image of a ball sits at depth 2 on 97/124 rows, depth 1 on 17, and is the row
itself on 10; per image the chance of beating the identity is the same at both depths
(23% at depth 1, 22% at depth 2), so the depth-2 advantage is breadth, not a better generator.
Per form the gain is largest on the aut-min rows (median log10 gain 1.02, 58/60 have a
strictly cheaper image) and smallest on the MS-640 rows (median gain 0.00; 5/19 already
cheapest as given), with the originals in between (0.48).

**Equal compute.** The oracle above spends 13 searches.  A portfolio that runs all 13 images
round-robin with 20,000 pops *in total* solves a row iff 13 x (best image cost) <= 20,000, i.e.
best <= 1538:

| level | rows | identity @20k | 13-image portfolio @20k total | oracle best image @20k each |
|---|---:|---:|---:|---:|
| 1 | 6 | 6 | 6 | 6 |
| 2 | 24 | 24 | 19 | 24 |
| 3 | 20 | 18 | 11 | 20 |
| 4 | 26 | 25 | 15 | 25 |
| 5 | 20 | 15 | 14 | 18 |
| 9 | 28 | 6 | 10 | 26 |
| all | 124 | 94 | 75 | 119 |

At equal compute the portfolio still beats the identity on the hard rows (level 9: 10 vs 6)
and loses on the easy ones, where the identity solves within 20k anyway but not within 1538.

### Level 9: the 28 representatives plain greedy cannot solve at 10M

`ladder s20` is the ladder's S20_MK2 escalation record on the representative (10M = unsolved);
`atlas id` the same start at 20k (20000 = censored); `best` the cheapest radius-2 image, with its
depth, the AUTOS sequence (`orbit.AUTOS` indices, applied left to right) and its total length
against the representative's; `greedy best` the cheapest image under plain greedy.

| rep | ladder s20 | atlas id | best | depth | seq | len best / rep | greedy best |
|---|---:|---:|---:|---:|---|---:|---:|
| ac19_15507 | 4,944 | 4,944 | 467 | 2 | 15 15 | 23 / 21 | 20,000 |
| ac19_61253 | 4,949 | 4,949 | 470 | 2 | 15 15 | 26 / 22 | 20,000 |
| ac19_28510 | 5,306 | 5,306 | 479 | 2 | 15 15 | 23 / 19 | 20,000 |
| ac19_56970 | 5,883 | 5,883 | 506 | 2 | 14 14 | 24 / 20 | 20,000 |
| ac19_67987 | 6,073 | 6,073 | 515 | 2 | 14 14 | 23 / 19 | 20,000 |
| ac19_23156 | 6,112 | 6,112 | 514 | 2 | 15 15 | 18 / 16 | 20,000 |
| ac19_50892 | 22,068 | 20,000 | 6,670 | 2 | 9 9 | 26 / 24 | 20,000 |
| ac19_27187 | 22,091 | 20,000 | 6,670 | 2 | 9 9 | 26 / 24 | 20,000 |
| ac19_65206 | 228,598 | 20,000 | 3,307 | 2 | 15 15 | 25 / 19 | 1,839 |
| ac19_20270 | 229,165 | 20,000 | 3,307 | 2 | 15 15 | 29 / 21 | 1,842 |
| ac19_57992 | 229,844 | 20,000 | 3,307 | 2 | 15 15 | 27 / 21 | 1,842 |
| ac19_36350 | 230,141 | 20,000 | 3,307 | 2 | 15 15 | 31 / 23 | 5,769 |
| ac19_46363 | 756,582 | 20,000 | 2,005 | 2 | 8 14 | 30 / 21 | 20,000 |
| ac19_55019 | 770,382 | 20,000 | 190 | 2 | 9 15 | 30 / 23 | 815 |
| ac19_67055 | 793,117 | 20,000 | 728 | 2 | 9 9 | 22 / 20 | 569 |
| ac19_40312 | 816,736 | 20,000 | 603 | 2 | 8 8 | 21 / 19 | 1,138 |
| ac19_54835 | 1,297,409 | 20,000 | 1,729 | 2 | 15 15 | 21 / 17 | 4,932 |
| ac19_12445 | 1,297,772 | 20,000 | 1,729 | 2 | 15 15 | 19 / 17 | 4,932 |
| ac19_31298 | 1,299,594 | 20,000 | 1,729 | 2 | 15 15 | 19 / 17 | 4,932 |
| ac19_16286 | 10,000,000 | 20,000 | 14,071 | 2 | 9 9 | 21 / 19 | 20,000 |
| ac19_27254 | 10,000,000 | 20,000 | 20,000 | 0 | id | 19 / 19 | 20,000 |
| ac19_28131 | 10,000,000 | 20,000 | 14,056 | 2 | 9 9 | 21 / 17 | 20,000 |
| ac19_44381 | 10,000,000 | 20,000 | 6,526 | 2 | 9 9 | 19 / 19 | 20,000 |
| ac19_50841 | 10,000,000 | 20,000 | 744 | 2 | 14 8 | 21 / 17 | 4,037 |
| ac19_51034 | 10,000,000 | 20,000 | 2,701 | 2 | 9 15 | 23 / 17 | 1,843 |
| ac19_59576 | 10,000,000 | 20,000 | 14,056 | 2 | 9 9 | 21 / 19 | 20,000 |
| ac19_65753 | 10,000,000 | 20,000 | 4,315 | 2 | 14 8 | 31 / 20 | 4,931 |
| ac19_7284 | 10,000,000 | 20,000 | 20,000 | 0 | id | 19 / 19 | 20,000 |

Twenty-six of the 28 have a radius-2 image S20 solves in at most 14,071 pops; the two it does
not (`ac19_27254`, `ac19_7284`, both `K3p_notable@1k` in the ladder) have no image solving
at 20k.  The cheapest image is never shorter than the representative: longer on 25 of the 26 solved
level-9 rows, equal on 1.  Its sequence is one generator applied twice (`15 15` = x -> YYx,
`9 9` = y -> XXy, `14 14` = x -> xyy) on 21 of the 26, two different generators on
5; over the whole panel the cheapest image is a repeated generator on 62/124 rows, two
different ones on 35, a single one on 17, the identity on 10 (and it is longer than
the row on 99, equal on 6, shorter on 9 of the 114 non-identity winners).
Plain greedy, 0/28 on the representatives at 10M, solves 13/28 from some radius-2 image at
20k — the oracle image turns an unsolvable-at-10M row into a sub-20k one for the baseline too.

### Caveats

- `cheapest = identity` counts ties, so a ball whose every image is censored is counted as
  "identity cheapest" (plain greedy at level 9: 15/28 are such all-censored balls).
- Costs above 20,000 are censored; the ladder's own record (`panel.csv`) gives the identity's
  true cost for rows the atlas censors.
- 40 of the 45 originals have their representative in the panel (level 9); the other five have
  level-8 (open-8) representatives that were not in the brief's panel, so the pair tables have
  40 rows.
- The depth-1 generator labels are relative to each row's own representative (a relabelling
  swaps `y->yx` with `y->Xy`), so the per-generator table says "no single first move helps on
  average", not which move to make.


## Deviations from the brief

- Panel of 124 rows, not 133 (duplicates; above).
- `ball` runs the first-discovered image of each relabel class, not the relabel key itself,
  so the identity is exactly the ladder's pair; the key is recorded as `rkey`.
- `verify_from_original` / `engine.replay` stop when a relator passes 512 letters (a wrong
  replay grows exponentially; the first draft of the test hung on it).
- The dashed tail in the figure is an AC-move descent (`orbit.greedy_descent`, the greedy
  strict-length descent over all Definition 2.1 moves — Nielsen moves on a basis pair), so
  the orange curve plus tail is a genuine AC path from the representative to (x, y).  On all
  40 pairs it reached (x, y) in 1–4 moves; the engine fallback was never needed.  A left
  Whitehead descent (applying automorphisms to the basis pair) would not be an AC path.
- `time_budget.py` also timed 40k (informational); B stays within the brief's menu.
- matplotlib installed with pip (not present on the box).

## The figure (`pairs_length_profiles.png`, `.json`)

Reproduced from the committed 40-pair data (`plot_pairs.py`; the per-pair series, phi and
the mapped states are in `pairs_length_profiles.json`).  For every pair the original's
10M-greedy certificate (`path`, re-checked move by move with `words.replay_move`) is drawn
in blue as total relator length; the SAME states mapped through phi -- the automorphism
`autcanon.peak_reduce` + `level_min` found from the original to its representative, which
landed exactly on the committed `rep_r1, rep_r2` on all 40 pairs -- in orange; and the
dashed tail is the AC-move descent from `(phi(x), phi(y))` to `(x, y)` (`orbit.greedy_descent`;
1–4 moves, engine fallback never needed).  Since AC moves commute with
automorphisms, orange + tail is a genuine AC path from the representative to the trivial pair.

| | original | representative side |
|---|---:|---:|
| median hump above the start (peak total length − start) | +1 | +29 |
| median peak total length | 29 | 49 |
| pairs whose peak exceeds cap 48 | 0/40 | 20/40 |
| pairs whose peak exceeds cap 64 | 0/40 | 10/40 |

The rep-side peak is higher than the original's on 40/40 pairs.  So from the
representative the original's certificate is not merely mountainous: on 20/40 pairs it
passes through states the cap-48 search may not even hold, and on 10/40 through states
above the cap-64 of the 10M runs.  The representative's own cheapest certificate, if any,
must be a different move sequence.
