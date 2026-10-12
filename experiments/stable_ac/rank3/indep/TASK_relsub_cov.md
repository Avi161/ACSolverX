# Task: `indep_relsub_cov.py` (relator subwords in rank 3, and the join with CoV)

Read `BRIEF.md` first; its hard rules and script contract apply. In addition
to its list, do NOT read `experiments/stable_ac/rank3/words.py`,
`experiments/stable_ac/rank3/class_view.py`,
`experiments/stable_ac/cov/cov_all.py` or the other `indep_*.py` scripts. You
may read `REPO/results/stable_ac/cov_all/README.md` and the text result files
in `REPO/results/stable_ac/rank3_bf/` and `REPO/results/stable_ac/cov_all/`
(look at a few lines of a `.gz` with `gzip -dc FILE | head -3`; never load a
whole file or open an `.npz` on this machine).

Recompute, from the raw files only, and compare with
`<stem>_summary.json` (stem `rank3_bf_ms640_b<B>_cap24`, B = 1000 and 10000):
the whole `relsub` block, `control_at_larger_budgets`, and the control columns
of `views["<B>"].gained_presentations_priced`. Integers equal; floats within
1e-9.

## Inputs

- `<stem>_relsub.jsonl` (on the box) or `<stem>_relsub.jsonl.gz` (as
  committed): accept either. Rows: `pres_id`, `z_word` (string), `is_proper`
  (bool), `solved`, `nodes_explored`, `path_length`, `r1`, `r2`.
- `<stem>_control.jsonl`: the control at budget B.
- `<stem>_L<n>.npz`: the brute-force arrays (needed only to find the
  presentations some word solves).
- The CoV sweep file. Default path
  `results/stable_ac/cov_all/cov_all_suballpxyb8_ms640_b100000.jsonl.gz`
  relative to the working directory (the script is run from the repo root);
  the environment variable `COV_FILE` overrides it. If absent, list every CoV
  check as skipped. One JSON row per search at node budget 100,000:
  `pres_id`, `is_control` (bool), `solved`, `nodes_explored`,
  `max_relator_length_cap`, and for non-control rows `z_word` (string; the
  word a CoV start was built from). Control rows have `z_word` null.

## Definitions

**fold(w)**: with x=1, y=2, X=-1, Y=-2, the larger of the integer tuples w and
w^-1 (ordinary tuple comparison). Report how many relsub `z_word`s are not
already their own fold (expected 0).

**Relator-subword word set of a presentation** (check the rows against it):
for each relator r (cyclically reduced, length |r|) and each length
2 <= l <= |r|, every window of length l of r written twice in a row, starting
at positions 0..|r|-1, folded. A word is `whole` if it arises with l = |r|
from either relator. The rows of a presentation must be exactly this set of
words, one row each, with `is_proper` = not whole (a word that is a whole
rotation of one relator is not proper even if it also sits strictly inside
the other).

**`relsub` block.** `rows`, `rows_proper` = counts. For `proper` (rows with
`is_proper`) and `all` (every row), over the presentations that have at least
one such row, with c_solved / c_nodes the control at budget B:
`solved_by_some_subword` = presentations with a solved row;
`gained_over_control` = those where the control is unsolved;
`mean_solve_rate` = mean over presentations of (solved rows / rows);
`some_subword_faster_than_control` = control-solved presentations with a
solved row of fewer nodes than the control;
`mean_fraction_faster_than_control` = mean over the control-solved
presentations of (solved rows with fewer nodes than the control / rows).

**CoV tables at budget B.** From the CoV file: its control rows give, per
presentation, (solved, nodes) at 100,000. For the non-control rows, with
w = fold(z_word): has_row[p] = set of w; a row counts as solved at B when
`solved` and `nodes_explored` <= B; cov_best[p] = fewest nodes over rows
solved at B; cov_by_word[p][w] = the same per word.

**`relsub.vs_cov`.** `cov_file_budget` = 100000; `cov_median_cap` = median of
`max_relator_length_cap` over ALL non-control CoV rows; `control` =
presentations the control solves at B; `rank3_subword_oracle` = presentations
with a solved proper relsub row; `cov_oracle` = presentations with a CoV row
solved at B; `control_or_rank3`, `control_or_cov` = unions; `rank3_not_cov`,
`cov_not_rank3` = set differences. Same-word join: over proper relsub rows
whose `z_word` is in has_row[p] (`same_word_pairs_joined`), with a = the row's
nodes if solved and c = cov_by_word[p][z_word] if present:
`same_word_neither` (no a, no c), `same_word_only_rank3_solves` (a, no c),
`same_word_only_cov_solves` (c, no a), `same_word_rank3_fewer_nodes` (a < c),
`same_word_tie` (a == c), `same_word_cov_fewer_nodes` (a > c).

**`control_at_larger_budgets`**: for b in 100, 1000, 10000, 100000, the number
of presentations whose CoV-file control row is solved with nodes <= b.

**`gained_presentations_priced`** (in `views["<B>"]`): the gained
presentations are those where some brute-force word (any length file present)
solves and the control at B does not. Check `gained_at_this_budget`,
`control_file_budget` (100000), `control_solves_them_at_file_budget`, and per
row `control_solved` and `control_nodes` (from the CoV file's control row).
Also check `best_word_nodes` per row (fewest nodes over the solving words) and
`best_word_cheaper_than_control` (rows where the control is unsolved at
100,000 or best_word_nodes < control_nodes).

**Cross-run check**: the CoV file's control rows cut back to B (solved and
nodes <= B) must agree with `<stem>_control.jsonl` on solved for every
presentation, and on nodes wherever solved.

Deliver `OUT/indep_relsub_cov.py` and `OUT/indep_relsub_cov.md`.
