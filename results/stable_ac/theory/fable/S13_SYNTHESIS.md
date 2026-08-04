# S13 — What arbitrary stabilization buys: the S-line's answer

Branch `claude/stable-ac-conjecture-stabilization-rwo9as`. **This branch must be merged into
`fable/proof` by the user** — a cloud session can only push to its own `claude/*` branch, so
nothing here reaches `fable/proof` on its own. No PR opened (`FRAMING` trap 10).

Session brief: does the stable AC conjecture get easier for hard presentations — AK(3), the
124 unsolved Miller–Schupp AC-classes — once the rank is allowed to grow well past 3, say to
9 or 10 generators? Use change of variables and Lemma 11. Is there a simple general method?

## 1. The answer, in one paragraph

**No — not by any mechanism, and not by any population effect this session could measure.**
Every way of using extra generators that we could isolate is either provably inert or
measurably counterproductive: abbreviation is a *subdivision* of the presentation complex,
splitting is *monotone*, change of variables is entirely a *depth-1* phenomenon, and
stabilization itself plus the first slide over a fresh stabilizer are inert. The one
measurement that looked positive — certificates getting commoner with rank — turned out
under adversarial audit to be measuring **relator length**, not rank. What is real is much
narrower and worth keeping: *short relators are cheap to decide and long ones are not*, and
raising the rank is one way to buy short relators — but it buys them **by re-spelling, which
provably does not change the answer**.

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
| **S8** | Generator splitting never decreases γ_N (`link(P)` is a **minor** of `link(P′)`) | conjecture + proof sketch + machine certificate; 632 states, none below base |

## 3. What was measured

- **Triangulation is inert**: 1,525 + 480 triangulations, defect histograms bit-identical.
  AK(3) is `minimum_defect` 4 (γ_N = 2) at rank 2 **and** at rank 9, with the same census
  size 86,400 — a peel never changes an original germ's degree.
- **Splitting is monotone**: 632 states at ranks 4 and 6, none below base.
- **Move flip rates** (exact censuses, A8): AC2 destroys 425 / creates 73 of 1,863 — the
  only slide measured to create the certificate; move (0) creates 315 / destroys 0 of 2,510;
  **bare AC3 destroys 315 / creates 0 of 3,507**, and destroys on 16.3 % of trivial-group
  bases. AC1, rotation, AC4/AC5 and T4′ slides: 0 flips in 2,236 + 4,472 + 1,118 + 3,332.
- **Depth ladder, length-matched** (A7): an AC-trivial control returns **39/40** hits across
  rank ceilings 2–6; **AK(3) returns 0/40** on the same rungs, seeds, move set and budget.
- **Depth costs detection at fixed budget** (this line's `--target` mode): control detection
  6/6 at depth 0 falls to 2/6 at depth 1 — precisely T4′'s prediction, since budget spent on
  the inert first slide cannot move γ_N.
- **The cubic regime is rich** (A6, exhaustive): of the 43,008 non-degenerate cubic
  triangular presentations of the trivial group at rank 4, **27,648 (64.29 %) are
  thickenable**. No cubic form for AK(3) was found; that null is 48 correlated attempts at a
  measured 33 % detection rate, i.e. suggestive at best.
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

(`aca_117` re-verified independently by the orchestrator: exhaustive census over 518,400
rotations gives `minimum_defect` 2, and Todd–Coxeter gives index 1. AK(3) reproduces at
defect 4, index 1.)

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

## 6. Standing deliverables

- **Method**: `S12_CERTIFICATE_HUNT.md` + `experiments/stable_ac/fable/s12_hunt.py` (14
  tests) — a sound semi-algorithm for proving stable AC-triviality, with its soundness
  repaired to discharge all three readings of "thickenable", and its move weights set from
  measured flip rates rather than taste.
- **Instruments**: `high_rank_refine.py` (+39 tests), `rank_n_ac_search.py` (+36 tests),
  `u124_thickenability.py`, `spelling_high_rank.py`, `cubic_split_search.py`.
- **Lessons filed**: `stabilization-that-only-rebookkeeps-is-inert.md`,
  `instrument-the-search-before-reading-its-null.md`, and T-S10 inside `S10`.
