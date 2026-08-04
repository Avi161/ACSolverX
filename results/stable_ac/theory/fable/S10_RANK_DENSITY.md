# S10 — Thickenability gets DENSER with rank: the first positive result for high-rank stabilization

S-line, branch `claude/stable-ac-conjecture-stabilization-rwo9as` (merge into
`fable/proof`). Status: **measurement, with its confounds listed and one control still
outstanding (§4).** This is the counterweight to S3/S8, which showed the two obvious
high-rank *mechanisms* are inert. The mechanism is inert; the **population** is not.

## 1. The question, made measurable

Lackenby Thm 1.3 turns a thickenable balanced presentation of the trivial group into an
AC-trivialization. So the practical question behind "does going to 9 or 10 generators help"
is not about a clever move — it is about *how common the certificate is*:

> Among presentations that ARE AC-trivial, at a fixed total relator length, what fraction
> is (orientably) thickenable — and does that fraction depend on the rank?

If the fraction rises with rank, then a stable-AC search that first stabilizes and then
wanders is hunting a much larger target, and high rank pays even though no single
high-rank *move* creates thickenability.

## 2. Design

Sampling: from the standard presentation `⟨x_1..x_n | x_1,…,x_n⟩` take an independent short
random walk in AC1/AC2/AC3 (6–40 moves, per-state total-length cap 40) and keep the first
state whose total length falls in the band and all of whose relators have length ≥ 3.
Every sampled state is therefore **AC-trivial and presents the trivial group by
construction** — no triviality test needed and no bias toward hard instances. Deduplicated
on sorted word tuples. Verdict: exact `gamma_N_factorial_n`, `cap_rotations = 4·10⁵`;
states whose census exceeds the cap are recorded as *skipped*, never as a verdict
(fail-closed). `minimum_defect` reported raw; γ_N = defect/2; defect 0 = orientably
thickenable (see S3 repair R3 — this is the orientable predicate, and its relation to
Lackenby's weaker hypothesis is the open Joint-A link).

## 3. Result — matched band, total length 12–16

| rank | scored | defect 0 | **fraction** | skipped (census > cap) | median length |
|---|---|---|---|---|---|
| 2 | 112 | 46 | **0.411** | 88 | 13 |
| 3 | 179 | 130 | **0.726** | 21 | 14 |
| 4 | 196 | 170 | **0.867** | 4 | 15 |

A second, longer band (total length 15–24, `cap 2.5·10⁵`) extends the picture upward, where
rank 2 is not computable at all:

| rank | scored | defect 0 | fraction | skipped | median length |
|---|---|---|---|---|---|
| 2 | 0 | — | **not computable** | 80 | — |
| 3 | 22 | 11 | 0.500 | 58 | 15 |
| 4 | 28 | 20 | 0.714 | 52 | 17 |
| 5 | 26 | 17 | 0.654 | 54 | 20 |
| 6 | 23 | 16 | 0.696 | 57 | 22 |

**Reading.** At matched length the thickenable fraction roughly doubles from rank 2 to
rank 4. And in the longer band rank 2 is *not measurable at all* — every sampled rank-2
state at length 15–24 blew the census cap, while rank 3–6 states at the same lengths were
decided in seconds.

## 4. Confounds — all of them push against the trend, except one which is untested

1. **Skip rate biases rank 2 UPWARD.** A state is skipped when `∏(deg−1)!` exceeds the cap,
   i.e. when its germs are high-degree — and high-degree germs are exactly the crowded
   links that tend not to embed. 88 of 200 rank-2 states were skipped versus 4 of 200 at
   rank 4, so the true rank-2 fraction is **at most** 0.411 and the gap is at least as
   large as measured.
2. **Median length drifts up with rank** (13 → 14 → 15 inside the band). Longer is
   generally less thickenable, so this too understates the trend.
3. **[OPEN CONTROL] Distance from the standard presentation.** All samples come from short
   walks, so they are *near* standard. AK(3)'s stable class is not. If the density falls
   steeply with walk length, this baseline does not transfer to AK(3) and §5 must be
   discounted. **This control has not been run and the section below is conditional on
   it.** (Filed-lesson discipline: `contrast-length-confound.md` — a gap in a rate can be a
   gap in a covariate in disguise.)
4. **No p-values.** Walk-generated states are not independent draws
   (`contrast-length-confound.md`), so only the raw fractions are quoted.

## 5. What it implies for AK(3) — conditional on the §4.3 control

The repo's own rank-3 (depth-1) contrast, re-read with this baseline, becomes sharper than
it looked:

| harvest | distinct members | thickenable | rate |
|---|---|---|---|
| AK(2)+z, rank 3, 1,000 pops | 27,350 | 14,999 | **54.8 %** |
| AK(3)+z, rank 3, 1,000 pops | 171,842 | **0** | **0 %** (686 undecided) |

AK(2) is AC-trivial, and its depth-1 class comes back at 54.8 % thickenable — squarely in
line with the 72.6 % baseline for generic AC-trivial rank-3 states of comparable length.
AK(3)'s depth-1 class returns **zero in 171,842**. The two harvests share one operator
implementation and matched budgets (`stable_contrast_summary.json`, `comparison_table`),
though not absolute length caps (18 vs 16), and AK(3)+z's members are longer (mode 22–24)
than AK(2)+z's (mode 9–11) — **the length confound is real and is why this is stated as a
tension, not a result.**

Read in the direction the S-line cares about: *if* AK(3) were stably AC-trivial, the
density measurement says its stable class should be thick with Lackenby certificates —
more so, not less, as the rank climbs. That it is empty at depth 1 across 171,842 members
is the strongest single piece of evidence on this line, and it points at the **disproof**
side of `FRAMING` §2, not the proof side.

## 6. What this changes about the session's plan

- The high-rank programme is **not** dead — S3/S8 killed the *bookkeeping* mechanisms, and
  S10 says the *target* grows with rank. Those are compatible: refinements do not move a
  state's γ_N, but genuine AC2 slides at rank 5–6 wander in a population where 65–87 % of
  the AC-trivial states are thickenable.
- The right high-rank experiment is therefore: **stabilize to rank 5–6, slide, test**, with
  the detection rate measured on an AC-trivial positive ladder at the same rank and length
  (task A7's depth ladder).
- And a second, purely instrumental payoff worth stating on its own: **the thickenability
  decision is cheap at high rank and infeasible at rank 2 for the same total length.**
  At length 15–24 not one rank-2 sample was decidable inside the cap; every rank-3-to-6
  sample was. Whatever else high rank does, it restores the instrument in the length regime
  where AK(3)'s stable class actually lives.
