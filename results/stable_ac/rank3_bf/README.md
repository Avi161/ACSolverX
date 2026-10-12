# 3-, 4- and 5-generator brute-force baseline on MS640

**Status, 12 Oct 2026 07:30 UTC: interim.** In this directory: word lengths 1 to 9 at budget
1,000, lengths 1 to 6 at budget 10,000, rank 4 and rank 5. Still running on AWS: length 10 at
budget 1,000 and length 7 at budget 10,000. The numbers below change only by those two lengths.

The baseline greedy (`run_baseline.greedy_search`, cap 24, cost = nodes popped) is run on every
MS640 presentation `<x,y | r1,r2>` (the **control**) and on the stabilized presentation

    <x, y, z | r1, r2, Z·w>          for every freely reduced word w in x, y

with nothing changed in the search except the rank (`solvern_fast.search_n_fast`, the rank-n port
of the same greedy: same children, same canonical form, same tie-break). Plan, definitions and
every deviation: [`PLAN.md`](../../../experiments/stable_ac/rank3/PLAN.md). A solve from a
stabilized start certifies **stable** AC-triviality only.

## Result

A third generator with a brute-forced relator `Z·w` does not help the greedy; it costs.
Budget 1,000, words of length 1 to 9 (19,682 words per presentation, 12,596,480 searches):

| | control | 3 generators |
|---|---|---|
| a random word: fewer nodes than the control | | 0.6% of starts (0.4% by more than the relabeling noise) |
| a random word: more nodes | | 65.5% |
| a random word: not solved within 1,000 nodes | | 33.9% |
| presentations solved by one fixed word for all (best word, chosen with hindsight) | 554 | 528 (`yXYYYxyyy`) |
| the same, word chosen on one half of MS640 and scored on the other | 281 and 273 of 320 | 258 and 264 of 320 |
| presentations solved by *some* word (oracle: needs the right word per presentation) | 554 | 576 |
| presentations where words run in shortlex order until the first solve cost fewer nodes in total | | 0 of the 554 the control solves |

- No word solves as many presentations as the control. 0 of 19,682 words tie or beat it.
- The oracle's 22 extra presentations are not out of the control's reach: the control solves all
  22 with 1,160 to 26,838 nodes (18 of them within 10,000). The best word solves them in under
  1,000, but finding it by trying words in order costs 41,000 nodes or more.
- Longer words do not help: the share of solved starts falls slowly from 69.8% (length 3) to
  65.9% (length 9), and the oracle gains nothing from length 9 (576 at length 8 and at length 9).
- Budget 10,000, lengths 1 to 6 (control 606): a random word has fewer nodes 0.9%, more 80.1%,
  unsolved 18.9%; some word solves 600, 4 gained and 10 lost.
- Rank 4 and rank 5 are worse again (below).

### By word length (budget 1,000, mean over presentations of the per-presentation share)

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

Gained = solved by some word and not by the control (554). Lost = solved by the control and by no
word up to that length. Full tables, the 100-node view, the best words and the price of the
oracle: [`rank3_bf_ms640_b1000_cap24_summary.md`](rank3_bf_ms640_b1000_cap24_summary.md),
[`rank3_bf_ms640_b10000_cap24_summary.md`](rank3_bf_ms640_b10000_cap24_summary.md).

### Graphs (same layout as the CoV graph)

Nodes from a random stabilized start against nodes from the control, with y = x, then the
fewer / same / more / unsolved split by the control's cost.

| | budget 1,000 | budget 10,000 |
|---|---|---|
| rank 3, all lengths | [`..._b1000_cap24_control_vs_start_L1-9.png`](rank3_bf_ms640_b1000_cap24_control_vs_start_L1-9.png) | [`..._b10000_cap24_control_vs_start_L1-6.png`](rank3_bf_ms640_b10000_cap24_control_vs_start_L1-6.png) |
| rank 3, lengths 1 to 4 | [`..._b1000_cap24_control_vs_start_L1-4.png`](rank3_bf_ms640_b1000_cap24_control_vs_start_L1-4.png) | [`..._b10000_cap24_control_vs_start_L1-4.png`](rank3_bf_ms640_b10000_cap24_control_vs_start_L1-4.png) |
| rank 4 | [`rankn_..._r4_control_vs_start.png`](rankn_bf_ms640_b1000_cap24_r4_control_vs_start.png) | |
| rank 5 | [`rankn_..._r5_control_vs_start.png`](rankn_bf_ms640_b1000_cap24_r5_control_vs_start.png) | |

Each `.png` has a `.md` with the numbers behind it.

## Rank 4 and rank 5 (budget 1,000)

Start `<x,y,z1..zk | r1, r2, Z1·w1, .., Zk·wk>` for every multiset of words: rank 4 with every
pair of words up to length 3 (351 starts per presentation), rank 5 with every triple up to
length 2 (120 starts). The rank-3 column uses the same word pool, so the only change along a row
is the number of extra generators.

| | control | rank 3, same word pool | rank 4 (pairs, \|w\| <= 3) | rank 5 (triples, \|w\| <= 2) |
|---|---|---|---|---|
| searches | 640 | | 224,640 | 76,800 |
| a random start solves | | 60.1 to 69.8% | 59.1% | 53.6% |
| a random start has fewer nodes than the control | | 0.0 to 1.1% | 0.2% | 0.0% |
| presentations solved by some start | 554 | 516 (\|w\| <= 3), 472 (\|w\| <= 2) | 506 | 416 |
| gained over the control | | 0, 0 | 0 | 0 |
| lost by every start | | 38, 82 | 48 | 138 |
| best single start solves | 554 | 478, 449 | 454 | 376 |

Every extra generator makes the same greedy worse at the same budget. No start of rank 4 or 5
solves a presentation the control does not.

## Against CoV: why eliminate the generator

CoV uses the same z = w, substitutes it into the relators and then removes a generator, so the
greedy runs in rank 2. Rank 3 keeps the generator. Budget-matched (CoV rows are cut back to the
budget; a search at a budget is a prefix of the same search at a larger one):

| presentations solved (of 640) | budget 1,000 | budget 10,000 |
|---|---|---|
| control | 554 | 606 |
| rank 3, some word of the brute-force family | 576 (\|w\| <= 9) | 600 (\|w\| <= 6) |
| rank 3, some proper subword of a relator (the CoV word set) | 544 | 592 |
| CoV, some start ([`cov_all`](../cov_all/README.md)) | 604 | 626 |

A random start at budget 10,000: CoV has fewer nodes than the control 33.0% of the time, the same
9.6%, more 48.3%, unsolved 9.2%; rank 3 has fewer 0.9%, the same 0.0%, more 80.1%, unsolved
18.9%. On the 9,759 (presentation, word) pairs that have both a rank-3 row and a CoV row, at
budget 1,000: rank 3 uses fewer nodes than the best CoV start built from that word 602 times, the
same 456, more 4,832; only rank 3 solves 33, only CoV 1,576, neither 2,260.

Not at equal caps: CoV starts ran at cap max(24, longest relator + 16) (median 33), rank 3 at 24
throughout (PLAN §11 item 6). The CoV comparison is the one block here that the independent
scripts did not recompute.

## The same presentation twice: relabeling classes

MS640 is 319 presentations, each listed two or four times up to renaming x, y, X, Y (318 pairs,
one class of four). The greedy breaks ties by letter, so two copies of one problem are not
identical runs. Measured on every pair of searches that differ only by the renaming:

| searches (budget 1,000) | pairs | solved flag differs | both solve | same nodes | 90th percentile of the node gap |
|---|---|---|---|---|---|
| control | 324 | 0 | 281 | 65.8% | 15.4% |
| starts, word length 5 | 10,884 | 0.7% | 7,262 | 56.1% | 14.3% |
| starts, word length 9 | 743,364 | 1.7% | 484,629 | 49.8% | 20.0% |

So "fewer nodes" by less than about 17% is inside what a renaming alone does, and every oracle
count is a minimum over thousands of draws against that noise. The threshold of 17% was fixed from
lengths 1 to 5; at lengths 6 to 9 the 90th percentile is 18 to 20%. One vote per class instead
of one per presentation (budget 1,000, words up to length 9): the control solves 276 of 319
classes, some word 287; 11 classes gained, 0 lost. Of the 22 gained presentations, none has a
copy the control solves. Tables: [`*_class_view.md`](rank3_bf_ms640_b1000_cap24_class_view.md).

A word and its inverse give isomorphic search graphs and one of each pair is run. Run both ways
on every word up to length 6 (465,920 pairs): 374,326 give the same result, the solved flag
differs on 2,806 (0.6%).

## Checks

All on AWS (commit `ff0d861`), against the files in this directory. Logs: `post_*.txt`.

- **Repo tests**: 33 passed (`tests/stable_ac/test_rank3_bf.py`, `test_rankn_class_view.py`).
- **Verifier** (`verify_rank3_bf --recheck 30`, [`post_verify.txt`](post_verify.txt)): the
  2-generator greedy, the rank-n solver at rank 2 and the null stabilization `<x,y,z | r1,r2,Z>`
  agree node for node on all 640 at both budgets, and equal the control rows of the CoV sweep;
  every sampled path and every solved subword row replayed through the pure-Python spec to the
  trivial presentation with 0 failures; 30 stored entries per file re-run with the reference
  `solvern.search_n`, all equal.
- **Reference re-check** ([`checks_reference.json`](checks_reference.json)): 2,570 stored
  results re-run with the reference solver, including both sides of 75 relabeled pairs whose
  solved flags differ: 0 mismatches.
- **Independent checks** ([`indep/`](../../../experiments/stable_ac/rank3/indep/)): five scripts
  written from a prose brief by testers who were not shown the runner, the fast solver, the
  verifier, the summarizer or the plot script, each read by a second tester, run with
  `python3 -I` (no repo imports). All five: 0 mismatches.

| script | what it did | compared | mismatches |
|---|---|---|---|
| `indep_search.py` | re-ran searches with its own best-first search: all 640 controls and 640 null starts, 25,280 rank-3 cells, 3,000 inverse-word cells, 3,000 + 3,000 rank-4/5 cells, 1,800 budget-10,000 cells; compared solved, nodes, path length | 37,560 searches | 0 |
| `indep_replay.py` | replayed every stored path with its own move code (legal moves, cap 24 at every step, trivial endpoint, stored lengths) | 121,039 paths ([log](post_indep_replay.txt)) | 0 |
| `indep_words_classes.py` | rebuilt each word family from the definition (21 files); value ranges of 9,187,103 cells; a search at 1,000 is a prefix of the same search at 10,000 (473,048 cells); the 319 relabeling classes (318 of size two, one of size four); duplicate starts (117,612 of 37,790,720) | 8 checks ([log](post_indep_words_classes.txt)) | 0 |
| `indep_stats_rank3.py` | recomputed the numbers of the two summaries from the raw arrays; not compared: the control's cost at 100,000 nodes on the gained presentations (it comes from the CoV sweep's file) | 58 checks, 4,241 values ([log](post_indep_stats_rank3.txt)) | 0 |
| `indep_stats_rankn_fig.py` | recomputed the rank-4/5 summaries and every table behind a graph | 20 checks, 1,906 values ([log](post_indep_stats_rankn_fig.txt)) | 0 |

What the checks do not cover is listed in each script's notes (`indep/*.md`) and in the `skipped`
field of each `indep_*.json`.

## Files

| file | what |
|---|---|
| `rank3_bf_ms640_b<B>_cap24_control.jsonl` | 640 control rows, with the rank-n solver's copy (`n2_*`) and the null stabilization (`null_*`) |
| `..._L<n>.npz` | every word of length n on every presentation: `pres_ids` [640], `words` [K], `nodes` uint16 [640, K], `path_len` int16 (-1 = unsolved), `min_total`, `block_seconds`, `meta` |
| `..._L<n>_inv.npz` | the same for the inverse words, n <= 6, budget 1,000 |
| `..._L<n>_sample.jsonl`, `..._sample_paths.jsonl` | 770 to 1,700 solved (presentation, word) rows per length with their full move paths |
| `..._relsub.jsonl.gz`, `..._relsub_paths.jsonl.gz` | every cyclic subword of a relator as w (69,816 rows per budget), every solved row with its path |
| `rankn_bf_ms640_b1000_cap24_r4.npz`, `..._r5.npz` | rank 4 and 5: `pres_ids`, `combos` [C, k] (word indices), `nodes`, `path_len` [640, C], `base` (control), `null`, `meta`; `_sample_paths.jsonl` and `_summary.json` beside each |
| `*_summary.md` / `.json`, `*_per_word.csv`, `*_per_presentation.csv` | `summarize_rank3_bf` |
| `*_control_vs_start*.png` / `.md` | `plot_rankn_vs_control` |
| `*_class_view.md` / `.json` | `class_view` |
| `indep_*.json`, `post_*.txt`, `checks_reference.json` | check results and logs |

Not committed: the per-block shards and the box logs, in
`s3://acsolver-u124-205558941715/cov_all/rank3_bf/`.

Reproduce / check (repo root, `PYTHONPATH=.`):

    python3 -m experiments.stable_ac.rank3.run_rank3_bf --budget 1000 --max-len 4 --workers N --out-dir OUT
    python3 -m experiments.stable_ac.rank3.rankn_bf --rank 4 --workers N --out-dir OUT
    python3 -m experiments.stable_ac.rank3.verify_rank3_bf --dir results/stable_ac/rank3_bf --recheck 30
    python3 -m experiments.stable_ac.rank3.summarize_rank3_bf --dir results/stable_ac/rank3_bf --budget 1000
    python3 -m experiments.stable_ac.rank3.plot_rankn_vs_control --rank3 results/stable_ac/rank3_bf --budget 1000
    python3 -m experiments.stable_ac.rank3.class_view --rank3 results/stable_ac/rank3_bf --budget 1000
    python3 -I experiments/stable_ac/rank3/indep/indep_search.py results/stable_ac/rank3_bf data/ms640_solved.txt OUT.json 8 40

The independent scripts read plain `.jsonl`; gunzip the four subword files first.

## Cost

Budget 1,000, lengths 1 to 9: 426 core-hours. Budget 10,000, lengths 1 to 6: 111 core-hours.
A rank-3 search at budget 1,000 takes about 0.12 core-seconds with the compiled solver; rank 4
and 5 about 0.075 (shorter words, more early failures). Boxes and their settings: PLAN §11.
