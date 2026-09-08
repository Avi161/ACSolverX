# Aut-minimising makes AC19 rows dramatically harder

Lucas Fagan asked whether the original of a hard AC19 presentation, before
aut-minimising, solves where its `Aut(F2)`-minimal representative does not.

**Yes, and by at least two to three orders of magnitude.**

| arm | originals | solved | representatives at 10M | ratio, median | ratio, worst row |
|---|---:|---:|---:|---:|---:|
| `greedy` | 40 | **40 / 40** | **0 / 28 solved** | **1,748x** | **191x** |
| `s20_mk2` | 18 | **18 / 18** | **0 / 9 solved** | **6,349x** | **977x** |

Every one of the 58 row-runs solved. **Not one needed 100,000 nodes** -- the
budget the cascade screen runs at -- against representatives that were given
**10,000,000** and exhausted every one.

### 58 is row-runs, not presentations

**The 18 `s20_mk2` originals are a strict subset of the 40 `greedy` originals**
-- set difference empty, checked from the derived lists, and pinned by
`tests/test_ac19_orig_10m.py::test_s20_mk2_originals_are_a_subset_of_greedy`.
The 9 `s20_mk2` orbits likewise sit inside the 28 `greedy` orbits.

So the target set is **28 distinct orbits and 40 distinct originals**, not 37
and 58. The 58 counts (arm x original) cells: 18 originals had BOTH arms run
on them, and both arms solved all 18. Any sentence of the form "all 58
presentations" overcounts distinct presentations by 18 and should say "all 58
row-runs" or "all 40 originals".

That overlap is not waste -- it is a paired head-to-head on 18 rows at equal
budget and cap, which no other part of this campaign has. It goes the
expected way on most of them and the other way on at least one, so it is a
distribution rather than a verdict:

| original | `greedy` | `s20_mk2` |
|---|---:|---:|
| `ac19x_139445` | 50,800 | 958 |
| `ac19x_90583` | 50,621 | 967 |
| `ac19x_91095` | 1,839 | **2,638** |

Those three are transcribed from the terminal, not re-derived; the full
18-row comparison is computed from the records once the jsonls land.

| arm | min | p50 | p90 | max | sum |
|---|---:|---:|---:|---:|---:|
| `greedy` | 509 | 5,720 | 45,868 | 52,143 | 714,752 |
| `s20_mk2` | 190 | 1,575 | 6,522 | 10,229 | 49,540 |

0 errors, 0 OOM. The box peaked at **14 GiB of 743**, and the campaign that
was sized for 6.5 hours finished in **6 minutes**, because every row solved
and nothing ran to exhaustion.

## Why the ratios are a lower bound

The numerator is censored. No representative solved at 10,000,000, so the
true cost of the minimised form is unknown and larger -- 10M is where the
search was stopped, not where it would have finished.

The denominator is exact: these are real solves carrying replayable
certificates.

## The join that makes the bound honest

A ratio against "10M" is only fair if every representative really was
exhausted **by the same arm at the same cap**. Checked row by row against
`../ac19_10m/`, and it holds without exception:

| arm | originals | orbits | every representative exhausted at exactly 10,000,000 nodes, cap 64 |
|---|---:|---:|---|
| `greedy` | 40 | 28 | yes |
| `s20_mk2` | 18 | 9 | yes |

No representative was merely un-run, none solved, none stopped early, and
none ran at a different cap. `tests/test_ac19_orig_10m.py` re-derives the row
lists from those same jsonls, so the two sides cannot drift apart.

## It is not length, and it is not the arm

**Not length.** Every original is as long as its representative or longer --
17 to 32 total against at most 24. The shorter word is the harder one, which
is the opposite of what a length-ordered search should prefer.

**Not the arm.** Both arms show it, and `s20_mk2` -- the stronger of the two
-- shows the *larger* effect: 6,349x median against greedy's 1,748x.

**Not a normalisation artifact.** The experiment is void if the arm
normalises its own input, so that is pinned by a test: no `aut_canon`,
`reduce_basis`, `basis_moves` or `canon_pair` appears anywhere in
`greedy_compact.py`, `greedy_baseline.py`, `run_leftovers_5m.py` or
`experiments/heuristic_search/core/`. The original and the representative
really are different starting points.

## Corroboration at a different budget and a different arm

The cascade shows the same thing on a disjoint set. Its own 8 open
representatives, at budget 100,000 with `--starter-budget 10000`, cap 255:
**8 of 8 originals solve at 12,641-13,352 nodes, 0 of 8 representatives
solve.** See [`../ac19_orig_cascade/RESULTS.md`](../ac19_orig_cascade/RESULTS.md).
Three arms, three budgets, three caps, same direction.

## What this does not show

- **No presentation changed AC status.** Every representative here was
  already settled -- 25 of the 28 by the cascade at under 4,275 nodes, the
  other 3 by `s20_mk2` at 1M. This is a search-difficulty result.
- **Nothing about aut-minimising in general**, only about these 28 orbits,
  which were selected precisely for being hard after minimisation. The
  selection is the point of the experiment and also its limit: it says
  minimisation *can* cost orders of magnitude, not how often it does.
- **Within-orbit variance is not yet reported.** 7 of the 28 greedy orbits
  carry more than one original; that breakdown needs the per-row jsonl.

## Files

Run at sha `727914d2`, `ENGINE=hcompact`, campaign `ac19_orig_10m`, 5 workers,
budget 10,000,000, cap 64, paths captured.

    s3://acsolver-u124-205558941715/backup/orig10m/   2 jsonl + runA.log

**The jsonls are not yet in the repo.** The table above is the run's reported
summary; the per-row records, the certificates and the within-orbit
breakdown land here when they are pulled.

Reproduce:

    export ENGINE=hcompact
    PYTHONPATH=. python3 -m experiments.search.run_leftovers_5m \
        --arm greedy --campaign ac19_orig_10m \
        --out-dir results/heuristic_search/ac19_orig_10m --workers 5
