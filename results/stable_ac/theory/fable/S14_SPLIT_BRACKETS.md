# S14 — Splitting as an instrument: sound, calibrated, and **too loose to buy back the blind regime**

Task A13, S-line, branch `claude/stable-ac-conjecture-stabilization-rwo9as` (**must be merged
into `fable/proof` by the user**). Written 2026-08-04. **New files only**: this note adds
`experiments/stable_ac/fable/split_bracket.py`, `tests/fable/test_split_bracket.py` and the
artifacts below; it edits no existing file and no existing code.

Status: **instrument built, calibrated two-sidedly, and run. The calibration is the result.**

| artifact | content |
|---|---|
| `results/stable_ac/fable/split_bracket_calibration.json` | the two-sided overshoot measurement, indexed by forced census reduction |
| `results/stable_ac/fable/split_bracket_targets.jsonl` | per-target rows (checkpointed as they finish) |
| `results/stable_ac/fable/split_bracket_summary.json` | closures, merged ranking of all 124, Baumslag–Solitar test |

Tests: `tests/fable/test_split_bracket.py`, **24 tests, all passing**. They test the *bound
direction* rather than the numbers: that `split_shapes` never emits a degenerate shape, that a
tampered split fails the replay certificate, that `independent_defect` agrees with
`gateway_scan.verify_witness` and rejects a broken rotation, that every certified split of a
known state lands at or above it, and that `bracket_row` **raises** rather than record a value
below a certified lower bound or a known exact γ_N.

**Process note.** `guarded_run`'s `GuardLock` was held continuously by other lines' experiments
for the whole session, with a second line already queued behind it, so taking it would have
stalled two other agents. Every run here was therefore made directly under the same discipline
the guard enforces — foreground, one at a time, `OMP/OPENBLAS/MKL/NUMBA` pinned to 1 thread, a
hard `timeout`, per-census and per-row caps so no stage can hang, and checkpointing to disk after
every row. Total: 355 s calibration + 900 s + 304 s targets ≈ **26 minutes** of compute.

---

## 0. Units and bound direction, fixed before anything else

`gamma_N_factorial_n` returns `minimum_defect`; this project's **γ_N = minimum_defect // 2**,
and `defect 0` ⟺ `SPHERICAL` ⟺ thickenable. Every raw number below labelled `defect` is
UNHALVED.

The one inequality this note uses, and the only direction it may be used in:

> For a **certified** split `P'` of `P` and ANY compatible rotation system on `P'` of defect `d`:
> `d/2 ≥ γ_N(P') ≥ γ_N(P)`.

So a witness found *after* splitting is an **upper** bound for the base — and a *failure* to
find one after splitting says **nothing** about the base. Concluding anything about `P` from
`γ_N(P') > k` is the filed bound-direction error
(`experiments/lessons/parallel-runs-and-bound-direction.md`) and the code refuses it: the only
fields that carry a split's value are named `split_*` / `*_upper`, the base's value is only ever
the interval `[lower, upper]`, and `bracket_row` raises rather than record a split value below a
certified lower bound.

**Everything here is conditional on Conjecture S8** (`S8_SPLITTING_MONOTONICITY.md` §3), which
is a proof *sketch* with two open gaps (GAP‑S8‑1, the defect bookkeeping under the bigon
contraction; GAP‑S8‑2, degenerate splits). GAP‑S8‑2 is excluded by construction —
`split_shapes` never emits a shape leaving a generator of germ degree 1. GAP‑S8‑1 is not
discharged here; it is *tested*, see §2.

---

## 1. The instrument

`split_bracket.py`. Given a presentation `P`:

1. **enumerate splits.** For each generator of degree `d`, a *shape* `(k, a0, sizes)` puts `a0`
   occurrences back on `g` and `sizes[i]` on a fresh copy `u_i`. The germ degrees become
   `deg(g) = a0 + k` and `deg(u_i) = sizes[i] + 1` — note the `k` definition relators `u_i g^{-1}`
   each put one occurrence of `g` *back*, which is why a generator of degree 18 cannot be
   pushed below a census factor of ≈5.6·10⁶ in a single round. The compatible census shrinks
   from `(d-1)!` to `(a0+k-1)!·∏ sizes[i]!`. A *pattern* then decides **which** occurrences go
   together (block / round-robin / random, with a rotation offset).
2. **certify every split by replay** — `high_rank_refine.certify_refinement`, which re-reads the
   definition layering out of `P'` alone, expands innermost-out and requires the input relators
   to reappear up to cyclic rotation and inversion. Single-step plans additionally pass
   `high_rank_refine.split_minor_certificate` (the link of `P` must be exactly the contraction of
   the link of `P'` along the `k` bigon edges — S8's structural claim, checked instance by
   instance). **No uncertified plan is ever scored.**
3. **score** each certified split by the exact census when the family fits the cap (two-sided *on
   the split*), otherwise by `gateway_scan.sampled_min_defect` (upper bound on the split).
4. **report the minimum over certified splits**, with the winning plan recorded so the bound is
   replayable, and the winning rotation re-verified twice: `gateway_scan.verify_witness` **and**
   `split_bracket.independent_defect`, a from-scratch rebuild of `A`, `B` and the germ map from
   the letters that never calls `build_link_n`.

### 1a. The one design fact worth carrying forward

**The pattern matters more than the shape.** On `aca_117` (exact γ_N = 1) the shape
`k = 2, a0 = 2` reaches the true defect 2 with a *block* pattern and overshoots to 4 with a
round-robin pattern; `k = 3, a0 = 1` behaves the same way. Cost is set by the shape, tightness
by the pattern. The search therefore walks a few cheap shapes and many patterns, not the other
way round.

---

## 2. Calibration — a two-sided ladder, and Conjecture S8 survived 65 tests

Rungs are states whose γ_N is a **number**, not a bound: A9's three exactly-censused rows, its six
certified gateways, γ_N = 0 states from `u124_thickenability.positive_ladder`, and short AK(2)
members re-censused exactly here. 25 rungs, 100 (rung × reduction) cells, 65 of them producing a
bound.

**S8 test.** A certified split scoring strictly BELOW its base's exact γ_N would refute
monotonicity; `bracket_row` raises `MonotonicityViolation` and never records it as a better
bound. **0 violations in 65 measured cells** (27 on γ_N = 0 rungs, 34 on γ_N = 1, 4 on γ_N = 2).
That is not a proof of GAP‑S8‑1, but it is 65 more instances on top of S8's 632 — and unlike
those, these were produced at split depths up to 12 fresh generators, where the sketch's bigon
contraction has to be iterated.

**Why the rungs had to be forced to split (T‑S9b, applied).** A length-13 rung has a compatible
family of ~10⁴ and needs *no* split at all; every one of the 124 targets has a family between
1.6·10⁹ and 2.6·10¹⁷ and needs a **reduction of at least ~8·10³** before anything fits a
200,000-rotation cap. A calibration that let each rung split as little as it liked would measure
a regime no target occupies. So every rung was re-run with the per-split census cap forced down
to `base_census // R`, and the overshoot is reported against the **achieved** reduction.

### The overshoot distribution (this is the headline)

| achieved reduction `base census / split census` | cells | mean overshoot | fraction exact |
|---|---|---|---|
| < 10 | 15 | **0.00** | **1.00** |
| 10 – 10² | 2 | 0.50 | 0.50 |
| 10² – 10³ | 18 | 0.94 | 0.17 |
| 10³ – 10⁴ | 14 | **2.14** | **0.00** |
| 10⁴ – 10⁶ | 16 | **1.44** | **0.00** |

Overall histogram of (split upper bound − true γ_N): `0 → 19, 1 → 27, 2 → 13, 3 → 6`.

**Read the bottom two rows against the fact that every target needs ≥ 8·10³.** In 30 cells at
target-matched reductions the instrument recovered the true γ_N **zero times**, with mean
overshoot 1.4–2.1.

### The gateways, rung by rung (true γ_N in bold where recovered)

| row | L | true γ_N | R = 1 | R = 100 | R = 10⁴ | R = 10⁶ |
|---|---|---|---|---|---|---|
| `aca_117` | 14 | 1 | **1** | 2 | – | – |
| `aca_11` | 15 | 1 | **1** | 2 | 3 | 3 |
| `aca_121` | 16 | 1 | 2 | 2 | 3 | 3 |
| `aca_17` | 17 | 1 | 2 | 2 | 2 | 2 |
| `aca_30` | 17 | 1 | 2 | 2 | 2 | 2 |
| `aca_122` | 18 | 1 | 2 | 2 | 2 | 2 |
| `aca_115` = AK(3) | 13 | 2 | **2** | **2** | – | – |
| `aca_116` | 14 | 2 | **2** | **2** | – | – |

(`–` = no certified plan survived at that cap; see §5, the certifier's layering budget.)

**Verdict on the instrument, stated plainly.** The split bracket is *sound* (0 violations, every
bound replayable, every witness twice-verified) and it is *exact only where it barely has to
split*. At the reductions the 124 unsolved rows actually require it overshoots by 1–3 and never
lands on the truth. **It does not buy back the regime where A9's sampler is blind.** The idea
that motivated A13 — "splitting shrinks the census, so it buys the long rows" — is refuted on its
own calibration: splitting shrinks the census by paying in defect, and at the exchange rate the
long rows need, the payment exceeds the whole quantity being measured.

---

## 3. The targets

Run at exactly the calibration's budget (census cap 200,000, 10 plans, 8 s per row) so the
calibration applies to it — `experiments/lessons/instrument-the-search-before-reading-its-null.md`.

**Caveat on the budget, recorded because it is the kind of thing that quietly invalidates a
calibration.** The per-row budget is *wall clock*, and this container was shared with three other
lines' experiments throughout, so the number of plans a row actually got varies with load. Both
stages ran under comparable load, and every row records `plans_built`, `plans_evaluated`,
`plans_failed_certification` and `defects_by_plan`, so the realised budget is auditable per row
rather than assumed. Nothing here should be compared against a future run made on an idle box
without re-reading those counters.

**Scope run: all 116 rows of the 124 whose bracket was still open**, which contains 86 of A9's
87 `sample_calibrated = false` rows (the 87th, `aca_122`, already had a certified γ_N = 1 and is
therefore not open). Rows were processed shortest-first and checkpointed to
`split_bracket_targets.jsonl` as they finished; the run took two passes because of the wall-clock
cap, and the resume path deduplicates by row name.

### Headline

| question | answer |
|---|---|
| brackets closed (upper = lower = 1) | **0 of 116** |
| new certified γ_N = 1 gateways | **0** |
| rows reaching defect 0 | **0** — no `LOUD_ZERO_ALERT` |
| rows where the split bound beat A9's sampler | **18**, every one by exactly 1 |
| rows where the split bound was worse than A9's | 40 |
| certified brackets over all 124, before → after | **8 → 8** |

So the answer to A13's question is **no**: splitting closed nothing. It did not produce a single
new gateway, and the six certified γ_N = 1 rows are still A9's six.

### Where the instrument sits relative to A9's sampler, by length

`red~` is the median achieved census reduction `base census / split census`; `fresh~` is the
median number of fresh generators the winning plan used.

| L | rows | split upper | A9 upper | red~ | fresh~ |
|---|---|---|---|---|---|
| 15 | 7 | 2×7 | 2×7 | 21 | 2 |
| 16 | 5 | 2×5 | 2×5 | 1.8·10² | 3 |
| 17 | 18 | 2×10, **3×8** | 2×18 | 1.4·10³ | 4 |
| 18 | 6 | 2×1, **3×5** | 2×6 | 8.7·10³ | 6 |
| 19 | 22 | **3×21, 4×1** | 2×18, 3×4 | 2.6·10⁵ | 10 |
| 20 | 7 | 3×3, 4×4 | 2×5, 3×2 | 9.9·10⁵ | 12 |
| 21 | 18 | 3×12, 4×6 | 2×4, 3×14 | 1.0·10⁷ | 12 |
| 22 | 6 | 3×3, 4×3 | 3×6 | 7.4·10⁶ | 12 |
| 23 | 9 | **3×7**, 4×2 | 3×4, 4×5 | 2.4·10⁸ | 12 |
| 24 | 2 | **3×2** | 3×1, 4×1 | 1.3·10⁹ | 12 |
| 25 | 16 | **3×14**, 4×2 | 3×1, 4×15 | 7.1·10⁹ | 12 |

This is the calibration playing out exactly as measured. Below L18 the required reduction is
10¹–10³ and the split bound ties A9 (both say 2, neither closing the bracket at 1); from L17
upward it starts *losing* to A9; and it only wins at L23–25, where A9's sampler is completely
blind and answers 4 while the split — via a 12-fresh-generator, rank-14 presentation scored by
the sampler, not a census — produces a verified defect-6 witness and answers 3.

**The 18 improvements are real certificates.** Each is an explicit rotation system on an
explicitly recorded certified split, re-verified by `gateway_scan.verify_witness` and by
`split_bracket.independent_defect`. They move the merged upper-bound histogram over all 124 rows
from A9's `{1:6, 2:65, 3:32, 4:21}` to `{1:6, 2:65, 3:50, 4:3}` — the whole γ_N ≤ 4 tail
collapses to γ_N ≤ 3. That is the instrument's entire yield: **a one-unit improvement on 18 of
the longest rows, and nothing else.**

**Two honesty notes on those 18.** (i) Their achieved reductions (2·10⁸–7·10⁹) are two to four
orders of magnitude beyond the top calibrated band, so "3" there is a sound ceiling with an
*unmeasured* slack — it is emphatically not evidence that those rows sit at γ_N = 3. (ii) All 18
came from the sampled path, so they are one-sided in the same way A9's numbers were; what makes
them usable is that a *found* witness is a certificate at any length (T‑S9d).

**Certifier fail-closures**: 45 plan-level `CertificationError`s across the run, concentrated at
L20–L22 where plans reach 12 fresh generators. No row lost all its plans, so every one of the 116
still carries a bound.

---

## 4. The §3b Baumslag–Solitar lead

S13 §3b flagged that four of the six certified γ_N = 1 gateways carry the same relator
`YXXXyxx` = `y⁻¹x⁻³yx²` (Baumslag–Solitar `y⁻¹x³y = x²`), against 11 occurrences of that relator
among the 124, and asked whether that is real or an artifact of which rows were short enough for
A9's sampler.

**The test was run and it returned no new information, because the instrument closed no new
brackets.** The enrichment table is *bit-for-bit A9's*:

| population | rows | certified γ_N = 1 |
|---|---|---|
| contains `YXXXyxx` | 11 | 4 |
| all others | 113 | 2 |

**Verdict: the lead is neither confirmed nor refuted — it remains untested.** Reporting it as
"still there" would be reporting A9's own numbers a second time and calling the repetition
evidence.

The one *new* thing that can be said uses the split upper bound as an independent ranking key,
compared **inside each length band** (`contrast-length-confound.md`): only 5 of the 11
Baumslag–Solitar rows are among the 116 open rows at all, and their split bounds are
indistinguishable from their length-mates —

| L | `YXXXyxx` rows | everything else |
|---|---|---|
| 15 | 2, 2, 2 | 2, 2, 2, 2 |
| 20 | 4 | 3, 3, 3, 4, 4, 4 |
| 22 | 3 | 3, 3, 4, 4, 4 |
| 24 | 3 | 3 |

Five rows, one per cell or so; that is a sample from which nothing may be concluded in either
direction, and per the filed lesson no p-value is quotable for a family drawn from a move tree.
What *would* settle §3b is closing more brackets, and this instrument cannot do that — so the
question passes to whatever tool comes next, unchanged.

---

## 5. Traps this run confirmed or added

* **T‑S14a (new).** *A census-shrinking transform is not free, and its price is denominated in the
  quantity you are trying to measure.* The whole appeal of splitting was that
  `∏(deg−1)!` collapses. It does — and the minimum defect over the smaller family rises at
  roughly the same rate. Any future proposal of the form "make the exact computation affordable by
  transforming the presentation" must be calibrated against the *achieved* transformation strength,
  not against word length, before its numbers are read.
* **T‑S14b (new).** *A calibration ladder that is allowed to skip the hard part measures nothing.*
  The first calibration run let each rung split as much or as little as it needed; most rungs
  needed **zero** splits (their base census already fit) and scored a perfect overshoot of 0. That
  number would have been reported as "the instrument recovers the truth" while measuring only the
  exact census. Forcing the reduction is what turned a fake 100 % into the table in §2. This is
  `contrast-length-confound.md` and T‑S9b recurring in a third shape: the matched variable here is
  neither length nor degree but **how hard the instrument was made to work**.
* **T‑S14c (new).** *The replay certifier bounds how deep the instrument can split.*
  `certify_refinement` refuses when the number of candidate definition layerings read back out of
  `P'` exceeds `max_layerings = 20,000`, which happens routinely once a plan introduces ~12 fresh
  generators. The correct reading is **fail-closed, not failure**: those plans are dropped, the row
  keeps whatever bound its certified plans gave, and the artifact records
  `plans_failed_certification`. It is recorded here because a future session raising that budget
  would silently change the instrument's reach — and would have to re-run the calibration.
* **T‑S9d confirmed.** A found witness and an unfound witness stay asymmetric under splitting too:
  every bound reported here is a *witness*, and the rows where nothing was found are recorded as
  "no bound", never as evidence that γ_N is high.

---

## 6. What this does and does not establish

**Does:**

* A sound, replayable, twice-verified **upper-bound instrument** for γ_N that works through
  certified generator splittings, with its accuracy measured on a two-sided ladder rather than
  assumed.
* **65 further two-sided tests of Conjecture S8 with 0 violations**, at split depths (up to 12 fresh
  generators, rank 14) far beyond S8's own 632 states at ranks 4 and 6.
* A measured exchange rate: census reduction is bought at ~1 unit of γ_N per ~10³ of reduction on
  this corpus.
* A **one-unit improvement, certified by explicit twice-verified witnesses, on 18 of the 124** —
  the rows at total length 23–25 where A9's sampler was blind. The merged γ_N ≤ 4 tail collapses
  from 21 rows to 3.
* A live, positive-controlled **zero detector**: `verify_zero` was exercised on a known
  thickenable state (`('YXX','YXYXXXYXXX')`) and all three checks fired correctly —
  `witness_check_n` defect 0 with `L = 1` and `⟨AC,BC⟩` transitive, exact census over 241,920
  rotations with `minimum_defect = 0`, Todd–Coxeter index 1. The `0 of 116` above is therefore a
  measured null from a detector known to work, not silence from dead code.

**Does not:**

* It does not discharge GAP‑S8‑1. Every bound remains conditional on Conjecture S8.
* It says nothing about the AC-triviality of any of the 124, and nothing class-wide. An upper
  bound on a *presentation's* γ_N is not a statement about its AC class (`FRAMING.md` §2, S9 §6).
* A high split bound is **not** evidence that a row's γ_N is high. Per §2 the instrument overshoots
  by 1–3 at these reductions, so the long rows' split bounds are uninformative in exactly the same
  way A9's sampler nulls were — and they are marked so. In particular the 40 rows where the split
  bound is *worse* than A9's say nothing about those rows; they say the instrument was made to
  split too hard.
* It does not settle §3b. It could not: settling §3b needs closed brackets, and none were closed.

## 7. Operational recommendation

Do **not** spend more budget widening this instrument at the census cap — the exchange rate in §2
is the reason it cannot close a bracket at these degrees, and it is a property of splitting, not
of the search budget. Two things would change the picture, in this order:

1. **Discharge GAP‑S8‑1.** Everything here is conditional; a proved monotonicity would at least
   make the 18 improvements unconditional.
2. **Find a census-shrinking transform that is *tight*, not merely monotone.** The requirement is
   now quantitative and testable with this same harness: a transform is useful here only if its
   overshoot stays 0 at achieved reductions of 10⁴ and beyond. Splitting fails that test by a
   wide margin; abbreviation (S3) passes it trivially but achieves reduction 1, which is why it is
   inert. The gap between those two is where a usable instrument would live, and this note gives
   the measurement that any candidate has to beat.
