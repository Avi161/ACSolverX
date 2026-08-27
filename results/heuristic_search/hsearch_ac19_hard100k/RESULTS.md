# AC19_extended hard tail @ 100,000 — results

Colab continuation of [`hsearch_ac19_autmin_1k/`](../hsearch_ac19_autmin_1k/) (pulled 2026-08-04, run 2026-07-31). Each arm was re-run **only on the presentations it had left unsolved at budget 10,000**, at budget 100,000, cap 48. Verified against the 10k wave: both residual sets match their arm's 10k-unsolved list exactly — no extras, no gaps.

| | |
|---|---|
| dataset | `ac19_unsolved10k` — the per-arm residual of `AC19_extended_aut_min` (72,779 Aut orbits) |
| budget / cap | **100,000** / 48 |
| arms | `baseline` (length) · `s20_mk2` (L + 20·S + 2·MK) |
| engine | `hcompact`, `N_WORKERS="auto"` |

Layout:
```
results/heuristic_search/hsearch_ac19_hard100k/
  ac19_unsolved10k_baseline_b100000_mrl48.{jsonl,md}   831 rows
  ac19_unsolved10k_s20_mk2_b100000_mrl48.{jsonl,md}    259 rows
  RESULTS.md
```

## ⚠ The two arms have different denominators

`baseline` was re-run on **831** presentations, `s20_mk2` on **259** — because those are the sets each arm failed to solve at 10k. **609/831 vs 220/259 is not a comparison.** Every number below is recomputed over the **common** set of orbits both arms searched.

## Residual set sizes (per arm)

| arm | rows @10k | unsolved @10k | re-run @100k | solved @100k |
|---|---:|---:|---:|---:|
| `baseline` | 71,556 | 831 | 831 | 609 |
| `s20_mk2` | 71,582 | 259 | 259 | 220 |

## Full course, common denominator

70,723 orbits searched by both arms. A search at budget *B* is exactly the first *B* pops of a longer search, so the 100k continuation's `solved_at` / `nodes_explored` are true totals and splice onto the 10k wave without adjustment.

| arm | solved @10k | solved @100k | still unsolved |
|---|---:|---:|---:|
| `baseline` | 69,894 | 70,502 | **221** |
| `s20_mk2` | 70,465 | 70,684 | **39** |

The residual is **5.7× smaller** under the S+MK ordering. Both arms fail on 39 shared orbits; 182 of length's failures are recovered by S+MK, none the other way.

## Node / path efficiency — both-solved subset (70,502)

Per-arm solved-only means are biased: the treatment picks up harder residuals and inflates its own mean. Scored only on orbits **both** arms solved.

| arm | mean nodes | median nodes | mean path | median path |
|---|---:|---:|---:|---:|
| `baseline` | 563.3 | 14.0 | 23.50 | 10.0 |
| `s20_mk2` | 263.2 | 14.0 | 26.57 | 11.0 |

- **Mean nodes halve** (2.14×), **median is identical** — the saving is entirely in the hard tail, not in the typical orbit. Geo-mean ratio **0.81**, cheaper on 32,118/70,502 (45.6%): on a coin-flip of individual rows the length baseline is actually cheaper, and S+MK wins by avoiding the expensive failures.
- **Path length is not improved** — certificates are ~13% longer under S+MK, consistent with the 1M ladder run. The gain is node efficiency, never shorter proofs.

## Caveats carried forward

`ac-advisor` REVISE items from the 10k wave still apply: these are Aut-**minimal representatives** (difficulty is not orbit-invariant), stratify L>19 in any write-up, and exclude the 142 selection-overlap names when scoring `s20_mk2`.
