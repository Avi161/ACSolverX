# S11 — Spelling space at high rank: **Conjecture SR is false**, and a decision instrument restored in the blind band

Task A10, S-line, branch `claude/stable-ac-conjecture-stabilization-rwo9as`
(**must be merged into `fable/proof` by the user**). Date 2026-08-04.
Owner files: `experiments/stable_ac/fable/spelling_high_rank.py`,
`tests/fable/test_spelling_high_rank.py`, `results/stable_ac/fable/s11_*.json`.
`high_rank_refine.py` and `rank_n_ac_search.py` are **imported, never edited**.

**THREE RESULTS, in order of importance.**

1. **Conjecture SR of `R7_SPELLING_SPACE.md` §3.1 is FALSE** (§4.3). Verified
   counterexample, both sides by exhaustive census, the defect-0 side re-verified by two
   further independent tools. Consequences: R7's `γ*(AK(3)) = 1` and "the entire
   spelling-space route to a thickenable AK(3) is closed" lose their hypothesis; R7's
   Conjecture U falls too if its Theorem S10 is right; R7's retroactive upgrade of ≈17,100
   `NOT_SPHERICAL` verdicts is withdrawn. **The spelling route to AK(3) is reopened** in the
   sense that the argument closing it is gone.
2. **A decision instrument restored in the length band where this line was blind** (§3).
   The exact census decides 95 % of rank-8 states at total length 22 and 57 % at length 25,
   where rank 2 and rank 3 decide **0 %** — with `missed = 0` across a 163-rung certified
   positive ladder, i.e. zero disagreements against an independent witness route.
3. **A correction to the line's own soundness bookkeeping** (§1): the element-tuple
   argument does not transfer a thickenability *hypothesis*, and trap T-S9 has its
   containment backwards — `γ_N = 0` is the *stronger* predicate and discharges Lackenby's
   for free; the orientable gap costs recall, not soundness.

STATUS. §1 is an inference-chain audit — a draft for adversarial audit, not a result.
§§3–5 are **measurements** by exact census, each with its cap, skip count and bias
direction. §4.3's counterexample is a **finite, exhaustively verified fact** and is as
close to a result as this note gets; it still wants an independent audit, and the audit
is cheap because the whole object is two words and two censuses of 144 and 4,320.
§2 records a route closure that belongs to task A8; it is repeated here because it is what
redirected this task mid-flight.

Claims addressed (FRAMING.md taxonomy): everything here is **MACHINERY** plus one
inference-chain audit. **Nothing here claims anything about AK(3)'s AC-triviality or
stable AC-triviality in either direction** — §4.3 removes an argument *against* one
spelling-space route; it does not supply one for it.

---

## 1. FIRST TASK — is the spelling argument sound?

The chain under audit, as handed to this task:

> If ANY spelling of ANY member of AK(3)'s stable class is thickenable, then by Lackenby
> Thm 1.3 that presentation is AC-trivializable, and **AK(3) is stably AC-trivial**.

### 1.1 (i) Does Lackenby's framework admit non-freely-reduced relator words?

**Verdict: yes in §§1–5, on a two-channel relay, and this is the ONLY channel that makes
the chain sound.**

`S2_LITERATURE_HIGH_RANK.md` records the move list as relayed from the source:

> "(0) remove or introduce `xᵢxᵢ⁻¹` or `xᵢ⁻¹xᵢ` in some relation `rⱼ`; (1) replace some
> `rᵢ` by `rᵢ⁻¹`; (2) … (3) …"

Three things follow, and S2 states each of them explicitly:

* relations in §§1–5 are **free-semigroup words**, not free-group elements (§6 switches to
  free-group elements and *drops* move (0), which is why FRAMING trap 7 forbids importing
  §6 statements into §§1–5);
* an unreduced spelling is therefore a **bona fide presentation of the framework**, and is
  joined to its reduction by (0)-moves;
* so if a thickenable unreduced spelling `P′` exists, Thm 1.3 applies **to `P′`**, and the
  (0)-moves carry the conclusion back to `P`.

**Flag, per `experiments/lessons/literature-absent-in-cloud-clones.md`.** `literature/` is
gitignored and this clone holds only `literature/fake_surfaces/`; `ls literature/` was run
in *this* session and confirms it. The move list above is **SOURCE-RELAYED, not read from
source here.** It costs exactly one inference: if the relay is wrong and the framework
requires reduced attaching words, §1.2's fallback does not save the chain, and the whole
spelling route to a *transfer theorem* is void (the existence question it decides is
unaffected — that is machine-checked and owes the literature nothing).

### 1.2 (ii) Is move (0) available in both directions — and does the element-tuple argument rescue the hunt if not?

**Verdict on the direction: both directions, per the same relay** — the verb is "remove or
introduce", so spike INSERTION is a legal move (0), not merely its inverse. Two corrections
to the line's own files fall out:

* `FRAMING.md` §1 glosses move (0) as "free and cyclic reduction (Lackenby's move (0);
  harmless normalization)". Both halves of that gloss are wrong on the relayed text: it is
  free insertion **or** deletion (not a one-way normalization), and it is **free**, not
  cyclic — the cyclic part is this repo's own extension. S2 already flagged this; it is
  repeated here because this task's operating contract depended on it.
* The project's operating move set does include (0) (FRAMING §1, "AC1–AC3 (+(0))"), so a
  trivialization of `P′` that uses (0)-moves is a trivialization in this line's sense.

**Verdict on the fallback: the element-tuple argument does NOT rescue the hunt, and the
brief that proposed it was wrong on this point.** The argument runs "the AC moves act on
elements of the free group, so two spellings of the same tuple are the same presentation
for AC purposes". That is true of the *conclusion* side and false of the *hypothesis*
side. Lackenby Thm 1.3's hypothesis is a property of the presentation **2-complex**, and
the 2-complex of a spelling is a different complex from the 2-complex of its reduction —
that is the entire content of `R1F_REDUCTION_AND_SPIKES.md`. If unreduced words are out of
the framework's scope, a thickenable spelling never enters the theorem at all and there is
nothing for the element-tuple identification to transfer. This is exactly **Joint A** of
`LITERATURE_STATUS.md` §4 ("the hypothesis side; THIS IS THE RISK"), whose Joint B ("the
conclusion side; probably safe") is the element-tuple argument — it is the *other* joint,
and it was never the one at risk.

The only fallback that would work is a theorem *"γ_N(spelling) = 0 ⇒ γ_N(reduction) = 0"*,
which is R7's **Conjecture SR** — **open**. So:

> **Justification in force for any spelling-space hit on this line: the framework-scope
> channel (§1.1), source-relayed and flagged. Not the element-tuple argument.**

### 1.3 (iii) Trap T-S9 and the Joint-A gap — the direction is backwards in `S3_SUBDIVISION_INVARIANCE.md`

S3 repair R3 and trap T-S9 say:

> "a `γ_N = 0` hit discharges the *orientable* hypothesis, whereas Lackenby Thm 1.3's
> hypothesis is the weaker 'some 3-manifold'. Whether the first discharges the second is
> the open **Joint-A** question."

**Two corrections.**

1. **The implication is free, not open.** The repo's bridge is `γ_N = 0 ⟺ K` embeds in an
   *orientable* PL 3-manifold (`R1E` Theorem D, AUDITED; Neuwirth's own framing is *closed
   orientable*). An orientable 3-manifold **is** a 3-manifold. So the repo's predicate is
   strictly **stronger** than Lackenby's hypothesis and a `γ_N = 0` hit discharges it
   immediately. The standing lesson
   `experiments/lessons/parallel-runs-and-bound-direction.md` is the relevant one: this is
   a containment read in the wrong direction, and it is the third recurrence of that
   failure family on this line.
2. **What the orientable/general gap actually costs is RECALL, not soundness.** A state
   that embeds in a non-orientable 3-manifold but no orientable one has `γ_N > 0` and is
   invisible to every instrument in this repo, while still satisfying Lackenby's
   hypothesis. So `γ_N > 0` is **not** "not thickenable in Lackenby's sense", and no
   census null on this line may be read as one. Call this **[GAP-O]**, matching
   `S6_MOVE_CLASSIFICATION.md` §0.1, which states it correctly.
3. **The real Joint-A gap is §1.1's**, and it must be flagged on every payoff claim:
   *does an unreduced spelling lie in the theorem's scope?* Two channels say yes; no
   source read in this clone says so.

**Corrected reporting rule for this line.** A defect-0 census on a spelling is to be
reported as *"a thickenable spelling exists in this class"*, and the step to
*"…is stably AC-trivial"* must carry: (a) the Joint-A scope flag of §1.1, and (b) the
`[UNVERIFIED]` flag on Thm 1.3 itself (`FRAMING.md` §5). It is **not** gated on
orientability.

---

## 2. Route closure — the spike hunt on reduced bases cannot win (task A8's measurement)

Task A8 (`S6_MOVE_CLASSIFICATION.md` §1) measured, by exact census, what move (0) does:

| direction | measured |
|---|---|
| free/cyclic reduction **creates** `γ_N = 0` | **315 of 2,510** non-thickenable spellings |
| free/cyclic reduction **destroys** `γ_N = 0` | **0 of 997** thickenable spellings |

Read contrapositively, spike insertion **never created** thickenability in any of 997
trials, and R7's own corpus adds ≈114,000 complexes with the same verdict (R1F tier-1
cross-tabulation: base `γ_N = 1` → min over its spikes = 1 in 2,514 of 2,514 bases; base
`γ_N = 2` → min = 1 or 2, never 0). Therefore:

> **The reduced spelling of a state is, empirically, always at least as good a certificate
> candidate as any spelling of it.** A hunt that adds spikes to a *cyclically reduced*
> base — AK(3) is cyclically reduced, and so is every chord refinement of it, since
> `high_rank_refine._check_input` refuses anything else — is searching a region that
> cannot beat the base it started from.

**This retires the spike-insertion hunt on AK(3) for the positive direction**, together
with the depth-2/3 exhaustive census at rank 9 that this task was scoped to run. (§6 shows
that census would not have been affordable anyway, for a second and independent reason.)

Two honest qualifications, both of which keep the route from being *proved* closed:

* **This is a measurement, not a theorem.** Conjecture SR is open. R7's Corollary S5 (the
  spike ceiling, `γ_N(spike(P)) ≥ γ_N(P) − 1`) is a *proof*, and it only rules out
  spike-depth ≤ 1 for a base at `γ_N = 2`. Depth ≥ 2 is unrefuted by any theorem.
* **The S3_AUDIT §3.2 lead is not a counterexample to it, and the brief that sent this task
  chasing it over-read the rows.** Those five `defect 2 → 0` rows have bases that were
  already NOT cyclically reduced (`('XYYyxY','XyX')` and friends). What moved the defect
  was the free reduction *at the end* of the pipeline, i.e. the creating direction of move
  (0) — the same direction A8 measured at 315/2,510. It is not a mechanism that beats a
  reduced base. Reproduced here as a regression fixture
  (`test_peel_and_reduce_reproduces_the_S3_AUDIT_row`), with the full row
  `('XYYyxY','XyX')` d=2 → `('axYXY','XyX','aYy')` d=2 → `('axYXY','XyX','a')` d=**0**.

**One structural fact worth keeping from the wreck.** The §3.2 mechanism, once the free
reduction is done, is *exactly* `AC4` followed by `AC2`:
`P → (r_1, …, r_j·z, …, r_n, z)` at rank `n+1` — the definition relator `z(a_1a_1^{-1})^{-1}`
reduces to the single letter `z`, and the residual `z a_3…a_m` is the same **cyclic** word
as `a_3…a_m z`. So its legality never needed the spelling framework at all. Pinned in
`test_degenerate_peel_equals_stabilize_and_graft_as_a_cyclic_word`, and it is the same
move as `S6`'s row **M4′**, which is proved (T4′) to be a *subdivision* on the first slide —
hence inert. Any use of it as a mechanism must therefore be at the second slide or later,
where `z` has three or more germs and T4′ no longer applies.

---

## 3. THE DELIVERABLE — where the exact census can and cannot decide, by (length, rank)

### 3.1 Why this is the right instrument to calibrate

`experiments/lessons/calibrate-one-sided-hunts-on-a-positive-ladder.md` is the standing
constraint: the project's earlier spelling hunt used a randomised defect-0 climber whose
**measured** detection fell from 100 % at total length 16 to 0 % at 21, retiring 1,312 of
1,909 swept states as uninformative (R7b). The blind band is total length ≈ 19–27, which is
precisely where AK(3)'s stable class lives (S10 §5: the AK(3)+z rank-3 harvest has mode
22–24).

The instrument calibrated here is a **different** one: the exact census
`gamma_N_factorial_n`, which never guesses. On any state it returns either an *equality*
for `γ_N` or `UNKNOWN_SIZE`, and it returns the latter exactly when
`∏_g (deg(g⁺) − 1)! > cap`. So on a state that really is thickenable,

> **detection ⟺ the compatible family fits inside the cap** — a function of the DEGREE
> PROFILE alone.

And the degree profile is what rank controls: at fixed total length `ℓ` and rank `n`, the
average germ degree is `ℓ/n`. That is the mechanism, and §3.2 measures it.

Cap used throughout: **200,000 rotation systems** (≈ 1 s per state; the user asked for
modest node budgets). Every state above the cap is recorded `SKIPPED`, never given a
verdict.

### 3.2 Decidability by (length, rank) — the bias-free estimator

`results/stable_ac/fable/s11_decidability.json`. Sampling: independent AC1–AC3 walks out of
the standard presentation `⟨x_1..x_n | x_1,…,x_n⟩` (the S10 design), so **every state is
AC-trivial and presents the trivial group by construction**; 60 states per cell, band
half-width 1, no `γ_N` filter at all — hence no selection by any climber and no
circularity with the instrument under test.

**Fraction of states the census decides at cap 2·10⁵** (n = 60 per cell):

| total length | rank 2 | rank 3 | rank 4 | rank 6 | rank 8 |
|---|---|---|---|---|---|
| 13 | 0.62 | 1.00 | 1.00 | 1.00 | 1.00 |
| 16 | **0.00** | 0.35 | 0.93 | 1.00 | 1.00 |
| 19 | 0.00 | **0.00** | 0.17 | 0.97 | 1.00 |
| 22 | 0.00 | 0.00 | **0.00** | 0.52 | 0.95 |
| 25 | 0.00 | 0.00 | 0.00 | 0.03 | **0.57** |

**Median census size — the same table in the units that explain it:**

| total length | rank 2 | rank 3 | rank 4 | rank 6 | rank 8 |
|---|---|---|---|---|---|
| 13 | 1.2·10⁵ | 2.9·10³ | 288 | 12 | 4 |
| 16 | 2.0·10⁸ | 5.2·10⁵ | 1.7·10⁴ | 144 | 24 |
| 19 | 2.9·10¹⁰ | 5.8·10⁷ | 1.5·10⁶ | 8.6·10³ | 192 |
| 22 | 1.3·10¹³ | 3.7·10¹⁰ | 1.2·10⁸ | 1.7·10⁵ | 5.8·10³ |
| 25 | 2.3·10¹⁶ | 1.1·10¹³ | 3.7·10¹⁰ | 1.7·10⁷ | 1.4·10⁵ |

At total length 22 the median rank-2 state costs **2.3 billion times** more to decide than
the median rank-8 state of the same length. The claim under test — *detection collapses
with length at rank 2 and does not collapse at rank 6–8* — **holds**, with the collapse
edge moving from length 13→16 at rank 2 to length 22→25 at rank 8.

### 3.3 The positive ladder — direct confirmation on states KNOWN to be thickenable

§3.2 is an argument plus a degree measurement. This is the direct version demanded by the
lesson: presentations that ARE thickenable, with the fact hidden from the instrument, run
through the identical decide step.

**Certification is independent of the census.** Every rung carries a defect-0 rotation
system found by `rank_n_ac_search.hunt_defect` (bounds `γ_N` from ABOVE, so a defect-0
return is a *complete positive certificate*) and re-verified by
`witness_check_n.check_witness_n`, which rebuilds `D, A, B` from the words and shares no
scheme code with the hunter. `verify_defect_zero` is called with `census_cap = 0` so the
census plays **no part** in building the ladder.

Rank-2 seeds are the 15 rungs of the earlier session's ladder
(`results/stable_ac/fable/witness_sensitivity.json`, total lengths 7–22, certified
census+witness, the top rungs at 2,000,000 evaluations); every column is then grown by
spikes whose children are re-certified by the same witness route.

`results/stable_ac/fable/s11_ladder.json` — **163 certified rungs**, 246 s, cap 2·10⁵.

**Detection rate = (rungs returned defect 0) / (rungs in the cell)**, with `SKIPPED`
counted as a non-detection:

| total length | rank 2 | rank 4 | rank 6 | rank 8 |
|---|---|---|---|---|
| 13 | 0.90 (9/10) | 1.00 (10/10) | 1.00 (10/10) | 1.00 (10/10) |
| 16 | **0.00** (0/10) | 0.90 (9/10) | 1.00 (10/10) | 1.00 (10/10) |
| 19 | 0.00 (0/10) | 0.30 (3/10) | 1.00 (10/10) | 1.00 (10/10) |
| 22 | 0.00 (0/2) † | 0.00 (0/1) † | 0.30 (3/10) | 1.00 (10/10) |
| 25 | — ‡ | — ‡ | 0.00 (0/10) | **0.40** (4/10) |

Median census in the same cells: `3.0·10⁴ / 288 / 24 / 4` at length 13, rising to
`1.4·10¹³ / 1.2·10⁷ / 1.0·10⁶ / 1.9·10³` at length 22.

† **thin cells, and the thinness is itself the R7b finding.** The ladder could not be
grown to 10 rungs at (22, rank 2) or (22, rank 4): the certifying climber is the same
instrument R7b measured at 0–10 % detection above total length 20, so the ladder stalls
exactly where the earlier one did. Those two cells are reported at their true `n`.
‡ **no rungs at all** at (25, rank 2) and (25, rank 4) — the ladder itself cannot be
extended there at this budget, so by the standing rule *no* hunt at ≤ this budget in those
cells can support any conclusion. Recorded as a gap, not as a rate.

**The cross-check that matters, and it is clean: `missed = 0` in every cell.** Not one
rung that the census decided came back with `defect > 0`. So across 163 states, two
structurally independent instruments — a randomised climber whose witness is re-verified
by `check_witness_n` (which rebuilds `D, A, B` from the words), and the exhaustive census —
never disagreed. Every cell's shortfall from 1.00 is *entirely* `SKIPPED`, i.e.
affordability, exactly as §3.1 predicts for an exact method.

**Result.** The claim under test holds on certified positives as well as on the
unconditional sample: the collapse edge sits between length 13 and 16 at rank 2, and
between 22 and 25 at rank 8.

**Bias directions, recorded (both push the same way).**

1. The census bounds `γ_N` by **equality** inside the cap and says nothing above it — a
   `SKIPPED` is counted here as a non-detection, which is the honest reading of an
   instrument that returned silence.
2. The ladder bounds sensitivity from **ABOVE**: rungs are by construction states some
   climber could certify, so real states at the same (length, rank) can only be harder. A
   **low** cell is conclusive (the null it licenses is vacuous); a **high** cell is
   optimistic and is never a licence to read a null as absence.
3. No p-values. Rungs come from a spike/move tree and are not independent draws
   (`experiments/lessons/contrast-length-confound.md`).

---

## 4. The one spelling question still pointed the right way — a hunt for a counterexample to Conjecture SR

If reduction can **destroy** thickenability, R7's Conjecture SR is false, `γ*` is not
computable from the reduced spelling, and the entire spelling route reopens — including
for AK(3). That is the only direction in spelling space that the A8 measurement has *not*
foreclosed, so the remaining budget went there.

Shape of a counterexample: a spelling `K` with `γ_N(K) = 0` whose free/cyclic reduction
has `γ_N > 0`. Both sides decided by exact census inside the cap; a pair where either side
skips is counted and discarded, never converted into a verdict. Bases are AC1–AC3 walks out
of the standard presentation, so every one is AC-trivial and presents the trivial group;
only the **non-thickenable** bases can host a counterexample, and the spikes are piled on
those.

### 4.1 The rank-2 attempt, and why it is nearly vacuous — a live demonstration of §3

`results/stable_ac/fable/s11_sr_hunt_rank2.json`. Ranks 2–4 requested, base length ≤ 12,
spike depth 2, 210 s, cap 2·10⁵:

| | |
|---|---|
| spellings decided | **960** |
| spellings **skipped** (census over cap) | **7,849** — 89 % |
| counterexamples | **0** |
| ranks actually reached | rank 2 only (27 bases, 13 of them non-thickenable); the whole budget went on rank 2 |

Nine spellings in ten were *not decided*. This is §3's table happening in real time: a
length-12 rank-2 base plus two spikes is a length-16 rank-2 complex, and §3.2 measures
rank-2 length-16 decidability at **0.00**. The run is reported because it is the cleanest
demonstration on this line of what the blind band costs — not because its null is worth
much.

### 4.2 The same hunt at rank 4–8, where the instrument works

`results/stable_ac/fable/s11_sr_hunt.json`. Ranks 4, 6, 8; base length ≤ 17; spike depth 2;
225 s split evenly across the three ranks; cap 2·10⁵.

| | rank-2 run (§4.1) | rank 4–8 run |
|---|---|---|
| wall clock | 210 s | 225 s |
| spellings **decided** | 960 | **8,565** |
| spellings skipped over cap | 7,849 (**89 %**) | 204 (**2.4 %**) |
| counterexamples to SR | 0 | **0** |
| non-thickenable bases reached | 13 (rank 2 only) | 5 (3 at rank 4, 1 at rank 6, 1 at rank 8) |

**8.9× the spellings decided, at a 37× lower skip rate, in the same wall clock** — the
§3 table cashed out on a real experiment rather than a sample.

**What the null is worth, stated with its limits.** This is a *two-sided* instrument, not
a one-sided one: every one of the 8,565 rows is an exact `γ_N`, so the lesson about
one-sided silence does not apply and no detection-rate discount is needed. What *does*
limit it:

* only **5 distinct non-thickenable bases** were reached, because at rank 4–8 most
  AC1–AC3 walk states are *already* thickenable (exactly S10's density result), and only a
  non-thickenable reduction can host a counterexample. The 8,565 spellings are the spike
  tree over those 5 bases and are **not independent draws**
  (`experiments/lessons/contrast-length-confound.md`) — no p-value is quoted, and the
  correct summary is "5 bases, exhaustively spiked to depth 2, no counterexample";
* it is nonetheless the **first test of Conjecture SR above rank 3**. R7's ≈114,000
  complexes and A8's 997 are rank 2 (A8 reaching rank 3). Every previous SR datum lives in
  the one regime where the census is cheapest and the germ degrees highest; these 8,565
  live in the opposite corner.

**Verdict on this run: no counterexample, in a rank regime SR had never been tested in.**
But that is not where the counterexample was — see §4.3.

### 4.3 **CONJECTURE SR IS FALSE.** A verified counterexample, and what it does and does not break

Every SR test ever run on this line — R1F's 110,917 complexes, R7's 5,241, A8's 997 —
takes a **cyclically reduced** base and applies **one** spike. That tests the induction step
`depth 1 → depth 0` and nothing else. The Corollary SR is *wanted* for
(`γ*(P) = 0 ⟺ γ_N(P_red) = 0`, hence `γ*(AK(3)) = 1` and the closure of the spelling route)
iterates SR at **every** depth. So the step to attack is `depth 2 → depth 1`. It breaks
immediately.

> **Counterexample.** With `P = ("XYYyxY", "XyX")` and the spike `u = "Y"` at position 0 of
> the first relator,
>
> | | census | min defect | `γ_N` |
> |---|---|---|---|
> | `P = ("XYYyxY","XyX")` | 144 | **2** | 1 |
> | `spike(P) = ("YyXYYyxY","XyX")` | 4,320 | **0** | **0** |
>
> Both censuses are **exhaustive** — no cap was hit and nothing was sampled. So
> `γ_N(spike(P)) = 0` while `γ_N(P) = 1`, and **`γ_N(spike(P)) = 0 ⇒ γ_N(P) = 0` is false.**

**Verification, on both sides, by tools that do not share code.**

* `spike(P)`'s defect 0: exact census (4,320 systems, 2 accepting); `check_witness_n`
  accepts the witness outright (`defect 0`, `L = 1`, `|C|−|A|+|AC| = 4−11+9 = 2`,
  `⟨AC,BC⟩` transitive, compatible); and `rank_n_ac_search.independent_defect`, which
  rebuilds the dart dictionary from the words, returns `defect 0`.
* `P`'s defect 2: exact census over all 144 systems here — **and independently, `P` is
  literally row 1 of `S3_AUDIT.md` §3.2**, where a different agent's from-scratch census
  (`audit_s3/mygamma.py`) recorded `('XYYyxY','XyX') d=2`. Two implementations, two
  sessions, same number.
* Not a degenerate case: `L = 1` on both, both relators of length ≥ 3, both using both
  generators — R1F's **strict stratum**.

**What is broken.**

1. **Conjecture SR (R7 §3.1) is refuted.** It must be struck from R7 and from anything
   downstream of it.
2. **R7's "Corollary (conditional on SR)" loses its hypothesis.** The claims
   *"`γ*(AK(3)) = 1` exactly"*, *"no spelling of AK(3) is thickenable"* and *"the entire
   spelling-space route to a thickenable AK(3) is closed"* were derived from SR. They are
   now **unsupported** — not disproved, but no longer proved. **The spelling route to
   AK(3) is reopened**, in the exact sense that the argument which closed it is gone.
3. **Conjecture U (unnesting) falls with it** — *if* R7's Theorem S10 (`U ⇒ SR`) is correct
   as stated. Contrapositive: `¬SR ⇒ ¬U`. S10 was **not** re-derived here, so this is
   reported as a consequence to check, not as an established refutation.
4. **R7's "retroactive strengthening" is withdrawn.** The ≈17,100 `NOT_SPHERICAL` verdicts
   in this project's corpus were to be upgraded from single-realization statements to
   whole-spelling-family statements *under SR*. That upgrade is no longer available.

**What is NOT broken, and this is the important half.**

* **The Corollary's *conclusion* survives on this example.** The other one-step reduction
  of `spike(P)` — deleting the interior `Yy` instead of the leading one — is
  `("YyXYxY","XyX")` with defect **0**, and the full reduction `("XYxY","XyX")` also has
  defect **0**. So `γ*` and `γ_N(P_red)` still agree here.
* **The natural repair is the EXISTENTIAL form.** Call it

  > **SR′.** `γ_N(K) = 0 ⇒ SOME one-step reduction `K → K′` has `γ_N(K′) = 0`.

  SR′ still yields the Corollary by induction (each step takes the good reduction), and it
  held in **every** counterexample found here. It is unproved and is now the right target.
* **A8's "0 destroy of 997" is not contradicted.** Their reduction step is free *and
  cyclic* reduction, i.e. reduction to the reduced form, and full reduction of `spike(P)`
  lands on `("XYxY","XyX")` with defect 0. The correct reconciliation: *full reduction*
  never destroyed `γ_N = 0` in 997 trials, while a *single spike deletion* demonstrably
  can. That distinction was invisible while every base tested was reduced, and it is
  exactly the distinction SR trades on.

**How common is it?**

`results/stable_ac/fable/s11_sr_spelled.json`, 200 s, cap 2·10⁵. Bases: cyclically
reduced rank-2 pairs of total length ≤ 8, both relators using both generators; for each,
every depth-1 spike with **positive** defect, then every depth-2 spike of those.

| | |
|---|---|
| reduced bases reached | **5** (the run is deep, not wide — one base is ~40 s) |
| depth-1 spellings with `γ_N > 0` | 64 |
| depth-2 spellings decided | **1,856** |
| depth-2 skipped over cap | **0** — every single one decided exactly |
| **counterexamples** | **16**, over **8 distinct** depth-1 `P` |
| shortest counterexample in this run | total length 12 |
| shortest counterexample known | **total length 11** — the pinned `("YyXYYyxY","XyX")` |
| existential repair SR′ survives | **16 of 16** |
| counterexamples whose reduced base presents the trivial group | 0 in this sample |

So it is **not a freak**: ~0.9 % of decided depth-2 spellings over these bases break SR,
and the search found the first one in under a second. It was invisible for ≈120,000
measurements purely because every one of those measurements started from a reduced base.

**The one thing still worth hunting**, and it is now sharply defined: a counterexample
where **SR′ also fails** — a thickenable spelling *none* of whose one-step reductions is
thickenable. That, and not this, would break the Corollary itself and put `γ*(AK(3)) = 0`
genuinely back on the table. 0 of 16 here; the next session should widen this hunt (more
bases, spike depth 3) rather than deepen it. A second target, cheaper and equally
pointed: a counterexample whose reduced base presents the **trivial group**, since only
those can bear on Lackenby's hypothesis at all.

---

## 5. How much of the previously-blind band was bought back

### 5.1 The honest accounting, and it has a hard negative in it

The band R7b retired: **1,312 of 1,909 swept states**, the graft images of AK(3)'s eight
gateway spikes, total length 21–24, run at a budget with a *measured* 0 % detection above
length 20.

**Those 1,312 states are NOT bought back, and the reason is a theorem this line already
owns.** They are rank-2 and rank-3 states. The obvious move — refine them to rank 8 or 9
so the census becomes affordable — **does not work**, because a share-free chord
refinement gives every fresh germ degree exactly 2, `(2−1)! = 1`, and leaves the degrees of
the original generators untouched: the compatible census size is a **triangulation
invariant** (`high_rank_refine` structural fact 1; Lemma S3′, measured at 1,525/1,525
bit-identical histograms). Pinned as a regression test here
(`test_rank_lowers_the_census_at_fixed_total_length`): the rank-9 refinement of AK(3) has
census 86,400 and minimum defect 4 — the *same numbers* as AK(3) itself.

> **High rank does not make a low-rank state cheap. It makes a genuinely high-rank state
> cheap.** Raising the rank by abbreviation buys nothing (S3); raising it by moves that
> spread the letters over many generators with low multiplicity buys everything.

### 5.2 What IS bought back

At fixed total length, the census is affordable exactly when the average germ degree
`ℓ/n` is small. Reading the two tables of §3 together gives the rule of thumb

> **decidable at cap 2·10⁵ ⟺ `ℓ/n ≲ 3`**

— length 22 at rank 8 is `ℓ/n = 2.75` and 95 % decidable; length 25 at rank 8 is `3.1` and
57 %; length 19 at rank 4 is `4.75` and 17 %. That is precisely the **cubic regime** S3 §4
identified on theoretical grounds ("every generator occurring exactly 3 times … the whole
compatible census is ≤ 2^{2N} — cheap and exhaustive at rank 9 and well beyond") — now with
a measured boundary rather than an asymptotic.

So the band bought back, stated as a region rather than a length:

| region | rank-2/3 instrument | this instrument |
|---|---|---|
| total length 19, `ℓ/n ≤ 3` (rank ≥ 7) | 0 % decidable; climber 20–40 % | **100 %**, exact |
| total length 22, `ℓ/n ≤ 3` (rank ≥ 8) | 0 % decidable; climber 0–10 % at 40k–120k | **95 %**, exact |
| total length 25, `ℓ/n ≈ 3` (rank 8) | 0 %; climber ladder STALLED at 23–24 | **57 %**, exact |
| total length 19–25 at rank 2–4 | 0 % | **0 %** — unchanged |

The instrumental gain is real and it is large — the exact census decides, at length 22–25,
states that no instrument on this line could previously decide *at all*, and it decides
them with an equality rather than a one-sided bound, with **zero** disagreements against
the independent witness route across 163 certified positives. But it is only available
where the state is *natively* high rank, which is the regime `rank_n_ac_search`'s
stabilize-and-slide search produces and the regime a refinement of AK(3) does **not**.

### 5.3 What this means for the S-line's plan

S10 §6 proposed "stabilize to rank 5–6, slide, test, with the detection rate measured on
an AC-trivial positive ladder at the same rank and length". §3.3 **is** that measurement,
extended to rank 8, and it says the test half of that plan is sound: at rank 6–8 and
length ≤ 22 the tester is exact and essentially never abstains. The binding constraint on
that programme is therefore **not** the thickenability decision any more; it is whether the
slide search can reach `ℓ/n ≲ 3` states of AK(3)'s stable class at all.

---

## 6. The one AK(3) experiment that is still exactly at the frontier, sized but not run

Recorded so a future session does not have to re-derive the cost.

R7's **Corollary S5** (the spike ceiling, `γ_N(spike(P)) ≥ γ_N(P) − 1`) is a *proof*, and
with `γ_N(AK(3)) = 2` it forces every thickenable spelling of AK(3) to sit at **spike-depth
≥ 2** (Corollary S6). Depth 1 is exhaustively decided (R1F: histogram `{1: 8, 2: 31}`).
Depth 2 is closed only by the *conjecture* SR and by A8's 997 measurements, not by any
theorem. So a **complete exact census of AK(3)'s depth-2 spelling space** is the single
sharpest open computation in this corner: a hit settles AK(3) and refutes SR; a clean sweep
is the strongest possible confirmation of SR at the one place it matters.

**It is not affordable, and the reason is §5.1.** AK(3)'s census is 86,400 and every chord
refinement of it has *the same* 86,400 (Lemma S3′). A depth-2 spike raises two germ degrees
by one each on each of two spikes, so a typical depth-2 spelling costs ≈ 3.5·10⁵ rotation
systems, and there are ≈ 2.5·10⁵ distinct depth-2 spellings at rank 9 — about **10¹¹
rotation systems**, or ~three weeks of the single-thread rate measured here
(1.8·10⁵ systems/s at rank 2, ~5·10⁴/s at rank 9). Refining to rank 9 does not help; only a
transform that genuinely lowers `deg(x⁺) = 6` and `deg(y⁺) = 7` would.

**The one transform that does that is generator SPLITTING** (`high_rank_refine.split_generator`),
which is a vertex split rather than a subdivision and so is *not* covered by Theorem S3 —
splitting `x` and `y` three ways each would take the census from 86,400 to ~4·10¹ and make
depth-2, even depth-3, exhaustive. That is `high_rank_gamma_sweep.py`'s territory (another
agent owns it) and is flagged here rather than duplicated. Caveat before anyone runs it:
splitting produces **length-2 relators**, which trip the fail-closed gate of the fast
solver (`neuwirth_rank_n.py` `MIN_RELATOR_LENGTH`); only `gamma_N_factorial_n` stays valid.

## 7. Traps this note adds

* **T-S11a.** The **element-tuple argument does not transfer a thickenability hypothesis.**
  "The AC moves act on free-group elements, so all spellings are one presentation" is
  Joint B (the conclusion side, safe). Joint A (the hypothesis side) needs the spelling to
  be a presentation *of the framework*; nothing about free-group elements supplies that.
* **T-S11b.** **T-S9 has the containment backwards.** `γ_N = 0` (orientable, indeed closed
  orientable) is STRONGER than Lackenby's "some 3-manifold", so a hit discharges his
  hypothesis for free. The orientable/general gap costs **recall**: `γ_N > 0` does not mean
  "not thickenable in Lackenby's sense", and no census null on this line may be read as
  one. Flag the real Joint A — the unreduced-spelling scope question — instead.
* **T-S11c.** **Never quote a detection rate without its cap and its skip count.** For an
  exact census, "detection" and "affordability" are the same event, so a detection table
  is a degree-profile table in disguise; quoting it as a property of the *search* would
  hide that the fix is to change the cell structure, not the budget.
* **T-S11d.** `high_rank_refine._check_input` and `certify_refinement` both **refuse
  non-cyclically-reduced input**. Any future spelling × high-rank pipeline must therefore
  refine first and spike second (spike-then-refine raises `RefinementError`), or bring its
  own refiner — which then does not carry the audited replay certificate.
* **T-S11e — the one worth promoting to `experiments/lessons/`.**
  **Conjecture SR is FALSE; never cite it, and re-check anything conditional on it.**
  More useful than the fact is *why ~120,000 measurements missed it*: SR is an induction
  step `depth k → depth k−1`, and every corpus that "confirmed" it generated its states by
  applying **one** operation to a **normal-form** base — so it only ever measured `k = 1`.
  The counterexample lives at `k = 2` and was reachable in under a second once the base was
  allowed to be non-normal.

  > **Rule.** When the conjecture you are testing is an induction step, your generator must
  > sample the step at depth ≥ 2. A corpus built by "normal form + one move" cannot
  > falsify "every move step behaves", however large it is — its size is measuring the
  > wrong dimension.

  Corollary for reading this repo: any claim of the form "0 counterexamples in N complexes"
  should be read together with *how the N were generated*, and specifically whether the
  generator can produce the shape a counterexample would have.
* **T-S11f.** A `γ_N = 0` calibration state need not present the trivial group — R1F's own
  fixture `("xyXY","xxy")` presents **ℤ** (relators `[x,y]` and `x²y`), and
  `witness_check_n.check_witness_n` correctly raises `AuditContradiction` on its witness
  because `verify_defect_zero` hardcodes `trivial_group=True`. That refusal is a *feature*
  and must not be silenced. Any state promoted from "thickenable" to "Lackenby
  certificate" needs `todd_coxeter_check` as a separate step.
