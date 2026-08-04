# S3_AUDIT — adversarial audit of `S3_SUBDIVISION_INVARIANCE.md` (task A5)

Auditor: independent adversarial agent, 2026-08-04. Branch
`claude/stable-ac-conjecture-stabilization-rwo9as` (**must be merged into `fable/proof` by
the user**). Target: `results/stable_ac/theory/fable/S3_SUBDIVISION_INVARIANCE.md`.
S3 itself was **not edited**; nothing was committed. All code written for this audit lives
in the session scratchpad (`audit_s3/mygamma.py`, `triangulate_audit.py`, `audit_run*.py`,
`calib.py`) and reuses nothing from `experiments/stable_ac/fable/high_rank_refine.py`,
which was never opened.

---

## VERDICT: **AMEND**

Theorem S3's mathematical core — *an elementary chord refinement is a CW subdivision, so
`|K_{P'}| ≅ |K_P|` and the `γ_N = 0` predicate is invariant* — **survives the attack and is
correct**. I could not refute it, and 1,525 independent triangulations produced zero
counterexamples.

But S3 as written must not be adopted in its current form. It contains one **false claim
presented as a measured fact**, on which it founds a **new permanent trap (T-S6)** for the
whole line; it **understates its own theorem** (the correct statement is far stronger and
needs none of the unverified topology); it **misstates the semantics of the predicate it
reasons about**; it is **missing two non-degeneracy hypotheses** that are live inside the
very construction it describes; and its **"BLOCKED" verdict on the S0 §3 route is broader
than what it proves**.

Seven repairs are specified in §7. Two of them (R1, R2) are corrections of statements that
are currently **wrong**, not merely imprecise.

---

## 1. THE HEADLINE PROBLEM — §3's reconciliation is a defect-vs-genus unit error, and the
##    theorem it "explains away" is actually **stronger** than S3 claims

### 1.1 What S3 says

S3 §3 tabulates

| measurement | S3's value |
|---|---|
| AK(3) rank-2 | γ_N = **2** |
| AK(3) linear-peel triangulation, rank 9, 27 letters, census 86,400 | γ_N = **4** |

and reconciles the two with

> "**γ_N itself is not a topological invariant**; only 'γ_N = 0' is. Any future use of γ_N
> as a *quantity* across different cell structures is therefore invalid …"

and then writes that sentence into the project's permanent trap list as **T-S6**.

### 1.2 What the code actually returns

`γ_N` in this repo is the **minimum genus**, `defect/2`, not the defect:

* `experiments/stable_ac/fable/neuwirth_core.py:38` — *"The Neuwirth genus potential is
  `gamma_N = min_C defect(C) / 2`"*;
* `neuwirth_core.py:290,299` — `defect = nA - nC + 2*L - nAC`, `"genus": defect // 2`;
* `neuwirth_rank_n.py:1038,1051` — `minimum_genus = minimum_defect // 2`.

Recomputed with the repo oracle `gamma_N_factorial_n` **and** with my own independent
implementation (see §5.1):

```
AK(3) rank 2                    minimum_defect = 4   gamma_N = 2   census = 86,400
S1 §4.4 rank-9 triangulation    minimum_defect = 4   gamma_N = 2   census = 86,400
full defect histograms          {4: 724, 6: 14882, 8: 55438, 10: 15356}   ***IDENTICAL***
```

The "γ_N = 4" in S3's third row is the **minimum defect**, reported in the second row's
units as if it were a genus. The two measurements do not disagree at all: **both are
γ_N = 2**. The repo already recorded the same identity for the rank-3 case
(`R1E_DISCONNECTED_LINK.md:352`: *"AK3+z root: joint rank-3 census defect = rank-2 census
defect = 4 (γ_N = 2 …)"*).

### 1.3 Consequences (all three are damaging)

1. **The evidence for T-S6 is void.** The only observation S3 offers for "γ_N's value is
   not invariant" is the 2-vs-4 pair, which is one number written twice in two units.
2. **T-S6 is FALSE on the case it was written about.** Not only is the *predicate*
   invariant under chord refinement — the entire defect histogram, the census size, the
   minimum, and the count of accepting orders are all invariant (§2). A trap that tells
   future sessions "never compare defect values across a refinement" forbids a comparison
   that is exactly, provably valid, and it retro-flags correct cross-rank comparisons
   already in the repo. This is the same failure family the trap cites
   (`parallel-runs-and-bound-direction.md`) — a quantity read in a direction it does not
   support — committed one level up.
3. **S3 understates its own theorem** and thereby loses the strongest thing the S-line has
   produced this session (§2).

If the rank-9 number had genuinely been γ_N = 4 while the rank-2 number was γ_N = 2, the
correct conclusion would have been **"Theorem S3 is refuted or the triangulation code is
buggy"** — not "the theorem is fine, only the predicate is invariant". S3 reached for a
weakening of its own theorem to absorb an anomaly instead of treating the anomaly as a
falsification. That reflex is the process failure worth recording, independently of the
arithmetic.

---

## 2. THE REPAIR THAT MAKES S3 STRONGER — a dart-level proof, with no topology in it

S3's proof routes through `|K_{P'}| ≅ |K_P|` and then through the bridge
"γ_N = 0 ⟺ thickenable", which is **[UNVERIFIED]** in this clone (§4). That is a needless
dependency: the invariance is a two-line combinatorial fact about the Neuwirth dictionary,
and it gives much more.

> **Lemma S3′ (exact census invariance).** Let `P` be any word-realized presentation
> containing a relator `r = a_1 a_2 a_3 … a_m` with `m ≥ 4`, and let `P'` be its elementary
> chord refinement at `(r, a_1a_2)` **taken literally, with no free reduction**. Then there
> is a bijection `Φ` from the compatible rotation systems of `P` onto those of `P'` with
> `defect(Φ(C)) = defect(C)` for every `C`. Hence the census size, the **entire defect
> histogram**, `γ_N`, and the number of accepting orders are all **equal** for `P` and `P'`.
> No reducedness, balance, connectivity or triviality hypothesis is used.

*Proof.* The link `Λ(P)` has one vertex per present germ and one edge per corner. Compare
corner sets. `P'` replaces `r`'s `m` corners by the 3 corners of `D_T = z a_2^{-1}a_1^{-1}`
and the `m−1` corners of `D_R = z a_3…a_m`:

* corner `(a_1,a_2)` ↦ corner `(a_2^{-1},a_1^{-1})` of `D_T`. Its endpoints are the terminal
  germ of `a_1` and the initial germ of `a_2` in both cases — **same germ pair**;
* corners `(a_t,a_{t+1})`, `3 ≤ t ≤ m−1` ↦ the identical corners of `D_R`;
* corner `(a_2,a_3)` ↦ the two corners `(z,a_3)` of `D_R` and `(z,a_2^{-1})` of `D_T`,
  which form the path `h(a_2) — z⁻ — d(a_3)`: the link edge is **subdivided** by `z⁻`;
* corner `(a_m,a_1)` ↦ the two corners `(a_m,z)` of `D_R` and `(a_1^{-1},z)` of `D_T`, the
  path `h(a_m) — z⁺ — d(a_1)`: **subdivided** by `z⁺`.

So `Λ(P') = Λ(P)` with exactly two edges subdivided, the two new vertices `z^±` having
degree 2. Every old germ keeps its degree (inverting a letter does not change how many
occurrences of that generator there are), so the census size
`∏_g (deg(g⁺) − 1)!` is unchanged — `z^±` contribute `(2−1)! = 1`. A degree-2 germ admits a
unique cyclic order and satisfies `C_{τv} = B C_v^{-1} B` automatically (a 2-cycle is its own
inverse), so every compatible `C` of `Λ(P)` extends **uniquely** to a compatible `C'`, and
suppressing `z^±` inverts this: `Φ` is a bijection. Finally `|A'| = |A| + 2`,
`|C'| = |C| + 2`, `L' = L` (both new vertices attach to germs already present), and
`|A'C'| = |AC|` (subdividing an edge of a rotation system leaves the faces in bijection).
Hence `defect(C') = |A'| − |C'| + 2L' − |A'C'| = defect(C)`. ∎

Three things follow that S3 does not have:

* the invariance is **independent of the Neuwirth bridge** — it holds whatever γ_N = 0
  turns out to mean, so §4's [UNVERIFIED] semantics cannot break it;
* it holds **without cyclic reducedness**, which S3 needs for its geometric argument;
* it kills a *separate* claim: **S0 §2's cost motivation is refuted.** The census size is
  *exactly preserved* (86,400 at rank 2 **and** at rank 9). Chord triangulation never
  thins the census, because it never touches `deg(x⁺)` or `deg(y⁺)` — it only adds
  degree-2 germs. S0 §2's "more stabilization … makes the decidable thickenability test
  cheaper — the reason the S-line is worth running" is false for this construction.
  (`S2_LITERATURE_HIGH_RANK.md:405-414` reaches the same conclusion from the literature
  side by a different route.)

**Empirical confirmation:** 1,525/1,525 triangulations reproduced the base histogram
bit-for-bit (§5.2).

---

## 3. ATTACK POINT 1 — is the chord really a chord? Two missing hypotheses

The chord construction itself is sound. Specifically:

* **`p ≠ q` always holds.** `p` and `q` are distinct *points of the boundary circle `∂D`*
  even though both map to the single vertex `v`; they coincide only at `m = 2`, which the
  definition's `m ≥ 4` excludes. S3's phrasing ("`p ≠ q` lie on `∂D`") is correct, but it
  is worth stating *why* — a reader who thinks of `p, q` as points of `K_P` will think they
  are equal, and the proof will look broken. **No repair needed, one clarifying clause.**
* **`m = 4` is fine.** `D_R` is then a triangle, exactly like `D_T`. Verified: base
  `("xyxY","xxyy")` refined at all four rotations, histogram identical in 4/4.
* **`m = 3` is also fine at the dart level** (Lemma S3′ goes through, `D_R` has length 2),
  but it produces a length-2 relator, which trips the fail-closed gate of the *fast* solver
  (`neuwirth_rank_n.py:542-546`, `UNSUPPORTED` for `len(w) < MIN_RELATOR_LENGTH`). The exact
  census `gamma_N_factorial_n` has no such gate and stays valid. This is S0's T-S4 and needs
  no repair, only a cross-reference.

**Two hypotheses are genuinely missing, and both are reachable inside S1's own construction:**

### 3.1 [MISSING-1] "no free reduction may be applied to the two new relators"

Lemma S3′ and S3's own argument are statements about the **literal** word-realized complex.
`FRAMING.md` trap 3 orders the opposite: *"Free-reduce every substituted relator completely,
including the seam."* In the non-degenerate case the two prescriptions agree (both new
relators are already reduced). In the degenerate case they do not, and the difference is not
cosmetic.

### 3.2 [MISSING-2] "`r` must be cyclically reduced" must appear in the **theorem**, not
only in §1's setup — and its failure is live

`S1_TRIANGULATION_LEMMA.md` §4.1 assumes only that the relators are **freely** reduced, and
§4.5 item 2 explicitly licenses peeling **any** adjacent pair of the *cyclic* word, noting
that for a non-cyclically-reduced relator "the rotation can shorten it". So the corner with
`a_2 = a_1^{-1}` is reachable by the very family S3 is reasoning about. At that corner the
definition relator is the literal `z a_1 a_1^{-1}` (e.g. `"axX"`), whose free reduction is
the length-1 word `"a"` — a different complex.

**Measured consequence (this is a real, if in-scope-narrow, breach).** Over 98 randomly
generated non-cyclically-reduced rank-2 bases I found 6 cases where the degenerate chord
refinement, followed by the free/cyclic reduction FRAMING trap 3 mandates, **changes the
defect** — 5 of them from `defect 2` (γ_N = 1) to `defect 0` (**γ_N = 0**):

```
('XYYyxY','XyX')  d=2  --refine-->  ('axYXY','XyX','aYy')  d=2  --reduce-->  ('axYXY','XyX','a')  d=0
('YXyYX','xxx')   d=2  --refine-->  ('aXYX','xxx','ayY')   d=2  --reduce-->  ('aXYX','xxx','a')   d=0
('xXYXYY','xxxYx') d=2 --refine-->  ('aYXYY','xxxYx','axX') d=2 --reduce-->  ('aYXYY','xxxYx','a') d=0
('yXxyy','xYxxy')  d=2 --refine-->  ('ayyy','xYxxy','aXx')  d=2 --reduce-->  ('ayyy','xYxxy','a')  d=4
('xyyYx','xyxyx')  d=2 --refine-->  ('axxy','xyxyx','ayY')  d=2 --reduce-->  ('axxy','xyxyx','a')  d=0
('Xxyxy','xYYYx')  d=2 --refine-->  ('ayxy','xYYYx','aXx')  d=2 --reduce-->  ('ayxy','xYYYx','a')  d=0
```

Note the shape carefully. This does **not** refute Theorem S3 — the refinement step itself
preserved the histogram in every one of these rows (`d=2 → d=2`); it is the *free reduction
afterwards* that moves the value. But it does refute the unqualified sentence in S3 §0:

> "So **no amount of triangulation can ever produce a thickenable member** of AK(3)'s
> stable class."

as soon as the pipeline free-reduces (as the project's own trap 3 requires) or the input
spelling is not cyclically reduced. This matters because live routes on this line —
`R7_SPELLING_SPACE.md`, `R1F_REDUCTION_AND_SPIKES.md`, the whole spike programme — work
**precisely** with non-cyclically-reduced spellings.

---

## 4. ATTACK POINT 3 — the semantics of `γ_N = 0` in this repo. S3 §1 states it **wrongly**

S3 §1 writes:

> "*Thickenable* = `|K_P|` embeds in **some 3-manifold** (Neuwirth; decidable; the repo's
> `SPHERICAL` verdict, γ_N = 0)."

That is not the repo's predicate. The repo's own bridge, in four places, is **orientable
PL**:

* `results/stable_ac/theory/fable/R1E_DISCONNECTED_LINK.md:68-77` — Theorem D: *"`K_P`
  embeds in an **orientable PL** 3-manifold if and only if there is a compatible `C` with
  `defect(C) = |A| − |C| + 2L − |AC| = 0` … i.e. `K_P` is **orientably thickenable** ⟺
  `γ_N(P) = 0`"*;
* `R1C_RANK_N_THREECONNECTED.md:29` — *"The BRIDGE `γ_N = 0 ⟺ orientably thickenable`
  (`lit_AK3_NEUWIRTH.md` Thm 2) is proved there for balanced presentations with connected
  link; **use the bridge only on balanced states**"*;
* `R7_SPELLING_SPACE.md:508,607` — *"(i) `γ_N(K) = 0`; (ii) `K` PL-embeds in some
  **orientable** 3-manifold"*; and `R7_SPELLING_SPACE.md:166` — *"compatible rotation
  systems are by construction orientable"*;
* `R7_SPELLING_SPACE.md:719` — *"No claim about non-orientable thickenings."*

Mechanically this is exactly what the code enforces: `is_compatible`
(`neuwirth_core.py:304-311`) requires `B C B = C^{-1}`, the defect is `Σ 2g_i` over
**orientable** rotation surfaces (`neuwirth_core.py:282-301`, which raises on an odd or
negative defect), and `compatible_orders_n` (`neuwirth_rank_n.py:960-986`) *derives* the
negative germ's order as the `B`-image of the reversed positive order — the family never
contains an orientation-reversing tube.

Worse, the source of the bridge is **absent from this clone**: `find . -iname
'lit_AK3_NEUWIRTH*'` returns nothing, and `literature/` holds only `fake_surfaces/`. This is
exactly the failure mode of `experiments/lessons/literature-absent-in-cloud-clones.md`, and
`S2_LITERATURE_HIGH_RANK.md:398-404` already flags **three inequivalent** definitions of
"thickenable" in play (Lackenby: *some* 3-manifold; Fulek–Tóth: *some orientable*;
Neuwirth: *closed orientable*), with the explicit instruction *"a positive under the weaker
one does not automatically discharge Lackenby's — check before citing across"*. S3 §1 picks
the **weakest** of the three and attaches the repo's `SPHERICAL` verdict to it.

**Does this break the theorem? No — but for a reason S3 does not give.** "Embeds in an
orientable PL 3-manifold" is still a property of the underlying PL space, and a CW
subdivision is a PL homeomorphism, so the invariance argument survives verbatim under the
corrected reading. And with Lemma S3′ (§2) the theorem does not touch the bridge at all.
**But the mis-stated semantics is load-bearing downstream**: the payoff chain S0 §3 step 2
runs through Lackenby Thm 1.3, whose hypothesis is the *weak* "some 3-manifold" reading; a
`γ_N = 0` hit discharges the **orientable** hypothesis, and whether that discharges
Lackenby's is exactly the open Joint-A question of `LITERATURE_STATUS.md:124-146`. S3 §1
silently closes that gap by definition. **Repair R3.**

---

## 5. ATTACK POINT 4 — independent empirical falsification

### 5.1 Instrument independence

I wrote my own Neuwirth census (`audit_s3/mygamma.py`) from scratch: named germs
`(gen, ±)`, an explicit link object with corner half-edges, face tracing via `σ∘α` (the repo
traces `α∘σ`), and **per-connected-component** Euler characteristic with the genus summed
component-wise (the repo uses the aggregate `2L` formula). It agrees with
`gamma_N_factorial_n` on minimum defect, full histogram **and** census size in 10/10 probes,
including the AK(3) fixture, the T³ fixture `("xyXY","yzYZ","zxZX")`, the S1 §4.4 rank-9
triangulation, and a non-cyclically-reduced input `("xXy","yy")`.

My triangulation code (`audit_s3/triangulate_audit.py`) implements the S3 chord refinement
plus S1 §4.5 items 1–4 (any relator, any cyclic rotation, prefix **or** suffix peel, `z := a₁a₂`
**or** `z := (a₁a₂)^{-1}`) and item 6 (shared definition). `high_rank_refine.py` was never read.

### 5.2 The table

All γ_N values via `gamma_N_factorial_n` with `cap_rotations = 2e6`, `PYTHONPATH=/home/user/ACSolverX`.
Total wall time of the three runs: ≈ 4 min.

| # | test | n | S3's prediction | **result** |
|---|---|---|---|---|
| 0 | S3 §3 row 3 recomputed (S1 §4.4 rank-9 triangulation of AK(3)) | 1 | γ_N = 4 | **γ_N = 2**, defect 4, census 86,400 — histogram *bit-identical* to AK(3)'s |
| A | 25 rank-2 bases with γ_N = 0, × 20 random full triangulations each | 500 | 0 stays 0 | **500/500 stayed γ_N = 0**; **500/500 full histogram identical** |
| B | 25 rank-2 bases with γ_N > 0, × 40 random full triangulations each | 1000 | never 0 | **0 hits**; **1000/1000 full histogram identical** |
| C | AK(3), 25 random full triangulations to rank ≤ 12 | 25 | γ_N = 2 preserved | **25/25 defect 4**; **25/25 histogram identical** |
| C′ | occurrence audit over 400 further AK(3) triangulations | 2800 new gens | each occurs twice | **0 violations** |
| F | generalised chord: `z` once in each of **two distinct** relators, vs the literal AC2-merge | 289 | (not in S3) | **289/289 minimum defect equal** |
| J | pure destabilisation `("z","Z"+v)` vs `(v,)` | 5 | (not in S3) | **5/5 histogram identical** |
| G2 | `z` occurring **once** (AC4 + Lemma S-a definition, no shortening) | 48 | (not in S3) | **0/48 changed the defect** |
| H | degenerate corner `a₂ = a₁^{-1}`, then trap-3 free reduction | 98 bases | (not in S3) | **6 defect changes; 5 of them γ_N 1 → γ_N 0** |
| E | shared definition, `z` used 3×, ≥ 2 relators shortened (S1 §4.5 item 6) | 131 | escape hatch open | **0 defect drops** — *uncalibrated null* |
| E-cal | calibration for E: random rank-3 stable neighbours of γ_N > 0 rank-2 bases | 2747 | — | **0 defect-0 hits ⇒ detection rate unmeasured** |

**Bottom line: 1,525 triangulations, 1,525 bit-identical defect histograms, zero
counterexamples.** Theorem S3's two predictions ("0 stays 0", ">0 never becomes 0") both
held without exception — and the far stronger prediction of Lemma S3′ (the *whole
histogram* is preserved) also held without exception.

**Honesty note on row E.** Per
`experiments/lessons/calibrate-one-sided-hunts-on-a-positive-ladder.md`, this null is worth
exactly its measured detection rate, and row E-cal shows I never measured one: 2,747 random
rank-3 stable neighbours of non-thickenable rank-2 bases produced no `γ_N = 0` either, so I
have no positive control proving the hunt *could* have seen a hit. **Row E must not be
quoted as evidence that the escape hatch is closed.**

---

## 6. ATTACK POINTS 2 AND 5 — the two-occurrence claim and the dividing line

### 6.1 The two-occurrence claim is TRUE, and the sign claim attached to it is FALSE

Verified: in the elementary refinement `z` occurs exactly twice; after free reduction it
still occurs exactly twice (nothing cancels — `z` is fresh); and under composition an
earlier `z` never regains a third occurrence, because a later refinement **replaces** one of
its two occurrences rather than adding one. Machine-checked: 2,800 new generators across 400
random AK(3) triangulations, **0 with occurrence count ≠ 2** (row C′).

However, S3 §4 asserts

> "… and the two occurrences carry **opposite signs**."

For the presentation **as S3 displays it in §1** this is false: both new relators are
`z·(a_1a_2)^{-1}` and `z·a_3…a_m`, and `z` carries exponent **+1 in both**. Machine check on
one elementary refinement of AK(3): `('axYXY','xxxYYYY','aYX')` → the two `a`-occurrences
are `['a','a']`. (The signs *are* opposite in the coherently-oriented boundary reading of
§2, `∂D_T = a_1a_2z^{-1}` vs `∂D_R = a_3…a_mz` — S3 §2 inverts the first before displaying
it, which is AC1 and harmless, but then §4 quotes the orientation-convention sign as if it
were a fact about the displayed words.) The sign is in any case **irrelevant**: row F
confirms 289/289 agreement with `u`, `v` unconstrained, i.e. for same-sign merges too.
**Repair R5** — strike the clause; it is currently part of the stated hypothesis of the
escape-hatch principle, so it makes that principle unusable as written.

### 6.2 The dividing line is NOT the occurrence count. T-S7 as written is refuted

S3 §4 boxes:

> "Extra generators buy nothing while they are used as abbreviations. They begin to buy
> something exactly when a stabilized generator is used **at least three times**."

and T-S7 hardens this into a permanent trap: *"Abbreviation-style stabilization (new
generator used twice) is **provably inert** for thickenability."*

The count alone proves nothing. The load-bearing hypothesis is *where* the two occurrences
sit:

* **exactly twice, in two DISTINCT relators** → the two 2-cells meet along the single edge
  `z`, their union is a disc, and the complex is a subdivision of the AC2-merged,
  AC5-destabilised presentation. This is the true general statement, strictly wider than
  S3's chord refinement (`u`, `v` arbitrary, signs arbitrary). **Verified 289/289** (row F),
  including the pure destabilisation case `("z","Z"+v)` vs `(v,)` (row J, 5/5 identical
  histograms).
* **exactly twice, in the SAME relator** → *not* a subdivision, and the count determines
  nothing. Minimal witness that the count is not sufficient:
  `("zxZy","xxy")` has defect 2 while its `z`-free shadow `("xy","xxy")` has defect 0
  (likewise `("zxZY","xyy")` defect 2 vs `("xY","xyy")` defect 0). And `("zz",)` — RP², one
  generator used exactly twice — is not a subdivision of anything `z`-free at all.
  *Caveat, stated because I am the auditor and not the advocate:* I did **not** find a
  balanced, stably-AC-legal presentation in which a new generator occurs exactly twice in
  one relator. Lemma S-a cannot produce one: the definition relator has total `z`-exponent
  sum 1, so it cannot contain exactly two `z`-occurrences. So the two-in-one-relator case
  may be unreachable — but T-S7 is a *trap* written for future readers who will apply the
  count as a test, and the count is not the test.
* **exactly once** (AC4 + a Lemma S-a definition, *no* shortening — a legal, balanced,
  in-class rank-(n+1) presentation that S3 does not mention at all) → measured inert,
  0/48 defect changes (row G2). There is a plausible reason: adding a relator only adds
  edges to the link, and a compatible rotation of the larger complex restricts to a
  compatible rotation of the smaller one with no larger defect, so γ_N should be monotone
  non-decreasing under adding relators and a pure definition can never *create* γ_N = 0.
  **I did not prove this** — it is a measured regularity plus a sketch, and it belongs in
  S3 as an open item, not as a claim.

**Repair R6:** restate the escape hatch structurally — *"the new edge `z` carries exactly
two 2-cell germs and they come from two distinct 2-cells"* — and downgrade T-S7 to the
verified form.

---

## 7. ATTACK — scope of the "BLOCKED" verdict, and the repair list

### 7.1 [SCOPE] S3 blocks less of S0 §3 than it claims

S3 §0: *"The route as stated in S0 §3 is **BLOCKED**."* But S0 §3 step 2 reads (verbatim,
`S0_HIGH_RANK_PLAN.md:65-66`):

> "If P_Δ (**or any member of the family of triangulations / their Aut(F_N) images / their
> bounded AC-neighbourhoods**) is **thickenable**, then …"

S3 proves a statement about *composites of elementary chord refinements only*. It says
nothing about:

* **Aut(F_N) images** of `P_Δ` and its **bounded AC-neighbourhoods** at rank 9. γ_N is
  emphatically *not* an AC-invariant — the entire R1/R7 programme is built on that — so the
  rank-9 AC-neighbourhood is untouched by S3 and is a genuinely larger search region than
  the rank-2 one;
* **S1 §4.5 item 6** (one definition `z := w` shortening *several* relators), which S1
  explicitly lists as a member of the triangulation family and which is **not** a chord
  refinement: `z` then occurs 3+ times. My sweep found 0 defect drops in 131 such steps, but
  that null is uncalibrated (§5.2 row E-cal) and carries no weight.

So the correct verdict is: **the naive sub-route — "chord-triangulate and test the
triangulation itself" — is a provable no-op. S0 §3 as written is not fully blocked.**
Separately, S3 §4 consequence 1 ("target the cubic regime", every generator occurring
exactly 3 times) is *not reachable by any construction in the S-line*: chord triangulation
leaves `deg(x) = 6`, `deg(y) = 7` and adds only degree-2 germs. A6 therefore needs a
construction that does not exist yet, which S3 does not say.

### 7.2 Repairs

| id | where | repair |
|---|---|---|
| **R1** | §3 table + T-S6 | **Correct the rank-9 number to γ_N = 2 (defect 4)**, state that it *equals* the rank-2 value and that the full histogram `{4:724, 6:14882, 8:55438, 10:15356}` is identical. **Delete T-S6** or replace it with its true content: *γ_N's value **is** invariant under chord refinement; if a measured value ever differs across a refinement, that is a bug or a falsification, not a fact about cell structures.* Add a units guard: `minimum_defect = 2·γ_N`. |
| **R2** | §2 | **Replace the proof with Lemma S3′ (§2 above)** or add it alongside: state the conclusion as *the census size, the whole defect histogram and γ_N are equal*, not just the predicate. This removes the dependency on the unverified bridge and on cyclic reducedness. |
| **R3** | §1 | Change "embeds in some 3-manifold" to **"PL-embeds in some *orientable* 3-manifold"**, cite `R1E_DISCONNECTED_LINK.md` Thm D, and flag that `lit_AK3_NEUWIRTH.md` is absent from this clone and that `S2_LITERATURE_HIGH_RANK.md:398-404` records three inequivalent readings — a `γ_N = 0` hit does **not** automatically discharge Lackenby's hypothesis. |
| **R4** | §1 Definition, §2 | Add the two missing hypotheses explicitly: **(a) `r` is cyclically reduced** (or: the corner `a_1a_2` is freely reduced); **(b) the two new relators are taken literally — no free reduction, in deliberate suspension of FRAMING trap 3.** Record the §3.2 measurement (6/98 bases where trap-3 reduction after a degenerate refinement moves the defect, 5 of them to 0) as the reason both are needed, and note the collision with the spelling/spike routes. |
| **R5** | §4 | **Strike "and the two occurrences carry opposite signs"** — false for the words displayed in §1, and irrelevant (row F). |
| **R6** | §4 box + T-S7 | Restate the dividing line structurally: *inert ⟺ the new edge carries exactly two 2-cell germs from two **distinct** 2-cells*. Record the verified general form (289/289) and the counterexamples to the count-only version. Add the once-occurring case as measured-inert-but-unproven. |
| **R7** | §0 | Narrow the BLOCKED verdict to *"chord-refinement composites of P are a provable no-op"*; explicitly leave open the Aut(F_N) images, the rank-9 bounded AC-neighbourhoods, and S1 §4.5 item 6. Add: **S0 §2's cost motivation is refuted** — the census size is exactly preserved (86,400 at rank 2 and at rank 9). Add that §4 consequence 1's cubic regime is not reachable by any S-line construction to date. |

---

## 8. What I could NOT break

For the record, so a future session does not re-run these:

* the CW/subdivision argument itself — correct, and I strengthened it (§2);
* the `m ≥ 4`, `m = 4`, `p ≠ q` and iterated-refinement cases — all clean;
* the two-occurrence claim (2,800 new generators checked, 0 violations);
* the prediction "γ_N = 0 stays 0" — 500/500;
* the prediction "γ_N > 0 never becomes 0" under chord refinement — 0 hits in 1,000;
* AK(3) specifically — 25/25 triangulations at γ_N = 2.

The theorem is real. What is not real is §3's reconciliation, T-S6, T-S7 as written, §1's
semantics, and the breadth of the BLOCKED verdict.

---

## 9. Reproduction

```bash
export PYTHONPATH=/home/user/ACSolverX
python3 audit_s3/audit_run.py    # parts 0, A, B, C, D, E      (~97 s)
python3 audit_s3/audit_run2.py   # probes F, G, H, I, J        (~60 s)
python3 audit_s3/audit_run3.py   # probes G2, E2               (~35 s)
python3 audit_s3/calib.py        # calibration for probe E     (~90 s)
```

One-line reproduction of the headline finding:

```python
from experiments.stable_ac.fable.neuwirth_rank_n import gamma_N_factorial_n
a = gamma_N_factorial_n(("xyxYXY","xxxYYYY"))
b = gamma_N_factorial_n(("cXY","gYY","aYX","bXA","cyB","dXX","eXD","fyE","gyF"))
assert a["minimum_defect"] == b["minimum_defect"] == 4          # gamma_N = 2, BOTH
assert a["defect_histogram"] == b["defect_histogram"]           # bit-identical
assert a["expected_cases"] == b["expected_cases"] == 86400      # census NOT thinned
```
