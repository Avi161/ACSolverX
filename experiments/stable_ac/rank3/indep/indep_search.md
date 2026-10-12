# indep_search.py: notes

Independent re-implementation of the experiment's greedy best-first search
(any rank), used to re-run stored cells and compare `(solved, nodes, path_len)`.

    python3 indep_search.py <RESULTS_DIR> <DATASET> <OUT_JSON> [workers=1] [minutes=30]

**Status: never executed.** Only the `ast.parse` syntax check was run (it
passed, under the local Python 3.14 parser; the code uses nothing newer than
3.8 syntax). Its first real run is the one on the AWS box. A start-up self-test
(below) is the guard against a slip in the optimized code.

## What I read

- `experiments/stable_ac/rank3/PLAN.md` (definitions, section 2; arms and deviations for context).
- `experiments/stable_ac/solvern.py` (the slow reference), to pin down what the prose leaves open. Not imported, not pasted.
- The examples in `schema/` and `post_preview/` for file formats.
- Not read: `solvern_fast.py`, `run_rank3_bf.py`, `rankn_bf.py`, `words.py`, `run_baseline`, and every file the brief forbids.

## The search, as implemented

State: the list of relators, each cyclically reduced and replaced by a
canonical representative, the list sorted. Best-first on a heap keyed
`(total length, depth, tie-break)`. Loop: while the heap is not empty and
`nodes < budget`: pop, `nodes += 1`, if every relator has length 1 return
solved with `path_len = depth`; otherwise generate children. A child replaces
relator i by `reduce(rot(r_i) · rot(r_j^±1))` for j != i and every pair of
rotations whose seam cancels (last letter of the first factor inverse to the
first letter of the second); it is dropped if any of its relators is longer
than the cap; it is pushed only the first time its state is seen, at depth + 1.

Two implementations live in the script:

- `search`: the one used for the comparison. Words are `bytes` in a code where
  byte order is the canonical-form order; the tie-break is one
  `join + translate`. Per (target, partner) pair of words the set of new
  canonical target words is memoised (`PAIR`), as is word -> canonical word
  (`CANON`). The free reduction of `rot(r_i)·rot(r_j^±1)` is done as seam
  cancellation only, which is exact because both factors are rotations of
  cyclically reduced words (every relator of a state is).
- `naive_search`: a literal transcription on tuples of signed ints, no caches,
  full stack reduction, explicit key functions. Used for the self-test and to
  re-run up to 2 mismatching budget-1,000 cells per worker, so that a mismatch
  row in `first_mismatches` shows `stored`, `mine` and `own_naive_rerun`.

## Details I could only get from the code, not from the prose

1. **Canonical relator**: the least word among all rotations of w *and of
   w^-1*, in the letter order `(-|g|, g>0)`: higher generator index first,
   inverse before generator (`Z<z<Y<y<X<x`; rank 5: `B<b<A<a<Z<..`).
2. **Relator list order**: sorted by `(length, that same letter order)`.
   A state is this sorted tuple; move indices refer to it.
3. **Tie-break** (third heap field): the state compared relator by relator in
   its sorted order, letters ordered `(g>0, |g|)`: every inverse letter below
   every generator, by index inside each block; a word that is a prefix of
   another sorts first. For rank 3 this is ASCII order of `XYZxyz`. For rank
   4 and 5 it is **not** ASCII order of the rendered letters (`x y z a b`):
   the code orders by generator index (`X<Y<Z<A<B<x<y<z<a<b`). I follow the
   code.
4. **Reduction**: free reduction of the whole concatenation (it can give the
   empty word), then strip cancelling end pairs.
5. **Rotations**: `np.roll` right rotations, `rot_k(w) = w[-k:] + w[:-k]`,
   loops in the order i, j, sign (+1 then -1), k1, k2. The inverse is of the
   stored canonical `r_j`.
6. **Order of children does not matter** for `(solved, nodes, path_len)`:
   all children of one pop get the same depth and the same parent, and heap
   order depends only on `(total, depth, state)`, never on push order. It only
   changes which move string is recorded. (My pair cache keeps the reference's
   first-seen order anyway.) The prose and the task text suggest it matters.
7. **Cap**: per relator only, no cap on the total; an inherited relator over
   the cap also drops the child. Never triggered here: dataset relators are
   padded to 24 = cap and `Z·w` has at most 11 letters.
8. **Empty relator**: a relator that cancels to the empty word is kept
   (length 0, sorts first); afterwards it is skipped as target and as partner,
   and such a state is never terminal ("every relator has length 1", not
   "total = n").
9. **Counting**: a node is counted when popped, before the terminal test; the
   terminal pop counts. The budget test is `nodes < budget` before the pop.
   A terminal state that was generated but not popped when the budget ran out
   is **unsolved**. The brief's "reached within the budget" does not say this.
10. **Visited at generation**, first discovery wins; depth is never lowered.
    `path_len` is therefore the depth of the terminal state at its first
    discovery (an exact identity with the length of the reference's parent
    chain; I keep a set, not a parent map). It is not a shortest path.
11. **Start**: the given relators are reduced, canonicalised and sorted
    before the search; depth 0.
12. **Stabilised start**: relator `(-(2+i),) + w_i` (from the brief; the code
    agrees for rank 3).

## Checks

| name | what |
|---|---|
| `selftest_fast_vs_naive` | `search` against `naive_search` on 22 small starts (ranks 2 to 5, an unreduced start, a start over a small cap, duplicate relators, a relator that cancels to empty). Budgets 40 to 60, edge cases first, 20 s limit. A failure here means the script, not the data, is wrong; a crash of the self-test counts as one mismatch. |
| `control_b1000` | all rows of `..._control.jsonl`: my rank-2 search of dataset line `pres_id` against `(solved, nodes_explored, path_length)`. |
| `control_b1000_n2_copy` | extra, free: the same runs against `(n2_solved, n2_nodes, n2_path_length)`. |
| `control_b1000_relators_vs_dataset` | extra: `r1`, `r2` strings of each row equal the dataset line. |
| `extra_rank3_null_b1000` | extra, 30 rows: rank-3 start `<r1, r2, Z>` against `null_*` of the control file. |
| `rank3_b1000_L<n>` | 150 random (row, word) cells of each length file present. |
| `rank3_b1000_L<n>_inv` | 40 random cells of each `_inv` file present. |
| `rank3_b1000_L<n>_inv_words` | extra: `words[k]` of the `_inv` file is the inverse of `words[k]` of the forward file. |
| `rank4_b1000`, `rank5_b1000` | 200 random (row, combo) cells each. |
| `rank4_b1000_null`, `rank5_b1000_null` | 30 random rows each, start `<r1, r2, Z1, .., Zk>` against the `null` array. |
| `rank3_b10000_L<n>` | 15 random cells of each budget-10,000 length file present. |
| `meta_params` | budget, cap (and rank, k) recorded in each file equal the file name's (a file that does not record them fails); the control file has one row per dataset line. |

Output also has `kinds` (planned / compared / equal per kind: `control`,
`rank3_b1000`, `rank3_b1000_inv`, `rank4`, `rank4_null`, `rank5`,
`rank5_null`, `rank3_b10000`, `extra_rank3_null`), printed as `KIND ...` lines.
`mismatches` is the sum over `checks`.

## Sampling, order, time box

- `master = random.Random(12345)`. One sub-generator
  `random.Random(master.getrandbits(64))` per expected file, drawn in this
  fixed order whether or not the file exists, so a missing file does not move
  the other samples: control order; b1000 L1..L10; b1000 inv L1..L10; rank 4
  cells, rank 4 nulls; rank 5 cells, rank 5 nulls; b10000 L1..L10; rank-3
  null extra.
- Cells: `rng.sample(range(rows*cols), n)`, `divmod` by cols. Control: all
  rows, in a shuffled order (a time-out leaves a random subset, not the easy
  prefix).
- Interleave: job j of a group of m gets position j/m, groups sorted
  together. The first job of every group runs first; any prefix of the run
  holds about the same share of every group.
- `multiprocessing` fork context, `Pool(workers)`, `imap_unordered(...,
  chunksize=1)`, polled with a 2 s timeout; at `minutes` the pool is
  terminated and the report is written with `stopped_early` set and
  "not run N" per check.
- Workers read no files; the parent reads one file at a time and keeps only
  the sampled cells.

## Assumptions and readings chosen

- Presentation relators always come from the dataset line `pres_ids[i]` (or
  the control row's `pres_id`), not from row position.
- Rank 4/5: column t of a `combos` row is the word of generator 3 + t.
  The assignment matters for tie-breaks, so a different pairing in the runner
  would show up as mismatches.
- `_inv` files: the word searched is `words[k]` as stored in the `_inv` file.
  If that file stored the forward words, `..._inv_words` fails and so do the
  cells.
- Stored "no path": `null` or -1, both read as -1. An unsolved row with any
  other path length, or a solved row with none, is a mismatch.
- npz cells: `solved` is `path_len >= 0` (the files hold no separate flag), so
  the comparison is really `(nodes, path_len)` there.
- The search uses the budget and cap recorded in each file (`meta`, control
  row); `meta_params` fails if they differ from the file name.
- Exit code 1 (not 0) when no search at all was compared, or when a worker
  job raised; 3 when any check has a mismatch.
- A file that cannot be read as described counts as one mismatch with
  `compared 0`.

## Things that looked off

- The control file's main triple comes from the 2-generator baseline
  (`run_baseline.greedy_search`), which I did not read. My rank-2 run follows
  `solvern` semantics; PLAN states the two agree node for node.
- `pres_ids` is `<i4` in the rank-3 example and `<i8` in the rank-5 example;
  the brief says int32. Harmless.
- PLAN section 2 says states are "compared as strings"; for rank 4 and 5 that
  is only true in the generator-index alphabet (item 3).
- Worst-case memory is the search's own frontier: a budget-10,000 cell that
  is not solved can hold a few hundred MB in one worker.

## Review

Reviewer pass, 12 Oct 2026. The script was read line by line against the
brief, the task, `PLAN.md` section 2 and `solvern.py`. It was **not executed**
(no local compute); only the `ast.parse` syntax check was re-run after the
edits, and it passed. Everything below is from reading.

### Read and found correct (no change)

- `search` and `naive_search` against `solvern.search_n`: letter code and
  canonical form (byte order = `(-|g|, g>0)`), state sort `(length, word)`,
  tie-break bytes (`|g| + 64*(g>0)`, 0 separator), pop / count / terminal test
  order, `nodes < budget`, per-relator cap with the inherited-relator guard,
  empty relators skipped as target and partner, visited at generation,
  `path_len` = depth. Seam-only cancellation in `expand_pair` equals the
  reference's full free reduction because both factors are rotations of
  cyclically reduced words; the cyclic strip has the same strict bound.
- The claim that child order cannot change `(solved, nodes, path_len)`: the
  tie-break bytes determine the state, so heap order is a total order that
  does not depend on push order.
- numpy handling: every cell is converted with `int()` before any comparison
  or arithmetic (no uint16 / int16 wrap), words go through `str()`, nothing
  numpy reaches the JSON. `allow_pickle=False` is enough for the `<U` arrays
  in the two example files.
- Keys and shapes against `schema/`: control keys, `<stem>_L2.npz` members and
  dtypes, `rankn_..._r5.npz` (`combos` int16 [120, 3], `null` int32 [640, 3],
  `meta` with `words`, `rank`, `extra_generators`, `node_budget`,
  `max_relator_length_cap`), dataset lines (valid JSON lists, 2 x 24).
- Time box: polled every 2 s, `pool.terminate()` at the deadline, planning and
  the self-test are inside the box.

Two hand replays (by reading, no code run) agree with stored rows under the
script's definitions:

- `L2_sample`, presentation 0, w = `xx` and w = `yx`: the greedy pops 5
  nodes, path 4, and the moves are the stored `path_moves`.
- `r5_sample_paths`, presentation 0, index 52 (`y`, `xy`, `yX`): the stored
  6 moves are legal and end trivial with column t of `combos` on generator
  3 + t (`Zy`, `Axy`, `ByX`). With the columns reversed the second stored
  move has no cancelling seam. So the column-to-generator reading is right
  at least for this row.

### Changes

1. **`meta_params` could pass on nothing.** A rank-3 file with no readable
   `meta` was dropped from the check and searched with the file name's
   budget and cap, silently. Now every file read adds one entry, and it
   fails unless `node_budget` and `max_relator_length_cap` are recorded and
   equal the file name's. The rank-4/5 entry likewise requires `rank`,
   `extra_generators`, `node_budget`, `max_relator_length_cap` to be present
   (missing keys used to fall back to the expected value and pass).
2. **Control row count was reported, not checked.** "All 640 rows" was
   whatever the file held. `meta_params` now has an entry that fails unless
   rows = distinct `pres_id` = dataset lines.
3. **Mismatches with no example.** `control_b1000_relators_vs_dataset` and
   `rank3_b1000_L<n>_inv_words` counted mismatches but put nothing in
   `first_mismatches`. Each now adds up to 3 examples.
4. **One line per check.** A job traceback inside a check's `detail` printed
   as several lines; the printed summary now flattens newlines (the JSON
   keeps them).

No change to either search, the sampling, the job order or the exit codes.

### Doubts not settled

- **Never run.** A name error or a wrong call signature that `ast.parse`
  cannot see would show only on the box (exit 1). I found none by reading.
- **Unsolved encodings.** Assumed: control `path_length` is `null` (or -1)
  on unsolved rows, and `null[:, 2]` in the rank-4/5 files is -1. The
  examples only show solved rows. Another encoding would show up as
  mismatches on exactly the unsolved rows.
- **Exit 0 with uncovered checks.** After a time-out a check that compared 0
  is labelled `COMPARED 0 - NOT A PASS` in its detail and in the KIND lines,
  but the exit code is 0 as long as some search was compared and nothing
  mismatched. Read the per-check lines, not the exit code alone. Exit 1 for
  "no search compared" or "a worker job raised" is the author's reading of
  the contract; I kept it.
- **Memory.** One unsolved budget-10,000 search can hold 1 to 3 million
  states (my estimate, about 300 bytes each), and the slow jobs pile up on
  the workers, so most of 8 workers can be in one at once: several GB in
  total. Should fit in 16 GB; not measured. If a worker is OOM-killed its
  job never returns and the script idles until `minutes`, then reports the
  job as not run.
- **Speed.** "About 1 s per budget-1,000 search" is the author's estimate.
  At that rate the roughly 3,000 budget-1,000 jobs plus about 105
  budget-10,000 jobs need 4 or more workers to finish in 30 minutes; with
  fewer the interleaved order still covers every group.
- **Exit 3 for an unreadable file.** A result file that is present but cannot
  be read as described is caught and counted as one mismatch (`compared 0`),
  so the exit code is 3, not 1. The brief's "1 on a crash" can be read either
  way (the script did not crash). The author's choice names the file in a
  check line; I kept it.
- **Naive re-runs.** Up to 2 per worker on mismatching budget-1,000 cells.
  Not timed; a full budget-1,000 naive run is probably tens of seconds to a
  few minutes (my estimate, more in rank 5). Bounded at 2 per worker, but
  with mismatches on every worker it can cost several worker-minutes of the
  box.
- **Self-test.** Both searches are by the same author, so it only guards
  the optimised one against slips; it takes up to about 20 s of the box and
  a failure there makes the exit code 3 without any data being wrong.
- **Control solver.** The control's main triple is from the 2-generator
  baseline, which neither the author nor I read. `control_b1000_n2_copy`
  compares the same runs with the rank-n solver's columns.
