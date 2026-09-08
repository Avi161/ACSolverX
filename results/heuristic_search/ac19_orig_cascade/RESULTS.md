# Aut-minimising makes these rows harder: the cascade on 8 originals

Lucas Fagan's question, on the AC19 rows that resist large budgets:

> Did you try the original of those presentations, before aut minimizing,
> on 10M nodes?

This is that experiment at the budget where the cascade actually fails,
run locally in **0.6 minutes**. The answer is **yes, the original is
easier** -- by at least 7.5x and probably far more.

## The comparison

Both sides are the SAME configuration: `cascade501`, budget 100,000,
`--starter-budget 10000`, cap 255. The only difference is the input word.

| | representative (aut-minimal) | original (raw dataset row) |
|---|---|---|
| rows | 8 | 8 |
| solved | **0** | **8** |
| nodes | censored at 100,000 | **12,641 to 13,352** |
| certificate | -- | 8 AC, 0 `aut_assisted` |
| deciding stage | -- | `s20_mk2` on all 8 |

**8 of 8 against 0 of 8**, at a ratio of **at least 7.5x** -- a lower bound,
because the representatives were stopped at the budget rather than run to a
solve.

| original | orbit | nodes | original total | rep total |
|---|---|---:|---:|---:|
| `ac19x_62834` | `ac19_39288` | 12,641 | 21 | 18 |
| `ac19x_72661` | `ac19_43611` | 12,641 | 24 | 19 |
| `ac19x_86209` | `ac19_49095` | 12,641 | 19 | 18 |
| `ac19x_101379` | `ac19_54765` | 13,280 | 21 | 20 |
| `ac19x_100913` | `ac19_54616` | 13,344 | 23 | 23 |
| `ac19x_27180` | `ac19_20270` | 13,352 | 29 | 21 |
| `ac19x_110483` | `ac19_57992` | 13,352 | 27 | 21 |
| `ac19x_132233` | `ac19_65206` | 13,352 | 25 | 19 |

**It is not length.** Every original is as long as its representative or
longer -- 19 to 29 against 18 to 23. The shorter word is the harder one.

## Corroboration, with its caveat

Standalone `s20_mk2` settles these same 8 representatives at 1M in
149,461 to 229,844 nodes. Subtracting the cascade's fixed 10,001-node
prefix, the originals reach the same place in **2,640 to 3,351** stage-4
pops. That is a 45x to 87x ratio -- but the 1M run was at **cap 48** and
this one at **cap 255**, which are different searches, so it corroborates
the direction rather than pinning the factor. The clean number is the 7.5x
lower bound above, where every parameter matches.

## Why the cascade can see this at all

Its first stage is `reduce_basis_key`, a greedy Nielsen length descent, so
the natural guess is that it normalises the input and erases the
distinction. Measured: the descent lands original and representative on the
**identical state in 7 of the 8**. The distinction survives anyway, because
of the frontier discard -- `cascade_heuristics.search()` passes the canon'd
**original** pair to both search stages, never the descended state, so the
descent's output feeds only the rewrite stage. Stage 4 is therefore seeded
by the raw row, and the raw row is the easier seed.

This also means the finding is not really about the cascade. Stage 4 is
`s20_mk2` -- the same arm, the same priority `L + 20*S + 2*MK` -- so what is
measured here is that **`s20_mk2` finds the original easier than the
aut-minimal representative**, which is exactly Lucas's hypothesis for the
arm he asked about.

## What this does not show

- **Nothing about 10M.** These rows settle five orders of magnitude below
  it. The 10M question is the `ac19_orig_10m` campaign, on a different set:
  the originals of the orbits `greedy` and `s20_mk2` failed at 10,000,000.
- **Nothing about AC status.** All 8 representatives were already
  AC-certified by `s20_mk2` at 1M. This is a search-difficulty result, not
  a new solve.
- **8 rows.** Every one is a singleton orbit, so there is no within-orbit
  variance here. The 10M campaign's 40 originals include 7 multi-member
  orbits and will supply it.

## Files

| file | what |
|---|---|
| `orig_of_cascade_open8.csv` | the 8 originals, with their orbit |
| `ac19_cascade_screen_cascade501_b100000_mrl255_sb10000.jsonl` | the run, 8 rows with certificates |

Reproduce:

    PYTHONPATH=. python3 -m experiments.search.run_ac19_cascade_screen run \
        --arm cascade501 --budget 100000 --starter-budget 10000 \
        --rows-csv results/heuristic_search/ac19_orig_cascade/orig_of_cascade_open8.csv \
        --out-dir results/heuristic_search/ac19_orig_cascade --workers 4
