# Rank-3 brute-force baseline on MS640: plan

Written 12 Oct 2026 (UTC), before the sweep was launched. Later changes go in
[Deviations](#11-deviations), not into the sections above it. Two corrections
made in place after the literature review are marked *(corrected)* and listed
there. Sections 12 and 13 were added after launch and before any result was
read.

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

Expected, to be checked *(corrected)*: a word that is not a subword of a
relator gives the search nothing to substitute, so `Z·w` is dead weight that
must be reduced to `Z` before the end. Given a rank-2 trivialization of s
moves, `Z·w` can be stripped letter by letter once r1, r2 are single letters,
so a rank-3 path of at most s + |w| moves always exists: |w| is an **upper**
bound on the extra path length, not a lower one (w = r1 needs one extra move).
Path length is not node count; the greedy can still spend many more pops, and
that is what is measured. Subwords of a relator let one S-move shorten that
relator by |w| − 1, which is the CoV substitution performed inside the search,
so any gain should concentrate in relsub. Whole rotations of a relator are the
control in disguise (one move turns `Z·w` into `Z`) and are reported
separately.

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
- Independent checks (`indep/`). Five scripts written from a prose brief
  (`indep/BRIEF.md`) by testers who were not shown the runner, the fast solver,
  the verifier, the summarizer, the plot script or their tests, and each read
  line by line by a second tester. They import nothing from the repo (the box
  runs them with `python -I`) and exit 3 on any mismatch:
  `indep_words_classes.py` (word family rebuilt from the definition, file
  shapes and value ranges, control rows, the rank-4/5 arrays, a search at
  budget 1,000 is a prefix of the same search at 10,000, relabeling classes,
  duplicate starts), `indep_replay.py` (its own AC-move replayer on every
  stored path: legal moves, cap 24 at every step, trivial endpoint, stored
  lengths), `indep_search.py` (its own best-first search: all 640 controls and
  a time-boxed random sample of rank-3, inverse-word, rank-4/5 and
  budget-10,000 cells, compared on solved, nodes and path length),
  `indep_stats_rank3.py` and `indep_stats_rankn_fig.py` (every number in the
  summaries and in the control-vs-start tables recomputed from the raw arrays).
  Each script's notes (`indep/*.md`) list what it assumed and what it could not
  check.
- Relabeling classes (`class_view.py`, tests in
  `tests/stable_ac/test_rankn_class_view.py`). MS640 holds each presentation
  up to a signed relabeling of x, y more than once (319 classes: 318 pairs and
  one class of four), and the greedy is not invariant under relabeling, so
  every headline count is also given per class, together with the node gap
  between relabeled copies of the same search (the noise floor of §6).

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

Recorded 12 Oct 2026, 04:15 UTC, after launch and before any result was read.

1. **§6, corrected in place.** The first version said a non-subword costs "at
   least |w| extra moves". It is at most s + |w| (see §6 and §12).
2. **Second box.** §4 said budget 10,000 for L <= 7 "if the first is healthy".
   It was launched with the first, for L <= 8, because the spot quota allowed
   both (288 of 300 vCPU).
3. **Box script.** The user-data both boxes run is `aws_rank3_bf_box.sh` of
   the pinned commit plus an `EXTRA` variable for extra runner flags, empty on
   both. The repository code both boxes run is `8b3a51d`.
4. **Shard identity (audit E1).** At `8b3a51d` a shard file carries no budget,
   cap or dataset, so a second run with other parameters in the same
   `--out-dir` would reuse it. Not reachable in these runs: one box per
   budget, each with its own disk and its own S3 prefix, both logged
   "restored 0 files". Fixed after launch (shards live under the run's stem
   and store what they hold; a mismatch is refused), with a test. A relaunch
   after a spot interruption must use the same user-data as the box it
   replaces.
5. **Not logged.** Children generated per pop. The cost axis is pops; the
   extra work per rank-3 pop shows only in wall time (`block_seconds`).
6. **relsub vs CoV is not at equal caps.** The CoV sweep (PR #26) runs each
   start at cap max(24, longest relator + 16), median 32; only 4% of its rows
   ran at 24. Rank 3 runs at 24 throughout. The CoV rows also keep one row
   per class of outputs under one representative word, so the same-word join
   covers only (presentation, word) pairs that have a CoV row.

Recorded 12 Oct 2026, 04:30 UTC, after lengths 1 to 6 of box A were read.

7. **Scope, from Truett (03:44 to 04:25 UTC messages).** This is the baseline
   of the stable-AC paper, so ranks 4 and 5 are part of it, not a follow-up
   (§10). Spend rate at most $5 per hour. No compute on the laptop: tests and
   re-checks run on AWS. Branch only, no pull request.
8. **Rank 4 and 5 arms (new, box C).** `rankn_bf.py`: start
   `<x,y,z1..zk | r1, r2, Z1·w1, .., Zk·wk>` for every multiset of folded
   reduced words: rank 4 with |w| <= 3 (26 words, 351 multisets), rank 5 with
   |w| <= 2 (8 words, 120 multisets); 301,440 searches, same solver, cap 24,
   budget 1,000. Per presentation the 2-generator control and the null
   stabilization `Z1, .., Zk` must agree node for node. The script was
   syntax-checked only before launch; its first real test is the box's own
   preflight on presentations 0, 320, 639, re-run with the reference solver.
9. **Reference re-check (new, box C).** `rankn_checks.py` re-runs random
   cells of the rank-3 files (lengths 1 to 7), of the rank-4/5 files, and
   both sides of mirror-twin pairs whose solved flags differ, with
   `solvern.search_n`, and compares (solved, nodes, path length). Time-boxed.
10. **MS640 is 319 classes, not 640 (found 04:20 UTC).** Under the 8 signed
    relabelings of {x, y} the 640 rows form 318 classes of two and one of
    four; 317 pairs are y <-> Y mirrors (r1 is its own mirror up to rotation
    and inversion). So (row, w) and (mirror row, mirror w) are the same
    problem. Only rows 7 and 9 are symmetric themselves (58,806 of 37,790,720
    starts duplicated inside a row). The greedy breaks ties by letter, so
    mirror copies are not identical runs: on lengths 1 to 5 the solved flag
    differs on 0.16 to 0.90% of mirror pairs, the node count is equal on
    about 60% of both-solved pairs, and the 90th percentile of the node gap
    is 13 to 17%. Consequences: all 640 rows are kept (each compared with its
    own control); every table is also given per class; a node difference
    inside the mirror gap is reported as relabeling noise, not as faster or
    slower. The control and the CoV sweep carry the same doubling.
11. **Box B and its timer.** At 0.6 to 0.8 core-seconds per search, length 8
    at budget 10,000 will probably not finish inside the 600-minute timer.
    Shards are in S3; the remainder is finished by a relaunch with the same
    user-data and commit `8b3a51d`.
12. **Box A relaunched once (04:43 to 04:48 UTC).** Truett asked for a lower
    hourly rate if the finish time did not move. Box A was terminated to move
    it to the same hardware in a cheaper zone (c7a.metal-48xl, us-east-1f,
    $2.09 against $3.06 per hour); that zone had no spot capacity, so it was
    relaunched as the same c7a.48xlarge in us-east-1d (instance
    `i-0154e51769e25b45e`, `DEADMAN` 780, otherwise the same user-data and
    commit `8b3a51d`). It restored 2,466 files from S3, skipped lengths 1 to 7
    as merged and resumed length 8 with 1,275 of 1,280 tasks to run. Cost:
    about 16 minutes of the run, nothing else. The first boot's log is
    `b1000/run_box1.log`. No setup under $2 per hour finishes at the same
    time (the sweep needs about 290 cores).
13. **No automatic restart after a spot interruption.** A persistent spot
    request with stop behavior was tested on a c7a.medium
    (`restart_test/run.log`): an OS shutdown leaves the instance stopped and
    the request disabled, so a finished box does not relaunch itself. Not
    tested: the restart after a real interruption (AWS-documented only). It is
    not used, because the IAM user that launches the boxes may not call
    `ec2:CancelSpotInstanceRequests`, `ec2:StartInstances` or
    `ec2:StopInstances`; a persistent request for a 192-vCPU box would have no
    off switch except its `ValidUntil`. All boxes are one-time spot requests.
    An interruption stops the run; shards are in S3 and a relaunch resumes it.
    The test request expired at 06:00 UTC (state `cancelled`); its stopped
    instance carried no `Project` tag, was tagged and terminated at 06:02 UTC.
14. **Box B stops after length 7 (05:42 to 05:45 UTC).** Length 6 at budget
    10,000 merged at 05:40:51 (311,040 searches, 80.96% solved, 277,310
    core-seconds). At three times that per length, length 8 could not finish
    inside the timer (item 11) and would have spent about 5 hours on a partial
    length. Box B was terminated once the length-6 files were in S3 and
    relaunched as `i-0c4e7978972ef4e53` (same type, zone and commit `8b3a51d`,
    `MAX_LEN` 7, `DEADMAN` 300; four `MaxSpotInstanceCountExceeded` retries
    while the old box still counted against the quota). It restored 1,445
    files, skipped lengths 1 to 6 as merged and started length 7 at 05:47:27.
    The first boot's log is `b10000/run_box1.log`. Length 8 at 10,000 is not
    run. If the box's own verifier is cut off by the timer, the post box
    (item 15) verifies the same files.
15. **Post box (new).** `aws_rank3_post_box.sh`: a small on-demand box that
    syncs the merged files of all three runs, runs the tests, the summaries,
    the figures (`plot_rankn_vs_control.py`), the relabeling-class view
    (`class_view.py`), the verifier with 30 reference re-runs per file and the
    independent checks of §7, once at launch and once when box A logs DONE.
16. **Committed layout.** The four relator-subword files (12 to 25 MB each)
    are committed gzipped; `verify_rank3_bf` unpacks them to a temporary
    directory. Everything else is committed as the boxes wrote it; shards and
    logs stay in S3.

### Boxes

Box C: c7a.2xlarge spot, 8 vCPU, launched 12 Oct 04:29:03 UTC, commit
`8b3a51d` plus `rankn_bf.py` and `rankn_checks.py` from
`cov_all/rank3_bf/rankn/code/`, `DEADMAN` 420, `PREFIX`
`cov_all/rank3_bf/rankn`, user-data `aws_rankn_box.sh`.

| | Box A | Box B |
|---|---|---|
| Instance | c7a.48xlarge spot, 192 vCPU | m7a.24xlarge spot, 96 vCPU |
| Launched (UTC) | 12 Oct 04:02:51 | 12 Oct 04:03:19 |
| Commit | `8b3a51d` | `8b3a51d` |
| `BUDGET` | 1000 | 10000 |
| `MAX_LEN` | 10 | 8 (7 after the relaunch, item 14) |
| `INV_MAX_LEN` | 6 | 0 |
| `WORKERS` | 192 | 96 |
| `EXTRA` | empty | empty |
| `PRE_IDS`, `PRE_MAX_LEN` | 0,320 and 4 | 0,320 and 4 |
| `DEADMAN` (minutes) | 720 (780 after the relaunch, item 12) | 600 (300 after the relaunch, item 14) |
| `PREFIX` | `cov_all/rank3_bf/b1000` | `cov_all/rank3_bf/b10000` |

## 12. Literature: what exists, and what a rank-3 baseline has to state

No published source read for this plan reports a search-found trivialization
that used a third generator.

| Source | What it did with rank 3 or stabilization |
|---|---|
| Miasnikov 1999 (genetic algorithm) | tried the stabilization move; no efficiency gain |
| Myasnikov–Myasnikov–Shpilrain 2002 | AK(3) stabilized by hand with z = y⁻³, then y eliminated; the proof has a misprint, so stable AC-triviality of AK(3) is open |
| Krawiec–Swan 2016 (genetic algorithm) | rank-3 instances included, none solved; 19 rank-2 instances solved |
| Shehper et al. 2024, §9, Lemma 11 | defines the `z⁻¹w` stabilization and the elimination; no search |
| Lisitsa 2025 | states no known computational approach searches stable AC-transformations directly |
| Lackenby 2023 | generalized stable move restricted to \|w\| <= 2; double-exponential upper bound for thickenable presentations |
| Bridson; Lishak | tower-type lower bounds on moves that hold with stabilization allowed (rank >= 4; rank 3) |
| Fagan et al. 2026 (Two-Hump) | the greedy and benchmark used here; 533 / 604 / 634 / 640 / 640 solved at 614 / 10K / 100K / 1M / 10M nodes; no stable-AC experiment |
| This project, `nocov` | 16 hand-picked words and thinned prefixes, cap 64, 11 to 66 presentations: 51/176 at 1,000 nodes, AK(3) 0/102 |
| Mentor email, 1 Jul 2026 | names `<x,y,z | r1,r2,z>` and the 4-, 5-generator versions as the baselines to have, then Lemma 11 words |

What follows for this run:

- **Moves.** The Two-Hump substitution move on every ordered pair of the three
  relators (6 instead of 2), cancelling seam only. `solvern` does this.
- **Cost unit.** Nodes popped, as in the repo's baseline. Shehper et al. count
  enqueued states; the Two-Hump text says "visited" without saying which. No
  published figure exists at 1,000 nodes, so the only valid comparator is the
  control run here, with the same code.
- **Cap.** 24 per relator on all three relators. It is the repo's baseline
  setting, not a number from the paper.
- **Solved.** Every relator has length 1, in rank 3. Reaching a solved rank-2
  pair by eliminating z is the CoV experiment, not this one.
- **What a solve certifies.** `Z·w` is the image of `Z` under z -> z·w⁻¹, so a
  rank-3 solve certifies stable AC-triviality with one stabilization. All 640
  are already AC-trivial; the measurement is cost.
- **Derived, not in a source.** (a) A rank-2 trivialization of s moves gives a
  rank-3 one of at most s + |w| from `Z·w`. (b) Every CoV solve lifts to a
  rank-3 path from `Z·w` (each substitution and each elimination step is a
  legal rank-3 move), so an uncapped, unbounded rank-3 search contains CoV;
  what differs is the order the greedy visits things in, the cap, and the
  extra relator in the length objective. (c) All starts `Z·w` for one
  presentation lie in one AC component of rank 3: the sweep over w is a
  multi-start inside one component, not a jump between components. (d) The
  only length-preserving symmetry between words for a fixed presentation is
  w <-> w⁻¹.
- **Limits.** Failure at 1,000 or 10,000 nodes says nothing about stable
  triviality. An any-word count is best-of-many and is priced (§6.4).

## 13. Audit of the existing rank-3 branch, in full

Search kernel: matches the pure-Python spec on 16 of 16 re-run rows (solved,
nodes, minimum length, moves). No bug found in moves, seam test, reduction or
canonical form.

Found, and what this run does about each:

| Finding in `nocov` | Effect | Here |
|---|---|---|
| A start relator longer than the cap is searched but rejected by the verifier | unreachable while 1 + \|w\| <= cap | asserted (longest relator 17, cap 24) |
| Terminal test accepts single letters without checking they are distinct | sound only for \|det\| = 1 starts | \|det\| = 1 asserted on the dataset |
| Tie-break not invariant under z <-> Z: w and w⁻¹ differ in nodes on 12 of 40 pairs, never in solved status | a 10% node gap between two words is label noise | `inv` arm measures it on every word to length 6 |
| A2 contains whole rotations of a relator (563 jobs, 336 solved, control + 1 node) | inflates pooled solve rates | flagged and reported apart |
| 197 duplicate (presentation, word) jobs across families; 45 to 96 jobs per presentation | pooled rates weight presentations unequally | one family, same words for every presentation, per-presentation means |
| Results row written before its certificate | a crash leaves a solved row with no path | paths written first |
| Resume key not bound to relators, cap or budget; files with mixed commits | stale rows under a new name | shard identity checked; verifier binds rows to the dataset |
| Verifier replays paths only | node counts never re-derived | sampled rows re-run with the reference search |

Recount of the old data, combined_66 at 10,000 nodes: the best of up to 96
words solves 41 of 60 ladder rows, the control 40. On the 40 control-solved
rows, with each presentation weighted equally, a word is cheaper than the
control 1.9% of the time, the same 0.0%, more expensive 60.8%, unsolved 37.3%.

An older branch (`test/stable-ac-moves`, `z` in {x, y, r1, r2}, 500,000 nodes,
another tie-break and cap 23) points the same way: every arm solved a strict
subset of the baseline's 634 (619, 602, 540, 523).
