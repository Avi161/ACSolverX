# Task: `indep_class_view.py` (relabeling classes and the noise between copies)

Read `BRIEF.md` first; its hard rules and script contract apply. In addition
to its list, do NOT read `experiments/stable_ac/rank3/class_view.py`,
`tests/stable_ac/test_rankn_class_view.py`,
`experiments/equivalence_classes/lib/words.py` or the other `indep_*.py`
scripts. You may read the result files in `REPO/results/stable_ac/rank3_bf/`
(text files directly; never open an `.npz` on this machine).

Recompute, from the raw arrays and the dataset only, every number in
`<stem>_class_view.json` for both rank-3 budgets (stem
`rank3_bf_ms640_b<B>_cap24`) and in
`rankn_bf_ms640_b1000_cap24_r<R>_class_view.json` (R = 4, 5), and compare.
Integers must be equal; floats within 1e-9.

## Definitions

**Class of copies.** A signed relabeling sends x to fx and y to fy with
(fx, fy) one of, in this order: (x,y), (x,Y), (X,y), (X,Y), (y,x), (y,X),
(Y,x), (Y,X); inverses follow (X goes to fx^-1). Its name is the string
`x->{fx},y->{fy}`. Two presentations are copies when some signed relabeling
maps the unordered pair {r1, r2} of one onto the other's, each relator taken
up to rotation (cyclic shift) and inversion. Classes are the equivalence
classes of the 640 presentations under "is a copy of".

**Twin pairs.** Within each class take the members in dataset order
(pres_id ascending) and every pair (a, b) with a before b. The pair's
relabeling is the FIRST one in the order above that maps a onto b.

**Gap statistics** of two aligned lists of searches (solved flags sa, sb and
node counts na, nb): `pairs` = length; `solved_flag_differs` = count of
sa != sb; `both_solved` = count of sa and sb; on the both-solved entries, with
gap = |na - nb| / max(na, nb) in float64: `same_nodes` = mean of (gap == 0),
`gap_median`, `gap_p90`, `gap_p99` = numpy median and quantile (default linear
interpolation) at 0.9 and 0.99. With no both-solved entry only the three
counts exist.

**Control noise** (`noise.control`): the gap statistics over the twin pairs,
searches = the control of a and the control of b. For the rank-3 files the
control comes from `<stem>_control.jsonl` (`solved`, `nodes_explored`); for a
rank-n file from its `base` array (column 0 solved, column 1 nodes).

**Start noise** (`noise.starts["<n>"]`, rank 3 only, one entry per length file
present): for every twin pair (a, b, relabeling f) and every word w of the
file's `words` whose image f(w) (letter by letter) is itself an entry of
`words`, pair the search (a, w) with the search (b, f(w)); gap statistics over
all such pairs of that length. Words whose image is not in `words` (it is the
inverse of a stored word) contribute nothing.

**Rows** (`rows`). Rank 3: one row per length n present, cumulative: the starts
of a presentation are all words of lengths 1..n (`starts` = their number,
`name` = "words up to length n"). Rank n: one row, the starts are all columns.
With best[p] = fewest nodes over the SOLVED starts of p (none: no start
solves), c_solved[p], c_nodes[p] the control, and for a class K:
kc[K] = fewest control nodes over the copies the control solves, ks[K] =
smallest best[p] over its copies:

- `presentations`: `n`; `control` = count c_solved; `some_start` = count with a
  solving start; `gained` = some start solves and not c_solved;
  `gained_but_control_solves_a_copy` = gained and the control solves some copy
  in p's class; `lost` = c_solved and no start solves; `cheaper` = some start
  solves and (not c_solved or best[p] < c_nodes[p]);
  `cheaper_beyond_noise` = gained, or (c_solved and some start solves and
  best[p] < c_nodes[p] * (1 - 0.17), evaluated in float64 exactly as written);
  `cheaper_than_every_copy_of_control` = some start solves and (no copy in
  p's class is solved by the control or best[p] < kc[class of p]).
- `classes`: `n`; `control` = classes with a copy the control solves;
  `some_start` = classes where some start of some copy solves; `gained` =
  some_start and not control; `lost` = control and not some_start; `cheaper` =
  some_start and (not control or ks < kc).

`classes` block of the JSON: `presentations`, `n`, `sizes` (class size ->
number of classes), `twin_pairs`, `twin_relabelings` (name -> number of twin
pairs), `class_of` (pres_id -> class label; compare as a partition, labels are
arbitrary). `noise_threshold` must be 0.17.

Also report (not as a mismatch): how many presentations sit exactly on the
17% boundary (100 * best == 83 * c_nodes), per file.

Deliver `OUT/indep_class_view.py` and `OUT/indep_class_view.md`.
