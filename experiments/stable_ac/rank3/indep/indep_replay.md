# indep_replay.py: notes

Status: **[unverified]** by execution. Only the `ast.parse` syntax check was run
(it passed). Correctness rests on the hand traces below.

Run: `python3 indep_replay.py <RESULTS_DIR> <DATASET> <OUT_JSON> [workers] [minutes]`
Exit code, in this order: 3 if any mismatch; else 1 on a crash or an internal
error of the script in one file group (the JSON is still written, with
`internal_errors`, and the group is listed in `skipped`); else 0.
**Exit 0 does not mean replays happened**: a run where every check compared 0
items (wrong directory, all files absent) also exits 0. Read the per-check
lines; compared = 0 is printed as `NO DATA (compared 0, not a pass)`.

## What a move does (my own implementation)

Read from `solvern.py` (`moves_to_states`), not copied:

- A state is the list of relators, each one free + cyclically reduced and
  replaced by the least word among all rotations of it and of its inverse, the
  list then sorted by (length, word). Letter order: larger generator first,
  inverse before generator: `B<b<A<a<Z<z<Y<y<X<x`.
- Move `i_j_s_k1_k2`: `i`, `j` are **positions in that sorted parent state**,
  not positions in `<r1, r2, Zw>`. New relator i =
  `roll(r_i, k1) . roll(r_j^s, k2)`, reduced, made canonical; list re-sorted.
  `roll(w, k)` is numpy's: the last k letters move to the front.
- Start: canonical form of `[r1, r2, Z.w]` (rank n: `[r1, r2, Z.w1, A.w2, B.w3]`),
  r1, r2 from the dataset line of `pres_id`, w from the row.

I use a plain minimum over the 2n rotations (no Booth algorithm) on one byte
per letter in the order above.

### Hand traces (schema rows, all end trivial with the stored length)

`ms640_1`, `z_word` "xy", moves `2_0_-1_2_0, 2_1_1_0_0, 2_1_-1_0_0`, stored
`path_length` 3:

| step | state (sorted) | move | work |
|---|---|---|---|
| 0 | `YX, Zxy, YYXyx` | | canonical start |
| 1 | `X, YX, Zxy` | `2_0_-1_2_0` | roll(`YYXyx`,2)=`yxYYX`, inverse(`YX`)=`xy`, seam `X.x` cancels; `yxYYXxy` -> `yxY` -> cyclic `x` -> canonical `X` |
| 2 | `Z, X, YX` | `2_1_1_0_0` | `Zxy.YX` -> `Z` |
| 3 | `Z, Y, X` | `2_1_-1_0_0` | `YX.x` -> `Y` |

With a left rotation the first seam would be `Y.x` (no cancel), so the roll
direction is pinned by the data. Also traced, same result:
`ms640_0` "xx" (4 moves), relsub `ms640_506` "Xy" (9 moves, uses k1 = 7 and
k1 = 1), rank 5 `pres_id` 0 index 33 (5 moves) and index 52 (6 moves, uses
`3_2_1_0_1` and `4_1_1_1_0`).

## Checks

Aggregated over files; `detail.per_file` has compared / mismatches per file,
and top-level `per_file` has, per path file: path rows, rows replayed, replay
failures, rows with any failure.

Asked for:

| check | what |
|---|---|
| `replay_ends_trivial` | every path row: after all moves every relator is one letter and the letters are the n generators up to inverse. A bad move string, `i == j`, an index out of range or `s` not +-1 also fails here. The full row, the start and the final state go to `first_mismatches`. |
| `no_relator_over_24_on_path` | no relator longer than 24 at any state, start included. |
| `row_r1_r2_equal_dataset` | `r1`, `r2` strings of every rank-3 / relsub row (path rows and sample / relsub rows) equal the dataset relators of its `pres_id`. Rank-n path rows have no `r1`/`r2`. |
| `n_moves_eq_jsonl_path_length` | `len(path_moves)` == `path_length` of the sample row (same `pres_id` + `z_word`) or relsub row (same `name` + `z_word`), and that row is solved. No such row = mismatch. |
| `n_moves_eq_npz_path_len` | rank 3: == `path_len[row of pres_id, word_index]` of `<base>.npz`, `word_index` from the sample row. Rank n: == `path_len[row of pres_id, index]`. |
| `jsonl_nodes_eq_npz_nodes` | rank 3: every sample row `nodes_explored` == `nodes` cell. Rank n: every path row. |
| `solved_rows_have_path_row` | every sample / relsub row with `solved` true has a path row. |

Extra (kept separate so they cannot hide or fake a result above):

| check | what |
|---|---|
| `moves_wellformed_for_search` | each move is one the search can emit: `0 <= k1 < len(r_i)`, `0 <= k2 < len(r_j)`, both non-empty, seam cancels. If this fails in bulk while paths still end trivial, suspect a convention difference, not the paths. If both fail in bulk, suspect my canonical form first. |
| `sample_path_length_eq_npz_path_len` | every sample row: `path_length` (null -> -1) == npz cell and `solved` <=> cell >= 0. |
| `sample_word_index_eq_npz_word` | npz `words[word_index]` == `z_word`. |
| `rankn_row_matches_npz_combo` | `rank` == 2 + len(`z_words`) == R of the file name == meta `rank`; `z_words` == `[words[c] for c in combos[index]]`. |
| `row_name_zword_zrelator_consistent` | `name` is `ms640_<pres_id>`, `z_word` in x,y (length L and freely reduced in an L file), `z_relator` == "Z" + `z_word`. |
| `jsonl_rows_parse_unique` | each line is a JSON object; no two sample / relsub rows with one key disagree. |
| `path_file_has_rows` | a path file that is present has at least one row. |
| `companion_files_present` | paths / rows / npz of one group are all present or all absent. |

## Assumptions

- File names: `<base>_sample_paths.jsonl` with `<base>_sample.jsonl` and
  `<base>.npz`; `<base>_relsub_paths.jsonl` with `<base>_relsub.jsonl`;
  `rankn_..._r<R>_sample_paths.jsonl` with `rankn_..._r<R>.npz`. `_inv` files
  are assumed to be `<stem>_L<n>_inv_sample[_paths].jsonl` (the brief does not
  spell it). Files are found by suffix, so any base works; the expected list
  (L1-10, L1-6 inv, relsub, both budgets; r4, r5) is only used for `skipped`.
- The npz row of a presentation is looked up in `pres_ids`, not assumed equal
  to `pres_id`.
- A check with 0 comparisons prints `NO DATA (compared 0, not a pass)`. Absent
  group = skipped. Present path file with 0 rows, or a group with one file
  missing, = mismatch (my reading).
- `workers` > 1 only fans the replay out to a process pool; one npz is loaded
  at a time, in the parent. After `minutes`, no more replays and no new file
  group; the group in progress still finishes its length and coverage checks
  (they need no replay). Unreplayed rows are listed in `skipped`. The clock is
  read between replay jobs (100 rows) and between file groups, not while the
  sample / relsub rows are read.
- Rank is limited to 5 (letters `x y z a b`).

## Doubtful / looked odd

1. The brief does not say that `i`, `j`, `k1`, `k2` refer to the canonical
   sorted state. Replaying on `<r1, r2, Zw>` in file order fails at once.
2. The run used `solvern_fast.search_n_fast` (npz `meta.solver`), which I did
   not read. My semantics come from `solvern.py`; the traces above agree with
   rows that solver produced, but only on short paths.
3. A replay proves the stored moves are a valid path of that length. It does
   not prove the search finds that path, nor `nodes_explored`.
4. Not applicable, so not checked: `r1`/`r2` on rank-n rows (no such fields),
   check 3 for rank n (no sample jsonl), npz cells for relsub (no npz).
5. `pres_ids` is int32 in the rank-3 npz and int64 in the rank-n npz (brief
   says int32). Harmless.
6. L2 `meta`: `path_sample_target` 2000 but `n_sample` 1342. Not checked here.
7. If the `_inv` npz stores the forward words, `sample_word_index_eq_npz_word`
   fails on every `_inv` row; the example then carries the note "the npz word
   is the inverse of z_word".

## Review

Reviewer pass, read line by line against BRIEF.md and the task. The script was
**not run** (no local compute); only the `ast.parse` syntax check was re-run
after the edits, and it passed. Everything below is **[unverified]** by
execution.

### What I checked by reading

- Move semantics against `solvern.py` (`moves_to_states`, `reduce_word_nj`,
  `canonical_word_nj`, `_sort_key`): free + cyclic reduction, `np.roll`
  direction, inverse before roll, least word over rotations of w and w^-1 in the
  order `B<b<A<a<Z<z<Y<y<X<x`, sort by (length, word). Equivalent.
- Own hand traces, independent of the tester's: `ms640_1` "xy" (3 moves),
  rank-3 inv `ms640_0` "X" (3 moves), rank 5 `pres_id` 0 index 33 (5 moves),
  and the first 9 moves of a real 30-move relsub path (`ms640_612`,
  "Yxyyyyyyy": `2_1_1_6_9`, `2_0_-1_0_6`, `2_1_1_0_1`, `0_2_1_0_1`,
  `2_0_-1_2_0`, `2_1_1_2_0`, `2_0_1_3_4`, `1_2_1_1_5`, `2_1_-1_3_3`). The seam
  cancels at every one, through two three-way length ties in the sort. This
  goes beyond "short paths only" (doubt 2 above) but is still not a full path
  of a long row.
- Keys, shapes and dtypes against the real files: npy headers of the schema
  L2 and r5 npz (`nodes` `<u2`, `path_len` `<i2`, `combos` `<i2` [120, 3],
  `pres_ids` `<i4` / `<i8`, `words` `<U2`, `meta` 0-d `<U`), and the rows of a
  partial real download (`work/dl/b1000`: L1 to L5 plain and `_inv`, relsub).
  `_inv` files are named `<stem>_L<n>_inv_sample[_paths].jsonl` (assumption
  confirmed), the `_inv` npz stores the inverse words (`XXX`, `YXX`, `XYX`, ..),
  and `word_index` of an `_inv` row indexes them (doubt 7 does not arise).
  Spot cells read with `xxd`: L1_inv `nodes[0,:]` = 4,4 and `path_len[0,:]` =
  3,3; L2 `[1,1]` = 4 / 3; r5 `[0,33]` = 6 / 5, `[0,45]` = 8 / 7, `[0,52]` =
  7 / 6; all equal the jsonl rows. `combos[33]` = (0,6,6) and `combos[52]` =
  (1,3,6) give the rows' `z_words`.
- Overflow: every npz value is turned into a Python int at the one place a cell
  is read (`npz_cell`); no array arithmetic, no uint16 / int16 comparison.
  Words are `str(...)` before use. Nothing numpy reaches the JSON (and
  `default=str` would catch it).
- Size: no loop over npz cells. Real row counts: about 1,300 path rows per
  sample file, 39,968 relsub path rows (69,816 relsub rows), about 14 moves per
  path on average. The whole replay is seconds, the time box is not at risk.
- Relsub `z_len` is at most 17 in the real b1000 file, so the start relator
  `Z.w` is at most 18 letters: counting the start state in
  `no_relator_over_24_on_path` cannot give a false mismatch there.

### Changes

1. `run_replays`: with `workers` > 1 the loop over `pool.imap(...)` blocked
   for ever if a worker process was killed (its job never comes back), which
   would break the time box. Each job is now waited for at most
   `POOL_WAIT_SECONDS` (300 s) and never more than 5 s past the deadline. If
   a job does not come back within that wait and the deadline has not passed,
   the rest is replayed in the parent process (no row is dropped) and
   `pool_note` says so; if the deadline has passed, it is the ordinary
   time-out (rows listed in `skipped`). `multiprocessing` is imported at the
   top of the file for this.
2. Per-file counters: a path row whose start could not be built (bad name,
   `path_moves` not a list, bad `z_word`) was counted in `rows_replayed`. It
   now goes to the new `rows_start_not_built`; `rows_replayed` is only rows
   that were really replayed. It is still a `replay_ends_trivial` mismatch.
   The `FILE` lines print both, plus the rows not replayed for lack of time.
3. Checks that compared 0 items: besides the per-check `NO DATA` status, the
   JSON now has `checks_with_no_data` (list of names), one `NO DATA ...` line
   is printed, and the `TOTAL` line carries `checks_with_no_data=<n>`, so a
   run against an empty or wrong directory cannot be read as a pass from the
   last line alone. Exit code unchanged.
4. `pool_note` now lives in the run context and is printed (`POOL: ...`).

No check was weakened, and no check definition was changed.

### Doubts I could not settle

1. `companion_files_present` and `path_file_has_rows` turn an absent or empty
   file into a mismatch (exit 3), while the brief says an absent expected file
   is skipped and listed. Kept as the tester wrote it: the file is also listed
   in `skipped`, and the real run log shows the npz, sample and path files of a
   length are written in one step, so a half-present group is a real anomaly.
   If a results directory is copied while a length is being merged, expect a
   mismatch here that is not a data error.
2. Exit code 0 when every check has `NO DATA`. This is the letter of the
   contract ("0 if no mismatch"); see change 3.
3. Exit code 3 wins over 1 when there are both mismatches and an internal
   error in a file group. The JSON has `internal_errors` in both cases.
4. A row whose replay stops at a malformed move is still counted as compared
   (and passing) in `no_relator_over_24_on_path` for the states seen so far.
   It is a `replay_ends_trivial` mismatch already, so nothing is hidden, but
   `compared` of the cap check is slightly generous in that case.
5. The pool path (`workers` > 1), including change 1, has never been
   executed. `IMapIterator.next(timeout)` and `multiprocessing.TimeoutError`
   are the documented API. With `workers` = 1 none of that code runs.
6. Files I did not see: any b10000 file, the rank-4 npz and path file, L6 to
   L10. Same writer, so same format is assumed.
7. `solvern_fast.py` was not read (forbidden). See the hand traces above.
8. Reading beyond the brief's list, for data formats only: file names, first
   rows and `wc -l` of `work/dl/b1000`, npy headers via `unzip -p`, and a grep
   of that run's log for "sample". No forbidden file was opened.
