# ac19_s40_1k: is `s40_gen` a strong algorithm on its own?

Status: **COMPLETE**, both arms, 72,779 / 72,779 rows each.
Branch `claude/ac19-leftover-solver-notebook-6yan6d`. Not merged to main.
Budget 1,000 nodes, cap 255, `heuristic_1k.mixed_search`.

## The question

`s40_gen` is the cascade's third stage and settles more of the screen than any
other -- 53,624 of 72,779. But it had only ever been measured **inside** the
cascade, after the BS rewrite stage has already taken the easy rows. Run bare
over the whole screen at a 1,000-node budget, how strong is it, and how does it
compare with `s20_mk2` at the same budget?

## The design: one knob apart in each direction

A three-way comparison is worthless if the arms differ in three ways at once,
so each pair here moves exactly one thing:

| arm | priority | move set | engine / cap |
|---|---|---|---|
| `s40_gen` | L + 40·S | AC substitutions **+ 4 Nielsen basis changes** | mixed_search / 255 |
| `ac501` | L + 40·S | AC substitutions only | mixed_search / 255 |
| `s20_bare` | L + 20·S + 2·MK | AC substitutions only | mixed_search / 255 |
| `s20_mk2` | L + 20·S + 2·MK | AC substitutions only | hcompact / 48 |

`s40_gen` vs `ac501` isolates the **move set**. `s40_gen` vs `s20_bare`
isolates **priority + move set**. `s20_bare` vs `s20_mk2` isolates **engine and
cap** -- and that last pair is why this study can be read at all (below).

## Results

| arm | solved | share | AC-certified | share | aut-assisted | unsolved | median | p90 | mean |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `s40_gen` | **70,391** | **96.7%** | 12,741 | 17.5% | 57,650 | 2,388 | 14 | **88** | **43.2** |
| `s20_bare` | 68,475 | 94.1% | 68,475 | 94.1% | 0 | 4,304 | 13 | 158 | 63.6 |
| `ac501` | 66,184 | 90.9% | 66,184 | 90.9% | 0 | 6,595 | 16 | 162 | 65.6 |

Cost: `s40_gen` 1.47 core-hours (0.073 s/row), `s20_bare` 1.83 (0.091 s/row).

**`s40_gen` reaches furthest AND costs least per row.** Its p90 is 88 nodes
against 158 and 162; its mean is 43.2 against 63.6 and 65.6. The medians are
within a node of each other, so the whole advantage is in the tail: the rows
that are awkward for an AC-only search are exactly the ones a basis change
cracks quickly.

## What the Nielsen door actually buys, and what it costs

Against its exact control:

| | rows |
|---|---:|
| both `s40_gen` and `ac501` solve | 65,843 |
| **`s40_gen` only** | **4,548** |
| **`ac501` only** | **341** |

Net **+4,207**, so the basis moves are worth about 5.8 points of reach. But it
is not a strict improvement: 341 rows the AC-only search settles are lost,
because four extra children per popped node spend budget the deeper AC-only
search would have used. Same against `s20_bare`: +2,465 / −549.

The cost is bookkeeping, not mathematics. **79.2% of `s40_gen`'s solves change
basis**, so their certificate is not in AC form. That is what
`aut_assisted_s40_gen_b1000.csv` (57,650 rows) records.

## The aut-assisted rows really are AC solves -- spot-checked, not assumed

10 rows drawn at random from the 57,650, re-run with capture and pushed through
`experiments/search/ac_decode.py`:

| row | steps (of which automorphism) | elementary AC moves | basis tail |
|---|---:|---:|---:|
| ac19_5475 | 7 (1) | 5 | 0 |
| ac19_50045 | 7 (3) | 6 | 2 |
| ac19_39320 | 13 (1) | 11 | 0 |
| ac19_51854 | 23 (5) | 23 | 5 |

**10 of 10** decoded and replayed from the original input to a terminal pair,
with a basis tail of 0 to 5 moves. So the 17.5% is a state of the archive, not
a mathematical limit: the conversion exists, is cheap, and works.

**It has not been run over all 57,650.** Until it is, 96.7% is the reach and
17.5% is what is certified today, and quoting the first without the second
overstates the arm against `s20_mk2`, whose solves are always substitution-only.

## A free result: the two `s20_mk2` measurements are bit-identical

`s20_bare` (Python `mixed_search`, cap 255) and the campaign's `s20_mk2`
(numba `hcompact`, cap 48) solve **the same 68,475 rows**, and agree on the
**node count of every single one** -- symmetric difference 0, disagreements 0.

Two engines, two caps, 72,779 rows, no exceptions. That is the property
`perf_lab`'s gates check over 60 rows, obtained here over the whole screen as a
side effect. It also removes the confound this study was most at risk from: the
engine and the cap make no difference at this budget, so every difference in
the table above is priority and move set, and nothing else.

## Verification

* 72,779 rows per arm, unique names, `solved + aut_assisted + unsolved` = 72,779.
* `aut_assisted` is **0** for `ac501` and `s20_bare`, asserted rather than
  observed -- neither arm can emit a basis move, so a nonzero count would mean
  the arm dispatch is wrong.
* `ac501`'s total is the union of (solved at 501) and (solved at 1,000 over the
  501-residue), taken as a set rather than by adding the two files.
* 0 rejected certificates on both arms.

## Files

| file | what |
|---|---|
| `ac19_s40_1k_costs.csv` | per (arm, row): solved, aut_assisted, nodes_explored |
| `unsolved_s40_gen_b1000.csv` | 2,388 rows `s40_gen` did not settle |
| `aut_assisted_s40_gen_b1000.csv` | 57,650 rows it settled by changing basis |
| `unsolved_s20_bare_b1000.csv` | 4,304 rows `s20_bare` did not settle |

The 43 MB and 10 MB raw jsonl are gitignored; regenerate with
`run_ac19_cascade_screen run --arm s40_gen|s20_bare --budget 1000`.
