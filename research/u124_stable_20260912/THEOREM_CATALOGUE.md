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
(see below). Not a mathematical obstruction.

A first bounded census (`code/q_residue_scan.py`, word ≤ 2, template ≤ 4,
`minimum_z_occurrences=2`) accepted **0** corridors on all 12 `Q_{n,δ}`
(`n=2..7`) and the 10 matching U124 best floors (0.6 s wall). This is a
**recognizer-bound negative**, not a mathematical obstruction.

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

**Not claimed.** These nine rows are not ordinary-AC trivial by C5.
Reciprocal BS(3,2) symmetry is not used. A new theorem that replaces
Britton for this specific companion `YXXXyxYx` (for example a power–Bézout
corridor against the `x^{-3}` block, or a stable defining word that makes
Britton fire) would clear an infinite family covering those ten U124
rows.

**Recognizer.** Donor equals `YXXXyxYx` (or its rotation/inverse class)
and companion `bs_mm1_shape` with m≥3. `tables/shared_donor_families.json`.
