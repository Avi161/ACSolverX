# EXP-27 — re-tuning from scratch on ground the earlier tuning never touched

260 configs over all 17 features, threshold optional, budget 1000, cap 48. Selected on **50** presentations from `ms640` that no stage of this program had read; the winner and the incumbents are then scored on **25** more that the selection never saw. Split frozen before any fitting (`splits_ms640.json`).

| config | tuned on (50) | **held back (25)** |
|---|---|---|
| `[<=20]L1[<=inf]Bmax-4.44+L1+Lmax5.278+MK-0.472+densi` ← re-tuned winner | 29/50 | **19/25** |
| `[<=inf]K2.53+L1+MK6.418+S8.458+xyimb3.292` ← recommended (incumbent) | 31/50 | **19/25** |
| `[<=16]L1[<=inf]K8.936+L1+xyimb-5.978` ← lean (incumbent) | 24/50 | **15/25** |
| `[<=inf]L1` ← baseline (length) | 13/50 | **7/25** |

## Verdict

The re-tune **ties** the incumbent out of sample (19/25 each), and it did not even win the half it was selected on (29 vs the incumbent's 31) — the incumbent, fitted on entirely different presentations, is better on the re-tune's own training data. **The incumbent is confirmed on genuinely independent data**, by a search fitted elsewhere that had every chance to beat it.

