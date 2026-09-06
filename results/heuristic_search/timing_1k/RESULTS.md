# Matched local timing at 1,000 pops

2026-09-06. Same 60 rows, cap 48 per relator, maximum 1,000 popped states
per presentation, one thread, one warmed process, identical search machinery
and path capture. Execution order rotates across rows, with cooldowns between
every search. These are newly measured controls, not historical timing values.

| method | solved /60 | total popped states | search wall time | process CPU time |
|---|---:|---:|---:|---:|
| length greedy | 29 | 36,090 | 5.050 s | 5.010 s |
| S20_MK2 | 37 | 28,658 | 4.490 s | 4.403 s |
| S20_MK2 + 2W | 42 | 27,952 | 5.358 s | 5.290 s |
| S20_MK2 with generator-change neighbors | 43 | 18,961 | 4.713 s | 4.594 s |

The pure new score gains five solves, loses none, and takes **19.3% more wall
time** than S20_MK2 in this pass (20.2% more CPU time). Across all 60 rows it
pops 2.5% fewer states, but scoring work and the visited states differ. This
is a coverage improvement, not a wall-time speedup. On the 37 shared solves
it uses 6,951 pops versus S20's 5,658: 22.9% more.

The extra-move method gains six solves, loses none, and takes **5.0% more wall
time** than S20 (4.3% more CPU time). Its 33.8% fewer popped states across
the full subset do not translate into an elapsed-time saving in this pass;
each expansion can construct extra basis-change neighbors. The 5% timing
difference should not be treated as a stable performance margin from a
single local pass.

## What the timers include

Times sum complete `run()` calls over all 60 rows, including unsolved rows
that consume the full 1,000 pops. They include input checking/canonicalization,
search and successful path reconstruction. They exclude JIT warm-up, explicit
pre-run garbage collection, certificate replay, JSON output, and cooldown.
Certificate replay totals were 0.007 s, 0.012 s, 0.015 s and 0.012 s in table
order and are stored separately.

All four methods together used 19.610 seconds of measured search wall time
and 19.297 seconds of process CPU time. The batch took 151.476 seconds including
cooldowns and bookkeeping, plus 0.683 seconds of warm-up. Each search was
followed by at least max(0.5 seconds, its elapsed search time) of cooldown.
No local presentation search exceeded 1,000 pops.

This is a warmed, serial comparison on the same Mac CPU, not a guaranteed
physical-core-pinned measurement. macOS controls core assignment and frequency.
All configured numerical-library thread counts were one. The sandbox denied
lowering scheduling priority, so inherited priority was used and recorded.
No statistical confidence interval or large-budget throughput is claimed.

## Implementation and correctness

See [PIPELINE.md](PIPELINE.md) for the exact loop, four-response adjacency
formula, motivating AK3 comparison, and optimization boundaries. The shared
runner uses optimized packed expansion with a Python heap/parent map. The new
score has not yet been integrated into the large-campaign compact state arena.
Even greedy uses the common feature-extraction kernel, so these numbers compare
orderings in the same implementation, not separately optimized solvers.

All 240 newly measured outcome/pop-count pairs match their saved records
exactly. Every solve was certificate-replayed from its original input before
its record was written. The extra-move certificates explicitly contain
automorphisms and are not presented as ordinary-AC-only certificates.
Eleven focused tests passed before timing; no full performance suite was run.

This subset was used for exploratory selection and contains repeated Aut
classes. These results do not establish held-out generalization, and the
states are not forced into Aut-minimal form. Production remains S20_MK2.

## Reproduction

From the project root, use a fresh output directory:

```sh
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 NUMBA_NUM_THREADS=1 .venv/bin/python -m experiments.search.time_heuristic_1k --out results/heuristic_search/timing_1k_repeat
```

The same command was run with `--out results/heuristic_search/timing_1k`.
`manifest.json` records source/input SHA-256 hashes and the execution protocol;
`runs.jsonl` contains per-row clocks, counts, order positions and certificates;
`summary.json` contains the unrounded totals. The original exploratory runner
is preserved as `../exploratory_1k/runner_snapshot.py` at its recorded hash.
