# 3-, 4- and 5-generator brute-force baseline on MS640

**Status, 12 Oct 2026 08:10 UTC: interim.** In this directory: word lengths 1 to 9 at budget
1,000, lengths 1 to 6 at budget 10,000, rank 4 and rank 5. Still running on AWS: length 10 at
budget 1,000 and length 7 at budget 10,000. The numbers below change only by those two lengths.

## Setup and terms

- **MS640**: the 640 Miller–Schupp presentations `<x,y | r1,r2>` of the trivial group in
  `data/ms640_solved.txt`. A capital letter is the inverse of a generator (`X` = x⁻¹).
- **Greedy**: the published baseline, `run_baseline.greedy_search`: best-first search over
  Andrews–Curtis (AC) moves, ordered by total relator length. **Nodes** = states popped from
  the heap, the cost unit. **Budget**: the search stops after 1,000 (or 10,000) nodes. A child
  with a relator longer than 24 letters is dropped (**cap 24**).
- **Control**: the greedy on the presentation as given, 2 generators.
- **3-generator (rank-3) start**: the same greedy, same children, same canonical form, same
  tie-break (`solvern_fast.search_n_fast`, its port to n generators), started from

      <x, y, z | r1, r2, Z·w>          for a freely reduced word w in x, y

  which adds a generator z and the relator z = w. Reaching the trivial presentation from it
  certifies **stable** AC-triviality only.
- **Brute-force family**: every freely reduced word w of length 1 to L, one of each pair
  {w, w⁻¹} (2·3^(n−1) words of length n; 19,682 up to length 9). The two members of a pair give
  the same start up to renaming z, Z; that fold is tested below.
- **Rank 4, rank 5**: two or three new generators, one word each.
- **Some word (oracle)**: a presentation counts if at least one word of the pool solves it. It
  is an existence statement, not a method: it needs the right word for each presentation.
  **Gained**: solved by some word and not by the control. **Lost**: solved by the control and
  by no word of the pool.
- **Shortlex order**: words by length, then alphabetically. The price of the oracle is the
  total nodes spent trying words in that order until one solves.
- **CoV** (change of variables, [`cov_all`](../cov_all/README.md)): takes the same z = w with
  w a **proper subword** of a relator (a cyclic subword of length at least 2 that is not a
  whole relator), substitutes z for w in the relators and eliminates x or y, so the greedy
  runs on 2 generators again.
- Percentages for "a random word" are the share of a presentation's words, averaged over
  presentations, so every presentation weighs the same.

Plan, definitions and every deviation: [`PLAN.md`](../../../experiments/stable_ac/rank3/PLAN.md).

## Result

Adding a generator and a relator `Z·w` helps the greedy only if the right word is known for
each presentation in advance. A word picked at random and one word fixed for all presentations
solve fewer presentations than the control; words tried in shortlex order until one solves
cost more nodes than the control.

Budget 1,000, words of length 1 to 9 (19,682 words per presentation, 12,596,480 searches); the
control solves 554 of 640.

| a random word, against the control | all 640 presentations | the 554 the control solves |
|---|---|---|
| fewer nodes | 0.6% (0.4% by more than 17%) | 0.6% |
| the same nodes | 0.0% | 0.0% |
| more nodes | 65.5% | 75.6% |
| not solved within 1,000 nodes | 33.9% | 23.7% |

In the first column a solve where the control fails counts as fewer nodes (the convention of
the graphs); on the 86 presentations the control does not solve, a random word solves 0.2%.
The 17% is a fixed threshold, set from the 90th percentile of the node gap between two
relabeled copies of one search on word lengths 1 to 5 (PLAN §11 item 10); in the final tables
that percentile is 15.4% for the control and 1.1 to 20.0% by word length (section "Relabeling
classes"). It is a yardstick, not a bound.

How much worse:

- The main cost is lost solves: on a presentation the control solves, a random word fails
  23.7% of the time.
- When the word does solve, the extra nodes are few: the median over presentations of the
  median extra nodes is 1 to 6, depending on the word length. "More nodes" is 100.0% (to one
  decimal) on the 295 presentations the control solves in under 10 nodes; these are 46 of the
  65.5 points.

What a choice of word can and cannot do (the control solves 554):

| | presentations solved |
|---|---|
| one fixed word for all presentations, best of 19,682 picked with hindsight (`yXYYYxyyy`) | 528 |
| one fixed word picked on half of MS640 and scored on the other half (two ways) | 258 and 264 of 320, where the control solves 281 and 273 |
| some word (oracle) | 576: 22 gained, 0 lost |

- 0 of the 19,682 words solve as many presentations as the control.
- With the right word per presentation the start is cheaper than the control on 198 of 640
  presentations (176 of the 554 the control solves, plus the 22 gained), 187 of them by more
  than 17% (165 plus the 22). These are minima over 19,682 draws each.
- The 22 gained presentations are within the control's reach at a larger budget: the control
  solves all 22 with 1,160 to 26,838 nodes, 18 of them within 10,000 (the control costs are
  read from the CoV sweep's 100,000-node control rows). The best word solves them
  in 51 to 849 nodes.
- Trying words in shortlex order until one solves costs 41,711 nodes or more on each of
  the 22, more than the control needs, and beats the control on 0 of the 554 presentations it
  solves (a word that fails costs the full 1,000 nodes, and the two words of length 1 are
  never faster).
- At 100 nodes (same searches, cut back) the oracle is further ahead, 519 against the
  control's 455; the best fixed word is still behind (453).

### By word length (budget 1,000, all 640 presentations)

| \|w\| | words | solved | fewer nodes than control | more nodes | unsolved | solved by some word up to this length | gained | lost |
|---|---|---|---|---|---|---|---|---|
| 1 | 2 | 60.1% | 0.0% | 60.1% | 39.9% | 403 | 0 | 151 |
| 2 | 6 | 68.4% | 1.1% | 67.2% | 31.6% | 472 | 0 | 82 |
| 3 | 18 | 69.8% | 0.6% | 69.2% | 30.2% | 516 | 0 | 38 |
| 4 | 54 | 68.6% | 1.1% | 67.4% | 31.4% | 540 | 4 | 18 |
| 5 | 162 | 67.3% | 0.9% | 66.5% | 32.7% | 546 | 8 | 16 |
| 6 | 486 | 66.8% | 0.7% | 66.1% | 33.2% | 562 | 16 | 8 |
| 7 | 1,458 | 66.5% | 0.6% | 65.9% | 33.5% | 572 | 20 | 2 |
| 8 | 4,374 | 66.2% | 0.6% | 65.6% | 33.8% | 576 | 22 | 0 |
| 9 | 13,122 | 65.9% | 0.5% | 65.3% | 34.1% | 576 | 22 | 0 |

A longer random word is no better: its solve rate falls slowly from 69.8% at length 3 to 65.9%
at length 9. The oracle grows with every length up to 8 (three times as many words to choose
from each time) and gains nothing from length 9. Length 10 is still running.

### Budget 10,000 (words of length 1 to 6, 728 per presentation, 465,920 searches)

The control solves 606. A random word: fewer nodes 0.9%, the same 0.0%, more 80.1%, unsolved
18.9% (all 640); on the 606 the control solves: faster 0.9%, slower 84.6%, lost 14.4%. With the
same 728 words at both budgets the oracle's edge disappears as the budget grows:

| words of length 1 to 6 | budget 1,000 | budget 10,000 |
|---|---|---|
| control | 554 | 606 |
| some word (oracle) | 562 (16 gained, 8 lost) | 600 (4 gained, 10 lost) |

Full tables: [`rank3_bf_ms640_b1000_cap24_summary.md`](rank3_bf_ms640_b1000_cap24_summary.md),
[`rank3_bf_ms640_b10000_cap24_summary.md`](rank3_bf_ms640_b10000_cap24_summary.md). Their
"faster / slower / lost" columns are over the control-solved presentations only.

### Graphs (same layout as the CoV graph in [`cov_all`](../cov_all/README.md))

Top: nodes of a random stabilized start (vertical) against nodes of the control (horizontal),
with the diagonal of equal cost. Bottom: the fewer / same / more / unsolved split, grouped by
the control's cost.

| | budget 1,000 | budget 10,000 |
|---|---|---|
| rank 3, all lengths | [`..._b1000_cap24_control_vs_start_L1-9.png`](rank3_bf_ms640_b1000_cap24_control_vs_start_L1-9.png) | [`..._b10000_cap24_control_vs_start_L1-6.png`](rank3_bf_ms640_b10000_cap24_control_vs_start_L1-6.png) |
| rank 3, lengths 1 to 4 | [`..._b1000_cap24_control_vs_start_L1-4.png`](rank3_bf_ms640_b1000_cap24_control_vs_start_L1-4.png) | [`..._b10000_cap24_control_vs_start_L1-4.png`](rank3_bf_ms640_b10000_cap24_control_vs_start_L1-4.png) |
| rank 4 | [`rankn_..._r4_control_vs_start.png`](rankn_bf_ms640_b1000_cap24_r4_control_vs_start.png) | |
| rank 5 | [`rankn_..._r5_control_vs_start.png`](rankn_bf_ms640_b1000_cap24_r5_control_vs_start.png) | |

Each `.png` has a `.md` with the numbers behind it.

## Rank 4 and rank 5 (budget 1,000)

Start `<x,y,z1..zk | r1, r2, Z1·w1, .., Zk·wk>`. Rank 4: every unordered pair of words up to
length 3, repeats allowed (351 starts per presentation). Rank 5: every unordered triple of
words up to length 2, repeats allowed (120 starts). Each is compared with rank 3 on the same word pool; rank 4
against rank 5 is not like for like, because the pools differ.

| | rank 3, \|w\| <= 3 | rank 4, \|w\| <= 3 | rank 3, \|w\| <= 2 | rank 5, \|w\| <= 2 |
|---|---|---|---|---|
| starts per presentation | 26 | 351 | 8 | 120 |
| a random start solves | 68.7% | 59.1% | 66.3% | 53.6% |
| a random start has fewer nodes than the control | 0.6% | 0.2% | 0.8% | 0.0% |
| presentations solved by some start (control 554) | 516 | 506 | 472 | 416 |
| gained over the control | 0 | 0 | 0 | 0 |
| lost by every start | 38 | 48 | 82 | 138 |
| best single start, picked with hindsight | 478 | 454 | 449 | 376 |

On the same words, a second or third extra generator is worse than one on every outcome row
except gained, where all are 0, although rank 4 and 5 have many more starts to choose from.
The rank-3 percentages are the per-length rows above weighted by their word counts, before
rounding.

## Against CoV: why eliminate the generator

Rank 3 and CoV add the same relator z = w; CoV then removes a generator and rank 3 keeps it.
The matched comparison uses the CoV word set in rank 3: every proper subword of a relator
(59,486 starts over MS640). CoV numbers are at the same budget: its 100,000-node rows are cut
back, which is exact because a search at a budget is the first part of the same search at a
larger one.

| presentations solved by some start (of 640) | budget 1,000 | budget 10,000 |
|---|---|---|
| control | 554 | 606 |
| rank 3, proper relator subwords | 544 | 592 |
| CoV, starts built from the same words | 604 | 626 |
| rank 3, brute-force family (a different, larger pool) | 576 (\|w\| <= 9) | 600 (\|w\| <= 6) |

- Every presentation the rank-3 subword starts solve, CoV solves too; CoV solves 60 more at
  1,000 and 34 more at 10,000.
- A random start at budget 10,000. CoV: fewer nodes than the control 33.0%, the same 9.6%,
  more 48.3%, unsolved 9.2% (all 640). Rank 3 with a random proper relator subword: solves
  80.9%, and has fewer nodes than the control 1.3% of the time (on the control-solved
  presentations). The two "fewer" shares have different denominators, so only their sign and
  size compare.
- Word for word. 9,759 of the 59,486 (presentation, proper subword) pairs have a CoV row under
  the same word (CoV keeps one row per class of equal outputs). On those, rank 3 against the
  best of the CoV starts built from that word:

| | rank 3 fewer nodes | same | CoV fewer nodes | only rank 3 solves | only CoV solves | neither |
|---|---|---|---|---|---|---|
| budget 1,000 | 602 | 456 | 4,832 | 33 | 1,576 | 2,260 |
| budget 10,000 | 725 | 456 | 6,018 | 36 | 1,350 | 1,174 |

Not like for like in two ways, both in CoV's favour: several CoV starts can share a word and
the best is taken, and CoV ran at cap max(24, longest relator + 16) (median 33 over its rows;
PLAN §11 item 6 estimated 32) against 24 here.

The plan expected any gain to concentrate in relator subwords. At budget 1,000, lengths 1 to
9, per start it does, slightly: inside the brute-force family, words that are a cyclic subword
of a relator of their presentation (whole rotations included) solve 70.7% and beat the control
1.1% of the time (on the control-solved presentations), the other words 66.0% and 0.6%. As a pool
it does not: the proper subwords solve 544, fewer than the control. A word that is a whole
rotation of a relator is the control in disguise (one move turns `Z·w` into `Z`): 7,210 such
(presentation, word) pairs, 6,536 solved, none faster than the control.

## Relabeling classes: the same presentation more than once

MS640 is 319 presentations, each listed two or four times up to renaming x, y, X, Y (318 pairs
and one class of four, so 318 + 6 = 324 pairs of copies). The greedy breaks ties by letter, so
two copies of one problem are not identical runs. Each row below pairs a search with the same
search after the renaming (for starts the word is renamed too, and the pair is used when the
renamed word is itself in the family):

| searches (budget 1,000) | pairs | solved flag differs | both solve | same nodes | node gap, 90th percentile | 99th |
|---|---|---|---|---|---|---|
| control | 324 | 0 | 281 | 65.8% | 15.4% | 30.4% |
| starts, word length 5 | 10,884 | 74 (0.7%) | 7,262 | 56.1% | 14.3% | 74.3% |
| starts, word length 9 | 743,364 | 12,385 (1.7%) | 484,629 | 49.8% | 20.0% | 81.9% |

Node gap = |a − b| / max(a, b), over the pairs where both solve. A renaming alone moves the
node count by more than 15 to 20% in one such pair out of ten and can flip the solved flag, so
a single "fewer nodes" is weak evidence, and "cheaper by more than 17%" is not a significance
test. The 17% was fixed from lengths 1 to 5; at lengths 6 to 9 the 90th percentile is 18 to
20%.

Counting each class once (budget 1,000, words up to length 9; a class counts as solved if any
copy is): the control solves 276 of 319 classes, some word 287; 11 classes gained, 0 lost. None
of the 22 gained presentations has a copy the control solves. Tables:
[`rank3_bf_ms640_b1000_cap24_class_view.md`](rank3_bf_ms640_b1000_cap24_class_view.md) and the
other `*_class_view.md`.

**One word per pair {w, w⁻¹}.** The starts for w and w⁻¹ differ by renaming z, Z, and the
tie-break is not invariant under it. Both were run for every word up to length 6 (465,920
pairs): 374,326 (80.3%) agree in solved flag and node count, the solved flag differs on 2,806
(0.6%), and when both solve the node counts differ by 6.4 on average (99th percentile 119).
That is smaller than the relabeling noise above but not zero, so running one word per pair is
a sampling choice (half of the 39,364 words up to length 9), not an exact symmetry, and every
"some word" count is over that half.

## Checks

All on AWS, against the files in this directory: the reference re-check on the rank-4/5
machine (commit `8b3a51d` plus `rankn_checks.py`, PLAN §11 item 9), the rest on the
post-processing machine (commit `ff0d861`). Logs: `post_*.txt`.

- **Repo tests**: 33 passed (`tests/stable_ac/test_rank3_bf.py`, `test_rankn_class_view.py`;
  the line is in the machine log, `post/run.log` in S3).
- **Verifier** (`verify_rank3_bf --recheck 30`, [`post_verify.txt`](post_verify.txt)): the
  2-generator greedy, the n-generator solver at 2 generators and the start with the empty word
  `<x,y,z | r1,r2,Z>` agree node for node on all 640 at both budgets, and equal the control
  rows of the CoV sweep; every stored solution path (117,534, including every solved subword
  row) replayed move by move with a separate pure-Python implementation of the moves, 0
  failures; 630 re-runs of stored results (30 draws per file) with the unoptimized reference
  solver `solvern.search_n` (the verifier exits 0 only if every one is equal).
- **Reference re-check** ([`checks_reference.json`](checks_reference.json)): 2,570 stored
  results re-run with the reference solver (1,660 rank 3 at lengths 1 to 7, 300 rank 4, 300
  rank 5, 80 controls, 80 empty-word starts, and both sides of 75 relabeled pairs whose solved
  flags differ): 0 mismatches.
- **Independent checks** ([`indep/`](../../../experiments/stable_ac/rank3/indep/)): five scripts
  written from a prose brief by testers who were not shown the runner, the fast solver, the
  verifier, the summarizer or the plot script, each read by a second tester, run with
  `python3 -I` (no repo imports). All five: 0 mismatches.

| script | what it did | compared | mismatches |
|---|---|---|---|
| `indep_search.py` | re-ran searches with its own best-first search and compared solved, nodes and path length: all 640 controls and 640 empty-word starts, 25,280 rank-3 results, 3,000 for inverse words, 3,000 + 3,000 for rank 4 and 5 and 100 + 100 of their empty-word starts, 1,800 at budget 10,000 | 37,560 searches | 0 |
| `indep_replay.py` | replayed every stored path with its own move code (legal moves, cap 24 at every step, trivial endpoint, stored lengths) | 121,039 paths ([log](post_indep_replay.txt)) | 0 |
| `indep_words_classes.py` | rebuilt each word family from the definition (21 files); value ranges of 9,187,103 results; a search at 1,000 is the first part of the same search at 10,000 (473,048 results) | 6 checks with an expected value, 2 report-only ([log](post_indep_words_classes.txt)) | 0 |
| `indep_stats_rank3.py` | recomputed the numbers of the two summaries from the raw arrays | 58 checks, 4,241 values ([log](post_indep_stats_rank3.txt)) | 0 |
| `indep_stats_rankn_fig.py` | recomputed the rank-4/5 summaries and every table behind a graph | 20 checks, 1,906 values ([log](post_indep_stats_rankn_fig.txt)) | 0 |

`indep_words_classes.py` also reports, without an expected value to compare against, the same
319 classes (318 of two, one of four) as `class_view`, and 117,612 starts (58,806 pairs) that
duplicate another start of their own presentation, out of the 37,790,720 of lengths 1 to 10.

**Not independently recomputed yet.** These rest on the summarizer or `class_view`, their unit
tests, and the replay of every solved subword path: the relator-subword numbers (544, 592 and
the rest of that block), the whole comparison with CoV, the relabeling-class section (gaps and
per-class counts), and the control's cost above 10,000 nodes on the gained presentations (read
from the CoV sweep's file). Two more independent scripts for these blocks are being written.
The `skipped` field of each `indep_*.json` and the notes in `indep/*.md` list the rest.

## Files

| file | what |
|---|---|
| `rank3_bf_ms640_b<B>_cap24_control.jsonl` | 640 control rows, with the n-generator solver's copy (`n2_*`) and the empty-word start (`null_*`) |
| `..._L<n>.npz` | every word of length n on every presentation: `pres_ids` [640], `words` [K], `nodes` uint16 [640, K], `path_len` int16 (-1 = unsolved), `min_total`, `block_seconds`, `meta` |
| `..._L<n>_inv.npz` | the same for the inverse words, n <= 6, budget 1,000 |
| `..._L<n>_sample.jsonl`, `..._sample_paths.jsonl` | 769 to 1,694 solved (presentation, word) rows per length with their full move paths (PLAN §5 said about 2,000: that target counts unsolved rows too) |
| `..._relsub.jsonl.gz`, `..._relsub_paths.jsonl.gz` | every cyclic subword of a relator as w (69,816 rows per budget, 59,486 proper), every solved row with its path |
| `rankn_bf_ms640_b1000_cap24_r4.npz`, `..._r5.npz` | rank 4 and 5: `pres_ids`, `combos` [C, k] (word indices), `nodes`, `path_len` [640, C], `base` (control), `null` (empty words), `meta`; `_sample_paths.jsonl` and `_summary.json` beside each |
| `*_summary.md` / `.json`, `*_per_word.csv`, `*_per_presentation.csv` | `summarize_rank3_bf` |
| `*_control_vs_start*.png` / `.md` | `plot_rankn_vs_control` |
| `*_class_view.md` / `.json` | `class_view` |
| `indep_*.json`, `post_*.txt`, `checks_reference.json` | check results and logs |

Not committed: the per-block partial files and the machine logs, in
`s3://acsolver-u124-205558941715/cov_all/rank3_bf/`.

Reproduce / check (repo root, `PYTHONPATH=.`; `D=results/stable_ac/rank3_bf`,
`C=results/stable_ac/cov_all/cov_all_suballpxyb8_ms640_b100000.jsonl.gz`):

    python3 -m experiments.stable_ac.rank3.run_rank3_bf --budget 1000 --max-len 4 --inv-max-len 4 --workers N --out-dir OUT
    python3 experiments/stable_ac/rank3/rankn_bf.py OUT N            # ranks 4 and 5
    python3 -m experiments.stable_ac.rank3.verify_rank3_bf --dir $D --cov-control $C --recheck 30
    python3 -m experiments.stable_ac.rank3.summarize_rank3_bf --dir $D --budget 1000 --cov $C
    python3 -m experiments.stable_ac.rank3.plot_rankn_vs_control --rank3 $D --budget 1000 [--lengths 1-4]
    python3 -m experiments.stable_ac.rank3.plot_rankn_vs_control --rankn $D/rankn_bf_ms640_b1000_cap24_r4.npz
    python3 -m experiments.stable_ac.rank3.class_view --rank3 $D --budget 1000
    python3 -I experiments/stable_ac/rank3/indep/indep_search.py $D data/ms640_solved.txt OUT.json 8 40

The independent scripts read plain `.jsonl`; gunzip the four subword files first.

## Cost

Budget 1,000, lengths 1 to 9: 426 core-hours, 0.12 core-seconds per search. Budget 10,000,
lengths 1 to 6: 111 core-hours, 0.86 core-seconds per search. Rank 4 and 5: 0.075 core-seconds
per search. The control's wall time was not recorded by this run, so the cost per node of the
third generator is not reported. Machines and their settings: PLAN §11.
