# EXP-08 — the second hump, on real solves only

Train bins 8-9 (8 rows) + the reach slice (6 open rows). Budget 1000, cap 64 (relators allowed to grow). Best 8 orderings from the sweeps, plus the baseline.

Ranked on nothing but solves: EXP-07 showed knot- and length-progress do not predict a solve at the boundary, so `min_total`/`min_K` below are context, not a score.

**No hard row solved at 1000 nodes** by any ordering — expected: these need tens of thousands to millions of nodes under the baseline, and a 1,000-node local ceiling cannot reach that. The finding is that the knot ordering does not collapse any second-hump row to a small search, not that it fails to help on the decidable rows (it does — see EXP-02/03).

## Best knot count reached (descriptive — NOT a ranking)

| config | rows where min_K < start_K | mean min_K reached |
|---|---|---|
| `[<=inf]L1` ← ctrl | 2/14 | 4.57 |
| `[<=16]L1[<=inf]K8.936+L1+xyimb-5.978` | 10/14 | 3.93 |
| `[<=14]L1[<=inf]L1+xyimb-16` | 7/14 | 4.21 |
| `[<=8]L1[<=inf]B10.307+L1+MK4.962+S6.408` | 10/14 | 3.93 |
| `[<=16]L1[<=inf]K2.53+L1+MK6.418+S8.458+x` | 10/14 | 3.93 |
| `[<=16]L1[<=inf]K8+L1` | 10/14 | 4.00 |
| `[<=16]L1[<=inf]L1+nb4` | 10/14 | 4.00 |
| `[<=16]L1[<=inf]B11.25+K7.884+L1` | 10/14 | 4.00 |
| `[<=8]L1[<=inf]Bmin-0.113+K1.809+L1+imbal` | 10/14 | 3.93 |
