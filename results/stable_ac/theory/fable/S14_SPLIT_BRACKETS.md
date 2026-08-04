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
| `results/stable_ac/fable/split_bracket_summary.json` | closures, merged ranking, Baumslag–Solitar test |

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
bound. **0 violations in 65 measured cells** (36 cells on γ_N = 0 rungs, 56 on γ_N = 1, 8 on
γ_N = 2 — counted per cell). That is not a proof of GAP‑S8‑1, but it is 65 more instances on top
of S8's 632.

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

<!--TARGETS-->

---

## 4. The §3b Baumslag–Solitar lead

<!--BS-->

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

**Does not:**

* It does not discharge GAP‑S8‑1. Every bound remains conditional on Conjecture S8.
* It says nothing about the AC-triviality of any of the 124, and nothing class-wide. An upper
  bound on a *presentation's* γ_N is not a statement about its AC class (`FRAMING.md` §2, S9 §6).
* A high split bound is **not** evidence that a row's γ_N is high. Per §2 the instrument overshoots
  by 1–3 at these reductions, so the long rows' split bounds are uninformative in exactly the same
  way A9's sampler nulls were — and they are marked so.
