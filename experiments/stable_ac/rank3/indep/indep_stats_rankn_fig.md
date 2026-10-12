# indep_stats_rankn_fig.py: notes

Written 2026-10-12. Not run here (no local compute); only the `ast.parse` syntax check was run, and it passed.

`python3 indep_stats_rankn_fig.py <RESULTS_DIR> <DATASET> <OUT_JSON> [workers] [minutes]`

`workers` is accepted and unused (nothing here searches; one process, one file in memory at a time; the rank-3 `L<n>.npz` rows are cast to int64 32 at a time, the small rank-4/5 arrays in one go). `minutes` is honoured before each `.npz` load; files not reached are listed in `skipped`.

## What is read

| Used as raw input | Compared against it (never trusted) |
|---|---|
| `rankn_bf_ms640_b1000_cap24_r<R>.npz` (`pres_ids`, `nodes`, `path_len`, `base`, `null`, `combos`, `meta`) | `..._r<R>_summary.json`, `..._r<R>_control_vs_start.md` |
| `rank3_bf_ms640_b<B>_cap24_control.jsonl` (`pres_id`, `solved`, `nodes_explored`, `node_budget`) and `..._L<n>.npz` (`pres_ids`, `words`, `nodes`, `path_len`, `meta`) | `rank3_bf_ms640_b<B>_cap24_control_vs_start_L<a>-<b>.md` |
| `DATASET` | only its line count (number of presentations) |

Nothing is imported from the repo. I read only BRIEF.md, the preview outputs in `post_preview/` (the summary JSONs, the `.md` tables, the top of the rank-3 summary JSON) and the headers of the two example `.npz` files in `schema/`. I did not open `rankn_bf.py`, `plot_rankn_vs_control.py` or any other excluded file.

## Checks

1. **`<rankn>.npz: structure of the raw arrays`**. Shapes, distinct `pres_ids`, `meta.rank` / `node_budget` / cap against the file name, `rank == 2 + extra_generators`, `meta.words` is the families of lengths 1..`max_word_len` concatenated (2·3^(n-1) words of length n), `combos` has C(W+k-1, k) rows that are distinct multisets with indices in range, `base[:,0]` is 0/1, presentations == lines of DATASET.
2. **`<rankn>.npz: base vs rank3 control.jsonl`** (one item per presentation). `base` solved flag equals the `solved` of the rank-3 control file of the same budget, and node counts are equal where solved. Extra to the task, but both are "the control".
3. **`<rankn>_summary.json: every field`** (one item per field). Definitions below.
4. **`<md>: table rows`** (one item per numeric cell: the count and six percentages of every row). Definitions below.
5. **`<md>: numbers in the title and the prose`**. Extra to the task: stem in backticks, rank, budget, presentations, starts each, searches, "Control solved: N of P", length range (rank 3), new generators and maximum word length (rank 4/5). An item whose text is not found is listed in `detail.not_found_in_the_text`, not counted.
6. **`rank3 ... : raw inputs of the tables`**. Per budget: control.jsonl has no duplicated `pres_id`, `node_budget` matches the file name, presentations == lines of DATASET, solved controls have 1..budget nodes; per `L<n>.npz`: shapes, K == 2·3^(n-1), every word has length n, words distinct, `meta.node_budget`, `pres_ids` is a permutation of the control's.

Rows are always aligned through `pres_ids` / `pres_id`, never by position.

## Definitions used

A start "solves" when `path_len >= 0`. `nodes` is cast from uint16 to int64 first.

### Tables (b)

Per presentation, over its K starts (K is the same for every presentation):

- fewer: solves and (control unsolved or nodes < control nodes)
- same: both solve, nodes equal
- more: both solve, nodes > control nodes
- not solved: the start does not solve
- fewer by more than 17%: solves and (control unsolved or nodes < 0.83·control nodes)
- more by more than 17%: both solve and nodes > 1.17·control nodes

Row value = 100 × mean over the group's presentations of the per-presentation share = 100 × Σ counts / (presentations × K). Groups: control solved with 1..9, 10..99, ... nodes, the last decade being the one that ends at budget−1 and also taking a control solved at exactly the budget; `unsolved`; `all`. The per-word-length table is the `all` row computed for one `L<n>.npz` at a time, with `starts` = K of that file.

Comparison: counts (`presentations`, `starts`) exactly; a percentage printed with d decimals within 0.5·10^-d + 0.001 (0.051 points for one decimal). A missing row of a non-empty group, an unknown or duplicated row label, an unparsable cell and a header whose six share columns cannot be identified each count as one mismatch. A row for an empty group is compared on its count only (its shares are undefined).

Rank 3 uses the control of `control.jsonl` (`solved`, `nodes_explored`) and the forward files `L<n>.npz` for n = a..b from the file name; if any of them is absent the control's-nodes table of that `.md` is skipped (listed) and only the per-length rows that have a file are compared. Rank 4/5 uses `base` of the `.npz` as the control and all C combos as the starts.

### Summary fields (a)

P = presentations, C = combos, solved = `path_len >= 0`, cs = `base[:,0] != 0`, cn = `base[:,1]`.

| Field | Recomputed as | Compared |
|---|---|---|
| `rank` | `meta.rank` | exact |
| `combos_per_presentation` | C | exact |
| `searches` | P·C | exact |
| `core_seconds` | `meta.core_seconds` | within 0.5 (the file rounds to an integer) |
| `ms_per_search` | 1000·`meta.core_seconds` / (P·C), from the unrounded seconds or from the seconds rounded to an integer, whichever is nearer to the file | within 0.05 |
| `null_mismatch_pres_ids` | `pres_ids` where the `null` row differs from the `base` row in any of (solved, nodes, path_len) | sorted lists |
| `control_solved` | Σ cs | exact |
| `mean_solve_rate_per_presentation` | mean over presentations of (solved combos / C) | 4 decimals (5e-5) |
| `mean_solve_rate_on_control_solved` / `_unsolved` | the same mean over presentations with cs / without cs | 4 decimals |
| `solved_by_some_combo` | presentations with any solved combo | exact |
| `gained_presentations` | `pres_ids` with a solved combo and an unsolved control | sorted lists |
| `lost_by_every_combo` | presentations with cs and no solved combo | exact count (a list of ids is also accepted and compared as a list) |
| `share_of_solved_combos_faster_than_control` | cells (cs, solved, nodes < cn) / cells (cs, solved) | 4 decimals |
| `presentations_where_some_combo_is_faster` | presentations with cs and a solved combo with nodes < cn | exact |
| `best_single_combo_solved` | max over combos of presentations solved | exact |
| `best_single_combo` | the named words must be one row of `combos` (as a multiset) and that row must solve `best_single_combo_solved` presentations | see below |

A field of the file that is not in this table is listed in `skipped` ("not known to this script"); a field of this table missing from the file is a mismatch.

## Assumptions and choices

- **Denominator of `share_of_solved_combos_faster_than_control`.** I take solved cells with a solved control. The preview numbers support it: for rank 5 the other reading (all cells with a solved control, 554·120) would need about 53 "fewer" cells, which would print 0.1% in the `all` row of the table, and the table says 0.0%; for rank 4 it would need about 525 cells while the table rows allow at most about 430. `detail.other_readings_not_compared` gives the other readings.
- **`presentations_where_some_combo_is_faster`** needs a solved control (same convention as the share field). The reading that also counts a gained presentation is in `detail`; the two differ only when `gained_presentations` is not empty.
- **`null_mismatch_pres_ids`** compares `null` with `base` inside the `.npz`, all three columns. The (solved, nodes)-only reading is in `detail`.
- **`best_single_combo` and ties.** Any combo that reaches the maximum satisfies the definition, so I check that the named combo reaches it instead of comparing with my own argmax. `detail.best_single_combo` says how many combos tie, whether the file names the first one, and whether the word order equals the `combos` row.
- **17% thresholds are the float64 products of the stated definition** (`nodes < cn*0.83`, `nodes > cn*1.17`; changed in review, see `## Review`). The exact integer reading (100·nodes vs 83·cn and 117·cn in int64) differs from it only when cn is 1700, 3300, 3400, 3500 or 6500..7000 in steps of 100 and nodes is exactly 1.17·cn: the float product rounds just below the integer, so the float reading counts that cell as "more by more than 17%" and the exact reading does not. `cn*0.83` never differs. So this can only matter at budget 10,000, and each such cell moves a row by less than 0.01 points. The number of cells the exact reading classifies differently is in `detail` of every table check (`exact_integer_17pct_cells_classified_differently`).
- **Group labels** are generated from the budget in the file name as "10^d to 10^(d+1)−1" and matched after removing thousands separators.
- **Compared-0 checks.** Anything that cannot be parsed is counted as a mismatch, so a check ends with `compared = 0` only when its inputs are listed in `skipped`; it is printed as `NOTHING COMPARED`, never as ok. The exit code follows the brief (0 when there is no mismatch), so a run on an empty directory exits 0 with `"compared": 0` and the last line says `(NOTHING COMPARED)`.

## Things that looked odd

- The rank-3 tables say "every word w of lengths 1 to n" and "6,560 starts each" for n = 8. That is Σ 2·3^(n-1): one word per pair {w, w^-1}, the forward files only. The `_inv.npz` runs (lengths 1 to 6) are not in the tables. The script follows the tables (forward files) and checks `starts` against the forward `K`; the wording of the prose overstates the set by a factor of two.
- The title calls it "a random k-generator start", but the numbers are exhaustive means over every start with each presentation weighted equally, not a sample.
- `control.jsonl` carries three controls (`solved`/`nodes_explored`, `n2_*`, `null_*`). The script uses the first. The number of rows where the other two differ from it is reported in `detail` of the raw-inputs check and is not counted as a mismatch.
- `pres_ids` is int64 in the example rank-5 file and int32 in the rank-3 files (the brief says int32); the script does not depend on the dtype.
- In the preview, `rank3_bf_ms640_b1000_cap24_control_vs_start_L1-7.md` and the rank-4 summary are older than the other files (01:15 vs 01:26). If stale files of that kind are in RESULTS_DIR they are checked like any other.

## Review

Reviewed 2026-10-12 by a second tester who did not write the script. Not run (no local compute). Read line by line against BRIEF.md, the task text, the preview outputs in `post_preview/` and the raw bytes (npy headers, `xxd`) of the two example `.npz` files in `schema/`. The `ast.parse` syntax check passes after the edits. `rankn_bf.py`, `plot_rankn_vs_control.py` and the other excluded files were not opened; nothing is imported from the repo.

### Changes

1. **17% thresholds (`cell_counts`)**: the compared values now use the float64 products of the stated definition, `nodes < cn*0.83` and `nodes > cn*1.17`. Before, the script compared the exact integer reading (100·nodes vs 83·cn, 117·cn) and only recorded the float reading. That was a deviation from the definition as given in the task. The exact reading is still computed and its number of differently classified cells is in `detail`; the key was renamed from `float64_literal_17pct_cells_classified_differently` to `exact_integer_17pct_cells_classified_differently`. I checked the first author's boundary claim by hand: 0.83 is stored as 0.83 − 0.36·2^-53 and 1.17 as 1.17 − 0.64·2^-53, so `cn*0.83` always rounds back to the exact product and `cn*1.17` rounds below it only for cn = 1700, 3300, 3400, 3500, 6500..7000 (step 100). At budget 1,000 the two readings agree on every cell.
2. **`ms_per_search` (`check_rankn_summary`)**: accepted when within 0.05 of 1000·core/(P·C) with core taken either unrounded from `meta.core_seconds` or rounded to an integer (the reading nearer to the file is used). Before, only the unrounded reading was accepted; if the file divides the rounded `core_seconds` the two differ by up to 500/(P·C) ms (0.0065 for rank 5), enough to turn a rounding-boundary case into a false mismatch.
3. **Notes**: the "17% thresholds" paragraph and the `ms_per_search` table row above were rewritten to match changes 1 and 2.

Nothing else was changed.

### Read and found correct

- Formats in `schema/`: `nodes` `<u2`, `path_len` `<i2`, `base`/`null` `<i4` [640, 3], `combos` `<i2`, `meta` a 0-d `<U` string, `pres_ids` `<i8` (rank 5) and `<i4` (rank 3), `words` `<U2`. Unsolved rows are (0, budget, -1). `base` and `null` are byte-identical in the example rank-5 file. Every load matches these; `allow_pickle=False` is fine (no object arrays).
- uint16/int16 are cast to int64 before every comparison and product (per 32-row chunk for rank 3, on load for rank 4/5). No Python loop runs over cells; the largest loop is over 640 presentations or 39,366 words. One `.npz` in memory at a time.
- Table parsing against the real preview files: the six share columns are identified (the "17%" headers are tested before plain "fewer"/"more"), `1,000 to 9,999` normalises to the generated label, `1,458` and `100.0%` parse, the separator row is dropped, the prose line containing `<x,y,z | r1, ...>` is not taken for a table.
- Decades: budget 1,000 gives rows up to `100 to 999`, budget 10,000 up to `1000 to 9999`; a control solved at exactly the budget lands in the last decade; unsolved controls go to `unsolved` whatever their node count.
- Not vacuous: a missing table, a missing row of a non-empty group, an unknown or duplicated label, an unparsable cell and a missing summary field each count as a compared item and a mismatch; a check with `compared = 0` prints `NOTHING COMPARED`.
- `share_of_solved_combos_faster_than_control`: the denominator (solved cells with a solved control) is the only reading consistent with the preview tables (rank 4 would need about 525 faster cells with the other denominator; the table rows allow at most about 430).
- Contract: argv positions, exit codes 0/3/1, OUT_JSON keys (`compared` at top level and `crash` are extras), numpy scalars and NaN removed by `clean()`, time box tested before every `.npz` load.

### Doubts not settled

- **Exit 0 with nothing compared.** On an empty or wrong RESULTS_DIR the script exits 0. The JSON (`"compared": 0`) and the last printed line (`NOTHING COMPARED`) say so, but a caller that reads only the exit code sees a pass.
- **A crash stops the remaining files.** An unexpected exception in one file's check ends the run (exit 1); the JSON still holds the checks done so far and the traceback. I found no crash path on the real formats, so I did not add per-file isolation.
- **`null_mismatch_pres_ids`** compares all three columns, including `path_len`. The generator may compare only (solved, nodes); that reading is in `detail`.
- **`presentations_where_some_combo_is_faster`** needs a solved control. It differs from the "gained also counts" reading only when `gained_presentations` is not empty.
- **`best_single_combo`** accepts any combo that reaches the maximum. A stricter "first maximiser" reading is reported in `detail` and not enforced.
- **A mean over an empty group** (for example no unsolved control) expects `null` or NaN in the file; a file that writes 0.0 there is reported as a mismatch.
- **Rank-3 starts** are the forward `L<n>.npz` files only (K = 2·3^(n-1)). This matches the "starts each" numbers of the tables, not their "every word w" wording.
- **Rank-3 control** is `solved` / `nodes_explored` of `control.jsonl`. If the tables were built from the `n2_*` copy and the two differ, rows will mismatch; the number of differing rows is in `detail` of the raw-inputs check.
- **Extra checks can fail on their own**: duplicated `pres_id` rows in `control.jsonl` count as a mismatch even when the rows are identical, and `base` of the rank-4/5 file is compared with the rank-3 `control.jsonl`. Neither is asked for by the task; a mismatch there is about the raw files, not about the summary or the tables.
- **A rank-3 `.md` with no per-word-length table** is listed as skipped for that table, not as a mismatch.
- **A stale file** (the preview has an older `_L1-7.md` and an older rank-4 summary) is checked like any other and may mismatch for that reason alone.
- **A third form of the 17% test** in the generator (for example a ratio `nodes/cn`) could differ from both readings, but only on exact ties (100·nodes equal to 83·cn or 117·cn).
