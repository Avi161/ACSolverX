# Scout: S-arm cap + add-on (budget 1,000)

Frozen holdout slice: first 20 odd-idx AC1M length-hard rows from `screen_length_ac1m.jsonl` (idxs [121, 873, 1061, 2283, 2941, 3223, 3505, 4351, 6137, 6701, 7735, 7829, 8581, 9521, 10179, 11025, 11119, 12153, 12341, 12435]).

Scout-then-scale: short ≤1k only; scale winner on Colab via `hsearch_s24_scale.ipynb`.

## Solved / 20

| arm | solved | mean nodes (solved) | cap |
|---|---:|---:|---:|
| `length_c24` | **0/20** | — | 24 |
| `length_c48` | **0/20** | — | 48 |
| `s20_c24` | **6/20** | 623.7 | 24 |
| `s20_c48` | **6/20** | 623.7 | 48 |
| `s24_c24` | **4/20** | 537.2 | 24 |
| `s24_c48` | **4/20** | 537.2 | 48 |
| `recommended_c48` | **1/20** | 535.0 | 48 |
| `s20_mk8_c48` | **2/20** | 605.5 | 48 |
| `s24_mk8_c48` | **1/20** | 423.0 | 48 |

## Readout (no fitting)

- **Cap 24 ≡ cap 48** on every S arm here (same solved set and same nodes). Raising the
  ceiling did not buy recoveries on this slice — Colab can keep `MAX_RELATOR_LENGTH=48`
  as a headroom default, but the scout does not require it.
- **Pure `L+20·S` wins the slice** (6/20) over `L+24·S` (4/20). Matches the frozen
  S-grid holdout peak (`w=20` on 404 odd-idx hard). `s24` stays a secondary Colab arm.
- **Add-ons hurt:** `s20+MK8` 2/20, `recommended` 1/20. Do **not** scale the multi-feature
  mix for hard recovery — scale pure S.
- **Colab default:** `ARMS = ["baseline", "s20", "s24"]` in
  [`hsearch_s24_scale.ipynb`](../../../experiments/heuristic_search/hsearch_s24_scale.ipynb).

Raw: [`s_cap_addon_b1k.jsonl`](s_cap_addon_b1k.jsonl).

