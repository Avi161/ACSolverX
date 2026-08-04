# S10 / S12 / S7 — adversarial audit of the session's three POSITIVE claims

Auditor: independent adversarial agent, 2026-08-04. Branch
`claude/stable-ac-conjecture-stabilization-rwo9as` (**must be merged into `fable/proof` by
the user**). Targets: `S10_RANK_DENSITY.md`, `S12_CERTIFICATE_HUNT.md` §2/§4,
`S7_STABILIZATION_DEPTH.md` §5.

**Nothing in the target files was edited and nothing was committed.** All instruments were
written from scratch for this audit and live in the session scratchpad
(`aud2.py`, `aud3.py`, `aud_f1.py`); the S-line's own `density.py` / `dist.py` were read to
find bugs but not executed and not imported. The only shared code is the repo's
`neuwirth_rank_n.gamma_N_factorial_n` / `solve_spherical_n`, which is the object under
test, not the instrument.

| target | verdict |
|---|---|
| **1. S10's density trend 0.411 / 0.726 / 0.867 with rank** | **REFUTED as a rank effect** (measurement replaces it, §1.3) |
| **2. S12 §2 soundness argument (4 steps)** | **AMEND** — step 3 is the weak one and is repairable in one line; §4 row (c) must be re-graded **REFUTED**, row (d) re-graded *true but not evidence for rank* |
| **3. S7 §5 "261 → 124, and that reduction is a theorem"** | **AMEND** — the classes are **not** `Aut(F₂)` orbits; the conclusion survives with a different (weaker) statement |

---

## 1. TARGET 1 — S10's density trend. **REFUTED as a rank effect.**

### 1.1 The instrument agrees with S10, so this is not a coding dispute

I re-implemented the sampler independently (own free/cyclic reduction, own move sampler,
own dedup, own census pre-check) and reproduced S10 §3 under S10's own acceptance rule
(first walk state with all relators ≥ 3 and **total** length in 12–16; per-state length cap
40; `cap_rotations = 4·10⁵`; fail-closed skip):

| rank | S10 §3 scored / d0 / frac / skipped | this audit, same rule | **median MEAN relator length** |
|---|---|---|---|
| 2 | 112 / 46 / **0.411** / 88 | 113 / 43 / **0.381** / 87 | **6.5** |
| 3 | 179 / 130 / **0.726** / 21 | 180 / 135 / **0.750** / 20 | **4.67** |
| 4 | 196 / 170 / **0.867** / 4 | 199 / 178 / **0.894** / 1 | **3.75** |

Agreement to within sampling noise. The code is right. The **design** is what fails.

The last column is the whole audit in one number. Under a fixed *total*-length band, rank
and per-relator length are the same axis: at rank 2 the band forces relators of ~6.5
letters, at rank 4 relators of ~3.75. S10's "rank" axis is a **relator-length axis wearing
a costume** — precisely the shape of `experiments/lessons/contrast-length-confound.md`,
which S10 §4.4 cites for the p-value rule but does not apply to its own matching variable.

### 1.2 The decisive test — hold PER-RELATOR length fixed instead

Identical move set, identical walks, identical cap, identical census budget, identical
fail-closed skip. **The only change is the acceptance variable: mean relator length in
[3.0, 4.5] instead of total length in [12, 16].**

| rank | scored | defect 0 | **fraction** | skipped | median mean rel. len | median total |
|---|---|---|---|---|---|---|
| 2 | 220 | 191 | **0.868** | 0 | 4.0 | 8 |
| 3 | 220 | 191 | **0.868** | 0 | 4.0 | 12 |
| 4 | 181 | 151 | **0.834** | 39 | 4.0 | 16 |
| 5 | 91 | 71 | **0.780** | 129 | 3.8 | 19 |

A second per-relator band, mean length in [4.5, 6.5]:

| rank | scored | defect 0 | fraction | skipped | median mean rel. len |
|---|---|---|---|---|---|
| 2 | 199 | 125 | **0.628** | 1 | 5.5 |
| 3 | 107 | 71 | **0.664** | 93 | 5.0 |

**The trend does not survive.** At matched per-relator length the fraction is flat and, if
anything, drifts *down* with rank (0.868 → 0.868 → 0.834 → 0.780). Rank 2 moves from 0.411
to 0.868 with no change to anything except which length is held fixed.

### 1.3 The corrected picture: one curve in relator length, rank does nothing

Pooling every state sampled in this audit (three designs, 1,657 scored states) and
tabulating the defect-0 fraction by **(rank, mean relator length)** — cell = fraction (n):

| rank | [3.0,3.5) | [3.5,4.0) | [4.0,4.5) | [4.5,5.5) | [5.5,6.5) | [6.5,7.5) |
|---|---|---|---|---|---|---|
| 2 | — | 1.00 (61) | 0.77 (120) | 0.82 (94) | 0.55 (170) | **0.41 (87)** |
| 3 | 1.00 (31) | 0.90 (51) | **0.83 (228)** | 0.66 (196) | 0.00 (1) | — |
| 4 | 1.00 (19) | **0.91 (160)** | 0.84 (177) | 0.67 (24) | — | — |
| 5 | 0.88 (8) | 0.88 (41) | 0.67 (42) | — | — | — |

Read **down a column** (rank varying, relator length fixed): nothing happens — the spread
is ±0.1 with overlapping samples, and the sign is not even consistent. Read **across a
row** (relator length varying, rank fixed): a strong monotone fall, 1.00 → 0.41 at rank 2
alone. The bolded cells are exactly S10's three headline numbers; they are the **diagonal**
of this matrix, and the diagonal is a length sweep.

> **Corrected statement.** Orientable thickenability among AC-trivial presentations near
> the standard one is governed by **mean relator length**, not by rank. At mean relator
> length ≈ 4 the fraction is ≈ 0.85 at every rank 2–5; at mean relator length ≈ 6.5 it is
> ≈ 0.4. S10's "the certificate gets commoner with rank" is an artifact of matching on
> total length. There is no measured population effect of rank.

### 1.4 The census-cap argument (S10 §4.1) — **unverified, and it flips sign under matching**

S10 argues the skip biases rank 2 *upward* ("high-degree germs are exactly the crowded
links that tend not to embed"), so 0.411 is an upper bound. I tried to verify it by
deciding the skipped states with the cut-scheme stack `solve_spherical_n`:

| rank | skipped (T design) | attempted | `NOT_SPHERICAL` | `SPHERICAL` | `UNSUPPORTED` |
|---|---|---|---|---|---|
| 2 | 87 | 87 | 5 | 0 | 82 |
| 3 | 20 | 20 | 0 | 0 | 20 |
| 4 | 1 | 1 | 0 | 0 | 1 |

The fast path decides **5 of 87** (5.7 %). All 5 are non-thickenable, which is *consistent*
with S10's direction and establishes nothing else: per
`calibrate-one-sided-hunts-on-a-positive-ladder.md`, a 5.7 % detection rate makes the
silence on the other 82 worth ~nothing. The premise "crowded links tend not to embed" is
also exactly the prior `S2` Q5 records as **untested in either direction** ("no genericity
theorem, no sparsity-based obstruction, no random-model study"). So §4.1 is a plausible
heuristic presented as a bound; it is not a bound.

Worse for the trend: **the skip asymmetry is itself a length artifact and reverses under
matching.** Under S10's rule the skips are 87/200 at rank 2 and 1/200 at rank 4. Under
matched per-relator length they are **0/220 at rank 2, 39/220 at rank 4, 129/220 at
rank 5** — because census size is `∏(deg−1)!` and at fixed *mean relator length* total
length grows with rank. If the S10 §4.1 heuristic is right, then in the matched design it
biases the **high** ranks upward, i.e. the corrected table of §1.2 is if anything an
over-estimate at rank 4–5 and the drift downward is real.

### 1.5 The "standard-likeness" attack (task 1c) — **fails; reported as a negative**

Structural flags on the scored states, T design (S10's own rule):

| rank | scored | frac | relator of length < 3 | destabilizable | some generator occurring **once** in the whole presentation | frac excluding those | link components ≥ 2 |
|---|---|---|---|---|---|---|---|
| 2 | 113 | 0.381 | 0 | 0 | 0 | 0.381 | 0 |
| 3 | 180 | 0.750 | 0 | 0 | 23 | 0.745 | 0 |
| 4 | 199 | 0.894 | 0 | 0 | **99** | 0.910 | 0 |

The acceptance rule already forbids short and destabilizable relators, so those counts are
zero by construction. The rank-4 samples *are* dramatically more "standard-like" in one
measurable sense — **half of them (99/199) still contain a generator that occurs exactly
once in the entire presentation**, versus none at rank 2 — but **excluding them does not
move the fraction** (0.894 → 0.910; at rank 5 in the matched design 0.780 → 0.694). So this
sub-attack does not explain the trend and is recorded as a failed line of attack. Median
walk depth at acceptance is 19–25 across all ranks and designs, so the ranks are not being
sampled at different distances either. **The confound is length and only length.**

### 1.6 What S10 §4.3's "distance" control does and does not control

Read from `dist.py`: the control replaces first-passage with a fixed step count and then
tests the band, which *is* a genuine distance control — but it **keeps the total-length
band (12–18)**, so it varies distance *inside* the confound and cannot address it. Two
further defects to record: at walk 70–120 the acceptance rate collapses (rank 4: **0**
states accepted in 18,000 walks; rank 3: 2), so the surviving states are an extreme
conditioning artifact rather than a sample of the distant population; and the surviving
rank-2 vs rank-3/4 comparison at walk 25–45 (0.485 vs 0.766/0.675) is the same
length-confounded diagonal as §3. S10 §4.3's conclusion "**the rank ordering survives**"
is therefore not supported by that control.

### 1.7 Required repairs to S10

- **R1.** §3's table and its "Reading" paragraph must be re-stated as a *relator-length*
  measurement, not a rank measurement; the §1.3 matrix above (or a re-run of it) replaces
  the headline. The sentence "at matched length the thickenable fraction roughly doubles
  from rank 2 to rank 4" is **false** as an inference about rank.
- **R2.** §4 must add matching-variable choice as confound 0 and record that it is the one
  that kills the result; the current §4 list ("all of them push against the trend") is
  wrong, because the dominant confound pushes *for* it.
- **R3.** §4.1 must be downgraded from "so the true rank-2 fraction is at most 0.411" to a
  stated heuristic with its measured verification rate (5/87 decided).
- **R4.** §4.3's "the rank ordering survives the control" must be withdrawn.
- **R5.** §5 and §6's first bullet ("S10 says the *target* grows with rank") must be
  withdrawn. What survives is: *the target grows as relators get shorter*, which is a
  restatement of Lackenby Lemma 3.1's own regime and buys no rank argument.
- **R6.** §6's second bullet (the computability payoff) survives as arithmetic — see §2.4
  below for the correct wording.

---

## 2. TARGET 2 — S12 §2's four-step soundness argument. **AMEND.**

### 2.1 Step 1 — sound

`Q` balanced and trivial: AC1–AC3 conjugate the presented group's Tietze class and
preserve tuple length; AC4 adds one generator and one relator. No gap. (Side note, checked:
the hunt can never produce a state in which some generator fails to occur, because the
abelianised relator matrix of a presentation of the trivial group is unimodular and a
missing generator gives a zero column — so Theorem D's "every generator occurs" hypothesis
is automatically satisfied and needs no gate.)

### 2.2 Step 2 — the stated flag is the right flag, and the machinery does deliver a global embedding

Task (i) asked whether `γ_N = 0` gives only a regular-neighbourhood or link-local
condition. It does not. `R1E_DISCONNECTED_LINK.md` Theorem D **sufficiency** constructs
`W = H⁰ ∪ (1-handles) ∪ (2-handles)`, a *compact orientable PL 3-manifold*, with
`K_P ⊂ int(W)` — a genuine global PL embedding, assembled per-component with a single
global orientation of `∂H⁰` and with the nesting objection explicitly answered (the
construction cones complementary regions rather than capping them). The code matches the
theorem: `gamma_N_factorial_n` (`neuwirth_rank_n.py:989`) minimises
`|A| − |C| + 2L − |AC|` over the whole compatible family with the general `2L` term, and
fails closed to `UNKNOWN_SIZE` above the cap. **Step 2 is sound modulo its own declared
dependency** (`lit_AK3_NEUWIRTH.md` is absent from this clone — S12 already flags this and
`literature-absent-in-cloud-clones.md` is exactly this failure mode). No repair beyond
keeping the flag.

### 2.3 Step 3 — **this is the weak step.** AMEND, one-line repair available

S12 step 3 reads: *"An orientable PL 3-manifold is a 3-manifold, so `Q` satisfies the
hypothesis of Lackenby Thm 1.3."* That sentence silently selects **the weakest of three
inequivalent definitions** that `S2` Q5 explicitly warns are inequivalent:

| source | "thickenable" means | is it what S2 verified? |
|---|---|---|
| Lackenby, as relayed | embeds in **some** 3-manifold | **SOURCE-RELAYED only** — the abstract, which is the only source-verified text, never defines the word |
| Fulek–Tóth (JACM 2022) | embeds in some **orientable** 3-manifold | SECONDARY |
| Neuwirth 1968, own framing | spine of a **closed orientable** 3-manifold | SECONDARY |

Answering task (ii) directly: **S2 did not verify "some 3-manifold"; S2 relayed it**, and
S2's own citation table forbids exactly this move ("safe to *use*, flag when *quoting*;
must NOT silently substitute 'orientable' or 'closed orientable'"). S12 step 3 uses the
relayed definition unflagged, and the step is a one-liner *only* under that reading. Under
either stronger reading the one-liner does not apply as written.

**Repair (and the reason this is AMEND, not REFUTED).** Theorem D's `W` is *compact*, so
all three readings are discharged by one extra sentence:

> `K_Q ⊂ int(W)` with `W` compact orientable PL. Its double `DW = W ∪_∂ W` is a **closed**
> orientable PL 3-manifold containing `W`, hence containing `K_Q`. And since `Q` is
> balanced with `π₁ = 1`, the regular neighbourhood `N(K_Q) ⊂ int(W)` is a compact
> contractible 3-manifold, so a 3-ball by Perelman (`R1E` Corollary D3); embedding
> `N ≅ B³ ⊂ S³` exhibits `K_Q` as a spine of the complement of a ball in a closed
> orientable 3-manifold. Every one of the three hypotheses above is therefore met.

This repair costs nothing and removes the line's dependence on which of the three
definitions Lackenby actually uses — which matters, because that is precisely the fact the
S-line cannot source. **S12 §2 step 3 must not ship in its current one-line form.**

### 2.4 Step 4 — sound (task (iii))

Each link checked:
`P ~st P^{+k}` — k applications of AC4. ✓
`P^{+k} ~AC Q` — the hunt's own AC1–AC3 path at rank `N`. ✓
`Q ~AC standard_N` — Lackenby Thm 1.3 at rank `N`; `S2` found no rank restriction in three
channels, flagged as *absence of evidence*, and S12 §7.1 already records that the weaker
"stably AC-trivializable" reading also closes the chain. ✓
`standard_N ~st standard_n` — `N − n` applications of AC5, each legal because the relator
`x_i` is a single generator occurring in no other relator. ✓
Transitivity of `~st` closes it. **No gap.** (The `~^{(1)}` used in §5 is likewise
transitive: concatenating two chains of rank ≤ n+1 gives a chain of rank ≤ n+1.)

### 2.5 §4's verdict table must be re-graded — this is the substantive consequence

| S12 §4 row | S12's grade | audited grade |
|---|---|---|
| (c) more generators make the certificate more common | **SUPPORTED** (cites S10's 0.411/0.726/0.867) | **REFUTED.** §1 above: at matched per-relator length the fraction is 0.868 / 0.868 / 0.834 / 0.780 for ranks 2/3/4/5. There is no rank effect. |
| (d) more generators make the test computable | SUPPORTED | **TRUE BUT MIS-READ.** It is the identity `census = ∏(deg−1)!` with `deg ≈ (total length)/(rank)`; it says *the census is affordable exactly when relators are short*, which is a statement about relator length, not about rank. It cannot be quoted as "high rank restores the instrument in the length regime where AK(3)'s stable class lives" (S10 §6), because a rank-`N` state of total length 15–24 has near-minimal relators, i.e. it is near-standard — it is not a length-matched stand-in for a deep rank-2 class member. |

With (b) already REFUTED by S3/S8 and (a) admitted vacuous, **§4 leaves nothing on the
positive side of the "does high rank help" question except an arithmetic remark about
census cost.** S12's headline answer — "not by any mechanism, by a population effect and a
computability effect" — must lose the population effect. The operational recommendation
"run the hunt at rank 4–6, not at rank 2" loses its stated basis; what the corrected data
supports instead is *run the hunt where relators are short*, which is rank-agnostic advice
and is the regime Lackenby's own Lemma 3.1 passes through.

Falsifiable prediction **P1** ("succeed at a rate near the S10 density, ≳ 70 %, at depth
2–4") must be restated against mean relator length, not rank, or it is untestable.

---

## 3. TARGET 3 — S7 §5's "261 → 124 is a theorem". **AMEND.**

### 3.1 What "aca" actually means (fetched and read this session)

`origin/cursor/heur-u124-s20mk2-a42e` was fetched and four artifacts read:
`data/ms_unsolved_reps/aca_124.csv`,
`results/equivalence_classes/ms1190_tables/unsolved_124_aca_classes.csv` and its `README.md`,
`results/equivalence_classes/PROOFS.md`, and `experiments/equivalence_classes/README.md`.
That branch answers the question in its own words, and the answer contradicts S7:

> `ms1190_tables/README.md`: "Table A is quotiented by **Aut(F₂)** only … Table B is
> quotiented by **ACA = AC moves *together with* change of variables**, which is strictly
> coarser. **124 is an upper bound** on the number of distinct problems, not a proven class
> count."

and the counts, from `PROOFS.md`'s own summary table: 261 presentations, **137 edges**,
**93 change-of-variables-only (`cv`)**, **44 needing AC moves (`ac`)**, 124 classes.

So: **the 124 `aca_*` classes are NOT `Aut(F₂)`-orbit classes.** The Aut-orbit table on
that branch is a *different file* — `solved_640_aut_orbits.csv`, 113 rows, the solved side.
S7 §5 cites `unsolved_124_aca_classes.csv` and describes it as "`Aut(F₂)`-orbit based".
That is factually wrong about the file it cites.

Spot-checks run with my own substitution/canonicalisation code (`aud_f1.py`), independent
of both branches: `aca_115` **is** AK(3) (both canonicalise to `XYXyxy`, `XXXyyyy`) ✓; the
`cv` edge 22_13 → 22_14 under `x ↦ X, y ↦ y` ✓; the `cv` edge 22_13 → 23_21 under
`x ↦ xY, y ↦ y` ✓. The two substitutions are Nielsen automorphisms. So the certificates I
sampled are real; the *description* of what they certify is what is wrong.

### 3.2 Does Cor. F1 still do the collapsing work? **Yes — and here is the correct argument**

The 137 edges form a spanning forest (261 − 137 = 124), so any subset is acyclic. Deleting
the 93 `cv` edges leaves **261 − 44 = 217** components. Therefore:

- without F1, the 261 representatives are **at most 217** objects up to AC-equivalence;
- `~^{(1)}` contains `~AC` (= `~^{(0)}`) and, by Cor. F1, contains every `Aut(F_n)` orbit,
  and `~^{(1)}` is transitive; so every ACA class is a single `~^{(1)}` object;
- hence the 261 representatives are **at most 124** objects at depth ≥ 1.

F1 does real work — it is what turns ≤ 217 into ≤ 124 — but the reason S7 gives for it is
the wrong reason, and the count is an **upper bound**, not an exact class count (two
distinct ACA classes may still be `~^{(1)}`-equivalent; nothing rules that out).

### 3.3 Required repairs to S7 §5

- **R7.** Replace "the class structure is `Aut(F₂)`-orbit based
  (`unsolved_124_aca_classes.csv`)" with "the class structure is **ACA** — AC moves
  *together with* change of variables (`unsolved_124_aca_classes.csv`; the `Aut(F₂)`-orbit
  table on that branch is the *other* file, `solved_640_aut_orbits.csv`)".
- **R8.** Replace "there are 124" with "**there are at most 124**", per the source's own
  README.
- **R9.** Replace "that reduction is a theorem, not a heuristic" with a statement that
  names its two inputs: Cor. F1 (this line, proved, audit status as recorded in S7) **and**
  137 machine-verified merge certificates produced on `origin/cursor/heur-u124-s20mk2-a42e`
  and **not re-verified here** (3 of 137 spot-checked in this audit). It is a theorem
  *conditional on those certificates*; calling it "a theorem, not a heuristic" without the
  dependency overstates what this branch has established.
- **R10.** Give F1's actual contribution as the sharp number: it collapses ≤ 217 AC-classes
  to ≤ 124 `~^{(1)}`-objects (93 of the 137 edges are change-of-variables only).

---

## 4. The single most serious problem

**S10's rank axis is a relator-length axis, and S12 §4(c) — the only "SUPPORTED" row on the
positive side of the session's central question — is built on it.** With (c) refuted, the
session's answer to "does going to 9 or 10 generators help" has no positive empirical
component left: S3 and S8 killed the mechanisms, and the population effect was an artifact
of matching on total length. The corrected measurement is flat-to-slightly-decreasing in
rank, which if anything is mild evidence *against* the high-rank programme.

## 5. What the audit did NOT break

- The census implementation: independently exercised, reproduces S10's own numbers under
  S10's own rule, and returns the certified values on the fixtures (AK(3) `minimum_defect`
  4; standard `("x","y","z")` defect 0).
- `R1E` Theorem D as machinery: the sufficiency construction really does produce a global
  PL embedding in a compact orientable 3-manifold. Only its provenance flag stands.
- S12 §2 steps 1, 2 and 4: no gap found.
- The "standard-likeness" attack on the rank-4 samples (§1.5): the degeneracy is real and
  large (99/199) but does not move the fraction. Recorded as a failed attack.
- S7 §5's identification of AK(3) as `aca_115`: verified independently.
