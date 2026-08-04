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
   search's near-cubic pool are also at `γ_N = 1`. **No `γ_N = 0` was found**, but the route
   is no longer inert: it moves the obstruction in the useful direction.
3. **A flip census of `SPLIT` on small instances says the opposite — and it is wrong to
   extrapolate it.** On a rank-5 corpus, `SPLIT` destroyed `γ_N = 0` in 643/960 cases and
   created it in **0/1,470**, against a matched AC2 control that created in 14/1,470 (§3).
   I drafted a monotonicity conjecture on that measurement and **my own rank-9→13 search
   refutes it** (§3.4). Recorded in full, including the refutation, because the failure mode
   — a clean small-instance null extrapolated past the regime it was measured in — is the
   reusable lesson here.
4. **Two cost-model corrections** (§5): a cubic triangular presentation at rank `N` has
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

## 3. The SPLIT flip census — the decisive measurement

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

## 4. The scaled search for the cubic form, and its calibration

<!--SEARCHTABLE-->

---

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
| Q-red for AK(3) (cubic form, all relators cyclically reduced) | **OPEN**; scaled search found none; null calibrated in §4 |
| can `SPLIT` deliver a `γ_N = 0` certificate for AK(3)? | **measured NO** (§3), conjectured no (S4B-M), **not proved** |
| is the cubic regime cheap to decide at AK(3)'s scale? | **NO** — census `2^N` (§5.1) |
| does the 64 % rank-4 fraction transfer to AK(3)? | **NO** — base rate, not conditional (§5.2) |
| is the route BLOCKED (FRAMING §3)? | **not blocked, but re-scoped**: it does not reduce to another open problem, and its value is now the normal-form question and Conjecture S4B-M, not the certificate |

**Next concrete step**, in priority order:
1. Prove or refute **Conjecture S4B-M** (§3.4). A proof closes the certificate half of the
   route with a theorem and is the first genuine obstruction on the S-line.
2. If S4B-M holds, the certificate hunt must move to move classes `S6` measures as
   *creators* — general AC2 slides and spelling choice — which is what `S12` already does.
3. Q-red itself (Lemma S4.6 / Observation S4.5) remains open and is now a pure normal-form
   question with no certificate payoff attached.

## 7. Traps added to the line

* **T-S12.** *The cubic census is `2^N`, not "16 cases".* Any claim that high rank makes the
  Neuwirth decision cheaper must name the rank: the census is exponential in it. Same failure
  family as `S0` §2 (see `S3_AUDIT.md` §2).
* **T-S13.** *A base rate over an exhaustively enumerated tiny class is not a prior for a
  hard instance's descendants.* The 64.29 % of S4 §4 is measured over rank-4 AC-trivial
  presentations; the route's actual population is the `SPLIT`-descendants of one pinned root.
* **T-S14.** *Every triangulation of AK(3) has `γ_N = 2` exactly* (`S3_AUDIT` Lemma S3′).
  Enlarging the set of triangulation roots can only diversify a *search*; it can never move
  the starting `γ_N`.

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

Artefacts: `results/stable_ac/fable/s4b_flips.jsonl`, `s4b_ak3.jsonl`, `s4b_ladder.jsonl`;
guard ledger `results/stable_ac/fable/guard_ledger.jsonl`; child logs
`results/stable_ac/fable/guard_logs/`.
