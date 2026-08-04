# S21_AUDIT — adversarial audit of `S21_MATCHED_NEGATIVE.md`

Branch `claude/stable-ac-conjecture-stabilization-rwo9as`. **This branch must be merged into
`fable/proof` by the user.** No commit, no push, no PR from this audit. New files only;
nothing under `experiments/` or `ac_solver/` was modified and no existing `.md` was edited.

**Timing note, because it matters for how to read this file.** The audit was commissioned
against S21 as of commit `871cf87`. While its experiments were running, the S-line itself
retracted the S21 headline in `6979205` (T-S20: the control escapes through a length region
AK(3) cannot enter). This audit was written independently, reached the same mechanism from a
different direction, and is left as an independent check rather than rewritten to agree.
Where it agrees, it agrees on data the retraction did not use.

---

# VERDICT: **RETRACT** — concurring with T-S20, on independent evidence, and extending it

The retraction is **correct and I confirm it from data it does not use**. But my route to it
was the opposite of the one the brief anticipated, and the difference is the useful part:

* **The structural "fourth costume" does not exist.** I hunted it hard — the relator `YYXyx`
  shared by all five controls, the single Miller–Schupp family, the abelianised matrix
  (every control has a relator abelianising to a *generator*; AK(3) has none), and the
  relator-length shape (AK(3) is 6+7; the controls are 5+8 or 5+7). I built three AC-trivial
  defect-4 controls **off the ladder**, sharing no relator with it, with **no unit
  abelianised row**, one of them matched to AK(3) on **shape 6+7 as well**. All three score
  **8/8**. Pooled: **59/64** over eight presentations from two unrelated sources. **None of
  the structural variables is the confound.**
* **The confound is the one T-S20 names, and my off-ladder controls show it too.** Requiring
  only that the witness end back in band (`length ≥ root`), my two length-13 off-ladder
  controls collapse from 16/16 to **3/16 = 0.19**; across all three (including the length-12
  one) 8/24 = 0.33 — the same collapse the retraction measured on the ladder controls, now
  replicated on a control family with no relator, no generator-shape and no provenance in
  common with them.
* **Chain-level confirmation, which the retraction flags as missing.** S21's §0 correctly
  warns that "the witness being back in band does not mean the *chain* stayed in band". I
  replayed one control hit end to end with a parent-tracking clone of `hunt`: the full length
  trace is `13, 12, 15, 18, 17, 11, 14, 17, 10, 11, 15, 17, 14, 9, 8, 7` and the certificate
  is created at total length **7**. The chain does not stay in band. Every one of its 15
  steps was independently re-verified as a legitimate AC move, and the hit's `minimum_defect`
  is 0 by exact census — so the hit is **real** and is a genuine **creation** (`4 → 2 → 0`).
  It is real *and* it is out of band. Both at once is exactly T-S20.

So the correct summary of the whole line is sharper than "the control was mismatched": **the
control was matched on every structural axis this audit could measure, and it still was not
comparable.** That is the strongest possible form of T-S20's closing point — *this is not a
fixable control design* — and it is worth recording that the matching was pushed to
exhaustion before the route was abandoned, so no future session re-opens it hoping a better
structural match exists. It does not.

**Two defects are independent of the retraction and still need fixing**, because the
surviving parts of S21 and the retraction's own arithmetic rest on them:

* **B1.** Two of the three artifacts §4/§7 cite for the AK(3) null **still do not exist**
  (`date -u` = 2026-08-04 10:09:46Z); those runs are still executing. 18 of the 34 AK(3)
  trials are console readings, not artifacts. §7 marks them "**measured**".
* **B2.** §5.4's "the 40 control trials are independent randomized restarts" is **false**:
  all five runs used `--seed 991`, so the 40 trials are 8 RNG streams reused five times. The
  retraction's own `19/24` and `8/24` inherit this.

---

## 0. What I did

| check | tool (all new files) | artifact |
|---|---|---|
| rank-2/3/4 exact defect of AK(3) + the five controls, abelianised rows, shapes | `experiments/stable_ac/fable/s21_audit_probe.py --mode defects` | `results/stable_ac/fable/s21_audit_defects.json` |
| independent defect-4 scan of 240 solved-ladder members | same, `--mode scan` | `results/stable_ac/fable/s21_audit_scan.json` |
| build AC-trivial defect-4 controls outside the ladder family | `experiments/stable_ac/fable/s21_audit_gen_replay.py --mode gen` | `results/stable_ac/fable/s21_audit_gen.json` |
| replay one control hit chain, verify every step is an AC move, census the hit | same, `--mode replay` | `results/stable_ac/fable/s21_audit_replay.json` |
| AK(3) starvation instrumentation, two trials at seed 811 | same, `--mode replay` | `results/stable_ac/fable/s21_audit_ak3_trial0.json`, `..._trial1.json` |
| the strongest single test: hunt on non-`YYXyx`, no-unit-row defect-4 controls, one shape-matched 6+7 | `s12_hunt --target …` (unmodified, distinct `--out`) | `results/stable_ac/fable/s21_audit_nonms_A.json`, `..._B.json`, `..._C67.json` |

---

# Findings

## 1. [BLOCKING, survives the retraction] Two of the three artifacts behind the AK(3) null do not exist

> §4: "`s12_ak3_hi_k1` (its depth-0 row) | 8,000 | 12 | **0**" and "`s12_ak3_depth_ladder`
> (its depth-0 row) | 2,000 | 6 | **0**"
>
> §7: "§4 AK(3) 0/34 | three runs, artifacts `s12_ak3_hi_k0.json`, `s12_ak3_hi_k1.json`,
> `s12_ak3_depth_ladder.json` | **measured**"

**What is wrong.** `results/stable_ac/fable/s12_ak3_hi_k1.json` and
`results/stable_ac/fable/s12_ak3_depth_ladder.json` do not exist.
`s12_hunt.cmd_target` writes its JSON only after the *last* depth in `range(kmax+1)`
completes (`s12_hunt.py:308-310`); both runs have `kmax > 0` and both are still executing
(`ps` at 10:09:46Z: PID 21015 `--kmax 1 --seed 812`, PID 14686 `--kmax 5 --seed 907`). The
two depth-0 rows were read from a console line, so 18 of the 34 trials in "0/34" cannot be
reproduced or re-analysed from the repository. This matters *after* the retraction too: 0/34
is still quoted as the target-side figure the in-band control rate is compared against.

**Replacement wording** (§4, under the AK(3) table):

> Only `s12_ak3_hi_k0.json` is an artifact. The `hi_k1` and `depth_ladder` rows are **console
> readings from runs still in flight at the time of writing** — `s12_hunt` writes its JSON
> only after its last depth completes. The artifact-backed AK(3) null is **0/16 at 8,000
> nodes (seed 811)**; the pooled 0/34 is provisional until those files land.

and (§7):

> | §4 AK(3) 0/16 | one run, artifact `s12_ak3_hi_k0.json` | **measured** |
> | §4 AK(3) 0/34 pooled | two of three runs still executing, no artifact written | **provisional — console reading only** |

## 2. The structural confounds are NOT the mechanism — three off-ladder controls, one shape-matched, all 8/8

> §5.3: "All five share the first relator `YYXyx` and come from the same solved-ladder
> family. The effective number of independent controls is smaller than five — possibly much
> smaller."

**What is wrong.** This was the right worry and it is **tested and refuted**. Three
AC-trivial rank-2 defect-4 controls were built by an AC walk from `⟨x,y | x,y⟩` (AC-trivial
by construction, with an explicit witness chain), selected to share **no relator** with the
ladder family and to have **no unit abelianised row**. All three root defects were re-censused
exactly and all three roots are `NOT_SPHERICAL`, so all three are creation controls, not
survival controls (T-S19):

| new control | shape | abelianised rows | det | rank-2 exact defect (census) | trials | hits |
|---|---|---|---|---|---|---|
| `('yxYXYYx','xYYYx')` | 5+7 | `[[1,-2],[2,-3]]` | 1 | **4** (17,280) | 8 | **8** |
| `('YxYXX','yyXYYxYX')` | 5+8 | `[[-1,-2],[-1,-1]]` | −1 | **4** (86,400) | 8 | **8** |
| **`('xyXXXyx','XyxyyX')`** — shape-matched to AK(3) | **6+7** | `[[-1,2],[-1,3]]` | −1 | **4** (120,960) | 8 | **8** |

Identical protocol (`--nodes 8000 --trials 8 --controls 2 --control-trials 3 --kmax 0
--headroom 4 --seed 991`); all three runs' internal controls scored 6/6. The third matches
AK(3) on group, rank, total length, relator shape 6+7, `minimum_defect` 4 (`γ_N = 2`) and
absence of a unit abelianised row — and still hits 8/8.

**Why this is worth keeping after the retraction.** It closes the search for a structural
fourth costume. Neither the shared relator, nor the Miller–Schupp family, nor the abelianised
shape, nor the 5+8-versus-6+7 split explains the control rate. Any future session tempted to
answer T-S20 with "we just need a better-matched control" should read this row: the match was
pushed to every axis the instrument can see, and comparability did not follow.

**Replacement wording** (§5.3):

> **The five ladder controls are not five independent presentations — but that is not the
> problem with them.** Three further defect-4 controls built outside the family —
> `('yxYXYYx','xYYYx')`, `('YxYXX','yyXYYxYX')` and `('xyXXXyx','XyxyyX')`, AC-trivial by
> construction from `⟨x,y|x,y⟩`, sharing no relator with the ladder, with no unit abelianised
> row, the last matched to AK(3) on relator shape 6+7 — score 8/8, 8/8 and 8/8 on the
> identical protocol (`S21_AUDIT` §2). The pooled control rate is 59/64 over eight
> presentations from two unrelated sources. Family membership is not the confound; the
> length-band exit (§0, T-S20) is.

## 3. Independent replication of the in-band collapse, on the off-ladder controls

**What this adds.** The retraction measures the in-band collapse on the five ladder controls
(19/24 → 8/24). The same test on my three off-ladder controls, which share nothing with them:

| control | root length | raw hits | witness lengths | witness `≥ root` |
|---|---|---|---|---|
| `('yxYXYYx','xYYYx')` | 12 | 8/8 | 4, 8, 11, 12, 12, 15, 19, 20 | 5/8 |
| `('YxYXX','yyXYYxYX')` | 13 | 8/8 | 7, 7, 8, 10, 11, 11, 13, 18 | 2/8 |
| `('xyXXXyx','XyxyyX')` | 13 | 8/8 | 3, 5, 6, 7, 9, 11, 11, 13 | 1/8 |
| **length-13 only** | 13 | **16/16** | | **3/16 = 0.19** |
| **all three** | | **24/24** | | **8/24 = 0.33** |

The collapse reproduces on a second control family, and on the length-13 pair it is steeper
than on the ladder (0.19 against 0.33). T-S20 is therefore not an artifact of the
Miller–Schupp source.

**Bound direction, stated because this is the trap that recurs here:** every number in this
table is produced by a **witness constructor**, so each bounds `Γ(P) = min{γ_N(Q) : Q ~_st P}`
from **ABOVE** for the control concerned. Nothing here bounds anything about AK(3) from
below, and the in-band rate is a statement about the *instrument's reachable region*, not
about AK(3)'s class.

## 4. Chain-level confirmation of T-S20, and end-to-end verification that a control hit is real

> §0 (retraction): "The witness being back in band does not mean the *chain* stayed in band —
> it may dip and return."

**Measured.** Target `('YYXyx','YXYXXyxx')`, trial 5, seed 991, 8,000 nodes, headroom 4,
reproduced exactly (`pops = 183`, same reported state) with a parent-tracking clone of `hunt`
having the identical RNG call order:

```
[ 0] len=13 defect=4  ('YYXyx','YXYXXyxx')   <- root, exact census defect 4 (gamma_N = 2)
[ 1] len=12 defect=2  [ 2] len=15   [ 3] len=18   [ 4] len=17
[ 5] len=11 defect=2  [ 6] len=14   [ 7] len=17   [ 8] len=10 defect=2
[ 9] len=11 defect=2  [10] len=15   [11] len=17   [12] len=14 defect=2
[13] len= 9 defect=2  [14] len= 8 defect=2
[15] len= 7 defect=0  ('xxYx','Yxx')         <- hit, exact census defect 0 (gamma_N = 0)
```

* **The hit is real.** Independent exact factorial census on `('xxYx','Yxx')` returns
  `minimum_defect = 0`, agreeing with the run's `r1c_v2_solver` verdict. The 16-state chain
  was recovered and **all 15 steps independently re-verified** as
  `r_i ← cyclered(r_i · u r_j^{±1} u⁻¹)` or `r_i ← r_i⁻¹`, by a checker sharing no code with
  `slides`. So the hit is genuinely in the control's AC class.
* **It is a creation, not a survival** (T-S19 passes): root defect 4 → hit defect 0, trace
  `4 → 2 → … → 2 → 0`, the two `γ_N` units §2 claims.
* **And the chain leaves the band and never returns**: minimum length 7, certificate at 7.
  This is the chain-level version of the evidence the retraction could only infer from
  witness lengths, and it confirms it.

## 5. §5.4's independence claim is false — one seed drives all 40 trials (and the retraction's 24)

> §5.4: "The 40 control trials are independent randomized restarts …"

**What is wrong.** All five control artifacts record `"seed": 991`. In
`s12_hunt.repeat_hunt` (`s12_hunt.py:262`) the per-trial stream is
`random.Random(seed + 7919·t + 104729·kstab)` with `kstab = 0`, so trial `t` uses
`Random(991 + 7919·t)` **for every one of the five controls**. The 40 trials are 8 distinct
RNG streams reused five times. The retraction's `19/24` and `8/24` are drawn from the same 8
streams reused three times. The conclusion of §5.4 — no p-value is computable — is right; its
premise is wrong.

**Replacement wording:**

> **No p-value, and none is computable.** The 40 control trials are **not** 40 independent
> draws: all five runs used `--seed 991`, so trial `t` uses the same stream
> `Random(991 + 7919·t)` on every control — 8 distinct streams reused across five
> presentations, and the same 8 reused across the three length-13 controls in §0. Even were
> they independent, the per-trial success probability is target-specific, so the control's
> rate is not AK(3)'s null hypothesis.

## 6. §3 — the surviving section — is missing the number its use in §2 requires

> §3 table: "| AK(3) | NOT_SPHERICAL | defect **4** | defect **4** | defect **4** |"
> §1: "reading the defect off the **stabilized** form (legitimate because stabilization is
> machine-confirmed inert for `γ_N`, §3)"

**Why this still matters.** The retraction states that §3 is what survives S21. As printed,
§3's rank-2 column holds a *verdict*, not a defect, so the table demonstrates
rank 3 = rank 4 = rank 5 and says **nothing about rank 2 → rank 3** — the only step §2's
"defect read off the stabilized form" actually needs. The five controls' rank-2 defects appear
nowhere in S21.

**Measured here — the claim holds** (exact factorial census, this clone):

| presentation | shape | rank-2 defect (census size) | rank 3 | rank 4 |
|---|---|---|---|---|
| AK(3) `('xyxYXY','xxxYYYY')` | 6+7 | **4** (86,400) | 4 | 4 |
| `('YYXyx','YYxxxyXX')` | 5+8 | **4** (86,400) | 4 | 4 |
| `('YYXyx','YYxxyXXX')` | 5+8 | **4** (86,400) | 4 | 4 |
| `('YYXyx','YXYXXyxx')` | 5+8 | **4** (86,400) | 4 | 4 |
| `('YYXyx','YXXYxxx')` | 5+7 | **4** (17,280) | 4 | 4 |
| `('YYXyx','YXXXYxx')` | 5+7 | **4** (17,280) | 4 | 4 |

**Replacement wording:** put those numbers in the rank-2 column, and replace the §1
parenthesis with

> (and since the rank-2 defect is now measured directly for all six presentations, the
> defect-4 match does not rest on the inertness of stabilization at all — `S21_AUDIT` §6).

`minimum_defect = 2·γ_N` throughout: defect 4 is **`γ_N = 2`**.

## 7. Two extrapolations in §3 are written in the register of measurement

> §3: "*Adding generators alone does not move `γ_N` at all, at any rank.* AK(3) is still at
> `γ_N = 2` at rank 5, and would be at rank 20."
> §3: "A control verified non-thickenable at rank 2 stays non-thickenable however deep it is
> stabilized …"

**What is wrong.** "at any rank", "rank 20" and "however deep" are consequences of **T4**,
which §7 itself flags as *proved (A8, **unaudited**)*. The measurement covers ranks 2–5 on
three presentations (2–4 on six, after Finding 6). Since §3 is the section the retraction
preserves, its measured content and its extrapolated content must be separable.

**Replacement wording:**

> *Adding generators alone does not move `γ_N` at ranks 2–5, on every presentation tested.*
> AK(3) is at `γ_N = 2` at every rank measured, and **T4 (proved, unaudited) predicts this
> holds at every rank** — the measurement stops at rank 5. Likewise: a control verified
> non-thickenable at rank 2 was still non-thickenable at ranks 3–5, and T4 predicts it stays
> so at every depth; the ladder calibration is measured to depth 5 and asserted beyond it.

## 8. The AK(3) null did not starve — measured here, because the artifacts cannot show it

> §4: "Each of those runs carried its own non-thickenable controls, which scored 15/16, 12/12
> and 9/9 respectively — so the instrument was working in every run that produced a zero."

**What is wrong procedurally.** `s12_hunt.cmd_target` never records which controls it drew or
their root defects, and stores `stats` **only for trials that hit**
(`"target_rows": [r for r in t_rows if r["hit"]]`, `s12_hunt.py:300`). So a zero-hit AK(3)
run's artifact contains **no `pops`, no `decided`, no `undecided` at all** — exactly the
instrumentation `experiments/lessons/instrument-the-search-before-reading-its-null.md`
requires before any null may be read. And `hunt` returns a "hit" at `pops = 0` when the root
is already SPHERICAL, so an undetected already-`γ_N = 0` control would give a survival rate
(T-S19) invisibly. Both gaps are closed here, and both close in S21's favour — this finding
is a **defence**, and it survives the retraction because it is what stops "0/34" from being
dismissed as a starved search:

* **Internal controls**, reconstructed deterministically (`random.Random(seed)` →
  `load_ladder(400, rng, lo=L, hi=L)[:controls]`) and censused: every control of every cited
  run is `NOT_SPHERICAL` with root defect **2** — `hi_k0` (seed 811): `('YYYXyxyX','YYXyx')`,
  `('YYYXyyxx','YYXyx')`, `('YYYYxxyX','YYXyx')`, `('YYYXyyx','YYXXyx')`; `hi_k1` (812) and
  `depth_ladder` (907) likewise. **No survival control anywhere.**
* **Starvation**: AK(3) trials 0 and 1 at seed 811, 8,000 nodes, re-run with the tracked
  clone — `pops = 8000 / 8000` (budget fully consumed), `decided = 2557` and `2408`,
  `undecided = 0`, `restarts = 1361` and `1399`. **The AK(3) searches did not starve.**

**Replacement wording** (§4):

> Each of those runs carried its own controls. Their identities are not stored in the
> artifact, so they were reconstructed from the seed and censused in the audit
> (`S21_AUDIT` §8): all are `NOT_SPHERICAL` with root defect 2 — none is a survival control
> (T-S19) — and they scored 15/16, 12/12 and 9/9. The artifacts store `stats` only for trials
> that *hit*, so the AK(3) zeros carry no `pops`/`decided` record; two `hi_k0` trials re-run
> in the audit reached `pops = 8000` with `decided ≈ 2,500` and `undecided = 0`, so the
> searches consumed their budget rather than starving.

## 9. "8,000 nodes" is a pop budget, not a state count — and 6 of the 34 trials ran at 2,000

> §6: "a thickenable member of its stable class is not reachable by this instrument within
> 8,000 nodes at depth 0"

**What is wrong.** (i) `nodes` bounds `pops`; a pop expands ≤ 10 sampled slides, most already
`seen`. Measured, an 8,000-pop AK(3) trial *decides* ≈ 2,500 distinct states, so the searched
region is ~2,500 states per trial, not 8,000. (ii) The pooled 34 includes the 6
`depth_ladder` trials at **2,000** nodes, which §4's table records but §6's sentence promotes
to 8,000.

**Replacement wording:**

> … is not reachable by this instrument in 28 trials of 8,000 pops and 6 of 2,000 pops at
> depth 0 — 8,000 pops decide ≈ 2,500 distinct states, and the 34 trials overlap heavily
> because they share a root.

## 10. "five at defect 4" is a property of one shuffle, not of the ladder

> §1: "Scanning harder — 240 solved-ladder members, lengths 11–18 … — found **78** with a
> defect number: 73 at defect 2 and **five at defect 4**."

**What is wrong.** `load_ladder` shuffles `data/ms640_solved.txt` with the caller's RNG and
takes the first `n`, so both 78 and five are sample statistics. An independent 240-sample
here (seed 20260804) returned **96 with a defect number and a different five**:
`('YYXyx','YXYXXyxx')`, `('YYXyx','YXXyxxYx')`, `('YYXyx','YXXXYxx')`, `('YYXyx','YXXYxxx')`,
`('YYXyx','YYxxyXXX')` — four shared with S21's, one new, one of S21's absent. The defect-4
subfamily is not exhausted.

**Replacement wording:**

> … found 78 with a defect number: 73 at defect 2 and five at defect 4. Both counts are
> **sample statistics** — `load_ladder` shuffles the 640-member file, and a second
> 240-sample returns a different, overlapping five (`S21_AUDIT` §10).

## 11. A structural fact about the control source, for the record

Every S21 control has a relator abelianising to a **generator** (`YYXyx ↦ (0,−1)`); AK(3)'s
rows are `(1,−1)` and `(3,−4)`, with no unit row. This is not incidental to the five: **all
640 members of `data/ms640_solved.txt` have a unit row** (measured 640/640), because the
Miller–Schupp first relator is `x⁻¹yⁿxy^−(n+1)`. `s12_hunt.load_ladder` — the *only* control
source the instrument has — is structurally incapable of matching AK(3) there, or on the 6+7
relator shape. That is the same shape of defect as T-S19: an axis the control family cannot
vary, under a comparison that reads it as matched.

Finding 2 shows both axes can be matched off-ladder and that neither is the confound. Two
supporting bounded searches (each bounds a **frequency from ABOVE**; neither is a
nonexistence proof):

* over 502 no-unit-row AC-trivial rank-2 states of total length 12–13, exact census gave
  defect 4 at 5+8 (4 of 219) and 5+7 (1 of 87);
* over 429 AC-trivial states of shape **6+7** at length 13, defect 4 occurred **once** —
  `('xyXXXyx','XyxyyX')`, the control used in Finding 2 — against 416 at defect 2.

AK(3)'s (shape 6+7, defect 4) combination is rare among AC-trivial presentations (≈1 in 429
here against ≈1 in 50 at 5+7/5+8) but **not unique**; and rarity of a *control* is not a
property of the *target*.

---

## Numbers in §4 that DO reproduce

All five control rows (7/8, 4/8, 8/8, 8/8, 8/8), the pooled 35/40 = 0.875, the length-13-only
19/24 = 0.79, and every recorded budget (`nodes 8000`, `kmax 0`, `headroom 4`, `seed 991`,
`controls 2`, `control-trials 3`, control 6/6) match the five `s12_d4ctl_*.json` artifacts
exactly. The AK(3) `hi_k0` row (8,000 nodes, 16 trials, 0 hits, controls 15/16, seed 811)
matches `s12_ak3_hi_k0.json` exactly. §2's defect match is correct and is now verified at
rank 2 (Finding 6). Only the two absent artifacts (Finding 1) fail to reproduce, for want of
a file.

## What must not be inferred from this audit

Nothing here bounds `Γ(AK(3)) = min{γ_N(Q) : Q ~_st AK(3)}` from **below**, and nothing here
is evidence for or against the AC or stable AC conjecture. Every instrument used —
`s12_hunt`, the cut-scheme solver, the factorial census as used here — produces **witnesses**,
so each bounds `Γ` from **ABOVE**. The three 8/8 runs raise the audit's own control rate; they
do not move AK(3), and under T-S20 they do not calibrate it either.
