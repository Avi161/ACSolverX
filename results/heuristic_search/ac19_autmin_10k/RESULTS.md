# ac19_autmin_10k: greedy and s20_mk2 over all 72,779 AC19 orbits

Status: **COMPLETE, both arms**. 72,779 / 72,779 rows each, oracle clean.
Branch `claude/ac19-leftover-solver-notebook-6yan6d`. Not merged to main.
Engine memory generation 6, `hcompact`, cap 48, budget 10,000.

## Why it was run

The original 1k/10k wave over these orbits ran in Colab on 2026-07-31 and
only its **failure** lists came back into the repo:
`ac19_autmin_screen/unsolved_10k_baseline.csv` (831 rows) and
`unsolved_10k_s20_mk2.csv` (259). The per-row costs of the ~72k rows that
**solved** were never committed. Every rung above this one is a funnel --
each ran only the rung below's failures -- so the 100k / 1M / 5M / 10M
jsonls add depth on those same 831 and 259 and not one extra
presentation.

The visible consequence was in the week-9 deck: its three-arm comparison
rested on **225 rows**, the mutual 10k failures, because a mutual failure
was the only kind of row the archive priced for both arms. Everything the
two arms solved under the screen was unpriced, and the figures had to draw
a 1-to-10,000 bracket over 98% of the population.

This run reverses the earlier "do not run greedy or s20_mk2 again on those
~72k", on the operator's explicit later direction to re-run both arms
locally and push the result so it cannot be lost twice.

## What was run

    PYTHONPATH=. python3 -m experiments.search.run_ac19_autmin_10k run --arm greedy
    PYTHONPATH=. python3 -m experiments.search.run_ac19_autmin_10k run --arm s20_mk2
    PYTHONPATH=. python3 -m experiments.search.run_ac19_autmin_10k verify --arm greedy
    PYTHONPATH=. python3 -m experiments.search.run_ac19_autmin_10k costs

Row list `ac19_autmin_screen/ac19_autmin_orbits.csv`, all 72,779 orbits.
The runner calls `run_leftovers_1m._job` verbatim, so the records are
byte-comparable with the 100k rung's; what it supplies is a persistent
pool, because both older runners give every row a fresh interpreter --
right at 25-80 minutes a row, ruinous at 20-30 ms.

**One pass at 10,000 rebuilds both lost waves.** A search at budget *B* is
exactly the first *B* pops of a longer one, so a row that solves at 340
nodes records 340 whether the ceiling was 1,000 or 10,000. The 1,000-node
rung is read off the same file by filtering `nodes_explored <= 1000`; no
second pass was needed. **Cap 48 is not a free choice**: it is what the
100k/1M/5M rungs ran at, and a different cap would be a different search
that could not be spliced onto them.

## Cost

| quantity | greedy | s20_mk2 |
|---|---:|---:|
| rows | 72,779 | 72,779 |
| CPU | 0.58 core-hours | 0.42 core-hours |
| per row | 28.6 ms | 20.9 ms |
| wall, 3 workers on 4 cores | 12.1 min | 8.5 min |
| errors, reservation failures | 0 | 0 |

## What came back

| | greedy | s20_mk2 |
|---|---:|---:|
| solved at 10,000 | 71,936 | 72,519 |
| unsolved at 10,000 | 843 | 260 |
| **solved within 1,000** | **66,086** (90.8%) | **68,475** (94.1%) |
| mean nodes (solved rows) | 311.7 | 217.4 |
| median nodes | 14 | 14 |
| p90 | 659 | 339 |
| max | 9,943 | 9,916 |
| mean path length | 27.7 | 25.9 |
| median path length | 12 | 11 |

"Most of them solve in less than 1k budget" is right by a wide margin:
90.8% of the whole screen under greedy, 94.1% under s20_mk2.

## Difficulty bands (solved rows, share of all 72,779)

| band | greedy n | share | mean | median | s20_mk2 n | share | mean | median |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| < 10 | 24,202 | 33.25% | 6.8 | 7 | 21,957 | 30.17% | 6.8 | 7 |
| 10-100 | 30,430 | 41.81% | 29.2 | 19 | 36,282 | 49.85% | 27.4 | 17 |
| 100-1k | 11,450 | 15.73% | 330.7 | 267 | 10,233 | 14.06% | 313.5 | 212 |
| 1k-10k | 5,854 | 8.04% | 3,003.0 | 2,833 | 4,047 | 5.56% | 2,820.0 | 2,383 |

## THE ORACLE PASSED, WHICH IS THE POINT

Every row in the archived 10k failure lists was searched at exactly this
budget and this cap by the original wave, did not solve, and ran the full
10,000 pops. A faithful re-run must reproduce that on every one of them --
the same verdict **and** the same node count.

| arm | archived failures | reproduced (verdict + node count) | now solve |
|---|---:|---:|---:|
| greedy | 831 | **831** | **0** |
| s20_mk2 | 259 | **259** | **0** |

Those rows were judged by a different engine generation, on a different
machine, eight weeks earlier. So this is not only a sanity check on the
re-run: it is a **cross-generation bit-identity check over 72,779 rows**,
of the kind `perf_lab`'s gates do over 60. Had any archived failure solved
here, the splice onto the 100k/1M/5M rungs would have been invalid and the
correct move would have been to stop.

`verify` exits nonzero on any of: an archived failure that solves, an
archived failure that stops at a different node count, or more
unexplained failures than the coverage gap allows.

## Coverage: 12 and 1 new failures, both inside the gap

The original wave judged **71,556** of the 72,779 orbits on greedy and
**71,582** on s20_mk2 (`hsearch_ac19_hard100k/RESULTS.md`), leaving 1,223
and 1,197 it never saw. This run judges all 72,779, so it may legitimately
fail on rows the archive never judged -- 12 on greedy, 1 on s20_mk2, both
far inside the bound. Those rows have no higher rung above them, since the
100k/1M/5M lists were built from what the wave saw; the deck counts them
as `unescalated` and drops them rather than guessing a cost.

## The 13 never-escalated rows are closed

The re-run left 12 greedy rows and 1 s20_mk2 row that failed at 10,000 with no
higher rung above them -- every later list was built from what the original wave
saw, and it never judged them. That is the whole residue of the coverage gap,
and it is now empty.

Derived by `experiments/search/make_ac19_unescalated_lists.py` (never by hand)
and run up the same ladder at the same cap 48 by the runner that owns those
rungs, into `results/heuristic_search/ac19_unescalated/`:

    PYTHONPATH=. python3 -m experiments.search.make_ac19_unescalated_lists --write
    PYTHONPATH=. python3 -m experiments.search.run_leftovers_1m --arm greedy \
        --budget 100000 --floor 10000 \
        --csv-path .../unescalated_10k_baseline.csv --out-dir .../ac19_unescalated

| arm | rows | solved at 100,000 | solved at 1,000,000 | still open |
|---|---:|---:|---:|---:|
| greedy | 12 | 11 | **12** | **0** |
| s20_mk2 | 1 | **1** | — | **0** |

29 s and 14 s of wall clock. Costs run 11,431 to 44,793 nodes at the 100k rung;
the one row that needed 1,000,000, `ac19_48537`, solved at **202,390**. The
single s20_mk2 row, `ac19_33435`, solved at **62,705** -- and it is not a random
gap row: `run_leftovers_1m.COMMON_DENOMINATOR_EXCLUDED` names it as the one
orbit outside the 70,723 both arms searched at 10k, so this closes that
discrepancy on that arm from the other end.

None of the 13 was a hard presentation. The cascade settles all of them at 54 to
23,393 nodes, and `s20_mk2` settles 11 of greedy's 12 inside 10,000. They were
one arm's blind spots that the coverage gap happened to hide.

Every solve is above its row's 10,000-node floor -- the minimum is 11,431 -- so
the same "wrong search is running" check that the 10k oracle applies from below
holds here from above. `run_leftovers_1m.classify` now takes that floor as a
parameter rather than hardcoding 100,000, which on this list would have made the
check silently vacuous while still printing.

**Both arms are now complete over the population**: greedy 72,751 measured + 28
censored at 10,000,000; s20_mk2 72,770 + 9. Nothing is unmeasured at an
unstated budget.

## greedy vs s20_mk2, on all 72,779 for the first time

| | rows |
|---|---:|
| both arms solve | 71,903 |
| **s20_mk2 solves, greedy does not** | **616** |
| **greedy solves, s20_mk2 does not** | **33** |
| neither solves at 10,000 | 227 |

On the 71,903 both solve:

| | greedy | s20_mk2 |
|---|---:|---:|
| total nodes | 22,320,350 | 13,685,373 |
| median nodes | 14 | 14 |
| rows where this arm is cheaper | 17,431 | 32,418 |
| ties | 22,054 | 22,054 |

s20_mk2 does **1.63x** less total work and is cheaper on 45.1% of rows
against greedy's 24.2%, with 30.7% ties. That is a much narrower result
than the "5.7x smaller residual" the 100k rung reports, and both are true:
the ordering's advantage is concentrated in the hard tail, and on the bulk
of the screen the two arms mostly agree, often to the node.

**s20_mk2 is not uniformly stronger.** 33 rows greedy solves inside 10,000
nodes that s20_mk2 does not, and in the archived failure lists the same
asymmetry appears as 34 rows. A claim that one ordering dominates the other
is false at this budget.

## Files

| file | what |
|---|---|
| `ac19_autmin_10k_greedy_b10000_mrl48.jsonl` | 72,779 records, greedy |
| `ac19_autmin_10k_s20_mk2_b10000_mrl48.jsonl` | 72,779 records, s20_mk2 |
| `ac19_autmin_10k_costs.csv` | 145,558 rows: name, arm, solved, nodes_explored, path_length |

Record schema is `run_leftovers_1m._job`'s, unchanged: `name, arm, r1, r2,
budget, max_relator_length, solved, nodes_explored, path_length,
min_relator_length, max_relator_length_expanded, seconds`. No move
sequences -- `path_length` is identical with and without capture (checked
on a 40-row sample: 0 of 40 differ), and 145,558 certificates are not what
this rung is for. A certificate for any named row is recovered by re-running
that row with capture on at its recorded `nodes_explored`; the search is
deterministic.
