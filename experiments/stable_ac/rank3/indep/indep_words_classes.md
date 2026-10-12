# indep_words_classes.py: notes

Status: [unverified]. Written without running it (brief rule). Only the `ast` syntax check was run.

Run: `python3 indep_words_classes.py <RESULTS_DIR> <DATASET> <OUT_JSON> [workers] [minutes]`
Needs numpy only. Imports nothing from the repo. `workers` is ignored (no search). `minutes` is tested before each result file is opened; files not reached go to `skipped`.
Exit 0 = no mismatch, 3 = mismatch, 1 = crash. An exception inside one check is recorded in that check's `detail.errors`, the other checks still run, and the exit code is 1.
A check with `compared = 0` prints `NOTHING COMPARED (not a pass)`.

Sources read: BRIEF.md, the examples in `schema/` and `post_preview/`, the head of `data/ms640_solved.txt`, and one real control file (`dl/b1000/..._control.jsonl`) to see how unsolved rows are written. No repo source, none of the forbidden files, no author tooling.

## Checks

**0_dataset_format** (added, not in the task list). 640 lines; each line parses to an even number of integers; each half is letters from {1, 2, -1, -2} followed only by zeros. Reported, not judged: rows with a relator that is not freely or not cyclically reduced, min and max relator length, sha256 of the file.

**1_word_family.** For every `<stem>_L<n>.npz` (n = 1..10) and `<stem>_L<n>_inv.npz` (any n present; absent ones are listed as skipped only for n <= 6), both budgets:
- each entry of `words` has length n, letters in x,y,X,Y, no letter next to its inverse;
- `len(words) == 2*3^(n-1)`;
- no two entries equal, no two mutually inverse;
- the set of pairs {w, w^-1} equals my own: all 4*3^(n-1) reduced words built by extension, pair named by `min(w, inv(w))`;
- `_inv`: `words[k] == inverse(plain words[k])` for every k, same count;
- `pres_ids` has shape [640] and `pres_ids[i] == i`;
- `nodes`, `path_len` have shape [640, K] with K = 2*3^(n-1); `min_total` too when present;
- `meta.node_budget` equals the budget in the name. When the keys exist: `max_relator_length_cap == 24`, `z_len == n`, `n_words == K`, `n_presentations == 640`.

**2_value_sanity.** Per npz (rank-3 files and the rank-4/5 files, budget from the file name): every cell with `path_len >= 0` must have `1 <= nodes <= budget` and `path_len >= 1`. `compared` = number of solved cells. Detail per file and overall: max and min of `nodes - path_len` over solved cells, unsolved cells with `nodes < budget`, plus unsolved with `nodes > budget`, solved with `nodes == budget`, cells with `path_len < -1`.

**3_control_files.** Per budget: 640 rows; each pres_id 0..639 exactly once (any order); `node_budget` equals the name; `r1`, `r2` equal the dataset line rendered as letters; `(solved, nodes_explored, path_length)` equals the `n2_*` triple and the `null_*` triple, raw JSON values, `null` kept as `null`. A missing key is a mismatch.

**4_rank45_npz.** For R = 4, 5: `meta.rank == R`, `extra_generators == R-2`, `node_budget == 1000`; `meta.words` cut into slices of 2*3^(n-1) for n = 1..max_word_len, each slice checked as in check 1, total 3^m - 1; `combos` is [C, R-2] with C = comb(W+k-1, k), entries in [0, W), no multiset twice, and the set of sorted rows equals `combinations_with_replacement(range(W), k)`; `nodes`, `path_len` are [640, C]; `pres_ids` holds 0..639 once each; `base`, `null` are [640, 3]; `null[i] == base[i]`; `base[i] == (int(solved), nodes_explored, path_length)` of the budget-1,000 control row with pres_id `pres_ids[i]`.

**5_cross_budget_prefix.** For every `L<n>` and `L<n>_inv` present in both budgets: rows matched by pres_id, columns matched by word string (not by position). Per cell: `[path_len_1000 >= 0] == [path_len_10000 >= 0 and nodes_10000 <= 1000]`, and when solved at 1,000 `nodes` and `path_len` are equal in both files. One mismatch per bad cell. A pres_id or word present in only one budget is a mismatch. Same test on the two control files, on each of the three triples, plus `r1`/`r2` equal in both.
Detail per pair: cells solved at 10,000 with `nodes == 1000` exactly, and how many solved-flag mismatches sit on that boundary.

**6_signed_relabelings_ms640.** Report only (`compared = 640`, `mismatches = 0`). Canonical relator = least string among all rotations of r and of r^-1. Presentation key = the two canonical relators, sorted. The 8 relabelings are x -> one of x,y,X,Y and y -> plus or minus the other letter. Class of a row = least key over the 8 images. Detail: number of classes, histogram of rows per class, groups of rows with the same key (duplicates under the identity), groups of byte-identical lines, rows fixed by a non-identity relabeling with the list of those relabelings, histogram of stabiliser orders, and the full partition (rows of each class, with the relabelings taking the first row to each member).

**7_duplicate_starts_in_row.** Report only. For each row fixed by non-identity relabelings H, for n = 1..10: number of pair classes {w, w^-1} with `pair(s(w)) != pair(w)` for at least one s in H. Per row: that count, the count per relabeling, the number of H-orbits of pair classes (`distinct_starts`) and `redundant_starts` = words minus orbits. Totals over all rows, and total starts = 640 * (3^10 - 1) = 37,790,720. The words come from my own enumeration, not from the result files; the count does not depend on which member of a pair the files store.

## Memory

Arrays stay in their stored dtypes (uint16 / int16); nothing is widened except the solved subset used for `nodes - path_len`. Checks 1 and 2 hold one npz. Check 5 has to hold two (the same length at both budgets): `nodes` and `path_len` of each plus boolean masks, about 250 MB at worst for L10 present at both budgets, a few MB for the lengths expected at 10,000.

## Assumptions

- "pres_ids is exactly 0..639" in check 1 is read as in order (`pres_ids[i] == i`). In check 3 and check 4 it is read as "once each", because the control file is written in shard order.
- `min_total` is not named in the task; its shape is tested when it is present, its absence is noted and not counted.
- Check 2 judges only what the task states. `path_len < -1` is reported in the detail, not counted.
- Check 4 compares `base` with the main triple of the control row. The control file writes `path_length: null` for an unsolved row and `base` holds -1, so `null` is read as -1 (count in the detail).
- Check 4 slices `meta.words` by position. If the list is not ordered by length the slices fail.
- Check 5 covers the `_inv` files as well as the plain ones.
- Check 6 does no free or cyclic reduction: rotation is rotation of the letter sequence. If check 0 reports relators that are not cyclically reduced, the classes could differ from a definition that reduces first.
- Check 7 counts, for a row fixed by several relabelings, a word once if any of them moves it (union). Per-relabeling counts are also given.

## Things that looked off in the formats

- The brief gives `pres_ids` as int32. In the rank-5 example it is int64. Values are compared, dtypes are only reported.
- `path_length` is `null` in the control file for unsolved rows, while the npz files use -1.
- The control file rows are not in pres_id order (540, 556, 554 appear in that order among the unsolved rows).
- Check 5 at the boundary: a cell solved at 10,000 with exactly 1,000 nodes must be solved at 1,000 under the stated rule. If the solver stops before popping node number `budget`, those cells fail; the detail separates them.
- `extra_distinct_starts_whole_dataset_up_to_relabeling` in check 7 is an extra figure nobody asked for; it assumes the search treats relabelled starts alike, which this script does not test.
