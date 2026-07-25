# EXP-14 — the second feature family, screened like the first

Slice `train` (40), budget 500, cap 48. Decidable subset **27** rows: baseline **17**, standing phased winner **27**.

`alone` repeats EXP-02's design (`L + w·f`, both signs) so a new coordinate can be read against `K`'s result on the same axis. `added` puts the feature on top of the standing winner — a feature that scores well alone but adds nothing there is re-expressing something already captured, not a new coordinate.

| feature | best alone | best added to winner | verdict |
|---|---|---|---|
| `Bmaxrun` | 19/27 (w=-0.25) | 25/27 (w=1) | beats the baseline alone, but adds nothing to the winner |
| `Bspread` | 19/27 (w=-0.25) | 25/27 (w=1) | beats the baseline alone, but adds nothing to the winner |
| `ratio` | 20/27 (w=-4) | 27/27 (w=8) | beats the baseline alone, but adds nothing to the winner |
| `density` | 19/27 (w=16) | 27/27 (w=8) | beats the baseline alone, but adds nothing to the winner |

## Verdict

**Nothing in the second family improves on the standing winner** — but read that with its ceiling in mind.

The decidable subset is defined as the rows on which the configs in this file disagree, and the standing winner solves **all 27 of them**. So no arm here *could* have shown an improvement: the measurement has no headroom, which is the same "no dynamic range" trap that has bitten this program before, arriving from the treatment side instead of the control side.

What this sweep can honestly conclude is the weaker statement: across 98 configurations, **no new-feature arm unlocked a single row the standing winner does not already solve**, and none of the four is a better *stand-alone* ordering than the knot term (best alone 20/27 against `K`'s 27/27 as part of the winner). The four new shapes look redundant with the block and knot features already present — `density` especially, being `nb/L` where `nb = 2K` by the balance theorem.

Testing whether they add anything would need headroom the 66-row benchmark does not have at these budgets: rows that are decidable but that the winner misses. Bins 8-9 and the reach rows are unsolved by everything, so they supply none.


## Every arm, best-first

| config | kind | feature | decidable | net | p |
|---|---|---|---|---|---|
| `[<=16]L1[<=inf]K8.936+L1+ratio-4+xyimb-5.978` | added | ratio | 27/27 | +10 | 0.002 |
| `[<=16]L1[<=inf]K8.936+L1+ratio-2+xyimb-5.978` | added | ratio | 27/27 | +10 | 0.002 |
| `[<=16]L1[<=inf]K8.936+L1+density-4+xyimb-5.9` | added | density | 27/27 | +10 | 0.002 |
| `[<=16]L1[<=inf]K8.936+L1+density-2+xyimb-5.9` | added | density | 27/27 | +10 | 0.002 |
| `[<=16]L1[<=inf]K8.936+L1+density-8+xyimb-5.9` | added | density | 27/27 | +10 | 0.002 |
| `[<=16]L1[<=inf]K8.936+L1+ratio-1+xyimb-5.978` | added | ratio | 27/27 | +10 | 0.002 |
| `[<=16]L1[<=inf]K8.936+L1+density-1+xyimb-5.9` | added | density | 27/27 | +10 | 0.002 |
| `[<=16]L1[<=inf]K8.936+L1+xyimb-5.978` ← winner | winner | — | 27/27 | +10 | 0.002 |
| `[<=16]L1[<=inf]K8.936+L1+density1+xyimb-5.97` | added | density | 27/27 | +10 | 0.002 |
| `[<=16]L1[<=inf]K8.936+L1+density2+xyimb-5.97` | added | density | 27/27 | +10 | 0.002 |
| `[<=16]L1[<=inf]K8.936+L1+ratio1+xyimb-5.978` | added | ratio | 27/27 | +10 | 0.002 |
| `[<=16]L1[<=inf]K8.936+L1+density4+xyimb-5.97` | added | density | 27/27 | +10 | 0.002 |
| `[<=16]L1[<=inf]K8.936+L1+density8+xyimb-5.97` | added | density | 27/27 | +10 | 0.002 |
| `[<=16]L1[<=inf]K8.936+L1+ratio2+xyimb-5.978` | added | ratio | 27/27 | +10 | 0.002 |
| `[<=16]L1[<=inf]K8.936+L1+ratio4+xyimb-5.978` | added | ratio | 27/27 | +10 | 0.002 |
| `[<=16]L1[<=inf]K8.936+L1+ratio8+xyimb-5.978` | added | ratio | 27/27 | +10 | 0.002 |
| `[<=16]L1[<=inf]K8.936+L1+ratio-8+xyimb-5.978` | added | ratio | 25/27 | +8 | 0.008 |
| `[<=16]L1[<=inf]Bmaxrun1+K8.936+L1+xyimb-5.97` | added | Bmaxrun | 25/27 | +8 | 0.008 |
| `[<=16]L1[<=inf]Bspread1+K8.936+L1+xyimb-5.97` | added | Bspread | 25/27 | +8 | 0.008 |
| `[<=16]L1[<=inf]Bmaxrun2+K8.936+L1+xyimb-5.97` | added | Bmaxrun | 24/27 | +7 | 0.016 |
