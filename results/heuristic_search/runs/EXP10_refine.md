# EXP-10 — round two: a finer search near the winners, at budget 1,000

Slice: `aut_train` (45), budget 1000, cap 48, 400 configs drawn near the earlier winners. **The test slice is untouched** — it was already spent on the finalists, so this reports `aut_train` only.

## Best-of-N optimism on aut_train

- gain on the half it was **chosen** on: **+4.25**
- gain on the half it was **not**: **+3.02**
- optimism of a best-of-400 pick: **1.23** presentations
- 7 distinct half-split winners

## Did anything beat the standing best?

- standing best on `aut_train` @1000 (from the finalists): **20/24** decidable
- round-two best: `[<=16]L1[<=inf]K9.39+L1+S4.742+imbal0.092` — **20/24** decidable (baseline 12/24)

Nothing near the winners beats them on `aut_train` — the finalists and the round-two best reach the same count on the same rows. **The recommendation stands**; the earlier winners are at the local ceiling for this family.

## Top 12 on aut_train (decidable)

| config | decidable | net | p | mean nodes | mean path |
|---|---|---|---|---|---|
| `[<=16]L1[<=inf]K9.39+L1+S4.742+imbal0.092` | 20/24 | +8 | 0.008 | 61 | 15.9 |
| `[<=16]L1[<=inf]K9.904+L1+imbal0.63` | 20/24 | +8 | 0.008 | 63 | 15.9 |
| `[<=16]L1[<=inf]K8.151+L1+MK0.675+imbal0.096+xyim` | 20/24 | +8 | 0.008 | 69 | 15.9 |
| `[<=14]L1[<=inf]Bmax-1.983+Bmin-0.964+L1+S8.995+x` | 20/24 | +8 | 0.008 | 75 | 16.4 |
| `[<=18]L1[<=inf]Bmax-2.19+L1+xyimb-7.527` | 20/24 | +8 | 0.008 | 85 | 17.1 |
| `[<=18]L1[<=inf]Bmax-1.81+Bmin-0.307+K1.654+L1+S5` | 20/24 | +8 | 0.008 | 87 | 17.1 |
| `[<=18]L1[<=inf]Bmin0.096+K7.743+L1+imbal0.753+xy` | 20/24 | +8 | 0.008 | 90 | 17.1 |
| `[<=14]L1[<=inf]Bmax0.29+K3.744+L1+MK4.438+S6.146` | 20/24 | +8 | 0.008 | 99 | 16.4 |
| `[<=20]L1[<=inf]Bmax-3.872+Bmin-0.742+L1+S8.229+i` | 20/24 | +8 | 0.008 | 114 | 16.9 |
| `[<=16]L1[<=inf]L1+MK7.127+S6.533` | 20/24 | +8 | 0.008 | 118 | 18.8 |
| `[<=20]L1[<=inf]K6.263+L1+S8.262+imbal1.054+xyimb` | 20/24 | +8 | 0.008 | 120 | 17.2 |
| `[<=20]L1[<=inf]K5.948+L1+imbal1.159` | 20/24 | +8 | 0.008 | 120 | 17.2 |
