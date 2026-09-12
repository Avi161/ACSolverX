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
the prefix/one-letter set, or involving the new letter `u`; a defining
word other than `ξ`. Gate 2 on `Q'`: `k=L1+2m` for `m≥0` when `L1≥6`
(`δ=+1` all `n`, and `δ=−1` with `n≥6`); conjugators outside the stated
set. Stored `aca_67` / `aca_87`. F3 depth ≥ 3 after AC4. Materializing
Lemma 11 for either gate.

**U124.** Same C16 Q' family as C22/C23, plus the five stored C16
endpoints. Incoming C16 remains two non-effective C0 uses. **Not a
solve.**

**Audit.** `code/c24_even_k.py`, `tables/c24_even_k.json`. Same-code
deterministic replay (not a second implementation); planted MITM
hit/miss control in `mitm_controls`. `ingest/advisor_wave9.md`
**REVISE** applied.
