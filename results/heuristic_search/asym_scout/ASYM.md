# Abelianization-Gram / asym scout

Updated `2026-07-30T23:19:03.985026+00:00`

**selected_on** = `splits_ac1m_hard_aut` train 120
**evaluated_on (primary, first read)** = `splits_asym_virgin_holdout60`
**evaluated_on (second read)** = `splits_fft_fresh_holdout60`
**evaluated_on (third read)** = `splits_ac1m_hard_aut` holdout 60

Budget 1000 / cap 48. Heap term = shipped base + `wA · feat`.

## Verdict framing

- **Mob/L² is BLOCKED** as an ordering feature (R² vs 17 shipped = 0.922). Train-only negative-control arms are reported below; do not promote.
- **asym = |⟨ab(r1),ab(r2)⟩|/T is IDEAS.md idea 8** (abelianized-distance priority), not a new sign-channel mechanism. Prior kill-first on solved paths: length↑∧abel↓ in 0.4% of steps. This scout re-tests the *same-length ordering* escape hatch.
- R² on train starts: asym=0.314, num=0.415, num/L=0.344, T=0.985, Mob/L²=0.922.

- Best-of-N optimism (7 half-splits on train): 3 distinct winners `['s20_Arawm3', 's20_Arawm3', 's20_Arawm3', 's20_mk2_Anormm3', 's20_mk2_Anormm3', 's20_mk2_Anormm8', 's20_mk2_Anormm3']`.

## Train selection winner: `s20_Arawm3`

mode=raw, wA=-3 → **59/120** (goal_hidden=0), mean nodes 339
Control `s20_mk2`: **54/120** (goal_hidden=0).

## Primary virgin 60

| arm | mode | wA | solved | Δ vs s20_mk2 | goal_hidden | mean nodes |
|---|---|---:|---:|---:|---:|---:|
| `s20_Anormm3` | norm | -3 | **27/60** | +4 | 0 | 495 |
| `s20` | norm | 0 | **26/60** | +3 | 0 | 478 |
| `s20_Arawm3` | raw | -3 | **25/60** | +2 | 0 | 387 |
| `s20_mk2` | norm | 0 | **23/60** | +0 | 0 | 432 |
| `s20_mk2_Anormm3` | norm | -3 | **23/60** | +0 | 0 | 457 |
| `s20_mk2_Anormp3` | norm | 3 | **22/60** | -1 | 0 | 365 |
| `s20_Anormp3` | norm | 3 | **22/60** | -1 | 0 | 469 |
| `s20_mk2_Arawm3` | raw | -3 | **21/60** | -2 | 0 | 337 |
| `s20_Arawp3` | raw | 3 | **18/60** | -5 | 0 | 331 |
| `s20_mk2_Arawp3` | raw | 3 | **17/60** | -6 | 0 | 386 |
| `length` | norm | 0 | **0/60** | -23 | 0 | — |

McNemar `s20_Arawm3` vs `s20_mk2`: b(win-only)=10, c(base-only)=8, both=15, Δ=+2, exact two-sided p=0.8145.
Decidable subset (disagree rows): `s20_Arawm3` 10/18 vs `s20_mk2` 8/18.

## Second-read FFT-fresh 60

| arm | mode | wA | solved | Δ vs s20_mk2 | goal_hidden | mean nodes |
|---|---|---:|---:|---:|---:|---:|
| `s20_mk2_Anormm3` | norm | -3 | **33/60** | +6 | 0 | 481 |
| `s20_mk2_Anormp3` | norm | 3 | **30/60** | +3 | 0 | 475 |
| `s20_mk2` | norm | 0 | **27/60** | +0 | 0 | 449 |
| `s20` | norm | 0 | **27/60** | +0 | 0 | 496 |
| `s20_Arawm3` | raw | -3 | **25/60** | -2 | 0 | 325 |
| `s20_Anormm3` | norm | -3 | **25/60** | -2 | 0 | 420 |
| `s20_mk2_Arawm3` | raw | -3 | **24/60** | -3 | 0 | 419 |
| `s20_Anormp3` | norm | 3 | **24/60** | -3 | 0 | 530 |
| `s20_mk2_Arawp3` | raw | 3 | **23/60** | -4 | 0 | 460 |
| `s20_Arawp3` | raw | 3 | **16/60** | -11 | 0 | 445 |
| `length` | norm | 0 | **0/60** | -27 | 0 | — |

McNemar `s20_Arawm3` vs `s20_mk2`: b(win-only)=6, c(base-only)=8, both=19, Δ=-2, exact two-sided p=0.7905.
Decidable subset (disagree rows): `s20_Arawm3` 6/14 vs `s20_mk2` 8/14.

## Third-read spent Aut 60

| arm | mode | wA | solved | Δ vs s20_mk2 | goal_hidden | mean nodes |
|---|---|---:|---:|---:|---:|---:|
| `s20_mk2_Anormp3` | norm | 3 | **33/60** | +0 | 0 | 396 |
| `s20_mk2` | norm | 0 | **33/60** | +0 | 0 | 453 |
| `s20_mk2_Anormm3` | norm | -3 | **32/60** | -1 | 0 | 449 |
| `s20_mk2_Arawp3` | raw | 3 | **31/60** | -2 | 0 | 465 |
| `s20_Anormm3` | norm | -3 | **30/60** | -3 | 0 | 442 |
| `s20` | norm | 0 | **30/60** | -3 | 0 | 449 |
| `s20_mk2_Arawm3` | raw | -3 | **27/60** | -6 | 0 | 380 |
| `s20_Anormp3` | norm | 3 | **27/60** | -6 | 0 | 420 |
| `s20_Arawm3` | raw | -3 | **26/60** | -7 | 0 | 379 |
| `s20_Arawp3` | raw | 3 | **26/60** | -7 | 0 | 409 |
| `length` | norm | 0 | **0/60** | -33 | 0 | — |

McNemar `s20_Arawm3` vs `s20_mk2`: b(win-only)=2, c(base-only)=9, both=24, Δ=-7, exact two-sided p=0.0654.
Decidable subset (disagree rows): `s20_Arawm3` 2/11 vs `s20_mk2` 9/11.

## Train 120 ranking (all arms)

| rank | arm | mode | wA | solved | goal_hidden | mean nodes |
|---:|---|---|---:|---:|---:|---:|
| 1 | `s20_Arawm3` | raw | -3 | 59/120 | 0 | 339 |
| 2 | `s20_mk2_Anormm8` | norm | -8 | 59/120 | 0 | 460 |
| 3 | `s20_mk2_Anormm3` | norm | -3 | 58/120 | 0 | 432 |
| 4 | `s20_mk2_Amobm8` | mob | -8 | 54/120 | 0 | 426 |
| 5 | `s20_Anormm8` | norm | -8 | 54/120 | 0 | 428 |
| 6 | `s20_mk2_Amobp8` | mob | 8 | 54/120 | 0 | 438 |
| 7 | `s20_Anormm3` | norm | -3 | 54/120 | 0 | 451 |
| 8 | `s20_mk2` | norm | 0 | 54/120 | 0 | 454 |
| 9 | `s20_mk2_Anormp3` | norm | 3 | 52/120 | 0 | 392 |
| 10 | `s20_mk2_Arawm3` | raw | -3 | 51/120 | 0 | 329 |
| 11 | `s20_mk2_Anormp8` | norm | 8 | 50/120 | 0 | 427 |
| 12 | `s20` | norm | 0 | 49/120 | 0 | 432 |
| 13 | `s20_Amobp8` | mob | 8 | 49/120 | 0 | 477 |
| 14 | `s20_Amobm8` | mob | -8 | 48/120 | 0 | 392 |
| 15 | `s20_mk2_Arawp3` | raw | 3 | 46/120 | 0 | 425 |
| 16 | `s20_Anormp3` | norm | 3 | 44/120 | 0 | 411 |
| 17 | `s20_mk2_Arawp8` | raw | 8 | 38/120 | 0 | 324 |
| 18 | `s20_Arawp3` | raw | 3 | 35/120 | 0 | 387 |
| 19 | `s20_Anormp8` | norm | 8 | 34/120 | 0 | 377 |
| 20 | `s20_Arawp8` | raw | 8 | 31/120 | 0 | 346 |
| 21 | `length_Arawm3` | raw | -3 | 30/120 | 0 | 584 |
| 22 | `s20_mk2_Arawm8` | raw | -8 | 28/120 | 0 | 329 |
| 23 | `length_Arawp8` | raw | 8 | 26/120 | 0 | 720 |
| 24 | `s20_Arawm8` | raw | -8 | 23/120 | 1 | 318 |
| 25 | `length_Anormm3` | norm | -3 | 20/120 | 0 | 674 |
| 26 | `length_Anormm8` | norm | -8 | 18/120 | 0 | 648 |
| 27 | `length_Anormp8` | norm | 8 | 17/120 | 0 | 678 |
| 28 | `length_Arawp3` | raw | 3 | 10/120 | 0 | 455 |
| 29 | `length_Amobm8` | mob | -8 | 9/120 | 0 | 659 |
| 30 | `length_Anormp3` | norm | 3 | 7/120 | 0 | 445 |
| 31 | `length_Arawm8` | raw | -8 | 3/120 | 1 | 258 |
| 32 | `length_Amobp8` | mob | 8 | 1/120 | 0 | 124 |
| 33 | `length` | norm | 0 | 0/120 | 0 | — |

## Promotion bar

Promote only if: same-sign Δ vs `s20_mk2` on virgin **and** at least one confirmatory read; McNemar exact p suggests real lift (target ballpark ≥ +6/60 discordant net, but report b,c,p not a hard cutoff); no systematic `goal_hidden` inflation; and a mechanism story for the **sign of wA** (wA>0 = idea-8 as written; wA<0 = opposite).

Do **not** promote Mob/L² from this file.

## VERDICT: DO NOT PROMOTE

| claim | evidence |
|---|---|
| Mob/L² as ordering feature | **BLOCKED.** R²=0.922 vs shipped 17. On train, `s20_mk2_Amob±8` = 54/120 = `s20_mk2` control. No lift. |
| Train-selected `s20_Arawm3` (wA=−3, num/L) | **Overfit.** Train 59/120 (+5 vs `s20_mk2`), virgin +2 (p=0.81), fft **−2**, spent **−7**. Sign flip across reads. |
| vs its own base `s20` | Train +10 (59 vs 49); virgin −1, fft −2, spent −4. Term does not transfer. |
| Idea-8 direction (wA>0) | Does **not** win selection. Train prefers **wA<0** (penalise near-orthonormal abel frames / prefer large \|⟨v1,v2⟩\|). That is the opposite of the stated idea-8 intuition, and it still fails holdout. |
| Best non-selected peek (`s20_mk2_Anormm3`) | fft +6 looks juicy on a second-read, but virgin +0 and spent −1 — do not cherry-pick. |

Ship remains **`S20_MK2`**. No new arm from this scout.

