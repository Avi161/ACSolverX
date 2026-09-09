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

---

# Does the dedupe set saturate with budget?

A second hypothesis, raised from the campaign box: MAX peak RSS was 27.53 GiB
at 500,000 nodes and 28.23 GiB at 1,000,000 -- 2x the budget for +2.5% -- so
memory on this path might be budget INDEPENDENT. If it were, 2,000,000 would
cost ~30 GiB per lane rather than the ~105 linear scaling predicts, and every
budget ruled out tonight on memory grounds would reopen.

The mechanism is measurable without waiting for a campaign: stored entries per
POPPED node, and the fraction of generated children already in the store.
Linear growth means every pop still discovers new states; saturation means the
search is re-deriving what it already holds and the duplicate rate is climbing
toward 1.

Measured on `aca_2`, capture off, cap 255, one budget per fresh process:

| budget | stored | per popped node | duplicate rate | RSS delta | KB/node |
|---:|---:|---:|---:|---:|---:|
| 100,000 | 9,510,483 | 95.1 | 0.157 | 1.906 GiB | 20.0 |
| 250,000 | 24,931,026 | **99.7** | **0.163** | 5.391 GiB | 22.6 |

**No saturation, and the trend runs the other way.** Stored entries per popped
node RISE from 95.1 to 99.7. The duplicate rate is flat -- 15.7% to 16.3%
across a 2.5x budget increase. RSS grows 2.83x for 2.5x the budget, mildly
SUPERlinear.

For memory to go budget-independent between 500,000 and 1,000,000 the
duplicate rate would have to climb from about 16% to nearly 100% over that one
interval. Nothing in the measured trend supports that.

**Stated limit on this evidence:** the dev box has 15 GiB of RAM, so 500,000
nodes (~11 GiB) and 1,000,000 (~22 GiB) are not reachable here. The two points
above bracket a lower range than the observation they address. What they
establish is the mechanism and its direction, not a measurement inside the
interval in question.

The far likelier explanation of the campaign reading is the censoring trap
that caught this project three times in one night: the 1,000,000 MAX came from
21 of 124 rows, and the heavy rows land late -- at 500,000 the MAX climbed
21.09 -> 26.28 -> 27.53 as the run progressed. The prediction on record is
that at 124/124 the 1,000,000 MAX lands near twice the 500,000 MAX, roughly
55 GiB, not 28.
