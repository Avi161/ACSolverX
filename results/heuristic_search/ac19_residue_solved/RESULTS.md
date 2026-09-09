# The AC19 residue is solved: 72,779 / 72,779

`ac19_44381`, `ac19_51034` and `ac19_65753` were the mutual residue of every
arm at every budget. `s20_mk2` failed all three at **10,000,000 nodes, twice**
(`results/heuristic_search/ac19_10m/`, and a fresh campaign re-run), 2,205 to
2,997 seconds and 90 to 108 GB each. The 501-node cascade prefix failed them.
The 12-row benchmark put them among the nine rows the cascade lost.

They solve in **984, 4,272 and 4,274 nodes -- about six seconds for all three
on one core.**

## What changed

Nothing in the engine, the cap, or the node budget. One parameter:
`cascade_heuristics.search(starter_budget=...)`, the allowance given to the
`s40_gen` component, off its **500-node default**.

| row | starter budget that solves | nodes | mixed steps | elementary AC moves | seconds |
|---|---:|---:|---:|---:|---:|
| ac19_44381 | 1,000 | 984 | 72 | 30,679 | 1.0 |
| ac19_51034 | 5,000 | 4,272 | 48 | 14,249 | 5.3 |
| ac19_65753 | 5,000 | 4,274 | 49 | 12,964 | 4.9 |

At starter 500 -- the shipped default -- all three fail. At 900 all three still
fail. `ac19_44381` crosses between 900 and 1,000; the other two between 2,000
and 5,000. The default was 500, and 500 was the only value ever run.

## These are AC certificates, replay-verified

`s40_gen` searches Aut(F2) moves alongside AC substitutions, so the raw path is
mixed: 55 of 72 steps are AC substitutions for `ac19_44381`, 33 of 48 for
`ac19_51034`, 34 of 49 for `ac19_65753`; the rest are Nielsen images.
`ac_decode.decode_elementary` pushes the basis change back through the path and
`replay_elementary` replays the result letter by letter, from the original
presentation, with no search in the loop:

    ac19_44381: 30,679 elementary AC moves -> ['x', 'y']
    ac19_51034: 14,249 elementary AC moves -> ['x', 'y']
    ac19_65753: 12,964 elementary AC moves -> ['x', 'y']

All three land on the trivial pair. Regenerate and re-verify with

    PYTHONPATH=. python -m experiments.search.verify_ac19_residue

`certificates.json` stores the **mixed** path (72 / 48 / 49 steps, 22 kB), not
the elementary expansion (58,000 moves) -- the campaign convention, since the
decoder regenerates the expansion on demand.

## Every solve climbs, and the harder the row the more certain that is

The paths go UP before they come down:

| row | start total | peak total | peak at step | end |
|---|---:|---:|---:|---:|
| ac19_44381 | 19 | 23 | 8 of 72 | 2 |
| ac19_51034 | 17 | 28 | 5 of 48 | 2 |
| ac19_65753 | 20 | 28 | 6 of 49 | 2 |

Across the whole corpus climbing is not universal -- it is a function of
difficulty. From the 5M hcompact certificates (`leftovers_5m`, every solved row
that stored a path):

| sample | rows | climb > 0 | median climb | max |
|---|---:|---:|---:|---:|
| greedy solved at 5M | 57 | **57 (100%)** | +15 | +20 |
| s20_mk2 solved at 5M | 5 | **5 (100%)** | +22 | +22 |

and from the extended screen at budget 1,000, bucketed by search cost:

| nodes to solve | rows | climb > 0 | median climb |
|---|---:|---:|---:|
| 1 - 10 | 5,496 | 21.4% | 0 |
| 10 - 100 | 24,026 | 54.8% | +1 |
| 100 - 501 | 1,949 | **78.3%** | +2 |
| 501 - 1,001 | 158 | **79.1%** | +2 |

Trivial rows walk straight downhill. Rows that take real search essentially
always climb first, and every row that needed more than a million nodes did.

## What this says about the cap, and about the priority

The three rows were never limited by the length corridor. After 10,000,000
nodes at cap 64 the longest single relator any of them ever reached was **33**
-- see RUNBOOK section 10, where the bound is proved rather than sampled. They
were limited by what the search would agree to pop.

`s20_mk2` orders by `L + 20*S + 2*MK`, with `L` the total length. A row that
must reach total 28 from a start of 17 is asking the queue to promote states
`L` is charging 28 for, and at 10,000,000 pops it never promoted the right
ones. `s40_gen` -- `L + 40*S`, no `MK`, with Nielsen images in the heap --
promoted them inside 5,000.

So the residue was a **priority** result, not a corridor result and not a
budget result. 10,000,000 nodes of the wrong ordering lost to 4,274 nodes of a
better one.

## Status

With these three, the AC19 aut-min screen is **72,779 / 72,779**. The extended
set was already 156,762 / 156,762. No AC19 row is open.
