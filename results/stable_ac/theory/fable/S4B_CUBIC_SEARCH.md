# S4B — Scaled SPLIT search for a cubic form of AK(3), and the SPLIT flip census

Date 2026-08-04. Branch `claude/stable-ac-conjecture-stabilization-rwo9as` — **must be
merged into `fable/proof` by the user.** Follow-up to `S4_CUBIC_NORMAL_FORM.md` (task A6);
`S4` is **not edited** by this note. Code: `experiments/stable_ac/fable/cubic_split_search.py`
(new file; nothing existing is modified). Standing frame: `FRAMING.md`.

Everything here is about **balanced presentations of the trivial group**. Claim taxonomy:
this file proves **no** AC-triviality and **no** stable AC-triviality of anything. It
delivers one **measurement** with a matched control, two **corrections** to the route's
cost model, and a scaled **null** with its calibration.

---

## 0. Answers, up front

> ### **AK(3) HAS A CUBIC TRIANGULAR FORM. Q-red is answered YES for AK(3).**
>
> ```
> C1 = ⟨ a,b,c,d,e,f,g,h,i,j,k,x,y |
>        kAe, Xgb, aXH, bxH, cYY, ydJ, eid, IfC, gKF, hAe, igb, jfC, kdJ ⟩
> ```
> rank 13 · all 13 relators of length exactly 3 · all 13 multiplicities exactly 3 ·
> every relator cyclically reduced (**non-degenerate**, so Thm S4.3 does not apply and
> Prop S4.2's rank bound is respected) · **presents the trivial group** (Todd–Coxeter over
> the trivial subgroup, index 1) · reached from AK(3) by **7 chord refinements + 4 SPLITs**,
> all AC4 + AC1–AC3, **no destabilisation** · and
>
> ### **γ_N(C1) = 1 — strictly below AK(3)'s γ_N = 2.**
>
> A second, independent cubic form `C2` (rank 13, different root) has γ_N = 2.
> Verification of both is in §4.2; the chains are machine-replayed and the roots are
> independently un-merged back to AK(3).

This is what `S4` §0 item 6 left open ("**No cubic form of AK(3) is reported**", 0 hits in
48 attempts). The scaled search finds them at **2 of 28 roots**.

1. **Q-red for AK(3): YES**, with two explicit witnesses at rank 13 (§4). Rank 13 is the
   *minimum possible* for this calculus (§5.1), so these are extremal.
2. **The `SPLIT` calculus does lower `γ_N`.** `C1` sits at `γ_N = 1` while AK(3) and *every*
   one of its chord triangulations sit at `γ_N = 2` exactly (§2). Four further states in the
   search's near-cubic pool are also at `γ_N = 1`. **No `γ_N = 0` was found.**
   **`γ_N = 1` TIES the best previously reached for AK(3)'s class; it does not beat it.**
   `results/stable_ac/fable/gateway_scan.json` already records a `γ_N = 1` **gateway at rank
   2**, total length 14, inside AK(3)'s classical class: the pair
   `("YYYXXyx","YXYXyxx")`, 1 gateway in 2,500 members scanned
   (`gamma_hat_histogram {1:1, 2:63, 3:316, 4:932, 5:814, 6:355, 7:19}`), pinned exactly by
   combining the sampler's defect-2 witness (upper bound) with the solver's certified
   `NOT_SPHERICAL` (lower bound `γ_N ≥ 1`). Verified in this session by reading that file.
   What is new is *where* `γ_N = 1` now sits — in the cubic regime, where the decision is
   cheap — not the value itself.
3. **A flip census of `SPLIT` on small instances says the opposite — and it is wrong to
   extrapolate it.** On a rank-5 corpus, `SPLIT` destroyed `γ_N = 0` in 643/960 cases and
   created it in **0/1,470**, against a matched AC2 control that created in 14/1,470 (§3).
   I drafted a monotonicity conjecture on that measurement and **my own rank-9→13 search
   refutes it** (§3.4). Recorded in full, including the refutation, because the failure mode
   — a clean small-instance null extrapolated past the regime it was measured in — is the
   reusable lesson here.
4. **45,111 states of AK(3)'s stable class decided EXACTLY, and none is thickenable**
   (§4.5). Ranks 12–13, every state's whole compatible-rotation census enumerated — no
   sampling — with the histogram `{γ_N = 0: 0, γ_N = 1: 527, γ_N = 2: 40,100, γ_N = 3: 4,484}`.
   The pool is persisted with full replayable chains. **And proximity to cubic form turns out
   to be anti-correlated with low defect**: 0/1,232 of the states one `SPLIT` from cubic are
   at `γ_N = 1`, against 527/43,879 two SPLITs away (T-S17).
5. **THE NULL IS NOW CALIBRATED, and it survives** (§4.6–4.8). Running the *identical*
   pipeline on a rank-2 source that is AC-trivial **and thickenable** produced **759
   `γ_N = 0` states in 50,320** (1.51 %) in the same rank-12/13 region — one of them verified
   six ways, including `witness_check_n`, Todd–Coxeter and a full chain replay back to the
   rank-2 source. So the region **does** contain certificates and this instrument **does**
   find them. Under the control's rate, AK(3)'s 45,111 states should have contained ≈ **681**
   thickenable members; **0** were found. AK(3)'s null is informative, not an artefact.
   Per-step tracing shows why: chord refinement holds `γ_N` **exactly constant** (a live
   check on Theorem S3), and it is the `SPLIT`s that destroy it.
6. **Two cost-model corrections** (§5): a cubic triangular presentation at rank `N` has
   census exactly `2^N`, so S4 §7.2's "16 cases" does not transfer (AK(3)'s cubic forms have
   census `2^13 = 8,192`, and the advantage over AK(3)'s own 86,400 inverts at rank 17); and
   the 64.29 % thickenable fraction of S4 §4 is a base rate over tiny rank-4 AC-trivial
   presentations, **not** a prior for AK(3)'s descendants — the two cubic forms actually
   found came out at `γ_N = 1` and `γ_N = 2`, i.e. **0 of 2 thickenable**.

---

## 1. What the search actually explores, and why every state counts

`SPLIT` (S4 Lemma S4.4) takes a length-3 relator, rotates it to `R' = λ u v`, adjoins a
fresh generator `t` with definition relator `D = t u v`, and rewrites `k` occurrences of
`λ^{±1}` elsewhere to `t^{±1}`. Rank `+1`, every relator still length 3, cyclic reducedness
preserved.

Two properties make the search worth running at all:

* **every visited state is in the source's stable class**, reached by AC4 + AC1–AC3 with no
  destabilisation, so a `γ_N = 0` anywhere in it is a Lackenby Thm 1.3 certificate for the
  source (S12) — the orientability gap does not encumber a *hit* (an orientable PL
  3-manifold is a 3-manifold), only a null;
* **every visited state is triangular**, so its census is `∏_g (m_g − 1)!`.

### 1.1 Verification of every state (T-S3)

`cubic_split_search.py` checks, on **every** child it generates:

| check | where |
|---|---|
| S4.4 step-3 identity `D R'^{-1} = t λ^{-1}` as free words | `split_apply`, raises on failure |
| retraction certificate: substituting `t ↦ λ` returns exactly the parent's relators plus one duplicate of `R'`, as a multiset of canonical cyclic words | `verify_split` / `verify_chain` |
| all relators length 3, all cyclically reduced, balanced | `split_apply` |
| occurrence bookkeeping `Δδ = −k e_{g_λ} + e_{g_u} + e_{g_v} + (k−2) e_t` (S4 §5.3) | `selftest` |
| the published S4 §6 triangulation of AK(3) presents the trivial group (Todd–Coxeter, index 1) and has `Σ|δ| = 14` | `selftest` |

This certifies the *arithmetic* of the chain. It is **not** a full elementary-move replay:
the Lemma S-a portion needs an expression of `w` as a product of conjugates of the `r_i^{±1}`,
which `S1` §8 records as a search problem in its own right. Move counts are not quoted
anywhere (FRAMING trap 6 / T-S5).

---

## 2. The starting point is pinned — no triangulation of AK(3) can help

`S3_AUDIT.md` (audit A5 of Theorem S3) proves **Lemma S3′**: an elementary chord refinement
induces a defect-preserving *bijection* of compatible rotation systems, so the census size,
the **whole defect histogram**, and `γ_N` are all invariant — not merely the predicate
`γ_N = 0`.

Measured, and reproduced here:

```
AK(3)                        = ("xyxYXY","xxxYYYY")   defect 4  gamma_N 2  census 86,400
S4 §6 / S1 §4.4 rank-9 form  = (pYX,qXP,ryQ,rXY,sXX,tXS,uyT,vyU,vYY)
                                                      defect 4  gamma_N 2  census 86,400
histograms                   {4: 724, 6: 14882, 8: 55438, 10: 15356}   IDENTICAL
```

1,525 random triangulations of `γ_N = 0` and `γ_N > 0` rank-2 bases reproduced the base
histogram bit-for-bit in 1,525/1,525 cases (`S3_AUDIT.md` §5.2).

> **Therefore the "48 triangulations vs all triangulations" axis of the brief buys nothing
> for the certificate.** Every root of every SPLIT search on AK(3) has `γ_N = 2` exactly.
> More roots buy search diversity for the *cubic normal form* question only.

**Correction to `S4` §3 row and `S6` §0.3.** `S6_MOVE_CLASSIFICATION.md` §0 point 3 imports
trap T-S6 ("`γ_N`'s value is not comparable across cell structures; only `γ_N = 0` is
topological"). That trap is refuted by the S3 audit for chord refinement — and `S6`'s own
M4′ and (S3) rows already record "`γ_N` equal exactly in all", which agrees with the audit
and contradicts the trap it cites. T-S6 should be struck per `S3_AUDIT.md` repair R1.

---

## 3. The SPLIT flip census — a small-instance measurement, and the conjecture it wrongly suggested

### 3.1 Design

Format of `S6` §1: for a parent state `P` and a child `P'` reached by one move, record the
pair `(γ_N(P) = 0, γ_N(P') = 0)`. *Created* = `False → True`; *destroyed* = `True → False`.

* **Corpus.** Random AC-trivial rank-2 presentations of total length 9 (random AC1/AC2/AC3
  walk from `⟨x,y | x,y⟩`, so AC-triviality is by construction), each triangulated by a
  random member of the chord-refinement family to a rank-5 triangular state — cheap census,
  and by Lemma S3′ the triangulation inherits the source's `γ_N` exactly, which is what makes
  both `γ_N` classes easy to populate. AK(3)'s own rank-9 triangulation is included.
* **Arm 1 — `SPLIT`**: up to 30 single `SPLIT` children per parent, `k ∈ {1,2,3}`, all six
  (rotation × inversion) choices of `(λ,u,v)`, sampled occurrence subsets.
* **Arm 2 — control, general AC2**: `r_i ← freered(r_i r_j^{±1})` on the **same parents**.
  This leaves the triangular world, which is exactly the point: `S6` measures AC2 as the
  only creator of thickenability, so this arm measures whether a creation is **detectable at
  all on this corpus**. Without it a "SPLIT never creates" null bounds nothing
  (`experiments/lessons/calibrate-one-sided-hunts-on-a-positive-ladder.md`).
* `γ_N` by exact census `gamma_N_factorial_n`, cap 120,000; pairs above the cap are skipped
  and never converted into a verdict.

### 3.2 Result

81 parents measured inside the budget; 2,430 `SPLIT` pairs and 2,423 control pairs decided
by exact census. **The two arms share the same parents, so the denominators are matched.**

| arm | pairs | parents thickenable | parents NOT thickenable | **created** | **destroyed** |
|---|---|---|---|---|---|
| **`SPLIT`** | 2,430 | 960 | 1,470 | **0 / 1,470 = 0.00 %** | 643 / 960 = **67.0 %** |
| **control: general AC2** | 2,423 | 953 | 1,470 | **14 / 1,470 = 0.95 %** | 410 / 953 = 43.0 % |

Full defect transitions (defect = `2·γ_N`):

| arm | `0→0` | `0→2` | `2→0` | `2→2` | `2→4` |
|---|---|---|---|---|---|
| `SPLIT` | 317 | 643 | **0** | 1,403 | 67 |
| AC2 control | 543 | 410 | **14** | 1,444 | 12 |

By rewrite count `k` (`SPLIT` only): `k=1` 8 destroy / 0 create of 118; `k=2` 360 destroy /
0 create of 1,560; `k=3` 275 destroy / 0 create of 752.

### 3.3 Reading it

1. **`SPLIT` never created `γ_N = 0`, in 1,470 opportunities.** The control had the *same*
   1,470 opportunities and created 14 times. If `SPLIT` created at the control's rate one
   would expect ≈ 14 creations; 0 were seen.
2. **Stronger than "never creates": `SPLIT` never lowered the defect at all.** Every one of
   the 2,430 transitions is `0→0`, `0→2`, `2→2` or `2→4` — the `2→0` cell is empty, and no
   `4→2` occurred either. The control's `2→0` cell is not empty. This is the evidence for
   Conjecture S4B-M (§3.4) and it is a *directional* asymmetry of exactly the kind `S6`
   records for AC3 (315 destroy / 0 create).
3. **Destruction is the norm, not the exception**: two thirds of thickenable parents lose
   `γ_N = 0` to a single `SPLIT`, at every `k`. So the calculus actively moves *away* from
   the certificate while it moves toward the normal form.

**Honesty caveats, all mandatory.**
* The 2,430 pairs come from only **81 parents** (≈ 30 children each) and the parents come
  from a random-AC-walk generator, so the pairs are **not independent draws**. **No p-value
  is quotable** (`experiments/lessons/contrast-length-confound.md`). The right reading is the
  matched-denominator contrast in the table, nothing more.
* The corpus is length-9 rank-2 sources triangulated to rank 5, plus AK(3)'s rank-9
  triangulation. It is a *small-instance* corpus; a creation mechanism that only switches on
  at higher rank would be invisible here. The control's rate is also low (0.95 %), so the
  instrument's sensitivity on this corpus is modest — a `SPLIT` creation rate below roughly
  0.2 % would not have been resolved.
* This measures **orientable** thickenability (`γ_N = 0`, `R1E` Thm D). Per `S6` §0
  `[GAP-O]`, the orientable/general gap is open — but it encumbers only nulls, and this *is*
  a null, so it is a second reason S4B-M must stay a conjecture.

### 3.4 Conjecture S4B-M — drafted on §3.2, and **REFUTED by §4 of this same file**

On the strength of §3.2 (2,430 pairs, no downward defect transition whatsoever) I drafted:

> ~~**Conjecture S4B-M (SPLIT monotonicity).** For every `SPLIT` child `P'` of `P`,
> `γ_N(P') ≥ γ_N(P)`; in particular `SPLIT` never creates `γ_N = 0`.~~ **REFUTED.**

**Counterexample, from this file's own AK(3) run.** The rank-9 root
`(EaY, GxB, aXY, bxY, cYY, dXy, eXd, fCx, gYF)` — a chord triangulation of AK(3), hence
`γ_N = 2` by §2 — reaches the rank-13 cubic form `C1` in **four `SPLIT`s**, and
`γ_N(C1) = 1`. So some `SPLIT` in that chain **strictly lowered** the defect, from 4 to 2.
Four more states in the near-cubic pool are likewise at defect 2 (§4.1). `SPLIT` therefore
creates thickenability-progress; whether it can reach `0` is open.

> **This refutes MY conjecture, not `S8`'s.** `S8_SPLITTING_MONOTONICITY.md`'s *generator
> splitting* introduces a **length-2** definition relator `u g^{-1}` — a bigon — so
> `link(P)` is a **minor** of `link(P')` (contract the bigon's two link edges) and its
> proof sketch goes through. My `SPLIT` (S4 Lemma S4.4) introduces a **length-3** definition
> relator `D = t u v`; there is no bigon and no minor relation, which is exactly why the
> contraction argument does not transfer and why S4B-M was never more than a guess.
> **Conjecture S8 is untouched by anything in this file** — including S8 §2's observation
> that AK(3)'s 236 split states at ranks 4 and 6 all sat at defect 4, which is consistent
> with a *different* move reaching defect 2 at rank 13.

**Why the census did not see it, and the lesson.** §3.2's corpus is rank-5 states from
length-9 sources; the refuting events live at ranks 9→13 with far richer link graphs. The
census's own caveat ("a creation mechanism that only switches on at higher rank would be
invisible here") was correct, and the conjecture ignored it. The reusable form:

* **T-S15 (new).** *A move's flip census is a statement about the corpus's rank, not about
  the move.* `SPLIT` shows 0 creations in 1,470 rank-5 opportunities and demonstrably lowers
  `γ_N` at rank 9. Never promote a flip rate measured on small instances into a monotonicity
  claim; state the rank band the measurement covers, and calibrate at the *large* end
  (`experiments/lessons/parallel-runs-and-bound-direction.md`, last bullet: a weaker
  instrument and a real trend produce the same shape).

The §3.2 numbers stand as what they are: an exact measurement of `SPLIT`'s flip behaviour on
rank-5 triangular states, showing that at that scale destruction dominates (67 % of
thickenable parents) and creation is rare-to-absent. That is genuine information about the
calculus's *bias*; it is not an obstruction.

---

## 4. The scaled search: two cubic forms of AK(3), and the calibration

### 4.1 The runs

Beam search over `SPLIT`, cost `(Σ|δ|, −#Lemma-S4.6-exits)`, beam 60, depth 20, ≤ 300
children per node. **The one change that mattered** is the `diversity` parameter: 30 % of
each beam is filled by a *uniform random sample* of the non-best children instead of by the
cost ranking. Leaving the T-S11 parity plateau at `Σ|δ| = 2` provably requires a temporarily
cost-increasing move, so a pure ranking beam — S4's — can never do it, however large the
beam. That is why S4 saw 0/48 and this run sees 2/28.

| run | roots | **cubic forms found** | nodes | near-cubic states collected (`Σ|δ| ≤ 4`) | deep `γ_N` scan (cap) | deep defect histogram |
|---|---|---|---|---|---|---|
| **AK(3)** run 1 (28 distinct triangulations, 9 s each, seed 11) | 28 | **2** (7.1 %) | 1,298,733 | 66,756 (lost — not persisted) | 500 tested (900,000) | `{4: 402, 6: 94, **2: 4**}` — **no 0** |
| **AK(3)** run 2 (47 triangulations, 9 s each, seed 2026) | 47 | 0 | — | **45,264 (persisted, §4.5)** | **45,111 tested exactly** | `{2: 527, 4: 40,100, 6: 4,484}` — **no 0** |
| **matched-difficulty ladder** (35 AC-trivial rank-2 sources, `L = 13`, triangulated to rank 9, `Σ|δ| = 14` — the same numbers AK(3) has; 6 s each) | 35 | **0** | 930,647 | 29,678 | 200 tested (400,000) | `{4: 149, **2: 51**}` — **no 0** |

### 4.2 The two cubic forms, verified end to end

```
root12 = (EaY, GxB, aXY, bxY, cYY, dXy, eXd, fCx, gYF)        rank 9,  Σ|δ| = 14
   --4 SPLITs-->
C1     = (kAe, Xgb, aXH, bxH, cYY, ydJ, eid, IfC, gKF, hAe, igb, jfC, kdJ)
         rank 13 · cubic · non-degenerate · trivial group (index 1) · defect 2, γ_N = 1
         census 8,192 · histogram {2:2, 4:60, 6:510, 8:2338, 10:3766, 12:1516}

root13 = (Xbc, gxE, aYX, bAy, cyX, dYx, eYY, fDx, gfy)        rank 9,  Σ|δ| = 14
   --4 SPLITs-->
C2     = (Xbc, hEg, aYX, JbA, YCk, dIk, eYj, xfD, gfi, hfD, ibA, jCh, kEg)
         rank 13 · cubic · non-degenerate · trivial group (index 1) · defect 4, γ_N = 2
         census 8,192 · histogram {4:6, 6:158, 8:1620, 10:4124, 12:2124, 14:160}
```

Four independent checks, all passed:

1. **The `SPLIT` chain replays** from the root with the retraction certificate verified at
   every step (`verify_chain`, §1.1) — `chain_verified: true` for both.
2. **The root really is a triangulation of AK(3)**, checked *independently of the code that
   built it*: repeatedly AC2-merge a generator occurring exactly twice in two distinct
   relators and destabilise it (the inverse chord refinement of `S3_AUDIT` §6.2). Both roots
   collapse in exactly **7** un-merges to `("XyxyXY","yyXXXyy")` resp. `("yXYXyx","YxxxYYY")`,
   which are AK(3)'s two relators up to rotation and inversion.
3. **Trivial group**: Todd–Coxeter over the trivial subgroup completes at index 1 for both.
4. **Cubic + triangular + non-degenerate + balanced**: 13 generators, 13 relators, every
   relator length 3 and cyclically reduced, every multiplicity exactly 3.

Rank 13 is the **minimum possible** (§5.1: `Σ|δ| = 14` and no `SPLIT` reduces `Σ|δ|` by more
than 4, so rank `≥ 9 + ⌈14/4⌉ = 13`). Both witnesses are extremal.

### 4.3 Reading the calibration — it reverses S4's

S4 reported AK(3) 0/48 against a matched ladder at 4/12 = 33 % and called the AK(3) null
"suggestive of a real obstruction". This run has AK(3) at **2/28** and the matched ladder at
**0/35**. So on the improved search **AK(3) is not harder than matched-difficulty AC-trivial
inputs — it is, if anything, easier.** Whatever S4's 0/48 measured, it was the ranking beam's
plateau, not a property of AK(3).

Two confounds, stated rather than buried: the ladder got 6 s per root against AK(3)'s 9 s,
and the AK(3) roots are 28 triangulations of **one** source while the ladder is 35 **distinct**
sources with one triangulation each. Neither difference is in AK(3)'s favour on the axis that
matters (AK(3) had less source diversity), but the two rates are not interchangeable and no
p-value is quotable — these are move-tree samples, not independent draws.

The one contrast that *is* like-for-like is the deep `γ_N` scan, which ran on both:
**AK(3)'s near-cubic descendants reach defect 2 in 4/500 = 0.8 % of tested states, the
ladder's in 51/200 = 25 %.** AK(3)'s stable class sits measurably higher in the defect
landscape than matched AC-trivial inputs — which is consistent with AK(3) being hard, and is
the first quantitative version of that on this line. It is **not** evidence of an
obstruction: the ladder sources have varied `γ_N` at rank 2 (inherited exactly by their
triangulations, §2), and that was not controlled for.

### 4.4 What the `γ_N = 0` null is worth here

**Zero `γ_N = 0` states were found**, and the null is weak by construction:

* in run 1 only **500 of 66,756** collected states were tested (0.75 %) and the pool was
  then lost, and 200 of 29,678 on the ladder — those deep scans were budget-bound. **This is
  fixed in §4.5**, where the pool is persisted and 45,111 of 45,264 are decided exactly;
* the in-search scan tested **nothing** (`gamma_tested: 0` in both runs): a near-cubic state
  at rank `N` has census `2^N ≥ 2^10`, above the in-search cap. Every `γ_N` number here comes
  from the post-hoc deep scan;
* the ladder shows the scan *can* see low defects (51 states at defect 2), so the instrument
  works — and the detection rate for a `γ_N = 0` state is **now measured**: 1.51 % on a
  matched thickenable control (§4.6), which is what makes §4.5's null readable
  (`experiments/lessons/calibrate-one-sided-hunts-on-a-positive-ladder.md`).

That gap is now closed — see §4.5, where the pool is persisted and **exhaustively**
decided.

### 4.5 The exhaustive decision of the near-cubic pool — 45,111 states, no `γ_N = 0`

The first run's pool was never written to disk and was lost. It has been regenerated with
**every near-cubic state persisted as it is found** (gzipped JSONL with its rank, `Σ|δ|`,
census, provenance and the **full `SPLIT` trace back to its root**), and then decided.

* **Instrument.** A numba kernel (`fast_min_defect`) that enumerates the *entire* compatible
  rotation family by mixed-radix over the per-germ cyclic orders and returns the exact
  minimum defect. **No sampling anywhere.** It is validated in `selftest` against the audited
  oracle `gamma_N_factorial_n` on 44 states — cubic, near-cubic, AK(3) and its rank-9
  triangulation — with **exact agreement on every one**. Throughput 8.25 ms/state at census
  8,192 (~110 states/s), versus 0.12 s/state for the pure-Python oracle.
* **Pool.** Search seed 2026, 47 roots, 430 s: **45,264 states**, all distinct as ordered
  multisets of canonical cyclic words, distributed
  `(rank, Σ|δ|) → {(12,2): 912, (12,4): 42,534, (13,2): 332, (13,4): 1,486}`.
* **Decision.** 470 s; **45,111 of 45,264 decided exactly** (153 left by the budget cut).

> ### Exact defect histogram over 45,111 states of AK(3)'s stable class, ranks 12–13
>
> | `γ_N` | defect | count | share |
> |---|---|---|---|
> | **0 (thickenable)** | 0 | **0** | **0.000 %** |
> | 1 | 2 | **527** | 1.17 % |
> | 2 | 4 | 40,100 | 88.89 % |
> | 3 | 6 | 4,484 | 9.94 % |
>
> Split by distance to cubic form:
>
> | `Σ|δ|` | states decided | `γ_N = 1` | `γ_N = 2` | `γ_N = 3` |
> |---|---|---|---|---|
> | 2 (one SPLIT from cubic) | 1,232 | **0** | 1,028 | 204 |
> | 4 (two SPLITs from cubic) | 43,879 | 527 | 39,072 | 4,280 |

**Three things this settles, and one it does not.**

1. **No thickenable member was found in 45,111 exactly-decided states.** This is the largest
   exhaustively decided region of AK(3)'s stable class measured on this line, and unlike
   every previous null on it, **nothing here is sampled** — each state's whole compatible
   census was enumerated, so each individual verdict is a certificate, not a bound.
2. **527 members at `γ_N = 1`.** Before this run, `γ_N = 1` was known for AK(3)'s class at
   exactly two places: the single rank-2 gateway of `gateway_scan.json` and the four states
   the first (sampled) deep scan happened to hit. There are now 527 explicit ones, with
   replayable chains.
3. **Proximity to cubic form is ANTI-correlated with low defect here.** The states one
   `SPLIT` from cubic (`Σ|δ| = 2`) are **0/1,232** at `γ_N = 1`, while the states two SPLITs
   away are 527/43,879 = 1.2 %. Whatever drives the defect down, it is not "get closer to
   cubic". This directly undercuts the route's own premise and is recorded as **T-S17**.
4. **What it does not settle**: the pool is the near-cubic frontier of *one* 430-second
   search from 47 roots — a vanishing fraction of the stable class — and the dedup is on the
   multiset of canonical cyclic words, **not** up to generator relabelling, so 45,264 is an
   upper bound on the number of genuinely distinct complexes. **The missing positive control
   is supplied in §4.6** — 759 `γ_N = 0` states at rank 12–13 from a matched thickenable
   source — so the null below is exact per state *and* calibrated as a claim about the
   region, though still bounded by the pool's coverage of the class.

---

### 4.6 THE POSITIVE CONTROL — the region does contain certificates, and the instrument finds them

§4.5's null was uncalibrated: with no `γ_N = 0` state known to exist anywhere at rank 12–13,
"AK(3) has none" and "the region has none, for anybody" were indistinguishable. That is a
**reachability** question, not a search-sensitivity one, and it is settled by construction.

**Design.** Identical pipeline, identical kernel, identical budgets — only the rank-2 defect
of the source changes. Sources are AC-trivial rank-2 presentations of total length 13 with
both relators ≥ 4 and **`γ_N = 0` at rank 2**, so their rank-9 chord triangulations are
thickenable *by construction* (`S3_AUDIT` Lemma S3′: chord refinement preserves the whole
defect histogram). Matched to AK(3) on rank, length, root rank and `Σ|δ| = 14`.

> ### The control fires: **759 `γ_N = 0` states in 50,320**
>
> Source `("XYXXY","XXYXYXXY")` (`γ_N = 0` at rank 2), 33 roots, all 50,320 pooled states
> decided exactly:
>
> | `γ_N` | defect | count | share |
> |---|---|---|---|
> | **0 (thickenable)** | 0 | **759** | **1.51 %** |
> | 1 | 2 | 23,083 | 45.87 % |
> | 2 | 4 | 26,439 | 52.54 % |
> | 3 | 6 | 39 | 0.08 % |
>
> by distance to cubic: `Σ|δ| = 2` → **103/6,300 = 1.63 %**; `Σ|δ| = 4` → **656/44,020 = 1.49 %**.

**One control hit, verified six ways** (the protocol reserved for an AK(3) hit, run here to
validate the instrument):

```
source ("XYXXY","XXYXYXXY")   rank 2, gamma_N = 0, AC-trivial
  --7 chord refinements-->    root (XYC,fYG,axx,byx,caY,dYX,eXD,fxB,gXE)   rank 9
  --3 SPLITs-->               (IjC,YGf,aii,xby,caj,dYH,xEd,fhB,gXE,hEd,iby,jGf)   rank 12
```
1. structural: triangular, non-degenerate, balanced, multiplicities `{2,3,4}`;
2. **oracle** `gamma_N_factorial_n`: defect **0**, genus **0**, census 9,216, 2 accepting orders;
3. fast numba kernel agrees exactly;
4. **Todd–Coxeter**: trivial group, index 1;
5. **`witness_check_n`** on the accepting rotation: `defect 0, genus 0, compatible True`;
6. **chain replays**: `verify_chain` from the root passes, and the root **un-merges in
   exactly 7 steps** to `("xxyxy","XYXXYXYX")` = the source up to rotation and inversion.

### 4.7 What the calibration does to AK(3)'s null

| | states decided exactly | `γ_N = 0` | rate |
|---|---|---|---|
| **control** (thickenable rank-2 source) | 50,320 | **759** | **1.51 %** |
| **AK(3)** | 45,111 | **0** | **0.00 %** |

Under the control's rate one would expect ≈ **681** thickenable states among AK(3)'s 45,111.
**Zero were found.** So:

* the rank-12/13 near-cubic region is **not** structurally `γ_N ≥ 1` — it contains
  certificates in quantity, and this pipeline reaches them and this kernel decides them;
* therefore **AK(3)'s 0/45,111 is a genuinely informative null**, not an instrument artefact
  and not a statement about the region;
* it is the first calibrated negative this line has produced about AK(3)'s stable class at
  high rank.

**Four caveats, all binding.**
1. **The control is ONE source.** The 300 s search budget was consumed by source 0 (33 roots
   × 9 s), so sources 1–5 were never searched — `by_source` in the summary has a single key.
   The 1.51 % is that source's descendant rate, not a cross-source constant, and it must not
   be treated as a universal prior.
2. **No p-value.** Both pools are move-tree frontiers, not independent draws
   (`contrast-length-confound.md`).
3. The two pools come from different searches (seeds 2026 / 5150) and differ slightly in
   size and `(rank, Σ|δ|)` mix; the comparison is like-for-like in construction, not
   randomised.
4. **T-S17 does not reproduce in the control** and must be narrowed. AK(3)'s `Σ|δ| = 2`
   states were 0/1,232 at `γ_N = 1` against 527/43,879 further out; the control's rates are
   essentially flat and if anything favour *closer* to cubic (1.63 % vs 1.49 %). So the
   anti-correlation is an **AK(3)-specific** observation, not a property of the region. T-S17
   is rewritten accordingly in §7.

### 4.8 The mechanism, traced step by step

`chaintrace` records `γ_N` at the rank-2 base, after **every** chord refinement, and after
every `SPLIT`:

| base | `γ_N` across the 8 chord refinements | then per SPLIT |
|---|---|---|
| AK(3) | `4,4,4,4,4,4,4,4` — **constant** | `4, 4, 4, 4` |
| thickenable control 0 | `0,0,0,0,0,0,0,0` — **constant** | `2, 2, 4, 4` |
| thickenable control 1 | `0,0,0,0,0,0,0,0` — **constant** | `2, 2, 4, 4` |

(defects, i.e. `2·γ_N`; chord-defect constancy 3/3 chains.)

Two things at once. **(a) A live check on Theorem S3 / `S3_AUDIT` Lemma S3′**: the defect is
constant across every chord refinement, on every chain, exactly as the lemma predicts —
independent confirmation on a fresh corpus. **(b) The destruction is entirely the `SPLIT`s'
doing**: the greedy cost-guided chain from a thickenable base loses `γ_N = 0` at the *first*
`SPLIT` and never recovers, consistent with the 67 % destruction rate of §3.2. That the
broader beam search nonetheless retains 759 thickenable states shows destruction is the
*typical* behaviour of `SPLIT`, not the inevitable one — which is precisely why a
cost-greedy search is the wrong instrument for a certificate hunt, and why S6's advice to
propose creator-moves rather than `SPLIT` is the right next step.

## 5. Two corrections to the route's cost model

### 5.1 A cubic form of AK(3) is **not** cheap to decide

For a cubic triangular presentation every `m_g = 3`, so the compatible-rotation census is

```
    prod_g (m_g - 1)!  =  prod_g 2  =  2^N          (N = rank)
```

exactly — which reproduces S4 §1's own measured sizes 4, 8, 16 at `N = 2, 3, 4`.

Now bound the rank a cubic form of AK(3) could have. One `SPLIT` changes the cost by
`ΔΣ|δ| = −k − 2 + |k − 2|`, which is `−4` for every `k ≥ 2` and `−2` for `k = 1`: **no
`SPLIT` reduces `Σ|δ|` by more than 4.** AK(3)'s triangulations start at `Σ|δ| = 14` and
rank 9, and each `SPLIT` adds exactly one to the rank, so

```
    a cubic form of AK(3) in this calculus has rank >= 9 + ceil(14/4) = 13,
    hence census >= 2^13 = 8,192 ;   AK(3)'s own census is 5!*6! = 86,400 = between 2^16 and 2^17.
```

So the cheapness claim survives *only* for ranks 13–16 and **inverts at rank 17**
(`2^17 = 131,072 > 86,400`). S4 §7.2's "the cubic census is 16 cases where AK(3)'s rank-2
census is astronomically larger" is a rank-4 number that is off by roughly three orders of
magnitude at the rank AK(3) would actually land on, and it reverses outright a little beyond
it. This is the same error family the S3 audit found in `S0` §2 ("more stabilization … makes
the test cheaper"): rank growth adds letters, and the census is exponential in the rank.
**The cubic route's motivation is the normal form and the 3-regular link, not decision cost.**

*(The `Σ|δ|` bound above is also the reason no cubic form of AK(3) can be shallow: at least
four `SPLIT`s are needed, and — see §4 — the searches reach `Σ|δ| = 2` in three and then
stall on the T-S11 parity plateau, exactly one unit short.)*

### 5.2 The 64.29 % thickenable fraction is a base rate, not a prior for AK(3)

S4 §4c already flags both caveats (not independent draws; every member is a tiny AC-trivial
presentation). They bind harder than the brief allows: the 27,648/43,008 figure is the
fraction over *all* non-degenerate cubic triangular presentations of 1 at rank 4, whereas
the objects the route would actually produce are the `SPLIT`-descendants of a **specific**
root whose defect is pinned at 4 by §2 and which — per §3 — `SPLIT` is measured never to
lower. The base rate and the conditional rate are different quantities; only the second is
the route's prior, and the flip census is the first direct measurement of it.

---

## 6. Status of the route after this file

| question | status |
|---|---|
| **Q-red for AK(3)** (cubic form, all relators cyclically reduced) | **ANSWERED YES** — two explicit rank-13 witnesses, verified four ways (§4.2). This closes S4 §0 item 6 and S4 §7.3's first branch **for AK(3)** |
| Q-red in general (every balanced presentation of 1) | **still OPEN** — Lemma S4.6 / Observation S4.5 unproved; two witnesses are not a theorem |
| can `SPLIT` lower `γ_N`? | **YES, measured** — `γ_N = 2 → 1` from AK(3)'s triangulation (§3.4). My own monotonicity conjecture is refuted |
| can `SPLIT` deliver a `γ_N = 0` certificate for AK(3)? | **OPEN, with a large CALIBRATED exact null against it**: 45,111 states decided exactly, **0 thickenable**, against a matched control that yields 1.51 % (§4.6–4.7). Expected ≈ 681, observed 0 |
| does the rank-12/13 region contain `γ_N = 0` states at all? | **YES — 759 exhibited** (§4.6). The AK(3) null is a fact about AK(3), not about the region |
| which step destroys thickenability? | **the `SPLIT`s.** Chord refinement holds `γ_N` exactly constant on every traced chain (§4.8, live check on Thm S3) |
| does driving toward cubic form drive toward thickenability? | **NO, measured**: `Σ|δ| = 2` states are 0/1,232 at `γ_N = 1`; `Σ|δ| = 4` states are 527/43,879 (§4.5, T-S17) |
| is AK(3) harder than matched AC-trivial inputs for this search? | **NO** on the cubic-form axis (2/28 vs 0/35, §4.3), **YES** on the defect axis (0.8 % vs 25 % of tested near-cubic states reach defect 2) |
| is the cubic regime cheap to decide at AK(3)'s scale? | partly — `2^13 = 8,192` at the minimum rank, inverting against AK(3)'s own 86,400 at rank 17 (§5.1) |
| does the 64 % rank-4 thickenable fraction transfer to AK(3)? | **NO** — and the two forms actually found are 0/2 thickenable (§5.2) |
| is the route BLOCKED (FRAMING §3)? | **NO — it is the most alive it has been.** It delivered a normal form for AK(3) and the first stable-class member below `γ_N = 2` |

**Next concrete step**, in priority order:

1. **Done — see §4.5.** The pool is persisted and 45,111 of 45,264 states are decided
   exactly. Zero thickenable. The next version of this step is *width*, not depth: the pool
   is one search's frontier, and the anti-correlation in §4.5 says the near-cubic frontier
   is the wrong place to look.
2. **Push from `γ_N = 1`.** There are now **528+ explicit `γ_N = 1` members** of AK(3)'s
   stable class (527 from §4.5 plus `C1`), all with replayable chains, against the single
   rank-2 gateway previously known. `γ_N = 1` is a *tie* with that gateway, not a new record
   — but it is now a large, cheap, structured population instead of a lone point. Re-root the
   search at them and apply the moves `S6` classifies as *creators* (general AC2, spelling
   choice) rather than `SPLIT`, which §4.5 shows does not get there.
3. **Done — §4.6.** The control yields 1.51 %. What remains is *breadth*: only one control
   source was actually searched (§4.6 caveat 1), so run the remaining five to see how much
   the rate varies across thickenable sources before treating 1.51 % as a reference.
4. Q-red in general (Lemma S4.6) — now with two worked instances to generalise from.

## 7. Traps added to the line

* **T-S12.** *The cubic census is `2^N`, not "16 cases".* Any claim that high rank makes the
  Neuwirth decision cheaper must name the rank: the census is exponential in it. Same failure
  family as `S0` §2 (see `S3_AUDIT.md` §2).
* **T-S13.** *A base rate over an exhaustively enumerated tiny class is not a prior for a
  hard instance's descendants.* The 64.29 % of S4 §4 is measured over rank-4 AC-trivial
  presentations; the two cubic forms this route actually produced are 0/2 thickenable.
* **T-S14.** *Every triangulation of AK(3) has `γ_N = 2` exactly* (`S3_AUDIT` Lemma S3′).
  Enlarging the set of triangulation roots can only diversify a *search*; it can never move
  the starting `γ_N`.
* **T-S15.** *A move's flip census is a statement about the corpus's rank, not about the
  move* — §3.4. `SPLIT`: 0 creations in 1,470 rank-5 opportunities, and a demonstrated
  `γ_N` drop at rank 9.
* **T-S17 (NARROWED by the control — do not quote the original form).** Over 45,111 exactly
  decided states of **AK(3)**'s stable class, the ones closest to cubic (`Σ|δ| = 2`) had
  **zero** members at `γ_N = 1` while those further out had 527. **This does NOT generalise**:
  the matched thickenable control's rates are flat (`Σ|δ| = 2`: 1.63 %, `Σ|δ| = 4`: 1.49 %,
  §4.6). So the anti-correlation is an observation about AK(3), not about the cubic regime.
  The transferable half is the weaker statement: *a normal-form target and a thickenability
  target need not point the same way — check, do not assume.*
* **T-S18.** *A "the region may simply be empty" doubt is a reachability question and is
  fixable by construction.* Do not report an exact-per-state null over a region until a
  matched input with a **known** positive has been pushed through the same pipeline. Here it
  took one extra run and converted 0/45,111 from uninterpretable into the line's first
  calibrated high-rank negative.
* **T-S16.** *A ranking beam cannot cross a plateau whose exit is cost-increasing.* S4's
  0/48 on AK(3) was an artefact of exactly that (T-S11's `Σ|δ| = 2` plateau); adding 30 %
  random beam fill turned it into 2/28. Before reading any search null on this line, check
  that the search can take a cost-increasing move at all.

---

## 8. Reproduction

```bash
export PYTHONPATH=/home/user/ACSolverX
python3 experiments/stable_ac/fable/cubic_split_search.py selftest
python3 -m experiments.stable_ac.fable.guarded_run --preflight --timeout 55 -- \
    python3 experiments/stable_ac/fable/cubic_split_search.py flips --budget 40 --corpus 20
python3 -m experiments.stable_ac.fable.guarded_run --timeout 500 -- \
    python3 experiments/stable_ac/fable/cubic_split_search.py flips \
      --budget 460 --corpus 400 --source-length 9 --flip-children 30 \
      --deep-cap 120000 --include-ak3 --out results/stable_ac/fable/s4b_flips.jsonl
python3 -m experiments.stable_ac.fable.guarded_run --timeout 500 -- \
    python3 experiments/stable_ac/fable/cubic_split_search.py ak3 ...
python3 -m experiments.stable_ac.fable.guarded_run --timeout 500 -- \
    python3 experiments/stable_ac/fable/cubic_split_search.py ladder ...
```

Exhaustive decision of the persisted pool (§4.5):

```bash
python3 -m experiments.stable_ac.fable.guarded_run --timeout 520 -- \
    python3 experiments/stable_ac/fable/cubic_split_search.py ak3 --budget 430 \
      --per-root 9 --roots-per-source 400 --mode tiebreak --beam 60 --depth 20 \
      --max-children 300 --diversity 0.30 --deep-threshold 4 --seed 2026 \
      --pool-out results/stable_ac/fable/s4b_pool.jsonl.gz \
      --out results/stable_ac/fable/s4b_ak3_run2.jsonl
python3 -m experiments.stable_ac.fable.guarded_run --timeout 540 -- \
    python3 experiments/stable_ac/fable/cubic_split_search.py decide \
      --pool-in results/stable_ac/fable/s4b_pool.jsonl.gz \
      --decide-out results/stable_ac/fable/s4b_decided.jsonl.gz --decide-budget 470
```

Positive control (§4.6) and the chain trace (§4.8):

```bash
python3 experiments/stable_ac/fable/cubic_split_search.py control --budget 300 \
    --per-root 9 --roots-per-source 60 --ladder 6 --want-defect 0 --diversity 0.30 \
    --pool-out results/stable_ac/fable/s4b_control_pool.jsonl.gz --seed 5150
python3 experiments/stable_ac/fable/cubic_split_search.py decide --by-source \
    --pool-in results/stable_ac/fable/s4b_control_pool.jsonl.gz \
    --decide-out results/stable_ac/fable/s4b_control_decided.jsonl.gz
python3 experiments/stable_ac/fable/cubic_split_search.py chaintrace --ladder 2 \
    --split-steps 4 --deep-cap 400000
```

Artefacts: `results/stable_ac/fable/s4b_flips.jsonl`, `s4b_ak3.jsonl`, `s4b_ak3_run2.jsonl`,
`s4b_ladder.jsonl`, **`s4b_pool.jsonl.gz`** (45,264 near-cubic states with full chains),
**`s4b_decided.jsonl.gz`** + `s4b_decided_summary.json` (45,111 exact verdicts),
**`s4b_control_pool.jsonl.gz`** (50,320 control states) and
**`s4b_control_decided.jsonl.gz`** + `s4b_control_decided_summary.json` (50,320 exact
verdicts, 759 thickenable), `s4b_control.jsonl`;
guard ledger `results/stable_ac/fable/guard_ledger.jsonl`; child logs
`results/stable_ac/fable/guard_logs/`.
