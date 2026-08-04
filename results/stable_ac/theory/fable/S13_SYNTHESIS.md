# S13 — What arbitrary stabilization buys: the S-line's answer

Branch `claude/stable-ac-conjecture-stabilization-rwo9as`. **This branch must be merged into
`fable/proof` by the user** — a cloud session can only push to its own `claude/*` branch, so
nothing here reaches `fable/proof` on its own. No PR opened (`FRAMING` trap 10).

Session brief: does the stable AC conjecture get easier for hard presentations — AK(3), the
124 unsolved Miller–Schupp AC-classes — once the rank is allowed to grow well past 3, say to
9 or 10 generators? Use change of variables and Lemma 11. Is there a simple general method?

## 1. The answer

**Not by any mechanism — but yes, decisively, for decidability.** Two halves, and they must
be kept apart.

**(i) Almost no mechanism — with one exception found late, and it matters.** The exception
first: A6's **SPLIT** move (a fresh generator with a *length-3* definition `tuv`, used in
further positions, so its edge carries three or more 2-cell germs) **does** lower γ_N — it
is what took AK(3) from γ_N = 2 to the rank-13 cubic form `C1` at γ_N = 1. That refutes this
file's earlier blanket claim that re-describing the relators is worthless, and it is the
only high-rank mechanism this session found that moves γ_N in the right direction. With that
said, every *other* way of using extra generators that we could isolate is provably inert or
measurably counterproductive: abbreviation is a *CW subdivision* of the
presentation complex (S3, audited), change of variables is entirely a *depth-1* phenomenon
(F1), stabilization itself and the first slide over a fresh stabilizer are inert
(T4, T4′), and bare AC3 conjugation only destroys. The one measurement suggesting
certificates get *commoner* with rank was, under adversarial audit, measuring **relator
length** (S10, retracted). Hunted at rank ceilings 2–6 on AK(3) (A7: 0/40 against a
length-matched control's 39/40) and at depths 0–1 on all 124 unsolved classes, the extra
generators produced **no certificate for any open case**.

**(0) Read (i) and (ii) through this, added last and overriding both.** The session's nulls
were originally presented as evidence about AK(3). They are not — see §3z-bis, **retracted**,
and `S16_CONTROL_RETRACTION.md`. The calibration control was itself already thickenable, so
it measured *survival* of a certificate, not *creation* of one; all 759 of its hits have
defect chain `(0,0,0,0)`. Against four AC-trivial, length-matched, **non**-thickenable
sources the pipeline scores 0 in 61,157 — exactly AK(3)'s score. **The real finding is
about the instrument, not the target:** the chord + SPLIT pipeline created `γ_N = 0`
**0 times in 106,268 decided states** from five non-thickenable roots (plus 0 in 1,470 rank-5
flip-census opportunities) while remaining demonstrably able to *find* certificates that
already existed. It is certificate-preserving and certificate-non-creating, so it can only
settle a presentation whose rank-2 root is already thickenable.

**At the strength the evidence supports:** AK(3)'s own rank-2 spelling has `γ_N = 2` (exact
census, 86,400 rotations), and no thickenable member of its class has been found in the
124,296-member rank-2 matched harvest or the 171,842-member depth-1 stable class — **bounded
nulls, not an absence proof**; their class-wide negation would *be* the disproof. So *on the
evidence* the cubic route **did not** settle AK(3): the pipeline lowered `γ_N` (527 descents
4 → 2, plus `C1` at `γ_N = 1`) but never reached 0. That is a **measured instrument
limitation, not a proved obstruction** — no monotonicity theorem forbids reaching 0
(`S15` §6). And this is one move set only: on the A7 ladder a plain AC1–AC5 search created
`γ_N = 0` from a non-thickenable length-13 base in **39 of 40** runs. Nothing here bounds
`Γ(AK(3))` from below; see `S15_ONE_SIDEDNESS.md` for why no instrument on this route can.

**(ii) But high rank buys decidability, and the size of the effect is now measured.** The
compatible census is `∏(deg−1)!`, so what matters is the *ratio* ℓ/n of total length to
rank. A10's certified ladder, 163 rungs, two instruments agreeing with `missed = 0` in every
cell:

| total length | rank 2 | rank 4 | rank 6 | rank 8 |
|---|---|---|---|---|
| 13 | 0.90 | 1.00 | 1.00 | 1.00 |
| 16 | **0.00** | 0.90 | 1.00 | 1.00 |
| 19 | 0.00 | 0.30 | 1.00 | 1.00 |
| 22 | 0.00 | 0.00 | 0.30 | **1.00** |
| 25 | — | — | 0.00 | **0.40** |

Median census at length 22: **1.3 · 10¹³ at rank 2 against 5,760 at rank 8**. The decidable
region is ℓ/n ≲ 3 — exactly the cubic regime. **Hard limitation:** this helps
*natively* high-rank states only. Lifting a rank-2 state to rank 9 by chord refinement
changes the census not at all (Lemma S3′), so it does **not** buy back the 1,312 states an
earlier session retired as undecidable.

**And the sharpest single demonstration of (i) and (ii) together:** AK(3) *does* have a
**cubic triangular form at rank 13** — all 13 relators of length 3, all 13 multiplicities
exactly 3, reached by 7 chord refinements and 4 SPLITs with no destabilization
(A6/`S4B`). **The whole chain was re-verified here with independent code**: un-SPLITting C1
four times (substitute each fresh `t ↦ λ`, drop its definition relator `tuv`) returns the
rank-9 root exactly, and un-merging that root seven times (each chord is a generator
occurring twice in two distinct relators; merge the two relators across it) returns
`('XyxyXY','xxYYYYx')` — cyclically **equal to AK(3)**. Plus trivial group at Todd–Coxeter
index 1, 481 cosets. So C1 is in AK(3)'s stable class, established without trusting the
search that produced it. Its entire
compatible census is **8,192**, against 86,400 for AK(3) at rank 2 — so at rank 13 the
question becomes trivially cheap to ask. Its answer is `minimum_defect` 2, i.e. **γ_N = 1**:
better than AK(3)'s own γ_N = 2, and **exactly tying** the best previously reached anywhere
in AK(3)'s class (a γ_N = 1 gateway found at rank 2 and length 14, `gateway_scan.json`).
So the extra nine generators bought a much cheaper question and *no better answer*.

## 2. What was proved

| # | statement | status |
|---|---|---|
| **S-a** | For a balanced presentation of the **trivial** group, the AC4 relator `z` may be replaced by `z·w` for any `w` — and **only** for `w ∈ ⟪r₁..rₙ⟫`, i.e. the triviality hypothesis is exactly sharp (biconditional) | proved (A1) |
| **S-b** | Every balanced presentation of the trivial group triangulates to relators of length ≤ 3 at rank `n + Σ(|rᵢ|−3)` — rank 9 for AK(3), and **8** by sharing a definition | proved (A1); it is Lackenby's Lemma 3.1 minus the thickenability hypothesis (A2) |
| **F1** | The whole `Aut(Fₙ)` orbit lies in `~^{(1)}`: one stabilization realizes any change of variables | proved (A1) |
| **S3** | A chord refinement is a **CW subdivision**: `|K_{P′}| ≅ |K_P|`, and the *entire defect histogram* is preserved by a dart-level bijection | proved + **audited**; 1,525 triangulations, zero counterexamples |
| **T1, T4, T4′** | AC1, cyclic rotation and relator permutation are homeomorphisms; AC4/AC5 wedge on a 2-disc; and the **first slide over a fresh stabilizer is a subdivision** | proved (A8), unaudited |
| **T2** | A bare AC3 conjugation **is a single spike** up to cyclic rotation, so the whole spike calculus transfers to AC3 | proved (A8), unaudited |
| **S4.1/S4.2/S4.3** | Sign rigidity forces a cubic triangular presentation's abelianised matrix to be nonnegative with all row and column sums 3; hence `|det| = 1` is **impossible below rank 4**; and a degenerate length-3 relator collapses the rank | proved (A6), unaudited |
| **S8** | Generator splitting never decreases γ_N (`link(P)` is a **minor** of `link(P′)`) | conjecture + proof sketch + machine certificate; 632 states, none below base. **Under audit (A14) and under pressure**: A6's *different* SPLIT move (a length-3 definition `tuv`, not S8's length-2 bigon `uG`) demonstrably lowered γ_N from 2 to 1 along the AK(3) → C1 chain. The two moves must not be conflated, but S8 should be treated as doubtful until the audit lands |
| **SR refuted** | Free reduction can **destroy** thickenability, on a balanced presentation of the **trivial group** | proved by exhaustive census (A10), re-verified here — see §3c |

## 3. What was measured

- **Triangulation is inert**: 1,525 + 480 triangulations, defect histograms bit-identical.
  AK(3) is `minimum_defect` 4 (γ_N = 2) at rank 2 **and** at rank 9, with the same census
  size 86,400 — a peel never changes an original germ's degree.
- **Splitting is monotone**: 632 states at ranks 4 and 6, none below base.
- **Move flip rates, and they are much better on the trivial group than S6 first reported**
  (A14 audit §1.5). S6's published rates came from an *unrestricted* rank-2 corpus; the AC
  programme only ever acts on presentations of the trivial group. Re-measured on two corpora
  built and processed identically in the same length band, the control reproducing S6's
  numbers to sampling noise so the shift is attributable to the restriction alone:

  | corpus | AC2 destroys / thickenable base | AC2 **creates** / non-thickenable base | bare AC3 destroys | AC3 cancelling |
  |---|---|---|---|---|
  | **trivial group** | 28/133 = **21.1 %** | 58/313 = **18.5 %** | 9/156 = **5.8 %** | 0/1,432 |
  | unrestricted (control) | 236/481 = 49.1 % | 30/568 = 5.3 % | 175/789 = 22.2 % | 0/1,432 |
  | S6 as published | 51.5 % | 7.0 % | 24.0 % | 0/3,413 |

  The control reproduces S6's published rates, so the shift is the restriction and not the
  instrument, and it survives length stratification (checked per total length 7–10). On the
  presentations that actually matter, **an AC2 slide creates the Lackenby certificate 18.5 %
  of the time** — 3.5× S6's headline — and because non-thickenable bases are the common
  case, AC2 is **net-positive in absolute terms** (58 creates against 28 destroys). AC3's
  alarming "24 % destroys" is 5.8 % where it matters. AC1, rotation, AC4/AC5 and T4′ slides:
  0 flips in 2,236 + 4,472 + 1,118 + 3,332.
  **This is the strongest single reason to believe the certificate hunt is a viable method
  rather than a long shot**, and it is the one number in the session that moved decisively
  in the favourable direction under audit.
- **Depth ladder, length-matched** (A7): an AC-trivial control returns **39/40** hits across
  rank ceilings 2–6; **AK(3) returns 0/40** on the same rungs, seeds, move set and budget.
- **Depth costs detection at fixed budget** (this line's `--target` mode): control detection
  6/6 at depth 0 falls to 2/6 at depth 1 — precisely T4′'s prediction, since budget spent on
  the inert first slide cannot move γ_N.
- **The cubic regime is rich** (A6, exhaustive): of the 43,008 non-degenerate cubic
  triangular presentations of the trivial group at rank 4, **27,648 (64.29 %) are
  thickenable**.
- **AK(3) has a cubic form, and the first search's null was a search artefact** (A6, second
  pass). The first attempt reported 0 hits in 48 roots; the scaled search found **2 in 28**.
  What changed was not the budget but the *beam*: a pure cost ranking cannot leave the
  Σ|δ| = 2 parity plateau, because leaving it provably requires a cost-*increasing* move, so
  filling 30 % of each beam at random turned 0/48 into 2/28 — and the calibration reverses
  with it (AK(3) 2/28 against a matched ladder's 0/35). A textbook case of a null that was
  measuring the searcher, not the target.
- **The density trend is a length effect** (A12 audit): holding *per-relator* length fixed,
  the thickenable fraction is 0.868 / 0.868 / 0.834 / 0.780 at ranks 2/3/4/5 — flat, then
  slightly decreasing.
- **The 124 unsolved classes are all non-thickenable, and this one is CERTIFIED, not a
  null** (A9). All 124 representatives plus **67,864 distinct AC-class members** decided
  `NOT_SPHERICAL` by an exact procedure (`disconnected_split.decide_pair`, every row
  `exhaustive = true`, `IN_SCOPE`, `L = 1`), with an **independent second solver** agreeing
  on 123/124 and failing closed on 1 — zero disagreements — and Todd–Coxeter confirming all
  124 present the trivial group. The instrument's positive ladder is 54/55 with **zero false
  negatives and no length degradation**, which is exactly why this null is informative where
  a sampler's would not be.

### 3z. The largest exhaustively decided region of AK(3)'s stable class

45,264 states at ranks 12–13, reached from AK(3) by chord refinements and SPLITs and
persisted with the full move chain back to their root; **45,111 decided exactly** by a numba
kernel that enumerates the whole compatible rotation family (no sampling), validated against
the audited oracle on 44 states with exact agreement:

| γ_N | defect | count | share |
|---|---|---|---|
| **0 — thickenable** | 0 | **0** | **0.000 %** |
| 1 | 2 | 527 | 1.17 % |
| 2 | 4 | 40,100 | 88.89 % |
| 3 | 6 | 4,484 | 9.94 % |

Every row is a certificate, not a bound. **Limits, which matter:** this is one search's
frontier from 47 roots — a vanishing fraction of the class; dedup is on canonical cyclic
words, *not* up to generator relabelling, so 45,264 upper-bounds the distinct complexes; and
there is **no positive control** — no γ_N = 0 state at rank 12–13 is known to exist anywhere,
so the hunt's detection rate is unmeasured. The verdicts are exact; the *null about the
class* is not calibrated.

**T-S17 — AK(3)-SPECIFIC, not a property of the region (narrowed after the control ran).**
Proximity to cubic form is **anti-correlated** with low defect *for AK(3)*:

| Σ\|δ\| from cubic | decided | γ_N = 1 | γ_N = 2 | γ_N = 3 |
|---|---|---|---|---|
| 2 (one SPLIT away) | 1,232 | **0** | 1,028 | 204 |
| 4 (two SPLITs away) | 43,879 | **527** | 39,072 | 4,280 |

The states *closest* to cubic form contain **no** γ_N = 1 members at all. But the matched
control's rates are flat across the same axis (1.63 % at Σ|δ| = 2 against 1.49 % at
Σ|δ| = 4), so this is **not** a property of the rank-12/13 region — it is something about
AK(3). The transferable half of the trap survives: "drive toward cubic form" is not a proxy
for "drive toward a certificate", because the chain's γ_N is destroyed by the SPLITs and
preserved by the refinements, so a cost-greedy march to the normal form is the wrong
instrument for a certificate hunt.

### 3z-bis. ~~THE CALIBRATED NEGATIVE — the strongest result of the session~~ **RETRACTED**

> ## ⛔ RETRACTED IN FULL — see `S16_CONTROL_RETRACTION.md`
>
> The control family was widened to five AC-trivial rank-2 sources **all of total length 13**
> (so no length confound). The source `γ_N` values were then recomputed in this clone with the
> repo's own decider:
>
> | source | γ_N of the source | decided | γ_N = 0 hits |
> |---|---|---|---|
> | the control used below, `("XYXXY","XXYXYXXY")` | **0 — SPHERICAL** | 50,320 | **759** |
> | ctrl2 `src0`–`src3` (all NOT_SPHERICAL) | ≥ 1 | 61,157 | **0** |
> | **AK(3)** (NOT_SPHERICAL) | 2 | 45,111 | **0** |
>
> The 1.51 % was **not** a property of being AC-trivial. It was a property of that one root
> already being thickenable. Three independent non-thickenable sources score exactly what
> AK(3) scores: zero. The between-source variance inside the control family swamps the
> target-vs-control gap this section was reading, so **AK(3)'s 0/45,111 is not a fact about
> AK(3)**, and the "expected ≈ 681" is void with the rate that produced it.
>
> The tell was in this section's own line below — *"only the source's rank-2 defect
> differs"*. That was the whole effect, named and then attributed elsewhere.
>
> What survives, and is worth more, is the instrument fact (S16 §4): across **106,268**
> decided states from **five** independent non-thickenable roots, the cubic split search
> created γ_N = 0 **zero** times. In this move set thickenability is **inherited, not
> generated** — exactly as S3 (chord refinement = CW subdivision, defect histogram preserved)
> and T4/T4′ (stabilization inert) predict. So this search could never have certified AK(3);
> it can only confirm roots that were already done.

*Everything from here to the end of §3z-bis is the retracted text, kept verbatim for the
record.*

The 3z null above was uncalibrated: with no γ_N = 0 state known to exist at rank 12–13, "AK(3)
has none" and "the region has none" were indistinguishable. Building the control settles it.

Control source `("XYXXY","XXYXYXXY")`: AC-trivial, rank 2, total length 13, γ_N = 0,
triangulating to rank-9 roots with Σ|δ| = 14 — **matched to AK(3) on every axis the pipeline
sees**. Identical pipeline, kernel and budgets; only the source's rank-2 defect differs.

| | decided exactly | γ_N = 0 | rate |
|---|---|---|---|
| **control** | 50,320 | **759** | **1.51 %** |
| **AK(3)** | 45,111 | **0** | **0.00 %** |

At the control's rate AK(3)'s pool should have contained ≈ **681** thickenable members. It
contained **none**. So the rank-12/13 region is *not* structurally γ_N ≥ 1, and **AK(3)'s
0/45,111 is a fact about AK(3), not about the region.** This is the first calibrated
high-rank negative on this line; every earlier one was a reachability null with no way to
separate "absent here" from "absent everywhere".

One control hit was verified **six ways** — the protocol reserved for an AK(3) hit, run to
validate the instrument: structural check; the oracle `gamma_N_factorial_n` (defect 0,
genus 0, census 9,216, two accepting orders); the fast kernel agreeing; Todd–Coxeter trivial
at index 1; `witness_check_n` (defect 0, compatible); and a chain replay whose root un-merges
in exactly seven steps back to the source.

**Mechanism, traced per step — and it confirms Theorem S3 live on a fresh corpus.** γ_N is
*constant* across all eight chord refinements for all three bases traced (AK(3):
`4,4,4,4,4,4,4,4`; two thickenable controls: `0,0,0,0,0,0,0,0`), and the loss happens
entirely at the SPLITs: the greedy chain loses γ_N = 0 at the **first** SPLIT.

**Caveats, all binding.** The control is **one source** — the search budget was consumed by
source 0, so 1.51 % is that source's descendant rate, not a cross-source constant. No
p-value: both pools are move-tree frontiers, not independent draws. Seeds and pool sizes
differ. The comparison is like-for-like by construction, not randomised. What it supports is
therefore: *AK(3)'s stable class is anomalously devoid of certificates in this region
relative to the one matched AC-trivial class measured the same way* — pointing at the
disproof side of `FRAMING` §2, and still not evidence of a disproof.

### 3a. The one concretely actionable find: six γ_N = 1 gateways

Closing the bracket (exhaustive `NOT_SPHERICAL` ⇒ γ_N ≥ 1, plus a re-verified defect-2
witness ⇒ γ_N ≤ 1) gives **exact** γ_N without a census:

| row | pair | length | γ_N |
|---|---|---|---|
| `aca_117` | `YYYXyyx, YXXXyxx` | 14 | **1** |
| `aca_11` | `YXXXyxx, YYYXyxyx` | 15 | **1** |
| `aca_121` | `YXXXyxx, YYYYXyyyx` | 16 | **1** |
| `aca_17` | `YXXXYxYx, YYYYXyyyx` | 17 | **1** |
| `aca_30` | `YYXXyx, YYYYYxyXXyX` | 17 | **1** |
| `aca_122` | `YXXXyxx, YYYYYXyyyyx` | 18 | **1** |
| `aca_115` = **AK(3)** | `YXYxyx, YYYYxxx` | 13 | **2** |

**Both halves of every bracket were re-verified independently by the orchestrator.**

- *Lower half* (γ_N ≥ 1): all six re-run through the cut-scheme solver and Todd–Coxeter —
  **6/6 `NOT_SPHERICAL`, 6/6 trivial group**. AK(3) reproduces at defect 4, index 1.
- *Upper half* (γ_N ≤ 1): only `aca_117`'s census is small enough to enumerate exactly
  (518,400 rotations → `minimum_defect` 2). The other five need 3.6 · 10⁶, 2.9 · 10⁷,
  2.6 · 10⁸, 2.6 · 10⁸ and 2.6 · 10⁹ rotations, so instead their **stored rotation-system
  witnesses** were fed to `witness_check_n`, which recomputes the defect from the words and
  the rotation, independently of the sampler that found it. It returned **defect 2 on all
  five** (as a refusal to certify sphericity — its message is literally "defect 2 != 0" —
  which is the computation we wanted). Compatibility passed in every case, so each is a
  genuine compatible rotation system of defect 2, giving γ_N ≤ 1.

So the six γ_N = 1 values are bracketed from both sides by instruments independent of the
one that produced them. The witnesses are stored per row in
`results/stable_ac/fable/u124_sweep.jsonl` under `sample.witness` and are replayable.

By the project's audited graft ceiling (a graft lowers γ_N by at most 1), a thickenable
member is only reachable from a γ_N = 1 state. **Six of AK(3)'s 123 unsolved siblings sit
one unit closer to Lackenby's hypothesis than AK(3) itself does** — and 39,108 states inside
their classes have already been swept without a hit. They are the sharpest targets this
session produced, and they are targets *at rank 2*, which is the final irony of the S-line:
the best lead is not at high rank at all.

### 3b. The gateways cluster on one relator — a lead, not a result

Four of the six carry the **same** relator, `YXXXyxx` = `y⁻¹x⁻³yx²`, i.e. the
Baumslag–Solitar relation `y⁻¹x³y = x²`. That relator appears in only 11 of the 124 classes:

| population | rows | certified γ_N = 1 |
|---|---|---|
| contains `YXXXyxx` | 11 | **4** |
| all others | 113 | 2 |
| contains `YXXXyxx`, **length ≤ 18** | 8 | **4** |
| all others, **length ≤ 18** | 36 | 2 |

The length control matters and is applied above, because the witness sampler's detection
rate falls with length (A9: 1.00 at L13 down to 0.00 at L19), so a "γ_N = 1" label is easier
to earn on a short row. Inside the band where witnesses are findable the enrichment is
50 % against 5.6 %.

**What this is not.** The six are the rows where a defect-2 witness was *found*; the others
carry γ_N ∈ {1, 2} brackets that are merely unresolved, so some of the 113 may be gateways
too. Eight versus thirty-six is a small sample, the classes are a structured family rather
than independent draws, and **no p-value is quotable** (`contrast-length-confound.md`). Read
it as: *if you are looking for the class closest to a Lackenby certificate, start with the
Baumslag–Solitar-relator rows and close their brackets first.*

## 4. What the session got wrong, and how it was caught

Recorded because the corrections are the most transferable part of the work.

1. **A unit error** — `minimum_defect` is `2·γ_N`. I compared one against the other,
   manufactured a "γ_N went 2 → 4 under triangulation" anomaly, and filed a whole trap
   (T-S6) to explain it. Both were wrong; the value is invariant. *Caught by* the
   falsification run predicting exact preservation, then by the A5 audit.
2. **The density confound** — matching **total** length across ranks does not match length
   at all, because `mean relator length = total / rank`. The session's only positive
   empirical claim was the diagonal of a matrix whose real variable was relator length.
   *Caught by* the A12 audit re-implementing the sampler and changing only the acceptance
   variable. This is `contrast-length-confound.md` recurring **in a file that cites it
   twice**.
3. **Three ways a search silently starves** — reseeding from the root, pure length descent,
   and an absolute rather than root-relative length cap. Detection sat at 0.25–0.30 across a
   10× budget change while 148 hunts at 2,500 nodes finished in 12 seconds. *Caught by*
   instrumenting `pops` against the budget. Fixed: 0.30 → 0.46 → 0.54, and decided/pops from
   0.048 to 0.80.
4. **A silent false negative** — the hunt decided only children, never its start state, so a
   root already carrying the certificate was reported as a miss. *Caught by* a unit test.
5. **Over-reading a conjecture refutation** — a spelling chain with defects 0 → 2 → 0 refutes
   Conjecture SR *for presentations in general*, but Todd–Coxeter gives that presentation
   index **4**: it presents ℤ/4, not the trivial group. The version the AC programme needs is
   untouched. *Caught by* checking the group before writing the sentence.
6. **A wrong class count** — the 124 `aca_*` classes are not `Aut(F₂)` orbits but "AC moves
   together with change of variables" classes, and 124 is an **upper bound**. *Caught by* the
   A12 audit reading the source branch's README.
7. **Estimated timestamps** in the session log instead of measured ones, in direct violation
   of a filed lesson. *Caught by* re-reading the lesson; corrected from `git log`.

## 5. Where the leads are, for the next session

1. **Q(F2): is `~^{(1)} = ~^{(k)}`?** The bounded-stabilization filtration is untouched in
   the literature (A2, Q4). A collapse would say "10 generators is provably worth what 3 is";
   strictness would be the first such result. Nothing in this session settles it.
2. **Conjecture SR restricted to the trivial group.** The general version is false. The
   trivial-group version — the only one the AC programme can use — is unrefuted, and
   A8 measured **0 creates in 2,195** on that side. Settling it decides whether the spelling
   route is alive at all.
3. **The cubic regime.** 64.29 % of rank-4 cubic presentations of the trivial group carry a
   certificate, and A6's SPLIT move keeps relators at length 3 while raising the rank with
   bookkeeping that is never the obstruction. Whether AK(3) has a cubic form is a reachability
   question in a state-dependent move set, and it has only had a small search.
4. **Bound `m` in Lemma 11** (the authors' own open problem). A bound turns Cor. F1 from an
   existence statement into an algorithm and makes depth-1 excursions searchable.
5. **Split-based brackets: BUILT, TESTED, and TOO LOOSE** (A13, complete). S8's
   monotonicity read forwards *is* a valid tool — a witness for a split of `P` upper-bounds
   `P` — and the instrument is sound (24 tests on bound direction; every witness verified
   twice, the second time by a from-scratch defect rebuild). It simply is not tight enough:
   splitting shrinks the census by **paying in defect**, and at the exchange rate the long
   rows need, the payment exceeds the quantity being measured. Forced to the reductions the
   targets actually require (10³–10⁶), it recovered the true γ_N in **0 of 30** calibration
   cells; on the six known gateways, 2 of 6 exact at no reduction and **0 of 6** at any
   useful one. Result on the targets: **0 brackets closed, 0 new gateways, nothing reached
   0**, and 40 rows came out worse than A9's. Certified brackets across the 124: 8 → 8.
   Two by-products are worth keeping: **Conjecture S8 survived again** (0 violations in 65
   two-sided cells at split depths up to rank 14, far beyond S8's own evidence), and the
   γ_N ≤ 4 tail collapses from 21 rows to 3 — though at reductions of 10⁸–10⁹, far past the
   calibrated band, so that "3" is a ceiling with unmeasured slack. **Do not reach for this
   instrument again without first forcing its calibration ladder to make the same reduction
   the targets need** (trap T-S14b: a ladder allowed to skip the hard part measures nothing —
   the first calibration scored a fake 100 % exactly that way).
6. **The one untested high-rank mechanism: entangled AC2 slides.** S7 §4 isolated what depth
   `k ≥ 2` can buy that depth 1 cannot — a slide by a conjugate of a relator that already
   involves *several* new generators, with no depth-1 serialization, because Lemma 11
   removal substitutes a definition back and undoes exactly the entanglement that made the
   slide interesting. Nobody has isolated and measured that class of move. The experiment is
   well posed: at rank `n+2`, classify states by whether a relator involves both `y₁` and
   `y₂` irreducibly, and compare γ_N flip rates against the non-entangled slides. It is the
   last mechanism this session did not test.
7. **The disproof side.** AK(3)'s depth-1 stable class is 0 thickenable in 171,842 against
   an AC-trivial class's 54.8 % under the same operator, and A7's length-matched ladder is
   0/40 against 39/40. Both are bounded, confounded by length, and — per S3's corrected trap
   T-S9 — nulls about **orientable** thickenability only. They point at the disproof side of
   `FRAMING` §2 without being evidence of one.

### 5b. The cheapest unexploited speed-up: planarity as a pre-filter

In the cubic regime the link is **3-regular on 2N germs with 3N edges** (C1: 26 germs, 39
edges, connected), and the compatible census is exactly `2^N` — 8,192 at N = 13, still under
10⁶ at N = 20. Planarity of the link is **necessary** for thickenability, and `C1`'s link is
in fact certified NONPLANAR, which is *why* its γ_N exceeds 0.

So a linear-time planarity test would reject most candidates before any census runs. The
repo has no fast path for this: `classify_cut_support` decides planarity but takes **3.9 s**
on `C1` — 25× the census it is meant to avoid — and `networkx` is not installed in this
container. The Euler bound cannot help either: a cubic link has `3N ≤ 6N − 6` edges for all
`N ≥ 2`, so the sparsity certificate provably never fires in this regime.

> **Implementing (or vendoring) a linear-time planarity test is the single cheapest way to
> make cubic-regime sweeps 10–100× larger.** Until then, budget `0.155 s` per state and
> report coverage as a fraction of the pool, not as an exhaustion.

### 4a. One experiment was attempted and abandoned — recorded so it is not assumed done

A depth-0/1 certificate hunt on the **six γ_N = 1 gateways** was launched twice and produced
**exactly one usable rung** before both runs were lost — and that rung is worth having:

> `aca_117` (`YYYXyyx, YXXXyxx`, the shortest gateway at length 14), depth 0, 1,000 nodes:
> **length-matched AC-trivial control 8/8 = 1.00, target 0/8.**

The sweep was then relaunched at depth 0 for the rest. Full table, 1,000 nodes, 8 target
runs and 8 length-matched AC-trivial control runs each:

| gateway | length | control detection | target | null is |
|---|---|---|---|---|
| `aca_117` | 14 | **8/8 = 1.00** | 0/8 | **informative** |
| `aca_11` | 15 | 0/8 = 0.00 | 0/8 | **uninformative** |
| `aca_121` | 16 | 0/8 = 0.00 | 0/8 | **uninformative** |
| `aca_17` | 17 | 4/8 = 0.50 | 0/8 | weakly informative |
| `aca_30` | 17 | 4/8 = 0.50 | 0/8 | weakly informative |
| `aca_122` | 18 | 0/8 = 0.00 | 0/8 | **uninformative** |

**Read it row by row, never pooled.** Five of the six carry control rates of 0.00 or 0.50,
so their identical `0/8` targets are worth little or nothing — the instrument prints that
warning itself. And with only 8 control runs per row, `8/8` / `0/8` / `0/8` / `4/8` / `4/8` /
`0/8` is not a clean length trend; it is six noisy estimates. Only `aca_117` supports a confident null,
and it supports exactly one: at 1,000 nodes and depth 0, a search that finds a certificate on
every one of eight length-matched AC-trivial controls finds none on the gateway closest to
Lackenby's hypothesis.

The rest of the original sweep was lost to process management rather than to the mathematics:
the
first loop's shell was reaped while its children kept running on stale code, and the second
was killed deliberately to free CPU for the exhaustive rank-12/13 sweep, which had a chance
of settling AK(3) and which the gateway hunt did not. Contributing factor: a `pkill -f`
whose pattern matched the very command issuing it.

So **five of the six gateways have never been hunted at all, and none above depth 0**;
A9's 39,108-state sweep of their classes plus this single calibrated rung is all that
exists. Given they are the presentations *closest* to a Lackenby
certificate anywhere in the 124, that is the most obvious unfinished experiment on this line
and it is cheap — it is item 3 of §5.

### 4b. The entangled-slide census: attempted four times, never completed

`S7` §4 isolated the one thing depth `k ≥ 2` can offer that depth 1 cannot — an AC2 slide by
a conjugate of a relator that already involves **several** fresh generators, which no
Lemma-11 removal can serialize because removal substitutes a definition back and undoes the
entanglement. Measuring whether such slides flip γ_N any better than plain ones would close
the last hole in §1(i). It was attempted four times and **produced no data**. The causes,
recorded because three of them are process lessons rather than mathematics:

1. **Output only at the end.** The first run printed its tally after the loop, so its
   10-minute timeout erased the whole measurement — precisely the failure
   `instrument-the-search-before-reading-its-null.md` was filed about, committed by the
   author of that lesson.
2. **`nohup` runs were reaped.** Two attempts launched with `nohup … &` were killed with the
   shell that spawned them; only harness-tracked background tasks survive here.
3. **The inner loop never checked the clock.** With a per-base loop of 15 `decide()` calls
   and no time check inside it, a single slow decision blocked the outer cap indefinitely.
4. The final, fixed attempt exited without printing for reasons not diagnosed.

**Cost of the diagnosis, which is the part worth keeping:** at rank 4 with these relator
lengths a large fraction of states come back `UNDECIDED` — the cut-scheme solver is out of
scope and the exact census exceeds any reasonable cap — so the census is both slow *and*
sparse in usable pairs. Anyone repeating this should decide with the factorial census under
a tight relator-length cap (≤ 10) and treat `UNDECIDED` rates as a design parameter, not an
afterthought. **The claim in §1(i) is therefore complete for every mechanism except this
one, which remains untested rather than tested-and-null.**

### 5a. An instrument note for the cubic regime

Measured on `C1` (rank 13, 13 relators of length 3): the exact factorial census takes
**0.155 s** (8,192 cases) while `classify_cut_support` — the R1c-v2 fast path that is the
right choice at rank 2 — takes **3.9 s** on the same state. The fast path is fast only when
the link is *small and dense*; in the cubic regime the link is large and sparse and the
brute-force census wins by a factor of 25.

> **Use `gamma_N_factorial_n` in the cubic regime and the cut-scheme solver at low rank.**
> Picking the wrong one costs an order of magnitude, in the direction that makes a sweep
> look infeasible when it is not.

## 6. Standing deliverables

- **Method**: `S12_CERTIFICATE_HUNT.md` + `experiments/stable_ac/fable/s12_hunt.py` (14
  tests) — a sound semi-algorithm for proving stable AC-triviality, with its soundness
  repaired to discharge all three readings of "thickenable", and its move weights set from
  measured flip rates rather than taste.
- **Instruments**: `high_rank_refine.py` (+39 tests), `rank_n_ac_search.py` (+36 tests),
  `u124_thickenability.py`, `spelling_high_rank.py`, `cubic_split_search.py`.
- **Lessons filed**: `stabilization-that-only-rebookkeeps-is-inert.md`,
  `instrument-the-search-before-reading-its-null.md`, and T-S10 inside `S10`.

## 7. If you are a fresh session, start here

1. Read `FRAMING.md` (statements, traps, what does not count), then this file, then
   `S3_SUBDIVISION_INVARIANCE.md` §4–§6 and `S6_MOVE_CLASSIFICATION.md` §1. Those three
   between them tell you which moves can possibly change anything, and will stop you
   re-running the S-line's dead ends.
2. **Do not propose a high-rank mechanism without first stating how many 2-cell germs its
   new edges carry.** Two germs from two distinct 2-cells ⇒ provably inert (S3). If the
   answer is "the same relators, re-spelled", the proposal is already refuted (T-S8).
3. The sharpest open targets are **at rank 2**: the six certified γ_N = 1 gateways of §3a,
   preferentially the ones carrying the Baumslag–Solitar relator `YXXXyxx` (§3b). Closing
   more brackets with the split-based upper bound (§5.5) is the cheapest way to find more.
4. The sharpest open *theory* question is **Q(F2) at k ≥ 2** (`S7` §4). Level 1 is blocked —
   it reduces to the Panteleev–Ushakov conjecture — so do not attack it.
5. Every null on this line is worth exactly its measured detection rate, and every
   `NOT_SPHERICAL` is a statement about **orientable** thickenability only (T-S9). Both of
   those have already cost this project real work; they are not boilerplate.

**Branch discipline reminder.** This branch is `claude/stable-ac-conjecture-stabilization-rwo9as`
and **must be merged into `fable/proof` by the user**; a cloud session cannot push there
itself. No PR was opened (`FRAMING` trap 10). Full suite at the time of writing:
**762 passed, 8 skipped, 0 failed**.

## 3c. Conjecture SR is false — including on the trivial group

R7's Conjecture SR ("free reduction never destroys thickenability") stood on roughly
114,000 confirming complexes, and A8 re-measured it this session as 0 destroys in 997. It is
false. A10's counterexample chain, all three rows balanced presentations of the **trivial
group** (Todd–Coxeter index 1 at every step), re-verified independently by the orchestrator:

| spelling | census | `minimum_defect` | index |
|---|---|---|---|
| `("ABbbabAAaB","baB")` | 86,400 | **0** | 1 |
| `("AbabAAaB","baB")` | 2,880 | **2** | 1 |
| `("AbabAB","baB")` (fully reduced) | 144 | **0** | 1 |

One free-reduction step takes defect 0 to defect 2. **Why ~120,000 measurements missed it:**
SR is an induction step `depth k → k−1`, and every prior corpus was built as "cyclically
reduced base **plus one move**" — i.e. it only ever sampled `k = 1`. The conjecture breaks
at `k = 2`, and no amount of growth at `k = 1` could have found it. Filed as a lesson.

**The caveat that must travel with this.** In all 28 counterexamples the *fully reduced*
form already had defect 0 — no spelling ever beat its own reduction. That is precisely the
case AK(3) needs, and it remains unrefuted. What SR's fall removes is a **proof of
impossibility**; nothing was put in its place. Reading "SR is false" as "the spelling route
is open for AK(3)" is an over-reading — one the orchestrator made once this session, on the
earlier ℤ/4 version of the counterexample, and had to retract.
