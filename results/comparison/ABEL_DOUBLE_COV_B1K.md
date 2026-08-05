# Two-hop abelianized-magnitude CoV beam @ budget 1000 (subset-60)

Per presentation: rank every subword CoV by abelianized magnitude, keep the top 3;
enumerate every CoV of each of those and keep its top 3 (3x3 = 9 second-hop
candidates); rank those 9 and search the top 3 with the greedy at budget
1000, stopping at the first solve. Selection is search-free at both
hops — the key is a pure function of the two start strings.

## Headline

| arm | searches | solved |
|---|---:|---:|
| `greedy` — untransformed control | 1 | **29/60** |
| `hop1_topk` — one CoV, top 3 | <= 3 | **41/60** |
| **`hop2_topk` — two CoVs, top 3 of the 9** | <= 3 | **43/60** |
| `pooled_topk` — top 3 of hop-1 top 3 U the 9 | <= 3 | **43/60** |
| `hop2_all` — every one of the 9 (ceiling, not a proposal) | <= 9 | **43/60** |

- rows `hop2_topk` reaches that `hop1_topk` does not: **[581, 586]**
- rows `hop1_topk` reaches that `hop2_topk` does not: **[]**
- rows `pooled_topk` adds over `hop1_topk`: **[581, 586]**

## Cost

Both top-3 arms are at most 3 searches of <= 1000 nodes, so the
second hop is free in *search* budget — it buys enumeration, not pops. On the
41 rows both solve, nodes to first solve:

| arm | median | mean | max |
|---|---:|---:|---:|
| `hop1_topk` | 18 | 137 | 1025 |
| `hop2_topk` | 14 | 79 | 626 |

## Is the gain new reach, or a better needle?

The frozen sweep searched **every** single CoV at this budget, so its solved set is the
ceiling of one hop: **45/60**. Against it:

- rows `hop2_topk` reaches that **no single CoV** reaches: **none**
- rows one CoV reaches that `hop2_topk` does not: **[634, 635]**

Every row the second hop gains was **already inside** the one-hop ceiling — a needle the hop-1 ranking did not pick:

- **581**: 1 of its 109 single CoVs solve at this budget, and the hop-1 top 3 missed all of them; its hop-2 picks ran at caps [29, 29, 29] against hop-1's [29, 31, 37].
- **586**: 1 of its 109 single CoVs solve at this budget, and the hop-1 top 3 missed all of them; its hop-2 picks ran at caps [29, 29, 29] against hop-1's [29, 39, 37].

So the second hop is not enlarging what is reachable — it is enlarging what the
*ranking* finds. Read the +2 as a selection result, not a reachability one.

## The cap confound, measured rather than assumed

A CoV lengthens relators and the cap follows (`max(24, longest + 16)`), so the arms do
not run at one cap: control 24, hop-1 picks 24-41, hop-2 picks
24-33. A larger cap is a strictly larger search space, so a hop-2
gain bought by cap would not be a depth result. On every one of the 2 gained rows the hop-2 picks ran at a cap no larger than the hop-1 picks, so on these rows the gain is **not** bought by a wider cap. Caps are carried per row
in the CSV.

## Gate

Hop-1 enumeration reproduces the frozen `covsweep_1000_66_*.jsonl` candidate keyset,
outputs and caps exactly on the rows checked — so `hop1_topk` here is the same object
as the shipped 1-hop numbers, and hop 2 is the only new thing.

## Source

- Rows: [`abel_double_cov_b1k_subset60.jsonl`](abel_double_cov_b1k_subset60.jsonl),
  [`.csv`](abel_double_cov_b1k_subset60.csv)
- Runner: `experiments/heuristic_search/runners/abel_double_cov_b1k.py`
- One-hop @10k companion: [`ABEL_TOPK_COV_B10K.md`](ABEL_TOPK_COV_B10K.md)
