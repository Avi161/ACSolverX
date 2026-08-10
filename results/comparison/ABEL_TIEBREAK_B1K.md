# The abel tie-break at budget 1,000: shorter relator, or shorter total?

**Zero search nodes.** A re-ranking of the frozen `results/stable_ac/cov/covsweep_1000_66_subnc2pxysb_mrl24_cyc_s60r6_07_20_26.jsonl` through `abel_topk_cov_b1k`'s gated loader (6,788 rows checked by its truncation gate), subset-60, top 3, budget 1,000 — plus the same arms on the 10,000-node twin of that sweep, which costs nothing because gate 1 already opens it.

## Verdict

**Neither ordering outperforms.** `abel_min_len` and `abel_len_min` solve the same 41/60 at top 3, the same 40/60 at rank 1, and differ on **1 of the 41 presentations both solve, by 2 nodes out of 4,631** (0.04%). Exact paired p on discordant solves = 1.000. At budget 10,000 the same two arms differ on 1 of 52 rows and 2 nodes. The head-to-head is **a dead heat**.

What the run *does* separate is whether `min(|r1|,|r2|)` carries signal the total length does not — and at fixed `abel`, **it does not**. As a sole second key it discriminates strictly less than the total (a unique pick on 24/60 against 31/60), and adding min anywhere in the chain — before the total or after it — moves the whole bill by at most 6 nodes in 61,627. The recommendation stays `(abel, total length)`; min does not earn a slot.

## The proposal as worded is one arm, not two

Every candidate in this sweep is a **two**-relator pair, so mean relator length = total / 2 — a strictly monotone function of total length and therefore the identical ordering. `(abel, mean, total)` and `(abel, total, mean)` produce **the same top 3 on all 60 presentations** (checked, not argued: `assert_mean_is_length`), and both coincide with the incumbent `(abel, total, longest)` on 45/60. So the substantive contrast is `min(|r1|, |r2|)`, which is not a function of the total.

That intuition was earned by `min_relator_length` as a **search progress** signal. The key here reads `min(len(r1), len(r2))` off the **start** pair, before a node is popped; the anti-leak gate exists so no key can reach the search-derived column. Same word, different object.

## Every arm at top 3, budget 1,000

| arm | k=1 | k=2 | **k=3** | median | mean | max | deployed total | rank-1 ties | top-3 ties |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `abel` | 38 | 41 | **41** | 18 | 165.6 | 1,626 | 63,790 | 53 | 54 |
| `abel_len_lex` | 39 | 41 | **41** | 18 | 137.2 | 1,025 | 62,627 | 28 | 17 |
| `len_only` | 37 | 39 | **39** | 60 | 244.8 | 1,226 | 72,549 | 32 | 51 |
| `abel_mean_len` | 40 | 41 | **41** | 18 | 112.9 | 1,025 | 61,627 | 29 | 28 |
| `abel_len_mean` | 40 | 41 | **41** | 18 | 112.9 | 1,025 | 61,627 | 29 | 28 |
| `abel_min_len` | 40 | 41 | **41** | 18 | 113.0 | 1,025 | 61,631 | 26 | 19 |
| `abel_len_min` | 40 | 41 | **41** | 18 | 113.0 | 1,025 | 61,633 | 26 | 20 |
| `abel_min` | 40 | 41 | **41** | 19 | 113.4 | 1,025 | 61,651 | 36 | 37 |

Median/mean/max are `first_solve_nodes` over that arm's own solved set, so in general they are not comparable across arms; here they happen to be, because every `abel`-first arm turns out to solve the **same** 41 presentations at k=3. That is a measured coincidence, not a guarantee — the arms disagree on the top-3 *set* on up to 17 of 60 presentations, and a different set could have reached a different presentation. The paired sections below are the comparison that does not rely on it. `deployed total` is the whole bill over all 60 (a presentation no rank solves costs the full 3 × 1,000). The last two columns count presentations where the ordered keys run out and `_ident` picks.

Reference points at this budget: the best-CoV **oracle is 45/60**, plain greedy on the untransformed pair is **29/60**, and the incumbent `abel_len_lex` is 41/60. The solve column has 4 rows of headroom above bare `abel` and none above the oracle, so it is saturated by construction — read the cost columns.

## The head-to-head

`abel_min_len` against `abel_len_min`, paired on the 41 presentations both solve:

| | `abel_min_len` | `abel_len_min` |
|---|---:|---:|
| solved / 60 at k=3 | 41 | 41 |
| solved / 60 at k=1 | 40 | 40 |
| median nodes | 18 | 18 |
| mean nodes | 113.0 | 113.0 |
| total nodes | 4,631 | 4,633 |

Cheaper on 1, tied on 40, dearer on 0; solve-count discordance 0–0, exact p = 1.000. The differing rows are `[(533, -2)]` (pres_id, `abel_min_len` − `abel_len_min`).

Each arm against the incumbent `abel_len_lex`, same paired rule:

| arm | n both | arm mean | `abel_len_lex` mean | arm total | incumbent total | cheaper / tied / dearer |
|---|---:|---:|---:|---:|---:|---|
| `abel` | 41 | 165.6 | 137.2 | 6,790 | 5,627 | 3 / 31 / 7 |
| `abel_mean_len` | 41 | 112.9 | 137.2 | 4,627 | 5,627 | 1 / 40 / 0 |
| `abel_min_len` | 41 | 113.0 | 137.2 | 4,631 | 5,627 | 1 / 39 / 1 |
| `abel_len_min` | 41 | 113.0 | 137.2 | 4,633 | 5,627 | 1 / 39 / 1 |
| `abel_min` | 41 | 113.4 | 137.2 | 4,651 | 5,627 | 5 / 32 / 4 |

The 1,000-node gap over the incumbent is **one presentation**, not a distribution: the win/tie/loss column is 1/40/0. `longest` as the third key sends one rank-1 pick into a search that burns the whole budget; `total` and `min` both avoid it.

## How much tie is left for each key to break

| key chain | median candidates tied at the minimum | mean | collapses to one pick | worst |
|---|---:|---:|---:|---:|
| `abel` | 6 | 8.35 | 7/60 | 21 |
| `abel + min` | 2 | 2.80 | 24/60 | 9 |
| `abel + total` | 1 | 2.22 | 31/60 | 8 |
| `abel + min + total` | 1 | 2.03 | 34/60 | 8 |
| `abel + total + longest` | 1 | 2.17 | 32/60 | 8 |

`abel` alone decides a unique pick on 7/60. Total length is the stronger second key (31/60 unique against min's 24/60), and the two together reach 34/60 — so **26 of 60 presentations still need a further key after all three**, and with two relators `max = total − min` means no length feature is left. That residue is what `_ident` decides today, and the ms640 census already says what it should be spent on instead: a **Booth-canonical dedup of the candidate list before the top 3 is taken**, not a fourth sort key — canonically identical candidates carry equal keys, sort adjacent, and both enter the top 3 either way. No dedup is applied here, deliberately, so these numbers stay comparable to the incumbent 41/60.

## Rank 1 alone, and why the 1,000-node margin does not survive a budget change

| arm | k=1 solved @1,000 | k=1 mean nodes @1,000 | k=1 solved @10,000 | k=1 mean nodes @10,000 |
|---|---:|---:|---:|---:|
| `abel` | 38 | 66.1 | 52 | 1,103.3 |
| `abel_len_lex` | 39 | 91.7 | 52 | 1,080.1 |
| `len_only` | 37 | 196.3 | 47 | 958.9 |
| `abel_mean_len` | 40 | 90.0 | 51 | 905.7 |
| `abel_len_mean` | 40 | 90.0 | 51 | 905.7 |
| `abel_min_len` | 40 | 90.2 | 51 | 905.8 |
| `abel_len_min` | 40 | 90.2 | 51 | 905.8 |
| `abel_min` | 40 | 90.7 | 51 | 903.9 |

Each mean is over that arm's **own** k=1 solved set, so an arm that solves more rows can carry a higher mean by picking up expensive ones — bare `abel`'s 66.1 at 1,000 is over 38 rows against the length-keyed arms' 40. At budget 1,000 any length-bearing second key is worth **+2 presentations at rank 1** over bare `abel` (38 → 40) and cuts the top-3 mean from 165.6 to 112.9 nodes. At budget 10,000 it goes the other way: bare `abel` reaches 52/60 at rank 1 and every length-keyed arm reaches 51, with a *higher* top-3 mean (1,231.3 against 1,103.3).

| arm | k=1 | k=2 | **k=3** | median | mean | max | deployed total | rank-1 ties | top-3 ties |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `abel` | 52 | 52 | **52** | 35 | 1,103.3 | 7,875 | 297,372 | 53 | 54 |
| `abel_len_lex` | 52 | 52 | **52** | 35 | 1,080.1 | 7,875 | 296,166 | 28 | 17 |
| `len_only` | 47 | 48 | **49** | 270 | 1,797.8 | 26,517 | 418,090 | 32 | 51 |
| `abel_mean_len` | 51 | 52 | **52** | 32 | 1,231.3 | 17,838 | 304,030 | 29 | 28 |
| `abel_len_mean` | 51 | 52 | **52** | 32 | 1,231.3 | 17,838 | 304,030 | 29 | 28 |
| `abel_min_len` | 51 | 52 | **52** | 35 | 1,231.4 | 17,838 | 304,034 | 26 | 19 |
| `abel_len_min` | 51 | 52 | **52** | 35 | 1,231.5 | 17,838 | 304,036 | 26 | 20 |
| `abel_min` | 51 | 52 | **52** | 36 | 1,229.6 | 17,840 | 303,941 | 36 | 37 |

Oracle 52/60, plain greedy 40/60 at 10,000. Both budgets are the same 60 presentations and the same 6,177 candidates — only the solved flags move — so this is a budget-robustness check on one frozen sweep, not a second experiment. What it establishes is negative and worth stating: **a one-or-two-row margin on subset-60 is not a property of the key.** The powered evidence for `(abel, total)` is the ms640 census — 640 presentations at budget 100,000, where re-scoring the searched top 3 under `(abel, length, lex)` came to 420,419 nodes against `_ident`'s 458,688 — not this file.

## The held-out set cannot test this

`results/stable_ac/cov/covsweep_50000_124_subnc2pxysb_mrl24_cyc_aca124_07_21_26.jsonl` covers the 124 unsolved representatives at budget 50,000, and **0 of its 124 presentations have any solving CoV candidate at all**. Every arm scores zero, so it separates nothing. That is the repo's own [control-with-no-dynamic-range](../../experiments/lessons/control-with-no-dynamic-range.md) shape, and it is why the honest scope of this comparison is subset-60.

## Source

- Sweep: `results/stable_ac/cov/covsweep_1000_66_subnc2pxysb_mrl24_cyc_s60r6_07_20_26.jsonl` (cross-checked against `results/stable_ac/cov/covsweep_10000_66_subnc2pxysb_mrl24_cyc_s60r6_07_20_26.jsonl` by gate 1)
- Table: [`abel_tiebreak_b1k_subset60.csv`](abel_tiebreak_b1k_subset60.csv)
- Runner: `experiments/heuristic_search/runners/abel_tiebreak_b1k.py` (`python3 -m experiments.heuristic_search.runners.abel_tiebreak_b1k`)
- Incumbent numbers it is read against: [`ABEL_TOPK_COV_B1K.md`](ABEL_TOPK_COV_B1K.md)
