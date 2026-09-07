# ac19_all: every AC19 presentation, move-wise certificates

What the cloud run does, what it costs, and the exact command. All figures
measured on a 4-core 15 GB box, on a 1,046-row stride sample of
`data/AC19_extended.txt` unless stated otherwise.

## The job

156,762 presentations -- every line of `data/AC19_extended.txt`,
Aut-duplicates included -- through the cascade at a 1,000-node budget,
storing a **move-wise** certificate per solved row.

## Cost, measured

| quantity | value |
|---|---:|
| search | 31.56 ms/row |
| solve rate | 98.18% (1,027 / 1,046 in the sample) |
| peak RSS per worker | 0.22 GiB |
| **total CPU** | **1.37 core-hours** |
| bytes per row, move-wise | 889 |
| **total output** | **~0.13 GiB** |

An earlier full 156,762-row pass at this budget took 32.3 minutes wall on
3 workers and 1.61 core-hours, which is the figure to hold this to.

## Why not store elementary AC moves

`decode_ac_jsonl` expands a stored certificate into generator-level AC
operations -- invert, swap, conjugate-by-a-letter, multiply -- and every
one of those replays to `["x", "y"]`. But 98.5% of the expansion is
conjugation letters, which are no-ops on the canonical state, and the
median path goes from 10 moves to 226:

| schema | bytes/row | total |
|---|---:|---:|
| **move-wise (stored)** | **889** | **0.13 GiB** |
| move-wise + states | 1,278 | 0.18 GiB |
| elementary expansion | 10,440 | 1.50 GiB |

States are redundant with the moves -- rebuilt exactly on 617/617 solved
rows by `ac_decode.states_from_steps` -- so they are not stored either.
The elementary form is regenerated on demand and is proven: 640/640 MS640
certificates replay to `["x", "y"]`, verified twice with independent
implementations of the four operations.

## Sizing

Output is 0.13 GiB and peak RSS is 0.22 GiB per worker, so **neither disk
nor RAM binds**. Cores do, and only for about 90 seconds of wall clock on
a large box. The default root volume is enough; there is nothing to
stream to S3 mid-run, because the whole run is shorter than a sync
interval.

## Run it

    CAMPAIGN=ac19_all ./experiments/search/run_remote.sh plan
    CAMPAIGN=ac19_all ./experiments/search/run_remote.sh smoke
    CAMPAIGN=ac19_all ./experiments/search/run_remote.sh run

`run` writes the move-wise jsonl, reports, writes the residue lists, and
then runs `decode_ac_jsonl` over the result to produce
`ac19_all_elementary.jsonl`. Drop that last step by setting `EMIT_MIXED=0`
if only the move-wise record is wanted.

The generated `_job.sh` bakes `--chunks 1 --chunk-index 1`, the
single-box convention: without it the runner would fall back to a chunk
count and silently run a fraction of the list.

## Inputs the box builds for itself

`results/heuristic_search/ac19_autmin_screen/ac19_extended_rows.csv` is
generated, not committed as a search input:

    PYTHONPATH=. python3 -m experiments.search.make_ac19_autmin_screen \
        --write --dataset-rows

which also rebuilds the 72,779-orbit list and cross-checks it against
every shipped residue row before writing anything.
