# EXP-05 — does the cap bind once the ordering climbs?

Slice: `train` (40). Budget 500. Caps 24, 32, 48, 64, 96. Each cap carries its own baseline control, because an ordering compared against a control at a different cap is not a comparison.

`max pop` is the longest single relator any search under that arm actually popped. Where it sits strictly below the cap, the cap **provably did not bind** and equality with a lower cap is a tautology, not evidence.

| config | cap 24 | cap 32 | cap 48 | cap 64 | cap 96 |
|---|---|---|---|---|---|
| `[<=inf]L1` ← control | 17/40 (maxpop 19) | 17/40 (maxpop 19) | 17/40 (maxpop 19) | 17/40 (maxpop 19) | 17/40 (maxpop 19) |
| `[<=16]L1[<=inf]K8.936+L1+xyimb-5.978` | 27/40 (maxpop 24) | 27/40 (maxpop 31) | 27/40 (maxpop 31) | 27/40 (maxpop 31) | 27/40 (maxpop 31) |
| `[<=14]L1[<=inf]L1+xyimb-16` | 25/40 (maxpop 23) | 25/40 (maxpop 23) | 25/40 (maxpop 23) | 25/40 (maxpop 23) | 25/40 (maxpop 23) |
| `[<=8]L1[<=inf]B10.307+L1+MK4.962+S6.408` | 25/40 (maxpop 24) | 25/40 (maxpop 25) | 25/40 (maxpop 25) | 25/40 (maxpop 25) | 25/40 (maxpop 25) |
| `[<=16]L1[<=inf]K2.53+L1+MK6.418+S8.458+xyimb` | 25/40 (maxpop 24) | 25/40 (maxpop 27) | 25/40 (maxpop 27) | 25/40 (maxpop 27) | 25/40 (maxpop 27) |
| `[<=16]L1[<=inf]K8+L1` | 25/40 (maxpop 24) | 25/40 (maxpop 28) | 25/40 (maxpop 28) | 25/40 (maxpop 28) | 25/40 (maxpop 28) |
| `[<=16]L1[<=inf]L1+nb4` | 25/40 (maxpop 24) | 25/40 (maxpop 28) | 25/40 (maxpop 28) | 25/40 (maxpop 28) | 25/40 (maxpop 28) |
