# R7c — The drop floor: reducing "spiked thickenable ⇒ reduced thickenable" to one case

> ## CORRECTION, added at session end — READ BEFORE THE BODY
>
> **The pointwise DROP FLOOR stated below is REFUTED, and the claimed equivalence with (SR)
> is wrong in one direction. The body is retained unedited as the record of a failed
> reduction; every statement in it must be read against this box.**
>
> **1. The pointwise drop floor is false.** `drop_floor_check.py` swept 522 canonical
> 2-generator bases (498 examined, 24 skipped by the rank gate), 12,768 spikes and
> **4,125,888 (base, spike, rotation) triples**, of which **2,540,432 sat at
> `defect(ρ(C′)) = 2`** — the sole case the reduction left open. It found **1,408 strict
> drops from base defect 2**, i.e. `defect(C′) = 0` with `defect(ρ(C′)) = 2`.
> Minimal witness, hand-verified and non-degenerate (both relators of length ≥ 2):
> base `("xx","xxY")`, spike `(j=0, k=0, u="x")` → `("xXxx","xxY")`, with
> `defs = [2,0,0,0,0]` and `deltas = [−2,0,0,0]` — exactly the `X⁻ = 1, X⁺ = 0` signature.
> `min defect(ρ) over all strict drops = 2`.
>
> **2. The equivalence claim was the actual error.** The Proposition's forward half
> (DROP FLOOR ⇒ SR) is correct and survives. Its reverse half does not: **(SR) asserts only
> that the base has SOME defect-0 rotation, not that the particular rotation reached by
> restriction has defect 0.** So a base can satisfy (SR) while a different rotation of that
> same base still strict-drops from defect 2 — which is precisely what all 1,408 witnesses
> do: **every one of them has `γ_N(base) = 0` already, via another rotation.**
> Confirmed independently by the R7 auditor, and the repaired statement is theirs: given the
> ceiling, **(SR) ⟺ no spike of a base with γ_N = 1 is thickenable.** That is the one hard
> case restated, not progress into it.
>
> **3. (SR) itself is NOT refuted.** Zero counterexamples in the corpus:
> `pair (γ_N(base), γ_N(spike))` histogram `{(0,0): 5724, (0,1): 428, (1,1): 6616}` — no
> pair with `γ_N(base) > 0 = γ_N(spike)` anywhere.
>
> **4. Caveat 1 of the body is withdrawn; my S2 diagnosis was wrong.** The S2 failures I
> attributed to length-1 relators were a bug in the auditor's own harness (its fibre key
> compared rotation cycles as raw tuples, while `compatible_orders` pins a distinguished
> head dart, so equal cyclic orders compared unequal). After canonicalising: **0 failures**,
> including on `("x","xYY")` alone (all 16 spikes, 96 rotations) and on **all 1,816 spikes of
> every length-1-relator base up to total length 5**. So `|w_j| ≥ 2` must **NOT** be added to
> S2/S4/S5 — they hold under hypothesis (H) alone. Two premises of my diagnosis were also
> wrong: a length-1 relator's corner `{h₀,d₀}` joins `arr(x)` to `dep(x)` and is **not** an
> A-loop, and `("x","xYY")` is loop-bearing because of the `yY` in relator 1, not relator 0.
> Correspondingly, the refutation in item 1 is **not** a length-1 artefact: violations occur
> at spiked-relator lengths 1 through 6 (`{1:2784, 2:3552, 3:6032, 4:8640, 5:13360, 6:12016}`).
>
> **5. What survives, and is now stronger than when the body was written.** The pointwise
> floor `defect(C′) ≥ defect(ρ(C′)) − 2` was never violated: 0 failures in ~277,000
> independently traced rotation systems, including non-reduced loop-bearing bases, rank 3,
> length-1 relators, and 12,000 sampled rotations of AK(3)'s own gateway spikes. The
> **SPIKE CEILING is therefore citable as a THEOREM** (MACHINERY, under (H)), per the
> independent audit. Identity (★) held in **all** 46,384 strict drops with
> `(X⁻,X⁺) = (1,0)` in 100% of them, and `δ_comp = 1` **never** co-occurred with a strict
> drop — `(defect(ρ), δ_comp)` over strict drops is `{(2,0): 1408, (4,0): 44976}`. That
> 100% correlation is the surviving structural lead: a proof of the repaired statement would
> be built from it.
>
> **6. Non-negativity (Observation 1) stands** — no negative defect in any of the 4,125,888
> triples, corroborating the 42,632-rotation check in the body.
>
> Instruments: `experiments/stable_ac/fable/drop_floor_check.py`,
> `results/stable_ac/fable/drop_floor_check.json` (1.1 MB, complete).

STATUS: **REDUCTION, author-derived — REFUTED, see the correction box above. Retained as a
record of a failed route, per the standing rule that negative results are results.**
Claim class:
MACHINERY (a property of exact word-realized complexes). Nothing here claims anything
about AK(3)'s AC-triviality or stable AC-triviality in either direction. What it does is
replace an open implication by a strictly smaller open statement, and say exactly what
would settle it.

## Why this implication is the highest-value item in spelling space

γ_N is a property of the EXACT word realization, not of the free-group tuple (R1F,
machine-checked). Consequently every AC search ever run in this project — and, as far as
the literature review reached, every published one — normalises to cyclically reduced
words and never enters the unreduced fibre of a class. R1F showed the fibre is not
cosmetic: AK(3) sits at γ_N = 2, and eight of its 39 distinct single spikes sit at
γ_N = 1 exactly.

So the fibre either matters or it does not, and one implication decides which:

> **(SR) Spiked thickenable ⇒ reduced thickenable.** If some spelling of P is orientably
> thickenable, then the cyclically reduced P is.

If (SR) is a **theorem**, the unreduced fibre contains no thickenable complex that the
reduced corpus does not already exhibit; spelling space closes, the ~141,000 existing
reduced verdicts extend to whole spelling families, R7's hunt is closed by proof rather
than by budget, and the 150 undecided loop-bearing rows are decided. If (SR) **fails**,
the counterexample is a concrete target and the route has somewhere to go. Either
outcome is a result. Note the transfer of a *positive* finding to an AC-triviality claim
still runs through the hypothesis-side gate of `LITERATURE_STATUS.md` §4; (SR) itself is
pure machinery and does not touch that gate.

The empirical prior, from the 110,917 measured spiked complexes of
`spike_monotonicity.json`: all 464 observed strict drops are 2 → 1, **not one reaches 0**;
the 2,514 bases at γ_N = 1 produced no thickenable spike in ~58,000 attempts; and every
one of the 13,976 spiked complexes at γ_N = 0 descends from a base already at γ_N = 0.
Zero counterexamples in the whole corpus, while the CONVERSE of (SR) is refuted by an
explicit counterexample. That asymmetry is the pre-registration this note acts on.

## The four-op decomposition (from R7 §S4, whose audit is in flight)

A spike is resolved into four elementary ribbon-graph ops interpolating between the base
ribbon graph carrying `ρ(C')` and the spiked one carrying `C'`: delete the old corner
`e_0`, insert the spike loop `ℓ`, insert the seam `J_1`, insert the seam `J_2`. The
machine check over 33,008 spiked rotation systems found the deletion contributes
`δ ∈ {0, −2}` and each insertion `δ ∈ {0, +2}`, with no value outside those ranges. Write
`X⁻ ∈ {0,1}` for the deletion event and `X⁺ ∈ {0,1,2,3}` for the number of splitting
insertions. Then, pointwise in `C'`,

    defect(C') − defect(ρ(C'))  =  −2·X⁻ + 2·X⁺.                        (★)

The observed pointwise histogram of `defect(C') − defect(ρ(C'))` is
`{−2: 128, 0: 15024, +2: 15488, +4: 2368}` — consistent with (★), and the source of the
**pointwise floor** `defect(C') ≥ defect(ρ(C')) − 2`, which is what the SPIKE CEILING
γ_N(spike) ≥ γ_N(P) − 1 rests on.

## The reduction

**Definition (DROP FLOOR).** For every base `P`, spike `(j,k,u)` and compatible rotation
system `C'` of the spiked complex: if `defect(C') = defect(ρ(C')) − 2`, then
`defect(ρ(C')) ≥ 4`.

**Observation 1 (the ladder has no rung below 0).** Defect is even and **non-negative
pointwise** — each compatible rotation system determines a closed orientable surface and
the defect is twice its genus sum. Verified empirically this session: over 42,632
compatible rotation systems of all 2-generator presentations with both relators of length
≤ 3, the defect histogram is `{0: 23048, 2: 19584}` and there are **zero** negative
values. Hence `defect(ρ(C')) = 0` cannot support a strict drop: (★) would force
`defect(C') = −2`.

**Observation 2 (a strict drop is the extremal event).** By (★), `δ = −2` holds iff
`X⁻ = 1` **and** `X⁺ = 0` — the deletion must be defect-reducing and **all three**
insertions must be non-splitting simultaneously. A strict drop is therefore not generic;
it is the single most constrained configuration in the walk. This is consistent with its
rarity in the data (128 of 33,008 rotations, 0.39%).

**Proposition (REDUCTION).** Given the pointwise floor, the DROP FLOOR is **equivalent**
to (SR), and by Observation 1 it reduces to the single case `defect(ρ(C')) = 2`.

*Proof.* (DROP FLOOR ⇒ SR.) Let `C'` realize `γ_N(spike) = 0`, i.e. `defect(C') = 0`. The
pointwise floor gives `defect(ρ(C')) ≤ 2`. By the DROP FLOOR, `defect(ρ(C')) = 2` would
require a strict drop from a base defect ≥ 4, contradiction; and `defect(ρ(C')) = 2` with
no strict drop contradicts `defect(C') = 0` via (★), since `δ = −2` is the only way to
reach 0 from 2. So `defect(ρ(C')) = 0`, and `ρ(C')` is a compatible rotation system of the
base witnessing `γ_N(P) = 0`. (SR ⇒ DROP FLOOR.) A strict drop from `defect(ρ(C')) = 2`
lands at `defect(C') = 0`, exhibiting a thickenable spelling over a base whose rotation
`ρ(C')` has defect 2; iterating (SR) over the base's other rotations is not needed —
(SR) asserts the base has *some* defect-0 rotation, so the two statements differ only by
that quantifier, and Observation 1 removes the remaining case `defect(ρ(C')) = 0`. ∎

**What this buys.** The spike ceiling alone gives only `γ_N(spike) = 0 ⇒ γ_N(P) ≤ 1` — one
unit short of (SR). The reduction says the missing unit is not a second inequality to be
found but a single extremal configuration to be excluded: *the deletion cannot be
defect-reducing while all three insertions are simultaneously non-splitting, over a base
rotation of defect exactly 2.*

## The two caveats that travel with this note

1. **It inherits R7 §S4's audit status.** (★) is R7's master formula, and the independent
   adversarial audit of R7 is still running. It has already found the S2 fibration failing
   on **degenerate bases with a length-1 relator** (witness: `("x","xYY")` — `ρ` lands
   outside the base census, fibre size 3 against the predicted `D(D+1) = 6`). Whether the
   repair is `|w_j| ≥ 2` or something stronger is not yet settled, so every statement here
   carries an unresolved hypothesis on relator length. AK(3)'s relators have lengths 6 and
   7, so a `|w_j| ≥ 2` repair would not touch the AK(3) application — but that is a
   prediction, not a verdict, until the audit lands.
2. **Non-negativity is verified, not proved here.** Observation 1 rests on pointwise
   non-negativity of the Neuwirth defect. The 42,632-rotation check above found no
   counterexample, and the genus reading explains why, but the proof is cited from the
   Euler dictionary rather than reproduced. If non-negativity failed, `defect(ρ) = 0` would
   re-enter and the reduction would lose its base case.

## Status of the decision

`experiments/stable_ac/fable/drop_floor_check.py` is testing the DROP FLOOR directly,
reporting the joint `(defect(ρ), defect(C'))` histogram, the minimum base defect over all
strict drops (the sharpest form of the answer), the joint `(defect(ρ), δ_comp)` histogram
over strict drops — the correlation a proof would be built from — and, independently, any
`(base, spike)` pair with `γ_N(spike) = 0 < γ_N(base)`, which would be a direct
counterexample to (SR). The two must agree; disagreement means a harness bug, not a
discovery.

Result to be recorded here on completion, with the count of triples examined **at base
defect exactly 2** stated separately — a CONFIRMED verdict is worth precisely that number,
not the total triple count.

## Artifacts

Instrument: `experiments/stable_ac/fable/drop_floor_check.py` (in flight), reusing
`audit_r7_core.py` / `audit_r7_checks.py`. Output:
`results/stable_ac/fable/drop_floor_check.json`. Upstream: `R7_SPELLING_SPACE.md` §S4–S5
(UNAUDITED), `R1F_REDUCTION_AND_SPIKES.md` (censuses), `spike_monotonicity.json`.
