# The length limit, and why climbing is what solves these

Two questions, one answer. The length corridor was never the constraint; the
priority function always was. This document gives the numbers for both.

---

## 1. The length limit

### Where the cap lives, and what it bounds

The cap is **per relator, not per pair**, and it is a filter on insertion:
a child is refused entry to the queue if either of its two relators exceeds it.

    experiments/heuristic_search/core/hexpand.py:344   if len_oth > cap: continue
    experiments/heuristic_search/core/hexpand.py:375   if m > cap:       continue

`hcompact.py:658` bounds it: `1 <= max_relator_length <= 255`.

### The field that says the cap is binding is not a measurement

    experiments/search/run_leftovers_5m.py:721
        "budget": budget, "max_relator_length": mrl,

`max_relator_length` in every jsonl record is **the configured `--mrl` flag,
echoed back**. It reads 64 on every row ever run at `--mrl 64` — including the
31 greedy rows whose longest popped pair totals 33. It measures nothing.
`min_relator_length` is a *total* (`|r1|+|r2|`), not a per-relator minimum.
Read together as a range they say "min 17 / max 64" for any mrl-64 row and
falsely suggest the search is pressed against the corridor.

| field | what it actually is |
|---|---|
| `max_relator_length` | the `--mrl` flag. Not a measurement. |
| `min_relator_length` | best **total** `\|r1\|+\|r2\|` reached |
| `max_relator_length_expanded` | largest **total** ever *popped* |
| `max_relator_expanded` | that pair, as words |
| `max_relator_length_discovered` | largest total ever *discovered* (added in `c8741bef`; older records lack it) |

### What the search actually reaches

Measured with the engine's own counters on `ac19_44381`, cap 64:

| budget | states discovered | largest total **discovered** | largest total **popped** | longest single relator |
|---:|---:|---:|---:|---:|
| 200,000 | 28,808,038 | 75 | 45 | **42** |
| 500,000 | 75,046,588 | 82 | 47 | — |

And in the finished 10M archive, across all 40 completed `ac19_10m` row-runs —
400 million popped nodes — the longest single relator ever produced is **39**.
On the three rows that mattered, after **ten million nodes**:

| row | longest popped pair | total | longest single relator | cap |
|---|---|---:|---:|---:|
| ac19_44381 | [23, 30] | 53 | 30 | 64 |
| ac19_51034 | [21, 33] | 54 | **33** | 64 |
| ac19_65753 | [21, 33] | 54 | **33** | 64 |

It never got within half the cap.

### The cap scan

`ac19_44381`, 200,000 nodes, four caps:

| cap | states discovered | largest total discovered | longest discovered pair | nodes/sec |
|---:|---:|---:|---|---:|
| 64 | 28,808,038 | 75 | 33 + 42 | 3,018 |
| 96 | 28,808,038 | 75 | 33 + 42 | 1,980 |
| 128 | 28,808,038 | 75 | 33 + 42 | 1,942 |
| 255 | 28,808,038 | 75 | 33 + 42 | 1,992 |

**Bit-identical, four ways** — same state count, same extremes, same words.
Confirmed on `ac19_51034` and `ac19_65753` at caps 64/96/128 as well.

The ~33% throughput loss is not the row width — the arena settles at the same
`w = 12 B/relator` at cap 64 and cap 255 alike, because it packs at the
*current* width (`off = sid * rw`, `rw = 2*self.w`, widened in place), not the
cap width. It is `maxc = 4*(cap+1)^2`, the per-pop child bound: 16,900 entries
at cap 64 against 262,144 at cap 255.

### The bound

> **Every relator of every child — accepted or rejected — is bounded by the
> total of the state that produced it.**

A child is `r_i ← rot(r_i)·rot(r_j^±)` with the other relator kept, so the new
relator has length at most `|r_i| + |r_j|` (the popped total) and the kept one
has length `|r_j|`, also at most the popped total.

Consequence: a run whose largest popped total stays under the cap **cannot have
had a single child rejected by it**. That total is recorded on every row as
`max_relator_length_expanded`. Across the nine open rows at 10M it is 50, 52,
53, 54, 54, 54, 54, 54, **55** — worst 55 against a cap of 64. The cap rejected
zero children in ninety million popped nodes.

The *form* of the bound is structural and holds at any budget; the *value*
(the largest popped total) is measured and does grow slowly with budget — 45 at
200k, 47 at 500k, 53–55 at 10M. So the right way to ask "did the corridor
bind" on any future run is to read `max_relator_length_expanded` off the
finished record, not to widen the cap speculatively.

### Practical consequence

**Raising `mrl` cannot change any result on these rows, so no run at a wider
cap is worth buying.** It costs about a third of the throughput and returns a
bit-identical search.

---

## 2. Climbing

### Solutions go up before they come down

Every solved path was measured for the total `|r1|+|r2|` at each step: where it
starts, the highest it reaches, where that peak falls, and where it ends (2,
the trivial pair).

The three rows nothing else could solve:

| row | start | **peak** | peak at step | end |
|---|---:|---:|---:|---:|
| ac19_44381 | 19 | **23** | 8 of 72 | 2 |
| ac19_51034 | 17 | **28** | 5 of 48 | 2 |
| ac19_65753 | 20 | **28** | 6 of 49 | 2 |

`ac19_51034` in full — the shape is unmistakable, up for five steps, then a
long descent:

    17, 23, 23, 21, 21, 28, 27, 28, 27, 28, 27, 24, 25, 22, 21, 19, 20, 19,
    24, 19, 21, 19, 22, 21, 20, 19, 21, 21, 21, 21, 21, 19, 19, 17, 17, 16,
    17, 15, 16, 13, 13, 12, 11, 10, 9, 7, 4, 3, 2

It must reach a presentation **65% longer than the one it started with** before
any route down exists.

### Climbing is not universal — it scales with difficulty

From the extended screen at budget 1,000, bucketed by how many nodes the solve
actually cost (40,411 solved rows measured):

| nodes to solve | N | climb > 0 | rate | median climb |
|---|---:|---:|---:|---:|
| 1 – 9 | 6,968 | 1,503 | **21.6%** | 0 |
| 10 – 99 | 30,745 | 16,862 | **54.8%** | +1 |
| 100 – 500 | 2,504 | 1,970 | **78.7%** | +2 |
| 501 – 1,000 | 194 | 155 | **79.9%** | +2 |
| all | 40,411 | 20,490 | 50.7% | +1 |

And from the 5M hcompact certificates — every solved row that stored a path,
these being rows that had already survived a million nodes:

| sample | N | climb > 0 | median climb | max |
|---|---:|---:|---:|---:|
| greedy solved at 5M | 57 | **57 (100%)** | +15 | +20 |
| s20_mk2 solved at 5M | 5 | **5 (100%)** | +22 | +22 |

A representative hard row: **`ac19_68854`** starts at total 19, climbs to **39**
— more than double — peaking at step 4 of 106, and descends to 2. It cost
1,600,407 nodes.

**Trivial rows walk straight downhill. Rows that need real search almost always
climb first, and every row that needed more than a million nodes did.**

---

## 3. `s40_gen`: what actually solved them

| row | starter budget | nodes | mixed steps | elementary AC moves | seconds |
|---|---:|---:|---:|---:|---:|
| ac19_44381 | 1,000 | **984** | 72 | 30,679 | 1.0 |
| ac19_51034 | 5,000 | **4,272** | 48 | 14,249 | 5.3 |
| ac19_65753 | 5,000 | **4,274** | 49 | 12,964 | 4.9 |

Run as `cascade_heuristics.search(pair, budget=SB, cap=64, starter_budget=SB)`
with `SB` the starter budget in the table, so `s40_gen` receives the whole
allowance and the `s20_mk2` fallback never runs. At the shipped default of
**500** all three fail; at 900 all three still fail. `ac19_44381` crosses
between 900 and 1,000, the other two between 2,000 and 5,000.

Against `s20_mk2` at **10,000,000 nodes**, which failed all three twice, at
2,205–2,997 seconds and 90–108 GB each.

### Why `s40_gen` climbs and `s20_mk2` does not

Both search by popping the cheapest state first. `s20_mk2` scores a state
`L + 20*S + 2*MK`, where **`L` is the total length** — so a longer presentation
is literally more expensive to look at, and a row that must pass through total
28 to escape from 17 is asking the queue to promote states it is charging 65%
more for. Over ten million pops it never promoted the right ones.

`s40_gen` scores `L + 40*S` — no `MK` term, and double the weight on `S` — so
length is a much smaller share of the score, and it additionally puts **Nielsen
images** (change-of-basis moves) in the queue beside ordinary AC substitutions.
The result is an ordering that will pay to go uphill. It found the same
climbing routes in a few thousand pops.

---

## 4. The one-line version

> **The cap was never the lever and the priority always was: after ten million
> nodes the search had not reached half the length it was allowed, so nothing
> external was stopping it — what stopped it was its own ordering charging too
> much for the climb that every hard solution requires.**
