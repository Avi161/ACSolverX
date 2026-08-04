# Fair compute: full K=4 beam pipeline vs plain greedy @1k

**Fair set:** 11 presentations unsolved by **both** plain greedy@1000 (original)
and K=4 nonsym-beam → greedy@1000 — so neither arm stops early by solving.

**What was timed (wall clock, serial, warmed JIT):**
- plain: length-greedy @1000 from the original pair, cap 24
- beam: full climb (`beam_k=4`, `max_aut_canon=1000`, `rungs=32`) **plus**
  terminal length-greedy @1000 from `best_rep`

## Summary

| | total wall (11) | mean / row | median / row |
|---|---:|---:|---:|
| plain greedy@1k | 9.68 s | 0.88 s | 0.86 s |
| beam + greedy@1k | 28.74 s | 2.61 s | 2.74 s |

**Whole-pipeline cost ≈ 3.0×** a full 1000-node greedy on these unsolved rows
(per-row ratios 2.3×–3.3×). Mean Aut-min calls on this set ≈ 1001 (cap-bound).

Machine-local wall times; ratios are the durable comparison.
Raw rows: `compute_fair_both_unsolved_b1k.json`.
