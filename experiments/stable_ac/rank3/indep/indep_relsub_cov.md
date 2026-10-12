# indep_relsub_cov.py

Independent recomputation of three parts of `rank3_bf_ms640_b<B>_cap24_summary.json`
(B = 1000 and 10000) from the raw files: the whole `relsub` block,
`control_at_larger_budgets`, and the control columns of
`views["<B>"].gained_presentations_priced`.

    python3 -I -u indep_relsub_cov.py <RESULTS_DIR> <DATASET> <OUT_JSON> [workers] [minutes]

Standard library + numpy. Nothing imported from the repo. Written from `BRIEF.md` and
`TASK_relsub_cov.md` only; none of the forbidden files were read. **Never run by me**
(syntax check only), so the first run on the box is its first run.

Exit 0 = no mismatch, 3 = at least one mismatch, 1 = crash (a partial OUT_JSON with a
`crash` field is still written). Integers must be equal, floats within 1e-9, booleans and
null exactly.

## Inputs it reads

| File | Use |
|---|---|
| `DATASET` | relators of presentation p = line p; source of the expected word set |
| `<stem>_summary.json` | the values under test |
| `<stem>_control.jsonl` | control at budget B: `solved`, `nodes_explored` |
| `<stem>_relsub.jsonl` or `.jsonl.gz` | relsub rows (plain file preferred; gzip detected by magic bytes) |
| `<stem>_L<n>.npz`, n = 1..10 | only `pres_ids`, `nodes`, `path_len` (+ `meta`, and `words` for one extra check) |
| CoV file | `$COV_FILE`, else `results/stable_ac/cov_all/cov_all_suballpxyb8_ms640_b100000.jsonl.gz` relative to the cwd; also tried: the same path without `.gz`, and the same basename inside `RESULTS_DIR` |

The CoV file is streamed once, line by line. Kept: the control row per presentation, the
fewest solved nodes per (presentation, fold(z_word)), every non-control cap. Because
"solved at B" is `solved and nodes <= B`, the fewest nodes at B is the fewest nodes overall
when that is <= B, so one pass serves both budgets.

Absent files are listed in `skipped` and the checks that need them are skipped by name.
With no CoV file every CoV check is skipped; the rest still runs.

## Checks

Per-budget names carry the prefix `b1000:` or `b10000:`.

Raw inputs:

- `dataset:lines_and_relators_well_formed`: 640 lines; each relator non-empty, letters in
  x,y,X,Y, zeros only as trailing padding. The number of relators that are not already
  cyclically reduced is in the detail (information, not a mismatch).
- `control_rows`: one row per presentation, `node_budget` = B, `r1`/`r2` equal to the
  dataset relators, solved rows have a `path_length` >= 0, unsolved ones null or negative.
- `relsub_rows_fields`: per row: valid `pres_id`, `z_word` in x,y, boolean `is_proper` and
  `solved`, integer `nodes_explored`, `family_tag` = "relsub", `r1`/`r2` equal to the
  dataset, and where present `node_budget` = B, cap = 24, `name` = "ms640_<pres_id>",
  `z_relator` = "Z" + `z_word`, `z_len` = length.
- `relsub_zword_is_own_fold`: rows whose `z_word` is not fold(z_word). Expected 0.
- `relsub_one_row_per_word`: no second row for the same (presentation, word).
- `relsub_wordset_per_presentation`: for each of the 640 presentations, the set of row words
  equals the relator-subword word set built from the dataset (missing and extra both count).
- `relsub_is_proper_flag`: `is_proper` equals "not whole" for every row whose word is in the
  expected set.
- `cov:rows_fields`: valid `pres_id`, boolean `is_control` and `solved`, integer nodes,
  `node_budget` = 100000, control rows have null `z_word`, non-control rows a word and a cap.
- `cov:orig_relators_match_dataset`: `r1_orig`/`r2_orig` of every CoV row equal the dataset
  relators (the join depends on both runs numbering presentations the same way).
- `cov:one_control_row_per_presentation`: exactly one, no conflicting copies.
- `bruteforce_npz_files`: shapes agree, `path_len` is signed, K = 2*3^(n-1), `pres_ids` is a
  permutation of 0..639, `meta.node_budget` = B and cap = 24.

Summary values:

- `summary_relsub_counts_and_stats`: `rows`, `rows_proper`, and the five numbers of `proper`
  and of `all` (12 leaves).
- `summary_relsub_vs_cov`: the 16 leaves of `relsub.vs_cov`.
- `summary_control_at_larger_budgets`: the four counts, keys "100" .. "100000".
- `summary_priced_gained_set_and_best_word_nodes`: `gained_at_this_budget`, the set of row
  `pres_id`s (missing, extra, duplicate), `best_word_nodes` per row. Needs no CoV file.
- `summary_priced_control_columns`: `control_file_budget`, `control_solves_them_at_file_budget`,
  `best_word_cheaper_than_control`, and per row `control_solved`, `control_nodes`.
- `summary_priced_best_word_attains_best_nodes` (extra to the task): the summary's `best_word`
  is a column of the `L<len>` file, solved for that presentation, with exactly the recomputed
  fewest nodes. It does not check which of several tied words was named.

Cross-run:

- `crossrun_control_solved`: CoV control row cut to B (solved and nodes <= B) against
  `<stem>_control.jsonl`, all 640 presentations.
- `crossrun_control_nodes`: nodes equal wherever both are solved at B.

## Readings I chose where the text left room

1. **Zero compared.** A check that ran and compared 0 items gets status `ZERO_COMPARED` and
   counts as 1 mismatch, so the exit code cannot be 0. Checks that cannot run are in
   `skipped` instead.
2. **`vs_cov.control`** comes from `<stem>_control.jsonl` (the rank-3 run's own control at B),
   not from the CoV file cut back to B. The cross-run check says whether the two agree; the
   CoV-based count is in the detail as `alternative_control_from_cov_file_cut_to_B`.
3. **`cov_oracle`** uses non-control CoV rows only. The count with control rows included is in
   the detail. In the committed summaries `control_or_cov` = `cov_oracle`, so both readings
   give the same number there.
4. **`rank3_not_cov`, `cov_not_rank3`** are differences of the two oracle sets (proper relsub
   solved vs CoV solved at B), control not involved.
5. **Join key.** The relsub row's `z_word` is looked up as written in has_row[p] (CoV words
   folded). No fold is applied to the relsub side; if a relsub word were not its own fold the
   fold check fails and the join would miss it.
6. **`is_proper` in the statistics** is the row's own flag. Whether the flag is right is the
   separate `relsub_is_proper_flag` check.
7. **Word set** is built from the cyclic reduction of the dataset relator (free reduction,
   then stripping inverse end pairs). Row `r1`/`r2` are compared with the relator as written
   in the dataset. Both agree if the dataset is cyclically reduced, which the detail reports.
8. **`rows`, `rows_proper`** count every line of the relsub file, including any malformed one.
9. **Means.** `mean_solve_rate` is over presentations with at least one such row;
   `mean_fraction_faster_than_control` over the control-solved ones among them, with all the
   presentation's such rows in the denominator (solved or not).
10. **Gained presentations** use every `<stem>_L<n>.npz` present, n = 1..10, and never the
    `_inv` files (the summary's `n_words_per_presentation` = 19,682 = sum of 2*3^(n-1) for
    n <= 9 says the views hold no inverse words). The lengths used and the summary's `max_len`
    are in the detail. If the box holds a length the summary was not built from, this check
    fails on purpose.
11. **`control_nodes`** is compared with the CoV control row's `nodes_explored` literally,
    solved or not. No gained presentation has an unsolved control at 100,000 in the committed
    summaries, so this branch is untested; a summary that writes null there would be flagged.
12. **`control_file_budget`, `cov_file_budget`** are compared with the constant 100000;
    `cov:rows_fields` separately checks that every CoV row says `node_budget` 100000.
13. **`cov_median_cap`** is `statistics.median` over every non-control row's cap (mean of the
    two middle values for an even count), compared as a float.
14. **Unknown summary keys.** A key I recompute that is missing in the summary is a mismatch.
    A key in the summary that the task does not define (`shortlex_nodes`,
    `shortlex_to_first_solve_cheaper_than_control`, anything new) is listed in `skipped` as
    not verified.
15. **Only `views["<B>"]`** of the stem's own budget is checked. In the committed files the
    priced block is null in the other views.
16. **Incomplete brute-force input.** If a present `L<n>.npz` cannot be used (time box, bad
    shape or dtype) the three priced checks are skipped rather than computed from fewer words.
17. **`workers`** is ignored. **`minutes`** is checked between stages and every 20,000 CoV rows;
    stages not started are skipped.

## Not checked

Row order in any file; `shortlex_*` fields; the tie-break behind `best_word`; the priced
block of other views; `_inv` files; `relsub_paths`; that solved rows have nodes <= B (another
tester's ground).

## Things that looked odd

- **The relsub file is not in presentation order** (the committed b1000 file starts with
  `pres_id` 506, then 524). Harmless here: rows are grouped by `pres_id`.
- **CoV `r1`/`r2` are the transformed relators**; the originals are `r1_orig`/`r2_orig`.
  Anyone joining on `r1` would silently get nothing for non-control rows.
- **Several CoV rows share one (presentation, word)** (for example pres 444 has many `yy`
  rows with caps 27 to 45). So the same-word comparison sets one rank-3 search at cap 24
  against the best of several CoV starts at larger caps (median 33). The summary text does say
  "best CoV start", but `same_word_cov_fewer_nodes` and `same_word_only_cov_solves` are a
  best-of-several against one, not a like-for-like count.
- **Only 9,759 of 59,486 proper relsub rows join** to a CoV row with the same word, while the
  summary .md calls the proper rows "in the CoV family". The same-word table covers about a
  sixth of them.
- **`same_word_tie` is 456 at both budgets.** Plausible (ties sit at small node counts, already
  inside 1,000) but worth a look if anything else in `vs_cov` fails.
- **`vs_cov.control` has no stated source** in the task. See reading 2.
- **The brief's example word `'xY'`** for the npz `words` is not its own fold under this task's
  fold (that would be `'yX'`). The few words I checked by hand (the L2 sample, three
  `best_word`s) are their own fold, so the example is probably only illustrative. The script
  does not depend on it.
- **`control_nodes` for an unsolved control** is undefined in the task. See reading 11.

## Second tester

Read the script line by line against `BRIEF.md` and `TASK_relsub_cov.md`. Never run (syntax
check only, passes after the last edit). None of the forbidden files were read. No definition
was changed: every compared number is computed exactly as the first tester wrote it.

### Confirmed against the task and real rows

- **Fold.** Coding x=1, y=2, X=-1, Y=-2, larger tuple of w and w^-1. By hand on rows of the
  committed b1000 relsub file: `Yxy` = (-2,1,2) against its inverse (-2,-1,2): own fold;
  `yyxY` = (2,2,1,-2) against (2,-1,-2,-2): own fold; `XYYYYYYxy` (pres 506) = (-1,..) against
  its inverse `YXyyyyyyx` = (-2,..), which is the window of r1: the row carries the larger one.
  The rows of a presentation are sorted by length and then by this integer order
  (`Yxy` < `Xyy` < `xyy` < `yxY` ..), which confirms Y < X < x < y.
- **Word set and `whole`.** Pres 506, r2 = `YYYYYYX`: its seven rotations fold to `xyyyyyy`,
  `yxyyyyy`, .., `yyyyyyx`, exactly the seven length-7 rows with `is_proper` false; `yyyyyyx`
  also sits strictly inside r1 and is still not proper; `yyyyyyy` (inside r1 only) is proper.
  Pres 506 has 5 words of length 2, as computed by hand. In `relator_subwords` "whole wins"
  does not depend on the order of the relators.
- **Dataset.** Checked with awk: 640 lines, width 48, zeros only trailing, every relator
  freely and cyclically reduced, lengths 2..17. Reading 7 never matters on this dataset.
- **Solved at B** through the overall minimum and `<= B` is exact; "faster" is strict `<`;
  `control_at_larger_budgets` uses `<= b`; the six join buckets sum to the joined count in both
  committed summaries (9,759).
- **Set differences.** Committed numbers fit rank3 − cov on the two oracle sets (60 = 604 − 544,
  34 = 626 − 592), not the unions with the control (that would be 40 and 16).
- **npz.** `nodes` is cast to int64 before the minimum, `path_len >= 0` is taken on a signed
  array (checked), no array is compared with the budget. One file in memory at a time.
- **Sizes and time.** CoV file: 4.1 MB gzipped, 88,154,686 bytes plain (gzip trailer), 114,682
  rows, about 770 bytes a row; relsub files 24.9 MB plain each. No multi-GB input exists. The
  CoV file is streamed; kept are 640 control tuples, at most 114,042 (presentation, word)
  minima, the same number of raw words and caps. `json.loads` on every line is a few seconds.
  Whole run: well under a minute.
- **Zero compared (reading 1).** Every optional input goes through `skip` before a check is
  created; `summary_priced_best_word_attains_best_nodes` is skipped when there is no candidate.
  A null block in the summary where the script can recompute is a real mismatch (1 compared,
  1 mismatch), never a zero-compared one. Left as is: `cov:orig_relators_match_dataset` would
  compare 0 if the CoV rows had no `r1_orig` (the committed file has it on every row seen).
- The lead's "reading 4" and "reading 5" are readings 5 and 10 of the list above.

### Changes

1. **Exit code when no summary value is compared** (`run`, after the budget loop). The dataset
   and CoV checks always compare items, so a wrong or empty `RESULTS_DIR` ended with exit 0 and
   everything else in `skipped`. Now a check `summary:no_summary_value_compared` with 0 items is
   added in that case: status `ZERO_COMPARED`, exit 3.
2. **`report_only` key per check** (`Check.report_only`, written next to `detail`). Other
   readings of the same numbers, computed in the same run, never compared. Each block is in a
   `try`, so it cannot crash the compared part.
   - `summary_relsub_counts_and_stats` (for `proper` and `all`): solve rate pooled over rows;
     mean solve rate over all 640; mean fraction faster over all control-solved presentations,
     over every presentation with such rows (unsolved control as 0), with a gain counted as
     faster, and as faster rows / solved rows; faster-or-gained count.
   - `summary_relsub_vs_cov`: `control` from the CoV file cut to B and the two unions with it
     (reading 2); `cov_oracle` with control rows (reading 3); the two differences taken between
     the unions (reading 4); joined count with the relsub word folded before the lookup, with
     the CoV word not folded, and with whole rows included (reading 5); how many CoV words are
     not their own fold; low and high median of the cap (reading 13). The two alternatives that
     sat under `detail.notes` moved here.
   - `summary_priced_gained_set_and_best_word_nodes`: gained count if only lengths up to m were
     used, for every m present (reading 10; says at once which `max_len` a different summary
     count belongs to); gained count with the CoV control row cut to B as the control.
   - `summary_priced_control_columns`: the gained rows whose control is unsolved at 100,000 with
     what the summary wrote for them, the number of `control_nodes` mismatches under the "null
     when unsolved" reading, `best_word_cheaper` counting only solved controls (reading 11).
3. **Length files beyond 10** (`scan_bruteforce`). The loop was `1..MAX_LEN` with `MAX_LEN`
   10 (not 9). It now also takes any `<stem>_L<n>.npz` with a larger n found in the directory,
   since the summary is built from every length file present. `_inv` files do not match.
4. **A line that is not JSON** (`json_lines`) is counted as one bad row by the loader instead
   of crashing the run with exit 1.
5. `detail.notes` of `summary_relsub_vs_cov` also lists the presentations in `cov_not_rank3`.

### Not resolved

- **`control_nodes` when the control is unsolved at 100,000** (reading 11). On the box L10
  (b1000) and L7 (b10000) are new, so the gained sets can grow past the committed 22 and 4. The
  CoV README says the control fails at 100,000 on `pres_id` 634-639. If one of them is gained,
  the compared reading (the CoV row's `nodes_explored`, 100000) fails against a summary that
  writes null there. `report_only` of that check shows which reading the summary follows.
- **`cov_oracle`** (reading 3). The committed summaries have `cov_oracle` = `control_or_cov`,
  which fits both readings of the summary but does not show that the non-control count equals
  it. If the summarizer counts control rows in the oracle, `cov_oracle` and `cov_not_rank3` fail
  here; `report_only.cov_oracle_including_control_rows` tells.
- **`_inv` files** are not used for the gained set and no alternative is computed with them.
- **Fold check as a mismatch.** The task says "report how many"; the script counts each such
  row as a mismatch. Kept: such a row would fail the word-set check too.
- **Truncated gzip input** still crashes (EOFError from gzip), exit 1.
- **Empty gained set with a null priced block** would be one mismatch ("missing in the
  summary"). Not the case on any committed summary.
