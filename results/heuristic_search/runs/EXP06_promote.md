# EXP-06 — the same orderings at budget 1,000

Slice: `train` (40). Cap 48. Only the budget changed. Control = baseline, **20/40** at 1,000 (was 17/40 at 500).

An ordering that gains going 500 → 1,000 is spending early pops on structure and cashing in later — the behaviour this program is looking for. One that loses ground was winning at 500 by reaching the easy solutions first.

| config | 500 | 1,000 | Δ | net@1k | p | mean nodes | mean path | Δmin |
|---|---|---|---|---|---|---|---|---|
| `[<=16]L1[<=inf]K2.53+L1+MK6.418+S8.458+xyimb3.` | 25/40 | 29/40 | +4 | +9 | 0.004 | 108 | 17.8 | +1.64 |
| `[<=16]L1[<=inf]K8.936+L1+xyimb-5.978` | 27/40 | 27/40 | +0 | +7 | 0.016 | 72 | 16.6 | +1.54 |
| `[<=16]L1[<=inf]K8+L1` | 25/40 | 27/40 | +2 | +7 | 0.016 | 84 | 16.6 | +1.08 |
| `[<=16]L1[<=inf]L1+nb4` | 25/40 | 27/40 | +2 | +7 | 0.016 | 84 | 16.6 | +1.08 |
| `[<=8]L1[<=inf]Bmin-0.113+K1.809+L1+imbal0.743+` | 24/40 | 27/40 | +3 | +7 | 0.016 | 98 | 20.1 | +1.46 |
| `[<=8]L1[<=inf]B10.307+L1+MK4.962+S6.408` | 25/40 | 27/40 | +2 | +7 | 0.016 | 105 | 20.8 | +1.46 |
| `[<=16]L1[<=inf]B11.25+K7.884+L1` | 25/40 | 27/40 | +2 | +7 | 0.016 | 117 | 16.8 | +1.23 |
| `[<=8]L1[<=inf]Bmax-3.046+Bmin-0.499+L1+MK0.612` | 24/40 | 27/40 | +3 | +7 | 0.016 | 163 | 17.2 | +1.62 |
| `[<=14]L1[<=inf]L1+xyimb-16` | 25/40 | 25/40 | +0 | +5 | 0.062 | 65 | 17.3 | +0.87 |
| `[<=inf]K7.119+L1+xyimb-2.169` | 24/40 | 25/40 | +1 | +5 | 0.180 | 79 | 15.8 | -0.53 |
| `[<=inf]L1` ← control | 17/40 | 20/40 | +3 | +0 | 1.000 | 201 | 19.6 | +0.00 |
