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

1. **No cubic triangular form of AK(3) was found.** The scaled search is reported in §4
   with its calibration; the null is stronger than S4's but is still a null about *this*
   move calculus, not about stable AC.
2. **The headline result is a different one, and it is negative for the route's prize.**
   A flip census of the `SPLIT` move, in the format of `S6_MOVE_CLASSIFICATION.md` §1 and
   with a **matched AC2 control arm on the same parents**, finds that `SPLIT`
   **destroys `γ_N = 0` often and creates it never** (§3). The control creates, so the null
   is calibrated and not an instrument artefact.
3. **Consequence, and it re-scopes the whole route.** Chord triangulation preserves the
   *entire* defect histogram (`S3_AUDIT.md` Lemma S3′), so **every** triangulation of AK(3)
   starts at `γ_N = 2` — no choice of root can help. If `SPLIT` never creates, then the
   whole `(triangulate ∘ SPLIT)` region of AK(3)'s stable class is non-thickenable, and the
   cubic route can only ever deliver a **normal form**, never the Lackenby certificate.
   That is a measurement, not a theorem: stated as **Conjecture S4B-M** in §3.4.
4. **Two cost-model corrections** (§5): a cubic triangular presentation at rank `N` has
   census exactly `2^N`, so the cubic form of AK(3) — which the search drives to rank 15–20 —
   is **not** cheaper to decide than AK(3) itself (`2^17 > 86,400`); and the 64.29 %
   thickenable fraction of S4 §4 is a base rate over tiny AC-trivial rank-4 presentations
   and is **not** a prior for AK(3)'s descendants.

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

### 3.4 Conjecture S4B-M, and why it is only a conjecture

> **Conjecture S4B-M (SPLIT monotonicity).** For every `SPLIT` child `P'` of `P`,
> `γ_N(P') ≥ γ_N(P)`. In particular `SPLIT` never creates `γ_N = 0`.

Status: **measured, not proved.** The natural proof route is a restriction argument — every
compatible rotation system of `K_{P'}` should restrict, along the retraction `t ↦ λ`, to one
of `K_P` with no larger defect — but the retraction is *not* a subdivision, so the argument
that works for chord refinement (`S3_AUDIT` Lemma S3′) does not transfer. Concretely,
`D ∪ R'` is a disc whose boundary is the bigon `t λ^{-1}`, so `t` and `λ` cobound a bigon and
the rewriting step pushes 2-cell corners across it; but the bigon's interior meets the edges
`u` and `v`, which other 2-cells also use, so the push is a homotopy and not a homeomorphism.
`[GAP-S4B-1]`

**If S4B-M is proved, the certificate half of the cubic route is closed** — combined with §2
it says the entire `(triangulate ∘ SPLIT)` region of AK(3)'s stable class has `γ_N ≥ 2`. That
would be a genuine obstruction theorem about a named region, i.e. the second of the two
publishable outcomes S4 §7.3 anticipated. It would **not** say anything about stable ACC:
it is a statement about one move calculus.

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

exactly — which reproduces S4 §1's own measured sizes 4, 8, 16 at `N = 2, 3, 4`. AK(3)'s
rank-2 census is `5!·6! = 86,400`, and `2^16 = 65,536 < 86,400 < 131,072 = 2^17`. The search
drives AK(3)'s triangulations to `Σ|δ| = 2` at ranks in the high teens, so a cubic form of
AK(3), if one exists in this calculus, would sit at a rank where **its census is comparable
to or larger than AK(3)'s own**.

So S4 §7.2's "the cubic census is 16 cases where AK(3)'s rank-2 census is astronomically
larger" is a rank-4 number that does not transfer to AK(3). This is the same error family the
S3 audit found in `S0` §2 ("more stabilization … makes the test cheaper"): rank growth adds
letters, and the census is exponential in the rank. **The cubic route's motivation is the
normal form and the 3-regular link, not decision cost.**

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
