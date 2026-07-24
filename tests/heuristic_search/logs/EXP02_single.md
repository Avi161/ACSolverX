# EXP-02 — single-feature screen (`L + w·f`), budget 500, cap 48

Slice: `train` (40 presentations). Control = the baseline ordering, **17/40** solved. `net` counts presentations won minus lost against the control; `p` is a two-sided exact sign test on those discordant pairs. `Δmin` is the mean improvement in shortest total length reached, over the presentations this arm did **not** solve — progress where there is no solve.

## Best weight per feature

| feature | best weight | solved | net | p | mean nodes | mean path | Δmin |
|---|---|---|---|---|---|---|---|
| `K` | `8` | 23/40 | +6 | 0.031 | 95 | 14.8 | +1.00 |
| `nb` | `4` | 23/40 | +6 | 0.031 | 95 | 14.8 | +1.00 |
| `MK` | `8` | 22/40 | +5 | 0.062 | 137 | 15.6 | +0.83 |
| `xyimb` | `-16` | 21/40 | +4 | 0.289 | 31 | 14.5 | -0.16 |
| `Lmax` | `4` | 21/40 | +4 | 0.125 | 65 | 14.9 | +0.74 |
| `S` | `8` | 20/40 | +3 | 0.250 | 42 | 15.4 | +0.10 |
| `Bmax` | `-2` | 20/40 | +3 | 0.250 | 54 | 16.7 | +0.75 |
| `imbal` | `0.5` | 20/40 | +3 | 0.250 | 67 | 14.9 | +0.40 |
| `Lmin` | `-0.5` | 20/40 | +3 | 0.250 | 70 | 14.9 | +0.20 |
| `mK` | `-0.5` | 19/40 | +2 | 0.500 | 72 | 14.9 | +0.00 |
| `B1` | `-0.25` | 18/40 | +1 | 1.000 | 59 | 14.3 | -0.73 |
| `Bmin` | `-4` | 17/40 | +0 | 1.000 | 114 | 16.0 | +0.00 |

## Top 20 configs overall

| config | solved | net | p | mean nodes | mean path | Δmin | max relator popped |
|---|---|---|---|---|---|---|---|
| `[<=inf]K8+L1` | 23/40 | +6 | 0.031 | 95 | 14.8 | +1.00 | 28 |
| `[<=inf]L1+nb4` | 23/40 | +6 | 0.031 | 95 | 14.8 | +1.00 | 28 |
| `[<=inf]L1+MK8` | 22/40 | +5 | 0.062 | 137 | 15.6 | +0.83 | 28 |
| `[<=inf]L1+xyimb-16` | 21/40 | +4 | 0.289 | 31 | 14.5 | -0.16 | 23 |
| `[<=inf]L1+xyimb-8` | 21/40 | +4 | 0.125 | 38 | 16.0 | +0.32 | 21 |
| `[<=inf]L1+Lmax4` | 21/40 | +4 | 0.125 | 65 | 14.9 | +0.74 | 18 |
| `[<=inf]L1+Lmax8` | 21/40 | +4 | 0.125 | 65 | 14.9 | +1.63 | 18 |
| `[<=inf]L1+Lmax16` | 21/40 | +4 | 0.125 | 65 | 14.9 | +1.74 | 18 |
| `[<=inf]L1+Lmax1e+06` | 21/40 | +4 | 0.125 | 65 | 14.9 | +1.74 | 18 |
| `[<=inf]K4+L1` | 21/40 | +4 | 0.125 | 67 | 14.6 | +1.05 | 27 |
| `[<=inf]L1+nb2` | 21/40 | +4 | 0.125 | 67 | 14.6 | +1.05 | 27 |
| `[<=inf]L1+S8` | 20/40 | +3 | 0.250 | 42 | 15.4 | +0.10 | 19 |
| `[<=inf]Bmax-2+L1` | 20/40 | +3 | 0.250 | 54 | 16.7 | +0.75 | 24 |
| `[<=inf]L1+S4` | 20/40 | +3 | 0.250 | 55 | 15.5 | +0.05 | 19 |
| `[<=inf]L1+S16` | 20/40 | +3 | 0.250 | 58 | 17.2 | +0.50 | 20 |
| `[<=inf]L1+Lmax2` | 20/40 | +3 | 0.250 | 67 | 14.9 | +0.40 | 19 |
| `[<=inf]L1+imbal0.5` | 20/40 | +3 | 0.250 | 67 | 14.9 | +0.40 | 19 |
| `[<=inf]L1+Lmin-0.5` | 20/40 | +3 | 0.250 | 70 | 14.9 | +0.20 | 19 |
| `[<=inf]L1+Lmax1` | 20/40 | +3 | 0.250 | 70 | 14.9 | +0.20 | 19 |
| `[<=inf]L1+xyimb-4` | 20/40 | +3 | 0.250 | 77 | 14.9 | +0.20 | 19 |

Longest single relator popped by **any** of the 193 configs: **48** (cap was 48). Configs that ever popped a relator longer than 24: 78/193.

