# R7b — The spike-space hunt, and what its silence is actually worth

STATUS: MEASUREMENT + INSTRUMENT CALIBRATION. Claims addressed: the POSITIVE direction
(a thickenable spelling would imply AC-triviality, subject to the gate in
`LITERATURE_STATUS.md` §4). **No positive result was obtained, and most of the null is
retired as uninformative by the calibration below.** Project Red line 3 applies: search
failure is never evidence of a counterexample.

## Why hunt in spelling space at all

γ_N is a property of the EXACT word-realized complex, not of the presentation as a tuple
of free-group elements (R1F, machine-checked). Every search in this project — and, as far
as the project's literature review found, every published AC search — normalises to
cyclically reduced words, so the unreduced fibre of every AC class is unentered. R1F
showed the fibre is not cosmetic: AK(3) is at γ_N = 2, eight of its 39 distinct single
spikes are at γ_N = 1 exactly.

The instrument matters as much as the target. Every other γ_N tool here produces LOWER
bounds — the R1c-v2 solver certifies NOT_SPHERICAL exhaustively, which can only ever
produce a negative — and both it and the census die in this region: the solver fails
closed on the A-loops every unreduced spelling carries, and the census costs
∏_v (deg(v)−1)!, which is 1.5e10 already at length 19. A **defect-0 rotation system**,
re-verified in isolation by `gateway_scan.verify_witness`, is the mirror image: a complete
POSITIVE certificate, valid at any length, one-sided in the useful direction.

## What was swept

| group | states | total length |
|---|---|---|
| AK(3) single spikes | 39 | 15 |
| spikes of the length-13 gateways | 78 | 15 |
| AK(3) double spikes | 330 | 17 |
| graft images of the eight gateway spikes | 1,312 | 21–24 |
| the loop-bearing rows `gateway_neighborhood` could not decide | 150 | 19–20 |

**No defect-0 witness was found anywhere**, at 40,000 evaluations per state for the first
four groups and 120,000 for the last. Zero sampler/verifier disagreements; zero states
lost a generator (the gate that would otherwise let a rank-losing state report a spurious
defect 0 — see §"Traps" below).

## The calibration, which is the point of this document

A one-sided hunt's silence is worth exactly its measured detection rate, and nothing was
known about that rate at these lengths. So it was measured, on a ladder of 16 states
**known** to have γ_N = 0 — exact census through length 15 (largest family enumerated:
3,628,800) and a re-verified defect-0 witness at every rung through length 22 — with 10
independent seeds per cell (`witness_sensitivity.json`):

| total length | 10k | 40k | 120k | 200k |
|---|---|---|---|---|
| ≤ 16 | 10/10 | 10/10 | — | 10/10 |
| 17 | 4/10 | 7/10 | — | 10/10 |
| 18 | 3/10 | **4/10** | — | 10/10 |
| 19 | 1/10 | 2/10 | **4/10** | 6/10 |
| 20 | 0/10 | 4/10 | **2/10** | 1/10 |
| 21 | 0/10 | **0/10** | 0/10 | 2/10 |
| 22 | 0/10 | 0/10 | 1/10 | 1/10 |
| 23, 24 | ladder STALLED — no γ_N = 0 rung certifiable even at 2,000,000 evaluations |

(Non-monotone cells at length 20 are seed noise; disjoint seeds, SE ≈ ±0.15 at n = 10.
The rates are optimistic twice over: the climber bounds γ_N from ABOVE always, and the
rungs are pre-selected climbable states, so real states of equal length can only be
harder.)

## The honest verdict on this hunt

| group | states | budget | detection at that length | what the null is worth |
|---|---|---|---|---|
| single spikes, gateway spikes (L15) | 117 | 40k | 100% | **informative** |
| double spikes (L17) | 330 | 40k | 70% | **informative** |
| undecided loop-bearing (L19–20) | 150 | 120k | 40% / 20% | **weak** — see below |
| graft images (L21–24) | 1,312 | 40k | **0%** | **VACUOUS** |

So of 1,909 states swept, **447 carry a null worth recording and 1,312 do not.** The
graft-image group — the largest and the one at exactly the right frontier, since AK(3)'s
γ_N = 2 minus one spike minus one graft is precisely 0 — was run at a budget that has
demonstrated **zero detections on any known-positive state above length 20.** That null is
withdrawn. A re-run of the 486 length-21 members at 2,000,000 evaluations (the tier at
which the ladder did certify length 21) is in progress; lengths 22–24 have no defensible
budget, because 50× the production budget could not certify a single known-positive rung
at 23–24.

The 150-row null at lengths 19–20 sits in between: at 40% and 20% detection, if those
states carried witnesses as findable as the ladder's rungs, roughly 30–60 hits would have
been expected and none appeared. That argues against *many easy witnesses*; it cannot
distinguish "no witness" from "witness beyond reach", and it closes nothing — those rows
remain undecidable by present means (R1G).

## Traps this hunt had to defuse

* **The generator-derivation path.** `sampled_min_defect` and `verify_witness` both derive
  the generator set FROM the words. A state that lost a generator would be silently scored
  as a lower-rank complex and could report defect 0 — a spurious-thickenable path straight
  into a false headline. Every state is now gated on `generators == {x, y}` and non-empty
  relators before scoring, and a hit is re-checked against the same predicate. Verified: 0
  of 1,909 states were affected, so the path was never exercised, but it was open.
* **Bound direction.** Every unreduced state is loop-bearing, so the solver supplies no
  lower bound here. This hunt's output is upper-bounds-only and must never be presented as
  a γ_N landscape — a degrading search and a rising obstruction produce the same histogram.
* **Dedup.** Spiked spellings must be keyed WITHOUT free reduction (`spelling_key`), which
  quotients only by rotation, inversion and relator permutation — all γ_N-invariant. Using
  the project's usual `canon_multi` collapses every spiked spelling back onto its base and
  silently reduces 39 distinct spikes to 1.

## The empirical prior this hunt was always fighting

From the 110,917 measured spiked complexes (`spike_monotonicity.json`): all 464 observed
strict drops are 2 → 1, **not one reaches 0**; the 2,514 bases at γ_N = 1 produced no
thickenable spike in ~58,000 attempts; and every one of the 13,976 spiked complexes at
γ_N = 0 descends from a base already at γ_N = 0. Across the whole corpus, "spiked
thickenable ⇒ reduced thickenable" holds with zero counterexamples, while its converse is
refuted by an explicit counterexample.

That asymmetry is the pre-registration this route needed, and it forces a clean dichotomy:
**either** the implication is a theorem, in which case the unreduced fibre contains nothing
the reduced corpus does not already cover and this route is closed — **or** it fails, in
which case the route has a target and the transfer to an AC-triviality claim runs through
the hypothesis-side gate of `LITERATURE_STATUS.md` §4. Proving that implication is
therefore worth more than any further hunting, and it is where the effort has gone.

## Artifacts

`results/stable_ac/fable/spike_space_hunt.json`, `spike_space_hunt_undecided.json`,
`spike_space_hunt_L21_deep.json` (in progress), `witness_sensitivity.json`. Instruments:
`experiments/stable_ac/fable/spike_space_hunt.py`, `spike_witness.py`,
`witness_sensitivity.py`. Lesson:
`experiments/lessons/calibrate-one-sided-hunts-on-a-positive-ladder.md`.
