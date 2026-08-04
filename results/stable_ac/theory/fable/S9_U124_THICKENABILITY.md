# S9 — The 124 unsolved Miller–Schupp classes are all NON-thickenable, and six of them are certified γ_N = 1 gateways

Task A9, S-line, branch `claude/stable-ac-conjecture-stabilization-rwo9as` (**must be merged
into `fable/proof` by the user**). Written 2026-08-04. **This file only ADDS; it edits no
existing file and modifies no existing code.**

Status: **measurement complete; the negative is certified two-sidedly, the ranking is a
search-order recommendation and is explicitly length-confounded above the calibrated band.**

Artifacts (all new, under `results/stable_ac/fable/`):

| file | content |
|---|---|
| `aca_124.csv` | the 124 minimal representatives, copied verbatim from `origin/cursor/heur-u124-s20mk2-a42e:data/ms_unsolved_reps/aca_124.csv` (no code taken from that branch) |
| `u124_sweep.jsonl` / `u124_sweep_summary.json` | the per-row sweep and the ranking |
| `u124_calibration.json` | the positive-ladder calibration, rates BY LENGTH |
| `u124_neighbourhood.jsonl.gz` / `..._summary.json` | depth-1 AC neighbourhood of all 124 |
| `u124_gateway_neighbourhood.jsonl.gz` / `..._summary.json` | deeper harvest from the six γ_N = 1 gateways |

Code: `experiments/stable_ac/fable/u124_thickenability.py`; tests
`tests/test_u124_thickenability.py` (24 tests, all passing). Combined run of the new file plus
the pre-existing `tests/fable` suite: **695 passed, 8 skipped, 0 failed**.

---

## 0. Units, fixed first (S3 §0)

`neuwirth_rank_n.gamma_N_factorial_n` returns `minimum_defect`; this project's
`γ_N = minimum_defect // 2`. **`defect 0` ⟺ `SPHERICAL` ⟺ thickenable.** Every raw number
below is the UNHALVED defect where it says `defect`, and halved where it says `γ_N`.

---

## 1. What was tested and why it could have settled an open case

Lackenby arXiv:2606.06122v1 (abstract VERIFIED-FROM-SOURCE, `S2_LITERATURE_HIGH_RANK.md`
Q1): *thickenable balanced presentations of the trivial group satisfy the (unstable)
Andrews–Curtis conjecture*. All 124 rows are balanced (2 generators, 2 relators) and — checked
here, not assumed — present the trivial group. So a single `γ_N = 0` row would have settled an
open Miller–Schupp case outright.

`aca_115 = ⟨x,y | YXYxyx, YYYYxxx⟩` **is AK(3)** and is the anchor. The project had censused
AK(3)'s own class (124,296 members, 0 spherical); the other **123 classes had never been
tested**.

**Group triviality re-checked per row.** Todd–Coxeter over the trivial subgroup completes with
index 1 for **all 124** rows. `TC_CAP` had to be raised to 2·10⁶: at 2·10⁵, `aca_82` and
`aca_86` come back `CAP_EXCEEDED`, which is *unknown*, never *non-trivial*. They need ≈2.5·10⁵
and ≈2.3·10⁵ cosets respectively.

---

## 2. HEADLINE — no hit, and the negative is certified, not a null

> **None of the 124 representatives is thickenable, and none of the 67,864 distinct AC-class
> members reached from them is either.** No open Miller–Schupp case is settled by this sweep.

| population | states decided | `SPHERICAL` | `NOT_SPHERICAL` | fail-closed / uninformative |
|---|---|---|---|---|
| the 124 representatives | 124 | **0** | **124** | **0** |
| depth-1 AC neighbourhood of all 124 | 34,666 | 0 | 34,666 | 0 |
| deeper harvest from the six γ_N = 1 gateways | 39,108 | 0 | 39,108 | 0 |
| union of the two neighbourhood runs | **67,864 distinct** | **0** | all | **0** |

**Why this is a certified negative and not a budget exhaustion.** The deciding instrument is
`disconnected_split.decide_pair` — the R1c-v2 cut-scheme solver with the exact factorial census
behind it, i.e. the *same entry point* the 13,040-member AK(2) battery and the 124,296-member
AK(3) matched control used. It is a decision procedure, not a search:

* every one of the 124 rows carries `exhaustive = true` and `support_kind = IN_SCOPE`
  (all 124 have link components `L = 1` and no A-loop, so nothing fell through the fail-closed
  boundary);
* an **independent second solver** — `neuwirth_rank_n.solve_spherical_n`, the rank-*n*
  Theorem-R decision, which reaches the slot arithmetic through a completely different support
  decomposition — was run on every row and agrees `NOT_SPHERICAL` on **123/124**, failing closed
  on the remaining one. **Zero disagreements.** A disagreement raises `SweepContradiction` and
  is never voted on;
* the three rows whose compatible family fits the 2·10⁶ cap were additionally censused
  exhaustively and the census agrees with the solver on all three.

So the sentence "these 124 presentations are not thickenable" is a theorem-grade statement about
the *presentations*, modulo the R1c-v2 note's own audited correctness — **not** a statement about
their AC classes (see §6).

---

## 3. The one genuinely new positive finding: six certified γ_N = 1 gateways

A closed bracket is an **exact** γ_N even without a census: instrument A's exhaustive
`NOT_SPHERICAL` certifies `γ_N ≥ 1`, and a re-verified defect-2 rotation certifies `γ_N ≤ 1`.
That is `gateway_scan.py`'s two-sided argument, and it does not depend on any detection rate.

Every witness below was recomputed **twice independently** — by
`gateway_scan.verify_witness` and by `disconnected_split.check_witness_l_general` (a
permutation-only checker in a different module, which also re-derives `L` and the per-component
Euler numbers). All six came back `defect = 2, genus = 1, L = 1, compatible = True`.

| row | presentation | total length | γ_N | how |
|---|---|---|---|---|
| **aca_117** | `YYYXyyx, YXXXyxx` | 14 | **1** | exact census, 518,400 rotations, `minimum_defect = 2` |
| **aca_11** | `YXXXyxx, YYYXyxyx` | 15 | **1** | exhaustive NO + verified defect-2 witness |
| **aca_121** | `YXXXyxx, YYYYXyyyx` | 16 | **1** | exhaustive NO + verified defect-2 witness |
| **aca_17** | `YXXXYxYx, YYYYXyyyx` | 17 | **1** | exhaustive NO + verified defect-2 witness |
| **aca_30** | `YYXXyx, YYYYYxyXXyX` | 17 | **1** | exhaustive NO + verified defect-2 witness |
| **aca_122** | `YXXXyxx, YYYYYXyyyyx` | 18 | **1** | exhaustive NO + verified defect-2 witness |
| aca_115 = **AK(3)** | `YXYxyx, YYYYxxx` | 13 | **2** | exact census, 86,400 rotations, `minimum_defect = 4` (reproduces the pinned S3 value) |
| aca_116 | `YYYXyyX, YXXXyxx` | 14 | **2** | exact census, 518,400 rotations, `minimum_defect = 4` |

**Why the gateways matter.** By the AUDITED graft ceiling (`R3PRIME_GRAFT_CALCULUS.md` Thm G6)
a single non-cancelling AC2 graft lowers γ_N by at most 1, so **a thickenable member can only
ever be reached from a γ_N = 1 state**. AK(3) itself sits at γ_N = 2 — one unit further out than
six of its 123 unsolved siblings. The six rows above are, on this measure, the *closest of the
124 to Lackenby's hypothesis*, and they are where the next session's search budget belongs.

**This is the deliverable even though nothing hit zero.** The deeper harvest already spent
39,108 states inside those six classes (6,518 canonical members each, per-relator cap
`total length + 4`) without a hit; that is a bounded negative on the gateways' immediate
vicinity, not on their classes.

---

## 4. Calibration — mandatory, and it changes how the table above may be read

Two instruments were used and they must not be conflated.

**Instrument A — the exact decision** (`decide_pair`). Two-sided. Measured on the positive
ladder (states independently known to have γ_N = 0):

| total length | ladder states measured | A detects SPHERICAL | A fails closed | A false negatives |
|---|---|---|---|---|
| 13 | 12 | 12/12 = **1.00** | 0 | 0 |
| 14 | 12 | 11/12 = 0.92 | 1 | 0 |
| 15 | 6 | 6/6 = **1.00** | 0 | 0 |
| 16 | 12 | 12/12 = **1.00** | 0 | 0 |
| 17 | 12 | 12/12 = **1.00** | 0 | 0 |
| 19 | 1 | 1/1 = **1.00** | 0 | 0 |

**54/55 detected, 1 fail-closed (an A-loop rung from `witness_sensitivity.json`), and zero
false negatives** — the run raises `SweepContradiction` if instrument A ever returns
`NOT_SPHERICAL` on a certified γ_N = 0 state, and it never did. Instrument A does **not**
degrade with length in the measured band, which is what a decision procedure should look like.

**Instrument B — the sampled hill-climb** (`gateway_scan.sampled_min_defect`, 40,000
evaluations × 3 independent seeds, every witness re-verified). ONE-SIDED: it bounds γ_N from
ABOVE only.

| total length | 13 | 14 | 15 | 16 | 17 | 19 |
|---|---|---|---|---|---|---|
| B detection rate | **1.00** | 0.92 | 0.83 | 0.92 | **0.50** | **0.00** (n = 1) |

The cliff reproduces the filed lesson
(`experiments/lessons/calibrate-one-sided-hunts-on-a-positive-ladder.md`) at a slightly
different place: 100 % at 13, half at 17, nothing at 19.

**No positive control exists at total lengths 18, 20, 21, 22, 23, 24, 25.** AK(2)'s thickenable
members top out at length 19 (a single state) and `witness_sensitivity.json`'s certified ladder
stops at 22 with rungs whose spelling is out of instrument A's scope. So instrument B is
**calibrated only for 13–17** and is **uncalibrated or blind for 18–25**, which covers
**87 of the 124 rows**.

**Two bias directions, both pointing UP** (so both make the numbers look better than they are):

1. rung selection — a state is on the ladder only because some instrument certified it;
2. **composition mismatch** — every one of the 124 targets has min generator degree ≥ 6
   (histogram: 6→2, 7→90, 8→11, 9→11, 10→4, 11→6), while the ladder's 125 states run
   3→32, 4→32, 5→33, 6→9, 7→18, 8→1, i.e. **57 % of the ladder sits below the targets' floor**
   and the mismatch is worst at exactly the lengths that matter: all 12 measured length-14 rungs
   except one have min degree 3, and all 12 length-17 rungs have min degree 5. A state that is
   sparse in one generator has a much smaller compatible family in that direction and is
   *easier* for the sampler than a target of the same total length. (Length 16 is the one clean
   cell: all 12 rungs have min degree 7, and B scores 0.92 there.)

So the measured B rates bound the instrument's sensitivity **on the actual targets** from above.
A low cell is conclusive; a high cell is optimistic.

### What is and is not marked UNINFORMATIVE

* **Zero of the 124 rows are UNINFORMATIVE about thickenability.** The headline negative comes
  from instrument A, which returned a two-sided, exhaustively certified verdict on all 124 (and
  on all 67,864 neighbours). Its calibration shows no length degradation. This null is *not* a
  one-sided hunt's silence.
* **87 of the 124 rows carry an UNINFORMATIVE γ_N *upper bound*** (`sample_calibrated = false`:
  lengths 18–25). There, the *absence* of a lower witness says nothing, so `γ_N_upper` may be far
  above the truth and must not be read as a measurement of distance.
* A witness that WAS found is a certificate at every length: it was re-verified by an
  independent recomputation of the defect. That is why `aca_122` (length 18, formally outside the
  calibrated band) still has a *certified* γ_N = 1 — the bracket closed.

---

## 5. The ranking, and the length confound that eats most of it

Full ranking: `u124_sweep_summary.json → ranking` (124 rows). Top 10:

| rank | row | pair | L | γ_N bracket | certified? | B calibrated at this L? |
|---|---|---|---|---|---|---|
| 1 | aca_117 | `YYYXyyx, YXXXyxx` | 14 | **[1, 1]** | yes (census) | n/a (exact) |
| 2 | aca_11 | `YXXXyxx, YYYXyxyx` | 15 | **[1, 1]** | yes | yes |
| 3 | aca_121 | `YXXXyxx, YYYYXyyyx` | 16 | **[1, 1]** | yes | yes |
| 4 | aca_17 | `YXXXYxYx, YYYYXyyyx` | 17 | **[1, 1]** | yes | yes |
| 5 | aca_30 | `YYXXyx, YYYYYxyXXyX` | 17 | **[1, 1]** | yes | yes |
| 6 | aca_122 | `YXXXyxx, YYYYYXyyyyx` | 18 | **[1, 1]** | yes | **no** (witness still valid) |
| 7 | aca_115 = AK(3) | `YXYxyx, YYYYxxx` | 13 | [2, 2] | yes (census) | n/a (exact) |
| 8 | aca_116 | `YYYXyyX, YXXXyxx` | 14 | [2, 2] | yes (census) | n/a (exact) |
| 9 | aca_1 | `YYXXyxx, YYYxyXyX` | 15 | [1, 2] | no | yes |
| 10 | aca_10 | `YXXXyxx, YYXYXyyX` | 15 | [1, 2] | no | yes |

**The length confound is not hypothetical here — it is visible in the data**
(`experiments/lessons/contrast-length-confound.md`):

| total length | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 24 | 25 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| rows | 1 | 2 | 8 | 6 | 20 | 7 | 22 | 7 | 18 | 6 | 9 | 2 | 16 |
| min γ_N upper | 2 | 1 | 1 | 1 | 1 | 1 | 2 | 2 | 2 | 3 | 3 | 3 | 3 |
| median γ_N upper | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 3 | 4 | 4 | 4 |

The median upper bound rises monotonically with total length, and it does so exactly where
instrument B's calibration falls off. **The most likely reading is that above length 17 the
ranking key is measuring word length, not distance to thickenability.** Rows of different length
are therefore NOT comparable, and the only part of the ranking that carries weight is the
certified bracket in §3 plus the calibrated band L ≤ 17 (37 rows: 5 at γ_N ≤ 1, 32 at γ_N ≤ 2).

**Operational recommendation for the next session:** attack `aca_117, aca_11, aca_121, aca_17,
aca_30, aca_122` — in that order — and do NOT read the long rows' high bounds as evidence they
are far from thickenable. If a cheap γ_N upper bound is wanted for the long rows, the
calibration ladder must be extended to lengths 18–25 *first*; per the filed lesson, a hunt at a
length where the ladder itself cannot be built supports no conclusion.

---

## 6. What this does and does not prove

**Does:**

* Each of the 124 presentations, *as spelled*, is not thickenable — so Lackenby Thm 1.3 cannot
  be applied to it directly. Same for 67,864 members of their AC classes reached here.
* Six of them have γ_N = 1 exactly, AK(3) and aca_116 have γ_N = 2 exactly. These are the first
  exact γ_N values recorded for any Miller–Schupp unsolved representative other than AK(3).

**Does not:**

* It says nothing about the AC-triviality of any of the 124. Thickenability is a property of a
  *presentation*, not of an AC class; a class can contain a thickenable member with no member
  tested here being one. The AK(3) precedent is exactly this shape: 124,296 members censused, 0
  spherical, and AK(3)'s AC-triviality remains open.
* It says nothing in the negative direction either. Per `FRAMING.md` §2, a *class-wide* lower
  bound on γ_N would be the headline disproof of stable ACC — and nothing here is class-wide.
  The neighbourhoods are bounded harvests, and a bounded-budget search outcome is never a proof
  (`FRAMING.md` §3).
* The `NOT_SPHERICAL` verdicts inherit whatever correctness `R1C_V2_CUT_SCHEMES.md` has. That
  note is marked AUDITED with errata E1–E4; the cross-check against `solve_spherical_n` (123/124
  agreeing, 0 disagreements) and against the exact census (3/3 agreeing) is the strongest
  independent evidence this sweep can add, not a replacement for that audit.

---

## 7. Traps this run confirmed or added

* **T-S9a (confirmed, filed lesson).** The one-sided sampler's cliff is real and lands between
  lengths 17 and 19 at 120,000 total evaluations. It is *not* the instrument that produced the
  headline: separating the exact decision from the sampled bound is what let this sweep report a
  certified negative instead of an uninformative one. **Any future one-instrument design here
  should be refused.**
* **T-S9b (new).** *A positive ladder matched only on LENGTH is not matched.* AK(2)'s thickenable
  members are structurally sparser than the targets (57 % of the ladder has min generator degree
  below the targets' floor of 6), and the mismatch is length-dependent, so it varies cell by cell
  rather than shifting the curve uniformly. Length-matching alone therefore biases detection
  rates upward by an amount that itself depends on length. Record `min_degree` and the census
  family size of every rung, and say which direction the residual mismatch biases.
* **T-S9c (new).** *Todd–Coxeter's cap is a silent trap on this corpus.* At 2·10⁵ cosets, two of
  the 124 (`aca_82`, `aca_86`) return `CAP_EXCEEDED`. A pipeline that reads that as "not the
  trivial group" would have wrongly excluded two rows from Lackenby's hypothesis. Cap 2·10⁶
  completes both at index 1 in under a second.
* **T-S9d (new).** *A found witness and an unfound witness are not symmetric.* `sample_calibrated
  = false` invalidates the *absence* of a better witness, never a witness that was found and
  re-verified. Conflating the two would have thrown away `aca_122`'s certified γ_N = 1.

---

## 8. Budget and process

All computation ran under `guarded_run.py` (`PROCESS_GUARD.md`), one experiment at a time,
single-threaded, foreground, each stage preflighted on the same code path:

| stage | wall | guard verdict |
|---|---|---|
| calibration | 35.5 s | ok |
| sweep (124 rows), first run | 156.1 s | ok |
| neighbourhood, depth 1 over all 124 + top-10 harvests | 185.8 s | ok |
| gateway neighbourhood, top-6 deep harvest | 249.6 s | ok |
| sweep (124 rows), re-run to add the certified-bracket fields | 152.6 s | ok |

The sweep was run twice: the second run only added the `gamma_N_certified` /
`certified_gamma_N_rows` / `gateways_gamma_N_1` fields and the `sample_calibrated_meaning`
note to the artifact; **every verdict, census value and ranking position was identical**
(124 `NOT_SPHERICAL`, 0 thickenable, 0 uninformative, same top-10). Total guarded compute
≈ **13.0 minutes**, well inside the ~45-minute task budget and the 10-minute-per-experiment
ceiling. Ledger rows are in `results/stable_ac/fable/guard_ledger.jsonl`; child logs in
`guard_logs/`.

**Nothing was committed and no PR was opened**, per the task contract. The branch must be merged
into `fable/proof` by the user.
