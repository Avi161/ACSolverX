# The best heuristic — what to use, by node budget

The short answer, then the evidence and the caveats. Everything here is measured on the greedy substitution search with the heap ordering swapped; nothing else about the search changed, so every number is attributable to the ordering alone.

## Use this

**One shape wins at every budget: phase the ordering at total length 16.** While the pair is longer than 16 letters, order by a structural climb (tolerate a temporarily worse-by-length state if it is structurally better); once it is 16 or shorter, revert to pure length and cash in. The phase boundary sits where the two-hump barrier is, and reverting below it is not optional — the `inverted` direction (structure when short, length when long) never beat the baseline.

The right denominator is **the 24 rows in difficulty bins 4–7** — the ones that are neither free (bins 0–3, which every ordering solves) nor out of reach (bins 8–9 and the reach rows, which nothing solves at ≤1000). That is where an ordering is actually tested.

| your node budget | the ordering to use | bins 4–7 (of 24) | full 66 | held-out /15 (leak-free) |
|---|---|---|---|---|
| **~500** | `while L>16: L + 8·knots − 6·xy-imbalance;  else: L` | **16** (baseline 2) | 40 | 13 (baseline 9) |
| **~1000** | `while L>16: L + 2.5·knots + 6.4·max-knots + 8.5·smaller-block + 3.3·xy-imbalance;  else: L` | **19** (baseline 5) | 43 | 15 (baseline 9) |

At budget 1000 that is a near-4× improvement on the rows in question (5 → 19 of 24), and on the leak-free held-out slice the tuned ordering solves **all 15** where the baseline solves 9. It also solves *shorter*: on the 29 rows both solve at 1000, mean path **17.3 vs 19.2** — a win on the secondary criterion too.

`L` = total length of the pair. `knots` = `max(#x-blocks, #y-blocks)` summed over both relators. `max-knots` = the larger relator's knot count. `xy-imbalance` = `|#x − #y| / L`. `smaller-block` = the smaller of the two generators' mean run-lengths. **Let relators grow to ~48** (they climb to ~30; capping at 24 loses nothing at these budgets but nothing is gained by capping either — see caveats).

Both rows are the *same* config family — a length-16 phase boundary with a structural climb above it and pure length below. What shifts with budget is how rich the climb should be: at 500 a lean knots + generator-imbalance climb is best (a richer one wastes early pops), while at 1000 the richer knots + block climb overtakes it (bins 4–7: 11 → 19 with budget where the lean one holds at 16). That crossover is the whole reason to re-tune at the budget you run.

**One honest wrinkle on the 1000 pick.** The selection procedure actually chose a *block* climb (`while L>16: L − 2·max-block + 5·smaller-block`) — it and the knot climb both reach 43/66 and both solve 15/15 on the held-out slice, a dead tie. I recommend the knot climb above because it is the more principled (it is what the whole study points at) and it is what the budget-1000 promotion (EXP-06) selected; the block config is an equally-good empirical alternative, not a better one. If you want one ordering for both budgets, use the 500 row.

## Why knots, and why phased

- **Knots are the signal.** Of the thirteen rotation-invariant state features swept one at a time (EXP-02), knot count moved the needle most: `L + 8·knots` took the baseline from 17/40 to 23/40 on the training slice, and on the *decidable* rows (excluding the 16 easy rows every ordering solves) from 2/10 to 8/10. This is the operational form of the "reduce a knot to open opportunity" idea — a state that bought a knot reduction sorts above one that did not, so the search spends its budget where the structure improves.
- **Phasing is real, not a tuning artifact.** Switching to a structural climb only while the pair is long, and to pure length once short, reached 25/40 (EXP-03) and the joint search pushed it to 27/40 (EXP-04). The control on the *direction* — climbing while short, length while long — never beat the baseline at any threshold, which is what proves the boundary is phasing the search across the barrier rather than just partitioning the queue.
- **The pipeline earns its second stage.** The best ordering at 500 nodes is *not* the best at 1000 (EXP-06): the lean knot climb plateaus (27→27) while a richer multi-feature climb keeps converting budget into solves (25→29). Always re-select at the budget you will actually run.

## The caveats — read these before trusting the numbers

- **This is decidable → decidable generalisation, and the split is leak-free — but the pipeline is not perfectly so.** Train and test share no automorphism class (`splits_aut.json`), so the held-out solves are transfer to genuinely new problems, not change-of-variables twins. The one caveat: the 25 candidates that were re-scored on the aut split were *proposed* by ranking on the stratified train slice, which overlaps the held-out rows — so a config could have entered the shortlist partly for solving a row it is later "held out" on. Treat the held-out fraction (15/15) as an optimistic upper bound, not a clean transfer number. The qualitative claim — baseline 9 → tuned 15 on unseen aut-classes, structure generalises — survives this; the exact figure is soft. The *structure* (phase at 16, climb on knots/blocks) is what is robust; the exact weights are within selection noise, so do not read the third decimal of any weight as meaningful.
- **The second hump is out of reach at ≤1000 nodes, and that is expected.** No presentation in bins 8–9 or the six reach rows solved under any ordering (EXP-08). These need tens of thousands to millions of nodes; a 1000-node budget cannot reach them. The knot ordering does not collapse a second-hump row to a small search — it helps on the decidable rows, which is a different and measurable claim.
- **Knot-*progress* does not predict a solve, even though the knot-*ordering* helps.** A checkpoint proxy — "how many knots did the search shed by node 500" — does not forecast whether it will solve by 1000 (EXP-07: P(solve | dropped a knot) = 0.10 vs 0.14 without; length-progress fails the same way). So for the unsolvable second hump there is no honest progress signal to rank orderings by, and this recommendation is for the decidable regime only. Tuning the climb to be stronger for harder (longer) presentations — the length-tiered knot weight — is the natural next step, but it is an unvalidated extrapolation until the second hump becomes measurable at a larger budget.
- **Path length is secondary, as requested.** The winners' solved paths average ~18 moves on the test slice; the baseline solves none of those rows, so there is no path to compare against there. Where both solve (the easy rows) paths are within a move or two of the baseline's.

## How this was produced

Eight experiments, each with its raw jsonl and a report in this directory; the index is in `README.md`. The search kernel (`hfast.py`) does one numba call per pop and is pinned bit-identical to the reference solver on the states where they could differ (`test_hfast.py`, `verify_fast.py`). Selection used the difficulty-stratified split; the final winner and this held-out number used the automorphism-disjoint split, read once.
