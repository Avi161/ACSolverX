# indep_stats_rank3.py: notes

2026-10-12. **[unverified]** The script has never been executed (the brief allows only `ast.parse`, which passes). Its first run is the real run.

## What it does

`python3 indep_stats_rank3.py RESULTS_DIR DATASET OUT_JSON [workers] [minutes]`

For each budget B in (1000, 10000) it reads `rank3_bf_ms640_b<B>_cap24_summary.json`, `_control.jsonl`, `_L<n>.npz` (one at a time, nodes cast to int64), `_L<n>_inv.npz` and, for two row counts only, `_relsub.jsonl`. It recomputes the summary numbers and compares them leaf by leaf. Nothing is imported from the repo; the summarizer was not read.

- Ints must be equal. Floats: absolute 1e-9. Timing fields: relative 1e-5 (source is float32).
- `workers` is ignored (nothing searches). `minutes` is checked before each length file; what was not reached is listed in `skipped`.
- `DATASET` is only used for an information line (how many control rows have the same r1, r2 as the dataset line) and as a fallback for r1, r2.
- Exit 0 no mismatch, 3 any mismatch, 1 crash or load error, and also 1 when nothing at all was compared. A check with `compared: 0` prints `NOT COMPARED` and has `status: "not_compared"`.
- OUT_JSON has the contract keys plus `compared`, `info`, `errors`, `crashed`, and a `status` per check.
- Every leaf of the summary JSON that was not compared is listed in `skipped` with a reason (grouped by field).

## Checks

Names are `b<B>:...`; `inferred` in the name means the task gave no definition and the reading is mine.

| Check | Compared | Reading |
|---|---|---|
| `header` | node_budget, cap, n_presentations, view keys, by_length and oracle row sets, word family of each file (2·3^(n-1) distinct words of length n), meta budget and cap, n_words_per_presentation, n_searches | given |
| `control_equals_null_start` | per presentation: (solved, nodes, path_length) against the `n2_*` and `null_*` columns | the .md says "identical to the null stabilization" |
| `view<V>:by_length` | control_solved, n_words, solve_rate, solve_rate_control_solved / unsolved, faster, equal, slower, lost, mean_presentations_per_word, best_single_word (+ count) | given. In view V a search is solved iff solved in the file and nodes <= V; same for the control. Rates are means over presentations of the per-presentation fraction |
| `view<V>:oracle` | words, solved_by_some_word, gained_over_control, control_solved_lost_by_every_word | given |
| `oracle_some_word_faster_than_control` | that column, all views | both readings are computed; see below |
| `view<V>:overall` | faster, equal, slower, lost, solve_rate, solve_rate_control_unsolved | per-presentation fraction over all words of lengths 1..max_len |
| `inverse_pairs` | words of `_inv` are the inverses in the same order; pairs, identical, solved_status_differs, mean and p99 of the node difference | at the file budget. identical = same solved flag and same nodes. Mean and p99 (numpy linear) over pairs where both solve |
| `inferred:median_extra_nodes` | by_length column | see below |
| `inferred:timing` | ms_per_search, core_seconds | 1000·sum(block_seconds)/(640·K); sum over the main L files |
| `inferred:view<V>:words_vs_control` | words_beating_control (per length and total), words_matching_control | words whose solved count is above / equal to the control's |
| `inferred:view<V>:relator_rotations` | relator_rotations block, overall_without_relator_rotations, oracle column some_non_rotation_word_faster | see below |
| `inferred:view<V>:top_words` | solved, gained, lost, faster of each listed word; list is in non-increasing solved order and equals the largest counts | faster = control-solved presentations solved with fewer nodes |
| `inferred:view<V>:fixed_word_cross_validated` | train/test solved and control counts; the word has the largest train count | halves by parity of pres_id |
| `inferred:view<V>:price` | price block; of gained_presentations_priced: gained_at_this_budget, the set of pres_id, best_word, best_word_nodes, shortlex_nodes | see below |
| `inferred:view<V>:gained_priced_control_columns` | control_solved, control_nodes of the gained rows, against the budget-10,000 control file | only rows whose published control_nodes <= 10,000 |
| `inferred:control_at_larger_budgets` | entries up to the largest control budget present | solved and nodes <= that budget |
| `inferred:relsub_row_counts` | relsub.rows, relsub.rows_proper | lines of `_relsub.jsonl`; lines with `is_proper` true |
| `cross:prefix_property_b1000_vs_b10000` | views 100 and 1,000 recomputed from the b1000 arrays against the b10000 arrays, lengths in both | not a summary comparison; tests the prefix rule the views rest on |

## Readings I chose

- **some word faster than control.** Primary: strict (the control solves in the view and some word solves with fewer nodes). The inclusive count (plus presentations only a word solves) is also computed; the detail says which one reproduces the rows, and mismatches are counted against the better one, as the task asked which reading matches. Evidence for strict: in the example `per_presentation.csv`, pres 538 (control unsolved) has 191 words solving and `words_faster` 0.
- **median_extra_nodes.** No definition, and the .md does not print it. Checked against: per presentation, median of (word nodes - control nodes) over its solving words, control-solved presentations only; then the median over presentations. The pooled median over cells and the per-word-then-median reading are also computed and their hit counts are in the detail. Pooled looked unlikely: published values include 5.5, 3.5, 8.5, which a pooled median over thousands of small integers almost never gives. My confidence in the primary is about one half; a failure here with another reading at full hits is a difference of definition, not of data.
- **relator rotation.** (presentation, word) is one when w or w^-1 is a cyclic rotation of r1 or r2 (the family keeps only one of w, w^-1). The published 6,310 rows are about 9.9 per presentation, which fits this and not "w itself only" (about half). The alternative row count is in the detail. faster/equal/slower count only rows where the control solves; the mean extra nodes is pooled over rows where both solve (published mean x published solved is an integer in both views). "Without rotations" uses per-presentation fractions over the remaining words.
- **price.** Words are run in file order (L1, L2, ... and column order inside a file). A search that does not solve in the view costs min(nodes, V); the first solving one costs its nodes. This matches the example rows (151,649 = 151 x 1,000 + 649). "Beats the control" = fewer nodes, or solved where the control is not (the .md says so). `control_nodes_median_same_presentations` = median of the control's raw nodes over every presentation the run solves; the alternative (only control-solved ones) is in the detail.
- **best_single_word, cross-validated word, best_word of a gained row.** Ties are accepted: the named word must attain the maximum (or minimum nodes); the tie-break itself is not checked.
- **max_len.** Treated as the summarizer's choice, not a statistic. L files beyond it are listed in `skipped`, not counted as a mismatch.

## Not checked (listed in `skipped` at run time)

- `subword_vs_other_within_bf`, `relsub.proper`, `relsub.all`: rule for subwords and denominators not defined.
- `relsub.vs_cov`: needs CoV files.
- `gained_presentations_priced` totals and the control columns above 10,000 nodes, `control_at_larger_budgets["100000"]`: need a control run at 100,000 nodes, which is not among the result files.
- `source`.

## Things that looked odd

- `gained_presentations_priced.control_file_budget` is 100,000, but `<stem>_control.jsonl` in the schema example is at the sweep budget (1,000). The summary depends on a control file that the brief does not list.
- The b10000 example summary has no `inverse_pairs` block; the b1000 one has. If b10000 `_inv` files exist the script reports its own counts in `skipped`.
- The .md says "shortlex order", but the L2 file order is xx, xy, yx, yy, yX, Xy. I assumed the summarizer means file order.
- `median_extra_nodes` jumps at length 3 (5.5 at 1,000 nodes, 8.5 at 10,000) and falls back at length 4. It may be an average of two unlike middle values rather than a typical value.
- An unsolved search stores nodes = budget and path_len = -1 (seen in the L2 example bytes); the script relies on `path_len >= 0` only.

## Review

2026-10-12, by a second reader who did not write the script and could not run it. **[unverified]** Still never executed; `ast.parse` passes after the edits. Evidence below comes from reading the example outputs in `post_preview/` and the example `L2.npz` header bytes (grep counts on the example `per_presentation.csv`, no computation on arrays).

### Changes made to the script

1. **`price.control_nodes_median_same_presentations`: the checked reading changed.** It was the median of the control's nodes over every presentation the shortlex run solves; it is now over the presentations the run solves *and* the control solves in the view. The old reading cannot reproduce the example b1000 summary at 100 nodes: among control-solved presentations the control's nodes have 206 values <= 7, 250 <= 8, 295 <= 9. Median over the 455 control-solved ones = 8 (published 8.0); over all 514 the two middle values are both 9. The old reading would have failed on a correct summary. The other value is still printed in the check's detail. This supersedes the sentence about that field under "Readings I chose / price".
2. **`inferred:view<V>:gained_priced_control_columns`: a branch that could not fail was removed.** When the control file that reaches furthest is this budget's own (always at budget 10,000, or when the b10000 control file is absent), "that file must not solve the gained row" is true by construction, because the row is gained exactly when that file leaves it unsolved. Those rows are now listed in `skipped` instead of counted as compared. The check then prints `NOT COMPARED` if nothing else fed it.
3. **`header`: the pass-only record for `max_len` was removed.** It was recorded only when equal to the number of L files and never as a mismatch, so it could not fail. `max_len` is now listed in `skipped` with both numbers. Same for `inverse_pairs.max_len`, which was marked as seen without any comparison.
4. **`control_equals_null_start`: the path length is compared only when the search is solved.** The example CSV prints an empty path length for unsolved control rows; if the control row stores `null` and the `n2_*`/`null_*` copies store -1 (or the reverse), the old list comparison would have reported 86 false mismatches per copy. Solved flag and nodes are still compared for every row.

### Checked against the example outputs, no change needed

- **Relator rotations (w or w^-1 a rotation of r1 or r2).** Sum of the lengths of all relators of length <= 8 in the example CSV = 28 + 42 + 56 + 1,010 + 468 + 2,114 + 2,592 = 6,310 = published `rows` at budget 1,000; lengths <= 5 give 1,136 = published at budget 10,000. Exact both times.
- **`some_word_faster_than_control`: strict.** 171 example rows have control solved and `words_faster` >= 1; published 171 at 1,000 nodes, length 8. The inclusive reading would give 193.
- **Folds by parity of pres_id.** 273 even and 281 odd control-solved rows = published `train_control` / `test_control` at 1,000 nodes; 224 / 231 at 100 nodes.
- **Views of the control.** 455 rows with control solved and nodes <= 100.
- **Timing.** Sum over lengths of `ms_per_search` x 640 x words = 487,473 s = published `core_seconds`, so both come from the main L files only.
- **`median_nodes_to_first_solve`.** 250 of the 576 first-solve costs are <= 9 and 45 equal 10, so the median is 10.0 as published.
- Format strings (argument counts), key names against the example JSON, dtypes against the L2 header (`<u2`, `<i2`, `<U2`, `<f4` shape (640, 1), 0-d `<U492` meta), int64 casts before arithmetic, JSON serialisation of every value that reaches OUT_JSON: read line by line, no fault found.
- Size and time: no Python loop over cells; the largest file needs about 1 GB at peak (int64 nodes 200 MB plus per-view temporaries); the time box is tested before each length file.

### Doubts I could not settle

- **`median_extra_nodes`.** Still a guess between "per presentation, then median over presentations" (checked) and "per word, then median over words". The half-integer values at lengths 2 and 3 only (6 and 18 words) fit both. Expect this check to fail if the summarizer uses the other one; the detail gives the hit count of each reading.
- **`control_nodes_median_same_presentations`.** "Run solves and control solves" and "every control-solved presentation" give the same values on both examples; the first is checked.
- **Cost of a search that does not solve inside a view smaller than the file budget** (`min(nodes, V)`). Nothing published depends on it in the examples (the medians fall on presentations solved by the first word), so it is untested either way.
- **`inverse_pairs` mean and p99.** Over pairs where both solve, at the file budget, numpy linear percentile: inferred from the names only.
- **`gained_priced_control_columns` and `control_at_larger_budgets["10000"]` at budget 1,000** compare numbers the summary took from a 100,000-node control file with the b10000 control file. A mismatch there means the two control runs are not the same search, not that the summary is wrong about its own source.
- **`ms_per_search` on real bytes.** The example L2 file comes from the fast solver (about 1 ms per presentation block) and the example summary from an older run (67 ms per search), so the formula is confirmed by arithmetic only.
- **Exit code when one budget crashes and another has mismatches.** The script returns 3 and lists the crash under `errors`; a crash with no mismatch returns 1. The contract does not say which wins.
- **`control_equals_null_start`.** If the null rank-3 start does not pop the same number of nodes as the 2-generator control this check fails on every such row; the example head shows equal triples for the first four presentations only.
