# S22_AUDIT — adversarial audit of `S22_FINAL_ANSWER.md`

Branch `claude/stable-ac-conjecture-stabilization-rwo9as`. **This branch must be merged into
`fable/proof` by the user.** No commit, no push, no PR from this audit. New files only:
this file and `experiments/stable_ac/fable/s22_audit_numbers.py` (read-only re-counter, runs
no search and decides no state). No existing `.md` and no existing code was modified.

Audited at `date -u` = **2026-08-04 10:35:22Z**, against working tree at `e191a84`.
Units throughout: `minimum_defect = 2·γ_N`.

---

# VERDICT: **AMEND**

Not RETRACT. I re-counted every load-bearing number from the artifacts and **the core
measurements reproduce exactly** — 174,178 edges, the whole 4×4 transition matrix, the empty
`1→0` cell in 56,388 opportunities, 2,101/3,017 = 69.64 % destruction, 0 upward crossings,
45,111 + 61,157 = 106,268, 527 `γ_N = 1` states in AK(3)'s pool, 14/1,470 vs 0/1,470 at
rank 5, and Lemma 11 at `ac_paper@d86984d:sec/stable.tex` (I opened the file; the lemma, the
`m` remark and the open-problem paragraph are all there verbatim). §4's retraction record is
substantively right and unusually honest.

Not ACCEPT. Eleven findings follow. **One number does not reproduce at all** (F1: "8/40 at
ceiling 2" — the artifact says **8/8** at ceiling 2; 8/40 is the pooled total *including* the
32 zero-trials it is being contrasted with). Two sentences re-import, verbatim, overreaches
that an audit committed **today** ordered repaired (F2, F4). One headline is internally
self-contradictory on the same page (F5). One drops an epistemic hedge in exactly the
direction of the disproof (F3). And the document that *supersedes* `S13` §1 silently deletes
`S13` §1's surviving positive half (F8).

Findings are ordered by severity. Each gives the exact quoted sentence, what is wrong, the
evidence, and a drop-in replacement.

---

## F1 — [BLOCKING NUMBER] "8/40 at ceiling 2" does not reproduce; the artifact says 8/8

> §0.1: "…where extra rank was measured against a fixed budget it *hurt* — 0/32 at rank
> ceilings 3–6 against **8/40 at ceiling 2**."

**What is wrong.** `8/40` is the **pooled total over all five rungs** of the defect-matched
ladder, not the ceiling-2 rate. The 40 trials are 5 rungs × 8 seeds; all 8 hits are at
`depth_k = 0` (rank ceiling 2) and every other rung is 0/8. So the denominator `40` *contains*
the `32` it is being compared against, and the contrast as printed is `0/32` against a figure
that is 80 % composed of those same 32 zeros. The real contrast is far stronger than the one
S22 states — which is why the error is worth fixing rather than shrugging at.

**Evidence** (`results/stable_ac/fable/s18_defect4_ladder.json`, recounted this audit):

```
trials by depth_k (rank ceiling = 2 + k): {0: 8, 1: 8, 2: 8, 3: 8, 4: 8}
hits   by depth_k:                        {0: 8}
pooled: 8/40
```

`S18_S5_RECHECK.md` §5 states it correctly — "**8/8** at rank ceiling 2 and **0/32** at
ceilings 3–6" — and `S18` §5 table reads `k=0: 8/8 … total 8/40`. The mislabel was introduced
downstream of S18 (it is also in `FRAMING.md`'s route-S paragraph, which is outside this
audit's scope but should be fixed in the same pass).

**Second defect in the same sentence.** All 8 of the ceiling-2 hits are **out of band** —
`s18_defect4_ladder.json` gives `created_and_in_band(min chain total_length >= 13) = 0`, with
minimum chain lengths 5, 7, 7, 9, 9, 11, 11, 11. So the entire positive arm of "extra rank
hurt" consists of witnesses obtained through the exit T-S20 proves AK(3) cannot use. Reporting
it in §0 without that flag re-imports a retracted mechanism into the answer paragraph.

**Replacement (§0.1, final clause):**

> …and where extra rank was measured against a fixed budget it *hurt*: on the defect-matched
> ladder the search hit **8/8 at rank ceiling 2 and 0/8 at each of ceilings 3, 4, 5 and 6**
> (0/32 pooled), at 600 nodes per trial. Read this as an instrument fact only — all 8
> ceiling-2 hits are **out of band** (minimum chain lengths 5–11 against a root length of 13),
> i.e. obtained through the exit T-S20 shows AK(3) is denied, so what extra rank cost the
> search was access to a route the target never had.

---

## F2 — [BLOCKING OVERCLAIM] "at any rank" is an extrapolation from ranks 2–5, and A21 already ordered this repaired today

> §0.1: "`γ_N` does not move under stabilization **at any rank** (exact census, ranks 2–5)"
> §1: "Adding generators alone does not move `γ_N` **at any rank**. Only moves that *use* the
> new generators can."

**What is wrong.** The claim quantifies over all ranks; the parenthesis names its evidence as
a census at ranks 2–5. Those are different statements, and S22 itself files this block under
"**measured** rather than proved". This is verbatim the sentence `S21_AUDIT.md` Finding 7
flagged **this morning** and supplied a replacement for — and S22 makes it *worse* than S21
did, because S21 at least attributed the extrapolation to **T4** (`S6` move classification,
*proved, unaudited*), whereas S22 cites nothing and reads as a bare measurement claim.

**Evidence.** `S21_AUDIT.md` §7: *"'at any rank', 'rank 20' and 'however deep' are
consequences of **T4**, which §7 itself flags as *proved (A8, unaudited)*. The measurement
covers ranks 2–5 on three presentations."* `S21_MATCHED_NEGATIVE.md` §7 status row: "§3
stabilization inert | exact census at ranks 2–5 on three presentations | **measured**; it
confirms **T4**, which is *proved* (A8, unaudited)".

**A second, separate defect in the same block.**

> §1: "Exact census: AK(3) holds `minimum_defect` 4 at ranks 2, 3, 4 **and** 5; **two controls
> hold defect 2 across the same**."

The two controls' **rank-2 entry is not a defect at all**. `S21` §3's table gives them
`NOT_SPHERICAL` at rank 2 — a verdict, not a number — and `S21_AUDIT.md` §6 says so
explicitly ("As printed, §3's rank-2 column holds a *verdict*, not a defect"). A21 then
measured rank-2 defects, but for the **five defect-4 ladder controls**, not for these two
defect-2 controls, and only to rank 4. So "defect 2 across the same [ranks 2–5]" is **not on
disk for rank 2**.

**Replacement (§1, the italic block):**

> **Stabilization is inert for `γ_N` at every rank measured.** Exact census: AK(3) holds
> `minimum_defect` 4 at rank 2 (`S21_AUDIT` §6), and at ranks 3, 4 and 5 (`S21` §3); two
> controls hold defect 2 at ranks 3, 4 and 5, and are certified `NOT_SPHERICAL` (γ_N ≥ 1) at
> rank 2, where their exact defect was not censused. **T4** (`S6`, *proved but unaudited*)
> predicts inertness at every rank; the measurement stops at 5 and nothing here proves the
> general statement. Only moves that *use* the new generators can move `γ_N` — and A6's SPLIT
> demonstrably does (2 → 1).

**Replacement (§0.1, first clause):** replace "at any rank (exact census, ranks 2–5)" with
"at every rank measured — exact census at ranks 2–5, with T4 (proved, unaudited) predicting
the general case".

---

## F3 — [BLOCKING, bound direction] "…in a way an open target is not" drops "known to be", and the dropped words are the whole disproof

> §4: "**any control you can verify is solvable is, by that verification, close to a solution
> in a way an open target is not.**"

**What is wrong.** As written this asserts that the open target *is* far from a solution.
That is a **lower** bound on `Γ(AK(3))`, i.e. the disproof of the stable AC conjecture, and
nothing on this line establishes it — every instrument bounds `Γ` from **above** (`S15` §4,
`S16` §5, `S17` §6, `S21_AUDIT`'s closing paragraph). The two sources S22 is compressing both
carry the hedge:

* `S21` §5.2: "any presentation known to be AC-trivial is by definition close in a way AK(3)
  is **not known to be**."
* `control-escapes-through-a-region-the-target-cannot-enter.md` rule 3: "close to a solution
  in a way the open target is **not known to be**."

Deleting three words converts an epistemic statement into an ontological one. This is the
repo's most expensive recurring trap wearing its smallest disguise, in the sentence a future
session is most likely to quote.

**Replacement:**

> **any control you can verify is solvable is, by that verification, close to a solution in a
> way an open target is *not known* to be** — and that gap is epistemic, not a measured
> property of the target; nothing here bounds `Γ(AK(3))` from below.

---

## F4 — [MAJOR] "every hit walks *down*" is false; 8 of 24 length-13 control trials ended in band

> §4, S21 row: "the controls **exit the length band** — **every hit walks *down*** (witnesses
> at 3,4,5,…7) into a region AK(3) provably cannot enter…"

**What is wrong.** Two errors in one cell.

1. **"every hit"** is contradicted by S21's own retraction table: restricted to the three
   length-13 targets, the raw rate is 19/24 and the **witness-length ≥ 13** rate is **8/24**.
   So 8 of the 19 hits ended *back in band* at witness level. What is true is (a) the
   *dominant* route is downward, (b) witness length is inflatable by inert AC4 discs so
   in-band witnesses can be short cores in costume (39/39 reduce to length-8 or 11 rank-2
   cores, `S18` §3), and (c) the one hit replayed end to end never returned to band
   (`13,12,15,18,17,11,14,17,10,11,15,17,14,9,8,7`, certificate at 7 — `S21_AUDIT` §4). The
   claim needs (b)+(c), not the false universal.
2. **"witnesses at 3,4,5,…7"** is garbled and, as an ellipsis terminating at 7, implies the
   witnesses top out at 7. `S21`'s banner lists "3, 3, 4, 4, 4, 5, 7, 7, 8, 9, 9, 9, 9, 10,
   11, 11, 11, …" and `S21_AUDIT` §3 records off-ladder witnesses at 15, 18, 19 and 20.

**Replacement:**

> the control's *dominant* route **exits the length band** — witness lengths from a start of
> 13 run 3, 3, 4, 4, 4, 5, 7, 7, 8, 9, … — into a region AK(3) provably cannot enter, since
> any member of its class below length 13 would settle the problem (Havas–Ramsay). Requiring
> only that the witness end at length ≥ 13 takes the length-13 rate from **19/24 to 8/24**,
> and total length is inflatable by inert AC4 discs, so even those 8 are suspect: 39 of 39
> sibling witnesses reduce to a rank-2 core of length 8 or 11 (`S18` §3), and the one hit
> replayed end to end reaches its certificate at length 7 without returning to band
> (`S21_AUDIT` §4). (**T-S20**)

---

## F5 — [MAJOR, self-contradiction] "certificate-preserving" is contradicted three lines below by "destroys certificates at 69.6 %"

> §3 headline: "**The cubic chord+SPLIT pipeline is certificate-preserving and
> certificate-non-creating.**"
> §3, twelve lines later: "SPLIT **destroys** certificates at 69.6 %…"

**What is wrong.** "Preserving" is inherited from `S16` §4, where it meant *the 759 hits were
inherited from an already-`γ_N = 0` root*. In S22 it sits as a bolded headline directly above
a measurement that a single SPLIT destroys the certificate roughly seven times in ten
(2,101/3,017, re-counted this audit at 69.64 %). A reader of the session's first-read document
will take "preserving" at face value, and it is the opposite of what the transition table
says. The true property is one-way inheritance along chains whose defect never left 0, not
per-step preservation.

**Replacement (§3 headline):**

> **The cubic chord+SPLIT pipeline never creates a thickenability certificate, and destroys
> one more often than not.** Certificates are *inherited* — every `γ_N = 0` state it exhibits
> descends from a root that was already `γ_N = 0` (chain `(0,0,0,0)` × 759) — while a single
> SPLIT applied to a `γ_N = 0` state destroys it 2,101 times in 3,017 (69.6 %).

---

## F6 — [MAJOR] "a mechanism rather than a null" — most of the mechanism is a null

> §0.1: "**No, and now with a mechanism rather than a null: adding generators is exactly
> inert.**"

**What is wrong.** The three legs of the "mechanism" have three different epistemic statuses,
and only one is a mechanism:

| leg | status |
|---|---|
| chord refinement is a CW subdivision, defect histogram preserved (`S3`) | **PROVED + audited** — a genuine mechanism |
| stabilization alone does not move `γ_N` | **MEASURED** at ranks 2–5; T4 proved but unaudited (F2) |
| SPLIT never lowers `γ_N` to 0 | **A NULL** — 0 in 57,858, and `S17` §6 says in terms: "It is **not** a theorem … and it is **not** an obstruction" |

`S20` was commissioned to *supply* the mechanism for the third leg and returned the negative:
planarity is "**consistent** with S17's empty `1 → 0` cell … but it is **not its mechanism**"
(`S20` §6), leaving 26,761 unblocked opportunities unexplained. So the leg that carries the
word "No" is exactly the leg that is still a null. S22's own §3 concedes this ("as an
**instrument fact, not a theorem**") — §0 must not claim more than §3 delivers.

Separately, "adding generators is *exactly inert*" answers a weaker question than the brief
asked. The brief asks whether the problem gets easier once rank grows; S22's very next
sentence concedes "Only moves that *use* the new generators can [move `γ_N`]", and A6's SPLIT
did move it (2 → 1, 527 states). Stabilization-alone-is-inert is nearly tautological in that
framing and cannot by itself support a flat "No".

**Replacement (§0.1):**

> 1. **Not by any mechanism this line could find — and the closure is now part mechanism, part
>    calibrated null.** Chord refinement is a *proved* CW subdivision that cannot move `γ_N`
>    at all (S3, audited); stabilization alone is *measured* inert at ranks 2–5 (T4 predicts
>    all ranks, unaudited); change of variables is a depth-1 phenomenon; and the one move that
>    exploits new generators, A6's SPLIT, *did* lower `γ_N` (2 → 1) but never to 0 in 57,858
>    tries — **a null, explicitly not an obstruction** (`S17` §6), and `S20` refuted the one
>    mechanism proposed to explain it. Nothing here bounds `Γ` from below, so "No" is a
>    statement about these instruments, not about high rank.

---

## F7 — [MODERATE] §2 states S15.5c unconditionally; the Thm 1.3 dependency is carried in §0 and §1 but dropped here

> §2: "**'A simple general way'** — by S15.5c such a construction *is* the stable AC
> conjecture on balanced trivial-group presentations."

**What is wrong.** S15.5c's forward direction (`γ_N = 0` member ⇒ stably AC-trivial) is
**conditional on Lackenby Thm 1.3**, which this clone does not contain — I ran `ls literature/`
while writing this sentence and it returns `fake_surfaces` only. `S15` §7 classifies S15.5b/c
as "**conditional on Lackenby Thm 1.3**, which is source-relayed only in this clone". S22 §0.2
and §1 both carry the flag; §2 — the section a reader goes to for the brief's specific
question — does not. Per `literature-absent-in-cloud-clones.md`, an unflagged restatement is
how a relayed theorem gets promoted to a read one.

**Replacement (§2, third paragraph):**

> **"A simple general way"** — by S15.5c (**conditional on Lackenby Thm 1.3, source-relayed,
> not read in this clone — see §5**) such a construction *is* the stable AC conjecture on
> balanced trivial-group presentations. Its absence after seven hours is not a defect of the
> approach; any future candidate must be checked for a hidden reduction to the open problem
> before it is believed.

---

## F8 — [MODERATE] S22 supersedes `S13` §1 but silently deletes `S13` §1's surviving positive half

> Header: "This supersedes `S13_SYNTHESIS.md` §1 as the session's answer."

**What is wrong.** `S13` §1 has two halves. **(i)** "almost no mechanism" — which S22 keeps
and sharpens. **(ii)** "**But high rank buys decidability, and the size of the effect is now
measured**" — the A10 certified ladder, 163 rungs, two instruments with `missed = 0` in every
cell, median census 1.3·10¹³ at rank 2 against 5,760 at rank 8, decidable region ℓ/n ≲ 3.
That half was **not retracted**; `S13_AUDIT` amends its phrasing (the critical ratio *falls*
with rank; "decidable at every rank measured" is the correct statement) but confirms the
numbers. S22 contains no trace of it. A future session that reads S22 first — as `FRAMING`
now instructs — will conclude that rank ≫ 3 bought nothing, when in fact it bought the only
thing this line measured a positive effect on: **the cost of asking the question**.

**Replacement — add to §2, after the "Lemma 11" paragraph:**

> **What high rank *did* buy: decidability, not answers.** The compatible census is
> `∏(deg−1)!`, so what matters is `ℓ/n`. `S13` §1(ii)'s certified ladder (163 rungs, two
> instruments, `missed = 0` in every cell) measures median census **1.3·10¹³ at rank 2 against
> 5,760 at rank 8** at total length 22, with the decidable region at `ℓ/n ≲ 3` — the cubic
> regime. AK(3)'s rank-13 cubic form `C1` has census **8,192** against AK(3)'s 86,400.
> Hard limit, and it is why this does not rescue the route: the effect is for *natively*
> high-rank states. Lifting a rank-2 state by chord refinement changes the census not at all
> (`S3` Lemma S3′), and `C1`'s cheaper question returned `γ_N = 1` — tying, not beating, the
> rank-2 gateway. **Extra generators bought a much cheaper question and no better answer.**

---

## F9 — [MODERATE] "ascents jump by 2" misstates the measured matrix; most ascents are by 1

> §3: "Shape facts (measured): every descent is by exactly 1 (`2→0`, `3→1`, `1→0` all empty)
> while **ascents jump by 2** (`0→2` = 650), so no `|Δγ_N| ≤ 1` law explains it"

**What is wrong.** Ascents by 1 dominate overwhelmingly. Re-counted from
`s17_transition_edges.jsonl.gz` this audit:

```
from 0: {0: 916, 1: 1451, 2: 650}      <- 1451 ascents by 1, 650 by 2
from 1: {1: 30821, 2: 25433, 3: 134}   <- 25433 ascents by 1, 134 by 2
from 2: {1: 1049, 2: 102839, 3: 7675}  <- 7675 ascents by 1
```

`S17` §2 states it correctly: "Ascents are **not so limited**: `0→2` (650) and `1→3` (134)
**both occur**, so a `|Δγ_N| ≤ 1` law is false". S22 turns "ascents by 2 also occur" into
"ascents jump by 2", which is a different and false claim about the shape of the data. The
logical point S22 needs (no `|Δγ_N| ≤ 1` law) survives the correction intact.

**Replacement:**

> Shape facts (measured): every descent is by exactly 1 — `2→0`, `3→1` and `1→0` are all
> empty — while ascents are **not** so limited: `0→2` occurs 650 times and `1→3` 134 times, so
> no `|Δγ_N| ≤ 1` law explains the empty cell.

---

## F10 — [MODERATE] §6.1 states as "need not" what S15.2a proves as "cannot", and shrinks "every stable AC move" to "SPLIT"

> §6.1: "Note S20.1 shows such a quantity **need not** be a homotopy invariant — **it just has
> to survive SPLIT**, which planarity does not."

**What is wrong.** Two direction errors.

1. `S15.2a` proves the *stronger* statement: every balanced trivial-group presentation is
   contractible, so **no** homotopy invariant can separate AK(3) from `T_2`; any obstruction
   **must** be combinatorial. "Need not be a homotopy invariant" understates a proved
   impossibility as a permission, and attributes it to S20.1 rather than to S15.2.
2. "It just has to survive SPLIT" is wrong by a wide margin. `S15` §6 states the actual
   requirement: a computable `Φ` with `Φ(AK(3)) > 0`, `Φ(T_n) = 0`, and `Φ` non-increasing
   under **every** stable AC move (AC1–AC5). SPLIT is one composite move in one instrument.
   Left as written this sends the next session hunting for a SPLIT-invariant, which would not
   be an obstruction even if found. (`S20` §7 makes the same point: AC1/AC2/AC3/AC4/AC5 versus
   non-planarity are **open**, and AC2 is "the reason the route cannot be closed".)

**Replacement:**

> Note the requirement is sharper than it looks in both directions: `S15.2a` proves such a
> quantity **cannot** be a homotopy invariant (all these complexes are contractible), and it
> must be non-increasing under **every** stable AC move AC1–AC5, not merely survive SPLIT.
> Planarity fails the second test on SPLIT alone (`S20` §3.2); its behaviour under AC1, AC2,
> AC3, AC4 and AC5 is untested (`S20` §7).

---

## F11 — [MINOR] Four denominators and one range that need a word each

1. > §3: "crossing the thickenability boundary 2,101 times downward and **zero** times upward
   > in 174,178 tries."

   The 2,101 downward crossings come from **3,017** tries (the `γ_N = 0` row), not 174,178;
   and the upward tries number **171,161** (174,178 minus that row). Verified this audit.
   **Replace with:** "crossing the thickenability boundary downward 2,101 times in the 3,017
   chances it had (69.6 %) and upward **zero** times in 171,161."

2. > §0.3: "has never created one in **57,858** attempts, while plain AC2 creates them 14
   > times in 1,470 on *identical* parents."

   57,858 = 56,388 (ranks 9–13) + 1,470 (rank 5). The AC2 comparison exists **only** at rank
   5 and covers only the 1,470 — `S17` §3.4 states this as "the honest gap": at ranks 9–13 no
   move of any kind has been shown here to take `γ_N = 1` to `γ_N = 0` in one step.
   Juxtaposing 57,858 with 1,470 invites reading them as one experiment.
   **Replace with:** "has never created one in 57,858 attempts (56,388 at ranks 9–13, 1,470 at
   rank 5), while on the *same* rank-5 parents plain AC2 creates them **14 times in 1,470** —
   the paired control exists at rank 5 only."

3. > §3 table: "states from **five non-thickenable roots** | 106,268 decided | **0**"

   45,111 of the 106,268 are AK(3)'s own pool — the target is one of the five "roots". Correct
   per `S16` §4, but a reader of the table will take all five for controls.
   **Replace the row label with:** "states from five non-thickenable roots (four controls +
   AK(3) itself: 61,157 + 45,111)".

4. > §3(iv): "…so it explains **at most half** the empty cell."

   Measured is **at most 52.5 %** (`S20` §6). "At most half" is a rounding *in the direction of
   the conclusion S22 wants*. **Replace with:** "so it accounts for at most 52.5 % of the
   opportunities and leaves 26,761 genuinely unblocked chances unexplained."

5. > §1: "**S19.5** | `m*(L) ≥ L − 2`, unconditionally"

   `S19` §3.2 states it "**for all `L ≥ 3`**". **Replace with:** "`m*(L) ≥ L − 2` for all
   `L ≥ 3`, unconditionally".

---

## Numbers in S22 that DO reproduce (re-counted from artifacts this audit)

| S22 figure | source | verdict |
|---|---|---|
| 174,178 edges; the whole 4×4 matrix (3,017 / 56,388 / 111,563 / 3,210) | `s17_transition_edges.jsonl.gz` | **exact** |
| `1→0` = 0 in 56,388 opportunities | same | **exact** |
| 1,958 distinct `γ_N = 1` parents, ranks 9–12, depths 0–3 | same | **exact** (1,956 of them have at least one *decided* child; the other 2 appear only on the 184 undecided-child edges — immaterial, but the observed 56,388 outcomes come from 1,956) |
| 2,101 downward crossings; 69.6 % destruction | same (2,101/3,017 = 69.64 %) | **exact** |
| 0 upward crossings | same | **exact** (denominator 171,161, see F11.1) |
| 8.60 % → 0.94 % → 0 % descent collapse | 276/3,210, 1,049/111,563, 0/56,388 | **exact** |
| 106,268 decided from five non-thickenable roots, 0 creations | 45,111 + 61,157, recounted row by row | **exact** |
| 527 `γ_N = 1` states in AK(3)'s pool | `s4b_decided.jsonl.gz` hist `{1: 527, 2: 40100, 3: 4484}` | **exact** |
| AC2 14/1,470 vs SPLIT 0/1,470, rank 5, same parents | `s17_transition_table.json → depth1_flip_census_rank5` | **exact** |
| 945 `γ_N = 0` states, 945 planar, 0 non-planar | `S20` §0 (759 ∪ 916 ∪ 186) | **as stated in source** |
| 16.9 % of `γ_N=1` parents non-planar; 47.5 % of edges with planar child | `S20` §6 (331/1,958; 26,761/56,388) | **exact** |
| 59/64 | `S21_AUDIT` §2 (35/40 + 24/24) | **arithmetic exact** — but see note below |
| 19/24 → 8/24 | `S21` §0 | **as stated in source**; all 24 trials share 8 RNG streams (`S21_AUDIT` §5) |
| `Area_{AK(2)}(x) ≥ 4`, instrument saturated | `S19` §4 / status row 21 | **exact** |
| Lemma 11 at `ac_paper@d86984d`, `sec/stable.tex` | **I opened the clone.** Lemma "Substitution and Removal", "Note that $m$ may be much larger than $n$", and "Finding this bound, or discovering an alternative proof … would be very useful" are all present verbatim | **verified from source, again** |
| `ls literature/` → `fake_surfaces` only | run while writing this line | **exact** |
| `s12_ak3_hi_k1.json` / `s12_ak3_depth_ladder.json` still absent | `ls`, 10:35:22Z | **confirmed** — the `0/16`-not-`0/34` correction in §4 stands |
| "> 40 minutes inside depth 1" | `logs/04-08-2026.md` says "> 45 minutes" | **consistent** (S22 is the weaker claim); note the source is a log observation, not an artifact |

**Note on 59/64.** §4 reads "An auditor built controls matched on every axis the instrument
can see … and the rate did not collapse (59/64)." The auditor's *new* controls scored
**24/24**; 59/64 pools them with the original five ladder controls, which were **not** matched
on those axes. **Replace with:** "…and the rate did not collapse — 8/8, 8/8, 8/8 on the three
newly matched controls (24/24), 59/64 pooled with the original five."

---

## What must not be inferred from this audit

Nothing here bounds `Γ(AK(3)) = min{γ_N(Q) : Q ~_st AK(3)}` from **below**, and nothing here
is evidence for or against the AC or the stable AC conjecture. This audit re-counted rows in
existing artifacts; it ran no search, decided no state and spent no search node. Every
instrument whose output it re-counted bounds `Γ` from **above**, so every null it confirms
confirms a null and nothing more.

**After the eleven repairs, S22 is fit to be the document a future session reads first.**
Its measurements are sound, its retraction record is accurate and unusually candid, and its
core judgement — that this route is retired and that target-versus-control cannot settle the
question — survives the audit intact. What needs fixing is the register: §0's three sentences
currently claim at the strength of a theorem what §§3–5 correctly classify as measurements,
one null, and one conditional.
