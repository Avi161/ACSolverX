# Rank-3 brute-force baseline on MS640: plan

Written 12 Oct 2026 (UTC), before the sweep was launched. Later changes go in
[Deviations](#11-deviations), not into the sections above it.

## 1. Question

Does the standard greedy trivialize a Miller–Schupp presentation **more or less
quickly** when it is first stabilized with one extra generator,

    <x, y | r1, r2>   ->   <x, y, z | r1, r2, Z·w>,     w a word in x, y,

and searched in rank 3, than when it is searched in rank 2? Answered for
**every** word w up to a length L, on all 640 presentations of MS640, at a fixed
node budget, with nothing changed in the search except the rank.

This is the baseline a 3-generator method has to beat, and the baseline the
change-of-variables (CoV) work is measured against: CoV picks the same z = w,
substitutes, and then *eliminates* a generator to return to rank 2. Here the
generator stays.

## 2. Definitions

- **Search.** The Two-Hump greedy as implemented in `run_baseline.greedy_search`:
  best-first on total relator length (heap key `(total length, depth, state)`),
  moves `r_i <- rot_k1(r_i) · rot_k2(r_j^±1)` kept only when the seam cancels,
  cyclic reduction on, a child dropped when any relator exceeds the per-relator
  cap, cost counted in **nodes popped**. Rank n uses its port
  `solvern_fast.search_n_fast` (same children order, same canonical form, same
  tie-break). Terminal state: every relator has length 1.
- **Cap 24, budget 1,000.** The cap of the 2-generator control. The start
  relator `Z·w` has length |w| + 1 <= 11, far below it.
- **Stabilized start.** `<x,y,z | r1, r2, Z·w>` is the image of the plain
  stabilization `<x,y,z | r1, r2, Z>` under the free-group automorphism
  z -> z·w^-1: it presents the same (trivial) group, and since w lies in
  the normal closure of r1, r2 it is AC-equivalent in rank 3 to the plain
  stabilization. A rank-3 solve therefore certifies **stable** AC-triviality
  of `<x,y | r1,r2>` and nothing stronger. Every MS640 presentation is already
  known AC-trivial, so the question here is cost, not existence.
- **Null stabilization.** `w` empty: `<x,y,z | r1, r2, Z>`. `Z` shares no letter
  with r1, r2, so no move ever touches it and the rank-3 search is the rank-2
  search with one inert relator.

## 3. Arms

| Arm | Start | Rows on MS640 |
|---|---|---|
| control | `<x,y \| r1,r2>`, and the null stabilization | 640 |
| bf (brute force) | `Z·w` for every freely reduced w, 1 <= \|w\| <= L, one per `{w, w^-1}` | 640 · (3^L − 1) |
| inv | `Z·w^-1` for every w with \|w\| <= 6 | 640 · 728 |
| relsub | `Z·w` for every cyclic subword w of r1 or r2, 2 <= \|w\| <= \|r\| | about 10^5 |

**Brute-force family.** There are 4·3^(n−1) freely reduced words of length n
over {x, y, X, Y}. Renaming z -> z^-1 turns `Z·w` into a rotation of
`(Z·w^-1)^-1`, so w and w^-1 give isomorphic search graphs and one of each pair
is run: 2·3^(n−1) words of length n, **3^L − 1** up to length L.

| L | words per presentation | searches on MS640 |
|---|---|---|
| 6 | 728 | 465,920 |
| 8 | 6,560 | 4,198,400 |
| 9 | 19,682 | 12,596,480 |
| 10 | 59,048 | 37,790,720 |

Nothing else is folded. A rotation or conjugate of w, `w·r` for a relator r, and
the images of w under the 8 signed relabelings of {x, y} are different starts
for a fixed (r1, r2) and are all run.

The isomorphism under w -> w^-1 does not fix the heap tie-break (states are
compared as strings, and the renaming changes the order of `z` and `Z`), so node
counts can differ. The **inv** arm measures by how much, on every word up to
length 6. If the difference is not negligible the fold is reported as a
sampling choice, not as a symmetry.

**relsub** is the word set of the CoV sweep (`cov_all.subwords`, PR #26) plus
the full rotations of a relator, with the same representative `max(w, w^-1)`,
at every length up to |r| (up to 17). It is the "subset of the relators"
construction, searched in rank 3 with no generator eliminated, and it is the
arm that is matched word for word with CoV.

## 4. What is run

1. `control` on all 640. The runner stops if the 2-generator greedy, the rank-n
   port at n = 2 and the null stabilization differ on any presentation.
2. `relsub` on all 640, every solved row stored with its path.
3. `bf` for n = 1, 2, …, 10 in order, each length complete before the next, so
   a run that is cut short still leaves an exhaustive result up to some L.
   `inv` for n <= 6.
4. Budget 1,000 everywhere. A budget-B search is the first B pops of any longer
   one, so the 100-node results are read off the same rows.
5. Second box, if the first is healthy: budget 10,000 for L <= 7 and relsub,
   to compare with the CoV sweep at 10,000.

Longest word length: 10. Measured cost is 35 to 52 ms per search on one M4 core
(length 4 to 10); at L = 10 that is about 900 core-hours on the cloud CPU, one
night on a 192-core box. Length 11 alone would add 75.6 million searches.

## 5. Stored per search

`nodes` (pops, uint16), `path_len` (−1 unsolved), `min_total` (smallest total
length pushed), in arrays indexed `[presentation, word]`, one file per length;
the word list is stored with them and is reproducible from `words.py`. Paths
are kept for about 2,000 rows per length chosen by a hash of the row key, and
for every solved relsub row.

## 6. Comparisons, fixed before looking at results

Cost axis: nodes popped, the unit of the published baseline. Wall time is
reported beside it, because a rank-3 pop expands three times as many relator
pairs as a rank-2 pop.

Per presentation p with control cost c_p (nodes, or unsolved at 1,000):

1. **Solve rate by length**: fraction of (p, w) solved, for n = 1..10, split by
   control-solved and control-unsolved presentations.
2. **Quicker or slower**: among control-solved p, the fraction of words with
   nodes < c_p, = c_p, > c_p, and unsolved; the distribution of nodes − c_p by
   length. Aggregated per presentation first, then across presentations, so a
   few presentations cannot carry the average.
3. **Any word (oracle)**: number of presentations solved by at least one w with
   |w| <= L. Numbers to beat at 1,000 nodes: control **554/640**, CoV oracle
   **604/640** (PR #26). An oracle count is an existence statement, not a
   method, and is labelled so.
4. **Price of the oracle**: nodes spent running the words in shortlex order
   until the first solve, compared with the control given the same total
   (the control solves 606 at 10^4 and 634 at 10^5 nodes).
5. **One fixed word (runnable)**: for each w, presentations solved out of 640.
   The best word is chosen on the even pres_ids and scored on the odd ones, and
   the reverse, so the reported number is not selected on its own test set.
6. **Random word**: the mean over w at each length, the expected result of
   picking a word blind.
7. **relsub vs CoV**: for the same (p, w), rank-3 nodes against the best CoV
   start built from that w (PR #26 rows), and the oracle counts side by side.
8. **Gained and lost**: control-unsolved presentations some word solves, and
   control-solved presentations a word loses, by length.

Expected, to be checked: a word that is not a subword of a relator gives the
search nothing to substitute, so `Z·w` is dead weight that must be reduced to
`Z` at the end, costing at least |w| extra moves; such words should be slower.
Subwords of a relator let one S-move shorten that relator by |w| − 1, which is
the CoV substitution performed inside the search, so any gain should
concentrate in relsub.

## 7. Verification

- 2-generator greedy = rank-n port = null stabilization on all 640, and equal
  to the control rows of the CoV sweep (independent run, PR #26).
- Every stored word list equals `words_of_length(n)`; every (presentation,
  word) has a row; counts equal 2·3^(n−1).
- Every sampled path and every solved relsub row is replayed by
  `verify_results` through the pure-Python spec (legal moves, cancelling seams,
  cap respected at every step, trivial endpoint), independent of the numba
  solvers, and must match the stored nodes and path length.
- A random sample of stored entries is re-run with the reference
  `solvern.search_n`, not the fast twin used by the sweep.
- Tests (`tests/stable_ac/test_rank3_bf.py`): family completeness and counts,
  block partition, relsub ⊇ CoV family, null stabilization, budget prefix
  property in rank 3, runner end to end against the reference search, resume,
  verifier rejects a tampered array.

## 8. Problems in the existing rank-3 branch (`nocov`), and what this run does instead

| `nocov` (Branch A) | Here |
|---|---|
| A1 is 16 hand-picked words, with both members of {x, X}, {y, Y}, {xY, yX} | every reduced word to length L, one per inverse pair |
| A2 (rotation prefixes) is thinned to evenly spaced words when over `A2_MAX_WORDS` | every cyclic subword, no thinning |
| cap 64, against baseline columns at cap 24 | cap 24 for every arm |
| baseline columns read from a 50,000-node snapshot | control re-run in the same job, checked three ways |
| benchmark is the subset ladder / combined_66 | all 640 of MS640 |
| "best word" reported without pricing the words tried, pooled over rows | oracle labelled, priced, and cross-validated; per presentation first |

The search itself (`solvern`, `solvern_fast`) is sound: at n = 2 it equals the
baseline node for node, and the null stabilization equals the control.

## 9. Compute

One autonomous spot box per budget (`aws_rank3_bf_box.sh`): clone at a pinned
commit, run the tests, pre-flight on two presentations with verification, the
sweep, the verifier, sync to S3 every two minutes, shut down (= terminate). A
dead-man timer shuts it down regardless. Work is checkpointed per
(presentation, length, 2,187-word block); a relaunch resumes from S3. Budget
1,000 needs a few MB per worker, so every core runs a worker.

## 10. Why CoV, and what comes after

**Why eliminate the generator at all.** The rank-3 search pays for the extra
generator on every pop: three relators give 6 ordered pairs instead of 2, the
state space contains every rank-2 state times every state of the third relator,
and a solve must also spend moves reducing `Z·w` to a single letter. CoV uses
the same z = w to shorten the relators and then removes z, so the greedy runs
in rank 2 with shorter relators and none of that overhead. This sweep is the
measurement behind that sentence: "we ran the 3-generator search for every word
up to length 10; this is what it gives, and this is what eliminating the
generator adds." If rank 3 turns out to match CoV, the elimination step is not
needed and the simpler method wins.

**Rank 4 and 5.** `solvern` takes any number of generators, so
`<x,y,z,t | r1, r2, Z·w1, T·w2>` runs unchanged. Brute force does not: the
family is the square of this one (3.5·10^9 pairs at L = 10). The follow-up is
to take the top-k words per presentation from this sweep and run all pairs
(and for rank 5, triples) of them, plus words `w2` in x, y, z, against two
controls: the best single word, and the null double stabilization.

## 11. Deviations

None yet.
