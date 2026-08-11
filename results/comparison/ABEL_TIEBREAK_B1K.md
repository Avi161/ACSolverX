# The abel tie-break at budget 1,000: total length, or `S`?

**Zero search nodes.** A re-ranking of the frozen `results/stable_ac/cov/covsweep_1000_66_subnc2pxysb_mrl24_cyc_s60r6_07_20_26.jsonl` through `abel_topk_cov_b1k`'s gated loader (6,788 rows checked by its truncation gate), subset-60, top 3, budget 1,000 — plus the same arms on the 10,000-node twin of that sweep, which costs nothing because gate 1 already opens it.

## Verdict

**Total length first.** `abel_len_S` solves **40/60 at rank 1** against `abel_S_len`'s 38, at a mean of **113.0 nodes against 166.1** paired over the 41 presentations both solve — 5 rows dearer for `abel_S_len`, 0 cheaper, 36 tied. The head-to-head is a win for **`abel_len_S`**. Putting `S` *ahead* of length costs 2,179 nodes out of 4,633 (47% more), and two of the five losses are a rank-1 pick that burns the entire budget.

`S` **behind** length is free and inert: `abel_len_S` and the plain `(abel, total)` differ by 6 nodes in 61,627 on the whole bill. By the time length has been applied, `S` has almost nothing left to break — which is the finding, not a caveat.

`S` is the right feature to have suspected: it carries the heaviest weight in `hsolve.RECOMMENDED` (8.458 against `L`'s 1.0) and it is the `S` in `L + 20·S + 2·MK`, the ordering that ran the ac19 hard-100k A/B. But it has never been used the way a lexicographic tie-break uses it — **`s20_mk2` and `RECOMMENDED` both keep `L` inside the same expression, where it can outvote `S`**; a lexicographic first key cannot be outvoted by anything. Score the composite itself and it holds up: `(abel, L + 20·S + 2·MK)` is the joint-cheapest arm in this file at 61,625 nodes, 40/60 at rank 1, against `(abel, total)`'s 61,627 and 40/60 — a 2-node difference, i.e. no difference. So the honest reading is not "`S` fails" but **"`S` adds nothing to a start ranking that already has `abel` and length, and actively hurts if given priority over length"**. Whether it earns its weight as a *climb* feature is a separate question this file cannot touch.

## Every feature as the second key, both positions

Since a key costs nothing to evaluate, every one of the 17 `hlab` features was scored in both positions, plus two composites used as one key each: `reco`, the full `RECOMMENDED` score (`L=1.0, K=2.53, MK=6.418, S=8.458, xyimb=3.292`), and `s20_mk2` = `L + 20·S + 2·MK`, the ordering that ran the ac19 hard-100k A/B. `uniq` is how often `(abel, f)` alone reaches a single candidate.

| f | (abel, **f**, total): k=1 | mean | deployed | (abel, total, **f**): k=1 | mean | deployed | uniq |
|---|---:|---:|---:|---:|---:|---:|---:|
| `L` | 40 | 112.9 | 61,627 | 40 | 112.9 | 61,627 | 31/60 |
| `Lmin` | 40 | 113.0 | 61,631 | 40 | 113.0 | 61,633 | 24/60 |
| `Lmax` | 38 | 171.9 | 64,049 | 39 | 137.2 | 62,627 | 23/60 |
| `imbal` | 37 | 198.5 | 65,137 | 39 | 137.2 | 62,627 | 34/60 |
| `K` | 40 | 112.8 | 61,625 | 40 | 112.8 | 61,625 | 22/60 |
| `MK` | 40 | 112.8 | 61,625 | 40 | 112.8 | 61,625 | 19/60 |
| `mK` | 40 | 112.9 | 61,627 | 40 | 112.9 | 61,627 | 16/60 |
| `S` | 38 | 166.1 | 63,812 | 40 | 113.0 | 61,633 | 14/60 |
| `Bmax` | 22 | 641.9 | 83,317 | 39 | 137.4 | 62,633 | 58/60 |
| `B1` | 40 | 112.8 | 61,623 | 40 | 112.8 | 61,625 | 20/60 |
| `Bmin` | 40 | 112.9 | 61,627 | 40 | 112.9 | 61,627 | 7/60 |
| `nb` | 40 | 112.8 | 61,625 | 40 | 112.8 | 61,625 | 22/60 |
| `xyimb` | 22 | 641.9 | 83,317 | 39 | 137.4 | 62,633 | 58/60 |
| `Bmaxrun` | 22 | 641.9 | 83,317 | 39 | 137.4 | 62,633 | 55/60 |
| `Bspread` | 22 | 641.9 | 83,317 | 39 | 137.4 | 62,633 | 55/60 |
| `ratio` | 36 | 211.0 | 65,653 | 40 | 113.0 | 61,633 | 49/60 |
| `density` | 39 | 163.4 | 63,699 | 40 | 112.8 | 61,625 | 48/60 |
| `reco` | 40 | 112.8 | 61,625 | 40 | 112.8 | 61,625 | 38/60 |
| `s20_mk2` | 40 | 112.8 | 61,625 | 40 | 112.8 | 61,625 | 48/60 |

Read the two halves separately, because they say different things.

**Placed before length, not one feature beats it.** 9 of the 19 lose rank-1 solves against `(abel, total)`'s 40/60 — `Lmax`, `imbal`, `S`, `Bmax`, `xyimb`, `Bmaxrun`, `Bspread`, `ratio`, `density` — and 4 of those are a collapse rather than a slip: `Bmax`, `xyimb`, `Bmaxrun`, `Bspread` fall to 22/60 and take the bill from 61,627 to 83,317 nodes. Those four are exactly the features with the *highest* `uniq` (55–58 of 60 decided outright). A key that discriminates more is not a better key; it is a key that overrides length more often, and length is the one that pays. The remaining 10 keep the full 40/60 — and the best of them beats `(abel, total)` by 4 nodes in 61,627, which is not a result. Note *which* ones they are: the two composites (`reco`, `s20_mk2`) and the pure counts (`K`, `MK`, `mK`, `nb`, `B1`, `Bmin`). Both composites contain `L`, so putting them "ahead of length" does not actually demote length — see the section above. The counts are integers on a coarse scale that rarely separates two candidates length would have ordered differently.

**Placed after length, no feature helps and most do nothing at all.** 13 of 19 keep the full 40/60 at rank 1 and land within 6 nodes of `(abel, total)`'s 61,627 — a spread smaller than one search on one presentation. The other 6 (`Lmax`, `imbal`, `Bmax`, `xyimb`, `Bmaxrun`, `Bspread`) give a rank-1 solve back and cost about 1,000 nodes, which is the same single presentation the incumbent's `longest` third key loses. Nothing in this vocabulary, the tuned linear score included, improves on `(abel, total length)` by a measurable amount.

One apparent exception is worth pricing, because the 10,000-node table below makes it look like a win: `abel_len_S` posts the lowest bill of any arm there (294,036 against `(abel, total)`'s 304,030) and is the only length-keyed arm to reach 52/60 at rank 1. Paired, that is **win/tie/loss 1/50/1** — one presentation (634) where `S` happens to break the tie toward a rank 1 that solves, worth the whole 10,000-node budget, against one it loses by 6 nodes. At budget 1,000 the same pair is 0/40/1, the other way. A margin carried by one row on a 60-row set is the repo's own [gap-metric](../../experiments/lessons/gap-metric-saturates-when-the-treatment-wins.md) shape, not a reason to add a key.

## Lexicographic is not weighted — which is why `s20_mk2` survives and bare `S` does not

`S` never ships on its own. It ships inside `L + 20·S + 2·MK` (`s20_mk2`, the arm that ran the ac19 hard-100k A/B) and inside `RECOMMENDED`'s weighted sum — **always with `L` in the same expression, always able to be outvoted by it**. A lexicographic key is the opposite: whatever comes first has absolute priority, and every later key only sees the ties it left.

Scored three ways on the same 60 presentations, at budget 1,000:

| how `S` is used | rank-1 solves | deployed |
|---|---:|---:|
| lexicographic, **ahead** of length — `(abel, S, total)` | 38/60 | 63,812 |
| lexicographic, alone after `abel` — `(abel, S)` | 36/60 | 65,975 |
| lexicographic, **behind** length — `(abel, total, S)` | 40/60 | 61,633 |
| **weighted, with `L` in the sum** — `(abel, L + 20·S + 2·MK)` | 40/60 | 61,625 |
| reference — `(abel, total)` | 40/60 | 61,627 |

The composite is the joint-best arm in the whole file (61,625 nodes, 1/40/0 against `(abel, total)`), and the *same feature* used lexicographically ahead of length is one of the worst. That is the finding this file is actually good for: **the "before length" column below is not evidence that these features are bad, it is evidence that lexicographic priority is the wrong way to spend them.** No arm in `hsearch`/`hsolve` has ever used one that way.

The magnitudes say why. Over all 6,177 candidates, `L` runs 6–57 while the `20·S + 2·MK` term stays in a band of standard deviation 5.1 — big enough to reorder candidates of similar length, never big enough to put a long pair ahead of a short one. Lexicographic `S` does exactly that, on every tie.

Two honest limits on the composite. Its own 10,000-node edge over `(abel, total)` is **2/50/0** and comes from the same single presentation (634) that carries `abel_len_S`'s — one row, not a distribution. And with `abel` dropped entirely, `s20_mk2` alone ranks *worse* than length alone (36/60 against 39 at 1,000, 48/60 against 49 at 10,000), so nothing here promotes it above the abelian filter.

## `Lmin` and "mean relator length", the two keys asked for first

Mean relator length is **not a distinct key**: every candidate is a *two*-relator pair, so mean = total / 2, a strictly monotone function of the total and therefore the identical ordering. `(abel, mean, total)` and `(abel, total, mean)` produce the same top 3 on all 60 presentations — checked by `assert_mean_is_length`, not argued — and both coincide with the incumbent `(abel, total, longest)` on 45/60.

`Lmin` = `min(|r1|, |r2|)` (`hlab.FEATURES[1]`, pinned equal to this file's `_minrel` by `assert_lmin_is_minrel`) genuinely is not a function of the total, and against it the total is **a dead heat**: `abel_min_len` and `abel_len_min` both solve 41/60 at top 3 and 40/60 at rank 1, differing on 1 of 41 both-solved rows by 2 nodes. `Lmin` also discriminates strictly less on its own than the total (24/60 unique against 31/60). With two relators `max = total − Lmin`, so once `abel`, `Lmin` and the total are fixed there is no further *length* information anywhere — which is why the sweep above ranges over shape features instead.

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
| `abel_S_len` | 38 | 41 | **41** | 19 | 166.1 | 1,429 | 63,812 | 12 | 23 |
| `abel_len_S` | 40 | 41 | **41** | 18 | 113.0 | 1,025 | 61,633 | 27 | 21 |
| `abel_S` | 36 | 41 | **41** | 19 | 218.9 | 1,626 | 65,975 | 46 | 44 |
| `S_only` | 29 | 33 | **35** | 112 | 395.3 | 2,110 | 88,835 | 60 | 60 |
| `abel_s20mk2` | 40 | 41 | **41** | 18 | 112.8 | 1,025 | 61,625 | 12 | 22 |
| `abel_len_s20mk2` | 40 | 41 | **41** | 18 | 112.8 | 1,025 | 61,625 | 27 | 19 |
| `s20mk2_only` | 34 | 36 | **36** | 92 | 189.9 | 1,726 | 78,838 | 41 | 54 |

Median/mean/max are `first_solve_nodes` over that arm's own solved set, so they are **not** comparable across arms in general — and the last two rows are exactly where that bites: `len_only` and `S_only` drop `abel` entirely and solve 39 and 35 of 60, so their means are over smaller, easier sets. Among the `abel`-first arms the means happen to be comparable, because every one of them solves the **same** 41 presentations at k=3. That is a measured coincidence, not a guarantee — the arms disagree on the top-3 *set* on up to 17 of 60 presentations, and a different set could have reached a different presentation. The paired sections below are the comparison that does not rely on it. `deployed total` is the whole bill over all 60 (a presentation no rank solves costs the full 3 × 1,000). The last two columns count presentations where the ordered keys run out and `_ident` picks.

Reference points at this budget: the best-CoV **oracle is 45/60**, plain greedy on the untransformed pair is **29/60**, and the incumbent `abel_len_lex` is 41/60. The solve column has 4 rows of headroom above bare `abel` and none above the oracle, so it is saturated by construction — read the cost columns.

## The head-to-head

`abel_S_len` against `abel_len_S`, paired on the 41 presentations both solve:

| | `abel_S_len` | `abel_len_S` |
|---|---:|---:|
| solved / 60 at k=3 | 41 | 41 |
| solved / 60 at k=1 | 38 | 40 |
| median nodes | 19 | 18 |
| mean nodes | 166.1 | 113.0 |
| total nodes | 6,812 | 4,633 |

Cheaper on 0, tied on 36, dearer on 5; solve-count discordance 0–0, exact p = 1.000. The differing rows are `[(217, 14), (380, 84), (505, 81), (628, 1000), (633, 1000)]` (pres_id, `abel_S_len` − `abel_len_S`).

Each arm against the incumbent `abel_len_lex`, same paired rule:

| arm | n both | arm mean | `abel_len_lex` mean | arm total | incumbent total | cheaper / tied / dearer |
|---|---:|---:|---:|---:|---:|---|
| `abel` | 41 | 165.6 | 137.2 | 6,790 | 5,627 | 3 / 31 / 7 |
| `abel_mean_len` | 41 | 112.9 | 137.2 | 4,627 | 5,627 | 1 / 40 / 0 |
| `abel_min_len` | 41 | 113.0 | 137.2 | 4,631 | 5,627 | 1 / 39 / 1 |
| `abel_len_min` | 41 | 113.0 | 137.2 | 4,633 | 5,627 | 1 / 39 / 1 |
| `abel_min` | 41 | 113.4 | 137.2 | 4,651 | 5,627 | 5 / 32 / 4 |
| `abel_S_len` | 41 | 166.1 | 137.2 | 6,812 | 5,627 | 1 / 35 / 5 |
| `abel_len_S` | 41 | 113.0 | 137.2 | 4,633 | 5,627 | 1 / 39 / 1 |
| `abel_S` | 41 | 218.9 | 137.2 | 8,975 | 5,627 | 3 / 27 / 11 |

The 1,000-node gap over the incumbent is **one presentation**, not a distribution: the win/tie/loss column is 1/40/0. `longest` as the third key sends one rank-1 pick into a search that burns the whole budget; `total` and `min` both avoid it.

## How much tie is left for each key to break

| key chain | median candidates tied at the minimum | mean | collapses to one pick | worst |
|---|---:|---:|---:|---:|
| `abel` | 6 | 8.35 | 7/60 | 21 |
| `abel + min` | 2 | 2.80 | 24/60 | 9 |
| `abel + total` | 1 | 2.22 | 31/60 | 8 |
| `abel + min + total` | 1 | 2.03 | 34/60 | 8 |
| `abel + total + longest` | 1 | 2.17 | 32/60 | 8 |
| `abel + S` | 4 | 5.68 | 14/60 | 17 |
| `abel + S + total` | 1 | 1.58 | 48/60 | 6 |
| `abel + reco` | 1 | 1.82 | 38/60 | 8 |
| `abel + s20mk2` | 1 | 1.68 | 48/60 | 8 |

**This column is not a scoreboard — read it against the one above.** `abel` alone decides a unique pick on 7/60; total length as the second key takes it to 31/60, `Lmin` to only 24/60, and `S` to 14/60. But `abel + S + total` decides **48/60** — the most of any chain here, more than `abel + total + Lmin`'s 34 — and it is the arm that *loses* 2 rank-1 solves and 2,185 nodes. `abel + reco` decides 38/60 and buys nothing. Breaking more ties is not the objective; breaking them *toward the shorter pair* is.

After `abel` and the total, **29 of 60 presentations are still tied** and — since `max = total − Lmin` — no length feature remains to supply another key. The next section asks what to do about that, and the answer is nothing.

## What to do when the tie survives: nothing

Three measurements, in the order that settles the question.

**1. Half the tie is not a tie.** The 102 candidates tied at `(abel, total)`'s minimum across those 29 presentations reduce to **52 distinct Booth-canonical pairs** (49% duplicates), and on 9 of the 29 the whole tied set is **one** start listed several times. Two candidates with the same canonical pair are not similar starts, they are the same search: same pops, same `nodes_explored`, same outcome. Choosing between them is not a decision.

**2. Where the tie is real, it is almost always inconsequential.** Split the 29 tied sets by outcome: **12** where every member solves, **16** where none does, and **1** mixed. A homogeneous set cannot be improved by any tie-break — every choice returns the same verdict. Exactly 1 presentation is a genuine decision: `533`, where the tied pair splits 25 nodes against 1,000. That is the same row that has driven every margin in this file.

**3. Deduplicating before the top 3 is free and buys nothing.** It is a real intervention, not a no-op — **42 of 60** top-3 lists currently spend at least one slot on a search an earlier rank already ran (56 slots in total), and dropping the duplicates changes the top-3 *set* on those 42 rows. The result is identical anyway:

| | k=1 | k=2 | k=3 | median | mean | deployed |
|---|---:|---:|---:|---:|---:|---:|
| `(abel, total)` top 3 | 40 | 41 | 41 | 18 | 112.9 | 61,627 |
| + canonical dedup | 40 | 41 | 41 | 18 | 112.9 | 61,627 |

Paired: win/tie/loss **0/41/0** at budget 1,000 and **0/52/0** at 10,000 — not one node moves at either budget. The promoted candidates never solve where the old top 3 failed.

This is **not** a refutation of the dedup recommendation in [`cov_top3/RESULTS.md`](../stable_ac/cov/cov_top3/RESULTS.md); it is the abel-arm half of it, measured. That census found the waste is overwhelmingly a `len`-arm problem — `len` spent **325,963 nodes, 10% of its census, on 126 repeated searches**, while **abel spent 707 nodes on 38** — and it flagged its own re-score as a lower bound because it could only reorder picks already searched. This file removes that limitation (it re-ranks the whole enumerated family, so the dedup really does pull in candidates that were never in the top 3) and finds the abel arm's gain is not merely small but **exactly zero** on all 60 rows at both budgets. So: keep the dedup, because 42/60 lists really do waste a slot and `k` should mean *k distinct searches* — but for an `abel`-ranked arm it is hygiene, not headroom, and it must never be reported as a gain. The correction is to the first version of *this* file, which offered it as the answer to the residue on the strength of the 49% duplicate count alone.

## Where the headroom actually is

The tie is exhausted, so the 4 rows between this arm's 41/60 and the oracle's 45/60 have to come from somewhere else. Rank of the first *solving* candidate under `(abel, total)`, over the 45 solvable presentations:

| k | 1 | 2 | 3 | 5 | 10 | 25 | 50 |
|---|---:|---:|---:|---:|---:|---:|---:|
| solved within k | 40 | 41 | 41 | 41 | 43 | 43 | 45 |

Widening k is not the answer either: k=3 to k=5 buys **0**, and the four rows beyond k=3 sit at ranks 8, 8, 49, 44 out of 109, 109, 138, 134 candidates. Their solving searches cost 410–632 nodes — they are **cheap solves ranked far down**, so this is a primary-ranking failure, not a budget or a tie-break failure.

All four share one cause: the solving candidate sits **one abel step above the minimum** (abel 3 against the rank-1 pick's abel 2), and on two of them it is also much longer (41 and 37 against 24). Both keys point away from it. Over all 45 solvable rows, `abel(first solving candidate) − min abel` is **40** at offset 0 and **5** at offset 1 — so the abelian filter's own minimum shell is right 40 times out of 45 and wrong 5. The open question this file leaves is therefore **when to skip abel's minimum shell**, which is not a tie-break question.

Reserving a slot for the next shell does not answer it. Three class-quota policies, scored the same way:

| policy | k=1 | k=2 | k=3 | deployed |
|---|---:|---:|---:|---:|
| all 3 from the minimum shell | 40 | 40 | 40 | 61,602 |
| 2 from the minimum + 1 from the next | 40 | 41 | 41 | 61,627 |
| 1 from each of the 3 lowest | 40 | 41 | 41 | 61,627 |
| `(abel, total)` top 3, for reference | 40 | 41 | 41 | 61,627 |

Not one recovers a row, and the pure-shell policy *loses* one. The reason is that `(abel, total)` already spills into the next shell whenever the minimum shell holds fewer than 3 candidates, so an explicit quota is mostly a no-op — and where it is not, it displaces a rank that was solving. Whatever promotes these four is a signal not yet in the vocabulary.

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
| `abel_S_len` | 38 | 77.9 | 50 | 1,068.0 |
| `abel_len_S` | 40 | 90.2 | 52 | 1,039.2 |
| `abel_S` | 36 | 51.6 | 50 | 1,182.9 |
| `S_only` | 29 | 138.2 | 44 | 1,870.8 |
| `abel_s20mk2` | 40 | 90.0 | 52 | 1,039.2 |
| `abel_len_s20mk2` | 40 | 90.0 | 52 | 1,039.0 |
| `s20mk2_only` | 34 | 117.1 | 46 | 1,042.7 |

Each mean is over that arm's **own** k=1 solved set, so an arm that solves more rows can carry a higher mean by picking up expensive ones — bare `abel`'s 66.1 at 1,000 is over 38 rows against the length-keyed arms' 40. At budget 1,000 any length-bearing second key is worth **+2 presentations at rank 1** over bare `abel` (38 → 40) and cuts the top-3 mean from 165.6 to 112.9 nodes. At budget 10,000 it goes the other way: bare `abel` reaches 52/60 at rank 1 while `(abel, total)` reaches 51, with a *higher* top-3 mean (1,231.3 against 1,103.3). The one length-keyed arm that still reaches 52 there is `abel_len_S`, on the single presentation priced two sections above.

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
| `abel_S_len` | 50 | 52 | **52** | 38 | 1,427.4 | 10,429 | 314,225 | 12 | 23 |
| `abel_len_S` | 52 | 52 | **52** | 35 | 1,039.2 | 7,875 | 294,036 | 27 | 21 |
| `abel_S` | 50 | 52 | **52** | 38 | 1,538.1 | 10,429 | 319,982 | 46 | 44 |
| `S_only` | 44 | 48 | **50** | 339 | 3,562.8 | 25,064 | 478,139 | 60 | 60 |
| `abel_s20mk2` | 52 | 52 | **52** | 32 | 1,039.2 | 7,875 | 294,038 | 12 | 22 |
| `abel_len_s20mk2` | 52 | 52 | **52** | 32 | 1,039.0 | 7,875 | 294,028 | 27 | 19 |
| `s20mk2_only` | 46 | 48 | **48** | 132 | 1,454.5 | 11,124 | 429,815 | 41 | 54 |

Oracle 52/60, plain greedy 40/60 at 10,000. Both budgets are the same 60 presentations and the same 6,177 candidates — only the solved flags move — so this is a budget-robustness check on one frozen sweep, not a second experiment. What it establishes is negative and worth stating: **a one-or-two-row margin on subset-60 is not a property of the key.** The powered evidence for `(abel, total)` is the ms640 census — 640 presentations at budget 100,000, where re-scoring the searched top 3 under `(abel, length, lex)` came to 420,419 nodes against `_ident`'s 458,688 — not this file.

## The held-out set cannot test this

`results/stable_ac/cov/covsweep_50000_124_subnc2pxysb_mrl24_cyc_aca124_07_21_26.jsonl` covers the 124 unsolved representatives at budget 50,000, and **0 of its 124 presentations have any solving CoV candidate at all**. Every arm scores zero, so it separates nothing. That is the repo's own [control-with-no-dynamic-range](../../experiments/lessons/control-with-no-dynamic-range.md) shape, and it is why the honest scope of this comparison is subset-60.

## Source

- Sweep: `results/stable_ac/cov/covsweep_1000_66_subnc2pxysb_mrl24_cyc_s60r6_07_20_26.jsonl` (cross-checked against `results/stable_ac/cov/covsweep_10000_66_subnc2pxysb_mrl24_cyc_s60r6_07_20_26.jsonl` by gate 1)
- Table: [`abel_tiebreak_b1k_subset60.csv`](abel_tiebreak_b1k_subset60.csv)
- Runner: `experiments/heuristic_search/runners/abel_tiebreak_b1k.py` (`python3 -m experiments.heuristic_search.runners.abel_tiebreak_b1k`)
- Incumbent numbers it is read against: [`ABEL_TOPK_COV_B1K.md`](ABEL_TOPK_COV_B1K.md)
