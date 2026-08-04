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

**T-S17 — and it cuts against the cubic route's own premise.** Proximity to cubic form is
**anti-correlated** with low defect:

| Σ\|δ\| from cubic | decided | γ_N = 1 | γ_N = 2 | γ_N = 3 |
|---|---|---|---|---|
| 2 (one SPLIT away) | 1,232 | **0** | 1,028 | 204 |
| 4 (two SPLITs away) | 43,879 | **527** | 39,072 | 4,280 |

The states *closest* to cubic form contain **no** γ_N = 1 members at all. The normal-form
target and the thickenability target point in opposite directions in this region, so
"drive toward cubic form" is not a good proxy for "drive toward a certificate".

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
5. **Close the remaining γ_N brackets with splitting** (task A13, in flight). S8's
   monotonicity, read forwards, is a *tool*: a witness found for a **split** of `P` is a
   valid **upper** bound for `P` itself, and splitting shrinks the census `∏(deg−1)!` — so
   it buys back exactly the long-length regime where A9's direct witness sampler is blind
   (detection 1.00 at L13 falling to 0.00 at L19, with 87 of 124 rows carrying an
   uninformative upper bound). This is the one place the S-line's negative result becomes a
   positive instrument, and it is the cheapest way to find more gateways.
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
