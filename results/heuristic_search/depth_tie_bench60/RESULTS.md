# Depth tie-break on bench60 — `(score, +depth)` vs `(score, −depth)`

Updated `2026-08-04T02:45:43.628267+00:00`

**evaluated_on** = `benchmark_subset_60` (n=60), budget 1000, cap 48, engine `search_fast`.

Heap entry is `((seg, score), tie·depth, key)`. `tie=+1` (shipped) prefers shallower ties; `tie=−1` prefers deeper. This never changes scores — only exact-score ties. (Precedent: EXP-24 on bins 4–7; this scout is the full 60 × s20_mk2.)

## Headline @ budget 1,000

| arm | tie | solved | median nodes | mean nodes | median path | mean path |
|---|---:|---:|---:|---:|---:|---:|
| greedy baseline (frozen) | +1 | **29/60** | 61 | 175.5 | 16 | 19.2 |
| `length` ← current | +1 | **29/60** | 61 | 175.5 | 16 | 19.2 |
| `length` ← deepest | -1 | **28/60** | 44 | 174.6 | 21 | 23.8 |
| `s20_mk2` ← current | +1 | **37/60** | 52 | 152.9 | 22 | 25.3 |
| `s20_mk2` ← deepest | -1 | **37/60** | 54 | 146.2 | 23 | 28.9 |

## `+depth` vs `−depth` (same arm, same engine)

| arm | +depth solved | −depth solved | Δ solves | −depth-only | +depth-only | both |
|---|---:|---:|---:|---:|---:|---:|
| `length` | 29 | 28 | -1 | 0 | 1 | 28 |
| `s20_mk2` | 37 | 37 | +0 | 0 | 0 | 37 |

### Cost on jointly solved (both ties)

| arm | n joint | median nodes (+/−) | median path (+/−) | mean path (+/−) |
|---|---:|---|---|---|
| `length` | 28 | 59 / 44 | 16 / 21 | 18.2 / 23.8 |
| `s20_mk2` | 37 | 52 / 54 | 22 / 23 | 25.3 / 28.9 |

## vs frozen greedy @1k (arms.json `b1k_greedy_*`)

| arm | tie | solved | Δ vs greedy | notes |
|---|---:|---:|---:|---|
| `length` | +1 | 29/60 | +0 | same-engine length control |
| `length` | -1 | 28/60 | -1 | same-engine length control |
| `s20_mk2` | +1 | 37/60 | +8 | L+20S+2MK |
| `s20_mk2` | -1 | 37/60 | +8 | L+20S+2MK |

Cap note: frozen greedy columns are historically **mrl 24**; this scout uses **mrl 48**. Same-engine `length tie=+1` is the clean control for the flip; greedy is the published baseline reference.

## Per-bin solves

| bin | greedy@1k | length + | length − | s20_mk2 + | s20_mk2 − |
|---:|---:|---:|---:|---:|---:|
| 0 | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 |
| 1 | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 |
| 2 | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 |
| 3 | 6/6 | 6/6 | 6/6 | 6/6 | 6/6 |
| 4 | 5/6 | 5/6 | 4/6 | 6/6 | 6/6 |
| 5 | 0/6 | 0/6 | 0/6 | 5/6 | 5/6 |
| 6 | 0/6 | 0/6 | 0/6 | 2/6 | 2/6 |
| 7 | 0/6 | 0/6 | 0/6 | 0/6 | 0/6 |
| 8 | 0/6 | 0/6 | 0/6 | 0/6 | 0/6 |
| 9 | 0/6 | 0/6 | 0/6 | 0/6 | 0/6 |

## Verdict

`tie=−1` **loses or ties** on solves (length 29→28, s20_mk2 37→37). Shipped `+depth` stays. Matches EXP-24's reading on richer orderings.

Row table: `per_row.csv`.

