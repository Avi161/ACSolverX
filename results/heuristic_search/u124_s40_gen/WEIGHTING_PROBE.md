# The u124 floor does not move with the priority function

A cheap test of one hypothesis: `s40_gen` is `L + 40*S` with **`mk_weight = 0`**,
so it discards the MK signal that `s20_mk2` carries. If u124's rows need MK,
no budget on this arm would ever find it, and a flat result at any budget
would be an artefact of the arm rather than a fact about the presentations.

**The hypothesis is wrong, and cleanly so.**

## The run

4 rows, 6 weightings, 10,000 nodes, cap 128, `mixed_search` with
`arm='aut_edges'`. Rows are the start-25 band, where all of u124's observed
movement lives: `aca_99`, `aca_107`, `aca_110`, `aca_113`.

| weighting | totals reached | floor |
|---|---|---:|
| `s40_gen` L+40S | 22, 23 | **22** |
| `s20_mk2` L+20S+2MK | 22, 23 | **22** |
| L+40S+2MK | 22, 23 | **22** |
| L+40S+8MK | 22, 23 | **22** |
| L+20S+8MK | 22, 23 | **22** |
| L+10S+5MK | 22, 23 | **22** |

24 of 24 jobs. **Below 22: zero. Solved: zero.** Per row the floor is
identical under every weighting -- `aca_99`, `aca_107` and `aca_110` floor at
22, `aca_113` at 23 -- and it does not move by even 1.

## Why this is more than a null

The six searches are not doing the same thing.
`max_relator_length_seen` spans **45 to 81** across the grid: `L+20S+8MK`
climbs to relators of 81 where `s40_gen` reaches only 45, a 1.8x spread in
the territory explored. Six searches that wander through visibly different
regions of the space bottom out at the same total. That is an invariance,
not a coincidence of identical runs.

The cap did not bind: 81 against 128.

## What it establishes, with the budget axis

Two independent axes now say the same thing about the same floor:

| axis | range tested | floor moves by |
|---|---|---|
| budget | 10,000 -> 500,000 (50x) | at most 2 |
| priority | 6 weightings over the S and MK terms | 0 |

The honest statement is therefore about the presentations, not the search:
**the floor is a property of these rows, not of the priority function or of
the budget.** A solve needs total length 2; the start-25 rows reach 22 and
stop, and six rows sitting natively at 22 never move at all. The 25s carry
about three units of removable slack above a wall the whole set shares.

That reframes what more nodes can buy. It does not make u124 solvable, and it
is worth more than another budget rung that was never going to travel the
remaining 20 units.

## Files

`u124_weighting_probe_b10000_mrl128.jsonl` -- one record per job, with
`minTOT`, `maxrel`, `maxpop`, `nodes` and wall time.
