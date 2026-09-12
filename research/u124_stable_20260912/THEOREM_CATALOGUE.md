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

**U124.** Not yet scanned in this campaign (bounded census pending; keep
`max_word_length` small).

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

**U124.** Scan of exact `Q_{n,δ}` for `n=2..7`, both signs:
`code/q_cyclic_complement.py`. Positive control `⟨x,y²⟩` has one rose hit;
AK3 has 0/45 as previously recorded. All 12 Q cores have **0 rose hits**, so
join corank ≥ 2. The cyclic-complement criterion therefore **does not fire**
on these exact residues. That is not an AC obstruction (AK2 control).

---

## C9. Power–Bézout corridors — INHERITED, AK3-specialized

Euclidean reduction of a defining power `t⁻¹ v^k` against a relator `a v^{-m}`
when `gcd(k,m)=1`. Portable **mechanism**; current write-up is at the AK(3)
root. Candidate for a U124 theorem if a pair has a power block and a coprime
defining exponent.

---

## C10. MM03 length ≤ 12 — LITERATURE

Every balanced 2-generator trivial-group presentation of total length ≤ 12 is
AC-trivial (computer-assisted). Used only after a **legal** stable reduction
to such a pair, with the degenerate/order-120 caveats in `MU_CRITERION.md`.
