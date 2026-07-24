# Greedy against best CoV, all 60 — nodes explored and path length

`greedy_vs_bestcov_subset60_nodes_path.csv`, written by `experiments/stable_ac/cov/rebuild_comparison_tables.py`. Both arms cover **60/60**. No search was run to build it: every row is a join over runs that already existed.

| | greedy | best CoV |
|---|---|---|
| budget | 1,000,000 | 20,000 per start |
| cap | 24 | 24–46, per transform |
| solved | 60/60 | 60/60 |
| nodes, mean over 60 | 45,244 | 2,383 |
| nodes, median | 1,310 | 34 |
| searches to produce it | 60 | 6,177 + 909 |

## Why best CoV at 20,000 is defined for all 60 without a new sweep

A search at budget `B` is exactly the first `B` pops of any longer search. So for a presentation whose best CoV solved in `n ≤ 10,000`, that start still solves in exactly `n` at 20,000, and any start that only *newly* solves must have cost more than 10,000 — hence more than `n`. The minimum cannot move. Only the eight with no solving start at 10,000 could change, and they come from the escalation run. The builder asserts this on all 52 rather than assuming it: `bestcov_nodes` and `bestcov_path` must equal the b10k table's values exactly, or it refuses to write.

`bestcov_found_at_budget` records which run supplied each row — 10,000 for 52, 20,000 for `ms622`–`ms625` and `ms636`–`ms639`.

## Three things this table does not claim

**The caps differ, by construction.** The greedy runs at cap 24; each CoV winner runs at the cap its own transform needs (24–46 across the 60). A change of variables lengthens relators, so this is not a confound that was closed — it is inherent to the comparison. Both caps are carried per row (`greedy_cap`, `bestcov_cap`) so the mismatch is visible wherever the ratio is read.

**The two path lengths are not comparable, and no ratio column is emitted.** A CoV path is measured from the *transformed* pair; it certifies that pair, not the original. The gap is large enough to mislead if it were divided — on `ms622` the greedy's certificate is 671 moves and the best CoV's is 489, but they are certificates for different presentations.

**Best CoV is an oracle.** `bestcov_nodes` is the cheapest of `bestcov_n_tried` searches (80–174 per presentation), priced as if the winning `z` were known in advance. The honest cost of *finding* it is the full sweep — 6,177 searches at 10,000 nodes plus 909 at 20,000. The runnable version of the same idea, and what it is actually worth, is in [`../stable_ac/cov/allcov_escape/ESCAPE.md`](../stable_ac/cov/allcov_escape/ESCAPE.md): a blind restart beats the greedy 2.6×–3.4× on four rows and not at all on four others, and the tuned heap ordering beats both on all eight.

## Related

`nodes_comparison_subset60.csv` is the wider six-arm table; it now carries `nodes_bestcov_b20k` / `solved_bestcov_b20k` alongside the untouched `*_bestcov_b10k` columns, and `best_technique_is_oracle` marks every row whose winner is a best-of-N rather than a single search (**53 of 60** — 45 of those predate the escalation, and only 7 rows are won by a single-search arm). `nodes_comparison_subset60.png` is regenerated from it by `experiments/stable_ac/cov/make_nodes_comparison_fig.py`.
