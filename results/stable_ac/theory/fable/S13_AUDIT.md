# S13_AUDIT — adversarial audit of `S13_SYNTHESIS.md`

Branch `claude/stable-ac-conjecture-stabilization-rwo9as`. **This branch must be merged into
`fable/proof` by the user.** No PR opened (`FRAMING` trap 10). Audit only: this file adds
`experiments/stable_ac/fable/audit_s13_gateway_recheck.py` (new, throwaway) and edits nothing
under `experiments/` or `ac_solver/`.

Audited against the working tree at commit `c851897` ("propagate the retraction into S13
section 1 and S15 section 5"). **The file moved twice while this audit ran** — §3z-bis was
retracted by the session at `4e22f1d` — so §§1 and 6 below record what I derived
independently *before* that retraction landed, as corroboration rather than as a new finding.

---

# VERDICT: **AMEND**

Not REJECT: the load-bearing measurements I could re-run all reproduce exactly (§0 below),
including all six γ_N = 1 gateways, `C1`, the rank-12/13 histograms, the A7 ladder and the
Baumslag–Solitar counts. Not ACCEPT: the newly added §0 — the paragraph that *overrides*
everything else in the file — commits the repo's most expensive recurring error
(`parallel-runs-and-bound-direction.md`) in its second-to-last sentence, and the blanket claim
it imports from `S15` §5 is refuted by an artifact this same session committed. §4a is stale
against data committed at `8bbf9b1`. Seventeen findings follow, ordered by severity.

---

## 0. What I re-ran and what reproduced (no finding — recorded so the amendments are trusted)

Every number in this section was recomputed in this clone with the repo's own tooling, not
read from a summary file.

| claim | tool | result |
|---|---|---|
| six gateways, lower half γ_N ≥ 1 | `disconnected_split.decide_pair` | **6/6 `NOT_SPHERICAL`**, exhaustive, `IN_SCOPE`; AK(3) likewise |
| six gateways, trivial group | `coset_enum.is_trivial_group` | **6/6 `COMPLETE`, index 1** (+ AK(3)) |
| `aca_117` upper half | exact census, 518,400 rotations | `minimum_defect` **2** ⇒ γ_N = 1 exactly |
| other five, upper half | `witness_check_n` on the stored `sample.witness` | **`WitnessError: defect 2 != 0`** on all five, and I confirmed by reading `check_witness_n` that the **compatibility test (step 2) runs and passes *before* the defect test (step 3)** — so S13's "Compatibility passed in every case" is not a short-circuited claim |
| AK(3) | exact census, 86,400 | `minimum_defect` **4** ⇒ γ_N = 2 |
| `C1` | census + Todd–Coxeter + `classify_support_n` | rank 13, all 13 multiplicities **3**, census **8,192**, `minimum_defect` **2**, TC index 1 / **481 cosets**, link **`NONPLANAR`**; census 0.14 s vs `classify_support_n` 3.0 s |
| §3z histogram and T-S17 table | `s4b_decided_summary.json` + row-by-row re-read of `s4b_decided.jsonl.gz` | exact match (45,111 decided; 527/40,100/4,484; sd-2 row 0/1,028/204) |
| §3b enrichment | `u124_sweep.jsonl` | **11 rows / 4 certified**, **113 / 2**, **8 / 4** and **36 / 2** at length ≤ 18 — exact |
| A7 depth ladder | `rank_n_ac_search_depth_ladder.json` | control `ak2ctl` **39 hits / 40 runs**, AK(3) **0 / 40**, both families starting at total length 13 and stabilised identically — **genuinely length-matched** (I initially mis-read the pooled `ladder_D` row as 39/80; it is not) |
| instrument-A positive ladder | `u124_calibration.json` | **54/55**, zero false negatives |
| ctrl2 control sources | exact census + TC | `('XyyXy','YxYYYxxY')`, `('yXYxx','YxxyXYxx')`, `('XYYXYYXY','yxxyy')` — all total length 13, all TC index 1, all `minimum_defect` **2** (γ_N = 1). S16's "the sharp controls are at defect 2" is correct |
| ctrl2 pool | row-by-row re-read of `s4b_ctrl2_decided.jsonl.gz` | 19,132 + 12,012 + 15,154 = **46,298** decided, **0** at defect 0 |
| 5b cubic-link arithmetic | by hand | 2N germs, 3N edges; `3N ≤ 6N−6` ⟺ `N ≥ 2`, so the sparsity certificate provably never fires — correct |

**And the §3z-bis retraction is correct.** Before `4e22f1d` landed I had independently
established the same thing from the artifacts: the control's rank-9 root
`('CXA','XEG','aYX','bxy','cXY','dXY','eDX','fXb','gFY')` has `minimum_defect` **0** (recomputed
here), so every one of the 759 "hits" is a *retained* certificate, never a created one, and the
event whose absence was reported for AK(3) (a two-unit descent) is **unobservable in the
control by construction** — its root is already at the floor. The per-cell rates also survive
band restriction (rank 12: control 759/49,352 = 1.54 %, AK(3) 0/43,382), so the retraction is
*not* a length confound; it is the deeper "the control could not have failed" confound. The
retraction text is accurate and I endorse it.

---

## FINDINGS

### F1 — CRITICAL. §0 asserts a class-wide absence as fact, in the paragraph correcting exactly that error. (line 41–42)

> "It is certificate-preserving and certificate-non-creating, so it can only settle a
> presentation that already has a thickenable member at rank 2 — **which AK(3) does not**."

**What is wrong.** "AK(3) does not [have a thickenable member at rank 2]" is a statement of
absence over AK(3)'s entire rank-2 AC class. Nothing establishes it. What is established is
(a) the presentation AK(3) itself has γ_N = 2 by exact census, and (b) bounded nulls — 0
thickenable in the 171,842-member depth-1 stable class (rank 3, AK(3)+z), and the 124,296-member
rank-2 matched harvest whose best find was a γ_N = 1 gateway. Those are
bounded searches; by `S15` §4 — cited two lines later in the same paragraph — a null on this
route "bounds nothing". Worse, the negation of this sentence, taken class-wide over all ranks,
is the *disproof* of the stable AC conjecture (`FRAMING` §2, second shape). Stating it as an
aside is the single most dangerous sentence in the file. This is
`parallel-runs-and-bound-direction.md` guard (1) verbatim: a "does not exist" resting on a
search.

**Recommended replacement.**

> "It is certificate-preserving and, in every regime measured here, certificate-non-creating,
> so it can only settle a presentation whose rank-2 root is *already* thickenable. AK(3)'s own
> rank-2 spelling has γ_N = 2 (exact census, 86,400 rotations), and no thickenable member has
> been found in the 124,296-member rank-2 matched harvest or the 171,842-member depth-1 stable
> class — bounded nulls, not an absence proof. Until such a member is exhibited by other means,
> this pipeline cannot settle AK(3)."

---

### F2 — CRITICAL. "no known move manufactures one" is refuted by this session's own committed artifact. (`S15_ONE_SIDEDNESS.md` §5, imported into S13 §0 as "certificate-non-creating")

> `S15` §5: "So the difficulty is not that certificates are scarce; it is that **no known move
> manufactures one**."
> S13 §0: "the chord + SPLIT pipeline created `γ_N = 0` **0 times in 93,638 opportunities**"

**What is wrong.** The S13 sentence is correctly scoped to the chord+SPLIT pipeline. The S15
sentence is not, and it is false. Evidence, recomputed here:

* `rank_n_ac_search_depth_ladder.json`, family `ak2ctl`. Base `("YYxxx","YxYxYxxx")`:
  total length 13, Todd–Coxeter index 1, exact census 120,960, **`minimum_defect` 2 — γ_N = 1,
  NOT thickenable.** At rank ceiling 2 the search reached `("YYxxx","xYx")` with
  **defect 0**, verified in the row's own `verification` block by `check_witness_n`, an
  independent defect rebuild and an exact 48-case census — **8 hits in 8 runs**, and 39/40
  across ceilings 2–6. That is AC1–AC3 manufacturing a certificate from a non-thickenable
  trivial-group root, forty times over.
* `S6_S8_S4_AUDIT.md` §1.7: AC2 **creates** on 58/313 = 18.5 % of non-thickenable
  trivial-group bases.

The correct scope is *this move set*, and S16 §6 already says so ("an instrument fact about
this move set and budget"). S15's blanket generalisation over-corrects and, if believed, would
retire the one route (`S12`'s AC2-weighted hunt) that the session's own flip census supports.

**Recommended replacement (S15 §5, last paragraph).**

> "So the difficulty is not that certificates are scarce; it is that *the chord + SPLIT cubic
> pipeline* never manufactures one — 0 creations in 91,409 decided states from four
> non-thickenable roots. Other move sets demonstrably do: on the A7 depth ladder a plain
> AC1–AC5 search created γ_N = 0 from the non-thickenable, AC-trivial, length-13 base
> `("YYxxx","YxYxYxxx")` (γ_N = 1 by exact census) in **39 of 40** runs, and A14 measures AC2
> creating on 18.5 % of non-thickenable trivial-group bases at total length 7–10. The
> instrument fact is about the cubic pipeline, not about the move set in general."

And in S13 §0, replace "It is certificate-preserving and certificate-non-creating" with
"**This pipeline** is certificate-preserving and, at every budget tried, certificate-non-creating
— unlike the general AC search, which created a certificate from a non-thickenable root in 39
of 40 A7 ladder runs."

---

### F3 — MAJOR. §0's "cannot" is contradicted by §1(i) three lines above it, and by 527 measured descents. (line 42)

> "**The cubic route cannot settle AK(3), and this retires it with a mechanism rather than
> with silence.**"

**What is wrong.** "Cannot" is a modal absolute derived from a bounded measurement, and the
mechanism it claims does not exist. §1(i), fourteen lines above, says the SPLIT move "**does**
lower γ_N — it is what took AK(3) from γ_N = 2 to … `C1` at γ_N = 1". `s4b_decided_summary.json`
records **527 states** in AK(3)'s own pool that descended from defect 4 to defect 2. So the
pipeline is demonstrably γ_N-**lowering**; what has never been observed is a descent that
reaches 0. A "mechanism" would need a monotonicity theorem, and `S15` §6 states plainly that
"no monotone quantity is currently known on this line".

**Recommended replacement.**

> "**On the evidence, the cubic route did not and probably cannot settle AK(3) at this budget:
> the pipeline lowered γ_N (527 descents 4 → 2, plus `C1` at γ_N = 1) but never reached 0 in
> 91,409 decided states from four non-thickenable roots.** This is a measured instrument
> limitation, not a proved obstruction — no monotonicity theorem covers the length-3 SPLIT
> (`S15` §6), so 'cannot' is not yet available."

---

### F4 — MAJOR. Two different totals for one fact, and one of them pools a denominator that is not a creation opportunity. (line 39; retraction banner; `S16` §4/§5; `S15` §5)

> S13 §0: "created `γ_N = 0` **0 times in 93,638 opportunities** across three ranks"
> S13 §3z-bis banner: "across **91,409** decided states from **four** independent
> non-thickenable roots, the cubic split search created γ_N = 0 **zero** times"

**What is wrong.** Both numbers appear in one document without reconciliation. 91,409 =
46,298 + 45,111 (the four non-thickenable roots) — coherent. 93,638 adds the rank-5 flip
census (1,470) *and* the **759 replayed control chains**. The 759 chains start at defect 0;
they were never opportunities to *create* a certificate, so including them inflates the
denominator with the one population where the event is definitionally impossible. That is a
smaller version of the error §3z-bis was just retracted for. Separately, "opportunities" counts
decided *states*, not moves, and those states share ancestors in a move tree — the correlation
caveat that `contrast-length-confound.md` rule 3 demands is present in S16 §6 but absent from
S13 §0.

**Recommended replacement (S13 §0).**

> "the chord + SPLIT pipeline created `γ_N = 0` **0 times in 91,409 decided states** descended
> from four independent non-thickenable roots at ranks 12–13 (plus 0 in 1,470 rank-5 flip-census
> opportunities), while remaining demonstrably able to *find* certificates that already existed.
> These states come from a move tree and are not independent draws, so the figure is a coverage
> count, not a probability."

Delete the "control hit chains (replayed) | 9 → 12/13 | 0 | 759" row from `S16` §4's table, or
relabel its denominator "chains from an *already thickenable* root — no creation was possible;
listed for completeness, excluded from the total".

---

### F5 — MAJOR. §4a is stale: it contradicts data committed at `8bbf9b1` and contradicts `S15` §4. (lines 421–449)

> "| `aca_11` | 15 | 0/8 = 0.00 | 0/8 | **uninformative** |"
> "| `aca_121` | 16 | 0/8 = 0.00 | 0/8 | **uninformative** |"
> "So **five of the six gateways have never been hunted at all, and none above depth 0**"

**What is wrong.** `results/stable_ac/fable/s12_gateway_hi_aca_{11,121,122,17}.json` (tracked,
committed at `8bbf9b1`/`c851897`) rerun the same targets at **8,000 nodes with 12 control
trials**:

| gateway | length | control (8,000 nodes) | target | null is |
|---|---|---|---|---|
| `aca_11` | 15 | **12/12 = 1.00** | 0/8 | **informative** |
| `aca_121` | 16 | 8/12 = 0.67 | 0/8 | moderately informative |
| `aca_17` | 17 | 7/12 = 0.58 | 0/8 | moderately informative |
| `aca_122` | 18 | 0/12 = 0.00 | 0/8 | uninformative even at 8× nodes |

So `aca_11` is a **second fully calibrated null**, not an uninformative row, and four of the six
gateways *have* now been hunted. `S15` §4 already quotes these numbers ("12/12 at length 15,
8/12 at length 16 and 0/12 at length 18"), so S13 — the synthesis — contradicts a sibling
document written after it.

**Recommended replacement.** Add the high-budget rows to the §4a table and replace the closing
sentence with:

> "So **two of the six gateways now carry calibrated nulls** — `aca_117` at 1,000 nodes
> (control 8/8, target 0/8) and `aca_11` at 8,000 nodes (control 12/12, target 0/8) — `aca_121`
> and `aca_17` carry partially calibrated ones (control 8/12 and 7/12), `aca_122` is
> uninformative even at 8× nodes (control 0/12), and `aca_30` has only its 1,000-node rung.
> None has been hunted above depth 0."

---

### F6 — MAJOR. §3a's headline ranking is dissolved by §1 of the same file and by `S15` §3. (lines 289–292)

> "**Six of AK(3)'s 123 unsolved siblings sit one unit closer to Lackenby's hypothesis than
> AK(3) itself does**"

**What is wrong.** The quantity that matters for Lackenby's hypothesis is the class minimum
`Γ(P) = min{γ_N(Q) : Q ~ P}`, and γ_N of a chosen representative bounds it only from **above**.
On that quantity AK(3) is *not* one unit further out:

* §1 of this same file, line 78: "a γ_N = 1 gateway found at rank 2 and length 14,
  `gateway_scan.json`" — I read the artifact: `("YYYXXyx","YXYXyxx")`, γ_N = 1, harvested from
  `ak3_matched_members.jsonl.gz`, i.e. **inside AK(3)'s own class**;
* `S15` §3 states the bracket outright: "**Current bracket. `0 ≤ Γ(AK(3)) ≤ 1`**";
* §3z of this file records **527** states of AK(3)'s stable class at γ_N = 1, and §1 records
  `C1` at γ_N = 1.

The six gateways' `Γ` is also ≤ 1. So the ranking compares *representatives*, not classes, and
says nothing about which class is closer. This is the same shape as the recurrence in
`parallel-runs-and-bound-direction.md`: an upper bound read as a floor, with the consequence
"send the search budget here".

**Recommended replacement.**

> "**Six of the 123 unsolved siblings have a rank-2 representative at γ_N = 1, where AK(3)'s
> own rank-2 spelling sits at γ_N = 2.** This is a statement about representatives, not about
> classes: γ_N of a representative bounds the class minimum Γ only from above, and AK(3)'s Γ is
> already bracketed `0 ≤ Γ(AK(3)) ≤ 1` (`S15` §3 — a γ_N = 1 member of its own class at rank 2,
> length 14, `gateway_scan.json`). What the six buy is a *cheap starting point*, not a closer
> class — and 39,108 states inside their classes have already been swept without a hit."

---

### F7 — MAJOR. §3a drops both qualifiers from the graft ceiling, turning a lemma about one move into a claim about the whole move set. (lines 289–290)

> "By the project's audited graft ceiling (**a graft lowers γ_N by at most 1**), a thickenable
> member is **only reachable from a γ_N = 1 state**."

**What is wrong.** `R3PRIME_GRAFT_CALCULUS.md` Thm G6, as `S9` §3 states it, is: "a single
**non-cancelling AC2** graft lowers γ_N by at most 1". `R3PRIME` line 21 and
`S6_MOVE_CLASSIFICATION.md` line 389 both record that **the cancelling case is outside G6's
stated domain**. The conclusion "only reachable from a γ_N = 1 state" additionally quantifies
over *every* move in the search's repertoire — AC1, AC3, free reduction, AC4/AC5, and (in the
high-rank work) the length-3 SPLIT — none of which G6 covers. `S6` line 553 records that a
slide "can raise γ_N by up to 2 (proved)", so the calculus is not uniformly 1-Lipschitz even in
the direction that is proved.

**Recommended replacement.**

> "By the project's audited graft ceiling (`R3PRIME` Thm G6: a single **non-cancelling AC2**
> graft lowers γ_N by at most 1), a thickenable member is only reachable from a γ_N = 1 state
> **along non-cancelling AC2 grafts**. No ceiling is proved for cancelling grafts, for AC3, for
> free reduction or for the length-3 SPLIT, so this is a heuristic for ordering targets, not a
> reachability theorem."

---

### F8 — MAJOR. Retraction hygiene: §5.7 re-quotes the 54.8 % headline that `contrast-length-confound.md` was filed to retire. (line 392)

> "AK(3)'s depth-1 stable class is 0 thickenable in 171,842 against **an AC-trivial class's
> 54.8 %** under the same operator"

**What is wrong.** `experiments/lessons/contrast-length-confound.md` exists specifically to say
that this number must not be the contrast: in the shared length band 14–21 the control's rate
is **0.147 %** (13/8,862), a factor of 370 lower, and the lesson's rule 1 is "report the
per-length table, always, and lead with the in-band comparison". S13 §4 item 2 even names this
lesson as "recurring in a file that cites it twice" — and then §5.7 quotes the retired number
without the in-band figure. I also re-read `contrast_length_matched.json` and found a fact
neither S13 nor the lesson quotes: `"distinct_parents_of_hits": 1`,
`"largest_parent_family": 14999` — **all 14,999 control hits descend from a single parent.**

**Recommended replacement.**

> "AK(3)'s depth-1 stable class is 0 thickenable in 171,842. The AC-trivial control's headline
> 54.8 % is not the comparison: restricted to the length band the two harvests share (14–21) the
> control's rate is **0.147 %** (13 in 8,862), and all 14,999 of its hits descend from a
> **single parent** (`contrast_length_matched.json`). The honest scale is '0 observed where ≈13
> would be expected at the control's in-band rate', with the caveat that the expectation is
> descriptive only."

---

### F9 — MODERATE. §3z contains a sentence the session has since falsified. (line 167)

> "there is **no positive control** — **no γ_N = 0 state at rank 12–13 is known to exist
> anywhere**, so the hunt's detection rate is unmeasured."

**What is wrong.** 759 such states were exhibited (`s4b_control_decided.jsonl.gz`), one verified
six ways. The §3z-bis *contrast* is retracted; the **existence** of those 759 is not, and is
the one durable thing that section produced. Leaving this sentence makes §3z and §3z-bis
mutually inconsistent.

**Recommended replacement.**

> "when this section was written there was **no positive control**; 759 γ_N = 0 states at rank
> 12–13 have since been exhibited (§3z-bis, whose *contrast* is retracted but whose existence
> claim stands). What remains unmeasured is the rate at which this search *creates* a
> certificate from a non-thickenable root — measured since at **0 in 91,409** — so the null
> below is calibrated for detection and uncalibrated for descent."

---

### F10 — MODERATE. §1(ii)'s mechanism sentence is contradicted by the table it introduces. (lines 46–47, 59–60)

> "The compatible census is `∏(deg−1)!`, so **what matters is the *ratio* ℓ/n** of total length
> to rank." … "**The decidable region is ℓ/n ≲ 3** — exactly the cubic regime."

**What is wrong.** With mean multiplicity `ℓ/n`, the census is ≈ `((ℓ/n − 1)!)^n` — it grows in
`n` at fixed ratio, so the ratio is not a sufficient statistic. The doc's own table and the n=60
artifact `s11_decidability.json` show the critical ratio **falling** with rank:

| rank | ratio at which decidability crosses ≈50 % (n=60 sweep) |
|---|---|
| 2 | between 6.5 (0.617) and 8.0 (0.000) |
| 3 | ≈ 5.3 (0.350) |
| 4 | between 4.0 (0.933) and 4.75 (0.167) |
| 6 | ≈ 3.7 (0.517) |
| 8 | between 3.1 (0.567) and higher |

"ℓ/n ≲ 3" is roughly the rank-8 threshold and understates rank 2 and rank 4 by a factor of two —
in the direction that flatters the high-rank narrative.

**Recommended replacement.**

> "The compatible census is `∏(deg−1)!` ≈ `((ℓ/n − 1)!)^n`, so at **fixed total length** more
> generators is dramatically cheaper — but the ratio is *not* the sufficient statistic: at fixed
> ℓ/n, higher rank is more expensive, and the ratio at which the census stops fitting the cap
> falls from ≈7 at rank 2 to ≈4.3 at rank 4 to ≈3.2 at rank 8. The cubic regime (ℓ/n = 3) is
> decidable at every rank measured; that is the correct statement."

---

### F11 — MODERATE. "3.5× S6's headline" is arithmetically wrong. (line 116)

> "an AC2 slide creates the Lackenby certificate 18.5 % of the time — **3.5× S6's headline**"

**What is wrong.** S6's published creation rate is **7.0 %** (the table three lines above says
so). 18.5 / 7.0 = **2.6×**. The 3.5× figure is 18.5 / 5.3, i.e. against the *unrestricted
control's* rate, not S6's headline. The same paragraph elsewhere calls the 5.3 % vs 7.0 % gap
"sampling noise", so the two readings cannot both stand.

**Recommended replacement.**

> "an AC2 slide creates the Lackenby certificate 18.5 % of the time — **2.6× S6's published
> 7.0 %, and 3.5× the matched unrestricted control's 5.3 %**"

---

### F12 — MODERATE. The flip-rate paragraph is promoted past the length band it was measured in. (lines 120–121)

> "**This is the strongest single reason to believe the certificate hunt is a viable method
> rather than a long shot**"

**What is wrong.** `S6_S8_S4_AUDIT.md` §1.7a stratifies the corpus by **total length 7–10** at
**rank 2**. AK(3) is length 13; the gateways are 14–18; the swept class members run to length 33.
The session's own new trap T-S15 (`S4B` §3.4) says: "*A move's flip census is a statement about
the corpus's rank, not about the move* … state the rank band the measurement covers, and
calibrate at the *large* end." The A9 calibration measures the sampler collapsing from 1.00 at
L13 to 0.00 at L19 — direct evidence that this regime does not extrapolate. Also, "AC2 is
net-positive in absolute terms (58 creates against 28 destroys)" compares counts over different
denominators (313 non-thickenable vs 133 thickenable bases); in AK(3)'s class, where thickenable
states are absent, the "destroys" column is irrelevant and the comparison carries no information.
A14 itself says only "*nearly* net-positive … on this corpus".

**Recommended replacement.**

> "On the presentations that actually matter, an AC2 slide creates the Lackenby certificate
> 18.5 % of the time **on a rank-2 corpus of total length 7–10** — the band the measurement
> covers. Whether that rate survives to length 13–18, where the targets live, is untested, and
> T-S15 (`S4B` §3.4) warns explicitly against the extrapolation. Read as: *the best available
> evidence that the certificate hunt is not a long shot, measured two length classes below the
> targets.*"

---

### F13 — MODERATE. Two of the ladder table's cells rest on 1 and 2 samples. (lines 51–57)

The table is `s11_ladder.json` and reproduces exactly, but per-cell `n` is 10 everywhere except
**`22|2` where n = 2** and **`22|4` where n = 1**. Both are printed as flat "0.00" beside cells
with n = 10.

**Recommended replacement.** Add a footnote directly under the table:

> "All cells are n = 10 except (length 22, rank 2) with **n = 2** and (length 22, rank 4) with
> **n = 1** — those two zeros are not measurements, they are single draws. 163 rungs total,
> `missed = 0` in every cell."

---

### F14 — MINOR. The median-census sentence silently switches artifacts. (line 59)

> "Median census at length 22: **1.3 · 10¹³ at rank 2 against 5,760 at rank 8**."

Those are the n = 60 `s11_decidability.json` medians (1.317·10¹³ and 5,760). The table
immediately above is `s11_ladder.json` (n = 10), whose length-22 medians are **1.45·10¹³** and
**1,920**. Both are real; mixing them in adjacent sentences invites a reader to check the wrong
file.

**Recommended replacement.**

> "Median census at length 22, from the wider n = 60 sweep (`s11_decidability.json`):
> **1.3 · 10¹³ at rank 2 against 5,760 at rank 8**."

---

### F15 — MINOR. "cyclically equal to AK(3)" is true only under the repo's inversion-closed canonical form. (line 72; repeated in `S15` §3)

> "returns `('XyxyXY','xxYYYYx')` — cyclically **equal to AK(3)**."

I checked: `xxYYYYx` *is* a cyclic rotation of `xxxYYYY`, but `XyxyXY` is **not** a rotation of
`xyxYXY` — it is a rotation of its **inverse**. The claim is defensible because
`ac_words.canon_rel` is documented as "lex-min over all rotations of `cyc_reduce(w)` **and of
its inverse**", and inversion is AC1, so `AK(3) ~_st C1` stands. But an auditor checking the
words naively finds the sentence false, and `S15` §3 leans on it for Proposition S15.3.

**Recommended replacement.**

> "returns `('XyxyXY','xxYYYYx')` — **equal to AK(3) up to cyclic rotation and inversion of the
> first relator** (one AC1 move), i.e. identical under `ac_words.canon_rel`."

---

### F16 — MINOR. §5 lead 3 quotes 64.29 % as a prior after `S4B` retracted exactly that use. (lines 359–363)

> "**The cubic regime.** 64.29 % of rank-4 cubic presentations of the trivial group carry a
> certificate…"

`S4B` §0 item 6 says in terms: "the 64.29 % thickenable fraction of `S4` §4 is a base rate over
tiny rank-4 AC-trivial presentations, **not** a prior for AK(3)'s descendants — the two cubic
forms actually found came out at γ_N = 1 and γ_N = 2, i.e. **0 of 2 thickenable**." The session's
own rank-12/13 measurements are 759/50,320 = 1.5 % (thickenable root) and 0/91,409
(non-thickenable roots). Quoting 64.29 % as motivation without that correction is a 40×
optimistic prior.

**Recommended replacement.**

> "**The cubic regime.** 64.29 % of *rank-4* cubic presentations of the trivial group carry a
> certificate — a base rate over tiny AC-trivial presentations and explicitly **not** a prior for
> AK(3)'s descendants (`S4B` §0.6). At rank 12–13 the measured rates are 1.5 % from an already
> thickenable root and **0 in 91,409** from non-thickenable ones. What survives as a lead is the
> normal form, not the density."

---

### F17 — MINOR. §5 lead 1 and §7 item 4 give opposite advice on Q(F2). (lines 353–357 vs 517)

> §5.1: "**Q(F2): is `~^{(1)} = ~^{(k)}`?** … Nothing in this session settles it." (listed first)
> §7.4: "The sharpest open *theory* question is **Q(F2) at k ≥ 2**. **Level 1 is blocked** — it
> reduces to the Panteleev–Ushakov conjecture — **so do not attack it.**"

A fresh session reading §5 first will attack the thing §7 forbids. Make §5.1 carry the
restriction.

**Recommended replacement (§5 lead 1, first sentence).**

> "**Q(F2) at k ≥ 2: is `~^{(1)} = ~^{(k)}`?** The bounded-stabilization filtration is untouched
> in the literature (A2, Q4). **Level 1 is BLOCKED** — it reduces to the Panteleev–Ushakov
> conjecture (`FRAMING` §3) — so only `k ≥ 2` is attackable."

---

## Sub-finding on §3b (no amendment required, but record it)

§3b is correctly labelled "a lead, not a result", correctly refuses a p-value, and its four
counts reproduce exactly. One residual the caveat paragraph does not name: **inside the ≤ 18
band the two groups are still not length-matched** — mean total length 15.25 (Baumslag–Solitar
rows) against 16.69 (others) — and the per-length breakdown is
`L14 1/2 · L15 1/4 · L16 1/1 · L18 1/1` for the BS rows against `L13 0/1 · L15 0/4 · L16 0/5 ·
L17 2/20 · L18 0/6` for the others, i.e. both "other" hits sit at L17, a length where the BS
group has no rows at all. Suggested one-line addition to §3b's "What this is not":

> "Even inside the ≤ 18 band the two groups differ in mean length (15.25 vs 16.69) and do not
> overlap at L17, where both non-BS hits sit — so the enrichment is not length-controlled at
> per-length granularity either."

## Sub-finding on §1(i) (no amendment required)

"bare AC3 conjugation **only destroys**" is supported (0 creates in the A14 corpus) but the
measured destroy rate on trivial-group bases is 5.8 %, not the 22–24 % an unqualified "only
destroys" evokes; §3's table already says so. Leave as is.

## Claims I could not check in this session

* "Full suite … **762 passed, 8 skipped, 0 failed**" (line 526) — not re-run; a full `pytest`
  exceeds this audit's 5-minute compute budget. **UNVERIFIED.**
* Every Lackenby Thm 1.2/1.3 dependency. `ls literature/` returns only `fake_surfaces/` — **no
  Lackenby paper in this clone**. `S15` §4 flags this correctly and in the right place; S13 does
  not repeat the flag anywhere, and §3z-bis's now-retracted text called its control "AC-trivial"
  on the strength of it. **UNSOURCED**, as `S15` says.
* T1/T2/T4/T4′ and S4.1–S4.3 are marked "unaudited" in §2 and were not audited here either.

---

## Summary table

| # | severity | section | one-line issue |
|---|---|---|---|
| F1 | **critical** | §0 | "which AK(3) does not" — class-wide absence asserted from a search |
| F2 | **critical** | §0 / `S15` §5 | "no known move manufactures one" refuted by `rank_n_ac_search_depth_ladder.json` (39/40) |
| F3 | major | §0 | "cannot settle AK(3)" contradicted by §1(i) and 527 measured descents |
| F4 | major | §0 / banner | 93,638 vs 91,409; the 759-chain row is not a creation opportunity |
| F5 | major | §4a | stale against `s12_gateway_hi_*.json` and `S15` §4 — `aca_11` is calibrated 12/12 |
| F6 | major | §3a | "one unit closer" dissolved by §1 line 78 and `S15` §3's `Γ(AK(3)) ≤ 1` |
| F7 | major | §3a | graft ceiling quoted without "non-cancelling AC2"; generalised to all moves |
| F8 | major | §5.7 | re-quotes the retired 54.8 %; in-band is 0.147 % and all hits share one parent |
| F9 | moderate | §3z | "no γ_N = 0 state at rank 12–13 is known to exist" — 759 now exist |
| F10 | moderate | §1(ii) | "what matters is the ratio ℓ/n" contradicted by its own table |
| F11 | moderate | §3 | "3.5× S6's headline" — it is 2.6×; 3.5× is against the control |
| F12 | moderate | §3 | 18.5 % promoted past its length-7–10 corpus, against T-S15 |
| F13 | moderate | §1(ii) | two table cells are n = 1 and n = 2, printed as flat zeros |
| F14 | minor | §1(ii) | median-census sentence switches artifact without saying so |
| F15 | minor | §1 / `S15` §3 | "cyclically equal to AK(3)" true only up to inversion |
| F16 | minor | §5.3 | 64.29 % quoted as a prior after `S4B` §0.6 retracted that use |
| F17 | minor | §5.1 vs §7.4 | opposite advice on attacking Q(F2) level 1 |

Nothing in this audit is a proof or disproof of the AC or stable AC conjecture. Its content is
one critical bound-direction repair (F1), one refuted blanket claim (F2), one staleness repair
(F5), and fourteen smaller corrections. **Do not commit S13 as final until F1, F2 and F5 are
applied** — F1 and F2 are the two sentences a future session would most plausibly act on.
