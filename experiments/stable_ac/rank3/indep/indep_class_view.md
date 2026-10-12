# indep_class_view.py

Independent recomputation of every number in the four class views:
`rank3_bf_ms640_b1000_cap24_class_view.json`, `rank3_bf_ms640_b10000_cap24_class_view.json`,
`rankn_bf_ms640_b1000_cap24_r4_class_view.json`, `rankn_bf_ms640_b1000_cap24_r5_class_view.json`.

    python3 -I -u indep_class_view.py <RESULTS_DIR> <DATASET> <OUT_JSON> [workers] [minutes]

Standard library and numpy only, nothing imported from the repository. Written from
`BRIEF.md` and `TASK_class_view.md`; never run (only the `ast.parse` syntax check), so
it was desk-checked instead. Not read: `class_view.py`, its test, `words.py`, the other
`indep_*.py` scripts, or any file on the brief's list.

Inputs used: the dataset, `<stem>_control.jsonl`, `<stem>_L<n>.npz` (arrays `pres_ids`,
`words`, `nodes`, `path_len`), `rankn_..._r<R>.npz` (`pres_ids`, `nodes`, `path_len`,
`base`; `meta` and `combos` only for side checks). The committed `*_class_view.json` is
read only as the thing to compare against. The `_inv` files are not used (see below).

## Checks (one set per file, named `<stem>:<check>`)

| check | what is compared |
|---|---|
| `inputs` | Prerequisites of the recomputation. Control: every pres_id 0..639 has exactly one row, its `r1`/`r2` strings equal the dataset line (2 per row), `solved` is a boolean with an integer node count (1 per row). Each length file: `pres_ids` is a permutation of 0..639, `nodes`/`path_len` are [640, len(words)], `words` are distinct. Rank n: the same, `base` is [640, >=2] with column 0 in {0, 1}, `combos` has one row per column, `meta.rank` equals the file name. An unusable file is a mismatch here and is then treated as absent. |
| `classes` | `presentations` (640), `n`, `sizes`, `twin_pairs`, `twin_relabelings`; any other key in the block or at top level is a mismatch. |
| `classes.class_of` | Compared as a partition, 640 items: for each presentation the set of its copies must be the same set. Labels are ignored. A missing or non pres_id key is a mismatch. |
| `noise_threshold` | Equals 0.17. |
| `noise.control` | The gap statistics over the twin pairs on the control. |
| `noise.starts` | Rank 3: one entry per length file present, two-sided (a present file without a committed entry is a mismatch; a committed entry whose file is absent is listed as skipped). Rank n: the block must be `{}` (1 item). |
| `rows` | Rank 3: rows matched by `name`, each with `name`, `starts`, the 9 presentation counts and the 6 class counts. Rank n: exactly one row; `starts` = number of columns of `nodes`. |
| `boundary_17pct(report only)` | Never a mismatch. Per row: how many presentations (control solves and some start solves) have `100*best == 83*control_nodes`, how many of those the float test counts as beyond noise, and how many presentations the float test classifies differently from the exact integer test `100*best < 83*c_nodes`. `compared` is the number of presentations looked at. Also under `info` in the output. |

Integers must be equal, floats within 1e-9 (absolute). Comparison is two-sided: a key
the definitions produce and the JSON lacks, or the reverse, is a mismatch.

The output JSON also carries `recomputed` (everything this script computed, including
its own `class_of`), `info`, `compared_total`, `checks_that_compared_0`, `errors`.

## How each number is recomputed

- **Dataset.** Line p is presentation p. Each half of the list, zeros dropped, is a
  relator as a tuple of signed letters.
- **Classes.** For a relabeling f and a presentation p, key(f, p) = the sorted pair of
  canon(f(r1)), canon(f(r2)), where canon(w) is the smallest of all rotations of w and
  of w^-1. a and b are copies iff key(f, a) == key(identity, b) for some f. Classes come
  from a union-find over that relation. As a self-check the same partition is rebuilt as
  "minimum of key(f, p) over the 8 relabelings"; the 8 relabelings are a group (all signed
  permutations of two letters), so the two must agree, and a difference raises (bug in
  this script, exit 1).
- **Twin pairs.** Per class, members by pres_id, all a < b; relabeling = first f in the
  task's order with key(f, a) == key(identity, b).
- **Gap statistics.** As written in the task: gap = |na - nb| / max(na, nb) in float64
  on the both-solved entries, `np.mean(gap == 0)`, `np.median`, `np.quantile(., 0.9)`,
  `np.quantile(., 0.99)`. `nodes` is cast to int64 before the subtraction.
- **Start noise.** Per length file and per twin pair (a, b, f): the columns k whose
  translated word f(words[k]) is itself in `words`, paired with that entry's column in
  the row of b.
- **Rows.** best[p] = fewest nodes over the columns with `path_len >= 0`; rank 3 keeps a
  running minimum over the length files in ascending length. The 9 + 6 counts are
  plain Python loops over the 640 presentations and the classes, exactly the task's
  formulas; `cheaper_beyond_noise` uses `float(best) < float(c_nodes) * (1 - 0.17)`.

Hand check of the reading, no code run. The word lists were read with jq from the
`word_index` / `z_word` fields of `..._b1000_cap24_L1_sample.jsonl` and `_L2_sample.jsonl`:
length 1 is [x, y], length 2 is [xx, xy, yx, yy, yX, Xy]. With "f(w) is literally in
`words`", length 1 gives 320 x 1 pairs for `x->x,y->Y` plus 0 + 1 + 1 + 2 for the four other
relabelings = 324, the committed `starts["1"].pairs`; length 2 gives
320 + 4 + 3 + 3 + 2 = 332, also the committed number. Also read with jq: the control
files have 554 and 606 solved rows (the committed `control` counts), 640 distinct
`pres_id`, and no row where `n2_*` or `null_*` differs from `solved` / `nodes_explored`.

**An `inputs` mismatch is not a class-view mismatch.** The `inputs` check is a
prerequisite added by this script (it is not one of the task's comparisons). It still
counts toward exit 3, because a control row whose `r1`/`r2` text differs from the dataset
line means the pres_id alignment the class view relies on is in doubt. Read it as "the
input data is inconsistent", not as "a number in `class_view.json` is wrong".

## Assumptions and ambiguities resolved

1. **No reduction of the relators.** "Up to rotation and inversion" is taken literally on
   the dataset words; nothing is freely or cyclically reduced first. `info.classes`
   reports how many relators are not reduced and whether reducing first would give the
   same classes.
2. **Direction of a twin relabeling.** f is applied to a (the smaller pres_id) and must
   give b. Counts cannot tell `x->y,y->X` from its inverse `x->Y,y->x` (one pair each in
   the committed files), but the start-noise pairing can.
3. **Unordered pair** {r1, r2} is compared as a multiset (sorted pair of canonical forms).
4. **Gap with 0 nodes on both sides** (|0 - 0| / max(0, 0)) is read as gap 0; the number of
   such entries is reported in the check's detail. Not expected to occur.
5. **Rank 3 row n** = all words of the length files that are present with length <= n. If a
   length below n is missing the row is still computed and compared, and
   `rows.detail.length_gap_before` says so. A committed row or `starts` entry whose own
   length file is absent, unreadable or past the time box is listed in `skipped`.
6. **`_inv` files are ignored.** The committed `starts` values (2, 8, 26, ...) are the sizes
   of the forward families only, and the task says a word whose image is the inverse of a
   stored word contributes nothing.
7. **`sizes` and `twin_relabelings`**: a name that is absent counts as 0 on either side.
8. **Rank-n row name** is not defined in the task. Only its numbers are compared: the
   integers in the name must be (`extra_generators`, `max_word_len`, rank) from `meta`.
   That format was learned from the committed file, so this one item is not independent.
   The rank-3 name `words up to length n` is compared as a string.
9. **Rank-n alignment.** `base` rows are taken in the same order as `nodes` (row i is
   `pres_ids[i]`); control solved = `base[:, 0] != 0`.
10. **Control rows are indexed by `pres_id`**, not by line (the file is not in pres_id order).
11. **Exit codes.** 0 no mismatch; 3 some mismatch, and also when nothing was compared
    with a committed class view (`inputs` and the report-only check do not count; a run
    that verified nothing must not look like a pass); 1 when the dataset
    cannot be read, a committed JSON or control file does not parse, or any other
    exception in one of the four files (the other files are still processed and written).
    A single check that compared 0 items prints `COMPARED 0 (not a pass)` and is listed in
    `checks_that_compared_0`.
12. **`workers` is unused** (no search). `minutes` is checked before each result file; files
    not reached are listed as skipped.
13. `words`/`meta` are loaded with `allow_pickle=False`; only if numpy refuses (object
    array) are those two reloaded with pickle allowed. All other arrays never use pickle.
14. Memory: one length file at a time (`nodes` uint16, `path_len` int16, one bool mask);
    the int64 work is done in 4,096-column chunks.

## Things that looked odd in the definitions or data

- **The 17% line is a float test.** `best < c_nodes * (1 - 0.17)` depends on rounding when
  `100*best == 83*c_nodes`. The report-only check counts those presentations and whether
  any is classified differently from the exact integer test.
- **0.17 is below the measured p90 in several rows of the same files.** Budget 10,000:
  p90 gap is 19.1% (length 1), 28.6% (length 2), 19.1% (length 4), 20.3% (length 6).
  Budget 1,000: 18 to 20% at lengths 6 to 9. So `cheaper_beyond_noise` is "beyond the
  typical renaming gap", not "beyond 90% of renaming gaps" at every length. The p99 gaps
  are 30% (control) to 87% (starts).
- **The start-noise sample is a small, structured subset.** A word is paired only when its
  image is the stored member of its {w, w^-1} pair. At length 9 that is 743,364 pairs out
  of 324 x 39,366 = 12.75 million (about 6%). For lengths 1 to 6 at budget 1,000 the
  `_inv` files would allow pairing the rest; the definition does not use them.
- **Twin pairs are not independent**: the one class of four contributes 6 of the 324 pairs.
- `control.jsonl` is not sorted by `pres_id` (harmless once indexed by id).
- The rank-n class views repeat the rank-3 budget-1,000 control noise exactly
  (324 / 0 / 281 / 0.6584), as expected if `base` is the same control; this script
  recomputes it from `base`, so a difference between `base` and `control.jsonl` would not
  show here. (Inside `control.jsonl` the `n2_*` and `null_*` copies equal the control on
  all 640 rows at both budgets.)
- The output's `compared_total` counts only items compared with a committed class view;
  `input_items_checked` counts the prerequisite items.

## Second tester

Read line by line against `BRIEF.md` and `TASK_class_view.md`; never run (only the
`ast.parse` syntax check, which passes after the last edit). Not read: any file on the
independence list, the other `indep_*.py`, `rank3/words.py`, any `.npz`.

**Verdict on the first version.** Every definition of the task maps to code that computes
it: the 8 relabelings in the task's order, "first that maps a onto b" (`keys[a][j] ==
keys[b][0]`), twin pairs a < b by pres_id, gap = |a - b| / max in float64 after an int64
cast, `np.median` / `np.quantile` default (linear), start-noise pairing (a, w) with
(b, f(w)) only when f(w) is literally in `words`, cumulative best/any per pres_id through
`row_of`, the 9 + 6 counts, the float test `best < c_nodes * (1 - 0.17)`, `base[:, 0/1]`
for rank n. No uint16/int16 arithmetic anywhere (every `nodes` slice is cast to int64
first, the boundary test uses Python ints, `path_len >= 0` is the only use of `path_len`).
No O(cells) Python loop: the per-word Python work is one `str.translate` + dict lookup per
(relabeling used, word), cached per relabeling (5 relabelings x 39,366 words at length 10,
twice with the report-only pass, about 0.4 million simple operations); everything per cell
is numpy in 4,096-column chunks. Expected run time: well under a minute; memory under
300 MB. No crash or wrong-number bug was found; the changes below are about what is
compared, the exit code, and diagnosis.

### Changes (line numbers of the edited file)

1. **A cumulative row with a missing lower length is no longer compared** (lines 945-948,
   968-982, 1076-1077). Before, with `L3` absent and `L4` present, row "up to length 4" was
   built from lengths {1, 2, 4} and compared: a guaranteed false mismatch (and the old test
   only flagged the first length after the gap, not the later ones). The task defines the
   row over all lengths 1..n, so it is undefined there. Now such a row is listed in
   `skipped`, kept under `report_only`, and a committed row of that length is neither a
   mismatch nor compared. `noise.starts[n]` is still compared (it needs only its own file).
   Supersedes assumption 5 above.
2. **Exit 3 when any comparison check compared nothing** (lines 1385-1392; listed in the
   JSON as `comparison_checks_that_compared_0_(exit_3)`). Before, the run exited 0 as long as
   one item anywhere was compared, e.g. with every `.npz` missing but the `class_of`
   partition equal. Prerequisite (`inputs`) and report-only checks do not count. This is
   stricter than `BRIEF.md`'s three codes on purpose; in the expected run (four class
   views, their control/length/rank-n files) no comparison check compares 0. Supersedes
   assumption 11 above.
3. **`report_only` key in the output JSON** (never compared, every block in `try/except`
   so it cannot crash or change a compared number):
   - `classes.twin_pairs_by_number_of_relabelings_that_map_a_onto_b`: if this is
     `{"1": 324}` the "FIRST one in the order" rule never has a choice to make.
   - `classes.twin_pairs_whose_relabeling_is_not_its_own_inverse` and
     `classes.twin_relabelings_if_the_relabeling_is_the_first_that_maps_b_onto_a`: the two
     pairs where the direction matters (expected: 31/179 and 57/177).
   - `<rank-3 stem>."noise.starts_if_the_twin_relabeling_is_the_first_that_maps_b_onto_a"`:
     per length, the full start-noise statistics with (a, w) paired with (b, g(w)), g the
     first relabeling that maps b onto a, plus `identical_to_the_compared_reading`. A
     start-noise mismatch that this block reproduces is a direction difference, settled in
     one run.
   - `<rank-3 stem>.rows_from_the_available_lengths_when_a_lower_length_is_missing`: see 1.
   - `<rank-n stem>.if_row_i_of_base_is_presentation_i`: only when `pres_ids` is not
     0..639 in order (flag `pres_ids_is_0_to_639_in_order` in the `inputs` detail);
     otherwise the two readings of the row order of `base` are the same thing.
   - the boundary block of each row now also carries `cheaper_beyond_noise` by the exact
     test `100*best < 83*c_nodes` next to the float test of the task (lines 599-600, 630-631).
4. **Stale class view is named in the detail** (lines 1035, 1064): the lengths whose file
   is present but that the committed JSON does not have are listed in
   `length_files_present_without_a_committed_entry` / `rows_recomputed_without_a_committed_row`.
   Still a mismatch, as the task says ("one entry per length file present").

### Checked by hand or with jq (no numpy, no `.npz`)

- Control `r1`/`r2` of all 640 rows equal the dataset line, both budgets (jq + `cmp`): the
  `inputs` check cannot give a false mismatch on the committed control files. `solved` is a
  boolean and `nodes_explored` an integer >= 3 on every row; neither file is in pres_id order.
- All 1,280 relators are freely and cyclically reduced (jq), all 640 lines have 48 entries:
  assumption 1 (no reduction) changes nothing on this dataset.
- The stored length-3 family (18 words, from `L3_sample.jsonl`) under the five relabelings
  of the committed `twin_relabelings`: 5 words keep their image in the family under
  `x->x,y->Y`, 14 under `x->y,y->x`, 9 under `x->y,y->X`, 9 under `x->Y,y->x`, 4 under
  `x->Y,y->X`: 320 x 5 + 14 + 9 + 9 + 4 = 1,636 = the committed `starts["3"].pairs`. With the
  first tester's lengths 1 and 2 (324, 332) the pairing rule "f(w) literally in `words`"
  gives the committed pair counts at lengths 1 to 3.
- With the committed `class_of` as the partition, jq (|a - b| / max, sorted, linear
  interpolation at q x (n - 1)) gives the committed `noise.control` to the last digit at
  both budgets (324 / 0 / 281 / 0.6583629893238434 / 0 / 0.15384615384615385 /
  0.3039466265739511 and 324 / 0 / 307 / 0.6058631921824105 / 0 / 0.15384615384615385 /
  0.31923845755315394). So the gap formula and the quantile method are read the same way.
- `..._b1000_cap24_L1_sample.jsonl` holds every solved length-1 search (769 rows, 403
  presentations = the committed `some_start` of row 1), so length 1 could be redone in jq
  with the committed `class_of` and the relabelings above: `noise.starts["1"]` comes out as
  324 / 5 / 203 / 0.8719211822660099 / 0 / 0.011158686908005751 / 0.42066957787481807 and
  row "words up to length 1" as all 9 + 6 committed counts. Both directions of the two
  non-involutive pairs give the same numbers at length 1 (x and y cost the same on 31, 57,
  177, 179), so length 1 does not settle the direction; the `report_only` block will.
- The class of four (31, 57, 177, 179) by hand: no non-identity relabeling fixes
  presentation 31, so the dataset holds 4 of the 8 relabelings of that problem and each of
  its 6 pairs has exactly one relabeling: `x->x,y->Y` twice, `x->Y,y->X` (31 to 177),
  `x->y,y->X` (31 to 179), `x->Y,y->x` (57 to 177), `x->y,y->x` (57 to 179), the committed
  counts. Presentation 0 has no symmetry either, so its pair (0, 1) has one relabeling.

### The first tester's assumptions against the task

| # | assumption | task |
|---|---|---|
| 1 | relators not reduced first | silent; no effect here (all reduced), flag in `info.classes` |
| 2 | f is applied to a and gives b | stated ("maps a onto b", "(a, w) with (b, f(w))"); other direction now under `report_only` |
| 3 | unordered pair = sorted pair of canonical forms | stated |
| 4 | 0/0 gap read as 0 | silent; cannot occur (a solved search pops at least 1 node; control minimum is 3), counted in the detail |
| 5 | row n from the lengths present <= n | silent when a lower length is missing: changed, see change 1 |
| 6 | `_inv` files not used | stated for start noise; for rows the committed `starts` (2, 8, 26, ...) is the forward family only |
| 7 | absent count name = 0 | silent; equal in meaning, and the script never emits a 0 itself, so it stays two-sided |
| 8 | rank-n row name: only its numbers | silent; learned from the committed file, disclosed |
| 9 | `base` row i is `pres_ids[i]` | silent; flag + other reading under `report_only` |
| 10 | control indexed by `pres_id` | stated in the brief |
| 11 | exit codes | changed, see change 2 |
| 12-14 | workers unused, pickle fallback for `words`/`meta` only, chunked int64 | fine |

### Risks left and ambiguities not resolved

- **Stale class view = exit 3.** The class views committed in the repo today stop at
  length 9 (budget 1,000) and 6 (budget 10,000). If the results directory on the machine
  holds `L10` / `L7` files and class views that were not regenerated after them, each such
  length gives 2 mismatches ("the length file is present but the committed JSON has no
  entry / row"). That is what the task defines, not a bug of either side: regenerate the
  class views first, or read those two lines as "stale", not "wrong".
- Nothing was executed. Numpy behaviours relied on and not testable here: `words` loads
  with `allow_pickle=False` (a `<U` array; object arrays fall back to pickle),
  `np.where(bool, int64, python int 2**63-1)` stays int64, `np.quantile` default method.
- `noise.starts` beyond length 3, every `rows` count and both rank-n rows could not be
  hand-checked (they need the arrays).
- The rank-n control noise is recomputed from `base`; a `base` that differs from
  `control.jsonl` is not this script's check (unchanged from the first version).
- "Per file" in the task's boundary report: the script gives the count per row, and the
  last row in the one-line summary.
- `BRIEF.md` does not say what the exit code is when one check compared 0 and the others
  passed; change 2 picks 3.
