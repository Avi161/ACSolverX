# s40_gen on u124: zero solves, and a better zero than the incumbent's

`s40_gen` at a raised starter budget solved the three AC19 rows that
10,000,000 nodes of `s20_mk2` could not (`../ac19_residue_solved/`). The
obvious question is whether it does the same to u124 -- 124 rows, **0 solved
at 10,000,000 nodes each**, and `s40_gen` had never been run on it.

It does not. **0 of 124.**

    PYTHONPATH=. python -m ... cascade_heuristics.search(
        pair, budget=10000, cap=64, starter_budget=10000)

10,000 is the ceiling: `cascade_heuristics.py:15` validates
`0 <= starter_budget <= 10000`, so this is the most the cascade's API will
give the component. 124 rows, 35 minutes on two cores, no errors.

## But it reaches the same floor a thousand times cheaper

The reduction metric -- the best total `|r1|+|r2|` a row ever reaches -- is
what an unsolved row has to show for itself.

| | budget/row | rows that improved on their start | strictly better than the other |
|---|---:|---:|---:|
| `s20_mk2` | **10,000,000** | 14 / 124 | 0 |
| `s40_gen` | **10,000** | **16 / 124** | **3** |

`s40_gen` is never worse on any row, ties on 13, and strictly beats the 10M
baseline on three:

| row | start | `s40_gen` @ 10,000 | `s20_mk2` @ 10,000,000 |
|---|---:|---:|---:|
| aca_36 | 18 | **16** | 17 |
| aca_108 | 25 | **24** | 25 |
| aca_112 | 25 | **24** | 25 |

and matches it at 22 from a start of 25 on `aca_99`, `aca_100`, `aca_107`,
`aca_110` -- the deepest reductions either arm has ever found on this set.

**At one thousandth of the budget it reaches the same floor or better,
everywhere.**

## What the zero actually says

On AC19 the residue was an ordering problem: `s20_mk2` charged too much for
the climb, `s40_gen` paid it, and 10,000,000 nodes lost to 984. On u124 both
orderings stop in the same place, and 108 of 124 rows never improve on the
pair they were handed at all -- under either arm, at either budget.

So `s40_gen`'s advantage is real but bounded: **it is a much better search,
not a different barrier.** Whatever stops u124 is not the priority function,
which is the one thing AC19's residue turned out to be.

Nor is it the length corridor. The longest single relator `s40_gen` ever
reached here is **53** against a cap of 64 (median 39). The five u124 rows
whose largest *popped* total reaches 64-65 under `s20_mk2` are the only place
in either campaign where the bound of RUNBOOK section 10 leaves the cap
undetermined, and even there the longest single relator popped is 48.

## Files

`u124_s40_gen_starter10000.jsonl` -- one record per row: solved, winner,
nodes, best total reached (`minTOT`), longest relator seen, seconds.
