# Living theorem catalogue — U124 stable-AC

Status labels: **PROVEN** (identities + stable expansion + independent replay),
**INHERITED** (stated in-repo, this campaign has not yet independently audited),
**IDENTITY-CHECKED** (free-group identities hold; expansion/replay pending),
**NEGATIVE** (a precisely defined route is ruled out), **ABSENT** (cited but
missing from git).

A row is not a U124 solve unless a certificate independently replays to a free
basis and legally deletes every auxiliary generator.

---

## C0. Lemma 11 — substitution and removal — INHERITED / source missing

**Statement.** If `P = ⟨x₁,…,xₙ, y | r₁,…,rₙ, y⁻¹w⟩` presents the trivial
group and `w ∈ F(x₁,…,xₙ)`, then substituting `y ↦ w` and deleting `(y, y⁻¹w)`
is a stable-AC composite.

**Proof source.** arXiv:2408.15332 Lemma 11; reconstructed in
`results/equivalence_classes/LEMMA_11_AND_THE_126_CLASSES.md`. `PROOFS.tex` is
cited and **absent**.

**Expansion.** Definition-1 substitutions (linear) replace every `y` by `w`.
The triviality hypothesis puts `w` in the normal closure of the substituted
relators; an **unbounded** product of conjugates reduces `y⁻¹w` to `y`, then
AC5 deletes it.

**Termination.** Finite, but move count unbounded in `|w|`.

**Certificate-growth bound.** None effective; never hide this cost.

**U124.** Load-bearing for every CoV hop and every defining-generator deletion.
Does **not** itself trivialize any row.

**Audit.** Pending reconstruction of `PROOFS.tex` from the arXiv text.

---

## C1. Stable ambient automorphism principle — INHERITED / source missing

**Statement.** If `⟨r,s⟩` is a balanced presentation of the trivial group and
`φ ∈ Aut(F₂)`, then `(r,s) ~_st (φr, φs)`.

**Not a theorem.** The **unstable** pairwise principle is not proved and may
fail (Panteleev–Ushakov 2016). Lesson:
`experiments/lessons/ambient-principle-unstable-is-not-a-theorem.md`.

**Expansion.** Elementary Nielsen maps realized by two generator exchanges
(Lemma 11) plus AC3 for inner automorphisms.

**U124.** Required whenever a certificate uses a simultaneous automorphism.

---

## C2. Gated subword CoV is stable (Prop A) — INHERITED

`results/stable_ac/theory/MU_CRITERION.md`. Depends on C0–C1 and the
**trivial-group hypothesis**. μ ≤ 12 plus MM03 is the stated stable-solve
criterion. μ = 13 is never a removal.

**U124.** 36 best-table substitutions are μ-floor CoVs. None reach μ ≤ 12.

---

## C3. Two-block unimodular row reduction — INHERITED (AC19)

If both relators are, up to rotation/inversion/conjugation, `x^m y^n` and the
exponent matrix has det ±1, the pair is ordinary-AC trivial by Euclidean row
operations realized as invert/multiply/conjugate.

**U124 cheap scan.** See `tables/census_summary.json` `two_block_both_best`.
Supermove 10k on best: 0 fires that close a row.

---

## C4. Primitive one-occurrence donor elimination — INHERITED (AC19)

A free-basis donor whose companion has exponent ±1 on the complementary
generator is ordinary-AC trivial.

**U124.** Cheap one-occurrence flag is **not** a solve. Nielsen descent to a
generator is extra work and must be certified.

---

## C5. Consecutive BS(m,m+1) + Britton preflight — INHERITED (AC19)

Donor `b⁻¹ a^m b a^{-(m+1)}`, companion stable-letter exponent ±1, and cyclic
Britton reduction to a single stable letter ⇒ ordinary-AC trivial.

**Cautions.** BS(1,2) with exponent ±1 is ordinary-trivial. General BS(m,m+1)
can stall. Reciprocal BS(3,2) is not free from symmetry.

**U124.** 122,842 BS-donor states on the best table, **all** Britton-rejected
(`aca124_supermoves_10000.summary.json`). That is a **measured** negative for
this exact recognizer at 10k units on best pairs, not a mathematical
obstruction to every BS-like rewrite.

---

## C6. Rank-3 isolator corridor (Thm 3.1) — INHERITED PROVEN (AK3 note, general statement)

`literature/proofs/AK3_RANK3_COMPRESSION.md`. Hypotheses are on an arbitrary
balanced trivial pair, a word `w`, and an isolator `I` with exactly one
`b^{±1}` and at least one `z^{±1}` whose `z↦w` expansion is a source relator.
Code: `experiments/stable_ac/rank3_compression/corridors.py`.

**U124.** Bounded census on Q and the matching floors: 0 accepted corridors
at the original `|w|≤2` bound (see below). Not a mathematical obstruction.

A first bounded census (`code/q_residue_scan.py`, word ≤ 2, template ≤ 4,
`minimum_z_occurrences=2`) accepted **0** corridors on all 12 `Q_{n,δ}`
(`n=2..7`) and the 10 matching U124 best floors (0.6 s wall). This is a
**recognizer-bound negative**, not a mathematical obstruction.

C22.5: the C16 isolator template `I = z² x^{nδ} y⁻¹` with `w = ξ = y⁻¹ x y`
(`|w|=3`, `|I|=n+3`) **does** satisfy Theorem 3.1 on all 12 `Q'_{n,δ}`.
The output is **not** the C16 pair: C6 letter-substitutes `y` in the
companion, which expands the displayed `ξ`-block instead of replacing it
by `z`. Cyclic totals are `4n+15` (`δ=−1`) or `4n+17` (`δ=+1`), versus
C16’s `2n+13`. Still two C0 uses. Not a solve.

---

## C7. MS two-hop template `P_{n,δ} → Q_{n,δ}` — IDENTITY-CHECKED this campaign (14/14 exact)

**Statement.** For `n ≥ 2` and `δ ∈ {±1}`,

`P_{n,δ} = ⟨x,y | y⁻¹ x⁻³ y^δ x², y^{-(n+1)} x⁻¹ y^n x⟩`

is carried by gated CoVs `z=xy` then `z=x^n` (each `n_subs ≥ 2`) to a pair in
the rotation/inversion class of

`Q_{n,δ} = ⟨x,y | x⁻¹y⁻¹xy x² y x^δ y⁻¹x⁻², y⁻¹x²y x^{nδ} y⁻¹x⁻²⟩`.

The automorphism `y ↦ x⁻² y` makes the cyclic total of `Q` at most `n+12`.

**Proof of identities.** `code/ms_template_identities.py` re-applies
`cov.cov_branches`. For every `n=2..8` and both signs, hop1 (`z=xy`,
`n_subs=2`, isolate `x` from the MS relator) followed by hop2 (`z=x^n`,
`n_subs=4`, `iso_index=0`) reproduces **literal** `Q_{n,δ}`, not merely a
rotation class. After `y ↦ x^{-2}y`, both cyclic total and `aut_min_len`
equal `n+12` exactly. Expansion into elementary moves is still C2/C0, not a
new elementary certificate.

**U124 applicability.** Eleven archival initial rows **are** `P_{n,δ}` up to
relator swap: aca_120/34/58/81/97 (`δ=-1`, `n=3..7`), aca_121/122/123/85/98
(`δ=+1`, `n=3..7`), and aca_117 (`δ=+1`, `n=2`, the zero-descent wall).
Ten best-table floors also match the Aut-minimal shapes
`(YXXyxYx, Y^n X y² x²)` and `(YXyXYxx, Y^n X² Y² x)`. This reduces those
classes to a single power-block family. It does **not** trivialize them:
μ(Q) = n+12 ∈ {14,…,19} after the stated automorphism.

**Negative.** Iterating the template cannot re-fire on `Q` (off the MS shape).
Induction `n → n+1` via a defining relator `z⁻¹ x^n` is obstructed for `δ=+1`
and experimentally non-uniform for `δ=-1` (`LISITSA_TRANSFER.md`).

---

## C7b. Family A two-hop template — IDENTITY-CHECKED (Aut-minimal, 6/6)

**Statement.** For `n ≥ 2`,

`P(n) = ⟨x,y | y⁻¹x⁻²y⁻¹xy⁻¹x³, y⁻ⁿx⁻¹yⁿx⁻²yx²⟩`

is carried by CoVs `z=yx⁻²` (`iso_gen=x`, `n_subs=3`) then `z=yx²y⁻¹`
(`iso_gen=y`, `n_subs=2`) to a pair whose Aut-minimal representative is that
of

`Q(n) = ⟨x,y | y⁻²x⁻ⁿyx², y⁻²xyxyx⁻¹y⁻¹xyx⁻¹⟩`.

Measured: `μ(P)=2n+15`, `μ(Q)=n+16` exactly for `n=2..7`. The hop-2 spelling
is not literal `Q`; `aut_canon` agrees. The intermediate hop raises μ
(n=2: 19→21→18).

**U124.** Archival `aca_43` is `P(2)`, `aca_95` is `P(3)`. Best-table
representatives match `aut_canon(Q(n))`. Not a solve (floors 18 and 19).

**Audit.** `code/family_a_identities.py`. Because the match uses Aut-minimals,
citing C1 (stable ambient automorphism) is required before calling this a
stable reduction of those two rows.

---

## C8. Cyclic-complement criterion — INHERITED PROVEN (sufficient, not necessary)

Unimodular `(A,B)` plus `c` with `⟨A,B,c⟩ = F(a,b)` ⇒ stable triviality at
rank 3. AK(3) fails the criterion. AK(2) also fails and is still ordinary-AC
trivial. **Do not treat a failed complement search as an obstruction.**

**U124.** Scan of exact `Q_{n,δ}`, the image under `y↦x^{-2}y`, and the
Aut-minimal floor shapes, for `n=2..7` both signs:
`code/q_cyclic_complement.py`. Positive control `⟨x,y²⟩` has one rose hit;
AK3 has 0 rose hits. All 36 family cores have **0 rose hits**, so join
corank ≥ 2 in each of these three coordinates. The cyclic-complement
criterion therefore **does not fire**. That is not an AC obstruction (AK2
control). Join corank is still not an invariant: other AC-equivalent
spellings are not classified.

---

## C9. Power–Bézout corridors — INHERITED, AK3-specialized

Euclidean reduction of a defining power `t⁻¹ v^k` against a relator `a v^{-m}`
when `gcd(k,m)=1`. Portable **mechanism**; current write-up is at the AK(3)
root. Candidate for a U124 theorem if a pair has a power block and a coprime
defining exponent.

**Q diagnostic (this campaign).** No cyclic conjugate of `Q_{n,δ}`'s first
relator is `v^{±m}` times a `v`-free word for `v = y⁻¹x⁻²` (`n=2..8`, both
signs; `tables/q_peel.json` `q_r1_v_power_shape_hits = 0`). The AK3 shape
`A = a v^{-m}` is therefore not visible on that spelling. This is not an
obstruction to a different defining word.

---

## C10. MM03 length ≤ 12 — LITERATURE

Every balanced 2-generator trivial-group presentation of total length ≤ 12 is
AC-trivial (computer-assisted). Used only after a **legal** stable reduction
to such a pair, with the degenerate/order-120 caveats in `MU_CRITERION.md`.

---

## C11. Common-suffix peel — IDENTITY-CHECKED (elementary AC1+AC2)

**Statement.** If freely reduced relators satisfy `R1 = g v` and `R2 = u v`
with the same nonempty suffix `v`, then the AC2 replacement
`R2 ← R2 · R1⁻¹` (donor sign −1, displayed spelling) yields
`R2' = u g⁻¹` after free cancellation of `v`. Cyclic permutation of either
relator first is AC3 by a prefix of that relator.

**Q specialization.** For `Q_{n,δ}` one has `g = x⁻¹y⁻¹xy x² y`,
`u = y⁻¹x²y`, `v = y⁻¹x⁻²`, and the extra `x^δ` / `x^{nδ}` blocks sit
immediately before `v`. The displayed peel is

`R2' = u x^{(n-1)δ} g⁻¹ = u x^{(n-1)δ} v [y⁻¹,x⁻¹]`.

Compact: `g = XYxyxxy`, `u = Yxxy`, `v = YXX`, commutator `YXyx`.
Checked `n=2..8`, both signs, 14/14 (`code/q_peel.py`).

**If the form `u x^{kδ} v` could be restored after each peel,** then `k = n`
descends to `0` and `u v = y⁻¹x²y·y⁻¹x⁻²` freely reduces to `y⁻¹`. The pair
`(R1, y⁻¹)` then eliminates `y` from `R1` by displayed substitutions and
leaves a generator. That restoration is **not** given by repeating the same
unconjugated multiply: the second displayed peel neither restores `R2` nor
keeps a common suffix `v`.

**Orientation search.** After the displayed peel, all AC1/AC3 orientations
with suffix length ≥ 2 were enumerated (`code/q_peel_orientations.py`). Some
second peels strictly drop raw pair length relative to the inflated
post-peel pair, or drop the longest `x`-run. Independently checked on
`Q_{2,±1}`: the length-9 remainder `YXyxYYXyx` is ordinary-AC reachable in
two multiplies/rotations, but `aut_min_len` rises **14 → 18**, and the
remainder is not primitive (Whitehead minimum 9). Other length-9/7
remainders are either the original `R2` (undo) or Aut-equivalent to the
input floor. So this is **not** a well-founded descent on μ, and an
`x`-run drop is not by itself a progress measure.

**Family A analogue.** Claimed `Q(n)` spellings share prefix `y⁻²`. Then
`R2 R1⁻¹` is the conjugate `y⁻² (B A⁻¹) y²`. After AC3 the core `B A⁻¹`
is a relator. For `n=2..7` this **raises** μ (18→21 at `n=2`, and the gap
grows). Not a descent.

**Length.** Displayed Q peel never drops total length (`q_length_drops = 0`).
Adjoining `t⁻¹ v` and isolating `t` from the substituted first relator
reproduces the peeled pair; it is not a return to the original pair, and it
is unnecessary once the elementary multiply is written.

**U124.** Applies to the eleven MS-template rows once they are at `Q_{n,δ}`.
Not a solve.

**Audit.** Identities machine-checked. `ingest/advisor_wave2.md` **APPROVE**.
The n-fold peel remains counterfactual; the μ-increase of the `Q_{2,±1}`
second peel is independently checked.

---

## C12. Primitive relator ⇒ stable AC triviality — CONDITIONAL on C1, currently non-effective

**Statement.** Let `⟨x,y | r, s⟩` be a balanced presentation of the trivial
group with abelian determinant `±1`. If `r` is primitive in `F(x,y)`, then
the pair is **stably** AC-trivial, **conditional on C1**. This is not an
ordinary-AC theorem. C1’s cited `PROOFS.tex` is absent, so the Aut step is
an existence argument with unbounded unmaterialized Lemma-11 cost, not a
replayable elementary certificate.

**Proof.**
1. Whitehead’s algorithm supplies `φ ∈ Aut(F₂)` with `φ(r)` cyclically
   equal to `x^{±1}`.
2. C1 transports the pair simultaneously: `(r,s) ~_st (φ(r), φ(s))`. Each
   Whitehead second-kind factor is a Nielsen map; C1 realizes those maps
   stably. This step is **non-effective**.
3. AC1/AC3, acting only on the first relator, normalize `φ(r)` to the
   generator `x`. Write `s'` for the companion (still `φ(s)`). The exponent
   matrix of `(x, s')` is `[1 0 ; a b]` with `b = ±1`, so the total
   `y`-exponent of `s'` is `±1`.
4. Displayed generator deletion (elementary, finite). If `s' = p x^ε q`,
   change the first relator `x` by AC1/AC3 to the donor `q⁻¹ x^{-ε} q`,
   replace `s' ← s' · (q⁻¹ x^{-ε} q) = pq` by AC2, then restore the first
   relator by the inverse AC3/AC1. Repeat for every remaining displayed
   `x^{±1}`. This is not a free substitution and not Lemma 11. After at
   most `|s'|` such cycles, `s'` is a word in `⟨y⟩`. Deletion multiplies
   by conjugates of `x^{±1}`, so the `y`-exponent is unchanged and the
   freely reduced leftover is exactly `y^{±1}`. Replay:
   `code/c12_generator_deletion.py`.
5. The pair `(x, y^{±1})` is the standard trivial pair.

Pair-length μ-minimization can miss this route, because a `φ` that
shortens `r` to length 1 may lengthen `s`.

**Recognizer.** `reduce_word(w, generators=("x","y"))` with
`is_primitive_word`; abelian `gcd` of exponent sums ≠ 1 is an immediate
negative. Code: `code/primitive_relator_census.py`, aggregates in
`code/primitive_aggregates.py`. Independent replay of each Whitehead
witness via `check_word_reduction`.

**Positive examples.** Generator `x`; cyclic conjugate `xyX` (minimum `Y`).
Step 4 also replays on mixed unimodular companions `yx`, `xy`, `xyXYy`.
**Negative examples.** Commutator `xyXY` (minimum 4; leftover empty, det 0);
AK(3) relators; MS donors `YXXyxYx` (minimum 6), `YXyXYxx` (minimum 5).

**U124 applicability (implemented recognizer only).** The 248 displayed
best-table relators: 0 primitive. Histogram of Whitehead minima starts at
5 (13 words). Closest words are the MS lower donor `YXyXYxx` (6 rows) and
`YXyXYxxx` (5 rows); `aca_115` is AK(3). A Whitehead minimum of 5 is a
negative for length-1 primitivity, not a partial hit. Guarded aggregates
(`tables/primitive_aggregates.json`): cyclic stored-orientation products
`r1 r2` and `r1 r2⁻¹` are 0 primitive of 248; unique new relators among
depth-1 AC2 children, after discarding rotation/inverse copies of the
stored 248, are 11,686 words, 0 primitive, minima starting at 5. Those
counts are bounded recognizer reports. They do not exclude a primitive
relator after other AC or stable moves, and they do not trivialize any
U124 row.

**Certificate-growth.** Non-effective C1 Aut realization, then O(`|s'|`)
elementary AC1+AC2+AC3 deletions.

**Audit.** `ingest/advisor_wave2.md`: C11 APPROVE; C12 REVISE (this text
is the revision).

---

## C13. Depth-1 ordinary AC2 neighbourhood of the best table — NEGATIVE (exact, bounded)

**Statement.** For every one of the 124 best-table pairs, every AC2 child
obtained by multiplying one cyclically rotated relator by a cyclic
rotation of the other or its inverse, then freely and cyclically reducing,
has cyclic total length at least the input length, and none of those
children is a new one-occurrence pair or a two-block–both pair.

**Evidence.** `code/elementary_ac2_scan.py`: 44,016 children, 0 strict
length drops, 0 new one-occurrence, 0 new two-block–both (15.8 s, guarded).
AC1 and AC3 do not change cyclic length, so this is the complete
length-reducing depth-1 neighbourhood of `{AC1,AC2,AC3}`.

**Not an obstruction** to longer ordinary products, stable moves, or
length-increasing routes with a different well-founded measure.

---

## C14. Shared-relator inventory — DATA (not a theorem)

Best-table relators that occur at least six times as a row:

| count | word | sample rows |
|---:|---|---|
| 11 | `YXXyxYx` | aca_0,3,34,36,53,58,81,97,118,119,120 |
| 11 | `YXXXyxYx` | aca_18,20,33,40,42,63,65,91,93,102,104 |
| 9 | `YYYYYXyyyyx` | (power companions) |
| 8 | `YXXYxxyx` | |
| 6 | `YYXXyxx` | includes Family A floor aca_43 |
| 6 | `YXyXYxx` | MS lower family aca_8,85,98,121–123 |

A theorem that stably trivializes every unimodular companion of one of
these donors would clear a whole block. C12 shows the donors themselves
are not primitive, so “make the shared donor a generator by Aut” is
exactly C12 and does not fire. Full list:
`tables/primitive_relator_census.json` `shared_relators_count_ge_3`.
Inventory with syllable/BS flags: `tables/shared_donor_families.json`
(74/124 rows sit in the ten listed donor families; each companion is a
distinct rotation class, so these are parameterized families, not
duplicate spellings).

---

## C15. `YXXXyxYx` + consecutive BS(m,m+1) stall family — NAMED NEGATIVE

**Statement (classifier, not a new obstruction).** Ten best-table rows
are the pair

`⟨ y⁻¹ x⁻³ y x y⁻¹ x ,  y^{-(m+1)} x^{±1} y^m x^{∓1} ⟩`

up to swapping and the cyclic orientation that exhibits the second
relator as consecutive BS(m,m+1). Compact donor: `YXXXyxYx`. Companions
checked: aca_18,20 (m=3); aca_40,42 (m=4); aca_63,65 (m=5); aca_91,93
(m=6); aca_102,104 (m=7) — ten of the eleven `YXXXyxYx` rows; aca_33 is
the exception (not BS-shaped).

The second relator is BS(m,m+1) after rotation (`bs_mm1_shape`). The
donor’s x-exponent sum is −1. C5’s first two hypotheses therefore hold.
C5’s third hypothesis (cyclic Britton reduction of the companion to a
single stable letter) is the one that failed for **all** 122,842
BS-donor states on the best table, including these rows
(`aca124_supermoves_10000.summary.json` on theorem-strength). This is
exactly the recorded caution: exponent ±1 is not enough for general
`BS(m,m+1)`; divisibility can stall.

**Divisibility probes (this campaign).** AC3 by `y^k`, cyclic orientation of
the donor, and all 20 Whitehead automorphisms never make every y-run length
a multiple of `m` on these ten rows (`tables/c15_divisibility_scan.json`).
The explicit conjugate `y^{-(m-1)} W y^{m-1}` starts with a legal leading
run and keeps interior runs `(…,1,1,m-1)` (for `m=3`: `YYYXXXyxYxyy`,
runs `3,1,1,2`). Depth-1 AC2 from that `m=3` pair has 432 children and no
divisibility/terminal hit. Exact for those lists, not a Britton obstruction.

**Not claimed.** These ten rows are not ordinary-AC trivial by C5.
Reciprocal BS(3,2) symmetry is not used. A new theorem that replaces
Britton for this specific companion `YXXXyxYx` (for example a power–Bézout
corridor against the `x^{-3}` block, or a stable defining word that makes
Britton fire) would clear an infinite family covering those ten U124
rows.

**Recognizer.** Donor equals `YXXXyxYx` (or its rotation/inverse class)
and companion `bs_mm1_shape` with m≥3. `tables/shared_donor_families.json`.

---

## C16. Conjugate-tag exchange corridor — IDENTITY-CHECKED (independent replay), non-effective

**Statement.** Let `ξ = y⁻¹ x y`. For words `A,B` in `{x,ξ}`, `p ≠ 0`, and
`b,c ∈ ℤ`,

```
⟨x,y | A(x,ξ)· y xᵇ y⁻¹ ·B(x,ξ) , ξᵖ xᶜ y⁻¹⟩
  ~_st
⟨x,u | A(x,u)· uᵖ xᵇ u⁻ᵖ ·B(x,u) , u⁻¹ x⁻ᶜ u⁻ᵖ x uᵖ xᶜ⟩
```

by two gated CoVs (C2/C0) plus a bounded elementary core. The first output
row is **c-free**; every remaining `c` in the second row is a conjugating
flank. Hypotheses are decided by a Magnus scan: isolator height `h = −1`
with blocks `[(1,p),(0,c)]`; companion height `0`, support in `{0,1,−1}`,
exactly one block at index `−1`. The rank-2 isolator is **not** “one
`y`-letter”: `ξ₁² = Yxxy` has three. The single-`y` property is a
consequence of Gate 1. The campaign `|w|≤2` isolator census could not
represent the tag `ξ = Yxy` (length 3) and is not evidence against C16.

**U124 Q' instance.** `(A,B,p,b,c) = (x⁻¹ξ, 1, 2, δ, nδ)` **is** the
image of `Q_{n,δ}` under `y ↦ x⁻² y` (14/14 freely equal, repo
`apply_hom`). Output `S_{n,δ} = (x⁻¹ u³ xᵟ u⁻², u⁻¹ x^{-nδ} u⁻² x u² x^{nδ})`.
Checked `n=2..7`, both signs: Magnus H2/H3, Gate-1 faithfulness, one `y`
after Gate 1, and `Â` independent of `c`. Length/μ rise `n+12 → 2n+13`.

**Corollary C16.1 (δ=+1 loop) — IDENTITY-CHECKED NEGATIVE.** `ρ = x⁻¹ u⁻³ x u²`
is a cyclic rotation of `Â⁻¹` iff `δ = +1`. One further AC2 then sends
`S_{n,+1}` to `P_{n,+1}` up to the generator relabel `(x,y) ↦ (u,x)`
(Nielsen; stable transport is C1), same `n`. The corridor is a closed loop
on that branch. For `δ = −1` the rotation is absent; the endpoint donor
`x⁻¹ u³ x⁻¹ u⁻²` has x-exponent `−2` and is not BS/HNN. Multiplying by `ρ`
anyway is **illegal** and silently shortens (`n=2`: cyclic total 17→12).

**General identities.** Parameter sweep
`A ∈ {x⁻¹ξ, ξ², x, 1, x⁻¹ξ², ξ x⁻¹}`, `B ∈ {1, x, ξ x⁻¹}`,
`p ∈ {1,2,3,−2}`, `b ∈ {−1,1,2}`, `c ∈ {−5,−2,0,3,7}`: **1080/1080**
faithful, isolator, c-free.

**Stored U124 spellings that already match H2+H3.** Independent Magnus
census of all rotations/inversions of both rows:

| table | pairs with H2 | pairs with H3 | both (C16 fires) | substitutions verified |
|---|---:|---:|---:|---|
| best | 27 | 14 | 5 | 5/5 |
| initial | 20 | 15 | 1 | 1/1 |

Best hits, none of which admit the C16.1 `ρ`-rotation:

| id | `(A,B,p,b,c)` in `{x,u}` | endpoint x-exp of `Â` |
|---|---|---:|
| aca_16 | `(u⁻¹ x², x, −3, −1, 2)` | 2 |
| aca_43 | `(u x⁻¹ u x⁻¹, 1, −2, −1, 2)` | −3 |
| aca_67 | `(u⁻¹ x u⁻¹ x, 1, −3, −1, −3)` | 1 |
| aca_87 | `(u⁻¹ x u⁻¹ x, 1, −3, +1, −3)` | 3 |
| aca_90 | `(u⁻¹ x u⁻¹ x, 1, −3, −1, 3)` | 1 |

These five are extra to the MS `Q'` family. Aut-minimal spellings of `Q'`
generally **do not** fire C16 (only `Q'_{2,−1}` among `n=2,3` both signs),
so the eleven MS initial rows still need C7 then the C1 automorphism
`y ↦ x⁻² y` to reach the `Q'` spelling. C16.1’s loop is **not** claimed
for these five: they escape. Length still rises. **Not a solve.**

**Expansion.** Gate 1 and Gate 2 each use **C0 (Lemma 11)** once.
Elementary core: 7 AC2 with accompanying AC1/AC3, independent of `n`.
Certificate growth **unbounded**. Termination measure on the corridor:
`ν = (# displayed ξ-blocks, # y-letters other than the isolator)`, lex.
This is not a U124 descent.

**Audit.** Independent coordinator replay:
`code/theory_wave1_replay.py`, `tables/theory_wave1_replay.json`.
Inventor draft: `ingest/theory_wave1.md`. Cyclic-complement and
overgroup numbers in that draft were **not** re-run here.
`ingest/advisor_wave3.md`: C16 and C16.1 **APPROVE**; C17 and C18
**REVISE** (wording above is the revision).

---

## C17. Flank shear over a BS(M,N) donor — IDENTITY-CHECKED shear; C4 tail uncertified

**Statement.** Donor `D = x⁻¹ u^M x u^{-N}` with `|M−N|=1`, companion
`E(c,e) = u⁻¹ x^{-c} u^{-e} x u^e x^c`. If `c>0` and `M^{|c|} | e`, or
`c<0` and `N^{|c|} | e`, then displayed shears

```
u^e ↦ x u^{Ne/M} x⁻¹   (needs M|e)  ⇒  E(c,e) ↦ E(c−1, Ne/M)
u^e ↦ x⁻¹ u^{Me/N} x    (needs N|e)  ⇒  E(c,e) ↦ E(c+1, Me/N)
```

are finite ordinary AC1–AC3 displayed-block substitutions
(Lemma-11-free); a block `u^{±e}` requires `|e|/M` donor multiplications for
shear-down, or `|e|/N` for shear-up.
Progress `|c|`. Terminal `E(0,e)` is one-occurrence in `x` and becomes a
**C4 obligation**. The one-occurrence flag is not a solve.

**Identities.** Literal free-word shears for
`(M,N) ∈ {(2,1),(3,2),(4,3),(5,4)}`, `c ∈ {−3,0,2,5}`,
`e ∈ {N, 2N, MN, M²N}`. Positive control `(c,e)=(2,9)` with `(3,2)`
reaches `(0,4)`; `E(0,4)` has exactly one `x`.

**U124.** `S_{n,+1}` is exactly `(D_{BS(3,2)}, E(n,2))`. H3 asks
`3^{|n|} | 2`, which fails (`3 ∤ 2`). Complete shear orbit of `(c,2)`:
`{(c,2),(c+1,3)}` — the flank never drops. For each displayed `S_{n,+1}`
state, the two-shear orbit explains why this recognizer cannot lower the
flank. It neither classifies nor explains all 122,842 Britton rejects
and is not an obstruction to other BS-like moves. `S_{n,−1}` row 1 has x-exponent `−2` and is not
BS, so H1 fails. The five extra C16 endpoints above are likewise not
this BS(3,2) donor.

**Certificate growth.** If `e_j` is the inner exponent before step `j` and
`d_j = M` for shear-down or `N` for shear-up, the shear uses
`2 ∑_j |e_j|/d_j` AC2 moves, plus explicit AC1/AC3 orientations; this is
finite and effective. The C4 tail remains uncertified.

---

## C18. Coprime Bézout + radix — IDENTITY-CHECKED; U124 H1 absent on Q/Q'/S

**Statement.** At rank `≥ 3`: H1 a two-block power `c₀ x^m` with `c₀`
x-free; H2 a defining power `t⁻¹ x^k`; H3 `gcd(k,m)=1`. Each displayed
subtraction against an AC1/AC3 orientation of `c₀ x^m` is a cyclic, not
literal, identity. The replay proves isolation for the tested `k = qm+1`
chains. No full elementary Euclidean expansion for every coprime `(k,m)`
is supplied, so `gcd(k,m)=1` is presently a lattice prerequisite for
this two-row route, not an audited sufficient criterion in that
generality. Generalizes C9 off the AK3 root (C9 tested only
`v = y⁻¹ x⁻²` on `Q`’s first relator).

**Radix corollary.** A displayed `x^m` compresses to length `O(log m)`
by adjoining `t_{i+1}⁻¹ t_i²`. Move count stays `Θ(m)` (994 AC2 for
`m=1000`). This does **not** beat the `Θ(n)` certificate barrier. A
one-auxiliary defining-power round trip has two non-effective C0 uses;
a radix chain has a C0-based installation and removal for each auxiliary
defining row, in addition to its `Θ(m)` elementary multiplications.

**U124.** Every rotation and inversion of every row of `Q`, `Q'`, and
`S`, `n=2..8`, both signs, both power letters: **1764 spellings, 0 H1
hits**. Adjoining a fresh `t⁻¹ x^k` then destablizing is a round trip;
H2 must be found, not manufactured. Not an obstruction to other
spellings in the AC orbit. The five extra C16 stored hits were not part
of this 1764-spelling census.

**Audit.** Euclid, radix, and H1 census independently replayed in
`code/theory_wave1_replay.py`. `ingest/advisor_wave3.md` **REVISE**
applied: `gcd=1` is a lattice prerequisite, not a fully audited
sufficient Euclid expansion for every coprime pair.

---

## C19. δ=−1 endpoint AC2 → consecutive BS(n,n+1) — IDENTITY-CHECKED (elementary)

**Statement.** For `n ≥ 2` let `S_{n,−1}` be the C16 endpoint
`⟨ x⁻¹ u³ x⁻¹ u⁻² , u⁻¹ xⁿ u⁻² x u² x⁻ⁿ ⟩`. Rotating the second row
by `n` and the first by 2, then replacing the second row by the
product, yields a word cyclically equal to `u⁻¹ xⁿ u x⁻(n+1)`,
consecutive BS(n,n+1) with stable letter `u`. Compact product:
`x⁻ⁿ u⁻¹ xⁿ u x⁻¹`.

**Expansion.** AC3 rotate `E` by `n`; AC3 rotate `D` by 2; AC2 replace
`E` by the product; one restoring AC3 so the first row is the original
`D` (otherwise the displayed first row is `rot(D,2)`, the same cyclic
class). No C0, no C1.

**Length.** Cyclic total drops by 3: `2n+13 → 2n+10`. Uniform on `n=2..7`.

**U124.** Applies to the C16 image of the δ=−1 MS-template rows
(aca_120, 34, 58, 81, 97 for `n=3..7`). Reaching that image from the
archival spelling still uses C7, C1, and C16’s two Lemma-11 steps, so
this does **not** certify a shorter best-table representative and is
**not a solve**. After C19, C5’s exponent-±1 hypothesis holds if the
new BS is read as donor (`D` has u-exponent `+1`). `D` has opposite-sign
stable-letter boundary subwords, but their intervening x-exponent is
−1. For `n≥2` it is divisible by neither `n` nor `n+1`, so neither
boundary is a valid BS(n,n+1) Britton pinch and C5 does not fire.

**Control.** The same depth-1 neighbourhood on `S_{n,+1}` contains the
C16.1 loop onto relabeled `P_{n,+1}` and no analogous new BS family.

**Continuation.** Depth-1 AC2 and AC3 of `D` by `u^k`/`x^k` for
`k ∈ [-(n+2), n+2]` never change `D`’s pinch exponents off `{−1}`
(`code/c19_continuation.py`). Apparent `valid` pinches on AC2 children
are classified by C20 as round trips, not C5 progress.

**Audit.** `code/c16_escape_scan.py`, `tables/c16_escape_scan.json`.
`ingest/advisor_wave4.md` **REVISE** applied. Coordinator recovery:
`ingest/theory_wave3.md`.

---

## C20. One associated-subgroup pinch after AC2 of `D` by `B` is a Britton preflight return — IDENTITY-CHECKED NEGATIVE

**Statement.** Let `n ≥ 2`, `D = x⁻¹ u³ x⁻¹ u⁻²`, and `B = u⁻¹ xⁿ u x⁻(n+1)`
(the displayed spelling; cyclic conjugates appear among AC2 children).
Write `pinch` for an associated-subgroup rewrite on a freely reduced
word: replace a boundary `u⁻¹ x^{qn} u` by `x^{q(n+1)}` or
`u x^{q(n+1)} u⁻¹` by `x^{qn}`, `q ≠ 0`. This rewrite is **equality
modulo `B`**, a BS/Britton preflight. It is **not** an AC1–AC5 move
and is not a certificate.

1. On each displayed product `D·B`, `B·D`, `D·B⁻¹`, `B·D⁻¹`, each
   listed `pinch` returns a word cyclically equal to `D` or `D⁻¹`.
   This identity is uniform in `n ≥ 2` by free cancellation with the
   displayed `B`.
2. For **`n = 2..7` only**, on every `canon_pair`-unique depth-1
   ordinary AC2 child of `⟨D,B⟩` (all rotations and donor signs;
   uniqueness is cyclic/inverse canonicalization of each row, then
   slot order), **every** valid pinch occurrence on both retained
   rows rewrites to cyclic `D`, cyclic `D⁻¹`, cyclic `B`, cyclic
   `B⁻¹`, or the empty word. The empty word occurs only when the
   pinched row is the `B` slot. The `D` slot never pinches to empty.
   `other = 0`.
3. For each `n=2..7` there are exactly ten unique children with no
   valid pinch. They keep `D` and lengthen `B` (serialized with
   lengths in `tables/c20_roundtrip.json`; at `n=2` cyclic totals 17
   or 19 versus base 14).

**Identities.** `code/c20_roundtrip.py`, `tables/c20_roundtrip.json`.
Displayed four-product identities: `n=2..7` machine-checked (the
cancellation is the same for all `n≥2`). Neighbourhood counts for
`n=2..7` include every valid occurrence, not only the first.

**Expansion.** None as AC. The rewrite on `D·B` is `B`’s own pinch
sitting in the product. Empty-on-`B` is `B` reducing by its defining
relation, not a C5 finish on `D`. No C0.

**What this does not rule out.** Depth ≥ 2 AC2; AC3 of `D` by a word
that is not a generator power in the C19 scan; donors other than `B`;
raw (pre-`canon_pair`) representatives that were merged; a Britton
sequence using an intermediate spelling not in this neighbourhood.

**C12 probe (same artifact, not a fire).** For `n=2..7`, Whitehead
minima (second-kind plus signed permutations) are 7 for `D` and
`2n+3` for `B_n`. Neither relator is primitive, so C12 does not
apply to `⟨D,B⟩` or to `S_{n,−1}`. `Q'` relators and the five stored
C16 endpoints likewise fail the same recognizer. A capped Nielsen
search is consistent and is not an independent proof.

**U124.** Applies only to the C19 pair, itself the C16 image of the
`δ=−1` MS-template rows. Incoming C16 remains two non-effective C0
uses. **Not a solve, not a best-table shortening.**

**Audit.** Coordinator replay `code/c20_roundtrip.py`. Continuation
scan `code/c19_continuation.py`. `ingest/advisor_wave5.md` **REVISE**
applied.

---

## C21. Depth-2 AC2 from C20 no-pinch children; Gate 2 is not bare AC5 — IDENTITY-CHECKED NEGATIVE

**Statement.** Let `n ∈ {2,…,7}`, `D = x⁻¹ u³ x⁻¹ u⁻²`, and `B` the
C19 companion `u⁻¹ xⁿ u x⁻(n+1)`. C20 leaves exactly ten
`canon_pair`-unique depth-1 children with no valid BS(`n`,`n+1`)
pinch. All ten keep `D`. Companion lengths are uniformly
`2n+6` (four children) and `2n+8` (six children). Then:

1. One further ordinary AC2, over every globally `canon_pair`-unique
   grandchild of those ten (cyclic/inverse of each relator and slot
   order; 1580 unique at `n=2`, 3580 at `n=7`), never produces cyclic
   total below the C19 length `2n+10`.
2. All-edge parent-drop census (each of the ten parents, unique
   children of that parent, including grandchildren already seen from
   another parent): for `n≥3` there are exactly ten parent-length-drop
   edges, and each is `canon_pair`-equal to `⟨D,B⟩`. For `n=2` there
   are twelve such edges: the same ten returns plus two edges into a
   length-16 class still two above the C19 total 14. These drops are
   not a descent on the C19 length.
3. Single valid associated-subgroup rewrites on the scanned
   representatives, when the leftover is not cyclic `D`/`D⁻¹`/`B`/`B⁻¹`
   or empty, have leftover cyclic length at least 9 (`n=2`) or 10
   (`n≥3`), never strictly shorter than `D`. These are Britton
   preflights, not AC moves.
4. No globally unique grandchild is one-occurrence or two-block–both.

**C21.1 (Gate 2 destablization).** After C16 substitutions the
isolator is `I_S = u² x^{nδ} y⁻¹`. For `n=2..7` and `δ ∈ {±1}`, no
rotation or inversion of `I_S` is the generator `y^{±1}`. Bare AC5
therefore cannot remove `y` from Gate 2 as written. This does not
replace Gate 2’s C0 expansion. It is the inventor’s suggested
improvement of C16 (“try bare AC5”); it fails on the U124 instance
and on the sign-reversed twin.

**Expansion.** Depth-2 is two ordinary AC2 maps (with AC1/AC3
orientations already in `children`). C21.1 is a cyclic-word check,
no C0.

**What this does not rule out.** Depth ≥ 3; AC2 from C20’s
valid-pinch children (those are C20 round trips at depth 1);
donors other than `B`; a Lemma-11 expansion of Gate 2; rank-3
corridors that keep `y`.

**U124.** Same C19 pair as C20, still behind C16’s two C0 uses.
**Not a solve.**

**Audit.** `code/c21_depth2.py`, `tables/c21_depth2.json`.
`ingest/advisor_wave6.md` **REVISE** applied.

---

## C22. C16 Gate 1/2 as bounded ncl; C6 template ≠ C16; C15 bridge — IDENTITY-CHECKED NEGATIVE

**C22.1 (Gate 1 abelian, uniform in `n≥2`).** Write `Q'_{n,δ} = ⟨x,y | R,S⟩`
as in C16, and `ξ = y⁻¹ x y`. Then `R` is independent of `n`, cyclically
reduced of length 7, with exponent vector `(δ, 0)`. `S` has y-exponent
`−1`. `ξ` has exponent vector `(1, 0)`. The unique integer combination is
`ξ ≡ R^δ` in abelianization (`S`-coefficient `0`). In particular `ξ` is
not a product of two conjugates of `{R^{±1}, S^{±1}}`: every such product
has y-exponent in `{0, ±1, ±2}`, and the y-exponent-`0` cases are
`R^{±1} R^{±1}` or `S^{ε} S^{-ε}`, none of which has x-exponent `1`
except the one-factor class `R^δ`. Every freely reduced conjugate
`g⁻¹ R^δ g` has length at least the cyclic length 7. Since `|ξ| = 3 < 7`,
`ξ` is not a product of one or two conjugates of the Q' relators.

**C22.2 (Gate 1 depth-1 restore, uniform).** After AC4 the third relator is
the letter `u`. A restore-preserving AC2 against `R` or `S` (both `u`-free)
produces a word of free length `1+|R| = 8` or `1+|S| = n+6 ≥ 8`. `D = u⁻¹ξ`
has length 4 (`UYxy`). No such depth-1 product is `D`.

**C22.3 (machine check).** Exhaustive enumeration of products of one or two
prefix- or one-letter conjugates of `{R,S}` for `(n,δ) ∈ {2,3}×{±1}`: no
free equality with `ξ` or `ξ⁻¹`; shortest abelian match has length 7.
This is a sanity check of C22.1 on that conjugator set, not a restriction
of C22.1. A further best-first layer (not exhaustive; cap 800 extra
states, at most four factors, conjugator length ≤ 2) did not hit `ξ`.

**C22.4 (Gate 2).** On the C16 endpoint `⟨Â, B̂⟩`, write `e = u² x^{nδ}`.
The exponent matrix is unimodular. The unique combination `e ≡ a Â + b B̂`
is recorded in `tables/c22_gate_witness.json`; the unconjugated power
product `Â^a B̂^b` is never freely equal to `e` for `n=2..7`, both signs.
For `(n,δ)=(2,−1)` one has `(a,b)=(0,−2)`, so two factors are necessary;
products of two prefix- or one-letter conjugates have shortest abelian
match of length 12 `> |e|=4`. Sampled extra search (same cap as C22.3):
no hit. Stored endpoints aca_16 and aca_43 are unimodular; the same
bounded prefix/one-letter two-factor enumeration does not hit `e`.

**C22.5 (C16 isolator is a C6 corridor, not a C16 output).** On each of
the 12 `Q'_{n,δ}`, `w=ξ` and `I=z² x^{nδ} y⁻¹` satisfy Theorem 3.1
(`code` `corridor_output`). The second output row is the C16 `B̂` (tag
`y`). The first row is not C16’s `Â`: C6 substitutes the letter `y` in
the companion, so the displayed `ξ = y⁻¹ x y` becomes `e⁻¹ x e` rather
than the letter `z`. Not a solve.

**C22.6 (C15 bridge).** Freely, `YXXXyxYx · (x⁻¹ y x) = YXXXyxx = P_{m,+1}`
row 1, and the inverse identity restores the C15 donor. The conjugator
`x⁻¹ y x` is a conjugate of `y`, not an AC donor. The ten C15 rows have
4160 raw depth-1 cyclic-AC2 children (rotations and donor inversion);
2440 of those are source-row-local `canon_pair` classes. None is
`canon_pair`-equal to `P_{m,±1}`. C13 could not have seen this: the
totals are the same length.

**Expansion.** C22.1–C22.2 are abelian/length identities, no C0. C22.5
is C6, hence two C0 uses. C22.6 is a free-group identity; the missing
conjugator is not AC.

**What this does not rule out.** Even `k` and odd `k≥5` are C24
(conjugator-independent parity; five-factor prefix/one-letter). Gate 1
conjugators longer than prefixes/one letter, or involving the new letter
`u` at depth ≥ 3; a different defining word than `ξ`; a C15 theorem that
produces `x⁻¹ y x` by a route other than depth-1 AC2 with the BS companion.
Three-factor prefix/one-letter products are C23.

**U124.** Applies to the C16 Q' family (eleven MS initial rows after C7/C1,
five stored C16 hits, ten C15 rows). Incoming C16 remains two
non-effective C0 uses. **Not a solve.**

**Audit.** `code/c22_gate_witness.py`, `tables/c22_gate_witness.json`.
`ingest/advisor_wave7.md` **REVISE** applied.

---

## C23. Three-factor Gate 1 ncl; F3 depth-2 after AC4 — IDENTITY-CHECKED NEGATIVE

**C23.1 (abelian shapes, uniform in `n≥2`).** A product of three conjugates
of `{R^{±1}, S^{±1}}` abelianizes to `ξ` iff it is one of:

- **A.** two conjugates of `R^δ` and one of `R^{-δ}` (any order);
- **B.** one conjugate of `R^δ` and a pair of opposite-sign conjugates of
  `S` (any order).

No other signed type pattern of length 3 has exponent vector `(1, 0)`:
y-exponent is the signed S-count, hence even, so there are 0 or 2 factors
of type `S`; three `R` factors need net `R^δ`; one `R` and two `S` need
that `R` to be `R^δ` and the `S` pair to cancel. Checked for `n=2..7`,
both signs: 9 legal signed-typed patterns, 3 of shape A and 6 of shape B,
0 others.

**C23.2 (complete three-factor enumeration).** Over the C22 prefix/one-letter
conjugator set (prefixes of both spellings `R^{±1}`, `S^{±1}`, and
one-letter conjugators), every shape-A/B product for `n=2..7` and
`δ ∈ {±1}` (`1,529,400` products) has free length at least 7 and is not
`ξ` or `ξ⁻¹`. Products that contain a mutually inverse factor pair freely
reduce to a conjugate of `R^δ` (length ≥ 7). Nondegenerate products in
this conjugator class never cancel below 7. `R^{-δ} ξ` is independent of
`n` and has length 10.

**C23.3 (AC4 third relator, F3 conjugators, depth ≤ 2).** After AC4 the
third relator is `u` (or `U` by AC1). Restore-preserving products of one
or two conjugates of `{R^{±1}, S^{±1}}` with conjugators reduced of
length ≤ 2 in `{x,y,u}` together with prefixes of both spellings
`R^{±1}` and `S^{±1}`, for all 12 `Q'_{n,δ}` (`1,076,088` products):
none is freely or cyclically equal to `D^{±1}` (`D = UYxy`). Products other than a return to `u`/`U`
have length at least 8 `> |D|=4`.

**Expansion.** Restore-preserving AC3+AC2 as in C22. No C0 in the
enumerated moves. No witness under this predicate was found.

**What this does not rule out.** C23.2: five or more *odd* factors
(even `k` is C24.1; five-factor prefix/one-letter is C24.2). C23.3:
three or more factors (depth ≥ 3). Conjugators outside the stated sets;
a defining word other than `ξ`. Gate 2 three-factor products are
abelian-impossible on every `Q'_{n,δ}` (C24.3).

**U124.** Same C16 Q' family as C22. Incoming C16 remains two
non-effective C0 uses. **Not a solve.**

**Audit.** `code/c23_three_factor.py`, `tables/c23_three_factor.json`.
`ingest/advisor_wave8.md` **REVISE** applied.

---

## C24. Abelian factor-parity; five-factor Gate 1; four-factor Gate 2 — IDENTITY-CHECKED NEGATIVE

**C24.1 (factor-parity, all `n≥2`).** Let `U,V` be cyclically reduced
relators and let `w` have a **unique** integer combination
`w ≡ U^α V^β` in abelianization (unimodularity of the exponent matrix
is a sufficient condition used here). Write `σ_U = n_{U+} − n_{U−}`.
Then `n_U = |α| + 2 t_U` and `n_V = |β| + 2 t_V` for integers
`t_U,t_V ≥ 0`, so `k = |α|+|β| + 2(t_U+t_V)`. No odd increment of `k`
is possible.

On Gate 1, `w=ξ=y^{-1}xy`, `U=R`, `V=S`. The identities
`R = x^{-1}y^{-1}xyy\, x^δ y^{-1}` (independent of `n`, cyclic length 7,
exponent `(δ,0)`), `S` of y-exponent `−1`, and `ξ` of exponent `(1,0)`
give the unique combination `(α,β)=(δ,0)` and `L1=1`. Even `k` is
impossible, uniformly in `n≥2` and both signs (closed forms of `q_prime`,
not a bound `n≤20`). The x-exponent of `S` does not enter: once the
signed S-count is 0, the S-contribution to x-exponent is 0. The number
of signed-type patterns with `σ_R=±1` and `σ_S=0` is
`N_k = ∑_{r odd, r≤k} C(k,r)\,C(r,(r+1)/2)\,C(k-r,(k-r)/2)`, hence
`N_1=1`, `N_3=9`, `N_5=100`, and `N_k=0` for even `k`. Enumeration for
`n=2..7` matches this formula. Hypotheses also replayed for `n=2..20`.

This re-proves C22.1’s two-factor negative and rules out `k=4,6,8,…`
without search. `k=1` remains the length obstruction `|R|=7 > |ξ|=3`.
`k=3` is C23. The next odd value is `k=5`.

**C24.2 (five-factor Gate 1, prefix/one-letter).** Meet-in-the-middle
`2+3` over the C22 conjugator pool (prefixes of both spellings
`R^{±1}`, `S^{±1}`, and one-letter conjugators), then **globally
deduplicated as factor-words**. The census is every ordered `k`-tuple
from that pool: `|F|^k` products, neither typed/conjugator tuples nor
the abelian-legal subset. For `n=2..7` and `δ∈{±1}` (`12` pairs,
`103,765,444,800` tuples) no product freely equals `ξ` or `ξ^{-1}`.
The six raw cyclic permutations of `ξ^{±1}` freely reduce to four
targets `{ξ, ξ^{-1}, x, x^{-1}}`; extras `x^{±1}` are recorded and are
**not** Gate 1 witnesses for `ξ`. No product freely equals those extras
either. This is not a claim about cyclic reduction of a longer word,
and it does not speak to `k≥7` or longer conjugators. Split `2+3` is
complete for 5-tuples in the pool: free reduction is a homomorphism, so
`f1⋯f5 = ξ` iff `(f1 f2)^{-1} ξ = f3 f4 f5`.

**C24.3 (Gate 2 L1 on `Q'` / `S_{n,δ}`).** In coordinates `(x,u)`,
`Â` has exponent `(δ−1, 1)`, `B̂` has `(1, −1)`, and
`e=u^2 x^{nδ}` has `(nδ, 2)`. The unique combination is

- `δ=+1`: `(a,b)=(n+2,\, n)`, `L1=2n+2 ≥ 6`;
- `δ=−1`: `(a,b)=(n−2,\, n−4)`, `L1=|n−2|+|n−4| ≥ 2`, always even.

Odd `k` is therefore abelian-impossible on every `Q'_{n,δ}`. In
particular C23’s leftover “Gate 2 three-factor” cannot hit `e` on this
family. Four-factor products are abelian-legal only for `δ=−1` and
`n∈{2,3,4,5}` (`L1∈{2,2,2,4}`). Prefix/one-letter MITM `2+2` on those
four pairs (`891,860,544` tuples) never freely equals `e^{±1}`.

**C24.4 (stored C16 endpoints).** Best-table C16 hits have
`(id, L1)` = `(aca_16, 5)`, `(aca_43, 2)`, `(aca_67, 15)`,
`(aca_87, 21)`, `(aca_90, 3)`. Prefix/one-letter searches of the next
legal `k≤5` after earlier work: `aca_16` five-factor (`L1=5`);
`aca_43` four-factor (**C22.4 already searched `k=2`** on this L1=2
endpoint; `k=4` is next); `aca_90` three-factor. No hit. `aca_67` and
`aca_87` have `L1>5` and were not enumerated.

**Expansion.** Restore-preserving AC3+AC2 as in C22. No C0 in the
enumerated products. C24.1 is an abelian identity and does not expand
Lemma 11. No witness under these predicates was found.

**What this does not rule out.** Gate 1: `k=7,9,…`; conjugators outside
the prefix/one-letter set, or involving the new letter `u`; defining
word `y` (C25.2 identity; not a 3-factor census). Gate 2 on `Q'`:
`k=L1+2m` for `m≥0` when `L1≥6`. Stored `aca_67` / `aca_87`. F3 depth
≥ 3 after AC4. Materializing Lemma 11. The generator `x` as a 3-factor
product is C25.1.

**U124.** Same C16 Q' family as C22/C23, plus the five stored C16
endpoints. Incoming C16 remains two non-effective C0 uses. **Not a
solve.**

**Audit.** `code/c24_even_k.py`, `tables/c24_even_k.json`. Same-code
deterministic replay (not a second implementation); planted MITM
hit/miss control in `mitm_controls`. `ingest/advisor_wave9.md`
**REVISE** applied.

---

## C25. Alternative defining words; C15 conjugator class — IDENTITY-CHECKED NEGATIVE

**C25.1 (generator `x` on `Q'`, all `n≥2`).** `x` has exponent
`(1,0)`, the same abelian class as `ξ`. C24.1 therefore applies
verbatim: even `k` is impossible; `k=1` is the length obstruction
`|R|=7 > 1`. The C23 abelian-legal 3-factor shapes A/B are exactly
the 3-factor patterns for exponent `(1,0)`. The census is nine
signed-type Cartesian products after per-type unique conjugates
(not `|F|^3`). Prefix/one-letter enumeration on all 12 `Q'_{n,δ}`
(`1,529,400` products) never freely equals `x`. Products in this
census abelianize to `(1,0)`, so they cannot equal `x^{-1}`; that
negative target is ruled out by reversing and inverting the three
factors, a bijection on the nine configs. Every enumerated product
has free length at least 7. Five-factor products against `x^{±1}`
were already C24.2’s extra targets (no hit).

**C25.2 (`y` on `Q'`, closed L1, all `n≥2`).** The unique combination
is `(a,b)=(n+2δ,\,-1)`, so `L1=|n+2δ|+1` (closed form from
`R_{\mathrm{ab}}=(δ,0)` and `S_{\mathrm{ab}}=(2+nδ,-1)`; `n=2..20`
is a sanity check). `k=1` is **abelian-legal only** for
`(n,δ)=(2,-1)`, where the combination is `(0,-1)` i.e. `S^{-1}`;
that case is still blocked by `|S|=7>1`. For every other `n≥2` and
both signs, `L1≥2`, so `k=1` is abelian-impossible. Parity follows
C24.1. No 3-factor census for `y` is claimed here.

**C25.3 (C15 conjugator class, `m≥3`).** On
`⟨ YXXXyxYx , B ⟩` with `B` a consecutive BS(`m`,`m+1`) of cyclic
length `2m+3`, both `y` and `x^{-1}yx` have exponent `(0,1)` and
unique combination `(0,-1)` against `(D,B)`: they are abelian-
equivalent to `B^{-1}`, `L1=1`, uniformly in `m` and both inner
signs. `k=1` is impossible (`2m+3 ≥ 9 > 3`). Even `k` is impossible.
The one-letter conjugacy class of `y^{±1}` is exactly
`{y, Y, Xyx, xyX, XYx, xYX}`; the three words of exponent `(0,1)`
are `{y, Xyx, xyX}`, and the other three are their inverses.
Prefix/one-letter 3-factor products of the nine abelian-legal
signed-type patterns, all ten C15 rows (`2,884,950` Cartesian
tuples): none equals a positive-class word. Negative-class words
follow by inversion as in C25.1. Every product has free length at
least 7. A hit would be a **normal-closure candidate** for that
word, not an AC-reachable primitive relator (C12, which also
needs C1) and not a legal C22.6 multiplication: C22.6 is only the
free identity `D · Xyx = P_{m,+1}` **row 1**, and `Xyx` is not an
AC donor. Exactly five of the ten C15 companions are literally
`P_{m,+1}` row 2 (`YYYYX y^m x`); the other five have the opposite
inner sign.

**Expansion.** Restore-preserving AC3+AC2 as in C22/C23. No C0 in the
enumerated products. C25.1–C25.2 are abelian identities plus the
stated censuses. No witness was found. Same-code replay, not a
second implementation.

**What this does not rule out.** C15: `k=5,7,…`; conjugators outside
the prefix/one-letter set. Q' defining word `y` at `k=L1` when
`L1≥2` is C26 for the `2≤L1≤7` window. Gate 1 `ξ` at `k≥7`.
Longer conjugators. Materializing Lemma 11. An explicit AC1–AC5
path from a future ncl hit.

**U124.** Ten C15 best-table rows (aca_18,20,40,42,63,65,91,93,102,104)
and the C16 Q' family. **Not a solve.**

**Audit.** `code/c25_alt_words.py`, `tables/c25_alt_words.json`. Same-code
deterministic replay. `ingest/advisor_wave10.md` **REVISE** applied.

---

## C26. Exact-L1 typed products for `y` on `Q'` — IDENTITY-CHECKED NEGATIVE

**C26.1 (combination, all `n≥2`).** Same identity as C25.2:
`(a,b)=(n+2δ,-1)`, `L1=|n+2δ|+1`. Exact-L1 products are `|a|`
conjugates of `R^{\mathrm{sign}(a)}` and one conjugate of `S^{-1}`,
in some order (`t_R=t_S=0`). For `n≥2` in this campaign's window,
`a≥0` except the excluded `L1=1` cell `(n,δ)=(2,-1)`.

**C26.2 (prefix/one-letter census, `n=2..7`, `2≤L1≤7`).** Unique
conjugates per signed type; counts are typed Cartesian sizes
`k\,|A|^{k-1}|B|`, not `|F|^k`. Distinguish three numbers:

- All eight cells, typed search-space total: `33,815,630,588`.
- Two Cartesian cells, actually enumerated products: `38,940`
  (observed free-length minima 11 and 13; every enumerated word has
  length at least 11).
- Six MITM cells, typed search-space only (not enumerated products):
  `33,815,591,648`. Existence MITM on unique freely reduced folds of
  the same typed slots.

Targets are the exponent-`(0,1)` one-letter class `{y, Xyx, xyX}`.
The inverse class follows by reversing and inverting factors. No cell
hits. Same-code planted controls cover Cartesian `k=2`, MITM arities
4–6, the recursive `L=3,R=3` split, a cancellation-heavy empty
5-fold, and Cartesian/MITM agreement on a tiny pool.
`independent_checker=false`.

Window: `(n,δ) = (3,-1),(4,-1),(5,-1),(6,-1),(7,-1),(2,+1),(3,+1),(4,+1)`.
Excluded: `(2,-1)` (`L1=1`, C25.2 length block); `δ=+1` and `n≥5`
(`L1≥8`).

**Expansion.** Restore-preserving AC3+AC2 as in C22. No C0 in the
enumerated products. A hit would be a **normal-closure candidate**,
not an AC-reachable primitive (C12, which also needs C1).

**What this does not rule out.** `k=L1+2t` for `t≥1` except the unique
`L1=2` cell at `k=4`, which is C27.2. `L1≥8`. Conjugators outside the
prefix/one-letter set, or involving `u`. Gate 1 `ξ` at `k≥7`. C15
`k≥5`. Materializing Lemma 11.

**U124.** C16 Q' family. **Not a solve.**

**Audit.** `code/c26_y_exact_l1.py`, `tables/c26_y_exact_l1.json`.
Same-code replay plus branch-complete planted Cartesian/MITM
controls. `independent_checker=false`. `ingest/advisor_wave11.md`
**REVISE** applied.

---

## C27. Archival depth-1 AC2; `k=L1+2` for `y` on `Q'_{3,-1}` — IDENTITY-CHECKED NEGATIVE

**C27.1 (archival initial table and parametric families).** C13
enumerated the depth-1 ordinary AC2 neighbourhood of the **best**
table (0 length drops, 0 new one-occurrence, 0 new two-block).
“Depth-1” here means **one AC2**, with cyclic orientations of both
factors realized as AC3 by a prefix (not a longer AC3–AC2 composite).
Thirty-six μ-floor rows have a different archival initial spelling.
The same neighbourhood on `aca_124_initial.csv` (124 rows, 36
changed) has 0 unique strict length drops, 0 new one-occurrence
children, and 0 new two-block children. The same holds for the
parametric families `P_{n,δ}`, `Q_{n,δ}` (`n=2..7`, both signs) and
Family A `P(n)`, `Q(n)` (`n=2..7`): 36 pairs, 0 drops. Unique
children of those parametric pairs are all strictly longer than the
input. Planted control: `⟨x, xy⟩` drops to `⟨x, y⟩` by AC2.

**C27.2 (`k=4` extra pair for `y` on `Q'_{3,-1}`).** Unique L1=2
cell: combination `(1,-1)`. Exact `k=L1+2` products are one extra
cancelling pair on top of one `R^+` and one `S^-`, i.e. the two
multinomial types `(R^+)^2 R^- S^-` and `R^+ S^+ (S^-)^2` (12
sequences each after per-type unique conjugates). Typed Cartesian
enumeration: `5,128,200` products, equal to the typed size, observed
minimum free length 11, none equal to `{y, Xyx, xyX}`. Inverse class
by reversing and inverting factors. A hit would be a **normal-closure
candidate**, not a C12 primitive.

**Expansion.** C27.1 is one ordinary AC2, with rotations as AC3 by a
prefix of the displayed factor. C27.2 is restore-preserving AC3+AC2
as in C22. No C0.

**What this does not rule out.** Depth ≥ 2 AC2 on archival or best
spellings (C28). `k=L1+2t` for `t≥2` or for cells with `L1≠2`. `L1≥8`.
Gate 1 `ξ` at `k≥7`. C15 `k≥5`. Longer conjugators. Materializing
Lemma 11.

**U124.** All 124 archival initial rows plus the C16 `Q'` family
(C27.2 is one cell). **Not a solve.**

**Audit.** `code/c27_archival_k4.py`, `tables/c27_archival_k4.json`.
Same-code replay plus planted AC2 and typed-4-tuple controls.
`independent_checker=false`. `ingest/advisor_wave12.md` **APPROVE**.

---

## C28. Depth ≤ 2 ordinary AC2 on archival initial and parametric families — IDENTITY-CHECKED NEGATIVE

**C28.1.** Depth ≤ 2 in the C13/C27.1 neighbourhood: each step is
**one AC2**, with cyclic orientations of both factors realized as AC3
by a prefix (not a longer AC3–AC2 composite). Unique depth-1 children
are scored against the input (a replay of C27.1 / C13), then each is
expanded once. Unique grandchildren are scored for strict cyclic-length
drop versus the input, new one-occurrence, and new two-block–both. On
the 36 μ-floor rows, a child or grandchild whose cyclic length is at
most the stored best length is compared by `canon_pair` to the
best-table spelling.

On `aca_124_initial.csv` (124 rows, 36 different from best): 36,312
row-local exact-spelling-unique depth-1 children, 19,066,394 row-local
exact-spelling-unique grandchildren, 30,630,336 raw second-step edges
from those deduplicated depth-1 parents (move-tuple multiplicity
retained). 0 unique length drops at depth 1 or 2, 0 new
one-occurrence, 0 new two-block–both, 0 `canon_pair` hits on the stored
best spelling. Parametric `P_{n,δ}`, `Q_{n,δ}` (`n=2..7`, both signs)
and Family A `P(n)`, `Q(n)` (`n=2..7`): 36 pairs, 7,166,262 row-local
exact-spelling-unique grandchildren, 0 drops, 0 new one-occurrence,
0 new two-block.
Planted control: `⟨x, xy⟩` drops at depth 1; `⟨x, y⟩` has no length
drop (lengthening two-block grandchildren of `⟨x, y⟩` are expected at
depth 2 and are not a miss failure).

**Expansion.** Depth counts AC2 multiplications. Each macro-edge uses
one AC2 plus any required AC1/AC3 orientation, restoration, and final
cyclic-reduction moves; this is not a two-elementary-move certificate.
No Aut, no C0.

**What this does not rule out.** Depth ≥ 3. Heap search. `k=L1+2t`
for `t≥2`. `L1≥8`. Gate 1 `ξ` at `k≥7`. C15 `k≥5`. Lemma 11.

**U124.** All 124 archival initial rows and parametric `P`/`Q`/Family A
(`n=2..7`). **Not a solve.** This is a bounded negative, not a
counterexample to stable triviality.

**Audit.** `code/c28_depth2_ac2.py`, `tables/c28_depth2_ac2.json`.
`children_fast` is junction cyclic reduction, checked equal to
`elementary_ac2_scan.children` including move triples on sampled pairs.
JSON is a single resumed deterministic census plus sampled
same-implementation checks, not a second implementation or a fresh
full replay of every row. `independent_checker=false`.
`ingest/advisor_wave13.md` **REVISE** applied. The census was resumed
in 50s slices under the 60s process guard.

---

## C29. `YXXyxYx` family: `y ≡ D^{-1}` then k=3 ncl — IDENTITY-CHECKED NEGATIVE

**C29.1 (abelian).** Compact donor `D = YXXyxYx` has exponent `(0,-1)`
and cyclic length 7. On every unimodular companion the unique
combination of `y` (and of `{Xyx, xyX}`) against `(D, C)` is
`(α,β)=(-1,0)`, so `L1=1`. Even `k` is abelian-impossible. `k=1` is
blocked by `|D|=7`. Five companions are the C7 Aut-minimal floors
`Y^n X y^2 x^2` (`n=3..7`): aca_120, 34, 58, 81, 97; that Aut-orbit is
not a solve.

**C29.2 (k=3 nine-config).** Same signed-type Cartesian products as
C23/C25.3, with `R^+ = D^{-1}` and `S = C`, prefix/one-letter
conjugators, per-type unique conjugates. Targets `{y, Xyx, xyX}`.
Inverse class by reversing and inverting factors. Typed Cartesian
enumeration: `1,650,843` products, equal to the typed size, observed
minimum free length 7 on every row, none equal to a target. Per-row
products: aca_0 181917; aca_3 152361; aca_34 126225; aca_36 126225;
aca_53 181917; aca_58 152361; aca_81 181917; aca_97 215109; aca_118
103293; aca_119 126225; aca_120 103293. Counts are nine-config typed
sizes after per-type unique conjugates, not `|F|^3`. Observed
minimum 7 is a census fact, not a length theorem. None of the eleven
companions is `bs_mm1_shape`.

**Expansion.** Restore-preserving AC3+AC2 as in C22. No C0. A hit would
be a **normal-closure candidate**, not a C12 primitive or an
AC-reachable generator. The free identity `D · x^{-1}yx = YXXyxx` is
not an AC2 (`Xyx` is not a donor; same caveat as C22.6).

**What this does not rule out.** `k=5,7,…`. Longer conjugators,
including conjugators involving `u`. Defining word `x` is C30 (exact
L1 closed). Depth ≥ 3 AC2. Lemma 11. An explicit
AC1–AC5 path from a future ncl hit.

**U124.** Eleven best-table rows aca_0,3,34,36,53,58,81,97,118,119,120.
**Not a solve.** Bounded negative for this typed k=3 pool.

**Audit.** `code/c29_yxx_family.py`, `tables/c29_yxx_family.json`.
Same-code deterministic replay plus planted nine-config control.
`independent_checker=false`. `ingest/advisor_wave15.md` **APPROVE**.

---

## C30. Exact-L1 typed products for `x` on the `YXXyxYx` family — IDENTITY-CHECKED NEGATIVE

**C30.1 (combination).** Donor `D = YXXyxYx` abelianizes to `(0,-1)`.
Any unimodular companion `C` abelianizes to `(p,q)` with `p=±1`, and
the unique solution of `a D_{\mathrm{ab}} + b C_{\mathrm{ab}} = (1,0)`
is `(a,b)=(pq,p)`; hence `|b|=1` for every such companion. On the
eleven listed rows, `L1=|a|+1 ∈ {2,…,7}` (not a claim about every
conceivable unimodular companion). Exact-L1 products are `|a|`
conjugates of `D^{\mathrm{sign}(a)}` and one conjugate of
`C^{\mathrm{sign}(b)}`, in some order (`t_D=t_C=0`). Even `k` is
abelian-legal on even-L1 rows among those eleven; there is no
C24-style even-k block. `k=1` never arises on those rows
(`min L1=2`).

**C30.2 (prefix/one-letter census, all eleven rows).** Unique conjugates
per signed type; counts are typed Cartesian sizes `k\,|A|^{k-1}|B|`,
not `|F|^k`. Distinguish three numbers:

- All eleven rows, typed search-space total: `43,999,487,350`.
- Three Cartesian cells (aca_34, aca_53, aca_120), actually enumerated
  products: `107,212` (observed free-length minima 15, 15, and 11;
  every enumerated word has length at least 11).
- Eight MITM cells, typed search-space only (not enumerated products):
  `43,999,380,138`. Existence MITM on unique freely reduced folds of
  the same typed slots (C26 `mitm_m_plus_one`).

Targets are the exponent-`(1,0)` one-letter class `{x, Yxy, yxY}`
(`Yxy` is C22’s `ξ`). The inverse class `{X, YXy, yXY}` follows by
reversing and inverting factors. No row hits.
`independent_checker=false`.

Cells: L1=2 aca_120 Cartesian; L1=3 aca_34 and aca_53 Cartesian;
L1=4 aca_3, 58, 118 MITM; L1=5 aca_0, 81, 119 MITM; L1=6 aca_97 MITM;
L1=7 aca_36 MITM.

**Expansion.** Restore-preserving AC3+AC2 as in C22. No C0. A hit would
be a **normal-closure candidate**, not a C12 primitive. Five companions
are C7 Aut-minimal P floors; that Aut-orbit is not a solve.

**What this does not rule out.** `k=L1+2t` for `t≥1`. Longer
conjugators, including conjugators involving `u`. Equality was tested
after free reduction only against `{x, Yxy, yxY}`. No cyclic-reduction
or conjugacy quotient, ambient `Aut(F_2)`, or Tietze identification
was used; freely reduced longer conjugates of `x` not among these
three targets remain untested. C29 leftover `k=5,7,…` for defining
word `y`. The eight-row donor `YXXYxxyx` is C31. Depth ≥ 3 AC2.
Lemma 11.

**U124.** Eleven best-table rows aca_0,3,34,36,53,58,81,97,118,119,120.
**Not a solve.** Bounded negative for this exact-L1 typed pool.

**Audit.** `code/c30_x_exact_l1.py`, `tables/c30_x_exact_l1.json`.
Same-code replay plus C26 planted controls. Cartesian observed minima
11 and 15 are census facts, not a length theorem. MITM typed sizes are
search-space, not enumerated products. `independent_checker=false`.
`ingest/advisor_wave14.md` **REVISE** applied.

---

## C31. `YXXYxxyx` family: `y ≡ C^{-1}` then k=3 ncl — IDENTITY-CHECKED NEGATIVE

**C31.1 (abelian).** Compact donor `D = YXXYxxyx` has exponent `(1,-1)`
and cyclic length 8. Seven of the eight best-table companions are
consecutive `BS(m,m+1)` (`m=3..6`) with exponent `(0,-1)`: aca_22, 23,
46, 49, 68, 70, 89. On those rows the unique combination of `y` (and
of `{Xyx, xyX}`) against `(D, C)` is `(0,-1)`, so `L1=1` and
`y ≡ C^{-1}`. Even `k` is abelian-impossible. `k=1` is blocked by
`|C|≥9`. This is a parallel stall family to C15, not the same donor.

The remaining row aca_32 has companion `YYYYXyxyx`, not BS;
combination `(1,-1)`, `L1=2`.

**C31.2 (k=3 nine-config, seven BS rows).** Same signed-type Cartesian
products as C23/C25.3, with `R^+ = C^{-1}` and `S = D`, prefix/one-letter
conjugators, per-type unique conjugates. Targets `{y, Xyx, xyX}`.
Inverse class by reversing and inverting factors. Typed Cartesian
enumeration: `1,519,059` products, equal to the typed size, observed
minimum free length 9, none equal to a target. Per-row products:
aca_22 148275; aca_23 131472; aca_46 183924; aca_49 204849; aca_68
248808; aca_70 274311; aca_89 327420. Counts are nine-config typed
sizes, not `|F|^3`. Observed minimum 9 is a census fact for this pool,
not a length theorem and not a comparative control against C29's
minimum 7.

**C31.3 (exact L1=2, aca_32).** One conjugate of `D` and one of
`C^{-1}`: `1,104` Cartesian products, observed minimum 9, no hit.

**Expansion.** Restore-preserving AC3+AC2 as in C22. No C0. A hit would
be a **normal-closure candidate**, not a C12 primitive.

**What this does not rule out.** `k=5,7,…` on the seven BS rows.
Longer conjugators, including `u`. Defining word `x` is C32 (exact
L1 closed on these eight rows). Depth ≥ 3 AC2. Lemma 11.

**U124.** Eight best-table rows aca_22, 23, 32, 46, 49, 68, 70, 89.
**Not a solve.** Bounded negative for this typed pool.

**Audit.** `code/c31_yxxy_family.py`, `tables/c31_yxxy_family.json`.
Same-code deterministic replay plus planted nine-config control.
`independent_checker=false`. Tests spot-check identities and stored
JSON; they do not independently replay the census.
`ingest/advisor_wave16.md` **APPROVE**.

---

## C32. Exact-L1 typed products for `x` on the `YXXYxxyx` family — IDENTITY-CHECKED NEGATIVE

**C32.1 (combination).** Donor `D = YXXYxxyx` abelianizes to `(1,-1)`.
Any unimodular companion `C` abelianizes to `(p,q)` with `|p+q|=1`, and
the unique solution of `a D_{\mathrm{ab}} + b C_{\mathrm{ab}} = (1,0)`
is `b=p+q`, `a=(p+q)q`; hence `|b|=1`. On the eight listed rows,
`L1=2` on the seven consecutive BS companions and `L1=3` on aca_32
(not a claim about every conceivable unimodular companion). Exact-L1
products are `|a|` conjugates of `D^{\mathrm{sign}(a)}` and one
conjugate of `C^{\mathrm{sign}(b)}` (`t_D=t_C=0`).

**C32.2 (prefix/one-letter census, all eight rows).** Unique conjugates
per signed type; counts are typed Cartesian sizes `k\,|A|^{k-1}|B|`,
not `|F|^k`. All eight cells are within the Cartesian cap: `51,412`
products, equal to the typed size, observed free-length minima 13, 11,
13, 13, 15, 15, 17, 17 (every enumerated word has length at least 11).
No MITM cells. Targets `{x, Yxy, yxY}`; inverse class by reversing and
inverting factors. No hit. Equality is free-reduce literal match.
`independent_checker=false`.

**Expansion.** Restore-preserving AC3+AC2 as in C22. No C0. A hit would
be a **normal-closure candidate**, not a C12 primitive.

**What this does not rule out.** `k=L1+2t` for `t≥1`. Longer
conjugators, including `u`. Equality was tested after free reduction
only against `{x, Yxy, yxY}`. No cyclic-reduction or conjugacy
quotient, ambient `Aut(F_2)`, or Tietze identification was used;
freely reduced longer conjugates of `x` not among these three targets
remain untested. C31 leftover `k=5,7,…` for `y`. Remaining length-7
donors with `D_ab=(0,-1)` are C33. Depth ≥ 3 AC2. Lemma 11.

**U124.** Eight best-table rows aca_22, 23, 32, 46, 49, 68, 70, 89.
**Not a solve.** Bounded negative for this exact-L1 typed pool.

**Audit.** `code/c32_x_exact_l1.py`, `tables/c32_x_exact_l1.json`.
Same-code replay plus C26 planted controls. Observed minimum 11 is a
census fact, not a length theorem. Tests independently check the
algebra and rerun only aca_23/aca_32; they do not independently replay
all eight cells. `independent_checker=false`.
`ingest/advisor_wave17.md` **REVISE** applied.

---

## C33. Remaining length-7 donors with `D_ab=(0,-1)`: `y ≡ D^{-1}` then k=3 ncl — IDENTITY-CHECKED NEGATIVE

**C33.1 (abelian).** Same identity as C29.1: any compact donor with
exponent `(0,-1)` and a unimodular companion has unique `y`-combination
`(-1,0)`, so `L1=1`. Even `k` is abelian-impossible. `k=1` is blocked
by cyclic length 7. This census covers the two unused such donors on
the best table. The donor/row pool is disjoint from C29's `YXXyxYx`;
C33 imports C29/C25 machinery and is not independent code:

- `YXyXYxx`: aca_8, 85, 98, 121, 122, 123
- `YYXXyxx`: aca_1, 7, 31, 43, 72, 99

**C33.2 (k=3 nine-config).** Same signed-type Cartesian products as
C23/C25.3/C29.2, with `R^+ = D^{-1}` and `S = C`, prefix/one-letter
conjugators, per-type unique conjugates. Targets `{y, Xyx, xyX}`.
Inverse class by reversing and inverting factors. Typed Cartesian
enumeration: `1,737,522` products, equal to the typed size, observed
minimum free length 7 on every row, none equal to a target. Counts are
nine-config typed sizes, not `|F|^3`. Observed minimum 7 is a census
fact for this pool, not a length theorem and not a comparative control
against C29.

**Expansion.** Restore-preserving AC3+AC2 as in C22. No C0. A hit would
be a **normal-closure candidate**, not a C12 primitive.

**What this does not rule out.** `k=5,7,…`. Longer conjugators,
including `u`. Defining word `x` is C34 in the `2≤L1≤7` window;
aca_43 (`L1=1`) and L1≥8 remain. Depth ≥ 3 AC2. Lemma 11.

**U124.** Twelve best-table rows listed above. **Not a solve.** Bounded
negative for this typed k=3 pool.

**Audit.** `code/c33_len7_donors.py`, `tables/c33_len7_donors.json`.
Same-code deterministic replay plus planted nine-config control.
`independent_checker=false`. Tests spot-check identities and stored
JSON; they do not independently enumerate the census.
`ingest/advisor_wave18.md` **APPROVE**.

---

## C34. Exact-L1 typed products for `x` on the C33 rows — IDENTITY-CHECKED NEGATIVE

**C34.1 (combination).** Both C33 donors abelianize to `(0,-1)`, so
C30's formula applies: unimodular `C_ab=(p,q)` has `p=±1` and unique
x-combination `(a,b)=(pq,p)`; hence `|b|=1` for every such companion.
On the twelve listed rows `L1` runs from 1 to 10. The census window
`2≤L1≤7` is the eight listed rows below, not every conceivable
unimodular companion. Exact-L1 products are `|a|` conjugates of
`D^{\mathrm{sign}(a)}` and one of `C^{\mathrm{sign}(b)}`. Even `k` is
abelian-legal on even-L1 window rows; there is no C24-style even-k
block in the window.

**C34.2 (prefix/one-letter census, `2≤L1≤7`).** Unique conjugates per
signed type; counts are typed Cartesian sizes `k\,|A|^{k-1}|B|`, not
`|F|^k`. Distinguish three numbers:

- Four Cartesian cells (aca_8, 1, 72, 99): `59,884` enumerated typed
  tuples, observed minima 9, 11, 17, 15 (every enumerated word has
  length at least 9).
- Four MITM cells (aca_121, 122, 7, 31): typed search-space
  `69,587,713,197`, not enumerated products.
- All-window typed total `69,587,773,081`.

Targets `{x, Yxy, yxY}` (`Yxy` is C22’s `ξ`). Inverse class by
reversing and inverting factors. No hit. Equality is free-reduce
literal match. No cyclic-reduction or conjugacy quotient, ambient
`Aut(F_2)`, or Tietze identification. `independent_checker=false`.

Skipped: aca_43 (`L1=1`; combo `(0,-1)`, so `x ≡ C^{-1}`; k=1 blocked
by `|C|=11`; even k impossible); aca_123, 85, 98 (`L1≥8`).

**Expansion.** Restore-preserving AC3+AC2 as in C22. No C0. A hit would
be a **normal-closure candidate**, not a C12 primitive.

**What this does not rule out.** `k=L1+2t` for `t≥1`. Longer
conjugators, including `u`. Equality was tested after free reduction
only against `{x, Yxy, yxY}`; freely reduced longer conjugates of `x`
not among these three targets remain untested. aca_43 k=3 for `x`.
`L1≥8`. C33 leftover `k=5,7,…` for `y`. The remaining listed
length-7 donor `YXXXyxx` is C35. Depth ≥ 3 AC2. Lemma 11.

**U124.** Eight of the twelve C33 rows. **Not a solve.** Bounded
negative for this typed exact-L1 pool.

**Audit.** `code/c34_x_exact_l1.py`, `tables/c34_x_exact_l1.json`.
Same-code replay plus C26 planted controls. Observed Cartesian minimum
9 is a census fact. MITM typed sizes are search-space, not enumerated
products. Tests independently check the algebra and rerun only
aca_8/aca_72; they do not independently replay MITM.
`independent_checker=false`. `ingest/advisor_wave19.md` **APPROVE**.

---

## C35. Last listed length-7 donor `YXXXyxx`: `x ≡ D^{-1}` then k=3 ncl — IDENTITY-CHECKED NEGATIVE

**C35.1 (abelian).** Donor `D = YXXXyxx` abelianizes to `(-1,0)`. Write
`C_{\mathrm{ab}}=(p,q)`. The pair exponent matrix has
`\det(D,C)=-q`. If that matrix is unimodular, then `q=\pm1`, and
solving `a D_{\mathrm{ab}} + b C_{\mathrm{ab}}=(1,0)` gives uniquely
`(a,b)=(-1,0)`. The same combination holds for `{x, Yxy, yxY}`. Thus
`L1=1`. Even `k` is abelian-impossible. `k=1` is blocked by cyclic
length 7. This is the last unused length-7 donor **in the listed
shared-donor inventory**. The same spelling already appears in C22.6
as the free identity `YXXXyxYx · (x^{-1} y x) = YXXXyxx = P_{m,+1}`
row 1; that identity is not an AC2 and is not this census. Six
best-table rows, all with `q=-1` so `\det=+1`:

- aca_9, 10, 11, 12, 116, 117

**C35.2 (k=3 nine-config).** Same signed-type Cartesian products as
C23/C25.3/C29.2, with `R^+ = D^{-1}` and `S = C`, prefix/one-letter
conjugators, per-type unique conjugates. Targets `{x, Yxy, yxY}`.
Inverse class by reversing and inverting factors. Typed Cartesian
enumeration: `579,870` products, equal to the typed size on every
row, observed minimum free length 7 on every row, none equal to a
target. Counts are nine-config typed sizes, not `|F|^3`. Observed
minimum 7 is a C35 census fact for this pool, not a length theorem
and not a comparative control against C29/C33/C34. A hit would persist
ordered signed types, three factor words, conjugators, and a
free-reduce replay; no hit occurred.

Per-row products: aca_9, 10, 11, 12 each 103293; aca_116, 117 each
83349.

**Expansion.** Restore-preserving AC3+AC2 as in C22. No C0. A hit would
be a **normal-closure candidate**, not a C12 primitive.

**What this does not rule out.** `k=5,7,…`. Longer conjugators,
including `u`. Defining word `y` on these rows (L1 is 4, 4, 2, 2, 3, 1
respectively; aca_117 has `y ≡ C^{-1}`). aca_43 k=3 for `x`. C34
`L1≥8`. Unused listed donors `YYXXXyxx`, `YXXyXYxxx`, `YXXXyxYxx`.
The listed donor `YXXYxxyX` is C36. Depth ≥ 3 AC2. Lemma 11.

**U124.** Six best-table rows listed above. **Not a solve.** Bounded
negative for this typed k=3 pool.

**Audit.** `code/c35_yxxx_family.py`, `tables/c35_yxxx_family.json`.
Same-code deterministic replay plus planted nine-config control with a
persisted factor/conjugator witness. `independent_checker=false`.
Tests independently check the algebra, the planted witness schema, and
rerun only aca_117; they do not independently enumerate the census.
Plan advisor REVISE applied (`ingest/advisor_c35_plan.md`).
`ingest/advisor_wave20.md` **APPROVE**.

---

## C36. Listed `YXXYxxyX` BS companions: `y ≡ C^{-1}` then k=3 ncl — IDENTITY-CHECKED NEGATIVE

**C36.1 (abelian, listed rows).** Donor `D = YXXYxxyX` abelianizes to
`(-1,-1)`. The seven best-table companions are consecutive
`BS(m,m+1)` (`m=3..6`) with `C_{\mathrm{ab}}=(0,-1)`:

- aca_21, 25, 47, 50, 69, 73, 96

On those listed companions, solving
`a D_{\mathrm{ab}} + b C_{\mathrm{ab}}=(0,1)` gives uniquely
`(a,b)=(0,-1)`, so `L1=1` and `y ≡ C^{-1}`. The same combination holds
for `{y, Xyx, xyX}`. This is **not** a claim about every unimodular
companion of `D`. Even `k` is abelian-impossible. `k=1` is blocked by
cyclic length `|C|≥9`. No exceptional row. Defining word `x` has
uniform combo `(-1,1)` and `L1=2` on these seven rows (leftover).

**C36.2 (k=3 nine-config).** C31 orientation: `R^+ = C^{-1}`,
`S = D`. Prefix/one-letter conjugators, per-type unique conjugates.
Targets `{y, Xyx, xyX}`. Inverse class by reversing and inverting
factors. Typed Cartesian enumeration: `1,549,596` products, equal to
the typed size on every row, none equal to a target. Observed free
lengths by row: 9, 9, 11, 11, 13, 13, 15; census minimum 9. Counts are
nine-config typed sizes, not `|F|^3`. Observed minima are C36 census
facts, not a length theorem and not a comparative control against C31.
A hit would persist ordered signed types, three factor words,
conjugators, and a free-reduce replay **outside** the scanner loop; no
hit occurred.

Per-row products: aca_21 131472; aca_25 148275; aca_47 183924;
aca_50 204849; aca_69 248808; aca_73 274311; aca_96 357957.

Disjointness is of donor/row **presentation pairs**, not of the
companion-word set (those overlap C31/C15). C28 previously touched
these rows under a different depth-2 AC2 predicate.

**Expansion.** Restore-preserving AC3+AC2 as in C22. No C0. A hit would
be a **normal-closure candidate**, not a C12 primitive.

**What this does not rule out.** `k=5,7,…`. Longer conjugators,
including `u`. Exact-L1 for `x` (`L1=2`) on these rows is C37. Other unused
listed donors `YYXXXyxx`, `YXXyXYxxx`. The listed donor `YXXXyxYxx` is
C38. aca_43 k=3 for `x`. C35 leftover `y`. Depth ≥ 3 AC2. Lemma 11.

**U124.** Seven best-table rows listed above. **Not a solve.** Bounded
negative for this typed k=3 pool.

**Audit.** `code/c36_yxxyx_family.py`, `tables/c36_yxxyx_family.json`.
Same-code deterministic replay plus planted nine-config control with a
persisted factor/conjugator witness replayed outside the scanner.
`independent_checker=false`. Tests independently check the algebra,
orientation, planted outside-replay, and rerun only aca_21; they do
not independently enumerate the census. Plan advisor REVISE applied
(`ingest/advisor_c36_plan.md`). `ingest/advisor_wave21.md` **APPROVE**.

---

## C37. Exact-L1 typed products for `x` on the C36 rows — IDENTITY-CHECKED NEGATIVE

**C37.1 (combination, listed rows).** On the seven listed `YXXYxxyX`
companions with `C_{\mathrm{ab}}=(0,-1)`, solving
`a D_{\mathrm{ab}} + b C_{\mathrm{ab}}=(1,0)` gives uniquely
`(a,b)=(-1,1)`, so `L1=2`. Exact-L1 products are one conjugate of
`D^{-1}` and one conjugate of `C`, in either order. This is **not** a
claim about every unimodular companion of `D`.

**C37.2 (prefix/one-letter census, all seven rows).** Unique conjugates
per signed type; counts are typed Cartesian sizes `2\,|A|\,|B|`, not
`|F|^k`. All seven cells are Cartesian: `11,804` enumerated typed
tuples, equal to the typed size, observed free-length minima 11, 13,
13, 15, 15, 17, 19 (census minimum 11). No MITM. Targets `{x, Yxy, yxY}`;
inverse class by reversing and inverting factors. No hit. Equality is
free-reduce literal match. `independent_checker=false`.

Per-row products: aca_21 1200; aca_25 1300; aca_47 1508; aca_50 1620;
aca_69 1848; aca_73 1972; aca_96 2356.

A hit would persist ordered signed types, two factor words, conjugators,
and a free-reduce replay **outside** the scanner loop; no hit occurred.
Observed minima are C37 census facts, not a length theorem and not a
comparative control against C32.

**Expansion.** Restore-preserving AC3+AC2 as in C22. No C0. A hit would
be a **normal-closure candidate**, not a C12 primitive.

**What this does not rule out.** `k=L1+2t` for `t≥1`. Longer
conjugators, including `u`. Equality was tested after free reduction
only against `{x, Yxy, yxY}`; freely reduced longer conjugates of `x`
not among these three targets remain untested. C36 leftover `k=5,7,…`
for `y`. Unused listed donors `YYXXXyxx`, `YXXyXYxxx`. The listed donor
`YXXXyxYxx` is C38. aca_43 k=3 for `x`. Depth ≥ 3 AC2. Lemma 11.

**U124.** Seven best-table rows listed in C36. **Not a solve.** Bounded
negative for this typed exact-L1 pool.

**Audit.** `code/c37_x_exact_l1.py`, `tables/c37_x_exact_l1.json`.
Same-code replay plus planted two-factor control with outside-scanner
replay. Observed Cartesian minimum 11 is a census fact. Tests
independently check the algebra and rerun only aca_21; they do not
independently replay all seven cells. `independent_checker=false`.
Plan advisor REVISE applied (`ingest/advisor_c37_plan.md`).
`ingest/advisor_wave22.md` **APPROVE**.

---

## C38. Listed `YXXXyxYxx` rows: `y ≡ D^{-1}` then k=3 ncl — IDENTITY-CHECKED NEGATIVE

**C38.1 (abelian, listed rows).** Donor `D = YXXXyxYxx` abelianizes to
`(0,-1)` and has cyclic length 9. The seven best-table companions all
have `|p|=1`, so `\det(D,C)=p=\pm 1`. Solving
`a D_{\mathrm{ab}} + b C_{\mathrm{ab}}=(0,1)` gives uniquely
`(a,b)=(-1,0)`, so `L1=1` and `y \equiv D^{-1}`. The same combination
holds for `{y, Xyx, xyX}`. This is **not** a claim about every
companion of `D`, nor about `p=0`. Even `k` is abelian-impossible.
`k=1` is blocked by cyclic length 9. Seven rows:

- aca_48, 60, 75, 76, 84, 110, 113

**C38.2 (k=3 nine-config).** Same signed-type Cartesian products as
C23/C25.3/C29.2, with `R^+ = D^{-1}` and `S = C` (C35 orientation,
asserted; not C31). Prefix/one-letter conjugators, per-type unique
conjugates. Targets `{y, Xyx, xyX}`. Inverse class by reversing and
inverting factors. Typed Cartesian enumeration: `1,798,887` products,
equal to the typed size on every row, observed free-length minimum 9
on every row, none equal to a target. Counts are nine-config typed
sizes, not `|F|^3`. Observed minimum 9 is a C38 census fact, not a
length theorem and not a comparative control against C29/C33.

Per-row products: aca_48 188328; aca_60 222120; aca_75 235197;
aca_76 259776; aca_84 274329; aca_110 301512; aca_113 317625.

A hit would persist ordered signed types, three factor words,
conjugators, and a free-reduce replay **outside** the scanner loop; no
hit occurred.

Disjointness is of donor/row **presentation pairs**, not of the
companion-word set (`YYYYYYXXXYxx` also appears with aca_77, and
`YYYYYYYXXXYxx` with aca_107, in unused `YXXyXYxxx`). C28 previously
touched these rows under a different depth-2 AC2 predicate. This is
**not** the last unused listed donor.

**Expansion.** Restore-preserving AC3+AC2 as in C22. No C0. A hit would
be a **normal-closure candidate**, not a C12 primitive.

**What this does not rule out.** `k=5,7,…`. Longer conjugators,
including `u`. Exact-L1 for `x` on these rows (C30 leftover combo
`(a,b)=(pq,p)`; L1 is 4, 5, 8, 6, 9, 7, 10 respectively). Unused
listed donors `YYXXXyxx`. The listed donor `YXXyXYxxx` is C39. aca_43
k=3 for `x`. C35 leftover `y`. C36 leftover `k=5,7,…` for `y`. Depth ≥ 3
AC2. Lemma 11.

**U124.** Seven best-table rows listed above. **Not a solve.** Bounded
negative for this typed k=3 pool.

**Audit.** `code/c38_yxxxyx_family.py`, `tables/c38_yxxxyx_family.json`.
Same-code deterministic replay plus planted nine-config control with a
persisted factor/conjugator witness replayed outside the scanner.
`independent_checker=false`. Tests independently check the algebra,
orientation, planted outside-replay, and rerun only aca_48; they do
not independently enumerate the census. Plan advisor APPROVE
(`ingest/advisor_c38_plan.md`). `ingest/advisor_wave23.md` **APPROVE**.

---

## C39. Listed `YXXyXYxxx` rows: `y ≡ D^{-1}` then k=3 ncl — IDENTITY-CHECKED NEGATIVE

**C39.1 (abelian, listed rows).** Donor `D = YXXyXYxxx` abelianizes to
`(0,-1)` and has cyclic length 9. The six best-table companions all
have `|p|=1`, so `\det(D,C)=p=\pm 1`. Solving
`a D_{\mathrm{ab}} + b C_{\mathrm{ab}}=(0,1)` gives uniquely
`(a,b)=(-1,0)`, so `L1=1` and `y \equiv D^{-1}`. The same combination
holds for `{y, Xyx, xyX}`. This is **not** a claim about every
companion of `D`, nor about `p=0`. Even `k` is abelian-impossible.
`k=1` is blocked by cyclic length 9. Six rows:

- aca_45, 61, 77, 83, 107, 114

**C39.2 (k=3 nine-config).** Same signed-type Cartesian products as
C23/C25.3/C29.2/C38.2, with `R^+ = D^{-1}` and `S = C` (C35 orientation,
asserted; not C31). Prefix/one-letter conjugators, per-type unique
conjugates. Targets `{y, Xyx, xyX}`. Inverse class by reversing and
inverting factors. Typed Cartesian enumeration: `1,563,690` products,
equal to the typed size on every row, observed free-length minimum 9
on every row, none equal to a target. Counts are nine-config typed
sizes, not `|F|^3`. Observed minimum 9 is a C39 census fact, not a
length theorem and not a comparative control against C38/C29/C33.
Equal typed sizes to some C38 rows do not identify those censuses.

Per-row products: aca_45 188328; aca_61 222120; aca_77 259776;
aca_83 274329; aca_107 301512; aca_114 317625.

A hit would persist ordered signed types, three factor words,
conjugators, and a free-reduce replay **outside** the scanner loop; no
hit occurred.

Disjointness is of donor/row **presentation pairs**, not of the
companion-word set (`YYYYYYXXXYxx` also appears with aca_75, and
`YYYYYYYXXXYxx` with aca_84, in C38). C28 previously touched these
rows under a different depth-2 AC2 predicate. This is **not** the last
unused listed donor.

**Expansion.** Restore-preserving AC3+AC2 as in C22. No C0. A hit would
be a **normal-closure candidate**, not a C12 primitive.

**What this does not rule out.** `k=5,7,…`. Longer conjugators,
including `u`. Exact-L1 for `x` on these rows (C30 leftover combo
`(a,b)=(pq,p)`; L1 is 6, 7, 8, 7, 9, 8 respectively). Unused listed
donor `YYXXXyxx` (mixed `C_ab`; C40 covers only the two `C_ab=(1,0)`
rows). aca_43 k=3 for `x`. C35 leftover `y`. C36 leftover `k=5,7,…`
for `y`. C38 leftover `x` and `k≥5`. Depth ≥ 3 AC2. Lemma 11.

**U124.** Six best-table rows listed above. **Not a solve.** Bounded
negative for this typed k=3 pool.

**Audit.** `code/c39_yxxyxyxxx_family.py`, `tables/c39_yxxyxyxxx_family.json`.
Same-code deterministic replay plus planted nine-config control with a
persisted factor/conjugator witness replayed outside the scanner.
`independent_checker=false`. Tests independently check the algebra,
orientation, planted outside-replay, and rerun only aca_45; they do
not independently enumerate the census. Plan advisor APPROVE
(`ingest/advisor_c39_plan.md`). `ingest/advisor_wave24.md` **APPROVE**.

---

## C40. Two `YYXXXyxx` rows with `x ≡ C` in abelianization, then k=3 ncl — IDENTITY-CHECKED NEGATIVE

**C40.1 (abelian, listed rows).** Donor `D = YYXXXyxx` abelianizes to
`(-1,-1)`. The six-row family is mixed; C40 is **only** the two
companions with `C_{\mathrm{ab}}=(1,0)`:

- aca_16 companion `YXyxxyXYx`, cyclic length 9
- aca_95 companion `YYxyxyXYxyX`, cyclic length 11

Solving `a D_{\mathrm{ab}} + b C_{\mathrm{ab}}=(1,0)` gives uniquely
`(a,b)=(0,1)`, so `L1=1` and `x \equiv C` **in abelianization** (not
free equality). The same combination holds for `{x, Yxy, yxY}`. This
is **not** a claim about every companion of `D`. Even `k` is
abelian-impossible. `k=1` is blocked by `|C|\ge 9`. aca_16 instantiates
C16 and escapes C16.1; that is a disclosure, not a C16 re-proof.

**C40.2 (k=3 nine-config).** Same signed-type Cartesian products as
C23/C25.3, with `R^+ = C` and `S = D` (C40 orientation, asserted; not
C35, not C31). Prefix/one-letter conjugators, per-type unique
conjugates. Targets `{x, Yxy, yxY}`. Inverse class by reversing and
inverting factors. Typed Cartesian enumeration: `332,199` products,
equal to the typed size on every row, observed free-length minima 9
and 11, none equal to a target. Counts are nine-config typed sizes,
not `|F|^3`. Observed minima are C40 census facts, not a length
theorem and not a comparative control against C35/C36/C38.

Per-row products: aca_16 148275; aca_95 183924.

A hit would persist ordered signed types, three factor words,
conjugators, and a free-reduce replay **outside** the scanner loop; no
hit occurred.

Disjointness is relative to prior typed donor-family censuses. C28
previously touched these rows under a different depth-2 AC2
predicate. This is **not** a six-row `YYXXXyxx` census.

**Expansion.** Restore-preserving AC3+AC2 as in C22. No C0. A hit would
be a **normal-closure candidate**, not a C12 primitive.

**What this does not rule out.** `k=5,7,…`. Longer conjugators,
including `u`. Exact-L1 for `y` on these rows (`L1=2`). Remaining
`YYXXXyxx` rows: aca_71 is C41; leftover `y` on aca_71 (`L1=2`); aca_38
(`y \equiv C^{-1}`, C31 orientation); aca_56 and aca_57 (`L1\ge 3`).
aca_43 k=3 for `x`. C35 leftover `y`. C36 leftover `k=5,7,…` for `y`.
C38/C39 leftover `x`. Depth ≥ 3 AC2. Lemma 11.

**U124.** Two best-table rows listed above. **Not a solve.** Bounded
negative for this typed k=3 pool.

**Audit.** `code/c40_yyxxxyxx_x_eq_c.py`, `tables/c40_yyxxxyxx_x_eq_c.json`.
Same-code deterministic replay plus planted nine-config control with a
persisted factor/conjugator witness replayed outside the scanner.
`independent_checker=false`. Tests independently check the algebra of
both rows and rerun only aca_16; they do not independently enumerate
aca_95. Plan advisor REVISE applied (`ingest/advisor_c40_plan.md`).
`ingest/advisor_wave25.md` **APPROVE**.

---

## C41. One `YYXXXyxx` row with `x ≡ C^{-1}` in abelianization, then k=3 ncl — IDENTITY-CHECKED NEGATIVE

**C41.1 (abelian, listed row).** Donor `D = YYXXXyxx` abelianizes to
`(-1,-1)`. C41 is **only** aca_71, companion `YYXyxyXYxyX`,
`C_{\mathrm{ab}}=(-1,0)`, pair det `-1`, cyclic length 11. Solving
`a D_{\mathrm{ab}} + b C_{\mathrm{ab}}=(1,0)` gives uniquely
`(a,b)=(0,-1)`, so `L1=1` and `x \equiv C^{-1}` **in abelianization**
(not free equality). The same combination holds for `{x, Yxy, yxY}`.
This is **not** a claim about every companion of `D`, **not** a six-row
`YYXXXyxx` census, and **not** lumped with aca_38. Even `k` is
abelian-impossible. `k=1` is blocked by `|C|=11`. Leftover `y` has
combo `(-1,1)`, `L1=2`, and is not part of C41. aca_71 has a recorded
`mu_floor_r8` chain pending orbit replay; that is a disclosure, not a
C8 re-proof.

**C41.2 (k=3 nine-config).** Same signed-type Cartesian products as
C23/C25.3, with `R^+ = C^{-1}` and `S = D` (C31 orientation, asserted;
not C35, not C40). Prefix/one-letter conjugators, per-type unique
conjugates. Targets `{x, Yxy, yxY}`. Inverse class by reversing and
inverting factors. Typed Cartesian enumeration: `164,475` products,
equal to the typed size, unique-conjugate counts `(25,25,28,28)`,
observed free-length minimum 11, none equal to a target. Completeness
is all `164,475` typed tuples in this bounded pool, not `|F|^3`.
Observed minimum 11 is a C41 census fact, not a length theorem and not
a comparative control against C31/C36/C40. Equal typed size `164,475`
does not identify other censuses.

A hit would persist ordered signed types, three factor words,
conjugators, and a free-reduce replay **outside** the scanner loop; no
hit occurred.

Disjointness is relative to prior typed donor-family censuses. C28
previously touched this row under a different depth-2 AC2 predicate.
C40 used the same donor on different companions with a different
orientation.

**Expansion.** Restore-preserving AC3+AC2 as in C22. No C0. A hit would
be a **normal-closure candidate**, not a C12 primitive.

**What this does not rule out.** `k=5,7,…`. Longer conjugators,
including `u`. Exact-L1 for `y` on this row (`L1=2`). Remaining
`YYXXXyxx` rows: aca_38 (`y \equiv C^{-1}` in abelianization, C31
orientation), aca_56 and aca_57 (`L1\ge 3`). C40 leftover exact-L1 `y`
on aca_16/95. aca_43 k=3 for `x`. C35 leftover `y`. C36 leftover
`k=5,7,…` for `y`. C38/C39 leftover `x`. Depth ≥ 3 AC2. Lemma 11.

**U124.** One best-table row listed above. **Not a solve.** Bounded
negative for this typed k=3 pool.

**Audit.** `code/c41_yyxxxyxx_x_eq_cinv.py`, `tables/c41_yyxxxyxx_x_eq_cinv.json`.
Same-code deterministic replay plus planted nine-config control with a
persisted factor/conjugator witness replayed outside the scanner.
`independent_checker=false`. Tests independently check the algebra and
rerun the single row. Plan advisor APPROVE (`ingest/advisor_c41_plan.md`).
`ingest/advisor_wave26.md` **APPROVE**.









